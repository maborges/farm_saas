"""
Parser de Extrato Bancário (OFX)

Implementa parse de arquivos OFX (Open Financial Exchange)
para conciliação bancária.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from io import StringIO
import logging

logger = logging.getLogger(__name__)


@dataclass
class TransacaoOFX:
    """Representa uma transação bancária do extrato OFX"""
    
    data: datetime
    valor: float
    tipo: str  # 'C' para crédito, 'D' para débito
    descricao: str
    complemento: Optional[str] = None
    codigo_banco: Optional[str] = None
    numero_documento: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "data": self.data.isoformat(),
            "valor": self.valor,
            "tipo": self.tipo,
            "descricao": self.descricao,
            "complemento": self.complemento,
            "codigo_banco": self.codigo_banco,
            "numero_documento": self.numero_documento,
        }


@dataclass
class ExtratoBancario:
    """Representa um extrato bancário completo"""
    
    banco: str
    conta: str
    agencia: str
    saldo_inicial: float
    saldo_final: float
    data_inicial: datetime
    data_final: datetime
    transacoes: List[TransacaoOFX]
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "banco": self.banco,
            "conta": self.conta,
            "agencia": self.agencia,
            "saldo_inicial": self.saldo_inicial,
            "saldo_final": self.saldo_final,
            "data_inicial": self.data_inicial.isoformat(),
            "data_final": self.data_final.isoformat(),
            "transacoes": [t.to_dict() for t in self.transacoes],
        }


class OFXParser:
    """
    Parser de arquivos OFX
    
    Suporta OFX 2.1.1 e variações dos principais bancos brasileiros.
    """
    
    # Mapeamento de códigos de bancos brasileiros
    BANCOS = {
        "001": "Banco do Brasil",
        "104": "Caixa Econômica Federal",
        "237": "Bradesco",
        "341": "Itaú",
        "033": "Santander",
        "745": "Citibank",
        "399": "HSBC",
        "260": "NuPagamentos (Nubank)",
        "182": "Banco Inter",
    }
    
    def __init__(self):
        self.conteudo = ""
        self.linhas = []
    
    def parse_arquivo(self, arquivo_path: str) -> ExtratoBancario:
        """
        Parse de arquivo OFX
        
        Args:
            arquivo_path: Caminho para o arquivo OFX
            
        Returns:
            ExtratoBancario parseado
        """
        with open(arquivo_path, 'r', encoding='latin-1') as f:
            conteudo = f.read()
        
        return self.parse_conteudo(conteudo)
    
    def parse_conteudo(self, conteudo: str) -> ExtratoBancario:
        """
        Parse de conteúdo OFX como string
        
        Args:
            conteudo: Conteúdo do arquivo OFX
            
        Returns:
            ExtratoBancario parseado
        """
        self.conteudo = conteudo
        self.linhas = conteudo.split('\n')
        
        # Extrair informações da conta
        banco, conta, agencia = self._extrair_conta()
        
        # Extrair saldo
        saldo_inicial, saldo_final = self._extrair_saldos()
        
        # Extrair período
        data_inicial, data_final = self._extrair_periodo()
        
        # Extrair transações
        transacoes = self._extrair_transacoes()
        
        logger.info(f"OFX parseado: {len(transacoes)} transações encontradas")
        
        return ExtratoBancario(
            banco=banco,
            conta=conta,
            agencia=agencia,
            saldo_inicial=saldo_inicial,
            saldo_final=saldo_final,
            data_inicial=data_inicial,
            data_final=data_final,
            transacoes=transacoes,
        )
    
    def _extrair_conta(self) -> tuple:
        """Extrai informações da conta bancária"""
        banco = ""
        conta = ""
        agencia = ""
        
        # Padrão para encontrar informações da conta
        padrao_conta = re.compile(
            r'<ACCTID>([^<]+)',
            re.IGNORECASE
        )
        
        padrao_agencia = re.compile(
            r'<BRANCHID>([^<]+)',
            re.IGNORECASE
        )
        
        padrao_banco = re.compile(
            r'<BANKID>([^<]+)',
            re.IGNORECASE
        )
        
        # Buscar no conteúdo
        match_conta = padrao_conta.search(self.conteudo)
        match_agencia = padrao_agencia.search(self.conteudo)
        match_banco = padrao_banco.search(self.conteudo)
        
        if match_conta:
            conta = match_conta.group(1).strip()
        
        if match_agencia:
            agencia = match_agencia.group(1).strip()
        
        if match_banco:
            banco_id = match_banco.group(1).strip()
            banco = self.BANCOS.get(banco_id, f"Banco {banco_id}")
        
        # Se não encontrou, tentar padrões alternativos
        if not banco or not conta:
            self._extrair_conta_padrao_brasileiro()
        
        return banco, conta, agencia
    
    def _extrair_conta_padrao_brasileiro(self) -> tuple:
        """Extrai conta em OFX de bancos brasileiros (formato específico)"""
        # Padrão específico para alguns bancos brasileiros
        padrao = re.compile(
            r'<CONTA>([^<]+).*?<AGENCIA>([^<]+)',
            re.IGNORECASE | re.DOTALL
        )
        
        match = padrao.search(self.conteudo)
        
        if match:
            return match.group(1).strip(), match.group(2).strip()
        
        return "", ""
    
    def _extrair_saldos(self) -> tuple:
        """Extrai saldo inicial e final"""
        saldo_inicial = 0.0
        saldo_final = 0.0
        
        # Padrão para saldo final (ledger balance)
        padrao_saldo_final = re.compile(
            r'<LEDGERBAL>.*?<BALAMT>([^<]+)',
            re.IGNORECASE | re.DOTALL
        )
        
        # Padrão para saldo inicial (available balance)
        padrao_saldo_inicial = re.compile(
            r'<AVAILBAL>.*?<BALAMT>([^<]+)',
            re.IGNORECASE | re.DOTALL
        )
        
        match_saldo_final = padrao_saldo_final.search(self.conteudo)
        match_saldo_inicial = padrao_saldo_inicial.search(self.conteudo)
        
        if match_saldo_final:
            saldo_final = self._parse_valor(match_saldo_final.group(1))
        
        if match_saldo_inicial:
            saldo_inicial = self._parse_valor(match_saldo_inicial.group(1))
        
        return saldo_inicial, saldo_final
    
    def _extrair_periodo(self) -> tuple:
        """Extrai período do extrato"""
        data_inicial = None
        data_final = None
        
        # Padrão para data final
        padrao_dt_final = re.compile(
            r'<DTEND>([^<]+)',
            re.IGNORECASE
        )
        
        # Padrão para data inicial
        padrao_dt_inicial = re.compile(
            r'<DTSTART>([^<]+)',
            re.IGNORECASE
        )
        
        match_dt_final = padrao_dt_final.search(self.conteudo)
        match_dt_inicial = padrao_dt_inicial.search(self.conteudo)
        
        if match_dt_final:
            data_final = self._parse_data(match_dt_final.group(1))
        
        if match_dt_inicial:
            data_inicial = self._parse_data(match_dt_inicial.group(1))
        
        return data_inicial, data_final
    
    def _extrair_transacoes(self) -> List[TransacaoOFX]:
        """Extrai todas as transações do extrato"""
        transacoes = []
        
        # Padrão para encontrar blocos de transação
        padrao_stmtrpt = re.compile(
            r'<STMTTRN>(.*?)</STMTTRN>',
            re.IGNORECASE | re.DOTALL
        )
        
        blocos = padrao_stmtrpt.findall(self.conteudo)
        
        for bloco in blocos:
            transacao = self._parse_transacao(bloco)
            
            if transacao:
                transacoes.append(transacao)
        
        return transacoes
    
    def _parse_transacao(self, bloco: str) -> Optional[TransacaoOFX]:
        """
        Parse de um bloco de transação
        
        Args:
            bloco: Bloco XML da transação
            
        Returns:
            TransacaoOFX ou None
        """
        # Extrair tipo (TRNTYPE)
        tipo_match = re.search(r'<TRNTYPE>([^<]+)', bloco, re.IGNORECASE)
        tipo = tipo_match.group(1).strip() if tipo_match else ""
        
        # Mapear tipo OFX para crédito/débito
        tipo_cd = self._mapear_tipo(tipo)
        
        # Extrair data (DTPOSTED)
        data_match = re.search(r'<DTPOSTED>([^<]+)', bloco, re.IGNORECASE)
        data = self._parse_data(data_match.group(1)) if data_match else None
        
        # Extrair valor (TRNAMT)
        valor_match = re.search(r'<TRNAMT>([^<]+)', bloco, re.IGNORECASE)
        valor = self._parse_valor(valor_match.group(1)) if valor_match else 0.0
        
        # Extrair descrição (FITID, MEMO, NAME)
        descricao = ""
        
        nome_match = re.search(r'<NAME>([^<]+)', bloco, re.IGNORECASE)
        if nome_match:
            descricao = nome_match.group(1).strip()
        
        memo_match = re.search(r'<MEMO>([^<]+)', bloco, re.IGNORECASE)
        complemento = memo_match.group(1).strip() if memo_match else None
        
        if not descricao:
            descricao = complemento or "Transação não identificada"
        
        # Extrair documento
        fitid_match = re.search(r'<FITID>([^<]+)', bloco, re.IGNORECASE)
        numero_documento = fitid_match.group(1).strip() if fitid_match else None
        
        if not data or valor == 0.0:
            return None
        
        return TransacaoOFX(
            data=data,
            valor=abs(valor),
            tipo=tipo_cd,
            descricao=descricao,
            complemento=complemento,
            numero_documento=numero_documento,
        )
    
    def _mapear_tipo(self, tipo_ofx: str) -> str:
        """
        Mapeia tipo OFX para crédito/débito
        
        Tipos OFX comuns:
        - CREDIT: Crédito
        - DEBIT: Débito
        - INT: Juros
        - DIV: Dividendo
        - FEE: Taxa
        - SRVCHG: Taxa de serviço
        - DEP: Depósito
        - ATM: Saque ATM
        - POS: Ponto de venda
        - XFER: Transferência
        - CHECK: Cheque
        - PAYMENT: Pagamento
        - CASH: Dinheiro
        - DIRECTDEP: Depósito direto
        - DIRECTDEBIT: Débito direto
        - REPEATPMT: Pagamento repetido
        - OTHER: Outro
        """
        tipos_credito = ['CREDIT', 'DIV', 'DEP', 'XFER', 'DIRECTDEP']
        
        if tipo_ofx.upper() in tipos_credito:
            return 'C'
        else:
            return 'D'
    
    def _parse_data(self, data_str: str) -> Optional[datetime]:
        """
        Parse de data no formato OFX
        
        Formatos suportados:
        - YYYYMMDDHHMMSS
        - YYYYMMDD
        - YYYYMMDDHHMMSS[offset]
        """
        if not data_str:
            return None
        
        # Remover timezone se existir
        data_str = re.sub(r'\[.*\]', '', data_str)
        data_str = data_str.strip()
        
        # Tentar diferentes formatos
        formatos = [
            '%Y%m%d%H%M%S',  # 20260331103000
            '%Y%m%d',        # 20260331
            '%Y%m%d%H%M',    # 202603311030
        ]
        
        for formato in formatos:
            try:
                return datetime.strptime(data_str, formato)
            except ValueError:
                continue
        
        logger.warning(f"Não foi possível parsear data: {data_str}")
        return None
    
    def _parse_valor(self, valor_str: str) -> float:
        """
        Parse de valor monetário
        
        Args:
            valor_str: String com valor (ex: "1500.50" ou "-1500,50")
            
        Returns:
            Valor como float
        """
        if not valor_str:
            return 0.0
        
        valor_str = valor_str.strip()
        
        # Substituir vírgula por ponto (formato brasileiro)
        valor_str = valor_str.replace(',', '.')
        
        try:
            return float(valor_str)
        except ValueError:
            logger.warning(f"Não foi possível parsear valor: {valor_str}")
            return 0.0
    
    def validar_ofx(self) -> bool:
        """
        Valida se o conteúdo é um arquivo OFX válido
        
        Returns:
            True se válido, False caso contrário
        """
        # Verificar se tem tags OFX essenciais
        tags_essenciais = [
            '<OFX>',
            '</OFX>',
            '<SIGNONMSGSRSV1>',
            '<BANKMSGSRSV1>',
        ]
        
        for tag in tags_essenciais:
            if tag not in self.conteudo.upper():
                return False
        
        return True


class OFXParserFactory:
    """Factory para criar parsers OFX"""
    
    @staticmethod
    def get_parser() -> OFXParser:
        """Obtém instância de parser"""
        return OFXParser()
    
    @staticmethod
    def parse_arquivo(arquivo_path: str) -> ExtratoBancario:
        """Parse direto de arquivo"""
        parser = OFXParser()
        return parser.parse_arquivo(arquivo_path)
