import uuid
from typing import List, Optional
from datetime import datetime, timedelta, timezone, date
import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from core.models.auth import Usuario, ConviteAcesso, PerfilAcesso, TenantUsuario, FazendaUsuario
from core.models.tenant import Tenant
from core.models.fazenda import Fazenda
from core.models.billing import PlanoAssinatura, AssinaturaTenant
from core.schemas.onboarding_schemas import AssinanteRegisterRequest, ConviteCreateRequest, ConviteResponse
from core.services.email_service import email_service
from loguru import logger

class OnboardingService:
    def __init__(self, session: AsyncSession, auth_service=None):
        self.session = session
        self.auth_svc = auth_service # pass AuthService instance to hash pass

    async def _get_perfil_owner_sistema(self) -> PerfilAcesso:
        """Retorna o perfil 'owner' padrão do sistema (tenant_id=NULL)."""
        from core.constants import TenantRoles
        stmt = select(PerfilAcesso).where(
            PerfilAcesso.tenant_id.is_(None),
            PerfilAcesso.is_custom == False,
            PerfilAcesso.nome == TenantRoles.OWNER,
        )
        perfil = (await self.session.execute(stmt)).scalar_one_or_none()
        if not perfil:
            raise HTTPException(
                status_code=500,
                detail="Perfil padrão 'owner' não encontrado. Execute: python scripts/seed_perfis.py"
            )
        return perfil

    async def register_new_tenant(self, data: AssinanteRegisterRequest) -> Usuario:
        """
        Cria do zero: Usuário (Dono) -> Tenant (SaaS) -> Fazenda (Propriedade) -> Assinatura Padrão
        """
        # 1. Checar email
        stmt = select(Usuario).where((Usuario.email == data.email) | (Usuario.username == data.username))
        if (await self.session.execute(stmt)).scalars().first():
            raise HTTPException(status_code=400, detail="E-mail ou Username já existe no sistema.")

        # 2. Criar Usuario Global
        hashed_pw = self.auth_svc.get_password_hash(data.senha) if self.auth_svc else "hash_dummy"
        user = Usuario(
            email=data.email,
            username=data.username,
            nome_completo=data.nome_completo,
            senha_hash=hashed_pw
        )
        self.session.add(user)
        await self.session.flush()

        # 3. Criar a Conta (Tenant)
        tenant = Tenant(
            nome=f"Fazendas {data.nome_completo}",
            documento=data.cnpj_tenant,
            modulos_ativos=["CORE"] # Inicia apenas com módulo base, o financeiro ativará o resto
        )
        self.session.add(tenant)
        await self.session.flush()

        # 4. Buscar Perfil de Acesso Root (sistema, compartilhado)
        perfil_admin = await self._get_perfil_owner_sistema()

        # 5. Criar vínculo Usuario <-> Tenant como Owner
        tu = TenantUsuario(
            tenant_id=tenant.id,
            usuario_id=user.id,
            perfil_id=perfil_admin.id,
            is_owner=True
        )
        self.session.add(tu)
        
        # 6. Criar a Primeira Fazenda
        fazenda = Fazenda(
            tenant_id=tenant.id,
            nome=data.nome_fazenda
        )
        self.session.add(fazenda)
        await self.session.flush()
        
        # 7. Vincular o Owner a essa Fazenda
        fu = FazendaUsuario(
            tenant_id=tenant.id,
            usuario_id=user.id,
            fazenda_id=fazenda.id
        )
        self.session.add(fu)

        # 8. Criar a Assinatura Financeira Pendente
        # Encontra o plano básico/default ou cria um fake caso banco esteja raspado
        plano_stmt = select(PlanoAssinatura).limit(1)
        plano = (await self.session.execute(plano_stmt)).scalar_one_or_none()
        
        if not plano:
            plano = PlanoAssinatura(nome="Plano Base Starter", modulos_inclusos=["CORE", "A1"])
            self.session.add(plano)
            await self.session.flush()

        assinatura = AssinaturaTenant(
            tenant_id=tenant.id,
            plano_id=plano.id,
            status="PENDENTE" # Fica aguardando comprovante + aprovação
        )
        self.session.add(assinatura)

        await self.session.commit()

        # Enviar Boas-vindas (Background)
        try:
            await email_service.send_welcome(
                email=user.email,
                nome=user.nome_completo or user.username,
                tenant_nome=tenant.nome,
                username=user.username
            )
        except Exception as e:
            logger.error(f"Falha ao enviar email de boas-vindas: {e}")

        return user


    # ========================================================
    # GESTÃO DE CONVITES REGRAS 6 e 11
    # ========================================================

    async def enviar_convite(self, tenant_id: uuid.UUID, invoker_user_id: uuid.UUID, data: ConviteCreateRequest) -> ConviteAcesso:
        # Validação de segurança: Quem convida é owner/admin do tenant? (Pular no MVP isolado de Service)
        
        token = secrets.token_urlsafe(32)
        
        dt_val = None
        if data.data_validade_acesso:
            dt_val = date.fromisoformat(data.data_validade_acesso)

        convite = ConviteAcesso(
            tenant_id=tenant_id,
            email_convidado=data.email_convidado,
            perfil_id=data.perfil_id,
            fazendas_ids=data.fazendas_ids,
            token_convite=token,
            data_expiracao=datetime.now(timezone.utc) + timedelta(days=3), # Expira em 3 dias
            data_validade_acesso=dt_val
        )
        self.session.add(convite)
        await self.session.commit()
        
        # Enviar E-mail real de Convite
        try:
            # Buscar nomes para o template
            tenant = await self.session.get(Tenant, tenant_id)
            invoker = await self.session.get(Usuario, invoker_user_id)
            perfil = await self.session.get(PerfilAcesso, data.perfil_id)
            
            await email_service.send_invite(
                email=data.email_convidado,
                remetente=invoker.nome_completo or invoker.username,
                tenant_nome=tenant.nome,
                perfil_nome=perfil.nome,
                token=token
            )
        except Exception as e:
            logger.error(f"Falha ao disparar convite p/ {data.email_convidado}: {e}")
        
        return convite


    async def aceitar_convite(self, token: str, user_id: uuid.UUID):
        stmt = select(ConviteAcesso).where(
            ConviteAcesso.token_convite == token, 
            ConviteAcesso.status == "PENDENTE"
        )
        convite = (await self.session.execute(stmt)).scalar_one_or_none()
        
        if not convite:
            raise HTTPException(status_code=404, detail="Convite inválido, expirado ou já aceito.")
            
        if convite.data_expiracao < datetime.utcnow():
            convite.status = "EXPIRADO"
            await self.session.commit()
            raise HTTPException(status_code=400, detail="Convite expirado.")

        # Vínculo no Tenant
        # Checar unicidade de Vínculo (Regra 10)
        check_tu = select(TenantUsuario).where(
            TenantUsuario.tenant_id == convite.tenant_id,
            TenantUsuario.usuario_id == user_id
        )
        existe_tu = (await self.session.execute(check_tu)).scalar_one_or_none()
        
        if not existe_tu:
            tu = TenantUsuario(
                tenant_id=convite.tenant_id,
                usuario_id=user_id,
                perfil_id=convite.perfil_id,
                data_validade_acesso=convite.data_validade_acesso
            )
            self.session.add(tu)
            
        # Vínculo nas Fazendas
        for fazenda_id_str in convite.fazendas_ids:
            check_fu = select(FazendaUsuario).where(
                FazendaUsuario.usuario_id == user_id,
                FazendaUsuario.fazenda_id == uuid.UUID(fazenda_id_str)
            )
            existe_fu = (await self.session.execute(check_fu)).scalar_one_or_none()
            if not existe_fu:
                fu = FazendaUsuario(
                    tenant_id=convite.tenant_id,
                    usuario_id=user_id,
                    fazenda_id=uuid.UUID(fazenda_id_str)
                )
                self.session.add(fu)

        # Trancar convite
        convite.status = "ACEITO"
        await self.session.commit()
        return {"status": "success", "message": "Bem-vindo à Fazenda!"}
