import pytest
import asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import MetaData, Table, text
from core.database import Base
from core.models import Tenant, Fazenda

# Dois Tenants globais para guerra de isolamento nos testes
TENANT_A_ID = uuid.uuid4()
TENANT_B_ID = uuid.uuid4()

@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()

@pytest.fixture
async def engine_memory():
    # Use SQLite em-memória para testes (ultrarrápido, sem JSONB que SQLite não suporta)
    from sqlalchemy import create_engine, event
    from sqlalchemy.pool import StaticPool

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as conn:
        # Criar apenas tabelas simples (sem JSONB)
        # Usa raw SQL para evitar JSONB do SafraFaseHistorico
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tenants (
                id CHAR(32) PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                ativo BOOLEAN DEFAULT 1
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cadastros_areas_rurais (
                id CHAR(32) PRIMARY KEY,
                tenant_id CHAR(32) NOT NULL,
                nome VARCHAR(255),
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS safras (
                id CHAR(32) PRIMARY KEY,
                tenant_id CHAR(32) NOT NULL,
                talhao_id CHAR(32) NOT NULL,
                ano_safra VARCHAR(10),
                cultura VARCHAR(50),
                cultivar_id CHAR(32),
                cultivar_nome VARCHAR(100),
                commodity_id CHAR(32),
                sistema_plantio VARCHAR(50),
                data_plantio_prevista DATE,
                data_plantio_real DATE,
                data_colheita_prevista DATE,
                data_colheita_real DATE,
                populacao_prevista INTEGER,
                populacao_real INTEGER,
                espacamento_cm INTEGER,
                area_plantada_ha NUMERIC(12, 4),
                produtividade_meta_sc_ha NUMERIC(12, 2),
                produtividade_real_sc_ha NUMERIC(12, 2),
                preco_venda_previsto NUMERIC(12, 2),
                custo_previsto_ha NUMERIC(12, 2),
                custo_realizado_ha NUMERIC(12, 2),
                status VARCHAR(20),
                observacoes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (talhao_id) REFERENCES cadastros_areas_rurais(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS agricola_operacao_tipo_fase (
                id CHAR(32) PRIMARY KEY,
                tenant_id CHAR(32),
                tipo_operacao VARCHAR(50) UNIQUE,
                fases_permitidas TEXT,
                descricao TEXT,
                ativo BOOLEAN DEFAULT 1,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS operacoes_agricolas (
                id CHAR(32) PRIMARY KEY,
                tenant_id CHAR(32) NOT NULL,
                safra_id CHAR(32) NOT NULL,
                talhao_id CHAR(32) NOT NULL,
                tipo VARCHAR(50),
                descricao TEXT,
                data_realizada DATE,
                area_aplicada_ha NUMERIC(12, 4),
                custo_total NUMERIC(12, 2),
                custo_por_ha NUMERIC(12, 2),
                fase_safra VARCHAR(30),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (safra_id) REFERENCES safras(id),
                FOREIGN KEY (talhao_id) REFERENCES cadastros_areas_rurais(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS insumo_operacao (
                id CHAR(32) PRIMARY KEY,
                operacao_id CHAR(32) NOT NULL,
                tenant_id CHAR(32) NOT NULL,
                insumo_id CHAR(32) NOT NULL,
                lote_insumo VARCHAR(100),
                dose_por_ha NUMERIC(12, 4),
                unidade VARCHAR(20),
                area_aplicada NUMERIC(12, 4),
                quantidade_total NUMERIC(12, 2),
                custo_unitario NUMERIC(12, 4),
                custo_total NUMERIC(15, 2),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (operacao_id) REFERENCES operacoes_agricolas(id),
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (insumo_id) REFERENCES cadastros_produtos(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS romaneios_colheita (
                id CHAR(32) PRIMARY KEY,
                tenant_id CHAR(32) NOT NULL,
                safra_id CHAR(32) NOT NULL,
                talhao_id CHAR(32) NOT NULL,
                data_colheita DATE,
                peso_bruto_kg NUMERIC(15, 2),
                tara_kg NUMERIC(15, 2),
                umidade_pct NUMERIC(5, 2),
                impureza_pct NUMERIC(5, 2),
                preco_saca NUMERIC(12, 2),
                peso_liquido_kg NUMERIC(15, 2),
                sacas_60kg NUMERIC(12, 2),
                receita_total NUMERIC(15, 2),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (safra_id) REFERENCES safras(id),
                FOREIGN KEY (talhao_id) REFERENCES cadastros_areas_rurais(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS planos_conta (
                id CHAR(32) PRIMARY KEY,
                tenant_id CHAR(32),
                descricao VARCHAR(255),
                categoria_rfb VARCHAR(50),
                ativo BOOLEAN DEFAULT 1,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fin_despesas (
                id CHAR(32) PRIMARY KEY,
                tenant_id CHAR(32) NOT NULL,
                fazenda_id CHAR(32),
                plano_conta_id CHAR(32),
                descricao TEXT,
                valor_total NUMERIC(15, 2),
                data_emissao DATE,
                data_vencimento DATE,
                data_pagamento DATE,
                status VARCHAR(20),
                origem_id CHAR(32),
                origem_tipo VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (plano_conta_id) REFERENCES planos_conta(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fin_receitas (
                id CHAR(32) PRIMARY KEY,
                tenant_id CHAR(32) NOT NULL,
                fazenda_id CHAR(32),
                plano_conta_id CHAR(32),
                descricao TEXT,
                valor_total NUMERIC(15, 2),
                data_emissao DATE,
                data_vencimento DATE,
                data_recebimento DATE,
                status VARCHAR(20),
                origem_id CHAR(32),
                origem_tipo VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (plano_conta_id) REFERENCES planos_conta(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fazendas (
                id CHAR(32) PRIMARY KEY,
                tenant_id CHAR(32) NOT NULL,
                grupo_id CHAR(32),
                nome VARCHAR(150) NOT NULL,
                cnpj VARCHAR(20),
                inscricao_estadual VARCHAR(50),
                area_total_ha NUMERIC(10, 2),
                coordenadas_sede VARCHAR(100),
                geometria TEXT,
                ativo BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cadastros_produtos (
                id CHAR(32) PRIMARY KEY,
                tenant_id CHAR(32),
                nome VARCHAR(255) NOT NULL,
                tipo VARCHAR(50),
                unidade_medida VARCHAR(10) DEFAULT 'UN',
                codigo_interno VARCHAR(50),
                sku VARCHAR(100),
                codigo_barras VARCHAR(60),
                descricao TEXT,
                marca_id CHAR(32),
                modelo_id CHAR(32),
                marca VARCHAR(100),
                fabricante VARCHAR(100),
                referencia_fabricante VARCHAR(100),
                categoria_id CHAR(32),
                imagem_url VARCHAR(500),
                qtd_conteudo NUMERIC(12, 2),
                unidade_conteudo VARCHAR(10),
                estoque_minimo NUMERIC(12, 2) DEFAULT 0.0,
                preco_medio NUMERIC(12, 2) DEFAULT 0.0,
                preco_ultima_compra NUMERIC(12, 2),
                dados_extras JSON,
                ativo BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS estoque_depositos (
                id CHAR(32) PRIMARY KEY,
                tenant_id CHAR(32) NOT NULL,
                fazenda_id CHAR(32) NOT NULL,
                nome VARCHAR(100) NOT NULL,
                tipo VARCHAR(50) DEFAULT 'GERAL',
                localizacao_desc VARCHAR(200),
                ativo BOOLEAN DEFAULT 1,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (fazenda_id) REFERENCES fazendas(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS estoque_lotes (
                id CHAR(32) PRIMARY KEY,
                produto_id CHAR(32) NOT NULL,
                deposito_id CHAR(32) NOT NULL,
                numero_lote VARCHAR(100) NOT NULL,
                data_fabricacao DATE,
                data_validade DATE,
                quantidade_inicial NUMERIC(12, 2) DEFAULT 0.0,
                quantidade_atual NUMERIC(12, 2) DEFAULT 0.0,
                custo_unitario NUMERIC(12, 4) DEFAULT 0.0,
                nota_fiscal_ref VARCHAR(100),
                status VARCHAR(20) DEFAULT 'ATIVO',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (produto_id) REFERENCES cadastros_produtos(id),
                FOREIGN KEY (deposito_id) REFERENCES estoque_depositos(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS estoque_saldos (
                id CHAR(32) PRIMARY KEY,
                deposito_id CHAR(32) NOT NULL,
                produto_id CHAR(32) NOT NULL,
                quantidade_atual NUMERIC(12, 2) DEFAULT 0.0,
                quantidade_reservada NUMERIC(12, 2) DEFAULT 0.0,
                ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deposito_id) REFERENCES estoque_depositos(id),
                FOREIGN KEY (produto_id) REFERENCES cadastros_produtos(id)
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS estoque_movimentacoes (
                id CHAR(32) PRIMARY KEY,
                deposito_id CHAR(32) NOT NULL,
                produto_id CHAR(32) NOT NULL,
                usuario_id CHAR(32),
                lote_id CHAR(32),
                tipo VARCHAR(20) NOT NULL,
                quantidade NUMERIC(12, 2) NOT NULL,
                data_movimentacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                custo_unitario NUMERIC(12, 4),
                custo_total NUMERIC(15, 2),
                motivo VARCHAR(255),
                origem_id CHAR(32),
                origem_tipo VARCHAR(50),
                FOREIGN KEY (deposito_id) REFERENCES estoque_depositos(id),
                FOREIGN KEY (produto_id) REFERENCES cadastros_produtos(id),
                FOREIGN KEY (lote_id) REFERENCES estoque_lotes(id)
            )
        """))

    yield engine
    await engine.dispose()

@pytest.fixture
async def session_a(engine_memory) -> AsyncSession:
    """Uma sessão simulando o contexto restrito do Tenant A"""
    async_session = async_sessionmaker(engine_memory, expire_on_commit=False)
    async with async_session() as session:
        session.info["tenant_id"] = TENANT_A_ID
        yield session

@pytest.fixture
async def session_b(engine_memory) -> AsyncSession:
    """Uma sessão simulando o contexto restrito do Tenant B, o invasor"""
    async_session = async_sessionmaker(engine_memory, expire_on_commit=False)
    async with async_session() as session:
        session.info["tenant_id"] = TENANT_B_ID
        yield session

@pytest.fixture
async def session(session_a) -> AsyncSession:
    """Alias para session_a para compatibilidade com testes existentes"""
    return session_a

@pytest.fixture
def tenant_id() -> str:
    """ID do tenant padrão para testes"""
    return str(TENANT_A_ID)

@pytest.fixture
def outro_tenant_id() -> str:
    """ID de outro tenant para testes de isolamento"""
    return str(TENANT_B_ID)

@pytest.fixture
async def fazenda_id(session: AsyncSession, tenant_id: str) -> str:
    """ID de uma fazenda criada no banco para testes"""
    fazenda = Fazenda(
        id=uuid.uuid4(),
        tenant_id=uuid.UUID(tenant_id),
        nome="Fazenda Teste",
        ativo=True,
    )
    session.add(fazenda)
    await session.commit()
    return str(fazenda.id)

@pytest.fixture
def talhao_id() -> str:
    """ID de um talhão para testes (corresponde ao campo em Safra)"""
    return str(uuid.uuid4())
