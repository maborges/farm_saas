from fastapi import APIRouter, Depends, status, UploadFile, File
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role
from core.dependencies import get_session_with_tenant
from agricola.monitoramento.schemas import (
    MonitoramentoPragasCreate,
    MonitoramentoPragasUpdate,
    MonitoramentoPragasResponse,
    MonitoramentoCatalogoCreate,
    MonitoramentoCatalogoResponse,
)
from agricola.monitoramento.service import MonitoramentoService, MonitoramentoCatalogoService

router = APIRouter(prefix="/monitoramentos", tags=["Monitoramento Fitossanitário"])

# ─── Catálogo ─────────────────────────────────────────────────────────────────

@router.get("/catalogo", response_model=List[MonitoramentoCatalogoResponse])
async def listar_catalogo(
    tipo: str | None = None,
    cultura: str | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = MonitoramentoCatalogoService(session, tenant_id)
    items = await svc.listar(tipo=tipo, cultura=cultura)
    return [MonitoramentoCatalogoResponse.model_validate(i) for i in items]


@router.post("/catalogo", response_model=MonitoramentoCatalogoResponse, status_code=status.HTTP_201_CREATED)
async def criar_catalogo(
    dados: MonitoramentoCatalogoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = MonitoramentoCatalogoService(session, tenant_id)
    item = await svc.criar(dados.model_dump())
    return MonitoramentoCatalogoResponse.model_validate(item)


# ─── Monitoramento ────────────────────────────────────────────────────────────

@router.post("/", response_model=MonitoramentoPragasResponse, status_code=status.HTTP_201_CREATED)
async def criar_monitoramento(
    dados: MonitoramentoPragasCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = MonitoramentoService(session, tenant_id)
    tecnico_id = UUID(user["sub"]) if user.get("sub") else None
    registro = await svc.criar(dados, tecnico_id=tecnico_id)
    await session.commit()
    await session.refresh(registro)
    return MonitoramentoPragasResponse.model_validate(registro)


@router.get("/safra/{safra_id}", response_model=List[MonitoramentoPragasResponse])
async def listar_por_safra(
    safra_id: UUID,
    tipo: str | None = None,
    talhao_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = MonitoramentoService(session, tenant_id)
    registros = await svc.listar_por_safra(safra_id, tipo=tipo, talhao_id=talhao_id)
    return [MonitoramentoPragasResponse.model_validate(r) for r in registros]


@router.get("/{id}", response_model=MonitoramentoPragasResponse)
async def detalhar_monitoramento(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = MonitoramentoService(session, tenant_id)
    return MonitoramentoPragasResponse.model_validate(await svc.get_or_fail(id))


@router.patch("/{id}", response_model=MonitoramentoPragasResponse)
async def atualizar_monitoramento(
    id: UUID,
    dados: MonitoramentoPragasUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = MonitoramentoService(session, tenant_id)
    registro = await svc.update(id, dados.model_dump(exclude_none=True))
    await session.commit()
    await session.refresh(registro)
    return MonitoramentoPragasResponse.model_validate(registro)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_monitoramento(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = MonitoramentoService(session, tenant_id)
    await svc.hard_delete(id)
    await session.commit()


@router.post("/diagnosticar-avulso")
async def diagnosticar_avulso(
    foto: UploadFile = File(...),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    """Diagnóstico IA rápido antes de salvar o registro."""
    svc = MonitoramentoService(session, tenant_id)
    return await svc.diagnosticar_imagem(await foto.read())
