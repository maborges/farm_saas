# Guia: Como Adicionar um Novo Módulo ao AgroSaaS

Passo a passo completo para incluir uma nova entidade/módulo na aplicação,
seguindo todos os padrões arquiteturais do projeto.

---

## Visão Geral do Fluxo

```
Request HTTP
    ↓
main.py (roteamento)
    ↓
Dependencies (JWT → tenant_id → módulo → role)
    ↓
Router (HTTP handler)
    ↓
Service (regras de negócio)
    ↓
BaseService (CRUD + isolamento de tenant)
    ↓
PostgreSQL (schema farms + RLS)
```

---

## Passo 1 — Scaffold do Módulo

Use o script de scaffolding para gerar a estrutura base:

```bash
cd services/api
source .venv/bin/activate
python scripts/create_module.py <nome_do_modulo>
```

Isso cria a pasta com os arquivos base em branco. Se for um submódulo
dentro de um domínio existente (ex: `agricola/`), crie a pasta manualmente:

```bash
mkdir -p services/api/agricola/meu_modulo
touch services/api/agricola/meu_modulo/__init__.py
touch services/api/agricola/meu_modulo/models.py
touch services/api/agricola/meu_modulo/schemas.py
touch services/api/agricola/meu_modulo/service.py
touch services/api/agricola/meu_modulo/router.py
```

**Estrutura resultante:**
```
agricola/meu_modulo/
├── __init__.py
├── models.py    ← SQLAlchemy 2.0
├── schemas.py   ← Pydantic v2
├── service.py   ← regras de negócio
└── router.py    ← endpoints HTTP
```

---

## Passo 2 — Model (`models.py`)

Toda entidade **DEVE** ter `tenant_id`. Use sempre `mapped_column()` (SQLAlchemy 2.0).

```python
# agricola/meu_modulo/models.py
import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class MinhaEntidade(Base):
    __tablename__ = "minhas_entidades"

    # --- PKs e FKs obrigatórias ---
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,          # SEMPRE indexar tenant_id
    )

    # --- Opcional: FK para fazenda (se for por fazenda) ---
    fazenda_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("fazendas.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # --- Campos de domínio ---
    nome: Mapped[str] = mapped_column(String(150))
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ATIVO")

    # --- Auditoria (obrigatório) ---
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("(CURRENT_TIMESTAMP)")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("(CURRENT_TIMESTAMP)"),
        onupdate=datetime.utcnow,
    )
```

**Regras:**
- `tenant_id` com `index=True` sempre
- `mapped_column()` — nunca `Column()` (legado)
- `created_at` / `updated_at` em todas as entidades
- Herdar de `Base` importado de `core.database`

---

## Passo 3 — Schemas (`schemas.py`)

Pydantic v2 com schemas separados para Create, Update e Response.

```python
# agricola/meu_modulo/schemas.py
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MinhaEntidadeCreate(BaseModel):
    fazenda_id: UUID | None = None
    nome: str = Field(..., min_length=2, max_length=150)
    descricao: str | None = None
    status: str = "ATIVO"


class MinhaEntidadeUpdate(BaseModel):
    # Todos os campos opcionais no Update
    nome: str | None = Field(None, min_length=2, max_length=150)
    descricao: str | None = None
    status: str | None = None


class MinhaEntidadeResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    fazenda_id: UUID | None
    nome: str
    descricao: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Regras:**
- `model_dump()` — nunca `.dict()` (Pydantic v1 legado)
- `ConfigDict(from_attributes=True)` no Response (para ORM → Pydantic)
- Campos opcionais no Update sempre com `None` como default

---

## Passo 4 — Service (`service.py`)

Estende `BaseService` e adiciona regras de negócio específicas.

```python
# agricola/meu_modulo/service.py
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_service import BaseService
from core.exceptions import BusinessRuleError
from .models import MinhaEntidade
from .schemas import MinhaEntidadeCreate, MinhaEntidadeUpdate


class MinhaEntidadeService(BaseService[MinhaEntidade]):

    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(MinhaEntidade, session, tenant_id)

    async def criar(self, dados: MinhaEntidadeCreate) -> MinhaEntidade:
        # Exemplo: validar duplicata
        stmt = select(MinhaEntidade).filter_by(
            tenant_id=self.tenant_id,
            nome=dados.nome,
        )
        result = await self.session.execute(stmt)
        if result.scalars().first():
            raise BusinessRuleError(
                f"Já existe uma entidade com o nome '{dados.nome}'"
            )

        # Delegar criação ao BaseService (tenant_id injetado automaticamente)
        return await super().create(dados.model_dump())

    async def atualizar(
        self, id: uuid.UUID, dados: MinhaEntidadeUpdate
    ) -> MinhaEntidade:
        # get_or_fail já valida tenant_id — lança EntityNotFoundError se cruzar tenant
        entidade = await self.get_or_fail(id)

        return await super().update(id, dados.model_dump(exclude_unset=True))
```

**Regras:**
- Construtor sempre recebe `session` e `tenant_id`, repassa ao `super()`
- Usar `super().create()`, `super().update()`, `super().list_all()` para CRUD
- Nunca escrever queries raw direto no router
- `BusinessRuleError` para violações de regras de negócio
- `get_or_fail()` valida automaticamente o `tenant_id` — se a entidade não pertence
  ao tenant, lança `TenantViolationError` → 403

---

## Passo 5 — Router (`router.py`)

Endpoints HTTP com as camadas de segurança em ordem.

```python
# agricola/meu_modulo/router.py
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import (
    get_session_with_tenant,
    get_tenant_id,
    require_module,
    require_role,
)
from .models import MinhaEntidade
from .schemas import MinhaEntidadeCreate, MinhaEntidadeUpdate, MinhaEntidadeResponse
from .service import MinhaEntidadeService

router = APIRouter(prefix="/minha-entidade", tags=["Minha Entidade"])


@router.get("/", response_model=List[MinhaEntidadeResponse])
async def listar(
    fazenda_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),  # ajustar módulo
):
    svc = MinhaEntidadeService(session, tenant_id)
    filters = {}
    if fazenda_id:
        filters["fazenda_id"] = fazenda_id
    items = await svc.list_all(**filters)
    return [MinhaEntidadeResponse.model_validate(i) for i in items]


@router.post(
    "/",
    response_model=MinhaEntidadeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar(
    dados: MinhaEntidadeCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
    user: dict = Depends(require_role(["admin", "agronomo", "operador"])),
):
    svc = MinhaEntidadeService(session, tenant_id)
    item = await svc.criar(dados)
    await session.commit()
    return MinhaEntidadeResponse.model_validate(item)


@router.get("/{id}", response_model=MinhaEntidadeResponse)
async def buscar(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    svc = MinhaEntidadeService(session, tenant_id)
    item = await svc.get_or_fail(id)
    return MinhaEntidadeResponse.model_validate(item)


@router.patch("/{id}", response_model=MinhaEntidadeResponse)
async def atualizar(
    id: UUID,
    dados: MinhaEntidadeUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
    user: dict = Depends(require_role(["admin", "agronomo"])),
):
    svc = MinhaEntidadeService(session, tenant_id)
    item = await svc.atualizar(id, dados)
    await session.commit()
    return MinhaEntidadeResponse.model_validate(item)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
    user: dict = Depends(require_role(["admin"])),
):
    svc = MinhaEntidadeService(session, tenant_id)
    await svc.hard_delete(id)
    await session.commit()
```

**Camadas de segurança por ordem:**
1. `get_session_with_tenant` → valida JWT + abre sessão com tenant_id
2. `get_tenant_id` → extrai UUID do tenant do token
3. `require_module(...)` → verifica se o plano tem o módulo contratado
4. `require_role([...])` → verifica role do usuário na fazenda

**Regra:** Sempre `await session.commit()` nas operações de escrita (POST, PATCH, DELETE).

---

## Passo 6 — Registrar o Router em `main.py`

```python
# services/api/main.py

# Adicione o import junto aos demais routers do domínio
from agricola.meu_modulo.router import router as router_meu_modulo

# Adicione o include junto aos demais includes
app.include_router(router_meu_modulo, prefix="/api/v1")
```

---

## Passo 7 — Registrar o Model nas Migrations (Alembic)

Abra `services/api/migrations/env.py` e adicione o import do model:

```python
# migrations/env.py  (seção de imports dos models)

# ... imports existentes ...
from agricola.meu_modulo.models import MinhaEntidade  # ← adicionar aqui
```

O Alembic precisa conhecer todos os models para gerar o diff correto.

---

## Passo 8 — Gerar e Aplicar a Migration

```bash
cd services/api
source .venv/bin/activate

# Gerar migration com base no diff dos models
alembic revision --autogenerate -m "add_minhas_entidades_table"

# Revisar o arquivo gerado em migrations/versions/
# (verificar se o SQL gerado está correto)

# Aplicar a migration no banco
alembic upgrade head

# Confirmar versão atual
alembic current
```

---

## Passo 9 — (Opcional) Adicionar Permissões no Frontend

Se o módulo requer controle de acesso no frontend, adicione a permissão
em `apps/web/src/lib/permissions.ts` e use o hook:

```typescript
// Em qualquer componente React
const { hasModule } = useHasModule();
const { hasPermission } = usePermission();

if (!hasModule('A1_PLANEJAMENTO')) return <ModuleUpsell />;
if (!hasPermission('tenant:minha_entidade:create')) return null;
```

---

## Checklist de Validação

Antes de considerar o módulo pronto, confirme:

- [ ] Model tem `tenant_id` com `ForeignKey("tenants.id")` e `index=True`
- [ ] Model usa `mapped_column()` (não `Column()`)
- [ ] Model tem `created_at` e `updated_at`
- [ ] Model importado em `migrations/env.py`
- [ ] Migration gerada e aplicada (`alembic upgrade head`)
- [ ] Service estende `BaseService[MinhaEntidade]`
- [ ] Service usa `super().create()` / `super().update()` / `super().list_all()`
- [ ] Nenhuma query raw SQLAlchemy no router
- [ ] Router tem `require_module(...)` em todos os endpoints
- [ ] Router tem `require_role([...])` nos endpoints de escrita
- [ ] Router importado e registrado em `main.py`
- [ ] `await session.commit()` em todos os endpoints de escrita
- [ ] Schemas usam `model_dump()` (não `.dict()`)
- [ ] Schema de Response tem `ConfigDict(from_attributes=True)`

---

## Referência Rápida de Dependências

| Dependência | Uso | Retorna |
|---|---|---|
| `get_session_with_tenant` | Abre sessão com tenant_id injetado | `AsyncSession` |
| `get_tenant_id` | Extrai tenant_id do JWT | `UUID` |
| `require_module("X")` | Bloqueia se módulo não contratado | `None` (ou 402) |
| `require_any_module("X","Y")` | Libera se tiver pelo menos 1 | `None` (ou 402) |
| `require_role(["admin"])` | Verifica role do usuário | `dict` com claims |
| `require_permission("backoffice:x:y")` | Para endpoints do backoffice | `None` (ou 403) |
| `require_tenant_permission("tenant:x:y")` | Para endpoints tenant com RBAC fino | `None` (ou 403) |

---

## Referência de Erros e Códigos HTTP

| Exceção | HTTP | Quando usar |
|---|---|---|
| `EntityNotFoundError` | 404 | Entidade não encontrada (ou de outro tenant) |
| `TenantViolationError` | 403 | Acesso cross-tenant detectado |
| `ModuleNotContractedError` | 402 | Módulo não incluído no plano |
| `BusinessRuleError` | 422 | Violação de regra de negócio |

---

## Fluxo Completo de uma Requisição

```
POST /api/v1/minha-entidade
Authorization: Bearer <JWT>

1. main.py roteia para router_meu_modulo
2. get_session_with_tenant → decodifica JWT, extrai tenant_id, abre sessão
3. get_tenant_id → retorna UUID do tenant
4. require_module("A1_PLANEJAMENTO") → verifica plano (JWT cache → DB)
5. require_role(["admin","agronomo"]) → verifica perfil na fazenda
6. Handler executa:
   a) MinhaEntidadeService(session, tenant_id)
   b) svc.criar(dados) → valida duplicata → super().create()
   c) BaseService injeta tenant_id no INSERT automaticamente
   d) session.commit()
7. MinhaEntidadeResponse.model_validate(item) → 201 Created

Cenários de erro:
  Sem JWT           → 401
  Módulo ausente    → 402
  Role insuficiente → 403
  Duplicata         → 422 (BusinessRuleError)
  Cross-tenant      → 403 + log SECURITY_INCIDENT
```
