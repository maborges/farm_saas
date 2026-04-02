"""
Serviço de Alertas de Desmatamento

Implementa geração e gerenciamento de alertas automáticos
de desmatamento baseados em análise de NDVI.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AlertaDesmatamento:
    """Representa um alerta de desmatamento"""
    id: str
    car_id: str
    data_alerta: datetime
    data_evento: datetime
    latitude: float
    longitude: float
    area_hectares: float
    severidade: str  # 'baixa', 'media', 'alta', 'critica'
    ndvi_anterior: float
    ndvi_atual: float
    delta_ndvi: float
    status: str  # 'novo', 'em_analise', 'confirmado', 'falso_positivo', 'mitigado'
    notificado: bool
    data_notificacao: Optional[datetime]


class AlertaService:
    """
    Serviço de Gestão de Alertas
    
    Gerencia ciclo de vida de alertas de desmatamento.
    """
    
    # Thresholds para geração de alertas
    AREA_MINIMA_HECTARES = 1.0
    DELTA_NDVI_MINIMO = 0.2
    
    def __init__(self):
        self.alertas = []
    
    def gerar_alerta(
        self,
        car_id: str,
        area_hectares: float,
        ndvi_anterior: float,
        ndvi_atual: float,
        delta_ndvi: float,
        coordenadas: tuple
    ) -> Optional[AlertaDesmatamento]:
        """
        Gera alerta de desmatamento
        
        Args:
            car_id: ID do CAR
            area_hectares: Área desmatada em hectares
            ndvi_anterior: NDVI antes da mudança
            ndvi_atual: NDVI após a mudança
            delta_ndvi: Variação do NDVI
            coordenadas: (latitude, longitude)
            
        Returns:
            AlertaDesmatamento ou None
        """
        # Verificar se atende critérios mínimos
        if area_hectares < self.AREA_MINIMA_HECTARES:
            logger.info(f"Área {area_hectares}ha abaixo do mínimo ({self.AREA_MINIMA_HECTARES}ha)")
            return None
        
        if delta_ndvi < self.DELTA_NDVI_MINIMO:
            logger.info(f"Delta NDVI {delta_ndvi} abaixo do mínimo ({self.DELTA_NDVI_MINIMO})")
            return None
        
        # Determinar severidade
        severidade = self._classificar_severidade(delta_ndvi, area_hectares)
        
        # Criar alerta
        alerta = AlertaDesmatamento(
            id=self._gerar_id_alerta(),
            car_id=car_id,
            data_alerta=datetime.now(),
            data_evento=datetime.now(),
            latitude=coordenadas[0],
            longitude=coordenadas[1],
            area_hectares=area_hectares,
            severidade=severidade,
            ndvi_anterior=ndvi_anterior,
            ndvi_atual=ndvi_atual,
            delta_ndvi=delta_ndvi,
            status='novo',
            notificado=False,
            data_notificacao=None,
        )
        
        self.alertas.append(alerta)
        
        logger.info(f"Alerta gerado: {alerta.id} - {area_hectares}ha - {severidade}")
        
        return alerta
    
    def _classificar_severidade(self, delta_ndvi: float, area_hectares: float) -> str:
        """Classifica severidade do alerta"""
        # Score baseado em delta NDVI e área
        score_ndvi = min(1.0, delta_ndvi / 0.6)  # Normalizar 0-1
        score_area = min(1.0, area_hectares / 100)  # Normalizar 0-1
        
        score_total = (score_ndvi * 0.6) + (score_area * 0.4)
        
        if score_total < 0.25:
            return 'baixa'
        elif score_total < 0.5:
            return 'media'
        elif score_total < 0.75:
            return 'alta'
        else:
            return 'critica'
    
    def _gerar_id_alerta(self) -> str:
        """Gera ID único para alerta"""
        import uuid
        return f"ALT-{uuid.uuid4().hex[:8].upper()}"
    
    def notificar_alerta(self, alerta_id: str, email_destinatario: str) -> bool:
        """
        Envia notificação de alerta
        
        Args:
            alerta_id: ID do alerta
            email_destinatario: E-mail para notificação
            
        Returns:
            True se notificado com sucesso
        """
        alerta = self._buscar_alerta(alerta_id)
        
        if not alerta:
            logger.error(f"Alerta {alerta_id} não encontrado")
            return False
        
        # Enviar e-mail
        sucesso = self._enviar_email_alerta(alerta, email_destinatario)
        
        if sucesso:
            alerta.notificado = True
            alerta.data_notificacao = datetime.now()
            logger.info(f"Alerta {alerta_id} notificado para {email_destinatario}")
        
        return sucesso
    
    def _buscar_alerta(self, alerta_id: str) -> Optional[AlertaDesmatamento]:
        """Busca alerta por ID"""
        for alerta in self.alertas:
            if alerta.id == alerta_id:
                return alerta
        return None
    
    def _enviar_email_alerta(self, alerta: AlertaDesmatamento, destinatario: str) -> bool:
        """Envia e-mail de alerta"""
        # TODO: Implementar envio de e-mail
        logger.info(f"Enviando e-mail para {destinatario} sobre alerta {alerta.id}")
        
        # Simular envio
        return True
    
    def atualizar_status_alerta(self, alerta_id: str, novo_status: str) -> bool:
        """
        Atualiza status do alerta
        
        Args:
            alerta_id: ID do alerta
            novo_status: Novo status ('novo', 'em_analise', 'confirmado', 'falso_positivo', 'mitigado')
            
        Returns:
            True se atualizado
        """
        alerta = self._buscar_alerta(alerta_id)
        
        if not alerta:
            return False
        
        alerta.status = novo_status
        logger.info(f"Alerta {alerta_id} atualizado para {novo_status}")
        
        return True
    
    def listar_alertas(
        self,
        car_id: Optional[str] = None,
        status: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> List[AlertaDesmatamento]:
        """
        Lista alertas com filtros
        
        Args:
            car_id: Filtrar por CAR
            status: Filtrar por status
            data_inicio: Filtrar por data inicial
            data_fim: Filtrar por data final
            
        Returns:
            Lista de alertas
        """
        resultados = self.alertas
        
        if car_id:
            resultados = [a for a in resultados if a.car_id == car_id]
        
        if status:
            resultados = [a for a in resultados if a.status == status]
        
        if data_inicio:
            resultados = [a for a in resultados if a.data_alerta >= data_inicio]
        
        if data_fim:
            resultados = [a for a in resultados if a.data_alerta <= data_fim]
        
        return resultados
    
    def obter_resumo_alertas(self, car_id: str) -> Dict[str, Any]:
        """
        Obtém resumo de alertas para um CAR
        
        Args:
            car_id: ID do CAR
            
        Returns:
            Dict com resumo
        """
        alertas = self.listar_alertas(car_id=car_id)
        
        total = len(alertas)
        novos = len([a for a in alertas if a.status == 'novo'])
        confirmados = len([a for a in alertas if a.status == 'confirmado'])
        area_total = sum(a.area_hectares for a in alertas)
        
        return {
            'total_alertas': total,
            'alertas_novos': novos,
            'alertas_confirmados': confirmados,
            'area_total_afetada_ha': area_total,
            'alertas_por_severidade': {
                'baixa': len([a for a in alertas if a.severidade == 'baixa']),
                'media': len([a for a in alertas if a.severidade == 'media']),
                'alta': len([a for a in alertas if a.severidade == 'alta']),
                'critica': len([a for a in alertas if a.severidade == 'critica']),
            },
        }


class MonitoramentoService:
    """
    Serviço de Monitoramento Ambiental
    
    Combina análise de imagens com geração de alertas.
    """
    
    def __init__(self):
        self.alerta_service = AlertaService()
    
    def monitorar_car(
        self,
        car_id: str,
        latitude: float,
        longitude: float,
        periodo_dias: int = 30
    ) -> Dict[str, Any]:
        """
        Monitora CAR em busca de desmatamento
        
        Args:
            car_id: ID do CAR
            latitude: Latitude do centro
            longitude: Longitude do centro
            periodo_dias: Período para análise
            
        Returns:
            Dict com resultados do monitoramento
        """
        logger.info(f"Monitorando CAR {car_id}")
        
        # 1. Obter imagens Sentinel-2 do período
        # (implementação via Sentinel2Service)
        
        # 2. Calcular NDVI das imagens
        
        # 3. Detectar mudanças
        
        # 4. Gerar alertas
        
        return {
            'car_id': car_id,
            'periodo_dias': periodo_dias,
            'alertas_gerados': 0,
            'area_monitorada_ha': 0,
            'status': 'sucesso',
        }
    
    def gerar_relatorio_mensal(self, car_id: str, mes: int, ano: int) -> Dict[str, Any]:
        """
        Gera relatório mensal de monitoramento
        
        Args:
            car_id: ID do CAR
            mes: Mês de referência
            ano: Ano de referência
            
        Returns:
            Dict com relatório
        """
        data_inicio = datetime(ano, mes, 1)
        if mes == 12:
            data_fim = datetime(ano + 1, 1, 1)
        else:
            data_fim = datetime(ano, mes + 1, 1)
        
        alertas = self.alerta_service.listar_alertas(
            car_id=car_id,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        
        return {
            'car_id': car_id,
            'mes': mes,
            'ano': ano,
            'total_alertas': len(alertas),
            'alertas': [
                {
                    'id': a.id,
                    'data': a.data_alerta.isoformat(),
                    'area_ha': a.area_hectares,
                    'severidade': a.severidade,
                    'status': a.status,
                }
                for a in alertas
            ],
        }


class MonitoramentoFactory:
    """Factory para criar serviços"""
    
    @staticmethod
    def get_monitoramento() -> MonitoramentoService:
        """Obtém instância de serviço"""
        return MonitoramentoService()
