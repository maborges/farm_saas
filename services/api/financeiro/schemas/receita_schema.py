from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from datetime import date, datetime
import uuid

FormasRecebimento = Literal["PIX", "BOLETO", "TRANSFERENCIA", "DINHEIRO", "CARTAO", "CHEQUE"]
StatusReceita = Literal["A_RECEBER", "RECEBIDO", "RECEBIDO_PARCIAL", "CANCELADO"]


class ReceitaCreate(BaseModel):
    fazenda_id: uuid.UUID
    plano_conta_id: uuid.UUID
    descricao: str = Field(..., min_length=3, max_length=255)
    valor_total: float = Field(..., gt=0)

    data_emissao: date
    data_vencimento: date
    data_recebimento: Optional[date] = None
    competencia: Optional[date] = None

    status: StatusReceita = "A_RECEBER"
    forma_recebimento: Optional[FormasRecebimento] = None
    valor_recebido: Optional[float] = Field(None, gt=0)

    # Vínculo com Pessoas — preferível ao campo texto livre
    pessoa_id: Optional[uuid.UUID] = None
    cliente: Optional[str] = Field(None, max_length=150, description="Texto livre (usar pessoa_id quando possível)")

    # Parcelamento: se total_parcelas > 1, cria N receitas automaticamente
    total_parcelas: int = Field(1, ge=1, le=360, description="1 = sem parcelamento")

    # Fiscal
    numero_nf: Optional[str] = Field(None, max_length=20)
    serie_nf: Optional[str] = Field(None, max_length=5)
    chave_nfe: Optional[str] = Field(None, max_length=44)
    nota_fiscal: Optional[str] = Field(None, max_length=100, description="Legado")

    observacoes: Optional[str] = None


class ReceitaUpdate(BaseModel):
    descricao: Optional[str] = Field(None, min_length=3, max_length=255)
    plano_conta_id: Optional[uuid.UUID] = None
    valor_total: Optional[float] = Field(None, gt=0)
    valor_recebido: Optional[float] = Field(None, ge=0)
    data_emissao: Optional[date] = None
    data_vencimento: Optional[date] = None
    data_recebimento: Optional[date] = None
    competencia: Optional[date] = None
    status: Optional[StatusReceita] = None
    forma_recebimento: Optional[FormasRecebimento] = None
    pessoa_id: Optional[uuid.UUID] = None
    cliente: Optional[str] = Field(None, max_length=150)
    numero_nf: Optional[str] = Field(None, max_length=20)
    serie_nf: Optional[str] = Field(None, max_length=5)
    chave_nfe: Optional[str] = Field(None, max_length=44)
    observacoes: Optional[str] = None


class ReceitaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    fazenda_id: uuid.UUID
    plano_conta_id: uuid.UUID
    pessoa_id: Optional[uuid.UUID]
    descricao: str
    valor_total: float
    valor_recebido: Optional[float]
    data_emissao: date
    data_vencimento: date
    data_recebimento: Optional[date]
    competencia: Optional[date]
    status: str
    forma_recebimento: Optional[str]
    grupo_parcela_id: Optional[uuid.UUID]
    numero_parcela: Optional[int]
    total_parcelas: Optional[int]
    numero_nf: Optional[str]
    serie_nf: Optional[str]
    chave_nfe: Optional[str]
    cliente: Optional[str]
    nota_fiscal: Optional[str]
    observacoes: Optional[str]
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReceitaListItem(BaseModel):
    """Versão resumida para listagens."""
    id: uuid.UUID
    fazenda_id: uuid.UUID
    pessoa_id: Optional[uuid.UUID]
    cliente: Optional[str]
    descricao: str
    valor_total: float
    valor_recebido: Optional[float]
    data_vencimento: date
    data_recebimento: Optional[date]
    status: str
    numero_parcela: Optional[int]
    total_parcelas: Optional[int]

    model_config = ConfigDict(from_attributes=True)
