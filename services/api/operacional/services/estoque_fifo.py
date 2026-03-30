"""
FIFO (First In, First Out) inventory deduction for agricultural operations.

When an operation is created with inputs:
1. Find all LoteEstoque batches for the product (oldest first)
2. Deduct quantidade from each batch until fully consumed
3. Calculate cost: quantidade × lote.custo_unitario
4. Record MovimentacaoEstoque for each batch consumed
5. Update SaldoEstoque and LoteEstoque.quantidade_atual
"""

from uuid import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, join
from loguru import logger

from core.exceptions import BusinessRuleError
from operacional.models.estoque import LoteEstoque, SaldoEstoque, MovimentacaoEstoque, Deposito
from core.cadastros.produtos.models import Produto


class EstoqueConsumidoFIFO:
    """Result of FIFO consumption - tracks what was consumed and cost."""

    def __init__(self):
        self.lotes_consumidos: list[dict] = []  # [{"lote_id": uuid, "deposito_id": uuid, "quantidade": float, "custo": float, ...}]
        self.custo_total: float = 0.0
        self.quantidade_consumida: float = 0.0


async def consumir_lotes_fifo(
    session: AsyncSession,
    produto_id: UUID,
    quantidade_necessaria: float,
    deposito_id: UUID | None = None,
    tenant_id: UUID | None = None,
) -> EstoqueConsumidoFIFO:
    """
    Consume inventory using FIFO method: oldest batches first.

    Args:
        session: AsyncSession
        produto_id: Product to consume
        quantidade_necessaria: Total quantity to consume
        deposito_id: Specific deposit (optional, searches all if None)
        tenant_id: Tenant ID for isolation

    Returns:
        EstoqueConsumidoFIFO with lotes_consumidos and custo_total

    Raises:
        BusinessRuleError: If insufficient inventory
    """

    resultado = EstoqueConsumidoFIFO()
    quantidade_pendente = quantidade_necessaria

    # 1. Find all active batches for product (OLDEST FIRST = FIFO)
    stmt = select(LoteEstoque).join(Deposito).where(
        and_(
            LoteEstoque.produto_id == produto_id,
            LoteEstoque.status == "ATIVO",
            LoteEstoque.quantidade_atual > 0,
        )
    )

    # Filter by tenant_id if provided (multi-tenant isolation)
    if tenant_id:
        stmt = stmt.where(Deposito.tenant_id == tenant_id)

    # If deposito_id specified, filter to that deposit
    if deposito_id:
        stmt = stmt.where(LoteEstoque.deposito_id == deposito_id)

    # ORDER BY data_fabricacao ASC = oldest first (FIFO)
    stmt = stmt.order_by(LoteEstoque.data_fabricacao.asc().nullsfirst())

    lotes = list((await session.execute(stmt)).scalars().all())

    if not lotes:
        total_disponivel = 0.0
        raise BusinessRuleError(
            f"Produto {produto_id} não tem lotes ativos disponíveis. "
            f"Necessário: {quantidade_necessaria}, disponível: {total_disponivel}"
        )

    # 2. Consume from oldest batches until quantidade_pendente = 0
    for lote in lotes:
        if quantidade_pendente <= 0:
            break

        # How much to consume from this batch?
        quantidade_do_lote = min(quantidade_pendente, lote.quantidade_atual)

        # Calculate cost for this batch
        custo_do_lote = quantidade_do_lote * lote.custo_unitario

        # Record consumption (includes deposito_id for audit trail)
        resultado.lotes_consumidos.append({
            "lote_id": lote.id,
            "deposito_id": lote.deposito_id,
            "numero_lote": lote.numero_lote,
            "quantidade": quantidade_do_lote,
            "custo_unitario": lote.custo_unitario,
            "custo": custo_do_lote,
            "data_fabricacao": lote.data_fabricacao,
        })

        resultado.quantidade_consumida += quantidade_do_lote
        resultado.custo_total += custo_do_lote
        quantidade_pendente -= quantidade_do_lote

        # Update lote quantity
        lote.quantidade_atual -= quantidade_do_lote

        # Mark as esgotado if no more quantity
        if lote.quantidade_atual <= 0:
            lote.status = "ESGOTADO"
            logger.info(
                f"Batch {lote.numero_lote} exhausted after FIFO deduction",
                lote_id=str(lote.id),
                deposito_id=str(lote.deposito_id),
                quantidade_final=lote.quantidade_atual,
            )

        session.add(lote)

    # 3. Check if we consumed enough
    if quantidade_pendente > 0:
        total_disponivel = sum(l.quantidade_atual for l in lotes)
        logger.warning(
            f"Insufficient inventory for product {produto_id}",
            produto_id=str(produto_id),
            necessario=quantidade_necessaria,
            disponivel=resultado.quantidade_consumida,
            faltando=quantidade_pendente,
        )
        raise BusinessRuleError(
            f"Saldo insuficiente para produto {produto_id} (FIFO). "
            f"Necessário: {quantidade_necessaria}, "
            f"disponível: {resultado.quantidade_consumida}, "
            f"faltando: {quantidade_pendente}"
        )

    # Log successful FIFO consumption
    logger.info(
        f"FIFO deduction completed: {resultado.quantidade_consumida} units @ R$ {resultado.custo_total:.2f}",
        produto_id=str(produto_id),
        quantidade_consumida=resultado.quantidade_consumida,
        custo_total=resultado.custo_total,
        num_lotes_consumidos=len(resultado.lotes_consumidos),
        num_batches=len(resultado.lotes_consumidos),
    )

    await session.flush()
    return resultado


async def atualizar_saldo_apos_consumo(
    session: AsyncSession,
    produto_id: UUID,
    quantidade_total: float,
    deposito_id: UUID | None = None,
) -> None:
    """
    Update SaldoEstoque after FIFO consumption.
    Recalculates total from all lotes.
    """

    stmt = select(LoteEstoque).where(
        LoteEstoque.produto_id == produto_id,
        LoteEstoque.status == "ATIVO",
    )

    if deposito_id:
        stmt = stmt.where(LoteEstoque.deposito_id == deposito_id)

    lotes = list((await session.execute(stmt)).scalars().all())

    total_atual = sum(l.quantidade_atual for l in lotes)

    # Update SaldoEstoque
    if deposito_id:
        saldo_stmt = select(SaldoEstoque).where(
            SaldoEstoque.produto_id == produto_id,
            SaldoEstoque.deposito_id == deposito_id,
        )
    else:
        saldo_stmt = select(SaldoEstoque).where(
            SaldoEstoque.produto_id == produto_id,
        )

    saldos = list((await session.execute(saldo_stmt)).scalars().all())

    for saldo in saldos:
        saldo.quantidade_atual = total_atual
        saldo.ultima_atualizacao = datetime.now(timezone.utc)
        session.add(saldo)

    await session.flush()
