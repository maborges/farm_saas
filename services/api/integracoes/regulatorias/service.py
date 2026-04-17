"""
Serviço de integrações regulatórias — MVP:
- CEP: BrasilAPI (fallback ViaCEP)
- CNPJ: BrasilAPI
- CAR: SICAR/IBAMA

Cache em memória com TTL para evitar chamadas repetidas.
Falhas nunca bloqueiam o cadastro — retornam None silenciosamente.
"""

import re
import time
import httpx
from typing import Optional
from loguru import logger

# ---------------------------------------------------------------------------
# Cache TTL simples em memória
# ---------------------------------------------------------------------------
_CACHE: dict[str, tuple[dict, float]] = {}
_CEP_TTL = 86400      # 24h — CEPs mudam raramente
_CNPJ_TTL = 3600      # 1h
_CAR_TTL = 86400      # 24h
_TIMEOUT = 5.0        # segundos


def _cache_get(key: str) -> Optional[dict]:
    entry = _CACHE.get(key)
    if entry and time.monotonic() < entry[1]:
        return entry[0]
    _CACHE.pop(key, None)
    return None


def _cache_set(key: str, value: dict, ttl: float) -> None:
    if len(_CACHE) > 5000:
        # Evict 10% mais antigos
        oldest = sorted(_CACHE, key=lambda k: _CACHE[k][1])[:500]
        for k in oldest:
            _CACHE.pop(k, None)
    _CACHE[key] = (value, time.monotonic() + ttl)


# ---------------------------------------------------------------------------
# CEP — BrasilAPI (fallback ViaCEP)
# ---------------------------------------------------------------------------

async def consultar_cep(cep: str) -> Optional[dict]:
    """
    Retorna dados de endereço pelo CEP.

    Formato de retorno:
    {
        "cep": "01310100",
        "logradouro": "Avenida Paulista",
        "bairro": "Bela Vista",
        "municipio": "São Paulo",
        "uf": "SP",
        "ibge_municipio_codigo": "3550308"
    }
    """
    cep_limpo = re.sub(r"\D", "", cep)
    if len(cep_limpo) != 8:
        return None

    cached = _cache_get(f"cep:{cep_limpo}")
    if cached:
        return cached

    # Tenta ViaCEP primeiro — retorna código IBGE do município
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            if resp.status_code == 200:
                data = resp.json()
                if not data.get("erro"):
                    result = {
                        "cep": cep_limpo,
                        "logradouro": data.get("logradouro", ""),
                        "bairro": data.get("bairro", ""),
                        "municipio": data.get("localidade", ""),
                        "uf": data.get("uf", ""),
                        "ibge_municipio_codigo": data.get("ibge", ""),
                    }
                    _cache_set(f"cep:{cep_limpo}", result, _CEP_TTL)
                    return result
    except Exception as e:
        logger.warning(f"ViaCEP falhou para {cep_limpo}: {e}")

    # Fallback: BrasilAPI (não retorna IBGE)
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"https://brasilapi.com.br/api/cep/v2/{cep_limpo}")
            if resp.status_code == 200:
                data = resp.json()
                result = {
                    "cep": cep_limpo,
                    "logradouro": data.get("street", ""),
                    "bairro": data.get("neighborhood", ""),
                    "municipio": data.get("city", ""),
                    "uf": data.get("state", ""),
                    "ibge_municipio_codigo": "",
                }
                _cache_set(f"cep:{cep_limpo}", result, _CEP_TTL)
                return result
    except Exception as e:
        logger.warning(f"BrasilAPI CEP falhou para {cep_limpo}: {e}")

    return None


# ---------------------------------------------------------------------------
# CNPJ — BrasilAPI
# ---------------------------------------------------------------------------

async def consultar_cnpj(cnpj: str) -> Optional[dict]:
    """
    Retorna dados da empresa pelo CNPJ via BrasilAPI.

    Formato de retorno:
    {
        "cnpj": "00000000000100",
        "razao_social": "Empresa LTDA",
        "nome_fantasia": "Empresa",
        "situacao_cadastral": "ATIVA",
        "tipo": "MATRIZ",
        "cep": "01310100",
        "logradouro": "...",
        "municipio": "...",
        "uf": "SP"
    }
    """
    cnpj_limpo = re.sub(r"\D", "", cnpj)
    if len(cnpj_limpo) != 14:
        return None

    cached = _cache_get(f"cnpj:{cnpj_limpo}")
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}")
            if resp.status_code == 200:
                data = resp.json()
                result = {
                    "cnpj": cnpj_limpo,
                    "razao_social": data.get("razao_social", ""),
                    "nome_fantasia": data.get("nome_fantasia", ""),
                    "situacao_cadastral": data.get("descricao_situacao_cadastral", ""),
                    "tipo": data.get("descricao_identificador_matriz_filial", ""),
                    "cep": re.sub(r"\D", "", data.get("cep", "")),
                    "logradouro": f"{data.get('logradouro', '')} {data.get('numero', '')}".strip(),
                    "bairro": data.get("bairro", ""),
                    "municipio": data.get("municipio", ""),
                    "uf": data.get("uf", ""),
                }
                _cache_set(f"cnpj:{cnpj_limpo}", result, _CNPJ_TTL)
                return result
    except Exception as e:
        logger.warning(f"BrasilAPI CNPJ falhou para {cnpj_limpo}: {e}")

    return None


# ---------------------------------------------------------------------------
# CAR — SICAR/IBAMA
# ---------------------------------------------------------------------------

_CAR_REGEX = re.compile(
    r"^[A-Z]{2}-\d{7}-[A-Z0-9]{8}\.[A-Z0-9]{4}\.[A-Z0-9]{4}/\d{4}-\d{2}$"
)


def validar_formato_car(car_codigo: str) -> bool:
    """Valida formato do código CAR: UF-XXXXXXX-XXXX.XXXX.XXXX/XXXX-XX"""
    return bool(_CAR_REGEX.match(car_codigo.upper().strip())) if car_codigo else False


async def consultar_car(car_codigo: str) -> Optional[dict]:
    """
    Consulta dados do imóvel no SICAR/IBAMA pelo código CAR.

    NOTA: A API pública do SICAR é instável e não tem documentação oficial.
    Esta implementação usa o endpoint público de consulta.
    Em caso de falha, retorna None — o cadastro manual continua disponível.

    Formato de retorno:
    {
        "car_codigo": "SP-1234567-ABCD.EFGH.IJKL/2024-01",
        "status": "AT",  # AT=Ativo, PE=Pendente, CA=Cancelado, SU=Suspenso
        "status_descricao": "Ativo",
        "area_ha": 150.50,
        "municipio": "Ribeirão Preto",
        "uf": "SP",
        "data_cadastro": "2020-03-15"
    }
    """
    if not car_codigo:
        return None

    car_upper = car_codigo.upper().strip()
    cached = _cache_get(f"car:{car_upper}")
    if cached:
        return cached

    # Extrai UF do código CAR
    uf = car_upper[:2] if len(car_upper) >= 2 else ""

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                "https://consultapublica.car.gov.br/publico/imovel/pesquisar",
                params={"numeroCar": car_upper},
                headers={"Accept": "application/json"},
            )
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    item = data[0] if isinstance(data, list) else data
                    status_map = {
                        "AT": "Ativo",
                        "PE": "Pendente",
                        "CA": "Cancelado",
                        "SU": "Suspenso",
                    }
                    status = item.get("situacaoImovel", "")
                    result = {
                        "car_codigo": car_upper,
                        "status": status,
                        "status_descricao": status_map.get(status, status),
                        "area_ha": item.get("areaImovel"),
                        "municipio": item.get("nomeMunicipio", ""),
                        "uf": item.get("siglaUf", uf),
                        "data_cadastro": item.get("dataInicioAtividade", ""),
                    }
                    _cache_set(f"car:{car_upper}", result, _CAR_TTL)
                    return result
    except Exception as e:
        logger.warning(f"SICAR CAR falhou para {car_upper}: {e}")

    return None
