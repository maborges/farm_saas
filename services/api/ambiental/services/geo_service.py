"""
Serviços de Geoprocessamento

Implementa cálculos de áreas, sobreposições e análises espaciais
para gestão ambiental do CAR.
"""

from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import func
import logging
import json

logger = logging.getLogger(__name__)


class GeoService:
    """
    Serviço de Geoprocessamento
    
    Implementa operações espaciais usando GeoAlchemy2 e Shapely.
    """
    
    # Constantes de cálculo
    M2_PARA_HECTARE = 10000.0
    PI = 3.141592653589793
    
    # Faixas de APP (em metros) conforme Código Florestal
    APP_RIOS = {
        "ate_10m": 30,    # Rios até 10m de largura: 30m de APP
        "10a_50m": 50,    # Rios de 10-50m: 50m de APP
        "50a_200m": 100,  # Rios de 50-200m: 100m de APP
        "200a_600m": 200, # Rios de 200-600m: 200m de APP
        "mais_600m": 500, # Rios acima de 600m: 500m de APP
    }
    
    APP_NASCENTES = 50  # 50m de raio para nascentes
    APP_LAGOAS = 100    # 100m para lagoas naturais
    APP_SERRAS = 100    # 100m para topo de serra
    APP_MORROS = 100    # 100m para morros
    
    # Percentuais de RL por bioma e região
    RL_AMAZONIA = {
        "floresta": 0.80,  # 80% para floresta
        "cerrado": 0.35,   # 35% para cerrado
        "campos_gerais": 0.20,  # 20% para campos gerais
    }
    
    RL_OUTRAS_REGIONS = 0.20  # 20% para outras regiões
    
    def __init__(self):
        pass
    
    def calcular_area_poligono(self, coordenadas: List[List[float]]) -> float:
        """
        Calcula área de um polígono em hectares
        
        Args:
            coordenadas: Lista de coordenadas [longitude, latitude]
            
        Returns:
            Área em hectares
        """
        try:
            from shapely.geometry import Polygon
            
            # Criar polígono
            poligono = Polygon(coordenadas)
            
            # Calcular área em metros quadrados (usando projeção adequada)
            area_m2 = self._calcular_area_projetada(poligono)
            
            # Converter para hectares
            area_ha = area_m2 / self.M2_PARA_HECTARE
            
            logger.info(f"Área calculada: {area_ha:.2f} ha")
            
            return area_ha
            
        except ImportError:
            logger.warning("Shapely não instalado. Usando cálculo simplificado.")
            return self._calcular_area_simplificada(coordenadas)
        except Exception as e:
            logger.error(f"Erro ao calcular área: {str(e)}")
            return 0.0
    
    def _calcular_area_projetada(self, poligono) -> float:
        """
        Calcula área usando projeção adequada
        
        Args:
            poligono: Polígono Shapely
            
        Returns:
            Área em m²
        """
        from shapely.ops import transform
        from functools import partial
        import pyproj
        
        # Projetar para UTM (zona baseada no centroide)
        centroide = poligono.centroid
        lon, lat = centroide.x, centroide.y
        
        # Calcular zona UTM
        zona_utm = int((lon + 180) / 6) + 1
        
        # Criar projeção UTM
        proj_utm = pyproj.Proj(proj='utm', zone=zona_utm, ellps='WGS84')
        
        # Transformar polígono para UTM
        project = partial(pyproj.transform,
                         pyproj.Proj(init='EPSG:4326'),
                         proj_utm)
        
        poligono_utm = transform(project, poligono)
        
        # Calcular área em metros quadrados
        return poligono_utm.area
    
    def _calcular_area_simplificada(self, coordenadas: List[List[float]]) -> float:
        """
        Calcula área usando fórmula de Gauss (simplificado)
        
        Args:
            coordenadas: Lista de coordenadas [lon, lat]
            
        Returns:
            Área aproximada em hectares
        """
        n = len(coordenadas)
        
        if n < 3:
            return 0.0
        
        # Fórmula de Gauss para área de polígono
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += coordenadas[i][0] * coordenadas[j][1]
            area -= coordenadas[j][0] * coordenadas[i][1]
        
        area = abs(area) / 2.0
        
        # Converter de graus² para hectares (aproximação)
        # 1 grau ≈ 111km no equador
        area_ha = area * (111000 ** 2) / self.M2_PARA_HECTARE
        
        return area_ha
    
    def calcular_area_app_rio(self,
                              largura_rio: float,
                              comprimento_rio: float) -> float:
        """
        Calcula área de APP ao longo de rio
        
        Args:
            largura_rio: Largura do rio em metros
            comprimento_rio: Comprimento do rio em metros
            
        Returns:
            Área de APP em hectares
        """
        # Determinar faixa de APP conforme largura do rio
        if largura_rio < 10:
            faixa_app = self.APP_RIOS["ate_10m"]
        elif largura_rio < 50:
            faixa_app = self.APP_RIOS["10a_50m"]
        elif largura_rio < 200:
            faixa_app = self.APP_RIOS["50a_200m"]
        elif largura_rio < 600:
            faixa_app = self.APP_RIOS["200a_600m"]
        else:
            faixa_app = self.APP_RIOS["mais_600m"]
        
        # Calcular área (faixa em ambos os lados do rio)
        area_m2 = faixa_app * comprimento_rio * 2
        
        # Converter para hectares
        area_ha = area_m2 / self.M2_PARA_HECTARE
        
        logger.info(f"APP de rio: {faixa_app}m de faixa, {area_ha:.2f} ha")
        
        return area_ha
    
    def calcular_area_app_nascente(self,
                                   numero_nascentes: int) -> float:
        """
        Calcula área de APP ao redor de nascentes
        
        Args:
            numero_nascentes: Número de nascentes
            
        Returns:
            Área de APP em hectares
        """
        # Área de APP por nascente (círculo de 50m de raio)
        area_por_nascente = self.PI * (self.APP_NASCENTES ** 2)
        
        # Área total
        area_total_m2 = area_por_nascente * numero_nascentes
        
        # Converter para hectares
        area_ha = area_total_m2 / self.M2_PARA_HECTARE
        
        logger.info(f"APP de nascentes: {numero_nascentes} nascentes, {area_ha:.2f} ha")
        
        return area_ha
    
    def calcular_area_rl(self,
                         area_total: float,
                         bioma: str,
                         regiao: str) -> float:
        """
        Calcula área mínima de Reserva Legal
        
        Args:
            area_total: Área total do imóvel em hectares
            bioma: Bioma (floresta, cerrado, campos_gerais, caatinga, pampa, pantanal)
            regiao: Região (amazonia, outras_regioes)
            
        Returns:
            Área mínima de RL em hectares
        """
        # Determinar percentual de RL
        if regiao.lower() == 'amazonia':
            percentual = self.RL_AMAZONIA.get(bioma.lower(), 0.35)
        else:
            percentual = self.RL_OUTRAS_REGIONS
        
        # Calcular área mínima
        area_rl_minima = area_total * percentual
        
        logger.info(f"RL mínima: {percentual*100:.0f}% de {area_total:.2f}ha = {area_rl_minima:.2f}ha")
        
        return area_rl_minima
    
    def verificar_sobreposicao(self,
                               poligono_imovel: List[List[float]],
                               poligono_sobreposicao: List[List[float]]) -> Dict[str, Any]:
        """
        Verifica sobreposição entre dois polígonos
        
        Args:
            poligono_imovel: Polígono do imóvel
            poligono_sobreposicao: Polígono da sobreposição (TI, UC, etc.)
            
        Returns:
            Dicionário com informações da sobreposição
        """
        try:
            from shapely.geometry import Polygon
            
            # Criar polígonos
            poligono1 = Polygon(poligono_imovel)
            poligono2 = Polygon(poligono_sobreposicao)
            
            # Calcular interseção
            interseccao = poligono1.intersection(poligono2)
            
            if interseccao.is_empty:
                return {
                    "possui_sobreposicao": False,
                    "area_sobreposta_ha": 0.0,
                    "percentual_sobreposto": 0.0,
                }
            
            # Calcular área da interseção
            area_sobreposta_m2 = interseccao.area
            area_sobreposta_ha = area_sobreposta_m2 / self.M2_PARA_HECTARE
            
            # Calcular percentual
            area_imovel_m2 = poligono1.area
            percentual = (area_sobreposta_ha / (area_imovel_m2 / self.M2_PARA_HECTARE)) * 100 if area_imovel_m2 > 0 else 0.0
            
            return {
                "possui_sobreposicao": True,
                "area_sobreposta_ha": round(area_sobreposta_ha, 2),
                "percentual_sobreposto": round(percentual, 2),
                "geometria_interseccao": json.loads(interseccao.__geo_interface__),
            }
            
        except ImportError:
            logger.warning("Shapely não instalado. Sobreposição não calculada.")
            return {
                "possui_sobreposicao": False,
                "area_sobreposta_ha": 0.0,
                "percentual_sobreposto": 0.0,
            }
        except Exception as e:
            logger.error(f"Erro ao verificar sobreposição: {str(e)}")
            return {
                "possui_sobreposicao": False,
                "area_sobreposta_ha": 0.0,
                "percentual_sobreposto": 0.0,
                "erro": str(e),
            }
    
    def calcular_ndvi(self,
                      banda_vermelho: float,
                      banda_infravermelho: float) -> float:
        """
        Calcula NDVI (Normalized Difference Vegetation Index)
        
        Args:
            banda_vermelho: Reflectância na banda do vermelho
            banda_infravermelho: Reflectância na banda do infravermelho próximo
            
        Returns:
            NDVI (valor entre -1 e 1)
        """
        # Fórmula do NDVI: (NIR - RED) / (NIR + RED)
        if banda_infravermelho + banda_vermelho == 0:
            return 0.0
        
        ndvi = (banda_infravermelho - banda_vermelho) / \
               (banda_infravermelho + banda_vermelho)
        
        return ndvi
    
    def classificar_vegetacao_por_ndvi(self, ndvi: float) -> str:
        """
        Classifica tipo de vegetação baseado no NDVI
        
        Args:
            ndvi: Valor do NDVI
            
        Returns:
            Tipo de vegetação
        """
        if ndvi < 0.1:
            return "solo_exposto"  # Solo exposto, água, rocha
        elif ndvi < 0.2:
            return "vegetacao_rala"  # Vegetação rala, pastagem degradada
        elif ndvi < 0.4:
            return "vegetacao_moderada"  # Vegetação moderada
        elif ndvi < 0.6:
            return "vegetacao_saudavel"  # Vegetação saudável
        else:
            return "vegetacao_densa"  # Vegetação muito densa, floresta
    
    def detectar_desmatamento(self,
                              ndvi_anterior: float,
                              ndvi_atual: float,
                              area_hectares: float) -> Dict[str, Any]:
        """
        Detecta possível desmatamento baseado na mudança de NDVI
        
        Args:
            ndvi_anterior: NDVI da imagem anterior
            ndvi_atual: NDVI da imagem atual
            area_hectares: Área da mudança em hectares
            
        Returns:
            Dicionário com informações do alerta
        """
        # Calcular mudança de NDVI
        delta_ndvi = ndvi_anterior - ndvi_atual
        
        # Classificar severidade
        if delta_ndvi < 0.2:
            severidade = "baixa"
        elif delta_ndvi < 0.4:
            severidade = "media"
        elif delta_ndvi < 0.6:
            severidade = "alta"
        else:
            severidade = "critica"
        
        # Determinar se é alerta válido
        gerar_alerta = delta_ndvi > 0.2 and area_hectares > 1.0
        
        return {
            "delta_ndvi": round(delta_ndvi, 3),
            "severidade": severidade,
            "area_hectares": area_hectares,
            "gerar_alerta": gerar_alerta,
            "ndvi_anterior": ndvi_anterior,
            "ndvi_atual": ndvi_atual,
            "classificacao_anterior": self.classificar_vegetacao_por_ndvi(ndvi_anterior),
            "classificacao_atual": self.classificar_vegetacao_por_ndvi(ndvi_atual),
        }
    
    def calcular_percentual_vegetacao(self,
                                      area_total: float,
                                      area_vegetacao: float) -> float:
        """
        Calcula percentual de vegetação nativa
        
        Args:
            area_total: Área total em hectares
            area_vegetacao: Área de vegetação em hectares
            
        Returns:
            Percentual de vegetação
        """
        if area_total <= 0:
            return 0.0
        
        percentual = (area_vegetacao / area_total) * 100
        
        return round(percentual, 2)
    
    def verificar_cumprimento_rl(self,
                                 area_rl_exigente: float,
                                 area_rl_existente: float) -> Dict[str, Any]:
        """
        Verifica se o imóvel cumpre a Reserva Legal
        
        Args:
            area_rl_exigente: Área de RL exigida por lei
            area_rl_existente: Área de RL existente no imóvel
            
        Returns:
            Dicionário com situação da RL
        """
        area_suficiente = area_rl_existente >= area_rl_exigente
        
        if area_suficiente:
            saldo = area_rl_existente - area_rl_exigente
            situacao = "cumprida"
        else:
            deficit = area_rl_exigente - area_rl_existente
            situacao = "deficit"
            saldo = -deficit
        
        return {
            "situacao": situacao,
            "area_exigente_ha": round(area_rl_exigente, 2),
            "area_existente_ha": round(area_rl_existente, 2),
            "saldo_ha": round(saldo, 2),
            "percentual_cumprimento": round((area_rl_existente / area_rl_exigente) * 100, 2) if area_rl_exigente > 0 else 0,
        }


class GeoServiceFactory:
    """Factory para criar instâncias do GeoService"""
    
    _instancia = None
    
    @classmethod
    def get_service(cls) -> GeoService:
        """Obtém instância singleton do serviço"""
        if cls._instancia is None:
            cls._instancia = GeoService()
        return cls._instancia
