# 📚 API Reference - RBAC e Multi-Assinatura

## 🎯 Índice

1. [Backoffice - Gestão de Admins](#backoffice---gestão-de-admins)
2. [Team - Gestão de Equipe](#team---gestão-de-equipe)
3. [Grupos de Fazendas](#grupos-de-fazendas)
4. [Autenticação e Permissões](#autenticação-e-permissões)

---

## 🔐 Backoffice - Gestão de Admins

Base URL: `/api/v1/backoffice/admins`

### **GET `/stats`**
Estatísticas de administradores do SaaS.

**Permissão:** `backoffice:admin_users:view`

**Response:**
```json
{
  "total": 12,
  "ativos": 10,
  "super_admins": 2,
  "por_role": {
    "super_admin": 2,
    "admin": 3,
    "suporte": 4,
    "financeiro": 2,
    "comercial": 1
  }
}
```

---

### **GET `/`**
Lista todos os administradores.

**Permissão:** `backoffice:admin_users:view`

**Query Params:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `role` (string, optional): Filtrar por role
- `ativo` (boolean, optional): Filtrar por status

**Response:**
```json
[
  {
    "id": "uuid",
    "email": "admin@agrosaas.com",
    "nome": "João Silva",
    "role": "admin",
    "ativo": true,
    "ultimo_acesso": "2024-03-12T10:30:00Z",
    "timezone": "America/Sao_Paulo",
    "locale": "pt-BR",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-03-12T10:30:00Z"
  }
]
```

---

### **POST `/`**
Cria novo administrador.

**Permissão:** `backoffice:admin_users:create`

**Request Body:**
```json
{
  "email": "novo@agrosaas.com",
  "nome": "Maria Santos",
  "role": "suporte",
  "senha": "senha_segura_123",
  "timezone": "America/Sao_Paulo",
  "locale": "pt-BR"
}
```

**Roles válidas:**
- `super_admin` - Acesso total
- `admin` - Gestão geral
- `suporte` - Atendimento
- `financeiro` - Billing
- `comercial` - Planos e vendas

**Response:** 201 Created
```json
{
  "id": "uuid",
  "email": "novo@agrosaas.com",
  "nome": "Maria Santos",
  ...
}
```

---

### **PATCH `/{admin_id}`**
Atualiza administrador.

**Permissão:** `backoffice:admin_users:update`

**Request Body:**
```json
{
  "nome": "Maria Santos Silva",
  "role": "admin",
  "ativo": true
}
```

---

### **DELETE `/{admin_id}`**
Desativa administrador (soft delete).

**Permissão:** `backoffice:admin_users:delete`

**Restrição:** Não pode desativar `super_admin`

**Response:** 204 No Content

---

### **POST `/{admin_id}/reset-password`**
Reseta senha de um administrador.

**Permissão:** `backoffice:admin_users:update`

**Request Body:**
```json
{
  "nova_senha": "nova_senha_segura_456"
}
```

---

## 👥 Team - Gestão de Equipe

Base URL: `/api/v1/team`

### **GET `/stats`**
Estatísticas da equipe do tenant.

**Permissão:** `tenant:users:view`

**Response:**
```json
{
  "total_membros": 15,
  "ativos": 14,
  "owners": 1,
  "convites_pendentes": 3
}
```

---

### **GET `/users`**
Lista membros da equipe.

**Permissão:** `tenant:users:view`

**Response:**
```json
[
  {
    "id": "tenant_usuario_id",
    "usuario_id": "usuario_id",
    "nome": "João Silva",
    "email": "joao@fazenda.com",
    "perfil": {
      "id": "perfil_id",
      "nome": "Agrônomo",
      "is_custom": false,
      "descricao": "Técnico agrícola (Agricultura completo)"
    },
    "is_owner": false,
    "status": "ATIVO",
    "fazendas": [
      {"id": "fazenda_id", "nome": "Santa Cruz"}
    ],
    "fazendas_com_perfil_especifico": [
      {
        "fazenda_id": "fazenda_id",
        "fazenda_nome": "Boa Vista",
        "perfil_id": "perfil_id",
        "perfil_nome": "Financeiro"
      }
    ],
    "data_cadastro": "2024-01-15T00:00:00Z"
  }
]
```

---

### **POST `/invite`**
Convida novo membro.

**Permissão:** `tenant:users:invite`

**Request Body:**
```json
{
  "email": "novo@exemplo.com",
  "perfil_id": "uuid_perfil",
  "fazendas_ids": ["fazenda1_id", "fazenda2_id"],
  "data_validade_acesso": "2024-12-31"
}
```

**Campos:**
- `fazendas_ids`: vazio = acesso a todas as fazendas
- `data_validade_acesso`: opcional, para prestadores temporários (formato: YYYY-MM-DD)

**Response:** 201 Created
```json
{
  "message": "Convite enviado com sucesso",
  "convite_id": "uuid",
  "token": "token_seguro_para_aceitar"
}
```

---

### **GET `/invites`**
Lista convites pendentes.

**Permissão:** `tenant:users:view`

**Response:**
```json
[
  {
    "id": "uuid",
    "email_convidado": "novo@exemplo.com",
    "perfil": {
      "id": "uuid",
      "nome": "Operador",
      "is_custom": false
    },
    "fazendas": [
      {"id": "fazenda_id", "nome": "Santa Cruz"}
    ],
    "status": "PENDENTE",
    "data_expiracao": "2024-03-19T10:00:00Z",
    "data_validade_acesso": "2024-12-31",
    "created_at": "2024-03-12T10:00:00Z"
  }
]
```

---

### **PATCH `/users/{tenant_usuario_id}/role`**
Altera perfil de um membro.

**Permissão:** `tenant:users:update`

**Request Body:**
```json
{
  "perfil_id": "novo_perfil_uuid"
}
```

**Restrição:** Não pode alterar perfil do `owner`

---

### **DELETE `/users/{tenant_usuario_id}`**
Remove membro da equipe.

**Permissão:** `tenant:users:delete`

**Restrição:** Não pode remover `owner`

**Response:** 204 No Content

---

### **GET `/roles`**
Lista perfis disponíveis (padrão + customizados).

**Permissão:** `tenant:permissions:view`

**Response:**
```json
[
  {
    "id": "uuid",
    "nome": "Owner",
    "is_custom": false,
    "descricao": "Proprietário da assinatura (acesso total)"
  },
  {
    "id": "uuid",
    "nome": "Gerente Regional Sul",
    "is_custom": true,
    "descricao": null
  }
]
```

---

### **POST `/roles`**
Cria perfil customizado.

**Permissão:** `tenant:permissions:create`

**Request Body:**
```json
{
  "nome": "Gerente Financeiro",
  "descricao": "Acesso ao módulo financeiro e visualização de lavoura",
  "permissoes": {
    "agricola": "read",
    "pecuaria": "none",
    "financeiro": "write",
    "operacional": "read"
  }
}
```

**Níveis de permissão:**
- `write` ou `*`: Acesso total (criar, editar, deletar)
- `read`: Apenas leitura
- `none`: Sem acesso

**Response:** 201 Created

---

## 🏘️ Grupos de Fazendas

Base URL: `/api/v1/grupos-fazendas`

### **GET `/`**
Lista grupos de fazendas.

**Permissão:** `tenant:grupos:view`

**Query Params:**
- `include_inactive` (boolean, default: false)

**Response:**
```json
[
  {
    "id": "uuid",
    "nome": "Fazendas Região Sul",
    "descricao": "Grupo de fazendas do sul do estado",
    "cor": "#3B82F6",
    "icone": "MapPin",
    "ordem": 1,
    "ativo": true,
    "total_fazendas": 3,
    "area_total_ha": 1500.5,
    "assinatura": {
      "id": "uuid",
      "plano_nome": "PRO",
      "status": "ATIVA",
      "limite_usuarios": 10,
      "modulos": ["CORE", "A1_PLANEJAMENTO", "F1_TESOURARIA"]
    },
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### **GET `/{grupo_id}`**
Detalhes do grupo com lista de fazendas.

**Permissão:** `tenant:grupos:view`

**Response:**
```json
{
  "id": "uuid",
  "nome": "Fazendas Região Sul",
  ...
  "fazendas": [
    {
      "id": "uuid",
      "nome": "Santa Cruz",
      "area_total_ha": 500.0,
      "ativo": true
    }
  ]
}
```

---

### **POST `/`**
Cria novo grupo.

**Permissão:** `tenant:grupos:create`

**Request Body:**
```json
{
  "nome": "Fazendas Região Norte",
  "descricao": "Grupo de fazendas do norte",
  "cor": "#10B981",
  "icone": "Building2",
  "ordem": 2
}
```

**Response:** 201 Created

---

### **PATCH `/{grupo_id}`**
Atualiza grupo.

**Permissão:** `tenant:grupos:update`

**Request Body:**
```json
{
  "nome": "Fazendas Sul - Atualizado",
  "cor": "#EF4444",
  "ativo": true
}
```

---

### **DELETE `/{grupo_id}`**
Exclui grupo (soft delete).

**Permissão:** `tenant:grupos:delete`

**Restrição:** Não pode excluir grupo com assinatura ativa

**Efeito:** Marca grupo como inativo e remove `grupo_id` das fazendas

**Response:** 204 No Content

---

### **POST `/{grupo_id}/fazendas`**
Adiciona fazendas ao grupo.

**Permissão:** `tenant:grupos:update`

**Request Body:**
```json
{
  "fazendas_ids": ["fazenda1_id", "fazenda2_id", "fazenda3_id"]
}
```

**Response:**
```json
{
  "message": "3 fazendas adicionadas ao grupo"
}
```

---

### **DELETE `/{grupo_id}/fazendas/{fazenda_id}`**
Remove fazenda do grupo.

**Permissão:** `tenant:grupos:update`

**Response:** 204 No Content

---

## 🔒 Autenticação e Permissões

### **Headers Obrigatórios**

```http
Authorization: Bearer <JWT_TOKEN>
x-fazenda-id: <uuid>  # Opcional: contexto de fazenda específica
```

### **Estrutura do JWT**

```json
{
  "sub": "usuario_id",
  "tenant_id": "tenant_id",
  "is_superuser": false,
  "role": "admin",
  "modules": ["CORE", "A1", "F1"],
  "fazendas": [
    {"id": "f1", "role": "gerente"},
    {"id": "f2", "role": "operador"}
  ]
}
```

### **Códigos de Erro Comuns**

| Código | Descrição |
|--------|-----------|
| 401 | Token ausente ou inválido |
| 402 | Módulo não contratado (Payment Required) |
| 403 | Permissão negada |
| 404 | Recurso não encontrado |
| 422 | Regra de negócio violada |
| 429 | Limite de usuários simultâneos atingido |

### **Permissões do Backoffice**

```
backoffice:dashboard:view
backoffice:bi:view
backoffice:tenants:view
backoffice:tenants:create
backoffice:tenants:update
backoffice:tenants:delete
backoffice:plans:view
backoffice:plans:create
backoffice:plans:update
backoffice:billing:view
backoffice:billing:update
backoffice:admin_users:view
backoffice:admin_users:create
backoffice:admin_users:update
backoffice:admin_users:delete
backoffice:support:view
backoffice:support:update
backoffice:config:view
backoffice:config:update
backoffice:impersonate
```

### **Permissões do Tenant**

```
tenant:users:view
tenant:users:invite
tenant:users:update
tenant:users:delete
tenant:permissions:view
tenant:permissions:create
tenant:permissions:update
tenant:fazendas:view
tenant:fazendas:create
tenant:fazendas:update
tenant:grupos:view
tenant:grupos:create
tenant:grupos:update
tenant:grupos:delete
tenant:settings:view
tenant:settings:update
tenant:billing:view
tenant:audit:view
```

### **Permissões por Módulo**

```
agricola:*                 # Todas as operações agrícolas
agricola:operacoes:view
agricola:operacoes:create
agricola:custos:view
pecuaria:*
pecuaria:manejo:create
financeiro:*
financeiro:despesas:create
operacional:*
operacional:frota:view
```

---

## 📝 Exemplos de Uso

### **Criar Admin de Suporte**

```bash
curl -X POST http://localhost:8000/api/v1/backoffice/admins \
  -H "Authorization: Bearer $SUPER_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "suporte@agrosaas.com",
    "nome": "Equipe Suporte",
    "role": "suporte",
    "senha": "senha_forte_123"
  }'
```

### **Convidar Agrônomo para Tenant**

```bash
curl -X POST http://localhost:8000/api/v1/team/invite \
  -H "Authorization: Bearer $TENANT_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "agronomo@exemplo.com",
    "perfil_id": "uuid_perfil_agronomo",
    "fazendas_ids": ["fazenda1_id", "fazenda2_id"]
  }'
```

### **Criar Grupo e Adicionar Fazendas**

```bash
# 1. Criar grupo
GRUPO_ID=$(curl -X POST http://localhost:8000/api/v1/grupos-fazendas \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Região Sul",
    "cor": "#3B82F6"
  }' | jq -r '.id')

# 2. Adicionar fazendas
curl -X POST http://localhost:8000/api/v1/grupos-fazendas/$GRUPO_ID/fazendas \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fazendas_ids": ["faz1", "faz2", "faz3"]
  }'
```

---

## 🎯 Próximos Passos

- [ ] Implementar frontend (React/Next.js)
- [ ] Sistema de notificações por email
- [ ] Controle de sessões simultâneas (FASE 5)
- [ ] Sistema de impersonation (FASE 6)
- [ ] Dashboard de analytics

**Documentação completa:** [IMPLEMENTACAO_RBAC_MULTI_SUB.md](IMPLEMENTACAO_RBAC_MULTI_SUB.md)
