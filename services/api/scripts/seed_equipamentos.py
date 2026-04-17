"""
Seed de Equipamentos & Frota - AgroSaaS

Cria dados realistas de equipamentos para teste e desenvolvimento:
- Tratores
- Colhedoras
- Veículos
- Implementos
- Pulverizadores

Pré-requisitos:
    - O seed_dev.py já deve ter sido executado (precisa de tenant e fazenda)

Uso:
    cd services/api
    source .venv/bin/activate
    python scripts/seed_equipamentos.py
"""

import sys
import os
# Adicionar o diretório raiz da API no PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import text

from core.database import async_session_maker


# Dados de exemplo realistas para uma fazenda
EQUIPAMENTOS = [
    # ── TRATORES ──────────────────────────────────────────────────────────────
    {
        "tipo": "TRATOR",
        "nome": "John Deere 8R 310",
        "marca": "John Deere",
        "modelo": "8R 310",
        "ano_fabricacao": 2023,
        "ano_modelo": 2024,
        "patrimonio": "TR-001",
        "combustivel": "DIESEL",
        "potencia_cv": 310.0,
        "capacidade_tanque_l": 1135.0,
        "horimetro_atual": 1250.5,
        "valor_aquisicao": 1850000.0,
        "dados_extras": {"tracao": "4x4", "rpm_pto": 540, "transmissao": "CVT"},
        "status": "ATIVO",
        "observacoes": "Trator principal para preparo de solo",
    },
    {
        "tipo": "TRATOR",
        "nome": "Case IH Magnum 340",
        "marca": "Case IH",
        "modelo": "Magnum 340",
        "ano_fabricacao": 2022,
        "ano_modelo": 2022,
        "patrimonio": "TR-002",
        "combustivel": "DIESEL",
        "potencia_cv": 340.0,
        "capacidade_tanque_l": 870.0,
        "horimetro_atual": 2340.0,
        "valor_aquisicao": 1650000.0,
        "dados_extras": {"tracao": "4x4", "rpm_pto": 1000, "transmissao": "PowerShift"},
        "status": "ATIVO",
        "observacoes": None,
    },
    {
        "tipo": "TRATOR",
        "nome": "New Holland T7.270",
        "marca": "New Holland",
        "modelo": "T7.270",
        "ano_fabricacao": 2021,
        "ano_modelo": 2021,
        "patrimonio": "TR-003",
        "combustivel": "DIESEL",
        "potencia_cv": 270.0,
        "capacidade_tanque_l": 605.0,
        "horimetro_atual": 3890.2,
        "valor_aquisicao": 1200000.0,
        "dados_extras": {"tracao": "4x4", "transmissao": "AutoCommand"},
        "status": "EM_MANUTENCAO",
        "observacoes": "Revisão de 4000h agendada",
    },
    {
        "tipo": "TRATOR",
        "nome": "Massey Ferguson 8S.305",
        "marca": "Massey Ferguson",
        "modelo": "8S.305",
        "ano_fabricacao": 2024,
        "ano_modelo": 2024,
        "patrimonio": "TR-004",
        "combustivel": "DIESEL",
        "potencia_cv": 305.0,
        "capacidade_tanque_l": 850.0,
        "horimetro_atual": 180.0,
        "valor_aquisicao": 1750000.0,
        "dados_extras": {"tracao": "4x4", "transmissao": "Dyna-VT"},
        "status": "ATIVO",
        "observacoes": "Aquisição recente - em rodagem",
    },

    # ── COLHEDORAS ────────────────────────────────────────────────────────────
    {
        "tipo": "COLHEDORA",
        "nome": "John Deere S790",
        "marca": "John Deere",
        "modelo": "S790",
        "ano_fabricacao": 2023,
        "ano_modelo": 2023,
        "patrimonio": "CL-001",
        "combustivel": "DIESEL",
        "potencia_cv": 610.0,
        "capacidade_tanque_l": 14100.0,
        "horimetro_atual": 890.0,
        "valor_aquisicao": 4500000.0,
        "dados_extras": {"plataforma_pe": 30, "velocidade_trilha": 1050, "plataforma": "Cabeceira 40ft"},
        "status": "ATIVO",
        "observacoes": "Colhedora principal - safra 2024/2025",
    },
    {
        "tipo": "COLHEDORA",
        "nome": "Case IH Axial-Flow 9250",
        "marca": "Case IH",
        "modelo": "Axial-Flow 9250",
        "ano_fabricacao": 2022,
        "ano_modelo": 2022,
        "patrimonio": "CL-002",
        "combustivel": "DIESEL",
        "potencia_cv": 571.0,
        "capacidade_tanque_l": 11300.0,
        "horimetro_atual": 1560.0,
        "valor_aquisicao": 3800000.0,
        "dados_extras": {"plataforma_pe": 25, "plataforma": "Rigide Flex 35ft"},
        "status": "ATIVO",
        "observacoes": None,
    },

    # ── PULVERIZADORES ────────────────────────────────────────────────────────
    {
        "tipo": "PULVERIZADOR",
        "nome": "Jacto Uniport 3500",
        "marca": "Jacto",
        "modelo": "Uniport 3500",
        "ano_fabricacao": 2023,
        "ano_modelo": 2023,
        "patrimonio": "PL-001",
        "combustivel": "DIESEL",
        "potencia_cv": 300.0,
        "capacidade_tanque_l": 3000.0,
        "horimetro_atual": 720.0,
        "valor_aquisicao": 2100000.0,
        "dados_extras": {"capacidade_litros": 3000, "largura_barra_m": 36, "controle_secao": "5 seções"},
        "status": "ATIVO",
        "observacoes": "Pulverizador auto-propelido com controle de taxa variável",
    },
    {
        "tipo": "PULVERIZADOR",
        "nome": "Stara Topper 4000",
        "marca": "Stara",
        "modelo": "Topper 4000",
        "ano_fabricacao": 2021,
        "ano_modelo": 2021,
        "patrimonio": "PL-002",
        "combustivel": "DIESEL",
        "potencia_cv": 275.0,
        "capacidade_tanque_l": 4000.0,
        "horimetro_atual": 2100.0,
        "valor_aquisicao": 1800000.0,
        "dados_extras": {"capacidade_litros": 4000, "largura_barra_m": 32},
        "status": "ATIVO",
        "observacoes": None,
    },

    # ── IMPLEMENTOS ───────────────────────────────────────────────────────────
    {
        "tipo": "IMPLEMENTO",
        "nome": "Grade Aradora Stara 28 Discos",
        "marca": "Stara",
        "modelo": "Galizota 28D",
        "ano_fabricacao": 2020,
        "ano_modelo": 2020,
        "patrimonio": "IMP-001",
        "combustivel": "NAO_APLICAVEL",
        "potencia_cv": None,
        "capacidade_tanque_l": None,
        "horimetro_atual": 0.0,
        "valor_aquisicao": 180000.0,
        "dados_extras": {"num_discos": 28, "largura_trabalho_m": 5.2},
        "status": "ATIVO",
        "observacoes": "Implemento tracionado",
    },
    {
        "tipo": "IMPLEMENTO",
        "nome": "Plantadeira John Deere DB60",
        "marca": "John Deere",
        "modelo": "DB60",
        "ano_fabricacao": 2022,
        "ano_modelo": 2022,
        "patrimonio": "IMP-002",
        "combustivel": "NAO_APLICAVEL",
        "potencia_cv": None,
        "capacidade_tanque_l": None,
        "horimetro_atual": 0.0,
        "valor_aquisicao": 1200000.0,
        "dados_extras": {"num_linhas": 20, "espacamento_m": 0.45, "tipo": "Eletrônica"},
        "status": "ATIVO",
        "observacoes": "Plantadeira de precisão 20 linhas",
    },
    {
        "tipo": "IMPLEMENTO",
        "nome": "Escarificador Stara 5 Braços",
        "marca": "Stara",
        "modelo": "ECM 5",
        "ano_fabricacao": 2019,
        "ano_modelo": 2019,
        "patrimonio": "IMP-003",
        "combustivel": "NAO_APLICAVEL",
        "potencia_cv": None,
        "capacidade_tanque_l": None,
        "horimetro_atual": 0.0,
        "valor_aquisicao": 95000.0,
        "dados_extras": {"num_bracos": 5, "profundidade_max_cm": 45},
        "status": "ATIVO",
        "observacoes": None,
    },

    # ── VEÍCULOS ──────────────────────────────────────────────────────────────
    {
        "tipo": "VEICULO",
        "nome": "Toyota Hilux SW4",
        "marca": "Toyota",
        "modelo": "Hilux SW4 SRX",
        "ano_fabricacao": 2024,
        "ano_modelo": 2024,
        "placa": "QST8A23",
        "patrimonio": "VH-001",
        "combustivel": "DIESEL",
        "potencia_cv": 200.0,
        "capacidade_tanque_l": 80.0,
        "km_atual": 12500.0,
        "valor_aquisicao": 320000.0,
        "status": "ATIVO",
        "observacoes": "Veículo gerência",
    },
    {
        "tipo": "VEICULO",
        "nome": "Ford F-250 XLT",
        "marca": "Ford",
        "modelo": "F-250 XLT CD",
        "ano_fabricacao": 2023,
        "ano_modelo": 2024,
        "placa": "QST9B45",
        "patrimonio": "VH-002",
        "combustivel": "DIESEL",
        "potencia_cv": 230.0,
        "capacidade_tanque_l": 116.0,
        "km_atual": 35000.0,
        "valor_aquisicao": 290000.0,
        "status": "ATIVO",
        "observacoes": "Caminhonete apoio operacional",
    },
    {
        "tipo": "VEICULO",
        "nome": "Mercedes-Benz Atego 1719",
        "marca": "Mercedes-Benz",
        "modelo": "Atego 1719",
        "ano_fabricacao": 2021,
        "ano_modelo": 2021,
        "placa": "QST7C89",
        "patrimonio": "VH-003",
        "combustivel": "DIESEL",
        "potencia_cv": 210.0,
        "capacidade_tanque_l": 275.0,
        "km_atual": 89000.0,
        "valor_aquisicao": 450000.0,
        "dados_extras": {"capacidade_carga_kg": 10000, "carroceria": "Graneleiro"},
        "status": "ATIVO",
        "observacoes": "Caminhão graneleiro",
    },
    {
        "tipo": "VEICULO",
        "nome": "VW Constellation 19.320",
        "marca": "Volkswagen",
        "modelo": "Constellation 19.320",
        "ano_fabricacao": 2020,
        "ano_modelo": 2020,
        "placa": "QST6D12",
        "patrimonio": "VH-004",
        "combustivel": "DIESEL",
        "potencia_cv": 320.0,
        "capacidade_tanque_l": 400.0,
        "km_atual": 145000.0,
        "valor_aquisicao": 520000.0,
        "dados_extras": {"capacidade_carga_kg": 15000, "eixos": 3, "carroceria": "Bitrem"},
        "status": "EM_MANUTENCAO",
        "observacoes": "Troca de embreagem em andamento",
    },
    {
        "tipo": "VEICULO",
        "nome": "Fiat Toro Volcano",
        "marca": "Fiat",
        "modelo": "Toro Volcano",
        "ano_fabricacao": 2023,
        "ano_modelo": 2023,
        "placa": "QST5E67",
        "patrimonio": "VH-005",
        "combustivel": "FLEX",
        "potencia_cv": 185.0,
        "capacidade_tanque_l": 50.0,
        "km_atual": 22000.0,
        "valor_aquisicao": 165000.0,
        "status": "ATIVO",
        "observacoes": "Veículo administrativo",
    },

    # ── IRRIGAÇÃO ─────────────────────────────────────────────────────────────
    {
        "tipo": "IRRIGACAO",
        "nome": "Pivô Central S1000",
        "marca": "Valmont (Irriga Brasil)",
        "modelo": "S1000",
        "ano_fabricacao": 2021,
        "ano_modelo": 2021,
        "patrimonio": "IR-001",
        "combustivel": "ELETRICO",
        "potencia_cv": 60.0,
        "valor_aquisicao": 850000.0,
        "dados_extras": {"area_irrigada_ha": 120, "vazao_m3h": 350, "torres": 8, "diametro_tubo_mm": 219},
        "status": "ATIVO",
        "observacoes": "Pivô central - Talhão 12",
    },
    {
        "tipo": "IRRIGACAO",
        "nome": "Bomba Submersa KSB",
        "marca": "KSB",
        "modelo": "Amarex KRT 150",
        "ano_fabricacao": 2020,
        "ano_modelo": 2020,
        "patrimonio": "IR-002",
        "combustivel": "ELETRICO",
        "potencia_cv": 100.0,
        "valor_aquisicao": 85000.0,
        "dados_extras": {"vazao_m3h": 200, "profundidade_m": 60},
        "status": "ATIVO",
        "observacoes": "Poço artesiano - Área de irrigação",
    },
]


async def seed() -> None:
    """Popula banco com equipamentos de desenvolvimento."""

    print("=" * 60)
    print("🚜 SEED DE EQUIPAMENTOS & FROTA")
    print("=" * 60)

    async with async_session_maker() as session:
        try:
            # ── Pré-requisito: buscar tenant e fazenda ─────────────────────
            print("\n🔍 Busando tenant existente...")
            result = await session.execute(
                text("SELECT id FROM tenants ORDER BY created_at ASC LIMIT 1")
            )
            tenant_row = result.fetchone()
            if not tenant_row:
                print("  ❌ Nenhum tenant encontrado! Execute seed_dev.py primeiro.")
                return
            tenant_id = tenant_row[0]
            print(f"  ✅ Tenant: {tenant_id}")

            print("\n🔍 Busando unidade produtiva (fazenda)...")
            result = await session.execute(
                text("SELECT id FROM unidades_produtivas WHERE tenant_id = :tid ORDER BY created_at ASC LIMIT 1"),
                {"tid": tenant_id}
            )
            fazenda_row = result.fetchone()
            if not fazenda_row:
                print("  ❌ Nenhuma unidade produtiva encontrada! Execute seed_dev.py primeiro.")
                return
            fazenda_id = fazenda_row[0]
            print(f"  ✅ Fazenda: {fazenda_id}")

            # ── Contagem antes ─────────────────────────────────────────────
            result = await session.execute(
                text("SELECT COUNT(*) FROM cadastros_equipamentos WHERE tenant_id = :tid"),
                {"tid": tenant_id}
            )
            count_antes = result.scalar()

            # ── Inserir equipamentos via SQL puro ──────────────────────────
            print(f"\n📦 Inserindo {len(EQUIPAMENTOS)} equipamentos...")

            inseridos = 0
            atualizados = 0

            for eq in EQUIPAMENTOS:
                # Verificar se já existe pelo patrimônio
                result = await session.execute(
                    text(
                        "SELECT id FROM cadastros_equipamentos "
                        "WHERE tenant_id = :tid AND patrimonio = :pat"
                    ),
                    {"tid": tenant_id, "pat": eq["patrimonio"]}
                )
                existente = result.fetchone()

                if existente:
                    print(f"  ⚠️  '{eq['nome']}' (pat: {eq['patrimonio']}) já existe")
                    atualizados += 1
                    continue

                # Gerar UUID único
                eq_id = uuid.uuid4()
                now = datetime.now(timezone.utc)
                dados_extras_json = None
                if eq.get("dados_extras"):
                    import json
                    dados_extras_json = json.dumps(eq["dados_extras"])

                # Inserir via SQL
                await session.execute(
                    text("""
                        INSERT INTO cadastros_equipamentos (
                            id, tenant_id, unidade_produtiva_id,
                            tipo, nome, marca, modelo,
                            ano_fabricacao, ano_modelo,
                            placa, chassi, numero_serie, patrimonio,
                            combustivel, potencia_cv, capacidade_tanque_l,
                            horimetro_atual, km_atual,
                            valor_aquisicao, data_aquisicao,
                            dados_extras, status, observacoes, ativo,
                            created_at, updated_at
                        ) VALUES (
                            :id, :tenant_id, :fazenda_id,
                            :tipo, :nome, :marca, :modelo,
                            :ano_fabricacao, :ano_modelo,
                            :placa, NULL, NULL, :patrimonio,
                            :combustivel, :potencia_cv, :capacidade_tanque_l,
                            :horimetro_atual, :km_atual,
                            :valor_aquisicao, NULL,
                            :dados_extras, :status, :observacoes, true,
                            :now, :now
                        )
                    """),
                    {
                        "id": str(eq_id),
                        "tenant_id": str(tenant_id),
                        "fazenda_id": str(fazenda_id),
                        "tipo": eq["tipo"],
                        "nome": eq["nome"],
                        "marca": eq["marca"],
                        "modelo": eq["modelo"],
                        "ano_fabricacao": eq.get("ano_fabricacao"),
                        "ano_modelo": eq.get("ano_modelo"),
                        "placa": eq.get("placa"),
                        "patrimonio": eq["patrimonio"],
                        "combustivel": eq["combustivel"],
                        "potencia_cv": eq.get("potencia_cv"),
                        "capacidade_tanque_l": eq.get("capacidade_tanque_l"),
                        "horimetro_atual": eq.get("horimetro_atual", 0.0),
                        "km_atual": eq.get("km_atual", 0.0),
                        "valor_aquisicao": eq.get("valor_aquisicao"),
                        "dados_extras": dados_extras_json,
                        "status": eq["status"],
                        "observacoes": eq.get("observacoes"),
                        "now": now,
                    }
                )
                inseridos += 1
                print(f"  ✅ '{eq['nome']}' inserido (tipo: {eq['tipo']})")

            await session.commit()

            # ── Contagem depois ────────────────────────────────────────────
            result = await session.execute(
                text("SELECT COUNT(*) FROM cadastros_equipamentos WHERE tenant_id = :tid"),
                {"tid": tenant_id}
            )
            count_depois = result.scalar()

            # ── Resumo por tipo ───────────────────────────────────────────
            result = await session.execute(
                text(
                    "SELECT tipo, COUNT(*) as qtd "
                    "FROM cadastros_equipamentos WHERE tenant_id = :tid "
                    "GROUP BY tipo ORDER BY tipo"
                ),
                {"tid": tenant_id}
            )
            resumo = result.fetchall()

            # ── Resumo por status ──────────────────────────────────────────
            result = await session.execute(
                text(
                    "SELECT status, COUNT(*) as qtd "
                    "FROM cadastros_equipamentos WHERE tenant_id = :tid "
                    "GROUP BY status ORDER BY status"
                ),
                {"tid": tenant_id}
            )
            status_resumo = result.fetchall()

            # ── Valor total ───────────────────────────────────────────────
            result = await session.execute(
                text(
                    "SELECT COALESCE(SUM(valor_aquisicao), 0) as total "
                    "FROM cadastros_equipamentos WHERE tenant_id = :tid"
                ),
                {"tid": tenant_id}
            )
            valor_total = result.scalar()

            # ==========================================================================
            # RESUMO
            # ==========================================================================
            print("\n" + "=" * 60)
            print("✅ SEED DE EQUIPAMENTOS CONCLUÍDO!")
            print("=" * 60)
            print(f"\n📊 ESTATÍSTICAS:")
            print(f"  • Novos inseridos: {inseridos}")
            print(f"  • Já existentes: {atualizados}")
            print(f"  • Total no banco: {count_depois}")
            print(f"\n📋 POR TIPO:")
            for row in resumo:
                print(f"  • {row[0]}: {row[1]}")
            print(f"\n📋 POR STATUS:")
            for row in status_resumo:
                print(f"  • {row[0]}: {row[1]}")
            print(f"\n💰 VALOR TOTAL DA FROTA: R$ {valor_total:,.2f}")
            print("=" * 60)

        except Exception as e:
            await session.rollback()
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(seed())
