#!/bin/bash

# Script de Inicialização do Backend AgroSaaS

echo "🚀 Iniciando Backend AgroSaaS..."
echo ""

# Verificar se está na pasta correta
cd /opt/lampp/htdocs/farm/services/api

# Verificar se existe .venv
if [ -d ".venv" ]; then
    echo "✅ Ativando ambiente virtual..."
    source .venv/bin/activate
else
    echo "⚠️  Ambiente virtual não encontrado. Usando Python global..."
fi

# Verificar dependências
echo "📦 Verificando dependências..."
python3 -m pip install -q uvicorn fastapi sqlalchemy 2>/dev/null

# Iniciar servidor
echo "🌐 Iniciando servidor em http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""

python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
