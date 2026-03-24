from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module
from core.dependencies import get_session_with_tenant
from agricola.climatico.schemas import ClimaResponse
from agricola.climatico.service import ClimaService

router = APIRouter(prefix="/climatico", tags=["Clima e Pluviometria"])

@router.post("/sincronizar/{fazenda_id}", status_code=status.HTTP_202_ACCEPTED)
async def sincronizar_api_clima(
    fazenda_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = ClimaService(session, tenant_id)
    msg = await svc.sync_open_meteo(fazenda_id)
    return {"message": msg}

@router.get("/historico/{fazenda_id}", response_model=List[ClimaResponse])
async def historico_clima(
    fazenda_id: UUID,
    dias: int = 30,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = ClimaService(session, tenant_id)
    hoje = date.today()
    inicio = hoje - timedelta(days=dias)
    registros = await svc.get_clima_periodo(fazenda_id, inicio, hoje)
    return [ClimaResponse.model_validate(r) for r in registros]

@router.get("/chuva-acumulada/{fazenda_id}")
async def acumulado_chuva(
    fazenda_id: UUID,
    dias: int = 30,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = ClimaService(session, tenant_id)
    acumulado = await svc.get_chuva_acumulada(fazenda_id, dias)
    return {"fazenda_id": fazenda_id, "dias": dias, "chuva_acumulada_mm": acumulado}
