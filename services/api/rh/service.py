import uuid as _uuid
from uuid import UUID
from collections import defaultdict
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_

from core.base_service import BaseService
from rh.models import ColaboradorRH, LancamentoDiaria, Empreitada
from rh.schemas import ColaboradorCreate, DiarariaCreate, EmpreitadaCreate


class ColaboradorService(BaseService[ColaboradorRH]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(ColaboradorRH, session, tenant_id)

    async def criar(self, dados: ColaboradorCreate) -> ColaboradorRH:
        return await self.create(dados.model_dump())

    async def desativar(self, colaborador_id: UUID) -> ColaboradorRH:
        col = await self.get_or_fail(colaborador_id)
        col.ativo = False
        self.session.add(col)
        await self.session.commit()
        await self.session.refresh(col)
        return col


class DiariaService(BaseService[LancamentoDiaria]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(LancamentoDiaria, session, tenant_id)

    async def criar(self, dados: DiarariaCreate) -> LancamentoDiaria:
        return await self.create(dados.model_dump())

    async def pagar_lote(self, ids: list[UUID], data_pagamento: date | None = None) -> int:
        from sqlalchemy import update
        dp = data_pagamento or date.today()

        # Busca diarias + fazenda_id antes do update para integração financeira
        stmt_fetch = (
            select(LancamentoDiaria, ColaboradorRH.fazenda_id)
            .join(ColaboradorRH, LancamentoDiaria.colaborador_id == ColaboradorRH.id)
            .where(
                LancamentoDiaria.tenant_id == self.tenant_id,
                LancamentoDiaria.id.in_(ids),
                LancamentoDiaria.status == "PENDENTE",
            )
        )
        rows = list((await self.session.execute(stmt_fetch)).all())

        # Agrupa total por fazenda_id
        por_fazenda: dict[UUID | None, float] = defaultdict(float)
        for diaria, fazenda_id in rows:
            por_fazenda[fazenda_id] += float(diaria.valor_diaria or 0)

        # Cria Despesas por fazenda
        if rows:
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
            plano_id = (await self.session.execute(stmt_pc)).scalar()
            if plano_id:
                for fazenda_id, total in por_fazenda.items():
                    if fazenda_id and total > 0:
                        self.session.add(Despesa(
                            id=_uuid.uuid4(),
                            tenant_id=self.tenant_id,
                            fazenda_id=fazenda_id,
                            plano_conta_id=plano_id,
                            descricao=f"RH — Pagamento de Diárias ({len(ids)} lançamentos)",
                            valor_total=round(total, 2),
                            data_emissao=dp,
                            data_vencimento=dp,
                            data_pagamento=dp,
                            status="PAGO",
                        ))

        stmt = (
            update(LancamentoDiaria)
            .where(
                LancamentoDiaria.tenant_id == self.tenant_id,
                LancamentoDiaria.id.in_(ids),
                LancamentoDiaria.status == "PENDENTE",
            )
            .values(status="PAGO", data_pagamento=dp)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def listar_por_colaborador(self, colaborador_id: UUID) -> list[LancamentoDiaria]:
        stmt = (
            select(LancamentoDiaria)
            .where(
                LancamentoDiaria.tenant_id == self.tenant_id,
                LancamentoDiaria.colaborador_id == colaborador_id,
            )
            .order_by(LancamentoDiaria.data.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())


class EmpreitadaService(BaseService[Empreitada]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(Empreitada, session, tenant_id)

    async def criar(self, dados: EmpreitadaCreate) -> Empreitada:
        d = dados.model_dump()
        d["valor_total"] = round(dados.quantidade * dados.valor_unitario, 2)
        return await self.create(d)

    async def concluir(self, empreitada_id: UUID, quantidade_final: float | None, data_fim: date | None) -> Empreitada:
        emp = await self.get_or_fail(empreitada_id)
        if quantidade_final is not None:
            emp.quantidade = quantidade_final
            emp.valor_total = round(quantidade_final * float(emp.valor_unitario), 2)
        emp.data_fim = data_fim or date.today()
        emp.status = "CONCLUIDA"
        self.session.add(emp)
        await self.session.commit()
        await self.session.refresh(emp)
        return emp

    async def pagar(self, empreitada_id: UUID, data_pagamento: date | None = None) -> Empreitada:
        emp = await self.get_or_fail(empreitada_id)
        emp.status = "PAGA"
        emp.data_pagamento = data_pagamento or date.today()
        dp = emp.data_pagamento
        self.session.add(emp)

        # Integração Financeira: Despesa de Empreitada
        stmt_faz = select(ColaboradorRH.fazenda_id).where(ColaboradorRH.id == emp.colaborador_id)
        fazenda_id = (await self.session.execute(stmt_faz)).scalar()
        if fazenda_id and emp.valor_total and float(emp.valor_total) > 0:
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
            plano_id = (await self.session.execute(stmt_pc)).scalar()
            if plano_id:
                self.session.add(Despesa(
                    id=_uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    fazenda_id=fazenda_id,
                    plano_conta_id=plano_id,
                    descricao=f"RH — Empreitada: {emp.descricao}",
                    valor_total=round(float(emp.valor_total), 2),
                    data_emissao=dp,
                    data_vencimento=dp,
                    data_pagamento=dp,
                    status="PAGO",
                ))

        await self.session.commit()
        await self.session.refresh(emp)
        return emp


async def get_dashboard_rh(session: AsyncSession, tenant_id: UUID) -> dict:
    hoje = date.today()
    mes_inicio = date(hoje.year, hoje.month, 1)

    # Colaboradores
    stmt_col = select(
        func.count(ColaboradorRH.id).label("total"),
        func.sum(func.cast(ColaboradorRH.tipo_contrato == "DIARISTA", type_=None)).label("diaristas"),
        func.sum(func.cast(ColaboradorRH.tipo_contrato == "EMPREITEIRO", type_=None)).label("empreiteiros"),
    ).where(ColaboradorRH.tenant_id == tenant_id, ColaboradorRH.ativo == True)
    r_col = (await session.execute(stmt_col)).one()

    # Diárias do mês
    stmt_dia_mes = select(func.sum(LancamentoDiaria.valor_diaria)).where(
        LancamentoDiaria.tenant_id == tenant_id,
        LancamentoDiaria.data >= mes_inicio,
    )
    gasto_diarias = (await session.execute(stmt_dia_mes)).scalar() or 0.0

    # Diárias pendentes (total)
    stmt_dia_pend = select(func.sum(LancamentoDiaria.valor_diaria)).where(
        LancamentoDiaria.tenant_id == tenant_id,
        LancamentoDiaria.status == "PENDENTE",
    )
    pendente_diarias = (await session.execute(stmt_dia_pend)).scalar() or 0.0

    # Empreitadas do mês
    stmt_emp_mes = select(func.sum(Empreitada.valor_total)).where(
        Empreitada.tenant_id == tenant_id,
        Empreitada.data_inicio >= mes_inicio,
    )
    gasto_emp = (await session.execute(stmt_emp_mes)).scalar() or 0.0

    # Empreitadas abertas
    stmt_emp_ab = select(
        func.count(Empreitada.id),
        func.sum(Empreitada.valor_total),
    ).where(
        Empreitada.tenant_id == tenant_id,
        Empreitada.status.in_(["ABERTA", "CONCLUIDA"]),
    )
    r_emp = (await session.execute(stmt_emp_ab)).one()

    return {
        "total_colaboradores_ativos": r_col.total or 0,
        "total_diaristas": int(r_col.diaristas or 0),
        "total_empreiteiros": int(r_col.empreiteiros or 0),
        "gasto_diarias_mes": float(gasto_diarias),
        "gasto_empreitadas_mes": float(gasto_emp),
        "total_pendente_diarias": float(pendente_diarias),
        "total_pendente_empreitadas": float(r_emp[1] or 0),
        "empreitadas_abertas": int(r_emp[0] or 0),
    }
