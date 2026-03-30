# Brainstorming — Análise Completa do Módulo Agricola

**Data:** 2026-03-30
**Análise do:** Módulo Agricola (A1_PLANEJAMENTO)
**Status:** Mapeamento de funcionalidades, workflow e gaps

---

## FASE 1 — Entendimento do Problema

### O QUE é o módulo agricola?
Sistema de gestão do ciclo de vida de safras (colheita), desde planejamento até colheita, passando por operações agrícolas, monitoramento e rastreabilidade.

### POR QUE existe?
- Permite que produtores rurais controlarem suas safras de forma estruturada
- Rastreabilidade de operações (quem, quando, onde, como plantou/colheu)
- Análise de custos e rendimento por safra
- Integração com dados climáticos, NDVI, previsões

### QUEM usa?
- **Operador:** Registra operações (plantio, pulverização, colheita)
- **Agrônomo:** Monitora fenologia, prescreve operações, analisa solo
- **Gerente/Gestor:** Acompanha resumos, custos, metas da safra
- **Financeiro:** Integra custos de operações para relatórios

### CONSTRAINTS atuais?
- ✅ Multi-tenant: cada tenant vê apenas suas safras
- ✅ Role-based: operador ≠ agrônomo ≠ gerente
- ⚠️ Algumas funcionalidades frontend/backend desalinhadas
- ⚠️ Alguns endpoints ainda não implementados

---

## FASE 2 — Mapa de Submódulos

| Submódulo | Propósito | Status Backend | Status Frontend | Descrição |
|-----------|-----------|---|---|---|
| **a1_planejamento** | Planejamento estratégico da safra | ✅ Implementado | ✅ Página | Metas, orçamento, cronograma |
| **safras** | CRUD + workflow (Planejada → Encerrada) | ✅ Completo | ✅ Completo | Core do módulo: ciclo de vida |
| **talhoes** | Parcelas de terra por fazenda | ✅ Completo | ✅ Completo | Cadastro básico com geometria |
| **operacoes** | Ações agrícolas (plantio, pulverização, etc) | ✅ Completo | ✅ Completo | Registro com rastreabilidade |
| **fenologia** | Estágios de desenvolvimento da planta | ✅ Completo | ✅ Página | Escalas padronizadas (BBCh) |
| **ndvi** | Índices de vegetação (satélite/drone) | ✅ Completo | ✅ Página | Análise visual do vigor da safra |
| **climatico** | Dados climáticos (integrado) | ✅ Completo | ✅ Página | Temperatura, umidade, chuva |
| **monitoramento** | Observações em campo (texto + foto) | ✅ Completo | ✅ Página | Registro qualitativo de problemas |
| **romaneios** | Rastreamento de colheita (lote) | ✅ Completo | ✅ Página | Controle de quantidade/qualidade |
| **beneficiamento** | Pós-colheita (secagem, limpeza) | ✅ Completo | ✅ Página | Processamento do grão |
| **rastreabilidade** | Trilha auditável (público + privado) | ✅ Completo | ✅ Página | QR code + histórico público |
| **analises_solo** | Análises laboratoriais de solo | ✅ Completo | ✅ Página | Relatórios de fertilidade |
| **cadastros** | Culturas, cultivares, insumos | ✅ Completo | ✅ Página | Dados de referência |
| **agronomo** | Workspace do agrônomo | ✅ Completo | ✅ Página | Vista de recomendações |
| **checklist** | Tarefas/checklist da safra | ✅ Completo | ✅ Página | Atividades obrigatórias |
| **prescricoes** | Prescrições agrônomas (IA?) | ✅ Completo | ✅ Página | Recomendações de operações |
| **previsoes** | Previsões de rendimento (IA?) | ✅ Completo | ✅ Página | Estimativas de colheita |
| **custos** | Análise de custos por operação | ✅ Completo | ✅ Página | Integrado com operacional |
| **alertas** | Alertas automáticos | ✅ Service | ❌ Não integrado | Notificações de anomalias |
| **dashboard** | Dashboard agrícola | ✅ Completo | ✅ Página | KPIs e resumos |

---

## FASE 3 — Workflow Principal

```
SAFRA
  ├── Status: PLANEJADA → PREPARO_SOLO → PLANTIO → DESENVOLVIMENTO → COLHEITA → POS_COLHEITA → ENCERRADA
  ├── Talhoes (1..N)
  │   ├── Geometria (GeoJSON/PostGIS)
  │   ├── Histórico de culturas
  │   └── Análises de solo
  │
  ├── Operações (N)
  │   ├── Tipo: plantio, pulverização, adubação, colheita
  │   ├── Data, hora, operador
  │   ├── Condições climáticas
  │   └── Rastreamento de maquinário
  │
  ├── Fenologia (timeline)
  │   ├── Escala BBCh (0-99)
  │   └── Registro de estágios
  │
  ├── Monitoramento (diário/semanal)
  │   ├── Observações + fotos
  │   └── Alertas de problemas
  │
  ├── NDVI (semanal)
  │   ├── Imagens de satélite/drone
  │   └── Mapa de vigor
  │
  ├── Romaneios (colheita)
  │   ├── Lotes colhidos
  │   ├── Quantidade (sacas)
  │   └── Qualidade (umidade, impurezas)
  │
  └── Encerramento
      ├── Custos totais
      ├── Rendimento (sacas/ha)
      └── ROI
```

---

## FASE 4 — Análise de Implementação por Feature

### ✅ IMPLEMENTADO E ESTÁVEL

1. **CRUD de Safras**
   - Criar, listar, detalhar, atualizar
   - Transições de status validadas
   - Histórico de fases registrado
   - Tenant isolation: ✅

2. **CRUD de Talhões**
   - Cadastro com geometria (GeoJSON em SQLite / PostGIS em Postgres)
   - Histórico de culturas (JSON)
   - Características de solo
   - Tenant isolation: ✅

3. **CRUD de Operações**
   - Tipo, subtipo, descrição
   - Data, hora, operador
   - Condições climáticas capturadas
   - Rastreamento de máquinas/implementos
   - Tenant isolation: ✅

4. **Fenologia**
   - Escala BBCh (0-99) com descrições
   - Registro de estágios por data
   - Seed scripts com escalas padronizadas
   - Tenant isolation: ✅

5. **NDVI / Monitoramento**
   - Upload de imagens
   - Indexação
   - Frontend com mapas
   - Tenant isolation: ✅

6. **Romaneios (Colheita)**
   - Lotes com quantidade/qualidade
   - Integrado com operações
   - Tenant isolation: ✅

7. **Rastreabilidade**
   - Router público (sem auth) para QR codes
   - Histórico completo
   - Tenant isolation: ✅

---

### ⚠️ IMPLEMENTADO MAS COM GAPS

1. **Workflow de Fases (Safra)**
   - ✅ Backend: Transições validadas com SAFRA_TRANSICOES
   - ⚠️ Frontend: Falta ícone visual da progressão
   - ⚠️ Falta indicador de "atraso" vs. meta
   - **Recomendação:** Adicionar timeline visual com datas planejadas vs. reais

2. **Custos**
   - ✅ Backend: Service criado
   - ⚠️ Frontend: Página existe mas falta integração com operações
   - ⚠️ Falta relatório de ROI por talhão
   - **Recomendação:** Integrar custos de operações automaticamente

3. **Alertas**
   - ✅ Backend: Service de verificação pós-operação
   - ❌ Frontend: Não integrado em nenhuma página
   - ❌ Falta notificação em tempo real
   - **Recomendação:** Criar widget de alertas no dashboard ou na safra

4. **Prescrições**
   - ✅ Backend: Endpoints existem
   - ⚠️ Frontend: Página existe mas parece ser um mockup
   - ⚠️ Falta integração com operações (sugerir prescrição → criar operação)
   - **Recomendação:** Fluxo "Prescrever → Operação" automático

5. **Previsões**
   - ✅ Backend: Endpoints existem
   - ⚠️ Frontend: Página é mockup
   - ⚠️ Modelo de IA não implementado
   - **Recomendação:** Integrar com ML (ou remover se não é prioridade)

---

### ❌ FALTANDO OU INCOMPLETO

1. **Integração Financeira**
   - ⚠️ Comentário no código: "Integrar httpx api-financeiro para receita"
   - ❌ Falta calcular receita de romaneios (sacas × preço)
   - ❌ Falta sincronizar custos com módulo financeiro
   - **Recomendação:** Implementar POST `/financeiro/operacoes` ao criar operação

2. **Validações de Regras de Negócio**
   - ✅ Transições de fase validadas
   - ⚠️ Falta validar: operação não pode ser registrada em fase errada (ex: plantio em COLHEITA)
   - ⚠️ Falta validar: data de operação não pode ser no futuro
   - **Recomendação:** Adicionar validações em `create_operacao()`

3. **Permissões por Role**
   - ✅ Backend: Decoradores `@require_tenant_permission()` existem
   - ⚠️ Frontend: Falta verificar permissões em algumas páginas (ex: deletar safra)
   - **Recomendação:** Adicionar `usePermission()` em diálogos de ação destrutiva

4. **Importação de Dados**
   - ❌ Falta endpoint para importar safras em lote (ex: CSV/Excel)
   - ❌ Falta endpoint para importar operações de sistema externo
   - **Recomendação:** Não é urgente, pode ser feature futura

5. **Relatórios Avançados**
   - ✅ Dashboard básico existe
   - ⚠️ Falta: relatório de evolução fenológica vs. NDVI
   - ⚠️ Falta: relatório comparativo (safra atual vs. histórico)
   - ⚠️ Falta: análise de corrrelação (chuva → rendimento)
   - **Recomendação:** Depende de prioridade do produto

---

## FASE 5 — Recomendações Priorizadas

### 🔴 CRÍTICO (Bloqueia features)

1. **Integração Safra ↔ Operações ↔ Financeiro**
   - Atualmente não há sincronização automática de custos
   - **Ação:** Implementar webhook ao criar operação → POST `/financeiro/`
   - **Impacto:** Usuários não conseguem ver custos totais por safra

2. **Validações de Regra de Negócio**
   - Operação pode ser registrada em qualquer fase (BUG!)
   - **Ação:** Adicionar check na `criar_operacao()`: `if safra.status not in OPERACOES_PERMITIDAS[tipo]`
   - **Impacto:** Integridade de dados

### 🟡 IMPORTANTE (Melhora UX/credibilidade)

3. **Alertas no Frontend**
   - Alertas são gerados mas não mostrados
   - **Ação:** Criar widget na página de safra listando alertas
   - **Ação:** Integrar com notificações (Slack? Email?)
   - **Impacto:** Agrônomo não vê problemas em tempo real

4. **Timeline Visual de Fases**
   - Status da safra é difícil de visualizar
   - **Ação:** Componente tipo Stepper com datas planejadas vs. reais
   - **Impacto:** UX melhora, usuário entende atraso

5. **Validações Frontend (Permissions)**
   - Botões destrutivos (deletar safra) aparecem mesmo sem permissão
   - **Ação:** Adicionar `hasPermission('agricola:safras:delete')` em diálogos
   - **Impacto:** Evita 403 errors, melhora UX

### 🟢 MELHORIAS (Nice-to-have)

6. **Prescrições → Operações Automáticas**
   - Atualmente é manual
   - **Ação:** Botão "Aplicar prescrição" cria operação automaticamente
   - **Impacto:** Agrônomo economiza tempo

7. **Relatórios Comparativos**
   - Falta análise histórica
   - **Ação:** Página de estatísticas (safra atual vs. 3 anos)
   - **Impacto:** Insights para decisão

8. **Importação em Lote**
   - Hoje só cadastro manual
   - **Ação:** Endpoint `/safras/import` (CSV/Excel)
   - **Impacto:** Onboarding mais rápido

---

## FASE 6 — Plano de Ação Recomendado

### ITERAÇÃO 1 (Estabilidade)
- [ ] Implementar validações de regra de negócio (operação só em fases permitidas)
- [ ] Integrar operações com módulo financeiro
- [ ] Adicionar testes de tenant isolation

### ITERAÇÃO 2 (UX)
- [ ] Timeline visual de fases da safra
- [ ] Widget de alertas no dashboard
- [ ] Validações de permissão no frontend

### ITERAÇÃO 3 (Features)
- [ ] Prescrições → Operações automáticas
- [ ] Relatórios comparativos
- [ ] Importação em lote

---

---

## PARTE 2 — Integração com Módulos Auxiliares

### Contexto do Problema

O processo de colheita é **multi-módulo**. Não acontece apenas em `agricola/`, mas envolve:

1. **Operacional:** Frota (maquinário), Estoque (depósitos), Compras (insumos)
2. **Financeiro:** Despesas (custos), Receitas (venda)
3. **Core Cadastros:** Pessoas (operadores), Equipamentos, Produtos, Áreas Rurais
4. **Rastreabilidade:** Trilha auditável (para certificação)

Hoje há **silos de dados** — informações não fluem entre módulos.

---

## Mapa Expandido: Fluxo Completo da Colheita

```
┌─────────────────────────────────────────────────────────────────────────┐
│ SAFRA.status = COLHEITA                                                │
│ (agricola/safras)                                                       │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
    ┌────▼──────────────┐        ┌──────────▼────────┐
    │ OPERAÇÃO COLHEITA │        │ CHECAR MAQUINÁRIO │
    │ (agricola/        │        │ (operacional/     │
    │  operacoes)       │        │  frota/equipamento)
    │                   │        │                   │
    │ ✅ Tipo: colheita │        │ ✅ Está pronto?  │
    │ ✅ Data realizada │        │ ❌ Manutenção OK? │
    │ ✅ Operador       │        │ ❌ Combustível?  │
    │ ✅ Maquinário_id  │        │                   │
    │ ❌ Validar fase   │        └───────────────────┘
    │ ❌ Validar insumo │
    │    (carência)     │
    └────┬─────────────┘
         │
         ▼
    ┌─────────────────────────────────┐
    │ REGISTRAR INSUMO DA OPERAÇÃO    │
    │ (agricola/operacoes/            │
    │  InsumoOperacao)                │
    │                                 │
    │ ✅ Produto (defensivo/adubo)   │
    │ ✅ Lote + validade              │
    │ ✅ Dose, quantidade, custo      │
    │ ❌ Descontar do ESTOQUE?        │
    │ ❌ Gerar DESPESA?               │
    └────┬────────────────────────────┘
         │
         ▼
    ┌─────────────────────────────────┐
    │ ROMANEIO DE COLHEITA            │
    │ (agricola/romaneios)            │
    │                                 │
    │ ✅ Peso bruto/líquido (sacas)  │
    │ ✅ Umidade, impureza, avariados│
    │ ✅ Operador, turno, máquina     │
    │ ✅ Número romaneio              │
    │ ❌ Destino (armazém/terceiro?)  │
    │ ❌ Preco_saca → RECEITA?        │
    │ ❌ Nota fiscal integrada?       │
    └────┬────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────┐
    │ ARMAZENAR (ESTOQUE)              │
    │ (operacional/estoque)            │
    │                                  │
    │ ✅ Depósito/armazém destino     │
    │ ✅ Lote de colheita              │
    │ ✅ Quantidade (kg/sacas)         │
    │ ✅ Validade (grão)               │
    │ ❌ Rastrear lote → receita?     │
    │ ❌ Sincronizar quantidade?      │
    └────┬─────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────┐
    │ BENEFICIAMENTO (PÓS-COLHEITA)    │
    │ (agricola/beneficiamento)        │
    │                                  │
    │ ✅ Secagem, limpeza, peneiramento│
    │ ✅ Entrada + saída (peso)        │
    │ ✅ Perdas registradas            │
    │ ❌ Custo de processamento?       │
    │ ❌ Sincronizar estoque?          │
    └────┬─────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────┐
    │ RASTREABILIDADE                  │
    │ (agricola/rastreabilidade)       │
    │                                  │
    │ ✅ QR code gerado                │
    │ ✅ Histórico completo publicado │
    │ ✅ Rota publica (sem auth)       │
    │ ✅ Certificação (organic?)       │
    └────┬─────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────┐
    │ VENDA / RECEITA                  │
    │ (financeiro/receitas)            │
    │                                  │
    │ ❌ Automático do romaneio?       │
    │ ❌ Quantidade × Preço            │
    │ ❌ Nota fiscal eletrônica?       │
    │ ❌ Rastreabilidade na NF?        │
    └────┬─────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────┐
    │ ENCERRAR SAFRA                   │
    │ (agricola/safras)                │
    │                                  │
    │ ✅ Status: POS_COLHEITA → ENCERRADA
    │ ❌ Agregação automática?         │
    │ ❌ ROI calculado?                │
    │ ❌ Comparativo com anos anteriores?
    └──────────────────────────────────┘
```

---

## Módulos Auxiliares — Status de Integração

### 1. OPERACIONAL (Frota, Estoque, Compras)

| Feature | Model | Backend | Status | Gap |
|---------|-------|---------|--------|-----|
| **Maquinário/Equipamento** | `core.cadastros.equipamentos.Equipamento` | ✅ | ✅ CRUD completo | ⚠️ Não linkado com operações agrícolas |
| **Frota (Plano + Manutenção)** | `operacional.frota.PlanoManutencao`, `OrdemServico` | ✅ | ✅ CRUD + rotas | ⚠️ Sem histórico de disponibilidade |
| **Estoque (Depósitos)** | `operacional.estoque.Deposito`, `SaldoEstoque`, `LoteEstoque` | ✅ | ✅ CRUD completo | ❌ Não integra com operações (descontar insumo) |
| **Insumo na Operação** | `agricola.operacoes.InsumoOperacao` | ✅ | ✅ Criado | ❌ Não desconta estoque automaticamente |
| **Compras** | `operacional.compras.PedidoCompra`, `CotacaoFornecedor` | ✅ | ✅ CRUD completo | ⚠️ Sem integração com operações |
| **Apontamento (Uso de Máquina)** | `operacional.apontamento.ApontamentoUso` | ✅ | ✅ Criado | ❌ Não vinculado com operações agrícolas |

**Gaps Críticos:**
- Operação agrícola pode usar máquina, mas não registra seu **histórico de uso**
- Insumo da operação não **desconta automaticamente do estoque**
- Falta **rastreamento de disponibilidade** de máquinas (quando está em uso?)
- Falta **integração de custos** (operação → despesa)

---

### 2. FINANCEIRO (Despesas, Receitas)

| Feature | Model | Backend | Status | Gap |
|---------|-------|---------|--------|-----|
| **Despesa** | `financeiro.despesa.Despesa` | ✅ | ✅ CRUD + parcelamento | ❌ Não tem origem_id (ref. para operação) |
| **Receita** | `financeiro.receita.Receita` | ✅ | ✅ CRUD + parcelamento | ❌ Não linkada com romaneio |
| **Plano de Contas** | `financeiro.plano_conta.PlanoConta` | ✅ | ✅ CRUD | ✅ OK |
| **Rateio** | `financeiro.rateio.Rateio` | ✅ | ✅ Criado | ⚠️ Sem uso evidente |

**Gaps Críticos:**
- Operação agrícola tem `custo_total`, mas não cria `Despesa` automaticamente
- Romaneio tem `preco_saca` e `receita_total`, mas não cria `Receita` automaticamente
- Falta **rastreamento de origem** (qual operação gerou qual despesa?)
- Falta **dashboard financeiro por safra** (custo total vs. receita total)

---

### 3. CORE CADASTROS (Pessoas, Equipamentos, Produtos)

| Feature | Model | Backend | Status | Gap |
|---------|-------|---------|--------|-----|
| **Pessoa (Operador)** | `core.cadastros.pessoas.Pessoa` | ✅ | ✅ CRUD completo | ✅ Linkado em operações |
| **Equipamento (Máquina)** | `core.cadastros.equipamentos.Equipamento` | ✅ | ✅ CRUD completo | ⚠️ Referência UUID genérica em operações |
| **Produto (Insumo)** | `core.cadastros.produtos.Produto` | ✅ | ✅ CRUD + extensões | ✅ OK |
| **Produto Agrícola** | `core.cadastros.produtos.ProdutoAgricola` | ✅ | ✅ Defensivos, sementes, etc | ✅ OK |
| **Área Rural (Talhão)** | `core.cadastros.propriedades.AreaRural` | ✅ | ✅ CRUD + geometria | ✅ Linkado em safras |

**Status:** ✅ Dados de referência OK, integração parcial

---

### 4. PECUÁRIA (Não relevante para colheita? Talvez integração)

| Feature | Model | Backend | Status | Gap |
|---------|-------|---------|--------|-----|
| **Lote** | `pecuaria.animal.Lote` | ✅ | ✅ Criado | N/A (não é colheita) |
| **Manejo** | `pecuaria.producao.ManejoLote` | ✅ | ✅ Criado | N/A (não é colheita) |

**Nota:** Módulo pecuária pode compartilhar estoque, equipamentos, pessoas (operadores), financeiro.

---

## Fluxos que FALTAM Integração

### FLUXO 1: Operação → Despesa Automática

**Hoje:**
```
criar_operacao(tipo=colheita, custo_total=5000)
→ Salva OperacaoAgricola.custo_total = 5000
→ ❌ Não cria Despesa
→ ❌ Usuário não vê custo na aba Financeiro
```

**Deveria ser:**
```
criar_operacao(...)
→ Registra OperacaoAgricola + InsumoOperacao
→ ✅ Cria Despesa automaticamente
  - Descrição: "Colheita - Safra ABC / Talhão XYZ"
  - Valor: soma(insumo.custo_total) + maquina.custo_hora
  - Categoria: PlanoConta (ex: "Serviços de Colheita")
  - Referência: operacao_id (rastreabilidade)
→ ✅ Desconta de Estoque (insumo)
```

**Implementar:**
- [ ] Adicionar `operacao_id` FK em `Despesa`
- [ ] Webhook pós `criar_operacao()` → POST `/financeiro/despesas/`
- [ ] Desconto automático de estoque

---

### FLUXO 2: Romaneio → Receita Automática

**Hoje:**
```
criar_romaneio(safra_id, peso_kg=30000, preco_saca=200)
→ Calcula receita_total = 250 sacas × $200 = $50.000
→ ❌ Não cria Receita
→ ❌ Usuário precisa lanç manualmente
```

**Deveria ser:**
```
criar_romaneio(...)
→ ✅ Cria Receita automaticamente
  - Descrição: "Venda - Colheita Safra ABC"
  - Valor: romaneio.receita_total
  - Cliente: "Armazém / Comprador" (customizável)
  - Referência: romaneio_id (rastreabilidade)
→ ✅ Gera NFe automaticamente (se configurado)
→ ✅ Atualiza estoque (deposita lote)
```

**Implementar:**
- [ ] Adicionar `romaneio_id` FK em `Receita`
- [ ] Webhook pós `criar_romaneio()` → POST `/financeiro/receitas/`
- [ ] Integração com NF-e (ou mock)

---

### FLUXO 3: Operação + Fase Safra (Validação)

**Hoje:**
```
criar_operacao(tipo=plantio, safra_id=...)
→ Safra.status = COLHEITA
→ ❌ Sem validação
→ ❌ Cria plantio em safra já colhida (BUG!)
```

**Deveria ser:**
```
criar_operacao(tipo=X, safra_id=...)
→ Fetch safra.status
→ Validar: X permitido em status?
   - PLANTIO → só em PLANTIO/DESENVOLVIMENTO
   - COLHEITA → só em COLHEITA
   - ADUBAÇÃO → só em PREPARO_SOLO/DESENVOLVIMENTO
   - ETC.
→ Se inválido: BusinessRuleError (422)
→ Registra: operacao.fase_safra = safra.status (snapshot)
```

**Implementar:**
- [ ] Adicionar validação em `crear_operacao()`
- [ ] Mapear tipos de operação → fases permitidas
- [ ] Adicionar testes de RN

---

### FLUXO 4: Insumo Operação → Estoque Desconto

**Hoje:**
```
criar_insumo_operacao(produto_id, quantidade=100, unidade=L)
→ ❌ Não desconta de estoque
→ ❌ Estoque fica inconsistente
```

**Deveria ser:**
```
criar_insumo_operacao(...)
→ ✅ Verifica SaldoEstoque (quantidade_atual >= 100L)
→ ✅ Desconta: quantidade_atual -= 100L
→ ✅ Registra MovimentacaoEstoque (SAÍDA)
→ ✅ Se lote com validade, usa FIFO
→ Se quantidade insuficiente → BusinessRuleError
```

**Implementar:**
- [ ] Webhook em `criar_insumo_operacao()` → atualizar estoque
- [ ] FIFO logic em `LoteEstoque`
- [ ] Testes de estoque negativo

---

### FLUXO 5: Dashboard de Safra (Agregação)

**Hoje:**
```
GET /safras/{id} → SomaPerdas, SomaOperacoes
→ ❌ Falta dados de receita
→ ❌ Falta custo total integrado
```

**Deveria ser:**
```
GET /safras/{id}/resumo
→ {
  "safra": {...},
  "operacoes": {
    "total": 15,
    "custo_total": 45000,  ← de Despesa.origem_id = operacao_id
    "tempo_total_h": 120
  },
  "romaneios": {
    "total_sacas": 1500,
    "receita_total": 300000,  ← de Receita.origem_id = romaneio_id
    "produtividade_sc_ha": 50
  },
  "financeiro": {
    "despesa_total": 50000,  ← todas as operações + insumos
    "receita_total": 300000,
    "lucro_safra": 250000,
    "roi": "600%"
  }
}
```

**Implementar:**
- [ ] View ou Stored Procedure para agregação
- [ ] Incluir links entre Operação ↔ Despesa
- [ ] Incluir links entre Romaneio ↔ Receita
- [ ] Calcular ROI por safra

---

## Plano de Ação Expandido

### 🔴 CRÍTICO (Bloqueia integridade)

1. **Validação Operação + Fase Safra** (agricola)
   - Ação: Adicionar check em `criar_operacao()`
   - Impacto: Evita operações em fase errada

2. **Operação → Despesa** (agricola ↔ financeiro)
   - Ação: Webhook + FK em Despesa
   - Impacto: Custos visíveis no financeiro

3. **Insumo Operação → Estoque** (agricola ↔ operacional)
   - Ação: Desconto automático + FIFO
   - Impacto: Estoque consistente

---

### 🟡 IMPORTANTE (Melhora UX)

4. **Romaneio → Receita** (agricola ↔ financeiro)
   - Ação: Webhook + FK em Receita
   - Impacto: Receita visível em tempo real

5. **Dashboard Safra** (agregação)
   - Ação: View com custo + receita + ROI
   - Impacto: Usuário vê saúde da safra

6. **Apontamento Máquina** (agricola ↔ operacional)
   - Ação: Registrar tempo de uso de máquina
   - Impacto: Histórico de disponibilidade

---

### 🟢 NICE-TO-HAVE (Features futuras)

7. **NFe Automática** (romaneio → financeiro)
   - Ação: Integrar com API da RFB ou provider
   - Impacto: Processo 100% digital

8. **Sugestão de Preço** (inteligência)
   - Ação: ML com histórico de preços
   - Impacto: Negociação mais informada

---

## ANEXO — Checklist de Verificação Expandido

### Agricola (Core)
- [x] Todos os submódulos têm models.py
- [x] Todos têm schemas.py
- [x] Todos têm service.py
- [x] Todos têm router.py
- [x] Tenant isolation validado
- [ ] Permissões por role completas
- [ ] Validações de RN (fase safra + tipo operação)
- [ ] Alertas integrados no frontend

### Integrações (Cross-Module)
- [ ] Operação ↔ Despesa (webhook)
- [ ] Romaneio ↔ Receita (webhook)
- [ ] Insumo ↔ Estoque (desconto automático)
- [ ] Máquina ↔ Apontamento (histórico de uso)
- [ ] Dashboard de safra (agregação completa)
- [ ] Testes end-to-end (workflow completo)

### Frontend (Validação + UX)
- [ ] Permissões em diálogos destrutivos
- [ ] Timeline visual de fases
- [ ] Widget de alertas
- [ ] Dashboard financeiro por safra
- [ ] Integração de custos na safra
- [ ] Integração de receitas na safra

