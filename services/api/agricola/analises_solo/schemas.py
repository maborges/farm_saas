from pydantic import BaseModel, ConfigDict, computed_field
from uuid import UUID
from datetime import date, datetime
from typing import Literal

TipoIrrigacao = Literal["SEQUEIRO", "GOTEJAMENTO", "PIVO_CENTRAL", "ASPERSAO", "SULCO"]
SistemaManejo = Literal["PLANTIO_DIRETO", "CONVENCIONAL", "MINIMO"]


class AnaliseSoloCreate(BaseModel):
    talhao_id: UUID
    data_coleta: date
    laboratorio: str | None = None
    codigo_amostra: str | None = None
    profundidade_cm: int | None = None

    # Físicos
    argila_pct: float | None = None
    silte_pct: float | None = None
    areia_pct: float | None = None

    # Químicos
    ph_agua: float | None = None
    ph_cacl2: float | None = None
    materia_organica_pct: float | None = None
    fosforo_p: float | None = None
    potassio_k: float | None = None
    calcio_ca: float | None = None
    magnesio_mg: float | None = None
    aluminio_al: float | None = None
    hidrogenio_al_hal: float | None = None

    # Calculados (backend pode inferir se não informados)
    ctc: float | None = None
    v_pct: float | None = None
    saturacao_al_m_pct: float | None = None

    # Micronutrientes
    zinco_zn: float | None = None
    boro_b: float | None = None
    ferro_fe: float | None = None
    manganes_mn: float | None = None

    # Contexto agronômico
    tipo_irrigacao: TipoIrrigacao | None = None
    sistema_manejo: SistemaManejo | None = None
    cultura_nome: str | None = None
    cultura_anterior: str | None = None

    # Validade
    validade_meses: int | None = 12

    # Extras
    arquivo_laudo_url: str | None = None
    observacoes: str | None = None


class AnaliseSoloUpdate(BaseModel):
    data_coleta: date | None = None
    laboratorio: str | None = None
    codigo_amostra: str | None = None
    profundidade_cm: int | None = None
    argila_pct: float | None = None
    silte_pct: float | None = None
    areia_pct: float | None = None
    ph_agua: float | None = None
    ph_cacl2: float | None = None
    materia_organica_pct: float | None = None
    fosforo_p: float | None = None
    potassio_k: float | None = None
    calcio_ca: float | None = None
    magnesio_mg: float | None = None
    aluminio_al: float | None = None
    hidrogenio_al_hal: float | None = None
    ctc: float | None = None
    v_pct: float | None = None
    saturacao_al_m_pct: float | None = None
    zinco_zn: float | None = None
    boro_b: float | None = None
    ferro_fe: float | None = None
    manganes_mn: float | None = None
    tipo_irrigacao: TipoIrrigacao | None = None
    sistema_manejo: SistemaManejo | None = None
    cultura_nome: str | None = None
    cultura_anterior: str | None = None
    validade_meses: int | None = None
    arquivo_laudo_url: str | None = None
    observacoes: str | None = None


class AnaliseSoloResponse(AnaliseSoloCreate):
    id: UUID
    tenant_id: UUID
    talhao_nome: str | None = None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def vencida(self) -> bool:
        from datetime import date as date_
        meses = self.validade_meses or 12
        from dateutil.relativedelta import relativedelta
        return date_.today() > self.data_coleta + relativedelta(months=meses)

    model_config = ConfigDict(from_attributes=True)
