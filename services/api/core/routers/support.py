from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from core.dependencies import get_session, get_current_user, get_current_tenant
from core.models.tenant import Tenant
from core.models.auth import Usuario
from core.models.support import ChamadoSuporte, MensagemChamado, TicketStatus
from core.schemas.support_schemas import (
    ChamadoSuporteCreate, ChamadoSuporteResponse, 
    ChamadoDetalheResponse, MensagemChamadoCreate, MensagemChamadoResponse
)

router = APIRouter(prefix="/support", tags=["Suporte / Tickets"])

@router.post("/tickets", response_model=ChamadoSuporteResponse)
async def create_ticket(
    data: ChamadoSuporteCreate,
    user: Usuario = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Abre um novo chamado de suporte."""
    chamado = ChamadoSuporte(
        tenant_id=tenant.id,
        usuario_abertura_id=user.id,
        assunto=data.assunto,
        categoria=data.categoria,
        prioridade=data.prioridade,
        status=TicketStatus.ABERTO
    )
    session.add(chamado)
    await session.flush()
    
    # Criar a primeira mensagem
    msg = MensagemChamado(
        chamado_id=chamado.id,
        usuario_id=user.id,
        conteudo=data.mensagem_inicial,
        is_admin_reply=False
    )
    session.add(msg)
    
    await session.commit()
    return chamado

@router.get("/tickets", response_model=List[ChamadoSuporteResponse])
async def list_my_tickets(
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Lista todos os chamados da empresa logada."""
    stmt = select(ChamadoSuporte).where(ChamadoSuporte.tenant_id == tenant.id).order_by(ChamadoSuporte.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/tickets/{ticket_id}", response_model=ChamadoDetalheResponse)
async def get_ticket_details(
    ticket_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Retorna os detalhes e mensagens de um chamado."""
    stmt = select(ChamadoSuporte).where(
        ChamadoSuporte.id == ticket_id,
        ChamadoSuporte.tenant_id == tenant.id
    )
    result = await session.execute(stmt)
    chamado = result.scalar_one_or_none()
    
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    
    return chamado

@router.post("/tickets/{ticket_id}/messages", response_model=MensagemChamadoResponse)
async def reply_to_ticket(
    ticket_id: uuid.UUID,
    data: MensagemChamadoCreate,
    user: Usuario = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Usuário envia uma nova mensagem no chamado."""
    chamado = await session.get(ChamadoSuporte, ticket_id)
    if not chamado or chamado.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    
    if chamado.status == TicketStatus.CONCLUIDO:
        raise HTTPException(status_code=400, detail="Este chamado já foi concluído.")

    msg = MensagemChamado(
        chamado_id=ticket_id,
        usuario_id=user.id,
        conteudo=data.conteudo,
        anexo_url=data.anexo_url,
        is_admin_reply=False
    )
    
    # Se o cliente respondeu, volta para status ABERTO ou EM_ATENDIMENTO se já estava sendo atendido
    if chamado.status == TicketStatus.AGUARDANDO_CLIENTE:
        chamado.status = TicketStatus.EM_ATENDIMENTO

    session.add(msg)
    await session.commit()
    return msg
