# Plano de Ação — Integração Completa do Fluxo de Colheita

**Data:** 2026-03-30
**Escopo:** Resolver silos de dados entre Agricola, Financeiro, Operacional e Core Cadastros
**Meta:** Fluxo colheita 100% integrado (operação → despesa → estoque → receita)

---

## FASE 0 — Preparação (Migrations & Schemas)

### Tarefa 0.1: Adicionar FKs em Despesa e Receita

**Objetivo:** Rastreabilidade de origem (qual operação/romaneio gerou qual transação)

**Arquivos a modificar:**
- `services/api/alembic/versions/[next]_add_origin_fk_despesa_receita.py` (nova migration)
- `services/api/financeiro/models/despesa.py`
- `services/api/financeiro/models/receita.py`
- `services/api/financeiro/schemas/despesa.py`
- `services/api/financeiro/schemas/receita.py`

**Implementação:**

```sql
-- Migration (Alembic)
ALTER TABLE fin_despesas ADD COLUMN operacao_id UUID REFERENCES operacoes_agricolas(id) ON DELETE SET NULL;
CREATE INDEX idx_despesas_operacao_id ON fin_despesas(operacao_id);

ALTER TABLE fin_receitas ADD COLUMN romaneio_id UUID REFERENCES romaneios_colheita(id) ON DELETE SET NULL;
CREATE INDEX idx_receitas_romaneio_id ON fin_receitas(romaneio_id);
```

```python
# financeiro/models/despesa.py
class Despesa(Base):
    ...
    operacao_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("operacoes_agricolas.id", ondelete="SET NULL"),
        nullable=True,
        comment="Referência para rastreabilidade (operação que gerou)"
    )

# financeiro/models/receita.py
class Receita(Base):
    ...
    romaneio_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("romaneios_colheita.id", ondelete="SET NULL"),
        nullable=True,
        comment="Referência para rastreabilidade (romaneio de venda)"
    )
```

**Schemas:**
```python
# financeiro/schemas/despesa.py
class DespesaCreate(BaseModel):
    ...
    operacao_id: UUID | None = None

class DespesaResponse(BaseModel):
    ...
    operacao_id: UUID | None = None

# (similar para receita)
```

**Complexidade:** 🟢 Baixa (migration simples)
**Tempo:** 30 min
**Dependências:** Nenhuma

---

### Tarefa 0.2: Criar Lookup Table — Operação Tipo × Fases Permitidas

**Objetivo:** Validação de RN (operação só em fases permitidas)

**Arquivos:**
- `services/api/alembic/versions/[next]_create_operacao_tipo_fase_lookup.py`
- `services/api/agricola/models/operacao_tipo_fase.py` (novo)

**Implementação:**

```sql
-- Migration
CREATE TABLE agricola_operacao_tipo_fase (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo_operacao VARCHAR(30) NOT NULL UNIQUE,
    fases_permitidas VARCHAR(30)[] NOT NULL,
    descricao TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO agricola_operacao_tipo_fase (tipo_operacao, fases_permitidas, descricao) VALUES
('PLANTIO', ARRAY['PLANTIO', 'DESENVOLVIMENTO'], 'Semeadura e plantio'),
('ADUBAÇÃO', ARRAY['PREPARO_SOLO', 'DESENVOLVIMENTO'], 'Adubação de cobertura'),
('PULVERIZAÇÃO', ARRAY['DESENVOLVIMENTO', 'COLHEITA'], 'Aplicação de defensivos'),
('COLHEITA', ARRAY['COLHEITA'], 'Colheita manual ou mecanizada'),
('OPERAÇÃO_MECANIZADA', ARRAY['PLANTIO', 'DESENVOLVIMENTO'], 'Operações de máquina');
```

```python
# agricola/models/operacao_tipo_fase.py (novo arquivo)
class OperacaoTipoFase(Base):
    __tablename__ = "agricola_operacao_tipo_fase"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo_operacao: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    fases_permitidas: Mapped[list[str]] = mapped_column(JSON, nullable=False)  # ["PLANTIO", "DESENVOLVIMENTO"]
    descricao: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
```

**Complexidade:** 🟢 Baixa
**Tempo:** 45 min
**Dependências:** Nenhuma

---

## FASE 1 — Validações de Regra de Negócio

### Tarefa 1.1: Validar Operação + Fase Safra

**Objetivo:** Impedir que operação seja registrada em fase inválida

**Arquivos a modificar:**
- `services/api/agricola/operacoes/service.py`
- `services/api/agricola/operacoes/router.py`
- `services/api/tests/test_operacoes.py` (novo)

**Implementação:**

```python
# agricola/operacoes/service.py
class OperacaoAgricolaService(BaseService[OperacaoAgricola]):
    async def criar(self, dados: OperacaoAgricolaCreate) -> OperacaoAgricola:
        # 1. Verificar safra existe e tenant isolation
        safra = await self.session.execute(
            select(Safra).where(
                Safra.id == dados.safra_id,
                Safra.tenant_id == self.tenant_id
            )
        )
        safra = safra.scalars().first()
        if not safra:
            raise EntityNotFoundError("Safra não encontrada")

        # 2. Buscar tipos permitidos para o tipo desta operação
        tipo_fase = await self.session.execute(
            select(OperacaoTipoFase).where(
                OperacaoTipoFase.tipo_operacao == dados.tipo
            )
        )
        tipo_fase = tipo_fase.scalars().first()

        if not tipo_fase:
            raise BusinessRuleError(f"Tipo de operação '{dados.tipo}' não está cadastrado")

        # 3. Validar se fase atual da safra está permitida
        if safra.status not in tipo_fase.fases_permitidas:
            raise BusinessRuleError(
                f"Operação '{dados.tipo}' não é permitida na fase '{safra.status}'. "
                f"Fases permitidas: {', '.join(tipo_fase.fases_permitidas)}"
            )

        # 4. Registrar snapshot da fase
        dados_dict = dados.model_dump()
        dados_dict['fase_safra'] = safra.status

        # 5. Criar operação
        operacao = await super().create(dados_dict)
        return operacao
```

**Testes:**

```python
# tests/test_operacoes_validacao.py (novo arquivo)
@pytest.mark.asyncio
async def test_operacao_invalida_na_fase():
    """Operação PLANTIO não deve ser permitida em COLHEITA"""
    safra = await criar_safra_teste(status="COLHEITA")

    with pytest.raises(BusinessRuleError, match="não é permitida na fase"):
        await criar_operacao(tipo="PLANTIO", safra_id=safra.id)

@pytest.mark.asyncio
async def test_operacao_valida_na_fase():
    """Operação COLHEITA deve ser permitida em COLHEITA"""
    safra = await criar_safra_teste(status="COLHEITA")

    operacao = await criar_operacao(tipo="COLHEITA", safra_id=safra.id)
    assert operacao.fase_safra == "COLHEITA"

@pytest.mark.asyncio
async def test_tenant_isolation_operacao():
    """Operação de outro tenant não deveria ser acessível"""
    safra_outro_tenant = await criar_safra_teste(tenant_id=outro_tenant_id)

    with pytest.raises(EntityNotFoundError):
        await criar_operacao(safra_id=safra_outro_tenant.id)
```

**Complexidade:** 🟡 Média
**Tempo:** 1.5h (código + testes)
**Dependências:** ✅ Tarefa 0.2 (lookup table)

---

### Tarefa 1.2: Validar Data da Operação (não pode ser futura)

**Objetivo:** Evitar operações com data futura

**Arquivos a modificar:**
- `services/api/agricola/operacoes/service.py` (adicionar em `criar()`)
- `services/api/tests/test_operacoes.py` (adicionar teste)

**Implementação:**

```python
# agricola/operacoes/service.py
async def criar(self, dados: OperacaoAgricolaCreate) -> OperacaoAgricola:
    # ... validações anteriores ...

    # Validar data não é futura
    if dados.data_realizada > date.today():
        raise BusinessRuleError("Data da operação não pode ser futura")

    # ... resto do código ...
```

**Complexidade:** 🟢 Baixa
**Tempo:** 30 min
**Dependências:** Tarefa 1.1

---

## FASE 2 — Integrações com Financeiro

### Tarefa 2.1: Webhook — Operação → Despesa Automática

**Objetivo:** Quando operação é criada, criar despesa associada automaticamente

**Arquivos a modificar/criar:**
- `services/api/agricola/operacoes/service.py` (adicionar hook pós-criação)
- `services/api/financeiro/services/despesa_service.py` (adicionar método auxiliar)
- `services/api/tests/test_operacao_despesa_webhook.py` (novo)

**Implementação:**

```python
# agricola/operacoes/service.py
from financeiro.services.despesa_service import DespesaService
from financeiro.schemas.despesa import DespesaCreate

class OperacaoAgricolaService(BaseService[OperacaoAgricola]):
    async def criar(self, dados: OperacaoAgricolaCreate) -> OperacaoAgricola:
        # ... validações ...

        # Criar operação
        operacao = await super().create(dados_dict)

        # 🔥 WEBHOOK: Criar despesa automaticamente
        await self._criar_despesa_da_operacao(operacao)

        return operacao

    async def _criar_despesa_da_operacao(self, operacao: OperacaoAgricola) -> None:
        """Cria Despesa automaticamente para a operação"""
        if operacao.custo_total <= 0:
            # Se não há custo, não cria despesa
            return

        # Determinar categoria de custo (PlanoConta)
        categoria_map = {
            "PLANTIO": "Serviço de Plantio",
            "COLHEITA": "Serviço de Colheita",
            "PULVERIZAÇÃO": "Aplicação de Defensivos",
            "ADUBAÇÃO": "Adubação"
        }
        categoria = categoria_map.get(operacao.tipo, "Operação Agrícola")

        # Criar despesa
        despesa_service = DespesaService(self.session, self.tenant_id)
        despesa_create = DespesaCreate(
            descricao=f"{categoria} - Safra {operacao.safra_id.hex[:8]} / Talhão {operacao.talhao_id.hex[:8]}",
            valor=operacao.custo_total,
            data_operacao=operacao.data_realizada,
            categoria="Operações Agrícolas",
            operacao_id=operacao.id,  # ← RASTREABILIDADE
            status="PENDENTE"
        )

        try:
            await despesa_service.create(despesa_create.model_dump())
            logger.info(f"Despesa criada automaticamente para operação {operacao.id}")
        except Exception as e:
            logger.error(f"Erro ao criar despesa para operação {operacao.id}: {e}")
            # NÃO falha a operação se despesa falhar (falha silenciosa, mas logada)
```

**Testes:**

```python
# tests/test_operacao_despesa_webhook.py (novo arquivo)
@pytest.mark.asyncio
async def test_operacao_com_custo_cria_despesa():
    """Criar operação com custo_total > 0 deve criar Despesa automaticamente"""
    safra = await criar_safra_teste()

    operacao = await criar_operacao(
        tipo="COLHEITA",
        safra_id=safra.id,
        custo_total=5000
    )

    # Verificar despesa foi criada
    despesa = await session.execute(
        select(Despesa).where(Despesa.operacao_id == operacao.id)
    )
    despesa = despesa.scalars().first()

    assert despesa is not None
    assert despesa.valor == 5000
    assert "Colheita" in despesa.descricao

@pytest.mark.asyncio
async def test_operacao_sem_custo_nao_cria_despesa():
    """Operação com custo_total = 0 não deve criar Despesa"""
    safra = await criar_safra_teste()

    operacao = await criar_operacao(
        tipo="PLANTIO",
        safra_id=safra.id,
        custo_total=0
    )

    despesa = await session.execute(
        select(Despesa).where(Despesa.operacao_id == operacao.id)
    )
    despesa = despesa.scalars().first()

    assert despesa is None

@pytest.mark.asyncio
async def test_despesa_rastreabilidade():
    """Despesa deve ter referência para operação"""
    operacao = await criar_operacao(custo_total=1000)

    # Buscar receita por operacao_id
    despesa = await session.execute(
        select(Despesa).where(Despesa.operacao_id == operacao.id)
    )
    despesa = despesa.scalars().first()

    assert despesa.operacao_id == operacao.id
```

**Complexidade:** 🟡 Média
**Tempo:** 2h
**Dependências:** ✅ Tarefa 0.1 (FK em Despesa)

---

### Tarefa 2.2: Webhook — Romaneio → Receita Automática

**Objetivo:** Quando romaneio é criado, criar receita associada automaticamente

**Arquivos a modificar/criar:**
- `services/api/agricola/romaneios/service.py`
- `services/api/financeiro/services/receita_service.py` (adicionar método auxiliar)
- `services/api/tests/test_romaneio_receita_webhook.py` (novo)

**Implementação:**

```python
# agricola/romaneios/service.py
from financeiro.services.receita_service import ReceitaService
from financeiro.schemas.receita import ReceitaCreate

class RomaneioColheitaService(BaseService[RomaneioColheita]):
    async def criar(self, dados: RomaneioColheitaCreate) -> RomaneioColheita:
        # ... validações ...

        # Criar romaneio
        romaneio = await super().create(dados_dict)

        # 🔥 WEBHOOK: Criar receita automaticamente
        await self._criar_receita_do_romaneio(romaneio)

        return romaneio

    async def _criar_receita_do_romaneio(self, romaneio: RomaneioColheita) -> None:
        """Cria Receita automaticamente para o romaneio"""
        if not romaneio.preco_saca or romaneio.receita_total <= 0:
            # Se não há valor, não cria receita
            return

        receita_service = ReceitaService(self.session, self.tenant_id)
        receita_create = ReceitaCreate(
            descricao=f"Venda de colheita - Safra {romaneio.safra_id.hex[:8]} ({romaneio.sacas_60kg} sacas)",
            valor=romaneio.receita_total,
            data_operacao=romaneio.data_colheita,
            cliente="Comprador/Armazém",  # Customizável depois
            romaneio_id=romaneio.id,  # ← RASTREABILIDADE
            status="ABERTO"
        )

        try:
            await receita_service.create(receita_create.model_dump())
            logger.info(f"Receita criada automaticamente para romaneio {romaneio.id}")
        except Exception as e:
            logger.error(f"Erro ao criar receita para romaneio {romaneio.id}: {e}")
```

**Testes:** Similar ao 2.1

**Complexidade:** 🟡 Média
**Tempo:** 2h
**Dependências:** ✅ Tarefa 0.1 (FK em Receita)

---

## FASE 3 — Integrações com Estoque

### Tarefa 3.1: Desconto Automático de Insumo → Estoque

**Objetivo:** Quando insumo é adicionado a operação, descontar automaticamente do estoque

**Arquivos a modificar/criar:**
- `services/api/agricola/operacoes/service.py` (adicionar hook em criar insumo)
- `services/api/operacional/estoque/service.py` (novo método: descontar)
- `services/api/tests/test_insumo_estoque_webhook.py` (novo)

**Implementação:**

```python
# agricola/operacoes/service.py
from operacional.estoque.service import EstoqueService

class InsumoOperacaoService(BaseService[InsumoOperacao]):
    async def criar(self, dados: InsumoOperacaoCreate) -> InsumoOperacao:
        # 1. Validar insumo existe
        insumo = await self.session.execute(
            select(Produto).where(
                Produto.id == dados.insumo_id,
                Produto.tenant_id == self.tenant_id
            )
        )
        insumo = insumo.scalars().first()
        if not insumo:
            raise EntityNotFoundError("Insumo não encontrado")

        # 2. Criar InsumoOperacao
        insumo_op = await super().create(dados.model_dump())

        # 3. 🔥 WEBHOOK: Descontar do estoque
        await self._descontar_estoque(insumo_op)

        return insumo_op

    async def _descontar_estoque(self, insumo_op: InsumoOperacao) -> None:
        """Desconta insumo do estoque usando FIFO"""
        estoque_service = EstoqueService(self.session, self.tenant_id)

        try:
            await estoque_service.descontar_lote(
                produto_id=insumo_op.insumo_id,
                quantidade=insumo_op.quantidade_total,
                unidade=insumo_op.unidade,
                referencia_id=insumo_op.id,
                referencia_tipo="OPERACAO"
            )
            logger.info(f"Estoque descontado para insumo {insumo_op.id}")
        except Exception as e:
            # Falha crítica: se não pode descontar, rolback da operação
            raise BusinessRuleError(f"Erro ao descontar estoque: {str(e)}")
```

```python
# operacional/estoque/service.py
class EstoqueService(BaseService[SaldoEstoque]):
    async def descontar_lote(
        self,
        produto_id: UUID,
        quantidade: float,
        unidade: str,
        referencia_id: UUID,
        referencia_tipo: str  # "OPERACAO", "VENDA", etc
    ) -> None:
        """
        Desconta quantidade do estoque usando FIFO (First In, First Out).

        Procura por lotes válidos (não vencidos) e desconta sequencialmente.
        Registra MovimentacaoEstoque para rastreabilidade.
        """
        # 1. Buscar lotes válidos, ordenado por data_fabricacao (FIFO)
        lotes = await self.session.execute(
            select(LoteEstoque).filter(
                LoteEstoque.produto_id == produto_id,
                LoteEstoque.quantidade_atual > 0,
                (LoteEstoque.data_validade.is_(None) | (LoteEstoque.data_validade >= date.today()))
            ).order_by(LoteEstoque.data_fabricacao.asc())
        )
        lotes = list(lotes.scalars().all())

        if not lotes:
            raise BusinessRuleError(f"Sem lotes válidos disponíveis para produto {produto_id}")

        # 2. Descontar sequencialmente (FIFO)
        quantidade_faltante = quantidade

        for lote in lotes:
            if quantidade_faltante <= 0:
                break

            quantidade_a_descontar = min(lote.quantidade_atual, quantidade_faltante)

            # Atualizar lote
            lote.quantidade_atual -= quantidade_a_descontar
            self.session.add(lote)

            # Registrar movimentação
            movimentacao = MovimentacaoEstoque(
                lote_id=lote.id,
                produto_id=produto_id,
                tipo_movimento="SAÍDA",
                quantidade=quantidade_a_descontar,
                unidade=unidade,
                referencia_id=referencia_id,
                referencia_tipo=referencia_tipo,
                motivo=f"Operação agrícola ({referencia_tipo})"
            )
            self.session.add(movimentacao)

            quantidade_faltante -= quantidade_a_descontar

        # 3. Se ainda faltando, erro
        if quantidade_faltante > 0:
            raise BusinessRuleError(
                f"Quantidade insuficiente. Faltam {quantidade_faltante} {unidade}"
            )

        await self.session.commit()
```

**Testes:**

```python
# tests/test_insumo_estoque_webhook.py (novo arquivo)
@pytest.mark.asyncio
async def test_insumo_desconta_estoque_fifo():
    """Criar insumo deve descontar do estoque (FIFO)"""
    lote1 = criar_lote_estoque(quantidade=100, data_fab="2026-01-01")
    lote2 = criar_lote_estoque(quantidade=50, data_fab="2026-02-01")

    # Descontar 80 unidades
    await criar_insumo_operacao(quantidade=80)

    # Lote1 deve ter 20 (100 - 80)
    # Lote2 deve ter 50 (intacto)
    assert lote1.quantidade_atual == 20
    assert lote2.quantidade_atual == 50

@pytest.mark.asyncio
async def test_insumo_insuficiente_raises_erro():
    """Criar insumo com quantidade > estoque deve falhar"""
    lote = criar_lote_estoque(quantidade=50)

    with pytest.raises(BusinessRuleError, match="Quantidade insuficiente"):
        await criar_insumo_operacao(quantidade=100)
```

**Complexidade:** 🟡 Média
**Tempo:** 2.5h
**Dependências:** Nenhuma (novo feature)

---

## FASE 4 — Dashboard e Agregação

### Tarefa 4.1: View de Agregação Safra (Custo + Receita)

**Objetivo:** Dashboard com resumo financeiro completo da safra

**Arquivos a criar/modificar:**
- `services/api/agricola/dashboard/service.py` (adicionar novo endpoint)
- `services/api/agricola/dashboard/router.py` (novo endpoint)
- `services/api/agricola/dashboard/schemas.py` (novo schema)

**Implementação:**

```python
# agricola/dashboard/schemas.py (adicionar)
from pydantic import BaseModel

class SafraFinanceiroResumo(BaseModel):
    safra_id: UUID
    safra_status: str

    # Operações
    total_operacoes: int
    custo_operacoes_total: float
    tempo_total_h: float

    # Romaneios
    total_romaneios: int
    total_sacas: float
    receita_total: float
    produtividade_sc_ha: float | None

    # Financeiro
    despesa_total: float  # De Despesa WHERE operacao_id IS NOT NULL
    receita_total: float  # De Receita WHERE romaneio_id IS NOT NULL
    lucro_bruto: float
    roi_pct: float

class SafraResumoCompleto(BaseModel):
    id: UUID
    nome: str
    cultura: str
    ano_safra: int
    status: str
    area_ha: float

    financeiro: SafraFinanceiroResumo
    operacoes: list[Dict]  # Operações resumidas
    romaneios: list[Dict]  # Romaneios resumidos
```

```python
# agricola/dashboard/service.py
class DashboardAgricolaService:
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def resumo_safra(self, safra_id: UUID) -> SafraResumoCompleto:
        """Resumo completo da safra com dados financeiros"""

        # 1. Buscar safra
        safra = await self.session.execute(
            select(Safra).where(
                Safra.id == safra_id,
                Safra.tenant_id == self.tenant_id
            )
        )
        safra = safra.scalars().first()
        if not safra:
            raise EntityNotFoundError("Safra não encontrada")

        # 2. Buscar operações
        operacoes = await self.session.execute(
            select(OperacaoAgricola).where(
                OperacaoAgricola.safra_id == safra_id,
                OperacaoAgricola.tenant_id == self.tenant_id
            )
        )
        operacoes = list(operacoes.scalars().all())
        total_custo_op = sum(op.custo_total for op in operacoes)

        # 3. Buscar romaneios
        romaneios = await self.session.execute(
            select(RomaneioColheita).where(
                RomaneioColheita.safra_id == safra_id,
                RomaneioColheita.tenant_id == self.tenant_id
            )
        )
        romaneios = list(romaneios.scalars().all())
        total_receita_rom = sum(r.receita_total or 0 for r in romaneios)
        total_sacas = sum(r.sacas_60kg or 0 for r in romaneios)
        produtividade = (total_sacas / safra.area_ha) if safra.area_ha else 0

        # 4. Buscar despesas (de Despesa WHERE operacao_id IS NOT NULL)
        despesas = await self.session.execute(
            select(Despesa).where(
                Despesa.tenant_id == self.tenant_id,
                Despesa.operacao_id.in_(
                    select(OperacaoAgricola.id).where(
                        OperacaoAgricola.safra_id == safra_id
                    )
                )
            )
        )
        despesas = list(despesas.scalars().all())
        total_despesa = sum(d.valor for d in despesas)

        # 5. Buscar receitas (de Receita WHERE romaneio_id IS NOT NULL)
        receitas = await self.session.execute(
            select(Receita).where(
                Receita.tenant_id == self.tenant_id,
                Receita.romaneio_id.in_(
                    select(RomaneioColheita.id).where(
                        RomaneioColheita.safra_id == safra_id
                    )
                )
            )
        )
        receitas = list(receitas.scalars().all())
        total_receita_fin = sum(r.valor for r in receitas)

        # 6. Calcular métricas
        lucro_bruto = total_receita_fin - total_despesa
        roi_pct = (lucro_bruto / total_despesa * 100) if total_despesa > 0 else 0

        # 7. Montar resposta
        return SafraResumoCompleto(
            id=safra.id,
            nome=safra.nome,
            cultura=safra.cultura,
            ano_safra=safra.ano_safra,
            status=safra.status,
            area_ha=float(safra.area_ha) if safra.area_ha else 0,
            financeiro=SafraFinanceiroResumo(
                safra_id=safra.id,
                safra_status=safra.status,
                total_operacoes=len(operacoes),
                custo_operacoes_total=total_custo_op,
                tempo_total_h=0,  # TODO: calcular de operacoes
                total_romaneios=len(romaneios),
                total_sacas=total_sacas,
                receita_total=total_receita_rom,
                produtividade_sc_ha=produtividade,
                despesa_total=total_despesa,
                receita_total=total_receita_fin,
                lucro_bruto=lucro_bruto,
                roi_pct=roi_pct
            ),
            operacoes=[...],  # Simplificado
            romaneios=[...]   # Simplificado
        )
```

```python
# agricola/dashboard/router.py
@router.get("/safras/{safra_id}/resumo-financeiro", response_model=SafraResumoCompleto)
async def get_resumo_safra(
    safra_id: UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_tenant_permission("agricola:safras:view"))
):
    service = DashboardAgricolaService(session, tenant_id)
    return await service.resumo_safra(safra_id)
```

**Complexidade:** 🟡 Média
**Tempo:** 2h
**Dependências:** ✅ Tarefas 2.1, 2.2 (webhooks)

---

## FASE 5 — Frontend (UX)

### Tarefa 5.1: Adicionar Aba "Financeiro" em Detalhe de Safra

**Objetivo:** Mostrar resumo financeiro (custo, receita, ROI) na página de safra

**Arquivos a modificar:**
- `apps/web/src/app/(dashboard)/agricola/safras/[id]/page.tsx`
- `apps/web/src/components/agricola/safra-detail-financeiro.tsx` (novo)

**Implementação (pseudocódigo):**

```tsx
// apps/web/src/app/(dashboard)/agricola/safras/[id]/page.tsx
export default function SafraDetail() {
  const [tabActive, setTabActive] = useState('info')
  const { data: safra } = useSafra(safraId)
  const { data: resumo } = useQuery(
    ['safra', safraId, 'resumo-financeiro'],
    () => api.get(`/safras/${safraId}/resumo-financeiro`)
  )

  return (
    <Tabs value={tabActive} onValueChange={setTabActive}>
      <TabsList>
        <TabsTrigger value="info">Informações</TabsTrigger>
        <TabsTrigger value="operacoes">Operações ({safra?.operacoes_count})</TabsTrigger>
        <TabsTrigger value="romaneios">Romaneios ({safra?.romaneios_count})</TabsTrigger>
        <TabsTrigger value="financeiro">💰 Financeiro</TabsTrigger>
      </TabsList>

      <TabsContent value="financeiro">
        {resumo && <SafraDetailFinanceiro resumo={resumo} />}
      </TabsContent>
    </Tabs>
  )
}
```

```tsx
// apps/web/src/components/agricola/safra-detail-financeiro.tsx
export function SafraDetailFinanceiro({ resumo }: { resumo: SafraResumoCompleto }) {
  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Custo Total</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${formatCurrency(resumo.financeiro.despesa_total)}
            </div>
            <p className="text-xs text-muted-foreground">
              {resumo.financeiro.total_operacoes} operações
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Receita Total</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${formatCurrency(resumo.financeiro.receita_total)}
            </div>
            <p className="text-xs text-muted-foreground">
              {resumo.financeiro.total_sacas} sacas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lucro Bruto</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${resumo.financeiro.lucro_bruto >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ${formatCurrency(resumo.financeiro.lucro_bruto)}
            </div>
            <p className="text-xs text-muted-foreground">
              ROI: {resumo.financeiro.roi_pct.toFixed(1)}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Produtividade</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(resumo.financeiro.produtividade_sc_ha || 0).toFixed(1)} sc/ha
            </div>
            <p className="text-xs text-muted-foreground">
              {resumo.area_ha} ha
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Gráfico de Custo vs Receita */}
      <Card>
        <CardHeader>
          <CardTitle>Análise Financeira</CardTitle>
        </CardHeader>
        <CardContent>
          <BarChart
            data={[
              { label: 'Custo', value: resumo.financeiro.despesa_total, fill: '#ef4444' },
              { label: 'Receita', value: resumo.financeiro.receita_total, fill: '#22c55e' }
            ]}
          />
        </CardContent>
      </Card>

      {/* Tabela de Despesas */}
      <Card>
        <CardHeader>
          <CardTitle>Despesas por Operação</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Operação</TableHead>
                <TableHead>Data</TableHead>
                <TableHead className="text-right">Valor</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {/* TODO: Buscar Despesas com operacao_id */}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
```

**Complexidade:** 🟡 Média
**Tempo:** 1.5h
**Dependências:** ✅ Tarefa 4.1 (endpoint resumo)

---

### Tarefa 5.2: Timeline Visual de Fases (Stepper)

**Objetivo:** Mostrar progresso visual da safra (PLANEJADA → ENCERRADA)

**Arquivos a criar:**
- `apps/web/src/components/agricola/safra-fase-timeline.tsx` (novo)

**Implementação:**

```tsx
// apps/web/src/components/agricola/safra-fase-timeline.tsx
const FASES = [
  { id: 'PLANEJADA', label: 'Planejada', icon: '📋' },
  { id: 'PREPARO_SOLO', label: 'Preparo Solo', icon: '🚜' },
  { id: 'PLANTIO', label: 'Plantio', icon: '🌱' },
  { id: 'DESENVOLVIMENTO', label: 'Desenvolvimento', icon: '🌾' },
  { id: 'COLHEITA', label: 'Colheita', icon: '🌽' },
  { id: 'POS_COLHEITA', label: 'Pós-Colheita', icon: '📦' },
  { id: 'ENCERRADA', label: 'Encerrada', icon: '✅' }
]

export function SafraFaseTimeline({
  safraStatus,
  historicoFases
}: {
  safraStatus: string
  historicoFases: Array<{ fase_nova: string; data: string }>
}) {
  const indexAtual = FASES.findIndex(f => f.id === safraStatus)

  return (
    <div className="py-8">
      <div className="flex items-center justify-between">
        {FASES.map((fase, idx) => (
          <div key={fase.id} className="flex flex-col items-center flex-1">
            {/* Círculo da fase */}
            <div className={`
              w-12 h-12 rounded-full flex items-center justify-center text-lg
              ${idx <= indexAtual ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-600'}
            `}>
              {fase.icon}
            </div>

            {/* Label */}
            <p className="text-xs text-center mt-2">{fase.label}</p>

            {/* Data */}
            {historicoFases.find(h => h.fase_nova === fase.id) && (
              <p className="text-xs text-gray-500 mt-1">
                {new Date(historicoFases.find(h => h.fase_nova === fase.id)!.data).toLocaleDateString()}
              </p>
            )}

            {/* Linha conectora */}
            {idx < FASES.length - 1 && (
              <div className={`
                h-1 flex-1 ${idx < indexAtual ? 'bg-green-500' : 'bg-gray-200'}
              `} style={{ margin: '8px 0', width: 'calc(100% - 24px)' }} />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
```

**Complexidade:** 🟢 Baixa
**Tempo:** 1h
**Dependências:** Nenhuma

---

## Cronograma de Execução

### 📅 Semana 1

| Dia | Tarefa | Tempo | Status |
|-----|--------|-------|--------|
| Seg | 0.1 (FK Despesa/Receita) | 30 min | ⏳ |
| Ter | 0.2 (Lookup table) | 45 min | ⏳ |
| Qua | 1.1 (Validação fase) | 1.5h | ⏳ |
| Qui | 1.2 (Validação data) | 30 min | ⏳ |
| Sex | 2.1 (Operação → Despesa) | 2h | ⏳ |

**Subtotal:** 6.25h

### 📅 Semana 2

| Dia | Tarefa | Tempo | Status |
|-----|--------|-------|--------|
| Seg | 2.2 (Romaneio → Receita) | 2h | ⏳ |
| Ter | 3.1 (Insumo → Estoque) | 2.5h | ⏳ |
| Qua | 4.1 (Dashboard) | 2h | ⏳ |
| Qui | 5.1 (Aba Financeiro) | 1.5h | ⏳ |
| Sex | 5.2 (Timeline) + Testes | 1.5h | ⏳ |

**Subtotal:** 10.5h

### 📅 Semana 3

| Dia | Tarefa | Tempo | Status |
|-----|--------|-------|--------|
| Seg-Sex | Testes E2E + Deploy | 10h | ⏳ |

---

## Estimativa Total

| Categoria | Horas |
|-----------|-------|
| Banco de Dados | 1.25h |
| Backend (RN) | 3h |
| Backend (Webhooks) | 6.5h |
| Backend (Dashboard) | 2h |
| Frontend | 2.5h |
| Testes | 8h |
| **TOTAL** | **23.25h** |

**Timeline:** 3 semanas (160h/semana = 1.45 dias úteis)

---

## Dependências e Bloqueadores

```
Semana 1:
0.1 → 1.1, 2.1 ✓
0.2 → 1.1 ✓

Semana 2:
1.1 → 1.2 ✓
2.1 → 4.1 ✓
2.2 → 4.1 ✓
3.1 → standalone ✓
4.1 → 5.1 ✓

Semana 3:
5.1, 5.2 → Testes E2E ✓
```

**Caminho crítico:** 0.1 → 1.1 → 1.2 → 2.1 → 4.1 → 5.1 → Testes

---

## Checklist de Validação (Pré-Deploy)

### Backend
- [ ] Todas as migrations executadas com sucesso
- [ ] Testes unitários passando (100% dos casos críticos)
- [ ] Testes de tenant isolation passando
- [ ] Webhook de operação → despesa testado end-to-end
- [ ] Webhook de romaneio → receita testado end-to-end
- [ ] Desconto de estoque FIFO validado
- [ ] Dashboard retorna valores corretos
- [ ] Sem erros de lógica de RN

### Frontend
- [ ] Timeline visual renderiza corretamente
- [ ] Aba Financeiro mostra dados corretos
- [ ] Permissões validadas (não mostra botões sem permissão)
- [ ] Responsivo em mobile/tablet
- [ ] Sem erros no console

### Integração
- [ ] Criar operação → Despesa criada
- [ ] Criar romaneio → Receita criada
- [ ] Desconto de estoque refletido imediatamente
- [ ] Dashboard atualiza em tempo real

### Documentação
- [ ] README atualizado com novo fluxo
- [ ] Comentários em código-chave
- [ ] API docs atualizadas

---

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|--------|-----------|
| Webhook falha silenciosamente | Alta | Médio | Log detalhado + retry em background |
| FIFO com muitos lotes lento | Média | Médio | Índice em data_fabricacao + batch processing |
| FK cascata quebra dados | Baixa | Alto | Testes de integridade + backup |
| Frontend desincronizado com backend | Média | Médio | Testes E2E + validação de schema |
| Tenant isolation bug | Baixa | Crítico | Auditoria completa + testes separados por tenant |

---

## Próximos Passos (Pós-MVP)

1. **Iteração 3.2 (Estoque):** Historico de disponibilidade de máquinas
2. **Iteração 4.2 (Dashboard):** Relatórios comparativos (safra vs. histórico)
3. **Iteração 5.3 (UX):** Prescrição → Operação automática
4. **Integração 6:** NFe automática para romaneios

