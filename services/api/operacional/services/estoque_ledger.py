from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.tenant import Tenant  # noqa: F401 - registers FK target in metadata
from core.cadastros.commodities.models import Commodity  # noqa: F401 - registers FK target in metadata
from core.cadastros.pessoas.models import Pessoa  # noqa: F401 - registers FK target in metadata
from core.cadastros.produtos.models import Produto
from core.cadastros.propriedades.models import AreaRural  # noqa: F401 - registers FK target in metadata
from core.exceptions import BusinessRuleError
from core.measurements.models import UnidadeMedida  # noqa: F401 - registers FK target in metadata
from agricola.cultivos.models import Cultivo, CultivoArea  # noqa: F401 - registers FK target in metadata
from agricola.operacoes.models import OperacaoExecucao  # noqa: F401 - registers FK target in metadata
from agricola.production_units.models import ProductionUnit  # noqa: F401 - registers FK target in metadata
from agricola.safras.models import Safra  # noqa: F401 - registers FK target in metadata
from agricola.tarefas.models import SafraTarefa  # noqa: F401 - registers FK target in metadata
from operacional.models.estoque import EstoqueMovimento, LoteEstoque


UOM_ALIASES = {
    "SACA_60KG": "SC60",
    "SACA60": "SC60",
    "SC": "SC60",
    "SACAS": "SC60",
    "LITRO": "L",
    "LITROS": "L",
    "UNIDADE": "UN",
    "UNIDADES": "UN",
}

ORIGEM_ALIASES = {
    "PEDIDO_COMPRA": "COMPRA",
    "COMPRA_RECEBIMENTO": "COMPRA",
    "DEVOLUCAO_FORNECEDOR": "AJUSTE",
    "OPERACAO_AGRICOLA": "MANUAL",
    "ORDEM_SERVICO": "MANUAL",
    "INICIAL": "MANUAL",
}


def _normalizar_codigo_uom(codigo: str | None) -> str:
    normalizado = (codigo or "UN").strip().upper()
    return UOM_ALIASES.get(normalizado, normalizado)


def _normalizar_origem(origem: str | None) -> str:
    normalizada = (origem or "MANUAL").strip().upper()
    normalizada = ORIGEM_ALIASES.get(normalizada, normalizada)
    if normalizada not in {"OPERACAO_EXECUCAO", "COMPRA", "COLHEITA", "AJUSTE", "MANUAL", "TRANSFERENCIA"}:
        return "MANUAL"
    return normalizada


async def resolver_unidade_medida_id(
    session: AsyncSession,
    produto_id: UUID,
) -> UUID:
    produto = await session.get(Produto, produto_id)
    if not produto:
        raise BusinessRuleError(f"Produto {produto_id} não encontrado para registrar ledger de estoque.")

    codigo = _normalizar_codigo_uom(produto.unidade_medida)
    unidade_id = (await session.execute(text("""
        SELECT id
          FROM unidades_medida
         WHERE tenant_id IS NULL
           AND codigo = :codigo
           AND ativo = true
         LIMIT 1
    """), {"codigo": codigo})).scalar_one_or_none()
    if unidade_id:
        return unidade_id

    fallback = (await session.execute(text("""
        SELECT id
          FROM unidades_medida
         WHERE tenant_id IS NULL
           AND codigo = 'UN'
           AND ativo = true
         LIMIT 1
    """))).scalar_one_or_none()
    if not fallback:
        raise BusinessRuleError("Unidade de medida padrão UN não encontrada para ledger de estoque.")
    return fallback


async def registrar_ledger_estoque(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    produto_id: UUID,
    tipo_movimento: str,
    quantidade: float,
    origem: str,
    deposito_id: UUID | None = None,
    lote_id: UUID | None = None,
    custo_unitario: float | None = None,
    custo_total: float | None = None,
    origem_id: UUID | None = None,
    operacao_execucao_id: UUID | None = None,
    production_unit_id: UUID | None = None,
    ajuste_de: UUID | None = None,
    observacoes: str | None = None,
) -> EstoqueMovimento:
    origem = _normalizar_origem(origem)

    if tipo_movimento == "SAIDA" and quantidade > 0:
        quantidade = -quantidade
    elif tipo_movimento in {"ENTRADA", "SALDO_INICIAL", "DEVOLUCAO"} and quantidade < 0:
        quantidade = abs(quantidade)

    unidade_medida_id = await resolver_unidade_medida_id(session, produto_id)
    numero_lote = None
    if lote_id:
        lote = await session.get(LoteEstoque, lote_id)
        numero_lote = lote.numero_lote if lote else None

    if custo_total is None and custo_unitario is not None:
        custo_total = round(abs(float(quantidade)) * float(custo_unitario), 2)

    movimento = EstoqueMovimento(
        tenant_id=tenant_id,
        produto_id=produto_id,
        deposito_id=deposito_id,
        lote_id=lote_id,
        quantidade=quantidade,
        unidade_medida_id=unidade_medida_id,
        custo_unitario=custo_unitario,
        custo_total=custo_total,
        tipo_movimento=tipo_movimento,
        origem=origem,
        origem_id=origem_id,
        operacao_execucao_id=operacao_execucao_id,
        production_unit_id=production_unit_id,
        numero_lote=numero_lote,
        ajuste_de=ajuste_de,
        observacoes=observacoes,
    )
    session.add(movimento)
    return movimento
