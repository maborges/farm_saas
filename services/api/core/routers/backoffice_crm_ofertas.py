"""
Rotas do CRM para gerenciar ofertas comerciais flexíveis.

Endpoints para:
- Gerenciar produtos/módulos
- Criar/editar planos
- Gerar ofertas personalizadas para leads
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from core.dependencies import get_session, get_current_admin, require_permission
from core.models.crm_ofertas import (
    ModuloOferta, PrecificacaoModulo, PlanoComercial, OfertaPersonalizada
)
from core.models.crm import LeadCRM
from pydantic import BaseModel


router = APIRouter(
    prefix="/backoffice/crm/ofertas",
    tags=["Backoffice - CRM - Ofertas"],
    dependencies=[Depends(require_permission("backoffice:crm:view"))],
)


# ==================== SCHEMAS ====================

class ProdutoCreate(BaseModel):
    nome: str
    slug: str
    descricao: str | None = None
    categoria: str = "core"
    icone: str | None = None
    features: list[str] | None = None


class ProdutoResponse(BaseModel):
    id: UUID
    nome: str
    slug: str
    descricao: str | None
    categoria: str
    ativo: bool
    posicao: int

    class Config:
        from_attributes = True


class PrecificacaoModuloCreate(BaseModel):
    modulo_oferta_id: UUID
    preco_mensal: float
    preco_anual: float
    vigencia_inicio: datetime
    vigencia_fim: datetime | None = None
    condicoes: dict | None = None


class PlanoComercialCreate(BaseModel):
    nome: str
    slug: str
    descricao: str | None = None
    tipo_oferta: str = "bundle"  # bundle | modular | misto
    modulos_inclusos: List[UUID]
    preco_mensal_padrao: float | None = None
    preco_anual_padrao: float | None = None
    publico_alvo: str | None = None
    tier: int = 1


class PlanoComercialResponse(BaseModel):
    id: UUID
    nome: str
    slug: str
    tipo_oferta: str
    modulos_inclusos: list[str]
    preco_mensal_padrao: float | None
    preco_anual_padrao: float | None
    ativo: bool

    class Config:
        from_attributes = True


class OfertaPersonalizadaCreate(BaseModel):
    lead_id: UUID
    tipo_oferta: str  # plano_padrao | custom_modular | enterprise
    plano_base_id: UUID | None = None
    modulos_selecionados: List[UUID] | None = None
    preco_total_mensal: float
    preco_total_anual: float
    desconto_percentual: float = 0
    justificativa: str | None = None
    vigencia_dias: int = 30


class OfertaPersonalizadaResponse(BaseModel):
    id: UUID
    lead_id: UUID
    tipo_oferta: str
    preco_total_mensal: float
    preco_total_anual: float
    desconto_percentual: float
    status: str
    vigencia_inicio: datetime
    vigencia_fim: datetime

    class Config:
        from_attributes = True


# ==================== ENDPOINTS - PRODUTOS ====================

@router.get("/produtos", response_model=List[ProdutoResponse])
async def listar_produtos(
    categoria: str | None = None,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Lista todos os módulos/produtos disponíveis."""
    stmt = select(ModuloOferta).order_by(ModuloOferta.posicao, ModuloOferta.nome)
    if categoria:
        stmt = stmt.where(ModuloOferta.categoria == categoria)

    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("/produtos", response_model=ProdutoResponse, dependencies=[Depends(require_permission("backoffice:crm:edit"))])
async def criar_produto(
    data: ProdutoCreate,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Criar novo módulo/produto."""
    modulo = ModuloOferta(
        nome=data.nome,
        slug=data.slug,
        descricao=data.descricao,
        categoria=data.categoria,
        icone=data.icone,
        features=data.features,
    )
    session.add(modulo)
    await session.commit()
    await session.refresh(modulo)
    return modulo


# ==================== ENDPOINTS - PLANOS ====================

@router.get("/planos", response_model=List[PlanoComercialResponse])
async def listar_planos(
    ativo_apenas: bool = True,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Lista planos comerciais disponíveis."""
    stmt = select(PlanoComercial).order_by(PlanoComercial.tier, PlanoComercial.posicao)
    if ativo_apenas:
        stmt = stmt.where(PlanoComercial.ativo == True)

    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("/planos", response_model=PlanoComercialResponse, dependencies=[Depends(require_permission("backoffice:crm:edit"))])
async def criar_plano(
    data: PlanoComercialCreate,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Criar novo plano comercial."""
    plano = PlanoComercial(
        nome=data.nome,
        slug=data.slug,
        descricao=data.descricao,
        tipo_oferta=data.tipo_oferta,
        modulos_inclusos=[str(m) for m in data.modulos_inclusos],
        preco_mensal_padrao=data.preco_mensal_padrao,
        preco_anual_padrao=data.preco_anual_padrao,
        público_alvo=data.publico_alvo,
        tier=data.tier,
    )
    session.add(plano)
    await session.commit()
    await session.refresh(plano)
    return plano


# ==================== ENDPOINTS - OFERTAS PERSONALIZADAS ====================

@router.post("/leads/{lead_id}/oferta", response_model=OfertaPersonalizadaResponse, dependencies=[Depends(require_permission("backoffice:crm:edit"))])
async def criar_oferta_personalizada(
    lead_id: UUID,
    data: OfertaPersonalizadaCreate,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Criar oferta comercial personalizada para um lead."""
    # Verificar se lead existe
    lead_result = await session.execute(select(LeadCRM).where(LeadCRM.id == lead_id))
    lead = lead_result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    vigencia_fim = datetime.now(timezone.utc) + timedelta(days=data.vigencia_dias)

    oferta = OfertaPersonalizada(
        lead_id=lead_id,
        tipo_oferta=data.tipo_oferta,
        plano_base_id=data.plano_base_id,
        modulos_selecionados=[str(m) for m in (data.modulos_selecionados or [])],
        preco_total_mensal=data.preco_total_mensal,
        preco_total_anual=data.preco_total_anual,
        desconto_percentual=data.desconto_percentual,
        justificativa=data.justificativa,
        vigencia_inicio=datetime.now(timezone.utc),
        vigencia_fim=vigencia_fim,
        status="proposta",
    )
    session.add(oferta)
    await session.commit()
    await session.refresh(oferta)
    return oferta


@router.get("/leads/{lead_id}/ofertas", response_model=List[OfertaPersonalizadaResponse])
async def listar_ofertas_lead(
    lead_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Listar todas as ofertas de um lead."""
    stmt = (
        select(OfertaPersonalizada)
        .where(OfertaPersonalizada.lead_id == lead_id)
        .order_by(OfertaPersonalizada.created_at.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


@router.patch("/ofertas/{oferta_id}/status", dependencies=[Depends(require_permission("backoffice:crm:edit"))])
async def atualizar_status_oferta(
    oferta_id: UUID,
    novo_status: str,  # aceita | rejeitada | expirada
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Atualizar status de uma oferta (aceita/rejeitada)."""
    result = await session.execute(select(OfertaPersonalizada).where(OfertaPersonalizada.id == oferta_id))
    oferta = result.scalar_one_or_none()
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta não encontrada")

    oferta.status = novo_status
    await session.commit()
    return {"message": f"Oferta atualizada para {novo_status}"}


# ==================== HELPERS - CALCULAR PREÇO DINÂMICO ====================

@router.post("/calcular-preco")
async def calcular_preco_oferta(
    modulos: List[UUID],
    desconto_percentual: float = 0,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin),
):
    """Calcular preço total baseado nos módulos selecionados."""
    total_mensal = 0
    total_anual = 0

    # Buscar preços atuais de cada módulo
    for modulo_id in modulos:
        stmt = (
            select(PrecificacaoModulo)
            .where(PrecificacaoModulo.modulo_oferta_id == modulo_id)
            .where(PrecificacaoModulo.vigencia_inicio <= datetime.now(timezone.utc))
            .where((PrecificacaoModulo.vigencia_fim.is_(None)) | (PrecificacaoModulo.vigencia_fim >= datetime.now(timezone.utc)))
            .order_by(PrecificacaoModulo.vigencia_inicio.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        preco = result.scalar_one_or_none()

        if preco:
            total_mensal += float(preco.preco_mensal)
            total_anual += float(preco.preco_anual)

    # Aplicar desconto
    desconto_valor = (total_mensal + total_anual) * (desconto_percentual / 100)
    total_mensal -= (total_mensal * desconto_percentual / 100)
    total_anual -= (total_anual * desconto_percentual / 100)

    return {
        "preco_mensal": round(total_mensal, 2),
        "preco_anual": round(total_anual, 2),
        "desconto_aplicado": round(desconto_valor, 2),
    }
