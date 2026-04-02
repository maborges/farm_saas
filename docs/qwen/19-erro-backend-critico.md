# 🚨 ERRO CRÍTICO - Backend não Inicia

**Data:** 2026-06-06  
**Status:** ⚠️ **REQUER ATENÇÃO**

---

## 🎯 Erro Atual

```
sqlalchemy.exc.InvalidRequestError: 
Table 'prescricoes_vra' is already defined for this MetaData instance.
Specify 'extend_existing=True' to redefine options and columns on an existing Table object.
```

---

## 🔍 Causa Raiz

O modelo `PrescricaoVRA` está definido **múltiplas vezes** em arquivos diferentes, causando conflito no SQLAlchemy.

---

## ✅ Soluções

### Solução 1: Corrigir Modelos Duplicados (Recomendada)

**Arquivos para verificar:**
```bash
# Procurar por definições duplicadas
grep -r "class PrescricaoVRA" /opt/lampp/htdocs/farm/services/api/
```

**Ação:**
1. Identificar todos os arquivos com `class PrescricaoVRA`
2. Manter apenas UMA definição
3. Remover ou renomear as duplicatas

### Solução 2: Adicionar extend_existing=True

No arquivo do modelo duplicado:

```python
class PrescricaoVRA(Base):
    __tablename__ = "prescricoes_vra"
    __table_args__ = {'extend_existing': True}
    
    # ... resto do código
```

### Solução 3: Iniciar Apenas Módulos Essenciais

Para testes rápidos, comentar imports não essenciais no `main.py`:

```python
# Comentar módulos em desenvolvimento
# from agricola.amostragem_solo.routers import router as router_amostragem_solo
# from agricola.ndvi_avancado.routers import router as router_ndvi_avancado
```

---

## 🔧 Commands de Diagnóstico

### 1. Procurar Modelos Duplicados
```bash
cd /opt/lampp/htdocs/farm/services/api

# Procurar por PrescricaoVRA
grep -r "class PrescricaoVRA" --include="*.py" .

# Procurar por tabelas duplicadas
grep -r "__tablename__" --include="*.py" . | sort | uniq -d
```

### 2. Verificar Logs do Backend
```bash
cd /opt/lampp/htdocs/farm/services/api
source .venv/bin/activate
python main.py 2>&1 | tail -50
```

### 3. Testar Import Individual
```bash
cd /opt/lampp/htdocs/farm/services/api
source .venv/bin/activate
python -c "from core.database import get_db; print('OK')"
```

---

## 📝 Passos para Correção

### Passo 1: Identificar Duplicatas
```bash
cd /opt/lampp/htdocs/farm/services/api
grep -rn "class PrescricaoVRA" --include="*.py" .
```

### Passo 2: Decidir Qual Manter
- Manter no módulo principal (`agricola/amostragem_solo/models/`)
- Remover de outros módulos

### Passo 3: Corrigir Imports
Em vez de importar o modelo, importar o router:
```python
# Em vez de:
from agricola.amostragem_solo.models import PrescricaoVRA

# Usar:
from agricola.amostragem_solo.routers import router
```

### Passo 4: Testar Inicialização
```bash
cd /opt/lampp/htdocs/farm/services/api
source .venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🎯 Estado Atual

### ❌ Problemas
- [ ] Modelo `PrescricaoVRA` duplicado
- [ ] Backend não inicia
- [ ] Login não funciona

### ✅ Correções Pendentes
- [ ] Identificar arquivos duplicados
- [ ] Remover duplicatas
- [ ] Testar inicialização
- [ ] Validar login

---

## 📞 Próximos Passos Imediatos

1. **Rodar comando de diagnóstico:**
   ```bash
   grep -rn "class PrescricaoVRA" /opt/lampp/htdocs/farm/services/api/
   ```

2. **Listar arquivos duplicados**

3. **Decidir qual manter**

4. **Remover duplicatas**

5. **Testar backend**

---

**Prioridade:** 🔴 **CRÍTICA**  
**Impacto:** Sistema não funciona sem backend  
**Tempo Estimado:** 30 minutos

---

**Reportado por:** _______________________  
**Data:** 2026-06-06  
**Atribuído para:** _______________________
