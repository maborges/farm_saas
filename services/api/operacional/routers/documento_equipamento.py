import uuid
from typing import Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id, require_module
from core.exceptions import EntityNotFoundError
from operacional.models.documento_equipamento import DocumentoEquipamento
from operacional.schemas.documento_equipamento import (
    DocumentoEquipamentoCreate, DocumentoEquipamentoUpdate, DocumentoEquipamentoResponse
)

router = APIRouter(
    prefix="/frota/documentos",
    tags=["Frota — Documentos de Equipamentos"],
    dependencies=[Depends(require_module("O1"))],
)


@router.get("/", response_model=list[DocumentoEquipamentoResponse])
@router.get("", response_model=list[DocumentoEquipamentoResponse])
async def listar(
    equipamento_id: Optional[uuid.UUID] = Query(None),
    tipo: Optional[str] = Query(None),
    apenas_ativos: bool = Query(True),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(DocumentoEquipamento).where(DocumentoEquipamento.tenant_id == tenant_id)
    if equipamento_id:
        stmt = stmt.where(DocumentoEquipamento.equipamento_id == equipamento_id)
    if tipo:
        stmt = stmt.where(DocumentoEquipamento.tipo == tipo)
    if apenas_ativos:
        stmt = stmt.where(DocumentoEquipamento.ativo == True)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get("/vencendo", response_model=list[DocumentoEquipamentoResponse])
async def vencendo_em_breve(
    dias: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Retorna documentos que vencem nos próximos N dias (padrão 30)."""
    hoje = date.today()
    limite = hoje + timedelta(days=dias)
    stmt = select(DocumentoEquipamento).where(
        and_(
            DocumentoEquipamento.tenant_id == tenant_id,
            DocumentoEquipamento.ativo == True,
            DocumentoEquipamento.data_vencimento != None,
            DocumentoEquipamento.data_vencimento <= limite,
        )
    ).order_by(DocumentoEquipamento.data_vencimento)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/", response_model=DocumentoEquipamentoResponse, status_code=201)
@router.post("", response_model=DocumentoEquipamentoResponse, status_code=201)
async def criar(
    data: DocumentoEquipamentoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    obj = DocumentoEquipamento(tenant_id=tenant_id, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("/{doc_id}", response_model=DocumentoEquipamentoResponse)
async def obter(
    doc_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(DocumentoEquipamento).where(
            DocumentoEquipamento.id == doc_id, DocumentoEquipamento.tenant_id == tenant_id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Documento não encontrado")
    return obj


@router.patch("/{doc_id}", response_model=DocumentoEquipamentoResponse)
async def atualizar(
    doc_id: uuid.UUID,
    data: DocumentoEquipamentoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(DocumentoEquipamento).where(
            DocumentoEquipamento.id == doc_id, DocumentoEquipamento.tenant_id == tenant_id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Documento não encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/{doc_id}", status_code=204)
async def remover(
    doc_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    result = await session.execute(
        select(DocumentoEquipamento).where(
            DocumentoEquipamento.id == doc_id, DocumentoEquipamento.tenant_id == tenant_id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Documento não encontrado")
    obj.ativo = False  # soft delete
    await session.commit()
