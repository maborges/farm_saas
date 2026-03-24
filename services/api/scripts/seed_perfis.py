import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from core.database import async_session_maker
from core.models.auth import PerfilAcesso
from core.constants import TenantRoles, TenantPermissions


# Perfis padrão do sistema (tenant_id=NULL)
PERFIS_PADRAO = [
    {
        "nome": TenantRoles.OWNER,
        "descricao": TenantRoles.DESCRIPTIONS[TenantRoles.OWNER],
        "permissoes": {"permissions": TenantPermissions.PERMISSIONS_MAP[TenantRoles.OWNER]},
    },
    {
        "nome": TenantRoles.ADMIN,
        "descricao": TenantRoles.DESCRIPTIONS[TenantRoles.ADMIN],
        "permissoes": {"permissions": TenantPermissions.PERMISSIONS_MAP[TenantRoles.ADMIN]},
    },
    {
        "nome": TenantRoles.GERENTE,
        "descricao": TenantRoles.DESCRIPTIONS[TenantRoles.GERENTE],
        "permissoes": {"permissions": TenantPermissions.PERMISSIONS_MAP[TenantRoles.GERENTE]},
    },
    {
        "nome": TenantRoles.AGRONOMO,
        "descricao": TenantRoles.DESCRIPTIONS[TenantRoles.AGRONOMO],
        "permissoes": {"permissions": TenantPermissions.PERMISSIONS_MAP[TenantRoles.AGRONOMO]},
    },
    {
        "nome": TenantRoles.OPERADOR,
        "descricao": TenantRoles.DESCRIPTIONS[TenantRoles.OPERADOR],
        "permissoes": {"permissions": TenantPermissions.PERMISSIONS_MAP[TenantRoles.OPERADOR]},
    },
    {
        "nome": TenantRoles.CONSULTOR,
        "descricao": TenantRoles.DESCRIPTIONS[TenantRoles.CONSULTOR],
        "permissoes": {"permissions": TenantPermissions.PERMISSIONS_MAP[TenantRoles.CONSULTOR]},
    },
    {
        "nome": TenantRoles.FINANCEIRO,
        "descricao": TenantRoles.DESCRIPTIONS[TenantRoles.FINANCEIRO],
        "permissoes": {"permissions": TenantPermissions.PERMISSIONS_MAP[TenantRoles.FINANCEIRO]},
    },
]


async def seed_perfis():
    async with async_session_maker() as session:
        # Buscar perfis de sistema já existentes (tenant_id=NULL, is_custom=False)
        result = await session.execute(
            select(PerfilAcesso).where(
                PerfilAcesso.tenant_id.is_(None),
                PerfilAcesso.is_custom == False,
            )
        )
        existentes = {p.nome for p in result.scalars().all()}

        novos = []
        atualizados = 0

        for perfil_data in PERFIS_PADRAO:
            if perfil_data["nome"] in existentes:
                # Atualizar permissões caso tenham mudado
                result = await session.execute(
                    select(PerfilAcesso).where(
                        PerfilAcesso.tenant_id.is_(None),
                        PerfilAcesso.is_custom == False,
                        PerfilAcesso.nome == perfil_data["nome"],
                    )
                )
                perfil = result.scalar_one()
                perfil.descricao = perfil_data["descricao"]
                perfil.permissoes = perfil_data["permissoes"]
                atualizados += 1
            else:
                novos.append(
                    PerfilAcesso(
                        tenant_id=None,
                        nome=perfil_data["nome"],
                        descricao=perfil_data["descricao"],
                        is_custom=False,
                        permissoes=perfil_data["permissoes"],
                    )
                )

        if novos:
            session.add_all(novos)

        await session.commit()
        print(f"Perfis padrão: {len(novos)} criados, {atualizados} atualizados.")


if __name__ == "__main__":
    asyncio.run(seed_perfis())
