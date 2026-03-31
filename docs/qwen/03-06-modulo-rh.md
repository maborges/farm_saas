# Módulo RH - Análise de Mercado e Gap Analysis

**Versão:** 1.0.0
**Data:** 2026-03-31
**Status:** Ativo

---

## 📋 Visão Geral

| Atributo | Valor |
|----------|-------|
| **IDs** | RH1_REMUNERACAO, RH2_SEGURANCA |
| **Categoria** | Recursos Humanos |
| **Status** | 🟡 Parcialmente Ativo |
| **Preço** | R$ 149-199/mês por submódulo |
| **Score AgroSaaS** | 6/10 |
| **Média Mercado** | 6.5/10 |

---

## 🎯 Funcionalidades Atuais

### RH1_REMUNERACAO - Remuneração Rural
- ✅ Cadastro de colaboradores
- ✅ Lançamento de diárias
- ✅ Empreitadas
- ✅ Pagamento por produção
- ✅ Integração com financeiro

### RH2_SEGURANCA - Segurança do Trabalho
- 📋 EPIs (Equipamentos de Proteção Individual)
- 📋 EPCs (Equipamentos de Proteção Coletiva)
- 📋 PPP (Perfil Profissiográfico Previdenciário)
- 📋 PCMSO (Programa de Controle Médico de Saúde Ocupacional)
- 📋 NR-31 compliance

---

## 🔍 Comparativo com Concorrentes

### Aegro
| Funcionalidade | Aegro | AgroSaaS | Gap |
|----------------|-------|----------|-----|
| Gestão de equipe | ✅ | ✅ | - |
| Tarefas por colaborador | ✅ | ❌ | 🟡 Atenção |
| Apontamento de horas | ✅ | ❌ | 🟡 Atenção |
| Diárias | ✅ | ✅ | - |
| Produção por colaborador | ✅ | ✅ | - |
| App offline para equipe | ✅ | ❌ | 🔴 Crítico |

### MyFarm
| Funcionalidade | MyFarm | AgroSaaS | Gap |
|----------------|--------|----------|-----|
| Colaboradores | ✅ | ✅ | - |
| Apontamentos | ✅ | ❌ | 🟡 Atenção |
| Treinamentos | ✅ | ❌ | 🟡 Atenção |

### SSCrop
| Funcionalidade | SSCrop | AgroSaaS | Gap |
|----------------|--------|----------|-----|
| Colaboradores | ✅ | ✅ | - |
| Permissões de usuário | ✅ | ✅ | - |
| RH básico | ✅ | ✅ | - |

### eProdutor
| Funcionalidade | eProdutor | AgroSaaS | Gap |
|----------------|-----------|----------|-----|
| Treinamento de funcionários | ✅ | ❌ | 🔴 Crítico |
| App para colaboradores | ✅ | ❌ | 🔴 Crítico |
| Apontamentos | ✅ | ❌ | 🟡 Atenção |

### Softfocus (Especializado em RH Rural)
| Funcionalidade | Softfocus | AgroSaaS | Gap |
|----------------|-----------|----------|-----|
| Folha de pagamento | ✅ | ❌ | 🔴 Crítico |
| eSocial | ✅ | ❌ | 🔴 Crítico |
| EPI com ficha | ✅ | ❌ | 🟡 Atenção |
| Exames médicos | ✅ | ❌ | 🟡 Atenção |
| NR-31 completo | ✅ | ❌ | 🔴 Crítico |

---

## 📊 Gap Analysis

### 🔴 Gaps Críticos

#### 1. App para Colaboradores (Apontamentos)
**Status:** ❌ Não implementado
**Concorrentes:** Aegro, eProdutor
**Impacto:** Essencial para registro de horas no campo
**Esforço:** Alto
**Prioridade:** 🔴 Alta

**Descrição:** App para colaboradores registrarem horas trabalhadas, atividades, produção.

**Implementação Sugerida:**
```python
# services/api/rh/models/apontamentos.py
class ApontamentoHora(Base):
    __tablename__ = "rh_apontamentos_horas"
    
    id = Column(UUID, primary_key=True)
    colaborador_id = Column(UUID, ForeignKey('rh_colaboradores.id'))
    data = Column(Date)
    hora_inicio = Column(Time)
    hora_fim = Column(Time)
    atividade = Column(String)
    talhao_id = Column(UUID)
    producao = Column(Float)
    unidade = Column(String)  # 'hectares', 'caixas', 'litros'

@router.post("/rh/apontamentos")
async def registrar_apontamento(apontamento: ApontamentoSchema):
    # Registrar horas e produção
    # Integrar com pagamento por produção
```

**Ações:**
- [ ] App mobile para colaboradores
- [ ] Registro de horas trabalhadas
- [ ] Registro de produção (opcional)
- [ ] Aprovação de apontamentos pelo gestor
- [ ] Integração com remuneração

---

#### 2. Folha de Pagamento Rural
**Status:** ❌ Não implementado
**Concorrentes:** Softfocus, Aegro
**Impacto:** Essencial para fechamento de folha
**Esforço:** Alto
**Prioridade:** 🔴 Alta

**Descrição:** Cálculo de folha de pagamento com especificidades rurais (FUNRURAL, etc.).

**Implementação Sugerida:**
```python
# services/api/rh/models/folha_pagamento.py
class FolhaPagamento(Base):
    __tablename__ = "rh_folha_pagamento"
    
    id = Column(UUID, primary_key=True)
    colaborador_id = Column(UUID)
    mes_referencia = Column(Integer)
    ano_referencia = Column(Integer)
    salario_base = Column(Float)
    diarias = Column(Float)
    producao = Column(Float)
    horas_extras = Column(Float)
    descontos = Column(JSON)
    proventos = Column(JSON)
    liquido = Column(Float)
    funrural = Column(Float)
    
@router.post("/rh/folha/calcular")
async def calcular_folha(mes: int, ano: int):
    # Calcular folha de todos colaboradores
    # Incluir FUNRURAL, IRRF, INSS
    # Gerar recibos
```

**Ações:**
- [ ] Cálculo de salário base
- [ ] Cálculo de diárias
- [ ] Cálculo de produção
- [ ] Horas extras
- [ ] Descontos (INSS, IRRF, vale)
- [ ] FUNRURAL (específico rural)
- [ ] Geração de recibos (PDF)

---

#### 3. eSocial
**Status:** ❌ Não implementado
**Concorrentes:** Softfocus (diferencial), Aegro
**Impacto:** Obrigatório por lei
**Esforço:** Alto
**Prioridade:** 🔴 Crítica

**Descrição:** Envio de eventos para o eSocial (admissão, folha, desligamento).

**Implementação Sugerida:**
```python
# services/api/rh/services/esocial.py
class ESocialService:
    async def enviar_admissao(self, colaborador_id: UUID):
        # Gerar XML S-2200 (Cadastramento Inicial do Vínculo)
        # Assinar digitalmente
        # Transmitir para eSocial
        # Receber recibo
        
    async def enviar_folha(self, folha_id: UUID):
        # Gerar XML S-1200 (Remuneração do Trabalhador)
        # Transmitir para eSocial
```

**Ações:**
- [ ] Integração com eSocial (WebService)
- [ ] Certificado digital
- [ ] Evento S-2200 (Admissão)
- [ ] Evento S-2300 (Trabalhador Temporário)
- [ ] Evento S-1200 (Remuneração)
- [ ] Evento S-2299 (Desligamento)
- [ ] Validação de XML
- [ ] Tratamento de retornos

---

### 🟡 Gaps Competitivos

#### 4. Gestão de EPIs com Fichas
**Status:** ❌ Não implementado
**Concorrentes:** Softfocus, Aegro
**Impacto:** Compliance NR-31
**Esforço:** Baixo
**Prioridade:** 🟡 Alta

**Descrição:** Controle de entrega de EPIs com fichas de assinatura.

**Implementação Sugerida:**
```python
# services/api/rh/models/epis.py
class EPI(Base):
    __tablename__ = "rh_epis"
    
    id = Column(UUID, primary_key=True)
    nome = Column(String)
    ca = Column(String)  # Certificado de Aprovação
    validade_ca = Column(Date)
    
class EntregaEPI(Base):
    __tablename__ = "rh_entrega_epis"
    
    id = Column(UUID, primary_key=True)
    colaborador_id = Column(UUID)
    epi_id = Column(UUID)
    data_entrega = Column(DateTime)
    quantidade = Column(Integer)
    assinatura_digital = Column(String)
    termo_responsabilidade = Column(Text)
```

**Ações:**
- [ ] Cadastro de EPIs com CA
- [ ] Registro de entrega
- [ ] Ficha de EPI (PDF para assinatura)
- [ ] Alertas de troca periódica
- [ ] Controle de validade do CA

---

#### 5. Exames Médicos (PCMSO)
**Status:** ❌ Não implementado
**Concorrentes:** Softfocus
**Impacto:** Compliance NR-31
**Esforço:** Médio
**Prioridade:** 🟡 Média

**Descrição:** Controle de exames admissionais, periódicos, demissionais.

**Implementação Sugerida:**
```python
# services/api/rh/models/exames.py
class ExameMedico(Base):
    __tablename__ = "rh_exames_medicos"
    
    id = Column(UUID, primary_key=True)
    colaborador_id = Column(UUID)
    tipo = Column(String)  # 'admissional', 'periodico', 'demissional'
    data_realizacao = Column(Date)
    data_vencimento = Column(Date)
    clinica = Column(String)
    medico = Column(String)
    crm = Column(String)
    apto = Column(Boolean)
    restricoes = Column(Text)
    atestado = Column(Text)
```

**Ações:**
- [ ] Cadastro de exames
- [ ] Agendamento de exames
- [ ] Alertas de vencimento
- [ ] Armazenamento de atestados
- [ ] Relatório de PCMSO

---

#### 6. Treinamentos de Funcionários
**Status:** ❌ Não implementado
**Concorrentes:** eProdutor (diferencial)
**Impacto:** Capacitação de equipe
**Esforço:** Médio
**Prioridade:** 🟡 Baixa

**Descrição:** Plataforma de treinamentos para colaboradores.

**Ações:**
- [ ] Catálogo de treinamentos
- [ ] Atribuição de treinamentos
- [ ] Acompanhamento de conclusão
- [ ] Certificados
- [ ] Integração com app do colaborador

---

#### 7. NR-31 Compliance Completo
**Status:** ❌ Não implementado
**Concorrentes:** Softfocus
**Impacto:** Compliance legal
**Esforço:** Médio
**Prioridade:** 🟡 Alta

**Descrição:** Atendimento completo à Norma Regulamentadora 31 (segurança no trabalho rural).

**Ações:**
- [ ] Checklist NR-31
- [ ] Registro de EPIs/EPCs
- [ ] Treinamentos obrigatórios
- [ ] Exames médicos
- [ ] Análise de riscos
- [ ] Relatório de compliance

---

### 🟢 Diferenciais AgroSaaS

#### ✅ Diárias e Empreitadas
**Status:** ✅ Implementado
**Vantagem:** Específico para trabalho rural
**Concorrentes:** Aegro e Softfocus têm, mas AgroSaaS tem modelo mais flexível

#### ✅ Pagamento por Produção
**Status:** ✅ Implementado
**Vantagem:** Integração com colheita/produção
**Concorrentes:** Aegro tem, Softfocus básico

---

## 📈 Roadmap Sugerido

### Sprint 1-4 (4 semanas) - **eSocial Crítico**
- [ ] Integração eSocial (WebService)
- [ ] Evento S-2200 (Admissão)
- [ ] Evento S-1200 (Remuneração)
- [ ] Certificado digital

### Sprint 5-6 (2 semanas)
- [ ] Folha de pagamento rural
- [ ] Cálculo de FUNRURAL
- [ ] Recibos de pagamento

### Sprint 7-8 (2 semanas)
- [ ] Gestão de EPIs
- [ ] Fichas de entrega (PDF)
- [ ] Alertas de troca

### Sprint 9-10 (2 semanas)
- [ ] App para colaboradores (MVP)
- [ ] Apontamento de horas
- [ ] Aprovação de apontamentos

### Sprint 11-12 (2 semanas)
- [ ] Exames médicos (PCMSO)
- [ ] Alertas de vencimento
- [ ] NR-31 checklist

---

## 📊 Score Final

| Submódulo | Score | Comentários |
|-----------|-------|-------------|
| RH1_REMUNERACAO | 6/10 | 🟡 Básico, falta folha |
| RH2_SEGURANCA | 2/10 | ❌ Não implementado |
| **Média RH** | **4/10** | **40%** |

| Categoria | Gap | Prioridade |
|-----------|-----|------------|
| eSocial | 🔴 Crítico | 🔴 Crítica |
| Folha de pagamento | 🔴 Alto | 🔴 Alta |
| App colaborador | 🔴 Alto | 🔴 Alta |
| EPI com fichas | 🟡 Médio | 🟡 Alta |
| Exames médicos | 🟡 Médio | 🟡 Média |
| NR-31 completo | 🟡 Médio | 🟡 Alta |

---

## ✅ Resumo Executivo

**Pontos Fortes:**
- Diárias e empreitadas implementadas
- Pagamento por produção integrado
- Modelo flexível de remuneração rural

**Pontos de Atenção:**
- **eSocial é obrigatório** - sem isso não compete
- Folha de pagamento é essencial
- App para colaboradores é esperado (Aegro tem)
- NR-31 compliance é diferencial de Softfocus

**Recomendação Principal:**
**PRIORIDADE MÁXIMA:** Implementar eSocial e folha de pagamento rural. Sem eSocial, o módulo RH não é viável para produtores formais. App para colaboradores pode ser diferencial competitivo.
