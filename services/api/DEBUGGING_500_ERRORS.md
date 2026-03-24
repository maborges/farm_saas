# Guia para Debugar Erros 500 no Backend

## 📋 O Que É um Erro 500?

Um erro 500 (Internal Server Error) indica que o servidor encontrou uma exceção não tratada durante o processamento da requisição.

## 🔍 Como Identificar a Causa

### 1. Verificar os Logs do Servidor

**Se o servidor foi iniciado manualmente:**
- Veja o terminal onde uvicorn está rodando
- O traceback completo aparecerá lá

**Se o servidor foi iniciado em background:**
```bash
# Ver logs em tempo real
tail -f /tmp/agrosaas-api.log

# Ver últimas 100 linhas
tail -100 /tmp/agrosaas-api.log
```

### 2. Interpretar o Traceback

Exemplo de traceback:
```python
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "uvicorn/protocols/http/httptools_impl.py", line 416
  File "services/api/core/routers/backoffice.py", line 795  ← AQUI!
    "modulos_ativos": tenant.modulos_ativos,
AttributeError: 'NoneType' object has no attribute 'modulos_ativos'
```

**Leia de baixo para cima:**
- Última linha = tipo do erro e mensagem
- Penúltima linha = linha do código que causou o erro
- Demais linhas = stack trace (caminho até o erro)

### 3. Erros Comuns

#### a) AttributeError: 'NoneType'
**Causa:** Tentativa de acessar atributo de objeto None

**Exemplo:**
```python
# ❌ Errado
tenant = await session.get(Tenant, id)  # Pode retornar None
return {"nome": tenant.nome}  # AttributeError se None!

# ✅ Correto
tenant = await session.get(Tenant, id)
if not tenant:
    raise HTTPException(status_code=404, detail="Not found")
return {"nome": tenant.nome}
```

#### b) TypeError: argument must be...
**Causa:** Tipo de dado incorreto

**Exemplo:**
```python
# ❌ Errado
modulos = tenant.modulos_ativos  # Pode ser None
for modulo in modulos:  # TypeError!

# ✅ Correto
modulos = tenant.modulos_ativos or []  # Fallback para lista vazia
for modulo in modulos:
```

#### c) IntegrityError
**Causa:** Violação de constraint do banco de dados

**Exemplo:**
```python
# Duplicate key, foreign key violation, etc.
# Verifique:
# - Unicidade de campos unique
# - Existência de FK antes de inserir
# - Constraints NOT NULL
```

#### d) ImportError / ModuleNotFoundError
**Causa:** Módulo não encontrado ou import circular

**Solução:**
- Verifique se o módulo está instalado
- Mova imports para dentro da função se houver circular import
- Use imports absolutos (`from core.models.x import Y`)

### 4. Adicionar Logging Detalhado

**Envolva código suspeito em try-catch:**

```python
from loguru import logger

@router.get("/endpoint")
async def my_endpoint():
    try:
        # Código que pode falhar
        result = await some_operation()
        logger.info(f"Operação bem sucedida: {result}")
        return result
    except Exception as e:
        logger.error(f"Erro em my_endpoint: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
```

**Benefícios:**
- Log completo do erro
- Mensagem de erro mais clara para o cliente
- Não quebra a aplicação

### 5. Testar Isoladamente

**Crie um script de teste:**

```python
# test_endpoint.py
import asyncio
from core.database import async_session_maker
from core.models.tenant import Tenant

async def test():
    async with async_session_maker() as session:
        tenant = await session.get(Tenant, some_id)
        print(f"Tenant: {tenant}")
        print(f"Modulos: {tenant.modulos_ativos if tenant else 'None'}")

asyncio.run(test())
```

**Executar:**
```bash
cd services/api
source .venv/bin/activate
python test_endpoint.py
```

## 🛠️ Checklist de Debug

Quando encontrar um erro 500:

- [ ] **1. Ver logs do servidor**
  - Terminal do uvicorn OU
  - `tail -100 /tmp/agrosaas-api.log`

- [ ] **2. Identificar linha do erro**
  - Última linha do traceback

- [ ] **3. Analisar o tipo de erro**
  - AttributeError → objeto None
  - TypeError → tipo errado
  - IntegrityError → BD
  - ImportError → módulo faltando

- [ ] **4. Adicionar proteções**
  - Checks de None
  - Fallbacks (or [])
  - Try-catch com logging

- [ ] **5. Testar isoladamente**
  - Script de teste
  - Verificar cada query

- [ ] **6. Reiniciar servidor**
  - `pkill -f uvicorn`
  - `./start_server.sh`

- [ ] **7. Testar novamente**
  - Fazer a mesma requisição
  - Verificar se erro persiste

## 💡 Dicas de Prevenção

### Sempre Validar Nulls
```python
# Antes de usar, verifique:
if tenant:
    nome = tenant.nome
else:
    raise HTTPException(404, "Not found")
```

### Usar Fallbacks
```python
# Para listas que podem ser None:
modulos = tenant.modulos_ativos or []

# Para strings:
nome = tenant.nome or "Sem nome"

# Para números:
valor = tenant.valor or 0
```

### Try-Catch em Operações de BD
```python
try:
    result = await session.execute(stmt)
    items = result.scalars().all()
except Exception as e:
    logger.error(f"DB Error: {e}")
    raise HTTPException(500, "Database error")
```

### Logging Estratégico
```python
# No início da função:
logger.info(f"Endpoint chamado com params: {params}")

# Antes de operações complexas:
logger.debug(f"Executando query: {stmt}")

# Após operações:
logger.info(f"Resultado: {len(items)} items")
```

## 🔗 Exemplo Completo

```python
from loguru import logger
from fastapi import HTTPException

@router.get("/tenants/{id}/details")
async def get_tenant_details(id: UUID, session: AsyncSession = Depends(get_session)):
    try:
        # 1. Buscar tenant
        tenant = await session.get(Tenant, id)
        if not tenant:
            raise HTTPException(404, "Tenant not found")

        logger.info(f"Tenant {id} encontrado: {tenant.nome}")

        # 2. Buscar dados relacionados
        stmt = select(Assinatura).where(Assinatura.tenant_id == id)
        result = await session.execute(stmt)
        assinaturas = result.scalars().all()

        logger.debug(f"Encontradas {len(assinaturas)} assinaturas")

        # 3. Montar resposta com fallbacks
        return {
            "id": tenant.id,
            "nome": tenant.nome,
            "modulos": tenant.modulos_ativos or [],  # Fallback!
            "assinaturas": [a.to_dict() for a in assinaturas]
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Erro inesperado em get_tenant_details: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Internal error: {str(e)}")
```

## 📚 Referências

- [FastAPI Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Python Exception Handling](https://docs.python.org/3/tutorial/errors.html)
- [Loguru Documentation](https://loguru.readthedocs.io/)
- Arquivo: `services/api/test_endpoint.py` (script de teste)
