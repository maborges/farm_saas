"""
Testes para criação de nova assinatura (Nova Conta de Produtor).
- Criar tenant com trial 15 dias
- Gerar Fatura com vencimento correto
- Enviar email de aviso
"""
import pytest
import uuid
from datetime import datetime, timedelta, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.auth import Usuario
from core.models.tenant import Tenant
from core.models.billing import PlanoAssinatura, AssinaturaTenant, Fatura
# grupos_fazendas removed
from core.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_create_tenant_for_user_trial_pago(db_session: AsyncSession):
    """Testa criação de tenant com plano pago (deve criar trial + fatura)."""
    # Setup
    user = Usuario(
        email="teste@example.com",
        username="teste",
        nome_completo="Teste User",
        senha_hash="dummy_hash",
        ativo=True,
    )
    db_session.add(user)
    await db_session.flush()

    plano = PlanoAssinatura(
        nome="Pro",
        descricao="Plano profissional",
        preco_mensal=299.00,
        preco_anual=3000.00,
        is_free=False,
        tem_trial=True,
        dias_trial=15,
        modulos_inclusos=["CORE", "A1"],
        max_fazendas=10,
    )
    db_session.add(plano)
    await db_session.flush()

    svc = AuthService(db_session)

    # Execute
    result = await svc.create_tenant_for_user(
        user_id=user.id,
        nome="Fazenda Silva",
        plano_id=plano.id,
        ciclo="MENSAL",
        cpf_cnpj="12.345.678/0001-99",
    )

    # Assert
    assert result["access_token"]
    assert result["tenant_id"]
    assert result["nome_tenant"] == "Fazenda Silva"
    assert result["is_trial"] == True
    assert result["trial_expira_em"] is not None
    assert result["data_primeiro_vencimento"] is not None

    # Verificar Tenant criado
    tenant = await db_session.get(Tenant, result["tenant_id"])
    assert tenant is not None
    assert tenant.nome == "Fazenda Silva"
    assert tenant.documento == "12.345.678/0001-99"
    assert tenant.ativo == True

    from sqlalchemy import select
    grupos = (await db_session.execute(
    )).scalars().all()
    assert len(grupos) == 1
    grupo = grupos[0]
    assert grupo.ativo == True

    # Verificar Assinatura
    assinaturas = (await db_session.execute(
        select(AssinaturaTenant).where(AssinaturaTenant.tenant_id == tenant.id)
    )).scalars().all()
    assert len(assinaturas) == 1
    assin = assinaturas[0]
    assert assin.status == "TRIAL"
    assert assin.ciclo_pagamento == "MENSAL"

    # Verificar Fatura criada
    faturas = (await db_session.execute(
        select(Fatura).where(Fatura.assinatura_id == assin.id)
    )).scalars().all()
    assert len(faturas) == 1
    fatura = faturas[0]
    assert fatura.status == "ABERTA"
    assert fatura.valor == 299.00

    # Verificar data de vencimento = dia após trial terminar
    trial_expira = result["trial_expira_em"]
    esperado_vencimento = (trial_expira + timedelta(days=1)).date()
    assert fatura.data_vencimento.date() == esperado_vencimento

    # Verificar TenantUsuario (owner)
    from core.models.auth import TenantUsuario
    tenants_usuario = (await db_session.execute(
        select(TenantUsuario).where(
            TenantUsuario.tenant_id == tenant.id,
            TenantUsuario.usuario_id == user.id
        )
    )).scalars().all()
    assert len(tenants_usuario) == 1
    assert tenants_usuario[0].is_owner == True


@pytest.mark.asyncio
async def test_create_tenant_for_user_plan_gratis(db_session: AsyncSession):
    """Testa criação com plano gratuito (sem trial, sem fatura)."""
    user = Usuario(
        email="teste2@example.com",
        username="teste2",
        nome_completo="Teste User 2",
        senha_hash="dummy_hash",
        ativo=True,
    )
    db_session.add(user)
    await db_session.flush()

    plano = PlanoAssinatura(
        nome="Free",
        preco_mensal=0.0,
        preco_anual=0.0,
        is_free=True,
        tem_trial=False,
        modulos_inclusos=["CORE"],
        max_fazendas=1,
    )
    db_session.add(plano)
    await db_session.flush()

    svc = AuthService(db_session)

    result = await svc.create_tenant_for_user(
        user_id=user.id,
        nome="Sítio Small",
        plano_id=plano.id,
        ciclo="MENSAL",
    )

    assert result["access_token"]
    assert result["is_trial"] == False
    assert result["trial_expira_em"] is None
    assert result["data_primeiro_vencimento"] is None

    # Verificar Assinatura com status ATIVA (não TRIAL)
    from sqlalchemy import select
    assin = (await db_session.execute(
        select(AssinaturaTenant).where(
            AssinaturaTenant.tenant_id == result["tenant_id"]
        )
    )).scalar_one_or_none()
    assert assin.status == "ATIVA"

    # Verificar SEM fatura
    faturas = (await db_session.execute(
        select(Fatura).where(Fatura.assinatura_id == assin.id)
    )).scalars().all()
    assert len(faturas) == 0


@pytest.mark.asyncio
async def test_create_tenant_isolacao_multitenancy(db_session: AsyncSession):
    """Testa que novo tenant fica isolado de outros tenants."""
    # Criar 2 usuários
    user1 = Usuario(email="u1@x.com", username="u1", nome_completo="U1", senha_hash="x")
    user2 = Usuario(email="u2@x.com", username="u2", nome_completo="U2", senha_hash="x")
    db_session.add_all([user1, user2])
    await db_session.flush()

    plano = PlanoAssinatura(
        nome="Pro",
        preco_mensal=299.0,
        is_free=False,
        tem_trial=True,
        dias_trial=15,
        modulos_inclusos=["CORE"],
        max_fazendas=10,
    )
    db_session.add(plano)
    await db_session.flush()

    svc = AuthService(db_session)

    # Criar 2 tenants
    res1 = await svc.create_tenant_for_user(user1.id, "Fazenda A", plano.id)
    res2 = await svc.create_tenant_for_user(user2.id, "Fazenda B", plano.id)

    tenant1_id = uuid.UUID(res1["tenant_id"])
    tenant2_id = uuid.UUID(res2["tenant_id"])

    assert tenant1_id != tenant2_id

    # Verificar que Fatura 1 pertence a Tenant 1
    from sqlalchemy import select
    fatura1 = (await db_session.execute(
        select(Fatura).where(Fatura.tenant_id == tenant1_id)
    )).scalars().all()
    assert len(fatura1) == 1
    assert fatura1[0].tenant_id == tenant1_id

    # Verificar que Fatura 2 pertence a Tenant 2
    fatura2 = (await db_session.execute(
        select(Fatura).where(Fatura.tenant_id == tenant2_id)
    )).scalars().all()
    assert len(fatura2) == 1
    assert fatura2[0].tenant_id == tenant2_id
