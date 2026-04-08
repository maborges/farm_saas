# BL-07 — Segurança (Gaps da Refatoração)

**Módulo:** core/security  
**Frente:** Backend — Segurança  
**Dependências:** BL-01, BL-02, BL-03  
**Estimativa:** 2 dias

---

## Contexto

A base de segurança existente é sólida (BaseService, RLS, JWT, TenantViolationError).
Esta sprint cobre os gaps específicos introduzidos pela refatoração.

---

## Tarefas Técnicas

### Gap 1 — `require_propriedade_access()` dependency

Nova dependency para verificar acesso explícito do usuário à Propriedade.

- [ ] Implementar `require_propriedade_access(propriedade_id)` em `dependencies.py`
- [ ] Consulta `PropriedadeAcesso` com `usuario_id + propriedade_id + tenant_id`
- [ ] Verifica `vigencia_fim >= today` (ou NULL)
- [ ] `is_gestor` bypass — gestor sempre tem acesso
- [ ] Retorna 403 com mensagem clara se sem acesso
- [ ] Aplicar em todos os endpoints que recebem `propriedade_id`

---

### Gap 2 — `check_propriedade_limit()` no service

- [ ] Implementar em `PropriedadeService.create()`
- [ ] Conta `propriedades` ativas do tenant
- [ ] Compara com `plano.max_propriedades`
- [ ] Lança `BusinessRuleError` (422) se limite atingido
- [ ] Teste: criar propriedade além do limite → 422

---

### Gap 3 — Verificação de vigência em runtime

- [ ] Middleware ou dependency verifica `PropriedadeAcesso.vigencia_fim`
- [ ] Não depende do JWT (token ainda pode ser válido após expiração do acesso)
- [ ] Cache TTL curto (5 min) para evitar query por request
- [ ] Teste: acesso com vigência expirada → 403

---

### Gap 4 — Atualizar `_resolve_grupo_id`

- [ ] Substituir import `Fazenda` por `Propriedade` em `dependencies.py` linha ~197
- [ ] Atualizar header `X-Fazenda-Id` → `X-Propriedade-Id` (ou manter alias para compatibilidade)
- [ ] Verificar todos os routers que usam o header

---

### Gap 5 — RLS para novas tabelas

- [ ] Política RLS para `propriedades`
- [ ] Política RLS para `glebas`
- [ ] Política RLS para `unidades_operacionais`
- [ ] Política RLS para `propriedade_acessos`
- [ ] Teste de isolamento: tenant A não vê dados do tenant B

---

### Gap 6 — Teste de Isolamento de Tenant (obrigatório por endpoint)

- [ ] `PropriedadeService` — teste de isolamento
- [ ] `GlebaService` — teste de isolamento
- [ ] `UnidadeOperacionalService` — teste de isolamento
- [ ] `PropriedadeAcessoService` — teste de isolamento
- [ ] Padrão: criar dados em tenant A, autenticar como tenant B, verificar 404/403
