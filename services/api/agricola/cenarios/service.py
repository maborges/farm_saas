from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from sqlalchemy import func, select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_service import BaseService
from core.exceptions import BusinessRuleError, EntityNotFoundError

from agricola.cenarios.models import SafraCenario, SafraCenarioUnidade
from agricola.cenarios.schemas import (
    CenarioCreate,
    CenarioUpdate,
    ComparativoResponse,
    ComparativoCenarioColuna,
    DuplicarCenarioRequest,
)
from agricola.custos.models import CostAllocation
from agricola.a1_planejamento.models import ItemOrcamentoSafra
from agricola.romaneios.models import RomaneioColheita
from agricola.production_units.models import ProductionUnit
from agricola.safras.models import Safra
from agricola.cultivos.models import Cultivo
from core.measurements.models import UnidadeMedida

MAX_CENARIOS_ATIVOS = 20
_CODIGO_UOM_PADRAO = "SC60"


class CenariosService(BaseService[SafraCenario]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(SafraCenario, session, tenant_id)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    async def list_cenarios(self, safra_id: uuid.UUID) -> list[SafraCenario]:
        """Lista cenários e cria BASE automaticamente se não existir."""
        await self._get_or_create_base(safra_id)
        stmt = (
            select(SafraCenario)
            .where(
                and_(
                    SafraCenario.tenant_id == self.tenant_id,
                    SafraCenario.safra_id == safra_id,
                )
            )
            .order_by(SafraCenario.eh_base.desc(), SafraCenario.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_cenario(self, safra_id: uuid.UUID, cenario_id: uuid.UUID) -> SafraCenario:
        stmt = (
            select(SafraCenario)
            .options(selectinload(SafraCenario.unidades))
            .where(
                and_(
                    SafraCenario.id == cenario_id,
                    SafraCenario.safra_id == safra_id,
                    SafraCenario.tenant_id == self.tenant_id,
                )
            )
        )
        result = await self.session.execute(stmt)
        cenario = result.scalar_one_or_none()
        if not cenario:
            raise EntityNotFoundError("Cenário não encontrado.")
        return cenario

    async def create_cenario(self, safra_id: uuid.UUID, data: CenarioCreate) -> SafraCenario:
        await self._assert_safra_nao_cancelada(safra_id)
        await self._assert_limite_cenarios(safra_id)
        await self._assert_nome_unico(safra_id, data.nome)

        cenario = SafraCenario(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            safra_id=safra_id,
            nome=data.nome,
            descricao=data.descricao,
            tipo=data.tipo,
            eh_base=False,
            status="ATIVO",
            unidade_medida_id=data.unidade_medida_id,
            produtividade_default=data.produtividade_default,
            preco_default=data.preco_default,
            custo_ha_default=data.custo_ha_default,
            fator_custo_pct=data.fator_custo_pct,
            ir_aliquota_pct=data.ir_aliquota_pct,
        )
        cenario.unidades = []
        self.session.add(cenario)
        await self.session.flush()

        for u in data.unidades:
            await self._assert_pu_pertence_safra(u.production_unit_id, safra_id)
            linha = await self._build_linha(cenario, u.production_unit_id, u)
            self.session.add(linha)
            cenario.unidades.append(linha)
        await self.session.flush()

        await self._recalculate_all(cenario)
        return cenario

    async def update_cenario(
        self, safra_id: uuid.UUID, cenario_id: uuid.UUID, data: CenarioUpdate
    ) -> SafraCenario:
        cenario = await self.get_cenario(safra_id, cenario_id)

        if data.nome is not None and data.nome != cenario.nome:
            await self._assert_nome_unico(safra_id, data.nome, exclude_id=cenario_id)
            cenario.nome = data.nome
        if data.descricao is not None:
            cenario.descricao = data.descricao
        if data.tipo is not None and not cenario.eh_base:
            cenario.tipo = data.tipo
        if data.status is not None:
            cenario.status = data.status
        if data.unidade_medida_id is not None:
            cenario.unidade_medida_id = data.unidade_medida_id
        if data.produtividade_default is not None:
            cenario.produtividade_default = data.produtividade_default
        if data.preco_default is not None:
            cenario.preco_default = data.preco_default
        if data.custo_ha_default is not None:
            cenario.custo_ha_default = data.custo_ha_default
        if data.fator_custo_pct is not None:
            cenario.fator_custo_pct = data.fator_custo_pct
        if data.ir_aliquota_pct is not None:
            cenario.ir_aliquota_pct = data.ir_aliquota_pct

        if data.unidades is not None:
            for u in data.unidades:
                await self._assert_pu_pertence_safra(u.production_unit_id, safra_id)
                linha = await self._get_or_create_linha(cenario, u.production_unit_id)
                if u.produtividade_simulada is not None:
                    linha.produtividade_simulada = u.produtividade_simulada
                if u.preco_simulado is not None:
                    linha.preco_simulado = u.preco_simulado
                if u.custo_total_simulado_ha is not None:
                    linha.custo_total_simulado_ha = u.custo_total_simulado_ha
                if u.depreciacao_ha is not None:
                    linha.depreciacao_ha = u.depreciacao_ha
                if u.unidade_medida_id is not None:
                    linha.unidade_medida_id = u.unidade_medida_id

        await self.session.flush()
        await self._recalculate_all(cenario)
        return cenario

    async def delete_cenario(self, safra_id: uuid.UUID, cenario_id: uuid.UUID) -> None:
        cenario = await self.get_cenario(safra_id, cenario_id)
        if cenario.eh_base:
            raise BusinessRuleError("O cenário base não pode ser excluído.")
        await self.session.delete(cenario)
        await self.session.flush()

    async def duplicar(
        self, safra_id: uuid.UUID, cenario_id: uuid.UUID, data: DuplicarCenarioRequest
    ) -> SafraCenario:
        await self._assert_limite_cenarios(safra_id)
        await self._assert_nome_unico(safra_id, data.nome)

        fonte = await self.get_cenario(safra_id, cenario_id)
        novo = SafraCenario(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            safra_id=safra_id,
            nome=data.nome,
            descricao=fonte.descricao,
            tipo=fonte.tipo if not fonte.eh_base else "CUSTOM",
            eh_base=False,
            status="ATIVO",
            unidade_medida_id=fonte.unidade_medida_id,
            produtividade_default=fonte.produtividade_default,
            preco_default=fonte.preco_default,
            custo_ha_default=fonte.custo_ha_default,
            fator_custo_pct=fonte.fator_custo_pct,
        )
        novo.unidades = []
        self.session.add(novo)
        await self.session.flush()

        for linha_fonte in fonte.unidades:
            nova_linha = SafraCenarioUnidade(
                id=uuid.uuid4(),
                tenant_id=self.tenant_id,
                cenario_id=novo.id,
                production_unit_id=linha_fonte.production_unit_id,
                unidade_medida_id=linha_fonte.unidade_medida_id,
                cultivo_nome=linha_fonte.cultivo_nome,
                area_nome=linha_fonte.area_nome,
                area_ha=linha_fonte.area_ha,
                percentual_participacao=linha_fonte.percentual_participacao,
                produtividade_simulada=linha_fonte.produtividade_simulada,
                preco_simulado=linha_fonte.preco_simulado,
                custo_total_simulado_ha=linha_fonte.custo_total_simulado_ha,
                custo_base_fonte=linha_fonte.custo_base_fonte,
            )
            self.session.add(nova_linha)
            novo.unidades.append(nova_linha)
        await self.session.flush()
        await self._recalculate_all(novo)
        return novo

    async def recalcular_base(self, safra_id: uuid.UUID) -> SafraCenario:
        """Rebuild manual do cenário BASE com dados atuais."""
        base = await self._fetch_base(safra_id)
        if not base:
            return await self._get_or_create_base(safra_id)

        pus = await self._fetch_production_units(safra_id)
        uom_padrao_id = await self._fetch_uom_padrao_id()

        for pu in pus:
            linha = await self._get_or_create_linha(base, pu.id)
            cultivo_nome, area_nome = await self._fetch_snapshots(pu)
            linha.cultivo_nome = cultivo_nome
            linha.area_nome = area_nome
            linha.area_ha = float(pu.area_ha)
            linha.percentual_participacao = float(pu.percentual_participacao)

            custo_ha, fonte = await self._resolve_custo_base(pu.id, float(pu.area_ha))
            linha.custo_total_simulado_ha = custo_ha
            linha.custo_base_fonte = fonte

            prod, preco = await self._resolve_producao_base(pu.id)
            linha.produtividade_simulada = prod
            linha.preco_simulado = preco
            if linha.unidade_medida_id is None:
                linha.unidade_medida_id = uom_padrao_id

        await self.session.flush()
        await self._recalculate_all(base)
        return base

    async def get_comparativo(
        self, safra_id: uuid.UUID, cenario_ids: list[uuid.UUID]
    ) -> ComparativoResponse:
        colunas = []
        for cid in cenario_ids:
            c = await self.get_cenario(safra_id, cid)
            colunas.append(
                ComparativoCenarioColuna(
                    cenario_id=c.id,
                    nome=c.nome,
                    tipo=c.tipo,
                    eh_base=c.eh_base,
                    area_total_ha=c.area_total_ha,
                    receita_bruta_total=c.receita_bruta_total,
                    custo_total=c.custo_total,
                    margem_contribuicao_total=c.margem_contribuicao_total,
                    resultado_liquido_total=c.resultado_liquido_total,
                    ponto_equilibrio_sc_ha=c.ponto_equilibrio_sc_ha,
                    unidades=c.unidades,
                )
            )
        return ComparativoResponse(cenarios=colunas)

    # ------------------------------------------------------------------
    # Privados — criação do BASE
    # ------------------------------------------------------------------

    async def _get_or_create_base(self, safra_id: uuid.UUID) -> SafraCenario:
        base = await self._fetch_base(safra_id)
        if base:
            return base

        # Usa advisory lock para idempotência em chamadas concorrentes
        lock_key = hash(f"cenario_base:{self.tenant_id}:{safra_id}") & 0x7FFFFFFFFFFFFFFF
        await self.session.execute(
            select(func.pg_advisory_xact_lock(lock_key))
        )

        # Re-verifica após obter lock
        base = await self._fetch_base(safra_id)
        if base:
            return base

        await self._assert_safra_nao_cancelada(safra_id)
        uom_padrao_id = await self._fetch_uom_padrao_id()
        pus = await self._fetch_production_units(safra_id)

        base = SafraCenario(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            safra_id=safra_id,
            nome="Base Realizado",
            tipo="BASE",
            eh_base=True,
            status="ATIVO",
            unidade_medida_id=uom_padrao_id,
        )
        base.unidades = []
        self.session.add(base)
        await self.session.flush()

        for pu in pus:
            cultivo_nome, area_nome = await self._fetch_snapshots(pu)
            custo_ha, fonte = await self._resolve_custo_base(pu.id, float(pu.area_ha))
            prod, preco = await self._resolve_producao_base(pu.id)

            linha = SafraCenarioUnidade(
                id=uuid.uuid4(),
                tenant_id=self.tenant_id,
                cenario_id=base.id,
                production_unit_id=pu.id,
                unidade_medida_id=uom_padrao_id,
                cultivo_nome=cultivo_nome,
                area_nome=area_nome,
                area_ha=float(pu.area_ha),
                percentual_participacao=float(pu.percentual_participacao),
                produtividade_simulada=prod,
                preco_simulado=preco,
                custo_total_simulado_ha=custo_ha,
                custo_base_fonte=fonte,
            )
            self.session.add(linha)
            base.unidades.append(linha)

        await self.session.flush()
        await self._recalculate_all(base)
        return base

    # ------------------------------------------------------------------
    # Privados — resolução de dados base
    # ------------------------------------------------------------------

    async def _fetch_base(self, safra_id: uuid.UUID) -> SafraCenario | None:
        stmt = (
            select(SafraCenario)
            .options(selectinload(SafraCenario.unidades))
            .where(
                and_(
                    SafraCenario.tenant_id == self.tenant_id,
                    SafraCenario.safra_id == safra_id,
                    SafraCenario.eh_base == True,  # noqa: E712
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _fetch_production_units(self, safra_id: uuid.UUID) -> list[ProductionUnit]:
        stmt = select(ProductionUnit).where(
            and_(
                ProductionUnit.tenant_id == self.tenant_id,
                ProductionUnit.safra_id == safra_id,
                ProductionUnit.status == "ATIVA",
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _fetch_uom_padrao_id(self) -> uuid.UUID | None:
        stmt = select(UnidadeMedida.id).where(
            and_(
                UnidadeMedida.codigo == _CODIGO_UOM_PADRAO,
                UnidadeMedida.ativo == True,  # noqa: E712
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _fetch_snapshots(self, pu: ProductionUnit) -> tuple[str | None, str | None]:
        cultivo_nome: str | None = None
        area_nome: str | None = None

        stmt_c = select(Cultivo.cultura, Cultivo.cultivar_nome).where(Cultivo.id == pu.cultivo_id)
        r = await self.session.execute(stmt_c)
        res_c = r.one_or_none()
        if res_c:
            cultura, cultivar = res_c
            cultivo_nome = f"{cultura} ({cultivar})" if cultivar else cultura

        from core.cadastros.propriedades.models import AreaRural
        stmt_a = select(AreaRural.nome).where(AreaRural.id == pu.area_id)
        r = await self.session.execute(stmt_a)
        area_nome = r.scalar_one_or_none()

        return cultivo_nome, area_nome

    async def _resolve_custo_base(
        self, pu_id: uuid.UUID, area_ha: float
    ) -> tuple[float | None, str | None]:
        # 1º cost_allocations realizados
        stmt = select(func.sum(CostAllocation.amount)).where(
            and_(
                CostAllocation.tenant_id == self.tenant_id,
                CostAllocation.production_unit_id == pu_id,
            )
        )
        total = (await self.session.execute(stmt)).scalar_one_or_none()
        if total and float(total) > 0 and area_ha > 0:
            return round(float(total) / area_ha, 2), "REALIZADO"

        # 2º a1_planejamento orçado
        stmt2 = select(func.sum(ItemOrcamentoSafra.custo_total)).where(
            and_(
                ItemOrcamentoSafra.tenant_id == self.tenant_id,
                ItemOrcamentoSafra.production_unit_id == pu_id,
            )
        )
        total2 = (await self.session.execute(stmt2)).scalar_one_or_none()
        if total2 and float(total2) > 0 and area_ha > 0:
            return round(float(total2) / area_ha, 2), "ORCADO"

        # 3º manual
        return None, "MANUAL"

    async def _resolve_producao_base(
        self, pu_id: uuid.UUID
    ) -> tuple[float | None, float | None]:
        stmt = select(
            func.avg(RomaneioColheita.produtividade_sc_ha),
            func.avg(RomaneioColheita.preco_saca),
        ).where(
            and_(
                RomaneioColheita.tenant_id == self.tenant_id,
                RomaneioColheita.production_unit_id == pu_id,
                RomaneioColheita.produtividade_sc_ha.is_not(None),
            )
        )
        result = await self.session.execute(stmt)
        row = result.one()
        prod = round(float(row[0]), 3) if row[0] else None
        preco = round(float(row[1]), 4) if row[1] else None
        return prod, preco

    # ------------------------------------------------------------------
    # Privados — engine de cálculo
    # ------------------------------------------------------------------

    async def _recalculate_all(self, cenario: SafraCenario) -> None:
        now = datetime.now(timezone.utc)
        fator = float(cenario.fator_custo_pct or 1.0)
        ir_aliquota = _d(cenario.ir_aliquota_pct) or Decimal("0")

        area_total = Decimal("0")
        receita_total = Decimal("0")
        custo_total_sum = Decimal("0")
        margem_total = Decimal("0")
        depreciacao_total = Decimal("0")
        ir_total = Decimal("0")

        for linha in cenario.unidades:
            prod = _d(linha.produtividade_simulada) or _d(cenario.produtividade_default)
            preco = _d(linha.preco_simulado) or _d(cenario.preco_default)

            if linha.custo_total_simulado_ha is not None:
                custo_ha = _d(linha.custo_total_simulado_ha)
            else:
                base_custo = _d(cenario.custo_ha_default)
                custo_ha = base_custo * Decimal(str(fator)) if base_custo else None

            area = _d(linha.area_ha)
            producao = (prod * area) if prod and area else None
            receita = (producao * preco) if producao and preco else None
            custo = (custo_ha * area) if custo_ha and area else None
            margem = (receita - custo) if receita is not None and custo is not None else None
            margem_pct = (
                (margem / receita * 100).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                if margem is not None and receita and receita != 0
                else None
            )
            pe = (
                (custo_ha / preco).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
                if custo_ha and preco and preco != 0
                else None
            )

            # Depreciação por unidade (informada pelo usuário em R$/ha)
            dep_ha = _d(linha.depreciacao_ha) or Decimal("0")
            dep_total_linha = (dep_ha * area) if area else Decimal("0")

            # lucro_antes_ir = margem - depreciacao; IR só sobre lucro positivo
            lucro_antes_ir = (margem - dep_total_linha) if margem is not None else None
            ir_linha = (
                max(Decimal("0"), lucro_antes_ir) * ir_aliquota / Decimal("100")
                if lucro_antes_ir is not None and ir_aliquota
                else Decimal("0")
            )
            resultado = (lucro_antes_ir - ir_linha) if lucro_antes_ir is not None else None

            linha.produtividade_efetiva = _f(prod)
            linha.preco_efetivo = _f(preco)
            linha.custo_ha_efetivo = _f(custo_ha)
            linha.producao_total = _f(producao)
            linha.receita_bruta = _f(receita)
            linha.custo_total = _f(custo)
            linha.margem_contribuicao = _f(margem)
            linha.margem_pct = _f(margem_pct)
            linha.depreciacao_total = _f(dep_total_linha) if dep_total_linha else None
            linha.ir_valor = _f(ir_linha) if ir_linha else None
            linha.resultado_liquido = _f(resultado)
            linha.ponto_equilibrio = _f(pe)
            linha.updated_at = now

            if area:
                area_total += area
            if receita:
                receita_total += receita
            if custo:
                custo_total_sum += custo
            if margem:
                margem_total += margem
            depreciacao_total += dep_total_linha
            ir_total += ir_linha

        cenario.area_total_ha = _f(area_total) if area_total else None
        cenario.receita_bruta_total = _f(receita_total) if receita_total else None
        cenario.custo_total = _f(custo_total_sum) if custo_total_sum else None
        cenario.margem_contribuicao_total = _f(margem_total) if margem_total else None
        cenario.depreciacao_total = _f(depreciacao_total) if depreciacao_total else None
        cenario.ir_aliquota_pct = _f(ir_aliquota) if ir_aliquota else None
        cenario.ir_valor_total = _f(ir_total) if ir_total else None
        lucro_antes_ir_total = margem_total - depreciacao_total
        resultado_total = lucro_antes_ir_total - ir_total
        cenario.resultado_liquido_total = _f(resultado_total) if margem_total else None
        cenario.ponto_equilibrio_sc_ha = (
            _f(
                (custo_total_sum / (receita_total / area_total)).quantize(
                    Decimal("0.001"), rounding=ROUND_HALF_UP
                )
            )
            if area_total and receita_total and receita_total != 0
            else None
        )
        cenario.calculado_em = now
        cenario.updated_at = now

    # ------------------------------------------------------------------
    # Privados — helpers de validação
    # ------------------------------------------------------------------

    async def _assert_safra_nao_cancelada(self, safra_id: uuid.UUID) -> None:
        stmt = select(Safra.status).where(
            and_(Safra.id == safra_id, Safra.tenant_id == self.tenant_id)
        )
        status = (await self.session.execute(stmt)).scalar_one_or_none()
        if not status:
            raise EntityNotFoundError("Safra não encontrada.")
        if status == "CANCELADA":
            raise BusinessRuleError("Não é possível criar cenários para safra cancelada.")

    async def _assert_limite_cenarios(self, safra_id: uuid.UUID) -> None:
        stmt = select(func.count(SafraCenario.id)).where(
            and_(
                SafraCenario.tenant_id == self.tenant_id,
                SafraCenario.safra_id == safra_id,
                SafraCenario.status == "ATIVO",
            )
        )
        count = (await self.session.execute(stmt)).scalar_one()
        if count >= MAX_CENARIOS_ATIVOS:
            raise BusinessRuleError(
                f"Limite de {MAX_CENARIOS_ATIVOS} cenários ativos atingido. "
                "Arquive ou exclua cenários existentes."
            )

    async def _assert_nome_unico(
        self, safra_id: uuid.UUID, nome: str, exclude_id: uuid.UUID | None = None
    ) -> None:
        stmt = select(SafraCenario.id).where(
            and_(
                SafraCenario.tenant_id == self.tenant_id,
                SafraCenario.safra_id == safra_id,
                SafraCenario.nome == nome,
            )
        )
        if exclude_id:
            stmt = stmt.where(SafraCenario.id != exclude_id)
        exists = (await self.session.execute(stmt)).scalar_one_or_none()
        if exists:
            raise BusinessRuleError("Já existe um cenário com este nome nesta safra.")

    async def _assert_pu_pertence_safra(
        self, pu_id: uuid.UUID, safra_id: uuid.UUID
    ) -> None:
        stmt = select(ProductionUnit.id).where(
            and_(
                ProductionUnit.id == pu_id,
                ProductionUnit.safra_id == safra_id,
                ProductionUnit.tenant_id == self.tenant_id,
            )
        )
        exists = (await self.session.execute(stmt)).scalar_one_or_none()
        if not exists:
            raise BusinessRuleError(
                f"ProductionUnit {pu_id} não pertence a esta safra ou tenant."
            )

    async def _build_linha(
        self,
        cenario: SafraCenario,
        pu_id: uuid.UUID,
        u: Any,
    ) -> SafraCenarioUnidade:
        stmt = select(ProductionUnit).where(ProductionUnit.id == pu_id)
        pu = (await self.session.execute(stmt)).scalar_one()
        cultivo_nome, area_nome = await self._fetch_snapshots(pu)
        uom_id = u.unidade_medida_id or cenario.unidade_medida_id or await self._fetch_uom_padrao_id()
        return SafraCenarioUnidade(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            cenario_id=cenario.id,
            production_unit_id=pu_id,
            unidade_medida_id=uom_id,
            cultivo_nome=cultivo_nome,
            area_nome=area_nome,
            area_ha=float(pu.area_ha),
            percentual_participacao=float(pu.percentual_participacao),
            produtividade_simulada=u.produtividade_simulada,
            preco_simulado=u.preco_simulado,
            custo_total_simulado_ha=u.custo_total_simulado_ha,
            depreciacao_ha=getattr(u, "depreciacao_ha", None),
            custo_base_fonte=None,
        )

    async def _get_or_create_linha(
        self, cenario: SafraCenario, pu_id: uuid.UUID
    ) -> SafraCenarioUnidade:
        for linha in cenario.unidades:
            if linha.production_unit_id == pu_id:
                return linha
        stmt = select(ProductionUnit).where(ProductionUnit.id == pu_id)
        pu = (await self.session.execute(stmt)).scalar_one_or_none()
        if not pu:
            raise EntityNotFoundError(f"ProductionUnit {pu_id} não encontrada.")
        cultivo_nome, area_nome = await self._fetch_snapshots(pu)
        linha = SafraCenarioUnidade(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            cenario_id=cenario.id,
            production_unit_id=pu_id,
            cultivo_nome=cultivo_nome,
            area_nome=area_nome,
            area_ha=float(pu.area_ha),
            percentual_participacao=float(pu.percentual_participacao),
        )
        self.session.add(linha)
        cenario.unidades.append(linha)
        return linha


# ------------------------------------------------------------------
# Helpers numéricos
# ------------------------------------------------------------------

def _d(value: Any) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _f(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)
