# Operacional Module Expert - AgroSaaS

You are a specialist in the **Operacional (Operations) Module** of AgroSaaS, responsible for fleet management, inventory control, maintenance, and procurement operations.

## Module Overview

The Operacional module manages all operational support activities that enable agricultural and livestock production: machinery, inventory, maintenance, and purchasing.

**Module IDs (for module access control):**
- `O1_FROTA` - Fleet and machinery management (tractors, harvesters, maintenance)
- `O2_ESTOQUE` - Multi-warehouse inventory (inputs, spare parts, finished goods)
- `O3_COMPRAS` - Procurement and supplier management

## Submodules Structure

Location: [services/api/operacional/](../../services/api/operacional/)

### Core Models

**Location:** [services/api/operacional/models/](../../services/api/operacional/models/)

## 1. Frota (Fleet Management)

**Module:** O1_FROTA

### 1.1 Maquinário (Machinery & Equipment)

**Key Model:** [operacional/models/frota.py](../../services/api/operacional/models/frota.py)

**Maquinario Attributes:**
- `nome` - Equipment name/identifier
- `tipo` - Type (TRATOR, COLHEITADEIRA, PULVERIZADOR, PLANTADEIRA, CAMINHÃO)
- `marca` - Brand (John Deere, Case, Massey Ferguson, Valtra)
- `modelo` - Model
- `ano` - Manufacturing year
- `placa_chassi` - License plate or chassis number
- `horimetro_atual` - Current hourmeter reading
- `km_atual` - Current odometer reading (for vehicles)
- `status` - Status (ATIVO, MANUTENCAO, INATIVO, VENDIDO)

**Equipment Types:**
- **TRATOR** - Tractor (general purpose)
- **COLHEITADEIRA** - Combine harvester
- **PULVERIZADOR** - Sprayer (self-propelled or towed)
- **PLANTADEIRA** - Planter/seeder
- **ADUBADEIRA** - Fertilizer spreader
- **CAMINHÃO** - Truck
- **CARRETA** - Trailer/wagon
- **IMPLEMENTO** - Implement (plow, disc, etc.)

**Usage Tracking:**
```python
# Update hourmeter after operation
maquinario = get_maquinario(trator_id)
maquinario.horimetro_atual = 2547.5  # hours
maquinario.km_atual = 15420  # km (if applicable)

# Link to field operation
operacao = OrdemServico(
    maquinario_id=trator_id,
    horas_trabalhadas=8.5,
    horimetro_inicial=2539,
    horimetro_final=2547.5,
    combustivel_consumido_litros=85
)

# Automatic maintenance check triggered
check_maintenance_due(maquinario)
```

### 1.2 Plano de Manutenção (Maintenance Plans)

**Purpose:** Preventive maintenance scheduling

**Key Model:** [operacional/models/frota.py - PlanoManutencao](../../services/api/operacional/models/frota.py)

**PlanoManutencao Attributes:**
- `maquinario_id` - Equipment reference
- `descricao` - Maintenance description (e.g., "Troca de óleo e filtros")
- `frequencia_horas` - Frequency in hours (e.g., every 250h)
- `frequencia_km` - Frequency in km (e.g., every 10,000 km)
- `ultimo_registro_horas` - Last maintenance hourmeter
- `ultimo_registro_km` - Last maintenance odometer

**Common Maintenance Plans:**

**Tractor:**
- Oil & filter change: Every 250h
- Hydraulic fluid: Every 1000h
- Air filter: Every 500h
- Fuel filter: Every 500h
- Transmission oil: Every 2000h
- Annual inspection: Every 365 days

**Combine Harvester:**
- Pre-season inspection: Before harvest
- Daily greasing: Every 10h
- Belt tension check: Every 50h
- Chain lubrication: Daily during harvest
- Post-season overhaul: End of harvest

**Maintenance Due Calculation:**
```python
def check_maintenance_due(maquinario, plano):
    hours_since_last = maquinario.horimetro_atual - plano.ultimo_registro_horas
    km_since_last = maquinario.km_atual - plano.ultimo_registro_km

    if plano.frequencia_horas and hours_since_last >= plano.frequencia_horas:
        create_alert(f"Manutenção vencida: {plano.descricao}")
        create_ordem_servico(maquinario, plano, "PREVENTIVA")

    if plano.frequencia_km and km_since_last >= plano.frequencia_km:
        create_alert(f"Manutenção vencida: {plano.descricao}")
        create_ordem_servico(maquinario, plano, "PREVENTIVA")
```

### 1.3 Ordem de Serviço (Work Orders / Service Orders)

**Purpose:** Track maintenance and repair activities

**Key Model:** [operacional/models/frota.py - OrdemServico](../../services/api/operacional/models/frota.py)

**OrdemServico Attributes:**
- `numero_os` - Work order number (auto-generated, unique)
- `maquinario_id` - Equipment being serviced
- `tipo` - Type (PREVENTIVA, CORRETIVA, REVISAO)
- `status` - Status (ABERTA, EM_EXECUCAO, CONCLUIDA, CANCELADA)
- `descricao_problema` - Problem description
- `diagnostico_tecnico` - Technician's diagnosis
- `data_abertura` - Opening date
- `data_conclusao` - Completion date
- `horimetro_na_abertura` - Hourmeter at opening
- `tecnico_responsavel` - Responsible technician
- `custo_total_pecas` - Total parts cost
- `custo_mao_obra` - Labor cost

**Work Order Types:**
- **PREVENTIVA:** Scheduled maintenance (oil change, filter replacement)
- **CORRETIVA:** Breakdown repair (engine failure, hydraulic leak)
- **REVISAO:** Periodic inspection (annual inspection, pre-season check)
- **PREDITIVA:** Condition-based (vibration analysis, oil analysis)

**Work Order Flow:**
```
ABERTA (new issue reported)
   ↓
EM_EXECUCAO (technician working)
   ↓
CONCLUIDA (repair completed)
   or
CANCELADA (duplicate, not needed)
```

**Example - Breakdown Repair:**
```python
os = OrdemServico(
    numero_os="OS-2024-00123",
    maquinario_id=colheitadeira_id,
    tipo="CORRETIVA",
    status="ABERTA",
    descricao_problema="Motor superaquecendo, temperatura acima de 100°C",
    horimetro_na_abertura=1547,
    data_abertura=datetime.now()
)

# Technician diagnoses
os.diagnostico_tecnico = "Bomba d'água com vazamento, necessário substituição"
os.status = "EM_EXECUCAO"

# Add parts used
item = ItemOrdemServico(
    os_id=os.id,
    produto_id=bomba_agua_id,
    quantidade=1,
    preco_unitario_na_data=850.00
)

# Complete work
os.custo_total_pecas = 850.00
os.custo_mao_obra = 300.00  # 5 hours * R$ 60/hour
os.data_conclusao = datetime.now()
os.status = "CONCLUIDA"

# Update maintenance history
registro = RegistroManutencao(
    maquinario_id=colheitadeira_id,
    os_id=os.id,
    data_realizacao=datetime.now(),
    tipo="CORRETIVA",
    descricao="Substituição bomba d'água",
    custo_total=1150.00,
    horimetro_na_data=1547
)
```

### 1.4 Registro de Manutenção (Maintenance History)

**Purpose:** Historical log of all maintenance activities

**Key Model:** [operacional/models/frota.py - RegistroManutencao](../../services/api/operacional/models/frota.py)

**Uses:**
- Equipment history report
- Resale value assessment (well-maintained = higher value)
- Warranty claims (proof of maintenance)
- Reliability analysis (MTBF - Mean Time Between Failures)

**Metrics:**
- **Total Maintenance Cost:** Sum of all maintenance over lifetime
- **Cost per Hour:** Total maintenance cost / total hours operated
- **Availability:** (Total hours - Downtime hours) / Total hours * 100%
- **MTBF:** Total operating hours / Number of failures

### 1.5 Item de Ordem de Serviço (Parts Used)

**Purpose:** Track spare parts consumed in maintenance

**Key Model:** [operacional/models/frota.py - ItemOrdemServico](../../services/api/operacional/models/frota.py)

**ItemOrdemServico Attributes:**
- `os_id` - Work order reference
- `produto_id` - Spare part from inventory (Estoque module)
- `quantidade` - Quantity used
- `preco_unitario_na_data` - Unit price at the time (for costing)

**Integration with Estoque:**
```python
# When completing work order, update inventory
for item in os.itens:
    produto = get_produto(item.produto_id)
    produto.quantidade_estoque -= item.quantidade

    # Create inventory transaction
    movimentacao = MovimentacaoEstoque(
        produto_id=produto.id,
        tipo="SAIDA",
        quantidade=item.quantidade,
        motivo=f"Consumo OS {os.numero_os}",
        data_movimentacao=datetime.now()
    )
```

## 2. Estoque (Inventory Management)

**Module:** O2_ESTOQUE

### 2.1 Produto (Products / SKUs)

**Key Model:** [operacional/models/estoque.py](../../services/api/operacional/models/estoque.py)

**Produto Attributes:**
- `codigo` - SKU / product code
- `nome` - Product name
- `categoria` - Category (INSUMO, PECA, PRODUTO_ACABADO)
- `unidade_medida` - Unit (KG, LITRO, SACA, UNIDADE)
- `quantidade_estoque` - Current stock quantity
- `estoque_minimo` - Minimum stock level (reorder point)
- `estoque_maximo` - Maximum stock level
- `custo_medio` - Average cost (updated on purchases)
- `preco_venda` - Sale price (if applicable)
- `armazem_id` - Warehouse location (if multi-warehouse)

**Product Categories:**

**A. INSUMO (Agricultural Inputs):**
- Fertilizantes (Fertilizers): NPK, Urea, KCl
- Defensivos (Pesticides): Herbicides, Fungicides, Insecticides
- Sementes (Seeds): Corn, Soy, Wheat hybrids
- Combustível (Fuel): Diesel, gasoline

**B. PECA (Spare Parts):**
- Filtros (Filters): Oil, fuel, air, hydraulic
- Peças de reposição (Replacement parts): Belts, bearings, seals
- Pneus (Tires)
- Baterias (Batteries)

**C. PRODUTO_ACABADO (Finished Goods):**
- Grãos (Grains): Soy, corn in storage
- Leite (Milk): In bulk tank
- Gado (Cattle): Ready for sale

**Inventory Valuation Methods:**
- **FIFO (First-In, First-Out):** Oldest cost first
- **Weighted Average:** Recalculate on each purchase
- **LIFO (Last-In, First-Out):** Not allowed in Brazil for tax purposes

**Average Cost Calculation:**
```python
# Current stock: 100 kg @ R$ 10/kg (total value: R$ 1000)
# Purchase: 50 kg @ R$ 12/kg (total value: R$ 600)

new_quantity = 100 + 50  # 150 kg
new_total_value = 1000 + 600  # R$ 1600
new_average_cost = 1600 / 150  # R$ 10.67/kg

produto.quantidade_estoque = 150
produto.custo_medio = 10.67
```

### 2.2 Armazém (Warehouse / Storage Location)

**Purpose:** Multi-warehouse inventory tracking

**Armazem Attributes:**
- `nome` - Warehouse name
- `tipo` - Type (CENTRAL, FAZENDA, TERCEIRO)
- `capacidade_total` - Total capacity (kg, m³, bags)
- `capacidade_ocupada` - Current occupation
- `responsavel` - Warehouse manager
- `endereco` - Address (if external)

**Multi-Warehouse Scenarios:**
- Central warehouse + farm silos
- Grain storage at cooperatives (third-party)
- Different storage for different product types (chemicals, fertilizers, grain)

### 2.3 Movimentação de Estoque (Inventory Transactions)

**Purpose:** Track all inventory movements

**MovimentacaoEstoque Types:**
- **ENTRADA:** Receipt (purchase, production, return)
- **SAIDA:** Issue (consumption, sale, transfer)
- **AJUSTE:** Adjustment (physical count, damage, expiry)
- **TRANSFERENCIA:** Transfer between warehouses

**Movimentacao Attributes:**
- `produto_id`
- `tipo` - Transaction type
- `quantidade` - Quantity (+/-)
- `custo_unitario` - Unit cost (for ENTRADA)
- `motivo` - Reason/reference
- `armazem_origem_id` - Source warehouse (if transfer)
- `armazem_destino_id` - Destination warehouse (if transfer)
- `data_movimentacao` - Transaction date

**Examples:**
```python
# Purchase fertilizer
movimentacao = MovimentacaoEstoque(
    produto_id=ureia_id,
    tipo="ENTRADA",
    quantidade=5000,  # kg
    custo_unitario=2.50,  # R$/kg
    motivo="Compra NF 12345 - Supplier XYZ",
    armazem_destino_id=armazem_central_id
)

# Consumption in field operation
movimentacao = MovimentacaoEstoque(
    produto_id=ureia_id,
    tipo="SAIDA",
    quantidade=300,  # kg
    motivo="Adubação Talhão 01 - OS 456",
    armazem_origem_id=armazem_central_id
)

# Physical count adjustment
movimentacao = MovimentacaoEstoque(
    produto_id=ureia_id,
    tipo="AJUSTE",
    quantidade=-50,  # Found 50kg less than system
    motivo="Inventário físico 2024-12-31 - Diferença contagem"
)
```

### 2.4 Lote de Produto (Product Batches)

**Purpose:** Batch/lot tracking for traceability

**LoteProduto Attributes:**
- `produto_id`
- `numero_lote` - Batch number (from supplier or internal)
- `data_fabricacao` - Manufacturing date
- `data_validade` - Expiry date
- `quantidade` - Quantity in this batch
- `nota_fiscal` - Invoice number (for traceability)

**Use Cases:**
- Chemical expiry tracking (pesticides have shelf life)
- Seed lot tracking (germination rate varies by batch)
- Grain lot tracking (different harvest dates, moisture levels)
- Regulatory compliance (recall management)

**FEFO (First-Expired, First-Out):**
```python
# When issuing products, prioritize expiring batches
lotes_disponiveis = get_lotes_produto(produto_id, ordem="data_validade ASC")

for lote in lotes_disponiveis:
    if quantidade_restante <= 0:
        break

    quantidade_deste_lote = min(lote.quantidade, quantidade_restante)

    create_movimentacao(
        produto_id=produto_id,
        lote_id=lote.id,
        tipo="SAIDA",
        quantidade=quantidade_deste_lote
    )

    quantidade_restante -= quantidade_deste_lote
```

## 3. Compras (Procurement)

**Module:** O3_COMPRAS

### 3.1 Fornecedor (Suppliers)

**Fornecedor Attributes:**
- `nome_razao_social` - Company name
- `cnpj` - Tax ID
- `categoria` - Category (INSUMOS, PECAS, SERVICOS)
- `contato_principal` - Main contact
- `telefone`, `email`
- `condicoes_pagamento` - Payment terms
- `prazo_entrega_medio` - Average delivery time (days)
- `avaliacao` - Rating (1-5 stars)

**Supplier Evaluation:**
- Delivery time compliance
- Product quality
- Price competitiveness
- Payment flexibility
- Technical support

### 3.2 Cotação (Price Quotation)

**Purpose:** Compare prices from multiple suppliers

**Cotacao Attributes:**
- `data_cotacao` - Quotation date
- `validade_dias` - Validity period
- `status` - Status (ABERTA, AGUARDANDO_APROVACAO, APROVADA, CANCELADA)

**CotacaoItem:**
- `cotacao_id`
- `produto_id`
- `quantidade_solicitada`

**CotacaoFornecedor:**
- `cotacao_id`
- `fornecedor_id`
- `preco_unitario` - Unit price
- `prazo_entrega` - Delivery time
- `condicao_pagamento` - Payment terms
- `observacoes`

**Quotation Process:**
```
1. Create quotation request (products + quantities)
2. Send to multiple suppliers
3. Receive supplier quotes
4. Compare: price, delivery time, payment terms
5. Select winner (lowest price, best terms, preferred supplier)
6. Generate purchase order
```

**Price Comparison:**
```python
# Compare total cost including delivery and payment terms
for fornecedor_quote in cotacao.fornecedores:
    total_products = sum(item.quantidade * fornecedor_quote.preco_unitario
                         for item in cotacao.itens)

    # Adjust for payment terms (discount for cash, increase for installments)
    if fornecedor_quote.condicao_pagamento == "A_VISTA":
        total_products *= 0.97  # 3% cash discount
    elif fornecedor_quote.condicao_pagamento == "30_60_DIAS":
        total_products *= 1.02  # 2% increase for 60-day terms

    # Add freight cost
    total_with_freight = total_products + fornecedor_quote.custo_frete

    fornecedor_quote.total_comparativo = total_with_freight
```

### 3.3 Pedido de Compra (Purchase Order)

**PedidoCompra Attributes:**
- `numero_pedido` - PO number (auto-generated)
- `fornecedor_id` - Supplier
- `data_pedido` - Order date
- `data_entrega_prevista` - Expected delivery date
- `status` - Status (ABERTO, CONFIRMADO, PARCIALMENTE_RECEBIDO, RECEBIDO, CANCELADO)
- `valor_total` - Total amount
- `condicao_pagamento` - Payment terms
- `observacoes` - Notes (delivery address, special instructions)

**PedidoCompraItem:**
- `pedido_compra_id`
- `produto_id`
- `quantidade_pedida`
- `quantidade_recebida` - Received quantity (updated on receipt)
- `preco_unitario`
- `valor_total` - Unit price * quantity

**Purchase Order Flow:**
```
ABERTO (created, pending confirmation)
   ↓
CONFIRMADO (supplier acknowledged)
   ↓
PARCIALMENTE_RECEBIDO (partial delivery)
   ↓
RECEBIDO (fully delivered)
   or
CANCELADO (cancelled before delivery)
```

**Receiving Process:**
```python
# Receive goods against PO
recebimento = RecebimentoCompra(
    pedido_compra_id=po.id,
    data_recebimento=date.today(),
    nota_fiscal="NF 54321",
    transportadora="Transportadora ABC"
)

for item in po.itens:
    # Record received quantity (may differ from ordered)
    item.quantidade_recebida += quantidade_recebida

    # Update inventory
    movimentacao = MovimentacaoEstoque(
        produto_id=item.produto_id,
        tipo="ENTRADA",
        quantidade=quantidade_recebida,
        custo_unitario=item.preco_unitario,
        motivo=f"Recebimento PO {po.numero_pedido} - NF 54321"
    )

    # Update product average cost
    update_average_cost(item.produto_id, quantidade_recebida, item.preco_unitario)

# If fully received, close PO
if all(item.quantidade_recebida >= item.quantidade_pedida for item in po.itens):
    po.status = "RECEBIDO"
```

### 3.4 Requisição de Compra (Purchase Requisition)

**Purpose:** Internal request to purchase (approval workflow)

**RequisicaoCompra Attributes:**
- `solicitante_id` - Requester user
- `data_requisicao` - Request date
- `justificativa` - Justification
- `urgencia` - Priority (BAIXA, MEDIA, ALTA, URGENTE)
- `status` - Status (PENDENTE, APROVADA, REPROVADA)
- `aprovador_id` - Approver user
- `data_aprovacao` - Approval date

**Approval Workflow:**
```
User (field manager) → Requisition → Approver (farm manager) → Approved → Procurement → PO
```

**Approval Rules:**
- < R$ 1,000: Auto-approved
- R$ 1,000 - R$ 10,000: Farm manager approval
- > R$ 10,000: Owner approval
- Urgent requests: Fast-track approval

## Integration Points

### With Agricola Module
- **Field Operations:** Equipment used in agricola operations (OS)
- **Input Consumption:** Fertilizer, pesticide from estoque → safra costs
- **Harvest Storage:** Grain romaneios → inventory (grain in storage)

### With Pecuaria Module
- **Feed Inventory:** Ration, supplements, minerals
- **Medication Inventory:** Vaccines, dewormers, antibiotics
- **Equipment:** Cattle handling equipment, milking machines

### With Financeiro Module
- **Inventory Valuation:** Stock value for balance sheet
- **Purchase Costs:** Pedido compra → Despesa (AP)
- **Depreciation:** Equipment depreciation schedules
- **Maintenance Costs:** OS costs → operating expenses

### With Core Module
- **Module Access:** O1_FROTA, O2_ESTOQUE, O3_COMPRAS subscriptions
- **Permissions:** `operacional:frota:view`, `operacional:compras:create`
- **Tenant Isolation:** All data scoped to tenant_id

## Common Workflows

### 1. Complete Purchase Process
```
1. User creates Requisição (need fertilizer)
2. Manager approves requisição
3. Procurement creates Cotação (send to 3 suppliers)
4. Suppliers respond with quotes
5. Procurement compares and selects winner
6. Create Pedido de Compra
7. Send PO to supplier
8. Supplier delivers goods
9. Receive goods, verify quantity/quality
10. Create Movimentação Estoque (ENTRADA)
11. Update inventory, average cost
12. Create Despesa in Financeiro (for payment)
```

### 2. Preventive Maintenance Cycle
```
1. System checks hourmeter daily
2. Detects maintenance due (250h oil change)
3. Auto-creates Ordem de Serviço (PREVENTIVA)
4. Assigns to technician
5. Technician changes oil, filters
6. Records parts used (links to estoque)
7. Updates inventory (oil, filters consumed)
8. Closes OS
9. Creates RegistroManutencao
10. Updates PlanoManutencao.ultimo_registro_horas
11. Costs allocated to equipment (depreciation schedule)
```

### 3. Breakdown Repair
```
1. Operator reports problem (tractor won't start)
2. Create OS (CORRETIVA)
3. Technician diagnoses (starter motor failure)
4. Check estoque for spare part (starter motor)
5. If not in stock → Create Requisição → Emergency PO
6. Install part, test equipment
7. Record parts + labor in OS
8. Update inventory
9. Close OS
10. Equipment back in service
11. Calculate downtime impact (lost productivity hours)
```

## Key Performance Indicators (KPIs)

### Fleet Management
- **Fleet Availability:** (Total hours - Downtime) / Total hours * 100%
- **Maintenance Cost per Hour:** Total maintenance cost / Total hours operated
- **Fuel Efficiency:** Liters per hectare worked
- **Mean Time Between Failures (MTBF):** Operating hours / Number of breakdowns
- **Planned vs Unplanned Maintenance Ratio:** Target 80:20

### Inventory Management
- **Stock Turnover:** COGS / Average Inventory (higher = better)
- **Days of Supply:** (Current stock / Average daily consumption)
- **Stockout Rate:** (Stockouts / Total requisitions) * 100%
- **Inventory Accuracy:** (Physical count / System count) * 100%
- **Slow-Moving Items:** Items with turnover < 2x per year

### Procurement
- **Purchase Order Cycle Time:** Days from requisition to PO
- **Delivery Time Compliance:** % of POs delivered on time
- **Price Variance:** (Actual price - Budgeted price) / Budgeted price
- **Supplier Quality:** % of receipts without quality issues
- **Cost Savings:** Savings from quotation process vs list price

## Testing Guidelines

```python
def test_maintenance_due_alert():
    maquinario = create_tractor(horimetro_atual=250)
    plano = create_maintenance_plan(frequencia_horas=250, ultimo_registro=0)

    alerts = check_maintenance_due(maquinario)

    assert len(alerts) == 1
    assert alerts[0].tipo == "PREVENTIVA"

def test_inventory_average_cost():
    produto = create_produto(quantidade=100, custo_medio=10)

    # Purchase 50 units @ R$ 12
    add_purchase(produto, quantidade=50, custo=12)

    assert produto.quantidade_estoque == 150
    assert produto.custo_medio == pytest.approx(10.67, rel=0.01)

def test_cannot_issue_more_than_stock():
    produto = create_produto(quantidade_estoque=100)

    with pytest.raises(BusinessRuleError):
        issue_product(produto, quantidade=150)
```

## Troubleshooting

### Inventory Discrepancies
- Conduct physical count
- Identify source of discrepancy (theft, damage, measurement error)
- Create adjustment transaction with proper justification
- Investigate patterns (same product always short = systematic issue)

### Equipment Downtime
- Analyze failure patterns (which equipment, which component)
- Review maintenance compliance (preventive maintenance skipped?)
- Evaluate parts quality (cheap parts = frequent failures)
- Training needs (operator error causing breakdowns?)

### Late Deliveries
- Review supplier performance (chronic late deliveries → find alternative)
- Increase lead time buffer in planning
- Negotiate better terms or penalties
- Consider safety stock for critical items

## References

- [operacional/ module](../../services/api/operacional/) - All operacional models
- [constants.py](../../services/api/core/constants.py) - Module IDs: O1-O3
- Inventory management: ABC analysis, EOQ (Economic Order Quantity)
- Fleet management: TPM (Total Productive Maintenance), FMEA
- Brazilian accounting: CPC 27 (IAS 16) - Fixed Assets, CPC 16 (IAS 2) - Inventories
