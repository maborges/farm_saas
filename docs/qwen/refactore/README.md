# 📋 Índice — Refatoração Completa (3 Frentes)

**Criado:** 2026-04-06

---

## Documentos

| # | Documento | Caminho | Frentes | Descrição |
|---|-----------|---------|---------|-----------|
| 0 | **Contexto de Reinício** | `00-contexto-reinicio.md` | Todas | **PONTO DE ENTRADA** — tudo que foi analisado e decidido |
| 1 | **Análise de Impacto** | `01-analise-impacto.md` | A, B | Gap entre conceito arquitetural e implementação atual |
| 2 | **Plano Hierárquico** | `02-plano-hierarquia-completa.md` | A | Especificação técnica da hierarquia territorial + precisão |
| 3 | **Backlog por Módulo** | `03-backlogs-modulos.md` | A, B | Backlog detalhado por módulo/submódulo |
| 4 | **Sprints Refactore** | `04-sprints-refactore.md` | A | 4 sprints RF-01 a RF-04 (versão original, só Frente A) |
| 5 | **Matriz de Risco** | `05-matriz-risco.md` | Todas | Riscos, mitigação, rollback, script de diagnóstico |
| 6 | **Resumo Executivo** | `06-resumo-executivo.md` | Todas | Visão gerencial para aprovação |
| 7 | **Custeio Automático** | `07-custeio-automatico-analise.md` | B | Gap custeio ↔ financeiro, tarefas CF-01 a CF-11 |
| 8 | **Workflow Execução** | `08-workflow-execucao.md` | Todas | Workflow: branches, commits, CI/CD, rollback |
| 9 | **Backlog Completo** | `09-backlog-completo.md` | Todas | **141h** — ~110 tarefas das 3 frentes consolidadas |
| 10 | **Sprints Unificadas** | `10-sprints-unificadas.md` | Todas | **5 sprints** (00 + RF-01 a RF-04) com ordem e dependências |
| 11 | **Especificação Propriedade** | `11-especificacao-propriedade.md` | C | Modelos Propriedade, ExploracaoRural, DocumentoExploracao |

---

## Resumo das 3 Frentes

| Frente | Tema | Esforço | Sprints | Documentos-chave |
|--------|------|---------|---------|-----------------|
| **C** | Propriedade + Exploração Rural | 34h | Sprint 00 | `11-especificacao-propriedade.md` |
| **A** | Hierarquia + Agricultura de Precisão | 75h | RF-01, RF-02 | `02-plano-hierarquia-completa.md` |
| **B** | Custeio Automático → Financeiro | 32h | RF-03 | `07-custeio-automatico-analise.md` |

**Total: 141h em 5 sprints de 2 semanas = 10 semanas**

---

## Para quem vai executar agora

1. Leia `00-contexto-reinicio.md` (5min) — entende o panorama geral
2. Leia `10-sprints-unificadas.md` (5min) — entende a ordem de execução
3. Se vai iniciar pela Frente C: leia `11-especificacao-propriedade.md`
4. Se vai iniciar pela Frente A: leia `02-plano-hierarquia-completa.md`
5. Se vai iniciar pela Frente B: leia `07-custeio-automatico-analise.md`
6. Consulte `09-backlog-completo.md` para ver todas as tarefas
7. Consulte `05-matriz-risco.md` antes de fazer deploy
8. Consulte `08-workflow-execucao.md` para o workflow de branches e CI/CD
