from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from datetime import date

from core.dependencies import get_session, get_current_admin
from core.models.cupom import Cupom
from pydantic import BaseModel

router = APIRouter(prefix="/backoffice/cupons", tags=["Backoffice - Cupons"])


# Schemas
class CupomCreate(BaseModel):
    codigo: str
    tipo: str  # percentual, valor_fixo
    valor: float
    aplicavel_em: str
    duracao_meses: int | None = None
    uso_maximo: int = 1
    uso_por_cliente: int = 1
    data_inicio: date
    data_fim: date
    ativo: bool = True


class CupomResponse(BaseModel):
    id: uuid.UUID
    codigo: str
    tipo: str
    valor: float
    aplicavel_em: str
    uso_maximo: int
    uso_atual: int
    uso_por_cliente: int
    data_inicio: date
    data_fim: date
    ativo: bool
    pode_ser_usado: bool

    class Config:
        from_attributes = True


# Endpoints
@router.post("", response_model=CupomResponse, dependencies=[Depends(get_current_admin)])
async def criar_cupom(
    data: CupomCreate,
    session: AsyncSession = Depends(get_session)
):
    """Cria um novo cupom de desconto."""
    # Verificar se código já existe
    stmt = select(Cupom).where(Cupom.codigo == data.codigo.upper())
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de cupom já existe"
        )

    cupom = Cupom(
        codigo=data.codigo.upper(),
        tipo=data.tipo,
        valor=data.valor,
        aplicavel_em=data.aplicavel_em,
        duracao_meses=data.duracao_meses,
        uso_maximo=data.uso_maximo,
        uso_por_cliente=data.uso_por_cliente,
        data_inicio=data.data_inicio,
        data_fim=data.data_fim,
        ativo=data.ativo
    )

    session.add(cupom)
    await session.commit()
    await session.refresh(cupom)

    return CupomResponse(
        id=cupom.id,
        codigo=cupom.codigo,
        tipo=cupom.tipo,
        valor=cupom.valor,
        aplicavel_em=cupom.aplicavel_em,
        uso_maximo=cupom.uso_maximo,
        uso_atual=cupom.uso_atual,
        uso_por_cliente=cupom.uso_por_cliente,
        data_inicio=cupom.data_inicio,
        data_fim=cupom.data_fim,
        ativo=cupom.ativo,
        pode_ser_usado=cupom.pode_ser_usado()
    )


@router.get("", response_model=List[CupomResponse], dependencies=[Depends(get_current_admin)])
async def listar_cupons(
    apenas_ativos: bool = False,
    session: AsyncSession = Depends(get_session)
):
    """Lista todos os cupons."""
    stmt = select(Cupom)

    if apenas_ativos:
        stmt = stmt.where(Cupom.ativo == True)

    stmt = stmt.order_by(Cupom.created_at.desc())
    result = await session.execute(stmt)
    cupons = result.scalars().all()

    return [
        CupomResponse(
            id=cupom.id,
            codigo=cupom.codigo,
            tipo=cupom.tipo,
            valor=cupom.valor,
            aplicavel_em=cupom.aplicavel_em,
            uso_maximo=cupom.uso_maximo,
            uso_atual=cupom.uso_atual,
            uso_por_cliente=cupom.uso_por_cliente,
            data_inicio=cupom.data_inicio,
            data_fim=cupom.data_fim,
            ativo=cupom.ativo,
            pode_ser_usado=cupom.pode_ser_usado()
        )
        for cupom in cupons
    ]


@router.get("/{cupom_id}", response_model=CupomResponse, dependencies=[Depends(get_current_admin)])
async def obter_cupom(
    cupom_id: uuid.UUID,
    session: AsyncSession = Depends(get_session)
):
    """Retorna detalhes de um cupom."""
    cupom = await session.get(Cupom, cupom_id)
    if not cupom:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")

    return CupomResponse(
        id=cupom.id,
        codigo=cupom.codigo,
        tipo=cupom.tipo,
        valor=cupom.valor,
        aplicavel_em=cupom.aplicavel_em,
        uso_maximo=cupom.uso_maximo,
        uso_atual=cupom.uso_atual,
        uso_por_cliente=cupom.uso_por_cliente,
        data_inicio=cupom.data_inicio,
        data_fim=cupom.data_fim,
        ativo=cupom.ativo,
        pode_ser_usado=cupom.pode_ser_usado()
    )


@router.get("/validar/{codigo}", dependencies=[Depends(get_current_admin)])
async def validar_cupom(
    codigo: str,
    session: AsyncSession = Depends(get_session)
):
    """Valida se um cupom pode ser usado."""
    stmt = select(Cupom).where(Cupom.codigo == codigo.upper())
    result = await session.execute(stmt)
    cupom = result.scalar_one_or_none()

    if not cupom:
        return {"valido": False, "motivo": "Cupom não encontrado"}

    if not cupom.pode_ser_usado():
        motivos = []
        if not cupom.ativo:
            motivos.append("Cupom inativo")
        if cupom.uso_atual >= cupom.uso_maximo:
            motivos.append("Limite de uso atingido")
        hoje = date.today()
        if not (cupom.data_inicio <= hoje <= cupom.data_fim):
            motivos.append("Cupom fora do período de validade")

        return {"valido": False, "motivo": ", ".join(motivos)}

    return {
        "valido": True,
        "cupom": CupomResponse(
            id=cupom.id,
            codigo=cupom.codigo,
            tipo=cupom.tipo,
            valor=cupom.valor,
            aplicavel_em=cupom.aplicavel_em,
            uso_maximo=cupom.uso_maximo,
            uso_atual=cupom.uso_atual,
            uso_por_cliente=cupom.uso_por_cliente,
            data_inicio=cupom.data_inicio,
            data_fim=cupom.data_fim,
            ativo=cupom.ativo,
            pode_ser_usado=True
        )
    }


@router.delete("/{cupom_id}", dependencies=[Depends(get_current_admin)])
async def desativar_cupom(
    cupom_id: uuid.UUID,
    session: AsyncSession = Depends(get_session)
):
    """Desativa um cupom."""
    cupom = await session.get(Cupom, cupom_id)
    if not cupom:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")

    cupom.ativo = False
    await session.commit()

    return {"success": True, "message": "Cupom desativado"}
