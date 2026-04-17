"""
Script de diagnóstico: verifica por que /api/v1/fazendas/ retorna 402
Versão PostgreSQL
"""
import asyncio
import asyncpg
import json

DB_CONFIG = {
    "user": "borgus",
    "password": "numsey01",
    "host": "192.168.0.2",
    "database": "farms",
}

async def main():
    print("=" * 80)
    print("DIAGNÓSTICO - Erro 402 em /fazendas/")
    print(f"Banco: PostgreSQL @ {DB_CONFIG['host']}/{DB_CONFIG['database']}")
    print("=" * 80)

    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 1. Ver tenants
        print("\n📋 TENANTS:")
        tenants = await conn.fetch("SELECT id, nome FROM tenants LIMIT 5")
        for t in tenants:
            print(f"  Tenant ID: {t['id']} | Nome: {t['nome']}")
        
        if not tenants:
            print("  ❌ NENHUM tenant encontrado!")

        # 2. Ver grupos de fazendas
        print("\n🏘️ GRUPOS DE FAZENDAS:")
        grupos = await conn.fetch("SELECT id, nome, tenant_id FROM grupos_fazendas LIMIT 10")
        for g in grupos:
            print(f"  Grupo: {g['id']} | Nome: {g['nome']} | Tenant: {g['tenant_id']}")
        
        if not grupos:
            print("  ❌ NENHUM grupo encontrado!")

        # 3. Ver planos de assinatura
        print("\n💳 PLANOS_ASSINATURA:")
        planos = await conn.fetch("SELECT id, nome, modulos_inclusos FROM planos_assinatura")
        for p in planos:
            modulos = p['modulos_inclusos'] if isinstance(p['modulos_inclusos'], list) else json.loads(p['modulos_inclusos']) if p['modulos_inclusos'] else []
            print(f"  Plano: {p['id']} | {p['nome']} | Módulos: {modulos}")
        
        if not planos:
            print("  ❌ NENHUM plano encontrado!")

        # 4. Ver assinaturas
        print("\n📝 ASSINATURAS_TENANT:")
        assinaturas = await conn.fetch("""
                   at.status, at.tipo_assinatura, pa.modulos_inclusos
            FROM assinaturas_tenant at
            JOIN planos_assinatura pa ON at.plano_id = pa.id
            LIMIT 10
        """)
        
        if not assinaturas:
            print("  ❌ NENHUMA assinatura encontrada!")
        else:
            for a in assinaturas:
                modulos = a['modulos_inclusos'] if isinstance(a['modulos_inclusos'], list) else json.loads(a['modulos_inclusos']) if a['modulos_inclusos'] else []
                print(f"  ID: {a['id']}")
                print(f"    Plano: {a['plano_id']} | Status: {a['status']} | Tipo: {a['tipo_assinatura']}")
                print(f"    Módulos: {modulos}")
                print()

        # 5. Ver fazendas
        print("\n🌾 FAZENDAS:")
        fazendas = await conn.fetch("SELECT id, nome, tenant_id, grupo_id FROM fazendas LIMIT 10")
        for f in fazendas:
            print(f"  Fazenda: {f['id']} | Nome: {f['nome']} | Tenant: {f['tenant_id']} | Grupo: {f['grupo_id']}")
        
        if not fazendas:
            print("  ❌ NENHUMA fazenda encontrada!")

        # Diagnóstico
        print("\n" + "=" * 80)
        print("ANÁLISE:")
        print("=" * 80)
        
        if not assinaturas:
            print("\n❌ PROBLEMA: Tenant sem assinatura!")
            print("\n💡 SOLUÇÃO:")
            print("   Execute: cd services/api && python3 scripts/seed_plans.py")
            print("   Execute: cd services/api && python3 scripts/seed_dev.py")
            print("\n   Ou use o backoffice para ativar um plano para o tenant.")
        else:
            for a in assinaturas:
                modulos = a['modulos_inclusos'] if isinstance(a['modulos_inclusos'], list) else json.loads(a['modulos_inclusos']) if a['modulos_inclusos'] else []
                
                if a['status'] not in ("ATIVA", "PENDENTE_PAGAMENTO", "TRIAL"):
                    print(f"\n⚠️ Assinatura {a['id']}: Status '{a['status']}' inválido")
                
                if a['tipo_assinatura'] != "GRUPO":
                    print(f"\n⚠️ Assinatura {a['id']}: Tipo '{a['tipo_assinatura']}' deveria ser 'GRUPO'")
                
                if "CORE" not in modulos:
                    print(f"\n❌ Plano {a['plano_id']} NÃO tem módulo CORE!")
                    print(f"   Módulos: {modulos}")
                else:
                    print(f"\n✅ Tenant {a['tenant_id']}: CORE presente no plano {a['plano_id']}")
                    print(f"   Módulos: {modulos}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
