"""Teste completo do fluxo de recuperação de senha"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.database import async_session_maker
from core.services.email_service import email_service
from core.models.auth import Usuario, TenantUsuario
from sqlalchemy import select

async def test_password_recovery_email():
    print("\n" + "="*80)
    print("TESTE DE ENVIO DE EMAIL DE RECUPERAÇÃO DE SENHA")
    print("="*80)
    
    async with async_session_maker() as session:
        # 1. Busca um usuário de teste
        print("\n📋 Passo 1: Buscando usuário...")
        stmt = select(Usuario).limit(1)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ Nenhum usuário encontrado!")
            return
        
        print(f"✅ Usuário: {user.nome_completo or user.username}")
        print(f"   Email: {user.email}")
        print(f"   ID: {user.id}")
        
        # 2. Busca tenant do usuário
        print("\n📋 Passo 2: Buscando tenant do usuário...")
        tenant_stmt = select(TenantUsuario).where(
            TenantUsuario.usuario_id == user.id,
            TenantUsuario.status == "ATIVO"
        ).limit(1)
        tenant_result = await session.execute(tenant_stmt)
        tenant_usuario = tenant_result.scalar_one_or_none()
        
        tenant_id = None
        if tenant_usuario:
            tenant_id = tenant_usuario.tenant_id
            print(f"✅ Tenant ID: {tenant_id}")
        else:
            print("⚠️  Usuário sem tenant ativo (usará configuração global)")
        
        # 3. Obtém configuração SMTP
        print("\n📋 Passo 3: Obtendo configuração SMTP...")
        smtp_config = await email_service._get_smtp_config(tenant_id)
        print(f"   Host: {smtp_config.get('host')}")
        print(f"   Port: {smtp_config.get('port')}")
        print(f"   User: {smtp_config.get('user')}")
        print(f"   From: {smtp_config.get('from')}")
        print(f"   Pass: {'*' * len(smtp_config.get('pass', ''))}")
        
        # 4. Tenta enviar email de teste
        print("\n📋 Passo 4: Enviando email de teste...")
        try:
            await email_service.send_password_recovery(
                email=user.email,
                nome_usuario=user.nome_completo or user.username,
                token="TESTE_TOKEN_123456",
                tenant_id=tenant_id
            )
            print("✅ Email enviado com sucesso!")
        except Exception as e:
            print(f"❌ ERRO ao enviar email: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(test_password_recovery_email())
