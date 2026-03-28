from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from core.config import settings
from core.exceptions import (
    EntityNotFoundError,
    TenantViolationError,
    ModuleNotContractedError,
    BusinessRuleError
)
from core.routers import fazendas
from core.routers import auth
from core.routers import onboarding
from core.routers import backoffice
from core.routers import backoffice_admins
from core.routers import backoffice_tenants
from core.routers import team
from core.routers import grupos_fazendas
from core.routers import billing
from core.routers import plan_changes
from core.routers import backoffice_plan_changes
from core.routers import backoffice_profiles
from core.routers import webhooks_asaas
from core.routers import support
from core.routers import support_ws
from core.routers import knowledge_base
from core.routers import reports
from core.routers import configuration
from core.routers import cupons
from core.routers import backoffice_audit
from core.routers import backoffice_email_templates
from core.routers import backoffice_sessions
from core.routers import backoffice_crm
from core.routers import backoffice_crm_ofertas
from core.routers import backoffice_tabelas
from operacional.routers import frota
from operacional.routers import estoque
from operacional.routers import oficina
from operacional.routers import relatorios as operacional_relatorios
from operacional.routers import compras
from operacional.routers import apontamento as router_apontamento
from operacional.routers import abastecimento as router_abastecimento
from operacional.routers import checklist as router_checklist
from operacional.routers import documento_equipamento as router_doc_equipamento
from core.cadastros.router import router as router_core_cadastros
from core.cadastros.pessoas.router import router as router_pessoas, router_tipos as router_tipos_relacionamento
from core.cadastros.equipamentos.router import router as router_equipamentos
from core.cadastros.propriedades.router import router as router_areas_rurais
from core.cadastros.commodities.router import router as router_commodities
from core.cadastros.produtos.router import router as router_produtos


# -- Configuração Loguru Estruturado p/ Grafana/Loki Compatível
logger.configure(handlers=[{
    "sink": sys.stdout,
    "format": "{time:YYYY-MM-DDThh:mm:ssZ} | {level} | {name}:{function}:{line} | {message}",
    "serialize": False,  # No config final pode ser True para export JSON real
}])

app = FastAPI(
    title="AgroSaaS API",
    description="Motor principal do AgroSaaS - The Modular Monolith",
    version="0.1.0",
)

# IMPORTANTE: CORS deve ser o PRIMEIRO middleware para garantir que headers
# sejam adicionados mesmo em caso de erro de autenticação
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        # Adiciona suporte para redes locais (WSL, Docker, etc)
        "http://192.168.0.2:3000",
        "http://192.168.0.2:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # Cache de preflight por 10 minutos
)

# --- INCLUSÃO DE ROTEADORES ---
app.include_router(auth.router, prefix="/api/v1")
app.include_router(onboarding.router, prefix="/api/v1")
app.include_router(backoffice.router, prefix="/api/v1")
app.include_router(backoffice_admins.router, prefix="/api/v1")
app.include_router(backoffice_tenants.router, prefix="/api/v1")
app.include_router(team.router, prefix="/api/v1")
app.include_router(grupos_fazendas.router, prefix="/api/v1")
app.include_router(cupons.router, prefix="/api/v1")
app.include_router(backoffice_audit.router, prefix="/api/v1")
app.include_router(backoffice_email_templates.router, prefix="/api/v1")
app.include_router(backoffice_sessions.router, prefix="/api/v1")
app.include_router(backoffice_crm.router, prefix="/api/v1")
app.include_router(backoffice_crm_ofertas.router, prefix="/api/v1")
app.include_router(backoffice_tabelas.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(plan_changes.router, prefix="/api/v1")
app.include_router(backoffice_plan_changes.router, prefix="/api/v1")
app.include_router(backoffice_profiles.router, prefix="/api/v1")
app.include_router(webhooks_asaas.router, prefix="/api/v1")
app.include_router(support.router, prefix="/api/v1")
app.include_router(support_ws.router, prefix="/api/v1")
app.include_router(knowledge_base.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(configuration.router, prefix="/api/v1")
app.include_router(frota.router, prefix="/api/v1")
app.include_router(estoque.router, prefix="/api/v1")
app.include_router(oficina.router, prefix="/api/v1")
app.include_router(operacional_relatorios.router, prefix="/api/v1")
app.include_router(compras.router, prefix="/api/v1")
app.include_router(router_apontamento.router, prefix="/api/v1")
app.include_router(router_abastecimento.router, prefix="/api/v1")
app.include_router(router_checklist.router, prefix="/api/v1")
app.include_router(router_doc_equipamento.router, prefix="/api/v1")
app.include_router(router_core_cadastros, prefix="/api/v1")
app.include_router(router_pessoas, prefix="/api/v1")
app.include_router(router_tipos_relacionamento, prefix="/api/v1")
app.include_router(router_equipamentos, prefix="/api/v1")
app.include_router(router_areas_rurais, prefix="/api/v1")
app.include_router(router_commodities, prefix="/api/v1")
app.include_router(router_produtos, prefix="/api/v1")
app.include_router(fazendas.router)
from agricola.safras.router import router as router_safras
from agricola.checklist.router import router as router_checklist_agricola
from agricola.fenologia.router import router as router_fenologia
from agricola.dashboard.router import router as router_dashboard_agricola
from agricola.operacoes.router import router as router_operacoes
from agricola.monitoramento.router import router as router_monitoramentos
from agricola.romaneios.router import router as router_romaneios
from agricola.beneficiamento.router import router as router_beneficiamento
from agricola.previsoes.router import router as router_previsoes
from agricola.ndvi.router import router as router_ndvi
from agricola.climatico.router import router as router_climatico
from agricola.agronomo.router import router as router_agronomo
from agricola.analises_solo.router import router as router_analises_solo
from agricola.custos.router import router as router_custos
from agricola.cadastros.router import router as router_cadastros
from agricola.rastreabilidade.router import router as router_rastreabilidade
from agricola.rastreabilidade.public_router import router as router_rastreabilidade_publica
from agricola.prescricoes.router import router as router_prescricoes
from agricola.a1_planejamento.router import router as router_a1_planejamento

from financeiro.routers import despesas, receitas, planos_conta, relatorios as relatorios_fin, integracao as integracao_fin
from rh.router import router as router_rh
from notificacoes.router import router as router_notificacoes
from pecuaria.routers import lotes
from pecuaria.routers import manejos as pecuaria_manejos
from operacional.routers import frota as frota_router
app.include_router(router_safras, prefix="/api/v1")
app.include_router(router_checklist_agricola, prefix="/api/v1")
app.include_router(router_fenologia, prefix="/api/v1")
app.include_router(router_dashboard_agricola, prefix="/api/v1")
app.include_router(router_operacoes, prefix="/api/v1")
app.include_router(router_monitoramentos, prefix="/api/v1")
app.include_router(router_romaneios, prefix="/api/v1")
app.include_router(router_beneficiamento, prefix="/api/v1")
app.include_router(router_previsoes, prefix="/api/v1")
app.include_router(router_ndvi, prefix="/api/v1")
app.include_router(router_climatico, prefix="/api/v1")
app.include_router(router_agronomo, prefix="/api/v1")
app.include_router(router_analises_solo, prefix="/api/v1")
app.include_router(router_custos, prefix="/api/v1")
app.include_router(router_cadastros, prefix="/api/v1")
app.include_router(router_rastreabilidade, prefix="/api/v1")
app.include_router(router_rastreabilidade_publica, prefix="/api/v1")
app.include_router(router_prescricoes, prefix="/api/v1")
app.include_router(router_a1_planejamento, prefix="/api/v1")
app.include_router(router_rh, prefix="/api/v1")
app.include_router(router_notificacoes, prefix="/api/v1")
app.include_router(despesas.router, prefix="/api/v1/financeiro")
app.include_router(lotes.router, prefix="/api/v1")
app.include_router(pecuaria_manejos.router, prefix="/api/v1")
app.include_router(receitas.router, prefix="/api/v1/financeiro")
app.include_router(planos_conta.router, prefix="/api/v1/financeiro")
app.include_router(relatorios_fin.router, prefix="/api/v1")
app.include_router(integracao_fin.router, prefix="/api/v1/financeiro")
app.include_router(frota_router.router, prefix="/api/v1")

# --- EXCEPTION HANDLERS GLOBAIS ---
@app.exception_handler(EntityNotFoundError)
async def not_found_handler(request: Request, exc: EntityNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(TenantViolationError)
async def tenant_violation_handler(request: Request, exc: TenantViolationError):
    # Log como incidente de segurança sem vazar o erro cru para a Web
    logger.warning(f"SECURITY_INCIDENT - TENANT_VIOLATION: | Attempt Headers: {request.headers} | Msg: {exc}")
    return JSONResponse(status_code=403, content={"detail": "Acesso Negado. Violação de segmentação de dados."})

@app.exception_handler(ModuleNotContractedError)
async def module_not_contracted_handler(request: Request, exc: ModuleNotContractedError):
    return JSONResponse(status_code=402, content={"detail": str(exc), "code": "PAYMENT_REQUIRED"})

@app.exception_handler(BusinessRuleError)
async def business_rule_handler(request: Request, exc: BusinessRuleError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "AgroSaaS is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
