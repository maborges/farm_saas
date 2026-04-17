"""Services consolidados para Sprints 27-33."""

from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, date

from enterprise.models.sprints_27_33 import (
    MRVProjeto, MRVRelatorio,
    ESGIndicador, ESGRelatorio,
    TanqueRede, Arracoamento, Pesagem,
    ConfinamentoLote, RacaoTMR, Cocho,
    Raca, AnimalGenetica, SugestaoAcasalamento,
    ContratoFuturo, HedgeRegistro,
    SensorIoT, SensorLeitura,
    ILPFModulo, ColaboradorApontamento
)


class MRVService:
    """Serviço para MRV (Monitoramento, Reporte, Verificação)."""

    def __init__(self, db: Session):
        self.db = db

    def criar_projeto(self, tenant_id: str, nome: str,
                      metodologia: str, area_ha: float) -> MRVProjeto:
        """Cria projeto MRV."""
        projeto = MRVProjeto(
            tenant_id=tenant_id,
            nome=nome,
            metodologia=metodologia,
            area_ha=area_ha,
            status="ativo"
        )
        self.db.add(projeto)
        self.db.commit()
        self.db.refresh(projeto)
        return projeto

    def gerar_relatorio(self, projeto_id: int,
                       periodo_inicio: date,
                       periodo_fim: date) -> MRVRelatorio:
        """Gera relatório MRV."""
        relatorio = MRVRelatorio(
            tenant_id="tenant",  # Obter do projeto
            projeto_id=projeto_id,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            status="rascunho"
        )
        self.db.add(relatorio)
        self.db.commit()
        return relatorio


class ESGService:
    """Serviço para relatórios ESG."""

    def __init__(self, db: Session):
        self.db = db

    def registrar_indicador(self, tenant_id: str, categoria: str,
                           nome: str, valor: float,
                           periodo: str) -> ESGIndicador:
        """Registra indicador ESG."""
        indicador = ESGIndicador(
            tenant_id=tenant_id,
            categoria=categoria,
            nome=nome,
            valor=valor,
            periodo_referencia=periodo
        )
        self.db.add(indicador)
        self.db.commit()
        return indicador

    def gerar_relatorio(self, tenant_id: str, ano: int) -> ESGRelatorio:
        """Gera relatório ESG anual."""
        # Calcular scores baseado nos indicadores
        relatorio = ESGRelatorio(
            tenant_id=tenant_id,
            ano_referencia=ano,
            status="rascunho"
        )
        self.db.add(relatorio)
        self.db.commit()
        return relatorio


class PisciculturaService:
    """Serviço para gestão de piscicultura."""

    def __init__(self, db: Session):
        self.db = db

    def criar_tanque(self, tenant_id: str, nome: str,
                     volume_m3: float, especie: str,
                     unidade_produtiva_id: int = None) -> TanqueRede:
        """Cria tanque-rede."""
        tanque = TanqueRede(
            tenant_id=tenant_id,
            nome=nome,
            volume_m3=volume_m3,
            especie=especie,
            unidade_produtiva_id=unidade_produtiva_id,
            status="vazio"
        )
        self.db.add(tanque)
        self.db.commit()
        self.db.refresh(tanque)
        return tanque

    def registrar_arracoamento(self, tanque_id: int,
                               quantidade: float,
                               tipo_racao: str,
                               data: date) -> Arracoamento:
        """Registra arraçoamento."""
        arracoamento = Arracoamento(
            tenant_id="tenant",
            tanque_id=tanque_id,
            data=data,
            quantidade_razao=quantidade,
            tipo_racao=tipo_racao
        )
        self.db.add(arracoamento)
        self.db.commit()
        return arracoamento

    def registrar_pesagem(self, tanque_id: int,
                         total_peixes: int,
                         peso_total: float,
                         data: date) -> Pesagem:
        """Registra pesagem."""
        peso_medio = peso_total / total_peixes if total_peixes > 0 else 0
        
        pesagem = Pesagem(
            tenant_id="tenant",
            tanque_id=tanque_id,
            data=data,
            total_peixes=total_peixes,
            peso_total_kg=peso_total,
            peso_medio_g=peso_medio * 1000
        )
        self.db.add(pesagem)
        self.db.commit()
        return pesagem


class ConfinamentoService:
    """Serviço para gestão de confinamento."""

    def __init__(self, db: Session):
        self.db = db

    def criar_lote(self, tenant_id: str, codigo: str,
                   total_animais: int,
                   peso_inicial: float,
                   data_entrada: date,
                   unidade_produtiva_id: int = None) -> ConfinamentoLote:
        """Cria lote de confinamento."""
        lote = ConfinamentoLote(
            tenant_id=tenant_id,
            codigo=codigo,
            total_animais=total_animais,
            peso_inicial_kg=peso_inicial,
            peso_inicial_total_kg=peso_inicial * total_animais,
            data_entrada=data_entrada,
            unidade_produtiva_id=unidade_produtiva_id
        )
        self.db.add(lote)
        self.db.commit()
        self.db.refresh(lote)
        return lote

    def criar_racao_tmr(self, tenant_id: str, nome: str,
                        ingredientes: dict,
                        proteina_bruta: float) -> RacaoTMR:
        """Cria fórmula de ração TMR."""
        racao = RacaoTMR(
            tenant_id=tenant_id,
            nome=nome,
            ingredientes=ingredientes,
            proteina_bruta=proteina_bruta
        )
        self.db.add(racao)
        self.db.commit()
        return racao


class GeneticaService:
    """Serviço para genética animal."""

    def __init__(self, db: Session):
        self.db = db

    def cadastrar_raca(self, nome: str, especie: str,
                       origem: str) -> Raca:
        """Cadastra raça."""
        raca = Raca(
            nome=nome,
            especie=especie,
            origem=origem
        )
        self.db.add(raca)
        self.db.commit()
        return raca

    def sugerir_acasalamento(self, tenant_id: str,
                            matriz_id: int,
                            reprodutor_id: int) -> SugestaoAcasalamento:
        """Sugere acasalamento baseado em DEPs."""
        sugestao = SugestaoAcasalamento(
            tenant_id=tenant_id,
            matriz_id=matriz_id,
            reprodutor_id=reprodutor_id,
            score_complementaridade=0.8  # Calcular baseado em DEPs
        )
        self.db.add(sugestao)
        self.db.commit()
        return sugestao


class HedgingService:
    """Serviço para hedging de commodities."""

    def __init__(self, db: Session):
        self.db = db

    def criar_contrato(self, tenant_id: str, commodity: str,
                      mercado: str, codigo: str,
                      tipo: str, quantidade: float,
                      preco: float) -> ContratoFuturo:
        """Cria contrato futuro."""
        contrato = ContratoFuturo(
            tenant_id=tenant_id,
            commodity=commodity,
            mercado=mercado,
            codigo_contrato=codigo,
            tipo_posicao=tipo,
            quantidade=quantidade,
            preco_contratado=preco
        )
        self.db.add(contrato)
        self.db.commit()
        return contrato

    def registrar_hedge(self, tenant_id: str,
                       contrato_id: int,
                       tipo: str,
                       quantidade: float,
                       preco: float,
                       data: date) -> HedgeRegistro:
        """Registra operação de hedge."""
        registro = HedgeRegistro(
            tenant_id=tenant_id,
            contrato_id=contrato_id,
            tipo=tipo,
            quantidade=quantidade,
            preco=preco,
            data_operacao=data
        )
        self.db.add(registro)
        self.db.commit()
        return registro


class IoTService:
    """Serviço para sensores IoT."""

    def __init__(self, db: Session):
        self.db = db

    def cadastrar_sensor(self, tenant_id: str, nome: str,
                        tipo: str, protocolo: str,
                        unidade_produtiva_id: int = None) -> SensorIoT:
        """Cadastra sensor IoT."""
        sensor = SensorIoT(
            tenant_id=tenant_id,
            nome=nome,
            tipo=tipo,
            protocolo=protocolo,
            unidade_produtiva_id=unidade_produtiva_id
        )
        self.db.add(sensor)
        self.db.commit()
        return sensor

    def registrar_leitura(self, sensor_id: int,
                         valor: float,
                         unidade: str) -> SensorLeitura:
        """Registra leitura de sensor."""
        leitura = SensorLeitura(
            sensor_id=sensor_id,
            valor=valor,
            unidade=unidade,
            timestamp=datetime.utcnow()
        )
        self.db.add(leitura)
        self.db.commit()
        return leitura


class ILPFService:
    """Serviço para ILPF."""

    def __init__(self, db: Session):
        self.db = db

    def criar_modulo(self, tenant_id: str, nome: str,
                    tipo_ilpf: str, area_ha: float,
                    cultura: str,
                    especie_florestal: str,
                    unidade_produtiva_id: int = None) -> ILPFModulo:
        """Cria módulo ILPF."""
        modulo = ILPFModulo(
            tenant_id=tenant_id,
            nome=nome,
            tipo_ilpf=tipo_ilpf,
            area_ha=area_ha,
            cultura=cultura,
            especie_florestal=especie_florestal,
            unidade_produtiva_id=unidade_produtiva_id
        )
        self.db.add(modulo)
        self.db.commit()
        return modulo


class ColaboradorService:
    """Serviço para app de colaboradores."""

    def __init__(self, db: Session):
        self.db = db

    def registrar_apontamento(self, tenant_id: str,
                            colaborador_id: int,
                            data: date,
                            horas: float,
                            atividade: str) -> ColaboradorApontamento:
        """Registra apontamento de horas."""
        apontamento = ColaboradorApontamento(
            tenant_id=tenant_id,
            colaborador_id=colaborador_id,
            data=data,
            horas_trabalhadas=horas,
            atividade=atividade
        )
        self.db.add(apontamento)
        self.db.commit()
        return apontamento
