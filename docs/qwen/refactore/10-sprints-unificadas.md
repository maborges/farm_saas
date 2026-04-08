# Sprints Unificadas — 3 Frentes de Refatoração

**Data:** 2026-04-06
**Total de Sprints:** 5 + 1 (hardening)
**Duração por sprint:** 2 semanas

---

## Sprint 00 — Fundação: Propriedade + Exploração Rural (Frente C)

**Tema:** Separar quem produz (Propriedade) de onde produz (Fazenda)
**Duração:** 2 semanas
**Esforço:** ~34h (Backend: 15h, Frontend: 19h)

### Objetivos
1. Modelos `Propriedade`, `ExploracaoRural`, `DocumentoExploracao` criados
2. Migração de dados de `GrupoFazendas` → `Propriedade` funcionando
3. CRUD completo de Propriedade e Exploração
4. Upload/download de documentos de exploração
5. UI de lista e detalhe de Propriedades

### Backlog

| # | Tarefa | Tipo | Esforço |
|---|--------|------|---------|
| 1 | Modelos + enums (C-01, C-02) | Backend | 2h15 |
| 2 | Schemas Pydantic (C-03) | Backend | 1h |
| 3 | Service com validações (C-04) | Backend | 2h |
| 4 | Router CRUD + Documentos (C-05) | Backend | 2h |
| 5 | Migration 3 tabelas + migração dados (C-06) | Backend | 3h |
| 6 | Registrar router no main.py (C-07) | Backend | 15min |
| 7 | Testes unitários (C-08, C-09) | Backend | 1h30 |
| 8 | Testes integração (C-10) | Backend | 2h |
| 9 | Zod schemas (CF-C1) | Frontend | 1h |
| 10 | Lista de Propriedades (CF-C2) | Frontend | 4h |
| 11 | Detalhe da Propriedade com abas (CF-C3) | Frontend | 6h |
| 12 | Dialog de Exploração (CF-C4) | Frontend | 3h |
| 13 | Upload de documentos (CF-C5) | Frontend | 3h |
| 14 | Fazenda exibe vínculo de exploração (CF-C6) | Frontend | 2h |

### Critérios de Aceite
- [ ] Criar Propriedade com CNPJ, IE, email funciona
- [ ] Vincular Fazenda à Propriedade via ExploracaoRural funciona
- [ ] Natureza `arrendamento` com vigência (data_inicio, data_fim) funciona
- [ ] Sobreposição de vigência retorna erro 422
- [ ] Upload de contrato PDF vinculado à exploração funciona
- [ ] Listar propriedades mostra CNPJ, nº fazendas, status
- [ ] GrupoFazendas continua funcionando (migração gradual, sem breaking change)

### Definição de Pronto
- [ ] Migration up/down testados
- [ ] Testes unitários passando (>90%)
- [ ] Testes integração passando
- [ ] Lint/typecheck sem erros
- [ ] Zero regressões em GrupoFazendas

---

## Sprint RF-01 — Hierarquia Base (Frente A, parte 1)

**Tema:** Tipos semânticos + validação de hierarquia
**Duração:** 2 semanas
**Esforço:** ~24h (Backend: 14h, Frontend: 10h)

### Objetivos
1. `SUBTALHAO` + `ZONA_DE_MANEJO` no enum
2. Colunas de precisão no `AreaRural`
3. `HistoricoUsoTalhao` + `AmostraSolo` (modelos)
4. Validação hierárquica no backend
5. UI de árvore hierárquica

### Backlog

| # | Tarefa | Tipo | Esforço |
|---|--------|------|---------|
| 1 | Enum + colunas precisão + novos modelos (A-01 a A-04) | Backend | 3h15 |
| 2 | Migration (A-05) | Backend | 2h |
| 3 | Popular nivel_profundidade (A-06) | Backend | 1h |
| 4 | validar_hierarquia() + calcular_soma_areas() + obter_arvore() (A-07 a A-09) | Backend | 3h30 |
| 5 | Router: validação POST + endpoints novos (A-10 a A-13) | Backend | 3h |
| 6 | Schemas expandidos (A-14, A-15) | Backend | 1h30 |
| 7 | RN-CP-004 bloqueante (A-16) | Backend | 2h |
| 8 | Testes unitários + integração (A-17 a A-19) | Backend | 5h |
| 9 | Zod schemas (AF-A1) | Frontend | 2h |
| 10 | AreaTree.tsx (AF-A2) | Frontend | 6h |
| 11 | Aba Hierarquia (AF-A6) | Frontend | 4h |
| 12 | RN-CP-004 visual bloqueante (AF-A8) | Frontend | 2h |

### Critérios de Aceite
- [ ] Criar `SUBTALHAO` dentro de `TALHAO` funciona
- [ ] Criar `TALHAO` dentro de `APP` retorna erro 422
- [ ] Endpoint `/arvore` retorna JSON hierárquico
- [ ] Soma talhões > 105% bloqueada no backend
- [ ] `AreaTree` renderiza árvore expansível
- [ ] Progress bar vermelha quando > 105%

### Definição de Pronto
- [ ] Migration up/down
- [ ] Testes >90% coverage
- [ ] Lint/typecheck OK

---

## Sprint RF-02 — Dados de Precisão + Polimento (Frente A, parte 2)

**Tema:** Histórico, amostras, Safra nullable, UI completa
**Duração:** 2 semanas
**Esforço:** ~51h (Backend: 12h, Frontend: 39h)

### Backlog

| # | Tarefa | Tipo | Esforço |
|---|--------|------|---------|
| 1 | Safra.talhao_id nullable (A-20) | Backend | 2h |
| 2 | Restringir OperacaoAgricola.talhao_id (A-21) | Backend | 1h |
| 3 | Safra.talhao_id nullable migration testada | Backend | 1h |
| 4 | HistoricoUsoTimeline.tsx (AF-A4) | Frontend | 3h |
| 5 | AmostrasSoloMap.tsx (AF-A5) | Frontend | 6h |
| 6 | Aba Amostras de Solo (AF-A7) | Frontend | 4h |
| 7 | ZonaManejoDialog.tsx (AF-A3) | Frontend | 4h |
| 8 | Editar propriedade (AF-A11) | Frontend | 2h |
| 9 | Desativar/Reativar (AF-A12) | Frontend | 2h |
| 10 | Editar/excluir na lista (AF-A13) | Frontend | 2h |
| 11 | Empty state com CTA (AF-A14) | Frontend | 1h |
| 12 | Campos opcionais no form (AF-A15) | Frontend | 2h |
| 13 | Validação CAR frontend (AF-A16) | Frontend | 1h |
| 14 | Prescrição VRA por zona (AF-A9) | Frontend | 8h |
| 15 | Upload grade GeoJSON (AF-A10) | Frontend | 4h |

### Critérios de Aceite
- [ ] Registrar histórico de uso funciona (Soja 24/25 → Milho 2025)
- [ ] Timeline visual mostra alternância de culturas
- [ ] Cadastrar amostra de solo com coordenadas GPS funciona
- [ ] Mapa exibe pontos de amostra sobrepostos a polígonos
- [ ] `Safra.talhao_id` pode ser NULL
- [ ] Editar/desativar propriedade funcionais
- [ ] Empty state com ilustração + CTA
- [ ] Formato CAR validado no frontend

---

## Sprint RF-03 — Custeio Automático (Frente B)

**Tema:** Operação → Despesa → Rateio → Centro de Custo
**Duração:** 2 semanas
**Esforço:** ~32h (Backend: 18h, Frontend: 14h)

### Backlog

| # | Tarefa | Tipo | Esforço |
|---|--------|------|---------|
| 1 | Criar Rateio automático na despesa da operação (B-01) | Backend | 1h |
| 2 | Lookup table operação → plano de conta (B-02) | Backend | 2h |
| 3 | CustosService lê despesas do financeiro (B-03) | Backend | 2h |
| 4 | Custo de mão de obra na operação (B-04) | Backend | 3h |
| 5 | Custo de máquina na operação (B-05) | Backend | 3h |
| 6 | Testes integração: operação → despesa → rateio (B-06) | Backend | 2h |
| 7 | Margem líquida e ROI (B-07) | Backend | 2h |
| 8 | Comparativo inter-safras (B-08) | Backend | 3h |
| 9 | Dashboard unificado (BF-B1) | Frontend | 4h |
| 10 | Alerta divergência (BF-B2) | Frontend | 2h |
| 11 | UI indicadores econômicos (BF-B3) | Frontend | 4h |
| 12 | UI comparativo inter-safras (BF-B4) | Frontend | 4h |

### Critérios de Aceite
- [ ] Despesa criada pela operação tem Rateio vinculado (safra + talhão)
- [ ] `centro_custos()` do financeiro enxerga custos das operações
- [ ] Dashboard agrícola e financeiro mostram o mesmo custo
- [ ] Margem líquida e ROI calculados e exibidos
- [ ] Comparativo inter-safras lado a lado funciona

---

## Sprint RF-04 — Integração + Hardening

**Tema:** Juntar tudo, testar tudo, zerar bugs
**Duração:** 2 semanas
**Esforço:** ~20h (Backend: 8h, Frontend: 12h)

### Backlog

| # | Tarefa | Tipo | Esforço |
|---|--------|------|---------|
| 1 | Revisar todas migrations (conflitos, downgrade) | Backend | 2h |
| 2 | Script de diagnóstico pré-deploy | Backend | 1h |
| 3 | Smoke tests end-to-end | Backend | 2h |
| 4 | Performance: queries N+1 em obter_arvore | Backend | 1h |
| 5 | Documentação Swagger atualizada | Backend | 2h |
| 6 | Revisão de acessibilidade e responsividade | Frontend | 4h |
| 7 | Bug fixing de tudo que foi reportado | Ambos | 4h |
| 8 | Revisão geral de testes | QA | 4h |

### Critérios de Aceite
- [ ] Zero regressões em funcionalidades existentes
- [ ] Coverage geral > 85%
- [ ] Zero erros de type check
- [ ] p95 < 500ms para `/arvore`
- [ ] UI responsiva em tablet (1024px)
- [ ] Zero bugs Alta/Crítica abertos
- [ ] Documentação API atualizada

---

## Linha do Tempo

```
Semana 1-2   Sprint 00   ██████████  Propriedade + Exploração Rural
Semana 3-4   Sprint RF-01 ██████████  Hierarquia base + validação
Semana 5-6   Sprint RF-02 ██████████  Dados precisão + UI completa
Semana 7-8   Sprint RF-03 ██████████  Custeio automático + financeiro
Semana 9-10  Sprint RF-04 ██████████  Integração + hardening
```

**Pode iniciar RF-01 em paralelo com Sprint 00** se a equipe permitir.
**RF-03 depende de A-20** (Safra.talhao_id nullable) — pode iniciar após Sprint RF-01.

---

## Resumo de Sprints

| Sprint | Tema | Backend | Frontend | Total |
|--------|------|---------|----------|-------|
| **00** | Propriedade + Exploração | 15h | 19h | 34h |
| **RF-01** | Hierarquia base | 14h | 10h | 24h |
| **RF-02** | Dados precisão + UI | 12h | 39h | 51h |
| **RF-03** | Custeio + Financeiro | 18h | 14h | 32h |
| **RF-04** | Integração + Hardening | 8h | 12h | 20h |
| **TOTAL** | | **67h** | **94h** | **161h** |
