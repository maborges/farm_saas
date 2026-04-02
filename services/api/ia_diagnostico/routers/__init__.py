"""Routers para ia_diagnostico."""

from .pragas_doencas import router as pragas_doencas_router
from .tratamentos import router as tratamentos_router
from .diagnosticos import router as diagnosticos_router

__all__ = ["pragas_doencas_router", "tratamentos_router", "diagnosticos_router"]
