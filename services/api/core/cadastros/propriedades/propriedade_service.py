"""Service para gestão de Propriedades e Explorações Rurais."""
import uuid
from datetime import date
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_service import BaseService
from core.exceptions import BusinessRuleError, EntityNotFoundError
from .propriedade_models import Propriedade, ExploracaoRural, DocumentoExploracao, NaturezaVinculo
from .propriedade_schemas import ExploracaoCreate, ExploracaoUpdate


class PropriedadeService(BaseService[Propriedade]):
    """
    Serviço para CRUD de Propriedades.
    Herda tenant_id enforcement do BaseService.
    """
    pass


class ExploracaoRuralService:
    """
    Serviço para gestão de Explorações Rurais com validações de negócio.
    
    Regras:
    1. Não permitir sobreposição de períodos (mesma propriedade + mesma fazenda)
    2. data_fim > data_inicio se data_fim informada
    3. Área explorada <= área total fazenda × 1.05 (tolerância 5%)
    """

    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def _validar_sobreposicao(
        self,
        unidade_produtiva_id: uuid.UUID,
        propriedade_id: uuid.UUID,
        data_inicio: date,
        data_fim: date | None,
        exploracao_existente_id: uuid.UUID | None = None,
    ) -> None:
        """
        Regra: não permitir duas explorações da mesma propriedade
        na mesma fazenda com períodos sobrepostos.
        
        Sobreposição ocorre quando:
        - Nova: [data_inicio, data_fim] ou [data_inicio, ∞)
        - Existente: [e.data_inicio, e.data_fim] ou [e.data_inicio, ∞)
        - Há sobreposição se: nova.data_inicio <= existente.data_fim E nova.data_fim >= existente.data_inicio
        """
        stmt = select(ExploracaoRural).where(
            and_(
                ExploracaoRural.tenant_id == self.tenant_id,
                ExploracaoRural.unidade_produtiva_id == unidade_produtiva_id,
                ExploracaoRural.propriedade_id == propriedade_id,
                ExploracaoRural.ativo == True,
            )
        )
        
        if exploracao_existente_id:
            stmt = stmt.where(ExploracaoRural.id != exploracao_existente_id)
        
        result = await self.session.execute(stmt)
        exploracoes = list(result.scalars().all())
        
        for expl in exploracoes:
            # Verificar sobreposição de períodos
            expl_data_fim = expl.data_fim or date(9999, 12, 31)  # ∞ se None
            nova_data_fim = data_fim or date(9999, 12, 31)
            
            # Há sobreposição se: nova.data_inicio <= expl.data_fim E nova.data_fim >= expl.data_inicio
            if data_inicio <= expl_data_fim and nova_data_fim >= expl.data_inicio:
                raise BusinessRuleError(
                    f"Já existe uma exploração ativa para esta propriedade na fazenda "
                    f"com período sobreposto ({expl.data_inicio} até {expl.data_fim or 'indeterminado'})."
                )

    async def _validar_data_fim(self, data_inicio: date, data_fim: date | None) -> None:
        """Regra: data_fim deve ser posterior a data_inicio."""
        if data_fim is not None and data_fim <= data_inicio:
            raise BusinessRuleError("data_fim deve ser posterior a data_inicio.")

    async def _validar_area_explorada(
        self,
        unidade_produtiva_id: uuid.UUID,
        area_explorada_ha: float | None,
    ) -> None:
        """
        Regra: área explorada <= área total fazenda × 1.05 (tolerância 5%).
        """
        if area_explorada_ha is None:
            return
        
        # Tentar obter área total da fazenda
        # Nota: ajustar conforme modelo real de Fazendas
        from fazendas.models import Fazenda  # Pode variar conforme estrutura
        
        stmt = select(Fazenda).where(
            and_(
                Fazenda.id == unidade_produtiva_id,
                Fazenda.tenant_id == self.tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        fazenda = result.scalar_one_or_none()
        
        if fazenda and hasattr(fazenda, 'area_total_ha') and fazenda.area_total_ha:
            area_maxima = fazenda.area_total_ha * 1.05
            if area_explorada_ha > area_maxima:
                raise BusinessRuleError(
                    f"Área explorada ({area_explorada_ha} ha) excede a área total da fazenda "
                    f"({fazenda.area_total_ha} ha) com tolerância de 5% (máx: {area_maxima} ha)."
                )

    async def criar(self, propriedade_id: uuid.UUID, data: ExploracaoCreate) -> ExploracaoRural:
        """
        Cria uma nova exploração rural com todas as validações.
        """
        # Validar propriedade pertence ao tenant
        stmt = select(Propriedade).where(
            and_(
                Propriedade.id == propriedade_id,
                Propriedade.tenant_id == self.tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        propriedade = result.scalar_one_or_none()
        if not propriedade:
            raise EntityNotFoundError("Propriedade não encontrada neste tenant.")
        
        # Validações
        await self._validar_data_fim(data.data_inicio, data.data_fim)
        await self._validar_sobreposicao(
            unidade_produtiva_id=data.unidade_produtiva_id,
            propriedade_id=propriedade_id,
            data_inicio=data.data_inicio,
            data_fim=data.data_fim,
        )
        if data.area_explorada_ha:
            await self._validar_area_explorada(data.unidade_produtiva_id, data.area_explorada_ha)
        
        # Criar
        exploracao = ExploracaoRural(
            tenant_id=self.tenant_id,
            propriedade_id=propriedade_id,
            unidade_produtiva_id=data.unidade_produtiva_id,
            natureza=data.natureza,
            data_inicio=data.data_inicio,
            data_fim=data.data_fim,
            numero_contrato=data.numero_contrato,
            valor_anual=data.valor_anual,
            percentual_producao=data.percentual_producao,
            area_explorada_ha=data.area_explorada_ha,
            observacoes=data.observacoes,
        )
        self.session.add(exploracao)
        await self.session.flush()
        
        return exploracao

    async def atualizar(
        self,
        exploracao_id: uuid.UUID,
        data: ExploracaoUpdate,
    ) -> ExploracaoRural:
        """
        Atualiza uma exploração rural com validações.
        """
        stmt = select(ExploracaoRural).where(
            and_(
                ExploracaoRural.id == exploracao_id,
                ExploracaoRural.tenant_id == self.tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        exploracao = result.scalar_one_or_none()
        if not exploracao:
            raise EntityNotFoundError("Exploração rural não encontrada.")
        
        # Preparar dados para validação
        data_inicio = data.data_inicio or exploracao.data_inicio
        data_fim = data.data_fim if data.data_fim is not None else exploracao.data_fim
        unidade_produtiva_id = exploracao.unidade_produtiva_id
        propriedade_id = exploracao.propriedade_id
        
        # Validações
        if data.data_inicio is not None or data.data_fim is not None:
            await self._validar_data_fim(data_inicio, data_fim)
            await self._validar_sobreposicao(
                unidade_produtiva_id=unidade_produtiva_id,
                propriedade_id=propriedade_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                exploracao_existente_id=exploracao_id,
            )
        
        if data.area_explorada_ha is not None:
            await self._validar_area_explorada(unidade_produtiva_id, data.area_explorada_ha)
        
        # Atualizar campos
        update_data = data.model_dump(exclude_none=True)
        for campo, valor in update_data.items():
            setattr(exploracao, campo, valor)
        
        await self.session.flush()
        
        return exploracao

    async def listar_por_propriedade(self, propriedade_id: uuid.UUID) -> list[ExploracaoRural]:
        """Lista todas as explorações de uma propriedade."""
        stmt = select(ExploracaoRural).where(
            and_(
                ExploracaoRural.propriedade_id == propriedade_id,
                ExploracaoRural.tenant_id == self.tenant_id,
            )
        ).order_by(ExploracaoRural.data_inicio.desc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def listar_vigentes_por_fazenda(self, unidade_produtiva_id: uuid.UUID) -> list[ExploracaoRural]:
        """
        Retorna explorações ativas agora (data_fim NULL ou >= hoje).
        """
        hoje = date.today()
        
        stmt = select(ExploracaoRural).where(
            and_(
                ExploracaoRural.unidade_produtiva_id == unidade_produtiva_id,
                ExploracaoRural.tenant_id == self.tenant_id,
                ExploracaoRural.ativo == True,
                or_(
                    ExploracaoRural.data_fim == None,
                    ExploracaoRural.data_fim >= hoje,
                ),
            )
        ).order_by(ExploracaoRural.data_inicio.desc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def obter(self, exploracao_id: uuid.UUID) -> ExploracaoRural | None:
        """Obtém uma exploração por ID."""
        stmt = select(ExploracaoRural).where(
            and_(
                ExploracaoRural.id == exploracao_id,
                ExploracaoRural.tenant_id == self.tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def remover(self, exploracao_id: uuid.UUID) -> None:
        """Remove (soft delete) uma exploração."""
        exploracao = await self.obter(exploracao_id)
        if not exploracao:
            raise EntityNotFoundError("Exploração rural não encontrada.")
        
        exploracao.ativo = False
        await self.session.flush()


class DocumentoExploracaoService(BaseService[DocumentoExploracao]):
    """
    Serviço para CRUD de Documentos de Exploração.
    Herda tenant_id enforcement do BaseService.
    """
    pass
