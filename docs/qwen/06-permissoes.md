# AgroSaaS - Permissões e RBAC

**Versão:** 1.0.0  
**Última Atualização:** 2026-03-31  
**Status:** Ativo  

---

## 📋 Índice

1. [Visão Geral](#1-visão-geral)
2. [Backoffice Roles](#2-backoffice-roles)
3. [Tenant Roles](#3-tenant-roles)
4. [Catálogo de Permissões](#4-catálogo-de-permissões)
5. [Feature Gates por Módulo](#5-feature-gates-por-módulo)
6. [Permissões Customizadas](#6-permissões-customizadas)
7. [Hierarquia de Permissões](#7-hierarquia-de-permissões)
8. [Exemplos de Uso](#8-exemplos-de-uso)

---

## 1. Visão Geral

AgroSaaS possui **dois níveis de RBAC**:

1. **Backoffice** - Administradores da plataforma SaaS
2. **Tenant** - Usuários dos assinantes

### Estrutura de Permissões

Formato: `recurso:acao` ou `modulo:recurso:acao`

**Ações:**
- `view` - Visualizar
- `list` - Listar múltiplos
- `create` - Criar
- `update` - Atualizar
- `delete` - Excluir
- `*` - Todas ações

---

## 2. Backoffice Roles

### Roles Disponíveis

| Role | Descrição | Nível |
|------|-----------|-------|
| `super_admin` | Acesso total à plataforma | 5 |
| `admin` | Gestão operacional do SaaS | 4 |
| `suporte` | Suporte técnico | 2 |
| `financeiro` | Gestão financeira e billing | 3 |
| `comercial` | Vendas e CRM | 3 |

### Permissões por Role

#### super_admin

```json
{
  "role": "super_admin",
  "permissions": ["*"]
}
```

**Acesso:** Total e irrestrito a todos recursos.

#### admin

```json
{
  "role": "admin",
  "permissions": [
    "backoffice:dashboard:view",
    "backoffice:bi:view",
    "backoffice:tenants:*",
    "backoffice:plans:*",
    "backoffice:users:view",
    "backoffice:users:toggle_status",
    "backoffice:support:*",
    "backoffice:config:view",
    "backoffice:kb:*",
    "backoffice:profiles:*"
  ]
}
```

**Acesso:**
- ✅ Gerenciar tenants (CRUD completo)
- ✅ Gerenciar planos e assinaturas
- ✅ Visualizar usuários
- ✅ Ativar/desativar usuários
- ✅ Suporte técnico completo
- ✅ Base de conhecimento
- ✅ Perfis de acesso
- ❌ Billing (apenas financeiro)
- ❌ Configurações globais (apenas view)

#### suporte

```json
{
  "role": "suporte",
  "permissions": [
    "backoffice:dashboard:view",
    "backoffice:tenants:view",
    "backoffice:users:view",
    "backoffice:support:*",
    "backoffice:kb:*"
  ]
}
```

**Acesso:**
- ✅ Dashboard e BI (view only)
- ✅ Visualizar tenants e usuários
- ✅ Suporte técnico completo
- ✅ Base de conhecimento
- ❌ Modificar tenants/usuários
- ❌ Planos e billing

#### financeiro

```json
{
  "role": "financeiro",
  "permissions": [
    "backoffice:dashboard:view",
    "backoffice:bi:view",
    "backoffice:billing:*",
    "backoffice:tenants:view",
    "backoffice:plans:view",
    "backoffice:users:view"
  ]
}
```

**Acesso:**
- ✅ Dashboard e BI
- ✅ Billing completo (faturas, cobranças)
- ✅ Visualizar tenants, planos, usuários
- ❌ Modificar tenants/usuários
- ❌ Suporte técnico

#### comercial

```json
{
  "role": "comercial",
  "permissions": [
    "backoffice:dashboard:view",
    "backoffice:plans:*",
    "backoffice:cupons:*",
    "backoffice:tenants:view",
    "backoffice:tenants:assign_plan",
    "backoffice:bi:view"
  ]
}
```

**Acesso:**
- ✅ Dashboard e BI
- ✅ Planos (CRUD completo)
- ✅ Cupons e promoções
- ✅ Visualizar tenants
- ✅ Atribuir planos a tenants
- ❌ Billing e suporte

---

## 3. Tenant Roles

### Roles Disponíveis

| Role | Descrição | Nível |
|------|-----------|-------|
| `owner` | Proprietário da assinatura | 5 |
| `admin` | Administrador do tenant | 4 |
| `gerente` | Gerente de área | 3 |
| `agronomo` | Técnico agrícola | 3 |
| `financeiro` | Gestor financeiro | 3 |
| `operador` | Operador de campo | 2 |
| `consultor` | Consultor externo | 1 |

### Permissões por Role

#### owner

```json
{
  "role": "owner",
  "permissions": ["*"]
}
```

**Acesso:** Total no contexto do tenant (exceto billing do SaaS).

#### admin

```json
{
  "role": "admin",
  "permissions": [
    "tenant:users:*",
    "tenant:permissions:*",
    "tenant:invites:*",
    "tenant:fazendas:*",
    "tenant:grupos:*",
    "tenant:settings:*",
    "tenant:billing:view",
    "tenant:audit:view",
    "agricola:*",
    "pecuaria:*",
    "financeiro:*",
    "operacional:*",
    "rh:*",
    "ambiental:*"
  ]
}
```

**Acesso:**
- ✅ Gestão de equipe (usuários, convites, permissões)
- ✅ Gestão de fazendas e grupos
- ✅ Configurações do tenant
- ✅ Visualizar billing (assinatura)
- ✅ Audit log
- ✅ Todos módulos contratados
- ❌ Billing do SaaS (apenas owner)
- ❌ Excluir tenant

#### gerente

```json
{
  "role": "gerente",
  "permissions": [
    "tenant:users:view",
    "tenant:users:invite",
    "tenant:fazendas:view",
    "tenant:audit:view",
    "agricola:*",
    "pecuaria:view",
    "operacional:view"
  ]
}
```

**Acesso:**
- ✅ Visualizar usuários e convidar
- ✅ Visualizar fazendas
- ✅ Audit log (view)
- ✅ Módulo agrícola completo
- ✅ Módulos pecuária e operacional (view)
- ❌ Financeiro
- ❌ Gestão de equipe avançada

#### agronomo

```json
{
  "role": "agronomo",
  "permissions": [
    "tenant:users:view",
    "tenant:fazendas:view",
    "agricola:*",
    "operacional:view",
    "rh:view"
  ]
}
```

**Acesso:**
- ✅ Módulo agrícola completo
- ✅ Visualizar fazendas e usuários
- ✅ Operacional e RH (view)
- ❌ Financeiro
- ❌ Pecuária (a menos que contratado)
- ❌ Gestão de equipe

#### financeiro

```json
{
  "role": "financeiro",
  "permissions": [
    "tenant:users:view",
    "tenant:fazendas:view",
    "financeiro:*",
    "agricola:custos:view",
    "pecuaria:custos:view",
    "operacional:custos:view"
  ]
}
```

**Acesso:**
- ✅ Módulo financeiro completo
- ✅ Visualizar custos em todos módulos
- ✅ Visualizar fazendas e usuários
- ❌ Operações agrícolas (criar/editar)
- ❌ Gestão de equipe

#### operador

```json
{
  "role": "operador",
  "permissions": [
    "tenant:fazendas:view",
    "agricola:operacoes:*",
    "agricola:defensivos:view",
    "agricola:monitoramento:*",
    "pecuaria:manejo:*",
    "pecuaria:lotes:view",
    "operacional:frota:view",
    "operacional:ordens_servico:*"
  ]
}
```

**Acesso:**
- ✅ Operações de campo (criar/editar)
- ✅ Monitoramento de pragas
- ✅ Manejo de animais
- ✅ Ordens de serviço
- ✅ Visualizar frota e lotes
- ❌ Financeiro
- ❌ Configurações
- ❌ Gestão de equipe

#### consultor

```json
{
  "role": "consultor",
  "permissions": [
    "tenant:fazendas:view",
    "agricola:view",
    "pecuaria:view",
    "financeiro:view",
    "operacional:view"
  ]
}
```

**Acesso:**
- ✅ Apenas leitura em todos módulos
- ✅ Visualizar fazendas
- ❌ Criar/editar/excluir
- ❌ Gestão de equipe

---

## 4. Catálogo de Permissões

### Backoffice

| Permissão | Descrição | Roles |
|-----------|-----------|-------|
| `backoffice:dashboard:view` | Dashboard executivo | admin, suporte, financeiro, comercial |
| `backoffice:bi:view` | Business Intelligence | admin, financeiro, comercial |
| `backoffice:tenants:view` | Listar tenants | admin, suporte, financeiro, comercial |
| `backoffice:tenants:create` | Criar tenant | admin |
| `backoffice:tenants:update` | Atualizar tenant | admin |
| `backoffice:tenants:delete` | Excluir tenant | admin |
| `backoffice:tenants:toggle_status` | Bloquear/desbloquear | admin |
| `backoffice:tenants:assign_plan` | Atribuir plano | admin, comercial |
| `backoffice:plans:view` | Listar planos | admin, financeiro, comercial |
| `backoffice:plans:*` | Gerenciar planos | admin, comercial |
| `backoffice:billing:*` | Billing completo | financeiro |
| `backoffice:users:view` | Listar usuários | admin, suporte, financeiro |
| `backoffice:users:toggle_status` | Ativar/desativar usuário | admin |
| `backoffice:support:*` | Suporte completo | admin, suporte |
| `backoffice:kb:*` | Base de conhecimento | admin, suporte |
| `backoffice:config:view` | Configurações (view) | admin |
| `backoffice:profiles:*` | Perfis de acesso | admin |
| `backoffice:cupons:*` | Cupons | comercial |
| `backoffice:crm:*` | CRM | comercial |
| `backoffice:audit:view` | Audit log | admin |

### Tenant - Core

| Permissão | Descrição | Roles |
|-----------|-----------|-------|
| `tenant:users:view` | Listar usuários | admin, gerente, agronomo, financeiro |
| `tenant:users:create` | Criar usuário | admin |
| `tenant:users:update` | Atualizar usuário | admin |
| `tenant:users:delete` | Excluir usuário | admin |
| `tenant:users:invite` | Enviar convites | admin, gerente |
| `tenant:permissions:*` | Gerenciar permissões | admin |
| `tenant:invites:*` | Gerenciar convites | admin |
| `tenant:fazendas:view` | Listar fazendas | Todos |
| `tenant:fazendas:*` | Gerenciar fazendas | admin |
| `tenant:grupos:*` | Gerenciar grupos | admin |
| `tenant:settings:*` | Configurações do tenant | admin |
| `tenant:billing:view` | Visualizar assinatura | admin, owner |
| `tenant:audit:view` | Audit log | admin, gerente |

### Tenant - Módulo Agrícola

| Permissão | Descrição | Roles |
|-----------|-----------|-------|
| `agricola:safras:view` | Listar safras | admin, gerente, agronomo, operador, consultor |
| `agricola:safras:*` | Gerenciar safras | admin, gerente, agronomo |
| `agricola:talhoes:view` | Listar talhões | Todos |
| `agricola:talhoes:*` | Gerenciar talhões | admin |
| `agricola:operacoes:view` | Listar operações | Todos |
| `agricola:operacoes:*` | Registrar operações | admin, agronomo, operador |
| `agricola:romaneios:view` | Listar romaneios | Todos |
| `agricola:romaneios:*` | Registrar romaneios | admin, agronomo |
| `agricola:monitoramento:view` | Listar monitoramentos | Todos |
| `agricola:monitoramento:*` | Registrar monitoramento | admin, agronomo, operador |
| `agricola:defensivos:view` | Visualizar defensivos | Todos |
| `agricola:analises-solo:view` | Listar análises de solo | Todos |
| `agricola:analises-solo:*` | Criar análises | admin, agronomo |
| `agricola:custos:view` | Visualizar custos | admin, financeiro |
| `agricola:ndvi:view` | NDVI e imagens | admin, agronomo |
| `agricola:climatico:view` | Dados climáticos | Todos |
| `agricola:fenologia:view` | Fenologia | Todos |

### Tenant - Módulo Pecuária

| Permissão | Descrição | Roles |
|-----------|-----------|-------|
| `pecuaria:lotes:view` | Listar lotes | Todos |
| `pecuaria:lotes:*` | Gerenciar lotes | admin, agronomo |
| `pecuaria:animais:view` | Listar animais | Todos |
| `pecuaria:animais:*` | Cadastrar animais | admin, agronomo |
| `pecuaria:manejo:view` | Listar manejos | Todos |
| `pecuaria:manejo:*` | Registrar manejos | admin, agronomo, operador |
| `pecuaria:piquetes:view` | Listar piquetes | Todos |
| `pecuaria:piquetes:*` | Gerenciar piquetes | admin |
| `pecuaria:producao-leite:view` | Produção leiteira | Todos |
| `pecuaria:producao-leite:*` | Registrar produção | admin, operador |
| `pecuaria:custos:view` | Visualizar custos | admin, financeiro |

### Tenant - Módulo Financeiro

| Permissão | Descrição | Roles |
|-----------|-----------|-------|
| `financeiro:receitas:view` | Listar receitas | admin, financeiro |
| `financeiro:receitas:*` | Gerenciar receitas | admin, financeiro |
| `financeiro:despesas:view` | Listar despesas | admin, financeiro |
| `financeiro:despesas:*` | Gerenciar despesas | admin, financeiro |
| `financeiro:planos-conta:view` | Plano de contas | admin, financeiro |
| `financeiro:planos-conta:*` | Gerenciar plano | admin, financeiro |
| `financeiro:rateios:*` | Rateio de custos | admin, financeiro |
| `financeiro:relatorios:view` | Relatórios | admin, financeiro |
| `financeiro:conciliacao:*` | Conciliação bancária | admin, financeiro |

### Tenant - Módulo Operacional

| Permissão | Descrição | Roles |
|-----------|-----------|-------|
| `operacional:frota:view` | Listar frota | Todos |
| `operacional:frota:*` | Gerenciar frota | admin |
| `operacional:estoque:view` | Visualizar estoque | Todos |
| `operacional:estoque:*` | Gerenciar estoque | admin |
| `operacional:movimentacoes:*` | Movimentações | admin, operador |
| `operacional:requisicoes:*` | Requisições | admin, operador |
| `operacional:compras:view` | Listar compras | admin |
| `operacional:compras:*` | Gerenciar compras | admin |
| `operacional:ordens_servico:view` | Listar OS | Todos |
| `operacional:ordens_servico:*` | Gerenciar OS | admin, operador |

### Tenant - Módulo RH

| Permissão | Descrição | Roles |
|-----------|-----------|-------|
| `rh:colaboradores:view` | Listar colaboradores | admin, financeiro |
| `rh:colaboradores:*` | Gerenciar colaboradores | admin |
| `rh:diarias:*` | Lançar diárias | admin, financeiro |
| `rh:empreitadas:*` | Gerenciar empreitadas | admin |
| `rh:departamentos:view` | Departamentos | Todos |

---

## 5. Feature Gates por Módulo

### Módulos e Permissões

Cada módulo requer feature gate específico no backend:

```python
# Exemplo em router
@router.post(
    "/safras",
    dependencies=[Depends(require_module(Modulos.AGRICOLA_PLANEJAMENTO))]
)
async def criar_safra(...):
    ...
```

### Matriz de Módulos

| Módulo | ID | Permissão Base |
|--------|----|----------------|
| Agrícola - Planejamento | A1_PLANEJAMENTO | `agricola:planejamento:*` |
| Agrícola - Campo | A2_CAMPO | `agricola:operacoes:*` |
| Agrícola - Defensivos | A3_DEFENSIVOS | `agricola:defensivos:*` |
| Agrícola - Precisão | A4_PRECISAO | `agricola:precisao:*` |
| Agrícola - Colheita | A5_COLHEITA | `agricola:romaneios:*` |
| Pecuária - Rebanho | P1_REBANHO | `pecuaria:*` |
| Pecuária - Genética | P2_GENETICA | `pecuaria:genetica:*` |
| Pecuária - Leite | P4_LEITE | `pecuaria:leite:*` |
| Financeiro - Tesouraria | F1_TESOURARIA | `financeiro:*` |
| Financeiro - Custos | F2_CUSTOS_ABC | `financeiro:custos:*` |
| Operacional - Frota | O1_FROTA | `operacional:frota:*` |
| Operacional - Estoque | O2_ESTOQUE | `operacional:estoque:*` |
| RH - Remuneração | RH1_REMUNERACAO | `rh:*` |

---

## 6. Permissões Customizadas

### PerfilAcesso com Permissões Customizadas

```json
{
  "nome": "Gerente Agrícola",
  "permissoes": {
    "agricola": "write",
    "pecuaria": "read",
    "financeiro": "none",
    "operacional": "read",
    "rh": "none"
  }
}
```

### Níveis de Permissão

| Nível | Descrição |
|-------|-----------|
| `write` | Leitura e escrita completa |
| `read` | Apenas leitura |
| `none` | Sem acesso |

### Verificação de Permissão Customizada

```python
# core/models/auth.py
class PerfilAcesso:
    permissoes: Mapped[dict] = mapped_column(JSONB)
    
    def has_permission(self, permission: str) -> bool:
        parts = permission.split(":")
        module = parts[0]  # Ex: "agricola"
        action = parts[-1] if len(parts) > 1 else "view"
        
        perm_level = self.permissoes.get(module, "none")
        
        if perm_level == "write" or perm_level == "*":
            return True
        elif perm_level == "read" and action in ["view", "list", "get"]:
            return True
        
        return False
```

---

## 7. Hierarquia de Permissões

### Backoffice Hierarchy

```
super_admin (nível 5)
    └── admin (nível 4)
        ├── financeiro (nível 3)
        ├── comercial (nível 3)
        └── suporte (nível 2)
```

### Tenant Hierarchy

```
owner (nível 5)
    └── admin (nível 4)
        ├── gerente (nível 3)
        ├── agronomo (nível 3)
        ├── financeiro (nível 3)
        ├── operador (nível 2)
        └── consultor (nível 1)
```

### Regras de Hierarquia

1. **Roles de nível superior** herdam permissões de níveis inferiores
2. **Wildcards** (`*`) concedem todas ações do recurso
3. **Permissões explícitas** sempre prevalecem
4. **Negação explícita** não é suportada (allow-only)

---

## 8. Exemplos de Uso

### Backend - Verificar Permissão

```python
# services/api/core/dependencies.py
from fastapi import Depends, HTTPException, status
from core.constants import TenantPermissions

async def require_permission(permission: str):
    async def permission_checker(
        current_user: dict = Depends(get_current_user),
        custom_permissions: dict = Depends(get_custom_permissions),
    ):
        if not TenantPermissions.has_permission(
            current_user["role"],
            permission,
            custom_permissions
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada"
            )
        return current_user
    return permission_checker

# Uso em router
@router.post(
    "/safras",
    dependencies=[
        Depends(require_module(Modulos.AGRICOLA_PLANEJAMENTO)),
        Depends(require_permission("agricola:safras:create"))
    ]
)
async def criar_safra(...):
    ...
```

### Frontend - Hook de Permissão

```typescript
// hooks/use-permission.ts
import { useAppStore } from "@/lib/stores/app-store"
import { TenantPermissions } from "@/lib/permissions"

export function usePermission(permission: string) {
  const { user, customPermissions } = useAppStore()
  
  if (!user) return false
  
  return TenantPermissions.hasPermission(
    user.role,
    permission,
    customPermissions
  )
}

// Uso em componente
function SafrasPage() {
  const canCreate = usePermission("agricola:safras:create")
  const canEdit = usePermission("agricola:safras:update")
  
  return (
    <div>
      <SafrasGrid />
      {canCreate && <Button>Criar Safra</Button>}
    </div>
  )
}
```

### Frontend - Componente com Feature Gate

```typescript
// components/shared/module-gate.tsx
"use client"

import { useHasModule } from "@/hooks/use-has-module"

interface ModuleGateProps {
  module: string
  children: React.ReactNode
  fallback?: React.ReactNode
}

export function ModuleGate({ module, children, fallback }: ModuleGateProps) {
  const hasModule = useHasModule(module)
  
  if (!hasModule) {
    return fallback || <UpgradePrompt module={module} />
  }
  
  return children
}

// Uso
<ModuleGate module="A1_PLANEJAMENTO">
  <PlanejamentoDashboard />
</ModuleGate>
```

### Frontend - Botão Condicional por Permissão

```typescript
// components/agricola/safras-actions.tsx
"use client"

import { usePermission } from "@/hooks/use-permission"

export function SafrasActions({ safra }: { safra: Safra }) {
  const canEdit = usePermission("agricola:safras:update")
  const canDelete = usePermission("agricola:safras:delete")
  
  return (
    <DropdownMenu>
      <DropdownMenuContent>
        {canEdit && (
          <DropdownMenuItem onClick={() => editSafra(safra)}>
            Editar
          </DropdownMenuItem>
        )}
        {canDelete && (
          <DropdownMenuItem 
            onClick={() => deleteSafra(safra)}
            className="text-destructive"
          >
            Excluir
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

---

## Referências Cruzadas

| Documento | Descrição |
|-----------|-----------|
| `docs/qwen/01-arquitetura.md` | Arquitetura geral |
| `docs/qwen/02-modulos.md` | Módulos do sistema |
| `docs/qwen/05-api.md` | API reference |

---

## Changelog

| Data | Versão | Descrição |
|------|--------|-----------|
| 2026-03-31 | 1.0.0 | Documentação inicial completa |
