"""Router para keys."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_tenant

router = APIRouter(prefix="/keys", tags=["Keys"])


@router.get("/")
def listar_keys(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista keys."""
    # Implementar lógica aqui
    return []


@router.post("/", status_code=201)
def criar_key(
    # dados: KeyCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Cria key."""
    # Implementar lógica aqui
    return {}
