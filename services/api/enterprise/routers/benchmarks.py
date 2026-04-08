"""Router para benchmarks."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_tenant, require_module

router = APIRouter(prefix="/benchmarks", tags=["Benchmarks"], dependencies=[Depends(require_module("EXT_IA"))])


@router.get("/")
def listar_benchmarks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista benchmarks."""
    # Implementar lógica aqui
    return []


@router.post("/", status_code=201)
def criar_benchmark(
    # dados: BenchmarkCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Cria benchmark."""
    # Implementar lógica aqui
    return {}
