from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select

from core.database import async_session_maker
from agricola.rastreabilidade.models import LoteRastreabilidade

router = APIRouter(prefix="/public", tags=["Rastreabilidade Pública"])


@router.get("/track/{codigo_lote}")
async def track_lote_publico(codigo_lote: str):
    """Endpoint público para rastreamento de lote via QR code. Sem autenticação."""
    async with async_session_maker() as session:
        stmt = select(LoteRastreabilidade).where(
            LoteRastreabilidade.codigo_lote == codigo_lote
        )
        result = await session.execute(stmt)
        lote = result.scalar_one_or_none()

    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado.")

    return {
        "codigo_lote": lote.codigo_lote,
        "produto": lote.produto,
        "variedade": lote.variedade,
        "quantidade_total": float(lote.quantidade_total or 0),
        "unidade": lote.unidade,
        "status": lote.status,
        "certificacoes": lote.certificacoes or [],
        "data_geracao": lote.data_geracao.isoformat() if lote.data_geracao else None,
        "qr_code_url": lote.qr_code_url,
    }
