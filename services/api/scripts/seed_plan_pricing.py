"""
Seed de dados iniciais para pricing de planos e configurações do SaaS.

Cria:
1. Configurações globais (dias_bloqueio, etc.)
2. Matriz de pricing para planos existentes

Uso:
    python scripts/seed_plan_pricing.py
"""
import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from sqlalchemy import select
from core.database import async_session_maker
from core.models.billing import PlanoAssinatura
from core.models.configuration import ConfiguracaoSaaS
from core.services.plan_pricing_service import PlanoPricingService


async def seed_configuracoes_saas():
    """Cria configurações globais do SaaS."""
    logger.info("=== Seeding configurações do SaaS ===")

    configuracoes = [
        {
            "chave": "dias_bloqueio_inadimplencia",
            "valor": {"dias": 5},
            "descricao": "Dias de tolerância para pagamento antes de bloquear tenant por inadimplência"
        },
        {
            "chave": "dias_vencimento_upgrade",
            "valor": {"dias": 3},
            "descricao": "Dias até vencimento de cobrança de upgrade de plano"
        },
        {
            "chave": "asaas_modo_sandbox",
            "valor": {"ativo": True},
            "descricao": "Usar ambiente sandbox do Asaas (desenvolvimento)"
        },
        {
            "chave": "notificacoes_upgrade",
            "valor": {"email": True, "sms": False, "whatsapp": False},
            "descricao": "Canais de notificação para upgrades de plano"
        }
    ]

    async with async_session_maker() as session:
        for config_data in configuracoes:
            # Verificar se já existe
            stmt = select(ConfiguracaoSaaS).where(ConfiguracaoSaaS.chave == config_data["chave"])
            result = await session.execute(stmt)
            existe = result.scalar_one_or_none()

            if existe:
                logger.info(f"Configuração '{config_data['chave']}' já existe, pulando...")
                continue

            # Criar
            config = ConfiguracaoSaaS(
                chave=config_data["chave"],
                valor=config_data["valor"],
                descricao=config_data["descricao"],
                ativo=True
            )

            session.add(config)
            logger.info(f"✓ Criada configuração: {config_data['chave']}")

        await session.commit()

    logger.info("Configurações do SaaS criadas com sucesso\n")


async def seed_pricing_exemplo():
    """
    Cria matriz de pricing exemplo para planos existentes.

    IMPORTANTE: Adapte os valores para sua realidade de negócio!
    """
    logger.info("=== Seeding pricing de planos ===")

    # Definir pricing exemplo por plano
    pricing_config = {
        "Básico": [
            {"faixa_inicio": 1, "faixa_fim": 5, "mensal": Decimal("30.00"), "anual": Decimal("300.00")},
            {"faixa_inicio": 6, "faixa_fim": 10, "mensal": Decimal("25.00"), "anual": Decimal("250.00")},
        ],
        "Pro": [
            {"faixa_inicio": 1, "faixa_fim": 10, "mensal": Decimal("40.00"), "anual": Decimal("400.00")},
            {"faixa_inicio": 11, "faixa_fim": 30, "mensal": Decimal("35.00"), "anual": Decimal("350.00")},
            {"faixa_inicio": 31, "faixa_fim": 50, "mensal": Decimal("30.00"), "anual": Decimal("300.00")},
        ],
        "Enterprise": [
            {"faixa_inicio": 1, "faixa_fim": 10, "mensal": Decimal("50.00"), "anual": Decimal("500.00")},
            {"faixa_inicio": 11, "faixa_fim": 50, "mensal": Decimal("45.00"), "anual": Decimal("450.00")},
            {"faixa_inicio": 51, "faixa_fim": 100, "mensal": Decimal("40.00"), "anual": Decimal("400.00")},
            {"faixa_inicio": 101, "faixa_fim": None, "mensal": Decimal("35.00"), "anual": Decimal("350.00")},  # Ilimitado
        ]
    }

    async with async_session_maker() as session:
        pricing_service = PlanoPricingService(session)

        # Buscar planos
        stmt = select(PlanoAssinatura).where(PlanoAssinatura.ativo == True)
        result = await session.execute(stmt)
        planos = result.scalars().all()

        if not planos:
            logger.warning("Nenhum plano encontrado! Execute seed_plans.py primeiro.")
            return

        for plano in planos:
            logger.info(f"\nProcessando plano: {plano.nome}")

            # Verificar se já tem pricing
            faixas_existentes = await pricing_service.obter_faixas_plano(plano.id)
            if faixas_existentes:
                logger.info(f"  Plano '{plano.nome}' já possui {len(faixas_existentes)} faixas de pricing, pulando...")
                continue

            # Buscar configuração de pricing para este plano
            config_plano = pricing_config.get(plano.nome)

            if not config_plano:
                logger.warning(f"  Sem configuração de pricing para '{plano.nome}', usando padrão básico...")
                config_plano = [
                    {"faixa_inicio": 1, "faixa_fim": None, "mensal": Decimal("50.00"), "anual": Decimal("500.00")}
                ]

            # Criar faixas
            for faixa in config_plano:
                try:
                    await pricing_service.criar_faixa_pricing(
                        plano_id=plano.id,
                        faixa_inicio=faixa["faixa_inicio"],
                        faixa_fim=faixa["faixa_fim"],
                        preco_mensal=faixa["mensal"],
                        preco_anual=faixa["anual"]
                    )

                    faixa_desc = f"{faixa['faixa_inicio']}-{faixa['faixa_fim'] or '∞'}"
                    logger.info(
                        f"  ✓ Faixa {faixa_desc}: "
                        f"R$ {faixa['mensal']}/user (mensal), "
                        f"R$ {faixa['anual']}/user (anual)"
                    )

                except Exception as e:
                    logger.error(f"  ✗ Erro ao criar faixa: {e}")

        # Atualizar limites de usuários nos planos
        logger.info("\n=== Atualizando limites de usuários nos planos ===")

        limites_planos = {
            "Básico": {"minimo": 1, "maximo": 10},
            "Pro": {"minimo": 1, "maximo": 50},
            "Enterprise": {"minimo": 1, "maximo": None},  # Ilimitado
        }

        for plano in planos:
            limites = limites_planos.get(plano.nome)
            if limites:
                plano.limite_usuarios_minimo = limites["minimo"]
                plano.limite_usuarios_maximo = limites["maximo"]
                logger.info(
                    f"✓ Plano '{plano.nome}': "
                    f"{limites['minimo']}-{limites['maximo'] or '∞'} usuários"
                )

        await session.commit()

    logger.info("\nPricing de planos criado com sucesso\n")


async def main():
    """Executa todos os seeds."""
    logger.info("### SEED: Pricing e Configurações de Planos ###\n")

    try:
        # 1. Configurações globais
        await seed_configuracoes_saas()

        # 2. Pricing dos planos
        await seed_pricing_exemplo()

        logger.info("=== Seed concluído com sucesso! ===")
        logger.info("\n⚠️  IMPORTANTE: Revise os valores de pricing em produção!")
        logger.info("Os valores são exemplos e devem ser ajustados para sua realidade de negócio.\n")

        return True

    except Exception as e:
        logger.error(f"Erro ao executar seed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    # Configurar logger
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
        level="INFO"
    )

    # Executar seed
    sucesso = asyncio.run(main())
    sys.exit(0 if sucesso else 1)
