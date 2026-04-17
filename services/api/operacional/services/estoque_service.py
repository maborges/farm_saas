from uuid import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.base_service import BaseService
from core.exceptions import BusinessRuleError, EntityNotFoundError
from datetime import date, timezone, datetime
from operacional.models.estoque import (
    Deposito, SaldoEstoque, MovimentacaoEstoque,
    LoteEstoque, RequisicaoMaterial, ItemRequisicao, ReservaEstoque,
)
from core.cadastros.models import ProdutoCatalogo
from operacional.schemas.estoque import (
    DepositoCreate, DepositoUpdate,
    EntradaEstoqueRequest,
    SaidaEstoqueRequest,
    AjusteEstoqueRequest,
    TransferenciaEstoqueRequest,
    SaldoResponse,
    AlertaEstoqueItem,
    LoteCreate, LoteUpdate,
    RequisicaoCreate, RequisicaoAprovarRequest, RequisicaoEntregarRequest,
    ReservaCreate, ReservaCancelarRequest, ReservaConsumirRequest,
)


class EstoqueService(BaseService[SaldoEstoque]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(SaldoEstoque, session, tenant_id)

    async def _get_produto(self, produto_id: UUID) -> ProdutoCatalogo | None:
        stmt = select(ProdutoCatalogo).where(
            ProdutoCatalogo.id == produto_id,
            ProdutoCatalogo.tenant_id == self.tenant_id,
        )
        return (await self.session.execute(stmt)).scalars().first()

    # ── Categorias ────────────────────────────────────────────────────────

    # ── Depósitos ─────────────────────────────────────────────────────────

    async def criar_deposito(self, data: DepositoCreate) -> Deposito:
        dep = Deposito(
            tenant_id=self.tenant_id,
            unidade_produtiva_id=data.unidade_produtiva_id,
            nome=data.nome,
            tipo=data.tipo,
            localizacao_desc=data.localizacao_desc,
        )
        self.session.add(dep)
        await self.session.flush()
        await self.session.refresh(dep)
        return dep

    async def atualizar_deposito(self, deposito_id: UUID, data: DepositoUpdate) -> Deposito:
        stmt = select(Deposito).where(
            Deposito.id == deposito_id, Deposito.tenant_id == self.tenant_id
        )
        dep = (await self.session.execute(stmt)).scalars().first()
        if not dep:
            raise EntityNotFoundError(f"Depósito {deposito_id} não encontrado.")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(dep, field, value)
        self.session.add(dep)
        await self.session.flush()
        await self.session.refresh(dep)
        return dep

    async def listar_depositos(self, unidade_produtiva_id: UUID | None = None) -> list[Deposito]:
        stmt = select(Deposito).where(Deposito.tenant_id == self.tenant_id)
        if unidade_produtiva_id:
            stmt = stmt.where(Deposito.unidade_produtiva_id == unidade_produtiva_id)
        return list((await self.session.execute(stmt)).scalars().all())

    # ── Saldos ────────────────────────────────────────────────────────────

    async def _get_ou_criar_saldo(self, deposito_id: UUID, produto_id: UUID) -> SaldoEstoque:
        stmt = select(SaldoEstoque).where(
            SaldoEstoque.deposito_id == deposito_id,
            SaldoEstoque.produto_id == produto_id,
        )
        saldo = (await self.session.execute(stmt)).scalars().first()
        if not saldo:
            saldo = SaldoEstoque(deposito_id=deposito_id, produto_id=produto_id, quantidade_atual=0.0)
            self.session.add(saldo)
            await self.session.flush()
        return saldo

    async def listar_saldos(self, unidade_produtiva_id: UUID | None = None) -> list[SaldoResponse]:
        dep_stmt = select(Deposito).where(Deposito.tenant_id == self.tenant_id, Deposito.ativo == True)
        if unidade_produtiva_id:
            dep_stmt = dep_stmt.where(Deposito.unidade_produtiva_id == unidade_produtiva_id)
        depositos = {d.id: d for d in (await self.session.execute(dep_stmt)).scalars().all()}

        prod_stmt = select(ProdutoCatalogo).where(ProdutoCatalogo.tenant_id == self.tenant_id, ProdutoCatalogo.ativo == True)
        produtos = {p.id: p for p in (await self.session.execute(prod_stmt)).scalars().all()}

        if not depositos:
            return []

        saldo_stmt = select(SaldoEstoque).where(
            SaldoEstoque.deposito_id.in_(list(depositos.keys()))
        )
        saldos = (await self.session.execute(saldo_stmt)).scalars().all()

        result = []
        for s in saldos:
            dep = depositos.get(s.deposito_id)
            prod = produtos.get(s.produto_id)
            if not dep or not prod:
                continue
            result.append(SaldoResponse(
                id=s.id,
                deposito_id=s.deposito_id,
                produto_id=s.produto_id,
                produto_nome=prod.nome,
                deposito_nome=dep.nome,
                quantidade_atual=s.quantidade_atual,
                quantidade_reservada=s.quantidade_reservada,
                quantidade_disponivel=max(0.0, s.quantidade_atual - s.quantidade_reservada),
                preco_medio=prod.preco_medio,
                unidade_medida=prod.unidade_medida,
                abaixo_minimo=s.quantidade_atual < prod.estoque_minimo,
                ultima_atualizacao=s.ultima_atualizacao,
            ))
        return result

    # ── Lotes ─────────────────────────────────────────────────────────────

    async def criar_lote(self, data: LoteCreate) -> LoteEstoque:
        lote = LoteEstoque(
            produto_id=data.produto_id,
            deposito_id=data.deposito_id,
            numero_lote=data.numero_lote,
            data_fabricacao=data.data_fabricacao,
            data_validade=data.data_validade,
            quantidade_inicial=data.quantidade_inicial,
            quantidade_atual=data.quantidade_inicial,
            custo_unitario=data.custo_unitario,
            nota_fiscal_ref=data.nota_fiscal_ref,
            status="ATIVO",
        )
        self.session.add(lote)
        await self.session.flush()
        await self.session.refresh(lote)
        return lote

    async def atualizar_lote(self, lote_id: UUID, data: LoteUpdate) -> LoteEstoque:
        stmt = select(LoteEstoque).where(LoteEstoque.id == lote_id)
        lote = (await self.session.execute(stmt)).scalars().first()
        if not lote:
            raise EntityNotFoundError(f"Lote {lote_id} não encontrado.")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(lote, field, value)
        self.session.add(lote)
        await self.session.flush()
        await self.session.refresh(lote)
        return lote

    async def listar_lotes(
        self,
        produto_id: UUID | None = None,
        deposito_id: UUID | None = None,
        vencendo_em_dias: int | None = None,
        apenas_ativos: bool = True,
    ) -> list[LoteEstoque]:
        # Garante acesso apenas a depósitos do tenant
        dep_stmt = select(Deposito.id).where(Deposito.tenant_id == self.tenant_id)
        dep_ids = set((await self.session.execute(dep_stmt)).scalars().all())

        stmt = select(LoteEstoque).where(LoteEstoque.deposito_id.in_(dep_ids))
        if produto_id:
            stmt = stmt.where(LoteEstoque.produto_id == produto_id)
        if deposito_id:
            stmt = stmt.where(LoteEstoque.deposito_id == deposito_id)
        if apenas_ativos:
            stmt = stmt.where(LoteEstoque.status == "ATIVO")
        if vencendo_em_dias is not None:
            from datetime import timedelta
            limite = date.today() + timedelta(days=vencendo_em_dias)
            stmt = stmt.where(
                LoteEstoque.data_validade != None,
                LoteEstoque.data_validade <= limite,
            )
        stmt = stmt.order_by(LoteEstoque.data_validade.asc().nullslast())
        return list((await self.session.execute(stmt)).scalars().all())

    async def _atualizar_status_lotes_vencidos(self) -> None:
        """Marca automaticamente lotes vencidos."""
        stmt = select(LoteEstoque).where(
            LoteEstoque.status == "ATIVO",
            LoteEstoque.data_validade != None,
            LoteEstoque.data_validade < date.today(),
        )
        lotes = (await self.session.execute(stmt)).scalars().all()
        for lote in lotes:
            lote.status = "VENCIDO"

    # ── Movimentações ─────────────────────────────────────────────────────

    def _registrar_mov(
        self,
        deposito_id: UUID,
        produto_id: UUID,
        tipo: str,
        quantidade: float,
        custo_unitario: float | None = None,
        motivo: str | None = None,
        origem_id: UUID | None = None,
        origem_tipo: str | None = None,
        lote_id: UUID | None = None,
    ) -> MovimentacaoEstoque:
        custo_total = round(quantidade * custo_unitario, 2) if custo_unitario else None
        mov = MovimentacaoEstoque(
            deposito_id=deposito_id,
            produto_id=produto_id,
            tipo=tipo,
            quantidade=quantidade,
            custo_unitario=custo_unitario,
            custo_total=custo_total,
            motivo=motivo,
            origem_id=origem_id,
            origem_tipo=origem_tipo,
            lote_id=lote_id,
        )
        self.session.add(mov)
        return mov

    async def _descontar_lote(self, lote_id: UUID, quantidade: float) -> LoteEstoque:
        """Desconta quantidade de um lote e atualiza status se esgotado."""
        stmt = select(LoteEstoque).where(LoteEstoque.id == lote_id)
        lote = (await self.session.execute(stmt)).scalars().first()
        if not lote:
            raise EntityNotFoundError(f"Lote {lote_id} não encontrado.")
        if lote.quantidade_atual < quantidade:
            raise BusinessRuleError(
                f"Saldo insuficiente no lote {lote.numero_lote}. "
                f"Disponível: {lote.quantidade_atual}, solicitado: {quantidade}"
            )
        lote.quantidade_atual -= quantidade
        if lote.quantidade_atual <= 0:
            lote.status = "ESGOTADO"
        return lote

    async def registrar_entrada(self, data: EntradaEstoqueRequest) -> MovimentacaoEstoque:
        stmt = select(Deposito).where(
            Deposito.id == data.deposito_id, Deposito.tenant_id == self.tenant_id
        )
        dep = (await self.session.execute(stmt)).scalars().first()
        if not dep:
            raise EntityNotFoundError("Depósito não encontrado.")

        saldo = await self._get_ou_criar_saldo(data.deposito_id, data.produto_id)
        qtd_antes = saldo.quantidade_atual
        saldo.quantidade_atual += data.quantidade

        # Atualiza preço médio ponderado
        prod = await self._get_produto(data.produto_id)
        if data.custo_unitario and data.custo_unitario > 0:
            if qtd_antes > 0:
                prod.preco_medio = round(
                    (qtd_antes * prod.preco_medio + data.quantidade * data.custo_unitario)
                    / saldo.quantidade_atual, 4
                )
            else:
                prod.preco_medio = data.custo_unitario
            self.session.add(prod)

        # Atualiza saldo do lote se informado
        if data.lote_id:
            stmt_lote = select(LoteEstoque).where(LoteEstoque.id == data.lote_id)
            lote = (await self.session.execute(stmt_lote)).scalars().first()
            if lote:
                lote.quantidade_atual += data.quantidade

        mov = self._registrar_mov(
            deposito_id=data.deposito_id,
            produto_id=data.produto_id,
            tipo="ENTRADA",
            quantidade=data.quantidade,
            custo_unitario=data.custo_unitario or prod.preco_medio,
            motivo=data.motivo or "Entrada manual",
            origem_id=data.origem_id,
            origem_tipo=data.origem_tipo or "MANUAL",
            lote_id=data.lote_id,
        )
        await self.session.flush()
        await self.session.refresh(mov)
        return mov

    async def registrar_saida_insumo(
        self,
        produto_id: UUID,
        quantidade: float,
        unidade_produtiva_id: UUID,
        origem_id: UUID,
        origem_tipo: str = "OPERACAO_AGRICOLA",
        motivo: str = "Uso em operação agrícola",
        deposito_id: UUID | None = None,
    ) -> MovimentacaoEstoque:
        if deposito_id:
            stmt_saldo = select(SaldoEstoque).where(
                SaldoEstoque.produto_id == produto_id,
                SaldoEstoque.deposito_id == deposito_id,
            )
            saldos = list((await self.session.execute(stmt_saldo)).scalars().all())
        else:
            stmt_deps = select(Deposito.id).where(
                Deposito.tenant_id == self.tenant_id,
                Deposito.unidade_produtiva_id == unidade_produtiva_id,
                Deposito.ativo == True,
            )
            dep_ids = (await self.session.execute(stmt_deps)).scalars().all()
            if not dep_ids:
                raise BusinessRuleError(f"Nenhum depósito ativo na fazenda {unidade_produtiva_id}.")
            stmt_saldo = select(SaldoEstoque).where(
                SaldoEstoque.produto_id == produto_id,
                SaldoEstoque.deposito_id.in_(dep_ids),
            ).order_by(SaldoEstoque.quantidade_atual.desc())
            saldos = list((await self.session.execute(stmt_saldo)).scalars().all())

        if not saldos:
            raise BusinessRuleError(f"Produto {produto_id} sem saldo nos depósitos.")

        saldo_sel = next((s for s in saldos if s.quantidade_atual >= quantidade), None)
        if not saldo_sel:
            total = sum(s.quantidade_atual for s in saldos)
            raise BusinessRuleError(f"Saldo insuficiente. Necessário: {quantidade}, disponível: {total}")

        saldo_sel.quantidade_atual -= quantidade
        prod = await self._get_produto(produto_id)
        mov = self._registrar_mov(
            deposito_id=saldo_sel.deposito_id,
            produto_id=produto_id,
            tipo="SAIDA",
            quantidade=quantidade,
            custo_unitario=prod.preco_medio if prod else None,
            motivo=motivo,
            origem_id=origem_id,
            origem_tipo=origem_tipo,
        )
        await self.session.flush()
        await self.session.refresh(mov)
        return mov

    async def registrar_saida_insumo_por_nome(
        self,
        nome_insumo: str,
        quantidade: float,
        unidade_produtiva_id: UUID,
        origem_id: UUID,
        origem_tipo: str = "OPERACAO_AGRICOLA",
        motivo: str = "Uso em operação agrícola",
    ) -> MovimentacaoEstoque:
        """Busca o produto pelo nome e registra a saída."""
        stmt = select(ProdutoCatalogo).where(
            ProdutoCatalogo.tenant_id == self.tenant_id,
            ProdutoCatalogo.nome.ilike(f"%{nome_insumo}%"),
            ProdutoCatalogo.ativo == True
        ).limit(1)
        prod = (await self.session.execute(stmt)).scalars().first()
        
        if not prod:
            raise EntityNotFoundError(f"Produto de estoque '{nome_insumo}' não encontrado para baixa.")

        return await self.registrar_saida_insumo(
            produto_id=prod.id,
            quantidade=quantidade,
            unidade_produtiva_id=unidade_produtiva_id,
            origem_id=origem_id,
            origem_tipo=origem_tipo,
            motivo=motivo
        )

    async def registrar_saida(self, data: SaidaEstoqueRequest) -> MovimentacaoEstoque:
        if data.deposito_id:
            stmt = select(SaldoEstoque).where(
                SaldoEstoque.produto_id == data.produto_id,
                SaldoEstoque.deposito_id == data.deposito_id,
            )
            saldo = (await self.session.execute(stmt)).scalars().first()
            if not saldo:
                raise BusinessRuleError("Saldo não encontrado para o depósito selecionado.")
            disponivel = saldo.quantidade_atual - saldo.quantidade_reservada
            if disponivel < data.quantidade:
                raise BusinessRuleError(
                    f"Saldo disponível insuficiente. Disponível: {disponivel:.3f}, Necessário: {data.quantidade:.3f}"
                )
            saldo.quantidade_atual -= data.quantidade
            if data.lote_id:
                await self._descontar_lote(data.lote_id, data.quantidade)
            prod = await self._get_produto(data.produto_id)
            mov = self._registrar_mov(
                deposito_id=data.deposito_id, produto_id=data.produto_id,
                tipo="SAIDA", quantidade=data.quantidade,
                custo_unitario=prod.preco_medio if prod else None,
                motivo=data.motivo, origem_id=data.origem_id,
                origem_tipo=data.origem_tipo or "MANUAL",
                lote_id=data.lote_id,
            )
            await self.session.flush()
            await self.session.refresh(mov)
            return mov
        elif data.unidade_produtiva_id:
            return await self.registrar_saida_insumo(
                produto_id=data.produto_id, quantidade=data.quantidade,
                unidade_produtiva_id=data.unidade_produtiva_id,
                origem_id=data.origem_id or uuid.uuid4(),
                origem_tipo=data.origem_tipo or "MANUAL",
                motivo=data.motivo or "Saída manual",
            )
        raise BusinessRuleError("Informe deposito_id ou unidade_produtiva_id.")

    async def registrar_ajuste(self, data: AjusteEstoqueRequest) -> MovimentacaoEstoque:
        saldo = await self._get_ou_criar_saldo(data.deposito_id, data.produto_id)
        diff = data.quantidade_nova - saldo.quantidade_atual
        saldo.quantidade_atual = data.quantidade_nova
        mov = self._registrar_mov(
            deposito_id=data.deposito_id, produto_id=data.produto_id,
            tipo="AJUSTE", quantidade=abs(diff),
            motivo=data.motivo, origem_tipo="AJUSTE",
        )
        await self.session.flush()
        await self.session.refresh(mov)
        return mov

    async def registrar_transferencia(self, data: TransferenciaEstoqueRequest) -> list[MovimentacaoEstoque]:
        stmt = select(SaldoEstoque).where(
            SaldoEstoque.produto_id == data.produto_id,
            SaldoEstoque.deposito_id == data.deposito_origem_id,
        )
        saldo_orig = (await self.session.execute(stmt)).scalars().first()
        if not saldo_orig or saldo_orig.quantidade_atual < data.quantidade:
            raise BusinessRuleError("Saldo insuficiente no depósito de origem.")

        saldo_orig.quantidade_atual -= data.quantidade
        saldo_dest = await self._get_ou_criar_saldo(data.deposito_destino_id, data.produto_id)
        saldo_dest.quantidade_atual += data.quantidade

        prod = await self._get_produto(data.produto_id)
        motivo = data.motivo or "Transferência entre depósitos"
        mov_saida = self._registrar_mov(
            deposito_id=data.deposito_origem_id, produto_id=data.produto_id,
            tipo="TRANSFERENCIA", quantidade=data.quantidade,
            custo_unitario=prod.preco_medio if prod else None,
            motivo=motivo, origem_tipo="TRANSFERENCIA",
        )
        mov_entrada = self._registrar_mov(
            deposito_id=data.deposito_destino_id, produto_id=data.produto_id,
            tipo="TRANSFERENCIA", quantidade=data.quantidade,
            custo_unitario=prod.preco_medio if prod else None,
            motivo=motivo, origem_tipo="TRANSFERENCIA",
        )
        await self.session.flush()
        return [mov_saida, mov_entrada]

    async def listar_movimentacoes(
        self,
        produto_id: UUID | None = None,
        deposito_id: UUID | None = None,
        limit: int = 100,
    ) -> list[MovimentacaoEstoque]:
        dep_stmt = select(Deposito.id).where(Deposito.tenant_id == self.tenant_id)
        dep_ids = set((await self.session.execute(dep_stmt)).scalars().all())

        stmt = select(MovimentacaoEstoque).where(
            MovimentacaoEstoque.deposito_id.in_(dep_ids)
        ).order_by(MovimentacaoEstoque.data_movimentacao.desc()).limit(limit)

        if produto_id:
            stmt = stmt.where(MovimentacaoEstoque.produto_id == produto_id)
        if deposito_id:
            stmt = stmt.where(MovimentacaoEstoque.deposito_id == deposito_id)

        return list((await self.session.execute(stmt)).scalars().all())

    # ── Requisições de Material ────────────────────────────────────────────

    async def criar_requisicao(self, data: RequisicaoCreate, solicitante_id: UUID) -> RequisicaoMaterial:
        req = RequisicaoMaterial(
            tenant_id=self.tenant_id,
            unidade_produtiva_id=data.unidade_produtiva_id,
            solicitante_id=solicitante_id,
            data_necessidade=data.data_necessidade,
            origem_tipo=data.origem_tipo,
            origem_id=data.origem_id,
            observacoes=data.observacoes,
            status="PENDENTE",
        )
        self.session.add(req)
        await self.session.flush()
        for item_data in data.itens:
            item = ItemRequisicao(
                requisicao_id=req.id,
                produto_id=item_data.produto_id,
                deposito_id=item_data.deposito_id,
                quantidade_solicitada=item_data.quantidade_solicitada,
                observacoes=item_data.observacoes,
            )
            self.session.add(item)
        await self.session.flush()
        await self.session.refresh(req)
        return req

    async def listar_requisicoes(
        self,
        unidade_produtiva_id: UUID | None = None,
        status: str | None = None,
        solicitante_id: UUID | None = None,
    ) -> list[RequisicaoMaterial]:
        stmt = select(RequisicaoMaterial).where(RequisicaoMaterial.tenant_id == self.tenant_id)
        if unidade_produtiva_id:
            stmt = stmt.where(RequisicaoMaterial.unidade_produtiva_id == unidade_produtiva_id)
        if status:
            stmt = stmt.where(RequisicaoMaterial.status == status)
        if solicitante_id:
            stmt = stmt.where(RequisicaoMaterial.solicitante_id == solicitante_id)
        stmt = stmt.order_by(RequisicaoMaterial.data_solicitacao.desc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def aprovar_requisicao(
        self, req_id: UUID, data: RequisicaoAprovarRequest, aprovador_id: UUID
    ) -> RequisicaoMaterial:
        stmt = select(RequisicaoMaterial).where(
            RequisicaoMaterial.id == req_id, RequisicaoMaterial.tenant_id == self.tenant_id
        )
        req = (await self.session.execute(stmt)).scalars().first()
        if not req:
            raise EntityNotFoundError(f"Requisição {req_id} não encontrada.")
        if req.status != "PENDENTE":
            raise BusinessRuleError(f"Requisição não pode ser aprovada no status '{req.status}'.")

        item_map = {i.item_id: i for i in data.itens}
        stmt_itens = select(ItemRequisicao).where(ItemRequisicao.requisicao_id == req_id)
        itens = (await self.session.execute(stmt_itens)).scalars().all()
        for item in itens:
            if item.id in item_map:
                upd = item_map[item.id]
                item.quantidade_aprovada = upd.quantidade_aprovada
                if upd.deposito_id:
                    item.deposito_id = upd.deposito_id

        req.aprovador_id = aprovador_id
        req.status = "APROVADA"
        await self.session.flush()
        await self.session.refresh(req)
        return req

    async def entregar_requisicao(
        self, req_id: UUID, data: RequisicaoEntregarRequest
    ) -> RequisicaoMaterial:
        stmt = select(RequisicaoMaterial).where(
            RequisicaoMaterial.id == req_id, RequisicaoMaterial.tenant_id == self.tenant_id
        )
        req = (await self.session.execute(stmt)).scalars().first()
        if not req:
            raise EntityNotFoundError(f"Requisição {req_id} não encontrada.")
        if req.status not in ("APROVADA", "SEPARANDO"):
            raise BusinessRuleError(f"Requisição não pode ser entregue no status '{req.status}'.")

        item_map = {i.item_id: i for i in data.itens}
        stmt_itens = select(ItemRequisicao).where(ItemRequisicao.requisicao_id == req_id)
        itens = (await self.session.execute(stmt_itens)).scalars().all()
        for item in itens:
            if item.id not in item_map:
                continue
            upd = item_map[item.id]
            qtd = upd.quantidade_entregue
            if qtd <= 0:
                continue
            if not item.deposito_id:
                raise BusinessRuleError(f"Item {item.id} sem depósito definido para entrega.")
            # Baixa de estoque
            saida = SaidaEstoqueRequest(
                deposito_id=item.deposito_id,
                produto_id=item.produto_id,
                quantidade=qtd,
                motivo=f"Requisição {req_id}",
                origem_id=req_id,
                origem_tipo="REQUISICAO",
                lote_id=upd.lote_id,
            )
            await self.registrar_saida(saida)
            item.quantidade_entregue = qtd
            item.lote_id = upd.lote_id

        req.status = "ENTREGUE"
        await self.session.flush()
        await self.session.refresh(req)
        return req

    async def atualizar_status_requisicao(self, req_id: UUID, novo_status: str) -> RequisicaoMaterial:
        stmt = select(RequisicaoMaterial).where(
            RequisicaoMaterial.id == req_id, RequisicaoMaterial.tenant_id == self.tenant_id
        )
        req = (await self.session.execute(stmt)).scalars().first()
        if not req:
            raise EntityNotFoundError(f"Requisição {req_id} não encontrada.")
        req.status = novo_status
        await self.session.flush()
        await self.session.refresh(req)
        return req

    # ── Reservas de Estoque ────────────────────────────────────────────────

    async def criar_reserva(self, data: ReservaCreate, usuario_id: UUID) -> ReservaEstoque:
        saldo = await self._get_ou_criar_saldo(data.deposito_id, data.produto_id)
        disponivel = saldo.quantidade_atual - saldo.quantidade_reservada
        if disponivel < data.quantidade:
            raise BusinessRuleError(
                f"Saldo disponível insuficiente para reserva. Disponível: {disponivel:.3f}, Solicitado: {data.quantidade:.3f}"
            )
        reserva = ReservaEstoque(
            tenant_id=self.tenant_id,
            produto_id=data.produto_id,
            deposito_id=data.deposito_id,
            criado_por_id=usuario_id,
            quantidade=data.quantidade,
            motivo=data.motivo,
            referencia_tipo=data.referencia_tipo,
            referencia_id=data.referencia_id,
            status="ATIVA",
        )
        saldo.quantidade_reservada += data.quantidade
        self.session.add(reserva)
        await self.session.flush()
        await self.session.refresh(reserva)
        return reserva

    async def cancelar_reserva(self, reserva_id: UUID) -> ReservaEstoque:
        reserva = await self._get_reserva(reserva_id)
        if reserva.status != "ATIVA":
            raise BusinessRuleError(f"Reserva não pode ser cancelada no status '{reserva.status}'.")
        saldo = await self._get_ou_criar_saldo(reserva.deposito_id, reserva.produto_id)
        saldo.quantidade_reservada = max(0.0, saldo.quantidade_reservada - reserva.quantidade)
        reserva.status = "CANCELADA"
        await self.session.flush()
        await self.session.refresh(reserva)
        return reserva

    async def consumir_reserva(self, reserva_id: UUID, data: ReservaConsumirRequest) -> ReservaEstoque:
        reserva = await self._get_reserva(reserva_id)
        if reserva.status != "ATIVA":
            raise BusinessRuleError(f"Reserva não pode ser consumida no status '{reserva.status}'.")
        qtd = data.quantidade or reserva.quantidade
        if qtd > reserva.quantidade:
            raise BusinessRuleError(f"Quantidade a consumir ({qtd:.3f}) excede a reserva ({reserva.quantidade:.3f}).")
        # Libera a reserva antes de registrar saída (evita conflito na checagem de disponível)
        saldo = await self._get_ou_criar_saldo(reserva.deposito_id, reserva.produto_id)
        saldo.quantidade_reservada = max(0.0, saldo.quantidade_reservada - reserva.quantidade)
        # Registra saída física
        await self.registrar_saida(SaidaEstoqueRequest(
            deposito_id=reserva.deposito_id,
            produto_id=reserva.produto_id,
            quantidade=qtd,
            motivo=data.motivo or f"Consumo de reserva: {reserva.motivo}",
            origem_id=reserva.referencia_id,
            origem_tipo=reserva.referencia_tipo or "RESERVA",
        ))
        reserva.status = "CONSUMIDA"
        await self.session.flush()
        await self.session.refresh(reserva)
        return reserva

    async def listar_reservas(
        self,
        produto_id: UUID | None = None,
        deposito_id: UUID | None = None,
        status: str | None = "ATIVA",
    ) -> list[ReservaEstoque]:
        # Filtra apenas reservas do tenant (via depósitos)
        dep_stmt = select(Deposito.id).where(Deposito.tenant_id == self.tenant_id)
        dep_ids = set((await self.session.execute(dep_stmt)).scalars().all())
        stmt = select(ReservaEstoque).where(
            ReservaEstoque.deposito_id.in_(dep_ids)
        ).order_by(ReservaEstoque.created_at.desc())
        if produto_id:
            stmt = stmt.where(ReservaEstoque.produto_id == produto_id)
        if deposito_id:
            stmt = stmt.where(ReservaEstoque.deposito_id == deposito_id)
        if status:
            stmt = stmt.where(ReservaEstoque.status == status)
        return list((await self.session.execute(stmt)).scalars().all())

    async def _get_reserva(self, reserva_id: UUID) -> ReservaEstoque:
        dep_stmt = select(Deposito.id).where(Deposito.tenant_id == self.tenant_id)
        dep_ids = set((await self.session.execute(dep_stmt)).scalars().all())
        stmt = select(ReservaEstoque).where(
            ReservaEstoque.id == reserva_id,
            ReservaEstoque.deposito_id.in_(dep_ids),
        )
        reserva = (await self.session.execute(stmt)).scalars().first()
        if not reserva:
            raise EntityNotFoundError(f"Reserva {reserva_id} não encontrada.")
        return reserva

    async def alertas_estoque_minimo(self, unidade_produtiva_id: UUID | None = None) -> list[AlertaEstoqueItem]:
        saldos = await self.listar_saldos(unidade_produtiva_id)

        # Busca estoque_minimo dos produtos
        prod_ids = [s.produto_id for s in saldos if s.abaixo_minimo]
        if not prod_ids:
            return []
        stmt = select(ProdutoCatalogo).where(ProdutoCatalogo.id.in_(prod_ids))
        prods = {p.id: p for p in (await self.session.execute(stmt)).scalars().all()}

        return [
            AlertaEstoqueItem(
                produto_id=s.produto_id,
                produto_nome=s.produto_nome,
                deposito_nome=s.deposito_nome,
                quantidade_atual=s.quantidade_atual,
                estoque_minimo=prods[s.produto_id].estoque_minimo if s.produto_id in prods else 0.0,
                unidade_medida=s.unidade_medida,
                deficit=round(
                    (prods[s.produto_id].estoque_minimo if s.produto_id in prods else 0.0) - s.quantidade_atual, 4
                ),
            )
            for s in saldos if s.abaixo_minimo
        ]
