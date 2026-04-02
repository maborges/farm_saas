"""Routers para Sprint 26: New Holland, Marketplace, Carbono."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from core.database import get_db
from core.dependencies import get_current_tenant
from iot_integracao.new_holland.models import (
    IntegracaoNewHolland, MaquinaNewHolland,
    MarketplaceIntegracao, TenantIntegracao,
    CarbonoEmissao, CarbonoProjeto, CarbonoRelatorio
)
from iot_integracao.new_holland.services import (
    NewHollandService, MarketplaceService, CarbonoService
)

router = APIRouter(prefix="/sprint26", tags=["Sprint 26"])


def get_nh_service(db: Session = Depends(get_db)) -> NewHollandService:
    return NewHollandService(db)


def get_marketplace_service(db: Session = Depends(get_db)) -> MarketplaceService:
    return MarketplaceService(db)


def get_carbono_service(db: Session = Depends(get_db)) -> CarbonoService:
    return CarbonoService(db)


# ============================================
# NEW HOLLAND
# ============================================

@router.post("/new-holland/conectar", response_model=None)
def conectar_new_holland(
    client_id: str,
    client_secret: str,
    fazenda_id: Optional[int] = None,
    tenant_id: str = Depends(get_current_tenant),
    service: NewHollandService = Depends(get_nh_service)
):
    """Conecta integração com New Holland PLM Connect."""
    return service.conectar(tenant_id, client_id, client_secret, fazenda_id)


@router.get("/new-holland", response_model=None)
def listar_new_holland(
    tenant_id: str = Depends(get_current_tenant),
    service: NewHollandService = Depends(get_nh_service)
):
    """Lista integrações New Holland do tenant."""
    return service.listar_integracoes(tenant_id)


@router.post("/new-holland/{integracao_id}/sincronizar", response_model=None)
def sincronizar_new_holland(
    integracao_id: int,
    tenant_id: str = Depends(get_current_tenant),
    service: NewHollandService = Depends(get_nh_service)
):
    """Sincroniza máquinas da New Holland."""
    count = service.sincronizar_maquinas(tenant_id, integracao_id)
    return {"mensagem": f"{count} máquinas sincronizadas"}


@router.get("/new-holland/{integracao_id}/maquinas", response_model=None)
def listar_maquinas_nh(
    integracao_id: int,
    tenant_id: str = Depends(get_current_tenant),
    service: NewHollandService = Depends(get_nh_service)
):
    """Lista máquinas New Holland."""
    return service.listar_maquinas(tenant_id, integracao_id)


# ============================================
# MARKETPLACE
# ============================================

@router.get("/marketplace", response_model=None)
def listar_marketplace(
    categoria: Optional[str] = None,
    service: MarketplaceService = Depends(get_marketplace_service)
):
    """Lista integrações disponíveis no marketplace."""
    return service.listar_integracoes(categoria)


@router.get("/marketplace/instaladas", response_model=None)
def listar_instaladas(
    tenant_id: str = Depends(get_current_tenant),
    service: MarketplaceService = Depends(get_marketplace_service)
):
    """Lista integrações instaladas pelo tenant."""
    return service.listar_instaladas(tenant_id)


@router.post("/marketplace/{integracao_id}/instalar", response_model=None)
def instalar_integracao(
    integracao_id: int,
    configuracoes: dict = None,
    tenant_id: str = Depends(get_current_tenant),
    service: MarketplaceService = Depends(get_marketplace_service)
):
    """Instala integração do marketplace."""
    return service.instalar_integracao(tenant_id, integracao_id, configuracoes)


@router.post("/marketplace/{integracao_id}/desinstalar", response_model=None)
def desinstalar_integracao(
    integracao_id: int,
    tenant_id: str = Depends(get_current_tenant),
    service: MarketplaceService = Depends(get_marketplace_service)
):
    """Desinstala integração do tenant."""
    if not service.desinstalar_integracao(tenant_id, integracao_id):
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    return {"mensagem": "Integração desinstalada"}


# ============================================
# CARBONO
# ============================================

@router.post("/carbono/emissao", response_model=None)
def registrar_emissao(
    escopo: int,
    categoria: str,
    quantidade: float,
    unidade: str,
    data_referencia: date,
    fazenda_id: Optional[int] = None,
    tenant_id: str = Depends(get_current_tenant),
    service: CarbonoService = Depends(get_carbono_service)
):
    """Registra emissão de carbono."""
    return service.registrar_emissao(
        tenant_id, escopo, categoria, quantidade,
        unidade, data_referencia, fazenda_id=fazenda_id
    )


@router.get("/carbono/pegada", response_model=None)
def calcular_pegada(
    periodo_inicio: date,
    periodo_fim: date,
    tenant_id: str = Depends(get_current_tenant),
    service: CarbonoService = Depends(get_carbono_service)
):
    """Calcula pegada de carbono do período."""
    return service.calcular_pegada(tenant_id, periodo_inicio, periodo_fim)


@router.post("/carbono/projetos", response_model=None)
def criar_projeto_carbono(
    nome: str,
    tipo: str,
    area_ha: float,
    fazenda_id: Optional[int] = None,
    tenant_id: str = Depends(get_current_tenant),
    service: CarbonoService = Depends(get_carbono_service)
):
    """Cria projeto de crédito de carbono."""
    return service.criar_projeto(tenant_id, nome, tipo, area_ha, fazenda_id)


@router.get("/carbono/projetos", response_model=None)
def listar_projetos_carbono(
    tenant_id: str = Depends(get_current_tenant),
    service: CarbonoService = Depends(get_carbono_service)
):
    """Lista projetos de carbono do tenant."""
    return service.listar_projetos(tenant_id)


@router.post("/carbono/relatorio", response_model=None)
def gerar_relatorio_carbono(
    periodo_inicio: date,
    periodo_fim: date,
    tenant_id: str = Depends(get_current_tenant),
    service: CarbonoService = Depends(get_carbono_service)
):
    """Gera relatório de pegada de carbono."""
    return service.gerar_relatorio(tenant_id, periodo_inicio, periodo_fim)
