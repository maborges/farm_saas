"""
Serviço de Rate Limiting para Login

Implementa controle de tentativas de login para prevenção de brute-force attacks:
- Configuração por tenant (ativa/desativa, tentativas, tempo de bloqueio)
- Bloqueio automático após exceder tentativas
- Desbloqueio automático após tempo configurado
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from typing import Optional
from loguru import logger
import uuid
from core.models.auth import TentativaLogin

# Constantes padrão (usadas quando não há config do tenant ou para backoffice)
DEFAULT_MAX_TENTATIVAS = 5
DEFAULT_JANELA_TEMPO_MINUTOS = 15
DEFAULT_TEMPO_BLOQUEIO_MINUTOS = 15


class LoginRateLimitService:
    """
    Serviço para gerenciar rate limiting de tentativas de login.

    Aceita configuração por tenant via dict seguranca_config:
    - rate_limiting_ativo: bool (default True)
    - max_tentativas: int (default 5)
    - tempo_bloqueio_minutos: int (default 15)
    - janela_tempo_minutos: int (default 15) - janela para contar tentativas
    """

    def __init__(
        self,
        session: AsyncSession,
        seguranca_config: Optional[dict] = None,
    ):
        self.session = session
        self.config = seguranca_config or {}
        self.rate_limiting_ativo = self.config.get("rate_limiting_ativo", True)
        self.max_tentativas = self.config.get("max_tentativas", DEFAULT_MAX_TENTATIVAS)
        self.janela_tempo_minutos = self.config.get("janela_tempo_minutos", DEFAULT_JANELA_TEMPO_MINUTOS)
        self.tempo_bloqueio_minutos = self.config.get("tempo_bloqueio_minutos", DEFAULT_TEMPO_BLOQUEIO_MINUTOS)
    
    async def verificar_bloqueio(self, email: str) -> tuple[bool, Optional[datetime]]:
        """
        Verifica se o e-mail está bloqueado para login.

        Returns:
            tuple[bool, Optional[datetime]]: (está_bloqueado, data_desbloqueio)
        """
        # Se rate limiting está desativado, nunca bloqueia
        if not self.rate_limiting_ativo:
            return False, None

        # Busca registro de tentativas para este e-mail
        stmt = select(TentativaLogin).where(
            TentativaLogin.email == email.lower()
        ).order_by(TentativaLogin.created_at.desc()).limit(1)

        result = await self.session.execute(stmt)
        tentativa = result.scalar_one_or_none()

        if not tentativa:
            return False, None

        # Verifica se está bloqueado
        if tentativa.bloqueado:
            # Verifica se já passou o tempo de bloqueio
            if tentativa.data_desbloqueio:
                if datetime.now(timezone.utc) >= tentativa.data_desbloqueio:
                    # Desbloqueia automaticamente
                    tentativa.bloqueado = False
                    tentativa.data_bloqueio = None
                    tentativa.data_desbloqueio = None
                    tentativa.tentativas_count = 0
                    await self.session.commit()
                    logger.info(f"Desbloqueio automático para {email}")
                    return False, None
                else:
                    # Ainda está bloqueado
                    logger.warning(f"Login bloqueado para {email} até {tentativa.data_desbloqueio}")
                    return True, tentativa.data_desbloqueio
            else:
                # Bloqueado sem data de desbloqueio (deveria ter)
                return True, None

        # Verifica se as tentativas estão dentro da janela de tempo
        janela_inicio = datetime.now(timezone.utc) - timedelta(minutes=self.janela_tempo_minutos)

        if tentativa.created_at < janela_inicio:
            # Tentativas expiradas, reseta contador
            tentativa.tentativas_count = 0
            await self.session.commit()
            return False, None

        # Verifica se atingiu o limite
        if tentativa.tentativas_count >= self.max_tentativas:
            return True, tentativa.data_desbloqueio

        return False, None
    
    async def registrar_tentativa_falha(
        self,
        email: str,
        motivo: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> tuple[bool, Optional[datetime]]:
        """
        Registra uma tentativa de login falha.

        Returns:
            tuple[bool, Optional[datetime]]: (foi_bloqueado, data_desbloqueio)
        """
        email_lower = email.lower()
        logger.warning(f"Registrando tentativa falha para {email_lower}, motivo: {motivo}")

        # Se rate limiting está desativado, só registra sem bloquear
        if not self.rate_limiting_ativo:
            stmt = select(TentativaLogin).where(
                TentativaLogin.email == email_lower
            ).order_by(TentativaLogin.created_at.desc()).limit(1)
            result = await self.session.execute(stmt)
            tentativa = result.scalar_one_or_none()

            if tentativa:
                tentativa.tentativas_count += 1
                tentativa.updated_at = datetime.now(timezone.utc)
                tentativa.motivo_falha = motivo
                tentativa.ip_address = ip_address or tentativa.ip_address
                tentativa.user_agent = user_agent or tentativa.user_agent
                await self.session.commit()
            else:
                tentativa = TentativaLogin(
                    email=email_lower,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    sucesso=False,
                    motivo_falha=motivo,
                    tentativas_count=1,
                    bloqueado=False
                )
                self.session.add(tentativa)
                await self.session.commit()
            return False, None

        # Busca registro existente
        stmt = select(TentativaLogin).where(
            TentativaLogin.email == email_lower
        ).order_by(TentativaLogin.created_at.desc()).limit(1)

        result = await self.session.execute(stmt)
        tentativa = result.scalar_one_or_none()

        logger.warning(f"Tentativa existente: {tentativa}")

        janela_inicio = datetime.now(timezone.utc) - timedelta(minutes=self.janela_tempo_minutos)

        if tentativa and tentativa.created_at >= janela_inicio and not tentativa.bloqueado:
            # Atualiza registro existente
            tentativa.tentativas_count += 1
            tentativa.updated_at = datetime.now(timezone.utc)
            tentativa.motivo_falha = motivo
            tentativa.ip_address = ip_address or tentativa.ip_address
            tentativa.user_agent = user_agent or tentativa.user_agent
            logger.warning(f"Atualizando tentativa, count={tentativa.tentativas_count}")

            # Verifica se deve bloquear
            if tentativa.tentativas_count >= self.max_tentativas:
                tentativa.bloqueado = True
                tentativa.data_bloqueio = datetime.now(timezone.utc)
                tentativa.data_desbloqueio = datetime.now(timezone.utc) + timedelta(minutes=self.tempo_bloqueio_minutos)
                logger.warning(f"Bloqueio automático para {email} após {tentativa.tentativas_count} tentativas")
                await self.session.commit()
                return True, tentativa.data_desbloqueio
            await self.session.commit()
        else:
            # Cria novo registro
            logger.warning(f"Criando novo registro de tentativa")
            tentativa = TentativaLogin(
                email=email_lower,
                ip_address=ip_address,
                user_agent=user_agent,
                sucesso=False,
                motivo_falha=motivo,
                tentativas_count=1,
                bloqueado=False
            )
            self.session.add(tentativa)
            await self.session.commit()
            logger.warning(f"Registro criado, id={tentativa.id}")

        return False, None
    
    async def registrar_tentativa_sucesso(self, email: str):
        """
        Registra uma tentativa de login bem-sucedida.
        Reseta o contador de tentativas falhas.
        """
        email_lower = email.lower()
        
        # Busca registro existente
        stmt = select(TentativaLogin).where(
            TentativaLogin.email == email_lower
        ).limit(1)
        
        result = await self.session.execute(stmt)
        tentativa = result.scalar_one_or_none()
        
        if tentativa:
            # Atualiza para sucesso e reseta contador
            tentativa.sucesso = True
            tentativa.tentativas_count = 0
            tentativa.bloqueado = False
            tentativa.data_bloqueio = None
            tentativa.data_desbloqueio = None
            tentativa.motivo_falha = None
            tentativa.updated_at = datetime.now(timezone.utc)
            await self.session.commit()
            logger.info(f"Login bem-sucedido para {email}, contador resetado")
    
    async def get_tentativas_restantes(self, email: str) -> int:
        """
        Retorna quantas tentativas de login ainda estão disponíveis.
        """
        bloqueado, _ = await self.verificar_bloqueio(email)

        if bloqueado:
            return 0

        stmt = select(TentativaLogin).where(
            TentativaLogin.email == email.lower()
        ).order_by(TentativaLogin.created_at.desc()).limit(1)

        result = await self.session.execute(stmt)
        tentativa = result.scalar_one_or_none()

        if not tentativa:
            return self.max_tentativas

        janela_inicio = datetime.now(timezone.utc) - timedelta(minutes=self.janela_tempo_minutos)

        if tentativa.created_at < janela_inicio:
            return self.max_tentativas

        return max(0, self.max_tentativas - tentativa.tentativas_count)
    
    async def desbloquear_manual(self, email: str):
        """
        Desbloqueio manual (usado por admin/backoffice).
        """
        email_lower = email.lower()
        
        stmt = select(TentativaLogin).where(
            TentativaLogin.email == email_lower
        ).limit(1)
        
        result = await self.session.execute(stmt)
        tentativa = result.scalar_one_or_none()
        
        if tentativa:
            tentativa.bloqueado = False
            tentativa.data_bloqueio = None
            tentativa.data_desbloqueio = None
            tentativa.tentativas_count = 0
            await self.session.commit()
            logger.info(f"Desbloqueio manual para {email}")
            return True
        return False
    
    async def desbloquear_por_usuario_id(self, usuario_id: uuid.UUID):
        """
        Desbloqueio por ID do usuário (usado por gestor do tenant).
        Busca o email do usuário e desbloqueia.
        
        Returns:
            bool: True se desbloqueou, False se usuário não encontrado
        """
        from core.models.auth import Usuario
        
        stmt_user = select(Usuario).where(Usuario.id == usuario_id)
        result = await self.session.execute(stmt_user)
        usuario = result.scalar_one_or_none()
        
        if not usuario:
            return False
        
        return await self.desbloquear_manual(usuario.email)
    
    async def get_tentativas_por_email(self, email: str) -> Optional[dict]:
        """
        Retorna informações sobre tentativas de login de um email.
        """
        email_lower = email.lower()
        
        stmt = select(TentativaLogin).where(
            TentativaLogin.email == email_lower
        ).order_by(TentativaLogin.created_at.desc()).limit(1)
        
        result = await self.session.execute(stmt)
        tentativa = result.scalar_one_or_none()
        
        if not tentativa:
            return None
        
        return {
            "email": tentativa.email,
            "tentativas_count": tentativa.tentativas_count,
            "bloqueado": tentativa.bloqueado,
            "data_bloqueio": tentativa.data_bloqueio.isoformat() if tentativa.data_bloqueio else None,
            "data_desbloqueio": tentativa.data_desbloqueio.isoformat() if tentativa.data_desbloqueio else None,
            "ultima_tentativa": tentativa.created_at.isoformat() if tentativa.created_at else None,
            "motivo_falha": tentativa.motivo_falha
        }
    
    async def listar_bloqueados_recentes(self, limit: int = 50) -> list[dict]:
        """
        Lista usuários bloqueados nas últimas 24 horas.
        Útil para backoffice monitorar bloqueios.
        """
        from sqlalchemy import and_
        
        janela_inicio = datetime.now(timezone.utc) - timedelta(hours=24)
        
        stmt = select(TentativaLogin).where(
            and_(
                TentativaLogin.bloqueado == True,
                TentativaLogin.created_at >= janela_inicio
            )
        ).order_by(TentativaLogin.created_at.desc()).limit(limit)
        
        result = await self.session.execute(stmt)
        tentativas = result.scalars().all()
        
        return [
            {
                "email": t.email,
                "tentativas_count": t.tentativas_count,
                "data_bloqueio": t.data_bloqueio.isoformat() if t.data_bloqueio else None,
                "data_desbloqueio": t.data_desbloqueio.isoformat() if t.data_desbloqueio else None,
                "motivo_falha": t.motivo_falha
            }
            for t in tentativas
        ]
