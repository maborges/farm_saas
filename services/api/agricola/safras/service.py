from uuid import UUID
from datetime import date, datetime
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

    # ─── Estoque (Inventory) ───────────────────────────────────────────────────

    async def get_saldo_safra(self, safra_id: UUID) -> dict:
        """
        Retorna saldo atual de estoque para uma safra.
        Agrupa por depósito e produto.
        """
        from operacional.models.estoque import LoteEstoque, Deposito
        from core.cadastros.produtos.models import Produto

        # Validar tenant isolation
        safra = await self.get_or_fail(safra_id)

        # Query: Lotes ativos → agrupa por deposito + produto
        stmt = (
            select(
                LoteEstoque.deposito_id,
                LoteEstoque.produto_id,
                Deposito.nome.label("deposito_nome"),
                Produto.nome.label("produto_nome"),
                Produto.unidade_estoque,
                func.sum(LoteEstoque.quantidade_atual).label("quantidade_atual"),
                func.count(LoteEstoque.id).label("num_lotes"),
            )
            .join(Deposito, LoteEstoque.deposito_id == Deposito.id)
            .join(Produto, LoteEstoque.produto_id == Produto.id)
            .where(
                LoteEstoque.status == "ATIVO",
                LoteEstoque.quantidade_atual > 0,
                Deposito.tenant_id == self.tenant_id,
            )
            .group_by(
                LoteEstoque.deposito_id,
                LoteEstoque.produto_id,
                Deposito.nome,
                Produto.nome,
                Produto.unidade_estoque,
            )
            .order_by(Deposito.nome, Produto.nome)
        )

        rows = await self.session.execute(stmt)
        results = rows.all()

        # Formata resposta
        saldos_dict = {}
        for row in results:
            deposito_id = row.deposito_id
            if deposito_id not in saldos_dict:
                saldos_dict[deposito_id] = {
                    "deposito_id": deposito_id,
                    "deposito_nome": row.deposito_nome,
                    "produtos": [],
                }

            saldos_dict[deposito_id]["produtos"].append({
                "produto_id": row.produto_id,
                "produto_nome": row.produto_nome,
                "quantidade_atual": float(row.quantidade_atual or 0),
                "unidade": row.unidade_estoque,
                "num_lotes": row.num_lotes,
            })

        return {
            "safra_id": safra_id,
            "depositos": list(saldos_dict.values()),
            "total_depositos": len(saldos_dict),
            "total_produtos_ativos": sum(len(d["produtos"]) for d in saldos_dict.values()),
        }

    async def get_movimentacoes_safra(
        self,
        safra_id: UUID,
        tipo: str | None = None,
        deposito_id: UUID | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        numero_lote: str | None = None,
        origem_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """
        Retorna histórico de movimentações de estoque para uma safra.
        Filtra por tipo, depósito, período, lote, operação associada.
        """
        from operacional.models.estoque import MovimentacaoEstoque, LoteEstoque, Deposito
        from core.cadastros.produtos.models import Produto
        from agricola.operacoes.models import OperacaoAgricola

        # Validar tenant isolation
        safra = await self.get_or_fail(safra_id)

        # Query base: MovimentacaoEstoque linked to safra via operacao
        stmt = (
            select(
                MovimentacaoEstoque.id,
                MovimentacaoEstoque.produto_id,
                MovimentacaoEstoque.lote_id,
                MovimentacaoEstoque.deposito_id,
                MovimentacaoEstoque.tipo,
                MovimentacaoEstoque.quantidade,
                MovimentacaoEstoque.custo_unitario,
                MovimentacaoEstoque.custo_total,
                MovimentacaoEstoque.motivo,
                MovimentacaoEstoque.origem_id,
                MovimentacaoEstoque.origem_tipo,
                MovimentacaoEstoque.data_movimentacao,
                Produto.nome.label("produto_nome"),
                Produto.unidade_estoque,
                LoteEstoque.numero_lote,
                Deposito.nome.label("deposito_nome"),
                OperacaoAgricola.tipo.label("operacao_tipo"),
            )
            .join(Produto, MovimentacaoEstoque.produto_id == Produto.id, isouter=True)
            .join(LoteEstoque, MovimentacaoEstoque.lote_id == LoteEstoque.id, isouter=True)
            .join(Deposito, MovimentacaoEstoque.deposito_id == Deposito.id, isouter=True)
            .join(
                OperacaoAgricola,
                (MovimentacaoEstoque.origem_id == OperacaoAgricola.id)
                & (MovimentacaoEstoque.origem_tipo == "OPERACAO_AGRICOLA"),
                isouter=True,
            )
            .where(
                OperacaoAgricola.safra_id == safra_id,
                OperacaoAgricola.tenant_id == self.tenant_id,
            )
        )

        # Aplica filtros
        if tipo:
            stmt = stmt.where(MovimentacaoEstoque.tipo == tipo)
        if deposito_id:
            stmt = stmt.where(MovimentacaoEstoque.deposito_id == deposito_id)
        if data_inicio:
            stmt = stmt.where(MovimentacaoEstoque.data_movimentacao >= data_inicio)
        if data_fim:
            stmt = stmt.where(MovimentacaoEstoque.data_movimentacao <= data_fim)
        if numero_lote:
            stmt = stmt.where(LoteEstoque.numero_lote.ilike(f"%{numero_lote}%"))

        # Ordem e paginação
        stmt = stmt.order_by(MovimentacaoEstoque.data_movimentacao.desc()).limit(limit).offset(offset)

        rows = await self.session.execute(stmt)
        movimentacoes = rows.all()

        # Conta total (sem limit/offset para saber se tem mais)
        count_stmt = (
            select(func.count(MovimentacaoEstoque.id))
            .join(OperacaoAgricola,
                  (MovimentacaoEstoque.origem_id == OperacaoAgricola.id)
                  & (MovimentacaoEstoque.origem_tipo == "OPERACAO_AGRICOLA"),
                  isouter=True)
            .where(
                OperacaoAgricola.safra_id == safra_id,
                OperacaoAgricola.tenant_id == self.tenant_id,
            )
        )
        if tipo:
            count_stmt = count_stmt.where(MovimentacaoEstoque.tipo == tipo)
        if deposito_id:
            count_stmt = count_stmt.where(MovimentacaoEstoque.deposito_id == deposito_id)
        if data_inicio:
            count_stmt = count_stmt.where(MovimentacaoEstoque.data_movimentacao >= data_inicio)
        if data_fim:
            count_stmt = count_stmt.where(MovimentacaoEstoque.data_movimentacao <= data_fim)
        if numero_lote:
            count_stmt = count_stmt.where(LoteEstoque.numero_lote.ilike(f"%{numero_lote}%"))

        total = (await self.session.execute(count_stmt)).scalar() or 0

        return {
            "safra_id": safra_id,
            "movimentacoes": [
                {
                    "id": mov.id,
                    "produto_id": mov.produto_id,
                    "produto_nome": mov.produto_nome,
                    "lote_id": mov.lote_id,
                    "numero_lote": mov.numero_lote,
                    "deposito_id": mov.deposito_id,
                    "deposito_nome": mov.deposito_nome,
                    "tipo": mov.tipo,
                    "quantidade": float(mov.quantidade),
                    "unidade": mov.unidade_estoque,
                    "custo_unitario": float(mov.custo_unitario) if mov.custo_unitario else None,
                    "custo_total": float(mov.custo_total) if mov.custo_total else None,
                    "motivo": mov.motivo,
                    "origem_id": mov.origem_id,
                    "origem_tipo": mov.origem_tipo,
                    "operacao_tipo": mov.operacao_tipo,
                    "data_movimentacao": mov.data_movimentacao,
                }
                for mov in movimentacoes
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
