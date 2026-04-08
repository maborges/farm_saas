# Sprints de Refatoração — Hierarquia + Agricultura de Precisão

**Data:** 2026-04-06
**Total de Sprints:** 4
**Duração estimada por sprint:** 2 semanas

---

## Sprint RF-01 — Fundação Territorial

**Tema:** Tipos semânticos + validação de hierarquia
**Duração:** 2 semanas
**Esforço:** ~30h (Backend: 14h, Frontend: 16h)

### Objetivos
1. Adicionar `SUBTALHAO` e `ZONA_DE_MANEJO` ao sistema
2. Validar hierarquia no backend (impedir erros conceituais)
3. Campos de agricultura de precisão disponíveis
4. UI de hierarquia em árvore

### Backlog

| # | Tarefa | Backlog ID | Módulo | Esforço |
|---|--------|-----------|--------|---------|
| 1 | Adicionar `SUBTALHAO` + `ZONA_DE_MANEJO` ao enum `TipoArea` | C-01 | Backend | 15min |
| 2 | Adicionar colunas de precisão ao `AreaRural` | C-02 | Backend | 1h |
| 3 | Adicionar `nivel_profundidade` ao `AreaRural` | C-02b | Backend | 30min |
| 4 | `validar_hierarquia()` no `AreaRuralService` | C-08 | Backend | 2h |
| 5 | Aplicar validação no POST do router | C-11 | Backend | 30min |
| 6 | Criar migration (tipos + colunas) | C-06 (parcial) | Backend | 2h |
| 7 | Script popular `nivel_profundidade` existente | C-07 | Backend | 1h |
| 8 | Endpoint `GET /{area_id}/arvore` | C-12 | Backend | 30min |
| 9 | Endpoint `GET /{area_id}/soma-areas` | C-13 | Backend | 30min |
| 10 | `calcular_soma_areas()` no Service | C-09 | Backend | 30min |
| 11 | Expandir schemas `AreaRuralCreate/Update` | C-16 | Backend | 30min |
| 12 | Testes unitários: validação hierárquica | C-20 | Backend | 2h |
| 13 | Atualizar Zod schemas (`fazenda-schemas.ts` + novos) | CF-01, CF-02 | Frontend | 3h |
| 14 | Componente `AreaTree.tsx` | CF-03 | Frontend | 6h |
| 15 | Nova aba "Hierarquia" na página de detalhe | CF-07 | Frontend | 4h |
| 16 | Integrar `AreaTree` na aba Hierarquia | CF-07b | Frontend | 2h |
| 17 | Validar RN-CP-004 no backend (soma ≤ 105%) | C-19 | Backend | 2h |
| 18 | Integrar RN-CP-004 visual bloqueante no frontend | CF-09 | Frontend | 2h |

### Critérios de Aceite

- [ ] Criar `SUBTALHAO` dentro de `TALHAO` funciona
- [ ] Criar `ZONA_DE_MANEJO` dentro de `SUBTALHAO` funciona
- [ ] Criar `TALHAO` dentro de `APP` retorna erro 422
- [ ] Criar `ZONA_DE_MANEJO` como raiz retorna erro 422
- [ ] Endpoint `/arvore` retorna JSON hierárquico correto
- [ ] Endpoint `/soma-areas` retorna soma correta dos filhos
- [ ] Soma de talhões > 105% bloqueada no backend
- [ ] Progress bar no frontend fica vermelha e bloqueia quando > 105%
- [ ] `AreaTree` renderiza árvore expansível com ícones por tipo
- [ ] Zod schemas incluem campos de precisão

### Definição de Pronto

- [ ] Migration criada e aplicada
- [ ] Testes unitários passando (>90% coverage)
- [ ] Testes de integração passando
- [ ] Lint/typecheck sem erros
- [ ] Documentação de API atualizada (Swagger)

---

## Sprint RF-02 — Dados de Precisão + Histórico

**Tema:** Amostras de solo + histórico de uso + edição de propriedade
**Duração:** 2 semanas
**Esforço:** ~32h (Backend: 14h, Frontend: 18h)

### Backlog

| # | Tarefa | Backlog ID | Módulo | Esforço |
|---|--------|-----------|--------|---------|
| 1 | Criar modelo `HistoricoUsoTalhao` | C-03 | Backend | 1h |
| 2 | Criar modelo `AmostraSolo` | C-04 | Backend | 1h |
| 3 | Adicionar relationships `historico_uso` + `amostras_solo` | C-05 | Backend | 15min |
| 4 | Migration (tabelas novas) | C-06 (parcial) | Backend | 2h |
| 5 | Schemas `HistoricoUsoCreate/Response` | C-17 | Backend | 30min |
| 6 | Schemas `AmostraSoloCreate/Response` | C-18 | Backend | 30min |
| 7 | Endpoints `GET/POST /{area_id}/historico-uso` | C-14 | Backend | 1h |
| 8 | Endpoints `GET/POST /{area_id}/amostras-solo` | C-15 | Backend | 1h |
| 9 | Testes integração: histórico de uso | C-22 | Backend | 1h |
| 10 | Testes integração: amostras de solo | C-23 | Backend | 1h |
| 11 | Tornar `Safra.talhao_id` nullable | A-01 | Backend | 2h |
| 12 | Restringir `OperacaoAgricola.talhao_id` a tipos válidos | A-02 | Backend | 1h |
| 13 | Componente `HistoricoUsoTimeline.tsx` | CF-05 | Frontend | 3h |
| 14 | Componente `AmostrasSoloMap.tsx` | CF-06 | Frontend | 6h |
| 15 | Nova aba "Amostras de Solo" na página de detalhe | CF-08 | Frontend | 4h |
| 16 | Botão "Editar propriedade" (hoje stub) | CF-10 | Frontend | 2h |
| 17 | Botão "Desativar/Reativar" (hoje stub) | CF-11 | Frontend | 2h |
| 18 | Campos opcionais no form de criação (CAR, NIRF, IE) | CF-14 | Frontend | 2h |

### Critérios de Aceite

- [ ] Registrar histórico de uso (Soja 24/25 → Milho 2025) funciona
- [ ] Timeline visual mostra alternância de culturas
- [ ] Cadastrar amostra de solo com coordenadas GPS funciona
- [ ] Mapa exibe pontos de amostra sobrepostos a polígonos
- [ ] `Safra.talhao_id` pode ser NULL (usa-se `SafraTalhao` N:N)
- [ ] Operação agrícola rejeita vínculo com GLEBA, SEDE, APP
- [ ] Editar propriedade abre formulário com dados atuais
- [ ] Desativar propriedade com dependências mostra mensagem clara
- [ ] Form de criação inclui CAR, NIRF, Inscrição Estadual

### Definição de Pronto

- [ ] Migration aplicada
- [ ] Testes passando
- [ ] Lint/typecheck OK
- [ ] Nenhum regression bug em safras/operacoes existentes

---

## Sprint RF-03 — Agricultura de Precisão na Prática

**Tema:** Zonas de manejo + Prescrição VRA por zona
**Duração:** 2 semanas
**Esforço:** ~25h (Backend: 8h, Frontend: 17h)

### Backlog

| # | Tarefa | Backlog ID | Módulo | Esforço |
|---|--------|-----------|--------|---------|
| 1 | Componente `ZonaManejoDialog.tsx` | CF-04 | Frontend | 4h |
| 2 | UI de criação de subtalhão no dialog | CF-04b | Frontend | 3h |
| 3 | UI de criação de zona de manejo no dialog | CF-04c | Frontend | 3h |
| 4 | UI de prescrição por zona (mapa colorido) | VF-01 | Frontend | 8h |
| 5 | Upload de grade de prescrição (GeoJSON) | VF-02 | Frontend | 4h |
| 6 | Validar prescrição VRA para SUBTALHAO/ZONA | V-01 | Backend | 1h |
| 7 | Campo `nivel_area` em `PrescricaoVRA` | V-01b | Backend | 1h |
| 8 | Endpoint `GET /prescricoes/safra/{id}/por-zona` | V-02 | Backend | 2h |
| 9 | Validar soma de áreas das zonas = área do subtalhão | V-03 | Backend | 2h |
| 10 | Testes: operação com subtalhão/zona | A-06 | Backend | 1h |
| 11 | Botão editar/excluir na lista de propriedades | CF-12 | Frontend | 2h |
| 12 | Empty state com CTA na lista | CF-13 | Frontend | 1h |
| 13 | Validação de formato CAR no frontend | CF-15 | Frontend | 1h |

### Critérios de Aceite

- [ ] Criar zona de manejo dentro de subtalhão via UI
- [ ] Zona de manejo exibe dados de solo e produtividade
- [ ] Prescrição VRA pode ser criada por zona de manejo
- [ ] Mapa de prescrição exibe zonas coloridas por dose
- [ ] Upload de GeoJSON de grade de prescrição funciona
- [ ] Validação: soma de áreas das zonas = área do subtalhão (tolerância 2%)
- [ ] Lista de propriedades tem botões de editar e excluir
- [ ] Empty state exibe ilustração + CTA "Nova Propriedade"
- [ ] Formato CAR validado no frontend (UF + 12 dígitos)

### Definição de Pronto

- [ ] Testes de prescrição por zona passando
- [ ] Mapa de prescrição funcional em desktop e tablet
- [ ] Zero regression bugs em prescrições existentes

---

## Sprint RF-04 — Indicadores Econômicos + Polimento

**Tema:** Custos por ciclo, margem, ROI, comparativo inter-safras
**Duração:** 2 semanas
**Esforço:** ~22h (Backend: 11h, Frontend: 11h)

### Backlog

| # | Tarefa | Backlog ID | Módulo | Esforço |
|---|--------|-----------|--------|---------|
| 1 | Calcular margem líquida no resumo da safra | F-01 (safras) | Backend | 2h |
| 2 | Calcular ROI por safra | F-02 | Backend | 2h |
| 3 | Adicionar `objetivo_economico` a `Safra` | A-04 | Backend | 1h |
| 4 | Endpoint comparativo inter-safras | F-03 | Backend | 3h |
| 5 | Adapter de custos lê agrícola + pecuária | F-04 | Backend | 4h |
| 6 | UI de indicadores econômicos na safra | F-01 (FE) | Frontend | 4h |
| 7 | UI comparativo inter-safras | F-03 (FE) | Frontend | 4h |
| 8 | Documentação de API completa (Swagger) | — | Backend | 2h |
| 9 | Revisão geral de testes | — | QA | 2h |
| 10 | Revisão de acessibilidade e responsividade | — | Frontend | 2h |
| 11 | Performance: queries N+1 em `obter_arvore` | — | Backend | 1h |

### Critérios de Aceite

- [ ] Resumo da safra exibe: custo/ha, receita/ha, margem líquida, ROI%
- [ ] Comparativo inter-safras: Soja 23/24 vs Soja 24/25 lado a lado
- [ ] Adapter de custos agrega operações agrícolas + eventos pecuários
- [ ] API documentada no Swagger com exemplos
- [ ] Todos os testes passando (>85% coverage geral)
- [ ] UI responsiva em tablet (uso em campo)
- [ ] Queries N+1 eliminadas na árvore hierárquica

### Definição de Pronto

- [ ] Todos os critérios de aceite das Sprints RF-01 a RF-04 atendidos
- [ ] Zero bugs abertos de prioridade Alta ou Crítica
- [ ] Documentação técnica atualizada
- [ ] Demo funcional para stakeholders

---

## Resumo de Sprints

| Sprint | Tema | Backend | Frontend | Total |
|--------|------|---------|----------|-------|
| **RF-01** | Fundação Territorial | 14h | 16h | 30h |
| **RF-02** | Dados Precisão + Histórico | 14h | 18h | 32h |
| **RF-03** | VRA por Zona + Polimento | 8h | 17h | 25h |
| **RF-04** | Indicadores + Polimento | 11h | 11h | 22h |
| **TOTAL** | | **47h** | **62h** | **109h** |

---

## Dependências entre Sprints

```
RF-01 (Fundação)
  │
  ├──→ RF-02 (Dados Precisão)  [depende de colunas de precisão + migration]
  │      │
  │      └──→ RF-03 (VRA por Zona)  [depende de SUBTALHAO + ZONA + amostras]
  │
  └──→ RF-04 (Indicadores)  [pode rodar em paralelo com RF-02]
```

**RF-01 é bloqueante** para RF-02 e RF-03.
**RF-04 pode iniciar em paralelo** após RF-01.
