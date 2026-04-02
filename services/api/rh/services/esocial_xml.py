"""
Gerador de XML para eSocial

Gera XML dos eventos do eSocial conforme layout 2.4.02.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import hashlib
import base64
import logging

logger = logging.getLogger(__name__)


class ESocialXMLGenerator:
    """
    Gerador de XML para eSocial
    
    Implementa geração de eventos conforme Manual de Orientação do eSocial.
    Layout 2.4.02
    """
    
    # Versão do layout
    VERSAO_LAYOUT = "2.4.02"
    
    # Namespace
    NAMESPACE_ESOCIAL = "http://www.esocial.gov.br/schema/evt/evtAdmissao/v02_04_02"
    
    def __init__(self, certificado_path: str, senha: str):
        """
        Inicializa com certificado digital
        
        Args:
            certificado_path: Caminho do certificado A1
            senha: Senha do certificado
        """
        self.certificado_path = certificado_path
        self.senha = senha
        self.root = None
    
    def gerar_s2200(self, colaborador: Dict[str, Any]) -> str:
        """
        Gera XML do evento S-2200 (Cadastramento Inicial do Vínculo)
        
        Args:
            colaborador: Dados do colaborador
            
        Returns:
            XML assinado como string
        """
        # Estrutura raiz
        self.root = ET.Element("eSocial", {
            "xmlns": "http://www.esocial.gov.br/schema/evt/evtAdmissao/v02_04_02"
        })
        
        # Evento
        evt_admissao = ET.SubElement(self.root, "evtAdmissao", {
            "Id": f"ID{self._gerar_id(colaborador)}"
        })
        
        # Preencher elementos
        self._preparar_identificacao(evt_admissao, colaborador)
        self._preparar_trabalhador(evt_admissao, colaborador)
        self._preparar_vinculo(evt_admissao, colaborador)
        self._preparar_remuneracao(evt_admissao, colaborador)
        self._preparar_informacoes_adicionais(evt_admissao, colaborador)
        
        # Gerar XML formatado
        xml_str = self._formatar_xml()
        
        # Assinar XML
        xml_assinado = self._assinar_xml(xml_str)
        
        logger.info(f"XML S-2200 gerado para {colaborador.get('nome')}")
        
        return xml_assinado
    
    def _gerar_id(self, colaborador: Dict[str, Any]) -> str:
        """Gera ID único para o evento"""
        # ID = ID + CNPJ do empregador + código do evento + timestamp
        cnpj = colaborador.get("cnpj_empregador", "00000000000000")
        codigo = "S2200"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Hash único
        conteudo = f"{cnpj}{codigo}{timestamp}{colaborador.get('cpf', '')}"
        hash_id = hashlib.sha256(conteudo.encode()).hexdigest()[:30]
        
        return f"{cnpj}{codigo}{hash_id}"
    
    def _preparar_identificacao(self, evt: ET.Element, colaborador: Dict[str, Any]):
        """Prepara elemento ide (identificação)"""
        ide = ET.SubElement(evt, "ideEvento")
        
        # Tipo de ambiente (1=Produção, 2=Homologação)
        ET.SubElement(ide, "tpAmb").text = colaborador.get("ambiente", "2")
        
        # Processo de emissão
        ET.SubElement(ide, "procEmi").text = "1"  # 1=Aplicativo do contribuinte
        
        # Versão do processo
        ET.SubElement(ide, "verProc").text = "1.0.0"
    
    def _preparar_trabalhador(self, evt: ET.Element, colaborador: Dict[str, Any]):
        """Prepara elemento trabalhador"""
        trabalhador = ET.SubElement(evt, "trabalhador")
        
        # Nome
        ET.SubElement(trabalhador, "nmTrab").text = colaborador.get("nome", "")
        
        # Sexo (M/F)
        ET.SubElement(trabalhador, "sexo").text = colaborador.get("sexo", "M")
        
        # Raça/cor
        ET.SubElement(trabalhador, "racaCor").text = colaborador.get("raca_cor", "9")
        
        # Estado civil
        ET.SubElement(trabalhador, "estCiv").text = colaborador.get("estado_civil", "9")
        
        # Grau de instrução
        ET.SubElement(trabalhador, "grauInstr").text = colaborador.get("escolaridade", "05")
        
        # Nascimento
        nascimento = ET.SubElement(trabalhador, "nascimento")
        ET.SubElement(nascimento, "dtNascto").text = colaborador.get("data_nascimento", "")
        ET.SubElement(nascimento, "codMunic").text = colaborador.get("naturalidade_municipio", "")
        ET.SubElement(nascimento, "uf").text = colaborador.get("naturalidade_uf", "")
        ET.SubElement(nascimento, "pais").text = colaborador.get("nacionalidade", "105")
        
        # Endereço
        if colaborador.get("logradouro"):
            endereco = ET.SubElement(trabalhador, "endereco")
            endereco_completo = ET.SubElement(endereco, "enderecoCompleto")
            
            ET.SubElement(endereco_completo, "ideLograd").text = "1"  # Logradouro
            ET.SubElement(endereco_completo, "tpLograd").text = colaborador.get("tipo_logradouro", "RUA")
            ET.SubElement(endereco_completo, "dscLograd").text = colaborador.get("logradouro", "")
            ET.SubElement(endereco_completo, "nrLograd").text = colaborador.get("numero", "")
            
            if colaborador.get("complemento"):
                ET.SubElement(endereco_completo, "complLograd").text = colaborador.get("complemento")
            
            ET.SubElement(endereco_completo, "bairro").text = colaborador.get("bairro", "")
            ET.SubElement(endereco_completo, "cep").text = str(colaborador.get("cep", "")).replace("-", "")
            ET.SubElement(endereco_completo, "codMunic").text = colaborador.get("municipio_ibge", "")
            ET.SubElement(endereco_completo, "uf").text = colaborador.get("uf", "")
        
        # Documentos
        documentos = ET.SubElement(trabalhador, "documentos")
        
        # CTPS
        if colaborador.get("ctps_numero"):
            ctps = ET.SubElement(documentos, "CTPS")
            ET.SubElement(ctps, "nrCtps").text = str(colaborador.get("ctps_numero"))
            ET.SubElement(ctps, "serieCtps").text = str(colaborador.get("ctps_serie", "0"))
            ET.SubElement(ctps, "ufCtps").text = colaborador.get("ctps_uf", "SP")
        
        # RG
        if colaborador.get("rg_numero"):
            rg = ET.SubElement(documentos, "RG")
            ET.SubElement(rg, "nrRg").text = str(colaborador.get("rg_numero"))
            ET.SubElement(rg, "orgaoEmissor").text = colaborador.get("rg_orgao", "SSP")
            ET.SubElement(rg, "ufExped").text = colaborador.get("rg_uf", "SP")
        
        # CPF (obrigatório)
        cpf = ET.SubElement(documentos, "cpf")
        ET.SubElement(cpf, "nrCpf").text = str(colaborador.get("cpf", "")).zfill(11)
        
        # Dados bancários
        if colaborador.get("banco_agencia"):
            info_banco = ET.SubElement(trabalhador, "infoBanco")
            ET.SubElement(info_banco, "codBanco").text = str(colaborador.get("banco_codigo", "001"))
            ET.SubElement(info_banco, "codAgencia").text = str(colaborador.get("banco_agencia", ""))
            ET.SubElement(info_banco, "nrContaBanco").text = str(colaborador.get("banco_conta", ""))
    
    def _preparar_vinculo(self, evt: ET.Element, colaborador: Dict[str, Any]):
        """Prepara elemento vínculo"""
        vinculo = ET.SubElement(evt, "vinculo")
        
        # Matrícula
        ET.SubElement(vinculo, "matricula").text = colaborador.get("matricula", "0001")
        
        # Categoria do trabalhador
        ET.SubElement(vinculo, "codCateg").text = colaborador.get("categoria", "101")
        
        # Tipo de contrato
        ET.SubElement(vinculo, "tpRegPrev").text = colaborador.get("regime_previdencia", "1")
        
        # Informações do contrato
        info_contrato = ET.SubElement(vinculo, "infoContrato")
        
        # CBO (Classificação Brasileira de Ocupações)
        ET.SubElement(info_contrato, "codCargo").text = colaborador.get("cbo", "000000")
        
        # Função
        ET.SubElement(info_contrato, "funcao").text = colaborador.get("funcao", "")
        
        # Tipo de jornada
        jornada = ET.SubElement(info_contrato, "infoRegimeJuridico")
        ET.SubElement(jornada, "indCoop").text = "0"  # Não é cooperativa
        ET.SubElement(jornada, "indContrApr").text = "0"  # Não é contrato de aprendizagem
        
        # Datas
        ET.SubElement(info_contrato, "dtAdm").text = colaborador.get("data_admissao", "")
        
        # Tipo de admissão
        ET.SubElement(info_contrato, "tpAdmissao").text = "1"  # Preenchimento pelo empregador
        
        # Tipo de regime
        ET.SubElement(info_contrato, "tpRegJor").text = "1"  # Normal (40h semanais)
    
    def _preparar_remuneracao(self, evt: ET.Element, colaborador: Dict[str, Any]):
        """Prepara elemento remuneração"""
        remuneracao = ET.SubElement(evt, "remuneracao")
        
        # Salário base
        ET.SubElement(remuneracao, "remunPer").text = f"{colaborador.get('salario_base', 0.0):.2f}"
        
        # Unidade de tempo (M=Mensal, H=Hora, T=Tarefa)
        ET.SubElement(remuneracao, "undSal").text = colaborador.get("unidade_salario", "M")
        
        # Forma de pagamento
        ET.SubElement(remuneracao, "tpPag").text = "1"  # Por mês
    
    def _preparar_informacoes_adicionais(self, evt: ET.Element, colaborador: Dict[str, Any]):
        """Prepara informações adicionais"""
        # Pode ser expandido conforme necessidade
        pass
    
    def _assinar_xml(self, xml_str: str) -> str:
        """
        Assina o XML com certificado digital
        
        Args:
            xml_str: XML como string
            
        Returns:
            XML assinado
        """
        # TODO: Implementar assinatura digital
        # Por enquanto, retorna XML sem assinatura
        logger.warning("Assinatura XML não implementada")
        return xml_str
    
    def _formatar_xml(self) -> str:
        """Formata XML para saída legível"""
        xml_str = ET.tostring(self.root, encoding="unicode")
        
        # Pretty print
        dom = minidom.parseString(xml_str)
        xml_formatado = dom.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
        
        return xml_formatado
    
    def gerar_s1200(self, remuneracoes: list) -> str:
        """
        Gera XML do evento S-1200 (Remuneração de Trabalhador)
        
        Args:
            remuneracoes: Lista de remunerações
            
        Returns:
            XML assinado como string
        """
        # Implementação similar ao S-2200
        # TODO: Implementar estrutura do S-1200
        logger.warning("S-1200 não implementado")
        return ""
    
    def gerar_s2300(self, trabalhador_temporario: Dict[str, Any]) -> str:
        """
        Gera XML do evento S-2300 (Trabalhador Temporário)
        
        Args:
            trabalhador_temporario: Dados do trabalhador temporário
            
        Returns:
            XML assinado como string
        """
        # TODO: Implementar S-2300
        logger.warning("S-2300 não implementado")
        return ""
    
    def gerar_s2299(self, desligamento: Dict[str, Any]) -> str:
        """
        Gera XML do evento S-2299 (Desligamento)
        
        Args:
            desligamento: Dados do desligamento
            
        Returns:
            XML assinado como string
        """
        # TODO: Implementar S-2299
        logger.warning("S-2299 não implementado")
        return ""


class ESocialTransmissaoService:
    """
    Serviço de transmissão de eventos para eSocial
    """
    
    # URLs do eSocial
    URL_HOMOLOGACAO = "https://preprodbase.esocial.gov.br/servicos/empregador/WS/RECEBERLOTE"
    URL_PRODUCAO = "https://servicos.esocial.gov.br/servicos/empregador/WS/RECEBERLOTE"
    
    def __init__(self, certificado_path: str, senha: str, ambiente: str = "homologacao"):
        self.certificado_path = certificado_path
        self.senha = senha
        self.ambiente = ambiente
        self.url = self.URL_HOMOLOGACAO if ambiente == "homologacao" else self.URL_PRODUCAO
    
    def enviar_lote(self, xml_lote: str) -> dict:
        """
        Envia lote de eventos para eSocial
        
        Args:
            xml_lote: XML do lote
            
        Returns:
            Dicionário com resposta
        """
        # TODO: Implementar envio SOAP para eSocial
        logger.warning("Transmissão eSocial não implementada")
        return {
            "status": "pendente",
            "recibo": None,
        }
    
    def consultar_recibo(self, numero_recibo: str) -> dict:
        """
        Consulta situação do lote
        
        Args:
            numero_recibo: Número do recibo
            
        Returns:
            Dicionário com situação
        """
        # TODO: Implementar consulta
        logger.warning("Consulta eSocial não implementada")
        return {
            "status": "desconhecido",
        }
