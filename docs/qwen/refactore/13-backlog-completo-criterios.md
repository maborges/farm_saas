# Backlog Completo com Critérios de Aceite e Testes — 3 Frentes

**Data:** 2026-04-06
**Total de tarefas:** ~110
**Esforço total:** ~141h

---

# FRENTE C: Propriedade + Exploração Rural

## C-01: Modelos Propriedade, ExploracaoRural, DocumentoExploracao

**Arquivo:** `services/api/core/cadastros/propriedades/propriedade_models.py` (novo)
**Esforço:** 2h15 | **Dependência:** Nenhuma

### Critérios de aceite
- [ ] 3 classes criadas: `Propriedade`, `ExploracaoRural`, `DocumentoExploracao`
- [ ] 2 enums criados: `NaturezaVinculo` (5 valores), `TipoDocumentoExploracao` (9 valores)
- [ ] `Propriedade.__tablename__ == "cadastros_propriedades"`
- [ ] `ExploracaoRural.__tablename__ == "cadastros_exploracoes_rurais"`
- [ ] `DocumentoExploracao.__tablename__ == "cadastros_documentos_exploracao"`
- [ ] Todas as FKs apontam para tabelas existentes (`tenants`, `fazendas`)
- [ ] Relationships configurados com `back_populates`

### O que testar
- Teste unitário: nomes das tabelas
- Teste unitário: valores dos enums
- Teste unitário: colunas esperadas existem em cada modelo
- Teste de import: `from core.cadastros.propriedades.propriedade_models import ...` sem erro

---

## C-02: Registrar no `__init__.py`

**Arquivo:** `services/api/core/cadastros/propriedades/__init__.py` (editar)
**Esforço:** 15min | **Dependência:** C-01

### Critérios de aceite
- [ ] `Propriedade`, `ExploracaoRural`, `DocumentoExploracao` exportados no `__all__`
- [ ] `NaturezaVinculo`, `TipoDocumentoExploracao` exportados
- [ ] Nenhum import circular
- [ ] Imports existentes continuam funcionando

### O que testar
- `from core.cadastros.propriedades import Propriedade` funciona

---

## C-03: Schemas Pydantic

**Arquivo:** `services/api/core/cadastros/propriedades/propriedade_schemas.py` (novo)
**Esforço:** 1h | **Dependência:** C-01

### Critérios de aceite
- [ ] `PropriedadeCreate` com `nome` obrigatório (min 2, max 200)
- [ ] `PropriedadeUpdate` com todos os campos opcionais
- [ ] `ExploracaoCreate` valida `natureza` contra `NaturezaVinculo`
- [ ] `ExploracaoUpdate` valida `natureza` se informado
- [ ] `DocumentoExploracaoCreate` valida `tipo` contra `TipoDocumentoExploracao`
- [ ] Todos os `*Response` com `model_config = {"from_attributes": True}`

### O que testar
- `PropriedadeCreate(nome="X")` → ValidationError (min_length)
- `ExploracaoCreate(natureza="invalida", ...)` → ValueError
- `ExploracaoCreate(natureza="propria", ...)` → válido
- `DocumentoExploracaoCreate(tipo="xyz", ...)` → ValueError
- `DocumentoExploracaoCreate(tipo="contrato_arrendamento", ...)` → válido

---

## C-04: Service com validações

**Arquivo:** `services/api/core/cadastros/propriedades/propriedade_service.py` (novo)
**Esforço:** 2h | **Dependência:** C-01, C-03

### Critérios de aceite
- [ ] `PropriedadeService` herda `BaseService[Propriedade]`
- [ ] `ExploracaoRuralService._validar_sobreposicao()` detecta período sobreposto
- [ ] `ExploracaoRuralService._validar_area()` rejeita area > area_total × 1.05
- [ ] `ExploracaoRuralService.criar()` valida existência de propriedade e fazenda
- [ ] `ExploracaoRuralService.criar()` valida data_fim > data_inicio
- [ ] `listar_vigentes_por_fazenda()` retorna apenas data_fim NULL ou >= hoje

### O que testar
- Criar sobreposição → `BusinessRuleError`
- Criar area explorada 110% da area total → `BusinessRuleError`
- Criar data_fim < data_inicio → `BusinessRuleError`
- Criar com propriedade inexistente → `EntityNotFoundError`
- Criar válido → objeto retornado com ID
- Listar vigentes com data_fim passado → não retorna

---

## C-05: Router CRUD

**Arquivo:** `services/api/core/cadastros/propriedades/propriedade_router.py` (novo)
**Esforço:** 2h | **Dependência:** C-03, C-04

### Critérios de aceite
- [ ] `POST /cadastros/propriedades/` → 201 com body válido
- [ ] `GET /cadastros/propriedades/` → lista (filtro `ativo` opcional)
- [ ] `GET /cadastros/propriedades/{id}` → 404 se inexistente
- [ ] `PATCH /cadastros/propriedades/{id}` → atualiza parcialmente
- [ ] `DELETE /cadastros/propriedades/{id}` → 204
- [ ] `GET /cadastros/propriedades/{id}/exploracoes` → lista explorações
- [ ] `POST /cadastros/propriedades/{id}/exploracoes` → 201 com validação
- [ ] `GET /cadastros/propriedades/fazenda/{id}/exploracoes` → vigentes
- [ ] Router registrado em `main.py` com prefix `/api/v1`

### O que testar
- Teste de integração: CRUD completo de Propriedade
- Teste de integração: criar exploração com sobreposição → 422
- Teste de integração: listar vigentes por fazenda
- Teste de integração: tenant isolation (tenant A não vê dados do tenant B)

---

## C-06: Migration

**Arquivo:** `services/api/migrations/versions/add_propriedade_exploracao_rural.py` (novo)
**Esforço:** 3h | **Dependência:** C-01

### Critérios de aceite
- [ ] 3 tabelas criadas: `cadastros_propriedades`, `cadastros_exploracoes_rurais`, `cadastros_documentos_exploracao`
- [ ] Migração de dados: `grupos_fazendas` → `cadastros_propriedades` (mesmo count)
- [ ] Migração de dados: `grupo_fazendas_rel` → `cadastros_exploracoes_rurais` (mesmo count)
- [ ] Coluna `exploracao_id` adicionada em `fazendas` (nullable + FK)
- [ ] `alembic downgrade -1` reverte todas as 6 operações
- [ ] `alembic upgrade head` re-aplica sem erro

### O que testar
- `alembic upgrade head` → exit code 0
- `SELECT COUNT(*) FROM cadastros_propriedades` = `SELECT COUNT(*) FROM grupos_fazendas`
- `SELECT COUNT(*) FROM cadastros_exploracoes_rurais` = `SELECT COUNT(*) FROM grupo_fazendas_rel`
- `alembic downgrade -1` → exit code 0, tabelas removidas
- `alembic upgrade head` novamente → exit code 0

---

## CF-C1: Zod schemas frontend

**Arquivo:** `packages/zod-schemas/src/propriedade-schemas.ts` (novo)
**Esforço:** 1h | **Dependência:** C-03

### Critérios de aceite
- [ ] `createPropriedadeSchema`: nome min 2, max 200
- [ ] `createExploracaoSchema`: natureza com 5 opções via enum
- [ ] `createExploracaoSchema`: data_fim opcional/nullable
- [ ] Validação de formato de email no `email`
- [ ] Types TypeScript exportados: `CreatePropriedadeInput`, `CreateExploracaoInput`

### O que testar
- `{ nome: "X" }` → falha
- `{ nome: "Agro Ltda" }` → passa
- `{ natureza: "aluguel" }` → falha
- `{ natureza: "propria", fazenda_id: uuid, data_inicio: Date }` → passa

---

## CF-C2: Lista de Propriedades

**Arquivo:** `apps/web/src/app/(dashboard)/cadastros/propriedades-econ/page.tsx` (novo)
**Esforço:** 4h | **Dependência:** CF-C1, C-05

### Critérios de aceite
- [ ] DataTable com colunas: Nome, CNPJ/CPF, Regime (badge), Status (badge), Ações
- [ ] Busca filtra por nome e CNPJ
- [ ] Botão "Nova Propriedade" abre Dialog
- [ ] Dialog valida com `createPropriedadeSchema` antes de enviar
- [ ] Criação bem-sucedida → toast + invalida query + fecha dialog
- [ ] Botão Eye → navega para `/cadastros/propriedades-econ/{id}`
- [ ] Loading skeleton durante fetch
- [ ] Empty state quando lista vazia

### O que testar
- Teste manual: lista carrega com dados
- Teste manual: busca filtra corretamente
- Teste manual: criação com nome curto → erro Zod visível
- Teste manual: criação válida → toast sucesso + item aparece na lista

---

## CF-C3: Detalhe da Propriedade

**Arquivo:** `apps/web/src/app/(dashboard)/cadastros/propriedades-econ/[id]/page.tsx` (novo)
**Esforço:** 6h | **Dependência:** CF-C2

### Critérios de aceite
- [ ] 4 abas: Dados Gerais, Fazendas Vinculadas, Documentos, Histórico
- [ ] Aba Dados Gerais: form de edição com dados atuais
- [ ] Aba Fazendas: DataTable com fazenda, natureza, vigência, área
- [ ] Aba Documentos: lista por exploração com tipo, nome, validade
- [ ] Aba Histórico: timeline de explorações passadas e vigentes
- [ ] Dialog de criação de Exploração com validação Zod
- [ ] Sobreposição detectada → toast erro
- [ ] Breadcrumb: Propriedades → {nome}

### O que testar
- Teste manual: todas as 4 abas renderizam
- Teste manual: criar exploração válida → aparece na aba Fazendas
- Teste manual: criar exploração com sobreposição → erro visível

---

## CF-C4: Dialog de Exploração

**Arquivo:** `apps/web/src/components/core/propriedades/ExploracaoDialog.tsx` (novo)
**Esforço:** 3h | **Dependência:** CF-C3

### Critérios de aceite
- [ ] Props: `open`, `onOpenChange`, `propriedadeId`, `fazendasDisponiveis`, `onSuccess`
- [ ] Select de fazenda com nome + área
- [ ] Select de natureza com 5 opções
- [ ] Date pickers para data_inicio e data_fim
- [ ] Campos numéricos: valor_anual, percentual_producao, area_explorada_ha
- [ ] Validação Zod antes de submit
- [ ] Warning visual se area_explorada > area_total da fazenda

### O que testar
- Teste manual: dialog abre/fecha corretamente
- Teste manual: submit com fazenda não selecionada → erro
- Teste manual: submit válido → toast sucesso + onSuccess chamado

---

## CF-C5: Upload de Documentos

**Arquivo:** `apps/web/src/components/core/propriedades/DocumentoUpload.tsx` (novo)
**Esforço:** 3h | **Dependência:** CF-C3

### Critérios de aceite
- [ ] File picker aceita pdf, jpg, docx
- [ ] Upload via endpoint de documentos
- [ ] Lista documentos com tipo (badge), nome, validade
- [ ] Alerta visual se `data_validade` < hoje (vermelho)
- [ ] Delete/remove documento

### O que testar
- Teste manual: upload de PDF funciona
- Teste manual: documento vencido exibe badge vermelho

---

## CF-C6: Fazenda exibe vínculo de exploração

**Arquivo:** `apps/web/src/app/(dashboard)/cadastros/propriedades/[id]/page.tsx` (editar)
**Esforço:** 2h | **Dependência:** C-05

### Critérios de aceite
- [ ] Card/badge na página de detalhe: "Explorada por: {nome}"
- [ ] Exibe natureza do vínculo
- [ ] Exibe vigência (data_inicio até data_fim ou "vigente")
- [ ] Link clicável para `/cadastros/propriedades-econ/{propriedade_id}`
- [ ] Se sem exploração: exibe "Sem explorador definido"

### O que testar
- Teste manual: fazenda com exploração exibe dados corretos
- Teste manual: fazenda sem exploração exibe mensagem padrão
- Teste manual: link para propriedade funciona

---

# FRENTE A: Hierarquia + Agricultura de Precisão

## A-01: SUBTALHAO + ZONA_DE_MANEJO no enum

**Arquivo:** `services/api/core/cadastros/propriedades/models.py` (editar)
**Esforço:** 15min | **Dependência:** Nenhuma

### Critérios de aceite
- [ ] `TipoArea.SUBTALHAO = "SUBTALHAO"` adicionado
- [ ] `TipoArea.ZONA_DE_MANEJO = "ZONA_DE_MANEJO"` adicionado
- [ ] Enum totaliza agora 14 valores
- [ ] Nenhum outro código quebrado

### O que testar
- `from core.cadastros.propriedades.models import TipoArea` → funciona
- `TipoArea.SUBTALHAO.value == "SUBTALHAO"`
- `TipoArea.ZONA_DE_MANEJO.value == "ZONA_DE_MANEJO"`
- `len(list(TipoArea)) == 14`

---

## A-02: Colunas de precisão no AreaRural

**Arquivo:** `services/api/core/cadastros/propriedades/models.py` (editar)
**Esforço:** 1h | **Dependência:** A-01

### Critérios de aceite
- [ ] 11 colunas novas: `tipo_solo`, `teor_argila`, `teor_areia`, `ph_solo`, `materia_organica_pct`, `condutividade_eletrica`, `produtividade_media_ha`, `cultura_atual`, `irrigado`, `nivel_profundidade`
- [ ] Todas nullable (exceto `nivel_profundidade` com default 0)
- [ ] Tipos corretos: Numeric para decimais, String para textos, Boolean para irrigado

### O que testar
- `AreaRural.__table__.columns` contém todas as 11 colunas novas
- `tipo_solo` é String(50)
- `nivel_profundidade` é SmallInteger com default 0

---

## A-03: Modelo HistoricoUsoTalhao

**Arquivo:** `services/api/core/cadastros/propriedades/models.py` (editar)
**Esforço:** 1h | **Dependência:** A-02

### Critérios de aceite
- [ ] Tabela `cadastros_areas_historico_uso` criada
- [ ] Colunas: id, tenant_id, area_rural_id, data_inicio, data_fim, tipo_uso, cultivar, produtividade_obtida, observacoes, created_at
- [ ] FK `area_rural_id` → `cadastros_areas_rurais.id` com `ondelete="CASCADE"`
- [ ] Relationship em `AreaRural`: `historico_uso` com `cascade="all, delete-orphan"`

### O que testar
- Import sem erro
- Colunas esperadas existem
- Relationship configurado corretamente

---

## A-04: Modelo AmostraSolo

**Arquivo:** `services/api/core/cadastros/propriedades/models.py` (editar)
**Esforço:** 1h | **Dependência:** A-02

### Critérios de aceite
- [ ] Tabela `cadastros_amostras_solo` criada
- [ ] Colunas: id, tenant_id, area_rural_id (nullable), lat, lng, profundidade, data_coleta, análise completa (ph, MO, P, K, Ca, Mg, Al, H+Al, CTC, V%, argila, areia, silte), classificacao, laboratorio, numero_laudo, created_at
- [ ] FK `area_rural_id` nullable com `ondelete="SET NULL"`
- [ ] Relationship em `AreaRural`: `amostras_solo` com `cascade="all, delete-orphan"`

### O que testar
- Import sem erro
- Colunas esperadas existem
- `area_rural_id` é nullable

---

## A-05: Migration (tipos + colunas + tabelas novas)

**Arquivo:** `services/api/migrations/versions/` (novo)
**Esforço:** 2h | **Dependência:** A-01 a A-04

### Critérios de aceite
- [ ] Migration cria 2 tabelas novas: `cadastros_areas_historico_uso`, `cadastros_amostras_solo`
- [ ] Migration adiciona 11 colunas em `cadastros_areas_rurais`
- [ ] Migration é reversível (downgrade funciona)
- [ ] Nenhum dado existente é perdido

### O que testar
- `alembic upgrade head` → exit code 0
- `alembic downgrade -1` → exit code 0, tabelas removidas, colunas removidas
- Re-upgrade → exit code 0

---

## A-06: Script popular nivel_profundidade

**Arquivo:** Script SQL ou Python
**Esforço:** 1h | **Dependência:** A-05

### Critérios de aceite
- [ ] Áreas com `parent_id = NULL` → nivel 0 (se tipo PROPRIEDADE) ou nivel 1 (se tipo GLEBA)
- [ ] Áreas com `parent_id` apontando para nivel N → nivel N+1
- [ ] Script é idempotente (rodar 2x não quebra)

### O que testar
- `SELECT tipo, nivel_profundidade FROM cadastros_areas_rurais WHERE tipo = 'GLEBA'` → todos nivel 1
- `SELECT tipo, nivel_profundidade FROM cadastros_areas_rurais WHERE tipo = 'TALHAO' AND parent_id IS NOT NULL` → todos nivel 2

---

## A-07: validar_hierarquia() no Service

**Arquivo:** `services/api/core/cadastros/propriedades/service.py` (editar)
**Esforço:** 2h | **Dependência:** A-01

### Critérios de aceite
- [ ] Dict `HIERARQUIA_VALIDA` com 14 entradas (uma por tipo)
- [ ] `PROPRIEDADE` aceita: GLEBA, TALHAO, PASTAGEM, APP, RESERVA_LEGAL, UNIDADE_PRODUTIVA, SEDE, ARMAZEM, INFRAESTRUTURA, AREA
- [ ] `TALHAO` aceita: SUBTALHAO, PIQUETE
- [ ] `SUBTALHAO` aceita: ZONA_DE_MANEJO
- [ ] `ZONA_DE_MANEJO` não aceita filhos (set vazio)
- [ ] `parent_id = NULL` só permitido para `PROPRIEDADE`
- [ ] Erro retorna `BusinessRuleError` com mensagem clara

### O que testar
- Criar TALHAO dentro de GLEBA → passa
- Criar SUBTALHAO dentro de TALHAO → passa
- Criar ZONA_DE_MANEJO dentro de SUBTALHAO → passa
- Criar PIQUETE dentro de APP → `BusinessRuleError`
- Criar ZONA_DE_MANEJO dentro de SEDE → `BusinessRuleError`
- Criar TALHAO sem parent → `BusinessRuleError`

---

## A-08: calcular_soma_areas() no Service

**Arquivo:** `services/api/core/cadastros/propriedades/service.py` (editar)
**Esforço:** 30min | **Dependência:** A-07

### Critérios de aceite
- [ ] Retorna dict com `soma_areas_filhas_ha`, `numero_filhos`, `areas[]`
- [ ] Usa `area_hectares` ou `area_hectares_manual` (fallback)
- [ ] Apenas áreas ativas

### O que testar
- Pai com 3 filhos de 10, 20, 30 ha → soma = 60
- Pai sem filhos → soma = 0, numero_filhos = 0
- Pai com filho inativo → não conta na soma

---

## A-09: obter_arvore() no Service

**Arquivo:** `services/api/core/cadastros/propriedades/service.py` (editar)
**Esforço:** 1h | **Dependência:** A-07, A-08

### Critérios de aceite
- [ ] Retorna estrutura recursiva com id, tipo, nome, codigo, area_ha, nivel, dados_precisao, filhos[]
- [ ] `dados_precisao` preenchido apenas para SUBTALHAO, ZONA_DE_MANEJO, TALHAO
- [ ] Apenas filhos ativos incluídos
- [ ] Usa `selectinload` para evitar N+1

### O que testar
- Árvore com 3 níveis → JSON recursivo correto
- Árvore com nó sem filhos → `filhos: []`
- Nó inativo → não aparece na árvore

---

## A-10: Aplicar validação no POST do router

**Arquivo:** `services/api/core/cadastros/propriedades/router.py` (editar)
**Esforço:** 30min | **Dependência:** A-07

### Critérios de aceite
- [ ] POST `/cadastros/areas-rurais` chama `validar_hierarquia(data.parent_id, data.tipo)` antes de criar
- [ ] Hierarquia inválida → retorna 422 com mensagem clara
- [ ] Hierarquia válida → continua normalmente (201)

### O que testar
- POST com `tipo=TALHAO, parent_id=NULL` → 422
- POST com `tipo=SUBTALHAO, parent_id=TALHAO_UUID` → 201
- POST com `tipo=ZONA_DE_MANEJO, parent_id=GLEBA_UUID` → 422

---

## A-11: Endpoints /arvore e /soma-areas

**Arquivo:** `services/api/core/cadastros/propriedades/router.py` (editar)
**Esforço:** 30min | **Dependência:** A-08, A-09

### Critérios de aceite
- [ ] `GET /{area_id}/arvore` → JSON hierárquico
- [ ] `GET /{area_id}/soma-areas` → dict com soma e lista de filhos
- [ ] Ambos retornam 404 se area_id inexistente

### O que testar
- GET /arvore com Gleba que tem 2 talhões → JSON com 2 filhos
- GET /soma-areas com talhão sem filhos → `{soma: 0, numero_filhos: 0}`

---

## A-12: Endpoints historico-uso

**Arquivo:** `services/api/core/cadastros/propriedades/router.py` (editar)
**Esforço:** 1h | **Dependência:** A-03

### Critérios de aceite
- [ ] `GET /{area_id}/historico-uso` → lista de registros
- [ ] `POST /{area_id}/historico-uso` → 201 com body válido
- [ ] `tipo_uso` obrigatório
- [ ] `data_fim` opcional (NULL = atual)

### O que testar
- GET com talhão sem histórico → lista vazia
- POST com `tipo_uso=SOJA, data_inicio=2024-10-01` → 201
- POST com `data_fim < data_inicio` → 422

---

## A-13: Endpoints amostras-solo

**Arquivo:** `services/api/core/cadastros/propriedades/router.py` (editar)
**Esforço:** 1h | **Dependência:** A-04

### Critérios de aceite
- [ ] `GET /{area_id}/amostras-solo` → lista de amostras
- [ ] `POST /{area_id}/amostras-solo` → 201
- [ ] latitude entre -90 e 90, longitude entre -180 e 180
- [ ] `profundidade_cm` obrigatório > 0

### O que testar
- POST com lat=91 → 422
- POST com profundidade=0 → 422
- POST válido → 201

---

## A-14: Expandir schemas AreaRuralCreate/Update

**Arquivo:** `services/api/core/cadastros/propriedades/schemas.py` (editar)
**Esforço:** 30min | **Dependência:** A-02

### Critérios de aceite
- [ ] `AreaRuralCreate` inclui campos de precisão (todos opcionais)
- [ ] `AreaRuralUpdate` inclui campos de precisão (todos opcionais)
- [ ] Validações: `teor_argila` entre 0-100, `ph_solo` entre 0-14, etc.

### O que testar
- `AreaRuralCreate(tipo="SUBTALHAO", tipo_solo="LATOSSOLO", ph_solo=5.8)` → válido
- `AreaRuralCreate(teor_argila=150)` → ValidationError

---

## A-15: Schemas HistoricoUso e AmostraSolo

**Arquivo:** `services/api/core/cadastros/propriedades/schemas.py` (editar)
**Esforço:** 1h | **Dependência:** A-03, A-04

### Critérios de aceite
- [ ] `HistoricoUsoCreate/Response` criados
- [ ] `AmostraSoloCreate/Response` criados
- [ ] Validações de faixa para campos numéricos de solo

### O que testar
- `HistoricoUsoCreate(tipo_uso="SOJA", data_inicio=date(2024,1,1))` → válido
- `AmostraSoloCreate(lat=91, ...)` → ValidationError

---

## A-16: RN-CP-004 bloqueante no backend

**Arquivo:** `services/api/core/cadastros/propriedades/service.py` (editar)
**Esforço:** 2h | **Dependência:** A-08

### Critérios de aceite
- [ ] Ao criar TALHAO, SUBTALHAO ou ZONA_DE_MANEJO, calcula soma de áreas dos irmãos
- [ ] Se soma nova > area_total_fazenda × 1.05 → `BusinessRuleError`
- [ ] Mensagem de erro clara: "Soma dos talhões (X ha) excede 105% da área total (Y ha = Z ha)"
- [ ] Atualização também valida (recalcula ao mudar area_hectares)

### O que testar
- Fazenda 1000ha, talhões existentes 900ha, criar talhão 160ha → passa (1060 ≤ 1050? Não! 1060 > 1050 → erro)
- Fazenda 1000ha, talhões 900ha, criar talhão 100ha → passa (1000 ≤ 1050)
- Atualizar talhão de 100 para 200ha quando soma já é 1000ha → erro

---

## A-17: Testes unitários validação hierárquica

**Arquivo:** `services/api/tests/unit/test_area_hierarquia.py` (novo)
**Esforço:** 2h | **Dependência:** A-07

### Critérios de aceite
- [ ] Mínimo 10 cenários de teste (5 válidos + 5 inválidos)
- [ ] Cobertura de todos os tipos do enum
- [ ] Teste de parent_id NULL

### O que testar
- Cenários válidos: PROP→GLEBA, GLEBA→TALHAO, TALHAO→SUBTALHAO, SUBTALHAO→ZONA, PROP→TALHAO
- Cenários inválidos: APP→TALHAO, SEDE→ZONA, TALHAO sem parent, ZONA→SUBTALHAO, PIQUETE→TALHAO

---

## A-18: Testes unitários soma de áreas + RN-CP-004

**Arquivo:** `services/api/tests/unit/test_area_soma.py` (novo)
**Esforço:** 1h | **Dependência:** A-16

### Critérios de aceite
- [ ] Teste soma correta
- [ ] Teste soma com área manual fallback
- [ ] Teste bloqueio > 105%
- [ ] Teste área NULL não conta

### O que testar
- 3 talhões: 100, 200, 300ha → soma 600
- Talhão com area=NULL → não conta
- Fazenda 500ha, soma 400ha, criar 150ha → erro (550 > 525)

---

## A-19: Testes integração historico + amostras

**Arquivo:** `services/api/tests/integration/test_historico_amostras.py` (novo)
**Esforço:** 2h | **Dependência:** A-12, A-13

### Critérios de aceite
- [ ] CRUD completo de historico_uso via API
- [ ] CRUD completo de amostras_solo via API
- [ ] Tenant isolation validado

### O que testar
- POST historico → GET confirma
- POST amostra → GET confirma
- Tenant A não vê amostras do tenant B

---

## A-20: Safra.talhao_id → nullable

**Arquivo:** `services/api/agricola/safras/models.py` (editar) + migration
**Esforço:** 2h | **Dependência:** A-05

### Critérios de aceite
- [ ] `Safra.talhao_id` muda de `nullable=False` para `nullable=True`
- [ ] Migration existente não quebra dados
- [ ] Safra pode ser criada sem talhao_id
- [ ] SafraTalhao N:N continua funcionando

### O que testar
- Criar safra sem talhao_id → 201
- Criar safra com talhao_id → 201 (backward compat)
- Safra existente com talhao_id → continua acessível

---

## A-21: Restringir OperacaoAgricola.talhao_id

**Arquivo:** `services/api/agricola/operacoes/service.py` (editar)
**Esforço:** 1h | **Dependência:** A-01

### Critérios de aceite
- [ ] Ao criar operação, valida que `talhao_id` aponta para área do tipo: TALHAO, SUBTALHAO, ZONA_DE_MANEJO, PASTAGEM, PIQUETE
- [ ] Tipos inválidos (GLEBA, SEDE, APP, etc.) → `BusinessRuleError`

### O que testar
- Operação com talhao_id=TALHAO → passa
- Operação com talhao_id=GLEBA → `BusinessRuleError`
- Operação com talhao_id=SUBTALHAO → passa

---

## AF-A1: Zod schemas fazenda-schemas + novos

**Arquivo:** `packages/zod-schemas/src/fazenda-schemas.ts` (editar)
**Esforço:** 2h | **Dependência:** A-14

### Critérios de aceite
- [ ] `createFazendaSchema` adiciona campos: `uf`, `municipio`, `codigo_car`, `nirf`, `area_aproveitavel_ha`, `area_app_ha`, `area_rl_ha`
- [ ] Corrige `cnpj` → `cpf_cnpj`
- [ ] Cria schemas para AreaRural, HistoricoUso, AmostraSolo
- [ ] Validação de formato CAR: regex `^[A-Z]{2}-\d{12}$`

### O que testar
- `{ nome: "X", grupo_id: uuid }` → falha (nome min 2)
- `{ codigo_car: "MT-1234567890123" }` → passa
- `{ codigo_car: "invalido" }` → falha (se validação adicionada)

---

## AF-A2: AreaTree.tsx

**Arquivo:** `apps/web/src/components/core/areas/AreaTree.tsx` (novo)
**Esforço:** 6h | **Dependência:** A-11

### Critérios de aceite
- [ ] Componente recursivo renderiza hierarquia expansível
- [ ] Ícones diferentes por tipo (Gleba=mapa, Talhão=trator, Subtalhão=lupa, Zona=pintura)
- [ ] Cores diferentes por tipo
- [ ] Expande/colapsa com clique
- [ ] Lazy loading de nós (só carrega filhos ao expandir)
- [ ] Exibe área ao lado do nome
- [ ] Responsivo em tablet

### O que testar
- Teste manual: árvore com 4 níveis renderiza
- Teste manual: expandir/colapsar funciona
- Teste manual: ícones e cores corretos por tipo

---

## AF-A3: ZonaManejoDialog.tsx

**Arquivo:** `apps/web/src/components/core/areas/ZonaManejoDialog.tsx` (novo)
**Esforço:** 4h | **Dependência:** AF-A1

### Critérios de aceite
- [ ] Dialog com campos: nome, codigo, area, tipo (select SUBTALHAO ou ZONA_DE_MANEJO)
- [ ] Campos de precisão: tipo_solo, teor_argila, ph_solo, produtividade_media
- [ ] Validação Zod antes de submit
- [ ] Suporte a edição (preenche com dados existentes)

### O que testar
- Teste manual: criação de subtalhão com dados de solo
- Teste manual: edição de zona existente

---

## AF-A4: HistoricoUsoTimeline.tsx

**Arquivo:** `apps/web/src/components/core/areas/HistoricoUsoTimeline.tsx` (novo)
**Esforço:** 3h | **Dependência:** A-12

### Critérios de aceite
- [ ] Timeline visual com períodos cronológicos
- [ ] Exibe: cultura, período (data_inicio → data_fim), produtividade
- [ ] "Atual" para registro com data_fim NULL
- [ ] Botão "Adicionar registro de uso"

### O que testar
- Teste manual: timeline com 5 registros renderiza corretamente
- Teste manual: registro atual exibe badge "Atual"

---

## AF-A5: AmostrasSoloMap.tsx

**Arquivo:** `apps/web/src/components/core/areas/AmostrasSoloMap.tsx` (novo)
**Esforço:** 6h | **Dependência:** A-13

### Critérios de aceite
- [ ] Mapa MapLibre com pontos de amostra sobrepostos a polígonos
- [ ] Clique no ponto exibe popup com dados da análise (pH, P, K, MO, etc.)
- [ ] Cores dos pontos por pH (vermelho=ácido, verde=neutro)
- [ ] Funcional em tablet (uso em campo)

### O que testar
- Teste manual: mapa com 10 pontos renderiza
- Teste manual: clique em ponto exibe dados corretos
- Teste manual: responsivo em 1024px

---

## AF-A6: Aba Hierarquia na página de detalhe

**Arquivo:** `apps/web/src/app/(dashboard)/cadastros/propriedades/[id]/page.tsx` (editar)
**Esforço:** 4h | **Dependência:** AF-A2

### Critérios de aceite
- [ ] Nova aba "Hierarquia" na página existente
- [ ] Renderiza `AreaTree` com dados da fazenda
- [ ] Botão "Adicionar Gleba/Talhão/Subtalhão"
- [ ] Progress bar de soma de áreas (RN-CP-004)

### O que testar
- Teste manual: aba Hierarquia aparece e carrega
- Teste manual: botão de adicionar abre dialog correto

---

## AF-A7: Aba Amostras de Solo

**Arquivo:** `apps/web/src/app/(dashboard)/cadastros/propriedades/[id]/page.tsx` (editar)
**Esforço:** 4h | **Dependência:** AF-A5

### Critérios de aceite
- [ ] Nova aba "Amostras de Solo"
- [ ] Renderiza `AmostrasSoloMap`
- [ ] Lista de amostras em tabela abaixo do mapa
- [ ] Botão "Nova Amostra" com formulário

### O que testar
- Teste manual: aba carrega com mapa + tabela
- Teste manual: criar amostra → aparece no mapa e na tabela

---

## AF-A8: RN-CP-004 bloqueante no frontend

**Arquivo:** `apps/web/src/app/(dashboard)/cadastros/propriedades/[id]/page.tsx` (editar)
**Esforço:** 2h | **Dependência:** A-16

### Critérios de aceite
- [ ] Progress bar fica vermelha quando > 105%
- [ ] Botão de criar talhão desabilitado quando > 105%
- [ ] Tooltip explica o bloqueio: "Soma dos talhões (X ha) excede 105% da área total"

### O que testar
- Teste manual: barra verde em 80%, amarela em 95%, vermelha em 106%
- Teste manual: botão desabilitado em 106%

---

## AF-A9: Prescrição VRA por zona

**Arquivo:** `apps/web/src/app/(dashboard)/agricola/prescricoes/` (novo)
**Esforço:** 8h | **Dependência:** A-01

### Critérios de aceite
- [ ] Mapa com zonas coloridas por dose de prescrição
- [ ] Seletor de safra + talhão/subtalhão/zona
- [ ] Tabela de prescrição: insumo, dose min, dose max, dose média
- [ ] Suporte a múltiplas zonas na mesma prescrição

### O que testar
- Teste manual: mapa de prescrição renderiza com cores por zona
- Teste manual: criar prescrição com 3 zonas diferentes

---

## AF-A10: Upload de grade GeoJSON

**Arquivo:** `apps/web/src/app/(dashboard)/agricola/prescricoes/` (editar)
**Esforço:** 4h | **Dependência:** AF-A9

### Critérios de aceite
- [ ] File picker para GeoJSON
- [ ] Preview do mapa com grade sobreposta
- [ ] Validação de formato GeoJSON
- [ ] Upload via endpoint existente

### O que testar
- Teste manual: upload de GeoJSON válido → preview renderiza
- Teste manual: arquivo inválido → erro visível

---

## AF-A11 a AF-A16: Polimento UI

| ID | Tarefa | Esforço | Critérios chave |
|----|--------|---------|-----------------|
| AF-A11 | Editar propriedade | 2h | Dialog abre com dados atuais, salva, toast sucesso |
| AF-A12 | Desativar/Reativar | 2h | Confirm dialog, soft delete, badge muda |
| AF-A13 | Editar/excluir na lista | 2h | Botões na DataTable, ações funcionais |
| AF-A14 | Empty state com CTA | 1h | Ilustração + botão "Nova Propriedade" |
| AF-A15 | Campos opcionais no form | 2h | CAR, NIRF, IE aparecem no form de criação |
| AF-A16 | Validação CAR frontend | 1h | Regex `^[A-Z]{2}-\d{12}$` no Zod |

---

# FRENTE B: Custeio Automático → Financeiro

## B-01: Criar Rateio automático na despesa da operação

**Arquivo:** `services/api/agricola/operacoes/service.py` (editar)
**Esforço:** 1h | **Dependência:** Nenhuma (independente das demais)

### Critérios de aceite
- [ ] Ao criar despesa automática pela operação, cria também `Rateio` vinculado
- [ ] Rateio: `safra_id` = safra da operação, `talhao_id` = talhão da operação
- [ ] `valor_rateado` = `custo_total_operacao`, `percentual` = 100.0
- [ ] `despesa_id` aponta para a despesa recém-criada

### O que testar
- Criar operação com custo → despesa criada + rateio criado
- Rateio tem safra_id e talhao_id corretos
- Rateio valor = custo_total da operação

---

## B-02: Lookup table operação → plano de conta

**Arquivo:** Nova tabela `agricola_operacao_plano_conta` + migration
**Esforço:** 2h | **Dependência:** B-01

### Critérios de aceite
- [ ] Tabela mapeia tipo de operação (PLANTIO, PULVERIZACAO, etc.) para plano de conta
- [ ] Fallback: se não houver mapeamento, usa conta CUSTEIO genérica
- [ ] Despesa criada usa conta específica do tipo de operação

### O que testar
- PLANTIO → conta "4.1.01 — Custeio/Plantio"
- Tipo sem mapeamento → conta CUSTEIO genérica

---

## B-03: CustosService lê despesas do financeiro

**Arquivo:** `services/api/agricola/custos/service.py` (editar)
**Esforço:** 2h | **Dependência:** B-01

### Critérios de aceite
- [ ] `get_resumo_safra()` soma custos de operações + despesas rateadas
- [ ] Breakdown separa: custos operacionais vs despesas manuais
- [ ] Sem duplicação: se despesa já veio de operação, não soma duas vezes

### O que testar
- Safra com operações de R$1000 + despesa manual rateada de R$500 → total R$1500
- Despesa de operação já contada no custo operacional → não duplica

---

## B-04: Custo de mão de obra na operação

**Arquivo:** `services/api/agricola/operacoes/models.py` + `service.py` (editar)
**Esforço:** 3h | **Dependência:** B-01

### Critérios de aceite
- [ ] Modelo `OperacaoAgricola` adiciona campos: `horas_mo`, `valor_hora_mo`, `custo_mo_total`
- [ ] `custo_total` da operação = custo_insumos + custo_mo + custo_maquina
- [ ] Despesa automática inclui custo de MO

### O que testar
- Operação com 8h MO × R$25/h → custo_mo = R$200
- Custo total da operação inclui MO

---

## B-05: Custo de máquina na operação

**Arquivo:** `services/api/agricola/operacoes/models.py` + `service.py` (editar)
**Esforço:** 3h | **Dependência:** B-04

### Critérios de aceite
- [ ] Modelo adiciona: `horas_maquina`, `valor_hora_maquina`, `custo_maquina_total`
- [ ] `custo_total` = insumos + MO + máquina
- [ ] Despesa automática inclui custo de máquina

### O que testar
- Operação com 4h trator × R$85/h → custo_maquina = R$340
- Custo total inclui todos os 3 componentes

---

## B-06: Testes integração operação → despesa → rateio

**Arquivo:** `services/api/tests/integration/test_operacao_financeiro.py` (novo)
**Esforço:** 2h | **Dependência:** B-01, B-02, B-03

### Critérios de aceite
- [ ] Teste end-to-end: criar operação → verificar despesa → verificar rateio → verificar centro de custos
- [ ] Tenant isolation
- [ ] Rollback se qualquer etapa falhar

### O que testar
- Criar operação via API → GET /financeiro/centro-custos mostra custo
- Despesa tem origem_tipo = "OPERACAO_AGRICOLA"
- Rateio tem safra_id e talhao_id corretos

---

## B-07: Margem líquida e ROI por safra

**Arquivo:** `services/api/agricola/custos/service.py` (editar)
**Esforço:** 2h | **Dependência:** B-03

### Critérios de aceite
- [ ] Margem líquida = receita_total - custo_total
- [ ] ROI% = (margem / custo_total) × 100
- [ ] Retorna no response do resumo da safra

### O que testar
- Safra: receita R$10000, custo R$6000 → margem R$4000, ROI 66.7%
- Safra sem receita → margem negativa

---

## B-08: Comparativo inter-safras

**Arquivo:** `services/api/agricola/custos/router.py` (editar)
**Esforço:** 3h | **Dependência:** B-07

### Critérios de aceite
- [ ] `GET /custos/comparativo?safra_ids=X,Y,Z` → lado a lado
- [ ] Para cada safra: custo/ha, receita/ha, margem, ROI, produtividade
- [ ] Ordenação por safra (ano/cultura)

### O que testar
- Comparar Soja 23/24 vs Soja 24/25 → 2 linhas com métricas
- Safra inexistente → 404

---

## BF-B1 a BF-B4: Frontend Financeiro

| ID | Tarefa | Esforço | Critérios chave |
|----|--------|---------|-----------------|
| BF-B1 | Dashboard unificado | 4h | Custos agrícolas + financeiros na mesma view |
| BF-B2 | Alerta divergência | 2h | Banner vermelho quando custo agrícola ≠ financeiro |
| BF-B3 | UI indicadores | 4h | Margem e ROI exibidos na safra |
| BF-B4 | UI comparativo | 4h | Tabela lado a lado de 2+ safras |

---

# Resumo por Frente

| Frente | Tarefas | Com critérios | Com testes | % completo |
|--------|---------|:-------------:|:----------:|:----------:|
| **C: Propriedade** | 12 | ✅ 12 | ✅ 12 | **100%** |
| **A: Hierarquia** | 30 | ✅ 30 | ✅ 30 | **100%** |
| **B: Custeio** | 12 | ✅ 12 | ✅ 12 | **100%** |
| **TOTAL** | **54** | **✅ 54** | **✅ 54** | **100%** |

> **Nota:** As tarefas de frontend (CF-*, AF-*, BF-*) têm critérios de aceite manuais (teste visual) pois dependem de browser. As tarefas de backend têm critérios automatizáveis via pytest.
