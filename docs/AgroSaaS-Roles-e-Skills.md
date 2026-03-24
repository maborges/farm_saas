# AgroSaaS — Roles de Desenvolvimento & Skills Especializadas por Módulo
> Documento de organização do time de engenharia.
> Cada role tem responsabilidade clara. Cada skill é um conjunto de conhecimento especializado
> necessário para construir e manter aquela parte do sistema.

---

## Parte 1 — Roles de Desenvolvimento

### Hierarquia do Time

```
CTO / Arquiteto-Chefe
  │
  ├── Tech Lead Plataforma (CORE)
  │     ├── Engenheiro de Plataforma Sr (auth, multitenancy, assinaturas)
  │     └── Engenheiro DevOps / Infra Sr
  │
  ├── Tech Lead Agrícola
  │     ├── Engenheiro Backend Agrícola Sr
  │     ├── Engenheiro Full Stack Agrícola
  │     └── Especialista Geoespacial / Satélite
  │
  ├── Tech Lead Pecuário
  │     ├── Engenheiro Backend Pecuário Sr
  │     └── Engenheiro Full Stack Pecuário
  │
  ├── Tech Lead Financeiro
  │     ├── Engenheiro Fiscal / NF-e Sr
  │     └── Engenheiro Full Stack Financeiro
  │
  ├── Tech Lead Operacional & Pessoas
  │     └── Engenheiro Full Stack Operacional
  │
  ├── Tech Lead Inteligência Artificial
  │     ├── Engenheiro de ML / LLM Sr
  │     └── Engenheiro de Dados / MLOps
  │
  ├── Tech Lead Mobile
  │     └── Engenheiro React Native Sr
  │
  └── Tech Lead QA & Segurança
        ├── Engenheiro de Testes Sr
        └── Engenheiro de Segurança / DevSecOps
```

---

### Role 01 — CTO / Arquiteto-Chefe

**Responsabilidade:** Visão técnica global, decisões de arquitetura não reversíveis, governança da stack, contratação técnica sênior.

**O que decide:** Mudanças de stack, novos microsserviços, breaking changes de API, estratégia de segurança e multitenancy.

**Skills obrigatórias:** Todas as skills de plataforma. Conhecimento profundo de PostgreSQL, K3s, Keycloak. Experiência com produtos SaaS multi-tenant.

---

### Role 02 — Tech Lead Plataforma (CORE)

**Responsabilidade:** Módulo CORE — identidade global, contas, assinaturas, workareas, roles, multitenancy, feature flags, onboarding.

**Entrega:** `api-core` completo, sistema de assinatura, controle de acesso RBAC, JWT com claims customizados, painel do financeiro interno.

**Skills obrigatórias:**
- SKILL-CORE-01: Identidade Global e Multitenancy
- SKILL-CORE-02: Sistema de Assinatura e Onboarding
- SKILL-CORE-03: RBAC e Controle de Acesso
- SKILL-INFRA-01: Keycloak e JWT

---

### Role 03 — Engenheiro de Plataforma Sr

**Responsabilidade:** Implementação do `api-core`, schemas de banco do CORE, RLS policies, Keycloak realms, seeds de roles padrão.

**Skills obrigatórias:**
- SKILL-CORE-01, SKILL-CORE-02, SKILL-CORE-03
- SKILL-DB-01: PostgreSQL e RLS
- SKILL-INFRA-01: Keycloak

---

### Role 04 — Engenheiro DevOps / Infra Sr

**Responsabilidade:** K3s, Helm charts, CI/CD (Gitea Actions), Harbor, Ansible, Vault, observabilidade LGTM, redes, backups.

**Entrega:** Cluster K3s funcional, pipeline completo deploy→staging→prod, Grafana dashboards, alertas de produção.

**Skills obrigatórias:**
- SKILL-INFRA-02: K3s e Kubernetes
- SKILL-INFRA-03: CI/CD e GitOps
- SKILL-INFRA-04: Observabilidade LGTM
- SKILL-INFRA-05: Segurança e Secrets

---

### Role 05 — Tech Lead Agrícola

**Responsabilidade:** Todos os submódulos agrícolas (A1-A5), integração Sentinel-2, dados climáticos, mapas de prescrição.

**Entrega:** `api-agricola` completo — talhões, safras, caderno de campo, NDVI, clima, custo por saca.

**Skills obrigatórias:**
- SKILL-AGRO-01 a SKILL-AGRO-06 (todas)
- SKILL-GEO-01: PostGIS e Geoespacial
- SKILL-IA-02: Processamento Sentinel-2 / NDVI

---

### Role 06 — Engenheiro Backend Agrícola Sr

**Responsabilidade:** Backend do módulo agrícola — services, routers, migrations, tasks Celery, integrações externas.

**Skills obrigatórias:**
- SKILL-AGRO-01, SKILL-AGRO-02, SKILL-AGRO-03
- SKILL-DB-02: TimescaleDB (dados climáticos e NDVI)
- SKILL-GEO-01: PostGIS

---

### Role 07 — Engenheiro Full Stack Agrícola

**Responsabilidade:** Frontend do módulo agrícola — mapas MapLibre, gráficos NDVI, formulários de safra, caderno de campo.

**Skills obrigatórias:**
- SKILL-AGRO-01, SKILL-AGRO-02
- SKILL-FRONTEND-02: MapLibre e Geoespacial
- SKILL-FRONTEND-01: Next.js RSC e TanStack Query

---

### Role 08 — Especialista Geoespacial / Satélite

**Responsabilidade:** Integração Sentinel-2 / Copernicus, processamento NDVI com rasterio, mapas de variabilidade, mapa de prescrição VRA.

**Skills obrigatórias:**
- SKILL-GEO-01: PostGIS e Geoespacial
- SKILL-GEO-02: Sentinel-2 e Processamento Raster
- SKILL-IA-02: NDVI e Análise de Vegetação

---

### Role 09 — Tech Lead Pecuário

**Responsabilidade:** Todos os submódulos pecuários (P1-P6), SISBOV, rastreabilidade bovina.

**Entrega:** `api-pecuaria` completo — rebanho, pesagens, reprodução, sanidade, leite, confinamento.

**Skills obrigatórias:**
- SKILL-PEC-01 a SKILL-PEC-06 (todas)
- SKILL-DB-01: PostgreSQL e TimescaleDB (pesagens)

---

### Role 10 — Engenheiro Backend Pecuário Sr

**Responsabilidade:** Services de rebanho, pesagens, reprodução, sanidade. Algoritmos GMD, taxa de prenhez, eficiência reprodutiva.

**Skills obrigatórias:**
- SKILL-PEC-01, SKILL-PEC-02, SKILL-PEC-03
- SKILL-DB-01: PostgreSQL
- SKILL-DB-02: TimescaleDB (series temporais de pesagem)

---

### Role 11 — Engenheiro Full Stack Pecuário

**Responsabilidade:** Frontend pecuário — AG Grid de rebanho, formulários de manejo, timeline reprodutiva, dashboard de lote.

**Skills obrigatórias:**
- SKILL-PEC-01, SKILL-PEC-02
- SKILL-FRONTEND-01: Next.js RSC e TanStack Query
- SKILL-FRONTEND-03: AG Grid e visualizações

---

### Role 12 — Tech Lead Financeiro

**Responsabilidade:** Módulos financeiros (F1-F4) — contas, custos, NF-e/SEFAZ, contratos, cotações.

**Entrega:** `api-financeiro` completo — fluxo de caixa, DRE, NF-e via SEFAZ, LCDPR, integração B3.

**Skills obrigatórias:**
- SKILL-FIN-01 a SKILL-FIN-04 (todas)
- SKILL-FIS-01: Fiscal e NF-e Brasil

---

### Role 13 — Engenheiro Fiscal / NF-e Sr

**Responsabilidade:** Integração SEFAZ, emissão NF-e produtor rural, LCDPR, Manifesto de documentos fiscais. Conhecimento de legislação fiscal rural brasileira.

**Skills obrigatórias:**
- SKILL-FIS-01: Fiscal e NF-e Brasil
- SKILL-FIN-03: Módulo Fiscal
- SKILL-BACKEND-01: Celery Tasks (NF-e é assíncrona)

---

### Role 14 — Engenheiro Full Stack Financeiro

**Responsabilidade:** Frontend financeiro — fluxo de caixa, DRE, lançamentos, conciliação, relatórios.

**Skills obrigatórias:**
- SKILL-FIN-01, SKILL-FIN-02
- SKILL-FRONTEND-01: Next.js RSC e TanStack Query
- SKILL-FRONTEND-03: AG Grid e Recharts

---

### Role 15 — Tech Lead Operacional & Pessoas

**Responsabilidade:** Módulos operacionais (O1-O4) e RH (RH1-RH2) — máquinas, estoque, compras, patrimônio, colaboradores, SST.

**Entrega:** `api-operacional` completo.

**Skills obrigatórias:**
- SKILL-OPS-01 a SKILL-OPS-04
- SKILL-RH-01, SKILL-RH-02

---

### Role 16 — Tech Lead Inteligência Artificial

**Responsabilidade:** Módulo IA (`api-ia`) — Agrônomo Virtual LLM, diagnóstico de pragas YOLO, previsão de produtividade ML, RAG pipeline.

**Entrega:** LLM self-hosted funcional, modelos YOLO treinados, pipeline XGBoost de produtividade, RAG com base EMBRAPA.

**Skills obrigatórias:**
- SKILL-IA-01: LLM e RAG com Ollama
- SKILL-IA-02: Computer Vision e YOLO
- SKILL-IA-03: Machine Learning (XGBoost, Prophet)
- SKILL-IA-04: MLOps e MLflow

---

### Role 17 — Engenheiro de ML / LLM Sr

**Responsabilidade:** Desenvolvimento dos modelos, treinamento, avaliação, versionamento no MLflow.

**Skills obrigatórias:**
- SKILL-IA-01, SKILL-IA-02, SKILL-IA-03, SKILL-IA-04

---

### Role 18 — Engenheiro de Dados / MLOps

**Responsabilidade:** Pipelines de dados para treinamento, feature engineering, monitoramento de drift de modelos em produção.

**Skills obrigatórias:**
- SKILL-IA-03: Machine Learning
- SKILL-IA-04: MLOps e MLflow
- SKILL-DB-02: TimescaleDB (dados históricos para treino)

---

### Role 19 — Tech Lead Mobile

**Responsabilidade:** App React Native / Expo — operador de campo, offline-first, sincronização, câmera para diagnóstico.

**Entrega:** App mobile funcional, offline completo, sincronização robusta, diagnóstico de pragas por câmera.

**Skills obrigatórias:**
- SKILL-MOBILE-01: React Native e Expo
- SKILL-MOBILE-02: Offline-First e WatermelonDB
- SKILL-MOBILE-03: Câmera e GPS

---

### Role 20 — Tech Lead QA & Segurança

**Responsabilidade:** Cobertura de testes, testes de segurança, tenant isolation validation, OWASP, pentesting periódico.

**Entrega:** Suite de testes completa, relatórios de cobertura, testes de penetração, checklists de segurança.

**Skills obrigatórias:**
- SKILL-QA-01: Testes de Backend (pytest)
- SKILL-QA-02: Testes de Frontend (Vitest + Playwright)
- SKILL-SEC-01: Segurança e Multitenancy
- SKILL-SEC-02: OWASP e Vulnerabilidades

---

## Parte 2 — Skills Especializadas

> Cada skill é um conjunto de conhecimento autônomo que pode ser atribuído individualmente.
> Um engenheiro pode ter múltiplas skills. Uma skill pode ser exigida por múltiplos roles.

---

### 🔷 CORE — Plataforma e Identidade

---

#### SKILL-CORE-01: Identidade Global e Multitenancy

**Escopo:** Arquitetura de identidade que separa `platform_users` (global) de `accounts` (tenant). Entender como um usuário pode pertencer a múltiplas contas com papéis diferentes.

**Conhecimentos necessários:**
- Modelo de dados: `platform_users`, `accounts`, `account_members`
- Busca por e-mail ao convidar: fluxo de usuário existente vs novo
- Seletor de conta no frontend (alternância sem novo login)
- JWT com `account_id` ativo e `contas_adicionais[]`
- Keycloak: realms, clients, user federation

**Entregáveis típicos:**
- Endpoint `POST /plataforma/usuarios/verificar-email`
- Endpoint `POST /accounts/{id}/membros/convidar`
- Componente `AccountSwitcher` no header do sistema
- Claim customizado no Keycloak: `account_id`, `tipo_membro`

---

#### SKILL-CORE-02: Sistema de Assinatura e Onboarding

**Escopo:** Ciclo de vida completo da assinatura — criação, comprovação financeira, ativação, suspensão, renovação. Wizard de onboarding pós-ativação.

**Conhecimentos necessários:**
- Modelo: `accounts`, `subscriptions`, `subscription_modules`
- Estados de conta: `pendente_pagamento → ativo → suspenso → cancelado`
- Fluxo de aprovação do financeiro interno
- Wizard pós-ativação: propriedades → perfis → usuários
- Notificações por evento (convite, ativação, suspensão)
- Feature gate em runtime via `subscription_modules`

**Entregáveis típicos:**
- Página `/assinar` (cadastro + escolha de plano)
- Painel do financeiro AgroSaaS (aprovação de comprovantes)
- Wizard `/onboarding` com 3 etapas
- Middleware de bloqueio para conta suspensa

---

#### SKILL-CORE-03: RBAC e Controle de Acesso

**Escopo:** Perfis de acesso (roles system + custom), permissões por módulo, associação usuário × workarea × role.

**Conhecimentos necessários:**
- Modelo: `roles`, `workareas`, `user_workarea_roles`
- Perfis padrão do sistema (is_system = true, não editável)
- Criação de perfis customizados pelo assinante
- Estrutura JSONB de permissões: `{modulo: [ler, escrever, aprovar]}`
- Acesso temporal com `valido_ate`
- `require_module()` e `require_role()` no FastAPI
- Verificação de acesso por workarea no BaseService

**Entregáveis típicos:**
- Tabelas `roles` e `user_workarea_roles` com migrations
- Endpoints: `GET/POST /accounts/{id}/roles`
- Endpoint `POST /accounts/{id}/usuarios/{uid}/associar`
- Claim `permissoes` no JWT
- Dependência `require_role()` no FastAPI

---

### 🌿 AGRÍCOLA

---

#### SKILL-AGRO-01: Planejamento de Safra (A1)

**Escopo:** Módulo `AGRICOLA_A1` — cadastro e planejamento de safras por talhão e ano.

**Conhecimentos necessários:**
- Entidades: `talhoes`, `safras`, `cultivares`
- Calendário agrícola e janelas de plantio (base ZARC/MAPA)
- Cálculo de data prevista de colheita via GDU do cultivar
- Rotação de culturas: histórico por talhão, sugestão de sequência
- Orçamento de safra: custo previsto por categoria
- Transições de status: `PLANEJADA → EM_PREPARO → PLANTADA → EM_CRESCIMENTO → COLHIDA`

**Entregáveis típicos:**
- Migration: tabelas `talhoes`, `safras`, `cultivares`
- `SafraService.criar()` com cálculo de datas
- Endpoint `PATCH /safras/{id}/status`
- Tela de planejamento de safra com calendário visual

---

#### SKILL-AGRO-02: Manejo de Agricultura / Caderno de Campo (A2)

**Escopo:** Módulo `AGRICOLA_A2` — registro de todas as operações realizadas no talhão ao longo do ciclo.

**Conhecimentos necessários:**
- Entidade: `operacoes_agricolas`, `insumos_operacao`
- Tipos de operação: preparo, plantio, adubação, defensivo, irrigação, colheita
- Integração com estoque: baixa automática de insumos ao registrar operação
- Carência de defensivos: `data_reentrada = data_operacao + carencia_dias`
- Geolocalização de operações (GPS do app mobile)
- Condições climáticas no momento (integração Open-Meteo)
- Receituário agronômico: geração de PDF ao planejar aplicação de defensivo

**Entregáveis típicos:**
- `OperacaoService.criar()` com baixa de estoque via httpx
- Endpoint `GET /operacoes/carencias-ativas`
- AG Grid de caderno de campo com filtros por tipo e período
- Formulário de operação com insumos dinâmicos

---

#### SKILL-AGRO-03: Controle de Insumos Agrícolas (A3)

**Escopo:** Módulo `AGRICOLA_A3` — estoque específico de insumos agrícolas (sementes, fertilizantes, defensivos).

**Conhecimentos necessários:**
- Rastreabilidade de lote: `lote_insumo` vinculado à operação
- Validade de defensivos: alerta quando próximo ao vencimento
- Registro MAPA: validação de produto registrado para cultura/praga
- Integração com módulo de compras (O3)
- Custo médio ponderado por insumo

**Entregáveis típicos:**
- Tela de estoque agrícola com validade e lotes
- Alerta de defensivos próximos ao vencimento
- Busca de registro MAPA por praga + cultura

---

#### SKILL-AGRO-04: Agricultura de Precisão (A4)

**Escopo:** Módulo `AGRICOLA_A4` — análise de solo, zonas de manejo, mapas de prescrição VRA, integração com terminais ISOBUS.

**Conhecimentos necessários:**
- Análise de solo: importação de laudos, recomendação de calagem/gessagem
- Zonas de manejo: clustering por NDVI histórico + fertilidade de solo
- Mapa de prescrição: geração de shapefile/geotiff para VRA
- Integração com colheitadeiras (John Deere Operations Center, CNH AFS, AGCO Fuse)
- Exportação para formato compatível com terminal ISOBUS

**Entregáveis típicos:**
- `AnaliseSoloService` com interpretação automática via LLM
- Mapa de zonas de variabilidade (GeoJSON para MapLibre)
- Geração de shapefile de prescrição

---

#### SKILL-AGRO-05: Colheita e Romaneio (A5)

**Escopo:** Módulo `AGRICOLA_A5` — registro de romaneios, cálculo de produtividade real, destino da produção.

**Conhecimentos necessários:**
- Entidade: `romaneios_colheita`
- Cálculo de descontos ABIOVE/ANEC: umidade, impureza, avariados
- Conversão para sacas 60kg
- Produtividade real: `sc/ha = sacas_totais / area_plantada`
- Destino: armazém próprio, cooperativa, trading, venda direta
- Integração financeira: romaneio → lançamento de receita automático

**Entregáveis típicos:**
- `RomaneioService.fechar_safra()` com cálculo agregado
- Tela de romaneio com comparativo previsto vs real por talhão

---

#### SKILL-AGRO-06: Inteligência Climática e NDVI

**Escopo:** Integração com Open-Meteo (histórico + previsão) e Sentinel-2 (NDVI), cálculo de GDU, alertas agronômicos.

**Conhecimentos necessários:**
- Open-Meteo API: archive + forecast, sem API key
- Cálculo de GDU por cultura: `max(0, (Tmax+Tmin)/2 - Tbase)`
- Estimativa de estágio fenológico via GDU acumulado
- Balanço hídrico: precipitação - ET0 (Penman-Monteith)
- Janelas de aplicação: vento < 15km/h + sem chuva prevista + temperatura adequada
- Copernicus Data Space: OAuth2, download S2L2A, bandas B04/B08
- Rasterio + numpy: processamento NDVI, máscara por polígono PostGIS

**Entregáveis típicos:**
- Task Celery `sincronizar_clima_todos_talhoes` (diário às 05:00)
- Task Celery `processar_ndvi_todos_talhoes` (diário às 06:00)
- `ClimaticoService.alerta_janela_aplicacao()`
- Gráfico de NDVI temporal com Recharts

---

### 🐄 PECUÁRIO

---

#### SKILL-PEC-01: Gestão de Rebanho Bovino (P1)

**Escopo:** Módulo `PECUARIA_P1` — cadastro individual, lotes, genealogia, movimentações.

**Conhecimentos necessários:**
- Entidade: `animais` com auto-referência genealogia (mae_id, pai_id)
- Categorias: bezerro, novilho, novilha, vaca, touro, boi
- Brinco visual, brinco eletrônico, SISBOV
- Lotes: agrupamento operacional de animais
- Movimentações: entrada, saída, transferência entre fazendas
- Integração SISBOV: registro e consulta de animais rastreados

**Entregáveis típicos:**
- Migration: tabelas `animais`, `lotes`, `movimentacoes_animais`
- AG Grid de rebanho com 100k+ linhas, filtros avançados
- Formulário de cadastro com validação de SISBOV
- Endpoint `GET /animais?busca=&categoria=&lote_id=`

---

#### SKILL-PEC-02: Pesagem e Desempenho (P1)

**Escopo:** Registro de pesagens, cálculo de GMD, análise de desempenho por lote.

**Conhecimentos necessários:**
- TimescaleDB: hypertable `pesagens` particionada por mês
- Cálculo GMD: `(peso_final - peso_inicial) / dias`
- Continuous aggregate: `gmd_mensal_por_lote`
- Tipos: nascimento, desmama, rotina, embarque, abate
- Alerta de GMD abaixo do mínimo configurado
- Projeção de peso futuro via Prophet (series temporais)

**Entregáveis típicos:**
- `PesagemService.registrar()` com cálculo automático de GMD
- Gráfico de evolução de peso por animal/lote
- Dashboard de GMD médio vs meta por lote
- Alerta `GMD_BAIXO` via alertas_agronomicos

---

#### SKILL-PEC-03: Reprodução Animal (P2)

**Escopo:** Módulo `PECUARIA_P2` — IATF, monta natural, diagnóstico de gestação, partos, índices reprodutivos.

**Conhecimentos necessários:**
- Entidade: `reproducao_eventos` com tipos: CIO, IA, IATF, MONTA, DIAGNOSTICO, PARTO, ABORTO
- Protocolos IATF: fases e hormônios (D0, D8, D11 aplicação)
- Taxa de prenhez = vacas prenhes / vacas expostas
- Intervalo entre partos, taxa de natalidade
- Agenda de diagnóstico: 30-35 dias após IA/IATF
- Previsão de partos: `data_prevista = data_iatf + 283 dias`

**Entregáveis típicos:**
- `ReproducaoService.aplicar_protocolo_iatf_lote()`
- Agenda reprodutiva com alertas de diagnóstico pendente
- Dashboard com taxa de prenhez, IEP, natalidade
- Calendário de partos previstos

---

#### SKILL-PEC-04: Sanidade Animal (P3)

**Escopo:** Módulo `PECUARIA_P3` — vacinações, vermifugações, tratamentos, protocolos sanitários.

**Conhecimentos necessários:**
- Entidade: `eventos_sanitarios` — vacina, vermifugação, tratamento, exame
- Calendário sanitário oficial: aftosa, brucelose, raiva, carbúnculo
- Controle de estoque de vacinas e medicamentos
- Carência de medicamentos antes do abate
- Notificação de rebanho: obrigações legais MAPA
- Geração de atestado sanitário em PDF

**Entregáveis típicos:**
- `SanidadeService.vacinacao_em_lote()`
- Calendário sanitário com alertas de vencimento
- Relatório sanitário para exportação/certificação

---

#### SKILL-PEC-05: Produção de Leite (P4)

**Escopo:** Módulo `PECUARIA_P4` — registro de produção diária, CCS, gordura, proteína, pagamento por qualidade.

**Conhecimentos necessários:**
- TimescaleDB: hypertable `producao_leite` por animal/dia
- Índices: produção/dia, pico de lactação, persistência
- CCS (Contagem de Células Somáticas): alerta de mastite
- Pagamento por qualidade: tabelas de desconto/bonificação por laticínio
- Lactação: número, dias em lactação, curva de produção

**Entregáveis típicos:**
- Registro diário de produção (individual ou por lote)
- Curva de lactação por animal com Recharts
- Dashboard de CCS médio com alerta de limiar

---

#### SKILL-PEC-06: Confinamento e Feedlot (P5) / Avicultura e Suinocultura (P6)

**Escopo:** Módulo `PECUARIA_P5` — gestão de confinamento, dieta, consumo de ração, custo por arroba. Módulo `PECUARIA_P6` — lotes de aves/suínos, conversão alimentar, mortalidade, ciclos de produção.

**Conhecimentos necessários (P5):**
- Entidade: `lotes_confinamento`, `dietas`, `arracoamentos`
- Custo por arroba @ = custo total / (arrobas produzidas)
- Consumo de matéria seca, conversão alimentar: `kg ração / kg ganho`
- GPD (ganho de peso diário) em confinamento
- Margem de confinamento vs compra a pasto

**Conhecimentos necessários (P6):**
- Entidade: `lotes_avicola`, `ciclos_avicola`
- FCR (Feed Conversion Ratio): `kg ração consumida / kg ganho`
- Densidade, mortalidade acumulada, uniformidade de lote
- Custo de produção por Kg vivo produzido

---

### 💰 FINANCEIRO

---

#### SKILL-FIN-01: Gestão Financeira Operacional (F1)

**Escopo:** Módulo `FINANCEIRO_F1` — contas a pagar e receber, fluxo de caixa, livro caixa.

**Conhecimentos necessários:**
- Entidade: `lancamentos_financeiros` com centro de custo
- Centro de custo: safra, lote, máquina, geral
- Fluxo de caixa projetado (90 dias): realizado + previstos
- Conciliação bancária
- Categorias financeiras hierárquicas (plano de contas rural)
- Integração automática: romaneio → receita, operação agrícola → despesa

**Entregáveis típicos:**
- Dashboard fluxo de caixa com Recharts (real vs projetado)
- AG Grid de lançamentos com filtros por categoria/período/centro de custo
- Endpoint `GET /fluxo-caixa?inicio=&fim=&fazenda_id=`

---

#### SKILL-FIN-02: Custos e DRE (F2)

**Escopo:** Módulo `FINANCEIRO_F2` — custo de produção por safra/lote, DRE por atividade, custo por saca/arroba.

**Conhecimentos necessários:**
- DRE agropecuária: Receita Bruta, Deduções, Custo de Produção, Margem Bruta
- Custo por saca = custo_total_ha / produtividade_sc_ha
- Ponto de equilíbrio: custo_realizado_ha / cotação_atual
- Rateio de custos indiretos (máquinas, RH) por atividade
- Benchmark regional com dados CONAB/SENAR

**Entregáveis típicos:**
- `CustoSacaService.calcular_custo_atual(safra_id)`
- Simulador de cenários de preço
- Tela DRE com comparativo safras anteriores

---

#### SKILL-FIN-03: Fiscal e NF-e (F3)

**Escopo:** Módulo `FINANCEIRO_F3` — emissão de NF-e produtor rural via SEFAZ, LCDPR, Manifesto eletrônico.

**Conhecimentos necessários:**
- NF-e produtor rural: CST, CFOP agropecuário, NCM de produtos agrícolas e animais
- Integração SEFAZ: endpoint de autorização, contingência offline
- Assinatura digital: certificado A1/A3
- Celery task assíncrona: emissão com retry exponencial
- LCDPR: Livro Caixa Digital do Produtor Rural (IN RFB 1.848/2018)
- Manifesto Eletrônico de Documentos Fiscais (MDF-e)

**Entregáveis típicos:**
- Task `emitir_nfe` com 5 retentativas e backoff
- Painel de NF-es com status: rascunho, processando, autorizada, erro
- Exportação LCDPR em formato Receita Federal

---

#### SKILL-FIN-04: Contratos e Comercial (F4)

**Escopo:** Módulo `FINANCEIRO_F4` — contratos de venda de commodities, travas, cotações em tempo real.

**Conhecimentos necessários:**
- Tipos de contrato: disponível, a termo (forward), opções
- Cotações B3: soja, milho, boi gordo, algodão — via API ou scraping
- CBOT (Chicago): câmbio aplicado, base local
- Preço de venda médio vs ponto de equilíbrio
- Percentual comercializado da safra

**Entregáveis típicos:**
- Widget de cotações em tempo real no dashboard
- `CotacaoService` com cache Redis TTL 1h
- Tela de contratos com mark-to-market em tempo real

---

### ⚙️ OPERACIONAL

---

#### SKILL-OPS-01: Máquinas e Frotas (O1)

**Escopo:** Módulo `OPERACIONAL_O1` — cadastro de máquinas, manutenções, abastecimento, custo por hora.

**Conhecimentos necessários:**
- Entidade: `maquinas`, `manutencoes`, `abastecimentos`
- Plano de manutenção: por horas/km ou por data (preventiva)
- Alerta de manutenção iminente: 50h antes do vencimento
- Custo horário: (depreciação + combustível + manutenção) / horas trabalhadas
- Integração com operações agrícolas: qual máquina fez qual operação

**Entregáveis típicos:**
- Dashboard de frota com status de cada máquina
- Alerta de manutenção preventiva próxima
- Cálculo automático de custo/hora por máquina

---

#### SKILL-OPS-02: Estoque e Almoxarifado (O2)

**Escopo:** Módulo `OPERACIONAL_O2` — estoque geral (inclui insumos agrícolas e veterinários, peças, combustível).

**Conhecimentos necessários:**
- Entradas e saídas com lote e validade
- Custo médio ponderado
- Inventário: contagem periódica com ajuste de inventário
- Estoque mínimo com alerta de reposição
- Integração com operações (baixa automática) e compras

---

#### SKILL-OPS-03: Compras (O3)

**Escopo:** Módulo `OPERACIONAL_O3` — pedidos de compra, cotações de fornecedores, aprovação.

**Conhecimentos necessários:**
- Fluxo: requisição → cotação → pedido → recebimento → baixa estoque
- Comparativo de cotações por produto/fornecedor
- Integração com financeiro: pedido aprovado → conta a pagar
- Histórico de preços por fornecedor e produto

---

#### SKILL-OPS-04: Infraestrutura e Patrimônio (O4)

**Escopo:** Módulo `OPERACIONAL_O4` — benfeitorias, silos, açudes, cercas, patrimônio imobilizado.

**Conhecimentos necessários:**
- Cadastro georreferenciado de infraestrutura (PostGIS Point)
- Depreciação de bens do ativo imobilizado
- Manutenções de infraestrutura (silos, galpões, sistemas de irrigação)
- Relatório de patrimônio para fins contábeis

---

### 👥 PESSOAS

---

#### SKILL-RH-01: Gestão de Colaboradores (RH1)

**Escopo:** Módulo `PESSOAS_RH1` — cadastro de funcionários, contratos, ponto, férias, folha simples.

**Conhecimentos necessários:**
- Entidade: `colaboradores`, `contratos_trabalho`, `registros_ponto`
- Tipos de vínculo: CLT, temporário, diarista, empreiteiro
- Registro de ponto: entrada, saída, intervalos
- Cálculo simples de horas extras e banco de horas
- Férias: controle de período aquisitivo e gozo

**Entregáveis típicos:**
- App mobile para registro de ponto com GPS
- Relatório mensal de horas por colaborador

---

#### SKILL-RH-02: Saúde e Segurança do Trabalho (RH2)

**Escopo:** Módulo `PESSOAS_RH2` — controle de EPIs, treinamentos obrigatórios, CAT, laudos.

**Conhecimentos necessários:**
- Entrega de EPI: ficha de EPI por colaborador
- Treinamentos obrigatórios: NR31 (agropecuária), NR6 (EPI), NR9 (PPRA)
- CAT (Comunicação de Acidente de Trabalho)
- PCMSO e PPRA básicos para propriedades rurais

---

### 🌱 AMBIENTAL

---

#### SKILL-AM-01: Gestão Ambiental e CAR (AM1)

**Escopo:** Módulo `AMBIENTAL_AM1` — CAR, APP, Reserva Legal, sobreposição geoespacial.

**Conhecimentos necessários:**
- CAR: integração com SICAR (Serviço Florestal Brasileiro) para consulta
- APP: Área de Preservação Permanente — rios, nascentes, topos de morro
- Reserva Legal: cálculo de percentual obrigatório por bioma
- PostGIS: ST_Intersects entre talhões e APP/RL
- Alerta quando operação agrícola planejada em área de restrição

**Entregáveis típicos:**
- Layer no mapa de APP e Reserva Legal sobre os talhões
- Alerta automático ao criar safra em talhão com sobreposição de APP

---

#### SKILL-AM-02: Rastreabilidade e Certificações (AM2)

**Escopo:** Módulo `AMBIENTAL_AM2` — cadeia de custódia, Soja Plus, RTRS, créditos de carbono.

**Conhecimentos necessários:**
- Cadeia de custódia: semente → operações → romaneio de entrega
- Soja Plus: formulário de conformidade, rastreabilidade por talhão
- RTRS (Round Table on Responsible Soy): critérios e exportação de relatório
- Crédito de carbono: cálculo de emissão/sequestro por talhão (baseline IPCC)
- Blockchain opcional: registro imutável de rastreabilidade

---

### 🤖 INTELIGÊNCIA ARTIFICIAL

---

#### SKILL-IA-01: LLM e RAG com Ollama

**Escopo:** Agrônomo Virtual — LLM self-hosted, RAG pipeline, contexto de safra no prompt, streaming SSE.

**Conhecimentos necessários:**
- Ollama: modelos Llama 3.1, Qwen 2.5, Mistral
- LangChain + LangGraph: chain building, memory, RAG
- pgvector: embeddings com `nomic-embed-text`, índice HNSW
- Chunking e indexação de documentos EMBRAPA, bulas MAPA
- Montagem de contexto: safra + NDVI + clima + histórico operações
- FastAPI StreamingResponse com Server-Sent Events
- Temperatura baixa (0.3) para respostas técnicas determinísticas

**Entregáveis típicos:**
- `AgronomoVirtualService.chat_stream()`
- Pipeline de indexação de documentos no pgvector
- Componente `AgronomoChat` com streaming visível
- Base de conhecimento EMBRAPA indexada

---

#### SKILL-IA-02: Computer Vision e YOLO (Diagnóstico de Pragas)

**Escopo:** Diagnóstico de pragas e doenças por foto — modelo YOLO v11, processamento de imagem, NDVI via rasterio.

**Conhecimentos necessários:**
- YOLOv11 / EfficientNet: treinamento com dataset de pragas tropicais
- ONNX Runtime: inferência local sem GPU obrigatória
- Pré-processamento: resize 640x640, normalização float32
- Dataset: lagarta-do-cartucho, ferrugem, mancha-alvo, percevejo, cigarrinha
- Rasterio: abertura de rasters, recorte por máscara PostGIS
- NumPy: cálculo NDVI (B08-B04)/(B08+B04), estatísticas por zona

**Entregáveis típicos:**
- `DiagnosticoPragaService.diagnosticar_por_foto()`
- Modelo YOLO treinado: `yolo_pragas_br_v1.onnx`
- `NdviService.buscar_e_processar_sentinel2()`
- GeoTIFF de NDVI salvo no MinIO

---

#### SKILL-IA-03: Machine Learning — Produtividade e Séries Temporais

**Escopo:** Previsão de produtividade por talhão (XGBoost), previsão de peso animal (Prophet), anomalias de custo.

**Conhecimentos necessários:**
- XGBoost: features de NDVI, clima, GDU, histórico de talhão
- Prophet: séries temporais de peso, produção de leite, precipitação
- Feature engineering: GDU acumulado, déficit hídrico, NDVI relativo
- Intervalos de confiança via bootstrap (IC 80%)
- Scikit-learn: GridSearchCV, validação cruzada temporal (TimeSeriesSplit)
- MLflow: tracking de experimentos, registro de versão de modelo

**Entregáveis típicos:**
- `PrevisaoProdutividadeService.prever(safra_id)`
- Modelo XGBoost registrado no MLflow por cultura
- Gráfico de previsão com intervalo de confiança

---

#### SKILL-IA-04: MLOps e MLflow

**Escopo:** Ciclo de vida de modelos — treinamento periódico, versionamento, monitoramento de drift, retreinamento automático.

**Conhecimentos necessários:**
- MLflow: experiments, runs, model registry, artifact store (MinIO)
- Celery task de treinamento mensal por tenant
- Monitoramento de drift: desvio da distribuição de features em produção
- Shadow mode: novo modelo roda em paralelo antes de promover
- A/B testing de modelos por tenant

**Entregáveis típicos:**
- Task Celery `treinar_modelos_mensalmente`
- Dashboard MLflow com comparativo de modelos
- Alertas de drift de modelo via Grafana

---

### 📱 MOBILE

---

#### SKILL-MOBILE-01: React Native e Expo

**Escopo:** Estrutura do app mobile — Expo Router, navegação, autenticação, UI components.

**Conhecimentos necessários:**
- Expo SDK 52: Router, módulos nativos
- Expo Router: file-based routing similar ao Next.js App Router
- NativeWind: Tailwind classes no React Native
- Autenticação: expo-auth-session com Keycloak
- Deep links para abrir registros específicos via notificação
- OTA updates: expo-updates para deploy sem app store

**Entregáveis típicos:**
- Estrutura base do app com autenticação Keycloak
- Navegação: tab bar com módulos contratados
- Tela de rebanho com busca por brinco
- Tela de caderno de campo com registro rápido

---

#### SKILL-MOBILE-02: Offline-First e WatermelonDB

**Escopo:** Sincronização offline-first — WatermelonDB local, sync engine, conflict resolution.

**Conhecimentos necessários:**
- WatermelonDB: schema local, queries, observáveis
- Sync protocol: pull changes (D-1 desde último sync) + push local
- Conflict resolution: last-write-wins com timestamp
- NetInfo: detecção de conectividade para trigger de sync
- Expo Background Fetch: sync automático em background
- Dados prioritários offline: animais, safras ativas, operações pendentes

**Entregáveis típicos:**
- Schema WatermelonDB sincronizado com PostgreSQL
- `SyncEngine.push()` e `SyncEngine.pull()`
- Indicador visual de estado de sincronização
- Fila de operações pendentes com retry

---

#### SKILL-MOBILE-03: Câmera, GPS e Sensores

**Escopo:** Uso de câmera para diagnóstico de pragas, GPS para georeferenciamento, QR code para brinco eletrônico.

**Conhecimentos necessários:**
- expo-camera: captura de foto, modo de câmera frontal/traseira
- expo-location: captura de coordenadas com precisão, foreground/background
- expo-barcode-scanner: leitura de QR code no brinco eletrônico
- Upload de imagem para MinIO via presigned URL
- Envio para `POST /agronomo/diagnostico-praga` com multipart

**Entregáveis típicos:**
- Tela de diagnóstico: câmera → upload → resultado IA em segundos
- GPS automático ao registrar pesagem ou operação
- Leitor de QR code para identificação rápida de animal

---

### 🗄️ BANCO DE DADOS

---

#### SKILL-DB-01: PostgreSQL, RLS e Migrations

**Escopo:** PostgreSQL 16 — schemas, RLS policies, migrations Alembic, índices estratégicos, performance.

**Conhecimentos necessários:**
- Row Level Security: política por tenant, `SET LOCAL app.current_tenant_id`
- Alembic: `upgrade()`, `downgrade()`, `op.execute()` para CONCURRENTLY
- Índices: BTREE, GIST (PostGIS), GIN (full-text), HNSW (pgvector)
- `EXPLAIN ANALYZE`: leitura de plano de execução
- `pg_stat_statements`: identificação de queries lentas
- Ciclo de deprecação de coluna (3 passos)
- Partial indexes: `WHERE ativo = TRUE`

---

#### SKILL-DB-02: TimescaleDB e Séries Temporais

**Escopo:** TimescaleDB — hypertables, compressão, continuous aggregates, retenção automática.

**Conhecimentos necessários:**
- `create_hypertable()`: configuração de chunk interval por tabela
- Compressão: `compress_segmentby`, `compress_orderby`, `add_compression_policy`
- Continuous aggregates: `WITH (timescaledb.continuous)`, refresh policy
- `time_bucket()`: agregação por período (dia, semana, mês)
- Tabelas que usam: `pesagens`, `ndvi_talhao`, `dados_climaticos_talhao`, `producao_leite`

---

### 🖥️ FRONTEND

---

#### SKILL-FRONTEND-01: Next.js RSC e TanStack Query

**Escopo:** Next.js 16 App Router — Server Components, streaming, TanStack Query, Zustand.

**Conhecimentos necessários:**
- App Router: layouts, grupos de rota, loading.tsx, error.tsx
- RSC: quando usar Server vs Client Component
- `headers()` para injetar tenant_id em RSC
- TanStack Query: query keys, staleTime, optimistic updates
- Zustand: stores com immer + persist
- Middleware Edge Runtime: JWT + extração de tenant do subdomínio

---

#### SKILL-FRONTEND-02: MapLibre e Geoespacial

**Escopo:** Mapas interativos — polígonos de talhões, layers NDVI, mapa de prescrição.

**Conhecimentos necessários:**
- MapLibre GL JS 4: sources, layers, paint expressions
- GeoJSON: FeatureCollection de talhões com propriedades NDVI
- Colormap NDVI: interpolate linear por valor (-1 a 1)
- Raster layer: overlay de GeoTIFF de NDVI via MinIO URL assinada
- Draw mode: desenho de polígono para cadastro de talhão
- Popup ao clicar: dados da safra ativa do talhão

---

#### SKILL-FRONTEND-03: AG Grid e Visualizações

**Escopo:** AG Grid Community (100k+ linhas), Recharts, Nivo para visualizações de dados agropecuários.

**Conhecimentos necessários:**
- AG Grid: columnDefs, serverSide rowModel, filtros, export CSV/Excel
- Recharts: LineChart, BarChart, ComposedChart com área
- Nivo: heatmap (GMD por período), calendar (operações por dia)
- Virtualização: apenas renderizar linhas visíveis no grid
- AG Grid Themes: customização com Tailwind CSS vars

---

### 🏗️ INFRAESTRUTURA

---

#### SKILL-INFRA-01: Keycloak e JWT

**Escopo:** Keycloak 26 self-hosted — realm, clients, mappers de claims, RBAC, SSO.

**Conhecimentos necessários:**
- Realm configuration: client_id, client_secret, redirect URIs
- Protocol mappers: adicionar `account_id`, `modules[]`, `roles[]` ao JWT
- User federation: mapeamento de `platform_users` via PostgreSQL
- Token refresh: Keycloak client credentials para api-to-api
- jwtVerify com chave pública RS256 no Edge Middleware

---

#### SKILL-INFRA-02: K3s e Kubernetes

**Escopo:** K3s no bare metal — deployments, services, ingress, PVC, HPA, Longhorn storage.

**Conhecimentos necessários:**
- K3s: instalação em nós, kubeconfig, kubectl
- Deployment: rolling update, readiness/liveness probes
- HPA: autoscaling por CPU/memória
- Longhorn: PVC, StorageClass, snapshots
- Helm: install/upgrade de charts, values customization
- Rancher: UI para gerenciamento do cluster

---

#### SKILL-INFRA-03: CI/CD e GitOps

**Escopo:** Gitea Actions — pipeline lint → test → build → staging → produção.

**Conhecimentos necessários:**
- Gitea Actions: matrix builds por serviço, secrets no Vault
- Docker: multi-stage Dockerfile para Python e Next.js
- Harbor: push de imagens, vulnerability scanning
- kubectl set image: deploy por SHA de commit
- Smoke tests: pytest + requests contra staging
- Rollback: `kubectl rollout undo`

---

#### SKILL-INFRA-04: Observabilidade LGTM

**Escopo:** Prometheus, Loki, Grafana, Tempo — métricas, logs, tracing distribuído.

**Conhecimentos necessários:**
- Prometheus: exporters (postgres, redis, node), AlertManager
- Loki + Promtail: coleta de logs de containers K8s
- Grafana: dashboards por serviço, correlação métrica + log
- Grafana Tempo: OpenTelemetry tracing, request flow cross-service
- Sentry: error tracking Python + TypeScript com contexto de tenant
- Uptime Kuma: status page para clientes

---

#### SKILL-INFRA-05: Segurança e Secrets

**Escopo:** HashiCorp Vault, pfSense, WireGuard, segurança de cluster.

**Conhecimentos necessários:**
- Vault: dynamic secrets PostgreSQL, KV para API keys, PKI
- Secrets Store CSI Driver: montar secrets no pod sem ENV vars
- WireGuard: config de peers, roteamento inter-site
- pfSense / Suricata: regras de firewall, IDS/IPS
- Network policies K8s: isolamento entre namespaces

---

### 🔐 QUALIDADE E SEGURANÇA

---

#### SKILL-QA-01: Testes de Backend (pytest)

**Escopo:** Suite completa de testes Python — unitários, integração, tenant isolation.

**Conhecimentos necessários:**
- pytest + pytest-asyncio: fixtures async, conftest.py
- factory_boy: criação de fixtures de dados realistas
- SQLite in-memory para testes: sem dependência de PostgreSQL real
- Mocking com `unittest.mock.patch`: httpx, Redis, Celery
- Cobertura mínima: 90% services, 80% routers, 95% utils
- Testes de tenant isolation obrigatórios em todo novo Service

---

#### SKILL-QA-02: Testes de Frontend (Vitest + Playwright)

**Escopo:** Testes unitários React com Vitest e E2E com Playwright.

**Conhecimentos necessários:**
- Vitest: testing-library, msw para mock de API
- Playwright: page fixtures, autenticação via storageState
- Visual regression testing: screenshots de componentes críticos
- Testes E2E de fluxos críticos: login, registro de pesagem, emissão NF-e

---

#### SKILL-SEC-01: Segurança e Multitenancy

**Escopo:** Validação de isolamento multi-tenant, testes de segurança, OWASP Top 10 aplicado ao AgroSaaS.

**Conhecimentos necessários:**
- Testes de tenant isolation: tentar acessar dados de outro tenant
- SQL injection prevention: ORM sempre, nunca f-string
- JWT tampering: testar claims manipulados
- RLS bypass attempts: testar SET LOCAL manipulado
- Rate limiting por tenant em endpoints críticos
- Audit log: quem fez o quê em qual tenant

---

#### SKILL-SEC-02: OWASP e Vulnerabilidades

**Escopo:** Trivy para dependências, Bandit para Python, ESLint security para TypeScript, DAST básico.

**Conhecimentos necessários:**
- Trivy: scan de imagens Docker e dependências
- Bandit: análise estática de código Python para vulnerabilidades
- OWASP ZAP: DAST básico contra staging
- Política de rotação de credenciais
- Revisão de secrets em código (git-secrets, trufflehog)

---

## Parte 3 — Matriz de Skills por Role

| Role | Skills Obrigatórias |
|---|---|
| CTO / Arquiteto | CORE-01,02,03 · INFRA-01,02,03 · DB-01,02 · SEC-01,02 |
| TL Plataforma | CORE-01,02,03 · INFRA-01 · DB-01 |
| Eng. Plataforma Sr | CORE-01,02,03 · DB-01 · INFRA-01 |
| Eng. DevOps Sr | INFRA-02,03,04,05 |
| TL Agrícola | AGRO-01 a 06 · GEO-01,02 · IA-02 |
| Eng. Backend Agrícola Sr | AGRO-01,02,03 · DB-01,02 · GEO-01 |
| Eng. Full Stack Agrícola | AGRO-01,02 · FRONTEND-01,02 |
| Esp. Geoespacial | GEO-01,02 · IA-02 |
| TL Pecuário | PEC-01 a 06 · DB-01,02 |
| Eng. Backend Pecuário Sr | PEC-01,02,03 · DB-01,02 |
| Eng. Full Stack Pecuário | PEC-01,02 · FRONTEND-01,03 |
| TL Financeiro | FIN-01,02,03,04 · FIS-01 |
| Eng. Fiscal / NF-e Sr | FIS-01 · FIN-03 · BACKEND-01 |
| Eng. Full Stack Financeiro | FIN-01,02 · FRONTEND-01,03 |
| TL Operacional | OPS-01,02,03,04 · RH-01,02 |
| TL Inteligência Artificial | IA-01,02,03,04 |
| Eng. ML / LLM Sr | IA-01,02,03,04 |
| Eng. Dados / MLOps | IA-03,04 · DB-02 |
| TL Mobile | MOBILE-01,02,03 |
| TL QA & Segurança | QA-01,02 · SEC-01,02 |
