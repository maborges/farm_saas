"""
Seed: produtos padrão do sistema para tenants existentes.

Cria produtos realistas de entrada (insumos, peças, EPIs, etc.)
associados às marcas, modelos e categorias já existentes.

Uso:
    cd services/api
    source .venv/bin/activate
    PYTHONPATH=. python scripts/seed_produtos.py
"""
import asyncio
from sqlalchemy import select
from core.database import async_session_maker
import core.models  # noqa: F401

from core.cadastros.produtos.models import (
    Marca, ModeloProduto, CategoriaProduto, Produto,
    ProdutoAgricola, ProdutoEstoque, ProdutoEPI,
)
from core.models.tenant import Tenant

# ---------------------------------------------------------------------------
# Produtos padrão
# ---------------------------------------------------------------------------

PRODUTOS = [
    # ==================== SEMENTES ====================
    {
        "nome": "Soja Pioneer P10T20 IPRO",
        "tipo": "SEMENTE",
        "unidade_medida": "UN",
        "codigo_interno": "SEM-SOJA-P10T20",
        "descricao": "Semente de soja Pioneer P10T20 com tecnologia IPRO, ciclo médio, alta produtividade.",
        "marca": "Pioneer",
        "modelo": None,
        "categoria": "Sementes",
        "qtd_conteudo": 1.0,
        "unidade_conteudo": "UN",
        "estoque_minimo": 10.0,
        "preco_medio": 185.00,
        "detalhe_agricola": {
            "cultivar": "P10T20",
            "cultura_alvo": "SOJA",
            "pureza_pct": 99.0,
            "germinacao_pct": 95.0,
            "tsi": True,
        },
        "detalhe_estoque": {
            "peso_unitario_kg": 40.0,
            "perecivel": True,
            "prazo_validade_dias": 365,
            "ncm": "12019090",
            "lote_controlado": True,
        },
    },
    {
        "nome": "Milho Nidera NK 7059 IPRO",
        "tipo": "SEMENTE",
        "unidade_medida": "UN",
        "codigo_interno": "SEM-MILHO-NK7059",
        "descricao": "Semente de milho híbrido Nidera NK 7059 com tecnologia IPRO VT PRO3.",
        "marca": "Nidera",
        "modelo": "NK 7059 IPRO",
        "categoria": "Sementes",
        "qtd_conteudo": 1.0,
        "unidade_conteudo": "UN",
        "estoque_minimo": 20.0,
        "preco_medio": 220.00,
        "detalhe_agricola": {
            "cultivar": "NK 7059",
            "cultura_alvo": "MILHO",
            "pureza_pct": 99.5,
            "germinacao_pct": 96.0,
            "tsi": True,
        },
        "detalhe_estoque": {
            "peso_unitario_kg": 40.0,
            "perecivel": True,
            "prazo_validade_dias": 365,
            "ncm": "10059000",
            "lote_controlado": True,
        },
    },
    {
        "nome": "Soja TMG 1175 RR",
        "tipo": "SEMENTE",
        "unidade_medida": "UN",
        "codigo_interno": "SEM-SOJA-TMG1175",
        "descricao": "Semente de soja TMG 1175 RR, ciclo semiprecoce, excelente desempenho em cerrado.",
        "marca": "TMG",
        "modelo": None,
        "categoria": "Sementes",
        "qtd_conteudo": 1.0,
        "unidade_conteudo": "UN",
        "estoque_minimo": 10.0,
        "preco_medio": 165.00,
        "detalhe_agricola": {
            "cultivar": "TMG 1175",
            "cultura_alvo": "SOJA",
            "pureza_pct": 99.0,
            "germinacao_pct": 94.0,
            "tsi": False,
        },
        "detalhe_estoque": {
            "peso_unitario_kg": 40.0,
            "perecivel": True,
            "prazo_validade_dias": 365,
            "ncm": "12019090",
            "lote_controlado": True,
        },
    },

    # ==================== DEFENSIVOS - HERBICIDAS ====================
    {
        "nome": "Roundup Original DI 1L",
        "tipo": "DEFENSIVO",
        "unidade_medida": "UN",
        "codigo_interno": "DEF-GLI-RND-1L",
        "descricao": "Herbicida glifosato Roundup Original, pós-emergente, sistêmico, não seletivo. Embalagem 1L.",
        "marca": "Bayer",
        "modelo": "Roundup Original",
        "categoria": "Herbicidas",
        "qtd_conteudo": 1.0,
        "unidade_conteudo": "L",
        "estoque_minimo": 20.0,
        "preco_medio": 65.00,
        "detalhe_agricola": {
            "registro_mapa": "BR01987654321",
            "classe_agronomica": "HERBICIDA",
            "classe_toxicologica": "IV",
            "principio_ativo": "Glifosato",
            "formulacao": "SL",
            "periodo_carencia_dias": 30,
            "intervalo_reentrada_horas": 24,
            "epi_obrigatorio": ["luvas", "oculos", "mascara", "avental"],
            "cultura_alvo": "SOJA",
            "densidade_g_ml": 1.2,
        },
        "detalhe_estoque": {
            "localizacao_default": "Galpão A - Prateleira 3",
            "peso_unitario_kg": 1.2,
            "perecivel": True,
            "prazo_validade_dias": 730,
            "ncm": "38089329",
            "requer_receituario": False,
            "lote_controlado": True,
        },
    },
    {
        "nome": "Roundup WG 250g",
        "tipo": "DEFENSIVO",
        "unidade_medida": "UN",
        "codigo_interno": "DEF-GLI-RNDWG-250",
        "descricao": "Herbicida glifosato Roundup WG, formulação granular dispersível. Embalagem 250g.",
        "marca": "Bayer",
        "modelo": "Roundup WG",
        "categoria": "Herbicidas",
        "qtd_conteudo": 250.0,
        "unidade_conteudo": "G",
        "estoque_minimo": 15.0,
        "preco_medio": 55.00,
        "detalhe_agricola": {
            "registro_mapa": "BR01987654322",
            "classe_agronomica": "HERBICIDA",
            "classe_toxicologica": "IV",
            "principio_ativo": "Glifosato",
            "formulacao": "WG",
            "periodo_carencia_dias": 30,
            "intervalo_reentrada_horas": 12,
            "epi_obrigatorio": ["luvas", "oculos", "mascara"],
            "cultura_alvo": "SOJA",
        },
        "detalhe_estoque": {
            "localizacao_default": "Galpão A - Prateleira 3",
            "peso_unitario_kg": 0.25,
            "perecivel": True,
            "prazo_validade_dias": 730,
            "ncm": "38089329",
            "requer_receituario": False,
            "lote_controlado": True,
        },
    },
    {
        "nome": "Gramoxone 200 1L",
        "tipo": "DEFENSIVO",
        "unidade_medida": "UN",
        "codigo_interno": "DEF-PAR-GRX-1L",
        "descricao": "Herbicida de contato para dessecação pré-plantio. Embalagem 1L.",
        "marca": "Syngenta",
        "modelo": "Gramoxone 200",
        "categoria": "Herbicidas",
        "qtd_conteudo": 1.0,
        "unidade_conteudo": "L",
        "estoque_minimo": 10.0,
        "preco_medio": 78.00,
        "detalhe_agricola": {
            "registro_mapa": "BR01987654323",
            "classe_agronomica": "HERBICIDA",
            "classe_toxicologica": "III",
            "principio_ativo": "Paraquate",
            "formulacao": "SL",
            "periodo_carencia_dias": 0,
            "intervalo_reentrada_horas": 48,
            "epi_obrigatorio": ["luvas", "oculos", "mascara", "avental", "bota"],
            "cultura_alvo": "SOJA",
            "densidade_g_ml": 1.1,
        },
        "detalhe_estoque": {
            "localizacao_default": "Galpão A - Prateleira 2",
            "peso_unitario_kg": 1.1,
            "perecivel": True,
            "prazo_validade_dias": 730,
            "ncm": "38089290",
            "requer_receituario": True,
            "lote_controlado": True,
        },
    },

    # ==================== DEFENSIVOS - FUNGICIDAS ====================
    {
        "nome": "Elatus 200g",
        "tipo": "DEFENSIVO",
        "unidade_medida": "UN",
        "codigo_interno": "DEF-FUN-ELA-200",
        "descricao": "Fungicida sistêmico para controle de doenças foliares em soja e trigo. Embalagem 200g.",
        "marca": "Syngenta",
        "modelo": "Elatus",
        "categoria": "Fungicidas",
        "qtd_conteudo": 200.0,
        "unidade_conteudo": "G",
        "estoque_minimo": 15.0,
        "preco_medio": 250.00,
        "detalhe_agricola": {
            "registro_mapa": "BR01987654324",
            "classe_agronomica": "FUNGICIDA",
            "classe_toxicologica": "IV",
            "principio_ativo": "Benzovindiflupir + Azoxistrobina",
            "formulacao": "WG",
            "periodo_carencia_dias": 28,
            "intervalo_reentrada_horas": 24,
            "epi_obrigatorio": ["luvas", "oculos", "mascara"],
            "cultura_alvo": "SOJA",
        },
        "detalhe_estoque": {
            "localizacao_default": "Galpão A - Prateleira 5",
            "peso_unitario_kg": 0.2,
            "perecivel": True,
            "prazo_validade_dias": 730,
            "ncm": "38089219",
            "requer_receituario": True,
            "lote_controlado": True,
        },
    },
    {
        "nome": "Priori Xtra 1L",
        "tipo": "DEFENSIVO",
        "unidade_medida": "UN",
        "codigo_interno": "DEF-FUN-PRI-1L",
        "descricao": "Fungicida preventivo e curativo para ferrugem asiática da soja. Embalagem 1L.",
        "marca": "Bayer",
        "modelo": "Priori Xtra",
        "categoria": "Fungicidas",
        "qtd_conteudo": 1.0,
        "unidade_conteudo": "L",
        "estoque_minimo": 10.0,
        "preco_medio": 320.00,
        "detalhe_agricola": {
            "registro_mapa": "BR01987654325",
            "classe_agronomica": "FUNGICIDA",
            "classe_toxicologica": "IV",
            "principio_ativo": "Azoxistrobina + Ciproconazol",
            "formulacao": "SC",
            "periodo_carencia_dias": 28,
            "intervalo_reentrada_horas": 24,
            "epi_obrigatorio": ["luvas", "oculos", "mascara"],
            "cultura_alvo": "SOJA",
            "densidade_g_ml": 1.05,
        },
        "detalhe_estoque": {
            "localizacao_default": "Galpão A - Prateleira 5",
            "peso_unitario_kg": 1.05,
            "perecivel": True,
            "prazo_validade_dias": 730,
            "ncm": "38089219",
            "requer_receituario": True,
            "lote_controlado": True,
        },
    },
    {
        "nome": "Comet 1L",
        "tipo": "DEFENSIVO",
        "unidade_medida": "UN",
        "codigo_interno": "DEF-FUN-COM-1L",
        "descricao": "Fungicida estrobilurina para controle de doenças em soja, milho e trigo. Embalagem 1L.",
        "marca": "BASF",
        "modelo": "Comet",
        "categoria": "Fungicidas",
        "qtd_conteudo": 1.0,
        "unidade_conteudo": "L",
        "estoque_minimo": 10.0,
        "preco_medio": 195.00,
        "detalhe_agricola": {
            "registro_mapa": "BR01987654326",
            "classe_agronomica": "FUNGICIDA",
            "classe_toxicologica": "IV",
            "principio_ativo": "Piraclostrobina",
            "formulacao": "EC",
            "periodo_carencia_dias": 30,
            "intervalo_reentrada_horas": 24,
            "epi_obrigatorio": ["luvas", "oculos", "mascara"],
            "cultura_alvo": "SOJA",
            "densidade_g_ml": 0.98,
        },
        "detalhe_estoque": {
            "localizacao_default": "Galpão A - Prateleira 5",
            "peso_unitario_kg": 0.98,
            "perecivel": True,
            "prazo_validade_dias": 730,
            "ncm": "38089219",
            "requer_receituario": True,
            "lote_controlado": True,
        },
    },

    # ==================== DEFENSIVOS - INSETICIDAS ====================
    {
        "nome": "Talstar 100 EC 1L",
        "tipo": "DEFENSIVO",
        "unidade_medida": "UN",
        "codigo_interno": "DEF-INS-TAL-1L",
        "descricao": "Inseticida piretroide de amplo espectro para controle de pragas. Embalagem 1L.",
        "marca": "FMC",
        "modelo": "Talstar 100 EC",
        "categoria": "Inseticidas",
        "qtd_conteudo": 1.0,
        "unidade_conteudo": "L",
        "estoque_minimo": 10.0,
        "preco_medio": 110.00,
        "detalhe_agricola": {
            "registro_mapa": "BR01987654327",
            "classe_agronomica": "INSETICIDA",
            "classe_toxicologica": "III",
            "principio_ativo": "Bifentrina",
            "formulacao": "EC",
            "periodo_carencia_dias": 14,
            "intervalo_reentrada_horas": 24,
            "epi_obrigatorio": ["luvas", "oculos", "mascara", "avental"],
            "cultura_alvo": "SOJA",
            "densidade_g_ml": 0.9,
        },
        "detalhe_estoque": {
            "localizacao_default": "Galpão A - Prateleira 4",
            "peso_unitario_kg": 0.9,
            "perecivel": True,
            "prazo_validade_dias": 730,
            "ncm": "38089190",
            "requer_receituario": True,
            "lote_controlado": True,
        },
    },

    # ==================== FERTILIZANTES ====================
    {
        "nome": "Fertilizante NPK 10-10-10 50kg",
        "tipo": "FERTILIZANTE",
        "unidade_medida": "UN",
        "codigo_interno": "FERT-NPK-10-10-10",
        "descricao": "Fertilizante mineral NPK formulação 10-10-10 para adubação de plantio. Saco 50kg.",
        "marca": "Mosaic",
        "modelo": None,
        "categoria": "Fertilizantes Sólidos",
        "qtd_conteudo": 50.0,
        "unidade_conteudo": "KG",
        "estoque_minimo": 100.0,
        "preco_medio": 135.00,
        "detalhe_agricola": {
            "composicao_npk": "10-10-10",
        },
        "detalhe_estoque": {
            "localizacao_default": "Galpão B - Piso",
            "peso_unitario_kg": 50.0,
            "perecivel": False,
            "ncm": "31052010",
        },
    },
    {
        "nome": "Fertilizante NPK 04-14-08 50kg",
        "tipo": "FERTILIZANTE",
        "unidade_medida": "UN",
        "codigo_interno": "FERT-NPK-04-14-08",
        "descricao": "Fertilizante mineral NPK formulação 04-14-08 para adubação de plantio. Saco 50kg.",
        "marca": "Yara",
        "modelo": None,
        "categoria": "Fertilizantes Sólidos",
        "qtd_conteudo": 50.0,
        "unidade_conteudo": "KG",
        "estoque_minimo": 100.0,
        "preco_medio": 140.00,
        "detalhe_agricola": {
            "composicao_npk": "04-14-08",
        },
        "detalhe_estoque": {
            "localizacao_default": "Galpão B - Piso",
            "peso_unitario_kg": 50.0,
            "perecivel": False,
            "ncm": "31052010",
        },
    },
    {
        "nome": "Fertilizante MAP 18-46-00 50kg",
        "tipo": "FERTILIZANTE",
        "unidade_medida": "UN",
        "codigo_interno": "FERT-MAP-18-46",
        "descricao": "Fertilizante fosfatado MAP (Monoamônio Fosfato) 18-46-00. Saco 50kg.",
        "marca": "Mosaic",
        "modelo": None,
        "categoria": "Fertilizantes Sólidos",
        "qtd_conteudo": 50.0,
        "unidade_conteudo": "KG",
        "estoque_minimo": 50.0,
        "preco_medio": 165.00,
        "detalhe_agricola": {
            "composicao_npk": "18-46-00",
        },
        "detalhe_estoque": {
            "localizacao_default": "Galpão B - Piso",
            "peso_unitario_kg": 50.0,
            "perecivel": False,
            "ncm": "31053000",
        },
    },
    {
        "nome": "Fertilizante Foliar YaraVita 1L",
        "tipo": "FERTILIZANTE",
        "unidade_medida": "UN",
        "codigo_interno": "FERT-FOL-YARA-1L",
        "descricao": "Fertilizante foliar com micronutrientes quelatizados para aplicação foliar. Embalagem 1L.",
        "marca": "Yara",
        "modelo": None,
        "categoria": "Foliares",
        "qtd_conteudo": 1.0,
        "unidade_conteudo": "L",
        "estoque_minimo": 20.0,
        "preco_medio": 85.00,
        "detalhe_agricola": {
            "densidade_g_ml": 1.3,
        },
        "detalhe_estoque": {
            "localizacao_default": "Galpão A - Prateleira 6",
            "peso_unitario_kg": 1.3,
            "perecivel": False,
            "ncm": "31059090",
        },
    },

    # ==================== ADJUVANTES ====================
    {
        "nome": "Adjuvante Agral 1L",
        "tipo": "ADJUVANTE",
        "unidade_medida": "UN",
        "codigo_interno": "ADJ-AGR-1L",
        "descricao": "Adjuvante não iônico para melhorar a aderência e espalhamento de calda. Embalagem 1L.",
        "marca": "Syngenta",
        "modelo": None,
        "categoria": "Adjuvantes",
        "qtd_conteudo": 1.0,
        "unidade_conteudo": "L",
        "estoque_minimo": 15.0,
        "preco_medio": 42.00,
        "detalhe_agricola": {
            "densidade_g_ml": 1.0,
        },
        "detalhe_estoque": {
            "localizacao_default": "Galpão A - Prateleira 7",
            "peso_unitario_kg": 1.0,
            "perecivel": False,
            "ncm": "38089999",
        },
    },

    # ==================== LUBRIFICANTES ====================
    {
        "nome": "Rimula R4 X 15W-40 20L",
        "tipo": "LUBRIFICANTE",
        "unidade_medida": "UN",
        "codigo_interno": "LUB-MOT-RIM-20L",
        "descricao": "Óleo lubrificante diesel Shell Rimula R4 X 15W-40. Balde 20L.",
        "marca": "Shell",
        "modelo": "Rimula R4 X 15W-40",
        "categoria": "Lubrificantes e Filtros",
        "qtd_conteudo": 20.0,
        "unidade_conteudo": "L",
        "estoque_minimo": 5.0,
        "preco_medio": 310.00,
        "detalhe_estoque": {
            "localizacao_default": "Galpão C - Prateleira 1",
            "peso_unitario_kg": 18.0,
            "perecivel": False,
            "ncm": "27101922",
        },
    },
    {
        "nome": "Helix HX7 10W-40 1L",
        "tipo": "LUBRIFICANTE",
        "unidade_medida": "UN",
        "codigo_interno": "LUB-MOT-HEL-1L",
        "descricao": "Óleo lubrificante para motores a gasolina Shell Helix HX7 10W-40. Embalagem 1L.",
        "marca": "Shell",
        "modelo": "Helix HX7 10W-40",
        "categoria": "Lubrificantes e Filtros",
        "qtd_conteudo": 1.0,
        "unidade_conteudo": "L",
        "estoque_minimo": 10.0,
        "preco_medio": 45.00,
        "detalhe_estoque": {
            "localizacao_default": "Galpão C - Prateleira 1",
            "peso_unitario_kg": 0.85,
            "perecivel": False,
            "ncm": "27101922",
        },
    },
    {
        "nome": "Delvac MX 15W-40 20L",
        "tipo": "LUBRIFICANTE",
        "unidade_medida": "UN",
        "codigo_interno": "LUB-MOT-DEL-20L",
        "descricao": "Óleo lubrificante diesel Mobil Delvac MX 15W-40. Balde 20L.",
        "marca": "Mobil",
        "modelo": "Delvac MX 15W-40",
        "categoria": "Lubrificantes e Filtros",
        "qtd_conteudo": 20.0,
        "unidade_conteudo": "L",
        "estoque_minimo": 5.0,
        "preco_medio": 295.00,
        "detalhe_estoque": {
            "localizacao_default": "Galpão C - Prateleira 2",
            "peso_unitario_kg": 18.0,
            "perecivel": False,
            "ncm": "27101922",
        },
    },

    # ==================== COMBUSTÍVEL ====================
    {
        "nome": "Diesel S10 (litro)",
        "tipo": "COMBUSTIVEL",
        "unidade_medida": "L",
        "codigo_interno": "COM-DIESEL-S10",
        "descricao": "Diesel S10 para tratores e máquinas agrícolas. Preço por litro.",
        "marca": None,
        "modelo": None,
        "categoria": "Combustíveis",
        "qtd_conteudo": 1.0,
        "unidade_conteudo": "L",
        "estoque_minimo": 1000.0,
        "preco_medio": 6.15,
        "detalhe_estoque": {
            "localizacao_default": "Tanque de combustível",
            "perecivel": False,
            "ncm": "27101921",
            "lote_controlado": False,
        },
    },

    # ==================== PEÇAS ====================
    {
        "nome": "Filtro de óleo motor JD RE522651",
        "tipo": "PECA",
        "unidade_medida": "UN",
        "codigo_interno": "PEC-FIL-JD-RE522651",
        "descricao": "Filtro de óleo do motor John Deere. Ref: RE522651. Compatível com Série 6M e 7J.",
        "marca": "John Deere",
        "modelo": None,
        "categoria": "Peças de Reposição",
        "estoque_minimo": 4.0,
        "preco_medio": 65.00,
        "detalhe_estoque": {
            "localizacao_default": "Almoxarifado - Estante 4",
            "peso_unitario_kg": 0.5,
            "perecivel": False,
            "ncm": "84212300",
        },
    },
    {
        "nome": "Filtro de ar JD JD1000",
        "tipo": "PECA",
        "unidade_medida": "UN",
        "codigo_interno": "PEC-FIL-AR-JD1000",
        "descricao": "Filtro de ar para tratores John Deere. Ref: JD1000.",
        "marca": "John Deere",
        "modelo": None,
        "categoria": "Peças de Reposição",
        "estoque_minimo": 4.0,
        "preco_medio": 120.00,
        "detalhe_estoque": {
            "localizacao_default": "Almoxarifado - Estante 4",
            "peso_unitario_kg": 0.8,
            "perecivel": False,
            "ncm": "84213100",
        },
    },
    {
        "nome": "Correia dentada John Deere Série 5E",
        "tipo": "PECA",
        "unidade_medida": "UN",
        "codigo_interno": "PEC-COR-JD-5E",
        "descricao": "Correia dentada para trator John Deere Série 5E.",
        "marca": "John Deere",
        "modelo": "Série 5E",
        "categoria": "Pneus e Correias",
        "estoque_minimo": 2.0,
        "preco_medio": 185.00,
        "detalhe_estoque": {
            "localizacao_default": "Almoxarifado - Estante 5",
            "peso_unitario_kg": 1.2,
            "perecivel": False,
            "ncm": "40103990",
        },
    },

    # ==================== EPIs ====================
    {
        "nome": "Luva Nitrílica Cano Longo",
        "tipo": "EPI",
        "unidade_medida": "UN",
        "codigo_interno": "EPI-LUV-NIT-CL",
        "descricao": "Luva de nitrila cano longo para manuseio de defensivos agrícolas. Par.",
        "marca": "3M",
        "modelo": None,
        "categoria": "EPI",
        "estoque_minimo": 20.0,
        "preco_medio": 25.00,
        "detalhe_epi": {
            "tipo_protecao": "MAOS",
            "vida_util_meses": 6,
            "tamanho": "M",
        },
        "detalhe_estoque": {
            "localizacao_default": "Almoxarifado - Estante 10",
            "perecivel": False,
            "ncm": "40151100",
        },
    },
    {
        "nome": "Óculos de Proteção Antiembaçante",
        "tipo": "EPI",
        "unidade_medida": "UN",
        "codigo_interno": "EPI-OCU-ANT-001",
        "descricao": "Óculos de proteção com lentes antiembaçantes e antivisco. Uso com agroquímicos.",
        "marca": "3M",
        "modelo": None,
        "categoria": "EPI",
        "estoque_minimo": 15.0,
        "preco_medio": 35.00,
        "detalhe_epi": {
            "tipo_protecao": "OLHOS",
            "vida_util_meses": 24,
            "tamanho": "UNICO",
        },
        "detalhe_estoque": {
            "localizacao_default": "Almoxarifado - Estante 10",
            "perecivel": False,
            "ncm": "90049090",
        },
    },
    {
        "nome": "Respirador Semi-Facial P2",
        "tipo": "EPI",
        "unidade_medida": "UN",
        "codigo_interno": "EPI-MAS-P2-001",
        "descricao": "Respirador semi-facial com filtro P2 para proteção contra vapores orgânicos. Com refil.",
        "marca": "3M",
        "modelo": None,
        "categoria": "EPI",
        "estoque_minimo": 10.0,
        "preco_medio": 89.00,
        "detalhe_epi": {
            "tipo_protecao": "RESPIRATORIO",
            "vida_util_meses": 36,
            "tamanho": "M",
        },
        "detalhe_estoque": {
            "localizacao_default": "Almoxarifado - Estante 11",
            "perecivel": False,
            "ncm": "90200000",
        },
    },
    {
        "nome": "Avental Impermeável PVC",
        "tipo": "EPI",
        "unidade_medida": "UN",
        "codigo_interno": "EPI-AVE-PVC-001",
        "descricao": "Avental impermeável em PVC para manuseio de defensivos. Comprimento 90cm.",
        "marca": "3M",
        "modelo": None,
        "categoria": "EPI",
        "estoque_minimo": 10.0,
        "preco_medio": 55.00,
        "detalhe_epi": {
            "tipo_protecao": "CORPO",
            "vida_util_meses": 12,
            "tamanho": "UNICO",
        },
        "detalhe_estoque": {
            "localizacao_default": "Almoxarifado - Estante 11",
            "perecivel": False,
            "ncm": "39269090",
        },
    },
    {
        "nome": "Bota de Borracha Cano Alto",
        "tipo": "EPI",
        "unidade_medida": "UN",
        "codigo_interno": "EPI-BOT-BOR-CA",
        "descricao": "Bota de borracha cano alto com solado antiderrapante. Para uso no campo.",
        "marca": "3M",
        "modelo": None,
        "categoria": "EPI",
        "estoque_minimo": 10.0,
        "preco_medio": 75.00,
        "detalhe_epi": {
            "tipo_protecao": "PES",
            "vida_util_meses": 18,
            "tamanho": "G",
        },
        "detalhe_estoque": {
            "localizacao_default": "Almoxarifado - Estante 12",
            "perecivel": False,
            "ncm": "64019900",
        },
    },

    # ==================== PECUÁRIA - RAÇÃO ====================
    {
        "nome": "Ração Bovino de Corte Engorda 50kg",
        "tipo": "RACAO",
        "unidade_medida": "UN",
        "codigo_interno": "PEC-RAC-BC-ENG",
        "descricao": "Ração para bovinos de corte em fase de engorda. Saco 50kg. Proteína bruta 22%.",
        "marca": None,
        "modelo": None,
        "categoria": "Rações e Suplementos",
        "qtd_conteudo": 50.0,
        "unidade_conteudo": "KG",
        "estoque_minimo": 30.0,
        "preco_medio": 95.00,
        "detalhe_estoque": {
            "localizacao_default": "Galpão D - Piso",
            "peso_unitario_kg": 50.0,
            "perecivel": True,
            "prazo_validade_dias": 90,
            "ncm": "23099010",
        },
    },
    {
        "nome": "Sal Mineralizado para Bovinos 50kg",
        "tipo": "MINERAL",
        "unidade_medida": "UN",
        "codigo_interno": "PEC-SAL-MIN-50",
        "descricao": "Sal mineralizado com fósforo, cálcio e oligoelementos. Saco 50kg.",
        "marca": None,
        "modelo": None,
        "categoria": "Minerais e Sal",
        "qtd_conteudo": 50.0,
        "unidade_conteudo": "KG",
        "estoque_minimo": 20.0,
        "preco_medio": 68.00,
        "detalhe_estoque": {
            "localizacao_default": "Galpão D - Piso",
            "peso_unitario_kg": 50.0,
            "perecivel": False,
            "ncm": "25010010",
        },
    },

    # ==================== SERVIÇO ====================
    {
        "nome": "Serviço de Manutenção Trator (hora)",
        "tipo": "SERVICO",
        "unidade_medida": "H",
        "codigo_interno": "SRV-MAN-TRATOR",
        "descricao": "Serviço de manutenção preventiva ou corretiva para tratores. Cobrado por hora.",
        "marca": None,
        "modelo": None,
        "categoria": "Material Geral",
        "estoque_minimo": 0.0,
        "preco_medio": 150.00,
    },

    # ==================== MATERIAL GERAL ====================
    {
        "nome": "Tampão Auricular de Silicone",
        "tipo": "EPI",
        "unidade_medida": "UN",
        "codigo_interno": "EPI-TAM-SIL-001",
        "descricao": "Protetor auricular tipo plug em silicone. Par. NRRsf 22dB.",
        "marca": "3M",
        "modelo": None,
        "categoria": "EPI",
        "estoque_minimo": 20.0,
        "preco_medio": 18.00,
        "detalhe_epi": {
            "tipo_protecao": "AUDITIVO",
            "vida_util_meses": 6,
            "tamanho": "UNICO",
        },
        "detalhe_estoque": {
            "localizacao_default": "Almoxarifado - Estante 12",
            "perecivel": False,
            "ncm": "39269090",
        },
    },
]


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------

async def seed():
    async with async_session_maker() as session:
        # Carregar tenants
        stmt_tenants = select(Tenant)
        tenants = list((await session.execute(stmt_tenants)).scalars().all())
        if not tenants:
            print("Nenhum tenant encontrado. Crie um tenant antes de rodar este seed.")
            return

        print(f"Tenants encontrados: {len(tenants)}")
        for t in tenants:
            print(f"  - {t.id} | {getattr(t, 'nome', getattr(t, 'razao_social', 'N/A'))}")

        # Carregar marcas (sistema)
        marca_map: dict[str, object] = {}
        stmt = select(Marca).where(Marca.tenant_id.is_(None))
        for m in (await session.execute(stmt)).scalars().all():
            marca_map[m.nome] = m

        # Carregar modelos (sistema)
        modelo_map: dict[str, object] = {}
        stmt = select(ModeloProduto)
        for mod in (await session.execute(stmt)).scalars().all():
            modelo_map[mod.nome] = mod

        # Carregar categorias (sistema)
        cat_map: dict[str, object] = {}
        stmt = select(CategoriaProduto)
        for c in (await session.execute(stmt)).scalars().all():
            cat_map[c.nome] = c

        for tenant in tenants:
            print(f"\n── Produtos para tenant {tenant.id} ──────────────")

            for item in PRODUTOS:
                marca_nome = item.pop("marca", None)
                modelo_nome = item.pop("modelo", None)
                cat_nome = item.pop("categoria", None)
                detalhe_agricola = item.pop("detalhe_agricola", None)
                detalhe_estoque = item.pop("detalhe_estoque", None)
                detalhe_epi = item.pop("detalhe_epi", None)

                # Resolver FK marca
                marca_obj = None
                if marca_nome:
                    marca_obj = marca_map.get(marca_nome)
                    if not marca_obj:
                        print(f"  ✗ Marca '{marca_nome}' não encontrada para {item['nome']}")
                        continue

                # Resolver FK modelo
                modelo_obj = None
                if modelo_nome:
                    modelo_obj = modelo_map.get(modelo_nome)
                    if not modelo_obj:
                        print(f"  ⚠ Modelo '{modelo_nome}' não encontrado para {item['nome']}")

                # Resolver FK categoria
                categoria_obj = None
                if cat_nome:
                    categoria_obj = cat_map.get(cat_nome)
                    if not categoria_obj:
                        print(f"  ✗ Categoria '{cat_nome}' não encontrada para {item['nome']}")
                        continue

                # Verificar se já existe pelo codigo_interno neste tenant
                stmt = select(Produto).where(
                    Produto.codigo_interno == item["codigo_interno"],
                    Produto.tenant_id == tenant.id,
                )
                existing = (await session.execute(stmt)).scalar_one_or_none()
                if existing:
                    print(f"  ✓ {item['nome']} já existe")
                    # Re-pop keys for next tenant iteration
                    item["marca"] = marca_nome
                    item["modelo"] = modelo_nome
                    item["categoria"] = cat_nome
                    if detalhe_agricola:
                        item["detalhe_agricola"] = detalhe_agricola
                    if detalhe_estoque:
                        item["detalhe_estoque"] = detalhe_estoque
                    if detalhe_epi:
                        item["detalhe_epi"] = detalhe_epi
                    continue

                produto = Produto(
                    tenant_id=tenant.id,
                    marca_id=marca_obj.id if marca_obj else None,
                    modelo_id=modelo_obj.id if modelo_obj else None,
                    categoria_id=categoria_obj.id if categoria_obj else None,
                    ativo=True,
                    **item,
                )
                session.add(produto)
                await session.flush()

                # Extensão agrícola
                if detalhe_agricola:
                    ext = ProdutoAgricola(produto_id=produto.id, **detalhe_agricola)
                    session.add(ext)

                # Extensão estoque
                if detalhe_estoque:
                    ext = ProdutoEstoque(produto_id=produto.id, **detalhe_estoque)
                    session.add(ext)

                # Extensão EPI
                if detalhe_epi:
                    ext = ProdutoEPI(produto_id=produto.id, **detalhe_epi)
                    session.add(ext)

                print(f"  + {item['nome']} criado")

                # Re-pop keys for next tenant
                item["marca"] = marca_nome
                item["modelo"] = modelo_nome
                item["categoria"] = cat_nome
                if detalhe_agricola:
                    item["detalhe_agricola"] = detalhe_agricola
                if detalhe_estoque:
                    item["detalhe_estoque"] = detalhe_estoque
                if detalhe_epi:
                    item["detalhe_epi"] = detalhe_epi

        await session.commit()
    print("\nSeed de produtos concluído.")


if __name__ == "__main__":
    asyncio.run(seed())
