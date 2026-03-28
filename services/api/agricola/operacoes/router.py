from fastapi import APIRouter, Depends, status, BackgroundTasks, Response
from typing import List
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, require_role
from core.dependencies import get_session_with_tenant
from core.utils.pdf_generator import generate_caderno_campo_pdf
from agricola.operacoes.schemas import (
    OperacaoAgricolaCreate, OperacaoAgricolaResponse, OperacaoAgricolaUpdate,
    SafraOperacoesPorFaseResponse,
)
from agricola.operacoes.service import OperacaoService

router = APIRouter(prefix="/operacoes", tags=["Operações Agrícolas"])

# ... (outros endpoints)

@router.get(
    "/export/pdf",
    summary="Exporta caderno de campo em PDF",
)
async def exportar_caderno_pdf(
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = OperacaoService(session, tenant_id)
    operacoes = await svc.list_all()
    
    # Prepara dados para o PDF
    data_list = []
    for op in operacoes:
        data_list.append({
            "data_realizada": op.data_realizada.strftime("%d/%m/%Y"),
            "tipo": op.tipo,
            "talhao_id": str(op.talhao_id),
            "area_aplicada_ha": float(op.area_aplicada_ha or 0),
            "custo_total": float(op.custo_total or 0),
            "status": op.status
        })
    
    pdf_content = generate_caderno_campo_pdf(data_list)
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Caderno_Campo.pdf"}
    )

def verificar_alertas_pos_operacao(operacao_id: UUID, tenant_id: UUID):
    # Dummy worker task
    pass

@router.post(
    "/",
    response_model=OperacaoAgricolaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra operação agrícola no caderno de campo",
    description="""
    Registra uma operação realizada no talhão (plantio, aplicação de defensivo,
    adubação, etc.). Automaticamente:
    - Baixa insumos do estoque
    - Calcula custo da operação
    - Atualiza custo realizado da safra
    - Detecta carência de defensivos
    - Busca condições climáticas do momento (se lat/lng fornecidos)
    """,
)
async def criar_operacao(
    dados: OperacaoAgricolaCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
    user: dict = Depends(require_role(["agronomo", "admin", "operador"])),
):
    svc = OperacaoService(session, tenant_id)
    operacao = await svc.criar(dados)
    # Task em background — não bloqueia a resposta
    background_tasks.add_task(
        verificar_alertas_pos_operacao,
        operacao_id=operacao.id,
        tenant_id=tenant_id,
    )
    return OperacaoAgricolaResponse.model_validate(operacao)


@router.get(
    "/",
    response_model=List[OperacaoAgricolaResponse],
    summary="Lista operações agrícolas",
)
async def listar_operacoes(
    safra_id: UUID | None = None,
    tipo: str | None = None,
    # data_inicio: date | None = None,
    # data_fim: date | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = OperacaoService(session, tenant_id)
    # Apply standard get_all for exact matches right now
    filters = {}
    if safra_id: filters["safra_id"] = safra_id
    if tipo: filters["tipo"] = tipo
    
    operacoes = await svc.list_all(**filters)
    return [OperacaoAgricolaResponse.model_validate(o) for o in operacoes]

@router.get(
    "/{id}",
    response_model=OperacaoAgricolaResponse,
    summary="Detalhes da operação",
)
async def detalhar_operacao(
    id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = OperacaoService(session, tenant_id)
    operacao = await svc.get_or_fail(id)
    return OperacaoAgricolaResponse.model_validate(operacao)

@router.get(
    "/safra/{safra_id}/por-fase",
    response_model=SafraOperacoesPorFaseResponse,
    summary="KPIs e custo de operações agrupados por fase da safra",
)
async def operacoes_por_fase(
    safra_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = OperacaoService(session, tenant_id)
    return await svc.resumo_por_fase(safra_id)


@router.get(
    "/safra/{safra_id}/fase/{fase}",
    response_model=List[OperacaoAgricolaResponse],
    summary="Lista operações de uma fase específica da safra",
)
async def operacoes_de_fase(
    safra_id: UUID,
    fase: str,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = OperacaoService(session, tenant_id)
    ops = await svc.listar_por_safra_e_fase(safra_id, fase.upper())
    return [OperacaoAgricolaResponse.model_validate(o) for o in ops]


@router.patch(
    "/{id}",
    response_model=OperacaoAgricolaResponse,
    summary="Atualiza dados da operação",
)
async def atualizar_operacao(
    id: UUID,
    dados: OperacaoAgricolaUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = OperacaoService(session, tenant_id)
    operacao = await svc.atualizar(id, dados)
    return OperacaoAgricolaResponse.model_validate(operacao)
