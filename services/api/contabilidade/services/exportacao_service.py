"""Services para Integrações Contábeis - Sprint 25."""

import os
import json
from datetime import datetime, date
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from contabilidade.models import (
    IntegracaoContabil, ExportacaoContabil, LancamentoContabil,
    PlanoContas, MapeamentoContabil
)


class DominioSistemasService:
    """Integração com Domínio Sistemas."""

    def __init__(self, db: Session):
        self.db = db

    def gerar_arquivo_lancamentos(self, exportacao: ExportacaoContabil,
                                   lancamentos: List[LancamentoContabil]) -> str:
        """
        Gera arquivo no formato Domínio Sistemas.
        Formato: TXT com layout específico
        """
        linhas = []
        
        for lanc in lancamentos:
            # Formato Domínio: Tipo Registro | Data | Histórico | Conta Débito | Conta Crédito | Valor
            linha = (
                f"1|{lanc.data_lancamento.strftime('%d/%m/%Y')}|"
                f"{lanc.historico[:50]}|{lanc.conta_debito or ''}|"
                f"{lanc.conta_credito or ''}|"
                f"{lanc.valor_debito:.2f}|{lanc.valor_credito:.2f}|"
                f"{lanc.centro_custo or ''}"
            )
            linhas.append(linha)
        
        # Salvar arquivo
        arquivo_path = self._salvar_arquivo(exportacao, linhas)
        return arquivo_path

    def gerar_arquivo_societario(self, exportacao: ExportacaoContabil,
                                  lancamentos: List[LancamentoContabil]) -> str:
        """Gera arquivo para Domínio Societário."""
        linhas = []
        
        for lanc in lancamentos:
            linha = (
                f"LAN|{lanc.data_lancamento.strftime('%d/%m/%Y')}|"
                f"{lanc.documento or ''}|{lanc.historico[:80]}|"
                f"{lanc.valor_debito + lanc.valor_credito:.2f}"
            )
            linhas.append(linha)
        
        arquivo_path = self._salvar_arquivo(exportacao, linhas)
        return arquivo_path

    def _salvar_arquivo(self, exportacao: ExportacaoContabil,
                        linhas: List[str]) -> str:
        """Salva arquivo de exportação."""
        diretorio = f"/tmp/exportacoes_contabeis/{exportacao.tenant_id}"
        os.makedirs(diretorio, exist_ok=True)
        
        arquivo_nome = f"dominio_{exportacao.tipo}_{exportacao.periodo_inicio}_{exportacao.periodo_fim}.txt"
        arquivo_path = os.path.join(diretorio, arquivo_nome)
        
        with open(arquivo_path, 'w', encoding='latin-1') as f:
            f.write('\n'.join(linhas))
        
        return arquivo_path


class FortesService:
    """Integração com Fortes Contábil."""

    def __init__(self, db: Session):
        self.db = db

    def gerar_arquivo_lancamentos(self, exportacao: ExportacaoContabil,
                                   lancamentos: List[LancamentoContabil]) -> str:
        """
        Gera arquivo no formato Fortes Contábil.
        Formato: CSV ou TXT
        """
        linhas = []
        
        # Cabeçalho
        linhas.append("Data;Documento;Historico;ContaDebito;ContaCredito;ValorDebito;ValorCredito;CentroCusto")
        
        for lanc in lancamentos:
            linha = (
                f"{lanc.data_lancamento.strftime('%d/%m/%Y')};"
                f"{lanc.documento or ''};"
                f"{lanc.historico[:100].replace(';', '-')};"
                f"{lanc.conta_debito or ''};"
                f"{lanc.conta_credito or ''};"
                f"{lanc.valor_debito:.2f};"
                f"{lanc.valor_credito:.2f};"
                f"{lanc.centro_custo or ''}"
            )
            linhas.append(linha)
        
        arquivo_path = self._salvar_arquivo(exportacao, linhas, '.csv')
        return arquivo_path

    def gerar_arquivo_xml(self, exportacao: ExportacaoContabil,
                          lancamentos: List[LancamentoContabil]) -> str:
        """Gera arquivo XML para Fortes."""
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<Lancamentos>\n'
        
        for lanc in lancamentos:
            xml += '  <Lancamento>\n'
            xml += f'    <Data>{lanc.data_lancamento.strftime("%Y-%m-%d")}</Data>\n'
            xml += f'    <Documento>{lanc.documento or ""}</Documento>\n'
            xml += f'    <Historico>{lanc.historico}</Historico>\n'
            xml += f'    <ContaDebito>{lanc.conta_debito or ""}</ContaDebito>\n'
            xml += f'    <ContaCredito>{lanc.conta_credito or ""}</ContaCredito>\n'
            xml += f'    <ValorDebito>{lanc.valor_debito:.2f}</ValorDebito>\n'
            xml += f'    <ValorCredito>{lanc.valor_credito:.2f}</ValorCredito>\n'
            xml += f'    <CentroCusto>{lanc.centro_custo or ""}</CentroCusto>\n'
            xml += '  </Lancamento>\n'
        
        xml += '</Lancamentos>'
        
        arquivo_path = self._salvar_arquivo(exportacao, [xml], '.xml')
        return arquivo_path

    def _salvar_arquivo(self, exportacao: ExportacaoContabil,
                        linhas: List[str], extensao: str = '.csv') -> str:
        """Salva arquivo de exportação."""
        diretorio = f"/tmp/exportacoes_contabeis/{exportacao.tenant_id}"
        os.makedirs(diretorio, exist_ok=True)
        
        arquivo_nome = f"fortes_{exportacao.tipo}_{exportacao.periodo_inicio}_{exportacao.periodo_fim}{extensao}"
        arquivo_path = os.path.join(diretorio, arquivo_nome)
        
        with open(arquivo_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(linhas))
        
        return arquivo_path


class ContmaticService:
    """Integração com Contmatic (Domínio Contmatic)."""

    def __init__(self, db: Session):
        self.db = db

    def gerar_arquivo_lancamentos(self, exportacao: ExportacaoContabil,
                                   lancamentos: List[LancamentoContabil]) -> str:
        """
        Gera arquivo no formato Contmatic.
        Formato específico Contmatic
        """
        linhas = []
        
        for lanc in lancamentos:
            # Formato Contmatic: Registro | Código Conta | Data | Valor | Histórico | CC
            if lanc.valor_debito > 0:
                tipo = 'D'
                valor = lanc.valor_debito
                conta = lanc.conta_debito
            else:
                tipo = 'C'
                valor = lanc.valor_credito
                conta = lanc.conta_credito
            
            linha = (
                f"M|{conta or ''}|{lanc.data_lancamento.strftime('%d/%m/%Y')}|"
                f"{tipo}|{valor:.2f}|{lanc.historico[:60]}|{lanc.centro_custo or ''}"
            )
            linhas.append(linha)
        
        arquivo_path = self._salvar_arquivo(exportacao, linhas)
        return arquivo_path

    def _salvar_arquivo(self, exportacao: ExportacaoContabil,
                        linhas: List[str]) -> str:
        """Salva arquivo de exportação."""
        diretorio = f"/tmp/exportacoes_contabeis/{exportacao.tenant_id}"
        os.makedirs(diretorio, exist_ok=True)
        
        arquivo_nome = f"contmatic_{exportacao.tipo}_{exportacao.periodo_inicio}_{exportacao.periodo_fim}.txt"
        arquivo_path = os.path.join(diretorio, arquivo_nome)
        
        with open(arquivo_path, 'w', encoding='latin-1') as f:
            f.write('\n'.join(linhas))
        
        return arquivo_path


class ExportacaoContabilService:
    """Serviço principal de exportação contábil."""

    def __init__(self, db: Session):
        self.db = db
        self.dominio = DominioSistemasService(db)
        self.fortes = FortesService(db)
        self.contmatic = ContmaticService(db)

    def criar_integracao(self, tenant_id: str, sistema: str,
                         nome: str, configuracoes: dict) -> IntegracaoContabil:
        """Cria nova integração contábil."""
        integracao = IntegracaoContabil(
            tenant_id=tenant_id,
            sistema=sistema,
            nome=nome,
            configuracoes=configuracoes
        )
        self.db.add(integracao)
        self.db.commit()
        self.db.refresh(integracao)
        return integracao

    def exportar_lancamentos(self, tenant_id: str, integracao_id: int,
                             periodo_inicio: date, periodo_fim: date,
                             tipo: str = 'lancamentos') -> ExportacaoContabil:
        """Exporta lançamentos contábeis para sistema contábil."""
        integracao = self.db.query(IntegracaoContabil).filter(
            IntegracaoContabil.id == integracao_id,
            IntegracaoContabil.tenant_id == tenant_id
        ).first()
        
        if not integracao:
            raise ValueError("Integração não encontrada")
        
        # Buscar lançamentos do período
        lancamentos = self.db.query(LancamentoContabil).filter(
            LancamentoContabil.tenant_id == tenant_id,
            LancamentoContabil.data_lancamento.between(periodo_inicio, periodo_fim),
            LancamentoContabil.exportado == False
        ).all()
        
        # Criar registro de exportação
        exportacao = ExportacaoContabil(
            tenant_id=tenant_id,
            integracao_id=integracao_id,
            tipo=tipo,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            status='processando',
            registros_exportados=len(lancamentos)
        )
        self.db.add(exportacao)
        self.db.commit()
        self.db.refresh(exportacao)
        
        try:
            # Gerar arquivo baseado no sistema
            if integracao.sistema == 'dominio':
                arquivo_path = self.dominio.gerar_arquivo_lancamentos(exportacao, lancamentos)
            elif integracao.sistema == 'fortes':
                arquivo_path = self.fortes.gerar_arquivo_lancamentos(exportacao, lancamentos)
            elif integracao.sistema == 'contmatic':
                arquivo_path = self.contmatic.gerar_arquivo_lancamentos(exportacao, lancamentos)
            else:
                raise ValueError(f"Sistema {integracao.sistema} não suportado")
            
            # Atualizar exportação
            exportacao.status = 'concluida'
            exportacao.arquivo_path = arquivo_path
            exportacao.arquivo_nome = os.path.basename(arquivo_path)
            exportacao.arquivo_formato = os.path.splitext(arquivo_path)[1][1:]
            exportacao.arquivo_tamanho = os.path.getsize(arquivo_path)
            exportacao.processada_em = datetime.utcnow()
            
            # Marcar lançamentos como exportados
            for lanc in lancamentos:
                lanc.exportado = True
                lanc.exportacao_id = exportacao.id
            
            # Atualizar última exportação da integração
            integracao.ultima_exportacao = datetime.utcnow()
            
            self.db.commit()
            
        except Exception as e:
            exportacao.status = 'erro'
            exportacao.erro_mensagem = str(e)
            self.db.commit()
            raise
        
        return exportacao

    def agendar_exportacao(self, tenant_id: str, integracao_id: int,
                           periodo: str = 'mensal',
                           dia_execucao: int = 5) -> dict:
        """Agenda exportação automática."""
        # Em produção, configurar Celery beat
        return {
            "sucesso": True,
            "mensagem": f"Exportação agendada para dia {dia_execucao} de cada mês",
            "periodo": periodo,
            "dia_execucao": dia_execucao
        }

    def listar_exportacoes(self, tenant_id: str,
                           integracao_id: Optional[int] = None,
                           status: Optional[str] = None) -> List[ExportacaoContabil]:
        """Lista exportações contábeis."""
        query = self.db.query(ExportacaoContabil).filter(
            ExportacaoContabil.tenant_id == tenant_id
        )
        
        if integracao_id:
            query = query.filter(ExportacaoContabil.integracao_id == integracao_id)
        
        if status:
            query = query.filter(ExportacaoContabil.status == status)
        
        return query.order_by(ExportacaoContabil.created_at.desc()).all()
