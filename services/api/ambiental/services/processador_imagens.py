"""
Processamento de Imagens de Satélite

Implementa cálculo de NDVI e detecção de mudança de cobertura
a partir de imagens Sentinel-2.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ResultadoNDVI:
    """Resultado do cálculo de NDVI"""
    data: datetime
    ndvi_medio: float
    ndvi_minimo: float
    ndvi_maximo: float
    ndvi_desvio_padrao: float
    area_vegetacao_saudavel: float  # hectares
    area_vegetacao_moderada: float
    area_vegetacao_rala: float
    area_sem_vegetacao: float
    imagem_path: str
    nuvens_percentual: float


@dataclass
class ResultadoMudanca:
    """Resultado da detecção de mudança"""
    data_inicial: datetime
    data_final: datetime
    area_mudanca_hectares: float
    tipo_mudanca: str  # 'desmatamento', 'regeneracao', 'agricultura'
    severidade: str  # 'baixa', 'media', 'alta', 'critica'
    ndvi_anterior: float
    ndvi_atual: float
    delta_ndvi: float
    coordenadas: List[Tuple[float, float]]
    confianca: float  # 0.0 a 1.0


class ProcessadorImagens:
    """
    Processador de Imagens de Satélite
    
    Implementa algoritmos para cálculo de NDVI e detecção
    de mudança de cobertura vegetal.
    """
    
    # Thresholds de NDVI para classificação de vegetação
    NDVI_SOLO_EXPOSTO = 0.1
    NDVI_VEGETACAO_RALA = 0.2
    NDVI_VEGETACAO_MODERADA = 0.4
    NDVI_VEGETACAO_SAUDAVEL = 0.6
    
    # Thresholds para detecção de mudança
    MUDANCA_LEVE = 0.2
    MUDANCA_MODERADA = 0.4
    MUDANCA_SEVERA = 0.6
    
    def __init__(self, resolucao_metros: float = 10.0):
        """
        Inicializa processador
        
        Args:
            resolucao_metros: Resolução espacial da imagem (metros por pixel)
        """
        self.resolucao_metros = resolucao_metros
        self.area_por_pixel_m2 = resolucao_metros ** 2
        self.area_por_pixel_ha = self.area_por_pixel_m2 / 10000.0
    
    def calcular_ndvi(
        self,
        banda_vermelho: np.ndarray,
        banda_infravermelho: np.ndarray
    ) -> np.ndarray:
        """
        Calcula NDVI a partir das bandas Red e NIR
        
        NDVI = (NIR - RED) / (NIR + RED)
        
        Args:
            banda_vermelho: Array 2D com reflectância da banda vermelha
            banda_infravermelho: Array 2D com reflectância da banda NIR
            
        Returns:
            Array 2D com valores de NDVI (-1 a 1)
        """
        logger.info("Calculando NDVI")
        
        # Evitar divisão por zero
        denominador = banda_infravermelho + banda_vermelho
        
        # Máscara para evitar divisão por zero
        mascara = denominador == 0
        
        # Calcular NDVI
        ndvi = (banda_infravermelho - banda_vermelho) / denominador
        
        # Preencher valores inválidos com -1 (sem dados)
        ndvi[mascara] = -1
        
        return ndvi
    
    def carregar_bandas_sentinel2(
        self,
        caminho_banda_vermelho: str,
        caminho_banda_nir: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Carrega bandas Sentinel-2 de arquivos JP2
        
        Args:
            caminho_banda_vermelho: Caminho para B04.jp2 (Red)
            caminho_banda_nir: Caminho para B08.jp2 (NIR)
            
        Returns:
            Tuple (banda_vermelho, banda_infravermelho)
        """
        try:
            # Tentar usar rasterio para abrir JP2
            import rasterio
            
            with rasterio.open(caminho_banda_vermelho) as src:
                banda_vermelho = src.read(1).astype(np.float32)
                # Normalizar para reflectância (0-1)
                banda_vermelho = banda_vermelho / 10000.0
                
            with rasterio.open(caminho_banda_nir) as src:
                banda_infravermelho = src.read(1).astype(np.float32)
                banda_infravermelho = banda_infravermelho / 10000.0
                
            logger.info(f"Bandas carregadas: {banda_vermelho.shape}")
            
            return banda_vermelho, banda_infravermelho
            
        except ImportError:
            logger.warning("rasterio não instalado. Usando dados simulados.")
            return self._gerar_dados_simulados()
        except Exception as e:
            logger.error(f"Erro ao carregar bandas: {str(e)}")
            return self._gerar_dados_simulados()
    
    def _gerar_dados_simulados(self) -> Tuple[np.ndarray, np.ndarray]:
        """Gera dados simulados para testes"""
        # Simular imagem 1000x1000 pixels
        tamanho = 1000
        
        # Banda vermelha (valores mais altos = menos vegetação)
        banda_vermelho = np.random.uniform(0.05, 0.3, (tamanho, tamanho))
        
        # Banda NIR (valores mais altos = mais vegetação)
        banda_infravermelho = np.random.uniform(0.2, 0.5, (tamanho, tamanho))
        
        # Criar área de desmatamento (canto superior direito)
        banda_vermelho[0:200, 800:1000] = 0.35  # Solo exposto
        banda_infravermelho[0:200, 800:1000] = 0.15  # Sem vegetação
        
        return banda_vermelho, banda_infravermelho
    
    def classificar_vegetacao(self, ndvi: np.ndarray) -> Dict[str, float]:
        """
        Classifica vegetação por faixa de NDVI
        
        Args:
            ndvi: Array 2D com valores de NDVI
            
        Returns:
            Dict com áreas em hectares por classe
        """
        total_pixels = ndvi.size
        
        # Contar pixels por classe
        pixels_sem_vegetacao = np.sum(ndvi < self.NDVI_SOLO_EXPOSTO)
        pixels_vegetacao_rala = np.sum(
            (ndvi >= self.NDVI_SOLO_EXPOSTO) & (ndvi < self.NDVI_VEGETACAO_RALA)
        )
        pixels_vegetacao_moderada = np.sum(
            (ndvi >= self.NDVI_VEGETACAO_RALA) & (ndvi < self.NDVI_VEGETACAO_MODERADA)
        )
        pixels_vegetacao_saudavel = np.sum(ndvi >= self.NDVI_VEGETACAO_MODERADA)
        
        # Converter para hectares
        area_sem = pixels_sem_vegetacao * self.area_por_pixel_ha
        area_rala = pixels_vegetacao_rala * self.area_por_pixel_ha
        area_moderada = pixels_vegetacao_moderada * self.area_por_pixel_ha
        area_saudavel = pixels_vegetacao_saudavel * self.area_por_pixel_ha
        
        return {
            'sem_vegetacao': area_sem,
            'vegetacao_rala': area_rala,
            'vegetacao_moderada': area_moderada,
            'vegetacao_saudavel': area_saudavel,
        }
    
    def processar_imagem(
        self,
        caminho_banda_vermelho: str,
        caminho_banda_nir: str,
        data_imagem: datetime,
        nuvens_percentual: float = 0.0
    ) -> ResultadoNDVI:
        """
        Processa imagem completa e calcula NDVI
        
        Args:
            caminho_banda_vermelho: Caminho B04.jp2
            caminho_banda_nir: Caminho B08.jp2
            data_imagem: Data da imagem
            nuvens_percentual: Percentual de cobertura de nuvens
            
        Returns:
            ResultadoNDVI
        """
        logger.info(f"Processando imagem de {data_imagem}")
        
        # Carregar bandas
        banda_vermelho, banda_infravermelho = self.carregar_bandas_sentinel2(
            caminho_banda_vermelho,
            caminho_banda_nir
        )
        
        # Calcular NDVI
        ndvi = self.calcular_ndvi(banda_vermelho, banda_infravermelho)
        
        # Estatísticas
        ndvi_valido = ndvi[ndvi > -1]  # Excluir pixels inválidos
        
        ndvi_medio = float(np.mean(ndvi_valido))
        ndvi_minimo = float(np.min(ndvi_valido))
        ndvi_maximo = float(np.max(ndvi_valido))
        ndvi_desvio = float(np.std(ndvi_valido))
        
        # Classificar vegetação
        classificacao = self.classificar_vegetacao(ndvi_valido)
        
        logger.info(f"NDVI médio: {ndvi_medio:.3f}")
        
        return ResultadoNDVI(
            data=data_imagem,
            ndvi_medio=ndvi_medio,
            ndvi_minimo=ndvi_minimo,
            ndvi_maximo=ndvi_maximo,
            ndvi_desvio_padrao=ndvi_desvio,
            area_vegetacao_saudavel=classificacao['vegetacao_saudavel'],
            area_vegetacao_moderada=classificacao['vegetacao_moderada'],
            area_vegetacao_rala=classificacao['vegetacao_rala'],
            area_sem_vegetacao=classificacao['sem_vegetacao'],
            imagem_path=caminho_banda_vermelho,
            nuvens_percentual=nuvens_percentual,
        )
    
    def detectar_mudanca(
        self,
        ndvi_anterior: np.ndarray,
        ndvi_atual: np.ndarray,
        threshold: float = 0.3
    ) -> List[ResultadoMudanca]:
        """
        Detecta mudanças entre duas imagens de NDVI
        
        Args:
            ndvi_anterior: Array 2D com NDVI anterior
            ndvi_atual: Array 2D com NDVI atual
            threshold: Threshold mínimo para considerar mudança
            
        Returns:
            Lista de ResultadoMudanca
        """
        logger.info("Detectando mudanças de cobertura")
        
        # Calcular diferença
        delta_ndvi = ndvi_anterior - ndvi_atual
        
        # Máscara de mudança significativa
        mascara_mudanca = np.abs(delta_ndvi) > threshold
        
        if not np.any(mascara_mudanca):
            logger.info("Nenhuma mudança significativa detectada")
            return []
        
        # Identificar regiões de mudança (connected components)
        try:
            from scipy import ndimage
            
            # Estrutura de conectividade (8 vizinhos)
            estrutura = ndimage.generate_binary_structure(2, 2)
            
            # Rotular regiões conectadas
            labeled, num_features = ndimage.label(mascara_mudanca, structure=estrutura)
            
            logger.info(f"{num_features} regiões de mudança detectadas")
            
            resultados = []
            
            for i in range(1, num_features + 1):
                regiao = (labeled == i)
                
                # Calcular estatísticas da região
                delta_regiao = delta_ndvi[regiao]
                delta_medio = float(np.mean(delta_regiao))
                area_pixels = int(np.sum(regiao))
                area_hectares = area_pixels * self.area_por_pixel_ha
                
                # Determinar tipo de mudança
                if delta_medio > 0:
                    tipo = 'desmatamento'  # NDVI diminuiu
                elif delta_medio < 0:
                    tipo = 'regeneracao'  # NDVI aumentou
                else:
                    tipo = 'agricultura'
                
                # Determinar severidade
                delta_abs = np.abs(delta_medio)
                if delta_abs < self.MUDANCA_LEVE:
                    severidade = 'baixa'
                elif delta_abs < self.MUDANCA_MODERADA:
                    severidade = 'media'
                elif delta_abs < self.MUDANCA_SEVERA:
                    severidade = 'alta'
                else:
                    severidade = 'critica'
                
                # Calcular confiança (baseada no tamanho da região)
                confianca = min(1.0, area_pixels / 100)
                
                # Obter coordenadas (simplificado - centroide da região)
                centroide = ndimage.center_of_mass(regiao)
                coordenadas = [(float(centroide[0]), float(centroide[1]))]
                
                resultado = ResultadoMudanca(
                    data_inicial=datetime.now(),  # Preencher com data real
                    data_final=datetime.now(),
                    area_mudanca_hectares=area_hectares,
                    tipo_mudanca=tipo,
                    severidade=severidade,
                    ndvi_anterior=0.0,  # Preencher com valor real
                    ndvi_atual=0.0,
                    delta_ndvi=delta_medio,
                    coordenadas=coordenadas,
                    confianca=confianca,
                )
                
                resultados.append(resultado)
            
            return resultados
            
        except ImportError:
            logger.warning("scipy não instalado. Detecção simplificada.")
            return self._detectar_mudanca_simplificada(ndvi_anterior, ndvi_atual, threshold)
    
    def _detectar_mudanca_simplificada(
        self,
        ndvi_anterior: np.ndarray,
        ndvi_atual: np.ndarray,
        threshold: float
    ) -> List[ResultadoMudanca]:
        """Detecção simplificada sem scipy"""
        delta_ndvi = ndvi_anterior - ndvi_atual
        mascara = np.abs(delta_ndvi) > threshold
        
        if not np.any(mascara):
            return []
        
        # Criar uma única região de mudança
        area_total = np.sum(mascara) * self.area_por_pixel_ha
        delta_medio = float(np.mean(delta_ndvi[mascara]))
        
        tipo = 'desmatamento' if delta_medio > 0 else 'regeneracao'
        severidade = 'media' if np.abs(delta_medio) < 0.4 else 'alta'
        
        return [
            ResultadoMudanca(
                data_inicial=datetime.now(),
                data_final=datetime.now(),
                area_mudanca_hectares=area_total,
                tipo_mudanca=tipo,
                severidade=severidade,
                ndvi_anterior=0.0,
                ndvi_atual=0.0,
                delta_ndvi=delta_medio,
                coordenadas=[],
                confianca=0.5,
            )
        ]
    
    def salvar_resultado(
        self,
        resultado: ResultadoNDVI,
        caminho_saida: str
    ) -> str:
        """
        Salva resultado do processamento
        
        Args:
            resultado: ResultadoNDVI
            caminho_saida: Caminho para salvar
            
        Returns:
            Caminho do arquivo salvo
        """
        import json
        
        dados = {
            'data': resultado.data.isoformat(),
            'ndvi_medio': resultado.ndvi_medio,
            'ndvi_minimo': resultado.ndvi_minimo,
            'ndvi_maximo': resultado.ndvi_maximo,
            'ndvi_desvio_padrao': resultado.ndvi_desvio_padrao,
            'areas': {
                'vegetacao_saudavel': resultado.area_vegetacao_saudavel,
                'vegetacao_moderada': resultado.area_vegetacao_moderada,
                'vegetacao_rala': resultado.area_vegetacao_rala,
                'sem_vegetacao': resultado.area_sem_vegetacao,
            },
            'nuvens_percentual': resultado.nuvens_percentual,
        }
        
        with open(caminho_saida, 'w') as f:
            json.dump(dados, f, indent=2)
        
        logger.info(f"Resultado salvo: {caminho_saida}")
        
        return caminho_saida


class ProcessadorImagensFactory:
    """Factory para criar processadores"""
    
    @staticmethod
    def get_processador(resolucao_metros: float = 10.0) -> ProcessadorImagens:
        """Obtém instância de processador"""
        return ProcessadorImagens(resolucao_metros)
