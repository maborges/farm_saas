"""
Integração com WebService do eSocial

Implementa comunicação SOAP com o WebService do eSocial
para envio e consulta de eventos.
"""

from typing import Dict, Any, Optional, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
from dataclasses import dataclass
import hashlib
import base64

logger = logging.getLogger(__name__)


@dataclass
class RetornoESocial:
    """Classe para representar o retorno do eSocial"""
    status: str  # 'SUCESSO', 'ERRO', 'PROCESSAMENTO'
    codigo: str
    descricao: str
    numero_recibo: Optional[str] = None
    hash_retorno: Optional[str] = None
    xml_retorno: Optional[str] = None
    erros: Optional[List[str]] = None


class ESocialWebService:
    """
    WebService do eSocial
    
    Implementa comunicação SOAP com o eSocial conforme
    Manual de Orientação do WebService.
    """
    
    # URLs do eSocial (Produção e Homologação)
    URLS = {
        'producao': 'https://servicos.esocial.gov.br/servicos/empregador/WS/RECEBERLOTE',
        'homologacao': 'https://preprodbase.esocial.gov.br/servicos/empregador/WS/RECEBERLOTE',
        'consulta': {
            'producao': 'https://servicos.esocial.gov.br/servicos/empregador/WS/CONSULTARLOTE',
            'homologacao': 'https://preprodbase.esocial.gov.br/servicos/empregador/WS/CONSULTARLOTE',
        }
    }
    
    # Namespace SOAP
    NAMESPACE_SOAP = "http://www.w3.org/2003/05/soap-envelope"
    NAMESPACE_ESOCIAL = "http://www.esocial.gov.br/schema/lote/eventos/v1_0_0"
    
    def __init__(self, certificado_path: str, senha: str, ambiente: str = 'homologacao'):
        """
        Inicializa o WebService do eSocial
        
        Args:
            certificado_path: Caminho do certificado digital A1
            senha: Senha do certificado
            ambiente: 'producao' ou 'homologacao'
        """
        self.certificado_path = certificado_path
        self.senha = senha
        self.ambiente = ambiente
        self.url_recepcao = self.URLS[ambiente]
        self.url_consulta = self.URLS[ambiente]['consulta']
        
        # Configurar sessão com retry
        self.session = self._configurar_sessao()
        
        logger.info(f"ESocialWebService inicializado para {ambiente}")
    
    def _configurar_sessao(self) -> requests.Session:
        """Configura sessão HTTP com retry e certificados"""
        session = requests.Session()
        
        # Configurar retry para falhas temporárias
        retry = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        
        # Configurar timeout padrão (60 segundos)
        session.timeout = 60
        
        # TODO: Configurar certificado digital para autenticação mútua
        # session.cert = (certificado_path, senha)
        
        return session
    
    def enviar_lote(self, eventos: List[str]) -> RetornoESocial:
        """
        Envia lote de eventos para o eSocial
        
        Args:
            eventos: Lista de XMLs de eventos (já assinados)
            
        Returns:
            RetornoESocial com status do envio
        """
        logger.info(f"Enviando lote com {len(eventos)} eventos para eSocial")
        
        # Montar XML do lote
        xml_lote = self._montar_xml_lote(eventos)
        
        # Montar envelope SOAP
        envelope = self._montar_envelope_soap(xml_lote)
        
        try:
            # Enviar requisição
            resposta = self.session.post(
                self.url_recepcao,
                data=envelope,
                headers={
                    "Content-Type": "application/soap+xml; charset=utf-8",
                    "SOAPAction": "http://www.esocial.gov.br/servicos/empregador/WS/RECEBERLOTE/ReceberLote",
                },
                timeout=60
            )
            
            resposta.raise_for_status()
            
            # Processar retorno
            retorno = self._processar_retorno_recepcao(resposta.text)
            
            logger.info(f"Lote enviado. Recibo: {retorno.numero_recibo}")
            
            return retorno
            
        except requests.exceptions.Timeout:
            logger.error("Timeout na comunicação com eSocial")
            return RetornoESocial(
                status='ERRO',
                codigo='TIMEOUT',
                descricao='Timeout na comunicação com eSocial (60s)',
                erros=['Timeout após 60 segundos']
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na comunicação: {str(e)}")
            return RetornoESocial(
                status='ERRO',
                codigo='COMUNICACAO',
                descricao=f'Erro de comunicação: {str(e)}',
                erros=[str(e)]
            )
        except Exception as e:
            logger.error(f"Erro ao enviar lote: {str(e)}")
            return RetornoESocial(
                status='ERRO',
                codigo='ERRO_GERAL',
                descricao=f'Erro ao enviar lote: {str(e)}',
                erros=[str(e)]
            )
    
    def consultar_lote(self, numero_recibo: str) -> RetornoESocial:
        """
        Consulta situação do lote pelo número do recibo
        
        Args:
            numero_recibo: Número do recibo obtido no envio
            
        Returns:
            RetornoESocial com situação do processamento
        """
        logger.info(f"Consultando lote: {numero_recibo}")
        
        # Montar XML de consulta
        xml_consulta = self._montar_xml_consulta(numero_recibo)
        
        # Montar envelope SOAP
        envelope = self._montar_envelope_soap_consulta(xml_consulta)
        
        try:
            resposta = self.session.post(
                self.url_consulta,
                data=envelope,
                headers={
                    "Content-Type": "application/soap+xml; charset=utf-8",
                    "SOAPAction": "http://www.esocial.gov.br/servicos/empregador/WS/CONSULTARLOTE/ConsultarLote",
                },
                timeout=60
            )
            
            resposta.raise_for_status()
            
            # Processar retorno
            retorno = self._processar_retorno_consulta(resposta.text)
            
            return retorno
            
        except Exception as e:
            logger.error(f"Erro ao consultar lote: {str(e)}")
            return RetornoESocial(
                status='ERRO',
                codigo='ERRO_CONSULTA',
                descricao=f'Erro ao consultar: {str(e)}',
                erros=[str(e)]
            )
    
    def _montar_xml_lote(self, eventos: List[str]) -> str:
        """
        Monta XML do lote de eventos
        
        Args:
            eventos: Lista de XMLs de eventos
            
        Returns:
            XML do lote
        """
        # Calcular hash do lote (SHA256)
        conteudo = ''.join(eventos)
        hash_lote = hashlib.sha256(conteudo.encode()).hexdigest()
        
        # Estrutura do lote
        raiz = ET.Element("{http://www.esocial.gov.br/schema/lote/eventos/v1_0_0}eSocial")
        envio_lote = ET.SubElement(raiz, "envioLoteEventos")
        
        # Número do lote (sequencial)
        numero_lote = datetime.now().strftime("%Y%m%d%H%M%S")
        ET.SubElement(envio_lote, "numeroLote").text = numero_lote
        
        # CNPJ do empregador
        # TODO: Obter CNPJ do tenant
        ET.SubElement(envio_lote, "cnpjEmpregador").text = "00000000000000"
        
        # Tipo de evento (1=Original, 2=Retificação)
        ET.SubElement(envio_lote, "tpEmis").text = "1"
        
        # Informações do remetente
        informacoes_remetente = ET.SubElement(envio_lote, "informacoesRemetente")
        ET.SubElement(informacoes_remetente, "ideRemetente").text = "1"  # Pessoa Física
        ET.SubElement(informacoes_remetente, "nrInscRemetente").text = "00000000000000"
        
        # Eventos
        eventos_xml = ET.SubElement(envio_lote, "eventos")
        
        for evento_xml in eventos:
            # Parse do evento e adicionar ao lote
            evento_elem = ET.fromstring(evento_xml)
            eventos_xml.append(evento_elem)
        
        # Gerar XML formatado
        xml_str = ET.tostring(raiz, encoding="unicode")
        
        # Pretty print
        from xml.dom import minidom
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    
    def _montar_envelope_soap(self, xml_conteudo: str) -> str:
        """
        Monta envelope SOAP para envio
        
        Args:
            xml_conteudo: XML do lote
            
        Returns:
            Envelope SOAP
        """
        envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                 xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                 xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Header/>
  <soap12:Body>
    <ReceberLote xmlns="http://www.esocial.gov.br/servicos/empregador/WS/RECEBERLOTE">
      <xml>
        {xml_conteudo}
      </xml>
    </ReceberLote>
  </soap12:Body>
</soap12:Envelope>"""
        
        return envelope
    
    def _montar_xml_consulta(self, numero_recibo: str) -> str:
        """
        Monta XML de consulta de lote
        
        Args:
            numero_recibo: Número do recibo
            
        Returns:
            XML de consulta
        """
        raiz = ET.Element("{http://www.esocial.gov.br/schema/lote/eventos/v1_0_0}eSocial")
        consulta_lote = ET.SubElement(raiz, "consultaLoteEventos")
        
        # CNPJ do empregador
        ET.SubElement(consulta_lote, "cnpjEmpregador").text = "00000000000000"
        
        # Número do recibo
        ET.SubElement(consulta_lote, "numeroRecibo").text = numero_recibo
        
        # Gerar XML
        xml_str = ET.tostring(raiz, encoding="unicode")
        
        from xml.dom import minidom
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    
    def _montar_envelope_soap_consulta(self, xml_conteudo: str) -> str:
        """
        Monta envelope SOAP para consulta
        
        Args:
            xml_conteudo: XML de consulta
            
        Returns:
            Envelope SOAP
        """
        envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                 xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                 xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Header/>
  <soap12:Body>
    <ConsultarLote xmlns="http://www.esocial.gov.br/servicos/empregador/WS/CONSULTARLOTE">
      <xml>
        {xml_conteudo}
      </xml>
    </ConsultarLote>
  </soap12:Body>
</soap12:Envelope>"""
        
        return envelope
    
    def _processar_retorno_recepcao(self, xml_retorno: str) -> RetornoESocial:
        """
        Processa retorno da recepção de lote
        
        Args:
            xml_retorno: XML de retorno do eSocial
            
        Returns:
            RetornoESocial processado
        """
        try:
            root = ET.fromstring(xml_retorno)
            
            # Extrair namespace
            ns = {"ns": "http://www.esocial.gov.br/servicos/empregador/WS/RECEBERLOTE"}
            
            # Buscar elemento de resposta
            resposta = root.find(".//ns:ReceberLoteResponse", ns)
            
            if resposta is None:
                # Tentar sem namespace
                resposta = root.find(".//ReceberLoteResponse")
            
            if resposta is None:
                # Tentar encontrar elemento de erro no SOAP
                fault = root.find(".//{http://www.w3.org/2003/05/soap-envelope}Fault")
                if fault is not None:
                    fault_text = fault.find(".//{http://www.w3.org/2003/05/soap-envelope}Text")
                    return RetornoESocial(
                        status='ERRO',
                        codigo='SOAP_FAULT',
                        descricao=fault_text.text if fault_text else 'SOAP Fault',
                        erros=[fault_text.text if fault_text else 'SOAP Fault']
                    )
                
                return RetornoESocial(
                    status='ERRO',
                    codigo='XML_INVALIDO',
                    descricao='Não foi possível parsear retorno',
                    xml_retorno=xml_retorno
                )
            
            # Extrair número do recibo
            numero_recibo_elem = resposta.find(".//numeroRecibo")
            numero_recibo = numero_recibo_elem.text if numero_recibo_elem is not None else None
            
            # Extrair hash
            hash_elem = resposta.find(".//hash")
            hash_retorno = hash_elem.text if hash_elem is not None else None
            
            return RetornoESocial(
                status='SUCESSO',
                codigo='200',
                descricao='Lote recebido com sucesso',
                numero_recibo=numero_recibo,
                hash_retorno=hash_retorno,
                xml_retorno=xml_retorno
            )
            
        except ET.ParseError as e:
            logger.error(f"Erro ao parsear retorno: {str(e)}")
            return RetornoESocial(
                status='ERRO',
                codigo='PARSE_ERROR',
                descricao=f'Erro ao parsear retorno: {str(e)}',
                xml_retorno=xml_retorno
            )
    
    def _processar_retorno_consulta(self, xml_retorno: str) -> RetornoESocial:
        """
        Processa retorno da consulta de lote
        
        Args:
            xml_retorno: XML de retorno do eSocial
            
        Returns:
            RetornoESocial processado
        """
        try:
            root = ET.fromstring(xml_retorno)
            
            # Extrair informações do processamento
            # TODO: Implementar parse completo do retorno
            
            # Buscar status de processamento
            status_elem = root.find(".//status")
            
            if status_elem is not None:
                status_text = status_elem.text
                
                if status_text == 'PROCESSADO':
                    return RetornoESocial(
                        status='SUCESSO',
                        codigo='200',
                        descricao='Lote processado com sucesso',
                        xml_retorno=xml_retorno
                    )
                elif status_text == 'EM_PROCESSAMENTO':
                    return RetornoESocial(
                        status='PROCESSAMENTO',
                        codigo='100',
                        descricao='Lote em processamento',
                        xml_retorno=xml_retorno
                    )
                else:
                    return RetornoESocial(
                        status='ERRO',
                        codigo='500',
                        descricao=f'Status: {status_text}',
                        xml_retorno=xml_retorno
                    )
            
            return RetornoESocial(
                status='SUCESSO',
                codigo='200',
                descricao='Consulta realizada',
                xml_retorno=xml_retorno
            )
            
        except Exception as e:
            logger.error(f"Erro ao processar retorno: {str(e)}")
            return RetornoESocial(
                status='ERRO',
                codigo='ERRO_PROCESSAMENTO',
                descricao=f'Erro ao processar: {str(e)}',
                xml_retorno=xml_retorno
            )
    
    def aguardar_processamento(
        self,
        numero_recibo: str,
        tentativas: int = 20,
        intervalo_segundos: int = 10
    ) -> RetornoESocial:
        """
        Aguarda processamento do lote consultando repetidamente
        
        Args:
            numero_recibo: Número do recibo
            tentativas: Número máximo de tentativas
            intervalo_segundos: Intervalo entre consultas
            
        Returns:
            RetornoESocial final
        """
        import time
        
        for i in range(tentativas):
            logger.info(f"Consulta {i+1}/{tentativas} - Recibo: {numero_recibo}")
            
            retorno = self.consultar_lote(numero_recibo)
            
            # Status 100 = Em processamento
            # Status 200 = Processado
            if retorno.status == 'SUCESSO':
                logger.info(f"Lote processado. Status: {retorno.descricao}")
                return retorno
            elif retorno.status == 'PROCESSAMENTO':
                logger.info(f"Lote em processamento. Aguardando {intervalo_segundos}s...")
                time.sleep(intervalo_segundos)
            else:
                logger.warning(f"Status inesperado: {retorno.status} - {retorno.descricao}")
                return retorno
        
        logger.error(f"Timeout após {tentativas} tentativas")
        return RetornoESocial(
            status='ERRO',
            codigo='TIMEOUT_PROCESSAMENTO',
            descricao='Timeout no processamento do lote',
            erros=[f'Lote não processado após {tentativas} consultas']
        )


class ESocialService:
    """
    Serviço de alto nível para integração com eSocial
    
    Combina geração de XML e transmissão.
    """
    
    def __init__(
        self,
        certificado_path: str,
        senha: str,
        cnpj_empregador: str,
        ambiente: str = 'homologacao'
    ):
        self.certificado_path = certificado_path
        self.senha = senha
        self.cnpj_empregador = cnpj_empregador
        self.ambiente = ambiente
        
        self.webservice = ESocialWebService(certificado_path, senha, ambiente)
    
    def enviar_admissao(self, colaborador: Dict[str, Any]) -> RetornoESocial:
        """
        Envia evento S-2200 (Admissão) para eSocial
        
        Args:
            colaborador: Dados do colaborador
            
        Returns:
            RetornoESocial
        """
        from .esocial_xml import ESocialXMLGenerator
        
        # Gerar XML do S-2200
        gerador = ESocialXMLGenerator(self.certificado_path, self.senha)
        xml_s2200 = gerador.gerar_s2200(colaborador)
        
        # Enviar para eSocial
        retorno = self.webservice.enviar_lote([xml_s2200])
        
        logger.info(f"Admissão enviada para {colaborador.get('nome')}. Recibo: {retorno.numero_recibo}")
        
        return retorno
    
    def enviar_remuneracao(self, remuneracoes: List[Dict[str, Any]]) -> RetornoESocial:
        """
        Envia evento S-1200 (Remuneração) para eSocial
        
        Args:
            remuneracoes: Lista de remunerações
            
        Returns:
            RetornoESocial
        """
        from .esocial_xml import ESocialXMLGenerator
        
        # Gerar XML do S-1200
        gerador = ESocialXMLGenerator(self.certificado_path, self.senha)
        xml_s1200 = gerador.gerar_s1200(remuneracoes)
        
        # Enviar para eSocial
        retorno = self.webservice.enviar_lote([xml_s1200])
        
        return retorno
    
    def enviar_desligamento(self, desligamento: Dict[str, Any]) -> RetornoESocial:
        """
        Envia evento S-2299 (Desligamento) para eSocial
        
        Args:
            desligamento: Dados do desligamento
            
        Returns:
            RetornoESocial
        """
        from .esocial_xml import ESocialXMLGenerator
        
        # Gerar XML do S-2299
        gerador = ESocialXMLGenerator(self.certificado_path, self.senha)
        xml_s2299 = gerador.gerar_s2299(desligamento)
        
        # Enviar para eSocial
        retorno = self.webservice.enviar_lote([xml_s2299])
        
        return retorno
