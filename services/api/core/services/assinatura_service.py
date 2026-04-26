"""
AssinaturaService — máquina de estados para AssinaturaTenant.

Centraliza todas as transições de status de assinatura, garantindo que:
- Somente transições válidas são permitidas
- Toda transição é auditada via log
- O job de suspensão automática usa este serviço
"""
import uuid
from datetime import datetime, timezone, timedelta
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

# Transições válidas: status_atual → set(status_permitidos)
_TRANSICOES: dict[str, set[str]] = {
    "PENDENTE":           {"TRIAL", "ATIVA", "CANCELADA"},
    "TRIAL":              {"ATIVA", "CANCELADA", "SUSPENSA"},
    "ATIVA":              {"PENDENTE_PAGAMENTO", "SUSPENSA", "CANCELADA"},
    "PENDENTE_PAGAMENTO": {"ATIVA", "SUSPENSA", "CANCELADA"},
    "SUSPENSA":           {"ATIVA", "CANCELADA"},
    "BLOQUEADA":          {"ATIVA", "CANCELADA"},
    "CANCELADA":          set(),  # terminal — nenhuma transição permitida
}


class TransicaoInvalidaError(Exception):
    pass


async def transicionar_assinatura(
    session: AsyncSession,
    assinatura_id: uuid.UUID,
    novo_status: str,
    motivo: str = "",
    operador_id: uuid.UUID | None = None,
) -> None:
    """
    Transiciona o status de uma AssinaturaTenant com validação de máquina de estados.

    Raises:
        TransicaoInvalidaError: se a transição não for permitida.
        ValueError: se assinatura não for encontrada.
    """
    from core.models.billing import AssinaturaTenant

    result = await session.execute(
        select(AssinaturaTenant).where(AssinaturaTenant.id == assinatura_id)
    )
    assinatura = result.scalar_one_or_none()
    if not assinatura:
        raise ValueError(f"AssinaturaTenant {assinatura_id} não encontrada.")

    status_atual = assinatura.status
    permitidos = _TRANSICOES.get(status_atual, set())

    if novo_status not in permitidos:
        raise TransicaoInvalidaError(
            f"Transição '{status_atual}' → '{novo_status}' não permitida. "
            f"Transições válidas: {sorted(permitidos) or 'nenhuma (terminal)'}."
        )

    valores: dict = {"status": novo_status}
    if novo_status == "SUSPENSA":
        valores["data_bloqueio"] = datetime.now(timezone.utc)

    await session.execute(
        update(AssinaturaTenant)
        .where(AssinaturaTenant.id == assinatura_id)
        .values(**valores)
    )

    logger.info(
        f"assinatura {assinatura_id} tenant={assinatura.tenant_id}: "
        f"{status_atual} → {novo_status}"
        + (f" | motivo: {motivo}" if motivo else "")
        + (f" | operador: {operador_id}" if operador_id else "")
    )


async def suspender_vencidos(session: AsyncSession) -> int:
    """
    Job automático: suspende assinaturas vencidas além do grace period.

    Critério: status ATIVA ou PENDENTE_PAGAMENTO
              AND data_proxima_renovacao + grace_period_days < agora

    Retorna o número de assinaturas suspensas.
    """
    from core.models.billing import AssinaturaTenant
    from sqlalchemy import func, and_, or_

    agora = datetime.now(timezone.utc)

    result = await session.execute(
        select(AssinaturaTenant).where(
            AssinaturaTenant.status.in_(["ATIVA", "PENDENTE_PAGAMENTO"]),
            AssinaturaTenant.data_proxima_renovacao.isnot(None),
            # vencimento + carência já passou
            AssinaturaTenant.data_proxima_renovacao
            + func.make_interval(0, 0, 0, AssinaturaTenant.grace_period_days)
            < agora,
        )
    )
    vencidas = result.scalars().all()

    count = 0
    for assinatura in vencidas:
        try:
            await transicionar_assinatura(
                session,
                assinatura.id,
                "SUSPENSA",
                motivo="Vencimento + grace period ultrapassados — suspensão automática",
            )
            count += 1
        except TransicaoInvalidaError as e:
            logger.warning(f"suspender_vencidos: {e}")

    if count:
        await session.commit()
        logger.info(f"suspender_vencidos: {count} assinatura(s) suspensa(s).")

    return count


async def suspender_trials_expirados(session: AsyncSession) -> int:
    """
    Job automático: suspende trials cujo trial_expires_at já passou.
    """
    from core.models.billing import AssinaturaTenant

    agora = datetime.now(timezone.utc)

    result = await session.execute(
        select(AssinaturaTenant).where(
            AssinaturaTenant.status == "TRIAL",
            AssinaturaTenant.trial_expires_at.isnot(None),
            AssinaturaTenant.trial_expires_at < agora,
        )
    )
    expirados = result.scalars().all()

    count = 0
    for assinatura in expirados:
        try:
            await transicionar_assinatura(
                session,
                assinatura.id,
                "SUSPENSA",
                motivo="Trial expirado — suspensão automática",
            )
            count += 1
        except TransicaoInvalidaError as e:
            logger.warning(f"suspender_trials_expirados: {e}")

    if count:
        await session.commit()
        logger.info(f"suspender_trials_expirados: {count} trial(s) suspenso(s).")

    return count
