# Alternância de Assinaturas (Grupos/Fazendas)

## Visão Geral

Funcionalidade que permite a um assinante alternar entre diferentes assinaturas (grupos de fazendas) dentro do mesmo tenant. Isso é útil quando um produtor rural possui múltiplas assinaturas para diferentes grupos de propriedades.

## Cenário de Uso

Um produtor pode ter:
- **Grupo "Fazendas Región Sul"** (3 fazendas) → Assinatura Plano Profissional
- **Grupo "Fazendas Región Norte"** (2 fazendas) → Assinatura Plano Essencial

Cada grupo possui módulos, limites e configurações diferentes. O usuário pode alternar entre eles sem precisar fazer logout/login.

## Arquitetura

### Backend

#### Novos Endpoints

**1. `GET /api/v1/auth/minhas-assinaturas`**

Lista todas as assinaturas (grupos) que o usuário tem acesso no tenant atual.

**Resposta:**
```json
[
  {
    "grupo_id": "uuid",
    "grupo_nome": "Fazendas Región Sul",
    "plano_nome": "Plano Profissional",
    "plano_tier": "PROFISSIONAL",
    "status": "ATIVA",
    "total_fazendas": 3,
    "fazendas": [
      {"id": "uuid", "nome": "Fazenda A"},
      {"id": "uuid", "nome": "Fazenda B"}
    ],
    "modulos": ["CORE", "A1_PLANEJAMENTO", "F1_ESTOQUE"],
    "is_ativa": true
  }
]
```

**2. `POST /api/v1/auth/switch-grupo`**

Alterna o contexto para outro grupo de fazendas (assinatura).

**Request:**
```json
{
  "grupo_id": "uuid"
}
```

**Resposta:**
```json
{
  "access_token": "novo JWT com contexto do grupo",
  "grupo_ativo": {
    "grupo_id": "uuid",
    "grupo_nome": "Fazendas Región Norte",
    "plano_nome": "Plano Essencial",
    "status": "ATIVA",
    "total_fazendas": 2,
    "fazendas": [...],
    "modulos": ["CORE"],
    "is_ativa": true
  }
}
```

#### Método no AuthService

**`generate_token_for_grupo(user_id, tenant_id, grupo_id, ip_address, user_agent)`**

Gera um JWT com o grupo selecionado como contexto ativo. Similar ao `generate_token_for_tenant`, mas foca em um grupo específico.

**Claims do JWT:**
```json
{
  "sub": "user_id",
  "tenant_id": "tenant_id",
  "modules": ["CORE", "A1_PLANEJAMENTO"],
  "fazendas_auth": [...],
  "grupos_auth": ["grupo_id"],
  "grupos": [...],
  "active_grupo_id": "grupo_id",
  "is_superuser": false,
  "plan_tier": "PROFISSIONAL"
}
```

### Frontend

#### App Store (Zustand)

**Novos estados:**
- `minhasAssinaturas: AssinaturaInfo[]` - Lista de assinaturas disponíveis

**Novos métodos:**
- `loadMinhasAssinaturas()` - Carrega assinaturas do backend
- `switchAssinatura(grupoId: string)` - Alterna para outra assinatura

#### Componentes Atualizados

**1. `ContextSelector`**

- Exibe dropdown de assinaturas quando há múltiplas assinaturas
- Mostra informações do plano, tier e número de fazendas
- Permite alternar entre assinaturas com um clique
- Mantém seletor de fazendas do grupo ativo

**2. `TenantSwitcher`**

- Carrega assinaturas após trocar de tenant
- Garante que as assinaturas estejam sempre atualizadas

**3. `FazendasSync`**

- Carrega assinaturas após sincronizar fazendas
- Garante que as assinaturas estejam disponíveis após o login

#### Tipos TypeScript

```typescript
interface AssinaturaInfo {
  grupo_id: string;
  grupo_nome: string;
  plano_nome: string;
  plano_tier: PlanTierId;
  status: string;
  total_fazendas: number;
  fazendas: Array<{ id: string; nome: string }>;
  modulos: ModuleId[];
  is_ativa: boolean;
}
```

## Fluxo de Uso

1. **Login Inicial**
   - Usuário faz login no sistema
   - Backend retorna JWT com todos os grupos disponíveis em `grupos[]`
   - Frontend carrega assinaturas via `loadMinhasAssinaturas()`

2. **Alternar Assinatura**
   - Usuário clica no seletor de assinaturas no header
   - Dropdown exibe todas as assinaturas com informações do plano
   - Usuário seleciona a assinatura desejada
   - Frontend chama `POST /auth/switch-grupo`
   - Backend retorna novo JWT com contexto do grupo
   - Frontend atualiza token e recarrega dashboard

3. **Sincronização**
   - `FazendasSync` carrega assinaturas periodicamente
   - Garante que novas assinaturas apareçam sem logout
   - Mantém cache atualizado no Zustand store

## Segurança

- **Validação de Acesso:** Backend verifica que o usuário tem acesso ao grupo via `GrupoUsuario`
- **Validação de Tenant:** Grupo deve pertencer ao mesmo tenant do usuário
- **Validação de Status:** Grupo deve estar ativo (`ativo == True`)
- **Assinatura Ativa:** Módulos e limites vêm da assinatura com `status == "ATIVA"`
- **JWT Isolado:** Cada assinatura gera um JWT com contexto isolado

## Regras de Negócio

1. **RN-AS-001:** Usuário só pode alternar para grupos que tem vínculo (`GrupoUsuario`)
2. **RN-AS-002:** Grupo deve estar ativo e pertencer ao tenant atual
3. **RN-AS-003:** Módulos disponíveis são definidos pela assinatura do grupo
4. **RN-AS-004:** Tier do plano pode mudar entre assinaturas diferentes
5. **RN-AS-005:** Fazendas disponíveis mudam conforme o grupo selecionado
6. **RN-AS-006:** Se houver apenas 1 grupo, `active_grupo_id` é definido automaticamente no login
7. **RN-AS-007:** Alternância de assinatura recarrega o dashboard para atualizar contexto

## Testes Manuais

### Cenário 1: Usuário com Múltiplas Assinaturas
1. Crie um tenant com 2 grupos de fazendas
2. Associe assinaturas diferentes para cada grupo (ex: Profissional e Essencial)
3. Vincule um usuário a ambos os grupos via `GrupoUsuario`
4. Faça login com o usuário
5. Verifique que o `ContextSelector` exibe dropdown de assinaturas
6. Alterne entre assinaturas e verifique que:
   - Token é atualizado
   - Módulos disponíveis mudam
   - Fazendas disponíveis mudam
   - Dashboard recarrega com novo contexto

### Cenário 2: Usuário com Apenas 1 Assinatura
1. Crie um tenant com 1 grupo de fazendas
2. Faça login com usuário vinculado ao grupo
3. Verifique que `ContextSelector` exibe apenas seletor de fazendas (sem dropdown de assinaturas)
4. Verifique que `active_grupo_id` está definido no JWT

### Cenário 3: Alternar Tenant
1. Usuário com acesso a múltiplos tenants
2. Use `TenantSwitcher` para trocar de tenant
3. Verifique que assinaturas são recarregadas para o novo tenant
4. Verifique que `ContextSelector` mostra assinaturas do tenant correto

## Troubleshooting

**Problema:** Dropdown de assinaturas não aparece
- Verifique se usuário tem vínculo com múltiplos grupos via `GrupoUsuario`
- Verifique se há múltiplas assinaturas ativas (`minhasAssinaturas.length > 1`)
- Console do navegador deve mostrar assinaturas carregadas

**Problema:** Erro 403 ao alternar grupo
- Verifique se usuário tem registro em `GrupoUsuario` para o grupo alvo
- Verifique se grupo está ativo (`ativo == True`)
- Verifique se grupo pertence ao tenant atual

**Problema:** Módulos não atualizam após troca
- Verifique que JWT possui `modules` correto para o novo grupo
- Verifique que `activeModules()` no store retorna módulos corretos
- Refresh force do navegador pode ser necessário

## Arquivos Modificados

### Backend
- `services/api/core/routers/auth.py` - Novos endpoints
- `services/api/core/services/auth_service.py` - Método `generate_token_for_grupo`
- `services/api/core/services/auth_service.py` - Atualização em `generate_token_for_tenant`

### Frontend
- `apps/web/src/types/global.d.ts` - Tipo `AssinaturaInfo`
- `apps/web/src/lib/stores/app-store.ts` - Estados e métodos de assinatura
- `apps/web/src/components/layout/context-selector.tsx` - UI de alternância
- `apps/web/src/components/layout/tenant-switcher.tsx` - Carregamento de assinaturas
- `apps/web/src/components/auth/fazendas-sync.tsx` - Sincronização de assinaturas

## Próximos Passos

1. **Testes Automatizados:** Criar testes de integração para endpoints
2. **UI/UX:** Melhorar visual do dropdown de assinaturas com ícones e cores
3. **Performance:** Cache de assinaturas para evitar queries repetidas
4. **Analytics:** Rastrear uso de alternância de assinaturas
5. **Notificações:** Notificar usuário quando módulos mudam ao alternar
