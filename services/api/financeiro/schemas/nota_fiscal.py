"""
Schemas Pydantic para Notas Fiscais (NFP-e e NF-e)

Schemas de validação e serialização para o módulo de notas fiscais.
"""

from pydantic import BaseModel, Field, validator, constr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import re


class TipoNotaFiscalEnum(str, Enum):
    """Tipo de nota fiscal"""
    NFP_E = "NFP-e"
    NF_E = "NF-e"
    NFC_E = "NFC-e"


class StatusSEFAZEnum(str, Enum):
    """Status da nota na SEFAZ"""
    EM_DIGITACAO = "em_digitacao"
    ASSINADA = "assinada"
    TRANSMITIDA = "transmitida"
    AUTORIZADA = "autorizada"
    CANCELADA = "cancelada"
    DENEGADA = "denegada"
    INUTILIZADA = "inutilizada"


class DestinatarioTipoEnum(str, Enum):
    """Tipo de destinatário"""
    PF = "PF"
    PJ = "PJ"


# ============ Schemas de Item ============

class NotaFiscalItemBase(BaseModel):
    """Schema base para item da nota fiscal"""
    codigo: str = Field(..., description="Código do produto", max_length=60)
    descricao: str = Field(..., description="Descrição do produto", max_length=120)
    ncm: str = Field(..., description="Código NCM", pattern=r'^\d{8}$')
    cfop: str = Field(..., description="Código CFOP", pattern=r'^\d{4}$')
    quantidade: float = Field(..., description="Quantidade", gt=0)
    unidade: str = Field(..., description="Unidade de medida", max_length=6)
    valor_unitario: float = Field(..., description="Valor unitário", ge=0)
    origem: str = Field(default="0", description="Origem da mercadoria", pattern=r'^[0-9]$')
    
    # Impostos
    csosn: Optional[str] = Field(None, description="CSOSN", max_length=3)
    cst: Optional[str] = Field(None, description="CST", max_length=2)
    aliq_icms: float = Field(default=0.0, description="Alíquota ICMS", ge=0, le=100)
    aliq_ipi: float = Field(default=0.0, description="Alíquota IPI", ge=0, le=100)
    aliq_pis: float = Field(default=0.0, description="Alíquota PIS", ge=0, le=100)
    aliq_cofins: float = Field(default=0.0, description="Alíquota COFINS", ge=0, le=100)
    
    class Config:
        schema_extra = {
            "example": {
                "codigo": "001",
                "descricao": "Soja em grão",
                "ncm": "12019000",
                "cfop": "5101",
                "quantidade": 1000.00,
                "unidade": "SC",
                "valor_unitario": 150.00,
                "origem": "0",
                "csosn": "102",
                "aliq_icms": 0.0
            }
        }


class NotaFiscalItemCreate(NotaFiscalItemBase):
    """Schema para criação de item"""
    pass


class NotaFiscalItemResponse(NotaFiscalItemBase):
    """Schema para resposta de item"""
    valor_total: float = Field(..., description="Valor total do item")
    
    class Config:
        orm_mode = True


# ============ Schemas de Endereço ============

class EnderecoDestinatario(BaseModel):
    """Schema de endereço do destinatário"""
    logradouro: Optional[str] = Field(None, max_length=200)
    numero: Optional[str] = Field(None, max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    municipio: Optional[str] = Field(None, max_length=100)
    uf: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, pattern=r'^\d{5}-?\d{3}$')
    pais: Optional[str] = Field(default="Brasil", max_length=50)
    cod_municipio: Optional[str] = Field(None, pattern=r'^\d{7}$')
    
    class Config:
        schema_extra = {
            "example": {
                "logradouro": "Rua das Flores",
                "numero": "123",
                "bairro": "Centro",
                "municipio": "São Paulo",
                "uf": "SP",
                "cep": "01234-567"
            }
        }


# ============ Schemas de Transporte ============

class Transportadora(BaseModel):
    """Schema de transportadora"""
    nome: Optional[str] = Field(None, max_length=200)
    cnpj_cpf: Optional[str] = Field(None, pattern=r'^\d{11,14}$')
    ie: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = Field(None, max_length=200)
    municipio: Optional[str] = Field(None, max_length=100)
    uf: Optional[str] = Field(None, max_length=2)
    
    class Config:
        schema_extra = {
            "example": {
                "nome": "Transportadora Silva",
                "cnpj_cpf": "12345678000190",
                "ie": "123456789"
            }
        }


class VeiculoTransporte(BaseModel):
    """Schema de veículo de transporte"""
    placa: Optional[str] = Field(None, pattern=r'^[A-Z]{3}\d{4}$')
    uf: Optional[str] = Field(None, max_length=2)
    rntc: Optional[str] = Field(None, max_length=20)
    
    class Config:
        schema_extra = {
            "example": {
                "placa": "ABC1234",
                "uf": "SP"
            }
        }


# ============ Schemas Principais ============

class NotaFiscalBase(BaseModel):
    """Schema base para Nota Fiscal"""
    tipo: TipoNotaFiscalEnum = Field(default=TipoNotaFiscalEnum.NFP_E)
    serie: constr(max_length=10) = Field(default="1")
    data_saida_entrada: Optional[datetime] = None
    
    # Emitente
    emitente_id: Optional[str] = None
    emitente_nome: str = Field(..., max_length=200)
    emitente_cnpj_cpf: str = Field(..., pattern=r'^\d{11,14}$')
    emitente_ie: Optional[str] = Field(None, max_length=20)
    emitente_im: Optional[str] = Field(None, max_length=20)
    
    # Destinatário
    destinatario_tipo: DestinatarioTipoEnum
    destinatario_nome: str = Field(..., max_length=200)
    destinatario_documento: str = Field(..., pattern=r'^\d{11,14}$')
    destinatario_ie: Optional[str] = Field(None, max_length=20)
    destinatario_email: Optional[str] = Field(None, max_length=120)
    destinatario_telefone: Optional[str] = Field(None, max_length=20)
    
    # Valores
    valor_frete: float = Field(default=0.0, ge=0)
    valor_seguro: float = Field(default=0.0, ge=0)
    valor_descontos: float = Field(default=0.0, ge=0)
    valor_outras_despesas: float = Field(default=0.0, ge=0)
    
    # Informações adicionais
    info_adicionais_fisco: Optional[str] = Field(None, max_length=255)
    info_adicionais_contribuinte: Optional[str] = Field(None, max_length=255)
    
    # Safra (para NFP-e)
    safra_id: Optional[str] = None
    codigo_agricultor: Optional[str] = Field(None, max_length=20)


class NotaFiscalCreate(NotaFiscalBase):
    """Schema para criação de Nota Fiscal"""
    tenant_id: str
    numero: int = Field(..., gt=0)
    itens: List[NotaFiscalItemCreate] = Field(..., min_items=1)
    endereco_destinatario: Optional[EnderecoDestinatario] = None
    transportadora: Optional[Transportadora] = None
    veiculo: Optional[VeiculoTransporte] = None
    modalidade_frete: Optional[int] = Field(None, ge=0, le=4)
    
    @validator('itens')
    def validar_itens(cls, v):
        if len(v) == 0:
            raise ValueError('A nota fiscal deve ter pelo menos 1 item')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "tipo": "NFP-e",
                "numero": 1,
                "serie": "1",
                "emitente_nome": "Fazenda Santa Maria",
                "emitente_cnpj_cpf": "12345678000190",
                "destinatario_tipo": "PJ",
                "destinatario_nome": "Cerealista Silva Ltda",
                "destinatario_documento": "12345678000190",
                "itens": [
                    {
                        "codigo": "001",
                        "descricao": "Soja em grão",
                        "ncm": "12019000",
                        "cfop": "5101",
                        "quantidade": 1000.00,
                        "unidade": "SC",
                        "valor_unitario": 150.00,
                        "origem": "0",
                        "csosn": "102"
                    }
                ]
            }
        }


class NotaFiscalUpdate(BaseModel):
    """Schema para atualização de Nota Fiscal"""
    tipo: Optional[TipoNotaFiscalEnum] = None
    serie: Optional[str] = Field(None, max_length=10)
    data_saida_entrada: Optional[datetime] = None
    emitente_nome: Optional[str] = Field(None, max_length=200)
    destinatario_nome: Optional[str] = Field(None, max_length=200)
    valor_frete: Optional[float] = Field(None, ge=0)
    valor_seguro: Optional[float] = Field(None, ge=0)
    valor_descontos: Optional[float] = Field(None, ge=0)
    info_adicionais_fisco: Optional[str] = Field(None, max_length=255)
    info_adicionais_contribuinte: Optional[str] = Field(None, max_length=255)
    
    class Config:
        orm_mode = True


class NotaFiscalResponse(NotaFiscalBase):
    """Schema para resposta de Nota Fiscal"""
    id: str
    tenant_id: str
    numero: int
    data_emissao: datetime
    data_autorizacao: Optional[datetime] = None
    valor_total: float
    valor_produtos: float
    valor_tributos: float
    valor_icms: float
    valor_pis: float
    valor_cofins: float
    itens: List[NotaFiscalItemResponse]
    chave_acesso: Optional[str] = None
    status_sefaz: StatusSEFAZEnum
    numero_recibo: Optional[str] = None
    numero_protocolo: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "tipo": "NFP-e",
                "numero": 1,
                "serie": "1",
                "data_emissao": "2026-03-31T10:00:00",
                "emitente_nome": "Fazenda Santa Maria",
                "destinatario_nome": "Cerealista Silva Ltda",
                "valor_total": 150000.00,
                "valor_produtos": 150000.00,
                "status_sefaz": "autorizada",
                "chave_acesso": "35260312345678000190550010000000010000000000"
            }
        }


class NotaFiscalListaResponse(BaseModel):
    """Schema para lista de notas fiscais"""
    total: int
    page: int
    page_size: int
    total_pages: int
    itens: List[NotaFiscalResponse]
    
    class Config:
        orm_mode = True


class NotaFiscalEmissaoResponse(BaseModel):
    """Schema para resposta de emissão de nota"""
    sucesso: bool
    mensagem: str
    chave_acesso: Optional[str] = None
    numero_recibo: Optional[str] = None
    numero_protocolo: Optional[str] = None
    data_autorizacao: Optional[datetime] = None
    xml: Optional[str] = None
    danfe: Optional[str] = None
    
    class Config:
        orm_mode = True


class NotaFiscalCancelamentoRequest(BaseModel):
    """Schema para solicitação de cancelamento"""
    justificativa: str = Field(..., min_length=15, max_length=255)
    
    class Config:
        schema_extra = {
            "example": {
                "justificativa": "Nota fiscal emitida por engano, solicitamos o cancelamento."
            }
        }


class NotaFiscalCancelamentoResponse(BaseModel):
    """Schema para resposta de cancelamento"""
    sucesso: bool
    mensagem: str
    numero_protocolo: Optional[str] = None
    data_cancelamento: Optional[datetime] = None
    
    class Config:
        orm_mode = True
