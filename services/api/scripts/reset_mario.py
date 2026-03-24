import asyncio
from core.database import async_session_maker
from core.models.auth import Usuario
from core.services.auth_service import AuthService
from sqlalchemy import select

async def reset():
    print("Iniciando reset de senha...")
    async with async_session_maker() as session:
        auth_svc = AuthService(session)
        res = await session.execute(select(Usuario).where(Usuario.email == 'mario.agronomo@teste.com'))
        u = res.scalar_one_or_none()
        if u:
            u.senha_hash = auth_svc.get_password_hash('agro123')
            await session.commit()
            print('Senha de Mario resetada para: agro123')
        else:
            print('Usuário Mario não encontrado no banco.')

if __name__ == "__main__":
    asyncio.run(reset())
