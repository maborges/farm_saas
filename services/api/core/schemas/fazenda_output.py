# Backward compatibility shim — use unidade_produtiva_output instead
from core.schemas.unidade_produtiva_output import UnidadeProdutivaResponse

FazendaResponse = UnidadeProdutivaResponse

__all__ = ["FazendaResponse", "UnidadeProdutivaResponse"]
