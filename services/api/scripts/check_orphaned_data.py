"""
Verifica se há dados órfãos que impediriam a criação das foreign keys.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from core.database import engine


async def check_orphaned_data():
    """Verifica dados órfãos para cada FK que será adicionada."""

    checks = [
        {
            'name': 'frota_abastecimentos.fornecedor_id',
            'query': """
                SELECT COUNT(*) as count
                FROM farms.frota_abastecimentos fa
                WHERE fa.fornecedor_id IS NOT NULL
                  AND NOT EXISTS (
                    SELECT 1 FROM farms.cadastros_pessoas cp
                    WHERE cp.id = fa.fornecedor_id
                  )
            """
        },
        {
            'name': 'frota_apontamentos_uso.talhao_id',
            'query': """
                SELECT COUNT(*) as count
                FROM farms.frota_apontamentos_uso fau
                WHERE fau.talhao_id IS NOT NULL
                  AND NOT EXISTS (
                    SELECT 1 FROM farms.talhoes t
                    WHERE t.id = fau.talhao_id
                  )
            """
        },
        {
            'name': 'frota_apontamentos_uso.operacao_id',
            'query': """
                SELECT COUNT(*) as count
                FROM farms.frota_apontamentos_uso fau
                WHERE fau.operacao_id IS NOT NULL
                  AND NOT EXISTS (
                    SELECT 1 FROM farms.operacoes o
                    WHERE o.id = fau.operacao_id
                  )
            """
        },
        {
            'name': 'operacoes_agricolas.operador_id',
            'query': """
                SELECT COUNT(*) as count
                FROM farms.operacoes_agricolas oa
                WHERE oa.operador_id IS NOT NULL
                  AND NOT EXISTS (
                    SELECT 1 FROM farms.cadastros_pessoas cp
                    WHERE cp.id = oa.operador_id
                  )
            """
        },
        {
            'name': 'rh_empreitadas.safra_id',
            'query': """
                SELECT COUNT(*) as count
                FROM farms.rh_empreitadas re
                WHERE re.safra_id IS NOT NULL
                  AND NOT EXISTS (
                    SELECT 1 FROM farms.safras s
                    WHERE s.id = re.safra_id
                  )
            """
        },
        {
            'name': 'rh_lancamentos_diarias.safra_id',
            'query': """
                SELECT COUNT(*) as count
                FROM farms.rh_lancamentos_diarias rld
                WHERE rld.safra_id IS NOT NULL
                  AND NOT EXISTS (
                    SELECT 1 FROM farms.safras s
                    WHERE s.id = rld.safra_id
                  )
            """
        },
        {
            'name': 'romaneios_colheita.operador_id',
            'query': """
                SELECT COUNT(*) as count
                FROM farms.romaneios_colheita rc
                WHERE rc.operador_id IS NOT NULL
                  AND NOT EXISTS (
                    SELECT 1 FROM farms.cadastros_pessoas cp
                    WHERE cp.id = rc.operador_id
                  )
            """
        },
    ]

    print("=" * 80)
    print("🔍 VERIFICAÇÃO DE DADOS ÓRFÃOS")
    print("=" * 80)
    print()

    has_issues = False

    async with engine.begin() as conn:
        for check in checks:
            try:
                result = await conn.execute(text(check['query']))
                count = result.scalar()

                if count > 0:
                    print(f"❌ {check['name']}")
                    print(f"   {count} registro(s) órfão(s) encontrado(s)")
                    has_issues = True
                else:
                    print(f"✅ {check['name']}")
                    print(f"   Nenhum dado órfão")
            except Exception as e:
                print(f"⚠️  {check['name']}")
                print(f"   Erro ao verificar: {e}")
                # Pode ser que a tabela não exista, continua...

            print()

    print("=" * 80)
    if has_issues:
        print("❌ Dados órfãos encontrados! É necessário corrigir antes de aplicar FKs.")
        return False
    else:
        print("✅ Nenhum dado órfão encontrado! Seguro para aplicar FKs.")
        return True


if __name__ == "__main__":
    result = asyncio.run(check_orphaned_data())
    sys.exit(0 if result else 1)
