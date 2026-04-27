from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
import uuid

from core.constants import PlanTier
from core.dependencies import get_session, get_current_user, require_module, require_tier
from core.models.tenant import Tenant

router = APIRouter(prefix="/reports", tags=["Relatórios"])

@router.get("/agricola/summary")
async def get_agricola_summary_report(
    session: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
    _module: None = Depends(require_module("A1_PLANEJAMENTO")),
    _tier: None = Depends(require_tier(PlanTier.PROFISSIONAL)),
):
    """Consolidado de dados agrícolas para relatórios."""
    # Simulação de agregação de dados reais dos módulos (Safra, Operações, Talhões)
    # Em produção, cruzaríamos dados de agricola.safras, agricola.operacoes, etc.
    
    return {
        "resumo": {
            "total_hectares": 1250.5,
            "safras_ativas": 2,
            "custo_medio_ha": 3450.80,
            "previsao_colheita_ton": 8400
        },
        "produtividade_por_cultura": [
            {"cultura": "Soja", "area": 800, "produtividade": 62, "unidade": "sc/ha"},
            {"cultura": "Milho Safrinha", "area": 450, "produtividade": 115, "unidade": "sc/ha"}
        ],
        "uso_insumos": [
            {"insumo": "Fertilizante NPK", "quantidade": 250, "unidade": "ton", "custo": 450000},
            {"insumo": "Sementes Variedade X", "quantidade": 1200, "unidade": "bag", "custo": 320000},
            {"insumo": "Herbicida Seletivo", "quantidade": 850, "unidade": "litros", "custo": 125000}
        ],
        "cronograma_atividades": [
            {"data": "2026-03-15", "atividade": "Aplicação de Fungicida", "status": "PENDENTE"},
            {"data": "2026-03-20", "atividade": "Monitoramento de Pragas", "status": "AGENDADO"},
            {"data": "2026-04-05", "atividade": "Início da Colheita", "status": "PLANEJADO"}
        ]
    }

@router.get("/pecuaria/summary")
async def get_pecuaria_summary_report(
    session: AsyncSession = Depends(get_session),
    user = Depends(get_current_user)
):
    """Consolidado de dados zootécnicos."""
    return {
        "rebanho": {
            "total_cabecas": 2450,
            "ua_total": 1850.5, # Unidade Animal
            "gmd_medio": 0.850, # Ganho Médio Diário (kg)
            "lotes_ativos": 12
        },
        "composicao_categorias": [
            {"categoria": "Bezerros", "quantidade": 850},
            {"categoria": "Novilhas", "quantidade": 600},
            {"categoria": "Touros", "quantidade": 50},
            {"categoria": "Vacas", "quantidade": 950}
        ],
        "sanitario_pendente": 145, # Animais com vacina atrasada
        "estoque_pastagem": {
            "disponivel_massa": 2500, # kg/DM/ha
            "carga_animal": 1.5 # UA/ha
        }
    }

@router.get("/agricola/talhoes")
async def get_agricola_talhoes_report(
    session: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
    _module: None = Depends(require_module("A1_PLANEJAMENTO")),
    _tier: None = Depends(require_tier(PlanTier.PROFISSIONAL)),
):
    """Lista resumida de talhões para seleção no relatório."""
    return [
        {"id": "t1", "nome": "Talhão 01 - Sede", "area": 120, "cultura": "Soja"},
        {"id": "t2", "nome": "Talhão 02 - Represa", "area": 85, "cultura": "Soja"},
        {"id": "t3", "nome": "Talhão 05 - Curva", "area": 210, "cultura": "Milho"},
        {"id": "t4", "nome": "Talhão 08 - Morro", "area": 145, "cultura": "Milho"},
    ]


@router.get("/agricola/profitability")
async def get_agricola_profitability_report(
    session: AsyncSession = Depends(get_session),
    user = Depends(get_current_user),
    _module: None = Depends(require_module("A1_PLANEJAMENTO")),
    _tier: None = Depends(require_tier(PlanTier.PROFISSIONAL)),
):
    """Dados de rentabilidade e ROI por talhão/cultura."""
    return {
        "roi_geral": 1.45, # 145% de retorno
        "margem_media": 32.5, # 32.5% margem líquida
        "receita_total": 12500000.00,
        "lucro_total": 4062500.00,
        "por_talhao": [
            {"id": "t1", "nome": "Talhão 01", "receita": 350000, "custo": 189700, "lucro": 160300, "margem": 45.8},
            {"id": "t2", "nome": "Talhão 02", "receita": 280000, "custo": 145000, "lucro": 135000, "margem": 48.2},
            {"id": "t3", "nome": "Talhão 05", "receita": 890000, "custo": 620000, "lucro": 270000, "margem": 30.3},
            {"id": "t4", "nome": "Talhão 08", "receita": 450000, "custo": 380000, "lucro": 70000, "margem": 15.5}
        ],
        "distribuicao_lucro_cultura": [
            {"name": "Soja", "value": 2850000},
            {"name": "Milho", "value": 1212500}
        ]
    }
