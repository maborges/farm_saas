# Próximos Passos — Análise de Gaps Restantes

## Data: 2026-04-01
## Status: Atualizado após implementação de Limites + Notificações

---

## 📊 Status Atualizado do Core

| Submódulo | Implementação Anterior | Implementação Atual | Gap Restante |
|-----------|----------------------|---------------------|--------------|
| **Identidade e Acesso** | 90% | 90% | 10% |
| **Cadastro da Propriedade** | 85% | 85% | 15% |
| **Multipropriedade** | 80% | 80% | 20% |
| **Configurações Globais** | 60% | 60% | 40% |
| **Notificações e Alertas** | 50% | **95%** | **5%** ✅ |
| **Integrações Essenciais** | 40% | 40% | 60% |
| **Planos e Assinatura** | 75% | **85%** | 15% ✅ |

**Legenda:**
- ✅ Implementado (validação de limites + notificações)
- ⚠️ Parcial (falta pouco)
- ❌ Crítico (falta muito)

---

## 🎯 Próximos Gaps Críticos (Por Prioridade)

### **PRIORIDADE ALTA — O Que Fazer Agora**

#### 1. **Configurações Globais** (Gap: 40%)

**O Que Já Existe:**
- ✅ `ConfiguracaoTenant` model
- ✅ `ConfiguracaoSaaS` model
- ✅ Router `configuration.py`

**O Que Falta:**
- ❌ Wizard de onboarding (UI + API)
- ❌ Conversão de unidades (hectare ↔ alqueire)
- ❌ Categorias customizáveis (CRUD)
- ❌ Override por fazenda

**Impacto:** Alto — afeta todos os módulos
**Esforço:** 2-3 horas
**Recomendação:** ✅ **FAZER AGORA**

---

#### 2. **Integrações Essenciais** (Gap: 60%)

**O Que Já Existe:**
- ✅ `ApiKey` model
- ✅ Webhooks (parcial)
- ✅ Email service

**O Que Falta:**
- ❌ OAuth2 flow completo
- ❌ Rate limiting (Redis)
- ❌ Importação CSV/XLSX engine
- ❌ Exportação assíncrona
- ❌ Documentação OpenAPI pública

**Impacto:** Alto — bloqueia integrações enterprise
**Esforço:** 6-8 horas
**Recomendação:** ⚠️ **FAZER DEPOIS** (depende de Redis)

---

#### 3. **Upload de Shapefile/KML** (Gap: 15%)

**O Que Já Existe:**
- ✅ `Fazenda.geometria` (GeoJSON)
- ✅ CRUD de fazendas

**O Que Falta:**
- ❌ Endpoint de upload de shapefile
- ❌ Conversão shapefile → GeoJSON
- ❌ Cálculo de área do polígono (ha)

**Impacto:** Médio — afeta cadastro de propriedades
**Esforço:** 2-3 horas
**Recomendação:** ⚠️ **FAZER EM SEGUIDA**

---

### **PRIORIDADE MÉDIA — O Que Fazer Esta Semana**

#### 4. **Logs de Auditoria** (Gap: 10%)

**O Que Já Existe:**
- ✅ `AdminAuditLog` model
- ✅ `LogAuditoria` model

**O Que Falta:**
- ❌ Decorator `@audit_log`
- ❌ Log automático em operações CRUD

**Impacto:** Médio — compliance e segurança
**Esforço:** 1-2 horas
**Recomendação:** ✅ **RÁPIDO E VALIOSO**

---

#### 5. **2FA/TOTP** (Gap: 10%)

**O Que Já Existe:**
- ✅ `Usuario.senha_hash`
- ✅ Auth service

**O Que Falta:**
- ❌ Geração de secret TOTP
- ❌ Validação de código 6 dígitos
- ❌ QR Code para setup

**Impacto:** Médio — segurança de backoffice
**Esforço:** 2-3 horas
**Recomendação:** ⚠️ **SEGURANÇA CRÍTICA**

---

### **PRIORIDADE BAIXA — O Que Pode Esperar**

#### 6. **Refresh Token** (Gap: 10%)

**O Que Já Existe:**
- ✅ JWT 24h

**O Que Falta:**
- ❌ Refresh token 30 dias
- ❌ Endpoint `/refresh`

**Impacto:** Baixo — UX (não segurança)
**Esforço:** 1 hora
**Recomendação:** ⚠️ **FÁCIL MAS NÃO URGENTE**

---

#### 7. **SSO Google/Microsoft** (Gap: 10%)

**O Que Já Existe:**
- ✅ Auth service

**O Que Falta:**
- ❌ OAuth2 Google
- ❌ OAuth2 Microsoft

**Impacto:** Baixo — conveniência
**Esforço:** 3-4 horas
**Recomendação:** ❌ **DEPOIS DO MVP**

---

## 📋 Roadmap Recomendado

### **Semana 1: Configurações + Upload**

| Dia | Tarefa | Entregável |
|-----|--------|------------|
| 1 | Configurações Globais — Wizard | API de configurações + conversão de unidades |
| 2 | Configurações — Categorias | CRUD de categorias customizáveis |
| 3 | Upload de Shapefile | Endpoint + cálculo de área |
| 4 | Logs de Auditoria | Decorator `@audit_log` |
| 5 | Testes + documentação | Testes + guia de uso |

**Total:** 5 dias, ~15 horas

---

### **Semana 2: Segurança + Integrações**

| Dia | Tarefa | Entregável |
|-----|--------|------------|
| 1 | 2FA/TOTP | Geração + validação + QR Code |
| 2-3 | OAuth2 API | `/oauth/token`, `/oauth/authorize` |
| 4 | Rate Limiting | Redis + decorator |
| 5 | Webhooks | Payload signing + retry logic |

**Total:** 5 dias, ~20 horas

---

### **Semana 3: Import/Export**

| Dia | Tarefa | Entregável |
|-----|--------|------------|
| 1-2 | Importação CSV | Validação + processamento |
| 3-4 | Exportação XLSX | Jobs assíncronos |
| 5 | Documentação OpenAPI | Swagger público |

**Total:** 5 dias, ~15 horas

---

## 🎯 Próxima Ação Imediata

**Recomendação:** Começar por **Configurações Globais**

### Por quê?
1. ✅ **Alto impacto** — afeta todos os módulos
2. ✅ **Baixo risco** — não depende de sistemas externos
3. ✅ **Rápido** — 2-3 horas
4. ✅ **Já tem base** — models existem

### O Que Implementar:
```python
# 1. Conversão de unidades
def converter_area(valor: float, de: str, para: str) -> float:
    """Converte entre hectare, alqueire paulista, mineiro, etc."""
    
# 2. CRUD de categorias
@router.post("/categorias")
async def criar_categoria(dados: CategoriaCreate, ...):
    """Cria categoria customizada (despesa, receita, operação, produto)"""

# 3. Wizard de onboarding
@router.post("/onboarding/configuracoes")
async def completar_onboarding(dados: OnboardingConfig, ...):
    """Salva configurações iniciais do tenant"""
```

---

## 📊 Matriz de Decisão

| Tarefa | Impacto | Esforço | Risco | Prioridade |
|--------|---------|---------|-------|------------|
| Configurações Globais | Alto | Baixo | Baixo | **1** |
| Upload Shapefile | Médio | Baixo | Baixo | **2** |
| Logs de Auditoria | Médio | Baixo | Baixo | **3** |
| 2FA/TOTP | Médio | Médio | Baixo | **4** |
| OAuth2 API | Alto | Alto | Médio | **5** |
| Importação CSV | Alto | Médio | Baixo | **6** |
| SSO Google | Baixo | Médio | Baixo | **7** |

---

## 🔗 Links Relacionados

- [Análise de Gap Completa](docs/contexts/CORE-GAP-ANALYSIS.md)
- [Validação de Limites — Implementação](docs/contexts/IMPLEMENTACAO_LIMITES_RESUMO.md)
- [Sistema de Notificações — Guia](docs/contexts/SISTEMA-NOTIFICACOES-GUIA.md)
- [Especificação de Configurações](docs/contexts/core/configuracoes-globais.md)
- [Especificação de Integrações](docs/contexts/core/integracoes-essenciais.md)

---

**Documento gerado em:** 2026-04-01  
**Próxima revisão:** Após implementação de Configurações Globais  
**Responsável:** Tech Lead
