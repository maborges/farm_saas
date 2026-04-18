"""Shared helpers for integration tests."""
import uuid
from sqlalchemy import text

PLANO_BASE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

MODULOS_ADMIN = [
    "CORE",
    "A1_PLANEJAMENTO", "A2_CAMPO", "A3_DEFENSIVOS", "A4_PRECISAO", "A5_COLHEITA",
    "F1_TESOURARIA", "F2_CUSTOS_ABC", "F3_FISCAL",
    "O1_FROTA", "O2_ESTOQUE", "O3_COMPRAS",
    "P1_REBANHO",
    "RH1_REMUNERACAO", "RH2_SEGURANCA",
]


async def garantir_assinatura(session, tenant_id: uuid.UUID) -> None:
    """Cria plano + assinatura ativa para o tenant, necessário para require_module()."""
    import json
    modulos_json = json.dumps(MODULOS_ADMIN)
    await session.execute(text("""
        INSERT INTO planos_assinatura
            (id, nome, modulos_inclusos, limite_usuarios_minimo, limite_usuarios_maximo,
             preco_mensal, preco_anual, max_fazendas, max_categorias_plano,
             tem_trial, dias_trial, is_free, destaque, ordem,
             ativo, disponivel_site, disponivel_crm, created_at)
        VALUES
            (:id, 'Plano Admin Teste', CAST(:modulos AS json), 1, 100,
             0, 0, -1, -1, false, 0, false, false, 0,
             true, false, true, NOW())
        ON CONFLICT (id) DO UPDATE SET modulos_inclusos = CAST(:modulos AS json)
    """), {"id": str(PLANO_BASE_ID), "modulos": modulos_json})

    await session.execute(text("""
        INSERT INTO assinaturas_tenant
            (id, tenant_id, plano_id, status, tipo_assinatura, ciclo_pagamento, data_inicio, created_at, updated_at)
        VALUES
            (:id, :tenant_id, :plano_id, 'ATIVA', 'TENANT', 'MENSAL', NOW(), NOW(), NOW())
        ON CONFLICT (tenant_id, tipo_assinatura) DO UPDATE
            SET plano_id = EXCLUDED.plano_id, status = 'ATIVA'
    """), {"id": str(uuid.uuid4()), "tenant_id": str(tenant_id), "plano_id": str(PLANO_BASE_ID)})
