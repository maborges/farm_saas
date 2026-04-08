from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
import uuid


class FazendaCreate(BaseModel):
    grupo_id: uuid.UUID = Field(..., description="Grupo de fazendas ao qual esta propriedade pertence.")
    nome: str = Field(..., min_length=2, max_length=150, description="Nome da propriedade rural.")
    cpf_cnpj: Optional[str] = Field(None, max_length=18, description="CPF ou CNPJ do proprietário.")
    inscricao_estadual: Optional[str] = Field(None, max_length=50)
    codigo_car: Optional[str] = Field(None, max_length=50, description="Código CAR no formato SICAR.")
    nirf: Optional[str] = Field(None, max_length=20, description="Número do Imóvel na Receita Federal.")
    uf: Optional[str] = Field(None, min_length=2, max_length=2, description="UF da propriedade.")
    municipio: Optional[str] = Field(None, max_length=100)
    area_total_ha: Optional[Decimal] = Field(None, gt=0, description="Área total em hectares.")
    area_aproveitavel_ha: Optional[Decimal] = Field(None, gt=0)
    area_app_ha: Optional[Decimal] = Field(None, ge=0, description="Área de Preservação Permanente.")
    area_rl_ha: Optional[Decimal] = Field(None, ge=0, description="Área de Reserva Legal.")
    coordenadas_sede: Optional[str] = Field(None, max_length=100, description="Lat,Long. Ex: -23.5505,-46.6333")
    geometria: Optional[dict] = Field(None, description="Polígono GeoJSON da fazenda.")
    ativo: bool = True


class FazendaUpdate(BaseModel):
    grupo_id: Optional[uuid.UUID] = None
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    inscricao_estadual: Optional[str] = Field(None, max_length=50)
    codigo_car: Optional[str] = Field(None, max_length=50)
    nirf: Optional[str] = Field(None, max_length=20)
    uf: Optional[str] = Field(None, min_length=2, max_length=2)
    municipio: Optional[str] = Field(None, max_length=100)
    area_total_ha: Optional[Decimal] = Field(None, gt=0)
    area_aproveitavel_ha: Optional[Decimal] = Field(None, gt=0)
    area_app_ha: Optional[Decimal] = Field(None, ge=0)
    area_rl_ha: Optional[Decimal] = Field(None, ge=0)
    coordenadas_sede: Optional[str] = Field(None, max_length=100)
    geometria: Optional[dict] = None
    ativo: Optional[bool] = None
