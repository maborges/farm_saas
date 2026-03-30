# Brainstorming — CRM: Processo pós-conversão de lead

**Data:** 2026-03-28
**Status:** Em andamento

---

## 1. Controle de comercialização de planos

### Problema
`PlanoAssinatura` tem apenas `ativo: bool` — sem distinção entre canal de venda.

### Solução aprovada
Adicionar dois campos independentes ao modelo `PlanoAssinatura`:

```python
ativo: Mapped[bool]          # controle geral (desativado = oculto em tudo)
disponivel_site: Mapped[bool] = False   # aparece no checkout/landing público
disponivel_crm: Mapped[bool] = True    # aparece nas opções do CRM
```

**Matriz de visibilidade:**

| ativo | disponivel_site | disponivel_crm | Resultado |
|-------|----------------|----------------|-----------|
| False | qualquer | qualquer | Oculto em tudo |
| True | True | True | Público + CRM |
| True | False | True | Só CRM (campanhas/personalizados) |
| True | True | False | Só site |
| True | False | False | Rascunho interno |

### Migration
- Adicionar `disponivel_site` e `disponivel_crm` em `planos_assinatura`
- Dados existentes com `ativo=True` → `disponivel_crm=True`, `disponivel_site` definido manualmente

---

## 2. Fluxo de conversão de lead (definição em andamento)

### Fluxo macro aprovado

1. Lead marcado como **aprovado** no CRM pelo comercial
2. Backoffice admin executa **wizard de conversão** com:
   - Seleção do plano (`disponivel_crm=True`)
   - Criação do Tenant
   - Criação da AssinaturaTenant (com plano acordado)
   - Definição do usuário como **administrador**
   - Criação da(s) Fazenda(s)
3. Sistema envia **email de ativação** ao lead
4. Lead acessa link, confirma/complementa dados pré-preenchidos pelo CRM
5. Status muda para **convertido** apenas após verificação pelo assinante

### Dados pré-preenchidos pelo CRM → a definir
*(próximo passo do brainstorming)*

---

## 3. Integração Stripe

- Gateway: Stripe (cartão de crédito, fase inicial)
- Integração do zero (não existe no projeto)
- Fluxo: Stripe Checkout Session → webhook `payment_intent.succeeded`
- A assinatura só fica `ATIVA` após confirmação do webhook
- Lançamento em contas_a_receber gerado no momento da criação da assinatura (status: PENDENTE)
- Baixa automática via webhook

---

## 4. Fluxo completo consolidado

```
[CRM] Lead aprovado pelo comercial
     ↓
[BACKOFFICE] Wizard de conversão (admin)
  1. Confirma dados do lead (pré-preenchidos do CRM)
  2. Seleciona plano (disponivel_crm=True)
  3. Define fazenda(s) e nomes
  4. Confirma → sistema cria:
     • Tenant (status: PENDENTE)
     • AssinaturaTenant (status: PENDENTE_PAGAMENTO)
     • Usuário admin (senha temporária)
     • Fazenda(s)
     • Lançamento em contas_a_receber
     • Lead.tenant_convertido_id = tenant.id
     ↓
[SISTEMA] Envia email de ativação com link único
     ↓
[ASSINANTE] Acessa link → tela de onboarding
  • Confirma/corrige dados pessoais e empresa
  • Define senha definitiva
  • Insere cartão de crédito → Stripe Checkout
     ↓
[STRIPE] Webhook payment_intent.succeeded
  • AssinaturaTenant.status → ATIVA
  • Tenant.status → ATIVO
  • Baixa no contas_a_receber
  • Lead.status → "convertido"
  • Lead.data_conversao = hoje
```

---

## Arquivos a criar/modificar

### Backend
| Arquivo | Ação |
|---|---|
| `core/models/billing.py` | Adicionar `disponivel_site`, `disponivel_crm`; status `PENDENTE_PAGAMENTO` |
| `core/routers/backoffice_tenants.py` | Endpoint wizard de conversão |
| `core/stripe_service.py` | **Novo** — integração Stripe (checkout session, webhook) |
| `core/routers/stripe_webhooks.py` | **Novo** — handler eventos Stripe |
| `core/routers/onboarding.py` | **Novo** — endpoints públicos de ativação do assinante |
| `financeiro/models.py` | Verificar/ajustar model de contas_a_receber |
| Migration Alembic | `disponivel_site`, `disponivel_crm` em `planos_assinatura` |

### Frontend
| Tela | Ação |
|---|---|
| Backoffice — planos | Substituir toggle único por dois toggles (site / CRM) |
| Backoffice — wizard conversão de lead | **Novo** — 3 passos: dados, plano, fazendas |
| Onboarding do assinante | **Nova** — confirmação de dados + Stripe Elements |
