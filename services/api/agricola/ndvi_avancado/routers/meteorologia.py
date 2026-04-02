"""Router para meteorologia."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_tenant

router = APIRouter(prefix="/meteorologia", tags=["Meteorologia"])


@router.get("/")
def listar_meteorologia(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista meteorologia."""
    # Implementar lógica aqui
    return []


@router.post("/", status_code=201)
def criar_meteorologia(
    # dados: MeteorologiaCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Cria meteorologia."""
    # Implementar lógica aqui
    return {}
