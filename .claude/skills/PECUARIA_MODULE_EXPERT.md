# Pecuaria Module Expert - AgroSaaS

You are a specialist in the **Pecuaria (Livestock/Cattle) Module** of AgroSaaS, responsible for livestock management, reproduction, feeding, and animal health.

## Module Overview

The Pecuaria module manages cattle operations from birth to sale, including individual animal tracking, herd management, reproduction, feeding programs, and health protocols.

**Module IDs (for module access control):**
- `P1_REBANHO` - Basic herd tracking (individual animals, lots, pasture)
- `P2_GENETICA` - Reproductive genetics (IATF, genealogy, breeding values)
- `P3_CONFINAMENTO` - Feedlot operations (ration formulation, feed delivery, performance)
- `P4_LEITE` - Dairy operations (milk production, milk quality, lactation curves)

## Submodules Structure

Location: [services/api/pecuaria/](../../services/api/pecuaria/)

### Core Models

**Location:** [services/api/pecuaria/models/](../../services/api/pecuaria/models/)

### 1. Lotes (Lots/Batches)
**Purpose:** Group animals by category, age, or management strategy

**Key Model:** [pecuaria/models/lote.py](../../services/api/pecuaria/models/lote.py)

**LoteBovino Attributes:**
- `identificacao` - Lot name/code
- `categoria` - Category (BEZERROS, NOVILHAS, VACAS, TOUROS, BOIS)
- `raca` - Breed (NELORE, ANGUS, BRAHMAN, CRUZAMENTO)
- `quantidade_cabecas` - Head count
- `peso_medio_kg` - Average weight
- `piquete_id` - Current pasture location
- `data_formacao` - Lot formation date

**Lot Categories:**
- BEZERROS - Calves (0-12 months)
- BEZERRAS - Heifer calves
- NOVILHOS - Young steers (12-24 months)
- NOVILHAS - Young heifers (breeding replacements)
- VACAS - Cows (breeding females)
- TOUROS - Bulls (breeding males)
- BOIS - Steers (castrated males for slaughter)

**Business Logic:**
- Lot weight updated on weighing events
- Head count updated on animal movements (birth, death, sale, purchase)
- Automatic lot splitting when animals diverge (e.g., separation by weight)
- Performance tracking: GMD (Average Daily Gain) = (final_weight - initial_weight) / days

**Common Operations:**
```python
# Create lot
lote = LoteBovino(
    tenant_id=tenant_id,
    fazenda_id=fazenda_id,
    identificacao="Lote Desmama 2024",
    categoria="BEZERROS",
    raca="NELORE",
    quantidade_cabecas=150,
    peso_medio_kg=180,
    piquete_id=piquete_id
)

# Update after weighing
lote.peso_medio_kg = 220  # 40kg gain
days = (date.today() - lote.data_formacao).days
gmd = (220 - 180) / days  # kg/day
```

### 2. Piquetes (Pastures/Paddocks)
**Purpose:** Pasture management and rotational grazing

**Key Model:** [pecuaria/models/piquete.py](../../services/api/pecuaria/models/piquete.py)

**Piquete Attributes:**
- `nome` - Pasture name
- `area_ha` - Area in hectares
- `capacidade_ua` - Capacity in Animal Units (UA)
- `tipo_pastagem` - Forage type (BRAQUIARIA, TIFTON, MOMBAÇA)
- `status` - Status (DISPONIVEL, OCUPADO, DESCANSO, REFORMA)
- `data_ultimo_pastejo` - Last grazing date
- `geometria` - Geospatial polygon (optional, links to talhao)

**Pasture Types:**
- BRAQUIARIA - Brachiaria grass species
- MOMBAÇA - Mombasa grass (high yield)
- TIFTON - Tifton grass (high quality)
- TANZÂNIA - Tanzania grass
- CAPIM_ELEFANTE - Elephant grass
- AVEIA - Oats (winter)
- AZEVÉM - Ryegrass (winter)

**Rotational Grazing:**
- Track occupation: current lot + entry date
- Calculate stocking rate: UA/ha
- Rest period tracking (recommended: 28-35 days)
- Forage availability estimation

**Stocking Calculations:**
```python
# Animal Unit (UA) = 450kg live weight reference
# Calculate UA from actual weight
ua_per_animal = peso_medio_kg / 450

# Total UA in pasture
total_ua = lote.quantidade_cabecas * ua_per_animal

# Stocking rate
stocking_rate = total_ua / piquete.area_ha  # UA/ha

# Check capacity
if total_ua > piquete.capacidade_ua:
    raise BusinessRuleError("Piquete overcapacity")
```

### 3. Manejos (Livestock Handling/Management)
**Purpose:** Record all animal handling events

**Key Model:** [pecuaria/models/manejo.py](../../services/api/pecuaria/models/manejo.py)

**Manejo Types:**

**A. Sanitário (Health/Veterinary):**
- VACINACAO - Vaccination
- VERMIFUGACAO - Deworming
- APLICACAO_MEDICAMENTO - Medication
- TRATAMENTO_DOENCA - Disease treatment
- EXAME_CLINICO - Clinical examination

**B. Reprodutivo (Reproductive):**
- INSEMINACAO - Artificial insemination
- DIAGNOSTICO_GESTACAO - Pregnancy diagnosis
- PARTO - Calving
- DESMAMA - Weaning

**C. Nutricional (Nutritional):**
- SUPLEMENTACAO - Supplementation
- MUDANCA_DIETA - Diet change
- FORNECIMENTO_RACAO - Feed delivery

**D. Zootécnico (Zootechnical):**
- PESAGEM - Weighing
- MARCACAO - Marking/tattooing
- CASTRACAO - Castration
- DESCORNA - Dehorning

**E. Movimentação (Movement):**
- ENTRADA - Entry (purchase, birth)
- SAIDA - Exit (sale, death, transfer)
- MUDANCA_PIQUETE - Pasture rotation

**Manejo Record Structure:**
```python
manejo = Manejo(
    tenant_id=tenant_id,
    lote_id=lote_id,
    tipo="VACINACAO",
    data_realizacao=date.today(),
    observacoes="Febre aftosa - dose anual",
    produto_utilizado="Vacina Aftosa Biovet",
    quantidade_aplicada=150,  # doses
    responsavel_tecnico="Dr. João Silva - CRMV 12345"
)
```

**Vaccination Protocols:**
- Track vaccination calendar per animal category
- Alert for upcoming vaccinations
- Link to product batch (rastreability)
- Regulatory compliance (MAPA)

**Key Vaccinations (Brazil):**
- Febre Aftosa (Foot-and-mouth disease) - Required by law
- Brucelose (Brucellosis) - Heifers 3-8 months
- Raiva (Rabies) - Endemic areas
- Clostridioses (Clostridial diseases)
- IBR/BVD (Respiratory/reproductive viruses)

### 4. Rastreabilidade Individual (Individual Traceability)
**Module:** P1_REBANHO (basic), enhanced in P2_GENETICA

**Purpose:** Individual animal tracking (required for export markets)

**Individual Animal Attributes:**
- SISBOV tag number (Brazil's traceability system)
- Electronic ear tag (RFID)
- Birth date and dam/sire
- Weight history (growth curve)
- Health records (vaccinations, treatments)
- Genealogy (if P2_GENETICA module)

**Export Requirements:**
- EU: 18-month traceability (birth to slaughter)
- China: SISBOV certification mandatory
- Hilton Quota: Individual tracking with genetics data

**Traceability Chain:**
```
Birth → Weaning → Vaccinations → Weighings → Movements → Pre-sale Exam → Sale → Transport
```

### 5. Reprodução (Reproduction)
**Module:** P2_GENETICA

**Purpose:** Breeding program management

**Reproductive Protocols:**

**A. IATF (Timed Artificial Insemination):**
- Protocol: D0 → D8 → D9 (hormone synchronization)
- Bull selection by breeding value
- Pregnancy diagnosis (30-60 days post-AI)
- Conception rate tracking

**B. Natural Breeding:**
- Bull-to-cow ratio (1:25 to 1:30)
- Bull rotation
- Breeding season definition
- Calving season planning

**Reproductive Metrics:**
- Taxa de concepção (Conception rate)
- Taxa de prenhez (Pregnancy rate)
- Taxa de parição (Calving rate)
- Taxa de desmama (Weaning rate)
- Intervalo entre partos (Calving interval) - target: 12-13 months

**Calving Management:**
```python
# Record calving event
parto = Manejo(
    tipo="PARTO",
    data_realizacao=date.today(),
    observacoes="Parto normal, bezerra fêmea",
    peso_nascimento_kg=32,
    mae_id=vaca_id,
    sexo_cria="FEMEA"
)

# Update herd inventory
lote_bezerras.quantidade_cabecas += 1

# Schedule weaning (6-8 months)
scheduled_weaning = date.today() + timedelta(days=210)
```

**Genetic Evaluation:**
- DEP (Expected Progeny Difference) - genetic merit
- MGT (Molecular Genetic Testing) - DNA markers
- Breeding value for: weight, carcass, fertility, temperament

### 6. Confinamento (Feedlot Operations)
**Module:** P3_CONFINAMENTO

**Purpose:** Intensive feeding for finishing cattle

**Feedlot Phases:**
1. **Adaptação (Adaptation):** 14-21 days, gradual diet transition
2. **Crescimento (Growth):** High-energy diet, muscle development
3. **Terminação (Finishing):** Maximum weight gain, fat deposition
4. **Pré-abate (Pre-slaughter):** Final adjustments

**Diet Formulation:**
- Roughage % (silage, hay)
- Concentrate % (corn, soy meal)
- Protein content (12-14% crude protein)
- Minerals and vitamins
- Additives (ionophores, growth promoters)

**Feed Delivery:**
- TMR (Total Mixed Ration) preparation
- Feed bunk management (empty every 24h)
- Dry matter intake (DMI) tracking: 2-3% of body weight
- Feed efficiency: kg feed / kg gain (target: 6-7:1)

**Performance Monitoring:**
```python
# Calculate feedlot performance
confinamento = {
    "peso_entrada": 350,  # kg
    "peso_saida": 550,     # kg
    "dias_confinado": 100,
    "consumo_total_ms": 2100  # kg dry matter
}

ganho_total = 550 - 350  # 200kg
gmd = ganho_total / 100  # 2.0 kg/day
conversao = 2100 / 200   # 10.5:1 (feed:gain)
```

**Cost Tracking:**
- Feed cost ($/kg gain)
- Medication and supplements
- Labor
- Equipment depreciation
- Total cost of gain (COG)

### 7. Pecuária Leiteira (Dairy Operations)
**Module:** P4_LEITE

**Purpose:** Milk production management

**Milk Production Tracking:**
- Daily production per cow (liters/day)
- Lactation curve (305-day standard)
- Peak production date
- Persistency (lactation curve shape)

**Milk Quality:**
- CCS (Somatic Cell Count) - mastitis indicator (target: <200,000/ml)
- CBT (Total Bacterial Count) - hygiene indicator (target: <100,000/ml)
- Fat % (target: 3.5-4.5%)
- Protein % (target: 3.0-3.5%)
- Milk temperature at collection

**Payment System:**
- Base price per liter
- Quality bonuses (low CCS/CBT)
- Volume bonuses
- Composition bonuses (fat/protein)
- Penalties (high CCS/CBT, low temperature)

**Milking Management:**
- Milking frequency (2x or 3x per day)
- Parlor throughput (cows/hour)
- Pre-dipping and post-dipping
- Teat condition scoring

**Lactation Curve:**
```python
# Wood's curve model: y = a * t^b * e^(-c*t)
# t = days in milk (DIM)
# Peak production typically at 40-60 DIM

def lactation_curve(dim, a, b, c):
    return a * (dim ** b) * math.exp(-c * dim)

# Example: Project 305-day production
total_milk_305 = sum(lactation_curve(day, a, b, c) for day in range(1, 306))
```

**Reproductive Management (Dairy):**
- Voluntary waiting period: 60 days post-calving
- Heat detection (activity monitors, visual)
- AI timing: 12-18h after heat onset
- Pregnancy check: 30-40 days post-AI
- Dry period: 60 days before next calving

## Integration Points

### With Agricola Module
- **Shared Talhões:** Pastures used for both crops and grazing
- **Silage Production:** Corn/sorghum safra → cattle feed
- **Crop Residue:** Grazing on crop stubble after harvest
- **Pasture Rotation:** Crop-livestock integration (ILPF)

### With Financeiro Module
- **Animal Purchase/Sale:** Revenue and costs
- **Feed Costs:** Ration, supplements, minerals
- **Veterinary Costs:** Medications, vaccines, services
- **Depreciation:** Bulls, dairy cows (breeding stock)

### With Operacional Module
- **Feed Inventory:** Estoque module for feed ingredients
- **Equipment:** Mixer wagons, feed trucks, milking equipment
- **Purchase Orders:** Feed suppliers, medications

### With Core Module
- **Module Access:** Requires P1_REBANHO (base) + optional P2/P3/P4
- **Permissions:** `pecuaria:lotes:view`, `pecuaria:manejos:create`
- **Tenant Isolation:** All data scoped to tenant_id via BaseService

## Key Business Rules

### 1. Lot Management
- Cannot have negative head count
- Cannot have lot without assigned piquete (if status = OCUPADO)
- Weight must be positive
- Category must match age range (e.g., BEZERROS < 12 months)

### 2. Pasture Capacity
- Total AU cannot exceed piquete capacity
- Minimum rest period before re-grazing (28 days for tropical grass)
- Warn if stocking rate > 2 AU/ha (overgrazing risk)

### 3. Health Protocols
- Vaccination calendar enforced (e.g., Aftosa every 6 months)
- Withdrawal period respected (meat/milk) after medication
- Veterinary prescription required for antibiotics

### 4. Reproduction
- Minimum breeding age: 15 months (heifers), 24 months (bulls)
- Pregnancy length: 283 days average
- Minimum calving interval target: 365 days

### 5. Feedlot Performance
- Maximum DMI: 3.5% of body weight
- Target ADG (average daily gain): 1.5-2.0 kg/day
- Alert if feed conversion > 8:1 (inefficient)

### 6. Milk Quality
- CCS > 500,000 → Mandatory treatment protocol
- CBT > 300,000 → Review hygiene procedures
- Temperature > 7°C → Cooling system failure alert

## Common Workflows

### 1. Complete Cattle Cycle (Beef)
```
1. Purchase weaned calves (8 months, 180kg)
2. Create Lote → Categoria: BEZERROS
3. Manejo: ENTRADA (record purchase)
4. Manejo: VACINACAO (initial protocol)
5. Assign to Piquete (pasture growth phase)
6. Manejo: PESAGEM (monthly weighing)
7. Monitor GMD (target: 0.6-0.8 kg/day on pasture)
8. At 18 months / 350kg → Enter feedlot (P3)
9. Feedlot diet (100 days, target: 2.0 kg/day)
10. Final weight: 550kg
11. Manejo: SAIDA (sale to slaughterhouse)
12. Calculate profitability
```

### 2. IATF Protocol (P2_GENETICA)
```
Day 0: Insert progesterone implant + IM injection (eCG)
Day 8: Remove implant + IM injection (PGF2α)
Day 9: IM injection (GnRH)
Day 10: Artificial insemination (48-52h after implant removal)
Day 40: Pregnancy diagnosis (ultrasound)
If pregnant → Schedule next protocol for 60 days post-calving
If open → Re-sync or natural breeding
```

### 3. Rotational Grazing
```
1. Divide farm into 20 piquetes (5% of farm each)
2. Calculate stocking rate (total AU / area)
3. Move lote every 3 days (occupation period)
4. Each piquete rests 57 days (19 x 3 days)
5. Track forage availability
6. Adjust occupation period based on forage growth
7. Monitor animal performance (GMD)
```

### 4. Dairy Production Day
```
Morning Milking:
1. Pre-dipping (iodine solution)
2. Forestrip (check mastitis)
3. Attach milking units
4. Automatic detachment (flow <0.5 L/min)
5. Post-dipping
6. Record production per cow (electronic ID)
7. Collect composite sample (quality testing)
8. Feed TMR after milking (to keep cows standing)

Evening Milking: Repeat

Daily Tasks:
- Check CCS/CBT alerts
- Review production vs expectations
- Identify cows for AI (heat detection)
- Calculate feed needed for tomorrow
```

## Performance Metrics (KPIs)

### Beef Cattle
- **GMD (Average Daily Gain):** 0.6-0.8 kg/day (pasture), 1.5-2.0 kg/day (feedlot)
- **Feed Conversion:** 6-8:1 (feedlot)
- **Carcass Yield:** 52-58%
- **Pregnancy Rate:** >85%
- **Weaning Rate:** >80%
- **Mortality:** <2% per year

### Dairy Cattle
- **Milk Production:** 20-30 L/cow/day (average herd)
- **Lactation 305 days:** 6,000-9,000 L
- **CCS:** <200,000 cells/ml
- **CBT:** <100,000 CFU/ml
- **Calving Interval:** 12-13 months
- **Conception Rate (AI):** >40%

### Pasture Management
- **Stocking Rate:** 1.0-2.0 AU/ha (varies by region/season)
- **Rest Period:** 28-35 days (tropical grass)
- **Forage Availability:** 2,500-3,000 kg DM/ha at entry

## Testing Guidelines

### Business Logic Tests
```python
def test_lot_weight_cannot_be_negative():
    with pytest.raises(ValidationError):
        lote = LoteBovino(peso_medio_kg=-10)

def test_cannot_exceed_pasture_capacity():
    piquete = Piquete(capacidade_ua=50)
    lote = LoteBovino(quantidade_cabecas=200, peso_medio_kg=450)  # 200 UA

    with pytest.raises(BusinessRuleError):
        assign_lot_to_pasture(lote, piquete)
```

### Performance Calculations
```python
def test_gmd_calculation():
    initial_weight = 180
    final_weight = 220
    days = 50

    gmd = calculate_gmd(initial_weight, final_weight, days)

    assert gmd == 0.8  # kg/day
```

## Troubleshooting

### Low GMD (Gain Performance)
- Check pasture quality (forage availability)
- Review health status (parasites, diseases)
- Verify supplementation program
- Check water availability and quality

### High CCS (Mastitis)
- Review milking hygiene protocols
- Check milking equipment (vacuum, pulsation)
- Evaluate bedding quality
- Implement segregated milking (high CCS last)
- Culture milk samples (identify pathogen)

### Low Conception Rate
- Verify bull fertility (semen quality)
- Check cow body condition score (target: 3.0-3.5)
- Review heat detection accuracy
- Evaluate AI timing
- Check for reproductive diseases (IBR, BVD)

### Pasture Degradation
- Reduce stocking rate
- Allow longer rest periods
- Over-seeding with improved forage
- Soil fertility correction (lime, fertilizer)
- Control weeds and invasive species

## Regulatory Compliance (Brazil)

### MAPA (Ministry of Agriculture)
- Mandatory vaccinations (Aftosa, Brucelose)
- Movement permits (GTA - Guia de Trânsito Animal)
- SISBOV registration (for export)
- Health certifications

### Environmental
- CAR registration (Rural Environmental Registry)
- Water use permits
- Riparian buffer compliance
- Waste management (manure, carcasses)

### Traceability
- Individual identification (SISBOV)
- Vaccination records
- Movement history
- Treatment records (antibiotics)

## References

- [pecuaria/ module](../../services/api/pecuaria/) - All pecuaria models
- [constants.py](../../services/api/core/constants.py) - Module IDs: P1-P4
- MAPA regulations: IN 17/2006 (SISBOV), IN 42/2018 (GTA)
- Beef Cattle Nutrition: NRC 2000, BR-CORTE
- Dairy Cattle Nutrition: NRC 2001
