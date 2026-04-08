# AgroSaaS — Global Development Rules
> **Versão:** 1.0.0 · **Status:** Ativo · **Owners:** Tech Lead + Arquiteto  
> Stack: Next.js 16 · Python 3.12 / FastAPI · PostgreSQL 16 · K3s On-Premise

---

## Índice

1. [Princípios Fundamentais](#1-princípios-fundamentais)
2. [Arquitetura & Estrutura de Pastas](#2-arquitetura--estrutura-de-pastas)
3. [Padrões de Código — Python](#3-padrões-de-código--python)
4. [Padrões de Código — TypeScript / Next.js](#4-padrões-de-código--typescript--nextjs)
5. [Boas Práticas de Engenharia](#5-boas-práticas-de-engenharia)
6. [Segurança & Multitenancy](#6-segurança--multitenancy)
7. [Banco de Dados & Migrations](#7-banco-de-dados--migrations)
8. [Testes & Cobertura Mínima](#8-testes--cobertura-mínima)
9. [Git, Commits & PR Workflow](#9-git-commits--pr-workflow)
10. [Checklist de Code Review](#10-checklist-de-code-review)
11. [Arquitetura de Módulos de Negócio](#11-arquitetura-de-módulos-de-negócio)

---

## 1. Princípios Fundamentais

Estas regras têm força de **lei técnica** no projeto. Todo desenvolvedor que escreve, revisa ou aprova código é responsável pelo cumprimento.

### 1.1 Os Cinco Mandamentos

```
1. CLAREZA > ESPERTEZA     — Código óbvio é melhor que código brilhante.
2. FALHE CEDO, FALHE CLARO — Valide entradas na borda, erro explícito > comportamento silencioso.
3. ZERO CONFIANÇA IMPLÍCITA — Nunca assuma que o caller é do mesmo tenant. Sempre verifique.
4. DADOS SÃO SAGRADOS      — Nunca mute banco sem migration versionada e testada.
5. O TIME LE O CÓDIGO       — Escreva para o próximo dev, não para o compilador.
```

### 1.2 Princípios de Design (obrigatórios)

| Princípio | Aplicação no AgroSaaS |
|---|---|
| **SRP** — Single Responsibility | Cada classe/função tem uma razão para mudar. `AnimalService` cuida de animal, não de pesagem. |
| **DRY** — Don't Repeat Yourself | Lógica de negócio existe em um lugar. Validação Zod/Pydantic é a fonte da verdade. |
| **YAGNI** — You Aren't Gonna Need It | Não abstrai antes da 3ª ocorrência. Evite over-engineering de módulos futuros. |
| **OCP** — Open/Closed | Extensível (novos módulos/plugins) sem modificar o core. Use dependency injection. |
| **DI** — Dependency Injection | Services recebem dependências (session, tenant_id) via parâmetro. Jamais instanciam internamente. |
| **FAIL FAST** | Valide entradas no início da função. Retorne ou lance exceção antes de processar. |

---

## 2. Arquitetura & Estrutura de Pastas

### 2.1 Visão Geral do Monorepo

```
agrosass/
├── apps/
│   ├── web/                    # Next.js 16 (frontend)
│   └── mobile/                 # React Native / Expo 52
├── services/
│   ├── api-core/               # FastAPI — auth, tenant, usuários
│   ├── api-agricola/           # FastAPI — safra, lavoura, insumos
│   ├── api-pecuaria/           # FastAPI — rebanho, reprodução, sanidade
│   ├── api-financeiro/         # FastAPI — contas, NF-e, fiscal
│   ├── api-operacional/        # FastAPI — máquinas, RH, estoque
│   └── api-ia/                 # FastAPI — LLM, ML, diagnóstico
├── packages/
│   ├── types/                  # Tipos TypeScript compartilhados (web + mobile)
│   ├── zod-schemas/            # Schemas de validação compartilhados
│   └── utils/                  # Utilitários puros sem side-effects
├── infra/
│   ├── k8s/                    # Manifests K3s/Kubernetes
│   ├── ansible/                # Playbooks de provisionamento
│   └── docker/                 # Dockerfiles e compose files
├── .gitea/
│   └── workflows/              # CI/CD pipelines
└── docs/                       # Documentação técnica
```

### 2.2 Estrutura de Cada Microsserviço Python

```
api_{dominio}/
├── main.py                     # FastAPI factory + lifespan hooks
├── dependencies.py             # Injeção: tenant_id, user, session, feature gates
├── database.py                 # Engine async + session maker
├── config.py                   # Settings via pydantic-settings (env vars)
├── models/                     # SQLAlchemy 2.0 models (1 arquivo por entidade)
│   └── animal.py
├── schemas/                    # Pydantic v2 schemas
│   ├── animal_input.py         # Request body schemas
│   └── animal_output.py        # Response schemas (nunca retornar model raw)
├── services/                   # Lógica de negócio (herda BaseService)
│   └── animal_service.py
├── routers/                    # FastAPI routers (1 por recurso)
│   └── animais.py
├── tasks/                      # Celery tasks
│   └── alertas.py
├── migrations/                 # Alembic
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── Dockerfile
└── pyproject.toml
```

**Regras de organização:**
- ❌ Nunca importar de `services/` dentro de `routers/` diretamente — use Depends()
- ❌ Nunca colocar lógica de negócio em `routers/` — apenas validação de entrada e chamada de service
- ❌ Nunca retornar um SQLAlchemy model diretamente — sempre serializar via schema Pydantic
- ✅ Um router por recurso REST, um service por agregado de domínio

### 2.3 Estrutura do Frontend Next.js

```
apps/web/
├── app/                        # App Router (Next.js 16)
│   ├── (auth)/                 # Route group — sem layout de dashboard
│   │   └── login/
│   ├── (dashboard)/            # Route group — com layout autenticado
│   │   ├── layout.tsx          # Server Layout: injeta tenant + módulos
│   │   ├── agricola/
│   │   ├── pecuaria/
│   │   │   └── rebanho/
│   │   │       ├── page.tsx    # Server Component (RSC)
│   │   │       └── loading.tsx # Skeleton automático (Suspense)
│   │   └── financeiro/
│   └── api/                    # Route Handlers (BFF proxy)
├── components/
│   ├── ui/                     # shadcn/ui (copiados, não importados)
│   ├── {dominio}/              # Componentes por domínio
│   │   └── rebanho-grid.tsx    # Client Component ("use client")
│   └── shared/                 # Componentes reutilizáveis entre domínios
│       ├── module-gate.tsx     # HOC de feature flag
│       └── data-table.tsx      # Wrapper AG Grid padronizado
├── lib/
│   ├── api/                    # Fetch functions (usadas nos RSC)
│   ├── stores/                 # Zustand stores
│   ├── hooks/                  # TanStack Query hooks (1 arquivo por domínio)
│   ├── modules.ts              # Helpers de feature flag
│   └── utils.ts                # cn(), formatters, etc.
├── types/                      # Re-exports do package @agrosass/types
└── middleware.ts               # Edge middleware (auth + tenant)
```

**Regras de organização:**
- ✅ Por padrão, todo componente é Server Component. Adicione `"use client"` apenas quando necessário
- ✅ `page.tsx` é sempre RSC — busca dados no servidor e passa para Client Components
- ❌ Nunca use `fetch()` em Client Components para dados iniciais — use TanStack Query para refetch/mutations
- ❌ Nunca importe um Client Component diretamente em um RSC sem `Suspense`

---

## 3. Padrões de Código — Python

### 3.1 Configuração Obrigatória

Todo microsserviço **deve** ter estas ferramentas configuradas no `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py312"
line-length = 100
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "S",   # bandit (security)
    "N",   # pep8-naming
]
ignore = ["S101"]  # permite assert em testes

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = false

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### 3.2 Type Hints — Obrigatório em Todo Código

```python
# ❌ PROIBIDO — sem type hints
def criar_animal(dados, session, tenant):
    ...

# ✅ CORRETO — type hints completos
async def criar_animal(
    dados: AnimalCreate,
    session: AsyncSession,
    tenant_id: UUID,
) -> AnimalResponse:
    ...
```

### 3.3 Schemas Pydantic — Padrão Input/Output

Cada recurso deve ter schemas separados para entrada e saída. Nunca expor o model ORM diretamente.

```python
# schemas/animal_input.py
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import date

class AnimalCreate(BaseModel):
    brinco_visual: str = Field(..., min_length=1, max_length=20)
    raca: str = Field(..., min_length=2, max_length=50)
    sexo: Literal["M", "F"]
    categoria: CategoriaAnimal  # Enum — não string livre
    data_nascimento: date | None = None
    lote_id: UUID | None = None

    @field_validator("brinco_visual")
    @classmethod
    def normalizar_brinco(cls, v: str) -> str:
        return v.strip().upper()  # padroniza na entrada

# schemas/animal_output.py
class AnimalResponse(BaseModel):
    id: UUID
    brinco_visual: str
    categoria: CategoriaAnimal
    idade_meses: int  # calculado, não salvo no banco
    ultimo_peso_kg: float | None
    gmd_30d: float | None

    model_config = ConfigDict(from_attributes=True)
```

### 3.4 Services — Padrão de Implementação

```python
# services/animal_service.py
from .base_service import BaseService
from ..models.animal import Animal
from ..schemas.animal_input import AnimalCreate, PesagemCreate
from ..schemas.animal_output import AnimalResponse

class AnimalService(BaseService[Animal]):
    """
    Responsabilidade única: operações de domínio sobre Animal.
    NÃO lida com HTTP, NÃO conhece Request/Response.
    """

    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(Animal, session, tenant_id)

    async def criar(self, dados: AnimalCreate) -> Animal:
        # Valida regras de negócio antes de persistir
        if dados.lote_id:
            lote = await self._verificar_lote_existe(dados.lote_id)
            if lote.fazenda.tenant_id != self.tenant_id:
                raise TenantViolationError("Lote não pertence ao tenant")

        return await super().create(dados.model_dump())

    async def registrar_pesagem(
        self,
        animal_id: UUID,
        dados: PesagemCreate,
    ) -> Pesagem:
        animal = await self.get(animal_id)
        if not animal:
            raise EntityNotFoundError(f"Animal {animal_id} não encontrado")

        # Lógica de negócio isolada no service
        gmd = self._calcular_gmd(animal.ultima_pesagem, dados)
        pesagem = Pesagem(
            animal_id=animal_id,
            tenant_id=self.tenant_id,
            peso_kg=dados.peso_kg,
            data_pesagem=dados.data_pesagem,
            gmd_desde_anterior=gmd,
        )
        self.session.add(pesagem)
        await self.session.commit()
        return pesagem

    def _calcular_gmd(
        self,
        ultima: Pesagem | None,
        nova: PesagemCreate,
    ) -> float | None:
        """Método privado — lógica pura, fácil de testar."""
        if not ultima:
            return None
        dias = (nova.data_pesagem - ultima.data_pesagem).days
        if dias <= 0:
            return None
        return round((nova.peso_kg - ultima.peso_kg) / dias, 3)
```

### 3.5 Routers — Padrão de Implementação

```python
# routers/animais.py
from fastapi import APIRouter, Depends, Query, status
from uuid import UUID

router = APIRouter(prefix="/animais", tags=["Rebanho — Animais"])

@router.get(
    "/",
    response_model=PaginatedResponse[AnimalResponse],
    summary="Lista animais do rebanho",
)
async def listar_animais(
    # Parâmetros de filtro
    categoria: CategoriaAnimal | None = Query(None),
    lote_id: UUID | None = Query(None),
    busca: str | None = Query(None, max_length=100),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(50, ge=1, le=500),
    # Dependencies — injetadas pelo FastAPI
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("PECUARIA_P1")),  # feature gate
    _user: dict = Depends(require_role("veterinario", "admin", "operador")),
):
    svc = AnimalService(session, tenant_id)
    return await svc.listar_paginado(
        pagina=pagina,
        por_pagina=por_pagina,
        categoria=categoria,
        lote_id=lote_id,
        busca=busca,
    )

@router.post(
    "/",
    response_model=AnimalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra novo animal",
)
async def criar_animal(
    dados: AnimalCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("PECUARIA_P1")),
    _user: dict = Depends(require_role("veterinario", "admin")),
):
    svc = AnimalService(session, tenant_id)
    animal = await svc.criar(dados)
    return AnimalResponse.model_validate(animal)
```

### 3.6 Tratamento de Erros

```python
# exceptions.py — exceções de domínio
class AgroSaaSError(Exception):
    """Base para todas as exceções do domínio."""
    pass

class EntityNotFoundError(AgroSaaSError):
    pass

class TenantViolationError(AgroSaaSError):
    """Tentativa de acesso a dados de outro tenant."""
    pass

class ModuleNotContractedError(AgroSaaSError):
    pass

class BusinessRuleError(AgroSaaSError):
    """Violação de regra de negócio."""
    pass

# main.py — handlers globais
@app.exception_handler(EntityNotFoundError)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(TenantViolationError)
async def tenant_violation_handler(request, exc):
    # Log como incidente de segurança — não vazar detalhes
    logger.warning(f"TENANT_VIOLATION: {request.headers.get('x-tenant-id')} — {exc}")
    return JSONResponse(status_code=403, content={"detail": "Acesso negado"})

@app.exception_handler(BusinessRuleError)
async def business_rule_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": str(exc)})
```

### 3.7 Logging Estruturado

```python
# Configuração — main.py
from loguru import logger
import sys

logger.configure(handlers=[{
    "sink": sys.stdout,
    "format": "{time:YYYY-MM-DDThh:mm:ssZ} | {level} | {name}:{function}:{line} | {message}",
    "serialize": True,  # JSON — compatível com Loki/Grafana
}])

# Uso em qualquer arquivo
logger.info("Pesagem registrada", animal_id=str(animal_id), peso=peso_kg, tenant=str(tenant_id))
logger.warning("GMD abaixo do mínimo", animal_id=str(animal_id), gmd=gmd, minimo=animal.gmd_minimo)
logger.error("Falha ao emitir NF-e", nota_id=str(nota_id), erro=str(exc))

# ❌ NUNCA logar dados sensíveis
logger.info("Login", cpf=cpf)          # PROIBIDO
logger.info("Pagamento", valor=valor)  # PROIBIDO
```

---

## 4. Padrões de Código — TypeScript / Next.js

### 4.1 Configuração TSConfig Obrigatória

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "exactOptionalPropertyTypes": true,
    "moduleResolution": "bundler",
    "target": "ES2022"
  }
}
```

### 4.2 Convenções de Nomenclatura

| Tipo | Convenção | Exemplo |
|---|---|---|
| Componentes | PascalCase | `RebanhoGrid`, `AnimalCard` |
| Hooks | camelCase com `use` | `useRebanho`, `useRegistrarPesagem` |
| Stores Zustand | camelCase com `use` + `Store` | `useAppStore`, `useRebanhoStore` |
| Funções utilitárias | camelCase | `formatPeso`, `calcularGMD` |
| Tipos / Interfaces | PascalCase | `Animal`, `PesagemInput` |
| Enums | PascalCase | `CategoriaAnimal`, `StatusSafra` |
| Constantes globais | SCREAMING_SNAKE | `MAX_ANIMAIS_POR_LOTE` |
| Arquivos de componente | kebab-case | `rebanho-grid.tsx` |
| Arquivos de hook | kebab-case | `use-rebanho.ts` |

### 4.3 Server vs Client Components — Regra de Ouro

```typescript
// ✅ Server Component (padrão) — sem "use client"
// - Busca dados diretamente (banco, API, cache)
// - Não tem estado nem event handlers
// - Bundle JS zero no cliente para esta lógica
// app/(dashboard)/pecuaria/rebanho/page.tsx
export default async function RebanhoPage({ searchParams }) {
  const data = await fetchRebanho({ ...searchParams })
  return <RebanhoGrid animais={data.animais} /> // passa para Client Component
}

// ✅ Client Component — apenas quando necessário
// - Estado interativo (useState, useReducer)
// - Event handlers (onClick, onChange)
// - Browser APIs (window, localStorage, navigator)
// - Hooks de terceiros (TanStack Query, Zustand)
// components/pecuaria/rebanho-grid.tsx
"use client"
import { useState } from "react"
export function RebanhoGrid({ animais }: { animais: Animal[] }) { ... }

// ❌ PROIBIDO — "use client" em page.tsx
"use client" // NUNCA em arquivos de rota
export default function RebanhoPage() { ... }
```

### 4.4 TanStack Query — Padrão de Hooks

```typescript
// hooks/pecuaria/use-rebanho.ts

// 1. Query keys tipadas e centralizadas
export const rebanhoKeys = {
  all: ["rebanho"] as const,
  list: (tenantId: string, filters: RebanhoFilters) =>
    [...rebanhoKeys.all, "list", tenantId, filters] as const,
  detail: (id: string) =>
    [...rebanhoKeys.all, "detail", id] as const,
}

// 2. Hook de listagem
export function useRebanho(filters: RebanhoFilters = {}) {
  const { tenant } = useAppStore()

  return useQuery({
    queryKey: rebanhoKeys.list(tenant!.id, filters),
    queryFn: () => api.pecuaria.listarAnimais(tenant!.id, filters),
    staleTime: 5 * 60 * 1000,  // 5 min — dados de rebanho mudam pouco
    placeholderData: keepPreviousData,  // sem flash ao trocar filtros
    enabled: !!tenant,
  })
}

// 3. Mutation com optimistic update
export function useRegistrarPesagem() {
  const qc = useQueryClient()
  const { tenant } = useAppStore()

  return useMutation({
    mutationFn: (data: PesagemInput) =>
      api.pecuaria.registrarPesagem(tenant!.id, data),

    onMutate: async (nova) => {
      await qc.cancelQueries({ queryKey: rebanhoKeys.all })
      const snapshot = qc.getQueryData(rebanhoKeys.detail(nova.animalId))
      // Atualiza UI otimisticamente
      qc.setQueryData(rebanhoKeys.detail(nova.animalId), (old: Animal) => ({
        ...old,
        ultimoPesoKg: nova.pesoKg,
      }))
      return { snapshot }
    },
    onError: (_, vars, ctx) => {
      // Reverte em caso de erro
      qc.setQueryData(rebanhoKeys.detail(vars.animalId), ctx?.snapshot)
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: rebanhoKeys.all })
    },
  })
}
```

### 4.5 Formulários — Padrão com Zod + React Hook Form

```typescript
// O schema Zod é a fonte da verdade — compartilhado com o backend
// packages/zod-schemas/src/pecuaria/pesagem.ts
import { z } from "zod"

export const pesagemSchema = z.object({
  animalId: z.string().uuid("ID do animal inválido"),
  pesoKg: z
    .number({ required_error: "Peso é obrigatório" })
    .positive("Peso deve ser maior que zero")
    .max(2000, "Peso excede o máximo permitido"),
  dataPesagem: z.coerce.date(),
  tipo: z.enum(["NASCIMENTO", "DESMAMA", "ROTINA", "EMBARQUE", "ABATE"]),
})

export type PesagemInput = z.infer<typeof pesagemSchema>

// components/pecuaria/pesagem-form.tsx
"use client"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

export function PesagemForm({ animalId }: { animalId: string }) {
  const { mutate, isPending } = useRegistrarPesagem()

  const form = useForm<PesagemInput>({
    resolver: zodResolver(pesagemSchema),
    defaultValues: {
      animalId,
      tipo: "ROTINA",
      dataPesagem: new Date(),
    },
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit((data) => mutate(data))}>
        {/* Campos do formulário */}
      </form>
    </Form>
  )
}
```

### 4.6 Zustand Store — Padrão

```typescript
// lib/stores/app-store.ts
import { create } from "zustand"
import { persist } from "zustand/middleware"
import { immer } from "zustand/middleware/immer"

// ✅ Interface tipada e explícita
interface AppState {
  // Estado
  tenant: Tenant | null
  user: User | null
  modules: string[]
  activeFazendaId: string | null
  // Actions — nomeadas como verbos
  setTenant: (tenant: Tenant) => void
  setModules: (modules: string[]) => void
  hasModule: (moduleId: ModuleId) => boolean
  setActiveFazenda: (id: string) => void
  reset: () => void
}

const initialState = {
  tenant: null,
  user: null,
  modules: [],
  activeFazendaId: null,
}

export const useAppStore = create<AppState>()(
  persist(
    immer((set, get) => ({
      ...initialState,
      setTenant: (tenant) => set((s) => { s.tenant = tenant }),
      setModules: (modules) => set((s) => { s.modules = modules }),
      hasModule: (id) => get().modules.includes(id),
      setActiveFazenda: (id) => set((s) => { s.activeFazendaId = id }),
      reset: () => set(initialState),
    })),
    {
      name: "agro-app-state",
      // Persiste apenas o necessário — não persiste dados sensíveis
      partialize: (s) => ({ activeFazendaId: s.activeFazendaId }),
    }
  )
)
```

---

## 5. Boas Práticas de Engenharia

### 5.1 DRY — Não Repita Lógica de Negócio

```python
# ❌ VIOLAÇÃO DRY — lógica de GMD duplicada em 3 lugares
# router/animais.py
gmd = (nova_pesagem - ultima_pesagem) / dias_entre_pesagens

# router/relatorios.py  
gmd = (peso_atual - peso_anterior) / diferenca_dias

# tasks/alertas.py
gmd_calculado = (peso_novo - peso_velho) / total_dias

# ✅ CORRETO — lógica em um único lugar
# domain/pecuaria/calculos.py
def calcular_gmd(peso_inicial: float, peso_final: float, dias: int) -> float | None:
    """
    Calcula o Ganho Médio Diário entre duas pesagens.
    Retorna None se o intervalo for <= 0 dias.
    """
    if dias <= 0:
        return None
    return round((peso_final - peso_inicial) / dias, 3)

# Todos os pontos importam e usam calcular_gmd()
```

### 5.2 SRP — Uma Responsabilidade por Módulo

```python
# ❌ VIOLAÇÃO SRP — AnimalService faz tudo
class AnimalService:
    async def criar(self): ...
    async def listar(self): ...
    async def registrar_pesagem(self): ...      # ← responsabilidade de Pesagem
    async def aplicar_vacina(self): ...         # ← responsabilidade de Sanidade
    async def registrar_parto(self): ...        # ← responsabilidade de Reprodução
    async def enviar_alerta_whatsapp(self): ... # ← responsabilidade de Notificação
    async def calcular_dre_lote(self): ...      # ← responsabilidade de Financeiro

# ✅ CORRETO — responsabilidades separadas
class AnimalService(BaseService[Animal]):
    """Somente: CRUD de Animal + regras do agregado Animal."""

class PesagemService(BaseService[Pesagem]):
    """Somente: registro e consulta de pesagens."""

class SanidadeService:
    """Somente: vacinações, vermifugações, protocolos."""

class ReproducaoService:
    """Somente: IATF, partos, diagnósticos."""
```

### 5.3 Design Patterns Aprovados

#### Factory Pattern — para objetos complexos

```python
# domain/financeiro/nota_fiscal_factory.py
class NotaFiscalFactory:
    """Constrói NF-e com todas as validações fiscais aplicadas."""

    @staticmethod
    def criar_de_venda_animais(
        venda: VendaAnimais,
        tenant: Tenant,
    ) -> NotaFiscal:
        NotaFiscalFactory._validar_dados_emitente(tenant)
        NotaFiscalFactory._validar_dados_destinatario(venda.comprador)
        itens = [NotaFiscalFactory._criar_item_animal(a) for a in venda.animais]
        impostos = ImpostoCalculator.calcular(itens, tenant.regime_tributario)
        return NotaFiscal(
            tenant_id=tenant.id,
            itens=itens,
            impostos=impostos,
            natureza_operacao="VENDA DE ANIMAIS",
        )
```

#### Strategy Pattern — para variações de comportamento

```python
# domain/ia/diagnostico_strategy.py
from abc import ABC, abstractmethod

class DiagnosticoPragaStrategy(ABC):
    @abstractmethod
    async def diagnosticar(self, imagem: bytes) -> DiagnosticoResult:
        pass

class YOLOv11Strategy(DiagnosticoPragaStrategy):
    """Diagnóstico local via ONNX — offline-capable."""
    async def diagnosticar(self, imagem: bytes) -> DiagnosticoResult:
        ...

class OllamaVisionStrategy(DiagnosticoPragaStrategy):
    """Diagnóstico via LLM local com visão."""
    async def diagnosticar(self, imagem: bytes) -> DiagnosticoResult:
        ...

class DiagnosticoService:
    def __init__(self, strategy: DiagnosticoPragaStrategy):
        self._strategy = strategy  # injetado via DI

    async def diagnosticar(self, imagem: bytes) -> DiagnosticoResult:
        return await self._strategy.diagnosticar(imagem)
```

#### Repository Pattern — já implementado via BaseService

O `BaseService` funciona como Repository — acesso a dados centralizado, testável via mock da session.

#### Observer Pattern — para eventos de domínio

```python
# domain/events.py
from dataclasses import dataclass
from uuid import UUID

@dataclass
class PesagemRegistradaEvent:
    animal_id: UUID
    tenant_id: UUID
    peso_kg: float
    gmd: float | None

# Em PesagemService.registrar():
# Após commit, publica o evento no Redis pub/sub
# Celery worker consome e dispara alertas se necessário
```

### 5.4 Funções — Regras de Ouro

```python
# Regra 1: Funções fazem UMA coisa
# ❌ Nome com "e" = sinal de violação SRP
async def validar_e_salvar_e_notificar_pesagem(): ...

# ✅ Separadas
async def validar_pesagem(dados: PesagemCreate) -> None: ...
async def salvar_pesagem(animal: Animal, dados: PesagemCreate) -> Pesagem: ...
async def notificar_gmd_baixo(animal: Animal, gmd: float) -> None: ...

# Regra 2: Máximo 3 parâmetros posicionais — use dataclass/schema para mais
# ❌
async def criar_animal(brinco, raca, sexo, categoria, nascimento, lote_id, mae_id, pai_id):

# ✅
async def criar_animal(dados: AnimalCreate) -> Animal: ...

# Regra 3: Evite flags booleanas — prefira dois métodos explícitos
# ❌
async def listar_animais(incluir_inativos: bool = False): ...

# ✅
async def listar_animais_ativos(): ...
async def listar_todos_animais(): ...
```

---

## 6. Segurança & Multitenancy

### 6.1 Regras Absolutas de Segurança

```
NUNCA:
  - Confie em input do usuário sem validação Pydantic/Zod
  - Construa queries SQL com f-string ou concatenação
  - Logue dados sensíveis (CPF, senhas, tokens, valores financeiros)
  - Armazene secrets em código, .env commitado ou variáveis hardcoded
  - Retorne stack traces de Python para o cliente em produção
  - Ignore erros de TenantViolation — sempre logue como incidente

SEMPRE:
  - Valide tenant_id em TODA operação de banco, mesmo com RLS ativo
  - Use parameterized queries via SQLAlchemy ORM
  - Injete secrets apenas via HashiCorp Vault ou variáveis de ambiente seguras
  - Implemente rate limiting por tenant nas rotas críticas
  - Verifique permissão de módulo (require_module) antes de executar
  - Verifique role do usuário (require_role) antes de executar
```

### 6.2 Tenant Isolation — Defense in Depth

A segurança multi-tenant tem **três camadas independentes**:

```
Camada 1 — PostgreSQL RLS (banco de dados)
  ✓ SET LOCAL app.current_tenant_id = '<uuid>'
  ✓ Policy USING (tenant_id = current_setting(...)::uuid)
  ✓ Isolamento garantido mesmo se a aplicação falhar

Camada 2 — BaseService (aplicação)
  ✓ Todos os selects filtram por tenant_id explicitamente
  ✓ Não confia cegamente no RLS — adiciona WHERE sempre
  ✓ TenantViolationError se tenant não coincidir

Camada 3 — Middleware JWT (borda)
  ✓ Extrai tenant do subdomínio + valida JWT
  ✓ Injeta x-tenant-id header verificado em todas as requests
  ✓ Nenhum request chega aos services sem tenant validado
```

```python
# database.py — injeção do tenant_id na sessão PostgreSQL
from sqlalchemy import event, text

@event.listens_for(AsyncSession, "after_begin")
async def set_tenant_context(session, transaction, connection):
    tenant_id = session.info.get("tenant_id")
    if tenant_id:
        await connection.execute(
            text("SET LOCAL app.current_tenant_id = :tid"),
            {"tid": str(tenant_id)}
        )

# dependencies.py — como a session recebe o tenant
async def get_session_with_tenant(
    tenant_id: UUID = Depends(get_tenant_id),
) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        session.info["tenant_id"] = tenant_id  # injeta no contexto
        yield session
```

### 6.3 Secrets — Hierarquia de Acesso

```
Desenvolvimento local:
  .env.local (nunca commitado — no .gitignore obrigatório)
  
Staging / Produção:
  HashiCorp Vault → K8s Secrets Store CSI → /vault/secrets/
  Nunca em ConfigMaps, nunca em imagens Docker

Rotação:
  Credenciais de banco: Vault Dynamic Secrets (rotação automática a cada 24h)
  API keys externas: Vault KV com TTL de 90 dias
  Certificados TLS: cert-manager com renovação automática
```

```python
# config.py — NUNCA hardcode, sempre pydantic-settings
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str                     # obrigatório — erro explícito se ausente
    redis_url: str
    keycloak_public_key: str
    sefaz_certificate_path: str
    ollama_base_url: str = "http://ollama:11434"  # default seguro

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
    )

settings = Settings()  # instância única, importada por todos
```

### 6.4 Validação de Entradas

```python
# ✅ CORRETO — Pydantic valida na fronteira da aplicação
@router.post("/animais/{id}/pesagens")
async def registrar_pesagem(
    animal_id: UUID,           # FastAPI valida UUID automaticamente
    dados: PesagemCreate,      # Pydantic valida corpo completo
    tenant_id: UUID = Depends(get_tenant_id),
):
    # Aqui dentro: dados já é válido e tipado. Confiança total.
    ...

# ❌ PROIBIDO — validação manual após receber dados
@router.post("/animais/{id}/pesagens")
async def registrar_pesagem(animal_id: str, peso: float):
    if not animal_id:  # isso não deveria existir
        raise ...
    if peso <= 0:      # isso deve estar no schema Pydantic
        raise ...
```

---

## 7. Banco de Dados & Migrations

### 7.1 Regras de Migrations

```
NUNCA:
  - Faça ALTER TABLE em produção sem migration versionada
  - Delete colunas sem um ciclo de deprecação (3 passos)
  - Renomeie colunas diretamente (crie nova + migre + delete antiga)
  - Adicione NOT NULL sem DEFAULT em tabela com dados existentes
  - Crie índice com CREATE INDEX (use CREATE INDEX CONCURRENTLY)
  - Faça rollback de migration que já rodou em produção sem plano de dados

SEMPRE:
  - Crie migration para qualquer mudança de schema
  - Inclua downgrade() funcional em toda migration
  - Teste migration em staging antes da produção
  - Nomeie migrations de forma descritiva: 001_add_gmd_to_pesagens.py
  - Documente breaking changes no cabeçalho da migration
```

### 7.2 Padrão de Migration Alembic

```python
# migrations/versions/003_add_sisbov_to_animais.py
"""Add SISBOV column to animais table

Revision ID: 003abc123def
Revises: 002xyz789abc
Create Date: 2025-01-15 10:30:00

BREAKING CHANGES: Nenhum.
NOTAS: Coluna nullable — dados históricos não têm SISBOV.
ROLLBACK: Remove coluna — não há perda de dados se aplicado antes de produção.
"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # UNIQUE apenas para não-nulos (padrão para campos opcionais únicos)
    op.add_column(
        "animais",
        sa.Column("sisbov", sa.String(20), nullable=True),
    )
    op.create_index(
        "ix_animais_sisbov",
        "animais",
        ["sisbov"],
        unique=True,
        postgresql_where=sa.text("sisbov IS NOT NULL"),  # partial unique index
    )

def downgrade() -> None:
    op.drop_index("ix_animais_sisbov", table_name="animais")
    op.drop_column("animais", "sisbov")
```

### 7.3 Ciclo de Deprecação de Coluna (3 Passos)

```
Passo 1 — Migration: marcar coluna como deprecated (sem remover)
  ALTER TABLE animais ADD COLUMN nome_legado_deprecated boolean DEFAULT false;

Passo 2 — Código: parar de ler/escrever na coluna deprecated (1+ versão)
  # Remover do schema Pydantic, remover do ORM model

Passo 3 — Migration: remover fisicamente a coluna
  ALTER TABLE animais DROP COLUMN nome_legado_deprecated;
  # Apenas após o Passo 2 estar em produção por pelo menos 1 sprint
```

### 7.4 Convenções de Nomenclatura no Banco

```sql
-- Tabelas: plural, snake_case
animais, pesagens, lancamentos_financeiros, ordens_servico

-- Colunas: snake_case, sem prefixo de tabela
id, tenant_id, created_at, updated_at

-- Índices: ix_{tabela}_{coluna(s)}
ix_animais_tenant_categoria
ix_pesagens_animal_data

-- Foreign Keys: fk_{tabela}_{coluna}__{tabela_ref}
fk_animais_lote_id__lotes
fk_pesagens_animal_id__animais

-- Checks: ck_{tabela}_{regra}
ck_animais_sexo_valido
ck_pesagens_peso_positivo

-- Unique constraints: uq_{tabela}_{coluna(s)}
uq_animais_sisbov
uq_usuarios_keycloak_id
```

### 7.5 Queries — Boas Práticas

```python
# ✅ Uso correto de select com joins explícitos
stmt = (
    select(Animal)
    .options(selectinload(Animal.lote))    # carrega relação sem N+1
    .where(
        and_(
            Animal.tenant_id == tenant_id,
            Animal.ativo == True,
            Animal.categoria == categoria,
        )
    )
    .order_by(Animal.brinco_visual)
    .limit(limit)
    .offset(offset)
)

# ✅ Para grandes volumes — use yield_per para streaming
async for animal in await session.stream_scalars(stmt.yield_per(1000)):
    process(animal)

# ❌ PROIBIDO — lazy loading em contexto async (gera N+1)
animal = await session.get(Animal, id)
print(animal.lote.nome)  # ERRO: lazy load não funciona em async

# ❌ PROIBIDO — queries sem filtro de tenant
stmt = select(Animal)  # falta .where(Animal.tenant_id == tenant_id)
```

---

## 8. Testes & Cobertura Mínima

### 8.1 Cobertura Mínima Obrigatória

| Tipo de Código | Cobertura Mínima | Bloqueio de PR |
|---|---|---|
| Services (lógica de negócio) | **90%** | ✅ Sim |
| Routers (endpoints) | **80%** | ✅ Sim |
| Utils / Helpers | **95%** | ✅ Sim |
| Tasks Celery | **75%** | ✅ Sim |
| Models / Schemas | **70%** | ✅ Sim |
| Migrations | Revisão manual | ❌ Não (CI check) |
| **Total do serviço** | **80%** | ✅ Sim |

### 8.2 Estrutura de Testes Python

```python
# tests/conftest.py — fixtures globais do serviço
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from uuid import uuid4

from ..main import app
from ..database import Base

TEST_TENANT_ID = uuid4()

@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()

@pytest.fixture
async def db_session():
    """Banco em memória para testes — isolado por teste."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        session.info["tenant_id"] = TEST_TENANT_ID
        yield session
    await engine.dispose()

@pytest.fixture
async def client(db_session):
    """HTTP test client com tenant autenticado."""
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_tenant_id] = lambda: TEST_TENANT_ID
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def animal_factory(db_session):
    """Factory para criar animais de teste."""
    async def _create(**kwargs) -> Animal:
        defaults = {
            "brinco_visual": f"BRQ{uuid4().hex[:6].upper()}",
            "raca": "Nelore",
            "sexo": "M",
            "categoria": CategoriaAnimal.NOVILHO,
            "tenant_id": TEST_TENANT_ID,
        }
        animal = Animal(**{**defaults, **kwargs})
        db_session.add(animal)
        await db_session.commit()
        return animal
    return _create
```

```python
# tests/unit/test_animal_service.py — testes unitários

class TestAnimalService:
    """Testa lógica de negócio isolada — sem HTTP."""

    async def test_criar_animal_sucesso(self, db_session):
        svc = AnimalService(db_session, TEST_TENANT_ID)
        dados = AnimalCreate(
            brinco_visual="BRQ001",
            raca="Nelore",
            sexo="M",
            categoria=CategoriaAnimal.NOVILHO,
        )
        animal = await svc.criar(dados)
        assert animal.id is not None
        assert animal.brinco_visual == "BRQ001"
        assert animal.tenant_id == TEST_TENANT_ID

    async def test_calcular_gmd_correto(self, db_session):
        svc = AnimalService(db_session, TEST_TENANT_ID)
        gmd = svc._calcular_gmd(
            ultima=Pesagem(peso_kg=300, data_pesagem=date(2025, 1, 1)),
            nova=PesagemCreate(peso_kg=330, data_pesagem=date(2025, 2, 1)),
        )
        assert gmd == pytest.approx(0.968, rel=1e-3)  # 30kg / 31 dias

    async def test_calcular_gmd_retorna_none_sem_pesagem_anterior(self, db_session):
        svc = AnimalService(db_session, TEST_TENANT_ID)
        gmd = svc._calcular_gmd(ultima=None, nova=PesagemCreate(peso_kg=200, data_pesagem=date.today()))
        assert gmd is None

    async def test_criar_animal_tenant_isolation(self, db_session):
        """Animal criado por tenant A não aparece na listagem do tenant B."""
        svc_a = AnimalService(db_session, TEST_TENANT_ID)
        svc_b = AnimalService(db_session, uuid4())  # tenant diferente
        await svc_a.criar(AnimalCreate(brinco_visual="A001", raca="Nelore", sexo="M", categoria=CategoriaAnimal.NOVILHO))
        animais_b = await svc_b.listar()
        assert len(animais_b) == 0  # tenant B não vê dados do tenant A
```

```python
# tests/integration/test_animais_router.py — testes de integração

class TestAnimaisRouter:
    """Testa os endpoints HTTP — inclui autenticação e feature gates."""

    async def test_listar_animais_retorna_200(self, client, animal_factory):
        await animal_factory(brinco_visual="TST001")
        await animal_factory(brinco_visual="TST002")
        response = await client.get("/animais/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_criar_animal_retorna_201(self, client):
        response = await client.post("/animais/", json={
            "brinco_visual": "NEW001",
            "raca": "Angus",
            "sexo": "F",
            "categoria": "novilha",
        })
        assert response.status_code == 201
        assert response.json()["brinco_visual"] == "NEW001"

    async def test_peso_invalido_retorna_422(self, client, animal_factory):
        animal = await animal_factory()
        response = await client.post(f"/animais/{animal.id}/pesagens", json={
            "peso_kg": -10,  # inválido
            "data_pesagem": "2025-01-01",
            "tipo": "ROTINA",
        })
        assert response.status_code == 422

    async def test_sem_modulo_retorna_403(self, client):
        """Sem módulo PECUARIA_P1 contratado — deve retornar 403."""
        # Override do feature gate para simular módulo não contratado
        app.dependency_overrides[require_module("PECUARIA_P1")] = lambda: (_ for _ in ()).throw(
            HTTPException(403, "MODULE_NOT_CONTRACTED")
        )
        response = await client.get("/animais/")
        assert response.status_code == 403
```

### 8.3 Testes Frontend (Vitest + Playwright)

```typescript
// tests/unit/hooks/use-rebanho.test.ts
import { renderHook, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useRebanho } from "@/hooks/pecuaria/use-rebanho"

describe("useRebanho", () => {
  it("retorna lista de animais", async () => {
    const { result } = renderHook(() => useRebanho(), {
      wrapper: createWrapper(),
    })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.animais).toHaveLength(2)
  })

  it("aplica filtro de categoria", async () => {
    const { result } = renderHook(
      () => useRebanho({ categoria: "novilho" }),
      { wrapper: createWrapper() }
    )
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    result.current.data?.animais.forEach((a) => {
      expect(a.categoria).toBe("novilho")
    })
  })
})
```

```typescript
// tests/e2e/pecuaria/pesagem.spec.ts (Playwright)
import { test, expect } from "@playwright/test"

test.describe("Registro de Pesagem", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/pecuaria/rebanho")
    await loginAsTenant(page, "fazenda-teste")
  })

  test("deve registrar pesagem com sucesso", async ({ page }) => {
    await page.getByTestId("animal-row-BRQ001").click()
    await page.getByRole("button", { name: "Registrar Pesagem" }).click()
    await page.getByLabel("Peso (kg)").fill("350.5")
    await page.getByRole("button", { name: "Salvar" }).click()
    await expect(page.getByText("Pesagem registrada com sucesso")).toBeVisible()
    await expect(page.getByTestId("ultimo-peso")).toContainText("350,5 kg")
  })

  test("deve mostrar erro para peso negativo", async ({ page }) => {
    await page.getByTestId("animal-row-BRQ001").click()
    await page.getByRole("button", { name: "Registrar Pesagem" }).click()
    await page.getByLabel("Peso (kg)").fill("-10")
    await page.getByRole("button", { name: "Salvar" }).click()
    await expect(page.getByText("Peso deve ser maior que zero")).toBeVisible()
  })
})
```

---

## 9. Git, Commits & PR Workflow

### 9.1 Estratégia de Branches

```
main                    — produção, protegida, requer 2 aprovações
  └── develop           — integração, requer 1 aprovação
        ├── feat/       — novas funcionalidades
        ├── fix/        — correção de bugs
        ├── refactor/   — refatoração sem mudança de comportamento
        ├── chore/      — tarefas de manutenção (deps, configs)
        ├── docs/       — apenas documentação
        └── hotfix/     — correção urgente em produção (parte de main)
```

**Regras:**
- `main` aceita merge somente de `develop` ou `hotfix/*`
- `develop` aceita merge de feature, fix, refactor, chore, docs branches
- Nenhum commit direto em `main` ou `develop` — apenas via PR
- Branches de feature devem partir de `develop` e ter vida máxima de 7 dias

### 9.2 Conventional Commits — Obrigatório

```
Formato:
  <tipo>(<escopo>): <descrição imperativa em minúsculas>

  [corpo opcional — contexto do porquê]

  [rodapé opcional — breaking changes, issues]
```

**Tipos válidos:**

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade para o usuário |
| `fix` | Correção de bug |
| `refactor` | Mudança de código sem alterar comportamento |
| `test` | Adição ou correção de testes |
| `docs` | Apenas documentação |
| `chore` | Dependências, configs, CI/CD |
| `perf` | Melhoria de performance |
| `security` | Correção de vulnerabilidade |
| `migration` | Nova migration de banco |

**Exemplos:**

```bash
# ✅ Correto
feat(pecuaria): adiciona cálculo automático de GMD ao registrar pesagem
fix(financeiro): corrige arredondamento em cálculo de impostos NF-e
refactor(core): extrai lógica de tenant para BaseService reutilizável
test(pecuaria): adiciona testes de tenant isolation no AnimalService
migration(pecuaria): adiciona coluna sisbov na tabela animais
security(auth): corrige validação de JWT expirado no middleware
chore(deps): atualiza FastAPI para 0.115.6

# ✅ Com breaking change
feat(api)!: altera formato de retorno de /animais para incluir paginação

BREAKING CHANGE: response agora é { animais: [], total: int, pagina: int }
ao invés de []. Atualizar todos os consumers do endpoint.

# ❌ Errado — proibido
fix stuff
update
WIP
ajustes
corrigindo bug
```

### 9.3 Pull Request — Regras e Template

**Tamanho máximo de PR:**
- ≤ 400 linhas alteradas por PR (exceto migrations e arquivos gerados)
- PRs maiores devem ser quebrados em menores por responsabilidade

**Template obrigatório** (`.gitea/PULL_REQUEST_TEMPLATE.md`):

```markdown
## Descrição
<!-- O que este PR faz? Por que foi necessário? -->

## Tipo de Mudança
- [ ] feat — nova funcionalidade
- [ ] fix — correção de bug
- [ ] refactor — sem mudança de comportamento
- [ ] migration — mudança de schema
- [ ] security — correção de segurança

## Como Testar
<!-- Passos para revisar e testar manualmente -->
1. 
2. 

## Checklist
- [ ] Testes escritos e passando (cobertura mínima mantida)
- [ ] Sem `console.log` / `print()` de debug no código
- [ ] Sem secrets ou dados sensíveis commitados
- [ ] Migration tem `downgrade()` implementado
- [ ] `ruff`, `mypy` (Python) ou `eslint`, `tsc` (TS) sem erros
- [ ] Documentação atualizada se necessário

## Breaking Changes
- [ ] Não há breaking changes
- [ ] Há breaking changes — descreva abaixo:

## Issues Relacionadas
Closes #
```

### 9.4 Regras de Code Review

**Para o Author (quem abre o PR):**
- PR deve ter descrição clara — revisor não precisa adivinhar o contexto
- Resolva `TODO`, `FIXME` e `HACK` antes de abrir o PR (ou crie issue separada)
- Responda comentários em até 24h durante dias úteis
- Não force-push após aprovação

**Para o Reviewer (quem revisa):**
- Aprove somente se entendeu o que o código faz e por quê
- Use prefixos em comentários para clareza:
  - `nit:` — sugestão menor, não bloqueia merge
  - `blocking:` — deve ser resolvido antes do merge
  - `question:` — pergunta, não necessariamente um problema
  - `suggestion:` — alternativa, deixa ao critério do author
- Revise em até 24h após solicitação (dias úteis)
- Foque em lógica, segurança e arquitetura — não em estilo (o linter resolve)

**Aprovações necessárias:**

| Branch destino | Aprovações mínimas | Quem pode aprovar |
|---|---|---|
| `develop` | 1 | Qualquer dev sênior |
| `main` | 2 | Tech Lead obrigatório + 1 sênior |
| `hotfix → main` | 1 | Tech Lead |

---

## 10. Checklist de Code Review

Use este checklist ao revisar qualquer PR no AgroSaaS.

### Arquitetura
- [ ] A mudança respeita a separação de responsabilidades (SRP)?
- [ ] Lógica de negócio está no `Service`, não no `Router` ou `Component`?
- [ ] Não há dependências circulares entre módulos?
- [ ] Novos abstrações são realmente necessárias (YAGNI)?

### Segurança & Multitenancy
- [ ] Toda query de banco filtra por `tenant_id`?
- [ ] Nenhum dado de outro tenant pode vazar por este código?
- [ ] Inputs são validados por Pydantic/Zod antes de processar?
- [ ] Nenhum secret está hardcoded ou em log?
- [ ] `require_module()` e `require_role()` aplicados nos endpoints novos?

### Banco de Dados
- [ ] Migration incluída para qualquer mudança de schema?
- [ ] `downgrade()` implementado e testado na migration?
- [ ] Índices criados com `CONCURRENTLY` onde necessário?
- [ ] Sem risco de N+1 queries (use `selectinload` ou `joinedload`)?
- [ ] Colunas `NOT NULL` novas têm `DEFAULT` ou migration em 2 passos?

### Testes
- [ ] Cobertura mínima mantida (80% total, 90% services)?
- [ ] Testes de tenant isolation presentes para novos services?
- [ ] Casos de erro testados (400, 403, 404, 422)?
- [ ] Nenhum teste que depende de ordem de execução ou estado externo?

### Código
- [ ] Sem código morto ou comentado?
- [ ] Sem `print()`, `console.log()` ou logs de debug?
- [ ] Funções têm type hints completos (Python) ou tipos TS explícitos?
- [ ] Erros lançados são do tipo correto (`EntityNotFoundError`, etc.)?
- [ ] Nenhuma string mágica — usar Enum ou constante nomeada?

### Git
- [ ] Commits seguem Conventional Commits?
- [ ] Branch parte de `develop` (não de `main`)?
- [ ] PR tem descrição clara e checklist preenchido?
- [ ] Sem arquivos desnecessários (`.DS_Store`, `__pycache__`, `.env`)?

---

## 11. Arquitetura de Módulos de Negócio

Esta seção conecta as regras técnicas deste manual com a estratégia de módulos e funcionalidades do AgroSaaS.

### 11.1 Visão Geral da Arquitetura Modular

O AgroSaaS é organizado em **módulos de negócio** que mapeiam para **microsserviços técnicos**:

| Módulo de Negócio | Microsserviço(s) | Níveis de Maturidade |
|------------------|------------------|---------------------|
| **Core** | `api-core` | Core (obrigatório) |
| **Agrícola** | `api-agricola` | Essencial, Profissional, Enterprise |
| **Pecuária** | `api-pecuaria` | Essencial, Profissional, Enterprise |
| **Financeiro** | `api-financeiro` | Essencial, Profissional, Enterprise |
| **Operacional** | `api-operacional` | Essencial, Profissional, Enterprise |
| **IA & Diagnóstico** | `api-ia` | Add-on Enterprise |

### 11.2 Níveis de Maturidade por Módulo

Cada módulo é implantado progressivamente em 3 níveis:

| Nível | Nome | Feature Flag | Quando Implantar |
|-------|------|--------------|------------------|
| 1 | **Essencial** | `{MODULO}_E` | MVP do módulo — funcionalidades básicas |
| 2 | **Profissional** | `{MODULO}_P1`, `{MODULO}_P2` | Automações, relatórios, integrações |
| 3 | **Enterprise** | `{MODULO}_E1`, `{MODULO}_E2` | BI, multi-empresa, integrações fiscais |

**Exemplo de uso no código:**

```python
# routers/animais.py
@router.post("/animais/")
async def criar_animal(
    dados: AnimalCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("PECUARIA_E")),  # Essencial
):
    ...

@router.post("/animais/{id}/pesagens/gmd-avancado")
async def calcular_gmd_avancado(
    animal_id: UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("PECUARIA_P1")),  # Profissional
):
    ...

@router.get("/relatorios/dre-lote")
async def dre_lote(
    fazenda_id: UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("FINANCEIRO_E1")),  # Enterprise
):
    ...
```

### 11.3 Pacotes de Assinatura

Os níveis de maturidade são combinados em **pacotes de assinatura**:

| Pacote | Módulos Incluídos | Nível Máximo | Público-Alvo |
|--------|------------------|--------------|--------------|
| **Produtor** | Core + 1 módulo | Essencial | Pequeno produtor |
| **Gestão** | Core + 3 módulos | Profissional | Fazenda média |
| **Pecuária** | Core + Pecuária + Operacional | Profissional | Pecuária especializada |
| **Lavoura** | Core + Agrícola + Financeiro | Profissional | Agricultura de grãos |
| **Rastreabilidade** | Core + Rastreabilidade + Compliance | Enterprise | Exportadores |
| **Enterprise** | Todos os módulos | Enterprise | Grandes grupos, cooperativas |

**Controle via banco de dados:**

```sql
-- Tabela: assinaturas
CREATE TABLE assinaturas (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    pacote VARCHAR(50) NOT NULL, -- 'produtor', 'gestao', 'pecuaria', etc.
    status VARCHAR(20) NOT NULL, -- 'ativa', 'cancelada', 'trial'
    data_inicio DATE NOT NULL,
    data_vencimento DATE,
    limites JSONB NOT NULL, -- {'max_propriedades': 5, 'max_usuarios': 10}
    modulos_contratados TEXT[] NOT NULL, -- ['PECUARIA_E', 'PECUARIA_P1', ...]
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para consulta rápida de feature flags
CREATE INDEX ix_assinaturas_tenant_modulos ON assinaturas USING GIN (modulos_contratados);
```

### 11.4 Documentação de Contexto por Módulo

Cada módulo possui documentação detalhada em `docs/contexts/`:

```
docs/contexts/
├── _index.md                        ← Índice mestre
├── _competitive-analysis.md         ← Análise de concorrentes
├── _bundle-packages.md              ← Pacotes de assinatura
├── _module-dependency-graph.md      ← Dependências entre módulos
├── _parallel-agent-workflow.md      ← Workflow de desenvolvimento
│
├── core/                            ← Módulo Core (fundação)
│   ├── _overview.md
│   ├── _implantation-workflow.md
│   ├── identidade-acesso.md
│   ├── cadastro-propriedade.md
│   └── ... (7 submódulos)
│
├── agricola/                        ← Módulo Agrícola
│   ├── _overview.md
│   ├── _implantation-workflow.md
│   ├── essencial/
│   │   ├── safras.md
│   │   ├── operacoes-campo.md
│   │   └── caderno-campo.md
│   ├── profissional/
│   │   ├── planejamento-safra.md
│   │   ├── monitoramento-ndvi.md
│   │   └── custos-producao.md
│   └── enterprise/
│       ├── rastreabilidade-campo.md
│       ├── prescricoes-vrt.md
│       └── beneficiamento.md
│
└── ... (demais módulos: pecuaria, financeiro, operacional, etc.)
```

**Template de documento de submódulo:**

```markdown
---
modulo: [nome do módulo]
submodulo: [nome do submódulo]
nivel: essencial | profissional | enterprise | core
core: true | false
dependencias_core: [submódulos do core necessários]
dependencias_modulos: [outros submódulos dependentes]
standalone: true | false
complexidade: XS | S | M | L | XL
assinante_alvo: [pequeno produtor | fazenda média | grande operação]
---

## Descrição Funcional
## Personas
## Dores que resolve
## Regras de Negócio
## Entidades de Dados Principais
## Integrações Necessárias
## Fluxo de Uso Principal
## Casos Extremos e Exceções
## Critérios de Aceite (DoD)
## Sugestões de Melhoria Futura
```

### 11.5 Ordem de Implantação

**Regra obrigatória:** módulos são implantados **sempre na ordem ascendente de maturidade**:

```
Fase 1: Core (obrigatório para todos os pacotes)
  └── Identidade e Acesso
  └── Cadastro de Propriedade
  └── Multipropriedade
  └── Configurações Globais
  └── Notificações
  └── Integrações Essenciais
  └── Planos e Assinatura

Fase 2: Módulos Essenciais (paralelo)
  ├── Agrícola Essencial
  ├── Pecuária Essencial
  ├── Financeiro Essencial
  └── Operacional Essencial

Fase 3: Módulos Profissionais (paralelo)
  ├── Agrícola Profissional
  ├── Pecuária Profissional
  ├── Financeiro Profissional
  └── Operacional Profissional

Fase 4: Módulos Enterprise (paralelo)
  ├── Agrícola Enterprise
  ├── Pecuária Enterprise
  ├── Financeiro Enterprise
  ├── Operacional Enterprise
  ├── Rastreabilidade Enterprise
  ├── Compliance Enterprise
  └── Comercialização Enterprise
```

**Nunca** implante Profissional antes do Essencial, ou Enterprise antes do Profissional.

### 11.6 Feature Flags na Prática

**Backend (Python/FastAPI):**

```python
# dependencies.py
from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def require_module(module_flag: str):
    """
    Dependency que verifica se o tenant contratou o módulo.
    Uso: _: None = Depends(require_module("PECUARIA_P1"))
    """
    async def _check_module(
        tenant_id: UUID = Depends(get_tenant_id),
        session: AsyncSession = Depends(get_session),
    ):
        result = await session.execute(
            select(Assinatura.modulos_contratados)
            .where(Assinatura.tenant_id == tenant_id)
            .where(Assinatura.status == "ativa")
        )
        assinatura = result.scalar_one_or_none()
        
        if not assinatura:
            raise HTTPException(status_code=402, detail="Assinatura não encontrada")
        
        if module_flag not in assinatura.modulos_contratados:
            raise HTTPException(
                status_code=403,
                detail=f"Módulo {module_flag} não contratado",
            )
    
    return _check_module
```

**Frontend (TypeScript/React):**

```typescript
// lib/modules.ts
export type ModuleId =
  | 'CORE'
  | 'AGRICOLA_E'
  | 'AGRICOLA_P1'
  | 'AGRICOLA_E1'
  | 'PECUARIA_E'
  | 'PECUARIA_P1'
  | 'PECUARIA_E1'
  | 'FINANCEIRO_E'
  | 'FINANCEIRO_P1'
  | 'FINANCEIRO_E1'
  | 'OPERACIONAL_E'
  | 'OPERACIONAL_P1'
  | 'OPERACIONAL_E1'

export function useModule(moduleId: ModuleId): boolean {
  const { modules } = useAppStore()
  return modules.includes(moduleId)
}

// components/shared/module-gate.tsx
export function ModuleGate({
  moduleId,
  children,
  fallback = null,
}: {
  moduleId: ModuleId
  children: React.ReactNode
  fallback?: React.ReactNode
}) {
  const hasModule = useModule(moduleId)
  
  if (!hasModule) {
    return <>{fallback}</>
  }
  
  return <>{children}</>
}

// Uso em páginas
<ModuleGate
  moduleId="PECUARIA_P1"
  fallback={<UpgradePrompt module="Pecuária Profissional" />}
>
  <GmdAvancadoChart />
</ModuleGate>
```

### 11.7 Links para Documentação Estratégica

| Documento | Localização | Propósito |
|-----------|-------------|-----------|
| **Arquitetura Modular** | [`../strategy/module-architecture.md`](../strategy/module-architecture.md) | Missão, tarefas, estrutura de documentação |
| **Análise Competitiva** | [`../contexts/_competitive-analysis.md`](../contexts/_competitive-analysis.md) | Comparativo com concorrentes |
| **Pacotes de Assinatura** | [`../contexts/_bundle-packages.md`](../contexts/_bundle-packages.md) | Detalhe de pacotes, preços, limites |
| **Dependências** | [`../contexts/_module-dependency-graph.md`](../contexts/_module-dependency-graph.md) | Grafo de dependências entre módulos |
| **Workflow de Agentes** | [`../contexts/_parallel-agent-workflow.md`](../contexts/_parallel-agent-workflow.md) | Como múltiplos agentes trabalham em paralelo |
| **Índice de Contextos** | [`../contexts/_index.md`](../contexts/_index.md) | Navegação completa da documentação |

---

*Documento mantido pelo time de arquitetura. Sugestões de melhoria via PR com discussão prévia em `#tech-guidelines`.*

*Versão: 1.0.0 · Revisão: trimestral*
