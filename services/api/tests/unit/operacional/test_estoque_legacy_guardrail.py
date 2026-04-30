from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[5]
FORBIDDEN_REFERENCES = ("MovimentacaoEstoque", "estoque_movimentacoes")
SEARCH_ROOTS = (
    REPO_ROOT / "services/api",
    REPO_ROOT / "apps/web/services/api",
)
IGNORED_DIR_NAMES = {
    "__pycache__",
    ".venv",
    "migrations",
    "tests",
    "scripts",
    "docs",
}
IGNORED_FILE_NAMES = {
    "test_estoque_legacy_guardrail.py",
}


def _iter_active_python_files() -> list[Path]:
    files: list[Path] = []
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if any(part in IGNORED_DIR_NAMES for part in path.parts):
                continue
            if path.name in IGNORED_FILE_NAMES:
                continue
            files.append(path)
    return files


def test_estoque_legacy_terms_absent_from_active_code() -> None:
    violations: list[str] = []

    for path in sorted(_iter_active_python_files()):
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for forbidden in FORBIDDEN_REFERENCES:
                if forbidden in line:
                    relpath = path.relative_to(REPO_ROOT)
                    violations.append(f"{relpath}:{lineno}: {forbidden}")

    assert not violations, "Referências legadas de estoque encontradas em código ativo:\n" + "\n".join(violations)
