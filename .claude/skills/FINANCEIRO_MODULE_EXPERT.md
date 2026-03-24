# Financeiro Module Expert - AgroSaaS

You are a specialist in the **Financeiro (Financial) Module** of AgroSaaS, responsible for cash flow, accounts payable/receivable, cost accounting, and financial reporting for farm operations.

## Module Overview

The Financeiro module manages all financial aspects of farm operations with a focus on agricultural economics, cost centers, and profitability analysis by crop/livestock.

**Module IDs (for module access control):**
- `F1_TESOURARIA` - Cash flow, AP/AR, bank reconciliation
- `F2_CUSTOS_ABC` - ABC costing, cost allocation, profitability by talhao/safra
- `F3_FISCAL` - Tax compliance, SPED, NF-e integration
- `F4_HEDGING` - Commodity hedging, futures, barter operations

## Submodules Structure

Location: [services/api/financeiro/](../../services/api/financeiro/)

### Core Models

**Location:** [services/api/financeiro/models/](../../services/api/financeiro/models/)

### 1. Plano de Contas (Chart of Accounts)
**Purpose:** Structured account classification for agricultural operations

**Key Model:** [financeiro/models/plano_conta.py](../../services/api/financeiro/models/plano_conta.py)

**Account Structure:**
```
1. RECEITAS (Revenue)
  1.1 Receita de Vendas
    1.1.1 Venda de Grãos
      1.1.1.1 Soja
      1.1.1.2 Milho
      1.1.1.3 Trigo
    1.1.2 Venda de Gado
    1.1.3 Venda de Leite
  1.2 Outras Receitas
    1.2.1 Arrendamento de Terras
    1.2.2 Prestação de Serviços

2. DESPESAS (Expenses)
  2.1 Custeio Agrícola
    2.1.1 Sementes
    2.1.2 Defensivos
    2.1.3 Fertilizantes
    2.1.4 Combustível
  2.2 Custeio Pecuário
    2.2.1 Ração
    2.2.2 Sal Mineral
    2.2.3 Medicamentos Veterinários
  2.3 Despesas Operacionais
    2.3.1 Mão de Obra
    2.3.2 Energia Elétrica
    2.3.3 Manutenção de Máquinas
  2.4 Despesas Administrativas
  2.5 Despesas Financeiras
    2.5.1 Juros de Empréstimos
    2.5.2 Tarifas Bancárias

3. INVESTIMENTOS (Assets)
  3.1 Terras
  3.2 Benfeitorias
  3.3 Máquinas e Equipamentos
  3.4 Animais de Produção (Reprodutores)
```

**Account Attributes:**
- `codigo` - Account code (e.g., "2.1.1.1")
- `nome` - Account name
- `tipo` - Type (RECEITA, DESPESA, ATIVO, PASSIVO)
- `nivel` - Hierarchy level (1-5)
- `conta_pai_id` - Parent account (for hierarchy)
- `aceita_lancamento` - Can post transactions (leaf accounts only)
- `centro_custo_obrigatorio` - Requires cost center

**Agricultural-Specific Accounts:**
- Cost centers by: Talhão, Safra, Lote (animal), Activity
- Rateio (cost allocation) rules
- Seasonal patterns (harvest revenue, planting expenses)

### 2. Despesas (Expenses / Accounts Payable)
**Purpose:** Track all farm expenses and supplier invoices

**Key Model:** [financeiro/models/despesa.py](../../services/api/financeiro/models/despesa.py)

**Despesa Attributes:**
- `plano_conta_id` - Chart of accounts classification
- `descricao` - Description
- `valor_total` - Total amount
- `data_emissao` - Invoice date
- `data_vencimento` - Due date
- `data_pagamento` - Payment date (null if unpaid)
- `status` - Status (A_PAGAR, PAGO, ATRASADO, CANCELADO)
- `fornecedor` - Supplier name
- `nota_fiscal` - Invoice number
- `fazenda_id` - Farm (for cost center)

**Status Workflow:**
```
A_PAGAR (unpaid) → PAGO (paid)
             ↓
        ATRASADO (overdue if data_vencimento < today)
             ↓
        CANCELADO (cancelled)
```

**Payment Methods:**
- DINHEIRO - Cash
- CHEQUE - Check
- TRANSFERENCIA - Bank transfer
- BOLETO - Bank slip (Brazil)
- CARTAO - Credit card
- BARTER - Commodity exchange

**Cost Allocation:**
```python
# Link expense to multiple cost centers (rateio)
despesa = Despesa(
    descricao="Fertilizante NPK - 10 toneladas",
    valor_total=50000,
    plano_conta_id=fertilizantes_id,
    fazenda_id=fazenda_id
)

# Allocate to safras (ABC costing)
rateios = [
    Rateio(despesa_id=despesa.id, safra_id=safra_soja_id, percentual=60),  # R$ 30k
    Rateio(despesa_id=despesa.id, safra_id=safra_milho_id, percentual=40)   # R$ 20k
]
```

### 3. Receitas (Revenue / Accounts Receivable)
**Purpose:** Track sales and revenue

**Key Model:** Similar structure to Despesa

**Receita Attributes:**
- `plano_conta_id` - Revenue account
- `descricao` - Description
- `valor_total` - Total amount
- `data_emissao` - Sale date
- `data_vencimento` - Expected receipt date
- `data_recebimento` - Actual receipt date
- `status` - Status (A_RECEBER, RECEBIDO, ATRASADO)
- `cliente` - Customer name
- `nota_fiscal` - Invoice number (NF-e)

**Agricultural Revenue Sources:**
- Grain sales (linked to Romaneio)
- Cattle sales (linked to Lote)
- Milk sales (daily production)
- Land lease (arrendamento)
- Service provision (machinery rental)

**Revenue Recognition:**
```python
# Example: Soy harvest sale
romaneio = Romaneio(
    safra_id=safra_id,
    peso_liquido_kg=60000,  # 1000 bags
    preco_por_saca=120.00
)

receita = Receita(
    descricao=f"Venda Soja - Romaneio {romaneio.numero}",
    valor_total=120000,  # 1000 bags * R$ 120
    plano_conta_id=venda_soja_id,
    data_emissao=date.today(),
    data_vencimento=date.today() + timedelta(days=30),  # 30-day payment term
    safra_id=safra_id  # Link to safra for profitability
)
```

### 4. Rateio (Cost Allocation)
**Purpose:** Distribute shared costs across multiple cost centers

**Key Model:** [financeiro/models/rateio.py](../../services/api/financeiro/models/rateio.py)

**Rateio Methods:**

**A. By Percentage:**
```python
# Allocate diesel fuel across safras
rateios = [
    {"safra_id": safra_soja_id, "percentual": 50},
    {"safra_id": safra_milho_id, "percentual": 30},
    {"safra_id": safra_trigo_id, "percentual": 20}
]
```

**B. By Area (Hectare):**
```python
# Allocate fixed costs by planted area
total_area = 1000  # ha
for safra in safras:
    percentual = (safra.area_plantada_ha / total_area) * 100
    create_rateio(despesa_id, safra_id, percentual)
```

**C. By Production (Activity-Based):**
```python
# Allocate machinery depreciation by hours used
total_hours = 500
for operacao in operacoes:
    percentual = (operacao.horas_trabalhadas / total_hours) * 100
    create_rateio(despesa_id, operacao.safra_id, percentual)
```

**Validation:**
- Sum of percentages must equal 100%
- Cannot allocate to deleted/inactive entities
- Audit trail (who created, when, why)

### 5. Fluxo de Caixa (Cash Flow)
**Module:** F1_TESOURARIA

**Purpose:** Daily cash position and projections

**Cash Flow Categories:**
- **Operational:** Day-to-day farm operations
- **Investment:** Equipment, land, infrastructure
- **Financing:** Loans, interest payments

**Cash Flow Statement:**
```
Opening Balance: R$ 100,000
+ Receipts (Receitas):
  - Grain sales: R$ 250,000
  - Cattle sales: R$ 80,000
  - Milk sales: R$ 30,000
- Payments (Despesas):
  - Suppliers: R$ 120,000
  - Payroll: R$ 40,000
  - Loan payment: R$ 50,000
= Closing Balance: R$ 250,000
```

**Projection (90 days):**
- Scheduled AP/AR
- Recurring expenses (payroll, utilities)
- Seasonal patterns (harvest revenue, planting expenses)
- Alert for negative cash position

**Bank Reconciliation:**
- Import bank statements (OFX format)
- Auto-match transactions (by value, date, description)
- Manual reconciliation for unmatched items
- Flag discrepancies

### 6. DRE (Income Statement)
**Module:** F1_TESOURARIA

**Purpose:** Profit & Loss by period

**Agricultural DRE Structure:**
```
RECEITA BRUTA
  Venda de Grãos
  Venda de Gado
  Venda de Leite
  (-) Devoluções e Cancelamentos
= RECEITA LÍQUIDA

(-) CUSTO DOS PRODUTOS VENDIDOS (CPV)
  Custeio Agrícola Direto
  Custeio Pecuário Direto
= LUCRO BRUTO

(-) DESPESAS OPERACIONAIS
  Mão de Obra Fixa
  Energia e Combustível
  Manutenção
  Administrativas
= LUCRO OPERACIONAL (EBIT)

(-) DESPESAS FINANCEIRAS
  Juros de Empréstimos
(+) RECEITAS FINANCEIRAS
  Rendimentos de Aplicações
= LUCRO ANTES DOS IMPOSTOS (LAIR)

(-) IMPOSTOS
= LUCRO LÍQUIDO
```

**Agricultural Adjustments:**
- **Inventory Valuation:** Grain in storage (market price vs cost)
- **Biological Assets:** Growing crops, maturing animals (IAS 41)
- **Depreciation:** Straight-line or units of production (machinery)
- **Prepaid Expenses:** Seeds, fertilizer purchased for next season

### 7. Custos por Safra (Crop Profitability)
**Module:** F2_CUSTOS_ABC

**Purpose:** Detailed cost analysis per crop/field

**Cost Structure:**
```python
safra_analysis = {
    "safra_id": safra_soja_id,
    "area_ha": 500,
    "producao_sacas": 75000,  # 150 bags/ha

    "custos_variaveis": {
        "sementes": 45000,      # R$ 90/ha
        "defensivos": 100000,   # R$ 200/ha
        "fertilizantes": 150000,  # R$ 300/ha
        "combustivel": 25000,   # R$ 50/ha
        "total": 320000         # R$ 640/ha
    },

    "custos_fixos": {
        "mao_obra": 50000,      # R$ 100/ha
        "deprec_maquinas": 25000,  # R$ 50/ha
        "arrendamento": 75000,  # R$ 150/ha (if leased)
        "total": 150000         # R$ 300/ha
    },

    "custo_total": 470000,      # R$ 940/ha
    "custo_por_saca": 6.27,     # R$ 470k / 75k bags

    "receita_bruta": 900000,    # 75k bags * R$ 12/bag
    "receita_por_ha": 1800,

    "lucro_bruto": 430000,      # R$ 900k - R$ 470k
    "margem_bruta": 47.78,      # %
    "lucro_por_ha": 860,
    "lucro_por_saca": 5.73
}
```

**Profitability Metrics:**
- **Break-even Point:** Cost per bag = Sale price
- **Break-even Yield:** Cost per ha / Price per bag
- **Return on Investment (ROI):** (Profit / Total Cost) * 100
- **Gross Margin:** ((Revenue - Variable Costs) / Revenue) * 100

**Benchmarking:**
- Compare with industry averages
- Historical trends (3-5 year average)
- Regional comparisons

### 8. Empréstimos e Financiamentos (Loans & Financing)
**Module:** F1_TESOURARIA

**Purpose:** Agricultural credit management

**Loan Types (Brazil):**
- **Custeio:** Operating loan for crop inputs (1 season)
- **Investimento:** Investment loan for equipment, infrastructure (5-10 years)
- **Comercialização:** Marketing loan (grain storage, delayed sale)

**Government Programs:**
- **PRONAF:** Family farming credit (subsidized rates)
- **PRONAMP:** Medium-sized farm credit
- **MODERFROTA:** Machinery financing
- **PSI Rural:** BNDES rural credit

**Loan Structure:**
```python
loan = {
    "tipo": "CUSTEIO",
    "banco": "Banco do Brasil",
    "programa": "PRONAMP",
    "valor_principal": 500000,
    "taxa_juros_aa": 6.5,  # % per year
    "prazo_meses": 12,
    "carencia_meses": 6,
    "garantias": ["Penhor de safra", "Hipoteca de terra"],

    "parcelas": [
        {"vencimento": "2025-01-15", "principal": 0, "juros": 2708},  # grace period
        {"vencimento": "2025-07-15", "principal": 250000, "juros": 1354},
        {"vencimento": "2026-01-15", "principal": 250000, "juros": 677}
    ]
}
```

**Interest Calculation:**
- Simple interest (most custeio loans)
- Compound interest (most investment loans)
- Inflation-linked (IPCA + rate)

**Amortization Methods:**
- SAC (Sistema de Amortização Constante) - Constant principal
- PRICE (Tabela Price) - Constant payment
- Balloon payment - Pay at harvest

### 9. Barter Operations
**Module:** F4_HEDGING

**Purpose:** Input purchase with grain payment

**Barter Flow:**
```
1. Farmer needs fertilizer for 500 ha
2. Supplier offers: 10 tons fertilizer = 1000 bags of soy (at harvest)
3. Contract: Deliver 1000 bags of soy on Nov 15
4. Record as:
   - Despesa: R$ 50,000 (fertilizer at current price)
   - Receita Diferida: R$ 60,000 (soy at futures price)
   - Obligation: Deliver 1000 bags
5. At harvest:
   - Deliver soy to supplier
   - Close barter contract
   - Recognize profit/loss vs market price
```

**Accounting Treatment:**
- Record expense at input acquisition
- Record deferred revenue at futures price
- Track physical obligation (bags to deliver)
- Mark-to-market at balance sheet date

**Risk Management:**
- Price risk (soy price drops → loss on barter)
- Production risk (crop failure → cannot deliver)
- Counterparty risk (supplier default)

### 10. Commodity Hedging
**Module:** F4_HEDGING

**Purpose:** Price risk management using futures markets

**Hedging Instruments:**
- **Futures Contracts:** B3 (Brazil), CBOT (Chicago)
- **Options:** Call/put options on futures
- **Forward Contracts:** Direct with buyers
- **CPR (Cédula de Produto Rural):** Brazilian agro-bond

**Hedge Example:**
```python
# Farmer plants 500 ha soy, expects 75,000 bags at harvest (Nov)
# Current futures price (May): R$ 120/bag
# Farmer locks in 50% of production

hedge = {
    "data_operacao": "2024-05-01",
    "instrumento": "FUTURE_SOY_NOV24",
    "quantidade_sacas": 37500,  # 50% of expected production
    "preco_contrato": 120,
    "margem_requerida": 225000,  # 5% of notional (37,500 * 120)

    "cenario_1_preco_cai": {
        "preco_mercado_nov": 100,
        "receita_fisica": 3750000,  # 37,500 * 100
        "ganho_hedge": 750000,      # 37,500 * (120 - 100)
        "receita_total": 4500000    # Locked in R$ 120/bag
    },

    "cenario_2_preco_sobe": {
        "preco_mercado_nov": 140,
        "receita_fisica": 5250000,  # 37,500 * 140
        "perda_hedge": -750000,     # 37,500 * (120 - 140)
        "receita_total": 4500000    # Still R$ 120/bag (opportunity cost)
    }
}
```

**Hedge Effectiveness:**
- Correlation between cash and futures prices
- Basis risk (local price vs futures price)
- Roll yield (contango/backwardation)

### 11. Fiscal Compliance (Tax)
**Module:** F3_FISCAL

**Purpose:** Brazilian tax compliance for rural producers

**Tax Regimes:**
- **Simples Nacional:** Simplified tax (revenue < R$ 4.8MM)
- **Lucro Presumido:** Presumed profit (8-32% of revenue)
- **Lucro Real:** Actual profit (full accounting required)

**Taxes:**
- **ICMS:** State VAT on sales (varies by state, 7-18%)
- **FUNRURAL:** Social security on rural revenue (1.2% + 0.1%)
- **IRPJ:** Corporate income tax (15% + 10% surcharge)
- **CSLL:** Social contribution (9%)

**Tax Benefits for Agriculture:**
- ICMS exemption for primary production (some states)
- Reduced FUNRURAL for family farming
- Depreciation incentives (special rates)

**Electronic Documents:**
- **NF-e:** Electronic invoice for sales
- **CT-e:** Electronic transport document
- **MDF-e:** Multi-modal manifest
- **EFD ICMS/IPI:** Digital tax bookkeeping (SPED)

### 12. Financial Reporting
**Module:** F1_TESOURARIA, F2_CUSTOS_ABC

**Standard Reports:**

**A. Cash Flow Report:**
- Daily, weekly, monthly cash position
- 30/60/90 day projection
- AP aging (overdue analysis)
- AR aging (collection analysis)

**B. DRE (Income Statement):**
- Monthly comparison (actual vs budget)
- Year-to-date accumulation
- Previous year comparison

**C. Balance Sheet:**
- Assets: Cash, AR, inventory (grain/cattle), fixed assets
- Liabilities: AP, loans, deferred taxes
- Equity: Capital, retained earnings

**D. Cost Analysis Reports:**
- Cost per hectare by input category
- Cost per bag/liter/kg produced
- Profitability by talhao/safra/lote
- Budget vs actual variance

**E. Tax Reports:**
- SPED EFD-ICMS/IPI
- DCTF (federal tax declaration)
- DIRF (withholding tax)
- GFIP (payroll social security)

## Integration Points

### With Agricola Module
- **Safra Costs:** All agricola operations → financial transactions
- **Romaneios:** Harvest revenue recognition
- **Input Consumption:** Fertilizer, pesticide usage → inventory and expenses

### With Pecuaria Module
- **Animal Sales:** Cattle revenue
- **Feed Costs:** Ration, supplements → cost of production
- **Milk Sales:** Daily revenue recognition

### With Operacional Module
- **Inventory:** Stock valuation (FIFO, weighted average)
- **Equipment:** Depreciation schedules
- **Maintenance:** Maintenance costs → OpEx

### With Core Module
- **Subscriptions:** Module F1, F2, F3, F4 access control
- **Permissions:** `financeiro:despesas:create`, `financeiro:relatorios:view`
- **Tenant Isolation:** Financial data scoped to tenant_id

## Common Workflows

### 1. Monthly Closing Process
```
1. Reconcile bank accounts
2. Accrue unpaid expenses (competência)
3. Recognize earned revenue
4. Depreciation calculation
5. Inventory valuation (grain, inputs, animals)
6. Generate DRE
7. Generate Balance Sheet
8. Tax calculation
9. Management reports
10. Lock period (prevent backdated changes)
```

### 2. Harvest Revenue Recognition
```
1. Romaneio created (agricola module)
2. Calculate net weight (moisture/impurity adjustments)
3. Auto-create Receita:
   - Description: "Venda Soja - Romaneio #123"
   - Amount: net_weight_bags * price_per_bag
   - Account: 1.1.1.1 (Venda Soja)
   - Link to safra (for profitability)
4. Update safra.custo_realizado (if expenses allocated)
5. Calculate profit margin
6. Generate NF-e (if F3_FISCAL module active)
```

### 3. Cost Allocation (ABC)
```
1. Record expense (e.g., diesel fuel)
2. Identify cost centers (safras using machinery)
3. Choose allocation method:
   - By area planted
   - By machine hours
   - By fuel consumption
4. Create rateio records
5. Update each safra.custo_realizado_ha
6. Recalculate profitability
```

## Key Financial Metrics (Farm-Specific)

### Liquidity Ratios
- **Current Ratio:** Current Assets / Current Liabilities (target: > 1.5)
- **Quick Ratio:** (Cash + AR) / Current Liabilities
- **Cash Conversion Cycle:** Days (inventory + AR - AP)

### Profitability Ratios
- **Gross Margin:** (Revenue - COGS) / Revenue (target: > 35%)
- **Operating Margin:** EBIT / Revenue
- **Net Margin:** Net Income / Revenue
- **ROA (Return on Assets):** Net Income / Total Assets
- **ROE (Return on Equity):** Net Income / Equity

### Efficiency Ratios
- **Asset Turnover:** Revenue / Total Assets
- **Inventory Turnover:** COGS / Average Inventory
- **AR Turnover:** Revenue / Average AR (Days Sales Outstanding)

### Agricultural-Specific
- **Cost per Hectare:** Total Costs / Hectares Planted
- **Revenue per Hectare:** Total Revenue / Hectares
- **Cost per Unit Produced:** Total Costs / Bags (or kg, liters)
- **Break-even Yield:** Fixed Costs / (Price - Variable Cost per unit)

## Testing Guidelines

### Financial Calculation Tests
```python
def test_rateio_sum_equals_100_percent():
    despesa = create_despesa(valor=1000)
    rateios = [
        {"safra_id": s1, "percentual": 40},
        {"safra_id": s2, "percentual": 60}
    ]

    assert sum(r["percentual"] for r in rateios) == 100

def test_break_even_calculation():
    fixed_costs = 100000  # R$/ha
    variable_costs = 640  # R$/ha
    price_per_bag = 120   # R$/bag

    break_even_yield = (fixed_costs + variable_costs) / price_per_bag

    assert break_even_yield == pytest.approx(6.17)  # bags/ha
```

### Business Logic Tests
```python
def test_cannot_pay_expense_twice():
    despesa = create_despesa(status="A_PAGAR")
    pay_expense(despesa.id, date.today())

    assert despesa.status == "PAGO"

    with pytest.raises(BusinessRuleError):
        pay_expense(despesa.id, date.today())  # Already paid
```

## Troubleshooting

### Cash Flow Discrepancies
- Verify all transactions reconciled with bank
- Check for duplicate entries
- Ensure all AR/AP included in projection
- Review reclassifications (transfers between accounts)

### Profitability Analysis Issues
- Verify all costs allocated to correct safra
- Check rateio percentages sum to 100%
- Ensure inventory valuation method consistent
- Review depreciation schedules (assets fully depreciated?)

### Tax Calculation Errors
- Verify tax rates updated for current year
- Check exemptions/reductions properly applied
- Ensure tax base calculated correctly (gross vs net revenue)
- Review withholding tax calculations

## Brazilian Agricultural Accounting Standards

### CPC 29 (IAS 41) - Biological Assets
- **Fair Value:** Market price - selling costs
- **Gains/Losses:** Changes in fair value → income statement
- **Disclosure:** Reconciliation of biological assets (beginning, purchases, gains, sales, ending)

### Examples:
- **Growing Crops:** Mark-to-market at balance sheet date
- **Breeding Cattle:** Fair value (market price for similar animals)
- **Milk Cows:** Productive asset, depreciate over useful life

## References

- [financeiro/ module](../../services/api/financeiro/) - All financeiro models
- [constants.py](../../services/api/core/constants.py) - Module IDs: F1-F4
- CPC 29 (IAS 41) - Biological Assets
- Brazilian tax law: Lei 8.023/1990 (FUNRURAL), Lei 9.430/1996 (IRPJ/CSLL)
- SPED: Sistema Público de Escrituração Digital
- Rural accounting: Custos Agrícolas (Marion, 2014)
