---
modulo: Financeiro
submodulo: Conciliação Bancária
nivel: profissional
core: false
dependencias_core:
  - categorias-contas
  - lancamentos-basicos
dependencias_modulos:
  - ../essencial/lancamentos-basicos.md
  - ../essencial/categorias-contas.md
standalone: true
complexidade: L
assinante_alvo:
  - médio produtor rural
  - gestor financeiro rural
  - empresa agrícola
  - escritório de contabilidade rural
---

# Conciliação Bancária

## Descrição Funcional

Submódulo que permite ao produtor importar extratos bancários (formato OFX/CSV) e conciliar manualmente as transações do extrato com os lançamentos registrados no sistema. A conciliação garante que os registros financeiros internos estejam alinhados com a movimentação real das contas bancárias, identificando divergências, lançamentos faltantes e transações não reconhecidas.

Este é o processo manual de conciliação — a versão automatizada está disponível no nível Enterprise.

## Personas — Quem usa este submódulo

- **Gestor Financeiro:** realiza a conciliação semanal/mensal; identifica divergências e corrige lançamentos.
- **Assistente financeiro:** importa extratos e faz o matching manual das transações mais simples.
- **Contador externo:** valida que todos os lançamentos estão conciliados antes do fechamento.
- **Produtor Rural (owner):** confere se os saldos batem com o extrato do banco.

## Dores que resolve

1. **Lançamentos fantasma:** registros no sistema que não existem no banco (ou vice-versa).
2. **Saldo divergente:** saldo no sistema diferente do saldo real no banco.
3. **Lançamentos duplicados:** sem conciliação, duplicidades passam despercebidas.
4. **Fechamento contábil demorado:** contador gasta horas cruzando extratos com planilhas.
5. **Fraudes não detectadas:** movimentações bancárias não reconhecidas podem indicar fraude.

## Regras de Negócio

1. Importação suporta formatos OFX e CSV (layout configurável para CSV).
2. Cada importação é vinculada a uma conta financeira específica.
3. Transações importadas são armazenadas como `TransacaoExtrato` — entidade separada dos lançamentos.
4. Conciliação = vincular uma `TransacaoExtrato` a um `Lancamento` existente.
5. Status de transação do extrato: `PENDENTE`, `CONCILIADA`, `IGNORADA`.
6. Status de lançamento na conciliação: `NAO_CONCILIADO`, `CONCILIADO`.
7. O sistema sugere matches por: valor, data (±3 dias) e descrição (similaridade).
8. Match é manual: o usuário confirma ou rejeita a sugestão.
9. Transações do extrato sem match podem gerar um novo lançamento com um clique.
10. Período de conciliação é registrado; não é possível conciliar o mesmo período duas vezes sem desfazer a anterior.
11. Saldo do extrato é comparado com o saldo calculado no sistema; divergência é exibida.
12. Arquivos importados são armazenados para auditoria.

## Entidades de Dados Principais

### ImportacaoExtrato
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| conta_id | UUID | sim | FK → ContaFinanceira |
| arquivo_nome | VARCHAR(255) | sim | Nome do arquivo importado |
| arquivo_path | VARCHAR(512) | sim | Caminho no storage |
| formato | ENUM(OFX, CSV) | sim | Formato do arquivo |
| data_inicio | DATE | sim | Data início do extrato |
| data_fim | DATE | sim | Data fim do extrato |
| saldo_inicial_centavos | INTEGER | não | Saldo inicial do extrato |
| saldo_final_centavos | INTEGER | não | Saldo final do extrato |
| total_transacoes | INTEGER | sim | Quantidade de transações importadas |
| importado_em | TIMESTAMP | sim | Data/hora da importação |
| importado_por | UUID | sim | FK → Usuário |

### TransacaoExtrato
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| importacao_id | UUID | sim | FK → ImportacaoExtrato |
| data | DATE | sim | Data da transação |
| descricao | VARCHAR(255) | sim | Descrição do banco |
| valor_centavos | INTEGER | sim | Valor (positivo = crédito, negativo = débito) |
| tipo | ENUM(CREDITO, DEBITO) | sim | Tipo |
| referencia_banco | VARCHAR(100) | não | ID da transação no banco |
| status | ENUM(PENDENTE, CONCILIADA, IGNORADA) | sim | Status da conciliação |
| lancamento_id | UUID | não | FK → Lancamento (quando conciliada) |
| conciliado_em | TIMESTAMP | não | Data/hora da conciliação |
| conciliado_por | UUID | não | FK → Usuário que conciliou |

## Integrações Necessárias

- **Lançamentos Básicos (essencial):** lançamentos são o alvo da conciliação; novos lançamentos podem ser criados a partir de transações não reconhecidas.
- **Categorias e Contas (essencial):** conta financeira é a referência para importação; categorias sugeridas para novos lançamentos.
- **Contas a Pagar/Receber (profissional):** parcelas baixadas devem ser conciliadas.
- **Conciliação Automática (enterprise):** versão automatizada deste submódulo.

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa "Conciliação Bancária" no menu Financeiro.
2. Seleciona a conta financeira que deseja conciliar.
3. Clica em "Importar Extrato" e faz upload do arquivo OFX ou CSV.
4. Sistema processa o arquivo e lista as transações importadas.
5. Para cada transação, o sistema sugere possíveis matches com lançamentos existentes.
6. Usuário revisa e confirma os matches corretos (vincular extrato ↔ lançamento).
7. Transações sem match: usuário pode criar novo lançamento, ignorar ou deixar pendente.
8. Ao finalizar, sistema exibe resumo: conciliadas, pendentes, ignoradas e divergência de saldo.
9. Usuário finaliza a conciliação do período.
10. Relatório de conciliação fica disponível para auditoria.

## Casos Extremos e Exceções

- **Arquivo OFX corrompido:** rejeitar com mensagem clara; não importar parcialmente.
- **Transação duplicada na importação:** detectar por `referencia_banco` + data + valor; alertar o usuário.
- **Lançamento já conciliado com outra transação:** não permitir dupla conciliação; desvincular primeiro.
- **Valor da transação difere do lançamento:** permitir conciliar com diferença, registrando a divergência.
- **Extrato com período sobreposto a importação anterior:** alertar e permitir reimportação (substitui a anterior).
- **CSV com layout desconhecido:** tela de mapeamento de colunas para o usuário configurar.
- **Conta financeira sem lançamentos:** conciliação gera todos os lançamentos a partir do extrato.
- **Encoding do arquivo:** suportar UTF-8 e ISO-8859-1 (comum em bancos brasileiros).

## Critérios de Aceite (Definition of Done)

- [ ] Importação de arquivos OFX com parsing correto de transações.
- [ ] Importação de CSV com mapeamento configurável de colunas.
- [ ] Listagem de transações importadas com sugestão de match.
- [ ] Conciliação manual: vincular transação ↔ lançamento.
- [ ] Criação de lançamento a partir de transação não reconhecida.
- [ ] Detecção de duplicatas na importação.
- [ ] Comparação de saldos (extrato vs. sistema).
- [ ] Relatório de conciliação com status de cada transação.
- [ ] Armazenamento do arquivo original para auditoria.
- [ ] Tenant isolation em todos os endpoints.
- [ ] Testes: importação OFX, importação CSV, matching, conciliação, duplicatas, tenant isolation.

## Sugestões de Melhoria Futura

- **Conciliação automática:** matching por regras configuráveis (ver Enterprise).
- **Integração Open Finance:** importar extrato diretamente via API bancária, sem arquivo.
- **Machine learning para sugestão:** melhorar sugestões de match com base no histórico de conciliações do usuário.
- **Conciliação em lote:** confirmar todos os matches sugeridos de uma vez.
- **Relatório de pendências:** listar lançamentos não conciliados por mais de 30 dias.
- **Multi-banco simultâneo:** conciliar múltiplas contas em uma única sessão.
