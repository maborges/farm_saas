"""Router para pontos."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_tenant

router = APIRouter(prefix="/pontos", tags=["Pontos"])


@router.get("/")
def listar_pontos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista pontos."""
    # Implementar lógica aqui
    return []


@router.post("/", status_code=201)
def criar_ponto(
    # dados: PontoCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Cria ponto."""
    # Implementar lógica aqui
    return {}
