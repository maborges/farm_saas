import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.exceptions import EntityNotFoundError, BusinessRuleError
from agricola.tarefas.models import SafraTarefa
from agricola.tarefas.schemas import TarefaCreate, TarefaUpdate

TRANSICOES = {
    "PENDENTE_APROVACAO": ["APROVADA", "CANCELADA"],
    "APROVADA":           ["EM_EXECUCAO", "CANCELADA"],
    "EM_EXECUCAO":        ["CONCLUIDA", "CANCELADA"],
    "CONCLUIDA":          [],
    "CANCELADA":          [],
}


class TarefaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def _get(self, tarefa_id: uuid.UUID) -> SafraTarefa:
        stmt = select(SafraTarefa).where(
            SafraTarefa.id == tarefa_id,
            SafraTarefa.tenant_id == self.tenant_id,
        )
        t = (await self.session.execute(stmt)).scalars().first()
        if not t:
            raise EntityNotFoundError(f"Tarefa {tarefa_id} não encontrada.")
        return t

    async def listar(self, safra_id: uuid.UUID, status: str | None = None, talhao_id: uuid.UUID | None = None) -> list[SafraTarefa]:
        stmt = select(SafraTarefa).where(
            SafraTarefa.tenant_id == self.tenant_id,
            SafraTarefa.safra_id == safra_id,
        ).order_by(SafraTarefa.created_at.desc())
        if status:
            stmt = stmt.where(SafraTarefa.status == status)
        if talhao_id:
            stmt = stmt.where(SafraTarefa.talhao_id == talhao_id)
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar(self, safra_id: uuid.UUID, dados: TarefaCreate, user_id: uuid.UUID | None = None) -> SafraTarefa:
        # Tarefas manuais nascem APROVADAS; automáticas (SOLO/TEMPLATE) nascem PENDENTE_APROVACAO
        status_inicial = "APROVADA" if dados.origem == "MANUAL" else "PENDENTE_APROVACAO"
        tarefa = SafraTarefa(
            tenant_id=self.tenant_id,
            safra_id=safra_id,
            talhao_id=dados.talhao_id,
            production_unit_id=dados.production_unit_id,
            cultivo_area_id=dados.cultivo_area_id,
            analise_solo_id=dados.analise_solo_id,
            origem=dados.origem,
            tipo=dados.tipo,
            fase=dados.fase,
            criticidade=dados.criticidade,
            descricao=dados.descricao,
            obs=dados.obs,
            prioridade=dados.prioridade,
            status=status_inicial,
            dose_estimada_kg_ha=dados.dose_estimada_kg_ha,
            quantidade_total_estimada_kg=dados.quantidade_total_estimada_kg,
            area_ha=dados.area_ha,
            custo_estimado=dados.custo_estimado,
            data_prevista=dados.data_prevista,
            created_by=user_id,
        )
        self.session.add(tarefa)
        await self.session.flush()
        return tarefa

    async def atualizar(self, tarefa_id: uuid.UUID, dados: TarefaUpdate) -> SafraTarefa:
        tarefa = await self._get(tarefa_id)
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(tarefa, campo, valor)
        tarefa.updated_at = datetime.utcnow()
        await self.session.flush()
        return tarefa

    async def aprovar(self, tarefa_id: uuid.UUID, aprovador_id: uuid.UUID) -> SafraTarefa:
        tarefa = await self._get(tarefa_id)
        if "APROVADA" not in TRANSICOES.get(tarefa.status, []):
            raise BusinessRuleError(f"Tarefa com status '{tarefa.status}' não pode ser aprovada.")
        tarefa.status = "APROVADA"
        tarefa.aprovado_por = aprovador_id
        tarefa.aprovado_em = datetime.utcnow()
        tarefa.updated_at = datetime.utcnow()
        await self.session.flush()
        return tarefa

    async def rejeitar(self, tarefa_id: uuid.UUID, motivo: str | None = None, user_id: uuid.UUID | None = None) -> SafraTarefa:
        tarefa = await self._get(tarefa_id)
        if "CANCELADA" not in TRANSICOES.get(tarefa.status, []):
            raise BusinessRuleError(f"Tarefa com status '{tarefa.status}' não pode ser cancelada.")
        tarefa.status = "CANCELADA"
        tarefa.motivo_cancelamento = motivo
        tarefa.cancelado_por = user_id
        tarefa.cancelado_em = datetime.utcnow()
        tarefa.updated_at = datetime.utcnow()
        await self.session.flush()
        return tarefa

    async def iniciar(self, tarefa_id: uuid.UUID) -> SafraTarefa:
        tarefa = await self._get(tarefa_id)
        if "EM_EXECUCAO" not in TRANSICOES.get(tarefa.status, []):
            raise BusinessRuleError(f"Tarefa com status '{tarefa.status}' não pode ser iniciada.")
        tarefa.status = "EM_EXECUCAO"
        tarefa.updated_at = datetime.utcnow()
        await self.session.flush()
        return tarefa

    async def concluir(self, tarefa_id: uuid.UUID) -> SafraTarefa:
        tarefa = await self._get(tarefa_id)
        if "CONCLUIDA" not in TRANSICOES.get(tarefa.status, []):
            raise BusinessRuleError(f"Tarefa com status '{tarefa.status}' não pode ser concluída.")
        tarefa.status = "CONCLUIDA"
        tarefa.concluida_em = datetime.utcnow()
        tarefa.updated_at = datetime.utcnow()
        await self.session.flush()
        return tarefa

    async def concluir_via_operacao(self, tarefa_id: uuid.UUID, operacao_id: uuid.UUID) -> SafraTarefa:
        tarefa = await self._get(tarefa_id)
        tarefa.status = "CONCLUIDA"
        tarefa.operacao_id = operacao_id
        tarefa.concluida_em = datetime.utcnow()
        tarefa.updated_at = datetime.utcnow()
        await self.session.flush()
        return tarefa

    async def get(self, tarefa_id: uuid.UUID) -> SafraTarefa:
        return await self._get(tarefa_id)
