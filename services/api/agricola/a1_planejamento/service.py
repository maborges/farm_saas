import uuid
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from core.exceptions import BusinessRuleError, EntityNotFoundError
from agricola.safras.models import Safra
from agricola.operacoes.models import OperacaoAgricola
from agricola.a1_planejamento.models import ItemOrcamentoSafra
from financeiro.models.rateio import Rateio
from agricola.a1_planejamento.schemas import (
    ItemOrcamentoCreate,
    ItemOrcamentoUpdate,
    ItemOrcamentoResponse,
    CustoCategoria,
    OrcamentoPrevisto,
    OrcamentoRealizado,
    DesvioOrcamento,
    OrcamentoSafraResponse,
    SafraKPI,
    CampanhasResponse,
)


class PlanejamentoService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def _get_safra(self, safra_id: uuid.UUID) -> Safra:
        stmt = select(Safra).where(
            Safra.id == safra_id,
            Safra.tenant_id == self.tenant_id,
        )
        safra = (await self.session.execute(stmt)).scalars().first()
        if not safra:
            raise EntityNotFoundError(f"Safra {safra_id} não encontrada.")
        return safra

    # ── Itens do Orçamento ────────────────────────────────────────────────

    async def listar_itens(self, safra_id: uuid.UUID) -> list[ItemOrcamentoSafra]:
        await self._get_safra(safra_id)
        stmt = select(ItemOrcamentoSafra).where(
            ItemOrcamentoSafra.tenant_id == self.tenant_id,
            ItemOrcamentoSafra.safra_id == safra_id,
        ).order_by(ItemOrcamentoSafra.categoria, ItemOrcamentoSafra.ordem)
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar_item(self, safra_id: uuid.UUID, data: ItemOrcamentoCreate) -> ItemOrcamentoSafra:
        await self._get_safra(safra_id)
        custo_total = round(data.quantidade * data.custo_unitario, 2)
        item = ItemOrcamentoSafra(
            tenant_id=self.tenant_id,
            safra_id=safra_id,
            categoria=data.categoria,
            descricao=data.descricao,
            quantidade=data.quantidade,
            unidade=data.unidade,
            custo_unitario=data.custo_unitario,
            custo_total=custo_total,
            ordem=data.ordem,
            observacoes=data.observacoes,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def atualizar_item(self, item_id: uuid.UUID, data: ItemOrcamentoUpdate) -> ItemOrcamentoSafra:
        stmt = select(ItemOrcamentoSafra).where(
            ItemOrcamentoSafra.id == item_id,
            ItemOrcamentoSafra.tenant_id == self.tenant_id,
        )
        item = (await self.session.execute(stmt)).scalars().first()
        if not item:
            raise EntityNotFoundError(f"Item de orçamento {item_id} não encontrado.")

        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(item, field, value)

        # Recalcula custo_total se quantidade ou custo_unitario mudaram
        if "quantidade" in updates or "custo_unitario" in updates:
            item.custo_total = round(float(item.quantidade) * float(item.custo_unitario), 2)

        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def deletar_item(self, item_id: uuid.UUID) -> None:
        stmt = select(ItemOrcamentoSafra).where(
            ItemOrcamentoSafra.id == item_id,
            ItemOrcamentoSafra.tenant_id == self.tenant_id,
        )
        item = (await self.session.execute(stmt)).scalars().first()
        if not item:
            raise EntityNotFoundError(f"Item de orçamento {item_id} não encontrado.")
        await self.session.delete(item)
        await self.session.flush()

    # ── Orçamento Previsto × Realizado ────────────────────────────────────

    def _por_categoria(self, agrupado: dict[str, float], area_ha: float, total: float) -> list[CustoCategoria]:
        return sorted([
            CustoCategoria(
                categoria=cat,
                custo_total=round(valor, 2),
                custo_por_ha=round(valor / area_ha, 2) if area_ha else 0.0,
                percentual=round(valor / total * 100, 2) if total else 0.0,
            )
            for cat, valor in agrupado.items()
        ], key=lambda x: x.custo_total, reverse=True)

    async def get_orcamento(self, safra_id: uuid.UUID) -> OrcamentoSafraResponse:
        safra = await self._get_safra(safra_id)
        area_ha = float(safra.area_plantada_ha or 1.0)

        # ── Previsto: itens do orçamento ──────────────────────────────────
        itens = await self.listar_itens(safra_id)
        itens_response = [ItemOrcamentoResponse.model_validate(i) for i in itens]

        previsto: OrcamentoPrevisto | None = None
        if itens:
            cat_prev: dict[str, float] = defaultdict(float)
            for item in itens:
                cat_prev[item.categoria] += float(item.custo_total)
            custo_prev_total = sum(cat_prev.values())

            receita_esperada = 0.0
            receita_ha = 0.0
            ponto_eq = None
            if safra.produtividade_meta_sc_ha and safra.preco_venda_previsto:
                receita_ha = float(safra.produtividade_meta_sc_ha) * float(safra.preco_venda_previsto)
                receita_esperada = round(receita_ha * area_ha, 2)
                custo_ha = custo_prev_total / area_ha if area_ha else 0
                if safra.preco_venda_previsto > 0:
                    ponto_eq = round(custo_ha / float(safra.preco_venda_previsto), 2)

            previsto = OrcamentoPrevisto(
                custo_total=round(custo_prev_total, 2),
                custo_por_ha=round(custo_prev_total / area_ha, 2),
                receita_esperada=receita_esperada,
                receita_por_ha=round(receita_ha, 2),
                margem_bruta=round(receita_esperada - custo_prev_total, 2),
                ponto_equilibrio_sc_ha=ponto_eq,
                por_categoria=self._por_categoria(cat_prev, area_ha, custo_prev_total),
            )
        elif safra.custo_previsto_ha:
            # Fallback: usa custo_previsto_ha da safra
            custo_prev_total = float(safra.custo_previsto_ha) * area_ha
            receita_esperada = 0.0
            ponto_eq = None
            if safra.produtividade_meta_sc_ha and safra.preco_venda_previsto:
                receita_ha = float(safra.produtividade_meta_sc_ha) * float(safra.preco_venda_previsto)
                receita_esperada = round(receita_ha * area_ha, 2)
                if safra.preco_venda_previsto > 0:
                    ponto_eq = round(float(safra.custo_previsto_ha) / float(safra.preco_venda_previsto), 2)
            previsto = OrcamentoPrevisto(
                custo_total=round(custo_prev_total, 2),
                custo_por_ha=float(safra.custo_previsto_ha),
                receita_esperada=receita_esperada,
                receita_por_ha=round(float(safra.produtividade_meta_sc_ha or 0) * float(safra.preco_venda_previsto or 0), 2),
                margem_bruta=round(receita_esperada - custo_prev_total, 2),
                ponto_equilibrio_sc_ha=ponto_eq,
                por_categoria=[],
            )

        # ── Realizado: operações agrícolas ────────────────────────────────
        ops_stmt = select(OperacaoAgricola).where(
            OperacaoAgricola.safra_id == safra_id,
            OperacaoAgricola.tenant_id == self.tenant_id,
        )
        operacoes = list((await self.session.execute(ops_stmt)).scalars().all())
        cat_real: dict[str, float] = defaultdict(float)
        custo_ops = 0.0
        for op in operacoes:
            custo_ops += float(op.custo_total or 0)
            cat_real[op.tipo] += float(op.custo_total or 0)

        # Rateios financeiros vinculados a esta safra
        rat_stmt = select(Rateio).where(
            Rateio.tenant_id == self.tenant_id,
            Rateio.safra_id == safra_id,
        )
        rateios = list((await self.session.execute(rat_stmt)).scalars().all())
        custo_rateios = sum(float(r.valor_rateado) for r in rateios)
        # Rateios entram como categoria OUTROS para não duplicar com operações
        if custo_rateios > 0:
            cat_real["DESPESA_FINANCEIRA"] = cat_real.get("DESPESA_FINANCEIRA", 0.0) + custo_rateios

        custo_real_total = custo_ops + custo_rateios
        realizado = OrcamentoRealizado(
            custo_operacoes=round(custo_ops, 2),
            custo_rateios=round(custo_rateios, 2),
            custo_total=round(custo_real_total, 2),
            custo_por_ha=round(custo_real_total / area_ha, 2),
            por_categoria=self._por_categoria(cat_real, area_ha, custo_real_total),
        )

        # ── Desvio ────────────────────────────────────────────────────────
        desvio: DesvioOrcamento | None = None
        if previsto and previsto.custo_total > 0:
            desvio_valor = custo_real_total - previsto.custo_total
            desvio_pct = round(desvio_valor / previsto.custo_total * 100, 2)
            status = "DENTRO" if abs(desvio_pct) <= 5 else "ACIMA" if desvio_pct > 0 else "ABAIXO"
            desvio = DesvioOrcamento(
                custo_desvio_valor=round(desvio_valor, 2),
                custo_desvio_pct=desvio_pct,
                status=status,
            )
        elif not previsto:
            desvio = DesvioOrcamento(
                custo_desvio_valor=custo_real_total,
                custo_desvio_pct=0.0,
                status="SEM_ORCAMENTO",
            )

        return OrcamentoSafraResponse(
            safra_id=safra_id,
            cultura=safra.cultura,
            ano_safra=safra.ano_safra,
            area_ha=area_ha,
            status_safra=safra.status,
            previsto=previsto,
            realizado=realizado,
            desvio=desvio,
            itens=itens_response,
        )

    # ── Visão Geral Campanhas ─────────────────────────────────────────────

    async def listar_campanhas(self, ano_safra: str | None = None) -> CampanhasResponse:
        stmt = select(Safra).where(Safra.tenant_id == self.tenant_id)
        if ano_safra:
            stmt = stmt.where(Safra.ano_safra == ano_safra)
        stmt = stmt.order_by(Safra.ano_safra.desc(), Safra.cultura)
        safras = list((await self.session.execute(stmt)).scalars().all())

        kpis: list[SafraKPI] = []
        total_area = 0.0
        total_prev = 0.0
        total_real = 0.0

        for s in safras:
            area = float(s.area_plantada_ha or 0)
            total_area += area

            custo_prev_ha = float(s.custo_previsto_ha) if s.custo_previsto_ha else None
            custo_real_ha = float(s.custo_realizado_ha) if s.custo_realizado_ha else None

            desvio_custo = None
            if custo_prev_ha and custo_real_ha and custo_prev_ha > 0:
                desvio_custo = round((custo_real_ha - custo_prev_ha) / custo_prev_ha * 100, 2)

            prod_meta = float(s.produtividade_meta_sc_ha) if s.produtividade_meta_sc_ha else None
            prod_real = float(s.produtividade_real_sc_ha) if s.produtividade_real_sc_ha else None

            desvio_prod = None
            if prod_meta and prod_real and prod_meta > 0:
                desvio_prod = round((prod_real - prod_meta) / prod_meta * 100, 2)

            receita_esp = None
            if prod_meta and s.preco_venda_previsto and area:
                receita_esp = round(prod_meta * float(s.preco_venda_previsto) * area, 2)

            if custo_prev_ha and area:
                total_prev += custo_prev_ha * area
            if custo_real_ha and area:
                total_real += custo_real_ha * area

            kpis.append(SafraKPI(
                safra_id=s.id,
                talhao_id=s.talhao_id,
                cultura=s.cultura,
                ano_safra=s.ano_safra,
                area_ha=area,
                status=s.status,
                custo_previsto_ha=custo_prev_ha,
                custo_realizado_ha=custo_real_ha,
                desvio_custo_pct=desvio_custo,
                produtividade_meta_sc_ha=prod_meta,
                produtividade_real_sc_ha=prod_real,
                desvio_prod_pct=desvio_prod,
                receita_esperada=receita_esp,
            ))

        return CampanhasResponse(
            ano_safra=ano_safra,
            total_area_ha=round(total_area, 2),
            total_custo_previsto=round(total_prev, 2),
            total_custo_realizado=round(total_real, 2),
            safras=kpis,
        )
