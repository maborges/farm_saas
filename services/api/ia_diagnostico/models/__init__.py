"""Models para ia_diagnostico."""

from .pragas_doencas import PragasDoencas
from .tratamentos import Tratamentos
from .diagnosticos import Diagnosticos
from .recomendacoes import Recomendacoes
from .modelos_ml import ModelosMl

__all__ = ["PragasDoencas", "Tratamentos", "Diagnosticos", "Recomendacoes", "ModelosMl"]
