from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime


# ── Colaborador ───────────────────────────────────────────────────────────────

class ColaboradorCreate(BaseModel):
    nome: str
    cpf: Optional[str] = None
    cargo: Optional[str] = None
    tipo_contrato: str = "DIARISTA"
    valor_diaria: Optional[float] = None
    valor_hora: Optional[float] = None
    data_admissao: Optional[date] = None
    fazenda_id: Optional[UUID] = None
    observacoes: Optional[str] = None


class ColaboradorResponse(ColaboradorCreate):
    id: UUID
    tenant_id: UUID
    ativo: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Diária ────────────────────────────────────────────────────────────────────

class DiarariaCreate(BaseModel):
    colaborador_id: UUID
    data: date
    horas_trabalhadas: float = 8.0
    atividade: str = "GERAL"
    valor_diaria: float = Field(..., gt=0)
    fazenda_id: Optional[UUID] = None
    safra_id: Optional[UUID] = None
    observacoes: Optional[str] = None


class DiariaResponse(DiarariaCreate):
    id: UUID
    tenant_id: UUID
    status: str
    data_pagamento: Optional[date]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PagarDiariasRequest(BaseModel):
    ids: List[UUID]
    data_pagamento: Optional[date] = None


# ── Empreitada ────────────────────────────────────────────────────────────────

class EmpreitadaCreate(BaseModel):
    colaborador_id: UUID
    descricao: str
    unidade: str = "HECTARE"
    quantidade: float = Field(..., gt=0)
    valor_unitario: float = Field(..., gt=0)
    data_inicio: date
    data_fim: Optional[date] = None
    fazenda_id: Optional[UUID] = None
    safra_id: Optional[UUID] = None
    observacoes: Optional[str] = None


class EmpreitadaResponse(EmpreitadaCreate):
    id: UUID
    tenant_id: UUID
    valor_total: float
    status: str
    data_pagamento: Optional[date]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConcluirEmpreitadaRequest(BaseModel):
    quantidade_final: Optional[float] = None
    data_fim: Optional[date] = None


# ── Dashboard RH ──────────────────────────────────────────────────────────────

class DashboardRHResponse(BaseModel):
    total_colaboradores_ativos: int
    total_diaristas: int
    total_empreiteiros: int
    gasto_diarias_mes: float
    gasto_empreitadas_mes: float
    total_pendente_diarias: float
    total_pendente_empreitadas: float
    empreitadas_abertas: int
