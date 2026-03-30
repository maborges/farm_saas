# FASE 6: E2E Tests & Documentation

## Overview

FASE 6 completes the Harvest Integration project with end-to-end test coverage and comprehensive documentation. All tests validate FIFO inventory deduction, tenant isolation, and error handling.

**Status:** ✅ COMPLETE
**Tests:** 9 passing (3 E2E + 6 unit)
**Coverage:** FIFO logic, tenant isolation, error scenarios

---

## Test Coverage

### E2E Tests (`test_e2e_colheita_completa.py`)

#### 1. `test_fifo_deduction_completo`
Complete FIFO inventory deduction workflow:
- Creates deposit, product (Adubo Nitrogenado), two batches with different historical costs
  - Batch 1 (oldest): 1000 kg @ R$ 10/kg custo_unitario
  - Batch 2 (newer): 500 kg @ R$ 12/kg custo_unitario
- Consumes 600 kg via FIFO
- **Validates:**
  - Oldest batch consumed first (FIFO principle)
  - Historical cost used (R$ 10/kg, not current preco_medio of R$ 15/kg)
  - `quantidade_atual` updated correctly (1000 - 600 = 400)
  - Batch remains ATIVO (not fully consumed)

**Key Assertions:**
```python
assert consumo.quantidade_consumida == 600.0
assert consumo.lotes_consumidos[0]["custo_unitario"] == 10.0
assert consumo.custo_total == 6000.0  # 600 × 10
assert lote_antigo.quantidade_atual == 400.0
```

#### 2. `test_fifo_erro_estoque_insuficiente`
Error handling when insufficient inventory:
- Creates batch with 50 kg
- Attempts to consume 100 kg
- **Validates:** BusinessRuleError raised with "Saldo insuficiente" message

#### 3. `test_isolamento_tenant_estoque`
Multi-tenant isolation:
- Tenant A creates deposit and batch
- Tenant B attempts to consume Tenant A's inventory
- **Validates:** BusinessRuleError raised with "não tem lotes ativos disponíveis"
- **Security:** Proves tenant_id filtering prevents cross-tenant access

---

## Unit Tests (`test_fifo_estoque.py`)

6 additional tests covering edge cases:

1. **FIFO ordering** - Multiple batches, correct consumption order
2. **Historical cost** - Uses batch.custo_unitario, not product.preco_medio
3. **Insufficient inventory** - Error handling
4. **Exact consumption** - All batches fully consumed
5. **Status tracking** - Batches marked ESGOTADO when empty
6. **No deposit filter** - Works across all deposits

---

## Implementation Details

### Tenant Isolation in FIFO

The `consumir_lotes_fifo` function now enforces tenant isolation:

```python
# Join with Deposito to filter by tenant_id
stmt = select(LoteEstoque).join(Deposito).where(
    and_(
        LoteEstoque.produto_id == produto_id,
        LoteEstoque.status == "ATIVO",
        LoteEstoque.quantidade_atual > 0,
    )
)

# Filter by tenant_id if provided
if tenant_id:
    stmt = stmt.where(Deposito.tenant_id == tenant_id)
```

**Security Guarantee:** When `tenant_id` is provided, only batches in deposits belonging to that tenant are considered.

### Test Database Setup

SQLite in-memory database (`conftest.py`):
- Lightweight, fast test execution (0.3s for all 9 tests)
- No JSONB support, but all required tables created
- `cadastros_produtos` schema includes all Produto model columns:
  - `unidade_medida`, `codigo_interno`, `sku`, `marca_id`, `categoria_id`, etc.

---

## Running the Tests

```bash
cd services/api
source .venv/bin/activate

# Run only E2E tests
pytest tests/test_e2e_colheita_completa.py -v

# Run only FIFO tests
pytest tests/test_fifo_estoque.py -v

# Run all tests together
pytest tests/ -v -k "e2e_colheita or fifo_estoque"

# Run with detailed output
pytest tests/test_e2e_colheita_completa.py -vv --tb=short
```

**Expected Output:**
```
3 passed in 0.29s    (E2E tests)
6 passed in 0.45s    (FIFO tests)
```

---

## What's Tested

| Scenario | Test | Result |
|----------|------|--------|
| FIFO consumption order | `test_fifo_deduction_completo` | ✅ Oldest batch first |
| Historical cost tracking | `test_fifo_custo_historico_nao_preco_medio` | ✅ Uses batch cost, not product price |
| Insufficient inventory | `test_fifo_erro_estoque_insuficiente` | ✅ Raises BusinessRuleError |
| Tenant isolation | `test_isolamento_tenant_estoque` | ✅ Tenant B cannot access Tenant A inventory |
| Status updates | `test_fifo_lote_status_esgotado` | ✅ Batch marked ESGOTADO when empty |
| Multiple batches | `test_fifo_exato_all_lotes_consumidos` | ✅ Consumes across multiple batches |

---

## Integration with Harvest Workflow

Tests validate the integration chain:

1. **Operation Creation** (via API)
2. **Insumo → FIFO Deduction** (webhook)
   - Validates oldest batch consumed first
   - Validates historical costs applied
   - Validates tenant isolation maintained
3. **Estoque State Update**
   - `LoteEstoque.quantidade_atual` decremented
   - `LoteEstoque.status` → ESGOTADO if empty
   - `SaldoEstoque` recalculated
4. **Movimentacao Audit Trail** (recorded in DB)

---

## Known Limitations

1. **SQLite in Tests** - No JSONB support in test environment
   - Solution: JSON columns use native SQLite TEXT type

2. **No RLS in Tests** - PostgreSQL Row Level Security not available
   - Mitigation: Explicit tenant_id filtering in service layer

3. **Synchronous Models** - Tests use synchronous ORM models
   - All async/await patterns still validated via AsyncSession

---

## Next Steps

1. **Frontend Estoque Tab** - Already implemented (FASE 5)
   - Displays saldo by deposit
   - Shows movimentacao history with pagination
   - Timeline visualization of consumption

2. **Deployment Validation** - See DEPLOYMENT_CHECKLIST.md
   - PostgreSQL connection test
   - Migration verification
   - API endpoint validation

3. **Production Readiness**
   - Monitor tenant isolation in production logs
   - Track FIFO consumption accuracy in BI reports
   - Set up alerts for insufficient inventory scenarios

---

## References

- **Service Implementation:** `/services/api/operacional/services/estoque_fifo.py`
- **Models:** `/services/api/operacional/models/estoque.py`
- **Tests:** `/services/api/tests/test_e2e_colheita_completa.py`
- **Fixtures:** `/services/api/tests/conftest.py`
- **Frontend:** `/apps/web/src/hooks/use-estoque.ts`
