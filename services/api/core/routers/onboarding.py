from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone, timedelta
import uuid

from core.dependencies import get_session, get_current_user_claims, get_tenant_id
from core.schemas.onboarding_schemas import AssinanteRegisterRequest, ConviteCreateRequest, ConviteResponse
from core.services.onboarding_service import OnboardingService
from core.services.auth_service import AuthService
from core.schemas.auth_schemas import TokenResponse, UsuarioMeResponse
from core.models.tenant import Tenant
from core.models.auth import Usuario, TenantUsuario
from core.models.fazenda import Fazenda
from core.models.billing import AssinaturaTenant, Fatura, PlanoAssinatura
from core.utils.cpf_cnpj import validar_cpf_ou_cnpj, apenas_numeros
from pydantic import BaseModel, EmailStr, Field
from loguru import logger

router = APIRouter(prefix="/onboarding", tags=["SaaS — Onboarding & Equipe"])


class VerificarDocumentoResponse(BaseModel):
    """Resposta da verificação de disponibilidade de CPF/CNPJ."""
    disponivel: bool
    mensagem: str | None = None


@router.get(
    "/verificar-documento/{documento}",
    response_model=VerificarDocumentoResponse,
    summary="Verifica se um CPF/CNPJ já está cadastrado",
)
async def verificar_documento(documento: str, session: AsyncSession = Depends(get_session)):
    """
    Verifica se o CPF ou CNPJ informado já está cadastrado no sistema.
    Usado pelo frontend para validação em tempo real durante o cadastro.
    """
    # Validar formato
    if not validar_cpf_ou_cnpj(documento):
        return VerificarDocumentoResponse(
            disponivel=False,
            mensagem="CPF ou CNPJ inválido. Verifique os dados informados."
        )

    # Checar se já existe
    documento_limpo = apenas_numeros(documento)
    stmt = select(Tenant).where(Tenant.documento == documento_limpo)
    tenant_existente = (await session.execute(stmt)).scalars().first()

    if tenant_existente:
        return VerificarDocumentoResponse(
            disponivel=False,
            mensagem="Este CPF ou CNPJ já está cadastrado no sistema."
        )

    return VerificarDocumentoResponse(disponivel=True)


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

# ============================================================================
# ATIVAÇÃO DE CONTA — Fluxo pós-conversão de lead
# ============================================================================

class AtivarContaRequest(BaseModel):
    """Dados confirmados/corrigidos pelo assinante + senha definitiva."""
    nome_completo: str = Field(..., min_length=3)
    telefone: str | None = None
    senha: str = Field(..., min_length=6)


class AtivarContaInfoResponse(BaseModel):
    """Dados pré-preenchidos para o formulário de ativação."""
    nome_tenant: str
    email: str
    nome_completo: str
    telefone: str | None
    fazendas: list[str]
    plano_nome: str
    ciclo_pagamento: str


class AtivarContaCheckoutResponse(BaseModel):
    checkout_url: str
    message: str


@router.get(
    "/ativar/{token}",
    response_model=AtivarContaInfoResponse,
    summary="Valida token de ativação e retorna dados pré-preenchidos",
)
async def obter_dados_ativacao(token: str, session: AsyncSession = Depends(get_session)):
    """Valida o token enviado por email e retorna os dados para o formulário de ativação."""
    stmt = select(Tenant).where(Tenant.activation_token == token)
    result = await session.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Token de ativação inválido ou não encontrado")

    if tenant.activation_expires_at and tenant.activation_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Token de ativação expirado. Solicite um novo link ao suporte.")

    if tenant.ativo:
        raise HTTPException(status_code=409, detail="Esta conta já foi ativada.")

    # Buscar usuário owner
    stmt = select(Usuario).join(TenantUsuario, TenantUsuario.usuario_id == Usuario.id).where(
        TenantUsuario.tenant_id == tenant.id,
        TenantUsuario.is_owner == True,
    )
    result = await session.execute(stmt)
    usuario = result.scalar_one_or_none()

    # Buscar fazendas
    stmt = select(Fazenda).where(Fazenda.tenant_id == tenant.id)
    result = await session.execute(stmt)
    fazendas = result.scalars().all()

    # Buscar assinatura + plano
    stmt = select(AssinaturaTenant).where(
        AssinaturaTenant.tenant_id == tenant.id,
        AssinaturaTenant.tipo_assinatura == "PRINCIPAL",
    )
    result = await session.execute(stmt)
    assinatura = result.scalar_one_or_none()

    plano_nome = "N/A"
    if assinatura:
        from core.models.billing import PlanoAssinatura
        plano = await session.get(PlanoAssinatura, assinatura.plano_id)
        if plano:
            plano_nome = plano.nome

    return AtivarContaInfoResponse(
        nome_tenant=tenant.nome,
        email=usuario.email if usuario else tenant.email_responsavel or "",
        nome_completo=usuario.nome_completo if usuario else "",
        telefone=tenant.telefone_responsavel,
        fazendas=[f.nome for f in fazendas],
        plano_nome=plano_nome,
        ciclo_pagamento=assinatura.ciclo_pagamento if assinatura else "MENSAL",
    )


@router.post(
    "/ativar/{token}",
    response_model=AtivarContaCheckoutResponse,
    summary="Confirma dados, define senha e gera checkout Stripe",
)
async def ativar_conta(
    token: str,
    dados: AtivarContaRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Confirma os dados do assinante, define a senha definitiva
    e cria a sessão de checkout no Stripe para o primeiro pagamento.
    """
    stmt = select(Tenant).where(Tenant.activation_token == token)
    result = await session.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Token de ativação inválido")

    if tenant.activation_expires_at and tenant.activation_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Token expirado. Solicite um novo link ao suporte.")

    if tenant.ativo:
        raise HTTPException(status_code=409, detail="Conta já ativada.")

    # Buscar usuário owner
    stmt = select(Usuario).join(TenantUsuario, TenantUsuario.usuario_id == Usuario.id).where(
        TenantUsuario.tenant_id == tenant.id,
        TenantUsuario.is_owner == True,
    )
    result = await session.execute(stmt)
    usuario = result.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=500, detail="Usuário owner não encontrado")

    # Atualizar dados do usuário
    auth_service = AuthService(session)
    usuario.nome_completo = dados.nome_completo
    usuario.senha_hash = auth_service.get_password_hash(dados.senha)
    if dados.telefone:
        tenant.telefone_responsavel = dados.telefone

    # Buscar assinatura
    stmt = select(AssinaturaTenant).where(
        AssinaturaTenant.tenant_id == tenant.id,
        AssinaturaTenant.tipo_assinatura == "PRINCIPAL",
    )
    result = await session.execute(stmt)
    assinatura = result.scalar_one_or_none()

    if not assinatura:
        raise HTTPException(status_code=500, detail="Assinatura não encontrada")

    # Criar checkout Stripe
    from core.services.stripe_service import StripeService
    stripe_svc = StripeService()
    checkout_url = await stripe_svc.criar_checkout_assinatura(
        tenant_id=str(tenant.id),
        assinatura_id=str(assinatura.id),
        email=usuario.email,
        plano_id=str(assinatura.plano_id),
        ciclo=assinatura.ciclo_pagamento,
    )

    # Criar fatura ABERTA para que o webhook possa baixá-la ao confirmar pagamento
    fatura_existente = (await session.execute(
        select(Fatura).where(
            Fatura.assinatura_id == assinatura.id,
            Fatura.status == "ABERTA",
        )
    )).scalar_one_or_none()

    if not fatura_existente:
        plano = await session.get(PlanoAssinatura, assinatura.plano_id)
        valor = plano.preco_anual if assinatura.ciclo_pagamento == "ANUAL" else plano.preco_mensal
        vencimento = (datetime.now(timezone.utc) + timedelta(days=3)).date()
        nova_fatura = Fatura(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            assinatura_id=assinatura.id,
            valor=valor,
            data_vencimento=vencimento,
            status="ABERTA",
        )
        session.add(nova_fatura)
        logger.info(f"Fatura ABERTA criada para assinatura {assinatura.id} — R${valor}")

    await session.commit()

    logger.info(f"Onboarding iniciado para tenant {tenant.id} ({tenant.nome}) — checkout Stripe criado")

    return AtivarContaCheckoutResponse(
        checkout_url=checkout_url,
        message="Dados confirmados. Prossiga para o pagamento.",
    )


@router.get("/convites/{token}", summary="Verifica token e retorna detalhes do convite sem aceitá-lo ainda")
async def obter_detalhes_convite(
    token: str,
    session: AsyncSession = Depends(get_session)
):
    onboard_svc = OnboardingService(session)
    return await onboard_svc.obter_detalhes_convite(token)


class RegistrarViaConviteRequest(BaseModel):
    token: str
    senha: str = Field(..., min_length=8)
    nome_completo: str | None = Field(None, max_length=150)
    foto_perfil_url: str | None = None


@router.post("/convites/registrar", response_model=TokenResponse, summary="Cria conta a partir de convite (usuário novo)")
async def registrar_via_convite(
    dados: RegistrarViaConviteRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Cria um novo usuário com o e-mail do convite, define senha e foto,
    vincula ao tenant/fazenda/perfil do convite e retorna JWT pronto.
    Não requer autenticação prévia.
    """
    auth_svc = AuthService(session)
    onboard_svc = OnboardingService(session, auth_svc)

    novo_usuario = await onboard_svc.registrar_via_convite(
        token=dados.token,
        senha=dados.senha,
        nome_completo=dados.nome_completo,
        foto_perfil_url=dados.foto_perfil_url,
    )

    # Autentica imediatamente para retornar JWT
    from core.schemas.auth_schemas import LoginRequest
    login_data = LoginRequest(email=novo_usuario.email, senha=dados.senha)
    _, access_token = await auth_svc.authenticate_user(login_data)
    return TokenResponse(access_token=access_token)


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
