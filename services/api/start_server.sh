#!/bin/bash
# Script para iniciar o servidor FastAPI com CORS configurado corretamente
# Uso: ./start_server.sh

cd "$(dirname "$0")"

# Verificar se o virtual environment existe
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment não encontrado!"
    echo "Execute: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Ativar virtual environment
source .venv/bin/activate

# Verificar se uvicorn está instalado
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "❌ Uvicorn não está instalado!"
    echo "Execute: pip install uvicorn"
    exit 1
fi

# Parar servidor anterior se estiver rodando
pkill -f "uvicorn main:app" 2>/dev/null && echo "🛑 Servidor anterior parado"

# Iniciar servidor
echo "🚀 Iniciando servidor FastAPI com CORS habilitado..."
echo "📍 URL: http://localhost:8000"
echo "📍 Docs: http://localhost:8000/docs"
echo ""
echo "🌐 CORS configurado para:"
echo "   - http://localhost:3000"
echo "   - http://localhost:3001"
echo "   - http://127.0.0.1:3000"
echo "   - http://127.0.0.1:3001"
echo "   - http://192.168.0.108:3000"
echo "   - http://192.168.0.108:3001"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
