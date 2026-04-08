# BL-02 — Território (Propriedade / Gleba / Unidade Operacional)

**Módulo:** core/territorio  
**Frente:** Backend — Modelos & Migrations  
**Dependências:** BL-01 (Assinatura/tenant_id)  
**Estimativa:** 4 dias

---

## Contexto

Hierarquia territorial flexível:
```
Propriedade (obrigatório, conta no limite do plano)
  └── Gleba (opcional)
        └── UnidadeOperacional: Talhão | Piquete | ÁreaFuncional (opcional)
```

Refatoração limpa: `fazendas` → `propriedades`, `talhoes` e `piquetes` → `unidades_operacionais`.

---

## User Stories

### US-02.1 — Cadastro de Propriedade
**Como** gestor da assinatura,  
**quero** cadastrar minhas propriedades rurais (fazenda, sítio, arrendamento),  
**para** organizar a estrutura produtiva do produtor.

**Critérios de aceite:**
- [ ] Tipos: `fazenda | sitio | chacara | arrendamento | parceria`
- [ ] Campos: nome, área total (Decimal ha), tipo_posse
- [ ] Localização: CEP → preenche município/UF/IBGE automaticamente
- [ ] Identificadores regulatórios: `car_codigo`, `nirf`, `ccir`, `sigef_codigo`, `cif_mapa`
- [ ] Limite do plano validado ao criar (`check_propriedade_limit`)
- [ ] `ativo: bool` para desativação sem exclusão

---

### US-02.2 — Cadastro de Gleba (opcional)
**Como** gerente de fazenda,  
**quero** subdividir minha propriedade em glebas,  
**para** organizar áreas com características distintas de solo/topografia.

**Critérios de aceite:**
- [ ] Vinculada a uma Propriedade
- [ ] Campos: nome, área (Decimal ha), tipo_solo, topografia, observações
- [ ] Opcional — propriedade sem gleba é válida

---

### US-02.3 — Cadastro de Unidade Operacional
**Como** gerente de fazenda,  
**quero** cadastrar talhões, piquetes e áreas funcionais,  
**para** planejar e registrar operações no nível correto.

**Critérios de aceite:**
- [ ] Tipos: `talhao | piquete | area_funcional`
- [ ] Vinculado a Gleba (se existir) ou diretamente à Propriedade
- [ ] **Talhão:** cultura_atual, variedade, sistema_plantio, data_ultimo_plantio
- [ ] **Piquete:** capacidade_ua (Decimal), tipo_pastagem, sistema_pastejo
- [ ] **Área Funcional:** subtipo (reserva_legal | app | sede | estrada | curral | açude | outros)
- [ ] geojson opcional (polígono)

---

### US-02.4 — Visualização em Árvore
**Como** usuário,  
**quero** ver a hierarquia territorial em formato de árvore,  
**para** navegar e gerenciar a estrutura da propriedade.

**Critérios de aceite:**
- [ ] API retorna árvore aninhada: Propriedade → Glebas → Unidades
- [ ] Filtro por `propriedade_id`
- [ ] Componente `AreaTree` reutilizado (já existe)

---

## Tarefas Técnicas

### Backend
- [ ] Model `Propriedade` com todos os campos mapeados
- [ ] Model `Gleba` com FK `propriedade_id`
- [ ] Model `UnidadeOperacional` com FK `gleba_id` (nullable) + `propriedade_id` (fallback)
- [ ] Migration: drop `fazendas`, criar `propriedades`, `glebas`, `unidades_operacionais`
- [ ] `PropriedadeService(BaseService[Propriedade])`
- [ ] `GlebaService(BaseService[Gleba])`
- [ ] `UnidadeOperacionalService(BaseService[UnidadeOperacional])`
- [ ] Router `propriedades` — CRUD completo
- [ ] Router `glebas` — CRUD completo
- [ ] Router `unidades_operacionais` — CRUD completo
- [ ] Endpoint `GET /propriedades/{id}/arvore` — retorna árvore aninhada
- [ ] Índices: `(tenant_id)`, `(propriedade_id, tenant_id)`, `(tipo, propriedade_id)`
- [ ] Testes de isolamento de tenant para cada router

### Schemas
- [ ] `PropriedadeSchema` — create/update/public/tree
- [ ] `GlebaSchema`
- [ ] `UnidadeOperacionalSchema` com discriminated union por tipo
- [ ] `AreaRuralTree` — já existe, verificar compatibilidade
