import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session, get_tenant_id
from core.exceptions import EntityNotFoundError, EntityAlreadyExistsError
from .models import Commodity, CommodityClassificacao, CotacaoCommodity
from .schemas import (
    CommodityCreate, CommodityUpdate, CommodityResponse,
    CommodityDetalhadaResponse,
    CommodityClassificacaoCreate, CommodityClassificacaoUpdate, CommodityClassificacaoResponse,
    CotacaoCommodityCreate, CotacaoCommodityUpdate, CotacaoCommodityResponse,
)
from .cotacao_service import CotacaoService
from .conversao import ConversaoUnidade

router = APIRouter(prefix="/cadastros/commodities", tags=["Cadastros — Commodities"])


# ===========================================================================
# Commodity — CRUD
# ===========================================================================

@router.get("/", response_model=list[CommodityResponse])
@router.get("", response_model=list[CommodityResponse])
async def listar(
    tipo: Optional[str] = Query(None),
    apenas_ativos: bool = Query(True),
    incluir_sistema: bool = Query(True, description="Incluir commodities padrão do sistema (sistema=True)"),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(Commodity)
    if incluir_sistema:
        stmt = stmt.where(
            or_(
                Commodity.tenant_id == tenant_id,
                Commodity.sistema == True,
            )
        )
    else:
        stmt = stmt.where(Commodity.tenant_id == tenant_id)
    if apenas_ativos:
        stmt = stmt.where(Commodity.ativo == True)
    if tipo:
        stmt = stmt.where(Commodity.tipo == tipo)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/", response_model=CommodityResponse, status_code=201)
@router.post("", response_model=CommodityResponse, status_code=201)
async def criar(
    data: CommodityCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    # Verificar unicidade de nome por tenant
    stmt = select(Commodity).where(
        Commodity.tenant_id == tenant_id,
        Commodity.nome == data.nome,
        Commodity.ativo == True,
    )
    existente = (await session.execute(stmt)).scalar_one_or_none()
    if existente:
        raise EntityAlreadyExistsError(f"Já existe uma commodity ativa com o nome '{data.nome}'")

    obj = Commodity(tenant_id=tenant_id, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("/{commodity_id}", response_model=CommodityDetalhadaResponse)
async def obter(
    commodity_id: uuid.UUID,
    incluir_classificacoes: bool = Query(True),
    incluir_cotacao: bool = Query(True),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(Commodity).where(
        Commodity.id == commodity_id,
        or_(
            Commodity.tenant_id == tenant_id,
            Commodity.sistema == True,
        ),
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Commodity não encontrada")

    # Construir resposta detalhada
    data = CommodityDetalhadaResponse.model_validate(obj)

    if incluir_classificacoes:
        stmt_cls = select(CommodityClassificacao).where(
            CommodityClassificacao.commodity_id == commodity_id,
            CommodityClassificacao.ativo == True,
        )
        cls_result = await session.execute(stmt_cls)
        data.classificacoes = [
            CommodityClassificacaoResponse.model_validate(c)
            for c in cls_result.scalars().all()
        ]

    if incluir_cotacao:
        stmt_cot = select(CotacaoCommodity).where(
            CotacaoCommodity.commodity_id == commodity_id,
        ).order_by(CotacaoCommodity.data.desc()).limit(1)
        cot_result = await session.execute(stmt_cot)
        ultima = cot_result.scalar_one_or_none()
        if ultima:
            data.ultima_cotacao = CotacaoCommodityResponse.model_validate(ultima)

    return data


@router.patch("/{commodity_id}", response_model=CommodityResponse)
async def atualizar(
    commodity_id: uuid.UUID,
    data: CommodityUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    # Buscar a commodity (incluindo do sistema para dar erro adequado)
    stmt = select(Commodity).where(
        Commodity.id == commodity_id,
        or_(
            Commodity.tenant_id == tenant_id,
            Commodity.sistema == True,
        ),
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Commodity não encontrada")
    if obj.sistema:
        raise HTTPException(
            status_code=403,
            detail="Commodity do sistema — apenas administrador do SaaS pode alterar",
        )

    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)

    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/{commodity_id}", status_code=204)
async def remover(
    commodity_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    stmt = select(Commodity).where(
        Commodity.id == commodity_id,
        or_(
            Commodity.tenant_id == tenant_id,
            Commodity.sistema == True,
        ),
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Commodity não encontrada")
    if obj.sistema:
        raise HTTPException(
            status_code=403,
            detail="Commodity do sistema — apenas administrador do SaaS pode excluir",
        )
    obj.ativo = False
    await session.commit()


# ===========================================================================
# Helpers
# ===========================================================================

async def _verificar_posse_commodity(
    commodity_id: uuid.UUID,
    tenant_id: uuid.UUID,
    session: AsyncSession,
    permitir_escrita: bool = False,
) -> Commodity:
    """Verifica posse da commodity. Retorna o objeto ou lança erro adequado."""
    stmt = select(Commodity).where(
        Commodity.id == commodity_id,
        or_(
            Commodity.tenant_id == tenant_id,
            Commodity.sistema == True,
        ),
    )
    obj = (await session.execute(stmt)).scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Commodity não encontrada")
    if permitir_escrita and obj.sistema:
        raise HTTPException(
            status_code=403,
            detail="Commodity do sistema — apenas administrador do SaaS pode alterar",
        )
    return obj


# ===========================================================================
# CommodityClassificacao — CRUD aninhado
# ===========================================================================

classif_router = APIRouter(
    prefix="/cadastros/commodities/{commodity_id}/classificacoes",
    tags=["Cadastros — Commodities — Classificações"],
)


@classif_router.get("/", response_model=list[CommodityClassificacaoResponse])
async def listar_classificacoes(
    commodity_id: uuid.UUID,
    apenas_ativas: bool = Query(True),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _verificar_posse_commodity(commodity_id, tenant_id, session)

    stmt_cls = select(CommodityClassificacao).where(
        CommodityClassificacao.commodity_id == commodity_id,
    )
    if apenas_ativas:
        stmt_cls = stmt_cls.where(CommodityClassificacao.ativo == True)
    result = await session.execute(stmt_cls)
    return list(result.scalars().all())


@classif_router.post("/", response_model=CommodityClassificacaoResponse, status_code=201)
async def criar_classificacao(
    commodity_id: uuid.UUID,
    data: CommodityClassificacaoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _verificar_posse_commodity(commodity_id, tenant_id, session, permitir_escrita=True)

    obj = CommodityClassificacao(commodity_id=commodity_id, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@classif_router.get("/{classificacao_id}", response_model=CommodityClassificacaoResponse)
async def obter_classificacao(
    commodity_id: uuid.UUID,
    classificacao_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _verificar_posse_commodity(commodity_id, tenant_id, session)

    stmt = select(CommodityClassificacao).where(
        CommodityClassificacao.id == classificacao_id,
        CommodityClassificacao.commodity_id == commodity_id,
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Classificação não encontrada")
    return obj


@classif_router.patch("/{classificacao_id}", response_model=CommodityClassificacaoResponse)
async def atualizar_classificacao(
    commodity_id: uuid.UUID,
    classificacao_id: uuid.UUID,
    data: CommodityClassificacaoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _verificar_posse_commodity(commodity_id, tenant_id, session, permitir_escrita=True)

    stmt = select(CommodityClassificacao).where(
        CommodityClassificacao.id == classificacao_id,
        CommodityClassificacao.commodity_id == commodity_id,
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Classificação não encontrada")

    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)

    await session.commit()
    await session.refresh(obj)
    return obj


@classif_router.delete("/{classificacao_id}", status_code=204)
async def remover_classificacao(
    commodity_id: uuid.UUID,
    classificacao_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _verificar_posse_commodity(commodity_id, tenant_id, session, permitir_escrita=True)

    stmt = select(CommodityClassificacao).where(
        CommodityClassificacao.id == classificacao_id,
        CommodityClassificacao.commodity_id == commodity_id,
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Classificação não encontrada")
    obj.ativo = False
    await session.commit()


# ===========================================================================
# CotacaoCommodity — CRUD aninhado
# ===========================================================================

cotacao_router = APIRouter(
    prefix="/cadastros/commodities/{commodity_id}/cotacoes",
    tags=["Cadastros — Commodities — Cotações"],
)


@cotacao_router.get("/", response_model=list[CotacaoCommodityResponse])
async def listar_cotacoes(
    commodity_id: uuid.UUID,
    data_inicio: Optional[str] = Query(None, description="YYYY-MM-DD"),
    data_fim: Optional[str] = Query(None, description="YYYY-MM-DD"),
    fonte: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _verificar_posse_commodity(commodity_id, tenant_id, session)

    stmt_cot = select(CotacaoCommodity).where(
        CotacaoCommodity.commodity_id == commodity_id,
    )
    if data_inicio:
        stmt_cot = stmt_cot.where(CotacaoCommodity.data >= data_inicio)
    if data_fim:
        stmt_cot = stmt_cot.where(CotacaoCommodity.data <= data_fim)
    if fonte:
        stmt_cot = stmt_cot.where(CotacaoCommodity.fonte == fonte)
    stmt_cot = stmt_cot.order_by(CotacaoCommodity.data.desc())
    result = await session.execute(stmt_cot)
    return list(result.scalars().all())


@cotacao_router.post("/", response_model=CotacaoCommodityResponse, status_code=201)
async def criar_cotacao(
    commodity_id: uuid.UUID,
    data: CotacaoCommodityCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _verificar_posse_commodity(commodity_id, tenant_id, session, permitir_escrita=True)

    obj = CotacaoCommodity(commodity_id=commodity_id, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@cotacao_router.get("/ultima", response_model=CotacaoCommodityResponse)
async def ultima_cotacao(
    commodity_id: uuid.UUID,
    fonte: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _verificar_posse_commodity(commodity_id, tenant_id, session)

    stmt_cot = select(CotacaoCommodity).where(
        CotacaoCommodity.commodity_id == commodity_id,
    )
    if fonte:
        stmt_cot = stmt_cot.where(CotacaoCommodity.fonte == fonte)
    stmt_cot = stmt_cot.order_by(CotacaoCommodity.data.desc()).limit(1)
    result = await session.execute(stmt_cot)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Nenhuma cotação encontrada para esta commodity")
    return obj


@cotacao_router.delete("/{cotacao_id}", status_code=204)
async def remover_cotacao(
    commodity_id: uuid.UUID,
    cotacao_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _verificar_posse_commodity(commodity_id, tenant_id, session, permitir_escrita=True)

    stmt = select(CotacaoCommodity).where(
        CotacaoCommodity.id == cotacao_id,
        CotacaoCommodity.commodity_id == commodity_id,
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise EntityNotFoundError("Cotação não encontrada")
    await session.delete(obj)
    await session.commit()


# ===========================================================================
# Atualização automática de cotações
# ===========================================================================

@router.post("/cotacoes/atualizar")
async def atualizar_cotacoes(
    fonte: Optional[str] = Query(None, description="Forçar fonte específica: CEPEA, CBOT, B3"),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """
    Atualiza cotações de todas as commodities com `possui_cotacao=True`.

    Tenta cada fonte em ordem: CEPEA → CBOT → B3.
    Se nenhuma fonte retornar valor, registra falha no resultado.
    """
    svc = CotacaoService(session, tenant_id)
    try:
        resultado = await svc.atualizar_todas(fonte=fonte)
        return resultado
    finally:
        await svc.close()


# ===========================================================================
# ConversaoUnidade — CRUD aninhado
# ===========================================================================

conversao_router = APIRouter(
    prefix="/cadastros/commodities/{commodity_id}/conversoes",
    tags=["Cadastros — Commodities — Conversões de Unidade"],
)


@conversao_router.get("/")
async def listar_conversoes(
    commodity_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Lista todas as conversões disponíveis para uma commodity."""
    await _verificar_posse_commodity(commodity_id, tenant_id, session)

    stmt = select(ConversaoUnidade).where(
        ConversaoUnidade.commodity_id == commodity_id,
        ConversaoUnidade.ativo == True,
    ).order_by(ConversaoUnidade.unidade_origem, ConversaoUnidade.unidade_destino)
    result = await session.execute(stmt)
    itens = result.scalars().all()
    return [{
        "unidade_origem": i.unidade_origem,
        "unidade_destino": i.unidade_destino,
        "fator": i.fator,
        "descricao": i.descricao,
        "exemplo": f"1 {i.unidade_origem} = {i.fator} {i.unidade_destino}",
    } for i in itens]


@conversao_router.post("/")
async def criar_conversao(
    commodity_id: uuid.UUID,
    data: dict,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Cria uma nova conversão de unidades para a commodity."""
    await _verificar_posse_commodity(commodity_id, tenant_id, session, permitir_escrita=True)

    obj = ConversaoUnidade(
        commodity_id=commodity_id,
        unidade_origem=data["unidade_origem"],
        unidade_destino=data["unidade_destino"],
        fator=data["fator"],
        descricao=data.get("descricao"),
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return {
        "unidade_origem": obj.unidade_origem,
        "unidade_destino": obj.unidade_destino,
        "fator": obj.fator,
        "descricao": obj.descricao,
        "exemplo": f"1 {obj.unidade_origem} = {obj.fator} {obj.unidade_destino}",
    }


@conversao_router.post("/calcular")
async def calcular_conversao(
    commodity_id: uuid.UUID,
    data: dict,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """
    Calcula uma conversão de unidades sem persistir.
    Body: {\"quantidade\": 100, \"origem\": \"SACA_60KG\", \"destino\": \"TONELADA\"}
    """
    await _verificar_posse_commodity(commodity_id, tenant_id, session)

    quantidade = data["quantidade"]
    origem = data["origem"]
    destino = data["destino"]

    # Buscar fator na tabela
    stmt = select(ConversaoUnidade).where(
        ConversaoUnidade.commodity_id == commodity_id,
        ConversaoUnidade.unidade_origem == origem,
        ConversaoUnidade.unidade_destino == destino,
        ConversaoUnidade.ativo == True,
    )
    conv = (await session.execute(stmt)).scalar_one_or_none()

    if not conv:
        # Fallback: tentar calcular via peso_unidade da commodity
        from .models import Commodity
        comm = await session.get(Commodity, commodity_id)
        if comm and comm.peso_unidade and origem == comm.unidade_padrao and destino == "KG":
            resultado = quantidade * comm.peso_unidade
            return {"quantidade_origem": quantidade, "unidade_origem": origem,
                    "quantidade_destino": resultado, "unidade_destino": destino,
                    "origem": "peso_unidade_commodity"}

        raise HTTPException(404, f"Conversão {origem} → {destino} não encontrada para esta commodity")

    resultado = conv.converter(quantidade)
    return {
        "quantidade_origem": quantidade,
        "unidade_origem": origem,
        "quantidade_destino": round(resultado, 6),
        "unidade_destino": destino,
        "fator_usado": conv.fator,
        "origem": "tabela_conversao",
    }
