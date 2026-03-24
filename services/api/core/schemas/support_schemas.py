from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import List, Optional
from core.models.support import TicketStatus, TicketPriority

class MensagemChamadoBase(BaseModel):
    conteudo: str
    anexo_url: Optional[str] = None

class MensagemChamadoCreate(MensagemChamadoBase):
    pass

class MensagemChamadoResponse(MensagemChamadoBase):
    id: uuid.UUID
    chamado_id: uuid.UUID
    usuario_id: uuid.UUID
    is_admin_reply: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ChamadoSuporteBase(BaseModel):
    assunto: str
    categoria: str = "TECNICO"
    prioridade: TicketPriority = TicketPriority.MEDIA

class ChamadoSuporteCreate(ChamadoSuporteBase):
    mensagem_inicial: str

class ChamadoSuporteResponse(ChamadoSuporteBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    usuario_abertura_id: uuid.UUID
    status: TicketStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChamadoDetalheResponse(ChamadoSuporteResponse):
    mensagens: List[MensagemChamadoResponse] = []
