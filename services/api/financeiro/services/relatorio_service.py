import uuid
from collections import defaultdict
from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from financeiro.models.despesa import Despesa
from financeiro.models.receita import Receita
from financeiro.models.rateio import Rateio
from agricola.safras.models import Safra
from agricola.talhoes.models import Talhao
from financeiro.models.plano_conta import PlanoConta
from financeiro.schemas.relatorio_schema import (
    FluxoCaixaPeriodo,
    FluxoCaixaTotais,
    FluxoCaixaResponse,
    LivroCaixaLancamento,
    LivroCaixaGrupo,
    LivroCaixaResponse,
    DREResponse,
    CentroCustoCategoria,
    CentroCusto,
    CentroCustoResponse,
)

STATUS_REALIZADO_RECEITA = {"RECEBIDO", "RECEBIDO_PARCIAL"}
STATUS_REALIZADO_DESPESA = {"PAGO", "PAGO_PARCIAL"}
STATUS_PREVISTO_RECEITA = {"A_RECEBER"}
STATUS_PREVISTO_DESPESA = {"A_PAGAR", "ATRASADO"}


def _primeiro_dia(d: date) -> date:
    return d.replace(day=1)


def _meses_entre(inicio: date, fim: date) -> list[date]:
    meses = []
    atual = _primeiro_dia(inicio)
    fim_mes = _primeiro_dia(fim)
    while atual <= fim_mes:
        meses.append(atual)
        atual += relativedelta(months=1)
    return meses


class RelatorioService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def _carregar_receitas(
        self, data_inicio: date, data_fim: date, fazenda_id: uuid.UUID | None
    ) -> list[Receita]:
        stmt = select(Receita).where(
            Receita.tenant_id == self.tenant_id,
            Receita.ativo == True,
        )
        if fazenda_id:
            stmt = stmt.where(Receita.fazenda_id == fazenda_id)
        # Inclui tudo com recebimento OU vencimento dentro do período
        stmt = stmt.where(
            (
                (Receita.data_recebimento >= data_inicio) &
                (Receita.data_recebimento <= data_fim)
            ) | (
                (Receita.data_vencimento >= data_inicio) &
                (Receita.data_vencimento <= data_fim)
            )
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def _carregar_despesas(
        self, data_inicio: date, data_fim: date, fazenda_id: uuid.UUID | None
    ) -> list[Despesa]:
        stmt = select(Despesa).where(
            Despesa.tenant_id == self.tenant_id,
            Despesa.ativo == True,
        )
        if fazenda_id:
            stmt = stmt.where(Despesa.fazenda_id == fazenda_id)
        stmt = stmt.where(
            (
                (Despesa.data_pagamento >= data_inicio) &
                (Despesa.data_pagamento <= data_fim)
            ) | (
                (Despesa.data_vencimento >= data_inicio) &
                (Despesa.data_vencimento <= data_fim)
            )
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def fluxo_caixa(
        self,
        data_inicio: date,
        data_fim: date,
        fazenda_id: uuid.UUID | None = None,
    ) -> FluxoCaixaResponse:
        receitas = await self._carregar_receitas(data_inicio, data_fim, fazenda_id)
        despesas = await self._carregar_despesas(data_inicio, data_fim, fazenda_id)

        meses = _meses_entre(data_inicio, data_fim)
        periodos_map: dict[date, FluxoCaixaPeriodo] = {
            m: FluxoCaixaPeriodo(periodo=m) for m in meses
        }

        # Processa receitas
        for r in receitas:
            # Realizado: registra no mês do recebimento efetivo
            if r.status in STATUS_REALIZADO_RECEITA and r.data_recebimento:
                mes = _primeiro_dia(r.data_recebimento)
                if mes in periodos_map:
                    valor = float(r.valor_recebido or r.valor_total)
                    periodos_map[mes].receitas_realizadas += valor

            # Previsto: registra no mês do vencimento
            if r.status in STATUS_PREVISTO_RECEITA:
                mes = _primeiro_dia(r.data_vencimento)
                if mes in periodos_map:
                    periodos_map[mes].receitas_previstas += float(r.valor_total)

        # Processa despesas
        for d in despesas:
            if d.status in STATUS_REALIZADO_DESPESA and d.data_pagamento:
                mes = _primeiro_dia(d.data_pagamento)
                if mes in periodos_map:
                    valor = float(d.valor_pago or d.valor_total)
                    periodos_map[mes].despesas_realizadas += valor

            if d.status in STATUS_PREVISTO_DESPESA:
                mes = _primeiro_dia(d.data_vencimento)
                if mes in periodos_map:
                    periodos_map[mes].despesas_previstas += float(d.valor_total)

        # Calcula saldos e acumulado
        saldo_acumulado = 0.0
        for mes in meses:
            p = periodos_map[mes]
            p.receitas_realizadas = round(p.receitas_realizadas, 2)
            p.despesas_realizadas = round(p.despesas_realizadas, 2)
            p.receitas_previstas = round(p.receitas_previstas, 2)
            p.despesas_previstas = round(p.despesas_previstas, 2)
            p.saldo_realizado = round(p.receitas_realizadas - p.despesas_realizadas, 2)
            p.saldo_previsto = round(p.receitas_previstas - p.despesas_previstas, 2)
            saldo_acumulado += p.saldo_realizado
            p.saldo_acumulado = round(saldo_acumulado, 2)

        periodos = [periodos_map[m] for m in meses]

        totais = FluxoCaixaTotais(
            total_receitas_realizadas=round(sum(p.receitas_realizadas for p in periodos), 2),
            total_despesas_realizadas=round(sum(p.despesas_realizadas for p in periodos), 2),
            total_saldo_realizado=round(sum(p.saldo_realizado for p in periodos), 2),
            total_receitas_previstas=round(sum(p.receitas_previstas for p in periodos), 2),
            total_despesas_previstas=round(sum(p.despesas_previstas for p in periodos), 2),
            total_saldo_previsto=round(sum(p.saldo_previsto for p in periodos), 2),
        )

        return FluxoCaixaResponse(
            data_inicio=data_inicio,
            data_fim=data_fim,
            fazenda_id=fazenda_id,
            periodos=periodos,
            totais=totais,
        )

    async def livro_caixa(
        self,
        competencia_inicio: date,
        competencia_fim: date,
        fazenda_id: uuid.UUID | None = None,
    ) -> LivroCaixaResponse:
        """
        Livro Caixa do Produtor Rural (RFB).
        Agrupa lançamentos realizados por categoria_rfb do plano de contas.
        Filtra por campo `competencia` quando preenchido, senão usa data_recebimento/data_pagamento.
        """
        # Carrega planos de conta para lookup
        pc_stmt = select(PlanoConta).where(PlanoConta.tenant_id == self.tenant_id)
        planos = {
            pc.id: pc
            for pc in (await self.session.execute(pc_stmt)).scalars().all()
        }

        lancamentos: list[LivroCaixaLancamento] = []

        # Receitas realizadas
        rec_stmt = select(Receita).where(
            Receita.tenant_id == self.tenant_id,
            Receita.ativo == True,
            Receita.status.in_(STATUS_REALIZADO_RECEITA),
        )
        if fazenda_id:
            rec_stmt = rec_stmt.where(Receita.fazenda_id == fazenda_id)

        receitas = list((await self.session.execute(rec_stmt)).scalars().all())
        for r in receitas:
            # Usa competencia se preenchida, senão data_recebimento
            data_ref = r.competencia or r.data_recebimento
            if not data_ref or not (competencia_inicio <= data_ref <= competencia_fim):
                continue
            pc = planos.get(r.plano_conta_id)
            lancamentos.append(LivroCaixaLancamento(
                data=data_ref,
                descricao=r.descricao,
                tipo="RECEITA",
                categoria_rfb=pc.categoria_rfb if pc else None,
                plano_conta_nome=pc.nome if pc else "—",
                valor=float(r.valor_recebido or r.valor_total),
                forma=r.forma_recebimento,
                documento=r.numero_nf,
            ))

        # Despesas realizadas
        desp_stmt = select(Despesa).where(
            Despesa.tenant_id == self.tenant_id,
            Despesa.ativo == True,
            Despesa.status.in_(STATUS_REALIZADO_DESPESA),
        )
        if fazenda_id:
            desp_stmt = desp_stmt.where(Despesa.fazenda_id == fazenda_id)

        despesas = list((await self.session.execute(desp_stmt)).scalars().all())
        for d in despesas:
            data_ref = d.competencia or d.data_pagamento
            if not data_ref or not (competencia_inicio <= data_ref <= competencia_fim):
                continue
            pc = planos.get(d.plano_conta_id)
            lancamentos.append(LivroCaixaLancamento(
                data=data_ref,
                descricao=d.descricao,
                tipo="DESPESA",
                categoria_rfb=pc.categoria_rfb if pc else None,
                plano_conta_nome=pc.nome if pc else "—",
                valor=float(d.valor_pago or d.valor_total),
                forma=d.forma_pagamento,
                documento=d.numero_nf,
            ))

        # Agrupa por (categoria_rfb, tipo)
        grupos_map: dict[tuple, list[LivroCaixaLancamento]] = defaultdict(list)
        for l in sorted(lancamentos, key=lambda x: x.data):
            key = (l.categoria_rfb or "SEM_CATEGORIA", l.tipo)
            grupos_map[key].append(l)

        grupos = [
            LivroCaixaGrupo(
                categoria_rfb=key[0],
                tipo=key[1],
                total=round(sum(l.valor for l in items), 2),
                lancamentos=items,
            )
            for key, items in sorted(grupos_map.items())
        ]

        total_receitas = round(sum(g.total for g in grupos if g.tipo == "RECEITA"), 2)
        total_despesas = round(sum(g.total for g in grupos if g.tipo == "DESPESA"), 2)

        return LivroCaixaResponse(
            competencia_inicio=competencia_inicio,
            competencia_fim=competencia_fim,
            fazenda_id=fazenda_id,
            total_receitas=total_receitas,
            total_despesas=total_despesas,
            resultado=round(total_receitas - total_despesas, 2),
            grupos=grupos,
        )

    async def dre(
        self,
        data_inicio: date,
        data_fim: date,
        fazenda_id: uuid.UUID | None = None,
    ) -> DREResponse:
        """DRE simplificado: agrupa por categoria_rfb do plano de contas."""
        # Reutiliza o livro_caixa com range de competência = período do DRE
        lc = await self.livro_caixa(data_inicio, data_fim, fazenda_id)

        totais_rfb: dict[tuple, float] = defaultdict(float)
        for g in lc.grupos:
            totais_rfb[(g.categoria_rfb, g.tipo)] += g.total

        receita_atividade = totais_rfb.get(("RECEITA_ATIVIDADE", "RECEITA"), 0.0)
        outras_receitas = totais_rfb.get(("RECEITA_FORA_ATIVIDADE", "RECEITA"), 0.0)
        custeio = totais_rfb.get(("CUSTEIO", "DESPESA"), 0.0)
        investimento = totais_rfb.get(("INVESTIMENTO", "DESPESA"), 0.0)
        nao_dedutivel = totais_rfb.get(("NAO_DEDUTIVEL", "DESPESA"), 0.0)

        resultado_atividade = round(receita_atividade - custeio, 2)
        resultado_liquido = round(resultado_atividade + outras_receitas - nao_dedutivel, 2)

        return DREResponse(
            data_inicio=data_inicio,
            data_fim=data_fim,
            fazenda_id=fazenda_id,
            receita_bruta=round(receita_atividade, 2),
            total_custeio=round(custeio, 2),
            total_investimento=round(investimento, 2),
            total_nao_dedutivel=round(nao_dedutivel, 2),
            resultado_atividade_rural=resultado_atividade,
            outras_receitas=round(outras_receitas, 2),
            resultado_liquido=resultado_liquido,
        )

    async def centro_custos(
        self,
        data_inicio: date,
        data_fim: date,
        fazenda_id: uuid.UUID | None = None,
        safra_id: uuid.UUID | None = None,
    ) -> CentroCustoResponse:
        """
        Custo por centro de custo (safra/talhão).
        Considera apenas despesas pagas (PAGO/PAGO_PARCIAL) com rateios no período.
        """
        # Lookups
        planos_stmt = select(PlanoConta).where(PlanoConta.tenant_id == self.tenant_id)
        planos = {
            pc.id: pc
            for pc in (await self.session.execute(planos_stmt)).scalars().all()
        }

        safras_stmt = select(Safra).where(Safra.tenant_id == self.tenant_id)
        safras = {
            s.id: s
            for s in (await self.session.execute(safras_stmt)).scalars().all()
        }

        talhoes_stmt = select(Talhao).where(Talhao.tenant_id == self.tenant_id)
        talhoes = {
            t.id: t
            for t in (await self.session.execute(talhoes_stmt)).scalars().all()
        }

        # Despesas pagas no período
        desp_stmt = select(Despesa).where(
            Despesa.tenant_id == self.tenant_id,
            Despesa.ativo == True,
            Despesa.status.in_({"PAGO", "PAGO_PARCIAL"}),
            Despesa.data_pagamento >= data_inicio,
            Despesa.data_pagamento <= data_fim,
        )
        if fazenda_id:
            desp_stmt = desp_stmt.where(Despesa.fazenda_id == fazenda_id)
        despesas_map = {
            d.id: d
            for d in (await self.session.execute(desp_stmt)).scalars().all()
        }

        if not despesas_map:
            return CentroCustoResponse(
                data_inicio=data_inicio,
                data_fim=data_fim,
                fazenda_id=fazenda_id,
                total_geral=0.0,
                centros=[],
            )

        # Rateios das despesas do período
        rat_stmt = select(Rateio).where(
            Rateio.tenant_id == self.tenant_id,
            Rateio.despesa_id.in_(list(despesas_map.keys())),
        )
        if safra_id:
            rat_stmt = rat_stmt.where(Rateio.safra_id == safra_id)
        rateios = list((await self.session.execute(rat_stmt)).scalars().all())

        # Agrupa por (safra_id, talhao_id) → plano_conta_id → [valores]
        grupos: dict[tuple, dict[uuid.UUID, list[float]]] = defaultdict(lambda: defaultdict(list))
        for r in rateios:
            key = (r.safra_id, r.talhao_id)
            desp = despesas_map.get(r.despesa_id)
            if desp:
                grupos[key][desp.plano_conta_id].append(float(r.valor_rateado))

        centros: list[CentroCusto] = []
        for (s_id, t_id), por_plano in sorted(grupos.items(), key=lambda x: str(x[0])):
            safra = safras.get(s_id) if s_id else None
            talhao = talhoes.get(t_id) if t_id else None

            categorias = [
                CentroCustoCategoria(
                    plano_conta_nome=planos[pc_id].nome if pc_id in planos else "—",
                    categoria_rfb=planos[pc_id].categoria_rfb if pc_id in planos else None,
                    total_rateado=round(sum(vals), 2),
                    quantidade=len(vals),
                )
                for pc_id, vals in sorted(por_plano.items(), key=lambda x: str(x[0]))
            ]
            total = round(sum(c.total_rateado for c in categorias), 2)

            centros.append(CentroCusto(
                safra_id=s_id,
                safra_nome=f"{safra.cultura} {safra.ano_safra}" if safra else None,
                talhao_id=t_id,
                talhao_nome=talhao.nome if talhao else None,
                total_rateado=total,
                por_categoria=sorted(categorias, key=lambda x: x.total_rateado, reverse=True),
            ))

        centros.sort(key=lambda x: x.total_rateado, reverse=True)
        total_geral = round(sum(c.total_rateado for c in centros), 2)

        return CentroCustoResponse(
            data_inicio=data_inicio,
            data_fim=data_fim,
            fazenda_id=fazenda_id,
            total_geral=total_geral,
            centros=centros,
        )
