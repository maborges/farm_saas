from uuid import UUID
from datetime import date, datetime
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, func, and_
from sqlalchemy.orm import selectinload
from core.exceptions import BusinessRuleError
from core.base_service import BaseService

from agricola.safras.models import Safra, SafraFaseHistorico, SafraTalhao, SAFRA_TRANSICOES
from agricola.safras.schemas import SafraCreate, SafraUpdate
from agricola.cultivos.models import Cultivo, CultivoArea

class SafraService(BaseService[Safra]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(Safra, session, tenant_id)

    async def criar(self, dados: SafraCreate) -> Safra:
        """Cria uma safra com cultivos de forma atômica.

        Suporta dois fluxos:
        1. Novo: cultivos + areas aninhados em SafraCreate.cultivos
        2. Legado: talhao_ids para compatibilidade
        """
        talhao_principal_id: UUID | None = None

        # Determina talhão principal
        if dados.cultivos:
            # Novo fluxo: extrai talhão principal do primeiro cultivo
            primeiro_cultivo = dados.cultivos[0]
            if primeiro_cultivo.areas:
                talhao_principal_id = primeiro_cultivo.areas[0].area_id
        elif dados.talhao_ids:
            # Fluxo legado: usa primeiro talhao_ids
            talhao_principal_id = dados.talhao_ids[0]

        if not talhao_principal_id:
            raise BusinessRuleError("Informe pelo menos um talhão (via cultivos ou talhao_ids)")

        # Valida duplicatas via CultivoArea (fonte de verdade)
        dup_stmt = (
            select(func.count(Safra.id))
            .join(Cultivo, Cultivo.safra_id == Safra.id)
            .join(CultivoArea, CultivoArea.cultivo_id == Cultivo.id)
            .where(
                Safra.tenant_id == self.tenant_id,
                Safra.ano_safra == dados.ano_safra,
                Safra.status != 'CANCELADA',
                CultivoArea.area_id == talhao_principal_id,
            )
        )
        if (await self.session.execute(dup_stmt)).scalar() or 0 > 0:
            raise BusinessRuleError(f"Já existe safra ativa para {dados.ano_safra} neste talhão.")

        # Cultura principal (legado): pega do primeiro cultivo ou do campo raiz
        cultura_principal: str | None = None
        if dados.cultivos:
            cultura_principal = dados.cultivos[0].cultura
        elif dados.cultura:
            cultura_principal = dados.cultura

        # Cria a Safra
        safra = Safra(
            tenant_id=self.tenant_id,
            ano_safra=dados.ano_safra,
            cultura=cultura_principal,
            status='PLANEJADA',
            observacoes=dados.observacoes,
        )
        self.session.add(safra)
        await self.session.flush()

        # Fluxo novo: cria Cultivos com CultivoAreas
        if dados.cultivos:
            for cult_data in dados.cultivos:
                cultivo = Cultivo(
                    tenant_id=self.tenant_id,
                    safra_id=safra.id,
                    cultura=cult_data.cultura,
                    cultivar_id=cult_data.cultivar_id,
                    cultivar_nome=cult_data.cultivar_nome,
                    commodity_id=cult_data.commodity_id,
                    sistema_plantio=cult_data.sistema_plantio,
                    populacao_prevista=cult_data.populacao_prevista,
                    espacamento_cm=cult_data.espacamento_cm,
                    data_plantio_prevista=cult_data.data_plantio_prevista,
                    data_inicio=cult_data.data_inicio,
                    data_fim=cult_data.data_fim,
                    produtividade_meta_sc_ha=cult_data.produtividade_meta_sc_ha,
                    preco_venda_previsto=cult_data.preco_venda_previsto,
                    consorciado=cult_data.consorciado,
                    observacoes=cult_data.observacoes,
                )
                self.session.add(cultivo)
                await self.session.flush()

                # Adiciona CultivoAreas
                for area_data in cult_data.areas:
                    area = CultivoArea(
                        tenant_id=self.tenant_id,
                        cultivo_id=cultivo.id,
                        area_id=area_data.area_id,
                        area_ha=area_data.area_ha,
                    )
                    self.session.add(area)

        # Fluxo legado: cria SafraTalhoes + Cultivo para compatibilidade
        elif dados.talhao_ids:
            for talhao_id in dados.talhao_ids:
                st = SafraTalhao(
                    safra_id=safra.id,
                    tenant_id=self.tenant_id,
                    area_id=talhao_id,
                    principal=False
                )
                self.session.add(st)

            # Cria cultivo legado se cultura foi informada
            if dados.cultura:
                cultivo = Cultivo(
                    tenant_id=self.tenant_id,
                    safra_id=safra.id,
                    cultura=dados.cultura,
                    cultivar_id=dados.cultivar_id,
                    cultivar_nome=dados.cultivar_nome,
                    commodity_id=dados.commodity_id,
                    sistema_plantio=dados.sistema_plantio,
                    populacao_prevista=dados.populacao_prevista,
                    espacamento_cm=dados.espacamento_cm,
                    data_plantio_prevista=dados.data_plantio_prevista,
                    data_inicio=getattr(dados, "data_inicio", None),
                    data_fim=getattr(dados, "data_fim", None),
                    produtividade_meta_sc_ha=dados.produtividade_meta_sc_ha,
                    preco_venda_previsto=dados.preco_venda_previsto,
                )
                self.session.add(cultivo)
                await self.session.flush()
                # Cria CultivoAreas para cada talhão (fluxo legado)
                if dados.talhao_ids:
                    for talhao_id in dados.talhao_ids:
                        area = CultivoArea(
                            tenant_id=self.tenant_id,
                            cultivo_id=cultivo.id,
                            area_id=talhao_id,
                            area_ha=0.0,  # Área é definida no fluxo novo via cultivos
                        )
                        self.session.add(area)

        await self.session.commit()
        await self.session.refresh(safra, ["cultivos"])
        return safra

    async def list_with_cultivos(self, **filters) -> list[Safra]:
        """Lista safras com cultivos eager-loaded."""
        stmt = select(Safra).options(
            selectinload(Safra.cultivos)
        ).where(Safra.tenant_id == self.tenant_id)

        # Aplicar filtros
        if "talhao_id" in filters:
            stmt = stmt.join(SafraTalhao, SafraTalhao.safra_id == Safra.id).where(
                SafraTalhao.area_id == filters["talhao_id"],
                SafraTalhao.tenant_id == self.tenant_id,
            )
        if "ano_safra" in filters:
            stmt = stmt.where(Safra.ano_safra == filters["ano_safra"])
        if "cultura" in filters:
            stmt = stmt.where(Safra.cultura == filters["cultura"])
        if "status" in filters:
            stmt = stmt.where(Safra.status == filters["status"])

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def avancar_fase(
        self,
        safra_id: UUID,
        novo_status: str,
        usuario_id: UUID | None = None,
        observacao: str | None = None,
        dados_fase: dict | None = None,
        forcar_avanco: bool = False,
        justificativa_forcar_avanco: str | None = None,
    ) -> Safra:
        safra = await self.get_or_fail(safra_id)
        permitidas = SAFRA_TRANSICOES.get(safra.status, [])
        if novo_status not in permitidas:
            raise BusinessRuleError(
                f"Transição inválida: {safra.status} → {novo_status}. "
                f"Permitidas: {permitidas or 'nenhuma'}"
            )

        # Validação de checklist obrigatório da fase ATUAL antes de avançar
        from agricola.checklist.service import SafraChecklistService
        from agricola.tarefas.models import SafraTarefa
        
        checklist_svc = SafraChecklistService(self.session, self.tenant_id)
        status_checklist = await checklist_svc.status_fase(safra_id, safra.status)
        
        # Validação de tarefas críticas pendentes na fase atual
        stmt_tarefas = select(func.count(SafraTarefa.id)).where(
            SafraTarefa.safra_id == safra_id,
            SafraTarefa.tenant_id == self.tenant_id,
            SafraTarefa.fase == safra.status,
            SafraTarefa.criticidade == "CRITICA",
            SafraTarefa.status.notin_(["CONCLUIDA", "CANCELADA"])
        )
        tarefas_criticas_pendentes = (await self.session.execute(stmt_tarefas)).scalar() or 0
        
        if not forcar_avanco:
            if not status_checklist.pode_avancar:
                raise BusinessRuleError(
                    f"Bloqueio de fase: Existem {status_checklist.obrigatorios_pendentes} "
                    "atividades obrigatórias pendentes no checklist desta fase."
                )
            if tarefas_criticas_pendentes > 0:
                raise BusinessRuleError(
                    f"Bloqueio de fase: Existem {tarefas_criticas_pendentes} tarefas críticas pendentes nesta fase."
                )
        else:
            if not justificativa_forcar_avanco:
                raise BusinessRuleError("Para forçar o avanço de fase (bypass), é obrigatório informar uma justificativa.")

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
            forcou_avanco=forcar_avanco,
            justificativa_avanco=justificativa_forcar_avanco if forcar_avanco else None,
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

        # Calcula área total da safra (soma das áreas dos cultivos)
        from sqlalchemy import and_
        stmt_area = select(func.sum(CultivoArea.area_ha)).join(
            Cultivo, CultivoArea.cultivo_id == Cultivo.id
        ).where(
            and_(
                Cultivo.safra_id == safra_id,
                Cultivo.tenant_id == self.tenant_id,
                CultivoArea.tenant_id == self.tenant_id,
            )
        )
        area = float((await self.session.execute(stmt_area)).scalar() or 0)
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
        from sqlalchemy import delete
        from core.cadastros.propriedades.models import AreaRural
        from sqlalchemy.future import select

        # Remove existentes
        await self.session.execute(
            delete(SafraTalhao).where(
                SafraTalhao.safra_id == safra_id,
                SafraTalhao.tenant_id == self.tenant_id,
            )
        )
        await self.session.flush()

        novos = []
        for tid in talhao_ids:
            # Procura area_ha com chaves como str (UUID) ou UUID direto
            area_ha_valor = None
            if areas_ha:
                area_ha_valor = areas_ha.get(str(tid)) or areas_ha.get(tid)

            # Validar se area_ha foi informado
            if area_ha_valor is not None:
                # Buscar área cadastrada do talhão
                area_stmt = select(AreaRural).where(
                    AreaRural.id == tid,
                    AreaRural.tenant_id == self.tenant_id,
                )
                area = (await self.session.execute(area_stmt)).scalars().first()

                if not area:
                    raise BusinessRuleError(f"Talhão {tid} não encontrado.")

                # Validar valor negativo
                if area_ha_valor < 0:
                    raise BusinessRuleError(f"Área em hectares não pode ser negativa.")

                # Validar se não excede área cadastrada
                area_cadastrada = float(area.area_hectares or area.area_hectares_manual or 0)
                if area_cadastrada > 0 and area_ha_valor > area_cadastrada:
                    raise BusinessRuleError(
                        f"Área informada ({area_ha_valor} ha) não pode ser maior que a área "
                        f"cadastrada do talhão ({area_cadastrada} ha)."
                    )

            st = SafraTalhao(
                tenant_id=self.tenant_id,
                safra_id=safra_id,
                area_id=tid,
                principal=False,  # Nenhum talhão é "principal" - todos têm igual importância
                area_ha=area_ha_valor,
            )
            self.session.add(st)
            novos.append(st)

        await self.session.flush()

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
        from operacional.models.estoque import EstoqueMovimento, LoteEstoque, Deposito
        from core.cadastros.produtos.models import Produto
        from agricola.operacoes.models import OperacaoAgricola, OperacaoExecucao

        # Validar tenant isolation
        safra = await self.get_or_fail(safra_id)

        stmt = (
            select(
                EstoqueMovimento.id,
                EstoqueMovimento.produto_id,
                EstoqueMovimento.lote_id,
                EstoqueMovimento.deposito_id,
                EstoqueMovimento.tipo_movimento,
                EstoqueMovimento.quantidade,
                EstoqueMovimento.custo_unitario,
                EstoqueMovimento.custo_total,
                EstoqueMovimento.origem_id,
                EstoqueMovimento.origem,
                EstoqueMovimento.data_movimento,
                Produto.nome.label("produto_nome"),
                Produto.unidade_medida.label("unidade_estoque"),
                LoteEstoque.numero_lote,
                Deposito.nome.label("deposito_nome"),
                OperacaoAgricola.tipo.label("operacao_tipo"),
            )
            .join(Produto, EstoqueMovimento.produto_id == Produto.id, isouter=True)
            .join(LoteEstoque, EstoqueMovimento.lote_id == LoteEstoque.id, isouter=True)
            .join(Deposito, EstoqueMovimento.deposito_id == Deposito.id, isouter=True)
            .join(OperacaoExecucao, EstoqueMovimento.operacao_execucao_id == OperacaoExecucao.id, isouter=True)
            .join(OperacaoAgricola, OperacaoExecucao.operacao_id == OperacaoAgricola.id, isouter=True)
            .where(
                OperacaoAgricola.safra_id == safra_id,
                OperacaoAgricola.tenant_id == self.tenant_id,
            )
        )

        if tipo:
            stmt = stmt.where(EstoqueMovimento.tipo_movimento == tipo)
        if deposito_id:
            stmt = stmt.where(EstoqueMovimento.deposito_id == deposito_id)
        if data_inicio:
            stmt = stmt.where(EstoqueMovimento.data_movimento >= data_inicio)
        if data_fim:
            stmt = stmt.where(EstoqueMovimento.data_movimento <= data_fim)
        if numero_lote:
            stmt = stmt.where(LoteEstoque.numero_lote.ilike(f"%{numero_lote}%"))

        stmt = stmt.order_by(EstoqueMovimento.data_movimento.desc()).limit(limit).offset(offset)

        rows = await self.session.execute(stmt)
        movimentacoes = rows.all()

        count_stmt = (
            select(func.count(EstoqueMovimento.id))
            .join(OperacaoExecucao, EstoqueMovimento.operacao_execucao_id == OperacaoExecucao.id, isouter=True)
            .join(OperacaoAgricola, OperacaoExecucao.operacao_id == OperacaoAgricola.id, isouter=True)
            .where(
                OperacaoAgricola.safra_id == safra_id,
                OperacaoAgricola.tenant_id == self.tenant_id,
            )
        )
        if tipo:
            count_stmt = count_stmt.where(EstoqueMovimento.tipo_movimento == tipo)
        if deposito_id:
            count_stmt = count_stmt.where(EstoqueMovimento.deposito_id == deposito_id)
        if data_inicio:
            count_stmt = count_stmt.where(EstoqueMovimento.data_movimento >= data_inicio)
        if data_fim:
            count_stmt = count_stmt.where(EstoqueMovimento.data_movimento <= data_fim)
        if numero_lote:
            count_stmt = count_stmt.join(LoteEstoque, EstoqueMovimento.lote_id == LoteEstoque.id, isouter=True)
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
                    "tipo": mov.tipo_movimento,
                    "quantidade": float(mov.quantidade),
                    "unidade": mov.unidade_estoque,
                    "custo_unitario": float(mov.custo_unitario) if mov.custo_unitario else None,
                    "custo_total": float(mov.custo_total) if mov.custo_total else None,
                    "motivo": None,
                    "origem_id": mov.origem_id,
                    "origem_tipo": mov.origem,
                    "operacao_tipo": mov.operacao_tipo,
                    "data_movimentacao": mov.data_movimento,
                }
                for mov in movimentacoes
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    async def get_lotes_safra(
        self,
        safra_id: UUID,
        deposito_id: UUID | None = None,
    ) -> dict:
        """
        Retorna lotes (batches) consumidos em operações da safra.
        Mostra informações de rastreabilidade (numero_lote, fornecedor, custo histórico).
        """
        from operacional.models.estoque import LoteEstoque, Deposito, EstoqueMovimento
        from core.cadastros.produtos.models import Produto
        from agricola.operacoes.models import OperacaoAgricola, OperacaoExecucao

        # Validar tenant isolation
        safra = await self.get_or_fail(safra_id)

        stmt = (
            select(
                LoteEstoque.id,
                LoteEstoque.numero_lote,
                LoteEstoque.produto_id,
                LoteEstoque.deposito_id,
                LoteEstoque.quantidade_inicial,
                LoteEstoque.quantidade_atual,
                LoteEstoque.custo_unitario,
                LoteEstoque.status,
                LoteEstoque.data_fabricacao,
                LoteEstoque.data_validade,
                LoteEstoque.nota_fiscal_ref,
                LoteEstoque.created_at,
                Produto.nome.label("produto_nome"),
                Deposito.nome.label("deposito_nome"),
            )
            .join(Deposito, LoteEstoque.deposito_id == Deposito.id)
            .join(Produto, LoteEstoque.produto_id == Produto.id)
            .join(EstoqueMovimento, LoteEstoque.id == EstoqueMovimento.lote_id, isouter=True)
            .join(OperacaoExecucao, EstoqueMovimento.operacao_execucao_id == OperacaoExecucao.id, isouter=True)
            .join(OperacaoAgricola, OperacaoExecucao.operacao_id == OperacaoAgricola.id, isouter=True)
            .where(
                OperacaoAgricola.safra_id == safra_id,
                OperacaoAgricola.tenant_id == self.tenant_id,
            )
            .distinct()
        )

        # Filtro por depósito se especificado
        if deposito_id:
            stmt = stmt.where(LoteEstoque.deposito_id == deposito_id)

        # Ordena por data de criação (mais recentes primeiro)
        stmt = stmt.order_by(LoteEstoque.created_at.desc())

        rows = await self.session.execute(stmt)
        lotes = rows.all()

        return {
            "safra_id": safra_id,
            "total_lotes": len(lotes),
            "lotes": [
                {
                    "id": lote.id,
                    "numero_lote": lote.numero_lote,
                    "produto_id": lote.produto_id,
                    "produto_nome": lote.produto_nome,
                    "deposito_id": lote.deposito_id,
                    "deposito_nome": lote.deposito_nome,
                    "quantidade_inicial": float(lote.quantidade_inicial),
                    "quantidade_atual": float(lote.quantidade_atual),
                    "custo_unitario": float(lote.custo_unitario),
                    "status": lote.status,
                    "data_fabricacao": lote.data_fabricacao,
                    "data_validade": lote.data_validade,
                    "nota_fiscal_ref": lote.nota_fiscal_ref,
                    "created_at": lote.created_at,
                }
                for lote in lotes
            ],
        }
