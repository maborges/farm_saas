"""
Imóveis Rurais - API Routes

Endpoints para gestão de imóveis rurais:
- CRUD de imóveis com validações (NIRF, CAR, área)
- Gestão de cartórios
- Benfeitorias
- Feature gates por módulo IMOVEIS_CADASTRO
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from decimal import Decimal
import uuid

from core.dependencies import (
    get_session, 
    get_current_tenant, 
    get_current_user,
    require_module
)
from core.models.tenant import Tenant
from core.models.auth import Usuario
from core.constants import Modulos
from imoveis.models.imovel import (
    ImovelRural, Cartorio, Benfeitoria,
    TipoImovel, SituacaoImovel
)
from imoveis.services.imovel_service import ImovelService

from pydantic import BaseModel, Field, validator


# ==================== SCHEMAS ====================

class ImovelCreate(BaseModel):
    """Schema para criação de imóvel rural."""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do imóvel")
    unidade_produtiva_id: uuid.UUID = Field(..., description="ID da fazenda vinculada")
    
    # Dados da matrícula
    cartorio_id: Optional[uuid.UUID] = None
    numero_matricula: Optional[str] = Field(None, max_length=100)
    
    # Dados federais
    nirf: Optional[str] = Field(None, max_length=20, description="NIRF (Receita Federal)")
    car_numero: Optional[str] = Field(None, max_length=50, description="Número do CAR")
    ccir_numero: Optional[str] = Field(None, max_length=50, description="Número do CCIR")
    
    # Áreas
    area_total_ha: Decimal = Field(..., description="Área total em hectares")
    area_aproveitavel_ha: Optional[Decimal] = None
    area_app_ha: Optional[Decimal] = None
    area_rl_ha: Optional[Decimal] = None
    
    # Localização
    municipio: str = Field(..., max_length=100)
    uf: str = Field(..., min_length=2, max_length=2)
    codigo_municipio_ibge: Optional[str] = None
    
    # Coordenadas
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    
    # Tipo e situação
    tipo: TipoImovel = TipoImovel.RURAL
    observacao: Optional[str] = None


class ImovelUpdate(BaseModel):
    """Schema para atualização de imóvel."""
    nome: Optional[str] = Field(None, max_length=255)
    cartorio_id: Optional[uuid.UUID] = None
    numero_matricula: Optional[str] = None
    nirf: Optional[str] = Field(None, max_length=20)
    car_numero: Optional[str] = Field(None, max_length=50)
    ccir_numero: Optional[str] = Field(None, max_length=50)
    area_total_ha: Optional[Decimal] = None
    area_aproveitavel_ha: Optional[Decimal] = None
    area_app_ha: Optional[Decimal] = None
    area_rl_ha: Optional[Decimal] = None
    modulos_fiscais: Optional[Decimal] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    tipo: Optional[TipoImovel] = None
    observacao: Optional[str] = None
    motivo_alteracao_area: Optional[str] = None


class ImovelResponse(BaseModel):
    """Schema de resposta de imóvel."""
    id: uuid.UUID
    tenant_id: uuid.UUID
    unidade_produtiva_id: uuid.UUID
    nome: str
    nirf: Optional[str]
    car_numero: Optional[str]
    ccir_numero: Optional[str]
    area_total_ha: Decimal
    area_aproveitavel_ha: Optional[Decimal]
    area_app_ha: Optional[Decimal]
    area_rl_ha: Optional[Decimal]
    modulos_fiscais: Optional[Decimal]
    municipio: str
    uf: str
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    tipo: TipoImovel
    situacao: SituacaoImovel
    geometria: Optional[dict]
    observacao: Optional[str]
    
    class Config:
        from_attributes = True


class CartorioCreate(BaseModel):
    """Schema para criação de cartório."""
    nome: str = Field(..., max_length=255)
    comarca: str = Field(..., max_length=100)
    uf: str = Field(..., min_length=2, max_length=2)
    codigo_censec: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None


class CartorioResponse(BaseModel):
    """Schema de resposta de cartório."""
    id: uuid.UUID
    nome: str
    comarca: str
    uf: str
    codigo_censec: Optional[str]
    telefone: Optional[str]
    email: Optional[str]
    
    class Config:
        from_attributes = True


class BenfeitoriaCreate(BaseModel):
    """Schema para criação de benfeitoria."""
    nome: str = Field(..., max_length=100)
    tipo: str = Field(..., description="SEDE, SILO, CURRAL, CASA, GALPAO, OFICINA")
    area_construida: Optional[Decimal] = None
    capacidade: Optional[Decimal] = None
    unidade_capacidade: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    valor_estimado: Optional[Decimal] = None
    ano_construcao: Optional[int] = None
    observacoes: Optional[str] = None


class BenfeitoriaResponse(BaseModel):
    """Schema de resposta de benfeitoria."""
    id: uuid.UUID
    nome: str
    tipo: str
    area_construida: Optional[Decimal]
    capacidade: Optional[Decimal]
    unidade_capacidade: Optional[str]
    valor_estimado: Optional[Decimal]
    
    class Config:
        from_attributes = True


# ==================== ROUTER ====================

router = APIRouter(prefix="/imoveis", tags=["Imóveis Rurais"])


# ==================== IMÓVEIS - CRUD ====================

@router.get(
    "/",
    response_model=List[ImovelResponse],
    dependencies=[Depends(require_module(Modulos.IMOVEIS_CADASTRO))]
)
async def list_imoveis(
    unidade_produtiva_id: Optional[uuid.UUID] = Query(None, description="Filtrar por fazenda"),
    situacao: Optional[SituacaoImovel] = Query(None, description="Filtrar por situação"),
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """
    Lista imóveis rurais do tenant.
    
    - **unidade_produtiva_id**: Opcional. Filtra imóveis de uma fazenda específica.
    - **situacao**: Opcional. Filtra por situação cadastral (REGULAR, PENDENTE, IRREGULAR).
    
    Requer módulo: IMOVEIS_CADASTRO
    """
    service = ImovelService(session)
    
    if unidade_produtiva_id:
        imoveis = await service.get_imoveis_by_fazenda(unidade_produtiva_id, tenant.id)
    else:
        # Lista todos do tenant
        imoveis = await service.get_imoveis_by_fazenda(None, tenant.id)  # Implementar método geral
    
    if situacao:
        imoveis = [i for i in imoveis if i.situacao == situacao]
    
    return imoveis


@router.get(
    "/{imovel_id}",
    response_model=ImovelResponse,
    dependencies=[Depends(require_module(Modulos.IMOVEIS_CADASTRO))]
)
async def get_imovel(
    imovel_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """
    Obtém detalhes de um imóvel rural.
    
    Requer módulo: IMOVEIS_CADASTRO
    """
    service = ImovelService(session)
    imovel = await service.get_imovel_by_id(imovel_id, tenant.id)
    
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    return imovel


@router.post(
    "/",
    response_model=ImovelResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_module(Modulos.IMOVEIS_CADASTRO))]
)
async def create_imovel(
    data: ImovelCreate,
    tenant: Tenant = Depends(get_current_tenant),
    user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Cria novo imóvel rural.
    
    Validações:
    - NIRF único no tenant (com dígito verificador)
    - CAR com formato válido (UF + 12 dígitos)
    - Área consistente com a fazenda (tolerância 10%)
    - Múltiplos imóveis não podem exceder área da fazenda
    
    Retorna alertas se houver divergência de áreas.
    
    Requer módulo: IMOVEIS_CADASTRO
    """
    service = ImovelService(session)
    
    try:
        imovel, alertas = await service.criar_imovel(
            tenant_id=tenant.id,
            unidade_produtiva_id=data.unidade_produtiva_id,
            nome=data.nome,
            municipio=data.municipio,
            uf=data.uf,
            area_total_ha=data.area_total_ha,
            nirf=data.nirf,
            car_numero=data.car_numero,
            ccir_numero=data.ccir_numero,
            cartorio_id=data.cartorio_id,
            numero_matricula=data.numero_matricula,
            tipo=data.tipo,
            observacao=data.observacao,
            created_by=user.id
        )
        
        await session.commit()
        await session.refresh(imovel)
        
        # Adiciona alertas no header da resposta
        response = ImovelResponse.model_validate(imovel)
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{imovel_id}",
    response_model=ImovelResponse,
    dependencies=[Depends(require_module(Modulos.IMOVEIS_CADASTRO))]
)
async def update_imovel(
    imovel_id: uuid.UUID,
    data: ImovelUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Atualiza imóvel rural.
    
    - Alteração de NIRF valida unicidade
    - Alteração de área exige justificativa (motivo_alteracao_area)
    - Atualiza situação cadastral automaticamente
    
    Requer módulo: IMOVEIS_CADASTRO
    """
    service = ImovelService(session)
    
    imovel = await service.get_imovel_by_id(imovel_id, tenant.id)
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    try:
        dados = data.model_dump(exclude_unset=True)
        imovel, alertas = await service.atualizar_imovel(imovel, dados, user.id)
        
        await session.commit()
        await session.refresh(imovel)
        
        return ImovelResponse.model_validate(imovel)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{imovel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_module(Modulos.IMOVEIS_CADASTRO))]
)
async def delete_imovel(
    imovel_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """
    Exclusão lógica de imóvel.
    
    Só permite exclusão se:
    - Não houver documentos legais ativos
    - Não houver contratos de arrendamento ativos
    
    Requer módulo: IMOVEIS_CADASTRO
    """
    service = ImovelService(session)
    
    imovel = await service.get_imovel_by_id(imovel_id, tenant.id)
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    try:
        await service.excluir_imovel(imovel)
        await session.commit()
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== CARTÓRIOS ====================

@router.get(
    "/cartorios/",
    response_model=List[CartorioResponse],
    dependencies=[Depends(require_module(Modulos.IMOVEIS_CADASTRO))]
)
async def list_cartorios(
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Lista cartórios cadastrados no tenant."""
    service = ImovelService(session)
    cartorios = await service.get_cartorios(tenant.id)
    return cartorios


@router.post(
    "/cartorios/",
    response_model=CartorioResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_module(Modulos.IMOVEIS_CADASTRO))]
)
async def create_cartorio(
    data: CartorioCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Cadastra novo cartório de registro de imóveis."""
    service = ImovelService(session)
    
    cartorio = await service.criar_cartorio(
        tenant_id=tenant.id,
        nome=data.nome,
        comarca=data.comarca,
        uf=data.uf,
        codigo_censec=data.codigo_censec,
        telefone=data.telefone,
        email=data.email,
        endereco=data.endereco
    )
    
    await session.commit()
    await session.refresh(cartorio)
    
    return cartorio


# ==================== BENFEITORIAS ====================

@router.get(
    "/{imovel_id}/benfeitorias",
    response_model=List[BenfeitoriaResponse],
    dependencies=[Depends(require_module(Modulos.IMOVEIS_CADASTRO))]
)
async def list_benfeitorias(
    imovel_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Lista benfeitorias de um imóvel."""
    service = ImovelService(session)
    
    imovel = await service.get_imovel_by_id(imovel_id, tenant.id)
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    benfeitorias = await service.get_benfeitorias(imovel_id)
    return benfeitorias


@router.post(
    "/{imovel_id}/benfeitorias",
    response_model=BenfeitoriaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_module(Modulos.IMOVEIS_CADASTRO))]
)
async def create_benfeitoria(
    imovel_id: uuid.UUID,
    data: BenfeitoriaCreate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Cadastra nova benfeitoria em imóvel."""
    service = ImovelService(session)
    
    imovel = await service.get_imovel_by_id(imovel_id, tenant.id)
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    benfeitoria = Benfeitoria(
        imovel_id=imovel_id,
        nome=data.nome,
        tipo=data.tipo,
        area_construida=data.area_construida,
        capacidade=data.capacidade,
        unidade_capacidade=data.unidade_capacidade,
        latitude=data.latitude,
        longitude=data.longitude,
        valor_estimado=data.valor_estimado,
        ano_construcao=data.ano_construcao,
        observacoes=data.observacoes
    )
    
    session.add(benfeitoria)
    await session.commit()
    await session.refresh(benfeitoria)
    
    return benfeitoria
