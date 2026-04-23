import asyncio
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine
from core.database import Base, DB_URL, async_session_maker
from core.models import Tenant, Fazenda
from core.cadastros.propriedades.models import AreaRural
from agricola.analises_solo.models import AnaliseSolo
from agricola.analises_solo.service import AnaliseSoloService
from agricola.safras.models import Safra
from agricola.tarefas.models import SafraTarefa
from sqlalchemy import select

async def validate():
    print(f"🔍 Iniciando Validação de Inteligência de Solo...")
    
    tenant_id = uuid.UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")
    
    async with async_session_maker() as session:
        # 1. Preparar Talhão com Área
        t_id = uuid.uuid4()
        talhao = AreaRural(
            id=t_id,
            tenant_id=tenant_id,
            unidade_produtiva_id=uuid.uuid4(), # Fazenda dummy
            tipo="TALHAO",
            nome="Talhão de Teste Validação",
            area_hectares_manual=10.0, # 10 hectares para facilitar a conta
            ativo=True
        )
        session.add(talhao)
        
        # 2. Preparar Safra
        s_id = uuid.uuid4()
        safra = Safra(
            id=s_id,
            tenant_id=tenant_id,
            talhao_id=t_id,
            ano_safra="2024/25",
            cultura="MILHO",
            status="EM_ANDAMENTO"
        )
        session.add(safra)
        
        # 3. Criar Análise de Solo com V% baixo
        a_id = uuid.uuid4()
        analise = AnaliseSolo(
            id=a_id,
            tenant_id=tenant_id,
            talhao_id=t_id,
            data_coleta=date.today(),
            ph_agua=5.0,
            v_pct=35.0,
            ctc=12.0,
            fosforo_p=5.0, # Baixo
            potassio_k=40.0 # Baixo
        )
        session.add(analise)
        await session.commit()
        
        print(f"✅ Dados de base criados: Talhão 10ha, Safra Milho, Análise Solo (V=35%, P=5, K=40)")

        # 4. Invocação do Service para gerar recomendações e tarefas
        svc = AnaliseSoloService(session, tenant_id)
        
        print(f"⚙️  Gerando recomendações e tarefas...")
        tarefas_ids = await svc.vincular_e_gerar_tarefas(a_id, s_id)
        
        await session.commit()
        print(f"✅ {len(tarefas_ids)} tarefas geradas!")

        # 5. Verificação de Resultados Financeiros e Técnicos
        print(f"📊 Verificando integridade das tarefas...")
        stmt = select(SafraTarefa).where(SafraTarefa.id.in_(tarefas_ids))
        res = await session.execute(stmt)
        tarefas = res.scalars().all()
        
        for t in tarefas:
            print(f"   - Tarefa: {t.tipo}")
            print(f"     Description: {t.descricao}")
            print(f"     Dose Estimada: {t.dose_estimada_kg_ha} kg/ha")
            print(f"     Qtd Total: {t.quantidade_total_estimada_kg} kg")
            print(f"     Custo Est: R$ {t.custo_estimado}")
            
            # Validação básica
            assert t.area_ha == 10.0
            assert t.custo_estimado > 0
            assert t.quantidade_total_estimada_kg == float(t.dose_estimada_kg_ha) * 10.0
            print(f"     ✅ Validação: OK")

        print(f"\n🚀 VALIDAÇÃO CONCLUÍDA COM SUCESSO!")

if __name__ == "__main__":
    asyncio.run(validate())
