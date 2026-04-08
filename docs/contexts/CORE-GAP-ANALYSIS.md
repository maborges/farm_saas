---
titulo: Análise de Gap — Core Implementado vs Especificado
data_analise: 2026-04-01
analista: AgroSaaS AI Assistant
versao: 1.0
---

# Análise de Gap — Módulo Core

## Resumo Executivo

**Status Geral do Core:** ✅ **70% Implementado**

| Submódulo | Implementação | Gap | Prioridade |
|-----------|---------------|-----|------------|
| Identidade e Acesso | ✅ 90% | 10% | Baixa |
| Cadastro da Propriedade | ✅ 85% | 15% | Baixa |
| Multipropriedade | ✅ 80% | 20% | Média |
| Configurações Globais | ⚠️ 60% | 40% | Alta |
| Notificações e Alertas | ⚠️ 50% | 50% | Alta |
| Integrações Essenciais | ⚠️ 40% | 60% | Alta |
| Planos e Assinatura | ✅ 75% | 25% | Média |

---

## 1. IDENTIDADE E ACESSO

### ✅ O Que Já Existe

| Arquivo | Status | Funcionalidade |
|---------|--------|----------------|
| `core/models/auth.py` | ✅ Completo | `Usuario`, `PerfilAcesso`, `TenantUsuario`, `FazendaUsuario`, `ConviteAcesso` |
| `core/routers/auth.py` | ✅ Completo | Login, register, get-me |
| `core/services/auth_service.py` | ✅ Existe | Autenticação JWT |
| `core/dependencies.py` | ✅ Completo | `get_tenant_id`, `get_session_with_tenant`, `require_module` |
| `core/constants.py` | ✅ Completo | `Modulos` enum, `PlanTier` |

### ⚠️ Gaps Identificados

| Gap | Especificação | Implementação Atual | Prioridade |
|-----|---------------|---------------------|------------|
| **2FA/TOTP** | Obrigatório para admin/backoffice | ❌ Não implementado | Média |
| **Sessão Ativa** | Tabela `SessaoAtiva` para controle | ❌ Modelo existe em `core/models/sessao.py` mas não integrado | Baixa |
| **Log de Auditoria** | Tabela `LogAuditoria` | ❌ Modelo existe em `core/models/admin_audit_log.py` mas não integrado ao auth | Média |
| **Bloqueio por tentativas** | 5 tentativas → bloqueio 30min | ❌ Não implementado | Baixa |
| **Refresh Token** | JWT 24h + refresh 30 dias | ⚠️ Parcial (só JWT 24h) | Baixa |
| **SSO Google/Microsoft** | OAuth2 social login | ❌ Não implementado | Baixa |
| **Permissões por recurso/ação** | Tabela `Permissao` (módulo, recurso, ação) | ⚠️ `permissoes` é JSONB — não tem tabela normalizada | Média |

### 📋 Ações Recomendadas

```
PRIORIDADE MÉDIA:
1. Integrar LogAuditoria nos endpoints (middleware ou decorator)
2. Implementar 2FA TOTP para backoffice
3. Normalizar tabela Permissao (opcional — JSONB pode ser suficiente)

PRIORIDADE BAIXA:
4. Implementar refresh token
5. Implementar bloqueio por tentativas falhadas
6. Implementar SSO Google/Microsoft
```

---

## 2. CADASTRO DA PROPRIEDADE

### ✅ O Que Já Existe

| Arquivo | Status | Funcionalidade |
|---------|--------|----------------|
| `core/models/fazenda.py` | ✅ Completo | `Fazenda` com tenant_id, geometria (GeoJSON) |
| `core/routers/fazendas.py` | ✅ Existe | CRUD de fazendas |
| `core/cadastros/propriedades/` | ✅ Existe | Router + models para áreas rurais (talhões) |
| `core/services/fazenda_service.py` | ✅ Existe | Service herdando BaseService |

### ⚠️ Gaps Identificados

| Gap | Especificação | Implementação Atual | Prioridade |
|-----|---------------|---------------------|------------|
| **Hierarquia Fazenda → Talhão → Gleba** | Estrutura 3 níveis | ⚠️ Tem `Fazenda` e `areas_rurais` mas não clear se tem gleba | Baixa |
| **Geolocalização com shapefile/KML** | Upload de polígonos | ⚠️ Tem `geometria` JSONB mas não tem upload de shapefile | Média |
| **Cálculo automático de hectare útil** | Área do polígono | ❌ Não implementado | Baixa |
| **Bloqueio APP/Reserva Legal** | Sobreposição com áreas protegidas | ❌ Não implementado (é do módulo Compliance) | Baixa |
| **Infraestrutura (silos, galpões)** | Cadastro de benfeitorias | ❌ Não implementado | Baixa |

### 📋 Ações Recomendadas

```
PRIORIDADE MÉDIA:
1. Adicionar endpoint de upload de shapefile/KML
2. Implementar cálculo de área do polígono (ha)

PRIORIDADE BAIXA:
3. Adicionar modelo Gleba (se necessário)
4. Adicionar modelo InfraestruturaRural (silos, galpões, currais)
```

---

## 3. MULTIPROPRIEDADE

### ✅ O Que Já Existe

| Arquivo | Status | Funcionalidade |
|---------|--------|----------------|
| `core/models/tenant.py` | ✅ Completo | `Tenant` com `modulos_ativos`, `storage_limite_mb` |
| `core/models/grupo_fazendas.py` | ✅ Existe | Agrupamento de fazendas |
| `core/routers/grupos_fazendas.py` | ✅ Existe | CRUD de grupos |
| `FazendaUsuario.perfil_fazenda_id` | ✅ Implementado | Override de perfil por fazenda |

### ⚠️ Gaps Identificados

| Gap | Especificação | Implementação Atual | Prioridade |
|-----|---------------|---------------------|------------|
| **Isolamento de dados por propriedade** | RLS no PostgreSQL | ⚠️ `get_session_with_tenant` seta `app.current_tenant_id` mas não confirma se RLS está ativo | Alta |
| **Painel consolidado entre propriedades** | Dashboard multi-fazenda | ❌ Não implementado | Média |
| **Seletor de contexto de fazenda** | Frontend + API | ⚠️ Tem `FazendaUsuario` mas não tem endpoint para troca de contexto | Média |

### 📋 Ações Recomendadas

```
PRIORIDADE ALTA:
1. Verificar e testar RLS policies no PostgreSQL
2. Criar testes de isolamento multi-tenant

PRIORIDADE MÉDIA:
3. Implementar endpoint `/trocar-contexto` (fazenda_id → novo JWT)
4. Implementar dashboard consolidado (soma de áreas, animais, etc.)
```

---

## 4. CONFIGURAÇÕES GLOBAIS

### ✅ O Que Já Existe

| Arquivo | Status | Funcionalidade |
|---------|--------|----------------|
| `core/models/tenant_config.py` | ✅ Existe | Configurações por tenant |
| `core/cadastros/` | ✅ Existe | Cadastros de produtos, commodities, equipamentos |

### ⚠️ Gaps Identificados

| Gap | Especificação | Implementação Atual | Prioridade |
|-----|---------------|---------------------|------------|
| **Ano agrícola / safra** | Troca de contexto de safra | ⚠️ Tem `agricola/safras` mas não como configuração global | Média |
| **Unidades de medida** | Configurar hectare vs alqueire | ❌ Não implementado | Alta |
| **Moeda e fuso horário** | BRL/USD, timezone | ⚠️ Tem `idioma_padrao` no Tenant mas não timezone/moeda | Média |
| **Categorias customizáveis** | Tabelas auxiliares | ⚠️ Parcial — tem cadastros mas não customizáveis por tenant | Média |

### 📋 Ações Recomendadas

```
PRIORIDADE ALTA:
1. Criar modelo `ConfiguracoesTenant` com:
   - unidade_area: "HA" | "ALQUEIRE"
   - moeda: "BRL" | "USD"
   - timezone: "America/Sao_Paulo"
   - safra_contexto_id: UUID (safra ativa)

PRIORIDADE MÉDIA:
2. Implementar tabelas auxiliares customizáveis (ex: tipo de cultura, raças)
3. Adicionar timezone e moeda no modelo Tenant
```

---

## 5. NOTIFICAÇÕES E ALERTAS

### ✅ O Que Já Existe

| Arquivo | Status | Funcionalidade |
|---------|--------|----------------|
| `core/services/email_service.py` | ✅ Existe | Envio de e-mails |
| `core/templates/` | ✅ Existe | Templates de e-mail |

### ⚠️ Gaps Identificados

| Gap | Especificação | Implementação Atual | Prioridade |
|-----|---------------|---------------------|------------|
| **Motor de notificações** | Sistema unificado push/email/SMS | ❌ Não implementado | Alta |
| **Central de notificações in-app** | Tabela `Notificacao` com lido/não-lido | ❌ Não implementado | Alta |
| **Alertas por regra de negócio** | Vencimentos, estoques críticos, tarefas | ❌ Não implementado | Alta |
| **Firebase Cloud Messaging** | Push notifications | ❌ Não implementado | Média |
| **Twilio SMS** | SMS configurável | ❌ Não implementado | Baixa |

### 📋 Ações Recomendadas

```
PRIORIDADE ALTA:
1. Criar modelo `Notificacao`:
   - tenant_id, usuario_id, titulo, mensagem, tipo, lido, created_at

2. Criar service `NotificacaoService`:
   - enviar_push(), enviar_email(), enviar_sms()
   - marcar_lida(), listar_nao_lidas()

3. Criar router `core/routers/notificacoes.py`

4. Implementar motor de alertas (Celery task):
   - Verificar vencimentos diários
   - Verificar estoque mínimo
   - Verificar tarefas atrasadas

PRIORIDADE MÉDIA:
5. Integrar Firebase Cloud Messaging
6. Integrar Twilio SMS

PRIORIDADE BAIXA:
7. Implementar preferências de notificação por usuário
```

---

## 6. INTEGRAÇÕES ESSENCIAIS

### ✅ O Que Já Existe

| Arquivo | Status | Funcionalidade |
|---------|--------|----------------|
| `core/api_publica/` | ✅ Existe | API pública com models `ApiKey`, `ApiLog` |
| `core/routers/stripe_webhooks.py` | ✅ Existe | Webhook Stripe |
| `core/routers/webhooks_asaas.py` | ✅ Existe | Webhook Asaas |
| `integracoes/` | ✅ Existe | Sankhya, John Deere, Case IH, WhatsApp |

### ⚠️ Gaps Identificados

| Gap | Especificação | Implementação Atual | Prioridade |
|-----|---------------|---------------------|------------|
| **API REST OAuth2** | Autenticação OAuth2 para API externa | ⚠️ Tem `ApiKey` mas não OAuth2 completo | Alta |
| **Webhook engine** | Disparo de eventos para sistemas externos | ❌ Não implementado | Alta |
| **Importação/exportação CSV/XLSX** | Endpoints genéricos | ❌ Não implementado | Média |
| **Documentação Swagger pública** | OpenAPI para APIs externas | ⚠️ Tem Swagger mas não segregado por tenant | Média |

### 📋 Ações Recomendadas

```
PRIORIDADE ALTA:
1. Implementar OAuth2 flow para API pública:
   - /oauth/token
   - /oauth/authorize
   - Escopos por módulo

2. Implementar webhook engine:
   - Modelo `WebhookInscricao`: tenant_id, url, eventos (JSONB), ativo
   - Service `WebhookService`: disparar_evento(evento, payload)
   - Eventos: "safra.criada", "animal.pesado", "estoque.baixa", etc.

PRIORIDADE MÉDIA:
3. Implementar endpoints genéricos de import/export:
   - POST /import/{modelo} (CSV/XLSX → banco)
   - GET /export/{modelo} (banco → CSV/XLSX)

4. Implementar rate limiting para API pública
```

---

## 7. PLANOS E ASSINATURA

### ✅ O Que Já Existe

| Arquivo | Status | Funcionalidade |
|---------|--------|----------------|
| `core/models/billing.py` | ✅ Completo | `PlanoAssinatura`, `AssinaturaTenant`, `PlanoPricing` |
| `core/routers/billing.py` | ✅ Existe | Endpoints de billing |
| `core/routers/plan_changes.py` | ✅ Existe | Mudança de plano |
| `core/services/stripe_service.py` | ✅ Existe | Integração Stripe |
| `core/services/asaas_service.py` | ✅ Existe | Integração Asaas |
| `core/services/plan_pricing_service.py` | ✅ Existe | Cálculo de pricing |
| `core/constants.py` | ✅ Completo | `Modulos`, `PlanTier`, `ModuloMetadata` |

### ⚠️ Gaps Identificados

| Gap | Especificação | Implementação Atual | Prioridade |
|-----|---------------|---------------------|------------|
| **Feature flags por plano** | Habilita/desabilita módulos | ✅ `require_module` já implementado | — |
| **Controle de limites** | Usuários, hectares, fazendas | ⚠️ Tem no modelo mas não validado ativamente | Média |
| **Histórico de assinaturas** | Tabela `HistoricoAssinatura` | ❌ Não implementado | Baixa |
| **Upgrade/downgrade** | Fluxo completo com proration | ⚠️ Tem `plan_changes` mas não completo | Média |
| **Cancelamento** | Cancelamento com retenção | ❌ Não implementado | Baixa |
| **Trial** | 14 dias grátis automático | ⚠️ Tem `dias_trial` no modelo mas não automatizado | Média |

### 📋 Ações Recomendadas

```
PRIORIDADE MÉDIA:
1. Implementar validação ativa de limites:
   - Decorator `require_limit("max_fazendas")`
   - Validar antes de criar fazenda, usuário, etc.

2. Completar fluxo de upgrade/downgrade:
   - Proration de valores
   - Data de vigência da mudança
   - Notificação de confirmação

3. Automatizar trial:
   - Criar assinatura trial ao ativar tenant
   - Celery task diária para verificar trials expirados
   - Bloquear tenant expirado (somente leitura)

PRIORIDADE BAIXA:
4. Implementar tabela `HistoricoAssinatura`
5. Implementar fluxo de cancelamento com retenção
```

---

## 8. DEPENDÊNCIAS CRUZADAS — MÓDULOS EXTERNOS

### Módulos que Dependem do Core

| Módulo | Dependência do Core | Status |
|--------|---------------------|--------|
| **Agrícola** | `core/fazendas` (talhões), `core/cadastros` (culturas) | ✅ Implementado |
| **Pecuária** | `core/fazendas` (piquetes), `core/cadastros` (raças) | ✅ Implementado |
| **Financeiro** | `core/tenant`, `core/billing` (feature flags) | ✅ Implementado |
| **Estoque** | `core/fazendas` (almoxarifados por fazenda) | ⚠️ Verificar |
| **Frota** | `core/fazendas` (equipamentos por fazenda) | ⚠️ Verificar |
| **Compliance** | `core/fazendas` (geometria, CAR) | ⚠️ Verificar |
| **Rastreabilidade** | `core/tenant` (isolamento de dados) | ✅ Implementado |

---

## 9. TESTES DE ISOLAMENTO MULTI-TENANT

### ✅ O Que Já Existe

| Arquivo | Status |
|---------|--------|
| `conftest.py` | ✅ Existe na raiz |
| `services/api/tests/` | ✅ Pasta existe |

### ⚠️ Gaps Identificados

| Gap | Prioridade |
|-----|------------|
| **Testes de RLS** — Verificar que tenant A não vê dados de tenant B | Alta |
| **Testes de feature flags** — Tenant sem módulo não acessa endpoint | Alta |
| **Testes de limites** — Tenant atinge limite e é bloqueado | Média |
| **Testes de troca de contexto** — Usuário troca fazenda e permissões atualizam | Média |

### 📋 Ações Recomendadas

```
PRIORIDADE ALTA:
1. Criar testes em services/api/tests/core/test_tenant_isolation.py:
   - test_tenant_a_nao_ve_dados_tenant_b()
   - test_feature_gate_modulo_nao_contratado()
   - test_tenant_violation_log()

2. Criar testes em services/api/tests/core/test_rls.py:
   - test_rls_policy_insert()
   - test_rls_policy_select()
   - test_rls_bypass_superuser()
```

---

## 10. ROADMAP DE IMPLEMENTAÇÃO DO CORE

### Semana 1: Configurações + Notificações

| Dia | Tarefa | Entregável |
|-----|--------|------------|
| 1-2 | Configurações Globais | `ConfiguracoesTenant` model + endpoints |
| 3-4 | Motor de Notificações | `Notificacao` model + `NotificacaoService` |
| 5 | Central de Notificações | Endpoint `/notificacoes` (listar, marcar lida) |

### Semana 2: Integrações + Limites

| Dia | Tarefa | Entregável |
|-----|--------|------------|
| 1-2 | API OAuth2 | `/oauth/token`, `/oauth/authorize` |
| 3-4 | Webhook Engine | `WebhookInscricao` + `WebhookService` |
| 5 | Validação de Limites | Decorator `require_limit` |

### Semana 3: Testes + Refinamentos

| Dia | Tarefa | Entregável |
|-----|--------|------------|
| 1-3 | Testes de Isolamento | 10+ testes de tenant isolation |
| 4 | RLS Policies | Verificar e documentar RLS |
| 5 | Documentação Swagger | Revisar e atualizar |

---

## 11. CONCLUSÃO

### ✅ Pontos Fortes

1. **Modelagem de dados sólida** — Models bem estruturados, relacionamentos claros
2. **RBAC maduro** — `FazendaUsuario.perfil_fazenda_id` é diferencial competitivo
3. **Feature flags funcionais** — `require_module` já implementado
4. **Billing integrado** — Stripe e Asaas já conectados
5. **Constants bem organizadas** — `Modulos` enum facilita manutenção

### ⚠️ Pontos de Atenção

1. **RLS não testado** — Risco de vazamento cross-tenant
2. **Notificações inexistentes** — Impacta UX e retenção
3. **OAuth2 incompleto** — Limita integrações externas
4. **Limites não validados** — Risco de uso abusivo
5. **2FA ausente** — Risco de segurança para backoffice

### 🎯 Prioridades Imediatas

1. **Testar RLS** — Garantir isolamento multi-tenant
2. **Implementar notificações** — Essencial para engajamento
3. **Validar limites** — Proteger infraestrutura
4. **Completar OAuth2** — Habilitar integrações
5. **Implementar 2FA** — Segurança do backoffice

---

**Documento gerado em:** 2026-04-01  
**Próxima revisão:** Após implementação das prioridades  
**Responsável:** Tech Lead
