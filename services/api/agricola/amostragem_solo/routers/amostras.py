"""Router para amostras."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.constants import PlanTier
from core.database import get_db
from core.dependencies import get_current_tenant, require_module, require_tier

router = APIRouter(
    prefix="/amostras",
    tags=["Amostras"],
    dependencies=[
        Depends(require_module("A4_PRECISAO")),
        Depends(require_tier(PlanTier.PROFISSIONAL)),
    ],
)


@router.get("/")
def listar_amostras(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista amostras."""
    # Implementar lógica aqui
    return []


@router.post("/", status_code=201)
def criar_amostra(
    # dados: AmostraCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Cria amostra."""
    # Implementar lógica aqui
    return {}
