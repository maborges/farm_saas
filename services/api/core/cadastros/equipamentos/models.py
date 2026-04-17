import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Float, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base
import enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TipoEquipamento(str, enum.Enum):
    TRATOR          = "TRATOR"
    COLHEDORA       = "COLHEDORA"
    PLANTADEIRA     = "PLANTADEIRA"
    PULVERIZADOR    = "PULVERIZADOR"
    IMPLEMENTO      = "IMPLEMENTO"      # grade, arado, subsolador, etc.
    VEICULO         = "VEICULO"         # caminhão, pickup, utilitário
    IRRIGACAO       = "IRRIGACAO"       # pivô, bomba, tubulação
    OUTRO           = "OUTRO"


class CombustivelTipo(str, enum.Enum):
    DIESEL          = "DIESEL"
    GASOLINA        = "GASOLINA"
    ETANOL          = "ETANOL"
    FLEX            = "FLEX"
    ELETRICO        = "ELETRICO"
    GNV             = "GNV"
    NAO_APLICAVEL   = "NAO_APLICAVEL"


class StatusEquipamento(str, enum.Enum):
    ATIVO           = "ATIVO"
    EM_MANUTENCAO   = "EM_MANUTENCAO"
    INATIVO         = "INATIVO"
    VENDIDO         = "VENDIDO"
    SUCATEADO       = "SUCATEADO"


# ---------------------------------------------------------------------------
# Equipamento — entidade mestre (substitui frota_maquinarios)
# ---------------------------------------------------------------------------

class Equipamento(Base):
    """
    Cadastro mestre de máquinas, implementos e veículos do tenant.

    Substitui: frota_maquinarios.

    Os módulos operacional/frota/ (PlanoManutencao, OrdemServico, RegistroManutencao)
    continuam existindo e referenciam Equipamento.id via equipamento_id.

    dados_extras JSONB por tipo:
      TRATOR:       {"potencia_cv": 180, "tracao": "4x4", "rpm_pto": 540}
      COLHEDORA:    {"plataforma_pe": 30, "velocidade_trilha": 1050}
      PULVERIZADOR: {"capacidade_litros": 3000, "largura_barra_m": 28}
      PIVÔ:         {"area_irrigada_ha": 120, "vazao_m3h": 350}
      VEICULO:      {"capacidade_carga_kg": 15000, "eixos": 3}
    """
    __tablename__ = "cadastros_equipamentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unidade_produtiva_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("unidades_produtivas.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Identificação
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    marca: Mapped[str | None] = mapped_column(String(100), nullable=True)
    modelo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ano_fabricacao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ano_modelo: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Documentação
    placa: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    chassi: Mapped[str | None] = mapped_column(String(50), nullable=True)
    numero_serie: Mapped[str | None] = mapped_column(String(50), nullable=True)
    patrimonio: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Número de patrimônio interno")

    # Propulsão
    combustivel: Mapped[str] = mapped_column(String(20), default="DIESEL")
    potencia_cv: Mapped[float | None] = mapped_column(Float, nullable=True)
    capacidade_tanque_l: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Hodômetro / horímetro
    horimetro_atual: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    km_atual: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Valor patrimonial
    valor_aquisicao: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_aquisicao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valor_atual: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Valor de mercado atual estimado")

    # Atributos específicos por tipo
    dados_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="ATIVO", nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
