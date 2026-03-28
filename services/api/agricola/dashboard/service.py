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
                MonitoramentoPragas.agente_nome,
                MonitoramentoPragas.nivel_infestacao,
                MonitoramentoPragas.nde_cultura,
                MonitoramentoPragas.data_registro,
            ).where(
                MonitoramentoPragas.tenant_id == self.tenant_id,
                MonitoramentoPragas.safra_id.in_(safra_ids_ativas),
                MonitoramentoPragas.atingiu_nde == True,
            ).order_by(MonitoramentoPragas.data_registro.desc()).limit(10)
            nde_rows = (await self.session.execute(stmt_nde)).all()
            for row in nde_rows:
                safra_obj = next((s for s in safras_ativas if s.id == row.safra_id), None)
                alertas_nde.append({
                    "safra_id": str(row.safra_id),
                    "safra": f"{safra_obj.cultura} {safra_obj.ano_safra}" if safra_obj else "—",
                    "agente": row.agente_nome,
                    "nivel": float(row.nivel_infestacao or 0),
                    "nde": float(row.nde_cultura or 0),
                    "data": str(row.data_registro),
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
