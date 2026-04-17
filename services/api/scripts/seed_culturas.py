"""
Seed de culturas agrícolas padrão do sistema.

Cria o catálogo de culturas base com sistema=True (não editáveis pelo tenant).
Cada cultura vem com parâmetros agronômicos realistas para o contexto brasileiro.

Executar:
    cd services/api && .venv/bin/python scripts/seed_culturas.py
"""
import sys
import asyncio
sys.path.insert(0, '.')

from core.config import settings


CULTURAS_SEED = [
    # -----------------------------------------------------------------------
    # GRÃOS
    # -----------------------------------------------------------------------
    {
        "nome": "Soja",
        "nome_cientifico": "Glycine max",
        "grupo": "GRAOS",
        "ciclo_dias_min": 90,
        "ciclo_dias_max": 150,
        "espacamento_cm": 45.0,
        "populacao_plantas_ha": 250000,
        "produtividade_media_sc_ha": 60.0,
    },
    {
        "nome": "Milho",
        "nome_cientifico": "Zea mays",
        "grupo": "GRAOS",
        "ciclo_dias_min": 100,
        "ciclo_dias_max": 160,
        "espacamento_cm": 80.0,
        "populacao_plantas_ha": 60000,
        "produtividade_media_sc_ha": 100.0,
    },
    {
        "nome": "Trigo",
        "nome_cientifico": "Triticum aestivum",
        "grupo": "GRAOS",
        "ciclo_dias_min": 100,
        "ciclo_dias_max": 140,
        "espacamento_cm": 17.0,
        "populacao_plantas_ha": 2500000,
        "produtividade_media_sc_ha": 40.0,
    },
    {
        "nome": "Arroz",
        "nome_cientifico": "Oryza sativa",
        "grupo": "GRAOS",
        "ciclo_dias_min": 100,
        "ciclo_dias_max": 150,
        "espacamento_cm": 30.0,
        "populacao_plantas_ha": 200000,
        "produtividade_media_sc_ha": 50.0,
    },
    {
        "nome": "Feijão",
        "nome_cientifico": "Phaseolus vulgaris",
        "grupo": "GRAOS",
        "ciclo_dias_min": 70,
        "ciclo_dias_max": 100,
        "espacamento_cm": 50.0,
        "populacao_plantas_ha": 200000,
        "produtividade_media_sc_ha": 18.0,
    },
    {
        "nome": "Aveia",
        "nome_cientifico": "Avena sativa",
        "grupo": "GRAOS",
        "ciclo_dias_min": 90,
        "ciclo_dias_max": 120,
        "espacamento_cm": 17.0,
        "populacao_plantas_ha": 2000000,
        "produtividade_media_sc_ha": 30.0,
    },
    {
        "nome": "Cevada",
        "nome_cientifico": "Hordeum vulgare",
        "grupo": "GRAOS",
        "ciclo_dias_min": 90,
        "ciclo_dias_max": 120,
        "espacamento_cm": 17.0,
        "populacao_plantas_ha": 2200000,
        "produtividade_media_sc_ha": 35.0,
    },
    {
        "nome": "Sorgo",
        "nome_cientifico": "Sorghum bicolor",
        "grupo": "GRAOS",
        "ciclo_dias_min": 90,
        "ciclo_dias_max": 130,
        "espacamento_cm": 50.0,
        "populacao_plantas_ha": 150000,
        "produtividade_media_sc_ha": 60.0,
    },
    {
        "nome": "Milheto",
        "nome_cientifico": "Pennisetum glaucum",
        "grupo": "GRAOS",
        "ciclo_dias_min": 70,
        "ciclo_dias_max": 100,
        "espacamento_cm": 50.0,
        "populacao_plantas_ha": 150000,
        "produtividade_media_sc_ha": 30.0,
    },
    # -----------------------------------------------------------------------
    # FIBRAS
    # -----------------------------------------------------------------------
    {
        "nome": "Algodão",
        "nome_cientifico": "Gossypium hirsutum",
        "grupo": "FIBRAS",
        "ciclo_dias_min": 120,
        "ciclo_dias_max": 180,
        "espacamento_cm": 80.0,
        "populacao_plantas_ha": 100000,
        "produtividade_media_sc_ha": 50.0,
    },
    {
        "nome": "Sisal",
        "nome_cientifico": "Agave sisalana",
        "grupo": "FIBRAS",
        "ciclo_dias_min": 365,
        "ciclo_dias_max": 730,
        "espacamento_cm": 100.0,
        "populacao_plantas_ha": 4000,
        "produtividade_media_sc_ha": None,
    },
    # -----------------------------------------------------------------------
    # FRUTAS
    # -----------------------------------------------------------------------
    {
        "nome": "Laranja",
        "nome_cientifico": "Citrus × sinensis",
        "grupo": "FRUTAS",
        "ciclo_dias_min": 365,
        "ciclo_dias_max": 1095,
        "espacamento_cm": 600.0,
        "populacao_plantas_ha": 278,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Banana",
        "nome_cientifico": "Musa spp.",
        "grupo": "FRUTAS",
        "ciclo_dias_min": 270,
        "ciclo_dias_max": 400,
        "espacamento_cm": 300.0,
        "populacao_plantas_ha": 1100,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Maçã",
        "nome_cientifico": "Malus domestica",
        "grupo": "FRUTAS",
        "ciclo_dias_min": 365,
        "ciclo_dias_max": 1460,
        "espacamento_cm": 400.0,
        "populacao_plantas_ha": 625,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Uva",
        "nome_cientifico": "Vitis vinifera",
        "grupo": "FRUTAS",
        "ciclo_dias_min": 365,
        "ciclo_dias_max": 1095,
        "espacamento_cm": 200.0,
        "populacao_plantas_ha": 2500,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Manga",
        "nome_cientifico": "Mangifera indica",
        "grupo": "FRUTAS",
        "ciclo_dias_min": 730,
        "ciclo_dias_max": 1825,
        "espacamento_cm": 1000.0,
        "populacao_plantas_ha": 100,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Limão",
        "nome_cientifico": "Citrus × limon",
        "grupo": "FRUTAS",
        "ciclo_dias_min": 365,
        "ciclo_dias_max": 1095,
        "espacamento_cm": 600.0,
        "populacao_plantas_ha": 278,
        "produtividade_media_sc_ha": None,
    },
    # -----------------------------------------------------------------------
    # HORTALIÇAS
    # -----------------------------------------------------------------------
    {
        "nome": "Tomate",
        "nome_cientifico": "Solanum lycopersicum",
        "grupo": "HORTALICAS",
        "ciclo_dias_min": 80,
        "ciclo_dias_max": 140,
        "espacamento_cm": 60.0,
        "populacao_plantas_ha": 25000,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Cebola",
        "nome_cientifico": "Allium cepa",
        "grupo": "HORTALICAS",
        "ciclo_dias_min": 120,
        "ciclo_dias_max": 180,
        "espacamento_cm": 30.0,
        "populacao_plantas_ha": 350000,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Cenoura",
        "nome_cientifico": "Daucus carota",
        "grupo": "HORTALICAS",
        "ciclo_dias_min": 80,
        "ciclo_dias_max": 120,
        "espacamento_cm": 30.0,
        "populacao_plantas_ha": 400000,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Batata",
        "nome_cientifico": "Solanum tuberosum",
        "grupo": "HORTALICAS",
        "ciclo_dias_min": 80,
        "ciclo_dias_max": 120,
        "espacamento_cm": 70.0,
        "populacao_plantas_ha": 70000,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Alface",
        "nome_cientifico": "Lactuca sativa",
        "grupo": "HORTALICAS",
        "ciclo_dias_min": 30,
        "ciclo_dias_max": 60,
        "espacamento_cm": 30.0,
        "populacao_plantas_ha": 100000,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Pimenta",
        "nome_cientifico": "Capsicum spp.",
        "grupo": "HORTALICAS",
        "ciclo_dias_min": 90,
        "ciclo_dias_max": 150,
        "espacamento_cm": 60.0,
        "populacao_plantas_ha": 25000,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Pepino",
        "nome_cientifico": "Cucumis sativus",
        "grupo": "HORTALICAS",
        "ciclo_dias_min": 60,
        "ciclo_dias_max": 90,
        "espacamento_cm": 50.0,
        "populacao_plantas_ha": 30000,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Brócolis",
        "nome_cientifico": "Brassica oleracea var. italica",
        "grupo": "HORTALICAS",
        "ciclo_dias_min": 60,
        "ciclo_dias_max": 90,
        "espacamento_cm": 50.0,
        "populacao_plantas_ha": 40000,
        "produtividade_media_sc_ha": None,
    },
    # -----------------------------------------------------------------------
    # PASTAGEM
    # -----------------------------------------------------------------------
    {
        "nome": "Braquiária",
        "nome_cientifico": "Urochloa brizantha",
        "grupo": "PASTAGEM",
        "ciclo_dias_min": 60,
        "ciclo_dias_max": 365,
        "espacamento_cm": 50.0,
        "populacao_plantas_ha": None,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Brizantha",
        "nome_cientifico": "Urochloa brizantha cv. Marandu",
        "grupo": "PASTAGEM",
        "ciclo_dias_min": 60,
        "ciclo_dias_max": 365,
        "espacamento_cm": 50.0,
        "populacao_plantas_ha": None,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Mombaça",
        "nome_cientifico": "Megathyrsus maximus cv. Mombaça",
        "grupo": "PASTAGEM",
        "ciclo_dias_min": 60,
        "ciclo_dias_max": 365,
        "espacamento_cm": 50.0,
        "populacao_plantas_ha": None,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Tanzânia",
        "nome_cientifico": "Megathyrsus maximus cv. Tanzânia",
        "grupo": "PASTAGEM",
        "ciclo_dias_min": 60,
        "ciclo_dias_max": 365,
        "espacamento_cm": 50.0,
        "populacao_plantas_ha": None,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Aries",
        "nome_cientifico": "Avena sativa × Avena strigosa",
        "grupo": "PASTAGEM",
        "ciclo_dias_min": 60,
        "ciclo_dias_max": 180,
        "espacamento_cm": 17.0,
        "populacao_plantas_ha": 2000000,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Azevém",
        "nome_cientifico": "Lolium multiflorum",
        "grupo": "PASTAGEM",
        "ciclo_dias_min": 90,
        "ciclo_dias_max": 240,
        "espacamento_cm": 17.0,
        "populacao_plantas_ha": 2000000,
        "produtividade_media_sc_ha": None,
    },
    # -----------------------------------------------------------------------
    # OUTROS
    # -----------------------------------------------------------------------
    {
        "nome": "Cana-de-Açúcar",
        "nome_cientifico": "Saccharum officinarum",
        "grupo": "OUTRO",
        "ciclo_dias_min": 365,
        "ciclo_dias_max": 540,
        "espacamento_cm": 150.0,
        "populacao_plantas_ha": None,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Café",
        "nome_cientifico": "Coffea arabica",
        "grupo": "OUTRO",
        "ciclo_dias_min": 365,
        "ciclo_dias_max": 1095,
        "espacamento_cm": 300.0,
        "populacao_plantas_ha": 5000,
        "produtividade_media_sc_ha": 40.0,
    },
    {
        "nome": "Eucalipto",
        "nome_cientifico": "Eucalyptus spp.",
        "grupo": "OUTRO",
        "ciclo_dias_min": 1825,
        "ciclo_dias_max": 2555,
        "espacamento_cm": 300.0,
        "populacao_plantas_ha": 1111,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Mandioca",
        "nome_cientifico": "Manihot esculenta",
        "grupo": "OUTRO",
        "ciclo_dias_min": 240,
        "ciclo_dias_max": 365,
        "espacamento_cm": 100.0,
        "populacao_plantas_ha": 12000,
        "produtividade_media_sc_ha": None,
    },
    {
        "nome": "Girassol",
        "nome_cientifico": "Helianthus annuus",
        "grupo": "OUTRO",
        "ciclo_dias_min": 90,
        "ciclo_dias_max": 120,
        "espacamento_cm": 70.0,
        "populacao_plantas_ha": 50000,
        "produtividade_media_sc_ha": 30.0,
    },
    {
        "nome": "Amendoim",
        "nome_cientifico": "Arachis hypogaea",
        "grupo": "OUTRO",
        "ciclo_dias_min": 90,
        "ciclo_dias_max": 150,
        "espacamento_cm": 50.0,
        "populacao_plantas_ha": 200000,
        "produtividade_media_sc_ha": 40.0,
    },
    {
        "nome": "Canola",
        "nome_cientifico": "Brassica napus",
        "grupo": "OUTRO",
        "ciclo_dias_min": 100,
        "ciclo_dias_max": 130,
        "espacamento_cm": 17.0,
        "populacao_plantas_ha": 3000000,
        "produtividade_media_sc_ha": 25.0,
    },
]


async def run_seed():
    import asyncpg

    url = str(settings.database_url).replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(url)

    created_count = 0
    skipped_count = 0

    for item in CULTURAS_SEED:
        nome = item["nome"]
        nome_cientifico = item.get("nome_cientifico")

        # Verificar se já existe (por nome + grupo)
        exists = await conn.fetchval(
            "SELECT id FROM cadastros_culturas WHERE nome = $1 AND grupo = $2 AND sistema = true",
            nome,
            item["grupo"],
        )
        if exists:
            print(f"  ⏭️  {nome} — já existe, pulando")
            skipped_count += 1
            continue

        # Inserir cultura
        await conn.execute("""
            INSERT INTO cadastros_culturas (
                id, tenant_id, sistema, nome, nome_cientifico, grupo,
                ciclo_dias_min, ciclo_dias_max, espacamento_cm,
                populacao_plantas_ha, produtividade_media_sc_ha,
                dados_extras, ativa, created_at, updated_at
            ) VALUES (
                gen_random_uuid(), NULL, true,
                $1, $2, $3,
                $4, $5, $6,
                $7, $8,
                NULL, true, NOW(), NOW()
            )
        """,
            nome,
            nome_cientifico,
            item["grupo"],
            item.get("ciclo_dias_min"),
            item.get("ciclo_dias_max"),
            item.get("espacamento_cm"),
            item.get("populacao_plantas_ha"),
            item.get("produtividade_media_sc_ha"),
        )

        created_count += 1
        print(f"  ✅ {nome} ({nome_cientifico}) — criada")

    await conn.close()

    print()
    print("=" * 60)
    print(f"  Criadas:  {created_count}")
    print(f"  Puladas:  {skipped_count}")
    print("=" * 60)

    if created_count == 0:
        print("  Nenhuma cultura nova criada (todas já existiam).")
    else:
        print("  ✅ Seed concluído com sucesso!")


if __name__ == "__main__":
    print("=" * 60)
    print("  Seed — Culturas Agrícolas Padrão do Sistema")
    print("=" * 60)
    print()
    asyncio.run(run_seed())
