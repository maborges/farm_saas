#!/usr/bin/env python3
"""Gera apresentação comercial AgroSaaS em PDF."""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
import os

W, H = landscape(A4)
OUT = os.path.join(os.path.dirname(__file__), "AgroSaaS_Apresentacao_Comercial.pdf")

# Cores
GREEN_DARK = HexColor("#1B5E20")
GREEN_MED = HexColor("#2E7D32")
GREEN_LIGHT = HexColor("#4CAF50")
GREEN_PALE = HexColor("#E8F5E9")
GRAY_DARK = HexColor("#212121")
GRAY_MED = HexColor("#616161")
GRAY_LIGHT = HexColor("#F5F5F5")
ACCENT = HexColor("#FF6F00")
WHITE = white

# Styles
def style(name="body", size=14, color=GRAY_DARK, align=TA_LEFT, bold=False, leading=None):
    fname = "Helvetica-Bold" if bold else "Helvetica"
    return ParagraphStyle(name, fontName=fname, fontSize=size, textColor=color,
                          alignment=align, leading=leading or size * 1.4, spaceAfter=4)

S_TITLE = style("title", 36, WHITE, TA_CENTER, True)
S_SUBTITLE = style("sub", 18, HexColor("#C8E6C9"), TA_CENTER)
S_SLIDE_TITLE = style("stitle", 28, GREEN_DARK, TA_LEFT, True)
S_SLIDE_TITLE_W = style("stitlew", 28, WHITE, TA_LEFT, True)
S_BODY = style("body", 15, GRAY_DARK, TA_LEFT, leading=22)
S_BODY_W = style("bodyw", 15, WHITE, TA_LEFT, leading=22)
S_BULLET = style("bullet", 14, GRAY_DARK, TA_LEFT, leading=21)
S_BULLET_W = style("bulletw", 14, WHITE, TA_LEFT, leading=21)
S_SMALL = style("small", 12, GRAY_MED, TA_CENTER)
S_NUMBER = style("num", 48, GREEN_LIGHT, TA_CENTER, True)
S_NUMBER_LABEL = style("numl", 13, GRAY_MED, TA_CENTER)
S_CTA_TITLE = style("cta", 32, WHITE, TA_CENTER, True)
S_CTA_SUB = style("ctasub", 16, HexColor("#C8E6C9"), TA_CENTER)


def draw_bg(c, color=WHITE):
    c.setFillColor(color)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def draw_gradient_bg(c, top=GREEN_DARK, bot=GREEN_MED):
    steps = 60
    for i in range(steps):
        t = i / steps
        r = top.red + (bot.red - top.red) * t
        g = top.green + (bot.green - top.green) * t
        b = top.blue + (bot.blue - top.blue) * t
        c.setFillColor(HexColor(f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"))
        y = H - (H / steps) * i
        c.rect(0, y - H/steps, W, H/steps + 1, fill=1, stroke=0)


def draw_accent_bar(c, y=H - 8*mm, w=80*mm, h=4*mm, color=ACCENT):
    c.setFillColor(color)
    c.rect((W - w)/2, y, w, h, fill=1, stroke=0)


def draw_para(c, text, x, y, width, s):
    p = Paragraph(text, s)
    pw, ph = p.wrap(width, 999)
    p.drawOn(c, x, y - ph)
    return ph


def draw_card(c, x, y, w, h, title, body, icon=""):
    c.setFillColor(WHITE)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=0)
    c.setFillColor(GREEN_PALE)
    c.roundRect(x, y + h - 40, w, 40, 8, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.rect(x, y + h - 40, w, 8, fill=1, stroke=0)
    draw_para(c, f"{icon} <b>{title}</b>", x + 12, y + h - 10, w - 24, style("ct", 13, GREEN_DARK, bold=True))
    draw_para(c, body, x + 12, y + h - 48, w - 24, style("cb", 11, GRAY_MED, leading=16))


def draw_stat_card(c, x, y, w, h, number, label):
    c.setFillColor(WHITE)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=0)
    draw_para(c, number, x, y + h - 15, w, S_NUMBER)
    draw_para(c, label, x, y + 12, w, S_NUMBER_LABEL)


def new_slide(c):
    c.showPage()


# ============================
# SLIDE 1 — CAPA
# ============================
def slide_capa(c):
    draw_gradient_bg(c)
    draw_accent_bar(c, y=H - 12*mm, w=60*mm)
    draw_para(c, "AgroSaaS", 0, H/2 + 60, W, S_TITLE)
    draw_para(c, "Gestao Rural Inteligente. Do Plantio ao Balanco.", 0, H/2 + 10, W, S_SUBTITLE)
    draw_para(c, "Apresentacao Comercial 2026", 0, H/2 - 30, W, style("y", 14, HexColor("#A5D6A7"), TA_CENTER))
    draw_para(c, "Borgus Software Ltda", 0, 30, W, style("f", 11, HexColor("#81C784"), TA_CENTER))


# ============================
# SLIDE 2 — O AGRONEGÓCIO BRASILEIRO
# ============================
def slide_mercado(c):
    draw_bg(c, GRAY_LIGHT)
    draw_para(c, "O Agronegocio Brasileiro", 50, H - 50, W - 100, S_SLIDE_TITLE)
    draw_para(c, "Numeros que impressionam, mas escondem ineficiencias criticas.",
              50, H - 90, W - 100, S_BODY)

    stats = [
        ("R$ 835 bi", "PIB Agro 2025"),
        ("27%", "do PIB Nacional"),
        ("5,1 M", "Propriedades Rurais"),
        ("78%", "Nao usam software\nde gestao"),
    ]
    sw = 170
    gap = 25
    sx = (W - (sw * 4 + gap * 3)) / 2
    for i, (num, lbl) in enumerate(stats):
        draw_stat_card(c, sx + i * (sw + gap), H - 250, sw, 110, num, lbl)

    draw_para(c, "Fonte: CNA / IBGE / McKinsey AgTech Report 2025",
              0, 50, W, S_SMALL)


# ============================
# SLIDE 3 — DORES DO PRODUTOR
# ============================
def slide_dores(c):
    draw_bg(c)
    draw_para(c, "As Dores do Produtor Rural", 50, H - 50, W - 100, S_SLIDE_TITLE)

    dores = [
        ("Controle Financeiro Zero",
         "Mistura contas pessoais com as da fazenda. Nao sabe o custo real por hectare. Descobre o prejuizo so no fim da safra."),
        ("Planilhas e Cadernos",
         "Dados espalhados em cadernos, WhatsApp e Excel. Sem historico confiavel. Impossivel tomar decisao com dados reais."),
        ("Conformidade Fiscal",
         "Carnê-Leao, LCDPR, ITR: obrigacoes complexas, multas pesadas. Contador recebe dados incompletos e atrasados."),
        ("Rastreabilidade Inexistente",
         "Mercado externo exige rastreio do campo ao porto. Sem sistema, o produtor perde contratos premium."),
        ("Gestao de Pessoas Informal",
         "Funcionarios sem registro adequado, escalas em papel, custos de mao de obra desconhecidos por atividade."),
        ("Integracao Impossivel",
         "Cada area da fazenda usa uma ferramenta diferente. Dados nao conversam. Visao consolidada nao existe."),
    ]

    cols = 3
    cw = (W - 100 - 30) / cols
    ch = 130
    for i, (t, b) in enumerate(dores):
        col = i % cols
        row = i // cols
        x = 50 + col * (cw + 15)
        y = H - 160 - row * (ch + 15)
        draw_card(c, x, y, cw, ch, t, b, icon="&#x26A0;")


# ============================
# SLIDE 4 — PLAYERS DO MERCADO
# ============================
def slide_concorrencia(c):
    draw_bg(c)
    draw_para(c, "Players do Mercado e Suas Lacunas", 50, H - 50, W - 100, S_SLIDE_TITLE)

    players = [
        ("Aegro / Cropwise",
         "Foco agricola puro. Sem financeiro integrado, sem pecuaria, sem modulos fiscais. Preco unico sem flexibilidade modular."),
        ("Siagri / Datacoper",
         "ERP pesado, implantacao de meses, custo altissimo. Feito para cooperativas, nao para o produtor individual."),
        ("Conecta Campo / FarmGo",
         "Solucoes pontuais (clima, NDVI). Nao cobrem gestao financeira nem operacional. Dados isolados."),
        ("Totvs Agro / SAP Rural",
         "Enterprise: R$50k+ de implantacao. Complexidade absurda. Produtor medio nao consegue usar."),
        ("Planilhas / Caderno",
         "Gratuito, mas sem rastreabilidade, sem backup, sem relatorios, sem conformidade. O 'sistema' de 78% dos produtores."),
        ("Fintechs Agro",
         "Focam em credito e barter. Nao gerenciam operacao, campo ou estoque. Sao complementares, nao solucao."),
    ]

    cols = 3
    cw = (W - 100 - 30) / cols
    ch = 130
    for i, (t, b) in enumerate(players):
        col = i % cols
        row = i // cols
        x = 50 + col * (cw + 15)
        y = H - 155 - row * (ch + 15)
        draw_card(c, x, y, cw, ch, t, b)


# ============================
# SLIDE 5 — LACUNAS
# ============================
def slide_lacunas(c):
    draw_gradient_bg(c, GREEN_MED, GREEN_DARK)
    draw_para(c, "O Que Falta no Mercado", 50, H - 55, W - 100, S_SLIDE_TITLE_W)

    gaps = [
        "<b>1. Plataforma unica campo-a-balanco:</b> Nenhum concorrente cobre da operacao de campo ate o DRE fiscal num so lugar.",
        "<b>2. Precificacao modular real:</b> Players cobram pacote fechado. Produtor de soja paga por modulo de gado que nunca usa.",
        "<b>3. Multi-fazenda + multi-CNPJ:</b> Grupos com 3-5 fazendas precisam consolidar dados. Quase nenhum sistema faz isso bem.",
        "<b>4. Integracao agricultura + pecuaria + financeiro:</b> Custos cruzados (ex: pasto formado com insumo agricola) sao invisiveis.",
        "<b>5. Acessivel para pequeno e medio:</b> Solucoes enterprise excluem 90% do mercado. Solucoes simples nao escalam.",
        "<b>6. Conformidade fiscal embutida:</b> LCDPR, Carne-Leao, SPED integrados ao fluxo, nao como modulo separado caro.",
    ]

    yy = H - 110
    for g in gaps:
        ph = draw_para(c, g, 70, yy, W - 140, S_BULLET_W)
        yy -= ph + 12


# ============================
# SLIDE 6 — NOSSA SOLUÇÃO
# ============================
def slide_solucao(c):
    draw_bg(c, GRAY_LIGHT)
    draw_para(c, "AgroSaaS: A Solucao Completa", 50, H - 50, W - 100, S_SLIDE_TITLE)
    draw_para(c, "Uma plataforma modular que cobre toda a operacao rural — do planejamento de safra ao balanco financeiro.",
              50, H - 95, W - 100, S_BODY)

    modules = [
        ("Agricola", "Safras, campo, colheita,\nbeneficiamento, NDVI,\nrastreabilidade"),
        ("Pecuaria", "Rebanho, genetica,\nconfinamento, leite,\nmanejo sanitario"),
        ("Financeiro", "Tesouraria, custos ABC,\nfiscal (SPED/NF-e),\nhedging e barter"),
        ("Imoveis", "Cadastro, documentos,\narrendamentos,\navaliacao patrimonial"),
        ("Operacional", "Frota, estoque,\noficina, compras,\nRH e folha"),
    ]

    cw = (W - 100 - 40) / 5
    ch = 130
    sx = 50
    for i, (t, b) in enumerate(modules):
        x = sx + i * (cw + 10)
        draw_card(c, x, H - 280, cw, ch, t, b, icon="&#x2713;")

    features = [
        "<b>Multi-tenant:</b> Cada produtor tem seu espaco isolado e seguro.",
        "<b>Multi-fazenda:</b> Consolide dados de todas as propriedades num so painel.",
        "<b>Modular:</b> Pague apenas pelos modulos que usa. Escale quando crescer.",
        "<b>Cloud-native:</b> Acesse de qualquer lugar. Dados seguros na nuvem.",
    ]
    yy = H - 330
    for f in features:
        ph = draw_para(c, f, 70, yy, W - 140, S_BULLET)
        yy -= ph + 8


# ============================
# SLIDE 7 — DIFERENCIAIS
# ============================
def slide_diferenciais(c):
    draw_bg(c)
    draw_para(c, "Por Que o AgroSaaS e a Melhor Opcao", 50, H - 50, W - 100, S_SLIDE_TITLE)

    diffs = [
        ("Campo ao Balanco",
         "Unica plataforma que integra operacao de campo, estoque, beneficiamento e contabilidade fiscal num so fluxo."),
        ("Preco Justo e Modular",
         "3 tiers (Basico, Profissional, Premium) + modulos avulsos. Produtor pequeno paga pouco; grande paga pelo que usa."),
        ("Multi-Fazenda Nativo",
         "Grupos rurais consolidam todas as fazendas. Troque de propriedade com um clique. DRE por fazenda ou consolidado."),
        ("Seguranca Enterprise",
         "Isolamento por tenant, RBAC granular, permissoes por fazenda, auditoria completa. Dados nunca vazam entre clientes."),
        ("Rapido de Implantar",
         "SaaS puro: cadastrou, usou. Sem consultoria de 6 meses. Onboarding guiado com wizard inteligente."),
        ("Conformidade Integrada",
         "LCDPR, Carne-Leao, NF-e, SPED: gerados automaticamente a partir dos lancamentos. Contador recebe tudo pronto."),
    ]

    cols = 3
    cw = (W - 100 - 30) / cols
    ch = 130
    for i, (t, b) in enumerate(diffs):
        col = i % cols
        row = i // cols
        x = 50 + col * (cw + 15)
        y = H - 165 - row * (ch + 15)
        draw_card(c, x, y, cw, ch, t, b, icon="&#x2605;")


# ============================
# SLIDE 8 — PLANOS
# ============================
def slide_planos(c):
    draw_bg(c, GRAY_LIGHT)
    draw_para(c, "Planos e Precificacao", 50, H - 50, W - 100, S_SLIDE_TITLE)
    draw_para(c, "Modular. Flexivel. Justo.",
              50, H - 88, W - 100, style("ps", 15, GRAY_MED))

    plans = [
        ("BASICO", "R$ 149/mes", [
            "Core + Cadastros",
            "1 modulo incluso",
            "Ate 3 fazendas",
            "Suporte por email",
            "Dashboard basico",
        ]),
        ("PROFISSIONAL", "R$ 349/mes", [
            "Tudo do Basico +",
            "3 modulos inclusos",
            "Fazendas ilimitadas",
            "Custos ABC + Rateio",
            "Suporte prioritario",
        ]),
        ("PREMIUM", "R$ 699/mes", [
            "Tudo do Profissional +",
            "Modulos ilimitados",
            "NDVI + IoT + IA",
            "API aberta",
            "Gerente de conta dedicado",
        ]),
    ]

    pw = 220
    gap = 30
    sx = (W - (pw * 3 + gap * 2)) / 2
    for i, (name, price, feats) in enumerate(plans):
        x = sx + i * (pw + gap)
        y = 60
        h = H - 160
        is_pro = (i == 1)

        if is_pro:
            c.setFillColor(GREEN_DARK)
            c.roundRect(x - 4, y - 4, pw + 8, h + 28, 10, fill=1, stroke=0)

        c.setFillColor(WHITE)
        c.roundRect(x, y, pw, h, 8, fill=1, stroke=0)

        if is_pro:
            c.setFillColor(ACCENT)
            c.roundRect(x + 50, y + h - 2, pw - 100, 22, 6, fill=1, stroke=0)
            draw_para(c, "MAIS POPULAR", x + 50, y + h + 16, pw - 100,
                      style("pop", 10, WHITE, TA_CENTER, True))

        draw_para(c, name, x, y + h - 45, pw, style("pn", 16, GREEN_DARK, TA_CENTER, True))
        draw_para(c, price, x, y + h - 72, pw, style("pp", 24, GRAY_DARK, TA_CENTER, True))

        fy = y + h - 110
        for feat in feats:
            draw_para(c, f"&#x2713;  {feat}", x + 20, fy, pw - 40, style("pf", 12, GRAY_MED, leading=17))
            fy -= 22


# ============================
# SLIDE 9 — ROADMAP
# ============================
def slide_roadmap(c):
    draw_bg(c)
    draw_para(c, "Roadmap 2026", 50, H - 50, W - 100, S_SLIDE_TITLE)

    phases = [
        ("Q1 2026 - Concluido", GREEN_LIGHT, [
            "Core + Auth + Multi-tenant",
            "Modulo Agricola completo",
            "Billing + Self-service signup",
            "22 submodulos agricolas",
        ]),
        ("Q2 2026 - Em Andamento", ACCENT, [
            "Modulo Financeiro completo",
            "Modulo Imoveis Rurais",
            "App Mobile (React Native)",
            "Integracao fiscal (NF-e)",
        ]),
        ("Q3 2026 - Planejado", GRAY_MED, [
            "Modulo Pecuaria",
            "Modulo Operacional",
            "IA Preditiva (previsoes)",
            "Marketplace de integracoes",
        ]),
        ("Q4 2026 - Visao", HexColor("#90A4AE"), [
            "API publica + webhooks",
            "White-label para cooperativas",
            "Internacionalizacao (LATAM)",
            "Certificacoes (ISO, SOC2)",
        ]),
    ]

    pw = (W - 100 - 45) / 4
    for i, (title, color, items) in enumerate(phases):
        x = 50 + i * (pw + 15)
        y = 60
        h = H - 160

        c.setFillColor(color)
        c.roundRect(x, y + h - 40, pw, 40, 8, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.rect(x, y + h - 40, pw, 8, fill=1, stroke=0)
        c.setFillColor(GRAY_LIGHT)
        c.roundRect(x, y, pw, h - 32, 8, fill=1, stroke=0)

        draw_para(c, f"<b>{title}</b>", x + 10, y + h - 10, pw - 20,
                  style("rt", 11, WHITE, bold=True))

        fy = y + h - 65
        for item in items:
            draw_para(c, f"&#x2022; {item}", x + 12, fy, pw - 24,
                      style("ri", 11, GRAY_DARK, leading=16))
            fy -= 22


# ============================
# SLIDE 10 — CTA
# ============================
def slide_cta(c):
    draw_gradient_bg(c, GREEN_DARK, GREEN_MED)
    draw_para(c, "Pronto para Transformar\nsua Gestao Rural?", 0, H/2 + 80, W,
              style("cta", 34, WHITE, TA_CENTER, True, leading=44))
    draw_para(c, "Agende uma demonstracao gratuita e veja o AgroSaaS em acao.",
              0, H/2 + 10, W, S_CTA_SUB)

    # Button
    bw, bh = 280, 50
    bx = (W - bw) / 2
    by = H/2 - 60
    c.setFillColor(ACCENT)
    c.roundRect(bx, by, bw, bh, 25, fill=1, stroke=0)
    draw_para(c, "<b>SOLICITAR DEMONSTRACAO</b>", bx, by + 35, bw,
              style("btn", 15, WHITE, TA_CENTER, True))

    draw_para(c, "contato@borgus.com.br  |  borgus.com.br  |  WhatsApp: (XX) XXXXX-XXXX",
              0, 60, W, style("contact", 13, HexColor("#A5D6A7"), TA_CENTER))
    draw_para(c, "Borgus Software Ltda - 2026", 0, 35, W,
              style("copy", 11, HexColor("#81C784"), TA_CENTER))


# ============================
# GERAR PDF
# ============================
def main():
    c = canvas.Canvas(OUT, pagesize=landscape(A4))
    c.setTitle("AgroSaaS - Apresentacao Comercial")
    c.setAuthor("Borgus Software Ltda")
    c.setSubject("Apresentacao comercial da plataforma AgroSaaS")

    slides = [
        slide_capa,
        slide_mercado,
        slide_dores,
        slide_concorrencia,
        slide_lacunas,
        slide_solucao,
        slide_diferenciais,
        slide_planos,
        slide_roadmap,
        slide_cta,
    ]

    for i, fn in enumerate(slides):
        if i > 0:
            new_slide(c)
        fn(c)

    c.save()
    print(f"PDF gerado: {OUT}")


if __name__ == "__main__":
    main()
