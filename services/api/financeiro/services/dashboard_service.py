import uuid
from collections import defaultdict
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from financeiro.models.despesa import Despesa
from financeiro.models.receita import Receita
from financeiro.models.plano_conta import PlanoConta
from financeiro.schemas.relatorio_schema import (
    AlertaFinanceiro,
    DashboardFinanceiroResponse,
    TopCategoria,
    VencimentoProximo,
)


class DashboardService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def _planos(self) -> dict[uuid.UUID, PlanoConta]:
        stmt = select(PlanoConta).where(PlanoConta.tenant_id == self.tenant_id)
        return {
            pc.id: pc
            for pc in (await self.session.execute(stmt)).scalars().all()
        }

    async def resumo(
        self, fazenda_id: uuid.UUID | None = None
    ) -> DashboardFinanceiroResponse:
        hoje = date.today()
        inicio_mes = hoje.replace(day=1)

        planos = await self._planos()

        # ── Carrega receitas abertas + mês corrente ───────────────────────
        rec_stmt = select(Receita).where(
            Receita.tenant_id == self.tenant_id,
            Receita.ativo == True,
        )
        if fazenda_id:
            rec_stmt = rec_stmt.where(Receita.fazenda_id == fazenda_id)
        receitas = list((await self.session.execute(rec_stmt)).scalars().all())

        # ── Carrega despesas abertas + mês corrente ───────────────────────
        desp_stmt = select(Despesa).where(
            Despesa.tenant_id == self.tenant_id,
            Despesa.ativo == True,
        )
        if fazenda_id:
            desp_stmt = desp_stmt.where(Despesa.fazenda_id == fazenda_id)
        despesas = list((await self.session.execute(desp_stmt)).scalars().all())

        # ── Resumo do mês corrente ────────────────────────────────────────
        total_recebido_mes = sum(
            float(r.valor_recebido or r.valor_total)
            for r in receitas
            if r.status in {"RECEBIDO", "RECEBIDO_PARCIAL"}
            and r.data_recebimento and r.data_recebimento >= inicio_mes
        )
        total_pago_mes = sum(
            float(d.valor_pago or d.valor_total)
            for d in despesas
            if d.status in {"PAGO", "PAGO_PARCIAL"}
            and d.data_pagamento and d.data_pagamento >= inicio_mes
        )

        # ── Posição geral (abertos) ───────────────────────────────────────
        total_a_receber = sum(
            float(r.valor_total) for r in receitas if r.status == "A_RECEBER"
        )
        total_a_pagar = sum(
            float(d.valor_total) for d in despesas if d.status in {"A_PAGAR", "ATRASADO"}
        )
        total_atrasado_receitas = sum(
            float(r.valor_total)
            for r in receitas
            if r.status == "A_RECEBER" and r.data_vencimento < hoje
        )
        total_atrasado_despesas = sum(
            float(d.valor_total)
            for d in despesas
            if d.status in {"A_PAGAR", "ATRASADO"} and d.data_vencimento < hoje
        )

        # ── Próximos vencimentos ──────────────────────────────────────────
        vencendo_7d: list[VencimentoProximo] = []
        vencendo_8_15d: list[VencimentoProximo] = []
        vencendo_16_30d: list[VencimentoProximo] = []

        for r in receitas:
            if r.status != "A_RECEBER" or r.data_vencimento < hoje:
                continue
            dias = (r.data_vencimento - hoje).days
            item = VencimentoProximo(
                id=r.id,
                tipo="RECEITA",
                descricao=r.descricao,
                valor=float(r.valor_total),
                data_vencimento=r.data_vencimento,
                dias_restantes=dias,
                pessoa_nome=r.cliente,
            )
            if dias <= 7:
                vencendo_7d.append(item)
            elif dias <= 15:
                vencendo_8_15d.append(item)
            elif dias <= 30:
                vencendo_16_30d.append(item)

        for d in despesas:
            if d.status not in {"A_PAGAR", "ATRASADO"} or d.data_vencimento < hoje:
                continue
            dias = (d.data_vencimento - hoje).days
            item = VencimentoProximo(
                id=d.id,
                tipo="DESPESA",
                descricao=d.descricao,
                valor=float(d.valor_total),
                data_vencimento=d.data_vencimento,
                dias_restantes=dias,
                pessoa_nome=d.fornecedor,
            )
            if dias <= 7:
                vencendo_7d.append(item)
            elif dias <= 15:
                vencendo_8_15d.append(item)
            elif dias <= 30:
                vencendo_16_30d.append(item)

        _sort = lambda lst: sorted(lst, key=lambda x: x.data_vencimento)
        vencendo_7d = _sort(vencendo_7d)
        vencendo_8_15d = _sort(vencendo_8_15d)
        vencendo_16_30d = _sort(vencendo_16_30d)

        # ── Top 5 categorias do mês corrente ─────────────────────────────
        desp_mes: dict[uuid.UUID, list[float]] = defaultdict(list)
        for d in despesas:
            if d.status in {"PAGO", "PAGO_PARCIAL"} and d.data_pagamento and d.data_pagamento >= inicio_mes:
                desp_mes[d.plano_conta_id].append(float(d.valor_pago or d.valor_total))

        rec_mes: dict[uuid.UUID, list[float]] = defaultdict(list)
        for r in receitas:
            if r.status in {"RECEBIDO", "RECEBIDO_PARCIAL"} and r.data_recebimento and r.data_recebimento >= inicio_mes:
                rec_mes[r.plano_conta_id].append(float(r.valor_recebido or r.valor_total))

        def _top5(agrupado: dict) -> list[TopCategoria]:
            items = [
                TopCategoria(
                    plano_conta_nome=planos[pc_id].nome if pc_id in planos else "—",
                    categoria_rfb=planos[pc_id].categoria_rfb if pc_id in planos else None,
                    total=round(sum(vals), 2),
                    quantidade=len(vals),
                )
                for pc_id, vals in agrupado.items()
            ]
            return sorted(items, key=lambda x: x.total, reverse=True)[:5]

        top_despesas = _top5(desp_mes)
        top_receitas = _top5(rec_mes)

        # ── Alertas ───────────────────────────────────────────────────────
        alertas: list[AlertaFinanceiro] = []

        if total_atrasado_despesas > 0:
            alertas.append(AlertaFinanceiro(
                tipo="ATRASADO",
                nivel="CRITICO",
                mensagem=f"Você tem R$ {total_atrasado_despesas:,.2f} em contas a pagar vencidas.",
                valor=total_atrasado_despesas,
            ))
        if total_atrasado_receitas > 0:
            alertas.append(AlertaFinanceiro(
                tipo="ATRASADO",
                nivel="ALERTA",
                mensagem=f"Há R$ {total_atrasado_receitas:,.2f} em contas a receber vencidas.",
                valor=total_atrasado_receitas,
            ))
        venc_7d_desp = sum(i.valor for i in vencendo_7d if i.tipo == "DESPESA")
        if venc_7d_desp > 0:
            alertas.append(AlertaFinanceiro(
                tipo="VENCIMENTO_PROXIMO",
                nivel="ALERTA",
                mensagem=f"R$ {venc_7d_desp:,.2f} em despesas vencem nos próximos 7 dias.",
                valor=venc_7d_desp,
                data_referencia=hoje + timedelta(days=7),
            ))
        saldo_mes = round(total_recebido_mes - total_pago_mes, 2)
        if saldo_mes < 0:
            alertas.append(AlertaFinanceiro(
                tipo="SALDO_NEGATIVO",
                nivel="CRITICO",
                mensagem=f"Saldo do mês negativo: R$ {saldo_mes:,.2f}.",
                valor=saldo_mes,
            ))

        return DashboardFinanceiroResponse(
            data_referencia=hoje,
            fazenda_id=fazenda_id,
            total_recebido_mes=round(total_recebido_mes, 2),
            total_pago_mes=round(total_pago_mes, 2),
            saldo_mes=saldo_mes,
            total_a_receber=round(total_a_receber, 2),
            total_a_pagar=round(total_a_pagar, 2),
            total_atrasado_receitas=round(total_atrasado_receitas, 2),
            total_atrasado_despesas=round(total_atrasado_despesas, 2),
            vencendo_7d=vencendo_7d,
            vencendo_8_15d=vencendo_8_15d,
            vencendo_16_30d=vencendo_16_30d,
            top_despesas=top_despesas,
            top_receitas=top_receitas,
            alertas=alertas,
        )
