from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List
import uuid

from core.dependencies import get_session, get_current_user, get_current_admin
from core.models.knowledge_base import ConhecimentoCategoria, ConhecimentoArtigo
from core.schemas.knowledge_base_schemas import (
    ConhecimentoCategoriaCreate, ConhecimentoCategoriaResponse,
    ConhecimentoArtigoCreate, ConhecimentoArtigoResponse,
    ConhecimentoArtigoUpdate, CategoriaComArtigosResponse
)

router = APIRouter(prefix="/kb", tags=["Base de Conhecimento"])

# --- ÁREA PÚBLICA / CLIENTE ---

@router.get("/categories", response_model=List[CategoriaComArtigosResponse])
async def list_kb_public(session: AsyncSession = Depends(get_session)):
    """Lista categorias e artigos públicos."""
    stmt = (
        select(ConhecimentoCategoria)
        .options(selectinload(ConhecimentoCategoria.artigos))
        .order_by(ConhecimentoCategoria.ordem)
    )
    result = await session.execute(stmt)
    categorias = result.scalars().all()
    
    # Nota: Em produção, filtraríamos apenas artigos is_publico=True
    return categorias

@router.get("/articles/{slug}", response_model=ConhecimentoArtigoResponse)
async def get_article_by_slug(slug: str, session: AsyncSession = Depends(get_session)):
    """Busca um artigo pelo slug e incrementa visualizações."""
    stmt = select(ConhecimentoArtigo).where(ConhecimentoArtigo.slug == slug)
    result = await session.execute(stmt)
    artigo = result.scalar_one_or_none()
    
    if not artigo:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    
    artigo.visualizacoes += 1
    await session.commit()
    return artigo

# --- ÁREA ADMINISTRATIVA ---

@router.post("/categories", response_model=ConhecimentoCategoriaResponse, dependencies=[Depends(get_current_admin)])
async def create_category(data: ConhecimentoCategoriaCreate, session: AsyncSession = Depends(get_session)):
    cat = ConhecimentoCategoria(**data.model_dump())
    session.add(cat)
    await session.commit()
    await session.refresh(cat)
    return cat

@router.post("/articles", response_model=ConhecimentoArtigoResponse, dependencies=[Depends(get_current_admin)])
async def create_article(data: ConhecimentoArtigoCreate, session: AsyncSession = Depends(get_session)):
    art = ConhecimentoArtigo(**data.model_dump())
    session.add(art)
    try:
        await session.commit()
        await session.refresh(art)
        return art
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Erro ao criar artigo. Slug duplicado?")

@router.patch("/articles/{article_id}", response_model=ConhecimentoArtigoResponse, dependencies=[Depends(get_current_admin)])
async def update_article(article_id: uuid.UUID, data: ConhecimentoArtigoUpdate, session: AsyncSession = Depends(get_session)):
    art = await session.get(ConhecimentoArtigo, article_id)
    if not art:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(art, key, value)
        
    await session.commit()
    await session.refresh(art)
    return art

@router.delete("/articles/{article_id}", dependencies=[Depends(get_current_admin)])
async def delete_article(article_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    art = await session.get(ConhecimentoArtigo, article_id)
    if not art:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    
    await session.delete(art)
    await session.commit()
    return {"message": "Artigo removido"}
