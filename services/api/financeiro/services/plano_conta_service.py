import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.base_service import BaseService
from core.exceptions import BusinessRuleError, EntityNotFoundError
from financeiro.models.plano_conta import PlanoConta
from financeiro.schemas.plano_conta_schema import PlanoContaCreate, PlanoContaUpdate, PlanoContaNode


# Categorias padrão do Livro Caixa do Produtor Rural (RFB)
CATEGORIAS_PADRAO = [
    # ── RECEITAS ──────────────────────────────────────────────────────────
    {"codigo": "1", "nome": "Receitas da Atividade Rural", "tipo": "RECEITA",
     "natureza": "SINTETICA", "categoria_rfb": "RECEITA_ATIVIDADE", "ordem": 10},
    {"codigo": "1.01", "nome": "Venda de Produtos Vegetais", "tipo": "RECEITA",
     "natureza": "ANALITICA", "categoria_rfb": "RECEITA_ATIVIDADE", "ordem": 10, "_pai": "1"},
    {"codigo": "1.02", "nome": "Venda de Animais e Produtos de Origem Animal", "tipo": "RECEITA",
     "natureza": "ANALITICA", "categoria_rfb": "RECEITA_ATIVIDADE", "ordem": 20, "_pai": "1"},
    {"codigo": "1.03", "nome": "Serviços Prestados na Atividade Rural", "tipo": "RECEITA",
     "natureza": "ANALITICA", "categoria_rfb": "RECEITA_ATIVIDADE", "ordem": 30, "_pai": "1"},
    {"codigo": "1.04", "nome": "Subvenções e Incentivos", "tipo": "RECEITA",
     "natureza": "ANALITICA", "categoria_rfb": "RECEITA_ATIVIDADE", "ordem": 40, "_pai": "1"},
    {"codigo": "1.05", "nome": "Outras Receitas da Atividade Rural", "tipo": "RECEITA",
     "natureza": "ANALITICA", "categoria_rfb": "RECEITA_ATIVIDADE", "ordem": 50, "_pai": "1"},
    {"codigo": "2", "nome": "Receitas Fora da Atividade Rural", "tipo": "RECEITA",
     "natureza": "SINTETICA", "categoria_rfb": "RECEITA_FORA_ATIVIDADE", "ordem": 20},
    {"codigo": "2.01", "nome": "Arrendamento Recebido", "tipo": "RECEITA",
     "natureza": "ANALITICA", "categoria_rfb": "RECEITA_FORA_ATIVIDADE", "ordem": 10, "_pai": "2"},
    {"codigo": "2.02", "nome": "Outras Receitas", "tipo": "RECEITA",
     "natureza": "ANALITICA", "categoria_rfb": "RECEITA_FORA_ATIVIDADE", "ordem": 20, "_pai": "2"},
    # ── DESPESAS DE CUSTEIO ───────────────────────────────────────────────
    {"codigo": "3", "nome": "Despesas de Custeio", "tipo": "DESPESA",
     "natureza": "SINTETICA", "categoria_rfb": "CUSTEIO", "ordem": 30},
    {"codigo": "3.01", "nome": "Sementes e Mudas", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 10, "_pai": "3"},
    {"codigo": "3.02", "nome": "Fertilizantes e Corretivos", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 20, "_pai": "3"},
    {"codigo": "3.03", "nome": "Defensivos Agrícolas", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 30, "_pai": "3"},
    {"codigo": "3.04", "nome": "Combustíveis e Lubrificantes", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 40, "_pai": "3"},
    {"codigo": "3.05", "nome": "Mão de Obra (Diaristas e Empregados)", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 50, "_pai": "3"},
    {"codigo": "3.06", "nome": "Manutenção e Reparos de Máquinas e Equipamentos", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 60, "_pai": "3"},
    {"codigo": "3.07", "nome": "Energia Elétrica (Atividade Rural)", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 70, "_pai": "3"},
    {"codigo": "3.08", "nome": "Fretes e Carretos", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 80, "_pai": "3"},
    {"codigo": "3.09", "nome": "Arrendamento Pago", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 90, "_pai": "3"},
    {"codigo": "3.10", "nome": "Assistência Técnica e Veterinária", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 100, "_pai": "3"},
    {"codigo": "3.11", "nome": "Seguros (Atividade Rural)", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 110, "_pai": "3"},
    {"codigo": "3.12", "nome": "Ração e Suplementos Animais", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 120, "_pai": "3"},
    {"codigo": "3.13", "nome": "Medicamentos Veterinários", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 130, "_pai": "3"},
    {"codigo": "3.14", "nome": "Outras Despesas de Custeio", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "CUSTEIO", "ordem": 140, "_pai": "3"},
    # ── INVESTIMENTOS ─────────────────────────────────────────────────────
    {"codigo": "4", "nome": "Investimentos", "tipo": "DESPESA",
     "natureza": "SINTETICA", "categoria_rfb": "INVESTIMENTO", "ordem": 40},
    {"codigo": "4.01", "nome": "Aquisição de Máquinas e Equipamentos", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "INVESTIMENTO", "ordem": 10, "_pai": "4"},
    {"codigo": "4.02", "nome": "Construções e Benfeitorias", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "INVESTIMENTO", "ordem": 20, "_pai": "4"},
    {"codigo": "4.03", "nome": "Aquisição de Animais (Reprodução e Produção)", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "INVESTIMENTO", "ordem": 30, "_pai": "4"},
    {"codigo": "4.04", "nome": "Implantação de Culturas Permanentes", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "INVESTIMENTO", "ordem": 40, "_pai": "4"},
    {"codigo": "4.05", "nome": "Aquisição de Terrenos e Imóveis Rurais", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "INVESTIMENTO", "ordem": 50, "_pai": "4"},
    # ── DESPESAS NÃO DEDUTÍVEIS ───────────────────────────────────────────
    {"codigo": "5", "nome": "Despesas Não Dedutíveis", "tipo": "DESPESA",
     "natureza": "SINTETICA", "categoria_rfb": "NAO_DEDUTIVEL", "ordem": 50},
    {"codigo": "5.01", "nome": "Despesas Pessoais e Familiares", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "NAO_DEDUTIVEL", "ordem": 10, "_pai": "5"},
    {"codigo": "5.02", "nome": "Outras Despesas Não Dedutíveis", "tipo": "DESPESA",
     "natureza": "ANALITICA", "categoria_rfb": "NAO_DEDUTIVEL", "ordem": 20, "_pai": "5"},
]


class PlanoContaService(BaseService[PlanoConta]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(PlanoConta, session, tenant_id)

    async def criar(self, obj_in: PlanoContaCreate) -> PlanoConta:
        # Valida parent se informado
        if obj_in.parent_id:
            pai = await self.get(obj_in.parent_id)
            if not pai:
                raise BusinessRuleError("Conta pai não encontrada.")
            if pai.natureza == "ANALITICA":
                raise BusinessRuleError("Conta analítica não pode ter filhos.")
            if pai.tipo != obj_in.tipo:
                raise BusinessRuleError("Conta filha deve ter o mesmo tipo da conta pai.")

        # Código único por tenant
        stmt = select(PlanoConta).where(
            PlanoConta.tenant_id == self.tenant_id,
            PlanoConta.codigo == obj_in.codigo,
        )
        existente = (await self.session.execute(stmt)).scalars().first()
        if existente:
            raise BusinessRuleError(f"Código '{obj_in.codigo}' já existe no plano de contas.")

        data = obj_in.model_dump()
        data["tenant_id"] = self.tenant_id
        db_obj = PlanoConta(**data)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def atualizar(self, plano_id: uuid.UUID, data: PlanoContaUpdate) -> PlanoConta:
        plano = await self.get_or_fail(plano_id)
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(plano, field, value)
        self.session.add(plano)
        await self.session.flush()
        await self.session.refresh(plano)
        return plano

    async def deletar(self, plano_id: uuid.UUID) -> None:
        plano = await self.get_or_fail(plano_id)
        if plano.is_sistema:
            raise BusinessRuleError("Categorias do sistema não podem ser excluídas.")
        # Verifica se tem filhos
        stmt = select(PlanoConta).where(
            PlanoConta.tenant_id == self.tenant_id,
            PlanoConta.parent_id == plano_id,
        )
        filhos = (await self.session.execute(stmt)).scalars().first()
        if filhos:
            raise BusinessRuleError("Conta com subcategorias não pode ser excluída.")
        await self.hard_delete(plano_id)

    async def listar_arvore(self, tipo: str | None = None) -> list[PlanoContaNode]:
        """Retorna todos os planos em estrutura hierárquica."""
        stmt = select(PlanoConta).where(
            PlanoConta.tenant_id == self.tenant_id,
            PlanoConta.ativo == True,
        ).order_by(PlanoConta.ordem, PlanoConta.codigo)

        if tipo:
            stmt = stmt.where(PlanoConta.tipo == tipo)

        todos = list((await self.session.execute(stmt)).scalars().all())

        # Constrói mapa id → node
        mapa: dict[uuid.UUID, PlanoContaNode] = {}
        for item in todos:
            mapa[item.id] = PlanoContaNode.model_validate(item)

        raizes: list[PlanoContaNode] = []
        for item in todos:
            node = mapa[item.id]
            if item.parent_id and item.parent_id in mapa:
                mapa[item.parent_id].filhos.append(node)
            else:
                raizes.append(node)

        return raizes

    async def seed_padrao(self) -> int:
        """
        Popula o plano de contas com as categorias padrão RFB.
        Ignora categorias já existentes (idempotente por código).
        Retorna quantas foram criadas.
        """
        # Busca todos os códigos existentes
        stmt = select(PlanoConta.codigo).where(PlanoConta.tenant_id == self.tenant_id)
        codigos_existentes = set((await self.session.execute(stmt)).scalars().all())

        # Primeira passagem: cria raízes (sem _pai)
        codigo_para_id: dict[str, uuid.UUID] = {}

        # Busca IDs dos que já existem
        stmt2 = select(PlanoConta).where(PlanoConta.tenant_id == self.tenant_id)
        for pc in (await self.session.execute(stmt2)).scalars().all():
            codigo_para_id[pc.codigo] = pc.id

        criados = 0
        for cat in CATEGORIAS_PADRAO:
            if cat["codigo"] in codigos_existentes:
                continue

            pai_codigo = cat.get("_pai")
            parent_id = codigo_para_id.get(pai_codigo) if pai_codigo else None

            pc = PlanoConta(
                tenant_id=self.tenant_id,
                parent_id=parent_id,
                codigo=cat["codigo"],
                nome=cat["nome"],
                tipo=cat["tipo"],
                natureza=cat["natureza"],
                categoria_rfb=cat.get("categoria_rfb"),
                ordem=cat.get("ordem", 0),
                is_sistema=True,
            )
            self.session.add(pc)
            await self.session.flush()
            codigo_para_id[pc.codigo] = pc.id
            criados += 1

        return criados
