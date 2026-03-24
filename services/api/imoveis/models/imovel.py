import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Float, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base

class ImovelRural(Base):
    """Propriedade Rural legal (Matriz ou Filiais)."""
    __tablename__ = "imoveis_rurais"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    
    # Documentação Federal
    car_numero: Mapped[str | None] = mapped_column(String(100), index=True) # Cadastro Ambiental Rural
    nirf: Mapped[str | None] = mapped_column(String(20)) # Receita Federal
    incra: Mapped[str | None] = mapped_column(String(30))
    
    area_total_ha: Mapped[float] = mapped_column(Float, default=0.0)
    area_preservacao_ha: Mapped[float] = mapped_column(Float, default=0.0)
    
    cidade: Mapped[str | None] = mapped_column(String(100))
    estado: Mapped[str | None] = mapped_column(String(2))
    
    # Suporte a polígono (GeoJSON)
    geometria: Mapped[dict | None] = mapped_column(JSON, nullable=True)

class MatriculaImovel(Base):
    """Cada imóvel rural pode ter várias matrículas de cartório."""
    __tablename__ = "imoveis_matriculas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    imovel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("imoveis_rurais.id", ondelete="CASCADE"))
    
    numero_matricula: Mapped[str] = mapped_column(String(50), nullable=False)
    cartorio: Mapped[str | None] = mapped_column(String(200))
    area_matricula_ha: Mapped[float] = mapped_column(Float, default=0.0)

class Benfeitoria(Base):
    """Instalações: Sedes, casas de colonos, silos, barracões."""
    __tablename__ = "imoveis_benfeitorias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    imovel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("imoveis_rurais.id", ondelete="CASCADE"))
    
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50)) # SEDE, SILO, CURRAL, CASA, ALMOXARIFADO
    area_construida: Mapped[float | None] = mapped_column(Float)
    valor_estimado: Mapped[float | None] = mapped_column(Float)
