#!/usr/bin/env python3
"""Check tipos de operação cadastrados no banco."""
import asyncio
import sys
sys.path.insert(0, "services/api")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

async def main():
    # Tenta conectar - ajuste a URL conforme seu .env
    db_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/agrosaas"
    
    try:
        engine = create_async_engine(db_url, echo=False)
        async with AsyncSession(engine) as session:
            result = await session.execute(text("""
                SELECT id, tipo_operacao, fases_permitidas, descricao 
                FROM agricola_operacao_tipo_fase 
                ORDER BY tipo_operacao
            """))
            rows = result.fetchall()
            
            print(f"\n=== Tipos de Operação Cadastrados ({len(rows)}) ===\n")
            for row in rows:
                print(f"  tipo_operacao: '{row.tipo_operacao}'")
                print(f"  descricao:     {row.descricao}")
                print(f"  fases:         {row.fases_permitidas}")
                print()
            
            if not rows:
                print("⚠️  TABELA VAZIA! O seed não foi executado.")
                print("\nExecute este SQL para popular:")
                print("""
INSERT INTO agricola_operacao_tipo_fase (id, tipo_operacao, fases_permitidas, descricao)
VALUES 
    (gen_random_uuid(), 'PLANTIO', '["PLANTIO", "DESENVOLVIMENTO"]'::jsonb, 'Semeadura e plantio'),
    (gen_random_uuid(), 'ADUBACAO', '["PREPARO_SOLO", "DESENVOLVIMENTO"]'::jsonb, 'Adubação de cobertura'),
    (gen_random_uuid(), 'PULVERIZACAO', '["DESENVOLVIMENTO", "COLHEITA"]'::jsonb, 'Aplicação de defensivos'),
    (gen_random_uuid(), 'COLHEITA', '["COLHEITA"]'::jsonb, 'Colheita manual ou mecanizada'),
    (gen_random_uuid(), 'PREPARO_SOLO', '["PREPARO_SOLO"]'::jsonb, 'Aração, gradagem, subsolagem'),
    (gen_random_uuid(), 'CALAGEM', '["PREPARO_SOLO"]'::jsonb, 'Aplicação de calcário'),
    (gen_random_uuid(), 'IRRIGACAO', '["DESENVOLVIMENTO", "COLHEITA"]'::jsonb, 'Sistema de irrigação'),
    (gen_random_uuid(), 'OUTROS', '["PLANTIO", "DESENVOLVIMENTO", "COLHEITA", "PREPARO_SOLO"]'::jsonb, 'Outras operações');
""")
        
        await engine.dispose()
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        print("\nAjuste a URL do banco no script e tente novamente.")

asyncio.run(main())
