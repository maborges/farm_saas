#!/usr/bin/env python3
"""
Script para gerar estrutura de arquivos no padrão AgroSaaS.
Gera módulos com arquivos individuais por entidade.
"""

import os

BASE_DIR = "/opt/lampp/htdocs/farm/services/api"

# Definição dos módulos e suas entidades
MODULOS = {
    "ia_diagnostico": {
        "models": ["pragas_doencas", "tratamentos", "diagnosticos", "recomendacoes", "modelos_ml"],
        "schemas": ["pragas_doencas", "tratamentos", "diagnosticos", "recomendacoes", "modelos_ml"],
        "routers": ["pragas_doencas", "tratamentos", "diagnosticos"],
        "services": ["diagnostico_service"],
    },
    "iot_integracao": {
        "models": ["john_deere", "case_ih", "whatsapp", "comparador_precos"],
        "schemas": ["john_deere", "case_ih", "whatsapp", "comparador_precos"],
        "routers": ["john_deere", "case_ih", "whatsapp", "comparador_precos"],
        "services": ["integracao_service"],
    },
    "agricola/amostragem_solo": {
        "models": ["amostras", "mapas_fertilidade", "prescricoes_vra"],
        "schemas": ["amostras", "mapas_fertilidade", "prescricoes_vra"],
        "routers": ["amostras", "mapas_fertilidade", "prescricoes_vra"],
        "services": ["solo_service"],
    },
    "agricola/ndvi_avancado": {
        "models": ["imagens_satelite", "ndvi_registros", "irrigacao", "balanco_hidrico", "estacoes_meteorologicas"],
        "schemas": ["ndvi", "irrigacao", "meteorologia"],
        "routers": ["ndvi", "irrigacao", "meteorologia"],
        "services": ["ndvi_service", "irrigacao_service"],
    },
    "core/api_publica": {
        "models": ["api_keys", "api_logs", "api_versions", "sdks"],
        "schemas": ["api_keys", "api_logs", "api_versions", "sdks"],
        "routers": ["keys", "logs", "versions", "sdks"],
        "services": ["api_key_service"],
    },
    "enterprise": {
        "models": ["sap", "powerbi", "benchmarks", "preditivo", "pontos"],
        "schemas": ["sap", "powerbi", "benchmarks", "preditivo", "pontos"],
        "routers": ["sap", "powerbi", "benchmarks", "preditivo", "pontos"],
        "services": ["sap_service", "powerbi_service", "preditivo_service"],
    },
}


def criar_arquivo_base(path: str, content: str):
    """Cria arquivo se não existir."""
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(content)
        print(f"  ✅ Criado: {path}")
    else:
        print(f"  ⚠️  Já existe: {path}")


def gerar_init_models(modulo: str, entidades: list):
    """Gera __init__.py para models."""
    imports = "\n".join([
        f"from .{entidade} import {entidade.title().replace('_', '')}" 
        for entidade in entidades
    ])
    all_list = ", ".join([entidade.title().replace('_', '') for entidade in entidades])
    
    content = f"""\"\"\"Models para {modulo}.\"\"\"

{imports}

__all__ = [{", ".join(f'"{entidade.title().replace("_", "")}"' for entidade in entidades)}]
"""
    criar_arquivo_base(f"{BASE_DIR}/{modulo}/models/__init__.py", content)


def gerar_init_routers(modulo: str, entidades: list):
    """Gera __init__.py para routers."""
    imports = "\n".join([
        f"from .{entidade} import router as {entidade}_router"
        for entidade in entidades
    ])
    
    content = f"""\"\"\"Routers para {modulo}.\"\"\"

{imports}

__all__ = [{", ".join(f'"{entidade}_router"' for entidade in entidades)}]
"""
    criar_arquivo_base(f"{BASE_DIR}/{modulo}/routers/__init__.py", content)


def gerar_init_services(modulo: str, services: list):
    """Gera __init__.py para services."""
    imports = "\n".join([
        f"from .{service} import {service.title().replace('_', '')}"
        for service in services
    ])
    
    content = f"""\"\"\"Services para {modulo}.\"\"\"

{imports}

__all__ = [{", ".join(f'"{service.title().replace("_", "")}"' for service in services)}]
"""
    criar_arquivo_base(f"{BASE_DIR}/{modulo}/services/__init__.py", content)


def gerar_model_stub(modulo: str, entidade: str):
    """Gera arquivo stub para model."""
    class_name = entidade.title().replace('_', '')
    
    content = f"""\"\"\"Modelo para {entidade}.\"\"\"

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base


class {class_name}(Base):
    \"\"\"Modelo para {entidade}.\"\"\"
    __tablename__ = "{entidade}"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Adicionar campos específicos aqui
    # nome = Column(String(200), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
"""
    criar_arquivo_base(f"{BASE_DIR}/{modulo}/models/{entidade}.py", content)


def gerar_router_stub(modulo: str, entidade: str):
    """Gera arquivo stub para router."""
    entity_plural = entidade
    entity_singular = entidade.rstrip('s') if entidade.endswith('s') else entidade
    
    content = f"""\"\"\"Router para {entidade}.\"\"\"

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_tenant

router = APIRouter(prefix="/{entity_plural}", tags=["{entidade.title()}"])


@router.get("/")
def listar_{entity_plural}(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    \"\"\"Lista {entity_plural}.\"\"\"
    # Implementar lógica aqui
    return []


@router.post("/", status_code=201)
def criar_{entity_singular}(
    # dados: {entity_singular.title()}Create,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    \"\"\"Cria {entity_singular}.\"\"\"
    # Implementar lógica aqui
    return {{}}
"""
    criar_arquivo_base(f"{BASE_DIR}/{modulo}/routers/{entidade}.py", content)


def gerar_service_stub(modulo: str, service: str):
    """Gera arquivo stub para service."""
    class_name = service.title().replace('_', '')
    
    content = f"""\"\"\"Service para {service}.\"\"\"

from sqlalchemy.orm import Session


class {class_name}:
    \"\"\"Service para {service}.\"\"\"
    
    def __init__(self, db: Session):
        self.db = db
    
    # Adicionar métodos aqui
    # def listar(self, tenant_id: str):
    #     return []
"""
    criar_arquivo_base(f"{BASE_DIR}/{modulo}/services/{service}.py", content)


def main():
    print("🚀 Gerando estrutura de arquivos no padrão AgroSaaS...\n")
    
    for modulo, estrutura in MODULOS.items():
        print(f"\n📁 Módulo: {modulo}")
        print("-" * 50)
        
        # Gerar models
        if "models" in estrutura:
            print(f"  📦 Models: {len(estrutura['models'])} entidades")
            gerar_init_models(modulo, estrutura["models"])
            for entidade in estrutura["models"]:
                gerar_model_stub(modulo, entidade)
        
        # Gerar routers
        if "routers" in estrutura:
            print(f"  🛣️  Routers: {len(estrutura['routers'])} entidades")
            gerar_init_routers(modulo, estrutura["routers"])
            for entidade in estrutura["routers"]:
                gerar_router_stub(modulo, entidade)
        
        # Gerar services
        if "services" in estrutura:
            print(f"  ⚙️  Services: {len(estrutura['services'])} serviços")
            gerar_init_services(modulo, estrutura["services"])
            for service in estrutura["services"]:
                gerar_service_stub(modulo, service)
        
        print(f"  ✅ Módulo {modulo} concluído!")
    
    print("\n" + "=" * 50)
    print("✅ Geração concluída!")
    print("=" * 50)
    print("\nPróximos passos:")
    print("1. Preencher os arquivos stub com o código real")
    print("2. Atualizar main.py com os imports corretos")
    print("3. Criar migrations para as novas tabelas")


if __name__ == "__main__":
    main()
