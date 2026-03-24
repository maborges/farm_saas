---
trigger: glob: (services/api-*/**, apps/web/**, packages/**)
---

# AGRO-01: Segurança e Blindagem Multi-Tenant

**CONTEXTO:** Proteção da soberania de dados do produtor rural e isolamento entre módulos independentes.

### 1. SOBERANIA DE DADOS (Obrigatório)
- **Um Módulo, Um Banco**: Microsserviços (ex: `api-pecuaria`) NUNCA acessam o banco de outro módulo diretamente. Use APIs REST ou Eventos.
- **Tenant Isolation**: Toda query DEVE incluir `.eq('tenant_id', tenant_id)`.
- **Origem do Tenant**: O `tenant_id` SEMPRE vem da sessão autenticada (Iron Session no Next.js ou Depends(get_tenant_id) no FastAPI). NUNCA do request body ou user input.

### 2. ISOLAMENTO DE ESCRITA (Frontend)
- **Zero Writing from Client**: O frontend (Next.js client-side) é PROIBIDO de realizar INSERT/UPDATE/DELETE diretamente no banco. 
- Toda alteração passa por `/api/*` com validação de sessão e `tenant_id` no servidor.

### 3. PROTEÇÃO DE SEGREDOS E SESSÃO OBRIGATÓRIA
- **Criptografia em Repouso**: API Keys (Stripe, WhatsApp, etc.) devem ser salvas criptografadas (AES-256) via `EncryptionService`.
- **Higiene de Credenciais**: Senhas (bcrypt cost 12) + complexidade (8+ chars).
- **Session Hardening**: Uso inegociável de `iron-session` com `SESSION_SECRET` (32+ caracteres, em .env). Cookies DEVEM ter `httpOnly: true`, `secure: true`, `sameSite: 'lax'` e prefixo `__Host-`.
- **Proxy de Autenticação**: O frontend (client/browser) NUNCA se comunica diretamente com o backend (FastAPI). Todo request passa pelo seu próprio backend (Next.js API Routes / Proxy).
- **Repasse Seguro**: O Next.js decripta o cookie (iron-session), valida o payload e repassa a requisição ao FastAPI contendo o header de rede interna `X-User-Id`. O FastAPI confia nesse header e o valida via Dependency Injection (`Depends`).
- **Bloqueio de Tokens no Frontend**: Tokens JWT, Session IDs e Refresh Tokens são rigorosamente PROIBIDOS de residir no `localStorage`, `sessionStorage` ou cookies expostos ao Javascript cliente.

### 4. ROW LEVEL SECURITY (RLS) E ISOLAMENTO ESTRITO
- **Ativo em Toda Tabela**: Obrigatório RLS ativo em **todas** as tabelas do Supabase, sem exceção.
- **Tenant Policies**: Toda tabela de usuário DEVE conter a coluna `user_id` e policies obrigatórias de SELECT, INSERT, UPDATE e DELETE condicionados a `auth.uid() = user_id`.
- **Isolamento Comprovado (Regra Férrea)**: O User A NUNCA deve acessar dados do User B sob nenhuma circunstância.
- **Tabelas Públicas**: Tabelas de sistema (ex: `plans`, `pricing`) DEVEM ter política explícita limitando-se SOMENTE para leitura (`SELECT`). Regras de escrita nelas podem ocorrer aspenas via back-end seguro usando `service_role`.

### 5. VALIDAÇÃO & PROTEÇÃO DE DADOS
- **Input Validation**: Usar `Pydantic` de forma estrita em todos os endpoints para validar payloads, garantindo sanitização.
- **Upload de Arquivos**: Restringir rigorosamente tipo (MIME type) e tamanho máximo dos arquivos recebidos pelo servidor de upload.
- **Logs Limpos**: NUNCA registrar (log) dados sensíveis (senhas, tokens, dados PII). Todos os logs devem ofuscar/remover esses dados.

### 6. REDE E INTEGRAÇÕES (Closed by Default)
- **Closed by Default**: TODAS as rotas de API DEVEM ser autenticadas. Apenas exceções claras como _health check_ e subconjunto listado de rotas públicas.
- **CORS Configurado**: Especificar origens confiáveis validando o domínio exato do frontend, evitando permissividade genérica (`*`).
- **Rate Limiting**: Aplicar Rate Limiting isolado por `user_id` ou IP nos endpoints sensíveis (auth, billing e consumo de IA).
- **Webhooks Seguros**: Validar obrigatoriamente a assinatura de eventos externos (Stripe webhook) mediante key validada, e com log apenas do status.
- **Gestão de Segredos**: Manter credenciais no `.env`. Nunca fazer commit e usar script local `check-secrets.sh`. Variavéis secretas NUNCA podem ter prefixo `NEXT_PUBLIC_` (sob pena de vazar segredos na build client).

### 7. PREVENÇÃO DE EXPOSIÇÃO NO FRONTEND
- **Logs Nulos de IDs**: NUNCA logar informações e IDs que identifiquem registros e empresas de usuários (`user_id`, `empresa_id`) diretamente em consoles visíveis de browser.
- **Blindagem de Erros**: O Backend não envia pra front-end nenhum *Stack Trace*, queries cruas SQL ou qualquer insight do banco. Mensagens amigáveis para cliente.
- **URLs Limpas (Obfuscation)**: NUNCA injetar ou trafegar IDs de banco numéricos crus expostos por design nas URLs da aplicação. Utilizar URIs descritivos com UUIDs curtos ou `slugs`.

```python
# Exemplo Correto (FastAPI)
@router.get("/animais")
async def list_animais(tenant_id: UUID = Depends(get_tenant_id)):
    return await db.animais.filter(tenant_id=tenant_id).all()
```
