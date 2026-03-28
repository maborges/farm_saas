"""
Serviço de alertas agrícolas.
Verifica condições críticas nas safras e dispara notificações via NotificacaoService.

Condições verificadas:
1. Checklist obrigatório pendente na fase atual
2. Safra parada na mesma fase há N dias sem operações registradas
3. Safra em DESENVOLVIMENTO sem registro fenológico recente (> 14 dias)
"""
from uuid import UUID
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_

from agricola.safras.models import Safra
from agricola.checklist.models import SafraChecklistItem
from agricola.safras.models import SafraFaseHistorico
from agricola.fenologia.models import SafraFenologiaRegistro
from notificacoes.service import NotificacaoService
from notificacoes.schemas import NotificacaoCreate

DIAS_FASE_PARADA = 10       # alerta se safra ficou X dias na mesma fase sem avançar
DIAS_FENOLOGIA_VENCIDA = 14  # alerta se não há registro fenológico há X dias em DESENVOLVIMENTO


class AlertasAgricolasService:
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id
        self.notif_svc = NotificacaoService(session, tenant_id)

    async def verificar_todas(self, fazenda_ids: list[UUID] | None = None) -> int:
        """Verifica todas as condições de alerta e dispara notificações. Retorna total de alertas gerados."""
        total = 0
        total += await self._verificar_checklist_pendente()
        total += await self._verificar_fase_parada()
        total += await self._verificar_fenologia_vencida()
        return total

    async def _safras_ativas(self) -> list[Safra]:
        stmt = select(Safra).where(
            Safra.tenant_id == self.tenant_id,
            Safra.status.notin_(["ENCERRADA", "CANCELADA"]),
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def _verificar_checklist_pendente(self) -> int:
        """Alerta quando há itens obrigatórios não concluídos na fase atual."""
        safras = await self._safras_ativas()
        total = 0
        for safra in safras:
            stmt = select(func.count(SafraChecklistItem.id)).where(
                SafraChecklistItem.safra_id == safra.id,
                SafraChecklistItem.tenant_id == self.tenant_id,
                SafraChecklistItem.fase == safra.status,
                SafraChecklistItem.obrigatorio == True,
                SafraChecklistItem.concluido == False,
            )
            pendentes = (await self.session.execute(stmt)).scalar() or 0
            if pendentes > 0:
                await self.notif_svc.criar_e_push(NotificacaoCreate(
                    tipo="ALERTA_AGRICOLA",
                    titulo="Checklist obrigatório pendente",
                    mensagem=(
                        f"Safra {safra.cultura} {safra.ano_safra} possui {pendentes} "
                        f"atividade(s) obrigatória(s) pendente(s) na fase {safra.status}."
                    ),
                ))
                total += 1
        return total

    async def _verificar_fase_parada(self) -> int:
        """Alerta quando uma safra está na mesma fase há mais de DIAS_FASE_PARADA dias."""
        safras = await self._safras_ativas()
        total = 0
        limite = date.today() - timedelta(days=DIAS_FASE_PARADA)
        for safra in safras:
            # Busca a última transição de fase
            stmt = select(SafraFaseHistorico).where(
                SafraFaseHistorico.safra_id == safra.id,
                SafraFaseHistorico.tenant_id == self.tenant_id,
            ).order_by(SafraFaseHistorico.created_at.desc()).limit(1)
            ultimo = (await self.session.execute(stmt)).scalars().first()
            if ultimo and ultimo.created_at.date() < limite:
                dias = (date.today() - ultimo.created_at.date()).days
                await self.notif_svc.criar_e_push(NotificacaoCreate(
                    tipo="ALERTA_AGRICOLA",
                    titulo="Safra parada na mesma fase",
                    mensagem=(
                        f"Safra {safra.cultura} {safra.ano_safra} está na fase "
                        f"{safra.status} há {dias} dias sem avançar."
                    ),
                ))
                total += 1
        return total

    async def _verificar_fenologia_vencida(self) -> int:
        """Alerta quando não há registro fenológico recente em safras em DESENVOLVIMENTO."""
        stmt = select(Safra).where(
            Safra.tenant_id == self.tenant_id,
            Safra.status == "DESENVOLVIMENTO",
        )
        safras = list((await self.session.execute(stmt)).scalars().all())
        total = 0
        limite = date.today() - timedelta(days=DIAS_FENOLOGIA_VENCIDA)
        for safra in safras:
            stmt_fen = select(func.max(SafraFenologiaRegistro.data_observacao)).where(
                SafraFenologiaRegistro.safra_id == safra.id,
                SafraFenologiaRegistro.tenant_id == self.tenant_id,
            )
            ultimo = (await self.session.execute(stmt_fen)).scalar()
            if not ultimo or ultimo < limite:
                dias = (date.today() - ultimo).days if ultimo else "?"
                await self.notif_svc.criar_e_push(NotificacaoCreate(
                    tipo="ALERTA_AGRICOLA",
                    titulo="Sem registro fenológico recente",
                    mensagem=(
                        f"Safra {safra.cultura} {safra.ano_safra} está em DESENVOLVIMENTO "
                        f"sem registro fenológico há {dias} dias."
                    ),
                ))
                total += 1
        return total
