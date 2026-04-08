"""
Script de diagnóstico para verificar configurações SMTP
"""
import asyncio
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import async_session_maker
from core.models.tenant import Tenant
from core.models.configuration import ConfiguracaoSaaS
from core.models.auth import Usuario
from core.models.auth import TenantUsuario
from core.config import settings
from sqlalchemy import select


async def debug_smtp_config():
    print("=" * 80)
    print("DIAGNÓSTICO DE CONFIGURAÇÃO SMTP")
    print("=" * 80)
    
    # 1. Verifica configurações de ambiente
    print("\n📋 1. CONFIGURAÇÕES DO .env.local (Fallback):")
    print(f"   SMTP Host: {settings.smtp_host}")
    print(f"   SMTP Port: {settings.smtp_port}")
    print(f"   SMTP User: {settings.smtp_user or '(vazio)'}")
    print(f"   SMTP Pass: {settings.smtp_pass or '(vazio)'}")
    print(f"   Mail From: {settings.mail_from}")
    
    # 2. Verifica configuração global do SaaS
    print("\n📋 2. CONFIGURAÇÃO GLOBAL DO SAAS (configuracoes_saas):")
    async with async_session_maker() as session:
        stmt = select(ConfiguracaoSaaS).where(
            ConfiguracaoSaaS.chave == "smtp_global",
            ConfiguracaoSaaS.ativo == True
        )
        result = await session.execute(stmt)
        config_db = result.scalar_one_or_none()
        
        if config_db:
            print(f"   ✅ Encontrada! ID: {config_db.id}")
            print(f"   Descrição: {config_db.descricao}")
            print(f"   Valor: {config_db.valor}")
        else:
            print("   ❌ Nenhuma configuração SMTP global encontrada no banco")
    
    # 3. Verifica tenants e suas configurações
    print("\n📋 3. TENANTS E CONFIGURAÇÕES SMTP:")
    async with async_session_maker() as session:
        stmt = select(Tenant)
        result = await session.execute(stmt)
        tenants = result.scalars().all()
        
        if not tenants:
            print("   ⚠️  Nenhum tenant encontrado")
        else:
            for tenant in tenants:
                print(f"\n   Tenant: {tenant.nome}")
                print(f"   ID: {tenant.id}")
                print(f"   Email Responsável: {tenant.email_responsavel or '(não definido)'}")
                if tenant.smtp_config:
                    print(f"   ✅ SMTP Config: {tenant.smtp_config}")
                else:
                    print("   ❌ Sem configuração SMTP específica")
    
    # 4. Verifica usuários e seus tenants
    print("\n📋 4. USUÁRIOS E VÍNCULOS COM TENANTS:")
    async with async_session_maker() as session:
        stmt = select(Usuario).limit(10)
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        if not users:
            print("   ⚠️  Nenhum usuário encontrado")
        else:
            for user in users:
                print(f"\n   Usuário: {user.nome_completo or user.username}")
                print(f"   Email: {user.email}")
                print(f"   ID: {user.id}")
                
                # Busca tenant do usuário
                tenant_stmt = select(TenantUsuario).where(
                    TenantUsuario.usuario_id == user.id,
                    TenantUsuario.status == "ATIVO"
                ).limit(1)
                tenant_result = await session.execute(tenant_stmt)
                tenant_usuario = tenant_result.scalar_one_or_none()
                
                if tenant_usuario:
                    print(f"   ✅ Tenant ID: {tenant_usuario.tenant_id}")
                    
                    # Busca dados do tenant
                    tenant_data = await session.get(Tenant, tenant_usuario.tenant_id)
                    if tenant_data:
                        print(f"   Tenant Nome: {tenant_data.nome}")
                        if tenant_data.smtp_config:
                            print(f"   Tenant SMTP: {tenant_data.smtp_config}")
                        else:
                            print("   Tenant SMTP: ❌ Não configurado (usará configuração global)")
                else:
                    print("   ❌ Sem tenant ativo (usará fallback .env)")
    
    # 5. Simula o fluxo de recuperação de senha
    print("\n" + "=" * 80)
    print("SIMULAÇÃO DO FLUXO DE RECUPERAÇÃO DE SENHA")
    print("=" * 80)
    
    # Pede email do usuário
    email_teste = input("\nDigite o email do usuário para testar (ou pressione Enter para usar o primeiro): ")
    
    async with async_session_maker() as session:
        if email_teste:
            stmt = select(Usuario).where(Usuario.email == email_teste)
        else:
            stmt = select(Usuario).limit(1)
        
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ Usuário não encontrado!")
            return
        
        print(f"\n👤 Usuário encontrado: {user.nome_completo or user.username}")
        print(f"   Email: {user.email}")
        
        # Busca tenant
        tenant_stmt = select(TenantUsuario).where(
            TenantUsuario.usuario_id == user.id,
            TenantUsuario.status == "ATIVO"
        ).limit(1)
        tenant_result = await session.execute(tenant_stmt)
        tenant_usuario = tenant_result.scalar_one_or_none()
        
        tenant_id = None
        if tenant_usuario:
            tenant_id = tenant_usuario.tenant_id
            print(f"✅ Tenant ID encontrado: {tenant_id}")
            
            # Busca configuração do tenant
            tenant_data = await session.get(Tenant, tenant_id)
            if tenant_data and tenant_data.smtp_config:
                print(f"✅ Usando SMTP do Tenant: {tenant_data.smtp_config}")
                return tenant_data.smtp_config
        else:
            print("⚠️  Usuário sem tenant ativo")
        
        # Busca configuração global
        print("\n🔍 Buscando configuração global do SaaS...")
        stmt = select(ConfiguracaoSaaS).where(
            ConfiguracaoSaaS.chave == "smtp_global",
            ConfiguracaoSaaS.ativo == True
        )
        result = await session.execute(stmt)
        config_db = result.scalar_one_or_none()
        
        if config_db:
            print(f"✅ Usando configuração global: {config_db.valor}")
            return config_db.valor
        else:
            print("⚠️  Sem configuração global, usando fallback .env")
            fallback = {
                "host": settings.smtp_host,
                "port": settings.smtp_port,
                "user": settings.smtp_user or "(vazio)",
                "pass": settings.smtp_pass or "(vazio)",
                "from": settings.mail_from
            }
            print(f"📧 Fallback: {fallback}")
            return fallback


if __name__ == "__main__":
    config = asyncio.run(debug_smtp_config())
    
    print("\n" + "=" * 80)
    print("RESUMO DA CONFIGURAÇÃO SMTP QUE SERÁ USADA:")
    print("=" * 80)
    print(f"\n{config}")
    print("\n" + "=" * 80)
