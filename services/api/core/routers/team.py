"""
Router para gestão de equipe do tenant (usuários e permissões).

Endpoints:
- GET    /team/users              - Listar usuários da equipe
- POST   /team/invite             - Convidar novo membro
- PATCH  /team/users/{id}/role    - Alterar perfil
- PATCH  /team/users/{id}/fazendas - Configurar fazendas
- DELETE /team/users/{id}         - Remover membro
- GET    /team/invites            - Listar convites pendentes
- POST   /team/invites/{id}/resend - Reenviar convite
- DELETE /team/invites/{id}       - Cancelar convite
- GET    /team/roles              - Listar perfis disponíveis (sistema + customizados do tenant)
- POST   /team/roles              - Criar perfil customizado
- GET    /team/roles/{id}         - Detalhar perfil
- PATCH  /team/roles/{id}         - Editar perfil customizado (somente próprios)
- DELETE /team/roles/{id}         - Remover perfil customizado (somente próprios, se não estiver em uso)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List
import uuid
from datetime import datetime, timezone, timedelta
import secrets

from core.dependencies import (
    get_session,
    get_tenant_id,
    get_current_user,
    require_tenant_permission,
    require_limit  # ← Adicionado para validação de limites
)
from core.models.auth import (
    Usuario,
    TenantUsuario,
    FazendaUsuario,
    PerfilAcesso,
    ConviteAcesso
)
from core.models.fazenda import Fazenda
from core.models.tenant import Tenant
from core.constants import TenantRoles, TenantPermissions
from core.services.email_service import email_service
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(prefix="/team", tags=["Team Management"])

# ==================== SCHEMAS ====================

class FazendaSimple(BaseModel):
    id: str
    nome: str

class PerfilResponse(BaseModel):
    id: uuid.UUID | str
    nome: str
    is_custom: bool
    descricao: str | None = None
    permissoes: dict | None = None

    class Config:
        from_attributes = True

class TeamMemberResponse(BaseModel):
    id: str
    usuario_id: str
    nome: str | None
    email: str
    perfil: PerfilResponse | None
    is_owner: bool
    status: str
    fazendas: List[FazendaSimple]
    fazendas_com_perfil_especifico: List[dict]  # [{fazenda_id, fazenda_nome, perfil_id, perfil_nome}]
    data_cadastro: datetime

class TeamStatsResponse(BaseModel):
    total_membros: int
    ativos: int
    owners: int
    convites_pendentes: int

class InviteCreateRequest(BaseModel):
    email: EmailStr
    perfil_id: str
    fazendas_ids: List[str] = Field(default_factory=list, description="IDs das fazendas (vazio = todas)")
    data_validade_acesso: str | None = Field(None, description="YYYY-MM-DD para acesso temporário")

class InviteResponse(BaseModel):
    id: str
    email_convidado: str
    perfil: PerfilResponse
    fazendas: List[FazendaSimple]
    status: str
    data_expiracao: datetime
    data_validade_acesso: str | None
    created_at: datetime

class UpdateRoleRequest(BaseModel):
    perfil_id: str

class UpdateFazendasRequest(BaseModel):
    fazendas_ids: List[str]
    perfis_por_fazenda: dict[str, str] = Field(
        default_factory=dict,
        description="Mapa {fazenda_id: perfil_id} para perfis específicos por fazenda"
    )

class CreateCustomRoleRequest(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    descricao: str | None = Field(None, max_length=500)
    permissoes: dict = Field(
        ...,
        description='{"granted": ["agricola:operacoes:view", "financeiro:*", "agricola:relatorios:export"]}'
    )

    def permissoes_validas(self) -> bool:
        """Valida que o formato é {"granted": [...]} com strings."""
        granted = self.permissoes.get("granted")
        if granted is None:
            return False
        return isinstance(granted, list) and all(isinstance(p, str) for p in granted)


class UpdateCustomRoleRequest(BaseModel):
    nome: str | None = Field(None, min_length=3, max_length=100)
    descricao: str | None = Field(None, max_length=500)
    permissoes: dict | None = Field(
        None,
        description='{"granted": ["agricola:operacoes:view", "financeiro:*"]}'
    )

    def permissoes_validas(self) -> bool:
        if self.permissoes is None:
            return True
        granted = self.permissoes.get("granted")
        if granted is None:
            return False
        return isinstance(granted, list) and all(isinstance(p, str) for p in granted)


class CloneRoleRequest(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    descricao: str | None = Field(None, max_length=500)

# ==================== ENDPOINTS ====================

@router.get("/stats", response_model=TeamStatsResponse, dependencies=[Depends(require_tenant_permission("tenant:users:view"))])
async def get_team_stats(
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Estatísticas da equipe."""

    total = await session.scalar(
        select(func.count(TenantUsuario.id)).where(TenantUsuario.tenant_id == tenant_id)
    )

    ativos = await session.scalar(
        select(func.count(TenantUsuario.id)).where(
            and_(
                TenantUsuario.tenant_id == tenant_id,
                TenantUsuario.status == "ATIVO"
            )
        )
    )

    owners = await session.scalar(
        select(func.count(TenantUsuario.id)).where(
            and_(
                TenantUsuario.tenant_id == tenant_id,
                TenantUsuario.is_owner == True
            )
        )
    )

    convites = await session.scalar(
        select(func.count(ConviteAcesso.id)).where(
            and_(
                ConviteAcesso.tenant_id == tenant_id,
                ConviteAcesso.status == "PENDENTE"
            )
        )
    )

    return TeamStatsResponse(
        total_membros=total or 0,
        ativos=ativos or 0,
        owners=owners or 0,
        convites_pendentes=convites or 0
    )


@router.get("/users", response_model=List[TeamMemberResponse], dependencies=[Depends(require_tenant_permission("tenant:users:view"))])
async def list_team_members(
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Lista todos os membros da equipe do tenant."""

    # Buscar TenantUsuarios com joins
    stmt = (
        select(TenantUsuario, Usuario, PerfilAcesso)
        .join(Usuario, TenantUsuario.usuario_id == Usuario.id)
        .outerjoin(PerfilAcesso, TenantUsuario.perfil_id == PerfilAcesso.id)
        .where(TenantUsuario.tenant_id == tenant_id)
        .order_by(TenantUsuario.is_owner.desc(), Usuario.nome_completo)
    )

    result = await session.execute(stmt)
    rows = result.all()

    members = []
    for tenant_usuario, usuario, perfil_acesso in rows:
        # Buscar fazendas do usuário
        stmt_fazendas = (
            select(Fazenda, FazendaUsuario)
            .join(FazendaUsuario, Fazenda.id == FazendaUsuario.fazenda_id)
            .where(
                and_(
                    FazendaUsuario.tenant_id == tenant_id,
                    FazendaUsuario.usuario_id == usuario.id
                )
            )
        )
        result_fazendas = await session.execute(stmt_fazendas)
        fazendas_rows = result_fazendas.all()

        fazendas_simple = []
        fazendas_com_perfil = []

        for fazenda, fazenda_usuario in fazendas_rows:
            fazendas_simple.append(FazendaSimple(id=str(fazenda.id), nome=fazenda.nome))

            # Se tem perfil específico nesta fazenda
            if fazenda_usuario.perfil_fazenda_id:
                perfil_faz = await session.get(PerfilAcesso, fazenda_usuario.perfil_fazenda_id)
                if perfil_faz:
                    fazendas_com_perfil.append({
                        "fazenda_id": str(fazenda.id),
                        "fazenda_nome": fazenda.nome,
                        "perfil_id": str(perfil_faz.id),
                        "perfil_nome": perfil_faz.nome
                    })

        members.append(TeamMemberResponse(
            id=str(tenant_usuario.id),
            usuario_id=str(usuario.id),
            nome=usuario.nome_completo,
            email=usuario.email,
            perfil=PerfilResponse(
                id=str(perfil_acesso.id),
                nome=perfil_acesso.nome,
                is_custom=perfil_acesso.is_custom,
                descricao=perfil_acesso.descricao,
                permissoes=perfil_acesso.permissoes
            ) if perfil_acesso else None,
            is_owner=tenant_usuario.is_owner,
            status=tenant_usuario.status,
            fazendas=fazendas_simple,
            fazendas_com_perfil_especifico=fazendas_com_perfil,
            data_cadastro=tenant_usuario.created_at
        ))

    return members


@router.post(
    "/invite",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_tenant_permission("tenant:users:invite")),
        Depends(require_limit("max_usuarios")),  # ← Valida limite de usuários!
    ],
)
async def invite_team_member(
    data: InviteCreateRequest,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Convida um novo membro para a equipe — bloqueado se limite de usuários atingido."""

    # Verificar se perfil existe
    try:
        perfil_uuid = uuid.UUID(data.perfil_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="perfil_id inválido")

    perfil = await session.get(PerfilAcesso, perfil_uuid)
    if not perfil:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado")

    # Verificar se já existe usuário com este email no tenant
    stmt = (
        select(TenantUsuario)
        .join(Usuario, TenantUsuario.usuario_id == Usuario.id)
        .where(
            and_(
                TenantUsuario.tenant_id == tenant_id,
                Usuario.email == data.email
            )
        )
    )
    existing = await session.scalar(stmt)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já faz parte da equipe"
        )

    # Verificar se já existe convite pendente
    stmt_convite = (
        select(ConviteAcesso).where(
            and_(
                ConviteAcesso.tenant_id == tenant_id,
                ConviteAcesso.email_convidado == data.email,
                ConviteAcesso.status == "PENDENTE"
            )
        )
    )
    existing_invite = await session.scalar(stmt_convite)
    if existing_invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um convite pendente para este email"
        )

    # Criar convite
    token = secrets.token_urlsafe(32)
    expiracao = datetime.now(timezone.utc) + timedelta(days=7)

    convite = ConviteAcesso(
        tenant_id=tenant_id,
        email_convidado=data.email,
        perfil_id=perfil_uuid,
        fazendas_ids=data.fazendas_ids,
        token_convite=token,
        status="PENDENTE",
        data_expiracao=expiracao,
        data_validade_acesso=datetime.strptime(data.data_validade_acesso, "%Y-%m-%d").date() if data.data_validade_acesso else None
    )

    session.add(convite)
    await session.commit()
    await session.refresh(convite)

    tenant = await session.get(Tenant, tenant_id)
    remetente = current_user.nome_completo or current_user.username
    await email_service.send_invite(
        email=data.email,
        remetente=remetente,
        tenant_nome=tenant.nome if tenant else "",
        perfil_nome=perfil.nome,
        token=token,
        tenant_id=tenant_id,
    )

    return {"message": "Convite enviado com sucesso", "convite_id": str(convite.id), "token": token}


@router.get("/invites", response_model=List[InviteResponse], dependencies=[Depends(require_tenant_permission("tenant:users:view"))])
async def list_pending_invites(
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Lista convites pendentes."""

    stmt = (
        select(ConviteAcesso, PerfilAcesso)
        .join(PerfilAcesso, ConviteAcesso.perfil_id == PerfilAcesso.id)
        .where(
            and_(
                ConviteAcesso.tenant_id == tenant_id,
                ConviteAcesso.status == "PENDENTE"
            )
        )
        .order_by(ConviteAcesso.created_at.desc())
    )

    result = await session.execute(stmt)
    rows = result.all()

    invites = []
    for convite, perfil in rows:
        # Buscar fazendas
        fazendas = []
        if convite.fazendas_ids:
            for faz_id in convite.fazendas_ids:
                try:
                    faz_uuid = uuid.UUID(faz_id)
                    faz = await session.get(Fazenda, faz_uuid)
                    if faz:
                        fazendas.append(FazendaSimple(id=str(faz.id), nome=faz.nome))
                except ValueError:
                    pass

        invites.append(InviteResponse(
            id=str(convite.id),
            email_convidado=convite.email_convidado,
            perfil=PerfilResponse(
                id=str(perfil.id),
                nome=perfil.nome,
                is_custom=perfil.is_custom,
                descricao=perfil.descricao,
                permissoes=perfil.permissoes
            ),
            fazendas=fazendas,
            status=convite.status,
            data_expiracao=convite.data_expiracao,
            data_validade_acesso=str(convite.data_validade_acesso) if convite.data_validade_acesso else None,
            created_at=convite.created_at
        ))

    return invites


@router.patch("/users/{tenant_usuario_id}/role", dependencies=[Depends(require_tenant_permission("tenant:users:update"))])
async def update_member_role(
    tenant_usuario_id: str,
    data: UpdateRoleRequest,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Atualiza o perfil de um membro da equipe."""

    try:
        tu_uuid = uuid.UUID(tenant_usuario_id)
        perfil_uuid = uuid.UUID(data.perfil_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    # Buscar TenantUsuario
    tenant_usuario = await session.get(TenantUsuario, tu_uuid)
    if not tenant_usuario or tenant_usuario.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membro não encontrado")

    # Não permitir alterar perfil do owner
    if tenant_usuario.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível alterar o perfil do proprietário"
        )

    # Verificar se perfil existe
    perfil = await session.get(PerfilAcesso, perfil_uuid)
    if not perfil:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado")

    # Atualizar
    tenant_usuario.perfil_id = perfil_uuid
    await session.commit()

    return {"message": "Perfil atualizado com sucesso"}


@router.delete("/users/{tenant_usuario_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_tenant_permission("tenant:users:delete"))])
async def remove_team_member(
    tenant_usuario_id: str,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Remove um membro da equipe."""

    try:
        tu_uuid = uuid.UUID(tenant_usuario_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    tenant_usuario = await session.get(TenantUsuario, tu_uuid)
    if not tenant_usuario or tenant_usuario.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membro não encontrado")

    # Não permitir remover owner
    if tenant_usuario.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível remover o proprietário"
        )

    await session.delete(tenant_usuario)
    await session.commit()


@router.delete("/invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_tenant_permission("tenant:users:invite"))])
async def cancel_invite(
    invite_id: str,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Cancela um convite pendente."""
    try:
        inv_uuid = uuid.UUID(invite_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    convite = await session.get(ConviteAcesso, inv_uuid)
    if not convite or convite.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convite não encontrado")

    if convite.status != "PENDENTE":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Convite não está pendente")

    convite.status = "CANCELADO"
    await session.commit()


@router.post("/invites/{invite_id}/resend", dependencies=[Depends(require_tenant_permission("tenant:users:invite"))])
async def resend_invite(
    invite_id: str,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Reenvia um convite pendente, renovando o token e a data de expiração."""
    try:
        inv_uuid = uuid.UUID(invite_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    convite = await session.get(ConviteAcesso, inv_uuid)
    if not convite or convite.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convite não encontrado")

    if convite.status not in ["PENDENTE", "EXPIRADO"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Não é possível reenviar um convite com status {convite.status}"
        )

    # Renovar dados
    convite.token_convite = secrets.token_urlsafe(32)
    convite.data_expiracao = datetime.now(timezone.utc) + timedelta(days=7)
    convite.status = "PENDENTE"  # Garante que volta a ser pendente se estava expirado
    await session.commit()

    # Enviar e-mail (Seguindo o padrão do envio de convite que funciona)
    try:
        tenant = await session.get(Tenant, tenant_id)
        perfil = await session.get(PerfilAcesso, convite.perfil_id)
        remetente = current_user.nome_completo or current_user.username
        
        await email_service.send_invite(
            email=convite.email_convidado,
            remetente=remetente,
            tenant_nome=tenant.nome if tenant else "AgroSaaS",
            perfil_nome=perfil.nome if perfil else "Membro",
            token=convite.token_convite,
            tenant_id=tenant_id,
        )
    except Exception as e:
        from loguru import logger
        logger.error(f"Erro ao disparar e-mail de reenvio: {e}")
        # Retornamos sucesso no banco mas avisamos da falha no e-mail
        return {"message": "Convite renovado, mas o envio do e-mail falhou (Verifique seu SMTP)."}

    return {"message": "Convite reenviado com sucesso!"}


@router.get("/roles", response_model=List[PerfilResponse], dependencies=[Depends(require_tenant_permission("tenant:permissions:view"))])
async def list_available_roles(
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Lista perfis disponíveis (padrão do sistema + customizados do tenant)."""

    stmt = (
        select(PerfilAcesso)
        .where(
            (PerfilAcesso.tenant_id == None) |  # Perfis globais
            (PerfilAcesso.tenant_id == tenant_id)  # Perfis customizados deste tenant
        )
        .order_by(PerfilAcesso.is_custom, PerfilAcesso.nome)
    )

    result = await session.execute(stmt)
    perfis = result.scalars().all()

    return [
        PerfilResponse(
            id=str(p.id),
            nome=p.nome,
            is_custom=p.is_custom,
            descricao=TenantRoles.DESCRIPTIONS.get(p.nome.lower(), None) if not p.is_custom else None
        )
        for p in perfis
    ]


@router.post("/roles", response_model=PerfilResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_tenant_permission("tenant:permissions:create"))])
async def create_custom_role(
    data: CreateCustomRoleRequest,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Cria um perfil customizado para o tenant."""

    # Validar formato granular {"granted": [...]}
    if not data.permissoes_validas():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Formato inválido. Use: {"granted": ["modulo:recurso:acao", "financeiro:*"]}'
        )

    # Verificar nome duplicado para este tenant
    existing = await session.execute(
        select(PerfilAcesso).where(
            PerfilAcesso.tenant_id == tenant_id,
            PerfilAcesso.nome == data.nome
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe um perfil com o nome '{data.nome}'"
        )

    perfil = PerfilAcesso(
        tenant_id=tenant_id,
        nome=data.nome,
        descricao=data.descricao,
        is_custom=True,
        permissoes=data.permissoes
    )

    session.add(perfil)
    await session.commit()
    await session.refresh(perfil)

    return PerfilResponse(
        id=str(perfil.id),
        nome=perfil.nome,
        is_custom=perfil.is_custom,
        descricao=perfil.descricao,
        permissoes=perfil.permissoes
    )


# ==================== HELPERS INTERNOS ====================

VALID_PERMISSION_LEVELS = ["write", "read", "none", "*"]


async def _get_tenant_custom_role_or_404(
    role_id: str,
    tenant_id: uuid.UUID,
    session: AsyncSession
) -> PerfilAcesso:
    """Busca perfil customizado garantindo que pertence ao tenant solicitante."""
    try:
        rid = uuid.UUID(role_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    perfil = await session.get(PerfilAcesso, rid)

    if not perfil:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado")

    # Perfil padrão do sistema: tenant pode ver, mas não editar/deletar
    if perfil.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Perfis padrão do sistema não podem ser modificados pelo tenant"
        )

    # Isolamento de tenant: garante que o perfil pertence ao tenant solicitante
    if perfil.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado")

    return perfil


# ==================== ENDPOINTS DE PERFIL (CRUD COMPLETO) ====================

@router.get("/roles/{role_id}", response_model=PerfilResponse, dependencies=[Depends(require_tenant_permission("tenant:permissions:view"))])
async def get_role(
    role_id: str,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Detalha um perfil (padrão do sistema ou customizado do tenant).
    Perfis padrão são visíveis, mas apenas customizados do próprio tenant são editáveis.
    """
    try:
        rid = uuid.UUID(role_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    perfil = await session.get(PerfilAcesso, rid)
    if not perfil:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado")

    # Somente pode acessar perfis globais ou do próprio tenant
    if perfil.tenant_id is not None and perfil.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado")

    descricao = perfil.descricao
    if not descricao and not perfil.is_custom:
        descricao = TenantRoles.DESCRIPTIONS.get(perfil.nome.lower())

    return PerfilResponse(
        id=str(perfil.id),
        nome=perfil.nome,
        is_custom=perfil.is_custom,
        descricao=descricao,
        permissoes=perfil.permissoes or {}
    )


@router.post("/roles/{role_id}/clone", response_model=PerfilResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_tenant_permission("tenant:permissions:create"))])
async def clone_role(
    role_id: str,
    data: CloneRoleRequest,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Clona um perfil (padrão do sistema ou customizado) criando uma cópia editável para o tenant.
    Útil para partir de um perfil padrão (ex: Auditor) e ajustar as permissões.
    """
    try:
        rid = uuid.UUID(role_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    origem = await session.get(PerfilAcesso, rid)
    if not origem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil de origem não encontrado")

    # Somente pode clonar perfis globais ou do próprio tenant
    if origem.tenant_id is not None and origem.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado")

    # Verificar nome duplicado
    existing = await session.execute(
        select(PerfilAcesso).where(PerfilAcesso.tenant_id == tenant_id, PerfilAcesso.nome == data.nome)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Já existe um perfil com o nome '{data.nome}'")

    # Converter permissoes para formato granular ao clonar perfil de sistema
    permissoes_origem = origem.permissoes or {}
    permissions_list = permissoes_origem.get("permissions") or permissoes_origem.get("granted")
    permissoes_clone = {"granted": permissions_list} if permissions_list else permissoes_origem

    clone = PerfilAcesso(
        tenant_id=tenant_id,
        nome=data.nome,
        descricao=data.descricao or f"Baseado em: {origem.nome}",
        is_custom=True,
        permissoes=permissoes_clone,
    )

    session.add(clone)
    await session.commit()
    await session.refresh(clone)

    return PerfilResponse(
        id=str(clone.id),
        nome=clone.nome,
        is_custom=clone.is_custom,
        descricao=clone.descricao,
        permissoes=clone.permissoes,
    )


@router.patch("/roles/{role_id}", response_model=PerfilResponse, dependencies=[Depends(require_tenant_permission("tenant:permissions:update"))])
async def update_custom_role(
    role_id: str,
    data: UpdateCustomRoleRequest,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Edita um perfil customizado do tenant.
    Somente perfis com is_custom=True e tenant_id do próprio tenant podem ser alterados.
    """
    perfil = await _get_tenant_custom_role_or_404(role_id, tenant_id, session)

    if not data.permissoes_validas():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Formato inválido. Use: {"granted": ["modulo:recurso:acao", "financeiro:*"]}'
        )

    if data.nome is not None and data.nome != perfil.nome:
        existing = await session.execute(
            select(PerfilAcesso).where(
                PerfilAcesso.tenant_id == tenant_id,
                PerfilAcesso.nome == data.nome,
                PerfilAcesso.id != perfil.id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe um perfil com o nome '{data.nome}'"
            )
        perfil.nome = data.nome

    if data.descricao is not None:
        perfil.descricao = data.descricao

    if data.permissoes is not None:
        perfil.permissoes = data.permissoes

    await session.commit()
    await session.refresh(perfil)

    return PerfilResponse(
        id=str(perfil.id),
        nome=perfil.nome,
        is_custom=perfil.is_custom,
        descricao=perfil.descricao,
        permissoes=perfil.permissoes
    )


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_tenant_permission("tenant:permissions:delete"))])
async def delete_custom_role(
    role_id: str,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Remove um perfil customizado do tenant.
    Bloqueado se houver usuários ou fazendas usando este perfil.
    """
    from sqlalchemy import func

    perfil = await _get_tenant_custom_role_or_404(role_id, tenant_id, session)

    uso_tenant = (await session.execute(
        select(func.count(TenantUsuario.id)).where(TenantUsuario.perfil_id == perfil.id)
    )).scalar_one()

    uso_fazenda = (await session.execute(
        select(func.count(FazendaUsuario.id)).where(FazendaUsuario.perfil_fazenda_id == perfil.id)
    )).scalar_one()

    total_uso = uso_tenant + uso_fazenda
    if total_uso > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Perfil em uso por {total_uso} usuário(s). Reatribua-os antes de remover."
        )

    await session.delete(perfil)
    await session.commit()
