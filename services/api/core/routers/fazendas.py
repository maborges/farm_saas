from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form
from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_session_with_tenant
from core.dependencies import get_tenant_id, require_module, require_role, require_limit
from core.schemas.fazenda_input import FazendaCreate, FazendaUpdate
from core.schemas.fazenda_output import FazendaResponse
from core.services.fazenda_service import FazendaService
from core.services.geoprocessamento_service import GeoprocessamentoService

router = APIRouter(prefix="/fazendas", tags=["Core — Fazendas"])

@router.get(
    "/",
    response_model=List[FazendaResponse],
    summary="Lista todas as fazendas do Tenant logado",
)
async def listar_fazendas(
    # Dependencies
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("CORE")),
    # Sem require_role pois quem tem modulo CORE no tenant pode ver suas fazendas globais
):
    svc = FazendaService(session, tenant_id)
    fazendas = await svc.list_all()
    return fazendas

@router.post(
    "/",
    response_model=FazendaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra uma nova fazenda rural atrelada ao tenant",
    dependencies=[Depends(require_limit("max_fazendas"))],  # Valida limite de fazendas!
)
async def criar_fazenda(
    dados: FazendaCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("CORE")),
):
    svc = FazendaService(session, tenant_id)
    fazenda = await svc.create_fazenda(dados)
    # Importante: Como SQLAlchemy não auto-comita logo que se adiciona para permitir rollbacks:
    await session.commit()
    return fazenda

@router.get(
    "/{fazenda_id}",
    response_model=FazendaResponse,
    summary="Obtém detalhes de uma fazenda específica",
)
async def obter_fazenda(
    fazenda_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = FazendaService(session, tenant_id)
    # Se id não existir OU não pertencer ao tenant logado, levanta EntityNotFoundError
    fazenda = await svc.get_or_fail(fazenda_id)
    return fazenda

@router.put(
    "/{fazenda_id}",
    response_model=FazendaResponse,
    summary="Atualiza dados da fazenda",
)
async def atualizar_fazenda(
    fazenda_id: uuid.UUID,
    dados: FazendaUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = FazendaService(session, tenant_id)
    fazenda = await svc.update(fazenda_id, dados)
    await session.commit()
    return fazenda


# =============================================================================
# UPLOAD DE ARQUIVOS GEOESPACIAIS
# =============================================================================

@router.post("/upload-shapefile")
async def upload_shapefile(
    arquivo: UploadFile = File(..., description="Arquivo ZIP contendo shapefile (.shp, .dbf, .shx, .prj)"),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Faz upload de shapefile e retorna geometria GeoJSON + área calculada.
    
    O arquivo ZIP deve conter no mínimo:
    - .shp (geometria)
    - .dbf (atributos)
    - .shx (índice)
    - .prj (projeção, opcional mas recomendado)
    
    Retorna:
    - geometria: GeoJSON da geometria
    - area_ha: Área calculada em hectares
    - propriedades: Atributos da feature
    - crs: Sistema de referência espacial
    """
    # Validar tipo de arquivo
    if not arquivo.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser um ZIP contendo shapefile")
    
    # Ler conteúdo
    conteudo = await arquivo.read()
    
    # Processar
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
    """
    Faz upload de KML/KMZ e retorna geometria GeoJSON + área calculada.
    
    Retorna:
    - geometria: GeoJSON da geometria
    - area_ha: Área calculada em hectares
    - propriedades: Nomes e metadados
    """
    # Validar tipo de arquivo
    if not arquivo.filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo não informado")
    
    is_kmz = arquivo.filename.lower().endswith('.kmz')
    is_kml = arquivo.filename.lower().endswith('.kml')
    
    if not (is_kml or is_kmz):
        raise HTTPException(status_code=400, detail="Arquivo deve ser KML ou KMZ")
    
    # Ler conteúdo
    conteudo = await arquivo.read()
    
    # Processar
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
    """
    Valida geometria GeoJSON e calcula área.
    
    Útil para validar geometria antes de salvar fazenda.
    """
    svc = GeoprocessamentoService(session, tenant_id)
    
    try:
        resultado = await svc.validar_geometria(geometria)
        
        if resultado["valida"]:
            return {
                "valida": True,
                "area_ha": resultado["area_ha"],
                "bounds": resultado["bounds"],
            }
        else:
            return {
                "valida": False,
                "erros": resultado["erros"],
                "area_ha": resultado["area_ha"],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao validar: {str(e)}")
