"""
Routers de Conciliação Bancária

Endpoints para importação de extrato OFX e conciliação bancária.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
from datetime import datetime

from financeiro.services.ofx_parser import OFXParser, OFXParserFactory
from financeiro.services.conciliacao_service import (
    ConciliacaoBancariaService,
    ConciliacaoBancariaFactory,
    SugestaoConciliacao,
)
from core.database import get_db
from core.dependencies import get_current_tenant, require_module
from core.models.tenant import Tenant

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conciliacao", tags=["Conciliação Bancária"], dependencies=[Depends(require_module("F1_TESOURARIA"))])


@router.post("/upload-extrato")
async def upload_extrato(
    arquivo: UploadFile = File(..., description="Arquivo OFX do extrato bancário"),
    conta_bancaria_id: Optional[str] = None,
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Faz upload de arquivo OFX e extrai transações do extrato
    
    - **arquivo**: Arquivo OFX do banco
    - **conta_bancaria_id**: ID da conta bancária (opcional)
    
    Retorna as transações extraídas para conferência antes da conciliação.
    """
    # Validar arquivo
    if not arquivo.filename:
        raise HTTPException(status_code=400, detail="Arquivo não informado")
    
    if not arquivo.filename.lower().endswith('.ofx'):
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo inválido. Esperado OFX, recebido: {arquivo.filename}"
        )
    
    try:
        # Ler conteúdo do arquivo
        conteudo = await arquivo.read()
        conteudo_str = conteudo.decode('latin-1')  # OFX usa encoding latin-1
        
        # Parse do OFX
        parser = OFXParserFactory.get_parser()
        extrato = parser.parse_conteudo(conteudo_str)
        
        # Validar extrato
        if not extrato.transacoes:
            raise HTTPException(
                status_code=400,
                detail="Nenhuma transação encontrada no extrato"
            )
        
        # Retornar transações para conferência
        return {
            "sucesso": True,
            "mensagem": f"{len(extrato.transacoes)} transações encontradas",
            "extrato": {
                "banco": extrato.banco,
                "conta": extrato.conta,
                "agencia": extrato.agencia,
                "saldo_inicial": extrato.saldo_inicial,
                "saldo_final": extrato.saldo_final,
                "data_inicial": extrato.data_inicial.isoformat() if extrato.data_inicial else None,
                "data_final": extrato.data_final.isoformat() if extrato.data_final else None,
                "total_transacoes": len(extrato.transacoes),
            },
            "transacoes": extrato.to_dict()["transacoes"],
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar OFX: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )


@router.get("/transacoes-pendentes")
async def listar_transacoes_pendentes(
    conta_bancaria_id: Optional[str] = None,
    data_inicial: Optional[datetime] = None,
    data_final: Optional[datetime] = None,
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Lista transações do extrato ainda não conciliadas
    
    - **conta_bancaria_id**: Filtro por conta (opcional)
    - **data_inicial**: Filtro por data inicial (opcional)
    - **data_final**: Filtro por data final (opcional)
    """
    # TODO: Implementar busca no banco de dados
    # Por enquanto, retorna mock para desenvolvimento
    
    return {
        "total": 0,
        "transacoes": [],
    }


@router.get("/lancamentos-pendentes")
async def listar_lancamentos_pendentes(
    conta_bancaria_id: Optional[str] = None,
    data_inicial: Optional[datetime] = None,
    data_final: Optional[datetime] = None,
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Lista lançamentos do sistema financeiro ainda não conciliados
    
    - **conta_bancaria_id**: Filtro por conta (opcional)
    - **data_inicial**: Filtro por data inicial (opcional)
    - **data_final**: Filtro por data final (opcional)
    """
    # TODO: Implementar busca no banco de dados
    # Por enquanto, retorna mock para desenvolvimento
    
    return {
        "total": 0,
        "lancamentos": [],
    }


@router.post("/conciliar-automatico")
async def conciliar_automatico(
    transacoes_extrato: List[dict],
    lancamentos_sistema: List[dict],
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Realiza conciliação automática entre extrato e sistema
    
    - **transacoes_extrato**: Lista de transações do extrato
    - **lancamentos_sistema**: Lista de lançamentos do sistema
    
    Retorna sugestões de conciliação ordenadas por confiança.
    """
    try:
        service = ConciliacaoBancariaFactory.get_service()
        
        sugestoes = service.conciliar(
            transacoes_extrato=transacoes_extrato,
            lancamentos_sistema=lancamentos_sistema,
        )
        
        return {
            "sucesso": True,
            "total_sugestoes": len(sugestoes),
            "sugestoes": [s.to_dict() for s in sugestoes],
        }
        
    except Exception as e:
        logger.error(f"Erro na conciliação automática: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao conciliar: {str(e)}"
        )


@router.post("/conciliar-manual")
async def conciliar_manual(
    transacao_extrato_id: str,
    lancamento_sistema_id: str,
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Realiza conciliação manual (forçada pelo usuário)
    
    - **transacao_extrato_id**: ID da transação do extrato
    - **lancamento_sistema_id**: ID do lançamento do sistema
    """
    try:
        service = ConciliacaoBancariaFactory.get_service()
        
        sugestao = service.conciliar_manual(
            transacao_extrato_id=transacao_extrato_id,
            lancamento_sistema_id=lancamento_sistema_id,
        )
        
        # TODO: Salvar conciliação no banco de dados
        
        return {
            "sucesso": True,
            "mensagem": "Conciliação realizada com sucesso",
            "conciliacao": sugestao.to_dict(),
        }
        
    except Exception as e:
        logger.error(f"Erro na conciliação manual: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao conciliar: {str(e)}"
        )


@router.post("/aprovar-conciliacao")
async def aprovar_conciliacao(
    sugestoes: List[dict],
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Aprova lote de sugestões de conciliação
    
    - **sugestoes**: Lista de sugestões para aprovar
    """
    try:
        conciliacoes_aprovadas = []
        
        for sugestao in sugestoes:
            # TODO: Validar sugestão
            # TODO: Salvar conciliação no banco
            # TODO: Marcar transação e lançamento como conciliados
            
            conciliacoes_aprovadas.append({
                "transacao_extrato_id": sugestao.get("transacao_extrato_id"),
                "lancamento_sistema_id": sugestao.get("lancamento_sistema_id"),
                "status": "aprovado",
            })
        
        return {
            "sucesso": True,
            "total_aprovadas": len(conciliacoes_aprovadas),
            "conciliacoes": conciliacoes_aprovadas,
        }
        
    except Exception as e:
        logger.error(f"Erro ao aprovar conciliação: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao aprovar: {str(e)}"
        )


@router.get("/resumo-conciliacao")
async def get_resumo_conciliacao(
    periodo: str = "mes",  # dia, semana, mes, ano
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Retorna resumo das conciliações do período
    
    - **periodo**: Período do resumo (dia, semana, mes, ano)
    """
    # TODO: Implementar busca no banco de dados
    
    return {
        "periodo": periodo,
        "total_transacoes": 0,
        "total_conciliadas": 0,
        "total_pendentes": 0,
        "percentual_conciliado": 0.0,
        "valor_total_conciliado": 0.0,
    }


@router.delete("/desfazer-conciliacao/{conciliacao_id}")
async def desfazer_conciliacao(
    conciliacao_id: str,
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Desfaz uma conciliação aprovada
    
    - **conciliacao_id**: ID da conciliação para desfazer
    """
    # TODO: Implementar no banco de dados
    
    return {
        "sucesso": True,
        "mensagem": f"Conciliação {conciliacao_id} desfeita com sucesso",
    }
