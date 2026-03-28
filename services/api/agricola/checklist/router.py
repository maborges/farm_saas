from fastapi import APIRouter, Depends, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role, get_session_with_tenant
from agricola.checklist.schemas import (
    ChecklistTemplateCreate, ChecklistTemplateUpdate, ChecklistTemplateResponse,
    ChecklistItemConcluidoUpdate, ChecklistItemAdicionar,
    SafraChecklistItemResponse, ChecklistFaseStatus,
)
from agricola.checklist.service import ChecklistTemplateService, SafraChecklistService
from agricola.safras.models import SAFRA_FASES_ORDEM

router = APIRouter(tags=["Checklist Agrícola"])


# ─── Templates ────────────────────────────────────────────────────────────────

@router.get(
    "/checklist/templates",
    response_model=list[ChecklistTemplateResponse],
    summary="Lista templates de checklist",
)
async def listar_templates(
    cultura: str | None = None,
    fase: str | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = ChecklistTemplateService(session, tenant_id)
    return await svc.listar(cultura=cultura, fase=fase)


@router.post(
    "/checklist/templates",
    response_model=ChecklistTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria template de checklist",
)
async def criar_template(
    dados: ChecklistTemplateCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = ChecklistTemplateService(session, tenant_id)
    return await svc.criar(dados)


@router.patch(
    "/checklist/templates/{template_id}",
    response_model=ChecklistTemplateResponse,
    summary="Atualiza template de checklist",
)
async def atualizar_template(
    template_id: UUID,
    dados: ChecklistTemplateUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = ChecklistTemplateService(session, tenant_id)
    return await svc.atualizar(template_id, dados)


@router.delete(
    "/checklist/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desativa template de checklist",
)
async def desativar_template(
    template_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = ChecklistTemplateService(session, tenant_id)
    await svc.atualizar(template_id, ChecklistTemplateUpdate(ativo=False))


# ─── Checklist por safra ──────────────────────────────────────────────────────

@router.post(
    "/safras/{safra_id}/checklist/{fase}/gerar",
    response_model=list[SafraChecklistItemResponse],
    summary="Gera checklist para uma fase da safra a partir dos templates",
)
async def gerar_checklist_fase(
    safra_id: UUID,
    fase: str,
    cultura: str,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = SafraChecklistService(session, tenant_id)
    return await svc.gerar_para_fase(safra_id, cultura, fase.upper())


@router.get(
    "/safras/{safra_id}/checklist/{fase}",
    response_model=ChecklistFaseStatus,
    summary="Status do checklist de uma fase da safra",
)
async def status_checklist_fase(
    safra_id: UUID,
    fase: str,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = SafraChecklistService(session, tenant_id)
    return await svc.status_fase(safra_id, fase.upper())


@router.get(
    "/safras/{safra_id}/checklist",
    summary="Status do checklist de todas as fases da safra",
)
async def status_checklist_completo(
    safra_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = SafraChecklistService(session, tenant_id)
    return {
        fase: await svc.status_fase(safra_id, fase)
        for fase in SAFRA_FASES_ORDEM
    }


@router.patch(
    "/safras/{safra_id}/checklist/itens/{item_id}",
    response_model=SafraChecklistItemResponse,
    summary="Marca/desmarca item do checklist",
)
async def marcar_item_checklist(
    safra_id: UUID,
    item_id: UUID,
    dados: ChecklistItemConcluidoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = SafraChecklistService(session, tenant_id)
    usuario_id = UUID(user["sub"]) if user.get("sub") else None
    return await svc.marcar_item(item_id, dados.concluido, usuario_id)


@router.post(
    "/safras/{safra_id}/checklist/{fase}/itens",
    response_model=SafraChecklistItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adiciona item avulso ao checklist de uma fase",
)
async def adicionar_item_checklist(
    safra_id: UUID,
    fase: str,
    dados: ChecklistItemAdicionar,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = SafraChecklistService(session, tenant_id)
    return await svc.adicionar_item(safra_id, fase.upper(), dados)
