from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from agricola.safras.models import Safra
from agricola.operacoes.models import OperacaoAgricola
from agricola.checklist.models import SafraChecklistItem
from agricola.fenologia.models import SafraFenologiaRegistro, FenologiaEscala
from agricola.monitoramento.models import MonitoramentoPragas
from agricola.romaneios.models import RomaneioColheita
from agricola.safras.models import SAFRA_FASES_ORDEM
from core.exceptions import EntityNotFoundError
from financeiro.models.despesa import Despesa
from financeiro.models.receita import Receita
from agricola.dashboard.schemas import SafraResumoFinanceiro, FinanceiroResumo


class DashboardAgricolaService:
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def resumo(self, fazenda_ids: list[UUID] | None = None) -> dict:
        """Retorna todos os dados do dashboard em uma única chamada."""

        # ── Safras ───────────────────────────────────────────────────────────
        stmt_safras = select(Safra).where(Safra.tenant_id == self.tenant_id)
        safras = list((await self.session.execute(stmt_safras)).scalars().all())

        safras_ativas = [s for s in safras if s.status not in ("ENCERRADA", "CANCELADA")]
        safras_encerradas = [s for s in safras if s.status == "ENCERRADA"]
        safra_ids_ativas = [s.id for s in safras_ativas]

        # Por fase
        por_fase: dict[str, list[dict]] = {f: [] for f in SAFRA_FASES_ORDEM}
        for s in safras_ativas:
            if s.status in por_fase:
                por_fase[s.status].append({
                    "id": str(s.id),
                    "cultura": s.cultura,
                    "ano_safra": s.ano_safra,
                    "cultivar_nome": s.cultivar_nome,
                    "area_plantada_ha": float(s.area_plantada_ha or 0),
                    "produtividade_meta_sc_ha": float(s.produtividade_meta_sc_ha or 0),
                    "custo_previsto_ha": float(s.custo_previsto_ha or 0),
                    "custo_realizado_ha": float(s.custo_realizado_ha or 0),
                    "status": s.status,
                })

        # ── KPIs executivos ───────────────────────────────────────────────────
        area_total = sum(float(s.area_plantada_ha or 0) for s in safras_ativas)

        stmt_custo = select(func.coalesce(func.sum(OperacaoAgricola.custo_total), 0)).where(
            OperacaoAgricola.tenant_id == self.tenant_id,
            OperacaoAgricola.safra_id.in_(safra_ids_ativas) if safra_ids_ativas else False,
        )
        custo_acumulado = float((await self.session.execute(stmt_custo)).scalar() or 0)

        meta_total_sc = sum(
            float(s.produtividade_meta_sc_ha or 0) * float(s.area_plantada_ha or 0)
            for s in safras_ativas
        )

        # ── Romaneios: sacas e receita acumuladas ─────────────────────────────
        sacas_total = 0.0
        receita_romaneios = 0.0
        if safra_ids_ativas:
            stmt_rom = select(
                func.coalesce(func.sum(RomaneioColheita.sacas_60kg), 0),
                func.coalesce(func.sum(RomaneioColheita.receita_total), 0),
            ).where(
                RomaneioColheita.tenant_id == self.tenant_id,
                RomaneioColheita.safra_id.in_(safra_ids_ativas),
            )
            row_rom = (await self.session.execute(stmt_rom)).first()
            if row_rom:
                sacas_total = float(row_rom[0] or 0)
                receita_romaneios = float(row_rom[1] or 0)

        # ── Alertas de checklist ──────────────────────────────────────────────
        alertas_checklist: list[dict] = []
        for s in safras_ativas:
            stmt_pend = select(func.count(SafraChecklistItem.id)).where(
                SafraChecklistItem.safra_id == s.id,
                SafraChecklistItem.tenant_id == self.tenant_id,
                SafraChecklistItem.fase == s.status,
                SafraChecklistItem.obrigatorio == True,
                SafraChecklistItem.concluido == False,
            )
            pendentes = (await self.session.execute(stmt_pend)).scalar() or 0
            if pendentes > 0:
                alertas_checklist.append({
                    "safra_id": str(s.id),
                    "safra": f"{s.cultura} {s.ano_safra}",
                    "fase": s.status,
                    "pendentes": pendentes,
                    "severidade": "CRITICO" if pendentes >= 3 else "AVISO",
                })

        # ── Alertas NDE de monitoramento ──────────────────────────────────────
        alertas_nde: list[dict] = []
        if safra_ids_ativas:
            stmt_nde = select(
                MonitoramentoPragas.safra_id,
                MonitoramentoPragas.talhao_id,
                MonitoramentoPragas.nome_popular,
                MonitoramentoPragas.nivel_infestacao,
                MonitoramentoPragas.nde_cultura,
                MonitoramentoPragas.data_avaliacao,
            ).where(
                MonitoramentoPragas.tenant_id == self.tenant_id,
                MonitoramentoPragas.safra_id.in_(safra_ids_ativas),
                MonitoramentoPragas.atingiu_nde == True,
            ).order_by(MonitoramentoPragas.data_avaliacao.desc()).limit(10)
            nde_rows = (await self.session.execute(stmt_nde)).all()
            for row in nde_rows:
                safra_obj = next((s for s in safras_ativas if s.id == row.safra_id), None)
                alertas_nde.append({
                    "safra_id": str(row.safra_id),
                    "safra": f"{safra_obj.cultura} {safra_obj.ano_safra}" if safra_obj else "—",
                    "agente": row.nome_popular or "—",
                    "nivel": float(row.nivel_infestacao or 0),
                    "nde": float(row.nde_cultura or 0),
                    "data": str(row.data_avaliacao),
                    "severidade": "CRITICO",
                })

        # ── Fenologia atual por safra ─────────────────────────────────────────
        fenologia_atual: list[dict] = []
        safras_campo = [x for x in safras_ativas if x.status in ("PLANTIO", "DESENVOLVIMENTO", "COLHEITA")]
        for s in safras_campo:
            stmt_fen = (
                select(SafraFenologiaRegistro)
                .options(joinedload(SafraFenologiaRegistro.escala))
                .where(
                    SafraFenologiaRegistro.safra_id == s.id,
                    SafraFenologiaRegistro.tenant_id == self.tenant_id,
                )
                .order_by(SafraFenologiaRegistro.data_observacao.desc())
                .limit(1)
            )
            reg = (await self.session.execute(stmt_fen)).scalars().first()
            fenologia_atual.append({
                "safra_id": str(s.id),
                "safra": f"{s.cultura} {s.ano_safra}",
                "estagio_codigo": reg.escala.codigo if reg and reg.escala else None,
                "estagio_nome": reg.escala.nome if reg and reg.escala else None,
                "data_observacao": str(reg.data_observacao) if reg else None,
            })

        total_alertas = len(alertas_checklist) + len(alertas_nde)

        return {
            "kpis": {
                "total_safras_ativas": len(safras_ativas),
                "total_safras_encerradas": len(safras_encerradas),
                "area_total_ha": round(area_total, 2),
                "custo_acumulado": round(custo_acumulado, 2),
                "meta_producao_sc": round(meta_total_sc, 2),
                "sacas_colhidas": round(sacas_total, 2),
                "receita_colheita": round(receita_romaneios, 2),
                "total_alertas": total_alertas,
            },
            "safras_por_fase": {
                fase: itens for fase, itens in por_fase.items() if itens
            },
            "alertas_checklist": alertas_checklist,
            "alertas_nde": alertas_nde,
            "fenologia_atual": fenologia_atual,
        }

    async def resumo_financeiro_safra(self, safra_id: UUID) -> SafraResumoFinanceiro:
        """
        Resumo financeiro completo de uma safra:
        - Operações e custos
        - Despesas associadas (via origem_id)
        - Romaneios e receita
        - Comercializações (vendas reais)
        - Receitas associadas (via origem_id)
        - Cálculo de ROI, margem e produtividade

        Agrupa dados de múltiplas tabelas para visão financeira integrada.
        """
        from financeiro.comercializacao.models import ComercializacaoCommodity
        from agricola.colheita.models import ProdutoColhido

        # 1. Buscar safra
        safra = await self.session.get(Safra, safra_id)
        if not safra or safra.tenant_id != self.tenant_id:
            raise EntityNotFoundError("Safra", safra_id)

        area_ha = float(safra.area_plantada_ha or 0) if safra.area_plantada_ha else 0

        # 2. Operações
        stmt_ops = select(OperacaoAgricola).where(
            OperacaoAgricola.safra_id == safra_id,
            OperacaoAgricola.tenant_id == self.tenant_id
        )
        operacoes = list((await self.session.execute(stmt_ops)).scalars().all())
        total_operacoes = len(operacoes)
        custo_operacoes = sum(float(op.custo_total or 0) for op in operacoes)
        custo_por_ha = custo_operacoes / area_ha if area_ha > 0 else 0

        # 3. Despesas (vinculadas via origem_id)
        operacao_ids = [op.id for op in operacoes]
        stmt_despesas = select(Despesa).where(
            Despesa.tenant_id == self.tenant_id,
            Despesa.origem_tipo == "OPERACAO_AGRICOLA",
            Despesa.origem_id.in_(operacao_ids) if operacao_ids else False
        )
        despesas = list((await self.session.execute(stmt_despesas)).scalars().all())
        despesa_total = sum(float(d.valor_total or 0) for d in despesas)

        # 4. Romaneios
        stmt_romaneios = select(RomaneioColheita).where(
            RomaneioColheita.safra_id == safra_id,
            RomaneioColheita.tenant_id == self.tenant_id
        )
        romaneios = list((await self.session.execute(stmt_romaneios)).scalars().all())
        total_romaneios = len(romaneios)
        total_sacas = sum(float(r.sacas_60kg or 0) for r in romaneios)

        produtividade = total_sacas / area_ha if area_ha > 0 else None

        # 5. Receitas financeiras (romaneios)
        romaneio_ids = [r.id for r in romaneios]
        stmt_receitas = select(Receita).where(
            Receita.tenant_id == self.tenant_id,
            Receita.origem_tipo == "ROMANEIO_COLHEITA",
            Receita.origem_id.in_(romaneio_ids) if romaneio_ids else False
        )
        receitas = list((await self.session.execute(stmt_receitas)).scalars().all())
        receita_romaneios = sum(float(r.valor_total or 0) for r in receitas)

        # 6. Comercializações vinculadas a esta safra
        stmt_comm = select(ComercializacaoCommodity).where(
            ComercializacaoCommodity.tenant_id == self.tenant_id,
        )
        # Filtrar por produto_colhido desta safra
        stmt_pc = select(ProdutoColhido.id).where(
            ProdutoColhido.safra_id == safra_id,
            ProdutoColhido.tenant_id == self.tenant_id,
        )
        pc_ids_result = (await self.session.execute(stmt_pc)).scalars().all()
        if pc_ids_result:
            stmt_comm = stmt_comm.where(
                ComercializacaoCommodity.produto_colhido_id.in_(list(pc_ids_result))
            )
        comercializacoes = list((await self.session.execute(stmt_comm)).scalars().all())

        total_comercializacoes = len(comercializacoes)
        receita_comercializacoes = sum(float(c.valor_total or 0) for c in comercializacoes)
        valor_vendido = sum(
            float(c.valor_total or 0) for c in comercializacoes if c.status == "FINALIZADO"
        )

        # 7. Receita total = receitas financeiras + comercializações
        receita_total = receita_romaneios + receita_comercializacoes

        # 8. Cálculos financeiros
        # Custo: usar o menor entre custo_operacoes e despesa_total (evitar dupla contagem)
        custo_base = min(custo_operacoes, despesa_total) if despesa_total > 0 else custo_operacoes
        lucro_bruto = receita_total - custo_base
        roi_pct = (lucro_bruto / custo_base * 100) if custo_base > 0 else None

        # Margens
        margem_bruta = lucro_bruto
        margem_por_ha = margem_bruta / area_ha if area_ha > 0 else 0
        margem_pct = (margem_bruta / receita_total * 100) if receita_total > 0 else None

        # 9. Montar resposta
        financeiro = FinanceiroResumo(
            total_operacoes=total_operacoes,
            custo_operacoes_total=round(custo_operacoes, 2),
            custo_por_ha=round(custo_por_ha, 2),
            total_romaneios=total_romaneios,
            total_sacas=round(total_sacas, 3),
            produtividade_sc_ha=round(produtividade, 3) if produtividade else None,
            total_comercializacoes=total_comercializacoes,
            receita_comercializacoes=round(receita_comercializacoes, 2),
            valor_total_vendido=round(valor_vendido, 2),
            despesa_total=round(despesa_total, 2),
            receita_total=round(receita_total, 2),
            lucro_bruto=round(lucro_bruto, 2),
            roi_pct=round(roi_pct, 2) if roi_pct is not None else None,
            margem_bruta=round(margem_bruta, 2),
            margem_por_ha=round(margem_por_ha, 2),
            margem_pct=round(margem_pct, 2) if margem_pct is not None else None,
        )

        return SafraResumoFinanceiro(
            id=safra.id,
            cultura=safra.cultura,
            ano_safra=safra.ano_safra,
            status=safra.status,
            area_plantada_ha=float(safra.area_plantada_ha or 0),
            financeiro=financeiro
        )

    async def margem_safra_completa(self, safra_id: UUID) -> "SafraMargemCompleta":
        """
        Dashboard de margem por safra com breakdown por talhão e tipo de operação.

        Inclui:
        - Receita de romaneios + comercializações
        - Custos de operações agrícolas
        - Margem bruta, margem por ha, ROI
        - Breakdown por talhão
        - Breakdown por tipo de operação
        """
        from financeiro.comercializacao.models import ComercializacaoCommodity
        from agricola.colheita.models import ProdutoColhido
        from core.cadastros.propriedades.models import AreaRural
        from agricola.dashboard.schemas import SafraMargemCompleta, TalhaoMargemItem

        safra = await self.session.get(Safra, safra_id)
        if not safra or safra.tenant_id != self.tenant_id:
            raise EntityNotFoundError("Safra", safra_id)

        area_total = float(safra.area_plantada_ha or 0)

        # ── Operações e custos ──
        stmt_ops = select(OperacaoAgricola).where(
            OperacaoAgricola.safra_id == safra_id,
            OperacaoAgricola.tenant_id == self.tenant_id,
        ).order_by(OperacaoAgricola.tipo)
        operacoes = list((await self.session.execute(stmt_ops)).scalars().all())
        custo_total = sum(float(op.custo_total or 0) for op in operacoes)
        custo_por_ha = custo_total / area_total if area_total > 0 else 0

        # Breakdown por tipo de operação
        por_tipo: dict[str, float] = {}
        for op in operacoes:
            tipo = op.tipo or "OUTRO"
            por_tipo[tipo] = por_tipo.get(tipo, 0) + float(op.custo_total or 0)

        breakdown_operacoes = [
            {
                "tipo": tipo,
                "valor": round(valor, 2),
                "percentual": round(valor / custo_total * 100, 1) if custo_total > 0 else 0,
                "valor_por_ha": round(valor / area_total, 2) if area_total > 0 else 0,
            }
            for tipo, valor in sorted(por_tipo.items(), key=lambda x: -x[1])
        ]

        # ── Romaneios por talhão ──
        stmt_rom = select(RomaneioColheita).where(
            RomaneioColheita.safra_id == safra_id,
            RomaneioColheita.tenant_id == self.tenant_id,
        )
        romaneios = list((await self.session.execute(stmt_rom)).scalars().all())
        receita_rom_por_talhao: dict[UUID, float] = {}
        sacas_por_talhao: dict[UUID, float] = {}
        for r in romaneios:
            tid = r.talhao_id
            receita_rom_por_talhao[tid] = receita_rom_por_talhao.get(tid, 0) + float(r.receita_total or 0)
            sacas_por_talhao[tid] = sacas_por_talhao.get(tid, 0) + float(r.sacas_60kg or 0)

        # ── Comercializações por talhão (via ProdutoColhido) ──
        stmt_pc = select(ProdutoColhido).where(
            ProdutoColhido.safra_id == safra_id,
            ProdutoColhido.tenant_id == self.tenant_id,
        )
        produtos_colhidos = list((await self.session.execute(stmt_pc)).scalars().all())

        pc_ids = [pc.id for pc in produtos_colhidos]
        receita_comm_por_talhao: dict[UUID, float] = {}
        if pc_ids:
            stmt_comm = select(ComercializacaoCommodity).where(
                ComercializacaoCommodity.produto_colhido_id.in_(pc_ids)
            )
            comercializacoes = list((await self.session.execute(stmt_comm)).scalars().all())
            # Mapear produto_colhido → talhão
            pc_map = {pc.id: pc.talhao_id for pc in produtos_colhidos}
            for c in comercializacoes:
                tid = pc_map.get(c.produto_colhido_id)
                if tid:
                    receita_comm_por_talhao[tid] = receita_comm_por_talhao.get(tid, 0) + float(c.valor_total or 0)

        # ── Custos por talhão (operações por talhão) ──
        custo_por_talhao: dict[UUID, float] = {}
        area_por_talhao: dict[UUID, float] = {}
        for op in operacoes:
            tid = op.talhao_id
            custo_por_talhao[tid] = custo_por_talhao.get(tid, 0) + float(op.custo_total or 0)
            area_por_talhao[tid] = area_por_talhao.get(tid, 0) + float(op.area_aplicada_ha or 0)

        # ── Montar por talhão ──
        talhao_ids = set(
            list(receita_rom_por_talhao.keys())
            + list(receita_comm_por_talhao.keys())
            + list(custo_por_talhao.keys())
        )

        por_talhao = []
        for tid in talhao_ids:
            talhao = await self.session.get(AreaRural, tid)
            talhao_nome = talhao.nome if talhao else str(tid)[:8]
            talhao_area = area_por_talhao.get(tid, 0) or float(talhao.area_hectares or 0) if talhao else 0

            custo_op = custo_por_talhao.get(tid, 0)
            rec_rom = receita_rom_por_talhao.get(tid, 0)
            rec_comm = receita_comm_por_talhao.get(tid, 0)
            rec_total = rec_rom + rec_comm
            margem = rec_total - custo_op
            margem_pct_val = (margem / rec_total * 100) if rec_total > 0 else None
            prod_sc_ha = (sacas_por_talhao.get(tid, 0) / talhao_area) if talhao_area > 0 else None

            por_talhao.append(TalhaoMargemItem(
                talhao_id=tid,
                talhao_nome=talhao_nome,
                area_ha=round(talhao_area, 2),
                custo_operacoes=round(custo_op, 2),
                custo_por_ha=round(custo_op / talhao_area, 2) if talhao_area > 0 else 0,
                receita_romaneios=round(rec_rom, 2),
                receita_comercializacoes=round(rec_comm, 2),
                receita_total=round(rec_total, 2),
                margem_bruta=round(margem, 2),
                margem_pct=round(margem_pct_val, 2) if margem_pct_val is not None else None,
                produtividade_sc_ha=round(prod_sc_ha, 2) if prod_sc_ha else None,
                sacas_colhidas=round(sacas_por_talhao.get(tid, 0), 2),
            ))

        por_talhao.sort(key=lambda x: -x.margem_bruta)

        # ── Totais ──
        receita_total = sum(r.receita_total for r in por_talhao)
        margem_bruta = receita_total - custo_total
        margem_por_ha = margem_bruta / area_total if area_total > 0 else 0
        margem_pct = (margem_bruta / receita_total * 100) if receita_total > 0 else None
        roi_pct = (margem_bruta / custo_total * 100) if custo_total > 0 else None

        return SafraMargemCompleta(
            safra_id=safra.id,
            cultura=safra.cultura,
            ano_safra=safra.ano_safra,
            status=safra.status,
            area_total_ha=round(area_total, 2),
            custo_total=round(custo_total, 2),
            custo_por_ha=round(custo_por_ha, 2),
            receita_total=round(receita_total, 2),
            receita_por_ha=round(receita_total / area_total, 2) if area_total > 0 else 0,
            margem_bruta=round(margem_bruta, 2),
            margem_por_ha=round(margem_por_ha, 2),
            margem_pct=round(margem_pct, 2) if margem_pct is not None else None,
            roi_pct=round(roi_pct, 2) if roi_pct is not None else None,
            por_talhao=por_talhao,
            breakdown_operacoes=breakdown_operacoes,
        )

