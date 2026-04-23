from uuid import UUID
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from sqlalchemy.orm import selectinload

from core.base_service import BaseService
from core.exceptions import BusinessRuleError
from agricola.models.templates import (
    PhaseTemplate, PhaseTemplateChecklistItem, PhaseTemplateTask,
    PhaseGateRule, OperationTemplate, OperationTemplateItem, OperationDependency
)
from agricola.checklist.models import SafraChecklistItem
from agricola.tarefas.models import SafraTarefa
from agricola.safras.models import Safra


class PhaseTemplateService(BaseService[PhaseTemplate]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(PhaseTemplate, session, tenant_id)

    async def get_with_details(self, template_id: UUID) -> PhaseTemplate:
        stmt = select(PhaseTemplate).where(
            and_(
                PhaseTemplate.id == template_id,
                or_(PhaseTemplate.tenant_id == self.tenant_id, PhaseTemplate.tenant_id == None)
            )
        ).options(
            selectinload(PhaseTemplate.checklist_items),
            selectinload(PhaseTemplate.tasks),
            selectinload(PhaseTemplate.gate_rules)
        )
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            raise BusinessRuleError("Template não encontrado ou sem permissão.")
        return obj

    async def listar(self, cultura: str | None = None, fase: str | None = None) -> List[PhaseTemplate]:
        """Lista templates do tenant + templates globais do sistema."""
        stmt = select(PhaseTemplate).where(
            or_(PhaseTemplate.tenant_id == self.tenant_id, PhaseTemplate.tenant_id == None),
            PhaseTemplate.ativo == True
        )
        if cultura:
            stmt = stmt.where(or_(PhaseTemplate.cultura == cultura, PhaseTemplate.cultura == None))
        if fase:
            stmt = stmt.where(PhaseTemplate.fase == fase)
        
        stmt = stmt.order_by(PhaseTemplate.is_system_default.desc(), PhaseTemplate.titulo)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def duplicar_global(self, global_template_id: UUID) -> PhaseTemplate:
        """Cria uma cópia de um template global para o tenant atual."""
        global_tmpl = await self.get_with_details(global_template_id)
        if global_tmpl.tenant_id is not None:
            raise BusinessRuleError("Apenas templates globais podem ser duplicados desta forma.")
        
        # Cria novo container
        new_tmpl = PhaseTemplate(
            tenant_id=self.tenant_id,
            cultura=global_tmpl.cultura,
            fase=global_tmpl.fase,
            titulo=f"{global_tmpl.titulo} (Cópia)",
            descricao=global_tmpl.descricao,
            ativo=True,
            is_system_default=False
        )
        self.session.add(new_tmpl)
        await self.session.flush()

        # Copia itens
        for item in global_tmpl.checklist_items:
            self.session.add(PhaseTemplateChecklistItem(
                phase_template_id=new_tmpl.id,
                titulo=item.titulo,
                descricao=item.descricao,
                obrigatorio=item.obrigatorio,
                ordem=item.ordem,
                ativo=item.ativo
            ))
        
        for task in global_tmpl.tasks:
            self.session.add(PhaseTemplateTask(
                phase_template_id=new_tmpl.id,
                tipo=task.tipo,
                titulo=task.titulo,
                descricao=task.descricao,
                criticidade=task.criticidade,
                ordem=task.ordem
            ))

        for rule in global_tmpl.gate_rules:
            self.session.add(PhaseGateRule(
                phase_template_id=new_tmpl.id,
                rule_type=rule.rule_type,
                config=rule.config,
                ativo=rule.ativo
            ))
            
        await self.session.flush()
        return new_tmpl


class OperationTemplateService(BaseService[OperationTemplate]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(OperationTemplate, session, tenant_id)

    async def get_with_details(self, template_id: UUID) -> OperationTemplate:
        stmt = select(OperationTemplate).where(
            and_(
                OperationTemplate.id == template_id,
                or_(OperationTemplate.tenant_id == self.tenant_id, OperationTemplate.tenant_id == None)
            )
        ).options(selectinload(OperationTemplate.items))
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            raise BusinessRuleError("Template de operações não encontrado.")
        return obj

    async def listar(self, cultura: str | None = None, fase: str | None = None) -> List[OperationTemplate]:
        stmt = select(OperationTemplate).where(
            or_(OperationTemplate.tenant_id == self.tenant_id, OperationTemplate.tenant_id == None),
            OperationTemplate.ativo == True
        )
        if cultura:
            stmt = stmt.where(or_(OperationTemplate.cultura == cultura, OperationTemplate.cultura == None))
        if fase:
            stmt = stmt.where(or_(OperationTemplate.fase == fase, OperationTemplate.fase == None))
            
        stmt = stmt.order_by(OperationTemplate.is_system_default.desc(), OperationTemplate.titulo)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class TemplateApplicationService:
    """Service especializado em instanciar templates em uma Safra."""
    
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def aplicar_fase(self, safra_id: UUID, phase_template_id: UUID) -> Dict:
        """Instancia checklist e tarefas de um template na safra."""
        # 1. Carrega Safra e Template
        safra = await self.session.get(Safra, safra_id)
        if not safra or safra.tenant_id != self.tenant_id:
            raise BusinessRuleError("Safra não encontrada.")
            
        stmt = select(PhaseTemplate).where(PhaseTemplate.id == phase_template_id).options(
            selectinload(PhaseTemplate.checklist_items),
            selectinload(PhaseTemplate.tasks)
        )
        template = (await self.session.execute(stmt)).scalar_one_or_none()
        if not template:
            raise BusinessRuleError("Template de fase não encontrado.")

        res = {"checklist_criados": 0, "tarefas_criadas": 0}

        # 2. Instancia Checklist
        for tmpl_item in template.checklist_items:
            if not tmpl_item.ativo: continue
            
            item = SafraChecklistItem(
                safra_id=safra.id,
                tenant_id=self.tenant_id,
                template_id=tmpl_item.id,
                fase=template.fase,
                titulo=tmpl_item.titulo,
                descricao=tmpl_item.descricao,
                obrigatorio=tmpl_item.obrigatorio,
                ordem=tmpl_item.ordem
            )
            self.session.add(item)
            res["checklist_criados"] += 1

        # 3. Instancia Tarefas (como origem=TEMPLATE)
        for tmpl_task in template.tasks:
            # Note: PhaseTemplateTask não gera tarefa por talhão aqui, gera tarefa de governança da safra/fase
            # Se for necessário por talhão, o usuário deve selecionar no editor de instância
            tarefa = SafraTarefa(
                tenant_id=self.tenant_id,
                safra_id=safra.id,
                origem="TEMPLATE",
                tipo=tmpl_task.tipo,
                fase=template.fase,
                criticidade=tmpl_task.criticidade,
                descricao=tmpl_task.titulo,
                obs=tmpl_task.descricao,
                status="PENDENTE_APROVACAO"
            )
            self.session.add(tarefa)
            res["tarefas_criadas"] += 1

        await self.session.flush()
        return res

    async def aplicar_operacoes(self, safra_id: UUID, operation_template_id: UUID, talhao_ids: List[UUID]) -> Dict:
        """Gera tarefas operacionais para os talhões selecionados a partir de um template."""
        safra = await self.session.get(Safra, safra_id)
        if not safra: raise BusinessRuleError("Safra não encontrada.")
        
        stmt = select(OperationTemplate).where(OperationTemplate.id == operation_template_id).options(
            selectinload(OperationTemplate.items)
        )
        template = (await self.session.execute(stmt)).scalar_one_or_none()
        if not template: raise BusinessRuleError("Template operacional não encontrado.")

        tarefas_geradas = 0
        for talhao_id in talhao_ids:
            for item in template.items:
                if not item.can_generate_task: continue
                
                tarefa = SafraTarefa(
                    tenant_id=self.tenant_id,
                    safra_id=safra.id,
                    talhao_id=talhao_id,
                    origem="TEMPLATE",
                    tipo=item.tipo,
                    fase=template.fase or safra.fase_atual,
                    descricao=item.titulo,
                    obs=item.descricao,
                    dose_estimada_kg_ha=item.dose_sugerida,
                    status="PENDENTE_APROVACAO"
                )
                self.session.add(tarefa)
                tarefas_geradas += 1
        
        await self.session.flush()
        return {"tarefas_geradas": tarefas_geradas}
