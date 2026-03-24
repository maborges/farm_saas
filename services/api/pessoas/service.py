import uuid
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from core.base_service import BaseService
from core.exceptions import EntityNotFoundError
from pessoas.models import Pessoa
from pessoas.schemas.pessoa import PessoaCreate, PessoaUpdate


class PessoaService(BaseService[Pessoa]):
    """
    Serviço de cadastro de pessoas (fornecedores, clientes, funcionários, parceiros).

    Herda BaseService para garantir isolamento de tenant em todas as operações.
    """

    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(Pessoa, session, tenant_id)

    async def list_by_tipo(
        self,
        tipo: str | None = None,
        ativo: bool | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Pessoa]:
        """Lista pessoas com filtros opcionais por tipo, status e busca textual."""
        stmt = select(Pessoa).where(Pessoa.tenant_id == self.tenant_id)

        if tipo:
            # Busca tanto no tipo_principal quanto na lista JSON de tipos
            stmt = stmt.where(
                or_(
                    Pessoa.tipo_principal == tipo,
                    Pessoa.tipos.contains([tipo]),
                )
            )

        if ativo is not None:
            stmt = stmt.where(Pessoa.ativo == ativo)

        if search:
            termo = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Pessoa.nome.ilike(termo),
                    Pessoa.nome_fantasia.ilike(termo),
                    Pessoa.cpf_cnpj.ilike(termo),
                    Pessoa.email.ilike(termo),
                )
            )

        stmt = stmt.order_by(Pessoa.nome).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_tipo(self, tipo: str | None = None, ativo: bool | None = None) -> int:
        from sqlalchemy import func
        stmt = select(func.count()).select_from(Pessoa).where(Pessoa.tenant_id == self.tenant_id)
        if tipo:
            stmt = stmt.where(
                or_(Pessoa.tipo_principal == tipo, Pessoa.tipos.contains([tipo]))
            )
        if ativo is not None:
            stmt = stmt.where(Pessoa.ativo == ativo)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def criar(self, data: PessoaCreate) -> Pessoa:
        return await self.create(data.model_dump())

    async def atualizar(self, pessoa_id: uuid.UUID, data: PessoaUpdate) -> Pessoa:
        pessoa = await self.get_or_fail(pessoa_id)
        updates = data.model_dump(exclude_unset=True)
        return await self.update(pessoa, updates)

    async def buscar_por_cpf_cnpj(self, cpf_cnpj: str) -> Pessoa | None:
        """Busca por documento — útil para evitar duplicatas."""
        stmt = select(Pessoa).where(
            and_(
                Pessoa.tenant_id == self.tenant_id,
                Pessoa.cpf_cnpj == cpf_cnpj,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
