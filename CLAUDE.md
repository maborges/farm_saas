# CLAUDE.md — Diretrizes Completas do Projeto AgroSaaS

## 1. Context Efficiency (MANDATORY)

Respeite o budget de contexto em TODAS as respostas:

- **Commands >10 linhas:** Use `mcp__plugin_context-mode_context-mode__ctx_batch_execute(commands, queries)` ou `ctx_execute()`
  - NUNCA use Bash para: testes, busca de arquivos, análise de logs, processamento de outputs
  - Exceptions: git, mkdir, rm, mv, navegação local
- **Respostas:** ≤150 palavras; artefatos (código, configs) sempre em FILES, nunca inline.
- **Idioma:** nossa iteração será em português pt-br.
- **Valores decimais** usar "," como separador decimal e "." como sepadador de milhar.
- **Formatação de Campos** sempre usar mascáras para inputs ou apresentaçãoo de dados conforme campo (cpd, cpf, cnpj, etc)
- **Code review loops:** Delegue a subagents via Agent tool com isolation=worktree
- **Busca de padrões:** Use Grep com glob patterns (`--glob="*.ts"`), não find
- **Confirmação:** todas as mensagem de confirmação para o usuário devem utilizar o componente AlertDialog em @/components/ui/alert-dialog.

---

## 2. Stack & Architecture

### Backend
```
FastAPI 0.115+ | SQLAlchemy 2.0 async | Alembic | PostgreSQL 14+ (fallback SQLite)
Python 3.12 | Pydantic v2 | Loguru | python-jose + PyJWT | SQLAlchemy-Utils
```

### Frontend  
```
Next.js 16 App Router | React 19 | shadcn/ui | Zustand | TanStack Query v5+
Tailwind 4 | react-hook-form | zod | date-fns | lucide-react
```

### Monorepo
```
pnpm workspaces (root pnpm-workspace.yaml)
├─ apps/web              (Next.js 16, port 3000)
├─ apps/backoffice       (Next.js admin, port 3001)
├─ apps/mobile           (React Native)
├─ services/api          (FastAPI, port 8000)
├─ packages/zod-schemas  (Shared Pydantic/Zod schemas)
└─ docs/                 (Markdowns + brainstorms)
```

---

## 3. Segurança — Multi-tenancy Defense in Depth

### 3.1 JWT & Claims
```python
# JWT payload contém:
{
  "sub": user_id,           # UUID
  "tenant_id": tenant_id,   # UUID — NUNCA confie no frontend
  "email": user@domain,
  "name": "User Name",
  "is_owner": bool,         # Bypassa RBAC (exceto billing)
  "iat": issued_at,
  "exp": expires_at
}
```

**Validação:** `get_current_user_claims(token)` → `get_tenant_id(request, claims)` valida que user pertence ao tenant

### 3.2 BaseService — Auto-injection de tenant_id
```python
# ❌ NUNCA fazer raw SQLAlchemy em routers:
stmt = select(Safra).where(Safra.status == "ATIVA")  # INSEGURO!

# ✅ SEMPRE usar BaseService:
service = SafraService(session, tenant_id)
safras = await service.list_all(skip=0, limit=100, status="ATIVA")
# BaseService injeta automaticamente: Safra.tenant_id == tenant_id
```

### 3.3 RBAC — Três Camadas

**Backoffice (Admin):**
```python
@require_permission("backoffice:tenants:view")
async def list_tenants(claims: dict = Depends(get_current_user_claims)):
    # Apenas admins do sistema
```

**Tenant (User):**
```python
@require_tenant_permission("module:resource:action")
async def create_safra(safra_in: SafraCreate, claims: dict):
    # Usuário do tenant com permissão explícita
```

**Module Flags:**
```python
@require_module("A1_PLANEJAMENTO")  # Feature gate por plan tier
async def get_orcamento(safra_id: UUID, claims: dict):
    # Só aparece para plans que contrataram este módulo
```

**Farm-level Roles:**
```python
# FazendaUsuario.perfil_fazenda_id → override de role por fazenda
# Exemplo: user é "Operador" globalmente mas "Gerente" em fazenda X
```

### 3.4 Isolamento de Tenant — PostgreSQL RLS (optional)
```sql
-- RLS policy exemplo (camada 3):
CREATE POLICY tenant_isolation ON safras
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

### 3.5 Errors & Logging
```python
# Always log security incidents
TenantViolationError(...)      # → 403 Forbidden
EntityNotFoundError(...)       # → 404 Not Found
ModuleNotContractedError(...)  # → 402 Payment Required
BusinessRuleError(...)         # → 422 Unprocessable Entity
```

---

## 4. Padrões Backend

### 4.1 Estrutura de Diretórios
```
services/api/
├─ main.py                    # FastAPI app + router registration (linhas 91-130)
├─ core/
│  ├─ config.py              # Settings (DB_URL, JWT_SECRET, SMTP)
│  ├─ database.py            # AsyncSession factory + engine
│  ├─ dependencies.py        # Injeção de dependências (get_tenant_id, require_permission)
│  ├─ exceptions.py          # EntityNotFoundError, TenantViolationError, etc
│  ├─ base_service.py        # Repository pattern genérico
│  ├─ constants.py           # PlanTier, Modulos, Permissões
│  ├─ models/
│  │  ├─ base.py            # Base SQLAlchemy (with tenant_id, created_at, updated_at)
│  │  └─ *.py               # Models globais (Tenant, User, SessaoAtiva, etc)
│  └─ services/
│     └─ audit_service.py   # write_audit_log() para Tabela de Auditoria
├─ agricola/                 # Módulo agricola (22 submodules)
│  ├─ __init__.py
│  ├─ safras/
│  │  ├─ models.py          # SQLAlchemy models (Safra, SafraTalhao)
│  │  ├─ schemas.py         # Pydantic (SafraCreate, SafraUpdate, SafraResponse)
│  │  ├─ service.py         # SafraService(BaseService[Safra])
│  │  └─ router.py          # @router.get, @router.post endpoints
│  ├─ romaneios/
│  ├─ beneficiamento/
│  └─ ... (outras features)
├─ pecuaria/
├─ financeiro/
└─ ... (outros módulos)

migrations/
├─ env.py                   # Alembic config
├─ script.py.mako
└─ versions/
   ├─ 001_inicial.py
   ├─ 002_safra_talhoes.py  # Migration N:N
   └─ ... (historia de schema)
```

### 4.2 Modelo — Padrão Base
```python
from sqlalchemy import ForeignKey, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.models.base import Base
import uuid

class Safra(Base):
    __tablename__ = "safras"
    
    # Campos obrigatórios (herdados de Base via mixin)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[uuid.UUID] = mapped_column(nullable=True)  # Auditoria
    
    # Campos de negócio
    ano_safra: Mapped[str] = mapped_column(String(20), nullable=False)
    cultura: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PLANEJADA")
    area_plantada_ha: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)  # NUNCA Float para valores!
    produtividade_meta_sc_ha: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Relationships
    talhoes: Mapped[list["SafraTalhao"]] = relationship(back_populates="safra", lazy="noload")
    romaneios: Mapped[list["Romaneio"]] = relationship(back_populates="safra", lazy="selectin")
    
    # Índices compostos
    __table_args__ = (
        Index("ix_safras_tenant_ano", tenant_id, ano_safra),
        Index("ix_safras_status", status),
    )
```

**Regras:**
- TODOS os modelos têm `tenant_id` (chave estrangeira)
- NUNCA use `Float` para valores monetários/área → use `Decimal(precision, scale)`
- `lazy="noload"` por padrão (evita N+1 queries) → override em query específica com `selectin` ou `joined`
- Timestamps obrigatórios: `created_at`, `updated_at`
- Use `Index()` para queries frequentes

### 4.3 Schema — Pydantic v2
```python
from pydantic import BaseModel, Field
from datetime import datetime

class SafraCreate(BaseModel):
    ano_safra: str
    cultura: str
    area_plantada_ha: float | None = None
    produtividade_meta_sc_ha: float | None = None

class SafraUpdate(BaseModel):
    cultura: str | None = None
    status: str | None = None

class SafraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # ORM mode
    
    id: UUID
    ano_safra: str
    cultura: str
    status: str
    area_plantada_ha: float | None
    created_at: datetime
    updated_at: datetime
```

### 4.4 Service — CRUD + Negócio
```python
from core.base_service import BaseService
from typing import Optional, List

class SafraService(BaseService[Safra]):
    """Herda: get, get_or_fail, list_all, create, update, hard_delete"""
    
    async def avancar_fase(self, safra_id: UUID, nova_fase: str) -> Safra:
        """Lógica de negócio: validar transição de fase"""
        safra = await self.get_or_fail(safra_id)
        
        # Validar transição permitida
        if not self._fase_permitida(safra.status, nova_fase):
            raise BusinessRuleError(f"Transição {safra.status} → {nova_fase} não permitida")
        
        safra.status = nova_fase
        return await self.update(safra.id, {"status": nova_fase})
    
    async def list_ativas(self) -> List[Safra]:
        """Custom query baseada em list_all"""
        return await self.list_all(status="EM_ANDAMENTO")
    
    @staticmethod
    def _fase_permitida(atual: str, proxima: str) -> bool:
        transicoes = {
            "PLANEJADA": ["PREPARO_SOLO", "CANCELADA"],
            "PREPARO_SOLO": ["PLANTIO", "CANCELADA"],
            # ...
        }
        return proxima in transicoes.get(atual, [])
```

### 4.5 Router — Endpoints
```python
from fastapi import APIRouter, Depends, HTTPException, status
from core.dependencies import get_tenant_id, require_tenant_permission
from core.models.safra import Safra
from .service import SafraService
from .schemas import SafraCreate, SafraUpdate, SafraResponse

router = APIRouter(prefix="/safras", tags=["Safras"])

@router.get("/", response_model=List[SafraResponse])
async def list_safras(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Lista safras do tenant ativo"""
    service = SafraService(session, tenant_id)
    return await service.list_all(skip=skip, limit=limit, status=status)

@router.post("/", response_model=SafraResponse, status_code=status.HTTP_201_CREATED)
@require_tenant_permission("agricola:safra:criar")
async def create_safra(
    safra_in: SafraCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Cria nova safra"""
    service = SafraService(session, tenant_id)
    return await service.create(safra_in)

@router.get("/{safra_id}", response_model=SafraResponse)
async def get_safra(
    safra_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    service = SafraService(session, tenant_id)
    return await service.get_or_fail(safra_id)

@router.post("/{safra_id}/avancar-fase/{nova_fase}")
@require_tenant_permission("agricola:safra:avancar")
async def avancar_fase(
    safra_id: UUID,
    nova_fase: str,
    observacao: dict | None = None,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    service = SafraService(session, tenant_id)
    safra = await service.avancar_fase(safra_id, nova_fase)
    await session.commit()
    return safra
```

### 4.6 Migrations — Alembic + Async
```bash
# Criar migration
cd services/api
alembic revision --autogenerate -m "adiciona campo abc"

# Rodar
alembic upgrade head
```

**Regra CRÍTICA:** Após `run_sync()`, SEMPRE fazer `await connection.commit()` ou terá ROLLBACK silencioso:
```python
def upgrade():
    with op.batch_alter_table('safras', schema=None) as batch_op:
        batch_op.add_column(sa.Column('novo_campo', sa.String(50), nullable=True))
    # IMPORTANTE: commitar após operações síncronas
```

---

## 5. Padrões Frontend

### 5.1 Estrutura
```
apps/web/src/
├─ app/                          # Next.js 16 App Router
│  ├─ (dashboard)/
│  │  ├─ layout.tsx              # Layout principal
│  │  ├─ dashboard/
│  │  │  └─ agricola/
│  │  │     ├─ page.tsx          # /dashboard/agricola
│  │  │     ├─ safras/
│  │  │     │  ├─ page.tsx       # /safras (lista)
│  │  │     │  └─ [id]/
│  │  │     │     ├─ page.tsx    # /safras/:id (detalhe)
│  │  │     │     ├─ romaneios/
│  │  │     │     ├─ beneficiamento/
│  │  │     │     └─ ... (tabs)
│  │  │     └─ ... (outras features)
│  ├─ auth/
│  │  ├─ login/page.tsx
│  │  └─ signup/page.tsx
│  └─ ... (outros módulos)
├─ components/
│  ├─ ui/                        # shadcn/ui customizados
│  │  ├─ button.tsx
│  │  ├─ card.tsx
│  │  ├─ input.tsx
│  │  ├─ select.tsx
│  │  ├─ dialog.tsx
│  │  ├─ data-table.tsx
│  │  ├─ skeleton.tsx
│  │  └─ ... (30+ componentes)
│  ├─ shared/                    # Componentes reutilizáveis
│  │  ├─ page-header.tsx
│  │  ├─ empty-state.tsx
│  │  ├─ navbar.tsx
│  │  ├─ app-sidebar.tsx
│  │  └─ ...
│  ├─ agricola/                  # Componentes de domínio
│  │  ├─ safra-timeline.tsx
│  │  ├─ safra-talhoes.tsx
│  │  ├─ romaneios-colheita.tsx
│  │  ├─ beneficiamento-cafe.tsx
│  │  └─ ...
│  ├─ estoque/
│  ├─ contabilidade/
│  └─ ...
├─ lib/
│  ├─ api.ts                     # apiFetch wrapper
│  ├─ utils.ts                   # cn(), formatters
│  └─ stores/
│     ├─ app-store.ts            # Zustand: activeFazendaId, activeModule, etc
│     └─ user-store.ts
├─ hooks/                        # Custom hooks
│  ├─ useAppStore.ts
│  ├─ useFazendas.ts
│  └─ ...
├─ styles/
│  └─ globals.css
└─ env.ts                        # Type-safe env vars
```

### 5.2 Componentes — Padrões

**Server Component (padrão para dados):**
```tsx
// app/(dashboard)/dashboard/agricola/safras/page.tsx
import { SafrasTable } from "@/components/agricola/safras-table";

export default async function SafrasPage() {
  // ❌ NUNCA fetch aqui — passa para Client Component
  // ✅ Se fetch necessário, use fetch com revalidate/no-cache
  
  return (
    <div className="space-y-6 p-6">
      <PageHeader title="Safras" />
      <SafrasTable />  {/* Client Component que faz fetch */}
    </div>
  );
}
```

**Client Component (padrão para interação):**
```tsx
"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";

interface Safra {
  id: string;
  ano_safra: string;
  cultura: string;
  status: string;
}

export function SafrasTable() {
  const [pageIndex, setPageIndex] = useState(0);
  
  const { data: safras = [], isLoading } = useQuery<Safra[]>({
    queryKey: ["safras", pageIndex],
    queryFn: () => apiFetch(`/safras?skip=${pageIndex * 10}&limit=10`),
  });

  const createMut = useMutation({
    mutationFn: (safra: SafraCreate) => 
      apiFetch("/safras", { method: "POST", body: JSON.stringify(safra) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["safras"] });
      toast.success("Safra criada!");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return isLoading ? <Skeleton /> : <div>{/* render */}</div>;
}
```

### 5.3 Data Table — Padrão Obrigatório
```tsx
// Sempre com coluna de ação no final
const columns: ColumnDef<Safra>[] = [
  {
    id: "ano_safra",
    header: "Safra",
    accessorKey: "ano_safra",
  },
  {
    id: "cultura",
    header: "Cultura",
    accessorKey: "cultura",
  },
  // ... mais colunas
  {
    id: "acoes",  // ou "actions"
    header: "",   // NUNCA texto
    exportable: false,
    sortable: false,
    filterable: false,
    cell: (_, row) => (
      <div className="flex items-center gap-0 justify-end">
        <Button
          size="icon"
          variant="ghost"
          className="size-7 text-primary hover:text-primary"
          aria-label="Visualizar"
          asChild
        >
          <Link href={`/dashboard/agricola/safras/${row.id}`}>
            <Eye className="size-3.5" />
          </Link>
        </Button>
        <Button
          size="icon"
          variant="ghost"
          className="size-7 text-primary hover:text-primary"
          aria-label="Editar"
          onClick={() => handleEdit(row)}
        >
          <Pencil className="size-3.5" />
        </Button>
        <Button
          size="icon"
          variant="ghost"
          className="size-7 text-destructive hover:text-destructive"
          aria-label="Excluir"
          onClick={() => handleDelete(row.id)}
        >
          <Trash2 className="size-3.5" />
        </Button>
      </div>
    ),
  },
];

// Ícones canônicos (READ CODE FROM button.tsx, input.tsx, etc)
// Eye, Pencil, Trash2, MoreHorizontal, Plus, ChevronRight, etc
```

### 5.4 Forms — react-hook-form + Zod
```tsx
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const safraSchema = z.object({
  ano_safra: z.string().min(1, "Ano safra obrigatório"),
  cultura: z.string().min(1, "Cultura obrigatória"),
  area_plantada_ha: z.number().positive("Área deve ser positiva").optional(),
  talhao_id: z.string().uuid("Talhão inválido"),
});

type SafraFormData = z.infer<typeof safraSchema>;

export function SafraForm({ onSubmit }: { onSubmit: (data: SafraFormData) => void }) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<SafraFormData>({
    resolver: zodResolver(safraSchema),
    defaultValues: { talhao_id: "" },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label>Ano Safra *</Label>
        <Input {...register("ano_safra")} placeholder="Ex: 2024/25" />
        {errors.ano_safra && <p className="text-xs text-destructive">{errors.ano_safra.message}</p>}
      </div>
      <Button type="submit">Salvar</Button>
    </form>
  );
}
```

### 5.5 State Management — Zustand
```typescript
// lib/stores/app-store.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AppState {
  activeFazendaId: string | null;
  activeModule: string;
  sidebarOpen: boolean;
  setActiveFazenda: (id: string) => void;
  setActiveModule: (module: string) => void;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      activeFazendaId: null,
      activeModule: "dashboard",
      sidebarOpen: true,
      setActiveFazenda: (id) => set({ activeFazendaId: id }),
      setActiveModule: (module) => set({ activeModule: module }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    }),
    {
      name: "app-store",
      partialize: (state) => ({ activeFazendaId: state.activeFazendaId }),
    }
  )
);
```

---

## 6. Fluxos Comuns de Desenvolvimento

### 6.1 Criar Novo Endpoint
```
1. Backend (models → service → router → migration)
   ├─ services/api/agricola/novo_feature/models.py    (SQLAlchemy)
   ├─ services/api/agricola/novo_feature/schemas.py   (Pydantic)
   ├─ services/api/agricola/novo_feature/service.py   (BaseService)
   ├─ services/api/agricola/novo_feature/router.py    (APIRouter)
   ├─ Registrar router em main.py (linha 91-130)
   └─ Alembic migration se schema muda

2. Frontend
   ├─ apps/web/src/app/(dashboard)/dashboard/novo_feature/page.tsx
   ├─ apps/web/src/components/novo_feature/                (domain components)
   └─ packages/zod-schemas/src/index.ts (atualizar schemas compartilhados)

3. Testar
   ├─ Backend: pytest ./tests/agricola/test_novo_feature.py
   ├─ Frontend: npm test (em apps/web)
   └─ Integration: Postman ou curl

4. Commit & PR
   ├─ git add . && git commit -m "feat(novo_feature): descrição"
   └─ Abrir PR, deploy automático em staging/prod via CI
```

### 6.2 Adicionar Permissão Nova
```
1. core/constants.py — Adicionar permissão
   PERMISSION_MAP = {
       "agricola:novo_feature:ler": ["Gerente", "Operador"],
       "agricola:novo_feature:criar": ["Gerente"],
   }

2. Decorator no router
   @require_tenant_permission("agricola:novo_feature:ler")
   async def list_novo(...):
       ...

3. Tests — Verificar isolamento de tenant
   def test_novo_feature_tenant_isolation():
       # Usuário A não vê dados de Tenant B
```

### 6.3 Adicionar Módulo Feature Gate
```
1. core/constants.py
   MODULOS = {
       "A1_PLANEJAMENTO": {"tier": PlanTier.ESSENCIAL, "label": "Planejamento"},
       "A2_OPERACOES": {"tier": PlanTier.PROFISSIONAL, "label": "Operações"},
   }

2. Router
   @require_module("A2_OPERACOES")
   async def listar_operacoes(...):
       ...

3. Frontend
   const { activeModule } = useAppStore();
   // Renderizar apenas se modulo contratado
```

---

## 7. Testes

### Backend — pytest
```bash
cd services/api
pytest tests/agricola/test_safras.py -v
pytest tests/ -k "tenant_isolation" -v  # Testes de segurança
```

**Exemplo test isolamento de tenant:**
```python
@pytest.mark.asyncio
async def test_safra_tenant_isolation(session, tenant1, tenant2):
    """Usuário de tenant1 não vê safras de tenant2"""
    service1 = SafraService(session, tenant1.id)
    service2 = SafraService(session, tenant2.id)
    
    # Criar safra em tenant1
    safra = await service1.create(SafraCreate(ano_safra="2024", cultura="Soja"))
    
    # Tenant2 não pode acessar
    with pytest.raises(EntityNotFoundError):
        await service2.get_or_fail(safra.id)
```

### Frontend — vitest + React Testing Library
```bash
cd apps/web
npm test
npm test -- --ui  # Abrir test UI
```

---

## 8. Performance & Otimizações

### Query Optimization
```python
# ❌ N+1 queries
safras = await service.list_all()
for safra in safras:
    print(safra.talhoes)  # Executa query por safra!

# ✅ Eager loading
stmt = select(Safra).options(selectinload(Safra.talhoes))
safras = await session.execute(stmt)

# ✅ Batch query (para muitos registros)
from sqlalchemy import and_
stmt = select(Safra).where(and_(
    Safra.tenant_id == tenant_id,
    Safra.status.in_(["ATIVA", "FINALIZADA"])
)).offset(skip).limit(limit)
```

### Pagination (Always!)
```python
# Backend — sempre com skip/limit
@router.get("/")
async def list_safras(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    ...
):
    service = SafraService(session, tenant_id)
    return await service.list_all(skip=skip, limit=limit)

# Frontend
const { data } = useQuery({
  queryKey: ["safras", page],
  queryFn: () => apiFetch(`/safras?skip=${page * 10}&limit=10`),
});
```

### Índices — No Schema
```python
# Models.py — Índices para queries frequentes
class Safra(Base):
    __table_args__ = (
        Index("ix_safras_tenant_status", tenant_id, status),  # Composite
        Index("ix_safras_cultura", cultura),
        Index("ix_safras_created_at", created_at, order_by="DESC"),
    )
```

### Context Efficiency Rules
```
1. Bash: git, mkdir, rm, mv APENAS
2. >10 linhas output: ctx_execute ou ctx_batch_execute
3. Grep: sempre com --glob patterns
4. Read: APENAS para Edit ou schemas não-analíticos
5. Response: máx 150 palavras, artefatos em FILES
```

---

## 9. Known Issues & Soluções

### CORS After main.py Changes
```bash
# Problema: CORS error após editar main.py
# Solução:
cd services/api
pkill -f "uvicorn"
./start_server.sh
```

### Alembic Async — Silent Rollback
```python
# ❌ Problema: Migration roda mas nada salva
def upgrade():
    with op.batch_alter_table(...) as batch:
        batch.add_column(...)
    # Sem commit, rollback silencioso!

# ✅ Solução:
def upgrade():
    with op.batch_alter_table(...) as batch:
        batch.add_column(...)
    op.execute("COMMIT")  # Força commit
```

### Router Not Registered
```python
# Problema: Endpoint retorna 404
# Solução: Adicionar em main.py (linha ~110)
from agricola.novo_router import router as novo_router
app.include_router(novo_router, prefix="/api/v1")
```

### SQLite — No RLS
```
Não utilizar o SQLite, somente se for solicitado
RLS policies em PostgreSQL não funcionam em SQLite.
Para dev local, use PostgreSQL conforme configuração .env
```

---

## 10. Estrutura de Módulos Agrícola

**22 submódulos dentro de `/services/api/agricola/`:**

| Submódulo | Função | Tier |
|-----------|--------|------|
| `a1_planejamento` | Orçamento, safra, talhões | ESSENCIAL |
| `safras` | CRUD Safra + Fases | ESSENCIAL |
| `romaneios` | Colheita + romaneios | ESSENCIAL |
| `beneficiamento` | Pós-colheita (café) | PROFISSIONAL |
| `operacoes` | Tratos culturais | PROFISSIONAL |
| `ndvi` | Índices de vegetação | ENTERPRISE |
| `climatico` | Dados climáticos | PROFESSIONAL |
| `analises_solo` | Laudo de solo | ESSENCIAL |
| `amostragem_solo` | Coleta de amostras | PROFESSIONAL |
| `fenologia` | Estágios da planta | PROFESSIONAL |
| `prescricoes` | Receituário | PROFESSIONAL |
| `irrigacao` | Manejo de irrigação | PROFESSIONAL |
| `monitoramento` | Pragas e doenças | PROFESSIONAL |
| `custos` | Custo por operação | PROFESSIONAL |
| `financeiro_kpis` | KPIs financeiros | ESSENCIAL |
| `rastreabilidade` | Rastreio de lote | ENTERPRISE |
| `dashboard` | Dashboard agrícola | ESSENCIAL |
| `checklist` | Checklists operacional | PROFESSIONAL |
| `agronomo` | Visitas e laudos | PROFESSIONAL |
| `alertas` | Alertas e notificações | PROFESSIONAL |
| `previsoes` | Modelo preditivo | ENTERPRISE |
| `cadastros` | Dados mestres | ESSENCIAL |

---

## 11. Referências Rápidas

### Import Padrões
```python
# Backend
from core.base_service import BaseService
from core.dependencies import get_tenant_id, require_tenant_permission
from core.exceptions import EntityNotFoundError, TenantViolationError
from sqlalchemy import select, and_, insert, update, delete
from pydantic import BaseModel

# Frontend
import { useQuery, useMutation } from "@tanstack/react-query";
import { useAppStore } from "@/lib/stores/app-store";
import { apiFetch } from "@/lib/api";
import { useForm } from "react-hook-form";
import { Button, Input, Card } from "@/components/ui";
```

### Links Essenciais
- Roadmap: `/docs/PROXIMOS_PASSOS.md`
- RBAC: `/IMPLEMENTACAO_RBAC_MULTI_SUB.md`
- Frontend Patterns: `/FRONTEND_MAINTENANCE_GUIDE.md`
- CORS Issues: `/services/api/CORS_TROUBLESHOOTING.md`
- Module Contexts: `/docs/contexts/`
- Brainstorms: `/docs/brainstorm-*.md`

### Dev Server Commands
```bash
# Backend
cd services/api && ./start_server.sh

# Frontend
cd apps/web && pnpm dev

# Watch mode
cd services/api && alembic upgrade head && ./start_server.sh

# Kill all
pkill -f "uvicorn|next dev"
```

---

**Última atualização:** 2026-04-15  
**Maintainer:** Borgus Software Ltda  
**Stack versão:** FastAPI 0.115+, Next.js 16, React 19, SQLAlchemy 2.0
