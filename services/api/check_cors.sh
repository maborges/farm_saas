#!/bin/bash
# Script para verificar se CORS está configurado corretamente
# Uso: ./check_cors.sh [origem]

ORIGIN="${1:-http://localhost:3000}"
API_URL="http://localhost:8000"

echo "🔍 Verificando configuração de CORS..."
echo "📍 API: $API_URL"
echo "🌐 Origem: $ORIGIN"
echo ""

# Verificar se o backend está rodando
echo "1️⃣ Verificando se o backend está rodando..."
if curl -s --max-time 2 "$API_URL/health" > /dev/null 2>&1; then
    echo "   ✅ Backend está rodando"
else
    echo "   ❌ Backend NÃO está rodando!"
    echo "   Execute: ./start_server.sh"
    exit 1
fi
echo ""

# Testar preflight request (OPTIONS)
echo "2️⃣ Testando preflight request (OPTIONS)..."
RESPONSE=$(curl -s -X OPTIONS "$API_URL/api/v1/auth/login" \
    -H "Origin: $ORIGIN" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type" \
    -i 2>&1)

if echo "$RESPONSE" | grep -q "access-control-allow-origin: $ORIGIN"; then
    echo "   ✅ CORS configurado corretamente para $ORIGIN"
else
    echo "   ❌ CORS NÃO está configurado para $ORIGIN"
    echo ""
    echo "📋 Headers retornados:"
    echo "$RESPONSE" | grep -i "access-control"
    echo ""
    echo "💡 Soluções:"
    echo "   1. Adicione '$ORIGIN' em main.py na lista allow_origins"
    echo "   2. Reinicie o servidor: ./start_server.sh"
    exit 1
fi
echo ""

# Verificar headers específicos
echo "3️⃣ Verificando headers de CORS..."

if echo "$RESPONSE" | grep -q "access-control-allow-credentials: true"; then
    echo "   ✅ Credentials: permitido"
else
    echo "   ⚠️  Credentials: não configurado"
fi

if echo "$RESPONSE" | grep -q "access-control-allow-methods"; then
    METHODS=$(echo "$RESPONSE" | grep "access-control-allow-methods" | cut -d: -f2)
    echo "   ✅ Methods:$METHODS"
else
    echo "   ⚠️  Methods: não configurado"
fi

if echo "$RESPONSE" | grep -q "access-control-allow-headers"; then
    echo "   ✅ Headers: permitido"
else
    echo "   ⚠️  Headers: não configurado"
fi
echo ""

# Testar GET request
echo "4️⃣ Testando GET request real..."
GET_RESPONSE=$(curl -s -X GET "$API_URL/health" \
    -H "Origin: $ORIGIN" \
    -i 2>&1)

if echo "$GET_RESPONSE" | grep -q "access-control-allow-origin: $ORIGIN"; then
    echo "   ✅ GET request com CORS funcionando"
else
    echo "   ❌ GET request sem headers CORS"
fi
echo ""

echo "📊 Resultado Final:"
if echo "$RESPONSE" | grep -q "access-control-allow-origin: $ORIGIN" && \
   echo "$GET_RESPONSE" | grep -q "access-control-allow-origin: $ORIGIN"; then
    echo "   ✅ CORS está funcionando corretamente!"
    echo ""
    echo "🎯 Próximos passos:"
    echo "   - Acesse o frontend em $ORIGIN"
    echo "   - As requisições para $API_URL devem funcionar"
else
    echo "   ❌ CORS tem problemas"
    echo ""
    echo "🔧 Ações necessárias:"
    echo "   1. Verifique se '$ORIGIN' está em main.py (allow_origins)"
    echo "   2. Reinicie o servidor: pkill -f uvicorn && ./start_server.sh"
    echo "   3. Execute este script novamente"
    echo ""
    echo "📖 Documentação: cat CORS_TROUBLESHOOTING.md"
fi
echo ""
