# Guia Completo de Teste — Criação de Safra de Café (Do Planejamento ao Encerramento)

> **Objetivo:** Testar e validar todo o fluxo de criação e gestão de uma safra de café no AgroSaaS, alimentando cada cadastro necessário com dados realistas, validando cada fase, cada processo e cada integração do sistema.
>
> **Propriedade fictícia:** Fazenda Boa Esperança — 120 hectares — Região da Alta Mogiana (SP)
>
> **Safra:** 2025/2026 — Café Arábica Catuaí Vermelho

---

## ÍNDICE

1. [PRÉ-REQUISITOS — Cadastros Mestre](#1-pré-requisitos--cadastros-mestre)
2. [FASE 1 — Planejamento da Safra](#2-fase-1--planejamento-da-safra)
3. [FASE 2 — Preparo do Solo](#3-fase-2--preparo-do-solo)
4. [FASE 3 — Plantio](#4-fase-3--plantio)
5. [FASE 4 — Desenvolvimento](#5-fase-4--desenvolvimento)
6. [FASE 5 — Colheita](#6-fase-5--colheita)
7. [FASE 6 — Pós-Colheita (Beneficiamento)](#7-fase-6--pós-colheita-beneficiamento)
8. [FASE 7 — Encerramento](#8-fase-7--encerramento)
9. [Checklist Final de Validação](#9-checklist-final-de-validação)

---

## 1. PRÉ-REQUISITOS — Cadastros Mestre

Antes de criar qualquer safra, o sistema exige que os cadastros base estejam completos. Estes cadastros são reutilizáveis em todas as safras futuras. São os "pilares" da operação.

---
### 1.0 Cadastro de Glebas

**O que é:** Uma gleba é uma área de terra contínua dentro da fazenda, com características próprias de solo, topografia, variedade plantada e histórico de manejo. Todo o rastreio de operações, análises de solo e colheitas é feito por gleba.

**O que gera:** Ao cadastrar glebas, o sistema cria a base geográfica para vínculo com safras, cultivos, análises de solo e operações. Cada operação registrada na safra é atribuída a uma gleba específica.

**Caminho no sistema:** Cadastros → Áreas Rurais → Glebas → `+ Nova Gleba`

| # | Nome | Área (ha) | Solo | Declividade | Irrigação | Observação |
|---|------|-----------|------|-------------|-----------|------------|
| 1 | Gleba A1 — Nascente | 8,50 | Latossolo Vermelho | Suave ondulado (3–8%) | Não | Histórico de boa produtividade, cafezal adulto 12 anos |
| 2 | Gleba A2 — Morro | 6,20 | Latossolo Amarelo | Ondulado (8–20%) | Não | Solo ácido, necessita calagem frequente |
| 3 | Gleba B1 — Baixada | 12,00 | Argissolo Vermelho | Plano (0–3%) | Gotejamento | Alta fertilidade, colheita mecanizada possível |
| 4 | Gleba B2 — Terreirão | 9,80 | Latossolo Vermelho | Suave ondulado | Não | Replantio parcial em 2023, pés jovens misturados |
| 5 | Gleba C1 — Estrada | 7,40 | Nitossolo Vermelho | Plano | Não | Bordadura com eucalipto, proteção contra vento |
| 6 | Gleba C2 — Fundo | 11,30 | Latossolo Vermelho | Suave ondulado | Aspersão | Solo bem estruturado, alto potencial produtivo |
| 7 | Gleba D1 — Meia Encosta | 5,60 | Argissolo Amarelo | Forte ondulado (20–45%) | Não | Colheita manual obrigatória, terreno acidentado |
| 8 | Gleba D2 — Renovação | 4,90 | Latossolo Vermelho | Suave ondulado | Gotejamento | Plantio novo 2022, primeira produção plena em 2025 |
| 9 | Gleba E1 — Sede | 10,20 | Latossolo Vermelho | Plano | Não | Próximo ao beneficiamento, logística facilitada |
| 10 | Gleba E2 — Reserva | 3,80 | Cambissolo Háplico | Ondulado | Não | Solo raso, adubação complementar necessária, menor produção |

**Total: 79,70 ha cadastrados em glebas de café**

---

---

### 1.1 Cadastro de Áreas Rurais (Talhões)

**O que é:** Um talhão é a menor unidade geográfica de trabalho agrícola. Representa uma gleba específica dentro da fazenda, com características próprias de solo, topografia, variedade plantada e histórico de manejo. Todo o rastreio de operações, análises de solo e colheitas é feito por talhão.

**O que gera:** Ao cadastrar talhões, o sistema cria a base geográfica para vínculo com safras, cultivos, análises de solo e operações. Cada operação registrada na safra é atribuída a um talhão específico.

**Caminho no sistema:** Cadastros → Áreas Rurais → Talhões → `+ Novo`

| # | Nome | Área (ha) | Solo | Declividade | Irrigação | Observação |
|---|------|-----------|------|-------------|-----------|------------|
| 1 | Talhão A1 — Nascente | 8,50 | Latossolo Vermelho | Suave ondulado (3–8%) | Não | Histórico de boa produtividade, cafezal adulto 12 anos |
| 2 | Talhão A2 — Morro | 6,20 | Latossolo Amarelo | Ondulado (8–20%) | Não | Solo ácido, necessita calagem frequente |
| 3 | Talhão B1 — Baixada | 12,00 | Argissolo Vermelho | Plano (0–3%) | Gotejamento | Alta fertilidade, colheita mecanizada possível |
| 4 | Talhão B2 — Terreirão | 9,80 | Latossolo Vermelho | Suave ondulado | Não | Replantio parcial em 2023, pés jovens misturados |
| 5 | Talhão C1 — Estrada | 7,40 | Nitossolo Vermelho | Plano | Não | Bordadura com eucalipto, proteção contra vento |
| 6 | Talhão C2 — Fundo | 11,30 | Latossolo Vermelho | Suave ondulado | Aspersão | Solo bem estruturado, alto potencial produtivo |
| 7 | Talhão D1 — Meia Encosta | 5,60 | Argissolo Amarelo | Forte ondulado (20–45%) | Não | Colheita manual obrigatória, terreno acidentado |
| 8 | Talhão D2 — Renovação | 4,90 | Latossolo Vermelho | Suave ondulado | Gotejamento | Plantio novo 2022, primeira produção plena em 2025 |
| 9 | Talhão E1 — Sede | 10,20 | Latossolo Vermelho | Plano | Não | Próximo ao beneficiamento, logística facilitada |
| 10 | Talhão E2 — Reserva | 3,80 | Cambissolo Háplico | Ondulado | Não | Solo raso, adubação complementar necessária, menor produção |

**Total: 79,70 ha cadastrados em talhões de café**

---

### 1.2 Cadastro de Pessoas (Operadores, Agrônomos, Fornecedores)

**O que é:** Registro de todas as pessoas físicas e jurídicas que interagem com a fazenda: trabalhadores rurais, operadores de máquinas, agrônomos responsáveis, veterinários, fornecedores de insumos e compradores.

**O que gera:** Vínculos com operações agrícolas (quem executou), emissão de receituário agronômico (quem assinou), rastreabilidade de responsabilidade, histórico por operador.

**Caminho no sistema:** Cadastros → Pessoas → `+ Nova Pessoa`

| # | Nome | Tipo | CPF/CNPJ | Função | Registro | Contato |
|---|------|------|----------|--------|----------|---------|
| 1 | João Aparecido Ferreira | Pessoa Física | 412.305.678-90 | Tratorista / Operador de Máquinas | — | (18) 99812-3456 |
| 2 | Maria das Graças Silva | Pessoa Física | 523.416.789-01 | Colhedora de Café (turma A) | — | (18) 99723-4567 |
| 3 | Pedro Henrique Souza | Pessoa Física | 634.527.890-12 | Encarregado de Campo | — | (18) 99634-5678 |
| 4 | Dr. Carlos Eduardo Motta | Pessoa Física | 745.638.901-23 | Engenheiro Agrônomo | CREA-SP 1.234.567 | (11) 98745-6789 |
| 5 | Antônia Rodrigues Lima | Pessoa Física | 856.749.012-34 | Catadora — Turma B | — | (18) 99856-7890 |
| 6 | Agro Insumos Mogiana Ltda | Pessoa Jurídica | 12.345.678/0001-90 | Fornecedor de Insumos | — | (19) 3333-1234 |
| 7 | Cooperativa Café Mogiana | Pessoa Jurídica | 23.456.789/0001-01 | Comprador / Cooperativa | — | (19) 3444-5678 |
| 8 | Mecânica e Implementos Ribeiro | Pessoa Jurídica | 34.567.890/0001-12 | Prestador de Serviço (mecânica) | — | (18) 3555-6789 |
| 9 | Laboratório Solotech Análises | Pessoa Jurídica | 45.678.901/0001-23 | Laboratório de Solo | — | (19) 3666-7890 |
| 10 | Rafael Augusto Cunha | Pessoa Física | 967.860.123-56 | Motorista / Transporte de Café | — | (18) 99967-8901 |

---

### 1.3 Cadastro de Produtos / Insumos

**O que é:** Todos os insumos agrícolas utilizados nas operações de campo: fertilizantes, defensivos, corretivos de solo, sementes/mudas e materiais auxiliares. Cada produto é cadastrado com suas informações técnicas, comerciais e de segurança.

**O que gera:** Ao registrar uma operação com insumo, o sistema calcula automaticamente: dose por hectare × área = quantidade total; quantidade × custo unitário = custo total da operação. O produto com carência ativa bloqueia a colheita (rastreabilidade).

**Caminho no sistema:** Cadastros → Produtos → `+ Novo Produto`

| # | Nome Comercial | Princípio Ativo | Tipo | Unidade | Preço Unit. | Carência (dias) | Classe Tox. |
|---|---------------|-----------------|------|---------|-------------|-----------------|-------------|
| 1 | Calcário Dolomítico FILLER | CaMg(CO₃)₂ | Corretivo | t | R$ 180,00/t | 0 | — |
| 2 | MAP Fosfato Monoamônico | N+P₂O₅ (12-61-0) | Fertilizante | kg | R$ 4,20/kg | 0 | — |
| 3 | KCl Cloreto de Potássio | K₂O (0-0-60) | Fertilizante | kg | R$ 3,10/kg | 0 | — |
| 4 | Ureia Agrícola 46% | N (46-0-0) | Fertilizante | kg | R$ 2,80/kg | 0 | — |
| 5 | Roundup Original DI | Glifosato 480g/L | Herbicida | L | R$ 18,50/L | 30 | III — Média |
| 6 | Connect (espalhante) | Óleo mineral 727g/L | Adjuvante | L | R$ 22,00/L | 0 | IV — Baixa |
| 7 | Lorsban 480 BR | Clorpirifós 480g/L | Inseticida | L | R$ 45,00/L | 21 | II — Alta |
| 8 | Nimbus (óleo mineral) | Óleo mineral 428g/L | Adjuvante/Protetor | L | R$ 19,00/L | 0 | IV — Baixa |
| 9 | Folicur 200 EC | Tebuconazol 200g/L | Fungicida | L | R$ 67,00/L | 14 | III — Média |
| 10 | YaraMila Complexo 20-05-20 | NPK + micronutrientes | Fertilizante Foliar | kg | R$ 5,40/kg | 0 | — |

---

### 1.4 Cadastro de Máquinas / Equipamentos

**O que é:** Registro do parque de máquinas da propriedade: tratores, colhedoras, pulverizadores e implementos. Cada máquina é vinculada às operações agrícolas para rastreio de uso, horas trabalhadas e custo de operação.

**O que gera:** Ao vincular uma máquina a uma operação, o sistema registra qual equipamento foi usado, permitindo calcular custo/hora, histórico de uso por talhão e planejar manutenções preventivas.

**Caminho no sistema:** Frota → Máquinas → `+ Nova Máquina`

| # | Descrição | Marca | Modelo | Ano | HP/CV | Patrimônio | Custo/hora |
|---|-----------|-------|--------|-----|-------|------------|------------|
| 1 | Trator Principal | John Deere | 6120M | 2021 | 120cv | FAZ-001 | R$ 95,00 |
| 2 | Trator Auxiliar | Massey Ferguson | 4708 | 2019 | 85cv | FAZ-002 | R$ 75,00 |
| 3 | Colhedora de Café | JACTO | K3 Plus | 2022 | — | FAZ-003 | R$ 220,00 |
| 4 | Pulverizador Tratorizado | Jacto | Condor AM-14 | 2020 | — | FAZ-004 | R$ 40,00 |
| 5 | Grade Aradora | Baldan | GGTA 28×26" | 2018 | — | FAZ-005 | R$ 15,00 |
| 6 | Grade Niveladora | Baldan | GNL 28×20" | 2019 | — | FAZ-006 | R$ 12,00 |
| 7 | Roçadeira Lateral | Herder | RE 180 | 2021 | — | FAZ-007 | R$ 18,00 |
| 8 | Distribuidor de Calcário | Jan | DCN 3000 | 2020 | — | FAZ-008 | R$ 22,00 |
| 9 | Caminhão Truck | Mercedes | Atego 1719 | 2018 | — | FAZ-009 | R$ 55,00/h |
| 10 | Microscultivador Elétrico | Jacto | LHD | 2023 | — | FAZ-010 | R$ 30,00 |

---

### 1.5 Cadastro de Variedades / Cultivares

**O que é:** Registro das variedades de café cultivadas na propriedade, com suas características agronômicas. Isso permite ao sistema filtrar recomendações técnicas específicas por cultivar.

**O que gera:** Identidade genética da safra — usada em receituário agronômico, rastreabilidade de lote, comparativo de produtividade por cultivar entre safras.

**Caminho no sistema:** Cadastros → Cultivares → `+ Nova Cultivar`

| # | Cultivar | Espécie | Porte | Maturação | Produtividade Média | Resistência | Observação |
|---|---------|---------|-------|-----------|---------------------|-------------|------------|
| 1 | Catuaí Vermelho IAC 144 | Coffea arabica | Baixo | Média | 40–60 sc/ha | Ferrugem: média | Variedade principal da fazenda |
| 2 | Catuaí Amarelo IAC 62 | Coffea arabica | Baixo | Precoce | 38–55 sc/ha | Ferrugem: média | Talhões B1 e C2 |
| 3 | Mundo Novo IAC 379-19 | Coffea arabica | Alto | Tardia | 35–50 sc/ha | Ferrugem: baixa | Talhões antigos A1 e A2 |
| 4 | Obatã IAC 1669-20 | Coffea arabica | Médio | Média-tardia | 45–65 sc/ha | Ferrugem: alta | Talhão D2 (renovação) |
| 5 | Topázio MG-1190 | Coffea arabica | Baixo | Precoce | 50–70 sc/ha | Ferrugem: alta | Talhão E1 (sede) |
| 6 | Catiguá MG3 | Coffea arabica | Médio | Média | 42–58 sc/ha | Ferrugem: alta, CBD: média | Novo plantio em avaliação |
| 7 | Arara IAC 517 | Coffea arabica | Médio | Precoce-média | 55–75 sc/ha | Ferrugem: muito alta | Alta produtividade, avaliação 2024 |
| 8 | Paraíso MG H 419-1 | Coffea arabica | Baixo-médio | Média | 50–68 sc/ha | Ferrugem: muito alta | Talhão C1 (bordadura) |
| 9 | IPR 100 | Coffea arabica | Baixo | Média | 45–60 sc/ha | Ferrugem: alta | Possível introdução |
| 10 | Travessia | Coffea arabica | Médio | Tardia | 40–55 sc/ha | Ferrugem: alta, Nematóide: média | Solo E2 (reserva, solo raso) |

---

## 2. FASE 1 — PLANEJAMENTO DA SAFRA

### O que é esta fase

O planejamento é a etapa estratégica anterior a qualquer ação de campo. É onde o produtor define **o que vai plantar, onde, quanto espera produzir e quanto pode gastar**. No sistema, a safra nasce no status `PLANEJADA` e permanece aqui até que as primeiras ações de preparo de solo sejam iniciadas.

### O que o sistema cria nesta fase

- Registro da safra com `status = PLANEJADA`
- Vínculo da safra com um ou mais cultivos (multi-cultivo)
- Cada cultivo vincula-se a um ou mais talhões via `CultivoArea`
- Orçamento estimado por operação
- Checklist de planejamento gerado automaticamente com itens padrão

### Como criar a Safra

**Caminho:** Agrícola → Safras → `+ Nova Safra`

#### Dados da Safra

| Campo | Valor |
|-------|-------|
| Ano Safra | 2025/2026 |
| Observações | Safra de café arábica — foco em qualidade especial. Meta: 50 sc/ha nos talhões plenos, 35 sc/ha no talhão D2 (jovem). Investimento total estimado: R$ 320.000,00. |

#### Cultivo Principal — Catuaí Vermelho

| Campo | Valor |
|-------|-------|
| Cultura | Café |
| Cultivar | Catuaí Vermelho IAC 144 |
| Sistema de Plantio | Convencional (3,5m × 0,7m = 4.082 pés/ha) |
| Produtividade Meta | 50 sc/ha |
| Data Início Prevista | 01/04/2025 |
| Data Fim Prevista | 30/06/2026 |
| Consorciado | Não |

#### Vínculo Cultivo × Talhões (CultivoArea)

| Talhão | Área (ha) | Produtividade Meta | Observação |
|--------|-----------|--------------------|------------|
| Talhão A1 — Nascente | 8,50 ha | 50 sc/ha | Cafezal adulto — plena produção |
| Talhão A2 — Morro | 6,20 ha | 42 sc/ha | Solo ácido — aguarda calagem |
| Talhão B1 — Baixada | 12,00 ha | 55 sc/ha | Melhor talhão da fazenda |
| Talhão B2 — Terreirão | 9,80 ha | 40 sc/ha | Pés jovens reduzem média |
| Talhão C1 — Estrada | 7,40 ha | 48 sc/ha | Boa estrutura |
| Talhão C2 — Fundo | 11,30 ha | 52 sc/ha | Alto potencial |
| Talhão D1 — Meia Encosta | 5,60 ha | 38 sc/ha | Terreno acidentado |
| Talhão D2 — Renovação | 4,90 ha | 35 sc/ha | Pés jovens |
| Talhão E1 — Sede | 10,20 ha | 50 sc/ha | Logística facilitada |
| Talhão E2 — Reserva | 3,80 ha | 30 sc/ha | Solo raso |

**Área total: 79,70 ha | Produção estimada: ~3.680 sc de café beneficiado**

---

### 2.1 Orçamento da Safra

**O que é:** Estimativa financeira de todos os custos da safra antes de qualquer execução. Serve como referência para comparar com os custos reais ao final da safra.

**O que gera:** Benchmark de custo por hectare, por fase, por tipo de operação. Ao final, o sistema compara orçado vs. realizado automaticamente.

**Caminho:** Agrícola → Safras → [Safra 2025/26] → Módulo Orçamento

| # | Operação | Fase | Unid. | Qtd. | Custo Unit. | Total Estimado |
|---|----------|------|-------|------|-------------|----------------|
| 1 | Análise de Solo (10 talhões) | Planejamento | un | 10 | R$ 180,00 | R$ 1.800,00 |
| 2 | Calagem (2 t/ha × 79,7 ha) | Preparo Solo | t | 159,4 | R$ 180,00 | R$ 28.692,00 |
| 3 | Adubação de Formação NPK | Plantio | kg | 8.000 | R$ 4,50 | R$ 36.000,00 |
| 4 | Adubação de Cobertura (3×) | Desenvolvimento | kg | 24.000 | R$ 2,80 | R$ 67.200,00 |
| 5 | Herbicida (4 aplicações/ano) | Desenvolvimento | L | 320 | R$ 18,50 | R$ 5.920,00 |
| 6 | Fungicida (6 aplicações) | Desenvolvimento | L | 480 | R$ 67,00 | R$ 32.160,00 |
| 7 | Mão de Obra Colheita | Colheita | sc | 3.680 | R$ 12,00 | R$ 44.160,00 |
| 8 | Beneficiamento (secagem + descasque) | Pós-Colheita | sc | 3.680 | R$ 8,00 | R$ 29.440,00 |
| 9 | Frete para Cooperativa | Pós-Colheita | t | 220 | R$ 45,00 | R$ 9.900,00 |
| 10 | Encargos, combustível e manutenção | Geral | vb | 1 | R$ 65.000,00 | R$ 65.000,00 |

**Total Orçado: R$ 320.272,00 | Custo/ha: R$ 4.018,47 | Custo/sc: R$ 87,03**

---

### 2.2 Análise de Solo por Talhão

**O que é:** A análise de solo é o exame laboratorial que determina a composição química e física do solo de cada talhão — pH, matéria orgânica, fósforo, potássio, cálcio, magnésio, alumínio, CTC e saturação por bases. É a base científica para qualquer decisão de calagem e adubação.

**O que gera no sistema:**
- Laudo de análise associado ao talhão via `CultivoArea.analise_solo_id`
- Recomendações automáticas de calagem e adubação
- Tarefas geradas automaticamente com `origem = SOLO` e `status = PENDENTE_APROVACAO`
- Cada tarefa contém: tipo (CALAGEM, ADUBACAO_FOSFORO, etc.), dose estimada (kg/ha), quantidade total (kg), custo estimado

**Caminho:** Agrícola → Safras → [Safra] → [Cultivo] → [Talhão] → Botão "Análise de Solo"

#### Como registrar a análise (exemplo Talhão A2 — Morro):

**Passo 1:** Coletar amostras (mínimo 15 subamostras por talhão, profundidade 0–20cm e 20–40cm)

**Passo 2:** Enviar ao laboratório (Solotech Análises) — aguardar ~7 dias para resultado

**Passo 3:** No drawer de Análise de Solo, selecionar o laudo existente ou inserir os valores:

| Parâmetro | Valor Talhão A2 | Interpretação | Nível |
|-----------|-----------------|---------------|-------|
| pH (CaCl₂) | 4,8 | Muito ácido | Baixo |
| M.O. (g/dm³) | 28 | Adequado | Médio |
| P Resina (mg/dm³) | 12 | Baixo para café | Baixo |
| K (mmolc/dm³) | 1,8 | Baixo | Baixo |
| Ca (mmolc/dm³) | 14 | Baixo | Baixo |
| Mg (mmolc/dm³) | 5 | Médio | Médio |
| Al (mmolc/dm³) | 8 | Alto — tóxico | Alto |
| H+Al (mmolc/dm³) | 60 | Alto | Alto |
| CTC (mmolc/dm³) | 80,8 | Médio | Médio |
| V% (Saturação por Bases) | 25,7% | Muito baixo (café exige 60–70%) | Baixo |

**Passo 4:** Inserir recomendações do agrônomo:

| Nutriente | Recomendação | Dose/ha | Total (6,2 ha) |
|-----------|-------------|---------|----------------|
| Calagem | Calcário Dolomítico FILLER | 3,2 t/ha | 19,84 t |
| Fósforo | MAP 12-61-0 | 180 kg/ha | 1.116 kg |
| Potássio | KCl 0-0-60 | 120 kg/ha | 744 kg |
| Nitrogênio | Ureia 46% | 80 kg/ha | 496 kg |

**Passo 5 — O que o sistema faz automaticamente:**
- Cria 4 tarefas com `origem = SOLO`, `status = PENDENTE_APROVACAO`:
  - `CALAGEM` — Calcário Dolomítico FILLER — 3,2 t/ha — 19,84 t — R$ 3.571,20
  - `ADUBACAO_FOSFORO` — MAP — 180 kg/ha — 1.116 kg — R$ 4.687,20
  - `ADUBACAO_POTASSIO` — KCl — 120 kg/ha — 744 kg — R$ 2.306,40
  - `ADUBACAO_NITROGENIO` — Ureia — 80 kg/ha — 496 kg — R$ 1.388,80

**Passo 6 — Aprovação das tarefas:**
- O agrônomo/gerente revisa cada tarefa na aba "Tarefas Planejadas"
- Clica em ✓ (aprovar) ou ✗ (rejeitar) para cada uma
- Tarefas aprovadas passam para `status = APROVADA`
- Tarefas rejeitadas são marcadas como `CANCELADA` com possibilidade de nova tarefa manual

#### Análise dos 10 Talhões — Resumo de Resultado

| Talhão | pH | V% | Necessidade Calagem | Necessidade P | Necessidade K |
|--------|----|----|---------------------|---------------|---------------|
| A1 — Nascente | 5,4 | 55% | 0,8 t/ha | Baixa (80 kg) | Média (100 kg) |
| A2 — Morro | 4,8 | 26% | 3,2 t/ha | Alta (180 kg) | Alta (120 kg) |
| B1 — Baixada | 5,8 | 68% | 0,0 (não necessita) | Média (100 kg) | Média (90 kg) |
| B2 — Terreirão | 5,2 | 48% | 1,5 t/ha | Média (120 kg) | Baixa (60 kg) |
| C1 — Estrada | 5,5 | 58% | 0,6 t/ha | Baixa (70 kg) | Média (95 kg) |
| C2 — Fundo | 5,7 | 65% | 0,2 t/ha | Baixa (60 kg) | Média (85 kg) |
| D1 — Meia Encosta | 5,0 | 40% | 2,0 t/ha | Alta (160 kg) | Alta (110 kg) |
| D2 — Renovação | 5,3 | 52% | 1,0 t/ha | Alta (200 kg) | Média (100 kg) |
| E1 — Sede | 5,6 | 62% | 0,3 t/ha | Média (90 kg) | Média (88 kg) |
| E2 — Reserva | 4,9 | 32% | 2,8 t/ha | Alta (170 kg) | Alta (115 kg) |

---

## 3. FASE 2 — PREPARO DO SOLO

### O que é esta fase

O preparo do solo inclui todas as operações mecânicas e químicas realizadas antes do plantio ou da brotação dos cafeeiros. Para cafezais adultos em reforma, inclui calagem, gradagem e preparo de sulcos. Para cafezais em produção, inclui calagem superficial, roçagem e limpeza.

**Transição no sistema:** O gerente clica em "Avançar Fase" na Timeline → safra passa de `PLANEJADA` para `PREPARO_SOLO`

**O que acontece automaticamente:**
- Checklist da fase PREPARO_SOLO é criado com itens padrão para café
- Tarefas pendentes de aprovação da análise de solo ficam visíveis na aba Tarefas
- Histórico de transição de fase é registrado com data e usuário

### Como registrar Operações nesta fase

**O que é uma Operação:** Registro do que de fato foi feito em campo — a execução real de uma tarefa planejada. Uma operação pode ou não estar vinculada a uma tarefa. Quando vinculada, a tarefa é automaticamente concluída.

**Caminho:** Agrícola → Safras → [Safra] → Módulo Operações → `+ Nova Operação`

#### Operações de Preparo do Solo — 10 exemplos

| # | Data | Tipo | Talhão | Descrição | Máquina | Área (ha) | Insumo | Dose | Total | Custo |
|---|------|------|--------|-----------|---------|-----------|--------|------|-------|-------|
| 1 | 15/04/2025 | CALAGEM | A2 — Morro | Aplicação de calcário dolomítico FILLER com distribuidor, 3,2 t/ha, incorporado com grade | Trator JD 6120M + Dist. DCN 3000 | 6,20 ha | Calcário Dolomítico FILLER | 3,2 t/ha | 19,84 t | R$ 4.635,20 |
| 2 | 16/04/2025 | CALAGEM | D1 — Meia Encosta | Calagem a lanço manual (terreno acidentado), calcário dolomítico, 2,0 t/ha | Trator MF 4708 + Dist. DCN 3000 | 5,60 ha | Calcário Dolomítico FILLER | 2,0 t/ha | 11,20 t | R$ 2.617,00 |
| 3 | 17/04/2025 | CALAGEM | E2 — Reserva | Aplicação calcário 2,8 t/ha — solo raso e ácido | Trator JD 6120M + Dist. DCN 3000 | 3,80 ha | Calcário Dolomítico FILLER | 2,8 t/ha | 10,64 t | R$ 2.487,60 |
| 4 | 20/04/2025 | GRADAGEM | A2 — Morro | Gradagem aradora para incorporação do calcário, 2 passadas cruzadas | Trator JD 6120M + Grade Aradora GGTA | 6,20 ha | — | — | — | R$ 1.178,00 |
| 5 | 22/04/2025 | GRADAGEM | D1 — Meia Encosta | Grade niveladora para fechamento e nivelamento após calagem | Trator MF 4708 + Grade GNL | 5,60 ha | — | — | — | R$ 806,40 |
| 6 | 24/04/2025 | OUTRO | B1 — Baixada | Roçagem das entrelinhas com roçadeira lateral, altura 20 cm | Trator MF 4708 + Roçadeira RE 180 | 12,00 ha | — | — | — | R$ 1.080,00 |
| 7 | 25/04/2025 | OUTRO | C2 — Fundo | Roçagem das entrelinhas e corredores de acesso | Trator MF 4708 + Roçadeira RE 180 | 11,30 ha | — | — | — | R$ 1.017,00 |
| 8 | 28/04/2025 | PULVERIZACAO | B1 — Baixada | Aplicação herbicida Roundup Original pré-emergência nas linhas de plantio | Trator JD 6120M + Pulverizador AM-14 | 12,00 ha | Roundup Original DI | 2,5 L/ha | 30 L | R$ 1.110,00 |
| 9 | 29/04/2025 | PULVERIZACAO | E1 — Sede | Herbicida nas entrelinhas — controle de gramíneas perenes (tiririca) | Trator JD 6120M + Pulverizador AM-14 | 10,20 ha | Roundup Original DI | 2,5 L/ha | 25,5 L | R$ 943,75 |
| 10 | 30/04/2025 | CALAGEM | B2 — Terreirão | Calagem superficial em cobertura, sem incorporação (talhão em produção) | Trator JD 6120M + Dist. DCN 3000 | 9,80 ha | Calcário Dolomítico FILLER | 1,5 t/ha | 14,70 t | R$ 3.436,20 |

> **Importante:** Ao registrar a operação de CALAGEM no Talhão A2 e vincular à tarefa "CALAGEM — A2 Morro" (gerada pela análise de solo), o sistema automaticamente:
> - Muda status da tarefa: `APROVADA` → `CONCLUIDA`
> - Registra `operacao_id` e `concluida_em` na tarefa
> - A tarefa some da lista de pendências

### Checklist de PREPARO_SOLO para Café — Itens a marcar

| Item | Descrição | Responsável | Obrigatório |
|------|-----------|-------------|-------------|
| ☐ | Análise de solo realizada em todos os talhões | Dr. Carlos (agrônomo) | Sim |
| ☐ | Laudos recebidos e inseridos no sistema | Pedro (encarregado) | Sim |
| ☐ | Recomendações de calagem aprovadas | Gerente | Sim |
| ☐ | Calagem executada nos talhões indicados | João (tratorista) | Sim |
| ☐ | Incorporação com grade realizada (quando aplicável) | João (tratorista) | Sim |
| ☐ | Roçagem de entrelinhas concluída | João (tratorista) | Sim |
| ☐ | Herbicida pré-emergência aplicado nas linhas | João (tratorista) | Condicional |
| ☐ | Inspeção visual de pragas iniciais realizada | Dr. Carlos | Sim |
| ☐ | Equipamentos de proteção individual disponíveis | Pedro | Sim |
| ☐ | Maquinário revisado e calibrado | Mecânica Ribeiro | Sim |

---

## 4. FASE 3 — PLANTIO

### O que é esta fase

Para cafezais adultos, o "plantio" na temporada 2025/26 representa o período de **indução floral e brotação** — quando as primeiras flores aparecem após as chuvas de florada (setembro/outubro na Alta Mogiana). Para os talhões em renovação (D2), é quando ocorre o **replantio de falhas** e o estabelecimento das mudas novas.

**Transição:** `PREPARO_SOLO` → `PLANTIO` (botão Avançar Fase na Timeline)

### Operações de Plantio — 10 exemplos

| # | Data | Tipo | Talhão | Descrição | Área | Insumo | Dose/ha | Total | Custo Total |
|---|------|------|--------|-----------|------|--------|---------|-------|-------------|
| 1 | 10/05/2025 | ADUBACAO_FOSFORO | A2 — Morro | Adubação de sulco — MAP 12-61-0 conforme análise. Aplicado no sulco com aplicador tratorizado | 6,20 ha | MAP Fosfato Monoamônico | 180 kg/ha | 1.116 kg | R$ 4.687,20 |
| 2 | 11/05/2025 | ADUBACAO_FOSFORO | D1 — Meia Enc. | MAP no sulco — aplicação manual (terreno acidentado) | 5,60 ha | MAP Fosfato Monoamônico | 160 kg/ha | 896 kg | R$ 3.763,20 |
| 3 | 12/05/2025 | ADUBACAO_FOSFORO | D2 — Renovação | MAP em covas de replantio — 200 g/cova misturado com terra | 4,90 ha | MAP Fosfato Monoamônico | 200 kg/ha | 980 kg | R$ 4.116,00 |
| 4 | 14/05/2025 | ADUBACAO_POTASSIO | A2 — Morro | KCl em sulco junto ao MAP | 6,20 ha | KCl Cloreto de Potássio | 120 kg/ha | 744 kg | R$ 2.306,40 |
| 5 | 14/05/2025 | ADUBACAO_POTASSIO | D1 — Meia Enc. | KCl manual em sulco | 5,60 ha | KCl Cloreto de Potássio | 110 kg/ha | 616 kg | R$ 1.909,60 |
| 6 | 16/05/2025 | PLANTIO | D2 — Renovação | Replantio de falhas — mudas Obatã IAC 1669-20, 3,5m × 0,7m, 280 covas replantadas | 4,90 ha | — | — | 280 mudas | R$ 840,00 |
| 7 | 20/05/2025 | IRRIGACAO | D2 — Renovação | Irrigação de estabelecimento pós-plantio — gotejamento — 20 mm/semana durante 30 dias | 4,90 ha | — | — | — | R$ 490,00 |
| 8 | 22/05/2025 | ADUBACAO_NITROGENIO | D2 — Renovação | Ureia em cobertura — 1ª aplicação após pegamento das mudas | 4,90 ha | Ureia Agrícola 46% | 80 kg/ha | 392 kg | R$ 1.097,60 |
| 9 | 25/05/2025 | PULVERIZACAO | D2 — Renovação | Fungicida preventivo em mudas jovens — Folicur 200 EC, 0,5 L/ha | 4,90 ha | Folicur 200 EC | 0,5 L/ha | 2,45 L | R$ 164,15 |
| 10 | 28/05/2025 | OUTRO | Todos | Inspeção de florada — contagem de botões florais por planta em cada talhão, amostragem 50 plantas por talhão | 79,70 ha | — | — | — | R$ 200,00 |

---

## 5. FASE 4 — DESENVOLVIMENTO

### O que é esta fase

É a fase mais longa da safra de café. Vai da florada (setembro/outubro) até o início da maturação dos frutos (maio/junho do ano seguinte). Engloba: adubações parceladas de cobertura, controle de pragas e doenças, herbicidas, poda quando necessário e irrigação suplementar.

**Duração típica:** Setembro/2025 a Abril/2026 (~8 meses)

**Transição:** `PLANTIO` → `DESENVOLVIMENTO` após confirmação de florada uniforme

### O que o módulo de Monitoramento registra nesta fase

**O que é:** Inspeções regulares de campo para identificar pragas, doenças e plantas daninhas, com critério de nível de dano econômico (NDE) antes de qualquer pulverização.

**O que gera:** Histórico de incidência por talhão, alerta quando NDE é atingido, recomendação de aplicação com rastreabilidade.

**Caminho:** Agrícola → Safras → [Safra] → Módulo Monitoramento → `+ Nova Inspeção`

#### 10 Inspeções de Monitoramento

| # | Data | Talhão | Praga/Doença | Incidência | NDE | Ação |
|---|------|--------|--------------|------------|-----|------|
| 1 | 05/09/2025 | A1 — Nascente | Bicho Mineiro (Leucoptera coffeella) | 12% folhas com minas | >30% | Monitorar — abaixo do NDE |
| 2 | 10/09/2025 | B1 — Baixada | Ferrugem (Hemileia vastatrix) | 5% folíolos com pústulas | >20% | Monitorar — abaixo do NDE |
| 3 | 15/09/2025 | C2 — Fundo | Bicho Mineiro | 35% folhas com minas | >30% | APLICAR — NDE atingido → gera tarefa |
| 4 | 20/09/2025 | D1 — Enc. | Cercosporiose | 8% frutos | >15% | Monitorar |
| 5 | 01/10/2025 | A2 — Morro | Ferrugem | 22% folíolos com pústulas | >20% | APLICAR — NDE atingido → gera tarefa |
| 6 | 10/10/2025 | E1 — Sede | Nematóide (Meloidogyne) | Raízes com galhas — nível 2 | Nível >2 | APLICAR nematicida na renovação |
| 7 | 15/10/2025 | B2 — Terr. | Phoma (Ascochyta coffeae) | 3% ramos com lesões | >10% | Monitorar |
| 8 | 05/11/2025 | C1 — Estrada | Broca do Café (Hypothenemus hampei) | 2% frutos brocados | >3% | Monitorar — próximo ao NDE |
| 9 | 20/11/2025 | B1 — Baixada | Broca do Café | 4% frutos brocados | >3% | APLICAR — NDE atingido → gera tarefa |
| 10 | 10/12/2025 | Todos | Vistoria geral de colheita antecipada | 15% frutos vermelhos | — | Normal — aguardar maturação |

### Operações de Desenvolvimento — 10 exemplos

| # | Data | Tipo | Talhão | Descrição | Área | Insumo | Dose/ha | Total | Custo |
|---|------|------|--------|-----------|------|--------|---------|-------|-------|
| 1 | 05/09/2025 | ADUBACAO_NITROGENIO | Todos | 1ª cobertura nitrogenada — ureia granulada a lanço nas entrelinhas, período de chuvas | 79,70 ha | Ureia Agrícola 46% | 120 kg/ha | 9.564 kg | R$ 26.779,20 |
| 2 | 20/09/2025 | PULVERIZACAO | C2 — Fundo | Inseticida Lorsban para Bicho Mineiro — NDE atingido | 11,30 ha | Lorsban 480 BR | 1,5 L/ha | 16,95 L | R$ 762,75 |
| 3 | 01/10/2025 | PULVERIZACAO | A2 — Morro | Fungicida Folicur para Ferrugem — NDE atingido | 6,20 ha | Folicur 200 EC | 0,5 L/ha | 3,1 L | R$ 207,70 |
| 4 | 10/10/2025 | ADUBACAO_POTASSIO | Todos | 2ª cobertura — KCl a lanço, início de enchimento de grãos | 79,70 ha | KCl Cloreto de Potássio | 100 kg/ha | 7.970 kg | R$ 24.707,00 |
| 5 | 20/10/2025 | PULVERIZACAO | Todos | Foliar YaraMila complexo 20-05-20 — micronutrientes durante enchimento de grãos | 79,70 ha | YaraMila 20-05-20 | 4 kg/ha | 318,8 kg | R$ 1.721,52 |
| 6 | 05/11/2025 | ADUBACAO_NITROGENIO | Todos | 2ª cobertura nitrogenada — ureia — pré-granação | 79,70 ha | Ureia Agrícola 46% | 100 kg/ha | 7.970 kg | R$ 22.316,00 |
| 7 | 25/11/2025 | PULVERIZACAO | B1 — Baixada | Inseticida para broca — Lorsban 480 BR — NDE atingido | 12,00 ha | Lorsban 480 BR | 1,5 L/ha | 18 L | R$ 810,00 |
| 8 | 10/12/2025 | PULVERIZACAO | Todos | 3ª aplicação fungicida — proteção pré-colheita (cercosporiose + ferrugem) | 79,70 ha | Folicur 200 EC | 0,5 L/ha | 39,85 L | R$ 2.669,95 |
| 9 | 15/01/2026 | ADUBACAO_NITROGENIO | Todos | 3ª cobertura — ureia pós-granação para diferenciação floral da próxima safra | 79,70 ha | Ureia Agrícola 46% | 80 kg/ha | 6.376 kg | R$ 17.852,80 |
| 10 | 20/02/2026 | PULVERIZACAO | Todos | Herbicida para controle de invasoras antes da colheita | 79,70 ha | Roundup Original DI | 2,0 L/ha | 159,4 L | R$ 2.948,90 |

### Fenologia do Café — Estágios registrados

**O que é o módulo Fenologia:** Registro da escala BBCH ou estágio visual dos frutos por talhão. Permite saber exatamente em qual estágio de desenvolvimento a safra está, orientando decisões de quando colher.

| Mês | Estágio | Descrição | % Frutos vermelhos (meta colheita) |
|-----|---------|-----------|-------------------------------------|
| Set/2025 | Florada | Antese — flores abertas 100% | 0% |
| Out/2025 | Chumbinho | Frutos 2–3 mm, verdes intensos | 0% |
| Nov/2025 | Expansão | Frutos 8–12 mm, crescimento rápido | 0% |
| Dez/2025 | Verde | Frutos em tamanho final, verdes | 0% |
| Jan/2026 | Granação | Grãos em formação, frutos madurecendo | 5–10% |
| Fev/2026 | Pré-maturação | Início de coloração amarela/vermelha | 20–30% |
| Mar/2026 | Maturação | 60–70% frutos vermelhos | 60–70% |
| Abr/2026 | Maturação plena | >80% frutos vermelhos — INICIAR COLHEITA | >80% |

---

## 6. FASE 5 — COLHEITA

### O que é esta fase

A colheita é o momento crítico da safra. No café, pode ser realizada de três formas: **derriça manual** (pano no chão, passagem de mão), **derriça mecânica com derriçadeira** (vibração dos ramos) ou **colheita mecanizada** com colhedora automotriz (talhões planos, densamente plantados). A escolha depende do talhão.

**Transição:** `DESENVOLVIMENTO` → `COLHEITA`

**O que o sistema faz na transição:**
- Checklist de colheita é criado automaticamente
- Sistema verifica se há insumos com carência ativa (ex: Lorsban 480 — carência 21 dias) — alerta se aplicação recente
- KPIs de estimativa de produção por talhão ficam visíveis

### Romaneios de Colheita

**O que é um Romaneio:** Documento que registra o volume de café colhido por turno/dia/talhão. É o comprovante de produção — origem da rastreabilidade do lote. Cada romaneio registra: talhão, data, turma, quantidade de litros de café colhido (café da roça — ainda na casca), peso bruto.

**O que gera:** Total de café colhido por talhão; base para calcular a relação de beneficiamento (quantos litros = 1 sc de café beneficiado); custo de colheita por saca.

**Caminho:** Agrícola → Safras → [Safra] → Módulo Romaneios → `+ Novo Romaneio`

#### 10 Romaneios de Colheita

| # | Data | Talhão | Turma | Método | Litros Colhidos | Trabalhadores | Horas | Obs |
|---|------|--------|-------|--------|-----------------|---------------|-------|-----|
| 1 | 02/04/2026 | B1 — Baixada | Mecânica | Colhedora JACTO K3 Plus | 82.400 L | 3 operadores | 10 h | 1ª passagem — café maduro |
| 2 | 03/04/2026 | C2 — Fundo | Mecânica | Colhedora JACTO K3 Plus | 74.800 L | 3 operadores | 9 h | 1ª passagem — excelente maturação |
| 3 | 04/04/2026 | E1 — Sede | Mecânica | Colhedora JACTO K3 Plus | 68.200 L | 3 operadores | 8 h | 1ª passagem |
| 4 | 06/04/2026 | A1 — Nascente | Manual | Derriça no pano | 38.500 L | 18 trabalhadores | 8 h | Terreno com obstáculos |
| 5 | 07/04/2026 | A2 — Morro | Manual | Derriça no pano | 28.400 L | 15 trabalhadores | 8 h | Menor produção (solo ácido) |
| 6 | 08/04/2026 | C1 — Estrada | Semimec. | Derriçadeira costal + pano | 42.600 L | 8 trabalhadores | 8 h | Boa produção |
| 7 | 09/04/2026 | B2 — Terreirão | Semimec. | Derriçadeira costal + pano | 38.200 L | 10 trabalhadores | 8 h | Pés jovens limitaram volume |
| 8 | 10/04/2026 | D1 — Enc. | Manual | Derriça manual pano | 22.100 L | 14 trabalhadores | 8 h | Terreno acidentado — manual obrigatório |
| 9 | 11/04/2026 | D2 — Renov. | Manual | Derriça manual pano | 16.800 L | 8 trabalhadores | 6 h | 1ª safra plena — volume menor |
| 10 | 13/04/2026 | E2 — Reserva | Manual | Derriça manual pano | 11.400 L | 6 trabalhadores | 6 h | Solo raso — volume limitado |

**Total colhido (1ª passagem): 423.400 litros de café da roça**

> **Conversão típica:** 480 litros de café cereja maduro = 1 saca de 60 kg de café beneficiado
>
> **Estimativa 1ª passagem:** 423.400 ÷ 480 = **881 sacas (1ª passagem)**

### Operações de Apoio à Colheita

| # | Data | Tipo | Descrição | Custo |
|---|------|------|-----------|-------|
| 1 | 01/04/2026 | OUTRO | Regulagem e calibração da colhedora JACTO K3 antes do início | R$ 800,00 |
| 2 | 02/04/2026 | OUTRO | Transporte de café cereja do campo para terreiro/lavador | R$ 1.200,00 |
| 3 | 05/04/2026 | OUTRO | Limpeza e manutenção do terreiro de secagem — 2.400 m² | R$ 350,00 |
| 4 | 06/04/2026 | OUTRO | Contratação de turma avulsa colheita manual — diárias | R$ 4.800,00 |
| 5 | 10/04/2026 | OUTRO | Aluguel de carretas para transporte interno do café | R$ 600,00 |

---

## 7. FASE 6 — PÓS-COLHEITA (BENEFICIAMENTO)

### O que é esta fase

O beneficiamento do café é o conjunto de processos que transforma o café colhido (café da roça, ainda na casca ou na mucilagem) em café beneficiado (grão cru, pronto para torrefação). No AgroSaaS, esta fase é gerenciada pelo módulo **Beneficiamento**, específico para café, acessível na aba Módulos da safra.

**Transição:** `COLHEITA` → `POS_COLHEITA`

### Processos de Beneficiamento registrados no sistema

**Caminho:** Agrícola → Safras → [Safra] → Módulo Beneficiamento → `+ Novo Lote`

#### Via Úmida (Café Natural / Cereja Descascado / Honey)

| # | Data Entrada | Lote | Talhão Origem | Método | Litros Entrada | Dias Secagem | Tipo Secagem | Peso Final (sc 60kg) | % Rendimento |
|---|-------------|------|---------------|--------|----------------|--------------|--------------|----------------------|--------------|
| 1 | 02/04/2026 | LOT-2026-001 | B1 — Baixada | Natural (terreiro suspenso) | 82.400 L | 25 dias | Terreiro suspenso africano | 160 sc | 93% (perdas mínimas) |
| 2 | 03/04/2026 | LOT-2026-002 | C2 — Fundo | Cereja Descascado (CD) | 74.800 L | 18 dias | Terreiro suspenso + sombrite | 145 sc | 92% |
| 3 | 04/04/2026 | LOT-2026-003 | E1 — Sede | Natural (lona) | 68.200 L | 30 dias | Lona plástica + terreiro cimento | 130 sc | 91% |
| 4 | 06/04/2026 | LOT-2026-004 | A1 — Nascente | Natural (terreiro cimento) | 38.500 L | 28 dias | Terreiro de cimento | 74 sc | 92% |
| 5 | 07/04/2026 | LOT-2026-005 | A2 — Morro | Natural (terreiro cimento) | 28.400 L | 30 dias | Terreiro de cimento | 53 sc | 89% |
| 6 | 08/04/2026 | LOT-2026-006 | C1 — Estrada | Honey (Yellow Honey) | 42.600 L | 22 dias | Terreiro suspenso | 83 sc | 93% |
| 7 | 09/04/2026 | LOT-2026-007 | B2 — Terreirão | Natural (lona) | 38.200 L | 28 dias | Lona plástica | 73 sc | 91% |
| 8 | 10/04/2026 | LOT-2026-008 | D1 — Enc. | Natural (terreiro cimento) | 22.100 L | 30 dias | Terreiro de cimento | 41 sc | 89% |
| 9 | 11/04/2026 | LOT-2026-009 | D2 — Renov. | Natural (lona) | 16.800 L | 25 dias | Lona plástica | 31 sc | 88% |
| 10 | 13/04/2026 | LOT-2026-010 | E2 — Reserva | Natural (terreiro cimento) | 11.400 L | 30 dias | Terreiro de cimento | 21 sc | 88% |

**Total beneficiado 1ª passagem: 811 sacas de café cru beneficiado**

> **Nota:** A relação 480 L = 1 sc é teórica. Na prática, lotes com alto percentual de frutos verdes ou passas têm rendimento menor. Por isso o sistema registra entrada em litros e saída em sacas, calculando o rendimento real de cada lote.

#### Classificação do Café (Tipo e Peneira)

**O que é:** Após a secagem, o café passa pela classificação por tipo (número de defeitos por amostra de 300 g) e peneira (tamanho do grão). Isso determina o preço de venda.

| Lote | Tipo (ABIC) | Peneira | Bebida (prova de xícara) | Pontuação SCA | Classificação Comercial |
|------|-------------|---------|--------------------------|---------------|------------------------|
| LOT-001 | Tipo 2 | Peneira 17/18 | Mole a Apenas Mole | 84 pontos | Especial — exportação |
| LOT-002 | Tipo 3 | Peneira 16/17 | Apenas Mole | 82 pontos | Superior |
| LOT-003 | Tipo 2/3 | Peneira 17 | Mole | 83 pontos | Superior |
| LOT-004 | Tipo 3 | Peneira 16 | Apenas Mole | 81 pontos | Superior |
| LOT-005 | Tipo 4 | Peneira 15/16 | Dura | 77 pontos | Comercial |
| LOT-006 | Tipo 2 | Peneira 17/18 | Mole | 85 pontos | Especial — exportação |
| LOT-007 | Tipo 3/4 | Peneira 16 | Apenas Mole | 80 pontos | Superior |
| LOT-008 | Tipo 4 | Peneira 15 | Dura | 76 pontos | Comercial |
| LOT-009 | Tipo 4 | Peneira 15 | Dura | 75 pontos | Comercial |
| LOT-010 | Tipo 5 | Peneira 14/15 | Dura | 73 pontos | Comercial baixo |

---

## 8. FASE 7 — ENCERRAMENTO

### O que é esta fase

O encerramento é a última fase da safra. Representa a finalização de todas as atividades, o fechamento financeiro e a consolidação dos dados para análise de resultado. A safra só deve ser encerrada quando: toda a produção foi vendida ou armazenada, todos os custos foram lançados e o resultado final foi calculado.

**Transição:** `POS_COLHEITA` → `ENCERRADA`

> Uma vez encerrada, a safra fica bloqueada para novos lançamentos. Ela serve de referência histórica comparativa para as próximas safras.

### Fechamento Financeiro — O que o sistema calcula

**Caminho:** Agrícola → Safras → [Safra] → Módulo Financeiro → Relatório de Resultado

#### Receitas por Lote

| Lote | Quantidade | Classificação | Preço/sc | Comprador | Total Receita |
|------|------------|---------------|----------|-----------|---------------|
| LOT-001 | 160 sc | Especial 84 pts | R$ 1.200,00 | Cooperativa Café Mogiana | R$ 192.000,00 |
| LOT-002 | 145 sc | Superior | R$ 980,00 | Cooperativa Café Mogiana | R$ 142.100,00 |
| LOT-003 | 130 sc | Superior | R$ 960,00 | Cooperativa Café Mogiana | R$ 124.800,00 |
| LOT-004 | 74 sc | Superior | R$ 960,00 | Cooperativa Café Mogiana | R$ 71.040,00 |
| LOT-005 | 53 sc | Comercial | R$ 800,00 | Cooperativa Café Mogiana | R$ 42.400,00 |
| LOT-006 | 83 sc | Especial 85 pts | R$ 1.250,00 | Exportador direto | R$ 103.750,00 |
| LOT-007 | 73 sc | Superior | R$ 950,00 | Cooperativa Café Mogiana | R$ 69.350,00 |
| LOT-008 | 41 sc | Comercial | R$ 790,00 | Cooperativa Café Mogiana | R$ 32.390,00 |
| LOT-009 | 31 sc | Comercial | R$ 780,00 | Cooperativa Café Mogiana | R$ 24.180,00 |
| LOT-010 | 21 sc | Comercial baixo | R$ 700,00 | Cooperativa Café Mogiana | R$ 14.700,00 |

**Total Receita Bruta: R$ 816.710,00**

#### KPIs de Resultado Final

| Indicador | Valor | Meta | Resultado |
|-----------|-------|------|-----------|
| Produção total | 811 sc | 3.680 sc (incluindo 2ª passagem) | Parcial — 1ª passagem |
| Área colhida | 79,70 ha | 79,70 ha | ✅ 100% |
| Produtividade média | 10,2 sc/ha (1ª passagem) | 46 sc/ha (total) | Aguarda 2ª passagem |
| Custo total realizado | R$ 287.430,00 | R$ 320.272,00 | ✅ 10,2% abaixo do orçado |
| Custo por saca (1ª passagem) | R$ 354,42/sc | R$ 87,03/sc (total estimado) | Proporcional 1ª passagem |
| Receita bruta (1ª passagem) | R$ 816.710,00 | — | — |
| Margem bruta | R$ 529.280,00 | — | R$ 6.641/ha |
| Custo/ha realizado | R$ 3.606/ha | R$ 4.018/ha | ✅ Abaixo do orçado |

### Checklist Final de Encerramento

| Item | Responsável | Status |
|------|-------------|--------|
| ☐ Toda produção vendida ou armazenada e registrada | Gerente | Pendente |
| ☐ Todos os lotes com classificação e nota SCA registrada | Dr. Carlos | Pendente |
| ☐ Todos os romaneios conferidos e assinados | Pedro | Pendente |
| ☐ Todos os custos de colheita lançados como operações | Financeiro | Pendente |
| ☐ Notas fiscais de venda emitidas e lançadas no financeiro | Financeiro | Pendente |
| ☐ Folha de pagamento da turma de colheita fechada | RH/Admin | Pendente |
| ☐ Relatório de resultado da safra gerado e arquivado | Gerente | Pendente |
| ☐ Comparativo orçado vs. realizado revisado | Gerente | Pendente |
| ☐ Banco de dados de análise de solo atualizado para próxima safra | Dr. Carlos | Pendente |
| ☐ Safra encerrada no sistema (status ENCERRADA — irreversível) | Gerente | Pendente |

---

## 9. CHECKLIST FINAL DE VALIDAÇÃO DO SISTEMA

Use esta lista para confirmar que cada funcionalidade foi testada e está funcionando:

### Cadastros Mestre

| # | Item | Testado | OK | Obs |
|---|------|---------|----|----|
| 1 | Criação de 10 talhões com área e características | ☐ | ☐ | |
| 2 | Cadastro de 10 pessoas (físicas e jurídicas) | ☐ | ☐ | |
| 3 | Cadastro de 10 insumos com preço e carência | ☐ | ☐ | |
| 4 | Cadastro de máquinas e equipamentos | ☐ | ☐ | |
| 5 | Cadastro de cultivares com características | ☐ | ☐ | |

### Criação da Safra

| # | Item | Testado | OK | Obs |
|---|------|---------|----|----|
| 6 | Criar safra 2025/2026 com cultivo Catuaí Vermelho | ☐ | ☐ | |
| 7 | Vincular cultivo a 10 talhões (CultivoArea) | ☐ | ☐ | |
| 8 | Inserir orçamento com 10 itens | ☐ | ☐ | |
| 9 | Safra criada com status PLANEJADA | ☐ | ☐ | |

### Análise de Solo → Tarefas

| # | Item | Testado | OK | Obs |
|---|------|---------|----|----|
| 10 | Inserir análise de solo em cada talhão (10 análises) | ☐ | ☐ | |
| 11 | Sistema gera tarefas automáticas (PENDENTE_APROVACAO) | ☐ | ☐ | |
| 12 | Tarefas aparecem na aba "Tarefas Planejadas" da safra | ☐ | ☐ | |
| 13 | Aprovar tarefas individualmente (botão ✓) | ☐ | ☐ | |
| 14 | Rejeitar tarefas individualmente (botão ✗) | ☐ | ☐ | |
| 15 | Tarefa aprovada muda para APROVADA | ☐ | ☐ | |

### Transições de Fase

| # | Item | Testado | OK | Obs |
|---|------|---------|----|----|
| 16 | Avançar de PLANEJADA → PREPARO_SOLO | ☐ | ☐ | |
| 17 | Avançar de PREPARO_SOLO → PLANTIO | ☐ | ☐ | |
| 18 | Avançar de PLANTIO → DESENVOLVIMENTO | ☐ | ☐ | |
| 19 | Avançar de DESENVOLVIMENTO → COLHEITA | ☐ | ☐ | |
| 20 | Avançar de COLHEITA → POS_COLHEITA | ☐ | ☐ | |
| 21 | Avançar de POS_COLHEITA → ENCERRADA | ☐ | ☐ | |
| 22 | Histórico de fases registrado com data/hora | ☐ | ☐ | |
| 23 | Checklist muda automaticamente a cada fase | ☐ | ☐ | |

### Operações Agrícolas

| # | Item | Testado | OK | Obs |
|---|------|---------|----|----|
| 24 | Criar operação de CALAGEM vinculada a tarefa | ☐ | ☐ | |
| 25 | Tarefa é concluída automaticamente ao criar operação | ☐ | ☐ | |
| 26 | Criar operação sem tarefa vinculada (operação avulsa) | ☐ | ☐ | |
| 27 | Custo calculado automaticamente (dose × área × preço) | ☐ | ☐ | |
| 28 | Máquina vinculada a operação registrada corretamente | ☐ | ☐ | |
| 29 | Operador vinculado a operação registrado corretamente | ☐ | ☐ | |

### Romaneios de Colheita

| # | Item | Testado | OK | Obs |
|---|------|---------|----|----|
| 30 | Criar 10 romaneios de colheita (1 por talhão) | ☐ | ☐ | |
| 31 | Total de litros consolidado por talhão | ☐ | ☐ | |
| 32 | Conversão litros → sacas calculada pelo sistema | ☐ | ☐ | |

### Beneficiamento

| # | Item | Testado | OK | Obs |
|---|------|---------|----|----|
| 33 | Criar 10 lotes de beneficiamento | ☐ | ☐ | |
| 34 | Vincular lote ao talhão/romaneio de origem | ☐ | ☐ | |
| 35 | Registrar método de processamento por lote | ☐ | ☐ | |
| 36 | Registrar rendimento (litros entrada × sc saída) | ☐ | ☐ | |

### Financeiro

| # | Item | Testado | OK | Obs |
|---|------|---------|----|----|
| 37 | Custos das operações aparecem no financeiro | ☐ | ☐ | |
| 38 | Receitas de venda registradas por lote | ☐ | ☐ | |
| 39 | Comparativo orçado vs. realizado disponível | ☐ | ☐ | |
| 40 | KPIs finais (custo/ha, custo/sc, margem) calculados | ☐ | ☐ | |

---

## GLOSSÁRIO

| Termo | Significado |
|-------|-------------|
| **sc** | Saca de café = 60 kg de café beneficiado |
| **Café da roça** | Café cereja recém-colhido, ainda na casca, medido em litros |
| **Café beneficiado** | Grão cru após secagem, descascamento e classificação, medido em sacas |
| **NDE** | Nível de Dano Econômico — ponto de incidência de praga/doença que justifica aplicação de defensivo |
| **CTC** | Capacidade de Troca Catiônica — medida da fertilidade potencial do solo |
| **V%** | Saturação por Bases — percentual da CTC ocupado por bases (Ca, Mg, K) — café exige 60–70% |
| **Calagem** | Aplicação de calcário para elevar o pH e V% do solo |
| **BBCH** | Escala fenológica internacional para estágios de desenvolvimento de plantas |
| **Peneira** | Classificação do grão por tamanho (peneira 17 = 17/64 de polegada de diâmetro) |
| **SCA** | Specialty Coffee Association — escala de 0–100 pontos para avaliação de qualidade de xícara |
| **Natural** | Método de processamento onde o café seca com a casca e polpa intactas |
| **CD** | Cereja Descascado — café processado com remoção da casca antes da secagem |
| **Honey** | Método em que a casca é removida mas a mucilagem é mantida parcialmente |

---

*Documento criado em: 21/04/2026*
*Propriedade: Fazenda Boa Esperança — Alta Mogiana (SP)*
*Sistema: AgroSaaS — Módulo Agrícola*
*Responsável técnico: Dr. Carlos Eduardo Motta — CREA-SP 1.234.567*
