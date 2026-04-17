import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.base_service import BaseService
from core.exceptions import EntityNotFoundError, BusinessRuleError
from pecuaria.models.manejo import ManejoLote
from pecuaria.models.lote import LoteBovino
from pecuaria.schemas.manejo_schema import ManejoLoteCreate

TIPOS_VALIDOS = {
    "NASCIMENTO", "MORTE", "PESAGEM", "VACINACAO",
    "TRANSFERENCIA", "MEDICACAO", "VENDA", "ABATE",
}

# Tipos que geram Despesa automaticamente
TIPOS_DESPESA = {"VACINACAO", "MEDICACAO"}
# Tipos que geram Receita automaticamente
TIPOS_RECEITA = {"VENDA", "ABATE"}


class ManejoLoteService(BaseService[ManejoLote]):
    """
    Service para registro de eventos de vida no rebanho.

    Args:
        tenant_id: ID do tenant para isolamento de dados.

    Raises:
        BusinessRuleError: Se o tipo de evento for inválido ou o lote não existir.
    """

    def __init__(self, tenant_id: uuid.UUID):
        super().__init__(ManejoLote, None, tenant_id)

    async def listar_por_lote(
        self, db: AsyncSession, *, lote_id: uuid.UUID
    ) -> list[ManejoLote]:
        """Lista todos os eventos de um lote específico."""
        stmt = (
            select(self.model)
            .where(
                self.model.tenant_id == self.tenant_id,
                self.model.lote_id == lote_id,
            )
            .order_by(self.model.data_evento.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def listar_todos(self, db: AsyncSession) -> list[ManejoLote]:
        """Lista todos os eventos do tenant ordenados por data."""
        stmt = (
            select(self.model)
            .where(self.model.tenant_id == self.tenant_id)
            .order_by(self.model.data_evento.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def registrar_evento(
        self, db: AsyncSession, *, obj_in: ManejoLoteCreate
    ) -> ManejoLote:
        """
        Registra um evento de manejo (nascimento, morte, pesagem, etc.).

        Raises:
            BusinessRuleError: Se tipo_evento inválido ou lote não pertence ao tenant.
        """
        if obj_in.tipo_evento not in TIPOS_VALIDOS:
            raise BusinessRuleError(
                f"Tipo de evento inválido. Use: {', '.join(sorted(TIPOS_VALIDOS))}"
            )

        # Verifica que o lote pertence ao tenant
        stmt_lote = select(LoteBovino).where(
            LoteBovino.id == obj_in.lote_id,
            LoteBovino.tenant_id == self.tenant_id,
        )
        lote = (await db.execute(stmt_lote)).scalars().first()
        if not lote:
            raise EntityNotFoundError(f"Lote {obj_in.lote_id} não encontrado neste tenant.")

        obj_data = obj_in.model_dump()
        if obj_data.get("data_evento") is None:
            obj_data["data_evento"] = date.today()

        db_manejo = ManejoLote(**obj_data, tenant_id=self.tenant_id)
        db.add(db_manejo)
        await db.flush()
        await db.refresh(db_manejo)

        # ── Integração Financeira ─────────────────────────────────────────
        tipo = obj_in.tipo_evento
        data_ev = db_manejo.data_evento

        if tipo in TIPOS_DESPESA and (obj_in.custo_total or 0) > 0:
            from financeiro.models.despesa import Despesa
            from financeiro.models.plano_conta import PlanoConta
            stmt_pc = (
                select(PlanoConta.id)
                .where(
                    PlanoConta.tenant_id == self.tenant_id,
                    PlanoConta.categoria_rfb == "CUSTEIO",
                    PlanoConta.natureza == "ANALITICA",
                    PlanoConta.ativo == True,
                )
                .limit(1)
            )
            plano_id = (await db.execute(stmt_pc)).scalar()
            if plano_id:
                despesa = Despesa(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    unidade_produtiva_id=lote.unidade_produtiva_id,
                    plano_conta_id=plano_id,
                    descricao=f"Pecuária — {tipo.capitalize()} Lote {lote.identificacao}",
                    valor_total=float(obj_in.custo_total),
                    data_emissao=data_ev,
                    data_vencimento=data_ev,
                    data_pagamento=data_ev,
                    status="PAGO",
                )
                db.add(despesa)

        elif tipo in TIPOS_RECEITA and (obj_in.valor_venda or 0) > 0:
            from financeiro.models.receita import Receita
            from financeiro.models.plano_conta import PlanoConta
            stmt_pc = (
                select(PlanoConta.id)
                .where(
                    PlanoConta.tenant_id == self.tenant_id,
                    PlanoConta.categoria_rfb == "RECEITA_ATIVIDADE",
                    PlanoConta.natureza == "ANALITICA",
                    PlanoConta.ativo == True,
                )
                .limit(1)
            )
            plano_id = (await db.execute(stmt_pc)).scalar()
            if plano_id:
                receita = Receita(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    unidade_produtiva_id=lote.unidade_produtiva_id,
                    plano_conta_id=plano_id,
                    descricao=f"Pecuária — {tipo.capitalize()} Lote {lote.identificacao}",
                    valor_total=float(obj_in.valor_venda),
                    data_emissao=data_ev,
                    data_vencimento=data_ev,
                    data_recebimento=data_ev,
                    status="RECEBIDO",
                )
                db.add(receita)

        return db_manejo
