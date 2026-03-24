# Agricola Module Expert - AgroSaaS

You are a specialist in the **Agricola (Crop/Agriculture) Module** of AgroSaaS, responsible for crop planning, field operations, precision agriculture, and harvest management.

## Module Overview

The Agricola module is the largest and most complex module in AgroSaaS, covering the complete crop production cycle from planning to harvest.

**Module IDs (for module access control):**
- `A1_PLANEJAMENTO` - Crop planning and budgeting
- `A2_CAMPO` - Field operations (work orders, field notes)
- `A3_DEFENSIVOS` - Crop protection and agronomist prescriptions
- `A4_PRECISAO` - Precision agriculture (NDVI, IoT, variable rate)
- `A5_COLHEITA` - Harvest and grain tickets (romaneios)

## Submodules Structure

Location: [services/api/agricola/](../../services/api/agricola/)

### 1. Talhões (Fields/Plots)
**Purpose:** Geospatial field/plot management

**Key Models:** [agricola/talhoes/models.py](../../services/api/agricola/talhoes/models.py)
- `Talhao` - Field polygon with geometry (PostGIS)
- Attributes: area_ha, cultura_atual, status, geometria (GeoJSON)

**Key Operations:**
- Create field with polygon geometry
- Calculate area automatically from geometry
- Track crop rotation history
- Link to fazenda and safra

**Geospatial Features:**
- Uses GeoAlchemy2 for PostGIS geometry
- Geometry stored as GeoJSON (EPSG:4326)
- Frontend uses MapLibre/Mapbox GL for visualization
- Drawing tools: Mapbox GL Draw

**Example:**
```python
talhao = Talhao(
    tenant_id=tenant_id,
    fazenda_id=fazenda_id,
    nome="Talhão 01A",
    geometria=Polygon([...]),  # GeoJSON polygon
    cultura_atual="SOJA",
    status="EM_USO"
)
# area_ha calculated automatically via PostGIS ST_Area
```

### 2. Safras (Crop Seasons/Harvests)
**Purpose:** Crop season planning and tracking

**Key Models:** [agricola/safras/models.py](../../services/api/agricola/safras/models.py)
- `Safra` - Crop season record
- Tracks: planned vs actual dates, productivity, costs, prices

**Lifecycle Stages:**
1. `PLANEJADA` - Planning stage
2. `PLANTADA` - Planting completed
3. `EM_DESENVOLVIMENTO` - Growing
4. `COLHEITA` - Harvesting
5. `FINALIZADA` - Completed
6. `CANCELADA` - Cancelled

**Key Fields:**
- `ano_safra` - Season identifier (e.g., "2024/2025")
- `cultura` - Crop type (SOJA, MILHO, TRIGO, etc.)
- `cultivar_id` - Seed variety
- `data_plantio_prevista` / `data_plantio_real`
- `data_colheita_prevista` / `data_colheita_real`
- `produtividade_meta_sc_ha` / `produtividade_real_sc_ha` - Productivity (bags/hectare)
- `custo_previsto_ha` / `custo_realizado_ha`

**Business Logic:**
- One safra per talhao per season (can't overlap dates)
- Area planted can't exceed talhao area
- Productivity calculated: total harvest / area_planted

### 3. Operações Agrícolas (Field Operations)
**Purpose:** Work orders and field activity tracking

**Key Models:** [agricola/operacoes/models.py](../../services/api/agricola/operacoes/models.py)
- `OrdemServico` - Work order (planting, spraying, fertilizing)
- `ApontamentoOperacao` - Operation execution record
- `InsumoAplicado` - Input applied (fertilizer, pesticide, seed)

**Operation Types:**
- PLANTIO - Planting
- PULVERIZACAO - Spraying
- ADUBACAO - Fertilization
- COLHEITA - Harvesting
- PREPARO_SOLO - Soil preparation
- IRRIGACAO - Irrigation
- CONTROLE_PRAGAS - Pest control

**Work Order Flow:**
1. Create OS (planned operation)
2. Assign to operator/agronomist
3. Execute in field (create apontamento)
4. Record inputs used (seeds, fertilizer, pesticides)
5. Update estoque (inventory) automatically
6. Link to safra for cost tracking

**Integration Points:**
- Links to `Maquinario` (operacional module) for equipment tracking
- Links to `Produto` (estoque) for input consumption
- Updates `Safra.custo_realizado_ha` automatically

### 4. Cadastros (Master Data)
**Purpose:** Reference data for agricultural operations

**Key Models:** [agricola/cadastros/models.py](../../services/api/agricola/cadastros/models.py)
- `Cultura` - Crop types (seed varieties, hybrids)
- `Praga` - Pests and diseases
- `DefensivoAgricola` - Pesticides/fungicides/herbicides

**Cultura Attributes:**
- Nome científico, nome comum
- Ciclo médio (days)
- Espaçamento recomendado
- População por hectare
- Zona climática ideal

**Defensive Attributes:**
- Classe toxicológica
- Período de carência (days)
- Dosagem recomendada
- Pragas alvo

### 5. Prescrições (Prescriptions/Recommendations)
**Purpose:** Agronomist prescriptions for variable rate application

**Module:** A3_DEFENSIVOS, A4_PRECISAO

**Key Models:** [agricola/prescricoes/models.py](../../services/api/agricola/prescricoes/models.py)
- `PrescricaoAgronomica` - Agronomist prescription
- `ZonaPrescricao` - Management zone with specific recommendation

**Prescription Types:**
- `ADUBACAO_VARIAVEL` - Variable rate fertilization
- `CALAGEM` - Liming
- `SEMEADURA_VARIAVEL` - Variable rate seeding
- `PULVERIZACAO` - Spraying

**Workflow:**
1. Agronomist analyzes soil/NDVI data
2. Creates prescription with zones
3. Each zone has specific product + dosage
4. Generates shapefile for precision equipment
5. Links to OrdemServico for execution
6. Tracks application vs prescription

**Regulatory:**
- Requires CREA registration number (agronomist)
- Links to defensive registration (MAPA)
- Respects withholding period (período de carência)

### 6. Análises de Solo (Soil Analysis)
**Purpose:** Soil sampling and laboratory results

**Key Models:** [agricola/analises_solo/models.py](../../services/api/agricola/analises_solo/models.py)
- `AmostraSolo` - Soil sample collection
- `ResultadoAnalise` - Lab results

**Analysis Types:**
- Física - Texture, density, porosity
- Química - pH, nutrients (N, P, K, Ca, Mg), CTC
- Biológica - Organic matter, microbial activity

**Sampling Pattern:**
- Grid sampling (precision ag)
- Zone-based sampling
- Random/representative sampling

**Integration:**
- Results feed into prescription generation
- Historical tracking for soil fertility evolution
- Links to talhao for geospatial visualization

### 7. NDVI (Vegetation Index)
**Purpose:** Satellite imagery and vegetation health monitoring

**Module:** A4_PRECISAO

**Key Models:** [agricola/ndvi/models.py](../../services/api/agricola/ndvi/models.py)
- `ImagemNDVI` - NDVI raster image
- `AnaliseVegetacao` - Vegetation analysis result

**Data Sources:**
- Sentinel-2 (free, 10m resolution, 5-day revisit)
- Landsat (free, 30m resolution, 16-day revisit)
- Planet Labs (paid, 3m resolution, daily)
- Drone imagery (custom)

**Indices Supported:**
- NDVI - Normalized Difference Vegetation Index
- NDRE - Normalized Difference Red Edge
- EVI - Enhanced Vegetation Index
- SAVI - Soil Adjusted Vegetation Index

**Use Cases:**
- Vigor monitoring
- Problem detection (stress, disease, pests)
- Variable rate application zones
- Yield prediction

### 8. Romaneios (Grain Tickets/Harvest Records)
**Purpose:** Harvest logistics and grain ticket management

**Module:** A5_COLHEITA

**Key Models:** [agricola/romaneios/models.py](../../services/api/agricola/romaneios/models.py)
- `Romaneio` - Grain ticket record
- Tracks: truck, driver, gross/tare/net weight, moisture, impurity

**Harvest Flow:**
1. Truck arrives at farm
2. Get gross weight (scale)
3. Record moisture % and impurities %
4. Unload grain
5. Get tare weight (empty truck)
6. Calculate net weight
7. Calculate price adjustments (moisture, quality)
8. Link to safra for productivity calculation

**Quality Parameters:**
- Umidade % (moisture) - affects payment
- Impurezas % (impurities) - affects payment
- PH (hectoliter weight) - quality indicator
- Quebrados % - broken grains

**Integration:**
- Updates Safra.produtividade_real
- Can integrate with scales via API/serial
- Generates fiscal documents (NF-e) via Financeiro module

### 9. Custos Agrícolas (Agricultural Costs)
**Purpose:** Cost tracking and profitability analysis

**Key Models:** [agricola/custos/models.py](../../services/api/agricola/custos/schemas.py)
- Cost schemas for analysis
- Links all operations to cost centers

**Cost Categories:**
- Sementes (seeds)
- Defensivos (crop protection)
- Fertilizantes (fertilizers)
- Combustível (fuel)
- Mão de obra (labor)
- Maquinário (equipment depreciation)
- Arrendamento (land lease)

**Cost Tracking:**
- Per hectare (R$/ha)
- Per bag produced (R$/saca)
- Per talhao
- Per safra
- Per cultura

**Profitability Metrics:**
- Custo total / hectare
- Receita total / hectare
- Margem bruta (gross margin)
- Ponto de equilíbrio (break-even)
- ROI per talhao

### 10. Monitoramento (Field Scouting/Monitoring)
**Purpose:** Field inspection and problem reporting

**Key Models:** [agricola/monitoramento/models.py](../../services/api/agricola/monitoramento/models.py)
- `Monitoramento` - Field inspection record
- Tracks: pest/disease occurrence, severity, georeferenced photos

**Scouting Types:**
- Pragas (pests)
- Doenças (diseases)
- Plantas daninhas (weeds)
- Deficiências nutricionais (nutrient deficiency)
- Estresse hídrico (water stress)

**Data Collection:**
- Mobile app (offline-first)
- GPS coordinates
- Photos with metadata
- Severity scale (1-5)
- Affected area estimation

**Workflow:**
1. Scout walks field with mobile app
2. Identifies problem
3. Takes photo (geotagged)
4. Estimates severity and area
5. System auto-creates alert
6. Agronomist reviews and prescribes treatment
7. Treatment becomes OrdemServico

### 11. Previsões (Weather & Yield Forecasting)
**Purpose:** Weather data and yield predictions

**Key Models:** [agricola/previsoes/models.py](../../services/api/agricola/previsoes/models.py)
- `PrevisaoTempo` - Weather forecast
- `PrevisaoSafra` - Yield prediction

**Weather Integration:**
- OpenWeather API
- INMET (Brazil's national weather institute)
- Weather stations (IoT)

**Weather Data:**
- Temperature (min/max)
- Rainfall (mm)
- Humidity %
- Wind speed
- Solar radiation

**Yield Prediction:**
- Machine learning based on:
  - Historical yield data
  - NDVI trends
  - Weather patterns
  - Soil analysis
  - Crop stage

### 12. Rastreabilidade (Traceability)
**Purpose:** Farm-to-fork traceability for export compliance

**Key Models:** [agricola/rastreabilidade/models.py](../../services/api/agricola/rastreabilidade/models.py)
- `LoteRastreavel` - Traceable lot
- Links: talhao → safra → operations → romaneios → sales

**Traceability Chain:**
```
Talhao → Safra → Operações (what was applied) → Romaneio (batch) → Venda → Export
```

**Compliance:**
- GAP (Good Agricultural Practices)
- Rainforest Alliance
- Organic certification
- EU regulations (deforestation-free)

**Data Required:**
- All inputs applied (with dosage, date)
- All operations performed
- Soil analysis results
- Harvest date and conditions
- Storage conditions
- Transport chain

### 13. Agrônomo (Agronomist Tools)
**Purpose:** Professional agronomist workspace

**Module:** A3_DEFENSIVOS

**Key Models:** [agricola/agronomo/models.py](../../services/api/agricola/agronomo/models.py)
- `ReceitaAgronomica` - Agronomist prescription (legal document)
- Requires: CREA registration, electronic signature

**Regulatory Requirements:**
- Receituário agronômico required for Class I/II pesticides
- Must include: farm, talhao, plague, product, dosage, safety instructions
- Digital signature (e-CREA)
- Retention period: 2 years

### 14. Dados Climáticos (Climate Data)
**Purpose:** Historical and real-time climate tracking

**Key Models:** [agricola/climatico/models.py](../../services/api/agricola/climatico/models.py)
- `DadoClimatico` - Climate measurement record
- `EstacaoMeteorologica` - Weather station

**Data Sources:**
- IoT weather stations (farm-installed)
- INMET public API
- OpenWeather API
- Satellite data

**Uses:**
- Irrigation scheduling
- Spray window detection
- Disease risk modeling
- Frost alerts
- Planting date optimization

## Key Business Rules

### 1. Safra Lifecycle
- Cannot plant if talhao already has active safra
- Cannot harvest before planting date
- Productivity calculation: (total_romaneios_kg / area_planted_ha) / 60kg (1 saca)

### 2. Chemical Application Rules
- Class I/II pesticides require receita agronômica
- Respect withholding period before harvest
- Track total dosage per hectare per season
- Alert if exceeding recommended limits

### 3. Geospatial Constraints
- Talhao geometry must be within fazenda boundaries
- Cannot overlap talhoes (same fazenda)
- Area calculation via PostGIS ST_Area (authoritative)
- All coordinates in EPSG:4326 (WGS84)

### 4. Cost Allocation
- All operations linked to safra accumulate costs
- Cost per hectare = total_cost / area_planted
- Link to financeiro for budget vs actual analysis

### 5. Quality Control (Romaneios)
- Standard moisture for soy: 14%
- Price adjustment formula: `net_weight * (1 - (moisture - 14) * 0.01) * price_per_bag`
- Impurity discount: `adjusted_weight * (1 - impurity_pct)`

## Integration Points

### With Core Module
- Requires `A1_PLANEJAMENTO`, `A2_CAMPO`, etc. modules via subscription
- Permission checks: `agricola:safras:create`, `agricola:talhoes:edit`
- Tenant isolation via BaseService

### With Financeiro Module
- Safra costs → financial transactions
- Romaneios → sales revenue
- Budget planning → cash flow projection

### With Operacional Module
- OrdemServico links to Maquinario (frota)
- Input consumption updates Estoque
- Maintenance schedules based on usage

### With Pecuaria Module
- Shared talhoes (pasture rotation)
- Silage production (corn → cattle feed)

## Common Workflows

### Complete Crop Season Workflow
```
1. Create Talhao (if new field)
2. Create Safra (planning)
   - Set cultura, area, target productivity
   - Set dates (planting, harvest)
   - Budget costs
3. Create OrdemServico: PREPARO_SOLO
4. Create OrdemServico: PLANTIO
   - Record InsumoAplicado (seeds)
5. Monitor with NDVI
6. Field scouting (Monitoramento)
   - Detect problem
7. Agronomist creates Prescricao
8. Create OrdemServico: PULVERIZACAO
   - Execute prescription
9. Create OrdemServico: ADUBACAO (if needed)
10. Harvest: Create Romaneios
    - Record yield, quality
11. Calculate productivity
12. Close Safra (status: FINALIZADA)
13. Cost analysis (budget vs actual)
```

### Precision Agriculture Workflow
```
1. Collect soil samples (grid pattern)
2. Send to lab → AnaliseResultado
3. Get NDVI imagery
4. Agronomist analyzes: soil + NDVI
5. Creates PrescricaoAgronomica with zones
   - Zone A: 300kg/ha NPK
   - Zone B: 400kg/ha NPK
   - Zone C: 350kg/ha NPK
6. Export shapefile for precision equipment
7. Execute variable rate application
8. Track results with NDVI time series
```

## Performance Considerations

1. **Geospatial Queries:**
   - Use spatial indices (PostGIS GIST)
   - Simplify geometries for large farms
   - Cache rendered tiles (frontend)

2. **NDVI Processing:**
   - Process asynchronously (Celery task)
   - Store pre-rendered tiles
   - Limit resolution for web display

3. **Cost Calculations:**
   - Cache aggregated costs per safra
   - Update on insert/update trigger
   - Avoid real-time SUM queries

4. **Romaneio Volume:**
   - High-volume during harvest season
   - Batch insert operations
   - Index: safra_id, data_entrada

## Testing Guidelines

### Geospatial Testing
```python
def test_talhao_area_calculation():
    # Create polygon (square 100m x 100m = 1 ha)
    geometry = Polygon([...])
    talhao = Talhao(geometria=geometry, ...)

    assert talhao.area_ha == pytest.approx(1.0, rel=0.01)
```

### Business Logic Testing
```python
def test_cannot_create_overlapping_safras():
    safra1 = create_safra(talhao_id, inicio="2024-01-01", fim="2024-06-01")

    with pytest.raises(BusinessRuleError):
        safra2 = create_safra(talhao_id, inicio="2024-05-01", fim="2024-10-01")
```

### Tenant Isolation Testing
```python
def test_cannot_access_other_tenant_safra():
    tenant_a_token = create_jwt(tenant_id=tenant_a)

    response = client.get(
        f"/safras/{tenant_b_safra_id}",
        headers={"Authorization": f"Bearer {tenant_a_token}"}
    )

    assert response.status_code == 404
```

## Troubleshooting

### Geometry Issues
- **Invalid geometry:** Use PostGIS ST_IsValid() to check
- **Wrong area calculation:** Ensure SRID is 4326, reproject if needed
- **Overlapping talhoes:** Use ST_Overlaps() to detect

### NDVI Processing Failures
- Check satellite image availability (cloud cover)
- Verify date range is within sensor coverage
- Ensure area is within satellite footprint

### Cost Discrepancies
- Verify all operations linked to correct safra
- Check if input prices updated correctly
- Ensure rateio (cost allocation) applied

### Performance Issues
- Add index on: safra.talhao_id, operacao.safra_id
- Use EXPLAIN ANALYZE for slow queries
- Consider partitioning romaneios table by year

## References

- [agricola/ module](../../services/api/agricola/) - All agricola submodules
- [constants.py](../../services/api/core/constants.py) - Module IDs and permissions
- Brazilian agricultural regulations: IN 02/2008 (Receituário Agronômico)
- PostGIS documentation for geospatial functions
