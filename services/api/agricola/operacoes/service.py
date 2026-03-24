from uuid import UUID
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.exceptions import BusinessRuleError, EntityNotFoundError
from core.base_service import BaseService

from agricola.operacoes.models import OperacaoAgricola, InsumoOperacao
from agricola.operacoes.schemas import OperacaoAgricolaCreate, OperacaoAgricolaUpdate
from agricola.talhoes.models import Talhao
from agricola.safras.models import Safra
from core.cadastros.models import ProdutoCatalogo
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

        # 2. Extrai insumos
        insumos_data = dados.insumos
        dados_dict = dados.model_dump(exclude={"insumos"})
        
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
            # Busca conta ANALITICA de CUSTEIO do sistema para lançamento automático
            stmt_pc = (
                select(PlanoConta.id)
                .where(
                    PlanoConta.tenant_id == self.tenant_id,
                    PlanoConta.categoria_rfb == "CUSTEIO",
                    PlanoConta.natureza == "ANALITICA",
                    PlanoConta.ativo == True,
                )
                .limit(1)
            )
            plano_id = (await self.session.execute(stmt_pc)).scalar()
            
            if plano_id:
                despesa = Despesa(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    fazenda_id=fazenda_id,
                    plano_conta_id=plano_id,
                    descricao=f"Custo Insumos: {operacao.tipo} - Talhão {operacao.talhao_id}",
                    valor_total=float(custo_total_operacao),
                    data_emissao=operacao.data_realizada,
                    data_vencimento=operacao.data_realizada,
                    data_pagamento=operacao.data_realizada,
                    status="PAGO"
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

    async def gerar_receituario_agronomico(self, operacao_id: UUID) -> bytes:
        return b"%PDF-1.4\n..."
