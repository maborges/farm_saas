import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.base_service import BaseService
from core.exceptions import EntityNotFoundError, BusinessRuleError
from .models import AreaRural, MatriculaImovel, RegistroAmbiental, ValorPatrimonial, Infraestrutura, ArquivoGeo, StatusProcessamentoGeo


class AreaRuralService(BaseService[AreaRural]):
    """
    Serviço para cadastro de propriedades e áreas rurais.
    Herda tenant_id enforcement do BaseService.
    """

    async def listar(
        self,
        fazenda_id: uuid.UUID | None = None,
        tipo: str | None = None,
        parent_id: uuid.UUID | None = None,
        apenas_ativos: bool = True,
    ) -> list[AreaRural]:
        stmt = select(AreaRural).where(AreaRural.tenant_id == self.tenant_id)
        if apenas_ativos:
            stmt = stmt.where(AreaRural.ativo == True)
        if fazenda_id:
            stmt = stmt.where(AreaRural.fazenda_id == fazenda_id)
        if tipo:
            stmt = stmt.where(AreaRural.tipo == tipo)
        if parent_id is not None:
            stmt = stmt.where(AreaRural.parent_id == parent_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def listar_raizes(self, fazenda_id: uuid.UUID | None = None) -> list[AreaRural]:
        """Retorna apenas áreas sem parent (raízes da hierarquia)."""
        stmt = (
            select(AreaRural)
            .where(AreaRural.tenant_id == self.tenant_id, AreaRural.parent_id == None, AreaRural.ativo == True)
        )
        if fazenda_id:
            stmt = stmt.where(AreaRural.fazenda_id == fazenda_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def obter_com_filhos(self, area_id: uuid.UUID) -> AreaRural:
        """Carrega a área com todos os filhos diretos."""
        stmt = (
            select(AreaRural)
            .where(AreaRural.id == area_id, AreaRural.tenant_id == self.tenant_id)
            .options(selectinload(AreaRural.filhos))
        )
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Área rural não encontrada")
        return obj

    async def criar_area(self, data: dict) -> AreaRural:
        area = AreaRural(tenant_id=self.tenant_id, **data)
        self.session.add(area)
        await self.session.commit()
        await self.session.refresh(area)
        return area

    async def atualizar_area(self, area_id: uuid.UUID, data: dict) -> AreaRural:
        obj = await self.get_or_fail(area_id)
        for k, v in data.items():
            setattr(obj, k, v)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def soft_delete(self, area_id: uuid.UUID) -> None:
        obj = await self.get_or_fail(area_id)
        # Verifica se há filhos ativos
        stmt = select(AreaRural).where(
            AreaRural.parent_id == area_id, AreaRural.ativo == True
        )
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            raise BusinessRuleError("Não é possível inativar uma área que possui subáreas ativas")
        obj.ativo = False
        await self.session.commit()


class MatriculaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def _verificar_area(self, area_id: uuid.UUID) -> AreaRural:
        result = await self.session.execute(
            select(AreaRural).where(AreaRural.id == area_id, AreaRural.tenant_id == self.tenant_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Área rural não encontrada")
        return obj

    async def listar(self, area_id: uuid.UUID) -> list[MatriculaImovel]:
        await self._verificar_area(area_id)
        result = await self.session.execute(
            select(MatriculaImovel).where(MatriculaImovel.area_id == area_id)
        )
        return list(result.scalars().all())

    async def criar(self, data: dict) -> MatriculaImovel:
        await self._verificar_area(data["area_id"])
        obj = MatriculaImovel(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def atualizar(self, matricula_id: uuid.UUID, area_id: uuid.UUID, data: dict) -> MatriculaImovel:
        await self._verificar_area(area_id)
        result = await self.session.execute(
            select(MatriculaImovel).where(MatriculaImovel.id == matricula_id, MatriculaImovel.area_id == area_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Matrícula não encontrada")
        for k, v in data.items():
            setattr(obj, k, v)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def remover(self, matricula_id: uuid.UUID, area_id: uuid.UUID) -> None:
        await self._verificar_area(area_id)
        result = await self.session.execute(
            select(MatriculaImovel).where(MatriculaImovel.id == matricula_id, MatriculaImovel.area_id == area_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Matrícula não encontrada")
        await self.session.delete(obj)
        await self.session.commit()


class RegistroAmbientalService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def _verificar_area(self, area_id: uuid.UUID) -> AreaRural:
        result = await self.session.execute(
            select(AreaRural).where(AreaRural.id == area_id, AreaRural.tenant_id == self.tenant_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Área rural não encontrada")
        return obj

    async def listar(self, area_id: uuid.UUID) -> list[RegistroAmbiental]:
        await self._verificar_area(area_id)
        result = await self.session.execute(
            select(RegistroAmbiental).where(RegistroAmbiental.area_id == area_id, RegistroAmbiental.ativo == True)
        )
        return list(result.scalars().all())

    async def criar(self, data: dict) -> RegistroAmbiental:
        await self._verificar_area(data["area_id"])
        obj = RegistroAmbiental(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def atualizar(self, registro_id: uuid.UUID, area_id: uuid.UUID, data: dict) -> RegistroAmbiental:
        await self._verificar_area(area_id)
        result = await self.session.execute(
            select(RegistroAmbiental).where(RegistroAmbiental.id == registro_id, RegistroAmbiental.area_id == area_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Registro ambiental não encontrado")
        for k, v in data.items():
            setattr(obj, k, v)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def remover(self, registro_id: uuid.UUID, area_id: uuid.UUID) -> None:
        await self._verificar_area(area_id)
        result = await self.session.execute(
            select(RegistroAmbiental).where(RegistroAmbiental.id == registro_id, RegistroAmbiental.area_id == area_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Registro ambiental não encontrado")
        obj.ativo = False
        await self.session.commit()


class InfraestruturaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def _verificar_area(self, area_id: uuid.UUID) -> AreaRural:
        result = await self.session.execute(
            select(AreaRural).where(AreaRural.id == area_id, AreaRural.tenant_id == self.tenant_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Área rural não encontrada")
        return obj

    async def listar(self, area_rural_id: uuid.UUID, apenas_ativos: bool = True) -> list[Infraestrutura]:
        await self._verificar_area(area_rural_id)
        stmt = select(Infraestrutura).where(Infraestrutura.area_rural_id == area_rural_id)
        if apenas_ativos:
            stmt = stmt.where(Infraestrutura.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def criar(self, data: dict) -> Infraestrutura:
        await self._verificar_area(data["area_rural_id"])
        obj = Infraestrutura(tenant_id=self.tenant_id, **data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def atualizar(self, infra_id: uuid.UUID, area_rural_id: uuid.UUID, data: dict) -> Infraestrutura:
        await self._verificar_area(area_rural_id)
        result = await self.session.execute(
            select(Infraestrutura).where(
                Infraestrutura.id == infra_id,
                Infraestrutura.area_rural_id == area_rural_id,
                Infraestrutura.tenant_id == self.tenant_id,
            )
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Infraestrutura não encontrada")
        for k, v in data.items():
            setattr(obj, k, v)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def remover(self, infra_id: uuid.UUID, area_rural_id: uuid.UUID) -> None:
        await self._verificar_area(area_rural_id)
        result = await self.session.execute(
            select(Infraestrutura).where(
                Infraestrutura.id == infra_id,
                Infraestrutura.area_rural_id == area_rural_id,
                Infraestrutura.tenant_id == self.tenant_id,
            )
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Infraestrutura não encontrada")
        obj.is_active = False
        await self.session.commit()


class ArquivoGeoService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def _verificar_area(self, area_id: uuid.UUID) -> AreaRural:
        result = await self.session.execute(
            select(AreaRural).where(AreaRural.id == area_id, AreaRural.tenant_id == self.tenant_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Área rural não encontrada")
        return obj

    async def listar(self, area_rural_id: uuid.UUID) -> list[ArquivoGeo]:
        await self._verificar_area(area_rural_id)
        result = await self.session.execute(
            select(ArquivoGeo)
            .where(ArquivoGeo.area_rural_id == area_rural_id, ArquivoGeo.tenant_id == self.tenant_id)
            .order_by(ArquivoGeo.created_at.desc())
        )
        return list(result.scalars().all())

    async def criar(self, data: dict) -> ArquivoGeo:
        obj = ArquivoGeo(tenant_id=self.tenant_id, **data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def marcar_processado(
        self, arquivo_id: uuid.UUID, poligonos: int, area_ha: float
    ) -> ArquivoGeo:
        result = await self.session.execute(
            select(ArquivoGeo).where(
                ArquivoGeo.id == arquivo_id, ArquivoGeo.tenant_id == self.tenant_id
            )
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Arquivo geo não encontrado")
        obj.status = StatusProcessamentoGeo.PROCESSADO
        obj.poligonos_extraidos = poligonos
        obj.area_ha_extraida = area_ha
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def marcar_erro(self, arquivo_id: uuid.UUID, erro: str) -> ArquivoGeo:
        result = await self.session.execute(
            select(ArquivoGeo).where(
                ArquivoGeo.id == arquivo_id, ArquivoGeo.tenant_id == self.tenant_id
            )
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Arquivo geo não encontrado")
        obj.status = StatusProcessamentoGeo.ERRO
        obj.erro_msg = erro
        await self.session.commit()
        await self.session.refresh(obj)
        return obj


class ValorPatrimonialService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def _verificar_area(self, area_id: uuid.UUID) -> AreaRural:
        result = await self.session.execute(
            select(AreaRural).where(AreaRural.id == area_id, AreaRural.tenant_id == self.tenant_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Área rural não encontrada")
        return obj

    async def listar(self, area_id: uuid.UUID) -> list[ValorPatrimonial]:
        await self._verificar_area(area_id)
        result = await self.session.execute(
            select(ValorPatrimonial)
            .where(ValorPatrimonial.area_id == area_id)
            .order_by(ValorPatrimonial.data_avaliacao.desc())
        )
        return list(result.scalars().all())

    async def criar(self, data: dict) -> ValorPatrimonial:
        await self._verificar_area(data["area_id"])
        obj = ValorPatrimonial(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def atualizar(self, valor_id: uuid.UUID, area_id: uuid.UUID, data: dict) -> ValorPatrimonial:
        await self._verificar_area(area_id)
        result = await self.session.execute(
            select(ValorPatrimonial).where(ValorPatrimonial.id == valor_id, ValorPatrimonial.area_id == area_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Avaliação patrimonial não encontrada")
        for k, v in data.items():
            setattr(obj, k, v)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def remover(self, valor_id: uuid.UUID, area_id: uuid.UUID) -> None:
        await self._verificar_area(area_id)
        result = await self.session.execute(
            select(ValorPatrimonial).where(ValorPatrimonial.id == valor_id, ValorPatrimonial.area_id == area_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise EntityNotFoundError("Avaliação patrimonial não encontrada")
        await self.session.delete(obj)
        await self.session.commit()
