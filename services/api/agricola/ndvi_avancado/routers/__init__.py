"""Routers para agricola/ndvi_avancado."""

from .ndvi import router as ndvi_router
from .irrigacao import router as irrigacao_router
from .meteorologia import router as meteorologia_router

__all__ = ["ndvi_router", "irrigacao_router", "meteorologia_router"]
