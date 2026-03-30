from uuid import UUID
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from loguru import logger
from core.exceptions import BusinessRuleError, EntityNotFoundError
from core.base_service import BaseService

from agricola.operacoes.models import OperacaoAgricola, InsumoOperacao
from agricola.operacoes.schemas import OperacaoAgricolaCreate, OperacaoAgricolaUpdate, OperacaoPorFaseKPI, SafraOperacoesPorFaseResponse
from agricola.safras.models import SAFRA_FASES_ORDEM
from agricola.talhoes.models import Talhao
from agricola.safras.models import Safra
from agricola.models import OperacaoTipoFase
from core.cadastros.produtos.models import Produto
from operacional.services import EstoqueService
from financeiro.models.despesa import Despesa

class OperacaoService(BaseService[OperacaoAgricola]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(OperacaoAgricola, session, tenant_id)
        self.estoque_svc = EstoqueService(session, tenant_id)

    async def criar(self, dados: OperacaoAgricolaCreate) -> OperacaoAgricola:
        # 1. Busca talhão para obter fazenda_id
        stmt_talhao = select(Talhao.fazenda_id).where(Talhao.id == dados.talhao_id)
        fazenda_id = (await self.session.execute(stmt_talhao)).scalar()
        if not fazenda_id:
            raise EntityNotFoundError("Talhão", dados.talhao_id)

        # 2. Auto-preenche fase_safra com fase atual da safra (override permitido)
        safra_atual = await self.session.get(Safra, dados.safra_id)
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
        
        operacao = OperacaoAgricola(
            tenant_id=self.tenant_id,
            **dados_dict
        )
        self.session.add(operacao)
        await self.session.flush()

        # 3. Processa insumos e baixa estoque
        for insumo in insumos_data:
            quantidade_total = insumo.dose_por_ha * (insumo.area_aplicada or dados.area_aplicada_ha or 1.0)
            
            # Busca produto para obter preço médio
            produto = await self.session.get(Produto, insumo.insumo_id)
            if not produto:
                raise EntityNotFoundError("Produto/Insumo", insumo.insumo_id)
            
            custo_unitario = produto.preco_medio or 0.0
            custo_item = quantidade_total * custo_unitario
            
            # Baixa no estoque
            await self.estoque_svc.registrar_saida_insumo(
                produto_id=insumo.insumo_id,
                quantidade=quantidade_total,
                fazenda_id=fazenda_id,
                origem_id=operacao.id,
                origem_tipo="OPERACAO_AGRICOLA"
            )

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
                custo_unitario=custo_unitario,
                custo_total=custo_item,
            )
            # InsumoOperacao model uses 'uuid' default in some cases, 
            # but let's be explicitly safe if it's required.
            
            self.session.add(insumo_op)
            custo_total_operacao += custo_item
            
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
                    fazenda_id=fazenda_id,
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

        await self.session.commit()
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
        dados_dict = dados.model_dump(exclude_unset=True)
        return await super().update(obj_id, dados_dict)

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
