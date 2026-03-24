"""
Router backoffice para gestão de perfis de acesso padrão do sistema.

Apenas administradores SaaS gerenciam perfis globais (tenant_id = NULL).
Tenants não têm acesso a estes endpoints.

Endpoints:
- GET    /backoffice/profiles         - Listar todos os perfis padrão do sistema
- GET    /backoffice/profiles/{id}    - Detalhar perfil padrão
- POST   /backoffice/profiles         - Criar novo perfil padrão
- PATCH  /backoffice/profiles/{id}    - Editar perfil padrão
- DELETE /backoffice/profiles/{id}    - Remover perfil padrão (somente se não estiver em uso)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import uuid

from core.dependencies import get_session, require_permission
from core.models.auth import PerfilAcesso, TenantUsuario, FazendaUsuario
from core.constants import TenantRoles
from pydantic import BaseModel, Field

router = APIRouter(prefix="/backoffice/profiles", tags=["Backoffice - Perfis Padrão"])

VALID_PERMISSION_LEVELS = ["write", "read", "none", "*"]


# ==================== SCHEMAS ====================

class SystemProfileRequest(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    descricao: str | None = Field(None, max_length=500)
    permissoes: dict = Field(
        ...,
        description='{"agricola": "write", "pecuaria": "read", "financeiro": "none"}'
    )


class SystemProfileResponse(BaseModel):
    id: str
    nome: str
    descricao: str | None
    is_custom: bool
    permissoes: dict
    em_uso: int | None = None  # quantos tenant_usuarios usam este perfil

    class Config:
        from_attributes = True


# ==================== HELPERS ====================

def _validate_permissoes(permissoes: dict) -> None:
    for module, level in permissoes.items():
        if level not in VALID_PERMISSION_LEVELS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nível inválido para '{module}': '{level}'. Use: {', '.join(VALID_PERMISSION_LEVELS)}"
            )


async def _get_system_profile_or_404(profile_id: str, session: AsyncSession) -> PerfilAcesso:
    try:
        pid = uuid.UUID(profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    perfil = await session.get(PerfilAcesso, pid)
    if not perfil or perfil.tenant_id is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil padrão não encontrado"
        )
    return perfil


# ==================== ENDPOINTS ====================

@router.get("", response_model=List[SystemProfileResponse], dependencies=[Depends(require_permission("backoffice:profiles:view"))])
async def list_system_profiles(session: AsyncSession = Depends(get_session)):
    """Lista todos os perfis padrão do sistema (tenant_id = NULL)."""

    stmt = (
        select(PerfilAcesso)
        .where(PerfilAcesso.tenant_id == None)
        .order_by(PerfilAcesso.nome)
    )
    result = await session.execute(stmt)
    perfis = result.scalars().all()

    # Conta uso de cada perfil
    uso_stmt = (
        select(TenantUsuario.perfil_id, func.count(TenantUsuario.id))
        .where(TenantUsuario.perfil_id.in_([p.id for p in perfis]))
        .group_by(TenantUsuario.perfil_id)
    )
    uso_result = await session.execute(uso_stmt)
    uso_map = {str(row[0]): row[1] for row in uso_result.all()}

    return [
        SystemProfileResponse(
            id=str(p.id),
            nome=p.nome,
            descricao=p.descricao or TenantRoles.DESCRIPTIONS.get(p.nome.lower()),
            is_custom=p.is_custom,
            permissoes=p.permissoes or {},
            em_uso=uso_map.get(str(p.id), 0)
        )
        for p in perfis
    ]


@router.get("/{profile_id}", response_model=SystemProfileResponse, dependencies=[Depends(require_permission("backoffice:profiles:view"))])
async def get_system_profile(
    profile_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Detalha um perfil padrão do sistema."""

    perfil = await _get_system_profile_or_404(profile_id, session)

    uso_stmt = select(func.count(TenantUsuario.id)).where(TenantUsuario.perfil_id == perfil.id)
    em_uso = (await session.execute(uso_stmt)).scalar_one()

    return SystemProfileResponse(
        id=str(perfil.id),
        nome=perfil.nome,
        descricao=perfil.descricao or TenantRoles.DESCRIPTIONS.get(perfil.nome.lower()),
        is_custom=perfil.is_custom,
        permissoes=perfil.permissoes or {},
        em_uso=em_uso
    )


@router.post("", response_model=SystemProfileResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("backoffice:profiles:create"))])
async def create_system_profile(
    data: SystemProfileRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Cria um novo perfil padrão do sistema (tenant_id = NULL).
    Ficará disponível para todos os tenants como opção de perfil.
    """

    _validate_permissoes(data.permissoes)

    # Verificar nome duplicado entre perfis do sistema
    existing = await session.execute(
        select(PerfilAcesso).where(
            PerfilAcesso.tenant_id == None,
            PerfilAcesso.nome == data.nome
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe um perfil padrão com o nome '{data.nome}'"
        )

    perfil = PerfilAcesso(
        tenant_id=None,
        nome=data.nome,
        descricao=data.descricao,
        is_custom=False,
        permissoes=data.permissoes
    )
    session.add(perfil)
    await session.commit()
    await session.refresh(perfil)

    return SystemProfileResponse(
        id=str(perfil.id),
        nome=perfil.nome,
        descricao=perfil.descricao,
        is_custom=perfil.is_custom,
        permissoes=perfil.permissoes,
        em_uso=0
    )


@router.patch("/{profile_id}", response_model=SystemProfileResponse, dependencies=[Depends(require_permission("backoffice:profiles:update"))])
async def update_system_profile(
    profile_id: str,
    data: SystemProfileRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Edita um perfil padrão do sistema.
    Alterações refletem imediatamente nas verificações de permissão de todos os tenants que usam este perfil.
    """

    perfil = await _get_system_profile_or_404(profile_id, session)
    _validate_permissoes(data.permissoes)

    # Verificar conflito de nome (exceto o próprio)
    existing = await session.execute(
        select(PerfilAcesso).where(
            PerfilAcesso.tenant_id == None,
            PerfilAcesso.nome == data.nome,
            PerfilAcesso.id != perfil.id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe um perfil padrão com o nome '{data.nome}'"
        )

    perfil.nome = data.nome
    perfil.descricao = data.descricao
    perfil.permissoes = data.permissoes
    await session.commit()
    await session.refresh(perfil)

    uso_stmt = select(func.count(TenantUsuario.id)).where(TenantUsuario.perfil_id == perfil.id)
    em_uso = (await session.execute(uso_stmt)).scalar_one()

    return SystemProfileResponse(
        id=str(perfil.id),
        nome=perfil.nome,
        descricao=perfil.descricao,
        is_custom=perfil.is_custom,
        permissoes=perfil.permissoes,
        em_uso=em_uso
    )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("backoffice:profiles:delete"))])
async def delete_system_profile(
    profile_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Remove um perfil padrão do sistema.
    Bloqueado se há usuários (tenant_usuarios ou fazenda_usuarios) usando este perfil.
    """

    perfil = await _get_system_profile_or_404(profile_id, session)

    # Verificar se está em uso em tenant_usuarios
    uso_tenant = (await session.execute(
        select(func.count(TenantUsuario.id)).where(TenantUsuario.perfil_id == perfil.id)
    )).scalar_one()

    # Verificar se está em uso como override por fazenda
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
