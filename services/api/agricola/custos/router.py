from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role
from core.dependencies import get_session_with_tenant
from agricola.custos.schemas import ReumoCustosSafraResponse
from agricola.custos.service import CustosService

router = APIRouter(prefix="/custos", tags=["Custos Agrícolas (Integração F2)"])

@router.get("/safra/{safra_id}", response_model=ReumoCustosSafraResponse)
async def relatorio_custo_safra(
    safra_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = CustosService(session, tenant_id)
    return await svc.get_resumo_safra(safra_id)
