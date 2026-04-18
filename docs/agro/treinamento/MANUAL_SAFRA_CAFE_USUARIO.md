# 📚 Manual do Usuário: Como Criar e Gerenciar uma Safra de Café

## Introdução

Este manual guia você passo a passo para criar uma safra de café na aplicação, desde o planejamento inicial até o registro final do café pronto para venda.

**Tempo estimado:** 30 minutos para primeira safra (depois fica mais rápido)

---

## 🎬 PASSO 1: Criar a Safra

### Onde encontrar?
**Menu: Agricultura → ⑥ Resultados → Resumo de Safras**

### O que é um Cultivo?
Uma safra pode ter **um ou mais cultivos**. Cada cultivo representa uma **cultura específica** plantada em determinados talhões durante aquela safra. Exemplos:

- Safra 2025 → **Cultivo 1:** Café Bourbon no Talhão A1 (40 ha)
- Safra 2025 → **Cultivo 2:** Milho Safrinha no Talhão B2 (10 ha)

Isso permite rastrear custos, operações e orçamento **separadamente por cultura**.

### Como criar?
1. Clique em **"+ Nova Safra"** (botão no topo)
2. Um diálogo abre com um **formulário único** — preencha:

#### Campo: Ano Agrícola
| Campo | O que é | Exemplo |
|-------|---------|---------|
| **Ano Agrícola** | Identificação temporal da safra | "2025" ou "2025/26" |

#### Seção: Cultivos
Adicione **pelo menos um cultivo** clicando em **"+ Cultivo"**. Para cada cultivo:

| Campo | O que é | Exemplo |
|-------|---------|---------|
| **Cultura** | Tipo de plantação (dropdown) | "Café", "Milho", "Soja" |
| **Cultivar** | Variedade específica (opcional) | "Bourbon", "Catuaí", "Mundo Novo" |
| **Talhões** | Selecione um ou mais talhões | "Talhão A1" |
| **Área a Plantar (ha)** | Área real plantada naquele talhão | "40" — auto-preenchida com a área total do talhão |
| **Meta de Produtividade (sc/ha)** | Produtividade esperada (opcional) | "30" |
| **Consorciado** | Marca se este cultivo compartilha espaço com outro (checkbox) | ☐ (desmarcar = uso exclusivo) |
| **Início da ocupação** | Data quando o cultivo começa a ocupar o talhão (opcional) | "01/09/2025" |
| **Fim da ocupação** | Data quando o cultivo deixa de ocupar o talhão (opcional) | "30/08/2026" |

> 💡 **Dica:** Quando você seleciona um talhão, o campo "Área a Plantar" já vem preenchido com a área total cadastrada. Se for plantar menos (ex: pousio), edit o campo.

> ⚠️ **Validação:** A área a plantar não pode ser maior que a área real do talhão.

### ⚠️ O que é "Consorciado"?

**Consorciado** significa que este cultivo **compartilha o mesmo espaço físico** com outro cultivo no mesmo talhão e período.

**Exemplos:**
- Café (perene) + Milho Safrinha (temporário) no mesmo talhão = ambos marcados como consorciados
- Milho + Braquiária plantados juntos = ambos consorciados
- Soja sozinha no talhão = **não** marcar como consorciado

**Como funciona?**
- **SEM marcar "Consorciado":** O sistema não permite que dois cultivos ocupem a mesma área no mesmo período
- **MARCANDO "Consorciado":** Indica que os cultivos vão dividir o espaço, então não há limite de ocupação

**Regra prática:**
Se você plantar cultura A (30 ha) e cultura B (30 ha) no mesmo talhão de 50 ha **no mesmo período**, você DEVE marcar ambas como consorciadas. Caso contrário, o sistema vai rejeitar, alertando que a ocupação total ultrapassaria a capacidade do talhão.

### 📅 O que é "Período de Ocupação"?

**Início da ocupação** e **Fim da ocupação** definem quando o cultivo está ativo no talhão.

**Por que isso importa?**
- Permite registrar **rotação de culturas** (diferentes cultivos em períodos diferentes)
- Permite registrar **pousio** (períodos sem produção)
- Garante que a validação de consorciado seja **temporal** (só valida sobreposição no mesmo período)

**Exemplos:**

**Exemplo 1 — Rotação (sem sobreposição):**
```
Talhão A1:
├─ Cultivo: Café Bourbon
│  ├─ Início: 01/jan/2024
│  └─ Fim: 31/dez/2024
└─ Cultivo: Milho
   ├─ Início: 01/jan/2025
   └─ Fim: 31/dez/2025
   
Resultado: ✅ Válido (períodos não se sobrepõem)
```

**Exemplo 2 — Consórcio (sobreposição no mesmo período):**
```
Talhão A1 (50 ha):
├─ Cultivo: Café (40 ha)
│  ├─ Consorciado: ✓ (marcado)
│  ├─ Início: 01/jan/2024
│  └─ Fim: 31/dez/2024
└─ Cultivo: Milho Safrinha (30 ha)
   ├─ Consorciado: ✓ (marcado)
   ├─ Início: 01/jan/2024
   └─ Fim: 31/dez/2024
   
Resultado: ✅ Válido (ambos consorciados + períodos iguais)
```

**Exemplo 3 — Pousio:**
```
Talhão A1:
├─ Cultivo: Soja (período 1)
│  ├─ Início: 01/out/2024
│  └─ Fim: 28/fev/2025
└─ Cultivo: POUSIO (período 2)
   ├─ Início: 01/mar/2025
   └─ Fim: 31/ago/2025
   
Resultado: ✅ Histórico completo do talhão
```

> 💡 **Dica:** Se deixar os campos de data vazios, o sistema entende que o cultivo está "sempre ativo" durante a safra.

3. Após adicionar os cultivos, clique em **"Criar Safra"** (botão no rodapé)

✅ Sua safra foi criada com os cultivos e talhões já vinculados!

---

### 1.1 - Por que a área por talhão importa?

Ao informar a área de cada cultivo em cada talhão, o sistema consegue:
- Calcular o **custo por hectare** corretamente no orçamento
- Identificar **qual cultivo ocupa qual parte** da fazenda
- Fazer **rotação de culturas** no mesmo talhão em safras diferentes

**Exemplo:**
```
Talhão A1 (cadastrado com 100 ha)
├─ Cultivo: Café Bourbon → 80 ha (deixando 20 ha em pousio)
└─ Cultivo: Milho Safrinha → não entra neste talhão

Talhão B2 (cadastrado com 50 ha)
└─ Cultivo: Milho Safrinha → 50 ha (área toda)
```

**Resultado:**
- Café: 80 ha → orçamento calculado sobre 80 ha
- Milho: 50 ha → orçamento calculado sobre 50 ha

---

## 💰 PASSO 2: Planejar Custos (Orçamento)

### O que é?
Você define quanto vai gastar durante toda a safra para que depois possa comparar com o que realmente gastou. É como um planejamento financeiro.

### Onde encontrar?
**Menu: Agricultura → ① Planejamento → Orçamento de Safra**

Ou na página da safra: clique na aba/botão **"Orçamento"**

### O que fazer?

#### 2.1 - Adicionar cada tipo de custo

Clique em **"+ Adicionar Item"** e preencha:

| Categoria | O que incluir | Exemplo de Custo |
|-----------|--------------|------------------|
| **SEMENTE** | Sementes ou mudas que você vai plantar | R$ 1.200 (200 mudas × R$ 6) |
| **FERTILIZANTE** | Adubo que a planta precisa | R$ 2.000 (4 aplicações) |
| **DEFENSIVO** | Veneno/fungicida contra pragas e doenças | R$ 800 (5 pulverizações) |
| **COMBUSTIVEL** | Diesel/gasolina para máquinas | R$ 1.500 (colheitadeira, trator) |
| **MAO_DE_OBRA** | Salários de trabalhadores | R$ 4.000 (3 meses × salário) |
| **SERVICO** | Trabalho feito por terceiros | R$ 1.000 (preparação de solo) |
| **OUTROS** | Imprevistos, emergências | R$ 500 |

**Exemplo de entrada:**
```
Categoria: FERTILIZANTE
Cultivo: Café Bourbon (opcional — deixe em branco para aplicar a todos os cultivos)
Descrição: Adubo granulado para café
Quantidade: 500
Unidade: kg
Custo Unitário: R$ 4,00
→ Custo Total: R$ 2.000 (calculado automaticamente)
```

> 💡 **Campo Cultivo no Orçamento:** Se sua safra tem mais de um cultivo (ex: Café + Milho), você pode vincular cada item de custo a um cultivo específico. Isso permite visualizar o orçamento separado por cultura.

> 💡 **Rastreamento por Cultivo:** O sistema vincula automaticamente operações, despesas, colheita e beneficiamento ao cultivo correto. Toda a cadeia de valor — do plantio à venda — fica rastreável por cultura.

#### 2.2 - Onde você vê o resultado?
- **Custo Total Previsto:** Soma de tudo que você colocou
- **Custo por Hectare:** Divide pelo tamanho da área
- Exemplo: R$ 10.000 ÷ 5 hectares = **R$ 2.000 por hectare**

✅ Agora você tem um planejamento de quanto vai gastar!

---

### 2.3 - Rastreamento Completo por Cultivo

O sistema rastreia **toda a cadeia de valor** vinculada ao cultivo específico:

| Módulo | Campo Cultivo | O que permite |
|--------|--------------|---------------|
| **Orçamento** | ✅ Vincula por cultivo | Custo planejado por cultura |
| **Despesas Financeiras** | ✅ Vincula por cultivo | Custo real por cultura |
| **Operações de Campo** | ✅ Vincula por cultivo | Custo operacional por cultura |
| **Romaneio de Colheita** | ✅ Vincula por cultivo | Produção por cultura |
| **Beneficiamento** | ✅ Vincula por cultivo | Processamento por cultura |

> ✅ **Resultado:** Com todos os vínculos preenchidos, o sistema consegue calcular o **lucro real por cultivo** dentro da mesma safra.

---

## 🚜 PASSO 3: Registrar Operações (Atividades do Campo)

### O que é?
Cada atividade que você faz no campo (plantar, adubar, pulverizar, colher) fica registrada aqui. Também mostra quanto cada uma custou.

### Onde encontrar?
**Menu: Agricultura → ② Operação → Operações de Campo**

Ou na página da safra: clique na aba/botão **"Operações"**

### Tipos de Operações (no ciclo do café)

#### 3.1 - PLANTIO (primeira operação)
**Quando fazer:** Depois que o solo está preparado

**O que registrar:**
```
Tipo: PLANTIO
Cultivo: Café Bourbon (opcional — vincule à cultura específica se houver mais de uma)
Data: 15/09/2025
Descrição: Plantio de mudas de café no talhão A1
Custo Total: R$ 1.200
Observações: Solo estava úmido, condições ideais
```

> 💡 **Campo Cultivo nas Operações:** Em safras com múltiplos cultivos, selecione o cultivo correspondente para que os custos operacionais sejam atribuídos corretamente.

**Para café:** Espaçamento típico é **3,5m × 0,7m**  
(significa: 3,5 metros entre linhas, 0,7 entre mudas)

#### 3.2 - ADUBAÇÃO (durante o crescimento)
**Quando fazer:** Normalmente 3-4 vezes ao ano

**O que registrar:**
```
Tipo: ADUBACAO
Data: 15/11/2025
Descrição: 1ª adubação com NPK 20-5-20
Quantidade: 500 (kg)
Custo Total: R$ 2.000
Observações: Distribuído uniformemente no talhão
```

#### 3.3 - APLICAÇÃO DE DEFENSIVO (contra pragas/doenças)
**Quando fazer:** Conforme necessidade (varia: a cada 2 semanas até mensalmente)

**O que registrar:**
```
Tipo: PULVERIZACAO
Data: 01/12/2025
Descrição: Pulverização contra ferrugem do café
Quantidade: 200 (litros - diluído)
Custo Total: R$ 400
Observações: Temperatura ideal para aplicação
```

**Pragas/doenças comuns do café:**
- 🦗 **Broca:** inseto que entra no fruto
- 🍂 **Ferrugem:** manchas nas folhas
- 🕷️ **Ácaro:** danifica folhas
- 🌪️ **Oidio:** fungo branco nas folhas

#### 3.4 - COLHEITA (a operação mais importante)
**Quando fazer:** Entre 6-8 meses após plantio (café começa em ~2 anos)

**O que registrar:**
```
Tipo: COLHEITA
Data: 01/06/2026 (até 30/08/2026)
Descrição: Colheita mecanizada do café
Quantidade: 600 (sacas - unidade padrão)
Custo Total: R$ 3.000
Observações: Colheita inteira do talhão, qualidade boa
```

> 📌 **Importante:** Após registrar colheita aqui, você deve ir para **"Romaneios"** para registrar cada lote individualmente. Veja PASSO 5.

---

## 🔬 PASSO 4: Monitorar a Saúde (Fenologia, Monitoramento, NDVI)

### O que é?
Você acompanha se a planta está saudável e se está no momento certo para colher. É como uma "checklist de saúde" contínua.

### 4.1 - Fenologia (Estágios de Crescimento)
**Menu: Agricultura → ⑤ Monitoramento → Fenologia**

**O que é:** Rastrear em qual estágio a planta está:

| Estágio | O que significa | Quando acontece |
|---------|-----------------|-----------------|
| **Brotação** | Novas folhas saindo | Janeiro-fevereiro |
| **Floração** | Flores brancas aparecendo | Setembro-outubro |
| **Granação** | Frutos pequenos formando | Novembro-dezembro |
| **Maturação** | Frutos ficando vermelhos/roxos | Maio-junho |

**Como usar:** Clique em cada estágio conforme observar no campo. A aplicação mantém um histórico.

### 4.2 - Monitoramento (Pragas e Doenças)
**Menu: Agricultura → ② Operação → Pragas & Doenças**

**O que fazer:** Registre cada vez que encontrar problema:
```
Data: 01/12/2025
Praga: Broca do café
Nível: Baixo (menos de 5% dos frutos)
Ação tomada: Pulverizou defensivo XYZ
Próxima inspeção: 15/12/2025
```

### 4.3 - NDVI (Imagem de Satélite)
**Menu: Agricultura → ⑤ Monitoramento → Índices de Vegetação (NDVI)**

**O que é:** Foto de satélite que mostra a saúde da plantação (verde escuro = saudável, amarelo = com problemas)

> 💡 Útil para identificar trechos do talhão com problemas de nutrição ou água.

---

## 📝 PASSO 5: Registrar Colheita em Detalhes (Romaneios)

### O que é?
Enquanto você colhe, registra cada lote (um "romaneio" é um documento que rastreia aquele lote desde a colheita até o armazenamento).

### Onde encontrar?
**Menu: Agricultura → ③ Colheita → Romaneios (Colheita)**

### O que fazer?

Clique em **"+ Novo Romaneio"** para cada lote colhido:

```
Data: 01/06/2026
Talhão: Talhão A1
Tipo de Cereja: Cereja Vermelha
Quantidade: 150 sacas (ou kg)
Local Armazenamento: Terreiro 1
Qualidade: Boa (sem defeitos aparentes)
Observações: Dia ensolarado, frutos bem maduros
```

**Por que isso importa?**
- Rastreia **quem colheu**, **quando**, **quanto**
- Marca ponto de origem para café processado depois
- Essencial se você vender para diferentes compradores

---

## ☕ PASSO 6: Processar o Café (Beneficiamento) - *SÓ PARA CAFÉ*

### O que é?
Transformar café fresco em café pronto para vender. Inclui:
1. 🌞 Secagem (reduzir água de ~60% para ~11%)
2. 🔧 Descascamento (tirar casca/polpa)
3. 🔍 Classificação (separar por tamanho/qualidade)
4. 👜 Embalagem (colocar em sacos de 60kg)

### Onde encontrar?
**Menu: Agricultura → ④ Pós-Colheita → Beneficiamento**

### O que fazer?

#### 6.1 - Registrar Entrada (Lote chegando)
```
Data: 01/06/2026
Lote ID: ROMANEIO-001 (vem do passo anterior)
Tipo Entrada: Cereja Vermelha
Quantidade Bruta: 150 sacas
Teor Água: 55% (medido com umidômetro)
Observações: Lote sem defeitos, pronto para secar
```

#### 6.2 - Registrar Processos (conforme avança)

**Secagem:**
```
Data: 06/06/2026 (até 20/06/2026)
Processo: SECAGEM
Temperatura: 60°C
Duração: 15 dias (até teor de água chegar a ~11%)
Observações: Revirado 3 vezes ao dia
```

**Descascamento:**
```
Data: 21/06/2026
Processo: DESCASCAMENTO
Máquina: Descascadora XYZ
Resíduo: 25 sacas (polpa/casca - pode virar fertilizante!)
Observações: Rendimento normal
```

**Classificação:**
```
Data: 21/06/2026
Processo: CLASSIFICACAO
Tipo Final: Café Peneira 16+
Quantidade Final: 100 sacas
Defeitos: 5 sacas (peneira pequena - vira café inferior)
Observações: Qualidade premium obtida
```

**Embalagem:**
```
Data: 22/06/2026
Processo: EMBALAGEM
Sacos 60kg: 100 unidades
Tipo Embalagem: Saco de juta padrão
Local Armazenamento: Armazém Principal
Observações: Pronto para venda
```

#### 6.3 - Resultado
```
ENTRADA: 150 sacas cereja (bruto)
SAÍDA: 100 sacas beneficiadas
PERDA NATURAL: 50 sacas (33%) 
→ Isso é normal! Café seca e perde peso.
```

---

## 📊 PASSO 7: Acompanhar Financeiro

### Onde encontrar?
Na página da safra → Botão **"Financeiro"**

### O que você vê?

| Item | Significado |
|------|-------------|
| **Orçado** | R$ 10.000 (quanto você planejou gastar) |
| **Realizado** | R$ 9.800 (quanto realmente gastou) |
| **Desvio** | -R$ 200 (economizou) |
| **Margem** | Receita - Despesa = seu lucro |

---

## ✅ PASSO 8: Finalizar a Safra

### Quando fazer?
Depois que todo café foi beneficiado e armazenado.

### O que fazer?

1. Na página da safra, clique em **"Mudar Status"**
2. Selecione **"ENCERRADA"**
3. Preencha dados finais:
   - Produtividade Real: 100 sacas beneficiadas
   - Observações: "Safra bem-sucedida, clima favorável"

4. Clique em **"Salvar"**

✅ Safra encerrada! Você tem registro completo.

---

## 📖 Resumo Visual do Fluxo

```
┌─────────────────────────────────────────────────────────────┐
│                    CICLO COMPLETO DE CAFÉ                   │
└─────────────────────────────────────────────────────────────┘

① CRIAR SAFRA (5 min)
   └─→ Nome, data, talhão, área

② PLANEJAR CUSTOS (10 min)
   └─→ Orçamento de sementes, adubo, defensivo, mão-de-obra

③ OPERAÇÕES DO CAMPO (contínuo, 6-12 meses)
   ├─→ Plantio
   ├─→ Adubação (3-4 vezes)
   ├─→ Pulverização (conforme necessidade)
   └─→ Colheita

④ MONITORAR (semanal, conforme necessário)
   ├─→ Fenologia (estágio da planta)
   ├─→ Monitoramento (pragas/doenças)
   └─→ NDVI (satélite)

⑤ REGISTRAR COLHEITA (durante colheita)
   └─→ Romaneios (lote por lote)

⑥ PROCESSAR CAFÉ (2-3 semanas)
   ├─→ Secagem
   ├─→ Descascamento
   ├─→ Classificação
   └─→ Embalagem

⑦ ACOMPANHAR FINANCEIRO (contínuo)
   └─→ Verificar custos vs orçado

⑧ FINALIZAR (1 dia)
   └─→ Marcar safra como ENCERRADA

```

---

## 🆘 Dúvidas Frequentes

### P: Quanto tempo uma safra de café leva?
**R:** De 2 a 3 anos da primeira safra viável após plantio. Depois, todo ano você colhe.

### P: Posso ter múltiplas operações no mesmo dia?
**R:** Sim, mas normalmente você faz uma por vez (ou poucas simultâneas em talhões diferentes).

### P: Onde vejo o café pronto para venda?
**R:** Na seção **"Estoque"** ou no **"Beneficiamento"** quando terminar o processamento.

### P: Preciso usar TODOS os campos?
**R:** Campos com * (asterisco) são obrigatórios. Outros são opcionais.

### P: Posso editar depois?
**R:** Sim! Clique no ícone de **lápis** ao lado de qualquer item.

### P: O que fazer se colher mais ou menos do planejado?
**R:** Sem problema! O sistema compara automático: orçado vs realizado. Você vê a diferença em "Desvio".

---

## 📞 Precisa de Ajuda?

- **Dúvida sobre como registrar algo:** Clique em **"?"** ao lado do campo
- **Erro ao salvar:** Verifique se todos os campos obrigatórios (* vermelha) foram preenchidos
- **Café não aparece no estoque:** Confirme que **Beneficiamento foi finalizado**

**Boa sorte com sua safra de café!** ☕
