"""Router para irrigacao."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_tenant

router = APIRouter(prefix="/irrigacao", tags=["Irrigacao"])


@router.get("/")
def listar_irrigacao(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista irrigacao."""
    # Implementar lógica aqui
    return []


@router.post("/", status_code=201)
def criar_irrigacao(
    # dados: IrrigacaoCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Cria irrigacao."""
    # Implementar lógica aqui
    return {}
