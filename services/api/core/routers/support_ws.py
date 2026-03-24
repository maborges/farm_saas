"""
WebSocket router para chat em tempo real nos chamados de suporte.

Mantém conexões agrupadas por ticket_id. Quando uma mensagem chega,
é persistida e retransmitida a todos os participantes conectados
naquele chamado (usuário + admin).
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List
import json
import uuid
from datetime import datetime, timezone

from core.database import async_session_maker
from core.models.support import ChamadoSuporte, MensagemChamado, TicketStatus
from core.models.auth import Usuario
from jose import jwt, JWTError
from core.config import settings

router = APIRouter(prefix="/ws", tags=["WebSocket Suporte"])

# ─── Connection Manager ────────────────────────────────────────────────────────

class TicketConnectionManager:
    """Gerencia conexões WebSocket agrupadas por ticket_id."""

    def __init__(self) -> None:
        # { ticket_id: [ (websocket, user_id, is_admin) ] }
        self._rooms: Dict[str, List[tuple[WebSocket, str, bool]]] = {}

    async def connect(
        self, websocket: WebSocket, ticket_id: str, user_id: str, is_admin: bool
    ) -> None:
        await websocket.accept()
        self._rooms.setdefault(ticket_id, [])
        self._rooms[ticket_id].append((websocket, user_id, is_admin))

    def disconnect(self, websocket: WebSocket, ticket_id: str) -> None:
        if ticket_id in self._rooms:
            self._rooms[ticket_id] = [
                entry for entry in self._rooms[ticket_id] if entry[0] is not websocket
            ]

    async def broadcast_to_ticket(self, ticket_id: str, payload: dict) -> None:
        """Envia mensagem a todos os participantes do ticket."""
        for ws, _, _ in self._rooms.get(ticket_id, []):
            try:
                await ws.send_json(payload)
            except Exception:
                pass  # conexão morreu — será removida pelo disconnect


manager = TicketConnectionManager()


# ─── Auth Helper ─────────────────────────────────────────────────────────────

async def _resolve_user_from_token(token: str) -> tuple[str, bool]:
    """
    Valida JWT e retorna (user_id, is_superuser).

    Args:
        token: JWT bearer token passado via query param.

    Returns:
        Tupla com UUID do usuário e flag de superusuário.

    Raises:
        HTTPException 401 se token inválido.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido.")

    async with async_session_maker() as session:
        stmt = select(Usuario).where(Usuario.id == uuid.UUID(user_id))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user or not user.ativo:
            raise HTTPException(status_code=401, detail="Usuário não encontrado.")
        return str(user.id), user.is_superuser, tenant_id


# ─── WebSocket Endpoint ────────────────────────────────────────────────────────

@router.websocket("/tickets/{ticket_id}")
async def websocket_ticket_chat(
    websocket: WebSocket,
    ticket_id: str,
    token: str,
):
    """
    WebSocket para troca de mensagens em tempo real num chamado de suporte.

    Protocolo de mensagem recebida (JSON):
        { "conteudo": "texto da mensagem" }

    Payload emitido para todos os participantes:
        {
            "id": "<uuid>",
            "chamado_id": "<uuid>",
            "usuario_id": "<uuid>",
            "conteudo": "...",
            "is_admin_reply": bool,
            "created_at": "<iso8601>"
        }

    Args:
        ticket_id: UUID do chamado de suporte.
        token: JWT de autenticação (query param ?token=...).
    """
    try:
        user_id, is_admin, token_tenant_id = await _resolve_user_from_token(token)
    except HTTPException:
        await websocket.close(code=4001, reason="Não autorizado")
        return

    ticket_uuid = uuid.UUID(ticket_id)

    # Confirma que o ticket existe e o usuário tem acesso
    async with async_session_maker() as session:
        chamado = await session.get(ChamadoSuporte, ticket_uuid)
        if not chamado:
            await websocket.close(code=4004, reason="Chamado não encontrado")
            return

        if not is_admin and str(chamado.tenant_id) != token_tenant_id:
            await websocket.close(code=4003, reason="Acesso negado ao ticket")
            return

    await manager.connect(websocket, ticket_id, user_id, is_admin)

    # Envia evento de presença
    await websocket.send_json({"event": "connected", "ticket_id": ticket_id})

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            conteudo: str = data.get("conteudo", "").strip()

            if not conteudo:
                continue

            # Persiste a mensagem
            async with async_session_maker() as session:
                chamado = await session.get(ChamadoSuporte, ticket_uuid)
                if not chamado or chamado.status == TicketStatus.CONCLUIDO:
                    await websocket.send_json({"error": "Chamado encerrado ou não encontrado."})
                    continue

                msg = MensagemChamado(
                    chamado_id=ticket_uuid,
                    usuario_id=uuid.UUID(user_id),
                    conteudo=conteudo,
                    is_admin_reply=is_admin,
                )

                # Se cliente responde após aguardar, volta para em atendimento
                if not is_admin and chamado.status == TicketStatus.AGUARDANDO_CLIENTE:
                    chamado.status = TicketStatus.EM_ATENDIMENTO

                session.add(msg)
                await session.commit()
                await session.refresh(msg)

                payload = {
                    "id": str(msg.id),
                    "chamado_id": str(msg.chamado_id),
                    "usuario_id": str(msg.usuario_id),
                    "conteudo": msg.conteudo,
                    "is_admin_reply": msg.is_admin_reply,
                    "created_at": msg.created_at.isoformat(),
                    "anexo_url": msg.anexo_url,
                }

            await manager.broadcast_to_ticket(ticket_id, payload)

    except WebSocketDisconnect:
        manager.disconnect(websocket, ticket_id)
    except Exception:
        manager.disconnect(websocket, ticket_id)
        await websocket.close(code=1011)
