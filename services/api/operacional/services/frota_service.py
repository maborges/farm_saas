import uuid
from typing import List
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from core.base_service import BaseService
from core.exceptions import BusinessRuleError
from operacional.models.frota import Maquinario, PlanoManutencao, OrdemServico, RegistroManutencao, ItemOrdemServico
from operacional.schemas.frota import (
    PlanoManutencaoCreate, OrdemServicoCreate, OrdemServicoUpdate,
    ItemOrdemServicoCreate
)
from operacional.services.estoque_service import EstoqueService

class FrotaService(BaseService[Maquinario]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(Maquinario, session, tenant_id)

    async def criar_plano_manutencao(self, dados: PlanoManutencaoCreate) -> PlanoManutencao:
        plano = PlanoManutencao(**dados.model_dump())
        self.session.add(plano)
        await self.session.flush()
        return plano

    async def listar_planos(self, maquinario_id: uuid.UUID) -> List[PlanoManutencao]:
        stmt = select(PlanoManutencao).where(PlanoManutencao.maquinario_id == maquinario_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def abrir_os(self, dados: OrdemServicoCreate) -> OrdemServico:
        # Gera numero de OS sequencial ou baseado em timestamp
        timestamp = int(datetime.now().timestamp())
        numero_os = f"OS-{timestamp}"
        
        os = OrdemServico(
            tenant_id=self.tenant_id,
            numero_os=numero_os,
            **dados.model_dump()
        )
        
        # Opcional: Marcar maquinário em manutenção
        maquina = await self.session.get(Maquinario, dados.maquinario_id)
        if maquina:
            maquina.status = "MANUTENCAO"
            
        self.session.add(os)
        await self.session.commit()
        return os

    async def adicionar_item_os(self, os_id: uuid.UUID, dados: ItemOrdemServicoCreate) -> ItemOrdemServico:
        os = await self.session.get(OrdemServico, os_id)
        if not os or os.tenant_id != self.tenant_id:
            raise BusinessRuleError("Ordem de serviço não encontrada.")
        
        # Busca preço médio do produto para registrar o custo histórico na OS
        from core.cadastros.models import ProdutoCatalogo as Produto
        produto = await self.session.get(Produto, dados.produto_id)
        if not produto:
            raise BusinessRuleError("Produto não encontrado.")

        item = ItemOrdemServico(
            os_id=os_id,
            produto_id=dados.produto_id,
            quantidade=dados.quantidade,
            preco_unitario_na_data=produto.preco_medio
        )
        
        # Atualiza custo total de peças na OS
        os.custo_total_pecas += (dados.quantidade * produto.preco_medio)
        
        self.session.add(item)
        await self.session.commit()
        return item

    async def fechar_os(self, os_id: uuid.UUID, dados: OrdemServicoUpdate) -> OrdemServico:
        os = await self.session.get(OrdemServico, os_id)
        if not os or os.tenant_id != self.tenant_id:
            raise BusinessRuleError("Ordem de serviço não encontrada.")
            
        if os.status == "CONCLUIDA":
            raise BusinessRuleError("Esta OS já foi concluída.")

        # 1. Atualiza dados básicos
        for key, value in dados.model_dump(exclude_unset=True).items():
            setattr(os, key, value)
            
        os.status = "CONCLUIDA"
        os.data_conclusao = datetime.now(timezone.utc)
        
        # 2. Marcar maquinário como ATIVO e atualizar horímetro se houve evolução
        maquina = await self.session.get(Maquinario, os.maquinario_id)
        if maquina:
            maquina.status = "ATIVO"
            # Aqui poderíamos atualizar o horímetro da máquina se a OS registrou o uso final
        
        # 3. Baixa Automática no Estoque para cada item da OS
        estoque_svc = EstoqueService(self.session, self.tenant_id)
        
        stmt_itens = select(ItemOrdemServico).where(ItemOrdemServico.os_id == os_id)
        itens = (await self.session.execute(stmt_itens)).scalars().all()
        
        for item in itens:
            await estoque_svc.registrar_saida_insumo(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                fazenda_id=maquina.fazenda_id, # Usamos a fazenda do maquinário
                origem_id=os.id,
                origem_tipo="ORDEM_SERVICO",
                motivo=f"Uso na OS {os.numero_os} - {maquina.nome}"
            )
            
        # 4. Gera registro histórico consolidado
        custo_os = os.custo_total_pecas + (os.custo_mao_obra or 0)
        registro = RegistroManutencao(
            maquinario_id=os.maquinario_id,
            os_id=os.id,
            tipo=os.tipo,
            descricao=f"OS {os.numero_os} concluída: {os.descricao_problema}",
            custo_total=custo_os,
            horimetro_na_data=os.horimetro_na_abertura,
            tecnico_responsavel=os.tecnico_responsavel
        )
        self.session.add(registro)

        # 5. Integração Financeira: Despesa de Manutenção
        if maquina and maquina.fazenda_id and custo_os > 0:
            from datetime import date as _date
            from financeiro.models.despesa import Despesa
            from financeiro.models.plano_conta import PlanoConta
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
                hoje = _date.today()
                self.session.add(Despesa(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    fazenda_id=maquina.fazenda_id,
                    plano_conta_id=plano_id,
                    descricao=f"Manutenção — {os.numero_os}: {maquina.nome}",
                    valor_total=round(custo_os, 2),
                    data_emissao=hoje,
                    data_vencimento=hoje,
                    data_pagamento=hoje,
                    status="PAGO",
                ))

        await self.session.commit()
        await self.session.refresh(os)
        return os
