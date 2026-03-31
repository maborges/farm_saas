# AgroSaaS - Frontend (Next.js)

**Versão:** 1.0.0  
**Última Atualização:** 2026-03-31  
**Status:** Ativo  

---

## 📋 Índice

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura Next.js 16](#2-arquitetura-nextjs-16)
3. [Estrutura de Pastas](#3-estrutura-de-pastas)
4. [Componentes](#4-componentes)
5. [Gerenciamento de Estado](#5-gerenciamento-de-estado)
6. [Hooks Personalizados](#6-hooks-personalizados)
7. [Integração com API](#7-integração-com-api)
8. [Feature Flags e Módulos](#8-feature-flags-e-módulos)
9. [UI/UX e Componentes](#9-uiux-e-componentes)
10. [Boas Práticas](#10-boas-práticas)

---

## 1. Visão Geral

### Stack Tecnológico

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **Next.js** | 16 | Framework React com App Router |
| **React** | 19 | UI library |
| **TypeScript** | 5 | Type safety |
| **TanStack Query** | 5 | Server state management |
| **Zustand** | 5 | Client state management |
| **shadcn/ui** | 4 | Component library |
| **Tailwind CSS** | 4 | Styling |
| **Zod** | 4 | Validação de schemas |
| **React Hook Form** | 7 | Formulários |
| **MapLibre GL** | 5 | Mapas e GIS |

### Princípios Fundamentais

1. **Server Components First**: Tudo é Server Component por padrão
2. **Client Components quando necessário**: Apenas para interatividade
3. **Type Safety**: TypeScript estrito em todo código
4. **Shared Schemas**: Zod schemas compartilhados com backend
5. **Feature Gates**: Módulos renderizados baseado na assinatura

---

## 2. Arquitetura Next.js 16

### App Router

```
apps/web/src/app/
├── (auth)/                    # Route group - sem layout de dashboard
│   ├── login/
│   ├── register/
│   └── convite/
│
├── (dashboard)/               # Route group - com layout autenticado
│   ├── layout.tsx             # Layout com sidebar e navbar
│   ├── dashboard/             # Dashboards por módulo
│   ├── agricola/              # Módulo agrícola
│   ├── pecuaria/              # Módulo pecuária
│   ├── financeiro/            # Módulo financeiro
│   ├── operacional/           # Módulo operacional
│   ├── rh/                    # Módulo RH
│   └── backoffice/            # Admin SaaS
│
├── onboarding/                # Fluxo de onboarding
├── track/                     # Tracking page
├── actions/                   # Server actions
├── layout.tsx                 # Root layout
└── page.tsx                   # Home page
```

### Route Groups

**Route Groups** permitem organizar rotas sem afetar a URL:

```
(app)/
├── (auth)/login      → /login
├── (auth)/register   → /register
├── (dashboard)/agricola  → /agricola
└── (dashboard)/pecuaria  → /pecuaria
```

### Layouts Aninhados

```typescript
// app/(dashboard)/layout.tsx
export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Server Component - busca dados no servidor
  const tenant = await fetchTenant()
  const modules = await fetchModules()
  
  return (
    <div className="flex h-screen">
      <AppSidebar tenant={tenant} modules={modules} />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
```

---

## 3. Estrutura de Pastas

```
apps/web/
├── src/
│   ├── app/                        # Next.js App Router
│   │   ├── (auth)/                 # Auth routes
│   │   ├── (dashboard)/            # Dashboard routes
│   │   ├── onboarding/             # Onboarding flow
│   │   ├── actions/                # Server actions
│   │   ├── layout.tsx              # Root layout
│   │   └── page.tsx                # Home page
│   │
│   ├── components/
│   │   ├── ui/                     # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── form.tsx
│   │   │   ├── input.tsx
│   │   │   ├── table.tsx
│   │   │   ├── data-table.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/                 # Layout components
│   │   │   ├── sidebar.tsx
│   │   │   ├── app-sidebar.tsx
│   │   │   ├── navbar.tsx
│   │   │   ├── context-selector.tsx
│   │   │   └── notification-bell.tsx
│   │   │
│   │   ├── auth/                   # Auth components
│   │   ├── shared/                 # Shared components
│   │   ├── agricola/               # Agricultural components
│   │   ├── pecuaria/               # Livestock components
│   │   ├── financeiro/             # Financial components
│   │   └── operacional/            # Operational components
│   │
│   ├── hooks/                      # Custom hooks
│   │   ├── index.ts                # Barrel export
│   │   ├── use-permission.ts
│   │   ├── use-has-module.ts
│   │   ├── use-has-tier.ts
│   │   ├── use-team.ts
│   │   ├── use-estoque.ts
│   │   └── ...
│   │
│   ├── lib/                        # Utilities
│   │   ├── api.ts                  # Client API fetcher
│   │   ├── api-server.ts           # Server API fetcher (RSC)
│   │   ├── utils.ts                # cn(), formatters
│   │   ├── permissions.ts          # Permission utilities
│   │   ├── sidebar-config.ts       # Sidebar configuration
│   │   ├── stores/                 # Zustand stores
│   │   │   └── app-store.ts
│   │   └── constants/
│   │       ├── modulos.ts          # Module definitions
│   │       └── planos.ts           # Plan definitions
│   │
│   ├── store/                      # Legacy stores
│   │   └── use-auth-store.ts
│   │
│   └── types/                      # TypeScript types
│       └── global.d.ts
│
├── public/                         # Static assets
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
└── components.json
```

---

## 4. Componentes

### Server Components (Padrão)

```typescript
// app/(dashboard)/agricola/safras/page.tsx
// Server Component por padrão (sem "use client")

export default async function SafrasPage({
  searchParams,
}: {
  searchParams: { cultura?: string; status?: string }
}) {
  // Busca dados no servidor
  const safras = await fetchSafras(searchParams)
  
  return (
    <div>
      <SafrasHeader />
      <SafrasGrid safras={safras} />
    </div>
  )
}
```

### Client Components (Quando necessário)

```typescript
// components/agricola/safras-grid.tsx
"use client"

import { useState } from "react"
import { useSafras } from "@/hooks/use-safras"

export function SafrasGrid() {
  const [filtro, setFiltro] = useState("")
  const { data, isLoading } = useSafras()
  
  if (isLoading) return <Skeleton />
  
  return (
    <div>
      <input 
        value={filtro} 
        onChange={(e) => setFiltro(e.target.value)}
      />
      {/* Render data */}
    </div>
  )
}
```

### Regras para Client Components

Use `"use client"` APENAS quando precisar de:
- ✅ `useState`, `useReducer`
- ✅ Event handlers (`onClick`, `onChange`)
- ✅ Browser APIs (`window`, `localStorage`)
- ✅ Hooks de terceiros (TanStack Query, Zustand)
- ✅ Context API

**NUNCA** use em:
- ❌ `page.tsx` (sempre Server Component)
- ❌ Components que só renderizam dados
- ❌ Components sem interatividade

---

## 5. Gerenciamento de Estado

### Zustand - Estado Global

```typescript
// lib/stores/app-store.ts
import { create } from "zustand"
import { persist } from "zustand/middleware"
import { immer } from "zustand/middleware/immer"

interface AppState {
  // Estado
  tenant: Tenant | null
  user: User | null
  modules: string[]
  activeFazendaId: string | null
  
  // Actions
  setTenant: (tenant: Tenant) => void
  setModules: (modules: string[]) => void
  hasModule: (moduleId: string) => boolean
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
      partialize: (s) => ({ activeFazendaId: s.activeFazendaId }),
    }
  )
)
```

### Uso do Zustand

```typescript
// Em qualquer component
import { useAppStore } from "@/lib/stores/app-store"

function MeuComponente() {
  const { tenant, modules, hasModule } = useAppStore()
  
  if (!hasModule("A1_PLANEJAMENTO")) {
    return <ModuleGate module="A1_PLANEJAMENTO" />
  }
  
  return <div>{tenant?.nome}</div>
}
```

---

## 6. Hooks Personalizados

### TanStack Query - Server State

```typescript
// hooks/agricola/use-safras.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAppStore } from "@/lib/stores/app-store"

// Query keys tipadas
export const safrasKeys = {
  all: ["safras"] as const,
  list: (tenantId: string, filters: SafrasFilters) =>
    [...safrasKeys.all, "list", tenantId, filters] as const,
  detail: (id: string) =>
    [...safrasKeys.all, "detail", id] as const,
}

// Hook de listagem
export function useSafras(filters: SafrasFilters = {}) {
  const { tenant } = useAppStore()
  
  return useQuery({
    queryKey: safrasKeys.list(tenant!.id, filters),
    queryFn: () => api.agricola.listarSafras(tenant!.id, filters),
    staleTime: 5 * 60 * 1000, // 5 minutos
    placeholderData: (prev) => prev,
    enabled: !!tenant,
  })
}

// Hook de mutation
export function useCriarSafra() {
  const qc = useQueryClient()
  const { tenant } = useAppStore()
  
  return useMutation({
    mutationFn: (data: SafraCreate) =>
      api.agricola.criarSafra(tenant!.id, data),
    
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: safrasKeys.all })
    },
  })
}
```

### Hooks de Permissão

```typescript
// hooks/use-permission.ts
import { useAppStore } from "@/lib/stores/app-store"
import { TenantPermissions } from "@/lib/permissions"

export function usePermission(permission: string) {
  const { user, customPermissions } = useAppStore()
  
  if (!user) return false
  
  return TenantPermissions.hasPermission(
    user.role,
    permission,
    customPermissions
  )
}

// hooks/use-has-module.ts
export function useHasModule(moduleId: string) {
  const { modules } = useAppStore()
  return modules.includes(moduleId)
}

// hooks/use-has-tier.ts
import { PlanTier } from "@farm/zod-schemas"

export function useHasTier(requiredTier: PlanTier) {
  const { tenant } = useAppStore()
  
  if (!tenant) return false
  
  const tenantTier = tenant.plano.tier as PlanTier
  return tierLevel(tenantTier) >= tierLevel(requiredTier)
}
```

---

## 7. Integração com API

### Client API Fetcher

```typescript
// lib/api.ts
import { toast } from "sonner"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL

type RequestMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE"

async function request<T>(
  url: string,
  method: RequestMethod = "GET",
  data?: any
): Promise<T> {
  const options: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  }
  
  if (data) {
    options.body = JSON.stringify(data)
  }
  
  const response = await fetch(`${BASE_URL}${url}`, options)
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || "Erro na requisição")
  }
  
  return response.json()
}

export const api = {
  auth: {
    login: (email: string, senha: string) =>
      request("/auth/login", "POST", { email, senha }),
    register: (data: any) => request("/auth/register", "POST", data),
    logout: () => request("/auth/logout", "POST"),
  },
  
  agricola: {
    listarSafras: (tenantId: string, filters: any) =>
      request(`/agricola/planejamento/safras?${new URLSearchParams(filters)}`),
    criarSafra: (tenantId: string, data: any) =>
      request("/agricola/planejamento/safras", "POST", data),
    // ...
  },
  
  // ... outros módulos
}
```

### Server API Fetcher (RSC)

```typescript
// lib/api-server.ts
import { cookies } from "next/headers"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL

export async function fetchServer<T>(url: string): Promise<T> {
  const cookieStore = await cookies()
  const token = cookieStore.get("auth_token")?.value
  
  const response = await fetch(`${BASE_URL}${url}`, {
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    cache: "no-store",
  })
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  return response.json()
}

// Uso em Server Component
export default async function SafrasPage() {
  const safras = await fetchServer("/agricola/planejamento/safras")
  return <SafrasGrid safras={safras} />
}
```

---

## 8. Feature Flags e Módulos

### Module Gate Component

```typescript
// components/shared/module-gate.tsx
"use client"

import { useHasModule } from "@/hooks/use-has-module"
import { ModuloMetadata } from "@/lib/constants/modulos"

interface ModuleGateProps {
  module: string
  children: React.ReactNode
  fallback?: React.ReactNode
}

export function ModuleGate({ module, children, fallback }: ModuleGateProps) {
  const hasModule = useHasModule(module)
  
  if (!hasModule) {
    if (fallback) return fallback
    
    const info = ModuloMetadata[module]
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <h3 className="text-lg font-semibold">Módulo não contratado</h3>
          <p className="text-muted-foreground">
            {info?.nome} - {info?.descricao}
          </p>
          <Button className="mt-4">
            Contratar módulo
          </Button>
        </div>
      </div>
    )
  }
  
  return children
}
```

### Uso de Feature Gates

```typescript
// app/(dashboard)/agricola/page.tsx
import { ModuleGate } from "@/components/shared/module-gate"
import { Modulos } from "@/lib/constants/modulos"

export default function AgricolaDashboard() {
  return (
    <div>
      <ModuleGate module={Modulos.AGRICOLA_PLANEJAMENTO}>
        <PlanejamentoDashboard />
      </ModuleGate>
      
      <ModuleGate module={Modulos.AGRICOLA_CAMPO}>
        <CampoDashboard />
      </ModuleGate>
    </div>
  )
}
```

### Sidebar Dinâmica por Módulo

```typescript
// lib/sidebar-config.ts
export const MODULOS_OPERACIONAIS: SidebarModuleGroup[] = [
  {
    key: "A1",
    label: "Agricultura",
    moduleId: "A1",
    sections: [
      {
        key: "A1-planejamento",
        label: "Planejamento",
        items: [
          { href: "/agricola/safras", label: "Safras" },
          { href: "/agricola/talhoes", label: "Talhões" },
        ],
      },
      // ...
    ],
  },
  // ...
]

// components/layout/app-sidebar.tsx
export function AppSidebar() {
  const { modules } = useAppStore()
  
  return (
    <Sidebar>
      <SidebarContent>
        {MODULOS_OPERACIONAIS.map((modulo) => (
          <ModuleSection
            key={modulo.key}
            modulo={modulo}
            isVisible={modules.includes(modulo.moduleId)}
          />
        ))}
      </SidebarContent>
    </Sidebar>
  )
}
```

---

## 9. UI/UX e Componentes

### shadcn/ui Components

Componentes principais utilizados:

| Componente | Uso |
|------------|-----|
| `button` | Botões (variants: default, secondary, outline, ghost, destructive) |
| `card` | Cards de conteúdo |
| `dialog` | Modais |
| `form` | Formulários com React Hook Form |
| `input` | Campos de texto |
| `select` | Dropdowns |
| `table` | Tabelas |
| `data-table` | Tabelas com sorting, filtering, pagination |
| `badge` | Etiquetas de status |
| `avatar` | Avatares de usuário |
| `dropdown-menu` | Menus contextuais |
| `tooltip` | Tooltips informativos |
| `sonner` | Toast notifications |
| `sidebar` | Sidebar navigation |

### DataTable Component

```typescript
// components/ui/data-table.tsx
"use client"

import {
  ColumnDef,
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
} from "@tanstack/react-table"

interface DataTableProps<T> {
  columns: ColumnDef<T>[]
  data: T[]
  searchKey?: string
}

export function DataTable<T>({ columns, data, searchKey }: DataTableProps<T>) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [filtering, setFiltering] = useState("")
  
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    state: { sorting, globalFilter: filtering },
    onSortingChange: setSorting,
    onGlobalFilterChange: setFiltering,
  })
  
  return (
    <div>
      {searchKey && (
        <Input
          placeholder="Buscar..."
          value={filtering}
          onChange={(e) => setFiltering(e.target.value)}
        />
      )}
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((group) => (
            <TableRow key={group.id}>
              {group.headers.map((header) => (
                <TableHead key={header.id}>
                  {header.isPlaceholder
                    ? null
                    : flexRender(header.column.columnDef.header, header.getContext())}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows.map((row) => (
            <TableRow key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <TableCell key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <Pagination table={table} />
    </div>
  )
}
```

---

## 10. Boas Práticas

### 10.1 Server vs Client Components

```typescript
// ✅ CORRETO: Server Component busca dados
// app/(dashboard)/agricola/safras/page.tsx
export default async function SafrasPage() {
  const safras = await fetchSafras()
  return <SafrasClient data={safras} />
}

// ✅ CORRETO: Client Component para interatividade
// components/agricola/safras-client.tsx
"use client"

export function SafrasClient({ data }: { data: any }) {
  const [filtro, setFiltro] = useState("")
  return (
    <div>
      <Input value={filtro} onChange={...} />
      <SafrasGrid data={data} filtro={filtro} />
    </div>
  )
}

// ❌ ERRADO: "use client" em page.tsx
"use client"  // NUNCA em arquivos de rota
export default function Page() { ... }
```

### 10.2 Loading States

```typescript
// app/(dashboard)/agricola/safras/loading.tsx
import { Skeleton } from "@/components/ui/skeleton"

export default function SafrasLoading() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-64 w-full" />
    </div>
  )
}

// Next.js automaticamente usa este loading.tsx
// enquanto o page.tsx carrega
```

### 10.3 Error Handling

```typescript
// app/(dashboard)/agricola/safras/error.tsx
"use client"

import { useEffect } from "react"
import { Button } from "@/components/ui/button"

export default function SafrasError({
  error,
  reset,
}: {
  error: Error
  reset: () => void
}) {
  useEffect(() => {
    console.error("Erro ao carregar safras:", error)
  }, [error])
  
  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <h3 className="text-lg font-semibold">Erro ao carregar</h3>
        <p className="text-muted-foreground">{error.message}</p>
        <Button onClick={reset} className="mt-4">
          Tentar novamente
        </Button>
      </div>
    </div>
  )
}
```

### 10.4 Type Safety

```typescript
// ✅ CORRETO: Tipos explícitos
interface SafraProps {
  safra: Safra
  onSelect: (id: string) => void
}

function SafraCard({ safra, onSelect }: SafraProps) {
  return <div>{safra.nome}</div>
}

// ❌ ERRADO: any implícito
function SafraCard({ safra, onSelect }: any) {
  return <div>{safra.nome}</div>
}
```

### 10.5 Performance

```typescript
// ✅ Use Suspense para carregamento progressivo
import { Suspense } from "react"

export default function Dashboard() {
  return (
    <Suspense fallback={<Skeleton />}>
      <DashboardContent />
    </Suspense>
  )
}

// ✅ Use React.memo para componentes pesados
export const SafrasGrid = memo(function SafrasGrid({ data }) {
  return <div>{/* render */}</div>
})

// ✅ Use useCallback para funções passadas como props
const handleSelect = useCallback((id: string) => {
  // ...
}, [])
```

---

## Referências Cruzadas

| Documento | Descrição |
|-----------|-----------|
| `docs/qwen/01-arquitetura.md` | Arquitetura geral |
| `docs/qwen/07-ui-ux.md` | Guidelines de UI/UX |
| `docs/qwen/02-modulos.md` | Módulos do sistema |

---

## Changelog

| Data | Versão | Descrição |
|------|--------|-----------|
| 2026-03-31 | 1.0.0 | Documentação inicial completa |
