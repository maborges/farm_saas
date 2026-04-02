# Integração ERP Sankhya - Documentação Técnica

**Versão:** 1.0.0
**Data:** 2026-03-31
**Status:** Implementado

---

## 📋 Visão Geral

Módulo de integração bidirecional com o ERP Sankhya via Web Services BPM.

### Funcionalidades

- ✅ Sincronização de cadastros (Pessoas, Produtos)
- ✅ Exportação/Importação de Notas Fiscais
- ✅ Integração financeira (Contas a Pagar/Receber)
- ✅ Sincronização de tabelas (CFOP, NCM)
- ✅ Logs completos de sincronização
- ✅ Retry automático em caso de falha

---

## 🏗️ Arquitetura

```
services/api/integracoes/sankhya/
├── models/
│   └── __init__.py          # Modelos SQLAlchemy
├── schemas/
│   └── __init__.py          # Schemas Pydantic
├── services/
│   ├── __init__.py
│   └── sync_service.py      # Services de sincronização
├── routers/
│   └── __init__.py          # Endpoints API
└── README.md                # Esta documentação
```

---

## 🔧 Configuração

### 1. Configurar Integração

```bash
POST /api/v1/integracoes/sankhya/config
```

**Request:**
```json
{
  "ws_url": "https://seu-servidor/bpm/ws",
  "username": "usuario_sankhya",
  "password": "senha_sankhya",
  "sync_interval": 900
}
```

**Response:**
```json
{
  "id": 1,
  "tenant_id": "tenant-abc",
  "ws_url": "https://seu-servidor/bpm/ws",
  "username": "usuario_sankhya",
  "ativo": true,
  "teste_status": null,
  "ultimo_sync": null,
  "sync_interval": 900,
  "created_at": "2026-03-31T12:00:00"
}
```

### 2. Testar Conexão

```bash
POST /api/v1/integracoes/sankhya/config/testar-conexao
```

**Response:**
```json
{
  "sucesso": true,
  "mensagem": "Conexão estabelecida"
}
```

---

## 📡 Endpoints de API

### Configuração

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/config` | Configurar integração |
| GET | `/config` | Obter configuração |
| POST | `/config/testar-conexao` | Testar conexão |
| GET | `/status` | Status da integração |

### Sincronização

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/sync/pessoas` | Sincronizar pessoas |
| POST | `/sync/produtos` | Sincronizar produtos |
| POST | `/sync/completo` | Sincronização completa |

### Logs

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/logs` | Listar logs de sincronização |

### Dados Sincronizados

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/pessoas` | Listar pessoas sincronizadas |
| GET | `/produtos` | Listar produtos sincronizados |

---

## 🗄️ Modelos de Banco

### sankhya_config
- Configuração da integração por tenant

### sankhya_sync_logs
- Log de todas as sincronizações
- Status, quantidade de registros, tempo de execução

### sankhya_pessoas
- Pessoas físicas e jurídicas sincronizadas
- Upsert baseado em `sankhya_id`

### sankhya_produtos
- Produtos sincronizados
- Inclui NCM, CFOP, preços

### sankhya_nfe
- Notas fiscais exportadas/importadas
- Chave de acesso, valores, status

### sankhya_lancamentos_financeiros
- Contas a pagar/receber
- Rateios por centro de custo

### sankhya_tabelas
- Tabelas auxiliares (CFOP, NCM, CST, etc.)

---

## 🔄 Fluxo de Sincronização

### 1. Sincronização de Pessoas

```python
# 1. Chamar endpoint
POST /api/v1/integracoes/sankhya/sync/pessoas

# 2. Sistema cria log de sincronização
SankhyaSyncLog(status="processando")

# 3. Busca pessoas do Sankhya
WS: PessoaFisica.findAll()
WS: PessoaJuridica.findAll()

# 4. Para cada pessoa, faz upsert
SankhyaPessoa (upsert by sankhya_id)

# 5. Finaliza log
SankhyaSyncLog(status="sucesso", registros_processados=N)
```

### 2. Sincronização de Produtos

```python
# 1. Chamar endpoint
POST /api/v1/integracoes/sankhya/sync/produtos

# 2. Busca produtos do Sankhya
WS: Produto.findAll()

# 3. Para cada produto, faz upsert
SankhyaProduto (upsert by sankhya_id)

# 4. Finaliza log
```

---

## 🛠️ Web Services Sankhya

### Endpoints WS

```
Base URL: https://<servidor>/bpm/ws

Serviços disponíveis:
- PessoaFisica.save
- PessoaFisica.findAll
- PessoaFisica.findByKey
- PessoaJuridica.save
- PessoaJuridica.findAll
- PessoaJuridica.findByKey
- Produto.save
- Produto.findAll
- NFe.save
- NFe.findByKey
- Lancamento.save
```

### Autenticação

```python
# Basic Auth
credentials = username:password
encoded = base64(credentials)
Authorization: Basic <encoded>
```

### Exemplo de Chamada SOAP

```python
import httpx
import base64

url = "https://servidor/bpm/ws"
username = "usuario"
password = "senha"

credentials = f"{username}:{password}"
encoded = base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": f"Basic {encoded}",
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": '""'
}

soap_envelope = """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:bpm="http://www.sankhya.com.br/bpm">
    <soapenv:Header/>
    <soapenv:Body>
        <bpm:findAll>
            <PessoaFisica>
                <CODPARC>123</CODPARC>
            </PessoaFisica>
        </bpm:findAll>
    </soapenv:Body>
</soapenv:Envelope>"""

response = httpx.post(url, headers=headers, content=soap_envelope)
```

---

## ⚙️ Configurações

### Variáveis de Ambiente

```bash
# settings.py
SANKHYA_WS_URL="https://<servidor>/bpm/ws"
SANKHYA_USERNAME="usuario"
SANKHYA_PASSWORD="senha"
SANKHYA_SYNC_INTERVAL=900  # 15 minutos
```

### Sincronização Automática

Para agendar sincronizações automáticas, usar Celery Beat:

```python
# celery_beat.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'sankhya-sync-pessoas': {
        'task': 'tasks.sankhya_sync_pessoas',
        'schedule': crontab(minute='*/15'),  # Cada 15 minutos
    },
    'sankhya-sync-produtos': {
        'task': 'tasks.sankhya_sync_produtos',
        'schedule': crontab(minute='*/30'),  # Cada 30 minutos
    },
}
```

---

## 🔍 Tratamento de Erros

### Retry Automático

```python
MAX_RETRIES = 3

async def executar_ws_com_retry(service, method, params):
    for tentativa in range(MAX_RETRIES):
        try:
            return await executar_ws(service, method, params)
        except Exception as e:
            if tentativa == MAX_RETRIES - 1:
                raise
            await asyncio.sleep(2 ** tentativa)  # Backoff exponencial
```

### Logs de Erro

Todos os erros são registrados no `sankhya_sync_logs`:
- `status`: "erro"
- `erro_mensagem`: Descrição do erro
- `registros_erro`: Quantidade de registros com erro

---

## 📊 Monitoramento

### Status da Integração

```bash
GET /api/v1/integracoes/sankhya/status
```

**Response:**
```json
{
  "configurado": true,
  "ativo": true,
  "ultimo_sync": "2026-03-31T12:00:00",
  "proximo_sync": "2026-03-31T12:15:00",
  "status_conexao": "sucesso"
}
```

### Logs de Sincronização

```bash
GET /api/v1/integracoes/sankhya/logs?tipo=pessoas&status=sucesso&limit=50
```

---

## 🧪 Testes

### Testar Conexão

```bash
curl -X POST "http://localhost:8000/api/v1/integracoes/sankhya/config/testar-conexao" \
  -H "Authorization: Bearer TOKEN"
```

### Sincronizar Pessoas

```bash
curl -X POST "http://localhost:8000/api/v1/integracoes/sankhya/sync/pessoas" \
  -H "Authorization: Bearer TOKEN"
```

### Listar Logs

```bash
curl -X GET "http://localhost:8000/api/v1/integracoes/sankhya/logs" \
  -H "Authorization: Bearer TOKEN"
```

---

## 📝 Próximos Passos

### Fase 1 (Implementado)
- [x] Configuração da integração
- [x] Sincronização de pessoas
- [x] Sincronização de produtos
- [x] Logs de sincronização

### Fase 2 (Planejado)
- [ ] Exportação de NFe para Sankhya
- [ ] Importação de NFe do Sankhya
- [ ] Integração financeira (Contas a Pagar/Receber)
- [ ] Sincronização de tabelas (CFOP, NCM)

### Fase 3 (Futuro)
- [ ] Sincronização bidirecional automática
- [ ] Dashboard de monitoramento
- [ ] Alertas de falha de sincronização

---

## 🔗 Links Úteis

- [Documentação Sankhya BPM](https://docs.sankhya.com.br/bpm/)
- [Web Services Sankhya](https://docs.sankhya.com.br/ws/)
- [Swagger API](http://localhost:8000/docs)

---

**Implementado por:** AgroSaaS Team
**Data:** 2026-03-31
**Versão:** 1.0.0
