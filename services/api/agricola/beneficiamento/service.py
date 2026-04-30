import uuid
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.base_service import BaseService
from core.exceptions import BusinessRuleError, EntityNotFoundError

from agricola.beneficiamento.models import LoteBeneficiamento
from agricola.beneficiamento.schemas import (
    LoteBeneficiamentoCreate,
    LoteBeneficiamentoUpdate,
    BeneficiamentoKPIs,
    RendimentoPorMetodo,
    BeneficiamentoRelatorioRendimento,
    LoteFromRomaneiosRequest,
)
from agricola.beneficiamento.models import LoteBeneficiamentoRomaneio
from agricola.romaneios.models import RomaneioColheita
from agricola.safras.models import Safra

# Fatores de redução esperados por método (referência para cálculo de perda)
FATOR_ESPERADO = {
    "NATURAL":    4.8,  # cereja seca com casca
    "LAVADO":     5.5,  # cereja despolpada+lavada
    "HONEY":      4.5,  # cereja despolpada s/ lavagem
    "DESCASCADO": 4.2,  # coco (já sem casca externa)
}


class BeneficiamentoService(BaseService[LoteBeneficiamento]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(LoteBeneficiamento, session, tenant_id)

    async def criar(self, dados: LoteBeneficiamentoCreate) -> LoteBeneficiamento:
        d = dados.model_dump()
        lote = await super().create(d)
        return lote

    async def atualizar(self, lote_id: UUID, dados: LoteBeneficiamentoUpdate) -> LoteBeneficiamento:
        patch = dados.model_dump(exclude_unset=True)

        # Recalcula campos derivados quando peso de saída é informado
        if "peso_saida_kg" in patch and patch["peso_saida_kg"]:
            lote = await self.get_or_fail(lote_id)
            peso_entrada = float(lote.peso_entrada_kg)
            peso_saida = float(patch["peso_saida_kg"])

            if peso_saida <= 0:
                raise BusinessRuleError("Peso de saída deve ser maior que zero.")
            if peso_saida > peso_entrada:
                raise BusinessRuleError("Peso de saída não pode ser maior que o peso de entrada.")

            # Fator de redução real
            fator_real = round(peso_entrada / peso_saida, 3)
            patch["fator_reducao"] = fator_real

            # Sacas de 60 kg beneficiadas
            patch["sacas_beneficiadas"] = round(peso_saida / 60.0, 3)

            # % de perda vs. fator esperado para o método
            fator_esp = FATOR_ESPERADO.get(lote.metodo, 4.8)
            peso_esperado = peso_entrada / fator_esp
            perda_pct = round((peso_esperado - peso_saida) / peso_esperado * 100, 2)
            patch["perda_pct"] = perda_pct

        # Calcula dias de secagem
        if "data_fim_secagem" in patch and patch["data_fim_secagem"]:
            lote = await self.get_or_fail(lote_id)
            inicio = patch.get("data_inicio_secagem") or lote.data_inicio_secagem
            if inicio:
                delta = (patch["data_fim_secagem"] - inicio).days
                patch["dias_secagem"] = max(0, delta)

        updated = await self.update(lote_id, patch)
        return updated

    async def kpis_safra(self, safra_id: UUID) -> BeneficiamentoKPIs:
        stmt = select(
            func.count(LoteBeneficiamento.id),
            func.coalesce(func.sum(LoteBeneficiamento.peso_entrada_kg), 0),
            func.coalesce(func.sum(LoteBeneficiamento.peso_saida_kg), 0),
            func.coalesce(func.sum(LoteBeneficiamento.sacas_beneficiadas), 0),
            func.avg(LoteBeneficiamento.fator_reducao),
            func.avg(LoteBeneficiamento.pontuacao_scaa),
        ).where(
            LoteBeneficiamento.tenant_id == self.tenant_id,
            LoteBeneficiamento.safra_id == safra_id,
        )
        row = (await self.session.execute(stmt)).first()

        stmt_proc = select(func.count(LoteBeneficiamento.id)).where(
            LoteBeneficiamento.tenant_id == self.tenant_id,
            LoteBeneficiamento.safra_id == safra_id,
            LoteBeneficiamento.status.in_(["RECEBIMENTO", "SECAGEM", "CLASSIFICACAO"]),
        )
        em_processo = (await self.session.execute(stmt_proc)).scalar() or 0

        stmt_conc = select(func.count(LoteBeneficiamento.id)).where(
            LoteBeneficiamento.tenant_id == self.tenant_id,
            LoteBeneficiamento.safra_id == safra_id,
            LoteBeneficiamento.status.in_(["ARMAZENADO", "VENDIDO"]),
        )
        concluidos = (await self.session.execute(stmt_conc)).scalar() or 0

        return BeneficiamentoKPIs(
            total_lotes=row[0],
            peso_entrada_total_kg=float(row[1]),
            peso_saida_total_kg=float(row[2]),
            sacas_beneficiadas_total=float(row[3]),
            fator_reducao_medio=float(row[4]) if row[4] else None,
            lotes_em_processo=em_processo,
            lotes_concluidos=concluidos,
            pontuacao_media_scaa=float(row[5]) if row[5] else None,
        )

    async def criar_from_romaneio(self, romaneio_id: UUID) -> LoteBeneficiamento:
        """Cria um LoteBeneficiamento pré-populado a partir de um Romaneio."""
        # Busca o romaneio
        stmt = select(RomaneioColheita).where(
            RomaneioColheita.id == romaneio_id,
            RomaneioColheita.tenant_id == self.tenant_id,
        )
        romaneio = (await self.session.execute(stmt)).scalars().first()
        if not romaneio:
            raise EntityNotFoundError(f"Romaneio {romaneio_id} não encontrado.")

        # Cria número de lote automático (timestamp + parte do romaneio)
        numero_lote = f"BEN-{romaneio.numero_romaneio}" if romaneio.numero_romaneio else f"BEN-{uuid.uuid4().hex[:8]}"

        # Cria dados do lote pré-populados do romaneio
        dados = LoteBeneficiamentoCreate(
            safra_id=romaneio.safra_id,
            talhao_id=romaneio.talhao_id,
            production_unit_id=romaneio.production_unit_id,
            romaneio_id=romaneio_id,
            numero_lote=numero_lote,
            metodo="NATURAL",  # Padrão: NATURAL (cereja), usuário pode alterar depois
            data_entrada=romaneio.data_colheita,
            peso_entrada_kg=float(romaneio.peso_liquido_kg or romaneio.peso_liquido_padrao_kg or 0),
            umidade_entrada_pct=float(romaneio.umidade_pct) if romaneio.umidade_pct else None,
        )

        lote = await self.criar(dados)
        return lote

    async def criar_from_romaneios(self, req: LoteFromRomaneiosRequest) -> LoteBeneficiamento:
        """Cria um LoteBeneficiamento agrupando múltiplos romaneios (blend)."""
        # Busca todos os romaneios
        stmt = select(RomaneioColheita).where(
            RomaneioColheita.id.in_(req.romaneio_ids),
            RomaneioColheita.tenant_id == self.tenant_id,
        )
        romaneios = (await self.session.execute(stmt)).scalars().all()

        if not romaneios or len(romaneios) != len(req.romaneio_ids):
            raise EntityNotFoundError("Um ou mais romaneios não encontrados.")

        # Valida que todos são da mesma safra
        safra_ids = set(r.safra_id for r in romaneios)
        if len(safra_ids) > 1:
            raise BusinessRuleError("Todos os romaneios devem ser da mesma safra.")

        safra_id = safra_ids.pop()

        # Soma peso de entrada
        peso_total = sum(float(r.peso_liquido_kg or r.peso_liquido_padrao_kg or 0) for r in romaneios)

        # Gera número de lote
        numero_lote = req.numero_lote or f"BEN-MULTI-{uuid.uuid4().hex[:6]}"

        # Usa o primeiro romaneio como referência (talhao, data)
        primeiro = romaneios[0]

        # Cria lote
        dados = LoteBeneficiamentoCreate(
            safra_id=safra_id,
            talhao_id=primeiro.talhao_id,
            production_unit_id=primeiro.production_unit_id,
            romaneio_id=primeiro.id,  # Registra primeiro romaneio como principal
            numero_lote=numero_lote,
            metodo=req.metodo,
            data_entrada=primeiro.data_colheita,
            peso_entrada_kg=peso_total,
            umidade_entrada_pct=float(primeiro.umidade_pct) if primeiro.umidade_pct else None,
        )

        lote = await self.criar(dados)

        # Cria registros N:N para cada romaneio
        for romaneio in romaneios:
            peso = float(romaneio.peso_liquido_kg or romaneio.peso_liquido_padrao_kg or 0)
            nm = LoteBeneficiamentoRomaneio(
                tenant_id=self.tenant_id,
                lote_id=lote.id,
                romaneio_id=romaneio.id,
                peso_entrada_kg=peso,
            )
            self.session.add(nm)

        await self.session.commit()
        await self.session.refresh(lote)
        return lote

    async def gerar_venda(self, lote_id: UUID) -> dict:
        """
        Gera uma Comercializacao (venda) a partir de um lote ARMAZENADO.
        Retorna dict com id e info da comercialização criada.
        """
        lote = await self.get_or_fail(lote_id)

        # Valida status
        if lote.status != "ARMAZENADO":
            raise BusinessRuleError(
                f"Apenas lotes com status ARMAZENADO podem gerar venda. Status atual: {lote.status}"
            )

        # Busca safra para obter commodity_id
        stmt_safra = select(Safra).where(
            Safra.id == lote.safra_id,
            Safra.tenant_id == self.tenant_id,
        )
        safra = (await self.session.execute(stmt_safra)).scalars().first()
        if not safra or not safra.commodity_id:
            raise BusinessRuleError(
                "Safra deve ter commodity associada para gerar venda."
            )

        # Importa ComercializacaoService dinamicamente para evitar circular imports
        from financeiro.comercializacao.service import ComercializacaoService
        from financeiro.comercializacao.schemas import ComercializacaoCommodityCreate

        # Cria dados da comercialização
        dados_venda = ComercializacaoCommodityCreate(
            commodity_id=safra.commodity_id,
            comprador_id=None,  # Será preenchido depois
            quantidade=float(lote.sacas_beneficiadas or 0),
            unidade="SC60",  # 60kg padrão
            status="RASCUNHO",
            dados_extras={
                "lote_beneficiamento_id": str(lote.id),
                "origem": "beneficiamento_auto",
            }
        )

        # Cria comercialização
        com_svc = ComercializacaoService(self.session, self.tenant_id)
        comercializacao = await com_svc.criar(dados_venda)
        await self.session.commit()
        await self.session.refresh(comercializacao)

        return {
            "id": str(comercializacao.id),
            "numero_contrato": comercializacao.numero_contrato,
            "quantidade": float(comercializacao.quantidade),
            "status": comercializacao.status,
        }

    async def relatorio_rendimento(self, safra_id: UUID) -> BeneficiamentoRelatorioRendimento:
        """Gera relatório de rendimento por método de beneficiamento."""
        # Query todos os lotes com saída
        stmt = select(
            LoteBeneficiamento.metodo,
            func.count(LoteBeneficiamento.id).label("total_lotes"),
            func.coalesce(func.sum(LoteBeneficiamento.peso_entrada_kg), 0),
            func.coalesce(func.sum(LoteBeneficiamento.peso_saida_kg), 0),
            func.coalesce(func.sum(LoteBeneficiamento.sacas_beneficiadas), 0),
            func.avg(LoteBeneficiamento.fator_reducao),
            func.coalesce(func.sum(LoteBeneficiamento.perda_secagem_kg), 0),
            func.coalesce(func.sum(LoteBeneficiamento.perda_quebra_kg), 0),
            func.coalesce(func.sum(LoteBeneficiamento.perda_defeito_kg), 0),
        ).where(
            LoteBeneficiamento.tenant_id == self.tenant_id,
            LoteBeneficiamento.safra_id == safra_id,
            LoteBeneficiamento.peso_saida_kg > 0,
        ).group_by(LoteBeneficiamento.metodo)

        rows = (await self.session.execute(stmt)).all()

        por_metodo = []
        total_peso_entrada = 0.0
        total_peso_saida = 0.0
        total_sacas = 0.0

        for row in rows:
            metodo = row[0]
            total_lotes = row[1]
            peso_entrada = float(row[2] or 0)
            peso_saida = float(row[3] or 0)
            sacas = float(row[4] or 0)
            fator_real = float(row[5]) if row[5] else None
            perda_secagem = float(row[6] or 0)
            perda_quebra = float(row[7] or 0)
            perda_defeito = float(row[8] or 0)

            fator_esperado = FATOR_ESPERADO.get(metodo, 4.8)

            # Eficiência: (fator_esperado / fator_real) * 100
            eficiencia_pct = 0.0
            if fator_real and fator_real > 0:
                eficiencia_pct = round((fator_esperado / fator_real) * 100, 2)

            perda_total = perda_secagem + perda_quebra + perda_defeito

            por_metodo.append(RendimentoPorMetodo(
                metodo=metodo,
                total_lotes=total_lotes,
                peso_entrada_kg=round(peso_entrada, 3),
                peso_saida_kg=round(peso_saida, 3),
                sacas_beneficiadas=round(sacas, 3),
                fator_reducao_real=round(fator_real, 3) if fator_real else None,
                fator_reducao_esperado=fator_esperado,
                eficiencia_pct=eficiencia_pct,
                perda_secagem_kg=round(perda_secagem, 3),
                perda_quebra_kg=round(perda_quebra, 3),
                perda_defeito_kg=round(perda_defeito, 3),
                perda_total_kg=round(perda_total, 3),
            ))

            total_peso_entrada += peso_entrada
            total_peso_saida += peso_saida
            total_sacas += sacas

        # Rendimento médio geral
        rendimento_medio_pct = 0.0
        if total_peso_entrada > 0 and total_peso_saida > 0:
            rendimento_medio_pct = round((total_peso_saida / total_peso_entrada) * 100, 2)

        return BeneficiamentoRelatorioRendimento(
            safra_id=safra_id,
            total_lotes=sum(m.total_lotes for m in por_metodo),
            peso_entrada_total_kg=round(total_peso_entrada, 3),
            peso_saida_total_kg=round(total_peso_saida, 3),
            sacas_total=round(total_sacas, 3),
            rendimento_medio_pct=rendimento_medio_pct,
            por_metodo=por_metodo,
        )

    async def armazenar_no_estoque(self, lote_id: UUID) -> dict:
        """
        Cria um LoteEstoque a partir de um lote beneficiado ARMAZENADO.
        Integração com o módulo de estoque.
        """
        lote = await self.get_or_fail(lote_id)

        # Validações
        if lote.status != "ARMAZENADO":
            raise BusinessRuleError(
                f"Apenas lotes ARMAZENADO podem ser armazenados. Status atual: {lote.status}"
            )
        if not lote.sacas_beneficiadas or lote.sacas_beneficiadas <= 0:
            raise BusinessRuleError("Lote deve ter sacas_beneficiadas > 0")
        if not lote.armazem_id:
            raise BusinessRuleError("Lote deve ter armazem_id preenchido")

        # Busca safra para commodity
        stmt_safra = select(Safra).where(
            Safra.id == lote.safra_id,
            Safra.tenant_id == self.tenant_id,
        )
        safra = (await self.session.execute(stmt_safra)).scalars().first()
        if not safra or not safra.commodity_id:
            raise BusinessRuleError("Safra deve ter commodity associada")

        # Importa EstoqueService dinamicamente
        from operacional.estoque.service import EstoqueService

        # Cria LoteEstoque
        estoque_svc = EstoqueService(self.session, self.tenant_id)
        lote_estoque = await estoque_svc.criar_lote(
            produto_id=safra.commodity_id,
            numero_lote=lote.numero_lote,
            deposito_id=lote.armazem_id,
            quantidade=float(lote.sacas_beneficiadas),
            lote_beneficiamento_id=lote.id,
        )

        # Registra movimento no ledger canônico de estoque
        await estoque_svc.registrar_movimentacao(
            tipo="ENTRADA",
            origem_tipo="BENEFICIAMENTO",
            origem_id=str(lote.id),
            produto_id=safra.commodity_id,
            quantidade=float(lote.sacas_beneficiadas),
            deposito_id=lote.armazem_id,
            lote_id=lote_estoque.id,
        )

        # Atualiza lote com referência ao estoque
        lote.lote_estoque_id = lote_estoque.id
        await self.session.commit()
        await self.session.refresh(lote)

        return {
            "lote_estoque_id": str(lote_estoque.id),
            "quantidade": float(lote.sacas_beneficiadas),
            "deposito_id": str(lote.armazem_id),
        }
