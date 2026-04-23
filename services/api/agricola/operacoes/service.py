from uuid import UUID
import uuid
from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from loguru import logger
from core.exceptions import BusinessRuleError, EntityNotFoundError
from core.base_service import BaseService

from agricola.operacoes.models import OperacaoAgricola, InsumoOperacao
from agricola.operacoes.schemas import OperacaoAgricolaCreate, OperacaoAgricolaUpdate, OperacaoPorFaseKPI, SafraOperacoesPorFaseResponse
from agricola.safras.models import SAFRA_FASES_ORDEM
from core.cadastros.propriedades.models import AreaRural
from agricola.safras.models import Safra
from agricola.models import OperacaoTipoFase
from core.cadastros.produtos.models import Produto
from operacional.services import EstoqueService
from operacional.models.estoque import MovimentacaoEstoque
from operacional.services.estoque_fifo import consumir_lotes_fifo, atualizar_saldo_apos_consumo
from financeiro.models.despesa import Despesa
from agricola.caderno.models import CadernoCampoEntrada

class OperacaoService(BaseService[OperacaoAgricola]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(OperacaoAgricola, session, tenant_id)
        self.estoque_svc = EstoqueService(session, tenant_id)

    async def criar(self, dados: OperacaoAgricolaCreate) -> OperacaoAgricola:
        # 1. Busca talhão para obter unidade_produtiva_id
        stmt_talhao = select(AreaRural.unidade_produtiva_id).where(AreaRural.id == dados.talhao_id)
        unidade_produtiva_id = (await self.session.execute(stmt_talhao)).scalar()
        if not unidade_produtiva_id:
            raise EntityNotFoundError("Talhão", dados.talhao_id)

        # 2. Auto-preenche fase_safra com fase atual da safra (override permitido)
        safra_stmt = select(Safra).where(Safra.id == dados.safra_id, Safra.tenant_id == self.tenant_id)
        safra_atual = (await self.session.execute(safra_stmt)).scalar_one_or_none()
        if not safra_atual:
            raise EntityNotFoundError("Safra", dados.safra_id)
        fase_safra = dados.fase_safra or safra_atual.status

        # 2.5. VALIDAÇÃO: Operação só permitida em fases específicas
        # Busca lookup table para tipo de operação
        tipo_fase_stmt = select(OperacaoTipoFase).where(
            OperacaoTipoFase.tipo_operacao == dados.tipo
        )
        tipo_fase = (await self.session.execute(tipo_fase_stmt)).scalars().first()

        if not tipo_fase:
            logger.warning(f"Tipo de operação '{dados.tipo}' não cadastrado em lookup table")
            raise BusinessRuleError(
                f"Tipo de operação '{dados.tipo}' não está cadastrado no sistema. "
                f"Tipos permitidos: PLANTIO, COLHEITA, PULVERIZAÇÃO, ADUBAÇÃO, etc."
            )

        # Validar se fase atual está permitida para este tipo
        if fase_safra not in tipo_fase.fases_permitidas:
            raise BusinessRuleError(
                f"Operação '{dados.tipo}' não é permitida na fase '{fase_safra}'. "
                f"Fases permitidas: {', '.join(tipo_fase.fases_permitidas)}"
            )

        # 2.6. VALIDAÇÃO: Data não pode ser futura
        if dados.data_realizada > date.today():
            raise BusinessRuleError(
                f"Data da operação não pode ser futura. "
                f"Informe a data em que a operação foi realmente realizada."
            )

        # 3. Extrai insumos
        insumos_data = dados.insumos
        dados_dict = dados.model_dump(exclude={"insumos"})
        dados_dict["fase_safra"] = fase_safra

        custo_total_operacao = 0.0

        # Create operacao in memory (NOT flushed yet)
        operacao = OperacaoAgricola(
            tenant_id=self.tenant_id,
            **dados_dict
        )
        self.session.add(operacao)

        # IMPORTANT: Do NOT flush operacao here. Process insumos first.
        # If FIFO fails, entire transaction will be rolled back.

        # 3. Processa insumos e baixa estoque (FIFO) - BEFORE flushing operacao
        try:
            for insumo in insumos_data:
                quantidade_total = insumo.dose_por_ha * (insumo.area_aplicada or dados.area_aplicada_ha or 1.0)

                # Busca produto
                produto = await self.session.get(Produto, insumo.insumo_id)
                if not produto:
                    raise EntityNotFoundError("Produto/Insumo", insumo.insumo_id)

                # FIFO: Consume oldest batches first
                try:
                    consumo = await consumir_lotes_fifo(
                        session=self.session,
                        produto_id=insumo.insumo_id,
                        quantidade_necessaria=quantidade_total,
                        tenant_id=self.tenant_id,
                    )
                except BusinessRuleError as e:
                    logger.warning(f"FIFO consumption failed for {insumo.insumo_id}: {e}")
                    raise

                # Custo real vem do FIFO (lotes históricos), não do preço médio
                custo_item = consumo.custo_total

                # Record MovimentacaoEstoque for each lote consumed (includes deposito_id for audit trail)
                for lote_consumido in consumo.lotes_consumidos:
                    mov = MovimentacaoEstoque(
                        id=uuid.uuid4(),
                        deposito_id=lote_consumido["deposito_id"],  # Required: audit trail of which deposit
                        produto_id=insumo.insumo_id,
                        usuario_id=None,
                        lote_id=lote_consumido["lote_id"],
                        tipo="SAIDA",
                        quantidade=lote_consumido["quantidade"],
                        data_movimentacao=datetime.now(timezone.utc),
                        custo_unitario=lote_consumido["custo_unitario"],
                        custo_total=lote_consumido["custo"],
                        motivo=f"Aplicação em operação agrícola ({operacao.tipo})",
                        origem_id=operacao.id,
                        origem_tipo="OPERACAO_AGRICOLA",
                    )
                    self.session.add(mov)
                    logger.info(
                        f"Batch consumed via FIFO: {lote_consumido['numero_lote']} × {lote_consumido['quantidade']}",
                        lote_id=str(lote_consumido["lote_id"]),
                        deposito_id=str(lote_consumido["deposito_id"]),
                        quantidade=lote_consumido["quantidade"],
                        custo=lote_consumido["custo"],
                    )

                # Record InsumoOperacao with actual FIFO cost
                # custo_unitario = weighted average of all consumed batches
                insumo_op = InsumoOperacao(
                    id=uuid.uuid4(),
                    operacao_id=operacao.id,
                    tenant_id=self.tenant_id,
                    insumo_id=insumo.insumo_id,
                    lote_insumo=insumo.lote_insumo,
                    dose_por_ha=insumo.dose_por_ha,
                    unidade=insumo.unidade,
                    area_aplicada=insumo.area_aplicada,
                    quantidade_total=quantidade_total,
                    custo_unitario=consumo.custo_total / quantidade_total if quantidade_total > 0 else 0.0,  # Weighted avg
                    custo_total=custo_item,
                )

                self.session.add(insumo_op)
                custo_total_operacao += custo_item

                # Update SaldoEstoque after FIFO consumption (required for UI accuracy)
                await atualizar_saldo_apos_consumo(
                    session=self.session,
                    produto_id=insumo.insumo_id,
                    quantidade_total=quantidade_total,
                )

            # All insumos processed successfully - finalize operacao
            operacao.custo_total = custo_total_operacao
            if operacao.area_aplicada_ha and operacao.area_aplicada_ha > 0:
                operacao.custo_por_ha = custo_total_operacao / operacao.area_aplicada_ha

            # 4. Sincroniza custo na Safra
            safra = await self.session.get(Safra, operacao.safra_id)
            if safra:
                # Re-calcula custo realizado por ha baseado em todas as operações (simplificado para fins de refino)
                stmt_sum = select(func.sum(OperacaoAgricola.custo_total)).where(OperacaoAgricola.safra_id == safra.id)
                total_acumulado = (await self.session.execute(stmt_sum)).scalar() or 0.0
                if safra.area_plantada_ha and safra.area_plantada_ha > 0:
                    safra.custo_realizado_ha = (float(total_acumulado) + custo_total_operacao) / float(safra.area_plantada_ha)

            # 5. Registra Despesa no Financeiro (Módulo Integrado)
            if custo_total_operacao > 0:
                from financeiro.models.plano_conta import PlanoConta
                # Tenta conta analítica de custeio; fallback para qualquer conta de custeio ativa
                stmt_pc = (
                    select(PlanoConta.id)
                    .where(
                        PlanoConta.tenant_id == self.tenant_id,
                        PlanoConta.categoria_rfb == "CUSTEIO",
                        PlanoConta.ativo == True,
                    )
                    .order_by(PlanoConta.natureza)  # ANALITICA < SINTETICA alfabeticamente
                    .limit(1)
                )
                plano_id = (await self.session.execute(stmt_pc)).scalar()

                if plano_id:
                    safra_desc = f"{safra_atual.cultura} {safra_atual.ano_safra}" if safra_atual else str(dados.safra_id)[:8]
                    descricao = f"{operacao.tipo} — {safra_desc} (fase {fase_safra})"
                    despesa = Despesa(
                        id=uuid.uuid4(),
                        tenant_id=self.tenant_id,
                        unidade_produtiva_id=unidade_produtiva_id,
                        plano_conta_id=plano_id,
                        descricao=descricao[:255],
                        valor_total=float(custo_total_operacao),
                        data_emissao=operacao.data_realizada,
                        data_vencimento=operacao.data_realizada,
                        data_pagamento=operacao.data_realizada,
                        status="PAGO",
                        origem_id=operacao.id,
                        origem_tipo="OPERACAO_AGRICOLA",
                    )
                    self.session.add(despesa)

            # Commit only if ALL operations succeeded (atomicity)
            # 6. TRIGGER: Se operação foi criada com status REALIZADA, cria entrada no caderno
            if operacao.status == "REALIZADA":
                SYSTEM_USER = UUID("00000000-0000-0000-0000-000000000000")
                descricao = operacao.tipo
                if operacao.area_aplicada_ha:
                    descricao += f"\nÁrea: {operacao.area_aplicada_ha} ha"
                if operacao.custo_total:
                    descricao += f"\nCusto: R$ {operacao.custo_total:.2f}"

                from agricola.caderno.models import CadernoCampoEntrada
                entrada = CadernoCampoEntrada(
                    tenant_id=self.tenant_id,
                    safra_id=operacao.safra_id,
                    talhao_id=operacao.talhao_id,
                    tipo="OPERACAO_AUTO",
                    descricao=descricao,
                    data_registro=operacao.data_realizada,
                    usuario_id=SYSTEM_USER,
                    operacao_id=operacao.id,
                )
                self.session.add(entrada)
                logger.info(
                    f"Entrada automática no caderno (criação): {operacao.tipo} → safra {operacao.safra_id}",
                    entrada_id=str(entrada.id),
                )

            # 7. Conclui a tarefa vinculada automaticamente
            if dados.tarefa_id:
                from agricola.tarefas.models import SafraTarefa
                tarefa = await self.session.get(SafraTarefa, dados.tarefa_id)
                if tarefa and tarefa.tenant_id == self.tenant_id:
                    tarefa.status = "CONCLUIDA"
                    tarefa.operacao_id = operacao.id
                    tarefa.concluida_em = datetime.now(timezone.utc)

            await self.session.commit()

        except BusinessRuleError as e:
            # FIFO failed - rollback entire transaction (operacao never persisted)
            await self.session.rollback()
            logger.error(
                f"Operation creation rolled back due to FIFO failure",
                operacao_tipo=operacao.tipo,
                safra_id=str(operacao.safra_id),
                error=str(e),
            )
            raise

        await self.session.refresh(operacao)

        return operacao

    async def buscar_condicoes_clima(self, lat: float, lng: float, data_op: date) -> dict:
        return {
            "temperatura_c": 25.0,
            "umidade_rel": 60.0,
            "vento_kmh": 10.0,
            "condicao_clima": "sol"
        }

    async def atualizar(self, obj_id: UUID, dados: OperacaoAgricolaUpdate) -> OperacaoAgricola:
        # 1. Busca estado atual antes de atualizar
        operacao_atual = await self.get_or_fail(obj_id)
        status_anterior = operacao_atual.status

        # 2. Aplica atualização
        dados_dict = dados.model_dump(exclude_unset=True)
        operacao = await super().update(obj_id, dados_dict)

        # 3. TRIGGER: Se status mudou para REALIZADA, cria entrada no caderno de campo
        novo_status = dados_dict.get("status")
        if novo_status == "REALIZADA" and status_anterior != "REALIZADA":
            descricao = operacao.tipo
            if operacao.area_aplicada_ha:
                descricao += f"\nÁrea: {operacao.area_aplicada_ha} ha"
            if operacao.custo_total:
                descricao += f"\nCusto: R$ {operacao.custo_total:.2f}"

            # UUID "zero" para indicar origem automática do sistema
            SYSTEM_USER = UUID("00000000-0000-0000-0000-000000000000")

            entrada = CadernoCampoEntrada(
                tenant_id=self.tenant_id,
                safra_id=operacao.safra_id,
                talhao_id=operacao.talhao_id,
                tipo="OPERACAO_AUTO",
                descricao=descricao,
                data_registro=operacao.data_realizada,
                usuario_id=SYSTEM_USER,
                operacao_id=operacao.id,
            )
            self.session.add(entrada)
            logger.info(
                f"Entrada automática no caderno: {operacao.tipo} → safra {operacao.safra_id}",
                entrada_id=str(entrada.id),
            )

        return operacao

    async def listar_por_safra_e_fase(
        self, safra_id: UUID, fase: str | None = None
    ) -> list[OperacaoAgricola]:
        stmt = select(OperacaoAgricola).where(
            OperacaoAgricola.safra_id == safra_id,
            OperacaoAgricola.tenant_id == self.tenant_id,
        ).order_by(OperacaoAgricola.data_realizada.desc())
        if fase:
            stmt = stmt.where(OperacaoAgricola.fase_safra == fase)
        return list((await self.session.execute(stmt)).scalars().all())

    async def resumo_por_fase(self, safra_id: UUID) -> SafraOperacoesPorFaseResponse:
        stmt = select(
            OperacaoAgricola.fase_safra,
            func.count(OperacaoAgricola.id).label("total"),
            func.coalesce(func.sum(OperacaoAgricola.custo_total), 0).label("custo_total"),
            func.coalesce(func.sum(OperacaoAgricola.area_aplicada_ha), 0).label("area_total"),
        ).where(
            OperacaoAgricola.safra_id == safra_id,
            OperacaoAgricola.tenant_id == self.tenant_id,
        ).group_by(OperacaoAgricola.fase_safra)

        rows = (await self.session.execute(stmt)).all()
        por_fase: dict[str, OperacaoPorFaseKPI] = {}
        for row in rows:
            fase = row.fase_safra or "SEM_FASE"
            area = float(row.area_total or 0)
            custo = float(row.custo_total or 0)
            por_fase[fase] = OperacaoPorFaseKPI(
                fase=fase,
                total_operacoes=row.total,
                custo_total=custo,
                custo_por_ha=round(custo / area, 2) if area > 0 else 0.0,
                area_total_ha=area,
            )

        # Ordena pelas fases do ciclo
        fases_ordenadas = [
            por_fase[f] for f in SAFRA_FASES_ORDEM if f in por_fase
        ]
        # Fases fora do ciclo padrão (SEM_FASE, etc.)
        extras = [v for k, v in por_fase.items() if k not in SAFRA_FASES_ORDEM]
        fases_ordenadas.extend(extras)

        custo_total = sum(f.custo_total for f in fases_ordenadas)
        return SafraOperacoesPorFaseResponse(
            safra_id=safra_id,
            fases=fases_ordenadas,
            custo_total_safra=custo_total,
        )

    async def gerar_receituario_agronomico(self, operacao_id: UUID) -> bytes:
        return b"%PDF-1.4\n..."
