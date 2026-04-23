"""
Script de emergência: encerra conexões ociosas do banco farms.
Execute com: ./.venv/bin/python scripts/kill_idle_connections.py
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://borgus:numsey01@192.168.0.2/farms"


async def main() -> None:
    # Conectar com pool mínimo — uma única conexão
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Ver conexões abertas
        rows = await conn.fetch(
            """
            SELECT pid, state, wait_event_type, wait_event,
                   now() - state_change AS idle_duration,
                   query
            FROM pg_stat_activity
            WHERE datname = 'farms'
              AND pid <> pg_backend_pid()
            ORDER BY state, idle_duration DESC NULLS LAST;
            """
        )
        print(f"\n{'PID':>8}  {'STATE':12}  {'IDLE':>12}  QUERY")
        print("-" * 80)
        for r in rows:
            idle = str(r["idle_duration"]).split(".")[0] if r["idle_duration"] else "—"
            q = (r["query"] or "")[:60].replace("\n", " ")
            print(f"{r['pid']:>8}  {str(r['state'] or '—'):12}  {idle:>12}  {q}")

        idle_pids = [
            r["pid"] for r in rows
            if r["state"] in ("idle", "idle in transaction", "idle in transaction (aborted)")
        ]

        if not idle_pids:
            print("\n✅ Nenhuma conexão ociosa encontrada.")
            return

        print(f"\n⚠️  {len(idle_pids)} conexões ociosas encontradas. Terminando...")
        for pid in idle_pids:
            result = await conn.fetchval("SELECT pg_terminate_backend($1)", pid)
            status = "✅ encerrada" if result else "⚠️  já fechada"
            print(f"   PID {pid}: {status}")

        print("\n✅ Limpeza concluída.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
