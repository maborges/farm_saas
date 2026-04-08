"""
Imóveis Rurais - Service Layer

Implementa regras de negócio para gestão de imóveis rurais:
- Validação de NIRF (algoritmo Receita Federal)
- Validação de CAR (formato por estado)
- Consistência de áreas (imóvel vs talhões)
- Situação cadastral automática
- Gestão de múltiplos imóveis por fazenda
"""
import uuid
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from imoveis.models.imovel import (
    ImovelRural, Cartorio, MatriculaImovelRural, Benfeitoria,
    TipoImovel, SituacaoImovel, TipoDocumento, StatusDocumento
)
from core.models.fazenda import Fazenda
from core.models.auth import Usuario


class NIRFValidator:
    """
    Validador de NIRF (Número do Imóvel na Receita Federal).
    
    Formato: 12 dígitos numéricos + 1 dígito verificador
    Algoritmo: Módulo 11 conforme IN RFB 1.902/2019
    """
    
    @staticmethod
    def limpar_nirf(nirf: str) -> str:
        """Remove caracteres não numéricos do NIRF."""
        return ''.join(c for c in nirf if c.isdigit())
    
    @staticmethod
    def validar(nirf: str) -> tuple[bool, str]:
        """
        Valida NIRF completo (12 dígitos + DV).
        
        Returns:
            tuple[bool, str]: (valido, mensagem)
        """
        nirf_limpo = NIRFValidator.limpar_nirf(nirf)
        
        # Valida tamanho
        if len(nirf_limpo) != 13:
            return False, f"NIRF deve ter 13 dígitos (12 + DV). Encontrado: {len(nirf_limpo)}"
        
        # Separa corpo e DV
        corpo = nirf_limpo[:12]
        dv_informado = int(nirf_limpo[12])
        
        # Calcula DV
        dv_calculado = NIRFValidator._calcular_dv(corpo)
        
        if dv_calculado != dv_informado:
            return False, f"Dígito verificador inválido. Esperado: {dv_calculado}, Informado: {dv_informado}"
        
        return True, "NIRF válido"
    
    @staticmethod
    def _calcular_dv(corpo: str) -> int:
        """
        Calcula dígito verificador usando Módulo 11.
        
        Pesos: 2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5 (da direita para esquerda)
        """
        pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]  # Invertidos para esquerda-direita
        
        soma = 0
        for i, digito in enumerate(corpo):
            soma += int(digito) * pesos[i]
        
        resto = soma % 11
        dv = 11 - resto
        
        if dv >= 10:
            dv = 0
        
        return dv
    
    @staticmethod
    def formatar(nirf: str) -> str:
        """Formata NIRF como XXX.XXX.XXX-DVV."""
        nirf_limpo = NIRFValidator.limpar_nirf(nirf)
        if len(nirf_limpo) != 13:
            return nirf
        
        return f"{nirf_limpo[:3]}.{nirf_limpo[3:6]}.{nirf_limpo[6:9]}-{nirf_limpo[9:]}"


class CARValidator:
    """
    Validador de CAR (Cadastro Ambiental Rural).
    
    Formato: 2 letras (UF) + 12 dígitos numéricos
    Conforme Manual Técnico do SICAR
    """
    
    UFS_VALIDAS = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]
    
    @staticmethod
    def limpar_car(car: str) -> str:
        """Remove caracteres não alfanuméricos do CAR."""
        return ''.join(c for c in car if c.isalnum()).upper()
    
    @staticmethod
    def validar(car: str) -> tuple[bool, str]:
        """
        Valida formato do CAR.
        
        Returns:
            tuple[bool, str]: (valido, mensagem)
        """
        if not car:
            return True, "CAR não informado (opcional)"
        
        car_limpo = CARValidator.limpar_car(car)
        
        # Valida tamanho
        if len(car_limpo) != 14:
            return False, f"CAR deve ter 14 caracteres (2 UF + 12 dígitos). Encontrado: {len(car_limpo)}"
        
        # Valida UF
        uf = car_limpo[:2]
        if uf not in CARValidator.UFS_VALIDAS:
            return False, f"UF '{uf}' inválida. UFs válidas: {', '.join(CARValidator.UFS_VALIDAS)}"
        
        # Valida dígitos numéricos
        numeros = car_limpo[2:]
        if not numeros.isdigit():
            return False, "CAR deve conter apenas dígitos após a UF"
        
        return True, "CAR válido"


class ImovelService:
    """
    Service para gestão de Imóveis Rurais.
    
    Responsabilidades:
    - CRUD de imóveis com validações
    - Validação de NIRF, CAR, CCIR
    - Consistência de áreas (imóvel vs talhões)
    - Cálculo de situação cadastral
    - Gestão de múltiplos imóveis por fazenda
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.nirf_validator = NIRFValidator()
        self.car_validator = CARValidator()
    
    async def get_imovel_by_id(
        self, 
        imovel_id: uuid.UUID, 
        tenant_id: uuid.UUID
    ) -> Optional[ImovelRural]:
        """Busca imóvel por ID com tenant isolation."""
        result = await self.session.execute(
            select(ImovelRural)
            .where(
                and_(
                    ImovelRural.id == imovel_id,
                    ImovelRural.tenant_id == tenant_id,
                    ImovelRural.deleted_at.is_(None)
                )
            )
            .options(
                selectinload(ImovelRural.cartorio),
                selectinload(ImovelRural.documentos),
                selectinload(ImovelRural.benfeitorias)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_imoveis_by_fazenda(
        self,
        fazenda_id: uuid.UUID,
        tenant_id: uuid.UUID
    ) -> list[ImovelRural]:
        """Busca todos imóveis de uma fazenda."""
        result = await self.session.execute(
            select(ImovelRural)
            .where(
                and_(
                    ImovelRural.fazenda_id == fazenda_id,
                    ImovelRural.tenant_id == tenant_id,
                    ImovelRural.deleted_at.is_(None)
                )
            )
            .order_by(ImovelRural.nome)
        )
        return list(result.scalars().all())
    
    async def validar_nirf_unico(self, nirf: str, tenant_id: uuid.UUID, imovel_id: Optional[uuid.UUID] = None) -> tuple[bool, str]:
        """
        Valida unicidade de NIRF no tenant.
        
        Args:
            nirf: NIRF a validar
            tenant_id: ID do tenant
            imovel_id: ID do imóvel (para exclusão de si mesmo na atualização)
        
        Returns:
            tuple[bool, str]: (valido, mensagem)
        """
        if not nirf:
            return True, "NIRF não informado (opcional)"
        
        # Valida formato
        valido, msg = self.nirf_validator.validar(nirf)
        if not valido:
            return False, msg
        
        # Valida unicidade
        stmt = select(ImovelRural).where(
            and_(
                ImovelRural.tenant_id == tenant_id,
                ImovelRural.nirf == nirf,
                ImovelRural.deleted_at.is_(None)
            )
        )
        
        if imovel_id:
            stmt = stmt.where(ImovelRural.id != imovel_id)
        
        result = await self.session.execute(stmt)
        existente = result.scalar_one_or_none()
        
        if existente:
            return False, f"NIRF já cadastrado no imóvel '{existente.nome}'"
        
        return True, "NIRF disponível"
    
    async def validar_area_consistente(
        self,
        area_imovel: Decimal,
        fazenda_id: uuid.UUID,
        imovel_id: Optional[uuid.UUID] = None
    ) -> tuple[bool, str, Optional[Decimal]]:
        """
        Valida consistência da área do imóvel com a fazenda.
        
        Args:
            area_imovel: Área do imóvel em hectares
            fazenda_id: ID da fazenda
            imovel_id: ID do imóvel (para exclusão de si mesmo)
        
        Returns:
            tuple[bool, str, Decimal]: (valido, mensagem, area_fazenda)
        """
        # Busca área da fazenda
        fazenda = await self.session.get(Fazenda, fazenda_id)
        if not fazenda:
            return False, "Fazenda não encontrada", None
        
        area_fazenda = Decimal(str(fazenda.area_total_ha))
        
        # Soma áreas de outros imóveis da fazenda
        stmt = select(func.sum(ImovelRural.area_total_ha)).where(
            and_(
                ImovelRural.fazenda_id == fazenda_id,
                ImovelRural.id != imovel_id,
                ImovelRural.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        area_outros_imoveis = result.scalar() or Decimal('0')
        
        area_total_imoveis = area_imovel + area_outros_imoveis
        
        # Tolerância de 10% para múltiplos imóveis
        limite = area_fazenda * Decimal('1.10')
        
        if area_total_imoveis > limite:
            return (
                False,
                f"Soma das áreas dos imóveis ({area_total_imoveis:.2f} ha) excede área da fazenda ({area_fazenda:.2f} ha) em mais de 10%",
                area_fazenda
            )
        
        # Alerta se divergência > 5%
        if area_imovel > area_fazenda * Decimal('1.05'):
            return (
                True,  # Não bloqueia, apenas alerta
                f"ALERTA: Área do imóvel ({area_imovel:.2f} ha) é {((area_imovel/area_fazenda - 1) * 100):.1f}% maior que área da fazenda ({area_fazenda:.2f} ha)",
                area_fazenda
            )
        
        return True, "Área consistente", area_fazenda
    
    async def calcular_situacao_cadastral(self, imovel: ImovelRural) -> SituacaoImovel:
        """
        Calcula situação cadastral baseada em documentos obrigatórios.
        
        REGULAR: Possui NIRF, CAR e CCIR válidos
        PENDENTE: Falta algum documento
        IRREGULAR: Documentos vencidos há mais de 90 dias
        """
        from datetime import date, timedelta
        
        # Busca documentos ativos
        stmt = select(DocumentoLegal).where(
            and_(
                DocumentoLegal.imovel_id == imovel.id,
                DocumentoLegal.status == StatusDocumento.ATIVO,
                DocumentoLegal.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        documentos = list(result.scalars().all())
        
        # Verifica documentos obrigatórios
        tem_nirf = bool(imovel.nirf)
        tem_car = bool(imovel.car_numero)
        tem_ccir = any(d.tipo == TipoDocumento.CCIR for d in documentos)
        
        # Verifica vencimentos
        hoje = date.today()
        documentos_vencidos = []
        
        for doc in documentos:
            if doc.data_vencimento and doc.data_vencimento < hoje:
                dias_vencido = (hoje - doc.data_vencimento).days
                if dias_vencido > 90:
                    documentos_vencidos.append(doc.tipo.value)
        
        # Determina situação
        if documentos_vencidos:
            return SituacaoImovel.IRREGULAR
        
        if tem_nirf and tem_car and tem_ccir:
            return SituacaoImovel.REGULAR
        
        return SituacaoImovel.PENDENTE
    
    async def criar_imovel(
        self,
        tenant_id: uuid.UUID,
        fazenda_id: uuid.UUID,
        nome: str,
        municipio: str,
        uf: str,
        area_total_ha: Decimal,
        nirf: Optional[str] = None,
        car_numero: Optional[str] = None,
        ccir_numero: Optional[str] = None,
        cartorio_id: Optional[uuid.UUID] = None,
        numero_matricula: Optional[str] = None,
        tipo: TipoImovel = TipoImovel.RURAL,
        observacao: Optional[str] = None,
        created_by: Optional[uuid.UUID] = None
    ) -> tuple[ImovelRural, list[str]]:
        """
        Cria novo imóvel rural com validações.
        
        Returns:
            tuple[ImovelRural, list[str]]: (imovel, alertas)
        """
        alertas = []
        
        # Valida NIRF
        if nirf:
            valido, msg = await self.validar_nirf_unico(nirf, tenant_id)
            if not valido:
                raise ValueError(msg)
        
        # Valida CAR
        if car_numero:
            valido, msg = self.car_validator.validar(car_numero)
            if not valido:
                raise ValueError(msg)
        
        # Valida área
        valido, msg, area_fazenda = await self.validar_area_consistente(
            area_total_ha, fazenda_id
        )
        if not valido:
            raise ValueError(msg)
        if "ALERTA" in msg:
            alertas.append(msg)
        
        # Determina situação inicial
        situacao = SituacaoImovel.PENDENTE
        if nirf and car_numero:
            situacao = SituacaoImovel.REGULAR
        
        # Cria imóvel
        imovel = ImovelRural(
            tenant_id=tenant_id,
            fazenda_id=fazenda_id,
            nome=nome,
            municipio=municipio,
            uf=uf,
            area_total_ha=area_total_ha,
            nirf=nirf,
            car_numero=car_numero,
            ccir_numero=ccir_numero,
            cartorio_id=cartorio_id,
            numero_matricula=numero_matricula,
            tipo=tipo,
            situacao=situacao,
            observacao=observacao,
            created_by=created_by
        )
        
        self.session.add(imovel)
        await self.session.flush()  # Para gerar o ID
        
        return imovel, alertas
    
    async def atualizar_imovel(
        self,
        imovel: ImovelRural,
        dados: dict,
        usuario_id: uuid.UUID
    ) -> tuple[ImovelRural, list[str]]:
        """
        Atualiza imóvel com validações.
        
        Args:
            imovel: Imóvel a atualizar
            dados: Dicionário com campos a atualizar
            usuario_id: ID do usuário fazendo a atualização
        
        Returns:
            tuple[ImovelRural, list[str]]: (imovel, alertas)
        """
        alertas = []
        
        # Valida NIRF se alterado
        if 'nirf' in dados and dados['nirf'] != imovel.nirf:
            valido, msg = await self.validar_nirf_unico(
                dados['nirf'], imovel.tenant_id, imovel.id
            )
            if not valido:
                raise ValueError(msg)
        
        # Valida área se alterada
        if 'area_total_ha' in dados and dados['area_total_ha'] != imovel.area_total_ha:
            # Exige justificativa
            if 'motivo_alteracao_area' not in dados or not dados['motivo_alteracao_area']:
                raise ValueError("Alteração de área exige justificativa no campo 'motivo_alteracao_area'")
            
            valido, msg, area_fazenda = await self.validar_area_consistente(
                dados['area_total_ha'], imovel.fazenda_id, imovel.id
            )
            if not valido:
                raise ValueError(msg)
            if "ALERTA" in msg:
                alertas.append(msg)
        
        # Atualiza campos
        for campo, valor in dados.items():
            if hasattr(imovel, campo):
                setattr(imovel, campo, valor)
        
        # Atualiza situação cadastral
        imovel.situacao = await self.calcular_situacao_cadastral(imovel)
        imovel.updated_at = func.now()
        
        return imovel, alertas
    
    async def excluir_imovel(self, imovel: ImovelRural) -> bool:
        """
        Exclusão lógica de imóvel.
        
        Só permite exclusão se não houver documentos ou contratos ativos.
        """
        from imoveis.models.imovel import ContratoArrendamento, StatusContrato
        from sqlalchemy import and_
        
        # Verifica documentos ativos
        stmt = select(DocumentoLegal).where(
            and_(
                DocumentoLegal.imovel_id == imovel.id,
                DocumentoLegal.status == StatusDocumento.ATIVO,
                DocumentoLegal.deleted_at.is_(None)
            )
        ).limit(1)
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError("Imóvel possui documentos ativos. Exclua ou cancele os documentos primeiro.")
        
        # Verifica contratos ativos
        stmt = select(ContratoArrendamento).where(
            and_(
                ContratoArrendamento.imovel_id == imovel.id,
                ContratoArrendamento.status == StatusContrato.ATIVO,
                ContratoArrendamento.deleted_at.is_(None)
            )
        ).limit(1)
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError("Imóvel possui contratos de arrendamento ativos.")
        
        # Exclusão lógica
        imovel.deleted_at = func.now()
        return True
    
    async def get_cartorio_by_id(
        self,
        cartorio_id: uuid.UUID,
        tenant_id: uuid.UUID
    ) -> Optional[Cartorio]:
        """Busca cartório por ID."""
        return await self.session.get(Cartorio, cartorio_id)
    
    async def get_cartorios(self, tenant_id: uuid.UUID) -> list[Cartorio]:
        """Lista todos cartórios do tenant."""
        result = await self.session.execute(
            select(Cartorio)
            .where(Cartorio.tenant_id == tenant_id)
            .order_by(Cartorio.nome)
        )
        return list(result.scalars().all())
    
    async def criar_cartorio(
        self,
        tenant_id: uuid.UUID,
        nome: str,
        comarca: str,
        uf: str,
        codigo_censec: Optional[str] = None,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
        endereco: Optional[str] = None
    ) -> Cartorio:
        """Cria novo cartório."""
        cartorio = Cartorio(
            tenant_id=tenant_id,
            nome=nome,
            comarca=comarca,
            uf=uf,
            codigo_censec=codigo_censec,
            telefone=telefone,
            email=email,
            endereco=endereco
        )
        self.session.add(cartorio)
        return cartorio
    
    async def get_benfeitorias(self, imovel_id: uuid.UUID) -> list[Benfeitoria]:
        """Lista benfeitorias de um imóvel."""
        result = await self.session.execute(
            select(Benfeitoria)
            .where(
                and_(
                    Benfeitoria.imovel_id == imovel_id,
                    Benfeitoria.deleted_at.is_(None)
                )
            )
            .order_by(Benfeitoria.nome)
        )
        return list(result.scalars().all())
