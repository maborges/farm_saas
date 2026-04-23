from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from core.database import get_db
from core.dependencies import get_current_admin
from sqlalchemy.future import select
from agricola.models.templates import (
    PhaseTemplateChecklistItem, PhaseTemplateTask,
    PhaseGateRule, OperationTemplateItem, OperationDependency
)
from agricola.templates.schemas import (
    PhaseTemplateRead, PhaseTemplateDetail, PhaseTemplateCreate, PhaseTemplateUpdate,
    PhaseTemplateChecklistItemRead, PhaseTemplateChecklistItemCreate,
    PhaseTemplateTaskRead, PhaseTemplateTaskCreate,
    PhaseGateRuleRead, PhaseGateRuleCreate,
    OperationTemplateRead, OperationTemplateDetail, OperationTemplateCreate, OperationTemplateUpdate,
    OperationTemplateItemRead, OperationTemplateItemCreate
)
from agricola.templates.service import PhaseTemplateService, OperationTemplateService

router = APIRouter(prefix="/backoffice/tabelas/agro-templates", tags=["Backoffice - Templates Agrícolas"])

@router.get("/{id}", response_model=PhaseTemplateDetail | OperationTemplateDetail)
async def get_template_detail_generic(
    id: UUID,
    type: str = Query("phase"),
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Retorna detalhes do template (fase ou operação) baseado no parâmetro type."""
    if type == "phase":
        service = PhaseTemplateService(db, None)
        return await service.get_with_details(id)
    else:
        service = OperationTemplateService(db, None)
        return await service.get_with_details(id)

# --- Phase Templates (Global) ---

@router.get("/phase", response_model=List[PhaseTemplateRead])
async def list_global_phase_templates(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = PhaseTemplateService(db, None) # None = Global
    return await service.listar()

@router.post("/phase", response_model=PhaseTemplateRead)
async def create_global_phase_template(
    dados: PhaseTemplateCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = PhaseTemplateService(db, None)
    # Força registro global
    obj = await service.create(dados)
    obj.tenant_id = None
    obj.is_system_default = True
    await db.commit()
    await db.refresh(obj)
    return obj

@router.get("/phase/{id}", response_model=PhaseTemplateDetail)
async def get_global_phase_template(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = PhaseTemplateService(db, None)
    return await service.get_with_details(id)

@router.put("/phase/{id}", response_model=PhaseTemplateRead)
async def update_global_phase_template(
    id: UUID,
    dados: PhaseTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = PhaseTemplateService(db, None)
    return await service.update(id, dados)

@router.delete("/phase/{id}")
async def delete_global_phase_template(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = PhaseTemplateService(db, None)
    await service.hard_delete(id)
    await db.commit()
    return {"status": "success"}

# --- Operation Templates (Global) ---

@router.get("/operations", response_model=List[OperationTemplateRead])
async def list_global_operation_templates(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = OperationTemplateService(db, None)
    return await service.listar()

@router.get("/operations/{id}", response_model=OperationTemplateDetail)
async def get_global_operation_template(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = OperationTemplateService(db, None)
    return await service.get_with_details(id)

@router.post("/operations", response_model=OperationTemplateRead)
async def create_global_operation_template(
    dados: OperationTemplateCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = OperationTemplateService(db, None)
    obj = await service.create(dados)
    obj.tenant_id = None
    obj.is_system_default = True
    await db.commit()
    await db.refresh(obj)
    return obj

# --- Sub-itens CRUD (Governança) ---

@router.post("/phase/{template_id}/checklist", response_model=PhaseTemplateChecklistItemRead)
async def add_phase_checklist_item(
    template_id: UUID,
    dados: PhaseTemplateChecklistItemCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    item = PhaseTemplateChecklistItem(**dados.model_dump(), phase_template_id=template_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/phase/checklist/{item_id}")
async def delete_phase_checklist_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    stmt = select(PhaseTemplateChecklistItem).where(PhaseTemplateChecklistItem.id == item_id)
    item = (await db.execute(stmt)).scalar_one_or_none()
    if item:
        await db.delete(item)
        await db.commit()
    return {"status": "success"}

@router.put("/phase/checklist/{item_id}", response_model=PhaseTemplateChecklistItemRead)
async def update_phase_checklist_item(
    item_id: UUID,
    dados: PhaseTemplateChecklistItemCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    stmt = select(PhaseTemplateChecklistItem).where(PhaseTemplateChecklistItem.id == item_id)
    item = (await db.execute(stmt)).scalar_one_or_none()
    if not item: raise HTTPException(status_code=404, detail="Item não encontrado")
    for key, val in dados.model_dump().items():
        setattr(item, key, val)
    await db.commit()
    await db.refresh(item)
    return item

@router.post("/phase/{template_id}/tasks", response_model=PhaseTemplateTaskRead)
async def add_phase_task(
    template_id: UUID,
    dados: PhaseTemplateTaskCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    item = PhaseTemplateTask(**dados.model_dump(), phase_template_id=template_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/phase/tasks/{item_id}")
async def delete_phase_task(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    stmt = select(PhaseTemplateTask).where(PhaseTemplateTask.id == item_id)
    item = (await db.execute(stmt)).scalar_one_or_none()
    if item:
        await db.delete(item)
        await db.commit()
    return {"status": "success"}

@router.put("/phase/tasks/{item_id}", response_model=PhaseTemplateTaskRead)
async def update_phase_task(
    item_id: UUID,
    dados: PhaseTemplateTaskCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    stmt = select(PhaseTemplateTask).where(PhaseTemplateTask.id == item_id)
    item = (await db.execute(stmt)).scalar_one_or_none()
    if not item: raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    for key, val in dados.model_dump().items():
        setattr(item, key, val)
    await db.commit()
    await db.refresh(item)
    return item

@router.post("/phase/{template_id}/gate", response_model=PhaseGateRuleRead)
async def add_phase_gate_rule(
    template_id: UUID,
    dados: PhaseGateRuleCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    item = PhaseGateRule(**dados.model_dump(), phase_template_id=template_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/phase/gate/{item_id}")
async def delete_phase_gate_rule(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    stmt = select(PhaseGateRule).where(PhaseGateRule.id == item_id)
    item = (await db.execute(stmt)).scalar_one_or_none()
    if item:
        await db.delete(item)
        await db.commit()
    return {"status": "success"}

@router.put("/phase/gate/{item_id}", response_model=PhaseGateRuleRead)
async def update_phase_gate_rule(
    item_id: UUID,
    dados: PhaseGateRuleCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    stmt = select(PhaseGateRule).where(PhaseGateRule.id == item_id)
    item = (await db.execute(stmt)).scalar_one_or_none()
    if not item: raise HTTPException(status_code=404, detail="Regra não encontrada")
    for key, val in dados.model_dump().items():
        setattr(item, key, val)
    await db.commit()
    await db.refresh(item)
    return item

# --- Sub-itens CRUD (Operacional) ---

@router.post("/operations/{template_id}/items", response_model=OperationTemplateItemRead)
async def add_operation_item(
    template_id: UUID,
    dados: OperationTemplateItemCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    # Remove dependency_ids from dump as it's a separate relation
    data = dados.model_dump()
    deps = data.pop("dependency_ids", [])
    
    item = OperationTemplateItem(**data, operation_template_id=template_id)
    db.add(item)
    await db.flush()
    
    for dep_id in deps:
        db.add(OperationDependency(item_id=item.id, dependency_id=dep_id))
    
    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/operations/items/{item_id}")
async def delete_operation_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    stmt = select(OperationTemplateItem).where(OperationTemplateItem.id == item_id)
    item = (await db.execute(stmt)).scalar_one_or_none()
    if item:
        await db.delete(item)
        await db.commit()
    return {"status": "success"}

@router.put("/operations/items/{item_id}", response_model=OperationTemplateItemRead)
async def update_operation_item(
    item_id: UUID,
    dados: OperationTemplateItemCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    stmt = select(OperationTemplateItem).where(OperationTemplateItem.id == item_id)
    item = (await db.execute(stmt)).scalar_one_or_none()
    if not item: raise HTTPException(status_code=404, detail="Item operacional não encontrado")
    
    data = dados.model_dump()
    deps = data.pop("dependency_ids", [])
    
    for key, val in data.items():
        setattr(item, key, val)
    
    # Update dependencies (recreate)
    await db.execute(text("DELETE FROM operation_dependencies WHERE item_id = :id"), {"id": item_id})
    for dep_id in deps:
        db.add(OperationDependency(item_id=item_id, dependency_id=dep_id))
        
    await db.commit()
    await db.refresh(item)
    return item

@router.put("/operations/{id}", response_model=OperationTemplateRead)
async def update_global_operation_template(
    id: UUID,
    dados: OperationTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = OperationTemplateService(db, None)
    return await service.update(id, dados)

@router.delete("/operations/{id}")
async def delete_global_operation_template(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = OperationTemplateService(db, None)
    await service.hard_delete(id)
    await db.commit()
    return {"status": "success"}
