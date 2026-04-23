from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role
from core.dependencies import get_session_with_tenant
from agricola.analises_solo.schemas import AnaliseSoloCreate, AnaliseSoloUpdate, AnaliseSoloResponse
from agricola.analises_solo.service import AnaliseSoloService

router = APIRouter(prefix="/analises-solo", tags=["Análises de Solo"])


@router.get("/culturas-disponiveis")
async def listar_culturas_disponiveis(
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    """Lista culturas do sistema + do tenant para uso no seletor do laudo."""
    svc = AnaliseSoloService(session, tenant_id)
    culturas = await svc.listar_culturas_disponiveis()
    return [
        {
            "id": str(c.id),
            "nome": c.nome,
            "grupo": c.grupo,
            "sistema": c.sistema,
            "v_meta_pct_padrao": float(c.v_meta_pct_padrao) if c.v_meta_pct_padrao else None,
        }
        for c in culturas
    ]


@router.post("/", response_model=AnaliseSoloResponse, status_code=status.HTTP_201_CREATED)
async def registrar_analise(
    dados: AnaliseSoloCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = AnaliseSoloService(session, tenant_id)
    analise = await svc.criar(dados)
    await session.commit()
    await session.refresh(analise)
    return AnaliseSoloResponse.model_validate(analise)


@router.get("/", response_model=List[AnaliseSoloResponse])
async def listar_analises(
    talhao_id: UUID | None = None,
    limit: int = Query(100, ge=1, le=100, description="Máximo de registros retornados"),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    svc = AnaliseSoloService(session, tenant_id)
    filters = {}
    if talhao_id:
        filters["talhao_id"] = talhao_id
    analises = await svc.list_all(limit=limit, **filters)
    return [AnaliseSoloResponse.model_validate(a) for a in analises]


@router.get("/{id}", response_model=AnaliseSoloResponse)
async def detalhar_analise(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    svc = AnaliseSoloService(session, tenant_id)
    analise = await svc.get_or_fail(id)
    return AnaliseSoloResponse.model_validate(analise)


@router.patch("/{id}", response_model=AnaliseSoloResponse)
async def atualizar_analise(
    id: UUID,
    dados: AnaliseSoloUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = AnaliseSoloService(session, tenant_id)
    analise = await svc.update(id, dados.model_dump(exclude_none=True))
    await session.commit()
    await session.refresh(analise)
    return AnaliseSoloResponse.model_validate(analise)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_analise(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = AnaliseSoloService(session, tenant_id)
    await svc.hard_delete(id)
    await session.commit()


@router.get("/{id}/recomendacoes")
async def recomendacoes_analise(
    id: UUID,
    cultura_id: Optional[UUID] = Query(None, description="UUID da cultura (preferencial)"),
    cultura: Optional[str] = Query("SOJA", description="Nome da cultura (fallback se cultura_id não informado)"),
    regiao: Optional[str] = Query(None, description="CERRADO | SUL | NORDESTE | SUDESTE | NORTE"),
    v_meta: Optional[float] = Query(None, description="Saturação por bases alvo (%) — usa padrão da cultura se omitido"),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    """Gera recomendações usando parâmetros cadastrados (com fallback Embrapa)."""
    svc = AnaliseSoloService(session, tenant_id)
    analise = await svc.get_or_fail(id)
    return await svc.gerar_recomendacoes(
        analise,
        cultura_id=cultura_id,
        cultura_nome=cultura or "SOJA",
        regiao=regiao,
        v_meta=v_meta,
    )

@router.get("/{id}/inteligencia")
async def analise_inteligente(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    """Gera recomendações usando o motor de regras agronômicas (RegraAgronomica)."""
    svc = AnaliseSoloService(session, tenant_id)
    return await svc.aplicar_regras(id)

@router.post("/{id}/gerar-tarefas", status_code=status.HTTP_201_CREATED)
async def gerar_tarefas_analise(
    id: UUID,
    safra_id: UUID = Query(..., description="ID da safra para vincular as tarefas"),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    user: dict = Depends(require_role(["agronomo", "admin"])),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    """Transforma as recomendações da análise em tarefas reais na safra."""
    svc = AnaliseSoloService(session, tenant_id)
    tarefas_ids = await svc.vincular_e_gerar_tarefas(id, safra_id, user_id=UUID(user["id"]) if "id" in user else None)
    await session.commit()
    return {"tarefas_geradas": [str(tid) for tid in tarefas_ids]}
