from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role, get_session_with_tenant
from agricola.rastreabilidade.schemas import (
    LoteRastreabilidadeCreate, LoteRastreabilidadeResponse,
    CertificacaoCreate, CertificacaoResponse
)
from agricola.rastreabilidade.service import RastreabilidadeService, CertificacaoService

router = APIRouter(prefix="/rastreabilidade", tags=["Rastreabilidade e Certificações"])

@router.post("/lotes", response_model=LoteRastreabilidadeResponse, status_code=status.HTTP_201_CREATED)
async def criar_lote(
    dados: LoteRastreabilidadeCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A5_COLHEITA")),
):
    svc = RastreabilidadeService(session, tenant_id)
    return await svc.criar_lote(dados)

@router.get("/lotes/{lote_id}/cadeia")
async def cadeia_rastreabilidade(
    lote_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A5_COLHEITA")),
):
    """Retorna a cadeia completa: lote → safra → talhão → operações + insumos → romaneios."""
    svc = RastreabilidadeService(session, tenant_id)
    return await svc.cadeia_rastreabilidade(lote_id)


@router.get("/lotes", response_model=List[LoteRastreabilidadeResponse])
async def listar_lotes(
    safra_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A5_COLHEITA")),
):
    svc = RastreabilidadeService(session, tenant_id)
    filters = {}
    if safra_id: filters["safra_id"] = safra_id
    return await svc.list_all(**filters)


@router.get("/produto-colhido/{produto_colhido_id}")
async def rastreabilidade_produto_colhido(
    produto_colhido_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A5_COLHEITA")),
):
    """
    Rastreabilidade por ProdutoColhido — cadeia completa:
    ProdutoColhido → Safra → Talhão → Operações → Romaneios → Comercializações.

    Ideal para consultar a origem de um lote em estoque.
    """
    from agricola.colheita.models import ProdutoColhido
    from core.exceptions import EntityNotFoundError, BusinessRuleError
    pc = await session.get(ProdutoColhido, produto_colhido_id)
    if not pc or pc.tenant_id != tenant_id:
        raise EntityNotFoundError("Produto colhido não encontrado")

    svc = RastreabilidadeService(session, tenant_id)

    # Reutilizar a lógica de cadeia_rastreabilidade mas vinculada ao ProdutoColhido
    from agricola.safras.models import Safra
    from core.cadastros.propriedades.models import AreaRural
    from agricola.operacoes.models import OperacaoAgricola
    from agricola.romaneios.models import RomaneioColheita
    from core.cadastros.models import ProdutoCatalogo as Produto
    from financeiro.comercializacao.models import ComercializacaoCommodity
    from core.cadastros.commodities.models import Commodity

    safra = await session.get(Safra, pc.safra_id)
    if not safra:
        raise EntityNotFoundError(f"Safra {pc.safra_id} não encontrada.")
    talhao = await session.get(AreaRural, pc.talhao_id)

    # Operações
    stmt_ops = (
        select(OperacaoAgricola)
        .where(
            OperacaoAgricola.safra_id == pc.safra_id,
            OperacaoAgricola.talhao_id == pc.talhao_id,
            OperacaoAgricola.tenant_id == tenant_id,
        )
        .order_by(OperacaoAgricola.data_realizada)
    )
    operacoes = list((await session.execute(stmt_ops)).scalars().all())

    produto_ids = {i.insumo_id for op in operacoes for i in op.insumos}
    produtos: dict[UUID, Produto] = {}
    if produto_ids:
        stmt_prods = select(Produto).where(Produto.id.in_(produto_ids))
        produtos = {p.id: p for p in (await session.execute(stmt_prods)).scalars().all()}

    # Romaneios
    stmt_rom = (
        select(RomaneioColheita)
        .where(
            RomaneioColheita.safra_id == pc.safra_id,
            RomaneioColheita.talhao_id == pc.talhao_id,
            RomaneioColheita.tenant_id == tenant_id,
        )
        .order_by(RomaneioColheita.data_colheita)
    )
    romaneios = list((await session.execute(stmt_rom)).scalars().all())

    # Todos os produtos colhidos desta safra/talhão
    stmt_pc = (
        select(ProdutoColhido)
        .where(
            ProdutoColhido.safra_id == pc.safra_id,
            ProdutoColhido.talhao_id == pc.talhao_id,
            ProdutoColhido.tenant_id == tenant_id,
        )
        .order_by(ProdutoColhido.data_entrada)
    )
    todos_pc = list((await session.execute(stmt_pc)).scalars().all())

    # Commodities
    pc_commodity_ids = {p.commodity_id for p in todos_pc}
    commodities: dict[UUID, Commodity] = {}
    if pc_commodity_ids:
        stmt_comm = select(Commodity).where(Commodity.id.in_(pc_commodity_ids))
        commodities = {c.id: c for c in (await session.execute(stmt_comm)).scalars().all()}

    # Comercializações vinculadas
    pc_ids = [p.id for p in todos_pc]
    comercializacoes = []
    if pc_ids:
        stmt_comm = (
            select(ComercializacaoCommodity)
            .where(ComercializacaoCommodity.produto_colhido_id.in_(pc_ids))
            .order_by(ComercializacaoCommodity.created_at)
        )
        comercializacoes = list((await session.execute(stmt_comm)).scalars().all())

    # Destacar o produto consultado
    pc_destaque = {
        "id": str(pc.id),
        "commodity_nome": commodities[pc.commodity_id].nome if pc.commodity_id in commodities else None,
        "commodity_codigo": commodities[pc.commodity_id].codigo if pc.commodity_id in commodities else None,
        "quantidade": float(pc.quantidade),
        "unidade": pc.unidade,
        "peso_liquido_kg": float(pc.peso_liquido_kg),
        "umidade_pct": float(pc.umidade_pct) if pc.umidade_pct else None,
        "impureza_pct": float(pc.impureza_pct) if pc.impureza_pct else None,
        "status": pc.status,
        "destino": pc.destino,
        "data_entrada": pc.data_entrada.isoformat(),
    }

    # Comercializações deste produto específico
    comercializacoes_pc = [c for c in comercializacoes if c.produto_colhido_id == pc.id]

    return {
        "produto_colhido": pc_destaque,
        "safra": {
            "id": str(safra.id),
            "cultura": safra.cultura,
            "ano_safra": safra.ano_safra,
            "area_plantada_ha": float(safra.area_plantada_ha or 0),
            "status": safra.status,
            "commodity_id": str(safra.commodity_id) if safra.commodity_id else None,
        },
        "talhao": {
            "id": str(talhao.id) if talhao else None,
            "nome": talhao.nome if talhao else "—",
            "area_ha": float(talhao.area_hectares or talhao.area_hectares_manual or 0) if talhao else 0,
        } if talhao else None,
        "operacoes": [
            {
                "id": str(op.id),
                "tipo": op.tipo,
                "subtipo": op.subtipo,
                "descricao": op.descricao,
                "data_realizada": op.data_realizada.isoformat() if op.data_realizada else None,
                "custo_total": float(op.custo_total or 0),
                "insumos": [
                    {
                        "produto": produtos[i.insumo_id].nome if i.insumo_id in produtos else None,
                        "quantidade_total": float(i.quantidade_total or 0),
                    }
                    for i in op.insumos
                ],
            }
            for op in operacoes
        ],
        "romaneios": [
            {
                "id": str(r.id),
                "data_colheita": r.data_colheita.isoformat() if r.data_colheita else None,
                "peso_liquido_kg": float(r.peso_liquido_kg or 0),
                "sacas_60kg": float(r.sacas_60kg or 0),
            }
            for r in romaneios
        ],
        "comercializacoes": [
            {
                "id": str(c.id),
                "numero_contrato": c.numero_contrato,
                "quantidade": float(c.quantidade),
                "preco_unitario": float(c.preco_unitario),
                "valor_total": float(c.valor_total),
                "status": c.status,
                "data_entrega_prevista": c.data_entrega_prevista.isoformat() if c.data_entrega_prevista else None,
            }
            for c in comercializacoes_pc
        ],
        "resumo": {
            "custo_total_operacoes": round(sum(float(op.custo_total or 0) for op in operacoes), 2),
            "total_colhido_sacas": round(sum(float(r.sacas_60kg or 0) for r in romaneios), 2),
            "total_estoque_kg": round(sum(float(p.peso_liquido_kg or 0) for p in todos_pc), 2),
            "receita_vendas": round(sum(float(c.valor_total or 0) for c in comercializacoes_pc), 2),
        },
    }

@router.post("/certificacoes", response_model=CertificacaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_certificacao(
    dados: CertificacaoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A5_COLHEITA")),
):
    svc = CertificacaoService(session, tenant_id)
    return await svc.create(dados.model_dump())

@router.get("/certificacoes", response_model=List[CertificacaoResponse])
async def listar_certificacoes(
    unidade_produtiva_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A5_COLHEITA")),
):
    svc = CertificacaoService(session, tenant_id)
    filters = {}
    if unidade_produtiva_id: filters["unidade_produtiva_id"] = unidade_produtiva_id
    return await svc.list_all(**filters)
