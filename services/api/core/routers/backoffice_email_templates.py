from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List
from uuid import UUID
from datetime import datetime

from core.dependencies import get_session, get_current_admin, require_permission
from core.models.email_template import EmailTemplate, EmailLog
from pydantic import BaseModel

router = APIRouter(
    prefix="/backoffice/email-templates",
    tags=["Backoffice - Email Templates"],
    dependencies=[Depends(require_permission("backoffice:email_templates:view"))],
)


# ==================== SCHEMAS ====================

class EmailTemplateCreate(BaseModel):
    codigo: str
    nome: str
    descricao: str | None = None
    assunto: str
    corpo_html: str
    corpo_texto: str
    variaveis: list[str] = []
    tipo: str  # transacional, marketing, sistema
    ativo: bool = True


class EmailTemplateUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    assunto: str | None = None
    corpo_html: str | None = None
    corpo_texto: str | None = None
    variaveis: list[str] | None = None
    tipo: str | None = None
    ativo: bool | None = None


class EmailTemplateResponse(BaseModel):
    id: UUID
    codigo: str
    nome: str
    descricao: str | None
    assunto: str
    corpo_html: str
    corpo_texto: str
    variaveis: list | dict
    tipo: str
    ativo: bool
    editado_por_id: UUID | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmailLogResponse(BaseModel):
    id: UUID
    template_id: UUID | None
    template_codigo: str | None
    destinatario_email: str
    destinatario_nome: str | None
    tenant_id: UUID | None
    assunto: str
    status: str
    erro_mensagem: str | None
    provider: str | None
    aberto: bool
    data_abertura: datetime | None
    clicado: bool
    data_clique: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class EmailLogListResponse(BaseModel):
    items: List[EmailLogResponse]
    total: int
    page: int
    page_size: int


class EmailStatsResponse(BaseModel):
    total_templates: int
    ativos: int
    inativos: int
    por_tipo: dict[str, int]
    emails_enviados: int
    emails_abertos: int
    emails_clicados: int
    taxa_abertura: float


# ==================== ENDPOINTS - TEMPLATES ====================

@router.get("/stats", response_model=EmailStatsResponse)
async def get_email_stats(
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Estatísticas de templates e envios."""
    total = await session.scalar(select(func.count(EmailTemplate.id))) or 0
    ativos = await session.scalar(select(func.count(EmailTemplate.id)).where(EmailTemplate.ativo == True)) or 0

    result = await session.execute(
        select(EmailTemplate.tipo, func.count(EmailTemplate.id))
        .group_by(EmailTemplate.tipo)
    )
    por_tipo = {row[0]: row[1] for row in result}

    enviados = await session.scalar(select(func.count(EmailLog.id))) or 0
    abertos = await session.scalar(select(func.count(EmailLog.id)).where(EmailLog.aberto == True)) or 0
    clicados = await session.scalar(select(func.count(EmailLog.id)).where(EmailLog.clicado == True)) or 0

    return EmailStatsResponse(
        total_templates=total,
        ativos=ativos,
        inativos=total - ativos,
        por_tipo=por_tipo,
        emails_enviados=enviados,
        emails_abertos=abertos,
        emails_clicados=clicados,
        taxa_abertura=round((abertos / enviados * 100) if enviados > 0 else 0, 1),
    )


@router.get("", response_model=List[EmailTemplateResponse])
async def listar_templates(
    tipo: str | None = None,
    ativo: bool | None = None,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Lista todos os templates de email."""
    stmt = select(EmailTemplate).order_by(EmailTemplate.tipo, EmailTemplate.nome)

    if tipo:
        stmt = stmt.where(EmailTemplate.tipo == tipo)
    if ativo is not None:
        stmt = stmt.where(EmailTemplate.ativo == ativo)

    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/{template_id}", response_model=EmailTemplateResponse)
async def get_template(
    template_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Retorna um template pelo ID."""
    template = await session.get(EmailTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    return template


@router.post(
    "",
    response_model=EmailTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("backoffice:email_templates:create"))],
)
async def criar_template(
    data: EmailTemplateCreate,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Cria um novo template de email."""
    # Verificar código duplicado
    existing = await session.execute(
        select(EmailTemplate).where(EmailTemplate.codigo == data.codigo)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Código de template já existe")

    template = EmailTemplate(
        codigo=data.codigo,
        nome=data.nome,
        descricao=data.descricao,
        assunto=data.assunto,
        corpo_html=data.corpo_html,
        corpo_texto=data.corpo_texto,
        variaveis=data.variaveis,
        tipo=data.tipo,
        ativo=data.ativo,
        editado_por_id=UUID(current_admin["admin_id"]) if current_admin.get("admin_id") else None,
    )

    session.add(template)
    await session.commit()
    await session.refresh(template)
    return template


@router.put(
    "/{template_id}",
    response_model=EmailTemplateResponse,
    dependencies=[Depends(require_permission("backoffice:email_templates:update"))],
)
async def atualizar_template(
    template_id: UUID,
    data: EmailTemplateUpdate,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Atualiza um template existente."""
    template = await session.get(EmailTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    template.editado_por_id = UUID(current_admin["admin_id"]) if current_admin.get("admin_id") else None

    await session.commit()
    await session.refresh(template)
    return template


# ==================== ENDPOINTS - LOGS ====================

@router.get("/logs/list", response_model=EmailLogListResponse)
async def listar_email_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=10, le=200),
    template_codigo: str | None = None,
    status_filtro: str | None = Query(None, alias="status"),
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Lista logs de emails enviados."""
    stmt = select(EmailLog)
    count_stmt = select(func.count(EmailLog.id))

    if template_codigo:
        stmt = stmt.where(EmailLog.template_codigo == template_codigo)
        count_stmt = count_stmt.where(EmailLog.template_codigo == template_codigo)
    if status_filtro:
        stmt = stmt.where(EmailLog.status == status_filtro)
        count_stmt = count_stmt.where(EmailLog.status == status_filtro)

    total = await session.scalar(count_stmt) or 0

    offset = (page - 1) * page_size
    stmt = stmt.order_by(desc(EmailLog.created_at)).offset(offset).limit(page_size)

    result = await session.execute(stmt)
    logs = result.scalars().all()

    return EmailLogListResponse(
        items=[EmailLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
    )
