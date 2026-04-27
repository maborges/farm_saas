# Contexto Técnico — Sistema SaaS de Gestão de Safras (Agro)

## 🎯 Objetivo
Evoluir o núcleo operacional da safra para suportar:

- Centro de custo agrícola real
- Execução operacional granular
- Ledger financeiro e de estoque
- Consórcios (multi-cultura na mesma área)
- Análise econômica por unidade produtiva
- Workflow robusto e consistente

---

# 🏛️ Princípios Arquiteturais

- Evolução incremental (não reescrever sistema)
- Schema diff (não redesign completo)
- Append-only para eventos críticos
- Separação entre estrutura, execução e análise
- Capability-driven workflow
- Fonte de verdade vs read models

---

# 📦 Ordem de Implementação

```
Step 14 → UOM (unidades de medida)
Step 15 → ProductionUnit + Consórcio
Step 16 → Propagação de FKs
Step 17 → OperationExecution
Step 18 → Inventory Ledger
Step 19 → Cost Allocation
Step 20 → Scenarios
```

---

# 📏 STEP 14 — Measurement Foundation

## Tabelas

- unidades_medida
- unidades_medida_conversoes

## Conceitos

### Unidade de Medida

- Dimensões: massa, volume, área, tempo, contagem, moeda, hora_maquina, hora_homem
- Campos principais:
  - fator_canonico
  - codigo_canonico
  - eh_canonica
  - casas_decimais

## Decisões

- 1 unidade canônica por dimensão (enforced no banco)
- Precisão de cálculo ≠ precisão de apresentação
- SC50/SC60 como unidades próprias
- Moeda (BRL) dentro do domínio de UOM
- Conversões preparadas para casos complexos (cultura, umidade, densidade)

## Status

✅ Step 14 aprovado e pronto para deploy

---

# 🌱 STEP 15 — ProductionUnit

## Conceito

ProductionUnit = Safra + Cultivo + Área

Representa:

- Unidade econômica
- Unidade operacional
- Centro de custo agrícola
- Unidade analítica

## Tabela: production_units (mantida em inglês)

### Campos

- tenant_id
- safra_id
- cultivo_id
- area_id
- cultivo_area_id (origem/backfill)
- percentual_participacao
- area_ha (snapshot)
- status (ATIVA, ENCERRADA, CANCELADA)
- datas

## Regras

- percentual_participacao > 0 e ≤ 100
- soma por área ≤ 100
- unicidade parcial ignorando CANCELADA

---

# 🔐 Controle de Concorrência

## Estratégia

PostgreSQL Advisory Lock:

```
pg_advisory_xact_lock(hashtextextended('pu_area:tenant:safra:area'))
```

## Defense in depth

1. Advisory lock (service)
2. Constraint trigger DEFERRABLE (DB)
3. Job noturno (detecção)

---

# 📊 status_consorcio_area

## Tipo

Read model + gate seletivo

## Fonte de verdade

production_units.percentual_participacao

## Estados

- VAZIO
- INCOMPLETO (< 99,99)
- VALIDO (99,99–100,01)
- INCONSISTENTE (> 100,01)

## Uso

- Dashboards
- Validação operacional

### Gates

- Bloqueia mutações se INCONSISTENTE
- Bloqueia encerramento de safra se != VALIDO

---

# 💰 Centro de Custo

ProductionUnit é o centro de custo agrícola canônico

- Não existe tabela separada de centros de custo
- Rateio tratado no Step 19

---

# ⚖️ Rateio

Default: AREA_HA

- Não pertence à ProductionUnit
- Implementado em cost_allocations (Step 19)

---

# 📦 Naming Convention

- Banco: pt-BR
- Exceção: production_units
- snake_case
- tabelas no plural
- FKs: entidade_id
- enums em pt-BR
- timestamps em inglês

---

# 🔐 Ledger (definição antecipada)

- append-only
- sem UPDATE/DELETE
- correções via adjustment_of

---

# 🧪 Testes

Cobertura obrigatória:

- Partial unique
- Constraint trigger deferred
- Advisory lock
- Idempotência de migrations
- Integridade de consórcio
- Rebuild de read model

---

# 🚀 Status Atual

- Step 14: concluído e aprovado
- Step 15: desenho aprovado
- Próximo: gerar DDL do Step 15

---

# 📌 Conclusão

O sistema evoluiu para um modelo transacional agrícola com:

- consistência forte
- controle de concorrência
- base econômica real
- suporte a consórcios
- preparação para analytics e IA

---

# 🔜 Próximo Passo

Gerar migration:

```
step15_production_units.py
```

com:

- tabelas
- triggers
- backfill
- constraints
- testes
- plano de rollout

---

Este documento pode ser usado como contexto inicial para novos chats ou agentes de IA.

