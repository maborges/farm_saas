# Módulo Agrícola - Análise de Mercado e Gap Analysis

**Versão:** 1.0.0
**Data:** 2026-03-31
**Status:** Ativo

---

## 📋 Visão Geral

| Atributo | Valor |
|----------|-------|
| **IDs** | A1_PLANEJAMENTO, A2_CAMPO, A3_DEFENSIVOS, A4_PRECISAO, A5_COLHEITA |
| **Categoria** | Agrícola |
| **Status** | ✅ Parcialmente Ativo |
| **Preço** | R$ 199-499/mês por submódulo |
| **Score AgroSaaS** | 8/10 |
| **Média Mercado** | 8.5/10 |

---

## 🎯 Funcionalidades Atuais

### A1_PLANEJAMENTO - Planejamento de Safra
- ✅ Cadastro de safras por ciclo
- ✅ Associação safra-talhões
- ✅ Fases da safra (7 estágios)
- ✅ Orçamento de safra
- ✅ Resumo planejado vs realizado

### A2_CAMPO - Caderno de Campo
- ✅ Operações agrícolas
- ✅ Insumos por operação
- ✅ Apontamentos de campo
- ✅ Cálculo de custos (MO + insumos + máquinas)
- ✅ Período de carência de defensivos
- ✅ Condições climáticas no momento

### A3_DEFENSIVOS - Defensivos e Receituário
- ✅ Monitoramento de pragas
- ✅ Catálogo de pragas/doenças
- ✅ Diagnóstico IA (avulso)
- ✅ Prescrições (receituários)

### A4_PRECISAO - Agricultura de Precisão
- 🔄 NDVI por talhão (em desenvolvimento)
- 🔄 Dados climáticos (em desenvolvimento)
- 🔄 Prescrição VRA (taxa variável)

### A5_COLHEITA - Colheita e Romaneio
- ✅ Romaneios de colheita
- ✅ KPIs de colheita
- ✅ Cálculo de produtividade (sc/ha)
- ✅ Descontos (umidade, impureza, avariados)
- ✅ Rastreabilidade completa

---

## 🔍 Comparativo com Concorrentes

### Aegro
| Funcionalidade | Aegro | AgroSaaS | Gap |
|----------------|-------|----------|-----|
| Planejamento de safra | ✅ | ✅ | - |
| Caderno de campo | ✅ | ✅ | - |
| Comparação preços insumos | ✅ | ❌ | 🔴 Crítico |
| Monitoramento pragas | ✅ | ✅ | - |
| NDVI/Imagens satélite | ✅ | 🔄 | 🟡 Atenção |
| Colheita | ✅ | ✅ | - |
| App offline | ✅ | ❌ | 🔴 Crítico |

### MyFarm
| Funcionalidade | MyFarm | AgroSaaS | Gap |
|----------------|--------|----------|-----|
| Planejamento | ✅ | ✅ | - |
| Atividades de campo | ✅ | ✅ | - |
| Custos por talhão | ✅ | ✅ | - |
| Indicadores climáticos | ✅ | 🔄 | 🟡 Atenção |
| Produtividade por variedade | ✅ | ✅ | - |

### SSCrop
| Funcionalidade | SSCrop | AgroSaaS | Gap |
|----------------|--------|----------|-----|
| Recebimento insumos | ✅ | ❌ | 🟡 Atenção |
| Aplicação por talhão | ✅ | ✅ | - |
| Manutenção máquinas | ✅ | ❌ | 🟡 Atenção |
| Colheita/produtividade | ✅ | ✅ | - |
| Refastecimento | ✅ | ❌ | 🟡 Atenção |

### eProdutor
| Funcionalidade | eProdutor | AgroSaaS | Gap |
|----------------|-----------|----------|-----|
| Imagens de satélite | ✅ | 🔄 | 🟡 Atenção |
| Estação meteorológica | ✅ | 🔄 | 🟡 Atenção |
| Monitoramento agroclimático | ✅ | ❌ | 🟡 Atenção |
| Mapa de fertilidade | ✅ | ❌ | 🔴 Crítico |
| Irrigação | ✅ | ❌ | 🔴 Crítico |
| Indicadores de pulverização | ✅ | ❌ | 🟡 Atenção |

---

## 📊 Gap Analysis

### 🔴 Gaps Críticos

#### 1. Comparação de Preços de Insumos
**Status:** ❌ Não implementado
**Concorrentes:** Aegro (diferencial principal)
**Impacto:** Economia direta para produtor
**Esforço:** Médio
**Prioridade:** 🔴 Alta

**Descrição:** Aegro permite comparar preços de insumos pagos por outros produtores na região, facilitando negociação.

**Implementação Sugerida:**
```python
# services/api/agricola/routers/insumos_preco.py
@router.get("/insumos/preco-medio-regional")
async def get_regional_price(
    insumo_id: UUID,
    regiao: str,
    raio_km: int = 50
):
    # Query anonimizada de preços da região
    # Mostrar média, mínimo, máximo
```

**Ações:**
- [ ] Modelar tabela de preços de insumos (anonimizado)
- [ ] Criar endpoint de comparação regional
- [ ] Dashboard de evolução de preços
- [ ] Alertas de preço baixo
- [ ] Opt-in de compartilhamento de preços

---

#### 2. Mapa de Fertilidade do Solo
**Status:** ❌ Não implementado
**Concorrentes:** eProdutor, Aegro
**Impacto:** Agricultura de precisão essencial
**Esforço:** Alto
**Prioridade:** 🔴 Alta

**Descrição:** Geração de mapas de fertilidade baseados em amostras de solo georreferenciadas.

**Implementação Sugerida:**
```python
# services/api/agricola/models/analise_solo.py
class AmostraSolo(Base):
    __tablename__ = "amostras_solo"
    
    id = Column(UUID, primary_key=True)
    talhao_id = Column(UUID, ForeignKey('talhoes.id'))
    latitude = Column(Float)
    longitude = Column(Float)
    ph = Column(Float)
    materia_organica = Column(Float)
    fosforo = Column(Float)
    potassio = Column(Float)
    # ... outros nutrientes

class MapaFertilidade(Base):
    __tablename__ = "mapas_fertilidade"
    
    id = Column(UUID, primary_key=True)
    talhao_id = Column(UUID)
    nutriente = Column(String)  # 'P', 'K', 'pH', etc.
    interpolacao = Column(JSON)  # GeoJSON do mapa
```

**Ações:**
- [ ] Cadastro de amostras georreferenciadas
- [ ] Interpolação (Krigagem ou IDW)
- [ ] Geração de mapas GeoJSON
- [ ] Visualização no frontend
- [ ] Exportação para máquinas (shapefile)

---

#### 3. Gestão de Irrigação
**Status:** ❌ Não implementado
**Concorrentes:** eProdutor, Climate FieldView
**Impacto:** Essencial para irrigantes
**Esforço:** Alto
**Prioridade:** 🔴 Alta

**Descrição:** Controle de lâmina de água, evapotranspiração, programação de irrigação.

**Implementação Sugerida:**
```python
# services/api/agricola/models/irrigacao.py
class SistemaIrrigacao(Base):
    __tablename__ = "sistemas_irrigacao"
    
    id = Column(UUID, primary_key=True)
    talhao_id = Column(UUID)
    tipo = Column(String)  # 'pivoo', 'gotejo', 'aspersao'
    vazao_m3_h = Column(Float)
    area_hectares = Column(Float)

class RegistroIrrigacao(Base):
    __tablename__ = "registros_irrigacao"
    
    id = Column(UUID, primary_key=True)
    sistema_id = Column(UUID)
    data_inicio = Column(DateTime)
    data_fim = Column(DateTime)
    lâmina_mm = Column(Float)
    volume_m3 = Column(Float)
```

**Ações:**
- [ ] Cadastro de sistemas de irrigação
- [ ] Cálculo de evapotranspiração (ET0)
- [ ] Balanço hídrico
- [ ] Programação de irrigação
- [ ] Integração com estações meteorológicas

---

### 🟡 Gaps Competitivos

#### 4. Alertas Climáticos em Tempo Real
**Status:** 🔄 Parcial (dados climáticos em desenvolvimento)
**Concorrentes:** MyFarm, eProdutor, Aegro
**Impacto:** Prevenção de perdas
**Esforço:** Médio
**Prioridade:** 🟡 Média

**Descrição:** Alertas de geada, granizo, chuva intensa, vento forte.

**Implementação Sugerida:**
```python
# services/api/agricola/services/alertas_climaticos.py
class AlertaClimaticoService:
    async def verificar_alertas(self, talhao_id: UUID):
        # Checar previsão de geada, granizo, etc.
        # Enviar notificação se risco > threshold
```

**Ações:**
- [ ] Integração com API climática (INMET, OpenWeather)
- [ ] Definir thresholds por cultura
- [ ] Sistema de notificações push
- [ ] Histórico de alertas

---

#### 5. Recebimento de Insumos (XML)
**Status:** ❌ Não implementado
**Concorrentes:** SSCrop, MyFarm
**Impacto:** Automação de entrada de notas
**Esforço:** Baixo
**Prioridade:** 🟡 Média

**Descrição:** Recebimento automático de XML de notas fiscais de insumos.

**Implementação Sugerida:**
```python
# services/api/agricola/routers/insumos.py
@router.post("/insumos/importar-xml")
async def importar_xml_insumo(xml: UploadFile):
    # Parse do XML da NF-e
    # Criar entrada de estoque automaticamente
```

**Ações:**
- [ ] Parser de XML de NF-e
- [ ] Mapeamento de produtos
- [ ] Entrada automática de estoque
- [ ] Vinculação com pedido de compra

---

#### 6. Indicadores de Pulverização
**Status:** ❌ Não implementado
**Concorrentes:** eProdutor
**Impacto:** Eficiência de aplicação
**Esforço:** Médio
**Prioridade:** 🟡 Baixa

**Descrição:** Condições ideais de aplicação (vento, temperatura, umidade).

**Ações:**
- [ ] Integração com estação meteorológica
- [ ] Cálculo de deriva potencial
- [ ] Recomendação de jato/bico
- [ ] Registro de condições na aplicação

---

### 🟢 Diferenciais AgroSaaS

#### ✅ Fases da Safra com Validação
**Status:** ✅ Implementado
**Vantagem:** Ciclo de vida estruturado
**Concorrentes:** Maioria não valida transições

#### ✅ Período de Carência
**Status:** ✅ Implementado
**Vantagem:** Compliance e segurança alimentar
**Concorrentes:** Apenas Aegro e SSCrop têm

#### ✅ Rastreabilidade Completa
**Status:** ✅ Implementado
**Vantagem:** Append-only, auditoria
**Concorrentes:** Poucos têm rastreabilidade total

#### ✅ NDVI Integrado
**Status:** 🔄 Em desenvolvimento
**Vantagem:** Agricultura de precisão nativa
**Concorrentes:** eProdutor e Aegro têm

---

## 📈 Roadmap Sugerido

### Sprint 1-2 (2 semanas)
- [ ] Importação XML de insumos
- [ ] Alertas climáticos básicos (geada)
- [ ] Dashboard de preços de insumos (interno)

### Sprint 3-4 (2 semanas)
- [ ] Amostragem de solo georreferenciada
- [ ] Interpolação para mapas de fertilidade
- [ ] Visualização de mapas no frontend

### Sprint 5-6 (2 semanas)
- [ ] Sistemas de irrigação
- [ ] Balanço hídrico
- [ ] Programação de irrigação

### Sprint 7-8 (2 semanas)
- [ ] Comparação de preços (crowdsourcing)
- [ ] Alertas de preço baixo
- [ ] Indicadores de pulverização

---

## 📊 Score Final

| Submódulo | Score | Comentários |
|-----------|-------|-------------|
| A1_PLANEJAMENTO | 9/10 | ✅ Completo, validações |
| A2_CAMPO | 8/10 | ✅ Bom, falta XML |
| A3_DEFENSIVOS | 8/10 | ✅ Bom, falta alertas |
| A4_PRECISAO | 6/10 | 🔄 NDVI em desenvolvimento |
| A5_COLHEITA | 9/10 | ✅ Completo, KPIs |
| **Média Agrícola** | **8/10** | **80%** |

| Categoria | Gap | Prioridade |
|-----------|-----|------------|
| Comparação preços | 🔴 Alto | 🔴 Crítica |
| Mapa fertilidade | 🔴 Alto | 🔴 Alta |
| Irrigação | 🔴 Alto | 🔴 Alta |
| Alertas climáticos | 🟡 Médio | 🟡 Média |
| XML insumos | 🟡 Baixo | 🟡 Média |

---

## ✅ Resumo Executivo

**Pontos Fortes:**
- Fases da safra validadas
- Período de carência implementado
- Rastreabilidade completa
- Colheita com KPIs detalhados

**Pontos de Atenção:**
- Comparação de preços é diferencial da Aegro
- Mapa de fertilidade essencial para precisão
- Irrigação ausente (grande gap)
- NDVI precisa ser acelerado

**Recomendação Principal:**
Implementar comparação de preços de insumos (baixo esforço, alto impacto) e acelerar NDVI/mapa de fertilidade para competir em agricultura de precisão.
