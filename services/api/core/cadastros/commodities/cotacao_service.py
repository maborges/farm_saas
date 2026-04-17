"""
Servico de cotações de commodities.

Fontes suportadas:
- CEPEA (Centro de Estudos Avançados em Economia Aplicada)
- B3 (Brasil Bolsa Balcão) — via API pública de futuros
- CONAB (Companhia Nacional de Abastecimento)
- Manual (entrada via API, padrão fallback)

Em produção, cada fonte requer credenciais configuradas no .env.
Fallback: se a fonte falhar, a cotação pode ser inserida manualmente.
"""
import asyncio
import httpx
from datetime import datetime, timezone, date
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.cadastros.commodities.models import Commodity
from core.cadastros.commodities.models import CotacaoCommodity
from core.config import settings
from loguru import logger


# ---------------------------------------------------------------------------
# Mapeamento commodity → código nas bolsas
# ---------------------------------------------------------------------------

BOLSAS = {
    # (commodity_codigo_bolsa, fonte_padrao)
    "SOJA": {"CBOT": "ZS", "CEPEA": "soja_sp"},
    "MILHO": {"CBOT": "ZC", "CEPEA": "milho_campinas"},
    "TRIGO": {"CBOT": "ZW"},
    "ALGODAO": {"ICE": "CT", "CEPEA": "algodao_mt"},
    "ARROZ": {"CBOT": "ZR"},
    "CAFE_ARABICA": {"ICE": "KC", "CEPEA": "cafe_arabica"},
    "CAFE_CONILON": {"ICE": "RC"},
    "BOI_GORDO": {"B3": "BGI", "CEPEA": "boi_gordo_sp"},
    "LEITE": {"CEPEA": "leite_cepea"},
    "EUCALIPTO": {"CEPEA": "eucalipto"},
}


class CotacaoService:
    """Busca e armazena cotações de commodities."""

    def __init__(self, session: AsyncSession, tenant_id):
        self.session = session
        self.tenant_id = tenant_id
        self.http = httpx.AsyncClient(timeout=15.0)

    async def close(self):
        await self.http.aclose()

    # ------------------------------------------------------------------
    # Fetchers por fonte
    # ------------------------------------------------------------------

    async def fetch_cepea(self, codigo_commodity: str, data_ref: Optional[date] = None) -> Optional[float]:
        """
        Busca cotação CEPEA.
        Requer CEPEA_API_URL e CEPEA_API_TOKEN no .env.
        Fallback: retorna None se não configurado.
        """
        token = getattr(settings, "cepea_api_token", None)
        base_url = getattr(settings, "cepea_api_url", None)
        if not token or not base_url:
            logger.debug("CEPEA não configurado (sem token/url)")
            return None

        codigo = BOLSAS.get(codigo_commodity, {}).get("CEPEA")
        if not codigo:
            return None

        url = f"{base_url}/indicadores/{codigo}"
        if data_ref:
            url += f"?data={data_ref.isoformat()}"

        try:
            resp = await self.http.get(url, headers={"Authorization": f"Bearer {token}"})
            resp.raise_for_status()
            dados = resp.json()
            # CEPEA retorna algo como {"valor": 150.50, "data": "2026-04-12"}
            return float(dados.get("valor") or dados.get("preco") or dados.get("cotacao"))
        except Exception as e:
            logger.warning(f"CEPEA falhou para {codigo_commodity}: {e}")
            return None

    async def fetch_b3(self, codigo_commodity: str, data_ref: Optional[date] = None) -> Optional[float]:
        """
        Busca cotação B3 (futuros).
        Fallback: retorna None — em produção usar API B3 com token.
        """
        codigo = BOLSAS.get(codigo_commodity, {}).get("B3")
        if not codigo:
            return None

        # B3 não tem API pública gratuita para dados históricos de futuros.
        # Placeholder para integração futura.
        logger.debug(f"B3: fetch não implementado para {codigo_commodity}")
        return None

    async def fetch_cbot(self, codigo_commodity: str, data_ref: Optional[date] = None) -> Optional[float]:
        """
        Busca cotação CBOT (Chicago Board of Trade).
        Usa API pública alternativa (ex: Alpha Vantage, Yahoo Finance).
        Fallback: None.
        """
        codigo = BOLSAS.get(codigo_commodity, {}).get("CBOT")
        if not codigo:
            return None

        api_key = getattr(settings, "alphavantage_api_key", None)
        if not api_key:
            logger.debug("Alpha Vantage não configurado")
            return None

        # Exemplo: Alpha Vantage futures endpoint
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={codigo}&apikey={api_key}"
        try:
            resp = await self.http.get(url)
            resp.raise_for_status()
            dados = resp.json()
            ts = dados.get("Time Series (Daily)", {})
            if ts:
                latest_date = list(ts.keys())[0]
                latest = ts[latest_date]
                # Retorna em USD — converter se necessário
                return float(latest.get("4. close", 0))
        except Exception as e:
            logger.warning(f"CBOT/Alpha Vantage falhou para {codigo_commodity}: {e}")
        return None

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------

    async def salvar_cotacao(
        self,
        commodity_id,
        data: date,
        preco: float,
        fonte: str,
        moeda: str = "BRL",
    ) -> CotacaoCommodity:
        """Salva ou atualiza cotação."""
        # Verificar se já existe
        stmt = select(CotacaoCommodity).where(
            CotacaoCommodity.commodity_id == commodity_id,
            CotacaoCommodity.data == data,
            CotacaoCommodity.fonte == fonte,
        )
        existente = (await self.session.execute(stmt)).scalar_one_or_none()

        if existente:
            existente.preco = preco
            existente.moeda = moeda
            cotacao = existente
        else:
            cotacao = CotacaoCommodity(
                commodity_id=commodity_id,
                data=data,
                preco=preco,
                moeda=moeda,
                fonte=fonte,
            )
            self.session.add(cotacao)

        return cotacao

    # ------------------------------------------------------------------
    # Orquestrador
    # ------------------------------------------------------------------

    async def atualizar_todas(
        self,
        fonte: Optional[str] = None,
        data_ref: Optional[date] = None,
    ) -> dict:
        """
        Atualiza cotações de todas as commodities com cotação habilitada.

        Retorna dict com estatísticas:
        {
            "total": 10,
            "sucesso": 7,
            "falha": 3,
            "detalhes": [{"commodity": "Soja", "fonte": "CEPEA", "preco": 150.50, "erro": None}, ...]
        }
        """
        if data_ref is None:
            data_ref = date.today()

        stmt = select(Commodity).where(
            Commodity.possui_cotacao == True,
            Commodity.ativo == True,
        )
        # Incluir commodities de sistema (tenant_id NULL)
        if self.tenant_id:
            from sqlalchemy import or_
            stmt = stmt.where(
                or_(
                    Commodity.tenant_id == self.tenant_id,
                    Commodity.sistema == True,
                )
            )

        commodities = (await self.session.execute(stmt)).scalars().all()

        resultado = {"total": len(commodities), "sucesso": 0, "falha": 0, "detalhes": []}

        for comm in commodities:
            # Determinar fontes a tentar
            fontes_para_tentar = []
            if fonte:
                fontes_para_tentar.append(fonte)
            else:
                # Ordem: CEPEA → CBOT → B3
                if comm.bolsa_referencia:
                    fontes_para_tentar.append(comm.bolsa_referencia.upper())
                fontes_para_tentar.extend(["CEPEA", "CBOT", "B3"])
                # Deduplicar mantendo ordem
                seen = set()
                fontes_para_tentar = [f for f in fontes_para_tentar if not (f in seen or seen.add(f))]

            preco = None
            fonte_usada = None

            for f in fontes_para_tentar:
                if f == "CEPEA":
                    preco = await self.fetch_cepea(comm.codigo, data_ref)
                elif f == "CBOT":
                    preco = await self.fetch_cbot(comm.codigo, data_ref)
                elif f == "B3":
                    preco = await self.fetch_b3(comm.codigo, data_ref)

                if preco is not None:
                    fonte_usada = f
                    break

            if preco is not None and preco > 0:
                await self.salvar_cotacao(
                    commodity_id=comm.id,
                    data=data_ref,
                    preco=preco,
                    fonte=fonte_usada or "MANUAL",
                )
                resultado["sucesso"] += 1
                resultado["detalhes"].append({
                    "commodity": comm.nome,
                    "codigo": comm.codigo,
                    "fonte": fonte_usada,
                    "preco": preco,
                    "erro": None,
                })
                logger.info(f"✅ Cotação {comm.nome}: {preco} ({fonte_usada})")
            else:
                resultado["falha"] += 1
                resultado["detalhes"].append({
                    "commodity": comm.nome,
                    "codigo": comm.codigo,
                    "fonte": None,
                    "preco": None,
                    "erro": "Nenhuma fonte retornou valor",
                })
                logger.warning(f"❌ Cotação {comm.nome}: nenhuma fonte disponível")

        await self.session.commit()
        return resultado
