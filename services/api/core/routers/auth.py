from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from core.dependencies import get_session, get_current_user_claims
from core.schemas.auth_schemas import LoginRequest, UserCreateRequest, TokenResponse, UsuarioMeResponse
from core.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["SaaS — Identity & Auth"])

@router.post("/register", response_model=UsuarioMeResponse, status_code=status.HTTP_201_CREATED, summary="Registra um novo usuário global (Produtor/Gestor)")
async def register(dados: UserCreateRequest, session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    user = await svc.register_user(dados)
    return await svc.get_user_me(user.id)

@router.post("/login", response_model=TokenResponse, summary="Autentica e gera Token (Substitui o gen_token.py simulador)")
async def login(dados: LoginRequest, session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    user, token = await svc.authenticate_user(dados)
    return TokenResponse(access_token=token)

@router.get("/me", response_model=UsuarioMeResponse, summary="Retorna os dados do usuário global logado com suas contas (Tenants) conectadas")
async def get_me(claims: dict = Depends(get_current_user_claims), session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    user_id = uuid.UUID(claims["sub"])
    return await svc.get_user_me(user_id)
