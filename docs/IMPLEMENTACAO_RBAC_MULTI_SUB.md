# 🚀 Implementação RBAC e Multi-Assinatura - AgroSaaS

## 📋 Resumo Executivo

Este documento descreve as implementações realizadas para suportar:
1. **Multi-assinatura** por tenant (múltiplas assinaturas simultâneas)
2. **Grupos de fazendas** com assinaturas dedicadas
3. **RBAC completo** (Role-Based Access Control) em dois níveis:
   - Backoffice (Admins do SaaS)
   - Tenant (Usuários do assinante)
4. **Perfis por fazenda** (usuário com roles diferentes por fazenda)
5. **Controle de sessões simultâneas**
6. **Sistema de impersonation** (admin → assinante)

---

## ✅ FASE 1: MODELO DE DADOS - CONCLUÍDA

### 📁 Novos Arquivos Criados

#### 1. `/services/api/core/models/grupo_fazendas.py`
**Propósito:** Permite agrupar fazendas para compartilhar uma assinatura

**Campos principais:**
- `tenant_id` - Proprietário do grupo
- `nome` - Nome do grupo (ex: "Fazendas Região Sul")
- `cor` / `icone` - Personalização visual
- `ativo` - Status do grupo

**Caso de uso:**
```
Tenant "Agro Corp" tem:
  - Grupo "Sul" (3 fazendas) → Assinatura PRO (10 usuários)
  - Grupo "Norte" (2 fazendas) → Assinatura BASIC (5 usuários)
  - Fazenda "Sede" (sem grupo) → Assinatura ENTERPRISE
```

---

#### 2. `/services/api/core/models/sessao.py`
**Propósito:** Controle de usuários simultâneos (limit enforcement)

**Campos principais:**
- `tenant_id` / `grupo_fazendas_id` - Contexto da sessão
- `usuario_id` - Usuário logado
- `token_hash` - SHA256 do JWT (identificação única)
- `ultimo_heartbeat` - Última atividade
- `expira_em` - Expiração automática (30min inativo)
- `status` - ATIVA, EXPIRADA, ENCERRADA

**Lógica:**
1. Ao fazer login, cria uma sessão
2. A cada requisição, atualiza `ultimo_heartbeat`
3. Valida limite: `count(sessoes_ativas) <= plano.limite_usuarios`
4. Se atingir limite, retorna HTTP 429 (Too Many Requests)

---

#### 3. `/services/api/core/models/admin_impersonation.py`
**Propósito:** Log de quando admin do SaaS acessa conta de assinante

**Campos principais:**
- `admin_user_id` - Admin que fez impersonation
- `tenant_id` / `fazenda_id` - Contexto acessado
- `motivo` - Justificativa obrigatória
- `categoria` - SUPORTE, AUDITORIA, DEMONSTRACAO, etc.
- `acoes_realizadas` - JSON array com log de ações
- `inicio` / `fim` - Duração do acesso

**Segurança:**
- Requer permissão `backoffice:impersonate`
- Motivo obrigatório
- Auditável e rastreável

---

### 📝 Arquivos Modificados

#### 4. `/services/api/core/models/fazenda.py`
**Mudança:** Adicionado campo `grupo_id`

```python
grupo_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("grupos_fazendas.id", ondelete="SET NULL"),
    nullable=True
)
```

**Permite:** Associar fazenda a um grupo

---

#### 5. `/services/api/core/models/billing.py`
**Mudanças:**
1. **Removido `unique=True`** de `tenant_id` → Permite múltiplas assinaturas
2. **Adicionado `grupo_fazendas_id`** → Assinatura específica por grupo
3. **Adicionado `tipo_assinatura`** → PRINCIPAL, GRUPO, ADICIONAL

```python
# ANTES (bloqueava múltiplas assinaturas):
tenant_id: Mapped[uuid.UUID] = mapped_column(..., unique=True)  # ❌

# DEPOIS (permite múltiplas):
tenant_id: Mapped[uuid.UUID] = mapped_column(..., index=True)  # ✅

grupo_fazendas_id: Mapped[uuid.UUID | None] = ...  # ✅ NOVO
tipo_assinatura: Mapped[str] = ...  # ✅ NOVO
```

**Permite:**
- Tenant ter assinatura PRINCIPAL (todas as fazendas)
- Tenant ter assinatura GRUPO_A (fazendas do grupo A)
- Tenant ter assinatura GRUPO_B (fazendas do grupo B)

---

#### 6. `/services/api/core/models/auth.py`
**Mudança:** Adicionado `perfil_fazenda_id` em `FazendaUsuario`

```python
perfil_fazenda_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("perfis_acesso.id", ondelete="SET NULL"),
    nullable=True,
    comment="Sobrescreve o perfil do TenantUsuario para esta fazenda"
)
```

**Permite:** Usuário ter perfil diferente por fazenda
- João: "financeiro" na Fazenda A, "agrônomo" na Fazenda B

---

### 🔐 Sistema de Permissões

#### 7. `/services/api/core/constants.py`
**Adicionadas 3 classes:**

##### A. `BackofficePermissions`
Permissões dos admins do SaaS (backoffice)

```python
PERMISSIONS_MAP = {
    "super_admin": ["*"],
    "admin": [
        "backoffice:dashboard:view",
        "backoffice:tenants:*",
        "backoffice:plans:*",
        ...
    ],
    "suporte": [
        "backoffice:support:*",
        "backoffice:tenants:view",
        ...
    ],
    "financeiro": [
        "backoffice:billing:*",
        ...
    ],
    "comercial": [
        "backoffice:plans:*",
        "backoffice:cupons:*",
        ...
    ]
}
```

##### B. `TenantRoles`
Perfis padrão para usuários de tenants

```python
OWNER = "owner"           # Acesso total
ADMIN = "admin"           # Gestão completa (exceto billing)
GERENTE = "gerente"       # Módulos específicos
AGRONOMO = "agronomo"     # Agricultura completo
OPERADOR = "operador"     # Apontamentos
CONSULTOR = "consultor"   # Apenas leitura
FINANCEIRO = "financeiro" # Módulo financeiro
```

##### C. `TenantPermissions`
Mapeamento de permissões por perfil

```python
PERMISSIONS_MAP = {
    "owner": ["*"],
    "admin": [
        "tenant:users:*",
        "tenant:fazendas:*",
        "agricola:*",
        "pecuaria:*",
        ...
    ],
    "agronomo": [
        "agricola:*",
        "operacional:view",
        ...
    ],
    ...
}
```

**Método principal:**
```python
TenantPermissions.has_permission(
    role="agronomo",
    permission="agricola:operacoes:create",
    custom_permissions=None  # ou {"agricola": "write"}
)
```

---

#### 8. `/services/api/core/dependencies.py`
**Atualizadas 2 funções:**

##### A. `require_permission(permissao: str)` - ATUALIZADA
Para backoffice (admins do SaaS)

```python
@router.get("/tenants", dependencies=[Depends(require_permission("backoffice:tenants:view"))])
@router.post("/plans", dependencies=[Depends(require_permission("backoffice:plans:create"))])
```

**Lógica:**
1. Verifica se é `is_superuser` → permite tudo
2. Busca `AdminUser` no banco
3. Usa `BackofficePermissions.has_permission(role, permissao)`
4. Se não tem, retorna HTTP 403

##### B. `require_tenant_permission(permission: str)` - NOVA
Para assinantes (usuários do tenant)

```python
@router.get("/team/users", dependencies=[Depends(require_tenant_permission("tenant:users:view"))])
@router.post("/team/invite", dependencies=[Depends(require_tenant_permission("tenant:users:invite"))])
```

**Lógica:**
1. Busca `TenantUsuario` + `PerfilAcesso`
2. Se é `is_owner` → permite tudo
3. Verifica `x-fazenda-id` header → busca `FazendaUsuario.perfil_fazenda_id` (override)
4. Usa `TenantPermissions.has_permission(role, permission, custom_perms)`
5. Se não tem, retorna HTTP 403

---

### 🗄️ Migration

#### 9. `/services/api/migrations/versions/20240312_multi_subscription_rbac.py`

**Execução:**
```bash
cd /opt/lampp/htdocs/farm/services/api
alembic upgrade head
```

**Alterações no banco:**
1. `CREATE TABLE grupos_fazendas`
2. `ALTER TABLE fazendas ADD grupo_id`
3. `ALTER TABLE assinaturas_tenant DROP CONSTRAINT unique(tenant_id)`
4. `ALTER TABLE assinaturas_tenant ADD grupo_fazendas_id, tipo_assinatura`
5. `ALTER TABLE fazenda_usuarios ADD perfil_fazenda_id`
6. `CREATE TABLE sessoes_ativas`
7. `CREATE TABLE admin_impersonations`

---

## 📊 DIAGRAMA DE ARQUITETURA

```
┌─────────────────────────────────────────────────────────────────┐
│                    TENANT COM MULTI-ASSINATURA                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Tenant "Agro Corp S.A."                                        │
│   │                                                             │
│   ├─── AssinaturaTenant (PRINCIPAL) ──> Plano ENTERPRISE       │
│   │        tipo: "PRINCIPAL"                                    │
│   │        grupo_id: NULL                                       │
│   │        limite_usuarios: 50                                  │
│   │        módulos: [CORE, A1, A2, F1, F2, P1, O1]             │
│   │                                                             │
│   ├─── GrupoFazendas "Região Sul"                              │
│   │        ├─> Fazenda "Santa Cruz"   (grupo_id: Sul)          │
│   │        ├─> Fazenda "Boa Vista"    (grupo_id: Sul)          │
│   │        └─> Fazenda "Campo Verde"  (grupo_id: Sul)          │
│   │                                                             │
│   ├─── AssinaturaTenant (GRUPO) ──> Plano PRO                  │
│   │        tipo: "GRUPO"                                        │
│   │        grupo_id: "Região Sul"                               │
│   │        limite_usuarios: 10                                  │
│   │        módulos: [CORE, A1, F1]                              │
│   │                                                             │
│   ├─── GrupoFazendas "Região Norte"                            │
│   │        ├─> Fazenda "Pantanal"     (grupo_id: Norte)        │
│   │        └─> Fazenda "Cerrado Alto" (grupo_id: Norte)        │
│   │                                                             │
│   └─── AssinaturaTenant (GRUPO) ──> Plano BASIC                │
│            tipo: "GRUPO"                                        │
│            grupo_id: "Região Norte"                             │
│            limite_usuarios: 5                                   │
│            módulos: [CORE, P1]                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              USUÁRIO COM PERFIS POR FAZENDA                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Usuario "João Silva"                                           │
│   │                                                             │
│   ├─── TenantUsuario ──> Tenant "Agro Corp"                    │
│   │        perfil_id: "admin"  (perfil global no tenant)       │
│   │        is_owner: false                                      │
│   │                                                             │
│   ├─── FazendaUsuario ──> Fazenda "Santa Cruz"                 │
│   │        perfil_fazenda_id: "financeiro" (sobrescreve!)      │
│   │        → João é "financeiro" nesta fazenda                  │
│   │                                                             │
│   └─── FazendaUsuario ──> Fazenda "Pantanal"                   │
│            perfil_fazenda_id: "agronomo" (sobrescreve!)        │
│            → João é "agrônomo" nesta fazenda                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 PRÓXIMAS FASES

### FASE 2: Permissões Granulares no Backoffice ⏳

**Tarefas:**
- [ ] Atualizar todas as rotas do backoffice com `require_permission()`
- [ ] Criar página `/backoffice/admin-users` (gestão de admins)
- [ ] Atualizar sidebar para mostrar menus baseado em permissões
- [ ] Criar seed de AdminUsers com diferentes roles

**Exemplo de implementação:**
```python
# ANTES:
@router.get("/tenants", dependencies=[Depends(get_current_admin)])

# DEPOIS:
@router.get("/tenants", dependencies=[Depends(require_permission("backoffice:tenants:view"))])
```

---

### FASE 3: Gestão de Equipe do Assinante ⏳

**Tarefas:**
- [ ] Criar router `/team/*` (listar, convidar, editar, remover usuários)
- [ ] Criar página `/settings/team` (frontend)
- [ ] Criar página `/settings/roles` (gestão de perfis customizados)
- [ ] Criar página `/settings/invites` (convites pendentes)
- [ ] Implementar envio de e-mail de convite

**Endpoints a criar:**
```python
GET    /team/users              # Listar equipe
POST   /team/invite             # Convidar novo membro
PATCH  /team/users/{id}/role    # Alterar perfil
DELETE /team/users/{id}         # Remover membro
GET    /team/invites            # Convites pendentes
POST   /team/invites/{id}/resend # Reenviar convite
DELETE /team/invites/{id}       # Cancelar convite
```

---

### FASE 4: Grupos de Fazendas (CRUD e UI) ⏳

**Tarefas:**
- [ ] Criar router `/grupos-fazendas/*`
- [ ] Criar página `/settings/grupos` (frontend)
- [ ] UI para criar/editar grupos
- [ ] Associar fazendas a grupos (drag-and-drop)
- [ ] Dashboard de consumo por grupo

---

### FASE 5: Controle de Sessões Simultâneas ⏳

**Tarefas:**
- [ ] Middleware de validação de limite (`validate_concurrent_users()`)
- [ ] Endpoint de heartbeat (`/session/heartbeat`)
- [ ] Cronjob de limpeza de sessões expiradas
- [ ] Endpoint `/session/active` (listar sessões ativas)
- [ ] UI para encerrar sessões remotamente

---

### FASE 6: Sistema de Impersonation ⏳

**Tarefas:**
- [ ] Endpoint `POST /backoffice/impersonate`
- [ ] Endpoint `POST /backoffice/impersonate/end`
- [ ] UI: Seletor de tenant/fazenda no backoffice
- [ ] Banner visual indicando modo impersonation
- [ ] Log automático de todas as ações

---

## 🔧 COMO APLICAR AS MUDANÇAS

### 1. Executar Migration

```bash
cd /opt/lampp/htdocs/farm/services/api

# Criar backup do banco (IMPORTANTE!)
sqlite3 agrosaas.db ".backup agrosaas_backup_$(date +%Y%m%d).db"

# Executar migration
alembic upgrade head

# Verificar se foi aplicada
alembic current
```

### 2. Criar Perfis Padrão (Seed)

```bash
cd /opt/lampp/htdocs/farm/services/api
python scripts/seed_perfis_acesso.py
```

**Criar o arquivo** `scripts/seed_perfis_acesso.py`:
```python
import asyncio
from core.database import async_session_maker
from core.models.auth import PerfilAcesso
from core.constants import TenantRoles, TenantPermissions

async def seed_perfis():
    async with async_session_maker() as session:
        # Criar perfis padrão (tenant_id=NULL = global)
        perfis = [
            PerfilAcesso(
                nome="Owner",
                is_custom=False,
                permissoes={"*": "*"}
            ),
            PerfilAcesso(
                nome="Admin",
                is_custom=False,
                permissoes={k: "write" for k in ["agricola", "pecuaria", "financeiro", "operacional"]}
            ),
            PerfilAcesso(
                nome="Agrônomo",
                is_custom=False,
                permissoes={"agricola": "write", "operacional": "read"}
            ),
            # ... adicionar outros perfis
        ]
        session.add_all(perfis)
        await session.commit()
        print(f"✅ {len(perfis)} perfis padrão criados")

if __name__ == "__main__":
    asyncio.run(seed_perfis())
```

### 3. Testar as Permissões

```bash
# Testar endpoint com permissão
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/backoffice/tenants

# Deve retornar 403 se não tiver permissão
# Deve retornar 200 se tiver permissão
```

---

## 📚 REFERÊNCIAS

### Modelos de Dados
- [grupo_fazendas.py](services/api/core/models/grupo_fazendas.py)
- [sessao.py](services/api/core/models/sessao.py)
- [admin_impersonation.py](services/api/core/models/admin_impersonation.py)
- [auth.py](services/api/core/models/auth.py)
- [billing.py](services/api/core/models/billing.py)
- [fazenda.py](services/api/core/models/fazenda.py)

### Permissões
- [constants.py](services/api/core/constants.py)
- [dependencies.py](services/api/core/dependencies.py)

### Migration
- [20240312_multi_subscription_rbac.py](services/api/migrations/versions/20240312_multi_subscription_rbac.py)

---

## 🎉 CONCLUSÃO

A **FASE 1** está **100% completa** e pronta para uso. O modelo de dados foi completamente reestruturado para suportar:

✅ Multi-assinatura por tenant
✅ Grupos de fazendas
✅ RBAC em dois níveis (Backoffice + Tenant)
✅ Perfis por fazenda
✅ Controle de sessões simultâneas
✅ Sistema de impersonation

As próximas fases implementarão os endpoints, UI e lógica de negócio para utilizar toda essa infraestrutura.

**Autor:** Claude Code (Anthropic)
**Data:** 12/03/2024
**Versão:** 1.0
