import asyncio
import uuid
from datetime import date, datetime
from sqlalchemy.ext.asyncio import create_async_engine
from core.database import Base, DB_URL, async_session_maker
from core.models import Tenant, Fazenda
# grupos_fazendas removed
from core.models.billing import PlanoAssinatura, AssinaturaTenant
from agricola.safras.models import Safra
from core.cadastros.propriedades.models import AreaRural
from agricola.cadastros.models import Cultura
from agricola.operacoes.models import OperacaoAgricola
from financeiro.models.plano_conta import PlanoConta
from financeiro.models.despesa import Despesa
from financeiro.models.rateio import Rateio
from pecuaria.models.piquete import Piquete
from pecuaria.animal.models import LoteAnimal as LoteBovino

# Engine para setup
engine = create_async_engine(DB_URL, echo=False)

async def init_db():
    print(f"🔄 Conectando em: {DB_URL}")
    
    async with engine.begin() as conn:
        print("🗑️  Limpando tabelas...")
        await conn.run_sync(Base.metadata.drop_all)
        print("🏗️  Recriando tabelas...")
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Banco pronto!")

    async with async_session_maker() as session:
        # 1. Tenant
        tenant_id = uuid.UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")
        tenant = Tenant(
            id=tenant_id,
            nome="Fazendas Ouro Verde",
            documento="12.345.678/0001-99",
        )
        session.add(tenant)
        await session.flush()

        # 1b. Grupo de fazendas + plano + assinatura
        grupo_id = uuid.UUID("a1b2c3d4-0000-0000-0000-000000000001")

        plano = PlanoAssinatura(
            nome="Plano Dev Seed",
            modulos_inclusos=[
                "CORE",
                "A1_PLANEJAMENTO",
                "F1_TESOURARIA",
                "O1_FROTA",
                "P1_REBANHO",
            ],
            max_fazendas=-1,
            preco_mensal=0,
            preco_anual=0,
        )
        session.add(plano)
        await session.flush()

        assinatura = AssinaturaTenant(
            tenant_id=tenant_id,
            plano_id=plano.id,
            tipo_assinatura="TENANT",
            status="ATIVA",
        )
        session.add(assinatura)

        # 2. Fazendas (vinculadas ao grupo)
        unidade_produtiva_id = uuid.UUID("e10b4290-7d71-4828-b80c-7b243ebd9e2f")
        fazenda = Fazenda(
            id=unidade_produtiva_id,
            tenant_id=tenant_id,
            grupo_id=grupo_id,
            nome="Fazenda Matriz - Chapadão",
            cnpj="12.345.678/0001-99"
        )
        session.add(fazenda)

        fazenda_id2 = uuid.UUID("f5979c3f-c1f0-4fe7-ad87-8ce698ccb0f5")
        fazenda2 = Fazenda(
            id=fazenda_id2,
            tenant_id=tenant_id,
            grupo_id=grupo_id,
            nome="Fazenda Araguaia (MG)",
            cnpj="12.345.678/0001-98"
        )
        session.add(fazenda2)
        await session.flush()
        
        # 3. Culturas
        soja = Cultura(id=uuid.uuid4(), tenant_id=tenant_id, nome="Soja", variedade="BMX DESAFIO", ciclo_dias=115)
        milho = Cultura(id=uuid.uuid4(), tenant_id=tenant_id, nome="Milho", variedade="DKB 255", ciclo_dias=140)
        session.add_all([soja, milho])
        await session.flush()

        # 4. Talhoes
        t1 = AreaRural(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            unidade_produtiva_id=unidade_produtiva_id,
            tipo="TALHAO",
            nome="Talhão 01 - Norte",
            area_hectares_manual=50.5,
            dados_extras={"irrigado": False},
        )
        t2 = AreaRural(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            unidade_produtiva_id=unidade_produtiva_id,
            tipo="TALHAO",
            nome="Talhão 02 - Sul",
            area_hectares_manual=40.0,
            dados_extras={"irrigado": True},
        )
        session.add_all([t1, t2])
        await session.flush()

        # 5. Safras
        safra1 = Safra(
            tenant_id=tenant_id,
            talhao_id=t1.id,
            ano_safra="2024/25",
            cultura="Soja",
            cultivar_id=soja.id,
            data_plantio_prevista=date(2024, 10, 15),
            status="EM_ANDAMENTO"
        )
        session.add(safra1)
        await session.flush()

        # 6. Operações
        op1 = OperacaoAgricola(
            tenant_id=tenant_id,
            safra_id=safra1.id,
            talhao_id=t1.id,
            tipo="PLANTIO",
            descricao="Plantio de Soja BMX",
            data_realizada=date(2024, 10, 20),
            status="REALIZADA"
        )
        session.add(op1)

        # 7. Financeiro
        plano = PlanoConta(tenant_id=tenant_id, nome="Insumos", codigo="1.01", tipo="DESPESA")
        session.add(plano)
        await session.flush()

        despesa = Despesa(
            tenant_id=tenant_id,
            unidade_produtiva_id=unidade_produtiva_id,
            plano_conta_id=plano.id,
            descricao="Compra de Sementes",
            valor_total=15000.0,
            status="A_PAGAR",
            data_emissao=date.today(),
            data_vencimento=date.today()
        )
        session.add(despesa)
        await session.flush()

        # 8. Pecuária
        piquete = Piquete(
            tenant_id=tenant_id,
            unidade_produtiva_id=unidade_produtiva_id,
            nome="Pasto 01",
            area_ha=25.0
        )
        session.add(piquete)
        await session.flush()

        lote = LoteBovino(
            tenant_id=tenant_id,
            unidade_produtiva_id=unidade_produtiva_id,
            piquete_id=piquete.id,
            identificacao="Lote 101",
            categoria="RECRIA",
            raca="NELORE",
            quantidade_cabecas=100,
            peso_medio_kg=250.0,
            data_formacao=date.today()
        )
        session.add(lote)

        await session.commit()
        print("🌱 Seed finalizado com sucesso!")

if __name__ == "__main__":
    asyncio.run(init_db())
