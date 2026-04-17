"""
Teste: verifica se o endpoint de produtos retorna os produtos do seed
"""
import asyncio
import httpx
from sqlalchemy import select
from core.database import async_session_maker
import core.models  # noqa: F401
from core.models.auth import Usuario
from core.models.tenant import Tenant
from jose import jwt
from datetime import datetime, timedelta
from core.config import settings

async def create_test_token(user_id: str, tenant_id: str) -> str:
    """Cria um JWT token de teste"""
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "type": "access"
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

async def run():
    async with async_session_maker() as session:
        # Buscar um usuário e tenant válidos
        usuario = (await session.execute(select(Usuario).limit(1))).scalar_one_or_none()
        tenant = (await session.execute(select(Tenant).limit(1))).scalar_one_or_none()
        
        if not usuario or not tenant:
            print("Erro: Usuario ou Tenant não encontrados")
            return
        
        user_id = str(usuario.id)
        tenant_id = str(tenant.id)
        print(f"Usuário: {usuario.id} | {getattr(usuario, 'nome', getattr(usuario, 'email', 'N/A'))}")
        print(f"Tenant: {tenant.id} | {getattr(tenant, 'nome', getattr(tenant, 'razao_social', 'N/A'))}")
        
        # Criar token
        token = await create_test_token(user_id, tenant_id)
        print(f"\nToken gerado: {token[:30]}...")
        
        # Fazer requisição ao endpoint
        headers = {
            "Authorization": f"Bearer {token}",
            "x-tenant-id": tenant_id,
        }
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get("http://127.0.0.1:8000/api/v1/cadastros/produtos", headers=headers, timeout=10.0)
                print(f"\nStatus: {resp.status_code}")
                print(f"Content-Type: {resp.headers.get('content-type', 'N/A')}")
                
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"\n✅ Produtos retornados: {len(data)}")
                    if data:
                        print("\nPrimeiros 3 produtos:")
                        for p in data[:3]:
                            print(f"  - {p.get('nome')} | tipo={p.get('tipo')} | ativo={p.get('ativo')} | marca={p.get('marca_nome', 'N/A')}")
                    else:
                        print("⚠️ Nenhum produto retornado!")
                else:
                    print(f"\n❌ Erro: {resp.text[:200]}")
                    
            except Exception as e:
                print(f"\n❌ Erro na requisição: {e}")

if __name__ == "__main__":
    asyncio.run(run())
