from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role
from core.dependencies import get_session_with_tenant
from agricola.analises_solo.schemas import AnaliseSoloCreate, AnaliseSoloResponse
from agricola.analises_solo.service import AnaliseSoloService

router = APIRouter(prefix="/analises-solo", tags=["Análises de Solo"])

@router.post("/", response_model=AnaliseSoloResponse, status_code=status.HTTP_201_CREATED)
async def registrar_analise(
    dados: AnaliseSoloCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = AnaliseSoloService(session, tenant_id)
    analise = await svc.criar(dados)
    return AnaliseSoloResponse.model_validate(analise)

@router.get("/", response_model=List[AnaliseSoloResponse])
async def listar_analises(
    talhao_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = AnaliseSoloService(session, tenant_id)
    filters = {}
    if talhao_id: filters["talhao_id"] = talhao_id
    
    analises = await svc.list_all(**filters)
    return [AnaliseSoloResponse.model_validate(a) for a in analises]

@router.get("/{id}", response_model=AnaliseSoloResponse)
async def detalhar_analise(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = AnaliseSoloService(session, tenant_id)
    analise = await svc.get_or_fail(id)
    return AnaliseSoloResponse.model_validate(analise)


@router.get("/{id}/recomendacoes")
async def recomendacoes_analise(
    id: UUID,
    cultura: Optional[str] = Query("SOJA", description="SOJA | MILHO | TRIGO | ALGODAO"),
    v_meta: Optional[float] = Query(60.0, description="Saturação por bases alvo (%)"),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    """Gera recomendações de calagem (método V% Embrapa) e adubação NPK para a análise."""
    svc = AnaliseSoloService(session, tenant_id)
    analise = await svc.get_or_fail(id)
    return svc.gerar_recomendacoes(analise, cultura=cultura or "SOJA", v_meta=v_meta or 60.0)
