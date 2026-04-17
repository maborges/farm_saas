# Backward compatibility shim — use unidade_produtiva_input instead
from core.schemas.unidade_produtiva_input import UnidadeProdutivaCreate, UnidadeProdutivaUpdate

FazendaCreate = UnidadeProdutivaCreate
FazendaUpdate = UnidadeProdutivaUpdate

__all__ = ["FazendaCreate", "FazendaUpdate", "UnidadeProdutivaCreate", "UnidadeProdutivaUpdate"]
