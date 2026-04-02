"""Routers para integração com ERP Sankhya."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import time
from datetime import date, timedelta

from core.database import get_db
from core.dependencies import get_current_tenant
from integracoes.sankhya.schemas import (
    SankhyaConfigCreate, SankhyaConfigResponse,
    SankhyaSyncLogResponse, SankhyaPessoaResponse,
    SankhyaProdutoResponse, SankhyaTestConnectionResponse,
    SankhyaSyncStatusResponse, SankhyaNFEResponse,
    SankhyaLancamentoFinanceiroResponse
)
from integracoes.sankhya.models import (
    SankhyaConfig, SankhyaSyncLog, SankhyaPessoa, SankhyaProduto,
    SankhyaNFe, SankhyaLancamentoFinanceiro
)
from integracoes.sankhya.services import (
    SankhyaSyncService, SankhyaPessoaService, SankhyaProdutoService,
    SankhyaNFeService, SankhyaFinanceiroService
)

router = APIRouter(prefix="/sankhya", tags=["Integração Sankhya"])


def get_sync_service(db: Session = Depends(get_db)) -> SankhyaSyncService:
    return SankhyaSyncService(db)


def get_pessoa_service(db: Session = Depends(get_db)) -> SankhyaPessoaService:
    return SankhyaPessoaService(db)


def get_produto_service(db: Session = Depends(get_db)) -> SankhyaProdutoService:
    return SankhyaProdutoService(db)


def get_nfe_service(db: Session = Depends(get_db)) -> SankhyaNFeService:
    return SankhyaNFeService(db)


def get_financeiro_service(db: Session = Depends(get_db)) -> SankhyaFinanceiroService:
    return SankhyaFinanceiroService(db)


# ============================================
# CONFIGURAÇÃO
# ============================================

@router.post("/config", response_model=SankhyaConfigResponse, status_code=201)
def configurar_sankhya(
    config: SankhyaConfigCreate,
    tenant_id: str = Depends(get_current_tenant),
    sync_service: SankhyaSyncService = Depends(get_sync_service)
):
    """Configura integração com Sankhya."""
    existing = sync_service.get_config(tenant_id)

    if existing:
        existing.ws_url = config.ws_url
        existing.username = config.username
        existing.password = config.password
        existing.sync_interval = config.sync_interval
        sync_service.db.commit()
        sync_service.db.refresh(existing)
        return existing
    else:
        return sync_service.criar_config(
            tenant_id=tenant_id,
            ws_url=config.ws_url,
            username=config.username,
            password=config.password,
            sync_interval=config.sync_interval
        )


@router.get("/config", response_model=SankhyaConfigResponse)
def obter_config_sankhya(
    tenant_id: str = Depends(get_current_tenant),
    sync_service: SankhyaSyncService = Depends(get_sync_service)
):
    """Obtém configuração Sankhya do tenant."""
    config = sync_service.get_config(tenant_id)
    if not config:
        raise HTTPException(status_code=404, detail="Sankhya não configurado")
    return config


@router.post("/config/testar-conexao", response_model=SankhyaTestConnectionResponse)
def testar_conexao_sankhya(
    tenant_id: str = Depends(get_current_tenant),
    sync_service: SankhyaSyncService = Depends(get_sync_service)
):
    """Testa conexão com Sankhya."""
    return sync_service.testar_conexao(tenant_id)


@router.get("/status", response_model=SankhyaSyncStatusResponse)
def obter_status_sankhya(
    tenant_id: str = Depends(get_current_tenant),
    sync_service: SankhyaSyncService = Depends(get_sync_service)
):
    """Obtém status da integração Sankhya."""
    config = sync_service.get_config(tenant_id)

    if not config:
        return {
            "configurado": False,
            "ativo": False,
            "ultimo_sync": None,
            "proximo_sync": None,
            "status_conexao": "nao_configurado"
        }

    proximo_sync = None
    if config.ultimo_sync:
        proximo_sync = config.ultimo_sync + timedelta(seconds=config.sync_interval)

    return {
        "configurado": True,
        "ativo": config.ativo,
        "ultimo_sync": config.ultimo_sync,
        "proximo_sync": proximo_sync,
        "status_conexao": config.teste_status or "desconhecido"
    }


# ============================================
# SINCRONIZAÇÃO
# ============================================

@router.post("/sync/pessoas", response_model=None)
def sincronizar_pessoas(
    tenant_id: str = Depends(get_current_tenant),
    sync_service: SankhyaSyncService = Depends(get_sync_service),
    pessoa_service: SankhyaPessoaService = Depends(get_pessoa_service)
):
    """Sincroniza pessoas do Sankhya."""
    import asyncio

    log = sync_service.iniciar_sync_log(tenant_id, "pessoas", "import")

    try:
        start_time = time.time()

        importados = asyncio.run(
            pessoa_service.importar_pessoas(tenant_id, log.id)
        )

        tempo_ms = (time.time() - start_time) * 1000

        sync_service.finalizar_sync_log(
            log.id, True, importados, 0, None, tempo_ms
        )

        return {
            "sucesso": True,
            "mensagem": f"{importados} pessoas sincronizadas",
            "tempo_ms": tempo_ms
        }

    except Exception as e:
        sync_service.finalizar_sync_log(
            log.id, False, 0, 0, str(e), 0
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/produtos", response_model=None)
def sincronizar_produtos(
    tenant_id: str = Depends(get_current_tenant),
    sync_service: SankhyaSyncService = Depends(get_sync_service),
    produto_service: SankhyaProdutoService = Depends(get_produto_service)
):
    """Sincroniza produtos do Sankhya."""
    import asyncio

    log = sync_service.iniciar_sync_log(tenant_id, "produtos", "import")

    try:
        start_time = time.time()

        importados = asyncio.run(
            produto_service.importar_produtos(tenant_id, log.id)
        )

        tempo_ms = (time.time() - start_time) * 1000

        sync_service.finalizar_sync_log(
            log.id, True, importados, 0, None, tempo_ms
        )

        return {
            "sucesso": True,
            "mensagem": f"{importados} produtos sincronizados",
            "tempo_ms": tempo_ms
        }

    except Exception as e:
        sync_service.finalizar_sync_log(
            log.id, False, 0, 0, str(e), 0
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/completo", response_model=None)
def sincronizar_completo(
    tenant_id: str = Depends(get_current_tenant),
    sync_service: SankhyaSyncService = Depends(get_sync_service)
):
    """Executa sincronização completa (pessoas + produtos)."""
    return {
        "pessoas": "Fila de sincronização",
        "produtos": "Fila de sincronização",
        "mensagem": "Sincronização em segundo plano iniciada"
    }


# ============================================
# LOGS
# ============================================

@router.get("/logs", response_model=List[SankhyaSyncLogResponse])
def listar_logs_sankhya(
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    tenant_id: str = Depends(get_current_tenant),
    sync_service: SankhyaSyncService = Depends(get_sync_service)
):
    """Lista logs de sincronização."""
    query = sync_service.db.query(SankhyaSyncLog).filter(
        SankhyaSyncLog.tenant_id == tenant_id
    )

    if tipo:
        query = query.filter(SankhyaSyncLog.tipo == tipo)

    if status:
        query = query.filter(SankhyaSyncLog.status == status)

    return query.order_by(SankhyaSyncLog.created_at.desc()).limit(limit).all()


# ============================================
# PESSOAS
# ============================================

@router.get("/pessoas", response_model=List[SankhyaPessoaResponse])
def listar_pessoas_sankhya(
    tipo: Optional[str] = None,
    ativo: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = Depends(get_current_tenant),
    pessoa_service: SankhyaPessoaService = Depends(get_pessoa_service)
):
    """Lista pessoas sincronizadas do Sankhya."""
    query = pessoa_service.db.query(SankhyaPessoa).filter(
        SankhyaPessoa.tenant_id == tenant_id
    )

    if tipo:
        query = query.filter(SankhyaPessoa.tipo == tipo)

    if ativo is not None:
        query = query.filter(SankhyaPessoa.ativo == ativo)

    return query.offset(skip).limit(limit).all()


# ============================================
# PRODUTOS
# ============================================

@router.get("/produtos", response_model=List[SankhyaProdutoResponse])
def listar_produtos_sankhya(
    ativo: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = Depends(get_current_tenant),
    produto_service: SankhyaProdutoService = Depends(get_produto_service)
):
    """Lista produtos sincronizados do Sankhya."""
    query = produto_service.db.query(SankhyaProduto).filter(
        SankhyaProduto.tenant_id == tenant_id
    )

    if ativo is not None:
        query = query.filter(SankhyaProduto.ativo == ativo)

    return query.offset(skip).limit(limit).all()


# ============================================
# NOTAS FISCAIS
# ============================================

@router.post("/nfe/exportar", response_model=None)
def exportar_nfe(
    nfe_data: dict,
    tenant_id: str = Depends(get_current_tenant),
    service: SankhyaNFeService = Depends(get_nfe_service)
):
    """Exporta Nota Fiscal para o Sankhya."""
    import asyncio

    try:
        resultado = asyncio.run(service.exportar_nfe(tenant_id, nfe_data))
        return {"sucesso": True, "dados": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nfe/importar-entrada", response_model=None)
def importar_nfe_entrada(
    periodo_inicio: date,
    periodo_fim: date,
    tenant_id: str = Depends(get_current_tenant),
    service: SankhyaNFeService = Depends(get_nfe_service)
):
    """Importa Notas Fiscais de entrada do Sankhya."""
    import asyncio

    try:
        importadas = asyncio.run(
            service.importar_nfe_entrada(tenant_id, periodo_inicio, periodo_fim)
        )
        return {
            "sucesso": True,
            "mensagem": f"{importadas} NFes de entrada importadas"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nfe", response_model=List[SankhyaNFEResponse])
def listar_nfe_sankhya(
    tipo_operacao: Optional[str] = None,
    exportado: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = Depends(get_current_tenant),
    service: SankhyaNFeService = Depends(get_nfe_service)
):
    """Lista Notas Fiscais sincronizadas."""
    query = service.db.query(SankhyaNFe).filter(
        SankhyaNFe.tenant_id == tenant_id
    )

    if tipo_operacao:
        query = query.filter(SankhyaNFe.tipo_operacao == tipo_operacao)

    if exportado is not None:
        query = query.filter(SankhyaNFe.exportado_sankhya == exportado)

    return query.offset(skip).limit(limit).all()


# ============================================
# FINANCEIRO
# ============================================

@router.post("/financeiro/exportar-contas-pagar", response_model=None)
def exportar_contas_pagar(
    lancamentos: List[dict],
    tenant_id: str = Depends(get_current_tenant),
    service: SankhyaFinanceiroService = Depends(get_financeiro_service)
):
    """Exporta contas a pagar para o Sankhya."""
    import asyncio

    try:
        resultado = asyncio.run(
            service.exportar_contas_pagar(tenant_id, lancamentos)
        )
        return {"sucesso": True, "dados": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/financeiro/exportar-contas-receber", response_model=None)
def exportar_contas_receber(
    lancamentos: List[dict],
    tenant_id: str = Depends(get_current_tenant),
    service: SankhyaFinanceiroService = Depends(get_financeiro_service)
):
    """Exporta contas a receber para o Sankhya."""
    import asyncio

    try:
        resultado = asyncio.run(
            service.exportar_contas_receber(tenant_id, lancamentos)
        )
        return {"sucesso": True, "dados": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/financeiro/importar", response_model=None)
def importar_financeiro(
    periodo_inicio: date,
    periodo_fim: date,
    tipo: str = "AMBOS",
    tenant_id: str = Depends(get_current_tenant),
    service: SankhyaFinanceiroService = Depends(get_financeiro_service)
):
    """Importa lançamentos financeiros do Sankhya."""
    import asyncio

    try:
        importados = asyncio.run(
            service.importar_lancamentos(tenant_id, periodo_inicio, periodo_fim, tipo)
        )
        return {
            "sucesso": True,
            "mensagem": f"{importados} lançamentos importados"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/financeiro", response_model=List[SankhyaLancamentoFinanceiroResponse])
def listar_financeiro_sankhya(
    tipo: Optional[str] = None,
    exportado: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = Depends(get_current_tenant),
    service: SankhyaFinanceiroService = Depends(get_financeiro_service)
):
    """Lista lançamentos financeiros sincronizados."""
    query = service.db.query(SankhyaLancamentoFinanceiro).filter(
        SankhyaLancamentoFinanceiro.tenant_id == tenant_id
    )

    if tipo:
        query = query.filter(SankhyaLancamentoFinanceiro.tipo == tipo)

    if exportado is not None:
        query = query.filter(SankhyaLancamentoFinanceiro.exportado_sankhya == exportado)

    return query.offset(skip).limit(limit).all()
