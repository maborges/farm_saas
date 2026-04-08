#!/usr/bin/env python3
"""
Script para criar tabela de notificacoes manualmente.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

import asyncio
from core.database import async_session_maker, engine
from notificacoes.models import Notificacao

async def criar_tabela():
    """Cria tabela de notificacoes se não existir."""
    try:
        print("Criando tabela 'notificacoes'...")
        
        # Usar engine síncrono para criar tabelas
        from core.database import engine
        from sqlalchemy import inspect
        
        # Verificar se já existe
        inspector = inspect(engine.sync_engine)
        if 'notificacoes' in inspector.get_table_names():
            print("✅ Tabela 'notificacoes' já existe")
            return
        
        # Criar apenas a tabela de notificacoes
        Notificacao.__table__.create(engine.sync_engine)
        
        print("✅ Tabela 'notificacoes' criada com sucesso!")
        
        # Verificar novamente
        inspector = inspect(engine.sync_engine)
        if 'notificacoes' in inspector.get_table_names():
            print("✅ Verificação: tabela existe no banco")
        else:
            print("⚠️  Verificação falhou - tabela pode não ter sido criada")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(criar_tabela())
