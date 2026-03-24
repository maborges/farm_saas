"""Seed: tipos de relacionamento padrão do sistema (tenant_id = NULL)."""
import asyncio
from sqlalchemy import select
from core.database import async_session_maker
import core.models  # noqa: F401 — garante que todas as tabelas estão registradas no metadata
from core.cadastros.pessoas.models import TipoRelacionamento

DEFAULTS = [
    {"codigo": "FORNECEDOR",          "nome": "Fornecedor",              "cor": "#F59E0B", "icone": "truck"},
    {"codigo": "CLIENTE",             "nome": "Cliente",                 "cor": "#10B981", "icone": "user-check"},
    {"codigo": "PARCEIRO",            "nome": "Parceiro",                "cor": "#6366F1", "icone": "handshake"},
    {"codigo": "PRESTADOR",           "nome": "Prestador de Serviço",    "cor": "#8B5CF6", "icone": "wrench"},
    {"codigo": "TRANSPORTADORA",      "nome": "Transportadora",          "cor": "#3B82F6", "icone": "truck-moving"},
    {"codigo": "COLABORADOR",         "nome": "Colaborador / Funcionário","cor": "#EC4899", "icone": "hard-hat"},
    {"codigo": "PROPRIETARIO",        "nome": "Proprietário / Arrendador","cor": "#0EA5E9", "icone": "landmark"},
    {"codigo": "ORGAO",               "nome": "Órgão / Instituição",     "cor": "#64748B", "icone": "building-2"},
    {"codigo": "RESPONSAVEL_TECNICO", "nome": "Responsável Técnico",     "cor": "#14B8A6", "icone": "clipboard-check"},
]


async def seed():
    async with async_session_maker() as session:
        for item in DEFAULTS:
            stmt = select(TipoRelacionamento).where(
                TipoRelacionamento.codigo == item["codigo"],
                TipoRelacionamento.tenant_id.is_(None),
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                print(f"  ✓ {item['codigo']} já existe")
                continue
            tipo = TipoRelacionamento(
                tenant_id=None,
                sistema=True,
                ativo=True,
                descricao=None,
                **item,
            )
            session.add(tipo)
            print(f"  + {item['codigo']} criado")
        await session.commit()
    print("Seed concluído.")


if __name__ == "__main__":
    asyncio.run(seed())
