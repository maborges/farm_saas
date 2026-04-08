"""
Arrendamentos Rurais - Service Layer

Implementa regras de negócio para gestão de contratos de arrendamento e parceria:
- Geração automática de parcelas
- Integração com módulo Financeiro
- Reajustes contratuais (IGP-M, IPCA)
- Validações legais (Lei 4.504/1964)
- Controle de inadimplência
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Tuple, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
import uuid
from dateutil.relativedelta import relativedelta

from imoveis.models.imovel import (
    ContratoArrendamento, ParcelaArrendamento, HistoricoReajuste,
    ImovelRural, TipoContrato, TipoArrendatario, ValorModalidade,
    Periodicidade, StatusContrato, StatusParcela
)
from core.models.auth import Usuario


class ArrendamentoService:
    """
    Service para gestão de Arrendamentos Rurais.
    
    Responsabilidades:
    - Criação de contratos com validações legais
    - Geração automática de parcelas
    - Reajustes contratuais anuais
    - Integração com módulo Financeiro (lancamentos)
    - Rescisão contratual
    - Controle de inadimplência
    
    Conformidade: Lei 4.504/1964 (Estatuto da Terra)
    """
    
    # Prazos mínimos legais (Lei 4.504/1964, Art. 95)
    PRAZO_MINIMO_AGRICOLA = 3  # anos
    PRAZO_MINIMO_PECUARIO = 3  # anos
    PRAZO_MINIMO_MISTO = 5  # anos
    
    # Valor máximo do arrendamento (Lei 4.504/1964, Art. 93)
    VALOR_MAXIMO_PERCENTUAL = Decimal('0.15')  # 15% do valor cadastral anual
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_contrato_by_id(
        self,
        contrato_id: uuid.UUID,
        tenant_id: uuid.UUID
    ) -> Optional[ContratoArrendamento]:
        """Busca contrato por ID com tenant isolation."""
        result = await self.session.execute(
            select(ContratoArrendamento)
            .where(
                and_(
                    ContratoArrendamento.id == contrato_id,
                    ContratoArrendamento.tenant_id == tenant_id,
                    ContratoArrendamento.deleted_at.is_(None)
                )
            )
            .options(
                selectinload(ContratoArrendamento.imovel),
                selectinload(ContratoArrendamento.parcelas),
                selectinload(ContratoArrendamento.reajustes)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_contratos_by_imovel(
        self,
        imovel_id: uuid.UUID,
        tenant_id: uuid.UUID,
        apenas_ativos: bool = True
    ) -> List[ContratoArrendamento]:
        """Busca contratos de um imóvel."""
        conditions = [
            ContratoArrendamento.imovel_id == imovel_id,
            ContratoArrendamento.tenant_id == tenant_id,
            ContratoArrendamento.deleted_at.is_(None)
        ]
        
        if apenas_ativos:
            conditions.append(ContratoArrendamento.status == StatusContrato.ATIVO)
        
        result = await self.session.execute(
            select(ContratoArrendamento)
            .where(and_(*conditions))
            .order_by(ContratoArrendamento.data_inicio.desc())
        )
        return list(result.scalars().all())
    
    def validar_prazo_minimo(
        self,
        data_inicio: date,
        data_fim: date,
        tipo_contrato: TipoContrato = TipoContrato.ARRENDAMENTO
    ) -> Tuple[bool, str]:
        """
        Valida prazo mínimo conforme Lei 4.504/1964.
        
        Returns:
            tuple[bool, str]: (valido, mensagem)
        """
        anos_contrato = (data_fim.year - data_inicio.year)
        
        # Ajusta se ainda não completou aniversário
        if (data_fim.month, data_fim.day) < (data_inicio.month, data_inicio.day):
            anos_contrato -= 1
        
        prazo_minimo = self.PRAZO_MINIMO_AGRICOLA  # Assume agrícola como padrão
        
        if anos_contrato < prazo_minimo:
            return (
                False,
                f"Prazo mínimo de {prazo_minimo} anos não atendido. Contrato: {anos_contrato} anos"
            )
        
        return True, f"Prazo de {anos_contrato} anos está dentro da lei"
    
    async def validar_ccir_ativo(
        self,
        imovel_id: uuid.UUID,
        tenant_id: uuid.UUID
    ) -> Tuple[bool, str]:
        """
        Valida se CCIR do imóvel está ativo.
        
        CCIR vencido bloqueia criação de contrato.
        """
        from imoveis.models.imovel import DocumentoLegal, TipoDocumento, StatusDocumento
        
        result = await self.session.execute(
            select(DocumentoLegal)
            .where(
                and_(
                    DocumentoLegal.imovel_id == imovel_id,
                    DocumentoLegal.tipo == TipoDocumento.CCIR,
                    DocumentoLegal.status == StatusDocumento.ATIVO,
                    DocumentoLegal.deleted_at.is_(None)
                )
            )
            .order_by(DocumentoLegal.data_vencimento.desc())
            .limit(1)
        )
        
        ccir = result.scalar_one_or_none()
        
        if not ccir:
            return False, "Imóvel não possui CCIR cadastrado"
        
        if ccir.data_vencimento and ccir.data_vencimento < date.today():
            dias_vencido = (date.today() - ccir.data_vencimento).days
            return (
                False,
                f"CCIR vencido há {dias_vencido} dias em {ccir.data_vencimento}"
            )
        
        return True, "CCIR ativo e válido"
    
    def calcular_parcelas(
        self,
        valor_total: Decimal,
        periodicidade: Periodicidade,
        data_inicio: date,
        data_fim: date,
        dia_vencimento: int = 10
    ) -> List[Dict]:
        """
        Calcula parcelas do arrendamento.
        
        Args:
            valor_total: Valor anual do arrendamento
            periodicidade: Frequência de pagamento
            data_inicio: Início do contrato
            data_fim: Fim do contrato
            dia_vencimento: Dia do mês para vencimento (1-28)
        
        Returns:
            list[dict]: Lista de parcelas com data_vencimento e valor
        """
        parcelas = []
        
        # Determina número de parcelas por ano
        parcelas_por_ano = {
            Periodicidade.MENSAL: 12,
            Periodicidade.SEMESTRAL: 2,
            Periodicidade.ANUAL: 1,
            Periodicidade.SAFRA: 1  # Safra considera uma parcela por ano agrícola
        }.get(periodicidade, 12)
        
        # Calcula valor da parcela
        valor_parcela = valor_total / parcelas_por_ano
        
        # Gera datas de vencimento
        data_atual = data_inicio
        numero_parcela = 1
        
        while data_atual <= data_fim:
            # Ajusta para dia de vencimento
            try:
                data_vencimento = data_atual.replace(day=dia_vencimento)
            except ValueError:
                # Se dia não existe no mês, usa último dia
                if data_atual.month in [4, 6, 9, 11]:
                    data_vencimento = data_atual.replace(day=30)
                elif data_atual.month == 2:
                    data_vencimento = data_atual.replace(day=28)
                else:
                    data_vencimento = data_atual.replace(day=31)
            
            # Garante que vencimento seja após início
            if data_vencimento < data_inicio:
                data_vencimento = (data_vencimento + relativedelta(months=1))
            
            parcelas.append({
                "numero_parcela": numero_parcela,
                "data_vencimento": data_vencimento,
                "valor_centavos": int(valor_parcela * 100),
                "status": StatusParcela.PREVISTA
            })
            
            numero_parcela += 1
            
            # Avança para próxima parcela
            if periodicidade == Periodicidade.MENSAL:
                data_atual = data_atual + relativedelta(months=1)
            elif periodicidade == Periodicidade.SEMESTRAL:
                data_atual = data_atual + relativedelta(months=6)
            elif periodicidade == Periodicidade.ANUAL:
                data_atual = data_atual + relativedelta(years=1)
            elif periodicidade == Periodicidade.SAFRA:
                data_atual = data_atual + relativedelta(years=1)
        
        return parcelas
    
    async def criar_contrato(
        self,
        tenant_id: uuid.UUID,
        imovel_id: uuid.UUID,
        fazenda_id: uuid.UUID,
        tipo: TipoContrato,
        arrendatario_tipo: TipoArrendatario,
        area_arrendada_ha: Decimal,
        valor_modalidade: ValorModalidade,
        valor: Decimal,
        periodicidade: Periodicidade,
        data_inicio: date,
        data_fim: date,
        dia_vencimento: int = 10,
        indice_reajuste: Optional[str] = None,
        data_reajuste_anual: Optional[date] = None,
        commodity_referencia: Optional[str] = None,
        arrendatario_pessoa_id: Optional[uuid.UUID] = None,
        arrendatario_fazenda_id: Optional[uuid.UUID] = None,
        path_contrato_pdf: Optional[str] = None,
        registro_cartorio: Optional[str] = None,
        clausulas_observacoes: Optional[str] = None,
        created_by: Optional[uuid.UUID] = None
    ) -> Tuple[ContratoArrendamento, List[str]]:
        """
        Cria contrato de arrendamento com validações e geração de parcelas.
        
        Returns:
            tuple[ContratoArrendamento, List[str]]: (contrato, alertas)
        """
        alertas = []
        
        # Validações legais
        valido, msg = self.validar_prazo_minimo(data_inicio, data_fim, tipo)
        if not valido:
            alertas.append(f"ALERTA LEGAL: {msg}")
        
        # Valida CCIR do imóvel
        valido, msg = await self.validar_ccir_ativo(imovel_id, tenant_id)
        if not valido:
            raise ValueError(f"CCIR irregular: {msg}")
        
        # Valida área arrendada vs área do imóvel
        imovel = await self.session.get(ImovelRural, imovel_id)
        if not imovel:
            raise ValueError("Imóvel não encontrado")
        
        if area_arrendada_ha > imovel.area_total_ha:
            alertas.append(
                f"ALERTA: Área arrendada ({area_arrendada_ha:.2f} ha) excede área do imóvel ({imovel.area_total_ha:.2f} ha)"
            )
        
        # Valida valor máximo (15% do valor cadastral)
        # Nota: Requer valor cadastral do imóvel - implementar quando disponível
        # if valor_modalidade == ValorModalidade.FIXO_BRL:
        #     valor_anual = valor * periodicidade  # Simplificado
        #     if valor_anual > imovel.valor_cadastral * self.VALOR_MAXIMO_PERCENTUAL:
        #         alertas.append("ALERTA: Valor excede 15% do valor cadastral (Lei 4.504/1964)")
        
        # Cria contrato
        contrato = ContratoArrendamento(
            tenant_id=tenant_id,
            imovel_id=imovel_id,
            fazenda_id=fazenda_id,
            tipo=tipo,
            arrendatario_tipo=arrendatario_tipo,
            arrendatario_pessoa_id=arrendatario_pessoa_id,
            arrendatario_fazenda_id=arrendatario_fazenda_id,
            area_arrendada_ha=area_arrendada_ha,
            valor_modalidade=valor_modalidade,
            valor=valor,
            commodity_referencia=commodity_referencia,
            periodicidade=periodicidade,
            data_inicio=data_inicio,
            data_fim=data_fim,
            dia_vencimento=dia_vencimento,
            indice_reajuste=indice_reajuste,
            data_reajuste_anual=data_reajuste_anual,
            status=StatusContrato.ATIVO,
            path_contrato_pdf=path_contrato_pdf,
            registro_cartorio=registro_cartorio,
            clausulas_observacoes=clausulas_observacoes,
            created_by=created_by
        )
        
        self.session.add(contrato)
        await self.session.flush()
        
        # Calcula e gera parcelas
        # Para arrendamento em BRL: valor = valor anual
        # Para sacas/ha: valor_total = valor * area_arrendada_ha
        if valor_modalidade == ValorModalidade.FIXO_SACAS:
            valor_total = valor * area_arrendada_ha  # Em sacas
        else:
            valor_total = valor  # Em BRL
        
        parcelas_calculadas = self.calcular_parcelas(
            valor_total=valor_total,
            periodicidade=periodicidade,
            data_inicio=data_inicio,
            data_fim=data_fim,
            dia_vencimento=dia_vencimento
        )
        
        # Cria parcelas
        for parcela_data in parcelas_calculadas:
            parcela = ParcelaArrendamento(
                contrato_id=contrato.id,
                numero_parcela=parcela_data["numero_parcela"],
                data_vencimento=parcela_data["data_vencimento"],
                valor_centavos=parcela_data["valor_centavos"],
                status=parcela_data["status"]
            )
            
            if valor_modalidade == ValorModalidade.FIXO_SACAS:
                parcela.valor_sacas = Decimal(parcela_data["valor_centavos"]) / 100
            
            self.session.add(parcela)
        
        alertas.append(f"Contrato criado com {len(parcelas_calculadas)} parcelas geradas")
        
        return contrato, alertas
    
    async def aplicar_reajuste(
        self,
        contrato_id: uuid.UUID,
        tenant_id: uuid.UUID,
        indice_nome: str,
        indice_valor: Decimal,
        usuario_id: uuid.UUID
    ) -> Tuple[ContratoArrendamento, List[str]]:
        """
        Aplica reajuste anual ao contrato.
        
        Args:
            contrato_id: ID do contrato
            tenant_id: ID do tenant
            indice_nome: Nome do índice (IGP-M, IPCA, etc.)
            indice_valor: Valor do índice (ex: 1.0450 para +4.5%)
            usuario_id: ID do usuário aplicando reajuste
        
        Returns:
            tuple[ContratoArrendamento, List[str]]: (contrato, alertas)
        """
        contrato = await self.get_contrato_by_id(contrato_id, tenant_id)
        
        if not contrato:
            raise ValueError("Contrato não encontrado")
        
        if contrato.status != StatusContrato.ATIVO:
            raise ValueError(f"Contrato está {contrato.status.value}, não pode ser reajustado")
        
        valor_anterior = contrato.valor
        valor_novo = valor_anterior * indice_valor
        
        # Registra histórico
        reajuste = HistoricoReajuste(
            contrato_id=contrato.id,
            data_reajuste=date.today(),
            indice_nome=indice_nome,
            indice_valor=indice_valor,
            valor_anterior=valor_anterior,
            valor_novo=valor_novo,
            created_by=usuario_id
        )
        self.session.add(reajuste)
        
        # Atualiza contrato
        contrato.valor = valor_novo
        
        # Atualiza parcelas futuras
        hoje = date.today()
        parcelas_futuras = await self.session.execute(
            select(ParcelaArrendamento)
            .where(
                and_(
                    ParcelaArrendamento.contrato_id == contrato.id,
                    ParcelaArrendamento.data_vencimento > hoje,
                    ParcelaArrendamento.status == StatusParcela.PREVISTA
                )
            )
        )
        
        parcelas_atualizadas = 0
        for parcela in parcelas_futuras.scalars().all():
            # Recalcula valor da parcela
            if contrato.valor_modalidade == ValorModalidade.FIXO_SACAS:
                parcela.valor_sacas = (parcela.valor_sacas or Decimal('0')) * indice_valor
                parcela.valor_centavos = int(parcela.valor_sacas * 100)
            else:
                parcela.valor_centavos = int(parcela.valor_centavos * indice_valor)
            
            parcela.indice_aplicado = indice_valor
            parcelas_atualizadas += 1
        
        alertas = [
            f"Reajuste de {indice_nome} ({indice_valor:.4f}) aplicado",
            f"Valor atualizado: R$ {valor_anterior:.2f} → R$ {valor_novo:.2f}",
            f"{parcelas_atualizadas} parcelas futuras atualizadas"
        ]
        
        return contrato, alertas
    
    async def rescindir_contrato(
        self,
        contrato_id: uuid.UUID,
        tenant_id: uuid.UUID,
        motivo: str,
        data_rescisao: date,
        usuario_id: uuid.UUID
    ) -> Tuple[ContratoArrendamento, List[str]]:
        """
        Rescinde contrato antecipadamente.
        
        Cancela parcelas futuras e registra motivo.
        """
        contrato = await self.get_contrato_by_id(contrato_id, tenant_id)
        
        if not contrato:
            raise ValueError("Contrato não encontrado")
        
        contrato.status = StatusContrato.RESCINDIDO
        contrato.motivo_rescisao = motivo
        
        # Cancela parcelas futuras
        hoje = date.today()
        parcelas_futuras = await self.session.execute(
            select(ParcelaArrendamento)
            .where(
                and_(
                    ParcelaArrendamento.contrato_id == contrato.id,
                    ParcelaArrendamento.data_vencimento > hoje,
                    ParcelaArrendamento.status == StatusParcela.PREVISTA
                )
            )
        )
        
        parcelas_canceladas = 0
        for parcela in parcelas_futuras.scalars().all():
            parcela.status = StatusParcela.CANCELADA
            parcelas_canceladas += 1
        
        alertas = [
            f"Contrato rescindido em {data_rescisao}",
            f"Motivo: {motivo}",
            f"{parcelas_canceladas} parcelas futuras canceladas"
        ]
        
        return contrato, alertas
    
    async def get_parcelas_vencidas(
        self,
        tenant_id: uuid.UUID,
        dias_atraso: int = 1
    ) -> List[ParcelaArrendamento]:
        """Busca parcelas vencidas há X dias ou mais."""
        hoje = date.today()
        limite = hoje - timedelta(days=dias_atraso)
        
        result = await self.session.execute(
            select(ParcelaArrendamento)
            .join(ContratoArrendamento)
            .where(
                and_(
                    ContratoArrendamento.tenant_id == tenant_id,
                    ParcelaArrendamento.data_vencimento < limite,
                    ParcelaArrendamento.status == StatusParcela.PREVISTA,
                    ContratoArrendamento.deleted_at.is_(None)
                )
            )
            .options(selectinload(ParcelaArrendamento.contrato))
            .order_by(ParcelaArrendamento.data_vencimento.asc())
        )
        
        return list(result.scalars().all())
    
    async def get_resumo_contrato(
        self,
        contrato_id: uuid.UUID,
        tenant_id: uuid.UUID
    ) -> dict:
        """
        Retorna resumo completo do contrato.
        
        Includes: valor total, parcelas pagas, pendentes, inadimplência
        """
        contrato = await self.get_contrato_by_id(contrato_id, tenant_id)
        
        if not contrato:
            raise ValueError("Contrato não encontrado")
        
        # Busca parcelas
        parcelas = await self.session.execute(
            select(ParcelaArrendamento)
            .where(ParcelaArrendamento.contrato_id == contrato.id)
            .order_by(ParcelaArrendamento.numero_parcela)
        )
        parcelas_list = list(parcelas.scalars().all())
        
        # Calcula totais
        total_parcelas = len(parcelas_list)
        parcelas_pagas = sum(1 for p in parcelas_list if p.status == StatusParcela.PAGA)
        parcelas_pendentes = sum(1 for p in parcelas_list if p.status == StatusParcela.PREVISTA)
        parcelas_vencidas = sum(
            1 for p in parcelas_list
            if p.status == StatusParcela.PREVISTA and p.data_vencimento < date.today()
        )
        
        valor_total = sum(p.valor_centavos for p in parcelas_list)
        valor_pago = sum(p.valor_centavos for p in parcelas_list if p.status == StatusParcela.PAGA)
        valor_pendente = sum(p.valor_centavos for p in parcelas_list if p.status == StatusParcela.PREVISTA)
        
        return {
            "contrato": contrato,
            "total_parcelas": total_parcelas,
            "parcelas_pagas": parcelas_pagas,
            "parcelas_pendentes": parcelas_pendentes,
            "parcelas_vencidas": parcelas_vencidas,
            "valor_total_centavos": valor_total,
            "valor_pago_centavos": valor_pago,
            "valor_pendente_centavos": valor_pendente,
            "percentual_pago": (valor_pago / valor_total * 100) if valor_total > 0 else 0
        }
