from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid

from core.dependencies import get_session, get_current_tenant
from core.exceptions import BusinessRuleError, EntityNotFoundError
from core.models.tenant import Tenant
from operacional.models.frota import OrdemServico, ItemOrdemServico, RegistroManutencao, Maquinario
from operacional.schemas.frota import (
    OrdemServicoCreate, OrdemServicoUpdate, OrdemServicoResponse,
    ItemOrdemServicoCreate, ItemOrdemServicoResponse,
    RegistroManutencaoResponse, StatusOS,
)
from operacional.services.frota_service import FrotaService

router = APIRouter(prefix="/oficina", tags=["Operacional — Oficina"])


def _svc(session: AsyncSession, tenant: Tenant) -> FrotaService:
    return FrotaService(session, tenant.id)


# ── Ordens de Serviço ─────────────────────────────────────────────────────────

@router.get("/os", response_model=List[OrdemServicoResponse])
async def listar_ordens_servico(
    maquinario_id: Optional[uuid.UUID] = Query(None),
    status: Optional[StatusOS] = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(OrdemServico).where(
        OrdemServico.tenant_id == tenant.id
    ).order_by(OrdemServico.data_abertura.desc())
    if maquinario_id:
        stmt = stmt.where(OrdemServico.maquinario_id == maquinario_id)
    if status:
        stmt = stmt.where(OrdemServico.status == status)
    return list((await session.execute(stmt)).scalars().all())


@router.post("/os", response_model=OrdemServicoResponse, status_code=201)
async def abrir_os(
    data: OrdemServicoCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    # Valida maquinário pertence ao tenant
    stmt = select(Maquinario).where(
        Maquinario.id == data.maquinario_id, Maquinario.tenant_id == tenant.id
    )
    maq = (await session.execute(stmt)).scalar_one_or_none()
    if not maq:
        raise EntityNotFoundError(f"Maquinário {data.maquinario_id} não encontrado.")

    svc = _svc(session, tenant)
    os = await svc.abrir_os(data)  # já faz commit internamente
    return os


@router.get("/os/{os_id}", response_model=OrdemServicoResponse)
async def detalhar_os(
    os_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(OrdemServico).where(
        OrdemServico.id == os_id, OrdemServico.tenant_id == tenant.id
    )
    os = (await session.execute(stmt)).scalar_one_or_none()
    if not os:
        raise EntityNotFoundError(f"OS {os_id} não encontrada.")
    return os


@router.patch("/os/{os_id}", response_model=OrdemServicoResponse)
async def atualizar_os(
    os_id: uuid.UUID,
    data: OrdemServicoUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Atualiza diagnóstico técnico e custo de mão de obra. Para mudar status use os endpoints específicos."""
    stmt = select(OrdemServico).where(
        OrdemServico.id == os_id, OrdemServico.tenant_id == tenant.id
    )
    os = (await session.execute(stmt)).scalar_one_or_none()
    if not os:
        raise EntityNotFoundError(f"OS {os_id} não encontrada.")
    if os.status in ("CONCLUIDA", "CANCELADA"):
        raise BusinessRuleError(f"OS {os.numero_os} já está {os.status} e não pode ser alterada.")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(os, field, value)
    session.add(os)
    await session.commit()
    await session.refresh(os)
    return os


@router.patch("/os/{os_id}/iniciar", response_model=OrdemServicoResponse)
async def iniciar_os(
    os_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Muda status de ABERTA para EM_EXECUCAO."""
    stmt = select(OrdemServico).where(
        OrdemServico.id == os_id, OrdemServico.tenant_id == tenant.id
    )
    os = (await session.execute(stmt)).scalar_one_or_none()
    if not os:
        raise EntityNotFoundError(f"OS {os_id} não encontrada.")
    if os.status != "ABERTA":
        raise BusinessRuleError(f"OS deve estar ABERTA para iniciar. Status atual: {os.status}")

    os.status = "EM_EXECUCAO"
    session.add(os)
    await session.commit()
    await session.refresh(os)
    return os


@router.patch("/os/{os_id}/cancelar", response_model=OrdemServicoResponse)
async def cancelar_os(
    os_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(OrdemServico).where(
        OrdemServico.id == os_id, OrdemServico.tenant_id == tenant.id
    )
    os = (await session.execute(stmt)).scalar_one_or_none()
    if not os:
        raise EntityNotFoundError(f"OS {os_id} não encontrada.")
    if os.status == "CONCLUIDA":
        raise BusinessRuleError("OS concluída não pode ser cancelada.")

    # Reativa maquinário
    maq = await session.get(Maquinario, os.maquinario_id)
    if maq and maq.status == "MANUTENCAO":
        maq.status = "ATIVO"
        session.add(maq)

    os.status = "CANCELADA"
    session.add(os)
    await session.commit()
    await session.refresh(os)
    return os


@router.patch("/os/{os_id}/fechar", response_model=OrdemServicoResponse)
async def fechar_os(
    os_id: uuid.UUID,
    data: OrdemServicoUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """
    Conclui a OS:
    - Baixa estoque de todas as peças adicionadas
    - Reativa o maquinário
    - Gera registro histórico de manutenção
    """
    svc = _svc(session, tenant)
    return await svc.fechar_os(os_id, data)  # já faz commit + saída de estoque


# ── Itens da OS ───────────────────────────────────────────────────────────────

@router.get("/os/{os_id}/itens", response_model=List[ItemOrdemServicoResponse])
async def listar_itens_os(
    os_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    # Valida tenant via join
    stmt = select(OrdemServico).where(
        OrdemServico.id == os_id, OrdemServico.tenant_id == tenant.id
    )
    if not (await session.execute(stmt)).scalar_one_or_none():
        raise EntityNotFoundError(f"OS {os_id} não encontrada.")

    stmt_itens = select(ItemOrdemServico).where(ItemOrdemServico.os_id == os_id)
    return list((await session.execute(stmt_itens)).scalars().all())


@router.post("/os/{os_id}/itens", response_model=ItemOrdemServicoResponse, status_code=201)
async def adicionar_item_os(
    os_id: uuid.UUID,
    data: ItemOrdemServicoCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Adiciona peça/insumo à OS. O estoque é baixado apenas ao fechar a OS."""
    svc = _svc(session, tenant)
    return await svc.adicionar_item_os(os_id, data)  # commit interno


@router.delete("/os/{os_id}/itens/{item_id}", status_code=204)
async def remover_item_os(
    os_id: uuid.UUID,
    item_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Remove item da OS enquanto ainda está ABERTA ou EM_EXECUCAO."""
    # Valida tenant e status
    stmt_os = select(OrdemServico).where(
        OrdemServico.id == os_id, OrdemServico.tenant_id == tenant.id
    )
    os = (await session.execute(stmt_os)).scalar_one_or_none()
    if not os:
        raise EntityNotFoundError(f"OS {os_id} não encontrada.")
    if os.status in ("CONCLUIDA", "CANCELADA"):
        raise BusinessRuleError("Não é possível remover itens de uma OS finalizada.")

    stmt_item = select(ItemOrdemServico).where(
        ItemOrdemServico.id == item_id, ItemOrdemServico.os_id == os_id
    )
    item = (await session.execute(stmt_item)).scalar_one_or_none()
    if not item:
        raise EntityNotFoundError(f"Item {item_id} não encontrado na OS.")

    # Recalcula custo de peças
    os.custo_total_pecas -= item.quantidade * item.preco_unitario_na_data
    os.custo_total_pecas = max(0.0, round(os.custo_total_pecas, 2))
    session.add(os)
    await session.delete(item)
    await session.commit()


# ── Histórico de manutenção ───────────────────────────────────────────────────

@router.get("/maquinarios/{maquinario_id}/historico", response_model=List[RegistroManutencaoResponse])
async def historico_manutencao(
    maquinario_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    # Valida maquinário do tenant
    stmt_maq = select(Maquinario).where(
        Maquinario.id == maquinario_id, Maquinario.tenant_id == tenant.id
    )
    if not (await session.execute(stmt_maq)).scalar_one_or_none():
        raise EntityNotFoundError(f"Maquinário {maquinario_id} não encontrado.")

    stmt = (
        select(RegistroManutencao)
        .where(RegistroManutencao.maquinario_id == maquinario_id)
        .order_by(RegistroManutencao.data_realizacao.desc())
        .limit(limit)
    )
    return list((await session.execute(stmt)).scalars().all())
