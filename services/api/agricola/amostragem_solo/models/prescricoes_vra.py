"""Modelo para prescricoes_vra."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid
from uuid import UUID as UUIDType

from core.database import Base


class PrescricaoVRA(Base):
    """Modelo para prescrição de aplicação em taxa variável (VRA)."""
    __tablename__ = "prescricoes_vra"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    fazenda_id = Column(Integer, ForeignKey("fazendas.id"), nullable=False)
    talhao_id = Column(Integer, ForeignKey("talhoes.id"), nullable=False)
    safra_id = Column(Integer, ForeignKey("safras.id"))

    # Tipo de prescrição
    tipo = Column(String(50), nullable=False)  # adubacao, calcario, corretivo
    elemento = Column(String(50))  # N, P, K, calcario, gesso

    # Parâmetros
    dose_media = Column(Float)  # kg/ha ou L/ha
    dose_minima = Column(Float)
    dose_maxima = Column(Float)
    unidade = Column(String(20), default="kg/ha")

    # Arquivos
    caminho_isoxml = Column(String(500))  # Arquivo ISOXML para máquinas
    caminho_shapefile = Column(String(500))
    caminho_geojson = Column(String(500))

    # Mapa de prescrição
    grid_tamanho_m = Column(Float)  # Tamanho do grid em metros
    total_pontos = Column(Integer)

    # Status
    status = Column(String(50), default="rascunho")  # rascunho, aprovada, aplicada
    aprovada_por = Column(Integer, ForeignKey("usuarios.id"))
    aprovada_em = Column(DateTime)

    # Responsável técnico
    responsavel_tecnico = Column(String(200))
    crt = Column(String(100))

    observacoes = Column(Text)
    criada_em = Column(DateTime, default=datetime.utcnow)
    atualizada_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    fazenda = relationship("Fazenda", backref="prescricoes_vra")
    talhao = relationship("Talhao", backref="prescricoes_vra")
