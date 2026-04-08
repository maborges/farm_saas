# Plano Técnico — Hierarquia Completa + Agricultura de Precisão

**Data:** 2026-04-06
**Base conceitual:** `docs/contexts/core/cadastro-propriedade-conceitos.md`

---

## 1. Hierarquia Territorial Alvo (5 níveis)

```
PROPRIEDADE (territorial — jurídico)          ← nível 0
└── GLEBA (territorial — geográfico)           ← nível 1
    └── TALHAO (operacional — manejo)          ← nível 2
        └── SUBTALHAO (técnico — ajuste)       ← nível 3
            └── ZONA_DE_MANEJO (analítico)     ← nível 4
```

### Regras de Hierarquia Válida

| Pai | Filhos permitidos |
|-----|------------------|
| `PROPRIEDADE` | `GLEBA`, `TALHAO`, `PASTAGEM`, `APP`, `RESERVA_LEGAL`, `UNIDADE_PRODUTIVA`, `SEDE`, `ARMAZEM`, `INFRAESTRUTURA`, `AREA` |
| `GLEBA` | `TALHAO`, `PASTAGEM`, `APP`, `RESERVA_LEGAL`, `AREA` |
| `UNIDADE_PRODUTIVA` | `TALHAO`, `PASTAGEM`, `AREA` |
| `TALHAO` | `SUBTALHAO`, `PIQUETE` |
| `SUBTALHAO` | `ZONA_DE_MANEJO` |
| `ZONA_DE_MANEJO` | _(nenhum — nível folha)_ |
| `PASTAGEM` | `PIQUETE` |
| `PIQUETE` | _(nenhum)_ |
| `APP`, `RESERVA_LEGAL` | _(nenhum)_ |
| `AREA` | `SUBTALHAO`, `ZONA_DE_MANEJO` |
| `SEDE`, `ARMAZEM`, `INFRAESTRUTURA` | _(nenhum)_ |

---

## 2. Mudanças no Backend

### 2.1. Enum `TipoArea` — 2 novos tipos

**Arquivo:** `services/api/core/cadastros/propriedades/models.py`

```python
class TipoArea(str, enum.Enum):
    # ─── TERRITORIAL ───
    PROPRIEDADE       = "PROPRIEDADE"
    GLEBA             = "GLEBA"

    # ─── AGRUPAMENTO ADMINISTRATIVO ───
    UNIDADE_PRODUTIVA = "UNIDADE_PRODUTIVA"
    AREA              = "AREA"

    # ─── OPERACIONAL ───
    TALHAO            = "TALHAO"
    PASTAGEM          = "PASTAGEM"
    PIQUETE           = "PIQUETE"

    # ─── TÉCNICO (NOVO) ───
    SUBTALHAO         = "SUBTALHAO"         # Zona de variação interna ao talhão

    # ─── ANALÍTICO (NOVO) ───
    ZONA_DE_MANEJO    = "ZONA_DE_MANEJO"    # Unidade de prescrição VRA

    # ─── AMBIENTAL ───
    APP               = "APP"
    RESERVA_LEGAL     = "RESERVA_LEGAL"

    # ─── INFRAESTRUTURA ───
    ARMAZEM           = "ARMAZEM"
    SEDE              = "SEDE"
    INFRAESTRUTURA    = "INFRAESTRUTURA"
```

### 2.2. Colunas de Agricultura de Precisão em `AreaRural`

**Arquivo:** `services/api/core/cadastros/propriedades/models.py`

```python
class AreaRural(Base):
    # ... colunas existentes ...

    # ─── NOVOS: Agricultura de Precisão ───
    tipo_solo: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="LATOSSOLO, ARGISSOLO, NEOSSOLO, CAMBISSOLO, etc."
    )
    teor_argila: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True, comment="%"
    )
    teor_areia: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True, comment="%"
    )
    ph_solo: Mapped[float | None] = mapped_column(
        Numeric(4, 2), nullable=True, comment="pH CaCl2"
    )
    materia_organica_pct: Mapped[float | None] = mapped_column(
        Numeric(4, 2), nullable=True, comment="%"
    )
    condutividade_eletrica: Mapped[float | None] = mapped_column(
        Numeric(6, 2), nullable=True, comment="mS/m"
    )
    produtividade_media_ha: Mapped[float | None] = mapped_column(
        Numeric(8, 2), nullable=True, comment="sacas/ha ou ton/ha"
    )
    cultura_atual: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Cultura/uso atual (nível TALHAO)"
    )
    irrigado: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, default=False
    )
    nivel_profundidade: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0,
        comment="0=Prop, 1=Gleba, 2=Talhão, 3=Subtalhão, 4=Zona"
    )
```

### 2.3. Novo Modelo: `HistoricoUsoTalhao`

Responde à dimensão **TEMPORAL**: "terra é fixa, uso muda".

```python
class HistoricoUsoTalhao(Base):
    """
    Histórico de uso do talhão ao longo do tempo.
    Suporta ILP (Integração Lavoura-Pecuária) e rotação de culturas.
    """
    __tablename__ = "cadastros_areas_historico_uso"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    area_rural_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True
    )
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date | None] = mapped_column(Date, nullable=True, comment="NULL = uso atual")
    tipo_uso: Mapped[str] = mapped_column(String(50), nullable=False, comment="SOJA, MILHO, PASTAGEM, BRAQUIARIA, etc.")
    cultivar: Mapped[str | None] = mapped_column(String(100), nullable=True)
    produtividade_obtida: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True, comment="sacas/ha")
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    area_rural: Mapped["AreaRural"] = relationship(back_populates="historico_uso", lazy="noload")
```

### 2.4. Novo Modelo: `AmostraSolo`

Base científica para zonas de manejo.

```python
class AmostraSolo(Base):
    __tablename__ = "cadastros_amostras_solo"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    area_rural_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_areas_rurais.id", ondelete="SET NULL"), nullable=True, index=True
    )
    latitude: Mapped[float] = mapped_column(Numeric(10, 8), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(11, 8), nullable=False)
    profundidade_cm: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    data_coleta: Mapped[date] = mapped_column(Date, nullable=False)
    ph_cacl2: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    materia_organica: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    fosforo_mg_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    potassio_cmolc_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    calcio_cmolc_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    magnesio_cmolc_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    aluminio_cmolc_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    h_aluminio_cmolc_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    ctc_cmolc_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    saturacao_base_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True, comment="V%")
    argila_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    areia_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    silte_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    tipo_solo_classificacao: Mapped[str | None] = mapped_column(String(50), nullable=True)
    laboratorio: Mapped[str | None] = mapped_column(String(100), nullable=True)
    numero_laudo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    area_rural: Mapped["AreaRural"] = relationship(back_populates="amostras_solo", lazy="noload")
```

### 2.5. Relationships em `AreaRural`

```python
    historico_uso: Mapped[list["HistoricoUsoTalhao"]] = relationship(
        back_populates="area_rural", lazy="noload", cascade="all, delete-orphan",
        order_by="HistoricoUsoTalhao.data_inicio.desc()"
    )
    amostras_solo: Mapped[list["AmostraSolo"]] = relationship(
        back_populates="area_rural", lazy="noload", cascade="all, delete-orphan"
    )
```

---

## 3. Service — Validação de Hierarquia

**Arquivo:** `services/api/core/cadastros/propriedades/service.py`

```python
HIERARQUIA_VALIDA = {
    "PROPRIEDADE":       {"GLEBA", "TALHAO", "PASTAGEM", "APP", "RESERVA_LEGAL", "UNIDADE_PRODUTIVA", "SEDE", "ARMAZEM", "INFRAESTRUTURA", "AREA"},
    "GLEBA":             {"TALHAO", "PASTAGEM", "APP", "RESERVA_LEGAL", "AREA"},
    "UNIDADE_PRODUTIVA": {"TALHAO", "PASTAGEM", "AREA"},
    "TALHAO":            {"SUBTALHAO", "PIQUETE"},
    "SUBTALHAO":         {"ZONA_DE_MANEJO"},
    "ZONA_DE_MANEJO":    set(),
    "PASTAGEM":          {"PIQUETE"},
    "PIQUETE":           set(),
    "APP":               set(),
    "RESERVA_LEGAL":     set(),
    "AREA":              {"SUBTALHAO", "ZONA_DE_MANEJO"},
    "SEDE":              set(),
    "ARMAZEM":           set(),
    "INFRAESTRUTURA":    set(),
}

NIVEL_PROFUNDO = {
    "PROPRIEDADE": 0, "GLEBA": 1, "UNIDADE_PRODUTIVA": 1,
    "TALHAO": 2, "PASTAGEM": 2, "APP": 1, "RESERVA_LEGAL": 1,
    "AREA": 2, "SUBTALHAO": 3, "ZONA_DE_MANEJO": 4,
    "PIQUETE": 3, "SEDE": 1, "ARMAZEM": 1, "INFRAESTRUTURA": 1,
}

class AreaRuralService(BaseService[AreaRural]):
    # ... métodos existentes ...

    async def validar_hierarquia(self, parent_id: uuid.UUID | None, tipo_filho: str) -> None:
        if parent_id is None:
            if tipo_filho != "PROPRIEDADE":
                raise BusinessRuleError(
                    f"Área do tipo {tipo_filho} não pode ser raiz. "
                    "Apenas PROPRIEDADE pode ser criada sem parent_id."
                )
            return

        pai = await self.get_or_fail(parent_id)
        permitidos = HIERARQUIA_VALIDA.get(pai.tipo, set())
        if tipo_filho not in permitidos:
            raise BusinessRuleError(
                f"Não é possível criar {tipo_filho} dentro de {pai.tipo}. "
                f"Filhos permitidos: {sorted(permitidos)}"
            )
```

### Métodos adicionais no Service

```python
    async def calcular_soma_areas(self, parent_id: uuid.UUID) -> dict:
        """Soma das áreas dos filhos diretos."""
        areas = await self.listar(parent_id=parent_id, apenas_ativos=True)
        soma = sum(a.area_hectares or a.area_hectares_manual or 0 for a in areas)
        return {
            "soma_areas_filhas_ha": round(soma, 4),
            "numero_filhos": len(areas),
            "areas": [{"id": str(a.id), "nome": a.nome, "tipo": a.tipo,
                       "area_ha": a.area_hectares or a.area_hectares_manual} for a in areas]
        }

    async def obter_arvore(self, area_id: uuid.UUID) -> dict:
        """Árvore hierárquica completa a partir de uma área."""
        raiz = await self.obter_com_filhos(area_id)
        def montar(area: AreaRural) -> dict:
            return {
                "id": str(area.id), "tipo": area.tipo, "nome": area.nome,
                "codigo": area.codigo, "area_ha": area.area_hectares or area.area_hectares_manual,
                "nivel": NIVEL_PROFUNDO.get(area.tipo, 0),
                "dados_precisao": {
                    "tipo_solo": area.tipo_solo, "teor_argila": area.teor_argila,
                    "ph_solo": area.ph_solo, "produtividade_media": area.produtividade_media_ha,
                } if area.tipo in ("SUBTALHAO", "ZONA_DE_MANEJO", "TALHAO") else None,
                "filhos": [montar(f) for f in area.filhos if f.ativo],
            }
        return montar(raiz)
```

---

## 4. Router — Novos Endpoints

**Arquivo:** `services/api/core/cadastros/propriedades/router.py`

### 4.1. Validação no POST existente

```python
@router.post("", response_model=AreaRuralResponse, status_code=201)
async def criar(data: AreaRuralCreate, session=Depends(get_session), tenant_id=Depends(get_tenant_id)):
    svc = AreaRuralService(AreaRural, session, tenant_id)
    await svc.validar_hierarquia(data.parent_id, data.tipo)  # ← NOVO
    return await svc.criar_area(data.model_dump())
```

### 4.2. Novos endpoints

```python
@router.get("/{area_id}/arvore", response_model=dict)
async def obter_arvore(area_id: uuid.UUID, ...):
    """Retorna a sub-árvore hierárquica."""
    svc = AreaRuralService(AreaRural, session, tenant_id)
    return await svc.obter_arvore(area_id)

@router.get("/{area_id}/soma-areas")
async def soma_areas(area_id: uuid.UUID, ...):
    """Soma das áreas dos filhos diretos (validação RN-CP-004)."""
    svc = AreaRuralService(AreaRural, session, tenant_id)
    return await svc.calcular_soma_areas(area_id)

@router.get("/{area_id}/historico-uso", response_model=list[HistoricoUsoResponse])
async def listar_historico(area_id: uuid.UUID, ...): ...

@router.post("/{area_id}/historico-uso", response_model=HistoricoUsoResponse, status_code=201)
async def criar_historico(area_id: uuid.UUID, data: HistoricoUsoCreate, ...): ...

@router.get("/{area_id}/amostras-solo", response_model=list[AmostraSoloResponse])
async def listar_amostras(area_id: uuid.UUID, ...): ...

@router.post("/{area_id}/amostras-solo", response_model=AmostraSoloResponse, status_code=201)
async def criar_amostra(area_id: uuid.UUID, data: AmostraSoloCreate, ...): ...
```

---

## 5. Schemas Pydantic

**Arquivo:** `services/api/core/cadastros/propriedades/schemas.py`

### 5.1. Expandir `AreaRuralCreate`

```python
class AreaRuralCreate(BaseModel):
    # ... campos existentes ...
    # NOVOS:
    tipo_solo: Optional[str] = Field(None, max_length=50)
    teor_argila: Optional[float] = Field(None, gt=0, le=100)
    teor_areia: Optional[float] = Field(None, gt=0, le=100)
    ph_solo: Optional[float] = Field(None, gt=0, le=14)
    materia_organica_pct: Optional[float] = Field(None, gt=0, le=100)
    condutividade_eletrica: Optional[float] = Field(None, gt=0)
    produtividade_media_ha: Optional[float] = Field(None, gt=0)
    cultura_atual: Optional[str] = Field(None, max_length=50)
    irrigado: Optional[bool] = False
```

### 5.2. Novos schemas

```python
class HistoricoUsoCreate(BaseModel):
    data_inicio: date
    data_fim: Optional[date] = None
    tipo_uso: str = Field(..., max_length=50)
    cultivar: Optional[str] = Field(None, max_length=100)
    produtividade_obtida: Optional[float] = None
    observacoes: Optional[str] = None

class HistoricoUsoResponse(BaseModel):
    id: uuid.UUID; data_inicio: date; data_fim: Optional[date]
    tipo_uso: str; cultivar: Optional[str]; produtividade_obtida: Optional[float]
    observacoes: Optional[str]; created_at: datetime
    model_config = {"from_attributes": True}

class AmostraSoloCreate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    profundidade_cm: float = Field(..., gt=0)
    data_coleta: date
    ph_cacl2: Optional[float] = Field(None, ge=0, le=14)
    materia_organica: Optional[float] = Field(None, ge=0)
    fosforo_mg_dm3: Optional[float] = Field(None, ge=0)
    potassio_cmolc_dm3: Optional[float] = Field(None, ge=0)
    calcio_cmolc_dm3: Optional[float] = Field(None, ge=0)
    magnesio_cmolc_dm3: Optional[float] = Field(None, ge=0)
    aluminio_cmolc_dm3: Optional[float] = Field(None, ge=0)
    h_aluminio_cmolc_dm3: Optional[float] = Field(None, ge=0)
    ctc_cmolc_dm3: Optional[float] = Field(None, ge=0)
    saturacao_base_pct: Optional[float] = Field(None, ge=0, le=100)
    argila_pct: Optional[float] = Field(None, ge=0, le=100)
    areia_pct: Optional[float] = Field(None, ge=0, le=100)
    silte_pct: Optional[float] = Field(None, ge=0, le=100)
    tipo_solo_classificacao: Optional[str] = Field(None, max_length=50)
    laboratorio: Optional[str] = Field(None, max_length=100)
    numero_laudo: Optional[str] = Field(None, max_length=50)

class AmostraSoloResponse(BaseModel):
    id: uuid.UUID; latitude: float; longitude: float; profundidade_cm: float
    data_coleta: date; ph_cacl2: Optional[float]; materia_organica: Optional[float]
    fosforo_mg_dm3: Optional[float]; potassio_cmolc_dm3: Optional[float]
    # ... demais campos ...
    created_at: datetime
    model_config = {"from_attributes": True}
```

---

## 6. Migration

```python
"""add_subtalhao_zona_manejo_precisao

Adiciona suporte a agricultura de precisão:
1. Novos tipos: SUBTALHAO, ZONA_DE_MANEJO
2. Colunas de precisão em cadastros_areas_rurais
3. Tabela cadastros_areas_historico_uso
4. Tabela cadastros_amostras_solo
5. Coluna nivel_profundidade
"""
```

---

## 7. Impacto em `PrescricaoVRA`

O modelo `PrescricaoVRA` já referencia `talhao_id → cadastros_areas_rurais`. Com `SUBTALHAO` e `ZONA_DE_MANEJO`:

- Prescrição por talhão → passa UUID do talhão ✅
- Prescrição por subtalhão → passa UUID do subtalhão ✅
- Prescrição por zona → passa UUID da zona ✅

**Adição recomendada:** campo `nivel_area` para documentar granularidade:

```python
nivel_area: Mapped[str] = mapped_column(
    String(20), default="TALHAO",
    comment="TALHAO, SUBTALHAO, ZONA_DE_MANEJO"
)
```

---

## 8. Frontend — Componentes Novos

| Componente | Arquivo | Descrição |
|------------|---------|-----------|
| `AreaTree` | `components/core/areas/AreaTree.tsx` | Árvore hierárquica expansível com ícones por tipo |
| `ZonaManejoDialog` | `components/core/areas/ZonaManejoDialog.tsx` | Form para subtalhão e zona de manejo |
| `HistoricoUsoTimeline` | `components/core/areas/HistoricoUsoTimeline.tsx` | Timeline de alternância de culturas |
| `AmostrasSoloMap` | `components/core/areas/AmostrasSoloMap.tsx` | Mapa com pontos de amostras sobre polígonos |
| `HierarquiaTab` | `app/(dashboard)/cadastros/propriedades/[id]/(tabs)/hierarquia/page.tsx` | Nova aba na página de detalhe |
| `AmostrasTab` | `app/(dashboard)/cadastros/propriedades/[id]/(tabs)/amostras/page.tsx` | Nova aba de amostras de solo |

---

## 9. Exemplo Completo de Uso

```
PROPRIEDADE: Fazenda Santa Maria (2500 ha, MT-Sorriso)
├── GLEBA: Gleba Norte (800 ha)
│   ├── TALHAO: Talhão 01 (120 ha) — cultura_atual: SOJA, irrigado: true
│   │   ├── SUBTALHAO: 01A — Argiloso (70 ha)
│   │   │   tipo_solo: LATOSSOLO, teor_argila: 65, ph_solo: 5.8
│   │   │   materia_organica: 3.2, condutividade: 45.2
│   │   │   produtividade_media: 65.0 sc/ha
│   │   │   ├── ZONA_DE_MANEJO: Alta Fertilidade (30 ha)
│   │   │   │   ph: 6.2, P: 15.5, K: 0.45, prod: 72.0
│   │   │   │   → Prescrição VRA: NPK 400kg/ha
│   │   │   └── ZONA_DE_MANEJO: Media Fertilidade (40 ha)
│   │   │       ph: 5.5, P: 8.2, K: 0.25, prod: 58.0
│   │   │       → Prescrição VRA: NPK 550kg/ha
│   │   └── SUBTALHAO: 01B — Arenoso (50 ha)
│   │       tipo_solo: NEOSSOLO, teor_areia: 75, ph: 4.8
│   │       prod: 42.0
│   │       → Prescrição VRA: Calcário 3ton/ha
│   └── TALHAO: Talhão 02 (200 ha) — cultura_atual: MILHO
└── RESERVA_LEGAL: Mata Ciliar (320 ha)

HistoricoUso do Talhão 01:
2022/23 → Soja (58 sc/ha)
2023    → Milho safrinha (75 sc/ha)
2023/24 → Soja (62 sc/ha)
2024    → Braquiária/ILP (18 UA/ha)
2024/25 → Soja (atual)
```
