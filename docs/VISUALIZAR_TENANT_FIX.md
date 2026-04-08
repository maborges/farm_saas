# Fix: Botão Visualizar na Gestão de Assinantes

## Problema
Na tela "Gestão de Assinantes" do backoffice, ao clicar no botão "Visualizar" no datatable, o dialog abria mas não carregava nenhuma informação.

## Causas Identificadas

### 1. Falta de Tratamento de Erro no Frontend
- O `useQuery` no componente `TenantDetailsDialog` não tinha tratamento de erro
- Erros de autenticação (403), não encontrado (404) ou servidor (500) falhavam silenciosamente
- Usuário não recebia nenhum feedback visual quando ocorria erro

### 2. Endpoint Requer Autenticação Admin
- O endpoint `/backoffice/tenants/{tenant_id}/details` usa `dependencies=[Depends(get_current_admin)]`
- Se o usuário não tiver permissão de superusuário admin, retorna 403 Forbidden
- O `get_current_admin` verifica `claims.get("is_superuser")`

### 3. Possível Problema de Autenticação
- O `apiFetch` depende do Zustand store estar hidratado com o token
- Se o store não hidratar corretamente, a requisição vai sem Authorization header
- O endpoint admin vai rejeitar a requisição

## Correções Aplicadas

### Arquivo: `apps/web/src/app/(dashboard)/dashboard/backoffice/tenants/tenants-client.tsx`

#### 1. Adicionado Tratamento de Erro no useQuery
```typescript
const { data: details, isLoading, error: detailsError } = useQuery({
    queryKey: ["backoffice", "tenant-details", tenantId],
    queryFn: () => apiFetch<TenantDetail>(`/backoffice/tenants/${tenantId}/details`),
    enabled: !!tenantId,
    retry: 1,  // Reduzido de valor padrão para falhar mais rápido
});

const { data: moduleUsage, error: moduleUsageError } = useQuery<...>({
    queryKey: ["backoffice", "module-usage", tenantId],
    queryFn: () => apiFetch(`/backoffice/tenants/${tenantId}/module-usage?days=30`),
    enabled: !!tenantId,
    retry: 1,
});

// Log de erros para debug
if (detailsError) {
    console.error("❌ Erro ao carregar detalhes do tenant:", detailsError);
}
if (moduleUsageError) {
    console.error("❌ Erro ao carregar uso de módulos:", moduleUsageError);
}
```

#### 2. Adicionado Estado de Erro Visual no Dialog
```typescript
{isLoading ? (
    <div className="p-8 space-y-4">
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-40 w-full" />
    </div>
) : detailsError ? (
    <div className="p-8 flex flex-col items-center justify-center h-full text-center space-y-4">
        <div className="h-16 w-16 rounded-full bg-red-500/10 flex items-center justify-center">
            <UserX className="h-8 w-8 text-red-500" />
        </div>
        <div className="space-y-2">
            <h3 className="text-lg font-semibold">Erro ao carregar detalhes</h3>
            <p className="text-sm text-muted-foreground max-w-md">
                {detailsError instanceof Error ? detailsError.message : "Não foi possível carregar os detalhes do tenant."}
            </p>
            <Button 
                variant="outline" 
                className="mt-2"
                onClick={() => {
                    queryClient.invalidateQueries({ queryKey: ["backoffice", "tenant-details", tenantId] });
                    queryClient.invalidateQueries({ queryKey: ["backoffice", "module-usage", tenantId] });
                }}
            >
                Tentar novamente
            </Button>
        </div>
    </div>
) : details ? (
    // ... conteúdo normal
```

#### 3. Adicionado useQueryClient no Componente
```typescript
function TenantDetailsDialog({ ... }: TenantDetailsDialogProps) {
    const queryClient = useQueryClient();  // Necessário para invalidar queries no botão "Tentar novamente"
    // ...
}
```

## Como Testar

### 1. Verificar no Console do Navegador
- Abra o DevTools (F12) → Console
- Clique no botão "Visualizar"
- Verifique se há mensagens de erro:
  - `⚠️ [apiFetch] Token ausente` → Problema de autenticação
  - `❌ Erro ao carregar detalhes do tenant:` → Mostra o erro específico

### 2. Cenários de Erro Esperados

#### Erro 403 Forbidden (Sem permissão admin)
**Sintoma**: Dialog mostra "Erro ao carregar detalhes" com mensagem "Acesso restrito ao Backoffice administrativo."

**Solução**: Verifique se o usuário logado tem `is_superuser=True` no banco de dados.

#### Erro 401 Unauthorized (Sem token)
**Sintoma**: Console mostra `⚠️ [apiFetch] Token ausente para /backoffice/tenants/{id}/details`

**Solução**: 
- Faça logout e login novamente
- Verifique localStorage: `localStorage.getItem("agrosaas-auth-storage")`
- Verifique se o backend está rodando em `http://127.0.0.1:8000`

#### Erro 404 Not Found (Tenant não existe)
**Sintoma**: Dialog mostra "Tenant não encontrado"

**Solução**: Verifique se o ID do tenant existe no banco de dados.

#### Erro 500 Internal Server Error
**Sintoma**: Dialog mostra mensagem de erro do servidor

**Solução**: Verifique logs do backend em `/opt/lampp/htdocs/farm/services/api/`

### 3. Verificar Backend Rodando
```bash
# Verifique se o backend está ativo
curl http://127.0.0.1:8000/docs
# Deve retornar a documentação Swagger UI
```

### 4. Verificar Permissões do Usuário
```sql
-- No banco de dados, verifique se o usuário é admin
SELECT email, is_superuser FROM usuarios WHERE email = 'seu@email.com';
-- is_superuser deve ser true/1
```

## Debug Avançado

### Logs do Backend
O endpoint de detalhes tem logging detalhado em caso de erro:
```python
logger.error(f"Erro ao buscar detalhes do tenant {tenant_id}: {e}")
logger.error(traceback.format_exc())
```

Verifique os logs do servidor para stack traces completos.

### Teste Manual do Endpoint
```bash
# Com token de admin
curl -X GET "http://127.0.0.1:8000/api/v1/backoffice/tenants/{tenant_id}/details" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# Deve retornar JSON com detalhes completos
```

## Próximos Passos Recomendados

1. **Adicionar Testes Automatizados**: Criar testes E2E para verificar o fluxo completo
2. **Melhorar Verificação de Autenticação**: Adicionar interceptor que redireciona para login se token expirar
3. **Adicionar Skeleton Mais Descritivo**: Melhorar UX enquanto carrega
4. **Cache Otimizado**: Configurar staleTime e cacheTime adequados para dados de tenant

## Arquivos Modificados
- `apps/web/src/app/(dashboard)/dashboard/backoffice/tenants/tenants-client.tsx`
