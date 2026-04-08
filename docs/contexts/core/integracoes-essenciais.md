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

Submódulo que fornece a infraestrutura de integração da plataforma com sistemas externos e processos de importação/exportação de dados. Abrange três pilares: (1) API REST pública com autenticação OAuth2 para integrações sistema-a-sistema, (2) motor de webhooks para notificação de eventos em tempo real a sistemas terceiros, e (3) engine de importação/exportação de dados em formatos CSV e XLSX para migração, carga inicial e extração de relatórios.

Este submódulo viabiliza a interoperabilidade do AgroSaaS com ERPs (TOTVS, SAP Agri), sistemas contábeis (Domínio, Contmatic), plataformas de marketplace agrícola (Agrofy, MF Rural) e ferramentas de BI (Power BI, Tableau).

O foco é eliminar o retrabalho de digitação e garantir que dados fluam automaticamente entre sistemas, reduzindo erros e liberando tempo do produtor para atividades estratégicas.

## Personas — Quem usa este submódulo

- **Administrador do Tenant (Owner):** Cria API keys, configura webhooks, autoriza integrações de terceiros. Precisa de visão clara de quais sistemas estão conectados e quais dados estão sendo compartilhados.

- **Desenvolvedor / Integrador:** Consome a API REST para integrar AgroSaaS com ERP, contabilidade ou BI. Consulta documentação OpenAPI, testa endpoints em sandbox e implementa integrações customizadas.

- **Gestor Administrativo:** Importa dados iniciais via planilha (fazendas, talhões, estoque, rebanho), exporta relatórios para análise externa. Usuário não-técnico que depende de import/export para onboarding.

- **Contador:** Exporta dados financeiros em XLSX para integração com sistema contábil. Importa lançamentos de despesas e receitas do escritório de contabilidade.

- **Analista de BI:** Consome API ou exporta dados brutos para ferramentas de análise. Cria dashboards customizados e relatórios gerenciais.

- **Backoffice da Plataforma:** Gerencia integrações em nível de plataforma, monitora saúde de webhooks, rate limiting e falhas de integração.

## Dores que resolve

1. **Dados isolados em silos:** Sem API, dados do AgroSaaS ficam presos na plataforma, impossibilitando consolidação com ERP ou contabilidade. Contador precisa digitar dados manualmente.

2. **Integração manual e propensa a erros:** Sem importação de planilhas, o onboarding de fazendas com milhares de registros (talhões, estoque, animais) é inviável. Digitação manual introduz erros.

3. **Falta de eventos em tempo real:** Sem webhooks, sistemas externos precisam fazer polling constante, desperdiçando recursos e introduzindo latência. Exemplo: ERP só sabe de venda de grãos 24h depois.

4. **Exportação limitada:** Sem exportação estruturada, relatórios customizados exigem acesso direto ao banco de dados. Analista de BI depende de TI para extrair dados.

5. **Segurança em integrações:** Sem OAuth2, integrações usam credenciais de usuário, sem escopo limitado nem expiração controlada. Risco de vazamento de credenciais.

6. **Migração de sistema legado:** Produtor que migra de planilhas ou outro software não tem como importar dados históricos. Perde-se rastreabilidade.

7. **Conciliação bancária manual:** Sem integração com bancos, conciliação é feita manualmente. Erros de lançamento passam despercebidos.

## Regras de Negócio

1. **RN-IE-001:** API keys são vinculadas a um `tenant_id` e têm escopo definido (lista de permissões). Nunca concedem acesso cross-tenant. Escopos seguem formato `modulo:recurso:acao` (ex: `financeiro:lancamento:leitura`).

2. **RN-IE-002:** Tokens OAuth2 expiram em 1 hora. Refresh tokens expiram em 90 dias com rotação. Refresh token reutilizado indica ataque e revoga toda a cadeia.

3. **RN-IE-003:** Rate limiting por API key: 100 req/min para plano Essencial, 500 req/min para Profissional, 2000 req/min para Enterprise. Limites são configuráveis por tenant.

4. **RN-IE-004:** Webhooks devem receber resposta HTTP 2xx em até 10 segundos. Caso contrário, retry com backoff: 1min, 5min, 30min, 2h, 12h. Após 5 falhas, webhook é desativado e Owner é notificado.

5. **RN-IE-005:** Payloads de webhooks são assinados com HMAC-SHA256 usando secret do webhook. Sistema receptor deve validar assinatura para garantir autenticidade.

6. **RN-IE-006:** Importação CSV/XLSX valida dados em duas fases: (1) validação de formato e tipos, (2) validação de regras de negócio. Erros são reportados por linha com mensagem descritiva.

7. **RN-IE-007:** Importação de arquivos com mais de 10.000 linhas é processada de forma assíncrona (job queue). Usuário recebe notificação ao concluir.

8. **RN-IE-008:** Exportação inclui apenas dados do `tenant_id` do solicitante. Cada arquivo exportado registra log de auditoria com `user_id`, `timestamp`, `entidade`, `filtros`.

9. **RN-IE-009:** A documentação da API (OpenAPI/Swagger) é gerada automaticamente a partir dos schemas FastAPI e disponível em `/api/docs`. Versão da API é semântica (v1, v2).

10. **RN-IE-010:** API keys podem ser revogadas a qualquer momento. Revogação é imediata (invalidação em cache Redis). Tokens ativos permanecem válidos até expiração.

11. **RN-IE-011:** Webhooks suportam no máximo 10 URLs por tenant. URLs devem usar HTTPS (exceto localhost para desenvolvimento).

12. **RN-IE-012:** Importação de dados duplicados (mesmo ID externo) atualiza registro existente ao invés de criar duplicado. Comportamento configurável: atualizar ou ignorar.

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `ApiKey` | id (UUID), tenant_id (UUID FK), nome (String 100), key_hash (String 256), scopes (JSONB), rate_limit (Integer default 100), is_active (Boolean default true), expires_at (DateTime nullable), created_by (UUID FK), last_used_at (DateTime nullable), created_at (DateTime) | → Tenant, → Usuario (criador) |
| `OAuthClient` | id (UUID), tenant_id (UUID FK), client_id (String 64 unique), client_secret_hash (String 256), redirect_uris (JSONB), scopes (JSONB), is_active (Boolean default true), created_at (DateTime) | → Tenant |
| `OAuthToken` | id (UUID), client_id (UUID FK), user_id (UUID FK), access_token_hash (String 256), refresh_token_hash (String 256), scopes (JSONB), expires_at (DateTime), created_at (DateTime) | → OAuthClient, → Usuario |
| `WebhookConfig` | id (UUID), tenant_id (UUID FK), url (String 512), secret_hash (String 256), eventos (JSONB), is_active (Boolean default true), falhas_consecutivas (Integer default 0), ultimo_sucesso_at (DateTime nullable), created_at (DateTime) | → Tenant |
| `WebhookLog` | id (UUID), webhook_id (UUID FK), evento (String 100), payload (JSONB), response_status (Integer nullable), response_time_ms (Integer nullable), tentativa (Integer default 1), erro (Text nullable), created_at (DateTime) | → WebhookConfig |
| `ImportJob` | id (UUID), tenant_id (UUID FK), usuario_id (UUID FK), tipo_entidade (String 50), nome_arquivo (String 255), s3_key (String 512), status (Enum: pendente/processando/concluido/erro), total_linhas (Integer), linhas_sucesso (Integer), linhas_erro (Integer), erros (JSONB), created_at (DateTime), completed_at (DateTime nullable) | → Tenant, → Usuario |
| `ExportJob` | id (UUID), tenant_id (UUID FK), usuario_id (UUID FK), tipo_entidade (String 50), filtros (JSONB), formato (Enum: csv/xlsx), s3_key (String 512), status (Enum: pendente/processando/concluido), total_linhas (Integer nullable), created_at (DateTime), completed_at (DateTime nullable) | → Tenant, → Usuario |
| `WebhookEvento` | id (UUID), nome (String 100), descricao (Text), schema_payload (JSONB), is_system (Boolean) | → WebhookLog[] |

## Integrações Necessárias

- **Redis:** Cache de rate limiting e invalidação imediata de API keys revogadas. Chaves: `rate_limit:{api_key}:{timestamp}`.

- **S3 / MinIO:** Armazenamento de arquivos de importação (upload) e exportação (download). URLs assinadas com validade de 24 horas.

- **Celery / ARQ (async job queue):** Processamento assíncrono de importações grandes e exportações pesadas. Workers dedicados para jobs de import/export.

- **Notificações e Alertas:** Notificação ao usuário quando import/export job é concluído ou quando webhook é desativado por falhas.

- **Sentry:** Monitoramento de erros em webhooks e jobs de importação. Alertas de falha em massa.

- **Todos os módulos de negócio:** Cada módulo expõe endpoints de API, eventos de webhook e templates de import/export para suas entidades.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Criação de API key
1. Owner acessa "Configurações" → "Integrações" → "API Keys".
2. Clica em "Nova API Key".
3. Define nome descritivo (ex: "ERP Contábil"), seleciona escopos (ex: `financeiro:leitura`, `estoque:leitura`).
4. Define data de expiração (opcional). Padrão: sem expiração.
5. Sistema gera API key (prefixo `ask_live_` ou `ask_test_` para sandbox), exibe uma única vez para cópia. Armazena apenas hash.
6. API key fica listada com status, último uso e opção de revogar.
7. Owner copia key e configura no sistema integrado.

### Fluxo 2: Configuração de webhook
1. Owner acessa "Configurações" → "Integrações" → "Webhooks".
2. Clica em "Novo Webhook".
3. Define URL de destino (HTTPS obrigatório) e seleciona eventos (ex: `estoque.movimentacao.criada`, `financeiro.despesa.paga`).
4. Sistema gera secret para assinatura HMAC e exibe uma única vez.
5. Owner testa webhook com evento de teste. Sistema envia payload de exemplo.
6. Sistema exibe resultado (status HTTP, tempo de resposta, headers).
7. Webhook ativado. Eventos futuros serão enviados para URL.

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
7. Notificação push avisa quando exportação está pronta.

### Fluxo 5: Consumo de API por sistema terceiro
1. Desenvolvedor consulta documentação OpenAPI em `/api/docs`.
2. Obtém token OAuth2 via client credentials flow (POST `/oauth/token`).
3. Faz requisições para endpoints com header `Authorization: Bearer {token}`.
4. Sistema valida token, escopos e rate limiting.
5. Resposta é retornada em JSON padronizado.
6. Ao receber 429 (Too Many Requests), sistema aguarda e retry com backoff.

## Casos Extremos e Exceções

- **Webhook com URL interna (SSRF):** Sistema valida URL contra blocklist de IPs privados (10.x, 172.16.x, 192.168.x, localhost). Bloqueia com erro descritivo: "URLs internas não são permitidas por segurança."

- **Importação com encoding incorreto:** Sistema tenta detectar encoding automaticamente (UTF-8, ISO-8859-1, Windows-1252). Se falhar, solicita seleção manual. Preview exibe dados decodificados para confirmação.

- **Planilha com fórmulas em vez de valores:** Parser ignora fórmulas e lê valores calculados. Se célula tiver erro (#REF!, #N/A), linha é reportada como erro.

- **API key com escopo insuficiente:** Retorna HTTP 403 com corpo descritivo indicando escopo necessário vs. escopo da key. Exemplo: "Escopo 'financeiro:lancamento:escrita' necessário. Sua key tem apenas 'financeiro:lancamento:leitura'."

- **Export de dataset muito grande (> 1M linhas):** Job assíncrono obrigatório. Arquivo gerado em partes e compactado (.zip). Limite hard de 5M linhas. Notificação de limite atingido.

- **Webhook recebe payload duplicado (retry após timeout):** Payload inclui `idempotency_key` (UUID). Sistema receptor deve usar para deduplicação. Documentação orienta implementação.

- **Importação com referência a entidade inexistente:** Linha reportada como erro com mensagem "Talhão 'ABC' não encontrado na fazenda X". Importação continua para demais linhas.

- **OAuth client com redirect URI inválido:** Validação estrita de redirect URIs cadastrados. Tentativa de redirecionamento para URI não cadastrado é bloqueada (prevenção de ataque).

- **Rate limit excedido:** Retorna HTTP 429 com header `Retry-After: 60` (segundos). Mensagem: "Limite de requisições atingido. Aguarde X segundos."

- **Arquivo de importação corrompido:** Validação de integridade no upload. Rejeita com mensagem: "Arquivo corrompido. Faça upload novamente."

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
- [ ] Headers de resposta padronizados (X-RateLimit-Remaining, X-RateLimit-Reset).

## Sugestões de Melhoria Futura

1. **Marketplace de integrações:** Catálogo de integrações pré-configuradas com ERPs populares (TOTVS, SAP Business One, Conta Azul), sistemas contábeis e marketplaces agrícolas.

2. **GraphQL para consultas complexas:** Alternativa ao REST para integrações que precisam de queries flexíveis com múltiplos joins. Reduz overfetching e underfetching.

3. **Integração nativa com Google Sheets:** Planilha do Google como fonte de dados bidirecional, atualizando automaticamente. Útil para produtores que já usam Sheets.

4. **SDK em Python e JavaScript:** Bibliotecas cliente oficiais para acelerar desenvolvimento de integrações. Exemplo: `pip install agrosaas-sdk`.

5. **Zapier / Make (Integromat):** Conector oficial para automações no-code. Permite integrar com 5000+ apps sem programação.

6. **Streaming de eventos (SSE/WebSocket):** Alternativa a webhooks para integrações em tempo real sem overhead de HTTP callbacks.

7. **Sandbox de desenvolvimento:** Ambiente isolado com dados fictícios para desenvolvedores testarem integrações sem afetar produção.

8. **Dashboard de uso de API:** Métricas de requisições por endpoint, erros, latência. Útil para desenvolvedores e backoffice.

9. **Versionamento de API:** Suporte a múltiplas versões da API simultâneas (v1, v2). Depreciação gradual com aviso de 6 meses.

10. **Integração com bancos brasileiros:** API de bancos (Open Banking) para conciliação automática e extrato bancário.
