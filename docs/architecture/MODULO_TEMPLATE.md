# Template de Estrutura de Módulo AgroSaaS

Este documento define a estrutura padrão que **TODOS** os módulos devem seguir.

## 📁 Estrutura de Diretórios

```
services/api/{dominio}/{modulo_id}/
├── __init__.py              # Exports principais do módulo
├── router.py                # FastAPI router (rotas HTTP)
├── models.py                # SQLAlchemy models (entidades de banco)
├── schemas.py               # Pydantic schemas (input/output)
├── services.py              # Lógica de negócio
├── dependencies.py          # Dependencies específicas (opcional)
├── exceptions.py            # Exceções customizadas (opcional)
└── README.md                # Documentação do módulo
```

## 📋 Exemplo Completo: Módulo A1 - Planejamento de Safra

### `__init__.py`
```python
"""
Módulo A1 - Planejamento de Safra e Orçamento
ID: A1_PLANEJAMENTO
Categoria: AGRICOLA
"""

from .router import router
from .models import Safra, OrcamentoSafra
from .schemas import SafraCreate, SafraResponse

__all__ = [
    "router",
    "Safra",
    "OrcamentoSafra",
    "SafraCreate",
    "SafraResponse",
]
```

### `models.py`
```python
"""
Models do módulo A1 - Planejamento de Safra.
Todas as entidades relacionadas a safras e orçamentos.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base


class Safra(Base):
    """
    Safra agrícola - Ciclo de plantio completo.

    Escopo: A1_PLANEJAMENTO
    Multi-tenancy: sim (tenant_id obrigatório)
    """
    __tablename__ = "safras"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    nome: Mapped[str] = mapped_column(String(100), nullable=False)  # Ex: "Soja 2025/26"
    cultura: Mapped[str] = mapped_column(String(50), nullable=False)  # Ex: "Soja", "Milho"
    ciclo: Mapped[str] = mapped_column(String(30), nullable=False)  # PRINCIPAL, SAFRINHA, PERENE

    data_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_fim_prevista: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    hectares_planejados: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    producao_esperada_sc: Mapped[float | None] = mapped_column(Numeric(12, 2))  # Sacas

    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class OrcamentoSafra(Base):
    """
    Orçamento previsto vs realizado de uma safra.

    Escopo: A1_PLANEJAMENTO
    """
    __tablename__ = "orcamentos_safra"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    safra_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("safras.id", ondelete="CASCADE"), nullable=False)

    custo_total_previsto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    custo_por_hectare_previsto: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    receita_esperada: Mapped[float | None] = mapped_column(Numeric(12, 2))
    margem_esperada: Mapped[float | None] = mapped_column(Numeric(12, 2))

    observacoes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

### `schemas.py`
```python
"""
Schemas Pydantic do módulo A1 - Planejamento de Safra.
Separados em *Create (input), *Update (input), *Response (output).
"""
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional


# ==================== INPUT SCHEMAS ====================

class SafraCreate(BaseModel):
    """Schema para criação de nova safra."""
    nome: str = Field(..., min_length=3, max_length=100, description="Nome da safra")
    cultura: str = Field(..., min_length=2, max_length=50, description="Cultura plantada")
    ciclo: str = Field(..., description="Tipo de ciclo")
    data_inicio: datetime
    data_fim_prevista: Optional[datetime] = None
    hectares_planejados: float = Field(..., gt=0, description="Hectares a plantar")
    producao_esperada_sc: Optional[float] = Field(None, ge=0)

    @field_validator("ciclo")
    @classmethod
    def validar_ciclo(cls, v: str) -> str:
        validos = ["PRINCIPAL", "SAFRINHA", "PERENE"]
        if v.upper() not in validos:
            raise ValueError(f"Ciclo deve ser um de: {validos}")
        return v.upper()


class SafraUpdate(BaseModel):
    """Schema para atualização de safra."""
    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    data_fim_prevista: Optional[datetime] = None
    hectares_planejados: Optional[float] = Field(None, gt=0)
    producao_esperada_sc: Optional[float] = Field(None, ge=0)
    ativo: Optional[bool] = None


class OrcamentoSafraCreate(BaseModel):
    """Schema para criação de orçamento."""
    safra_id: UUID
    custo_total_previsto: float = Field(..., gt=0)
    custo_por_hectare_previsto: float = Field(..., gt=0)
    receita_esperada: Optional[float] = Field(None, ge=0)
    margem_esperada: Optional[float] = None
    observacoes: Optional[str] = None


# ==================== OUTPUT SCHEMAS ====================

class SafraResponse(BaseModel):
    """Schema de resposta de safra."""
    id: UUID
    tenant_id: UUID
    nome: str
    cultura: str
    ciclo: str
    data_inicio: datetime
    data_fim_prevista: Optional[datetime]
    hectares_planejados: float
    producao_esperada_sc: Optional[float]
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrcamentoSafraResponse(BaseModel):
    """Schema de resposta de orçamento."""
    id: UUID
    tenant_id: UUID
    safra_id: UUID
    custo_total_previsto: float
    custo_por_hectare_previsto: float
    receita_esperada: Optional[float]
    margem_esperada: Optional[float]
    observacoes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
```

### `services.py`
```python
"""
Services do módulo A1 - Planejamento de Safra.
Lógica de negócio isolada, testável, reutilizável.
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional

from .models import Safra, OrcamentoSafra
from .schemas import SafraCreate, SafraUpdate, OrcamentoSafraCreate
from core.exceptions import EntityNotFoundError, BusinessRuleError


class SafraService:
    """
    Service para gestão de safras.
    Responsabilidade única: operações sobre Safra e OrcamentoSafra.
    """

    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def criar_safra(self, dados: SafraCreate) -> Safra:
        """Cria nova safra com validações de negócio."""

        # Regra de negócio: não permitir safras com mesmo nome no tenant
        stmt = select(Safra).where(
            and_(
                Safra.tenant_id == self.tenant_id,
                Safra.nome == dados.nome,
                Safra.ativo == True
            )
        )
        resultado = await self.session.execute(stmt)
        safra_existente = resultado.scalar_one_or_none()

        if safra_existente:
            raise BusinessRuleError(f"Já existe uma safra ativa com o nome '{dados.nome}'")

        # Criar safra
        safra = Safra(
            tenant_id=self.tenant_id,
            **dados.model_dump()
        )

        self.session.add(safra)
        await self.session.commit()
        await self.session.refresh(safra)

        return safra

    async def listar_safras(
        self,
        apenas_ativas: bool = True,
        cultura: Optional[str] = None
    ) -> List[Safra]:
        """Lista safras do tenant com filtros opcionais."""

        stmt = select(Safra).where(Safra.tenant_id == self.tenant_id)

        if apenas_ativas:
            stmt = stmt.where(Safra.ativo == True)

        if cultura:
            stmt = stmt.where(Safra.cultura == cultura)

        stmt = stmt.order_by(Safra.data_inicio.desc())

        resultado = await self.session.execute(stmt)
        return list(resultado.scalars().all())

    async def buscar_safra(self, safra_id: UUID) -> Safra:
        """Busca safra por ID com validação de tenant."""

        stmt = select(Safra).where(
            and_(
                Safra.id == safra_id,
                Safra.tenant_id == self.tenant_id
            )
        )
        resultado = await self.session.execute(stmt)
        safra = resultado.scalar_one_or_none()

        if not safra:
            raise EntityNotFoundError(f"Safra {safra_id} não encontrada")

        return safra

    async def atualizar_safra(self, safra_id: UUID, dados: SafraUpdate) -> Safra:
        """Atualiza safra existente."""

        safra = await self.buscar_safra(safra_id)

        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(safra, campo, valor)

        await self.session.commit()
        await self.session.refresh(safra)

        return safra
```

### `router.py`
```python
"""
Router do módulo A1 - Planejamento de Safra.
Endpoints HTTP com feature gate aplicado.
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional

from core.dependencies import get_session, get_tenant_id, require_module
from core.constants import Modulos

from .schemas import SafraCreate, SafraUpdate, SafraResponse, OrcamentoSafraCreate, OrcamentoSafraResponse
from .services import SafraService

# Router com prefixo e tags
router = APIRouter(
    prefix="/agricola/planejamento",
    tags=["Agrícola - Planejamento de Safra (A1)"]
)


@router.post(
    "/safras",
    response_model=SafraResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova safra",
    dependencies=[Depends(require_module(Modulos.AGRICOLA_PLANEJAMENTO))]  # Feature gate!
)
async def criar_safra(
    dados: SafraCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """
    Cria uma nova safra agrícola.

    **Requer módulo:** A1_PLANEJAMENTO

    Validações:
    - Nome não pode estar duplicado no tenant
    - Hectares deve ser > 0
    - Ciclo deve ser válido
    """
    service = SafraService(session, tenant_id)
    safra = await service.criar_safra(dados)
    return SafraResponse.model_validate(safra)


@router.get(
    "/safras",
    response_model=List[SafraResponse],
    summary="Listar safras",
    dependencies=[Depends(require_module(Modulos.AGRICOLA_PLANEJAMENTO))]
)
async def listar_safras(
    apenas_ativas: bool = Query(True, description="Filtrar apenas safras ativas"),
    cultura: Optional[str] = Query(None, description="Filtrar por cultura"),
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """
    Lista todas as safras do tenant.

    **Requer módulo:** A1_PLANEJAMENTO
    """
    service = SafraService(session, tenant_id)
    safras = await service.listar_safras(apenas_ativas, cultura)
    return [SafraResponse.model_validate(s) for s in safras]


@router.get(
    "/safras/{safra_id}",
    response_model=SafraResponse,
    summary="Buscar safra por ID",
    dependencies=[Depends(require_module(Modulos.AGRICOLA_PLANEJAMENTO))]
)
async def buscar_safra(
    safra_id: UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Retorna detalhes de uma safra específica."""
    service = SafraService(session, tenant_id)
    safra = await service.buscar_safra(safra_id)
    return SafraResponse.model_validate(safra)


@router.patch(
    "/safras/{safra_id}",
    response_model=SafraResponse,
    summary="Atualizar safra",
    dependencies=[Depends(require_module(Modulos.AGRICOLA_PLANEJAMENTO))]
)
async def atualizar_safra(
    safra_id: UUID,
    dados: SafraUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Atualiza informações de uma safra."""
    service = SafraService(session, tenant_id)
    safra = await service.atualizar_safra(safra_id, dados)
    return SafraResponse.model_validate(safra)
```

### `README.md`
```markdown
# Módulo A1 - Planejamento de Safra e Orçamento

**ID:** `A1_PLANEJAMENTO`
**Categoria:** AGRICOLA
**Status:** Ativo
**Preço Base:** R$ 199,00/mês

## Descrição

Módulo para gestão de ciclos agrícolas, orçado vs realizado, e rotação de culturas.

## Funcionalidades

- ✅ Cadastro de safras (PRINCIPAL, SAFRINHA, PERENE)
- ✅ Orçamento de custos por hectare
- ✅ Projeção de receita e margem
- ✅ Histórico de safras anteriores
- 🔄 Rotação de culturas (em desenvolvimento)
- 🔄 Integração com módulo de custos (F2)

## Dependências

- **CORE** (obrigatório)

## Integrações

Este módulo se integra com:
- **A2_CAMPO** - Operações planejadas viram ordens de serviço
- **A5_COLHEITA** - Comparação realizado vs planejado
- **F2_CUSTOS_ABC** - Rateio de custos por safra

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/agricola/planejamento/safras` | Criar safra |
| GET | `/agricola/planejamento/safras` | Listar safras |
| GET | `/agricola/planejamento/safras/{id}` | Buscar safra |
| PATCH | `/agricola/planejamento/safras/{id}` | Atualizar safra |

## Modelos de Dados

### Safra
- id (UUID)
- tenant_id (UUID) - Multi-tenancy
- nome (string)
- cultura (string)
- ciclo (PRINCIPAL | SAFRINHA | PERENE)
- hectares_planejados (decimal)
- producao_esperada_sc (decimal)

### OrcamentoSafra
- id (UUID)
- safra_id (UUID)
- custo_total_previsto (decimal)
- custo_por_hectare_previsto (decimal)
- receita_esperada (decimal)
- margem_esperada (decimal)

## Como Usar

```python
# No main.py
from agricola.a1_planejamento.router import router as router_planejamento_safra

app.include_router(router_planejamento_safra, prefix="/api/v1")
```

## Testes

```bash
cd services/api
pytest agricola/a1_planejamento/tests/ -v
```

## Changelog

### v1.0.0 (2026-03-10)
- ✅ Implementação inicial
- ✅ CRUD de safras
- ✅ Orçamentos básicos
```
