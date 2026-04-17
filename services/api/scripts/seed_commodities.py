"""
Seed de commodities padrão do sistema.

Cria as commodities base com sistema=True (não editáveis pelo tenant).
Cada commodity já vem com suas classificações de qualidade padrão.

Executar:
    cd services/api && .venv/bin/python scripts/seed_commodities.py
"""
import sys
import asyncio
sys.path.insert(0, '.')

from core.config import settings
from core.cadastros.commodities.models import (
    TipoCommodity, UnidadeCommodity,
    Commodity, CommodityClassificacao,
)

COMMODITIES_SEED = [
    # -----------------------------------------------------------------------
    # AGRÍCOLAS
    # -----------------------------------------------------------------------
    {
        "nome": "Soja",
        "codigo": "SOJA",
        "descricao": "Grão de soja (Glycine max) — principal commodity agrícola do Brasil",
        "tipo": TipoCommodity.AGRICOLA.value,
        "unidade_padrao": UnidadeCommodity.SACA_60KG.value,
        "peso_unidade": 60.0,
        "umidade_padrao_pct": 14.0,
        "impureza_padrao_pct": 1.0,
        "possui_cotacao": True,
        "bolsa_referencia": "CBOT",
        "codigo_bolsa": "ZS",
        "classificacoes": [
            {"classe": "TIPO_1", "descricao": "Soja tipo 1 — padrão de mercado", "umidade_max_pct": 14.0, "impureza_max_pct": 1.0, "avariados_max_pct": 4.0},
            {"classe": "TIPO_2", "descricao": "Soja tipo 2 — aceitável com desconto", "umidade_max_pct": 15.0, "impureza_max_pct": 2.0, "avariados_max_pct": 8.0},
            {"classe": "FORA_TIPO", "descricao": "Fora de padrão — requer renegociação", "umidade_max_pct": 18.0, "impureza_max_pct": 5.0, "avariados_max_pct": 15.0},
        ],
    },
    {
        "nome": "Milho",
        "codigo": "MILHO",
        "descricao": "Milho grão (Zea mays) — segunda commodity mais negociada",
        "tipo": TipoCommodity.AGRICOLA.value,
        "unidade_padrao": UnidadeCommodity.SACA_60KG.value,
        "peso_unidade": 60.0,
        "umidade_padrao_pct": 14.0,
        "impureza_padrao_pct": 1.0,
        "possui_cotacao": True,
        "bolsa_referencia": "CBOT",
        "codigo_bolsa": "ZC",
        "classificacoes": [
            {"classe": "TIPO_1", "descricao": "Milho tipo 1", "umidade_max_pct": 14.0, "impureza_max_pct": 1.0, "avariados_max_pct": 4.0},
            {"classe": "TIPO_2", "descricao": "Milho tipo 2", "umidade_max_pct": 15.5, "impureza_max_pct": 2.0, "avariados_max_pct": 8.0},
            {"classe": "FORA_TIPO", "descricao": "Fora de padrão", "umidade_max_pct": 18.0, "impureza_max_pct": 5.0, "avariados_max_pct": 15.0},
        ],
    },
    {
        "nome": "Café Arábica",
        "codigo": "CAFE_ARABICA",
        "descricao": "Café arábica (Coffea arabica) — bebida de maior valor agregado",
        "tipo": TipoCommodity.AGRICOLA.value,
        "unidade_padrao": UnidadeCommodity.SACA_60KG.value,
        "peso_unidade": 60.0,
        "umidade_padrao_pct": 12.0,
        "impureza_padrao_pct": 1.0,
        "possui_cotacao": True,
        "bolsa_referencia": "ICE",
        "codigo_bolsa": "KC",
        "classificacoes": [
            {"classe": "ESPECIAL", "descricao": "Café especial — pontuação SCAA > 84", "umidade_max_pct": 12.0, "impureza_max_pct": 0.5, "avariados_max_pct": 1.0, "ardidos_max_pct": 0.5},
            {"classe": "TIPO_1", "descricao": "Tipo 1 — fino, até 6 defeitos", "umidade_max_pct": 12.5, "impureza_max_pct": 1.0, "avariados_max_pct": 2.5, "ardidos_max_pct": 1.0},
            {"classe": "TIPO_2", "descricao": "Tipo 2 — bom, 7-20 defeitos", "umidade_max_pct": 13.0, "impureza_max_pct": 1.5, "avariados_max_pct": 5.0, "ardidos_max_pct": 2.0},
            {"classe": "FORA_TIPO", "descricao": "Fora de padrão", "umidade_max_pct": 15.0, "impureza_max_pct": 3.0, "avariados_max_pct": 10.0, "ardidos_max_pct": 5.0},
        ],
    },
    {
        "nome": "Café Conilon",
        "codigo": "CAFE_CONILON",
        "descricao": "Café conilon/robusta (Coffea canephora) — commodity separada do Arábica",
        "tipo": TipoCommodity.AGRICOLA.value,
        "unidade_padrao": UnidadeCommodity.SACA_60KG.value,
        "peso_unidade": 60.0,
        "umidade_padrao_pct": 12.0,
        "impureza_padrao_pct": 1.0,
        "possui_cotacao": True,
        "bolsa_referencia": "ICE",
        "codigo_bolsa": "RC",
        "classificacoes": [
            {"classe": "PREMIUM", "descricao": "Conilon premium", "umidade_max_pct": 12.0, "impureza_max_pct": 0.5, "avariados_max_pct": 1.0},
            {"classe": "TIPO_1", "descricao": "Conilon tipo 1", "umidade_max_pct": 12.5, "impureza_max_pct": 1.0, "avariados_max_pct": 3.0},
            {"classe": "TIPO_2", "descricao": "Conilon tipo 2", "umidade_max_pct": 13.5, "impureza_max_pct": 2.0, "avariados_max_pct": 6.0},
            {"classe": "FORA_TIPO", "descricao": "Fora de padrão", "umidade_max_pct": 15.0, "impureza_max_pct": 3.0, "avariados_max_pct": 12.0},
        ],
    },
    {
        "nome": "Trigo",
        "codigo": "TRIGO",
        "descricao": "Trigo (Triticum aestivum)",
        "tipo": TipoCommodity.AGRICOLA.value,
        "unidade_padrao": UnidadeCommodity.SACA_60KG.value,
        "peso_unidade": 60.0,
        "umidade_padrao_pct": 13.0,
        "impureza_padrao_pct": 1.0,
        "possui_cotacao": True,
        "bolsa_referencia": "CBOT",
        "codigo_bolsa": "ZW",
        "classificacoes": [
            {"classe": "TIPO_1", "descricao": "Trigo tipo 1", "umidade_max_pct": 13.0, "impureza_max_pct": 1.0, "avariados_max_pct": 3.0},
            {"classe": "TIPO_2", "descricao": "Trigo tipo 2", "umidade_max_pct": 14.0, "impureza_max_pct": 2.0, "avariados_max_pct": 6.0},
            {"classe": "FORA_TIPO", "descricao": "Fora de padrão", "umidade_max_pct": 16.0, "impureza_max_pct": 4.0, "avariados_max_pct": 12.0},
        ],
    },
    {
        "nome": "Algodão",
        "codigo": "ALGODAO",
        "descricao": "Algodão em pluma (Gossypium hirsutum)",
        "tipo": TipoCommodity.AGRICOLA.value,
        "unidade_padrao": UnidadeCommodity.SACA_60KG.value,
        "peso_unidade": 60.0,
        "umidade_padrao_pct": 8.0,
        "impureza_padrao_pct": 3.0,
        "possui_cotacao": True,
        "bolsa_referencia": "ICE",
        "codigo_bolsa": "CT",
        "classificacoes": [
            {"classe": "TIPO_1", "descricao": "Algodão tipo 1", "umidade_max_pct": 8.0, "impureza_max_pct": 3.0, "quebrados_max_pct": 2.0},
            {"classe": "TIPO_2", "descricao": "Algodão tipo 2", "umidade_max_pct": 10.0, "impureza_max_pct": 5.0, "quebrados_max_pct": 5.0},
            {"classe": "FORA_TIPO", "descricao": "Fora de padrão", "umidade_max_pct": 12.0, "impureza_max_pct": 8.0, "quebrados_max_pct": 10.0},
        ],
    },
    {
        "nome": "Arroz",
        "codigo": "ARROZ",
        "descricao": "Arroz em casca (Oryza sativa)",
        "tipo": TipoCommodity.AGRICOLA.value,
        "unidade_padrao": UnidadeCommodity.SACA_60KG.value,
        "peso_unidade": 50.0,
        "umidade_padrao_pct": 13.0,
        "impureza_padrao_pct": 1.0,
        "possui_cotacao": True,
        "bolsa_referencia": "CBOT",
        "codigo_bolsa": "ZR",
        "classificacoes": [
            {"classe": "TIPO_1", "descricao": "Arroz tipo 1 — inteiro longo", "umidade_max_pct": 13.0, "impureza_max_pct": 1.0, "quebrados_max_pct": 5.0},
            {"classe": "TIPO_2", "descricao": "Arroz tipo 2", "umidade_max_pct": 14.0, "impureza_max_pct": 2.0, "quebrados_max_pct": 15.0},
            {"classe": "FORA_TIPO", "descricao": "Fora de padrão", "umidade_max_pct": 16.0, "impureza_max_pct": 4.0, "quebrados_max_pct": 30.0},
        ],
    },
    # -----------------------------------------------------------------------
    # PECUÁRIAS
    # -----------------------------------------------------------------------
    {
        "nome": "Boi Gordo",
        "codigo": "BOI_GORDO",
        "descricao": "Boi gordo — animal terminado para abate",
        "tipo": TipoCommodity.PECUARIA.value,
        "unidade_padrao": UnidadeCommodity.ARROBA.value,
        "peso_unidade": 15.0,
        "possui_cotacao": True,
        "bolsa_referencia": "B3",
        "codigo_bolsa": "BGI",
        "classificacoes": [
            {"classe": "PREMIUM", "descricao": "Premium — acabamento excelente", "descricao_extra": "Gordura de cobertura uniforme"},
            {"classe": "TIPO_1", "descricao": "Tipo 1 — bom acabamento"},
            {"classe": "TIPO_2", "descricao": "Tipo 2 — acabamento regular"},
            {"classe": "FORA_TIPO", "descricao": "Fora de padrão — magro ou excessivamente gordo"},
        ],
    },
    {
        "nome": "Leite",
        "codigo": "LEITE",
        "descricao": "Leite bovino in natura",
        "tipo": TipoCommodity.PECUARIA.value,
        "unidade_padrao": UnidadeCommodity.LITRO.value,
        "peso_unidade": None,
        "possui_cotacao": True,
        "bolsa_referencia": "CEPEA",
        "codigo_bolsa": None,
        "classificacoes": [
            {"classe": "TIPO_A", "descricao": "Tipo A — pasteurizado, CCS < 100mil, CBT < 10mil", "umidade_max_pct": None},
            {"classe": "TIPO_B", "descricao": "Tipo B — CCS < 400mil, CBT < 500mil"},
            {"classe": "TIPO_C", "descricao": "Tipo C — padrão mínimo MAPA"},
            {"classe": "FORA_TIPO", "descricao": "Fora de padrão — reprovado na análise"},
        ],
    },
    {
        "nome": "Bezerro",
        "codigo": "BEZERRO",
        "descricao": "Bezerro — animal jovem para recria/engorda",
        "tipo": TipoCommodity.PECUARIA.value,
        "unidade_padrao": UnidadeCommodity.CABECA.value,
        "peso_unidade": None,  # peso varia por animal — controlado no lote
        "possui_cotacao": False,
        "bolsa_referencia": None,
        "codigo_bolsa": None,
        "classificacoes": [
            {"classe": "PREMIUM", "descricao": "Premium — raça definida, bom peso de desmama"},
            {"classe": "TIPO_1", "descricao": "Tipo 1 — desmama padrão"},
            {"classe": "TIPO_2", "descricao": "Tipo 2 — peso abaixo da média"},
        ],
    },
    # -----------------------------------------------------------------------
    # FLORESTAIS
    # -----------------------------------------------------------------------
    {
        "nome": "Eucalipto",
        "codigo": "EUCALIPTO",
        "descricao": "Madeira de eucalipto para celulose/papel",
        "tipo": TipoCommodity.FLORESTAL.value,
        "unidade_padrao": UnidadeCommodity.M3.value,
        "peso_unidade": None,  # volume — peso varia por densidade
        "umidade_padrao_pct": None,
        "impureza_padrao_pct": None,
        "possui_cotacao": True,
        "bolsa_referencia": "Cepea",
        "codigo_bolsa": None,
        "classificacoes": [
            {"classe": "TIPO_1", "descricao": "Tipo 1 — casca < 5%, diâmetro > 15cm"},
            {"classe": "TIPO_2", "descricao": "Tipo 2 — casca < 10%, diâmetro > 10cm"},
            {"classe": "FORA_TIPO", "descricao": "Fora de padrão"},
        ],
    },
]


async def run_seed():
    import asyncpg

    url = str(settings.database_url).replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(url)

    created_count = 0
    skipped_count = 0
    classificacoes_count = 0

    for item in COMMODITIES_SEED:
        codigo = item["codigo"]

        # Verificar se já existe
        exists = await conn.fetchval(
            "SELECT id FROM cadastros_commodities WHERE codigo = $1", codigo
        )
        if exists:
            print(f"  ⏭️  {item['nome']} ({codigo}) — já existe, pulando")
            skipped_count += 1
            continue

        # Inserir commodity
        commodity_id = await conn.fetchval("""
            INSERT INTO cadastros_commodities (
                id, tenant_id, sistema, nome, codigo, descricao,
                tipo, unidade_padrao, peso_unidade,
                umidade_padrao_pct, impureza_padrao_pct,
                possui_cotacao, bolsa_referencia, codigo_bolsa,
                ativo, created_at, updated_at
            ) VALUES (
                gen_random_uuid(), NULL, true,
                $1, $2, $3,
                $4, $5, $6,
                $7, $8,
                $9, $10, $11,
                true, NOW(), NOW()
            ) RETURNING id
        """,
            item["nome"],
            item["codigo"],
            item["descricao"],
            item["tipo"],
            item["unidade_padrao"],
            item.get("peso_unidade"),
            item.get("umidade_padrao_pct"),
            item.get("impureza_padrao_pct"),
            item["possui_cotacao"],
            item.get("bolsa_referencia"),
            item.get("codigo_bolsa"),
        )

        created_count += 1
        print(f"  ✅ {item['nome']} ({codigo}) — criada")

        # Inserir classificações
        for cls in item.get("classificacoes", []):
            await conn.execute("""
                INSERT INTO cadastros_commodities_classificacoes (
                    id, commodity_id, classe, descricao,
                    umidade_max_pct, impureza_max_pct, avariados_max_pct,
                    ardidos_max_pct, esverdeados_max_pct, quebrados_max_pct,
                    parametros_extras, ativo
                ) VALUES (
                    gen_random_uuid(), $1, $2, $3,
                    $4, $5, $6,
                    $7, $8, $9,
                    $10, true
                )
            """,
                commodity_id,
                cls["classe"],
                cls.get("descricao"),
                cls.get("umidade_max_pct"),
                cls.get("impureza_max_pct"),
                cls.get("avariados_max_pct"),
                cls.get("ardidos_max_pct"),
                cls.get("esverdeados_max_pct"),
                cls.get("quebrados_max_pct"),
                cls.get("descricao_extra"),
            )
            classificacoes_count += 1

    await conn.close()

    print()
    print("=" * 60)
    print(f"  Criadas:     {created_count}")
    print(f"  Puladas:     {skipped_count}")
    print(f"  Classificações: {classificacoes_count}")
    print("=" * 60)

    if created_count == 0:
        print("  Nenhuma commodity nova criada (todas já existiam).")
    else:
        print("  ✅ Seed concluído com sucesso!")


if __name__ == "__main__":
    print("=" * 60)
    print("  Seed — Commodities Padrão do Sistema")
    print("=" * 60)
    print()
    asyncio.run(run_seed())
