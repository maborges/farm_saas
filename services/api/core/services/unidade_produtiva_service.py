from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from core.base_service import BaseService
from core.models.unidade_produtiva import UnidadeProdutiva
from core.models.billing import AssinaturaTenant, PlanoAssinatura
from core.schemas.unidade_produtiva_input import UnidadeProdutivaCreate
from core.exceptions import BusinessRuleError


class UnidadeProdutivaService(BaseService[UnidadeProdutiva]):
    """
    Serviço que gerencia o ciclo de vida das unidades produtivas do AgroSaaS.
    Herda do BaseService que assegura blindagem por tenant_id de forma automática.
    """
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(UnidadeProdutiva, session, tenant_id)

    async def _check_limite_unidades(self) -> None:
        """Verifica se o tenant atingiu o limite de unidades produtivas do plano contratado."""
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
        max_unidades = result.scalar_one_or_none()

        if max_unidades is None or max_unidades == -1:
            return  # Sem plano ativo ou ilimitado

        stmt_count = select(func.count(UnidadeProdutiva.id)).where(
            UnidadeProdutiva.tenant_id == self.tenant_id,
            UnidadeProdutiva.ativo == True,
        )
        result_count = await self.session.execute(stmt_count)
        total = result_count.scalar_one()

        if total >= max_unidades:
            raise BusinessRuleError(
                f"Limite de {max_unidades} propriedade(s) atingido no plano contratado. "
                "Faça upgrade para adicionar mais propriedades."
            )

    async def create_unidade_produtiva(self, dados: UnidadeProdutivaCreate) -> UnidadeProdutiva:
        await self._check_limite_unidades()
        return await super().create(dados)

    # Backward compat alias
    async def create_fazenda(self, dados: UnidadeProdutivaCreate) -> UnidadeProdutiva:
        return await self.create_unidade_produtiva(dados)


# Backward compatibility alias
FazendaService = UnidadeProdutivaService
