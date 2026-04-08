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

O sistema foi desenhado para atender a realidade do agronegócio brasileiro, onde um proprietário pode ter 5 fazendas em estados diferentes, contratar gerentes temporários para safra, e precisar revogar acessos rapidamente quando um funcionário é demitido — situação comum e crítica no meio rural.

## Personas — Quem usa este submódulo

- **Administrador do Tenant (Owner):** Cria e gerencia usuários, define perfis de acesso, monitora logs de auditoria. Tem bypass de permissões via flag `is_owner`. Precisa de controle total sobre quem acessa quais dados.

- **Gestor de Fazenda:** Recebe perfil específico por fazenda, gerencia equipe local, visualiza logs da sua propriedade. Pode convidar operadores para sua fazenda sem afetar outras propriedades do grupo.

- **Colaborador Operacional:** Acessa funcionalidades conforme permissões atribuídas ao seu perfil. Não tem acesso a configurações de segurança. Exemplo: operador de colhedora vê apenas ordens de serviço da sua máquina.

- **Administrador Backoffice:** Gerencia tenants, visualiza métricas de uso, intervém em questões de segurança cross-tenant via permissões `backoffice:*`. Atua como suporte técnico da plataforma.

- **Auditor:** Consulta logs de auditoria sem capacidade de alteração. Perfil somente leitura. Comum em certificações (GlobalGAP, RTRS) e auditorias fiscais.

- **Funcionário Temporário (safra):** Usuário com acesso limitado por período determinado. Exemplo: trabalhador contratado apenas para colheita, com acesso restrito a ordens de serviço e registro de ponto.

## Dores que resolve

1. **Acesso não autorizado cross-fazenda:** Sem RBAC granular e isolamento por `fazenda_id`, qualquer usuário poderia acessar dados sensíveis de outras fazendas do mesmo tenant. Exemplo real: gerente da Fazenda A não pode ver custos da Fazenda B.

2. **Falta de rastreabilidade em auditorias:** Sem logs de auditoria, é impossível saber quem fez o quê e quando, comprometendo compliance (GlobalGAP, CAR, ITR) e resolução de incidentes. Auditor exige: "quem alterou o estoque de agrotóxico em 15/mar?"

3. **Gestão de acessos temporários:** Proprietário que contrata um gerente temporário precisa dar acesso limitado à fazenda X mas não às outras 3 propriedades do grupo — hoje faz isso por WhatsApp e depois esquece de revogar. Sistema permite vínculo `FazendaUsuario` com data de expiração.

4. **Permissões genéricas demais:** Perfis fixos (admin/usuário) não atendem a realidade de fazendas com hierarquias complexas (gerente, agrônomo, operador de máquinas, veterinário, estoquista). Cada função precisa de escopo específico.

5. **Vazamento entre tenants:** Sem isolamento via `tenant_id` em todas as queries, dados de um assinante poderiam vazar para outro — risco jurídico grave (LGPD). `BaseService` auto-injeta filtro de tenant em todas as queries.

6. **Sessões órfãs de funcionários demitidos:** Funcionário é desligado mas mantém acesso por sessões ativas. Sistema permite revogação imediata de todas as sessões de um usuário com um clique.

7. **2FA ignorado por "ser complicado":** Sem 2FA, contas de administradores são comprometidas via phishing. TOTP é obrigatório para perfis admin/backoffice, com fluxo de recuperação via códigos backup.

## Regras de Negócio

1. **RN-IA-001:** Todo endpoint deve extrair `tenant_id` exclusivamente via `get_tenant_id()` dependency — nunca confiar em dados do frontend. Manipulação de JWT é detectada e logada como incidente.

2. **RN-IA-002:** `BaseService` auto-injeta filtro de `tenant_id` em todas as queries. Queries raw em routers são proibidas. `TenantViolationError` retorna HTTP 403 e gera alerta de segurança.

3. **RN-IA-003:** Flag `is_owner` concede bypass de todas as permissões de tenant, exceto operações de billing (Stripe Customer Portal). Owner não pode modificar sua própria assinatura sem passar pelo gateway.

4. **RN-IA-004:** Perfis por fazenda (`FazendaUsuario.perfil_fazenda_id`) sobrescrevem o perfil global do usuário quando ele acessa aquela fazenda específica. Exemplo: usuário é "Visualizador" no tenant mas "Editor" na Fazenda A.

5. **RN-IA-005:** Tokens JWT expiram em 24 horas. Refresh tokens expiram em 30 dias com rotação — token antigo é invalidado após uso. Refresh token reutilizado indica ataque e revoga toda a cadeia.

6. **RN-IA-006:** Após 5 tentativas de login falhadas em 15 minutos, a conta é bloqueada por 30 minutos. Bloqueio é registrado em log de segurança e notifica o usuário por e-mail.

7. **RN-IA-007:** 2FA via TOTP é obrigatório para perfis de Administrador e Backoffice. Usuário recebe 10 códigos backup no setup — perda dos códigos exige contato com backoffice para reset manual com comprovação de identidade.

8. **RN-IA-008:** Toda operação de escrita (POST, PUT, PATCH, DELETE) gera um registro de auditoria com `user_id`, `tenant_id`, `action`, `resource`, `resource_id`, `timestamp`, `ip_address` e `payload_diff` (diff JSON do antes/depois).

9. **RN-IA-009:** `TenantViolationError` (tentativa de acesso cross-tenant via manipulação de ID) é logado como incidente de segurança, retorna HTTP 403 e notifica o backoffice via alerta crítico.

10. **RN-IA-010:** Convites de usuário expiram em 7 dias. Convites expirados devem ser reenviados manualmente. Link de convite é tokenizado e só pode ser usado uma vez.

11. **RN-IA-011:** Mesmo e-mail pode pertencer a múltiplos tenants (multi-tenancy por usuário). Troca de contexto entre tenants exige novo login ou seletor dedicado (fase futura).

12. **RN-IA-012:** Logout revoga o refresh token atual. Logout global (todas as sessões) invalida toda a cadeia de refresh tokens do usuário.

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `Usuario` | id (UUID), nome (String), email (String unique), senha_hash (String), is_active (Boolean), is_owner (Boolean), tenant_id (UUID FK), telefone (String), created_at (DateTime) | → Tenant, → PerfilAcesso, → FazendaUsuario[], → SessaoAtiva[], → LogAuditoria[] |
| `Tenant` | id (UUID), nome (String), cnpj_cpf (String), inscricao_estadual (String), plano_id (UUID FK), status (Enum: ativo/suspenso/inativo), stripe_customer_id (String), created_at (DateTime) | → Usuario[], → Fazenda[], → Plano, → Assinatura |
| `PerfilAcesso` | id (UUID), nome (String), tenant_id (UUID FK), permissoes (JSONB), is_system (Boolean), descricao (String), created_at (DateTime) | → Usuario[], → Permissao[] (M:N via perfil_permissoes) |
| `FazendaUsuario` | id (UUID), usuario_id (UUID FK), fazenda_id (UUID FK), perfil_fazenda_id (UUID FK), is_default (Boolean), data_vinculo (Date), data_expiracao (Date nullable) | → Usuario, → Fazenda, → PerfilAcesso |
| `Permissao` | id (UUID), modulo (String), recurso (String), acao (String), descricao (String) | → PerfilAcesso[] (M:N) |
| `SessaoAtiva` | id (UUID), usuario_id (UUID FK), token_hash (String), refresh_token_hash (String), ip_address (String), user_agent (String), device_name (String), expires_at (DateTime), created_at (DateTime) | → Usuario |
| `LogAuditoria` | id (UUID), usuario_id (UUID FK), tenant_id (UUID FK), action (String), resource (String), resource_id (UUID), payload_diff (JSONB), ip_address (String), user_agent (String), timestamp (DateTime) | → Usuario, → Tenant |
| `Convite` | id (UUID), email (String), tenant_id (UUID FK), perfil_id (UUID FK), token (String unique), expires_at (DateTime), accepted_at (DateTime nullable), created_by (UUID FK) | → Tenant, → PerfilAcesso, → Usuario (criador) |
| `TOTPSecret` | id (UUID), usuario_id (UUID FK), secret_hash (String), backup_codes_hash (JSONB), is_active (Boolean), created_at (DateTime) | → Usuario |

## Integrações Necessárias

- **Google OAuth2 / Microsoft Entra ID:** SSO para login social. Google é prioritário (90% dos produtores usam Gmail). Microsoft para grandes cooperativas com Active Directory.

- **SMTP (SendGrid/Amazon SES):** Envio de e-mails de convite, recuperação de senha, alertas de segurança (login suspeito, bloqueio de conta), notificação de 2FA.

- **Firebase Cloud Messaging:** Notificações push de sessão expirada, login suspeito, alerta de dispositivo não reconhecido.

- **Sentry / LogStash:** Centralização de logs de auditoria e incidentes de segurança. Alertas em tempo real para tentativas de violação.

- **Twilio Authy (futuro):** 2FA via SMS como fallback para usuários sem smartphone (comum em regiões rurais remotas).

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Primeiro acesso (convite)
1. Owner acessa painel de usuários e clica em "Convidar Usuário".
2. Preenche e-mail, nome, seleciona perfil de acesso global e fazendas vinculadas (múltipla escolha).
3. Opcionalmente define data de expiração do vínculo (ex: "3 meses" para temporário de safra).
4. Sistema gera token de convite com validade de 7 dias e envia e-mail com link único.
5. Convidado clica no link, valida e-mail, cria senha (mínimo 8 caracteres, 1 maiúscula, 1 número, 1 especial).
6. Se perfil for Admin/Backoffice, sistema obriga configuração de 2FA TOTP (scan QR code no Google Authenticator).
7. Sistema gera 10 códigos backup — usuário deve baixar ou imprimir (última chance de recuperação).
8. Sistema cria `Usuario`, vincula ao `Tenant`, cria `FazendaUsuario` para cada fazenda selecionada.
9. Convidado é redirecionado ao dashboard com permissões do perfil atribuído.

### Fluxo 2: Login com e-mail/senha + 2FA
1. Usuário informa e-mail e senha na tela de login.
2. Backend valida credenciais contra `senha_hash` (bcrypt, salt rounds=12).
3. Se inválidas, incrementa contador de tentativas. Se válidas, reseta contador.
4. Se contador >= 5 em 15 minutos, retorna erro "Conta bloqueada por 30 minutos" e loga incidente.
5. Se credenciais válidas e 2FA está ativo, solicita código TOTP (6 dígitos).
6. Código TOTP é validado contra `secret_hash` (janela de 30 segundos, tolerância de 1 período).
7. Código validado → gera JWT com claims (`user_id`, `tenant_id`, `permissions`, `fazenda_ids`, `is_owner`).
8. Cria registro em `SessaoAtiva` com `token_hash` e `refresh_token_hash`.
9. Frontend armazena token em memória (não localStorage) e redireciona ao dashboard.

### Fluxo 3: Troca de contexto de fazenda
1. Usuário clica no seletor de fazendas no header (dropdown com lista de fazendas vinculadas).
2. Frontend envia `fazenda_id` selecionada para endpoint `/api/v1/auth/trocar-contexto`.
3. Backend verifica `FazendaUsuario` para garantir que usuário tem vínculo com a fazenda.
4. Carrega `perfil_fazenda_id` (se houver override) e recalcula permissões efetivas.
5. Re-emite JWT com claims atualizados (`fazenda_id` ativo, `permissions` recalculadas).
6. Frontend substitui token e recarrega dados do dashboard com escopo da fazenda selecionada.

### Fluxo 4: Revogação de acesso (funcionário demitido)
1. Owner acessa "Usuários" → lista de usuários ativos.
2. Clica em "Revogar Acesso" no usuário a ser desligado.
3. Sistema exibe confirmação: "Isso irá encerrar todas as sessões ativas e impedir novos logins. Confirmar?"
4. Owner confirma. Sistema seta `Usuario.is_active = false` e `Usuario.deleted_at = now()`.
5. Todas as sessões ativas são invalidadas (`SessaoAtiva.expires_at = now()`).
6. Todos os refresh tokens são revogados.
7. Log de auditoria registra: "Acesso revogado por [owner_id]".
8. Usuário recebe e-mail de notificação (opcional, configurável).

## Casos Extremos e Exceções

- **Convite para e-mail já cadastrado em outro tenant:** Sistema permite multi-tenancy — o mesmo e-mail pode pertencer a múltiplos tenants. O convite cria um vínculo adicional. Usuário precisará de seletor de tenant no login (fase futura).

- **Owner tenta remover a si mesmo:** Bloqueado. Deve haver pelo menos 1 owner ativo por tenant. Mensagem: "Transfira a propriedade para outro usuário antes de remover seu acesso."

- **Sessão expirada durante operação longa:** Frontend intercepta 401 e tenta refresh token. Se refresh também expirou, redireciona ao login preservando URL de retorno e dados do formulário em sessionStorage.

- **2FA com celular perdido:** Fluxo de recuperação via códigos backup (gerados no setup do 2FA). Se códigos também perdidos, contato com backoffice via e-mail corporativo com comprovação de identidade (documento + selfie). Reset manual leva até 24h.

- **Migração de owner:** Transferência requer confirmação por e-mail do owner atual e do novo owner. Ambos clicam em link de confirmação. Log de auditoria registra a operação com IP e timestamp.

- **Tentativa de acesso cross-tenant via manipulação de JWT:** `BaseService` valida `tenant_id` do JWT contra o recurso acessado. Se `tenant_id` do recurso difere do JWT, lança `TenantViolationError`, loga incidente e retorna HTTP 403.

- **Usuário desativado tenta login:** Retorna erro genérico "Credenciais inválidas" (não revela que a conta existe mas está desativada). Previne enumeração de usuários.

- **Refresh token reutilizado (ataque):** Se refresh token é usado duas vezes, sistema detecta, revoga toda a cadeia de sessões do usuário e notifica por e-mail: "Sua conta pode estar comprometida. Redefina sua senha."

- **TOTP fora de sincronia:** Servidor aceita códigos com janela de ±1 período (90 segundos). Se usuário está fora dessa janela, sistema oferece sincronização manual (inserir 2 códigos consecivos).

## Critérios de Aceite (Definition of Done)

- [X] Login com e-mail/senha funcional com rate limiting (5 tentativas / 15 min) e bloqueio automático.
- [ ] SSO com Google OAuth2 funcional (Microsoft como fase posterior).
- [ ] 2FA via TOTP implementado e obrigatório para perfis admin/backoffice.
- [X] RBAC com permissões granulares (`modulo:recurso:acao`) validado em todos os endpoints.
- [X] Perfis por fazenda (`FazendaUsuario.perfil_fazenda_id`) sobrescrevendo perfil global.
- [X] Convite por e-mail com expiração de 7 dias e reenvio manual.
- [X] Log de auditoria para todas as operações de escrita com campos obrigatórios (`user_id`, `action`, `resource`, `payload_diff`).
- [X] `TenantViolationError` logado como incidente de segurança com alerta ao backoffice.
- [X] Testes de isolamento de tenant cobrindo todos os endpoints (100% de cobertura de tenant isolation).
- [N] Refresh token com rotação (token antigo invalidado após uso). (implementação futura)
- [X] Tela de sessões ativas com opção de revogar sessão remotamente (por dispositivo).
- [X] Revogação global de acesso (todas as sessões) funcional.
- [X] Recuperação de senha por e-mail com token expirável (1 hora).
- [N] Códigos backup de 2FA funcionais para recuperação de emergência. (implementação futura)

## Sugestões de Melhoria Futura

1. **Login biométrico (WebAuthn/FIDO2):** Permitir autenticação via impressão digital ou reconhecimento facial em dispositivos compatíveis. Ideal para acesso mobile em campo.

2. **SAML 2.0 para grandes cooperativas:** Integração com Identity Providers corporativos (ADFS, Okta, Azure AD). Necessário para clientes enterprise com diretório ativo próprio.

3. **Políticas de senha customizáveis por tenant:** Permitir que cada assinante defina requisitos mínimos (comprimento, complexidade, expiração, histórico).

4. **Auditoria com machine learning:** Detecção automática de padrões anômalos de acesso (login de IP incomum, horários atípicos, download em massa de dados).

5. **Delegação temporária de permissões:** Permitir que um gestor delegue suas permissões a um substituto por período definido (férias, licença).

6. **API keys para integrações M2M:** Tokens de longa duração com escopo limitado para integrações sistema-a-sistema (ERP, contabilidade).

7. **Seletor de tenant no login:** Para usuários com vínculo em múltiplos tenants, exibir dropdown de seleção após autenticação.

8. **Relatório de conformidade LGPD:** Exportar log de acessos por usuário para auditoria de privacidade de dados.
