"""
Gerenciamento de sessões ativas — visão tenant-facing.

Endpoints:
  GET  /auth/sessions/me          — sessões do usuário logado
  DELETE /auth/sessions/{id}      — revogar sessão própria
  GET  /auth/sessions/team        — owner/admin vê sessões da equipe
  DELETE /auth/sessions/team/{id} — owner/admin revoga sessão de membro
"""
import hashlib
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import (
    get_current_user_claims,
    get_session,
    get_tenant_id,
    invalidate_session_cache,
    require_tenant_permission,
)
from core.models.sessao import SessaoAtiva

router = APIRouter(prefix="/auth/sessions", tags=["Sessões Ativas"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class SessaoResponse(BaseModel):
    id: uuid.UUID
    ip_address: str | None
    user_agent: str | None
    inicio: datetime
    ultimo_heartbeat: datetime
    expira_em: datetime
    status: str
    is_current: bool = False

    class Config:
        from_attributes = True


class SessaoMembroResponse(SessaoResponse):
    usuario_id: uuid.UUID


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _token_hash_from_request(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return hashlib.sha256(auth[7:].encode()).hexdigest()
    return None


# ---------------------------------------------------------------------------
# Endpoints — sessões do próprio usuário
# ---------------------------------------------------------------------------

@router.get("/me", response_model=List[SessaoResponse])
async def listar_minhas_sessoes(
    request: Request,
    claims: dict = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_session),
):
    """Lista todas as sessões ativas do usuário logado."""
    usuario_id = uuid.UUID(claims["sub"])
    current_hash = _token_hash_from_request(request)

    result = await db.execute(
        select(SessaoAtiva)
        .where(SessaoAtiva.usuario_id == usuario_id, SessaoAtiva.status == "ATIVA")
        .order_by(SessaoAtiva.ultimo_heartbeat.desc())
    )
    sessoes = result.scalars().all()

    out = []
    for s in sessoes:
        data = SessaoResponse.model_validate(s)
        data.is_current = s.token_hash == current_hash
        out.append(data)
    return out


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def revogar_todas_minhas_sessoes(
    request: Request,
    claims: dict = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_session),
):
    """Encerra todas as sessões do usuário logado (exceto a atual)."""
    usuario_id = uuid.UUID(claims["sub"])
    current_hash = _token_hash_from_request(request)

    result = await db.execute(
        select(SessaoAtiva).where(
            SessaoAtiva.usuario_id == usuario_id,
            SessaoAtiva.status == "ATIVA",
            SessaoAtiva.token_hash != current_hash,
        )
    )
    sessoes = result.scalars().all()
    for s in sessoes:
        s.status = "ENCERRADA"
        invalidate_session_cache(s.token_hash)

    await db.commit()


@router.delete("/me/{sessao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revogar_minha_sessao(
    sessao_id: uuid.UUID,
    claims: dict = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_session),
):
    """Encerra uma sessão específica do usuário logado."""
    usuario_id = uuid.UUID(claims["sub"])

    sessao = await db.get(SessaoAtiva, sessao_id)
    if not sessao or sessao.usuario_id != usuario_id:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    sessao.status = "ENCERRADA"
    invalidate_session_cache(sessao.token_hash)
    await db.commit()


# ---------------------------------------------------------------------------
# Endpoints — visão da equipe (owner / admin)
# ---------------------------------------------------------------------------

@router.get(
    "/team",
    response_model=List[SessaoMembroResponse],
    dependencies=[Depends(require_tenant_permission("core:sessions:view"))],
)
async def listar_sessoes_equipe(
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Lista sessões ativas de todos os membros do tenant."""
    result = await db.execute(
        select(SessaoAtiva)
        .where(SessaoAtiva.tenant_id == tenant_id, SessaoAtiva.status == "ATIVA")
        .order_by(SessaoAtiva.ultimo_heartbeat.desc())
        .limit(500)
    )
    return result.scalars().all()


@router.delete(
    "/team/{sessao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_tenant_permission("core:sessions:manage"))],
)
async def revogar_sessao_membro(
    sessao_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    """Owner/admin encerra a sessão de qualquer membro do tenant."""
    sessao = await db.get(SessaoAtiva, sessao_id)
    if not sessao or sessao.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    sessao.status = "ENCERRADA"
    invalidate_session_cache(sessao.token_hash)
    await db.commit()


# ---------------------------------------------------------------------------
# Endpoint de logout
# ---------------------------------------------------------------------------

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    claims: dict = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_session),
):
    """Encerra a sessão atual do usuário (logout)."""
    token_hash = _token_hash_from_request(request)
    if not token_hash:
        raise HTTPException(status_code=400, detail="Token não encontrado")

    result = await db.execute(
        select(SessaoAtiva).where(SessaoAtiva.token_hash == token_hash)
    )
    sessao = result.scalar_one_or_none()

    if sessao:
        sessao.status = "ENCERRADA"
        invalidate_session_cache(token_hash)
        await db.commit()
