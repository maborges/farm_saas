"""Router para pragas_doencas."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.constants import PlanTier
from core.database import get_db
from core.dependencies import get_current_tenant, require_module, require_tier

router = APIRouter(
    prefix="/pragas_doencas",
    tags=["Pragas_Doencas"],
    dependencies=[
        Depends(require_module("EXT_IA")),
        Depends(require_tier(PlanTier.PROFISSIONAL)),
    ],
)


@router.get("/")
def listar_pragas_doencas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista pragas_doencas."""
    # Implementar lógica aqui
    return []


@router.post("/", status_code=201)
def criar_pragas_doenca(
    # dados: Pragas_DoencaCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Cria pragas_doenca."""
    # Implementar lógica aqui
    return {}
