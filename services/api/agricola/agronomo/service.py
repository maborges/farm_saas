from uuid import UUID
from datetime import datetime
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
