---
modulo: Core
submodulo: Integrações Essenciais
nivel: core
core: true
dependencias_core:
  - Identidade e Acesso
dependencias_modulos: []
standalone: false
complexidade: L
assinante_alvo: todos os assinantes
---

# Integrações Essenciais

## Descrição Funcional

Submódulo que fornece a infraestrutura de integração da plataforma com sistemas externos e processos de importação/exportação de dados. Abrange três pilares: (1) API REST pública com autenticação OAuth2 para integrações sistema-a-sistema, (2) motor de webhooks para notificação de eventos em tempo real a sistemas terceiros, e (3) engine de importação/exportação de dados em formatos CSV e XLSX para migração, carga inicial e extração de relatórios. Este submódulo viabiliza a interoperabilidade do AgroSaaS com ERPs, sistemas contábeis, plataformas de marketplace agrícola e ferramentas de BI.

## Personas — Quem usa este submódulo

- **Administrador do Tenant (Owner):** Cria API keys, configura webhooks, autoriza integrações de terceiros.
- **Desenvolvedor / Integrador:** Consome a API REST para integrar AgroSaaS com ERP, contabilidade ou BI. Consulta documentação OpenAPI.
- **Gestor Administrativo:** Importa dados iniciais via planilha (fazendas, talhões, estoque, rebanho), exporta relatórios para análise externa.
- **Contador:** Exporta dados financeiros em XLSX para integração com sistema contábil.

## Dores que resolve

1. **Dados isolados em silos:** Sem API, dados do AgroSaaS ficam presos na plataforma, impossibilitando consolidação com ERP ou contabilidade.
2. **Integração manual e propensa a erros:** Sem importação de planilhas, o onboarding de fazendas com milhares de registros (talhões, estoque, animais) é inviável.
3. **Falta de eventos em tempo real:** Sem webhooks, sistemas externos precisam fazer polling constante, desperdiçando recursos e introduzindo latência.
4. **Exportação limitada:** Sem exportação estruturada, relatórios customizados exigem acesso direto ao banco de dados.
5. **Segurança em integrações:** Sem OAuth2, integrações usam credenciais de usuário, sem escopo limitado nem expiração controlada.

## Regras de Negócio

1. **RN-IE-001:** API keys são vinculadas a um `tenant_id` e têm escopo definido (lista de permissões). Nunca concedem acesso cross-tenant.
2. **RN-IE-002:** Tokens OAuth2 expiram em 1 hora. Refresh tokens expiram em 90 dias.
3. **RN-IE-003:** Rate limiting por API key: 100 req/min para plano básico, 500 req/min para plano premium, 2000 req/min para enterprise.
4. **RN-IE-004:** Webhooks devem receber resposta HTTP 2xx em até 10 segundos. Caso contrário, retry com backoff: 1min, 5min, 30min, 2h, 12h. Após 5 falhas, webhook é desativado e Owner é notificado.
5. **RN-IE-005:** Payloads de webhooks são assinados com HMAC-SHA256 usando secret do webhook. Sistema receptor deve validar assinatura.
6. **RN-IE-006:** Importação CSV/XLSX valida dados em duas fases: (1) validação de formato e tipos, (2) validação de regras de negócio. Erros são reportados por linha.
7. **RN-IE-007:** Importação de arquivos com mais de 10.000 linhas é processada de forma assíncrona (job queue). Usuário recebe notificação ao concluir.
8. **RN-IE-008:** Exportação inclui apenas dados do `tenant_id` do solicitante. Cada arquivo exportado registra log de auditoria.
9. **RN-IE-009:** A documentação da API (OpenAPI/Swagger) é gerada automaticamente a partir dos schemas FastAPI e disponível em `/api/docs`.
10. **RN-IE-010:** API keys podem ser revogadas a qualquer momento. Revogação é imediata (invalidação em cache).

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `ApiKey` | id, tenant_id, nome, key_hash, scopes (JSONB), rate_limit, is_active, expires_at, created_by, last_used_at | → Tenant, → Usuario (criador) |
| `OAuthClient` | id, tenant_id, client_id, client_secret_hash, redirect_uris, scopes, is_active | → Tenant |
| `OAuthToken` | id, client_id, user_id, access_token_hash, refresh_token_hash, scopes, expires_at | → OAuthClient, → Usuario |
| `WebhookConfig` | id, tenant_id, url, secret_hash, eventos (JSONB), is_active, falhas_consecutivas | → Tenant |
| `WebhookLog` | id, webhook_id, evento, payload, response_status, response_time_ms, tentativa, created_at | → WebhookConfig |
| `ImportJob` | id, tenant_id, usuario_id, tipo_entidade, nome_arquivo, s3_key, status (pendente/processando/concluido/erro), total_linhas, linhas_sucesso, linhas_erro, erros (JSONB), created_at, completed_at | → Tenant, → Usuario |
| `ExportJob` | id, tenant_id, usuario_id, tipo_entidade, filtros (JSONB), formato (csv/xlsx), s3_key, status, created_at, completed_at | → Tenant, → Usuario |

## Integrações Necessárias

- **Redis:** Cache de rate limiting e invalidação imediata de API keys revogadas.
- **S3 / MinIO:** Armazenamento de arquivos de importação (upload) e exportação (download).
- **Celery / ARQ (async job queue):** Processamento assíncrono de importações grandes e exportações pesadas.
- **Notificações e Alertas:** Notificação ao usuário quando import/export job é concluído ou quando webhook é desativado por falhas.
- **Sentry:** Monitoramento de erros em webhooks e jobs de importação.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Criação de API key
1. Owner acessa "Configurações" → "Integrações" → "API Keys".
2. Clica em "Nova API Key".
3. Define nome descritivo (ex: "ERP Contábil"), seleciona escopos (ex: `financeiro:leitura`, `estoque:leitura`).
4. Define data de expiração (opcional).
5. Sistema gera API key, exibe uma única vez para cópia. Armazena apenas hash.
6. API key fica listada com status, último uso e opção de revogar.

### Fluxo 2: Configuração de webhook
1. Owner acessa "Configurações" → "Integrações" → "Webhooks".
2. Clica em "Novo Webhook".
3. Define URL de destino (HTTPS obrigatório) e seleciona eventos (ex: `estoque.movimentacao.criada`, `financeiro.despesa.paga`).
4. Sistema gera secret para assinatura HMAC e exibe uma única vez.
5. Owner testa webhook com evento de teste.
6. Sistema envia payload de exemplo e exibe resultado (status HTTP, tempo de resposta).
7. Webhook ativado.

### Fluxo 3: Importação de dados via planilha
1. Usuário acessa módulo relevante (ex: Estoque) → "Importar Dados".
2. Seleciona tipo de entidade a importar.
3. Baixa template CSV/XLSX com colunas esperadas e exemplos.
4. Preenche planilha com dados reais e faz upload.
5. **Fase 1 — Validação de formato:** Sistema valida tipos de dados, campos obrigatórios, formatos de data. Retorna preview das primeiras 10 linhas.
6. **Fase 2 — Validação de negócio:** Verifica duplicatas, referências a entidades existentes, regras de negócio. Retorna relatório de erros por linha.
7. Usuário revisa erros, corrige planilha se necessário e confirma importação.
8. Se > 10.000 linhas, job é enfileirado. Notificação enviada ao concluir.
9. Se <= 10.000 linhas, processamento síncrono com progress bar.
10. Resultado final: X linhas importadas, Y erros com detalhamento.

### Fluxo 4: Exportação de relatório
1. Usuário acessa relatório desejado em qualquer módulo.
2. Aplica filtros (período, fazenda, categorias).
3. Clica em "Exportar" e seleciona formato (CSV ou XLSX).
4. Sistema gera arquivo com dados filtrados, armazena no S3.
5. Link de download é disponibilizado (válido por 24 horas).
6. Log de auditoria registra: quem exportou, quais dados, quando.

## Casos Extremos e Exceções

- **Webhook com URL interna (SSRF):** Sistema valida URL contra blocklist de IPs privados (10.x, 172.16.x, 192.168.x, localhost). Bloqueia com erro descritivo.
- **Importação com encoding incorreto:** Sistema tenta detectar encoding automaticamente (UTF-8, ISO-8859-1, Windows-1252). Se falhar, solicita seleção manual.
- **Planilha com fórmulas em vez de valores:** Parser ignora fórmulas e lê valores calculados. Se célula tiver erro (#REF!, #N/A), linha é reportada como erro.
- **API key com escopo insuficiente:** Retorna HTTP 403 com corpo descritivo indicando escopo necessário vs. escopo da key.
- **Export de dataset muito grande (> 1M linhas):** Job assíncrono obrigatório. Arquivo gerado em partes e compactado (.zip). Limite hard de 5M linhas.
- **Webhook recebe payload duplicado (retry após timeout):** Payload inclui `idempotency_key`. Sistema receptor deve usar para deduplicação.
- **Importação com referência a entidade inexistente:** Linha reportada como erro com mensagem "Talhão 'ABC' não encontrado na fazenda X". Importação continua para demais linhas.

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de API keys com geração segura, exibição única e revogação imediata.
- [ ] Autenticação OAuth2 (client credentials flow) funcional para integrações M2M.
- [ ] Rate limiting por API key com limites configuráveis por plano.
- [ ] CRUD de webhooks com seleção de eventos, secret HMAC e endpoint de teste.
- [ ] Retry automático de webhooks com backoff exponencial e desativação após 5 falhas.
- [ ] Assinatura HMAC-SHA256 em todos os payloads de webhook.
- [ ] Importação CSV/XLSX com validação em 2 fases e relatório de erros por linha.
- [ ] Templates de importação disponíveis para download por entidade.
- [ ] Processamento assíncrono para importações > 10.000 linhas com notificação.
- [ ] Exportação CSV/XLSX com filtros, link temporário e log de auditoria.
- [ ] Documentação OpenAPI auto-gerada e acessível em `/api/docs`.
- [ ] Proteção contra SSRF em URLs de webhook.
- [ ] Testes de integração cobrindo: API key auth, webhook delivery, CSV import/export.

## Sugestões de Melhoria Futura

1. **Marketplace de integrações:** Catálogo de integrações pré-configuradas com ERPs populares (TOTVS, SAP Business One, Conta Azul).
2. **GraphQL para consultas complexas:** Alternativa ao REST para integrações que precisam de queries flexíveis com múltiplos joins.
3. **Integração nativa com Google Sheets:** Planilha do Google como fonte de dados bidirecional, atualizando automaticamente.
4. **SDK em Python e JavaScript:** Bibliotecas cliente oficiais para acelerar desenvolvimento de integrações.
5. **Zapier / Make (Integromat):** Conector oficial para automações no-code.
6. **Streaming de eventos (SSE/WebSocket):** Alternativa a webhooks para integrações em tempo real sem overhead de HTTP callbacks.
