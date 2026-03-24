"""
Módulo A1 - Planejamento de Safra e Orçamento
ID: A1_PLANEJAMENTO
Categoria: AGRICOLA

Responsável por:
- Gestão de ciclos de safra (PRINCIPAL, SAFRINHA, PERENE)
- Orçamento vs Realizado
- Projeções de receita e margem
- Rotação de culturas
"""

from .router import router

__all__ = ["router"]
