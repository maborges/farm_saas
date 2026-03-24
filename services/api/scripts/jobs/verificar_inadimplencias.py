"""
Job agendado para verificar inadimplências e aplicar mudanças de plano.

Este script deve ser executado diariamente via cron ou scheduler.

Uso:
    python scripts/jobs/verificar_inadimplencias.py

Cron sugerido (todos os dias às 3h da manhã):
    0 3 * * * cd /path/to/api && /path/to/.venv/bin/python scripts/jobs/verificar_inadimplencias.py
"""
import asyncio
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from loguru import logger
from core.database import async_session_maker
from core.services.mudanca_plano_service import MudancaPlanoService


async def verificar_inadimplencias():
    """Verifica e bloqueia tenants inadimplentes."""
    logger.info("=== Iniciando verificação de inadimplências ===")

    async with async_session_maker() as session:
        service = MudancaPlanoService(session, tenant_id=None)

        try:
            # Verificar inadimplências
            tenants_bloqueados = await service.verificar_inadimplencias()

            if tenants_bloqueados:
                logger.warning(
                    f"Bloqueados {len(tenants_bloqueados)} tenants por inadimplência: "
                    f"{tenants_bloqueados}"
                )
            else:
                logger.info("Nenhum tenant inadimplente encontrado")

            return tenants_bloqueados

        except Exception as e:
            logger.error(f"Erro ao verificar inadimplências: {e}", exc_info=True)
            raise


async def aplicar_mudancas_agendadas():
    """Aplica mudanças de plano agendadas (downgrades)."""
    logger.info("=== Iniciando aplicação de mudanças agendadas ===")

    async with async_session_maker() as session:
        service = MudancaPlanoService(session, tenant_id=None)

        try:
            # Aplicar mudanças agendadas
            mudancas_aplicadas = await service.aplicar_mudancas_agendadas()

            if mudancas_aplicadas:
                logger.info(
                    f"Aplicadas {len(mudancas_aplicadas)} mudanças agendadas"
                )
                for mudanca in mudancas_aplicadas:
                    logger.info(
                        f"  - Mudança {mudanca.id}: Tenant {mudanca.tenant_id} "
                        f"({mudanca.tipo_mudanca})"
                    )
            else:
                logger.info("Nenhuma mudança agendada para aplicar hoje")

            return mudancas_aplicadas

        except Exception as e:
            logger.error(f"Erro ao aplicar mudanças agendadas: {e}", exc_info=True)
            raise


async def main():
    """Executa todos os jobs."""
    logger.info("### JOB: Verificação de Inadimplências e Mudanças de Plano ###")

    try:
        # 1. Aplicar mudanças agendadas (downgrades)
        mudancas = await aplicar_mudancas_agendadas()

        # 2. Verificar inadimplências
        bloqueados = await verificar_inadimplencias()

        # Resumo
        logger.info("=== Resumo da execução ===")
        logger.info(f"Mudanças aplicadas: {len(mudancas)}")
        logger.info(f"Tenants bloqueados: {len(bloqueados)}")
        logger.info("Job concluído com sucesso")

        return {
            "mudancas_aplicadas": len(mudancas),
            "tenants_bloqueados": len(bloqueados),
            "sucesso": True
        }

    except Exception as e:
        logger.error(f"Falha na execução do job: {e}", exc_info=True)
        return {
            "sucesso": False,
            "erro": str(e)
        }


if __name__ == "__main__":
    # Configurar logger
    logger.remove()  # Remove handler padrão
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO"
    )
    logger.add(
        "logs/jobs/inadimplencias_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="1 day",
        retention="30 days",
        level="INFO"
    )

    # Executar job
    resultado = asyncio.run(main())

    # Exit code para cron
    sys.exit(0 if resultado.get("sucesso") else 1)
