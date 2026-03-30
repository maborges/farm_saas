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

# RAT (Relatório Agrônomo Técnico)
class Constatacao(BaseModel):
    nome: str
    tipo: str # PRAGA, DOENCA, PLANTA_DANINHA, DEFICIENCIA_NUTRICIONAL
    nivel: str # BAIXO, MEDIO, ALTO
    posicao_planta: str | None = None
    fotos: List[str] = []

class RelatorioTecnicoCreate(BaseModel):
    safra_id: UUID
    talhao_id: UUID
    data_visita: datetime | None = None
    estadio_fenologico: str | None = None
    condicao_climatica: Dict[str, Any] | None = None
    observacoes_gerais: str | None = None
    recomendacoes: str | None = None
    constatacoes: List[Constatacao] = []
    status: str = "RASCUNHO"

class RelatorioTecnicoUpdate(BaseModel):
    data_visita: datetime | None = None
    estadio_fenologico: str | None = None
    condicao_climatica: Dict[str, Any] | None = None
    observacoes_gerais: str | None = None
    recomendacoes: str | None = None
    constatacoes: List[Constatacao] | None = None
    status: str | None = None

class RelatorioTecnicoResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    safra_id: UUID
    talhao_id: UUID
    usuario_id: UUID
    data_visita: datetime
    estadio_fenologico: str | None
    condicao_climatica: Dict[str, Any] | None
    observacoes_gerais: str | None
    recomendacoes: str | None
    constatacoes: List[Dict[str, Any]]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
