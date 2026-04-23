"""
Seed de dados agronômicos padrão do sistema.

Cria tipos de solo, tipos de irrigação e regras agronômicas base.
"""
import sys
import asyncio
import uuid
from datetime import datetime, timezone

# Adiciona o diretório da API no PYTHONPATH
sys.path.insert(0, '.')

from core.config import settings

TIPOS_SOLO = [
    {
        "nome": "Arenoso",
        "retencao_agua": "BAIXA",
        "lixiviacao": "ALTA",
        "ctc_resumo": "BAIXA",
        "descricao": "Solos com mais de 70% de areia. Baixa capacidade de retenção de água e nutrientes."
    },
    {
        "nome": "Argiloso",
        "retencao_agua": "ALTA",
        "lixiviacao": "BAIXA",
        "ctc_resumo": "ALTA",
        "descricao": "Solos com mais de 35% de argila. Alta retenção de umidade e CTC elevada."
    },
    {
        "nome": "Médio",
        "retencao_agua": "MEDIA",
        "lixiviacao": "MEDIA",
        "ctc_resumo": "MEDIA",
        "descricao": "Equilíbrio entre areia, silte e argila. Boa aptidão agrícola."
    }
]

TIPOS_IRRIGACAO = [
    {"nome": "Sequeiro", "metodo": "NATURAL", "descricao": "Dependente exclusivamente das chuvas."},
    {"nome": "Gotejamento", "metodo": "LOCALIZADO", "descricao": "Aplicação de água diretamente na base da planta."},
    {"nome": "Pivô Central", "metodo": "ASPERSAO", "descricao": "Sistema circular mecanizado para grandes áreas."},
    {"nome": "Aspersão", "metodo": "ASPERSAO", "descricao": "Simulação de chuva via aspersores fixos ou móveis."},
    {"nome": "Sulco", "metodo": "GRAVIDADE", "descricao": "Distribuição de água por canais entre as linhas de plantio."}
]

REGRAS_BASE = [
    {
        "nome": "Necessidade de Calagem (V%)",
        "descricao": "Gera recomendação de calagem quando a saturação por bases está abaixo da meta da cultura.",
        "condicao_json": {
            "campo": "v_pct",
            "operador": "lt",
            "referencia": "v_meta_cultura"
        },
        "acao_json": {
            "tipo": "GERAR_TAREFA",
            "tarefa_tipo": "CALAGEM",
            "mensagem": "Saturação por bases insuficiente para a cultura alvo. Recomenda-se calagem."
        },
        "prioridade": 10
    },
    {
        "nome": "Correção de Fósforo",
        "descricao": "Recomenda adubação fosfatada quando o nível de P está crítico.",
        "condicao_json": {
            "campo": "fosforo_p",
            "operador": "lt",
            "referencia": "p_critico"
        },
        "acao_json": {
            "tipo": "GERAR_TAREFA",
            "tarefa_tipo": "ADUBACAO_FOSFORO",
            "mensagem": "Níveis de fósforo abaixo do ideal para o tipo de solo."
        },
        "prioridade": 8
    }
]

async def run_seed():
    import asyncpg

    url = str(settings.database_url).replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(url)

    print("🌱 Populando Tipos de Solo...")
    for item in TIPOS_SOLO:
        exists = await conn.fetchval("SELECT id FROM cadastros_tipos_solo WHERE nome = $1", item["nome"])
        if not exists:
            await conn.execute("""
                INSERT INTO cadastros_tipos_solo (id, nome, retencao_agua, lixiviacao, ctc_resumo, descricao, ativo)
                VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, true)
            """, item["nome"], item["retencao_agua"], item["lixiviacao"], item["ctc_resumo"], item["descricao"])
            print(f"  ✅ {item['nome']} criado")
        else:
            print(f"  ⏭️  {item['nome']} já existe")

    print("\n🌱 Populando Tipos de Irrigação...")
    for item in TIPOS_IRRIGACAO:
        exists = await conn.fetchval("SELECT id FROM cadastros_tipos_irrigacao WHERE nome = $1", item["nome"])
        if not exists:
            await conn.execute("""
                INSERT INTO cadastros_tipos_irrigacao (id, nome, metodo, descricao, ativo)
                VALUES (gen_random_uuid(), $1, $2, $3, true)
            """, item["nome"], item["metodo"], item["descricao"])
            print(f"  ✅ {item['nome']} criado")
        else:
            print(f"  ⏭️  {item['nome']} já existe")

    print("\n🌱 Populando Regras Agronômicas Base...")
    for item in REGRAS_BASE:
        exists = await conn.fetchval("SELECT id FROM agricola_regras_agronomicas WHERE nome = $1 AND tenant_id IS NULL", item["nome"])
        if not exists:
            import json
            await conn.execute("""
                INSERT INTO agricola_regras_agronomicas (
                    id, tenant_id, nome, descricao, condicao_json, acao_json, prioridade, ativo, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), NULL, $1, $2, $3, $4, $5, true, NOW(), NOW()
                )
            """, item["nome"], item["descricao"], json.dumps(item["condicao_json"]), json.dumps(item["acao_json"]), item["prioridade"])
            print(f"  ✅ {item['nome']} criada")
        else:
            print(f"  ⏭️  {item['nome']} já existe")

    await conn.close()
    print("\n✅ Seed agronômico concluído!")

if __name__ == "__main__":
    asyncio.run(run_seed())
