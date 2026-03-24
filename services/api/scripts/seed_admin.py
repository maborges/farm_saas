import asyncio
import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import async_session_maker
from core.models.admin_user import AdminUser
from core.models.email_template import EmailTemplate
from core.services.auth_service import hash_password
import uuid


async def seed_admin_user():
    """Cria usuário admin padrão."""
    async with async_session_maker() as session:
        # Verificar se já existe
        from sqlalchemy import select
        stmt = select(AdminUser).where(AdminUser.email == "admin@agrosass.com")
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            print("✅ Admin user já existe")
            return

        admin = AdminUser(
            email="admin@agrosass.com",
            senha_hash=hash_password("admin123"),
            nome="Administrador",
            role="super_admin",
            ativo=True
        )

        session.add(admin)
        await session.commit()
        print("✅ Admin user criado: admin@agrosass.com / admin123")


async def seed_email_templates():
    """Cria templates de email padrão."""
    async with async_session_maker() as session:
        templates = [
            {
                "codigo": "WELCOME",
                "nome": "Boas-vindas",
                "assunto": "Bem-vindo ao AgroSaaS!",
                "corpo_html": """
                    <h2>Olá {{nome_responsavel}},</h2>
                    <p>Bem-vindo ao AgroSaaS!</p>
                    <p>Sua conta foi criada com sucesso.</p>
                    <p><strong>Dados de acesso:</strong></p>
                    <ul>
                        <li>URL: {{tenant_url}}</li>
                        <li>Email: {{email}}</li>
                    </ul>
                    <p><a href="{{tenant_url}}">Acessar sistema</a></p>
                """,
                "corpo_texto": "Bem-vindo ao AgroSaaS! Acesse: {{tenant_url}}",
                "variaveis": ["nome_responsavel", "tenant_url", "email"],
                "tipo": "transacional"
            },
            {
                "codigo": "PASSWORD_RESET",
                "nome": "Reset de Senha",
                "assunto": "Redefinição de Senha - AgroSaaS",
                "corpo_html": """
                    <h2>Olá {{nome_responsavel}},</h2>
                    <p>Sua senha foi redefinida.</p>
                    <p><strong>Senha temporária:</strong> {{senha_temporaria}}</p>
                    <p>Você será obrigado a alterar no próximo login.</p>
                    <p><a href="{{tenant_url}}">Acessar sistema</a></p>
                """,
                "corpo_texto": "Senha resetada: {{senha_temporaria}}",
                "variaveis": ["nome_responsavel", "senha_temporaria", "tenant_url"],
                "tipo": "transacional"
            }
        ]

        for tpl_data in templates:
            # Verificar se já existe
            from sqlalchemy import select
            stmt = select(EmailTemplate).where(EmailTemplate.codigo == tpl_data["codigo"])
            result = await session.execute(stmt)
            if result.scalar_one_or_none():
                print(f"✅ Template {tpl_data['codigo']} já existe")
                continue

            template = EmailTemplate(**tpl_data)
            session.add(template)

        await session.commit()
        print(f"✅ {len(templates)} templates criados")


async def main():
    print("🚀 Iniciando seed de dados admin...")
    await seed_admin_user()
    await seed_email_templates()
    print("✅ Seed concluído!")


if __name__ == "__main__":
    asyncio.run(main())
