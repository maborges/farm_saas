from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, func
from fastapi import WebSocket

from core.base_service import BaseService
from notificacoes.models import Notificacao
from notificacoes.schemas import NotificacaoCreate


class NotificationManager:
    """Manages active WebSocket connections grouped by tenant_id."""

    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, tenant_id: str, ws: WebSocket):
        await ws.accept()
        self._connections.setdefault(tenant_id, []).append(ws)

    def disconnect(self, tenant_id: str, ws: WebSocket):
        conns = self._connections.get(tenant_id, [])
        if ws in conns:
            conns.remove(ws)

    async def push(self, tenant_id: str, data: dict):
        """Send JSON payload to all connections for a tenant."""
        for ws in list(self._connections.get(str(tenant_id), [])):
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect(str(tenant_id), ws)


# Singleton — shared across the FastAPI process
manager = NotificationManager()


class NotificacaoService(BaseService[Notificacao]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(Notificacao, session, tenant_id)

    async def criar_e_push(self, dados: NotificacaoCreate) -> Notificacao:
        notif = await self.create({
            "tipo": dados.tipo,
            "titulo": dados.titulo,
            "mensagem": dados.mensagem,
            "meta": dados.meta,
        })
        await self.session.commit()
        await self.session.refresh(notif)
        # Push to all connected clients of this tenant
        await manager.push(str(self.tenant_id), {
            "tipo": "nova_notificacao",
            "id": str(notif.id),
            "notificacao_tipo": notif.tipo,
            "titulo": notif.titulo,
            "mensagem": notif.mensagem,
            "created_at": notif.created_at.isoformat(),
        })
        return notif

    async def listar(self, lida: bool | None = None, limit: int = 50) -> list[Notificacao]:
        stmt = (
            select(Notificacao)
            .where(Notificacao.tenant_id == self.tenant_id)
        )
        if lida is not None:
            stmt = stmt.where(Notificacao.lida == lida)
        stmt = stmt.order_by(Notificacao.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def marcar_lidas(self, ids: list[UUID] | None = None) -> int:
        stmt = (
            update(Notificacao)
            .where(Notificacao.tenant_id == self.tenant_id)
        )
        if ids:
            stmt = stmt.where(Notificacao.id.in_(ids))
        stmt = stmt.values(lida=True)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def total_nao_lidas(self) -> int:
        stmt = (
            select(func.count(Notificacao.id))
            .where(
                Notificacao.tenant_id == self.tenant_id,
                Notificacao.lida == False,  # noqa: E712
            )
        )
        return (await self.session.execute(stmt)).scalar() or 0
