# Implementação: Nova Conta de Produtor

**Data:** 2026-04-08  
**Status:** ✅ Backend completo | 🟡 Frontend já está correto | 📋 Testes criados

---

## 📋 Resumo das Mudanças

### Backend

#### 1. **Atualizar `AuthService.create_tenant_for_user()`**
**Arquivo:** `services/api/core/services/auth_service.py`

**Mudanças:**
- ✅ Import `Fatura` do billing models
- ✅ Atualizar lógica de status:
  - `status = "TRIAL"` (antes: "PENDENTE_PAGAMENTO") se plano pago com trial
  - `status = "ATIVA"` se plano grátis
- ✅ Calcular `data_proxima_renovacao = agora + dias_trial`
- ✅ Calcular `data_primeiro_vencimento = trial_expira + 1 dia`
- ✅ **Criar `Fatura` automática:**
  - Apenas se `is_free == False` E `tem_trial == True`
  - Valor = `plano.preco_anual` (se ANUAL) ou `plano.preco_mensal` (se MENSAL)
  - `data_vencimento = data_primeiro_vencimento`
  - `status = "ABERTA"`
- ✅ **Enviar email de trial (async, não bloqueia):**
  - Método: `email_service.send_trial_notice()`
  - Informações: nome, dias trial, data vencimento

#### 2. **Atualizar `EmailService`**
**Arquivo:** `services/api/core/services/email_service.py`

**Novo método:**
```python
async def send_trial_notice(
    self, 
    email: str, 
    nome: str, 
    nome_produtor: str, 
    nome_plano: str, 
    dias_trial: int, 
    data_vencimento, 
    tenant_id: uuid.UUID = None
)
```

#### 3. **Criar Template de Email**
**Arquivo:** `services/api/core/templates/emails/trial_notice.html`

Template informando:
- Período de trial (15 dias)
- Data de cobrança automática
- Call-to-action para dashboard
- Aviso sobre cancelamento

#### 4. **Criar Testes**
**Arquivo:** `services/api/tests/test_create_subscription.py`

**Testes:**
- ✅ `test_create_tenant_for_user_trial_pago`: Valida trial + fatura
- ✅ `test_create_tenant_for_user_plan_gratis`: Valida plano grátis (sem fatura)
- ✅ `test_create_tenant_isolacao_multitenancy`: Valida isolamento de tenant

---

### Frontend

#### Status: ✅ Já Correto
**Arquivo:** `apps/web/src/components/auth/new-subscription-wizard.tsx`

O wizard **já coleta dados do Produtor** (não Grupo):
- Step 1: Nome Produtor + CNPJ/CPF (opcional)
- Step 2: Seleção de Plano + Ciclo
- Step 3: Confirmação

Nenhuma mudança necessária no frontend.

---

## 🔍 Conceito: GrupoFazendas Invisível

Para compatibilidade com código atual (zero breaking changes):
1. **Ao criar novo Tenant:** cria automaticamente 1 `GrupoFazendas` **invisível** (não mostrado no UI)
2. **Assinatura vinculada ao grupo invisível**
3. **JWT continua funcionando igual**

Futuro: Remover Grupo de forma controlada em refactor separada.

---

## 🧪 Checklist de Validação

Após deploy:

- [ ] Criar nova assinatura com plano PAGO
  - [ ] Status = "TRIAL"
  - [ ] Fatura criada com vencimento correto
  - [ ] Email recebido
  - [ ] Acesso ao dashboard liberado

- [ ] Criar nova assinatura com plano GRÁTIS
  - [ ] Status = "ATIVA"
  - [ ] Sem fatura
  - [ ] Acesso imediato

- [ ] Verificar isolamento
  - [ ] Tenants não veem dados uns dos outros
  - [ ] Faturas estão corretas por tenant

---

## 📊 Arquivos Modificados

```
Backend:
  ✏️ core/services/auth_service.py (método create_tenant_for_user)
  ✏️ core/services/email_service.py (novo método send_trial_notice)
  ✨ core/templates/emails/trial_notice.html (novo template)
  ✨ tests/test_create_subscription.py (novos testes)

Frontend:
  ✅ Nenhuma mudança necessária
```

---

## 🚀 Próximos Passos

1. **Deploy backend** com as mudanças
2. **Executar testes** para validar
3. **Testar manualmente** na plataforma
4. **Monitorar emails** no servidor SMTP
5. **Validar faturas** no banco de dados

---

## 📝 Notas

- Trial de **15 dias** é parametrizado em `PlanoAssinatura.dias_trial`
- Email é **assíncrono** (não bloqueia a criação)
- Fatura é criada com status **"ABERTA"** (aguarda pagamento/aprovação)
- Assinatura com status **"TRIAL"** passa em validações de billing (já atualizado em `dependencies.py`)
