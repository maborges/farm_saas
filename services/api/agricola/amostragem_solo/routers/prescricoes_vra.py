"""Router para prescricoes_vra."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_tenant

router = APIRouter(prefix="/prescricoes_vra", tags=["Prescricoes_Vra"])


@router.get("/")
def listar_prescricoes_vra(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista prescricoes_vra."""
    # Implementar lógica aqui
    return []


@router.post("/", status_code=201)
def criar_prescricoes_vra(
    # dados: Prescricoes_VraCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Cria prescricoes_vra."""
    # Implementar lógica aqui
    return {}
