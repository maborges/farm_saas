"""Services para integração de NFe e Financeiro com Sankhya."""

import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from sqlalchemy.orm import Session

from integracoes.sankhya.models import (
    SankhyaConfig, SankhyaSyncLog, SankhyaNFe,
    SankhyaLancamentoFinanceiro, SankhyaPessoa, SankhyaProduto
)
from integracoes.sankhya.services.sync_service import SankhyaWSClient


class SankhyaNFeService:
    """Serviço para integração de Notas Fiscais com Sankhya."""

    def __init__(self, db: Session):
        self.db = db

    def _get_config(self, tenant_id: str) -> Optional[SankhyaConfig]:
        return self.db.query(SankhyaConfig).filter(
            SankhyaConfig.tenant_id == tenant_id
        ).first()

    async def exportar_nfe(self, tenant_id: str, nfe_data: Dict) -> Dict[str, Any]:
        """
        Exporta Nota Fiscal para o Sankhya.
        
        Args:
            tenant_id: ID do tenant
            nfe_data: Dados da NFe
        
        Returns:
            Resultado da exportação
        """
        config = self._get_config(tenant_id)
        if not config:
            raise Exception("Sankhya não configurado")
        
        async with SankhyaWSClient(config) as client:
            # Preparar dados no formato Sankhya
            sankhya_data = self._prepare_nfe_data(nfe_data)
            
            # Chamar WS para salvar NFe
            resultado = await client.executar_ws(
                "NFe", "save", sankhya_data
            )
            
            # Atualizar registro local
            if resultado.get("success"):
                self._atualizar_nfe_exportada(
                    tenant_id, 
                    nfe_data.get("chave_acesso"),
                    resultado.get("sankhya_id")
                )
            
            return resultado

    async def importar_nfe_entrada(self, tenant_id: str,
                                   periodo_inicio: date,
                                   periodo_fim: date) -> int:
        """
        Importa Notas Fiscais de entrada do Sankhya.
        
        Args:
            tenant_id: ID do tenant
            periodo_inicio: Data início
            periodo_fim: Data fim
        
        Returns:
            Quantidade de NFes importadas
        """
        config = self._get_config(tenant_id)
        if not config:
            return 0
        
        importadas = 0
        
        async with SankhyaWSClient(config) as client:
            try:
                # Buscar NFes de entrada no período
                resultado = await client.executar_ws(
                    "NFe", "findEntradaByPeriodo",
                    {
                        "dataInicio": periodo_inicio.strftime("%Y-%m-%d"),
                        "dataFim": periodo_fim.strftime("%Y-%m-%d")
                    }
                )
                
                for nfe_data in resultado.get("nfe", []):
                    await self._salvar_nfe_entrada(tenant_id, nfe_data)
                    importadas += 1
                    
            except Exception as e:
                print(f"Erro ao importar NFe entrada: {e}")
        
        return importadas

    def _prepare_nfe_data(self, nfe_data: Dict) -> Dict:
        """Prepara dados da NFe no formato Sankhya."""
        return {
            "CHAVEACESSO": nfe_data.get("chave_acesso"),
            "NUMNOTA": nfe_data.get("numero"),
            "SERIE": nfe_data.get("serie"),
            "CFOP": nfe_data.get("cfop"),
            "CODPARC": nfe_data.get("cod_parc"),
            "VLTOTAL": nfe_data.get("valor_total"),
            "VLPROD": nfe_data.get("valor_produtos"),
            "VLFRETE": nfe_data.get("valor_frete"),
            "VLSEGURO": nfe_data.get("valor_seguro"),
            "VLDESC": nfe_data.get("valor_desconto"),
            "VLIPI": nfe_data.get("valor_ipi"),
            "VLICMS": nfe_data.get("valor_icms"),
            "VLPIS": nfe_data.get("valor_pis"),
            "VLCOFINS": nfe_data.get("valor_cofins"),
            "DATAEMISSAO": nfe_data.get("data_emissao"),
            "ITENS": nfe_data.get("itens", [])
        }

    def _atualizar_nfe_exportada(self, tenant_id: str,
                                 chave_acesso: str,
                                 sankhya_id: str):
        """Atualiza registro de NFe como exportada."""
        nfe = self.db.query(SankhyaNFe).filter(
            SankhyaNFe.tenant_id == tenant_id,
            SankhyaNFe.chave_acesso == chave_acesso
        ).first()
        
        if nfe:
            nfe.exportado_sankhya = True
            nfe.sankhya_id = sankhya_id
            nfe.sincronizado_em = datetime.utcnow()
            self.db.commit()

    async def _salvar_nfe_entrada(self, tenant_id: str,
                                 data: Dict) -> SankhyaNFe:
        """Salva NFe de entrada."""
        nfe = SankhyaNFe(
            tenant_id=tenant_id,
            sankhya_id=str(data.get("CODNEG", "")),
            tipo_operacao="ENTRADA",
            numero=str(data.get("NUMNOTA", "")),
            serie=data.get("SERIE", ""),
            modelo=data.get("MODNOTA", "55"),
            chave_acesso=data.get("CHAVEACESSO", ""),
            cnpj_emitente=data.get("CGCEMIT", ""),
            valor_total=float(data.get("VLTOTAL", 0) or 0),
            valor_produtos=float(data.get("VLPROD", 0) or 0),
            valor_frete=float(data.get("VLFRETE", 0) or 0),
            valor_icms=float(data.get("VLICMS", 0) or 0),
            data_emissao=self._parse_date(data.get("DATAEMISSAO")),
            status_sankhya=data.get("STATUS", ""),
            importado_sankhya=True,
            sincronizado_em=datetime.utcnow()
        )
        
        # Upsert
        existing = self.db.query(SankhyaNFe).filter(
            SankhyaNFe.chave_acesso == nfe.chave_acesso
        ).first()
        
        if existing:
            for key, value in nfe.__dict__.items():
                if not key.startswith('_') and value is not None:
                    setattr(existing, key, value)
            nfe = existing
        else:
            self.db.add(nfe)
        
        self.db.commit()
        self.db.refresh(nfe)
        return nfe

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse de string de data."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return None


class SankhyaFinanceiroService:
    """Serviço para integração financeira com Sankhya."""

    def __init__(self, db: Session):
        self.db = db

    def _get_config(self, tenant_id: str) -> Optional[SankhyaConfig]:
        return self.db.query(SankhyaConfig).filter(
            SankhyaConfig.tenant_id == tenant_id
        ).first()

    async def exportar_contas_pagar(self, tenant_id: str,
                                   lancamentos: List[Dict]) -> Dict[str, Any]:
        """
        Exporta contas a pagar para o Sankhya.
        
        Args:
            tenant_id: ID do tenant
            lancamentos: Lista de lançamentos
        
        Returns:
            Resultado da exportação
        """
        config = self._get_config(tenant_id)
        if not config:
            raise Exception("Sankhya não configurado")
        
        exportados = 0
        erros = []
        
        async with SankhyaWSClient(config) as client:
            for lancamento in lancamentos:
                try:
                    sankhya_data = self._prepare_lancamento_data(
                        lancamento, "CONTAS_PAGAR"
                    )
                    
                    resultado = await client.executar_ws(
                        "Lancamento", "save", sankhya_data
                    )
                    
                    if resultado.get("success"):
                        self._atualizar_lancamento_exportado(
                            tenant_id,
                            lancamento.get("id"),
                            resultado.get("sankhya_id"),
                            "CONTAS_PAGAR"
                        )
                        exportados += 1
                    else:
                        erros.append({
                            "id": lancamento.get("id"),
                            "erro": resultado.get("error")
                        })
                        
                except Exception as e:
                    erros.append({
                        "id": lancamento.get("id"),
                        "erro": str(e)
                    })
        
        return {
            "exportados": exportados,
            "erros": erros
        }

    async def exportar_contas_receber(self, tenant_id: str,
                                     lancamentos: List[Dict]) -> Dict[str, Any]:
        """
        Exporta contas a receber para o Sankhya.
        
        Args:
            tenant_id: ID do tenant
            lancamentos: Lista de lançamentos
        
        Returns:
            Resultado da exportação
        """
        config = self._get_config(tenant_id)
        if not config:
            raise Exception("Sankhya não configurado")
        
        exportados = 0
        erros = []
        
        async with SankhyaWSClient(config) as client:
            for lancamento in lancamentos:
                try:
                    sankhya_data = self._prepare_lancamento_data(
                        lancamento, "CONTAS_RECEBER"
                    )
                    
                    resultado = await client.executar_ws(
                        "Lancamento", "save", sankhya_data
                    )
                    
                    if resultado.get("success"):
                        self._atualizar_lancamento_exportado(
                            tenant_id,
                            lancamento.get("id"),
                            resultado.get("sankhya_id"),
                            "CONTAS_RECEBER"
                        )
                        exportados += 1
                    else:
                        erros.append({
                            "id": lancamento.get("id"),
                            "erro": resultado.get("error")
                        })
                        
                except Exception as e:
                    erros.append({
                        "id": lancamento.get("id"),
                        "erro": str(e)
                    })
        
        return {
            "exportados": exportados,
            "erros": erros
        }

    async def importar_lancamentos(self, tenant_id: str,
                                  periodo_inicio: date,
                                  periodo_fim: date,
                                  tipo: str = "AMBOS") -> int:
        """
        Importa lançamentos financeiros do Sankhya.
        
        Args:
            tenant_id: ID do tenant
            periodo_inicio: Data início
            periodo_fim: Data fim
            tipo: CONTAS_PAGAR, CONTAS_RECEBER ou AMBOS
        
        Returns:
            Quantidade de lançamentos importados
        """
        config = self._get_config(tenant_id)
        if not config:
            return 0
        
        importados = 0
        
        async with SankhyaWSClient(config) as client:
            try:
                resultado = await client.executar_ws(
                    "Lancamento", "findByPeriodo",
                    {
                        "dataInicio": periodo_inicio.strftime("%Y-%m-%d"),
                        "dataFim": periodo_fim.strftime("%Y-%m-%d"),
                        "tipo": tipo
                    }
                )
                
                for lanc_data in resultado.get("lancamentos", []):
                    await self._salvar_lancamento(tenant_id, lanc_data)
                    importados += 1
                    
            except Exception as e:
                print(f"Erro ao importar lançamentos: {e}")
        
        return importados

    def _prepare_lancamento_data(self, lancamento: Dict,
                                tipo: str) -> Dict:
        """Prepara dados do lançamento no formato Sankhya."""
        return {
            "TIPO": tipo,
            "CODPARC": lancamento.get("cod_parc"),
            "CODNEG": lancamento.get("cod_negocio"),
            "DESDOB": lancamento.get("desdobramento"),
            "VLRDESDOB": lancamento.get("valor"),
            "DTNEG": lancamento.get("data_negocio"),
            "DTVENC": lancamento.get("data_vencimento"),
            "HISTORICO": lancamento.get("historico"),
            "RATEIO": lancamento.get("rateio", {})
        }

    def _atualizar_lancamento_exportado(self, tenant_id: str,
                                       local_id: int,
                                       sankhya_id: str,
                                       tipo: str):
        """Atualiza lançamento como exportado."""
        lancamento = self.db.query(SankhyaLancamentoFinanceiro).filter(
            SankhyaLancamentoFinanceiro.tenant_id == tenant_id,
            SankhyaLancamentoFinanceiro.id == local_id
        ).first()
        
        if lancamento:
            lancamento.exportado_sankhya = True
            lancamento.sankhya_id = sankhya_id
            lancamento.sincronizado_em = datetime.utcnow()
            self.db.commit()

    async def _salvar_lancamento(self, tenant_id: str,
                                data: Dict) -> SankhyaLancamentoFinanceiro:
        """Salva lançamento financeiro."""
        lancamento = SankhyaLancamentoFinanceiro(
            tenant_id=tenant_id,
            sankhya_id=str(data.get("DESDOB", "")),
            tipo=data.get("TIPO", "CONTAS_PAGAR"),
            numero_documento=data.get("NUMDOC", ""),
            valor=float(data.get("VLRDESDOB", 0) or 0),
            valor_saldo=float(data.get("VLRSALDO", 0) or 0),
            data_lancamento=self._parse_date(data.get("DTLANC")),
            data_vencimento=self._parse_date(data.get("DTVENC")),
            historico=data.get("HISTORICO", ""),
            rateio=data.get("RATEIO", {}),
            status=data.get("STATUS", "ABERTO"),
            importado_sankhya=True,
            sincronizado_em=datetime.utcnow()
        )
        
        # Upsert
        existing = self.db.query(SankhyaLancamentoFinanceiro).filter(
            SankhyaLancamentoFinanceiro.sankhya_id == lancamento.sankhya_id
        ).first()
        
        if existing:
            for key, value in lancamento.__dict__.items():
                if not key.startswith('_') and value is not None:
                    setattr(existing, key, value)
            lancamento = existing
        else:
            self.db.add(lancamento)
        
        self.db.commit()
        self.db.refresh(lancamento)
        return lancamento

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse de string de data."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return None
