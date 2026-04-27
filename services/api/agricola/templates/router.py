from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from core.constants import PlanTier
from core.database import get_db
from core.dependencies import get_current_user, get_tenant_id, require_module, require_tier
from agricola.templates.schemas import (
    PhaseTemplateRead, PhaseTemplateDetail, PhaseTemplateCreate, PhaseTemplateUpdate,
    OperationTemplateRead, OperationTemplateDetail, OperationTemplateCreate, OperationTemplateUpdate,
    ApplyPhaseTemplateRequest, ApplyOperationTemplateRequest,
    PhaseTemplateChecklistItemRead, PhaseTemplateChecklistItemCreate,
    PhaseTemplateTaskRead, PhaseTemplateTaskCreate,
    PhaseGateRuleRead, PhaseGateRuleCreate
)
from agricola.templates.service import (
    PhaseTemplateService, OperationTemplateService, TemplateApplicationService
)

router = APIRouter(
    prefix="/templates",
    tags=["Templates Agrícolas"],
    dependencies=[
        Depends(require_module("A1_PLANEJAMENTO")),
        Depends(require_tier(PlanTier.PROFISSIONAL)),
    ],
)


# --- Phase Templates ---

@router.get("/phase", response_model=List[PhaseTemplateRead])
async def listar_phase_templates(
    cultura: str | None = None,
    fase: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id)
):
    service = PhaseTemplateService(db, tenant_id)
    return await service.listar(cultura, fase)

@router.get("/phase/{id}", response_model=PhaseTemplateDetail)
async def obter_phase_template(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id)
):
    service = PhaseTemplateService(db, tenant_id)
    return await service.get_with_details(id)

@router.post("/phase", response_model=PhaseTemplateRead)
async def criar_phase_template(
    dados: PhaseTemplateCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id)
):
    service = PhaseTemplateService(db, tenant_id)
    return await service.create(dados)

@router.put("/phase/{id}", response_model=PhaseTemplateRead)
async def atualizar_phase_template(
    id: UUID,
    dados: PhaseTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id)
):
    service = PhaseTemplateService(db, tenant_id)
    return await service.update(id, dados)

@router.post("/phase/{id}/duplicate", response_model=PhaseTemplateRead)
async def duplicar_phase_template(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id)
):
    service = PhaseTemplateService(db, tenant_id)
    return await service.duplicar_global(id)


# --- Operation Templates ---

@router.get("/operations", response_model=List[OperationTemplateRead])
async def listar_operation_templates(
    cultura: str | None = None,
    fase: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id)
):
    service = OperationTemplateService(db, tenant_id)
    return await service.listar(cultura, fase)

@router.get("/operations/{id}", response_model=OperationTemplateDetail)
async def obter_operation_template(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id)
):
    service = OperationTemplateService(db, tenant_id)
    return await service.get_with_details(id)

@router.post("/operations", response_model=OperationTemplateRead)
async def criar_operation_template(
    dados: OperationTemplateCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id)
):
    service = OperationTemplateService(db, tenant_id)
    return await service.create(dados)


# --- Ações de Aplicação ---

@router.post("/apply/phase")
async def aplicar_template_fase(
    dados: ApplyPhaseTemplateRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id)
):
    service = TemplateApplicationService(db, tenant_id)
    result = await service.aplicar_fase(dados.safra_id, dados.phase_template_id)
    await db.commit()
    return result

@router.post("/apply/operations")
async def aplicar_template_operacoes(
    dados: ApplyOperationTemplateRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id)
):
    service = TemplateApplicationService(db, tenant_id)
    result = await service.aplicar_operacoes(dados.safra_id, dados.operation_template_id, dados.talhao_ids)
    await db.commit()
    return result
