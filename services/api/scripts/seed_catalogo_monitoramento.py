"""
Seed do catálogo fitossanitário (system entries).
Uso: python scripts/seed_catalogo_monitoramento.py
"""
import asyncio
import uuid
from sqlalchemy import select, text
from core.database import async_session_maker
from core.models import Tenant  # noqa: F401 — needed for FK resolution
from agricola.monitoramento.catalogo_model import MonitoramentoCatalogo

SYSTEM_TENANT_ID = None  # será preenchido com o primeiro tenant existente

ENTRADAS = [
    # PRAGAS — Soja
    dict(tipo="PRAGA", nome_popular="Lagarta-da-soja", nome_cientifico="Anticarsia gemmatalis", cultura="Soja", nde_padrao=20.0, unidade_medida="lagartas/pano"),
    dict(tipo="PRAGA", nome_popular="Lagarta-do-cartucho", nome_cientifico="Spodoptera frugiperda", cultura="Milho", nde_padrao=2.0, unidade_medida="lagartas/planta"),
    dict(tipo="PRAGA", nome_popular="Percevejo-marrom", nome_cientifico="Euschistus heros", cultura="Soja", nde_padrao=2.0, unidade_medida="percevejos/pano"),
    dict(tipo="PRAGA", nome_popular="Percevejo-verde", nome_cientifico="Nezara viridula", cultura="Soja", nde_padrao=2.0, unidade_medida="percevejos/pano"),
    dict(tipo="PRAGA", nome_popular="Mosca-branca", nome_cientifico="Bemisia tabaci", cultura=None, nde_padrao=1.0, unidade_medida="adultos/folha"),
    dict(tipo="PRAGA", nome_popular="Pulgão-do-trigo", nome_cientifico="Schizaphis graminum", cultura="Trigo", nde_padrao=10.0, unidade_medida="pulgões/afilho"),
    dict(tipo="PRAGA", nome_popular="Cigarrinha-das-raízes", nome_cientifico="Deois flavopicta", cultura=None, nde_padrao=3.0, unidade_medida="ninfas/m²"),
    dict(tipo="PRAGA", nome_popular="Spodoptera cosmioides", nome_cientifico="Spodoptera cosmioides", cultura="Soja", nde_padrao=2.0, unidade_medida="lagartas/pano"),
    dict(tipo="PRAGA", nome_popular="Helicoverpa armigera", nome_cientifico="Helicoverpa armigera", cultura=None, nde_padrao=1.0, unidade_medida="lagartas/pano"),
    dict(tipo="PRAGA", nome_popular="Ácaro-rajado", nome_cientifico="Tetranychus urticae", cultura=None, nde_padrao=30.0, unidade_medida="% folhas infestadas"),
    dict(tipo="PRAGA", nome_popular="Broca-da-soja", nome_cientifico="Epinotia aporema", cultura="Soja", nde_padrao=30.0, unidade_medida="% plantas atacadas"),
    dict(tipo="PRAGA", nome_popular="Tamanduá-da-soja", nome_cientifico="Sternechus subsignatus", cultura="Soja", nde_padrao=5.0, unidade_medida="adultos/m"),
    dict(tipo="PRAGA", nome_popular="Elasmo", nome_cientifico="Elasmopalpus lignosellus", cultura="Milho", nde_padrao=10.0, unidade_medida="% plantas atacadas"),

    # DOENÇAS — Soja
    dict(tipo="DOENCA", nome_popular="Ferrugem Asiática", nome_cientifico="Phakopsora pachyrhizi", cultura="Soja", nde_padrao=1.0, unidade_medida="% área foliar afetada"),
    dict(tipo="DOENCA", nome_popular="Mancha-alvo", nome_cientifico="Corynespora cassiicola", cultura="Soja", nde_padrao=5.0, unidade_medida="% área foliar afetada"),
    dict(tipo="DOENCA", nome_popular="Antracnose", nome_cientifico="Colletotrichum truncatum", cultura="Soja", nde_padrao=5.0, unidade_medida="% plantas afetadas"),
    dict(tipo="DOENCA", nome_popular="Mofo-branco", nome_cientifico="Sclerotinia sclerotiorum", cultura=None, nde_padrao=1.0, unidade_medida="% plantas afetadas"),
    dict(tipo="DOENCA", nome_popular="Oídio", nome_cientifico="Erysiphe diffusa", cultura="Soja", nde_padrao=25.0, unidade_medida="% área foliar afetada"),
    dict(tipo="DOENCA", nome_popular="Cercospora", nome_cientifico="Cercospora kikuchii", cultura="Soja", nde_padrao=10.0, unidade_medida="% área foliar afetada"),
    dict(tipo="DOENCA", nome_popular="Podridão-vermelha-da-raiz", nome_cientifico="Fusarium virguliforme", cultura="Soja", nde_padrao=5.0, unidade_medida="% plantas afetadas"),
    dict(tipo="DOENCA", nome_popular="Ferrugem-da-folha do Trigo", nome_cientifico="Puccinia triticina", cultura="Trigo", nde_padrao=5.0, unidade_medida="% área foliar afetada"),
    dict(tipo="DOENCA", nome_popular="Giberela", nome_cientifico="Fusarium graminearum", cultura="Trigo", nde_padrao=2.0, unidade_medida="% espigas afetadas"),
    dict(tipo="DOENCA", nome_popular="Mancha-de-turcicum", nome_cientifico="Exserohilum turcicum", cultura="Milho", nde_padrao=10.0, unidade_medida="% área foliar afetada"),

    # PLANTAS DANINHAS
    dict(tipo="PLANTA_DANINHA", nome_popular="Buva", nome_cientifico="Conyza spp.", cultura=None, nde_padrao=1.0, unidade_medida="plantas/m²"),
    dict(tipo="PLANTA_DANINHA", nome_popular="Capim-amargoso", nome_cientifico="Digitaria insularis", cultura=None, nde_padrao=2.0, unidade_medida="plantas/m²"),
    dict(tipo="PLANTA_DANINHA", nome_popular="Leiteiro", nome_cientifico="Euphorbia heterophylla", cultura="Soja", nde_padrao=2.0, unidade_medida="plantas/m²"),
    dict(tipo="PLANTA_DANINHA", nome_popular="Capim-pé-de-galinha", nome_cientifico="Eleusine indica", cultura=None, nde_padrao=5.0, unidade_medida="plantas/m²"),
    dict(tipo="PLANTA_DANINHA", nome_popular="Picão-preto", nome_cientifico="Bidens pilosa", cultura=None, nde_padrao=4.0, unidade_medida="plantas/m²"),
    dict(tipo="PLANTA_DANINHA", nome_popular="Caruru", nome_cientifico="Amaranthus hybridus", cultura=None, nde_padrao=3.0, unidade_medida="plantas/m²"),
    dict(tipo="PLANTA_DANINHA", nome_popular="Nabiça", nome_cientifico="Raphanus raphanistrum", cultura=None, nde_padrao=2.0, unidade_medida="plantas/m²"),
    dict(tipo="PLANTA_DANINHA", nome_popular="Trapoeraba", nome_cientifico="Commelina benghalensis", cultura=None, nde_padrao=5.0, unidade_medida="plantas/m²"),
]


async def seed():
    async with async_session_maker() as session:
        # Usa o primeiro tenant existente para hospedar as entradas system
        row = (await session.execute(text("SELECT id FROM tenants LIMIT 1"))).fetchone()
        if not row:
            print("Nenhum tenant encontrado. Crie um tenant antes de rodar o seed.")
            return
        tenant_id = row[0]

        # Verifica existentes
        existing = set(
            r[0]
            for r in (
                await session.execute(
                    select(MonitoramentoCatalogo.nome_popular).where(
                        MonitoramentoCatalogo.is_system == True,
                    )
                )
            ).all()
        )

        inseridos = 0
        for e in ENTRADAS:
            if e["nome_popular"] in existing:
                continue
            session.add(MonitoramentoCatalogo(
                tenant_id=tenant_id,
                is_system=True,
                ativo=True,
                **e,
            ))
            inseridos += 1

        await session.commit()
        print(f"Seed concluído: {inseridos} entradas inseridas ({len(existing)} já existiam).")


if __name__ == "__main__":
    asyncio.run(seed())
