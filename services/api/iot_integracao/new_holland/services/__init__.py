"""Services para Sprint 26."""

from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, date

from iot_integracao.new_holland.models import (
    IntegracaoNewHolland, MaquinaNewHolland,
    MarketplaceIntegracao, TenantIntegracao, MarketplaceAvaliacao,
    CarbonoEmissao, CarbonoProjeto, CarbonoRelatorio
)


class NewHollandService:
    """Serviço de integração com New Holland PLM Connect."""

    BASE_URL = "https://api.plmconnect.newholland.com"

    def __init__(self, db: Session):
        self.db = db

    def conectar(self, tenant_id: str, client_id: str, 
                 client_secret: str, fazenda_id: Optional[int] = None) -> IntegracaoNewHolland:
        """Inicia integração com New Holland."""
        integracao = IntegracaoNewHolland(
            tenant_id=tenant_id,
            fazenda_id=fazenda_id,
            client_id=client_id,
            client_secret=client_secret,
            status="pendente"
        )
        self.db.add(integracao)
        self.db.commit()
        self.db.refresh(integracao)
        return integracao

    async def obter_token(self, integracao: IntegracaoNewHolland) -> Optional[str]:
        """Obtém ou renova token de acesso."""
        # Implementar OAuth2 New Holland
        pass

    async def sincronizar_maquinas(self, tenant_id: str, integracao_id: int) -> int:
        """Sincroniza máquinas da API New Holland."""
        # Implementar chamada à API
        return 0


class MarketplaceService:
    """Serviço do Marketplace de Integrações."""

    def __init__(self, db: Session):
        self.db = db

    def listar_integracoes(self, categoria: Optional[str] = None,
                           ativa: bool = True) -> List[MarketplaceIntegracao]:
        """Lista integrações disponíveis."""
        query = self.db.query(MarketplaceIntegracao).filter(
            MarketplaceIntegracao.ativa == ativa
        )
        if categoria:
            query = query.filter(MarketplaceIntegracao.categoria == categoria)
        return query.all()

    def instalar_integracao(self, tenant_id: str, integracao_id: int,
                           configuracoes: dict = None) -> TenantIntegracao:
        """Instala integração para um tenant."""
        integracao = self.db.query(MarketplaceIntegracao).filter(
            MarketplaceIntegracao.id == integracao_id
        ).first()
        if not integracao:
            raise ValueError("Integração não encontrada")

        tenant_integracao = TenantIntegracao(
            tenant_id=tenant_id,
            integracao_id=integracao_id,
            configuracoes=configuracoes or {}
        )
        self.db.add(tenant_integracao)
        
        # Atualizar stats
        integracao.total_instalacoes += 1
        
        self.db.commit()
        self.db.refresh(tenant_integracao)
        return tenant_integracao

    def desinstalar_integracao(self, tenant_id: str, integracao_id: int) -> bool:
        """Desinstala integração do tenant."""
        tenant_integracao = self.db.query(TenantIntegracao).filter(
            TenantIntegracao.tenant_id == tenant_id,
            TenantIntegracao.integracao_id == integracao_id
        ).first()
        if not tenant_integracao:
            return False
        
        self.db.delete(tenant_integracao)
        self.db.commit()
        return True

    def listar_instaladas(self, tenant_id: str) -> List[TenantIntegracao]:
        """Lista integrações instaladas pelo tenant."""
        return self.db.query(TenantIntegracao).filter(
            TenantIntegracao.tenant_id == tenant_id,
            TenantIntegracao.status == "ativa"
        ).all()


class CarbonoService:
    """Serviço para gestão de pegada de carbono."""

    # Fatores de emissão padrão (kgCO2e por unidade)
    FATORES_EMISSAO = {
        'diesel': 2.68,  # kgCO2e/L
        'gasolina': 2.31,  # kgCO2e/L
        'energia_eletrica': 0.061,  # kgCO2e/kWh (média Brasil)
        'gas_natural': 2.0,  # kgCO2e/m³
    }

    def __init__(self, db: Session):
        self.db = db

    def registrar_emissao(self, tenant_id: str, escopo: int,
                          categoria: str, quantidade: float,
                          unidade: str, data_referencia: date,
                          fator_emissao: float = None,
                          fazenda_id: int = None) -> CarbonoEmissao:
        """Registra emissão de carbono."""
        # Usar fator padrão se não fornecido
        if fator_emissao is None:
            fator_emissao = self.FATORES_EMISSAO.get(categoria.lower(), 0)

        total_co2e = quantidade * fator_emissao

        emissao = CarbonoEmissao(
            tenant_id=tenant_id,
            fazenda_id=fazenda_id,
            escopo=escopo,
            categoria=categoria,
            quantidade=quantidade,
            unidade=unidade,
            fator_emissao=fator_emissao,
            total_co2e=total_co2e,
            data_referencia=data_referencia
        )
        self.db.add(emissao)
        self.db.commit()
        self.db.refresh(emissao)
        return emissao

    def calcular_pegada(self, tenant_id: str, 
                        periodo_inicio: date,
                        periodo_fim: date) -> Dict:
        """Calcula pegada de carbono do período."""
        emissões = self.db.query(CarbonoEmissao).filter(
            CarbonoEmissao.tenant_id == tenant_id,
            CarbonoEmissao.data_referencia.between(periodo_inicio, periodo_fim)
        ).all()

        escopo_1 = sum(e.total_co2e for e in emissões if e.escopo == 1)
        escopo_2 = sum(e.total_co2e for e in emissões if e.escopo == 2)
        escopo_3 = sum(e.total_co2e for e in emissões if e.escopo == 3)

        return {
            "escopo_1": escopo_1,
            "escopo_2": escopo_2,
            "escopo_3": escopo_3,
            "total": escopo_1 + escopo_2 + escopo_3,
            "periodo_inicio": periodo_inicio,
            "periodo_fim": periodo_fim
        }

    def criar_projeto(self, tenant_id: str, nome: str,
                      tipo: str, area_ha: float,
                      fazenda_id: int = None) -> CarbonoProjeto:
        """Cria projeto de crédito de carbono."""
        projeto = CarbonoProjeto(
            tenant_id=tenant_id,
            fazenda_id=fazenda_id,
            nome=nome,
            tipo=tipo,
            area_ha=area_ha,
            status="planejamento"
        )
        self.db.add(projeto)
        self.db.commit()
        self.db.refresh(projeto)
        return projeto

    def gerar_relatorio(self, tenant_id: str,
                       periodo_inicio: date,
                       periodo_fim: date) -> CarbonoRelatorio:
        """Gera relatório de pegada de carbono."""
        pegada = self.calcular_pegada(tenant_id, periodo_inicio, periodo_fim)
        
        # Buscar créditos gerados
        creditos = self.db.query(CarbonoProjeto).filter(
            CarbonoProjeto.tenant_id == tenant_id,
            CarbonoProjeto.status == "certificado"
        ).all()
        creditos_gerados = sum(p.creditos_verificados or 0 for p in creditos)

        relatorio = CarbonoRelatorio(
            tenant_id=tenant_id,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            escopo_1_total=pegada["escopo_1"],
            escopo_2_total=pegada["escopo_2"],
            escopo_3_total=pegada["escopo_3"],
            total_geral=pegada["total"],
            creditos_gerados=creditos_gerados,
            saldo_liquido=pegada["total"] - creditos_gerados
        )
        self.db.add(relatorio)
        self.db.commit()
        self.db.refresh(relatorio)
        return relatorio
