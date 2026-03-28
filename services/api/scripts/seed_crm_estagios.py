#!/usr/bin/env python3
"""
Seed para criar estágios padrão do CRM.

Cria um pipeline comercial padrão com as seguintes colunas:
1. Prospecção
2. Qualificação
3. Proposta
4. Negociação
5. Fechamento
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime, timezone

# Importar models
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models.crm import PipelineEstagio
from core.config import settings

# Dados dos estágios padrão
ESTAGIOS_PADRAO = [
    {
        "nome": "Prospecção",
        "cor": "#3b82f6",  # Blue
        "ordem": 1,
    },
    {
        "nome": "Qualificação",
        "cor": "#8b5cf6",  # Purple
        "ordem": 2,
    },
    {
        "nome": "Proposta",
        "cor": "#f59e0b",  # Amber
        "ordem": 3,
    },
    {
        "nome": "Negociação",
        "cor": "#ec4899",  # Pink
        "ordem": 4,
    },
    {
        "nome": "Fechamento",
        "cor": "#10b981",  # Green
        "ordem": 5,
    },
]


async def seed():
    """Cria estágios padrão do CRM."""
    db_url = str(settings.database_url)
    if not db_url or "postgresql" not in db_url:
        db_url = "sqlite+aiosqlite:///./agrosaas.db"

    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("🌱 Seedando estágios do CRM...")

        for dados in ESTAGIOS_PADRAO:
            estagio = PipelineEstagio(
                nome=dados["nome"],
                cor=dados["cor"],
                ordem=dados["ordem"],
                ativo=True,
            )
            session.add(estagio)
            print(f"  ✓ Criado: {dados['nome']}")

        await session.commit()
        print("\n✅ Seed concluído com sucesso!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
