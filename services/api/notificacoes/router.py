from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, status
import asyncio
from loguru import logger
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, get_session_with_tenant
from core.database import async_session_maker
from notificacoes.models import Notificacao
from notificacoes.schemas import NotificacaoCreate, NotificacaoResponse, MarcarLidasRequest
from notificacoes.service import NotificacaoService, manager

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])


# ── REST ──────────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[NotificacaoResponse])
async def listar(
    lida: Optional[bool] = None,
    limit: int = 50,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    svc = NotificacaoService(session, tenant_id)
    return await svc.listar(lida=lida, limit=limit)


@router.get("/nao-lidas-count")
async def count_nao_lidas(
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    svc = NotificacaoService(session, tenant_id)
    return {"count": await svc.total_nao_lidas()}


@router.post("/marcar-lidas")
async def marcar_lidas(
    dados: MarcarLidasRequest,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    svc = NotificacaoService(session, tenant_id)
    count = await svc.marcar_lidas(dados.ids)
    return {"message": f"{count} notificação(ões) marcada(s) como lida(s)"}


@router.post("/", response_model=NotificacaoResponse, status_code=status.HTTP_201_CREATED)
async def criar(
    dados: NotificacaoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    svc = NotificacaoService(session, tenant_id)
    return await svc.criar_e_push(dados)


@router.post("/demo")
async def gerar_demo(
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Cria notificações de demonstração para testar o sistema."""
    svc = NotificacaoService(session, tenant_id)
    demos = [
        NotificacaoCreate(
            tipo="PREVISAO_CHUVA",
            titulo="Chuva prevista nas próximas 24h",
            mensagem="Risco de perda de eficiência em aplicações de defensivos. Evite aplicações nos Talhões A1 e B2.",
            meta={"talhoes": ["A1", "B2"], "precipitacao_mm": 35},
        ),
        NotificacaoCreate(
            tipo="NDVI_BAIXO",
            titulo="NDVI crítico — Talhão Norte",
            mensagem="NDVI do Talhão Norte caiu para 0.42, abaixo do limiar de 0.55. Verifique o desenvolvimento da cultura.",
            meta={"talhao": "Talhão Norte", "ndvi": 0.42, "limiar": 0.55},
        ),
        NotificacaoCreate(
            tipo="DIARIA_PENDENTE",
            titulo="3 diárias pendentes há mais de 15 dias",
            mensagem="Colaboradores com diárias não pagas: João Silva (3×), Maria Santos (2×). Total: R$ 750,00.",
            meta={"total_pendente": 750.0, "colaboradores": 2},
        ),
        NotificacaoCreate(
            tipo="VENCIMENTO_APLICACAO",
            titulo="Carência de aplicação vence amanhã",
            mensagem="O defensivo aplicado no Talhão Sul (Lote 04/B) tem carência vencendo em 24h. Não colher antes.",
            meta={"talhao": "Talhão Sul", "defensivo": "Fungicida X", "carencia_dias": 1},
        ),
    ]
    for d in demos:
        await svc.criar_e_push(d)
    return {"message": f"{len(demos)} notificações de demonstração criadas"}


# ── WebSocket ─────────────────────────────────────────────────────────────────

@router.websocket("/ws")
async def ws_notificacoes(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    WebSocket de notificações em tempo real.
    Conecte com: ws://<host>/api/v1/notificacoes/ws?token=<jwt>
    """
    from core.config import settings
    from jose import jwt as jose_jwt, JWTError

    try:
        payload = jose_jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        tenant_id: str = payload.get("tenant_id", "")
        if not tenant_id:
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return

    await manager.connect(tenant_id, websocket)
    try:
        # Send initial unread count on connect
        async with async_session_maker() as session:
            svc = NotificacaoService(session, UUID(tenant_id))
            count = await svc.total_nao_lidas()
            await websocket.send_json({"tipo": "init", "nao_lidas": count})

        # Listen for client-side actions (e.g. mark as read)
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "marcar_lidas":
                raw_ids = data.get("ids")
                ids = [UUID(i) for i in raw_ids] if raw_ids else None
                async with async_session_maker() as session:
                    svc = NotificacaoService(session, UUID(tenant_id))
                    await svc.marcar_lidas(ids)
                    count = await svc.total_nao_lidas()
                    await websocket.send_json({"tipo": "contagem_atualizada", "nao_lidas": count})

            elif action == "ping":
                await websocket.send_json({"tipo": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(tenant_id, websocket)
    except Exception as exc:
        logger.exception(f"WS notificacoes erro inesperado (tenant={tenant_id}): {exc}")
        manager.disconnect(tenant_id, websocket)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
