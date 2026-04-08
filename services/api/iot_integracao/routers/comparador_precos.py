"""Router para comparador_precos."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_tenant, require_module

router = APIRouter(prefix="/comparador_precos", tags=["Comparador_Precos"], dependencies=[Depends(require_module("EXT_IOT"))])


@router.get("/")
def listar_comparador_precos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista comparador_precos."""
    # Implementar lógica aqui
    return []


@router.post("/", status_code=201)
def criar_comparador_preco(
    # dados: Comparador_PrecoCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Cria comparador_preco."""
    # Implementar lógica aqui
    return {}
