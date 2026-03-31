# AgroSaaS - Módulos do Sistema

**Versão:** 1.0.0  
**Última Atualização:** 2026-03-31  
**Status:** Ativo  

---

## 📋 Índice

1. [Visão Geral dos Módulos](#1-visão-geral-dos-módulos)
2. [Módulo Core (Núcleo)](#2-módulo-core-núcleo)
3. [Módulo Agrícola (A1-A5)](#3-módulo-agrícola-a1-a5)
4. [Módulo Pecuária (P1-P4)](#4-módulo-pecuária-p1-p4)
5. [Módulo Financeiro (F1-F4)](#5-módulo-financeiro-f1-f4)
6. [Módulo Operacional (O1-O3)](#6-módulo-operacional-o1-o3)
7. [Módulo RH (RH1-RH2)](#7-módulo-rh-rh1-rh2)
8. [Módulo Ambiental (AM1-AM2)](#8-módulo-ambiental-am1-am2)
9. [Extensões Enterprise](#9-extensões-enterprise)
10. [Matriz de Integração](#10-matriz-de-integração)

---

## 1. Visão Geral dos Módulos

### Módulos Comercializáveis

| ID | Nome | Categoria | Preço Base | Status |
|----|------|-----------|------------|--------|
| **CORE** | Núcleo AgroSaaS | CORE | Incluso | ✅ Ativo |
| **A1_PLANEJAMENTO** | Planejamento de Safra | AGRICOLA | R$ 199/mês | ✅ Ativo |
| **A2_CAMPO** | Caderno de Campo | AGRICOLA | R$ 299/mês | ✅ Ativo |
| **A3_DEFENSIVOS** | Defensivos e Receituário | AGRICOLA | R$ 149/mês | ✅ Ativo |
| **A4_PRECISAO** | Agricultura de Precisão | AGRICOLA | R$ 499/mês | 🔄 Em desenvolvimento |
| **A5_COLHEITA** | Colheita e Romaneio | AGRICOLA | R$ 249/mês | ✅ Ativo |
| **P1_REBANHO** | Controle de Rebanho | PECUARIA | R$ 249/mês | ✅ Ativo |
| **P2_GENETICA** | Genética Reprodutiva | PECUARIA | R$ 349/mês | 🔄 Em desenvolvimento |
| **P3_CONFINAMENTO** | Feedlot Control | PECUARIA | R$ 399/mês | 🔄 Em desenvolvimento |
| **P4_LEITE** | Pecuária Leiteira | PECUARIA | R$ 299/mês | 🔄 Em desenvolvimento |
| **F1_TESOURARIA** | Tesouraria | FINANCEIRO | R$ 199/mês | ✅ Ativo |
| **F2_CUSTOS_ABC** | Custos ABC | FINANCEIRO | R$ 299/mês | 🔄 Em desenvolvimento |
| **F3_FISCAL** | Fiscal e Compliance | FINANCEIRO | R$ 449/mês | 🔄 Em desenvolvimento |
| **F4_HEDGING** | Hedging e Futuros | FINANCEIRO | R$ 599/mês | 📋 Planejado |
| **O1_FROTA** | Controle de Frota | OPERACIONAL | R$ 179/mês | ✅ Ativo |
| **O2_ESTOQUE** | Estoque Multi-armazéns | OPERACIONAL | R$ 199/mês | ✅ Ativo |
| **O3_COMPRAS** | Supply e Compras | OPERACIONAL | R$ 249/mês | ✅ Ativo |
| **RH1_REMUNERACAO** | Remuneração Rural | RH | R$ 199/mês | ✅ Ativo |
| **RH2_SEGURANCA** | Segurança do Trabalho | RH | R$ 149/mês | 📋 Planejado |
| **AM1_COMPLIANCE** | Compliance Ambiental | AMBIENTAL | R$ 299/mês | 📋 Planejado |
| **AM2_CARBONO** | Gestão de Carbono | AMBIENTAL | R$ 499/mês | 📋 Planejado |
| **EXT_IA** | IA Copilot Agrônoma | EXTENSAO | R$ 799/mês | 📋 Planejado |
| **EXT_IOT** | Integração IoT | EXTENSAO | R$ 599/mês | 📋 Planejado |
| **EXT_ERP** | Bridge ERP Corporativo | EXTENSAO | R$ 1299/mês | 📋 Planejado |

**📄 Ver:** `services/api/core/constants.py` para definições

---

## 2. Módulo Core (Núcleo)

**ID:** `CORE`  
**Categoria:** NUCLEO  
**Status:** ✅ Ativo (Obrigatório)  
**Preço:** Incluso em todos planos  

### Descrição

Módulo base que fornece infraestrutura para todos outros módulos:
- Multi-tenancy
- Autenticação e autorização (RBAC)
- Gestão de usuários e equipes
- Backoffice administrativo
- CRM e vendas
- Faturamento e billing
- Suporte técnico
- Base de conhecimento

### Principais Entidades

#### Core Models (`services/api/core/models/`)

| Tabela | Descrição |
|--------|-----------|
| `tenants` | Assinantes do SaaS |
| `tenants_usuarios` | Vínculo usuário-tenant |
| `usuarios` | Usuários da plataforma |
| `perfis_acesso` | Perfis de acesso (roles) |
| `fazendas` | Propriedades rurais |
| `grupos_fazendas` | Grupos de fazendas |
| `fazenda_usuarios` | Permissões por fazenda |
| `convites_acesso` | Convites para equipe |
| `planos_assinatura` | Planos comerciais |
| `assinaturas_tenant` | Assinaturas ativas |
| `faturas` | Faturas e cobranças |
| `admin_users` | Administradores do SaaS |
| `admin_audit_log` | Log de auditoria |
| `crm_leads` | Leads do CRM |
| `crm_ofertas` | Ofertas comerciais |
| `cupons` | Cupons de desconto |
| `support_chamados` | Chamados de suporte |
| `knowledge_base` | Base de conhecimento |

### Routers Core (`services/api/core/routers/`)

| Router | Endpoints Principais |
|--------|---------------------|
| `auth.py` | `/login`, `/register`, `/refresh`, `/logout` |
| `onboarding.py` | `/onboarding/complete`, `/onboarding/status` |
| `backoffice.py` | `/backoffice/dashboard`, `/backoffice/metrics` |
| `backoffice_tenants.py` | `/backoffice/tenants/*` |
| `backoffice_billing.py` | `/backoffice/billing/*` |
| `backoffice_crm.py` | `/backoffice/crm/*` |
| `team.py` | `/team/invites`, `/team/members` |
| `fazendas.py` | `/fazendas/*` |
| `grupos_fazendas.py` | `/grupos-fazendas/*` |
| `billing.py` | `/billing/invoices`, `/billing/subscription` |
| `plan_changes.py` | `/plan-changes/request`, `/plan-changes/history` |
| `cupons.py` | `/cupons/validate`, `/cupons/apply` |
| `support.py` | `/support/tickets`, `/support/messages` |
| `knowledge_base.py` | `/knowledge-base/articles` |
| `stripe_webhooks.py` | `/webhooks/stripe` |

### Dependências

- **Depende de:** Nenhum (é a base)
- **Dependem dele:** TODOS módulos

### Impacto de Mudanças

⚠️ **ALTO IMPACTO:** Qualquer alteração no CORE afeta todos módulos.

**Regras para modificar CORE:**
1. Sempre criar migration testada
2. Manter backward compatibility
3. Testar em todos ambientes
4. Documentar breaking changes

---

## 3. Módulo Agrícola (A1-A5)

### Visão Geral

| Submódulo | ID | Status | Preço |
|-----------|----|--------|-------|
| Planejamento | A1_PLANEJAMENTO | ✅ | R$ 199/mês |
| Caderno de Campo | A2_CAMPO | ✅ | R$ 299/mês |
| Defensivos | A3_DEFENSIVOS | ✅ | R$ 149/mês |
| Agricultura Precisão | A4_PRECISAO | 🔄 | R$ 499/mês |
| Colheita | A5_COLHEITA | ✅ | R$ 249/mês |

**Localização:** `services/api/agricola/`

---

### 3.1 A1_PLANEJAMENTO - Planejamento de Safra

**Path:** `services/api/agricola/a1_planejamento/`

#### Entidades

| Tabela | Descrição |
|--------|-----------|
| `safras` | Safras agrícolas (ciclos) |
| `safras_talhoes` | Associação safra-talhões |
| `safras_fases_historico` | Histórico de fases da safra |
| `orcamentos_safra` | Orçamentos de safra |

#### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/agricola/planejamento/safras` | Criar safra |
| GET | `/agricola/planejamento/safras` | Listar safras |
| GET | `/agricola/planejamento/safras/{id}` | Detalhes da safra |
| PATCH | `/agricola/planejamento/safras/{id}` | Atualizar safra |
| POST | `/agricola/planejamento/safras/{id}/avancar-fase` | Avançar fase |
| GET | `/agricola/planejamento/safras/{id}/resumo` | Resumo planejado vs realizado |

#### Regras de Negócio

- Safra tem ciclo de vida: `PLANEJADA` → `PREPARO_SOLO` → `PLANTIO` → `DESENVOLVIMENTO` → `COLHEITA` → `POS_COLHEITA` → `ENCERRADA`
- Não permitir safras com mesmo nome no tenant
- Transições de fase validadas
- Orçamento vinculado à safra

#### Dependências

- **Depende de:** CORE, Cadastros (talhoes)
- **Impacta:** F1_TESOURARIA (orçamento), A5_COLHEITA (comparação)

---

### 3.2 A2_CAMPO - Caderno de Campo

**Path:** `services/api/agricola/operacoes/`

#### Entidades

| Tabela | Descrição |
|--------|-----------|
| `operacoes_agricolas` | Operações de campo |
| `insumos_operacao` | Insumos usados em operações |
| `apontamentos` | Apontamentos de campo |

#### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/agricola/operacoes` | Registrar operação |
| GET | `/agricola/operacoes` | Listar operações |
| GET | `/agricola/operacoes/{id}` | Detalhes operação |
| PATCH | `/agricola/operacoes/{id}` | Atualizar operação |
| GET | `/agricola/operacoes/safra/{safra_id}/por-fase` | Operações por fase |
| GET | `/agricola/operacoes/export/pdf` | Exportar caderno PDF |

#### Regras de Negócio

- Operação gera baixa automática de estoque
- Operação calcula custos (mão de obra + insumos + máquinas)
- Validação de período de carência de defensivos
- Registro de condições climáticas no momento

#### Dependências

- **Depende de:** CORE, A1_PLANEJAMENTO, O2_ESTOQUE
- **Impacta:** F1_TESOURARIA (despesas), O2_ESTOQUE (baixa)

---

### 3.3 A3_DEFENSIVOS - Defensivos e Receituário

**Path:** `services/api/agricola/monitoramento/` + `services/api/agricola/prescricoes/`

#### Entidades

| Tabela | Descrição |
|--------|-----------|
| `monitoramentos_pragas` | Monitoramento de pragas |
| `monitoramento_catalogo` | Catálogo de pragas/doenças |
| `prescricoes` | Receituários agronômicos |

#### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/agricola/monitoramentos` | Criar monitoramento |
| GET | `/agricola/monitoramentos/safra/{safra_id}` | Listar por safra |
| POST | `/agricola/monitoramentos/diagnosticar-avulso` | Diagnóstico IA |
| GET | `/agricola/monitoramentos/catalogo` | Catálogo de pragas |
| POST | `/agricola/prescricoes` | Criar receituário |

#### Dependências

- **Depende de:** CORE, A2_CAMPO
- **Impacta:** A2_CAMPO (aplicações), O2_ESTOQUE (consumo)

---

### 3.4 A4_PRECISAO - Agricultura de Precisão

**Path:** `services/api/agricola/ndvi/` + `services/api/agricola/climatico/`

#### Entidades

| Tabela | Descrição |
|--------|-----------|
| `ndvi_imagens` | Imagens de satélite |
| `dados_climaticos` | Dados meteorológicos |
| `prescricoes_vra` | Prescrições taxa variável |

#### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/agricola/ndvi/talhoes/{talhao_id}` | NDVI por talhão |
| GET | `/agricola/climatico/talhoes/{talhao_id}` | Dados climáticos |
| POST | `/agricola/prescricoes/vra` | Criar prescrição VRA |

#### Dependências

- **Depende de:** CORE, A1_PLANEJAMENTO
- **Impacta:** A2_CAMPO (prescrições)

---

### 3.5 A5_COLHEITA - Colheita e Romaneio

**Path:** `services/api/agricola/romaneios/`

#### Entidades

| Tabela | Descrição |
|--------|-----------|
| `romaneios_colheita` | Romaneios de colheita |
| `romaneios_kpis` | KPIs de colheita |

#### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/agricola/romaneios` | Criar romaneio |
| GET | `/agricola/romaneios` | Listar romaneios |
| GET | `/agricola/romaneios/{id}` | Detalhes romaneio |
| PATCH | `/agricola/romaneios/{id}` | Atualizar romaneio |
| GET | `/agricola/romaneios/kpis` | KPIs de colheita |

#### Regras de Negócio

- Romaneio calcula produtividade (sc/ha)
- Romaneio gera receita no financeiro (opcional)
- Descontos por umidade, impureza, avariados
- Rastreabilidade completa (safra, talhão, máquina, operador)

#### Dependências

- **Depende de:** CORE, A1_PLANEJAMENTO
- **Impacta:** F1_TESOURARIA (receitas), A1_PLANEJAMENTO (realizado vs planejado)

---

### Outros Submódulos Agrícolas

| Submódulo | Path | Descrição |
|-----------|------|-----------|
| `safras` | `services/api/agricola/safras/` | Gestão de safras |
| `talhoes` | `services/api/agricola/talhoes/` | Gestão de talhões |
| `custos` | `services/api/agricola/custos/` | Custos agrícolas |
| `analises_solo` | `services/api/agricola/analises_solo/` | Análise de solo |
| `fenologia` | `services/api/agricola/fenologia/` | Fenologia da cultura |
| `beneficiamento` | `services/api/agricola/beneficiamento/` | Pós-colheita |
| `rastreabilidade` | `services/api/agricola/rastreabilidade/` | Rastreio completo |
| `agronomo` | `services/api/agricola/agronomo/` | Gestão de agrônomos |
| `checklist` | `services/api/agricola/checklist/` | Checklists operacionais |
| `dashboard` | `services/api/agricola/dashboard/` | Dashboard agrícola |

---

## 4. Módulo Pecuária (P1-P4)

### Visão Geral

| Submódulo | ID | Status | Preço |
|-----------|----|--------|-------|
| Rebanho | P1_REBANHO | ✅ | R$ 249/mês |
| Genética | P2_GENETICA | 🔄 | R$ 349/mês |
| Confinamento | P3_CONFINAMENTO | 🔄 | R$ 399/mês |
| Leite | P4_LEITE | 🔄 | R$ 299/mês |

**Localização:** `services/api/pecuaria/`

---

### 4.1 P1_REBANHO - Controle de Rebanho

**Path:** `services/api/pecuaria/`

#### Entidades

| Tabela | Descrição |
|--------|-----------|
| `lotes_animais` | Lotes de animais |
| `animais` | Animais individuais |
| `eventos_animais` | Eventos do animal (append-only) |
| `piquetes` | Piquetes/pastos |
| `manejos_lote` | Manejos de lote |

#### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/pecuaria/lotes-bovinos` | Listar lotes |
| POST | `/pecuaria/lotes-bovinos` | Criar lote |
| GET | `/pecuaria/manejos` | Listar eventos |
| POST | `/pecuaria/manejos` | Registrar evento |
| GET | `/pecuaria/piquetes` | Listar piquetes |
| POST | `/pecuaria/piquetes` | Criar piquete |

#### Regras de Negócio

- Eventos são append-only (histórico imutável)
- Categorias mudam automaticamente por idade
- Peso atual calculado da última pesagem
- Genealogia (pai, mãe) para animais individuais

#### Dependências

- **Depende de:** CORE, Cadastros (propriedades)
- **Impacta:** F1_TESOURARIA (vendas/compras), O2_ESTOQUE (consumo ração/medicamentos)

---

### 4.2 P2_GENETICA - Genética Reproditiva

**Path:** `services/api/pecuaria/` (em desenvolvimento)

#### Funcionalidades Planejadas

- IATF (Inseminação Artificial em Tempo Fixo)
- Diagnóstico de prenhez
- Genealogia completa
- DEPs (Diferenças Esperadas nas Progênies)
- Planejamento genético

---

### 4.3 P3_CONFINAMENTO - Feedlot Control

**Path:** `services/api/pecuaria/` (em desenvolvimento)

#### Funcionalidades Planejadas

- Fábrica de ração
- TMR (Total Mixed Ration)
- Controle de cochos
- Ganho de peso diário
- Conversão alimentar

---

### 4.4 P4_LEITE - Pecuária Leiteira

**Path:** `services/api/pecuaria/producao/`

#### Entidades

| Tabela | Descrição |
|--------|-----------|
| `producao_leite` | Produção leiteira diária |
| `qualidade_leite` | Qualidade (CCS, CBT, gordura, proteína) |

#### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/pecuaria/producao-leite` | Registrar produção |
| GET | `/pecuaria/producao-leite/vacas` | Produção por vaca |
| POST | `/pecuaria/qualidade-leite` | Registrar qualidade |

#### Dependências

- **Depende de:** CORE, P1_REBANHO
- **Impacta:** F1_TESOURARIA (receitas leite)

---

## 5. Módulo Financeiro (F1-F4)

### Visão Geral

| Submódulo | ID | Status | Preço |
|-----------|----|--------|-------|
| Tesouraria | F1_TESOURARIA | ✅ | R$ 199/mês |
| Custos ABC | F2_CUSTOS_ABC | 🔄 | R$ 299/mês |
| Fiscal | F3_FISCAL | 🔄 | R$ 449/mês |
| Hedging | F4_HEDGING | 📋 | R$ 599/mês |

**Localização:** `services/api/financeiro/`

---

### 5.1 F1_TESOURARIA - Tesouraria

**Path:** `services/api/financeiro/`

#### Entidades

| Tabela | Descrição |
|--------|-----------|
| `fin_receitas` | Contas a receber |
| `fin_despesas` | Contas a pagar |
| `fin_planos_conta` | Plano de contas hierárquico |
| `fin_rateios` | Rateio de custos |
| `fin_contas_bancarias` | Contas bancárias |
| `fin_lancamentos_bancarios` | Lançamentos bancários |
| `fin_conciliacoes` | Conciliação bancária |

#### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/financeiro/receitas` | Listar receitas |
| POST | `/financeiro/receitas` | Criar receita |
| GET | `/financeiro/receitas/vencendo` | Receitas vencendo |
| PATCH | `/financeiro/receitas/{id}` | Atualizar receita |
| GET | `/financeiro/despesas` | Listar despesas |
| POST | `/financeiro/despesas` | Criar despesa |
| POST | `/financeiro/despesas/{id}/parcelar` | Parcelar despesa |
| GET | `/financeiro/planos-conta` | Plano de contas |
| POST | `/financeiro/rateios` | Criar rateio |
| GET | `/financeiro/relatorios` | Relatórios financeiros |

#### Regras de Negócio

- Status automático: `A_PAGAR` → `PAGO` / `ATRASADO`
- Parcelamento de despesas e receitas
- Rateio de custos por centro de custo (safra, talhão, lote)
- Conciliação bancária
- Livro Caixa (RFB) para produtor rural

#### Dependências

- **Depende de:** CORE
- **Impacta:** Nenhum (é folha final)
- **Recebe dados de:** A5_COLHEITA (receitas), A2_CAMPO (despesas), P1_REBANHO (vendas/compras), O1_FROTA (manutenção), O2_ESTOQUE (compras)

---

### 5.2 F2_CUSTOS_ABC - Custos ABC

**Path:** `services/api/financeiro/` (em desenvolvimento)

#### Funcionalidades Planejadas

- Rateio automático de custos indiretos
- Centros de custo múltiplos
- Margem de contribuição por safra/talhão/lote
- Custeio baseado em atividades (ABC)

---

### 5.3 F3_FISCAL - Fiscal e Compliance

**Path:** `services/api/financeiro/` (em desenvolvimento)

#### Funcionalidades Planejadas

- NF-e (Nota Fiscal Eletrônica)
- MDFe (Manifesto de Documentos Fiscais)
- LCDPR (Livro Caixa Digital)
- SPED Rural
- GPS/DARF (previdência rural)

---

### 5.4 F4_HEDGING - Hedging e Futuros

**Path:** `services/api/financeiro/` (planejado)

#### Funcionalidades Planejadas

- Contratos futuros B3
- Barter (troca de commodity)
- Proteção de preço
- Fixação de preços

---

## 6. Módulo Operacional (O1-O3)

### Visão Geral

| Submódulo | ID | Status | Preço |
|-----------|----|--------|-------|
| Frota | O1_FROTA | ✅ | R$ 179/mês |
| Estoque | O2_ESTOQUE | ✅ | R$ 199/mês |
| Compras | O3_COMPRAS | ✅ | R$ 249/mês |

**Localização:** `services/api/operacional/`

---

### 6.1 O1_FROTA - Controle de Frota

**Path:** `services/api/operacional/`

#### Entidades

| Tabela | Descrição |
|--------|-----------|
| `frota_equipamentos` | Equipamentos e máquinas |
| `frota_planos_manutencao` | Planos de manutenção |
| `frota_ordens_servico` | Ordens de serviço |
| `frota_itens_os` | Itens usados em OS |
| `frota_registros_manutencao` | Histórico de manutenções |
| `apontamentos_uso` | Apontamentos de uso |

#### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/operacional/frota` | Cadastrar equipamento |
| GET | `/operacional/frota` | Listar frota |
| POST | `/operacional/frota/planos` | Criar plano manutenção |
| POST | `/operacional/frota/os` | Abrir OS |
| POST | `/operacional/frota/os/{os_id}/itens` | Adicionar itens à OS |
| PATCH | `/operacional/frota/os/{os_id}/fechar` | Fechar OS |

#### Regras de Negócio

- Manutenção preventiva por horas/km
- OS gera baixa de estoque de peças
- OS gera despesa no financeiro
- Histórico completo de manutenções

#### Dependências

- **Depende de:** CORE, O2_ESTOQUE
- **Impacta:** F1_TESOURARIA (despesas), O2_ESTOQUE (peças), A2_CAMPO (máquinas em uso)

---

### 6.2 O2_ESTOQUE - Estoque Multi-armazéns

**Path:** `services/api/operacional/`

#### Entidades

| Tabela | Descrição |
|--------|-----------|
| `estoque_depositos` | Depósitos/armazéns |
| `estoque_lotes` | Lotes de produtos |
| `estoque_saldos` | Saldos atuais |
| `estoque_movimentacoes` | Histórico de movimentações |
| `estoque_requisicoes` | Requisições de material |
| `estoque_itens_requisicao` | Itens da requisição |
| `estoque_reservas` | Reservas de estoque |

#### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/operacional/estoque/lotes` | Listar lotes |
| POST | `/operacional/estoque/lotes` | Criar lote |
| GET | `/operacional/estoque/lotes/alertas-validade` | Alertas de validade |
| GET | `/operacional/estoque/depositos` | Listar depósitos |
| GET | `/operacional/estoque/saldos` | Saldos atuais |
| GET | `/operacional/estoque/alertas` | Alertas de estoque mínimo |
| POST | `/operacional/estoque/movimentacoes/entrada` | Entrada de estoque |
| POST | `/operacional/estoque/movimentacoes/saida` | Saída de estoque |
| POST | `/operacional/estoque/movimentacoes/transferencia` | Transferência |
| POST | `/operacional/estoque/movimentacoes/ajuste` | Ajuste de inventário |
| POST | `/operacional/estoque/requisicoes` | Criar requisição |
| PATCH | `/operacional/estoque/requisicoes/{id}/aprovar` | Aprovar requisição |
| POST | `/operacional/estoque/reservas` | Criar reserva |
| PATCH | `/operacional/estoque/reservas/{id}/consumir` | Consumir reserva |

#### Regras de Negócio

- Rastreabilidade por lote (validade)
- Múltiplos depósitos
- Reservas para OS/pedidos
- Requisições com aprovação
- Alertas de estoque mínimo e validade

#### Dependências

- **Depende de:** CORE, Cadastros (produtos)
- **Impacta:** A2_CAMPO (insumos), O1_FROTA (peças), P1_REBANHO (ração/medicamentos), F1_TESOURARIA (compras)

---

### 6.3 O3_COMPRAS - Supply e Compras

**Path:** `services/api/operacional/`

#### Entidades

| Tabela | Descrição |
|--------|-----------|
| `compras_pedidos` | Pedidos de compra |
| `compras_cotacoes` | Cotações com fornecedores |
| `compras_itens_pedido` | Itens do pedido |

#### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/operacional/pedidos-compra` | Criar pedido |
| GET | `/operacional/pedidos-compra` | Listar pedidos |
| PATCH | `/operacional/pedidos-compra/{id}/cotacao` | Adicionar cotação |
| PATCH | `/operacional/pedidos-compra/{id}/aprovar` | Aprovar pedido |
| POST | `/operacional/pedidos-compra/{id}/receber` | Receber pedido |

#### Dependências

- **Depende de:** CORE, O2_ESTOQUE, Cadastros (fornecedores)
- **Impacta:** O2_ESTOQUE (entrada), F1_TESOURARIA (despesas)

---

## 7. Módulo RH (RH1-RH2)

### Visão Geral

| Submódulo | ID | Status | Preço |
|-----------|----|--------|-------|
| Remuneração | RH1_REMUNERACAO | ✅ | R$ 199/mês |
| Segurança | RH2_SEGURANCA | 📋 | R$ 149/mês |

**Localização:** `services/api/rh/`

---

### 7.1 RH1_REMUNERACAO - Remuneração Rural

**Path:** `services/api/rh/`

#### Entidades

| Tabela | Descrição |
|--------|-----------|
| `rh_colaboradores` | Colaboradores |
| `rh_lancamento_diarias` | Lançamento de diárias |
| `rh_empreitadas` | Empreitadas |
| `rh_pagamento_producao` | Pagamento por produção |

#### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/rh/colaboradores` | Cadastrar colaborador |
| GET | `/rh/colaboradores` | Listar colaboradores |
| POST | `/rh/diarias` | Lançar diárias |
| POST | `/rh/empreitadas` | Criar empreitada |
| POST | `/rh/pagamento-producao` | Lançar produção |

#### Dependências

- **Depende de:** CORE
- **Impacta:** F1_TESOURARIA (pagamentos)

---

### 7.2 RH2_SEGURANCA - Segurança do Trabalho

**Path:** `services/api/rh/` (planejado)

#### Funcionalidades Planejadas

- EPIs (Equipamentos de Proteção Individual)
- EPCs (Equipamentos de Proteção Coletiva)
- PPP (Perfil Profissiográfico Previdenciário)
- PCMSO (Programa de Controle Médico de Saúde Ocupacional)
- NR-31 compliance

---

## 8. Módulo Ambiental (AM1-AM2)

### Visão Geral

| Submódulo | ID | Status | Preço |
|-----------|----|--------|-------|
| Compliance | AM1_COMPLIANCE | 📋 | R$ 299/mês |
| Carbono | AM2_CARBONO | 📋 | R$ 499/mês |

---

### 8.1 AM1_COMPLIANCE - Compliance Ambiental

**Path:** `services/api/ambiental/` (planejado)

#### Funcionalidades Planejadas

- CAR (Cadastro Ambiental Rural)
- CCIR (Certificado de Cadastro de Imóvel Rural)
- Outorgas hídricas
- APP (Área de Preservação Permanente)
- RL (Reserva Legal)

---

### 8.2 AM2_CARBONO - Gestão de Carbono

**Path:** `services/api/ambiental/` (planejado)

#### Funcionalidades Planejadas

- MRV (Monitoramento, Reporte e Verificação)
- Pegada de carbono
- Créditos de carbono
- Relatórios de sustentabilidade

---

## 9. Extensões Enterprise

### Visão Geral

| Extensão | ID | Status | Preço |
|----------|----|--------|-------|
| IA Copilot | EXT_IA | 📋 | R$ 799/mês |
| IoT | EXT_IOT | 📋 | R$ 599/mês |
| ERP Bridge | EXT_ERP | 📋 | R$ 1299/mês |

---

### 9.1 EXT_IA - IA Copilot Agrônoma

**Path:** `services/api/ia/` (planejado)

#### Funcionalidades Planejadas

- LLM treinado em agronomia
- Diagnóstico de pragas/doenças via imagem
- Recomendações baseadas em EMBRAPA
- Alertas preditivos

---

### 9.2 EXT_IOT - Integração IoT

**Path:** `services/api/iot/` (planejado)

#### Funcionalidades Planejadas

- John Deere Ops Center
- Balanças inteligentes
- Sensores de solo
- Estações meteorológicas

---

### 9.3 EXT_ERP - Bridge ERP Corporativo

**Path:** `services/api/integrations/` (planejado)

#### Funcionalidades Planejadas

- SAP integration
- Datasul integration
- Open Banking
- Power BI embedded

---

## 10. Matriz de Integração

### Fluxo de Dados entre Módulos

```
┌─────────────────────────────────────────────────────────────────┐
│                        FINANCEIRO (F1)                          │
│  ←────────────────────────────────────────────────────────→     │
│  Receitas: Romaneios (A5), Venda Animais (P1), Leite (P4)       │
│  Despesas: Operações (A2), Manutenção (O1), Compras (O3), RH    │
│  Rateios: Safras (A1), Talhões, Lotes Animais (P1)              │
└─────────────────────────────────────────────────────────────────┘
          ▲                          ▲
          │                          │
          │                          │
┌─────────┴──────────┐    ┌──────────┴──────────────────────────┐
│   AGRICOLA (A1-A5) │    │        PECUARIA (P1-P4)             │
│  → Planejamento    │    │  → Lotes de animais                 │
│  → Operações       │    │  → Eventos (nascimento, venda)      │
│  → Romaneios       │    │  → Pesagens                         │
│  → Insumos         │    │  → Produção Leite                   │
└─────────┬──────────┘    └──────────┬──────────────────────────┘
          │                          │
          │ Consomem                 │ Consomem
          ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OPERACIONAL (O1-O3)                         │
│  → Estoque: fornece insumos, peças, ração, medicamentos         │
│  → Frota: máquinas para operações agrícolas                     │
│  → Compras: abastece estoque                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Tabela de Dependências

| Módulo | Depende De | Impacta |
|--------|------------|---------|
| **A1_PLANEJAMENTO** | CORE | F1, A5 |
| **A2_CAMPO** | CORE, A1, O2 | F1, O2 |
| **A3_DEFENSIVOS** | CORE, A2 | A2, O2 |
| **A4_PRECISAO** | CORE, A1 | A2 |
| **A5_COLHEITA** | CORE, A1 | F1, A1 |
| **P1_REBANHO** | CORE | F1, O2 |
| **P4_LEITE** | CORE, P1 | F1 |
| **F1_TESOURARIA** | CORE | Nenhum |
| **O1_FROTA** | CORE, O2 | F1, O2, A2 |
| **O2_ESTOQUE** | CORE | A2, O1, P1, F1 |
| **O3_COMPRAS** | CORE, O2 | O2, F1 |
| **RH1_REMUNERACAO** | CORE | F1 |

---

## Referências Cruzadas

| Documento | Descrição |
|-----------|-----------|
| `docs/qwen/01-arquitetura.md` | Arquitetura geral do sistema |
| `docs/qwen/03-banco-dados.md` | Schema completo do banco |
| `docs/qwen/05-api.md` | API reference completa |
| `docs/qwen/06-permissoes.md` | Catálogo de permissões e roles |

---

## Changelog

| Data | Versão | Descrição |
|------|--------|-----------|
| 2026-03-31 | 1.0.0 | Documentação inicial completa |
