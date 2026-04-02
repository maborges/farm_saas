"""
Integração com Copernicus Sentinel-2

Implementa acesso a imagens de satélite Sentinel-2
para monitoramento de vegetação e detecção de desmatamento.
"""

from typing import Dict, Any, List, Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SentinelImage:
    """Representa uma imagem Sentinel-2"""
    id: str
    tile_id: str
    sensing_time: datetime
    cloud_cover: float
    processing_level: str
    download_url: str
    thumbnail_url: str
    geometry: Dict[str, Any]
    size_mb: float


class Sentinel2Client:
    """
    Cliente da API Copernicus Sentinel-2
    
    Implementa acesso às imagens de satélite Sentinel-2
    através da API Copernicus Data Space Ecosystem.
    """
    
    # URLs da API
    URLS = {
        'producao': 'https://sh.dataspace.copernicus.eu',
        'homologacao': 'https://sh.dataspace.copernicus.eu',
    }
    
    # API de busca
    SEARCH_URL = 'https://catalogue.dataspace.copernicus.eu/odata/v1/Products'
    
    # API de download
    DOWNLOAD_URL = 'https://zipper.dataspace.copernicus.eu/odata/v1/Products'
    
    # API de autenticação
    AUTH_URL = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'
    
    def __init__(self, client_id: str, client_secret: str, ambiente: str = 'producao'):
        """
        Inicializa o cliente Sentinel-2
        
        Args:
            client_id: Client ID do Copernicus Data Space
            client_secret: Client Secret
            ambiente: 'producao' ou 'homologacao'
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.ambiente = ambiente
        self.access_token = None
        self.token_expires_at = None
        
        # Configurar sessão
        self.session = self._configurar_sessao()
        
        logger.info(f"Sentinel2Client inicializado para {ambiente}")
    
    def _configurar_sessao(self) -> requests.Session:
        """Configura sessão HTTP com retry"""
        session = requests.Session()
        
        # Configurar retry
        retry = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        
        # Timeout padrão (60 segundos)
        session.timeout = 60
        
        return session
    
    def autenticar(self) -> str:
        """
        Autentica na API Copernicus
        
        Returns:
            Access token
        """
        # Verificar se token ainda é válido
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                logger.debug("Usando token cacheado")
                return self.access_token
        
        logger.info("Obtendo novo access token")
        
        try:
            response = self.session.post(
                self.AUTH_URL,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                },
                timeout=30
            )
            
            response.raise_for_status()
            
            dados = response.json()
            
            self.access_token = dados['access_token']
            
            # Token expira em 1 hora (3600 segundos)
            expires_in = dados.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            logger.info(f"Token obtido. Expira em {expires_in} segundos")
            
            return self.access_token
            
        except Exception as e:
            logger.error(f"Erro ao autenticar: {str(e)}")
            raise ValueError(f"Falha na autenticação: {str(e)}")
    
    def buscar_imagens(
        self,
        latitude: float,
        longitude: float,
        data_inicio: datetime,
        data_fim: datetime,
        max_cloud_cover: float = 20.0,
        max_results: int = 10
    ) -> List[SentinelImage]:
        """
        Busca imagens Sentinel-2 para uma área e período
        
        Args:
            latitude: Latitude do centro da área
            longitude: Longitude do centro da área
            data_inicio: Data de início do período
            data_fim: Data de fim do período
            max_cloud_cover: Cobertura máxima de nuvens (%)
            max_results: Número máximo de resultados
            
        Returns:
            Lista de SentinelImage
        """
        logger.info(f"Buscando imagens para ({latitude}, {longitude}) de {data_inicio} a {data_fim}")
        
        # Autenticar
        token = self.autenticar()
        
        # Calcular bounding box (aproximadamente 10km x 10km)
        bbox = self._calcular_bbox(latitude, longitude, 0.1)
        
        # Parâmetros da busca
        params = {
            '$filter': (
                f"Collection/Name eq 'SENTINEL-2L2A' and "
                f"ContentDate/Start ge {data_inicio.isoformat()}Z and "
                f"ContentDate/Start le {data_fim.isoformat()}Z and "
                f"CloudCover le {max_cloud_cover}"
            ),
            '$expand': 'Attributes',
            '$top': max_results,
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
        }
        
        try:
            response = self.session.get(
                self.SEARCH_URL,
                params=params,
                headers=headers,
                timeout=60
            )
            
            response.raise_for_status()
            
            dados = response.json()
            
            imagens = []
            
            for item in dados.get('value', []):
                imagem = self._parse_imagem(item)
                if imagem:
                    imagens.append(imagem)
            
            logger.info(f"{len(imagens)} imagens encontradas")
            
            return imagens
            
        except Exception as e:
            logger.error(f"Erro ao buscar imagens: {str(e)}")
            return []
    
    def _calcular_bbox(self, lat: float, lon: float, delta: float) -> Tuple[float, float, float, float]:
        """
        Calcula bounding box ao redor de um ponto
        
        Args:
            lat: Latitude do centro
            lon: Longitude do centro
            delta: Delta em graus (aproximadamente)
            
        Returns:
            Tuple (min_lon, min_lat, max_lon, max_lat)
        """
        min_lon = lon - delta
        min_lat = lat - delta
        max_lon = lon + delta
        max_lat = lat + delta
        
        return (min_lon, min_lat, max_lon, max_lat)
    
    def _parse_imagem(self, item: Dict[str, Any]) -> Optional[SentinelImage]:
        """
        Parse de item da API para SentinelImage
        
        Args:
            item: Item da resposta da API
            
        Returns:
            SentinelImage ou None
        """
        try:
            # Extrair atributos
            attributes = item.get('Attributes', [])
            
            # Converter para dict
            attrs_dict = {attr['Name']: attr['Value'] for attr in attributes}
            
            # Cloud cover
            cloud_cover = attrs_dict.get('cloudCover', 100)
            
            # Sensing time
            sensing_time_str = item.get('ContentDate', {}).get('Start', '')
            sensing_time = datetime.fromisoformat(sensing_time_str.replace('Z', '+00:00'))
            
            # Geometry
            geometry = item.get('GeoFootprint', {})
            
            # Download URL
            download_url = f"{self.DOWNLOAD_URL}({item['Id']})/$value"
            
            # Thumbnail URL
            thumbnail_url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({item['Id']})/Products('quicklook')/$value"
            
            return SentinelImage(
                id=item['Id'],
                tile_id=attrs_dict.get('tileId', ''),
                sensing_time=sensing_time,
                cloud_cover=cloud_cover,
                processing_level='L2A',
                download_url=download_url,
                thumbnail_url=thumbnail_url,
                geometry=geometry,
                size_mb=item.get('ContentLength', 0) / (1024 * 1024),
            )
            
        except Exception as e:
            logger.error(f"Erro ao parsear imagem: {str(e)}")
            return None
    
    def baixar_imagem(self, imagem: SentinelImage, caminho_destino: str) -> str:
        """
        Baixa imagem Sentinel-2
        
        Args:
            imagem: SentinelImage para baixar
            caminho_destino: Caminho para salvar o arquivo
            
        Returns:
            Caminho do arquivo baixado
        """
        logger.info(f"Baixando imagem {imagem.id} para {caminho_destino}")
        
        token = self.autenticar()
        
        headers = {
            'Authorization': f'Bearer {token}',
        }
        
        try:
            response = self.session.get(
                imagem.download_url,
                headers=headers,
                stream=True,
                timeout=300  # 5 minutos para download
            )
            
            response.raise_for_status()
            
            # Salvar arquivo
            with open(caminho_destino, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Imagem baixada: {caminho_destino}")
            
            return caminho_destino
            
        except Exception as e:
            logger.error(f"Erro ao baixar imagem: {str(e)}")
            raise ValueError(f"Falha no download: {str(e)}")
    
    def baixar_bandas(
        self,
        imagem: SentinelImage,
        bandas: List[str],
        caminho_destino: str
    ) -> Dict[str, str]:
        """
        Baixa bandas específicas da imagem
        
        Args:
            imagem: SentinelImage
            bandas: Lista de bandas (B02, B03, B04, B08, etc.)
            caminho_destino: Diretório para salvar
            
        Returns:
            Dict com caminho de cada banda
        """
        logger.info(f"Baixando bandas {bandas} da imagem {imagem.id}")
        
        # Sentinel-2 bandas disponíveis:
        # B01: Coastal aerosol (60m)
        # B02: Blue (10m)
        # B03: Green (10m)
        # B04: Red (10m)
        # B05: Vegetation Red Edge (20m)
        # B06: Vegetation Red Edge (20m)
        # B07: Vegetation Red Edge (20m)
        # B08: Near Infrared (10m)
        # B8A: Narrow NIR (20m)
        # B09: Water vapour (60m)
        # B10: SWIR - Cirrus (60m)
        # B11: SWIR (20m)
        # B12: SWIR (20m)
        
        # Para NDVI precisamos de B04 (Red) e B08 (NIR)
        
        arquivos_baixados = {}
        
        for banda in bandas:
            try:
                # URL da banda específica
                banda_url = f"{self.DOWNLOAD_URL}({imagem.id})/Nodes('{banda}.jp2')/$value"
                
                token = self.autenticar()
                
                headers = {
                    'Authorization': f'Bearer {token}',
                }
                
                caminho_banda = f"{caminho_destino}/{banda}.jp2"
                
                response = self.session.get(
                    banda_url,
                    headers=headers,
                    stream=True,
                    timeout=120
                )
                
                response.raise_for_status()
                
                with open(caminho_banda, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                arquivos_baixados[banda] = caminho_banda
                
                logger.info(f"Bandas {banda} baixada: {caminho_banda}")
                
            except Exception as e:
                logger.error(f"Erro ao baixar banda {banda}: {str(e)}")
        
        return arquivos_baixados
    
    def obter_mosaico(
        self,
        latitude: float,
        longitude: float,
        data_referencia: datetime,
        max_cloud_cover: float = 10.0
    ) -> Optional[SentinelImage]:
        """
        Obtém a melhor imagem disponível para uma data
        
        Args:
            latitude: Latitude do centro
            longitude: Longitude do centro
            data_referencia: Data de referência
            max_cloud_cover: Cobertura máxima de nuvens
            
        Returns:
            Melhor SentinelImage encontrada ou None
        """
        # Buscar imagens em janela de ±7 dias
        data_inicio = data_referencia - timedelta(days=7)
        data_fim = data_referencia + timedelta(days=7)
        
        imagens = self.buscar_imagens(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            max_cloud_cover=max_cloud_cover,
            max_results=20
        )
        
        if not imagens:
            logger.warning(f"Nenhuma imagem encontrada para {data_referencia}")
            return None
        
        # Selecionar imagem com menor cobertura de nuvens
        melhor_imagem = min(imagens, key=lambda img: img.cloud_cover)
        
        logger.info(f"Melhor imagem: {melhor_imagem.id} com {melhor_imagem.cloud_cover}% de nuvens")
        
        return melhor_imagem


class Sentinel2Service:
    """
    Serviço de alto nível para Sentinel-2
    
    Combina cliente com processamento de imagens.
    """
    
    def __init__(self, client_id: str, client_secret: str):
        self.client = Sentinel2Client(client_id, client_secret)
    
    def obter_ndvi(
        self,
        latitude: float,
        longitude: float,
        data_referencia: datetime,
        caminho_saida: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtém NDVI para uma área e data
        
        Args:
            latitude: Latitude do centro
            longitude: Longitude do centro
            data_referencia: Data de referência
            caminho_saida: Diretório para salvar dados
            
        Returns:
            Dict com informações do NDVI ou None
        """
        logger.info(f"Obtendo NDVI para ({latitude}, {longitude}) em {data_referencia}")
        
        # Obter melhor imagem
        imagem = self.client.obter_mosaico(
            latitude=latitude,
            longitude=longitude,
            data_referencia=data_referencia,
            max_cloud_cover=15.0
        )
        
        if not imagem:
            return None
        
        # Baixar bandas B04 (Red) e B08 (NIR) para NDVI
        bandas_baixadas = self.client.baixar_bandas(
            imagem=imagem,
            bandas=['B04', 'B08'],
            caminho_destino=caminho_saida
        )
        
        if not bandas_baixadas:
            return None
        
        # Calcular NDVI
        # NDVI = (NIR - RED) / (NIR + RED)
        # Isso requer processamento das imagens JP2
        
        return {
            'imagem_id': imagem.id,
            'data': imagem.sensing_time.isoformat(),
            'cloud_cover': imagem.cloud_cover,
            'bandas_baixadas': list(bandas_baixadas.keys()),
            'caminho_bandas': bandas_baixadas,
            'ndvi_calculado': False,  # Requer processamento adicional
        }
    
    def monitorar_area(
        self,
        latitude: float,
        longitude: float,
        periodo_dias: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Monitora área em um período
        
        Args:
            latitude: Latitude do centro
            longitude: Longitude do centro
            periodo_dias: Período em dias para buscar imagens
            
        Returns:
            Lista de informações de imagens disponíveis
        """
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=periodo_dias)
        
        imagens = self.client.buscar_imagens(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            max_cloud_cover=30.0,
            max_results=50
        )
        
        resultados = []
        
        for imagem in imagens:
            resultados.append({
                'id': imagem.id,
                'data': imagem.sensing_time.isoformat(),
                'cloud_cover': imagem.cloud_cover,
                'tile_id': imagem.tile_id,
                'download_url': imagem.download_url,
            })
        
        return resultados


class Sentinel2Factory:
    """Factory para criar instâncias do serviço"""
    
    _instancia = None
    
    @classmethod
    def get_service(cls, client_id: str, client_secret: str) -> Sentinel2Service:
        """Obtém instância singleton do serviço"""
        if cls._instancia is None:
            cls._instancia = Sentinel2Service(client_id, client_secret)
        return cls._instancia
