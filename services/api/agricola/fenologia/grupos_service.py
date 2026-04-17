from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.base_service import BaseService
from core.exceptions import BusinessRuleError
from agricola.fenologia.models import SafraTalhaoGrupo, SafraTalhaoGrupoItem


class SafraTalhaoGrupoService(BaseService[SafraTalhaoGrupo]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(SafraTalhaoGrupo, session, tenant_id)

    async def listar(self, safra_id: UUID) -> list[SafraTalhaoGrupo]:
        stmt = (
            select(SafraTalhaoGrupo)
            .where(
                SafraTalhaoGrupo.safra_id == safra_id,
                SafraTalhaoGrupo.tenant_id == self.tenant_id,
            )
            .order_by(SafraTalhaoGrupo.ordem)
        )
        result = await self.session.execute(stmt)
        grupos = list(result.scalars().all())

        # Carrega itens de cada grupo
        for grupo in grupos:
            stmt_itens = select(SafraTalhaoGrupoItem).where(
                SafraTalhaoGrupoItem.tenant_id == grupo.id
            )
            itens = (await self.session.execute(stmt_itens)).scalars().all()
            grupo.itens = list(itens)

        return grupos

    async def criar(self, safra_id: UUID, nome: str, cor: str | None = None, ordem: int = 0) -> SafraTalhaoGrupo:
        grupo = SafraTalhaoGrupo(
            safra_id=safra_id,
            tenant_id=self.tenant_id,
            nome=nome,
            cor=cor,
            ordem=ordem,
        )
        self.session.add(grupo)
        await self.session.flush()
        grupo.itens = []
        return grupo

    async def atualizar(self, grupo_id: UUID, nome: str | None = None, cor: str | None = None, ordem: int | None = None) -> SafraTalhaoGrupo:
        grupo = await self.get_or_fail(grupo_id)
        if nome is not None:
            grupo.nome = nome
        if cor is not None:
            grupo.cor = cor
        if ordem is not None:
            grupo.ordem = ordem
        await self.session.flush()
        return grupo

    async def excluir(self, grupo_id: UUID) -> None:
        grupo = await self.get_or_fail(grupo_id)
        await self.session.delete(grupo)
        await self.session.flush()

    async def sincronizar_talhoes(self, grupo_id: UUID, talhao_ids: list[UUID]) -> SafraTalhaoGrupo:
        """Substitui todos os talhões do grupo pelos talhao_ids fornecidos (usado no drag & drop)."""
        grupo = await self.get_or_fail(grupo_id)

        # Remove itens atuais
        stmt_del = select(SafraTalhaoGrupoItem).where(SafraTalhaoGrupoItem.tenant_id == grupo_id)
        itens_atuais = (await self.session.execute(stmt_del)).scalars().all()
        for item in itens_atuais:
            await self.session.delete(item)

        # Adiciona novos
        novos: list[SafraTalhaoGrupoItem] = []
        for tid in talhao_ids:
            item = SafraTalhaoGrupoItem(
                grupo_id=grupo_id,
                talhao_id=tid,
                tenant_id=self.tenant_id,
            )
            self.session.add(item)
            novos.append(item)

        await self.session.flush()
        grupo.itens = novos
        return grupo

    async def copiar_de_safra(self, safra_origem_id: UUID, safra_destino_id: UUID) -> list[SafraTalhaoGrupo]:
        """Copia grupos e seus talhões de uma safra anterior para a safra destino."""
        grupos_origem = await self.listar(safra_origem_id)
        if not grupos_origem:
            raise BusinessRuleError("Safra de origem não possui grupos cadastrados.")

        novos_grupos: list[SafraTalhaoGrupo] = []
        for i, grupo_orig in enumerate(grupos_origem):
            novo = await self.criar(safra_destino_id, grupo_orig.nome, grupo_orig.cor, i)
            talhao_ids = [item.talhao_id for item in grupo_orig.itens]
            if talhao_ids:
                await self.sincronizar_talhoes(novo.id, talhao_ids)
            novos_grupos.append(novo)

        return novos_grupos
