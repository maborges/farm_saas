# Re-exports for backwards compatibility
from core.cadastros.produtos.models import (
    Produto as ProdutoCatalogo,
    ProdutoAgricola as ProdutoAgricolaDetalhe,
    ProdutoEstoque as ProdutoEstoqueDetalhe,
)

__all__ = ["ProdutoCatalogo", "ProdutoAgricolaDetalhe", "ProdutoEstoqueDetalhe"]
