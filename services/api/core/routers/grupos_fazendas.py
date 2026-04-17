"""
Router para gestão de grupos de fazendas.

Permite organizar fazendas em grupos para:
- Assinaturas dedicadas por grupo
- Limites compartilhados de usuários
- Gestão separada de módulos

Endpoints:
- GET    /grupos-fazendas          - Listar grupos
- POST   /grupos-fazendas          - Criar grupo
- PATCH  /grupos-fazendas/{id}     - Atualizar grupo
- DELETE /grupos-fazendas/{id}     - Excluir grupo
- POST   /grupos-fazendas/{id}/fazendas - Adicionar fazendas ao grupo
- DELETE /grupos-fazendas/{id}/fazendas/{unidade_produtiva_id} - Remover fazenda do grupo
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from core.dependencies import (
    get_session,
    get_tenant_id,
    require_tenant_permission
)
# grupos_fazendas removed
from core.models.unidade_produtiva import UnidadeProdutiva as Fazenda
from core.models.billing import AssinaturaTenant, PlanoAssinatura
from core.models.auth import Usuario
from pydantic import BaseModel, Field

router = APIRouter(prefix="/grupos-fazendas", tags=["Grupos de Fazendas"])

# ==================== SCHEMAS ====================

class GrupoFazendasCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=150)
    descricao: str | None = None
    cor: str | None = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Cor HEX (ex: #3B82F6)")
    icone: str | None = None
    ordem: int = 0

class GrupoFazendasUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    cor: str | None = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icone: str | None = None
    ordem: int | None = None
    ativo: bool | None = None

class FazendaInfo(BaseModel):
    id: str
    nome: str
    area_total_ha: float | None
    ativo: bool

class AssinaturaInfo(BaseModel):
    id: str
    plano_nome: str
    status: str
    limite_usuarios_maximo: Optional[int]
    modulos: List[str]

class GrupoFazendasResponse(BaseModel):
    id: str
    nome: str
    descricao: str | None
    cor: str | None
    icone: str | None
    ordem: int
    ativo: bool
    total_fazendas: int
    area_total_ha: float
    assinatura: AssinaturaInfo | None
    created_at: datetime

class GrupoDetalhadoResponse(GrupoFazendasResponse):
    fazendas: List[FazendaInfo]

class AddFazendasRequest(BaseModel):
    fazendas_ids: List[str] = Field(..., min_items=1)

# Member management schemas
class AddMembroRequest(BaseModel):
    user_id: str
    perfil_id: str | None = None

class UpdateMembroRequest(BaseModel):
    perfil_id: str | None = None

class MembroResponse(BaseModel):
    id: str
    user_id: str
    nome: str
    email: str
    perfil_id: str | None
    created_at: datetime

# ==================== ENDPOINTS ====================

@router.get("", response_model=List[GrupoFazendasResponse], dependencies=[Depends(require_tenant_permission("tenant:grupos:view"))])
async def list_grupos(
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    include_inactive: bool = False,
    session: AsyncSession = Depends(get_session)
):
    """Lista todos os grupos de fazendas do tenant."""

    stmt = select(GrupoFazendas).where(GrupoFazendas.tenant_id == tenant_id)

    if not include_inactive:
        stmt = stmt.where(GrupoFazendas.ativo == True)

    stmt = stmt.order_by(GrupoFazendas.ordem, GrupoFazendas.nome)

    result = await session.execute(stmt)
    grupos = result.scalars().all()

    response = []
    for grupo in grupos:
        # Contar fazendas e área total
        stmt_fazendas = select(
            func.count(Fazenda.id),
            func.sum(Fazenda.area_total_ha)
        ).where(Fazenda.unidade_produtiva_id == grupo.id)

        result_faz = await session.execute(stmt_fazendas)
        total_faz, area_total = result_faz.first()

        # Buscar assinatura do grupo
        stmt_assinatura = (
            select(AssinaturaTenant, PlanoAssinatura)
            .join(PlanoAssinatura, AssinaturaTenant.plano_id == PlanoAssinatura.id)
            .where(AssinaturaTenant.grupo_fazendas_id == grupo.id)
        )
        result_ass = await session.execute(stmt_assinatura)
        row_ass = result_ass.first()

        assinatura_info = None
        if row_ass:
            assinatura, plano = row_ass
            assinatura_info = AssinaturaInfo(
                id=str(assinatura.id),
                plano_nome=plano.nome,
                status=assinatura.status,
                limite_usuarios_maximo=plano.limite_usuarios_maximo,
                modulos=plano.modulos_inclusos
            )

        response.append(GrupoFazendasResponse(
            id=str(grupo.id),
            nome=grupo.nome,
            descricao=grupo.descricao,
            cor=grupo.cor,
            icone=grupo.icone,
            ordem=grupo.ordem,
            ativo=grupo.ativo,
            total_fazendas=total_faz or 0,
            area_total_ha=float(area_total or 0),
            assinatura=assinatura_info,
            created_at=grupo.created_at
        ))

    return response


@router.get("/{grupo_id}", response_model=GrupoDetalhadoResponse, dependencies=[Depends(require_tenant_permission("tenant:grupos:view"))])
async def get_grupo_detalhado(
    grupo_id: str,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Detalhes completos de um grupo incluindo fazendas."""

    try:
        grupo_uuid = uuid.UUID(grupo_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    grupo = await session.get(GrupoFazendas, grupo_uuid)
    if not grupo or grupo.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")

    # Buscar fazendas do grupo
    stmt_fazendas = select(Fazenda).where(Fazenda.unidade_produtiva_id == grupo_uuid)
    result_faz = await session.execute(stmt_fazendas)
    fazendas = result_faz.scalars().all()

    fazendas_info = [
        FazendaInfo(
            id=str(f.id),
            nome=f.nome,
            area_total_ha=f.area_total_ha,
            ativo=f.ativo
        )
        for f in fazendas
    ]

    # Área total e assinatura (igual ao list)
    total_faz = len(fazendas)
    area_total = sum(f.area_total_ha or 0 for f in fazendas)

    stmt_assinatura = (
        select(AssinaturaTenant, PlanoAssinatura)
        .join(PlanoAssinatura, AssinaturaTenant.plano_id == PlanoAssinatura.id)
        .where(AssinaturaTenant.grupo_fazendas_id == grupo.id)
    )
    result_ass = await session.execute(stmt_assinatura)
    row_ass = result_ass.first()

    assinatura_info = None
    if row_ass:
        assinatura, plano = row_ass
        assinatura_info = AssinaturaInfo(
            id=str(assinatura.id),
            plano_nome=plano.nome,
            status=assinatura.status,
            limite_usuarios_maximo=plano.limite_usuarios_maximo,
            modulos=plano.modulos_inclusos
        )

    return GrupoDetalhadoResponse(
        id=str(grupo.id),
        nome=grupo.nome,
        descricao=grupo.descricao,
        cor=grupo.cor,
        icone=grupo.icone,
        ordem=grupo.ordem,
        ativo=grupo.ativo,
        total_fazendas=total_faz,
        area_total_ha=area_total,
        assinatura=assinatura_info,
        created_at=grupo.created_at,
        fazendas=fazendas_info
    )


@router.post("", response_model=GrupoFazendasResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_tenant_permission("tenant:grupos:create"))])
async def create_grupo(
    data: GrupoFazendasCreate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Cria um novo grupo de fazendas."""

    grupo = GrupoFazendas(
        tenant_id=tenant_id,
        nome=data.nome,
        descricao=data.descricao,
        cor=data.cor,
        icone=data.icone,
        ordem=data.ordem,
        ativo=True
    )

    session.add(grupo)
    await session.commit()
    await session.refresh(grupo)

    return GrupoFazendasResponse(
        id=str(grupo.id),
        nome=grupo.nome,
        descricao=grupo.descricao,
        cor=grupo.cor,
        icone=grupo.icone,
        ordem=grupo.ordem,
        ativo=grupo.ativo,
        total_fazendas=0,
        area_total_ha=0.0,
        assinatura=None,
        created_at=grupo.created_at
    )


@router.patch("/{grupo_id}", response_model=GrupoFazendasResponse, dependencies=[Depends(require_tenant_permission("tenant:grupos:update"))])
async def update_grupo(
    grupo_id: str,
    data: GrupoFazendasUpdate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Atualiza dados de um grupo."""

    try:
        grupo_uuid = uuid.UUID(grupo_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    grupo = await session.get(GrupoFazendas, grupo_uuid)
    if not grupo or grupo.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")

    # Atualizar campos
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(grupo, field, value)

    grupo.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(grupo)

    # Recalcular totais
    stmt_fazendas = select(
        func.count(Fazenda.id),
        func.sum(Fazenda.area_total_ha)
    ).where(Fazenda.unidade_produtiva_id == grupo.id)
    result_faz = await session.execute(stmt_fazendas)
    total_faz, area_total = result_faz.first()

    return GrupoFazendasResponse(
        id=str(grupo.id),
        nome=grupo.nome,
        descricao=grupo.descricao,
        cor=grupo.cor,
        icone=grupo.icone,
        ordem=grupo.ordem,
        ativo=grupo.ativo,
        total_fazendas=total_faz or 0,
        area_total_ha=float(area_total or 0),
        assinatura=None,
        created_at=grupo.created_at
    )


@router.delete("/{grupo_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_tenant_permission("tenant:grupos:delete"))])
async def delete_grupo(
    grupo_id: str,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Exclui um grupo (soft delete - marca como inativo)."""

    try:
        grupo_uuid = uuid.UUID(grupo_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    grupo = await session.get(GrupoFazendas, grupo_uuid)
    if not grupo or grupo.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")

    # Verificar se grupo tem assinatura ativa
    stmt_ass = select(AssinaturaTenant).where(
        and_(
            AssinaturaTenant.grupo_fazendas_id == grupo_uuid,
            AssinaturaTenant.status == "ATIVA"
        )
    )
    assinatura_ativa = await session.scalar(stmt_ass)
    if assinatura_ativa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir grupo com assinatura ativa. Cancele a assinatura primeiro."
        )

    # Soft delete
    grupo.ativo = False
    grupo.updated_at = datetime.now(timezone.utc)

    # Remover grupo_id das fazendas
    stmt_fazendas = select(Fazenda).where(Fazenda.unidade_produtiva_id == grupo_uuid)
    result = await session.execute(stmt_fazendas)
    fazendas = result.scalars().all()

    for fazenda in fazendas:
        fazenda.grupo_id = None

    await session.commit()


@router.post("/{grupo_id}/fazendas", dependencies=[Depends(require_tenant_permission("tenant:grupos:update"))])
async def add_fazendas_to_grupo(
    grupo_id: str,
    data: AddFazendasRequest,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Adiciona fazendas a um grupo."""

    try:
        grupo_uuid = uuid.UUID(grupo_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    grupo = await session.get(GrupoFazendas, grupo_uuid)
    if not grupo or grupo.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")

    added_count = 0
    for fazenda_id_str in data.unidades_produtivas_ids:
        try:
            fazenda_uuid = uuid.UUID(fazenda_id_str)
            fazenda = await session.get(Fazenda, fazenda_uuid)

            if fazenda and fazenda.tenant_id == tenant_id:
                fazenda.grupo_id = grupo_uuid
                added_count += 1

        except ValueError:
            continue  # Ignora IDs inválidos

    await session.commit()

    return {"message": f"{added_count} fazendas adicionadas ao grupo"}


@router.delete("/{grupo_id}/fazendas/{unidade_produtiva_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_tenant_permission("tenant:grupos:update"))])
async def remove_fazenda_from_grupo(
    grupo_id: str,
    unidade_produtiva_id: str,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """Remove uma fazenda do grupo."""

    try:
        grupo_uuid = uuid.UUID(grupo_id)
        fazenda_uuid = uuid.UUID(unidade_produtiva_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID inválido")

    fazenda = await session.get(Fazenda, fazenda_uuid)
    if not fazenda or fazenda.tenant_id != tenant_id or fazenda.grupo_id != grupo_uuid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fazenda não encontrada neste grupo")

    fazenda.grupo_id = None
    await session.commit()


# ==================== MEMBER MANAGEMENT ====================

def _parse_uuid(value: str, label: str = "ID") -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{label} inválido")


async def _get_grupo_or_404(session: AsyncSession, grupo_uuid: uuid.UUID, tenant_id: uuid.UUID) -> GrupoFazendas:
    grupo = await session.get(GrupoFazendas, grupo_uuid)
    if not grupo or grupo.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    return grupo


@router.get(
    "/{grupo_id}/membros",
    response_model=List[MembroResponse],
    dependencies=[Depends(require_tenant_permission("tenant:grupos:view"))],
)
async def list_membros(
    grupo_id: str,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Lista membros de um grupo com detalhes do usuário."""
    grupo_uuid = _parse_uuid(grupo_id, "grupo_id")
    await _get_grupo_or_404(session, grupo_uuid, tenant_id)

    stmt = (
        select(GrupoUsuario, Usuario)
        .join(Usuario, GrupoUsuario.user_id == Usuario.id)
        .where(GrupoUsuario.tenant_id == grupo_uuid)
        .order_by(Usuario.nome)
    )
    result = await session.execute(stmt)
    rows = result.all()

    return [
        MembroResponse(
            id=str(gu.id),
            user_id=str(gu.user_id),
            nome=u.nome,
            email=u.email,
            perfil_id=str(gu.perfil_id) if gu.perfil_id else None,
            created_at=gu.created_at,
        )
        for gu, u in rows
    ]


@router.post(
    "/{grupo_id}/membros",
    response_model=MembroResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_tenant_permission("tenant:grupos:edit"))],
)
async def add_membro(
    grupo_id: str,
    data: AddMembroRequest,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Adiciona um usuário ao grupo."""
    grupo_uuid = _parse_uuid(grupo_id, "grupo_id")
    user_uuid = _parse_uuid(data.user_id, "user_id")
    perfil_uuid = _parse_uuid(data.perfil_id, "perfil_id") if data.perfil_id else None

    await _get_grupo_or_404(session, grupo_uuid, tenant_id)

    # Verify user belongs to this tenant
    usuario = await session.get(Usuario, user_uuid)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # Check duplicate
    existing = await session.scalar(
        select(GrupoUsuario).where(
            and_(GrupoUsuario.tenant_id == grupo_uuid, GrupoUsuario.user_id == user_uuid)
        )
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuário já é membro deste grupo")

    membro = GrupoUsuario(
        tenant_id=tenant_id,
        grupo_id=grupo_uuid,
        user_id=user_uuid,
        perfil_id=perfil_uuid,
    )
    session.add(membro)
    await session.commit()
    await session.refresh(membro)

    return MembroResponse(
        id=str(membro.id),
        user_id=str(membro.user_id),
        nome=usuario.nome,
        email=usuario.email,
        perfil_id=str(membro.perfil_id) if membro.perfil_id else None,
        created_at=membro.created_at,
    )


@router.delete(
    "/{grupo_id}/membros/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_tenant_permission("tenant:grupos:edit"))],
)
async def remove_membro(
    grupo_id: str,
    user_id: str,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Remove um usuário do grupo. Não é permitido remover o último membro com perfil de owner."""
    grupo_uuid = _parse_uuid(grupo_id, "grupo_id")
    user_uuid = _parse_uuid(user_id, "user_id")

    await _get_grupo_or_404(session, grupo_uuid, tenant_id)

    membro = await session.scalar(
        select(GrupoUsuario).where(
            and_(GrupoUsuario.tenant_id == grupo_uuid, GrupoUsuario.user_id == user_uuid)
        )
    )
    if not membro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membro não encontrado neste grupo")

    # Guard: cannot remove if last member
    total_membros = await session.scalar(
        select(func.count(GrupoUsuario.id)).where(GrupoUsuario.tenant_id == grupo_uuid)
    )
    if total_membros <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível remover o último membro do grupo",
        )

    await session.delete(membro)
    await session.commit()


@router.patch(
    "/{grupo_id}/membros/{user_id}",
    response_model=MembroResponse,
    dependencies=[Depends(require_tenant_permission("tenant:grupos:edit"))],
)
async def update_membro(
    grupo_id: str,
    user_id: str,
    data: UpdateMembroRequest,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Atualiza o perfil de acesso de um membro no grupo."""
    grupo_uuid = _parse_uuid(grupo_id, "grupo_id")
    user_uuid = _parse_uuid(user_id, "user_id")
    perfil_uuid = _parse_uuid(data.perfil_id, "perfil_id") if data.perfil_id else None

    await _get_grupo_or_404(session, grupo_uuid, tenant_id)

    membro = await session.scalar(
        select(GrupoUsuario).where(
            and_(GrupoUsuario.tenant_id == grupo_uuid, GrupoUsuario.user_id == user_uuid)
        )
    )
    if not membro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membro não encontrado neste grupo")

    membro.perfil_id = perfil_uuid
    await session.commit()
    await session.refresh(membro)

    usuario = await session.get(Usuario, user_uuid)

    return MembroResponse(
        id=str(membro.id),
        user_id=str(membro.user_id),
        nome=usuario.nome,
        email=usuario.email,
        perfil_id=str(membro.perfil_id) if membro.perfil_id else None,
        created_at=membro.created_at,
    )
