# Resumo Executivo — Refatoração Hierárquica + Agricultura de Precisão

**Data:** 2026-04-06
**Status:** Pronto para aprovação

---

## O que é

Refatoração de **~109 horas** em **4 sprints** para alinhar a implementação ao conceito arquitetural definido em `docs/architecture/agro-conceitos-arquitetura.md` e habilitar agricultura de precisão com hierarquia completa de 5 níveis.

## Por que

O sistema atual tem **~70% de conformidade** com o conceito arquitetural. Os gaps principais são:

1. **Sem SUBTALHAO nem ZONA_DE_MANEJO** — impossibilita agricultura de precisão
2. **Sem validação de hierarquia** — permite erros conceituais (ex: piquete dentro de APP)
3. **`Safra.talhao_id` obrigatório** — impede safra multi-talhão
4. **Sem histórico de uso** — não suporta ILP ou rotação de culturas
5. **Sem amostras de solo georreferenciadas** — sem base científica para zonas

## Escopo

| Incluído | Excluído |
|----------|----------|
| 5 níveis: Fazenda→Gleba→Talhão→Subtalhão→Zona | Unificar Safra + Pecuária |
| Validação semântica de hierarquia | Renomear Safra → CicloProdutivo |
| Campos de precisão no modelo | Reescrever módulo pecuário |
| Histórico de uso temporal | |
| Amostras de solo | |
| Prescrição VRA por zona | |
| Indicadores econômicos (margem, ROI) | |

## Esforço

| Sprint | Tema | Backend | Frontend | Total |
|--------|------|---------|----------|-------|
| RF-01 | Fundação Territorial | 14h | 16h | 30h |
| RF-02 | Dados Precisão + Histórico | 14h | 18h | 32h |
| RF-03 | VRA por Zona + Polimento | 8h | 17h | 25h |
| RF-04 | Indicadores + Polimento | 11h | 11h | 22h |
| **TOTAL** | | **47h** | **62h** | **109h** |

## Riscos

- **Migração é aditiva** — nada que funciona quebra
- **Rollback fácil** — `alembic downgrade` em cada sprint
- **Script de diagnóstico** pré-deploy detecta inconsistências
- **RF-01 é bloqueante** para RF-02 e RF-03; RF-04 pode rodar em paralelo

## Resultado Esperado

| Dimensão | Antes | Depois |
|----------|-------|--------|
| ESPAÇO (território) | 75% | **95%** |
| TEMPO (ciclo) | 85% | **92%** |
| EXECUÇÃO (operação) | 95% | **98%** |
| RESULTADO (economia) | 70% | **85%** |
| Agricultura de precisão | 20% | **90%** |

## Documentos Gerados

| # | Arquivo | Conteúdo |
|---|---------|----------|
| 1 | `docs/qwen/refactore/README.md` | Índice mestre |
| 2 | `01-analise-impacto.md` | Gap conceito vs implementação |
| 3 | `02-plano-hierarquia-completa.md` | Especificação técnica completa |
| 4 | `03-backlogs-modulos.md` | Backlog por módulo com estimativas |
| 5 | `04-sprints-refactore.md` | 4 sprints com tarefas e critérios |
| 6 | `05-matriz-risco.md` | Riscos, mitigação, rollback, diagnóstico |

---

**Próximo passo:** Aprovar o plano e iniciar Sprint RF-01.
