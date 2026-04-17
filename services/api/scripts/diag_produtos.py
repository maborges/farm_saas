"""
Diagnóstico: verifica produtos no banco e tenants
"""
import asyncio
from sqlalchemy import select, func
from core.database import async_session_maker
import core.models  # noqa: F401
from core.models.tenant import Tenant
from core.cadastros.produtos.models import Produto

async def run():
    async with async_session_maker() as session:
        # Tenants
        tenants = (await session.execute(select(Tenant))).scalars().all()
        print(f"\n=== TENANTS ({len(tenants)}) ===")
        for t in tenants:
            print(f"  ID: {t.id} | Nome: {getattr(t, 'nome', getattr(t, 'razao_social', 'N/A'))}")
        
        # Produtos por tenant
        print(f"\n=== PRODUTOS POR TENANT ===")
        stmt = select(Produto.tenant_id, func.count(Produto.id)).group_by(Produto.tenant_id)
        rows = (await session.execute(stmt)).all()
        for tenant_id, count in rows:
            print(f"  Tenant {tenant_id}: {count} produtos")
        
        # Detalhe: todos produtos com tenant_id e ativo
        print(f"\n=== DETALHE DOS PRODUTOS (primeiros 10) ===")
        stmt = select(Produto).limit(10).order_by(Produto.created_at.desc())
        produtos = (await session.execute(stmt)).scalars().all()
        for p in produtos:
            print(f"  [{p.tenant_id}] {p.nome} | ativo={p.ativo} | tipo={p.tipo} | codigo={p.codigo_interno}")
        
        # Total
        total = (await session.execute(select(func.count(Produto.id)))).scalar()
        print(f"\nTotal de produtos: {total}")

if __name__ == "__main__":
    asyncio.run(run())
