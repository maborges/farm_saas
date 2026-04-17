# Backward compatibility shim — use unidade_produtiva instead
from core.models.unidade_produtiva import UnidadeProdutiva, UnidadeProdutiva as Fazenda

__all__ = ["Fazenda", "UnidadeProdutiva"]
