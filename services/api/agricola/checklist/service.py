from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from core.base_service import BaseService
from core.exceptions import BusinessRuleError
from agricola.checklist.models import ChecklistTemplate, SafraChecklistItem
from agricola.checklist.schemas import (
    ChecklistTemplateCreate, ChecklistTemplateUpdate,
    ChecklistItemAdicionar, ChecklistFaseStatus,
)


class ChecklistTemplateService(BaseService[ChecklistTemplate]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(ChecklistTemplate, session, tenant_id)

    async def listar(self, cultura: str | None = None, fase: str | None = None) -> list[ChecklistTemplate]:
        filters: dict = {"ativo": True}
        if cultura:
            filters["cultura"] = cultura
        if fase:
            filters["fase"] = fase
        return await self.list_all(**filters)

    async def criar(self, dados: ChecklistTemplateCreate) -> ChecklistTemplate:
        d = dados.model_dump()
        d["is_system"] = False
        return await self.create(d)

    async def atualizar(self, template_id: UUID, dados: ChecklistTemplateUpdate) -> ChecklistTemplate:
        return await self.update(template_id, dados.model_dump(exclude_unset=True))


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
        stmt_tmpl = select(ChecklistTemplate).where(
            ChecklistTemplate.tenant_id == self.tenant_id,
            ChecklistTemplate.fase == fase,
            ChecklistTemplate.ativo == True,
            (ChecklistTemplate.cultura == cultura) | (ChecklistTemplate.cultura == None),
        ).order_by(ChecklistTemplate.ordem)
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
        obrigatorios_pendentes = sum(1 for i in itens if i.obrigatorio and not i.concluido)
        return ChecklistFaseStatus(
            fase=fase,
            total=total,
            concluidos=concluidos,
            obrigatorios_pendentes=obrigatorios_pendentes,
            pode_avancar=obrigatorios_pendentes == 0,
            itens=itens,
        )

    async def marcar_item(self, item_id: UUID, concluido: bool, usuario_id: UUID | None) -> SafraChecklistItem:
        item = await self.get_or_fail(item_id)
        item.concluido = concluido
        item.usuario_id = usuario_id if concluido else None
        item.concluido_em = datetime.utcnow() if concluido else None
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
