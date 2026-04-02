"""
Testes unitários para o gerador de XML NFe

Testes para validar a geração de XML no padrão NFe 4.0
"""

import pytest
from datetime import datetime
from services.api.financeiro.services.nfe_xml_generator import NFeXMLGenerator
import xml.etree.ElementTree as ET


class TestNFeXMLGenerator:
    """Classe de testes para NFeXMLGenerator"""
    
    @pytest.fixture
    def generator(self):
        """Fixture que cria uma instância do gerador"""
        return NFeXMLGenerator()
    
    @pytest.fixture
    def nota_fiscal_valida(self):
        """Fixture com dados válidos de nota fiscal"""
        return {
            "tipo": "NFP-e",
            "numero": 1,
            "serie": "1",
            "data_emissao": datetime(2026, 3, 31, 10, 0, 0),
            "emitente_cnpj_cpf": "12345678000190",
            "emitente_nome": "Fazenda Santa Maria",
            "emitente_uf": "SP",
            "emitente_municipio": "Ribeirão Preto",
            "emitente_cod_municipio": "3543402",
            "emitente_logradouro": "Rua da Fazenda",
            "emitente_numero": "1000",
            "emitente_bairro": "Zona Rural",
            "emitente_cep": "14000000",
            "emitente_ie": "123456789",
            "destinatario_tipo": "PJ",
            "destinatario_nome": "Cerealista Silva Ltda",
            "destinatario_documento": "98765432000190",
            "endereco_destinatario": {
                "logradouro": "Rua das Flores",
                "numero": "123",
                "bairro": "Centro",
                "municipio": "São Paulo",
                "uf": "SP",
                "cep": "01234567",
                "cod_municipio": "3550308"
            },
            "itens": [
                {
                    "codigo": "001",
                    "descricao": "Soja em grão",
                    "ncm": "12019000",
                    "cfop": "5101",
                    "quantidade": 1000.00,
                    "unidade": "SC",
                    "valor_unitario": 150.00,
                    "origem": "0",
                    "csosn": "102",
                    "aliq_icms": 0.0
                }
            ],
            "valor_total": 150000.00,
            "valor_produtos": 150000.00,
            "valor_icms": 0.0,
            "valor_pis": 0.0,
            "valor_cofins": 0.0
        }
    
    def test_gerar_xml_retorna_string(self, generator, nota_fiscal_valida):
        """Testa se gerar_xml retorna uma string"""
        xml = generator.gerar_xml(nota_fiscal_valida)
        
        assert isinstance(xml, str)
        assert len(xml) > 0
    
    def test_xml_contem_elemento_raiz(self, generator, nota_fiscal_valida):
        """Testa se o XML contém o elemento raiz nfeProc"""
        xml = generator.gerar_xml(nota_fiscal_valida)
        
        # Parse do XML
        root = ET.fromstring(xml)
        
        assert root.tag == "nfeProc"
        assert root.attrib["versao"] == "4.00"
    
    def test_xml_contem_nfe(self, generator, nota_fiscal_valida):
        """Testa se o XML contém o elemento NFe"""
        xml = generator.gerar_xml(nota_fiscal_valida)
        root = ET.fromstring(xml)
        
        nfe = root.find(".//NFe")
        assert nfe is not None
    
    def test_xml_contem_inf_nfe_com_id(self, generator, nota_fiscal_valida):
        """Testa se infNFe tem o atributo Id correto"""
        xml = generator.gerar_xml(nota_fiscal_valida)
        root = ET.fromstring(xml)
        
        inf_nfe = root.find(".//infNFe")
        assert inf_nfe is not None
        assert "Id" in inf_nfe.attrib
        assert inf_nfe.attrib["Id"].startswith("NFe")
        assert len(inf_nfe.attrib["Id"]) == 47  # NFe + 43 caracteres + DV
    
    def test_xml_contem_emitente(self, generator, nota_fiscal_valida):
        """Testa se os dados do emitente estão presentes"""
        xml = generator.gerar_xml(nota_fiscal_valida)
        root = ET.fromstring(xml)
        
        emit = root.find(".//emit")
        assert emit is not None
        
        cnpj = emit.find("CNPJ")
        assert cnpj is not None
        assert cnpj.text == "12345678000190"
        
        x_nome = emit.find("xNome")
        assert x_nome is not None
        assert x_nome.text == "Fazenda Santa Maria"
    
    def test_xml_contem_destinatario(self, generator, nota_fiscal_valida):
        """Testa se os dados do destinatário estão presentes"""
        xml = generator.gerar_xml(nota_fiscal_valida)
        root = ET.fromstring(xml)
        
        dest = root.find(".//dest")
        assert dest is not None
        
        cnpj = dest.find("CNPJ")
        assert cnpj is not None
        assert cnpj.text == "98765432000190"
        
        x_nome = dest.find("xNome")
        assert x_nome is not None
        assert x_nome.text == "Cerealista Silva Ltda"
    
    def test_xml_contem_produtos(self, generator, nota_fiscal_valida):
        """Testa se os produtos estão presentes"""
        xml = generator.gerar_xml(nota_fiscal_valida)
        root = ET.fromstring(xml)
        
        det = root.find(".//det")
        assert det is not None
        assert det.attrib["nItem"] == "1"
        
        prod = det.find("prod")
        assert prod is not None
        
        x_prod = prod.find("xProd")
        assert x_prod is not None
        assert x_prod.text == "Soja em grão"
        
        ncm = prod.find("NCM")
        assert ncm is not None
        assert ncm.text == "12019000"
        
        v_prod = prod.find("vProd")
        assert v_prod is not None
        assert v_prod.text == "150000.00"
    
    def test_xml_contem_totais(self, generator, nota_fiscal_valida):
        """Testa se os totais estão presentes"""
        xml = generator.gerar_xml(nota_fiscal_valida)
        root = ET.fromstring(xml)
        
        icms_tot = root.find(".//ICMSTot")
        assert icms_tot is not None
        
        v_prod = icms_tot.find("vProd")
        assert v_prod is not None
        assert v_prod.text == "150000.00"
        
        v_nf = icms_tot.find("vNF")
        assert v_nf is not None
        assert v_nf.text == "150000.00"
    
    def test_calculo_digito_verificador(self, generator):
        """Testa o cálculo do dígito verificador"""
        chave_teste = "352603123456780001905500100000000100000000"
        dv = generator._calcular_dv(chave_teste)
        
        assert isinstance(dv, str)
        assert len(dv) == 1
        assert dv.isdigit()
    
    def test_obter_codigo_uf(self, generator):
        """Testa obtenção do código da UF"""
        assert generator._obter_codigo_uf("SP") == "35"
        assert generator._obter_codigo_uf("MG") == "31"
        assert generator._obter_codigo_uf("RS") == "43"
        assert generator._obter_codigo_uf("PR") == "41"
    
    def test_formatar_decimal(self, generator):
        """Testa formatação de decimais"""
        assert generator._formatar_decimal(150.00) == "150.00"
        assert generator._formatar_decimal(150.5) == "150.50"
        assert generator._formatar_decimal(150.555) == "150.55"
        assert generator._formatar_decimal(0) == "0.00"
    
    def test_xml_contem_ide(self, generator, nota_fiscal_valida):
        """Testa se a identificação está presente"""
        xml = generator.gerar_xml(nota_fiscal_valida)
        root = ET.fromstring(xml)
        
        ide = root.find(".//ide")
        assert ide is not None
        
        c_uf = ide.find("cUF")
        assert c_uf is not None
        assert c_uf.text == "35"  # SP
        
        mod = ide.find("mod")
        assert mod is not None
        assert mod.text == "55"  # NFe
        
        tp_amb = ide.find("tpAmb")
        assert tp_amb is not None
        assert tp_amb.text == "2"  # Homologação
    
    def test_xml_contem_icms(self, generator, nota_fiscal_valida):
        """Testa se o ICMS está presente"""
        xml = generator.gerar_xml(nota_fiscal_valida)
        root = ET.fromstring(xml)
        
        icms_item = root.find(".//ICMS102")
        assert icms_item is not None
        
        csosn = icms_item.find("CSOSN")
        assert csosn is not None
        assert csosn.text == "102"
    
    def test_validar_xml(self, generator, nota_fiscal_valida):
        """Testa validação do XML"""
        xml = generator.gerar_xml(nota_fiscal_valida)
        
        # Validação sempre retorna True (implementação pendente)
        assert generator.validar_xml(xml) is True
    
    def test_xml_bem_formado(self, generator, nota_fiscal_valida):
        """Testa se o XML é bem formado"""
        xml = generator.gerar_xml(nota_fiscal_valida)
        
        # Deve começar com declaração XML
        assert xml.startswith('<?xml')
        
        # Deve ser parseável
        root = ET.fromstring(xml)
        assert root is not None
    
    def test_multiplos_itens(self, generator, nota_fiscal_valida):
        """Testa geração com múltiplos itens"""
        nota_fiscal_valida["itens"].append({
            "codigo": "002",
            "descricao": "Milho em grão",
            "ncm": "10059000",
            "cfop": "5101",
            "quantidade": 500.00,
            "unidade": "SC",
            "valor_unitario": 80.00,
            "origem": "0",
            "csosn": "102",
            "aliq_icms": 0.0
        })
        
        xml = generator.gerar_xml(nota_fiscal_valida)
        root = ET.fromstring(xml)
        
        # Deve ter 2 elementos det
        dets = root.findall(".//det")
        assert len(dets) == 2
        
        # Verificar segundo item
        det_2 = dets[1]
        assert det_2.attrib["nItem"] == "2"
        
        x_prod = det_2.find(".//xProd")
        assert x_prod.text == "Milho em grão"


class TestNFeXMLGeneratorHomologacao:
    """Testes de integração para ambiente de homologação"""
    
    def test_gerar_xml_homologacao(self):
        """Testa geração de XML para homologação"""
        generator = NFeXMLGenerator()
        
        nota = {
            "tipo": "NFP-e",
            "numero": 100,
            "serie": "1",
            "data_emissao": datetime.now(),
            "emitente_cnpj_cpf": "12345678000190",
            "emitente_nome": "Fazenda Teste",
            "emitente_uf": "SP",
            "destinatario_tipo": "PJ",
            "destinatario_nome": "Empresa Teste",
            "destinatario_documento": "98765432000190",
            "itens": [
                {
                    "codigo": "001",
                    "descricao": "Soja",
                    "ncm": "12019000",
                    "cfop": "5101",
                    "quantidade": 100.00,
                    "unidade": "SC",
                    "valor_unitario": 150.00,
                    "origem": "0",
                    "csosn": "102"
                }
            ],
            "valor_total": 15000.00
        }
        
        xml = generator.gerar_xml(nota, ambiente="homologacao")
        
        # Verificar se está em homologação
        root = ET.fromstring(xml)
        ide = root.find(".//ide")
        tp_amb = ide.find("tpAmb")
        assert tp_amb.text == "2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
