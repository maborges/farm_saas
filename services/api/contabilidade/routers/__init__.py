"""Routers para Contabilidade - Sprint 25."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from core.database import get_db
from core.dependencies import get_current_tenant
from contabilidade.schemas import (
    IntegracaoContabilCreate, IntegracaoContabilResponse,
    ExportacaoContabilCreate, ExportacaoContabilResponse,
    LancamentoContabilCreate, LancamentoContabilResponse,
    MapeamentoContabilCreate, MapeamentoContabilResponse,
    PlanoContasResponse
)
from contabilidade.models import (
    IntegracaoContabil, ExportacaoContabil, LancamentoContabil,
    MapeamentoContabil, PlanoContas
)
from contabilidade.services.exportacao_service import ExportacaoContabilService

router = APIRouter(prefix="/contabilidade", tags=["Contabilidade"])


def get_exportacao_service(db: Session) -> ExportacaoContabilService:
    return ExportacaoContabilService(db)


# ============================================
# INTEGRAÇÕES CONTÁBEIS
# ============================================

@router.post("/integracoes", response_model=IntegracaoContabilResponse, status_code=201)
def criar_integracao_contabil(
    integracao: IntegracaoContabilCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
    service: ExportacaoContabilService = Depends(get_exportacao_service)
):
    """Cria nova integração com sistema contábil."""
    return service.criar_integracao(
        tenant_id=tenant_id,
        sistema=integracao.sistema,
        nome=integracao.nome,
        configuracoes=integracao.configuracoes or {}
    )


@router.get("/integracoes", response_model=List[IntegracaoContabilResponse])
def listar_integracoes_contabeis(
    sistema: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista integrações contábeis do tenant."""
    query = db.query(IntegracaoContabil).filter(
        IntegracaoContabil.tenant_id == tenant_id
    )
    
    if sistema:
        query = query.filter(IntegracaoContabil.sistema == sistema)
    
    return query.all()


@router.delete("/integracoes/{integracao_id}", status_code=204)
def remover_integracao_contabil(
    integracao_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Remove integração contábil."""
    integracao = db.query(IntegracaoContabil).filter(
        IntegracaoContabil.id == integracao_id,
        IntegracaoContabil.tenant_id == tenant_id
    ).first()
    if not integracao:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    
    db.delete(integracao)
    db.commit()
    return None


# ============================================
# EXPORTAÇÕES CONTÁBEIS
# ============================================

@router.post("/exportacoes", response_model=ExportacaoContabilResponse)
def exportar_lancamentos(
    exportacao: ExportacaoContabilCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
    service: ExportacaoContabilService = Depends(get_exportacao_service)
):
    """Exporta lançamentos contábeis para sistema contábil."""
    return service.exportar_lancamentos(
        tenant_id=tenant_id,
        integracao_id=exportacao.integracao_id,
        periodo_inicio=exportacao.periodo_inicio,
        periodo_fim=exportacao.periodo_fim,
        tipo=exportacao.tipo
    )


@router.get("/exportacoes", response_model=List[ExportacaoContabilResponse])
def listar_exportacoes_contabeis(
    integracao_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista exportações contábeis."""
    query = db.query(ExportacaoContabil).filter(
        ExportacaoContabil.tenant_id == tenant_id
    )
    
    if integracao_id:
        query = query.filter(ExportacaoContabil.integracao_id == integracao_id)
    
    if status:
        query = query.filter(ExportacaoContabil.status == status)
    
    return query.order_by(ExportacaoContabil.created_at.desc()).all()


@router.get("/exportacoes/{exportacao_id}/download")
def download_exportacao(
    exportacao_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Download do arquivo de exportação."""
    exportacao = db.query(ExportacaoContabil).filter(
        ExportacaoContabil.id == exportacao_id,
        ExportacaoContabil.tenant_id == tenant_id
    ).first()
    if not exportacao:
        raise HTTPException(status_code=404, detail="Exportação não encontrada")
    
    if exportacao.status != 'concluida' or not exportacao.arquivo_path:
        raise HTTPException(status_code=400, detail="Arquivo não disponível")
    
    return {
        "arquivo": exportacao.arquivo_nome,
        "caminho": exportacao.arquivo_path,
        "formato": exportacao.arquivo_formato,
        "tamanho": exportacao.arquivo_tamanho
    }


@router.post("/exportacoes/agendar")
def agendar_exportacao(
    integracao_id: int,
    periodo: str = 'mensal',
    dia_execucao: int = 5,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
    service: ExportacaoContabilService = Depends(get_exportacao_service)
):
    """Agenda exportação automática."""
    return service.agendar_exportacao(
        tenant_id=tenant_id,
        integracao_id=integracao_id,
        periodo=periodo,
        dia_execucao=dia_execucao
    )


# ============================================
# LANÇAMENTOS CONTÁBEIS
# ============================================

@router.post("/lancamentos", response_model=LancamentoContabilResponse, status_code=201)
def criar_lancamento_contabil(
    lancamento: LancamentoContabilCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Cria lançamento contábil."""
    db_obj = LancamentoContabil(
        tenant_id=tenant_id,
        **lancamento.model_dump()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.get("/lancamentos", response_model=List[LancamentoContabilResponse])
def listar_lancamentos_contabeis(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    exportados: Optional[bool] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista lançamentos contábeis."""
    query = db.query(LancamentoContabil).filter(
        LancamentoContabil.tenant_id == tenant_id
    )
    
    if data_inicio:
        query = query.filter(LancamentoContabil.data_lancamento >= data_inicio)
    if data_fim:
        query = query.filter(LancamentoContabil.data_lancamento <= data_fim)
    if exportados is not None:
        query = query.filter(LancamentoContabil.exportado == exportados)
    
    return query.order_by(LancamentoContabil.data_lancamento.desc()).all()


# ============================================
# MAPEAMENTO CONTÁBIL
# ============================================

@router.post("/mapeamentos", response_model=MapeamentoContabilResponse, status_code=201)
def criar_mapeamento_contabil(
    mapeamento: MapeamentoContabilCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Cria mapeamento entre AgroSaaS e sistema contábil."""
    db_obj = MapeamentoContabil(
        tenant_id=tenant_id,
        **mapeamento.model_dump(exclude={'integracao_id'})
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.get("/mapeamentos", response_model=List[MapeamentoContabilResponse])
def listar_mapeamentos_contabeis(
    integracao_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista mapeamentos contábeis."""
    query = db.query(MapeamentoContabil).filter(
        MapeamentoContabil.tenant_id == tenant_id
    )
    
    if integracao_id:
        query = query.filter(MapeamentoContabil.integracao_id == integracao_id)
    
    return query.all()


# ============================================
# PLANO DE CONTAS
# ============================================

@router.get("/plano-contas", response_model=List[PlanoContasResponse])
def listar_plano_contas(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    """Lista plano de contas."""
    return db.query(PlanoContas).filter(
        PlanoContas.tenant_id == tenant_id,
        PlanoContas.ativo == True
    ).order_by(PlanoContas.codigo).all()
