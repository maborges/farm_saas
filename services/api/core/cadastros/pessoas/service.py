import uuid
from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.base_service import BaseService
from core.exceptions import EntityNotFoundError, BusinessRuleError
from .models import (
    Pessoa, PessoaPII, PessoaEndereco,
    TipoRelacionamento, PessoaRelacionamento,
    PessoaConsentimento, PessoaAcessoLog,
)
from .schemas import (
    PessoaCreate, PessoaUpdate, PessoaPIIUpdate,
    EnderecoCreate, RelacionamentoCreate, ConsentimentoCreate,
)


class TipoRelacionamentoService(BaseService[TipoRelacionamento]):
    """Gerencia tipos: retorna sistema + tenant."""

    async def listar(self) -> list[TipoRelacionamento]:
        from sqlalchemy import or_
        conditions = [TipoRelacionamento.tenant_id.is_(None)]
        if self.tenant_id:
            conditions.append(TipoRelacionamento.tenant_id == self.tenant_id)
        stmt = select(TipoRelacionamento).where(
            TipoRelacionamento.ativo == True,
            or_(*conditions),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def criar_custom(self, data: dict) -> TipoRelacionamento:
        tipo = TipoRelacionamento(tenant_id=self.tenant_id, sistema=False, **data)
        self.session.add(tipo)
        await self.session.commit()
        await self.session.refresh(tipo)
        return tipo

    async def desativar(self, tipo_id: uuid.UUID) -> TipoRelacionamento:
        stmt = select(TipoRelacionamento).where(
            TipoRelacionamento.id == tipo_id,
            TipoRelacionamento.tenant_id == self.tenant_id,
            TipoRelacionamento.sistema == False,
        )
        result = await self.session.execute(stmt)
        tipo = result.scalar_one_or_none()
        if not tipo:
            raise EntityNotFoundError("Tipo de relacionamento não encontrado ou é padrão do sistema")
        tipo.ativo = False
        await self.session.commit()
        return tipo


class PessoaService(BaseService[Pessoa]):

    async def listar(self, tipo: str | None = None, ativo: bool = True) -> list[Pessoa]:
        stmt = (
            select(Pessoa)
            .where(Pessoa.tenant_id == self.tenant_id, Pessoa.ativo == ativo)
            .options(
                selectinload(Pessoa.relacionamentos).selectinload(PessoaRelacionamento.tipo)
            )
        )
        if tipo:
            stmt = stmt.where(Pessoa.tipo == tipo)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def criar(self, data: PessoaCreate) -> Pessoa:
        pessoa = Pessoa(
            tenant_id=self.tenant_id,
            tipo=data.tipo,
            nome_exibicao=data.nome_exibicao,
            base_legal=data.base_legal,
            reter_dados_ate=data.reter_dados_ate,
        )
        self.session.add(pessoa)
        await self.session.flush()

        # PII
        pii_data = data.pii.model_dump(exclude_none=True) if data.pii else {}
        pii = PessoaPII(pessoa_id=pessoa.id, **pii_data)
        self.session.add(pii)

        # Endereços
        for end in data.enderecos:
            self.session.add(PessoaEndereco(pessoa_id=pessoa.id, **end.model_dump()))

        # Relacionamentos
        for rel in data.relacionamentos:
            self.session.add(PessoaRelacionamento(pessoa_id=pessoa.id, **rel.model_dump()))

        await self.session.commit()
        await self.session.refresh(pessoa)
        return pessoa

    async def _get_pessoa(self, pessoa_id: uuid.UUID) -> Pessoa:
        stmt = (
            select(Pessoa)
            .where(Pessoa.id == pessoa_id, Pessoa.tenant_id == self.tenant_id)
            .options(selectinload(Pessoa.relacionamentos).selectinload(PessoaRelacionamento.tipo))
        )
        result = await self.session.execute(stmt)
        pessoa = result.scalar_one_or_none()
        if not pessoa:
            raise EntityNotFoundError(f"Pessoa {pessoa_id} não encontrada")
        return pessoa

    async def atualizar(self, pessoa_id: uuid.UUID, data: PessoaUpdate) -> Pessoa:
        pessoa = await self._get_pessoa(pessoa_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(pessoa, field, value)
        await self.session.commit()
        await self.session.refresh(pessoa)
        return pessoa

    async def obter_pii(self, pessoa_id: uuid.UUID, usuario_id: uuid.UUID | None, motivo: str | None) -> PessoaPII | None:
        """Retorna PII e registra acesso no audit log."""
        stmt = select(PessoaPII).where(PessoaPII.pessoa_id == pessoa_id)
        result = await self.session.execute(stmt)
        pii = result.scalar_one_or_none()

        # Audit log
        campos = ["nome_completo", "cpf", "rg", "cnpj", "email", "telefone", "celular"]
        log = PessoaAcessoLog(
            pessoa_id=pessoa_id,
            usuario_id=usuario_id,
            campos_acessados=campos,
            motivo=motivo,
        )
        self.session.add(log)
        await self.session.commit()
        return pii

    async def atualizar_pii(self, pessoa_id: uuid.UUID, data: PessoaPIIUpdate) -> PessoaPII:
        await self._get_pessoa(pessoa_id)  # ensures tenant ownership
        stmt = select(PessoaPII).where(PessoaPII.pessoa_id == pessoa_id)
        result = await self.session.execute(stmt)
        pii = result.scalar_one_or_none()
        if not pii:
            pii = PessoaPII(pessoa_id=pessoa_id)
            self.session.add(pii)

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(pii, field, value)
        await self.session.commit()
        await self.session.refresh(pii)
        return pii

    async def listar_enderecos(self, pessoa_id: uuid.UUID) -> list[PessoaEndereco]:
        await self._get_pessoa(pessoa_id)
        stmt = select(PessoaEndereco).where(
            PessoaEndereco.pessoa_id == pessoa_id,
            PessoaEndereco.ativo == True,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def adicionar_endereco(self, pessoa_id: uuid.UUID, data: EnderecoCreate) -> PessoaEndereco:
        await self._get_pessoa(pessoa_id)
        endereco = PessoaEndereco(pessoa_id=pessoa_id, **data.model_dump())
        self.session.add(endereco)
        await self.session.commit()
        await self.session.refresh(endereco)
        return endereco

    async def adicionar_relacionamento(self, pessoa_id: uuid.UUID, data: RelacionamentoCreate) -> PessoaRelacionamento:
        await self._get_pessoa(pessoa_id)
        rel = PessoaRelacionamento(pessoa_id=pessoa_id, **data.model_dump())
        self.session.add(rel)
        await self.session.commit()
        await self.session.refresh(rel)
        return rel

    async def registrar_consentimento(self, pessoa_id: uuid.UUID, data: ConsentimentoCreate) -> PessoaConsentimento:
        await self._get_pessoa(pessoa_id)
        c = PessoaConsentimento(pessoa_id=pessoa_id, **data.model_dump())
        self.session.add(c)
        await self.session.commit()
        await self.session.refresh(c)
        return c

    async def anonimizar(self, pessoa_id: uuid.UUID) -> Pessoa:
        """LGPD — direito ao esquecimento. Apaga PII, mantém histórico operacional."""
        pessoa = await self._get_pessoa(pessoa_id)
        if pessoa.anonimizado_em:
            raise BusinessRuleError("Pessoa já foi anonimizada")

        # Zera PII
        stmt = select(PessoaPII).where(PessoaPII.pessoa_id == pessoa_id)
        result = await self.session.execute(stmt)
        pii = result.scalar_one_or_none()
        if pii:
            for col in ["nome_completo", "cpf", "rg", "razao_social", "cnpj",
                        "ie", "email", "telefone", "celular", "nome_fantasia"]:
                setattr(pii, col, None)
            pii.data_nascimento = None
            pii.data_fundacao = None

        pessoa.nome_exibicao = f"[ANONIMIZADO-{pessoa_id.hex[:8].upper()}]"
        pessoa.anonimizado_em = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(pessoa)
        return pessoa
