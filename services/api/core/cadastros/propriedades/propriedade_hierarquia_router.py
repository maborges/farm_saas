"""
Router para gestão de hierarquia de áreas rurais vinculadas a produtores.

Hierarquia:
  Propriedade Econômica
  └── Exploração Rural (vínculo com Fazenda)
      └── Fazenda
          └── AreaRural (PROPRIEDADE/GLEBA)
              └── AreaRural (TALHAO/PIQUETE/PASTAGEM)
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session_with_tenant, get_tenant_id
from core.exceptions import EntityNotFoundError
from core.cadastros.propriedades.schemas import (
    PropriedadeComHierarquiaResponse,
    AreaRuralCreate,
    AreaRuralUpdate,
    AreaRuralTreeResponse,
    AreaRuralResponse,
)
from core.cadastros.propriedades.service import AreaRuralService
from core.cadastros.propriedades.models import AreaRural
from core.cadastros.propriedades.hierarquia_service import HierarquiaService

router = APIRouter(
    prefix="/cadastros/propriedades",
    tags=["Cadastros — Propriedades com Hierarquia"],
)


@router.get("/{propriedade_id}/hierarquia", response_model=PropriedadeComHierarquiaResponse)
async def obter_propriedade_com_hierarquia(
    propriedade_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    try:
        return await HierarquiaService(session, tenant_id).obter_hierarquia_completa(propriedade_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Propriedade não encontrada")


@router.get("/{propriedade_id}/fazendas/{unidade_produtiva_id}/areas", response_model=list[AreaRuralTreeResponse])
async def listar_areas_por_fazenda(
    propriedade_id: uuid.UUID,
    unidade_produtiva_id: uuid.UUID,
    tipo: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await HierarquiaService(session, tenant_id).listar_areas_por_fazenda(
        propriedade_id, unidade_produtiva_id, tipo=tipo
    )


@router.post("/{propriedade_id}/fazendas/{unidade_produtiva_id}/areas", response_model=AreaRuralResponse, status_code=201)
async def criar_area_rural(
    propriedade_id: uuid.UUID,
    unidade_produtiva_id: uuid.UUID,
    data: AreaRuralCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    area = await HierarquiaService(session, tenant_id).criar_area_rural(propriedade_id, unidade_produtiva_id, data)
    await session.commit()
    return area


@router.patch("/fazendas/{unidade_produtiva_id}/areas/{area_id}", response_model=AreaRuralResponse)
async def atualizar_area_rural(
    unidade_produtiva_id: uuid.UUID,
    area_id: uuid.UUID,
    data: AreaRuralUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    areas_service = AreaRuralService(AreaRural, session, tenant_id)
    return await areas_service.atualizar_area(area_id, data.model_dump(exclude_none=True))


@router.delete("/fazendas/{unidade_produtiva_id}/areas/{area_id}", status_code=204)
async def remover_area_rural(
    unidade_produtiva_id: uuid.UUID,
    area_id: uuid.UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    areas_service = AreaRuralService(AreaRural, session, tenant_id)
    await areas_service.soft_delete(area_id)
