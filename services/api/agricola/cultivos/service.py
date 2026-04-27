import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
from sqlalchemy.orm import selectinload
from decimal import Decimal

from core.base_service import BaseService
from core.exceptions import BusinessRuleError, EntityNotFoundError
from agricola.safras.models import Safra
from agricola.cultivos.models import Cultivo, CultivoArea
from agricola.cultivos.schemas import (
    CultivoCreate,
    CultivoUpdate,
    CultivoResponse,
    CultivoAreaCreate,
    CultivoAreaAnalisePatch,
    TarefaSoloGerada,
)
from core.cadastros.propriedades.models import AreaRural


class CultivoService(BaseService[Cultivo]):
    """Serviço para gerenciar cultivos dentro de safras."""

    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        super().__init__(Cultivo, session, tenant_id)
        self.session = session
        self.tenant_id = tenant_id

    async def _get_safra(self, safra_id: uuid.UUID) -> Safra:
        """Valida que a safra existe e pertence ao tenant."""
        stmt = select(Safra).where(
            Safra.id == safra_id,
            Safra.tenant_id == self.tenant_id,
        )
        safra = (await self.session.execute(stmt)).scalars().first()
        if not safra:
            raise EntityNotFoundError(f"Safra {safra_id} não encontrada.")
        return safra

    @staticmethod
    def _periodos_se_sobrepoe(inicio1, fim1, inicio2, fim2) -> bool:
        """Verifica se dois períodos se sobrepõem.

        Períodos vazios (None) são considerados como "sempre ativo".
        """
        # Se ambos têm datas, verifica sobreposição
        if inicio1 and fim1 and inicio2 and fim2:
            return not (fim1 < inicio2 or fim2 < inicio1)
        # Se algum período está vazio, considera como sobreposição
        return True

    async def _validar_ocupacao_talhao(
        self, safra_id: uuid.UUID, areas_data: list[CultivoAreaCreate],
        consorciado: bool, data_inicio=None, data_fim=None, cultivo_id_exclui: uuid.UUID | None = None
    ) -> None:
        """Valida ocupação de talhão conforme regras de consórcio.

        Regra base: Soma das áreas simultâneas ≤ área total do talhão
        Exceção: Cultivos consorciados podem compartilhar espaço

        Lógicas:
        1. Consorciado: só é permitido se talhão NÃO tem cultivos não-consorciados
        2. Não-consorciado: só é permitido se talhão NÃO tem cultivos consorciados
           E a soma de não-consorciados simultâneos ≤ capacidade

        Args:
            cultivo_id_exclui: ID do cultivo a excluir da validação (edição)
        """
        if not areas_data:
            return

        for area_data in areas_data:
            # Buscar info do talhão
            talhao_stmt = select(AreaRural).where(
                AreaRural.id == area_data.area_id,
                AreaRural.tenant_id == self.tenant_id,
            )
            talhao = (await self.session.execute(talhao_stmt)).scalars().first()
            if not talhao or not talhao.area_hectares:
                continue

            # Subquery: cultivos que ocupam este talhão
            cultivo_ids_stmt = select(CultivoArea.cultivo_id).where(
                CultivoArea.area_id == area_data.area_id
            ).distinct()

            # Buscar cultivos existentes (ativos, nesta safra, neste talhão)
            conditions = [
                Cultivo.safra_id == safra_id,
                Cultivo.status.notin_(["CANCELADA", "ENCERRADA"]),
                Cultivo.id.in_(cultivo_ids_stmt),
            ]
            if cultivo_id_exclui:
                conditions.append(Cultivo.id != cultivo_id_exclui)

            cultivos_stmt = select(Cultivo).where(and_(*conditions))
            cultivos = (await self.session.execute(cultivos_stmt)).scalars().all()

            # REGRA 1: Se novo cultivo é CONSORCIADO
            if consorciado:
                # Verificar se há cultivos não-consorciados neste talhão
                cultivos_nao_consorciados = [c for c in cultivos if not c.consorciado]
                if cultivos_nao_consorciados:
                    raise BusinessRuleError(
                        f"Talhão '{talhao.nome}' já tem cultivos não-consorciados. "
                        f"Não é possível criar um cultivo consorciado que se sobrepõe. "
                        f"Use um talhão diferente ou crie cultivos puros (não-consorciados)."
                    )
                # Consorciados com consorciados = permitido, nenhuma soma de área
                continue

            # REGRA 2: Se novo cultivo é NÃO-CONSORCIADO
            else:
                # Verificar se há cultivos consorciados neste talhão
                cultivos_consorciados = [c for c in cultivos if c.consorciado]
                if cultivos_consorciados:
                    raise BusinessRuleError(
                        f"Talhão '{talhao.nome}' já tem cultivos consorciados. "
                        f"Não é possível criar um cultivo não-consorciado que se sobrepõe. "
                        f"Use um talhão diferente ou marque como 'consorciado'."
                    )

                # Somar áreas apenas de cultivos NÃO-consorciados que se sobrepõem
                total_area = float(area_data.area_ha)
                for cultivo in cultivos:
                    if not cultivo.consorciado and self._periodos_se_sobrepoe(
                        data_inicio, data_fim, cultivo.data_inicio, cultivo.data_fim
                    ):
                        areas_cultivo = select(func.sum(CultivoArea.area_ha)).where(
                            and_(
                                CultivoArea.cultivo_id == cultivo.id,
                                CultivoArea.area_id == area_data.area_id,
                            )
                        )
                        area_cultivo = (await self.session.execute(areas_cultivo)).scalar() or 0.0
                        total_area += float(area_cultivo)

                # Validar se soma de não-consorciados excede capacidade
                if total_area > float(talhao.area_hectares):
                    raise BusinessRuleError(
                        f"Talhão '{talhao.nome}' tem capacidade de {talhao.area_hectares} ha, "
                        f"mas seria ocupado com {total_area:.2f} ha no período. "
                        f"Reduza a área ou use outro talhão."
                    )

    async def criar_com_areas(
        self, safra_id: uuid.UUID, data: CultivoCreate
    ) -> Cultivo:
        """Cria um cultivo com suas CultivoAreas atomicamente."""
        await self._get_safra(safra_id)

        # Validar ocupação de talhões considerando períodos
        await self._validar_ocupacao_talhao(
            safra_id, data.areas, data.consorciado, data.data_inicio, data.data_fim
        )

        cultivo = Cultivo(
            tenant_id=self.tenant_id,
            safra_id=safra_id,
            cultura=data.cultura,
            cultivar_id=data.cultivar_id,
            cultivar_nome=data.cultivar_nome,
            commodity_id=data.commodity_id,
            sistema_plantio=data.sistema_plantio,
            populacao_prevista=data.populacao_prevista,
            espacamento_cm=data.espacamento_cm,
            data_inicio=data.data_inicio,
            data_fim=data.data_fim,
            data_plantio_prevista=data.data_plantio_prevista,
            produtividade_meta_sc_ha=data.produtividade_meta_sc_ha,
            preco_venda_previsto=data.preco_venda_previsto,
            consorciado=data.consorciado,
            observacoes=data.observacoes,
        )
        self.session.add(cultivo)
        await self.session.flush()

        # Adicionar áreas
        for area_data in data.areas:
            area = CultivoArea(
                tenant_id=self.tenant_id,
                cultivo_id=cultivo.id,
                area_id=area_data.area_id,
                area_ha=area_data.area_ha,
            )
            self.session.add(area)

        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(cultivo, ["areas"])
        return cultivo

    async def vincular_analise(
        self, cultivo_area_id: uuid.UUID, dados: CultivoAreaAnalisePatch
    ) -> CultivoArea:
        """Vincula (ou desvincula) uma análise de solo a um CultivoArea."""
        stmt = select(CultivoArea).where(
            CultivoArea.id == cultivo_area_id,
            CultivoArea.tenant_id == self.tenant_id,
        )
        area = (await self.session.execute(stmt)).scalar_one_or_none()
        if not area:
            raise EntityNotFoundError("CultivoArea", str(cultivo_area_id))

        area.analise_solo_id = dados.analise_solo_id
        area.regiao_analise = dados.regiao_analise
        area.analise_status = dados.analise_status if dados.analise_solo_id else "REJEITADA"

        await self.session.commit()
        await self.session.refresh(area)
        return area

    async def gerar_tarefas_solo(
        self, cultivo_area_id: uuid.UUID,
        analise_id: uuid.UUID | None = None,
        regiao: str | None = None,
    ) -> list[TarefaSoloGerada]:
        """Gera lista de tarefas. analise_id/regiao sobrepõem o vínculo salvo no banco."""
        stmt = select(CultivoArea).where(
            CultivoArea.id == cultivo_area_id,
            CultivoArea.tenant_id == self.tenant_id,
        )
        area = (await self.session.execute(stmt)).scalar_one_or_none()
        if not area:
            raise EntityNotFoundError("CultivoArea", str(cultivo_area_id))

        analise_id_resolvido = analise_id or area.analise_solo_id
        regiao_resolvida = regiao if regiao is not None else area.regiao_analise

        if not analise_id_resolvido:
            raise BusinessRuleError("Nenhuma análise vinculada a este talhão.")

        from agricola.analises_solo.service import AnaliseSoloService
        from agricola.analises_solo.models import AnaliseSolo

        analise_stmt = select(AnaliseSolo).where(
            AnaliseSolo.id == analise_id_resolvido,
            AnaliseSolo.tenant_id == self.tenant_id,
        )
        analise = (await self.session.execute(analise_stmt)).scalar_one_or_none()
        if not analise:
            raise EntityNotFoundError("AnaliseSolo", str(analise_id_resolvido))

        cultivo_stmt = select(Cultivo).where(Cultivo.id == area.cultivo_id)
        cultivo = (await self.session.execute(cultivo_stmt)).scalar_one_or_none()

        solo_svc = AnaliseSoloService(self.session, self.tenant_id)
        recs = await solo_svc.gerar_recomendacoes(
            analise,
            cultura_id=cultivo.cultivar_id if cultivo else None,
            cultura_nome=cultivo.cultura if cultivo else "SOJA",
            regiao=regiao_resolvida or None,
        )

        tarefas: list[TarefaSoloGerada] = []
        mapeamento = [
            ("calagem", "Calagem", "CALCARIO"),
            ("fosforo", "Adubação Fosfatada", "P₂O₅"),
            ("potassio", "Adubação Potássica", "K₂O"),
            ("nitrogenio", "Adubação Nitrogenada", "N"),
        ]
        for chave, descricao, nutriente in mapeamento:
            rec = recs.get(chave)
            if not rec:
                continue
            if chave == "calagem":
                if not rec.get("necessaria"):
                    continue
                dose_raw = rec.get("dose_t_ha")
                dose = float(dose_raw) * 1000 if dose_raw is not None else None  # t/ha → kg/ha
            elif chave == "fosforo":
                dose_raw = rec.get("rec_dose_kg_ha") or rec.get("rec_p2o5_kg_ha")
                dose = float(dose_raw) if dose_raw is not None else None
            elif chave == "potassio":
                dose_raw = rec.get("rec_dose_kg_ha") or rec.get("rec_k2o_kg_ha")
                dose = float(dose_raw) if dose_raw is not None else None
            elif chave == "nitrogenio":
                dose_raw = rec.get("rec_n_kg_ha")
                dose = float(dose_raw) if dose_raw is not None else None
            else:
                dose = None
            if dose is None:
                continue
            qtd_total = round(dose * float(area.area_ha), 2) if dose else None
            tarefas.append(TarefaSoloGerada(
                nutriente=nutriente,
                descricao=descricao,
                dose_kg_ha=round(dose, 2),
                area_ha=float(area.area_ha),
                quantidade_total_kg=qtd_total,
                nivel=rec.get("nivel", ""),
                obs=rec.get("obs"),
            ))
        return tarefas

    async def get_com_areas(self, cultivo_id: uuid.UUID) -> Cultivo:
        """Retorna cultivo com áreas carregadas. Lança EntityNotFoundError se não encontrado."""
        from core.exceptions import EntityNotFoundError
        stmt = (
            select(Cultivo)
            .where(Cultivo.id == cultivo_id, Cultivo.tenant_id == self.tenant_id)
            .options(selectinload(Cultivo.areas))
        )
        cultivo = (await self.session.execute(stmt)).scalars().first()
        if not cultivo:
            raise EntityNotFoundError("Cultivo não encontrado.")
        return cultivo

    async def atualizar_com_areas(self, cultivo_id: uuid.UUID, updates: dict) -> Cultivo:
        """Atualiza cultivo e retorna com áreas carregadas."""
        await self.update(cultivo_id, updates)
        return await self.get_com_areas(cultivo_id)

    async def listar_por_safra(self, safra_id: uuid.UUID) -> list[Cultivo]:
        """Lista todos os cultivos de uma safra."""
        await self._get_safra(safra_id)
        stmt = select(Cultivo).where(
            Cultivo.tenant_id == self.tenant_id,
            Cultivo.safra_id == safra_id,
        ).options(selectinload(Cultivo.areas)).order_by(Cultivo.cultura)
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_area_total(self, cultivo_id: uuid.UUID) -> float:
        """Retorna a área total (em hectares) do cultivo."""
        stmt = select(func.sum(CultivoArea.area_ha)).where(
            CultivoArea.cultivo_id == cultivo_id,
            CultivoArea.tenant_id == self.tenant_id,
        )
        total = (await self.session.execute(stmt)).scalar() or 0.0
        return float(total)

    async def sincronizar_areas(
        self, cultivo_id: uuid.UUID, areas_data: list[CultivoAreaCreate]
    ) -> Cultivo:
        """Atualiza as CultivoAreas de um cultivo (DELETE + INSERT)."""
        cultivo = await self.get_or_fail(cultivo_id)

        # Validar ocupação de talhões (excluindo este cultivo da validação)
        await self._validar_ocupacao_talhao(
            cultivo.safra_id, areas_data, cultivo.consorciado,
            cultivo.data_inicio, cultivo.data_fim, cultivo_id_exclui=cultivo_id
        )

        # Remover áreas antigas
        delete_stmt = select(CultivoArea).where(
            CultivoArea.cultivo_id == cultivo_id,
            CultivoArea.tenant_id == self.tenant_id,
        )
        old_areas = list((await self.session.execute(delete_stmt)).scalars().all())
        for area in old_areas:
            await self.session.delete(area)

        # Adicionar novas áreas
        for area_data in areas_data:
            area = CultivoArea(
                tenant_id=self.tenant_id,
                cultivo_id=cultivo_id,
                area_id=area_data.area_id,
                area_ha=area_data.area_ha,
            )
            self.session.add(area)

        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(cultivo, ["areas"])
        return cultivo
