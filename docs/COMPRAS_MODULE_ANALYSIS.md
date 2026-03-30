# Análise Módulo Compras (Purchases)

**Data:** 2026-03-30
**Status:** Operacional, mas com gaps críticos de integração

---

## 1. Estrutura Atual

### Entidades (8)
```
Fornecedor (Supplier)
  ├─ PedidoCompra (Purchase Order)
  │   ├─ ItemPedidoCompra (PO Items)
  │   ├─ CotacaoFornecedor (Supplier Quotes)
  │   ├─ RecebimentoParcial (Receiving)
  │   │   └─ ItemRecebimento (Received Items)
  │   └─ DevolucaoFornecedor (Returns)
  │       └─ ItemDevolucao (Return Items)
```

### Endpoints (17)
- ✅ Suppliers: create, list
- ✅ POs: create, list, get, close (partial)
- ✅ Quotes: create, list, select
- ✅ Receiving: register (partial), list
- ✅ Returns: create, list, update status
- ✅ Price history: list by product/supplier

### Integrations
- ✅ **Estoque:** Creates MovimentacaoEstoque on receive
- ✅ **Financeiro:** Creates Despesa (expense) on receive
- ✅ **Produtos:** Tracks historical prices

---

## 2. Critical Gaps

### Gap 1: ❌ LoteEstoque Not Created on Receipt

**Current Flow:**
```
ItemRecebimento received
  ↓
EstoqueService.registrar_entrada()
  ↓
MovimentacaoEstoque created (ENTRADA)
  ↓
❌ MISSING: estoque_lotes creation
```

**Problem:**
- MovimentacaoEstoque records entry but no batch (lote) is created
- LoteEstoque requires: numero_lote, data_fabricacao, custo_unitario, etc.
- Without LoteEstoque, **FIFO deduction cannot track purchase source**

**Impact:**
- Received inventory has no physical batch record
- SaldoEstoque updated but LoteEstoque stays empty
- FIFO deduction fails: no batches to consume
- Cannot answer: "Which supplier provided this batch?"

**Solution Required:**
```python
# When ItemRecebimento is confirmed, create LoteEstoque:
lote = LoteEstoque(
    produto_id=item.produto_id,
    deposito_id=deposito_id,
    numero_lote=f"NFE-{numero_nf}",  # Invoice number as batch ID
    data_fabricacao=data_recebimento,  # Reception date
    data_validade=data_recebimento + prazo_validade,
    quantidade_inicial=quantidade_recebida,
    quantidade_atual=quantidade_recebida,
    custo_unitario=preco_real_unitario,  # Historical cost
    status="ATIVO",
)
```

---

### Gap 2: ❌ Service Procurement (Non-Inventory)

**Current State:**
- Compras assumes **all purchases are products for inventory**
- No support for services (consulting, labor, maintenance)

**Missing Types:**
- Prestação de Serviços (service contracts)
- Aluguel/Leasing (rentals)
- Serviços Terceirizados (outsourced services)

**Problem:**
- Service purchases should NOT create LoteEstoque
- Service purchases should create Despesa directly
- Current code treats everything as inventory input

**Solution Required:**
```python
# Add to PedidoCompra model:
tipo_pedido: Mapped[str] = mapped_column(String(20), default="PRODUTO")
# Values: PRODUTO, SERVICO, MANUTENCAO, etc.

# In receiving endpoint:
if pedido.tipo_pedido == "PRODUTO":
    # Create LoteEstoque
elif pedido.tipo_pedido == "SERVICO":
    # Create Despesa directly, no inventory
```

---

### Gap 3: ⚠️ Lote Identification (número_lote)

**Current Issue:**
```
recebimento without explicit numero_lote
  → EstoqueService creates entry without lote reference
  → LoteEstoque would have no meaningful batch number
```

**Problem:**
- Lotes should be trackable by: Invoice #, Batch #, Serial #
- Current code doesn't capture supplier batch info
- No way to recall "which batch had contamination?"

**Solution Required:**
```python
# ItemRecebimento should capture:
numero_nf: str          # Invoice number
numero_lote_fornecedor: str | None  # Supplier batch number
chave_nfe: str          # NFe key for traceability

# Then in LoteEstoque.numero_lote:
numero_lote = f"{numero_nf}:{numero_lote_fornecedor}"
```

---

### Gap 4: ⚠️ Cost Tracking Disconnection

**Current State:**
```
ItemPedidoCompra.preco_real_unitario
  ├─ Used for Despesa creation
  └─ Used for price history

LoteEstoque.custo_unitario
  └─ Should come from ItemPedidoCompra BUT NO LINK
```

**Problem:**
- When creating LoteEstoque, where does custo_unitario come from?
- Is it preco_real_unitario? preco_estimado_unitario?
- No audit trail of cost decisions

**Impact:**
- FIFO uses lote.custo_unitario but it's not linked to purchase
- Cannot answer: "Why did this batch cost R$X/kg?"
- Cost reconciliation impossible

**Solution Required:**
```python
# ItemRecebimento should have explicit link:
class ItemRecebimento:
    item_pedido_id  # Already has this
    preco_real_unitario  # Cost at receiving time

    # Create LoteEstoque with same cost:
    custo_unitario = preco_real_unitario (from ItemPedidoCompra OR ItemRecebimento)
```

---

### Gap 5: ❌ Devolução Não Reverte FIFO

**Current State:**
```
DevolucaoFornecedor created
  ↓
ItemDevolucao lists items being returned
  ↓
❓ How does this affect LoteEstoque?
```

**Missing:**
- No reverse movimentacao created
- LoteEstoque.quantidade_atual not decremented
- SaldoEstoque not updated
- No rollback of FIFO history

**Problem:**
- If 100kg consumed via FIFO from batch A
- Then 50kg returned to supplier
- Current FIFO still thinks 100kg was consumed
- Inventory counts are wrong

**Solution Required:**
```python
# On DevolucaoFornecedor approval:
for item in devolucao.itens:
    # Create reverse MovimentacaoEstoque (SAIDA reversed)
    mov = MovimentacaoEstoque(
        tipo="SAIDA_REVERSA",  # OR update SAIDA with negative qty
        quantidade=-item.quantidade,
        origem_tipo="DEVOLUCAO_FORNECEDOR",
        origem_id=devolucao.id,
    )

    # Update LoteEstoque
    lote.quantidade_atual += item.quantidade
    lote.status = "ATIVO"  # Reactivate if was ESGOTADO
```

---

### Gap 6: ⚠️ No Expiration Date (Prazo de Validade)

**Current State:**
- PedidoCompra and ItemRecebimento have NO expiration tracking
- LoteEstoque has data_validade but it's never populated

**Problem:**
- Cannot enforce FIFO by oldest expiration (FEFO - First Expire First Out)
- Cannot alert when batches approach expiration
- Cannot track perishable inventory properly

**Solution Required:**
```python
# Add to ItemRecebimento (or ItemPedidoCompra):
data_validade: date | None
data_fabricacao: date | None

# Or: require supplier to provide in receiving
# Then use in LoteEstoque creation:
lote.data_validade = recebimento.data_validade
lote.data_fabricacao = recebimento.data_fabricacao
```

---

## 3. Current Positive Features

✅ **Supplier Management**
- Full CRUD for suppliers
- Multi-supplier support
- Contact tracking

✅ **Quote Management**
- Multiple suppliers per PO
- Quote comparison
- Selection tracking

✅ **Receiving Workflow**
- Partial receipts supported
- Invoice (NFe) tracking
- Receipt user tracking

✅ **Financial Integration**
- Despesa created automatically on receipt
- Cost tracking per item
- Price history available

✅ **Return Management**
- Returns tracked with reason
- Supplier tracking
- Status workflow

---

## 4. Integration Map

```
┌─────────────────────────────────────────────────────────┐
│                    Compras (Purchases)                  │
│                                                         │
│  PedidoCompra → ItemPedidoCompra                       │
│       ↓              ↓                                 │
│   [RECEBIDO]  CotacaoFornecedor (quotes)             │
│       ↓              ↓                                 │
│  RecebimentoParcial ItemRecebimento                   │
│       ↓              ↓                                 │
│   [entrada_estoque] [preco_real_unitario]            │
│       ↓              ↓                                 │
│   ┌───┴───────────────┘                              │
│   │                                                   │
│   ├─→ Estoque.MovimentacaoEstoque ✅                 │
│   │     (tipo=ENTRADA, origem_tipo=PEDIDO_COMPRA)   │
│   │                                                   │
│   ├─→ Estoque.SaldoEstoque ✅                        │
│   │     (quantidade_atual += qtd)                    │
│   │                                                   │
│   ├─→ Estoque.LoteEstoque ❌ MISSING!               │
│   │     Should contain:                              │
│   │     - numero_lote (from NFe)                     │
│   │     - data_fabricacao                            │
│   │     - data_validade                              │
│   │     - custo_unitario (from ItemRecebimento)      │
│   │                                                   │
│   └─→ Financeiro.Despesa ✅                          │
│         (valor_total, origin=PEDIDO_COMPRA)         │
│                                                       │
│  DevolucaoFornecedor → ItemDevolucao                 │
│       ↓                                               │
│   [CONCLUIDA]                                        │
│       ↓                                               │
│   ❌ NO ESTOQUE REVERSAL                             │
│                                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Implementation Priority

### P0 - Critical (Block Harvest Integration)
1. **Create LoteEstoque on Receipt** (Gap 1)
   - Required for FIFO to work
   - Impact: Without this, estoque_lotes table stays empty
   - Effort: 3-4 hours

2. **Add numero_lote from Invoice** (Gap 3)
   - Required for batch traceability
   - Impact: Enables recall/quality tracking
   - Effort: 1-2 hours

3. **Devolução Reversal** (Gap 5)
   - Required for inventory accuracy
   - Impact: Prevents inventory discrepancies
   - Effort: 2-3 hours

### P1 - High (Data Integrity)
4. **Explicit Cost Link** (Gap 4)
   - Required for FIFO audit trail
   - Impact: Enables cost reconciliation
   - Effort: 1-2 hours

5. **Service Procurement** (Gap 2)
   - Required for non-inventory purchases
   - Impact: Broadens module applicability
   - Effort: 4-5 hours

### P2 - Medium (Features)
6. **Expiration Tracking** (Gap 6)
   - Required for perishable inventory
   - Impact: Enables FEFO (First Expire First Out)
   - Effort: 2-3 hours

---

## 6. Recommended Next Steps

1. **Short Term (This week):**
   - Implement P0 fixes (LoteEstoque creation, numero_lote)
   - Add devolução reversal
   - Test with FIFO integration

2. **Medium Term (Next sprint):**
   - Service procurement support
   - Expiration date tracking
   - Detailed cost audit trail

3. **Long Term:**
   - Supplier performance metrics
   - Automated PO suggestions
   - Price trend analysis

---

## 7. Testing Gaps

Currently No Tests For:
- ❌ LoteEstoque creation on receipt
- ❌ Devolução reversal effects on estoque
- ❌ Price history accuracy
- ❌ Partial receipt workflow
- ❌ Service vs. Product PO types

---

## References

- **Models:** `/operacional/models/compras.py` (117 lines, 8 entities)
- **Router:** `/operacional/routers/compras.py` (670 lines, 17 endpoints)
- **Schemas:** `/operacional/schemas/compras.py`
- **Integration Point:** EstoqueService (registrar_entrada)
