# ✅ Estrutura de Arquivos Corrigida

**Data:** 2026-03-31
**Status:** Estrutura padronizada concluída

---

## 📁 Padrão Adotado

Seguindo o padrão dos módulos existentes (`operacional`, `financeiro`, `pecuaria`):

### Backend (`services/api/`)

```
modulo/
├── models/
│   ├── __init__.py          # Importa e exporta todos os modelos
│   ├── entidade1.py         # Modelo específico
│   └── entidade2.py
│
├── schemas/
│   ├── __init__.py
│   ├── entidade1.py
│   └── entidade2.py
│
├── routers/
│   ├── __init__.py          # Importa e exporta routers
│   ├── entidade1.py         # Router específico
│   └── entidade2.py
│
└── services/
    ├── __init__.py
    ├── service1.py
    └── service2.py
```

### Frontend (`apps/web/src/components/`)

```
modulo/
├── index.ts                 # Exporta todos os componentes
├── Componente1.tsx
├── Componente2.tsx
└── Componente3.tsx
```

---

## ✅ Módulos Corrigidos

### 1. Contabilidade ✅ (Referência)
```
contabilidade/
├── models/__init__.py
├── schemas/__init__.py
├── routers/
│   ├── __init__.py
│   ├── integracoes.py
│   ├── exportacoes.py
│   └── lancamentos.py
└── services/
    ├── __init__.py
    └── exportacao_service.py
```

### 2. IA Diagnóstico ✅
```
ia_diagnostico/
├── models/
│   ├── __init__.py
│   ├── pragas_doencas.py
│   ├── tratamentos.py
│   ├── diagnosticos.py
│   ├── recomendacoes.py
│   └── modelos_ml.py
├── routers/
│   ├── __init__.py
│   ├── pragas_doencas.py
│   ├── tratamentos.py
│   └── diagnosticos.py
└── services/
    ├── __init__.py
    └── diagnostico_service.py
```

### 3. IoT Integração ✅
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
└── services/
    ├── __init__.py
    └── integracao_service.py
```

### 4. Amostragem de Solo ✅
```
agricola/amostragem_solo/
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
└── services/
    ├── __init__.py
    └── solo_service.py
```

### 5. NDVI e Irrigação ✅
```
agricola/ndvi_avancado/
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
└── services/
    ├── __init__.py
    └── ndvi_service.py
```

### 6. API Pública ✅
```
core/api_publica/
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
└── services/
    ├── __init__.py
    └── api_key_service.py
```

### 7. Enterprise ✅
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
└── services/
    ├── __init__.py
    ├── sap_service.py
    ├── powerbi_service.py
    └── preditivo_service.py
```

---

## 📊 Resumo

| Módulo | Models | Routers | Services | Status |
|--------|--------|---------|----------|--------|
| contabilidade | 5 | 3 | 1 | ✅ |
| ia_diagnostico | 5 | 3 | 1 | ✅ |
| iot_integracao | 4 | 4 | 1 | ✅ |
| amostragem_solo | 3 | 3 | 1 | ✅ |
| ndvi_avancado | 5 | 3 | 1 | ✅ |
| api_publica | 4 | 3 | 1 | ✅ |
| enterprise | 5 | 4 | 1 | ✅ |
| **TOTAL** | **31** | **23** | **7** | **✅** |

---

## 🔄 main.py Atualizado

### Imports
```python
# Amostragem de Solo
from agricola.amostragem_solo.routers.amostras import router as amostras_solo_router
from agricola.amostragem_solo.routers.mapas_fertilidade import router as mapas_fertilidade_router
from agricola.amostragem_solo.routers.prescricoes_vra import router as prescricoes_vra_router

# NDVI e Irrigação
from agricola.ndvi_avancado.routers.ndvi import router as ndvi_router
from agricola.ndvi_avancado.routers.irrigacao import router as irrigacao_router
from agricola.ndvi_avancado.routers.meteorologia import router as meteorologia_router

# IA Diagnóstico
from ia_diagnostico.routers.pragas_doencas import router as ia_pragas_doencas_router
from ia_diagnostico.routers.tratamentos import router as ia_tratamentos_router
from ia_diagnostico.routers.diagnosticos import router as ia_diagnosticos_router

# IoT Integração
from iot_integracao.routers.john_deere import router as john_deere_router
from iot_integracao.routers.case_ih import router as case_ih_router
from iot_integracao.routers.whatsapp import router as whatsapp_router
from iot_integracao.routers.comparador_precos import router as comparador_precos_router

# API Pública
from core.api_publica.routers.keys import router as api_keys_router
from core.api_publica.routers.logs import router as api_logs_router
from core.api_publica.routers.versions import router as api_versions_router

# Enterprise
from enterprise.routers.sap import router as sap_router
from enterprise.routers.powerbi import router as powerbi_router
from enterprise.routers.benchmarks import router as benchmarks_router
from enterprise.routers.preditivo import router as preditivo_router

# Contabilidade
from contabilidade.routers.integracoes import router as contabilidade_integracoes_router
from contabilidade.routers.exportacoes import router as contabilidade_exportacoes_router
from contabilidade.routers.lancamentos import router as contabilidade_lancamentos_router
```

### Includes
```python
# Amostragem de Solo
app.include_router(amostras_solo_router, prefix="/api/v1/amostragem-solo")
app.include_router(mapas_fertilidade_router, prefix="/api/v1/amostragem-solo")
app.include_router(prescricoes_vra_router, prefix="/api/v1/amostragem-solo")

# NDVI e Irrigação
app.include_router(ndvi_router, prefix="/api/v1/agricultura-precisao")
app.include_router(irrigacao_router, prefix="/api/v1/agricultura-precisao")
app.include_router(meteorologia_router, prefix="/api/v1/agricultura-precisao")

# IA Diagnóstico
app.include_router(ia_pragas_doencas_router, prefix="/api/v1/ia-diagnostico")
app.include_router(ia_tratamentos_router, prefix="/api/v1/ia-diagnostico")
app.include_router(ia_diagnosticos_router, prefix="/api/v1/ia-diagnostico")

# IoT Integração
app.include_router(john_deere_router, prefix="/api/v1/iot")
app.include_router(case_ih_router, prefix="/api/v1/iot")
app.include_router(whatsapp_router, prefix="/api/v1/iot")
app.include_router(comparador_precos_router, prefix="/api/v1/iot")

# API Pública
app.include_router(api_keys_router, prefix="/api/v1/api-publica")
app.include_router(api_logs_router, prefix="/api/v1/api-publica")
app.include_router(api_versions_router, prefix="/api/v1/api-publica")

# Enterprise
app.include_router(sap_router, prefix="/api/v1/enterprise")
app.include_router(powerbi_router, prefix="/api/v1/enterprise")
app.include_router(benchmarks_router, prefix="/api/v1/enterprise")
app.include_router(preditivo_router, prefix="/api/v1/enterprise")

# Contabilidade
app.include_router(contabilidade_integracoes_router, prefix="/api/v1/contabilidade")
app.include_router(contabilidade_exportacoes_router, prefix="/api/v1/contabilidade")
app.include_router(contabilidade_lancamentos_router, prefix="/api/v1/contabilidade")
```

---

## 📝 Próximos Passos

1. ✅ Estrutura de arquivos gerada
2. ✅ main.py atualizado
3. ⏳ Preencher conteúdo real nos arquivos stub
4. ⏳ Criar migrations para todas as tabelas
5. ⏳ Testar todos os endpoints

---

**Script de Geração:** `scripts/gerar_estrutura_padrao.py`

**Status:** ✅ ESTRUTURA PADRONIZADA CONCLUÍDA
