from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from core.base_service import BaseService
from core.models.fazenda import Fazenda
from core.models.billing import AssinaturaTenant, PlanoAssinatura
from core.schemas.fazenda_input import FazendaCreate
from core.exceptions import BusinessRuleError


class FazendaService(BaseService[Fazenda]):
    """
    Serviço que gerencia o ciclo de vida das fazendas do AgroSaaS.
    Herda do BaseService que assegura blindagem por tenant_id de forma automática.
    """
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(Fazenda, session, tenant_id)

    async def _check_limite_fazendas(self) -> None:
        """Verifica se o tenant atingiu o limite de fazendas do plano contratado."""
        # Busca max_fazendas do plano ativo
        stmt_plano = (
            select(PlanoAssinatura.max_fazendas)
            .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
            .where(
                AssinaturaTenant.tenant_id == self.tenant_id,
                AssinaturaTenant.status == "ATIVA",
            )
            .limit(1)
        )
        result = await self.session.execute(stmt_plano)
        max_fazendas = result.scalar_one_or_none()

        if max_fazendas is None or max_fazendas == -1:
            return  # Sem plano ativo ou ilimitado

        # Conta fazendas ativas do tenant
        stmt_count = select(func.count(Fazenda.id)).where(
            Fazenda.tenant_id == self.tenant_id,
            Fazenda.ativo == True,
        )
        result_count = await self.session.execute(stmt_count)
        total = result_count.scalar_one()

        if total >= max_fazendas:
            raise BusinessRuleError(
                f"Limite de {max_fazendas} propriedade(s) atingido no plano contratado. "
                "Faça upgrade para adicionar mais propriedades."
            )

    async def create_fazenda(self, dados: FazendaCreate) -> Fazenda:
        await self._check_limite_fazendas()
        return await super().create(dados)
