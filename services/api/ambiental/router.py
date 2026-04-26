from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, ConfigDict

from core.dependencies import get_tenant_id, get_session_with_tenant, require_module
from core.exceptions import EntityNotFoundError
from ambiental.service import AmbientalService

router = APIRouter(prefix="/ambiental", tags=["Ambiental — Compliance"])

MODULE = "AM1_COMPLIANCE"


# ── Schemas ───────────────────────────────────────────────────────────────────

class CARCreate(BaseModel):
    fazenda_nome: str
    codigo_car: str
    uf: str
    municipio: Optional[str] = None
    status: str = "PENDENTE"
    area_total_ha: Optional[float] = None
    area_app_ha: Optional[float] = None
    area_rl_ha: Optional[float] = None
    area_vegetacao_nativa_ha: Optional[float] = None
    area_uso_consolidado_ha: Optional[float] = None
    data_inscricao: Optional[date] = None
    data_atualizacao: Optional[date] = None
    pendencias: Optional[str] = None
    observacoes: Optional[str] = None
    unidade_produtiva_id: Optional[UUID] = None


class CARUpdate(BaseModel):
    status: Optional[str] = None
    area_total_ha: Optional[float] = None
    area_app_ha: Optional[float] = None
    area_rl_ha: Optional[float] = None
    area_vegetacao_nativa_ha: Optional[float] = None
    area_uso_consolidado_ha: Optional[float] = None
    data_atualizacao: Optional[date] = None
    pendencias: Optional[str] = None
    observacoes: Optional[str] = None


class CARResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    unidade_produtiva_id: Optional[UUID]
    fazenda_nome: str
    codigo_car: str
    uf: str
    municipio: Optional[str]
    status: str
    area_total_ha: Optional[float]
    area_app_ha: Optional[float]
    area_rl_ha: Optional[float]
    area_vegetacao_nativa_ha: Optional[float]
    area_uso_consolidado_ha: Optional[float]
    data_inscricao: Optional[date]
    data_atualizacao: Optional[date]
    pendencias: Optional[str]
    observacoes: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AlertaCreate(BaseModel):
    fazenda_nome: Optional[str] = None
    unidade_produtiva_id: Optional[UUID] = None
    tipo: str = "DESMATAMENTO"
    severidade: str = "MEDIA"
    area_ha: Optional[float] = None
    descricao: Optional[str] = None
    fonte: Optional[str] = None
    talhao_nome: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    data_deteccao: Optional[date] = None


class AlertaUpdate(BaseModel):
    status: Optional[str] = None
    severidade: Optional[str] = None
    data_resolucao: Optional[date] = None
    resolucao_descricao: Optional[str] = None


class AlertaResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    unidade_produtiva_id: Optional[UUID]
    fazenda_nome: Optional[str]
    tipo: str
    severidade: str
    status: str
    area_ha: Optional[float]
    descricao: Optional[str]
    fonte: Optional[str]
    talhao_nome: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    data_deteccao: date
    data_resolucao: Optional[date]
    resolucao_descricao: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OutorgaCreate(BaseModel):
    fazenda_nome: Optional[str] = None
    unidade_produtiva_id: Optional[UUID] = None
    numero_outorga: str
    orgao_emissor: Optional[str] = None
    tipo_uso: str = "IRRIGACAO"
    corpo_hidrico: Optional[str] = None
    vazao_outorgada_ls: Optional[float] = None
    vazao_outorgada_m3h: Optional[float] = None
    data_emissao: Optional[date] = None
    data_vencimento: Optional[date] = None
    observacoes: Optional[str] = None


class OutorgaUpdate(BaseModel):
    status: Optional[str] = None
    vazao_outorgada_ls: Optional[float] = None
    vazao_outorgada_m3h: Optional[float] = None
    data_vencimento: Optional[date] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None


class OutorgaResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    unidade_produtiva_id: Optional[UUID]
    fazenda_nome: Optional[str]
    numero_outorga: str
    orgao_emissor: Optional[str]
    tipo_uso: str
    corpo_hidrico: Optional[str]
    vazao_outorgada_ls: Optional[float]
    vazao_outorgada_m3h: Optional[float]
    status: str
    data_emissao: Optional[date]
    data_vencimento: Optional[date]
    observacoes: Optional[str]
    ativo: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DashboardAmbientalResponse(BaseModel):
    total_cars: int
    cars_ativos: int
    cars_pendentes: int
    total_alertas_abertos: int
    alertas_criticos: int
    total_outorgas: int
    outorgas_vencendo: int


# ── CAR ───────────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=DashboardAmbientalResponse)
async def dashboard_ambiental(
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = AmbientalService(session, tenant_id)
    return await svc.dashboard()


@router.get("/car", response_model=List[CARResponse])
async def listar_cars(
    status_filter: Optional[str] = Query(None, alias="status"),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = AmbientalService(session, tenant_id)
    return await svc.listar_cars(status_filter=status_filter)


@router.post("/car", response_model=CARResponse, status_code=status.HTTP_201_CREATED)
async def criar_car(
    dados: CARCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = AmbientalService(session, tenant_id)
    car = await svc.criar_car(dados.model_dump(exclude_none=True))
    await session.commit()
    await session.refresh(car)
    return car


@router.patch("/car/{car_id}", response_model=CARResponse)
async def atualizar_car(
    car_id: UUID,
    dados: CARUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = AmbientalService(session, tenant_id)
    try:
        car = await svc.atualizar_car(car_id, dados.model_dump(exclude_none=True))
        await session.commit()
        await session.refresh(car)
        return car
    except EntityNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "CAR não encontrado.")


@router.delete("/car/{car_id}", status_code=200)
async def excluir_car(
    car_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = AmbientalService(session, tenant_id)
    try:
        await svc.excluir_car(car_id)
        await session.commit()
        return {"message": "CAR excluído."}
    except EntityNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "CAR não encontrado.")


# ── Alertas ───────────────────────────────────────────────────────────────────

@router.get("/alertas", response_model=List[AlertaResponse])
async def listar_alertas(
    status_filter: Optional[str] = Query(None, alias="status"),
    severidade: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = AmbientalService(session, tenant_id)
    return await svc.listar_alertas(status_filter=status_filter, severidade=severidade, tipo=tipo)


@router.post("/alertas", response_model=AlertaResponse, status_code=status.HTTP_201_CREATED)
async def criar_alerta(
    dados: AlertaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = AmbientalService(session, tenant_id)
    alerta = await svc.criar_alerta(dados.model_dump(exclude_none=True))
    await session.commit()
    await session.refresh(alerta)
    return alerta


@router.patch("/alertas/{alerta_id}", response_model=AlertaResponse)
async def atualizar_alerta(
    alerta_id: UUID,
    dados: AlertaUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = AmbientalService(session, tenant_id)
    try:
        alerta = await svc.atualizar_alerta(alerta_id, dados.model_dump(exclude_none=True))
        await session.commit()
        await session.refresh(alerta)
        return alerta
    except EntityNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alerta não encontrado.")


# ── Outorgas ──────────────────────────────────────────────────────────────────

@router.get("/outorgas", response_model=List[OutorgaResponse])
async def listar_outorgas(
    status_filter: Optional[str] = Query(None, alias="status"),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = AmbientalService(session, tenant_id)
    return await svc.listar_outorgas(status_filter=status_filter)


@router.post("/outorgas", response_model=OutorgaResponse, status_code=status.HTTP_201_CREATED)
async def criar_outorga(
    dados: OutorgaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = AmbientalService(session, tenant_id)
    outorga = await svc.criar_outorga(dados.model_dump(exclude_none=True))
    await session.commit()
    await session.refresh(outorga)
    return outorga


@router.patch("/outorgas/{outorga_id}", response_model=OutorgaResponse)
async def atualizar_outorga(
    outorga_id: UUID,
    dados: OutorgaUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = AmbientalService(session, tenant_id)
    try:
        outorga = await svc.atualizar_outorga(outorga_id, dados.model_dump(exclude_none=True))
        await session.commit()
        await session.refresh(outorga)
        return outorga
    except EntityNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Outorga não encontrada.")
