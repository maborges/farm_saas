import uuid
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.exceptions import BusinessRuleError
from core.base_service import BaseService

from sqlalchemy import func
from agricola.romaneios.models import RomaneioColheita
from agricola.romaneios.schemas import RomaneioColheitaCreate, RomaneioColheitaUpdate, RomaneioKPIs

class RomaneioService(BaseService[RomaneioColheita]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(RomaneioColheita, session, tenant_id)

    # Parâmetros de qualidade por cultura (umidade padrão MAPA, impureza padrão, saca kg)
    _PARAMS_CULTURA = {
        "Café":    {"umidade_padrao": 12.0, "impureza_padrao": 1.0, "saca_kg": 60.0},
        "Soja":    {"umidade_padrao": 14.0, "impureza_padrao": 1.0, "saca_kg": 60.0},
        "Milho":   {"umidade_padrao": 14.0, "impureza_padrao": 1.0, "saca_kg": 60.0},
        "Trigo":   {"umidade_padrao": 13.0, "impureza_padrao": 1.0, "saca_kg": 60.0},
        "Algodão": {"umidade_padrao": 8.0,  "impureza_padrao": 3.0, "saca_kg": 15.0},
        "Arroz":   {"umidade_padrao": 13.0, "impureza_padrao": 1.0, "saca_kg": 50.0},
        "Feijão":  {"umidade_padrao": 13.0, "impureza_padrao": 1.0, "saca_kg": 60.0},
    }
    _PARAMS_DEFAULT = {"umidade_padrao": 14.0, "impureza_padrao": 1.0, "saca_kg": 60.0}

    def _params_para_cultura(self, cultura: str | None) -> dict:
        if not cultura:
            return self._PARAMS_DEFAULT
        # match case-insensitive por prefixo
        for key, params in self._PARAMS_CULTURA.items():
            if cultura.lower().startswith(key.lower()):
                return params
        return self._PARAMS_DEFAULT

    async def _params_da_safra(self, safra_obj) -> dict:
        """Busca parâmetros de qualidade do Commodity vinculado à safra.
        Se não houver commodity vinculado, usa o dict hardcoded por cultura (fallback).
        """
        if safra_obj and safra_obj.commodity_id:
            from core.cadastros.commodities.models import Commodity
            commodity = await self.session.get(Commodity, safra_obj.commodity_id)
            if commodity:
                return {
                    "umidade_padrao": float(commodity.umidade_padrao_pct or self._PARAMS_DEFAULT["umidade_padrao"]),
                    "impureza_padrao": float(commodity.impureza_padrao_pct or self._PARAMS_DEFAULT["impureza_padrao"]),
                    "saca_kg": float(commodity.fator_conversao_kg or 60.0),
                }
        # fallback: dict por nome de cultura
        return self._params_para_cultura(safra_obj.cultura if safra_obj else None)

    def _calcular_peso_padrao(
        self,
        peso_liquido: float,
        umidade_entrada: float | None,
        impureza_entrada: float | None,
        params: dict,
    ) -> tuple[float, float, float, float]:
        """
        Retorna (desc_umidade_kg, desc_impureza_kg, peso_padrao_kg, sacas).

        Fórmula padrão MAPA (aplicável a todas as culturas):
            peso_seco = peso_liquido × (100 - umidade_entrada) / (100 - umidade_padrao)
        Em seguida desconta impureza acima do padrão:
            peso_padrao = peso_seco × (100 - impureza_entrada) / (100 - impureza_padrao)
        """
        u_entrada = umidade_entrada if umidade_entrada is not None else params["umidade_padrao"]
        i_entrada = impureza_entrada if impureza_entrada is not None else params["impureza_padrao"]
        u_padrao = params["umidade_padrao"]
        i_padrao = params["impureza_padrao"]
        saca_kg = params["saca_kg"]

        # Corrige umidade (fórmula MAPA — válida para qualquer faixa, inclusive café cereja)
        if u_entrada > u_padrao:
            peso_seco = peso_liquido * (100.0 - u_entrada) / (100.0 - u_padrao)
        else:
            peso_seco = peso_liquido  # não há bonificação por umidade abaixo do padrão
        desc_umidade = peso_liquido - peso_seco

        # Corrige impureza
        if i_entrada > i_padrao:
            peso_padrao = peso_seco * (100.0 - i_entrada) / (100.0 - i_padrao)
        else:
            peso_padrao = peso_seco
        desc_impureza = peso_seco - peso_padrao

        sacas = peso_padrao / saca_kg
        return desc_umidade, desc_impureza, peso_padrao, sacas

    async def criar(self, dados: RomaneioColheitaCreate) -> RomaneioColheita:
        dados_dict = dados.model_dump()

        # 1. Busca parâmetros do Commodity vinculado à safra (fallback: dict por cultura)
        from agricola.safras.models import Safra as SafraModel
        safra_obj = await self.session.get(SafraModel, dados.safra_id)
        params = await self._params_da_safra(safra_obj)

        # 2. Calcular o peso líquido bruto
        peso_bruto = dados_dict.get('peso_bruto_kg', 0)
        tara = float(dados_dict.get('tara_kg') or 0)
        peso_liquido = peso_bruto - tara
        dados_dict['peso_liquido_kg'] = peso_liquido

        if peso_liquido < 0:
            raise BusinessRuleError("Peso líquido não pode ser negativo.")

        # 3. Descontos por umidade e impureza (fórmula MAPA por cultura)
        desc_umidade, desc_impureza, peso_padrao, sacas = self._calcular_peso_padrao(
            peso_liquido,
            dados_dict.get('umidade_pct'),
            dados_dict.get('impureza_pct'),
            params,
        )
        dados_dict['desconto_umidade_kg'] = round(desc_umidade, 3)
        dados_dict['desconto_impureza_kg'] = round(desc_impureza, 3)
        dados_dict['peso_liquido_padrao_kg'] = round(peso_padrao, 3)

        # 4. Converter para sacas
        sacas = round(sacas, 3)
        dados_dict['sacas_60kg'] = sacas
        
        # 4. Calcular Receita Prevista se preço informado
        preco = dados_dict.get('preco_saca')
        if preco:
            dados_dict['receita_total'] = sacas * preco
            
        # 5. Produtividade sc/ha: busca área do talhão em SafraTalhao ou AreaRural
        from agricola.safras.models import SafraTalhao
        from core.cadastros.propriedades.models import AreaRural
        area_ha = None
        stmt_st = select(SafraTalhao.area_ha).where(
            SafraTalhao.safra_id == dados.safra_id,
            SafraTalhao.area_id == dados.talhao_id,
        )
        area_ha = (await self.session.execute(stmt_st)).scalar()
        if not area_ha:
            stmt_ar = select(AreaRural.area_hectares).where(AreaRural.id == dados.talhao_id)
            area_ha = (await self.session.execute(stmt_ar)).scalar()
        if area_ha and float(area_ha) > 0:
            dados_dict["produtividade_sc_ha"] = sacas / float(area_ha)

        romaneio = await super().create(dados_dict)

        # ── Integração com Financeiro: Receita de Venda de Grãos ──────────
        receita_total = dados_dict.get("receita_total") or 0.0
        if receita_total > 0:
            from financeiro.models.receita import Receita
            from financeiro.models.plano_conta import PlanoConta
            from agricola.talhoes.models import Talhao
            from agricola.safras.models import Safra

            stmt_talhao = select(Talhao.fazenda_id).where(Talhao.id == dados.talhao_id)
            fazenda_id = (await self.session.execute(stmt_talhao)).scalar()

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
            plano_id = (await self.session.execute(stmt_pc)).scalar()

            if plano_id and fazenda_id:
                stmt_safra = select(Safra.cultura, Safra.ano_safra).where(
                    Safra.id == dados.safra_id
                )
                safra_row = (await self.session.execute(stmt_safra)).first()
                descricao = (
                    f"Venda de grãos — {safra_row.cultura} {safra_row.ano_safra}"
                    if safra_row
                    else "Venda de grãos — Romaneio de Colheita"
                )
                rec = Receita(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    fazenda_id=fazenda_id,
                    plano_conta_id=plano_id,
                    descricao=descricao,
                    valor_total=float(receita_total),
                    data_emissao=dados.data_colheita,
                    data_vencimento=dados.data_colheita,
                    data_recebimento=dados.data_colheita,
                    status="RECEBIDO",
                    origem_id=romaneio.id,
                    origem_tipo="ROMANEIO_COLHEITA",
                )
                self.session.add(rec)

        await self.session.commit()
        await self.session.refresh(romaneio)
        return romaneio

    def _recalcular(self, d: dict, params: dict | None = None) -> dict:
        """Recalcula campos derivados usando fórmula MAPA por cultura."""
        if params is None:
            params = self._PARAMS_DEFAULT
        peso_bruto = float(d.get("peso_bruto_kg") or 0)
        tara = float(d.get("tara_kg") or 0)
        peso_liquido = peso_bruto - tara
        if peso_liquido < 0:
            raise BusinessRuleError("Peso líquido não pode ser negativo.")
        d["peso_liquido_kg"] = peso_liquido

        desc_umidade, desc_impureza, peso_padrao, sacas = self._calcular_peso_padrao(
            peso_liquido, d.get("umidade_pct"), d.get("impureza_pct"), params
        )
        d["desconto_umidade_kg"] = round(desc_umidade, 3)
        d["desconto_impureza_kg"] = round(desc_impureza, 3)
        d["peso_liquido_padrao_kg"] = round(peso_padrao, 3)
        d["sacas_60kg"] = round(sacas, 3)
        preco = d.get("preco_saca")
        if preco:
            d["receita_total"] = round(sacas * float(preco), 2)
        return d

    async def atualizar(self, id: UUID, dados: RomaneioColheitaUpdate) -> RomaneioColheita:
        romaneio = await self.get_or_fail(id)
        patch = dados.model_dump(exclude_unset=True)

        peso_fields = {"peso_bruto_kg", "tara_kg", "umidade_pct", "impureza_pct"}
        if patch.keys() & peso_fields:
            # Busca parâmetros do Commodity vinculado à safra (fallback: dict por cultura)
            from agricola.safras.models import Safra as SafraModel
            safra_obj = await self.session.get(SafraModel, romaneio.safra_id)
            params = await self._params_da_safra(safra_obj)

            merged = {
                "peso_bruto_kg": romaneio.peso_bruto_kg,
                "tara_kg": romaneio.tara_kg or 0,
                "umidade_pct": romaneio.umidade_pct,
                "impureza_pct": romaneio.impureza_pct,
                "preco_saca": romaneio.preco_saca,
            }
            merged.update(patch)
            patch = self._recalcular(merged, params)

        updated = await self.update(id, patch)
        return updated

    async def kpis_safra(self, safra_id: UUID) -> RomaneioKPIs:
        stmt = select(
            func.count(RomaneioColheita.id),
            func.coalesce(func.sum(RomaneioColheita.sacas_60kg), 0),
            func.coalesce(func.sum(RomaneioColheita.receita_total), 0),
        ).where(
            RomaneioColheita.tenant_id == self.tenant_id,
            RomaneioColheita.safra_id == safra_id,
        )
        row = (await self.session.execute(stmt)).first()
        total_romaneios, total_sacas, receita_total = row

        # Produtividade média: soma sacas / soma área dos talhões
        from agricola.safras.models import SafraTalhao
        stmt_area = select(func.sum(SafraTalhao.area_ha)).where(
            SafraTalhao.tenant_id == self.tenant_id,
            SafraTalhao.safra_id == safra_id,
        )
        area_total = (await self.session.execute(stmt_area)).scalar() or 0
        produtividade = float(total_sacas) / float(area_total) if area_total else None

        return RomaneioKPIs(
            total_romaneios=total_romaneios,
            total_sacas=float(total_sacas),
            receita_total=float(receita_total),
            produtividade_sc_ha=produtividade,
        )
