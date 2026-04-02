"""
Conciliação Bancária

Serviço de conciliação bancária automática entre extrato e lançamentos do sistema.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


@dataclass
class SugestaoConciliacao:
    """Representa uma sugestão de conciliação"""
    
    transacao_extrato_id: str
    lancamento_sistema_id: str
    score: float  # 0.0 a 1.0 (confiança)
    motivo: str
    diferenca_valor: float = 0.0
    diferenca_data: int = 0  # dias
    
    def to_dict(self) -> dict:
        return {
            "transacao_extrato_id": self.transacao_extrato_id,
            "lancamento_sistema_id": self.lancamento_sistema_id,
            "score": self.score,
            "motivo": self.motivo,
            "diferenca_valor": self.diferenca_valor,
            "diferenca_data": self.diferenca_data,
        }


class ConciliacaoBancariaService:
    """
    Serviço de Conciliação Bancária Automática
    
    Implementa algoritmo de matching entre transações do extrato
    e lançamentos do sistema financeiro.
    """
    
    # Pesos dos critérios de casamento
    PESO_VALOR = 0.50  # 50%
    PESO_DATA = 0.20   # 20%
    PESO_DESCRICAO = 0.30  # 30%
    
    # Tolerâncias
    TOLERANCIA_VALOR = 0.05  # 5% de diferença
    TOLERANCIA_DATA = 3  # ±3 dias
    
    def __init__(self):
        pass
    
    def conciliar(
        self,
        transacoes_extrato: List[Dict[str, Any]],
        lancamentos_sistema: List[Dict[str, Any]]
    ) -> List[SugestaoConciliacao]:
        """
        Realiza conciliação automática entre extrato e sistema
        
        Args:
            transacoes_extrato: Lista de transações do extrato bancário
            lancamentos_sistema: Lista de lançamentos do sistema financeiro
            
        Returns:
            Lista de SugestaoConciliacao ordenada por score
        """
        sugestoes = []
        
        for transacao in transacoes_extrato:
            # Pular transações já conciliadas
            if transacao.get('conciliado'):
                continue
            
            # Buscar melhor casamento para esta transação
            melhor_sugestao = self._encontrar_melhor_casamento(
                transacao,
                lancamentos_sistema
            )
            
            if melhor_sugestao and melhor_sugestao.score >= 0.6:  # Mínimo 60% confiança
                sugestoes.append(melhor_sugestao)
        
        # Ordenar por score (maior primeiro)
        sugestoes.sort(key=lambda s: s.score, reverse=True)
        
        logger.info(f"Conciliação: {len(sugestoes)} sugestões encontradas")
        
        return sugestoes
    
    def _encontrar_melhor_casamento(
        self,
        transacao: Dict[str, Any],
        lancamentos: List[Dict[str, Any]]
    ) -> Optional[SugestaoConciliacao]:
        """Encontra o melhor casamento para uma transação"""
        
        melhor_score = 0.0
        melhor_lancamento = None
        melhor_motivo = ""
        melhor_dif_valor = 0.0
        melhor_dif_data = 0
        
        for lancamento in lancamentos:
            # Pular lançamentos já conciliados
            if lancamento.get('conciliado'):
                continue
            
            # Calcular score de casamento
            score, motivo, dif_valor, dif_data = self._calcular_score(
                transacao,
                lancamento
            )
            
            if score > melhor_score:
                melhor_score = score
                melhor_lancamento = lancamento
                melhor_motivo = motivo
                melhor_dif_valor = dif_valor
                melhor_dif_data = dif_data
        
        if melhor_lancamento:
            return SugestaoConciliacao(
                transacao_extrato_id=transacao['id'],
                lancamento_sistema_id=melhor_lancamento['id'],
                score=melhor_score,
                motivo=melhor_motivo,
                diferenca_valor=melhor_dif_valor,
                diferenca_data=melhor_dif_data,
            )
        
        return None
    
    def _calcular_score(
        self,
        transacao: Dict[str, Any],
        lancamento: Dict[str, Any]
    ) -> Tuple[float, str, float, int]:
        """
        Calcula score de casamento entre transação e lançamento
        
        Returns:
            Tuple(score, motivo, diferenca_valor, diferenca_data)
        """
        scores = []
        motivos = []
        
        # 1. Score por valor (50%)
        score_valor, motivo_valor, dif_valor = self._score_valor(
            transacao.get('valor', 0),
            lancamento.get('valor', 0)
        )
        scores.append(score_valor * self.PESO_VALOR)
        motivos.append(motivo_valor)
        
        # 2. Score por data (20%)
        score_data, motivo_data, dif_data = self._score_data(
            transacao.get('data'),
            lancamento.get('data_vencimento') or lancamento.get('data')
        )
        scores.append(score_data * self.PESO_DATA)
        motivos.append(motivo_data)
        
        # 3. Score por descrição (30%)
        score_descricao, motivo_descricao = self._score_descricao(
            transacao.get('descricao', ''),
            lancamento.get('descricao', '') or lancamento.get('historico', '')
        )
        scores.append(score_descricao * self.PESO_DESCRICAO)
        motivos.append(motivo_descricao)
        
        # Score total
        score_total = sum(scores)
        
        # Montar motivo consolidado
        motivo_consolidado = "; ".join(motivos)
        
        return score_total, motivo_consolidado, dif_valor, dif_data
    
    def _score_valor(
        self,
        valor_extrato: float,
        valor_sistema: float
    ) -> Tuple[float, str, float]:
        """
        Calcula score baseado no valor
        
        Returns:
            Tuple(score, motivo, diferenca)
        """
        if valor_extrato == 0 or valor_sistema == 0:
            return 0.0, "Valor zerado", 0.0
        
        # Calcular diferença percentual
        diferenca = abs(valor_extrato - valor_sistema)
        diferenca_percentual = diferenca / max(valor_extrato, valor_sistema)
        
        # Score: 100% se igual, decresce conforme diferença
        if diferenca_percentual == 0:
            score = 1.0
            motivo = "Valor idêntico"
        elif diferenca_percentual <= self.TOLERANCIA_VALOR:
            score = 0.9
            motivo = f"Valor muito próximo (dif: {diferenca_percentual:.1%})"
        elif diferenca_percentual <= 0.10:  # 10%
            score = 0.7
            motivo = f"Valor próximo (dif: {diferenca_percentual:.1%})"
        elif diferenca_percentual <= 0.20:  # 20%
            score = 0.5
            motivo = f"Valor razoável (dif: {diferenca_percentual:.1%})"
        else:
            score = 0.2
            motivo = f"Valor diferente (dif: {diferenca_percentual:.1%})"
        
        return score, motivo, diferenca
    
    def _score_data(
        self,
        data_extrato: Any,
        data_sistema: Any
    ) -> Tuple[float, str, int]:
        """
        Calcula score baseado na data
        
        Returns:
            Tuple(score, motivo, diferenca_dias)
        """
        if not data_extrato or not data_sistema:
            return 0.0, "Data não informada", 0
        
        # Converter para datetime se necessário
        if isinstance(data_extrato, str):
            data_extrato = datetime.fromisoformat(data_extrato)
        if isinstance(data_sistema, str):
            data_sistema = datetime.fromisoformat(data_sistema)
        
        # Calcular diferença em dias
        diferenca = abs((data_extrato - data_sistema).days)
        
        if diferenca == 0:
            score = 1.0
            motivo = "Data idêntica"
        elif diferenca <= 1:
            score = 0.9
            motivo = f"Data muito próxima (±{diferenca} dia)"
        elif diferenca <= self.TOLERANCIA_DATA:
            score = 0.7
            motivo = f"Dentro da tolerância (±{diferenca} dias)"
        elif diferenca <= 7:
            score = 0.4
            motivo = f"Fora da tolerância (±{diferenca} dias)"
        else:
            score = 0.1
            motivo = f"Data muito distante (±{diferenca} dias)"
        
        return score, motivo, diferenca
    
    def _score_descricao(
        self,
        descricao_extrato: str,
        descricao_sistema: str
    ) -> Tuple[float, str]:
        """
        Calcula score baseado na descrição (similaridade de texto)
        
        Uses SequenceMatcher para similaridade de strings.
        
        Returns:
            Tuple(score, motivo)
        """
        if not descricao_extrato or not descricao_sistema:
            return 0.0, "Descrição não informada"
        
        # Normalizar strings
        desc_extrato = descricao_extrato.lower().strip()
        desc_sistema = descricao_sistema.lower().strip()
        
        # Calcular similaridade
        similaridade = SequenceMatcher(
            None,
            desc_extrato,
            desc_sistema
        ).ratio()
        
        # Extrair palavras-chave comuns
        palavras_extrato = set(desc_extrato.split())
        palavras_sistema = set(desc_sistema.split())
        palavras_comuns = palavras_extrato & palavras_sistema
        
        # Score baseado na similaridade e palavras comuns
        if similaridade >= 0.9:
            score = 1.0
            motivo = "Descrição idêntica"
        elif similaridade >= 0.7:
            score = 0.8
            motivo = f"Descrição muito similar ({similaridade:.0%})"
        elif similaridade >= 0.5:
            score = 0.6
            motivo = f"Descrição similar ({similaridade:.0%})"
        elif len(palavras_comuns) >= 2:
            score = 0.5
            motivo = f"Palavras comuns: {', '.join(palavras_comuns)}"
        elif similaridade >= 0.3:
            score = 0.3
            motivo = f"Descrição pouco similar ({similaridade:.0%})"
        else:
            score = 0.1
            motivo = "Descrições diferentes"
        
        return score, motivo
    
    def conciliar_manual(
        self,
        transacao_extrato_id: str,
        lancamento_sistema_id: str
    ) -> SugestaoConciliacao:
        """
        Cria conciliação manual (forçada pelo usuário)
        
        Args:
            transacao_extrato_id: ID da transação do extrato
            lancamento_sistema_id: ID do lançamento do sistema
            
        Returns:
            SugestaoConciliacao com score 1.0
        """
        return SugestaoConciliacao(
            transacao_extrato_id=transacao_extrato_id,
            lancamento_sistema_id=lancamento_sistema_id,
            score=1.0,
            motivo="Conciliação manual",
            diferenca_valor=0.0,
            diferenca_data=0,
        )
    
    def validar_conciliacao(
        self,
        sugestao: SugestaoConciliacao
    ) -> bool:
        """
        Valida se uma conciliação faz sentido
        
        Args:
            sugestao: Sugestão de conciliação
            
        Returns:
            True se válida, False se inválida
        """
        # Score mínimo
        if sugestao.score < 0.5:
            logger.warning(f"Score muito baixo: {sugestao.score}")
            return False
        
        # Diferença de valor muito alta
        if sugestao.diferenca_valor > (sugestao.diferenca_valor * 0.5):
            logger.warning(f"Diferença de valor muito alta")
            return False
        
        # Diferença de data muito alta
        if sugestao.diferenca_data > 15:
            logger.warning(f"Diferença de data muito alta: {sugestao.diferenca_data} dias")
            return False
        
        return True


class ConciliacaoBancariaFactory:
    """Factory para criar instâncias do serviço"""
    
    _instancia = None
    
    @classmethod
    def get_service(cls) -> ConciliacaoBancariaService:
        """Obtém instância singleton do serviço"""
        if cls._instancia is None:
            cls._instancia = ConciliacaoBancariaService()
        return cls._instancia
