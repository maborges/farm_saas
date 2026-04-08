# Correção da Funcionalidade "Sessões Ativas"

## Problema Identificado

A página "Sessões Ativas" não exibia nenhuma informação porque **nenhum registro estava sendo criado na tabela `sessoes_ativas` durante o login**.

### Causa Raiz
- O método `authenticate_user` no `auth_service.py` gerava o token JWT mas **não criava** o registro da sessão no banco
- O middleware de validação (`get_current_user_claims`) verificava sessões existentes, mas ninguém as criava
- Sem dados na tabela, a página de Sessões Ativas sempre retornava lista vazia

## Correções Implementadas

### 1. **Criação de Sessão no Login** (`core/services/auth_service.py`)
- Adicionado código para criar registro na tabela `sessoes_ativas` após geração do token
- Registra: `tenant_id`, `usuario_id`, `token_hash`, `ip_address`, `user_agent`, timestamps
- Sessão é criada com status "ATIVA" e expiração de 30 minutos

### 2. **Endpoint de Logout** (`core/routers/sessions.py`)
- Adicionado endpoint `POST /auth/sessions/logout`
- Marca a sessão como "ENCERRADA" no banco
- Invalida o cache da sessão para invalidação imediata

### 3. **Middleware de Heartbeat** (`main.py`)
- Criado `SessionHeartbeatMiddleware` para atualizar o heartbeat a cada requisição
- Atualiza `ultimo_heartbeat` e `expira_em` automaticamente
- Execução em background para não bloquear respostas
- Ignora rotas de login/register e documentação

### 4. **Logout no Frontend** (`apps/web/src/lib/stores/app-store.ts`)
- Função `logout()` agora chama a API para encerrar a sessão no servidor
- Sempre limpa o estado local mesmo se a API falhar
- Previne sessões órfãs no backend

## Como Testar

1. **Inicie o backend:**
   ```bash
   cd /opt/lampp/htdocs/farm/services/api
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Inicie o frontend:**
   ```bash
   cd /opt/lampp/htdocs/farm/apps/web
   npm run dev
   ```

3. **Teste o fluxo completo:**
   - Faça login na aplicação
   - Navegue até **Configurações → Sessões Ativas**
   - Você deve ver sua sessão atual listada com:
     - Dispositivo (Computador/Móvel)
     - Endereço IP
     - Último acesso (há X min)
     - Status (Sessão atual/Ativa)
   - Abra outra aba/navegador e faça login com outro usuário
   - Volte à página de Sessões Ativas e veja ambas as sessões
   - Teste encerrar sessões individuais ou todas de uma vez

## Endpoints Envolvidos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/auth/login` | Login (agora cria sessão) |
| GET | `/api/v1/auth/sessions/me` | Lista sessões do usuário atual |
| DELETE | `/api/v1/auth/sessions/me/{id}` | Encerra sessão específica |
| DELETE | `/api/v1/auth/sessions/me` | Encerra todas as outras sessões |
| POST | `/api/v1/auth/sessions/logout` | Logout da sessão atual |
| GET | `/api/v1/auth/sessions/team` | Lista sessões da equipe (owner/admin) |
| DELETE | `/api/v1/auth/sessions/team/{id}` | Encerra sessão de membro |

## Estrutura do Banco

Tabela: `sessoes_ativas`
- `id`: UUID primário
- `tenant_id`: FK para tenants
- `usuario_id`: FK para usuários
- `token_hash`: Hash SHA256 do JWT (único)
- `ip_address`: IP do cliente
- `user_agent`: Browser/dispositivo
- `inicio`: Timestamp de criação
- `ultimo_heartbeat`: Última atividade (atualizado a cada req)
- `expira_em`: Expiração (30 min de inatividade)
- `status`: ATIVA | EXPIRADA | ENCERRADA

## Segurança

✅ Sessões são invalidadas imediatamente no logout  
✅ Heartbeat automático previne expiração durante uso  
✅ Cache TTL de 30s para validação eficiente  
✅ Revogação granular por dispositivo  
✅ Owner/Admin pode gerenciar sessões da equipe  

## Arquivos Modificados

1. `services/api/core/services/auth_service.py` - Cria sessão no login
2. `services/api/core/routers/sessions.py` - Endpoint de logout
3. `services/api/main.py` - Middleware de heartbeat
4. `apps/web/src/lib/stores/app-store.ts` - Logout chama API
