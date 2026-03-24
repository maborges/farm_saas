from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime

def generate_dre_pdf(data: dict) -> bytes:
    """
    Gera um PDF do Demonstrativo de Resultados (DRE).
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, spaceAfter=20, fontName='Helvetica-Bold')
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], alignment=1, spaceAfter=10, fontSize=10)
    
    elements = []
    
    # 1. Cabeçalho
    elements.append(Paragraph("AgroSaaS - Gestão Inteligente", title_style))
    elements.append(Paragraph(f"Demonstrativo de Resultados (DRE) - Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", header_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # 2. Tabela de Dados
    table_data = [
        ["Descrição", "Valor (R$)"],
        ["RECEITA BRUTA", f"{data.get('receita_total', 0):,.2f}"],
        ["(-) CUSTOS VARIÁVEIS", f"{data.get('custos_variaveis', 0):,.2f}"],
        ["LUCRO BRUTO", f"{(data.get('receita_total', 0) - data.get('custos_variaveis', 0)):,.2f}"],
        ["(-) CUSTOS FIXOS", f"{data.get('custos_fixos', 0):,.2f}"],
        ["EBITDA", f"{data.get('ebitda', 0):,.2f}"],
        ["RESULTADO LÍQUIDO", f"{data.get('resultado_liquido', 0):,.2f}"],
    ]
    
    t = Table(table_data, colWidths=[10*cm, 5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2e7d32")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        # Linhas de totais em negrito
        ('FONTNAME', (0, 3), (1, 3), 'Helvetica-Bold'),
        ('FONTNAME', (0, 5), (1, 6), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 6), (1, 6), colors.darkblue),
    ]))
    
    elements.append(t)
    
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_caderno_campo_pdf(operacoes: list) -> bytes:
    """
    Gera um PDF das operações agrícolas (Caderno de Campo).
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, spaceAfter=20)
    
    elements = []
    elements.append(Paragraph("Caderno de Campo Digital", title_style))
    elements.append(Spacer(1, 0.5*cm))
    
    table_data = [["Data", "Operação", "Talhão", "Área (ha)", "Custo (R$)", "Status"]]
    
    for op in operacoes:
        table_data.append([
            op.get("data_realizada", ""),
            op.get("tipo", ""),
            op.get("talhao_nome", str(op.get("talhao_id"))[:8]),
            f"{op.get('area_aplicada_ha', 0):,.2f}",
            f"{op.get('custo_total', 0):,.2f}",
            op.get("status", "")
        ])
        
    t = Table(table_data, colWidths=[2.5*cm, 4*cm, 4*cm, 2.5*cm, 3*cm, 3*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.olive),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(t)
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
