"""Routers para iot_integracao."""

from .john_deere import router as john_deere_router
from .case_ih import router as case_ih_router
from .whatsapp import router as whatsapp_router
from .comparador_precos import router as comparador_precos_router

__all__ = ["john_deere_router", "case_ih_router", "whatsapp_router", "comparador_precos_router"]
