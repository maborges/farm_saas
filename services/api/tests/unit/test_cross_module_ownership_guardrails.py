"""Static guardrails for cross-module ownership decisions.

These tests intentionally avoid importing application models or touching the
database. They only scan model files for new table/file names that would
recreate entities already assigned to canonical owners in Step 48.
"""

from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
API_ROOT = REPO_ROOT / "services" / "api"

PROHIBITED_NAME_PATTERNS = (
    "fazendas",
    "fornecedores",
    "clientes",
    "produtos_estoque",
    "insumos_agricolas",
    "estoque_agricola",
    "estoque_pecuario",
    "maquina_veiculo",
)

# Exact legacy/canonical exceptions documented in Step 48. New files or table
# names matching the patterns above must not be added to this allowlist without
# citing docs/contexts/step48-cross-module-ownership-context.md.
ALLOWED_TABLES = {
    ("services/api/operacional/models/compras.py", "compras_fornecedores"),
    ("services/api/core/cadastros/produtos/models.py", "cadastros_produtos_estoque"),
}

ALLOWED_MODEL_FILES = {
    "services/api/core/models/fazenda.py",
    "services/api/operacional/models/compras.py",
    "services/api/core/cadastros/produtos/models.py",
}


def _iter_model_files() -> list[Path]:
    ignored_parts = {".venv", "__pycache__", "migrations", "tests"}
    files: list[Path] = []
    for path in API_ROOT.rglob("*.py"):
        if ignored_parts.intersection(path.parts):
            continue
        relative_parts = path.relative_to(API_ROOT).parts
        if path.name == "models.py" or "models" in relative_parts:
            files.append(path)
    return sorted(files)


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _extract_tablenames(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    tablenames: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "__tablename__" for target in node.targets):
            continue
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            tablenames.append(node.value.value)
    return tablenames


def _matches_prohibited_pattern(value: str) -> bool:
    normalized = value.lower()
    return any(pattern in normalized for pattern in PROHIBITED_NAME_PATTERNS)


def test_no_new_cross_module_duplicate_table_names() -> None:
    violations: list[str] = []

    for path in _iter_model_files():
        relative = _relative(path)
        for tablename in _extract_tablenames(path):
            if not _matches_prohibited_pattern(tablename):
                continue
            if (relative, tablename) in ALLOWED_TABLES:
                continue
            violations.append(f"{relative}: __tablename__ = {tablename!r}")

    assert not violations, (
        "Tabela/model duplicando entidade cross-modulo ja canonica. "
        "Use as fontes do Step 48 ou justifique excecao de ownership:\n"
        + "\n".join(violations)
    )


def test_no_new_cross_module_duplicate_model_file_names() -> None:
    violations: list[str] = []

    for path in _iter_model_files():
        relative = _relative(path)
        path_without_suffix = relative.removesuffix(".py").lower()
        if relative in ALLOWED_MODEL_FILES:
            continue
        if _matches_prohibited_pattern(path_without_suffix):
            violations.append(relative)

    assert not violations, (
        "Arquivo de model sugere novo cadastro/fluxo paralelo para entidade "
        "cross-modulo canonica. Cite o Step 48 para excecoes:\n"
        + "\n".join(violations)
    )
