import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config, create_async_engine

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

import os
import sys
from sqlalchemy import text

# Adiciona o diretório da API no PYTHONPATH do Alembic
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.database import Base, DB_URL
from core.models import (
    Tenant, Fazenda, Usuario, PerfilAcesso, TenantUsuario, FazendaUsuario,
    ConviteAcesso, PlanoAssinatura, AssinaturaTenant, Fatura, ChamadoSuporte,
    MensagemChamado, ConhecimentoCategoria, ConhecimentoArtigo, ConfiguracaoSaaS,
    ConfiguracaoTenant, AdminUser, Cupom, EmailTemplate, EmailLog, AdminAuditLog,
    PlanoPricing, MudancaPlano, CobrancaAsaas, HistoricoBloqueio
)
from agricola.talhoes.models import Talhao
from agricola.safras.models import Safra
from agricola.operacoes.models import OperacaoAgricola, InsumoOperacao
from agricola.monitoramento.models import MonitoramentoPragas
from agricola.romaneios.models import RomaneioColheita
from agricola.previsoes.models import PrevisaoProdutividade
from agricola.cadastros.models import Cultura
from agricola.a1_planejamento.models import ItemOrcamentoSafra

# Pecuaria
from pecuaria.models.piquete import Piquete
from pecuaria.models.lote import LoteBovino
from pecuaria.models.manejo import ManejoLote

# Pessoas
from pessoas.models import Pessoa

# Financeiro
from financeiro.models.plano_conta import PlanoConta
from financeiro.models.despesa import Despesa
from financeiro.models.rateio import Rateio

# add your model's MetaData object here
target_metadata = Base.metadata

# Set URL correctly - escape % for ConfigParser
# ConfigParser interprets % as interpolation, so we need to double it
config.set_main_option("sqlalchemy.url", DB_URL.replace("%", "%%"))

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    # Define search_path ao nível de sessão (antes de qualquer transação)
    # para que todas as operações — incluindo UPDATE alembic_version — usem
    # o schema "farms" sem precisar de qualificação explícita.
    if "postgresql" in DB_URL:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS farms"))
        connection.execute(text("SET search_path TO farms"))

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # async_engine_from_config não repassa connect_args corretamente para asyncpg.
    # Usamos create_async_engine diretamente com server_settings para garantir
    # que search_path='farms' persista em TODAS as execuções da sessão.
    engine_kwargs: dict = {"poolclass": pool.NullPool}
    if "postgresql" in DB_URL:
        engine_kwargs["connect_args"] = {"server_settings": {"search_path": "farms"}}

    connectable = create_async_engine(DB_URL, **engine_kwargs)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
        await connection.commit()

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
