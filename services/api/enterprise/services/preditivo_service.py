"""Service para preditivo_service."""

from sqlalchemy.orm import Session


class PreditivoService:
    """Service para preditivo_service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Adicionar métodos aqui
    # def listar(self, tenant_id: str):
    #     return []
