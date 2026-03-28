from fastapi import APIRouter, Depends, BackgroundTasks
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_tenant_id, require_module, get_session_with_tenant
from agricola.dashboard.service import DashboardAgricolaService
from agricola.alertas.service import AlertasAgricolasService

router = APIRouter(prefix="/agricola/dashboard", tags=["Dashboard Agrícola"])


@router.get("/", summary="Dashboard agrícola consolidado")
async def dashboard_agricola(
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    svc = DashboardAgricolaService(session, tenant_id)
    return await svc.resumo()


@router.post(
    "/verificar-alertas",
    summary="Executa verificação de alertas e dispara notificações",
)
async def verificar_alertas(
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(require_module("A1")),
):
    async def _run():
        svc = AlertasAgricolasService(session, tenant_id)
        total = await svc.verificar_todas()
        return total

    background_tasks.add_task(_run)
    return {"message": "Verificação de alertas iniciada em background"}
