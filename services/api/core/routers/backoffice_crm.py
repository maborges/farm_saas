from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, case, update
from sqlalchemy.orm import joinedload
from typing import List
from uuid import UUID
from datetime import datetime, date

from core.dependencies import get_session, get_current_admin, require_permission
from core.models.crm import PipelineEstagio, LeadCRM, AtividadeCRM
from pydantic import BaseModel


router = APIRouter(
    prefix="/backoffice/crm",
    tags=["Backoffice - CRM"],
    dependencies=[Depends(require_permission("backoffice:crm:view"))],
)


# ==================== SCHEMAS ====================

# --- Pipeline Estágios ---

class EstagioCreate(BaseModel):
    nome: str
    cor: str = "#3b82f6"
    ordem: int = 0


class EstagioUpdate(BaseModel):
    nome: str | None = None
    cor: str | None = None
    ordem: int | None = None
    ativo: bool | None = None


class EstagioResponse(BaseModel):
    id: UUID
    nome: str
    cor: str
    ordem: int
    ativo: bool
    created_at: datetime
    total_leads: int = 0

    class Config:
        from_attributes = True


class EstagioOrdemUpdate(BaseModel):
    estagios: list[dict]  # [{"id": "uuid", "ordem": 0}, ...]


# --- Leads ---

class LeadCreate(BaseModel):
    nome: str
    email: str | None = None
    telefone: str | None = None
    empresa: str | None = None
    documento: str | None = None
    estagio_id: UUID
    origem: str = "manual"
    valor_estimado: float | None = None
    plano_interesse: str | None = None
    qtd_fazendas: int | None = None
    qtd_usuarios: int | None = None
    responsavel_id: UUID | None = None
    notas: str | None = None
    tags: dict | None = None


class LeadUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None
    empresa: str | None = None
    documento: str | None = None
    estagio_id: UUID | None = None
    origem: str | None = None
    valor_estimado: float | None = None
    plano_interesse: str | None = None
    qtd_fazendas: int | None = None
    qtd_usuarios: int | None = None
    responsavel_id: UUID | None = None
    status: str | None = None
    motivo_perda: str | None = None
    notas: str | None = None
    tags: dict | None = None


class LeadMoveStage(BaseModel):
    estagio_id: UUID


class LeadConvert(BaseModel):
    tenant_convertido_id: UUID | None = None


class LeadLose(BaseModel):
    motivo_perda: str


class AtividadeCreate(BaseModel):
    tipo: str  # ligacao, email, reuniao, nota, tarefa, whatsapp
    descricao: str
    data_agendada: datetime | None = None


class AtividadeResponse(BaseModel):
    id: UUID
    lead_id: UUID
    tipo: str
    descricao: str
    data_agendada: datetime | None
    concluida: bool
    admin_user_id: UUID | None
    admin_email: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class LeadResponse(BaseModel):
    id: UUID
    nome: str
    email: str | None
    telefone: str | None
    empresa: str | None
    documento: str | None
    estagio_id: UUID
    origem: str
    valor_estimado: float | None
    plano_interesse: str | None
    qtd_fazendas: int | None
    qtd_usuarios: int | None
    responsavel_id: UUID | None
    status: str
    motivo_perda: str | None
    data_conversao: date | None
    tenant_convertido_id: UUID | None
    notas: str | None
    tags: dict | None
    created_at: datetime
    updated_at: datetime
    estagio: EstagioResponse | None = None
    atividades: list[AtividadeResponse] = []

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    total: int
    page: int
    page_size: int


class KanbanResponse(BaseModel):
    estagios: list[EstagioResponse]
    leads_por_estagio: dict[str, list[LeadResponse]]
    totais: dict[str, int]


class CRMStatsResponse(BaseModel):
    total_leads: int
    leads_ativos: int
    leads_convertidos: int
    leads_perdidos: int
    valor_pipeline: float
    por_origem: dict[str, int]
    por_estagio: dict[str, int]
    conversoes_mes: int


# ==================== ENDPOINTS - PIPELINE ====================

@router.get("/pipeline", response_model=List[EstagioResponse])
async def listar_estagios(
    ativo: bool | None = None,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Lista estágios do pipeline ordenados."""
    stmt = select(PipelineEstagio).order_by(PipelineEstagio.ordem)
    if ativo is not None:
        stmt = stmt.where(PipelineEstagio.ativo == ativo)

    result = await session.execute(stmt)
    estagios = result.scalars().all()

    # Contar leads por estágio
    count_result = await session.execute(
        select(LeadCRM.estagio_id, func.count(LeadCRM.id))
        .where(LeadCRM.status == "ativo")
        .group_by(LeadCRM.estagio_id)
    )
    counts = {str(row[0]): row[1] for row in count_result}

    response = []
    for e in estagios:
        resp = EstagioResponse.model_validate(e)
        resp.total_leads = counts.get(str(e.id), 0)
        response.append(resp)

    return response


@router.post(
    "/pipeline",
    response_model=EstagioResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("backoffice:crm:create"))],
)
async def criar_estagio(
    data: EstagioCreate,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Cria um novo estágio no pipeline."""
    estagio = PipelineEstagio(
        nome=data.nome,
        cor=data.cor,
        ordem=data.ordem,
    )
    session.add(estagio)
    await session.commit()
    await session.refresh(estagio)
    return EstagioResponse.model_validate(estagio)


@router.put(
    "/pipeline/{estagio_id}",
    response_model=EstagioResponse,
    dependencies=[Depends(require_permission("backoffice:crm:update"))],
)
async def atualizar_estagio(
    estagio_id: UUID,
    data: EstagioUpdate,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Atualiza um estágio."""
    estagio = await session.get(PipelineEstagio, estagio_id)
    if not estagio:
        raise HTTPException(status_code=404, detail="Estágio não encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(estagio, field, value)

    await session.commit()
    await session.refresh(estagio)
    return EstagioResponse.model_validate(estagio)


@router.put(
    "/pipeline/reorder",
    dependencies=[Depends(require_permission("backoffice:crm:update"))],
)
async def reordenar_estagios(
    data: EstagioOrdemUpdate,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Reordena os estágios do pipeline."""
    for item in data.estagios:
        await session.execute(
            update(PipelineEstagio)
            .where(PipelineEstagio.id == item["id"])
            .values(ordem=item["ordem"])
        )
    await session.commit()
    return {"ok": True}


# ==================== ENDPOINTS - STATS ====================

@router.get("/stats", response_model=CRMStatsResponse)
async def get_crm_stats(
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Estatísticas gerais do CRM."""
    total = await session.scalar(select(func.count(LeadCRM.id))) or 0
    ativos = await session.scalar(
        select(func.count(LeadCRM.id)).where(LeadCRM.status == "ativo")
    ) or 0
    convertidos = await session.scalar(
        select(func.count(LeadCRM.id)).where(LeadCRM.status == "convertido")
    ) or 0
    perdidos = await session.scalar(
        select(func.count(LeadCRM.id)).where(LeadCRM.status == "perdido")
    ) or 0

    valor = await session.scalar(
        select(func.coalesce(func.sum(LeadCRM.valor_estimado), 0))
        .where(LeadCRM.status == "ativo")
    ) or 0

    # Por origem
    result = await session.execute(
        select(LeadCRM.origem, func.count(LeadCRM.id))
        .group_by(LeadCRM.origem)
    )
    por_origem = {row[0]: row[1] for row in result}

    # Por estágio (com nome)
    result = await session.execute(
        select(PipelineEstagio.nome, func.count(LeadCRM.id))
        .join(PipelineEstagio, LeadCRM.estagio_id == PipelineEstagio.id)
        .where(LeadCRM.status == "ativo")
        .group_by(PipelineEstagio.nome)
    )
    por_estagio = {row[0]: row[1] for row in result}

    # Conversões do mês
    from datetime import timezone
    now = datetime.now(timezone.utc)
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    conversoes_mes = await session.scalar(
        select(func.count(LeadCRM.id))
        .where(LeadCRM.status == "convertido")
        .where(LeadCRM.data_conversao >= first_day.date())
    ) or 0

    return CRMStatsResponse(
        total_leads=total,
        leads_ativos=ativos,
        leads_convertidos=convertidos,
        leads_perdidos=perdidos,
        valor_pipeline=float(valor),
        por_origem=por_origem,
        por_estagio=por_estagio,
        conversoes_mes=conversoes_mes,
    )


# ==================== ENDPOINTS - KANBAN ====================

@router.get("/kanban", response_model=KanbanResponse)
async def get_kanban(
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Retorna dados para o board Kanban."""
    # Estágios ativos
    est_result = await session.execute(
        select(PipelineEstagio)
        .where(PipelineEstagio.ativo == True)
        .order_by(PipelineEstagio.ordem)
    )
    estagios = est_result.scalars().all()

    # Leads ativos com estágio
    leads_result = await session.execute(
        select(LeadCRM)
        .options(joinedload(LeadCRM.estagio))
        .where(LeadCRM.status == "ativo")
        .order_by(desc(LeadCRM.updated_at))
    )
    leads = leads_result.unique().scalars().all()

    # Agrupar por estágio
    leads_por_estagio: dict[str, list] = {}
    totais: dict[str, int] = {}

    for e in estagios:
        eid = str(e.id)
        stage_leads = [l for l in leads if str(l.estagio_id) == eid]
        leads_por_estagio[eid] = [LeadResponse.model_validate(l) for l in stage_leads]
        totais[eid] = len(stage_leads)

    return KanbanResponse(
        estagios=[EstagioResponse.model_validate(e) for e in estagios],
        leads_por_estagio=leads_por_estagio,
        totais=totais,
    )


# ==================== ENDPOINTS - LEADS ====================

@router.get("/leads", response_model=LeadListResponse)
async def listar_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=10, le=200),
    status_filtro: str | None = Query(None, alias="status"),
    estagio_id: UUID | None = None,
    origem: str | None = None,
    responsavel_id: UUID | None = None,
    busca: str | None = None,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Lista leads com filtros e paginação."""
    stmt = select(LeadCRM).options(joinedload(LeadCRM.estagio))
    count_stmt = select(func.count(LeadCRM.id))

    if status_filtro:
        stmt = stmt.where(LeadCRM.status == status_filtro)
        count_stmt = count_stmt.where(LeadCRM.status == status_filtro)
    if estagio_id:
        stmt = stmt.where(LeadCRM.estagio_id == estagio_id)
        count_stmt = count_stmt.where(LeadCRM.estagio_id == estagio_id)
    if origem:
        stmt = stmt.where(LeadCRM.origem == origem)
        count_stmt = count_stmt.where(LeadCRM.origem == origem)
    if responsavel_id:
        stmt = stmt.where(LeadCRM.responsavel_id == responsavel_id)
        count_stmt = count_stmt.where(LeadCRM.responsavel_id == responsavel_id)
    if busca:
        pattern = f"%{busca}%"
        stmt = stmt.where(
            LeadCRM.nome.ilike(pattern)
            | LeadCRM.email.ilike(pattern)
            | LeadCRM.empresa.ilike(pattern)
            | LeadCRM.telefone.ilike(pattern)
        )
        count_stmt = count_stmt.where(
            LeadCRM.nome.ilike(pattern)
            | LeadCRM.email.ilike(pattern)
            | LeadCRM.empresa.ilike(pattern)
            | LeadCRM.telefone.ilike(pattern)
        )

    total = await session.scalar(count_stmt) or 0

    offset = (page - 1) * page_size
    stmt = stmt.order_by(desc(LeadCRM.updated_at)).offset(offset).limit(page_size)

    result = await session.execute(stmt)
    leads = result.unique().scalars().all()

    return LeadListResponse(
        items=[LeadResponse.model_validate(l) for l in leads],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Retorna um lead com atividades."""
    result = await session.execute(
        select(LeadCRM)
        .options(
            joinedload(LeadCRM.estagio),
            joinedload(LeadCRM.atividades),
        )
        .where(LeadCRM.id == lead_id)
    )
    lead = result.unique().scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return lead


@router.post(
    "/leads",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("backoffice:crm:create"))],
)
async def criar_lead(
    data: LeadCreate,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Cria um novo lead."""
    # Verificar estágio existe
    estagio = await session.get(PipelineEstagio, data.estagio_id)
    if not estagio:
        raise HTTPException(status_code=400, detail="Estágio não encontrado")

    lead = LeadCRM(**data.model_dump())
    session.add(lead)
    await session.commit()
    await session.refresh(lead, ["estagio"])
    return lead


@router.put(
    "/leads/{lead_id}",
    response_model=LeadResponse,
    dependencies=[Depends(require_permission("backoffice:crm:update"))],
)
async def atualizar_lead(
    lead_id: UUID,
    data: LeadUpdate,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Atualiza dados de um lead."""
    lead = await session.get(LeadCRM, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)

    await session.commit()
    await session.refresh(lead, ["estagio"])
    return lead


@router.patch(
    "/leads/{lead_id}/move",
    response_model=LeadResponse,
    dependencies=[Depends(require_permission("backoffice:crm:update"))],
)
async def mover_lead(
    lead_id: UUID,
    data: LeadMoveStage,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Move lead para outro estágio (drag & drop do Kanban)."""
    lead = await session.get(LeadCRM, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    estagio = await session.get(PipelineEstagio, data.estagio_id)
    if not estagio:
        raise HTTPException(status_code=400, detail="Estágio não encontrado")

    lead.estagio_id = data.estagio_id
    await session.commit()
    await session.refresh(lead, ["estagio"])
    return lead


@router.patch(
    "/leads/{lead_id}/convert",
    response_model=LeadResponse,
    dependencies=[Depends(require_permission("backoffice:crm:update"))],
)
async def converter_lead(
    lead_id: UUID,
    data: LeadConvert,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Marca lead como convertido."""
    lead = await session.get(LeadCRM, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    lead.status = "convertido"
    lead.data_conversao = date.today()
    if data.tenant_convertido_id:
        lead.tenant_convertido_id = data.tenant_convertido_id

    await session.commit()
    await session.refresh(lead, ["estagio"])
    return lead


@router.patch(
    "/leads/{lead_id}/lose",
    response_model=LeadResponse,
    dependencies=[Depends(require_permission("backoffice:crm:update"))],
)
async def perder_lead(
    lead_id: UUID,
    data: LeadLose,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Marca lead como perdido."""
    lead = await session.get(LeadCRM, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    lead.status = "perdido"
    lead.motivo_perda = data.motivo_perda

    await session.commit()
    await session.refresh(lead, ["estagio"])
    return lead


@router.patch(
    "/leads/{lead_id}/reopen",
    response_model=LeadResponse,
    dependencies=[Depends(require_permission("backoffice:crm:update"))],
)
async def reabrir_lead(
    lead_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Reabre um lead perdido ou convertido."""
    lead = await session.get(LeadCRM, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    lead.status = "ativo"
    lead.motivo_perda = None
    lead.data_conversao = None
    lead.tenant_convertido_id = None

    await session.commit()
    await session.refresh(lead, ["estagio"])
    return lead


@router.patch(
    "/leads/{lead_id}/approve",
    response_model=LeadResponse,
    dependencies=[Depends(require_permission("backoffice:crm:update"))],
)
async def aprovar_lead(
    lead_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Aprova um lead ativo, habilitando-o para conversão em tenant."""
    lead = await session.get(LeadCRM, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    if lead.status != "ativo":
        raise HTTPException(status_code=422, detail=f"Somente leads com status 'ativo' podem ser aprovados. Status atual: '{lead.status}'")

    lead.status = "aprovado"

    await session.commit()
    await session.refresh(lead, ["estagio"])
    return lead


# ==================== ENDPOINTS - ATIVIDADES ====================

@router.get("/leads/{lead_id}/atividades", response_model=List[AtividadeResponse])
async def listar_atividades(
    lead_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Lista atividades de um lead."""
    result = await session.execute(
        select(AtividadeCRM)
        .where(AtividadeCRM.lead_id == lead_id)
        .order_by(desc(AtividadeCRM.created_at))
    )
    return result.scalars().all()


@router.post(
    "/leads/{lead_id}/atividades",
    response_model=AtividadeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("backoffice:crm:create"))],
)
async def criar_atividade(
    lead_id: UUID,
    data: AtividadeCreate,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Registra uma atividade no lead."""
    lead = await session.get(LeadCRM, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    atividade = AtividadeCRM(
        lead_id=lead_id,
        tipo=data.tipo,
        descricao=data.descricao,
        data_agendada=data.data_agendada,
        admin_user_id=UUID(current_admin["admin_id"]) if current_admin.get("admin_id") else None,
        admin_email=current_admin.get("email"),
    )

    session.add(atividade)
    await session.commit()
    await session.refresh(atividade)
    return atividade


@router.patch(
    "/atividades/{atividade_id}/toggle",
    response_model=AtividadeResponse,
    dependencies=[Depends(require_permission("backoffice:crm:update"))],
)
async def toggle_atividade(
    atividade_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Marca/desmarca atividade como concluída."""
    atividade = await session.get(AtividadeCRM, atividade_id)
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    atividade.concluida = not atividade.concluida
    await session.commit()
    await session.refresh(atividade)
    return atividade


@router.delete(
    "/atividades/{atividade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("backoffice:crm:delete"))],
)
async def deletar_atividade(
    atividade_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Remove uma atividade."""
    atividade = await session.get(AtividadeCRM, atividade_id)
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    await session.delete(atividade)
    await session.commit()
