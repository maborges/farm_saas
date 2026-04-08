from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from core.dependencies import get_session, get_current_user_claims, get_current_user
from core.schemas.auth_schemas import LoginRequest, UserCreateRequest, UserUpdateRequest, TokenResponse, UsuarioMeResponse
from core.schemas.auth_schemas import (
    LoginDesbloqueioRequest, LoginDesbloqueioResponse,
    LoginTentativasInfoResponse
)
from core.schemas.auth_schemas import (
    ForgotPasswordRequest, ForgotPasswordResponse,
    VerifyResetTokenRequest, VerifyResetTokenResponse,
    ResetPasswordRequest, ResetPasswordResponse
)
from core.services.auth_service import AuthService
from core.services.login_rate_limit_service import LoginRateLimitService
from core.models.auth import Usuario, TenantUsuario, FazendaUsuario
from core.models.grupo_fazendas import GrupoFazendas, GrupoUsuario
from core.models.billing import AssinaturaTenant, PlanoAssinatura
from core.models.fazenda import Fazenda
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter(prefix="/auth", tags=["SaaS — Identity & Auth"])

# ==================== SCHEMAS ====================

class AssinaturaInfo(BaseModel):
    """Informações resumidas de uma assinatura/grupo para o frontend."""
    grupo_id: str
    grupo_nome: str
    plano_nome: str
    plano_tier: str
    status: str
    total_fazendas: int
    fazendas: List[dict]
    modulos: List[str]
    is_ativa: bool

class SwitchGrupoRequest(BaseModel):
    grupo_id: str = Field(..., description="ID do grupo de fazendas para ativar")

class SwitchGrupoResponse(BaseModel):
    access_token: str
    grupo_ativo: AssinaturaInfo

@router.post("/register", response_model=UsuarioMeResponse, status_code=status.HTTP_201_CREATED, summary="Registra um novo usuário global (Produtor/Gestor)")
async def register(dados: UserCreateRequest, session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    user = await svc.register_user(dados)
    return await svc.get_user_me(user.id)

@router.post("/login", response_model=TokenResponse, summary="Autentica e gera Token (Substitui o gen_token.py simulador)")
async def login(request: Request, dados: LoginRequest, session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    
    # Extrai IP e user agent para auditoria
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", None)
    
    user, token = await svc.authenticate_user(dados, ip_address=ip_address, user_agent=user_agent)
    return TokenResponse(access_token=token)

@router.get("/me", response_model=UsuarioMeResponse, summary="Retorna os dados do usuário global logado com suas contas (Tenants) conectadas")
async def get_me(claims: dict = Depends(get_current_user_claims), session: AsyncSession = Depends(get_session)):
    svc = AuthService(session)
    user_id = uuid.UUID(claims["sub"])
    return await svc.get_user_me(user_id)


@router.put("/me", response_model=UsuarioMeResponse, summary="Atualiza dados do perfil do usuário logado")
async def update_me(
    dados: UserUpdateRequest,
    claims: dict = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session),
):
    """Permite ao usuário atualizar nome, telefone e foto de perfil."""
    user_id = uuid.UUID(claims["sub"])
    result = await session.execute(select(Usuario).where(Usuario.id == user_id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if dados.nome_completo is not None:
        usuario.nome_completo = dados.nome_completo
    if dados.telefone is not None:
        usuario.telefone = dados.telefone
    if dados.foto_perfil_url is not None:
        usuario.foto_perfil_url = dados.foto_perfil_url

    await session.commit()
    await session.refresh(usuario)

    svc = AuthService(session)
    return await svc.get_user_me(user_id)


@router.post("/switch-tenant", response_model=TokenResponse, summary="Troca o contexto de tenant e gera novo JWT com grupos[]")
async def switch_tenant(
    request: Request,
    claims: dict = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session)
):
    """
    Gera um novo JWT com os grupos[] do tenant selecionado via header X-Tenant-Id.
    Usado pelo tenant-switcher no frontend.
    """
    target_tenant_id_str = request.headers.get("x-tenant-id")
    if not target_tenant_id_str:
        raise HTTPException(status_code=400, detail="Header X-Tenant-Id obrigatório")

    try:
        target_tenant_id = uuid.UUID(target_tenant_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="X-Tenant-Id inválido")

    user_id = uuid.UUID(claims["sub"])

    # Verifica que o usuário tem acesso ao tenant alvo
    result = await session.execute(
        select(TenantUsuario).where(
            TenantUsuario.tenant_id == target_tenant_id,
            TenantUsuario.usuario_id == user_id,
            TenantUsuario.status == "ATIVO"
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Sem acesso ao tenant selecionado")

    # Gera novo token com contexto do tenant alvo
    svc = AuthService(session)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    token = await svc.generate_token_for_tenant(user_id, target_tenant_id, ip_address, user_agent)
    return TokenResponse(access_token=token)


@router.get(
    "/minhas-assinaturas",
    response_model=List[AssinaturaInfo],
    summary="Lista todas as assinaturas (grupos) que o usuário tem acesso no tenant atual"
)
async def listar_minhas_assinaturas(
    claims: dict = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna todas as assinaturas/grupos que o usuário pode acessar no tenant atual.
    
    Usado pelo frontend para permitir alternar entre diferentes assinaturas
    (grupos de fazendas) do mesmo tenant.
    """
    user_id = uuid.UUID(claims["sub"])
    tenant_id = uuid.UUID(claims["tenant_id"])

    # Buscar todos os grupos que o usuário tem acesso
    stmt_grupos = (
        select(GrupoFazendas, GrupoUsuario.perfil_id)
        .join(GrupoUsuario, GrupoUsuario.grupo_id == GrupoFazendas.id)
        .where(
            GrupoFazendas.tenant_id == tenant_id,
            GrupoFazendas.ativo == True,
            GrupoUsuario.user_id == user_id
        )
        .order_by(GrupoFazendas.ordem, GrupoFazendas.nome)
    )
    result_grupos = await session.execute(stmt_grupos)
    grupos_rows = result_grupos.all()

    assinaturas = []
    for grupo, perfil_id in grupos_rows:
        # Buscar assinatura do grupo
        stmt_assinatura = (
            select(AssinaturaTenant, PlanoAssinatura)
            .join(PlanoAssinatura, AssinaturaTenant.plano_id == PlanoAssinatura.id)
            .where(
                AssinaturaTenant.grupo_fazendas_id == grupo.id,
                AssinaturaTenant.tenant_id == tenant_id,
                AssinaturaTenant.tipo_assinatura == "GRUPO",
            )
            .limit(1)
        )
        result_ass = await session.execute(stmt_assinatura)
        row_ass = result_ass.first()

        # Buscar fazendas do grupo
        stmt_fazendas = select(FazendaUsuario.fazenda_id, Fazenda.nome).join(
            Fazenda, Fazenda.id == FazendaUsuario.fazenda_id
        ).where(
            Fazenda.grupo_id == grupo.id,
            Fazenda.tenant_id == tenant_id,
            Fazenda.ativo == True
        )
        result_faz = await session.execute(stmt_fazendas)
        fazendas_rows = result_faz.all()

        # Se não tem fazendas via FazendaUsuario, buscar todas as fazendas do grupo
        if not fazendas_rows:
            stmt_fazendas_all = select(Fazenda.id, Fazenda.nome).where(
                Fazenda.grupo_id == grupo.id,
                Fazenda.tenant_id == tenant_id,
                Fazenda.ativo == True
            )
            result_faz_all = await session.execute(stmt_fazendas_all)
            fazendas_rows = result_faz_all.all()

        fazendas_list = [{"id": str(f[0]), "nome": f[1]} for f in fazendas_rows]

        if row_ass:
            assinatura, plano = row_ass
            assinaturas.append(AssinaturaInfo(
                grupo_id=str(grupo.id),
                grupo_nome=grupo.nome,
                plano_nome=plano.nome,
                plano_tier=plano.plan_tier,
                status=assinatura.status,
                total_fazendas=len(fazendas_list),
                fazendas=fazendas_list,
                modulos=plano.modulos_inclusos,
                is_ativa=assinatura.status == "ATIVA"
            ))
        else:
            # Grupo sem assinatura (pode ser grupo livre ou em trial)
            assinaturas.append(AssinaturaInfo(
                grupo_id=str(grupo.id),
                grupo_nome=grupo.nome,
                plano_nome="Sem assinatura",
                plano_tier="BASICO",
                status="PENDENTE",
                total_fazendas=len(fazendas_list),
                fazendas=fazendas_list,
                modulos=["CORE"],
                is_ativa=False
            ))

    return assinaturas


@router.post(
    "/switch-grupo",
    response_model=SwitchGrupoResponse,
    summary="Alterna o contexto para outro grupo de fazendas (assinatura)"
)
async def switch_grupo(
    data: SwitchGrupoRequest,
    request: Request,
    claims: dict = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session)
):
    """
    Gera um novo JWT com o grupo de fazendas selecionado como contexto ativo.
    
    Permite que um usuário alterne entre diferentes assinaturas (grupos)
    do mesmo tenant sem precisar fazer logout/login.
    """
    user_id = uuid.UUID(claims["sub"])
    tenant_id = uuid.UUID(claims["tenant_id"])

    try:
        grupo_id = uuid.UUID(data.grupo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID do grupo inválido")

    # Verifica que o usuário tem acesso ao grupo
    result_grupo = await session.execute(
        select(GrupoUsuario).where(
            GrupoUsuario.grupo_id == grupo_id,
            GrupoUsuario.user_id == user_id,
            GrupoUsuario.tenant_id == tenant_id
        )
    )
    if not result_grupo.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Sem acesso ao grupo selecionado")

    # Verifica que o grupo está ativo
    grupo = await session.get(GrupoFazendas, grupo_id)
    if not grupo or not grupo.ativo or grupo.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Grupo não encontrado ou inativo")

    # Gera novo token com contexto do grupo alvo
    svc = AuthService(session)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    token = await svc.generate_token_for_grupo(user_id, tenant_id, grupo_id, ip_address, user_agent)

    # Buscar informações do grupo ativo para retornar
    stmt_assinatura = (
        select(AssinaturaTenant, PlanoAssinatura)
        .join(PlanoAssinatura, AssinaturaTenant.plano_id == PlanoAssinatura.id)
        .where(
            AssinaturaTenant.grupo_fazendas_id == grupo_id,
            AssinaturaTenant.tenant_id == tenant_id,
            AssinaturaTenant.tipo_assinatura == "GRUPO",
        )
        .limit(1)
    )
    result_ass = await session.execute(stmt_assinatura)
    row_ass = result_ass.first()

    stmt_fazendas = select(Fazenda.id, Fazenda.nome).where(
        Fazenda.grupo_id == grupo_id,
        Fazenda.tenant_id == tenant_id,
        Fazenda.ativo == True
    )
    result_faz = await session.execute(stmt_fazendas)
    fazendas_rows = result_faz.all()
    fazendas_list = [{"id": str(f[0]), "nome": f[1]} for f in fazendas_rows]

    if row_ass:
        assinatura, plano = row_ass
        grupo_ativo = AssinaturaInfo(
            grupo_id=str(grupo_id),
            grupo_nome=grupo.nome,
            plano_nome=plano.nome,
            plano_tier=plano.plan_tier,
            status=assinatura.status,
            total_fazendas=len(fazendas_list),
            fazendas=fazendas_list,
            modulos=plano.modulos_inclusos,
            is_ativa=assinatura.status == "ATIVA"
        )
    else:
        grupo_ativo = AssinaturaInfo(
            grupo_id=str(grupo_id),
            grupo_nome=grupo.nome,
            plano_nome="Sem assinatura",
            plano_tier="BASICO",
            status="PENDENTE",
            total_fazendas=len(fazendas_list),
            fazendas=fazendas_list,
            modulos=["CORE"],
            is_ativa=False
        )

    return SwitchGrupoResponse(access_token=token, grupo_ativo=grupo_ativo)


# ==================== GESTOR DE TENANT - DESBLOQUEIO DE USUÁRIOS ====================

@router.post("/tenant/usuarios/{usuario_id}/desbloquear-login", summary="Gestor desbloqueia login de usuário do tenant")
async def gestor_desbloquear_usuario(
    usuario_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    claims: dict = Depends(get_current_user_claims)
):
    """
    Gestor do Tenant: Desbloqueia login de usuário do seu tenant.
    
    Apenas usuários com perfil de gestor/admin do tenant podem desbloquear
    outros usuários do mesmo tenant.
    
    Útil quando:
    - Funcionário esquece senha e tenta várias vezes
    - Bloqueio acidental por erro de digitação
    - Retorno de férias/afastamento
    """
    tenant_id = claims.get("tenant_id")
    user_claims_id = claims.get("sub")
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não está vinculado a nenhum tenant"
        )
    
    # Verifica se o usuário atual tem permissão de gestor no tenant
    stmt = select(TenantUsuario).where(
        TenantUsuario.usuario_id == uuid.UUID(user_claims_id),
        TenantUsuario.tenant_id == uuid.UUID(tenant_id),
        TenantUsuario.status == "ATIVO"
    )
    result = await session.execute(stmt)
    tenant_usuario = result.scalar_one_or_none()
    
    if not tenant_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não tem acesso a este tenant"
        )
    
    # Verifica se é owner ou admin (perfil com permissão de gerenciar usuários)
    # Owner sempre pode, outros perfis precisam verificar permissões
    if not tenant_usuario.is_owner:
        # Verifica se tem permissão de admin no perfil
        if tenant_usuario.perfil_id:
            from core.models.auth import PerfilAcesso
            perfil_stmt = select(PerfilAcesso).where(PerfilAcesso.id == tenant_usuario.perfil_id)
            perfil_result = await session.execute(perfil_stmt)
            perfil = perfil_result.scalar_one_or_none()
            
            # Verifica se tem permissão de escrever em usuários
            permissoes = perfil.permissoes if perfil else {}
            pode_gerenciar_usuarios = (
                permissoes.get("core", {}).get("usuarios") == "write" or
                permissoes.get("backoffice") == "write" or
                perfil.nome.lower() in ["administrador", "admin", "owner", "gestor"]
            )
            
            if not pode_gerenciar_usuarios:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuário não tem permissão para desbloquear outros usuários"
                )
    
    # Verifica se o usuário a ser desbloqueado pertence ao mesmo tenant
    stmt_usuario_alvo = select(Usuario).where(Usuario.id == usuario_id)
    result_usuario = await session.execute(stmt_usuario_alvo)
    usuario_alvo = result_usuario.scalar_one_or_none()
    
    if not usuario_alvo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verifica se o usuário alvo está no mesmo tenant
    stmt_vinculo = select(TenantUsuario).where(
        TenantUsuario.usuario_id == usuario_id,
        TenantUsuario.tenant_id == uuid.UUID(tenant_id)
    )
    result_vinculo = await session.execute(stmt_vinculo)
    vinculo = result_vinculo.scalar_one_or_none()
    
    if not vinculo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não pertence a este tenant"
        )
    
    # Desbloqueia o login
    rate_limit_svc = LoginRateLimitService(session)
    desbloqueado = await rate_limit_svc.desbloquear_por_usuario_id(usuario_id)
    
    if not desbloqueado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum registro de bloqueio encontrado para este usuário"
        )
    
    return LoginDesbloqueioResponse(
        sucesso=True,
        mensagem=f"Usuário {usuario_alvo.email} desbloqueado com sucesso",
        email=usuario_alvo.email
    )


@router.get("/tenant/usuarios/{usuario_id}/login-tentativas", summary="Gestor vê tentativas de login de usuário do tenant")
async def gestor_ver_tentativas_usuario(
    usuario_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    claims: dict = Depends(get_current_user_claims)
):
    """
    Gestor do Tenant: Visualiza tentativas de login de um usuário do tenant.
    
    Retorna informações sobre bloqueio e contador de tentativas.
    """
    tenant_id = claims.get("tenant_id")
    user_claims_id = claims.get("sub")
    
    # Verifica permissões (mesma lógica do desbloqueio)
    stmt = select(TenantUsuario).where(
        TenantUsuario.usuario_id == uuid.UUID(user_claims_id),
        TenantUsuario.tenant_id == uuid.UUID(tenant_id),
        TenantUsuario.status == "ATIVO"
    )
    result = await session.execute(stmt)
    tenant_usuario = result.scalar_one_or_none()
    
    if not tenant_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não tem acesso a este tenant"
        )
    
    # Verifica se o usuário alvo pertence ao tenant
    stmt_vinculo = select(TenantUsuario).where(
        TenantUsuario.usuario_id == usuario_id,
        TenantUsuario.tenant_id == uuid.UUID(tenant_id)
    )
    result_vinculo = await session.execute(stmt_vinculo)
    vinculo = result_vinculo.scalar_one_or_none()
    
    if not vinculo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não pertence a este tenant"
        )
    
    # Busca informações do usuário
    stmt_usuario = select(Usuario).where(Usuario.id == usuario_id)
    result_usuario = await session.execute(stmt_usuario)
    usuario = result_usuario.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    rate_limit_svc = LoginRateLimitService(session)
    info = await rate_limit_svc.get_tentativas_por_email(usuario.email)
    
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhum registro de tentativas para {usuario.email}"
        )
    
    return LoginTentativasInfoResponse(**info)


# ==================== RECUPERAÇÃO DE SENHA ====================

@router.post("/forgot-password", response_model=ForgotPasswordResponse, summary="Solicita recuperação de senha por e-mail")
async def forgot_password(
    dados: ForgotPasswordRequest,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """
    Solicita recuperação de senha por e-mail com token expirável (1 hora).
    
    - Gera um token único e seguro
    - Envia e-mail com link de recuperação
    - Invalida tokens anteriores do mesmo usuário
    - Retorna mensagem genérica para evitar enumeração de usuários
    """
    svc = AuthService(session)
    
    # Extrai IP para auditoria
    ip_address = request.client.host if request.client else None
    
    resultado = await svc.create_password_reset_token(
        email=dados.email,
        ip_address=ip_address
    )
    
    return ForgotPasswordResponse(
        sucesso=resultado["sucesso"],
        mensagem=resultado["mensagem"],
        email=resultado.get("email")
    )


@router.post("/verify-reset-token", response_model=VerifyResetTokenResponse, summary="Verifica token de recuperação de senha")
async def verify_reset_token(
    dados: VerifyResetTokenRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Verifica se um token de recuperação de senha é válido.
    
    - Verifica se o token existe e não foi utilizado
    - Verifica se não expirou (1 hora)
    - Retorna informações sobre o token
    """
    svc = AuthService(session)
    resultado = await svc.verify_reset_token(token=dados.token)
    
    return VerifyResetTokenResponse(
        valido=resultado["valido"],
        mensagem=resultado["mensagem"],
        email=resultado.get("email"),
        expira_em=resultado.get("expira_em")
    )


@router.post("/reset-password", response_model=ResetPasswordResponse, summary="Redefine senha com token de recuperação")
async def reset_password(
    dados: ResetPasswordRequest,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """
    Redefine a senha do usuário usando um token de recuperação válido.
    
    - Verifica validade do token
    - Verifica se token não expirou
    - Valida confirmação de senha
    - Atualiza senha e invalida o token
    """
    # Verifica se as senhas coincidem
    if not dados.senhas_coincidem:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="As senhas não coincidem."
        )
    
    svc = AuthService(session)
    
    # Extrai IP para auditoria
    ip_address = request.client.host if request.client else None
    
    resultado = await svc.reset_password(
        token=dados.token,
        nova_senha=dados.nova_senha,
        ip_address=ip_address
    )
    
    return ResetPasswordResponse(
        sucesso=resultado["sucesso"],
        mensagem=resultado["mensagem"]
    )
