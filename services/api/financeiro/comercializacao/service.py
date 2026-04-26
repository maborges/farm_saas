"""
Service — ComercializacaoCommodity
"""
import uuid
from datetime import date
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import BusinessRuleError, EntityNotFoundError
from .models import ComercializacaoCommodity


# Transições permitidas de status
TRANSICOES = {
    "RASCUNHO":     ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO":   ["EM_TRANSITO", "CANCELADO"],
    "EM_TRANSITO":  ["ENTREGUE", "CANCELADO"],
    "ENTREGUE":     ["FINALIZADO"],
    "FINALIZADO":   [],
    "CANCELADO":    [],
}


class ComercializacaoService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def listar(
        self,
        status: Optional[str] = None,
        commodity_id: Optional[uuid.UUID] = None,
        comprador_id: Optional[uuid.UUID] = None,
    ) -> list[ComercializacaoCommodity]:
        stmt = select(ComercializacaoCommodity).where(
            ComercializacaoCommodity.tenant_id == self.tenant_id,
        )
        if status:
            stmt = stmt.where(ComercializacaoCommodity.status == status)
        if commodity_id:
            stmt = stmt.where(ComercializacaoCommodity.commodity_id == commodity_id)
        if comprador_id:
            stmt = stmt.where(ComercializacaoCommodity.comprador_id == comprador_id)
        return list((await self.session.execute(stmt.order_by(ComercializacaoCommodity.created_at.desc()))).scalars().all())

    async def criar(self, data) -> ComercializacaoCommodity:
        from sqlalchemy import or_
        from core.cadastros.commodities.models import Commodity
        from core.cadastros.pessoas.models import Pessoa
        from core.exceptions import EntityNotFoundError

        stmt_c = select(Commodity).where(
            Commodity.id == data.commodity_id,
            or_(Commodity.tenant_id == self.tenant_id, Commodity.sistema == True),
        )
        if not (await self.session.execute(stmt_c)).scalar_one_or_none():
            raise EntityNotFoundError("Commodity não encontrada")

        stmt_p = select(Pessoa).where(Pessoa.id == data.comprador_id, Pessoa.tenant_id == self.tenant_id)
        if not (await self.session.execute(stmt_p)).scalar_one_or_none():
            raise EntityNotFoundError("Comprador não encontrado")

        valor_total = round(data.quantidade * data.preco_unitario, 2)
        obj = ComercializacaoCommodity(tenant_id=self.tenant_id, valor_total=valor_total, **data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def obter(self, comercializacao_id: uuid.UUID) -> ComercializacaoCommodity:
        from core.exceptions import EntityNotFoundError
        stmt = select(ComercializacaoCommodity).where(
            ComercializacaoCommodity.id == comercializacao_id,
            ComercializacaoCommodity.tenant_id == self.tenant_id,
        )
        obj = (await self.session.execute(stmt)).scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Comercialização não encontrada")
        return obj

    async def remover(self, comercializacao_id: uuid.UUID) -> None:
        from core.exceptions import BusinessRuleError
        obj = await self.obter(comercializacao_id)
        if obj.status not in ("RASCUNHO", "CANCELADO"):
            raise BusinessRuleError("Só é possível excluir comercializações em RASCUNHO ou CANCELADO")
        await self.session.delete(obj)

    async def transicionar_status(
        self,
        comercializacao: ComercializacaoCommodity,
        novo_status: str,
        data_entrega_real: Optional[date] = None,
    ) -> ComercializacaoCommodity:
        """
        Transiciona o status da comercialização e executa efeitos colaterais:
        - CONFIRMADO: gera Receita no financeiro, reserva ProdutoColhido
        - EM_TRANSITO: (sem efeito automático adicional)
        - ENTREGUE: registra data_real se não informada
        - FINALIZADO: marca ProdutoColhido como VENDIDO
        """
        if novo_status not in TRANSICOES.get(comercializacao.status, []):
            raise BusinessRuleError(
                f"Transição inválida: '{comercializacao.status}' → '{novo_status}'. "
                f"Permitidas: {', '.join(TRANSICOES.get(comercializacao.status, []))}"
            )

        # ── Efeitos colaterais por transição ──────────────────────────

        if novo_status == "CONFIRMADO":
            await self._efeito_confirmado(comercializacao)

        if novo_status == "ENTREGUE":
            if data_entrega_real:
                comercializacao.data_entrega_real = data_entrega_real
            elif not comercializacao.data_entrega_real:
                from datetime import date as _date_mod
                comercializacao.data_entrega_real = _date_mod.today()

        if novo_status == "FINALIZADO":
            await self._efeito_finalizado(comercializacao)

        comercializacao.status = novo_status
        await self.session.commit()
        await self.session.refresh(comercializacao)
        return comercializacao

    async def _efeito_confirmado(self, comercializacao: ComercializacaoCommodity):
        """Ao confirmar: gera conta a receber + reserva estoque."""

        # 1. Reservar ProdutoColhido
        if comercializacao.produto_colhido_id:
            from agricola.colheita.models import ProdutoColhido
            pc = await self.session.get(ProdutoColhido, comercializacao.produto_colhido_id)
            if pc and pc.status == "ARMAZENADO":
                pc.status = "RESERVADO"

        # 2. Gerar Receita no financeiro
        await self._gerar_receita(comercializacao)

    async def _efeito_finalizado(self, comercializacao: ComercializacaoCommodity):
        """Ao finalizar: libera ProdutoColhido como VENDIDO."""
        if comercializacao.produto_colhido_id:
            from agricola.colheita.models import ProdutoColhido
            pc = await self.session.get(ProdutoColhido, comercializacao.produto_colhido_id)
            if pc and pc.status == "RESERVADO":
                pc.status = "VENDIDO"

    async def _gerar_receita(self, comercializacao: ComercializacaoCommodity):
        """Gera Receita (contas a receber) vinculada à comercialização."""
        from financeiro.models.receita import Receita
        from financeiro.models.plano_conta import PlanoConta

        # Buscar unidade_produtiva via ProdutoColhido → SafraTalhao → AreaRural
        unidade_produtiva_id = None
        if comercializacao.produto_colhido_id:
            from agricola.colheita.models import ProdutoColhido
            pc = await self.session.get(ProdutoColhido, comercializacao.produto_colhido_id)
            if pc:
                from core.cadastros.propriedades.models import AreaRural
                area = await self.session.get(AreaRural, pc.talhao_id)
                if area and area.unidade_produtiva_id:
                    unidade_produtiva_id = area.unidade_produtiva_id

        # Fallback: buscar qualquer unidade do tenant
        if not unidade_produtiva_id:
            from core.models import Fazenda
            faz = (await self.session.execute(
                select(Fazenda).where(Fazenda.tenant_id == self.tenant_id).limit(1)
            )).scalar_one_or_none()
            if faz:
                unidade_produtiva_id = faz.id

        # Buscar plano de conta de receita de atividade
        stmt_pc = (
            select(PlanoConta.id)
            .where(
                PlanoConta.tenant_id == self.tenant_id,
                PlanoConta.categoria_rfb == "RECEITA_ATIVIDADE",
                PlanoConta.natureza == "ANALITICA",
                PlanoConta.ativo == True,
            )
            .limit(1)
        )
        plano_id = (await self.session.execute(stmt_pc)).scalar_one_or_none()

        if not unidade_produtiva_id or not plano_id:
            # Sem infraestrutura financeira — apenas loga, não falha
            # (o admin pode criar a receita manualmente depois)
            return

        # Obter nome da commodity para descrição
        from core.cadastros.commodities.models import Commodity
        commodity = await self.session.get(Commodity, comercializacao.commodity_id)
        commodity_nome = commodity.nome if commodity else "Commodity"

        descricao = (
            f"Venda de {commodity_nome} — {comercializacao.quantidade:.3f} {comercializacao.unidade} "
            f"× {comercializacao.preco_unitario:.2f} {comercializacao.moeda}"
        )

        # Datas
        data_emissao = comercializacao.data_entrega_prevista or date.today()
        data_vencimento = comercializacao.data_entrega_prevista or date.today()

        # Mapear forma_pagamento
        forma_map = {
            "A_VISTA": "PIX",
            "PRAZO": None,
            "BOLETO": "BOLETO",
            "PIX": "PIX",
            "TRANSFERENCIA": "TRANSFERENCIA",
        }
        forma_receb = forma_map.get(comercializacao.forma_pagamento) if comercializacao.forma_pagamento else None

        rec = Receita(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            unidade_produtiva_id=unidade_produtiva_id,
            plano_conta_id=plano_id,
            pessoa_id=comercializacao.comprador_id,
            descricao=descricao,
            valor_total=float(comercializacao.valor_total),
            data_emissao=data_emissao,
            data_vencimento=data_vencimento,
            status="A_RECEBER",
            forma_recebimento=forma_receb,
            origem_id=comercializacao.id,
            origem_tipo="COMERCIALIZACAO",
            numero_nf=comercializacao.nf_numero,
            serie_nf=comercializacao.nf_serie,
            chave_nfe=comercializacao.nf_chave,
            observacoes=comercializacao.observacoes,
        )
        self.session.add(rec)
        comercializacao.receita_id = rec.id
