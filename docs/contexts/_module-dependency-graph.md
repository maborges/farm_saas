---
titulo: Mapa de Dependências entre Módulos
versao: 1.1
data_criacao: 2026-04-01
data_atualizacao: 2026-04-01
base_analise:
  - _competitive-analysis.md
  - ../strategy/bundle-packages.md
  - ../functional_requirements/funtionals.md
---

# Mapa de Dependências entre Módulos

## Visão Geral

Este documento mapeia todas as dependências entre módulos e submódulos do AgroSaaS, definindo a **ordem obrigatória de implantação** e os **pontos de integração** entre sistemas.

---

## REGRAS DE DEPENDÊNCIA

### Regra 1: Core é Pré-Requisito Universal

```
┌─────────────────────────────────────────────────┐
│              MÓDULO CORE                        │
│  (obrigatório para TODOS os outros módulos)    │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   [Agrícola]   [Pecuária]   [Financeiro]   ...
```

**Todos os módulos dependem de:**
- `core/identidade-acesso` — Autenticação e RBAC
- `core/cadastro-propriedade` — Fazendas e áreas
- `core/multipropriedade` — Isolamento de tenant
- `core/planos-assinatura` — Feature flags

---

### Regra 2: Essencial → Profissional → Enterprise

**Nunca implante na ordem inversa.**

```
Essencial ──► Profissional ──► Enterprise
   │              │                │
   ▼              ▼                ▼
 Base         Intermediário     Avançado
```

**Exemplo (Módulo Financeiro):**
```
lancamentos-basicos (Essencial)
         │
         ▼
contas-pagar-receber (Profissional)
         │
         ▼
conciliacao-automatica (Enterprise)
```

---

### Regra 3: Dependências Cruzadas entre Módulos

Alguns submódulos dependem de módulos **diferentes** do Core.

**Exemplo:**
- `financeiro/custo-producao-safra` depende de `agricola/safras`
- `pecuaria/nutricao` depende de `estoque/produtos`
- `comercializacao/nfe-emissao` depende de `financeiro/lancamentos`

---

## GRAFO DE DEPENDÊNCIAS — VISÃO MACRO

```
                              ┌──────────────┐
                              │     CORE     │
                              │  (obrigatório)│
                              └──────┬───────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
   ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
   │   AGRÍCOLA  │           │   PECUÁRIA  │           │  FINANCEIRO │
   │             │           │             │           │             │
   │ Essencial   │           │ Essencial   │           │ Essencial   │
   │ Profissional│           │ Profissional│           │ Profissional│
   │ Enterprise  │           │ Enterprise  │           │ Enterprise  │
   └──────┬──────┘           └──────┬──────┘           └──────┬──────┘
          │                         │                          │
          │                         │                          │
          └────────────┬────────────┘                          │
                       │                                       │
                       ▼                                       ▼
               ┌───────────────┐                       ┌───────────────┐
               │ESTOQUE/OPERAC.│                       │CONTABILIDADE  │
               │               │                       │               │
               │Depende de:    │                       │Depende de:    │
               │- Agrícola     │                       │- Financeiro   │
               │- Pecuária     │                       │- Todos        │
               └───────┬───────┘                       └───────┬───────┘
                       │                                       │
                       │                                       │
                       └───────────────────┬───────────────────┘
                                           │
                                           ▼
                                   ┌───────────────┐
                                   │COMERCIALIZAÇÃO│
                                   │               │
                                   │Depende de:    │
                                   │- Agrícola     │
                                   │- Pecuária     │
                                   │- Financeiro   │
                                   │- Estoque      │
                                   └───────────────┘
```

---

## DEPENDÊNCIAS DETALHADAS POR MÓDULO

---

## 1. CORE (Fundação)

### Submódulos

| Submódulo | Dependências Internas | Dependências Externas |
|-----------|----------------------|----------------------|
| `identidade-acesso` | Nenhuma | — |
| `cadastro-propriedade` | `identidade-acesso` | — |
| `multipropriedade` | `identidade-acesso`, `cadastro-propriedade` | — |
| `configuracoes-globais` | `identidade-acesso` | — |
| `notificacoes-alertas` | `identidade-acesso` | SMTP, Firebase, Twilio |
| `integracoes-essenciais` | `identidade-acesso` | — |
| `planos-assinatura` | `identidade-acesso` | Stripe, Asaas |

### Ordem de Implantação

```
1. identidade-acesso
2. cadastro-propriedade
3. configuracoes-globais
4. multipropriedade
5. notificacoes-alertas
6. integracoes-essenciais
7. planos-assinatura
```

---

## 2. AGRÍCOLA

### Dependências do Core

- ✅ `core/identidade-acesso` — Obrigatório
- ✅ `core/cadastro-propriedade` — Obrigatório (fazendas, talhões)
- ✅ `core/configuracoes-globais` — Obrigatório (safra, unidades)
- ✅ `core/planos-assinatura` — Feature flags (A1_PLANEJAMENTO, etc.)

### Dependências Internas (Agrícola)

```
safras (Essencial)
   │
   ├──────────────────┐
   │                  │
   ▼                  ▼
operacoes-campo   caderno-campo (Essencial)
   │                  │
   │                  │
   └────────┬─────────┘
            │
            ▼
      planejamento-safra (Profissional)
            │
            ├─────────────────┐
            │                 │
            ▼                 ▼
       monitoramento-ndvi  custos-producao (Profissional)
            │                 │
            │                 │
            └────────┬────────┘
                     │
                     ▼
            rastreabilidade-campo (Enterprise)
                     │
                     ├──────────────────┐
                     │                  │
                     ▼                  ▼
            prescricoes-vrt    beneficiamento (Enterprise)
```

### Dependências de Outros Módulos

| Submódulo Agrícola | Depende de | Tipo |
|-------------------|------------|------|
| `custos-producao` | `financeiro/lancamentos-basicos` | Soft link (se não contratado: valor manual) |
| `custos-producao` | `estoque/movimentacoes` | Soft link (se não contratado: valor manual) |
| `romaneios-colheita` | `comercializacao/registro-vendas` | Hard link (se contratado: integra automaticamente) |
| `beneficiamento` | `estoque/produtos` | Hard link |
| `prescricoes-vrt` | `operacional/frota` | Soft link (maquinário) |

---

## 3. PECUÁRIA

### Dependências do Core

- ✅ `core/identidade-acesso` — Obrigatório
- ✅ `core/cadastro-propriedade` — Obrigatório (fazendas, piquetes)
- ✅ `core/configuracoes-globais` — Obrigatório (unidades, safra)
- ✅ `core/planos-assinatura` — Feature flags (P1_RASTREIO, etc.)

### Dependências Internas (Pecuária)

```
rastreio-basico (Essencial)
   │
   ├──────────────────┐
   │                  │
   ▼                  ▼
controle-sanitario  piquetes-pastos (Essencial)
   │                  │
   │                  │
   └────────┬─────────┘
            │
            ▼
      genetica-reprodutiva (Profissional)
            │
            ├─────────────────┐
            │                 │
            ▼                 ▼
       nutricao-feedlot  pecuaria-leiteira (Profissional)
            │                 │
            │                 │
            └────────┬────────┘
                     │
                     ▼
            rastreabilidade-sisbov (Enterprise)
                     │
                     ├──────────────────┐
                     │                  │
                     ▼                  ▼
              gta-digital    genealogia-deps (Enterprise)
```

### Dependências de Outros Módulos

| Submódulo Pecuária | Depende de | Tipo |
|-------------------|------------|------|
| `nutricao-feedlot` | `estoque/produtos` | Hard link (ração, insumos) |
| `nutricao-feedlot` | `agricola/safras` | Soft link (produção própria de grãos) |
| `controle-sanitario` | `estoque/medicamentos` | Hard link (vacinas) |
| `rastreabilidade-sisbov` | `comercializacao/registro-vendas` | Hard link (venda de animais) |
| `pecuaria-leiteira` | `comercializacao/registro-vendas` | Hard link (venda de leite) |

---

## 4. FINANCEIRO

### Dependências do Core

- ✅ `core/identidade-acesso` — Obrigatório
- ✅ `core/cadastro-propriedade` — Obrigatório (centro de custo por fazenda)
- ✅ `core/planos-assinatura` — Feature flags (F1_TESOURARIA, etc.)

### Dependências Internas (Financeiro)

```
lancamentos-basicos (Essencial)
   │
   ├──────────────────┐
   │                  │
   ▼                  ▼
fluxo-caixa      categorias-contas (Essencial)
   │
   │
   ▼
contas-pagar-receber (Profissional)
   │
   ├──────────────────┐
   │                  │
   ▼                  ▼
centro-custo    conciliacao-bancaria (Profissional)
   │
   │
   ▼
conciliacao-automatica (Enterprise)
   │
   ├──────────────────┐
   │                  │
   ▼                  ▼
credito-rural    custo-producao-safra (Enterprise)
```

### Dependências de Outros Módulos

| Submódulo Financeiro | Depende de | Tipo |
|---------------------|------------|------|
| `centro-custo` | `agricola/safras` | Hard link (rateio por safra/talhão) |
| `centro-custo` | `pecuaria/lotes` | Hard link (rateio por lote) |
| `centro-custo` | `operacional/frota` | Hard link (rateio por máquina) |
| `custo-producao-safra` | `agricola/custos-producao` | Hard link |
| `custo-producao-safra` | `pecuaria/nutricao` | Hard link (custo de alimentação) |
| `credito-rural` | `agricola/planejamento-safra` | Soft link (projeto de crédito) |
| `lancamentos-basicos` | `estoque/movimentacoes` | Hard link (baixa automática) |
| `lancamentos-basicos` | `operacional/abastecimento` | Hard link (custo de combustível) |

---

## 5. ESTOQUE / OPERACIONAL

### Dependências do Core

- ✅ `core/identidade-acesso` — Obrigatório
- ✅ `core/cadastro-propriedade` — Obrigatório (almoxarifados por fazenda)
- ✅ `core/planos-assinatura` — Feature flags (O1_ESTOQUE, etc.)

### Dependências Internas (Estoque)

```
cadastro-produtos (Essencial)
   │
   │
   ▼
movimentacoes (Essencial)
   │
   ├──────────────────┐
   │                  │
   ▼                  ▼
consulta-saldo    almoxarifados (Essencial)
   │
   │
   ▼
fifo-custo-medio (Profissional)
   │
   ├──────────────────┐
   │                  │
   ▼                  ▼
estoque-minimo   rastreabilidade-lotes (Profissional)
   │
   │
   ▼
compras-integradas (Enterprise)
   │
   ├──────────────────┐
   │                  │
   ▼                  ▼
inventario-auto   integracao-fiscal (Enterprise)
```

### Dependências de Outros Módulos

| Submódulo Estoque | Depende de | Tipo |
|------------------|------------|------|
| `movimentacoes` | `agricola/operacoes-campo` | Hard link (baixa de insumos) |
| `movimentacoes` | `pecuaria/manejo-sanitario` | Hard link (baixa de vacinas) |
| `movimentacoes` | `operacional/abastecimento` | Hard link (baixa de combustível) |
| `compras-integradas` | `financeiro/contas-pagar` | Hard link |
| `integracao-fiscal` | `financeiro/lancamentos` | Hard link |
| `integracao-fiscal` | `comercializacao/nfe-emissao` | Hard link |

---

## 6. FROTA / MÁQUINAS

### Dependências do Core

- ✅ `core/identidade-acesso` — Obrigatório
- ✅ `core/cadastro-propriedade` — Obrigatório

### Dependências Internas (Frota)

```
cadastro-equipamentos (Essencial)
   │
   ├──────────────────┐
   │                  │
   ▼                  ▼
abastecimento    checklist-diario (Essencial)
   │
   │
   ▼
manutencao-preventiva (Profissional)
   │
   ├──────────────────┐
   │                  │
   ▼                  ▼
custo-hora-maquina  documentacao (Profissional)
   │
   │
   ▼
telemetria (Enterprise)
   │
   ├──────────────────┐
   │                  │
   ▼                  ▼
oficina-interna   indicadores-frota (Enterprise)
```

### Dependências de Outros Módulos

| Submódulo Frota | Depende de | Tipo |
|-----------------|------------|------|
| `abastecimento` | `estoque/combustivel` | Hard link |
| `manutencao-preventiva` | `estoque/pecas` | Hard link |
| `custo-hora-maquina` | `financeiro/lancamentos` | Hard link |
| `custo-hora-maquina` | `agricola/operacoes-campo` | Hard link (alocação por operação) |
| `telemetria` | `agricola/operacoes-campo` | Hard link (horas trabalhadas) |

---

## 7. RASTREABILIDADE

### Dependências do Core

- ✅ `core/identidade-acesso` — Obrigatório
- ✅ `core/planos-assinatura` — Feature flags

### Dependências de Outros Módulos

| Submódulo Rastreabilidade | Depende de | Tipo |
|--------------------------|------------|------|
| `lotes-producao` | `agricola/safras` | Hard link |
| `lotes-producao` | `pecuaria/lotes` | Hard link |
| `origem-destino` | `comercializacao/registro-vendas` | Hard link |
| `historico-aplicacoes` | `agricola/caderno-campo` | Hard link |
| `historico-aplicacoes` | `pecuaria/manejo-sanitario` | Hard link |
| `cadeia-custodia` | `estoque/movimentacoes` | Hard link |
| `qrcode-consulta` | `lotes-producao` | Hard link |
| `laudos-analises` | `agricola/analises-solo` | Soft link |
| `certificacoes` | `compliance/car-gestao` | Hard link |
| `blockchain` | `lotes-producao` | Hard link |
| `blockchain` | `origem-destino` | Hard link |
| `auditoria-exportacao` | `compliance/due-diligence` | Hard link |

---

## 8. COMERCIALIZAÇÃO

### Dependências do Core

- ✅ `core/identidade-acesso` — Obrigatório
- ✅ `core/planos-assinatura` — Feature flags

### Dependências de Outros Módulos

| Submódulo Comercialização | Depende de | Tipo |
|--------------------------|------------|------|
| `registro-vendas` | `agricola/safras` | Hard link (origem) |
| `registro-vendas` | `pecuaria/lotes` | Hard link (origem) |
| `clientes-compradores` | Nenhuma | — |
| `romaneios` | `agricola/romaneios-colheita` | Hard link |
| `contratos-venda` | `registro-vendas` | Hard link |
| `cotacoes-mercado` | Nenhuma (API externa) | CBOT, ESALQ, B3 |
| `nfe-emissao` | `financeiro/lancamentos` | Hard link |
| `nfe-emissao` | `estoque/movimentacoes` | Hard link |
| `cpr-cedulas` | `contratos-venda` | Hard link |
| `hedge-derivativos` | `cotacoes-mercado` | Hard link |
| `hedge-derivativos` | `contratos-venda` | Hard link |
| `exportacao` | `rastreabilidade/blockchain` | Hard link |
| `exportacao` | `compliance/due-diligence` | Hard link |

---

## 9. COMPLIANCE AMBIENTAL

### Dependências do Core

- ✅ `core/identidade-acesso` — Obrigatório
- ✅ `core/cadastro-propriedade` — Obrigatório (geolocalização, shapefiles)
- ✅ `core/planos-assinatura` — Feature flags

### Dependências de Outros Módulos

| Submódulo Compliance | Depende de | Tipo |
|---------------------|------------|------|
| `car-gestao` | `core/cadastro-propriedade` | Hard link |
| `app-reserva-legal` | `core/cadastro-propriedade` | Hard link (shapefiles) |
| `documentos-ambientais` | Nenhuma | — |
| `monitoramento-desmatamento` | `core/cadastro-propriedade` | Hard link (geolocalização) |
| `monitoramento-desmatamento` | APIs externas (INPE, NASA) | PRODES, DETER |
| `gestao-residuos` | `estoque/embalagens` | Hard link |
| `relatorios-esg` | `agricola/operacoes` | Hard link |
| `relatorios-esg` | `pecuaria/manejo` | Hard link |
| `relatorios-esg` | `operacional/combustivel` | Hard link |
| `carbono` | `relatorios-esg` | Hard link |
| `carbono` | `pecuaria/rebanho` | Hard link (emissões) |
| `due-diligence` | `rastreabilidade/blockchain` | Hard link |
| `due-diligence` | `compliance/car-gestao` | Hard link |
| `biodiversidade` | `core/cadastro-propriedade` | Hard link (áreas preservadas) |

---

## 10. CONTABILIDADE

### Dependências do Core

- ✅ `core/identidade-acesso` — Obrigatório
- ✅ `core/configuracoes-globais` — Obrigatório (plano de contas padrão)
- ✅ `core/planos-assinatura` — Feature flags

### Dependências de Outros Módulos

| Submódulo Contabilidade | Depende de | Tipo |
|------------------------|------------|------|
| `lcdpr` | `financeiro/lancamentos-basicos` | Hard link |
| `plano-contas-rural` | Nenhuma | — |
| `lancamentos-contabeis` | `financeiro/lancamentos-basicos` | Hard link |
| `integracao-contabil` | `lancamentos-contabeis` | Hard link |
| `integracao-contabil` | `financeiro/dre` | Hard link |
| `dre-rural` | `financeiro/centro-custo` | Hard link |
| `dre-rural` | `agricola/custos-producao` | Hard link |
| `balancete` | `lancamentos-contabeis` | Hard link |
| `multi-empresa` | `core/multipropriedade` | Hard link |
| `multi-empresa` | `dre-rural` | Hard link |
| `irpf-rural` | `dre-rural` | Hard link |
| `irpf-rural` | `lancamentos-contabeis` | Hard link |
| `sped-fiscal` | `lancamentos-contabeis` | Hard link |
| `sped-fiscal` | `comercializacao/nfe-emissao` | Hard link |

---

## ORDEM DE IMPLANTAÇÃO RECOMENDADA

### Fase 1: Core (Semanas 1-4)

```
Semana 1-2: identidade-acesso, cadastro-propriedade
Semana 3:   configuracoes-globais, multipropriedade
Semana 4:   notificacoes-alertas, integracoes-essenciais, planos-assinatura
```

### Fase 2: Módulos Essenciais (Semanas 5-10)

```
Semana 5-6:  Agrícola Essencial (safras, operacoes-campo, caderno-campo)
Semana 7:    Pecuária Essencial (rastreio-basico, controle-sanitario, piquetes)
Semana 8:    Financeiro Essencial (lancamentos-basicos, fluxo-caixa)
Semana 9:    Estoque Essencial (cadastro-produtos, movimentacoes)
Semana 10:   Frota Essencial (cadastro-equipamentos, abastecimento)
```

### Fase 3: Módulos Profissionais (Semanas 11-18)

```
Semana 11-12: Agrícola Profissional (planejamento, ndvi, custos)
Semana 13:    Pecuária Profissional (genetica, nutricao)
Semana 14:    Financeiro Profissional (contas-pagar-receber, centro-custo)
Semana 15:    Estoque Profissional (fifo, estoque-minimo)
Semana 16:    Frota Profissional (manutencao-preventiva, custo-hora)
Semana 17:    Compliance Profissional (monitoramento, residuos)
Semana 18:    Comercialização Profissional (contratos, cotacoes, nfe)
```

### Fase 4: Módulos Enterprise (Semanas 19-28)

```
Semana 19-20: Agrícola Enterprise (rastreabilidade, prescricoes-vrt, beneficiamento)
Semana 21:    Pecuária Enterprise (sisbov, gta, genealogia)
Semana 22-23: Financeiro Enterprise (conciliacao-automatica, credito-rural, custo-producao)
Semana 24:    Estoque Enterprise (compras-integradas, integracao-fiscal)
Semana 25:    Frota Enterprise (telemetria, oficina-interna)
Semana 26:    Rastreabilidade Enterprise (blockchain, certificacoes, auditoria)
Semana 27:    Compliance Enterprise (carbono, due-diligence)
Semana 28:    Contabilidade Enterprise (multi-empresa, sped-fiscal)
```

---

## MATRIZ DE DEPENDÊNCIAS CRUZADAS

| Módulo | Depende De | Para Quê |
|--------|-----------|----------|
| `financeiro/centro-custo` | `agricola/safras` | Rateio de custos por safra/talhão |
| `financeiro/centro-custo` | `pecuaria/lotes` | Rateio de custos por lote animal |
| `agricola/custos-producao` | `financeiro/lancamentos` | Dados financeiros reais |
| `agricola/custos-producao` | `estoque/movimentacoes` | Baixa de insumos |
| `pecuaria/nutricao` | `estoque/produtos` | Ração e suplementos |
| `pecuaria/nutricao` | `agricola/safras` | Produção própria de grãos |
| `comercializacao/nfe-emissao` | `financeiro/lancamentos` | Registro de receita |
| `comercializacao/nfe-emissao` | `estoque/movimentacoes` | Baixa de estoque |
| `compliance/carbono` | `pecuaria/rebanho` | Emissões de metano |
| `compliance/carbono` | `operacional/combustivel` | Emissões de CO₂ |
| `rastreabilidade/blockchain` | `agricola/safras` | Origem do produto |
| `rastreabilidade/blockchain` | `comercializacao/vendas` | Destino do produto |

---

## PONTOS DE SINCRONIZAÇÃO ENTRE AGENTES

### Agente Core ↔ Todos os Agentes

**Sincronização:** Diária durante Fase 1  
**Arquivos:** `core/*.md`, `core/dependencies.py`, `core/constants.py`

### Agente Agrícola ↔ Agente Financeiro

**Ponto de sincronização:** `financeiro/centro-custo` e `agricola/custos-producao`  
**Quando:** Semana 12 (início do Profissional)  
**Conflito potencial:** Rateio de custos por safra/talhão

### Agente Pecuária ↔ Agente Estoque

**Ponto de sincronização:** `pecuaria/nutricao` e `estoque/produtos`  
**Quando:** Semana 13  
**Conflito potencial:** Baixa automática de ração/medicamentos

### Agente Comercialização ↔ Agente Fiscal

**Ponto de sincronização:** `comercializacao/nfe-emissao` e `compliance/sped`  
**Quando:** Semana 28  
**Conflito potencial:** Layout de arquivos fiscais

---

## PROTOCOLO DE CONFLITO

Quando dois agentes tocam na mesma entidade:

1. **Identificar o conflito** — Ex: `centro-custo` (Financeiro) e `custos-producao` (Agrícola)
2. **Definir dono primário** — Ex: `centro-custo` é dono do Financeiro
3. **Criar interface clara** — Ex: Agrícola **consome** dados do Financeiro via API
4. **Documentar no arquivo** — Adicionar no frontmatter: `dependencias_modulos: ["../financeiro/centro-custo.md"]`
5. **Sincronizar antes de merge** — Ambos agentes revisam o PR

---

**Documento gerado em:** 2026-04-01  
**Próxima revisão:** Após conclusão da Fase 1 (Core)  
**Responsável:** Architecture Team AgroSaaS
