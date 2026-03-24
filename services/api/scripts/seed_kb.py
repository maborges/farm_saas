import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.database import Base
from core.models.knowledge_base import ConhecimentoCategoria, ConhecimentoArtigo

DATABASE_URL = "sqlite+aiosqlite:///./agrosaas.db"

async def seed_kb():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 1. Categorias
        cats = [
            ConhecimentoCategoria(nome="Primeiros Passos", icone="Tractor", ordem=1),
            ConhecimentoCategoria(nome="Gestão Agrícola", icone="Sprout", ordem=2),
            ConhecimentoCategoria(nome="Financeiro & Planos", icone="HandCoins", ordem=3),
            ConhecimentoCategoria(nome="Segurança e Acesso", icone="ShieldCheck", ordem=4),
        ]
        session.add_all(cats)
        await session.flush()

        # 2. Artigos Iniciais
        artigos = [
            ConhecimentoArtigo(
                categoria_id=cats[0].id,
                titulo="Como cadastrar seu primeiro Talhão",
                slug="cadastrar-primeiro-talhao",
                conteudo="# Cadastro de Talhões\n\nPara começar a gerir sua fazenda, o primeiro passo é cadastrar seus talhões.\n\n1. Acesse o menu **Agrícola**\n2. Clique em **Talhões**\n3. Selecione **Novo Talhão**\n4. Desenhe no mapa a área da sua propriedade.",
                is_publico=True
            ),
            ConhecimentoArtigo(
                categoria_id=cats[2].id,
                titulo="Formas de Pagamento Aceitas",
                slug="formas-pagamento",
                conteudo="# Pagamentos\n\nAtualmente aceitamos as seguintes formas:\n\n* **PIX**: Liberação instantânea.\n* **Boleto**: Até 48h úteis para compensação.\n* **Cartão de Crédito**: Em breve!",
                is_publico=True
            )
        ]
        session.add_all(artigos)
        
        await session.commit()
        print("✅ Base de Conhecimento semeada com sucesso!")

if __name__ == "__main__":
    asyncio.run(seed_kb())
