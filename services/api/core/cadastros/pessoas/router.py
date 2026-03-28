import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional
from fastapi import Request
from core.dependencies import get_session, get_tenant_id, get_current_user
from .models import TipoRelacionamento, Pessoa
from .schemas import (
    PessoaCreate, PessoaUpdate, PessoaResponse, PessoaComPIIResponse,
    PessoaPIIUpdate, PessoaPIIResponse,
    EnderecoCreate, EnderecoUpdate, EnderecoResponse,
    ContatoCreate, ContatoUpdate, ContatoResponse,
    BancarioCreate, BancarioUpdate, BancarioResponse,
    RelacionamentoCreate, RelacionamentoResponse,
    TipoRelacionamentoCreate, TipoRelacionamentoResponse,
    ConsentimentoCreate, ConsentimentoResponse,
)
from .service import PessoaService, TipoRelacionamentoService

router = APIRouter(prefix="/cadastros/pessoas", tags=["Cadastros — Pessoas"])
router_tipos = APIRouter(prefix="/cadastros/tipos-relacionamento", tags=["Cadastros — Tipos de Relacionamento"])


def get_optional_tenant_id(request: Request) -> Optional[uuid.UUID]:
    """Retorna tenant_id do JWT se disponível, None caso contrário (sem exigir auth)."""
    try:
        from core.dependencies import get_token, get_current_user_claims
        from jose import jwt
        from core.config import settings
        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return None
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        tid = payload.get("tenant_id")
        return uuid.UUID(tid) if tid else None
    except Exception:
        return None


def _svc(session: AsyncSession, tenant_id: uuid.UUID) -> PessoaService:
    return PessoaService(Pessoa, session, tenant_id)


def _svc_tipo(session: AsyncSession, tenant_id: uuid.UUID) -> TipoRelacionamentoService:
    return TipoRelacionamentoService(TipoRelacionamento, session, tenant_id)


# ── Tipos de Relacionamento ───────────────────────────────────────────────────

@router_tipos.get("", response_model=list[TipoRelacionamentoResponse])
async def listar_tipos(
    session: AsyncSession = Depends(get_session),
    tenant_id: Optional[uuid.UUID] = Depends(get_optional_tenant_id),
):
    return await _svc_tipo(session, tenant_id).listar()


@router_tipos.post("", response_model=TipoRelacionamentoResponse, status_code=201)
async def criar_tipo(
    data: TipoRelacionamentoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc_tipo(session, tenant_id).criar_custom(data.model_dump())


@router_tipos.delete("/{tipo_id}", status_code=204)
async def desativar_tipo(
    tipo_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _svc_tipo(session, tenant_id).desativar(tipo_id)


# ── Pessoas ───────────────────────────────────────────────────────────────────

@router.get("", response_model=list[PessoaResponse])
async def listar_pessoas(
    tipo: str | None = Query(None),
    ativo: bool = Query(True),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).listar(tipo=tipo, ativo=ativo)


@router.post("", response_model=PessoaResponse, status_code=201)
async def criar_pessoa(
    data: PessoaCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).criar(data)


@router.get("/{pessoa_id}", response_model=PessoaResponse)
async def obter_pessoa(
    pessoa_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id)._get_pessoa(pessoa_id)


@router.patch("/{pessoa_id}", response_model=PessoaResponse)
async def atualizar_pessoa(
    pessoa_id: uuid.UUID,
    data: PessoaUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).atualizar(pessoa_id, data)


@router.post("/{pessoa_id}/anonimizar", response_model=PessoaResponse)
async def anonimizar_pessoa(
    pessoa_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).anonimizar(pessoa_id)


# ── PII (acesso restrito + audit log) ────────────────────────────────────────

@router.get("/{pessoa_id}/pii", response_model=PessoaPIIResponse)
async def obter_pii(
    pessoa_id: uuid.UUID,
    motivo: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
):
    pii = await _svc(session, tenant_id).obter_pii(
        pessoa_id, current_user.get("sub"), motivo
    )
    if not pii:
        raise HTTPException(status_code=404, detail="PII não encontrada")
    return pii


@router.patch("/{pessoa_id}/pii", response_model=PessoaPIIResponse)
async def atualizar_pii(
    pessoa_id: uuid.UUID,
    data: PessoaPIIUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).atualizar_pii(pessoa_id, data)


# ── Endereços ─────────────────────────────────────────────────────────────────

@router.get("/{pessoa_id}/enderecos", response_model=list[EnderecoResponse])
async def listar_enderecos(
    pessoa_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).listar_enderecos(pessoa_id)


@router.post("/{pessoa_id}/enderecos", response_model=EnderecoResponse, status_code=201)
async def adicionar_endereco(
    pessoa_id: uuid.UUID,
    data: EnderecoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).adicionar_endereco(pessoa_id, data)


@router.patch("/{pessoa_id}/enderecos/{endereco_id}", response_model=EnderecoResponse)
async def atualizar_endereco(
    pessoa_id: uuid.UUID,
    endereco_id: uuid.UUID,
    data: EnderecoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).atualizar_endereco(pessoa_id, endereco_id, data)


@router.delete("/{pessoa_id}/enderecos/{endereco_id}", status_code=204)
async def remover_endereco(
    pessoa_id: uuid.UUID,
    endereco_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _svc(session, tenant_id).remover_endereco(pessoa_id, endereco_id)


# ── Contatos ──────────────────────────────────────────────────────────────────

@router.get("/{pessoa_id}/contatos", response_model=list[ContatoResponse])
async def listar_contatos(
    pessoa_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).listar_contatos(pessoa_id)


@router.post("/{pessoa_id}/contatos", response_model=ContatoResponse, status_code=201)
async def adicionar_contato(
    pessoa_id: uuid.UUID,
    data: ContatoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).adicionar_contato(pessoa_id, data)


@router.patch("/{pessoa_id}/contatos/{contato_id}", response_model=ContatoResponse)
async def atualizar_contato(
    pessoa_id: uuid.UUID,
    contato_id: uuid.UUID,
    data: ContatoUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).atualizar_contato(pessoa_id, contato_id, data)


@router.delete("/{pessoa_id}/contatos/{contato_id}", status_code=204)
async def remover_contato(
    pessoa_id: uuid.UUID,
    contato_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _svc(session, tenant_id).remover_contato(pessoa_id, contato_id)


# ── Dados Bancários ───────────────────────────────────────────────────────────

@router.get("/{pessoa_id}/bancario", response_model=list[BancarioResponse])
async def listar_bancario(
    pessoa_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).listar_bancario(pessoa_id)


@router.post("/{pessoa_id}/bancario", response_model=BancarioResponse, status_code=201)
async def adicionar_bancario(
    pessoa_id: uuid.UUID,
    data: BancarioCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).adicionar_bancario(pessoa_id, data)


@router.patch("/{pessoa_id}/bancario/{bancario_id}", response_model=BancarioResponse)
async def atualizar_bancario(
    pessoa_id: uuid.UUID,
    bancario_id: uuid.UUID,
    data: BancarioUpdate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).atualizar_bancario(pessoa_id, bancario_id, data)


@router.delete("/{pessoa_id}/bancario/{bancario_id}", status_code=204)
async def remover_bancario(
    pessoa_id: uuid.UUID,
    bancario_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _svc(session, tenant_id).remover_bancario(pessoa_id, bancario_id)


# ── Relacionamentos ───────────────────────────────────────────────────────────

@router.post("/{pessoa_id}/relacionamentos", response_model=RelacionamentoResponse, status_code=201)
async def adicionar_relacionamento(
    pessoa_id: uuid.UUID,
    data: RelacionamentoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).adicionar_relacionamento(pessoa_id, data)


@router.delete("/{pessoa_id}/relacionamentos/{rel_id}", status_code=204)
async def remover_relacionamento(
    pessoa_id: uuid.UUID,
    rel_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    await _svc(session, tenant_id).remover_relacionamento(pessoa_id, rel_id)


# ── Consentimentos ────────────────────────────────────────────────────────────

@router.post("/{pessoa_id}/consentimentos", response_model=ConsentimentoResponse, status_code=201)
async def registrar_consentimento(
    pessoa_id: uuid.UUID,
    data: ConsentimentoCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await _svc(session, tenant_id).registrar_consentimento(pessoa_id, data)
