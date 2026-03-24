from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from core.dependencies import get_session, get_current_user_claims, get_tenant_id
from core.schemas.onboarding_schemas import AssinanteRegisterRequest, ConviteCreateRequest, ConviteResponse
from core.services.onboarding_service import OnboardingService
from core.services.auth_service import AuthService
from core.schemas.auth_schemas import TokenResponse, UsuarioMeResponse

router = APIRouter(prefix="/onboarding", tags=["SaaS — Onboarding & Equipe"])

@router.post("/assinante", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, summary="Registro completo do Produtor (Conta + Fazenda + Assinatura)")
async def registrar_assinante(dados: AssinanteRegisterRequest, session: AsyncSession = Depends(get_session)):
    auth_svc = AuthService(session)
    onboard_svc = OnboardingService(session, auth_svc)
    
    # 1. Realiza a montanha-russa de criação
    user = await onboard_svc.register_new_tenant(dados)
    
    # 2. Loga o usuário de imediato retornando token
    from core.schemas.auth_schemas import LoginRequest
    login_data = LoginRequest(email=dados.email, senha=dados.senha)
    _, token = await auth_svc.authenticate_user(login_data)
    
    return TokenResponse(access_token=token)

@router.post("/convites", response_model=ConviteResponse, status_code=status.HTTP_201_CREATED, summary="Gera link seguro por e-mail para adicionar membro à fazenda")
async def gerar_convite(
    dados: ConviteCreateRequest, 
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    claims: dict = Depends(get_current_user_claims)
):
    invoker_id = uuid.UUID(claims["sub"])
    onboard_svc = OnboardingService(session)
    
    convite = await onboard_svc.enviar_convite(tenant_id, invoker_id, dados)
    return convite

@router.post("/convites/aceitar", summary="Membro clica no link e aceita a vaga na empresa/fazenda")
async def aceitar_convite(
    token: str,
    session: AsyncSession = Depends(get_session),
    claims: dict = Depends(get_current_user_claims) # Ele precisa ter criado uma conta/logado pra aceitar
):
    user_id = uuid.UUID(claims["sub"])
    onboard_svc = OnboardingService(session)
    
    resultado = await onboard_svc.aceitar_convite(token, user_id)
    return resultado
