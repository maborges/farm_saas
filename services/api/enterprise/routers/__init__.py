"""Routers para enterprise."""

from .sap import router as sap_router
from .powerbi import router as powerbi_router
from .benchmarks import router as benchmarks_router
from .preditivo import router as preditivo_router
from .pontos import router as pontos_router

__all__ = ["sap_router", "powerbi_router", "benchmarks_router", "preditivo_router", "pontos_router"]
