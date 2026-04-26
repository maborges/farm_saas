from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from core.base_service import BaseService
from core.exceptions import BusinessRuleError
from agricola.checklist.models import SafraChecklistItem
from agricola.models.templates import PhaseTemplate, PhaseTemplateChecklistItem
from agricola.checklist.schemas import (
    ChecklistTemplateCreate, ChecklistTemplateUpdate,
    ChecklistItemAdicionar, ChecklistFaseStatus,
)


class ChecklistTemplateService(BaseService[PhaseTemplateChecklistItem]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(PhaseTemplateChecklistItem, session, tenant_id)

    async def listar(self, cultura: str | None = None, fase: str | None = None):
        stmt = select(
            PhaseTemplateChecklistItem.id,
            PhaseTemplate.tenant_id,
            PhaseTemplate.cultura,
            PhaseTemplate.fase,
            PhaseTemplateChecklistItem.titulo,
            PhaseTemplateChecklistItem.descricao,
            PhaseTemplateChecklistItem.obrigatorio,
            PhaseTemplateChecklistItem.ordem,
            PhaseTemplateChecklistItem.ativo,
            PhaseTemplate.is_system_default.label("is_system"),
            PhaseTemplate.created_at
        ).join(PhaseTemplate).where(
            or_(PhaseTemplate.tenant_id == self.tenant_id, PhaseTemplate.tenant_id == None),
            PhaseTemplateChecklistItem.ativo == True
        )
        if cultura:
            stmt = stmt.where(or_(PhaseTemplate.cultura == cultura, PhaseTemplate.cultura == None))
        if fase:
            stmt = stmt.where(PhaseTemplate.fase == fase)
        
        result = await self.session.execute(stmt.order_by(PhaseTemplate.fase, PhaseTemplateChecklistItem.ordem))
        return [dict(r._mapping) for r in result.all()]

    async def criar(self, dados: ChecklistTemplateCreate) -> PhaseTemplateChecklistItem:
        # Nota: A criação direta aqui ficou mais complexa pois precisa de um PhaseTemplate container.
        # Por simplicidade, vamos buscar ou criar um PhaseTemplate para o tenant/cultura/fase.
        stmt = select(PhaseTemplate).where(
            PhaseTemplate.tenant_id == self.tenant_id,
            PhaseTemplate.cultura == dados.cultura,
            PhaseTemplate.fase == dados.fase
        )
        container = (await self.session.execute(stmt)).scalar_one_or_none()
        
        if not container:
            container = PhaseTemplate(
                tenant_id=self.tenant_id,
                cultura=dados.cultura,
                fase=dados.fase,
                titulo=f"Template {dados.fase}" + (f" - {dados.cultura}" if dados.cultura else ""),
                ativo=True
            )
            self.session.add(container)
            await self.session.flush()

        item = PhaseTemplateChecklistItem(
            phase_template_id=container.id,
            titulo=dados.titulo,
            descricao=dados.descricao,
            obrigatorio=dados.obrigatorio,
            ordem=dados.ordem,
            ativo=True
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def atualizar(self, item_id: UUID, dados: ChecklistTemplateUpdate) -> PhaseTemplateChecklistItem:
        return await self.update(item_id, dados.model_dump(exclude_unset=True))


class SafraChecklistService(BaseService[SafraChecklistItem]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(SafraChecklistItem, session, tenant_id)

    async def gerar_para_fase(self, safra_id: UUID, cultura: str, fase: str) -> list[SafraChecklistItem]:
        """Copia os templates ativos da cultura+fase para a safra (idempotente)."""
        # Verifica se já foram gerados
        stmt_existentes = select(SafraChecklistItem).where(
            SafraChecklistItem.safra_id == safra_id,
            SafraChecklistItem.tenant_id == self.tenant_id,
            SafraChecklistItem.fase == fase,
        )
        existentes = (await self.session.execute(stmt_existentes)).scalars().all()
        if existentes:
            return list(existentes)

        # Busca templates: específicos da cultura + genéricos (cultura=None)
        stmt_tmpl = select(PhaseTemplateChecklistItem).join(PhaseTemplate).where(
            or_(PhaseTemplate.tenant_id == self.tenant_id, PhaseTemplate.tenant_id == None),
            PhaseTemplate.fase == fase,
            PhaseTemplate.ativo == True,
            PhaseTemplateChecklistItem.ativo == True,
            or_(PhaseTemplate.cultura == cultura, PhaseTemplate.cultura == None),
        ).order_by(PhaseTemplateChecklistItem.ordem)
        templates = (await self.session.execute(stmt_tmpl)).scalars().all()

        itens: list[SafraChecklistItem] = []
        for tmpl in templates:
            item = SafraChecklistItem(
                safra_id=safra_id,
                tenant_id=self.tenant_id,
                template_id=tmpl.id,
                fase=fase,
                titulo=tmpl.titulo,
                descricao=tmpl.descricao,
                obrigatorio=tmpl.obrigatorio,
                ordem=tmpl.ordem,
            )
            self.session.add(item)
            itens.append(item)

        await self.session.flush()
        return itens

    async def listar_por_fase(self, safra_id: UUID, fase: str) -> list[SafraChecklistItem]:
        stmt = select(SafraChecklistItem).where(
            SafraChecklistItem.safra_id == safra_id,
            SafraChecklistItem.tenant_id == self.tenant_id,
            SafraChecklistItem.fase == fase,
        ).order_by(SafraChecklistItem.ordem)
        return list((await self.session.execute(stmt)).scalars().all())

    async def status_fase(self, safra_id: UUID, fase: str) -> ChecklistFaseStatus:
        itens = await self.listar_por_fase(safra_id, fase)
        total = len(itens)
        concluidos = sum(1 for i in itens if i.concluido)
        # Itens cancelados não são considerados pendentes (unblock phase)
        obrigatorios_pendentes = sum(1 for i in itens if i.obrigatorio and not i.concluido and not i.cancelado)
        return ChecklistFaseStatus(
            fase=fase,
            total=total,
            concluidos=concluidos,
            obrigatorios_pendentes=obrigatorios_pendentes,
            pode_avancar=obrigatorios_pendentes == 0,
            itens=itens,
        )

    async def marcar_item(self, item_id: UUID, concluido: bool | None, cancelado: bool | None, motivo: str | None, usuario_id: UUID | None) -> SafraChecklistItem:
        item = await self.get_or_fail(item_id)
        
        if concluido is not None:
            item.concluido = concluido
            item.usuario_id = usuario_id if concluido else None
            item.concluido_em = datetime.utcnow() if concluido else None
            if concluido:
                item.cancelado = False # Não pode ser ambos
        
        if cancelado is not None:
            item.cancelado = cancelado
            item.usuario_cancelamento_id = usuario_id if cancelado else None
            item.cancelado_em = datetime.utcnow() if cancelado else None
            item.motivo_cancelamento = motivo if cancelado else None
            if cancelado:
                item.concluido = False # Não pode ser ambos

        await self.session.flush()
        return item

    async def adicionar_item(self, safra_id: UUID, fase: str, dados: ChecklistItemAdicionar) -> SafraChecklistItem:
        item = SafraChecklistItem(
            safra_id=safra_id,
            tenant_id=self.tenant_id,
            fase=fase,
            **dados.model_dump(),
        )
        self.session.add(item)
        await self.session.flush()
        return item
