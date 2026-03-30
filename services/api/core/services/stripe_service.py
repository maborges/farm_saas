"""
Serviço de integração com Stripe.

Responsável por:
- Criar sessões de checkout para primeira cobrança
- Processar webhooks de pagamento (payment_intent.succeeded)

Configuração necessária em .env.local:
  STRIPE_SECRET_KEY=sk_live_...
  STRIPE_WEBHOOK_SECRET=whsec_...
  FRONTEND_URL=http://localhost:3000
"""
import stripe
from loguru import logger
from core.config import settings

stripe.api_key = settings.stripe_secret_key
FRONTEND_URL = settings.frontend_url
WEBHOOK_SECRET = settings.stripe_webhook_secret


class StripeService:

    async def criar_checkout_assinatura(
        self,
        tenant_id: str,
        assinatura_id: str,
        email: str,
        plano_id: str,
        ciclo: str,
    ) -> str:
        """
        Cria uma sessão de checkout Stripe para o primeiro pagamento.

        Retorna a URL de checkout para redirecionar o assinante.
        O preço é buscado dinamicamente via lookup_key no Stripe:
          - Formato: plano_{plano_id}_{MENSAL|ANUAL}

        Se STRIPE_SECRET_KEY não estiver configurada (desenvolvimento),
        retorna URL de simulação local.
        """
        if not stripe.api_key:
            logger.warning("STRIPE_SECRET_KEY não configurada — usando checkout simulado")
            return f"{FRONTEND_URL}/onboarding/pagamento-simulado?assinatura_id={assinatura_id}"

        try:
            # Buscar preço via lookup key
            lookup_key = f"plano_{plano_id}_{ciclo}"
            prices = stripe.Price.list(lookup_keys=[lookup_key], limit=1)

            if not prices.data:
                logger.error(f"Preço Stripe não encontrado para lookup_key={lookup_key}")
                raise ValueError(f"Preço não configurado no Stripe para o plano/ciclo selecionado")

            price_id = prices.data[0].id

            session = stripe.checkout.Session.create(
                customer_email=email,
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url=f"{FRONTEND_URL}/onboarding/sucesso?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{FRONTEND_URL}/onboarding/cancelado",
                metadata={
                    "tenant_id": tenant_id,
                    "assinatura_id": assinatura_id,
                },
            )

            logger.info(f"Checkout Stripe criado: {session.id} para tenant {tenant_id}")
            return session.url

        except stripe.StripeError as e:
            logger.error(f"Erro Stripe ao criar checkout: {e}")
            raise ValueError(f"Erro ao criar sessão de pagamento: {e.user_message}")

    def stripe_configured(self) -> bool:
        return bool(stripe.api_key)

    def verificar_webhook(self, payload: bytes, signature: str) -> stripe.Event:
        """Valida e parseia um evento de webhook Stripe."""
        if not WEBHOOK_SECRET:
            raise ValueError("STRIPE_WEBHOOK_SECRET não configurado")
        return stripe.Webhook.construct_event(payload, signature, WEBHOOK_SECRET)
