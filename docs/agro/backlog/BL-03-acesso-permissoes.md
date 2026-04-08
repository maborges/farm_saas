# BL-03 — Acesso & Permissões

**Módulo:** core/acesso  
**Frente:** Backend — Controle de Acesso  
**Dependências:** BL-01, BL-02  
**Estimativa:** 3 dias

---

## Contexto

Acesso a cada Propriedade deve ser explícito por usuário.
Vigência opcional (acesso temporário para auditores, consultores, funcionários temporários).

```
AssinaturaUsuario — usuário pertence à assinatura
  └── PropriedadeAcesso — acesso explícito por propriedade
        ├── perfil_id
        └── vigencia_inicio / vigencia_fim (nullable)
```

---

## User Stories

### US-03.1 — Convite de Usuário para Assinatura
**Como** gestor da assinatura,  
**quero** convidar usuários por email para minha assinatura,  
**para** que eles possam acessar as propriedades que eu autorizar.

**Critérios de aceite:**
- [ ] Busca usuário por email na plataforma
- [ ] Se não existe: envia convite de cadastro + link de acesso
- [ ] Se existe: envia convite de acesso direto
- [ ] Convite tem validade de 7 dias
- [ ] Status do convite: `pendente | aceito | expirado | cancelado`
- [ ] Gestor pode cancelar convite pendente

---

### US-03.2 — Acesso Explícito por Propriedade
**Como** gestor da assinatura,  
**quero** definir quais propriedades cada usuário pode acessar,  
**para** garantir isolamento de informações entre propriedades.

**Critérios de aceite:**
- [ ] Acesso a cada Propriedade é explícito (opt-in, nunca automático)
- [ ] Perfil por propriedade (pode ser diferente por propriedade)
- [ ] Vigência opcional: `vigencia_inicio` e `vigencia_fim`
- [ ] Gestor pode revogar acesso a qualquer momento
- [ ] `is_gestor` tem acesso implícito a todas as propriedades da assinatura

---

### US-03.3 — Acesso Temporário
**Como** gestor da assinatura,  
**quero** conceder acesso com prazo definido,  
**para** atender auditores fiscais, consultores e funcionários temporários.

**Critérios de aceite:**
- [ ] `vigencia_fim` define expiração automática
- [ ] Sistema nega acesso após `vigencia_fim` mesmo com JWT válido
- [ ] Notificação ao gestor 3 dias antes da expiração
- [ ] Usuário vê aviso de "acesso expira em X dias"

---

### US-03.4 — Gestão de Equipe
**Como** gestor,  
**quero** visualizar todos os usuários e seus acessos,  
**para** auditar e controlar quem acessa o quê.

**Critérios de aceite:**
- [ ] Lista usuários com perfil global + propriedades com acesso
- [ ] Indica acessos temporários com data de expiração
- [ ] Filtra por propriedade
- [ ] Exporta lista de acessos (CSV)

---

## Tarefas Técnicas

### Backend
- [ ] Model `AssinaturaUsuario` — usuario_id, assinatura_id, perfil_id, is_gestor, convite_aceito_em
- [ ] Model `PropriedadeAcesso` — usuario_id, assinatura_id, propriedade_id, perfil_id, vigencia_inicio, vigencia_fim
- [ ] Model `ConviteUsuario` — email, assinatura_id, token, status, expira_em
- [ ] Migration para os 3 models
- [ ] `require_propriedade_access()` dependency — verifica acesso explícito + vigência
- [ ] Verificação de vigência em runtime (não depende do JWT)
- [ ] Router `equipe` — CRUD de AssinaturaUsuario
- [ ] Router `convites` — create/accept/cancel
- [ ] Router `propriedade-acessos` — CRUD de PropriedadeAcesso
- [ ] Job/task: notificar gestor 3 dias antes de expiração
- [ ] Índices: `(usuario_id, assinatura_id)`, `(vigencia_fim)` para expiração

### Schemas
- [ ] `ConviteSchema`
- [ ] `AssinaturaUsuarioSchema`
- [ ] `PropriedadeAcessoSchema`
