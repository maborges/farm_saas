# Recuperação de Senha por E-mail com Token Expirável (1 hora)

## Visão Geral

Implementação completa de recuperação de senha por e-mail com token seguro e expirável, seguindo as melhores práticas de segurança.

## Funcionalidades Implementadas

### Backend (FastAPI + SQLAlchemy)

#### 1. **Model de Banco de Dados** (`core/models/auth.py`)

- **Tabela**: `tokens_recuperacao_senha`
- **Campos**:
  - `id`: UUID primary key
  - `usuario_id`: FK para usuarios (CASCADE delete)
  - `token`: String único e seguro (64 caracteres via `secrets.token_urlsafe`)
  - `utilizado`: Boolean (marca se foi usado)
  - `data_criacao`: Timestamp UTC
  - `data_expiracao`: Timestamp UTC (1 hora após criação)
  - `data_utilizacao`: Timestamp quando foi usado
  - `ip_origem`: IP que solicitou a recuperação
  - `ip_utilizacao`: IP que utilizou o token

- **Índices**:
  - `token` (UNIQUE) - Busca rápida do token
  - `usuario_id` - Busca por usuário
  - `utilizado` - Filtrar tokens não utilizados

- **Segurança**:
  - Relacionamento com `Usuario` via FK com CASCADE
  - Rastreamento de IP para auditoria
  - Tokens single-use (só podem ser usados uma vez)

#### 2. **Pydantic Schemas** (`core/schemas/auth_schemas.py`)

- `ForgotPasswordRequest`: Validação do email
- `ForgotPasswordResponse`: Resposta genérica (previne enumeração de usuários)
- `VerifyResetTokenRequest`: Validação do token
- `VerifyResetTokenResponse`: Status do token (válido/inválido, expiração)
- `ResetPasswordRequest`: Nova senha + confirmação (min 6 caracteres)
- `ResetPasswordResponse`: Confirmação de sucesso

#### 3. **Serviços** (`core/services/auth_service.py`)

**Métodos adicionados ao `AuthService`:**

1. **`create_password_reset_token(email, ip_address)`**
   - Busca usuário por email
   - Invalida tokens anteriores não utilizados (segurança)
   - Gera token criptográfico seguro (`secrets.token_urlsafe(48)`)
   - Define expiração para 1 hora
   - Envia email de recuperação
   - Retorna mensagem genérica (previne enumeração)

2. **`verify_reset_token(token)`**
   - Verifica existência e se não foi utilizado
   - Verifica expiração (1 hora)
   - Retorna informações do token (email, tempo restante)

3. **`reset_password(token, nova_senha, ip_address)`**
   - Valida token (existência, não utilizado, não expirado)
   - Verifica se nova senha é diferente da atual
   - Atualiza senha com hash bcrypt
   - Marca token como utilizado
   - Registra IP e timestamp de utilização

#### 4. **Email Service** (`core/services/email_service.py`)

- **Novo método**: `send_password_recovery(email, nome_usuario, token)`
- **Template**: `core/templates/emails/password_reset.html`
- **Conteúdo**:
  - Nome do usuário
  - Link de recuperação com token
  - Data/hora da solicitação
  - Aviso de expiração (1 hora)
  - Instruções de segurança

#### 5. **Endpoints da API** (`core/routers/auth.py`)

Todos montados em `/api/v1/auth/`:

1. **`POST /forgot-password`**
   - Request: `{ email: string }`
   - Response: `{ sucesso: bool, mensagem: string, email?: string }`
   - Sem autenticação requerida
   - Previne enumeração de usuários

2. **`POST /verify-reset-token`**
   - Request: `{ token: string }`
   - Response: `{ valido: bool, mensagem: string, email?: string, expira_em?: string }`
   - Sem autenticação requerida
   - Útil para validar token antes de mostrar formulário

3. **`POST /reset-password`**
   - Request: `{ token: string, nova_senha: string, confirmar_senha: string }`
   - Response: `{ sucesso: bool, mensagem: string }`
   - Sem autenticação requerida
   - Valida confirmação de senha

### Frontend (Next.js 16 + React 19)

#### 1. **Página Esqueci a Senha** (`apps/web/src/app/(auth)/forgot-password/page.tsx`)

- Formulário com validação Zod + React Hook Form
- Estado de sucesso com instruções
- Proteção contra enumeração de usuários
- Link para voltar ao login
- Reenvio opcional
- Design consistente com login (dark theme, glassmorphism)

#### 2. **Página Redefinir Senha** (`apps/web/src/app/(auth)/reset-password/page.tsx`)

- Verificação automática do token ao carregar
- Estados:
  - Loading (verificando token)
  - Token inválido/expirado
  - Formulário de redefinição
  - Sucesso (senha redefinida)
- Validações:
  - Senha mínima de 6 caracteres
  - Confirmação de senha obrigatória
- Exibição do tempo restante do token
- Redirecionamento para login após sucesso

#### 3. **Login Form Atualizado** (`apps/web/src/components/auth/login-form.tsx`)

- Link "Esqueceu a senha?" atualizado para `/forgot-password`
- Navegação consistente

### Migração do Banco de Dados

**Arquivo**: `migrations/versions/20260403_add_password_recovery_token.py`

- Cria tabela `tokens_recuperacao_senha`
- Adiciona índices para performance
- Suporte a rollback (downgrade)

## Fluxo de Uso

```
1. Usuário clica em "Esqueceu a senha?" na página de login
2. É redirecionado para /forgot-password
3. Insere seu e-mail e submete
4. Backend gera token seguro e envia e-mail
5. Usuário recebe e-mail com link (válido por 1 hora)
6. Clica no link e vai para /reset-password?token=XYZ
7. Frontend verifica validade do token
8. Se válido, mostra formulário de nova senha
9. Usuário digita nova senha e confirmação
10. Backend valida token, atualiza senha e invalida token
11. Usuário pode fazer login com nova senha
```

## Segurança

### Medidas Implementadas

✅ **Token criptográfico seguro** (`secrets.token_urlsafe(48)`)  
✅ **Expiração de 1 hora** (configurável)  
✅ **Single-use** (token só pode ser usado uma vez)  
✅ **Invalidação de tokens anteriores** ao gerar novo token  
✅ **Prevenção de enumeração de usuários** (mensagem genérica)  
✅ **Rastreamento de IP** (auditoria de segurança)  
✅ **Hash bcrypt** para senha (mesmo sistema de login)  
✅ **Validação de senha mínima** (6 caracteres)  
✅ **Verificação de senha diferente** (não permite reutilização imediata)  
✅ **Índices de banco** para performance e segurança  

### Recomendações para Produção

- Usar HTTPS para todos os endpoints
- Configurar SMTP adequado (não usar credenciais hardcoded)
- Monitorar tentativas de uso de tokens expirados
- Rate limiting no endpoint `/forgot-password` (ex: máx 3 por hora)
- Logging de auditoria para tentativas de recuperação
- Alertas de segurança para IPs suspeitos

## Testes

### Testes Manuais

1. **Fluxo completo**:
   ```bash
   # 1. Solicitar recuperação
   curl -X POST http://localhost:8000/api/v1/auth/forgot-password \
     -H "Content-Type: application/json" \
     -d '{"email": "usuario@teste.com"}'
   
   # 2. Verificar token (do e-mail recebido)
   curl -X POST http://localhost:8000/api/v1/auth/verify-reset-token \
     -H "Content-Type: application/json" \
     -d '{"token": "TOKEN_DO_EMAIL"}'
   
   # 3. Redefinir senha
   curl -X POST http://localhost:8000/api/v1/auth/reset-password \
     -H "Content-Type: application/json" \
     -d '{"token": "TOKEN_DO_EMAIL", "nova_senha": "nova123", "confirmar_senha": "nova123"}'
   ```

2. **Token expirado**:
   - Alterar `data_expiracao` manualmente no banco para passado
   - Tentar usar token → deve retornar erro

3. **Token já utilizado**:
   - Usar token duas vezes → segunda tentativa deve falhar

4. **Email não existente**:
   - Solicitar recuperação para email inexistente
   - Deve retornar mensagem genérica de sucesso (sem expor existência)

### Testes Automatizados (Sugeridos)

```python
# tests/test_password_recovery.py

async def test_create_reset_token(async_client, test_user):
    response = await async_client.post("/api/v1/auth/forgot-password", json={
        "email": test_user.email
    })
    assert response.status_code == 200
    assert "sucesso" in response.json()

async def test_reset_password_with_valid_token(async_client, test_user, db_session):
    # Solicitar token
    await async_client.post("/api/v1/auth/forgot-password", json={
        "email": test_user.email
    })
    
    # Buscar token no banco
    stmt = select(TokenRecuperacaoSenha).where(
        TokenRecuperacaoSenha.usuario_id == test_user.id,
        TokenRecuperacaoSenha.utilizado == False
    )
    result = await db_session.execute(stmt)
    token_record = result.scalar_one()
    
    # Reset password
    response = await async_client.post("/api/v1/auth/reset-password", json={
        "token": token_record.token,
        "nova_senha": "nova_senha_123",
        "confirmar_senha": "nova_senha_123"
    })
    
    assert response.status_code == 200
    assert response.json()["sucesso"] == True

async def test_token_expires_after_one_hour(async_client, test_user, db_session):
    # Similar ao teste anterior, mas com manipulação do tempo
    pass

async def test_cannot_reuse_token(async_client, test_user, db_session):
    # Usar token duas vezes deve falhar na segunda
    pass
```

## Arquivos Modificados/Criados

### Backend
- ✅ `services/api/core/models/auth.py` - Adicionado `TokenRecuperacaoSenha` model
- ✅ `services/api/core/schemas/auth_schemas.py` - Adicionados schemas de recuperação
- ✅ `services/api/core/services/auth_service.py` - Adicionados 3 métodos
- ✅ `services/api/core/services/email_service.py` - Adicionado método de envio
- ✅ `services/api/core/routers/auth.py` - Adicionados 3 endpoints
- ✅ `services/api/core/templates/emails/password_reset.html` - Template do email
- ✅ `services/api/migrations/versions/20260403_add_password_recovery_token.py` - Migration

### Frontend
- ✅ `apps/web/src/app/(auth)/forgot-password/page.tsx` - Página de solicitação
- ✅ `apps/web/src/app/(auth)/reset-password/page.tsx` - Página de redefinição
- ✅ `apps/web/src/components/auth/login-form.tsx` - Link atualizado

## Deploy

### 1. Rodar migração do banco:
```bash
cd services/api
alembic upgrade head
```

### 2. Configurar variáveis de ambiente (se necessário):
```bash
# .env.local
SMTP_HOST=smtp.seuservico.com
SMTP_PORT=587
SMTP_USER=seu_usuario
SMTP_PASS=sua_senha
MAIL_FROM=noreply@agrosaas.com.br
FRONTEND_URL=https://seu-dominio.com
```

### 3. Deploy do backend:
```bash
cd services/api
# Restart do servidor FastAPI
```

### 4. Build do frontend:
```bash
cd apps/web
pnpm build
```

## Monitoramento

### Logs Importantes

Monitorar no `EmailService` e `AuthService`:
- Tokens criados e emails enviados
- Tokens verificados (válidos/inválidos)
- Senhas redefinidas com sucesso
- Tentativas de uso de tokens expirados
- Falhas de envio de email

### Métricas Recomendadas

- Taxa de conversão (solicitação → redefinição)
- Tempo médio para uso do token
- Tokens expirados sem uso
- Tentativas de uso de tokens já utilizados
- Picos de solicitações (possível ataque)

## Referências

- OWASP Forgot Password: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- NIST SP 800-63B: Digital Identity Guidelines
- Python secrets module: https://docs.python.org/3/library/secrets.html
