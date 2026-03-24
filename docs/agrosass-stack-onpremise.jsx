import { useState } from "react";

const layers = [
  {
    id: "client",
    icon: "🖥️",
    label: "CLIENT LAYER",
    subtitle: "Interface & Experiência",
    color: "#0ea5e9",
    bg: "#f0f9ff",
    border: "#bae6fd",
    items: [
      {
        name: "Next.js 16",
        tag: "App Router + RSC",
        desc: "Framework principal. Server Components reduzem bundle em telas pesadas (rebanho, DRE, relatórios). App Router com layouts por módulo/plugin.",
        type: "core",
        links: ["TypeScript 5.x", "Turbopack"]
      },
      {
        name: "shadcn/ui + Tailwind 4",
        tag: "Design System",
        desc: "Componentes acessíveis, customizáveis e sem dependência de vendor. Base para todo o design system do produto.",
        type: "core",
        links: ["Radix UI", "CVA"]
      },
      {
        name: "TanStack Query v5",
        tag: "Server State",
        desc: "Cache inteligente, revalidação automática, otimistic updates. Essencial para dashboards com dados em tempo real de campo.",
        type: "core",
        links: ["TanStack Table", "TanStack Router"]
      },
      {
        name: "Zustand",
        tag: "Client State",
        desc: "Estado global leve (usuário, tenant ativo, módulos habilitados, preferências). Sem boilerplate do Redux.",
        type: "core",
        links: ["Immer", "Persist middleware"]
      },
      {
        name: "AG Grid Community",
        tag: "Data Grids",
        desc: "Tabelas com 100k+ linhas para rebanho, financeiro e estoque. Virtualização, filtros avançados, exportação Excel.",
        type: "core",
        links: ["React Hook Form", "Zod"]
      },
      {
        name: "Recharts + Nivo",
        tag: "Visualização",
        desc: "Recharts para gráficos de série temporal (pesagem, produção de leite, colheita). Nivo para heatmaps e gráficos de área.",
        type: "core",
        links: ["D3.js (base)"]
      },
      {
        name: "MapLibre GL JS",
        tag: "Mapas (open-source)",
        desc: "Fork open-source do Mapbox GL. Mapas de talhões, áreas de pastagem, APP/Reserva Legal. Sem custo de API key.",
        type: "infra",
        links: ["PMTiles", "GeoJSON", "PostGIS"]
      },
      {
        name: "React Native + Expo",
        tag: "Mobile Field App",
        desc: "App offline-first para operadores no campo. Compartilha hooks, tipos TS e lógica com o front web.",
        type: "mobile",
        links: ["WatermelonDB (offline)", "Expo Camera", "Expo Location"]
      }
    ]
  },
  {
    id: "gateway",
    icon: "🔀",
    label: "GATEWAY LAYER",
    subtitle: "Entrada única, segurança perimetral",
    color: "#8b5cf6",
    bg: "#faf5ff",
    border: "#ddd6fe",
    items: [
      {
        name: "Traefik v3",
        tag: "API Gateway + Reverse Proxy",
        desc: "Auto-discovery de serviços via Docker/K8s labels. TLS automático com cert-manager. Rate limiting, middleware de autenticação e roteamento por tenant/subdomínio.",
        type: "core",
        links: ["cert-manager", "Let's Encrypt (interno: step-ca)"]
      },
      {
        name: "Keycloak",
        tag: "Identity Provider (IdP)",
        desc: "SSO, OAuth2/OIDC, RBAC multi-tenant self-hosted. Integra com LDAP/AD corporativo. JWT emitidos para todos os serviços.",
        type: "core",
        links: ["LDAP/AD sync", "TOTP/MFA", "Social login"]
      },
      {
        name: "Unleash (Feature Flags)",
        tag: "Plugin / Module Gates",
        desc: "Feature flags por tenant para habilitar/desabilitar módulos contratados. Toggle instantâneo sem redeploy. Self-hosted, open-source.",
        type: "core",
        links: ["SDK Python", "SDK Next.js"]
      },
      {
        name: "Nginx / Traefik LoadBalancer",
        tag: "Load Balancer",
        desc: "Balanceamento entre réplicas dos microsserviços. Health checks e circuit breaker nativos.",
        type: "infra",
        links: ["Round-robin", "Sticky sessions"]
      }
    ]
  },
  {
    id: "backend",
    icon: "⚙️",
    label: "BACKEND LAYER",
    subtitle: "Microsserviços Python — um container por domínio",
    color: "#059669",
    bg: "#f0fdf4",
    border: "#bbf7d0",
    items: [
      {
        name: "FastAPI (Python 3.12)",
        tag: "Framework Core",
        desc: "Async nativo, Pydantic v2 para validação rigorosa, OpenAPI automático. Base de todos os microsserviços. Performance on par com Node.js/Go.",
        type: "core",
        links: ["Uvicorn", "Gunicorn", "Starlette"]
      },
      {
        name: "SQLAlchemy 2.0 async",
        tag: "ORM",
        desc: "ORM async com suporte total a PostgreSQL. Queries complexas (JOIN de rebanho + reprodução + pesagem) de forma legível e segura.",
        type: "core",
        links: ["Alembic (migrations)", "asyncpg (driver)"]
      },
      {
        name: "Celery + Redis",
        tag: "Task Queue",
        desc: "Jobs assíncronos: emissão de NF-e, geração de relatórios PDF, sincronização SISBOV, processamento de imagens de satélite, envio de alertas WhatsApp.",
        type: "core",
        links: ["Celery Beat (agendamento)", "Flower (UI)"]
      },
      {
        name: "Pydantic v2",
        tag: "Validação de Dados",
        desc: "Validação estrita de todas as entradas: doses de insumos, pesos animais, coordenadas geográficas, lançamentos financeiros. Erros descritivos para o frontend.",
        type: "core",
        links: ["Type hints", "Serialização JSON"]
      },
      {
        name: "httpx + tenacity",
        tag: "HTTP Client",
        desc: "Chamadas externas async para SEFAZ (NF-e), SISBOV, MAPA/ZARC, cotações B3/CBOT, APIs de clima. Tenacity para retry com backoff exponencial.",
        type: "core",
        links: ["SEFAZ", "SISBOV", "B3", "CPTEC"]
      },
      {
        name: "Microsserviços por Domínio",
        tag: "Arquitetura Modular",
        desc: "api-core | api-agricola | api-pecuaria | api-financeiro | api-operacional | api-ambiental | api-ia | api-integracoes. Cada um deployável e escalável independentemente.",
        type: "arch",
        links: ["gRPC interno (opção)", "REST externo"]
      }
    ]
  },
  {
    id: "data",
    icon: "🗄️",
    label: "DATA LAYER",
    subtitle: "Persistência, cache, busca e analytics",
    color: "#dc2626",
    bg: "#fef2f2",
    border: "#fecaca",
    items: [
      {
        name: "PostgreSQL 16",
        tag: "Banco Principal",
        desc: "Banco relacional principal. JSONB para dados flexíveis (laudos, configurações). Full-text search nativo. Transações ACID para dados financeiros.",
        type: "core",
        links: ["pgBouncer (pooling)", "Patroni (HA)", "pg_dump"]
      },
      {
        name: "PostGIS",
        tag: "Extensão Geoespacial",
        desc: "Talhões, coordenadas de animais (IoT), APP/Reserva Legal, áreas de pastagem. Queries geoespaciais nativas no PostgreSQL.",
        type: "core",
        links: ["ST_Area", "ST_Intersects", "GeoJSON export"]
      },
      {
        name: "TimescaleDB",
        tag: "Séries Temporais",
        desc: "Extensão PostgreSQL para dados de IoT (sensores de solo/clima), histórico de pesagem, produção de leite por dia, telemetria de máquinas.",
        type: "core",
        links: ["Hypertables", "Compressão automática", "Continuous aggregates"]
      },
      {
        name: "pgvector",
        tag: "Embeddings / IA",
        desc: "Armazenamento de vetores semânticos para busca inteligente (laudos veterinários, base de conhecimento agronômico, histórico de ordens de serviço).",
        type: "ai",
        links: ["Semantic search", "RAG pipeline"]
      },
      {
        name: "Redis 7",
        tag: "Cache + Filas",
        desc: "Cache de sessões JWT, resultado de queries pesadas (relatórios, dashboards), filas Celery, pub/sub para WebSocket de alertas em tempo real.",
        type: "core",
        links: ["Redis Sentinel (HA)", "Redis Streams"]
      },
      {
        name: "MinIO",
        tag: "Object Storage (S3-compatible)",
        desc: "Storage self-hosted para fotos de pragas, laudos veterinários PDF, imagens de satélite, backups de banco, documentos fiscais (NF-e XML).",
        type: "infra",
        links: ["S3-compatible API", "Bucket policies", "Versioning"]
      },
      {
        name: "ClickHouse",
        tag: "Analytics / BI",
        desc: "OLAP para relatórios pesados: DRE por safra, análise de custo por arroba, histórico de 5+ anos de produção. Leituras analíticas 100x mais rápidas que PostgreSQL.",
        type: "analytics",
        links: ["Grafana datasource", "ETL do PostgreSQL"]
      },
      {
        name: "Patroni + HAProxy",
        tag: "Alta Disponibilidade",
        desc: "Patroni gerencia failover automático do PostgreSQL (primary → replica). HAProxy roteia reads para réplicas e writes para primary.",
        type: "infra",
        links: ["etcd (consensus)", "3 nós mínimo"]
      }
    ]
  },
  {
    id: "ai",
    icon: "🤖",
    label: "INTELLIGENCE LAYER",
    subtitle: "IA, ML e processamento de dados agro",
    color: "#d97706",
    bg: "#fffbeb",
    border: "#fde68a",
    items: [
      {
        name: "Ollama (self-hosted LLM)",
        tag: "LLM On-Premise",
        desc: "Rodar modelos como Llama 3.1, Mistral, Gemma2 localmente. Agrônomo Virtual com ZERO custo por token e dados 100% na fazenda/datacenter.",
        type: "core",
        links: ["Llama 3.1 8B/70B", "Mistral 7B", "Qwen2.5"]
      },
      {
        name: "LangChain Python",
        tag: "Orchestração LLM",
        desc: "RAG pipeline com base de conhecimento agronômico (EMBRAPA, MAPA, manuais). Memória de conversação por usuário. Tool calling para consultar dados do tenant.",
        type: "core",
        links: ["LangGraph", "pgvector (RAG)", "ChromaDB (opção)"]
      },
      {
        name: "scikit-learn + Prophet",
        tag: "ML Clássico",
        desc: "Previsão de produtividade por talhão (RF/GBM). Series temporais de peso/leite com Prophet. Detecção de anomalias em custos e desempenho de rebanho.",
        type: "core",
        links: ["XGBoost", "MLflow (tracking)", "Joblib"]
      },
      {
        name: "Rasterio + GDAL + Shapely",
        tag: "Geoprocessamento",
        desc: "Processamento de imagens NDVI do Sentinel-2 (ESA, gratuito). Cálculo de índices por talhão. Geração de mapas de variabilidade e zonas de manejo.",
        type: "core",
        links: ["Sentinel Hub API", "INPE API", "Fiona (shapefiles)"]
      },
      {
        name: "YOLOv11 / EfficientNet",
        tag: "Visão Computacional",
        desc: "Diagnóstico de pragas e doenças por foto (app mobile). Modelo treinado com dataset agronômico brasileiro. Inferência local via ONNX.",
        type: "core",
        links: ["ONNX Runtime", "Torchvision", "Albumentations"]
      },
      {
        name: "MLflow (self-hosted)",
        tag: "MLOps",
        desc: "Rastreamento de experimentos, versionamento de modelos, registro de datasets. Pipeline de re-treinamento automatizado com novos dados da safra.",
        type: "infra",
        links: ["MinIO (artifacts)", "PostgreSQL (metadata)"]
      }
    ]
  },
  {
    id: "infra",
    icon: "🏗️",
    label: "INFRASTRUCTURE LAYER",
    subtitle: "On-premise — orquestração, rede e segurança",
    color: "#475569",
    bg: "#f8fafc",
    border: "#e2e8f0",
    items: [
      {
        name: "K3s (Lightweight Kubernetes)",
        tag: "Orquestração de Containers",
        desc: "Kubernetes certificado CNCF para on-premise/bare metal. 50% menos recursos que k8s vanilla. Ideal para servidores da fazenda ou datacenter próprio com hardware limitado.",
        type: "core",
        links: ["Helm 3", "kubectl", "Rancher (UI)"]
      },
      {
        name: "Docker + Docker Compose",
        tag: "Containers",
        desc: "Desenvolvimento local e ambientes menores. Cada módulo/serviço é um container isolado. Compose para orquestrar o ambiente de dev completo.",
        type: "core",
        links: ["BuildKit", "Multi-stage builds", "Harbor (registry)"]
      },
      {
        name: "Gitea (self-hosted)",
        tag: "Git + CI/CD",
        desc: "Repositório Git self-hosted. Interface similar ao GitHub. Gitea Actions para CI/CD sem dependência de GitHub/GitLab.",
        type: "infra",
        links: ["Gitea Actions", "Webhook triggers", "Package registry"]
      },
      {
        name: "Ansible",
        tag: "Configuração de Infraestrutura",
        desc: "Provisionamento e configuração de servidores on-premise. Playbooks para instalação do stack completo em novos nodes. Idempotente e auditável.",
        type: "infra",
        links: ["Roles reutilizáveis", "Vault (secrets)", "AWX (UI)"]
      },
      {
        name: "Longhorn",
        tag: "Persistent Storage (K8s)",
        desc: "Storage distribuído nativo para K3s/Kubernetes. Replica volumes entre nodes on-premise. Snapshots e backup automático para MinIO.",
        type: "infra",
        links: ["PVC", "Snapshots", "Backup to MinIO"]
      },
      {
        name: "WireGuard VPN",
        tag: "Rede Segura (fazenda ↔ datacenter)",
        desc: "VPN leve para conectar app mobile dos operadores de campo e estações remotas ao datacenter central. Criptografia moderna, baixo overhead.",
        type: "security",
        links: ["wg-easy (UI)", "Tailscale (alternativa gerenciada)"]
      },
      {
        name: "pfSense / OPNsense",
        tag: "Firewall On-Premise",
        desc: "Firewall dedicado para isolar rede do AgroSaaS. IDS/IPS com Suricata. VLANs por ambiente (produção, gestão, IoT). Self-hosted e auditável.",
        type: "security",
        links: ["Suricata IDS", "HAProxy", "VLAN segmentation"]
      },
      {
        name: "Vault (HashiCorp)",
        tag: "Gerenciamento de Secrets",
        desc: "Armazenamento centralizado de secrets (DB passwords, API keys, certificados). Dynamic secrets para PostgreSQL. Audit log de todos os acessos.",
        type: "security",
        links: ["Dynamic DB creds", "PKI (certificados)", "K8s integration"]
      }
    ]
  },
  {
    id: "observability",
    icon: "📊",
    label: "OBSERVABILITY LAYER",
    subtitle: "Monitoramento, logs, rastreamento e alertas",
    color: "#0891b2",
    bg: "#ecfeff",
    border: "#a5f3fc",
    items: [
      {
        name: "Prometheus",
        tag: "Métricas",
        desc: "Coleta métricas de todos os serviços, banco, K8s e hardware. AlertManager para alertas críticos (DB down, disco cheio, API lenta).",
        type: "core",
        links: ["Node Exporter", "Postgres Exporter", "AlertManager"]
      },
      {
        name: "Grafana",
        tag: "Dashboards",
        desc: "Visualização unificada de métricas (Prometheus), logs (Loki) e traces (Tempo). Dashboards operacionais para o time de infra e SRE.",
        type: "core",
        links: ["Loki datasource", "Prometheus datasource", "Tempo datasource"]
      },
      {
        name: "Loki + Promtail",
        tag: "Logs Agregados",
        desc: "Agregação de logs de todos os containers sem indexar conteúdo (barato, rápido). Correlação com métricas Prometheus via labels compartilhados.",
        type: "core",
        links: ["LogQL", "Grafana integration", "Alerting"]
      },
      {
        name: "Tempo",
        tag: "Distributed Tracing",
        desc: "Rastreamento de requests através de múltiplos microsserviços. Identificar onde uma operação lenta ocorre (API → DB → cache → external API).",
        type: "core",
        links: ["OpenTelemetry", "Jaeger-compatible", "Grafana integration"]
      },
      {
        name: "Sentry (self-hosted)",
        tag: "Error Tracking",
        desc: "Captura de erros do frontend (Next.js) e backend (FastAPI) com stack traces completos. Source maps para erros de produção JS.",
        type: "core",
        links: ["Performance monitoring", "Release tracking", "Alertas Slack/email"]
      },
      {
        name: "Uptime Kuma",
        tag: "Status Page",
        desc: "Monitoramento de uptime de todos os serviços e APIs externas (SEFAZ, SISBOV). Página de status pública para clientes. Alertas WhatsApp/Telegram.",
        type: "infra",
        links: ["Status page", "WhatsApp alerts", "Webhook"]
      }
    ]
  },
  {
    id: "devtools",
    icon: "🛠️",
    label: "DEV TOOLING LAYER",
    subtitle: "Qualidade, testes e produtividade do time",
    color: "#7c3aed",
    bg: "#faf5ff",
    border: "#ede9fe",
    items: [
      {
        name: "pytest + pytest-asyncio",
        tag: "Testes Backend",
        desc: "Suite completa de testes para FastAPI. Fixtures por módulo, factory_boy para dados de teste, pytest-cov para cobertura.",
        type: "core",
        links: ["factory_boy", "pytest-cov", "httpx (test client)"]
      },
      {
        name: "Playwright",
        tag: "Testes E2E",
        desc: "Testes end-to-end dos fluxos críticos: login multi-tenant, criação de animal, lançamento financeiro, emissão NF-e. Headless CI.",
        type: "core",
        links: ["CI integration", "Visual regression", "Mobile viewports"]
      },
      {
        name: "Ruff + Black",
        tag: "Linting Python",
        desc: "Ruff substitui flake8 + isort + pylint com 10-100x mais velocidade. Black para formatação automática. Pre-commit hooks.",
        type: "core",
        links: ["pre-commit", "mypy (types)", "bandit (security)"]
      },
      {
        name: "ESLint + Prettier",
        tag: "Linting TypeScript",
        desc: "Regras customizadas para Next.js, React hooks e Tailwind. Formatação automática consistente em todo o frontend.",
        type: "core",
        links: ["eslint-plugin-react", "typescript-eslint", "Husky"]
      },
      {
        name: "OpenAPI + Swagger UI",
        tag: "Documentação de API",
        desc: "FastAPI gera OpenAPI automaticamente. Swagger UI disponível em /docs de cada microsserviço. Geração automática de client TypeScript.",
        type: "core",
        links: ["openapi-typescript (codegen)", "ReDoc"]
      }
    ]
  }
];

const typeColors = {
  core: { bg: "#dbeafe", text: "#1e40af", label: "Core" },
  infra: { bg: "#e0e7ff", text: "#4338ca", label: "Infra" },
  security: { bg: "#fce7f3", text: "#9d174d", label: "Segurança" },
  ai: { bg: "#fef3c7", text: "#92400e", label: "IA" },
  analytics: { bg: "#d1fae5", text: "#065f46", label: "Analytics" },
  arch: { bg: "#f3e8ff", text: "#6b21a8", label: "Arquitetura" },
  mobile: { bg: "#cffafe", text: "#155e75", label: "Mobile" },
};

const Tag = ({ type }) => {
  const c = typeColors[type] || typeColors.core;
  return (
    <span style={{
      fontSize: 9, fontWeight: 700, padding: "2px 6px", borderRadius: 4,
      background: c.bg, color: c.text, letterSpacing: 0.5
    }}>{c.label}</span>
  );
};

export default function App() {
  const [expanded, setExpanded] = useState({ client: true });
  const [selectedItem, setSelectedItem] = useState(null);

  const toggle = (id) => setExpanded(e => ({ ...e, [id]: !e[id] }));

  return (
    <div style={{ fontFamily: "'Inter', system-ui, sans-serif", background: "#0f172a", minHeight: "100vh" }}>

      {/* Header */}
      <div style={{
        background: "linear-gradient(135deg, #0f172a 0%, #1e3a5f 40%, #064e3b 100%)",
        padding: "28px 20px 20px",
        borderBottom: "1px solid rgba(255,255,255,0.08)"
      }}>
        <div style={{ maxWidth: 900, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 6 }}>
            <span style={{ fontSize: 30 }}>🌾</span>
            <div>
              <h1 style={{ color: "white", fontSize: 20, fontWeight: 900, margin: 0, letterSpacing: -0.5 }}>
                AgroSaaS — Stack Técnico Completo
              </h1>
              <p style={{ color: "#94a3b8", fontSize: 12, margin: 0, marginTop: 2 }}>
                Next.js 16 · Python / FastAPI · PostgreSQL · <span style={{ color: "#4ade80", fontWeight: 700 }}>On-Premise First</span>
              </p>
            </div>
          </div>

          {/* Badges do stack principal */}
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 14 }}>
            {[
              { label: "Next.js 16", color: "#e2e8f0", bg: "#1e293b" },
              { label: "Python 3.12", color: "#fde68a", bg: "#292524" },
              { label: "FastAPI", color: "#6ee7b7", bg: "#052e16" },
              { label: "PostgreSQL 16", color: "#bfdbfe", bg: "#1e3a5f" },
              { label: "K3s (on-premise)", color: "#c4b5fd", bg: "#2e1065" },
              { label: "Ollama (LLM local)", color: "#fca5a5", bg: "#450a0a" },
              { label: "100% Self-hosted", color: "#4ade80", bg: "#052e16" },
            ].map(b => (
              <span key={b.label} style={{
                fontSize: 11, fontWeight: 700, padding: "4px 10px", borderRadius: 6,
                background: b.bg, color: b.color, border: `1px solid ${b.color}30`
              }}>{b.label}</span>
            ))}
          </div>
        </div>
      </div>

      <div style={{ maxWidth: 900, margin: "0 auto", padding: "16px 12px 40px" }}>

        {/* Arquitetura visual simplificada */}
        <div style={{
          background: "#1e293b", borderRadius: 12, padding: "14px 16px",
          border: "1px solid #334155", marginBottom: 16
        }}>
          <div style={{ color: "#94a3b8", fontSize: 10, fontWeight: 700, letterSpacing: 1, marginBottom: 10 }}>
            FLUXO DE DADOS — ON-PREMISE
          </div>
          <div style={{
            display: "flex", alignItems: "center", flexWrap: "wrap",
            gap: 0, fontSize: 11, fontWeight: 600
          }}>
            {[
              { label: "Browser / App Mobile", color: "#0ea5e9" },
              { label: "WireGuard VPN", color: "#8b5cf6" },
              { label: "Traefik (Gateway)", color: "#8b5cf6" },
              { label: "Keycloak (Auth)", color: "#8b5cf6" },
              { label: "FastAPI Services", color: "#059669" },
              { label: "PostgreSQL + Redis", color: "#dc2626" },
              { label: "MinIO (Storage)", color: "#dc2626" },
              { label: "Ollama (IA local)", color: "#d97706" },
            ].map((item, i, arr) => (
              <span key={item.label} style={{ display: "flex", alignItems: "center" }}>
                <span style={{
                  background: item.color + "20", color: item.color,
                  padding: "4px 10px", borderRadius: 6,
                  border: `1px solid ${item.color}40`,
                  whiteSpace: "nowrap"
                }}>{item.label}</span>
                {i < arr.length - 1 && (
                  <span style={{ color: "#475569", margin: "0 4px" }}>→</span>
                )}
              </span>
            ))}
          </div>
          <div style={{ marginTop: 10, display: "flex", gap: 16, flexWrap: "wrap" }}>
            <span style={{ fontSize: 10, color: "#64748b" }}>
              📡 Observabilidade: Prometheus → Loki → Grafana → Tempo (LGTM Stack)
            </span>
            <span style={{ fontSize: 10, color: "#64748b" }}>
              🔐 Secrets: HashiCorp Vault → todos os serviços
            </span>
            <span style={{ fontSize: 10, color: "#64748b" }}>
              🚀 CI/CD: Gitea → Gitea Actions → K3s (kubectl apply)
            </span>
          </div>
        </div>

        {/* Layers */}
        {layers.map(layer => (
          <div key={layer.id} style={{ marginBottom: 10 }}>
            <div
              onClick={() => toggle(layer.id)}
              style={{
                display: "flex", justifyContent: "space-between", alignItems: "center",
                background: layer.bg,
                border: `1.5px solid ${layer.border}`,
                borderRadius: expanded[layer.id] ? "10px 10px 0 0" : 10,
                padding: "12px 16px",
                cursor: "pointer",
                userSelect: "none"
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontSize: 20 }}>{layer.icon}</span>
                <div>
                  <div style={{
                    fontWeight: 800, fontSize: 12, color: layer.color,
                    letterSpacing: 1
                  }}>{layer.label}</div>
                  <div style={{ fontSize: 11, color: "#64748b", marginTop: 1 }}>
                    {layer.subtitle}
                  </div>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{
                  fontSize: 10, fontWeight: 700, color: layer.color,
                  background: layer.color + "15", padding: "2px 8px", borderRadius: 10
                }}>
                  {layer.items.length} tecnologias
                </span>
                <span style={{ color: layer.color, fontSize: 16 }}>
                  {expanded[layer.id] ? "▲" : "▼"}
                </span>
              </div>
            </div>

            {expanded[layer.id] && (
              <div style={{
                border: `1.5px solid ${layer.border}`,
                borderTop: "none",
                borderRadius: "0 0 10px 10px",
                padding: "2px",
                background: "white"
              }}>
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
                  gap: 1,
                  background: layer.border,
                }}>
                  {layer.items.map((item, idx) => (
                    <div
                      key={idx}
                      onClick={() => setSelectedItem(selectedItem?.name === item.name ? null : item)}
                      style={{
                        background: selectedItem?.name === item.name ? layer.bg : "white",
                        padding: "12px 14px",
                        cursor: "pointer",
                        transition: "background 0.15s",
                        borderRadius: idx === 0 ? "8px 0 0 0" :
                          idx === layer.items.length - 1 ? "0 0 8px 8px" : "0"
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 4 }}>
                        <div style={{ fontWeight: 700, fontSize: 13, color: "#0f172a" }}>{item.name}</div>
                        <Tag type={item.type} />
                      </div>
                      <div style={{ fontSize: 10, color: layer.color, fontWeight: 600, marginBottom: 5 }}>
                        {item.tag}
                      </div>
                      <div style={{ fontSize: 11, color: "#4b5563", lineHeight: 1.55 }}>
                        {item.desc}
                      </div>
                      {selectedItem?.name === item.name && item.links && (
                        <div style={{ marginTop: 8, display: "flex", gap: 4, flexWrap: "wrap" }}>
                          {item.links.map((l, i) => (
                            <span key={i} style={{
                              fontSize: 9, fontWeight: 600,
                              background: layer.color + "15",
                              color: layer.color,
                              padding: "2px 7px",
                              borderRadius: 4,
                              border: `1px solid ${layer.color}30`
                            }}>🔗 {l}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Hardware mínimo recomendado */}
        <div style={{
          marginTop: 16, background: "#1e293b", borderRadius: 12,
          padding: "16px 18px", border: "1px solid #334155"
        }}>
          <div style={{ color: "#e2e8f0", fontWeight: 800, fontSize: 13, marginBottom: 12 }}>
            🖥️ Especificações de Hardware On-Premise Recomendadas
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 10 }}>
            {[
              {
                tier: "Desenvolvimento",
                spec: "1 servidor ou VM",
                cpu: "8 cores",
                ram: "32 GB",
                disk: "500 GB SSD",
                note: "Docker Compose — stack completo local",
                color: "#0ea5e9"
              },
              {
                tier: "Pequeno (até 50 tenants)",
                spec: "3 nodes K3s",
                cpu: "16 cores/node",
                ram: "64 GB/node",
                disk: "2 TB NVMe/node",
                note: "HA PostgreSQL, redundância básica",
                color: "#059669"
              },
              {
                tier: "Médio (até 500 tenants)",
                spec: "5–8 nodes K3s",
                cpu: "32 cores/node",
                ram: "128 GB/node",
                disk: "4 TB NVMe + SAN",
                note: "Patroni HA, separação DB nodes",
                color: "#d97706"
              },
              {
                tier: "Enterprise (1000+ tenants)",
                spec: "10+ nodes + GPU",
                cpu: "64 cores/node",
                ram: "256 GB/node",
                disk: "SAN/Ceph distribuído",
                note: "GPU para IA local (NVIDIA L4/A100)",
                color: "#dc2626"
              }
            ].map(h => (
              <div key={h.tier} style={{
                background: "#0f172a", borderRadius: 8,
                padding: "12px 14px",
                border: `1px solid ${h.color}40`
              }}>
                <div style={{ color: h.color, fontWeight: 800, fontSize: 11, marginBottom: 8 }}>
                  {h.tier}
                </div>
                <div style={{ color: "#94a3b8", fontSize: 10, lineHeight: 1.8 }}>
                  <div>📦 <span style={{ color: "#e2e8f0" }}>{h.spec}</span></div>
                  <div>⚡ CPU: <span style={{ color: "#e2e8f0" }}>{h.cpu}</span></div>
                  <div>🧠 RAM: <span style={{ color: "#e2e8f0" }}>{h.ram}</span></div>
                  <div>💾 Disco: <span style={{ color: "#e2e8f0" }}>{h.disk}</span></div>
                </div>
                <div style={{
                  marginTop: 8, fontSize: 9, color: h.color,
                  background: h.color + "15", padding: "3px 8px",
                  borderRadius: 4, fontWeight: 600
                }}>{h.note}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Comparativo Cloud vs On-Premise */}
        <div style={{
          marginTop: 12, background: "white", borderRadius: 12,
          padding: "16px 18px", border: "1px solid #e2e8f0"
        }}>
          <div style={{ fontWeight: 800, fontSize: 13, color: "#0f172a", marginBottom: 12 }}>
            ☁️ Estratégia Híbrida — On-Premise como Padrão, Cloud como Exceção
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            <div style={{ background: "#f0fdf4", borderRadius: 8, padding: 12, border: "1px solid #bbf7d0" }}>
              <div style={{ fontWeight: 700, color: "#15803d", fontSize: 12, marginBottom: 8 }}>
                ✅ On-Premise (padrão do produto)
              </div>
              <ul style={{ fontSize: 11, color: "#374151", lineHeight: 1.8, paddingLeft: 16, margin: 0 }}>
                <li>Dados do produtor rural ficam na propriedade/cooperativa</li>
                <li>Conformidade com LGPD sem transferência a terceiros</li>
                <li>Custo fixo previsível após CAPEX inicial</li>
                <li>Funciona com conectividade intermitente</li>
                <li>LLMs locais via Ollama — zero custo por token</li>
                <li>Soberania de dados — exigência crescente do agro BR</li>
              </ul>
            </div>
            <div style={{ background: "#fffbeb", borderRadius: 8, padding: 12, border: "1px solid #fde68a" }}>
              <div style={{ fontWeight: 700, color: "#92400e", fontSize: 12, marginBottom: 8 }}>
                ⚡ Cloud (quando faz sentido)
              </div>
              <ul style={{ fontSize: 11, color: "#374151", lineHeight: 1.8, paddingLeft: 16, margin: 0 }}>
                <li>Backup offsite para disaster recovery (S3/Backblaze B2)</li>
                <li>CDN para assets estáticos (Cloudflare gratuito)</li>
                <li>Modelo SaaS multi-tenant para cooperativas grandes</li>
                <li>Modelos de IA pesados que exigem GPU cara (fine-tuning)</li>
                <li>Burst de capacidade em períodos de safra</li>
              </ul>
            </div>
          </div>
        </div>

        <div style={{ marginTop: 12, textAlign: "center", fontSize: 10, color: "#475569" }}>
          Stack 100% open-source · Sem vendor lock-in · Portável entre bare metal, VMs e cloud · 
          Licenças: PostgreSQL, Redis, K3s, MinIO, Keycloak, Prometheus, Grafana — todas open-source / Apache 2.0 / MIT
        </div>
      </div>
    </div>
  );
}
