from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import PlanTier
from core.dependencies import get_tenant_id, require_module, require_role, require_tier
from core.dependencies import get_session_with_tenant
from agricola.previsoes.schemas import PrevisaoProdutividadeResponse, PrevisaoProdutividadeCreate
from agricola.previsoes.service import PrevisaoService

router = APIRouter(prefix="/previsoes", tags=["Previsão de Produtividade"])

@router.post("/gerar", response_model=PrevisaoProdutividadeResponse, status_code=status.HTTP_201_CREATED)
async def gerar_previsao_maquina(
    safra_id: UUID,
    talhao_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
    _tier: None = Depends(require_tier(PlanTier.PROFISSIONAL)),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = PrevisaoService(session, tenant_id)
    previsao = await svc.gerar_nova_previsao(safra_id, talhao_id)
    return PrevisaoProdutividadeResponse.model_validate(previsao)

@router.get("/", response_model=List[PrevisaoProdutividadeResponse])
async def listar_previsoes(
    safra_id: UUID | None = None,
    talhao_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
    _tier: None = Depends(require_tier(PlanTier.PROFISSIONAL)),
):
    svc = PrevisaoService(session, tenant_id)
    filters = {}
    if safra_id: filters["safra_id"] = safra_id
    if talhao_id: filters["talhao_id"] = talhao_id
    
    previsoes = await svc.list_all(**filters)
    return [PrevisaoProdutividadeResponse.model_validate(p) for p in previsoes]
