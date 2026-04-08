# BL-01 — Identidade & Usuário

**Módulo:** core/auth  
**Frente:** Backend — Modelos & Migrations  
**Dependências:** nenhuma (fundação)  
**Estimativa:** 3 dias

---

## Contexto

Refatoração do modelo de usuário para suportar identidade global na plataforma.
Um usuário pertence à plataforma (CPF/email únicos), não a um tenant.
Assinatura = Tenant = Produtor.

---

## User Stories

### US-01.1 — Cadastro de Usuário na Plataforma
**Como** visitante,  
**quero** criar uma conta com CPF/email únicos,  
**para** acessar a plataforma como usuário.

**Critérios de aceite:**
- [ ] CPF validado (formato + dígitos verificadores)
- [ ] Email único globalmente
- [ ] CPF único globalmente
- [ ] Senha com hash bcrypt
- [ ] Status: `pendente_confirmacao | ativo | suspenso | inativo`
- [ ] Email de confirmação enviado ao cadastrar

---

### US-01.2 — Criação de Assinatura (Produtor)
**Como** usuário da plataforma,  
**quero** criar uma assinatura vinculada a um Produtor (PF ou PJ),  
**para** gerenciar minhas propriedades rurais.

**Critérios de aceite:**
- [ ] Tipo de pessoa: `PF | PJ`
- [ ] CPF/CNPJ validado via API Receita Federal
- [ ] Nome/razão social preenchido automaticamente
- [ ] Plano selecionado no ato da criação
- [ ] `tenant_id` gerado = `assinatura.id`
- [ ] Usuário criador vira `is_gestor = true` automaticamente

---

### US-01.3 — Multi-assinatura por Usuário
**Como** consultor rural,  
**quero** ter acesso a múltiplas assinaturas (produtores),  
**para** gerenciar vários clientes com dados isolados.

**Critérios de aceite:**
- [ ] `tenant-switcher` lista assinaturas ativas do usuário
- [ ] Troca de contexto reemite JWT com novo `tenant_id`
- [ ] Dados completamente isolados entre assinaturas

---

## Tarefas Técnicas

### Backend
- [x] Model `Usuario` — adicionados `cpf` (unique) e `telefone` — `core/models/auth.py`
- [x] Migration `f58b4e673940_add_cpf_telefone_to_usuarios` — aplicada
- [x] Schemas atualizados: `UsuarioMeResponse`, `UserCreateRequest`, `UserUpdateRequest` — `core/schemas/auth_schemas.py`
- [x] `Assinatura` = `Tenant` (já existe) — modelo validado
- [x] `AssinaturaUsuario` = `TenantUsuario` (já existe com vigência) — modelo validado
- [x] `ConviteAcesso` (já existe) — modelo validado
- [ ] Validação CPF (algoritmo) no Pydantic schema — `UserCreateRequest`
- [ ] Endpoint `PUT /auth/me` — atualiza perfil (usa `UserUpdateRequest`)
- [ ] Teste: CPF duplicado → 422

### Schemas (packages/zod-schemas)
- [ ] `UsuarioCreateSchema` — adicionar `cpf`, `telefone`
- [ ] `UsuarioPublicSchema` — adicionar `cpf`, `telefone`
