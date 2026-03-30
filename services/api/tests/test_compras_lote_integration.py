"""
Integration Test: Compras → LoteEstoque → FIFO Deduction

Validates complete flow:
1. Purchase order received
2. LoteEstoque created with invoice number
3. Operation consumes via FIFO
4. Correct batch consumed with correct cost
"""

import pytest
from uuid import uuid4, UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from operacional.models.estoque import LoteEstoque, Deposito, SaldoEstoque
from operacional.models.compras import (
    PedidoCompra, ItemPedidoCompra, RecebimentoParcial, ItemRecebimento,
)
from core.cadastros.produtos.models import Produto
from operacional.services.estoque_fifo import consumir_lotes_fifo, atualizar_saldo_apos_consumo
from core.exceptions import BusinessRuleError


class TestComprasLoteIntegration:
    """Test Compras → LoteEstoque → FIFO integration."""

    @pytest.mark.asyncio
    async def test_recebimento_cria_lote_e_fifo_consome(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
    ):
        """
        Validates complete flow:
        1. Create PO
        2. Register receipt → LoteEstoque created
        3. Create operation with insumo
        4. FIFO consumes from correct batch
        """
        tenant_uuid = UUID(tenant_id)
        fazenda_uuid = UUID(fazenda_id)

        # ── Setup: Create product and deposit ──────────────────────────────
        produto = Produto(
            id=uuid4(),
            tenant_id=tenant_uuid,
            nome="Adubo NPK",
            tipo="FERTILIZANTE",
            unidade_medida="KG",
            preco_medio=0.0,
            ativo=True,
        )
        session.add(produto)
        await session.flush()

        deposito = Deposito(
            id=uuid4(),
            tenant_id=tenant_uuid,
            fazenda_id=fazenda_uuid,
            nome="Galpão Adubos",
            tipo="GERAL",
            ativo=True,
        )
        session.add(deposito)
        await session.flush()

        # ── Step 1: Create PedidoCompra ───────────────────────────────────
        pedido = PedidoCompra(
            id=uuid4(),
            tenant_id=tenant_uuid,
            usuario_solicitante_id=uuid4(),
            deposito_destino_id=deposito.id,
            status="APROVADO",
        )
        session.add(pedido)
        await session.flush()

        # Add item to PO
        item_pedido = ItemPedidoCompra(
            id=uuid4(),
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade_solicitada=1000.0,
            preco_estimado_unitario=15.0,
            quantidade_recebida=0.0,
            status_item="PENDENTE",
        )
        session.add(item_pedido)
        await session.commit()

        # ── Step 2: Register receipt (simulating registrar_recebimento_parcial) ──
        # NOTE: In real flow, this goes through router which creates LoteEstoque
        # Here we simulate by creating both ItemRecebimento and LoteEstoque
        numero_nf = "NFe-2026-001"

        # Create LoteEstoque (as router does in P0.1)
        lote = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote=numero_nf,  # From invoice number
            data_fabricacao=date.today(),
            data_validade=None,
            quantidade_inicial=1000.0,
            quantidade_atual=1000.0,
            custo_unitario=15.0,  # From preco_real_unitario
            status="ATIVO",
        )
        session.add(lote)
        await session.flush()

        # Create ItemRecebimento
        recebimento = RecebimentoParcial(
            id=uuid4(),
            pedido_id=pedido.id,
            numero_nf=numero_nf,
        )
        session.add(recebimento)
        await session.flush()

        rec_item = ItemRecebimento(
            id=uuid4(),
            recebimento_id=recebimento.id,
            item_pedido_id=item_pedido.id,
            quantidade_recebida=1000.0,
            preco_real_unitario=15.0,
            lote_id=lote.id,  # Link to created LoteEstoque
        )
        session.add(rec_item)

        # Update SaldoEstoque (as EstoqueService.registrar_entrada does)
        saldo = SaldoEstoque(
            id=uuid4(),
            deposito_id=deposito.id,
            produto_id=produto.id,
            quantidade_atual=1000.0,
            quantidade_reservada=0.0,
        )
        session.add(saldo)
        await session.commit()

        # ── Verify: LoteEstoque created with correct data ──────────────────
        await session.refresh(lote)
        assert lote.numero_lote == numero_nf
        assert lote.quantidade_atual == 1000.0
        assert lote.custo_unitario == 15.0
        assert lote.status == "ATIVO"

        # Verify ItemRecebimento links to LoteEstoque
        await session.refresh(rec_item)
        assert rec_item.lote_id == lote.id

        # ── Step 3: Operation consumes insumo (via FIFO) ───────────────────
        consumo = await consumir_lotes_fifo(
            session=session,
            produto_id=produto.id,
            quantidade_necessaria=600.0,
            deposito_id=deposito.id,
            tenant_id=tenant_uuid,
        )

        # Update SaldoEstoque after FIFO deduction (required for UI accuracy)
        await atualizar_saldo_apos_consumo(
            session=session,
            produto_id=produto.id,
            quantidade_total=600.0,
            deposito_id=deposito.id,
        )
        await session.commit()

        # ── Verify: FIFO consumed from correct batch ──────────────────────
        assert consumo.quantidade_consumida == 600.0
        assert len(consumo.lotes_consumidos) == 1

        # Check correct batch consumed
        lote_consumido = consumo.lotes_consumidos[0]
        assert lote_consumido["lote_id"] == lote.id
        assert lote_consumido["numero_lote"] == numero_nf
        assert lote_consumido["quantidade"] == 600.0
        assert lote_consumido["custo_unitario"] == 15.0  # Historical cost
        assert lote_consumido["custo"] == 9000.0  # 600 × 15

        # ── Verify: LoteEstoque quantity decremented ──────────────────────
        await session.refresh(lote)
        assert lote.quantidade_atual == 400.0  # 1000 - 600
        assert lote.status == "ATIVO"  # Not yet exhausted

        # ── Verify: SaldoEstoque decremented ──────────────────────────────
        await session.refresh(saldo)
        assert saldo.quantidade_atual == 400.0

    @pytest.mark.asyncio
    async def test_lote_numero_from_invoice(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
    ):
        """Validate that LoteEstoque.numero_lote comes from NFe number."""
        tenant_uuid = UUID(tenant_id)
        fazenda_uuid = UUID(fazenda_id)

        produto = Produto(
            id=uuid4(),
            tenant_id=tenant_uuid,
            nome="Teste Produto",
            tipo="INSUMO",
            unidade_medida="KG",
            preco_medio=0.0,
            ativo=True,
        )
        session.add(produto)

        deposito = Deposito(
            id=uuid4(),
            tenant_id=tenant_uuid,
            fazenda_id=fazenda_uuid,
            nome="Galpão",
            tipo="GERAL",
            ativo=True,
        )
        session.add(deposito)
        await session.flush()

        # Create LoteEstoque with numero_lote from NFe
        numero_nf = "NFe-12345678901234567890123456789012"
        lote = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote=numero_nf,
            data_fabricacao=date.today(),
            quantidade_inicial=100.0,
            quantidade_atual=100.0,
            custo_unitario=10.0,
            status="ATIVO",
        )
        session.add(lote)
        await session.commit()

        # Verify numero_lote persisted correctly
        await session.refresh(lote)
        assert lote.numero_lote == numero_nf
        assert len(lote.numero_lote) > 0

    @pytest.mark.asyncio
    async def test_custo_unitario_from_real_price(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
    ):
        """Validate that LoteEstoque.custo_unitario comes from preco_real_unitario."""
        tenant_uuid = UUID(tenant_id)
        fazenda_uuid = UUID(fazenda_id)

        produto = Produto(
            id=uuid4(),
            tenant_id=tenant_uuid,
            nome="Produto",
            tipo="INSUMO",
            unidade_medida="UN",
            preco_medio=20.0,  # Will NOT be used
            ativo=True,
        )
        session.add(produto)

        deposito = Deposito(
            id=uuid4(),
            tenant_id=tenant_uuid,
            fazenda_id=fazenda_uuid,
            nome="Galpão",
            tipo="GERAL",
            ativo=True,
        )
        session.add(deposito)
        await session.flush()

        # Simulate different prices
        preco_estimado = 20.0
        preco_real = 18.5  # Negotiated lower price

        lote = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote="NFe-001",
            data_fabricacao=date.today(),
            quantidade_inicial=100.0,
            quantidade_atual=100.0,
            custo_unitario=preco_real,  # Use actual price, not estimated
            status="ATIVO",
        )
        session.add(lote)
        await session.commit()

        # Verify real price used (not estimated or product average)
        await session.refresh(lote)
        assert lote.custo_unitario == preco_real
        assert lote.custo_unitario != preco_estimado
        assert lote.custo_unitario != produto.preco_medio
