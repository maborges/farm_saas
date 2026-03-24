from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid

from core.dependencies import get_session, get_current_tenant
from core.models.tenant import Tenant
from imoveis.models.imovel import ImovelRural, MatriculaImovel, Benfeitoria
from pydantic import BaseModel

router = APIRouter(prefix="/imoveis", tags=["Patrimônio — Imóveis"])

class ImovelCreate(BaseModel):
    nome: str
    car_numero: Optional[str] = None
    nirf: Optional[str] = None
    incra: Optional[str] = None
    area_total_ha: float = 0.0
    cidade: Optional[str] = None
    estado: Optional[str] = None
    geometria: Optional[dict] = None

class ImovelResponse(BaseModel):
    id: uuid.UUID
    nome: str
    area_total_ha: float
    car_numero: Optional[str]
    cidade: Optional[str]
    estado: Optional[str]
    geometria: Optional[dict]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ImovelResponse])
async def list_imoveis(
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    stmt = select(ImovelRural).where(ImovelRural.tenant_id == tenant.id)
    res = await session.execute(stmt)
    return res.scalars().all()

@router.post("/", response_model=ImovelResponse, status_code=status.HTTP_201_CREATED)
async def create_imovel(
    data: ImovelCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    novo_imovel = ImovelRural(**data.model_dump(), tenant_id=tenant.id)
    session.add(novo_imovel)
    await session.commit()
    await session.refresh(novo_imovel)
    return novo_imovel

@router.patch("/{imovel_id}", response_model=ImovelResponse)
async def update_imovel(
    imovel_id: uuid.UUID,
    data: dict,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    stmt = select(ImovelRural).where(ImovelRural.id == imovel_id, ImovelRural.tenant_id == tenant.id)
    imovel = (await session.execute(stmt)).scalar_one_or_none()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    for key, value in data.items():
        if hasattr(imovel, key):
            setattr(imovel, key, value)
            
    await session.commit()
    await session.refresh(imovel)
    return imovel
