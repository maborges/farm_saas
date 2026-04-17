"""
Script para testar o endpoint de detalhes do tenant localmente
"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import async_session_maker
from core.models.tenant import Tenant
from core.models.billing import AssinaturaTenant, PlanoAssinatura
from core.models.unidade_produtiva import UnidadeProdutiva as Fazenda
from core.models.auth import Usuario, TenantUsuario, FazendaUsuario, PerfilAcesso
from sqlalchemy import select

async def test_tenant_details():
    tenant_id = uuid.UUID("514c2ae2-c62a-4d2b-ba82-d7f7b5325da0")

    async with async_session_maker() as session:
        print("1. Buscando tenant...")
        tenant = await session.get(Tenant, tenant_id)
        if not tenant:
            print(f"   ❌ Tenant {tenant_id} não encontrado")
            return
        print(f"   ✓ Tenant encontrado: {tenant.nome}")
        print(f"   - modulos_ativos: {tenant.modulos_ativos}")
        print(f"   - modulos_ativos type: {type(tenant.modulos_ativos)}")

        print("\n2. Buscando assinaturas...")
        try:
            stmt_assinaturas = (
                .join(PlanoAssinatura, AssinaturaTenant.plano_id == PlanoAssinatura.id)
                .where(AssinaturaTenant.tenant_id == tenant_id)
            )
            result = await session.execute(stmt_assinaturas)
            assinaturas = result.all()
            print(f"   ✓ {len(assinaturas)} assinatura(s) encontrada(s)")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            import traceback
            traceback.print_exc()

        print("\n3. Buscando usuários...")
        try:
            stmt_usuarios = (
                select(Usuario, TenantUsuario, PerfilAcesso)
                .join(TenantUsuario, Usuario.id == TenantUsuario.usuario_id)
                .join(PerfilAcesso, TenantUsuario.perfil_id == PerfilAcesso.id)
                .where(TenantUsuario.tenant_id == tenant_id, TenantUsuario.status == "ATIVO")
            )
            result = await session.execute(stmt_usuarios)
            usuarios = result.all()
            print(f"   ✓ {len(usuarios)} usuário(s) encontrado(s)")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            import traceback
            traceback.print_exc()

        print("\n4. Buscando grupos...")
        try:
            stmt_grupos = (
            )
            result = await session.execute(stmt_grupos)
            grupos = result.scalars().all()
            print(f"   ✓ {len(grupos)} grupo(s) encontrado(s)")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tenant_details())
