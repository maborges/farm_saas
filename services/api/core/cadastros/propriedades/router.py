import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query

from core.dependencies import get_session, get_tenant_id
from .models import AreaRural, MatriculaImovel, RegistroAmbiental
from .schemas import (
    AreaRuralCreate, AreaRuralUpdate, AreaRuralResponse,
    MatriculaCreate, MatriculaUpdate, MatriculaResponse,
    RegistroAmbientalCreate, RegistroAmbientalUpdate, RegistroAmbientalResponse,
    ValorPatrimonialCreate, ValorPatrimonialUpdate, ValorPatrimonialResponse,
)
from .service import AreaRuralService, MatriculaService, RegistroAmbientalService, ValorPatrimonialService

router = APIRouter(prefix="/cadastros/areas-rurais", tags=["Cadastros — Propriedades"])


# ---------------------------------------------------------------------------
# Áreas Rurais
# ---------------------------------------------------------------------------

@router.get("", response_model=list[AreaRuralResponse])
async def listar(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo (ex: TALHAO, PASTAGEM)"),
    fazenda_id: Optional[uuid.UUID] = Query(None),
    parent_id: Optional[uuid.UUID] = Query(None, description="Filhos diretos de um parent"),
    apenas_raizes: bool = Query(False, description="Retorna apenas áreas sem parent"),
    apenas_ativos: bool = Query(True),
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = AreaRuralService(AreaRural, session, tenant_id)
    if apenas_raizes:
        return await svc.listar_raizes(fazenda_id=fazenda_id)
    return await svc.listar(fazenda_id=fazenda_id, tipo=tipo, parent_id=parent_id, apenas_ativos=apenas_ativos)


@router.post("", response_model=AreaRuralResponse, status_code=201)
async def criar(
    data: AreaRuralCreate,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = AreaRuralService(AreaRural, session, tenant_id)
    return await svc.criar_area(data.model_dump())


@router.get("/{area_id}", response_model=AreaRuralResponse)
async def obter(
    area_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = AreaRuralService(AreaRural, session, tenant_id)
    return await svc.get_or_fail(area_id)


@router.get("/{area_id}/filhos", response_model=list[AreaRuralResponse])
async def listar_filhos(
    area_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Retorna subáreas diretas de uma área."""
    svc = AreaRuralService(AreaRural, session, tenant_id)
    return await svc.listar(parent_id=area_id)


@router.patch("/{area_id}", response_model=AreaRuralResponse)
async def atualizar(
    area_id: uuid.UUID,
    data: AreaRuralUpdate,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = AreaRuralService(AreaRural, session, tenant_id)
    return await svc.atualizar_area(area_id, data.model_dump(exclude_none=True))


@router.delete("/{area_id}", status_code=204)
async def remover(
    area_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = AreaRuralService(AreaRural, session, tenant_id)
    await svc.soft_delete(area_id)


# ---------------------------------------------------------------------------
# Matrículas
# ---------------------------------------------------------------------------

@router.get("/{area_id}/matriculas", response_model=list[MatriculaResponse])
async def listar_matriculas(
    area_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = MatriculaService(session, tenant_id)
    return await svc.listar(area_id)


@router.post("/{area_id}/matriculas", response_model=MatriculaResponse, status_code=201)
async def criar_matricula(
    area_id: uuid.UUID,
    data: MatriculaCreate,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = MatriculaService(session, tenant_id)
    payload = data.model_dump()
    payload["area_id"] = area_id  # garante consistência com o path
    return await svc.criar(payload)


@router.patch("/{area_id}/matriculas/{matricula_id}", response_model=MatriculaResponse)
async def atualizar_matricula(
    area_id: uuid.UUID,
    matricula_id: uuid.UUID,
    data: MatriculaUpdate,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = MatriculaService(session, tenant_id)
    return await svc.atualizar(matricula_id, area_id, data.model_dump(exclude_none=True))


@router.delete("/{area_id}/matriculas/{matricula_id}", status_code=204)
async def remover_matricula(
    area_id: uuid.UUID,
    matricula_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = MatriculaService(session, tenant_id)
    await svc.remover(matricula_id, area_id)


# ---------------------------------------------------------------------------
# Registros Ambientais
# ---------------------------------------------------------------------------

@router.get("/{area_id}/registros-ambientais", response_model=list[RegistroAmbientalResponse])
async def listar_registros_ambientais(
    area_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = RegistroAmbientalService(session, tenant_id)
    return await svc.listar(area_id)


@router.post("/{area_id}/registros-ambientais", response_model=RegistroAmbientalResponse, status_code=201)
async def criar_registro_ambiental(
    area_id: uuid.UUID,
    data: RegistroAmbientalCreate,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = RegistroAmbientalService(session, tenant_id)
    payload = data.model_dump()
    payload["area_id"] = area_id
    return await svc.criar(payload)


@router.patch("/{area_id}/registros-ambientais/{registro_id}", response_model=RegistroAmbientalResponse)
async def atualizar_registro_ambiental(
    area_id: uuid.UUID,
    registro_id: uuid.UUID,
    data: RegistroAmbientalUpdate,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = RegistroAmbientalService(session, tenant_id)
    return await svc.atualizar(registro_id, area_id, data.model_dump(exclude_none=True))


@router.delete("/{area_id}/registros-ambientais/{registro_id}", status_code=204)
async def remover_registro_ambiental(
    area_id: uuid.UUID,
    registro_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = RegistroAmbientalService(session, tenant_id)
    await svc.remover(registro_id, area_id)


# ---------------------------------------------------------------------------
# Valores Patrimoniais
# ---------------------------------------------------------------------------

@router.get("/{area_id}/valores-patrimoniais", response_model=list[ValorPatrimonialResponse])
async def listar_valores_patrimoniais(
    area_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = ValorPatrimonialService(session, tenant_id)
    return await svc.listar(area_id)


@router.post("/{area_id}/valores-patrimoniais", response_model=ValorPatrimonialResponse, status_code=201)
async def criar_valor_patrimonial(
    area_id: uuid.UUID,
    data: ValorPatrimonialCreate,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = ValorPatrimonialService(session, tenant_id)
    payload = data.model_dump()
    payload["area_id"] = area_id
    return await svc.criar(payload)


@router.patch("/{area_id}/valores-patrimoniais/{valor_id}", response_model=ValorPatrimonialResponse)
async def atualizar_valor_patrimonial(
    area_id: uuid.UUID,
    valor_id: uuid.UUID,
    data: ValorPatrimonialUpdate,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = ValorPatrimonialService(session, tenant_id)
    return await svc.atualizar(valor_id, area_id, data.model_dump(exclude_none=True))


@router.delete("/{area_id}/valores-patrimoniais/{valor_id}", status_code=204)
async def remover_valor_patrimonial(
    area_id: uuid.UUID,
    valor_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = ValorPatrimonialService(session, tenant_id)
    await svc.remover(valor_id, area_id)
