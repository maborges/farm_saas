# Módulo legado — mantido apenas para compatibilidade de imports existentes.
# O modelo canônico é pecuaria.animal.models.LoteAnimal (tabela pec_lotes).
# Este arquivo será removido na Onda 4 (limpeza final).
from pecuaria.animal.models import LoteAnimal as LoteBovino

__all__ = ["LoteBovino"]
