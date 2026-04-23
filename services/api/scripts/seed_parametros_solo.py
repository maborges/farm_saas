"""
Seed de parâmetros de interpretação de solo para culturas do sistema.

Baseado nas tabelas Embrapa para cerrado brasileiro (padrão geral, sem região).
Executar após seed_culturas.py:
    cd services/api && .venv/bin/python scripts/seed_parametros_solo.py
"""
import sys
import asyncio
sys.path.insert(0, ".")

from core.config import settings

# Parâmetros por cultura: lista de faixas por parâmetro
# Estrutura: (parametro, faixa_min, faixa_max, classificacao, rec_dose_kg_ha, obs)
PARAMETROS = {
    "Soja": {
        "v_meta_pct_padrao": 60.0,
        "faixas": [
            # Fósforo mg/dm³
            ("FOSFORO", 0,    6,    "MUITO_BAIXO", 130, "P muito baixo. Aplicar 130 kg/ha P₂O₅ + incorporar calcário."),
            ("FOSFORO", 6,    12,   "BAIXO",       100, "P baixo. Aplicar 100 kg/ha P₂O₅."),
            ("FOSFORO", 12,   25,   "MEDIO",        65, "P médio. Aplicar 65 kg/ha P₂O₅."),
            ("FOSFORO", 25,   None, "ALTO",          35, "P alto. Manutenção: 35 kg/ha P₂O₅."),
            # Potássio mg/dm³
            ("POTASSIO", 0,    70,   "BAIXO",  130, "K baixo. Aplicar 130 kg/ha K₂O."),
            ("POTASSIO", 70,   150,  "MEDIO",   75, "K médio. Aplicar 75 kg/ha K₂O."),
            ("POTASSIO", 150,  None, "ALTO",    45, "K alto. Manutenção: 45 kg/ha K₂O."),
            # Nitrogênio (referência para inoculação)
            ("NITROGENIO", 0, None, "PADRAO", 30,
             "Soja: inoculação com Bradyrhizobium spp. + 20–30 kg/ha N foliar em caso de déficit."),
        ],
    },
    "Milho": {
        "v_meta_pct_padrao": 60.0,
        "faixas": [
            ("FOSFORO", 0,    6,    "MUITO_BAIXO", 130, "P muito baixo. Aplicar 130 kg/ha P₂O₅."),
            ("FOSFORO", 6,    12,   "BAIXO",       100, "P baixo. Aplicar 100 kg/ha P₂O₅."),
            ("FOSFORO", 12,   25,   "MEDIO",        70, "P médio. Aplicar 70 kg/ha P₂O₅."),
            ("FOSFORO", 25,   None, "ALTO",          40, "P alto. Manutenção: 40 kg/ha P₂O₅."),
            ("POTASSIO", 0,    70,   "BAIXO",  120, "K baixo. Aplicar 120 kg/ha K₂O."),
            ("POTASSIO", 70,   150,  "MEDIO",   80, "K médio. Aplicar 80 kg/ha K₂O."),
            ("POTASSIO", 150,  None, "ALTO",    50, "K alto. Manutenção: 50 kg/ha K₂O."),
            ("NITROGENIO", 0, None, "PADRAO", 160,
             "Milho: 35 kg/ha N na semeadura + 125 kg/ha N em cobertura (V4–V6)."),
        ],
    },
    "Trigo": {
        "v_meta_pct_padrao": 65.0,
        "faixas": [
            ("FOSFORO", 0,    6,    "MUITO_BAIXO", 110, "P muito baixo. Aplicar 110 kg/ha P₂O₅."),
            ("FOSFORO", 6,    12,   "BAIXO",        90, "P baixo. Aplicar 90 kg/ha P₂O₅."),
            ("FOSFORO", 12,   25,   "MEDIO",         60, "P médio. Aplicar 60 kg/ha P₂O₅."),
            ("FOSFORO", 25,   None, "ALTO",           30, "P alto. Manutenção: 30 kg/ha P₂O₅."),
            ("POTASSIO", 0,    70,   "BAIXO",   90, "K baixo. Aplicar 90 kg/ha K₂O."),
            ("POTASSIO", 70,   150,  "MEDIO",   60, "K médio. Aplicar 60 kg/ha K₂O."),
            ("POTASSIO", 150,  None, "ALTO",    40, "K alto. Manutenção: 40 kg/ha K₂O."),
            ("NITROGENIO", 0, None, "PADRAO", 80,
             "Trigo: 20 kg/ha N na semeadura + 60 kg/ha N em cobertura (perfilhamento)."),
        ],
    },
    "Café": {
        "v_meta_pct_padrao": 50.0,
        "faixas": [
            ("FOSFORO", 0,    5,    "MUITO_BAIXO", 150, "P muito baixo para café. Aplicar 150 kg/ha P₂O₅."),
            ("FOSFORO", 5,    10,   "BAIXO",       120, "P baixo. Aplicar 120 kg/ha P₂O₅."),
            ("FOSFORO", 10,   20,   "MEDIO",        80, "P médio. Aplicar 80 kg/ha P₂O₅."),
            ("FOSFORO", 20,   None, "ALTO",          40, "P alto. Manutenção: 40 kg/ha P₂O₅."),
            ("POTASSIO", 0,    80,   "BAIXO",  150, "K baixo para café. Aplicar 150 kg/ha K₂O."),
            ("POTASSIO", 80,   160,  "MEDIO",  100, "K médio. Aplicar 100 kg/ha K₂O."),
            ("POTASSIO", 160,  None, "ALTO",    60, "K alto. Manutenção: 60 kg/ha K₂O."),
            ("NITROGENIO", 0, None, "PADRAO", 200,
             "Café: parcelar 200 kg/ha N em 4–6 aplicações ao longo do ciclo produtivo."),
        ],
    },
    "Algodão": {
        "v_meta_pct_padrao": 60.0,
        "faixas": [
            ("FOSFORO", 0,    6,    "MUITO_BAIXO", 130, "P muito baixo. Aplicar 130 kg/ha P₂O₅."),
            ("FOSFORO", 6,    12,   "BAIXO",       100, "P baixo. Aplicar 100 kg/ha P₂O₅."),
            ("FOSFORO", 12,   25,   "MEDIO",        70, "P médio. Aplicar 70 kg/ha P₂O₅."),
            ("FOSFORO", 25,   None, "ALTO",          40, "P alto. Manutenção: 40 kg/ha P₂O₅."),
            ("POTASSIO", 0,    70,   "BAIXO",  130, "K baixo. Aplicar 130 kg/ha K₂O."),
            ("POTASSIO", 70,   150,  "MEDIO",   90, "K médio. Aplicar 90 kg/ha K₂O."),
            ("POTASSIO", 150,  None, "ALTO",    55, "K alto. Manutenção: 55 kg/ha K₂O."),
            ("NITROGENIO", 0, None, "PADRAO", 120,
             "Algodão: 30 kg/ha N na semeadura + 90 kg/ha N em cobertura (B1–B2)."),
        ],
    },
    "Cana-de-Açúcar": {
        "v_meta_pct_padrao": 60.0,
        "faixas": [
            ("FOSFORO", 0,    10,   "BAIXO",  120, "P baixo para cana. Aplicar 120 kg/ha P₂O₅."),
            ("FOSFORO", 10,   25,   "MEDIO",   80, "P médio. Aplicar 80 kg/ha P₂O₅."),
            ("FOSFORO", 25,   None, "ALTO",    40, "P alto. Manutenção: 40 kg/ha P₂O₅."),
            ("POTASSIO", 0,    80,   "BAIXO",  150, "K baixo. Aplicar 150 kg/ha K₂O."),
            ("POTASSIO", 80,   160,  "MEDIO",  100, "K médio. Aplicar 100 kg/ha K₂O."),
            ("POTASSIO", 160,  None, "ALTO",    60, "K alto. Manutenção: 60 kg/ha K₂O."),
            ("NITROGENIO", 0, None, "PADRAO", 120,
             "Cana-planta: 30–40 kg/ha N no plantio. Cana-soca: 80–100 kg/ha N após corte."),
        ],
    },
}


async def run_seed():
    import asyncpg

    url = str(settings.database_url).replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(url)

    created = 0
    skipped = 0

    for nome_cultura, dados in PARAMETROS.items():
        # Buscar cultura do sistema
        cultura_id = await conn.fetchval(
            "SELECT id FROM cadastros_culturas WHERE nome = $1 AND sistema = true",
            nome_cultura,
        )
        if not cultura_id:
            print(f"  ⚠️  Cultura '{nome_cultura}' não encontrada — execute seed_culturas.py primeiro")
            continue

        # Atualizar v_meta_pct_padrao
        await conn.execute(
            "UPDATE cadastros_culturas SET v_meta_pct_padrao = $1 WHERE id = $2",
            dados["v_meta_pct_padrao"],
            cultura_id,
        )

        for (parametro, faixa_min, faixa_max, classificacao, rec_dose, obs) in dados["faixas"]:
            exists = await conn.fetchval(
                """SELECT id FROM solo_parametros_cultura
                   WHERE cultura_id=$1 AND tenant_id IS NULL AND regiao IS NULL
                   AND parametro=$2 AND faixa_min=$3""",
                cultura_id, parametro, faixa_min,
            )
            if exists:
                skipped += 1
                continue

            await conn.execute(
                """INSERT INTO solo_parametros_cultura
                   (id, cultura_id, tenant_id, regiao, parametro,
                    faixa_min, faixa_max, classificacao, rec_dose_kg_ha, obs,
                    created_at, updated_at)
                   VALUES (gen_random_uuid(), $1, NULL, NULL, $2,
                           $3, $4, $5, $6, $7, NOW(), NOW())""",
                cultura_id, parametro, faixa_min, faixa_max, classificacao, rec_dose, obs,
            )
            created += 1

        print(f"  ✅ {nome_cultura} — parâmetros processados")

    await conn.close()

    print()
    print("=" * 60)
    print(f"  Criados: {created}  |  Pulados: {skipped}")
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("  Seed — Parâmetros de Solo por Cultura (Embrapa)")
    print("=" * 60)
    print()
    asyncio.run(run_seed())
