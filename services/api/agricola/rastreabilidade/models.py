from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Date, Text, ForeignKey, text, JSON
from uuid import UUID
import uuid
from datetime import datetime
from core.database import Base

class LoteRastreabilidade(Base):
    __tablename__ = "lotes_rastreabilidade"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    codigo_lote: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    safra_id: Mapped[UUID] = mapped_column(ForeignKey("safras.id", ondelete="CASCADE"), nullable=False)
    talhao_id: Mapped[UUID] = mapped_column(ForeignKey("talhoes.id", ondelete="CASCADE"), nullable=False)
    
    produto: Mapped[str] = mapped_column(String(100), nullable=False)
    variedade: Mapped[str | None] = mapped_column(String(100))
    
    quantidade_total: Mapped[float] = mapped_column(default=0)
    unidade: Mapped[str] = mapped_column(String(20), default="KG")
    
    data_geracao: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
    qr_code_url: Mapped[str | None] = mapped_column(String(255))
    
    status: Mapped[str] = mapped_column(String(20), default="ATIVO") # ATIVO, EMBARCADO, PROCESSADO
    
    # Metadados de Auditoria / Certificações
    certificacoes: Mapped[list[str]] = mapped_column(JSON, default=list) # ["GLOBALGAP", "ORGÂNICO"]
    
    observacoes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))

class CertificacaoPropriedade(Base):
    __tablename__ = "certificacoes_propriedade"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    fazenda_id: Mapped[UUID] = mapped_column(ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False)
    
    nome: Mapped[str] = mapped_column(String(100), nullable=False) # Ex: GlobalGap, RTRS
    extensao: Mapped[str | None] = mapped_column(String(100)) # Escopo
    
    data_emissao: Mapped[datetime] = mapped_column(Date)
    data_validade: Mapped[datetime] = mapped_column(Date)
    
    orgao_certificador: Mapped[str | None] = mapped_column(String(100))
    numero_registro: Mapped[str | None] = mapped_column(String(50))
    
    status: Mapped[str] = mapped_column(String(20), default="VALIDA") # VALIDA, EXPIRADA, SUSPENSA
    
    link_documento: Mapped[str | None] = mapped_column(String(255))
    
    created_at: Mapped[datetime] = mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))
