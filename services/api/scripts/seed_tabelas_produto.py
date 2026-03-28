"""
Seed: marcas, modelos e categorias de produto padrão do sistema (tenant_id = NULL).

Registros com tenant_id=NULL e sistema=True são exibidos para todos os tenants
e não podem ser editados ou excluídos por eles — apenas os próprios tenants podem
criar registros adicionais com tenant_id preenchido.

Uso:
    cd services/api
    source .venv/bin/activate
    python scripts/seed_tabelas_produto.py
"""
import asyncio
from sqlalchemy import select
from core.database import async_session_maker
import core.models  # noqa: F401

from core.cadastros.produtos.models import Marca, ModeloProduto, CategoriaProduto

# ---------------------------------------------------------------------------
# Marcas padrão
# ---------------------------------------------------------------------------

MARCAS = [
    # Insumos agrícolas
    {"nome": "Bayer",           "pais_origem": "Alemanha"},
    {"nome": "Syngenta",        "pais_origem": "Suíça"},
    {"nome": "BASF",            "pais_origem": "Alemanha"},
    {"nome": "Corteva",         "pais_origem": "EUA"},
    {"nome": "FMC",             "pais_origem": "EUA"},
    {"nome": "UPL",             "pais_origem": "Índia"},
    {"nome": "Nufarm",          "pais_origem": "Austrália"},
    {"nome": "Adama",           "pais_origem": "Israel"},
    {"nome": "Ihara",           "pais_origem": "Japão"},
    {"nome": "Summit Agro",     "pais_origem": "Japão"},
    # Sementes
    {"nome": "Pioneer",         "pais_origem": "EUA"},
    {"nome": "Nidera",          "pais_origem": "Argentina"},
    {"nome": "Brasmax",         "pais_origem": "Brasil"},
    {"nome": "TMG",             "pais_origem": "Brasil"},
    {"nome": "Don Mario",       "pais_origem": "Argentina"},
    # Fertilizantes
    {"nome": "Yara",            "pais_origem": "Noruega"},
    {"nome": "Mosaic",          "pais_origem": "EUA"},
    {"nome": "Heringer",        "pais_origem": "Brasil"},
    {"nome": "Fertipar",        "pais_origem": "Brasil"},
    # Máquinas
    {"nome": "John Deere",      "pais_origem": "EUA"},
    {"nome": "Case IH",         "pais_origem": "EUA"},
    {"nome": "New Holland",     "pais_origem": "EUA"},
    {"nome": "Valtra",          "pais_origem": "Finlândia"},
    {"nome": "Agrale",          "pais_origem": "Brasil"},
    {"nome": "Jacto",           "pais_origem": "Brasil"},
    {"nome": "Stara",           "pais_origem": "Brasil"},
    # Lubrificantes
    {"nome": "Shell",           "pais_origem": "Holanda"},
    {"nome": "Mobil",           "pais_origem": "EUA"},
    {"nome": "Castrol",         "pais_origem": "Reino Unido"},
    {"nome": "Total Energies",  "pais_origem": "França"},
    # EPIs e ferramentas
    {"nome": "3M",              "pais_origem": "EUA"},
    {"nome": "Bosch",           "pais_origem": "Alemanha"},
    {"nome": "Stanley",         "pais_origem": "EUA"},
    {"nome": "Wärtsilä",        "pais_origem": "Finlândia"},
]

# ---------------------------------------------------------------------------
# Modelos padrão (referenciados por nome de marca)
# ---------------------------------------------------------------------------

MODELOS = [
    # Bayer
    {"marca": "Bayer",      "nome": "Roundup Original",     "tipo_produto": "DEFENSIVO"},
    {"marca": "Bayer",      "nome": "Roundup WG",           "tipo_produto": "DEFENSIVO"},
    {"marca": "Bayer",      "nome": "Fox Xpro",             "tipo_produto": "DEFENSIVO"},
    {"marca": "Bayer",      "nome": "Priori Xtra",          "tipo_produto": "DEFENSIVO"},
    # Syngenta
    {"marca": "Syngenta",   "nome": "Elatus",               "tipo_produto": "DEFENSIVO"},
    {"marca": "Syngenta",   "nome": "Gramoxone 200",        "tipo_produto": "DEFENSIVO"},
    {"marca": "Syngenta",   "nome": "NK 7059 IPRO",         "tipo_produto": "SEMENTE"},
    # BASF
    {"marca": "BASF",       "nome": "Comet",                "tipo_produto": "DEFENSIVO"},
    {"marca": "BASF",       "nome": "Opera Ultra",          "tipo_produto": "DEFENSIVO"},
    # FMC
    {"marca": "FMC",        "nome": "Talstar 100 EC",       "tipo_produto": "DEFENSIVO"},
    # John Deere
    {"marca": "John Deere", "nome": "Série 5E",             "tipo_produto": None},
    {"marca": "John Deere", "nome": "Série 6M",             "tipo_produto": None},
    {"marca": "John Deere", "nome": "Série 7J",             "tipo_produto": None},
    {"marca": "John Deere", "nome": "S760",                 "tipo_produto": None},
    # Shell
    {"marca": "Shell",      "nome": "Rimula R4 X 15W-40",  "tipo_produto": "LUBRIFICANTE"},
    {"marca": "Shell",      "nome": "Helix HX7 10W-40",    "tipo_produto": "LUBRIFICANTE"},
    # Mobil
    {"marca": "Mobil",      "nome": "Delvac MX 15W-40",    "tipo_produto": "LUBRIFICANTE"},
]

# ---------------------------------------------------------------------------
# Categorias padrão (hierárquicas)
# ---------------------------------------------------------------------------

CATEGORIAS = [
    # Raízes
    {"nome": "Insumos Agrícolas",       "cor": "#16A34A", "icone": "sprout",      "ordem": 1,  "parent": None},
    {"nome": "Pecuária",                "cor": "#B45309", "icone": "beef",        "ordem": 2,  "parent": None},
    {"nome": "Máquinas e Peças",        "cor": "#1D4ED8", "icone": "tractor",     "ordem": 3,  "parent": None},
    {"nome": "Combustíveis",            "cor": "#DC2626", "icone": "fuel",        "ordem": 4,  "parent": None},
    {"nome": "Material Geral",          "cor": "#6B7280", "icone": "package",     "ordem": 5,  "parent": None},
    # Insumos Agrícolas → filhos
    {"nome": "Sementes",                "cor": "#15803D", "icone": "circle-dot",  "ordem": 1,  "parent": "Insumos Agrícolas"},
    {"nome": "Defensivos",              "cor": "#B91C1C", "icone": "flask-conical","ordem": 2, "parent": "Insumos Agrícolas"},
    {"nome": "Fertilizantes",           "cor": "#A16207", "icone": "beaker",      "ordem": 3,  "parent": "Insumos Agrícolas"},
    {"nome": "Inoculantes",             "cor": "#0F766E", "icone": "microscope",  "ordem": 4,  "parent": "Insumos Agrícolas"},
    {"nome": "Adjuvantes",              "cor": "#7C3AED", "icone": "droplets",    "ordem": 5,  "parent": "Insumos Agrícolas"},
    # Defensivos → filhos
    {"nome": "Herbicidas",              "cor": "#DC2626", "icone": "leaf",        "ordem": 1,  "parent": "Defensivos"},
    {"nome": "Fungicidas",              "cor": "#9333EA", "icone": "bug",         "ordem": 2,  "parent": "Defensivos"},
    {"nome": "Inseticidas",             "cor": "#EA580C", "icone": "bug",         "ordem": 3,  "parent": "Defensivos"},
    {"nome": "Nematicidas",             "cor": "#0369A1", "icone": "bug",         "ordem": 4,  "parent": "Defensivos"},
    # Fertilizantes → filhos
    {"nome": "Fertilizantes Sólidos",   "cor": "#92400E", "icone": "layers",      "ordem": 1,  "parent": "Fertilizantes"},
    {"nome": "Fertilizantes Líquidos",  "cor": "#0D9488", "icone": "droplets",    "ordem": 2,  "parent": "Fertilizantes"},
    {"nome": "Foliares",                "cor": "#65A30D", "icone": "leaf",        "ordem": 3,  "parent": "Fertilizantes"},
    # Pecuária → filhos
    {"nome": "Rações e Suplementos",    "cor": "#92400E", "icone": "beef",        "ordem": 1,  "parent": "Pecuária"},
    {"nome": "Medicamentos Veterinários","cor": "#BE185D","icone": "syringe",     "ordem": 2,  "parent": "Pecuária"},
    {"nome": "Vacinas",                 "cor": "#0284C7", "icone": "syringe",     "ordem": 3,  "parent": "Pecuária"},
    {"nome": "Minerais e Sal",          "cor": "#64748B", "icone": "gem",         "ordem": 4,  "parent": "Pecuária"},
    # Máquinas e Peças → filhos
    {"nome": "Peças de Reposição",      "cor": "#1E40AF", "icone": "wrench",      "ordem": 1,  "parent": "Máquinas e Peças"},
    {"nome": "Lubrificantes e Filtros", "cor": "#0C4A6E", "icone": "droplets",    "ordem": 2,  "parent": "Máquinas e Peças"},
    {"nome": "Pneus e Correias",        "cor": "#374151", "icone": "circle",      "ordem": 3,  "parent": "Máquinas e Peças"},
    {"nome": "Implementos",             "cor": "#1D4ED8", "icone": "tractor",     "ordem": 4,  "parent": "Máquinas e Peças"},
    # Material Geral → filhos
    {"nome": "EPI",                     "cor": "#F59E0B", "icone": "hard-hat",    "ordem": 1,  "parent": "Material Geral"},
    {"nome": "Ferramentas",             "cor": "#6B7280", "icone": "wrench",      "ordem": 2,  "parent": "Material Geral"},
    {"nome": "Escritório",              "cor": "#8B5CF6", "icone": "file-text",   "ordem": 3,  "parent": "Material Geral"},
    {"nome": "Limpeza e Higiene",       "cor": "#06B6D4", "icone": "sparkles",    "ordem": 4,  "parent": "Material Geral"},
]


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------

async def seed():
    async with async_session_maker() as session:
        print("\n── Marcas ──────────────────────────────────────────")
        marca_map: dict[str, Marca] = {}
        for item in MARCAS:
            stmt = select(Marca).where(Marca.nome == item["nome"], Marca.tenant_id.is_(None))
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if existing:
                print(f"  ✓ {item['nome']} já existe")
                marca_map[item["nome"]] = existing
                continue
            obj = Marca(tenant_id=None, sistema=True, ativo=True, **item)
            session.add(obj)
            await session.flush()
            marca_map[item["nome"]] = obj
            print(f"  + {item['nome']} criada")

        print("\n── Modelos ─────────────────────────────────────────")
        for item in MODELOS:
            marca = marca_map.get(item["marca"])
            if not marca:
                print(f"  ✗ Marca '{item['marca']}' não encontrada, pulando {item['nome']}")
                continue
            stmt = select(ModeloProduto).where(
                ModeloProduto.nome == item["nome"],
                ModeloProduto.marca_id == marca.id,
                ModeloProduto.tenant_id.is_(None),
            )
            if (await session.execute(stmt)).scalar_one_or_none():
                print(f"  ✓ {item['nome']} já existe")
                continue
            obj = ModeloProduto(
                tenant_id=None, sistema=True, ativo=True,
                marca_id=marca.id,
                nome=item["nome"],
                tipo_produto=item.get("tipo_produto"),
            )
            session.add(obj)
            print(f"  + {item['nome']} criado")

        print("\n── Categorias ──────────────────────────────────────")
        cat_map: dict[str, CategoriaProduto] = {}
        # Primeira passagem: raízes
        for item in CATEGORIAS:
            if item["parent"] is not None:
                continue
            stmt = select(CategoriaProduto).where(
                CategoriaProduto.nome == item["nome"],
                CategoriaProduto.tenant_id.is_(None),
                CategoriaProduto.parent_id.is_(None),
            )
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if existing:
                print(f"  ✓ {item['nome']} já existe")
                cat_map[item["nome"]] = existing
                continue
            obj = CategoriaProduto(
                tenant_id=None, sistema=True, ativo=True, parent_id=None,
                nome=item["nome"], cor=item.get("cor"), icone=item.get("icone"), ordem=item.get("ordem", 0),
            )
            session.add(obj)
            await session.flush()
            cat_map[item["nome"]] = obj
            print(f"  + {item['nome']} criada")

        # Segunda passagem: filhos
        for item in CATEGORIAS:
            if item["parent"] is None:
                continue
            parent = cat_map.get(item["parent"])
            if not parent:
                print(f"  ✗ Pai '{item['parent']}' não encontrado, pulando {item['nome']}")
                continue
            stmt = select(CategoriaProduto).where(
                CategoriaProduto.nome == item["nome"],
                CategoriaProduto.tenant_id.is_(None),
                CategoriaProduto.parent_id == parent.id,
            )
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if existing:
                print(f"  ✓   └ {item['nome']} já existe")
                cat_map[item["nome"]] = existing
                continue
            obj = CategoriaProduto(
                tenant_id=None, sistema=True, ativo=True, parent_id=parent.id,
                nome=item["nome"], cor=item.get("cor"), icone=item.get("icone"), ordem=item.get("ordem", 0),
            )
            session.add(obj)
            await session.flush()
            cat_map[item["nome"]] = obj
            print(f"  +   └ {item['nome']} criada")

        await session.commit()
    print("\nSeed concluído.")


if __name__ == "__main__":
    asyncio.run(seed())
