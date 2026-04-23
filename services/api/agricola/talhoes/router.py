from fastapi import APIRouter, Depends
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, get_session_with_tenant, require_module
from core.cadastros.propriedades.schemas import AreaRuralResponse
from agricola.services.talhao_service import AgricolaTalhaoService

router = APIRouter(prefix="/talhoes", tags=["Agrícola - Talhões"])

@router.get("/contexto", response_model=List[AreaRuralResponse])
async def listar_talhoes_com_contexto(
    unidade_produtiva_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    """
    Retorna a lista de talhões da unidade produtiva com informações de solo,
    irrigação e o cultivo ATIVO (safra atual).
    """
    svc = AgricolaTalhaoService(session, tenant_id)
    return await svc.listar_talhoes_com_cultivo(unidade_produtiva_id=unidade_produtiva_id)
