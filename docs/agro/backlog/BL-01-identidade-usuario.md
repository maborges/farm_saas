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
- [ ] Criar/refatorar model `Usuario` — CPF, email únicos globais
- [ ] Criar model `Assinatura` — tenant_id, usuario_id, plano_id, status, vigencia
- [ ] Migration: `usuarios` e `assinaturas`
- [ ] Validação CPF (algoritmo) no Pydantic schema
- [ ] Endpoint `POST /auth/register` — cria usuário
- [ ] Endpoint `POST /assinaturas` — cria assinatura/produtor
- [ ] Atualizar geração de JWT para incluir `assinatura_id` como `tenant_id`
- [ ] Teste de isolamento: usuário não acessa dados de assinatura que não pertence

### Schemas (packages/zod-schemas)
- [ ] `UsuarioCreateSchema`, `UsuarioPublicSchema`
- [ ] `AssinaturaCreateSchema`, `AssinaturaPublicSchema`
