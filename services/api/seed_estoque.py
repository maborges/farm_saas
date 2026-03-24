import asyncio
import uuid
from core.database import async_session_maker
from core.models.tenant import Tenant
from core.models.fazenda import Fazenda
from operacional.models.estoque import Deposito, SaldoEstoque
from core.cadastros.models import ProdutoCatalogo
from sqlalchemy.future import select

async def seed():
    async with async_session_maker() as session:
        # IDs obtidos da base anteriormente
        tenant_id = uuid.UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")
        fazenda_id = uuid.UUID("e10b4290-7d71-4828-b80c-7b243ebd9e2f")

        print("Verificando se já existem dados de estoque...")
        stmt = select(Deposito).where(Deposito.tenant_id == tenant_id)
        existing_dep = (await session.execute(stmt)).scalar()
        if existing_dep:
            print("Dados de estoque já existentes. Pulando seed.")
            return

        print("Populando Estoque...")

        # 1. Categoria
        cat = CategoriaProduto(id=uuid.uuid4(), tenant_id=tenant_id, nome="Insumos Agrícolas")
        session.add(cat)
        await session.flush()

        # 2. Depósito
        dep = Deposito(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            fazenda_id=fazenda_id,
            nome="Galpão de Defensivos Central",
            tipo="DEFENSIVOS"
        )
        session.add(dep)
        await session.flush()

        # 3. Produtos
        p1 = Produto(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            categoria_id=cat.id,
            nome="Glifosato 480",
            unidade_medida="L",
            preco_medio=45.50
        )
        p2 = Produto(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            categoria_id=cat.id,
            nome="Fertilizante NPK 04-14-08",
            unidade_medida="KG",
            preco_medio=3.20
        )
        session.add_all([p1, p2])
        await session.flush()

        # 4. Saldos Iniciais
        s1 = SaldoEstoque(deposito_id=dep.id, produto_id=p1.id, quantidade_atual=5000.0)
        s2 = SaldoEstoque(deposito_id=dep.id, produto_id=p2.id, quantidade_atual=25000.0)
        session.add_all([s1, s2])

        await session.commit()
        print(f"Sucesso! 'Galpão de Defensivos Central' criado com {p1.nome} e {p2.nome}.")

if __name__ == "__main__":
    asyncio.run(seed())
