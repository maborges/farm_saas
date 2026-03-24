import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID
from core.database import Base

class ConhecimentoCategoria(Base):
    """Categorias para agrupar artigos da Base de Conhecimento."""
    __tablename__ = "conhecimento_categorias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    icone: Mapped[str | None] = mapped_column(String(50)) # Nome do ícone Lucide
    ordem: Mapped[int] = mapped_column(default=0)

    artigos: Mapped[list["ConhecimentoArtigo"]] = relationship("ConhecimentoArtigo", back_populates="categoria")

class ConhecimentoArtigo(Base):
    """Artigos com tutoriais e informações para os usuários."""
    __tablename__ = "conhecimento_artigos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    categoria_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conhecimento_categorias.id", ondelete="CASCADE"), index=True)
    
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False) # Markdown content
    
    is_publico: Mapped[bool] = mapped_column(default=True)
    visualizacoes: Mapped[int] = mapped_column(default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    categoria: Mapped["ConhecimentoCategoria"] = relationship("ConhecimentoCategoria", back_populates="artigos")
