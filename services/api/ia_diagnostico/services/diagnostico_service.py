"""Service para diagnostico_service."""

from sqlalchemy.orm import Session


class DiagnosticoService:
    """Service para diagnostico_service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Adicionar métodos aqui
    # def listar(self, tenant_id: str):
    #     return []
