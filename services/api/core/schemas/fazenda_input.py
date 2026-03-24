from pydantic import BaseModel, Field, constr
from typing import Optional

class FazendaCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150, description="Nome da propriedade rural.")
    cnpj: Optional[str] = Field(None, max_length=20, description="CNPJ opcional da propriedade.")
    inscricao_estadual: Optional[str] = Field(None, max_length=50, description="IE da propriedade se houver.")
    area_total_ha: Optional[float] = Field(None, gt=0, description="Tamanho em Hectares.")
    coordenadas_sede: Optional[str] = Field(None, max_length=100, description="Latitude, Longitude. Ex: -23.5505,-46.6333")
    geometria: Optional[dict] = Field(None, description="Polígono GeoJSON da fazenda.")
    ativo: bool = True

class FazendaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    cnpj: Optional[str] = Field(None, max_length=20)
    inscricao_estadual: Optional[str] = Field(None, max_length=50)
    area_total_ha: Optional[float] = Field(None, gt=0)
    coordenadas_sede: Optional[str] = Field(None, max_length=100)
    geometria: Optional[dict] = None
    ativo: Optional[bool] = None
