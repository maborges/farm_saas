import uuid
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.base_service import BaseService
from core.exceptions import BusinessRuleError

from agricola.beneficiamento.models import LoteBeneficiamento
from agricola.beneficiamento.schemas import (
    LoteBeneficiamentoCreate,
    LoteBeneficiamentoUpdate,
    BeneficiamentoKPIs,
)

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
