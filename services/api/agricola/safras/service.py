from uuid import UUID
from datetime import date
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, func
from core.exceptions import BusinessRuleError
from core.base_service import BaseService

from agricola.safras.models import Safra, SafraFaseHistorico, SafraTalhao, SAFRA_TRANSICOES
from agricola.safras.schemas import SafraCreate, SafraUpdate

class SafraService(BaseService[Safra]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(Safra, session, tenant_id)

    async def criar(self, dados: SafraCreate) -> Safra:
        # 1. Verifica se já existe safra ativa para talhao+ano+cultura
        stmt = select(Safra).filter_by(
            tenant_id=self.tenant_id,
            talhao_id=dados.talhao_id,
            ano_safra=dados.ano_safra,
            cultura=dados.cultura
        ).where(Safra.status != 'CANCELADA')
        result = await self.session.execute(stmt)
        if result.scalars().first():
            raise BusinessRuleError("Já existe uma safra ativa para este talhão, ano e cultura.")

        # O cálculo da colheita_prevista baseado na cultivar.ciclo_dias_media
        # (Isso assumiria uma consulta ao CULTIVAR, simplificando aqui para não sobrecarregar)

        # 3. Cria a Safra
        dados_dict = dados.model_dump()
        return await super().create(dados_dict)

    async def avancar_fase(
        self,
        safra_id: UUID,
        novo_status: str,
        usuario_id: UUID | None = None,
        observacao: str | None = None,
        dados_fase: dict | None = None,
    ) -> Safra:
        safra = await self.get_or_fail(safra_id)
        permitidas = SAFRA_TRANSICOES.get(safra.status, [])
        if novo_status not in permitidas:
            raise BusinessRuleError(
                f"Transição inválida: {safra.status} → {novo_status}. "
                f"Permitidas: {permitidas or 'nenhuma'}"
            )

        fase_anterior = safra.status
        upd: dict = {"status": novo_status}

        # Preenche datas automáticas na transição
        if novo_status == "PLANTIO" and not safra.data_plantio_real:
            upd["data_plantio_real"] = date.today()
        elif novo_status == "ENCERRADA" and not safra.data_colheita_real:
            upd["data_colheita_real"] = date.today()

        safra = await self.atualizar(safra_id, SafraUpdate(**upd))

        # Registra no histórico
        historico = SafraFaseHistorico(
            safra_id=safra_id,
            tenant_id=self.tenant_id,
            fase_anterior=fase_anterior,
            fase_nova=novo_status,
            usuario_id=usuario_id,
            observacao=observacao,
            dados_fase=dados_fase,
        )
        self.session.add(historico)
        await self.session.flush()

        return safra

    async def listar_historico(self, safra_id: UUID) -> list[SafraFaseHistorico]:
        await self.get_or_fail(safra_id)  # garante tenant isolation
        stmt = (
            select(SafraFaseHistorico)
            .where(
                SafraFaseHistorico.safra_id == safra_id,
                SafraFaseHistorico.tenant_id == self.tenant_id,
            )
            .order_by(SafraFaseHistorico.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def atualizar(self, obj_id: UUID, dados: SafraUpdate) -> Safra:
        dados_dict = dados.model_dump(exclude_unset=True)
        return await super().update(obj_id, dados_dict)

    async def fechar_safra(self, safra_id: UUID) -> Safra:
        # Agrega todos os romaneios / calcula área plantada x sacas
        # Agrega custos
        # Integrar httpx api-financeiro para receita
        return await self.get_or_fail(safra_id)

    async def calcular_gdu_acumulado(self, safra_id: UUID) -> float:
        return 0.0

    async def estimar_estagio_fenologico(self, safra_id: UUID) -> str:
        return "V1"

    async def resumo_planejado_realizado(self, safra_id: UUID) -> dict[str, Any]:
        """Retorna comparativo planejado vs realizado para uma safra."""
        from agricola.operacoes.models import OperacaoAgricola
        from agricola.romaneios.models import RomaneioColheita

        safra = await self.get_or_fail(safra_id)

        # Custo realizado = soma das operações
        stmt_custo = select(func.sum(OperacaoAgricola.custo_total)).where(
            OperacaoAgricola.safra_id == safra_id,
            OperacaoAgricola.tenant_id == self.tenant_id,
        )
        custo_realizado_total = (await self.session.execute(stmt_custo)).scalar() or 0.0

        area = float(safra.area_plantada_ha or 0)
        custo_realizado_ha = (custo_realizado_total / area) if area > 0 else 0.0

        # Produtividade e receita realizadas via romaneios
        stmt_rom = select(
            func.sum(RomaneioColheita.sacas_60kg),
            func.sum(RomaneioColheita.receita_total),
        ).where(
            RomaneioColheita.safra_id == safra_id,
            RomaneioColheita.tenant_id == self.tenant_id,
        )
        row = (await self.session.execute(stmt_rom)).first()
        sacas_totais = float(row[0] or 0)
        receita_realizada = float(row[1] or 0)
        produtividade_real_sc_ha = (sacas_totais / area) if area > 0 else 0.0

        # Receita prevista
        receita_prevista = 0.0
        if safra.produtividade_meta_sc_ha and safra.preco_venda_previsto and area > 0:
            receita_prevista = float(safra.produtividade_meta_sc_ha) * float(safra.preco_venda_previsto) * area

        custo_previsto_total = float(safra.custo_previsto_ha or 0) * area

        return {
            "safra_id": safra_id,
            "cultura": safra.cultura,
            "ano_safra": safra.ano_safra,
            "status": safra.status,
            "area_plantada_ha": area,
            # Custo
            "custo_previsto_ha": float(safra.custo_previsto_ha or 0),
            "custo_realizado_ha": round(custo_realizado_ha, 2),
            "custo_previsto_total": round(custo_previsto_total, 2),
            "custo_realizado_total": round(custo_realizado_total, 2),
            "desvio_custo_pct": round(
                ((custo_realizado_total - custo_previsto_total) / custo_previsto_total * 100)
                if custo_previsto_total > 0 else 0.0,
                1,
            ),
            # Produtividade
            "produtividade_meta_sc_ha": float(safra.produtividade_meta_sc_ha or 0),
            "produtividade_real_sc_ha": round(produtividade_real_sc_ha, 2),
            "sacas_totais": round(sacas_totais, 2),
            # Receita
            "preco_venda_previsto": float(safra.preco_venda_previsto or 0),
            "receita_prevista": round(receita_prevista, 2),
            "receita_realizada": round(receita_realizada, 2),
            "resultado_liquido": round(receita_realizada - custo_realizado_total, 2),
        }

    # ─── Talhões ──────────────────────────────────────────────────────────────

    async def listar_talhoes(self, safra_id: UUID) -> list[SafraTalhao]:
        """Retorna todos os talhões associados à safra."""
        stmt = (
            select(SafraTalhao)
            .where(
                SafraTalhao.safra_id == safra_id,
                SafraTalhao.tenant_id == self.tenant_id,
            )
            .order_by(SafraTalhao.principal.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def sincronizar_talhoes(
        self,
        safra_id: UUID,
        talhao_ids: list[UUID],
        areas_ha: dict[str, float] | None = None,
    ) -> list[SafraTalhao]:
        """Substitui a lista de talhões da safra (upsert idempotente).
        O primeiro ID da lista é marcado como principal.
        """
        # Remove existentes
        from sqlalchemy import delete
        await self.session.execute(
            delete(SafraTalhao).where(
                SafraTalhao.safra_id == safra_id,
                SafraTalhao.tenant_id == self.tenant_id,
            )
        )
        await self.session.flush()

        novos = []
        for i, tid in enumerate(talhao_ids):
            st = SafraTalhao(
                tenant_id=self.tenant_id,
                safra_id=safra_id,
                area_id=tid,
                principal=(i == 0),
                area_ha=(areas_ha or {}).get(str(tid)),
            )
            self.session.add(st)
            novos.append(st)

        await self.session.flush()

        # Atualiza talhao_id principal na safra para manter compat. legado
        if talhao_ids:
            safra = await self.get_or_fail(safra_id)
            safra.talhao_id = talhao_ids[0]

        return novos
