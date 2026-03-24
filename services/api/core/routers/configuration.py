from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid

from core.dependencies import get_session, get_current_admin, get_current_tenant
from core.models.tenant import Tenant
from core.models.configuration import ConfiguracaoSaaS
from core.models.tenant_config import ConfiguracaoTenant
from core.schemas.config_schemas import (
    SaaSConfigResponse, SaaSConfigUpdate, SMTPConfig,
    TenantConfigResponse, TenantConfigUpdate
)

router = APIRouter(prefix="/config", tags=["Configurações"])

# --- BACKOFFICE (Global) ---

@router.get("/saas", response_model=List[SaaSConfigResponse], dependencies=[Depends(get_current_admin)])
async def list_saas_configs(session: AsyncSession = Depends(get_session)):
    """Lista todas as configurações globais do SaaS."""
    stmt = select(ConfiguracaoSaaS)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.put("/saas/{chave}", response_model=SaaSConfigResponse, dependencies=[Depends(get_current_admin)])
async def update_saas_config(
    chave: str, 
    data: SaaSConfigUpdate, 
    session: AsyncSession = Depends(get_session)
):
    """Cria ou atualiza uma configuração global do sistema."""
    stmt = select(ConfiguracaoSaaS).where(ConfiguracaoSaaS.chave == chave)
    result = await session.execute(stmt)
    config = result.scalar_one_or_none()
    
    if not config:
        config = ConfiguracaoSaaS(chave=chave, valor=data.valor, descricao=data.descricao)
        session.add(config)
    else:
        config.valor = data.valor
        if data.descricao:
            config.descricao = data.descricao
        if data.ativo is not None:
            config.ativo = data.ativo
            
    await session.commit()
    await session.refresh(config)
    return config

# --- PRODUTOR (Tenant specific) ---

@router.get("/tenant", response_model=List[TenantConfigResponse])
async def list_tenant_configs(
    categoria: Optional[str] = None,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Lista as configurações ativas do assinante logado."""
    stmt = select(ConfiguracaoTenant).where(ConfiguracaoTenant.tenant_id == tenant.id)
    if categoria:
        stmt = stmt.where(ConfiguracaoTenant.categoria == categoria)
    
    result = await session.execute(stmt)
    return result.scalars().all()

@router.put("/tenant/{categoria}/{chave}", response_model=TenantConfigResponse)
async def update_tenant_config(
    categoria: str,
    chave: str,
    data: TenantConfigUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Cria ou atualiza uma configuração específica do assinante."""
    stmt = select(ConfiguracaoTenant).where(
        ConfiguracaoTenant.tenant_id == tenant.id,
        ConfiguracaoTenant.categoria == categoria,
        ConfiguracaoTenant.chave == chave
    )
    result = await session.execute(stmt)
    config = result.scalar_one_or_none()
    
    if not config:
        config = ConfiguracaoTenant(
            tenant_id=tenant.id,
            categoria=categoria,
            chave=chave,
            valor=data.valor,
            descricao=data.descricao
        )
        session.add(config)
    else:
        config.valor = data.valor
        if data.descricao:
            config.descricao = data.descricao
        if data.ativo is not None:
            config.ativo = data.ativo
            
    await session.commit()
    await session.refresh(config)
    return config

@router.get("/my-smtp", response_model=SMTPConfig)
async def get_my_smtp_config(
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Recupera a configuração SMTP do produtor (White-label)."""
    if not tenant.smtp_config:
        # Se não tem, retorna vazio ou erro 404 dependendo da semântica front
        return {
            "host": "",
            "port": 587,
            "user": "",
            "from": ""
        }
    return tenant.smtp_config

@router.put("/my-smtp")
async def update_my_smtp_config(
    data: SMTPConfig,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session)
):
    """Atualiza as credenciais de e-mail do produtor."""
    # O model_dump(by_alias=True) garante que salve as chaves como 'from' e 'pass' no JSON
    tenant.smtp_config = data.model_dump(by_alias=True)
    await session.commit()
    return {"message": "Configuração SMTP do tenant atualizada com sucesso."}
