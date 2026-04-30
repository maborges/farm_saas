"""
Testes para FIFO (First In, First Out) deduction de estoque.

Valida:
1. Deductão em ordem FIFO (lotes mais antigos primeiro)
2. Múltiplos lotes consumidos em uma operação
3. Cálculo de custo baseado em custo_unitario histórico (não preço médio)
4. Isolamento de tenant
5. Erro quando estoque insuficiente
"""

import pytest
from uuid import uuid4
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from operacional.models.estoque import LoteEstoque, Deposito
from operacional.services.estoque_fifo import consumir_lotes_fifo
from core.cadastros.produtos.models import Produto
from core.exceptions import BusinessRuleError


async def criar_produto(session: AsyncSession, tenant_id, nome: str = "Produto FIFO") -> Produto:
    produto = Produto(
        id=uuid4(),
        tenant_id=tenant_id,
        nome=nome,
        tipo="INSUMO",
        unidade_medida="KG",
        preco_medio=0.0,
        ativo=True,
    )
    session.add(produto)
    await session.flush()
    return produto


class TestFIFODeduction:
    """Testes de deductão FIFO de estoque."""

    @pytest.mark.asyncio
    async def test_fifo_consome_lote_mais_antigo_primeiro(
        self,
        session: AsyncSession,
        tenant_id: str,
        unidade_produtiva_id: str,
    ):
        """FIFO deve consumir lotes na ordem de data_fabricacao (ASC)."""
        # Setup: Criar 3 lotes com datas diferentes
        produto = await criar_produto(session, tenant_id, "Produto FIFO 1")
        deposito = Deposito(
            id=uuid4(),
            tenant_id=tenant_id,
            unidade_produtiva_id=unidade_produtiva_id,
            nome="Galpão A",
            tipo="GERAL",
            ativo=True,
        )
        session.add(deposito)
        await session.flush()

        # Lote 1: MAIS ANTIGO (2026-01-01)
        lote1 = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote="LOTE001",
            data_fabricacao=date(2026, 1, 1),
            data_validade=date(2027, 1, 1),
            quantidade_inicial=500.0,
            quantidade_atual=500.0,
            custo_unitario=10.0,  # Custo antigo
            status="ATIVO",
        )

        # Lote 2: Intermediário (2026-02-01)
        lote2 = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote="LOTE002",
            data_fabricacao=date(2026, 2, 1),
            data_validade=date(2027, 2, 1),
            quantidade_inicial=300.0,
            quantidade_atual=300.0,
            custo_unitario=12.0,  # Custo intermediário
            status="ATIVO",
        )

        # Lote 3: MAIS NOVO (2026-03-01)
        lote3 = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote="LOTE003",
            data_fabricacao=date(2026, 3, 1),
            data_validade=date(2027, 3, 1),
            quantidade_inicial=200.0,
            quantidade_atual=200.0,
            custo_unitario=15.0,  # Custo mais recente
            status="ATIVO",
        )

        session.add_all([lote1, lote2, lote3])
        await session.commit()

        # Act: Consumir 700 unidades (FIFO)
        consumo = await consumir_lotes_fifo(
            session=session,
            produto_id=produto.id,
            quantidade_necessaria=700.0,
            deposito_id=deposito.id,
            tenant_id=tenant_id,
        )

        # Assert: Deve consumir na ordem FIFO
        assert len(consumo.lotes_consumidos) == 2
        assert consumo.quantidade_consumida == 700.0

        # Lote 1 (mais antigo) deve ser consumido totalmente (500)
        assert consumo.lotes_consumidos[0]["lote_id"] == lote1.id
        assert consumo.lotes_consumidos[0]["quantidade"] == 500.0
        assert consumo.lotes_consumidos[0]["custo"] == 5000.0  # 500 × 10

        # Lote 2 deve ter 200 consumidas
        assert consumo.lotes_consumidos[1]["lote_id"] == lote2.id
        assert consumo.lotes_consumidos[1]["quantidade"] == 200.0
        assert consumo.lotes_consumidos[1]["custo"] == 2400.0  # 200 × 12

        # Lote 3 não deve ser consumido (ainda há estoque em lote2)
        # Custo total = 5000 + 2400 = 7400
        assert consumo.custo_total == 7400.0

    @pytest.mark.asyncio
    async def test_fifo_custo_historico_nao_preco_medio(
        self,
        session: AsyncSession,
        tenant_id: str,
        unidade_produtiva_id: str,
    ):
        """FIFO deve usar custo_unitario do lote (histórico), não preco_medio do produto."""
        produto = await criar_produto(session, tenant_id, "Produto FIFO 2")
        deposito = Deposito(
            id=uuid4(),
            tenant_id=tenant_id,
            unidade_produtiva_id=unidade_produtiva_id,
            nome="Galpão",
            tipo="GERAL",
            ativo=True,
        )
        session.add(deposito)
        await session.flush()

        # Lote antigo com custo baixo
        lote = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote="LOTE_ANTIGO",
            data_fabricacao=date(2025, 1, 1),
            quantidade_inicial=100.0,
            quantidade_atual=100.0,
            custo_unitario=5.0,  # Custo antigo baixo
            status="ATIVO",
        )
        session.add(lote)
        await session.commit()

        # Act
        consumo = await consumir_lotes_fifo(
            session=session,
            produto_id=produto.id,
            quantidade_necessaria=100.0,
            deposito_id=deposito.id,
            tenant_id=tenant_id,
        )

        # Assert: Custo deve ser 5.0 × 100 = 500, não preco_medio
        assert consumo.lotes_consumidos[0]["custo_unitario"] == 5.0
        assert consumo.custo_total == 500.0

    @pytest.mark.asyncio
    async def test_fifo_erro_estoque_insuficiente(
        self,
        session: AsyncSession,
        tenant_id: str,
        unidade_produtiva_id: str,
    ):
        """FIFO deve falhar com erro claro quando estoque insuficiente."""
        produto = await criar_produto(session, tenant_id, "Produto FIFO 3")
        deposito = Deposito(
            id=uuid4(),
            tenant_id=tenant_id,
            unidade_produtiva_id=unidade_produtiva_id,
            nome="Galpão",
            tipo="GERAL",
            ativo=True,
        )
        session.add(deposito)
        await session.flush()

        # Lote com apenas 50 unidades
        lote = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote="LOTE001",
            quantidade_inicial=50.0,
            quantidade_atual=50.0,
            custo_unitario=10.0,
            status="ATIVO",
        )
        session.add(lote)
        await session.commit()

        # Act & Assert: Tentar consumir 100 deve falhar
        with pytest.raises(BusinessRuleError) as exc_info:
            await consumir_lotes_fifo(
                session=session,
                produto_id=produto.id,
                quantidade_necessaria=100.0,
                deposito_id=deposito.id,
                tenant_id=tenant_id,
            )

        assert "Saldo insuficiente" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fifo_exato_all_lotes_consumidos(
        self,
        session: AsyncSession,
        tenant_id: str,
        unidade_produtiva_id: str,
    ):
        """FIFO com quantidade exata que consome todos os lotes."""
        produto = await criar_produto(session, tenant_id, "Produto FIFO 4")
        deposito = Deposito(
            id=uuid4(),
            tenant_id=tenant_id,
            unidade_produtiva_id=unidade_produtiva_id,
            nome="Galpão",
            tipo="GERAL",
            ativo=True,
        )
        session.add(deposito)
        await session.flush()

        # 2 lotes: 300 + 200 = 500 total
        lote1 = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote="L1",
            data_fabricacao=date(2026, 1, 1),
            quantidade_inicial=300.0,
            quantidade_atual=300.0,
            custo_unitario=10.0,
            status="ATIVO",
        )
        lote2 = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote="L2",
            data_fabricacao=date(2026, 2, 1),
            quantidade_inicial=200.0,
            quantidade_atual=200.0,
            custo_unitario=12.0,
            status="ATIVO",
        )
        session.add_all([lote1, lote2])
        await session.commit()

        # Act: Consumir exatamente 500
        consumo = await consumir_lotes_fifo(
            session=session,
            produto_id=produto.id,
            quantidade_necessaria=500.0,
            deposito_id=deposito.id,
            tenant_id=tenant_id,
        )

        # Assert
        assert consumo.quantidade_consumida == 500.0
        assert len(consumo.lotes_consumidos) == 2
        assert consumo.lotes_consumidos[0]["quantidade"] == 300.0
        assert consumo.lotes_consumidos[1]["quantidade"] == 200.0
        # Custo = (300 × 10) + (200 × 12) = 3000 + 2400 = 5400
        assert consumo.custo_total == 5400.0

    @pytest.mark.asyncio
    async def test_fifo_lote_status_esgotado(
        self,
        session: AsyncSession,
        tenant_id: str,
        unidade_produtiva_id: str,
    ):
        """FIFO deve marcar lote como ESGOTADO quando quantidade_atual = 0."""
        produto = await criar_produto(session, tenant_id, "Produto FIFO 5")
        deposito = Deposito(
            id=uuid4(),
            tenant_id=tenant_id,
            unidade_produtiva_id=unidade_produtiva_id,
            nome="Galpão",
            tipo="GERAL",
            ativo=True,
        )
        session.add(deposito)
        await session.flush()

        lote = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=deposito.id,
            numero_lote="LOTE",
            quantidade_inicial=100.0,
            quantidade_atual=100.0,
            custo_unitario=10.0,
            status="ATIVO",
        )
        session.add(lote)
        await session.commit()

        # Act: Consumir tudo
        await consumir_lotes_fifo(
            session=session,
            produto_id=produto.id,
            quantidade_necessaria=100.0,
            deposito_id=deposito.id,
            tenant_id=tenant_id,
        )

        # Assert: Lote deve estar ESGOTADO
        await session.refresh(lote)
        assert lote.status == "ESGOTADO"
        assert lote.quantidade_atual == 0.0

    @pytest.mark.asyncio
    async def test_fifo_sem_deposito_especifico(
        self,
        session: AsyncSession,
        tenant_id: str,
        unidade_produtiva_id: str,
    ):
        """FIFO sem deposito_id deve buscar em todos os depósitos da fazenda."""
        produto = await criar_produto(session, tenant_id, "Produto FIFO 6")

        # 2 depósitos
        dep1 = Deposito(
            id=uuid4(),
            tenant_id=tenant_id,
            unidade_produtiva_id=unidade_produtiva_id,
            nome="Galpão A",
            tipo="GERAL",
            ativo=True,
        )
        dep2 = Deposito(
            id=uuid4(),
            tenant_id=tenant_id,
            unidade_produtiva_id=unidade_produtiva_id,
            nome="Galpão B",
            tipo="GERAL",
            ativo=True,
        )
        session.add_all([dep1, dep2])
        await session.flush()

        # Lote em dep1
        lote1 = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=dep1.id,
            numero_lote="L1",
            data_fabricacao=date(2026, 1, 1),
            quantidade_inicial=100.0,
            quantidade_atual=100.0,
            custo_unitario=10.0,
            status="ATIVO",
        )
        # Lote em dep2
        lote2 = LoteEstoque(
            id=uuid4(),
            produto_id=produto.id,
            deposito_id=dep2.id,
            numero_lote="L2",
            data_fabricacao=date(2026, 2, 1),
            quantidade_inicial=50.0,
            quantidade_atual=50.0,
            custo_unitario=12.0,
            status="ATIVO",
        )
        session.add_all([lote1, lote2])
        await session.commit()

        # Act: Consumir sem especificar deposito
        consumo = await consumir_lotes_fifo(
            session=session,
            produto_id=produto.id,
            quantidade_necessaria=120.0,
            deposito_id=None,  # Busca em todos
            tenant_id=tenant_id,
        )

        # Assert: Deve consumir de ambos os depósitos (FIFO)
        assert consumo.quantidade_consumida == 120.0
        assert len(consumo.lotes_consumidos) == 2
        # L1 (mais antigo): 100 unidades
        # L2 (mais novo): 20 unidades
        assert consumo.lotes_consumidos[0]["quantidade"] == 100.0
        assert consumo.lotes_consumidos[1]["quantidade"] == 20.0
