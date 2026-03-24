"""
Routers para mudanças de plano (tenant - usuários finais).

Endpoints para simular, solicitar e gerenciar mudanças de plano.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_maker
from core.dependencies import get_current_user, get_tenant_id, require_tenant_permission
from core.services.mudanca_plano_service import MudancaPlanoService
from core.services.asaas_service import AsaasService
from core.schemas.plan_changes_schemas import (
    SimularMudancaPlanoRequest,
    SimularMudancaPlanoResponse,
    SolicitarMudancaPlanoRequest,
    MudancaPlanoResponse,
    CancelarMudancaPlanoRequest,
    ListarMudancasPlanoResponse
)
from core.exceptions import EntityNotFoundError, BusinessRuleError
from loguru import logger

router = APIRouter(prefix="/billing/mudancas-plano", tags=["Mudanças de Plano"])


@router.post(
    "/simular",
    response_model=SimularMudancaPlanoResponse,
    summary="Simular mudança de plano",
    description="Simula upgrade ou downgrade de plano sem criar solicitação. Retorna valores e condições."
)
async def simular_mudanca_plano(
    request: SimularMudancaPlanoRequest,
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """
    Simula mudança de plano.

    Permite ao usuário visualizar o impacto financeiro antes de confirmar:
    - Valor proporcional a pagar (upgrade)
    - Data de aplicação (downgrade)
    - Diferença de módulos e recursos
    """
    async with async_session_maker() as session:
        service = MudancaPlanoService(session, tenant_id)

        try:
            simulacao = await service.simular_mudanca(
                plano_destino_id=request.plano_destino_id,
                usuarios_destino=request.usuarios_destino,
                assinatura_id=request.assinatura_id,
                usuario_solicitante_id=current_user['user_id']
            )

            return simulacao

        except EntityNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except BusinessRuleError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Erro ao simular mudança de plano: {e}")
            raise HTTPException(status_code=500, detail="Erro interno ao simular mudança")


@router.post(
    "/solicitar",
    response_model=MudancaPlanoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar mudança de plano",
    description="Cria solicitação de mudança. Para upgrade, gera link de pagamento.",
    dependencies=[Depends(require_tenant_permission("tenant:billing:manage"))]
)
async def solicitar_mudanca_plano(
    request: SolicitarMudancaPlanoRequest,
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """
    Solicita mudança de plano.

    **Upgrade:**
    - Calcula valor proporcional
    - Cria cobrança no Asaas
    - Retorna URL de pagamento
    - Upgrade aplicado após confirmação de pagamento

    **Downgrade:**
    - Agenda para próximo ciclo de cobrança
    - Não gera cobrança
    - Acesso ao plano atual mantido até a data agendada
    """
    async with async_session_maker() as session:
        mudanca_service = MudancaPlanoService(session, tenant_id)
        asaas_service = AsaasService(session)

        try:
            # Criar solicitação
            mudanca = await mudanca_service.solicitar_mudanca(
                plano_destino_id=request.plano_destino_id,
                usuarios_destino=request.usuarios_destino,
                usuario_solicitante_id=current_user['user_id'],
                assinatura_id=request.assinatura_id
            )

            # Se for upgrade, criar cobrança no Asaas
            if mudanca.tipo_mudanca.startswith("UPGRADE") and mudanca.valor_proporcional > 0:
                try:
                    cobranca = await asaas_service.criar_cobranca_mudanca_plano(mudanca)
                    logger.info(f"Cobrança Asaas criada: {cobranca.id} - Mudança {mudanca.id}")
                except Exception as e:
                    logger.error(f"Erro ao criar cobrança Asaas: {e}")
                    # Mudança foi criada, mas falhou ao gerar cobrança
                    # Admin pode aprovar manualmente

            return mudanca

        except EntityNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except BusinessRuleError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Erro ao solicitar mudança de plano: {e}")
            raise HTTPException(status_code=500, detail="Erro interno ao solicitar mudança")


@router.get(
    "",
    response_model=ListarMudancasPlanoResponse,
    summary="Listar mudanças de plano",
    description="Lista histórico de mudanças de plano do tenant"
)
async def listar_mudancas_plano(
    pagina: int = 1,
    por_pagina: int = 20,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Lista mudanças de plano do tenant."""
    async with async_session_maker() as session:
        service = MudancaPlanoService(session, tenant_id)

        try:
            # Construir filtros
            filters = {}
            if status:
                filters['status'] = status

            # Buscar mudanças
            mudancas = await service.list_all(
                limit=por_pagina,
                offset=(pagina - 1) * por_pagina,
                **filters
            )

            # Contar total (simplificado, idealmente usar count query)
            total = len(mudancas)

            return {
                "mudancas": mudancas,
                "total": total,
                "pagina": pagina,
                "por_pagina": por_pagina
            }

        except Exception as e:
            logger.error(f"Erro ao listar mudanças: {e}")
            raise HTTPException(status_code=500, detail="Erro ao listar mudanças")


@router.get(
    "/{mudanca_id}",
    response_model=MudancaPlanoResponse,
    summary="Detalhes de mudança de plano"
)
async def obter_mudanca_plano(
    mudanca_id: UUID,
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Obtém detalhes de uma mudança específica."""
    async with async_session_maker() as session:
        service = MudancaPlanoService(session, tenant_id)

        try:
            mudanca = await service.get_or_fail(mudanca_id)
            return mudanca

        except EntityNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Erro ao buscar mudança: {e}")
            raise HTTPException(status_code=500, detail="Erro ao buscar mudança")


@router.delete(
    "/{mudanca_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar mudança de plano",
    description="Cancela mudança pendente ou agendada",
    dependencies=[Depends(require_tenant_permission("tenant:billing:manage"))]
)
async def cancelar_mudanca_plano(
    mudanca_id: UUID,
    request: CancelarMudancaPlanoRequest,
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """
    Cancela mudança de plano pendente.

    Apenas mudanças em status `pendente_pagamento` ou `agendado` podem ser canceladas.
    """
    async with async_session_maker() as session:
        service = MudancaPlanoService(session, tenant_id)

        try:
            await service.cancelar_mudanca(
                mudanca_id=mudanca_id,
                usuario_id=current_user['user_id'],
                motivo=request.motivo
            )

            return None

        except EntityNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except BusinessRuleError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Erro ao cancelar mudança: {e}")
            raise HTTPException(status_code=500, detail="Erro ao cancelar mudança")
