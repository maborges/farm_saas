from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, get_current_user_claims
from core.dependencies import get_session_with_tenant
from agricola.agronomo.schemas import MensagemCreate, RespostaIA, ConversaResponse
from agricola.agronomo.service import AgronomoService

router = APIRouter(prefix="/agronomo", tags=["Agrônomo Virtual (IA/Ollama)"])

@router.post("/chat", response_model=RespostaIA)
async def conversar_com_ia(
    dados: MensagemCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    claims: dict = Depends(get_current_user_claims),
    _: None = Depends(require_module("A1")),
):
    svc = AgronomoService(session, tenant_id)
    usuario_id = UUID(claims.get("sub"))
    resposta = await svc.enviar_mensagem(usuario_id, dados)
    return RespostaIA(**resposta)

@router.get("/conversas", response_model=List[ConversaResponse])
async def listar_conversas(
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    claims: dict = Depends(get_current_user_claims),
    _: None = Depends(require_module("A1")),
):
    svc = AgronomoService(session, tenant_id)
    usuario_id = UUID(claims.get("sub"))
    conversas = await svc.list_all(usuario_id=usuario_id)
    return [ConversaResponse.model_validate(c) for c in conversas]

from agricola.agronomo.schemas import RelatorioTecnicoCreate, RelatorioTecnicoUpdate, RelatorioTecnicoResponse
from agricola.agronomo.service import RelatorioTecnicoService

@router.get("/rat", response_model=List[RelatorioTecnicoResponse])
async def listar_rats(
    safra_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = RelatorioTecnicoService(session, tenant_id)
    if safra_id:
        rats = await svc.listar_por_safra(safra_id)
    else:
        rats = await svc.list_all()
    return [RelatorioTecnicoResponse.model_validate(r) for r in rats]

@router.post("/rat", response_model=RelatorioTecnicoResponse, status_code=status.HTTP_201_CREATED)
async def criar_rat(
    dados: RelatorioTecnicoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    claims: dict = Depends(get_current_user_claims),
    _: None = Depends(require_module("A1")),
):
    svc = RelatorioTecnicoService(session, tenant_id)
    usuario_id = UUID(claims.get("sub"))
    rat = await svc.criar_rat(usuario_id, dados)
    return RelatorioTecnicoResponse.model_validate(rat)

@router.get("/rat/{rat_id}", response_model=RelatorioTecnicoResponse)
async def obter_rat(
    rat_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = RelatorioTecnicoService(session, tenant_id)
    rat = await svc.get_or_fail(rat_id)
    return RelatorioTecnicoResponse.model_validate(rat)

@router.patch("/rat/{rat_id}", response_model=RelatorioTecnicoResponse)
async def atualizar_rat(
    rat_id: UUID,
    dados: RelatorioTecnicoUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = RelatorioTecnicoService(session, tenant_id)
    rat = await svc.atualizar_rat(rat_id, dados)
    return RelatorioTecnicoResponse.model_validate(rat)
