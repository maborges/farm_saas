from fastapi import APIRouter, Depends, HTTPException, Request, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import uuid

from core.dependencies import get_session, get_current_user, get_current_tenant, get_current_user_claims
from core.models.tenant import Tenant
from core.models.billing import AssinaturaTenant, PlanoAssinatura, Fatura
from core.models.fazenda import Fazenda
from core.models.auth import TenantUsuario
from core.schemas.billing_schemas import FaturaResponse, PlanoAssinaturaResponse

router = APIRouter(prefix="/billing", tags=["Billing / Conta"])

@router.get("/my-account")
async def get_my_account(tenant: Tenant = Depends(get_current_tenant), session: AsyncSession = Depends(get_session)):
    """Retorna detalhes da conta/tenant logado."""
    # Buscar assinatura e plano
    stmt = (
        select(AssinaturaTenant, PlanoAssinatura)
        .join(PlanoAssinatura, AssinaturaTenant.plano_id == PlanoAssinatura.id)
        .where(AssinaturaTenant.tenant_id == tenant.id)
    )
    result = await session.execute(stmt)
    row = result.first()
    
    assinatura_data = None
    if row:
        assinatura, plano = row
        assinatura_data = {
            "plano": plano.nome,
            "valor": float(plano.preco_mensal),
            "status": assinatura.status,
            "data_inicio": assinatura.data_inicio,
            "proximo_vencimento": assinatura.data_proxima_fatura
        }

    return {
        "tenant": {
            "id": tenant.id,
            "nome": tenant.nome,
            "documento": tenant.documento,
            "ativo": tenant.ativo,
            "modulos_ativos": tenant.modulos_ativos,
            "max_usuarios": tenant.max_usuarios_simultaneos,
            "created_at": tenant.created_at
        },
        "assinatura": assinatura_data
    }

@router.get("/invoices", response_model=List[FaturaResponse])
async def list_my_invoices(tenant: Tenant = Depends(get_current_tenant), session: AsyncSession = Depends(get_session)):
    """Lista o histórico de faturas do cliente logado."""
    stmt = (
        select(Fatura, PlanoAssinatura.nome.label("plano_nome"))
        .join(AssinaturaTenant, Fatura.assinatura_id == AssinaturaTenant.id)
        .join(PlanoAssinatura, AssinaturaTenant.plano_id == PlanoAssinatura.id)
        .where(Fatura.tenant_id == tenant.id)
        .order_by(Fatura.created_at.desc())
    )
    result = await session.execute(stmt)
    
    invoices = []
    for row in result:
        f = row[0]
        invoices.append({
            "id": f.id,
            "tenant_id": f.tenant_id,
            "tenant_nome": tenant.nome, # Já sabemos quem é
            "plano_nome": row.plano_nome,
            "valor": float(f.valor),
            "data_vencimento": f.data_vencimento,
            "status": f.status,
            "url_comprovante": f.url_comprovante,
            "data_envio_comprovante": f.data_envio_comprovante,
            "justificativa_rejeicao": f.justificativa_rejeicao,
            "created_at": f.created_at
        })
    return invoices

@router.post("/invoices/{invoice_id}/pay")
async def register_payment_proof(
    invoice_id: uuid.UUID,
    url_comprovante: str,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Envia o comprovante de pagamento (mockando upload por enquanto)."""
    fatura = await session.get(Fatura, invoice_id)
    if not fatura or fatura.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    
    if fatura.status == "PAGA":
        raise HTTPException(status_code=400, detail="Esta fatura já está paga.")

    from datetime import datetime, timezone
    
    fatura.url_comprovante = url_comprovante
    fatura.data_envio_comprovante = datetime.now(timezone.utc)
    fatura.status = "EM_ANALISE"
    
    await session.commit()
    return {"message": "Comprovante enviado para análise!"}

@router.get("/plans", response_model=List[PlanoAssinaturaResponse])
async def list_available_plans(session: AsyncSession = Depends(get_session)):
    """Lista todos os pacotes de assinatura ativos."""
    stmt = select(PlanoAssinatura).where(PlanoAssinatura.ativo == True).order_by(PlanoAssinatura.preco_mensal.asc())
    result = await session.execute(stmt)
    return result.scalars().all()

@router.post("/upgrade")
async def request_upgrade(
    plan_id: uuid.UUID = Body(..., embed=True),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """
    Solicita upgrade para um novo plano.
    Gera um chamado de suporte interno e uma fatura pendente (simulado).
    """
    plan = await session.get(PlanoAssinatura, plan_id)
    if not plan or not plan.ativo:
        raise HTTPException(status_code=404, detail="Plano não encontrado ou inativo")
        
    # Verifica se já está nesse plano
    stmt = select(AssinaturaTenant).where(AssinaturaTenant.tenant_id == tenant.id)
    result = await session.execute(stmt)
    assinatura = result.scalar_one_or_none()
    
    if assinatura and assinatura.plano_id == plan_id:
        raise HTTPException(status_code=400, detail="Você já possui este plano.")

    # Em uma implementação real, integraríamos com Stripe ou geraria fatura.
    # Aqui, vamos registrar a intenção e avisar o suporte.
    return {
        "message": f"Solicitação de upgrade para {plan.nome} recebida!",
        "instructions": "Nossa equipe entrará em contato em instantes para concluir a migração."
    }


@router.get("/limits")
async def get_tenant_limits(
    request: Request,
    claims: dict = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna status dos limites do grupo ativo (via X-Fazenda-Id ou X-Grupo-Id).
    """
    from core.models.billing import AssinaturaTenant, PlanoAssinatura
    from core.dependencies import _resolve_grupo_id

    tenant_id_str = claims.get("tenant_id")
    if not tenant_id_str:
        raise HTTPException(status_code=403, detail="Contexto de tenant ausente")

    tenant_id = uuid.UUID(tenant_id_str)
    grupo_id = await _resolve_grupo_id(request, tenant_id, session)

    # Buscar assinatura ativa do grupo
    stmt = (
        select(PlanoAssinatura)
        .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
        .where(
            AssinaturaTenant.tenant_id == tenant_id,
            AssinaturaTenant.status == "ATIVA",
            AssinaturaTenant.tipo_assinatura == "GRUPO",
        )
    )
    if grupo_id:
        stmt = stmt.where(AssinaturaTenant.grupo_fazendas_id == grupo_id)
    stmt = stmt.limit(1)
    result = await session.execute(stmt)
    plano = result.scalar_one_or_none()

    if not plano:
        return {
            "max_fazendas": {"atual": 0, "limite": 0, "porcentagem": 0.0, "atingido": False},
            "max_usuarios": {"atual": 0, "limite": 0, "porcentagem": 0.0, "atingido": False},
            "storage": {"atual": 0, "limite": 0, "porcentagem": 0.0, "atingido": False},
        }

    # Contar fazendas
    fazendas_count_stmt = select(func.count(Fazenda.id)).where(Fazenda.tenant_id == tenant_id, Fazenda.ativo == True)
    fazendas_result = await session.execute(fazendas_count_stmt)
    fazendas_atual = fazendas_result.scalar_one() or 0

    max_fazendas = plano.max_fazendas
    fazendas_limite = None if max_fazendas == -1 else max_fazendas
    fazendas_porcentagem = (fazendas_atual / fazendas_limite * 100) if fazendas_limite and fazendas_limite > 0 else 0.0

    # Contar usuários
    usuarios_count_stmt = select(func.count(TenantUsuario.id)).where(
        TenantUsuario.tenant_id == tenant_id,
        TenantUsuario.status == "ATIVO",
    )
    usuarios_result = await session.execute(usuarios_count_stmt)
    usuarios_atual = usuarios_result.scalar_one() or 0

    max_usuarios = plano.limite_usuarios_maximo
    usuarios_limite = None if max_usuarios is None else max_usuarios
    usuarios_porcentagem = (usuarios_atual / usuarios_limite * 100) if usuarios_limite and usuarios_limite > 0 else 0.0

    # Storage
    tenant = await session.get(Tenant, tenant_id)
    storage_atual = tenant.storage_usado_mb if tenant else 0
    storage_limite = tenant.storage_limite_mb if tenant else 0
    storage_porcentagem = (storage_atual / storage_limite * 100) if storage_limite > 0 else 0.0

    return {
        "max_fazendas": {
            "atual": fazendas_atual,
            "limite": fazendas_limite,
            "porcentagem": round(fazendas_porcentagem, 2),
            "atingido": fazendas_atual >= fazendas_limite if fazendas_limite else False,
        },
        "max_usuarios": {
            "atual": usuarios_atual,
            "limite": usuarios_limite,
            "porcentagem": round(usuarios_porcentagem, 2),
            "atingido": usuarios_atual >= usuarios_limite if usuarios_limite else False,
        },
        "storage": {
            "atual": storage_atual,
            "limite": storage_limite,
            "porcentagem": round(storage_porcentagem, 2),
            "atingido": storage_atual >= storage_limite,
        },
    }
