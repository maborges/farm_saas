"""
Router de Integrações Financeiras:
  - Contas Bancárias + importação OFX
  - Conciliação bancária
  - Exportação Carnê-Leão (RFB)
  - Resumo API Contábil
"""
import uuid
from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import io

from core.dependencies import get_session, get_tenant_id, require_module
from financeiro.services.integracao_service import (
    ConciliacaoService,
    CarneLeaoService,
    ContabilService,
)

router = APIRouter(
    prefix="/integracao",
    tags=["Financeiro - Integrações (F1)"],
    dependencies=[Depends(require_module("F1_TESOURARIA"))],
)


# ── Schemas inline ────────────────────────────────────────────────────────────

class ContaBancariaCreate(BaseModel):
    nome: str
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    tipo: str = "CORRENTE"
    fazenda_id: Optional[uuid.UUID] = None


class ContaBancariaResponse(BaseModel):
    id: uuid.UUID
    nome: str
    banco: Optional[str]
    agencia: Optional[str]
    conta: Optional[str]
    tipo: str
    ativa: bool
    fazenda_id: Optional[uuid.UUID]

    model_config = {"from_attributes": True}


class LancamentoBancarioResponse(BaseModel):
    id: uuid.UUID
    conta_id: uuid.UUID
    data: date
    valor: float
    descricao: Optional[str]
    tipo: str
    status_conciliacao: str
    id_ofx: Optional[str]
    despesa_id: Optional[uuid.UUID]
    receita_id: Optional[uuid.UUID]

    model_config = {"from_attributes": True}


class ConciliarRequest(BaseModel):
    despesa_id: Optional[uuid.UUID] = None
    receita_id: Optional[uuid.UUID] = None


# ── Contas Bancárias ──────────────────────────────────────────────────────────

@router.post("/contas-bancarias", response_model=ContaBancariaResponse, status_code=201)
async def criar_conta_bancaria(
    dados: ContaBancariaCreate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    svc = ConciliacaoService(db, tenant_id)
    conta = await svc.criar_conta(dados.model_dump())
    await db.commit()
    await db.refresh(conta)
    return conta


@router.get("/contas-bancarias", response_model=List[ContaBancariaResponse])
async def listar_contas_bancarias(
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    svc = ConciliacaoService(db, tenant_id)
    return await svc.listar_contas()


# ── Importação OFX ────────────────────────────────────────────────────────────

@router.post("/contas-bancarias/{conta_id}/importar-ofx")
async def importar_ofx(
    conta_id: uuid.UUID,
    arquivo: UploadFile = File(...),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    content_bytes = await arquivo.read()
    # Tenta UTF-8 com fallback para latin-1 (bancos brasileiros legados)
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content = content_bytes.decode("latin-1")

    svc = ConciliacaoService(db, tenant_id)
    resultado = await svc.importar_ofx(conta_id, content)
    await db.commit()
    return resultado


# ── Lançamentos e Conciliação ─────────────────────────────────────────────────

@router.get("/contas-bancarias/{conta_id}/lancamentos", response_model=List[LancamentoBancarioResponse])
async def listar_lancamentos(
    conta_id: uuid.UUID,
    status: Optional[str] = Query(None, description="NAO_CONCILIADO | CONCILIADO | IGNORADO"),
    data_de: Optional[date] = Query(None),
    data_ate: Optional[date] = Query(None),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    svc = ConciliacaoService(db, tenant_id)
    return await svc.listar_lancamentos(conta_id, status=status, data_de=data_de, data_ate=data_ate)


@router.get("/contas-bancarias/{conta_id}/sugestoes")
async def sugestoes_conciliacao(
    conta_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    svc = ConciliacaoService(db, tenant_id)
    return await svc.sugerir_conciliacao(conta_id)


@router.patch("/lancamentos/{lancamento_id}/conciliar", response_model=LancamentoBancarioResponse)
async def conciliar_lancamento(
    lancamento_id: uuid.UUID,
    dados: ConciliarRequest,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    if not dados.despesa_id and not dados.receita_id:
        raise HTTPException(status_code=422, detail="Informe despesa_id ou receita_id para conciliar.")
    svc = ConciliacaoService(db, tenant_id)
    lanc = await svc.conciliar(lancamento_id, despesa_id=dados.despesa_id, receita_id=dados.receita_id)
    await db.commit()
    await db.refresh(lanc)
    return lanc


@router.patch("/lancamentos/{lancamento_id}/ignorar", response_model=LancamentoBancarioResponse)
async def ignorar_lancamento(
    lancamento_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    from sqlalchemy.future import select
    from financeiro.models.conciliacao import LancamentoBancario
    from core.exceptions import EntityNotFoundError

    stmt = select(LancamentoBancario).where(
        LancamentoBancario.id == lancamento_id,
        LancamentoBancario.tenant_id == tenant_id,
    )
    lanc = (await db.execute(stmt)).scalar_one_or_none()
    if not lanc:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado.")
    lanc.status_conciliacao = "IGNORADO"
    db.add(lanc)
    await db.commit()
    await db.refresh(lanc)
    return lanc


# ── Carnê-Leão ────────────────────────────────────────────────────────────────

@router.get("/carne-leao/exportar")
async def exportar_carne_leao(
    ano: int = Query(..., description="Ano de competência (ex: 2024)"),
    fazenda_id: Optional[uuid.UUID] = Query(None),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    svc = CarneLeaoService(db, tenant_id)
    csv_content = await svc.exportar_csv(ano, fazenda_id=fazenda_id)
    filename = f"carne_leao_{ano}.csv"
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── API Contábil ─────────────────────────────────────────────────────────────

@router.get("/contabil/resumo")
async def resumo_contabil(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    fazenda_id: Optional[uuid.UUID] = Query(None),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_session),
):
    svc = ContabilService(db, tenant_id)
    return await svc.resumo(data_inicio, data_fim, fazenda_id=fazenda_id)
