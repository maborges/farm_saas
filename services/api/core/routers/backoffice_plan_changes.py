"""
Routers para gestão de mudanças de plano (backoffice - admins SaaS).

Endpoints para aprovar mudanças manualmente, gerenciar pricing e monitorar sistema.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from decimal import Decimal

from core.database import async_session_maker
from core.dependencies import get_current_admin, require_permission
from core.services.mudanca_plano_service import MudancaPlanoService
from core.services.plan_pricing_service import PlanoPricingService
from core.models.plan_changes import MudancaPlano, PlanoPricing
from core.schemas.plan_changes_schemas import (
    AprovarMudancaManualmenteRequest,
    AprovarMudancaManualmenteResponse,
    MudancaPlanoResponse,
    PlanoPricingCreate,
    PlanoPricingResponse,
    PlanoPricingUpdate,
    PlanoComPricingResponse,
    ResumoMudancasPlanoResponse
)
from core.exceptions import EntityNotFoundError, BusinessRuleError
from loguru import logger

router = APIRouter(prefix="/backoffice/plan-changes", tags=["Backoffice - Mudanças de Plano"])


# ============================================================================
# GESTÃO DE MUDANÇAS
# ============================================================================

@router.get(
    "/mudancas",
    response_model=list[MudancaPlanoResponse],
    summary="Listar todas as mudanças de plano",
    dependencies=[Depends(require_permission("backoffice:billing:view"))]
)
async def listar_todas_mudancas(
    status: Optional[str] = Query(None, description="Filtrar por status"),
    tenant_id: Optional[UUID] = Query(None, description="Filtrar por tenant"),
    limit: int = Query(50, le=100),
    offset: int = 0,
    current_admin: dict = Depends(get_current_admin)
):
    """Lista todas as mudanças de plano do sistema."""
    async with async_session_maker() as session:
        stmt = select(MudancaPlano)

        if status:
            stmt = stmt.where(MudancaPlano.status == status)
        if tenant_id:
            stmt = stmt.where(MudancaPlano.tenant_id == tenant_id)

        stmt = stmt.order_by(MudancaPlano.created_at.desc()).limit(limit).offset(offset)

        result = await session.execute(stmt)
        mudancas = result.scalars().all()

        return mudancas


@router.post(
    "/mudancas/{mudanca_id}/aprovar-manualmente",
    response_model=AprovarMudancaManualmenteResponse,
    summary="Aprovar mudança manualmente",
    description="Libera upgrade sem pagamento, com prazo para regularização",
    dependencies=[Depends(require_permission("backoffice:billing:approve"))]
)
async def aprovar_mudanca_manualmente(
    mudanca_id: UUID,
    request: AprovarMudancaManualmenteRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Aprova mudança de plano manualmente (sem pagamento).

    **Uso recomendado:**
    - Cliente confiável com histórico de pagamento
    - Negociação comercial especial
    - Problemas técnicos com gateway de pagamento

    **Atenção:**
    - Sistema bloqueará tenant automaticamente se não pagar no prazo
    - Ação fica registrada em auditoria
    """
    async with async_session_maker() as session:
        service = MudancaPlanoService(session, tenant_id=None)

        try:
            mudanca = await service.aprovar_manualmente(
                mudanca_id=mudanca_id,
                admin_id=current_admin['admin_id'],
                motivo=request.motivo_liberacao,
                dias_tolerancia=request.dias_tolerancia_pagamento
            )

            return {
                "mudanca_id": mudanca.id,
                "status": mudanca.status,
                "data_limite_pagamento": mudanca.data_limite_pagamento,
                "mensagem": f"Mudança aprovada manualmente. Tenant tem até {mudanca.data_limite_pagamento.strftime('%d/%m/%Y')} para regularizar pagamento."
            }

        except EntityNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except BusinessRuleError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Erro ao aprovar mudança manualmente: {e}")
            raise HTTPException(status_code=500, detail="Erro ao aprovar mudança")


@router.get(
    "/mudancas/resumo",
    response_model=ResumoMudancasPlanoResponse,
    summary="Resumo de mudanças para dashboard",
    dependencies=[Depends(require_permission("backoffice:billing:view"))]
)
async def resumo_mudancas_plano(
    current_admin: dict = Depends(get_current_admin)
):
    """Retorna métricas agregadas de mudanças de plano."""
    async with async_session_maker() as session:
        # Contar mudanças do mês atual
        from datetime import datetime, timezone
        inicio_mes = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0)

        # Upgrades do mês
        stmt_upgrades = select(func.count(MudancaPlano.id), func.sum(MudancaPlano.valor_proporcional)).where(
            MudancaPlano.created_at >= inicio_mes,
            MudancaPlano.tipo_mudanca.like("UPGRADE%")
        )
        result = await session.execute(stmt_upgrades)
        upgrades_count, upgrades_valor = result.one()

        # Downgrades do mês
        stmt_downgrades = select(func.count(MudancaPlano.id)).where(
            MudancaPlano.created_at >= inicio_mes,
            MudancaPlano.tipo_mudanca.like("DOWNGRADE%")
        )
        result = await session.execute(stmt_downgrades)
        downgrades_count = result.scalar()

        # Pendentes
        stmt_pendentes = select(func.count(MudancaPlano.id)).where(
            MudancaPlano.status.in_(["pendente_pagamento", "liberado_manualmente"])
        )
        result = await session.execute(stmt_pendentes)
        pendentes_count = result.scalar()

        # Bloqueados
        stmt_bloqueados = select(func.count(MudancaPlano.id)).where(
            MudancaPlano.status == "bloqueado"
        )
        result = await session.execute(stmt_bloqueados)
        bloqueados_count = result.scalar()

        return {
            "total_upgrades_mes": upgrades_count or 0,
            "total_downgrades_mes": downgrades_count or 0,
            "total_pendentes": pendentes_count or 0,
            "total_bloqueados": bloqueados_count or 0,
            "receita_upgrades_mes": Decimal(str(upgrades_valor or 0)),
            "taxa_conversao_upgrades": 0.0  # TODO: calcular baseado em simulações vs solicitações
        }


# ============================================================================
# GESTÃO DE PRICING
# ============================================================================

@router.post(
    "/pricing",
    response_model=PlanoPricingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar faixa de pricing",
    dependencies=[Depends(require_permission("backoffice:plans:manage"))]
)
async def criar_pricing(
    request: PlanoPricingCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Cria nova faixa de pricing para um plano."""
    async with async_session_maker() as session:
        service = PlanoPricingService(session)

        try:
            faixa = await service.criar_faixa_pricing(
                plano_id=request.plano_id,
                faixa_inicio=request.faixa_inicio,
                faixa_fim=request.faixa_fim,
                preco_mensal=request.preco_por_usuario_mensal,
                preco_anual=request.preco_por_usuario_anual
            )

            return faixa

        except EntityNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except BusinessRuleError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Erro ao criar pricing: {e}")
            raise HTTPException(status_code=500, detail="Erro ao criar pricing")


@router.get(
    "/pricing/{plano_id}",
    response_model=list[PlanoPricingResponse],
    summary="Listar pricing de um plano",
    dependencies=[Depends(require_permission("backoffice:plans:view"))]
)
async def listar_pricing_plano(
    plano_id: UUID,
    current_admin: dict = Depends(get_current_admin)
):
    """Lista todas as faixas de pricing de um plano."""
    async with async_session_maker() as session:
        service = PlanoPricingService(session)

        try:
            faixas = await service.obter_faixas_plano(plano_id)
            return faixas

        except Exception as e:
            logger.error(f"Erro ao listar pricing: {e}")
            raise HTTPException(status_code=500, detail="Erro ao listar pricing")


@router.put(
    "/pricing/{pricing_id}",
    response_model=PlanoPricingResponse,
    summary="Atualizar faixa de pricing",
    dependencies=[Depends(require_permission("backoffice:plans:manage"))]
)
async def atualizar_pricing(
    pricing_id: UUID,
    request: PlanoPricingUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    """Atualiza faixa de pricing existente."""
    async with async_session_maker() as session:
        service = PlanoPricingService(session)

        try:
            # Buscar faixa
            faixa = await service.get_or_fail(pricing_id)

            # Atualizar campos
            if request.faixa_inicio is not None:
                faixa.faixa_inicio = request.faixa_inicio
            if request.faixa_fim is not None:
                faixa.faixa_fim = request.faixa_fim
            if request.preco_por_usuario_mensal is not None:
                faixa.preco_por_usuario_mensal = request.preco_por_usuario_mensal
            if request.preco_por_usuario_anual is not None:
                faixa.preco_por_usuario_anual = request.preco_por_usuario_anual
            if request.ativo is not None:
                faixa.ativo = request.ativo

            await session.commit()
            await session.refresh(faixa)

            return faixa

        except EntityNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Erro ao atualizar pricing: {e}")
            raise HTTPException(status_code=500, detail="Erro ao atualizar pricing")


@router.delete(
    "/pricing/{pricing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desativar faixa de pricing",
    dependencies=[Depends(require_permission("backoffice:plans:manage"))]
)
async def desativar_pricing(
    pricing_id: UUID,
    current_admin: dict = Depends(get_current_admin)
):
    """Desativa (soft delete) faixa de pricing."""
    async with async_session_maker() as session:
        service = PlanoPricingService(session)

        try:
            faixa = await service.get_or_fail(pricing_id)
            faixa.ativo = False

            await session.commit()

            logger.info(f"Pricing {pricing_id} desativado por admin {current_admin['admin_id']}")

            return None

        except EntityNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Erro ao desativar pricing: {e}")
            raise HTTPException(status_code=500, detail="Erro ao desativar pricing")
