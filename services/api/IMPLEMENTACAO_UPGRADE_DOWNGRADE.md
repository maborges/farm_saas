# Implementação de Upgrade/Downgrade de Planos

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Modelos de Dados](#modelos-de-dados)
4. [Fluxos de Negócio](#fluxos-de-negócio)
5. [API Endpoints](#api-endpoints)
6. [Jobs Agendados](#jobs-agendados)
7. [Configuração](#configuração)
8. [Testes](#testes)
9. [Troubleshooting](#troubleshooting)

---

## Visão Geral

Sistema completo de gerenciamento de mudanças de plano (upgrade/downgrade) com:

- **Pricing dinâmico**: Preços progressivos por faixa de usuários
- **Upgrade imediato**: Após confirmação de pagamento via Asaas
- **Downgrade agendado**: Aplicado no próximo ciclo de cobrança
- **Aprovação manual**: Backoffice pode liberar sem pagamento (com prazo)
- **Bloqueio automático**: Sistema bloqueia inadimplentes automaticamente
- **Auditoria completa**: Histórico de todas as mudanças e bloqueios

---

## Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│                        TENANT (Frontend)                     │
│  Simular → Solicitar → [Pagar via Asaas] → Upgrade Aplicado │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                       │
│                                                               │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────┐  │
│  │ Plan Changes    │  │ Asaas Service    │  │ Pricing    │  │
│  │ Service         │──│ (Gateway)        │  │ Service    │  │
│  └─────────────────┘  └──────────────────┘  └────────────┘  │
│           │                    │                             │
│           ▼                    ▼                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Database (PostgreSQL)                    │   │
│  │  • mudancas_plano                                     │   │
│  │  • cobrancas_asaas                                    │   │
│  │  • plano_pricing                                      │   │
│  │  • historico_bloqueios                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                    ASAAS (Gateway Pagamento)                 │
│         Webhook → PAYMENT_CONFIRMED → Aplicar Upgrade        │
└─────────────────────────────────────────────────────────────┘
```

### Services

**PlanoPricingService** ([plan_pricing_service.py](services/api/core/services/plan_pricing_service.py))
- Cálculo de preços por faixa de usuários
- Validação de limites min/max por plano
- Gestão de matriz de pricing

**MudancaPlanoService** ([mudanca_plano_service.py](services/api/core/services/mudanca_plano_service.py))
- Simulação de mudanças
- Criação e aprovação de solicitações
- Aplicação de mudanças (upgrade/downgrade)
- Bloqueio por inadimplência

**AsaasService** ([asaas_service.py](services/api/core/services/asaas_service.py))
- Criação de cobranças no Asaas
- Processamento de webhooks
- Sincronização de status de pagamento

---

## Modelos de Dados

### plano_pricing

Matriz de preços progressivos por faixa de usuários.

```sql
CREATE TABLE plano_pricing (
    id UUID PRIMARY KEY,
    plano_id UUID REFERENCES planos_assinatura(id),
    faixa_inicio INTEGER NOT NULL,        -- Ex: 1, 11, 51
    faixa_fim INTEGER,                     -- Ex: 10, 50, NULL (ilimitado)
    preco_por_usuario_mensal NUMERIC(10,2),
    preco_por_usuario_anual NUMERIC(10,2),
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**Exemplo:**
```
Plano Pro:
- 1-10 users:  R$ 40/user = R$ 400/mês
- 11-30 users: R$ 35/user = R$ 1.050/mês (30 users)
- 31-50 users: R$ 30/user = R$ 1.500/mês (50 users)
```

### mudancas_plano

Histórico de solicitações de mudança de plano.

```sql
CREATE TABLE mudancas_plano (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    assinatura_id UUID REFERENCES assinaturas_tenant(id),

    -- Estado anterior e novo
    plano_origem_id UUID,
    usuarios_origem INTEGER,
    plano_destino_id UUID,
    usuarios_destino INTEGER,

    tipo_mudanca VARCHAR(30),  -- UPGRADE_PLANO, DOWNGRADE_USUARIOS, etc

    -- Financeiro
    valor_calculado NUMERIC(10,2),
    valor_proporcional NUMERIC(10,2),
    dias_restantes_ciclo INTEGER,

    -- Gateway
    cobranca_asaas_id VARCHAR(100),
    url_pagamento VARCHAR(500),

    -- Status e controle
    status VARCHAR(30),  -- pendente_pagamento, pago, aplicado, bloqueado, etc
    liberado_manualmente BOOLEAN DEFAULT FALSE,
    aprovado_por_admin_id UUID,
    data_limite_pagamento TIMESTAMP WITH TIME ZONE,

    agendado_para TIMESTAMP WITH TIME ZONE,  -- Para downgrades
    aplicado_em TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**Estados:**
- `pendente_pagamento`: Aguardando pagamento
- `liberado_manualmente`: Admin aprovou sem pagamento
- `pago`: Pagamento confirmado
- `aplicado`: Mudança efetivada
- `agendado`: Downgrade agendado para próximo ciclo
- `bloqueado`: Tenant bloqueado por inadimplência
- `cancelado`: Solicitação cancelada

### cobrancas_asaas

Registro de cobranças no gateway Asaas.

### historico_bloqueios

Auditoria de bloqueios de tenants.

---

## Fluxos de Negócio

### 1. Upgrade de Plano (Fluxo Completo)

```
┌─────────┐
│ Tenant  │
│ simula  │
│ upgrade │
└────┬────┘
     │
     ▼
┌────────────────────────────────────────┐
│ API: POST /billing/mudancas-plano/     │
│      simular                           │
│                                        │
│ Response:                              │
│ - Valor proporcional: R$ 150,00        │
│ - Dias restantes: 20                   │
│ - Módulos novos: [F1, O1]              │
└────────────┬───────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Tenant confirma upgrade                 │
│                                         │
│ API: POST /billing/mudancas-plano/      │
│      solicitar                          │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Backend:                                │
│ 1. Cria registro em mudancas_plano      │
│ 2. Cria cobrança no Asaas               │
│ 3. Retorna URL de pagamento             │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Tenant acessa URL e paga via PIX/boleto│
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Asaas → Webhook PAYMENT_CONFIRMED       │
│                                         │
│ POST /webhooks/asaas                    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Backend:                                │
│ 1. Atualiza status cobrança → CONFIRMED│
│ 2. Atualiza mudanca.status → pago      │
│ 3. Aplica mudança:                      │
│    - Atualiza assinatura.plano_id       │
│    - Atualiza assinatura.usuarios       │
│ 4. mudanca.status → aplicado            │
└─────────────────────────────────────────┘
```

### 2. Downgrade de Plano

```
┌─────────┐
│ Tenant  │
│ solicita│
│downgrade│
└────┬────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ Backend:                                │
│ 1. Cria mudancas_plano                  │
│ 2. status = "agendado"                  │
│ 3. agendado_para = data_proxima_renovacao│
│ 4. NÃO gera cobrança                    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Tenant continua com plano atual até     │
│ data de renovação                       │
└────────────┬────────────────────────────┘
             │
             ▼ (data de renovação)
┌─────────────────────────────────────────┐
│ Job diário:                             │
│ scripts/jobs/verificar_inadimplencias.py│
│                                         │
│ Aplica downgrades agendados             │
└─────────────────────────────────────────┘
```

### 3. Aprovação Manual (Backoffice)

```
┌────────────┐
│ Admin      │
│ Backoffice │
└─────┬──────┘
      │
      ▼
┌─────────────────────────────────────────┐
│ API: POST /backoffice/plan-changes/     │
│      mudancas/{id}/aprovar-manualmente  │
│                                         │
│ Body:                                   │
│ - motivo: "Cliente confiável"           │
│ - dias_tolerancia: 5                    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Backend:                                │
│ 1. mudanca.status = liberado_manualmente│
│ 2. data_limite_pagamento = hoje + 5 dias│
│ 3. Aplica mudança IMEDIATAMENTE         │
│ 4. Registra em auditoria                │
└────────────┬────────────────────────────┘
             │
             ▼ (após 5 dias sem pagamento)
┌─────────────────────────────────────────┐
│ Job diário verifica inadimplência:      │
│ 1. Bloqueia tenant                      │
│ 2. assinatura.status = BLOQUEADA        │
│ 3. Cria registro em historico_bloqueios │
└─────────────────────────────────────────┘
```

---

## API Endpoints

### Tenant (Usuários Finais)

#### `POST /api/v1/billing/mudancas-plano/simular`

Simula mudança de plano sem criar solicitação.

**Request:**
```json
{
  "plano_destino_id": "uuid",
  "usuarios_destino": 20,
  "assinatura_id": "uuid"  // Opcional
}
```

**Response:**
```json
{
  "tipo_mudanca": "UPGRADE_USUARIOS",
  "plano_atual": {
    "id": "uuid",
    "nome": "Pro",
    "modulos": ["CORE", "A1", "F1"]
  },
  "plano_novo": {
    "id": "uuid",
    "nome": "Pro",
    "modulos": ["CORE", "A1", "F1"]
  },
  "usuarios_atual": 10,
  "usuarios_novo": 20,
  "valor_atual_mensal": 400.00,
  "valor_novo_mensal": 700.00,
  "diferenca_mensal": 300.00,
  "dias_restantes_ciclo": 20,
  "valor_proporcional": 200.00,
  "data_proxima_cobranca": "2026-04-01T00:00:00Z",
  "mensagem": "Upgrade de Pro (10 users) para Pro (20 users). Você pagará R$ 200.00 proporcional aos 20 dias restantes do ciclo atual..."
}
```

#### `POST /api/v1/billing/mudancas-plano/solicitar`

Cria solicitação de mudança.

**Permissão:** `tenant:billing:manage`

**Request:**
```json
{
  "plano_destino_id": "uuid",
  "usuarios_destino": 20,
  "assinatura_id": "uuid"
}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "pendente_pagamento",
  "tipo_mudanca": "UPGRADE_USUARIOS",
  "valor_proporcional": 200.00,
  "url_pagamento": "https://www.asaas.com/b/uuid",
  "cobranca_asaas_id": "pay_123",
  "created_at": "2026-03-15T10:00:00Z"
}
```

#### `GET /api/v1/billing/mudancas-plano`

Lista histórico de mudanças do tenant.

#### `DELETE /api/v1/billing/mudancas-plano/{id}`

Cancela mudança pendente.

---

### Backoffice (Administração)

#### `POST /api/v1/backoffice/plan-changes/mudancas/{id}/aprovar-manualmente`

Aprova mudança sem pagamento.

**Permissão:** `backoffice:billing:approve`

**Request:**
```json
{
  "motivo_liberacao": "Cliente confiável com histórico de pagamento",
  "dias_tolerancia_pagamento": 5
}
```

#### `POST /api/v1/backoffice/plan-changes/pricing`

Cria faixa de pricing.

**Permissão:** `backoffice:plans:manage`

**Request:**
```json
{
  "plano_id": "uuid",
  "faixa_inicio": 1,
  "faixa_fim": 10,
  "preco_por_usuario_mensal": 40.00,
  "preco_por_usuario_anual": 400.00
}
```

#### `GET /api/v1/backoffice/plan-changes/mudancas/resumo`

Dashboard com métricas de mudanças.

---

### Webhooks

#### `POST /api/v1/webhooks/asaas`

Recebe notificações do Asaas.

**Payload (exemplo):**
```json
{
  "event": "PAYMENT_CONFIRMED",
  "payment": {
    "id": "pay_123",
    "status": "CONFIRMED",
    "value": 200.00,
    "netValue": 196.00,
    "confirmedDate": "2026-03-15"
  }
}
```

---

## Jobs Agendados

### Verificar Inadimplências

**Script:** `scripts/jobs/verificar_inadimplencias.py`

**Frequência:** Diário (3h da manhã)

**Função:**
1. Aplica mudanças agendadas (downgrades)
2. Verifica liberações manuais vencidas
3. Bloqueia tenants inadimplentes

**Cron:**
```bash
0 3 * * * cd /path/to/api && /path/to/.venv/bin/python scripts/jobs/verificar_inadimplencias.py
```

**Logs:** `logs/jobs/inadimplencias_YYYY-MM-DD.log`

---

## Configuração

### 1. Variáveis de Ambiente

Adicionar ao `.env.local`:

```bash
# Asaas (Gateway de Pagamento)
ASAAS_API_KEY=your_api_key_here
ASAAS_API_URL=https://sandbox.asaas.com/api/v3  # Sandbox
# ASAAS_API_URL=https://www.asaas.com/api/v3    # Produção
```

### 2. Seed de Dados Iniciais

```bash
cd services/api
source .venv/bin/activate

# Criar pricing para planos existentes
python scripts/seed_plan_pricing.py
```

### 3. Configurações do SaaS

As configurações são criadas automaticamente pelo seed, mas podem ser ajustadas via banco:

```sql
-- Ver configurações
SELECT * FROM farms.configuracoes_saas;

-- Ajustar dias de bloqueio
UPDATE farms.configuracoes_saas
SET valor = '{"dias": 10}'
WHERE chave = 'dias_bloqueio_inadimplencia';
```

---

## Testes

### Teste Manual (Desenvolvimento)

1. **Simular upgrade:**
```bash
curl -X POST http://localhost:8000/api/v1/billing/mudancas-plano/simular \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plano_destino_id": "uuid-do-plano-pro",
    "usuarios_destino": 20
  }'
```

2. **Solicitar upgrade:**
```bash
curl -X POST http://localhost:8000/api/v1/billing/mudancas-plano/solicitar \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plano_destino_id": "uuid-do-plano-pro",
    "usuarios_destino": 20
  }'
```

3. **Simular webhook do Asaas:**
```bash
curl -X POST http://localhost:8000/api/v1/webhooks/asaas \
  -H "Content-Type: application/json" \
  -d '{
    "event": "PAYMENT_CONFIRMED",
    "payment": {
      "id": "pay_simul_uuid-da-mudanca",
      "status": "CONFIRMED"
    }
  }'
```

### Modo Simulação

Por padrão, se `ASAAS_API_KEY` não estiver configurada, o sistema funciona em modo simulação:
- Cobranças fictícias são criadas
- Webhooks podem ser testados manualmente
- Ideal para desenvolvimento

---

## Troubleshooting

### Mudança não aplicada após pagamento

**Verificar:**
1. Webhook do Asaas foi recebido?
   ```sql
   SELECT * FROM farms.cobrancas_asaas WHERE asaas_charge_id = 'pay_xxx';
   ```

2. Status da mudança:
   ```sql
   SELECT * FROM farms.mudancas_plano WHERE id = 'uuid';
   ```

3. Logs da aplicação:
   ```bash
   grep "Mudança.*aplicada" logs/api.log
   ```

### Tenant não foi bloqueado por inadimplência

**Verificar:**
1. Job está rodando?
   ```bash
   cat logs/jobs/inadimplencias_$(date +%Y-%m-%d).log
   ```

2. Data limite está vencida?
   ```sql
   SELECT id, status, data_limite_pagamento
   FROM farms.mudancas_plano
   WHERE status = 'liberado_manualmente'
     AND data_limite_pagamento < NOW();
   ```

### Erro ao calcular pricing

**Verificar:**
1. Plano tem faixas configuradas?
   ```sql
   SELECT * FROM farms.plano_pricing WHERE plano_id = 'uuid';
   ```

2. Quantidade de usuários está dentro dos limites?
   ```sql
   SELECT limite_usuarios_minimo, limite_usuarios_maximo
   FROM farms.planos_assinatura
   WHERE id = 'uuid';
   ```

---

## Próximos Passos

- [ ] Implementar frontend (React)
- [ ] Adicionar testes unitários
- [ ] Implementar notificações (email/SMS)
- [ ] Dashboard de métricas (receita, churn, etc.)
- [ ] Relatórios financeiros
- [ ] Integração com outros gateways (Stripe, Mercado Pago)

---

## Referências

- [Documentação Asaas](https://docs.asaas.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
