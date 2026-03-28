"""
Auditoria completa de foreign keys em todo o sistema.

Este script:
1. Lista todos os models do sistema
2. Identifica campos UUID que potencialmente deveriam ter FK
3. Verifica se as FKs existem no banco de dados
4. Gera relatório de FKs faltantes
"""
import asyncio
import sys
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from core.database import engine


# Mapeamento de sufixos de campo para tabelas esperadas
EXPECTED_FK_PATTERNS = {
    '_id': {
        'tenant_id': 'tenants',
        'user_id': 'users',
        'usuario_id': 'tenant_usuarios',
        'pessoa_id': 'cadastros_pessoas',
        'equipamento_id': 'cadastros_equipamentos',
        'produto_id': 'cadastros_produtos',
        'commodity_id': 'cadastros_commodities',
        'propriedade_id': 'cadastros_propriedades',
        'fazenda_id': 'fazendas',
        'talhao_id': 'talhoes',
        'safra_id': 'safras',
        'cultura_id': 'culturas',
        'variedade_id': 'variedades',
        'operacao_id': 'operacoes',
        'fornecedor_id': 'cadastros_pessoas',  # FK lógica
        'cliente_id': 'cadastros_pessoas',     # FK lógica
        'operador_id': 'cadastros_pessoas',    # FK lógica
        'responsavel_id': 'cadastros_pessoas', # FK lógica
        'plano_conta_id': 'financeiro_planos_conta',
        'despesa_id': 'financeiro_despesas',
        'receita_id': 'financeiro_receitas',
        'lote_id': 'pecuaria_lotes',
        'animal_id': 'pecuaria_animais',
        'piquete_id': 'pecuaria_piquetes',
        'categoria_id': 'cadastros_categorias',
        'marca_id': 'cadastros_marcas',
        'modelo_id': 'cadastros_modelos',
        'area_id': 'cadastros_areas_rurais',
    }
}


async def get_all_tables() -> List[str]:
    """Retorna lista de todas as tabelas no banco."""
    async with engine.begin() as conn:
        dialect = conn.dialect.name

        if dialect == 'postgresql':
            result = await conn.execute(text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'farms'
                ORDER BY tablename
            """))
        else:  # sqlite
            result = await conn.execute(text("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                ORDER BY name
            """))

        return [row[0] for row in result.fetchall()]


async def get_table_columns(table_name: str) -> List[Tuple[str, str]]:
    """Retorna colunas de uma tabela (nome, tipo)."""
    async with engine.begin() as conn:
        dialect = conn.dialect.name

        if dialect == 'postgresql':
            result = await conn.execute(text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'farms'
                  AND table_name = :table_name
                ORDER BY ordinal_position
            """), {"table_name": table_name})
        else:  # sqlite
            result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
            # SQLite PRAGMA retorna: cid, name, type, notnull, dflt_value, pk
            rows = result.fetchall()
            return [(row[1], row[2]) for row in rows]

        return [(row[0], row[1]) for row in result.fetchall()]


async def get_table_foreign_keys(table_name: str) -> Dict[str, Tuple[str, str]]:
    """Retorna FKs de uma tabela: {coluna: (tabela_ref, coluna_ref)}."""
    async with engine.begin() as conn:
        dialect = conn.dialect.name

        if dialect == 'postgresql':
            result = await conn.execute(text("""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = 'farms'
                  AND tc.table_name = :table_name
            """), {"table_name": table_name})

            return {
                row[0]: (row[1], row[2])
                for row in result.fetchall()
            }
        else:  # sqlite
            result = await conn.execute(text(f"PRAGMA foreign_key_list({table_name})"))
            # SQLite: id, seq, table, from, to, on_update, on_delete, match
            rows = result.fetchall()
            return {
                row[3]: (row[2], row[4])
                for row in rows
            }


async def audit_foreign_keys():
    """Realiza auditoria completa de FKs."""

    print("=" * 80)
    print("🔍 AUDITORIA COMPLETA DE FOREIGN KEYS")
    print("=" * 80)
    print()

    tables = await get_all_tables()

    # Ignora tabelas do sistema
    tables = [t for t in tables if not t.startswith('alembic_')]

    print(f"📊 Total de tabelas analisadas: {len(tables)}")
    print()

    issues = []
    warnings = []
    total_fks = 0
    total_uuid_columns = 0

    for table_name in tables:
        columns = await get_table_columns(table_name)
        fks = await get_table_foreign_keys(table_name)

        total_fks += len(fks)

        # Identifica colunas UUID
        uuid_columns = [
            col_name for col_name, col_type in columns
            if 'uuid' in col_type.lower() and col_name != 'id'
        ]

        total_uuid_columns += len(uuid_columns)

        for col_name in uuid_columns:
            has_fk = col_name in fks

            # Verifica se deveria ter FK baseado em padrões comuns
            expected_table = None
            for pattern, table_map in EXPECTED_FK_PATTERNS.items():
                if col_name in table_map:
                    expected_table = table_map[col_name]
                    break

            if not has_fk:
                # Verifica se é um campo que provavelmente deveria ter FK
                if col_name.endswith('_id'):
                    # Verifica se tem comentário indicando "FK lógica"
                    if expected_table:
                        issues.append({
                            'table': table_name,
                            'column': col_name,
                            'expected_ref': expected_table,
                            'severity': 'ERROR' if 'tenant_id' in col_name or 'user_id' in col_name else 'WARNING'
                        })
                    else:
                        warnings.append({
                            'table': table_name,
                            'column': col_name,
                            'note': 'Campo UUID terminado em _id sem FK (pode ser proposital)'
                        })
            else:
                # Tem FK - verifica se aponta para tabela esperada
                actual_table, actual_col = fks[col_name]
                if expected_table and actual_table != expected_table:
                    warnings.append({
                        'table': table_name,
                        'column': col_name,
                        'note': f'FK aponta para {actual_table} mas esperado {expected_table}'
                    })

    # Relatório
    print()
    print("📈 ESTATÍSTICAS")
    print("-" * 80)
    print(f"Total de colunas UUID (exceto PK): {total_uuid_columns}")
    print(f"Total de Foreign Keys encontradas: {total_fks}")
    print(f"Issues críticos: {len([i for i in issues if i['severity'] == 'ERROR'])}")
    print(f"Avisos: {len([i for i in issues if i['severity'] == 'WARNING']) + len(warnings)}")
    print()

    if issues:
        print()
        print("❌ FOREIGN KEYS FALTANTES")
        print("-" * 80)

        errors = [i for i in issues if i['severity'] == 'ERROR']
        warns = [i for i in issues if i['severity'] == 'WARNING']

        if errors:
            print("\n🚨 CRÍTICO (tenant_id, user_id, etc):")
            for issue in errors:
                print(f"  • {issue['table']}.{issue['column']}")
                print(f"    → Deveria referenciar: {issue['expected_ref']}")

        if warns:
            print("\n⚠️  AVISOS (outros campos _id):")
            for issue in warns:
                print(f"  • {issue['table']}.{issue['column']}")
                print(f"    → Deveria referenciar: {issue['expected_ref']}")

    if warnings:
        print()
        print("⚠️  OBSERVAÇÕES")
        print("-" * 80)
        for warn in warnings[:20]:  # Limita para não poluir
            print(f"  • {warn['table']}.{warn['column']}")
            print(f"    {warn['note']}")

    print()
    print("=" * 80)
    print("✅ Auditoria concluída!")
    print("=" * 80)

    return len(issues), len(warnings)


async def main():
    try:
        issues_count, warnings_count = await audit_foreign_keys()

        if issues_count > 0:
            print()
            print("⚠️  Foram encontradas foreign keys faltantes!")
            print("   Revise o relatório acima e crie migrations para corrigir.")
            sys.exit(1)
        else:
            print()
            print("✅ Nenhuma foreign key crítica faltando!")
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ Erro durante auditoria: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
