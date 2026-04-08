# Sistema de Notificações — Guia Completo

## Visão Geral

O AgroSaaS possui um **sistema de notificações em tempo real** que combina:
- **Notificações in-app** (central de notificações)
- **WebSocket** (push em tempo real)
- **Email** (notificações importantes)
- **Alertas automáticos** (baseados em regras de negócio)

---

## 📦 Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    Motor de Alertas                         │
│  (notificacoes/alertas_engine.py)                           │
│  - Vencimentos (5 dias)                                     │
│  - Estoque baixo                                            │
│  - Carência de defensivos                                   │
│  - Tarefas atrasadas                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              NotificacaoService                             │
│  (notificacoes/service.py)                                  │
│  - criar_e_push()                                           │
│  - listar()                                                 │
│  - marcar_lidas()                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   PostgreSQL    │     │  WebSocket Push │
│ (notificacoes)  │     │  (tempo real)   │
└─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │    Frontend     │
                        │  (React/Next)   │
                        └─────────────────┘
```

---

## 🗄️ Modelo de Dados

### Tabela: `notificacoes`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | Identificador único |
| `tenant_id` | UUID | Isolamento multi-tenant |
| `tipo` | String(60) | Tipo da notificação (ex: `VENCIMENTO_CONTAS_PAGAR`) |
| `titulo` | String(200) | Título da notificação |
| `mensagem` | String(1000) | Mensagem completa |
| `lida` | Boolean | Status de leitura (padrão: `false`) |
| `meta` | JSON | Metadata específica do tipo |
| `created_at` | DateTime | Data de criação (auto) |

### Exemplo de `meta` JSON:
```json
{
  "quantidade": 5,
  "total": 1500.00,
  "periodo": "5 dias",
  "itens": [
    {"id": "...", "nome": "Fazenda A", "valor": 300.00}
  ]
}
```

---

## 📡 Endpoints REST

### 1. Listar Notificações

```http
GET /api/v1/notificacoes/?lida=false&limit=50
Authorization: Bearer <token>
```

**Parâmetros:**
- `lida` (bool, opcional): Filtrar por status de leitura
- `limit` (int, default 50): Quantidade máxima

**Retorno:**
```json
[
  {
    "id": "uuid",
    "tenant_id": "uuid",
    "tipo": "VENCIMENTO_CONTAS_PAGAR",
    "titulo": "5 contas a pagar vencendo em 5 dias",
    "mensagem": "Total: R$ 1.500,00...",
    "lida": false,
    "meta": {...},
    "created_at": "2026-04-01T10:00:00Z"
  }
]
```

---

### 2. Contar Não Lidas

```http
GET /api/v1/notificacoes/nao-lidas-count
Authorization: Bearer <token>
```

**Retorno:**
```json
{"count": 12}
```

---

### 3. Marcar como Lidas

```http
POST /api/v1/notificacoes/marcar-lidas
Authorization: Bearer <token>
Content-Type: application/json

{
  "ids": ["uuid-1", "uuid-2"]  // null = marcar todas
}
```

**Retorno:**
```json
{"message": "2 notificação(ões) marcada(s) como lida(s)"}
```

---

### 4. Criar Notificação Manual

```http
POST /api/v1/notificacoes/
Authorization: Bearer <token>
Content-Type: application/json

{
  "tipo": "ALERTA_CUSTOMIZADO",
  "titulo": "Alerta importante",
  "mensagem": "Mensagem da notificação",
  "meta": {"chave": "valor"}
}
```

**Retorno:** Notificação criada + push automático via WebSocket

---

### 5. Gerar Demo (Testes)

```http
POST /api/v1/notificacoes/demo
Authorization: Bearer <token>
```

**Retorno:** 4 notificações de exemplo criadas

---

### 6. Executar Motor de Alertas (Admin)

```http
POST /api/v1/notificacoes/alertas/verificar
Authorization: Bearer <admin_token>
```

**Parâmetros:**
- `tenant_id` (UUID, opcional): Verificar apenas um tenant

**Retorno:**
```json
{
  "tenants_verificados": 50,
  "alertas_gerados": 127,
  "erros": 0
}
```

---

## 🔌 WebSocket em Tempo Real

### Conexão

```javascript
const token = getAuthToken(); // JWT do usuário
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/notificacoes/ws?token=${token}`
);
```

### Eventos Recebidos

#### 1. Inicialização
```json
{
  "tipo": "init",
  "nao_lidas": 12
}
```

#### 2. Nova Notificação (push automático)
```json
{
  "tipo": "nova_notificacao",
  "id": "uuid",
  "notificacao_tipo": "VENCIMENTO_CONTAS_PAGAR",
  "titulo": "5 contas a pagar vencendo",
  "mensagem": "Total: R$ 1.500,00...",
  "created_at": "2026-04-01T10:00:00Z"
}
```

#### 3. Contagem Atualizada
```json
{
  "tipo": "contagem_atualizada",
  "nao_lidas": 10
}
```

### Eventos Enviados (Cliente → Servidor)

#### 1. Marcar como Lidas
```javascript
ws.send(JSON.stringify({
  "action": "marcar_lidas",
  "ids": ["uuid-1", "uuid-2"]
}));
```

#### 2. Ping (keepalive)
```javascript
ws.send(JSON.stringify({
  "action": "ping"
}));
// Recebe: {"tipo": "pong"}
```

---

## 🤖 Motor de Alertas Automáticos

### Tipos de Alertas

| Tipo | Gatilho | Frequência |
|------|---------|------------|
| `VENCIMENTO_CONTAS_PAGAR` | Despesas vencendo em 5 dias | Diário |
| `VENCIMENTO_CONTAS_RECEBER` | Receitas vencendo em 5 dias | Diário |
| `ESTOQUE_BAIXO` | Quantidade < estoque_mínimo | Diário |
| `CARENCIA_DEFENSIVO` | Carência vencendo em 24-48h | Diário |
| `TAREFAS_ATRASADAS` | Operações com data vencida | Diário |

### Execução Manual

```bash
cd services/api
python -m notificacoes.alertas_engine
```

### Execução Programada (Celery Beat)

```python
# celery_beat_config.py
CELERY_BEAT_SCHEDULE = {
    "verificar-alertas-diario": {
        "task": "notificacoes.tasks.verificar_alertas",
        "schedule": crontab(hour=8, minute=0),  # Todo dia às 08:00
    },
}
```

---

## 📧 Integração com Email

### Quando Enviar Email

Nem toda notificação gera email. Use email para:
- ✅ Vencimentos críticos (> R$ 1.000)
- ✅ Bloqueios de conta
- ✅ Alertas de segurança
- ✅ Notificações fiscais

### Exemplo de Integração

```python
from core.services.email_service import EmailService
from notificacoes.service import NotificacaoService

async def notificar_vencimento_critico(tenant_id, despesa):
    # 1. Criar notificação in-app
    async with async_session_maker() as session:
        svc = NotificacaoService(session, tenant_id)
        await svc.criar_e_push(NotificacaoCreate(
            tipo="VENCIMENTO_CRITICO",
            titulo=f"Conta de R$ {despesa.valor:.2f} vence amanhã",
            mensagem=f"Vencimento: {despesa.descricao}",
            meta={"despesa_id": str(despesa.id)},
        ))

    # 2. Enviar email se valor > R$ 1.000
    if despesa.valor > 1000:
        email_service = EmailService()
        await email_service.send_invoice_due(
            email=responsavel_email,
            nome=responsavel_nome,
            valor=despesa.valor,
            vencimento=despesa.data_vencimento,
        )
```

---

## 🎯 Tipos de Notificação

### Financeiro

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `VENCIMENTO_CONTAS_PAGAR` | Despesas vencendo | "5 contas vencendo em 5 dias" |
| `VENCIMENTO_CONTAS_RECEBER` | Receitas vencendo | "3 recebimentos amanhã" |
| `PAGAMENTO_APROVADO` | Pagamento confirmado | "Mensalidade aprovada" |
| `PAGAMENTO_REJEITADO` | Pagamento rejeitado | "Comprovante rejeitado" |
| `LIMITE_ATINGIDO` | Limite do plano | "Limite de fazendas atingido" |

### Agrícola

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `CARENCIA_DEFENSIVO` | Carência vencendo | "Não colher em 24h" |
| `TAREFAS_ATRASADAS` | Operações atrasadas | "3 tarefas com 10 dias de atraso" |
| `NDVI_BAIXO` | NDVI crítico | "Talhão Norte: 0.42" |
| `PREVISAO_CHUVA` | Chuva prevista | "35mm nas próximas 24h" |
| `GELO_ALERTA` | Geada prevista | "Temperatura: -2°C" |

### Pecuária

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `VACINA_VENCENDO` | Vacinação próxima | "Aftosa em 7 dias" |
| `PESO_IDEAL_ABATE` | Lote pronto | "Lote 12: 480@" |
| `GESTACAO_ALERTAS` | Prenhez negativa | "30% retorno ao cio" |

### Operacional

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `ESTOQUE_BAIXO` | Produto abaixo mínimo | "Ureia: 2/10 toneladas" |
| `MANUTENCAO_VENCENDO` | Revisão de máquina | "Trator 05: 50h" |
| `COMBUSTIVEL_BAIXO` | Tanque baixo | "Diesel: 15%" |

---

## 🧪 Testes

### Testar Notificação Manual

```bash
curl -X POST http://localhost:8000/api/v1/notificacoes \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "TESTE",
    "titulo": "Notificação de teste",
    "mensagem": "Esta é uma notificação de teste",
    "meta": {"teste": true}
  }'
```

### Testar WebSocket

```javascript
// No browser console
const ws = new WebSocket('ws://localhost:8000/api/v1/notificacoes/ws?token=SEU_TOKEN');

ws.onmessage = (event) => {
  console.log('Mensagem recebida:', JSON.parse(event.data));
};

ws.onopen = () => {
  console.log('WebSocket conectado!');
};
```

### Testar Motor de Alertas

```bash
cd services/api
python -m notificacoes.alertas_engine
```

---

## 📊 Métricas e Monitoramento

### Queries Úteis

```sql
-- Total de notificações por tipo (últimos 7 dias)
SELECT tipo, COUNT(*) as total
FROM notificacoes
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY tipo
ORDER BY total DESC;

-- Taxa de leitura por tenant
SELECT tenant_id,
       COUNT(*) as total,
       SUM(CASE WHEN lida THEN 1 ELSE 0 END) as lidas,
       ROUND(100.0 * SUM(CASE WHEN lida THEN 1 ELSE 0 END) / COUNT(*), 2) as taxa_leitura
FROM notificacoes
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY tenant_id;

-- Notificações não lidas por tenant
SELECT tenant_id, COUNT(*) as nao_lidas
FROM notificacoes
WHERE lida = false
GROUP BY tenant_id
ORDER BY nao_lidas DESC;
```

---

## 🔒 Segurança

### Isolamento Multi-Tenant

- ✅ Todas as queries filtram por `tenant_id`
- ✅ WebSocket valida JWT e extrai `tenant_id`
- ✅ Notificações de um tenant não vazam para outro

### Permissões

| Endpoint | Permissão |
|----------|-----------|
| `GET /notificacoes/` | Tenant usuário |
| `POST /notificacoes/marcar-lidas` | Tenant usuário |
| `POST /notificacoes/` | Tenant admin |
| `POST /notificacoes/alertas/verificar` | SaaS admin |

---

## 🚀 Frontend (Exemplo React)

```typescript
// apps/web/src/components/shared/notification-bell.tsx
"use client"

import { useEffect, useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'

export function NotificationBell() {
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [naoLidas, setNaoLidas] = useState(0)

  // Buscar não lidas
  const { data } = useQuery({
    queryKey: ['notificacoes-nao-lidas'],
    queryFn: async () => {
      const res = await fetch('/api/v1/notificacoes/nao-lidas-count')
      return res.json()
    },
  })

  // WebSocket para tempo real
  useEffect(() => {
    const token = localStorage.getItem('token')
    const websocket = new WebSocket(
      `ws://localhost:8000/api/v1/notificacoes/ws?token=${token}`
    )

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.tipo === 'init') {
        setNaoLidas(data.nao_lidas)
      } else if (data.tipo === 'nova_notificacao') {
        setNaoLidas(prev => prev + 1)
        // Mostrar toast
        toast.info(data.titulo)
      } else if (data.tipo === 'contagem_atualizada') {
        setNaoLidas(data.nao_lidas)
      }
    }

    setWs(websocket)
    return () => websocket.close()
  }, [])

  return (
    <button className="relative">
      <BellIcon />
      {naoLidas > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
          {naoLidas}
        </span>
      )}
    </button>
  )
}
```

---

## 📝 Próximos Passos

### Melhorias Futuras:
1. [ ] Integração com Firebase Cloud Messaging (push mobile)
2. [ ] Integração com Twilio (SMS)
3. [ ] Preferências de notificação por usuário
4. [ ] Agendamento de notificações recorrentes
5. [ ] Templates de notificação customizáveis
6. [ ] Webhook para sistemas externos

---

**Documento gerado em:** 2026-04-01  
**Responsável:** Tech Lead  
**Status:** ✅ Implementado e funcional
