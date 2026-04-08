# 🔀 Refatoração Completa — Contexto de Reinício

**Criado:** 2026-04-06
**Última atualização:** 2026-04-06
**Status:** Planejamento completo — pronto para execução

---

## 1. O que é este documento

Este é o **ponto de entrada** para quem vai executar a refatoração. Contém tudo que foi analisado, decidido e planejado até aqui. Se o trabalho parar e recomeçar, basta ler este arquivo e seguir para os documentos listados.

---

## 2. Escopo da Refatoração (3 frentes independentes)

### Frente A: Hierarquia Territorial + Agricultura de Precisão
**Tema:** Fazenda → Gleba → Talhão → Subtalhão → Zona de Manejo

- 2 novos tipos no enum: `SUBTALHAO`, `ZONA_DE_MANEJO`
- Validação semântica de hierarquia (não cria PIQUETE dentro de APP)
- 11 colunas de precisão dedicadas (tipo_solo, ph_solo, teor_argila...)
- 2 tabelas novas: `HistoricoUsoTalhao`, `AmostraSolo`
- UI de hierarquia em árvore
- Prescrição VRA por zona

📄 **Detalhes:** `02-plano-hierarquia-completa.md`
📄 **Backlog:** `03-backlogs-modulos.md` (seção CORE)
📄 **Sprints:** `04-sprints-refactore.md` (RF-01 a RF-04)

### Frente B: Custeio Automático → Financeiro
**Tema:** Operação → Custo → Despesa → Rateio → Centro de Custo

- Gap crítico: despesa automática NÃO cria rateio
- `Safra.talhao_id` → nullable (usa SafraTalhao N:N)
- Plano de conta específico por tipo de operação
- Custos de MO e máquina na operação

📄 **Detalhes:** `07-custeio-automatico-analise.md`

### Frente C: Propriedade (Econômica) + Exploração Rural (Vínculo)
**Tema:** Separação entre quem produz (Propriedade) e onde produz (Fazenda)

- `Propriedade` = unidade econômica (substitui `GrupoFazendas`)
- `ExploracaoRural` = vínculo temporal entre Propriedade e Fazenda
- 5 naturezas: própria, arrendamento, parceria, comodato, posse
- Controle de documentos por vínculo (contrato, CCIR, ITR, CAR)
- Histórico temporal: mesma fazenda pode ter diferentes exploradores

📄 **Base conceitual:** `docs/architecture/conceituacao-propriedade.md`

---

## 3. Estado Atual (o que existe no código hoje)

| Entidade | Tabela | Arquivo do modelo | Status |
|----------|--------|-------------------|--------|
| Fazenda | `fazendas` | `core/models/fazenda.py` | ✅ Completo |
| GrupoFazendas | `grupos_fazendas` | `core/models/grupo_fazendas.py` | ✅ Existe — será substituído por Propriedade |
| AreaRural | `cadastros_areas_rurais` | `core/cadastros/propriedades/models.py` | ✅ Existe — precisa de SUBTALHAO + ZONA + colunas precisão |
| Safra | `safras` | `agricola/safras/models.py` | ✅ Existe — `talhao_id` obrigatório (precisa ser nullable) |
| OperacaoAgricola | `operacoes_agricolas` | `agricola/operacoes/models.py` | ✅ Existe — cria despesa mas SEM rateio |
| FinDespesa | `fin_despesas` | `financeiro/models/despesa.py` | ✅ Existe |
| FinRateio | `fin_rateios` | `financeiro/models/rateio.py` | ✅ Existe — mas NÃO é preenchido automaticamente |
| PrescricaoVRA | `prescricoes_vra` | `agricola/amostragem_solo/models/prescricoes_vra.py` | ✅ Existe |
| Propriedade (nova) | — | **Não existe** | ❌ Criar |
| ExploracaoRural (nova) | — | **Não existe** | ❌ Criar |
| DocumentoExploracao (novo) | — | **Não existe** | ❌ Criar |
| HistoricoUsoTalhao (novo) | — | **Não existe** | ❌ Criar |
| AmostraSolo (nova) | — | **Não existe** | ❌ Criar |

---

## 4. Relação entre as 3 Frentes

```
Frente C: Propriedade + Exploração         ← Fundação (precede as demais)
    │
    ├── Fazenda (agora vinculada via ExploracaoRural)
    │   │
    │   └── Frente A: Hierarquia Territorial
    │       ├── Gleba → Talhão → Subtalhão → Zona de Manejo
    │       ├── Colunas de precisão
    │       ├── HistoricoUsoTalhao
    │       └── AmostraSolo
    │           │
    │           └── Frente B: Custeio Automático
    │               ├── Operação → Despesa → Rateio
    │               ├── Safra.talhao_id nullable
    │               └── Custos MO + máquina
    │
    └── Safra vinculada a Propriedade (não mais diretamente a Fazenda)
```

**Ordem de execução recomendada:** Frente C → Frente A → Frente B

Mas A e B podem ser executadas antes de C se necessário, pois são **independentes conceitualmente** — o vínculo Propriedade↔Fazenda não bloqueia hierarquia nem custeio.

---

## 5. Documentos gerados

| # | Arquivo | Frentes | Conteúdo |
|---|---------|---------|----------|
| 1 | `00-contexto-reinicio.md` | Todas | **ESTE ARQUIVO** — ponto de entrada |
| 2 | `01-analise-impacto.md` | A, B | Gap entre conceito arquitetural e implementação |
| 3 | `02-plano-hierarquia-completa.md` | A | Especificação técnica: modelos, schemas, service, router, migration |
| 4 | `03-backlogs-modulos.md` | Todas | Backlog detalhado por módulo com IDs e esforço |
| 5 | `04-sprints-refactore.md` | A | 4 sprints RF-01 a RF-04 |
| 6 | `05-matriz-risco.md` | Todas | 18 riscos, rollback, script de diagnóstico, checklist deploy |
| 7 | `06-resumo-executivo.md` | Todas | Visão gerencial para aprovação |
| 8 | `07-custeio-automatico-analise.md` | B | Gap custeio ↔ financeiro, tarefas CF-01 a CF-11 |
| 9 | `08-workflow-execucao.md` | Todas | Workflow de execução: branches, commits, CI/CD, rollback |
| 10 | `09-backlog-completo.md` | Todas | **NOVO** — backlog unificado das 3 frentes |
| 11 | `10-sprints-unificadas.md` | Todas | **NOVO** — sprints reorganizadas com C→A→B |
| 12 | `11-especificacao-propriedade.md` | C | **NOVO** — modelos Propriedade, ExploracaoRural, DocumentoExploracao |

---

## 6. Decisões Arquiteturais (registradas para não perder)

| Decisão | Racional | Status |
|---------|----------|--------|
| `AreaRural` continua como tabela polimórfica | Já funciona, só adicionar tipos e colunas | ✅ Decidido |
| `Fazenda` continua existindo como entidade territorial | É o imóvel rural físico — não conflita com Propriedade | ✅ Decidido |
| `GrupoFazendas` será substituído por `Propriedade` | Grupo é só agrupamento visual; Propriedade é unidade econômica | ✅ Decidido |
| `Safra` NÃO será renomeada para `CicloProdutivo` | 50+ FKs, 7 módulos, risco altíssimo | ✅ Decidido — manter Safra |
| `dados_extras` JSON NÃO será migrado para colunas | Migração complexa; adicionar colunas novas gradualmente | ✅ Decidido |
| Agricultura + Pecuária NÃO serão unificados sob `CicloProdutivo` | 200h+, risco altíssimo | ✅ Decidido — adiar |
| Validação de hierarquia é **bloqueante no backend** | Não pode criar PIQUETE dentro de APP | ✅ Decidido |
| `OperacaoService.criar()` continua criando despesa automática | Só adicionar rateio | ✅ Decidido |
| `ExploracaoRural` é entidade intermediária | Propriedade e Fazenda não se relacionam diretamente | ✅ Decidido |
| Documentos de exploração ficam em tabela separada | Múltiplos documentos por vínculo com validade | ✅ Decidido |

---

## 7. Próximo Passo para Execução

1. **Leia** `09-backlog-completo.md` para ver todas as tarefas
2. **Leia** `10-sprints-unificadas.md` para ver a ordem de execução
3. **Leia** `11-especificacao-propriedade.md` para os modelos novos da Frente C
4. **Inicie** pela Sprint 00 (Frente C: Propriedade) ou Sprint RF-01 (Frente A: Hierarquia), dependendo da prioridade de negócio

---

## 8. Métricas Consolidadas

| Métrica | Valor |
|---------|-------|
| Total de tarefas | ~110 |
| Backend | ~55h |
| Frontend | ~65h |
| Migrations novas | ~8 |
| Tabelas novas | 6 (Propriedade, ExploracaoRural, DocumentoExploracao, HistoricoUsoTalhao, AmostraSolo, +1 colunas AreaRural) |
| Sprints | 5 (Sprint 00 + RF-01 a RF-04) |
| Duração estimada | 10 semanas |
| Riscos críticos | 3 |
| Riscos médios | 7 |
