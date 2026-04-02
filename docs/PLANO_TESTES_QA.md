# 🧪 Plano de Testes QA - AgroSaaS

**Versão:** 1.0.0
**Data:** 2026-03-31
**Status:** ✅ Aprovado para execução

---

## 📋 Índice

1. [Visão Geral](#1-visão-geral)
2. [Estratégia de Testes](#2-estratégia-de-testes)
3. [Testes por Módulo](#3-testes-por-módulo)
   - [3.1 Módulo Core](#31-módulo-core)
   - [3.2 Módulo Agrícola](#32-módulo-agrícola)
   - [3.3 Módulo Pecuária](#33-módulo-pecuária)
   - [3.4 Módulo Financeiro](#34-módulo-financeiro)
   - [3.5 Módulo Operacional](#35-módulo-operacional)
   - [3.6 Módulo RH](#36-módulo-rh)
   - [3.7 Módulo Ambiental](#37-módulo-ambiental)
   - [3.8 Cadastros](#38-cadastros)
   - [3.9 Backoffice](#39-backoffice)
4. [Testes de Integração](#4-testes-de-integração)
5. [Testes E2E](#5-testes-e2e)
6. [Testes de Performance](#6-testes-de-performance)
7. [Testes de Segurança](#7-testes-de-segurança)
8. [Critérios de Aceite](#8-critérios-de-aceite)
9. [Matriz de Rastreabilidade](#9-matriz-de-rastreabilidade)

---

## 1. Visão Geral

### Objetivos do Plano de Testes

- ✅ Validar funcionalidades de todos os módulos
- ✅ Garantir integração entre módulos
- ✅ Assegurar qualidade do produto
- ✅ Prevenir regressões
- ✅ Documentar cenários de teste

### Escopo

| Módulo | Status | Prioridade |
|--------|--------|------------|
| Core | ✅ Ativo | 🔴 Crítica |
| Agrícola | ✅ Ativo | 🔴 Crítica |
| Financeiro | 🟡 Parcial | 🔴 Crítica |
| Operacional | ✅ Ativo | 🟡 Alta |
| Pecuária | ✅ Ativo | 🟡 Alta |
| RH | ✅ Ativo | 🟢 Média |
| Ambiental | 📋 Planejado | 🟢 Baixa |
| Backoffice | ✅ Ativo | 🔴 Crítica |

### Tipos de Testes

| Tipo | Ferramenta | Responsável | Frequência |
|------|------------|-------------|------------|
| Unitários | pytest | Devs | PR |
| Integração | pytest + httpx | Devs | PR |
| E2E | Playwright | QA | Sprint |
| Performance | k6/Locust | QA | Release |
| Segurança | OWASP ZAP | QA | Release |

---

## 2. Estratégia de Testes

### Pirâmide de Testes

```
          /\
         /  \   E2E (10%)
        /____\
       /      \  Integração (20%)
      /________\
     /          \ Unitários (70%)
    /____________\
```

### Definição de Pronto (DoD)

- ✅ Testes unitários com coverage > 80%
- ✅ Testes de integração passando
- ✅ Testes E2E críticos passando
- ✅ Sem bugs críticos/altos abertos
- ✅ Performance dentro do SLA (< 500ms)

### Ambiente de Testes

| Ambiente | URL | Finalidade |
|----------|-----|------------|
| Local | localhost:8000, localhost:3000 | Desenvolvimento |
| QA | qa-api.agrosaas.com.br | Testes automatizados |
| Staging | staging-api.agrosaas.com.br | Validação pré-produção |
| Produção | api.agrosaas.com.br | Monitoramento |

---

## 3. Testes por Módulo

### 3.1 Módulo Core

**Path:** `services/api/core/`

#### 3.1.1 Autenticação e Autorização

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| CORE-AUTH-01 | Login com credenciais válidas | Unitário | 🔴 | ⏳ |
| CORE-AUTH-02 | Login com email inválido | Unitário | 🔴 | ⏳ |
| CORE-AUTH-03 | Login com senha inválida | Unitário | 🔴 | ⏳ |
| CORE-AUTH-04 | Refresh token válido | Unitário | 🔴 | ⏳ |
| CORE-AUTH-05 | Refresh token expirado | Unitário | 🔴 | ⏳ |
| CORE-AUTH-06 | Logout invalida token | Unitário | 🟡 | ⏳ |
| CORE-AUTH-07 | Registro de novo usuário | Unitário | 🔴 | ⏳ |
| CORE-AUTH-08 | Registro com email duplicado | Unitário | 🔴 | ⏳ |
| CORE-AUTH-09 | Acesso sem token retorna 401 | Integração | 🔴 | ⏳ |
| CORE-AUTH-10 | Token expirado retorna 401 | Integração | 🔴 | ⏳ |

**Critérios de Aceite:**
- JWT gerado corretamente
- Refresh token funciona por 7 dias
- Blacklist de tokens funciona
- Senha hash com bcrypt

---

#### 3.1.2 Multi-tenancy

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| CORE-TEN-01 | Usuário vê apenas dados do seu tenant | Integração | 🔴 | ⏳ |
| CORE-TEN-02 | Tenant A não acessa dados do Tenant B | Integração | 🔴 | ⏳ |
| CORE-TEN-03 | Seleção de tenant ativo funciona | Integração | 🔴 | ⏳ |
| CORE-TEN-04 | Listar múltiplos tenants do usuário | Integração | 🟡 | ⏳ |
| CORE-TEN-05 | Criação de tenant com plano | Unitário | 🟡 | ⏳ |

**Critérios de Aceite:**
- Isolamento total entre tenants
- X-Tenant-ID header obrigatório
- Query filters aplicam tenant_id automaticamente

---

#### 3.1.3 RBAC e Permissões

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| CORE-RBAC-01 | Admin acessa todos endpoints | Integração | 🔴 | ⏳ |
| CORE-RBAC-02 | Viewer não cria recursos | Integração | 🔴 | ⏳ |
| CORE-RBAC-03 | Permissão específica bloqueia acesso | Integração | 🔴 | ⏳ |
| CORE-RBAC-04 | Role customizada com permissões parciais | Integração | 🟡 | ⏳ |
| CORE-RBAC-05 | Permissão por fazenda funciona | Integração | 🟡 | ⏳ |

**Critérios de Aceite:**
- 403 para sem permissão
- 404 para recursos de outra fazenda
- Permissões hierárquicas funcionam

---

#### 3.1.4 Gestão de Usuários e Convites

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| CORE-USR-01 | Enviar convite por email | Integração | 🟡 | ⏳ |
| CORE-USR-02 | Aceitar convite com token válido | Integração | 🟡 | ⏳ |
| CORE-USR-03 | Aceitar convite com token expirado | Unitário | 🟡 | ⏳ |
| CORE-USR-04 | Listar membros do tenant | Integração | 🟡 | ⏳ |
| CORE-USR-05 | Remover membro do tenant | Integração | 🟡 | ⏳ |
| CORE-USR-06 | Atualizar perfil de usuário | Integração | 🟡 | ⏳ |

---

#### 3.1.5 Fazendas e Grupos

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| CORE-FAZ-01 | Criar fazenda com geometria | Integração | 🔴 | ⏳ |
| CORE-FAZ-02 | Listar fazendas do tenant | Integração | 🔴 | ⏳ |
| CORE-FAZ-03 | Atualizar fazenda | Integração | 🟡 | ⏳ |
| CORE-FAZ-04 | Deletar fazenda com dependências | Unitário | 🟡 | ⏳ |
| CORE-FAZ-05 | Criar grupo de fazendas | Integração | 🟡 | ⏳ |
| CORE-FAZ-06 | Adicionar fazenda ao grupo | Integração | 🟡 | ⏳ |
| CORE-FAZ-07 | Geometria inválida retorna erro | Unitário | 🟡 | ⏳ |

---

#### 3.1.6 Billing e Assinaturas

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| CORE-BIL-01 | Criar assinatura com Stripe | Integração | 🔴 | ⏳ |
| CORE-BIL-02 | Webhook de pagamento funciona | Integração | 🔴 | ⏳ |
| CORE-BIL-03 | Fatura gerada corretamente | Integração | 🟡 | ⏳ |
| CORE-BIL-04 | Upgrade de plano funciona | Integração | 🟡 | ⏳ |
| CORE-BIL-05 | Downgrade de plano funciona | Integração | 🟡 | ⏳ |
| CORE-BIL-06 | Cupom de desconto aplica | Integração | 🟡 | ⏳ |
| CORE-BIL-07 | Cupom expirado não aplica | Unitário | 🟡 | ⏳ |
| CORE-BIL-08 | Cancelamento de assinatura | Integração | 🟡 | ⏳ |

---

#### 3.1.7 CRM e Leads

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| CORE-CRM-01 | Criar lead | Integração | 🟡 | ⏳ |
| CORE-CRM-02 | Atualizar status do lead | Integração | 🟡 | ⏳ |
| CORE-CRM-03 | Converter lead em tenant | Integração | 🟡 | ⏳ |
| CORE-CRM-04 | Criar oferta comercial | Integração | 🟢 | ⏳ |
| CORE-CRM-05 | Pipeline de vendas | Integração | 🟢 | ⏳ |

---

#### 3.1.8 Suporte Técnico

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| CORE-SUP-01 | Criar chamado de suporte | Integração | 🟡 | ⏳ |
| CORE-SUP-02 | Adicionar mensagem ao chamado | Integração | 🟡 | ⏳ |
| CORE-SUP-03 | Listar chamados do tenant | Integração | 🟡 | ⏳ |
| CORE-SUP-04 | Alterar status do chamado | Integração | 🟢 | ⏳ |
| CORE-SUP-05 | Base de conhecimento busca | Integração | 🟢 | ⏳ |

---

### 3.2 Módulo Agrícola

**Path:** `services/api/agricola/`

#### 3.2.1 A1_PLANEJAMENTO - Safras

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| AGR-SAF-01 | Criar safra com dados válidos | Integração | 🔴 | ⏳ |
| AGR-SAF-02 | Safra com nome duplicado retorna erro | Unitário | 🔴 | ⏳ |
| AGR-SAF-03 | Listar safras com filtros | Integração | 🔴 | ⏳ |
| AGR-SAF-04 | Atualizar safra | Integração | 🟡 | ⏳ |
| AGR-SAF-05 | Avançar fase da safra | Integração | 🔴 | ⏳ |
| AGR-SAF-06 | Avançar fase inválida retorna erro | Unitário | 🔴 | ⏳ |
| AGR-SAF-07 | Resumo da safra (planejado vs realizado) | Integração | 🟡 | ⏳ |
| AGR-SAF-08 | Safra com ciclo de vida completo | E2E | 🟡 | ⏳ |
| AGR-SAF-09 | Orçamento de safra | Integração | 🟡 | ⏳ |
| AGR-SAF-10 | Safra encerrada não permite operações | Unitário | 🟡 | ⏳ |

**Critérios de Aceite:**
- Fases: PLANEJADA → PREPARO_SOLO → PLANTIO → DESENVOLVIMENTO → COLHEITA → POS_COLHEITA → ENCERRADA
- Validação de transição de fases
- Hectares não ultrapassam área do talhão

---

#### 3.2.2 A2_CAMPO - Operações Agrícolas

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| AGR-OPR-01 | Registrar operação agrícola | Integração | 🔴 | ⏳ |
| AGR-OPR-02 | Operação em fase incompatível retorna erro | Unitário | 🔴 | ⏳ |
| AGR-OPR-03 | Operação gera baixa de estoque | Integração | 🔴 | ⏳ |
| AGR-OPR-04 | Operação calcula custos (MO + insumos + máquinas) | Unitário | 🔴 | ⏳ |
| AGR-OPR-05 | Operação sem insumos funciona | Unitário | 🟡 | ⏳ |
| AGR-OPR-06 | Listar operações por safra/fase | Integração | 🟡 | ⏳ |
| AGR-OPR-07 | Atualizar operação | Integração | 🟡 | ⏳ |
| AGR-OPR-08 | Deletar operação com baixa de estoque | Unitário | 🟡 | ⏳ |
| AGR-OPR-09 | Operação com data futura retorna erro | Unitário | 🟡 | ⏳ |
| AGR-OPR-10 | Exportar caderno de campo (PDF) | E2E | 🟢 | ⏳ |
| AGR-OPR-11 | Período de carência validado | Unitário | 🔴 | ⏳ |
| AGR-OPR-12 | Condições climáticas registradas | Unitário | 🟢 | ⏳ |

**Critérios de Aceite:**
- Baixa de estoque automática
- Cálculo de custos preciso
- Validação de período de carência
- Append-only para rastreabilidade

---

#### 3.2.3 A3_DEFENSIVOS - Monitoramento

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| AGR-MON-01 | Criar monitoramento de praga | Integração | 🟡 | ⏳ |
| AGR-MON-02 | Monitoramento com NDE ultrapassado | Unitário | 🟡 | ⏳ |
| AGR-MON-03 | Catálogo de pragas consulta | Integração | 🟢 | ⏳ |
| AGR-MON-04 | Diagnóstico por IA (avulso) | Integração | 🟡 | ⏳ |
| AGR-MON-05 | Criar prescrição (receituário) | Integração | 🟡 | ⏳ |
| AGR-MON-06 | Prescrição com responsável técnico | Unitário | 🟡 | ⏳ |
| AGR-MON-07 | Listar monitoramentos por safra | Integração | 🟡 | ⏳ |

---

#### 3.2.4 A4_PRECISAO - NDVI e Clima

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| AGR-NDV-01 | Buscar NDVI por talhão | Integração | 🟡 | ⏳ |
| AGR-NDV-02 | NDVI com data range | Integração | 🟢 | ⏳ |
| AGR-NDV-03 | Dados climáticos por talhão | Integração | 🟡 | ⏳ |
| AGR-NDV-04 | Alerta de geada | Integração | 🟡 | ⏳ |
| AGR-NDV-05 | Prescrição VRA (taxa variável) | E2E | 🟢 | ⏳ |

---

#### 3.2.5 A5_COLHEITA - Romaneios

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| AGR-ROM-01 | Criar romaneio de colheita | Integração | 🔴 | ⏳ |
| AGR-ROM-02 | Romaneio calcula sacas (MAPA) | Unitário | 🔴 | ⏳ |
| AGR-ROM-03 | Romaneio com descontos (umidade, impureza) | Unitário | 🔴 | ⏳ |
| AGR-ROM-04 | Romaneio gera receita automática | Integração | 🔴 | ⏳ |
| AGR-ROM-05 | Romaneio sem preço não gera receita | Unitário | 🔴 | ⏳ |
| AGR-ROM-06 | KPIs de colheita (produtividade) | Integração | 🟡 | ⏳ |
| AGR-ROM-07 | Listar romaneios por safra | Integração | 🟡 | ⏳ |
| AGR-ROM-08 | Atualizar romaneio | Integração | 🟡 | ⏳ |
| AGR-ROM-09 | Rastreabilidade completa | E2E | 🟡 | ⏳ |
| AGR-ROM-10 | Romaneio com destino ARMAZÉM | Unitário | 🟡 | ⏳ |
| AGR-ROM-11 | Romaneio com destino VENDA DIRETA | Unitário | 🟡 | ⏳ |

**Critérios de Aceite:**
- Cálculo: Sacas = Peso Líquido / 60
- Descontos aplicados corretamente
- Receita gerada automaticamente no financeiro
- Rastreabilidade: safra, talhão, máquina, operador

---

### 3.3 Módulo Pecuária

**Path:** `services/api/pecuaria/`

#### 3.3.1 P1_REBANHO - Lotes e Animais

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| PEC-LOT-01 | Criar lote de animais | Integração | 🟡 | ⏳ |
| PEC-LOT-02 | Listar lotes com filtros | Integração | 🟡 | ⏳ |
| PEC-LOT-03 | Atualizar lote | Integração | 🟢 | ⏳ |
| PEC-LOT-04 | Lote com categoria inválida retorna erro | Unitário | 🟡 | ⏳ |
| PEC-ANI-01 | Cadastrar animal individual | Integração | 🟡 | ⏳ |
| PEC-ANI-02 | Animal com brinco duplicado retorna erro | Unitário | 🟡 | ⏳ |
| PEC-ANI-03 | Genealogia (pai, mãe) | Integração | 🟢 | ⏳ |
| PEC-EVT-01 | Registrar evento (pesagem, vacinação) | Integração | 🔴 | ⏳ |
| PEC-EVT-02 | Eventos são append-only | Unitário | 🔴 | ⏳ |
| PEC-EVT-03 | Listar eventos por animal | Integração | 🟡 | ⏳ |
| PEC-EVT-04 | Categoria muda por idade | Unitário | 🟡 | ⏳ |
| PEC-PIQ-01 | Criar piquete | Integração | 🟢 | ⏳ |
| PEC-PIQ-02 | Lotação de piquete | Unitário | 🟢 | ⏳ |

---

#### 3.3.2 P4_LEITE - Produção Leiteira

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| PEC-LEI-01 | Registrar produção de leite | Integração | 🟡 | ⏳ |
| PEC-LEI-02 | Produção por vaca | Integração | 🟢 | ⏳ |
| PEC-LEI-03 | Qualidade do leite (CCS, CBT) | Integração | 🟡 | ⏳ |
| PEC-LEI-04 | Produção gera receita | Integração | 🟡 | ⏳ |
| PEC-LEI-05 | Curva de lactação | E2E | 🟢 | ⏳ |

---

### 3.4 Módulo Financeiro

**Path:** `services/api/financeiro/`

#### 3.4.1 F1_TESOURARIA - Receitas

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| FIN-REC-01 | Criar receita | Integração | 🔴 | ⏳ |
| FIN-REC-02 | Receita com origem (romaneio) | Integração | 🔴 | ⏳ |
| FIN-REC-03 | Parcelar receita | Integração | 🟡 | ⏳ |
| FIN-REC-04 | Receitas vencendo | Integração | 🟡 | ⏳ |
| FIN-REC-05 | Atualizar receita | Integração | 🟡 | ⏳ |
| FIN-REC-06 | Baixar receita (recebida) | Integração | 🟡 | ⏳ |
| FIN-REC-07 | Estornar receita | Unitário | 🟡 | ⏳ |
| FIN-REC-08 | Listar receitas por status | Integração | 🟡 | ⏳ |

---

#### 3.4.2 F1_TESOURARIA - Despesas

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| FIN-DES-01 | Criar despesa | Integração | 🔴 | ⏳ |
| FIN-DES-02 | Despesa com origem (operação) | Integração | 🔴 | ⏳ |
| FIN-DES-03 | Despesa sem custo não cria | Unitário | 🔴 | ⏳ |
| FIN-DES-04 | Parcelar despesa | Integração | 🟡 | ⏳ |
| FIN-DES-05 | Despesas vencendo | Integração | 🟡 | ⏳ |
| FIN-DES-06 | Atualizar despesa | Integração | 🟡 | ⏳ |
| FIN-DES-07 | Baixar despesa (paga) | Integração | 🟡 | ⏳ |
| FIN-DES-08 | Estornar despesa | Unitário | 🟡 | ⏳ |
| FIN-DES-09 | Despesa com rateios múltiplos | Integração | 🟡 | ⏳ |
| FIN-DES-10 | Rateio valida 100% | Unitário | 🟡 | ⏳ |

---

#### 3.4.3 F1_TESOURARIA - Plano de Contas

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| FIN-PLC-01 | Criar plano de contas hierárquico | Integração | 🟡 | ⏳ |
| FIN-PLC-02 | Plano de contas com pai inválido | Unitário | 🟡 | ⏳ |
| FIN-PLC-03 | Listar plano de contas (árvore) | Integração | 🟡 | ⏳ |
| FIN-PLC-04 | Categoria RFB válida | Unitário | 🟡 | ⏳ |
| FIN-PLC-05 | Conta analítica não tem filhos | Unitário | 🟡 | ⏳ |

---

#### 3.4.4 F1_TESOURARIA - Conciliação Bancária

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| FIN-CON-01 | Importar extrato OFX | Integração | 🟡 | ⏳ |
| FIN-CON-02 | Parse de OFX | Unitário | 🟡 | ⏳ |
| FIN-CON-03 | Casamento automático | Integração | 🟡 | ⏳ |
| FIN-CON-04 | Conciliação manual | Integração | 🟢 | ⏳ |
| FIN-CON-05 | Extrato com duplicidade | Unitário | 🟡 | ⏳ |

---

#### 3.4.5 F1_TESOURARIA - Relatórios

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| FIN-REL-01 | Balancete por mês/ano | Integração | 🟡 | ⏳ |
| FIN-REL-02 | DRE (Demonstrativo de Resultado) | Integração | 🟡 | ⏳ |
| FIN-REL-03 | Fluxo de caixa | Integração | 🟡 | ⏳ |
| FIN-REL-04 | Livro Caixa (RFB) | Integração | 🔴 | ⏳ |
| FIN-REL-05 | Razão analítico | Integração | 🟢 | ⏳ |

---

#### 3.4.6 F3_FISCAL - Notas Fiscais (EM DESENVOLVIMENTO)

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| FIN-FIS-01 | Gerar XML NFe 4.0 | Unitário | 🔴 | ⏳ |
| FIN-FIS-02 | Assinar XML com certificado | Integração | 🔴 | ⏳ |
| FIN-FIS-03 | Transmitir para SEFAZ | Integração | 🔴 | ⏳ |
| FIN-FIS-04 | Receber protocolo SEFAZ | Integração | 🔴 | ⏳ |
| FIN-FIS-05 | Gerar DANFE (PDF) | E2E | 🔴 | ⏳ |
| FIN-FIS-06 | Cancelar nota fiscal | Integração | 🟡 | ⏳ |
| FIN-FIS-07 | Download automático SEFAZ | Integração | 🟡 | ⏳ |
| FIN-FIS-08 | LCDPR geração | Integração | 🔴 | ⏳ |

---

### 3.5 Módulo Operacional

**Path:** `services/api/operacional/`

#### 3.5.1 O1_FROTA - Equipamentos

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| OPR-FRO-01 | Cadastrar equipamento | Integração | 🟡 | ⏳ |
| OPR-FRO-02 | Listar frota com filtros | Integração | 🟢 | ⏳ |
| OPR-FRO-03 | Atualizar horímetro | Integração | 🟡 | ⏳ |
| OPR-FRO-04 | Equipamento com número de série duplicado | Unitário | 🟡 | ⏳ |

---

#### 3.5.2 O1_FROTA - Manutenções

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| OPR-MAN-01 | Criar plano de manutenção | Integração | 🟡 | ⏳ |
| OPR-MAN-02 | Manutenção preventiva por horas | Unitário | 🟡 | ⏳ |
| OPR-MAN-03 | Abrir ordem de serviço | Integração | 🟡 | ⏳ |
| OPR-MAN-04 | Adicionar itens à OS | Integração | 🟡 | ⏳ |
| OPR-MAN-05 | OS gera baixa de estoque | Integração | 🔴 | ⏳ |
| OPR-MAN-06 | OS gera despesa | Integração | 🔴 | ⏳ |
| OPR-MAN-07 | Fechar OS | Integração | 🟡 | ⏳ |
| OPR-MAN-08 | Histórico de manutenções | Integração | 🟢 | ⏳ |

---

#### 3.5.3 O2_ESTOQUE - Depósitos

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| OPR-DEP-01 | Criar depósito | Integração | 🟡 | ⏳ |
| OPR-DEP-02 | Listar depósitos | Integração | 🟢 | ⏳ |
| OPR-DEP-03 | Atualizar depósito | Integração | 🟢 | ⏳ |
| OPR-DEP-04 | Depósito com responsável | Unitário | 🟢 | ⏳ |

---

#### 3.5.4 O2_ESTOQUE - Movimentações

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| OPR-MOV-01 | Entrada de estoque | Integração | 🔴 | ⏳ |
| OPR-MOV-02 | Saída de estoque | Integração | 🔴 | ⏳ |
| OPR-MOV-03 | Transferência entre depósitos | Integração | 🟡 | ⏳ |
| OPR-MOV-04 | Ajuste de inventário | Integração | 🟡 | ⏳ |
| OPR-MOV-05 | Movimentação com origem (compra, OS) | Integração | 🔴 | ⏳ |
| OPR-MOV-06 | Saldo negativo retorna erro | Unitário | 🔴 | ⏳ |
| OPR-MOV-07 | Histórico de movimentações | Integração | 🟡 | ⏳ |

---

#### 3.5.5 O2_ESTOQUE - Lotes e Validade

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| OPR-LOT-01 | Criar lote de produto | Integração | 🟡 | ⏳ |
| OPR-LOT-02 | Lote com validade | Unitário | 🟡 | ⏳ |
| OPR-LOT-03 | Alerta de validade próxima | Integração | 🟡 | ⏳ |
| OPR-LOT-04 | Saída usa lote mais antigo (PEPS) | Unitário | 🟡 | ⏳ |
| OPR-LOT-05 | Rastreabilidade por lote | E2E | 🟡 | ⏳ |

---

#### 3.5.6 O2_ESTOQUE - Requisições

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| OPR-REQ-01 | Criar requisição de material | Integração | 🟡 | ⏳ |
| OPR-REQ-02 | Aprovar requisição | Integração | 🟡 | ⏳ |
| OPR-REQ-03 | Requisição gera saída de estoque | Integração | 🔴 | ⏳ |
| OPR-REQ-04 | Listar requisições por status | Integração | 🟢 | ⏳ |

---

#### 3.5.7 O2_ESTOQUE - Reservas

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| OPR-RES-01 | Criar reserva de estoque | Integração | 🟡 | ⏳ |
| OPR-RES-02 | Reserva para OS/pedido | Integração | 🟡 | ⏳ |
| OPR-RES-03 | Consumir reserva | Integração | 🟡 | ⏳ |
| OPR-RES-04 | Reserva não disponível para outros | Unitário | 🟡 | ⏳ |

---

#### 3.5.8 O3_COMPRAS - Pedidos

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| OPR-COM-01 | Criar pedido de compra | Integração | 🟡 | ⏳ |
| OPR-COM-02 | Adicionar cotação ao pedido | Integração | 🟢 | ⏳ |
| OPR-COM-03 | Aprovar pedido | Integração | 🟡 | ⏳ |
| OPR-COM-04 | Receber pedido (entrada estoque) | Integração | 🔴 | ⏳ |
| OPR-COM-05 | Pedido gera despesa | Integração | 🔴 | ⏳ |
| OPR-COM-06 | Listar pedidos por status | Integração | 🟢 | ⏳ |

---

### 3.6 Módulo RH

**Path:** `services/api/rh/`

#### 3.6.1 RH1_REMUNERACAO - Colaboradores

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| RH-COL-01 | Cadastrar colaborador | Integração | 🟡 | ⏳ |
| RH-COL-02 | Listar colaboradores | Integração | 🟢 | ⏳ |
| RH-COL-03 | Atualizar colaborador | Integração | 🟢 | ⏳ |
| RH-COL-04 | Colaborador com CPF duplicado | Unitário | 🟡 | ⏳ |

---

#### 3.6.2 RH1_REMUNERACAO - Diárias e Empreitadas

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| RH-DIA-01 | Lançar diárias | Integração | 🟡 | ⏳ |
| RH-DIA-02 | Diárias geram pagamento | Integração | 🟡 | ⏳ |
| RH-EMP-01 | Criar empreitada | Integração | 🟡 | ⏳ |
| RH-EMP-02 | Empreitada com produção | Integração | 🟡 | ⏳ |
| RH-EMP-03 | Empreitada gera pagamento | Integração | 🟡 | ⏳ |
| RH-PAG-01 | Pagamento por produção | Integração | 🟡 | ⏳ |

---

### 3.7 Módulo Ambiental

**Path:** `services/api/ambiental/`

#### 3.7.1 AM1_COMPLIANCE - CAR

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| AMB-CAR-01 | Importar CAR | Integração | 🟢 | ⏳ |
| AMB-CAR-02 | Validar CCIR | Integração | 🟢 | ⏳ |
| AMB-APP-01 | Calcular APP | Unitário | 🟢 | ⏳ |
| AMB-RL-01 | Calcular Reserva Legal | Unitário | 🟢 | ⏳ |

---

### 3.8 Cadastros

**Path:** `services/api/cadastros/`

#### 3.8.1 Produtos

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| CAD-PRO-01 | Cadastrar produto | Integração | 🟡 | ⏳ |
| CAD-PRO-02 | Produto com código duplicado | Unitário | 🟡 | ⏳ |
| CAD-PRO-03 | Listar produtos com filtros | Integração | 🟡 | ⏳ |
| CAD-PRO-04 | Atualizar produto | Integração | 🟢 | ⏳ |
| CAD-PRO-05 | Inativar produto | Integração | 🟢 | ⏳ |

---

#### 3.8.2 Pessoas (Fornecedores/Clientes)

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| CAD-PES-01 | Cadastrar pessoa (CPF/CNPJ) | Integração | 🟡 | ⏳ |
| CAD-PES-02 | Validação de CPF/CNPJ | Unitário | 🔴 | ⏳ |
| CAD-PES-03 | Pessoa com documento duplicado | Unitário | 🟡 | ⏳ |
| CAD-PES-04 | Listar pessoas por tipo | Integração | 🟡 | ⏳ |
| CAD-PES-05 | Atualizar pessoa | Integração | 🟢 | ⏳ |

---

#### 3.8.3 Marcas e Modelos

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| CAD-MAR-01 | Cadastrar marca | Integração | 🟢 | ⏳ |
| CAD-MOD-01 | Cadastrar modelo | Integração | 🟢 | ⏳ |
| CAD-MOD-02 | Modelo com marca inválida | Unitário | 🟢 | ⏳ |

---

### 3.9 Backoffice

**Path:** `services/api/core/routers/backoffice*.py`

#### 3.9.1 Dashboard Administrativo

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| ADM-DAS-01 | Dashboard com métricas de tenants | Integração | 🟡 | ⏳ |
| ADM-DAS-02 | Dashboard com faturamento | Integração | 🟡 | ⏳ |
| ADM-DAS-03 | Dashboard com churn | Integração | 🟢 | ⏳ |
| ADM-DAS-04 | Dashboard com leads | Integração | 🟢 | ⏳ |

---

#### 3.9.2 Gestão de Tenants

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| ADM-TEN-01 | Listar todos tenants | Integração | 🟡 | ⏳ |
| ADM-TEN-02 | Atualizar tenant | Integração | 🟡 | ⏳ |
| ADM-TEN-03 | Ativar/desativar tenant | Integração | 🟡 | ⏳ |
| ADM-TEN-04 | Ver detalhes do tenant | Integração | 🟡 | ⏳ |

---

#### 3.9.3 Gestão de Planos

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| ADM-PLA-01 | Criar plano de assinatura | Integração | 🟡 | ⏳ |
| ADM-PLA-02 | Atualizar plano | Integração | 🟢 | ⏳ |
| ADM-PLA-03 | Listar planos | Integração | 🟢 | ⏳ |
| ADM-PLA-04 | Módulos do plano | Integração | 🟡 | ⏳ |

---

#### 3.9.4 Audit Log

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| ADM-AUD-01 | Log de ações de admin | Integração | 🟡 | ⏳ |
| ADM-AUD-02 | Filtro por admin | Integração | 🟢 | ⏳ |
| ADM-AUD-03 | Filtro por data | Integração | 🟢 | ⏳ |

---

## 4. Testes de Integração

### 4.1 Fluxo: Safra → Operação → Despesa

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| INT-SAF-DES-01 | Operação com custo gera despesa | E2E | 🔴 | ⏳ |
| INT-SAF-DES-02 | Operação sem custo não gera despesa | E2E | 🔴 | ⏳ |
| INT-SAF-DES-03 | Despesa com rateio por safra | E2E | 🟡 | ⏳ |
| INT-SAF-DES-04 | Múltiplas operações = múltiplas despesas | E2E | 🟡 | ⏳ |

**Critérios de Aceite:**
- Webhook de operação cria despesa
- Origem_id e origem_tipo preenchidos
- Rateios copiados da operação

---

### 4.2 Fluxo: Safra → Romaneio → Receita

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| INT-SAF-REC-01 | Romaneio com preço gera receita | E2E | 🔴 | ⏳ |
| INT-SAF-REC-02 | Romaneio sem preço não gera receita | E2E | 🔴 | ⏳ |
| INT-SAF-REC-03 | Receita com sacas_60kg | E2E | 🟡 | ⏳ |
| INT-SAF-REC-04 | Múltiplos romaneios = múltiplas receitas | E2E | 🟡 | ⏳ |

---

### 4.3 Fluxo: OS → Saída de Estoque → Despesa

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| INT-OS-EST-01 | OS com itens gera saída de estoque | E2E | 🔴 | ⏳ |
| INT-OS-EST-02 | Saída de estoque usa lote (PEPS) | E2E | 🟡 | ⏳ |
| INT-OS-EST-03 | OS gera despesa (mão de obra + peças) | E2E | 🔴 | ⏳ |
| INT-OS-EST-04 | Estoque negativo retorna erro | E2E | 🔴 | ⏳ |

---

### 4.4 Fluxo: Pedido de Compra → Recebimento → Entrada de Estoque

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| INT-COM-EST-01 | Receber pedido gera entrada de estoque | E2E | 🔴 | ⏳ |
| INT-COM-EST-02 | Entrada cria lote com validade | E2E | 🟡 | ⏳ |
| INT-COM-EST-03 | Pedido gera despesa | E2E | 🔴 | ⏳ |
| INT-COM-EST-04 | Recebimento parcial | E2E | 🟡 | ⏳ |

---

### 4.5 Fluxo: Animal → Evento → Peso

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| INT-ANI-EVT-01 | Pesagem atualiza peso do animal | E2E | 🟡 | ⏳ |
| INT-ANI-EVT-02 | Eventos são append-only | E2E | 🔴 | ⏳ |
| INT-ANI-EVT-03 | Categoria muda por idade | E2E | 🟡 | ⏳ |

---

### 4.6 Isolamento de Tenant

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| INT-TEN-01 | Tenant A não vê safras de Tenant B | E2E | 🔴 | ⏳ |
| INT-TEN-02 | Tenant A não vê financeiro de Tenant B | E2E | 🔴 | ⏳ |
| INT-TEN-03 | Tenant A não vê estoque de Tenant B | E2E | 🔴 | ⏳ |
| INT-TEN-04 | Usuário com acesso a múltiplos tenants | E2E | 🟡 | ⏳ |

---

## 5. Testes E2E

### 5.1 Safra de Soja Completa

**Cenário:** Criar safra, registrar operações, colheita e validar financeiro

| Passo | Ação | Esperado |
|-------|------|----------|
| 1 | Criar safra "Soja 2025/26" | Safra criada em PLANEJADA |
| 2 | Avançar para PREPARO_SOLO | Fase atualizada |
| 3 | Registrar operação de preparo | Operação criada |
| 4 | Avançar para PLANTIO | Fase atualizada |
| 5 | Registrar operação de plantio | Operação criada |
| 6 | Avançar para DESENVOLVIMENTO | Fase atualizada |
| 7 | Registrar monitoramento | Monitoramento criado |
| 8 | Avançar para COLHEITA | Fase atualizada |
| 9 | Criar romaneio | Romaneio criado |
| 10 | Validar dashboard financeiro | Receita e despesa corretas |

**Critérios de Aceite:**
- Todas fases transitam corretamente
- Operações geram despesas
- Romaneio gera receita
- KPIs calculados

---

### 5.2 Ciclo Pecuário de Corte

**Cenário:** Criar lote, registrar eventos, venda

| Passo | Ação | Esperado |
|-------|------|----------|
| 1 | Criar lote de engorda | Lote criado |
| 2 | Registrar pesagem inicial | Evento criado |
| 3 | Registrar vacinação | Evento criado |
| 4 | Registrar pesagem final | Evento criado |
| 5 | Vender lote | Receita gerada |

---

### 5.3 Gestão de Estoque Completa

**Cenário:** Compra, recebimento, requisição, uso

| Passo | Ação | Esperado |
|-------|------|----------|
| 1 | Criar pedido de compra | Pedido criado |
| 2 | Aprovar pedido | Status = APROVADO |
| 3 | Receber pedido | Entrada de estoque |
| 4 | Criar requisição | Requisição criada |
| 5 | Aprovar requisição | Status = APROVADA |
| 6 | Consumir requisição | Saída de estoque |

---

## 6. Testes de Performance

### 6.1 SLA por Endpoint

| Categoria | Endpoint | SLA (ms) | Prioridade |
|-----------|----------|----------|------------|
| Auth | /api/v1/auth/login | < 200 | 🔴 |
| Core | /api/v1/fazendas | < 300 | 🟡 |
| Agrícola | /api/v1/agricola/safras | < 300 | 🟡 |
| Agrícola | /api/v1/agricola/operacoes | < 400 | 🟡 |
| Financeiro | /api/v1/financeiro/receitas | < 300 | 🟡 |
| Financeiro | /api/v1/financeiro/relatorios | < 1000 | 🟡 |
| Operacional | /api/v1/operacional/estoque/saldos | < 300 | 🟡 |

---

### 6.2 Testes de Carga

| Cenário | Usuários | Duração | Requisições | Esperado |
|---------|----------|---------|-------------|----------|
| Login simultâneo | 100 | 1 min | 1000 | 99% sucesso |
| Listagem de safras | 50 | 5 min | 5000 | < 500ms |
| Criação de operações | 20 | 10 min | 2000 | < 400ms |
| Dashboard financeiro | 30 | 5 min | 3000 | < 600ms |

---

### 6.3 Testes de Stress

| Cenário | Pico | Duração | Esperado |
|---------|------|---------|----------|
| Black Friday | 500 usuários | 1 hora | Sistema estável |
| Fim de mês | 200 usuários | 30 min | < 1s response |
| Fechamento de safra | 100 usuários | 2 horas | Sem erros |

---

## 7. Testes de Segurança

### 7.1 Autenticação e Autorização

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| SEC-01 | Acesso sem token retorna 401 | Unitário | 🔴 | ⏳ |
| SEC-02 | Token expirado retorna 401 | Unitário | 🔴 | ⏳ |
| SEC-03 | Token inválido retorna 401 | Unitário | 🔴 | ⏳ |
| SEC-04 | Sem permissão retorna 403 | Unitário | 🔴 | ⏳ |
| SEC-05 | Tenant violation retorna 403 | Unitário | 🔴 | ⏳ |
| SEC-06 | SQL injection não funciona | Unitário | 🔴 | ⏳ |
| SEC-07 | XSS não funciona | Unitário | 🔴 | ⏳ |
| SEC-08 | Rate limiting funciona | Unitário | 🟡 | ⏳ |

---

### 7.2 Validação de Input

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| SEC-09 | CPF inválido retorna erro | Unitário | 🟡 | ⏳ |
| SEC-10 | CNPJ inválido retorna erro | Unitário | 🟡 | ⏳ |
| SEC-11 | Email inválido retorna erro | Unitário | 🟡 | ⏳ |
| SEC-12 | Data futura retorna erro | Unitário | 🟡 | ⏳ |
| SEC-13 | Valor negativo retorna erro | Unitário | 🟡 | ⏳ |
| SEC-14 | Geometria inválida retorna erro | Unitário | 🟡 | ⏳ |

---

### 7.3 LGPD

| ID | Teste | Tipo | Prioridade | Status |
|----|-------|------|------------|--------|
| LGPD-01 | Exportar dados pessoais | Integração | 🟡 | ⏳ |
| LGPD-02 | Excluir conta | Integração | 🟡 | ⏳ |
| LGPD-03 | Anonimizar dados | Integração | 🟡 | ⏳ |
| LGPD-04 | Log de consentimento | Unitário | 🟡 | ⏳ |

---

## 8. Critérios de Aceite

### 8.1 Por Tipo de Bug

| Severidade | Critério | SLA |
|------------|----------|-----|
| 🔴 Crítico | Sistema fora do ar, perda de dados | 4 horas |
| 🟡 Alto | Funcionalidade principal quebrada | 24 horas |
| 🟢 Médio | Funcionalidade secundária quebrada | 1 semana |
| ⚪ Baixo | Bug cosmético, typo | 2 semanas |

---

### 8.2 Definição de Pronto por Feature

- ✅ Testes unitários escritos e passando
- ✅ Testes de integração escritos e passando
- ✅ Coverage > 80%
- ✅ Testes E2E críticos passando
- ✅ Performance dentro do SLA
- ✅ Sem bugs críticos/altos abertos
- ✅ Documentação atualizada

---

## 9. Matriz de Rastreabilidade

### Requisitos → Testes

| Requisito | Testes Relacionados | Status |
|-----------|---------------------|--------|
| R001 - Multi-tenancy | CORE-TEN-01 a 05 | ✅ |
| R002 - RBAC | CORE-RBAC-01 a 05 | ✅ |
| R003 - Safra | AGR-SAF-01 a 10 | ✅ |
| R004 - Operação | AGR-OPR-01 a 12 | ✅ |
| R005 - Romaneio | AGR-ROM-01 a 11 | ✅ |
| R006 - Receita | FIN-REC-01 a 08 | ✅ |
| R007 - Despesa | FIN-DES-01 a 10 | ✅ |
| R008 - Estoque | OPR-MOV-01 a 07 | ✅ |
| R009 - Conciliação | FIN-CON-01 a 05 | 🟡 |
| R010 - NFe | FIN-FIS-01 a 08 | 📋 |

---

## 📊 Status Geral

| Módulo | Testes Totais | Passando | Falhando | Pendentes | Coverage |
|--------|---------------|----------|----------|-----------|----------|
| Core | 50 | 0 | 0 | 50 | 75% |
| Agrícola | 55 | 0 | 0 | 55 | 80% |
| Pecuária | 20 | 0 | 0 | 20 | 70% |
| Financeiro | 50 | 0 | 0 | 50 | 65% |
| Operacional | 50 | 0 | 0 | 50 | 70% |
| RH | 15 | 0 | 0 | 15 | 60% |
| Ambiental | 5 | 0 | 0 | 5 | 40% |
| Cadastros | 15 | 0 | 0 | 15 | 70% |
| Backoffice | 15 | 0 | 0 | 15 | 65% |
| **Total** | **275** | **0** | **0** | **275** | **69%** |

---

## ✅ Sign-Off

| Role | Nome | Data | Assinatura |
|------|------|------|------------|
| QA Lead | _____________________ | _________ | _____________________ |
| Tech Lead | _____________________ | _________ | _____________________ |
| Product Owner | _____________________ | _________ | _____________________ |

---

**Próxima Revisão:** 2026-04-30
**Responsável:** QA Team
