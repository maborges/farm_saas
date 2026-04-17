"""
Router para gestão de hierarquia de áreas rurais vinculadas a produtores.

Este router cria endpoints que unem:
- Propriedade Econômica (cadastros_propriedades)
- Fazenda (fazendas)
- Áreas Rurais (cadastros_areas_rurais): Gleba, Talhão, Piquete, etc.

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
from sqlalchemy import select, and_, or_

from core.dependencies import get_session, get_tenant_id
from core.cadastros.propriedades.propriedade_models import (
    Propriedade,
    ExploracaoRural,
    NaturezaVinculo,
)
from core.cadastros.propriedades.schemas import (
    PropriedadeComHierarquiaResponse,
    AreaRuralCreate,
    AreaRuralUpdate,
    AreaRuralTreeResponse,
    AreaRuralResponse,
)
from core.cadastros.propriedades.service import AreaRuralService
from core.cadastros.propriedades.models import AreaRural, TipoArea

router = APIRouter(
    prefix="/cadastros/propriedades",
    tags=["Cadastros — Propriedades com Hierarquia"],
)


# ============================================================================
# Endpoints de Hierarquia Completa
# ============================================================================

@router.get(
    "/{propriedade_id}/hierarquia",
    response_model=PropriedadeComHierarquiaResponse,
)
async def obter_propriedade_com_hierarquia(
    propriedade_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """
    Obtém a propriedade econômica completa com toda hierarquia de áreas rurais.
    
    Retorna:
    - Dados da propriedade
    - Lista de fazendas vinculadas (via ExploracaoRural)
    - Para cada fazenda: árvore completa de áreas rurais (Glebas → Talhões → Piquetes)
    """
    # 1. Buscar propriedade
    stmt = select(Propriedade).where(
        and_(
            Propriedade.id == propriedade_id,
            Propriedade.tenant_id == tenant_id,
        )
    )
    result = await session.execute(stmt)
    propriedade = result.scalar_one_or_none()
    if not propriedade:
        raise HTTPException(404, "Propriedade não encontrada")
    
    # 2. Buscar explorações vigentes
    stmt_exploracoes = select(ExploracaoRural).where(
        and_(
            ExploracaoRural.propriedade_id == propriedade_id,
            ExploracaoRural.tenant_id == tenant_id,
            ExploracaoRural.ativo == True,
        )
    )
    result_exploracoes = await session.execute(stmt_exploracoes)
    exploracoes = list(result_exploracoes.scalars().all())
    
    # 3. Para cada exploração, buscar árvore de áreas rurais da fazenda
    fazendas_com_hierarquia = []
    for expl in exploracoes:
        # Buscar áreas rurais da fazenda
        areas_service = AreaRuralService(AreaRural, session, tenant_id)
        areas_raizes = await areas_service.listar_raizes(unidade_produtiva_id=expl.unidade_produtiva_id)
        
        # Construir árvore para cada raiz
        arvore_areas = []
        for raiz in areas_raizes:
            arvore = await _construir_arvore_areas(session, tenant_id, raiz.id)
            arvore_areas.append(arvore)
        
        fazendas_com_hierarquia.append({
            "unidade_produtiva_id": expl.unidade_produtiva_id,
            "exploracao_id": expl.id,
            "natureza": expl.natureza,
            "data_inicio": expl.data_inicio,
            "data_fim": expl.data_fim,
            "areas": arvore_areas,
        })
    
    return {
        "propriedade": propriedade,
        "fazendas": fazendas_com_hierarquia,
    }


@router.get(
    "/{propriedade_id}/fazendas/{unidade_produtiva_id}/areas",
    response_model=list[AreaRuralTreeResponse],
)
async def listar_areas_por_fazenda(
    propriedade_id: uuid.UUID,
    unidade_produtiva_id: uuid.UUID,
    tipo: Optional[str] = Query(None, description="Filtrar por tipo (GLEBA, TALHAO, etc)"),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """
    Lista todas as áreas rurais de uma fazenda em formato de árvore.
    """
    # Verificar se propriedade e fazenda estão vinculadas
    stmt = select(ExploracaoRural).where(
        and_(
            ExploracaoRural.propriedade_id == propriedade_id,
            ExploracaoRural.unidade_produtiva_id == unidade_produtiva_id,
            ExploracaoRural.tenant_id == tenant_id,
        )
    )
    result = await session.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(400, "Fazenda não vinculada a esta propriedade")
    
    # Buscar áreas rurais
    areas_service = AreaRuralService(AreaRural, session, tenant_id)
    
    if tipo:
        areas_raizes = await areas_service.listar(unidade_produtiva_id=unidade_produtiva_id, tipo=tipo, parent_id=None)
    else:
        areas_raizes = await areas_service.listar_raizes(unidade_produtiva_id=unidade_produtiva_id)
    
    # Construir árvores
    arvores = []
    for raiz in areas_raizes:
        arvore = await _construir_arvore_areas(session, tenant_id, raiz.id)
        arvores.append(arvore)
    
    return arvores


# ============================================================================
# Endpoints de Gestão de Áreas Rurais (CRUD)
# ============================================================================

@router.post(
    "/{propriedade_id}/fazendas/{unidade_produtiva_id}/areas",
    response_model=AreaRuralResponse,
    status_code=201,
)
async def criar_area_rural(
    propriedade_id: uuid.UUID,
    unidade_produtiva_id: uuid.UUID,
    data: AreaRuralCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """
    Cria uma nova área rural (Gleba, Talhão, Piquete, etc.) vinculada a uma fazenda.
    """
    # Verificar vínculo
    stmt = select(ExploracaoRural).where(
        and_(
            ExploracaoRural.propriedade_id == propriedade_id,
            ExploracaoRural.unidade_produtiva_id == unidade_produtiva_id,
            ExploracaoRural.tenant_id == tenant_id,
        )
    )
    result = await session.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(400, "Fazenda não vinculada a esta propriedade")
    
    # Criar área
    areas_service = AreaRuralService(AreaRural, session, tenant_id)
    area_data = data.model_dump()
    area_data["unidade_produtiva_id"] = unidade_produtiva_id
    
    return await areas_service.criar_area(area_data)


@router.patch(
    "/fazendas/{unidade_produtiva_id}/areas/{area_id}",
    response_model=AreaRuralResponse,
)
async def atualizar_area_rural(
    unidade_produtiva_id: uuid.UUID,
    area_id: uuid.UUID,
    data: AreaRuralUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Atualiza uma área rural existente."""
    areas_service = AreaRuralService(AreaRural, session, tenant_id)
    return await areas_service.atualizar_area(area_id, data.model_dump(exclude_none=True))


@router.delete(
    "/fazendas/{unidade_produtiva_id}/areas/{area_id}",
    status_code=204,
)
async def remover_area_rural(
    unidade_produtiva_id: uuid.UUID,
    area_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Remove (soft delete) uma área rural e todas as suas filhas."""
    areas_service = AreaRuralService(AreaRural, session, tenant_id)
    await areas_service.soft_delete(area_id)


# ============================================================================
# Helpers
# ============================================================================

async def _construir_arvore_areas(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    area_id: uuid.UUID,
) -> AreaRuralTreeResponse:
    """Constrói árvore recursiva de áreas rurais."""
    from core.cadastros.propriedades.schemas import AreaRuralResponse
    
    stmt = select(AreaRural).where(
        and_(
            AreaRural.id == area_id,
            AreaRural.tenant_id == tenant_id,
            AreaRural.ativo == True,
        )
    )
    result = await session.execute(stmt)
    area = result.scalar_one_or_none()
    
    if not area:
        raise HTTPException(404, f"Área {area_id} não encontrada")
    
    # Buscar filhos
    stmt_filhos = select(AreaRural).where(
        and_(
            AreaRural.parent_id == area_id,
            AreaRural.tenant_id == tenant_id,
            AreaRural.ativo == True,
        )
    )
    result_filhos = await session.execute(stmt_filhos)
    filhos = list(result_filhos.scalars().all())
    
    # Recursão
    filhos_arvore = []
    for filho in filhos:
        filhos_arvore.append(
            await _construir_arvore_areas(session, tenant_id, filho.id)
        )
    
    return AreaRuralTreeResponse(
        id=area.id,
        tenant_id=area.tenant_id,
        unidade_produtiva_id=area.unidade_produtiva_id,
        parent_id=area.parent_id,
        tipo=area.tipo,
        nome=area.nome,
        codigo=area.codigo,
        descricao=area.descricao,
        area_hectares=area.area_hectares,
        area_hectares_manual=area.area_hectares_manual,
        geometria=area.geometria,
        centroide_lat=area.centroide_lat,
        centroide_lng=area.centroide_lng,
        dados_extras=area.dados_extras,
        ativo=area.ativo,
        created_at=area.created_at,
        updated_at=area.updated_at,
        filhos=filhos_arvore,
    )
