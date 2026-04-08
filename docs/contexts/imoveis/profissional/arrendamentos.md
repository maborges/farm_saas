---
modulo: Imóveis Rurais
submodulo: Arrendamentos
nivel: profissional
core: false
dependencias_core:
  - cadastro-propriedade
  - identidade-acesso
  - notificacoes-alertas
dependencias_modulos:
  - imoveis/essencial/cadastro-imovel
  - imoveis/essencial/documentos-legais
  - financeiro/essencial/lancamentos-basicos
standalone: false
complexidade: M
assinante_alvo:
  - proprietário rural com imóveis arrendados
  - arrendatário (produtor que arrenda terra)
  - contador agrícola
---

# Arrendamentos e Parcerias Rurais

## Descrição Funcional

Submódulo responsável pela gestão de contratos de arrendamento rural e parceria agrícola vinculados aos imóveis cadastrados. Cobre o ciclo completo: elaboração do contrato, registro das condições (valor, prazo, área, cláusulas), controle de parcelas/reajustes e integração automática com o módulo Financeiro para lançamento de receitas (proprietário) ou despesas (arrendatário).

Suporta os dois modelos regulamentados pela legislação brasileira:
- **Arrendamento:** pagamento fixo em dinheiro ou produto pelo uso da terra, regido pela Lei 4.504/1964 (Estatuto da Terra).
- **Parceria:** divisão dos frutos e resultados da atividade agropecuária entre proprietário e parceiro.

O submódulo automatiza a geração de lançamentos financeiros, alertas de vencimento de parcelas, reajustes anuais e vencimento de contrato, eliminando o controle manual em planilhas e reduzindo inadimplência.

## Personas — Quem usa este submódulo

- **Proprietário Rural (Arrendador):** Registra contrato, acompanha recebimentos, controla reajustes anuais. Precisa de previsibilidade de fluxo de caixa e garantia de recebimento.

- **Arrendatário/Parceiro:** Registra contrato de arrendamento que opera (despesa), acompanha vencimentos. Pode ser o próprio tenant (arrenda terra de terceiro) ou terceiro que arrenda terra do tenant.

- **Contador Agrícola:** Verifica lançamentos automáticos para apuração de LCDPR e ITR. Precisa de documentação completa para declaração de rendimentos de arrendamento.

- **Advogado Rural:** Consulta cláusulas, prazos e condições do contrato registrado. Due diligence de contratos vigentes.

- **Gestor de Fazenda:** Monitora área arrendada vs. área própria para planejamento de safra. Controle de operações em áreas arrendadas.

- **Gestor Financeiro:** Acompanha contas a receber de arrendamento, inadimplência e fluxo de caixa previsto.

## Dores que resolve

1. **Contratos informais:** Acordos verbais sem registro, sem controle de prazos. Produtor não tem comprovação em caso de disputa.

2. **Reajustes esquecidos:** Correção pelo IGP-M ou outro índice não aplicada no prazo correto. Prejuízo acumulado ao longo dos anos.

3. **Lançamentos financeiros manuais:** Proprietário lança receita de arrendamento manualmente todo mês. Trabalho repetitivo e propenso a erros.

4. **Sem visão consolidada:** Proprietário com múltiplos arrendamentos não sabe o total a receber por período. Dificulta planejamento financeiro.

5. **Vencimento de contrato:** Notificação tardia para renovação ou rescisão. Produtor fica sem saber se renova ou busca novo arrendatário.

6. **Inadimplência não monitorada:** Arrendatário atrasa pagamento e proprietário só descobre semanas depois. Sem alerta proativo.

7. **Área arrendada não integrada:** Operações em área arrendada não são segregadas das operações em área própria. Dificulta cálculo de rentabilidade.

## Regras de Negócio

1. **RN-AR-001:** Todo contrato vincula-se a exatamente um `imovel_id` e ao menos uma `fazenda_id` arrendada/parceria. Validação de existência.

2. **RN-AR-002:** Tipos de contrato: `ARRENDAMENTO` (pagamento fixo) ou `PARCERIA` (percentual da produção). Comportamento diferente para cada tipo.

3. **RN-AR-003:** Para arrendamento: valor fixo em `BRL` ou `sacas_ha` (ex.: 10 sacas de soja por hectare). Conversão para BRL na data do pagamento.

4. **RN-AR-004:** Para parceria: percentual do resultado (ex.: 30% da produção para o proprietário). Lançamento ocorre após colheita e venda.

5. **RN-AR-005:** Prazo mínimo legal: arrendamento agrícola 3 anos; pecuário 3 anos; misto 5 anos (Lei 4.504/1964, Art. 95). Contrato com prazo inferior é alertado como "irregular".

6. **RN-AR-006:** Reajuste anual: índice configurável (IGP-M, IPCA, SELIC, sacas de produto). Alertas 30 dias antes da data de reajuste.

7. **RN-AR-007:** Lançamentos financeiros automáticos: contrato ativo gera lançamento previsto no módulo Financeiro nas datas de vencimento das parcelas.

8. **RN-AR-008:** Contrato rescindido antecipadamente requer registro de motivo e data. Parcelas futuras são canceladas automaticamente.

9. **RN-AR-009:** CCIR do imóvel deve estar ativo para criar ou renovar contrato. Validação bloqueante: "CCIR vencido impede criação de arrendamento."

10. **RN-AR-010:** Valor máximo do arrendamento: 15% do valor cadastral do imóvel por ano (Lei 4.504/1964, Art. 93). Sistema alerta se ultrapassar.

11. **RN-AR-011:** Contrato deve ser registrado em cartório para validade plena (Lei 6.015/1973). Campo `registro_cartorio` com número e data.

12. **RN-AR-012:** Exclusão lógica; contratos encerrados ficam no histórico. Dados preservados para auditoria fiscal.

## Entidades de Dados Principais

### ContratoArrendamento
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| imovel_id | UUID | sim | FK → ImovelRural |
| fazenda_id | UUID | sim | FK → Fazenda |
| tipo | ENUM | sim | ARRENDAMENTO, PARCERIA |
| arrendatario_tipo | ENUM | sim | PESSOA_FISICA, PESSOA_JURIDICA, FAZENDA_TENANT |
| arrendatario_pessoa_id | UUID | não | FK → Pessoa (arrendatário externo) |
| arrendatario_fazenda_id | UUID | não | FK → Fazenda (arrendatário interno ao tenant) |
| area_arrendada_ha | DECIMAL(12,4) | sim | Área objeto do contrato em hectares |
| valor_modalidade | ENUM | sim | FIXO_BRL, FIXO_SACAS, PERCENTUAL |
| valor | DECIMAL(12,2) | sim | Valor (BRL, sacas/ha ou %) |
| commodity_referencia | VARCHAR(50) | não | Commodity de referência para sacas (ex.: "SOJA", "MILHO") |
| periodicidade | ENUM | sim | MENSAL, SEMESTRAL, ANUAL, SAFRA |
| data_inicio | DATE | sim | Início de vigência |
| data_fim | DATE | sim | Fim de vigência |
| indice_reajuste | VARCHAR(20) | não | IGP-M, IPCA, SELIC, SACAS |
| data_reajuste_anual | DATE | não | Data anual do reajuste (ex.: aniversário do contrato) |
| dia_vencimento | INTEGER | não | Dia do mês para vencimento (1-28) |
| status | ENUM | sim | ATIVO, ENCERRADO, RESCINDIDO, SUSPENSO |
| motivo_rescisao | TEXT | não | Motivo da rescisão antecipada |
| path_contrato_pdf | VARCHAR(512) | não | Caminho do contrato assinado em PDF |
| registro_cartorio | VARCHAR(100) | não | Número do registro em cartório |
| clausulas_observacoes | TEXT | não | Cláusulas e observações livres |
| created_by | UUID | sim | FK → Usuário que criou |
| created_at | TIMESTAMP | sim | Data de criação |
| updated_at | TIMESTAMP | sim | Última atualização |
| deleted_at | TIMESTAMP | não | Soft delete |

### ParcelaArrendamento
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| contrato_id | UUID | sim | FK → ContratoArrendamento |
| numero_parcela | INTEGER | sim | Número sequencial da parcela (1, 2, 3...) |
| data_vencimento | DATE | sim | Data de vencimento da parcela |
| valor_centavos | INTEGER | sim | Valor em centavos (BRL) |
| valor_sacas | DECIMAL(10,2) | não | Valor em sacas (se modalidade sacas) |
| status | ENUM | sim | PREVISTA, PAGA, CANCELADA, VENCIDA |
| lancamento_financeiro_id | UUID | não | FK → Lancamento (módulo Financeiro) |
| data_pagamento | DATE | não | Data efetiva do pagamento |
| indice_aplicado | DECIMAL(10,4) | não | Índice de reajuste aplicado (ex.: 1.0450 para +4.5%) |
| observacao | TEXT | não | Observações da parcela |
| created_at | TIMESTAMP | sim | Data de criação |

### HistoricoReajuste
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| contrato_id | UUID | sim | FK → ContratoArrendamento |
| data_reajuste | DATE | sim | Data do reajuste |
| indice_nome | VARCHAR(50) | sim | Nome do índice (IGP-M, IPCA, etc.) |
| indice_valor | DECIMAL(10,4) | sim | Valor do índice (ex.: 1.0450) |
| valor_anterior | DECIMAL(12,2) | sim | Valor antes do reajuste |
| valor_novo | DECIMAL(12,2) | sim | Valor após o reajuste |
| created_by | UUID | sim | FK → Usuario |
| created_at | TIMESTAMP | sim | Data do reajuste |

## Integrações Necessárias

- **Imóvel Rural — Cadastro:** Contrato referencia imóvel cadastrado com CCIR ativo. Validação de regularidade fiscal.

- **Imóvel Rural — Documentos:** Upload do contrato assinado como documento vinculado ao imóvel. Versionamento de aditivos.

- **Financeiro — Lançamentos Básicos:** Parcelas geram lançamentos previstos automaticamente; baixa via módulo Financeiro. Integração bidirecional.

- **Pessoas (core):** Arrendatário pode ser pessoa física ou jurídica cadastrada. Validação de CPF/CNPJ.

- **Notificações (core):** Alertas de vencimento de parcela (T-7 dias), reajuste (T-30 dias) e vencimento de contrato (T-60, T-30 dias).

- **API de Índices (IBGE/FGV):** Consulta automática de IGP-M, IPCA para reajuste. Integração futura.

- **API de Cotações (CEPEA/B3):** Conversão de sacas para BRL usando cotação do dia do pagamento.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Criação de contrato de arrendamento
1. Usuário acessa o imóvel e abre a aba "Arrendamentos".
2. Clica em "Novo Contrato".
3. Seleciona o tipo (Arrendamento ou Parceria).
4. Informa o arrendatário:
   - Se interno: seleciona fazenda do tenant.
   - Se externo: cadastra ou seleciona pessoa (CPF/CNPJ).
5. Define área arrendada (ex.: 200 ha), valor (ex.: R$ 500/ha ou 10 sacas/ha), periodicidade (anual, safra).
6. Configura índice de reajuste anual (ex.: IGP-M) e data de reajuste (aniversário do contrato).
7. Define dia de vencimento da parcela (ex.: dia 10 de cada mês).
8. Opcionalmente faz upload do contrato assinado em PDF.
9. Informa número de registro em cartório (se houver).
10. Salva — sistema valida CCIR ativo do imóvel.
11. Sistema gera automaticamente as parcelas previstas até o fim do contrato.
12. Lançamentos financeiros previstos são criados no módulo Financeiro.

### Fluxo 2: Geração automática de parcelas
1. Contrato é salvo com periodicidade mensal e duração de 3 anos (36 parcelas).
2. Sistema calcula valor total: área (200 ha) × valor (R$ 500/ha) = R$ 100.000/ano.
3. Valor da parcela mensal: R$ 100.000 ÷ 12 = R$ 8.333,33.
4. Para cada mês até o fim do contrato:
   - Cria registro em `ParcelaArrendamento` com data de vencimento.
   - Cria lançamento previsto no módulo Financeiro.
5. Parcelas são listadas com status "Prevista".
6. Usuário visualiza calendário de recebimentos.

### Fluxo 3: Baixa de parcela paga
1. Vence parcela do arrendamento.
2. Arrendatário realiza pagamento (PIX, boleto, transferência).
3. Proprietário acessa Financeiro → Contas a Receber.
4. Localiza lançamento do arrendamento e clica em "Baixar".
5. Informa data de pagamento, valor, possível desconto/juros.
6. Sistema atualiza `ParcelaArrendamento.status = PAGA`.
7. Lançamento financeiro é marcado como pago.
8. Histórico registra pagamento.

### Fluxo 4: Reajuste anual automático
1. Data de reajuste anual se aproxima (T-30 dias).
2. Sistema dispara alerta: "Reajuste de arrendamento em 30 dias."
3. Usuário acessa contrato e clica em "Aplicar Reajuste".
4. Sistema consulta índice configurado (ex.: IGP-M acumulado = 4.5%).
5. Exibe preview: "Valor atual: R$ 8.333,33 → Novo valor: R$ 8.708,33 (+4.5%)."
6. Usuário confirma reajuste.
7. Sistema cria registro em `HistoricoReajuste`.
8. Parcelas futuras são atualizadas com novo valor.
9. Lançamentos financeiros futuros são recalculados.

### Fluxo 5: Rescisão antecipada de contrato
1. Arrendatário solicita rescisão antecipada.
2. Proprietário acessa contrato → "Rescindir Contrato".
3. Seleciona motivo (dropdown: "Solicitação do arrendatário", "Venda do imóvel", "Uso próprio", "Inadimplência", etc.).
4. Informa data de rescisão.
5. Sistema exibe impacto: "X parcelas futuras serão canceladas."
6. Usuário confirma rescisão.
7. `ContratoArrendamento.status = RESCINDIDO`.
8. Parcelas futuras são marcadas como "Cancelada".
9. Lançamentos financeiros futuros são cancelados.
10. Histórico registra rescisão com motivo.

### Fluxo 6: Arrendamento em sacas de commodity
1. Contrato é criado com valor em sacas: 10 sacas de soja/ha.
2. Área: 200 ha. Total: 2.000 sacas/ano.
3. No vencimento da parcela, sistema consulta cotação do dia (CEPEA).
4. Cotação: R$ 150,00/saca. Valor da parcela: 2.000 × R$ 150 = R$ 300.000.
5. Lançamento financeiro é criado em BRL com referência à cotação.
6. Arrendatário paga em BRL equivalente às sacas.
7. Histórico registra cotação aplicada.

## Casos Extremos e Exceções

- **Arrendamento de parte do imóvel:** `area_arrendada_ha` pode ser menor que a área total. Múltiplos contratos podem coexistir para o mesmo imóvel (áreas diferentes). Validação: soma das áreas arrendadas ≤ área total do imóvel.

- **Arrendatário externo (não é tenant):** Usar `Pessoa` cadastrada. Lançamentos são internos ao tenant do proprietário. Arrendatário não tem acesso ao sistema.

- **Valor em sacas:** Conversão para BRL no momento da geração do lançamento financeiro, usando cotação informada manualmente ou integração CEPEA/B3.

- **Rescisão antecipada:** Parcelas futuras canceladas. Lançamentos financeiros correspondentes cancelados automaticamente. Multa rescisória pode ser registrada como observação.

- **CCIR vencido:** Bloquear criação de novo contrato. Contratos existentes geram alerta mas continuam ativos. Mensagem: "CCIR vencido. Regularize antes de criar novo arrendamento."

- **Parceria com resultado negativo:** Resultado zero ou negativo não gera lançamento de receita. Registrar como informação histórica. Proprietário não recebe.

- **Índice de reajuste não disponível:** Se IGP-M não é divulgado no mês do reajuste, usar último índice disponível ou aguardar publicação. Sistema alerta usuário.

- **Arrendatário inadimplente:** Parcela vencida há mais de 30 dias gera alerta de inadimplência. Proprietário pode marcar parcela como "Em cobrança" e acionar jurídico.

- **Contrato verbal (sem PDF):** Permitido mas alertado como "informal". Sistema recomenda registro em cartório para validade jurídica.

- **Prorrogação automática:** Contrato que prevê prorrogação automática gera alerta T-60 dias para confirmação ou cancelamento.

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de contratos com tenant isolation testado.
- [ ] Geração automática de parcelas ao salvar contrato.
- [ ] Lançamentos financeiros previstos criados automaticamente no módulo Financeiro.
- [ ] Bloqueio de criação de contrato com CCIR vencido (alerta bloqueante).
- [ ] Alertas de vencimento de parcela (T-7 dias) e vencimento de contrato (T-60, T-30 dias).
- [ ] Alertas de reajuste anual (T-30 dias antes da data configurada).
- [ ] Upload de PDF do contrato com versionamento.
- [ ] Listagem de contratos com filtro por imóvel, status e período.
- [ ] Rescisão registra motivo e cancela parcelas futuras.
- [ ] Testes: criação, rescisão, geração de parcelas, integração financeiro.
- [ ] Cálculo de reajuste com índice configurável.
- [ ] Suporte a valor em sacas com conversão para BRL.
- [ ] Validação de prazo mínimo legal (3 anos agrícola, 5 anos misto).
- [ ] Histórico de reajustes registrado por contrato.

## Sugestões de Melhoria Futura

- **Template de contrato:** Gerar minuta de contrato em PDF a partir dos dados cadastrados. Cláusulas padrão personalizáveis.

- **Assinatura digital:** Integração com DocuSign ou Gov.br para assinatura eletrônica do contrato. Validade jurídica sem papel.

- **Integração cotações:** Converter valor em sacas para BRL automaticamente via cotação CEPEA/B3 em tempo real.

- **Dashboard de arrendamentos:** Visão consolidada de receitas por imóvel, área arrendada vs. própria, ticket médio por hectare.

- **Notificação ao arrendatário:** Enviar lembrete de vencimento por e-mail/WhatsApp para o arrendatário externo.

- **Cobrança automatizada:** Integração com gateway de pagamento para cobrança automática (débito automático, PIX recorrente).

- **Índices automáticos:** Consulta automática de IGP-M, IPCA via API IBGE/FGV para reajuste sem intervenção manual.

- **Rateio de despesas:** Despesas de benfeitorias (cercas, estradas) rateadas entre proprietário e arrendatário conforme contrato.

- **Renovação automática:** Fluxo de renovação de contrato com aceite eletrônico de ambas as partes.

- **Garantia de contrato:** Registro de garantias (fiador, seguro, caução) vinculadas ao contrato.

- **Vistoria de entrada/saída:** Checklist de vistoria do imóvel no início e fim do contrato. Registro fotográfico.
