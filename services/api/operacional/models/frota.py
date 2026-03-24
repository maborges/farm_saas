import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base

class Maquinario(Base):
    __tablename__ = "frota_maquinarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    fazenda_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fazendas.id"), index=True)
    
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    # TRATOR, COLHEITADEIRA, VEICULO_LEVE, VEICULO_PESADO, IMPLEMENTO, PULVERIZADOR, OUTROS
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    marca: Mapped[str | None] = mapped_column(String(50))
    modelo: Mapped[str | None] = mapped_column(String(50))
    ano: Mapped[int | None] = mapped_column(Integer)
    placa_chassi: Mapped[str | None] = mapped_column(String(50))
    numero_serie: Mapped[str | None] = mapped_column(String(80))
    patrimonio: Mapped[str | None] = mapped_column(String(50))
    # DIESEL, GASOLINA, ETANOL, FLEX, ELETRICO, NAO_APLICAVEL
    combustivel: Mapped[str] = mapped_column(String(20), default="DIESEL")
    potencia_cv: Mapped[float | None] = mapped_column(Float, nullable=True)
    capacidade_tanque_l: Mapped[float | None] = mapped_column(Float, nullable=True)

    horimetro_atual: Mapped[float] = mapped_column(Float, default=0.0)
    km_atual: Mapped[float] = mapped_column(Float, default=0.0)
    
    status: Mapped[str] = mapped_column(String(20), default="ATIVO") # ATIVO, MANUTENCAO, INATIVO
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    planos: Mapped[list["PlanoManutencao"]] = relationship("PlanoManutencao", back_populates="maquinario", lazy="selectin")

class PlanoManutencao(Base):
    """Regras de quando deve ser feita a manutenção (ex: a cada 250h)."""
    __tablename__ = "frota_planos_manutencao"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maquinario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("frota_maquinarios.id", ondelete="CASCADE"))
    
    descricao: Mapped[str] = mapped_column(String(150), nullable=False)
    frequencia_horas: Mapped[float | None] = mapped_column(Float)
    frequencia_km: Mapped[float | None] = mapped_column(Float)
    
    ultimo_registro_horas: Mapped[float | None] = mapped_column(Float, default=0.0)
    ultimo_registro_km: Mapped[float | None] = mapped_column(Float, default=0.0)

    maquinario: Mapped["Maquinario"] = relationship("Maquinario", back_populates="planos")

class OrdemServico(Base):
    """Workflow de manutenção de oficina."""
    __tablename__ = "frota_ordens_servico"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    maquinario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("frota_maquinarios.id", ondelete="CASCADE"), index=True)
    
    numero_os: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    tipo: Mapped[str] = mapped_column(String(30)) # PREVENTIVA, CORRETIVA, REVISAO
    status: Mapped[str] = mapped_column(String(20), default="ABERTA") # ABERTA, EM_EXECUCAO, CONCLUIDA, CANCELADA
    
    descricao_problema: Mapped[str] = mapped_column(String(500))
    diagnostico_tecnico: Mapped[str | None] = mapped_column(String(1000))
    
    data_abertura: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    data_conclusao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    horimetro_na_abertura: Mapped[float] = mapped_column(Float)
    km_na_abertura: Mapped[float | None] = mapped_column(Float)
    
    tecnico_responsavel: Mapped[str | None] = mapped_column(String(100))
    custo_total_pecas: Mapped[float] = mapped_column(Float, default=0.0)
    custo_mao_obra: Mapped[float] = mapped_column(Float, default=0.0)

class ItemOrdemServico(Base):
    """Peças ou Insumos utilizados na OS (Baixa o estoque)."""
    __tablename__ = "frota_os_itens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    os_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("frota_ordens_servico.id", ondelete="CASCADE"))
    produto_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cadastros_produtos.id"))
    
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    preco_unitario_na_data: Mapped[float] = mapped_column(Float, default=0.0)

class RegistroManutencao(Base):
    """Log de manutenções realizadas (Histórico Simplificado)."""
    __tablename__ = "frota_registros_manutencao"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maquinario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("frota_maquinarios.id", ondelete="CASCADE"), index=True)
    os_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("frota_ordens_servico.id"), nullable=True)
    
    data_realizacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    tipo: Mapped[str] = mapped_column(String(30)) 
    descricao: Mapped[str] = mapped_column(String(500))
    custo_total: Mapped[float] = mapped_column(Float, default=0.0)
    
    horimetro_na_data: Mapped[float] = mapped_column(Float)
    km_na_data: Mapped[float | None] = mapped_column(Float)
    
    tecnico_responsavel: Mapped[str | None] = mapped_column(String(100))

