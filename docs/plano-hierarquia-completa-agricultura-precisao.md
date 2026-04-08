# Plano de Implementação — Hierarquia Completa + Agricultura de Precisão

**Data:** 2026-04-06
**Base conceitual:** `docs/contexts/core/cadastro-propriedade-conceitos.md`
**Status:** Proposta para revisão

---

## 1. Diagnóstico Conceitual

### Princípio Fundamental (do documento conceitual)

> **A terra é fixa. O uso da terra muda ao longo do tempo.**

O modelo atual `AreaRural` respeita parcialmente esse princípio. A hierarquia territorial funciona, mas:

1. **Não diferencia territorial de operacional** — `tipo` mistura gleba (territorial) com talhão (operacional) no mesmo enum
2. **Não diferencia operacional de temporal** — `dados_extras.cultura_atual` é um campo solto, sem histórico
3. **Falta o nível SUBTALHAO** — essencial para agricultura de precisão
4. **Falta o nível ZONA_DE_MANEJO** — unidade analítica para taxa variável

### Hierarquia Alvo (5 níveis)

```
PROPRIEDADE (territorial — jurídico)
└── GLEBA (territorial — geográfico)
    └── TALHAO (operacional — manejo)
        └── SUBTALHAO (técnico — ajuste operacional)
            └── ZONA_DE_MANEJO (analítico — agricultura de precisão)
```

### Regras de Hierarquia Válida

| Pai → Filho Permitidos | Exemplo |
|------------------------|---------|
| PROPRIEDADE → GLEBA | Fazenda → Gleba Norte |
| PROPRIEDADE → TALHAO | Fazenda → Talhão direto (sem gleba) |
| PROPRIEDADE → APP / RESERVA_LEGAL | Fazenda → Área de preservação |
| PROPRIEDADE → UNIDADE_PRODUTIVA | Fazenda → Bloco Norte (agrupamento) |
| GLEBA → TALHAO | Gleba Norte → Talhão 01 |
| GLEBA → APP / RESERVA_LEGAL | Gleba → APP do Rio |
| UNIDADE_PRODUTIVA → TALHAO | Bloco Norte → Talhão T-01 |
| UNIDADE_PRODUTIVA → PASTAGEM | Bloco Sul → Pastagem P-01 |
| TALHAO → SUBTALHAO | Talhão 01 → 01A (argiloso) |
| TALHAO → PIQUETE | Pastagem → Piquete 1 |
| SUBTALHAO → ZONA_DE_MANEJO | 01A → Zona Fértil |
| SUBTALHAO → SUBTALHAO | (não permitido — profundidade máx. 4) |
| PASTAGEM → PIQUETE | Pastagem P-01 → Piquete PQ-01 |

**Profundidade máxima:** 4 níveis (Propriedade → Gleba → Talhão → Subtalhão → Zona de Manejo)

---

## 2. Mudanças no Backend

### 2.1. Modelo — `models.py`

#### 2.1.1. Expandir `TipoArea`

```python
class TipoArea(str, enum.Enum):
    # ─── TERRITORIAL (espaço físico permanente) ───
    PROPRIEDADE       = "PROPRIEDADE"       # Imóvel rural (nível topo, tem matrícula)
    GLEBA             = "GLEBA"             # Parcela legal com matrícula própria

    # ─── AGRUPAMENTO ADMINISTRATIVO ───
    UNIDADE_PRODUTIVA = "UNIDADE_PRODUTIVA" # Agrupamento administrativo sem geometria
    AREA              = "AREA"              # Subdivisão genérica de unidade produtiva

    # ─── OPERACIONAL (onde ocorre o manejo) ───
    TALHAO            = "TALHAO"            # Unidade de plantio (polígono)
    PASTAGEM          = "PASTAGEM"          # Área de pastagem (polígono)
    PIQUETE           = "PIQUETE"           # Subdivisão de pastagem para rotação

    # ─── TÉCNICO (ajuste operacional dentro do talhão) ───
    SUBTALHAO         = "SUBTALHAO"         # Zona de variação interna ao talhão

    # ─── ANALÍTICO (agricultura de precisão) ───
    ZONA_DE_MANEJO    = "ZONA_DE_MANEJO"    # Unidade de prescrição VRA

    # ─── AMBIENTAL / LEGAL ───
    APP               = "APP"               # Área de Preservação Permanente
    RESERVA_LEGAL     = "RESERVA_LEGAL"     # Reserva Legal (Código Florestal)

    # ─── INFRAESTRUTURA ───
    ARMAZEM           = "ARMAZEM"           # Armazém / silo / galpão
    SEDE              = "SEDE"              # Sede administrativa / moradia
    INFRAESTRUTURA    = "INFRAESTRUTURA"    # Curral, aviário, pocilga, etc.
```

> **Novos tipos:** `SUBTALHAO`, `ZONA_DE_MANEJO`

#### 2.1.2. Adicionar colunas ao `AreaRural`

O modelo precisa de **colunas dedicadas para dados de agricultura de precisão** (ao invés de esconder tudo em `dados_extras`):

```python
class AreaRural(Base):
    # ... colunas existentes ...

    # ─── NOVOS: Dados de Agricultura de Precisão ───
    # Aplicável a: SUBTALHAO, ZONA_DE_MANEJO
    tipo_solo: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="Classificação de solo: LATOSSOLO, ARGISSOLO, NEOSSOLO, etc."
    )
    teor_argila: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True,
        comment="Teor de argila (%)"
    )
    teor_areia: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True,
        comment="Teor de areia (%)"
    )
    ph_solo: Mapped[float | None] = mapped_column(
        Numeric(4, 2), nullable=True,
        comment="pH do solo (CaCl2)"
    )
    materia_organica_pct: Mapped[float | None] = mapped_column(
        Numeric(4, 2), nullable=True,
        comment="Matéria orgânica (%)"
    )
    condutividade_eletrica: Mapped[float | None] = mapped_column(
        Numeric(6, 2), nullable=True,
        comment="Condutividade elétrica aparente (mS/m)"
    )
    produtividade_media_ha: Mapped[float | None] = mapped_column(
        Numeric(8, 2), nullable=True,
        comment="Produtividade média histórica (sacas/ha ou ton/ha)"
    )
    cultura_atual: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="Cultura/uso atual do talhão (para nível TALHAO)"
    )
    irrigado: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, default=False,
        comment="Se a área possui irrigação"
    )
```

> **Racional:** Colunas dedicadas permitem queries eficientes (ex: "todas as zonas com pH < 5.5") e índices. Manter tudo em `dados_extras` JSON inviabiliza análise espacial eficiente.

#### 2.1.3. Adicionar `nivel_profundidade` (validação)

```python
    nivel_profundidade: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0,
        comment="Nível na hierarquia: 0=Propriedade, 1=Gleba, 2=Talhão, 3=Subtalhão, 4=Zona"
    )
```

> Isso permite validação rápida e queries por nível sem precisar percorrer a árvore.

#### 2.1.4. Nova tabela: `HistoricoUsoTalhao`

Para resolver a **dimensão temporal** (conceito fundamental do documento):

```python
class HistoricoUsoTalhao(Base):
    """
    Histórico de uso do talhão ao longo do tempo.
    Resolve a dimensão TEMPORAL: território é fixo, uso muda.

    Um talhão pode ter múltiplos registros:
      2023/24 → Soja (safra verão)
      2024    → Milho (safrinha)
      2024/25 → Pastagem (ILP)
    """
    __tablename__ = "cadastros_areas_historico_uso"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    area_rural_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Período
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date | None] = mapped_column(Date, nullable=True, comment="NULL = uso atual")

    # Uso
    tipo_uso: Mapped[str] = mapped_column(String(50), nullable=False, comment="SOJA, MILHO, PASTAGEM, CANA, etc.")
    cultivar: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Cultivar/semente utilizada")
    produtividade_obtida: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True, comment="sacas/ha ou ton/ha")

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    area_rural: Mapped["AreaRural"] = relationship(back_populates="historico_uso", lazy="noload")
```

#### 2.1.5. Nova tabela: `AmostraSolo`

```python
class AmostraSolo(Base):
    """
    Amostra de solo georreferenciada vinculada a um talhão ou subtalhão.
    Base para zonas de manejo e prescrição VRA.
    """
    __tablename__ = "cadastros_amostras_solo"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    area_rural_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cadastros_areas_rurais.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Localização exata da amostra (ponto GPS)
    latitude: Mapped[float] = mapped_column(Numeric(10, 8), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(11, 8), nullable=False)
    profundidade_cm: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, comment="Profundidade da coleta (ex: 0-20cm)")

    # Análise laboratorial
    data_coleta: Mapped[date] = mapped_column(Date, nullable=False)
    ph_cacl2: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    materia_organica: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    fosforo_mg_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    potassio_cmolc_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    calcio_cmolc_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    magnesio_cmolc_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    aluminio_cmolc_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    h_aluminio_cmolc_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    ctc_cmolc_dm3: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True, comment="Capacidade Troca Catiônica")
    saturacao_base_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True, comment="V%")
    argila_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    areia_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    silte_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Classificação
    tipo_solo_classificacao: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Latossolo Vermelho distrófico, etc.")

    laboratorio: Mapped[str | None] = mapped_column(String(100), nullable=True)
    numero_laudo: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    area_rural: Mapped["AreaRural"] = relationship(back_populates="amostras_solo", lazy="noload")
```

#### 2.1.6. Adicionar relationships ao `AreaRural`

```python
    # Relationships (adicionar aos existentes)
    historico_uso: Mapped[list["HistoricoUsoTalhao"]] = relationship(
        back_populates="area_rural", lazy="noload", cascade="all, delete-orphan",
        order_by="HistoricoUsoTalhao.data_inicio.desc()"
    )
    amostras_solo: Mapped[list["AmostraSolo"]] = relationship(
        back_populates="area_rural", lazy="noload", cascade="all, delete-orphan"
    )
```

---

### 2.2. Service — `service.py`

#### 2.2.1. Adicionar `AreaRuralService.validar_hierarquia()`

```python
HIERARQUIA_VALIDA = {
    "PROPRIEDADE":       {"GLEBA", "TALHAO", "PASTAGEM", "APP", "RESERVA_LEGAL", "UNIDADE_PRODUTIVA", "SEDE", "ARMAZEM", "INFRAESTRUTURA", "AREA"},
    "GLEBA":             {"TALHAO", "PASTAGEM", "APP", "RESERVA_LEGAL", "AREA"},
    "UNIDADE_PRODUTIVA": {"TALHAO", "PASTAGEM", "AREA"},
    "TALHAO":            {"SUBTALHAO", "PIQUETE"},
    "SUBTALHAO":         {"ZONA_DE_MANEJO"},
    "ZONA_DE_MANEJO":    set(),  # Nível folha — não pode ter filhos
    "PASTAGEM":          {"PIQUETE"},
    "PIQUETE":           set(),
    "APP":               set(),
    "RESERVA_LEGAL":     set(),
    "AREA":              {"SUBTALHAO", "ZONA_DE_MANEJO"},
    "SEDE":              set(),
    "ARMAZEM":           set(),
    "INFRAESTRUTURA":    set(),
}

PROFUNDIDADE_MAX = {
    "PROPRIEDADE":       0,
    "GLEBA":             1,
    "UNIDADE_PRODUTIVA": 1,
    "TALHAO":            2,
    "PASTAGEM":          2,
    "SUBTALHAO":         3,
    "ZONA_DE_MANEJO":    4,
    "PIQUETE":           3,
    "APP":               1,
    "RESERVA_LEGAL":     1,
    "AREA":              2,
    "SEDE":              1,
    "ARMAZEM":           1,
    "INFRAESTRUTURA":    1,
}

async def validar_hierarquia(self, parent_id: uuid.UUID | None, tipo_filho: str) -> None:
    """Valida se o tipo do filho é permitido dado o tipo do pai."""
    if parent_id is None:
        # Sem pai = só PROPRIEDADE pode ser raiz
        if tipo_filho != "PROPRIEDADE":
            raise BusinessRuleError(
                f"Área do tipo {tipo_filho} não pode ser raiz. "
                "Apenas PROPRIEDADE pode ser criada sem parent_id."
            )
        return

    pai = await self.get_or_fail(parent_id)
    filhos_permitidos = HIERARQUIA_VALIDA.get(pai.tipo, set())
    if tipo_filho not in filhos_permitidos:
        raise BusinessRuleError(
            f"Não é possível criar {tipo_filho} dentro de {pai.tipo}. "
            f"Filhos permitidos para {pai.tipo}: {sorted(filhos_permitidos)}"
        )
```

#### 2.2.2. Adicionar `AreaRuralService.calcular_soma_areas()`

```python
async def calcular_soma_areas(self, parent_id: uuid.UUID) -> dict:
    """Calcula soma das áreas dos filhos diretos de uma área."""
    areas_filhas = await self.listar(parent_id=parent_id, apenas_ativos=True)
    soma = sum(a.area_hectares or a.area_hectares_manual or 0 for a in areas_filhas)
    return {
        "soma_areas_filhas_ha": round(soma, 4),
        "numero_filhos": len(areas_filhas),
        "areas": [
            {
                "id": str(a.id),
                "nome": a.nome,
                "tipo": a.tipo,
                "area_ha": a.area_hectares or a.area_hectares_manual,
            }
            for a in areas_filhas
        ]
    }
```

#### 2.2.3. Adicionar `AreaRuralService.obter_arvore_completa()`

```python
async def obter_arvore_completa(self, fazenda_id: uuid.UUID) -> dict:
    """Retorna a árvore hierárquica completa de uma fazenda."""
    # Busca a raiz (PROPRIEDADE) ou áreas raiz da fazenda
    raizes = await self.listar_raizes(fazenda_id=fazenda_id)

    def montar_no(area: AreaRural) -> dict:
        no = {
            "id": str(area.id),
            "tipo": area.tipo,
            "nome": area.nome,
            "codigo": area.codigo,
            "area_ha": area.area_hectares or area.area_hectares_manual,
            "nivel": PROFUNDIDADE_MAX.get(area.tipo, 0),
            "dados_precisao": {
                "tipo_solo": area.tipo_solo,
                "teor_argila": area.teor_argila,
                "ph_solo": area.ph_solo,
                "produtividade_media": area.produtividade_media_ha,
                "cultura_atual": area.cultura_atual,
            } if area.tipo in ("SUBTALHAO", "ZONA_DE_MANEJO", "TALHAO") else None,
            "filhos": [],
        }
        for filho in area.filhos:
            if filho.ativo:
                no["filhos"].append(montar_no(filho))
        return no

    return {
        "fazenda_id": str(fazenda_id),
        "arvore": [montar_no(raiz) for raiz in raizes]
    }
```

---

### 2.3. Schemas — `schemas.py`

#### 2.3.1. Expandir `AreaRuralCreate` e `AreaRuralUpdate`

```python
class AreaRuralCreate(BaseModel):
    nome: str
    tipo: str
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    fazenda_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    area_hectares: Optional[float] = None
    area_hectares_manual: Optional[float] = None
    geometria: Optional[dict[str, Any]] = None
    centroide_lat: Optional[float] = None
    centroide_lng: Optional[float] = None
    dados_extras: Optional[dict[str, Any]] = None

    # Agricultura de precisão (aplicável a SUBTALHAO, ZONA_DE_MANEJO, TALHAO)
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

#### 2.3.2. Novo schema: `AreaRuralTreeResponse`

```python
class AreaRuralTreeResponse(BaseModel):
    """Resposta hierárquica completa para visualização em árvore."""
    id: uuid.UUID
    tipo: str
    nome: str
    codigo: Optional[str]
    area_ha: Optional[float]
    nivel: int
    dados_precisao: Optional[dict[str, Any]] = None
    filhos: list["AreaRuralTreeResponse"] = []
    model_config = {"from_attributes": True}
```

#### 2.3.3. Novo schema: `HistoricoUsoCreate/Response`

```python
class HistoricoUsoCreate(BaseModel):
    area_rural_id: uuid.UUID
    data_inicio: date
    data_fim: Optional[date] = None
    tipo_uso: str = Field(..., max_length=50)
    cultivar: Optional[str] = Field(None, max_length=100)
    produtividade_obtida: Optional[float] = None
    observacoes: Optional[str] = None

class HistoricoUsoResponse(BaseModel):
    id: uuid.UUID
    area_rural_id: uuid.UUID
    data_inicio: date
    data_fim: Optional[date]
    tipo_uso: str
    cultivar: Optional[str]
    produtividade_obtida: Optional[float]
    observacoes: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}
```

#### 2.3.4. Novo schema: `AmostraSoloCreate/Response`

```python
class AmostraSoloCreate(BaseModel):
    area_rural_id: Optional[uuid.UUID] = None
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
    id: uuid.UUID
    area_rural_id: Optional[uuid.UUID]
    latitude: float
    longitude: float
    profundidade_cm: float
    data_coleta: date
    ph_cacl2: Optional[float]
    materia_organica: Optional[float]
    fosforo_mg_dm3: Optional[float]
    potassio_cmolc_dm3: Optional[float]
    calcio_cmolc_dm3: Optional[float]
    magnesio_cmolc_dm3: Optional[float]
    aluminio_cmolc_dm3: Optional[float]
    h_aluminio_cmolc_dm3: Optional[float]
    ctc_cmolc_dm3: Optional[float]
    saturacao_base_pct: Optional[float]
    argila_pct: Optional[float]
    areia_pct: Optional[float]
    silte_pct: Optional[float]
    tipo_solo_classificacao: Optional[str]
    laboratorio: Optional[str]
    numero_laudo: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}
```

---

### 2.4. Router — `router.py`

#### 2.4.1. Aplicar validação hierárquica no POST

```python
@router.post("", response_model=AreaRuralResponse, status_code=201)
async def criar(
    data: AreaRuralCreate,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    svc = AreaRuralService(AreaRural, session, tenant_id)

    # VALIDAÇÃO DE HIERARQUIA
    await svc.validar_hierarquia(data.parent_id, data.tipo)

    # VALIDAÇÃO RN-CP-004: soma de áreas de talhões
    if data.tipo in ("TALHAO", "SUBTALHAO", "ZONA_DE_MANEJO"):
        area_pai = data.parent_id
        if area_pai:
            pai = await svc.get_or_fail(area_pai)
            if pai.tipo == "PROPRIEDADE":
                fazenda = await fazenda_service.get_or_fail(pai.fazenda_id)  # precisa injeção
                areas_filhas = await svc.listar(parent_id=area_pai, tipo="TALHAO")
                soma_atual = sum(a.area_hectares or a.area_hectares_manual or 0 for a in areas_filhas)
                nova_soma = soma_atual + (data.area_hectares or data.area_hectares_manual or 0)
                limite = (fazenda.area_total_ha or 0) * 1.05
                if nova_soma > limite:
                    raise BusinessRuleError(
                        f"Soma dos talhões ({nova_soma:.2f} ha) excede 105% da área total "
                        f"da fazenda ({fazenda.area_total_ha} ha = {limite:.2f} ha)."
                    )

    return await svc.criar_area(data.model_dump())
```

#### 2.4.2. Novo endpoint: `/{area_id}/arvore`

```python
@router.get("/{area_id}/arvore", response_model=AreaRuralTreeResponse)
async def obter_arvore(
    area_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Retorna a sub-árvore hierárquica a partir de uma área."""
    svc = AreaRuralService(AreaRural, session, tenant_id)
    raiz = await svc.obter_com_filhos(area_id)

    def montar_no(area: AreaRural) -> AreaRuralTreeResponse:
        return AreaRuralTreeResponse(
            id=area.id,
            tipo=area.tipo,
            nome=area.nome,
            codigo=area.codigo,
            area_ha=area.area_hectares or area.area_hectares_manual,
            nivel=PROFUNDIDADE_MAX.get(area.tipo, 0),
            dados_precisao={
                "tipo_solo": area.tipo_solo,
                "teor_argila": area.teor_argila,
                "ph_solo": area.ph_solo,
                "produtividade_media": area.produtividade_media_ha,
            } if area.tipo in ("SUBTALHAO", "ZONA_DE_MANEJO") else None,
            filhos=[montar_no(f) for f in area.filhos if f.ativo],
        )

    return montar_no(raiz)
```

#### 2.4.3. Novo endpoint: `/{area_id}/soma-areas`

```python
@router.get("/{area_id}/soma-areas")
async def soma_areas(
    area_id: uuid.UUID,
    session=Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Calcula a soma das áreas dos filhos diretos."""
    svc = AreaRuralService(AreaRural, session, tenant_id)
    return await svc.calcular_soma_areas(area_id)
```

#### 2.4.4. Novos endpoints: Histórico de Uso

```python
@router.get("/{area_id}/historico-uso", response_model=list[HistoricoUsoResponse])
async def listar_historico_uso(area_id: uuid.UUID, ...):
    svc = AreaRuralService(AreaRural, session, tenant_id)
    stmt = select(HistoricoUsoTalhao).where(
        HistoricoUsoTalhao.area_rural_id == area_id,
        HistoricoUsoTalhao.tenant_id == tenant_id
    ).order_by(HistoricoUsoTalhao.data_inicio.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())

@router.post("/{area_id}/historico-uso", response_model=HistoricoUsoResponse, status_code=201)
async def criar_historico_uso(area_id: uuid.UUID, data: HistoricoUsoCreate, ...):
    payload = data.model_dump()
    payload["area_rural_id"] = area_id
    payload["tenant_id"] = tenant_id
    obj = HistoricoUsoTalhao(**payload)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj
```

#### 2.4.5. Novos endpoints: Amostras de Solo

```python
@router.get("/{area_id}/amostras-solo", response_model=list[AmostraSoloResponse])
async def listar_amostras(area_id: uuid.UUID, ...): ...

@router.post("/{area_id}/amostras-solo", response_model=AmostraSoloResponse, status_code=201)
async def criar_amostra(area_id: uuid.UUID, data: AmostraSoloCreate, ...): ...
```

---

### 2.5. Migration

```python
"""add_subtalhao_zona_manejo_precisao

Revision ID: add_subtalhao_zona_manejo
Revises: previous
Create Date: 2026-04-06

Changes:
1. Adiciona tipos SUBTALHAO e ZONA_DE_MANEJO ao enum (via CHECK constraint ou novo registro)
2. Adiciona colunas de agricultura de precisão a cadastros_areas_rurais:
   - tipo_solo, teor_argila, teor_areia, ph_solo, materia_organica_pct
   - condutividade_eletrica, produtividade_media_ha, cultura_atual, irrigado
3. Cria tabela cadastros_areas_historico_uso
4. Cria tabela cadastros_amostras_solo
5. Adiciona coluna nivel_profundidade a cadastros_areas_rurais
"""
```

---

### 2.6. Impacto em `PrescricaoVRA`

O modelo existente já referencia `talhao_id → cadastros_areas_rurais`. Com a adição de `SUBTALHAO` e `ZONA_DE_MANEJO`:

- **Prescrição por talhão:** já funciona (passa UUID do talhão)
- **Prescrição por subtalhão:** já funciona (passa UUID do subtalhão)
- **Prescrição por zona de manejo:** já funciona (passa UUID da zona)

**Mudança recomendada:** Adicionar campo `resolucao_m` indicando a granularidade da prescrição:

```python
class PrescricaoVRA(Base):
    # ... existente ...
    nivel_area: Mapped[str] = mapped_column(
        String(20), nullable=False, default="TALHAO",
        comment="Nível da área: TALHAO, SUBTALHAO, ZONA_DE_MANEJO"
    )
```

---

## 3. Mudanças no Frontend

### 3.1. Página `/cadastros/propriedades/[id]` — Nova Estrutura de Abas

```
Propriedade: Fazenda Santa Maria
├── [Dados Gerais]
├── [Hierarquia]          ← NOVA ABA (substitui "Talhões")
│   └── Árvore visual com níveis expansíveis
│       ├── 🏠 Gleba Norte
│       │   ├── 🚜 Talhão 01 — Soja
│       │   │   ├── 🔬 01A — Argiloso
│       │   │   │   └── 🗺️ Zona Fértil (pH 6.2)
│       │   │   └── 🔬 01B — Arenoso
│       │   │       └── 🗺️ Zona Baixa Fertilidade
│       │   └── 🚜 Talhão 02 — Milho
│       └── 🌿 Gleba Mata (Reserva Legal)
├── [Talhões]             ← Mantém (lista plana com filtros)
├── [Infraestrutura]
└── [Amostras de Solo]    ← NOVA ABA
```

### 3.2. Componente `AreaTree.tsx` (novo)

Renderiza a hierarquia como árvore expansível com ícones por tipo:

| Tipo | Ícone | Cor |
|------|-------|-----|
| PROPRIEDADE | 🏠 | Emerald |
| GLEBA | 🗺️ | Blue |
| TALHAO | 🚜 | Green |
| SUBTALHAO | 🔬 | Amber |
| ZONA_DE_MANEJO | 🗺️ | Purple |
| PASTAGEM | 🌿 | Lime |
| PIQUETE | 🐄 | Yellow |
| APP | 💧 | Red |
| RESERVA_LEGAL | 🌳 | Forest |
| INFRAESTRUTURA | 🏗️ | Slate |

### 3.3. Componente `ZonaManejoDialog.tsx` (novo)

Formulário específico para zonas de manejo com campos:
- Nome, código
- Tipo de solo (select)
- Teor de argila, areia (%)
- pH
- Condutividade elétrica
- Produtividade média histórica
- Upload de grade de prescrição (GeoJSON)

### 3.4. Componente `HistoricoUsoTimeline.tsx` (novo)

Timeline visual mostrando a alternância de culturas no talhão:

```
Talhão 01
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2023/24    2024      2024/25   2025
🫘 Soja    🌽 Milho   🌿 Past.   🫘 Soja
45 sc/ha   80 sc/ha   20 UA/ha   ??
```

### 3.5. Componente `AmostrasSoloMap.tsx` (novo)

Mapa com pontos de amostras de solo sobrepostos aos polígonos dos talhões. Clique no ponto exibe análise laboratorial.

### 3.6. Progress Bar de Área — Com Hierarquia

A validação RN-CP-004 agora considera:
- Soma de TALHAO + SUBTALHAO ≤ 105% da área total da fazenda
- ZONAS_DE_MANEJO dentro de um subtalhão somam 100% do subtalhão

```
Área Total da Fazenda: 1250 ha
┌──────────────────────────────────────────┐
│ Talhões: 1180 ha (94.4%)   ████████░░░░  │
│ Gleba Norte: 800 ha                      │
│   Talhão 01: 120 ha                      │
│   Talhão 02: 200 ha                      │
│   Talhão 03: 150 ha                      │
│ Gleba Sul: 380 ha                        │
│   Talhão 04: 180 ha                      │
│   Talhão 05: 200 ha                      │
└──────────────────────────────────────────┘
```

---

## 4. Exemplo Completo de Uso

### Cenário: Fazenda tecnificada com agricultura de precisão

```
PROPRIEDADE: Fazenda Santa Maria
  uf: MT, municipio: Sorriso, area_total_ha: 2500
  codigo_car: MT-1234567890123

├── GLEBA: Gleba Norte (800 ha)
│   parent_id: PROPRIEDADE
│
│   ├── TALHAO: Talhão 01 (120 ha)
│   │   parent_id: GLEBA, cultura_atual: SOJA, irrigado: true
│   │
│   │   ├── SUBTALHAO: 01A — Solo Argiloso (70 ha)
│   │   │   parent_id: TALHAO 01
│   │   │   tipo_solo: LATOSSOLO_VERMELHO, teor_argila: 65, ph_solo: 5.8
│   │   │   materia_organica: 3.2, condutividade_eletrica: 45.2
│   │   │   produtividade_media_ha: 65.0  (sacas soja/ha)
│   │   │
│   │   │   ├── ZONA_DE_MANEJO: Zona Alta Fertilidade (30 ha)
│   │   │   │   parent_id: SUBTALHAO 01A
│   │   │   │   ph_solo: 6.2, fosforo: 15.5, potassio: 0.45
│   │   │   │   produtividade_media_ha: 72.0
│   │   │   │   → Prescrição VRA: Adubação NPK 400kg/ha
│   │   │   │
│   │   │   └── ZONA_DE_MANEJO: Zona Media Fertilidade (40 ha)
│   │   │       parent_id: SUBTALHAO 01A
│   │   │       ph_solo: 5.5, fosforo: 8.2, potassio: 0.25
│   │   │       produtividade_media_ha: 58.0
│   │   │       → Prescrição VRA: Adubação NPK 550kg/ha
│   │   │
│   │   └── SUBTALHAO: 01B — Solo Arenoso (50 ha)
│   │       parent_id: TALHAO 01
│   │       tipo_solo: NEOSSOLO, teor_areia: 75, ph_solo: 4.8
│   │       produtividade_media_ha: 42.0
│   │       → Prescrição VRA: Corretivo calcário 3ton/ha
│   │
│   └── TALHAO: Talhão 02 (200 ha)
│       parent_id: GLEBA, cultura_atual: MILHO
│
├── GLEBA: Gleba Sul (380 ha)
│   └── ...
│
└── RESERVA_LEGAL: Mata Ciliar (320 ha)
    parent_id: PROPRIEDADE
```

**Histórico de uso do Talhão 01:**

| Período | Uso | Produtividade |
|---------|-----|--------------|
| 2022/23 | Soja | 58 sc/ha |
| 2023 | Milho safrinha | 75 sc/ha |
| 2023/24 | Soja | 62 sc/ha |
| 2024 | Braquiária (ILP) | 18 UA/ha |
| 2024/25 | Soja | (atual) |

---

## 5. Ordem de Implementação

| Fase | Tarefa | Arquivos | Estim. Complexidade |
|------|--------|----------|---------------------|
| **Fase 1** | Adicionar tipos `SUBTALHAO` e `ZONA_DE_MANEJO` ao enum | `models.py` | Baixa |
| **Fase 1** | Adicionar colunas de precisão ao `AreaRural` | `models.py` | Baixa |
| **Fase 1** | Adicionar `nivel_profundidade` + popular existente | `models.py` + migration | Média |
| **Fase 2** | Criar modelo `HistoricoUsoTalhao` | `models.py` | Média |
| **Fase 2** | Criar modelo `AmostraSolo` | `models.py` | Média |
| **Fase 2** | Criar migration completa | `migrations/versions/` | Média |
| **Fase 3** | `validar_hierarquia()` no `AreaRuralService` | `service.py` | Alta |
| **Fase 3** | `calcular_soma_areas()` no `AreaRuralService` | `service.py` | Baixa |
| **Fase 3** | `obter_arvore_completa()` no `AreaRuralService` | `service.py` | Média |
| **Fase 3** | Integrar validação hierárquica no POST do router | `router.py` | Média |
| **Fase 3** | Endpoints `/arvore`, `/soma-areas`, `/historico-uso`, `/amostras-solo` | `router.py` | Média |
| **Fase 4** | Expandir schemas Pydantic com campos de precisão | `schemas.py` | Baixa |
| **Fase 4** | Criar schemas `HistoricoUsoCreate/Response` | `schemas.py` | Baixa |
| **Fase 4** | Criar schemas `AmostraSoloCreate/Response` | `schemas.py` | Baixa |
| **Fase 5** | Atualizar schemas Zod do frontend | `fazenda-schemas.ts` | Baixa |
| **Fase 6** | UI: Componente `AreaTree.tsx` | `components/` | Alta |
| **Fase 6** | UI: Aba "Hierarquia" na página de detalhe | `page.tsx [id]` | Alta |
| **Fase 6** | UI: Dialog de Subtalhão e Zona de Manejo | `components/` | Média |
| **Fase 6** | UI: Timeline `HistoricoUsoTimeline.tsx` | `components/` | Média |
| **Fase 6** | UI: Mapa de amostras de solo | `components/` | Alta |
| **Fase 7** | Tests: validação hierárquica, soma de áreas | `tests/` | Média |

---

## 6. Checklist de Conformidade Conceitual

| Conceito do documento | Implementação |
|-----------------------|--------------|
| Terra é fixa, uso muda | ✅ `AreaRural` (fixo) + `HistoricoUsoTalhao` (temporal) |
| Gleba = geográfica, não produtiva | ✅ Gleba é tipo territorial, sem `cultura_atual` |
| Talhão = unidade operacional | ✅ Talhão tem `cultura_atual`, muda com `HistoricoUsoTalhao` |
| Subtalhão = variação interna | ✅ Tipo `SUBTALHAO` com atributos de solo |
| Zona de manejo = agricultura de precisão | ✅ Tipo `ZONA_DE_MANEJO` com dados analíticos |
| Separação territorial/operacional/temporal | ✅ 3 dimensões em modelos separados |
| ILP (alternância lavoura-pecuária) | ✅ `HistoricoUsoTalhao` registra alternância |
| Gleba não define cultura | ✅ Gleba não tem campo `cultura_atual` |
| Talhão pode mudar uso ao longo do tempo | ✅ `HistoricoUsoTalhao` com `data_inicio`/`data_fim` |

**Conformidade conceitual pós-implementação: ~95%**

---

## 7. Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| Migration em colunas novas pode ser lenta em bases grandes | Executar em janela de manutenção; usar `CREATE INDEX CONCURRENTLY` |
| Dados existentes sem `nivel_profundidade` | Script de migração calcula nível percorrendo `parent_id` |
| Validação hierárquica quebra APIs existentes que criam áreas sem parent | Validar apenas para novos registros; existente permanece |
| Complexidade da UI de árvore | Usar biblioteca `react-complex-tree` ou componente shadcn `Tree` |
| Prescrição VRA referenciando talhão inativo | FK com `ondelete="SET NULL"` já protege; validar no service |

---

## 8. Conclusão

A reestruturação proposta transforma o modelo `AreaRural` de um **registro geográfico simples** para um **sistema completo de gestão territorial e de precisão**, alinhado com a realidade do agro brasileiro:

1. **5 níveis de hierarquia** com validação semântica impedem erros conceituais
2. **Colunas dedicadas** para dados de solo e produtividade habilitam análise eficiente
3. **Histórico de uso** separa território (fixo) de atividade (temporal)
4. **Amostras de solo** georreferenciadas dão base científica para zonas de manejo
5. **Prescrição VRA** já suporta qualquer nível (talhão, subtalhão ou zona)

O investimento estimado é de **7 fases**, sendo as fases 1-4 (backend) as mais críticas e as fases 5-6 (frontend) as de maior impacto percebido pelo usuário.
