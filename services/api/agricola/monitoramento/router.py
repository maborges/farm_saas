from fastapi import APIRouter, Depends, status, BackgroundTasks, UploadFile, File
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role
from core.dependencies import get_session_with_tenant
from agricola.monitoramento.schemas import MonitoramentoPragasCreate, MonitoramentoPragasResponse, MonitoramentoPragasUpdate
from agricola.monitoramento.service import MonitoramentoService

router = APIRouter(prefix="/monitoramentos", tags=["Monitoramento e Manejo FITO"])

@router.post("/", response_model=MonitoramentoPragasResponse, status_code=status.HTTP_201_CREATED)
async def criar_monitoramento(
    dados: MonitoramentoPragasCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = MonitoramentoService(session, tenant_id)
    monitoramento = await svc.create(dados)
    return MonitoramentoPragasResponse.model_validate(monitoramento)

@router.get("/", response_model=List[MonitoramentoPragasResponse])
async def listar_monitoramentos(
    safra_id: UUID | None = None,
    tipo: str | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = MonitoramentoService(session, tenant_id)
    filters = {}
    if safra_id: filters["safra_id"] = safra_id
    if tipo: filters["tipo"] = tipo
    
    monitoramentos = await svc.list_all(**filters)
    return [MonitoramentoPragasResponse.model_validate(m) for m in monitoramentos]

@router.get("/{id}", response_model=MonitoramentoPragasResponse)
async def detalhar_monitoramento(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = MonitoramentoService(session, tenant_id)
    monitoramento = await svc.get_or_fail(id)
    return MonitoramentoPragasResponse.model_validate(monitoramento)

@router.post("/{id}/diagnosticar-imagem")
async def diagnosticar_imagem(
    id: UUID,
    foto: UploadFile = File(...),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = MonitoramentoService(session, tenant_id)
    foto_bytes = await foto.read()
    diagnostico = await svc.diagnosticar_imagem(foto_bytes)
    
    # Save partial results to table if needed
    # ...
    
    return diagnostico
@router.post("/diagnosticar-avulso")
async def diagnosticar_avulso(
    foto: UploadFile = File(...),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    """Diagnóstico rápido para novos levantamentos (antes de salvar)."""
    svc = MonitoramentoService(session, tenant_id)
    foto_bytes = await foto.read()
    return await svc.diagnosticar_imagem(foto_bytes)
