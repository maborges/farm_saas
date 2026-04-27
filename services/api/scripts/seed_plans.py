import asyncio
import uuid
import sys
import os

# Adicionar o diretório base para que 'core' seja visível
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from core.database import async_session_maker
from core.models.billing import PlanoAssinatura

async def seed_plans():
    async with async_session_maker() as session:
        # Verificar se já existem planos
        result = await session.execute(select(PlanoAssinatura))
        if result.scalars().first():
            print("Planos já existem no banco de dados.")
            return

        planos = [
            PlanoAssinatura(
                nome="Bronze (Essencial)",
                descricao="Ideal para pequenos produtores começando a digitalização. Inclui gestão financeira básica e acesso a 1 fazenda.",
                modulos_inclusos=["CORE", "F1_TESOURARIA"],
                limite_usuarios_minimo=1,
                limite_usuarios_maximo=2,
                limite_hectares=100.0,
                preco_mensal=199.90,
                preco_anual=1990.00,
                ativo=True,
                is_default=False
            ),
            PlanoAssinatura(
                nome="Prata (Profissional)",
                descricao="Controle completo da lavoura e finanças. Gestão de estoque, máquinas e apontamentos de campo.",
                modulos_inclusos=["CORE", "F1_TESOURARIA", "A1_PLANEJAMENTO", "O2_ESTOQUE"],
                limite_usuarios_minimo=1,
                limite_usuarios_maximo=5,
                limite_hectares=1000.0,
                preco_mensal=499.90,
                preco_anual=4990.00,
                ativo=True,
                is_default=True  # Plano padrão para onboarding
            ),
            PlanoAssinatura(
                nome="Ouro (Empresarial)",
                descricao="A solução definitiva. Integra rebanho, lavoura, agronomia avançada e suporte prioritário.",
                modulos_inclusos=[
                    "CORE",
                    "F1_TESOURARIA",
                    "A1_PLANEJAMENTO",
                    "O1_FROTA",
                    "O2_ESTOQUE",
                    "P1_REBANHO",
                    "A2_CAMPO",
                ],
                limite_usuarios_minimo=1,
                limite_usuarios_maximo=20,
                limite_hectares=None, # Ilimitado
                preco_mensal=999.90,
                preco_anual=9990.00,
                ativo=True,
                is_default=False
            )
        ]

        session.add_all(planos)
        await session.commit()
        print(f"Sucesso: {len(planos)} planos comerciais criados!")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    asyncio.run(seed_plans())
