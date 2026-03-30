# Estoque API Reference

Complete API reference for inventory/warehouse management endpoints.

---

## Endpoints

### GET `/api/v1/safras/{safra_id}/estoque/saldo`

Get current inventory balance by deposit for a harvest.

**Authentication:** Required (JWT)
**Permissions:** `A1_PLANEJAMENTO` module access

**Parameters:**
- `safra_id` (path, required) - UUID of the harvest

**Response:** `EstoqueResumoResponse`
```json
{
  "safra_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_produtos_ativos": 5,
  "total_depositos": 2,
  "depositos": [
    {
      "deposito_id": "660e8400-e29b-41d4-a716-446655440000",
      "deposito_nome": "Galpão de Insumos",
      "saldo_total": 1250.50,
      "produtos": [
        {
          "produto_id": "770e8400-e29b-41d4-a716-446655440000",
          "produto_nome": "Adubo Nitrogenado",
          "quantidade": 600.0,
          "unidade": "kg",
          "num_lotes": 2,
          "custo_total_lotes": 6000.00
        }
      ]
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `403` - Forbidden (module not contracted)
- `404` - Safra not found

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/safras/550e8400-e29b-41d4-a716-446655440000/estoque/saldo" \
  -H "Authorization: Bearer <token>"
```

---

### GET `/api/v1/safras/{safra_id}/estoque/movimentacoes`

Get inventory movements (transactions) for a harvest with filtering and pagination.

**Authentication:** Required (JWT)
**Permissions:** `A1_PLANEJAMENTO` module access

**Parameters (Query):**
- `safra_id` (path, required) - UUID of the harvest
- `tipo` (optional) - Filter by movement type: `ENTRADA`, `SAIDA`, `AJUSTE`, `TRANSFERENCIA`
- `deposito_id` (optional) - Filter by deposit UUID
- `data_inicio` (optional) - Start date (ISO 8601: `2026-03-30`)
- `data_fim` (optional) - End date (ISO 8601: `2026-03-30`)
- `numero_lote` (optional) - Filter by batch number (partial match)
- `limit` (optional, default: 100) - Records per page (max: 1000)
- `offset` (optional, default: 0) - Pagination offset

**Response:** `MovimentacaoResponse`
```json
{
  "total": 45,
  "limit": 100,
  "offset": 0,
  "movimentacoes": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440000",
      "deposito_id": "660e8400-e29b-41d4-a716-446655440000",
      "deposito_nome": "Galpão de Insumos",
      "produto_id": "770e8400-e29b-41d4-a716-446655440000",
      "produto_nome": "Adubo Nitrogenado",
      "lote_id": "990e8400-e29b-41d4-a716-446655440000",
      "numero_lote": "LOTE-2024-001",
      "tipo": "SAIDA",
      "quantidade": 150.5,
      "unidade": "kg",
      "data_movimentacao": "2026-03-28T14:30:00Z",
      "custo_unitario": 10.00,
      "custo_total": 1505.00,
      "motivo": "Aplicação em talhão 5",
      "operacao_tipo": "APLICACAO_DEFENSIVO",
      "operacao_id": "aa0e8400-e29b-41d4-a716-446655440000"
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid filter parameters
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Safra not found

**Examples:**

Fetch all SAIDA (consumption) movements:
```bash
curl -X GET "http://localhost:8000/api/v1/safras/550e8400-e29b-41d4-a716-446655440000/estoque/movimentacoes?tipo=SAIDA" \
  -H "Authorization: Bearer <token>"
```

Fetch movements in a date range:
```bash
curl -X GET "http://localhost:8000/api/v1/safras/550e8400-e29b-41d4-a716-446655440000/estoque/movimentacoes?data_inicio=2026-03-01&data_fim=2026-03-31" \
  -H "Authorization: Bearer <token>"
```

Fetch movements by deposit with pagination:
```bash
curl -X GET "http://localhost:8000/api/v1/safras/550e8400-e29b-41d4-a716-446655440000/estoque/movimentacoes?deposito_id=660e8400-e29b-41d4-a716-446655440000&limit=50&offset=0" \
  -H "Authorization: Bearer <token>"
```

---

## Data Types

### EstoqueResumoResponse
```python
{
  "safra_id": UUID,
  "total_produtos_ativos": int,
  "total_depositos": int,
  "depositos": List[DepositoSaldo]
}
```

### DepositoSaldo
```python
{
  "deposito_id": UUID,
  "deposito_nome": str,
  "saldo_total": float,
  "produtos": List[ProdutoSaldo]
}
```

### ProdutoSaldo
```python
{
  "produto_id": UUID,
  "produto_nome": str,
  "quantidade": float,
  "unidade": str,
  "num_lotes": int,
  "custo_total_lotes": float
}
```

### MovimentacaoResponse
```python
{
  "total": int,
  "limit": int,
  "offset": int,
  "movimentacoes": List[MovimentacaoSafra]
}
```

### MovimentacaoSafra
```python
{
  "id": UUID,
  "deposito_id": UUID,
  "deposito_nome": str,
  "produto_id": UUID,
  "produto_nome": str,
  "lote_id": UUID | None,
  "numero_lote": str | None,
  "tipo": str,  # ENTRADA, SAIDA, AJUSTE, TRANSFERENCIA
  "quantidade": float,
  "unidade": str,
  "data_movimentacao": datetime,
  "custo_unitario": float | None,
  "custo_total": float | None,
  "motivo": str | None,
  "operacao_tipo": str | None,  # PLANTIO, APLICACAO_DEFENSIVO, COLHEITA, etc.
  "operacao_id": UUID | None
}
```

---

## Filtering Guide

### By Movement Type
```bash
# Get all product receipts
?tipo=ENTRADA

# Get all consumptions (harvest, applications)
?tipo=SAIDA

# Get adjustments (inventory corrections)
?tipo=AJUSTE

# Get transfers between deposits
?tipo=TRANSFERENCIA
```

### By Date Range
```bash
# Full month of March
?data_inicio=2026-03-01&data_fim=2026-03-31

# Last 7 days (when called on 2026-03-30)
?data_inicio=2026-03-23&data_fim=2026-03-30
```

### By Batch
```bash
# Partial match on batch number
?numero_lote=LOTE-2024

# Exact match (database wildcard)
?numero_lote=LOTE-2024-001
```

### Pagination
```bash
# First 50 records
?limit=50&offset=0

# Second page (records 50-100)
?limit=50&offset=50

# Large results (1000 at a time)
?limit=1000&offset=0
```

---

## Error Responses

All errors return JSON with `detail` field:

```json
{
  "detail": "Safra não encontrada"
}
```

### Common Errors

| Status | Detail | Cause |
|--------|--------|-------|
| 400 | "Invalid tipo" | Unknown movement type |
| 400 | "Invalid date format" | Date not ISO 8601 |
| 401 | "Not authenticated" | Missing JWT token |
| 403 | "Module A1_PLANEJAMENTO not contracted" | Missing permission |
| 404 | "Safra não encontrada" | ID doesn't exist |

---

## Implementation Notes

### Tenant Isolation
- All queries automatically filter to authenticated user's tenant
- Extracted via JWT token `tenant_id` claim
- Enforced at service layer

### Performance
- **Saldo endpoint:** ~50ms for typical farm (10 deposits, 100 products)
- **Movimentacoes endpoint:** ~100ms with full-text search and joins
- Indexes on: `safra_id`, `deposito_id`, `tipo`, `data_movimentacao`

### Movimentacao Origin Tracking
The `operacao_tipo` and `operacao_id` fields track what triggered the movement:
- `APLICACAO_DEFENSIVO` → InsumoOperacao consumption
- `COLHEITA` → RomaneioColheita harvest
- `AJUSTE` → Manual adjustment by user
- `TRANSFERENCIA` → Deposit-to-deposit transfer

---

## Frontend Integration

See `/apps/web/src/hooks/use-estoque.ts` for React hooks:

```typescript
// Fetch saldo with 5-minute stale time
const { data: saldo, isLoading } = useEstoqueSaldo(safraId);

// Fetch movimentacoes with filters
const { data: movimentacoes } = useEstoqueMovimentacoes(safraId, filters);

// Combined hook with refetch
const { saldo, movimentacoes, refetch } = useEstoque(safraId, filters);
```

---

## Rate Limiting

No explicit rate limiting on these endpoints. Tenant isolation ensures data visibility limits.

---

## Changelog

**v1.0** (2026-03-30)
- Initial release
- FIFO inventory deduction
- Movement history with pagination
- Tenant isolation
