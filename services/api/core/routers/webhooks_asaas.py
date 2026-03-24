"""
Router para webhooks do Asaas.

Recebe notificações de eventos de pagamento do gateway Asaas.
"""
from fastapi import APIRouter, HTTPException, Request, status
from loguru import logger

from core.database import async_session_maker
from core.services.asaas_service import AsaasService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post(
    "/asaas",
    status_code=status.HTTP_200_OK,
    summary="Webhook do Asaas",
    description="Recebe notificações de eventos de pagamento do Asaas"
)
async def webhook_asaas(request: Request):
    """
    Processa webhooks do Asaas.

    **Eventos suportados:**
    - PAYMENT_RECEIVED: Pagamento recebido (PIX, cartão)
    - PAYMENT_CONFIRMED: Pagamento confirmado (boleto após compensação)
    - PAYMENT_OVERDUE: Pagamento vencido
    - PAYMENT_DELETED: Cobrança cancelada
    - PAYMENT_RESTORED: Cobrança restaurada

    **Segurança:**
    - TODO: Implementar validação de assinatura do webhook
    - TODO: Validar IP de origem (whitelist Asaas)

    **Documentação Asaas:**
    https://docs.asaas.com/reference/webhooks
    """
    try:
        # Receber payload
        payload = await request.json()

        logger.info(f"Webhook Asaas recebido: {payload.get('event')}")

        # Processar webhook
        async with async_session_maker() as session:
            asaas_service = AsaasService(session)

            success = await asaas_service.processar_webhook(payload)

            if success:
                return {"status": "processed", "message": "Webhook processado com sucesso"}
            else:
                logger.warning("Webhook não foi processado completamente")
                return {"status": "ignored", "message": "Webhook ignorado"}

    except ValueError as e:
        logger.error(f"Payload inválido no webhook Asaas: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload inválido"
        )
    except Exception as e:
        logger.error(f"Erro ao processar webhook Asaas: {e}", exc_info=True)
        # Retornar 200 mesmo com erro para evitar reenvios desnecessários
        # Asaas reenvia webhook se receber 4xx/5xx
        return {"status": "error", "message": "Erro ao processar webhook"}


@router.get(
    "/asaas/health",
    summary="Health check do webhook",
    description="Endpoint de teste para verificar se webhook está acessível"
)
async def webhook_asaas_health():
    """Health check para webhook do Asaas."""
    return {
        "status": "ok",
        "service": "asaas-webhook",
        "message": "Webhook está operacional"
    }
