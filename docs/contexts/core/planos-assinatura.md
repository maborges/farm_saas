---
modulo: Core
submodulo: Planos e Assinatura
nivel: core
core: true
dependencias_core:
  - Identidade e Acesso
  - Multipropriedade e Multitenant
dependencias_modulos: []
standalone: false
complexidade: L
assinante_alvo: todos os assinantes
---

# Planos e Assinatura

## Descrição Funcional

Submódulo responsável por todo o ciclo de vida de assinaturas da plataforma: definição de planos com módulos e limites, feature flags por plano, gestão de upgrades/downgrades, trial, cancelamento, cupons de desconto e integração com gateways de pagamento (Stripe para cartão internacional e Asaas para boleto/PIX no mercado brasileiro). Determina quais módulos e níveis cada tenant pode acessar em tempo real.

## Personas — Quem usa este submódulo

- **Owner do Tenant:** Visualiza plano atual, faz upgrade/downgrade, gerencia método de pagamento, consulta histórico de faturas.
- **Administrador Backoffice:** Cria e edita planos, gerencia cupons, monitora métricas de receita (MRR, churn, conversão de trial), ajusta limites manualmente.
- **Sistema (runtime):** Avalia feature flags em cada request via `require_module()` para habilitar/desabilitar funcionalidades conforme plano contratado.

## Dores que resolve

1. **Acesso indevido a funcionalidades não contratadas:** Sem feature flags, qualquer tenant poderia acessar módulos Enterprise sem pagar.
2. **Cobrança manual e desorganizada:** Sem integração com gateway, controle de pagamentos é feito em planilhas.
3. **Dificuldade em experimentar antes de pagar:** Sem trial, produtores hesitam em contratar sem testar.
4. **Perda de receita por churn silencioso:** Sem métricas de assinatura, cancelamentos passam despercebidos.
5. **Inflexibilidade de planos:** Sem upgrade/downgrade self-service, mudanças de plano dependem de suporte manual.

## Regras de Negócio

1. **RN-PA-001:** Cada Tenant possui exatamente 1 assinatura ativa por vez.
2. **RN-PA-002:** O plano define: módulos habilitados (com nível máximo), limites operacionais (fazendas, usuários, hectares, armazenamento).
3. **RN-PA-003:** `require_module()` consulta feature flags em runtime — módulo não contratado retorna HTTP 402 (`ModuleNotContractedError`).
4. **RN-PA-004:** Upgrade é imediato — diferença de valor cobrada pro-rata no ciclo atual.
5. **RN-PA-005:** Downgrade é agendado para o início do próximo ciclo de billing (sem reembolso).
6. **RN-PA-006:** Trial padrão: 14 dias com acesso a todos os módulos nível Enterprise.
7. **RN-PA-007:** Após trial sem conversão: downgrade automático para plano gratuito (Core only).
8. **RN-PA-008:** Falha de pagamento: grace period de 7 dias → suspensão de acesso (read-only) → após 30 dias, arquivamento.
9. **RN-PA-009:** Cancelamento: acesso mantido até o fim do ciclo pago. Dados preservados por 90 dias.
10. **RN-PA-010:** Cupons possuem: código único, tipo (percentual/valor fixo), validade, limite de usos, restrição por plano.
11. **RN-PA-011:** Stripe é gateway primário (cartão). Asaas é gateway secundário (boleto/PIX — mercado BR).
12. **RN-PA-012:** Webhooks de pagamento são idempotentes via `gateway_payment_id` (previne duplicação).

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `Plano` | id, nome, slug, modulos_json, limites_json, preco_mensal, preco_anual, ativo, ordem_display | → Assinatura[], → FeatureFlag[] |
| `Assinatura` | id, tenant_id, plano_id, status (trial/ativa/suspensa/cancelada), inicio, fim, trial_fim, gateway, gateway_subscription_id | → Tenant, → Plano, → Pagamento[] |
| `Pagamento` | id, assinatura_id, valor, status (pendente/pago/falha), gateway, gateway_payment_id, metodo, pago_em | → Assinatura |
| `Cupom` | id, codigo, tipo_desconto (percentual/fixo), valor_desconto, validade, usos_restantes, planos_permitidos[] | → Assinatura[] |
| `PlanoMudanca` | id, tenant_id, plano_anterior_id, plano_novo_id, tipo (upgrade/downgrade), efetivo_em, motivo | → Tenant, → Plano |
| `FeatureFlag` | plano_id, modulo, nivel_maximo (essencial/profissional/enterprise), habilitado | → Plano |

## Integrações Necessárias

- **Stripe:** Subscriptions API, Checkout Sessions, Customer Portal, Webhooks (payment_intent.succeeded, customer.subscription.updated/deleted).
- **Asaas:** Assinaturas, emissão de boleto, PIX QR code, webhooks de confirmação.
- **Core `require_module()`:** Avaliação de feature flags em cada request protegido.
- **Frontend:** Página de planos comparativos, fluxo de upgrade, portal de billing.
- **Backoffice:** CRUD de planos e cupons, dashboard de MRR/churn/trial conversion.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Assinatura inicial (pós-trial)
1. Trial de 14 dias expira → sistema exibe banner "Seu trial terminou".
2. Owner acessa "Planos" → vê comparativo com módulos e limites por plano.
3. Seleciona plano desejado → escolhe ciclo (mensal/anual com desconto).
4. Opcionalmente aplica código de cupom.
5. Redirecionado para checkout Stripe (cartão) ou Asaas (boleto/PIX).
6. Pagamento confirmado via webhook → feature flags atualizados → módulos desbloqueados.

### Fluxo 2: Upgrade self-service
1. Owner acessa "Minha Assinatura" → "Alterar Plano".
2. Vê planos superiores com destaque nas funcionalidades adicionais.
3. Seleciona novo plano → sistema calcula valor pro-rata restante do ciclo.
4. Confirma pagamento → upgrade aplicado imediatamente.
5. Feature flags atualizados → novos módulos disponíveis.

### Fluxo 3: Webhook de pagamento
1. Gateway (Stripe/Asaas) envia webhook com evento de pagamento.
2. Backend valida assinatura HMAC do webhook.
3. Busca `Pagamento` por `gateway_payment_id` (idempotência).
4. Atualiza status de Pagamento e Assinatura.
5. Se falha: incrementa tentativas → grace period 7 dias → suspensão.

## Casos Extremos e Exceções

- **Pagamento falha repetidamente:** Após 3 tentativas do gateway + 7 dias grace, acesso é suspenso (read-only). Após 30 dias, dados são arquivados.
- **Downgrade com dados acima do limite:** Dados existentes são mantidos em read-only nos módulos removidos. Novos registros bloqueados.
- **Cupom expirado no momento do checkout:** Erro amigável + sugestão de prosseguir sem cupom.
- **Webhook duplicado do gateway:** Tratado via idempotência (`gateway_payment_id`). Segundo processamento é ignorado.
- **Tenant cancelado quer reativar:** Dentro de 90 dias: reativa com dados preservados. Após 90 dias: novo onboarding.
- **Stripe indisponível:** Fallback para Asaas. Se ambos falharem, retry em background + notificação ao admin.
- **Trial sem método de pagamento:** Permitido. Método exigido apenas na conversão.

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de Planos no backoffice com módulos e limites configuráveis.
- [ ] Feature flags avaliados em `require_module()` retornando 402 para módulos não contratados.
- [ ] Checkout funcional via Stripe (cartão) com webhooks processados.
- [ ] Checkout funcional via Asaas (boleto/PIX) com webhooks processados.
- [ ] Upgrade pro-rata imediato e downgrade agendado para próximo ciclo.
- [ ] Trial de 14 dias com acesso Enterprise e downgrade automático.
- [ ] Cupons com validação de código, validade, limite de usos e restrição por plano.
- [ ] Grace period de 7 dias para falhas de pagamento com suspensão automática.
- [ ] Dashboard backoffice com métricas: MRR, churn rate, conversão de trial.
- [ ] Testes de integração cobrindo fluxo completo: trial → conversão → upgrade → cancelamento.

## Sugestões de Melhoria Futura

1. **Planos customizáveis (à la carte):** Assinante monta seu pacote escolhendo módulos individuais.
2. **Billing por uso:** Cobrança adicional por hectare excedente ou usuários extras.
3. **Programa de indicação:** Desconto para quem indica novos assinantes.
4. **Notificação proativa de cartão:** Alerta antes do vencimento do cartão de crédito.
5. **Relatório de ROI:** Demonstra ao produtor o valor gerado pela plataforma vs custo da assinatura.
6. **Integração com contabilidade:** Emissão automática de NFS-e da assinatura.
