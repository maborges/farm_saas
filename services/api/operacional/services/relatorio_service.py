from uuid import UUID
from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_

from operacional.models.frota import Maquinario, OrdemServico, RegistroManutencao
from operacional.models.estoque import MovimentacaoEstoque, Deposito
from core.cadastros.models import ProdutoCatalogo
from agricola.operacoes.models import InsumoOperacao, OperacaoAgricola
from agricola.safras.models import Safra


class OperacionalRelatorioService:
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id

    # ── 1. Custo por Maquinário ────────────────────────────────────────────────

    async def custo_por_maquinario(
        self,
        unidade_produtiva_id: Optional[UUID] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> list[dict]:
        # Busca maquinários do tenant
        stmt_maq = select(Maquinario).where(Maquinario.tenant_id == self.tenant_id)
        if unidade_produtiva_id:
            stmt_maq = stmt_maq.where(Maquinario.unidade_produtiva_id == unidade_produtiva_id)
        maquinas = {m.id: m for m in (await self.session.execute(stmt_maq)).scalars().all()}

        if not maquinas:
            return []

        # Agrega OS por maquinário
        stmt_os = (
            select(
                OrdemServico.maquinario_id,
                func.count(OrdemServico.id).label("total_os"),
                func.sum(OrdemServico.custo_total_pecas).label("total_pecas"),
                func.sum(OrdemServico.custo_mao_obra).label("total_mao_obra"),
            )
            .where(
                OrdemServico.tenant_id == self.tenant_id,
                OrdemServico.maquinario_id.in_(list(maquinas.keys())),
                OrdemServico.status == "CONCLUIDA",
            )
            .group_by(OrdemServico.maquinario_id)
        )
        if data_inicio:
            stmt_os = stmt_os.where(OrdemServico.data_conclusao >= datetime.combine(data_inicio, datetime.min.time()))
        if data_fim:
            stmt_os = stmt_os.where(OrdemServico.data_conclusao <= datetime.combine(data_fim, datetime.max.time()))

        os_rows = {r.maquinario_id: r for r in (await self.session.execute(stmt_os)).all()}

        result = []
        for maq_id, maq in maquinas.items():
            row = os_rows.get(maq_id)
            total_pecas = float(row.total_pecas or 0) if row else 0.0
            total_mao_obra = float(row.total_mao_obra or 0) if row else 0.0
            total_os = int(row.total_os or 0) if row else 0

            result.append({
                "maquinario_id": str(maq_id),
                "nome": maq.nome,
                "tipo": maq.tipo,
                "status": maq.status,
                "horimetro_atual": maq.horimetro_atual,
                "total_os_concluidas": total_os,
                "custo_total_pecas": round(total_pecas, 2),
                "custo_total_mao_obra": round(total_mao_obra, 2),
                "custo_total": round(total_pecas + total_mao_obra, 2),
                "custo_por_hora": round(
                    (total_pecas + total_mao_obra) / maq.horimetro_atual, 2
                ) if maq.horimetro_atual > 0 else 0.0,
            })

        return sorted(result, key=lambda x: x["custo_total"], reverse=True)

    # ── 2. Consumo de Insumos por Safra ────────────────────────────────────────

    async def consumo_insumos_por_safra(
        self,
        safra_id: Optional[UUID] = None,
    ) -> list[dict]:
        # Busca operações do tenant
        stmt_ops = select(OperacaoAgricola.id, OperacaoAgricola.safra_id).where(
            OperacaoAgricola.tenant_id == self.tenant_id
        )
        if safra_id:
            stmt_ops = stmt_ops.where(OperacaoAgricola.safra_id == safra_id)
        ops = {r.id: r.safra_id for r in (await self.session.execute(stmt_ops)).all()}

        if not ops:
            return []

        # Busca nomes de safras
        stmt_safras = select(Safra).where(
            Safra.tenant_id == self.tenant_id,
            Safra.id.in_(set(ops.values()))
        )
        safras = {s.id: s for s in (await self.session.execute(stmt_safras)).scalars().all()}

        # Busca insumos usados
        stmt_ins = select(InsumoOperacao).where(
            InsumoOperacao.tenant_id == self.tenant_id,
            InsumoOperacao.operacao_id.in_(list(ops.keys())),
        )
        insumos = (await self.session.execute(stmt_ins)).scalars().all()

        # Busca nomes dos produtos
        produto_ids = {i.insumo_id for i in insumos}
        stmt_prods = select(Produto).where(Produto.id.in_(produto_ids))
        produtos = {p.id: p for p in (await self.session.execute(stmt_prods)).scalars().all()}

        # Agrega: (safra_id, produto_id) → qty, custo
        agg: dict[tuple, dict] = {}
        for ins in insumos:
            safra = ops.get(ins.operacao_id)
            if not safra:
                continue
            key = (safra, ins.insumo_id)
            if key not in agg:
                prod = produtos.get(ins.insumo_id)
                safra_obj = safras.get(safra)
                agg[key] = {
                    "safra_id": str(safra),
                    "safra_nome": f"{safra_obj.cultura} {safra_obj.ano_safra}" if safra_obj else str(safra),
                    "produto_id": str(ins.insumo_id),
                    "produto_nome": prod.nome if prod else str(ins.insumo_id),
                    "unidade_medida": prod.unidade_medida if prod else "—",
                    "quantidade_total": 0.0,
                    "custo_total": 0.0,
                    "aplicacoes": 0,
                }
            agg[key]["quantidade_total"] += float(ins.quantidade_total or 0)
            agg[key]["custo_total"] += float(ins.custo_total or 0)
            agg[key]["aplicacoes"] += 1

        result = list(agg.values())
        for r in result:
            r["quantidade_total"] = round(r["quantidade_total"], 4)
            r["custo_total"] = round(r["custo_total"], 2)

        return sorted(result, key=lambda x: (x["safra_nome"], -x["custo_total"]))

    # ── 3. Movimentações de Estoque por Período ────────────────────────────────

    async def movimentacoes_por_periodo(
        self,
        data_inicio: date,
        data_fim: date,
        unidade_produtiva_id: Optional[UUID] = None,
    ) -> list[dict]:
        # Depósitos do tenant (com filtro opcional por fazenda)
        stmt_deps = select(Deposito.id, Deposito.nome).where(Deposito.tenant_id == self.tenant_id)
        if unidade_produtiva_id:
            stmt_deps = stmt_deps.where(Deposito.unidade_produtiva_id == unidade_produtiva_id)
        dep_rows = (await self.session.execute(stmt_deps)).all()
        dep_ids = {r.id for r in dep_rows}
        dep_nomes = {r.id: r.nome for r in dep_rows}

        if not dep_ids:
            return []

        dt_ini = datetime.combine(data_inicio, datetime.min.time()).replace(tzinfo=timezone.utc)
        dt_fim = datetime.combine(data_fim, datetime.max.time()).replace(tzinfo=timezone.utc)

        stmt = (
            select(
                MovimentacaoEstoque.produto_id,
                MovimentacaoEstoque.tipo,
                func.count(MovimentacaoEstoque.id).label("qtd_movimentos"),
                func.sum(MovimentacaoEstoque.quantidade).label("quantidade_total"),
                func.sum(MovimentacaoEstoque.custo_total).label("custo_total"),
            )
            .where(
                MovimentacaoEstoque.deposito_id.in_(dep_ids),
                MovimentacaoEstoque.data_movimentacao >= dt_ini,
                MovimentacaoEstoque.data_movimentacao <= dt_fim,
            )
            .group_by(MovimentacaoEstoque.produto_id, MovimentacaoEstoque.tipo)
        )
        rows = (await self.session.execute(stmt)).all()

        # Busca nomes dos produtos
        produto_ids = {r.produto_id for r in rows}
        stmt_prods = select(Produto).where(Produto.id.in_(produto_ids))
        produtos = {p.id: p for p in (await self.session.execute(stmt_prods)).scalars().all()}

        result = []
        for r in rows:
            prod = produtos.get(r.produto_id)
            result.append({
                "produto_id": str(r.produto_id),
                "produto_nome": prod.nome if prod else str(r.produto_id),
                "unidade_medida": prod.unidade_medida if prod else "—",
                "tipo": r.tipo,
                "qtd_movimentos": int(r.qtd_movimentos or 0),
                "quantidade_total": round(float(r.quantidade_total or 0), 4),
                "custo_total": round(float(r.custo_total or 0), 2),
            })

        return sorted(result, key=lambda x: (x["produto_nome"], x["tipo"]))
