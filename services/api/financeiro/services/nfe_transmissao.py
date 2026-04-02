"""
Transmissão de Notas Fiscais para SEFAZ

Implementa comunicação com WebService da SEFAZ para transmissão de NFe.
"""

from typing import Dict, Any, Optional, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetornoSEFAZ:
    """Classe para representar o retorno da SEFAZ"""
    status: int
    motivo: str
    numero_recibo: Optional[str] = None
    chave_acesso: Optional[str] = None
    numero_protocolo: Optional[str] = None
    data_autorizacao: Optional[datetime] = None
    xml_retorno: Optional[str] = None
    erros: Optional[List[str]] = None


class NFeTransmissaoService:
    """
    Serviço de transmissão de NFe para SEFAZ
    
    Implementa comunicação com WebService SOAP da SEFAZ
    conforme Manual Técnico da NFe.
    """
    
    # Versão do WebService
    VERSAO_NFE = "4.00"
    
    # URLs dos WebServices por estado (homologação)
    WS_URLS_HOMOLOGACAO = {
        "SP": {
            "recepcao_lote": "https://homologacao.nfe.fazenda.sp.gov.br/ws/nferecepcao4.asmx",
            "consulta_recibo": "https://homologacao.nfe.fazenda.sp.gov.br/ws/nferetreto4.asmx",
            "consulta_cadastro": "https://homologacao.nfe.fazenda.sp.gov.br/ws/cadconsultacadastro4.asmx",
            "consulta_nfe": "https://homologacao.nfe.fazenda.sp.gov.br/ws/nfeconsultaprotocolo4.asmx",
            "evento": "https://homologacao.nfe.fazenda.sp.gov.br/ws/recepcaoevento4.asmx",
        },
        "RS": {
            "recepcao_lote": "https://nfe-homologacao.sefazrs.gov.br/ws/NfeRecepcao/NfeRecepcao4.asmx",
            "consulta_recibo": "https://nfe-homologacao.sefazrs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao4.asmx",
        },
        "MG": {
            "recepcao_lote": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeRecepcao4",
            "consulta_recibo": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeRetRecepcao4",
        },
        # TODO: Adicionar todos os estados
    }
    
    # URLs de produção
    WS_URLS_PRODUCAO = {
        "SP": {
            "recepcao_lote": "https://nfe.fazenda.sp.gov.br/ws/nferecepcao4.asmx",
            "consulta_recibo": "https://nfe.fazenda.sp.gov.br/ws/nferetreto4.asmx",
        },
        # TODO: Adicionar todos os estados
    }
    
    def __init__(self, certificado_path: str, senha: str, uf: str = "SP", ambiente: str = "homologacao"):
        """
        Inicializa serviço de transmissão
        
        Args:
            certificado_path: Caminho do certificado digital
            senha: Senha do certificado
            uf: UF do emitente
            ambiente: "homologacao" ou "producao"
        """
        self.certificado_path = certificado_path
        self.senha = senha
        self.uf = uf.upper()
        self.ambiente = ambiente
        
        # Selecionar URLs baseado no ambiente
        self.urls = (
            self.WS_URLS_HOMOLOGACAO.get(uf, {})
            if ambiente == "homologacao"
            else self.WS_URLS_PRODUCAO.get(uf, {})
        )
        
        # Configurar sessão com retry
        self.session = self._configurar_sessao()
        
        logger.info(f"NFeTransmissaoService inicializado para {uf} ({ambiente})")
    
    def _configurar_sessao(self) -> requests.Session:
        """Configura sessão HTTP com retry e timeout"""
        session = requests.Session()
        
        # Configurar retry
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        
        # Timeout padrão (em segundos)
        session.timeout = 30
        
        return session
    
    def transmitir_lote(self, xml_lote: str) -> RetornoSEFAZ:
        """
        Transmite lote de NFe para SEFAZ
        
        Args:
            xml_lote: XML do lote de NFe (1-50 notas)
            
        Returns:
            RetornoSEFAZ com status e número do recibo
        """
        url = self.urls.get("recepcao_lote")
        
        if not url:
            raise ValueError(f"WebService de recepção não configurado para {self.uf}")
        
        logger.info(f"Transmitindo lote para {url}")
        
        # Montar envelope SOAP
        envelope = self._montar_envelope_soap(xml_lote, "NfeRecepcao")
        
        try:
            # Enviar requisição
            resposta = self.session.post(
                url,
                data=envelope,
                headers={
                    "Content-Type": "application/soap+xml; charset=utf-8",
                    "SOAPAction": "http://www.portalfiscal.inf.br/nfe/wsdl/NFeRecepcao4/nfeRecepcaoLote",
                },
                timeout=30
            )
            
            resposta.raise_for_status()
            
            # Parse do retorno
            retorno = self._processar_retorno_recepcao(resposta.text)
            
            logger.info(f"Lote transmitido. Recibo: {retorno.numero_recibo}")
            
            return retorno
            
        except requests.exceptions.Timeout:
            logger.error("Timeout na comunicação com SEFAZ")
            return RetornoSEFAZ(
                status=500,
                motivo="Timeout na comunicação com SEFAZ",
                erros=["Timeout após 30 segundos"]
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na comunicação: {str(e)}")
            return RetornoSEFAZ(
                status=500,
                motivo=f"Erro de comunicação: {str(e)}",
                erros=[str(e)]
            )
        except Exception as e:
            logger.error(f"Erro ao transmitir lote: {str(e)}")
            return RetornoSEFAZ(
                status=500,
                motivo=f"Erro ao transmitir: {str(e)}",
                erros=[str(e)]
            )
    
    def consultar_recibo(self, numero_recibo: str) -> RetornoSEFAZ:
        """
        Consulta situação do lote pelo número do recibo
        
        Args:
            numero_recibo: Número do recibo obtido na transmissão
            
        Returns:
            RetornoSEFAZ com status das notas
        """
        url = self.urls.get("consulta_recibo")
        
        if not url:
            raise ValueError(f"WebService de consulta não configurado para {self.uf}")
        
        logger.info(f"Consultando recibo: {numero_recibo}")
        
        # Montar XML de consulta
        xml_consulta = self._montar_xml_consulta(numero_recibo)
        
        # Montar envelope SOAP
        envelope = self._montar_envelope_soap(xml_consulta, "NfeRetRecepcao")
        
        try:
            resposta = self.session.post(
                url,
                data=envelope,
                headers={
                    "Content-Type": "application/soap+xml; charset=utf-8",
                    "SOAPAction": "http://www.portalfiscal.inf.br/nfe/wsdl/NFeRetRecepcao4/nfeRetRecepcaoLote",
                },
                timeout=30
            )
            
            resposta.raise_for_status()
            
            # Parse do retorno
            retorno = self._processar_retorno_consulta(resposta.text)
            
            return retorno
            
        except Exception as e:
            logger.error(f"Erro ao consultar recibo: {str(e)}")
            return RetornoSEFAZ(
                status=500,
                motivo=f"Erro ao consultar: {str(e)}",
                erros=[str(e)]
            )
    
    def _montar_envelope_soap(self, xml_conteudo: str, servico: str) -> str:
        """
        Monta envelope SOAP para comunicação
        
        Args:
            xml_conteudo: XML da NFe ou consulta
            servico: Nome do serviço (NfeRecepcao, NfeRetRecepcao)
            
        Returns:
            Envelope SOAP como string
        """
        envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                 xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                 xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"
                 xmlns:nfe="{self._get_namespace(servico)}">
  <soap12:Header>
    <nfeCabecMsg>
      <cUF>{self._get_codigo_uf(self.uf)}</cUF>
      <versaoDados>{self.VERSAO_NFE}</versaoDados>
    </nfeCabecMsg>
  </soap12:Header>
  <soap12:Body>
    <nfeDadosMsg>
      {xml_conteudo}
    </nfeDadosMsg>
  </soap12:Body>
</soap12:Envelope>"""
        
        return envelope
    
    def _get_namespace(self, servico: str) -> str:
        """Obtém namespace do serviço"""
        namespaces = {
            "NfeRecepcao": "http://www.portalfiscal.inf.br/nfe/wsdl/NFeRecepcao4",
            "NfeRetRecepcao": "http://www.portalfiscal.inf.br/nfe/wsdl/NFeRetRecepcao4",
            "NfeConsultaProtocolo": "http://www.portalfiscal.inf.br/nfe/wsdl/NFeConsultaProtocolo4",
            "RecepcaoEvento": "http://www.portalfiscal.inf.br/nfe/wsdl/RecepcaoEvento4",
        }
        return namespaces.get(servico, "")
    
    def _montar_xml_consulta(self, numero_recibo: str) -> str:
        """
        Monta XML de consulta de lote
        
        Args:
            numero_recibo: Número do recibo
            
        Returns:
            XML de consulta
        """
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<consReciNFe versao="{self.VERSAO_NFE}" xmlns="http://www.portalfiscal.inf.br/nfe">
  <tpAmb>{"2" if self.ambiente == "homologacao" else "1"}</tpAmb>
  <nRec>{numero_recibo}</nRec>
</consReciNFe>"""
        
        return xml
    
    def _processar_retorno_recepcao(self, xml_retorno: str) -> RetornoSEFAZ:
        """
        Processa retorno da recepção de lote
        
        Args:
            xml_retorno: XML de retorno da SEFAZ
            
        Returns:
            RetornoSEFAZ processado
        """
        try:
            root = ET.fromstring(xml_retorno)
            
            # Extrair namespace
            ns = {"ns": "http://www.portalfiscal.inf.br/nfe"}
            
            # Extrair dados do retorno
            ret_recibo = root.find(".//ns:retConsReciNFe", ns)
            
            if ret_recibo is None:
                # Tentar sem namespace
                ret_recibo = root.find(".//retConsReciNFe")
            
            status_elem = ret_recibo.find("cStat") if ret_recibo is not None else None
            motivo_elem = ret_recibo.find("xMotivo") if ret_recibo is not None else None
            
            status = int(status_elem.text) if status_elem is not None else 500
            motivo = motivo_elem.text if motivo_elem is not None else "Erro desconhecido"
            
            # Extrair número do recibo
            n_rec = ret_recibo.find("nRec") if ret_recibo is not None else None
            numero_recibo = n_rec.text if n_rec is not None else None
            
            return RetornoSEFAZ(
                status=status,
                motivo=motivo,
                numero_recibo=numero_recibo,
                xml_retorno=xml_retorno
            )
            
        except ET.ParseError as e:
            logger.error(f"Erro ao parsear retorno: {str(e)}")
            return RetornoSEFAZ(
                status=500,
                motivo=f"Erro ao parsear retorno: {str(e)}",
                xml_retorno=xml_retorno
            )
    
    def _processar_retorno_consulta(self, xml_retorno: str) -> RetornoSEFAZ:
        """
        Processa retorno da consulta de lote
        
        Args:
            xml_retorno: XML de retorno da SEFAZ
            
        Returns:
            RetornoSEFAZ processado
        """
        try:
            root = ET.fromstring(xml_retorno)
            
            # Extrair namespace
            ns = {"ns": "http://www.portalfiscal.inf.br/nfe"}
            
            ret_recibo = root.find(".//ns:retConsReciNFe", ns)
            
            if ret_recibo is None:
                ret_recibo = root.find(".//retConsReciNFe")
            
            status_elem = ret_recibo.find("cStat") if ret_recibo is not None else None
            motivo_elem = ret_recibo.find("xMotivo") if ret_recibo is not None else None
            
            status = int(status_elem.text) if status_elem is not None else 500
            motivo = motivo_elem.text if motivo_elem is not None else "Erro desconhecido"
            
            # Verificar se tem notas processadas
            prot_nfe = ret_recibo.find(".//protNFe") if ret_recibo is not None else None
            
            chave_acesso = None
            numero_protocolo = None
            data_autorizacao = None
            
            if prot_nfe is not None:
                # Nota processada
                inf_prot = prot_nfe.find("infProt")
                
                if inf_prot is not None:
                    ch_nfe = inf_prot.find("chNFe")
                    n_prot = inf_prot.find("nProt")
                    dh_recebto = inf_prot.find("dhRecbto")
                    
                    c_stat = inf_prot.find("cStat")
                    
                    # Verificar se foi autorizada
                    if c_stat is not None and c_stat.text == "100":
                        chave_acesso = ch_nfe.text if ch_nfe is not None else None
                        numero_protocolo = n_prot.text if n_prot is not None else None
                        
                        if dh_recebto is not None and dh_recebto.text:
                            data_autorizacao = datetime.fromisoformat(dh_recebto.text.replace('Z', '+00:00'))
            
            return RetornoSEFAZ(
                status=status,
                motivo=motivo,
                chave_acesso=chave_acesso,
                numero_protocolo=numero_protocolo,
                data_autorizacao=data_autorizacao,
                xml_retorno=xml_retorno
            )
            
        except Exception as e:
            logger.error(f"Erro ao processar retorno: {str(e)}")
            return RetornoSEFAZ(
                status=500,
                motivo=f"Erro ao processar retorno: {str(e)}",
                xml_retorno=xml_retorno
            )
    
    def _get_codigo_uf(self, uf: str) -> str:
        """Obtém código numérico da UF"""
        codigos = {
            "AC": "12", "AL": "27", "AP": "16", "AM": "13",
            "BA": "29", "CE": "23", "DF": "53", "ES": "32",
            "GO": "52", "MA": "21", "MT": "51", "MS": "50",
            "MG": "31", "PA": "15", "PB": "25", "PR": "41",
            "PE": "26", "PI": "22", "RJ": "33", "RN": "24",
            "RS": "43", "RO": "11", "RR": "14", "SC": "42",
            "SP": "35", "SE": "28", "TO": "17"
        }
        return codigos.get(uf.upper(), "35")
    
    def aguardar_processamento(
        self,
        numero_recibo: str,
        tentativas: int = 10,
        intervalo_segundos: int = 5
    ) -> RetornoSEFAZ:
        """
        Aguarda processamento do lote consultando repetidamente
        
        Args:
            numero_recibo: Número do recibo
            tentativas: Número máximo de tentativas
            intervalo_segundos: Intervalo entre consultas
            
        Returns:
            RetornoSEFAZ final
        """
        import time
        
        for i in range(tentativas):
            logger.info(f"Consulta {i+1}/{tentativas} - Recibo: {numero_recibo}")
            
            retorno = self.consultar_recibo(numero_recibo)
            
            # Status 105 = Em processamento
            # Status 104 = Lote processado
            if retorno.status == 104:
                logger.info(f"Lote processado. Status: {retorno.motivo}")
                return retorno
            elif retorno.status == 105:
                logger.info(f"Lote em processamento. Aguardando {intervalo_segundos}s...")
                time.sleep(intervalo_segundos)
            else:
                logger.warning(f"Status inesperado: {retorno.status} - {retorno.motivo}")
                return retorno
        
        logger.error(f"Timeout após {tentativas} tentativas")
        return RetornoSEFAZ(
            status=500,
            motivo="Timeout no processamento do lote",
            erros=[f"Lote não processado após {tentativas} consultas"]
        )


class NFeTransmissaoFactory:
    """Factory para criar instâncias de NFeTransmissaoService"""
    
    _instancias = {}
    
    @classmethod
    def get_transmissao(
        cls,
        tenant_id: str,
        certificado_path: str,
        senha: str,
        uf: str,
        ambiente: str = "homologacao"
    ) -> NFeTransmissaoService:
        """Obtém ou cria instância de transmissão"""
        chave = f"{tenant_id}_{uf}_{ambiente}"
        
        if chave not in cls._instancias:
            cls._instancias[chave] = NFeTransmissaoService(
                certificado_path=certificado_path,
                senha=senha,
                uf=uf,
                ambiente=ambiente
            )
        
        return cls._instancias[chave]
