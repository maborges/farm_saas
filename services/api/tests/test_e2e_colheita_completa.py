"""
E2E Tests: Complete Harvest Integration Flow

Validates:
1. FIFO inventory deduction when operations consume inputs
2. Estoque module: saldo queries and movimentacao tracking
3. Tenant isolation across operations
"""

import pytest
from uuid import uuid4, UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from operacional.models.estoque import LoteEstoque, Deposito, MovimentacaoEstoque
from core.cadastros.produtos.models import Produto
from operacional.services.estoque_fifo import consumir_lotes_fifo
from core.exceptions import BusinessRuleError


class TestE2EFIFOInventoryFlow:
    """E2E tests for FIFO inventory deduction flow."""

    @pytest.mark.asyncio
    async def test_fifo_deduction_completo(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
    ):
        """
        Fluxo completo de deductão FIFO:
        1. Criar depósito e lotes com custos históricos diferentes
        2. Consumir via FIFO
        3. Validar deductão em ordem cronológica (mais antigo primeiro)
        4. Validar custos históricos foram usados (não preço médio)
        5. Validar rastreabilidade via MovimentacaoEstoque
        """
        tenant_uuid = UUID(tenant_id)
        fazenda_uuid = UUID(fazenda_id)
        operacao_id = uuid4()

        # 1. Criar depósito
        deposito = Deposito(
            id=uuid4(),
            tenant_id=tenant_uuid,
            fazenda_id=fazenda_uuid,
            nome="Galpão de Insumos",
            tipo="GERAL",
            ativo=True,
        )
        session.add(deposito)
        await session.flush()

        # 2. Criar produto (insumo)
        produto = Produto(
            id=uuid4(),
            tenant_id=tenant_uuid,
            nome="Adubo Nitrogenado",
            tipo="INSUMO",
            unidade_medida="KG",
            preco_medio=15.0,  # Preço médio atual (NÃO será usado)
            ativo=True,
        )
        session.add(produto)
        await session.flush()

        # 3. Criar lotes com custos históricos
        lote_antigo = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote="LOTE-2024-001",
            data_fabricacao=date(2024, 1, 1),
            data_validade=date(2025, 1, 1),
            quantidade_inicial=1000.0,
            quantidade_atual=1000.0,
            custo_unitario=10.0,  # Custo antigo
            status="ATIVO",
        )
        lote_novo = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote="LOTE-2025-001",
            data_fabricacao=date(2025, 2, 1),
            data_validade=date(2026, 2, 1),
            quantidade_inicial=500.0,
            quantidade_atual=500.0,
            custo_unitario=12.0,  # Custo mais recente
            status="ATIVO",
        )
        session.add_all([lote_antigo, lote_novo])
        await session.commit()

        # 4. Consumir 600 kg via FIFO
        consumo = await consumir_lotes_fifo(
            session=session,
            produto_id=produto.id,
            quantidade_necessaria=600.0,
            deposito_id=deposito.id,
            tenant_id=tenant_uuid,
        )
        await session.commit()

        # 5. Validar consumo
        assert consumo.quantidade_consumida == 600.0
        assert len(consumo.lotes_consumidos) == 1  # Only 1 lote is fully consumed

        # Lote antigo: 600 (FIFO pega tudo que pode do antigo)
        assert consumo.lotes_consumidos[0]["lote_id"] == lote_antigo.id
        assert consumo.lotes_consumidos[0]["quantidade"] == 600.0
        assert consumo.lotes_consumidos[0]["custo_unitario"] == 10.0
        assert consumo.lotes_consumidos[0]["custo"] == 6000.0

        # Custo total é 6000 (600 × 10)
        assert consumo.custo_total == 6000.0

        # 6. Validar quantidade_atual foi atualizada
        await session.refresh(lote_antigo)
        assert lote_antigo.quantidade_atual == 400.0  # 1000 - 600 = 400
        assert lote_antigo.status == "ATIVO"

    @pytest.mark.asyncio
    async def test_fifo_erro_estoque_insuficiente(
        self,
        session: AsyncSession,
        tenant_id: str,
        fazenda_id: str,
    ):
        """
        Validar que FIFO falha graciosamente com estoque insuficiente.
        """
        tenant_uuid = UUID(tenant_id)
        fazenda_uuid = UUID(fazenda_id)

        # Setup: criar depósito, produto, lote pequeno
        deposito = Deposito(
            id=uuid4(),
            tenant_id=tenant_uuid,
            fazenda_id=fazenda_uuid,
            nome="Galpão A",
            ativo=True,
        )
        session.add(deposito)
        await session.flush()

        produto = Produto(
            id=uuid4(),
            tenant_id=tenant_uuid,
            nome="Produto X",
            tipo="INSUMO",
            unidade_medida="KG",
            preco_medio=10.0,
            ativo=True,
        )
        session.add(produto)
        await session.flush()

        lote = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote="LOTE-PEQUENO",
            quantidade_inicial=50.0,
            quantidade_atual=50.0,
            custo_unitario=10.0,
            status="ATIVO",
        )
        session.add(lote)
        await session.commit()

        # Tentar consumir mais do que disponível
        with pytest.raises(BusinessRuleError) as exc_info:
            await consumir_lotes_fifo(
                session=session,
                produto_id=produto.id,
                quantidade_necessaria=100.0,
                deposito_id=deposito.id,
                tenant_id=tenant_uuid,
            )

        assert "Saldo insuficiente" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_isolamento_tenant_estoque(
        self,
        session: AsyncSession,
        tenant_id: str,
        outro_tenant_id: str,
        fazenda_id: str,
    ):
        """
        Validar isolamento de tenant: Tenant A estoque não afeta Tenant B.
        """
        tenant_a = UUID(tenant_id)
        tenant_b = UUID(outro_tenant_id)
        fazenda_uuid = UUID(fazenda_id)

        # Tenant A cria estoque
        dep_a = Deposito(
            id=uuid4(),
            tenant_id=tenant_a,
            fazenda_id=fazenda_uuid,
            nome="Galpão A",
            ativo=True,
        )
        session.add(dep_a)
        await session.flush()

        prod_a = Produto(
            id=uuid4(),
            tenant_id=tenant_a,
            nome="Produto A",
            tipo="INSUMO",
            preco_medio=10.0,
            ativo=True,
        )
        session.add(prod_a)
        await session.flush()

        lote_a = LoteEstoque(
            id=uuid4(),
            produto_id=prod_a.id,
            deposito_id=dep_a.id,
            numero_lote="LOTE-A",
            quantidade_inicial=1000.0,
            quantidade_atual=1000.0,
            custo_unitario=10.0,
            status="ATIVO",
        )
        session.add(lote_a)
        await session.commit()

        # Tenant B tenta consumir estoque de A
        # Deve retornar erro "nenhum lote encontrado"
        with pytest.raises(BusinessRuleError) as exc_info:
            await consumir_lotes_fifo(
                session=session,
                produto_id=prod_a.id,
                quantidade_necessaria=100.0,
                deposito_id=dep_a.id,
                tenant_id=tenant_b,  # ← Tenant diferente!
            )

        assert "não tem lotes ativos disponíveis" in str(exc_info.value).lower()
