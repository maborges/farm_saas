"""Routers para agricola/amostragem_solo."""

from .amostras import router as amostras_router
from .mapas_fertilidade import router as mapas_fertilidade_router
from .prescricoes_vra import router as prescricoes_vra_router

__all__ = ["amostras_router", "mapas_fertilidade_router", "prescricoes_vra_router"]
