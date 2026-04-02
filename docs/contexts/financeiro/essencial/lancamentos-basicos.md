---
modulo: Financeiro
submodulo: Lançamentos Básicos
nivel: essencial
core: false
dependencias_core:
  - categorias-contas
dependencias_modulos: []
standalone: true
complexidade: S
assinante_alvo:
  - pequeno produtor rural
  - agricultor familiar
  - técnico agrícola autônomo
---

# Lançamentos Básicos

## Descrição Funcional

Submódulo responsável pelo registro de todas as movimentações financeiras da propriedade rural — receitas e despesas. Permite ao produtor lançar entradas (vendas de produção, serviços) e saídas (compras de insumos, folha de pagamento, manutenção) de forma simples e categorizada. Cada lançamento é vinculado a uma conta, categoria e opcionalmente a uma fazenda específica dentro do tenant.

O submódulo opera em regime de caixa por padrão (data do efetivo pagamento/recebimento), mas armazena também a data de competência para relatórios futuros.

## Personas — Quem usa este submódulo

- **Produtor Rural (owner):** registra receitas de vendas e despesas do dia a dia; precisa de visão rápida do que entrou e saiu.
- **Administrador da Fazenda:** lança despesas operacionais (diesel, ração, fertilizantes) e confere lançamentos da equipe.
- **Cônjuge/Familiar:** auxilia no registro financeiro da propriedade familiar; precisa de interface simples e intuitiva.
- **Contador externo (visualização):** consulta lançamentos para fechamento fiscal; não edita, apenas exporta.

## Dores que resolve

1. **Caderninho de papel:** produtores perdem controle financeiro por falta de ferramenta digital simples.
2. **Planilhas desorganizadas:** dados em múltiplas planilhas Excel sem padronização, impossível consolidar.
3. **Falta de categorização:** gastos sem classificação impedem análise de onde o dinheiro está indo.
4. **Sem histórico:** lançamentos perdidos tornam impossível comparar períodos e tomar decisões.
5. **Mistura de contas pessoais e da fazenda:** sem separação clara entre finanças pessoais e da propriedade.

## Regras de Negócio

1. Todo lançamento deve pertencer a exatamente um `tenant_id` e uma `fazenda_id`.
2. Tipos permitidos: `RECEITA` ou `DESPESA`.
3. Valor deve ser positivo (> 0); o tipo determina o sinal no fluxo de caixa.
4. `data_competencia` é obrigatória; `data_pagamento` é preenchida na baixa.
5. Lançamento com `data_pagamento` preenchida é considerado "efetivado"; sem ela, é "previsto".
6. Categoria é obrigatória e deve pertencer ao mesmo tenant.
7. Lançamentos efetivados há mais de 30 dias não podem ser editados (soft-lock); admin pode desbloquear.
8. Exclusão é lógica (`deleted_at`); nunca física.
9. Anexos (notas fiscais, comprovantes) são opcionais; máximo 5 por lançamento, 10 MB cada.
10. Campo `observacao` é texto livre, máximo 500 caracteres.

## Entidades de Dados Principais

### Lancamento
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| fazenda_id | UUID | sim | FK → Fazenda |
| tipo | ENUM(RECEITA, DESPESA) | sim | Tipo do lançamento |
| categoria_id | UUID | sim | FK → Categoria |
| conta_id | UUID | não | FK → Conta (bancária/caixa) |
| descricao | VARCHAR(255) | sim | Descrição breve |
| valor_centavos | INTEGER | sim | Valor em centavos (BRL) |
| data_competencia | DATE | sim | Data de competência contábil |
| data_pagamento | DATE | não | Data do efetivo pagamento |
| status | ENUM(PREVISTO, EFETIVADO, CANCELADO) | sim | Status do lançamento |
| observacao | TEXT | não | Observação livre |
| created_by | UUID | sim | FK → Usuário que criou |
| created_at | TIMESTAMP | sim | Data de criação |
| updated_at | TIMESTAMP | sim | Última atualização |
| deleted_at | TIMESTAMP | não | Soft delete |

### LancamentoAnexo
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| lancamento_id | UUID | sim | FK → Lancamento |
| nome_arquivo | VARCHAR(255) | sim | Nome original do arquivo |
| path_s3 | VARCHAR(512) | sim | Caminho no storage |
| tamanho_bytes | INTEGER | sim | Tamanho do arquivo |
| mime_type | VARCHAR(100) | sim | Tipo MIME |

## Integrações Necessárias

- **Categorias e Contas (essencial):** categorias e contas são pré-requisito para lançar.
- **Fluxo de Caixa (essencial):** lançamentos efetivados alimentam automaticamente o fluxo de caixa.
- **Contas a Pagar/Receber (profissional):** lançamentos previstos podem ser promovidos a contas a pagar/receber.
- **Centro de Custo (profissional):** lançamentos podem ser rateados entre centros de custo.
- **Estoque (operacional):** compra de insumos gera lançamento de despesa automaticamente.

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa a tela de Lançamentos no menu Financeiro.
2. Clica em "Novo Lançamento".
3. Seleciona o tipo: Receita ou Despesa.
4. Preenche descrição, valor e data de competência.
5. Seleciona categoria (filtrada por tipo) e conta (opcional).
6. Opcionalmente anexa comprovante (drag-and-drop ou seleção de arquivo).
7. Salva como "Previsto" ou marca "Já pago/recebido" para efetivar imediatamente.
8. O lançamento aparece na listagem com filtros por período, tipo, categoria e status.
9. Para efetivar um lançamento previsto, usuário clica em "Baixar" e informa a data de pagamento.
10. Lançamentos efetivados refletem automaticamente no Fluxo de Caixa.

## Casos Extremos e Exceções

- **Lançamento duplicado:** sistema alerta se existir lançamento com mesmo valor, data e descrição nos últimos 7 dias (alerta, não bloqueio).
- **Fazenda sem categoria:** ao criar a primeira fazenda, o sistema gera categorias padrão automaticamente (Insumos, Mão de Obra, Vendas, etc.).
- **Edição de lançamento efetivado antigo:** bloqueio após 30 dias; admin pode desbloquear via ação explícita com log de auditoria.
- **Exclusão de lançamento vinculado a conciliação:** não permitida; deve desvincular antes.
- **Valor zero:** não permitido; validação no frontend e backend.
- **Categoria excluída:** lançamentos existentes mantêm referência; categoria aparece como "(excluída)" na listagem.
- **Múltiplas fazendas:** lançamento pertence a uma única fazenda; para rateio entre fazendas, usar Centro de Custo (profissional).

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de lançamentos via API com tenant isolation testado.
- [ ] Validação de valor > 0, categoria obrigatória e data_competencia obrigatória.
- [ ] Soft delete implementado; lançamentos excluídos não aparecem em listagens.
- [ ] Filtros por período, tipo, categoria, status e fazenda funcionando.
- [ ] Upload de anexos com validação de tamanho (10 MB) e quantidade (5).
- [ ] Ação de "Baixar" (efetivar) lançamento previsto.
- [ ] Bloqueio de edição após 30 dias para lançamentos efetivados.
- [ ] Alerta de duplicidade ao criar lançamento.
- [ ] Paginação na listagem (default 20, max 100 por página).
- [ ] Testes de integração: criação, edição, exclusão, baixa, filtros e tenant isolation.
- [ ] Tela frontend com formulário responsivo e listagem com filtros.

## Sugestões de Melhoria Futura

- **Lançamentos recorrentes:** permitir criar templates de lançamentos que se repetem (mensal, semanal).
- **Importação via CSV/Excel:** upload em massa de lançamentos históricos.
- **OCR de notas fiscais:** extrair dados automaticamente de fotos de NF-e.
- **Regras automáticas:** categorizar automaticamente lançamentos baseado em padrões de descrição.
- **Tags customizáveis:** além de categorias, permitir tags livres para agrupamento flexível.
- **Integração com NF-e:** puxar lançamentos automaticamente de notas fiscais eletrônicas emitidas/recebidas.
