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

## Personas — Quem usa este submódulo

- **Administrador do Tenant (Owner):** Configura regras de alerta globais, define canais preferidos, monitora alertas críticos do portfólio.
- **Gestor de Fazenda:** Recebe alertas operacionais da sua fazenda (estoque baixo, tarefas atrasadas), configura preferências pessoais de canal.
- **Colaborador Operacional:** Recebe notificações de tarefas atribuídas, prazos e lembretes via push ou SMS.
- **Agrônomo / Consultor:** Recebe alertas de marcos de safra (plantio, colheita) e condições críticas (praga detectada, geada prevista).

## Dores que resolve

1. **Informação tardia:** Sem alertas proativos, o gestor só descobre estoque zerado quando precisa do insumo, ou documento vencido quando é autuado.
2. **Sobrecarga de informação:** Sem filtragem inteligente, todos recebem tudo, gerando fadiga de notificação e perda de alertas críticos.
3. **Canal único:** Apenas e-mail não atinge operadores de campo que raramente checam caixa de entrada.
4. **Sem histórico:** Notificações efêmeras (push) não ficam registradas, dificultando auditoria de "quem foi avisado sobre o quê".
5. **Alertas manuais:** Gestor precisa lembrar manualmente de cobrar vacinação, vencimento de licenças ou manutenção de máquinas.

## Regras de Negócio

1. **RN-NA-001:** Toda notificação é registrada na tabela `Notificacao` independente do canal de envio.
2. **RN-NA-002:** Usuários podem configurar preferências de canal por tipo de notificação (ex: push para tarefas, e-mail para relatórios, SMS para emergências).
3. **RN-NA-003:** Alertas são classificados por severidade: `info`, `warning`, `critical`. Alertas `critical` são enviados por todos os canais ativos do usuário.
4. **RN-NA-004:** Regras de alerta podem ser configuradas com condição, limiar e frequência (ex: "Estoque de diesel < 500L, verificar diariamente, alertar uma vez").
5. **RN-NA-005:** Notificações não lidas há mais de 7 dias são rebaixadas para histórico mas não excluídas.
6. **RN-NA-006:** E-mails de notificação respeitam opt-out por categoria. Notificações de segurança (login suspeito, violação de tenant) não podem ser desativadas.
7. **RN-NA-007:** SMS é limitado ao orçamento mensal definido pelo plano (campo `sms_mensal_limit`). Ao atingir 80%, sistema alerta o Owner.
8. **RN-NA-008:** Notificações são filtradas por `fazenda_id` — colaborador recebe apenas alertas das fazendas em que tem vínculo.
9. **RN-NA-009:** Deduplicação: mesma regra de alerta não gera notificação duplicada dentro de janela configurável (padrão: 24h).

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `Notificacao` | id, tenant_id, fazenda_id, usuario_id, tipo, titulo, mensagem, severidade, canal_envio, lida, lida_em, created_at | → Tenant, → Fazenda, → Usuario |
| `RegraAlerta` | id, tenant_id, fazenda_id, nome, condicao (JSONB), limiar, frequencia_check, canal_preferido, severidade, is_active | → Tenant, → Fazenda |
| `PreferenciaNotificacao` | id, usuario_id, tipo_notificacao, canal_push, canal_email, canal_sms, ativo | → Usuario |
| `HistoricoEnvio` | id, notificacao_id, canal, status (enviado/falhou/pendente), tentativas, erro, enviado_em | → Notificacao |
| `DispositivoPush` | id, usuario_id, fcm_token, device_name, platform (ios/android/web), is_active | → Usuario |

## Integrações Necessárias

- **Firebase Cloud Messaging (FCM):** Push notifications para web e mobile.
- **SMTP / SendGrid / Amazon SES:** Envio de e-mails transacionais e de alerta.
- **Twilio:** Envio de SMS para alertas críticos e confirmações.
- **Módulo Operacional (Estoque):** Monitora níveis de estoque para alertas de estoque crítico.
- **Módulo Agrícola (Safras):** Monitora marcos de safra e datas de operações planejadas vs. realizadas.
- **Módulo Financeiro:** Monitora vencimentos de contas a pagar e fluxo de caixa.
- **API de Clima (OpenWeather / INMET):** Condições meteorológicas adversas para alertas de geada, granizo, seca.

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
1. Cron job verifica regras ativas na frequência configurada.
2. Condição da regra é avaliada contra dados atuais (ex: estoque de diesel = 450L < 500L).
3. Verifica deduplicação: se alerta igual foi enviado nas últimas 24h, ignora.
4. Cria registro em `Notificacao` com dados da regra.
5. Para cada destinatário, verifica `PreferenciaNotificacao` e canais ativos.
6. Envia por cada canal aplicável: push via FCM, e-mail via SMTP, SMS via Twilio.
7. Registra resultado em `HistoricoEnvio` (sucesso ou falha com motivo).

### Fluxo 3: Central de notificações in-app
1. Usuário clica no ícone de sino no header.
2. Dropdown exibe últimas 10 notificações não lidas, ordenadas por data.
3. Badge no ícone mostra contador de não lidas.
4. Clicar em notificação marca como lida e redireciona ao contexto relevante (ex: tela de estoque).
5. Link "Ver todas" abre página completa com filtros por tipo, severidade, data e fazenda.
6. Ação "Marcar todas como lidas" disponível.

## Casos Extremos e Exceções

- **FCM token expirado/inválido:** Sistema marca `DispositivoPush.is_active = false` após 3 falhas consecutivas. Notificação é entregue pelos canais restantes.
- **Limite de SMS atingido:** Notificações SMS ficam com status `pendente`. Owner recebe alerta por e-mail para upgrade ou aguardar reset mensal.
- **Usuário sem nenhum canal ativo:** Notificação é criada no banco (visível in-app) mas sem envio externo. Log warning.
- **Regra de alerta com condição inválida (bug):** Regra é desativada automaticamente após 5 erros consecutivos de avaliação. Owner é notificado.
- **Centenas de alertas simultâneos (surto):** Sistema agrupa notificações do mesmo tipo em digest (ex: "15 itens de estoque abaixo do mínimo") ao invés de enviar 15 notificações separadas.
- **Falha do provedor de e-mail:** Retry com backoff exponencial (1min, 5min, 30min, 2h). Após 4 tentativas, marca como falha e notifica via outro canal.

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

## Sugestões de Melhoria Futura

1. **Notificações via WhatsApp Business API:** Canal mais utilizado no meio rural brasileiro que SMS.
2. **Alertas com IA preditiva:** Usar dados históricos para prever estoque zero, detectar anomalias de consumo e antecipar alertas.
3. **Escalonamento de alertas:** Se alerta `critical` não for lido em 30 minutos, escalonar para o próximo nível hierárquico (gestor → owner).
4. **Dashboard de saúde de notificações:** Métricas de taxa de entrega, taxa de leitura e tempo médio de resposta por canal.
5. **Templates personalizáveis:** Permitir que o tenant personalize o texto e layout dos e-mails de notificação.
6. **Integração com calendário:** Alertas de tarefas e vencimentos sincronizados com Google Calendar / Outlook.
