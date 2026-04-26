from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from loguru import logger
import sys

from core.config import settings
from core.exceptions import (
    EntityNotFoundError,
    TenantViolationError,
    ModuleNotContractedError,
    BusinessRuleError
)
from core.routers import unidades_produtivas
from core.routers import auth
from core.routers import onboarding
from core.routers import backoffice
from core.routers import billing
from core.routers import backoffice_admins
from core.routers import backoffice_tenants
from core.routers import backoffice_agro_templates
from core.routers import team
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
from core.routers import tenant_audit
from core.routers import backoffice_email_templates
from core.routers import backoffice_sessions
from core.routers import sessions
from core.routers import backoffice_crm
from core.routers import backoffice_crm_ofertas
from core.routers import backoffice_tabelas
from core.routers import backoffice_uom
from core.routers import stripe_webhooks
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
from core.cadastros.propriedades.propriedade_router import router as router_propriedades_econ
from core.cadastros.pessoas.router import router as router_pessoas, router_tipos as router_tipos_relacionamento
from core.cadastros.equipamentos.router import router as router_equipamentos
from core.cadastros.propriedades.router import router as router_areas_rurais
from core.cadastros.commodities.router import (
    router as router_commodities,
    classif_router as router_commodity_classificacoes,
    cotacao_router as router_commodity_cotacoes,
    conversao_router as router_commodity_conversoes,
)
from core.cadastros.produtos.router import router as router_produtos

# Imóveis Rurais
from imoveis.routers.imovel import router as router_imoveis


# -- Configuração Loguru Estruturado p/ Grafana/Loki Compatível
logger.configure(handlers=[{
    "sink": sys.stdout,
    "format": "{time:YYYY-MM-DDThh:mm:ssZ} | {level} | {name}:{function}:{line} | {message}",
    "serialize": False,  # No config final pode ser True para export JSON real
}])

import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app):
    """Startup/shutdown: inicia job periódico de suspensão de tenants vencidos."""
    async def _job_suspender_vencidos():
        from core.database import async_session_maker
        from core.services.assinatura_service import suspender_vencidos, suspender_trials_expirados
        while True:
            try:
                await asyncio.sleep(3600)  # roda a cada hora
                async with async_session_maker() as session:
                    n1 = await suspender_vencidos(session)
                    n2 = await suspender_trials_expirados(session)
                    if n1 or n2:
                        logger.info(f"[job] suspendidos: {n1} vencidos, {n2} trials")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[job] suspender_vencidos erro: {e}")

    task = asyncio.create_task(_job_suspender_vencidos())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="AgroSaaS API",
    description="Motor principal do AgroSaaS - The Modular Monolith",
    version="0.1.0",
    lifespan=lifespan,
)

# Monta diretório de avatares como static files
AVATAR_DIR = Path("/tmp/agrosaas_avatars")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static/avatars", StaticFiles(directory=str(AVATAR_DIR)), name="avatars")

# Monta diretório de logos de propriedades como static files
LOGOS_DIR = Path("/tmp/agrosaas_logos")
LOGOS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static/logos", StaticFiles(directory=str(LOGOS_DIR)), name="logos")

# Middleware para atualizar o heartbeat da sessão ativa
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timezone, timedelta
import hashlib


class SessionHeartbeatMiddleware(BaseHTTPMiddleware):
    """Atualiza o heartbeat da sessão ativa a cada requisição autenticada."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Ignora rotas de login/register e arquivos estáticos
        path = request.url.path
        if path.startswith(("/api/v1/auth/login", "/api/v1/auth/register", "/docs", "/openapi", "/health")):
            return response

        # Tenta extrair o token do header Authorization
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return response

        # Atualiza o heartbeat de forma assíncrona (fire-and-forget)
        token = auth_header[7:]
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Agenda atualização em background sem bloquear a resposta
        from core.database import async_session_maker
        from sqlalchemy import select, update
        from core.models.sessao import SessaoAtiva

        async def update_heartbeat():
            try:
                async with async_session_maker() as session:
                    agora = datetime.now(timezone.utc)
                    await session.execute(
                        update(SessaoAtiva)
                        .where(SessaoAtiva.token_hash == token_hash, SessaoAtiva.status == "ATIVA")
                        .values(ultimo_heartbeat=agora, expira_em=agora + timedelta(minutes=30))
                    )
                    await session.commit()
            except Exception:
                pass  # Silenciosamente ignora erros de heartbeat

        # Executa em background sem bloquear
        import asyncio
        asyncio.create_task(update_heartbeat())

        return response


class TenantRLSMiddleware(BaseHTTPMiddleware):
    """
    Extrai tenant_id do JWT (sem verificar exp) e grava em request.state.rls_tenant_id.
    get_session() usa esse valor para ativar RLS automaticamente em PostgreSQL,
    garantindo isolamento mesmo em routers que usam get_session em vez de
    get_session_with_tenant.
    """
    _SKIP_PATHS = ("/api/v1/auth/", "/docs", "/openapi", "/health", "/static")

    async def dispatch(self, request, call_next):
        path = request.url.path
        if not any(path.startswith(p) for p in self._SKIP_PATHS):
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                token = auth[7:]
                try:
                    from jose import jwt as _jwt
                    from core.config import settings as _settings
                    payload = _jwt.decode(
                        token,
                        _settings.jwt_secret_key,
                        algorithms=[_settings.jwt_algorithm],
                        options={"verify_exp": False},
                    )
                    tenant_id = payload.get("tenant_id")
                    if tenant_id:
                        request.state.rls_tenant_id = tenant_id
                except Exception:
                    pass
        return await call_next(request)


# Adicionar middlewares na ordem INVERSA (último adicionado = primeiro executado)
# TenantRLSMiddleware PRIMEIRO (define rls_tenant_id antes de tudo)
app.add_middleware(TenantRLSMiddleware)
# SessionHeartbeatMiddleware SEGUNDO
app.add_middleware(SessionHeartbeatMiddleware)

# CORS ÚLTIMO (será executado PRIMEIRO em tempo de execução)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        *settings.allow_origins,
        # Variantes de localhost
        "http://localhost:3000",
        "http://localhost:3001",
        "http://0.0.0.0:3000",
        "http://0.0.0.0:3001",
        "http://localhost.localdomain:3000",
        "http://localhost.localdomain:3001",
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
app.include_router(cupons.router, prefix="/api/v1")
app.include_router(backoffice_audit.router, prefix="/api/v1")
app.include_router(tenant_audit.router, prefix="/api/v1")
app.include_router(backoffice_email_templates.router, prefix="/api/v1")
app.include_router(backoffice_sessions.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(backoffice_crm.router, prefix="/api/v1")
app.include_router(backoffice_crm_ofertas.router, prefix="/api/v1")
app.include_router(backoffice_tabelas.router, prefix="/api/v1")
app.include_router(backoffice_uom.router, prefix="/api/v1")
app.include_router(stripe_webhooks.router, prefix="/api/v1")
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
app.include_router(router_propriedades_econ, prefix="/api/v1")
app.include_router(router_pessoas, prefix="/api/v1")
app.include_router(router_tipos_relacionamento, prefix="/api/v1")
app.include_router(router_equipamentos, prefix="/api/v1")
app.include_router(router_areas_rurais, prefix="/api/v1")
app.include_router(router_commodities, prefix="/api/v1")
app.include_router(router_commodity_classificacoes, prefix="/api/v1")
app.include_router(router_commodity_cotacoes, prefix="/api/v1")
app.include_router(router_commodity_conversoes, prefix="/api/v1")
app.include_router(router_produtos, prefix="/api/v1")
app.include_router(router_imoveis, prefix="/api/v1")
app.include_router(unidades_produtivas.router, prefix="/api/v1")
from agricola.safras.router import router as router_safras
from agricola.cultivos.router import router as router_cultivos
from agricola.talhoes.router import router as router_agricola_talhoes
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
from agricola.cenarios.router import router as router_cenarios
from agricola.cadastros.router import router as router_cadastros
from agricola.rastreabilidade.router import router as router_rastreabilidade
from agricola.rastreabilidade.public_router import router as router_rastreabilidade_publica
from agricola.prescricoes.router import router as router_prescricoes
from agricola.a1_planejamento.router import router as router_a1_planejamento
from agricola.tarefas.router import router as router_tarefas
from agricola.caderno.router import router as router_caderno
from agricola.colheita.router import router as router_produtos_colhidos
from agricola.templates.router import router as router_templates_agricola
# Amostragem de Solo
from agricola.amostragem_solo.routers.amostras import router as amostras_solo_router
from agricola.amostragem_solo.routers.mapas_fertilidade import router as mapas_fertilidade_router
from agricola.amostragem_solo.routers.prescricoes_vra import router as prescricoes_vra_router

# NDVI e Irrigação
from agricola.ndvi_avancado.routers.ndvi import router as ndvi_router
from agricola.ndvi_avancado.routers.irrigacao import router as irrigacao_router
from agricola.ndvi_avancado.routers.meteorologia import router as meteorologia_router

# IA Diagnóstico
from ia_diagnostico.routers.pragas_doencas import router as ia_pragas_doencas_router
from ia_diagnostico.routers.tratamentos import router as ia_tratamentos_router
from ia_diagnostico.routers.diagnosticos import router as ia_diagnosticos_router

# IoT Integração
from iot_integracao.routers.john_deere import router as john_deere_router
from iot_integracao.routers.case_ih import router as case_ih_router
from iot_integracao.routers.whatsapp import router as whatsapp_router
from iot_integracao.routers.comparador_precos import router as comparador_precos_router
from iot_integracao.new_holland.routers import router as sprint26_router

# API Pública
from core.api_publica.routers.keys import router as api_keys_router
from core.api_publica.routers.logs import router as api_logs_router
from core.api_publica.routers.versions import router as api_versions_router

# Enterprise (COMENTADO - Usa Session síncrono, requer migração para AsyncSession)
# from enterprise.routers.sap import router as sap_router
# from enterprise.routers.powerbi import router as powerbi_router
# from enterprise.routers.benchmarks import router as benchmarks_router
# from enterprise.routers.preditivo import router as preditivo_router
from enterprise.routers.sprints_27_33_router import router as sprints_27_33_router
from integracoes.sankhya.routers import router as sankhya_router
from integracoes.regulatorias.router import router as regulatorias_router

# Contabilidade (COMENTADO - Usa Session síncrono, requer migração para AsyncSession)
# from contabilidade.routers.integracoes import router as contabilidade_integracoes_router
# from contabilidade.routers.exportacoes import router as contabilidade_exportacoes_router
# from contabilidade.routers.lancamentos import router as contabilidade_lancamentos_router

from financeiro.routers import despesas, receitas, planos_conta, relatorios as relatorios_fin, integracao as integracao_fin, conciliacao, notas_fiscais as notas_fiscais_router
from financeiro.comercializacao.router import router as router_comercializacoes
from ambiental.router import router as router_ambiental
from rh.router import router as router_rh
from notificacoes.router import router as router_notificacoes
from pecuaria.routers import lotes
from pecuaria.routers import manejos as pecuaria_manejos
from operacional.routers import frota as frota_router
app.include_router(router_safras, prefix="/api/v1")
app.include_router(router_cultivos, prefix="/api/v1")
app.include_router(router_agricola_talhoes, prefix="/api/v1")
app.include_router(router_checklist_agricola, prefix="/api/v1")
app.include_router(router_fenologia, prefix="/api/v1")
app.include_router(router_dashboard_agricola, prefix="/api/v1")
app.include_router(router_operacoes, prefix="/api/v1")
app.include_router(router_monitoramentos, prefix="/api/v1")
app.include_router(router_romaneios, prefix="/api/v1")
app.include_router(router_produtos_colhidos, prefix="/api/v1")
app.include_router(router_beneficiamento, prefix="/api/v1")
app.include_router(router_previsoes, prefix="/api/v1")
app.include_router(router_ndvi, prefix="/api/v1")
app.include_router(router_climatico, prefix="/api/v1")
app.include_router(router_agronomo, prefix="/api/v1")
app.include_router(router_analises_solo, prefix="/api/v1")
app.include_router(router_custos, prefix="/api/v1")
app.include_router(router_cenarios, prefix="/api/v1")
app.include_router(router_cadastros, prefix="/api/v1")
app.include_router(router_rastreabilidade, prefix="/api/v1")
app.include_router(router_rastreabilidade_publica, prefix="/api/v1")
app.include_router(router_prescricoes, prefix="/api/v1")
app.include_router(router_caderno, prefix="/api/v1")
app.include_router(router_a1_planejamento, prefix="/api/v1")
app.include_router(router_tarefas, prefix="/api/v1")
app.include_router(router_templates_agricola, prefix="/api/v1")
app.include_router(backoffice_agro_templates.router, prefix="/api/v1")

# Amostragem de Solo
app.include_router(amostras_solo_router, prefix="/api/v1/amostragem-solo")
app.include_router(mapas_fertilidade_router, prefix="/api/v1/amostragem-solo")
app.include_router(prescricoes_vra_router, prefix="/api/v1/amostragem-solo")

# NDVI e Irrigação
app.include_router(ndvi_router, prefix="/api/v1/agricultura-precisao")
app.include_router(irrigacao_router, prefix="/api/v1/agricultura-precisao")
app.include_router(meteorologia_router, prefix="/api/v1/agricultura-precisao")

# IA Diagnóstico
app.include_router(ia_pragas_doencas_router, prefix="/api/v1/ia-diagnostico")
app.include_router(ia_tratamentos_router, prefix="/api/v1/ia-diagnostico")
app.include_router(ia_diagnosticos_router, prefix="/api/v1/ia-diagnostico")

# IoT Integração
app.include_router(john_deere_router, prefix="/api/v1/iot")
app.include_router(case_ih_router, prefix="/api/v1/iot")
app.include_router(whatsapp_router, prefix="/api/v1/iot")
app.include_router(comparador_precos_router, prefix="/api/v1/iot")
app.include_router(sprint26_router, prefix="/api/v1")

# API Pública
app.include_router(api_keys_router, prefix="/api/v1/api-publica")
app.include_router(api_logs_router, prefix="/api/v1/api-publica")
app.include_router(api_versions_router, prefix="/api/v1/api-publica")

# Enterprise
# Enterprise (COMENTADO)
# app.include_router(sap_router, prefix="/api/v1/enterprise")
# app.include_router(powerbi_router, prefix="/api/v1/enterprise")
# app.include_router(benchmarks_router, prefix="/api/v1/enterprise")
# app.include_router(preditivo_router, prefix="/api/v1/enterprise")
app.include_router(sprints_27_33_router, prefix="/api/v1/enterprise")
app.include_router(sankhya_router, prefix="/api/v1/integracoes")
app.include_router(regulatorias_router, prefix="/api/v1/integracoes/regulatorias")

# Contabilidade (COMENTADO)
# app.include_router(contabilidade_integracoes_router, prefix="/api/v1/contabilidade")
# app.include_router(contabilidade_exportacoes_router, prefix="/api/v1/contabilidade")
# app.include_router(contabilidade_lancamentos_router, prefix="/api/v1/contabilidade")
app.include_router(router_rh, prefix="/api/v1")
app.include_router(router_notificacoes, prefix="/api/v1")
app.include_router(despesas.router, prefix="/api/v1/financeiro")
app.include_router(lotes.router, prefix="/api/v1")
app.include_router(pecuaria_manejos.router, prefix="/api/v1")
app.include_router(receitas.router, prefix="/api/v1/financeiro")
app.include_router(planos_conta.router, prefix="/api/v1/financeiro")
app.include_router(relatorios_fin.router, prefix="/api/v1")
app.include_router(integracao_fin.router, prefix="/api/v1/financeiro")
app.include_router(conciliacao.router, prefix="/api/v1/financeiro")
app.include_router(notas_fiscais_router.router, prefix="/api/v1/financeiro")
app.include_router(router_comercializacoes, prefix="/api/v1/financeiro")
app.include_router(router_ambiental, prefix="/api/v1")
app.include_router(frota_router.router, prefix="/api/v1")

# --- EXCEPTION HANDLERS GLOBAIS ---
@app.exception_handler(EntityNotFoundError)
async def not_found_handler(request: Request, exc: EntityNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(TenantViolationError)
async def tenant_violation_handler(request: Request, exc: TenantViolationError):
    logger.critical(
        "SECURITY_INCIDENT - TENANT_VIOLATION",
        tenant_id=str(exc.tenant_id) if exc.tenant_id else None,
        user_id=str(exc.user_id) if exc.user_id else None,
        resource=exc.resource,
        path=str(request.url.path),
        method=request.method,
        ip=request.client.host if request.client else None,
    )
    # Persiste no banco de forma assíncrona e independente
    try:
        from core.database import async_session_maker
        from core.services.audit_service import write_audit_log
        if exc.tenant_id:
            async with async_session_maker() as _session:
                await write_audit_log(
                    _session,
                    tenant_id=exc.tenant_id,
                    user_id=exc.user_id,
                    action="SECURITY_INCIDENT",
                    resource=exc.resource or "unknown",
                    resource_id=None,
                    payload_before=None,
                    payload_after={"path": request.url.path, "method": request.method},
                    ip_address=request.client.host if request.client else None,
                )
                await _session.commit()
    except Exception as persist_err:
        logger.error(f"Falha ao persistir incidente de segurança: {persist_err}")
    return JSONResponse(status_code=403, content={"detail": "Acesso Negado. Violação de segmentação de dados."})

@app.exception_handler(ModuleNotContractedError)
async def module_not_contracted_handler(request: Request, exc: ModuleNotContractedError):
    return JSONResponse(status_code=402, content={"detail": str(exc), "code": "PAYMENT_REQUIRED"})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_msg = f"Unhandled Exception: {type(exc).__name__}: {str(exc)}\n{traceback.format_exc()}"
    logger.error(error_msg)
    # Log to a temporary file in the workspace
    with open("error_debug.log", "a") as f:
        f.write(f"\n--- {datetime.now()} ---\n{error_msg}\n")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)},
        headers={"Access-Control-Allow-Origin": "*"} # Force CORS for error
    )

@app.exception_handler(BusinessRuleError)
async def business_rule_handler(request: Request, exc: BusinessRuleError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "AgroSaaS is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
