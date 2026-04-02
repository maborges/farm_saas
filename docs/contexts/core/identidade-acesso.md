---
modulo: Core
submodulo: Identidade e Acesso
nivel: core
core: true
dependencias_core: []
dependencias_modulos: []
standalone: false
complexidade: L
assinante_alvo: todos os assinantes
---

# Identidade e Acesso

## Descrição Funcional

Submódulo responsável por toda a camada de autenticação (quem é o usuário) e autorização (o que ele pode fazer). Abrange login com e-mail/senha, SSO via Google/Microsoft, autenticação de dois fatores (2FA via TOTP), gerenciamento de sessões ativas, RBAC com permissões granulares por recurso e ação, perfis por fazenda, e logs de auditoria completos. É o alicerce de segurança da plataforma.

A plataforma já possui um sistema RBAC maduro com multi-subscription, perfis por fazenda (`FazendaUsuario.perfil_fazenda_id`), papéis de backoffice administrativo e flag `is_owner` que concede bypass em permissões de tenant (exceto billing).

## Personas — Quem usa este submódulo

- **Administrador do Tenant (Owner):** Cria e gerencia usuários, define perfis de acesso, monitora logs de auditoria. Tem bypass de permissões via flag `is_owner`.
- **Gestor de Fazenda:** Recebe perfil específico por fazenda, gerencia equipe local, visualiza logs da sua propriedade.
- **Colaborador Operacional:** Acessa funcionalidades conforme permissões atribuídas ao seu perfil. Não tem acesso a configurações de segurança.
- **Administrador Backoffice:** Gerencia tenants, visualiza métricas de uso, intervém em questões de segurança cross-tenant via permissões `backoffice:*`.
- **Auditor:** Consulta logs de auditoria sem capacidade de alteração. Perfil somente leitura.

## Dores que resolve

1. **Acesso não autorizado:** Sem RBAC granular, qualquer usuário poderia acessar dados sensíveis de outras fazendas ou módulos não contratados.
2. **Falta de rastreabilidade:** Sem logs de auditoria, é impossível saber quem fez o quê e quando, comprometendo compliance e resolução de incidentes.
3. **Gestão descentralizada de senhas:** Sem SSO e 2FA, cada sistema exige credenciais separadas, aumentando risco de senhas fracas ou reutilizadas.
4. **Permissões genéricas demais:** Perfis fixos (admin/usuário) não atendem a realidade de fazendas com hierarquias complexas (gerente, agrônomo, operador de máquinas).
5. **Vazamento entre tenants:** Sem isolamento via `tenant_id` em todas as queries, dados de um assinante poderiam vazar para outro.

## Regras de Negócio

1. **RN-IA-001:** Todo endpoint deve extrair `tenant_id` exclusivamente via `get_tenant_id()` dependency — nunca confiar em dados do frontend.
2. **RN-IA-002:** `BaseService` auto-injeta filtro de `tenant_id` em todas as queries. Queries raw em routers são proibidas.
3. **RN-IA-003:** Flag `is_owner` concede bypass de todas as permissões de tenant, exceto operações de billing.
4. **RN-IA-004:** Perfis por fazenda (`FazendaUsuario.perfil_fazenda_id`) sobrescrevem o perfil global do usuário quando ele acessa aquela fazenda específica.
5. **RN-IA-005:** Tokens JWT expiram em 24 horas. Refresh tokens expiram em 30 dias.
6. **RN-IA-006:** Após 5 tentativas de login falhadas em 15 minutos, a conta é bloqueada por 30 minutos.
7. **RN-IA-007:** 2FA via TOTP é obrigatório para perfis de Administrador e Backoffice.
8. **RN-IA-008:** Toda operação de escrita (POST, PUT, PATCH, DELETE) gera um registro de auditoria com `user_id`, `tenant_id`, `action`, `resource`, `timestamp`, `ip_address` e `payload_diff`.
9. **RN-IA-009:** `TenantViolationError` (tentativa de acesso cross-tenant) é logado como incidente de segurança e retorna HTTP 403.
10. **RN-IA-010:** Convites de usuário expiram em 7 dias. Convites expirados devem ser reenviados manualmente.

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `Usuario` | id, nome, email, senha_hash, is_active, is_owner, tenant_id, created_at | → Tenant, → PerfilAcesso, → FazendaUsuario[] |
| `Tenant` | id, nome, plano_id, status, stripe_customer_id | → Usuario[], → Fazenda[], → Plano |
| `PerfilAcesso` | id, nome, tenant_id, permissoes (JSONB), is_system | → Usuario[], → Permissao[] |
| `FazendaUsuario` | id, usuario_id, fazenda_id, perfil_fazenda_id | → Usuario, → Fazenda, → PerfilAcesso |
| `Permissao` | id, modulo, recurso, acao | → PerfilAcesso[] (M:N) |
| `SessaoAtiva` | id, usuario_id, token_hash, ip_address, user_agent, expires_at | → Usuario |
| `LogAuditoria` | id, usuario_id, tenant_id, action, resource, resource_id, payload_diff, ip_address, timestamp | → Usuario, → Tenant |
| `Convite` | id, email, tenant_id, perfil_id, token, expires_at, accepted_at | → Tenant, → PerfilAcesso |

## Integrações Necessárias

- **Google OAuth2 / Microsoft Entra ID:** SSO para login social.
- **SMTP (SendGrid/SES):** Envio de e-mails de convite, recuperação de senha, alertas de segurança.
- **Firebase Cloud Messaging:** Notificações push de sessão expirada ou login suspeito.
- **Sentry / LogStash:** Centralização de logs de auditoria e incidentes de segurança.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Primeiro acesso (convite)
1. Owner acessa painel de usuários e clica em "Convidar Usuário".
2. Preenche e-mail, seleciona perfil de acesso e fazendas vinculadas.
3. Sistema gera token de convite com validade de 7 dias e envia e-mail.
4. Convidado clica no link, cria senha e opcionalmente configura 2FA.
5. Sistema cria `Usuario`, vincula ao `Tenant`, cria `FazendaUsuario` para cada fazenda selecionada.
6. Convidado é redirecionado ao dashboard com permissões do perfil atribuído.

### Fluxo 2: Login com e-mail/senha + 2FA
1. Usuário informa e-mail e senha na tela de login.
2. Backend valida credenciais. Se inválidas, incrementa contador de tentativas.
3. Se 2FA está ativo, solicita código TOTP.
4. Código validado → gera JWT com claims (`user_id`, `tenant_id`, `permissions`, `fazenda_ids`).
5. Cria registro em `SessaoAtiva`.
6. Frontend armazena token e redireciona ao dashboard.

### Fluxo 3: Troca de contexto de fazenda
1. Usuário clica no seletor de fazendas no header.
2. Frontend envia `fazenda_id` selecionada.
3. Backend verifica `FazendaUsuario` e carrega `perfil_fazenda_id` (se houver override).
4. Novo token JWT é emitido com permissões ajustadas ao contexto da fazenda.

## Casos Extremos e Exceções

- **Convite para e-mail já cadastrado em outro tenant:** Sistema permite multi-tenancy — o mesmo e-mail pode pertencer a múltiplos tenants. O convite cria um vínculo adicional.
- **Owner tenta remover a si mesmo:** Bloqueado. Deve haver pelo menos 1 owner ativo por tenant.
- **Sessão expirada durante operação longa:** Frontend intercepta 401 e tenta refresh token. Se refresh também expirou, redireciona ao login preservando URL de retorno.
- **2FA com celular perdido:** Fluxo de recuperação via códigos backup (gerados no setup do 2FA) ou validação manual pelo suporte com comprovação de identidade.
- **Migração de owner:** Transferência requer confirmação por e-mail do owner atual e do novo owner. Log de auditoria registra a operação.
- **Tentativa de acesso cross-tenant via manipulação de JWT:** `BaseService` valida `tenant_id` do JWT contra o recurso acessado. `TenantViolationError` é lançado e logado.
- **Usuário desativado tenta login:** Retorna erro genérico "Credenciais inválidas" (não revela que a conta existe mas está desativada).

## Critérios de Aceite (Definition of Done)

- [ ] Login com e-mail/senha funcional com rate limiting (5 tentativas / 15 min).
- [ ] SSO com Google OAuth2 funcional (Microsoft como fase posterior).
- [ ] 2FA via TOTP implementado e obrigatório para perfis admin/backoffice.
- [ ] RBAC com permissões granulares (`modulo:recurso:acao`) validado em todos os endpoints.
- [ ] Perfis por fazenda (`FazendaUsuario.perfil_fazenda_id`) sobrescrevendo perfil global.
- [ ] Convite por e-mail com expiração de 7 dias e reenvio manual.
- [ ] Log de auditoria para todas as operações de escrita com campos obrigatórios.
- [ ] `TenantViolationError` logado como incidente de segurança com alerta ao backoffice.
- [ ] Testes de isolamento de tenant cobrindo todos os endpoints (100% de cobertura de tenant isolation).
- [ ] Refresh token com rotação (token antigo invalidado após uso).
- [ ] Tela de sessões ativas com opção de revogar sessão remotamente.

## Sugestões de Melhoria Futura

1. **Login biométrico (WebAuthn/FIDO2):** Permitir autenticação via impressão digital ou reconhecimento facial em dispositivos compatíveis.
2. **SAML 2.0 para grandes cooperativas:** Integração com Identity Providers corporativos (ADFS, Okta).
3. **Políticas de senha customizáveis por tenant:** Permitir que cada assinante defina requisitos mínimos (comprimento, complexidade, expiração).
4. **Auditoria com machine learning:** Detecção automática de padrões anômalos de acesso (login de IP incomum, horários atípicos).
5. **Delegação temporária de permissões:** Permitir que um gestor delegue suas permissões a um substituto por período definido (férias, licença).
6. **API keys para integrações M2M:** Tokens de longa duração com escopo limitado para integrações sistema-a-sistema.
