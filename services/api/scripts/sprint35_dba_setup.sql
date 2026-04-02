-- ============================================================
-- Sprint 35 - Performance Setup
-- ============================================================
-- Script para DBA habilitar monitoring de performance
-- Data: 2026-03-31
-- ============================================================

-- 1. Habilitar pg_stat_statements
-- ============================================================
-- Esta extensão permite monitorar todas as queries executadas
-- e identificar as queries mais lentas do sistema

CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Verificar se foi instalado com sucesso
SELECT * FROM pg_stat_statements LIMIT 1;

-- 2. Habilitar Query Logging
-- ============================================================
-- Loga todas as queries que demoram mais de 500ms
-- Essencial para identificar problemas de performance

ALTER SYSTEM SET log_min_duration_statement = 500;

-- Recarregar configuração
SELECT pg_reload_conf();

-- Verificar configuração
SHOW log_min_duration_statement;
-- Deve retornar: 500

-- 3. Configurações Adicionais (Opcional)
-- ============================================================

-- Habilitar auto_explain para queries lentas
-- Isso gera o EXPLAIN ANALYZE automaticamente nos logs
LOAD 'auto_explain';
SET auto_explain.log_min_duration = '500ms';
SET auto_explain.log_analyze = 'on';
SET auto_explain.log_buffers = 'on';

-- Verificar configurações atuais
SELECT name, setting 
FROM pg_settings 
WHERE name IN (
    'log_min_duration_statement',
    'shared_buffers',
    'work_mem',
    'effective_cache_size'
);

-- 4. Verificar Status
-- ============================================================

-- Verificar se pg_stat_statements está ativo
SELECT COUNT(*) as total_queries FROM pg_stat_statements;

-- Verificar tamanho do banco
SELECT pg_size_pretty(pg_database_size(current_database()));

-- ============================================================
-- FIM DO SCRIPT
-- ============================================================
-- Após executar este script:
-- 1. O monitoring de performance estará ativo
-- 2. Queries > 500ms serão logadas
-- 3. O script performance_baseline.py coletará métricas completas
-- ============================================================
