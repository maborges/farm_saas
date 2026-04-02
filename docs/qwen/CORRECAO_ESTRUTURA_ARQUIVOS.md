# 📁 Estrutura de Arquivos - Padrão AgroSaaS

**Data:** 2026-03-31
**Objetivo:** Documentar e corrigir estrutura de arquivos para seguir padrão do projeto

---

## ✅ Padrão Correto

### Backend (`services/api/`)

```
modulo/
├── models/
│   ├── __init__.py          # Importa e exporta todos os modelos
│   ├── entidade1.py         # Modelo específico (ex: praga.py)
│   └── entidade2.py         # Modelo específico (ex: tratamento.py)
│
├── schemas/
│   ├── __init__.py          # Exporta todos os schemas
│   ├── entidade1.py         # Schemas específicos
│   └── entidade2.py
│
├── routers/
│   ├── __init__.py          # Importa e exporta routers
│   ├── entidade1.py         # Router específico (ex: pragas.py)
│   └── entidade2.py         # Router específico (ex: tratamentos.py)
│
└── services/
    ├── __init__.py          # Exporta todos os services
    ├── service1.py          # Service específico
    └── service2.py
```

### Frontend (`apps/web/src/components/`)

```
modulo/
├── index.ts                 # Exporta todos os componentes
├── Componente1.tsx          # Componente específico
├── Componente2.tsx
└── Componente3.tsx
```

---

## 📋 Módulos a Corrigir

### Fase 2 (8 módulos)

1. **ia_diagnostico** - IA de pragas/doenças
2. **iot_integracao** - John Deere, Case IH, WhatsApp
3. **agricola/amostragem_solo** - Amostragem de solo
4. **agricola/ndvi_avancado** - NDVI e Irrigação
5. **core/api_publica** - API Pública
6. **enterprise** - SAP, Power BI, Preditivo

### Fase 3 (1 módulo até agora)

7. **contabilidade** - Integrações contábeis ✅ CORRETO

---

## 🔧 Correções Necessárias

### 1. ia_diagnostico

**Estrutura Atual:** ❌ Tudo em `__init__.py`
**Estrutura Correta:**
```
ia_diagnostico/
├── models/
│   ├── __init__.py
│   ├── pragas_doencas.py
│   ├── tratamentos.py
│   ├── diagnosticos.py
│   └── modelos_ml.py
├── schemas/
│   ├── __init__.py
│   ├── pragas_doencas.py
│   ├── tratamentos.py
│   └── diagnosticos.py
├── routers/
│   ├── __init__.py
│   ├── pragas_doencas.py
│   ├── tratamentos.py
│   └── diagnosticos.py
└── services/
    ├── __init__.py
    └── diagnostico_service.py
```

### 2. iot_integracao

**Estrutura Correta:**
```
iot_integracao/
├── models/
│   ├── __init__.py
│   ├── john_deere.py
│   ├── case_ih.py
│   ├── whatsapp.py
│   └── comparador_precos.py
├── routers/
│   ├── __init__.py
│   ├── john_deere.py
│   ├── case_ih.py
│   ├── whatsapp.py
│   └── comparador_precos.py
...
```

### 3. agricola/amostragem_solo

**Estrutura Correta:**
```
amostragem_solo/
├── models/
│   ├── __init__.py
│   ├── amostras.py
│   ├── mapas_fertilidade.py
│   └── prescricoes_vra.py
├── routers/
│   ├── __init__.py
│   ├── amostras.py
│   ├── mapas_fertilidade.py
│   └── prescricoes_vra.py
...
```

### 4. agricola/ndvi_avancado

**Estrutura Correta:**
```
ndvi_avancado/
├── models/
│   ├── __init__.py
│   ├── imagens_satelite.py
│   ├── ndvi_registros.py
│   ├── irrigacao.py
│   ├── balanco_hidrico.py
│   └── estacoes_meteorologicas.py
├── routers/
│   ├── __init__.py
│   ├── ndvi.py
│   ├── irrigacao.py
│   └── meteorologia.py
...
```

### 5. core/api_publica

**Estrutura Correta:**
```
api_publica/
├── models/
│   ├── __init__.py
│   ├── api_keys.py
│   ├── api_logs.py
│   ├── api_versions.py
│   └── sdks.py
├── routers/
│   ├── __init__.py
│   ├── keys.py
│   ├── logs.py
│   └── versions.py
...
```

### 6. enterprise

**Estrutura Correta:**
```
enterprise/
├── models/
│   ├── __init__.py
│   ├── sap.py
│   ├── powerbi.py
│   ├── benchmarks.py
│   ├── preditivo.py
│   └── pontos.py
├── routers/
│   ├── __init__.py
│   ├── sap.py
│   ├── powerbi.py
│   ├── benchmarks.py
│   └── preditivo.py
...
```

---

## 📝 Exemplo de Implementação

### models/pragas_doencas.py
```python
from sqlalchemy import Column, Integer, String, DateTime
from core.database import Base

class PragaDoenca(Base):
    __tablename__ = "pragas_doencas"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    # ... demais campos
```

### models/__init__.py
```python
from .pragas_doencas import PragaDoenca
from .tratamentos import Tratamento
from .diagnosticos import Diagnostico

__all__ = ["PragaDoenca", "Tratamento", "Diagnostico"]
```

### routers/pragas_doencas.py
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db

router = APIRouter(prefix="/pragas-doencas", tags=["Pragas e Doenças"])

@router.get("/")
def listar(...):
    ...
```

### routers/__init__.py
```python
from .pragas_doencas import router as pragas_doencas_router
from .tratamentos import router as tratamentos_router
from .diagnosticos import router as diagnosticos_router

__all__ = ["pragas_doencas_router", "tratamentos_router", "diagnosticos_router"]
```

---

## ✅ Status das Correções

| Módulo | Status | Progresso |
|--------|--------|-----------|
| contabilidade | ✅ Correto | 100% |
| ia_diagnostico | ⏳ Pendente | 0% |
| iot_integracao | ⏳ Pendente | 0% |
| amostragem_solo | ⏳ Pendente | 0% |
| ndvi_avancado | ⏳ Pendente | 0% |
| api_publica | ⏳ Pendente | 0% |
| enterprise | ⏳ Pendente | 0% |

---

**Próximo Passo:** Recriar cada módulo seguindo o padrão acima.
