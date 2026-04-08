# Validação de Limites — Guia de Uso

## Visão Geral

O AgroSaaS implementa **validação automática de limites** por plano de assinatura. Quando um tenant atinge o limite contratado, novas criações são bloqueadas até que faça upgrade.

---

## Como Funciona

### 1. Decorator `require_limit`

Adicione o decorator `require_limit` ao endpoint que deseja proteger:

```python
from core.dependencies import require_limit

@router.post(
    "/fazendas",
    response_model=FazendaResponse,
    dependencies=[Depends(require_limit("max_fazendas"))],  # ← Aqui!
)
async def criar_fazenda(...):
    ...
```

### 2. Tipos de Limite Suportados

| Tipo | Descrição | Quando Usar |
|------|-----------|-------------|
| `max_fazendas` | Número máximo de fazendas ativas | Criar fazenda |
| `max_usuarios` | Usuários simultâneos ativos | Criar usuário, enviar convite |
| `max_categorias_plano` | Categorias customizáveis no plano de contas | Criar categoria contábil |
| `storage_limite_mb` | Armazenamento em MB | Upload de arquivos, imagens |

---

## Exemplos de Uso

### Exemplo 1: Limite de Fazendas

```python
# services/api/core/routers/fazendas.py
from fastapi import Depends
from core.dependencies import require_limit

@router.post(
    "/",
    response_model=FazendaResponse,
    dependencies=[Depends(require_limit("max_fazendas"))],
)
async def criar_fazenda(dados: FazendaCreate, ...):
    """Cria fazenda — bloqueado se atingir limite."""
    ...
```

**Comportamento:**
- Tenant com 4/5 fazendas: ✅ Permite criar (retorna 201)
- Tenant com 5/5 fazendas: ❌ Bloqueia (retorna 402)
- Tenant com max_fazendas=-1: ✅ Sempre permite (ilimitado)

---

### Exemplo 2: Limite de Usuários

```python
# services/api/core/routers/team.py
from fastapi import Depends
from core.dependencies import require_limit

@router.post(
    "/convites",
    response_model=ConviteResponse,
    dependencies=[Depends(require_limit("max_usuarios"))],
)
async def criar_convite(dados: ConviteCreate, ...):
    """Envia convite — bloqueado se atingir limite."""
    ...
```

---

### Exemplo 3: Limite de Storage

```python
# services/api/operacional/routers/estoque.py
from fastapi import Depends, UploadFile
from core.dependencies import require_limit

@router.post(
    "/upload",
    dependencies=[Depends(require_limit("storage_limite_mb"))],
)
async def upload_arquivo(file: UploadFile, ...):
    """Upload de arquivo — bloqueado se storage cheio."""
    ...
```

---

## Resposta de Erro (402 Payment Required)

Quando o limite é atingido, a API retorna:

```json
HTTP 402 Payment Required
{
  "detail": "Limite de 5 fazendas atingido. Você tem 5 fazenda(s) ativas. Faça upgrade do plano para adicionar mais."
}
```

### Headers Informativos

A resposta inclui headers para o frontend:

```
X-Limit-Type: max_fazendas
X-Limit-Max: 5
X-Limit-Current: 5
```

---

## Endpoint de Status dos Limites

O frontend pode consultar os limites a qualquer momento:

### `GET /api/v1/billing/limits`

**Retorno:**
```json
{
  "max_fazendas": {
    "atual": 3,
    "limite": 5,
    "porcentagem": 60.0,
    "atingido": false
  },
  "max_usuarios": {
    "atual": 4,
    "limite": 5,
    "porcentagem": 80.0,
    "atingido": false
  },
  "storage": {
    "atual": 2048,
    "limite": 10240,
    "porcentagem": 20.0,
    "atingido": false
  }
}
```

---

## Verificação Suave (Soft Check)

Para mostrar warnings na UI **sem bloquear**, use `check_limit_soft`:

```python
from core.dependencies import check_limit_soft

@router.get("/dashboard")
async def dashboard(
    status_fazendas: dict = Depends(check_limit_soft("max_fazendas")),
):
    """Retorna dashboard com status dos limites."""
    return {
        "dashboard_data": {...},
        "warning_limite": status_fazendas["atingido"],
        "porcentagem_uso": status_fazendas["porcentagem"],
    }
```

---

## Configuração dos Limites por Plano

Os limites são definidos em `PlanoAssinatura`:

```python
# Exemplo de planos
PlanoAssinatura(
    nome="Produtor",
    max_fazendas=1,
    limite_usuarios_maximo=5,
    max_categorias_plano=10,
)

PlanoAssinatura(
    nome="Enterprise",
    max_fazendas=-1,  # -1 = ilimitado
    limite_usuarios_maximo=None,  # None = ilimitado
    max_categorias_plano=-1,
)
```

---

## Testes

Os testes estão em: `services/api/tests/core/test_limites.py`

### Executar testes:
```bash
cd services/api
pytest tests/core/test_limites.py -v
```

### Testes cobrem:
- ✅ Criar recurso abaixo do limite (deve permitir)
- ✅ Criar recurso no limite (deve bloquear com 402)
- ✅ Plano ilimitado (sempre permite)
- ✅ Headers informativos no erro
- ✅ Endpoint `/billing/limits` retorna status correto

---

## Boas Práticas

### 1. Sempre use `require_limit` em criações

```python
# ✅ CORRETO
@router.post("/", dependencies=[Depends(require_limit("max_fazendas"))])
async def criar(...): ...

# ❌ ERRADO — validação manual no código
@router.post("/")
async def criar(...):
    if count >= limite:
        raise HTTPException(402, "Limite atingido")
```

### 2. Use verificação suave para UI

```python
# ✅ CORRETO — UI mostra warning sem bloquear
status = await check_limit_soft("max_fazendas")
if status["porcentagem"] > 80:
    mostrar_warning("Quase atingindo limite!")

# ❌ ERRADO — bloquear na UI
if status["atingido"]:
    bloquear_botao()  # Deixe a API bloquear
```

### 3. Trate erro 402 no frontend

```typescript
// apps/web/src/lib/api/fazendas.ts
try {
  await api.post('/fazendas', dados)
} catch (error) {
  if (error.response?.status === 402) {
    // Mostrar modal de upgrade
    mostrarModalUpgrade({
      limite: error.response.headers['x-limit-max'],
      atual: error.response.headers['x-limit-current'],
    })
  }
}
```

---

## Troubleshooting

### Problema: Endpoint não está bloqueando

**Causa:** Decorator não foi adicionado ou ordem incorreta.

**Solução:**
```python
# ✅ CORRETO — dependencies na definição do router
@router.post("/", dependencies=[Depends(require_limit("max_fazendas"))])
async def criar(...): ...

# ❌ ERRADO — decorator fora do router
@require_limit("max_fazendas")  # Não funciona assim!
@router.post("/")
async def criar(...): ...
```

---

### Problema: Teste falha com "Sem assinatura ativa"

**Causa:** Fixture não criou assinatura para o tenant.

**Solução:**
```python
@pytest.fixture
def tenant_com_assinatura_ativa(session):
    tenant = Tenant(nome="Teste", documento="000")
    session.add(tenant)
    session.commit()

    plano = PlanoAssinatura(max_fazendas=5)
    session.add(plano)
    session.commit()

    assinatura = AssinaturaTenant(
        tenant_id=tenant.id,
        plano_id=plano.id,
        status="ATIVA",  # ← Importante!
        tipo_assinatura="PRINCIPAL",
    )
    session.add(assinatura)
    session.commit()

    return tenant
```

---

## Próximos Passos

### Melhorias Futuras:
1. [ ] Adicionar limite `max_hectares` (somar área de todas as fazendas)
2. [ ] Adicionar limite `max_animais` (pecuária)
3. [ ] Implementar notificação automática quando atingir 80% do limite
4. [ ] Criar webhook "limit.nearing" para integrações

---

**Documento gerado em:** 2026-04-01  
**Responsável:** Tech Lead  
**Status:** ✅ Implementado
