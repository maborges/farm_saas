"""Router para whatsapp."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_tenant, require_module

router = APIRouter(prefix="/whatsapp", tags=["Whatsapp"], dependencies=[Depends(require_module("EXT_IOT"))])


@router.get("/")
def listar_whatsapp(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista whatsapp."""
    # Implementar lógica aqui
    return []


@router.post("/", status_code=201)
def criar_whatsapp(
    # dados: WhatsappCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Cria whatsapp."""
    # Implementar lógica aqui
    return {}
