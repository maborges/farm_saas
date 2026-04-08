---
modulo: Core
submodulo: Planos e Assinatura
nivel: core
core: true
dependencias_core:
  - Identidade e Acesso
  - Multipropriedade
dependencias_modulos: []
standalone: false
complexidade: L
assinante_alvo: todos os assinantes
---

# Planos e Assinatura

## Descrição Funcional

Submódulo responsável por todo o ciclo de vida de assinaturas da plataforma: definição de planos com módulos e limites, feature flags por plano, gestão de upgrades/downgrades, trial, cancelamento, cupons de desconto e integração com gateways de pagamento (Stripe para cartão internacional e Asaas para boleto/PIX no mercado brasileiro). Determina quais módulos e níveis cada tenant pode acessar em tempo real.

Este submódulo implementa o modelo de negócios SaaS da plataforma, com três tiers (Essencial, Profissional, Enterprise) que diferenciam por módulos habilitados, limites operacionais (número de fazendas, usuários, armazenamento) e nível de suporte. O sistema de feature flags permite liberação gradual de funcionalidades e testes A/B de pricing.

A integração com Stripe e Asaas automatiza cobrança recorrente, reduzindo inadimplência e trabalho manual de backoffice. Webhooks de pagamento atualizam status de assinatura em tempo real.

## Personas — Quem usa este submódulo

- **Owner do Tenant:** Visualiza plano atual, faz upgrade/downgrade, gerencia método de pagamento, consulta histórico de faturas. Precisa de transparência sobre custos e benefícios de cada plano.

- **Administrador Backoffice:** Cria e edita planos, gerencia cupons, monitora métricas de receita (MRR, churn, conversão de trial), ajusta limites manualmente. Toma decisões de pricing baseadas em dados.

- **Sistema (runtime):** Avalia feature flags em cada request via `require_module()` para habilitar/desabilitar funcionalidades conforme plano contratado.

- **Gestor Financeiro do Tenant:** Acessa faturas, comprovantes de pagamento e notas fiscais. Configura dados de faturamento (CNPJ, endereço fiscal).

- **Suporte Comercial:** Aplica cupons de desconto, negocia planos customizados para grandes clientes, processa upgrades manuais.

## Dores que resolve

1. **Acesso indevido a funcionalidades não contratadas:** Sem feature flags, qualquer tenant poderia acessar módulos Enterprise sem pagar. Prejuízo direto de receita.

2. **Cobrança manual e desorganizada:** Sem integração com gateway, controle de pagamentos é feito em planilhas. Inadimplência alta por falta de automatização.

3. **Dificuldade em experimentar antes de pagar:** Sem trial, produtores hesitam em contratar sem testar. Taxa de conversão baixa.

4. **Perda de receita por churn silencioso:** Sem métricas de assinatura, cancelamentos passam despercebidos. Não há ação proativa de retenção.

5. **Inflexibilidade de planos:** Sem upgrade/downgrade self-service, mudanças de plano dependem de suporte manual. Fricção na jornada do cliente.

6. **Falta de transparência:** Tenant não sabe o que está incluído no plano, quantas fazendas pode adicionar, ou quando será cobrado.

7. **Gestão de cupons manual:** Cupons aplicados via planilha, sem controle de validade, limite de usos ou restrição por plano.

## Regras de Negócio

1. **RN-PA-001:** Cada Tenant possui exatamente 1 assinatura ativa por vez. Assinatura inclui plano, status, ciclo de billing e método de pagamento.

2. **RN-PA-002:** O plano define: módulos habilitados (com nível máximo), limites operacionais (fazendas, usuários, hectares, armazenamento), gateways disponíveis.

3. **RN-PA-003:** `require_module()` consulta feature flags em runtime — módulo não contratado retorna HTTP 402 (`ModuleNotContractedError`). Erro inclui mensagem de upgrade.

4. **RN-PA-004:** Upgrade é imediato — diferença de valor cobrada pro-rata no ciclo atual. Exemplo: upgrade no dia 15 de um ciclo de 30 dias cobra 50% do valor.

5. **RN-PA-005:** Downgrade é agendado para o início do próximo ciclo de billing (sem reembolso). Tenant mantém acesso ao plano atual até o fim do ciclo.

6. **RN-PA-006:** Trial padrão: 14 dias com acesso a todos os módulos nível Enterprise. Cartão de crédito não é exigido para iniciar trial.

7. **RN-PA-007:** Após trial sem conversão: downgrade automático para plano gratuito (Core only, 1 fazenda, 3 usuários). Dados são preservados.

8. **RN-PA-008:** Falha de pagamento: grace period de 7 dias → suspensão de acesso (read-only) → após 30 dias, arquivamento. Dados arquivados são exportáveis por 90 dias.

9. **RN-PA-009:** Cancelamento: acesso mantido até o fim do ciclo pago. Dados preservados por 90 dias para exportação. Após 90 dias, exclusão definitiva.

10. **RN-PA-010:** Cupons possuem: código único, tipo (percentual/valor fixo), validade, limite de usos, restrição por plano. Cupons não são cumulativos.

11. **RN-PA-011:** Stripe é gateway primário (cartão de crédito/débito). Asaas é gateway secundário (boleto/PIX — mercado brasileiro). Tenant escolhe gateway preferido.

12. **RN-PA-012:** Webhooks de pagamento são idempotentes via `gateway_payment_id` (previne duplicação). Webhook processado múltiplas vezes tem efeito único.

13. **RN-PA-013:** Reembolso só é processado manualmente via backoffice. Não há reembolso automático.

14. **RN-PA-014:** Plano Enterprise com contrato anual tem 2 meses grátis (desconto de 16.6%). Pagamento antecipado ou parcelado em até 12x.

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `Plano` | id (UUID), nome (String 50), slug (String 50 unique), descricao (Text), modulos_json (JSONB), limites_json (JSONB), preco_mensal (Decimal 10,2), preco_anual (Decimal 10,2), desconto_anual_percent (Decimal 5,2), ativo (Boolean), ordem_display (Integer), created_at (DateTime) | → Assinatura[], → FeatureFlag[] |
| `Assinatura` | id (UUID), tenant_id (UUID FK unique), plano_id (UUID FK), status (Enum: trial/ativa/suspensa/cancelada/grace_period), inicio (Date), fim (Date nullable), trial_fim (DateTime nullable), gateway (Enum: stripe/asaas), gateway_subscription_id (String 255), ciclo_dia (Integer 1-28), created_at (DateTime), updated_at (DateTime) | → Tenant, → Plano, → Pagamento[] |
| `Pagamento` | id (UUID), assinatura_id (UUID FK), valor (Decimal 10,2), status (Enum: pendente/pago/falha/reembolsado), gateway (Enum: stripe/asaas), gateway_payment_id (String 255 unique), metodo (Enum: cartao/boleto/pix), pago_em (DateTime nullable), vencimento_em (Date), created_at (DateTime) | → Assinatura |
| `Cupom` | id (UUID), codigo (String 50 unique), descricao (Text), tipo_desconto (Enum: percentual/fixo), valor_desconto (Decimal 10,2), validade_inicio (DateTime), validade_fim (DateTime), usos_restantes (Integer nullable), usos_maximos (Integer nullable), planos_permitidos (JSONB), is_active (Boolean default true), created_at (DateTime) | → Assinatura[] (via uso) |
| `PlanoMudanca` | id (UUID), tenant_id (UUID FK), plano_anterior_id (UUID FK), plano_novo_id (UUID FK), tipo (Enum: upgrade/downgrade), efetivo_em (DateTime), motivo (Text), valor_pro_rata (Decimal 10,2 nullable), created_by (UUID FK), created_at (DateTime) | → Tenant, → Plano (anterior e novo) |
| `FeatureFlag` | id (UUID), plano_id (UUID FK), modulo (String 50), nivel_maximo (Enum: essencial/profissional/enterprise), habilitado (Boolean default true), created_at (DateTime) | → Plano |
| `Fatura` | id (UUID), assinatura_id (UUID FK), periodo_inicio (Date), periodo_fim (Date), valor_total (Decimal 10,2), valor_desconto (Decimal 10,2), cupom_id (UUID FK nullable), status (Enum: aberta/paga/vencida/cancelada), pdf_s3_key (String 512), created_at (DateTime) | → Assinatura, → Cupom |
| `MetodoPagamento` | id (UUID), tenant_id (UUID FK), gateway (Enum: stripe/asaas), gateway_payment_method_id (String 255), tipo (Enum: cartao/boleto/pix), ultimo4 (String 4 nullable), bandeira (String 50 nullable), expiracao (String 5 nullable), is_default (Boolean default true), created_at (DateTime) | → Tenant |

## Integrações Necessárias

- **Stripe:** Subscriptions API, Checkout Sessions, Customer Portal, Webhooks (payment_intent.succeeded, customer.subscription.updated/deleted, invoice.paid/payment_failed).

- **Asaas:** Assinaturas, emissão de boleto, PIX QR code, webhooks de confirmação (PAYMENT_CREATED, PAYMENT_CONFIRMED, PAYMENT_OVERDUE).

- **Core `require_module()`:** Avaliação de feature flags em cada request protegido. Cache em Redis para performance.

- **Frontend:** Página de planos comparativos, fluxo de upgrade, portal de billing, checkout integrado.

- **Backoffice:** CRUD de planos e cupons, dashboard de MRR/churn/trial conversion, gestão manual de assinaturas.

- **Notificações e Alertas:** Notificações de vencimento de fatura, falha de pagamento, trial prestes a expirar.

- **Emissão de NF-e (futuro):** Integração com sistema de nota fiscal para emissão automática de notas de assinatura.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Assinatura inicial (pós-trial)
1. Trial de 14 dias expira → sistema exibe banner "Seu trial terminou. Escolha um plano para continuar."
2. Owner acessa "Planos" → vê comparativo com módulos e limites por plano (Essencial, Profissional, Enterprise).
3. Seleciona plano desejado → escolhe ciclo (mensal/anual com desconto de 16.6% para anual).
4. Opcionalmente aplica código de cupom. Sistema valida e exibe desconto.
5. Seleciona gateway (Stripe para cartão, Asaas para boleto/PIX).
6. Redirecionado para checkout do gateway (Stripe Checkout ou Asaas).
7. Gateway processa pagamento e redireciona de volta para plataforma.
8. Webhook de confirmação atualiza `Assinatura.status = ativa` e libera feature flags.
9. Owner recebe e-mail de confirmação e acesso liberado.

### Fluxo 2: Upgrade self-service
1. Owner acessa "Minha Assinatura" → "Alterar Plano".
2. Vê planos superiores com destaque nas funcionalidades adicionais.
3. Seleciona novo plano → sistema calcula valor pro-rata restante do ciclo.
4. Exibe resumo: "Upgrade para Plano Profissional. Valor adicional: R$ X,XX (proporcional a Y dias)."
5. Confirma pagamento → gateway processa cobrança imediata.
6. Webhook de confirmação → upgrade aplicado imediatamente.
7. Feature flags atualizados → novos módulos disponíveis instantaneamente.
8. Owner recebe e-mail com nova fatura e confirmação de upgrade.

### Fluxo 3: Webhook de pagamento
1. Gateway (Stripe/Asaas) envia webhook com evento de pagamento.
2. Backend valida assinatura HMAC do webhook (segurança).
3. Busca `Pagamento` por `gateway_payment_id` (idempotência).
4. Se pagamento já processado, retorna 200 OK imediatamente.
5. Se novo, atualiza status de Pagamento e Assinatura.
6. Se sucesso: `Pagamento.status = pago`, `Pagamento.pago_em = now()`.
7. Se falha: incrementa tentativas → grace period 7 dias → suspensão.
8. Notifica Owner por e-mail sobre status do pagamento.

### Fluxo 4: Cancelamento de assinatura
1. Owner acessa "Minha Assinatura" → "Cancelar Assinatura".
2. Sistema exibe modal de retenção: "Tem certeza? Você perderá acesso a X, Y, Z."
3. Owner confirma. Sistema solicita motivo (dropdown: preço, não uso, migração, outro).
4. `Assinatura.status = cancelada`, `Assinatura.fim = fim_do_ciclo_atual`.
5. Owner mantém acesso até o fim do ciclo pago.
6. E-mail de confirmação de cancelamento é enviado.
7. Backoffice é notificado para possível ação de retenção.
8. Após fim do ciclo, acesso é revogado. Dados preservados por 90 dias.

### Fluxo 5: Falha de pagamento e recuperação
1. Gateway notifica falha de pagamento (cartão recusado, boleto não pago).
2. `Assinatura.status = grace_period`. Owner recebe e-mail: "Pagamento falhou. Você tem 7 dias para regularizar."
3. Sistema tenta nova cobrança automática após 3 dias (Stripe retry).
4. Se falhar novamente, nova tentativa após 7 dias.
5. Após 7 dias sem pagamento: `Assinatura.status = suspensa`. Acesso se torna read-only.
6. Owner recebe e-mail: "Acesso suspenso. Regularize para reativar."
7. Após 30 dias suspenso: `Assinatura.status = arquivada`. Dados são exportáveis.
8. Owner pode reativar a qualquer momento pagando faturas pendentes.

## Casos Extremos e Exceções

- **Pagamento falha repetidamente:** Após 3 tentativas do gateway + 7 dias grace, acesso é suspenso (read-only). Após 30 dias, dados são arquivados. Owner pode exportar dados via "Exportar Dados" mesmo arquivado.

- **Downgrade com dados acima do limite:** Dados existentes são mantidos em read-only nos módulos removidos. Novos registros bloqueados. Exemplo: downgrade de Enterprise (10 fazendas) para Essencial (3 fazendas) com 5 fazendas ativas → não pode criar novas fazendas até inativar 2.

- **Cupom expirado no momento do checkout:** Erro amigável + sugestão de prosseguir sem cupom. Código é invalidado no frontend e backend.

- **Webhook duplicado do gateway:** Tratado via idempotência (`gateway_payment_id`). Segundo processamento é ignorado, retorna 200 OK.

- **Tenant cancelado quer reativar:** Dentro de 90 dias: reativa com dados preservados e mesma assinatura. Após 90 dias: novo onboarding, dados perdidos.

- **Stripe indisponível:** Fallback para Asaas. Se ambos falharem, retry em background + notificação ao admin. Checkout em manutenção exibe mensagem clara.

- **Trial sem método de pagamento:** Permitido. Método exigido apenas na conversão. Trial sem conversão vira plano gratuito automaticamente.

- **Plano descontinuado:** Planos existentes são mantidos (grandfather clause). Tenant não pode migrar de volta para plano descontinuado.

- **Chargeback de cartão de crédito:** `Assinatura.status = suspensa` imediatamente. Backoffice notificado para ação manual.

- **Mudança de fuso horário do tenant:** Ciclo de billing é ajustado para o novo fuso. Fatura do mês pode ter dias a mais ou a menos (prorrateamento).

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
- [ ] Portal do cliente (Stripe Customer Portal / Asaas) integrado para gestão de pagamento.
- [ ] Emissão de faturas em PDF com dados fiscais do tenant.

## Sugestões de Melhoria Futura

1. **Planos customizáveis (à la carte):** Assinante monta seu pacote escolhendo módulos individuais. Pricing dinâmico baseado em seleção.

2. **Billing por uso:** Cobrança adicional por hectare excedente, usuários extras ou armazenamento além do limite. Medição em tempo real.

3. **Programa de indicação:** Desconto para quem indica novos assinantes. Código de indicação com tracking de conversão.

4. **Notificação proativa de cartão:** Alerta antes do vencimento do cartão de crédito (30 dias antes da expiração).

5. **Relatório de ROI:** Demonstra ao produtor o valor gerado pela plataforma vs custo da assinatura. Exemplo: "Você economizou R$ X com otimização de insumos."

6. **Integração com contabilidade:** Emissão automática de NFS-e da assinatura. Dados fiscais sincronizados com sistema contábil.

7. **Cobrança via boleto parcelado:** Asaas suporta parcelamento. Tenant pode optar por pagar anual em até 12x no boleto.

8. **Retenção automática:** Oferta de desconto automático quando sistema detecta intenção de cancelamento (acesso reduzido, feature não usada).

9. **Planos sazonais:** Plano específico para safra (6 meses) com preço reduzido. Ideal para produtores que usam sistema apenas durante safra.

10. **White-label para cooperativas:** Cooperativa contrata plano Enterprise e revende para cooperados com marca própria.
