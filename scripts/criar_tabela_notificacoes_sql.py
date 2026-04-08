#!/usr/bin/env python3
"""
Script simples para criar tabela de notificacoes via SQL.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

import asyncio
from core.database import async_session_maker
from sqlalchemy import text

async def criar_tabela_sql():
    """Cria tabela de notificacoes via SQL."""
    async with async_session_maker() as session:
        try:
            # Criar tabela via SQL
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS notificacoes (
                    id CHAR(32) PRIMARY KEY,
                    tenant_id CHAR(32) NOT NULL,
                    tipo VARCHAR(60) NOT NULL,
                    titulo VARCHAR(200) NOT NULL,
                    mensagem VARCHAR(1000) NOT NULL,
                    lida BOOLEAN NOT NULL DEFAULT 0,
                    metadata JSON NOT NULL DEFAULT '{}',
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
                )
            """))
            
            # Criar índice
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_notificacoes_tenant_id 
                ON notificacoes(tenant_id)
            """))
            
            await session.commit()
            print("✅ Tabela 'notificacoes' criada com sucesso via SQL!")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            await session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(criar_tabela_sql())
