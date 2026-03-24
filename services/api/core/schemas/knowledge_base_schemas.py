from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import List, Optional

class ConhecimentoCategoriaBase(BaseModel):
    nome: str
    icone: Optional[str] = None
    ordem: int = 0

class ConhecimentoCategoriaCreate(ConhecimentoCategoriaBase):
    pass

class ConhecimentoCategoriaResponse(ConhecimentoCategoriaBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class ConhecimentoArtigoBase(BaseModel):
    categoria_id: uuid.UUID
    titulo: str
    slug: str
    conteudo: str
    is_publico: bool = True

class ConhecimentoArtigoCreate(ConhecimentoArtigoBase):
    pass

class ConhecimentoArtigoUpdate(BaseModel):
    categoria_id: Optional[uuid.UUID] = None
    titulo: Optional[str] = None
    slug: Optional[str] = None
    conteudo: Optional[str] = None
    is_publico: Optional[bool] = None

class ConhecimentoArtigoResponse(ConhecimentoArtigoBase):
    id: uuid.UUID
    visualizacoes: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoriaComArtigosResponse(ConhecimentoCategoriaResponse):
    artigos: List[ConhecimentoArtigoResponse] = []
