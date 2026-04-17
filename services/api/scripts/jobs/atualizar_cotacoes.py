#!/usr/bin/env python3
"""
Job: Atualizar cotações de commodities.

Executar via cron diário (ex: 06:00 BRT, antes do mercado abrir):
    0 6 * * 1-5 cd /opt/lampp/htdocs/farm/services/api && .venv/bin/python scripts/jobs/atualizar_cotacoes.py

Ou manualmente:
    .venv/bin/python scripts/jobs/atualizar_cotacoes.py --fonte CEPEA
"""
import sys
import asyncio
import argparse
sys.path.insert(0, '.')

from core.config import settings
from sqlalchemy import text


async def run(fonte: str | None = None):
    import asyncpg

    url = str(settings.database_url).replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(url)

    # Buscar todos os tenants ativos
    tenants = await conn.fetch("SELECT id FROM tenants WHERE ativo = true")

    if not tenants:
        print("⚠️  Nenhum tenant ativo encontrado.")
        await conn.close()
        return

    print(f"📈 Atualizando cotações para {len(tenants)} tenant(s)...")
    print(f"   Fonte forçada: {fonte or 'auto (CEPEA → CBOT → B3)'}")
    print()

    from core.cadastros.commodities.cotacao_service import CotacaoService
    from core.database import async_session_maker

    total_sucesso = 0
    total_falha = 0

    for tenant in tenants:
        tenant_id = tenant["id"]
        async with async_session_maker() as session:
            svc = CotacaoService(session, tenant_id)
            try:
                resultado = await svc.atualizar_todas(fonte=fonte)
                total_sucesso += resultado["sucesso"]
                total_falha += resultado["falha"]

                print(f"  Tenant {tenant_id}: {resultado['sucesso']}✅ {resultado['falha']}❌ de {resultado['total']}")
                for d in resultado["detalhes"]:
                    if d["erro"]:
                        print(f"    ❌ {d['commodity']:20s} — {d['erro']}")
                    else:
                        print(f"    ✅ {d['commodity']:20s} {d['preco']:>10.2f} ({d['fonte']})")
            except Exception as e:
                print(f"  ❌ Tenant {tenant_id}: ERRO — {e}")
                total_falha += 1
            finally:
                await svc.close()

    await conn.close()

    print()
    print("=" * 60)
    print(f"  Total: {total_sucesso}✅  {total_falha}❌")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Atualizar cotações de commodities")
    parser.add_argument("--fonte", choices=["CEPEA", "CBOT", "B3"], help="Forçar fonte específica")
    args = parser.parse_args()

    print("=" * 60)
    print("  Atualizar Cotações de Commodities")
    print("=" * 60)
    print()

    asyncio.run(run(fonte=args.fonte))
