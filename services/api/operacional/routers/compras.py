from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid
from datetime import datetime, date, timezone
from loguru import logger

from core.dependencies import get_session, get_current_tenant, get_current_user_claims, require_module
from core.exceptions import BusinessRuleError
from core.models.tenant import Tenant
from operacional.models.compras import (
    Fornecedor, PedidoCompra, ItemPedidoCompra, CotacaoFornecedor,
    RecebimentoParcial, ItemRecebimento, DevolucaoFornecedor, ItemDevolucao,
)
from operacional.schemas.compras import (
    RecebimentoCreate, RecebimentoResponse,
    DevolucaoCreate, DevolucaoStatusUpdate, DevolucaoResponse,
)
from core.cadastros.models import ProdutoCatalogo as Produto
from operacional.services.estoque_service import EstoqueService
from operacional.schemas.estoque import EntradaEstoqueRequest, LoteCreate
from operacional.models.estoque import LoteEstoque, MovimentacaoEstoque, SaldoEstoque
from pydantic import BaseModel, Field

router = APIRouter(prefix="/compras", tags=["Operacional — Compras"], dependencies=[Depends(require_module("O3_COMPRAS"))])

# --- SCHEMAS ---
class FornecedorCreate(BaseModel):
    nome_fantasia: str
    cnpj_cpf: Optional[str] = None
    condicoes_pagamento: Optional[str] = None

class FornecedorResponse(BaseModel):
    id: uuid.UUID
    nome_fantasia: str
    cnpj_cpf: Optional[str]
    condicoes_pagamento: Optional[str] = None
    class Config: from_attributes = True

class PedidoCreate(BaseModel):
    observacoes: Optional[str] = None

class PedidoResponse(BaseModel):
    id: uuid.UUID
    data_pedido: datetime
    status: str
    observacoes: Optional[str]
    class Config: from_attributes = True

class ItemPedidoCreate(BaseModel):
    produto_id: uuid.UUID
    quantidade_solicitada: float
    preco_estimado_unitario: float = 0.0

class ItemPedidoResponse(BaseModel):
    id: uuid.UUID
    produto_id: uuid.UUID
    quantidade_solicitada: float
    preco_estimado_unitario: float
    nome_produto: Optional[str] = None
    class Config: from_attributes = True

class CotacaoCreate(BaseModel):
    fornecedor_id: uuid.UUID
    valor_total: float
    prazo_entrega_dias: Optional[int] = None
    condicoes_pagamento: Optional[str] = None
    vencimento_cotacao: Optional[datetime] = None

class CotacaoResponse(BaseModel):
    id: uuid.UUID
    pedido_id: uuid.UUID
    fornecedor_id: uuid.UUID
    nome_fornecedor: Optional[str] = None
    valor_total: float
    prazo_entrega_dias: Optional[int]
    condicoes_pagamento: Optional[str]
    selecionada: bool
    class Config: from_attributes = True

# --- ENDPOINTS ---

@router.get("/fornecedores", response_model=List[FornecedorResponse])
async def list_fornecedores(
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    stmt = select(Fornecedor).where(Fornecedor.tenant_id == tenant.id)
    res = await session.execute(stmt)
    return res.scalars().all()


@router.post("/fornecedores", response_model=FornecedorResponse, status_code=status.HTTP_201_CREATED)
async def create_fornecedor(
    data: FornecedorCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    forn = Fornecedor(tenant_id=tenant.id, **data.model_dump())
    session.add(forn)
    await session.commit()
    await session.refresh(forn)
    return forn


@router.get("/pedidos", response_model=List[PedidoResponse])
async def list_pedidos(
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    stmt = select(PedidoCompra).where(PedidoCompra.tenant_id == tenant.id).order_by(PedidoCompra.data_pedido.desc())
    res = await session.execute(stmt)
    return res.scalars().all()

@router.get("/pedidos/{pedido_id}", response_model=PedidoResponse)
async def get_pedido(
    pedido_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    stmt = select(PedidoCompra).where(PedidoCompra.id == pedido_id, PedidoCompra.tenant_id == tenant.id)
    pedido = (await session.execute(stmt)).scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido

@router.post("/pedidos", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def create_pedido(
    observacoes: Optional[str] = None,
    tenant: Tenant = Depends(get_current_tenant),
    user_claims = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session)
):
    user_id = uuid.UUID(user_claims["sub"])
    novo_pedido = PedidoCompra(
        tenant_id=tenant.id,
        usuario_solicitante_id=user_id,
        observacoes=observacoes,
        status="ABERTO"
    )
    session.add(novo_pedido)
    await session.commit()
    await session.refresh(novo_pedido)
    return novo_pedido

@router.post("/pedidos/{pedido_id}/aprovar", response_model=PedidoResponse)
async def aprovar_pedido(
    pedido_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Aprova um pedido de compra, mudando status para APROVADO."""
    from sqlalchemy import select as sa_select
    result = await session.execute(
        sa_select(PedidoCompra).where(
            PedidoCompra.id == pedido_id,
            PedidoCompra.tenant_id == tenant.id,
        )
    )
    pedido = result.scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    if pedido.status not in ("ABERTO", "RASCUNHO", "PENDENTE"):
        raise HTTPException(status_code=422, detail=f"Pedido no status '{pedido.status}' não pode ser aprovado.")
    pedido.status = "APROVADO"
    session.add(pedido)
    await session.commit()
    await session.refresh(pedido)
    return pedido


@router.get("/pedidos/{pedido_id}/itens", response_model=List[ItemPedidoResponse])
async def list_itens_pedido(
    pedido_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    stmt = (
        select(ItemPedidoCompra, Produto.nome)
        .join(Produto, ItemPedidoCompra.produto_id == Produto.id)
        .join(PedidoCompra, ItemPedidoCompra.pedido_id == PedidoCompra.id)
        .where(PedidoCompra.id == pedido_id, PedidoCompra.tenant_id == tenant.id)
    )
    res = await session.execute(stmt)
    results = []
    for row in res.all():
        item = row[0]
        nome_prod = row[1]
        item_resp = ItemPedidoResponse.model_validate(item)
        item_resp.nome_produto = nome_prod
        results.append(item_resp)
    return results

@router.post("/pedidos/{pedido_id}/itens", response_model=ItemPedidoResponse)
async def add_item_pedido(
    pedido_id: uuid.UUID,
    data: ItemPedidoCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    stmt_check = select(PedidoCompra).where(PedidoCompra.id == pedido_id, PedidoCompra.tenant_id == tenant.id)
    pedido = (await session.execute(stmt_check)).scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    novo_item = ItemPedidoCompra(
        pedido_id=pedido_id,
        **data.model_dump()
    )
    session.add(novo_item)
    await session.commit()
    await session.refresh(novo_item)
    
    prod_nome = (await session.execute(select(Produto.nome).where(Produto.id == novo_item.produto_id))).scalar_one()
    resp = ItemPedidoResponse.model_validate(novo_item)
    resp.nome_produto = prod_nome
    return resp

@router.get("/pedidos/{pedido_id}/cotacoes", response_model=List[CotacaoResponse])
async def list_cotacoes(
    pedido_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    stmt = (
        select(CotacaoFornecedor, Fornecedor.nome_fantasia)
        .join(Fornecedor, CotacaoFornecedor.fornecedor_id == Fornecedor.id)
        .join(PedidoCompra, CotacaoFornecedor.pedido_id == PedidoCompra.id)
        .where(PedidoCompra.id == pedido_id, PedidoCompra.tenant_id == tenant.id)
    )
    res = await session.execute(stmt)
    results = []
    for row in res.all():
        cot = row[0]
        forn_nome = row[1]
        cot_resp = CotacaoResponse.model_validate(cot)
        cot_resp.nome_fornecedor = forn_nome
        results.append(cot_resp)
    return results

@router.post("/pedidos/{pedido_id}/cotacoes", response_model=CotacaoResponse)
async def add_cotacao(
    pedido_id: uuid.UUID,
    data: CotacaoCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    stmt_check = select(PedidoCompra).where(PedidoCompra.id == pedido_id, PedidoCompra.tenant_id == tenant.id)
    pedido = (await session.execute(stmt_check)).scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    nova_cot = CotacaoFornecedor(
        pedido_id=pedido_id,
        **data.model_dump()
    )
    session.add(nova_cot)
    
    if pedido.status == "ABERTO":
        pedido.status = "COTACAO"
        
    await session.commit()
    await session.refresh(nova_cot)
    
    forn_nome = (await session.execute(select(Fornecedor.nome_fantasia).where(Fornecedor.id == nova_cot.fornecedor_id))).scalar_one()
    resp = CotacaoResponse.model_validate(nova_cot)
    resp.nome_fornecedor = forn_nome
    return resp

class ItemRecebimentoOverride(BaseModel):
    item_id: uuid.UUID
    quantidade_recebida: float = Field(..., gt=0)
    preco_real_unitario: float = Field(..., ge=0)


class RecebimentoRequest(BaseModel):
    deposito_id: uuid.UUID
    data_recebimento: Optional[date] = None
    itens: Optional[List[ItemRecebimentoOverride]] = None  # None = usa quantidade_solicitada + preco_estimado


@router.patch("/pedidos/{pedido_id}/receber", status_code=200)
async def receber_pedido(
    pedido_id: uuid.UUID,
    data: RecebimentoRequest,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """
    Marca o pedido como RECEBIDO e lança entrada de estoque para cada item.
    O pedido deve estar em status APROVADO.
    """
    stmt = select(PedidoCompra).where(
        PedidoCompra.id == pedido_id, PedidoCompra.tenant_id == tenant.id
    )
    pedido = (await session.execute(stmt)).scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.status != "APROVADO":
        raise HTTPException(
            status_code=422,
            detail=f"Pedido deve estar em APROVADO para ser recebido. Status atual: {pedido.status}",
        )

    stmt_itens = select(ItemPedidoCompra).where(ItemPedidoCompra.pedido_id == pedido_id)
    itens = list((await session.execute(stmt_itens)).scalars().all())
    if not itens:
        raise HTTPException(status_code=422, detail="Pedido sem itens para receber")

    # Monta mapa de overrides por item_id
    overrides = {o.item_id: o for o in (data.itens or [])}

    estoque_svc = EstoqueService(session, tenant.id)
    movs = []
    for item in itens:
        ov = overrides.get(item.id)
        qtd = ov.quantidade_recebida if ov else item.quantidade_solicitada
        preco = ov.preco_real_unitario if ov else item.preco_estimado_unitario

        # Persiste o recebimento no item
        item.quantidade_recebida = qtd
        item.preco_real_unitario = preco
        session.add(item)

        # Lança entrada no estoque
        entrada = EntradaEstoqueRequest(
            deposito_id=data.deposito_id,
            produto_id=item.produto_id,
            quantidade=qtd,
            custo_unitario=preco,
            motivo=f"Recebimento pedido {pedido_id}",
            origem_id=pedido_id,
            origem_tipo="PEDIDO_COMPRA",
        )
        mov = await estoque_svc.registrar_entrada(entrada)
        movs.append(str(mov.id))

    pedido.status = "RECEBIDO"
    pedido.deposito_destino_id = data.deposito_id
    pedido.data_recebimento = data.data_recebimento or date.today()
    session.add(pedido)

    # ── Integração Financeira: Despesa de Compra ──────────────────────────
    from financeiro.models.despesa import Despesa
    from financeiro.models.plano_conta import PlanoConta
    from operacional.models.estoque import Deposito

    deposito_obj = await session.get(Deposito, data.deposito_id)
    fazenda_id_compra = deposito_obj.fazenda_id if deposito_obj else None
    valor_total_compra = sum(
        (item.preco_real_unitario or item.preco_estimado_unitario or 0.0)
        * (item.quantidade_recebida or item.quantidade_solicitada)
        for item in itens
    )

    if fazenda_id_compra and valor_total_compra > 0:
        stmt_pc = (
            select(PlanoConta.id)
            .where(
                PlanoConta.tenant_id == tenant.id,
                PlanoConta.categoria_rfb == "CUSTEIO",
                PlanoConta.natureza == "ANALITICA",
                PlanoConta.ativo == True,
            )
            .limit(1)
        )
        plano_id_compra = (await session.execute(stmt_pc)).scalar()
        if plano_id_compra:
            session.add(Despesa(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                fazenda_id=fazenda_id_compra,
                plano_conta_id=plano_id_compra,
                descricao=f"Compra — Pedido {pedido_id}",
                valor_total=round(valor_total_compra, 2),
                data_emissao=pedido.data_recebimento,
                data_vencimento=pedido.data_recebimento,
                data_pagamento=pedido.data_recebimento,
                status="PAGO",
            ))

    await session.commit()
    return {"message": "Pedido recebido com sucesso", "movimentacoes_criadas": len(movs)}


@router.get("/historico-precos")
async def historico_precos(
    produto_id: Optional[uuid.UUID] = None,
    fornecedor_id: Optional[uuid.UUID] = None,
    limit: int = 100,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Retorna histórico de preços praticados em pedidos RECEBIDOS."""
    from sqlalchemy import and_, true
    stmt = (
        select(
            ItemPedidoCompra.produto_id,
            Produto.nome.label("nome_produto"),
            ItemPedidoCompra.preco_real_unitario,
            ItemPedidoCompra.quantidade_recebida,
            PedidoCompra.data_recebimento,
            PedidoCompra.id.label("pedido_id"),
            CotacaoFornecedor.fornecedor_id.label("fornecedor_id"),
            Fornecedor.nome_fantasia.label("nome_fornecedor"),
        )
        .join(PedidoCompra, ItemPedidoCompra.pedido_id == PedidoCompra.id)
        .join(Produto, ItemPedidoCompra.produto_id == Produto.id)
        .outerjoin(
            CotacaoFornecedor,
            and_(
                CotacaoFornecedor.pedido_id == PedidoCompra.id,
                CotacaoFornecedor.selecionada == true(),
            ),
        )
        .outerjoin(Fornecedor, CotacaoFornecedor.fornecedor_id == Fornecedor.id)
        .where(
            PedidoCompra.tenant_id == tenant.id,
            PedidoCompra.status == "RECEBIDO",
            ItemPedidoCompra.preco_real_unitario.isnot(None),
        )
    )
    if produto_id:
        stmt = stmt.where(ItemPedidoCompra.produto_id == produto_id)
    if fornecedor_id:
        stmt = stmt.where(CotacaoFornecedor.fornecedor_id == fornecedor_id)
    stmt = stmt.order_by(PedidoCompra.data_recebimento.desc()).limit(limit)
    rows = (await session.execute(stmt)).all()
    return [
        {
            "produto_id": str(row.produto_id),
            "nome_produto": row.nome_produto,
            "preco_real_unitario": row.preco_real_unitario,
            "quantidade_recebida": row.quantidade_recebida,
            "data_recebimento": row.data_recebimento.isoformat() if row.data_recebimento else None,
            "pedido_id": str(row.pedido_id),
            "fornecedor_id": str(row.fornecedor_id) if row.fornecedor_id else None,
            "nome_fornecedor": row.nome_fornecedor,
        }
        for row in rows
    ]


# ── Recebimento Parcial ───────────────────────────────────────────────────────

@router.post("/pedidos/{pedido_id}/recebimentos", response_model=RecebimentoResponse, status_code=201)
async def registrar_recebimento_parcial(
    pedido_id: uuid.UUID,
    data: RecebimentoCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
    user_claims=Depends(get_current_user_claims),
):
    """Registra um recebimento parcial ou total de um pedido aprovado."""
    pedido = (await session.execute(
        select(PedidoCompra).where(PedidoCompra.id == pedido_id, PedidoCompra.tenant_id == tenant.id)
    )).scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.status not in ("APROVADO", "EM_RECEBIMENTO"):
        raise HTTPException(status_code=422, detail=f"Pedido no status '{pedido.status}' não pode receber mercadorias.")

    recebimento = RecebimentoParcial(
        pedido_id=pedido_id,
        numero_nf=data.numero_nf,
        chave_nfe=data.chave_nfe,
        recebido_por_id=uuid.UUID(user_claims["sub"]),
        observacoes=data.observacoes,
    )
    session.add(recebimento)
    await session.flush()

    # Busca depósito destino do pedido para entrada de estoque
    deposito_id = pedido.deposito_destino_id
    estoque_svc = EstoqueService(session, tenant.id)

    itens_map = {
        i.id: i for i in (await session.execute(
            select(ItemPedidoCompra).where(ItemPedidoCompra.pedido_id == pedido_id)
        )).scalars().all()
    }

    for item_data in data.itens:
        item = itens_map.get(item_data.item_pedido_id)
        if not item:
            raise HTTPException(status_code=422, detail=f"Item {item_data.item_pedido_id} não pertence a este pedido.")

        rec_item = ItemRecebimento(
            recebimento_id=recebimento.id,
            item_pedido_id=item.id,
            quantidade_recebida=item_data.quantidade_recebida,
            preco_real_unitario=item_data.preco_real_unitario,
            numero_lote_fornecedor=item_data.numero_lote_fornecedor,  # P0.2: Supplier batch number
            lote_id=item_data.lote_id,
        )
        session.add(rec_item)

        # Atualiza item do pedido
        item.quantidade_recebida = (item.quantidade_recebida or 0) + item_data.quantidade_recebida
        item.preco_real_unitario = item_data.preco_real_unitario
        if item.quantidade_recebida >= item.quantidade_solicitada:
            item.status_item = "COMPLETO"
        else:
            item.status_item = "PARCIAL"

        # P0.1: Create LoteEstoque on receipt (links purchase to inventory batch)
        lote_id_criado = None
        if deposito_id:
            try:
                # P0.2: Create batch with composite numero_lote: "{invoice}:{supplier_batch}"
                numero_base = data.numero_nf if data.numero_nf else f"RECEBIMENTO-{recebimento.id}"
                if item_data.numero_lote_fornecedor:
                    numero_lote = f"{numero_base}:{item_data.numero_lote_fornecedor}"
                else:
                    numero_lote = numero_base

                lote = await estoque_svc.criar_lote(LoteCreate(
                    produto_id=item.produto_id,
                    deposito_id=deposito_id,
                    numero_lote=numero_lote,
                    data_fabricacao=data.data_recebimento or date.today(),
                    data_validade=None,  # Could be populated if supplier provides it
                    quantidade_inicial=item_data.quantidade_recebida,
                    custo_unitario=item_data.preco_real_unitario or 0.0,
                    nota_fiscal_ref=data.numero_nf,
                ))
                lote_id_criado = lote.id
                rec_item.lote_id = lote_id_criado

                logger.info(
                    f"LoteEstoque created on receipt",
                    lote_id=str(lote_id_criado),
                    numero_lote=numero_lote,
                    produto_id=str(item.produto_id),
                    quantidade=item_data.quantidade_recebida,
                    custo_unitario=item_data.preco_real_unitario,
                )
            except Exception as e:
                logger.error(
                    f"Failed to create LoteEstoque on receipt",
                    error=str(e),
                    pedido_id=str(pedido_id),
                    item_id=str(item.id),
                )
                raise HTTPException(status_code=422, detail=f"Erro ao criar lote no estoque: {str(e)}")

        # Entrada no estoque (se houver depósito destino)
        if deposito_id:
            await estoque_svc.registrar_entrada(EntradaEstoqueRequest(
                deposito_id=deposito_id,
                produto_id=item.produto_id,
                quantidade=item_data.quantidade_recebida,
                custo_unitario=item_data.preco_real_unitario,
                motivo=f"Recebimento parcial — Pedido {pedido_id}",
                origem_id=pedido_id,
                origem_tipo="PEDIDO_COMPRA",
                lote_id=lote_id_criado or item_data.lote_id,  # Use newly created lote
            ))

    # Atualiza status do pedido
    todos_itens = list(itens_map.values())
    if all(i.status_item == "COMPLETO" for i in todos_itens):
        pedido.status = "RECEBIDO"
        pedido.data_recebimento = date.today()
    else:
        pedido.status = "EM_RECEBIMENTO"

    await session.commit()
    await session.refresh(recebimento)
    # Carrega itens para resposta
    recebimento_itens = (await session.execute(
        select(ItemRecebimento).where(ItemRecebimento.recebimento_id == recebimento.id)
    )).scalars().all()
    resp = RecebimentoResponse.model_validate(recebimento)
    resp.itens = [RecebimentoResponse.model_fields["itens"].annotation.__args__[0].model_validate(i) for i in recebimento_itens]
    return resp


@router.get("/pedidos/{pedido_id}/recebimentos", response_model=List[RecebimentoResponse])
async def listar_recebimentos(
    pedido_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    pedido = (await session.execute(
        select(PedidoCompra).where(PedidoCompra.id == pedido_id, PedidoCompra.tenant_id == tenant.id)
    )).scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    recs = (await session.execute(
        select(RecebimentoParcial).where(RecebimentoParcial.pedido_id == pedido_id)
        .order_by(RecebimentoParcial.data_recebimento.asc())
    )).scalars().all()
    return recs


@router.post("/pedidos/{pedido_id}/fechar-parcialmente", status_code=200)
async def fechar_pedido_parcialmente(
    pedido_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    """Encerra pedido com itens ainda pendentes (aceita entrega incompleta)."""
    pedido = (await session.execute(
        select(PedidoCompra).where(PedidoCompra.id == pedido_id, PedidoCompra.tenant_id == tenant.id)
    )).scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.status != "EM_RECEBIMENTO":
        raise HTTPException(status_code=422, detail="Apenas pedidos EM_RECEBIMENTO podem ser fechados parcialmente.")
    pedido.status = "RECEBIDO_PARCIAL"
    pedido.data_recebimento = date.today()
    await session.commit()
    return {"message": "Pedido fechado com recebimento parcial."}


# ── Devolução ao Fornecedor ────────────────────────────────────────────────────

@router.post("/devolucoes", response_model=DevolucaoResponse, status_code=201)
async def criar_devolucao(
    data: DevolucaoCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    dev = DevolucaoFornecedor(
        tenant_id=tenant.id,
        fornecedor_id=data.fornecedor_id,
        pedido_id=data.pedido_id,
        motivo=data.motivo,
        observacoes=data.observacoes,
        status="ABERTA",
    )
    session.add(dev)
    await session.flush()

    estoque_svc = EstoqueService(session, tenant.id)
    for item_data in data.itens:
        item_dev = ItemDevolucao(
            devolucao_id=dev.id,
            produto_id=item_data.produto_id,
            deposito_origem_id=item_data.deposito_origem_id,
            quantidade=item_data.quantidade,
            custo_unitario=item_data.custo_unitario,
            lote_id=item_data.lote_id,
        )
        session.add(item_dev)
        # Baixa de estoque imediata
        from operacional.schemas.estoque import SaidaEstoqueRequest
        await estoque_svc.registrar_saida(SaidaEstoqueRequest(
            deposito_id=item_data.deposito_origem_id,
            produto_id=item_data.produto_id,
            quantidade=item_data.quantidade,
            motivo=f"Devolução ao fornecedor — {data.motivo}",
            origem_id=dev.id,
            origem_tipo="DEVOLUCAO_FORNECEDOR",
            lote_id=item_data.lote_id,
        ))

    await session.commit()
    await session.refresh(dev)
    return dev


@router.get("/devolucoes", response_model=List[DevolucaoResponse])
async def listar_devolucoes(
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    devs = (await session.execute(
        select(DevolucaoFornecedor).where(DevolucaoFornecedor.tenant_id == tenant.id)
        .order_by(DevolucaoFornecedor.data_devolucao.desc())
    )).scalars().all()
    return devs


@router.get("/devolucoes/{dev_id}", response_model=DevolucaoResponse)
async def obter_devolucao(
    dev_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    dev = (await session.execute(
        select(DevolucaoFornecedor).where(DevolucaoFornecedor.id == dev_id, DevolucaoFornecedor.tenant_id == tenant.id)
    )).scalar_one_or_none()
    if not dev:
        raise HTTPException(status_code=404, detail="Devolução não encontrada")
    return dev


@router.patch("/devolucoes/{dev_id}/status", response_model=DevolucaoResponse)
async def atualizar_status_devolucao(
    dev_id: uuid.UUID,
    data: DevolucaoStatusUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
):
    dev = (await session.execute(
        select(DevolucaoFornecedor).where(DevolucaoFornecedor.id == dev_id, DevolucaoFornecedor.tenant_id == tenant.id)
    )).scalar_one_or_none()
    if not dev:
        raise HTTPException(status_code=404, detail="Devolução não encontrada")

    # P0.3: When devolução becomes CONCLUIDA, reverse FIFO effects
    if data.status == "CONCLUIDA" and dev.status != "CONCLUIDA":
        try:
            # Get all items being returned
            itens_dev = (await session.execute(
                select(ItemDevolucao).where(ItemDevolucao.devolucao_id == dev_id)
            )).scalars().all()

            for item_dev in itens_dev:
                if not item_dev.lote_id:
                    continue  # Skip items without explicit batch link

                # Find the batch being returned
                lote = await session.get(LoteEstoque, item_dev.lote_id)
                if not lote:
                    continue

                # Restore quantity to batch
                lote.quantidade_atual += item_dev.quantidade

                # Reactivate if was exhausted
                if lote.status == "ESGOTADO" and lote.quantidade_atual > 0:
                    lote.status = "ATIVO"

                session.add(lote)

                # Create reverse MovimentacaoEstoque (SAIDA_REVERSA)
                mov_reversa = MovimentacaoEstoque(
                    id=uuid.uuid4(),
                    deposito_id=item_dev.deposito_origem_id,
                    produto_id=item_dev.produto_id,
                    usuario_id=None,
                    lote_id=item_dev.lote_id,
                    tipo="SAIDA_REVERSA",
                    quantidade=item_dev.quantidade,
                    data_movimentacao=datetime.now(timezone.utc),
                    custo_unitario=item_dev.custo_unitario,
                    custo_total=item_dev.quantidade * item_dev.custo_unitario if item_dev.custo_unitario else 0.0,
                    motivo=f"Devolução aprovada ({dev.motivo})",
                    origem_id=dev.id,
                    origem_tipo="DEVOLUCAO_FORNECEDOR",
                )
                session.add(mov_reversa)

                # Update SaldoEstoque
                saldo_stmt = select(SaldoEstoque).where(
                    SaldoEstoque.deposito_id == item_dev.deposito_origem_id,
                    SaldoEstoque.produto_id == item_dev.produto_id,
                )
                saldo = (await session.execute(saldo_stmt)).scalar_one_or_none()
                if saldo:
                    saldo.quantidade_atual += item_dev.quantidade
                    saldo.ultima_atualizacao = datetime.now(timezone.utc)
                    session.add(saldo)

                logger.info(
                    f"Batch inventory restored via devolução reversal",
                    lote_id=str(item_dev.lote_id),
                    deposito_id=str(item_dev.deposito_origem_id),
                    quantidade_restaurada=item_dev.quantidade,
                    devolucao_id=str(dev.id),
                )

        except Exception as e:
            logger.error(f"P0.3 Devolução reversal failed: {e}", devolucao_id=str(dev_id))
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao processar devolução: {str(e)}")

    dev.status = data.status
    if data.numero_nf_devolucao:
        dev.numero_nf_devolucao = data.numero_nf_devolucao
    await session.commit()
    await session.refresh(dev)
    return dev


@router.post("/cotacoes/{cotacao_id}/selecionar")
async def select_cotacao(
    cotacao_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    stmt = (
        select(CotacaoFornecedor, PedidoCompra)
        .join(PedidoCompra, CotacaoFornecedor.pedido_id == PedidoCompra.id)
        .where(CotacaoFornecedor.id == cotacao_id, PedidoCompra.tenant_id == tenant.id)
    )
    res = (await session.execute(stmt)).first()
    if not res:
        raise HTTPException(status_code=404, detail="Cotação não encontrada")
    
    cotacao, pedido = res
    
    from sqlalchemy import update
    await session.execute(
        update(CotacaoFornecedor)
        .where(CotacaoFornecedor.pedido_id == pedido.id)
        .values(selecionada=False)
    )
    
    cotacao.selecionada = True
    pedido.status = "APROVADO"
    
    await session.commit()
    return {"message": "Cotação selecionada com sucesso e pedido aprovado"}
