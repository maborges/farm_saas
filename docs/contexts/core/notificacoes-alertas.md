---
modulo: Core
submodulo: Notificações e Alertas
nivel: core
core: true
dependencias_core:
  - Identidade e Acesso
  - Configurações Globais
dependencias_modulos: []
standalone: false
complexidade: M
assinante_alvo: todos os assinantes
---

# Notificações e Alertas

## Descrição Funcional

Submódulo responsável pelo envio e gerenciamento de notificações na plataforma, cobrindo três canais: push (via Firebase Cloud Messaging), e-mail (via SMTP/SendGrid) e SMS (via Twilio). Além de notificações transacionais (convites, recuperação de senha), o submódulo implementa alertas baseados em regras de negócio: vencimento de documentos, estoque crítico, tarefas atrasadas, condições climáticas adversas, e marcos de safra. Inclui central de notificações in-app com histórico, filtros e marcação de lido/não lido.

Este submódulo foi desenhado para a realidade do produtor rural brasileiro, que muitas vezes está em campo com conectividade limitada e depende de notificações via WhatsApp (integração futura) e SMS. Alertas são classificados por severidade e contexto, garantindo que informações críticas (geada, estoque zerado de combustível) cheguem imediatamente ao gestor.

O sistema de regras de alerta permite automação completa: o produtor configura uma vez e recebe notificações proativas sem necessidade de consulta manual ao sistema.

## Personas — Quem usa este submódulo

- **Administrador do Tenant (Owner):** Configura regras de alerta globais, define canais preferidos, monitora alertas críticos do portfólio. Recebe notificações de todos os tipos.

- **Gestor de Fazenda:** Recebe alertas operacionais da sua fazenda (estoque baixo, tarefas atrasadas), configura preferências pessoais de canal. Pode definir que recebe SMS apenas para emergências.

- **Colaborador Operacional:** Recebe notificações de tarefas atribuídas, prazos e lembretes via push ou SMS. Exemplo: operador de colhedora recebe alerta de manutenção preventiva.

- **Agrônomo / Consultor:** Recebe alertas de marcos de safra (plantio, colheita) e condições críticas (praga detectada, geada prevista). Precisa de antecedência para planejamento.

- **Contador Rural:** Recebe alertas de vencimento de obrigações fiscais (ITR, CCIR, DAP) com 60 e 30 dias de antecedência.

- **Backoffice da Plataforma:** Monitora saúde do sistema de notificações, taxa de entrega e falhas. Recebe alertas de falha em massa de provedores.

## Dores que resolve

1. **Informação tardia:** Sem alertas proativos, o gestor só descobre estoque zerado quando precisa do insumo, ou documento vencido quando é autuado. Exemplo real: produtor multado em R$ 50.000 por CCIR vencido.

2. **Sobrecarga de informação:** Sem filtragem inteligente, todos recebem tudo, gerando fadiga de notificação e perda de alertas críticos. Sistema permite configuração granular por tipo e severidade.

3. **Canal único:** Apenas e-mail não atinge operadores de campo que raramente checam caixa de entrada. Multi-canal (push, SMS, WhatsApp) garante que mensagem chegue.

4. **Sem histórico:** Notificações efêmeras (push) não ficam registradas, dificultando auditoria de "quem foi avisado sobre o quê". Todas as notificações são persistidas com histórico de envio.

5. **Alertas manuais:** Gestor precisa lembrar manualmente de cobrar vacinação, vencimento de licenças ou manutenção de máquinas. Automação elimina esquecimentos.

6. **Falta de contexto:** Alerta genérico "estoque baixo" não informa qual produto, quanto tem, quanto precisa. Notificações incluem contexto completo e link direto para ação.

7. **Alertas ignorados:** Sem classificação por severidade, alerta crítico se perde entre informativos. Sistema usa cores, sons e canais diferentes por severidade.

## Regras de Negócio

1. **RN-NA-001:** Toda notificação é registrada na tabela `Notificacao` independente do canal de envio. Registro inclui título, mensagem, severidade, destinatários e status de envio.

2. **RN-NA-002:** Usuários podem configurar preferências de canal por tipo de notificação (ex: push para tarefas, e-mail para relatórios, SMS para emergências). Preferências são respeitadas exceto para alertas críticos.

3. **RN-NA-003:** Alertas são classificados por severidade: `info` (azul), `warning` (amarelo), `critical` (vermelho). Alertas `critical` são enviados por todos os canais ativos do usuário, ignorando preferências.

4. **RN-NA-004:** Regras de alerta podem ser configuradas com condição, limiar e frequência (ex: "Estoque de diesel < 500L, verificar diariamente, alertar uma vez"). Condições usam operadores: <, >, =, >=, <=, !=.

5. **RN-NA-005:** Notificações não lidas há mais de 7 dias são rebaixadas para histórico mas não excluídas. Histórico é mantido por 90 dias.

6. **RN-NA-006:** E-mails de notificação respeitam opt-out por categoria. Notificações de segurança (login suspeito, violação de tenant) não podem ser desativadas.

7. **RN-NA-007:** SMS é limitado ao orçamento mensal definido pelo plano (campo `sms_mensal_limit`). Ao atingir 80%, sistema alerta o Owner. Ao atingir 100%, SMS é bloqueado até reset.

8. **RN-NA-008:** Notificações são filtradas por `fazenda_id` — colaborador recebe apenas alertas das fazendas em que tem vínculo. Owner recebe alertas de todas as fazendas.

9. **RN-NA-009:** Deduplicação: mesma regra de alerta não gera notificação duplicada dentro de janela configurável (padrão: 24h). Exceção: alerta crítico pode repetir a cada 4h se condição persistir.

10. **RN-NA-010:** Notificações push expiram em 7 dias no Firebase. Notificações não entregues (usuário offline) são descartadas após expiração.

11. **RN-NA-011:** Webhooks de notificação (integração futura com WhatsApp) devem receber resposta HTTP 2xx em até 5 segundos. Caso contrário, retry com backoff.

12. **RN-NA-012:** Alertas de vencimento de documentos são disparados em T-60, T-30, T-7 e T-1 dias. Após vencimento, alerta diário até regularização.

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `Notificacao` | id (UUID), tenant_id (UUID FK), fazenda_id (UUID FK nullable), usuario_id (UUID FK), tipo (String 50), titulo (String 200), mensagem (Text), severidade (Enum: info/warning/critical), canal_envio (JSONB: [push, email, sms]), lida (Boolean), lida_em (DateTime nullable), created_at (DateTime), expires_at (DateTime nullable) | → Tenant, → Fazenda, → Usuario, → HistoricoEnvio[] |
| `RegraAlerta` | id (UUID), tenant_id (UUID FK), fazenda_id (UUID FK nullable), nome (String 100), tipo (String 50), condicao (JSONB), limiar (JSONB), frequencia_check (Enum: hourly/daily/weekly), canal_preferido (Enum: push/email/sms), severidade (Enum), is_active (Boolean), created_by (UUID FK), created_at (DateTime) | → Tenant, → Fazenda, → Usuario |
| `PreferenciaNotificacao` | id (UUID), usuario_id (UUID FK), tipo_notificacao (String 50), canal_push (Boolean default true), canal_email (Boolean default true), canal_sms (Boolean default false), ativo (Boolean default true) | → Usuario |
| `HistoricoEnvio` | id (UUID), notificacao_id (UUID FK), canal (Enum: push/email/sms), status (Enum: enviado/falhou/pendente), tentativas (Integer default 0), erro (Text nullable), enviado_em (DateTime nullable) | → Notificacao |
| `DispositivoPush` | id (UUID), usuario_id (UUID FK), fcm_token (String 512), device_name (String 100), platform (Enum: ios/android/web), is_active (Boolean default true), last_seen_at (DateTime nullable) | → Usuario |
| `TemplateNotificacao` | id (UUID), tenant_id (UUID FK nullable), tipo (String 50), assunto (String 200), corpo (Text), canais (JSONB), is_system (Boolean) | → Tenant (nullable para templates globais) |

## Integrações Necessárias

- **Firebase Cloud Messaging (FCM):** Push notifications para web e mobile. Tokens registrados por dispositivo.

- **SMTP / SendGrid / Amazon SES:** Envio de e-mails transacionais e de alerta. Templates HTML responsivos.

- **Twilio:** Envio de SMS para alertas críticos e confirmações. Limite de caracteres por SMS (160).

- **Módulo Operacional (Estoque):** Monitora níveis de estoque para alertas de estoque crítico. Webhook de `estoque.movimentacao`.

- **Módulo Agrícola (Safras):** Monitora marcos de safra e datas de operações planejadas vs. realizadas. Alertas de atraso.

- **Módulo Financeiro:** Monitora vencimentos de contas a pagar e fluxo de caixa. Alertas de saldo negativo.

- **API de Clima (OpenWeather / INMET):** Condições meteorológicas adversas para alertas de geada, granizo, seca. Integração futura.

- **Módulo Imóveis:** Vencimento de documentos legais (CCIR, ITR, CAR) para alertas de regularização.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Configuração de regra de alerta
1. Owner acessa "Configurações" → "Alertas".
2. Clica em "Nova Regra de Alerta".
3. Seleciona tipo: Estoque Crítico, Tarefa Atrasada, Vencimento de Documento, Condição Climática, Personalizado.
4. Define condição e limiar (ex: tipo=Estoque, produto="Diesel", operador="<", valor=500, unidade="L").
5. Define frequência de verificação (a cada 1h, 6h, 12h, 24h).
6. Define severidade e canais de envio.
7. Define destinatários (usuários específicos ou perfis de acesso).
8. Salva regra. Cron job começa a verificar a condição na frequência definida.

### Fluxo 2: Disparo de alerta automático
1. Cron job verifica regras ativas na frequência configurada (worker em background).
2. Condição da regra é avaliada contra dados atuais (ex: estoque de diesel = 450L < 500L).
3. Verifica deduplicação: se alerta igual foi enviado nas últimas 24h, ignora.
4. Cria registro em `Notificacao` com dados da regra.
5. Para cada destinatário, verifica `PreferenciaNotificacao` e canais ativos.
6. Envia por cada canal aplicável: push via FCM, e-mail via SMTP, SMS via Twilio.
7. Registra resultado em `HistoricoEnvio` (sucesso ou falha com motivo).
8. Se falha, agenda retry com backoff exponencial.

### Fluxo 3: Central de notificações in-app
1. Usuário clica no ícone de sino no header.
2. Dropdown exibe últimas 10 notificações não lidas, ordenadas por data.
3. Badge no ícone mostra contador de não lidas (atualizado em tempo real via WebSocket).
4. Clicar em notificação marca como lida e redireciona ao contexto relevante (ex: tela de estoque).
5. Link "Ver todas" abre página completa com filtros por tipo, severidade, data e fazenda.
6. Ação "Marcar todas como lidas" disponível.
7. Notificações com mais de 7 dias são movidas para aba "Histórico".

### Fluxo 4: Configuração de preferências de notificação
1. Usuário acessa "Perfil" → "Preferências de Notificação".
2. Vê lista de tipos de notificação (Tarefas, Alertas de Estoque, Vencimentos, Relatórios, etc.).
3. Para cada tipo, toggle para ativar/desativar e checkboxes para canais (push, e-mail, SMS).
4. Alertas críticos não podem ser desativados.
5. Usuário salva preferências.
6. Preferências são aplicadas imediatamente a novas notificações.

## Casos Extremos e Exceções

- **FCM token expirado/inválido:** Sistema marca `DispositivoPush.is_active = false` após 3 falhas consecutivas. Notificação é entregue pelos canais restantes. Usuário recebe e-mail: "Seu dispositivo não está recebendo notificações push."

- **Limite de SMS atingido:** Notificações SMS ficam com status `pendente`. Owner recebe alerta por e-mail para upgrade ou aguardar reset mensal. Mensagem: "Limite de SMS atingido (X/Y). Upgrade de plano para mais SMS."

- **Usuário sem nenhum canal ativo:** Notificação é criada no banco (visível in-app) mas sem envio externo. Log warning para backoffice investigar.

- **Regra de alerta com condição inválida (bug):** Regra é desativada automaticamente após 5 erros consecutivos de avaliação. Owner é notificado: "Regra de alerta 'X' foi desativada devido a erros de avaliação."

- **Centenas de alertas simultâneos (surto):** Sistema agrupa notificações do mesmo tipo em digest (ex: "15 itens de estoque abaixo do mínimo") ao invés de enviar 15 notificações separadas. Digest é enviado a cada hora.

- **Falha do provedor de e-mail:** Retry com backoff exponencial (1min, 5min, 30min, 2h). Após 4 tentativas, marca como falha e notifica via outro canal. Backoffice é alertado para falha em massa.

- **Usuário inativo recebe notificação:** Sistema filtra usuários inativos antes de enviar. Notificação é descartada com log.

- **Condição de alerta deixa de existir antes do envio:** Exemplo: estoque de diesel volta para 600L antes do alerta ser enviado. Sistema cancela notificação pendente.

- **Fuso horário do usuário:** Alertas agendados (ex: digest diário às 8h) respeitam o fuso horário do usuário.

## Critérios de Aceite (Definition of Done)

- [ ] Central de notificações in-app com listagem, filtros e marcação de lido/não lido.
- [ ] Badge de contador de não lidas no ícone de sino com atualização em tempo real (WebSocket ou polling).
- [ ] Envio de e-mail funcional via SMTP configurado pelo tenant.
- [ ] Envio de push notification via Firebase Cloud Messaging.
- [ ] CRUD de regras de alerta com condição, limiar, frequência e destinatários.
- [ ] Cron job de verificação de regras funcionando nas frequências configuradas.
- [ ] Deduplicação de alertas com janela configurável.
- [ ] Preferências de canal por tipo de notificação configuráveis pelo usuário.
- [ ] Histórico de envio com status (enviado/falhou/pendente) e detalhes de erro.
- [ ] Digest de alertas quando volume excede 5 notificações do mesmo tipo em 1 hora.
- [ ] Testes de integração cobrindo fluxo completo: regra → avaliação → envio → registro.
- [ ] Retry automático com backoff exponencial para falhas de envio.
- [ ] Classificação por severidade com cores e ícones distintos.

## Sugestões de Melhoria Futura

1. **Notificações via WhatsApp Business API:** Canal mais utilizado no meio rural brasileiro que SMS. Integração com provider oficial (Zenvia, Take Blip).

2. **Alertas com IA preditiva:** Usar dados históricos para prever estoque zero, detectar anomalias de consumo e antecipar alertas. Exemplo: "Baseado no consumo médio, diesel acabará em 3 dias."

3. **Escalonamento de alertas:** Se alerta `critical` não for lido em 30 minutos, escalonar para o próximo nível hierárquico (gestor → owner).

4. **Dashboard de saúde de notificações:** Métricas de taxa de entrega, taxa de leitura e tempo médio de resposta por canal.

5. **Templates personalizáveis:** Permitir que o tenant personalize o texto e layout dos e-mails de notificação.

6. **Integração com calendário:** Alertas de tarefas e vencimentos sincronizados com Google Calendar / Outlook.

7. **Notificações por voz (robocall):** Para alertas críticos em áreas com baixa conectividade, chamada telefônica com mensagem gravada.

8. **Geofencing para alertas:** Notificações baseadas em localização do usuário. Exemplo: alerta de geada quando usuário está próximo da fazenda.

9. **Ações rápidas na notificação:** Botões de ação direta na notificação push (ex: "Aprovar", "Adiar", "Ver detalhes").

10. **Priorização inteligente:** Machine learning para priorizar notificações baseado em comportamento do usuário (quais notificações ele mais lê).
