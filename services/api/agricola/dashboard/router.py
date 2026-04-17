from fastapi import APIRouter, Depends, BackgroundTasks
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, get_session_with_tenant, require_tenant_permission
from agricola.dashboard.service import DashboardAgricolaService
from agricola.dashboard.schemas import SafraResumoFinanceiro, SafraMargemCompleta
from agricola.alertas.service import AlertasAgricolasService

router = APIRouter(prefix="/agricola/dashboard", tags=["Dashboard Agrícola"])


@router.get("/", summary="Dashboard agrícola consolidado")
async def dashboard_agricola(
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    svc = DashboardAgricolaService(session, tenant_id)
    return await svc.resumo()


@router.get(
    "/safras/{safra_id}/resumo-financeiro",
    response_model=SafraResumoFinanceiro,
    summary="Resumo financeiro completo de uma safra"
)
async def resumo_financeiro_safra(
    safra_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_tenant_permission("agricola:safras:view")),
):
    """
    Retorna resumo financeiro completo de uma safra:

    - **Operações:** Total de operações e custo acumulado
    - **Despesas:** Total de despesas vinculadas (origem_id)
    - **Romaneios:** Total de sacas e produtividade
    - **Receitas:** Total de receitas vinculadas (origem_id)
    - **Agregações:** Lucro bruto e ROI (receita - despesa)

    Agrupa dados de múltiplas tabelas (operacoes, romaneios, fin_despesas, fin_receitas)
    para visão financeira integrada da safra.
    """
    svc = DashboardAgricolaService(session, tenant_id)
    return await svc.resumo_financeiro_safra(safra_id)


@router.get(
    "/safras/{safra_id}/margem",
    response_model=SafraMargemCompleta,
    summary="Dashboard de margem por safra com breakdown por talhão"
)
async def margem_safra(
    safra_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_tenant_permission("agricola:safras:view")),
):
    """
    Dashboard completo de margem de lucro por safra.

    Retorna:
    - **Custo total** por tipo de operação (com breakdown)
    - **Receita total** de romaneios + comercializações
    - **Margem bruta**, margem por hectare, margem %
    - **ROI** da safra
    - **Breakdown por talhão**: custo, receita, margem, produtividade
    - **Breakdown por operação**: custo por tipo de operação com % do total
    """
    svc = DashboardAgricolaService(session, tenant_id)
    return await svc.margem_safra_completa(safra_id)


@router.post(
    "/verificar-alertas",
    summary="Executa verificação de alertas e dispara notificações",
)
async def verificar_alertas(
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1_PLANEJAMENTO")),
):
    async def _run():
        svc = AlertasAgricolasService(session, tenant_id)
        total = await svc.verificar_todas()
        return total

    background_tasks.add_task(_run)
    return {"message": "Verificação de alertas iniciada em background"}
