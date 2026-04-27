"""
Backoffice — Unidades de Medida (UoM) — Step 21c

Escopo: gerencia unidades_medida e unidades_medida_conversoes GLOBAIS do sistema
        (tenant_id = NULL, sistema = True).

Modelo de escopo:
  tenant_id = NULL  →  UoM global — disponível para todos os tenants.
  tenant_id = <id>  →  UoM customizada por tenant — fora deste escopo.

Regras de canônica:
  Cada dimensão (massa, volume, area…) tem exatamente 1 unidade canônica
  (eh_canonica=True, fator_canonico=1). As demais expressam seu fator em
  relação à canônica. Ex: SC60 → massa → fator_canonico=60 (60 kg).

Conversões (unidades_medida_conversoes):
  cultura = NULL  →  conversão genérica, válida para qualquer cultura.
  cultura = 'CAFE' →  conversão específica, prevalece sobre a genérica.
  Par (origem, destino, cultura) é único por escopo (DB: uq_unidades_medida_conversoes_escopo).

Garantias do banco (Step 14):
  • uq_unidades_medida_codigo_global     — código único por escopo global
  • uq_unidades_medida_canonica_global   — 1 canônica por dimensão global
  • uq_unidades_medida_conversoes_escopo — par (origem, destino, cultura) único
  • ck_unidades_medida_conversoes_fator_positivo
  • ck_unidades_medida_conversoes_unidades_distintas

Permissão exigida: backoffice:uom:gerenciar
"""
from __future__ import annotations

import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_current_admin, require_permission
from core.measurements.models import UnidadeMedida, UnidadeMedidaConversao

_PERM = "backoffice:uom:gerenciar"

router = APIRouter(
    prefix="/backoffice/uom",
    tags=["Backoffice — Unidades de Medida"],
    dependencies=[Depends(get_current_admin)],
)

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class UomCreate(BaseModel):
    codigo: str = Field(..., max_length=16, description="Código único da UoM. Normalizado para UPPERCASE.")
    nome: str = Field(..., max_length=80)
    dimensao: str = Field(..., max_length=24, description="Ex: massa, volume, area, moeda, contagem")
    codigo_canonico: str = Field(..., max_length=16, description="Código da UoM canônica desta dimensão")
    fator_canonico: float = Field(..., gt=0, description="Quantidade de unidades canônicas que 1 desta UoM equivale")
    casas_decimais: int = Field(2, ge=0, le=6)
    eh_canonica: bool = Field(False, description="True apenas para a unidade-base da dimensão (fator_canonico deve ser 1)")
    ativo: bool = True

    @field_validator("codigo", "codigo_canonico", mode="before")
    @classmethod
    def normalizar_codigo(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("dimensao", mode="before")
    @classmethod
    def normalizar_dimensao(cls, v: str) -> str:
        return v.strip().lower()


class UomUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=80)
    dimensao: Optional[str] = Field(None, max_length=24)
    codigo_canonico: Optional[str] = Field(None, max_length=16)
    fator_canonico: Optional[float] = Field(None, gt=0)
    casas_decimais: Optional[int] = Field(None, ge=0, le=6)
    eh_canonica: Optional[bool] = None
    ativo: Optional[bool] = None

    @field_validator("codigo_canonico", mode="before")
    @classmethod
    def normalizar_codigo(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().upper() if v else v

    @field_validator("dimensao", mode="before")
    @classmethod
    def normalizar_dimensao(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if v else v


class UomResponse(BaseModel):
    id: uuid.UUID
    codigo: str
    nome: str
    dimensao: str
    codigo_canonico: str
    fator_canonico: float
    casas_decimais: int
    eh_canonica: bool
    sistema: bool
    ativo: bool
    tenant_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversaoCreate(BaseModel):
    unidade_origem_id: uuid.UUID
    unidade_destino_id: uuid.UUID
    fator: float = Field(..., gt=0, description="Quantidade de unidades destino por 1 unidade origem")
    cultura: Optional[str] = Field(
        None, max_length=100,
        description="NULL = conversão genérica. Ex: 'CAFE' = específica para café. Prevalece sobre NULL.",
    )
    observacoes: Optional[str] = None

    @model_validator(mode="after")
    def validar_unidades_distintas(self) -> "ConversaoCreate":
        if self.unidade_origem_id == self.unidade_destino_id:
            raise ValueError("Unidade de origem e destino devem ser diferentes.")
        return self

    @field_validator("cultura", mode="before")
    @classmethod
    def normalizar_cultura(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().upper() if v else None


class ConversaoUpdate(BaseModel):
    fator: Optional[float] = Field(None, gt=0)
    cultura: Optional[str] = Field(None, max_length=100)
    observacoes: Optional[str] = None

    @field_validator("cultura", mode="before")
    @classmethod
    def normalizar_cultura(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().upper() if v else None


class ConversaoResponse(BaseModel):
    id: uuid.UUID
    unidade_origem_id: uuid.UUID
    unidade_destino_id: uuid.UUID
    fator: float
    cultura: Optional[str]
    observacoes: Optional[str]
    tenant_id: Optional[uuid.UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_uom_or_404(session: AsyncSession, uom_id: uuid.UUID) -> UnidadeMedida:
    stmt = select(UnidadeMedida).where(
        and_(UnidadeMedida.id == uom_id, UnidadeMedida.tenant_id.is_(None))
    )
    uom = (await session.execute(stmt)).scalar_one_or_none()
    if not uom:
        raise HTTPException(status_code=404, detail="Unidade de medida não encontrada.")
    return uom


async def _get_conversao_or_404(session: AsyncSession, conv_id: uuid.UUID) -> UnidadeMedidaConversao:
    stmt = select(UnidadeMedidaConversao).where(
        and_(UnidadeMedidaConversao.id == conv_id, UnidadeMedidaConversao.tenant_id.is_(None))
    )
    conv = (await session.execute(stmt)).scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversão não encontrada.")
    return conv


async def _assert_canonica_livre(
    session: AsyncSession, dimensao: str, exclude_id: uuid.UUID | None = None
) -> None:
    """Garante que não existe outra canônica global para a dimensão."""
    stmt = select(UnidadeMedida.id).where(
        and_(
            UnidadeMedida.dimensao == dimensao,
            UnidadeMedida.eh_canonica == True,  # noqa: E712
            UnidadeMedida.tenant_id.is_(None),
        )
    )
    if exclude_id:
        stmt = stmt.where(UnidadeMedida.id != exclude_id)
    if (await session.execute(stmt)).scalar_one_or_none():
        raise HTTPException(
            status_code=422,
            detail=f"Já existe uma unidade canônica para a dimensão '{dimensao}'. "
                   "Altere a existente para eh_canonica=False antes de promover outra.",
        )


# ---------------------------------------------------------------------------
# UoM endpoints
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[UomResponse])
async def list_uom(
    dimensao: Optional[str] = None,
    ativo: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_permission(_PERM)),
):
    """Lista UoMs globais (tenant_id=NULL). Filtrável por dimensão e ativo."""
    stmt = select(UnidadeMedida).where(UnidadeMedida.tenant_id.is_(None))
    if dimensao:
        stmt = stmt.where(UnidadeMedida.dimensao == dimensao.strip().lower())
    if ativo is not None:
        stmt = stmt.where(UnidadeMedida.ativo == ativo)
    stmt = stmt.order_by(UnidadeMedida.dimensao, UnidadeMedida.codigo)
    return list((await session.execute(stmt)).scalars().all())


@router.post("/", response_model=UomResponse, status_code=status.HTTP_201_CREATED)
async def create_uom(
    data: UomCreate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_permission(_PERM)),
):
    """
    Cria UoM global de sistema (tenant_id=NULL, sistema=True).
    Código é normalizado para UPPERCASE antes de persistir.
    """
    exists = (await session.execute(
        select(UnidadeMedida.id).where(
            and_(UnidadeMedida.codigo == data.codigo, UnidadeMedida.tenant_id.is_(None))
        )
    )).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail=f"Código '{data.codigo}' já existe.")

    if data.eh_canonica:
        await _assert_canonica_livre(session, data.dimensao)

    uom = UnidadeMedida(id=uuid.uuid4(), tenant_id=None, sistema=True, **data.model_dump())
    session.add(uom)
    await session.commit()
    await session.refresh(uom)
    return uom


@router.get("/{uom_id}", response_model=UomResponse)
async def get_uom(
    uom_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_permission(_PERM)),
):
    """Detalhe de uma UoM global."""
    return await _get_uom_or_404(session, uom_id)


@router.patch("/{uom_id}", response_model=UomResponse)
async def update_uom(
    uom_id: uuid.UUID,
    data: UomUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_permission(_PERM)),
):
    """Atualiza UoM global. Código não pode ser alterado após criação."""
    uom = await _get_uom_or_404(session, uom_id)

    if data.eh_canonica is True and not uom.eh_canonica:
        dimensao = data.dimensao or uom.dimensao
        await _assert_canonica_livre(session, dimensao, exclude_id=uom_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(uom, field, value)

    await session.commit()
    await session.refresh(uom)
    return uom


@router.delete("/{uom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_uom(
    uom_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_permission(_PERM)),
):
    """
    Soft-delete: marca ativo=False. Não remove do banco.
    FK RESTRICT impede desativação de UoMs referenciadas.
    UoM canônica não pode ser desativada sem designar outra antes.
    """
    uom = await _get_uom_or_404(session, uom_id)
    if uom.eh_canonica:
        raise HTTPException(
            status_code=422,
            detail="Unidade canônica não pode ser desativada. "
                   "Promova outra UoM como canônica desta dimensão antes.",
        )
    uom.ativo = False
    await session.commit()


# ---------------------------------------------------------------------------
# Conversões endpoints
# ---------------------------------------------------------------------------

@router.get("/conversoes/", response_model=list[ConversaoResponse])
async def list_conversoes(
    origem_id: Optional[uuid.UUID] = None,
    cultura: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_permission(_PERM)),
):
    """
    Lista conversões globais (tenant_id=NULL).
    cultura=NULL → genéricas. cultura='CAFE' → específicas para café.
    """
    stmt = select(UnidadeMedidaConversao).where(UnidadeMedidaConversao.tenant_id.is_(None))
    if origem_id:
        stmt = stmt.where(UnidadeMedidaConversao.unidade_origem_id == origem_id)
    if cultura:
        stmt = stmt.where(UnidadeMedidaConversao.cultura == cultura.strip().upper())
    stmt = stmt.order_by(UnidadeMedidaConversao.created_at)
    return list((await session.execute(stmt)).scalars().all())


@router.post("/conversoes/", response_model=ConversaoResponse, status_code=status.HTTP_201_CREATED)
async def create_conversao(
    data: ConversaoCreate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_permission(_PERM)),
):
    """
    Cria conversão global. Par (origem, destino, cultura) deve ser único.
    cultura=NULL significa conversão genérica (aplicável a qualquer cultura).
    A validação de origem != destino é feita tanto no Pydantic quanto no DB (CHECK constraint).
    """
    for uom_id in (data.unidade_origem_id, data.unidade_destino_id):
        await _get_uom_or_404(session, uom_id)

    dup = (await session.execute(
        select(UnidadeMedidaConversao.id).where(
            and_(
                UnidadeMedidaConversao.unidade_origem_id == data.unidade_origem_id,
                UnidadeMedidaConversao.unidade_destino_id == data.unidade_destino_id,
                UnidadeMedidaConversao.cultura == data.cultura,
                UnidadeMedidaConversao.tenant_id.is_(None),
            )
        )
    )).scalar_one_or_none()
    if dup:
        raise HTTPException(
            status_code=409,
            detail="Conversão para este par (origem, destino, cultura) já existe.",
        )

    conv = UnidadeMedidaConversao(id=uuid.uuid4(), tenant_id=None, **data.model_dump())
    session.add(conv)
    await session.commit()
    await session.refresh(conv)
    return conv


@router.patch("/conversoes/{conv_id}", response_model=ConversaoResponse)
async def update_conversao(
    conv_id: uuid.UUID,
    data: ConversaoUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_permission(_PERM)),
):
    """Atualiza fator, cultura ou observações de uma conversão global."""
    conv = await _get_conversao_or_404(session, conv_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(conv, field, value)
    await session.commit()
    await session.refresh(conv)
    return conv


@router.delete("/conversoes/{conv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversao(
    conv_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_permission(_PERM)),
):
    """Hard delete de conversão global. FK RESTRICT protege UoMs em uso."""
    conv = await _get_conversao_or_404(session, conv_id)
    await session.delete(conv)
    await session.commit()
