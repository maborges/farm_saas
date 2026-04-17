import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.base_service import BaseService
from core.exceptions import BusinessRuleError, EntityNotFoundError
from core.cadastros.equipamentos.models import Equipamento as Maquinario
from operacional.models.abastecimento import Abastecimento, LocalAbastecimento
from operacional.schemas.abastecimento import AbastecimentoCreate, AbastecimentoUpdate
from operacional.services.estoque_service import EstoqueService

class AbastecimentoService(BaseService[Abastecimento]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(Abastecimento, session, tenant_id)

    async def registrar(self, dados: AbastecimentoCreate) -> Abastecimento:
        """
        Registra um novo abastecimento com lógica de baixa de estoque ou custo financeiro.
        """
        # 1. Valida Equipamento
        maquina = await self.session.get(Maquinario, dados.equipamento_id)
        if not maquina or maquina.tenant_id != self.tenant_id:
            raise EntityNotFoundError("Equipamento não encontrado")

        custo_total = round(dados.litros * dados.preco_litro, 2)
        
        ab = Abastecimento(
            tenant_id=self.tenant_id,
            custo_total=custo_total,
            **dados.model_dump()
        )
        self.session.add(ab)

        # 2. Atualiza horímetro/km do equipamento se for maior que o atual
        if dados.horimetro_na_data > maquina.horimetro_atual:
            maquina.horimetro_atual = dados.horimetro_na_data
        if dados.km_na_data and dados.km_na_data > maquina.km_atual:
            maquina.km_atual = dados.km_na_data

        # 3. Baixa de Estoque (se for INTERNO)
        if dados.local == "INTERNO":
            estoque_svc = EstoqueService(self.session, self.tenant_id)
            # Tenta encontrar o produto correspondente ao combustível
            # Aqui assumimos que existe um produto no estoque com o nome/tipo do combustível
            # Em uma implementação real, o 'tipo_combustivel' estaria ligado a um produto_id
            await estoque_svc.registrar_saida_insumo_por_nome(
                nome_insumo=dados.tipo_combustivel,
                quantidade=dados.litros,
                unidade_produtiva_id=maquina.unidade_produtiva_id,
                origem_id=ab.id,
                origem_tipo="ABASTECIMENTO",
                motivo=f"Abastecimento maquina {maquina.nome}"
            )
        
        # 4. Integração Financeira (se for EXTERNO)
        if dados.local == "EXTERNO" and custo_total > 0:
            from financeiro.models.despesa import Despesa
            from financeiro.models.plano_conta import PlanoConta
            from datetime import date
            
            # Busca plano de conta padrão para combustíveis
            stmt_pc = (
                select(PlanoConta.id)
                .where(
                    PlanoConta.tenant_id == self.tenant_id,
                    PlanoConta.nome.ilike("%Combustível%"),
                    PlanoConta.natureza == "ANALITICA"
                )
                .limit(1)
            )
            plano_id = (await self.session.execute(stmt_pc)).scalar()
            
            if plano_id:
                hoje = date.today()
                despesa = Despesa(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    unidade_produtiva_id=maquina.unidade_produtiva_id,
                    plano_conta_id=plano_id,
                    descricao=f"Abastecimento Externo — {maquina.nome} ({dados.litros}L)",
                    valor_total=custo_total,
                    data_emissao=hoje,
                    data_vencimento=hoje,
                    data_pagamento=hoje,
                    status="PAGO",
                )
                self.session.add(despesa)

        await self.session.commit()
        await self.session.refresh(ab)
        return ab

    async def listar_por_equipamento(self, equipamento_id: uuid.UUID) -> List[Abastecimento]:
        stmt = select(Abastecimento).where(
            Abastecimento.tenant_id == self.tenant_id,
            Abastecimento.equipamento_id == equipamento_id
        ).order_by(Abastecimento.data.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
