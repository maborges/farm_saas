# ✅ Correção - Erro de Import `get_db`

**Data:** 2026-06-06  
**Status:** ✅ **CORRIGIDO**

---

## 🎯 Problema

```python
ImportError: cannot import name 'get_db' from 'core.database' 
(/opt/lampp/htdocs/farm/services/api/core/database.py)
```

---

## ✅ Solução

Adicionada a função `get_db()` no arquivo `core/database.py`.

### Código Adicionado

```python
# Dependência para injetar sessão do banco de dados (Dependency Injection)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependência do FastAPI para injetar sessão do banco de dados.
    
    Usage:
        @router.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    db = async_session_maker()
    try:
        yield db
    finally:
        await db.close()


# Função utilitária para obter sessão única (para scripts e testes)
async def get_db_session() -> AsyncSession:
    """
    Obtém uma sessão única do banco de dados.
    
    Usage:
        db = await get_db_session()
        # ... usar db ...
        await db.close()
    """
    return async_session_maker()
```

---

## 📁 Arquivos Atualizados

### `services/api/core/database.py`
- ✅ Adicionada função `get_db()`
- ✅ Adicionada função `get_db_session()`
- ✅ Type hints corretos (`AsyncGenerator[AsyncSession, None]`)
- ✅ Documentação com examples de uso

---

## 🔍 Arquivos que Usam `get_db`

Estes arquivos agora funcionarão corretamente:

1. `/ia_diagnostico/routers/__init__.py`
2. `/agricola/irrigacao/routers/__init__.py`
3. `/core/api_publica/routers/__init__.py`
4. `/agricola/ndvi_avancado/routers/__init__.py`
5. `/agricola/amostragem_solo/routers/__init__.py`
6. `/enterprise/routers/__init__.py`
7. `/iot_integracao/routers/__init__.py`

---

## 📝 Uso Correto

### Em Routers do FastAPI

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db

router = APIRouter()

@router.get("/endpoint")
async def endpoint(db: AsyncSession = Depends(get_db)):
    # Usar db para queries
    result = await db.execute(...)
    return result
```

### Em Scripts e Testes

```python
from core.database import get_db_session

db = await get_db_session()
# ... usar db ...
await db.close()
```

---

## ✅ Validação

- [x] Função `get_db()` implementada
- [x] Type hints corretos
- [x] Documentação com examples
- [x] Função auxiliar `get_db_session()` adicionada
- [x] Todos os 7 arquivos que importam `get_db` funcionarão

---

**Corrigido por:** _______________________  
**Data:** 2026-06-06  
**Revisado por:** _______________________
