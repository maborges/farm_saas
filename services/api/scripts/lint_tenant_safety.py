#!/usr/bin/env python3
"""
lint_tenant_safety.py — Pre-commit / CI lint para segurança multi-tenant.

Detecta violações de padrão sem precisar de análise estática complexa.
Retorna exit code 1 se encontrar violações.

Regras:
  R1  — Depends(get_session) em router fora de core/ (deve usar get_session_with_tenant)
  R2  — from sqlalchemy import select em */router.py (queries devem ir pelo service)
  R3  — StorageService.save( sem save_and_track( no mesmo arquivo (storage não rastreado)
  R4  — session.add( sem flush nem commit posterior no mesmo bloco de método (risco de perda)

Uso:
  python scripts/lint_tenant_safety.py [--strict]

  --strict: falha também em warnings (R4), não apenas erros (R1-R3)
"""
import sys
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent  # services/api/

ERRORS: list[str] = []
WARNINGS: list[str] = []

# ---------------------------------------------------------------------------
# Legado — violações existentes antes da adoção do lint (2026-04-26).
# Não remova daqui sem corrigir o arquivo correspondente.
# Adicionar novos arquivos aqui é PROIBIDO — corrija antes de commitar.
# ---------------------------------------------------------------------------
_R1_LEGACY_FILES = {
    "agricola/cultivos/router.py",
    "agricola/a1_planejamento/router.py",
    "agricola/colheita/router.py",
    "financeiro/comercializacao/router.py",
}

_R2_LEGACY_FILES = {
    "agricola/caderno/router.py",
    "agricola/cultivos/router.py",
    "agricola/colheita/router.py",
    "agricola/rastreabilidade/public_router.py",
    "agricola/rastreabilidade/router.py",
    "core/cadastros/propriedades/propriedade_router.py",
    "core/cadastros/propriedades/propriedade_hierarquia_router.py",
    "core/cadastros/commodities/router.py",
    "core/cadastros/produtos/router.py",
    "core/cadastros/equipamentos/router.py",
    "ambiental/router.py",
    "financeiro/comercializacao/router.py",
}

_R3_LEGACY_FILES: set[str] = {
    "core/cadastros/propriedades/router.py",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _router_files():
    """Todos os */router.py fora de tests/ e scripts/."""
    return [
        p for p in ROOT.rglob("*router*.py")
        if "test" not in p.parts and "scripts" not in p.parts
    ]

def _service_files():
    return [
        p for p in ROOT.rglob("*service*.py")
        if "test" not in p.parts and "scripts" not in p.parts
    ]

def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))

# ---------------------------------------------------------------------------
# R1 — get_session em router fora de core/
# ---------------------------------------------------------------------------

_R1_PATTERN = re.compile(r"Depends\s*\(\s*get_session\s*\)")

def check_r1():
    for f in _router_files():
        parts = f.parts
        # core/ usa get_session internamente em gates — permitido
        if "core" in parts:
            continue
        rel = _rel(f)
        if rel in _R1_LEGACY_FILES:
            continue  # legado — ignorar até ser corrigido
        text = f.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            if _R1_PATTERN.search(line) and "get_session_with_tenant" not in line:
                ERRORS.append(
                    f"[R1] {rel}:{lineno} — Depends(get_session) em router tenant-scoped. "
                    f"Use Depends(get_session_with_tenant) para garantir RLS."
                )

# ---------------------------------------------------------------------------
# R2 — from sqlalchemy import select em router.py
# ---------------------------------------------------------------------------

_R2_PATTERN = re.compile(r"^\s*from sqlalchemy.*\bimport\b.*\bselect\b")

def check_r2():
    for f in _router_files():
        rel = _rel(f)
        if rel in _R2_LEGACY_FILES:
            continue  # legado — ignorar até ser corrigido
        text = f.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            if _R2_PATTERN.match(line):
                ERRORS.append(
                    f"[R2] {rel}:{lineno} — 'select' importado em router. "
                    f"Mova a query para um service (BaseService ou custom)."
                )

# ---------------------------------------------------------------------------
# R3 — StorageService.save( sem save_and_track( no mesmo arquivo
# ---------------------------------------------------------------------------

def check_r3():
    for f in ROOT.rglob("*.py"):
        if "test" in f.parts or "scripts" in f.parts:
            continue
        if "storage_service" in f.name:
            continue
        rel = _rel(f)
        if rel in _R3_LEGACY_FILES:
            continue  # legado — ignorar até ser corrigido
        text = f.read_text(encoding="utf-8")
        if "StorageService.save(" in text and "save_and_track(" not in text:
            ERRORS.append(
                f"[R3] {rel} — usa StorageService.save() sem save_and_track(). "
                f"Storage quota não será atualizado. Use save_and_track() de storage_service."
            )

# ---------------------------------------------------------------------------
# R4 — session.add( sem flush/commit próximo (warning, não erro)
# ---------------------------------------------------------------------------

_R4_ADD = re.compile(r"\bsession\.add\(")
_R4_FLUSH = re.compile(r"await session\.(flush|commit)\(")

def check_r4():
    for f in _service_files():
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()
        for lineno, line in enumerate(lines, 1):
            if _R4_ADD.search(line):
                # Verifica as próximas 5 linhas
                window = "\n".join(lines[lineno : lineno + 5])
                if not _R4_FLUSH.search(window):
                    WARNINGS.append(
                        f"[R4] {_rel(f)}:{lineno} — session.add() sem flush/commit nas 5 linhas seguintes. "
                        f"Verifique se o caller commita antes de retornar."
                    )

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    strict = "--strict" in sys.argv

    check_r1()
    check_r2()
    check_r3()
    check_r4()

    if ERRORS:
        print("\n🚨  ERROS DE SEGURANÇA ENCONTRADOS:\n")
        for e in ERRORS:
            print(f"  {e}")

    if WARNINGS:
        print("\n⚠️   AVISOS:\n")
        for w in WARNINGS:
            print(f"  {w}")

    if not ERRORS and not WARNINGS:
        print("✅  Nenhuma violação de segurança encontrada.")

    total_errors = len(ERRORS) + (len(WARNINGS) if strict else 0)
    if total_errors:
        print(f"\n{'Falha' if ERRORS else 'Avisos'}: {len(ERRORS)} erro(s), {len(WARNINGS)} aviso(s).")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
