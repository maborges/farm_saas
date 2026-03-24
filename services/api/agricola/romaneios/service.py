import uuid
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.exceptions import BusinessRuleError
from core.base_service import BaseService

from agricola.romaneios.models import RomaneioColheita
from agricola.romaneios.schemas import RomaneioColheitaCreate

class RomaneioService(BaseService[RomaneioColheita]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(RomaneioColheita, session, tenant_id)

    async def criar(self, dados: RomaneioColheitaCreate) -> RomaneioColheita:
        dados_dict = dados.model_dump()
        
        # 1. Calcular o peso líquido bruto
        peso_bruto = dados_dict.get('peso_bruto_kg', 0)
        tara = dados_dict.get('tara_kg', 0)
        peso_liquido = peso_bruto - tara
        dados_dict['peso_liquido_kg'] = peso_liquido
        
        if peso_liquido < 0:
            raise BusinessRuleError("Peso líquido não pode ser negativo.")

        # 2. Descontos por impureza e umidade (Padrão genérico, pode variar por cultura)
        # Ex Soja: Umidade padrão 14%, Impureza padrão 1%
        umidade = dados_dict.get('umidade_pct') or 14.0
        impureza = dados_dict.get('impureza_pct') or 1.0
        
        # Calculo simplificado
        desc_umidade = 0
        if umidade > 14.0:
            # Ex: 0.14% de desconto para cada 0.1% a mais de umidade
            desc_umidade = peso_liquido * ((umidade - 14.0) * 0.014)
            
        desc_impureza = 0
        if impureza > 1.0:
            desc_impureza = peso_liquido * ((impureza - 1.0) * 0.01)
            
        dados_dict['desconto_umidade_kg'] = desc_umidade
        dados_dict['desconto_impureza_kg'] = desc_impureza
        
        peso_padrao = peso_liquido - desc_umidade - desc_impureza
        dados_dict['peso_liquido_padrao_kg'] = peso_padrao
        
        # 3. Converter para sacas (60kg)
        sacas = peso_padrao / 60.0
        dados_dict['sacas_60kg'] = sacas
        
        # 4. Calcular Receita Prevista se preço informado
        preco = dados_dict.get('preco_saca')
        if preco:
            dados_dict['receita_total'] = sacas * preco
            
        # O cálculo de produtividade (sc/ha) precisa da área do talhão, faremos via trigger
        # ou buscando o talhão
        romaneio = await super().create(dados_dict)

        # ── Integração com Financeiro: Receita de Venda de Grãos ──────────
        receita_total = dados_dict.get("receita_total") or 0.0
        if receita_total > 0:
            from financeiro.models.receita import Receita
            from financeiro.models.plano_conta import PlanoConta
            from agricola.talhoes.models import Talhao
            from agricola.safras.models import Safra

            stmt_talhao = select(Talhao.fazenda_id).where(Talhao.id == dados.talhao_id)
            fazenda_id = (await self.session.execute(stmt_talhao)).scalar()

            stmt_pc = (
                select(PlanoConta.id)
                .where(
                    PlanoConta.tenant_id == self.tenant_id,
                    PlanoConta.categoria_rfb == "RECEITA_ATIVIDADE",
                    PlanoConta.natureza == "ANALITICA",
                    PlanoConta.ativo == True,
                )
                .limit(1)
            )
            plano_id = (await self.session.execute(stmt_pc)).scalar()

            if plano_id and fazenda_id:
                stmt_safra = select(Safra.cultura, Safra.ano_safra).where(
                    Safra.id == dados.safra_id
                )
                safra_row = (await self.session.execute(stmt_safra)).first()
                descricao = (
                    f"Venda de grãos — {safra_row.cultura} {safra_row.ano_safra}"
                    if safra_row
                    else "Venda de grãos — Romaneio de Colheita"
                )
                rec = Receita(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    fazenda_id=fazenda_id,
                    plano_conta_id=plano_id,
                    descricao=descricao,
                    valor_total=float(receita_total),
                    data_emissao=dados.data_colheita,
                    data_vencimento=dados.data_colheita,
                    data_recebimento=dados.data_colheita,
                    status="RECEBIDO",
                )
                self.session.add(rec)

        await self.session.commit()
        await self.session.refresh(romaneio)
        return romaneio
