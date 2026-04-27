# Contexto — Step 29: Matriz Global de Monetização Agrícola

**Data:** 2026-04-27  
**Status:** DOCUMENTADO  

---

## Objetivo

Definir a matriz global de monetização do módulo Agricultura, separando:

- `A1_PLANEJAMENTO`: operação agrícola básica.
- `PROFISSIONAL`: inteligência, simulação, comparação, dashboards avançados e automações.
- `ENTERPRISE`: integrações, multiunidade avançado, auditoria avançada e BI.

Este step é somente documental. Não houve alteração de código, regras de negócio, seeds ou testes.

---

## Premissas comerciais

### A1_PLANEJAMENTO

Deve manter o uso operacional mínimo da fazenda:

- cadastro e manutenção de safras;
- talhões e contexto produtivo básico;
- cultivos e áreas vinculadas;
- orçamento operacional da safra;
- checklist, tarefas e fenologia operacional;
- caderno de campo básico;
- leitura do cenário econômico `BASE`;
- listagem e visualização de cenários existentes;
- Production Units operacionais da safra.

### PROFISSIONAL

Deve concentrar recursos de inteligência executiva:

- criação de cenários customizados;
- duplicação de cenários;
- comparação multi-cenário;
- dashboard executivo por safra;
- drill-downs executivos;
- alertas executivos;
- margem e resumo financeiro avançado;
- simulações, previsões e recomendações automáticas;
- geração automática de tarefas a partir de inteligência agrícola;
- comparativos por Production Unit.

### ENTERPRISE

Deve concentrar recursos de escala e governança:

- BI consolidado cross-fazenda/cross-tenant;
- integrações ERP, sensores, estações, satélite e IoT;
- auditoria avançada;
- exportações regulatórias assinadas e trilhas formais;
- multiunidade avançado;
- automações em lote;
- APIs e bridges externos;
- governança de dados e relatórios corporativos.

Observação técnica: o backend atual define `PlanTier` como `BASICO`, `PROFISSIONAL` e `PREMIUM`. Para esta matriz, `ENTERPRISE` é o nome comercial esperado para o topo da oferta; há inconsistência de nomenclatura a resolver antes de implementar gates Enterprise.

---

## Matriz de Monetização

| Área funcional | Funcionalidade | Tier alvo | Gate atual observado | Status |
|---|---|---:|---|---|
| Navegação agrícola | Acesso ao módulo Agricultura | A1_PLANEJAMENTO | `ModuleGate("A1_PLANEJAMENTO")` no frontend e `require_module("A1_PLANEJAMENTO")` em vários routers | Coerente |
| Safras | Criar, listar, visualizar, editar safra | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Coerente |
| Safras | Histórico de fases, avanço de fase, encerramento/cancelamento | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Coerente |
| Talhões/contexto | Contexto de áreas rurais e talhões da safra | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Coerente |
| Cultivos | CRUD de cultivos, áreas e vínculo safra × área | A1_PLANEJAMENTO | Permissões tenant `agricola:cultivo:*`, sem tier | Coerente como operação básica |
| Production Units | Criar, listar, editar, encerrar unidades produtivas da safra | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Coerente |
| Orçamento | Orçamento da safra e itens de orçamento | A1_PLANEJAMENTO | `require_module(Modulos.AGRICOLA_PLANEJAMENTO)` | Coerente |
| Custos | Resumo de custos da safra | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Coerente para visão básica |
| Checklist | Checklist por fase, itens e templates aplicados | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Coerente |
| Tarefas | CRUD de tarefas operacionais da safra | A1_PLANEJAMENTO | `require_module(MODULE)` com `A1_PLANEJAMENTO` | Coerente |
| Fenologia | Escalas, grupos de talhões e registros fenológicos | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Coerente |
| Caderno | Timeline, entradas, fotos, visitas técnicas e EPIs | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Parcialmente coerente |
| Caderno | Exportações, downloads e assinatura de exportações | ENTERPRISE | `require_module("A1_PLANEJAMENTO")` | Gap comercial |
| Cenários econômicos | Listar cenários | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Coerente |
| Cenários econômicos | Visualizar cenário | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Coerente |
| Cenários econômicos | Editar/excluir cenário existente | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Coerente com decisão atual |
| Cenários econômicos | Recalcular cenário `BASE` | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Coerente |
| Cenários econômicos | Criar cenário customizado | PROFISSIONAL | `require_tier(PlanTier.PROFISSIONAL)` | Coerente |
| Cenários econômicos | Duplicar cenário | PROFISSIONAL | `require_tier(PlanTier.PROFISSIONAL)` | Coerente |
| Cenários econômicos | Comparativo multi-cenário | PROFISSIONAL | `require_tier(PlanTier.PROFISSIONAL)` | Coerente |
| Dashboard da safra | Dashboard executivo, KPIs, riscos, drill-downs | PROFISSIONAL | Frontend usa `useHasTier("PROFISSIONAL")`; backend depende do comparativo gated | Coerente, mas acoplado ao endpoint de comparativo |
| Dashboard financeiro legado | Resumo financeiro da safra | PROFISSIONAL | `require_tier(PlanTier.PROFISSIONAL)` | Coerente |
| Dashboard financeiro legado | Margem completa | PROFISSIONAL | `require_tier(PlanTier.PROFISSIONAL)` | Coerente |
| Dashboard agrícola global | Dashboard consolidado operacional | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Coerente se mantido como resumo operacional |
| Dashboard agrícola global | Verificação de alertas | PROFISSIONAL | `require_module("A1_PLANEJAMENTO")` | Gap comercial se forem alertas executivos |
| Análises de solo | CRUD de análises e laudos | A1_PLANEJAMENTO | `require_module("A1_PLANEJAMENTO")` | Coerente |
| Análises de solo | Recomendações, inteligência e geração de tarefas | PROFISSIONAL | `require_module("A1_PLANEJAMENTO")` | Gap comercial |
| Previsões | Previsão de produtividade | PROFISSIONAL | `require_module("A1_PLANEJAMENTO")` | Gap comercial |
| Operações | Registro e consulta de operações de campo | A1_PLANEJAMENTO | `require_module(MODULE)` com módulo operacional agrícola | Coerente como operação |
| Monitoramento MIP | Catálogo, registros e diagnóstico avulso | PROFISSIONAL | `require_module("A2_CAMPO")` | Gap de tier se diagnóstico for inteligência |
| Agrônomo IA/RAT | Chat agronômico, conversas e RAT | PROFISSIONAL | `require_module("A2_CAMPO")` | Gap de tier |
| Climático | Histórico, chuva acumulada e sincronização | A1_PLANEJAMENTO para consulta básica; ENTERPRISE para integração/sync | `require_module("A1_PLANEJAMENTO")` | Gap em sincronização |
| NDVI básico | Série temporal e sincronização NDVI | PROFISSIONAL | `require_module("A4_PRECISAO")` | Gap de tier ou módulo premium |
| NDVI avançado | NDVI avançado, meteorologia, irrigação | ENTERPRISE | Sem gate explícito nos routers avançados observados | Gap crítico |
| Amostragem solo avançada | Amostras, mapas de fertilidade, prescrições VRA | ENTERPRISE | Sem gate explícito nos routers observados | Gap crítico |
| Prescrições VRA | Criar/listar/visualizar prescrições | ENTERPRISE | `require_module("A4_PRECISAO")` | Gap de tier se vendido como Enterprise |
| Romaneios | Registro e consulta de romaneios de colheita | A1_PLANEJAMENTO ou A5_COLHEITA | `require_module("A5_COLHEITA")` | Coerente como módulo adicional |
| Beneficiamento | Beneficiamento, armazenagem, venda e rendimento | A5_COLHEITA; relatórios avançados em PROFISSIONAL | `require_module("A5_COLHEITA")` | Gap para relatórios avançados |
| Rastreabilidade | Lotes, cadeia e certificações | ENTERPRISE para auditoria/certificação; A5 para operação | `require_module("A5_COLHEITA")` | Gap de governança |
| Relatórios agrícolas | Summary, talhões, talhão individual, profitability | PROFISSIONAL ou ENTERPRISE para BI | Frontend chama `/reports/agricola/*`; gate não validado neste levantamento | Requer revisão |
| Templates agrícolas | Templates de fases/operações e aplicação | PROFISSIONAL para automação; ENTERPRISE para governança global | Routers sem gate explícito observado | Gap crítico |

---

## Regras de Corte por Tier

### A1_PLANEJAMENTO

Inclui tudo que permite operar uma safra sem camada executiva:

- cadastrar e manter safras;
- registrar operações, tarefas, checklist, fenologia e caderno básico;
- consultar orçamento e custos básicos;
- organizar cultivos, áreas e Production Units;
- listar e visualizar cenários econômicos;
- recalcular o cenário `BASE`.

Não deve incluir:

- criação de cenários alternativos;
- duplicação de cenários;
- comparativos avançados;
- dashboards executivos;
- alertas executivos;
- automações derivadas de inteligência;
- BI, integrações e auditoria avançada.

### PROFISSIONAL

Inclui funcionalidades que transformam dados operacionais em decisão:

- cenários customizados;
- comparativos econômicos;
- dashboard executivo da safra;
- resumo financeiro avançado e margem;
- drill-downs e alertas executivos;
- previsões de produtividade;
- recomendações agronômicas;
- geração automática de tarefas;
- relatórios analíticos e rentabilidade.

### ENTERPRISE

Inclui capacidades que aumentam escala, governança ou dependem de integração:

- BI consolidado por múltiplas fazendas/unidades;
- integrações ERP e APIs externas;
- sincronizações satélite/IoT/estações;
- NDVI avançado, irrigação e meteorologia integrada;
- VRA, mapas de fertilidade e amostragem avançada;
- auditoria de rastreabilidade e certificações;
- exportações assinadas e evidências regulatórias;
- templates corporativos e automações globais.

---

## Gates Já Coerentes

- `POST /safras/{safra_id}/cenarios` exige `PROFISSIONAL`.
- `POST /safras/{safra_id}/cenarios/{cenario_id}/duplicar` exige `PROFISSIONAL`.
- `GET /safras/{safra_id}/cenarios/comparativo` exige `PROFISSIONAL`.
- `GET /agricola/dashboard/safras/{safra_id}/resumo-financeiro` exige `PROFISSIONAL`.
- `GET /agricola/dashboard/safras/{safra_id}/margem` exige `PROFISSIONAL`.
- Frontend do Dashboard Executivo da safra usa `useHasTier("PROFISSIONAL")` antes de carregar queries premium.
- Frontend do Comparativo de Cenários usa `useHasTier("PROFISSIONAL")` antes de carregar o comparativo.
- Frontend de Cenários mantém listagem em A1 e reserva Novo Cenário, Duplicar e Comparar para `PROFISSIONAL`.

---

## Inconsistências Identificadas

### 1. `ENTERPRISE` não existe como `PlanTier`

O código atual usa:

- `BASICO`
- `PROFISSIONAL`
- `PREMIUM`

A matriz comercial pede `ENTERPRISE`. Antes de implementar gates Enterprise, é necessário decidir se:

- `PREMIUM` será renomeado para `ENTERPRISE`;
- `ENTERPRISE` será alias comercial de `PREMIUM`;
- ou haverá novo tier técnico.

### 2. Recursos de inteligência ainda estão apenas em A1

Endpoints abaixo parecem premium pela matriz, mas estão só com `A1_PLANEJAMENTO`:

- `GET /agricola/analises-solo/{id}/recomendacoes`
- `GET /agricola/analises-solo/{id}/inteligencia`
- `POST /agricola/analises-solo/{id}/gerar-tarefas`
- `POST /agricola/previsoes/gerar`
- `GET /agricola/previsoes`
- `POST /agricola/dashboard/verificar-alertas`

### 3. Recursos avançados sem gate explícito observado

Routers de agricultura avançada observados sem `require_module`/`require_tier` explícito no próprio arquivo:

- `agricola/amostragem_solo/routers/amostras.py`
- `agricola/amostragem_solo/routers/mapas_fertilidade.py`
- `agricola/amostragem_solo/routers/prescricoes_vra.py`
- `agricola/ndvi_avancado/routers/ndvi.py`
- `agricola/ndvi_avancado/routers/meteorologia.py`
- `agricola/ndvi_avancado/routers/irrigacao.py`
- `agricola/templates/router.py`

Pode haver gate no include de router ou camada superior, mas isso deve ser validado antes de considerar seguro.

### 4. Módulos agrícolas A2/A4/A5 não substituem tier

O código usa módulos vendáveis como:

- `A2_CAMPO`
- `A4_PRECISAO`
- `A5_COLHEITA`

Eles resolvem contratação de módulos, mas não expressam profundidade de plano. Para monetização por tier, recursos como IA, diagnóstico, NDVI avançado, VRA, BI e auditoria precisam combinar:

- módulo contratado;
- tier mínimo.

### 5. Exportação e assinatura do caderno podem ser Enterprise

O caderno básico é operacional A1. Porém exportações, downloads formais e assinatura de exportações têm caráter de conformidade/auditoria. Pela matriz, devem ser avaliados para `ENTERPRISE`.

---

## Recomendação de Implementação Futura

Ordem sugerida para implementação posterior, sem alterar este step:

1. Resolver nomenclatura `PREMIUM` versus `ENTERPRISE`.
2. Adicionar testes de contrato para `require_tier` no topo da oferta.
3. Aplicar `PROFISSIONAL` em inteligência agrícola já existente que hoje está em A1.
4. Validar routers avançados sem gate explícito.
5. Aplicar `ENTERPRISE` em integrações, BI, auditoria e automações globais.
6. Atualizar frontend para não disparar queries bloqueadas, espelhando os gates backend.

---

## Critérios de Aceite

Este step atende ao objetivo porque:

- lista as principais funcionalidades existentes de Agricultura;
- define tier alvo para cada grupo funcional;
- preserva A1 como operação básica;
- concentra simulação, comparação, dashboards avançados e automações em `PROFISSIONAL`;
- concentra integrações, multiunidade avançado, auditoria e BI em `ENTERPRISE`;
- identifica inconsistências com gates já implementados;
- não altera código de produto.
