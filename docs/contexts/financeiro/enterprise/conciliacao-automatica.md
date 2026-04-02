---
modulo: Financeiro
submodulo: Conciliação Automática
nivel: enterprise
core: false
dependencias_core:
  - categorias-contas
  - lancamentos-basicos
dependencias_modulos:
  - ../profissional/conciliacao-bancaria.md
standalone: false
complexidade: XL
assinante_alvo:
  - grande produtor rural
  - empresa agrícola
  - cooperativa
  - grupo econômico rural
---

# Conciliação Automática

## Descrição Funcional

Submódulo que automatiza o processo de conciliação bancária através de regras configuráveis, matching inteligente e integração via API bancária (Open Finance). Enquanto a conciliação manual (nível Profissional) exige que o usuário confirme cada match individualmente, a conciliação automática processa centenas de transações em segundos, exigindo intervenção humana apenas em casos de ambiguidade.

Suporta importação automática de extratos via OFX agendado ou integração direta com APIs bancárias, eliminando o processo manual de download e upload de arquivos.

## Personas — Quem usa este submódulo

- **Gestor Financeiro corporativo:** configura regras de conciliação; monitora exceções; valida resultados.
- **Controller:** audita conciliações automáticas; configura regras de tolerância.
- **Diretor financeiro:** visualiza dashboards de conciliação consolidados de múltiplas fazendas.
- **Time de TI/integração:** configura conexões com APIs bancárias e monitora sincronização.

## Dores que resolve

1. **Volume alto de transações:** fazendas com centenas de movimentações mensais; conciliação manual é inviável.
2. **Múltiplas contas bancárias:** grupos com 10+ contas em bancos diferentes.
3. **Atraso no fechamento:** conciliação manual atrasa fechamento contábil em dias.
4. **Erro humano:** matching manual introduz erros; automação reduz falhas.
5. **Falta de tempo real:** sem integração bancária, saldo só é conferido periodicamente.

## Regras de Negócio

1. Matching automático opera em camadas de confiança:
   - **Nível 1 (alta confiança):** match exato por valor + data + referência bancária → concilia automaticamente.
   - **Nível 2 (média confiança):** match por valor + data (±2 dias) → concilia automaticamente se única opção.
   - **Nível 3 (baixa confiança):** match por valor com data distante ou múltiplos candidatos → envia para revisão manual.
2. Regras customizáveis por conta financeira.
3. Tolerância de valor configurável (ex.: aceitar diferença de até R$ 0,10 para taxas bancárias).
4. Tolerância de data configurável (padrão: ±3 dias úteis).
5. Regras de categorização automática: transações com padrão de descrição conhecido recebem categoria automaticamente.
6. Integração Open Finance: sincronização automática a cada 4 horas (configurável).
7. Log de auditoria completo: toda conciliação automática registra a regra que aplicou.
8. Taxa de acerto mínima: se batch de conciliação tiver < 70% de match nível 1+2, alertar o gestor.
9. Rollback em lote: é possível desfazer toda a conciliação de um período.
10. Transações de valor acima de limite configurável sempre vão para revisão manual.

## Entidades de Dados Principais

### RegrasConciliacao
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| conta_id | UUID | sim | FK → ContaFinanceira |
| nome | VARCHAR(100) | sim | Nome da regra |
| tipo_match | ENUM(EXATO, VALOR_DATA, DESCRICAO_PATTERN) | sim | Tipo de matching |
| tolerancia_valor_centavos | INTEGER | não | Tolerância de valor |
| tolerancia_dias | INTEGER | não | Tolerância de data |
| descricao_pattern | VARCHAR(255) | não | Regex para matching por descrição |
| categoria_id_auto | UUID | não | Categoria auto-atribuída |
| ativo | BOOLEAN | sim | Se está ativa |
| prioridade | INTEGER | sim | Ordem de execução |

### IntegracaoBancaria
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| conta_id | UUID | sim | FK → ContaFinanceira |
| provedor | ENUM(OPEN_FINANCE, PLUGGY, BELVO) | sim | Provedor de integração |
| status_conexao | ENUM(ATIVA, INATIVA, ERRO, EXPIRADA) | sim | Status |
| ultima_sincronizacao | TIMESTAMP | não | Última sincronização |
| intervalo_sync_minutos | INTEGER | sim | Intervalo de sincronização |
| credenciais_vault_ref | VARCHAR(255) | não | Referência no vault de credenciais |

### ConciliacaoAutomaticaLog
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| transacao_extrato_id | UUID | sim | FK → TransacaoExtrato |
| lancamento_id | UUID | não | FK → Lancamento (match encontrado) |
| regra_id | UUID | não | FK → RegrasConciliacao (regra aplicada) |
| nivel_confianca | ENUM(ALTO, MEDIO, BAIXO) | sim | Nível de confiança |
| resultado | ENUM(CONCILIADO_AUTO, REVISAO_MANUAL, SEM_MATCH) | sim | Resultado |
| executado_em | TIMESTAMP | sim | Data/hora da execução |

## Integrações Necessárias

- **Conciliação Bancária (profissional):** compartilha entidades de importação e transações; casos de revisão manual caem no fluxo padrão.
- **Lançamentos Básicos (essencial):** matching vincula transações a lançamentos.
- **Categorias e Contas (essencial):** regras de auto-categorização referenciam categorias existentes.
- **Open Finance / provedores:** APIs externas para importação automática de extratos (Pluggy, Belvo, etc.).

## Fluxo de Uso Principal (step-by-step)

1. Gestor acessa "Conciliação Automática" e configura regras para cada conta.
2. Opcionalmente configura integração bancária via Open Finance.
3. Sistema sincroniza extrato automaticamente no intervalo configurado (ou via upload manual).
4. Motor de conciliação processa transações aplicando regras por ordem de prioridade.
5. Transações com match de alta confiança são conciliadas automaticamente.
6. Transações de média confiança são conciliadas se match único; senão, vão para revisão.
7. Transações sem match ou de baixa confiança ficam na fila de revisão manual.
8. Gestor acessa dashboard de conciliação: conciliadas automaticamente, pendentes de revisão, sem match.
9. Resolve pendências manualmente (criar lançamento, vincular, ignorar).
10. Ao finalizar, relatório mostra taxa de acerto automático e exceções.

## Casos Extremos e Exceções

- **API bancária fora do ar:** sistema tenta novamente por 3 vezes com backoff; após isso, alerta o gestor.
- **Token Open Finance expirado:** notificar o usuário para reautenticar; suspender sincronização.
- **Transação com múltiplos matches de mesma confiança:** enviar para revisão manual; nunca conciliar automaticamente em caso de ambiguidade.
- **Regras conflitantes:** executar por ordem de prioridade; primeira regra que matcha vence.
- **Volume massivo (> 10.000 transações):** processamento assíncrono via fila; notificação ao concluir.
- **Transação de valor alto:** acima do limite configurado, sempre vai para revisão mesmo com match perfeito.
- **Rollback parcial:** ao desfazer conciliação de um período, lançamentos criados automaticamente são marcados como "estornados".
- **Múltiplas contas no mesmo banco:** transações entre contas próprias (transferências) devem ser detectadas e conciliadas em ambas.

## Critérios de Aceite (Definition of Done)

- [ ] Motor de matching com 3 níveis de confiança funcionando.
- [ ] Regras configuráveis por conta com tolerância de valor e data.
- [ ] Auto-categorização de transações por padrão de descrição.
- [ ] Integração com pelo menos 1 provedor Open Finance (Pluggy ou Belvo).
- [ ] Sincronização automática no intervalo configurado.
- [ ] Dashboard de conciliação com taxa de acerto e pendências.
- [ ] Rollback em lote de conciliação por período.
- [ ] Log de auditoria com regra aplicada e nível de confiança.
- [ ] Processamento assíncrono para volumes grandes.
- [ ] Alertas de erro de sincronização e taxa de acerto baixa.
- [ ] Tenant isolation em todos os endpoints e processos assíncronos.
- [ ] Testes: matching por camada, regras, integração mock, rollback, tenant isolation.

## Sugestões de Melhoria Futura

- **Machine learning adaptativo:** modelo que aprende com as conciliações manuais do usuário para melhorar sugestões.
- **Conciliação cross-conta:** detectar transferências entre contas próprias automaticamente.
- **Previsão de transações:** baseado em histórico, prever transações futuras para matching antecipado.
- **Integração Pix:** conciliar automaticamente recebimentos Pix com contas a receber.
- **WhatsApp alertas:** notificar o gestor via WhatsApp quando houver pendências de conciliação.
- **Multi-moeda:** suportar contas em USD para fazendas que exportam diretamente.
