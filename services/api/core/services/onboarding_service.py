import uuid
from typing import List, Optional
from datetime import datetime, timedelta, timezone, date
import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from core.models.auth import Usuario, ConviteAcesso, PerfilAcesso, TenantUsuario, UnidadeProdutivaUsuario as FazendaUsuario
from core.models.tenant import Tenant
from core.models.unidade_produtiva import UnidadeProdutiva as Fazenda
from core.models.billing import PlanoAssinatura, AssinaturaTenant, Fatura
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
        Cria do zero: Usuário (Assinante) -> Tenant (Produtor) -> Assinatura + Fatura + Email
        """
        from decimal import Decimal

        # 1. Checar email/username duplicado
        stmt = select(Usuario).where((Usuario.email == data.email) | (Usuario.username == data.username))
        if (await self.session.execute(stmt)).scalars().first():
            raise HTTPException(status_code=400, detail="E-mail ou Username já existe no sistema.")

        # 2. Checar CNPJ/CPF duplicado (se informado)
        if data.cnpj_tenant:
            stmt = select(Tenant).where(Tenant.documento == data.cnpj_tenant)
            if (await self.session.execute(stmt)).scalars().first():
                raise HTTPException(status_code=400, detail="Este CPF ou CNPJ já está cadastrado no sistema.")

        # 3. Verificar plano escolhido
        plano = (await self.session.execute(
            select(PlanoAssinatura).where(PlanoAssinatura.id == data.plano_id, PlanoAssinatura.ativo == True)
        )).scalar_one_or_none()
        if not plano:
            raise HTTPException(status_code=404, detail="Plano não encontrado.")

        agora = datetime.now(timezone.utc)

        # 4. Criar Usuário Global (Assinante Administrador)
        hashed_pw = self.auth_svc.get_password_hash(data.senha) if self.auth_svc else "hash_dummy"
        user = Usuario(
            email=data.email,
            username=data.username,
            nome_completo=data.nome_completo,
            senha_hash=hashed_pw,
            cpf=data.cpf or None,
            telefone=data.telefone or None,
            ativo=True,
        )
        self.session.add(user)
        await self.session.flush()

        # 5. Criar Tenant (Produtor Rural)
        tenant = Tenant(
            nome=data.nome_produtor,
            documento=data.cnpj_tenant or "",
            ativo=True,
        )
        self.session.add(tenant)
        await self.session.flush()

        # 6. Buscar Perfil Owner do sistema
        perfil_admin = await self._get_perfil_owner_sistema()

        # 7. Vincular Usuário -> Tenant como Owner
        tu = TenantUsuario(
            tenant_id=tenant.id,
            usuario_id=user.id,
            perfil_id=perfil_admin.id,
            is_owner=True,
            status="ATIVO",
        )
        self.session.add(tu)

        # 8. Criar Assinatura com status e trial corretos
        is_trial = not plano.is_free and plano.tem_trial
        if plano.is_free:
            status_assin = "ATIVA"
            trial_expira_em = None
            primeiro_vencimento = None
        else:
            status_assin = "TRIAL" if is_trial else "ATIVA"
            trial_expira_em = agora + timedelta(days=plano.dias_trial) if is_trial else None
            primeiro_vencimento = (trial_expira_em + timedelta(days=1)).date() if trial_expira_em else None

        assinatura = AssinaturaTenant(
            tenant_id=tenant.id,
            plano_id=plano.id,
            tipo_assinatura="TENANT",
            ciclo_pagamento=data.ciclo,
            status=status_assin,
            data_inicio=agora,
            data_proxima_renovacao=trial_expira_em,
        )
        self.session.add(assinatura)
        await self.session.flush()

        # 11. Criar Fatura automática (apenas se plano pago com trial)
        if not plano.is_free and is_trial and primeiro_vencimento:
            valor_fatura = Decimal(str(plano.preco_anual)) if data.ciclo == "ANUAL" else Decimal(str(plano.preco_mensal))
            vencimento_dt = datetime.combine(primeiro_vencimento, datetime.min.time(), tzinfo=timezone.utc)
            fatura = Fatura(
                tenant_id=tenant.id,
                assinatura_id=assinatura.id,
                valor=valor_fatura,
                data_vencimento=vencimento_dt,
                status="ABERTA",
            )
            self.session.add(fatura)
            logger.info(f"Fatura criada: R${valor_fatura} vence em {primeiro_vencimento} para {tenant.nome}")

        await self.session.commit()

        # 12. Enviar email (trial ou boas-vindas)
        try:
            if not plano.is_free and is_trial:
                await email_service.send_trial_notice(
                    email=user.email,
                    nome=user.nome_completo or user.username,
                    nome_produtor=tenant.nome,
                    nome_plano=plano.nome,
                    dias_trial=plano.dias_trial,
                    data_vencimento=primeiro_vencimento,
                    tenant_id=tenant.id,
                )
            else:
                await email_service.send_welcome(
                    email=user.email,
                    nome=user.nome_completo or user.username,
                    tenant_nome=tenant.nome,
                    username=user.username,
                    tenant_id=tenant.id,
                )
        except Exception as e:
            logger.error(f"Falha ao enviar email para {user.email}: {e}")

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
            unidades_produtivas_ids=data.unidades_produtivas_ids,
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

    async def obter_detalhes_convite(self, token: str):
        stmt = select(ConviteAcesso).where(
            ConviteAcesso.token_convite == token,
            ConviteAcesso.status == "PENDENTE"
        )
        convite = (await self.session.execute(stmt)).scalar_one_or_none()

        if not convite:
            raise HTTPException(status_code=404, detail="Convite inválido ou já expirou.")

        if convite.data_expiracao < datetime.now(timezone.utc):
             convite.status = "EXPIRADO"
             await self.session.commit()
             raise HTTPException(status_code=400, detail="Convite expirado.")

        tenant = await self.session.get(Tenant, convite.tenant_id)
        perfil = await self.session.get(PerfilAcesso, convite.perfil_id)

        # Buscar unidades produtivas
        fazendas_nomes = []
        unidades_ids = getattr(convite, 'unidades_produtivas_ids', None) or []
        for f_id in unidades_ids:
            f = await self.session.get(Fazenda, uuid.UUID(f_id))
            if f:
                fazendas_nomes.append(f.nome)

        # Verificar se o email já tem conta na plataforma
        stmt_user = select(Usuario).where(Usuario.email == convite.email_convidado)
        usuario_existente = (await self.session.execute(stmt_user)).scalar_one_or_none()

        return {
            "tenant_nome": tenant.nome,
            "perfil_nome": perfil.nome,
            "email_convidado": convite.email_convidado,
            "expira_em": convite.data_expiracao,
            "fazendas": fazendas_nomes,
            "usuario_existe": usuario_existente is not None,
        }


    async def registrar_via_convite(self, token: str, senha: str, nome_completo: str | None, foto_perfil_url: str | None) -> Usuario:
        """Cria um novo usuário usando o email do convite e já aceita o convite."""
        from core.services.auth_service import hash_password

        stmt = select(ConviteAcesso).where(
            ConviteAcesso.token_convite == token,
            ConviteAcesso.status == "PENDENTE"
        )
        convite = (await self.session.execute(stmt)).scalar_one_or_none()

        if not convite:
            raise HTTPException(status_code=404, detail="Convite inválido, expirado ou já aceito.")

        if convite.data_expiracao < datetime.now(timezone.utc):
            convite.status = "EXPIRADO"
            await self.session.commit()
            raise HTTPException(status_code=400, detail="Convite expirado.")

        # Checar se email já tem conta
        stmt_user = select(Usuario).where(Usuario.email == convite.email_convidado)
        existente = (await self.session.execute(stmt_user)).scalar_one_or_none()
        if existente:
            raise HTTPException(status_code=400, detail="Este e-mail já possui conta. Faça login e aceite o convite.")

        # Gerar username único a partir do email
        base_username = convite.email_convidado.split("@")[0][:40].lower().replace(".", "_")
        username = base_username
        suffix = 1
        while (await self.session.execute(select(Usuario).where(Usuario.username == username))).scalar_one_or_none():
            username = f"{base_username}_{suffix}"
            suffix += 1

        novo_usuario = Usuario(
            email=convite.email_convidado,
            username=username,
            nome_completo=nome_completo or convite.email_convidado.split("@")[0],
            senha_hash=hash_password(senha),
            foto_perfil_url=foto_perfil_url,
            ativo=True,
        )
        self.session.add(novo_usuario)
        await self.session.flush()  # gera ID sem commit

        # Aceitar convite com o novo user_id
        await self.aceitar_convite(token, novo_usuario.id)
        return novo_usuario

    async def aceitar_convite(self, token: str, user_id: uuid.UUID):
        stmt = select(ConviteAcesso).where(
            ConviteAcesso.token_convite == token, 
            ConviteAcesso.status == "PENDENTE"
        )
        convite = (await self.session.execute(stmt)).scalar_one_or_none()
        
        if not convite:
            raise HTTPException(status_code=404, detail="Convite inválido, expirado ou já aceito.")
            
        if convite.data_expiracao < datetime.now(timezone.utc):
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
            
        # Vínculo nas Unidades Produtivas
        unidades_ids = getattr(convite, 'unidades_produtivas_ids', None) or getattr(convite, 'fazendas_ids', [])
        for fazenda_id_str in unidades_ids:
            check_fu = select(FazendaUsuario).where(
                FazendaUsuario.usuario_id == user_id,
                FazendaUsuario.unidade_produtiva_id == uuid.UUID(fazenda_id_str)
            )
            existe_fu = (await self.session.execute(check_fu)).scalar_one_or_none()
            if not existe_fu:
                fu = FazendaUsuario(
                    tenant_id=convite.tenant_id,
                    usuario_id=user_id,
                    unidade_produtiva_id=uuid.UUID(fazenda_id_str)
                )
                self.session.add(fu)

        # Trancar convite
        convite.status = "ACEITO"
        await self.session.commit()
        return {"status": "success", "message": "Bem-vindo à Fazenda!"}
