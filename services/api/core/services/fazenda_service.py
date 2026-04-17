# Backward compatibility shim — use unidade_produtiva_service instead
from core.services.unidade_produtiva_service import UnidadeProdutivaService, UnidadeProdutivaService as FazendaService

__all__ = ["FazendaService", "UnidadeProdutivaService"]
