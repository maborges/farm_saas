from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Date, DateTime, Text, ForeignKey, text, Uuid, Numeric, JSON
from uuid import UUID
import uuid
from datetime import datetime, date
from core.database import Base


class CadernoCampoEntrada(Base):
    __tablename__ = "caderno_campo_entradas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    safra_id: Mapped[UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True)
    talhao_id: Mapped[UUID] = mapped_column(ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True)

    # OPERACAO_AUTO | MONITORAMENTO | VISITA_TECNICA | EPI_ENTREGA | OBSERVACAO | CLIMA | SOLO
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    data_registro: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    usuario_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    # Referência opcional à operação agrícola que gerou esta entrada automaticamente
    operacao_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("operacoes_agricolas.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Auditoria
    ip_dispositivo: Mapped[str | None] = mapped_column(String(100))
    excluida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    motivo_exclusao: Mapped[str | None] = mapped_column(Text)
    digitalizacao_retroativa: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    justificativa_retroativa: Mapped[str | None] = mapped_column(Text)

    # Campos específicos por tipo
    nivel_severidade: Mapped[str | None] = mapped_column(String(20))  # BAIXO | MEDIO | ALTO | CRITICO
    recomendacao: Mapped[str | None] = mapped_column(Text)
    numero_receituario: Mapped[str | None] = mapped_column(String(50))  # Lei 7.802/89

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)

    fotos: Mapped[list["CadernoCampoFoto"]] = relationship(
        back_populates="entrada", cascade="all, delete-orphan", lazy="selectin"
    )


class CadernoCampoFoto(Base):
    __tablename__ = "caderno_campo_fotos"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entrada_id: Mapped[UUID] = mapped_column(
        ForeignKey("caderno_campo_entradas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    data_captura: Mapped[datetime | None] = mapped_column(DateTime)

    entrada: Mapped["CadernoCampoEntrada"] = relationship(back_populates="fotos")


class VisitaTecnica(Base):
    __tablename__ = "visitas_tecnicas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    safra_id: Mapped[UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True)
    talhao_id: Mapped[UUID] = mapped_column(
        ForeignKey("cadastros_areas_rurais.id", ondelete="CASCADE"), nullable=False, index=True
    )

    responsavel_tecnico_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    nome_rt: Mapped[str] = mapped_column(String(200), nullable=False)
    crea: Mapped[str] = mapped_column(String(30), nullable=False)
    data_visita: Mapped[date] = mapped_column(Date, nullable=False)

    observacoes: Mapped[str | None] = mapped_column(Text)
    recomendacoes: Mapped[str | None] = mapped_column(Text)
    constatacoes: Mapped[list[dict]] = mapped_column(JSON, default=list)

    # Assinatura digital
    assinado: Mapped[bool] = mapped_column(Boolean, default=False)
    data_assinatura: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"), onupdate=datetime.utcnow)


class EPIEntrega(Base):
    __tablename__ = "epi_entregas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    trabalhador_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    nome_trabalhador: Mapped[str] = mapped_column(String(200), nullable=False)

    epi_tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    quantidade: Mapped[int] = mapped_column(nullable=False, default=1)
    data_entrega: Mapped[date] = mapped_column(Date, nullable=False)
    validade: Mapped[date | None] = mapped_column(Date)

    assinatura_url: Mapped[str | None] = mapped_column(String(500))
    operacao_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))


class CadernoExportacao(Base):
    __tablename__ = "caderno_exportacoes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    safra_id: Mapped[UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False, index=True)
    talhao_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)

    url_pdf: Mapped[str] = mapped_column(String(500), nullable=False)
    data_geracao: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))

    assinado_por: Mapped[str | None] = mapped_column(String(200))
    crea_rt: Mapped[str | None] = mapped_column(String(30))
    crea_validade: Mapped[date | None] = mapped_column(Date)

    # INTERNO | GLOBALGAP | ORGANICO | MAPA
    modelo_certificacao: Mapped[str] = mapped_column(String(30), default="INTERNO")

    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
