from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.base_service import BaseService
from core.exceptions import BusinessRuleError
from agricola.fenologia.models import FenologiaEscala, SafraFenologiaRegistro, SafraTalhaoGrupoItem
from agricola.fenologia.schemas import (
    FenologiaEscalaCreate, FenologiaEscalaUpdate,
    FenologiaRegistroCreate, FenologiaRegistroResponse,
)


class FenologiaEscalaService(BaseService[FenologiaEscala]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(FenologiaEscala, session, tenant_id)

    async def listar(self, cultura: str | None = None) -> list[FenologiaEscala]:
        filters: dict = {"ativo": True}
        if cultura:
            filters["cultura"] = cultura
        return await self.list_all(**filters)

    async def criar(self, dados: FenologiaEscalaCreate) -> FenologiaEscala:
        d = dados.model_dump()
        d["is_system"] = False
        return await self.create(d)

    async def atualizar(self, escala_id: UUID, dados: FenologiaEscalaUpdate) -> FenologiaEscala:
        return await self.update(escala_id, dados.model_dump(exclude_unset=True))


class FenologiaRegistroService(BaseService[SafraFenologiaRegistro]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(SafraFenologiaRegistro, session, tenant_id)

    async def _validar_escala(self, escala_id: UUID) -> FenologiaEscala:
        stmt = select(FenologiaEscala).where(
            FenologiaEscala.id == escala_id,
            FenologiaEscala.tenant_id == self.tenant_id,
            FenologiaEscala.ativo == True,
        )
        escala = (await self.session.execute(stmt)).scalars().first()
        if not escala:
            raise BusinessRuleError("Estágio fenológico não encontrado.")
        return escala

    async def registrar_por_talhao(
        self,
        safra_id: UUID,
        talhao_id: UUID,
        dados: FenologiaRegistroCreate,
        usuario_id: UUID | None,
        grupo_id: UUID | None = None,
    ) -> SafraFenologiaRegistro:
        await self._validar_escala(dados.escala_id)
        registro = SafraFenologiaRegistro(
            safra_id=safra_id,
            talhao_id=talhao_id,
            tenant_id=self.tenant_id,
            escala_id=dados.escala_id,
            grupo_id=grupo_id,
            data_observacao=dados.data_observacao,
            usuario_id=usuario_id,
            observacao=dados.observacao,
            dados_extras=dados.dados_extras,
        )
        self.session.add(registro)
        await self.session.flush()
        await self.session.refresh(registro)
        return registro

    async def registrar_por_grupo(
        self,
        safra_id: UUID,
        grupo_id: UUID,
        dados: FenologiaRegistroCreate,
        usuario_id: UUID | None,
    ) -> list[SafraFenologiaRegistro]:
        """Registra o mesmo estágio para todos os talhões do grupo."""
        await self._validar_escala(dados.escala_id)

        stmt = select(SafraTalhaoGrupoItem).where(SafraTalhaoGrupoItem.tenant_id == grupo_id)
        itens = (await self.session.execute(stmt)).scalars().all()
        if not itens:
            raise BusinessRuleError("Grupo sem talhões cadastrados.")

        registros: list[SafraFenologiaRegistro] = []
        for item in itens:
            r = await self.registrar_por_talhao(
                safra_id, item.talhao_id, dados, usuario_id, grupo_id
            )
            registros.append(r)
        return registros

    async def listar_por_talhao(self, safra_id: UUID, talhao_id: UUID) -> list[SafraFenologiaRegistro]:
        stmt = (
            select(SafraFenologiaRegistro)
            .where(
                SafraFenologiaRegistro.safra_id == safra_id,
                SafraFenologiaRegistro.talhao_id == talhao_id,
                SafraFenologiaRegistro.tenant_id == self.tenant_id,
            )
            .order_by(SafraFenologiaRegistro.data_observacao)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def listar_por_safra(self, safra_id: UUID) -> list[SafraFenologiaRegistro]:
        stmt = (
            select(SafraFenologiaRegistro)
            .where(
                SafraFenologiaRegistro.safra_id == safra_id,
                SafraFenologiaRegistro.tenant_id == self.tenant_id,
            )
            .order_by(SafraFenologiaRegistro.talhao_id, SafraFenologiaRegistro.data_observacao)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def estagio_atual_por_talhao(self, safra_id: UUID, talhao_id: UUID) -> SafraFenologiaRegistro | None:
        stmt = (
            select(SafraFenologiaRegistro)
            .where(
                SafraFenologiaRegistro.safra_id == safra_id,
                SafraFenologiaRegistro.talhao_id == talhao_id,
                SafraFenologiaRegistro.tenant_id == self.tenant_id,
            )
            .order_by(SafraFenologiaRegistro.data_observacao.desc())
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalars().first()

    def _to_response(self, r: SafraFenologiaRegistro) -> FenologiaRegistroResponse:
        return FenologiaRegistroResponse(
            id=r.id,
            safra_id=r.safra_id,
            talhao_id=r.talhao_id,
            grupo_id=r.grupo_id,
            escala_id=r.escala_id,
            data_observacao=r.data_observacao,
            usuario_id=r.usuario_id,
            observacao=r.observacao,
            dados_extras=r.dados_extras,
            created_at=r.created_at,
            escala_codigo=r.escala.codigo if r.escala else None,
            escala_nome=r.escala.nome if r.escala else None,
            escala_ordem=r.escala.ordem if r.escala else None,
        )
