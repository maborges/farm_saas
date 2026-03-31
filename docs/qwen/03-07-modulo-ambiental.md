# Módulo Ambiental - Análise de Mercado e Gap Analysis

**Versão:** 1.0.0
**Data:** 2026-03-31
**Status:** Ativo

---

## 📋 Visão Geral

| Atributo | Valor |
|----------|-------|
| **IDs** | AM1_COMPLIANCE, AM2_CARBONO |
| **Categoria** | Ambiental |
| **Status** | ❌ Planejado |
| **Preço** | R$ 299-499/mês por submódulo |
| **Score AgroSaaS** | 2/10 |
| **Média Mercado** | 6/10 |

---

## 🎯 Funcionalidades Atuais

### AM1_COMPLIANCE - Compliance Ambiental
- 📋 CAR (Cadastro Ambiental Rural)
- 📋 CCIR (Certificado de Cadastro de Imóvel Rural)
- 📋 Outorgas hídricas
- 📋 APP (Área de Preservação Permanente)
- 📋 RL (Reserva Legal)

### AM2_CARBONO - Gestão de Carbono
- 📋 MRV (Monitoramento, Reporte e Verificação)
- 📋 Pegada de carbono
- 📋 Créditos de carbono
- 📋 Relatórios de sustentabilidade

---

## 🔍 Comparativo com Concorrentes

### Agrotools (Líder em Compliance Ambiental)
| Funcionalidade | Agrotools | AgroSaaS | Gap |
|----------------|-----------|----------|-----|
| Monitoramento socioambient | ✅ | ❌ | 🔴 Crítico |
| Rastreabilidade de origem | ✅ | ❌ | 🔴 Crítico |
| Compliance CAR/CCIR | ✅ | ❌ | 🔴 Crítico |
| Análise de riscos | ✅ | ❌ | 🔴 Crítico |
| Due diligence | ✅ | ❌ | 🟡 Atenção |
| Green finance | ✅ | ❌ | 🟡 Atenção |

### Aegro
| Funcionalidade | Aegro | AgroSaaS | Gap |
|----------------|-------|----------|-----|
| CAR integrado | ✅ | ❌ | 🔴 Crítico |
| Monitoramento APP/RL | ✅ | ❌ | 🔴 Crítico |
| Compliance ambiental | ✅ | ❌ | 🔴 Crítico |
| Relatórios ambientais | ✅ | ❌ | 🟡 Atenção |

### SSCrop
| Funcionalidade | SSCrop | AgroSaaS | Gap |
|----------------|--------|----------|-----|
| CAR básico | ✅ | ❌ | 🔴 Crítico |
| Licenças ambientais | ✅ | ❌ | 🟡 Atenção |

### Climate FieldView (Bayer)
| Funcionalidade | Climate | AgroSaaS | Gap |
|----------------|---------|----------|-----|
| Sustentabilidade | ✅ | ❌ | 🟡 Atenção |
| Práticas conservacionistas | ✅ | ❌ | 🟡 Atenção |
| Relatórios ESG | ✅ | ❌ | 🟡 Atenção |

### Strider (Monitoramento de Pragas + Ambiental)
| Funcionalidade | Strider | AgroSaaS | Gap |
|----------------|---------|----------|-----|
| Monitoramento via satélite | ✅ | 🔄 | 🟡 Atenção |
| Alertas de desmatamento | ✅ | ❌ | 🔴 Crítico |
| Compliance cadeia | ✅ | ❌ | 🟡 Atenção |

---

## 📊 Gap Analysis

### 🔴 Gaps Críticos

#### 1. CAR (Cadastro Ambiental Rural)
**Status:** ❌ Não implementado
**Concorrentes:** Agrotools, Aegro, SSCrop (todos têm)
**Impacto:** Obrigatório por lei para imóveis rurais
**Esforço:** Alto
**Prioridade:** 🔴 Crítica

**Descrição:** Módulo para gestão do CAR, incluindo sobreposição com terras indígenas, quilombolas, unidades de conservação.

**Implementação Sugerida:**
```python
# services/api/ambiental/models/car.py
class CAR(Base):
    __tablename__ = "ambiental_car"
    
    id = Column(UUID, primary_key=True)
    tenant_id = Column(UUID)
    fazenda_id = Column(UUID, ForeignKey('fazendas.id'))
    codigo_car = Column(String)  # Código do CAR
    area_total = Column(Float)
    area_app = Column(Float)
    area_rl = Column(Float)
    area_uso_restrito = Column(Float)
    area_consolidada = Column(Float)
    sobreposicoes = Column(JSON)  # TI, UC, quilombos
    status = Column(String)  # 'ativo', 'pendente', 'cancelado'
    data_cadastro = Column(DateTime)
    data_atualizacao = Column(DateTime)
    recibo = Column(Text)

@router.post("/ambiental/car/importar")
async def importar_car(recibo: str):
    # Importar CAR do SNA (Sistema Nacional de CAR)
    # Parse do recibo
    # Calcular áreas
```

**Ações:**
- [ ] Importação de CAR do SNA
- [ ] Cálculo de áreas (APP, RL, uso restrito)
- [ ] Verificação de sobreposições
- [ ] Alertas de pendências
- [ ] Renovação de CAR
- [ ] Integração com SIG (Sistema de Informação Geográfica)

---

#### 2. Monitoramento de APP e Reserva Legal
**Status:** ❌ Não implementado
**Concorrentes:** Aegro, Agrotools
**Impacto:** Compliance ambiental obrigatório
**Esforço:** Alto
**Prioridade:** 🔴 Alta

**Descrição:** Monitoramento de Áreas de Preservação Permanente e Reserva Legal via satélite.

**Implementação Sugerida:**
```python
# services/api/ambiental/models/monitoramento.py
class MonitoramentoAPP(Base):
    __tablename__ = "ambiental_monitoramento_app"
    
    id = Column(UUID, primary_key=True)
    fazenda_id = Column(UUID)
    data = Column(Date)
    area_app_hectares = Column(Float)
    area_desmatada = Column(Float)
    alertas = Column(JSON)
    imagem_satelite_url = Column(String)
    
class ReservaLegal(Base):
    __tablename__ = "ambiental_reserva_legal"
    
    id = Column(UUID, primary_key=True)
    fazenda_id = Column(UUID)
    area_total_rl = Column(Float)
    area_vegetacao_nativa = Column(Float)
    percentual_rl = Column(Float)  # Mínimo 20% (varia por estado)
```

**Ações:**
- [ ] Integração com imagens de satélite (Sentinel-2, Landsat)
- [ ] Detecção de desmatamento
- [ ] Cálculo de percentual de RL
- [ ] Alertas de supressão não autorizada
- [ ] Relatório de conformidade

---

#### 3. Alertas de Desmatamento
**Status:** ❌ Não implementado
**Concorrentes:** Strider, Agrotools, Aegro
**Impacto:** Prevenção de multas ambientais
**Esforço:** Alto
**Prioridade:** 🔴 Alta

**Descrição:** Alertas automáticos de desmatamento detectado via satélite.

**Implementação Sugerida:**
```python
# services/api/ambiental/services/alertas_desmatamento.py
class AlertaDesmatamentoService:
    async def verificar_desmatamento(self, fazenda_id: UUID):
        # Analisar imagens de satélite (últimos 30 dias)
        # Detectar mudança de cobertura vegetal
        # Calcular área desmatada
        # Enviar alerta se área > threshold
```

**Ações:**
- [ ] Integração com API de monitoramento (MapBiomas, INPE)
- [ ] Análise de mudança de cobertura
- [ ] Thresholds configuráveis
- [ ] Alertas por e-mail/SMS/WhatsApp
- [ ] Relatório para órgãos ambientais

---

#### 4. Outorgas Hídricas
**Status:** ❌ Não implementado
**Concorrentes:** Aegro
**Impacto:** Compliance para uso de água
**Esforço:** Médio
**Prioridade:** 🟡 Alta

**Descrição:** Gestão de outorgas para captação de água (superficial e subterrânea).

**Implementação Sugerida:**
```python
# services/api/ambiental/models/outorgas.py
class OutorgaHidrica(Base):
    __tablename__ = "ambiental_outorgas_hidricas"
    
    id = Column(UUID, primary_key=True)
    fazenda_id = Column(UUID)
    tipo = Column(String)  # 'superficial', 'subterranea'
    numero_outorga = Column(String)
    orgao_emissor = Column(String)  # 'ANA', 'DAEE', etc.
    data_emissao = Column(Date)
    data_vencimento = Column(Date)
    vazao_maxima = Column(Float)  # m³/h
    volume_maximo_anual = Column(Float)  # m³/ano
    uso = Column(String)  # 'irrigacao', 'animal', 'industrial'
    status = Column(String)  # 'ativa', 'vencida', 'renovacao'
```

**Ações:**
- [ ] Cadastro de outorgas
- [ ] Alertas de vencimento
- [ ] Renovação de outorgas
- [ ] Medição de consumo (integração com hidrômetros)
- [ ] Relatório de consumo

---

### 🟡 Gaps Competitivos

#### 5. Pegada de Carbono
**Status:** ❌ Não implementado
**Concorrentes:** Climate FieldView, Agrotools
**Impacto:** Mercado de carbono em crescimento
**Esforço:** Alto
**Prioridade:** 🟡 Média

**Descrição:** Cálculo de emissões de GEE (Gases de Efeito Estufa) da propriedade.

**Ações:**
- [ ] Cálculo de emissões por atividade
- [ ] Sequestro de carbono (solo, biomassa)
- [ ] Balanço de carbono
- [ ] Relatório de pegada
- [ ] Certificação opcional

---

#### 6. Créditos de Carbono
**Status:** ❌ Não implementado
**Concorrentes:** Agrotools
**Impacto:** Receita adicional
**Esforço:** Alto
**Prioridade:** 🟡 Baixa

**Descrição:** Gestão de créditos de carbono para comercialização.

**Ações:**
- [ ] Metodologias de projeto (Verra, Gold Standard)
- [ ] MRV (Monitoramento, Reporte, Verificação)
- [ ] Registro de créditos
- [ ] Comercialização
- [ ] Relatórios de verificação

---

#### 7. Relatórios de Sustentabilidade (ESG)
**Status:** ❌ Não implementado
**Concorrentes:** Climate FieldView, Agrotools
**Impacto:** Demanda de compradores/exportação
**Esforço:** Médio
**Prioridade:** 🟡 Média

**Descrição:** Relatórios ESG (Environmental, Social, Governance) para compradores e investidores.

**Ações:**
- [ ] Indicadores ambientais
- [ ] Indicadores sociais
- [ ] Indicadores de governança
- [ ] Relatórios padronizados (GRI, SASB)
- [ ] Exportação PDF

---

#### 8. CCIR (Certificado de Cadastro de Imóvel Rural)
**Status:** ❌ Não implementado
**Concorrentes:** Aegro, SSCrop
**Impacto:** Obrigatório para financiamento
**Esforço:** Baixo
**Prioridade:** 🟡 Média

**Descrição:** Gestão de CCIR do INCRA.

**Ações:**
- [ ] Cadastro de CCIR
- [ ] Alertas de vencimento (anual)
- [ ] Integração com INCRA (opcional)
- [ ] Download de certificado

---

### 🟢 Diferenciais AgroSaaS Potenciais

#### ✅ Integração com Outros Módulos
**Vantagem:** Ambiental integrado com agrícola, financeiro, pecuária
**Concorrentes:** Maioria tem ambiental isolado

#### ✅ MRV Nativo
**Vantagem:** Monitoramento, Reporte e Verificação integrado
**Concorrentes:** Agrotools tem, mas é caro

---

## 📈 Roadmap Sugerido

### Sprint 1-4 (4 semanas) - **CAR Crítico**
- [ ] Importação de CAR do SNA
- [ ] Cálculo de áreas (APP, RL)
- [ ] Verificação de sobreposições
- [ ] Alertas de pendências

### Sprint 5-6 (2 semanas)
- [ ] Monitoramento de APP/RL
- [ ] Integração com imagens de satélite
- [ ] Alertas de desmatamento

### Sprint 7-8 (2 semanas)
- [ ] Outorgas hídricas
- [ ] Alertas de vencimento
- [ ] CCIR

### Sprint 9-12 (4 semanas)
- [ ] Pegada de carbono (MVP)
- [ ] Relatórios de sustentabilidade
- [ ] Integração com módulos existentes

---

## 📊 Score Final

| Submódulo | Score | Comentários |
|-----------|-------|-------------|
| AM1_COMPLIANCE | 2/10 | ❌ Não implementado |
| AM2_CARBONO | 2/10 | ❌ Não implementado |
| **Média Ambiental** | **2/10** | **20%** |

| Categoria | Gap | Prioridade |
|-----------|-----|------------|
| CAR | 🔴 Crítico | 🔴 Crítica |
| Monitoramento APP/RL | 🔴 Alto | 🔴 Alta |
| Alertas desmatamento | 🔴 Alto | 🔴 Alta |
| Outorgas hídricas | 🟡 Médio | 🟡 Alta |
| Pegada de carbono | 🟡 Médio | 🟡 Média |
| Créditos de carbono | 🟡 Alto | 🟡 Baixa |

---

## ✅ Resumo Executivo

**Pontos Fortes:**
- Nenhum implementado atualmente
- Oportunidade de criar módulo moderno
- Integração com outros módulos é diferencial

**Pontos de Atenção:**
- **CAR é obrigatório** - produtores precisam gerenciar
- Alertas de desmatamento previnem multas
- Agrotools domina mercado enterprise
- Aegro tem ambiental completo

**Recomendação Principal:**
**PRIORIDADE ALTA:** Implementar CAR e monitoramento de APP/RL nas próximas sprints. É requisito básico para competir no mercado. Alertas de desmatamento são diferenciais importantes. Módulo de carbono pode ser fase 2.
