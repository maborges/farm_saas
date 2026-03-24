# 🚀 Plano de Modularização Completa - AgroSaaS

## 📋 Visão Geral

Este documento descreve o plano completo de modularização do AgroSaaS, transformando o sistema atual em um SaaS verdadeiramente modular com módulos vendáveis individualmente.

**Data de início:** 2026-03-10
**Status:** Em execução
**Responsável:** Equipe de Arquitetura

## 🎯 Objetivos

1. **Granularidade Comercial**: Cada módulo é uma unidade vendável independente
2. **Isolamento Técnico**: Cada módulo possui suas próprias entidades, lógica e rotas
3. **Feature Gates**: Sistema dinâmico de controle de acesso por módulo contratado
4. **Precificação Flexível**: Permitir pacotes customizados à la carte
5. **Escalabilidade**: Facilitar o crescimento da equipe (1 dev por módulo)

## 📊 Estado Atual vs Estado Desejado

### Antes (Monolito por Domínio)
```
agricola/           → 1 módulo grande
  ├── safras/
  ├── operacoes/
  ├── ndvi/
  └── ...
```

### Depois (Módulos Granulares)
```
agricola/
  ├── a1_planejamento/    → Módulo vendável independente
  ├── a2_campo/           → Módulo vendável independente
  ├── a3_defensivos/      → Módulo vendável independente
  ├── a4_precisao/        → Módulo vendável independente
  └── a5_colheita/        → Módulo vendável independente
```

## 🗺️ Mapa de Módulos

### CORE (Obrigatório - Não vendável separadamente)
- Multi-tenancy
- Autenticação/Autorização
- GIS Base
- Billing
- Support

### BLOCO AGRÍCOLA (5 módulos)
| ID | Nome | Preço/mês | Status |
|----|------|-----------|--------|
| A1_PLANEJAMENTO | Planejamento de Safra | R$ 199 | 🔄 A criar |
| A2_CAMPO | Caderno de Campo | R$ 299 | 🔄 A criar |
| A3_DEFENSIVOS | Defensivos e Receituário | R$ 149 | 🔄 A criar |
| A4_PRECISAO | Agricultura de Precisão | R$ 499 | 🔄 A criar |
| A5_COLHEITA | Colheita e Romaneio | R$ 249 | 🔄 A criar |

### BLOCO PECUÁRIA (4 módulos)
| ID | Nome | Preço/mês | Status |
|----|------|-----------|--------|
| P1_REBANHO | Controle de Rebanho | R$ 249 | 🔄 A criar |
| P2_GENETICA | Genética Reprodutiva | R$ 349 | 🔄 A criar |
| P3_CONFINAMENTO | Feedlot Control | R$ 399 | 🔄 A criar |
| P4_LEITE | Pecuária Leiteira | R$ 299 | 🔄 A criar |

### BLOCO FINANCEIRO (4 módulos)
| ID | Nome | Preço/mês | Status |
|----|------|-----------|--------|
| F1_TESOURARIA | Tesouraria | R$ 199 | 🔄 A criar |
| F2_CUSTOS_ABC | Custos ABC | R$ 299 | 🔄 A criar |
| F3_FISCAL | Fiscal e Compliance | R$ 449 | 🔄 A criar |
| F4_HEDGING | Hedging e Futuros | R$ 599 | 🔄 A criar |

### BLOCO OPERACIONAL (3 módulos)
| ID | Nome | Preço/mês | Status |
|----|------|-----------|--------|
| O1_FROTA | Controle de Frota | R$ 179 | 🔄 A criar |
| O2_ESTOQUE | Estoque Multi-armazéns | R$ 199 | 🔄 A criar |
| O3_COMPRAS | Supply e Compras | R$ 249 | 🔄 A criar |

**Total de módulos vendáveis:** 20

## 🛠️ Ferramentas Criadas

### 1. Sistema de Constantes de Módulos
**Arquivo:** `services/api/core/constants.py`

Define todos os IDs de módulos, metadados e preços:
```python
from core.constants import Modulos

# Usar em feature gates
@router.get("/", dependencies=[Depends(require_module(Modulos.AGRICOLA_PLANEJAMENTO))])
```

### 2. Feature Gates Dinâmicos
**Arquivo:** `services/api/core/dependencies.py`

Três tipos de feature gates:
- `require_module(modulo_id)` - Requer um módulo específico
- `require_any_module(*modulos)` - Requer qualquer um dos módulos
- `require_all_modules(*modulos)` - Requer todos os módulos

### 3. Script Gerador de Módulos
**Arquivo:** `services/api/scripts/create_module.py`

Cria estrutura completa de um novo módulo:
```bash
python scripts/create_module.py \
  --modulo A1_PLANEJAMENTO \
  --dominio agricola \
  --nome "Planejamento de Safra"
```

Gera automaticamente:
- `__init__.py`
- `router.py` (com feature gates)
- `models.py` (templates SQLAlchemy)
- `schemas.py` (templates Pydantic)
- `services.py` (lógica de negócio)
- `README.md` (documentação)

## 📐 Arquitetura de Módulo Padrão

Cada módulo segue esta estrutura:

```
{dominio}/{modulo_id}/
├── __init__.py          # Exports
├── router.py            # FastAPI endpoints com feature gates
├── models.py            # SQLAlchemy models (tenant_id obrigatório)
├── schemas.py           # Pydantic schemas (Create/Update/Response)
├── services.py          # Lógica de negócio
├── dependencies.py      # Dependencies específicas (opcional)
├── exceptions.py        # Exceções customizadas (opcional)
├── tests/               # Testes unitários e integração
│   ├── test_services.py
│   └── test_router.py
└── README.md            # Documentação do módulo
```

### Princípios de Design

1. **Multi-tenancy Obrigatório**: Todo model tem `tenant_id` com index
2. **Feature Gates**: Toda rota protegida com `require_module()`
3. **Separação de Responsabilidades**:
   - Router = HTTP (validação de entrada)
   - Service = Lógica de negócio
   - Model = Persistência
4. **Schemas Explícitos**: Nunca retornar models diretamente
5. **Testes Obrigatórios**: Mínimo 80% de cobertura

## 🔄 Processo de Criação de Módulo

### Passo a Passo

#### 1. Verificar se o módulo está em `core/constants.py`
```python
# Se não estiver, adicionar em Modulos e ModuloMetadata.CATALOGO
```

#### 2. Gerar estrutura base
```bash
cd services/api
python scripts/create_module.py \
  --modulo A1_PLANEJAMENTO \
  --dominio agricola
```

#### 3. Implementar Models
```python
# agricola/a1_planejamento/models.py
class Safra(Base):
    __tablename__ = "safras"
    id: Mapped[uuid.UUID] = ...
    tenant_id: Mapped[uuid.UUID] = ...  # OBRIGATÓRIO
    # ... outros campos
```

#### 4. Criar Schemas
```python
# agricola/a1_planejamento/schemas.py
class SafraCreate(BaseModel): ...
class SafraUpdate(BaseModel): ...
class SafraResponse(BaseModel): ...
```

#### 5. Implementar Services
```python
# agricola/a1_planejamento/services.py
class SafraService:
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id
```

#### 6. Criar Rotas
```python
# agricola/a1_planejamento/router.py
@router.post(
    "/safras",
    dependencies=[Depends(require_module(Modulos.AGRICOLA_PLANEJAMENTO))]
)
async def criar_safra(...):
    pass
```

#### 7. Registrar no `main.py`
```python
from agricola.a1_planejamento.router import router as router_planejamento

app.include_router(router_planejamento, prefix="/api/v1")
```

#### 8. Criar Migration
```bash
alembic revision --autogenerate -m "add_a1_planejamento_module"
alembic upgrade head
```

#### 9. Escrever Testes
```python
# agricola/a1_planejamento/tests/test_services.py
async def test_criar_safra_sucesso():
    pass

async def test_tenant_isolation():
    pass
```

#### 10. Atualizar Documentação
Editar `agricola/a1_planejamento/README.md` com funcionalidades reais

## 📅 Cronograma de Execução

### Fase 1: Infraestrutura Base (✅ Concluído - 1 dia)
- [x] Criar `core/constants.py`
- [x] Melhorar feature gates em `core/dependencies.py`
- [x] Criar script gerador de módulos
- [x] Documentar template padrão

### Fase 2: Módulos Agrícolas (Estimativa: 2 semanas)
- [ ] A1_PLANEJAMENTO (3 dias)
- [ ] A2_CAMPO (4 dias)
- [ ] A3_DEFENSIVOS (2 dias)
- [ ] A4_PRECISAO (3 dias)
- [ ] A5_COLHEITA (3 dias)

### Fase 3: Módulos Pecuária (Estimativa: 1.5 semanas)
- [ ] P1_REBANHO (3 dias)
- [ ] P2_GENETICA (2 dias)
- [ ] P3_CONFINAMENTO (2 dias)
- [ ] P4_LEITE (2 dias)

### Fase 4: Módulos Financeiro (Estimativa: 2 semanas)
- [ ] F1_TESOURARIA (3 dias)
- [ ] F2_CUSTOS_ABC (4 dias)
- [ ] F3_FISCAL (4 dias)
- [ ] F4_HEDGING (3 dias)

### Fase 5: Módulos Operacional (Estimativa: 1 semana)
- [ ] O1_FROTA (2 dias)
- [ ] O2_ESTOQUE (3 dias)
- [ ] O3_COMPRAS (2 dias)

### Fase 6: Migração de Dados (Estimativa: 1 semana)
- [ ] Criar scripts de migração
- [ ] Migrar dados existentes para nova estrutura
- [ ] Validar integridade

### Fase 7: Testes e Validação (Estimativa: 1 semana)
- [ ] Testes de integração entre módulos
- [ ] Testes de tenant isolation
- [ ] Testes de feature gates
- [ ] Testes de performance

**Total estimado:** 8-9 semanas

## 🎨 Exemplo de Uso - Planos Customizados

Com a modularização, clientes podem montar pacotes personalizados:

### Plano "Fazenda Essencial"
```python
modulos = [
    Modulos.CORE,
    Modulos.AGRICOLA_PLANEJAMENTO,
    Modulos.AGRICOLA_CAMPO,
    Modulos.OPERACIONAL_ESTOQUE,
    Modulos.FINANCEIRO_TESOURARIA,
]
# Preço: R$ 896/mês
```

### Plano "Pecuária Completa"
```python
modulos = [
    Modulos.CORE,
    Modulos.PECUARIA_REBANHO,
    Modulos.PECUARIA_GENETICA,
    Modulos.PECUARIA_CONFINAMENTO,
    Modulos.FINANCEIRO_TESOURARIA,
    Modulos.OPERACIONAL_FROTA,
]
# Preço: R$ 1.575/mês
```

### Plano "Grãos Premium"
```python
modulos = [
    Modulos.CORE,
    Modulos.AGRICOLA_PLANEJAMENTO,
    Modulos.AGRICOLA_CAMPO,
    Modulos.AGRICOLA_DEFENSIVOS,
    Modulos.AGRICOLA_PRECISAO,
    Modulos.AGRICOLA_COLHEITA,
    Modulos.FINANCEIRO_TESOURARIA,
    Modulos.FINANCEIRO_CUSTOS_ABC,
    Modulos.FINANCEIRO_HEDGING,
    Modulos.OPERACIONAL_ESTOQUE,
]
# Preço: R$ 2.692/mês
```

## 🔒 Segurança e Multi-tenancy

### Validações Obrigatórias

Todo módulo **DEVE**:

1. **Filtrar por tenant_id em TODAS as queries**
```python
stmt = select(Safra).where(
    and_(
        Safra.tenant_id == self.tenant_id,
        Safra.id == safra_id
    )
)
```

2. **Proteger rotas com feature gates**
```python
@router.get("/", dependencies=[Depends(require_module(Modulos.XXX))])
```

3. **Validar dependências de módulos**
```python
# Se A3_DEFENSIVOS depende de A2_CAMPO
# Validar no service ou criar require_all_modules
```

### Testes de Segurança Obrigatórios

Cada módulo deve ter testes de:
- **Tenant Isolation**: Tenant A não vê dados do Tenant B
- **Feature Gate**: Tenant sem módulo recebe 402
- **Dependências**: Módulos dependentes funcionam juntos

## 📊 Métricas de Sucesso

### KPIs Técnicos
- [ ] 100% dos endpoints com feature gates
- [ ] 100% dos models com tenant_id
- [ ] Cobertura de testes ≥ 80%
- [ ] 0 queries sem filtro de tenant
- [ ] Documentação completa de todos os módulos

### KPIs de Negócio
- [ ] Permitir venda à la carte de módulos
- [ ] Tempo de onboarding de novo dev < 2 dias
- [ ] Criar 5+ pacotes pré-definidos no backoffice
- [ ] Implementar telemetria de uso por módulo

## 🆘 Suporte e Dúvidas

### Documentos de Referência
- [Template de Módulo](./architecture/MODULO_TEMPLATE.md)
- [Manual de Desenvolvimento](./architecture/AgroSaaS-Manual.md)
- [Requisitos Funcionais](./functional_requirements/funtionals.md)

### Comandos Úteis

```bash
# Criar novo módulo
python scripts/create_module.py --modulo XXX --dominio YYY

# Executar testes de um módulo
pytest agricola/a1_planejamento/tests/ -v

# Verificar cobertura
pytest --cov=agricola/a1_planejamento --cov-report=html

# Criar migration
alembic revision --autogenerate -m "mensagem"

# Aplicar migrations
alembic upgrade head
```

## 📝 Checklist de Conclusão

### Módulo Concluído Quando:
- [ ] Todos os arquivos criados (router, models, schemas, services)
- [ ] Feature gates aplicados em todas as rotas
- [ ] Models com tenant_id e indexes
- [ ] Services com validação de tenant
- [ ] Schemas com validações Pydantic
- [ ] Testes ≥ 80% cobertura
- [ ] README.md documentado
- [ ] Migration criada e aplicada
- [ ] Registrado no main.py
- [ ] Code review aprovado

---

**Última atualização:** 2026-03-10
**Versão do Documento:** 1.0
