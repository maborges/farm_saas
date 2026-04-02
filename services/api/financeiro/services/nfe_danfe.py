"""
Geração de DANFE (Documento Auxiliar da Nota Fiscal Eletrônica)

Gera PDF do DANFE no modelo oficial da SEFAZ.
"""

from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
import base64
from io import BytesIO
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DANFEGerador:
    """
    Gerador de DANFE no padrão oficial
    
    Gera PDF do Documento Auxiliar da Nota Fiscal Eletrônica
    conforme layout definido pelo Manual da NFe.
    """
    
    # Cores padrão
    COR_BORDA = colors.black
    COR_FUNDO_CABECALHO = colors.HexColor('#e0e0e0')
    
    def __init__(self):
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._configurar_estilos()
    
    def _configurar_estilos(self):
        """Configura estilos de parágrafo"""
        # Título
        self.styles.add(ParagraphStyle(
            name='Titulo',
            parent=self.styles['Heading1'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=6
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=3
        ))
        
        # Texto pequeno
        self.styles.add(ParagraphStyle(
            name='TextoPequeno',
            parent=self.styles['Normal'],
            fontSize=6,
            spaceAfter=2
        ))
        
        # Valor
        self.styles.add(ParagraphStyle(
            name='Valor',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_RIGHT,
            spaceAfter=3
        ))
    
    def gerar_danfe(self, nota_fiscal: Dict[str, Any]) -> str:
        """
        Gera PDF do DANFE
        
        Args:
            nota_fiscal: Dicionário com dados da nota fiscal
            
        Returns:
            PDF em base64
        """
        # Criar documento PDF
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=0.5*cm,
            leftMargin=0.5*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )
        
        elementos = []
        
        # 1. Cabeçalho
        elementos.extend(self._criar_cabecalho(nota_fiscal))
        
        # 2. Dados do destinatário
        elementos.extend(self._criar_destinatario(nota_fiscal))
        
        # 3. Dados da fatura
        elementos.extend(self._criar_fatura(nota_fiscal))
        
        # 4. Cálculo do imposto
        elementos.extend(self._criar_impostos(nota_fiscal))
        
        # 5. Transportador
        elementos.extend(self._criar_transportador(nota_fiscal))
        
        # 6. Dados dos produtos
        elementos.extend(self._criar_produtos(nota_fiscal))
        
        # 7. Dados adicionais
        elementos.extend(self._criar_dados_adicionais(nota_fiscal))
        
        # 8. Código de barras
        elementos.extend(self._criar_codigo_barras(nota_fiscal))
        
        # Construir PDF
        doc.build(elementos)
        
        # Obter PDF em base64
        pdf_base64 = base64.b64encode(self.buffer.getvalue()).decode('utf-8')
        
        logger.info(f"DANFE gerado com sucesso para nota {nota_fiscal.get('numero')}")
        
        return pdf_base64
    
    def _criar_cabecalho(self, nota: Dict[str, Any]) -> list:
        """Cria cabeçalho do DANFE"""
        elementos = []
        
        # Tabela de cabeçalho (3 colunas)
        dados = [
            # Coluna 1: Logo e dados do emitente
            self._criar_dados_emitente(nota),
            
            # Coluna 2: DANFE
            self._criar_danfe_identificacao(nota),
            
            # Coluna 3: Código de barras
            self._criar_codigo_barras_header(nota),
        ]
        
        tabela = Table(dados, colWidths=[5*cm, 8*cm, 5*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.COR_FUNDO_CABECALHO),
            ('BACKGROUND', (2, 0), (2, 0), self.COR_FUNDO_CABECALHO),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.2*cm))
        
        return elementos
    
    def _criar_dados_emitente(self, nota: Dict[str, Any]) -> list:
        """Cria dados do emitente"""
        dados = []
        
        # Nome do emitente
        dados.append(['DADOS DO EMITENTE'])
        dados.append([nota.get('emitente_nome', '')])
        dados.append([f"CNPJ: {nota.get('emitente_cnpj_cpf', '')}"])
        dados.append([f"IE: {nota.get('emitente_ie', '')}"])
        
        return dados
    
    def _criar_danfe_identificacao(self, nota: Dict[str, Any]) -> list:
        """Cria identificação do DANFE"""
        dados = []
        
        # Título
        dados.append(['DOCUMENTO AUXILIAR DA NOTA FISCAL ELETRÔNICA'])
        dados.append(['DANFE'])
        dados.append([''])
        
        # Número e série
        dados.append([f"Número: {nota.get('numero', 0)}"])
        dados.append([f"Série: {nota.get('serie', '1')}"])
        
        # Tipo de operação
        dados.append([f"Tipo: {nota.get('tipo', 'NFP-e')}"])
        
        # Página
        dados.append(['Página 1/1'])
        
        return dados
    
    def _criar_codigo_barras_header(self, nota: Dict[str, Any]) -> list:
        """Cria código de barras do cabeçalho"""
        dados = []
        
        chave = nota.get('chave_acesso', '')
        
        if chave:
            # Gerar código de barras
            codigo = self._gerar_codigo_barras(chave)
            dados.append([codigo])
            dados.append([f"Chave de Acesso: {self._formatar_chave(chave)}"])
        else:
            dados.append(['Aguardando geração da chave'])
        
        return dados
    
    def _criar_destinatario(self, nota: Dict[str, Any]) -> list:
        """Cria seção de destinatário"""
        elementos = []
        
        # Título
        titulo = Paragraph("DESTINATÁRIO / REMETENTE", self.styles['Titulo'])
        elementos.append(titulo)
        
        # Tabela de dados
        dados = [
            ['Nome / Razão Social:', nota.get('destinatario_nome', '')],
            ['CNPJ / CPF:', nota.get('destinatario_documento', '')],
            ['Endereço:', f"{nota.get('destinatario_logradouro', '')}, {nota.get('destinatario_numero', '')}"],
            ['Bairro:', nota.get('destinatario_bairro', '')],
            ['Município:', nota.get('destinatario_municipio', '')],
            ['UF:', nota.get('destinatario_uf', '')],
            ['CEP:', nota.get('destinatario_cep', '')],
        ]
        
        tabela = Table(dados, colWidths=[4*cm, 10*cm])
        tabela.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONT', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.2*cm))
        
        return elementos
    
    def _criar_fatura(self, nota: Dict[str, Any]) -> list:
        """Cria seção de fatura"""
        elementos = []
        
        titulo = Paragraph("FATURA / DUPLICATAS", self.styles['Titulo'])
        elementos.append(titulo)
        
        # Dados da fatura (simplificado)
        dados = [
            ['Fatura:', f"Número: {nota.get('numero', 0)}"],
            ['Vencimento:', 'A vista'],
            ['Valor:', f"R$ {nota.get('valor_total', 0):.2f}"],
        ]
        
        tabela = Table(dados, colWidths=[6*cm, 6*cm, 6*cm])
        tabela.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.2*cm))
        
        return elementos
    
    def _criar_impostos(self, nota: Dict[str, Any]) -> list:
        """Cria seção de cálculo de impostos"""
        elementos = []
        
        titulo = Paragraph("CÁLCULO DO IMPOSTO", self.styles['Titulo'])
        elementos.append(titulo)
        
        # Tabela de impostos
        dados = [
            [
                'Base de Cálculo do ICMS',
                f"R$ {nota.get('base_calculo_icms', 0):.2f}"
            ],
            [
                'Valor do ICMS',
                f"R$ {nota.get('valor_icms', 0):.2f}"
            ],
            [
                'Base de Cálculo ICMS ST',
                f"R$ {nota.get('base_calculo_icms_st', 0):.2f}"
            ],
            [
                'Valor do ICMS ST',
                f"R$ {nota.get('valor_icms_st', 0):.2f}"
            ],
            [
                'Valor Total dos Produtos',
                f"R$ {nota.get('valor_produtos', 0):.2f}"
            ],
            [
                'Valor Total da Nota',
                f"R$ {nota.get('valor_total', 0):.2f}"
            ],
        ]
        
        tabela = Table(dados, colWidths=[10*cm, 5*cm])
        tabela.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), self.COR_FUNDO_CABECALHO),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.2*cm))
        
        return elementos
    
    def _criar_transportador(self, nota: Dict[str, Any]) -> list:
        """Cria seção de transportador"""
        elementos = []
        
        titulo = Paragraph("TRANSPORTADOR / VOLUMES TRANSPORTADOS", self.styles['Titulo'])
        elementos.append(titulo)
        
        transportadora = nota.get('transportadora', {})
        
        dados = [
            ['Nome / Razão Social:', transportadora.get('nome', '')],
            ['CNPJ / CPF:', transportadora.get('cnpj_cpf', '')],
            ['Endereço:', transportadora.get('endereco', '')],
            ['Município:', transportadora.get('municipio', '')],
            ['UF:', transportadora.get('uf', '')],
        ]
        
        tabela = Table(dados, colWidths=[4*cm, 10*cm])
        tabela.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.2*cm))
        
        return elementos
    
    def _criar_produtos(self, nota: Dict[str, Any]) -> list:
        """Cria seção de produtos"""
        elementos = []
        
        titulo = Paragraph("DADOS DOS PRODUTOS / SERVIÇOS", self.styles['Titulo'])
        elementos.append(titulo)
        
        # Cabeçalho da tabela
        cabecalho = [
            'Código',
            'Descrição',
            'NCM',
            'CFOP',
            'Unid.',
            'Qtd.',
            'V. Unitário',
            'V. Total'
        ]
        
        # Dados dos produtos
        dados = [cabecalho]
        
        itens = nota.get('itens', [])
        for item in itens:
            dados.append([
                item.get('codigo', ''),
                item.get('descricao', ''),
                item.get('ncm', ''),
                item.get('cfop', ''),
                item.get('unidade', ''),
                f"{item.get('quantidade', 0):.2f}",
                f"R$ {item.get('valor_unitario', 0):.2f}",
                f"R$ {item.get('quantidade', 0) * item.get('valor_unitario', 0):.2f}"
            ])
        
        tabela = Table(dados, colWidths=[1.5*cm, 5*cm, 1.5*cm, 1.5*cm, 1*cm, 1.5*cm, 2*cm, 2*cm])
        tabela.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), self.COR_FUNDO_CABECALHO),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.2*cm))
        
        return elementos
    
    def _criar_dados_adicionais(self, nota: Dict[str, Any]) -> list:
        """Cria seção de dados adicionais"""
        elementos = []
        
        titulo = Paragraph("DADOS ADICIONAIS", self.styles['Titulo'])
        elementos.append(titulo)
        
        dados = [
            ['Informações Adicionais:', nota.get('info_adicionais_contribuinte', '')],
            ['Informações para o Fisco:', nota.get('info_adicionais_fisco', '')],
        ]
        
        tabela = Table(dados, colWidths=[4*cm, 10*cm])
        tabela.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.2*cm))
        
        return elementos
    
    def _criar_codigo_barras(self, nota: Dict[str, Any]) -> list:
        """Cria seção final com código de barras"""
        elementos = []
        
        chave = nota.get('chave_acesso', '')
        
        if chave:
            # Código de barras
            codigo = self._gerar_codigo_barras(chave)
            elementos.append(codigo)
            
            # Chave formatada
            chave_formatada = self._formatar_chave(chave)
            texto = Paragraph(
                f"Chave de Acesso: {chave_formatada}",
                self.styles['TextoNormal']
            )
            elementos.append(texto)
            
            # URL de consulta
            url = f"https://www.nfe.fazenda.gov.br/portal/consulta.aspx?chNFe={chave}"
            texto_url = Paragraph(
                f"Consulta em: {url}",
                self.styles['TextoPequeno']
            )
            elementos.append(texto_url)
        
        return elementos
    
    def _gerar_codigo_barras(self, chave: str) -> code128.Code128:
        """Gera código de barras Code128"""
        codigo = code128.Code128(chave, barHeight=15*mm, barWidth=0.3*mm)
        return codigo
    
    def _formatar_chave(self, chave: str) -> str:
        """Formata chave de acesso com pontos"""
        if not chave or len(chave) != 44:
            return chave
        
        # Formata: 0000.0000.0000.0000.0000.0000.0000.0000.0000.0000.0000
        return f"{chave[:4]}.{chave[4:8]}.{chave[8:12]}.{chave[12:16]}.{chave[16:20]}.{chave[20:24]}.{chave[24:28]}.{chave[28:32]}.{chave[32:36]}.{chave[36:40]}.{chave[40:]}"
    
    def gerar_qr_code(self, chave: str) -> Optional[Any]:
        """
        Gera QR Code para NFC-e
        
        Args:
            chave: Chave de acesso
            
        Returns:
            QR Code gerado ou None
        """
        # TODO: Implementar QR Code para NFC-e
        # Requer biblioteca qrcode
        logger.warning("QR Code não implementado")
        return None


class DANFEGeradorFactory:
    """Factory para criar instâncias de DANFEGerador"""
    
    @staticmethod
    def get_gerador() -> DANFEGerador:
        """Obtém instância de gerador"""
        return DANFEGerador()
