"""Routers consolidados para Sprints 27-33."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from core.database import get_db
from core.dependencies import get_current_tenant, require_module
from enterprise.services.sprints_27_33_service import (
    MRVService, ESGService, PisciculturaService,
    ConfinamentoService, GeneticaService, HedgingService,
    IoTService, ILPFService, ColaboradorService
)

router = APIRouter(prefix="/sprints27-33", tags=["Sprints 27-33"], dependencies=[Depends(require_module("EXT_IA"))])


def get_mrv_service(db: Session = Depends(get_db)) -> MRVService:
    return MRVService(db)


def get_esg_service(db: Session = Depends(get_db)) -> ESGService:
    return ESGService(db)


def get_piscicultura_service(db: Session = Depends(get_db)) -> PisciculturaService:
    return PisciculturaService(db)


def get_confinamento_service(db: Session = Depends(get_db)) -> ConfinamentoService:
    return ConfinamentoService(db)


def get_genetica_service(db: Session = Depends(get_db)) -> GeneticaService:
    return GeneticaService(db)


def get_hedging_service(db: Session = Depends(get_db)) -> HedgingService:
    return HedgingService(db)


def get_iot_service(db: Session = Depends(get_db)) -> IoTService:
    return IoTService(db)


def get_ilpf_service(db: Session = Depends(get_db)) -> ILPFService:
    return ILPFService(db)


def get_colaborador_service(db: Session = Depends(get_db)) -> ColaboradorService:
    return ColaboradorService(db)


# ============================================
# SPRINT 27 - MRV
# ============================================

@router.post("/mrv/projetos", response_model=None)
def criar_projeto_mrv(
    nome: str,
    metodologia: str,
    area_ha: float,
    tenant_id: str = Depends(get_current_tenant),
    service: MRVService = Depends(get_mrv_service)
):
    """Cria projeto MRV."""
    return service.criar_projeto(tenant_id, nome, metodologia, area_ha)


@router.post("/mrv/relatorios", response_model=None)
def gerar_relatorio_mrv(
    projeto_id: int,
    periodo_inicio: date,
    periodo_fim: date,
    service: MRVService = Depends(get_mrv_service)
):
    """Gera relatório MRV."""
    return service.gerar_relatorio(projeto_id, periodo_inicio, periodo_fim)


# ============================================
# SPRINT 28 - ESG
# ============================================

@router.post("/esg/indicadores", response_model=None)
def registrar_indicador_esg(
    categoria: str,
    nome: str,
    valor: float,
    periodo: str,
    tenant_id: str = Depends(get_current_tenant),
    service: ESGService = Depends(get_esg_service)
):
    """Registra indicador ESG."""
    return service.registrar_indicador(tenant_id, categoria, nome, valor, periodo)


@router.post("/esg/relatorios", response_model=None)
def gerar_relatorio_esg(
    ano: int,
    tenant_id: str = Depends(get_current_tenant),
    service: ESGService = Depends(get_esg_service)
):
    """Gera relatório ESG anual."""
    return service.gerar_relatorio(tenant_id, ano)


# ============================================
# SPRINT 28 - PISCICULTURA
# ============================================

@router.post("/piscicultura/tanques", response_model=None)
def criar_tanque(
    nome: str,
    volume_m3: float,
    especie: str,
    tenant_id: str = Depends(get_current_tenant),
    service: PisciculturaService = Depends(get_piscicultura_service)
):
    """Cria tanque-rede."""
    return service.criar_tanque(tenant_id, nome, volume_m3, especie)


@router.post("/piscicultura/arracoamento", response_model=None)
def registrar_arracoamento(
    tanque_id: int,
    quantidade: float,
    tipo_racao: str,
    data: date,
    service: PisciculturaService = Depends(get_piscicultura_service)
):
    """Registra arraçoamento."""
    return service.registrar_arracoamento(tanque_id, quantidade, tipo_racao, data)


@router.post("/piscicultura/pesagem", response_model=None)
def registrar_pesagem(
    tanque_id: int,
    total_peixes: int,
    peso_total: float,
    data: date,
    service: PisciculturaService = Depends(get_piscicultura_service)
):
    """Registra pesagem."""
    return service.registrar_pesagem(tanque_id, total_peixes, peso_total, data)


# ============================================
# SPRINT 29 - CONFINAMENTO
# ============================================

@router.post("/confinamento/lotes", response_model=None)
def criar_lote_confinamento(
    codigo: str,
    total_animais: int,
    peso_inicial: float,
    data_entrada: date,
    tenant_id: str = Depends(get_current_tenant),
    service: ConfinamentoService = Depends(get_confinamento_service)
):
    """Cria lote de confinamento."""
    return service.criar_lote(tenant_id, codigo, total_animais, peso_inicial, data_entrada)


@router.post("/confinamento/racoes", response_model=None)
def criar_racao_tmr(
    nome: str,
    ingredientes: dict,
    proteina_bruta: float,
    tenant_id: str = Depends(get_current_tenant),
    service: ConfinamentoService = Depends(get_confinamento_service)
):
    """Cria ração TMR."""
    return service.criar_racao_tmr(tenant_id, nome, ingredientes, proteina_bruta)


# ============================================
# SPRINT 30 - GENÉTICA
# ============================================

@router.post("/genetica/racas", response_model=None)
def cadastrar_raca(
    nome: str,
    especie: str,
    origem: str,
    service: GeneticaService = Depends(get_genetica_service)
):
    """Cadastra raça."""
    return service.cadastrar_raca(nome, especie, origem)


@router.post("/genetica/acasalamentos", response_model=None)
def sugerir_acasalamento(
    matriz_id: int,
    reprodutor_id: int,
    tenant_id: str = Depends(get_current_tenant),
    service: GeneticaService = Depends(get_genetica_service)
):
    """Sugere acasalamento."""
    return service.sugerir_acasalamento(tenant_id, matriz_id, reprodutor_id)


# ============================================
# SPRINT 31 - HEDGING
# ============================================

@router.post("/hedging/contratos", response_model=None)
def criar_contrato_futuro(
    commodity: str,
    mercado: str,
    codigo: str,
    tipo: str,
    quantidade: float,
    preco: float,
    tenant_id: str = Depends(get_current_tenant),
    service: HedgingService = Depends(get_hedging_service)
):
    """Cria contrato futuro."""
    return service.criar_contrato(tenant_id, commodity, mercado, codigo, tipo, quantidade, preco)


@router.post("/hedging/registros", response_model=None)
def registrar_hedge(
    contrato_id: int,
    tipo: str,
    quantidade: float,
    preco: float,
    data: date,
    tenant_id: str = Depends(get_current_tenant),
    service: HedgingService = Depends(get_hedging_service)
):
    """Registra operação de hedge."""
    return service.registrar_hedge(tenant_id, contrato_id, tipo, quantidade, preco, data)


# ============================================
# SPRINT 32 - IOT SENSORES
# ============================================

@router.post("/iot/sensores", response_model=None)
def cadastrar_sensor(
    nome: str,
    tipo: str,
    protocolo: str,
    tenant_id: str = Depends(get_current_tenant),
    service: IoTService = Depends(get_iot_service)
):
    """Cadastra sensor IoT."""
    return service.cadastrar_sensor(tenant_id, nome, tipo, protocolo)


@router.post("/iot/leituras", response_model=None)
def registrar_leitura_sensor(
    sensor_id: int,
    valor: float,
    unidade: str,
    service: IoTService = Depends(get_iot_service)
):
    """Registra leitura de sensor."""
    return service.registrar_leitura(sensor_id, valor, unidade)


# ============================================
# SPRINT 33 - ILPF
# ============================================

@router.post("/ilpf/modulos", response_model=None)
def criar_modulo_ilpf(
    nome: str,
    tipo_ilpf: str,
    area_ha: float,
    cultura: str,
    especie_florestal: str,
    tenant_id: str = Depends(get_current_tenant),
    service: ILPFService = Depends(get_ilpf_service)
):
    """Cria módulo ILPF."""
    return service.criar_modulo(tenant_id, nome, tipo_ilpf, area_ha, cultura, especie_florestal)


# ============================================
# SPRINT 33 - APP COLABORADORES
# ============================================

@router.post("/colaboradores/apontamentos", response_model=None)
def registrar_apontamento(
    colaborador_id: int,
    data: date,
    horas: float,
    atividade: str,
    tenant_id: str = Depends(get_current_tenant),
    service: ColaboradorService = Depends(get_colaborador_service)
):
    """Registra apontamento de horas."""
    return service.registrar_apontamento(tenant_id, colaborador_id, data, horas, atividade)
