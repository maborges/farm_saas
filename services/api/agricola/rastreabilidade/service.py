from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from core.base_service import BaseService
from core.exceptions import EntityNotFoundError
from agricola.rastreabilidade.models import LoteRastreabilidade, CertificacaoPropriedade
from agricola.rastreabilidade.schemas import LoteRastreabilidadeCreate, CertificacaoCreate


class RastreabilidadeService(BaseService[LoteRastreabilidade]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(LoteRastreabilidade, session, tenant_id)

    async def criar_lote(self, dados: LoteRastreabilidadeCreate) -> LoteRastreabilidade:
        dados_dict = dados.model_dump()
        dados_dict["qr_code_url"] = f"https://api.agrosaas.com/v1/public/track/{dados.codigo_lote}"
        return await super().create(dados_dict)

    async def cadeia_rastreabilidade(self, lote_id: UUID) -> dict:
        from agricola.safras.models import Safra
        from core.cadastros.propriedades.models import AreaRural
        from agricola.operacoes.models import OperacaoAgricola, InsumoOperacao
        from agricola.romaneios.models import RomaneioColheita
        from core.cadastros.models import ProdutoCatalogo as Produto
        from agricola.colheita.models import ProdutoColhido
        from financeiro.comercializacao.models import ComercializacaoCommodity
        from core.cadastros.commodities.models import Commodity

        lote = await self.get_or_fail(lote_id)

        # Safra
        safra = await self.session.get(Safra, lote.safra_id)
        if not safra:
            raise EntityNotFoundError(f"Safra {lote.safra_id} não encontrada.")

        # Talhão
        talhao = await self.session.get(AreaRural, lote.talhao_id)

        # Operações agrícolas no talhão/safra (com insumos via selectin)
        stmt_ops = (
            select(OperacaoAgricola)
            .where(
                OperacaoAgricola.safra_id == lote.safra_id,
                OperacaoAgricola.talhao_id == lote.talhao_id,
                OperacaoAgricola.tenant_id == self.tenant_id,
            )
            .order_by(OperacaoAgricola.data_realizada)
        )
        operacoes = list((await self.session.execute(stmt_ops)).scalars().all())

        # Busca nomes dos produtos dos insumos
        produto_ids = {i.insumo_id for op in operacoes for i in op.insumos}
        produtos: dict[UUID, Produto] = {}
        if produto_ids:
            stmt_prods = select(Produto).where(Produto.id.in_(produto_ids))
            produtos = {p.id: p for p in (await self.session.execute(stmt_prods)).scalars().all()}

        # Romaneios
        stmt_rom = (
            select(RomaneioColheita)
            .where(
                RomaneioColheita.safra_id == lote.safra_id,
                RomaneioColheita.talhao_id == lote.talhao_id,
                RomaneioColheita.tenant_id == self.tenant_id,
            )
            .order_by(RomaneioColheita.data_colheita)
        )
        romaneios = list((await self.session.execute(stmt_rom)).scalars().all())

        # ── ProdutoColhido (estoque colhido classificado) ───────────
        stmt_pc = (
            select(ProdutoColhido)
            .where(
                ProdutoColhido.safra_id == lote.safra_id,
                ProdutoColhido.talhao_id == lote.talhao_id,
                ProdutoColhido.tenant_id == self.tenant_id,
            )
            .order_by(ProdutoColhido.data_entrada)
        )
        produtos_colhidos = list((await self.session.execute(stmt_pc)).scalars().all())

        # Buscar dados das commodities
        pc_commodity_ids = {pc.commodity_id for pc in produtos_colhidos}
        commodities: dict[UUID, Commodity] = {}
        if pc_commodity_ids:
            stmt_comm = select(Commodity).where(Commodity.id.in_(pc_commodity_ids))
            commodities = {c.id: c for c in (await self.session.execute(stmt_comm)).scalars().all()}

        # ── Comercializações (vendas vinculadas aos produtos colhidos) ─
        pc_ids = [pc.id for pc in produtos_colhidos]
        comercializacoes = []
        if pc_ids:
            stmt_comm = (
                select(ComercializacaoCommodity)
                .where(ComercializacaoCommodity.produto_colhido_id.in_(pc_ids))
                .order_by(ComercializacaoCommodity.created_at)
            )
            comercializacoes = list((await self.session.execute(stmt_comm)).scalars().all())

        # Monta resposta
        return {
            "lote": {
                "id": str(lote.id),
                "codigo_lote": lote.codigo_lote,
                "produto": lote.produto,
                "variedade": lote.variedade,
                "quantidade_total": lote.quantidade_total,
                "unidade": lote.unidade,
                "status": lote.status,
                "certificacoes": lote.certificacoes,
                "qr_code_url": lote.qr_code_url,
                "data_geracao": lote.data_geracao.isoformat() if lote.data_geracao else None,
            },
            "safra": {
                "id": str(safra.id),
                "cultura": safra.cultura,
                "ano_safra": safra.ano_safra,
                "area_plantada_ha": float(safra.area_plantada_ha or 0),
                "status": safra.status,
            },
            "talhao": {
                "id": str(talhao.id) if talhao else None,
                "nome": talhao.nome if talhao else "—",
                "area_ha": float(talhao.area_hectares or talhao.area_hectares_manual or 0) if talhao else 0,
            } if talhao else None,
            "operacoes": [
                {
                    "id": str(op.id),
                    "tipo": op.tipo,
                    "subtipo": op.subtipo,
                    "descricao": op.descricao,
                    "data_realizada": op.data_realizada.isoformat(),
                    "area_aplicada_ha": float(op.area_aplicada_ha or 0),
                    "custo_total": float(op.custo_total or 0),
                    "status": op.status,
                    "insumos": [
                        {
                            "produto_nome": produtos[i.insumo_id].nome if i.insumo_id in produtos else str(i.insumo_id),
                            "unidade": i.unidade,
                            "dose_por_ha": float(i.dose_por_ha or 0),
                            "quantidade_total": float(i.quantidade_total or 0),
                            "custo_total": float(i.custo_total or 0),
                        }
                        for i in op.insumos
                    ],
                }
                for op in operacoes
            ],
            "romaneios": [
                {
                    "id": str(r.id),
                    "numero_romaneio": r.numero_romaneio,
                    "data_colheita": r.data_colheita.isoformat(),
                    "peso_bruto_kg": float(r.peso_bruto_kg or 0),
                    "peso_liquido_kg": float(r.peso_liquido_kg or 0),
                    "sacas_60kg": float(r.sacas_60kg or 0),
                    "umidade_pct": float(r.umidade_pct or 0),
                    "impureza_pct": float(r.impureza_pct or 0),
                    "destino": r.destino,
                    "receita_total": float(r.receita_total or 0),
                }
                for r in romaneios
            ],
            "produtos_colhidos": [
                {
                    "id": str(pc.id),
                    "commodity_nome": commodities[pc.commodity_id].nome if pc.commodity_id in commodities else None,
                    "commodity_codigo": commodities[pc.commodity_id].codigo if pc.commodity_id in commodities else None,
                    "quantidade": float(pc.quantidade),
                    "unidade": pc.unidade,
                    "peso_liquido_kg": float(pc.peso_liquido_kg),
                    "umidade_pct": float(pc.umidade_pct) if pc.umidade_pct else None,
                    "impureza_pct": float(pc.impureza_pct) if pc.impureza_pct else None,
                    "status": pc.status,
                    "destino": pc.destino,
                    "data_entrada": pc.data_entrada.isoformat(),
                }
                for pc in produtos_colhidos
            ],
            "comercializacoes": [
                {
                    "id": str(c.id),
                    "numero_contrato": c.numero_contrato,
                    "comprador_id": str(c.comprador_id),
                    "quantidade": float(c.quantidade),
                    "unidade": c.unidade,
                    "preco_unitario": float(c.preco_unitario),
                    "valor_total": float(c.valor_total),
                    "moeda": c.moeda,
                    "status": c.status,
                    "forma_pagamento": c.forma_pagamento,
                    "data_entrega_prevista": c.data_entrega_prevista.isoformat() if c.data_entrega_prevista else None,
                    "data_entrega_real": c.data_entrega_real.isoformat() if c.data_entrega_real else None,
                    "nf_numero": c.nf_numero,
                }
                for c in comercializacoes
            ],
            "resumo": {
                "total_operacoes": len(operacoes),
                "custo_total_operacoes": round(sum(float(op.custo_total or 0) for op in operacoes), 2),
                "total_insumos_aplicados": sum(len(op.insumos) for op in operacoes),
                "total_colhido_sacas": round(sum(float(r.sacas_60kg or 0) for r in romaneios), 2),
                "total_estoque_kg": round(sum(float(pc.peso_liquido_kg or 0) for pc in produtos_colhidos), 2),
                "total_vendido_kg": round(
                    sum(float(c.valor_total or 0) for c in comercializacoes if c.status == "FINALIZADO"), 2
                ),
                "receita_total_romaneios": round(sum(float(r.receita_total or 0) for r in romaneios), 2),
                "receita_total_comercializacoes": round(sum(float(c.valor_total or 0) for c in comercializacoes), 2),
            },
        }


class CertificacaoService(BaseService[CertificacaoPropriedade]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(CertificacaoPropriedade, session, tenant_id)
