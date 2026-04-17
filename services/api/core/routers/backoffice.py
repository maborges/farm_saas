from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import uuid
from loguru import logger

from core.dependencies import get_session, get_current_admin
from core.models.tenant import Tenant
from core.models.auth import Usuario, TenantUsuario
from core.models.billing import AssinaturaTenant, PlanoAssinatura, Fatura
from core.models.support import ChamadoSuporte, MensagemChamado, TicketStatus
from core.schemas.billing_schemas import (
    PlanoAssinaturaCreate, PlanoAssinaturaResponse, PlanoAssinaturaUpdate,
    FaturaResponse, ReviewInvoiceRequest
)
from core.schemas.support_schemas import (
    ChamadoSuporteResponse, ChamadoDetalheResponse, MensagemChamadoCreate, MensagemChamadoResponse
)
from core.services.email_service import email_service

router = APIRouter(prefix="/backoffice", tags=["Backoffice"])

@router.get("/bi/stats", dependencies=[Depends(get_current_admin)])
async def get_bi_stats(session: AsyncSession = Depends(get_session)):
    """Visão analítica profunda (BI) sobre a saúde do SaaS."""
    # 1. Churn Rate (Simulado com base em assinaturas inativas)
    total_assinaturas = await session.execute(select(func.count(AssinaturaTenant.id)))
    num_total = total_assinaturas.scalar_one() or 1
    
    inativas = await session.execute(select(func.count(AssinaturaTenant.id)).where(AssinaturaTenant.status == "CANCELADA"))
    num_inativas = inativas.scalar_one() or 0
    
    churn_rate = (num_inativas / num_total) * 100
    
    # 2. LTV (Lifetime Value) - Média MRR / Churn Rate
    mrr_res = await session.execute(select(func.sum(PlanoAssinatura.preco_mensal)).join(AssinaturaTenant).where(AssinaturaTenant.status == "ATIVA"))
    mrr = mrr_res.scalar_one() or 0
    avg_ticket = mrr / (num_total - num_inativas) if (num_total - num_inativas) > 0 else 0
    
    ltv = avg_ticket / (churn_rate / 100) if churn_rate > 0 else avg_ticket * 24 # Assume 2 anos se churn zero
    
    # 3. Retenção por Coorte (Simulado)
    coortes = [
        {"periodo": "2025-Q4", "tamanho": 45, "retencao": 92.5},
        {"periodo": "2026-Q1", "tamanho": 62, "retencao": 88.2},
        {"periodo": "2026-Q2", "tamanho": 28, "retencao": 95.0},
    ]

    # 4. Distribuição por Plano (Real)
    plano_dist = await session.execute(
        select(PlanoAssinatura.nome, func.count(AssinaturaTenant.id), func.sum(PlanoAssinatura.preco_mensal))
        .join(AssinaturaTenant)
        .group_by(PlanoAssinatura.nome)
    )
    dist = []
    for r in plano_dist:
        dist.append({
            "plano": r[0],
            "clientes": r[1],
            "receita": float(r[2] or 0)
        })

    # 5. Engajamento (Simulado - Seria contagem de operações agrícolas/financeiras)
    engajamento = {
        "usuarios_ativos_dia": int((num_total - num_inativas) * 0.65),
        "operacoes_por_dia": 1240,
        "hectares_gerenciados": 15400.5
    }

    return {
        "churn_rate": round(churn_rate, 2),
        "ltv": float(ltv),
        "cac_simulado": 450.0, # Custo de aquisição médio
        "payback_meses": round(450 / avg_ticket, 1) if avg_ticket > 0 else 0,
        "coortes": coortes,
        "distribuicao_receita": dist,
        "engajamento": engajamento,
        "periodo_analise": "Março/2026"
    }

@router.get("/dashboard/stats", dependencies=[Depends(get_current_admin)])
async def get_backoffice_stats(session: AsyncSession = Depends(get_session)):
    """Métricas avançadas para o Dashboard Administrativo do SaaS."""
    
    # 1. Contagens Básicas
    total_tenants = (await session.execute(select(func.count(Tenant.id)))).scalar()
    active_tenants = (await session.execute(select(func.count(Tenant.id)).where(Tenant.ativo == True))).scalar()
    total_users = (await session.execute(select(func.count(Usuario.id)))).scalar()
    
    # 2. Receita Mensal Recorrente (MRR) - Estimativa baseada em planos ativos
    # Seleciona soma dos preços mensais das assinaturas ATIVAS
    mrr_stmt = (
        select(func.sum(PlanoAssinatura.preco_mensal))
        .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
        .where(AssinaturaTenant.status == "ATIVA")
    )
    mrr_result = await session.execute(mrr_stmt)
    mrr_total = mrr_result.scalar() or 0.0

    # 3. Tendência de Faturamento (Mock para o gráfico por enquanto)
    # Em produção isso viria de um count/sum nas faturas agrupado por mês
    receita_trend = [
        {"mes": "Out", "valor": mrr_total * 0.7},
        {"mes": "Nov", "valor": mrr_total * 0.75},
        {"mes": "Dez", "valor": mrr_total * 0.82},
        {"mes": "Jan", "valor": mrr_total * 0.90},
        {"mes": "Fev", "valor": mrr_total * 0.95},
        {"mes": "Mar", "valor": mrr_total}
    ]

    # 4. Distribuição por Plano
    plano_dist_stmt = (
        select(PlanoAssinatura.nome, func.count(AssinaturaTenant.id))
        .join(AssinaturaTenant, AssinaturaTenant.plano_id == PlanoAssinatura.id)
        .group_by(PlanoAssinatura.nome)
    )
    plano_dist_result = await session.execute(plano_dist_stmt)
    distribuicao_planos = [{"name": r[0], "value": r[1]} for r in plano_dist_result]

    return {
        "resumo": {
            "mrr": float(mrr_total),
            "tenants_ativos": active_tenants,
            "tenants_total": total_tenants,
            "usuarios_total": total_users
        },
        "graficos": {
            "receita": receita_trend,
            "planos": distribuicao_planos
        },
        "plataforma": {
            "versao": "1.0.0-pro",
            "status": "online"
        }
    }

@router.get("/tenants", dependencies=[Depends(get_current_admin)])
async def list_tenants(session: AsyncSession = Depends(get_session)):
    """Lista todos os produtores e o status de suas assinaturas."""
    
    stmt = (
        select(Tenant, AssinaturaTenant, PlanoAssinatura)
        .outerjoin(AssinaturaTenant, Tenant.id == AssinaturaTenant.tenant_id)
        .outerjoin(PlanoAssinatura, AssinaturaTenant.plano_id == PlanoAssinatura.id)
        .order_by(Tenant.created_at.desc())
    )
    
    results = await session.execute(stmt)
    
    data = []
    for tenant, assinatura, plano in results:
        data.append({
            "id": tenant.id,
            "nome": tenant.nome,
            "documento": tenant.documento,
            "ativo": tenant.ativo,
            "modulos": plano.modulos_inclusos if plano else [],
            "data_cadastro": tenant.created_at,
            "assinatura": {
                "plano": plano.nome if plano else "Sem Plano",
                "plano_id": plano.id if plano else None,
                "status": assinatura.status if assinatura else "INATIVA",
                "ciclo": assinatura.ciclo_pagamento if assinatura else None
            }
        })
        
    return data

@router.post("/tenants/{tenant_id}/toggle-status", dependencies=[Depends(get_current_admin)])
async def toggle_tenant_status(tenant_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    """Bloqueia ou desbloqueia um Tenant (corte total de acesso)."""
    tenant = await session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    
    tenant.ativo = not tenant.ativo
    await session.commit()
    
    return {"id": tenant_id, "novo_status": tenant.ativo}

@router.get("/plans", response_model=List[PlanoAssinaturaResponse], dependencies=[Depends(get_current_admin)])
async def list_plans(session: AsyncSession = Depends(get_session)):
    """Lista todos os pacotes de assinatura."""
    stmt = select(PlanoAssinatura).order_by(PlanoAssinatura.preco_mensal.asc())
    result = await session.execute(stmt)
    return result.scalars().all()

@router.post("/plans", response_model=PlanoAssinaturaResponse, dependencies=[Depends(get_current_admin)])
async def create_plan(plan_data: PlanoAssinaturaCreate, session: AsyncSession = Depends(get_session)):
    """Cria um novo plano/pacote comercial."""
    # Se o novo plano for marcado como padrão, desmarcar todos os outros
    if plan_data.is_default:
        stmt = select(PlanoAssinatura).where(PlanoAssinatura.is_default == True)
        result = await session.execute(stmt)
        existing_default = result.scalar_one_or_none()
        if existing_default:
            existing_default.is_default = False
            logger.info(f"Plano {existing_default.id} deixou de ser o plano padrão")

    new_plan = PlanoAssinatura(**plan_data.model_dump())
    session.add(new_plan)
    await session.commit()
    await session.refresh(new_plan)
    return new_plan

@router.patch("/plans/{plan_id}", response_model=PlanoAssinaturaResponse, dependencies=[Depends(get_current_admin)])
async def update_plan(plan_id: uuid.UUID, plan_data: PlanoAssinaturaUpdate, session: AsyncSession = Depends(get_session)):
    """Atualiza um plano/pacote comercial."""
    plan = await session.get(PlanoAssinatura, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado")

    # Se estão marcando este plano como padrão, desmarcar os outros
    if plan_data.is_default is True:
        stmt = select(PlanoAssinatura).where(
            PlanoAssinatura.is_default == True,
            PlanoAssinatura.id != plan_id
        )
        result = await session.execute(stmt)
        existing_default = result.scalar_one_or_none()
        if existing_default:
            existing_default.is_default = False
            logger.info(f"Plano {existing_default.id} deixou de ser o plano padrão")
    # Se estão desmarcando este plano como padrão e não há outro, impedir
    elif plan_data.is_default is False and plan.is_default:
        stmt = select(func.count(PlanoAssinatura.id)).where(
            PlanoAssinatura.is_default == True,
            PlanoAssinatura.id != plan_id
        )
        result = await session.execute(stmt)
        other_default_count = result.scalar_one() or 0
        if other_default_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Deve haver pelo menos um plano padrão. Marque outro plano como padrão antes de desmarcar este."
            )

    for field, value in plan_data.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    await session.commit()
    await session.refresh(plan)
    return plan

@router.post("/plans/{plan_id}/toggle-status", dependencies=[Depends(get_current_admin)])
async def toggle_plan_status(plan_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    """Ativa ou desativa um plano comercial."""
    plan = await session.get(PlanoAssinatura, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    
    plan.ativo = not plan.ativo
    await session.commit()
    return {"id": plan_id, "novo_status": plan.ativo}

@router.get("/modules", dependencies=[Depends(get_current_admin)])
async def list_modules():
    """Retorna o catálogo completo de módulos disponíveis com metadados."""
    from core.constants import ModuloMetadata
    resultado = []
    for modulo_id, meta in ModuloMetadata.CATALOGO.items():
        resultado.append({
            "id": modulo_id,
            "nome": meta.get("nome", modulo_id),
            "descricao": meta.get("descricao", ""),
            "categoria": meta.get("categoria", ""),
            "obrigatorio": meta.get("obrigatorio", False),
            "preco_base_mensal": meta.get("preco_base_mensal", 0.0),
            "dependencias": meta.get("dependencias", []),
        })
    return resultado


@router.post("/tenants/{tenant_id}/assign-plan/{plan_id}", dependencies=[Depends(get_current_admin)])
async def assign_plan_to_tenant(
    tenant_id: uuid.UUID, 
    plan_id: uuid.UUID, 
    session: AsyncSession = Depends(get_session)
):
    """Vincula um plano a um produtor e libera os módulos correspondentes."""
    tenant = await session.get(Tenant, tenant_id)
    plan = await session.get(PlanoAssinatura, plan_id)
    
    if not tenant or not plan:
        raise HTTPException(status_code=404, detail="Tenant ou Plano não encontrado")
    
    # Buscar assinatura atual
    stmt = select(AssinaturaTenant).where(AssinaturaTenant.tenant_id == tenant_id)
    result = await session.execute(stmt)
    assinatura = result.scalar_one_or_none()
    
    from datetime import datetime, timezone
    
    if not assinatura:
        assinatura = AssinaturaTenant(
            tenant_id=tenant_id,
            plano_id=plan_id,
            status="ATIVA",
            data_inicio=datetime.now(timezone.utc)
        )
        session.add(assinatura)
    else:
        assinatura.plano_id = plan_id
        assinatura.status = "ATIVA" # Garante Reativação se estivesse pendente
        
    await session.commit()

    return {
        "message": f"Plano {plan.nome} atribuído ao tenant {tenant.nome}",
        "modulos_liberados": plan.modulos_inclusos
    }

@router.get("/invoices", response_model=List[FaturaResponse], dependencies=[Depends(get_current_admin)])
async def list_invoices(session: AsyncSession = Depends(get_session)):
    """Lista todas as faturas para conferência financeira."""
    stmt = (
        select(Fatura, Tenant.nome.label("tenant_nome"), PlanoAssinatura.nome.label("plano_nome"))
        .join(Tenant, Fatura.tenant_id == Tenant.id)
        .join(AssinaturaTenant, Fatura.assinatura_id == AssinaturaTenant.id)
        .join(PlanoAssinatura, AssinaturaTenant.plano_id == PlanoAssinatura.id)
        .order_by(Fatura.created_at.desc())
    )
    result = await session.execute(stmt)
    
    invoices = []
    for row in result:
        fatura = row[0]
        invoices.append({
            "id": fatura.id,
            "tenant_id": fatura.tenant_id,
            "tenant_nome": row.tenant_nome,
            "plano_nome": row.plano_nome,
            "valor": float(fatura.valor),
            "data_vencimento": fatura.data_vencimento,
            "status": fatura.status,
            "url_comprovante": fatura.url_comprovante,
            "data_envio_comprovante": fatura.data_envio_comprovante,
            "justificativa_rejeicao": fatura.justificativa_rejeicao,
            "created_at": fatura.created_at
        })
    return invoices

@router.post("/invoices/{invoice_id}/review", dependencies=[Depends(get_current_admin)])
async def review_invoice(
    invoice_id: uuid.UUID,
    review: ReviewInvoiceRequest,
    admin: Usuario = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    """Aprova ou Rejeita um pagamento enviado pelo produtor."""
    # Buscar fatura com dados do tenant e plano
    stmt = (
        select(Fatura, Tenant, PlanoAssinatura, Usuario.email, Usuario.nome_completo)
        .join(Tenant, Fatura.tenant_id == Tenant.id)
        .join(AssinaturaTenant, Fatura.assinatura_id == AssinaturaTenant.id)
        .join(PlanoAssinatura, AssinaturaTenant.plano_id == PlanoAssinatura.id)
        .join(TenantUsuario, Tenant.id == TenantUsuario.tenant_id)
        .join(Usuario, TenantUsuario.usuario_id == Usuario.id)
        .where(Fatura.id == invoice_id, TenantUsuario.is_owner == True)
    )
    result = await session.execute(stmt)
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Fatura ou Proprietário não encontrados")
    
    fatura, tenant, plano, owner_email, owner_nome = row
    
    from datetime import datetime, timezone
    
    if review.aprovado:
        fatura.status = "PAGA"
    else:
        fatura.status = "REJEITADA"
        fatura.justificativa_rejeicao = review.justificativa
        
    fatura.operador_revisao_id = admin.id
    fatura.data_aprovacao_rejeicao = datetime.now(timezone.utc)
    
    await session.commit()

    # Enviar Notificação por E-mail (Background / Fire and Forget for UX)
    # Em produção usaríamos Celery, aqui faremos async simples
    try:
        if review.aprovado:
            await email_service.send_invoice_approved(
                email=owner_email,
                nome=owner_nome or tenant.nome,
                plano=plano.nome,
                valor=float(fatura.valor)
            )
        else:
            await email_service.send_invoice_rejected(
                email=owner_email,
                nome=owner_nome or tenant.nome,
                justificativa=review.justificativa
            )
    except Exception as e:
        logger.error(f"Erro ao disparar e-mail de notificação: {e}")

    return {"id": invoice_id, "novo_status": fatura.status}

@router.get("/users", dependencies=[Depends(get_current_admin)])
async def list_global_users(session: AsyncSession = Depends(get_session)):
    """Lista todos os usuários da plataforma com seus vínculos."""

    # Busca usuários, nomes dos tenants e se é owner
    stmt = (
        select(
            Usuario,
            func.string_agg(Tenant.nome, ',').label("tenants"),
            func.bool_or(TenantUsuario.is_owner).label("is_owner")
        )
        .outerjoin(TenantUsuario, Usuario.id == TenantUsuario.usuario_id)
        .outerjoin(Tenant, TenantUsuario.tenant_id == Tenant.id)
        .group_by(Usuario.id)
        .order_by(Usuario.created_at.desc())
    )
    result = await session.execute(stmt)

    users = []
    for row in result:
        u = row.Usuario
        users.append({
            "id": u.id,
            "nome": u.nome_completo,
            "email": u.email,
            "username": u.username,
            "is_superuser": u.is_superuser,
            "is_owner": row.is_owner or False,
            "ativo": u.ativo,
            "data_cadastro": u.created_at,
            "tenants": row.tenants.split(",") if row.tenants else []
        })
    return users

@router.post("/users/{user_id}/toggle-status", dependencies=[Depends(get_current_admin)])
async def toggle_user_status(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    """Bloqueia ou desbloqueia um usuário globalmente."""
    user = await session.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if user.is_superuser:
        raise HTTPException(status_code=400, detail="Não é possível desativar um superusuário por aqui.")

    # Verifica se o usuário é owner de algum tenant
    stmt_owner = select(TenantUsuario).where(
        TenantUsuario.usuario_id == user_id,
        TenantUsuario.is_owner == True
    )
    result = await session.execute(stmt_owner)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Não é possível desativar o proprietário (owner) de um tenant."
        )

    user.ativo = not user.ativo
    await session.commit()
    return {"id": user_id, "novo_status": user.ativo}

@router.post("/users/{user_id}/reset-password", dependencies=[Depends(get_current_admin)])
async def reset_user_password(
    user_id: uuid.UUID,
    enviar_email: bool = True,
    session: AsyncSession = Depends(get_session)
):
    """
    Reseta a senha de um usuário global e retorna a senha temporária.
    Opcionalmente envia a senha por e-mail.
    """
    import secrets
    import string
    from core.services.auth_service import hash_password

    user = await session.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if user.is_superuser:
        raise HTTPException(status_code=400, detail="Não é possível resetar senha de superusuário por aqui.")

    # Gerar senha aleatória segura (12 caracteres com símbolos)
    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    senha_temporaria = ''.join(secrets.choice(caracteres) for _ in range(12))

    user.senha_hash = hash_password(senha_temporaria)
    await session.commit()

    # Enviar e-mail com a senha temporária
    if enviar_email and user.email:
        try:
            await email_service.send_email(
                to=user.email,
                subject="Redefinição de Senha - AgroSaaS",
                html_content=f"""
                <h2>Olá {user.nome_completo or user.username},</h2>
                <p>Sua senha foi redefinida pelo administrador do sistema AgroSaaS.</p>
                <p><strong>Senha temporária:</strong> <code>{senha_temporaria}</code></p>
                <p>Por segurança, recomendamos criar uma nova senha no próximo acesso.</p>
                """
            )
        except Exception as e:
            import logging
            logging.error(f"Erro ao enviar e-mail de reset: {e}")

    return {
        "success": True,
        "senha_temporaria": senha_temporaria if not enviar_email else "Enviada por e-mail",
        "email_enviado": enviar_email,
        "usuario_email": user.email
    }

@router.get("/tickets", response_model=List[dict], dependencies=[Depends(get_current_admin)])
async def list_all_tickets(session: AsyncSession = Depends(get_session)):
    """Lista todos os chamados da plataforma para o administrador."""
    stmt = (
        select(ChamadoSuporte, Tenant.nome.label("tenant_nome"), Usuario.nome_completo.label("usuario_nome"))
        .join(Tenant, ChamadoSuporte.tenant_id == Tenant.id)
        .join(Usuario, ChamadoSuporte.usuario_abertura_id == Usuario.id)
        .order_by(ChamadoSuporte.created_at.desc())
    )
    result = await session.execute(stmt)
    
    tickets = []
    for row in result:
        c = row.ChamadoSuporte
        tickets.append({
            "id": c.id,
            "tenant_nome": row.tenant_nome,
            "usuario_nome": row.usuario_nome,
            "assunto": c.assunto,
            "categoria": c.categoria,
            "status": c.status,
            "prioridade": c.prioridade,
            "created_at": c.created_at
        })
    return tickets

@router.get("/tickets/{ticket_id}", response_model=ChamadoDetalheResponse, dependencies=[Depends(get_current_admin)])
async def get_admin_ticket_details(ticket_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    """Retorna detalhes de um chamado para o administrador."""
    chamado = await session.get(ChamadoSuporte, ticket_id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return chamado

@router.post("/tickets/{ticket_id}/reply", response_model=MensagemChamadoResponse, dependencies=[Depends(get_current_admin)])
async def admin_reply_to_ticket(
    ticket_id: uuid.UUID,
    data: MensagemChamadoCreate,
    admin: Usuario = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    """Administrador responde a um chamado."""
    chamado = await session.get(ChamadoSuporte, ticket_id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    
    msg = MensagemChamado(
        chamado_id=ticket_id,
        usuario_id=admin.id,
        conteudo=data.conteudo,
        anexo_url=data.anexo_url,
        is_admin_reply=True
    )
    
    # Atualiza status quando admin responde
    chamado.status = TicketStatus.AGUARDANDO_CLIENTE
    
    session.add(msg)
    await session.commit()
    return msg

@router.post("/tickets/{ticket_id}/close", dependencies=[Depends(get_current_admin)])
async def close_ticket(ticket_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    """Finaliza um chamado de suporte."""
    chamado = await session.get(ChamadoSuporte, ticket_id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    
    chamado.status = TicketStatus.CONCLUIDO
    await session.commit()
    return {"id": ticket_id, "status": "CONCLUIDO"}


@router.post("/tenants/{tenant_id}/reset-password", dependencies=[Depends(get_current_admin)])
async def reset_tenant_password(
    tenant_id: uuid.UUID,
    enviar_email: bool = True,
    session: AsyncSession = Depends(get_session)
):
    """
    Reseta a senha do responsável pelo tenant e opcionalmente envia email.
    """
    import secrets
    import string
    from core.services.auth_service import hash_password

    # Buscar tenant
    tenant = await session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    # Gerar senha aleatória
    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    senha_temporaria = ''.join(secrets.choice(caracteres) for _ in range(12))

    # Buscar usuário principal do tenant (admin/owner)
    stmt = (
        select(Usuario)
        .join(TenantUsuario)
        .where(
            TenantUsuario.tenant_id == tenant_id,
            TenantUsuario.is_owner == True
        )
    )
    result = await session.execute(stmt)
    usuario = result.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário responsável não encontrado")

    # Atualizar senha
    usuario.senha_hash = hash_password(senha_temporaria)
    # usuario.force_password_change = True  # Ativar se o campo existir no modelo Usuario

    await session.commit()

    # Enviar email se solicitado
    if enviar_email:
        # Tenta enviar usando o email_service existente
        try:
            await email_service.send_email(
                to=usuario.email,
                subject="Redefinição de Senha - AgroSaaS",
                html_content=f"""
                <h2>Olá {usuario.nome_completo or tenant.nome},</h2>
                <p>Sua senha foi redefinida pelo administrador do sistema.</p>
                <p><strong>Senha temporária:</strong> {senha_temporaria}</p>
                <p>Por segurança, recomendamos criar uma nova senha no próximo acesso.</p>
                <p><a href="https://app.agrosass.com">Acessar sistema</a></p>
                """
            )
        except Exception as e:
             # Log error but return success since password was reset
             import logging
             logging.error(f"Erro ao enviar email de reset: {e}")

    return {
        "success": True,
        "senha_temporaria": senha_temporaria if not enviar_email else "Enviada por e-mail",
        "email_enviado": enviar_email,
        "usuario_email": usuario.email
    }


@router.patch("/tenants/{tenant_id}/change-plan", dependencies=[Depends(get_current_admin)])
async def change_tenant_plan(
    tenant_id: uuid.UUID,
    novo_plano_id: uuid.UUID,
    admin_user: Usuario = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    """
    Altera o plano de assinatura de um tenant.
    """
    # Buscar tenant
    tenant = await session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    # Buscar novo plano
    novo_plano = await session.get(PlanoAssinatura, novo_plano_id)
    if not novo_plano or not novo_plano.ativo:
        raise HTTPException(status_code=404, detail="Plano não encontrado ou inativo")

    # Buscar assinatura atual
    stmt = select(AssinaturaTenant).where(AssinaturaTenant.tenant_id == tenant_id)
    result = await session.execute(stmt)
    assinatura = result.scalar_one_or_none()

    if not assinatura:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")

    # Guardar dados antigos para audit log
    plano_anterior_id = assinatura.plano_id

    # Atualizar assinatura
    assinatura.plano_id = novo_plano_id

    # Registrar no audit log
    from core.models.admin_audit_log import AdminAuditLog
    audit = AdminAuditLog(
        admin_user_id=admin_user.id,
        admin_email=admin_user.email,
        acao="tenant.change_plan",
        entidade="tenant",
        entidade_id=tenant_id,
        descricao=f"Alteração de plano de {plano_anterior_id} para {novo_plano_id}",
        dados_anteriores={"plano_id": str(plano_anterior_id)},
        dados_novos={"plano_id": str(novo_plano_id)}
    )
    session.add(audit)

    await session.commit()

    return {
        "success": True,
        "tenant_id": tenant_id,
        "plano_anterior_id": plano_anterior_id,
        "plano_novo_id": novo_plano_id,
        "plano_novo_nome": novo_plano.nome,
        "novos_modulos": novo_plano.modulos_inclusos
    }


@router.get("/tenants/{tenant_id}/details", dependencies=[Depends(get_current_admin)])
async def get_tenant_details(tenant_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    """
    Retorna detalhes completos de um tenant incluindo:
    - Todas as assinaturas (múltiplas)
    - Usuários associados
    - Grupos de fazendas com suas fazendas
    - Usuários por fazenda com perfis
    """
    from core.models.unidade_produtiva import UnidadeProdutiva as Fazenda
    # grupos_fazendas removed
    from core.models.auth import FazendaUsuario, PerfilAcesso
    from datetime import datetime, timedelta, timezone
    from loguru import logger

    try:
        # Buscar tenant
        tenant = await session.get(Tenant, tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant não encontrado")

        # Buscar TODAS as assinaturas do tenant
        stmt_assinaturas = (
            select(AssinaturaTenant, PlanoAssinatura)
            .join(PlanoAssinatura, AssinaturaTenant.plano_id == PlanoAssinatura.id)
            .where(AssinaturaTenant.tenant_id == tenant_id)
            .order_by(AssinaturaTenant.tipo_assinatura, AssinaturaTenant.created_at.desc())
        )
        result_assinaturas = await session.execute(stmt_assinaturas)

        assinaturas = []
        for assinatura, plano in result_assinaturas:
            # Calcular próxima renovação
            proxima_renovacao = None
            if assinatura.data_proxima_renovacao:
                proxima_renovacao = assinatura.data_proxima_renovacao
            elif assinatura.data_inicio and assinatura.status == "ATIVA":
                if assinatura.ciclo_pagamento == "MENSAL":
                    proxima_renovacao = assinatura.data_inicio + timedelta(days=30)
                elif assinatura.ciclo_pagamento == "ANUAL":
                    proxima_renovacao = assinatura.data_inicio + timedelta(days=365)

            assinaturas.append({
                "id": assinatura.id,
                "tipo": assinatura.tipo_assinatura,
                "plano": {
                    "id": plano.id,
                    "nome": plano.nome,
                    "preco_mensal": float(plano.preco_mensal),
                    "preco_anual": float(plano.preco_anual),
                    "modulos": plano.modulos_inclusos,
                    "limite_usuarios_maximo": plano.limite_usuarios_maximo
                },
                "status": assinatura.status,
                "ciclo_pagamento": assinatura.ciclo_pagamento,
                "data_inicio": assinatura.data_inicio,
                "data_proxima_renovacao": proxima_renovacao,
                "created_at": assinatura.created_at
            })

        # Buscar todos os usuários do tenant
        stmt_usuarios = (
            select(Usuario, TenantUsuario, PerfilAcesso)
            .join(TenantUsuario, Usuario.id == TenantUsuario.usuario_id)
            .join(PerfilAcesso, TenantUsuario.perfil_id == PerfilAcesso.id)
            .where(TenantUsuario.tenant_id == tenant_id, TenantUsuario.status == "ATIVO")
            .order_by(TenantUsuario.is_owner.desc(), Usuario.nome_completo)
        )
        result_usuarios = await session.execute(stmt_usuarios)

        usuarios = []
        for usuario, tenant_usuario, perfil in result_usuarios:
            usuarios.append({
                "id": usuario.id,
                "nome_completo": usuario.nome_completo,
                "email": usuario.email,
                "username": usuario.username,
                "is_owner": tenant_usuario.is_owner,
                "perfil": {
                    "id": perfil.id,
                    "nome": perfil.nome
                },
                "ativo": usuario.ativo,
                "created_at": usuario.created_at
            })

        # Buscar grupos de fazendas com fazendas e usuários
        stmt_grupos = (
        )
        result_grupos = await session.execute(stmt_grupos)
        grupos_fazendas = result_grupos.scalars().all()

        grupos_tree = []
        for grupo in grupos_fazendas:
            # Buscar fazendas do grupo
            stmt_fazendas = (
                select(Fazenda)
                .where(Fazenda.unidade_produtiva_id == grupo.id)
                .order_by(Fazenda.nome)
            )
            result_fazendas = await session.execute(stmt_fazendas)
            fazendas = result_fazendas.scalars().all()

            fazendas_data = []
            for fazenda in fazendas:
                # Buscar usuários da fazenda
                stmt_usuarios_fazenda = (
                    select(Usuario, FazendaUsuario, PerfilAcesso)
                    .join(FazendaUsuario, Usuario.id == FazendaUsuario.usuario_id)
                    .outerjoin(PerfilAcesso, FazendaUsuario.perfil_fazenda_id == PerfilAcesso.id)
                    .where(FazendaUsuario.unidade_produtiva_id == fazenda.id)
                    .order_by(Usuario.nome_completo)
                )
                result_usuarios_fazenda = await session.execute(stmt_usuarios_fazenda)

                usuarios_fazenda = []
                for usuario_f, fazenda_usuario, perfil_f in result_usuarios_fazenda:
                    usuarios_fazenda.append({
                        "id": usuario_f.id,
                        "nome_completo": usuario_f.nome_completo,
                        "email": usuario_f.email,
                        "perfil_fazenda": {
                            "id": perfil_f.id,
                            "nome": perfil_f.nome
                        } if perfil_f else None
                    })

                fazendas_data.append({
                    "id": fazenda.id,
                    "nome": fazenda.nome,
                    "cpf_cnpj": fazenda.cpf_cnpj,
                    "coordenadas_sede": fazenda.coordenadas_sede,
                    "area_total_ha": float(fazenda.area_total_ha) if fazenda.area_total_ha else None,
                    "usuarios": usuarios_fazenda
                })

            grupos_tree.append({
                "id": grupo.id,
                "nome": grupo.nome,
                "descricao": grupo.descricao,
                "fazendas": fazendas_data
            })

        # Buscar fazendas sem grupo
        stmt_fazendas_sem_grupo = (
            select(Fazenda)
            .where(Fazenda.tenant_id == tenant_id, Fazenda.unidade_produtiva_id == None)
            .order_by(Fazenda.nome)
        )
        result_fazendas_sem_grupo = await session.execute(stmt_fazendas_sem_grupo)
        fazendas_sem_grupo = result_fazendas_sem_grupo.scalars().all()

        fazendas_sem_grupo_data = []
        for fazenda in fazendas_sem_grupo:
            # Buscar usuários da fazenda
            stmt_usuarios_fazenda = (
                select(Usuario, FazendaUsuario, PerfilAcesso)
                .join(FazendaUsuario, Usuario.id == FazendaUsuario.usuario_id)
                .outerjoin(PerfilAcesso, FazendaUsuario.perfil_fazenda_id == PerfilAcesso.id)
                .where(FazendaUsuario.unidade_produtiva_id == fazenda.id)
                .order_by(Usuario.nome_completo)
            )
            result_usuarios_fazenda = await session.execute(stmt_usuarios_fazenda)

            usuarios_fazenda = []
            for usuario_f, fazenda_usuario, perfil_f in result_usuarios_fazenda:
                usuarios_fazenda.append({
                    "id": usuario_f.id,
                    "nome_completo": usuario_f.nome_completo,
                    "email": usuario_f.email,
                    "perfil_fazenda": {
                        "id": perfil_f.id,
                        "nome": perfil_f.nome
                    } if perfil_f else None
                })

            fazendas_sem_grupo_data.append({
                "id": fazenda.id,
                "nome": fazenda.nome,
                "cpf_cnpj": fazenda.cpf_cnpj,
                "coordenadas_sede": fazenda.coordenadas_sede,
                "area_total_ha": float(fazenda.area_total_ha) if fazenda.area_total_ha else None,
                "usuarios": usuarios_fazenda
            })

        return {
            "tenant": {
                "id": tenant.id,
                "nome": tenant.nome,
                "documento": tenant.documento,
                "ativo": tenant.ativo,
                "modulos_ativos": list({m for a in assinaturas for m in (a.get("plano") or {}).get("modulos", [])}),
                "created_at": tenant.created_at
            },
            "assinaturas": assinaturas,
            "usuarios": usuarios,
            "estrutura": {
                "grupos": grupos_tree,
                "fazendas_sem_grupo": fazendas_sem_grupo_data
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes do tenant {tenant_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/tenants/storage/alertas", dependencies=[Depends(get_current_admin)])
async def get_storage_alerts(
    limite_percentual: float = 80.0,
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna tenants com storage próximo ao limite.
    """
    stmt = (
        select(Tenant)
        .where(
            Tenant.ativo == True,
            Tenant.storage_usado_mb > (Tenant.storage_limite_mb * (limite_percentual / 100))
        )
    )
    result = await session.execute(stmt)
    tenants = result.scalars().all()

    alertas = []
    for tenant in tenants:
        percentual = (tenant.storage_usado_mb / tenant.storage_limite_mb) * 100 if tenant.storage_limite_mb > 0 else 0
        alertas.append({
            "tenant_id": tenant.id,
            "tenant_nome": tenant.nome,
            "storage_usado_mb": tenant.storage_usado_mb,
            "storage_limite_mb": tenant.storage_limite_mb,
            "percentual_uso": round(percentual, 2),
            "alerta": "critico" if percentual >= 95 else "alto" if percentual >= 90 else "medio"
        })

    # Ordenar por percentual de uso decrescente
    alertas.sort(key=lambda x: x["percentual_uso"], reverse=True)

    return {
        "total_alertas": len(alertas),
        "tenants": alertas
    }


# ==================== LOGIN RATE LIMITING - DESBLOQUEIO ====================

from core.schemas.auth_schemas import (
    LoginDesbloqueioRequest, LoginDesbloqueioResponse,
    LoginTentativasInfoResponse, LoginBloqueadosListaResponse
)
from core.services.login_rate_limit_service import LoginRateLimitService

@router.post("/login/desbloquear", dependencies=[Depends(get_current_admin)])
async def backoffice_desbloquear_login(
    dados: LoginDesbloqueioRequest,
    session: AsyncSession = Depends(get_session),
    admin: dict = Depends(get_current_admin)
):
    """
    Backoffice: Desbloqueia login de usuário por email.
    
    Admin do SaaS pode desbloquear qualquer usuário da plataforma.
    Útil quando usuário entra em contato relatando bloqueio acidental.
    """
    rate_limit_svc = LoginRateLimitService(session)
    
    # Verifica se há tentativas registradas
    info = await rate_limit_svc.get_tentativas_por_email(dados.email)
    
    if not info:
        return LoginDesbloqueioResponse(
            sucesso=False,
            mensagem=f"Nenhum registro de tentativas para {dados.email}",
            email=dados.email
        )
    
    if not info["bloqueado"]:
        return LoginDesbloqueioResponse(
            sucesso=False,
            mensagem=f"Usuário {dados.email} não está bloqueado no momento",
            email=dados.email
        )
    
    # Desbloqueia
    await rate_limit_svc.desbloquear_manual(dados.email)
    
    # Log de auditoria (opcional - pode ser expandido)
    logger.info(f"Backoffice desbloqueou login para {dados.email} por {admin.get('sub')}")
    
    return LoginDesbloqueioResponse(
        sucesso=True,
        mensagem=f"Usuário {dados.email} desbloqueado com sucesso. Pode tentar login imediatamente.",
        email=dados.email
    )


@router.get("/login/tentativas/{email}", dependencies=[Depends(get_current_admin)])
async def backoffice_ver_tentativas_login(
    email: str,
    session: AsyncSession = Depends(get_session),
    admin: dict = Depends(get_current_admin)
):
    """
    Backoffice: Visualiza tentativas de login de um usuário.
    
    Retorna informações sobre bloqueio, contador de tentativas e histórico.
    """
    rate_limit_svc = LoginRateLimitService(session)
    info = await rate_limit_svc.get_tentativas_por_email(email)
    
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhum registro de tentativas para {email}"
        )
    
    return LoginTentativasInfoResponse(**info)


@router.get("/login/bloqueados", dependencies=[Depends(get_current_admin)])
async def backoffice_listar_bloqueados(
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
    admin: dict = Depends(get_current_admin)
):
    """
    Backoffice: Lista usuários bloqueados nas últimas 24 horas.
    
    Permite monitorar bloqueios em massa (possível ataque) ou identificar
    usuários que precisam de suporte.
    """
    rate_limit_svc = LoginRateLimitService(session)
    bloqueados = await rate_limit_svc.listar_bloqueados_recentes(limit)
    
    return LoginBloqueadosListaResponse(
        total=len(bloqueados),
        bloqueados=[LoginBloqueadoItem(**b) for b in bloqueados]
    )



# ── Telemetria de Módulos ─────────────────────────────────────────────────────

@router.get(
    "/tenants/{tenant_id}/module-usage",
    summary="Uso de módulos por tenant nos últimos N dias",
    dependencies=[Depends(get_current_admin)],
)
async def backoffice_module_usage(
    tenant_id: uuid.UUID,
    days: int = 30,
    session: AsyncSession = Depends(get_session),
):
    from core.services.module_usage_service import get_usage_by_module
    return await get_usage_by_module(session, tenant_id, days)


@router.get(
    "/tenants/{tenant_id}/module-usage/{module_id}",
    summary="Série temporal diária de uso de um módulo específico",
    dependencies=[Depends(get_current_admin)],
)
async def backoffice_module_usage_daily(
    tenant_id: uuid.UUID,
    module_id: str,
    days: int = 30,
    session: AsyncSession = Depends(get_session),
):
    from core.services.module_usage_service import get_daily_usage
    return await get_daily_usage(session, tenant_id, module_id, days)
