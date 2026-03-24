#!/usr/bin/env python3
"""
Script para criar a estrutura completa de um novo módulo AgroSaaS.

Uso:
    python scripts/create_module.py --modulo A1_PLANEJAMENTO --dominio agricola --nome "Planejamento de Safra"

Isso criará:
    - agricola/a1_planejamento/__init__.py
    - agricola/a1_planejamento/router.py
    - agricola/a1_planejamento/models.py
    - agricola/a1_planejamento/schemas.py
    - agricola/a1_planejamento/services.py
    - agricola/a1_planejamento/README.md
"""

import argparse
import os
from pathlib import Path
from typing import Dict


def get_module_info(modulo_id: str) -> Dict[str, str]:
    """Retorna informações do módulo a partir do ID."""
    from core.constants import ModuloMetadata

    info = ModuloMetadata.get_modulo_info(modulo_id)
    if not info:
        raise ValueError(f"Módulo {modulo_id} não encontrado em core.constants")

    return info


def to_snake_case(text: str) -> str:
    """Converte texto para snake_case."""
    return text.lower().replace(" ", "_").replace("-", "_")


def create_init_file(path: Path, modulo_id: str, modulo_nome: str, categoria: str):
    """Cria __init__.py do módulo."""
    content = f'''"""
Módulo {modulo_nome}
ID: {modulo_id}
Categoria: {categoria}
"""

from .router import router

__all__ = ["router"]
'''
    path.write_text(content)


def create_router_file(path: Path, modulo_id: str, modulo_nome: str, prefixo_rota: str):
    """Cria router.py do módulo."""
    content = f'''"""
Router do módulo {modulo_nome}.
Endpoints HTTP com feature gate aplicado.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from core.dependencies import get_session, get_tenant_id, require_module
from core.constants import Modulos

# Importar schemas e services quando criados
# from .schemas import ...
# from .services import ...

router = APIRouter(
    prefix="{prefixo_rota}",
    tags=["{modulo_nome}"]
)


@router.get(
    "/health",
    summary="Health check do módulo",
    dependencies=[Depends(require_module(Modulos.{modulo_id}))]
)
async def health_check():
    """
    Verifica se o módulo {modulo_nome} está ativo.

    **Requer módulo:** {modulo_id}
    """
    return {{
        "status": "ok",
        "module": "{modulo_id}",
        "name": "{modulo_nome}"
    }}


# TODO: Adicionar endpoints específicos do módulo aqui
# Exemplo:
# @router.post("/", dependencies=[Depends(require_module(Modulos.{modulo_id}))])
# async def criar_recurso(...):
#     pass
'''
    path.write_text(content)


def create_models_file(path: Path, modulo_id: str, modulo_nome: str):
    """Cria models.py do módulo."""
    content = f'''"""
Models do módulo {modulo_nome}.
Todas as entidades de banco relacionadas a este módulo.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


# TODO: Criar models específicos do módulo
# Exemplo:
#
# class RecursoExemplo(Base):
#     """
#     Descrição do recurso.
#
#     Escopo: {modulo_id}
#     Multi-tenancy: sim (tenant_id obrigatório)
#     """
#     __tablename__ = "recursos_exemplo"
#
#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     tenant_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("tenants.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True
#     )
#
#     nome: Mapped[str] = mapped_column(String(100), nullable=False)
#     ativo: Mapped[bool] = mapped_column(Boolean, default=True)
#
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         default=lambda: datetime.now(timezone.utc)
#     )
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc)
#     )
'''
    path.write_text(content)


def create_schemas_file(path: Path, modulo_id: str, modulo_nome: str):
    """Cria schemas.py do módulo."""
    content = f'''"""
Schemas Pydantic do módulo {modulo_nome}.
Separados em *Create (input), *Update (input), *Response (output).
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


# TODO: Criar schemas específicos do módulo
# Padrão: RecursoCreate, RecursoUpdate, RecursoResponse
#
# Exemplo:
#
# class RecursoCreate(BaseModel):
#     """Schema para criação de recurso."""
#     nome: str = Field(..., min_length=3, max_length=100)
#
#
# class RecursoUpdate(BaseModel):
#     """Schema para atualização de recurso."""
#     nome: Optional[str] = Field(None, min_length=3, max_length=100)
#     ativo: Optional[bool] = None
#
#
# class RecursoResponse(BaseModel):
#     """Schema de resposta de recurso."""
#     id: UUID
#     tenant_id: UUID
#     nome: str
#     ativo: bool
#     created_at: datetime
#     updated_at: datetime
#
#     model_config = {{"from_attributes": True}}
'''
    path.write_text(content)


def create_services_file(path: Path, modulo_id: str, modulo_nome: str):
    """Cria services.py do módulo."""
    content = f'''"""
Services do módulo {modulo_nome}.
Lógica de negócio isolada, testável, reutilizável.
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List

# from .models import ...
# from .schemas import ...
from core.exceptions import EntityNotFoundError, BusinessRuleError


# TODO: Criar services específicos do módulo
# Padrão: Uma classe Service por aggregate root
#
# Exemplo:
#
# class RecursoService:
#     """
#     Service para gestão de recursos.
#     Responsabilidade única: operações sobre Recurso.
#     """
#
#     def __init__(self, session: AsyncSession, tenant_id: UUID):
#         self.session = session
#         self.tenant_id = tenant_id
#
#     async def criar(self, dados: RecursoCreate) -> Recurso:
#         """Cria novo recurso com validações de negócio."""
#         # Implementar lógica de negócio
#         pass
#
#     async def listar(self) -> List[Recurso]:
#         """Lista recursos do tenant."""
#         pass
#
#     async def buscar(self, recurso_id: UUID) -> Recurso:
#         """Busca recurso por ID com validação de tenant."""
#         pass
'''
    path.write_text(content)


def create_readme_file(path: Path, modulo_id: str, modulo_info: Dict):
    """Cria README.md do módulo."""
    content = f'''# Módulo {modulo_info['nome']}

**ID:** `{modulo_id}`
**Categoria:** {modulo_info['categoria']}
**Status:** Em Desenvolvimento
**Preço Base:** R$ {modulo_info['preco_base_mensal']:.2f}/mês

## Descrição

{modulo_info['descricao']}

## Funcionalidades

- 🔄 Em desenvolvimento...

## Dependências

{chr(10).join(f"- **{dep}** (obrigatório)" for dep in modulo_info.get('dependencias', ['CORE']))}

## Integrações

Este módulo se integra com:
- (Definir integrações)

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Health check |

## Como Usar

```python
# No main.py
from {modulo_id.split('_')[0].lower()}.{modulo_id.lower()}.router import router as router_{modulo_id.lower()}

app.include_router(router_{modulo_id.lower()}, prefix="/api/v1")
```

## Testes

```bash
cd services/api
pytest {modulo_id.split('_')[0].lower()}/{modulo_id.lower()}/tests/ -v
```

## Changelog

### v1.0.0 (em desenvolvimento)
- 🔄 Estrutura inicial criada
'''
    path.write_text(content)


def main():
    parser = argparse.ArgumentParser(description="Criar novo módulo AgroSaaS")
    parser.add_argument("--modulo", required=True, help="ID do módulo (ex: A1_PLANEJAMENTO)")
    parser.add_argument("--dominio", required=True, help="Domínio (ex: agricola, pecuaria)")
    parser.add_argument("--prefixo", help="Prefixo da rota (ex: /agricola/planejamento)", default=None)

    args = parser.parse_args()

    modulo_id = args.modulo
    dominio = args.dominio.lower()
    modulo_id_lower = modulo_id.lower()

    # Buscar informações do módulo
    try:
        modulo_info = get_module_info(modulo_id)
    except ValueError as e:
        print(f"❌ Erro: {e}")
        print(f"💡 Dica: Adicione o módulo {modulo_id} em core/constants.py primeiro")
        return

    modulo_nome = modulo_info["nome"]

    # Determinar prefixo da rota
    if args.prefixo:
        prefixo_rota = args.prefixo
    else:
        prefixo_rota = f"/{dominio}/{modulo_id_lower.replace('_', '-')}"

    # Criar diretório do módulo
    api_dir = Path(__file__).parent.parent
    modulo_dir = api_dir / dominio / modulo_id_lower
    modulo_dir.mkdir(parents=True, exist_ok=True)

    print(f"📁 Criando módulo em: {modulo_dir}")

    # Criar arquivos
    files_created = []

    # __init__.py
    init_file = modulo_dir / "__init__.py"
    create_init_file(init_file, modulo_id, modulo_nome, modulo_info["categoria"])
    files_created.append(init_file)

    # router.py
    router_file = modulo_dir / "router.py"
    create_router_file(router_file, modulo_id, modulo_nome, prefixo_rota)
    files_created.append(router_file)

    # models.py
    models_file = modulo_dir / "models.py"
    create_models_file(models_file, modulo_id, modulo_nome)
    files_created.append(models_file)

    # schemas.py
    schemas_file = modulo_dir / "schemas.py"
    create_schemas_file(schemas_file, modulo_id, modulo_nome)
    files_created.append(schemas_file)

    # services.py
    services_file = modulo_dir / "services.py"
    create_services_file(services_file, modulo_id, modulo_nome)
    files_created.append(services_file)

    # README.md
    readme_file = modulo_dir / "README.md"
    create_readme_file(readme_file, modulo_id, modulo_info)
    files_created.append(readme_file)

    print(f"\n✅ Módulo {modulo_id} criado com sucesso!")
    print(f"\n📝 Arquivos criados:")
    for f in files_created:
        print(f"   - {f.relative_to(api_dir)}")

    print(f"\n🔧 Próximos passos:")
    print(f"   1. Implementar models em: {models_file.relative_to(api_dir)}")
    print(f"   2. Criar schemas em: {schemas_file.relative_to(api_dir)}")
    print(f"   3. Implementar services em: {services_file.relative_to(api_dir)}")
    print(f"   4. Criar rotas em: {router_file.relative_to(api_dir)}")
    print(f"   5. Adicionar ao main.py:")
    print(f"      from {dominio}.{modulo_id_lower}.router import router as router_{modulo_id_lower}")
    print(f'      app.include_router(router_{modulo_id_lower}, prefix="/api/v1")')
    print(f"   6. Criar migration para os models:")
    print(f"      alembic revision --autogenerate -m 'add_{modulo_id_lower}_module'")


if __name__ == "__main__":
    main()
