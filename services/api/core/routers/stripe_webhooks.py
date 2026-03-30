"""
Webhook handler para eventos Stripe.

Registra: POST /stripe/webhook

Eventos tratados:
- checkout.session.completed → ativa tenant + assinatura + converte lead
"""
import stripe
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from pydantic import BaseModel
from core.dependencies import require_permission
from sqlalchemy import select
from datetime import datetime, timezone
from loguru import logger

from core.database import async_session_maker
from core.models.tenant import Tenant
from core.models.billing import AssinaturaTenant, Fatura
from core.models.crm import LeadCRM
from core.services.stripe_service import StripeService

router = APIRouter(prefix="/stripe", tags=["Stripe — Webhooks"])


class SyncSessionRequest(BaseModel):
    session_id: str | None = None
    payment_intent_id: str | None = None


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
):
    payload = await request.body()

    stripe_svc = StripeService()
    try:
        event = stripe_svc.verificar_webhook(payload, stripe_signature or "")
    except ValueError as e:
        logger.warning(f"Webhook Stripe inválido: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await _handle_checkout_completed(session)

    return {"status": "ok"}


async def _handle_checkout_completed(session: dict) -> None:
    """
    Ativa tenant e assinatura após pagamento confirmado.
    Marca o lead como 'convertido'.
    """
    tenant_id = session.get("metadata", {}).get("tenant_id")
    assinatura_id = session.get("metadata", {}).get("assinatura_id")
    stripe_subscription_id = session.get("subscription")

    if not tenant_id or not assinatura_id:
        logger.error(f"Webhook checkout.session.completed sem metadata: {session.get('id')}")
        return

    async with async_session_maker() as db:
        try:
            # Ativar tenant
            tenant = await db.get(Tenant, tenant_id)
            if not tenant:
                logger.error(f"Tenant {tenant_id} não encontrado no webhook Stripe")
                return

            tenant.ativo = True
            tenant.activation_token = None
            tenant.activation_expires_at = None

            # Ativar assinatura
            assinatura = await db.get(AssinaturaTenant, assinatura_id)
            if assinatura:
                assinatura.status = "ATIVA"
                assinatura.stripe_subscription_id = stripe_subscription_id

            # Baixar fatura ABERTA vinculada à assinatura
            stmt_fatura = select(Fatura).where(
                Fatura.assinatura_id == assinatura_id,
                Fatura.status == "ABERTA"
            )
            fatura = (await db.execute(stmt_fatura)).scalar_one_or_none()
            if fatura:
                fatura.status = "PAGA"
                fatura.data_aprovacao_rejeicao = datetime.now(timezone.utc)

            # Converter lead vinculado
            stmt = select(LeadCRM).where(LeadCRM.tenant_convertido_id == tenant.id)
            result = await db.execute(stmt)
            lead = result.scalar_one_or_none()
            if lead and lead.status == "aprovado":
                lead.status = "convertido"
                lead.data_conversao = datetime.now(timezone.utc).date()

            await db.commit()

            logger.info(
                f"Tenant {tenant_id} ativado via Stripe webhook. "
                f"Assinatura {assinatura_id} → ATIVA. "
                f"Lead convertido: {lead.id if lead else 'N/A'}"
            )

        except Exception as e:
            logger.error(f"Erro ao processar webhook checkout.session.completed: {e}", exc_info=True)


@router.post(
    "/sync-session",
    summary="Sincronizar sessão Stripe manualmente",
    dependencies=[Depends(require_permission("backoffice:billing:manage"))],
)
async def sync_stripe_session(body: SyncSessionRequest):
    """
    Busca uma checkout session no Stripe pelo ID e reprocessa o evento
    manualmente. Útil quando o webhook não foi recebido.
    """
    if not body.session_id and not body.payment_intent_id:
        raise HTTPException(status_code=422, detail="Informe session_id ou payment_intent_id")

    stripe_svc = StripeService()
    if not stripe_svc.stripe_configured():
        raise HTTPException(status_code=503, detail="Stripe não configurado neste ambiente")

    try:
        if body.session_id:
            session = stripe.checkout.Session.retrieve(body.session_id)
        else:
            # Busca a sessão pelo Payment Intent
            sessions = stripe.checkout.Session.list(payment_intent=body.payment_intent_id, limit=1)
            if not sessions.data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Nenhuma checkout session encontrada para o Payment Intent {body.payment_intent_id}",
                )
            session = sessions.data[0]
    except HTTPException:
        raise
    except stripe.InvalidRequestError as e:
        raise HTTPException(status_code=404, detail=f"Registro não encontrado no Stripe: {e}")
    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail=f"Erro ao consultar Stripe: {e}")

    if getattr(session, "payment_status", None) not in ("paid", "no_payment_required"):
        raise HTTPException(
            status_code=400,
            detail=f"Sessão ainda não foi paga (status: {session.get('payment_status')})",
        )

    # Normaliza para dict pois _handle_checkout_completed espera dict com .get()
    session_dict = {
        "id": session.id,
        "subscription": session.subscription,
        "payment_status": session.payment_status,
        "metadata": session.metadata._to_dict_recursive() if session.metadata else {},
    }
    await _handle_checkout_completed(session_dict)
    ref = body.session_id or body.payment_intent_id
    logger.info(f"Sync manual da sessão Stripe {session.id} (ref={ref}) concluído por admin")
    return {"status": "ok", "session_id": session.id}
