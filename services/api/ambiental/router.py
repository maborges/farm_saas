from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, ConfigDict

from core.dependencies import get_tenant_id, get_session_with_tenant, require_module
from ambiental.models import RegistroCAR, AlertaAmbiental, OutorgaHidrica, StatusCAR, StatusAlerta, StatusOutorga

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
    fazenda_id: Optional[UUID] = None


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
    fazenda_id: Optional[UUID]
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
    fazenda_id: Optional[UUID] = None
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
    fazenda_id: Optional[UUID]
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
    fazenda_id: Optional[UUID] = None
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
    fazenda_id: Optional[UUID]
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
    outorgas_vencendo: int  # vencendo em 90 dias


# ── CAR ───────────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=DashboardAmbientalResponse)
async def dashboard_ambiental(
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    from datetime import timedelta
    cars = list((await session.execute(select(RegistroCAR).where(RegistroCAR.tenant_id == tenant_id))).scalars().all())
    alertas = list((await session.execute(select(AlertaAmbiental).where(AlertaAmbiental.tenant_id == tenant_id))).scalars().all())
    outorgas = list((await session.execute(select(OutorgaHidrica).where(OutorgaHidrica.tenant_id == tenant_id, OutorgaHidrica.ativo == True))).scalars().all())
    hoje = date.today()
    prazo = hoje + timedelta(days=90)
    return {
        "total_cars": len(cars),
        "cars_ativos": sum(1 for c in cars if c.status == StatusCAR.ATIVO),
        "cars_pendentes": sum(1 for c in cars if c.status == StatusCAR.PENDENTE),
        "total_alertas_abertos": sum(1 for a in alertas if a.status in (StatusAlerta.NOVO, StatusAlerta.EM_ANALISE)),
        "alertas_criticos": sum(1 for a in alertas if a.severidade == "CRITICA" and a.status != StatusAlerta.RESOLVIDO),
        "total_outorgas": len(outorgas),
        "outorgas_vencendo": sum(1 for o in outorgas if o.data_vencimento and hoje <= o.data_vencimento <= prazo),
    }


@router.get("/car", response_model=List[CARResponse])
async def listar_cars(
    status_filter: Optional[str] = Query(None, alias="status"),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    stmt = select(RegistroCAR).where(RegistroCAR.tenant_id == tenant_id).order_by(RegistroCAR.created_at.desc())
    if status_filter:
        stmt = stmt.where(RegistroCAR.status == status_filter)
    return list((await session.execute(stmt)).scalars().all())


@router.post("/car", response_model=CARResponse, status_code=status.HTTP_201_CREATED)
async def criar_car(
    dados: CARCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    car = RegistroCAR(tenant_id=tenant_id, **dados.model_dump(exclude_none=True))
    session.add(car)
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
    car = (await session.execute(
        select(RegistroCAR).where(RegistroCAR.id == car_id, RegistroCAR.tenant_id == tenant_id)
    )).scalar_one_or_none()
    if not car:
        from fastapi import HTTPException
        raise HTTPException(404, "CAR não encontrado.")
    for k, v in dados.model_dump(exclude_none=True).items():
        setattr(car, k, v)
    session.add(car)
    await session.commit()
    await session.refresh(car)
    return car


@router.delete("/car/{car_id}", status_code=200)
async def excluir_car(
    car_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    car = (await session.execute(
        select(RegistroCAR).where(RegistroCAR.id == car_id, RegistroCAR.tenant_id == tenant_id)
    )).scalar_one_or_none()
    if not car:
        from fastapi import HTTPException
        raise HTTPException(404, "CAR não encontrado.")
    await session.delete(car)
    await session.commit()
    return {"message": "CAR excluído."}


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
    stmt = select(AlertaAmbiental).where(AlertaAmbiental.tenant_id == tenant_id).order_by(AlertaAmbiental.data_deteccao.desc())
    if status_filter:
        stmt = stmt.where(AlertaAmbiental.status == status_filter)
    if severidade:
        stmt = stmt.where(AlertaAmbiental.severidade == severidade)
    if tipo:
        stmt = stmt.where(AlertaAmbiental.tipo == tipo)
    return list((await session.execute(stmt)).scalars().all())


@router.post("/alertas", response_model=AlertaResponse, status_code=status.HTTP_201_CREATED)
async def criar_alerta(
    dados: AlertaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    payload = dados.model_dump(exclude_none=True)
    if "data_deteccao" not in payload:
        payload["data_deteccao"] = date.today()
    alerta = AlertaAmbiental(tenant_id=tenant_id, **payload)
    session.add(alerta)
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
    alerta = (await session.execute(
        select(AlertaAmbiental).where(AlertaAmbiental.id == alerta_id, AlertaAmbiental.tenant_id == tenant_id)
    )).scalar_one_or_none()
    if not alerta:
        from fastapi import HTTPException
        raise HTTPException(404, "Alerta não encontrado.")
    for k, v in dados.model_dump(exclude_none=True).items():
        setattr(alerta, k, v)
    session.add(alerta)
    await session.commit()
    await session.refresh(alerta)
    return alerta


# ── Outorgas ──────────────────────────────────────────────────────────────────

@router.get("/outorgas", response_model=List[OutorgaResponse])
async def listar_outorgas(
    status_filter: Optional[str] = Query(None, alias="status"),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    stmt = (
        select(OutorgaHidrica)
        .where(OutorgaHidrica.tenant_id == tenant_id, OutorgaHidrica.ativo == True)
        .order_by(OutorgaHidrica.data_vencimento.asc())
    )
    if status_filter:
        stmt = stmt.where(OutorgaHidrica.status == status_filter)
    return list((await session.execute(stmt)).scalars().all())


@router.post("/outorgas", response_model=OutorgaResponse, status_code=status.HTTP_201_CREATED)
async def criar_outorga(
    dados: OutorgaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    outorga = OutorgaHidrica(tenant_id=tenant_id, **dados.model_dump(exclude_none=True))
    session.add(outorga)
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
    outorga = (await session.execute(
        select(OutorgaHidrica).where(OutorgaHidrica.id == outorga_id, OutorgaHidrica.tenant_id == tenant_id)
    )).scalar_one_or_none()
    if not outorga:
        from fastapi import HTTPException
        raise HTTPException(404, "Outorga não encontrada.")
    for k, v in dados.model_dump(exclude_none=True).items():
        setattr(outorga, k, v)
    session.add(outorga)
    await session.commit()
    await session.refresh(outorga)
    return outorga
