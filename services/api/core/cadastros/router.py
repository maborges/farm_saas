"""
Router de cadastros genéricos — endpoints auxiliares.

NOTA: Os endpoints de produtos foram movidos para `core/cadastros/produtos/router.py`.
Este arquivo mantém apenas endpoints auxiliares que não estejam duplicados.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/cadastros", tags=["Cadastros — Auxiliares"])

# Endpoints de produtos foram removidos — use /cadastros/produtos (Router B)
