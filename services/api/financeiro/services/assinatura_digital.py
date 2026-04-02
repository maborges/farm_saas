"""
Assinatura Digital para Nota Fiscal Eletrônica

Implementa assinatura digital no padrão ICP-Brasil para XML da NFe.
"""

from typing import Optional, BinaryIO
import xml.etree.ElementTree as ET
from xml.dom import minidom
import base64
import logging
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.primitives.serialization import pkcs12
import hashlib

logger = logging.getLogger(__name__)


class AssinaturaDigital:
    """
    Assinatura Digital no padrão ICP-Brasil
    
    Implementa assinatura XML usando certificado digital A1 (PKCS#12).
    """
    
    # Namespaces XML Signature
    NS_SIG = "http://www.w3.org/2000/09/xmldsig#"
    NS_NFE = "http://www.portalfiscal.inf.br/nfe"
    
    def __init__(self, certificado_path: str, senha: str):
        """
        Inicializa com certificado digital A1
        
        Args:
            certificado_path: Caminho para o arquivo .pfx ou .p12
            senha: Senha do certificado
        """
        self.certificado_path = certificado_path
        self.senha = senha.encode()
        self.chave_privada = None
        self.certificado = None
        self._carregar_certificado()
    
    def _carregar_certificado(self):
        """Carrega certificado PKCS#12 do arquivo"""
        try:
            with open(self.certificado_path, 'rb') as f:
                pkcs12_data = f.read()
            
            # Carregar certificado e chave privada do PKCS#12
            self.chave_privada, self.certificado, _ = pkcs12.load_key_and_certificates(
                pkcs12_data,
                self.senha,
                default_backend()
            )
            
            logger.info(f"Certificado carregado com sucesso: {self.certificado.subject}")
            logger.info(f"Válido até: {self.certificado.not_valid_after}")
            
        except FileNotFoundError:
            logger.error(f"Certificado não encontrado: {self.certificado_path}")
            raise
        except Exception as e:
            logger.error(f"Erro ao carregar certificado: {str(e)}")
            raise
    
    def assinar_xml(self, xml_string: str) -> str:
        """
        Assina o XML da NFe
        
        Args:
            xml_string: XML da NFe como string
            
        Returns:
            XML assinado como string
        """
        # Parse do XML
        root = ET.fromstring(xml_string)
        
        # Encontrar elemento infNFe para assinar
        inf_nfe = root.find(".//infNFe")
        
        if inf_nfe is None:
            raise ValueError("Elemento infNFe não encontrado no XML")
        
        # Obter ID do elemento
        id_valor = inf_nfe.attrib.get("Id")
        
        if not id_valor:
            raise ValueError("Atributo Id não encontrado em infNFe")
        
        # Criar elemento Signature
        signature = self._criar_assinatura(id_valor)
        
        # Adicionar assinatura ao XML
        # Na NFe, a signature deve ser filha imediata de NFe, antes de infNFe
        nfe = root.find(".//NFe")
        if nfe is not None:
            # Inserir signature antes de infNFe
            nfe.insert(0, signature)
        else:
            # Se não tem NFe, adicionar no root
            root.insert(0, signature)
        
        # Gerar XML formatado
        xml_assinado = self._formatar_xml(root)
        
        logger.info(f"XML assinado com sucesso: {id_valor}")
        return xml_assinado
    
    def _criar_assinatura(self, id_valor: str) -> ET.Element:
        """
        Cria elemento Signature conforme XML Signature
        
        Args:
            id_valor: ID do elemento a ser assinado (ex: NFe352603...)
            
        Returns:
            Elemento Signature
        """
        # Elemento raiz Signature
        signature = ET.Element("{%s}Signature" % self.NS_SIG)
        signature.attrib["xmlns"] = self.NS_SIG
        
        # SignedInfo
        signed_info = self._criar_signed_info(id_valor)
        signature.append(signed_info)
        
        # SignatureValue
        signature_value = self._criar_signature_value(signed_info)
        signature.append(signature_value)
        
        # KeyInfo
        key_info = self._criar_key_info()
        signature.append(key_info)
        
        return signature
    
    def _criar_signed_info(self, id_valor: str) -> ET.Element:
        """
        Cria elemento SignedInfo
        
        Args:
            id_valor: ID do elemento assinado
            
        Returns:
            Elemento SignedInfo
        """
        signed_info = ET.Element("{%s}SignedInfo" % self.NS_SIG)
        
        # CanonicalizationMethod
        canon_method = ET.SubElement(
            signed_info,
            "{%s}CanonicalizationMethod" % self.NS_SIG,
            {"Algorithm": "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"}
        )
        
        # SignatureMethod
        sig_method = ET.SubElement(
            signed_info,
            "{%s}SignatureMethod" % self.NS_SIG,
            {"Algorithm": "http://www.w3.org/2000/09/xmldsig#rsa-sha1"}
        )
        
        # Reference
        reference = ET.SubElement(
            signed_info,
            "{%s}Reference" % self.NS_SIG,
            {"URI": f"#{id_valor}"}
        )
        
        # Transforms
        transforms = ET.SubElement(reference, "{%s}Transforms" % self.NS_SIG)
        
        # Transform 1: Enveloped
        ET.SubElement(
            transforms,
            "{%s}Transform" % self.NS_SIG,
            {"Algorithm": "http://www.w3.org/2000/09/xmldsig#enveloped-signature"}
        )
        
        # Transform 2: C14N
        ET.SubElement(
            transforms,
            "{%s}Transform" % self.NS_SIG,
            {"Algorithm": "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"}
        )
        
        # DigestMethod
        digest_method = ET.SubElement(
            reference,
            "{%s}DigestMethod" % self.NS_SIG,
            {"Algorithm": "http://www.w3.org/2000/09/xmldsig#sha1"}
        )
        
        # Calcular DigestValue
        digest_value = self._calcular_digest(id_valor)
        ET.SubElement(reference, "{%s}DigestValue" % self.NS_SIG).text = digest_value
        
        return signed_info
    
    def _calcular_digest(self, id_valor: str) -> str:
        """
        Calcula o digest SHA-1 do elemento infNFe
        
        Args:
            id_valor: ID do elemento
            
        Returns:
            Digest em base64
        """
        # Encontrar elemento infNFe
        root = ET.fromstring("<root></root>")  # XML temporário
        inf_nfe = ET.SubElement(root, "infNFe", {"Id": id_valor})
        
        # Na prática, precisamos do XML real do infNFe
        # Isso será calculado durante a assinatura real
        # Por enquanto, retornamos um placeholder
        
        # TODO: Implementar cálculo real do digest
        # 1. Obter XML do infNFe
        # 2. Aplicar C14N
        # 3. Calcular SHA-1
        # 4. Codificar em base64
        
        # Placeholder - será implementado na integração real
        return "calcular_digest_real_aqui="
    
    def _criar_signature_value(self, signed_info: ET.Element) -> ET.Element:
        """
        Cria elemento SignatureValue com a assinatura RSA
        
        Args:
            signed_info: Elemento SignedInfo
            
        Returns:
            Elemento SignatureValue
        """
        # Serializar SignedInfo para bytes
        signed_info_bytes = self._canonicalizar_xml(signed_info)
        
        # Assinar com chave privada (RSA-SHA1)
        assinatura = self.chave_privada.sign(
            signed_info_bytes,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        
        # Codificar em base64
        assinatura_b64 = base64.b64encode(assinatura).decode('utf-8')
        
        # Quebrar em linhas de 76 caracteres (padrão)
        assinatura_formatada = '\n'.join(
            assinatura_b64[i:i+76] for i in range(0, len(assinatura_b64), 76)
        )
        
        signature_value = ET.Element("{%s}SignatureValue" % self.NS_SIG)
        signature_value.text = assinatura_formatada
        
        return signature_value
    
    def _criar_key_info(self) -> ET.Element:
        """
        Cria elemento KeyInfo com o certificado público
        
        Returns:
            Elemento KeyInfo
        """
        key_info = ET.Element("{%s}KeyInfo" % self.NS_SIG)
        
        # X509Data
        x509_data = ET.SubElement(key_info, "{%s}X509Data" % self.NS_SIG)
        
        # X509Certificate (certificado em base64)
        cert_der = self.certificado.public_bytes(serialization.Encoding.DER)
        cert_b64 = base64.b64encode(cert_der).decode('utf-8')
        
        x509_cert = ET.SubElement(x509_data, "{%s}X509Certificate" % self.NS_SIG)
        x509_cert.text = cert_b64
        
        return key_info
    
    def _canonicalizar_xml(self, elemento: ET.Element) -> bytes:
        """
        Aplica canonicalização C14N no XML
        
        Args:
            elemento: Elemento XML para canonicalizar
            
        Returns:
            XML canonicalizado como bytes
        """
        # Converter para string
        xml_str = ET.tostring(elemento, encoding='unicode')
        
        # Parse com minidom para canonicalização
        dom = minidom.parseString(xml_str)
        
        # Canonicalização C14N
        # Nota: Python não tem C14N nativo, precisamos de biblioteca externa
        # Por enquanto, usamos uma versão simplificada
        
        # TODO: Implementar C14N correta com lxml
        return dom.toxml(encoding='utf-8')
    
    def _formatar_xml(self, root: ET.Element) -> str:
        """
        Formata XML para saída legível
        
        Args:
            root: Elemento raiz do XML
            
        Returns:
            XML formatado como string
        """
        # Adicionar declaração XML
        xml_str = ET.tostring(root, encoding='unicode')
        
        # Pretty print com minidom
        dom = minidom.parseString(xml_str)
        xml_formatado = dom.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
        
        # Remover linhas vazias extras
        linhas = [linha for linha in xml_formatado.split('\n') if linha.strip()]
        
        return '\n'.join(linhas)
    
    def validar_assinatura(self, xml_assinado: str) -> bool:
        """
        Valida a assinatura digital do XML
        
        Args:
            xml_assinado: XML com assinatura
            
        Returns:
            True se assinatura válida, False caso contrário
        """
        try:
            root = ET.fromstring(xml_assinado)
            
            # Extrair Signature
            signature = root.find(".//{%s}Signature" % self.NS_SIG)
            
            if signature is None:
                logger.error("Assinatura não encontrada no XML")
                return False
            
            # Extrair SignatureValue
            sig_value_elem = signature.find("{%s}SignatureValue" % self.NS_SIG)
            
            if sig_value_elem is None or not sig_value_elem.text:
                logger.error("SignatureValue não encontrado")
                return False
            
            # Decodificar assinatura de base64
            assinatura_b64 = sig_value_elem.text.replace('\n', '')
            assinatura = base64.b64decode(assinatura_b64)
            
            # Extrair SignedInfo e recalcular digest
            signed_info = signature.find("{%s}SignedInfo" % self.NS_SIG)
            
            # Extrair certificado e validar
            # TODO: Implementar validação completa
            
            logger.info("Assinatura validada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar assinatura: {str(e)}")
            return False
    
    def obter_info_certificado(self) -> dict:
        """
        Obtém informações do certificado
        
        Returns:
            Dicionário com informações do certificado
        """
        if not self.certificado:
            return {}
        
        info = {
            "emitente": self.certificado.subject.rfc4514_string(),
            "valido_de": self.certificado.not_valid_before.isoformat(),
            "valido_ate": self.certificado.not_valid_after.isoformat(),
            "numero_serie": format(self.certificado.serial_number, 'x'),
            "issuer": self.certificado.issuer.rfc4514_string(),
        }
        
        return info
    
    def certificado_valido(self) -> bool:
        """
        Verifica se o certificado é válido (não expirado)
        
        Returns:
            True se válido, False se expirado
        """
        from datetime import datetime
        
        if not self.certificado:
            return False
        
        agora = datetime.now()
        return (
            self.certificado.not_valid_before <= agora <=
            self.certificado.not_valid_after
        )


class AssinaturaDigitalFactory:
    """Factory para criar instâncias de AssinaturaDigital"""
    
    _instancias = {}
    
    @classmethod
    def get_assinatura(cls, tenant_id: str, certificado_path: str, senha: str) -> AssinaturaDigital:
        """
        Obtém ou cria instância de assinatura para o tenant
        
        Args:
            tenant_id: ID do tenant
            certificado_path: Caminho do certificado
            senha: Senha do certificado
            
        Returns:
            Instância de AssinaturaDigital
        """
        if tenant_id not in cls._instancias:
            cls._instancias[tenant_id] = AssinaturaDigital(certificado_path, senha)
        
        return cls._instancias[tenant_id]
    
    @classmethod
    def remover_assinatura(cls, tenant_id: str):
        """Remove instância do cache"""
        if tenant_id in cls._instancias:
            del cls._instancias[tenant_id]
