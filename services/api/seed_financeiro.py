import asyncio
import uuid
from sqlalchemy.future import select
from core.database import async_session_maker, engine
from financeiro.models.plano_conta import PlanoConta
from core.models.tenant import Tenant

async def seed_financeiro():
    async with async_session_maker() as session:
        # Busca o primeiro tenant pra associar (ajuste se quiser tenant especifico)
        stmt_tenant = select(Tenant)
        tenant = (await session.execute(stmt_tenant)).scalars().first()
        if not tenant:
            print("Nenhum tenant encontrado. Crie um tenant primeiro.")
            return

        planos = [
            # RECEITAS
            {"codigo": "1.01", "nome": "Venda de Grãos", "tipo": "RECEITA"},
            {"codigo": "1.02", "nome": "Venda de Animais", "tipo": "RECEITA"},
            {"codigo": "1.03", "nome": "Prestação de Serviços", "tipo": "RECEITA"},
            
            # DESPESAS
            {"codigo": "2.01", "nome": "Insumos (Sementes/Adubo)", "tipo": "DESPESA"},
            {"codigo": "2.02", "nome": "Defensivos Agrícolas", "tipo": "DESPESA"},
            {"codigo": "2.03", "nome": "Combustíveis e Lubrificantes", "tipo": "DESPESA"},
            {"codigo": "2.04", "nome": "Mão de Obra / Salários", "tipo": "DESPESA"},
            {"codigo": "2.05", "nome": "Manutenção de Máquinas", "tipo": "DESPESA"},
            {"codigo": "2.06", "nome": "Energia Elétrica / Água", "tipo": "DESPESA"},
            {"codigo": "2.07", "nome": "Arrendamentos", "tipo": "DESPESA"},
        ]

        for p_data in planos:
            # Verifica se já existe
            stmt = select(PlanoConta).where(
                PlanoConta.tenant_id == tenant.id,
                PlanoConta.codigo == p_data["codigo"]
            )
            exists = (await session.execute(stmt)).scalars().first()
            
            if not exists:
                p = PlanoConta(**p_data, tenant_id=tenant.id)
                session.add(p)
                print(f"Semeado: {p_data['nome']}")
        
        await session.commit()
        print("Plano de Contas básico semeado!")

if __name__ == "__main__":
    asyncio.run(seed_financeiro())
