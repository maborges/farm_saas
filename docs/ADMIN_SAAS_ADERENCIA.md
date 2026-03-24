# 📊 Análise de Aderência - Sistema Admin vs Aplicação Atual

## 📋 Visão Geral

Este documento analisa a aderência entre a documentação proposta para o Sistema de Administração SaaS e a implementação atual da aplicação, identificando o que já existe, o que pode ser reutilizado e o que precisa ser criado.

**Data da Análise:** 2026-03-10

---

## ✅ O QUE JÁ EXISTE NA APLICAÇÃO

### 🏗️ Infraestrutura Base

#### ✓ Backend Estruturado
```
✅ FastAPI configurado (main.py)
✅ SQLAlchemy com async
✅ Alembic para migrations
✅ Sistema de routers modular
✅ Exception handlers globais
✅ CORS configurado
✅ Loguru para logging
```

#### ✓ Modelos Relacionados ao Admin

**1. Tenant (Assinante)**
- ✅ `core/models/tenant.py` - JÁ IMPLEMENTADO
  - ✅ id, nome, documento, ativo
  - ✅ modulos_ativos (lista de módulos contratados)
  - ✅ max_usuarios_simultaneos
  - ✅ slug e dominio_customizado (white-label)
  - ✅ branding (JSON)
  - ✅ smtp_config (JSON)
  - ⚠️ **FALTAM:** storage_usado, storage_limite, data_ultimo_acesso

**2. Billing (Assinaturas e Faturas)**
- ✅ `core/models/billing.py` - PARCIALMENTE IMPLEMENTADO
  - ✅ `PlanoAssinatura` (equivalente a Pacote)
    - ✅ nome, descricao, modulos_inclusos
    - ✅ limite_usuarios, limite_hectares
    - ✅ preco_mensal, preco_anual
    - ✅ ativo
  - ✅ `AssinaturaTenant` (equivalente a Subscription)
    - ✅ tenant_id, plano_id
    - ✅ ciclo_pagamento (MENSAL/ANUAL)
    - ✅ status (PENDENTE, ATIVA, SUSPENSA, CANCELADA)
    - ✅ data_inicio, data_proxima_renovacao
  - ✅ `Fatura` (Faturas)
    - ✅ assinatura_id, tenant_id
    - ✅ valor, data_vencimento
    - ✅ status (ABERTA, EM_ANALISE, PAGA, REJEITADA)
    - ✅ url_comprovante, data_envio_comprovante
    - ✅ operador_revisao_id, justificativa_rejeicao

**3. Support (Tickets)**
- ✅ `core/models/support.py` - JÁ IMPLEMENTADO
  - ✅ `ChamadoSuporte` (equivalente a Ticket)
    - ✅ tenant_id, usuario_abertura_id
    - ✅ assunto, categoria, prioridade
    - ✅ status (ABERTO, EM_ATENDIMENTO, AGUARDANDO_CLIENTE, CONCLUIDO)
  - ✅ `MensagemChamado` (equivalente a TicketMensagem)
    - ✅ chamado_id, usuario_id
    - ✅ conteudo, anexo_url
    - ✅ is_admin_reply
  - ⚠️ **FALTAM:**
    - SLA (sla_vencimento, data_primeira_resposta)
    - Avaliação (avaliacao_nota, avaliacao_comentario)
    - Atribuição (atendente_id)

**4. Auth (Usuários)**
- ✅ `core/models/auth.py` - JÁ IMPLEMENTADO
  - ✅ `Usuario` (usuários do tenant)
  - ✅ `TenantUsuario` (relação muitos-para-muitos)
  - ⚠️ **FALTA:** Modelo separado para AdminUser

#### ✓ Routers Existentes

**1. Backoffice** ✅
- ✅ `/api/v1/backoffice` - `core/routers/backoffice.py`
  - ✅ `/bi/stats` - Métricas BI (Churn, LTV, Coortes)
  - ✅ `/dashboard/stats` - Dashboard admin (MRR, tenants)
  - ✅ `/tenants` - Listar todos os tenants
  - ✅ `/tenants/{id}` - Detalhes do tenant
  - ✅ `/tenants/{id}/impersonate` - ✅ **JÁ EXISTE!**
  - ✅ `/tenants/{id}/suspend` - Suspender tenant
  - ✅ `/tenants/{id}/reactivate` - Reativar tenant
  - ✅ `/plans` - CRUD de planos
  - ✅ `/invoices` - Listar faturas
  - ✅ `/invoices/{id}/review` - Revisar fatura
  - ✅ `/support/tickets` - Tickets (admin view)
  - ✅ `/support/tickets/{id}/assign` - Atribuir ticket
  - ✅ `/support/tickets/{id}/reply` - Responder ticket

**2. Billing** ✅
- ✅ `/api/v1/billing` - `core/routers/billing.py`
  - ✅ `/my-account` - Dados da conta (tenant)
  - ✅ `/invoices` - Listar faturas do tenant
  - ✅ `/invoices/{id}/pay` - Enviar comprovante

**3. Support** ✅
- ✅ `/api/v1/support` - `core/routers/support.py`
  - ✅ `/tickets` - CRUD de tickets (tenant side)
  - ✅ `/tickets/{id}` - Detalhes do ticket
  - ✅ `/tickets/{id}/messages` - Mensagens do ticket

**4. Configuration** ✅
- ✅ `/api/v1/configuration` - `core/routers/configuration.py`
  - Configurações de tenant

#### ✓ Dependências e Segurança

- ✅ `core/dependencies.py` - JÁ IMPLEMENTADO
  - ✅ `get_current_user` - Pega usuário logado
  - ✅ `get_current_tenant` - Pega tenant do contexto
  - ✅ `get_current_admin` - ✅ **JÁ EXISTE!**
  - ✅ `require_module` - Feature gate por módulo

---

## ⚠️ O QUE PRECISA SER AJUSTADO/EXPANDIDO

### 1. Modelo Tenant - Adicionar campos de controle

```python
# core/models/tenant.py - ADICIONAR:

# Storage
storage_usado_mb: Mapped[int] = mapped_column(default=0)
storage_limite_mb: Mapped[int] = mapped_column(default=10240)  # 10GB

# Último acesso
data_ultimo_acesso: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

# Email responsável
email_responsavel: Mapped[str] = mapped_column(String(255))
telefone_responsavel: Mapped[str | None] = mapped_column(String(20))
```

### 2. Modelo Support - Adicionar SLA e Avaliação

```python
# core/models/support.py - ADICIONAR em ChamadoSuporte:

# Atendimento
atendente_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
data_primeira_resposta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
data_resolucao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
sla_vencimento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

# Avaliação
avaliacao_nota: Mapped[int | None] = mapped_column()  # 1-5
avaliacao_comentario: Mapped[str | None] = mapped_column(Text)
avaliacao_data: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
```

### 3. Criar Modelo AdminUser Separado

```python
# core/models/admin_user.py - CRIAR NOVO:

class AdminUser(Base):
    """Usuários administrativos do SaaS (separado dos usuários dos tenants)"""
    __tablename__ = "admin_users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500))

    # Perfil: super_admin, admin, suporte, financeiro, comercial
    role: Mapped[str] = mapped_column(String(20), nullable=False, default='admin')
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_acesso: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

### 4. Renomear/Alinhar Nomenclatura

**Sugestão de Alinhamento:**

| Atual | Proposto | Ação |
|-------|----------|------|
| `PlanoAssinatura` | `Pacote` | Renomear ou criar alias |
| `AssinaturaTenant` | `Subscription` | Renomear ou criar alias |
| `ChamadoSuporte` | `Ticket` | Renomear ou criar alias |
| `MensagemChamado` | `TicketMensagem` | Renomear ou criar alias |

**Recomendação:** Manter nomes atuais em português e criar aliases/types para compatibilidade com a documentação.

---

## 🆕 O QUE PRECISA SER CRIADO DO ZERO

### 1. Modelos Novos

#### ✗ Cupons de Desconto
```python
# core/models/cupom.py - CRIAR

class Cupom(Base):
    __tablename__ = "cupons"

    id: Mapped[uuid.UUID]
    codigo: Mapped[str]  # PROMO2024
    tipo: Mapped[str]  # percentual, valor_fixo
    valor: Mapped[float]
    aplicavel_em: Mapped[str]  # primeira_mensalidade, todos_meses
    duracao_meses: Mapped[int | None]
    planos_validos: Mapped[list[uuid.UUID]]  # Array
    uso_maximo: Mapped[int]
    uso_atual: Mapped[int]
    uso_por_cliente: Mapped[int]
    data_inicio: Mapped[date]
    data_fim: Mapped[date]
    ativo: Mapped[bool]
    created_at: Mapped[datetime]
```

#### ✗ Templates de Email
```python
# core/models/email_template.py - CRIAR

class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id: Mapped[uuid.UUID]
    codigo: Mapped[str]  # WELCOME, TRIAL_ENDING
    nome: Mapped[str]
    assunto: Mapped[str]
    corpo_html: Mapped[str]
    corpo_texto: Mapped[str]
    variaveis: Mapped[list[str]]  # ['nome_usuario', 'tenant_nome']
    tipo: Mapped[str]  # transacional, marketing, sistema
    ativo: Mapped[bool]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

#### ✗ Log de Emails
```python
# core/models/email_log.py - CRIAR

class EmailLog(Base):
    __tablename__ = "email_logs"

    id: Mapped[uuid.UUID]
    template_id: Mapped[uuid.UUID | None]
    destinatario_email: Mapped[str]
    destinatario_nome: Mapped[str | None]
    tenant_id: Mapped[uuid.UUID | None]
    assunto: Mapped[str]
    corpo_html: Mapped[str | None]
    status: Mapped[str]  # enviado, falha, pendente
    erro_mensagem: Mapped[str | None]
    provider: Mapped[str | None]
    aberto: Mapped[bool]
    clicado: Mapped[bool]
    enviado_em: Mapped[datetime]
```

#### ✗ Módulos do Sistema
```python
# core/models/modulo_sistema.py - CRIAR

class ModuloSistema(Base):
    __tablename__ = "modulos_sistema"

    id: Mapped[uuid.UUID]
    codigo: Mapped[str]  # A1_PLANEJAMENTO
    nome: Mapped[str]
    descricao: Mapped[str | None]
    icone: Mapped[str | None]
    dominio: Mapped[str]  # agricola, pecuaria, financeiro
    modulo_pai_codigo: Mapped[str | None]
    comercializavel: Mapped[bool]
    preco_adicional: Mapped[float]
    requer_modulos: Mapped[list[str]]  # Array
    ativo: Mapped[bool]
    em_desenvolvimento: Mapped[bool]
    ordem: Mapped[int]
    created_at: Mapped[datetime]
```

#### ✗ Audit Log para Admin
```python
# core/models/admin_audit_log.py - CRIAR

class AdminAuditLog(Base):
    __tablename__ = "admin_audit_log"

    id: Mapped[uuid.UUID]
    admin_user_id: Mapped[uuid.UUID]
    admin_email: Mapped[str]
    acao: Mapped[str]  # tenant.impersonate, subscription.suspend
    entidade: Mapped[str]  # tenant, subscription, ticket
    entidade_id: Mapped[uuid.UUID | None]
    descricao: Mapped[str | None]
    dados_anteriores: Mapped[dict | None]  # JSONB
    dados_novos: Mapped[dict | None]  # JSONB
    ip_address: Mapped[str | None]
    user_agent: Mapped[str | None]
    created_at: Mapped[datetime]
```

#### ✗ Configurações do Sistema
```python
# core/models/configuracao.py - CRIAR (ou expandir Configuration existente)

class ConfiguracaoSistema(Base):
    __tablename__ = "configuracoes_sistema"

    id: Mapped[uuid.UUID]
    chave: Mapped[str]  # stripe.secret_key
    valor: Mapped[str | None]
    valor_json: Mapped[dict | None]  # JSONB
    categoria: Mapped[str]  # stripe, smtp, storage
    tipo: Mapped[str]  # string, number, boolean, json, secret
    descricao: Mapped[str | None]
    is_secret: Mapped[bool]
    is_encrypted: Mapped[bool]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

### 2. Routers Novos/Expandir Existentes

#### ✅ Backoffice Router - JÁ TEM BASE, EXPANDIR:

**O que já existe:**
- ✅ Dashboard stats
- ✅ BI stats
- ✅ Impersonate
- ✅ Suspend/Reactivate
- ✅ CRUD de planos
- ✅ Review de faturas
- ✅ Tickets (admin side)

**O que precisa adicionar:**
- ✗ Reset de senha de assinante
- ✗ Alterar plano de assinante
- ✗ Histórico de ações (audit log)

#### ✗ Router de Cupons - CRIAR NOVO
```python
# core/routers/cupons.py - CRIAR

@router.post("/cupons")  # Criar cupom
@router.get("/cupons")  # Listar cupons
@router.get("/cupons/{id}")  # Detalhes
@router.put("/cupons/{id}")  # Atualizar
@router.delete("/cupons/{id}")  # Desativar
@router.get("/cupons/{codigo}/validate")  # Validar cupom
```

#### ✗ Router de Email Templates - CRIAR NOVO
```python
# core/routers/email_templates.py - CRIAR

@router.get("/email-templates")  # Listar templates
@router.get("/email-templates/{id}")  # Detalhes
@router.post("/email-templates")  # Criar
@router.put("/email-templates/{id}")  # Atualizar
@router.post("/email-templates/{id}/test")  # Enviar teste
@router.get("/email-templates/{id}/preview")  # Preview
@router.get("/email-logs")  # Histórico de envios
```

#### ✗ Router de Módulos - CRIAR NOVO
```python
# core/routers/modulos.py - CRIAR

@router.get("/modulos")  # Listar módulos
@router.get("/modulos/{codigo}")  # Detalhes
@router.put("/modulos/{codigo}")  # Atualizar (preço, status)
```

### 3. Services Novos

#### ✗ Email Service - Expandir
```python
# core/services/email_service.py - JÁ EXISTE, EXPANDIR

# Adicionar:
- render_template(template_codigo, context)
- send_from_template(template_codigo, to, context)
- log_email(email_data)
- track_open(email_id)
- track_click(email_id, link)
```

#### ✗ SLA Service - CRIAR
```python
# core/services/sla_service.py - CRIAR

- calcular_sla_vencimento(prioridade, data_abertura)
- verificar_sla_vencido(ticket)
- get_tickets_proximo_vencimento(horas)
- get_metricas_sla()
```

#### ✗ Storage Service - CRIAR
```python
# core/services/storage_service.py - CRIAR

- upload_file(file, path)
- delete_file(path)
- get_tenant_storage_usage(tenant_id)
- update_tenant_storage(tenant_id)
```

---

## 🎯 MAPA DE ADERÊNCIA

### Dashboard Admin

| Funcionalidade | Status | Comentário |
|----------------|--------|------------|
| Métricas básicas (MRR, Tenants) | ✅ Existe | `/backoffice/dashboard/stats` |
| Métricas BI (Churn, LTV) | ✅ Existe | `/backoffice/bi/stats` |
| Gráfico novos assinantes | ⚠️ Mocado | Precisa implementar query real |
| Alertas críticos | ✗ Falta | Criar endpoint e lógica |
| KPIs de suporte | ⚠️ Parcial | Existe contagem, falta SLA |

### Gestão de Assinantes

| Funcionalidade | Status | Comentário |
|----------------|--------|------------|
| Listar assinantes | ✅ Existe | `/backoffice/tenants` |
| Detalhes do assinante | ✅ Existe | `/backoffice/tenants/{id}` |
| Impersonate | ✅ Existe | `/backoffice/tenants/{id}/impersonate` |
| Suspender/Reativar | ✅ Existe | `/backoffice/tenants/{id}/suspend` |
| Reset de senha | ✗ Falta | Criar endpoint |
| Alterar plano | ✗ Falta | Criar endpoint |
| Filtros avançados | ⚠️ Básico | Expandir query params |

### Assinaturas

| Funcionalidade | Status | Comentário |
|----------------|--------|------------|
| Listagem | ✅ Existe | Já lista assinaturas |
| Aprovar/Rejeitar | ✅ Existe | Review de faturas |
| Suspender | ✅ Existe | Via tenant |
| Workflow completo | ⚠️ Parcial | Falta auto-criação tenant |

### Suporte (Tickets)

| Funcionalidade | Status | Comentário |
|----------------|--------|------------|
| CRUD de tickets | ✅ Existe | `/support/tickets` e `/backoffice/support/tickets` |
| Mensagens | ✅ Existe | Sistema de mensagens ok |
| Atribuir ticket | ✅ Existe | `/backoffice/support/tickets/{id}/assign` |
| Responder | ✅ Existe | `/backoffice/support/tickets/{id}/reply` |
| SLA | ✗ Falta | Adicionar campos e lógica |
| Avaliação | ✗ Falta | Adicionar campos |
| Métricas | ⚠️ Parcial | Contagem básica existe |

### Pacotes Comerciais

| Funcionalidade | Status | Comentário |
|----------------|--------|------------|
| CRUD de pacotes | ✅ Existe | `/backoffice/plans` |
| Módulos incluídos | ✅ Existe | `modulos_inclusos` em PlanoAssinatura |
| Trial configurável | ⚠️ Parcial | Não tem campos dias_trial, tem_trial |
| Limites customizados | ✅ Existe | JSON em limite_hectares |

### Cupons

| Funcionalidade | Status | Comentário |
|----------------|--------|------------|
| CRUD de cupons | ✗ Falta | Criar modelo e router |
| Validação | ✗ Falta | Criar lógica |
| Controle de uso | ✗ Falta | Criar controle |

### Financeiro

| Funcionalidade | Status | Comentário |
|----------------|--------|------------|
| Transferências | ✅ Existe | Via upload de comprovante |
| Conciliação | ✅ Existe | Review de faturas |
| MRR | ✅ Existe | Calculado em dashboard |
| Churn | ✅ Existe | Calculado em BI stats |
| Relatórios | ⚠️ Básico | Expandir |

### Email

| Funcionalidade | Status | Comentário |
|----------------|--------|------------|
| Templates | ✗ Falta | Criar modelo e CRUD |
| Envio | ⚠️ Básico | email_service existe mas simples |
| Variáveis dinâmicas | ✗ Falta | Criar render engine |
| Histórico | ✗ Falta | Criar log |
| Tracking | ✗ Falta | Criar sistema |

### Módulos

| Funcionalidade | Status | Comentário |
|----------------|--------|------------|
| Catálogo | ✗ Falta | Criar modelo ModuloSistema |
| Gestão | ✗ Falta | Criar CRUD |
| Ativar/Desativar comercialização | ✗ Falta | Criar lógica |

### Configurações

| Funcionalidade | Status | Comentário |
|----------------|--------|------------|
| Storage config | ⚠️ Parcial | Tem Configuration, expandir |
| SMTP config | ⚠️ Parcial | Tem smtp_config em Tenant |
| Stripe config | ✗ Falta | Criar |
| Push config | ✗ Falta | Criar |
| Configurações gerais | ⚠️ Parcial | Tem Configuration, expandir |

---

## 📈 Resumo de Aderência

### Backend

```
✅ Implementado Completo:      35%
⚠️  Implementado Parcial:      40%
✗ Não Implementado:           25%
```

**Detalhamento:**

| Categoria | Aderência | Prioridade |
|-----------|-----------|------------|
| Modelos Base (Tenant, Billing, Support) | 80% ✅ | - |
| Routers Admin (Backoffice) | 70% ⚠️ | Alta |
| Sistema de Tickets | 60% ⚠️ | Média |
| Dashboard e Métricas | 75% ⚠️ | Alta |
| Cupons | 0% ✗ | Média |
| Email Templates | 20% ✗ | Baixa |
| Módulos Sistema | 0% ✗ | Baixa |
| Configurações | 40% ⚠️ | Média |

---

## 🚀 Plano de Ação Recomendado

### Fase 1: Ajustes nos Modelos Existentes (1-2 dias)
1. ✅ Adicionar campos em `Tenant` (storage, último acesso)
2. ✅ Adicionar campos em `ChamadoSuporte` (SLA, avaliação, atendente)
3. ✅ Criar modelo `AdminUser` separado
4. ✅ Criar migration

### Fase 2: Expandir Backoffice Router (2-3 dias)
1. ✅ Adicionar endpoint reset senha
2. ✅ Adicionar endpoint alterar plano
3. ✅ Melhorar filtros de listagem
4. ✅ Adicionar endpoints de métricas faltantes

### Fase 3: Sistema de SLA e Avaliação (2 dias)
1. ✅ Criar `SLAService`
2. ✅ Implementar cálculo automático
3. ✅ Adicionar endpoints de avaliação
4. ✅ Criar métricas de SLA

### Fase 4: Cupons (2-3 dias)
1. ✅ Criar modelo `Cupom`
2. ✅ Criar router completo
3. ✅ Implementar validação
4. ✅ Integrar com billing

### Fase 5: Email Templates (3-4 dias)
1. ✅ Criar modelos `EmailTemplate` e `EmailLog`
2. ✅ Expandir `EmailService`
3. ✅ Criar render engine (Jinja2)
4. ✅ Criar CRUD de templates
5. ✅ Implementar tracking

### Fase 6: Módulos e Configurações (2-3 dias)
1. ✅ Criar modelo `ModuloSistema`
2. ✅ Seed inicial de módulos
3. ✅ Expandir `ConfiguracaoSistema`
4. ✅ Criar interface de config

### Fase 7: Frontend Admin (5-7 dias)
1. ✅ Criar layout admin
2. ✅ Implementar dashboard
3. ✅ Páginas de gestão
4. ✅ Integração com APIs

---

## 💡 Recomendações

### 1. Aproveitar o que Existe
O sistema já tem uma **base sólida** no `backoffice.py`. Recomendo:
- ✅ Manter e expandir o router existente
- ✅ Adicionar novos endpoints no mesmo padrão
- ✅ Usar os modelos existentes como base

### 2. Nomenclatura
Recomendo **manter a nomenclatura atual em português** para consistência:
- `PlanoAssinatura` ao invés de `Pacote`
- `ChamadoSuporte` ao invés de `Ticket`
- Criar aliases/exports se necessário para a doc

### 3. Estrutura Modular
A aplicação já segue estrutura modular (agricola, pecuaria, financeiro, operacional). O admin deve seguir o mesmo padrão:
```
core/
├── routers/
│   ├── backoffice/  # Reorganizar em módulos
│   │   ├── dashboard.py
│   │   ├── assinantes.py
│   │   ├── billing.py
│   │   ├── suporte.py
│   │   ├── cupons.py
│   │   └── emails.py
```

### 4. Reutilização
- ✅ O sistema de dependências (`get_current_admin`) já existe
- ✅ O sistema de feature gates (`require_module`) já existe
- ✅ A estrutura de exceptions já está madura

### 5. Frontend
O frontend pode ser:
- **Opção 1:** Integrado no monorepo existente (`apps/web`) como rota separada
- **Opção 2:** Aplicação Next.js separada para total isolamento
- **Recomendação:** Opção 1 para aproveitar componentes existentes

---

## 📊 Conclusão

A aplicação atual já possui **aproximadamente 60-70% da infraestrutura necessária** para o sistema admin proposto. Os principais gaps são:

**Alta Prioridade:**
1. Sistema de SLA para tickets
2. Reset de senha de assinantes
3. Expandir métricas do dashboard

**Média Prioridade:**
1. Sistema de cupons
2. Email templates
3. Melhorar relatórios financeiros

**Baixa Prioridade:**
1. Catálogo de módulos (pode usar constants.py)
2. Tracking de emails
3. Configurações avançadas

**Tempo Estimado Total:** 20-25 dias de desenvolvimento (1 dev full-time)

---

**Última atualização:** 2026-03-10
**Versão:** 1.0
**Responsável:** Análise Técnica AgroSaaS
