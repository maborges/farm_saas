"""
Service para integração com gateway de pagamento Asaas.

Implementa criação de cobranças, processamento de webhooks e sincronização de status.

Documentação Asaas: https://docs.asaas.com/reference/overview
"""
import httpx
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from core.models.plan_changes import CobrancaAsaas, MudancaPlano
from core.models.tenant import Tenant
from core.exceptions import BusinessRuleError, EntityNotFoundError
from core.config import settings


class AsaasService:
    """Service para integração com Asaas."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.api_key = getattr(settings, 'asaas_api_key', None)
        self.api_url = getattr(settings, 'asaas_api_url', 'https://sandbox.asaas.com/api/v3')

        if not self.api_key:
            logger.warning("Asaas API Key não configurada. Funcionando em modo simulação.")
            self.modo_simulacao = True
        else:
            self.modo_simulacao = False

    async def criar_cobranca_mudanca_plano(
        self,
        mudanca: MudancaPlano,
        dias_vencimento: int = 3
    ) -> CobrancaAsaas:
        """
        Cria cobrança no Asaas para mudança de plano.

        Args:
            mudanca: Mudança de plano
            dias_vencimento: Dias até vencimento

        Returns:
            CobrancaAsaas criada

        Raises:
            BusinessRuleError: Se erro na criação
        """
        # Buscar dados do tenant
        stmt = select(Tenant).where(Tenant.id == mudanca.tenant_id)
        result = await self.session.execute(stmt)
        tenant = result.scalar_one_or_none()

        if not tenant:
            raise EntityNotFoundError(f"Tenant {mudanca.tenant_id} não encontrado")

        # Obter ou criar customer no Asaas
        customer_id = await self._obter_ou_criar_customer(tenant)

        # Criar cobrança
        data_vencimento = datetime.now(timezone.utc) + timedelta(days=dias_vencimento)

        if self.modo_simulacao:
            # Modo simulação (desenvolvimento)
            charge_data = await self._criar_cobranca_simulada(
                mudanca,
                tenant,
                customer_id,
                data_vencimento
            )
        else:
            # Modo produção (Asaas real)
            charge_data = await self._criar_cobranca_asaas(
                mudanca,
                customer_id,
                data_vencimento
            )

        # Salvar no banco
        cobranca = CobrancaAsaas(
            tenant_id=mudanca.tenant_id,
            mudanca_plano_id=mudanca.id,
            assinatura_id=mudanca.assinatura_id,
            asaas_charge_id=charge_data['id'],
            asaas_customer_id=customer_id,
            valor=mudanca.valor_proporcional,
            descricao=f"Upgrade de plano - {mudanca.tipo_mudanca}",
            status=charge_data['status'],
            url_pagamento=charge_data.get('invoiceUrl'),
            codigo_barras=charge_data.get('bankSlipUrl'),
            qrcode_pix=charge_data.get('pixQrCode'),
            data_vencimento=data_vencimento
        )

        self.session.add(cobranca)

        # Atualizar mudança com dados da cobrança
        mudanca.cobranca_asaas_id = charge_data['id']
        mudanca.url_pagamento = charge_data.get('invoiceUrl')

        await self.session.commit()
        await self.session.refresh(cobranca)

        logger.info(
            f"Cobrança Asaas criada: {charge_data['id']} - "
            f"R$ {mudanca.valor_proporcional} - Tenant {tenant.nome}"
        )

        return cobranca

    async def processar_webhook(self, payload: dict) -> bool:
        """
        Processa webhook recebido do Asaas.

        Eventos principais:
        - PAYMENT_RECEIVED: Pagamento recebido (PIX, cartão)
        - PAYMENT_CONFIRMED: Pagamento confirmado (boleto)
        - PAYMENT_OVERDUE: Pagamento vencido

        Args:
            payload: Dados do webhook

        Returns:
            True se processado com sucesso
        """
        event = payload.get('event')
        payment_data = payload.get('payment', {})
        payment_id = payment_data.get('id')

        if not payment_id:
            logger.error("Webhook sem payment ID")
            return False

        # Buscar cobrança
        stmt = select(CobrancaAsaas).where(CobrancaAsaas.asaas_charge_id == payment_id)
        result = await self.session.execute(stmt)
        cobranca = result.scalar_one_or_none()

        if not cobranca:
            logger.warning(f"Cobrança {payment_id} não encontrada no banco")
            return False

        # Atualizar status
        cobranca.status = payment_data.get('status', cobranca.status)
        cobranca.ultimo_webhook_recebido = datetime.now(timezone.utc)

        # Processar evento
        if event in ['PAYMENT_RECEIVED', 'PAYMENT_CONFIRMED']:
            await self._processar_pagamento_confirmado(cobranca, payment_data)
        elif event == 'PAYMENT_OVERDUE':
            await self._processar_pagamento_vencido(cobranca)

        await self.session.commit()

        logger.info(f"Webhook processado: {event} - Cobrança {payment_id}")

        return True

    async def consultar_status_cobranca(self, cobranca_id: UUID) -> dict:
        """Consulta status atual de uma cobrança no Asaas."""
        stmt = select(CobrancaAsaas).where(CobrancaAsaas.id == cobranca_id)
        result = await self.session.execute(stmt)
        cobranca = result.scalar_one_or_none()

        if not cobranca:
            raise EntityNotFoundError(f"Cobrança {cobranca_id} não encontrada")

        if self.modo_simulacao:
            return {
                'id': cobranca.asaas_charge_id,
                'status': cobranca.status,
                'value': float(cobranca.valor)
            }

        # Consultar Asaas
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/payments/{cobranca.asaas_charge_id}",
                headers={'access_token': self.api_key}
            )

            if response.status_code != 200:
                raise BusinessRuleError(f"Erro ao consultar Asaas: {response.text}")

            return response.json()

    # ========================================================================
    # Métodos privados
    # ========================================================================

    async def _obter_ou_criar_customer(self, tenant: Tenant) -> str:
        """Obtém ID do customer no Asaas ou cria novo."""
        # Buscar cobrança existente para pegar customer_id
        stmt = (
            select(CobrancaAsaas)
            .where(CobrancaAsaas.tenant_id == tenant.id)
            .where(CobrancaAsaas.asaas_customer_id.isnot(None))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        cobranca_existente = result.scalar_one_or_none()

        if cobranca_existente and cobranca_existente.asaas_customer_id:
            return cobranca_existente.asaas_customer_id

        # Criar novo customer
        if self.modo_simulacao:
            return f"cus_simul_{tenant.id}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/customers",
                headers={'access_token': self.api_key},
                json={
                    'name': tenant.nome,
                    'cpfCnpj': tenant.documento,
                    'email': tenant.email_responsavel,
                    'phone': tenant.telefone_responsavel,
                    'externalReference': str(tenant.id)
                }
            )

            if response.status_code != 200:
                raise BusinessRuleError(f"Erro ao criar customer Asaas: {response.text}")

            customer_data = response.json()
            logger.info(f"Customer Asaas criado: {customer_data['id']} - {tenant.nome}")

            return customer_data['id']

    async def _criar_cobranca_asaas(
        self,
        mudanca: MudancaPlano,
        customer_id: str,
        data_vencimento: datetime
    ) -> dict:
        """Cria cobrança real no Asaas."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/payments",
                headers={'access_token': self.api_key},
                json={
                    'customer': customer_id,
                    'billingType': 'UNDEFINED',  # Permite PIX, boleto, cartão
                    'value': float(mudanca.valor_proporcional),
                    'dueDate': data_vencimento.strftime('%Y-%m-%d'),
                    'description': f"Upgrade de plano - {mudanca.tipo_mudanca}",
                    'externalReference': str(mudanca.id),
                    'postalService': False
                }
            )

            if response.status_code != 200:
                raise BusinessRuleError(f"Erro ao criar cobrança Asaas: {response.text}")

            return response.json()

    async def _criar_cobranca_simulada(
        self,
        mudanca: MudancaPlano,
        tenant: Tenant,
        customer_id: str,
        data_vencimento: datetime
    ) -> dict:
        """Cria cobrança simulada (desenvolvimento)."""
        return {
            'id': f'pay_simul_{mudanca.id}',
            'status': 'PENDING',
            'invoiceUrl': f'https://sandbox.asaas.com/invoice/simul_{mudanca.id}',
            'bankSlipUrl': None,
            'pixQrCode': None,
            'value': float(mudanca.valor_proporcional),
            'dueDate': data_vencimento.strftime('%Y-%m-%d')
        }

    async def _processar_pagamento_confirmado(
        self,
        cobranca: CobrancaAsaas,
        payment_data: dict
    ) -> None:
        """Processa confirmação de pagamento."""
        # Atualizar cobrança
        cobranca.data_pagamento = datetime.now(timezone.utc)
        cobranca.status = 'CONFIRMED'

        # Buscar mudança e aplicar
        if cobranca.mudanca_plano_id:
            stmt = select(MudancaPlano).where(MudancaPlano.id == cobranca.mudanca_plano_id)
            result = await self.session.execute(stmt)
            mudanca = result.scalar_one_or_none()

            if mudanca and mudanca.status == 'pendente_pagamento':
                # Importar aqui para evitar import circular
                from core.services.mudanca_plano_service import MudancaPlanoService

                mudanca_service = MudancaPlanoService(self.session, mudanca.tenant_id)
                await mudanca_service._aplicar_mudanca(mudanca)

                logger.info(
                    f"Pagamento confirmado! Mudança {mudanca.id} aplicada automaticamente"
                )

    async def _processar_pagamento_vencido(self, cobranca: CobrancaAsaas) -> None:
        """Processa vencimento de pagamento."""
        cobranca.status = 'OVERDUE'
        logger.warning(f"Cobrança {cobranca.id} vencida - Tenant {cobranca.tenant_id}")

        # TODO: Enviar notificação ao tenant
