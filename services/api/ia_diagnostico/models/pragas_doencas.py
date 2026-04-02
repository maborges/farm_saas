"""Modelo para pragas_doencas."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base


class PragasDoencas(Base):
    """Modelo para pragas_doencas."""
    __tablename__ = "pragas_doencas"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Adicionar campos específicos aqui
    # nome = Column(String(200), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
