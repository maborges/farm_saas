from uuid import UUID
from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.exceptions import BusinessRuleError
from core.base_service import BaseService

from agricola.agronomo.models import ConversaAgronomo
from agricola.agronomo.schemas import MensagemCreate

class AgronomoService(BaseService[ConversaAgronomo]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(ConversaAgronomo, session, tenant_id)

    async def enviar_mensagem(self, usuario_id: UUID, dados: MensagemCreate) -> dict:
        conversa = None
        if dados.conversa_id:
            conversa = await self.get_or_fail(dados.conversa_id)
        
        if not conversa:
            conversa = ConversaAgronomo(
                tenant_id=self.tenant_id,
                usuario_id=usuario_id,
                titulo=f"Conversa {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                contexto_atual=dados.contexto,
                historico_mensagens=[]
            )
            self.session.add(conversa)
            await self.session.flush()
            
        # Adiciona a mensagem do usuario
        mensagens = list(conversa.historico_mensagens)
        mensagens.append({"role": "user", "content": dados.conteudo})
        
        # Aqui integrariamos com o Ollama / LangChain para RAG local
        # mock response:
        resposta_ia = "Sou o Agrônomo Virtual. Identifiquei que seus níveis de Potássio no talhão estão baixos."
        
        mensagens.append({"role": "assistant", "content": resposta_ia})
        
        # Atualiza a flag JSON na marra ou usando ORM
        conversa.historico_mensagens = mensagens
        await self.session.commit()
        await self.session.refresh(conversa)
        
        return {
            "conversa_id": conversa.id,
            "mensagem": resposta_ia
        }

from agricola.agronomo.models import RelatorioTecnico
from agricola.agronomo.schemas import RelatorioTecnicoCreate, RelatorioTecnicoUpdate

class RelatorioTecnicoService(BaseService[RelatorioTecnico]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(RelatorioTecnico, session, tenant_id)

    async def listar_por_safra(self, safra_id: UUID) -> List[RelatorioTecnico]:
        query = select(RelatorioTecnico).where(
            RelatorioTecnico.tenant_id == self.tenant_id,
            RelatorioTecnico.safra_id == safra_id
        ).order_by(RelatorioTecnico.data_visita.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def criar_rat(self, usuario_id: UUID, dados: RelatorioTecnicoCreate) -> RelatorioTecnico:
        novo_rat = RelatorioTecnico(
            tenant_id=self.tenant_id,
            usuario_id=usuario_id,
            safra_id=dados.safra_id,
            talhao_id=dados.talhao_id,
            data_visita=dados.data_visita or datetime.now(),
            estadio_fenologico=dados.estadio_fenologico,
            condicao_climatica=dados.condicao_climatica,
            observacoes_gerais=dados.observacoes_gerais,
            recomendacoes=dados.recomendacoes,
            constatacoes=[c.model_dump() for c in dados.constatacoes],
            status=dados.status
        )
        self.session.add(novo_rat)
        await self.session.commit()
        await self.session.refresh(novo_rat)
        return novo_rat

    async def atualizar_rat(self, rat_id: UUID, dados: RelatorioTecnicoUpdate) -> RelatorioTecnico:
        rat = await self.get_or_fail(rat_id)
        
        update_data = dados.model_dump(exclude_unset=True)
        if "constatacoes" in update_data and update_data["constatacoes"] is not None:
            update_data["constatacoes"] = [c.model_dump() if hasattr(c, 'model_dump') else c for c in update_data["constatacoes"]]

        for key, value in update_data.items():
            setattr(rat, key, value)
            
        await self.session.commit()
        await self.session.refresh(rat)
        return rat
