---
trigger: manual
---

# PROMPT MASTER — MÓDULO LAVOURA (api_agricola + apps/web)
> Cole este prompt inteiro no contexto da sua IDE com IA (Cursor, Windsurf, Copilot Workspace).
> O objetivo é construir o módulo Lavoura do AgroSaaS **completo e operacional**.

---

## 0. CONTEXTO DO PROJETO — LEIA ANTES DE QUALQUER COISA

Você está trabalhando no **AgroSaaS**, uma plataforma SaaS modular de gestão agropecuária.
Já existem no repositório as seguintes estruturas base — **não recrie, apenas estenda**:

### Stack definida (imutável)
- **Backend:** Python 3.12, FastAPI 0.115, SQLAlchemy 2.0 async, Pydantic v2, Alembic, Celery 5.4, Redis 7
- **Frontend:** Next.js 16 (App Router, RSC), React 19, TypeScript 5.7, TanStack Query v5, Zustand 5, Zod 3.24, shadcn/ui, Tailwind CSS 4, AG Grid 33, Recharts, MapLibre GL 4
- **Banco:** PostgreSQL 16 com extensões PostGIS 3.5, TimescaleDB 2.x, pgvector 0.8
- **Infra:** K3s, Traefik v3, Keycloak (JWT RS256), Celery workers, MinIO, Ollama (LLM local), Redis Sentinel

### Arquivos base já existentes — importe, não recrie
```
services/api_agricola/
├── main.py                  # FastAPI app factory já configurada
├── dependencies.py          # get_session, get_tenant_id, require_module, require_role
├── database.py              # async_session_maker, Base
├── config.py                # Settings via pydantic-settings
└── services/base_service.py # BaseService[T] com tenant isolation automático
```

### Padrões obrigatórios do projeto (Dev Rules)
1. **Tenant isolation tripla:** RLS PostgreSQL + WHERE tenant_id no BaseService + JWT middleware
2. **SRP:** Router valida e delega. Service processa. Schema é a fonte da verdade.
3. **Type hints completos** em todo Python. TypeScript strict mode.
4. **Nunca retornar** SQLAlchemy model diretamente — sempre serializar via Pydantic schema.
5. **Migrations Alembic** para toda mudança de schema, com `downgrade()` funcional.
6. **Cobertura mínima:** 90% services, 80% total, testes de tenant isolation obrigatórios.
7. **Conventional Commits** em todos os arquivos criados nos comentários de cabeçalho.
8. **Feature gate:** todo endpoint do módulo Lavoura requer `Depends(require_module("AGRICOLA_A2"))`.

---

## 1. ESCOPO COMPLETO DO MÓDULO

O módulo Lavoura (`AGRICOLA_A2`) é composto pelos seguintes subdomínios.
**Implemente todos, na ordem apresentada**, pois há dependências entre eles.

```
SUBDOMÍNIO 1  — Talhões e Geometria (base para tudo)
SUBDOMÍNIO 2  — Planejamento de Safra
SUBDOMÍNIO 3  — Caderno de Campo (Operações)
SUBDOMÍNIO 4  — Manejo Fitossanitário
SUBDOMÍNIO 5  — Controle de Insumos (Agrícola)
SUBDOMÍNIO 6  — Colheita e Romaneio
SUBDOMÍNIO 7  — NDVI / Sentinel-2 (satélite)
SUBDOMÍNIO 8  — Agrônomo Virtual (LLM local)
SUBDOMÍNIO 9  — Previsão de Produtividade (ML)
SUBDOMÍNIO 10 — Integração Climática Inteligente
SUBDOMÍNIO 11 — Custo Real por Saca (Econômico)
SUBDOMÍNIO 12 — Rastreabilidade e Certificações
SUBDOMÍNIO 13 — Mapa de Prescrição (VRA)
```

---

## 2. SCHEMA DO BANCO — CRIE TODAS AS MIGRATIONS

### 2.1 Instrução geral de migrations
- Arquivo: `services/api_agricola/migrations/versions/`
- Nomeação: `{NNN}_{descricao_snake_case}.py`
- Toda migration deve ter `upgrade()` e `downgrade()` funcionais
- Índices sempre com `CREATE INDEX CONCURRENTLY` (use `op.execute()` para isso)
- Usar `postgresql_where` para partial indexes onde aplicável

### 2.2 Tabelas a criar

#### MIGRATION 001 — talhoes
```sql
CREATE TABLE talhoes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    fazenda_id      UUID NOT NULL REFERENCES fazendas(id) ON DELETE CASCADE,
    nome            VARCHAR(100) NOT NULL,
    codigo          VARCHAR(20),                      -- código interno da fazenda
    area_ha         NUMERIC(12,4),                    -- calculado do polígono PostGIS
    area_ha_manual  NUMERIC(12,4),                    -- fallback se não tiver geom
    geometria       GEOMETRY(Polygon, 4326),           -- polígono PostGIS WGS84
    centroide       GEOMETRY(Point, 4326),             -- calculado automaticamente
    tipo_solo       VARCHAR(50),
    classe_solo     VARCHAR(10),                       -- LVA, LV, PVA, RQ...
    textura_solo    VARCHAR(20),                       -- argiloso, médio, arenoso
    relevo          VARCHAR(20),                       -- plano, suave_ondulado, ondulado
    irrigado        BOOLEAN DEFAULT FALSE,
    sistema_irrigacao VARCHAR(50),                     -- pivot, gotejamento, aspersao
    historico_culturas JSONB DEFAULT '[]',             -- [{safra, cultura, produtividade_sc_ha}]
    ativo           BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX CONCURRENTLY ix_talhoes_tenant_fazenda ON talhoes(tenant_id, fazenda_id) WHERE ativo = TRUE;
CREATE INDEX CONCURRENTLY ix_talhoes_geometria ON talhoes USING GIST(geometria);
CREATE INDEX CONCURRENTLY ix_talhoes_centroide ON talhoes USING GIST(centroide);

-- RLS
ALTER TABLE talhoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE talhoes FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON talhoes FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Trigger: recalcula area_ha e centroide ao salvar geometria
CREATE OR REPLACE FUNCTION atualizar_geometria_talhao()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.geometria IS NOT NULL THEN
        NEW.area_ha := ST_Area(NEW.geometria::geography) / 10000.0;
        NEW.centroide := ST_Centroid(NEW.geometria);
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_talhao_geometria
    BEFORE INSERT OR UPDATE ON talhoes
    FOR EACH ROW EXECUTE FUNCTION atualizar_geometria_talhao();
```

#### MIGRATION 002 — cultivares (tabela de referência)
```sql
CREATE TABLE cultivares (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cultura         VARCHAR(50) NOT NULL,              -- soja, milho, algodao, trigo...
    nome            VARCHAR(100) NOT NULL,
    empresa         VARCHAR(100),
    ciclo_dias_min  INT,
    ciclo_dias_max  INT,
    gdu_necessario  NUMERIC(8,2),                      -- graus-dia úteis para maturação
    potencial_sc_ha NUMERIC(8,2),
    tecnologia      VARCHAR(50),                       -- RR, Bt, convencional
    populacao_min   INT,                               -- plantas/ha
    populacao_max   INT,
    espacamento_cm  INT,
    observacoes     TEXT,
    ativo           BOOLEAN DEFAULT TRUE
);
-- Populada via seed com dados públicos da EMBRAPA/Ministério da Agricultura
```

#### MIGRATION 003 — safras
```sql
CREATE TABLE safras (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id               UUID NOT NULL REFERENCES tenants(id),
    talhao_id               UUID NOT NULL REFERENCES talhoes(id),
    ano_safra               VARCHAR(10) NOT NULL,      -- '2024/25', '2025'
    cultura                 VARCHAR(50) NOT NULL,      -- soja, milho_1, milho_2, algodao...
    cultivar_id             UUID REFERENCES cultivares(id),
    cultivar_nome           VARCHAR(100),              -- fallback se cultivar não está na tabela
    sistema_plantio         VARCHAR(30),               -- convencional, plantio_direto, organico
    data_plantio_prevista   DATE,
    data_plantio_real       DATE,
    data_colheita_prevista  DATE,
    data_colheita_real      DATE,
    populacao_prevista      INT,                       -- plantas/ha
    populacao_real          INT,                       -- medido no estande
    espacamento_cm          INT,
    area_plantada_ha        NUMERIC(12,4),
    produtividade_meta_sc_ha NUMERIC(8,2),
    produtividade_real_sc_ha NUMERIC(8,2),             -- calculado ao fechar romaneios
    preco_venda_previsto    NUMERIC(12,2),             -- R$/saca no planejamento
    custo_previsto_ha       NUMERIC(12,2),
    custo_realizado_ha      NUMERIC(12,2),
    status  VARCHAR(20) NOT NULL DEFAULT 'PLANEJADA'
            CHECK (status IN ('PLANEJADA','EM_PREPARO','PLANTADA','EM_CRESCIMENTO',
                              'EM_COLHEITA','COLHIDA','CANCELADA')),
    observacoes             TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX CONCURRENTLY ix_safras_tenant_talhao ON safras(tenant_id, talhao_id);
CREATE INDEX CONCURRENTLY ix_safras_tenant_ano ON safras(tenant_id, ano_safra);
CREATE UNIQUE INDEX uq_safras_talhao_ano_cultura
    ON safras(talhao_id, ano_safra, cultura)
    WHERE status != 'CANCELADA';

ALTER TABLE safras ENABLE ROW LEVEL SECURITY;
ALTER TABLE safras FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON safras FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

#### MIGRATION 004 — operacoes_agricolas (caderno de campo)
```sql
CREATE TABLE operacoes_agricolas (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    safra_id        UUID NOT NULL REFERENCES safras(id),
    talhao_id       UUID NOT NULL REFERENCES talhoes(id),

    -- Classificação
    tipo            VARCHAR(30) NOT NULL
                    CHECK (tipo IN (
                        'PREPARO_SOLO','CALAGEM','GESSAGEM',
                        'PLANTIO','ADUBACAO_PLANTIO','ADUBACAO_COBERTURA',
                        'APLICACAO_DEFENSIVO','IRRIGACAO','DESSECACAO',
                        'COLHEITA','AMOSTRAGEM_SOLO','MONITORAMENTO','OUTRO'
                    )),
    subtipo         VARCHAR(50),                       -- herbicida, fungicida, inseticida...
    descricao       TEXT NOT NULL,

    -- Temporal
    data_prevista   DATE,
    data_realizada  DATE NOT NULL,
    hora_inicio     TIME,
    hora_fim        TIME,

    -- Área e equipamento
    area_aplicada_ha NUMERIC(12,4),
    maquina_id      UUID REFERENCES maquinas(id),
    implemento      VARCHAR(100),
    operador_id     UUID REFERENCES usuarios(id),

    -- Clima no momento (preenchido automaticamente via API)
    temperatura_c   NUMERIC(5,2),
    umidade_rel     NUMERIC(5,2),
    vento_kmh       NUMERIC(5,2),
    direcao_vento   VARCHAR(10),
    condicao_clima  VARCHAR(30),

    -- Localização (GPS do app mobile)
    latitude        NUMERIC(10,7),
    longitude       NUMERIC(10,7),

    -- Custo (calculado automaticamente dos insumos)
    custo_total     NUMERIC(15,2) DEFAULT 0,
    custo_por_ha    NUMERIC(12,4) DEFAULT 0,

    -- Status
    status          VARCHAR(20) DEFAULT 'REALIZADA'
                    CHECK (status IN ('PLANEJADA','REALIZADA','CANCELADA')),
    observacoes     TEXT,
    fotos           TEXT[] DEFAULT '{}',               -- paths no MinIO

    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX CONCURRENTLY ix_op_tenant_safra ON operacoes_agricolas(tenant_id, safra_id);
CREATE INDEX CONCURRENTLY ix_op_talhao_data ON operacoes_agricolas(talhao_id, data_realizada DESC);
CREATE INDEX CONCURRENTLY ix_op_tipo_data ON operacoes_agricolas(tenant_id, tipo, data_realizada DESC);

ALTER TABLE operacoes_agricolas ENABLE ROW LEVEL SECURITY;
ALTER TABLE operacoes_agricolas FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON operacoes_agricolas FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

#### MIGRATION 005 — insumos_operacao (itens de cada operação)
```sql
CREATE TABLE insumos_operacao (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operacao_id     UUID NOT NULL REFERENCES operacoes_agricolas(id) ON DELETE CASCADE,
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    insumo_id       UUID NOT NULL REFERENCES insumos(id),
    lote_insumo     VARCHAR(50),
    dose_por_ha     NUMERIC(12,4) NOT NULL,
    unidade         VARCHAR(20) NOT NULL,              -- kg, L, g, mL, kg/ha, L/ha
    area_aplicada   NUMERIC(12,4),
    quantidade_total NUMERIC(12,4),                   -- calculado: dose * area
    custo_unitario  NUMERIC(12,4),
    custo_total     NUMERIC(15,2),
    -- Para defensivos
    carencia_dias   INT,
    data_reentrada  DATE,                              -- calculada: data_operacao + carencia
    epi_necessario  TEXT[]
);

ALTER TABLE insumos_operacao ENABLE ROW LEVEL SECURITY;
ALTER TABLE insumos_operacao FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON insumos_operacao FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

#### MIGRATION 006 — monitoramento_pragas
```sql
CREATE TABLE monitoramento_pragas (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    safra_id        UUID NOT NULL REFERENCES safras(id),
    talhao_id       UUID NOT NULL REFERENCES talhoes(id),
    data_avaliacao  DATE NOT NULL,

    -- Organismo alvo
    tipo            VARCHAR(20) CHECK (tipo IN ('PRAGA','DOENCA','PLANTA_DANINHA')),
    nome_cientifico VARCHAR(100),
    nome_popular    VARCHAR(100),

    -- Nível de infestação
    nivel_infestacao NUMERIC(8,4),                    -- %folhas atacadas, insetos/m, plantas/m2
    unidade_medida  VARCHAR(30),                      -- '%_desfolha','insetos_30cm','plantas_m2'
    nde_cultura     NUMERIC(8,4),                     -- nível de dano econômico da cultura
    atingiu_nde     BOOLEAN DEFAULT FALSE,

    -- Evidências
    fotos           TEXT[] DEFAULT '{}',
    pontos_coleta   JSONB DEFAULT '[]',               -- [{lat, lng, nivel}]

    -- Diagnóstico IA (preenchido pelo sistema)
    diagnostico_ia  JSONB,                            -- {praga, confianca, recomendacoes}

    -- Monitoramento realizado por
    tecnico_id      UUID REFERENCES usuarios(id),
    latitude        NUMERIC(10,7),
    longitude       NUMERIC(10,7),
    observacoes     TEXT,

    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX CONCURRENTLY ix_monit_safra_data ON monitoramento_pragas(safra_id, data_avaliacao DESC);
CREATE INDEX CONCURRENTLY ix_monit_talhao_nde ON monitoramento_pragas(talhao_id, atingiu_nde)
    WHERE atingiu_nde = TRUE;

ALTER TABLE monitoramento_pragas ENABLE ROW LEVEL SECURITY;
ALTER TABLE monitoramento_pragas FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON monitoramento_pragas FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

#### MIGRATION 007 — romaneios_colheita
```sql
CREATE TABLE romaneios_colheita (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),
    safra_id            UUID NOT NULL REFERENCES safras(id),
    talhao_id           UUID NOT NULL REFERENCES talhoes(id),

    -- Dados do romaneio
    numero_romaneio     VARCHAR(30),
    data_colheita       DATE NOT NULL,
    turno               VARCHAR(10),                  -- manha, tarde, noite
    maquina_colhedora_id UUID REFERENCES maquinas(id),
    operador_id         UUID REFERENCES usuarios(id),

    -- Pesagem
    peso_bruto_kg       NUMERIC(12,3) NOT NULL,
    tara_kg             NUMERIC(12,3) DEFAULT 0,
    peso_liquido_kg     NUMERIC(12,3),               -- calculado

    -- Classificação
    umidade_pct         NUMERIC(5,2),
    impureza_pct        NUMERIC(5,2),
    avariados_pct       NUMERIC(5,2),
    desconto_umidade_kg NUMERIC(12,3),               -- calculado pela tabela ABIOVE/ANEC
    desconto_impureza_kg NUMERIC(12,3),
    peso_liquido_padrao_kg NUMERIC(12,3),            -- peso após descontos

    -- Produção em sacas
    sacas_60kg          NUMERIC(12,3),               -- calculado automaticamente
    produtividade_sc_ha NUMERIC(10,4),               -- calculado: sacas / area_plantada

    -- Destino
    destino             VARCHAR(30) CHECK (destino IN
                            ('ARMAZEM_PROPRIO','COOPERATIVA','TRADING','VENDA_DIRETA','CONSUMO_PROPRIO')),
    armazem_id          UUID,
    nf_id               UUID REFERENCES notas_fiscais(id),
    preco_saca          NUMERIC(12,2),
    receita_total       NUMERIC(15,2),               -- calculado: sacas * preco_saca

    observacoes         TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE romaneios_colheita ENABLE ROW LEVEL SECURITY;
ALTER TABLE romaneios_colheita FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON romaneios_colheita FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

#### MIGRATION 008 — ndvi_talhao (TimescaleDB)
```sql
CREATE TABLE ndvi_talhao (
    id              UUID DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    talhao_id       UUID NOT NULL REFERENCES talhoes(id),
    data_imagem     TIMESTAMPTZ NOT NULL,             -- partition key

    -- Valores NDVI
    ndvi_medio      NUMERIC(6,4),                    -- -1 a 1
    ndvi_min        NUMERIC(6,4),
    ndvi_max        NUMERIC(6,4),
    ndvi_desvio     NUMERIC(6,4),
    cobertura_nuvem NUMERIC(5,2),                    -- % de cobertura de nuvens
    pixels_validos  INT,

    -- Dados da imagem
    satelite        VARCHAR(30) DEFAULT 'Sentinel-2',
    banda_usada     VARCHAR(20) DEFAULT 'B04_B08',   -- bandas NIR e Red
    resolucao_m     INT DEFAULT 10,
    url_imagem      TEXT,                             -- MinIO bucket path

    -- Mapa raster gerado
    raster_path     TEXT,                             -- path no MinIO para o GeoTIFF
    geojson_zonas   JSONB,                            -- zonas de variabilidade detectadas

    PRIMARY KEY (id, data_imagem)
);

-- Converter em hypertable TimescaleDB
SELECT create_hypertable('ndvi_talhao', by_range('data_imagem', INTERVAL '3 months'));

ALTER TABLE ndvi_talhao SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'tenant_id, talhao_id',
    timescaledb.compress_orderby = 'data_imagem DESC'
);
SELECT add_compression_policy('ndvi_talhao', INTERVAL '6 months');

CREATE INDEX ix_ndvi_talhao_data ON ndvi_talhao(talhao_id, data_imagem DESC);

-- Continuous aggregate: NDVI mensal por talhão
CREATE MATERIALIZED VIEW ndvi_mensal
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 month', data_imagem) AS mes,
    tenant_id, talhao_id,
    AVG(ndvi_medio)      AS ndvi_medio,
    MIN(ndvi_min)        AS ndvi_min,
    MAX(ndvi_max)        AS ndvi_max,
    COUNT(*)             AS qtd_imagens
FROM ndvi_talhao
WHERE cobertura_nuvem < 20
GROUP BY 1, 2, 3
WITH NO DATA;
```

#### MIGRATION 009 — previsoes_produtividade
```sql
CREATE TABLE previsoes_produtividade (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    safra_id        UUID NOT NULL REFERENCES safras(id),
    talhao_id       UUID NOT NULL REFERENCES talhoes(id),
    data_previsao   TIMESTAMPTZ DEFAULT NOW(),

    -- Previsão
    produtividade_prevista_sc_ha NUMERIC(10,4),
    intervalo_inf_sc_ha         NUMERIC(10,4),       -- IC 80%
    intervalo_sup_sc_ha         NUMERIC(10,4),
    confianca_pct               NUMERIC(5,2),

    -- Inputs usados pelo modelo
    ndvi_atual              NUMERIC(6,4),
    ndvi_desvio_historico   NUMERIC(6,4),            -- desvio vs média histórica
    precipitacao_acumulada  NUMERIC(10,2),
    gdu_acumulado           NUMERIC(10,2),
    estagio_fenologico      VARCHAR(20),             -- V3, V6, R1, R3, R5...
    dias_desde_plantio      INT,

    -- Resultado do modelo
    modelo_usado            VARCHAR(50),             -- 'xgboost_v2', 'prophet_v1'
    features_importancia    JSONB,                   -- {feature: importancia}
    historico_talhao_sc_ha  NUMERIC(10,4),          -- média histórica do talhão

    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ix_prev_safra ON previsoes_produtividade(safra_id, data_previsao DESC);

ALTER TABLE previsoes_produtividade ENABLE ROW LEVEL SECURITY;
ALTER TABLE previsoes_produtividade FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON previsoes_produtividade FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

#### MIGRATION 010 — alertas_agronomicos
```sql
CREATE TABLE alertas_agronomicos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    safra_id        UUID REFERENCES safras(id),
    talhao_id       UUID REFERENCES talhoes(id),
    tipo            VARCHAR(50) NOT NULL
                    CHECK (tipo IN (
                        'NDE_ATINGIDO','NDVI_QUEDA','JANELA_APLICACAO',
                        'RISCO_GEADA','DEFICIT_HIDRICO','EXCESSO_HIDRICO',
                        'PRODUCAO_ABAIXO_META','CUSTO_ACIMA_ORCAMENTO',
                        'ESTAGIO_FENOLOGICO','PRAZO_CARENCIA','COLHEITA_PREVISTA'
                    )),
    prioridade      VARCHAR(10) DEFAULT 'MEDIA'
                    CHECK (prioridade IN ('CRITICA','ALTA','MEDIA','BAIXA')),
    titulo          VARCHAR(200) NOT NULL,
    descricao       TEXT,
    dados_extras    JSONB DEFAULT '{}',
    acao_sugerida   TEXT,
    lido            BOOLEAN DEFAULT FALSE,
    lido_em         TIMESTAMPTZ,
    lido_por        UUID REFERENCES usuarios(id),
    criado_em       TIMESTAMPTZ DEFAULT NOW(),
    expira_em       TIMESTAMPTZ
);

CREATE INDEX ix_alertas_tenant_lido ON alertas_agronomicos(tenant_id, lido, criado_em DESC)
    WHERE lido = FALSE;

ALTER TABLE alertas_agronomicos ENABLE ROW LEVEL SECURITY;
ALTER TABLE alertas_agronomicos FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON alertas_agronomicos FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

#### MIGRATION 011 — analises_solo
```sql
CREATE TABLE analises_solo (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    talhao_id       UUID NOT NULL REFERENCES talhoes(id),
    data_coleta     DATE NOT NULL,
    laboratorio     VARCHAR(100),
    numero_amostra  VARCHAR(50),
    profundidade_cm VARCHAR(20) DEFAULT '0-20',

    -- Macro
    ph_agua         NUMERIC(5,2),
    ph_cacl2        NUMERIC(5,2),
    materia_organica NUMERIC(8,4),                   -- g/dm3
    fosforo_ppm     NUMERIC(8,4),
    potassio_ppm    NUMERIC(8,4),
    calcio_ppm      NUMERIC(8,4),
    magnesio_ppm    NUMERIC(8,4),
    enxofre_ppm     NUMERIC(8,4),

    -- Micro
    boro_ppm        NUMERIC(8,4),
    cobre_ppm       NUMERIC(8,4),
    ferro_ppm       NUMERIC(8,4),
    manganes_ppm    NUMERIC(8,4),
    zinco_ppm       NUMERIC(8,4),

    -- Textura
    argila_pct      NUMERIC(6,2),
    silte_pct       NUMERIC(6,2),
    areia_pct       NUMERIC(6,2),

    -- CTC
    ctc_total       NUMERIC(10,4),
    saturacao_bases NUMERIC(6,2),                    -- % V
    saturacao_al    NUMERIC(6,2),

    -- Recomendações geradas por IA
    recomendacao_calagem_ha  NUMERIC(10,4),          -- t/ha
    recomendacao_gessagem_ha NUMERIC(10,4),
    recomendacao_npk         JSONB,                  -- {N:x, P:x, K:x} por cultura/fase
    laudo_ia                 TEXT,

    arquivo_laudo   TEXT,                             -- path MinIO do PDF original
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE analises_solo ENABLE ROW LEVEL SECURITY;
ALTER TABLE analises_solo FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON analises_solo FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

#### MIGRATION 012 — dados_climaticos_talhao (TimescaleDB)
```sql
CREATE TABLE dados_climaticos_talhao (
    tenant_id           UUID NOT NULL,
    talhao_id           UUID NOT NULL,
    timestamp           TIMESTAMPTZ NOT NULL,         -- partition key

    -- Meteorologia
    temperatura_max_c   NUMERIC(5,2),
    temperatura_min_c   NUMERIC(5,2),
    temperatura_med_c   NUMERIC(5,2),
    precipitacao_mm     NUMERIC(8,3),
    evapotranspiracoes_mm NUMERIC(8,3),              -- ET0 Penman-Monteith
    umidade_rel_pct     NUMERIC(5,2),
    vento_med_kmh       NUMERIC(6,2),
    vento_max_kmh       NUMERIC(6,2),
    radiacao_mj_m2      NUMERIC(8,4),

    -- Calculados
    gdu_dia             NUMERIC(6,3),                -- graus-dia úteis do dia
    balanco_hidrico_mm  NUMERIC(8,3),                -- precipitacao - evapotranspiracao
    risco_geada         BOOLEAN DEFAULT FALSE,

    -- Fonte
    fonte               VARCHAR(30) DEFAULT 'open-meteo',

    PRIMARY KEY (talhao_id, timestamp)
);

SELECT create_hypertable('dados_climaticos_talhao', by_range('timestamp', INTERVAL '1 month'));

ALTER TABLE dados_climaticos_talhao SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'tenant_id, talhao_id',
    timescaledb.compress_orderby = 'timestamp DESC'
);
SELECT add_compression_policy('dados_climaticos_talhao', INTERVAL '3 months');

-- Continuous aggregate: acumulados por safra
CREATE MATERIALIZED VIEW climatico_acumulado_mensal
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 month', timestamp) AS mes,
    tenant_id, talhao_id,
    SUM(precipitacao_mm)        AS precipitacao_total,
    SUM(evapotranspiracoes_mm)  AS et0_total,
    SUM(gdu_dia)                AS gdu_total,
    SUM(balanco_hidrico_mm)     AS balanco_hidrico,
    MAX(temperatura_max_c)      AS temp_max,
    MIN(temperatura_min_c)      AS temp_min,
    COUNT(*)                    AS dias
FROM dados_climaticos_talhao
GROUP BY 1, 2, 3
WITH NO DATA;
```

---

## 3. MODELS SQLALCHEMY — IMPLEMENTE TODOS

Crie em `services/api_agricola/models/`:

```python
# models/talhao.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Boolean, JSON, ForeignKey, text
from geoalchemy2 import Geometry
from uuid import UUID
import uuid
from datetime import datetime
from ..database import Base

class Talhao(Base):
    __tablename__ = "talhoes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    fazenda_id: Mapped[UUID] = mapped_column(ForeignKey("fazendas.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo: Mapped[str | None] = mapped_column(String(20))
    area_ha: Mapped[float | None] = mapped_column(Numeric(12, 4))
    area_ha_manual: Mapped[float | None] = mapped_column(Numeric(12, 4))
    geometria = mapped_column(Geometry("POLYGON", srid=4326), nullable=True)
    centroide = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    tipo_solo: Mapped[str | None] = mapped_column(String(50))
    classe_solo: Mapped[str | None] = mapped_column(String(10))
    textura_solo: Mapped[str | None] = mapped_column(String(20))
    relevo: Mapped[str | None] = mapped_column(String(20))
    irrigado: Mapped[bool] = mapped_column(Boolean, default=False)
    sistema_irrigacao: Mapped[str | None] = mapped_column(String(50))
    historico_culturas: Mapped[list] = mapped_column(JSON, default=list)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"), onupdate=datetime.utcnow)

    # Relacionamentos
    safras: Mapped[list["Safra"]] = relationship(back_populates="talhao", lazy="noload")
    analises_solo: Mapped[list["AnaliseSolo"]] = relationship(back_populates="talhao", lazy="noload")

    @property
    def area_efetiva_ha(self) -> float | None:
        """Retorna area_ha (PostGIS) ou area_ha_manual como fallback."""
        return self.area_ha or self.area_ha_manual
```

> Crie os demais models seguindo o mesmo padrão:
> `Safra`, `OperacaoAgricola`, `InsumoOperacao`, `MonitoramentoPragas`,
> `RomaneioColheita`, `NdviTalhao`, `PrevisaoProdutividade`,
> `AlertaAgronomico`, `AnaliseSolo`, `DadoClimatico`, `Cultivar`
>
> **Regras para todos os models:**
> - Usar `Mapped[]` e `mapped_column()` (SQLAlchemy 2.0 style)
> - Relacionamentos com `lazy="noload"` — carregar explicitamente com `selectinload`
> - Nunca usar `lazy="dynamic"` ou `lazy="subquery"`

---

## 4. SCHEMAS PYDANTIC V2 — IMPLEMENTE TODOS

Crie em `services/api_agricola/schemas/`:

### 4.1 Padrão obrigatório de nomenclatura
- `{entidade}_create.py` — input de criação (POST)
- `{entidade}_update.py` — input de atualização (PATCH), todos os campos Optional
- `{entidade}_response.py` — output (GET), nunca expor campos internos
- `{entidade}_filter.py` — parâmetros de filtro (Query params)

### 4.2 Schemas críticos a implementar

```python
# schemas/talhao_create.py
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Any
import json

class TalhaoCreate(BaseModel):
    fazenda_id: UUID
    nome: str = Field(..., min_length=1, max_length=100)
    codigo: str | None = Field(None, max_length=20)
    geometria_geojson: dict | None = None             # GeoJSON Polygon do frontend (MapLibre)
    area_ha_manual: float | None = Field(None, gt=0, le=100000)
    tipo_solo: str | None = None
    classe_solo: str | None = None
    textura_solo: TipoTexturaSolo | None = None
    relevo: TipoRelevo | None = None
    irrigado: bool = False
    sistema_irrigacao: str | None = None

    @model_validator(mode="after")
    def validar_area(self):
        if not self.geometria_geojson and not self.area_ha_manual:
            raise ValueError("É necessário informar geometria ou área manual do talhão")
        return self

class TalhaoResponse(BaseModel):
    id: UUID
    fazenda_id: UUID
    nome: str
    codigo: str | None
    area_ha: float | None
    area_ha_manual: float | None
    area_efetiva_ha: float | None                     # computed property do model
    tipo_solo: str | None
    classe_solo: str | None
    textura_solo: str | None
    irrigado: bool
    ativo: bool
    geometria_geojson: dict | None = None             # serializado pelo service
    centroide_lat: float | None = None
    centroide_lng: float | None = None
    historico_culturas: list[dict]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

```python
# schemas/safra_create.py
class SafraCreate(BaseModel):
    talhao_id: UUID
    ano_safra: str = Field(..., pattern=r"^\d{4}(/\d{2,4})?$")   # 2025 ou 2024/25
    cultura: CulturaEnum                              # Enum com todas as culturas suportadas
    cultivar_id: UUID | None = None
    cultivar_nome: str | None = None
    sistema_plantio: SistemaPlantioEnum
    data_plantio_prevista: date | None = None
    populacao_prevista: int | None = Field(None, gt=0, le=500000)
    espacamento_cm: int | None = Field(None, gt=0, le=200)
    area_plantada_ha: float | None = Field(None, gt=0)
    produtividade_meta_sc_ha: float | None = Field(None, gt=0)
    preco_venda_previsto: float | None = Field(None, gt=0)
    observacoes: str | None = None

    @model_validator(mode="after")
    def validar_cultivar(self):
        if not self.cultivar_id and not self.cultivar_nome:
            raise ValueError("Informe cultivar_id ou cultivar_nome")
        return self
```

```python
# schemas/operacao_create.py
class OperacaoAgricolaCreate(BaseModel):
    safra_id: UUID
    talhao_id: UUID
    tipo: TipoOperacaoEnum
    subtipo: str | None = None
    descricao: str = Field(..., min_length=3, max_length=500)
    data_realizada: date
    hora_inicio: time | None = None
    hora_fim: time | None = None
    area_aplicada_ha: float | None = Field(None, gt=0)
    maquina_id: UUID | None = None
    implemento: str | None = None
    operador_id: UUID | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    observacoes: str | None = None
    insumos: list["InsumoOperacaoCreate"] = []        # insumos usados nesta operação

class InsumoOperacaoCreate(BaseModel):
    insumo_id: UUID
    lote_insumo: str | None = None
    dose_por_ha: float = Field(..., gt=0)
    unidade: str = Field(..., min_length=1, max_length=20)
    area_aplicada: float | None = None
```

> Implemente schemas completos para todas as entidades restantes.
> Para cada entidade: `*Create`, `*Update` (todos Optional), `*Response`, `*Filter`.

---

## 5. SERVICES — IMPLEMENTE COM LÓGICA DE NEGÓCIO COMPLETA

Crie em `services/api_agricola/services/`:

### 5.1 TalhaoService

```python
# services/talhao_service.py
import json
from uuid import UUID
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape, mapping
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.talhao import Talhao
from ..schemas.talhao_create import TalhaoCreate, TalhaoUpdate
from .base_service import BaseService

class TalhaoService(BaseService[Talhao]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(Talhao, session, tenant_id)

    async def criar(self, dados: TalhaoCreate) -> Talhao:
        """
        Cria talhão com geometria PostGIS.
        Se geometria_geojson fornecida, converte para WKT e salva.
        area_ha é calculada automaticamente pelo trigger do banco.
        """
        dados_dict = dados.model_dump(exclude={"geometria_geojson"})

        if dados.geometria_geojson:
            geom_shapely = shape(dados.geometria_geojson)
            if not geom_shapely.is_valid:
                raise BusinessRuleError("Geometria do talhão é inválida")
            dados_dict["geometria"] = from_shape(geom_shapely, srid=4326)

        return await super().create(dados_dict)

    async def serializar_com_geojson(self, talhao: Talhao) -> dict:
        """Converte geometria PostGIS para GeoJSON para o frontend."""
        resultado = {col: getattr(talhao, col) for col in talhao.__table__.columns.keys()}
        if talhao.geometria is not None:
            geom = to_shape(talhao.geometria)
            resultado["geometria_geojson"] = mapping(geom)
        if talhao.centroide is not None:
            ponto = to_shape(talhao.centroide)
            resultado["centroide_lat"] = ponto.y
            resultado["centroide_lng"] = ponto.x
        return resultado

    async def calcular_sobreposicao(self, talhao_id: UUID, outro_talhao_id: UUID) -> float:
        """Retorna percentual de sobreposição entre dois talhões (deve ser 0 em produção)."""
        stmt = text("""
            SELECT ST_Area(
                ST_Intersection(a.geometria::geography, b.geometria::geography)
            ) / NULLIF(ST_Area(a.geometria::geography), 0) * 100 AS pct
            FROM talhoes a, talhoes b
            WHERE a.id = :id1 AND b.id = :id2
              AND a.tenant_id = :tid AND b.tenant_id = :tid
        """)
        result = await self.session.execute(stmt, {"id1": talhao_id, "id2": outro_talhao_id, "tid": self.tenant_id})
        return result.scalar() or 0.0
```

### 5.2 SafraService

```python
# services/safra_service.py
"""
Implemente SafraService com os métodos:

1. criar(dados: SafraCreate) -> Safra
   - Verifica se já existe safra ativa para o talhão+ano+cultura (unique constraint)
   - Calcula data_colheita_prevista com base na cultura + cultivar.ciclo_dias
   - Cria SafraConfiguracao inicial com os custos planejados

2. atualizar_status(safra_id, novo_status) -> Safra
   - Valida transições permitidas: PLANEJADA→EM_PREPARO→PLANTADA→EM_CRESCIMENTO→EM_COLHEITA→COLHIDA
   - Ao transitar para PLANTADA: registra data_plantio_real = hoje se não preenchida
   - Ao transitar para COLHIDA: chama fechar_safra()

3. fechar_safra(safra_id) -> Safra
   - Agrega todos os romaneios: produtividade_real_sc_ha = total_sacas / area_plantada
   - Agrega todos os custos das operações: custo_realizado_ha
   - Cria lançamento financeiro de receita no api-financeiro via httpx
   - Atualiza historico_culturas no Talhão com {safra, cultura, produtividade}

4. calcular_gdu_acumulado(safra_id) -> float
   - Soma gdu_dia de dados_climaticos_talhao desde data_plantio_real
   - Usa para estimar estágio fenológico atual

5. estimar_estagio_fenologico(safra_id) -> str
   - Com base em GDU acumulado + cultura + cultivar
   - Retorna: 'V1','V2'...'V6','R1'...'R8' para soja/milho
   - Usado por outros services para contexto no LLM
"""
```

### 5.3 OperacaoService

```python
# services/operacao_service.py
"""
Implemente OperacaoService com os métodos:

1. criar(dados: OperacaoAgricolaCreate) -> OperacaoAgricola
   - Para cada insumo em dados.insumos:
     a. Calcula quantidade_total = dose * area_aplicada
     b. Busca preço médio do estoque (api-operacional via httpx)
     c. Calcula custo do insumo
     d. Baixa do estoque (POST /estoques/{insumo_id}/baixa via httpx)
     e. Para defensivos: calcula data_reentrada = data_realizada + carencia_dias
   - Salva operacao com custo_total = soma dos insumos
   - Atualiza custo_realizado_ha na Safra (triggers ou update direto)
   - Dispara task Celery: verificar_alertas_pos_operacao

2. buscar_condicoes_clima(lat, lng, data) -> dict
   - Chama Open-Meteo API histórica para lat/lng/data
   - Retorna temperatura, umidade, vento, precipitação
   - Chamado automaticamente ao criar operação se lat/lng fornecidos

3. verificar_carencias_ativas(talhao_id, data_consulta) -> list[dict]
   - Retorna todos os defensivos com carência ainda ativa na data_consulta
   - Essencial antes de planejar colheita ou nova aplicação

4. gerar_receituario_agronomico(operacao_id) -> bytes (PDF)
   - Gera PDF do receituário com todos os dados legais
   - Salva no MinIO e retorna URL
"""
```

### 5.4 NdviService

```python
# services/ndvi_service.py
"""
Implemente NdviService com os métodos:

1. buscar_e_processar_sentinel2(talhao_id) -> NdviTalhao
   IMPLEMENTAÇÃO DETALHADA:

   a. Busca geometria do talhão (bbox = bounds do polígono)
   b. Chama Copernicus Data Space API (gratuito):
      URL: https://catalogue.dataspace.copernicus.eu/odata/v1/Products
      Filtros: CollectionName='SENTINEL-2', CloudCover le 20,
               ContentDate/Start ge <30 dias atrás>,
               OData.CSC.Intersects(area=geography'SRID=4326;{WKT_BBOX}')
   c. Baixa produto S2L2A (reflectância de superfície) via streaming
   d. Processa com rasterio + numpy:
      - Abre banda B04 (Red, 665nm) e B08 (NIR, 842nm)
      - Recorta pelo polígono do talhão (rasterio.mask.mask)
      - NDVI = (B08 - B04) / (B08 + B04)
      - Ignora pixels com valor == 0 (fora do talhão ou nuvem)
      - Calcula: ndvi_medio, ndvi_min, ndvi_max, ndvi_desvio
   e. Gera mapa de zonas de variabilidade:
      - Clasifica em 5 zonas: muito_baixo (<0.2), baixo (0.2-0.4),
        medio (0.4-0.6), alto (0.6-0.8), muito_alto (>0.8)
      - Converte para GeoJSON com ST_DumpAsPolygons
      - Salva GeoTIFF no MinIO: bucket/ndvi/{tenant_id}/{talhao_id}/{data}.tif
   f. Salva registro em ndvi_talhao
   g. Verifica se ndvi_medio caiu >15% vs média dos últimos 3 registros
      → Se sim: cria AlertaAgronomico tipo='NDVI_QUEDA'

2. calcular_historico_ndvi(talhao_id, meses=12) -> list[NdviTalhao]
   - Busca de ndvi_mensal (continuous aggregate)
   - Retorna série temporal para gráfico no frontend

3. gerar_mapa_variabilidade(talhao_id, safra_id) -> dict (GeoJSON)
   - Médias de NDVI durante o ciclo da safra
   - Classifica zonas e retorna FeatureCollection para MapLibre
"""
```

### 5.5 AgronomoVirtualService

```python
# services/agronomo_virtual_service.py
"""
Implemente AgronomoVirtualService com os métodos:

1. chat_stream(mensagem, safra_id, talhao_id) -> AsyncGenerator[str, None]
   IMPLEMENTAÇÃO DETALHADA:

   a. Monta contexto completo da safra/talhão:
      - safra: cultura, cultivar, status, dias desde plantio, área, meta produtividade
      - ultimo NDVI: valor, desvio da média histórica, data
      - clima atual: temperatura, precipitação 7d, GDU acumulado
      - estágio fenológico estimado
      - últimas 5 operações realizadas
      - custos acumulados vs orçado
      - alertas ativos

   b. RAG — busca knowledge base:
      - Usa pgvector: SELECT id, conteudo, <-> embedding AS distancia
        FROM documentos_rag
        WHERE categoria IN ('agronomia','defensivos','fertilizantes')
        ORDER BY embedding <=> query_embedding LIMIT 5
      - Documentos indexados: manuais EMBRAPA, bulas de defensivos registrados no MAPA,
        tabelas de adubação CQFS, ZARC por cultura/estado

   c. Monta prompt do sistema:
      SYSTEM_PROMPT = '''
      Você é um agrônomo virtual especializado em agricultura tropical brasileira.
      Responda SEMPRE em português do Brasil.
      Seja objetivo e prático — o produtor está no campo ou na sede da fazenda.

      DADOS ATUAIS DA SAFRA:
      {contexto_safra_json}

      DADOS CLIMÁTICOS:
      {contexto_clima}

      BASE DE CONHECIMENTO (EMBRAPA/MAPA):
      {documentos_rag}

      REGRAS:
      - Cite apenas produtos com registro MAPA válido
      - Informe dose e modo de aplicação quando recomendar defensivo
      - Mencione carência quando relevante para colheita próxima
      - Se detectar risco fitossanitário nos dados, alerte proativamente
      - Não extrapole para além dos dados disponíveis
      '''

   d. Chama Ollama com streaming:
      modelo: llama3.1:8b (ou mistral:7b como fallback)
      temperatura: 0.3 (respostas mais determinísticas para recomendações técnicas)
      max_tokens: 1000

   e. Yield cada chunk como Server-Sent Event

2. diagnosticar_praga_por_foto(imagem_bytes, talhao_id, cultura) -> DiagnosticoResult
   IMPLEMENTAÇÃO DETALHADA:

   a. Pré-processa imagem: resize para 640x640, normaliza para float32
   b. Roda modelo YOLO v11 via ONNX Runtime:
      - Carrega modelo: models/yolo_pragas_br_v1.onnx
        (treinado com dataset de pragas tropicais: lagarta-do-cartucho, ferrugem,
         mancha-alvo, percevejo-marrom, cigarrinha, broca-do-colmo...)
      - Threshold confiança: 0.5
      - Retorna: [{classe, confianca, bbox}]
   c. Para cada detecção com confiança > 0.5:
      - Busca praga na base (nome_cientifico, nome_popular, cultura_hospedeira)
      - Busca NDE para a cultura e estágio fenológico
      - Busca defensivos registrados para esta praga+cultura (MAPA)
   d. Gera resposta estruturada + envia para AgronomoVirtual para elaborar recomendação textual
   e. Salva diagnóstico em monitoramento_pragas automaticamente

3. recomendar_adubacao(talhao_id, cultura, produtividade_meta_sc_ha) -> RecomendacaoAdubacao
   - Busca última análise de solo do talhão
   - Aplica tabelas de recomendação CQFS/IAC/EMBRAPA por cultura+solo+meta
   - Retorna doses de N, P2O5, K2O por fase (plantio, cobertura 1, cobertura 2)
   - Calcula custo estimado da adubação recomendada
"""
```

### 5.6 PrevisaoProdutividadeService

```python
# services/previsao_produtividade_service.py
"""
Implemente PrevisaoProdutividadeService com os métodos:

1. prever(safra_id) -> PrevisaoProdutividade
   IMPLEMENTAÇÃO DETALHADA:

   a. Coleta features:
      features = {
          'ndvi_atual': ndvi mais recente do talhão,
          'ndvi_media_historica': média dos NDVIs dos mesmos estágios nas safras anteriores,
          'ndvi_desvio_historico': desvio relativo entre atual e histórico,
          'precipitacao_30d': soma precipitação últimos 30 dias (dados_climaticos),
          'precipitacao_60d': soma precipitação últimos 60 dias,
          'gdu_acumulado': graus-dia acumulados desde plantio,
          'gdu_esperado_estagio': GDU esperado para o estágio atual,
          'deficit_hidrico_30d': sum(max(0, ET0 - precipitacao)) dos últimos 30d,
          'temperatura_media': média das temperaturas dos últimos 30d,
          'dias_desde_plantio': int,
          'area_talhao_ha': float,
          'produtividade_media_historica': média das safras anteriores do mesmo talhão,
          'producoes_3anos': lista das últimas 3 produtividades,
      }

   b. Carrega modelo XGBoost:
      - Caminho: /models/xgboost_produtividade_{cultura}_v{versao}.pkl
      - Carregado via mlflow.sklearn.load_model() — versão registrada no MLflow
      - Se modelo não existir para a cultura, usa modelo genérico

   c. Gera previsão com intervalos de confiança:
      previsao = modelo.predict([features_array])[0]
      # Intervalo via predição com perturbação de features (bootstrap simples)
      ic_lower, ic_upper = calcular_intervalo_confianca(modelo, features_array, n=100)

   d. Calcula desvio vs meta:
      desvio_meta = (previsao - safra.produtividade_meta_sc_ha) / safra.produtividade_meta_sc_ha
      if desvio_meta < -0.15:
          criar_alerta(tipo='PRODUCAO_ABAIXO_META', prioridade='ALTA')

   e. Salva e retorna PrevisaoProdutividade

2. treinar_modelo(tenant_id) -> dict
   - Coleta dados históricos: todas as safras fechadas do tenant com dados climáticos e NDVI
   - Treina XGBoost com GridSearchCV para hiperparâmetros
   - Registra experimento no MLflow (tracking_uri = 'http://mlflow:5000')
   - Salva modelo e registra versão
   - Task Celery: executar mensalmente por tenant com histórico >= 3 safras
"""
```

### 5.7 ClimaticoService

```python
# services/climatico_service.py
"""
Implemente ClimaticoService com os métodos:

1. sincronizar_clima_talhao(talhao_id, data_inicio, data_fim) -> int
   IMPLEMENTAÇÃO DETALHADA:

   a. Busca centroide do talhão (lat, lng)
   b. Chama Open-Meteo API (sem API key):
      URL: https://archive-api.open-meteo.com/v1/archive
      Params:
        latitude={lat}&longitude={lng}
        &start_date={data_inicio}&end_date={data_fim}
        &daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,
               precipitation_sum,et0_fao_evapotranspiration,
               windspeed_10m_max,windspeed_10m_mean,
               shortwave_radiation_sum,relative_humidity_2m_mean
        &timezone=America/Sao_Paulo
   c. Para cada dia retornado:
      - Calcula GDU: max(0, (Tmax + Tmin)/2 - Tbase)
        Tbase = 10°C para soja/milho, 7°C para trigo
      - Calcula balanço hídrico: precipitacao - ET0
      - Detecta risco de geada: Tmin < 2°C
   d. Bulk insert em dados_climaticos_talhao
   e. Se geada detectada: cria AlertaAgronomico tipo='RISCO_GEADA'
   f. Retorna quantidade de dias inseridos

2. previsao_7dias(talhao_id) -> list[PrevisaoClimaDia]
   - Chama Open-Meteo forecast API para próximos 7 dias
   - Calcula risco de geada, excesso hídrico, déficit hídrico
   - Detecta janelas favoráveis de aplicação:
     janela_ok = (vento < 15 km/h) AND (sem_chuva_6h) AND (temp entre 15-28°C) AND (umidade < 70%)

3. calcular_balanco_hidrico_safra(safra_id) -> dict
   - Soma precipitação e ET0 desde data_plantio_real
   - Identifica períodos críticos de déficit (>30mm negativos consecutivos)
   - Retorna: {precipitacao_total, et0_total, balanco_total, periodos_deficit: [...]}

4. alerta_janela_aplicacao(safra_id) -> list[JanelaAplicacao]
   - Baseado na previsão dos próximos 7 dias
   - Retorna janelas de no mínimo 4h seguidas com condições favoráveis
   - Cria AlertaAgronomico tipo='JANELA_APLICACAO' se janela > 6h
"""
```

### 5.8 CustoSacaService

```python
# services/custo_saca_service.py
"""
Implemente CustoSacaService com os métodos:

1. calcular_custo_atual(safra_id) -> CustoSacaResult
   IMPLEMENTAÇÃO DETALHADA:
   
   a. Agrega custos realizados:
      - Operações agrícolas: SUM(operacoes.custo_total) / area_plantada_ha = custo_realizado_ha
      - Classifica por categoria: INSUMOS, MAO_OBRA, MAQUINARIO, OUTROS
   
   b. Coleta cotação da commodity:
      - Chama api-financeiro: GET /cotacoes/{cultura} (soja, milho, algodao...)
      - Cache Redis: TTL 1 hora
   
   c. Calcula métricas:
      custo_por_saca = custo_realizado_ha / produtividade_real_sc_ha
      ponto_equilibrio_sc_ha = custo_realizado_ha / cotacao_atual
      margem_bruta_projetada = (produtividade_meta * cotacao_atual) - custo_total_previsto
      percentual_custo_executado = custo_realizado / custo_previsto * 100
   
   d. Gera alertas se custo > 110% do orçado
   
   e. Retorna:
      {
        custo_ha_realizado, custo_ha_previsto, variacao_pct,
        custo_por_saca, ponto_equilibrio_sc_ha,
        cotacao_atual, margem_bruta_projetada,
        breakdown: { insumos_ha, mao_obra_ha, maquinario_ha, outros_ha },
        historico_safras_anteriores: [...]
      }

2. simulador_cenarios(safra_id, cenarios: list[CenarioPreco]) -> list[CenarioResult]
   - Para cada cenário de preço informado pelo usuário:
     resultado = { preco_saca, receita_total, lucro_bruto, roi_pct, recomendacao }
   - Retorna comparativo entre cenários para exibir no gráfico

3. benchmark_regional(safra_id) -> BenchmarkResult
   - Compara custo/ha e produtividade com médias regionais (dados CONAB/SENAR)
   - Classifica o talhão: acima_media, na_media, abaixo_media
"""
```

---

## 6. ROUTERS — IMPLEMENTE TODOS OS ENDPOINTS

### 6.1 Estrutura de arquivos
```
services/api_agricola/routers/
├── talhoes.py
├── safras.py
├── operacoes.py
├── monitoramento.py
├── romaneios.py
├── ndvi.py
├── agronomo.py
├── previsoes.py
├── climatico.py
├── custos.py
├── analises_solo.py
└── rastreabilidade.py
```

### 6.2 Endpoints completos por router

#### talhoes.py
```
GET    /talhoes/                          Lista talhões da fazenda (filtros: fazenda_id, ativo)
POST   /talhoes/                          Cria talhão (com ou sem geometria)
GET    /talhoes/{id}                      Detalhe com geometria GeoJSON
PATCH  /talhoes/{id}                      Atualiza dados
DELETE /talhoes/{id}                      Desativa (soft delete — ativo=False)
GET    /talhoes/{id}/geometria            Retorna só o GeoJSON do polígono
PATCH  /talhoes/{id}/geometria            Atualiza polígono via GeoJSON
GET    /talhoes/{id}/historico            Histórico de culturas do talhão
GET    /talhoes/{id}/ndvi/atual           NDVI mais recente do talhão
GET    /talhoes/{id}/analise-solo/ultima  Última análise de solo
```

#### safras.py
```
GET    /safras/                           Lista safras (filtros: talhao_id, ano_safra, cultura, status)
POST   /safras/                           Cria safra
GET    /safras/{id}                       Detalhe completo da safra
PATCH  /safras/{id}                       Atualiza dados
PATCH  /safras/{id}/status               Transição de status
GET    /safras/{id}/dashboard            Dashboard completo da safra (agrega tudo)
GET    /safras/{id}/operacoes            Operações da safra
GET    /safras/{id}/custos               Breakdown de custos
GET    /safras/{id}/produtividade        Produtividade real vs meta
GET    /safras/{id}/previsao             Previsão de produtividade ML
GET    /safras/{id}/clima                Dados climáticos do ciclo
GET    /safras/{id}/estagio-fenologico   Estágio estimado baseado em GDU
```

#### operacoes.py
```
GET    /operacoes/                        Lista operações (filtros: safra_id, tipo, data_inicio, data_fim)
POST   /operacoes/                        Cria operação (inclui insumos usados)
GET    /operacoes/{id}                    Detalhe
PATCH  /operacoes/{id}                    Atualiza
POST   /operacoes/{id}/fotos             Upload de foto para MinIO
GET    /operacoes/{id}/receituario       Gera PDF do receituário agronômico
GET    /operacoes/carencias-ativas       Carências de defensivos ativas no talhão/data
GET    /operacoes/planejadas             Operações planejadas para os próximos 7 dias
```

#### monitoramento.py
```
GET    /monitoramento/                    Lista monitoramentos (filtros: safra_id, tipo, atingiu_nde)
POST   /monitoramento/                    Registra monitoramento manual
POST   /monitoramento/diagnostico-foto   Upload foto → diagnóstico IA (YOLO + LLM)
GET    /monitoramento/{id}               Detalhe
GET    /monitoramento/alertas-nde        Monitoramentos com NDE atingido nas últimas 2 semanas
```

#### ndvi.py
```
GET    /ndvi/{talhao_id}/atual           NDVI mais recente
GET    /ndvi/{talhao_id}/historico       Série temporal de NDVI
POST   /ndvi/{talhao_id}/processar       Dispara busca e processamento Sentinel-2 (Celery job)
GET    /ndvi/{talhao_id}/variabilidade   Mapa de zonas de variabilidade (GeoJSON)
GET    /ndvi/{talhao_id}/raster          URL assinada do MinIO para o GeoTIFF mais recente
GET    /ndvi/safra/{safra_id}/comparativo NDVI atual vs médias históricas do mesmo período
```

#### agronomo.py
```
POST   /agronomo/chat                    Chat streaming com contexto da safra (SSE)
POST   /agronomo/diagnostico-praga       Diagnóstico por foto (multipart)
POST   /agronomo/recomendar-adubacao     Recomendação baseada em análise de solo
POST   /agronomo/interpretar-laudo-solo  Envia PDF de laudo → IA extrai e interpreta
GET    /agronomo/historico-chat          Últimas 20 conversas do usuário
```

#### previsoes.py
```
GET    /previsoes/safra/{safra_id}       Previsão atual de produtividade
POST   /previsoes/safra/{safra_id}/atualizar Força atualização da previsão
GET    /previsoes/talhao/{talhao_id}/historico Histórico de acurácia das previsões
```

#### climatico.py
```
GET    /climatico/{talhao_id}/atual      Clima atual + previsão 7 dias
GET    /climatico/{talhao_id}/historico  Série histórica (filtro: data_inicio, data_fim)
GET    /climatico/{talhao_id}/balanco-hidrico Balanço hídrico da safra atual
GET    /climatico/{talhao_id}/janelas-aplicacao Próximas janelas favoráveis de aplicação
GET    /climatico/safra/{safra_id}/gdu-acumulado GDU acumulado com estágio fenológico
```

#### custos.py
```
GET    /custos/safra/{safra_id}          Custo por saca em tempo real
GET    /custos/safra/{safra_id}/simulador Simulador de cenários de preço
GET    /custos/safra/{safra_id}/breakdown Custo detalhado por categoria
GET    /custos/safra/{safra_id}/benchmark Comparativo regional CONAB
GET    /custos/talhao/{talhao_id}/comparativo Comparativo entre safras do mesmo talhão
```

#### rastreabilidade.py
```
GET    /rastreabilidade/safra/{safra_id}/cadeia Cadeia completa semente→romaneio
GET    /rastreabilidade/safra/{safra_id}/relatorio-soja-plus Export Soja Plus
GET    /rastreabilidade/safra/{safra_id}/emissoes Emissões de carbono da safra (t CO2e/ha)
GET    /rastreabilidade/talhao/{talhao_id}/car-sobreposicao Verifica sobreposição com APP/RL
POST   /rastreabilidade/safra/{safra_id}/certificacao Solicita geração de relatório para certificação
```

### 6.3 Padrão de implementação de cada endpoint

```python
# Exemplo: POST /operacoes/ — use este padrão em TODOS os endpoints
@router.post(
    "/",
    response_model=OperacaoAgricolaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra operação agrícola no caderno de campo",
    description="""
    Registra uma operação realizada no talhão (plantio, aplicação de defensivo,
    adubação, etc.). Automaticamente:
    - Baixa insumos do estoque
    - Calcula custo da operação
    - Atualiza custo realizado da safra
    - Detecta carência de defensivos
    - Busca condições climáticas do momento (se lat/lng fornecidos)
    """,
)
async def criar_operacao(
    dados: OperacaoAgricolaCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("AGRICOLA_A2")),
    user: dict = Depends(require_role("agronomo", "admin", "operador")),
):
    svc = OperacaoService(session, tenant_id)
    operacao = await svc.criar(dados)
    # Task em background — não bloqueia a resposta
    background_tasks.add_task(
        verificar_alertas_pos_operacao,
        operacao_id=operacao.id,
        tenant_id=tenant_id,
    )
    return OperacaoAgricolaResponse.model_validate(operacao)
```

---

## 7. TASKS CELERY — IMPLEMENTE TODAS

Crie em `services/api_agricola/tasks/`:

```python
# tasks/ndvi_tasks.py
"""
Task: processar_ndvi_todos_talhoes
  - Schedule: diário às 06:00 (celery beat)
  - Para cada talhão ativo com safra em andamento:
    a. Verifica se já tem imagem dos últimos 5 dias
    b. Se não: chama NdviService.buscar_e_processar_sentinel2()
    c. Em caso de cobertura de nuvem > 20%: agenda retry em 2 dias
  - Prioridade: LOW (não bloqueia outras tasks)

Task: processar_ndvi_talhao (por talhão, acionada via endpoint)
  - Timeout: 300 segundos
  - Retry: 3 tentativas com backoff de 60s
  - Notifica usuário via WebSocket quando concluído

Task: verificar_alertas_ndvi
  - Schedule: após cada processamento de NDVI
  - Verifica queda > 15% em relação à média dos últimos 3 registros
  - Cria AlertaAgronomico se necessário
"""

# tasks/climatico_tasks.py
"""
Task: sincronizar_clima_todos_talhoes
  - Schedule: diário às 05:00
  - Para cada talhão ativo: chama ClimaticoService.sincronizar_clima_talhao()
  - Busca dados do dia anterior (D-1) — Open-Meteo Archive API
  - Batch de 50 talhões por vez para não sobrecarregar API

Task: previsao_clima_alertas
  - Schedule: diário às 07:00
  - Para cada safra em andamento: ClimaticoService.alerta_janela_aplicacao()
  - Envia alertas de geada com 72h de antecedência

Task: calcular_gdu_diario
  - Schedule: diário às 08:00, após sincronizar_clima
  - Para cada safra PLANTADA: atualiza GDU acumulado
  - Detecta transições de estágio fenológico e cria alertas
"""

# tasks/previsao_tasks.py
"""
Task: atualizar_previsoes_produtividade
  - Schedule: semanal às segundas, 09:00
  - Para cada safra ativa com dados suficientes: PrevisaoProdutividadeService.prever()
  - Dispara alerta se desvio vs meta > 15%

Task: treinar_modelos_mensalmente
  - Schedule: dia 1 de cada mês, 02:00
  - Para cada tenant com >= 3 safras fechadas:
    PrevisaoProdutividadeService.treinar_modelo()
  - Prioridade: LOWEST — roda em worker dedicado
"""
```

---

## 8. FRONTEND — PAGES E COMPONENTS

### 8.1 Estrutura de páginas

```
apps/web/app/(dashboard)/agricola/lavoura/
├── layout.tsx                            # Layout do módulo lavoura
├── page.tsx                              # Dashboard geral — lista de safras ativas
├── talhoes/
│   ├── page.tsx                          # Lista de talhões + mapa
│   └── [id]/
│       └── page.tsx                      # Detalhe do talhão + histórico
├── safras/
│   ├── [id]/
│   │   ├── page.tsx                      # Dashboard da safra
│   │   ├── operacoes/page.tsx            # Caderno de campo
│   │   ├── monitoramento/page.tsx        # Monitoramento fitossanitário
│   │   ├── ndvi/page.tsx                 # Mapas NDVI + variabilidade
│   │   ├── clima/page.tsx                # Dados climáticos + previsão
│   │   ├── custos/page.tsx               # Custo por saca + simulador
│   │   └── rastreabilidade/page.tsx      # Cadeia e relatórios
└── agronomo/
    └── page.tsx                          # Chat com Agrônomo Virtual
```

### 8.2 Components obrigatórios

```
apps/web/components/agricola/lavoura/
├── mapa-talhoes.tsx           # MapLibre — todos os talhões com polígonos + NDVI colormap
├── mapa-ndvi.tsx              # MapLibre — raster NDVI overlay + zonas de variabilidade
├── mapa-prescricao.tsx        # MapLibre — mapa de prescrição VRA
├── talhao-form.tsx            # Formulário de talhão com desenho de polígono no mapa
├── safra-dashboard.tsx        # Cards de KPIs da safra
├── caderno-campo-grid.tsx     # AG Grid de operações com filtros avançados
├── operacao-form.tsx          # Formulário de operação com insumos dinâmicos
├── monitoramento-form.tsx     # Form de monitoramento + upload foto
├── diagnostico-praga-card.tsx # Card de resultado do diagnóstico IA
├── ndvi-chart.tsx             # Recharts — série temporal de NDVI
├── clima-chart.tsx            # Recharts — precipitação + temperatura + GDU
├── custo-saca-card.tsx        # Card de custo em tempo real + ponto de equilíbrio
├── simulador-cenarios.tsx     # Tabela de cenários de preço interativa
├── agronomo-chat.tsx          # Interface de chat com streaming SSE
├── fenologico-timeline.tsx    # Timeline visual dos estágios fenológicos
└── alerta-badge.tsx           # Badge de alertas agronômicos
```

### 8.3 Implementação crítica — mapa-talhoes.tsx

```typescript
// components/agricola/lavoura/mapa-talhoes.tsx
"use client"
/**
 * Mapa interativo de talhões com:
 * - Polígonos de todos os talhões da fazenda
 * - Coloração por NDVI (verde escuro = alto, amarelo = médio, vermelho = baixo)
 * - Popup ao clicar: nome, área, NDVI atual, cultura da safra ativa
 * - Modo de desenho: permite criar/editar polígono do talhão
 * - Layer de imagem NDVI raster como overlay semitransparente
 * - Controle de opacidade do layer NDVI
 */
import maplibregl from "maplibre-gl"
import "maplibre-gl/dist/maplibre-gl.css"
import { useEffect, useRef, useState, useCallback } from "react"
import type { TalhaoResponse } from "@/types/agricola"

interface MapaTalhoesProps {
  talhoes: TalhaoResponse[]
  talhaoSelecionadoId?: string
  onTalhaoClick?: (talhao: TalhaoResponse) => void
  onPoligonoDesenho?: (geojson: GeoJSON.Polygon) => void // para o form de criação
  modoDesenho?: boolean
  ndviLayer?: boolean
}

export function MapaTalhoes({
  talhoes, talhaoSelecionadoId, onTalhaoClick, onPoligonoDesenho, modoDesenho = false, ndviLayer = true
}: MapaTalhoesProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<maplibregl.Map | null>(null)

  useEffect(() => {
    if (!mapContainer.current || map.current) return

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
      // Alternativa satélite gratuita: MapTiler Satellite (requer key gratuita)
      // ou: Bing Maps via raster tiles (requer key gratuita)
      center: [-52.0, -15.0],  // Centro do Brasil
      zoom: 4,
    })

    map.current.on("load", () => {
      // Adiciona source de talhões como GeoJSON
      map.current!.addSource("talhoes", {
        type: "geojson",
        data: talhoesToFeatureCollection(talhoes),
      })

      // Layer de preenchimento com cor baseada em NDVI
      map.current!.addLayer({
        id: "talhoes-fill",
        type: "fill",
        source: "talhoes",
        paint: {
          "fill-color": [
            "interpolate", ["linear"],
            ["coalesce", ["get", "ndvi_atual"], 0],
            0.0, "#d73027",   // baixo — vermelho
            0.3, "#fee08b",   // médio-baixo — amarelo
            0.5, "#1a9850",   // médio — verde
            0.8, "#006837",   // alto — verde escuro
          ],
          "fill-opacity": 0.6,
        },
      })

      // Layer de borda
      map.current!.addLayer({
        id: "talhoes-outline",
        type: "line",
        source: "talhoes",
        paint: {
          "line-color": "#FFFFFF",
          "line-width": ["case", ["==", ["get", "id"], talhaoSelecionadoId ?? ""], 3, 1],
          "line-opacity": 0.8,
        },
      })

      // Layer de labels
      map.current!.addLayer({
        id: "talhoes-labels",
        type: "symbol",
        source: "talhoes",
        layout: {
          "text-field": ["concat", ["get", "nome"], "\n", ["get", "area_ha_fmt"], " ha"],
          "text-size": 11,
          "text-font": ["Open Sans Regular"],
        },
        paint: {
          "text-color": "#FFFFFF",
          "text-halo-color": "#000000",
          "text-halo-width": 1,
        },
      })

      // Click handler
      map.current!.on("click", "talhoes-fill", (e) => {
        const feature = e.features?.[0]
        if (!feature) return
        const talhao = talhoes.find(t => t.id === feature.properties?.id)
        if (talhao) onTalhaoClick?.(talhao)
      })

      // Cursor pointer
      map.current!.on("mouseenter", "talhoes-fill", () => {
        map.current!.getCanvas().style.cursor = "pointer"
      })
      map.current!.on("mouseleave", "talhoes-fill", () => {
        map.current!.getCanvas().style.cursor = ""
      })

      // Fit bounds para mostrar todos os talhões
      if (talhoes.length > 0) {
        const bounds = calcularBounds(talhoes)
        map.current!.fitBounds(bounds, { padding: 40 })
      }
    })

    return () => map.current?.remove()
  }, [])

  // Atualiza dados quando talhoes muda
  useEffect(() => {
    const source = map.current?.getSource("talhoes") as maplibregl.GeoJSONSource
    if (source) {
      source.setData(talhoesToFeatureCollection(talhoes))
    }
  }, [talhoes])

  return (
    <div
      ref={mapContainer}
      className="w-full h-full rounded-lg overflow-hidden"
      style={{ minHeight: "400px" }}
    />
  )
}

function talhoesToFeatureCollection(talhoes: TalhaoResponse[]): GeoJSON.FeatureCollection {
  return {
    type: "FeatureCollection",
    features: talhoes
      .filter(t => t.geometria_geojson)
      .map(t => ({
        type: "Feature",
        geometry: t.geometria_geojson as GeoJSON.Polygon,
        properties: {
          id: t.id,
          nome: t.nome,
          area_ha_fmt: t.area_efetiva_ha?.toFixed(1) ?? "?",
          ndvi_atual: t.ndvi_atual?.ndvi_medio ?? null,
          cultura: t.safra_ativa?.cultura ?? null,
        },
      })),
  }
}
```

### 8.4 Implementação crítica — agronomo-chat.tsx

```typescript
// components/agricola/lavoura/agronomo-chat.tsx
"use client"
/**
 * Chat com streaming SSE com o Agrônomo Virtual.
 * O LLM tem contexto completo da safra/talhão selecionado.
 * Suporta:
 * - Texto livre
 * - Upload de foto para diagnóstico de praga (envia para /agronomo/diagnostico-praga)
 * - Respostas em streaming (Server-Sent Events)
 * - Histórico de conversa salvo localmente (Zustand)
 * - Badge com cultura e estágio fenológico atual do contexto
 */
import { useState, useRef, useCallback } from "react"
import { useAppStore } from "@/lib/stores/app-store"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface AgronomoChatProps {
  safraId?: string
  talhaoId?: string
}

export function AgronomoChat({ safraId, talhaoId }: AgronomoChatProps) {
  const [mensagens, setMensagens] = useState<Mensagem[]>([])
  const [inputText, setInputText] = useState("")
  const [isStreaming, setIsStreaming] = useState(false)
  const abortControllerRef = useRef<AbortController | null>(null)

  const enviarMensagem = useCallback(async (texto: string) => {
    if (!texto.trim() || isStreaming) return

    const novaMensagem: Mensagem = { role: "user", content: texto, timestamp: new Date() }
    setMensagens(prev => [...prev, novaMensagem])
    setInputText("")
    setIsStreaming(true)

    // Mensagem placeholder do assistente
    const msgId = Date.now().toString()
    setMensagens(prev => [...prev, { id: msgId, role: "assistant", content: "", timestamp: new Date() }])

    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch("/api/proxy/agricola/agronomo/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem: texto, safra_id: safraId, talhao_id: talhaoId }),
        signal: abortControllerRef.current.signal,
      })

      // Lê o stream SSE
      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let acumulado = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split("\n")

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6)
            if (data === "[DONE]") break
            try {
              const parsed = JSON.parse(data)
              acumulado += parsed.texto
              // Atualiza mensagem do assistente em tempo real
              setMensagens(prev => prev.map(m =>
                m.id === msgId ? { ...m, content: acumulado } : m
              ))
            } catch { /* ignora chunks inválidos */ }
          }
        }
      }
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setMensagens(prev => prev.map(m =>
          m.id === msgId ? { ...m, content: "Erro ao conectar com o Agrônomo Virtual." } : m
        ))
      }
    } finally {
      setIsStreaming(false)
    }
  }, [safraId, talhaoId, isStreaming])

  // Renderização — implemente o JSX completo com:
  // - Lista de mensagens com markdown renderizado (use react-markdown)
  // - Input de texto com Ctrl+Enter para enviar
  // - Botão de upload de foto (para diagnóstico de praga)
  // - Indicador de streaming (dots animation)
  // - Botão de cancelar streaming
  // - Badge de contexto: "Safra: Soja 2024/25 | Talhão 3 | R1"
  return (
    <div className="flex flex-col h-full">
      {/* implemente o JSX */}
    </div>
  )
}
```

### 8.5 TanStack Query hooks

```typescript
// Crie em apps/web/hooks/agricola/use-lavoura.ts

// Padrão de query keys para o módulo lavoura
export const lavourKeys = {
  all: ["lavoura"] as const,
  talhoes: (tenantId: string, fazendaId?: string) =>
    [...lavourKeys.all, "talhoes", tenantId, fazendaId] as const,
  talhao: (id: string) => [...lavourKeys.all, "talhao", id] as const,
  safras: (tenantId: string, filters: SafraFilters) =>
    [...lavourKeys.all, "safras", tenantId, filters] as const,
  safra: (id: string) => [...lavourKeys.all, "safra", id] as const,
  safraDashboard: (id: string) => [...lavourKeys.all, "safra-dashboard", id] as const,
  ndvi: (talhaoId: string) => [...lavourKeys.all, "ndvi", talhaoId] as const,
  clima: (talhaoId: string) => [...lavourKeys.all, "clima", talhaoId] as const,
  custoSaca: (safraId: string) => [...lavourKeys.all, "custo-saca", safraId] as const,
  previsao: (safraId: string) => [...lavourKeys.all, "previsao", safraId] as const,
  alertas: (tenantId: string) => [...lavourKeys.all, "alertas", tenantId] as const,
}

// Implemente os hooks:
// useTalhoes(fazendaId) — staleTime: 10min
// useTalhao(id)
// useSafras(filters) — staleTime: 5min
// useSafraDashboard(safraId) — staleTime: 2min (dados em tempo real)
// useNdviHistorico(talhaoId)
// useClimaAtual(talhaoId) — staleTime: 30min
// useCustoSaca(safraId) — staleTime: 5min
// usePrevisaoProdutividade(safraId) — staleTime: 1h
// useAlertasAtivos() — staleTime: 1min, refetch automático
// useOperacoes(safraId, filters)
// useMonitoramento(safraId)
```

---

## 9. TASKS CELERY — CONFIGURAÇÃO COMPLETA

```python
# celery_config.py — adicionar ao celeryconfig existente
from celery.schedules import crontab

beat_schedule = {
    # NDVI — diário às 06:00
    "processar-ndvi-todos-talhoes": {
        "task": "api_agricola.tasks.ndvi_tasks.processar_ndvi_todos_talhoes",
        "schedule": crontab(hour=6, minute=0),
        "options": {"queue": "low_priority"},
    },
    # Clima — diário às 05:00
    "sincronizar-clima-todos-talhoes": {
        "task": "api_agricola.tasks.climatico_tasks.sincronizar_clima_todos_talhoes",
        "schedule": crontab(hour=5, minute=0),
        "options": {"queue": "default"},
    },
    # Previsão climática e alertas — diário às 07:00
    "previsao-clima-alertas": {
        "task": "api_agricola.tasks.climatico_tasks.previsao_clima_alertas",
        "schedule": crontab(hour=7, minute=0),
        "options": {"queue": "default"},
    },
    # GDU e estágio fenológico — diário às 08:00
    "calcular-gdu-diario": {
        "task": "api_agricola.tasks.climatico_tasks.calcular_gdu_diario",
        "schedule": crontab(hour=8, minute=0),
        "options": {"queue": "default"},
    },
    # Previsão de produtividade — semanal às segundas
    "atualizar-previsoes-produtividade": {
        "task": "api_agricola.tasks.previsao_tasks.atualizar_previsoes_produtividade",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),
        "options": {"queue": "default"},
    },
    # Treinamento de modelos — mensal no dia 1
    "treinar-modelos-ml": {
        "task": "api_agricola.tasks.previsao_tasks.treinar_modelos_mensalmente",
        "schedule": crontab(hour=2, minute=0, day_of_month=1),
        "options": {"queue": "ml_training"},  # worker dedicado com GPU se disponível
    },
}

# Filas
task_routes = {
    "api_agricola.tasks.ndvi_tasks.*":       {"queue": "low_priority"},
    "api_agricola.tasks.climatico_tasks.*":  {"queue": "default"},
    "api_agricola.tasks.previsao_tasks.treinar_modelos_mensalmente": {"queue": "ml_training"},
    "api_agricola.tasks.*":                  {"queue": "default"},
}
```

---

## 10. TESTES — IMPLEMENTE COBERTURA MÍNIMA

### 10.1 Estrutura obrigatória
```
services/api_agricola/tests/
├── conftest.py                    # Fixtures: db_session, client, tenant_id, factories
├── unit/
│   ├── test_talhao_service.py
│   ├── test_safra_service.py
│   ├── test_operacao_service.py
│   ├── test_ndvi_service.py
│   ├── test_climatico_service.py
│   ├── test_custo_saca_service.py
│   └── test_previsao_service.py
└── integration/
    ├── test_talhoes_router.py
    ├── test_safras_router.py
    ├── test_operacoes_router.py
    ├── test_monitoramento_router.py
    └── test_tenant_isolation.py   # testes de segurança — obrigatórios
```

### 10.2 Testes de tenant isolation — OBRIGATÓRIOS

```python
# tests/integration/test_tenant_isolation.py
"""
Implemente os seguintes testes de segurança — TODOS DEVEM PASSAR:

1. test_talhao_tenant_a_invisivel_para_tenant_b
   - Cria talhão no tenant A
   - Faz GET /talhoes/ autenticado como tenant B
   - Asserta: talhão do tenant A não aparece na resposta

2. test_safra_nao_pode_referenciar_talhao_de_outro_tenant
   - Tenant B tenta criar safra com talhao_id pertencente ao tenant A
   - Asserta: retorna 404 (não 403 — não devemos confirmar existência)

3. test_operacao_nao_pode_baixar_estoque_de_outro_tenant
   - Tenant B tenta criar operação com insumo_id do tenant A
   - Asserta: retorna 404

4. test_ndvi_apenas_visivel_para_tenant_correto
   - GET /ndvi/{talhao_id_do_tenant_a} autenticado como tenant B
   - Asserta: retorna 404

5. test_rls_previne_vazamento_via_sql_injection
   - Tenta passar tenant_id manipulado no header x-tenant-id
   - Asserta: apenas dados do tenant do JWT são retornados
"""
```

### 10.3 Testes unitários críticos

```python
# Implemente pelo menos estes casos em cada service:

# TalhaoService:
# - test_criar_talhao_com_geometria_calcula_area_automaticamente
# - test_criar_talhao_sem_geometria_usa_area_manual
# - test_criar_talhao_sem_geometria_nem_area_manual_raises_error
# - test_sobreposicao_entre_talhoes_retorna_percentual

# SafraService:
# - test_criar_safra_calcula_data_colheita_prevista
# - test_criar_safra_duplicada_mesmo_talhao_ano_cultura_raises_error
# - test_transicao_status_invalida_raises_error (ex: PLANEJADA→COLHIDA)
# - test_fechar_safra_agrega_romaneios_corretamente
# - test_calcular_gdu_acumulado_retorna_soma_correta

# OperacaoService:
# - test_criar_operacao_baixa_estoque_corretamente
# - test_criar_operacao_calcula_custo_total_dos_insumos
# - test_defensivo_com_carencia_gera_data_reentrada

# CustoSacaService:
# - test_custo_por_saca_calculo_correto
# - test_ponto_equilibrio_com_cotacao_atual
# - test_simulador_cenarios_retorna_resultados_para_cada_preco

# ClimaticoService:
# - test_calcular_gdu_dia_temperatura_acima_base
# - test_calcular_gdu_dia_temperatura_abaixo_base_retorna_zero
# - test_janela_aplicacao_detecta_condicoes_favoraveis
# - test_risco_geada_detectado_para_temp_abaixo_2c
```

---

## 11. INTEGRAÇÕES EXTERNAS — IMPLEMENTAÇÃO DETALHADA

### 11.1 Sentinel-2 / Copernicus Data Space
```python
"""
BASE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1"

Autenticação: OAuth2 client credentials
  URL: https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token
  grant_type: client_credentials
  client_id: {configurado no Vault}
  client_secret: {configurado no Vault}

Buscar imagens disponíveis:
  GET {BASE_URL}/Products?$filter=
      Collection/Name eq 'SENTINEL-2'
      and ContentDate/Start gt {data_inicio}
      and ContentDate/End lt {data_fim}
      and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 20.00)
      and OData.CSC.Intersects(area=geography'SRID=4326;{WKT_GEOMETRIA_TALHAO}')
      &$orderby=ContentDate/Start desc
      &$top=3

Download do produto:
  GET {BASE_URL}/Products({product_id})/$value
  → Streaming download para /tmp/{product_id}.zip
  → Extrai apenas as bandas B04 e B08 do produto S2L2A

Processamento NDVI com rasterio:
  import rasterio
  import numpy as np
  from rasterio.mask import mask
  from rasterio.warp import reproject, Resampling

  with rasterio.open(path_b04) as red, rasterio.open(path_b08) as nir:
      # Recorta pelo polígono do talhão
      red_data, _ = mask(red, [geometria_shapely], crop=True, nodata=0)
      nir_data, _ = mask(nir, [geometria_shapely], crop=True, nodata=0)

      # Calcula NDVI (evita divisão por zero)
      np.seterr(divide='ignore', invalid='ignore')
      ndvi = np.where(
          (nir_data + red_data) == 0,
          np.nan,
          (nir_data.astype(float) - red_data.astype(float)) /
          (nir_data.astype(float) + red_data.astype(float))
      )

      # Estatísticas (ignora NaN e borda)
      ndvi_valid = ndvi[~np.isnan(ndvi) & (ndvi >= -1) & (ndvi <= 1)]
      ndvi_medio = float(np.mean(ndvi_valid))
      ndvi_desvio = float(np.std(ndvi_valid))
"""
```

### 11.2 Open-Meteo (Clima)
```python
"""
BASE_URL = "https://archive-api.open-meteo.com/v1/archive"  # histórico
BASE_URL_FORECAST = "https://api.open-meteo.com/v1/forecast"  # previsão

Sem API key — gratuito até 10k requests/dia

Variáveis diárias a buscar:
  temperature_2m_max, temperature_2m_min, temperature_2m_mean,
  precipitation_sum, et0_fao_evapotranspiration,
  windspeed_10m_max, windspeed_10m_mean,
  shortwave_radiation_sum, relative_humidity_2m_mean,
  weathercode (WMO code para condição)

Cálculo de GDU (Graus-Dia Úteis):
  Temperatura base por cultura:
    soja: 10°C, milho: 10°C, trigo: 7°C, algodao: 15°C, cana: 18°C

  GDU_dia = max(0, ((Tmax + Tmin) / 2) - T_base)
  GDU_acumulado = SUM(GDU_dia) desde data_plantio_real

Estimativa de estágio fenológico (soja):
  V1: GDU >= 90   V3: >= 210  V6: >= 360
  R1: >= 490      R3: >= 630  R5: >= 750  R7: >= 900  R8: >= 1000

Implementar com httpx AsyncClient + cache Redis (TTL 6h para histórico, 1h para forecast):
  async with httpx.AsyncClient(timeout=30) as client:
      response = await client.get(BASE_URL, params=params)
      response.raise_for_status()
"""
```

### 11.3 Ollama (LLM local)
```python
"""
BASE_URL = settings.ollama_base_url  # http://ollama:11434

Modelos disponíveis (em ordem de preferência):
  1. llama3.1:8b     — melhor custo-benefício para agro
  2. qwen2.5:14b     — melhor para português
  3. mistral:7b      — mais rápido, qualidade ligeiramente inferior

Chat com streaming:
  POST {BASE_URL}/api/chat
  {
    "model": "llama3.1:8b",
    "messages": [
      {"role": "system", "content": SYSTEM_PROMPT},
      {"role": "user", "content": mensagem}
    ],
    "stream": true,
    "options": {
      "temperature": 0.3,
      "num_predict": 1000,
      "top_p": 0.9
    }
  }

  Iterar sobre o stream:
  async for line in response.aiter_lines():
      if line:
          chunk = json.loads(line)
          if not chunk.get("done"):
              yield chunk["message"]["content"]

Embeddings para RAG:
  POST {BASE_URL}/api/embeddings
  {"model": "nomic-embed-text", "prompt": texto}
  → response["embedding"] — vetor float[] para pgvector
"""
```

---

## 12. ORDEM DE IMPLEMENTAÇÃO — EXECUTE NESTA SEQUÊNCIA

```
FASE 1 — FUNDAÇÃO (dias 1-3)
  [ ] Migrations 001-005 (talhoes, cultivares, safras, operacoes, insumos_operacao)
  [ ] Models SQLAlchemy: Talhao, Safra, OperacaoAgricola, InsumoOperacao
  [ ] Schemas Pydantic: Create, Update, Response para Talhao e Safra
  [ ] TalhaoService + SafraService (sem features avançadas)
  [ ] Routers: talhoes.py e safras.py (CRUD básico)
  [ ] Testes unitários + integração para Talhao e Safra
  [ ] Frontend: mapa-talhoes.tsx, talhao-form.tsx, lista de safras

FASE 2 — CADERNO DE CAMPO (dias 4-6)
  [ ] Schemas: OperacaoAgricolaCreate com insumos aninhados
  [ ] OperacaoService completo (custo, estoque, carência)
  [ ] Router operacoes.py
  [ ] Migration 006 (monitoramento_pragas)
  [ ] MonitoramentoService + router monitoramento.py
  [ ] Migration 007 (romaneios_colheita)
  [ ] RomaneioService + router romaneios.py
  [ ] Frontend: caderno-campo-grid.tsx, operacao-form.tsx
  [ ] Testes obrigatórios + tenant isolation

FASE 3 — DADOS AMBIENTAIS (dias 7-10)
  [ ] Migration 008 (ndvi_talhao — TimescaleDB)
  [ ] Migration 012 (dados_climaticos_talhao — TimescaleDB)
  [ ] NdviService + ClimaticoService
  [ ] Routers: ndvi.py, climatico.py
  [ ] Tasks Celery: processar_ndvi_todos_talhoes, sincronizar_clima_todos_talhoes
  [ ] Frontend: mapa-ndvi.tsx, ndvi-chart.tsx, clima-chart.tsx

FASE 4 — INTELIGÊNCIA (dias 11-15)
  [ ] Migration 009 (previsoes_produtividade)
  [ ] Migration 010 (alertas_agronomicos)
  [ ] AgronomoVirtualService (LLM streaming + diagnóstico YOLO)
  [ ] PrevisaoProdutividadeService (XGBoost + features)
  [ ] CustoSacaService (custo por saca em tempo real)
  [ ] Routers: agronomo.py, previsoes.py, custos.py
  [ ] Frontend: agronomo-chat.tsx, custo-saca-card.tsx, simulador-cenarios.tsx

FASE 5 — RASTREABILIDADE E PREMIUM (dias 16-18)
  [ ] Migration 011 (analises_solo)
  [ ] AnaliseSoloService + integração com recomendação de adubação
  [ ] Router rastreabilidade.py (cadeia completa, emissões carbono)
  [ ] Migration 013 (mapa_prescricao para VRA)
  [ ] MapaPrescricaoService + mapa-prescricao.tsx
  [ ] Testes de todos os services + cobertura mínima
  [ ] Revisão final de segurança + tenant isolation

FASE 6 — POLISH (dias 19-20)
  [ ] Dashboard principal do módulo (safra-dashboard.tsx com todos os KPIs)
  [ ] Alertas em tempo real (WebSocket ou polling 1min)
  [ ] Testes E2E Playwright para fluxos críticos
  [ ] Documentação OpenAPI (revisar descriptions de todos endpoints)
  [ ] Performance: verificar N+1 queries com explain analyze
```

---

## 13. VARIÁVEIS DE AMBIENTE NECESSÁRIAS

Adicione ao HashiCorp Vault / .env.local:

```bash
# Sentinel-2 / Copernicus Data Space
COPERNICUS_CLIENT_ID=...
COPERNICUS_CLIENT_SECRET=...

# Open-Meteo (sem key — mas registrar para limites maiores)
OPEN_METEO_API_URL=https://api.open-meteo.com/v1

# Ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL_CHAT=llama3.1:8b
OLLAMA_MODEL_EMBED=nomic-embed-text

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000
MLFLOW_EXPERIMENT_NAME=agrosass-produtividade

# MinIO — buckets do módulo lavoura
MINIO_BUCKET_NDVI=agro-mapas
MINIO_BUCKET_LAUDOS=agro-laudos
MINIO_BUCKET_FOTOS=agro-midia

# Modelos ML
MODELS_PATH=/app/models
YOLO_MODEL_PATH=/app/models/yolo_pragas_br_v1.onnx
```

---

## 14. CHECKLIST DE VALIDAÇÃO — ANTES DE CONSIDERAR CONCLUÍDO

```
SEGURANÇA:
  [ ] Todos endpoints têm Depends(require_module("AGRICOLA_A2"))
  [ ] Todos endpoints têm Depends(require_role(...)) apropriado
  [ ] Nenhuma query sem filtro de tenant_id
  [ ] RLS aplicado em todas as novas tabelas
  [ ] Nenhum dado sensível em logs

BANCO:
  [ ] Todas as migrations têm downgrade() funcional
  [ ] Índices críticos criados com CONCURRENTLY
  [ ] Hypertables TimescaleDB configuradas com compressão
  [ ] Continuous aggregates com refresh policy

INTEGRAÇÕES:
  [ ] Sentinel-2: download e processamento NDVI operacional
  [ ] Open-Meteo: sync histórico e forecast operacional
  [ ] Ollama: chat streaming e embeddings operacionais
  [ ] MinIO: upload/download de rasters e fotos operacional
  [ ] Celery: todas as tasks agendadas no beat schedule

TESTES:
  [ ] pytest --cov >= 80% total
  [ ] Services >= 90% de cobertura
  [ ] Todos os testes de tenant isolation passando
  [ ] Sem testes flakey (dependência de ordem ou estado externo)

FRONTEND:
  [ ] Mapa com polígonos de talhões renderizando
  [ ] NDVI colormap funcional no mapa
  [ ] Chat do Agrônomo Virtual com streaming visível
  [ ] Custo por saca atualizado em tempo real
  [ ] Alertas agronômicos exibidos com prioridade
  [ ] Formulário de operação baixa estoque corretamente

PERFORMANCE:
  [ ] Listagem de talhões com 1000+ registros < 500ms
  [ ] Dashboard de safra (agregação completa) < 2s
  [ ] Chat streaming: primeiro token < 3s
  [ ] Processamento NDVI por talhão < 120s (timeout da task)
```

---

*Prompt gerado para o projeto AgroSaaS — Módulo Lavoura (AGRICOLA_A2)*
*Stack: Python 3.12 · FastAPI · PostgreSQL 16 + PostGIS + TimescaleDB · Next.js 16 · K3s*
