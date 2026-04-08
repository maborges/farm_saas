"""Testa se está buscando SMTP do banco corretamente"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.services.email_service import email_service

async def test_smtp_config():
    print("\n" + "="*80)
    print("TESTANDO CONFIGURAÇÃO SMTP DO EMAIL SERVICE")
    print("="*80)
    
    # Teste 1: Sem tenant_id (deve buscar configuração global)
    print("\n📋 Teste 1: Buscando configuração global (sem tenant_id)")
    config1 = await email_service._get_smtp_config(tenant_id=None)
    print(f"Config obtida: {config1}")
    
    # Teste 2: Verifica se está usando configuração do banco ou .env
    print("\n📋 Verificação:")
    if config1.get('host') == 'smtp.hostinger.com':
        print("✅ CORRETO: Usando configuração do banco de dados!")
    elif config1.get('host') == 'smtp.mailtrap.io':
        print("❌ ERRADO: Usando configuração do .env.local!")
    else:
        print(f"⚠️  HOST desconhecido: {config1.get('host')}")
    
    print("\n" + "="*80)
    return config1

if __name__ == "__main__":
    asyncio.run(test_smtp_config())
