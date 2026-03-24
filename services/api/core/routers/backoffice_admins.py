"""
Router para gestão de administradores do SaaS (AdminUsers).

Endpoints:
- GET    /backoffice/admins           - Listar admins
- POST   /backoffice/admins           - Criar novo admin
- PATCH  /backoffice/admins/{id}      - Atualizar admin
- DELETE /backoffice/admins/{id}      - Desativar admin
- POST   /backoffice/admins/{id}/reset-password - Resetar senha
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import uuid
from datetime import datetime, timezone
from passlib.context import CryptContext

from core.dependencies import get_session, require_permission
from core.models.admin_user import AdminUser
from core.models.admin_audit_log import AdminAuditLog
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(prefix="/backoffice/admins", tags=["Backoffice - Admins"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== SCHEMAS ====================

class AdminUserCreate(BaseModel):
    email: EmailStr
    nome: str = Field(..., min_length=3, max_length=255)
    role: str = Field(..., description="super_admin, admin, suporte, financeiro, comercial")
    senha: str = Field(..., min_length=8)
    timezone: str = Field(default="America/Sao_Paulo")
    locale: str = Field(default="pt-BR")

class AdminUserUpdate(BaseModel):
    nome: str | None = None
    role: str | None = None
    ativo: bool | None = None
    timezone: str | None = None
    locale: str | None = None

class AdminUserResponse(BaseModel):
    id: str
    email: str
    nome: str
    role: str
    ativo: bool
    ultimo_acesso: datetime | None
    timezone: str
    locale: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AdminStatsResponse(BaseModel):
    total: int
    ativos: int
    super_admins: int
    por_role: dict[str, int]

class PasswordResetRequest(BaseModel):
    nova_senha: str = Field(..., min_length=8)

# ==================== ENDPOINTS ====================

@router.get("/stats", response_model=AdminStatsResponse, dependencies=[Depends(require_permission("backoffice:admin_users:view"))])
async def get_admin_stats(session: AsyncSession = Depends(get_session)):
    """Estatísticas de administradores."""

    total = await session.scalar(select(func.count(AdminUser.id)))
    ativos = await session.scalar(select(func.count(AdminUser.id)).where(AdminUser.ativo == True))
    super_admins = await session.scalar(select(func.count(AdminUser.id)).where(AdminUser.role == "super_admin"))

    # Contagem por role
    result = await session.execute(
        select(AdminUser.role, func.count(AdminUser.id))
        .group_by(AdminUser.role)
    )
    por_role = {row[0]: row[1] for row in result}

    return AdminStatsResponse(
        total=total or 0,
        ativos=ativos or 0,
        super_admins=super_admins or 0,
        por_role=por_role
    )


@router.get("", response_model=List[AdminUserResponse], dependencies=[Depends(require_permission("backoffice:admin_users:view"))])
async def list_admins(
    skip: int = 0,
    limit: int = 100,
    role: str | None = None,
    ativo: bool | None = None,
    session: AsyncSession = Depends(get_session)
):
    """Lista todos os administradores do SaaS."""

    stmt = select(AdminUser).offset(skip).limit(limit).order_by(AdminUser.created_at.desc())

    # Filtros
    if role:
        stmt = stmt.where(AdminUser.role == role)
    if ativo is not None:
        stmt = stmt.where(AdminUser.ativo == ativo)

    result = await session.execute(stmt)
    admins = result.scalars().all()

    return [AdminUserResponse.model_validate(admin) for admin in admins]


@router.post("", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("backoffice:admin_users:create"))])
async def create_admin(
    data: AdminUserCreate,
    session: AsyncSession = Depends(get_session)
):
    """Cria um novo administrador do SaaS."""

    # Validar role
    valid_roles = ["super_admin", "admin", "suporte", "financeiro", "comercial"]
    if data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role inválida. Opções: {', '.join(valid_roles)}"
        )

    # Verificar se email já existe
    existing = await session.scalar(select(AdminUser).where(AdminUser.email == data.email))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    # Hash da senha
    senha_hash = pwd_context.hash(data.senha)

    # Criar admin
    admin = AdminUser(
        email=data.email,
        nome=data.nome,
        role=data.role,
        senha_hash=senha_hash,
        timezone=data.timezone,
        locale=data.locale,
        ativo=True
    )

    session.add(admin)
    await session.commit()
    await session.refresh(admin)

    # Log de auditoria
    log = AdminAuditLog(
        admin_user_id=admin.id,
        acao="ADMIN_CREATED",
        recurso="admin_users",
        recurso_id=str(admin.id),
        detalhes={"email": data.email, "role": data.role}
    )
    session.add(log)
    await session.commit()

    return AdminUserResponse.model_validate(admin)


@router.patch("/{admin_id}", response_model=AdminUserResponse, dependencies=[Depends(require_permission("backoffice:admin_users:update"))])
async def update_admin(
    admin_id: str,
    data: AdminUserUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Atualiza dados de um administrador."""

    try:
        admin_uuid = uuid.UUID(admin_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    admin = await session.get(AdminUser, admin_uuid)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin não encontrado")

    # Atualizar campos
    update_data = data.model_dump(exclude_unset=True)

    if "role" in update_data:
        valid_roles = ["super_admin", "admin", "suporte", "financeiro", "comercial"]
        if update_data["role"] not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role inválida. Opções: {', '.join(valid_roles)}"
            )

    for field, value in update_data.items():
        setattr(admin, field, value)

    admin.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(admin)

    # Log de auditoria
    log = AdminAuditLog(
        admin_user_id=admin.id,
        acao="ADMIN_UPDATED",
        recurso="admin_users",
        recurso_id=str(admin.id),
        detalhes=update_data
    )
    session.add(log)
    await session.commit()

    return AdminUserResponse.model_validate(admin)


@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("backoffice:admin_users:delete"))])
async def deactivate_admin(
    admin_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Desativa um administrador (soft delete)."""

    try:
        admin_uuid = uuid.UUID(admin_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    admin = await session.get(AdminUser, admin_uuid)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin não encontrado")

    # Não permitir desativar super_admins
    if admin.role == "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível desativar super_admin"
        )

    admin.ativo = False
    admin.updated_at = datetime.now(timezone.utc)

    await session.commit()

    # Log de auditoria
    log = AdminAuditLog(
        admin_user_id=admin.id,
        acao="ADMIN_DEACTIVATED",
        recurso="admin_users",
        recurso_id=str(admin.id),
        detalhes={"email": admin.email}
    )
    session.add(log)
    await session.commit()


@router.post("/{admin_id}/reset-password", dependencies=[Depends(require_permission("backoffice:admin_users:update"))])
async def reset_admin_password(
    admin_id: str,
    data: PasswordResetRequest,
    session: AsyncSession = Depends(get_session)
):
    """Reseta a senha de um administrador."""

    try:
        admin_uuid = uuid.UUID(admin_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    admin = await session.get(AdminUser, admin_uuid)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin não encontrado")

    # Hash da nova senha
    admin.senha_hash = pwd_context.hash(data.nova_senha)
    admin.updated_at = datetime.now(timezone.utc)

    await session.commit()

    # Log de auditoria
    log = AdminAuditLog(
        admin_user_id=admin.id,
        acao="ADMIN_PASSWORD_RESET",
        recurso="admin_users",
        recurso_id=str(admin.id),
        detalhes={"email": admin.email}
    )
    session.add(log)
    await session.commit()

    return {"message": "Senha resetada com sucesso"}
