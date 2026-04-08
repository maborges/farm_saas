# 🎨 Guia de Manutenção do Frontend

## 📋 Status da Migration

⚠️ **ATENÇÃO:** A migration foi parcialmente aplicada. Algumas colunas já existem no banco de dados.

**Tabelas criadas:**
- ✅ `grupos_fazendas` (criada manualmente)
- ✅ `sessoes_ativas` (criada manualmente)
- ✅ `admin_impersonations` (criada manualmente)

**Colunas adicionadas:**
- ✅ `fazendas.grupo_id` (já existe)
- ⚠️ `assinaturas_tenant.grupo_fazendas_id` (precisa verificar)
- ⚠️ `assinaturas_tenant.tipo_assinatura` (precisa verificar)
- ⚠️ `fazenda_usuarios.perfil_fazenda_id` (precisa verificar)

---

## 🆕 PÁGINAS QUE PRECISAM SER CRIADAS

### **1. Backoffice - Gestão de Admins**

**Caminho:** `/apps/web/src/app/(dashboard)/backoffice/admin-users/page.tsx`

**Funcionalidades:**
- Listar administradores do SaaS
- Criar novo admin
- Editar admin (nome, role, status)
- Resetar senha
- Ver estatísticas (total, por role, ativos)

**API Endpoints:**
```typescript
GET    /api/v1/backoffice/admins/stats
GET    /api/v1/backoffice/admins
POST   /api/v1/backoffice/admins
PATCH  /api/v1/backoffice/admins/{id}
DELETE /api/v1/backoffice/admins/{id}
POST   /api/v1/backoffice/admins/{id}/reset-password
```

**Componentes sugeridos:**
- `AdminUsersTable` - Tabela de admins
- `CreateAdminDialog` - Modal de criação
- `EditAdminDialog` - Modal de edição
- `AdminStatsCards` - Cards de estatísticas

**Exemplo de estrutura:**
```typescript
// page.tsx
export default function AdminUsersPage() {
  const [admins, setAdmins] = useState([]);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch('/api/v1/backoffice/admins/stats')
      .then(r => r.json())
      .then(setStats);

    fetch('/api/v1/backoffice/admins')
      .then(r => r.json())
      .then(setAdmins);
  }, []);

  return (
    <div>
      <AdminStatsCards data={stats} />
      <AdminUsersTable data={admins} />
    </div>
  );
}
```

---

### **2. Settings - Gestão de Equipe**

**Caminho:** `/apps/web/src/app/(dashboard)/settings/team/page.tsx`

**Funcionalidades:**
- Listar membros da equipe
- Convidar novo membro
- Alterar perfil de membro
- Remover membro
- Ver convites pendentes

**API Endpoints:**
```typescript
GET    /api/v1/team/stats
GET    /api/v1/team/users
POST   /api/v1/team/invite
PATCH  /api/v1/team/users/{id}/role
DELETE /api/v1/team/users/{id}
GET    /api/v1/team/invites
```

**Componentes sugeridos:**
- `TeamMembersTable` - Tabela de membros
- `InviteUserDialog` - Modal de convite
- `PendingInvitesCard` - Card de convites pendentes
- `MemberDetailDialog` - Detalhes do membro (fazendas, perfis)

---

### **3. Settings - Perfis e Permissões**

**Caminho:** `/apps/web/src/app/(dashboard)/settings/roles/page.tsx`

**Funcionalidades:**
- Listar perfis (padrão + customizados)
- Criar perfil customizado
- Editar permissões granulares
- Deletar perfil customizado (se não estiver em uso)

**API Endpoints:**
```typescript
GET    /api/v1/team/roles
POST   /api/v1/team/roles
```

**Componentes sugeridos:**
- `RolesTable` - Tabela de perfis
- `CreateRoleDialog` - Modal de criação
- `PermissionsMatrix` - Matriz de permissões (agricola, pecuaria, financeiro, etc)

**Exemplo de PermissionsMatrix:**
```typescript
interface PermissionsMatrixProps {
  permissions: Record<string, 'write' | 'read' | 'none'>;
  onChange: (permissions: Record<string, string>) => void;
}

function PermissionsMatrix({ permissions, onChange }) {
  const modules = ['agricola', 'pecuaria', 'financeiro', 'operacional'];

  return (
    <table>
      <thead>
        <tr>
          <th>Módulo</th>
          <th>Escrita</th>
          <th>Leitura</th>
          <th>Nenhum</th>
        </tr>
      </thead>
      <tbody>
        {modules.map(module => (
          <tr key={module}>
            <td>{module}</td>
            <td>
              <input
                type="radio"
                checked={permissions[module] === 'write'}
                onChange={() => onChange({...permissions, [module]: 'write'})}
              />
            </td>
            {/* ... */}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

---

### **4. Settings - Grupos de Fazendas**

**Caminho:** `/apps/web/src/app/(dashboard)/settings/grupos/page.tsx`

**Funcionalidades:**
- Listar grupos de fazendas
- Criar grupo
- Editar grupo (nome, cor, ícone)
- Adicionar/remover fazendas do grupo
- Ver assinatura do grupo
- Excluir grupo

**API Endpoints:**
```typescript
GET    /api/v1/grupos-fazendas
GET    /api/v1/grupos-fazendas/{id}
POST   /api/v1/grupos-fazendas
PATCH  /api/v1/grupos-fazendas/{id}
DELETE /api/v1/grupos-fazendas/{id}
POST   /api/v1/grupos-fazendas/{id}/fazendas
DELETE /api/v1/grupos-fazendas/{id}/fazendas/{faz_id}
```

**Componentes sugeridos:**
- `GruposGrid` - Grid de cards de grupos (com cor e ícone)
- `CreateGrupoDialog` - Modal de criação
- `GrupoDetailDialog` - Detalhes do grupo
- `FazendasSelector` - Seletor de fazendas (drag-and-drop ideal)

---

## 🔄 MODIFICAÇÕES EM PÁGINAS EXISTENTES

### **1. Atualizar Sidebar**

**Arquivo:** `/apps/web/src/components/layout/app-sidebar.tsx`

**Mudanças necessárias:**

#### **A. Adicionar item no menu Backoffice:**
```typescript
{
  label: "Gestão de Admins",
  route: "/backoffice/admin-users",
  icon: ShieldCheck,
  permission: "backoffice:admin_users:view"
}
```

#### **B. Adicionar seção no menu Settings:**
```typescript
{
  label: "Gestão de Acessos",
  items: [
    {
      label: "Equipe",
      route: "/settings/team",
      icon: Users,
      permission: "tenant:users:view"
    },
    {
      label: "Perfis e Permissões",
      route: "/settings/roles",
      icon: Shield,
      permission: "tenant:permissions:view"
    },
    {
      label: "Grupos de Fazendas",
      route: "/settings/grupos",
      icon: FolderTree,
      permission: "tenant:grupos:view"
    }
  ]
}
```

#### **C. Implementar verificação de permissões:**
```typescript
// Exemplo de helper
function hasPermission(permission: string): boolean {
  const userRole = useAuth().user?.role;

  // Para backoffice
  if (permission.startsWith('backoffice:')) {
    return BackofficePermissions.has_permission(userRole, permission);
  }

  // Para tenant
  if (permission.startsWith('tenant:')) {
    return TenantPermissions.has_permission(userRole, permission);
  }

  return false;
}

// Uso no sidebar
{items.map(item => (
  hasPermission(item.permission) && (
    <SidebarItem key={item.route} {...item} />
  )
))}
```

---

### **2. Atualizar página de Usuários do Backoffice**

**Arquivo:** `/apps/web/src/app/(dashboard)/backoffice/users/page.tsx`

**Atual:** Lista todos os usuários globalmente (tabela `usuarios`)

**Novo comportamento:**
- Manter listagem de usuários globais
- Adicionar link para nova página `/backoffice/admin-users`
- Diferenciar visualmente usuários normais vs admins

---

## 🎨 COMPONENTES REUTILIZÁVEIS SUGERIDOS

### **1. PermissionGuard**

```typescript
// components/auth/permission-guard.tsx
interface PermissionGuardProps {
  permission: string;
  fallback?: ReactNode;
  children: ReactNode;
}

export function PermissionGuard({ permission, fallback, children }: PermissionGuardProps) {
  const hasPermission = usePermission(permission);

  if (!hasPermission) {
    return fallback || null;
  }

  return <>{children}</>;
}

// Uso:
<PermissionGuard permission="tenant:users:delete">
  <Button variant="destructive">Remover</Button>
</PermissionGuard>
```

---

### **2. RoleSelect**

```typescript
// components/team/role-select.tsx
interface RoleSelectProps {
  value: string;
  onChange: (roleId: string) => void;
  disabled?: boolean;
}

export function RoleSelect({ value, onChange, disabled }: RoleSelectProps) {
  const [roles, setRoles] = useState([]);

  useEffect(() => {
    fetch('/api/v1/team/roles')
      .then(r => r.json())
      .then(setRoles);
  }, []);

  return (
    <Select value={value} onValueChange={onChange} disabled={disabled}>
      <SelectTrigger>
        <SelectValue placeholder="Selecione um perfil" />
      </SelectTrigger>
      <SelectContent>
        {roles.map(role => (
          <SelectItem key={role.id} value={role.id}>
            {role.nome} {role.is_custom && '(Customizado)'}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
```

---

### **3. StatusBadge**

```typescript
// components/ui/status-badge.tsx
interface StatusBadgeProps {
  status: 'ATIVO' | 'INATIVO' | 'PENDENTE' | 'EXPIRADO';
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const variants = {
    ATIVO: 'success',
    INATIVO: 'secondary',
    PENDENTE: 'warning',
    EXPIRADO: 'destructive'
  };

  return (
    <Badge variant={variants[status]}>
      {status}
    </Badge>
  );
}
```

---

## 📦 BIBLIOTECAS RECOMENDADAS

```bash
# Gestão de permissões
npm install @casl/ability @casl/react

# Drag and drop (para fazendas em grupos)
npm install @dnd-kit/core @dnd-kit/sortable

# Gerenciamento de estado (se ainda não tiver)
npm install zustand

# Validação de formulários
npm install react-hook-form zod @hookform/resolvers
```

---

## 🔐 HOOKS CUSTOMIZADOS SUGERIDOS

### **1. usePermission**

```typescript
// hooks/use-permission.ts
import { useAuth } from '@/hooks/use-auth';
import { BackofficePermissions, TenantPermissions } from '@/lib/permissions';

export function usePermission(permission: string): boolean {
  const { user } = useAuth();

  if (!user) return false;

  // Verificar se é admin do backoffice
  if (user.is_superuser) {
    return BackofficePermissions.has_permission(user.role, permission);
  }

  // Verificar permissões do tenant
  return TenantPermissions.has_permission(user.tenant_role, permission, user.custom_permissions);
}
```

---

### **2. useTeam**

```typescript
// hooks/use-team.ts
export function useTeam() {
  const [members, setMembers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchTeam = async () => {
    setLoading(true);
    try {
      const [membersData, statsData] = await Promise.all([
        fetch('/api/v1/team/users').then(r => r.json()),
        fetch('/api/v1/team/stats').then(r => r.json())
      ]);
      setMembers(membersData);
      setStats(statsData);
    } finally {
      setLoading(false);
    }
  };

  const inviteMember = async (data) => {
    await fetch('/api/v1/team/invite', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    fetchTeam();
  };

  const removeMember = async (id) => {
    await fetch(`/api/v1/team/users/${id}`, { method: 'DELETE' });
    fetchTeam();
  };

  useEffect(() => {
    fetchTeam();
  }, []);

  return { members, stats, loading, inviteMember, removeMember, refresh: fetchTeam };
}
```

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

### **Fase 1: Infraestrutura (2-3 horas)**
- [ ] Criar arquivo de constantes de permissões (`lib/permissions.ts`)
- [ ] Criar hooks (`usePermission`, `useTeam`, `useRoles`)
- [ ] Criar componentes base (`PermissionGuard`, `StatusBadge`, `RoleSelect`)
- [ ] Atualizar contexto de autenticação para incluir permissões

### **Fase 2: Backoffice (4-5 horas)**
- [ ] Criar página `/backoffice/admin-users/page.tsx`
- [ ] Criar componentes da página (Table, Dialogs, Stats)
- [ ] Integrar com API
- [ ] Adicionar ao sidebar
- [ ] Testes manuais

### **Fase 3: Gestão de Equipe (6-8 horas)**
- [ ] Criar página `/settings/team/page.tsx`
- [ ] Criar página `/settings/roles/page.tsx`
- [ ] Criar componentes (Table, Dialogs, PermissionsMatrix)
- [ ] Integrar com API
- [ ] Adicionar ao sidebar
- [ ] Testes manuais

### **Fase 4: Grupos de Fazendas (6-8 horas)**
- [ ] Criar página `/settings/grupos/page.tsx`
- [ ] Criar componentes (Grid, Dialogs, FazendasSelector)
- [ ] Implementar drag-and-drop (opcional)
- [ ] Integrar com API
- [ ] Adicionar ao sidebar
- [ ] Testes manuais

### **Fase 5: Polimento (2-3 horas)**
- [ ] Adicionar loading states
- [ ] Adicionar error handling
- [ ] Adicionar toasts de sucesso/erro
- [ ] Validação de formulários
- [ ] Responsividade mobile
- [ ] Testes finais

---

## 🚀 ESTIMATIVA TOTAL

**Tempo estimado:** 20-27 horas (2.5-3.5 semanas)

**Distribuição:**
- Infraestrutura: 3h
- Backoffice: 5h
- Gestão de Equipe: 8h
- Grupos de Fazendas: 8h
- Polimento: 3h

---

## 📚 RECURSOS ADICIONAIS

- **API Reference:** Ver [API_REFERENCE_RBAC.md](API_REFERENCE_RBAC.md)
- **Arquitetura:** Ver [IMPLEMENTACAO_RBAC_MULTI_SUB.md](IMPLEMENTACAO_RBAC_MULTI_SUB.md)
- **Shadcn/UI:** https://ui.shadcn.com/docs/components
- **React Hook Form:** https://react-hook-form.com/
- **DnD Kit:** https://dndkit.com/

---

**Autor:** Claude Code (Anthropic)
**Data:** 12/03/2024
**Versão:** 1.0
