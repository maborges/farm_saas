from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import datetime
import uuid


class UnidadeProdutivaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    nome: str
    tipo_propriedade: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    codigo_car: Optional[str] = None
    nirf: Optional[str] = None
    ccir: Optional[str] = None
    sigef_codigo: Optional[str] = None
    # Localização
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    bairro: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    ibge_municipio_codigo: Optional[str] = None
    # Áreas
    area_total_ha: Optional[Decimal] = None
    area_app_ha: Optional[Decimal] = None
    area_rl_ha: Optional[Decimal] = None
    coordenadas_sede: Optional[str] = None
    geometria: Optional[dict] = None
    logo_url: Optional[str] = None
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Backward compatibility alias
FazendaResponse = UnidadeProdutivaResponse
