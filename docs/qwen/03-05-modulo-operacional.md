# Módulo Operacional - Análise de Mercado e Gap Analysis

**Versão:** 1.0.0
**Data:** 2026-03-31
**Status:** Ativo

---

## 📋 Visão Geral

| Atributo | Valor |
|----------|-------|
| **IDs** | O1_FROTA, O2_ESTOQUE, O3_COMPRAS |
| **Categoria** | Operacional |
| **Status** | ✅ Ativo |
| **Preço** | R$ 179-249/mês por submódulo |
| **Score AgroSaaS** | 8/10 |
| **Média Mercado** | 7.5/10 |

---

## 🎯 Funcionalidades Atuais

### O1_FROTA - Controle de Frota
- ✅ Cadastro de equipamentos/máquinas
- ✅ Planos de manutenção preventiva
- ✅ Ordens de serviço (OS)
- ✅ Itens usados em OS
- ✅ Histórico de manutenções
- ✅ Apontamentos de uso
- ✅ Manutenção por horas/km
- ✅ Baixa de estoque de peças
- ✅ OS gera despesa no financeiro

### O2_ESTOQUE - Estoque Multi-armazéns
- ✅ Múltiplos depósitos/armazéns
- ✅ Lotes de produtos (validade)
- ✅ Saldos atuais
- ✅ Histórico de movimentações
- ✅ Requisições de material
- ✅ Aprovação de requisições
- ✅ Reservas de estoque
- ✅ Alertas de estoque mínimo
- ✅ Alertas de validade
- ✅ Transferência entre depósitos
- ✅ Ajuste de inventário

### O3_COMPRAS - Supply e Compras
- ✅ Pedidos de compra
- ✅ Cotações com fornecedores
- ✅ Itens do pedido
- ✅ Aprovação de pedidos
- ✅ Recebimento de pedidos

---

## 🔍 Comparativo com Concorrentes

### SSCrop (Líder em Estoque)
| Funcionalidade | SSCrop | AgroSaaS | Gap |
|----------------|--------|----------|-----|
| Estoque multi-depósito | ✅ | ✅ | - |
| Alertas estoque mínimo | ✅ | ✅ | - |
| Alertas via WhatsApp | ✅ | ❌ | 🔴 Crítico |
| Localização por ponto | ✅ | ❌ | 🟡 Atenção |
| Recebimento XML | ✅ | ❌ | 🟡 Atenção |
| Histórico de compras | ✅ | ✅ | - |
| Pedido de compra | ✅ | ✅ | - |
| Cotação fornecedores | ✅ | ✅ | - |

### Aegro
| Funcionalidade | Aegro | AgroSaaS | Gap |
|----------------|-------|----------|-----|
| Controle de estoque | ✅ | ✅ | - |
| Integração campo-financeiro | ✅ | ✅ | - |
| Conexão com máquinas | ✅ | ❌ | 🟡 Atenção |
| Telemetria | ✅ | ❌ | 🔴 Crítico |
| Previsão de consumo | ✅ | ❌ | 🟡 Atenção |

### MyFarm
| Funcionalidade | MyFarm | AgroSaaS | Gap |
|----------------|--------|----------|-----|
| Gestão de estoque | ✅ | ✅ | - |
| Pedido de compra | ✅ | ✅ | - |
| Recebimento XML | ✅ | ❌ | 🟡 Atenção |
| Cadastro automático fornecedor | ✅ | ❌ | 🟡 Atenção |
| Manutenção preventiva | ✅ | ✅ | - |
| Alertas manutenção | ✅ | ❌ | 🟡 Atenção |
| Consumo de combustível | ✅ | ❌ | 🟡 Atenção |

### eProdutor
| Funcionalidade | eProdutor | AgroSaaS | Gap |
|----------------|-----------|----------|-----|
| Estoque básico | ✅ | ✅ | - |
| Silos automatizados | ✅ | ❌ | 🟡 Atenção |
| Balanças integradas | ✅ | ❌ | 🟡 Atenção |

---

## 📊 Gap Analysis

### 🔴 Gaps Críticos

#### 1. Alertas de Estoque via WhatsApp
**Status:** ❌ Não implementado
**Concorrentes:** SSCrop (diferencial)
**Impacto:** UX significativa para estoquistas
**Esforço:** Baixo
**Prioridade:** 🔴 Alta

**Descrição:** SSCrop envia alertas de estoque mínimo via WhatsApp.

**Implementação Sugerida:**
```python
# services/api/operacional/services/alertas_estoque.py
class AlertaEstoqueService:
    async def verificar_estoque_minimo(self):
        # Query de produtos abaixo do mínimo
        # Enviar alerta WhatsApp para responsável
        
    async def enviar_alerta_whatsapp(self, produto: str, saldo: float, minimo: float):
        # Integração com WhatsApp Business API
        # Enviar mensagem formatada
```

**Ações:**
- [ ] Integração WhatsApp Business API
- [ ] Template de mensagem de alerta
- [ ] Configuração de responsáveis por produto
- [ ] Frequência de alertas (diário, semanal)

---

#### 2. Telemetria de Máquinas
**Status:** ❌ Não implementado
**Concorrentes:** Aegro (John Deere Ops Center), eProdutor
**Impacto:** Agricultura de precisão
**Esforço:** Alto
**Prioridade:** 🔴 Alta

**Descrição:** Integração com telemetria de máquinas (horas, localização, consumo).

**Implementação Sugerida:**
```python
# services/api/operacional/models/telemetria.py
class TelemetriaMaquina(Base):
    __tablename__ = "telemetria_maquinas"
    
    id = Column(UUID, primary_key=True)
    equipamento_id = Column(UUID, ForeignKey('frota_equipamentos.id'))
    timestamp = Column(DateTime)
    horas_motor = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    velocidade = Column(Float)
    consumo_litros_h = Column(Float)
    implemento = Column(String)

@router.get("/operacional/telemetria/{equipamento_id}")
async def get_telemetria(equipamento_id: UUID):
    # Buscar dados de telemetria
    # Integrar com John Deere, Case, New Holland
```

**Ações:**
- [ ] Integração John Deere Ops Center API
- [ ] Integração Case IH (AFS Connect)
- [ ] Integração New Holland (PLM Connect)
- [ ] Dashboard de localização em tempo real
- [ ] Horas de trabalho automáticas
- [ ] Consumo de combustível automático

---

### 🟡 Gaps Competitivos

#### 3. Localização Física no Depósito (Endereçamento)
**Status:** ❌ Não implementado
**Concorrentes:** SSCrop
**Impacto:** Organização de armazéns grandes
**Esforço:** Baixo
**Prioridade:** 🟡 Média

**Descrição:** Endereço físico dentro do depósito (corredor, prateleira, nível).

**Implementação Sugerida:**
```python
# services/api/operacional/models/estoque_enderecos.py
class EnderecoDeposito(Base):
    __tablename__ = "endereco_depositos"
    
    id = Column(UUID, primary_key=True)
    deposito_id = Column(UUID, ForeignKey('estoque_depositos.id'))
    corredor = Column(String)  # 'A', 'B', 'C'
    prateleira = Column(String)  # '01', '02', '03'
    nivel = Column(String)  # '1', '2', '3'
    capacidade = Column(Float)
    
class EstoqueLote(Base):
    # Adicionar campo
    endereco_id = Column(UUID, ForeignKey('endereco_depositos.id'))
```

**Ações:**
- [ ] Cadastro de endereços no depósito
- [ ] Vincular lotes a endereços
- [ ] Mapa visual do depósito
- [ ] Sugestão de endereço na entrada

---

#### 4. Recebimento de XML de Nota Fiscal
**Status:** ❌ Não implementado
**Concorrentes:** SSCrop, MyFarm
**Impacto:** Automação de entrada de mercadoria
**Esforço:** Baixo
**Prioridade:** 🟡 Média

**Descrição:** Importar XML de NF-e de compra para entrada automática de estoque.

**Implementação Sugerida:**
```python
# services/api/operacional/routers/estoque.py
@router.post("/estoque/importar-xml-compra")
async def importar_xml_compra(xml: UploadFile):
    # Parse do XML da NF-e
    # Identificar produtos
    # Criar entrada de estoque automática
    # Vincular ao pedido de compra
```

**Ações:**
- [ ] Parser de XML de NF-e
- [ ] Mapeamento de produtos (código, descrição)
- [ ] Entrada automática de estoque
- [ ] Vinculação com pedido de compra
- [ ] Atualização de saldo

---

#### 5. Alertas de Manutenção Preventiva
**Status:** ❌ Não implementado
**Concorrentes:** MyFarm (diferencial)
**Impacto:** Redução de quebras
**Esforço:** Baixo
**Prioridade:** 🟡 Média

**Descrição:** Alertas automáticos quando máquina atingir horas para manutenção.

**Implementação Sugerida:**
```python
# services/api/operacional/services/manutencao_alertas.py
class ManutencaoAlertaService:
    async def verificar_manutencoes_pendentes(self):
        # Calcular horas até próxima manutenção
        # Enviar alerta se dentro do threshold
```

**Ações:**
- [ ] Cálculo de horas restantes
- [ ] Alertas por e-mail/push
- [ ] Alertas por WhatsApp
- [ ] Agendamento automático de OS

---

#### 6. Consumo de Combustível por Atividade
**Status:** ❌ Não implementado
**Concorrentes:** MyFarm, Aegro
**Impacto:** Controle de custos
**Esforço:** Baixo
**Prioridade:** 🟡 Média

**Descrição:** Registro e cálculo de consumo de combustível por máquina/atividade.

**Implementação Sugerida:**
```python
# services/api/operacional/models/combustivel.py
class Abastecimento(Base):
    __tablename__ = "frota_abastecimentos"
    
    id = Column(UUID, primary_key=True)
    equipamento_id = Column(UUID)
    data = Column(DateTime)
    litros = Column(Float)
    hodometro = Column(Float)
    operador_id = Column(UUID)
    atividade = Column(String)  # 'plantio', 'pulverizacao', 'colheita'
    
class ConsumoMedio(Base):
    # View ou cálculo
    equipamento_id = Column(UUID)
    atividade = Column(String)
    litros_por_hora = Column(Float)
    litros_por_hectare = Column(Float)
```

**Ações:**
- [ ] Registro de abastecimento
- [ ] Cálculo de consumo por hora
- [ ] Cálculo de consumo por hectare
- [ ] Relatório de consumo por atividade
- [ ] Alertas de consumo anormal

---

#### 7. Previsão de Consumo de Insumos
**Status:** ❌ Não implementado
**Concorrentes:** Aegro
**Impacto:** Planejamento de compras
**Esforço:** Médio
**Prioridade:** 🟡 Baixa

**Descrição:** Prever consumo baseado em histórico e planejamento de safra.

**Ações:**
- [ ] Histórico de consumo por safra
- [ ] Projeção baseada em área plantada
- [ ] Sugestão de compra
- [ ] Integração com orçamento

---

#### 8. Integração com Silos e Balanças
**Status:** ❌ Não implementado
**Concorrentes:** eProdutor
**Impacto:** Automação de armazenagem
**Esforço:** Alto
**Prioridade:** 🟡 Baixa

**Descrição:** Leitura automática de nível de silos e balanças.

**Ações:**
- [ ] Integração com sensores de nível
- [ ] Balanças inteligentes
- [ ] Leitura automática de peso
- [ ] Alertas de capacidade

---

### 🟢 Diferenciais AgroSaaS

#### ✅ Estoque Multi-armazéns Completo
**Status:** ✅ Implementado
**Vantagem:** Múltiplos depósitos, transferências
**Concorrentes:** SSCrop e Aegro têm, mas AgroSaaS tem mais recursos

#### ✅ Reservas de Estoque
**Status:** ✅ Implementado
**Vantagem:** Reservar para OS/pedidos específicos
**Concorrentes:** Poucos têm reservas

#### ✅ Requisições com Aprovação
**Status:** ✅ Implementado
**Vantagem:** Workflow de aprovação
**Concorrentes:** SSCrop tem, Aegro básico

#### ✅ Cotações com Fornecedores
**Status:** ✅ Implementado
**Vantagem:** Comparação de cotações
**Concorrentes:** SSCrop e MyFarm têm

---

## 📈 Roadmap Sugerido

### Sprint 1-2 (2 semanas)
- [ ] Alertas de estoque via WhatsApp
- [ ] Endereçamento de depósito
- [ ] Alertas de manutenção preventiva

### Sprint 3-4 (2 semanas)
- [ ] Importação de XML de NF-e
- [ ] Entrada automática de estoque
- [ ] Consumo de combustível por atividade

### Sprint 5-8 (4 semanas)
- [ ] Integração John Deere Ops Center
- [ ] Integração Case IH AFS Connect
- [ ] Dashboard de telemetria

### Sprint 9-10 (2 semanas)
- [ ] Previsão de consumo
- [ ] Sugestão de compras automáticas

---

## 📊 Score Final

| Submódulo | Score | Comentários |
|-----------|-------|-------------|
| O1_FROTA | 7/10 | ✅ Bom, falta telemetria |
| O2_ESTOQUE | 8/10 | ✅ Completo, falta WhatsApp |
| O3_COMPRAS | 8/10 | ✅ Bom, cotações |
| **Média Operacional** | **7.7/10** | **77%** |

| Categoria | Gap | Prioridade |
|-----------|-----|------------|
| Alertas WhatsApp | 🔴 Baixo esforço | 🔴 Alta |
| Telemetria máquinas | 🔴 Alto esforço | 🔴 Alta |
| Endereçamento depósito | 🟡 Baixo esforço | 🟡 Média |
| XML NF-e entrada | 🟡 Baixo esforço | 🟡 Média |
| Alertas manutenção | 🟡 Baixo esforço | 🟡 Média |
| Consumo combustível | 🟡 Baixo esforço | 🟡 Média |

---

## ✅ Resumo Executivo

**Pontos Fortes:**
- Estoque multi-armazéns completo
- Reservas de estoque
- Requisições com aprovação
- Cotações com fornecedores
- OS de manutenção integrada

**Pontos de Atenção:**
- Alertas WhatsApp é baixo esforço, alto impacto
- Telemetria é essencial para agricultura de precisão
- XML de entrada automatiza processo manual
- MyFarm tem alertas de manutenção (diferencial)

**Recomendação Principal:**
Implementar alertas de estoque via WhatsApp (baixo esforço, alto impacto) e endereçamento de depósito. Telemetria pode ser diferencial competitivo a médio prazo.
