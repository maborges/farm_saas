import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from loguru import logger

from core.dependencies import get_session, get_tenant_id
from .models import AreaRural, MatriculaImovel, RegistroAmbiental
from .schemas import (
    AreaRuralCreate, AreaRuralUpdate, AreaRuralResponse,
    MatriculaCreate, MatriculaUpdate, MatriculaResponse,
    RegistroAmbientalCreate, RegistroAmbientalUpdate, RegistroAmbientalResponse,
    ValorPatrimonialCreate, ValorPatrimonialUpdate, ValorPatrimonialResponse,
    InfraestruturaCreate, InfraestruturaUpdate, InfraestruturaResponse,
    ArquivoGeoResponse, ArquivoGeoProcessadoResponse,
    SumarioAreasResponse, TipoSoloResponse, TipoIrrigacaoResponse
)
from .service import AreaRuralService, MatriculaService, RegistroAmbientalService, ValorPatrimonialService, InfraestruturaService, ArquivoGeoService

router = APIRouter(prefix="/cadastros/areas-rurais", tags=["Cadastros — Propriedades"])


# ---------------------------------------------------------------------------
# Áreas Rurais
# ---------------------------------------------------------------------------

@router.get("/unidade/{unidade_produtiva_id}/sumario", response_model=SumarioAreasResponse)
async def sumario_areas(
    unidade_produtiva_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Agrega hectares por categoria (total, produtiva, ambiental, infraestrutura)."""
    svc = AreaRuralService(AreaRural, session, tenant_id)
    return await svc.sumario_areas(unidade_produtiva_id)


@router.get("/unidade/{unidade_produtiva_id}/arvore", response_model=list[AreaRuralResponse])
async def arvore_areas(
    unidade_produtiva_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Retorna as raízes da hierarquia (GLEBA e INFRAESTRUTURA) da unidade produtiva."""
    svc = AreaRuralService(AreaRural, session, tenant_id)
    return await svc.listar_raizes(unidade_produtiva_id=unidade_produtiva_id)


@router.get("", response_model=list[AreaRuralResponse])
async def listar(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo (ex: TALHAO, PASTAGEM)"),
    unidade_produtiva_id: Optional[uuid.UUID] = Query(None),
    parent_id: Optional[uuid.UUID] = Query(None, description="Filhos diretos de um parent"),
    apenas_raizes: bool = Query(False, description="Retorna apenas áreas sem parent"),
    apenas_ativos: bool = Query(True),
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = AreaRuralService(AreaRural, session, tenant_id)
    if apenas_raizes:
        return await svc.listar_raizes(unidade_produtiva_id=unidade_produtiva_id)
    return await svc.listar(unidade_produtiva_id=unidade_produtiva_id, tipo=tipo, parent_id=parent_id, apenas_ativos=apenas_ativos)


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
# Seletores (Lookup)
# ---------------------------------------------------------------------------

@router.get("/seletores/tipos-solo", response_model=list[TipoSoloResponse])
async def listar_tipos_solo(
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = AreaRuralService(AreaRural, session, tenant_id)
    return await svc.listar_tipos_solo()


@router.get("/seletores/tipos-irrigacao", response_model=list[TipoIrrigacaoResponse])
async def listar_tipos_irrigacao(
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = AreaRuralService(AreaRural, session, tenant_id)
    return await svc.listar_tipos_irrigacao()


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


# ---------------------------------------------------------------------------
# Infraestrutura
# ---------------------------------------------------------------------------

@router.get("/{area_id}/infraestruturas", response_model=list[InfraestruturaResponse])
async def listar_infraestruturas(
    area_id: uuid.UUID,
    apenas_ativos: bool = Query(True),
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = InfraestruturaService(session, tenant_id)
    return await svc.listar(area_id, apenas_ativos=apenas_ativos)


@router.post("/{area_id}/infraestruturas", response_model=InfraestruturaResponse, status_code=201)
async def criar_infraestrutura(
    area_id: uuid.UUID,
    data: InfraestruturaCreate,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = InfraestruturaService(session, tenant_id)
    payload = data.model_dump()
    payload["area_rural_id"] = area_id
    return await svc.criar(payload)


@router.patch("/{area_id}/infraestruturas/{infra_id}", response_model=InfraestruturaResponse)
async def atualizar_infraestrutura(
    area_id: uuid.UUID,
    infra_id: uuid.UUID,
    data: InfraestruturaUpdate,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = InfraestruturaService(session, tenant_id)
    return await svc.atualizar(infra_id, area_id, data.model_dump(exclude_none=True))


@router.delete("/{area_id}/infraestruturas/{infra_id}", status_code=204)
async def remover_infraestrutura(
    area_id: uuid.UUID,
    infra_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = InfraestruturaService(session, tenant_id)
    await svc.remover(infra_id, area_id)


# ---------------------------------------------------------------------------
# ArquivoGeo
# ---------------------------------------------------------------------------

FORMATOS_ACEITOS = {
    "application/zip": "shp",
    "application/x-zip-compressed": "shp",
    "application/vnd.google-earth.kml+xml": "kml",
    "application/vnd.google-earth.kmz": "kmz",
    "application/geo+json": "geojson",
    "application/json": "geojson",
    "text/plain": "kml",  # alguns clientes enviam KML como text/plain
}

_EXT_MAP = {".zip": "shp", ".shp": "shp", ".kml": "kml", ".kmz": "kmz", ".geojson": "geojson", ".json": "geojson"}


def _detectar_formato(filename: str, content_type: str) -> str:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return _EXT_MAP.get(ext) or FORMATOS_ACEITOS.get(content_type, "geojson")


@router.get("/{area_id}/arquivos-geo", response_model=list[ArquivoGeoResponse])
async def listar_arquivos_geo(
    area_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = ArquivoGeoService(session, tenant_id)
    return await svc.listar(area_id)


@router.post("/{area_id}/arquivos-geo/upload", response_model=ArquivoGeoProcessadoResponse, status_code=201)
async def upload_arquivo_geo(
    area_id: uuid.UUID,
    arquivo: UploadFile = File(...),
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    from core.config import settings
    from core.services.storage_service import StorageService
    from core.services.geoprocessamento_service import GeoprocessamentoService

    # Validar tamanho
    content = await arquivo.read()
    max_bytes = settings.storage_max_file_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(422, f"Arquivo excede {settings.storage_max_file_mb}MB")

    formato = _detectar_formato(arquivo.filename or "", arquivo.content_type or "")

    # Persistir no storage
    storage_path = StorageService.save(
        content, str(tenant_id), str(area_id), arquivo.filename or "upload"
    )

    svc = ArquivoGeoService(session, tenant_id)
    geo_record = await svc.criar({
        "area_rural_id": area_id,
        "nome_arquivo": arquivo.filename or "upload",
        "formato": formato,
        "tamanho_bytes": len(content),
        "storage_backend": settings.storage_backend,
        "storage_path": storage_path,
    })

    # Processar
    poligonos_geojson = None
    try:
        geo_svc = GeoprocessamentoService(session, tenant_id)
        if formato == "shp":
            resultado = await geo_svc.processar_shapefile(content)
        elif formato in ("kml", "kmz"):
            resultado = await geo_svc.processar_kml(content, is_kmz=(formato == "kmz"))
        else:
            import json as _json
            resultado = {"geometria": _json.loads(content), "area_ha": 0.0, "total_features": 1}

        poligonos_geojson = resultado.get("geometria")
        n_poligonos = resultado.get("total_features", 1)
        area_ha = resultado.get("area_ha", 0.0)
        geo_record = await svc.marcar_processado(geo_record.id, n_poligonos, area_ha)

    except Exception as e:
        logger.warning(f"Erro ao processar arquivo geo {geo_record.id}: {e}")
        geo_record = await svc.marcar_erro(geo_record.id, str(e))

    return ArquivoGeoProcessadoResponse(arquivo=geo_record, poligonos=poligonos_geojson)
