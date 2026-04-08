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
            "resumo": {
                "total_operacoes": len(operacoes),
                "custo_total_operacoes": round(sum(float(op.custo_total or 0) for op in operacoes), 2),
                "total_insumos_aplicados": sum(len(op.insumos) for op in operacoes),
                "total_colhido_sacas": round(sum(float(r.sacas_60kg or 0) for r in romaneios), 2),
                "receita_total": round(sum(float(r.receita_total or 0) for r in romaneios), 2),
            },
        }


class CertificacaoService(BaseService[CertificacaoPropriedade]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(CertificacaoPropriedade, session, tenant_id)
