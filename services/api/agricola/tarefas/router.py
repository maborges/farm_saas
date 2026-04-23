from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_session_with_tenant, get_tenant_id, require_module, require_role
from agricola.tarefas.schemas import TarefaCreate, TarefaUpdate, TarefaResponse
from agricola.tarefas.service import TarefaService

router = APIRouter(tags=["Agrícola - Tarefas (A2)"])
MODULE = "A2_CAMPO"


@router.get(
    "/safras/{safra_id}/tarefas",
    response_model=List[TarefaResponse],
    summary="Lista tarefas planejadas da safra",
)
async def listar_tarefas(
    safra_id: UUID,
    status: Optional[str] = Query(None),
    talhao_id: Optional[UUID] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = TarefaService(session, tenant_id)
    return await svc.listar(safra_id, status=status, talhao_id=talhao_id)


@router.post(
    "/safras/{safra_id}/tarefas",
    response_model=TarefaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria tarefa manual (nasce APROVADA)",
)
async def criar_tarefa(
    safra_id: UUID,
    dados: TarefaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
    user: dict = Depends(require_role(["agronomo", "admin", "gerente"])),
):
    svc = TarefaService(session, tenant_id)
    user_id = UUID(user["sub"]) if user.get("sub") else None
    dados.origem = "MANUAL"
    tarefa = await svc.criar(safra_id, dados, user_id=user_id)
    await session.commit()
    await session.refresh(tarefa)
    return tarefa


@router.get(
    "/tarefas/{tarefa_id}",
    response_model=TarefaResponse,
    summary="Detalha uma tarefa",
)
async def detalhar_tarefa(
    tarefa_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
):
    svc = TarefaService(session, tenant_id)
    return await svc.get(tarefa_id)


@router.patch(
    "/tarefas/{tarefa_id}",
    response_model=TarefaResponse,
    summary="Atualiza dados da tarefa",
)
async def atualizar_tarefa(
    tarefa_id: UUID,
    dados: TarefaUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
    user: dict = Depends(require_role(["agronomo", "admin", "gerente"])),
):
    svc = TarefaService(session, tenant_id)
    tarefa = await svc.atualizar(tarefa_id, dados)
    await session.commit()
    await session.refresh(tarefa)
    return tarefa


@router.patch(
    "/tarefas/{tarefa_id}/aprovar",
    response_model=TarefaResponse,
    summary="Aprova tarefa pendente",
)
async def aprovar_tarefa(
    tarefa_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
    user: dict = Depends(require_role(["agronomo", "admin", "gerente"])),
):
    svc = TarefaService(session, tenant_id)
    aprovador_id = UUID(user["sub"]) if user.get("sub") else tenant_id
    tarefa = await svc.aprovar(tarefa_id, aprovador_id)
    await session.commit()
    await session.refresh(tarefa)
    return tarefa


@router.delete(
    "/tarefas/{tarefa_id}/rejeitar",
    response_model=TarefaResponse,
    summary="Rejeita/cancela tarefa",
)
async def rejeitar_tarefa(
    tarefa_id: UUID,
    motivo: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
    user: dict = Depends(require_role(["agronomo", "admin", "gerente"])),
):
    svc = TarefaService(session, tenant_id)
    user_id = UUID(user["sub"]) if user.get("sub") else None
    tarefa = await svc.rejeitar(tarefa_id, motivo=motivo, user_id=user_id)
    await session.commit()
    await session.refresh(tarefa)
    return tarefa


@router.patch(
    "/tarefas/{tarefa_id}/iniciar",
    response_model=TarefaResponse,
    summary="Marca tarefa como em execução",
)
async def iniciar_tarefa(
    tarefa_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
    user: dict = Depends(require_role(["agronomo", "admin", "gerente", "operador"])),
):
    svc = TarefaService(session, tenant_id)
    tarefa = await svc.iniciar(tarefa_id)
    await session.commit()
    await session.refresh(tarefa)
    return tarefa


@router.patch(
    "/tarefas/{tarefa_id}/concluir",
    response_model=TarefaResponse,
    summary="Conclui tarefa manualmente",
)
async def concluir_tarefa(
    tarefa_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
    user: dict = Depends(require_role(["agronomo", "admin", "gerente", "operador"])),
):
    svc = TarefaService(session, tenant_id)
    tarefa = await svc.concluir(tarefa_id)
    await session.commit()
    await session.refresh(tarefa)
    return tarefa


@router.delete(
    "/tarefas/{tarefa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancela/remove tarefa",
)
async def cancelar_tarefa(
    tarefa_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module(MODULE)),
    user: dict = Depends(require_role(["agronomo", "admin"])),
):
    svc = TarefaService(session, tenant_id)
    await svc.rejeitar(tarefa_id)
    await session.commit()
