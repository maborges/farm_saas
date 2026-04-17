-- ============================================================
-- Script SQL gerado a partir das migrations:
--   1. commodity_refactor_classificacoes_cotacoes_qualidade
--   2. add_produto_colhido_and_romaneio_commodity_id
--
-- Executar: psql -U <user> -d <db> -f migrations_manual.sql
-- ============================================================

BEGIN;

-- ---------------------------------------------------------------
-- 1. Tabela cadastros_commodities_cotacoes (nova)
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cadastros_commodities_cotacoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commodity_id UUID NOT NULL REFERENCES cadastros_commodities(id) ON DELETE CASCADE,
    data TIMESTAMP WITH TIME ZONE NOT NULL,
    preco NUMERIC(12, 4) NOT NULL,
    moeda VARCHAR(3) NOT NULL DEFAULT 'BRL',
    fonte VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_cotacao_commodity_data_fonte UNIQUE (commodity_id, data, fonte)
);

CREATE INDEX IF NOT EXISTS ix_cadastros_commodities_cotacoes_commodity_id
    ON cadastros_commodities_cotacoes(commodity_id);
CREATE INDEX IF NOT EXISTS ix_cadastros_commodities_cotacoes_data
    ON cadastros_commodities_cotacoes(data);


-- ---------------------------------------------------------------
-- 2. Adicionar campos de qualidade a cadastros_commodities
-- ---------------------------------------------------------------
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'cadastros_commodities' AND column_name = 'umidade_padrao_pct'
    ) THEN
        ALTER TABLE cadastros_commodities ADD COLUMN umidade_padrao_pct FLOAT;
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'cadastros_commodities' AND column_name = 'impureza_padrao_pct'
    ) THEN
        ALTER TABLE cadastros_commodities ADD COLUMN impureza_padrao_pct FLOAT;
    END IF;
END $$;


-- ---------------------------------------------------------------
-- 3. UniqueConstraint tenant_id + nome
-- ---------------------------------------------------------------
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_commodity_tenant_nome'
    ) THEN
        ALTER TABLE cadastros_commodities
            ADD CONSTRAINT uq_commodity_tenant_nome UNIQUE (tenant_id, nome);
    END IF;
END $$;


-- ---------------------------------------------------------------
-- 4. Tornar codigo NOT NULL e popular nulos
-- ---------------------------------------------------------------
UPDATE cadastros_commodities
SET codigo = UPPER(REPLACE(nome, ' ', '_'))
WHERE codigo IS NULL OR codigo = '';

ALTER TABLE cadastros_commodities
    ALTER COLUMN codigo SET NOT NULL;


-- ---------------------------------------------------------------
-- 5. commodity_id em romaneios_colheita
-- ---------------------------------------------------------------
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'romaneios_colheita' AND column_name = 'commodity_id'
    ) THEN
        ALTER TABLE romaneios_colheita
            ADD COLUMN commodity_id UUID;
        ALTER TABLE romaneios_colheita
            ADD CONSTRAINT fk_romaneio_commodity
            FOREIGN KEY (commodity_id)
            REFERENCES cadastros_commodities(id)
            ON DELETE SET NULL;
        CREATE INDEX ix_romaneios_colheita_commodity_id
            ON romaneios_colheita(commodity_id);
    END IF;
END $$;

-- Popular commodity_id a partir da safra
UPDATE romaneios_colheita r
SET commodity_id = s.commodity_id
FROM safras s
WHERE r.safra_id = s.id
  AND r.commodity_id IS NULL;


-- ---------------------------------------------------------------
-- 6. Tabela agricola_produtos_colhidos
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agricola_produtos_colhidos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    safra_id UUID NOT NULL REFERENCES safras(id) ON DELETE CASCADE,
    talhao_id UUID NOT NULL REFERENCES cadastros_areas_rurais(id) ON DELETE CASCADE,
    romaneio_id UUID REFERENCES romaneios_colheita(id) ON DELETE SET NULL,
    commodity_id UUID NOT NULL REFERENCES cadastros_commodities(id) ON DELETE CASCADE,
    classificacao_id UUID REFERENCES cadastros_commodities_classificacoes(id) ON DELETE SET NULL,

    quantidade NUMERIC(14, 3) NOT NULL,
    unidade VARCHAR(20) NOT NULL,
    peso_liquido_kg NUMERIC(14, 3) NOT NULL,

    umidade_pct NUMERIC(5, 2),
    impureza_pct NUMERIC(5, 2),
    avariados_pct NUMERIC(5, 2),
    ardidos_pct NUMERIC(5, 2),
    quebrados_pct NUMERIC(5, 2),

    destino VARCHAR(30),
    armazem_id UUID,

    data_entrada DATE NOT NULL,
    data_saida_prevista DATE,

    nf_origem VARCHAR(50),
    observacoes TEXT,
    dados_extras JSONB,

    status VARCHAR(20) NOT NULL DEFAULT 'ARMAZENADO',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_agricola_produtos_colhidos_tenant_id
    ON agricola_produtos_colhidos(tenant_id);
CREATE INDEX IF NOT EXISTS ix_agricola_produtos_colhidos_safra_id
    ON agricola_produtos_colhidos(safra_id);
CREATE INDEX IF NOT EXISTS ix_agricola_produtos_colhidos_talhao_id
    ON agricola_produtos_colhidos(talhao_id);
CREATE INDEX IF NOT EXISTS ix_agricola_produtos_colhidos_romaneio_id
    ON agricola_produtos_colhidos(romaneio_id);
CREATE INDEX IF NOT EXISTS ix_agricola_produtos_colhidos_commodity_id
    ON agricola_produtos_colhidos(commodity_id);
CREATE INDEX IF NOT EXISTS ix_agricola_produtos_colhidos_classificacao_id
    ON agricola_produtos_colhidos(classificacao_id);
CREATE INDEX IF NOT EXISTS ix_agricola_produtos_colhidos_status
    ON agricola_produtos_colhidos(status);


-- ---------------------------------------------------------------
-- 7. Atualizar alembic_version para registrar as migrations
-- ---------------------------------------------------------------
INSERT INTO alembic_version (version_num)
VALUES ('produto_colhido_v1')
ON CONFLICT DO NOTHING;

COMMIT;

-- FIM DO SCRIPT
