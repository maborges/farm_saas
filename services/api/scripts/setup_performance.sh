#!/bin/bash
# Setup de Performance - PostgreSQL
# Configura pg_stat_statements e query logging

DB_HOST="192.168.0.2"
DB_NAME="farms"
DB_USER="borgus"
DB_PASS="numsey01"

export PGPASSWORD=$DB_PASS

echo "=========================================="
echo "🚀 Setup de Performance - PostgreSQL"
echo "=========================================="
echo ""

# 1. Testar conexão
echo "1️⃣  Testando conexão com o banco de dados..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1;" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Conexão estabelecida com sucesso!"
else
    echo "❌ Erro ao conectar no banco de dados"
    exit 1
fi

echo ""

# 2. Criar pg_stat_statements (se não existir)
echo "2️⃣  Configurando pg_stat_statements..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ pg_stat_statements configurado!"
else
    echo "⚠️  pg_stat_statements pode já existir ou requerer superuser"
fi

echo ""

# 3. Habilitar query logging
echo "3️⃣  Habilitando query logging (>500ms)..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "ALTER SYSTEM SET log_min_duration_statement = 500;" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Query logging habilitado!"
else
    echo "⚠️  Pode requerer privilégios de superuser"
fi

echo ""

# 4. Recarregar configuração
echo "4️⃣  Recarregando configuração..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT pg_reload_conf();" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Configuração recarregada!"
else
    echo "⚠️  Erro ao recarregar configuração"
fi

echo ""

# 5. Verificar configurações
echo "5️⃣  Verificando configurações..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SHOW log_min_duration_statement;" 2>&1

echo ""

# 6. Verificar se pg_stat_statements está ativo
echo "6️⃣  Verificando pg_stat_statements..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) as total_queries FROM pg_stat_statements;" 2>&1

echo ""
echo "=========================================="
echo "✅ Setup concluído!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Executar script de baseline: python scripts/performance_baseline.py"
echo "2. Analisar queries lentas no relatório"
echo ""

unset PGPASSWORD
