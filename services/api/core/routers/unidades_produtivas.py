from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form
from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_session_with_tenant
from core.dependencies import get_tenant_id, require_module, require_role, require_limit
from core.schemas.unidade_produtiva_input import UnidadeProdutivaCreate, UnidadeProdutivaUpdate
from core.schemas.unidade_produtiva_output import UnidadeProdutivaResponse
from core.services.unidade_produtiva_service import UnidadeProdutivaService
from core.services.geoprocessamento_service import GeoprocessamentoService

router = APIRouter(prefix="/unidades-produtivas", tags=["Core — Unidades Produtivas"])

@router.get(
    "/",
    response_model=List[UnidadeProdutivaResponse],
    summary="Lista todas as unidades produtivas do Tenant logado",
)
async def listar_unidades_produtivas(
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("CORE")),
):
    svc = UnidadeProdutivaService(session, tenant_id)
    return await svc.list_all()

@router.post(
    "/",
    response_model=UnidadeProdutivaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra uma nova unidade produtiva atrelada ao tenant",
    dependencies=[Depends(require_limit("max_fazendas"))],
)
async def criar_unidade_produtiva(
    dados: UnidadeProdutivaCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("CORE")),
):
    svc = UnidadeProdutivaService(session, tenant_id)
    unidade = await svc.create_unidade_produtiva(dados)
    await session.flush()  # garante o id antes de criar filhos

    from core.cadastros.propriedades.models import AreaRural
    from core.cadastros.propriedades.service import AreaRuralService
    area_svc = AreaRuralService(AreaRural, session, tenant_id)
    await area_svc.criar_estrutura_base(unidade.id)

    await session.commit()
    return unidade

@router.get(
    "/{unidade_produtiva_id}",
    response_model=UnidadeProdutivaResponse,
    summary="Obtém detalhes de uma unidade produtiva específica",
)
async def obter_unidade_produtiva(
    unidade_produtiva_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = UnidadeProdutivaService(session, tenant_id)
    return await svc.get_or_fail(unidade_produtiva_id)

@router.put(
    "/{unidade_produtiva_id}",
    response_model=UnidadeProdutivaResponse,
    summary="Atualiza dados da unidade produtiva",
)
async def atualizar_unidade_produtiva(
    unidade_produtiva_id: uuid.UUID,
    dados: UnidadeProdutivaUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = UnidadeProdutivaService(session, tenant_id)
    unidade = await svc.update(unidade_produtiva_id, dados)
    await session.commit()
    return unidade


# =============================================================================
# UPLOAD DE LOGO
# =============================================================================

@router.post(
    "/{unidade_produtiva_id}/logo",
    response_model=dict,
    summary="Upload do logotipo da propriedade",
)
async def upload_logo(
    unidade_produtiva_id: uuid.UUID,
    arquivo: UploadFile = File(..., description="Imagem do logo (JPEG, PNG, WebP). Máx 2MB."),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if arquivo.content_type not in allowed:
        raise HTTPException(status_code=400, detail=f"Tipo não suportado. Use: {', '.join(allowed)}")

    content = await arquivo.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Logo deve ter no máximo 2MB.")

    import hashlib as _hashlib
    from pathlib import Path
    from sqlalchemy import select as _select
    from core.models.unidade_produtiva import UnidadeProdutiva as _UP

    result = await session.execute(
        _select(_UP).where(_UP.id == unidade_produtiva_id, _UP.tenant_id == tenant_id)
    )
    unidade = result.scalar_one_or_none()
    if not unidade:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada.")

    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}.get(arquivo.content_type, ".jpg")
    filename_hash = _hashlib.md5(content).hexdigest()[:12]
    filename = f"{filename_hash}{ext}"

    storage_dir = Path("/tmp/agrosaas_logos")
    storage_dir.mkdir(parents=True, exist_ok=True)
    (storage_dir / filename).write_bytes(content)

    logo_url = f"/static/logos/{filename}"
    unidade.logo_url = logo_url
    await session.commit()

    return {"logo_url": logo_url}


# =============================================================================
# UPLOAD DE ARQUIVOS GEOESPACIAIS
# =============================================================================

@router.post("/upload-shapefile")
async def upload_shapefile(
    arquivo: UploadFile = File(..., description="Arquivo ZIP contendo shapefile (.shp, .dbf, .shx, .prj)"),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    if not arquivo.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser um ZIP contendo shapefile")
    conteudo = await arquivo.read()
    svc = GeoprocessamentoService(session, tenant_id)
    try:
        resultado = await svc.processar_shapefile(conteudo)
        return {
            "sucesso": True,
            "mensagem": f"Shapefile processado com sucesso. {resultado['total_features']} feature(s) encontrada(s).",
            "dados": resultado,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/upload-kml")
async def upload_kml(
    arquivo: UploadFile = File(..., description="Arquivo KML ou KMZ"),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    if not arquivo.filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo não informado")
    is_kmz = arquivo.filename.lower().endswith('.kmz')
    is_kml = arquivo.filename.lower().endswith('.kml')
    if not (is_kml or is_kmz):
        raise HTTPException(status_code=400, detail="Arquivo deve ser KML ou KMZ")
    conteudo = await arquivo.read()
    svc = GeoprocessamentoService(session, tenant_id)
    try:
        resultado = await svc.processar_kml(conteudo, is_kmz=is_kmz)
        return {
            "sucesso": True,
            "mensagem": f"KML processado com sucesso. {resultado['propriedades'].get('total_poligonos', 0)} polígono(s) encontrado(s).",
            "dados": resultado,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/validar-geometria")
async def validar_geometria(
    geometria: dict,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    svc = GeoprocessamentoService(session, tenant_id)
    try:
        resultado = await svc.validar_geometria(geometria)
        if resultado["valida"]:
            return {"valida": True, "area_ha": resultado["area_ha"], "bounds": resultado["bounds"]}
        else:
            return {"valida": False, "erros": resultado["erros"], "area_ha": resultado["area_ha"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao validar: {str(e)}")
