from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Dict, Any

class MensagemCreate(BaseModel):
    conversa_id: UUID | None = None # Se None, cria nova conversa
    conteudo: str
    contexto: dict | None = None # Para RAG (ex: talhao_id para puxar dados de solo)

class ConversaResponse(BaseModel):
    id: UUID
    titulo: str | None
    contexto_atual: dict | None
    historico_mensagens: list[dict]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class RespostaIA(BaseModel):
    conversa_id: UUID
    mensagem: str
