from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.base_service import BaseService
from agricola.monitoramento.models import MonitoramentoPragas
from agricola.monitoramento.catalogo_model import MonitoramentoCatalogo
from agricola.monitoramento.schemas import MonitoramentoPragasCreate, MonitoramentoPragasUpdate
from agricola.fenologia.models import SafraFenologiaRegistro
from agricola.safras.models import Safra
from agricola.checklist.service import SafraChecklistService
from agricola.checklist.schemas import ChecklistItemAdicionar
from notificacoes.service import NotificacaoService
from notificacoes.schemas import NotificacaoCreate


class MonitoramentoCatalogoService(BaseService[MonitoramentoCatalogo]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(MonitoramentoCatalogo, session, tenant_id)

    async def listar(self, tipo: str | None = None, cultura: str | None = None) -> list[MonitoramentoCatalogo]:
        """Retorna entradas do tenant + entradas system (is_system=True) visíveis para todos."""
        from sqlalchemy import or_
        stmt = (
            select(MonitoramentoCatalogo)
            .where(
                MonitoramentoCatalogo.ativo == True,
                or_(
                    MonitoramentoCatalogo.tenant_id == self.tenant_id,
                    MonitoramentoCatalogo.is_system == True,
                ),
            )
            .order_by(MonitoramentoCatalogo.tipo, MonitoramentoCatalogo.nome_popular)
        )
        if tipo:
            stmt = stmt.where(MonitoramentoCatalogo.tipo == tipo)
        if cultura:
            from sqlalchemy import or_ as or2
            stmt = stmt.where(
                or2(MonitoramentoCatalogo.cultura == cultura, MonitoramentoCatalogo.cultura == None)
            )
        return list((await self.session.execute(stmt)).scalars().all())

    async def criar(self, dados: dict) -> MonitoramentoCatalogo:
        dados["is_system"] = False
        return await self.create(dados)


class MonitoramentoService(BaseService[MonitoramentoPragas]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(MonitoramentoPragas, session, tenant_id)

    async def _buscar_estagio_fenologico(self, safra_id: UUID, data_avaliacao: date) -> SafraFenologiaRegistro | None:
        """Busca o último estágio fenológico registrado até a data de avaliação."""
        stmt = (
            select(SafraFenologiaRegistro)
            .where(
                SafraFenologiaRegistro.safra_id == safra_id,
                SafraFenologiaRegistro.tenant_id == self.tenant_id,
                SafraFenologiaRegistro.data_observacao <= data_avaliacao,
            )
            .order_by(SafraFenologiaRegistro.data_observacao.desc())
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalars().first()

    async def criar(self, dados: MonitoramentoPragasCreate, tecnico_id: UUID | None = None) -> MonitoramentoPragas:
        # Busca estágio fenológico automático
        estagio = await self._buscar_estagio_fenologico(dados.safra_id, dados.data_avaliacao)
        estagio_codigo = dados.estagio_fenologico_codigo or (estagio.escala.codigo if estagio and estagio.escala else None)
        estagio_id = dados.estagio_fenologico_id or (estagio.id if estagio else None)

        # Preenche NDE do catálogo se não informado
        nde_cultura = dados.nde_cultura
        nome_popular = dados.nome_popular
        nome_cientifico = dados.nome_cientifico
        tipo = dados.tipo
        unidade_medida = dados.unidade_medida

        if dados.catalogo_id:
            cat = await self.session.get(MonitoramentoCatalogo, dados.catalogo_id)
            if cat:
                nde_cultura = nde_cultura or (float(cat.nde_padrao) if cat.nde_padrao else None)
                nome_popular = nome_popular or cat.nome_popular
                nome_cientifico = nome_cientifico or cat.nome_cientifico
                tipo = tipo or cat.tipo
                unidade_medida = unidade_medida or cat.unidade_medida

        # Calcula se atingiu NDE
        atingiu_nde = bool(
            nde_cultura and dados.nivel_infestacao and float(dados.nivel_infestacao) >= float(nde_cultura)
        )

        registro = MonitoramentoPragas(
            tenant_id=self.tenant_id,
            safra_id=dados.safra_id,
            talhao_id=dados.talhao_id,
            data_avaliacao=dados.data_avaliacao,
            tipo=tipo,
            nome_popular=nome_popular,
            nome_cientifico=nome_cientifico,
            nivel_infestacao=dados.nivel_infestacao,
            unidade_medida=unidade_medida,
            nde_cultura=nde_cultura,
            atingiu_nde=atingiu_nde,
            catalogo_id=dados.catalogo_id,
            estagio_fenologico_codigo=estagio_codigo,
            estagio_fenologico_id=estagio_id,
            acao_tomada=dados.acao_tomada,
            observacoes=dados.observacoes,
            tecnico_id=tecnico_id,
            latitude=dados.latitude,
            longitude=dados.longitude,
        )
        self.session.add(registro)
        await self.session.flush()

        # Reações ao NDE atingido
        if atingiu_nde:
            await self._reagir_nde(registro, dados.safra_id)

        return registro

    async def _reagir_nde(self, registro: MonitoramentoPragas, safra_id: UUID) -> None:
        """Dispara notificação + cria tarefa obrigatória no checklist da fase atual."""
        safra = await self.session.get(Safra, safra_id)
        if not safra:
            return

        nome = registro.nome_popular or registro.nome_cientifico or "Organismo"

        # 1. Notificação push
        notif_svc = NotificacaoService(self.session, self.tenant_id)
        await notif_svc.criar_e_push(NotificacaoCreate(
            tipo="ALERTA_NDE",
            titulo=f"NDE atingido — {nome}",
            mensagem=(
                f"Safra {safra.cultura} {safra.ano_safra}: {nome} atingiu o nível de dano econômico "
                f"({registro.nivel_infestacao} {registro.unidade_medida or ''}). "
                f"Avalie a necessidade de controle."
            ),
        ))

        # 2. Tarefa obrigatória no checklist da fase atual
        checklist_svc = SafraChecklistService(self.session, self.tenant_id)
        await checklist_svc.adicionar_item(
            safra_id=safra_id,
            fase=safra.status,
            dados=ChecklistItemAdicionar(
                titulo=f"Controle de {nome} — NDE atingido",
                descricao=(
                    f"Nível detectado: {registro.nivel_infestacao} {registro.unidade_medida or ''}. "
                    f"Estágio: {registro.estagio_fenologico_codigo or 'N/D'}. "
                    f"Avalie e registre a operação de controle ou justifique a não intervenção."
                ),
                obrigatorio=True,
            ),
        )

    async def listar_por_safra(
        self, safra_id: UUID, tipo: str | None = None, talhao_id: UUID | None = None
    ) -> list[MonitoramentoPragas]:
        stmt = select(MonitoramentoPragas).where(
            MonitoramentoPragas.safra_id == safra_id,
            MonitoramentoPragas.tenant_id == self.tenant_id,
        ).order_by(MonitoramentoPragas.data_avaliacao.desc())
        if tipo:
            stmt = stmt.where(MonitoramentoPragas.tipo == tipo)
        if talhao_id:
            stmt = stmt.where(MonitoramentoPragas.talhao_id == talhao_id)
        return list((await self.session.execute(stmt)).scalars().all())

    async def diagnosticar_imagem(self, foto_bytes: bytes) -> dict:
        import random
        diagnosticos = [
            {"praga_identificada": "Lagarta-do-cartucho", "tipo": "PRAGA", "certeza_percentual": 98.2},
            {"praga_identificada": "Ferrugem Asiática", "tipo": "DOENCA", "certeza_percentual": 92.5},
            {"praga_identificada": "Percevejo Marrom", "tipo": "PRAGA", "certeza_percentual": 95.8},
            {"praga_identificada": "Buva", "tipo": "PLANTA_DANINHA", "certeza_percentual": 99.1},
        ]
        return random.choice(diagnosticos)
