from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
import uuid


class UnidadeProdutivaCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150, description="Nome da propriedade rural.")
    tipo_propriedade: Optional[str] = Field("fazenda", max_length=30, description="fazenda | sitio | chacara | arrendamento | parceria")
    cpf_cnpj: Optional[str] = Field(None, max_length=18, description="CPF ou CNPJ do proprietário.")
    inscricao_estadual: Optional[str] = Field(None, max_length=50)
    codigo_car: Optional[str] = Field(None, max_length=80, description="Código CAR no formato SICAR.")
    nirf: Optional[str] = Field(None, max_length=20, description="Número do Imóvel na Receita Federal.")
    ccir: Optional[str] = Field(None, max_length=30, description="Certificado de Cadastro de Imóvel Rural.")
    sigef_codigo: Optional[str] = Field(None, max_length=50, description="Código SIGEF/INCRA.")
    # Localização
    cep: Optional[str] = Field(None, max_length=9)
    logradouro: Optional[str] = Field(None, max_length=255)
    bairro: Optional[str] = Field(None, max_length=100)
    municipio: Optional[str] = Field(None, max_length=100)
    uf: Optional[str] = Field(None, min_length=2, max_length=2, description="UF da propriedade.")
    ibge_municipio_codigo: Optional[str] = Field(None, max_length=7)
    # Áreas
    area_total_ha: Optional[Decimal] = Field(None, gt=0, description="Área total em hectares.")
    area_app_ha: Optional[Decimal] = Field(None, ge=0, description="APP — referência inicial.")
    area_rl_ha: Optional[Decimal] = Field(None, ge=0, description="Reserva Legal — referência inicial.")
    coordenadas_sede: Optional[str] = Field(None, max_length=100, description="Lat,Long. Ex: -23.5505,-46.6333")
    geometria: Optional[dict] = Field(None, description="Polígono GeoJSON da unidade produtiva.")
    ativo: bool = True


class UnidadeProdutivaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    tipo_propriedade: Optional[str] = Field(None, max_length=30)
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    inscricao_estadual: Optional[str] = Field(None, max_length=50)
    codigo_car: Optional[str] = Field(None, max_length=80)
    nirf: Optional[str] = Field(None, max_length=20)
    ccir: Optional[str] = Field(None, max_length=30)
    sigef_codigo: Optional[str] = Field(None, max_length=50)
    cep: Optional[str] = Field(None, max_length=9)
    logradouro: Optional[str] = Field(None, max_length=255)
    bairro: Optional[str] = Field(None, max_length=100)
    municipio: Optional[str] = Field(None, max_length=100)
    uf: Optional[str] = Field(None, min_length=2, max_length=2)
    ibge_municipio_codigo: Optional[str] = Field(None, max_length=7)
    area_total_ha: Optional[Decimal] = Field(None, gt=0)
    area_app_ha: Optional[Decimal] = Field(None, ge=0)
    area_rl_ha: Optional[Decimal] = Field(None, ge=0)
    coordenadas_sede: Optional[str] = Field(None, max_length=100)
    geometria: Optional[dict] = None
    ativo: Optional[bool] = None


# Backward compatibility aliases
FazendaCreate = UnidadeProdutivaCreate
FazendaUpdate = UnidadeProdutivaUpdate
