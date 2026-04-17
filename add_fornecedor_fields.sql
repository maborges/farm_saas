-- Adicionar campos ao Fornecedor
-- Executar: psql -U <user> -d <db> -f add_fornecedor_fields.sql

BEGIN;

-- Adicionar coluna email
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'compras_fornecedores' AND column_name = 'email'
    ) THEN
        ALTER TABLE compras_fornecedores ADD COLUMN email VARCHAR(100);
    END IF;
END $$;

-- Adicionar coluna telefone
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'compras_fornecedores' AND column_name = 'telefone'
    ) THEN
        ALTER TABLE compras_fornecedores ADD COLUMN telefone VARCHAR(20);
    END IF;
END $$;

-- Adicionar coluna condicoes_pagamento
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'compras_fornecedores' AND column_name = 'condicoes_pagamento'
    ) THEN
        ALTER TABLE compras_fornecedores ADD COLUMN condicoes_pagamento VARCHAR(100);
    END IF;
END $$;

-- Adicionar coluna prazo_entrega_dias
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'compras_fornecedores' AND column_name = 'prazo_entrega_dias'
    ) THEN
        ALTER TABLE compras_fornecedores ADD COLUMN prazo_entrega_dias INTEGER;
    END IF;
END $$;

-- Adicionar coluna avaliacao
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'compras_fornecedores' AND column_name = 'avaliacao'
    ) THEN
        ALTER TABLE compras_fornecedores ADD COLUMN avaliacao FLOAT;
    END IF;
END $$;

-- Atualizar alembic_version
INSERT INTO alembic_version (version_num) VALUES ('add_fornecedor_fields') ON CONFLICT DO NOTHING;

COMMIT;
