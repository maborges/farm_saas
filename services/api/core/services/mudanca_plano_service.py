"""
Service para gerenciamento de mudanças de plano (upgrade/downgrade).

Implementa toda a lógica de negócio para solicitação, aprovação e aplicação
de mudanças de plano com integração ao gateway de pagamento.
"""
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from core.models.plan_changes import MudancaPlano, HistoricoBloqueio
from core.models.billing import PlanoAssinatura, AssinaturaTenant
from core.models.tenant import Tenant
from core.models.auth import Usuario
from core.base_service import BaseService
from core.exceptions import BusinessRuleError, EntityNotFoundError
from core.services.plan_pricing_service import PlanoPricingService


class MudancaPlanoService(BaseService[MudancaPlano]):
    """Service para gerenciar mudanças de plano."""

    def __init__(self, session: AsyncSession, tenant_id: Optional[UUID] = None):
        super().__init__(MudancaPlano, session, tenant_id)
        self.pricing_service = PlanoPricingService(session)

    async def simular_mudanca(
        self,
        plano_destino_id: UUID,
        usuarios_destino: int,
        assinatura_id: Optional[UUID] = None,
        usuario_solicitante_id: Optional[UUID] = None
    ) -> dict:
        """
        Simula mudança de plano sem criar registro.

        Calcula valores, identifica tipo de mudança (upgrade/downgrade),
        e retorna informações para o usuário decidir.

        Args:
            plano_destino_id: Plano desejado
            usuarios_destino: Quantidade de usuários desejada
            assinatura_id: ID da assinatura (se tenant tem múltiplas)
            usuario_solicitante_id: ID do usuário solicitante (para validação)

        Returns:
            dict com simulação completa

        Raises:
            EntityNotFoundError: Se assinatura não existe
            BusinessRuleError: Se mudança não é permitida
        """
        # Buscar assinatura atual
        assinatura = await self._obter_assinatura(assinatura_id)

        # Buscar planos
        plano_atual = await self._obter_plano(assinatura.plano_id)
        plano_novo = await self._obter_plano(plano_destino_id)

        # Determinar tipo de mudança
        tipo_mudanca = self._determinar_tipo_mudanca(
            assinatura.plano_id,
            assinatura.usuarios_contratados,
            plano_destino_id,
            usuarios_destino
        )

        # Calcular valores
        calculo = await self.pricing_service.calcular_diferenca_planos(
            plano_origem_id=assinatura.plano_id,
            usuarios_origem=assinatura.usuarios_contratados,
            plano_destino_id=plano_destino_id,
            usuarios_destino=usuarios_destino,
            ciclo=assinatura.ciclo_pagamento
        )

        # Calcular proporcional (para upgrade)
        dias_restantes = 0
        valor_proporcional = Decimal("0.00")

        if tipo_mudanca.startswith("UPGRADE") and assinatura.data_proxima_renovacao:
            dias_restantes = (assinatura.data_proxima_renovacao.date() - datetime.now(timezone.utc).date()).days
            dias_ciclo = 365 if assinatura.ciclo_pagamento == "ANUAL" else 30

            if dias_restantes > 0:
                valor_proporcional = (calculo["diferenca"] * dias_restantes) / dias_ciclo

        # Mensagem explicativa
        mensagem = self._gerar_mensagem_simulacao(
            tipo_mudanca,
            plano_atual.nome,
            plano_novo.nome,
            assinatura.usuarios_contratados,
            usuarios_destino,
            valor_proporcional,
            dias_restantes
        )

        return {
            "tipo_mudanca": tipo_mudanca,
            "plano_atual": {
                "id": str(plano_atual.id),
                "nome": plano_atual.nome,
                "modulos": plano_atual.modulos_inclusos
            },
            "plano_novo": {
                "id": str(plano_novo.id),
                "nome": plano_novo.nome,
                "modulos": plano_novo.modulos_inclusos
            },
            "usuarios_atual": assinatura.usuarios_contratados,
            "usuarios_novo": usuarios_destino,
            "valor_atual_mensal": float(calculo["valor_atual"]),
            "valor_novo_mensal": float(calculo["valor_novo"]),
            "diferenca_mensal": float(calculo["diferenca"]),
            "dias_restantes_ciclo": dias_restantes,
            "valor_proporcional": float(valor_proporcional),
            "data_proxima_cobranca": assinatura.data_proxima_renovacao,
            "mensagem": mensagem
        }

    async def solicitar_mudanca(
        self,
        plano_destino_id: UUID,
        usuarios_destino: int,
        usuario_solicitante_id: UUID,
        assinatura_id: Optional[UUID] = None
    ) -> MudancaPlano:
        """
        Cria solicitação de mudança de plano.

        Para UPGRADE: Cria cobrança no Asaas e retorna URL de pagamento.
        Para DOWNGRADE: Agenda mudança para próximo ciclo.

        Args:
            plano_destino_id: Plano desejado
            usuarios_destino: Quantidade de usuários
            usuario_solicitante_id: Quem está solicitando
            assinatura_id: ID da assinatura

        Returns:
            MudancaPlano criada

        Raises:
            BusinessRuleError: Se mudança não permitida
        """
        # Validar que não há mudança pendente
        await self._validar_mudanca_pendente(assinatura_id)

        # Simular para obter valores
        simulacao = await self.simular_mudanca(
            plano_destino_id,
            usuarios_destino,
            assinatura_id,
            usuario_solicitante_id
        )

        # Buscar assinatura
        assinatura = await self._obter_assinatura(assinatura_id)

        # Calcular valores
        dias_restantes = simulacao["dias_restantes_ciclo"]
        valor_proporcional = Decimal(str(simulacao["valor_proporcional"]))
        valor_diferenca = Decimal(str(simulacao["diferenca_mensal"]))

        # Criar registro de mudança
        mudanca = MudancaPlano(
            tenant_id=self.tenant_id,
            assinatura_id=assinatura.id,
            plano_origem_id=assinatura.plano_id,
            usuarios_origem=assinatura.usuarios_contratados,
            plano_destino_id=plano_destino_id,
            usuarios_destino=usuarios_destino,
            tipo_mudanca=simulacao["tipo_mudanca"],
            valor_calculado=valor_diferenca,
            valor_proporcional=valor_proporcional,
            dias_restantes_ciclo=dias_restantes if dias_restantes > 0 else None,
            solicitado_por_usuario_id=usuario_solicitante_id,
            status="pendente_pagamento"
        )

        # Se for DOWNGRADE, agendar para próximo ciclo
        if simulacao["tipo_mudanca"].startswith("DOWNGRADE"):
            mudanca.agendado_para = assinatura.data_proxima_renovacao
            mudanca.status = "agendado"
            logger.info(
                f"Downgrade agendado para {assinatura.data_proxima_renovacao} - "
                f"Tenant {self.tenant_id}"
            )

        self.session.add(mudanca)
        await self.session.commit()
        await self.session.refresh(mudanca)

        logger.info(
            f"Mudança de plano solicitada: {simulacao['tipo_mudanca']} - "
            f"Tenant {self.tenant_id}, Mudança ID {mudanca.id}"
        )

        return mudanca

    async def aprovar_manualmente(
        self,
        mudanca_id: UUID,
        admin_id: UUID,
        motivo: str,
        dias_tolerancia: int = 5
    ) -> MudancaPlano:
        """
        Aprova mudança manualmente (backoffice).

        Libera acesso sem pagamento, mas define prazo para regularização.
        Após o prazo, tenant é bloqueado automaticamente.

        Args:
            mudanca_id: ID da mudança
            admin_id: ID do admin aprovando
            motivo: Justificativa da liberação
            dias_tolerancia: Dias para regularizar pagamento

        Returns:
            MudancaPlano atualizada
        """
        # Buscar mudança (sem filtro de tenant, é operação de backoffice)
        stmt = select(MudancaPlano).where(MudancaPlano.id == mudanca_id)
        result = await self.session.execute(stmt)
        mudanca = result.scalar_one_or_none()

        if not mudanca:
            raise EntityNotFoundError(f"Mudança {mudanca_id} não encontrada")

        if mudanca.status not in ["pendente_pagamento", "agendado"]:
            raise BusinessRuleError(
                f"Mudança está em status {mudanca.status}, não pode ser aprovada manualmente"
            )

        # Atualizar mudança
        mudanca.status = "liberado_manualmente"
        mudanca.liberado_manualmente = True
        mudanca.aprovado_por_admin_id = admin_id
        mudanca.motivo_liberacao_manual = motivo
        mudanca.data_limite_pagamento = datetime.now(timezone.utc) + timedelta(days=dias_tolerancia)

        await self.session.commit()
        await self.session.refresh(mudanca)

        # Aplicar mudança imediatamente
        await self._aplicar_mudanca(mudanca)

        logger.warning(
            f"Mudança {mudanca_id} aprovada manualmente por admin {admin_id}. "
            f"Prazo para pagamento: {mudanca.data_limite_pagamento}"
        )

        return mudanca

    async def aplicar_mudancas_agendadas(self) -> list[MudancaPlano]:
        """
        Aplica mudanças agendadas cuja data chegou.

        Chamado por job diário para aplicar downgrades agendados.

        Returns:
            Lista de mudanças aplicadas
        """
        # Buscar mudanças agendadas com data <= hoje
        stmt = (
            select(MudancaPlano)
            .where(MudancaPlano.status == "agendado")
            .where(MudancaPlano.agendado_para <= datetime.now(timezone.utc))
        )
        result = await self.session.execute(stmt)
        mudancas = result.scalars().all()

        aplicadas = []

        for mudanca in mudancas:
            try:
                await self._aplicar_mudanca(mudanca)
                aplicadas.append(mudanca)
                logger.info(f"Mudança agendada {mudanca.id} aplicada automaticamente")
            except Exception as e:
                logger.error(f"Erro ao aplicar mudança {mudanca.id}: {e}")

        await self.session.commit()

        return aplicadas

    async def verificar_inadimplencias(self) -> list[UUID]:
        """
        Verifica mudanças liberadas manualmente sem pagamento no prazo.

        Bloqueia tenants inadimplentes.

        Returns:
            Lista de tenant_ids bloqueados
        """
        # Buscar mudanças liberadas manualmente com prazo vencido
        stmt = (
            select(MudancaPlano)
            .where(MudancaPlano.status == "liberado_manualmente")
            .where(MudancaPlano.data_limite_pagamento < datetime.now(timezone.utc))
        )
        result = await self.session.execute(stmt)
        mudancas_vencidas = result.scalars().all()

        tenants_bloqueados = []

        for mudanca in mudancas_vencidas:
            try:
                await self._bloquear_por_inadimplencia(mudanca)
                tenants_bloqueados.append(mudanca.tenant_id)
                logger.warning(
                    f"Tenant {mudanca.tenant_id} bloqueado por inadimplência - "
                    f"Mudança {mudanca.id}"
                )
            except Exception as e:
                logger.error(f"Erro ao bloquear tenant {mudanca.tenant_id}: {e}")

        await self.session.commit()

        return tenants_bloqueados

    async def cancelar_mudanca(
        self,
        mudanca_id: UUID,
        usuario_id: UUID,
        motivo: Optional[str] = None
    ) -> MudancaPlano:
        """
        Cancela mudança pendente.

        Apenas mudanças em status pendente/agendado podem ser canceladas.
        """
        mudanca = await self.get_or_fail(mudanca_id)

        if mudanca.status not in ["pendente_pagamento", "agendado"]:
            raise BusinessRuleError(
                f"Mudança em status {mudanca.status} não pode ser cancelada"
            )

        mudanca.status = "cancelado"
        mudanca.observacoes = motivo or "Cancelado pelo usuário"

        await self.session.commit()
        await self.session.refresh(mudanca)

        logger.info(f"Mudança {mudanca_id} cancelada por usuário {usuario_id}")

        return mudanca

    # ========================================================================
    # Métodos privados
    # ========================================================================

    async def _aplicar_mudanca(self, mudanca: MudancaPlano) -> None:
        """Aplica mudança na assinatura."""
        # Buscar assinatura
        stmt = select(AssinaturaTenant).where(AssinaturaTenant.id == mudanca.assinatura_id)
        result = await self.session.execute(stmt)
        assinatura = result.scalar_one()

        # Atualizar assinatura
        assinatura.plano_id = mudanca.plano_destino_id
        assinatura.usuarios_contratados = mudanca.usuarios_destino

        # Atualizar mudança
        mudanca.status = "aplicado"
        mudanca.aplicado_em = datetime.now(timezone.utc)
        mudanca.aplicado_por_job = True

        logger.info(
            f"Mudança {mudanca.id} aplicada: Plano {mudanca.plano_destino_id}, "
            f"{mudanca.usuarios_destino} usuários"
        )

    async def _bloquear_por_inadimplencia(self, mudanca: MudancaPlano) -> None:
        """Bloqueia tenant por inadimplência."""
        # Buscar assinatura
        stmt = select(AssinaturaTenant).where(AssinaturaTenant.id == mudanca.assinatura_id)
        result = await self.session.execute(stmt)
        assinatura = result.scalar_one()

        # Bloquear assinatura
        assinatura.status = "BLOQUEADA"
        assinatura.data_bloqueio = datetime.now(timezone.utc)

        # Atualizar mudança
        mudanca.status = "bloqueado"

        # Criar histórico de bloqueio
        bloqueio = HistoricoBloqueio(
            tenant_id=mudanca.tenant_id,
            mudanca_plano_id=mudanca.id,
            assinatura_id=assinatura.id,
            motivo="INADIMPLENCIA_MUDANCA_PLANO",
            descricao=f"Mudança {mudanca.id} liberada manualmente não foi paga no prazo ({mudanca.data_limite_pagamento})",
            data_bloqueio=datetime.now(timezone.utc),
            bloqueado_automaticamente=True
        )

        self.session.add(bloqueio)

    async def _obter_assinatura(self, assinatura_id: Optional[UUID]) -> AssinaturaTenant:
        """Busca assinatura do tenant."""
        if assinatura_id:
            stmt = select(AssinaturaTenant).where(
                and_(
                    AssinaturaTenant.id == assinatura_id,
                    AssinaturaTenant.tenant_id == self.tenant_id
                )
            )
        else:
            # Buscar assinatura principal
            stmt = select(AssinaturaTenant).where(
                and_(
                    AssinaturaTenant.tenant_id == self.tenant_id,
                    AssinaturaTenant.tipo_assinatura == "PRINCIPAL"
                )
            )

        result = await self.session.execute(stmt)
        assinatura = result.scalar_one_or_none()

        if not assinatura:
            raise EntityNotFoundError("Assinatura não encontrada")

        if assinatura.status == "BLOQUEADA":
            raise BusinessRuleError(
                "Assinatura está bloqueada. Entre em contato com o suporte."
            )

        return assinatura

    async def _obter_plano(self, plano_id: UUID) -> PlanoAssinatura:
        """Busca plano."""
        stmt = select(PlanoAssinatura).where(PlanoAssinatura.id == plano_id)
        result = await self.session.execute(stmt)
        plano = result.scalar_one_or_none()

        if not plano:
            raise EntityNotFoundError(f"Plano {plano_id} não encontrado")

        if not plano.ativo:
            raise BusinessRuleError(f"Plano {plano.nome} não está mais disponível")

        return plano

    def _determinar_tipo_mudanca(
        self,
        plano_origem_id: UUID,
        usuarios_origem: int,
        plano_destino_id: UUID,
        usuarios_destino: int
    ) -> str:
        """Determina tipo de mudança."""
        mudou_plano = plano_origem_id != plano_destino_id
        mudou_usuarios = usuarios_origem != usuarios_destino

        if mudou_plano and mudou_usuarios:
            if usuarios_destino > usuarios_origem:
                return "UPGRADE_COMPLETO"
            else:
                return "DOWNGRADE_COMPLETO"
        elif mudou_plano:
            # Apenas mudança de tier (assumimos upgrade se mudou plano)
            return "UPGRADE_PLANO"
        elif mudou_usuarios:
            if usuarios_destino > usuarios_origem:
                return "UPGRADE_USUARIOS"
            else:
                return "DOWNGRADE_USUARIOS"
        else:
            raise BusinessRuleError("Nenhuma mudança detectada")

    def _gerar_mensagem_simulacao(
        self,
        tipo_mudanca: str,
        plano_atual: str,
        plano_novo: str,
        usuarios_atual: int,
        usuarios_novo: int,
        valor_proporcional: Decimal,
        dias_restantes: int
    ) -> str:
        """Gera mensagem explicativa para o usuário."""
        if tipo_mudanca.startswith("UPGRADE"):
            if valor_proporcional > 0:
                return (
                    f"Upgrade de {plano_atual} ({usuarios_atual} users) para "
                    f"{plano_novo} ({usuarios_novo} users). "
                    f"Você pagará R$ {valor_proporcional:.2f} proporcional aos "
                    f"{dias_restantes} dias restantes do ciclo atual. "
                    f"Após confirmação do pagamento, o upgrade será aplicado imediatamente."
                )
            else:
                return f"Upgrade para {plano_novo} com {usuarios_novo} usuários será aplicado no próximo ciclo."

        else:  # DOWNGRADE
            return (
                f"Downgrade de {plano_atual} ({usuarios_atual} users) para "
                f"{plano_novo} ({usuarios_novo} users) será agendado para o próximo "
                f"ciclo de cobrança. Você continuará com acesso ao plano atual até lá."
            )

    async def _validar_mudanca_pendente(self, assinatura_id: Optional[UUID]) -> None:
        """Valida que não há mudança pendente."""
        assinatura = await self._obter_assinatura(assinatura_id)

        stmt = (
            select(MudancaPlano)
            .where(MudancaPlano.assinatura_id == assinatura.id)
            .where(MudancaPlano.status.in_(["pendente_pagamento", "agendado", "liberado_manualmente"]))
        )
        result = await self.session.execute(stmt)
        mudanca_existente = result.scalar_one_or_none()

        if mudanca_existente:
            raise BusinessRuleError(
                f"Já existe uma mudança de plano pendente (status: {mudanca_existente.status}). "
                "Cancele ou aguarde conclusão antes de solicitar nova mudança."
            )
