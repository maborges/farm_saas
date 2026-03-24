import { useState, Suspense, lazy } from "react";

// ═══════════════════════════════════════════════════════
//  CAMADA 1 — CLIENT LAYER
// ═══════════════════════════════════════════════════════
const deps = {
  core: [
    { name: "next", version: "16.0.0", role: "Framework principal", why: "App Router, RSC, Server Actions, Turbopack" },
    { name: "react", version: "19.0.0", role: "UI Runtime", why: "Server Components nativos, novo compilador React", peer: ["react-dom@19.0.0"] },
    { name: "typescript", version: "5.7.x", role: "Type Safety", why: "Tipos estritos em toda a base — erros em compilação", peer: ["@types/node", "@types/react@19"] },
  ],
  ui: [
    { name: "tailwindcss", version: "4.0.x", role: "Utility CSS", why: "CSS vars nativas, container queries, sem purge config" },
    { name: "@radix-ui/react-*", version: "2.x", role: "Primitivos acessíveis", why: "Sem estilos, WAI-ARIA completo, headless" },
    { name: "shadcn/ui", version: "2.x (CLI)", why: "Componentes copiados para o repo — sem vendor lock-in", role: "Design System base" },
    { name: "lucide-react", version: "0.468.x", role: "Ícones", why: "Tree-shakeable, 1500+ ícones consistentes" },
  ],
  state: [
    { name: "@tanstack/react-query", version: "5.62.x", role: "Server State", why: "Cache, revalidação, optimistic updates, prefetch SSR" },
    { name: "zustand", version: "5.0.x", role: "Client State", why: "Minimal boilerplate, middleware persist/immer" },
    { name: "react-hook-form", version: "7.54.x", role: "Formulários", why: "Zero re-renders, integração nativa com Zod" },
    { name: "zod", version: "3.24.x", role: "Validação / Schema", why: "Schema compartilhado front + back (monorepo)" },
  ],
  data: [
    { name: "ag-grid-react", version: "33.x", role: "Data Grids", why: "100k+ linhas, virtualização — rebanho, financeiro" },
    { name: "recharts", version: "2.15.x", role: "Gráficos operacionais", why: "Composable, SVG, responsive" },
    { name: "@nivo/core", version: "0.88.x", role: "Gráficos avançados", why: "Heatmaps de talhão, treemaps de custo" },
    { name: "maplibre-gl", version: "4.x", role: "Mapas (OSS)", why: "Fork OSS do Mapbox GL, sem API key" },
  ],
  mobile: [
    { name: "expo", version: "52.x", role: "React Native framework", why: "OTA updates, EAS build, compartilha lógica com web" },
    { name: "@nozbe/watermelondb", version: "0.27.x", role: "Offline-first DB", why: "SQLite local, sync incremental" },
    { name: "expo-camera", version: "16.x", role: "Câmera", why: "Foto de pragas + QR Code de animais" },
    { name: "expo-location", version: "18.x", role: "GPS", why: "Georeferenciamento de ocorrências e talhões" },
  ],
};

const clientCode = {
  middleware: `// middleware.ts — Edge Runtime (sem cold start)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { jwtVerify } from 'jose'

const PUBLIC_KEY = new TextEncoder().encode(process.env.KEYCLOAK_PUBLIC_KEY)

export async function middleware(request: NextRequest) {
  const hostname = request.headers.get('host') ?? ''
  
  // Extrai tenant: fazendaabc.agrosass.local → fazendaabc
  const tenant = hostname.split('.')[0]
  if (!tenant || tenant === 'www') {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  const token = request.cookies.get('access_token')?.value
  if (!token) return NextResponse.redirect(\`/login?tenant=\${tenant}\`)

  try {
    const { payload } = await jwtVerify(token, PUBLIC_KEY)
    const response = NextResponse.next()
    // Injeta context para Server Components
    response.headers.set('x-tenant-id', tenant)
    response.headers.set('x-user-roles', JSON.stringify(payload.roles))
    response.headers.set('x-modules', JSON.stringify(payload.modules ?? []))
    return response
  } catch {
    return NextResponse.redirect(\`/login?tenant=\${tenant}&reason=expired\`)
  }
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)']
}`,
  rsc: `// app/(dashboard)/pecuaria/rebanho/page.tsx
// ✅ Server Component — zero JS no cliente para esta lógica
import { headers } from 'next/headers'
import { RebanhoGrid } from '@/components/pecuaria/rebanho-grid'
import { fetchRebanho } from '@/lib/api/pecuaria'
import { checkModule } from '@/lib/modules'

export default async function RebanhoPage({ searchParams }) {
  const hdrs = await headers()
  const tenantId = hdrs.get('x-tenant-id')!
  const modules = JSON.parse(hdrs.get('x-modules') ?? '[]')

  // Feature gate server-side
  if (!checkModule(modules, 'PECUARIA_P1')) {
    return <ModuleNotContracted module="Gestão de Rebanho" />
  }

  // Busca direto no servidor — sem roundtrip API
  const { animais, total } = await fetchRebanho({
    tenantId,
    pagina: Number(searchParams.pagina ?? 1),
    categoria: searchParams.categoria,
  })

  return (
    <div className="flex flex-col gap-6 p-6">
      <RebanhoHeader total={total} />
      <Suspense fallback={<GridSkeleton rows={20} />}>
        <RebanhoGrid animais={animais} tenantId={tenantId} />
      </Suspense>
    </div>
  )
}`,
  zustand: `// lib/stores/app-store.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

interface AppState {
  tenant: { id: string; nome: string; plano: string } | null
  user: { id: string; nome: string; roles: string[] } | null
  modules: string[]  // ['AGRICOLA_A1', 'PECUARIA_P1', ...]
  activeFazenda: string | null
  setTenant: (t: AppState['tenant']) => void
  setModules: (m: string[]) => void
  hasModule: (id: string) => boolean
}

export const useAppStore = create<AppState>()(
  persist(
    immer((set, get) => ({
      tenant: null, user: null, modules: [], activeFazenda: null,
      setTenant: (tenant) => set(s => { s.tenant = tenant }),
      setModules: (modules) => set(s => { s.modules = modules }),
      // Verifica se módulo está habilitado
      hasModule: (id) => get().modules.includes(id),
    })),
    { name: 'agro-state', partialize: (s) => ({ activeFazenda: s.activeFazenda }) }
  )
)`,
};

// ═══════════════════════════════════════════════════════
//  CAMADA 2 — BACKEND LAYER
// ═══════════════════════════════════════════════════════
const services = [
  {
    id: "core", name: "api-core", port: 8000, color: "#6366f1", desc: "Autenticação, multitenancy, usuários, permissões", routes: [
      { method: "POST", path: "/auth/token/refresh", desc: "Renova JWT via Keycloak" },
      { method: "GET", path: "/tenants/{id}/modules", desc: "Lista módulos contratados" },
      { method: "POST", path: "/tenants/{id}/modules/{module}", desc: "Ativa módulo (contratação)" },
      { method: "GET", path: "/users/me", desc: "Perfil + roles + modules" },
    ]
  },
  {
    id: "pecuaria", name: "api-pecuaria", port: 8002, color: "#b45309", desc: "Rebanho, reprodução, sanidade, leite, confinamento", routes: [
      { method: "GET", path: "/animais", desc: "Lista rebanho paginado com filtros" },
      { method: "POST", path: "/animais/{id}/pesagens", desc: "Registra pesagem + calcula GMD" },
      { method: "POST", path: "/reproducao/iatf", desc: "Protocolo IATF em lote" },
      { method: "POST", path: "/sanidade/vacinacoes", desc: "Vacinação em lote" },
    ]
  },
  {
    id: "agricola", name: "api-agricola", port: 8001, color: "#16a34a", desc: "Safra, agricultura, insumos, colheita, precisão", routes: [
      { method: "POST", path: "/safras", desc: "Cria planejamento de safra" },
      { method: "GET", path: "/talhoes/{id}/ndvi", desc: "Índice NDVI (Sentinel-2)" },
      { method: "POST", path: "/ordens-servico", desc: "Cria OS de plantio/colheita" },
      { method: "POST", path: "/colheita/romaneio", desc: "Registra romaneio" },
    ]
  },
  {
    id: "financeiro", name: "api-financeiro", port: 8003, color: "#0891b2", desc: "Contas, custos, NF-e, LCDPR, cotações", routes: [
      { method: "GET", path: "/fluxo-caixa", desc: "Fluxo com projeção 90 dias" },
      { method: "POST", path: "/nfe/emitir", desc: "Emite NF-e via SEFAZ (Celery)" },
      { method: "GET", path: "/dre", desc: "DRE por atividade e período" },
      { method: "GET", path: "/cotacoes/commodities", desc: "Soja, milho, boi em tempo real" },
    ]
  },
  {
    id: "ia", name: "api-ia", port: 8005, color: "#dc2626", desc: "Agrônomo Virtual LLM, diagnóstico pragas, ML", routes: [
      { method: "POST", path: "/chat/mensagem", desc: "Chat streaming com Ollama local" },
      { method: "POST", path: "/diagnostico/praga", desc: "Foto → diagnóstico (YOLO)" },
      { method: "GET", path: "/previsao/safra/{id}", desc: "Previsão ML de produtividade" },
      { method: "POST", path: "/rag/consulta", desc: "Base de conhecimento EMBRAPA" },
    ]
  },
];

const backendCode = {
  base: `# services/base_service.py — MultiTenant BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import TypeVar, Generic, Type
from uuid import UUID

T = TypeVar("T")

class BaseService(Generic[T]):
    """Defense-in-depth além do RLS do PostgreSQL.
    Todos os services herdam — tenant_id sempre filtrado."""
    
    def __init__(self, model: Type[T], session: AsyncSession, tenant_id: UUID):
        self.model = model
        self.session = session
        self.tenant_id = tenant_id

    async def get(self, id: UUID) -> T | None:
        result = await self.session.execute(
            select(self.model).where(and_(
                self.model.id == id,
                self.model.tenant_id == self.tenant_id,
            ))
        )
        return result.scalar_one_or_none()

    async def list(self, limit=50, offset=0, **filters) -> list[T]:
        query = select(self.model).where(
            self.model.tenant_id == self.tenant_id
        )
        for field, value in filters.items():
            if value is not None:
                query = query.where(getattr(self.model, field) == value)
        result = await self.session.execute(query.limit(limit).offset(offset))
        return list(result.scalars().all())`,
  deps: `# dependencies.py — Injeção de tenant + feature gate
from fastapi import Depends, HTTPException, Header
from uuid import UUID

async def get_tenant_id(x_tenant_id: str = Header(...)) -> UUID:
    """Tenant ID injetado pelo Traefik/Next.js middleware."""
    try:
        return UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(400, "tenant_id inválido")

async def get_current_user(
    x_user_roles: str = Header(...),
    x_modules: str = Header(...),
) -> dict:
    import json
    return {
        "roles": json.loads(x_user_roles),
        "modules": json.loads(x_modules),
    }

def require_module(module_id: str):
    """Feature gate por módulo. Uso: Depends(require_module("PECUARIA_P1"))"""
    async def check(user: dict = Depends(get_current_user)):
        if module_id not in user["modules"]:
            raise HTTPException(403, detail={
                "error": "MODULE_NOT_CONTRACTED",
                "module": module_id,
            })
    return check`,
};

// ═══════════════════════════════════════════════════════
//  CAMADA 3 — DATA LAYER
// ═══════════════════════════════════════════════════════
const sqlSnippets = {
  rls: `-- Row Level Security — isolamento por tenant em todas as tabelas
ALTER TABLE animais ENABLE ROW LEVEL SECURITY;
ALTER TABLE animais FORCE ROW LEVEL SECURITY;

CREATE POLICY "tenant_isolation" ON animais
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- FastAPI injeta no início de cada request:
-- SET LOCAL app.current_tenant_id = '<uuid-do-tenant>';`,
  timescale: `-- TimescaleDB — Hypertable para pesagens (séries temporais)
SELECT create_hypertable('pesagens', by_range('data_pesagem', INTERVAL '1 month'));

ALTER TABLE pesagens SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'tenant_id, animal_id',
    timescaledb.compress_orderby   = 'data_pesagem DESC'
);
SELECT add_compression_policy('pesagens', INTERVAL '3 months');

-- Continuous Aggregate — GMD mensal pré-calculado
CREATE MATERIALIZED VIEW gmd_mensal_por_lote
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 month', p.data_pesagem) AS mes,
    a.tenant_id, a.lote_id,
    AVG(p.gmd_desde_anterior) AS gmd_medio,
    AVG(p.peso_kg)            AS peso_medio,
    COUNT(DISTINCT a.id)      AS qtd_animais
FROM pesagens p JOIN animais a ON a.id = p.animal_id
GROUP BY 1, 2, 3 WITH NO DATA;`,
  indexes: `-- Índices estratégicos
CREATE INDEX CONCURRENTLY idx_animais_tenant_categoria
    ON animais(tenant_id, categoria) WHERE ativo = true;

CREATE INDEX CONCURRENTLY idx_pesagens_animal_data
    ON pesagens(animal_id, data_pesagem DESC);

CREATE INDEX CONCURRENTLY idx_lancamentos_vencimento
    ON lancamentos_financeiros(tenant_id, data_vencimento)
    WHERE status = 'PENDENTE';

-- PostGIS — spatial index para talhões
CREATE INDEX CONCURRENTLY idx_talhoes_geometria
    ON talhoes USING GIST(geometria);

-- pgvector — HNSW para RAG semântico
CREATE INDEX CONCURRENTLY idx_embeddings_hnsw
    ON documentos_rag USING hnsw(embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);`,
};

const dbTables = [
  { schema: "core", name: "tenants", cols: ["id uuid PK", "nome varchar(200)", "plano varchar(50)", "modulos text[]", "ativo boolean"] },
  { schema: "core", name: "usuarios", cols: ["id uuid PK", "tenant_id uuid FK", "keycloak_id uuid UNIQUE", "roles text[]", "fazendas_acesso uuid[]"] },
  { schema: "core", name: "fazendas", cols: ["id uuid PK", "tenant_id uuid FK", "car varchar(50) UNIQUE", "area_total_ha numeric", "geometria geometry(MultiPolygon)"] },
  { schema: "pecuaria", name: "animais", cols: ["id uuid PK", "tenant_id uuid FK", "brinco_visual varchar(20)", "categoria varchar(20)", "lote_id uuid FK", "mae_id uuid FK(self)"] },
  { schema: "pecuaria", name: "pesagens", cols: ["id uuid PK", "animal_id uuid FK", "peso_kg numeric", "data_pesagem timestamptz ⏱", "gmd_desde_anterior numeric"] },
  { schema: "agricola", name: "talhoes", cols: ["id uuid PK", "fazenda_id uuid FK", "area_ha numeric", "geometria geometry(Polygon)", "tipo_solo varchar(50)"] },
  { schema: "agricola", name: "safras", cols: ["id uuid PK", "talhao_id uuid FK", "cultura varchar(50)", "produtividade_prev_sc_ha numeric", "status varchar(20)"] },
  { schema: "financeiro", name: "lancamentos_financeiros", cols: ["id uuid PK", "tipo IN(RECEITA,DESPESA)", "valor numeric(15,2)", "data_vencimento date", "centro_custo varchar(50)"] },
  { schema: "financeiro", name: "notas_fiscais", cols: ["id uuid PK", "chave_acesso char(44) UNIQUE", "status IN(AUTORIZADA,ERRO...)", "xml_completo text", "job_id varchar(100)"] },
];

// ═══════════════════════════════════════════════════════
//  CAMADA 4 — INFRA LAYER
// ═══════════════════════════════════════════════════════
const infraCode = {
  deployment: `# deployment.yaml — K3s (Kubernetes) — api-pecuaria
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-pecuaria
  namespace: agrosass-prod
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  template:
    spec:
      containers:
        - name: api-pecuaria
          image: harbor.agrosass.local/agrosass/api-pecuaria:1.0.0
          ports: [{ containerPort: 8002 }]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef: { name: db-creds, key: DATABASE_URL }
          resources:
            requests: { memory: "256Mi", cpu: "250m" }
            limits:   { memory: "512Mi", cpu: "1000m" }
          readinessProbe:
            httpGet: { path: /health, port: 8002 }
          livenessProbe:
            httpGet: { path: /health, port: 8002 }
            initialDelaySeconds: 30`,
  cicd: `# .gitea/workflows/deploy.yaml — Pipeline completo
name: Deploy AgroSaaS
on:
  push:
    branches: [main]

jobs:
  lint-test:
    steps:
      - run: ruff check . && mypy .
      - run: pytest --cov=. --cov-fail-under=80
      - run: pnpm lint && pnpm tsc --noEmit
      - run: pnpm test:ci

  build-push:
    needs: lint-test
    strategy:
      matrix:
        service: [api-core, api-pecuaria, api-agricola, api-financeiro, api-ia, web]
    steps:
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: harbor.agrosass.local/agrosass/\${{ matrix.service }}:\${{ github.sha }}

  deploy:
    needs: build-push
    steps:
      - name: Deploy staging
        run: kubectl set image deployment/\$SERVICE api=harbor.../\$SERVICE:\$SHA -n agrosass-staging
      - name: Smoke tests
        run: pytest tests/smoke/ --base-url=https://staging.agrosass.local
      - name: Deploy produção
        run: kubectl set image deployment/\$SERVICE api=harbor.../\$SERVICE:\$SHA -n agrosass-prod`,
};

const infraComponents = [
  {
    category: "Orquestração", icon: "☸️", items: [
      { name: "K3s v1.31", role: "Kubernetes certificado CNCF para on-premise/bare metal. 50% menos RAM que vanilla K8s." },
      { name: "Helm 3", role: "Gerenciamento de charts: Traefik, cert-manager, Longhorn, Prometheus, Keycloak." },
      { name: "Longhorn", role: "Storage distribuído nativo K8s. Replica volumes entre nodes. Backup para MinIO." },
    ], color: "#6366f1"
  },
  {
    category: "Gateway & Segurança", icon: "🔀", items: [
      { name: "Traefik v3", role: "Auto-discovery via K8s labels. TLS automático. Rate limiting e middleware de auth." },
      { name: "Keycloak 26", role: "SSO/OIDC/SAML self-hosted. JWT com claims de tenant + roles + modules." },
      { name: "HashiCorp Vault", role: "Secrets dinâmicos para PostgreSQL. PKI interna. Audit log de todos os acessos." },
      { name: "WireGuard VPN", role: "Túnel seguro para operadores de campo e sedes de fazendas remotas." },
    ], color: "#8b5cf6"
  },
  {
    category: "CI/CD & Registry", icon: "🚀", items: [
      { name: "Gitea", role: "Git self-hosted. Gitea Actions para CI/CD sem GitHub/GitLab." },
      { name: "Harbor", role: "Registry de containers self-hosted. Vulnerability scanning. Signed images." },
      { name: "Ansible", role: "Provisionamento de servidores do zero com um único comando." },
    ], color: "#16a34a"
  },
  {
    category: "Observabilidade (LGTM)", icon: "📊", items: [
      { name: "Prometheus + AlertManager", role: "Métricas de infra, serviços e K8s. Alertas para Slack/WhatsApp." },
      { name: "Loki + Promtail", role: "Logs agregados de todos os containers. Correlação com métricas." },
      { name: "Grafana Tempo", role: "Distributed tracing OpenTelemetry por todos os microsserviços." },
      { name: "Sentry (self-hosted)", role: "Error tracking Next.js + FastAPI com stack traces completos." },
    ], color: "#d97706"
  },
];

// ═══════════════════════════════════════════════════════
//  COMPONENTES COMPARTILHADOS
// ═══════════════════════════════════════════════════════
const methodColors = {
  GET: "#4ade80", POST: "#60a5fa", PUT: "#fb923c", DELETE: "#f87171", PATCH: "#c084fc",
};

function CodePanel({ code, lang, bg = "#0a0f0a", border = "#1a3a1a", textColor = "#a8d8a0" }) {
  const [copied, setCopied] = useState(false);
  return (
    <div style={{ background: bg, borderRadius: 8, border: `1px solid ${border}`, overflow: "hidden" }}>
      <div style={{ background: bg, padding: "7px 12px", borderBottom: `1px solid ${border}`, display: "flex", justifyContent: "space-between" }}>
        <span style={{ fontSize: 9, fontWeight: 800, color: "#64748b", letterSpacing: 1 }}>{lang}</span>
        <button onClick={() => { navigator.clipboard?.writeText(code); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
          style={{ background: copied ? "#059669" : "#1e293b", color: copied ? "#fff" : "#64748b", border: "none", borderRadius: 3, padding: "2px 8px", fontSize: 9, cursor: "pointer", fontWeight: 700 }}>
          {copied ? "✓" : "COPIAR"}
        </button>
      </div>
      <pre style={{ margin: 0, padding: "12px 14px", fontSize: 10, lineHeight: 1.7, color: textColor, overflowX: "auto", maxHeight: 340, overflowY: "auto" }}>
        <code>{code}</code>
      </pre>
    </div>
  );
}

// ═══════════════════════════════════════════════════════
//  APP PRINCIPAL
// ═══════════════════════════════════════════════════════
const LAYERS = [
  { id: "client", icon: "🖥️", label: "CLIENT", sub: "Next.js 16 · React 19 · TypeScript · Expo", color: "#0ea5e9" },
  { id: "backend", icon: "⚙️", label: "BACKEND", sub: "FastAPI · Python 3.12 · Celery · Ollama", color: "#16a34a" },
  { id: "data", icon: "🗄️", label: "DATA", sub: "PostgreSQL 16 · PostGIS · TimescaleDB · Redis", color: "#7c3aed" },
  { id: "infra", icon: "🏗️", label: "INFRA", sub: "K3s · Traefik · Keycloak · Ansible · LGTM", color: "#d97706" },
];

export default function AgroSaaSStack() {
  const [activeLayer, setActiveLayer] = useState("client");
  const [activeClientTab, setActiveClientTab] = useState("deps");
  const [activeClientCategory, setActiveClientCategory] = useState("core");
  const [activeClientCode, setActiveClientCode] = useState("middleware");
  const [activeService, setActiveService] = useState("pecuaria");
  const [activeBackendCode, setActiveBackendCode] = useState("base");
  const [activeDataTab, setActiveDataTab] = useState("tables");
  const [activeDataSql, setActiveDataSql] = useState("rls");
  const [activeInfraCategory, setActiveInfraCategory] = useState(0);
  const [activeInfraCode, setActiveInfraCode] = useState("deployment");

  const layer = LAYERS.find(l => l.id === activeLayer);
  const currentService = services.find(s => s.id === activeService);

  return (
    <div style={{ fontFamily: "'JetBrains Mono','Fira Code',monospace", background: "#080c10", minHeight: "100vh", color: "#e2e8f0" }}>

      {/* ── HEADER ── */}
      <div style={{ background: "linear-gradient(135deg, #0f172a 0%, #0d1f3c 50%, #0a1f14 100%)", borderBottom: "1px solid #1e2a3a", padding: "18px 20px" }}>
        <div style={{ maxWidth: 980, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14 }}>
            <span style={{ fontSize: 28 }}>🌾</span>
            <div>
              <h1 style={{ color: "#f1f5f9", fontSize: 17, fontWeight: 900, margin: 0, letterSpacing: -0.5 }}>
                AgroSaaS — Stack Técnico Detalhado
              </h1>
              <p style={{ color: "#475569", fontSize: 10, margin: 0, marginTop: 2 }}>
                Next.js 16 · Python / FastAPI · PostgreSQL 16 · K3s On-Premise · 100% Open-Source
              </p>
            </div>
            <div style={{ marginLeft: "auto" }}>
              <span style={{ fontSize: 9, fontWeight: 800, color: "#4ade80", background: "#052e16", border: "1px solid #166534", padding: "4px 10px", borderRadius: 20 }}>
                ON-PREMISE FIRST
              </span>
            </div>
          </div>

          {/* Layer tabs */}
          <div style={{ display: "flex", gap: 4 }}>
            {LAYERS.map(l => (
              <button key={l.id} onClick={() => setActiveLayer(l.id)} style={{
                flex: 1, padding: "10px 8px", borderRadius: 8, cursor: "pointer",
                border: `1.5px solid ${activeLayer === l.id ? l.color : "#1e2a3a"}`,
                background: activeLayer === l.id ? l.color + "18" : "#0f172a",
                color: activeLayer === l.id ? l.color : "#334155",
                transition: "all 0.2s"
              }}>
                <div style={{ fontSize: 16, marginBottom: 3 }}>{l.icon}</div>
                <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: 1 }}>{l.label}</div>
                <div style={{ fontSize: 8, opacity: 0.7, marginTop: 2, lineHeight: 1.3 }}>{l.sub}</div>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div style={{ maxWidth: 980, margin: "0 auto", padding: "14px 12px 48px" }}>

        {/* ══════════════════════════════════════════
            LAYER: CLIENT
        ══════════════════════════════════════════ */}
        {activeLayer === "client" && (
          <div>
            <div style={{ display: "flex", gap: 6, marginBottom: 12 }}>
              {["deps", "flows", "code"].map(t => (
                <button key={t} onClick={() => setActiveClientTab(t)} style={{
                  padding: "5px 14px", borderRadius: 6, fontSize: 10, fontWeight: 700, cursor: "pointer",
                  border: "none",
                  background: activeClientTab === t ? "#0ea5e9" : "#0f1a2e",
                  color: activeClientTab === t ? "#fff" : "#334155",
                  textTransform: "uppercase"
                }}>{t === "deps" ? "Dependências" : t === "flows" ? "Fluxos" : "Código"}</button>
              ))}
            </div>

            {activeClientTab === "deps" && (
              <div>
                <div style={{ display: "flex", gap: 5, marginBottom: 10, flexWrap: "wrap" }}>
                  {Object.keys(deps).map(cat => (
                    <button key={cat} onClick={() => setActiveClientCategory(cat)} style={{
                      padding: "3px 12px", borderRadius: 20, fontSize: 9, fontWeight: 800, cursor: "pointer",
                      border: `1.5px solid ${activeClientCategory === cat ? "#0ea5e9" : "#1e2a3a"}`,
                      background: activeClientCategory === cat ? "#0c2233" : "transparent",
                      color: activeClientCategory === cat ? "#38bdf8" : "#334155",
                      textTransform: "uppercase", letterSpacing: 1
                    }}>{cat}</button>
                  ))}
                </div>
                <div style={{ display: "grid", gap: 6 }}>
                  {deps[activeClientCategory].map((d, i) => (
                    <div key={i} style={{ display: "grid", gridTemplateColumns: "200px 100px 1fr", gap: 10, alignItems: "start", background: "#0a1628", border: "1px solid #1e2a3a", borderRadius: 7, padding: "10px 14px" }}>
                      <code style={{ color: "#38bdf8", fontWeight: 800, fontSize: 12 }}>{d.name}</code>
                      <code style={{ color: "#475569", fontSize: 9, background: "#0f172a", padding: "2px 6px", borderRadius: 3 }}>v{d.version}</code>
                      <span style={{ fontSize: 11, color: "#64748b", lineHeight: 1.5 }}>{d.why}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeClientTab === "flows" && (
              <div style={{ display: "grid", gap: 10 }}>
                {[
                  {
                    title: "Multi-tenant Auth (Edge Middleware)", color: "#0ea5e9", steps: [
                      ["Browser", "Acessa fazendaabc.agrosass.local"],
                      ["Next.js Middleware (Edge)", "Extrai tenant do hostname, valida JWT sem cold start"],
                      ["Keycloak SSO", "Emite JWT com claims: tenant_id + roles[] + modules[]"],
                      ["Server Layout (RSC)", "Lê JWT, renderiza menu só com módulos contratados"],
                      ["Unleash Feature Flags", "Valida módulos contratados por tenant no server"],
                      ["UI Final", "Dashboard personalizado — zero flash de conteúdo não autorizado"],
                    ]
                  },
                  {
                    title: "React Server Components — DRE Financeiro", color: "#4ade80", steps: [
                      ["Usuário", "Navega para /financeiro/dre?safra=2024"],
                      ["RSC (servidor)", "Busca DRE diretamente no PostgreSQL — sem roundtrip API"],
                      ["Suspense Streaming", "Envia HTML parcial: tabela principal antes dos gráficos"],
                      ["Client Component", "Hidrata somente os filtros interativos (bundle mínimo)"],
                      ["TanStack Query", "Revalida em background a cada 5 min"],
                    ]
                  },
                  {
                    title: "Offline-First Mobile (Campo Rural)", color: "#f59e0b", steps: [
                      ["Operador de Campo", "Abre app sem sinal 4G (área rural remota)"],
                      ["WatermelonDB", "Serve dados do SQLite local — app funciona normalmente"],
                      ["Usuário", "Registra pesagem, vacinação e foto de praga"],
                      ["NetInfo API", "Detecta conectividade restaurada em background"],
                      ["Sync Engine", "Push de registros offline → FastAPI /sync"],
                      ["FastAPI + PostgreSQL", "Persiste dados, retorna delta — device sincronizado"],
                    ]
                  },
                ].map((flow, fi) => (
                  <div key={fi} style={{ background: "#0a1628", borderRadius: 10, border: `1px solid ${flow.color}30`, padding: 14 }}>
                    <div style={{ color: flow.color, fontWeight: 800, fontSize: 11, marginBottom: 12 }}>{flow.title}</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
                      {flow.steps.map((step, i) => (
                        <div key={i} style={{ display: "flex", gap: 0, alignItems: "stretch" }}>
                          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 28, flexShrink: 0 }}>
                            <div style={{ width: 22, height: 22, borderRadius: "50%", background: flow.color, color: "#000", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 9, fontWeight: 900, flexShrink: 0 }}>{i + 1}</div>
                            {i < flow.steps.length - 1 && <div style={{ width: 2, flex: 1, background: flow.color + "30", margin: "2px 0" }} />}
                          </div>
                          <div style={{ marginLeft: 10, paddingBottom: i < flow.steps.length - 1 ? 10 : 0, flex: 1 }}>
                            <span style={{ fontSize: 9, fontWeight: 800, color: flow.color, background: flow.color + "18", padding: "1px 6px", borderRadius: 3, marginRight: 8 }}>{step[0]}</span>
                            <span style={{ fontSize: 11, color: "#cbd5e1" }}>{step[1]}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeClientTab === "code" && (
              <div>
                <div style={{ display: "flex", gap: 5, marginBottom: 10 }}>
                  {Object.keys(clientCode).map(k => (
                    <button key={k} onClick={() => setActiveClientCode(k)} style={{
                      padding: "4px 12px", borderRadius: 6, fontSize: 10, fontWeight: 700, cursor: "pointer",
                      border: `1px solid ${activeClientCode === k ? "#38bdf8" : "#1e2a3a"}`,
                      background: activeClientCode === k ? "#0c2233" : "transparent",
                      color: activeClientCode === k ? "#38bdf8" : "#334155"
                    }}>{k}</button>
                  ))}
                </div>
                <CodePanel code={clientCode[activeClientCode]} lang="TYPESCRIPT" bg="#08111e" border="#1e2a3a" textColor="#a8c8e8" />
              </div>
            )}
          </div>
        )}

        {/* ══════════════════════════════════════════
            LAYER: BACKEND
        ══════════════════════════════════════════ */}
        {activeLayer === "backend" && (
          <div>
            {/* Serviços */}
            <div style={{ display: "flex", gap: 5, flexWrap: "wrap", marginBottom: 10 }}>
              {services.map(s => (
                <button key={s.id} onClick={() => setActiveService(s.id)} style={{
                  padding: "4px 12px", borderRadius: 20, fontSize: 10, fontWeight: 700, cursor: "pointer",
                  border: `1.5px solid ${activeService === s.id ? s.color : "#1a2e1a"}`,
                  background: activeService === s.id ? s.color + "18" : "transparent",
                  color: activeService === s.id ? s.color : "#2a4a2a"
                }}>{s.name}</button>
              ))}
            </div>

            {currentService && (
              <div style={{ background: "#0a140a", borderRadius: 10, border: `1.5px solid ${currentService.color}40`, overflow: "hidden", marginBottom: 12 }}>
                <div style={{ background: currentService.color + "15", padding: "10px 14px", borderBottom: `1px solid ${currentService.color}20` }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ color: currentService.color, fontWeight: 800, fontSize: 13 }}>{currentService.name}</span>
                    <code style={{ color: "#334155", fontSize: 10, background: "#0a0f0a", padding: "2px 7px", borderRadius: 3 }}>:{currentService.port}</code>
                    <span style={{ fontSize: 10, color: "#2a4a2a" }}>{currentService.desc}</span>
                  </div>
                </div>
                {currentService.routes.map((r, i) => (
                  <div key={i} style={{ display: "flex", gap: 10, alignItems: "center", padding: "9px 14px", background: i % 2 === 0 ? "#080f08" : "#0a140a", borderTop: i > 0 ? "1px solid #0f1f0f" : "none" }}>
                    <span style={{ fontSize: 8, fontWeight: 800, color: methodColors[r.method] ?? "#64748b", background: (methodColors[r.method] ?? "#64748b") + "18", border: `1px solid ${(methodColors[r.method] ?? "#64748b")}40`, padding: "2px 6px", borderRadius: 3, minWidth: 38, textAlign: "center" }}>{r.method}</span>
                    <code style={{ fontSize: 10, color: "#7dd3fc", background: "#0f1a2e", padding: "2px 8px", borderRadius: 3, minWidth: 240 }}>{r.path}</code>
                    <span style={{ fontSize: 10, color: "#2a4a2a" }}>{r.desc}</span>
                  </div>
                ))}
              </div>
            )}

            <div style={{ display: "flex", gap: 5, marginBottom: 10 }}>
              {Object.keys(backendCode).map(k => (
                <button key={k} onClick={() => setActiveBackendCode(k)} style={{
                  padding: "4px 12px", borderRadius: 6, fontSize: 10, fontWeight: 700, cursor: "pointer",
                  border: `1px solid ${activeBackendCode === k ? "#4ade80" : "#1a3a1a"}`,
                  background: activeBackendCode === k ? "#0c200c" : "transparent",
                  color: activeBackendCode === k ? "#4ade80" : "#2a4a2a"
                }}>{k}</button>
              ))}
            </div>
            <CodePanel code={backendCode[activeBackendCode]} lang="PYTHON" bg="#080f08" border="#1a3a1a" textColor="#a8d8a0" />
          </div>
        )}

        {/* ══════════════════════════════════════════
            LAYER: DATA
        ══════════════════════════════════════════ */}
        {activeLayer === "data" && (
          <div>
            <div style={{ display: "flex", gap: 6, marginBottom: 12 }}>
              {["tables", "sql", "extensions"].map(t => (
                <button key={t} onClick={() => setActiveDataTab(t)} style={{
                  padding: "5px 14px", borderRadius: 6, fontSize: 10, fontWeight: 700, cursor: "pointer",
                  border: "none",
                  background: activeDataTab === t ? "#7c3aed" : "#14082e",
                  color: activeDataTab === t ? "#fff" : "#4b3a7a",
                  textTransform: "uppercase"
                }}>{t === "tables" ? "Schema / Tabelas" : t === "sql" ? "SQL Crítico" : "Extensões"}</button>
              ))}
            </div>

            {activeDataTab === "tables" && (
              <div style={{ display: "grid", gap: 6 }}>
                {dbTables.map((t, i) => (
                  <div key={i} style={{ background: "#0c0820", borderRadius: 8, border: "1px solid #1a1040", padding: "10px 14px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                      <code style={{ color: "#a78bfa", fontWeight: 800, fontSize: 12 }}>{t.name}</code>
                      <span style={{ fontSize: 9, color: "#4b3a7a", background: "#0a0618", padding: "1px 7px", borderRadius: 4, fontWeight: 700, letterSpacing: 1 }}>{t.schema.toUpperCase()}</span>
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                      {t.cols.map((c, j) => (
                        <span key={j} style={{
                          fontSize: 9, fontFamily: "monospace",
                          color: c.includes("PK") ? "#fbbf24" : c.includes("FK") ? "#60a5fa" : c.includes("⏱") ? "#f59e0b" : "#64748b",
                          background: "#0a0618",
                          border: `1px solid ${c.includes("PK") ? "#fbbf2430" : c.includes("FK") ? "#60a5fa30" : "#1a1040"}`,
                          padding: "2px 7px", borderRadius: 3
                        }}>{c}</span>
                      ))}
                    </div>
                  </div>
                ))}
                <div style={{ fontSize: 9, color: "#2a1a5a", textAlign: "center", padding: 4 }}>
                  🟡 PK — Primary Key &nbsp;|&nbsp; 🔵 FK — Foreign Key &nbsp;|&nbsp; ⏱ TimescaleDB hypertable
                </div>
              </div>
            )}

            {activeDataTab === "sql" && (
              <div>
                <div style={{ display: "flex", gap: 5, marginBottom: 10 }}>
                  {Object.keys(sqlSnippets).map(k => (
                    <button key={k} onClick={() => setActiveDataSql(k)} style={{
                      padding: "4px 12px", borderRadius: 6, fontSize: 10, fontWeight: 700, cursor: "pointer",
                      border: `1px solid ${activeDataSql === k ? "#a78bfa" : "#1a1040"}`,
                      background: activeDataSql === k ? "#1a0a3e" : "transparent",
                      color: activeDataSql === k ? "#a78bfa" : "#2a1a5a"
                    }}>{k}</button>
                  ))}
                </div>
                <CodePanel code={sqlSnippets[activeDataSql]} lang="SQL" bg="#0a0820" border="#1a1040" textColor="#c4b5fd" />
              </div>
            )}

            {activeDataTab === "extensions" && (
              <div style={{ display: "grid", gap: 8 }}>
                {[
                  { name: "PostGIS 3.5", color: "#3b82f6", items: ["Geometrias de talhões e fazendas (MultiPolygon)", "APP e Reserva Legal com ST_Intersects", "Distâncias e áreas com ST_Area, ST_Distance", "Índice GIST para queries geoespaciais rápidas", "Export GeoJSON para frontend MapLibre"] },
                  { name: "TimescaleDB 2.x", color: "#f59e0b", items: ["Hypertables para pesagens, IoT, histórico de produção", "Particionamento automático por tempo (1 mês)", "Compressão 90%+ em dados históricos (> 3 meses)", "Continuous aggregates pré-calculados (GMD mensal)", "Retenção automática configurável por tenant"] },
                  { name: "pgvector 0.8", color: "#ec4899", items: ["Índice HNSW para busca semântica O(log n)", "RAG pipeline: laudos, manuais EMBRAPA, NFs", "Embeddings de 1536 dims (text-embedding-3-small)", "Busca por similaridade cosine em ms", "Base de conhecimento agronômico consultável via LLM"] },
                  { name: "pg_cron + pg_stat_statements", color: "#10b981", items: ["Jobs agendados no banco (sem Celery para tarefas simples)", "Limpeza de tokens expirados às 3h diariamente", "Atualização de GMD pendente a cada 6h", "Monitoramento de queries lentas (> 100ms) exportado ao Prometheus", "Identificação de N+1 queries em desenvolvimento"] },
                ].map((ext, i) => (
                  <div key={i} style={{ background: "#0c0820", borderRadius: 8, border: `1px solid ${ext.color}30`, padding: "12px 14px" }}>
                    <div style={{ color: ext.color, fontWeight: 800, fontSize: 12, marginBottom: 8 }}>
                      <code>CREATE EXTENSION {ext.name};</code>
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                      {ext.items.map((item, j) => (
                        <span key={j} style={{ fontSize: 10, color: "#4b3a7a", background: "#0a0618", border: "1px solid #1a1040", padding: "3px 8px", borderRadius: 4 }}>
                          • {item}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ══════════════════════════════════════════
            LAYER: INFRA
        ══════════════════════════════════════════ */}
        {activeLayer === "infra" && (
          <div>
            {/* Network diagram */}
            <div style={{ background: "#0d0d1e", borderRadius: 10, border: "1px solid #1a1a3a", padding: "12px 14px", marginBottom: 12 }}>
              <div style={{ fontSize: 9, color: "#4b4b8a", fontWeight: 700, letterSpacing: 1, marginBottom: 8 }}>DIAGRAMA DE REDE ON-PREMISE</div>
              {[
                { label: "CAMPO / REMOTO", items: ["Mobile App (4G)", "Laptop Técnico", "Sede da Fazenda"], color: "#0891b2" },
                { label: "PERÍMETRO", items: ["WireGuard VPN", "Cloudflare CDN", "pfSense + Suricata"], color: "#8b5cf6" },
                { label: "GATEWAY (K3s)", items: ["Traefik v3", "Keycloak SSO", "Vault Secrets"], color: "#6366f1" },
                { label: "APP NODES", items: ["api-core/agricola/pecuaria/financeiro/ia", "Next.js Web", "Celery Workers"], color: "#16a34a" },
                { label: "DATA NODES", items: ["PostgreSQL Patroni HA x3", "Redis Sentinel x3", "MinIO Cluster"], color: "#dc2626" },
                { label: "OBSERVABILITY", items: ["Prometheus + Grafana", "Loki + Tempo", "Sentry + Uptime Kuma"], color: "#d97706" },
              ].map((row, i, arr) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: i < arr.length - 1 ? 5 : 0, flexWrap: "wrap" }}>
                  <span style={{ fontSize: 8, fontWeight: 800, color: row.color, minWidth: 130, textAlign: "right", letterSpacing: 0.5 }}>{row.label}</span>
                  <span style={{ color: "#1a1a3a", fontSize: 12 }}>▶</span>
                  {row.items.map((item, j) => (
                    <span key={j} style={{ fontSize: 9, color: row.color, background: row.color + "12", border: `1px solid ${row.color}25`, padding: "2px 7px", borderRadius: 4, fontWeight: 600 }}>{item}</span>
                  ))}
                </div>
              ))}
            </div>

            {/* Componentes */}
            <div style={{ display: "flex", gap: 5, flexWrap: "wrap", marginBottom: 10 }}>
              {infraComponents.map((cat, i) => (
                <button key={i} onClick={() => setActiveInfraCategory(i)} style={{
                  padding: "4px 12px", borderRadius: 20, fontSize: 10, fontWeight: 700, cursor: "pointer",
                  border: `1.5px solid ${activeInfraCategory === i ? cat.color : "#1a1a3a"}`,
                  background: activeInfraCategory === i ? cat.color + "18" : "transparent",
                  color: activeInfraCategory === i ? cat.color : "#2a2a4a"
                }}>{cat.icon} {cat.category}</button>
              ))}
            </div>

            <div style={{ background: "#0d0d1e", borderRadius: 10, border: `1px solid ${infraComponents[activeInfraCategory].color}30`, overflow: "hidden", marginBottom: 12 }}>
              {infraComponents[activeInfraCategory].items.map((item, i) => (
                <div key={i} style={{ display: "grid", gridTemplateColumns: "180px 1fr", gap: 12, padding: "10px 14px", background: i % 2 === 0 ? "#090914" : "#0d0d1e", borderTop: i > 0 ? "1px solid #1a1a3a" : "none" }}>
                  <code style={{ color: infraComponents[activeInfraCategory].color, fontWeight: 800, fontSize: 11 }}>{item.name}</code>
                  <span style={{ fontSize: 11, color: "#334155", lineHeight: 1.6 }}>{item.role}</span>
                </div>
              ))}
            </div>

            <div style={{ display: "flex", gap: 5, marginBottom: 10 }}>
              {Object.keys(infraCode).map(k => (
                <button key={k} onClick={() => setActiveInfraCode(k)} style={{
                  padding: "4px 12px", borderRadius: 6, fontSize: 10, fontWeight: 700, cursor: "pointer",
                  border: `1px solid ${activeInfraCode === k ? "#818cf8" : "#1a1a3a"}`,
                  background: activeInfraCode === k ? "#1e1b4b" : "transparent",
                  color: activeInfraCode === k ? "#818cf8" : "#2a2a4a"
                }}>{k}</button>
              ))}
            </div>
            <CodePanel code={infraCode[activeInfraCode]} lang="YAML" bg="#090914" border="#1a1a3a" textColor="#a5b4fc" />
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{ borderTop: "1px solid #0f1a2a", padding: "10px 20px", textAlign: "center" }}>
        <p style={{ fontSize: 9, color: "#1e2a3a", margin: 0, letterSpacing: 0.5 }}>
          100% OPEN-SOURCE · PostgreSQL · Redis · K3s · MinIO · Keycloak · Prometheus · Grafana · Ollama · Apache 2.0 / MIT / BSD
        </p>
      </div>
    </div>
  );
}
