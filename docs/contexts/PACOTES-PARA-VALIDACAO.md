# Validação de Pacotes e Preços — AgroSaaS

## Objetivo

Este documento resume os **6 pacotes de assinatura** propostos para validação com stakeholders antes da implementação no sistema de billing.

---

## Resumo Executivo

| Pacote | Preço Proposto | Público-Alvo | Margem Estimada |
|--------|---------------|-------------|-----------------|
| **Produtor** | R$ 49/mês | Pequeno produtor (500-5.000 ha) | 60% |
| **Gestão** | R$ 149/mês | Fazenda média (5.000-20.000 ha) | 75% |
| **Pecuária** | R$ 129/mês | Pecuária (1.000-10.000 cabeças) | 70% |
| **Lavoura** | R$ 129/mês | Grãos/cana (2.000-15.000 ha) | 70% |
| **Rastreabilidade** | R$ 299/mês | Exportadores/certificados | 80% |
| **Enterprise** | Sob consulta | Grandes grupos/cooperativas | 85% |

---

## Perguntas para Validação

### 1. Precificação

**Contexto:** 
- Aegro cobra R$ 242/mês (só agrícola)
- BovControl cobra R$ 79-149/mês (só pecuária)
- Totvs cobra R$ 500-2.000/mês (ERP completo)

**Perguntas:**
- [ ] O preço de R$ 49/mês para o plano **Produtor** é atraente o suficiente para capturar pequenos produtores?
- [ ] O preço de R$ 149/mês para o plano **Gestão** compete adequadamente com Aegro (R$ 242)?
- [ ] Devemos oferecer **desconto anual** (ex: pague 10 meses, receba 12)?
- [ ] O preço do plano **Enterprise** deve ser público (ex: "a partir de R$ 999/mês") ou sempre sob consulta?

**Decisão Necessária:** Aprovar, ajustar ou rejeitar faixa de preços proposta.

---

### 2. Limites Operacionais

**Contexto:** Cada pacote tem limites de propriedades, usuários, hectares, animais.

**Perguntas:**
- [ ] Limite de 5.000 hectares para **Produtor** é adequado? (1.000-5.000 ha é o alvo)
- [ ] Limite de 5 usuários para **Produtor** é suficiente?
- [ ] Devemos permitir **usuários ilimitados** em todos os planos (custo marginal baixo)?
- [ ] Limite de 500 animais para **Produtor** é adequado?

**Decisão Necessária:** Aprovar ou ajustar limites por pacote.

---

### 3. Módulos Incluídos

**Contexto:** Cada pacote inclui módulos em níveis diferentes (Essencial, Profissional, Enterprise).

**Perguntas:**
- [ ] **Produtor** deve incluir **Pecuária Essencial** ou só Agrícola?
- [ ] **Lavoura** deve incluir **Pecuária** (muitas fazendas têm integração lavoura-pecuária)?
- [ ] **Rastreabilidade** deve incluir **todos os módulos** ou só rastreabilidade + compliance?
- [ ] Devemos permitir **módulos avulsos** como add-on (ex: só NF-e por R$ 19/mês)?

**Decisão Necessária:** Aprovar ou ajustar composição de cada pacote.

---

### 4. Add-ons

**Contexto:** Add-ons são módulos/recursos adicionais cobrados à parte.

**Add-ons Propostos:**
| Add-on | Preço | Pacotes Disponíveis |
|--------|-------|---------------------|
| NDVI Básico | +R$ 29/mês | Produtor |
| NF-e Avulsa | +R$ 19/mês | Produtor |
| App Mobile | +R$ 15/mês | Produtor |
| Conciliação Automática | +R$ 49/mês | Gestão, Lavoura |
| Crédito Rural | +R$ 39/mês | Gestão, Lavoura |
| Balança IoT | +R$ 79/mês | Pecuária |
| Agricultura de Precisão | +R$ 79/mês | Lavoura |
| Blockchain Customizado | +R$ 199/mês | Rastreabilidade |

**Perguntas:**
- [ ] Preços dos add-ons estão adequados?
- [ ] Devemos oferecer **bundle de add-ons** com desconto?
- [ ] Algum add-on deveria ser **incluso** no pacote base?

**Decisão Necessária:** Aprovar, ajustar ou remover add-ons propostos.

---

### 5. Programa de Fidelidade

**Contexto:** Proposta de desconto por compromisso de longo prazo.

**Proposta:**
| Contrato | Benefício |
|----------|-----------|
| 12 meses | 1 mês grátis (pague 11, receba 12) |
| 24 meses | 2 meses grátis + upgrade de pacote por 3 meses |
| 36 meses | 3 meses grátis + customizações inclusas |

**Perguntas:**
- [ ] Benefícios são atraentes o suficiente?
- [ ] Devemos oferecer **desconto adicional para pagamento anual antecipado**?
- [ ] Devemos incluir **treinamento** nos planos de 12+ meses?

**Decisão Necessária:** Aprovar ou ajustar programa de fidelidade.

---

### 6. Período de Teste

**Contexto:** Definir política de trial/free tier.

**Opções:**
| Modelo | Vantagens | Desvantagens |
|--------|-----------|--------------|
| **14 dias grátis** | Simples, padrão de mercado | Pode não ser tempo suficiente para testar |
| **30 dias grátis** | Tempo adequado para ciclo agrícola | Maior custo de aquisição |
| **Free tier limitado** | Usuário pode usar indefinidamente (com limites) | Maior custo de infraestrutura |
| **Demo guiada** | Controle total da experiência | Requer equipe de vendas |

**Proposta:** 14 dias grátis + demo guiada sob demanda

**Perguntas:**
- [ ] Qual modelo adotar?
- [ ] Devemos pedir **cartão de crédito** no trial?
- [ ] Devemos limitar funcionalidades no trial?

**Decisão Necessária:** Escolher modelo de trial.

---

### 7. Estratégia de Entrada

**Contexto:** Como lançar os pacotes no mercado.

**Opções:**
1. **Lançamento gradual** — Começar com 1-2 pacotes, validar, expandir
2. **Lançamento completo** — Todos os 6 pacotes de uma vez
3. **Beta fechado** — 10-20 produtores por 3 meses, depois lançamento público

**Proposta:** Beta fechado (3 meses) → Lançamento gradual (Produtor + Gestão) → Expansão

**Perguntas:**
- [ ] Qual estratégia adotar?
- [ ] Quantos produtores no beta?
- [ ] Quais pacotes lançar primeiro?

**Decisão Necessária:** Definir estratégia de go-to-market.

---

## Checklist de Aprovação

### Aprovação de Produto

- [ ] **Head de Produto** — Pacotes e composição
- [ ] **Head de Vendas** — Preços e argumentos de venda
- [ ] **Head de Marketing** — Posicionamento e naming
- [ ] **CEO/Founders** — Estratégia geral

### Aprovação Técnica

- [ ] **CTO** — Viabilidade técnica dos limites
- [ ] **Head de Billing** — Configuração no Stripe/Asaas
- [ ] **Head de Suporte** — Capacidade de atendimento

---

## Próximos Passos Após Aprovação

1. **Configurar billing** — Stripe/Asaas com planos e add-ons
2. **Criar páginas de venda** — Landing page por pacote
3. **Treinar equipe de vendas** — Argumentos, objeções, concorrência
4. **Preparar material de marketing** — Comparativos, cases, demos
5. **Iniciar beta testing** — 10-20 produtores por 3 meses

---

## Anexos

### A. Comparativo com Concorrência

| Recurso | AgroSaaS | Aegro | BovControl | Totvs |
|---------|----------|-------|------------|-------|
| Preço base | R$ 49 | R$ 242 | R$ 79 | R$ 500+ |
| Agrícola | ✅ | ✅ | ❌ | ✅ |
| Pecuária | ✅ | ❌ | ✅ | ✅ |
| Financeiro | ✅ | ✅ | ❌ | ✅ |
| Compliance | ✅ | ❌ | ❌ | ⚠️ |
| Blockchain | ✅ | ❌ | ❌ | ❌ |
| Mobile | ✅ | ✅ | ✅ | ⚠️ |

### B. Projeção de Receita (Cenário Conservador)

| Ano | Assinantes | Ticket Médio | Receita Mensal | Receita Anual |
|-----|------------|--------------|----------------|---------------|
| 1 | 100 | R$ 99 | R$ 9.900 | R$ 118.800 |
| 2 | 500 | R$ 129 | R$ 64.500 | R$ 774.000 |
| 3 | 2.000 | R$ 149 | R$ 298.000 | R$ 3.576.000 |

**Premissas:**
- Ano 1: 100 assinantes (70% Produtor, 20% Gestão, 10% Pecuária)
- Ano 2: 500 assinantes (50% Produtor, 30% Gestão, 20% outros)
- Ano 3: 2.000 assinantes (40% Produtor, 30% Gestão, 30% outros)

### C. Custos Estimados por Assinante

| Custo | Valor Unitário |
|-------|----------------|
| Infraestrutura (AWS/Azure) | R$ 5-15/mês |
| Suporte | R$ 3-8/mês |
| Aquisição (CAC) | R$ 50-200 (uma vez) |
| Billing (Stripe/Asaas) | 3-5% da receita |

**Margem Bruta Estimada:** 60-85% (dependendo do pacote)

---

**Documento para:** Reunião de Validação de Pacotes  
**Data da Reunião:** [A definir]  
**Participantes:** Produto, Vendas, Marketing, Técnico, CEO  
**Decisão Necessária:** Aprovar, ajustar ou rejeitar proposta de pacotes e preços
