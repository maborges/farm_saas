-- Verificar tipos de operação cadastrados no banco
SELECT id, tipo_operacao, fases_permitidas, descricao 
FROM agricola_operacao_tipo_fase 
ORDER BY tipo_operacao;

-- Contagem
SELECT COUNT(*) as total FROM agricola_operacao_tipo_fase;
