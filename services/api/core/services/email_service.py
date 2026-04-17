import aiosmtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
import os
import uuid
from loguru import logger
from core.config import settings

class EmailService:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
    async def _get_smtp_config(self, tenant_id: uuid.UUID = None):
        """Busca configuração SMTP com hierarquia: Tenant -> DB Global -> Env Vars."""
        from core.database import async_session_maker
        from core.models.tenant import Tenant
        from core.models.configuration import ConfiguracaoSaaS
        from sqlalchemy import select

        async with async_session_maker() as session:
            # 1. White-label Tenant specific
            if tenant_id:
                tenant = await session.get(Tenant, tenant_id)
                if tenant and tenant.smtp_config:
                    return tenant.smtp_config

            # 2. Global DB Config
            stmt = select(ConfiguracaoSaaS).where(ConfiguracaoSaaS.chave == "smtp_global", ConfiguracaoSaaS.ativo == True)
            res = await session.execute(stmt)
            config_db = res.scalar_one_or_none()
            if config_db:
                return config_db.valor

        # 3. Fallback Env
        return {
            "host": settings.smtp_host,
            "port": settings.smtp_port,
            "user": settings.smtp_user,
            "pass": settings.smtp_pass,
            "from": settings.mail_from
        }

    async def _send(self, to_email: str, subject: str, html_content: str, tenant_id: uuid.UUID = None):
        """Método interno para envio via SMTP dinâmico."""
        config = await self._get_smtp_config(tenant_id)
        
        message = EmailMessage()
        message["From"] = config.get("from", settings.mail_from)
        message["To"] = to_email
        message["Subject"] = subject
        message.add_alternative(html_content, subtype="html")

        try:
            host = config.get("host")
            port = int(config.get("port", 587))
            user = config.get("user")
            pwd = config.get("pass")

            if user and pwd:
                await aiosmtplib.send(
                    message,
                    hostname=host,
                    port=port,
                    username=user,
                    password=pwd,
                    use_tls=port == 465,
                    start_tls=port == 587
                )
            else:
                await aiosmtplib.send(message, hostname=host, port=port)
                
            logger.info(f"Email enviado ({'White-label' if tenant_id else 'SaaS'}) para {to_email}")
        except Exception as e:
            logger.error(f"Falha ao enviar email para {to_email}: {e}")

    async def send_invoice_approved(self, email: str, nome: str, plano: str, valor: float, tenant_id: uuid.UUID = None):
        template = self.env.get_template("emails/invoice_approved.html")
        html = template.render(
            nome_cliente=nome,
            nome_plano=plano,
            valor=f"{valor:.2f}",
            referência="Mensalidade AgroSaaS",
            login_url="http://localhost:3000/login"
        )
        await self._send(email, "Pagamento Confirmado - AgroSaaS", html, tenant_id)

    async def send_invoice_rejected(self, email: str, nome: str, justificativa: str, tenant_id: uuid.UUID = None):
        template = self.env.get_template("emails/invoice_rejected.html")
        html = template.render(
            nome_cliente=nome,
            justificativa=justificativa,
            billing_url="http://localhost:3000/settings/account"
        )
        await self._send(email, "⚠️ Ação Necessária: Problema no Pagamento", html, tenant_id)

    async def send_welcome(self, email: str, nome: str, tenant_nome: str, username: str, tenant_id: uuid.UUID = None):
        template = self.env.get_template("emails/welcome.html")
        html = template.render(
            nome_cliente=nome,
            nome_tenant=tenant_nome,
            username=username,
            login_url="http://localhost:3000/login"
        )
        await self._send(email, "Bem-vindo ao AgroSaaS! 🚜", html, tenant_id)

    async def send_invite(self, email: str, remetente: str, tenant_nome: str, perfil_nome: str, token: str, tenant_id: uuid.UUID = None):
        template = self.env.get_template("emails/invite.html")
        html = template.render(
            remetente=remetente,
            nome_tenant=tenant_nome,
            perfil_nome=perfil_nome,
            invite_url=f"{settings.frontend_url}/convite/aceitar?token={token}"
        )
        await self._send(email, f"Convite: {tenant_nome} no AgroSaaS", html, tenant_id)

    async def send_password_recovery(self, email: str, nome_usuario: str, token: str, tenant_id: uuid.UUID = None):
        """Envia e-mail de recuperação de senha com token expirável."""
        template = self.env.get_template("emails/password_reset.html")
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"
        from datetime import datetime
        html = template.render(
            nome_usuario=nome_usuario,
            email_usuario=email,
            reset_url=reset_url,
            data_solicitacao=datetime.now().strftime("%d/%m/%Y às %H:%M")
        )
        await self._send(email, "Recuperação de Senha - AgroSaaS 🔑", html, tenant_id)

    async def send_trial_notice(self, email: str, nome: str, nome_produtor: str, nome_plano: str, dias_trial: int, data_vencimento, tenant_id: uuid.UUID = None):
        """Envia e-mail com aviso de período de trial para nova assinatura."""
        template = self.env.get_template("emails/trial_notice.html")
        from datetime import datetime
        data_vencimento_str = data_vencimento.strftime("%d/%m/%Y") if hasattr(data_vencimento, 'strftime') else str(data_vencimento)

        html = template.render(
            nome_usuario=nome,
            nome_produtor=nome_produtor,
            nome_plano=nome_plano,
            dias_trial=dias_trial,
            data_vencimento=data_vencimento_str,
            dashboard_url=f"{settings.frontend_url}/dashboard"
        )
        await self._send(email, f"Período de Trial Iniciado - {dias_trial} dias grátis 🎉", html, tenant_id)

email_service = EmailService()
