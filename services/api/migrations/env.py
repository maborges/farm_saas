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
from rh.models import ColaboradorRH, LancamentoDiaria, Empreitada
from core.models import (
    Tenant, Fazenda, Usuario, PerfilAcesso, TenantUsuario, FazendaUsuario,
    ConviteAcesso, PlanoAssinatura, AssinaturaTenant, Fatura, ChamadoSuporte,
    MensagemChamado, ConhecimentoCategoria, ConhecimentoArtigo, ConfiguracaoSaaS,
    ConfiguracaoTenant, AdminUser, Cupom, EmailTemplate, EmailLog, AdminAuditLog,
    PlanoPricing, MudancaPlano, CobrancaAsaas, HistoricoBloqueio
)
from agricola.safras.models import Safra, SafraTalhao, SafraFaseHistorico
from agricola.cultivos.models import Cultivo, CultivoArea
from agricola.operacoes.models import OperacaoAgricola, InsumoOperacao
from agricola.monitoramento.models import MonitoramentoPragas
from agricola.monitoramento.catalogo_model import MonitoramentoCatalogo
from agricola.analises_solo.models import AnaliseSolo, RegraAgronomica
from agricola.tarefas.models import SafraTarefa
from agricola.checklist.models import ChecklistTemplate, SafraChecklistItem
from agricola.models.templates import (
    PhaseTemplate, PhaseTemplateChecklistItem, PhaseTemplateTask,
    PhaseGateRule, OperationTemplate, OperationTemplateItem, OperationDependency
)
from agricola.fenologia.models import FenologiaEscala, SafraTalhaoGrupo, SafraTalhaoGrupoItem, SafraFenologiaRegistro
from agricola.romaneios.models import RomaneioColheita
from agricola.beneficiamento.models import LoteBeneficiamento
from agricola.previsoes.models import PrevisaoProdutividade
# Outras sub-áreas Agrícola
from agricola.ndvi.models import ImagemNDVI
from agricola.climatico.models import RegistroClima
from agricola.rastreabilidade.models import LoteRastreabilidade, CertificacaoPropriedade
from agricola.agronomo.models import ConversaAgronomo, RelatorioTecnico
from agricola.cadastros.models import Cultura
from agricola.caderno.models import CadernoCampoEntrada, CadernoCampoFoto, VisitaTecnica, EPIEntrega, CadernoExportacao
from agricola.colheita.models import ProdutoColhido

# Cultura migrada para cadastros/produtos (verificar redundância)
from agricola.a1_planejamento.models import ItemOrcamentoSafra

# Pecuaria
from pecuaria.animal.models import LoteAnimal, Animal, EventoAnimal
from pecuaria.producao.models import ProducaoLeite
from pecuaria.models.manejo import ManejoLote

# Pessoas (migrado para core.cadastros.pessoas)
from core.cadastros.pessoas.models import (
    Pessoa, PessoaDocumento, PessoaContato, PessoaEndereco, PessoaBancario,
    TipoRelacionamento, PessoaRelacionamento, PessoaConsentimento, PessoaAcessoLog,
)

# Propriedades / Áreas Rurais
from core.cadastros.propriedades.models import AreaRural, MatriculaImovel, RegistroAmbiental, TipoSolo, TipoIrrigacao
from core.cadastros.propriedades.propriedade_models import Propriedade, ExploracaoRural, DocumentoExploracao

# Equipamentos
from core.cadastros.equipamentos.models import Equipamento
from operacional.models.apontamento import ApontamentoUso
from operacional.models.abastecimento import Abastecimento
from operacional.models.checklist import ChecklistModelo, ChecklistRealizado
from operacional.models.documento_equipamento import DocumentoEquipamento

# Produtos (insumos / almoxarifado)
from core.cadastros.produtos.models import (
    Produto, ProdutoAgricola, ProdutoEstoque, ProdutoEPI, ProdutoCultura,
)

# Commodities (produtos de saída / receita)
from core.cadastros.commodities.models import Commodity

# Financeiro
from financeiro.models.plano_conta import PlanoConta
from financeiro.models.despesa import Despesa
from financeiro.models.receita import Receita
from financeiro.models.rateio import Rateio
from financeiro.comercializacao.models import ComercializacaoCommodity

# IA Diagnóstico
from ia_diagnostico.models import PragasDoencas, Tratamentos, Diagnosticos, Recomendacoes, ModelosMl

# IoT Integração
from iot_integracao.models import JohnDeere, CaseIh, Whatsapp, ComparadorPrecos

# Imóveis Rurais
from imoveis.models.imovel import (
    ImovelRural, Cartorio, MatriculaImovelRural, Benfeitoria,
    DocumentoLegal, HistoricoDocumento,
    ContratoArrendamento, ParcelaArrendamento, HistoricoReajuste
)

# Ambiental (CAR, Alertas, Outorgas)
from ambiental.models import RegistroCAR, AlertaAmbiental, OutorgaHidrica

# Notificações
from notificacoes.models import Notificacao

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


def include_object(object, name, type_, reflected, compare_to):
    """Exclude known constraints that cannot be auto-applied due to data issues."""
    if type_ == "unique_constraint" and name == "uq_produto_tenant_codigo_interno":
        return False
    return True


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
        include_object=include_object,
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
