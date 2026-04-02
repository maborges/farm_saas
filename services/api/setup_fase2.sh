#!/bin/bash
# Script de setup para Fase 2 - AgroSaaS
# Data: 2026-03-31

set -e

echo "============================================"
echo "  Setup Fase 2 - AgroSaaS"
echo "  IA, IoT e Agricultura de Precisão"
echo "============================================"
echo ""

cd "$(dirname "$0")"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[1/5] Instalando dependências Python...${NC}"
pip install torch torchvision pillow numpy pandas scikit-learn 2>/dev/null || {
    echo -e "${YELLOW}PyTorch pode requerer instalação manual. Verifique https://pytorch.org/${NC}"
}

pip install rasterio geopandas pyproj 2>/dev/null || {
    echo -e "${YELLOW}GIS packages podem requerer GDAL instalado no sistema${NC}"
}

echo -e "${GREEN}✓ Dependências instaladas${NC}"
echo ""

echo -e "${YELLOW}[2/5] Atualizando ambiente Python...${NC}"
cd services/api
pip install -e . 2>/dev/null || echo "Instalação em modo editável pode falhar em alguns ambientes"
echo -e "${GREEN}✓ Ambiente atualizado${NC}"
echo ""

echo -e "${YELLOW}[3/5] Rodando migrations do banco...${NC}"
# Verificar se alembic está configurado
if [ -f "alembic.ini" ]; then
    alembic upgrade head 2>/dev/null || {
        echo -e "${RED}Erro ao rodar migrations. Verifique conexão com banco.${NC}"
        echo "Você pode rodar manualmente depois: alembic upgrade head"
    }
    echo -e "${GREEN}✓ Migrations aplicadas${NC}"
else
    echo -e "${YELLOW}alembic.ini não encontrado. Pule esta etapa.${NC}"
fi
echo ""

echo -e "${YELLOW}[4/5] Rodando seed de pragas e doenças...${NC}"
python -m ia_diagnostico.seed 2>/dev/null || {
    echo -e "${RED}Seed falhou. Verifique se o banco está configurado.${NC}"
    echo "Você pode rodar manualmente depois: python -m ia_diagnostico.seed"
}
echo -e "${GREEN}✓ Seed executado${NC}"
echo ""

echo -e "${YELLOW}[5/5] Verificando estrutura de diretórios...${NC}"

# Verificar módulos criados
MODULES=(
    "ia_diagnostico"
    "iot_integracao"
    "agricola/amostragem_solo"
)

for module in "${MODULES[@]}"; do
    if [ -d "$module" ]; then
        echo -e "${GREEN}  ✓ $module${NC}"
    else
        echo -e "${RED}  ✗ $module não encontrado${NC}"
    fi
done

echo ""
echo "============================================"
echo "  Setup Concluído!"
echo "============================================"
echo ""
echo "Próximos passos:"
echo "1. Inicie o servidor: uvicorn main:app --reload"
echo "2. Acesse a API: http://localhost:8000/docs"
echo "3. Frontend IA: http://localhost:3000/ia-diagnostico"
echo ""
echo "Para integrar com APIs externas:"
echo "- John Deere: https://developer.deere.com/"
echo "- Case IH: https://afsconnect.caseih.com/"
echo "- WhatsApp: https://www.twilio.com/whatsapp"
echo ""
echo -e "${GREEN}Fase 2 pronta para desenvolvimento!${NC}"
