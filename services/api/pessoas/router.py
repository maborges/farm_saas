import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from core.dependencies import get_session_with_tenant, get_tenant_id, require_tenant_permission
from pessoas.models import Pessoa
from pessoas.schemas.pessoa import PessoaCreate, PessoaUpdate, PessoaResponse, PessoaListItem
from pessoas.service import PessoaService

router = APIRouter(
    prefix="/pessoas",
    tags=["Pessoas"],
)


@router.get(
    "/",
    response_model=list[PessoaListItem],
    dependencies=[Depends(require_tenant_permission("tenant:fazendas:view"))],
    summary="Listar pessoas",
)
async def listar_pessoas(
    tipo: str | None = Query(None, description="FORNECEDOR, CLIENTE, FUNCIONARIO, PARCEIRO, PRESTADOR"),
    ativo: bool | None = Query(None),
    search: str | None = Query(None, min_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
):
    service = PessoaService(session, tenant_id)
    return await service.list_by_tipo(tipo=tipo, ativo=ativo, search=search, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=PessoaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_tenant_permission("tenant:fazendas:view"))],
    summary="Cadastrar pessoa",
)
async def criar_pessoa(
    data: PessoaCreate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
):
    service = PessoaService(session, tenant_id)

    # Verificar duplicata por CPF/CNPJ
    if data.cpf_cnpj:
        existente = await service.buscar_por_cpf_cnpj(data.cpf_cnpj)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe uma pessoa cadastrada com o documento {data.cpf_cnpj}",
            )

    pessoa = await service.criar(data)
    await session.commit()
    await session.refresh(pessoa)
    logger.info(f"Pessoa criada: {pessoa.id} ({pessoa.nome}) tenant={tenant_id}")
    return pessoa


@router.get(
    "/{pessoa_id}",
    response_model=PessoaResponse,
    dependencies=[Depends(require_tenant_permission("tenant:fazendas:view"))],
    summary="Buscar pessoa por ID",
)
async def buscar_pessoa(
    pessoa_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
):
    service = PessoaService(session, tenant_id)
    return await service.get_or_fail(pessoa_id)


@router.patch(
    "/{pessoa_id}",
    response_model=PessoaResponse,
    dependencies=[Depends(require_tenant_permission("tenant:fazendas:view"))],
    summary="Atualizar pessoa",
)
async def atualizar_pessoa(
    pessoa_id: uuid.UUID,
    data: PessoaUpdate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
):
    service = PessoaService(session, tenant_id)
    pessoa = await service.atualizar(pessoa_id, data)
    await session.commit()
    await session.refresh(pessoa)
    return pessoa


@router.delete(
    "/{pessoa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_tenant_permission("tenant:fazendas:view"))],
    summary="Inativar pessoa (soft delete)",
)
async def inativar_pessoa(
    pessoa_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
):
    """Inativa a pessoa em vez de deletar para preservar histórico em lançamentos."""
    service = PessoaService(session, tenant_id)
    pessoa = await service.get_or_fail(pessoa_id)
    await service.update(pessoa, {"ativo": False})
    await session.commit()


@router.get(
    "/por-documento/{cpf_cnpj}",
    response_model=PessoaResponse,
    dependencies=[Depends(require_tenant_permission("tenant:fazendas:view"))],
    summary="Buscar pessoa por CPF/CNPJ",
)
async def buscar_por_documento(
    cpf_cnpj: str,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session_with_tenant),
):
    service = PessoaService(session, tenant_id)
    pessoa = await service.buscar_por_cpf_cnpj(cpf_cnpj)
    if not pessoa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pessoa não encontrada")
    return pessoa
