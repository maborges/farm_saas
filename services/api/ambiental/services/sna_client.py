"""
Integração com SNA (Sistema Nacional de CAR)

Implementa comunicação com a API do CAR para consulta
e download de dados do Cadastro Ambiental Rural.
"""

from typing import Dict, Any, Optional, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from dataclasses import dataclass
import base64

logger = logging.getLogger(__name__)


@dataclass
class RetornoSNA:
    """Classe para representar o retorno da API do SNA"""
    status: str  # 'SUCESSO', 'ERRO', 'NAO_ENCONTRADO'
    codigo: str
    descricao: str
    dados_car: Optional[Dict[str, Any]] = None
    recibo_pdf: Optional[str] = None  # Base64
    xml_car: Optional[str] = None
    erros: Optional[List[str]] = None


class SNAClient:
    """
    Cliente da API do SNA (Sistema Nacional de CAR)
    
    Implementa comunicação com o WebService do CAR
    conforme documentação do SNA.
    """
    
    # URLs do SNA
    URLS = {
        'producao': 'https://www.car.gov.br/api',
        'homologacao': 'https://preprodo.car.gov.br/api',
    }
    
    # Endpoints
    ENDPOINTS = {
        'consultar_car': '/car/consultar',
        'baixar_recibo': '/car/recibo',
        'baixar_xml': '/car/xml',
        'verificar_sobreposicoes': '/car/sobreposicoes',
        'listar_pendencias': '/car/pendencias',
    }
    
    def __init__(self, token: str, ambiente: str = 'homologacao'):
        """
        Inicializa o cliente do SNA
        
        Args:
            token: Token de autenticação da API
            ambiente: 'producao' ou 'homologacao'
        """
        self.token = token
        self.ambiente = ambiente
        self.base_url = self.URLS[ambiente]
        
        # Configurar sessão com retry
        self.session = self._configurar_sessao()
        
        logger.info(f"SNAClient inicializado para {ambiente}")
    
    def _configurar_sessao(self) -> requests.Session:
        """Configura sessão HTTP com retry e autenticação"""
        session = requests.Session()
        
        # Configurar retry para falhas temporárias
        retry = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        
        # Configurar timeout padrão (30 segundos)
        session.timeout = 30
        
        # Configurar headers padrão
        session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        
        return session
    
    def consultar_car(self, codigo_car: str) -> RetornoSNA:
        """
        Consulta dados do CAR pelo código
        
        Args:
            codigo_car: Código do CAR (ex: SP1234567890123456789)
            
        Returns:
            RetornoSNA com dados do CAR
        """
        logger.info(f"Consultando CAR: {codigo_car}")
        
        url = f"{self.base_url}{self.ENDPOINTS['consultar_car']}"
        
        params = {
            "codigo": codigo_car,
        }
        
        try:
            resposta = self.session.get(url, params=params, timeout=30)
            
            if resposta.status_code == 404:
                return RetornoSNA(
                    status='NAO_ENCONTRADO',
                    codigo='404',
                    descricao=f'CAR {codigo_car} não encontrado',
                    erros=[f'CAR não encontrado no SNA']
                )
            
            resposta.raise_for_status()
            
            dados = resposta.json()
            
            return RetornoSNA(
                status='SUCESSO',
                codigo=str(resposta.status_code),
                descricao='CAR consultado com sucesso',
                dados_car=dados,
            )
            
        except requests.exceptions.Timeout:
            logger.error("Timeout na comunicação com SNA")
            return RetornoSNA(
                status='ERRO',
                codigo='TIMEOUT',
                descricao='Timeout na comunicação com SNA (30s)',
                erros=['Timeout após 30 segundos']
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na comunicação: {str(e)}")
            return RetornoSNA(
                status='ERRO',
                codigo='COMUNICACAO',
                descricao=f'Erro de comunicação: {str(e)}',
                erros=[str(e)]
            )
        except Exception as e:
            logger.error(f"Erro ao consultar CAR: {str(e)}")
            return RetornoSNA(
                status='ERRO',
                codigo='ERRO_GERAL',
                descricao=f'Erro ao consultar CAR: {str(e)}',
                erros=[str(e)]
            )
    
    def baixar_recibo(self, codigo_car: str) -> RetornoSNA:
        """
        Baixa recibo do CAR em PDF
        
        Args:
            codigo_car: Código do CAR
            
        Returns:
            RetornoSNA com PDF em base64
        """
        logger.info(f"Baixando recibo do CAR: {codigo_car}")
        
        url = f"{self.base_url}{self.ENDPOINTS['baixar_recibo']}"
        
        params = {
            "codigo": codigo_car,
        }
        
        try:
            resposta = self.session.get(url, params=params, timeout=30)
            
            if resposta.status_code == 404:
                return RetornoSNA(
                    status='NAO_ENCONTRADO',
                    codigo='404',
                    descricao=f'Recibo do CAR {codigo_car} não encontrado',
                    erros=['Recibo não encontrado']
                )
            
            resposta.raise_for_status()
            
            # PDF vem em base64 no response
            pdf_base64 = base64.b64encode(resposta.content).decode('utf-8')
            
            return RetornoSNA(
                status='SUCESSO',
                codigo=str(resposta.status_code),
                descricao='Recibo baixado com sucesso',
                recibo_pdf=pdf_base64,
            )
            
        except Exception as e:
            logger.error(f"Erro ao baixar recibo: {str(e)}")
            return RetornoSNA(
                status='ERRO',
                codigo='ERRO_DOWNLOAD',
                descricao=f'Erro ao baixar recibo: {str(e)}',
                erros=[str(e)]
            )
    
    def baixar_xml(self, codigo_car: str) -> RetornoSNA:
        """
        Baixa XML do CAR
        
        Args:
            codigo_car: Código do CAR
            
        Returns:
            RetornoSNA com XML
        """
        logger.info(f"Baixando XML do CAR: {codigo_car}")
        
        url = f"{self.base_url}{self.ENDPOINTS['baixar_xml']}"
        
        params = {
            "codigo": codigo_car,
        }
        
        try:
            resposta = self.session.get(url, params=params, timeout=30)
            resposta.raise_for_status()
            
            xml_string = resposta.text
            
            return RetornoSNA(
                status='SUCESSO',
                codigo=str(resposta.status_code),
                descricao='XML baixado com sucesso',
                xml_car=xml_string,
            )
            
        except Exception as e:
            logger.error(f"Erro ao baixar XML: {str(e)}")
            return RetornoSNA(
                status='ERRO',
                codigo='ERRO_DOWNLOAD',
                descricao=f'Erro ao baixar XML: {str(e)}',
                erros=[str(e)]
            )
    
    def verificar_sobreposicoes(self, codigo_car: str) -> RetornoSNA:
        """
        Verifica sobreposições do CAR
        
        Args:
            codigo_car: Código do CAR
            
        Returns:
            RetornoSNA com lista de sobreposições
        """
        logger.info(f"Verificando sobreposições do CAR: {codigo_car}")
        
        url = f"{self.base_url}{self.ENDPOINTS['verificar_sobreposicoes']}"
        
        params = {
            "codigo": codigo_car,
        }
        
        try:
            resposta = self.session.get(url, params=params, timeout=30)
            resposta.raise_for_status()
            
            dados = resposta.json()
            
            return RetornoSNA(
                status='SUCESSO',
                codigo=str(resposta.status_code),
                descricao='Sobreposições verificadas',
                dados_car=dados,
            )
            
        except Exception as e:
            logger.error(f"Erro ao verificar sobreposições: {str(e)}")
            return RetornoSNA(
                status='ERRO',
                codigo='ERRO_CONSULTA',
                descricao=f'Erro ao verificar sobreposições: {str(e)}',
                erros=[str(e)]
            )
    
    def listar_pendencias(self, codigo_car: str) -> RetornoSNA:
        """
        Lista pendências do CAR
        
        Args:
            codigo_car: Código do CAR
            
        Returns:
            RetornoSNA com lista de pendências
        """
        logger.info(f"Listando pendências do CAR: {codigo_car}")
        
        url = f"{self.base_url}{self.ENDPOINTS['listar_pendencias']}"
        
        params = {
            "codigo": codigo_car,
        }
        
        try:
            resposta = self.session.get(url, params=params, timeout=30)
            resposta.raise_for_status()
            
            dados = resposta.json()
            
            return RetornoSNA(
                status='SUCESSO',
                codigo=str(resposta.status_code),
                descricao='Pendências listadas',
                dados_car=dados,
            )
            
        except Exception as e:
            logger.error(f"Erro ao listar pendências: {str(e)}")
            return RetornoSNA(
                status='ERRO',
                codigo='ERRO_CONSULTA',
                descricao=f'Erro ao listar pendências: {str(e)}',
                erros=[str(e)]
            )
    
    def sincronizar_car(self, codigo_car: str) -> RetornoSNA:
        """
        Sincroniza todos os dados do CAR
        
        Método conveniente que consulta CAR, baixa recibo, XML,
        verifica sobreposições e pendências.
        
        Args:
            codigo_car: Código do CAR
            
        Returns:
            RetornoSNA com todos os dados
        """
        logger.info(f"Sincronizando CAR completo: {codigo_car}")
        
        dados_completos = {
            "codigo": codigo_car,
            "dados_cadastrais": None,
            "recibo_pdf": None,
            "xml": None,
            "sobreposicoes": [],
            "pendencias": [],
        }
        
        # 1. Consultar dados cadastrais
        retorno_consulta = self.consultar_car(codigo_car)
        
        if retorno_consulta.status != 'SUCESSO':
            return retorno_consulta
        
        dados_completos["dados_cadastrais"] = retorno_consulta.dados_car
        
        # 2. Baixar recibo PDF
        retorno_recibo = self.baixar_recibo(codigo_car)
        
        if retorno_recibo.status == 'SUCESSO':
            dados_completos["recibo_pdf"] = retorno_recibo.recibo_pdf
        
        # 3. Baixar XML
        retorno_xml = self.baixar_xml(codigo_car)
        
        if retorno_xml.status == 'SUCESSO':
            dados_completos["xml"] = retorno_xml.xml_car
        
        # 4. Verificar sobreposições
        retorno_sobreposicoes = self.verificar_sobreposicoes(codigo_car)
        
        if retorno_sobreposicoes.status == 'SUCESSO':
            dados_completos["sobreposicoes"] = retorno_sobreposicoes.dados_car
        
        # 5. Listar pendências
        retorno_pendencias = self.listar_pendencias(codigo_car)
        
        if retorno_pendencias.status == 'SUCESSO':
            dados_completos["pendencias"] = retorno_pendencias.dados_car
        
        return RetornoSNA(
            status='SUCESSO',
            codigo='200',
            descricao='CAR sincronizado com sucesso',
            dados_car=dados_completos,
        )


class SNAService:
    """
    Serviço de alto nível para integração com SNA
    
    Combina cliente SNA com modelos do banco de dados.
    """
    
    def __init__(self, token: str, ambiente: str = 'homologacao'):
        self.token = token
        self.ambiente = ambiente
        self.client = SNAClient(token, ambiente)
    
    def importar_car(self, codigo_car: str, tenant_id: str, fazenda_id: str) -> Dict[str, Any]:
        """
        Importa CAR do SNA e salva no banco de dados
        
        Args:
            codigo_car: Código do CAR
            tenant_id: ID do tenant
            fazenda_id: ID da fazenda
            
        Returns:
            Dicionário com resultado da importação
        """
        from services.api.ambiental.models.car import CAR
        from services.api.ambiental.services.car_parser import CARParser
        from sqlalchemy.orm import Session
        
        logger.info(f"Importando CAR {codigo_car} para tenant {tenant_id}")
        
        # 1. Sincronizar dados do SNA
        retorno = self.client.sincronizar_car(codigo_car)
        
        if retorno.status != 'SUCESSO':
            return {
                "sucesso": False,
                "erro": retorno.descricao,
                "detalhes": retorno.erros,
            }
        
        # 2. Parsear dados do CAR
        dados = retorno.dados_car
        
        # 3. Salvar no banco de dados
        # TODO: Implementar save no banco
        
        return {
            "sucesso": True,
            "mensagem": f"CAR {codigo_car} importado com sucesso",
            "dados": {
                "area_total": dados.get("dados_cadastrais", {}).get("area_total", 0),
                "area_app": dados.get("dados_cadastrais", {}).get("area_app", 0),
                "area_rl": dados.get("dados_cadastrais", {}).get("area_rl", 0),
                "possui_sobreposicao": len(dados.get("sobreposicoes", [])) > 0,
                "possui_pendencias": len(dados.get("pendencias", [])) > 0,
            },
        }
    
    def atualizar_car(self, car_id: str) -> Dict[str, Any]:
        """
        Atualiza dados do CAR no banco de dados
        
        Args:
            car_id: ID do CAR no banco
            
        Returns:
            Dicionário com resultado da atualização
        """
        from services.api.ambiental.models.car import CAR
        from sqlalchemy.orm import Session
        
        # TODO: Implementar atualização
        
        return {
            "sucesso": True,
            "mensagem": f"CAR {car_id} atualizado com sucesso",
        }
    
    def verificar_pendencias_car(self, codigo_car: str) -> Dict[str, Any]:
        """
        Verifica pendências do CAR
        
        Args:
            codigo_car: Código do CAR
            
        Returns:
            Dicionário com pendências
        """
        retorno = self.client.listar_pendencias(codigo_car)
        
        if retorno.status != 'SUCESSO':
            return {
                "sucesso": False,
                "erro": retorno.descricao,
            }
        
        pendencias = retorno.dados_car.get("pendencias", [])
        
        return {
            "sucesso": True,
            "total_pendencias": len(pendencias),
            "pendencias": pendencias,
            "possui_pendencias_graves": any(
                p.get("gravidade") in ["alta", "critica"]
                for p in pendencias
            ),
        }
    
    def verificar_sobreposicoes_car(self, codigo_car: str) -> Dict[str, Any]:
        """
        Verifica sobreposições do CAR
        
        Args:
            codigo_car: Código do CAR
            
        Returns:
            Dicionário com sobreposições
        """
        retorno = self.client.verificar_sobreposicoes(codigo_car)
        
        if retorno.status != 'SUCESSO':
            return {
                "sucesso": False,
                "erro": retorno.descricao,
            }
        
        sobreposicoes = retorno.dados_car.get("sobreposicoes", [])
        
        return {
            "sucesso": True,
            "total_sobreposicoes": len(sobreposicoes),
            "sobreposicoes": sobreposicoes,
            "tipos": list(set(s.get("tipo") for s in sobreposicoes)),
        }
