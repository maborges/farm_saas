"""Backfill de pessoa_id em compras_fornecedores.

Preenche fornecedores legados com a Pessoa canônica por tenant, priorizando:
1. Match por documento (CPF/CNPJ normalizado)
2. Fallback por nome normalizado (baixa confiança; auditado em log)
3. Criação de nova Pessoa canônica quando não houver match

O script é idempotente:
- reutiliza Pessoa existente quando já resolvida;
- não duplica Pessoa quando o mesmo documento reaparece;
- não altera fornecedores já vinculados corretamente.
"""

import argparse
import asyncio
import sys
import unicodedata
import uuid
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import core.models  # noqa: F401 - garante metadata carregado para scripts
from core.cadastros.pessoas.models import Pessoa, PessoaDocumento
from core.database import async_session_maker
from operacional.models.compras import Fornecedor
from operacional.services.fornecedores_service import (
    _buscar_pessoa_por_documento,
    _garantir_relacionamento_fornecedor,
    _obter_tipo_fornecedor,
    normalizar_documento,
    resolve_fornecedor,
)


@dataclass
class BackfillStats:
    total_processado: int = 0
    ja_vinculados: int = 0
    vinculados_documento: int = 0
    vinculados_nome: int = 0
    criados_novos: int = 0
    erros: int = 0


def normalizar_nome(nome: str | None) -> str:
    if not nome:
        return ""

    decomposed = unicodedata.normalize("NFKD", nome)
    sem_acento = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    alnum_espaco = "".join(ch if ch.isalnum() else " " for ch in sem_acento.lower())
    return " ".join(alnum_espaco.split())


async def _buscar_documentos_da_pessoa(
    session: AsyncSession,
    pessoa_id: uuid.UUID,
) -> list[PessoaDocumento]:
    stmt = select(PessoaDocumento).where(PessoaDocumento.pessoa_id == pessoa_id)
    return (await session.execute(stmt)).scalars().all()


async def _garantir_papel_fornecedor(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    pessoa_id: uuid.UUID,
) -> None:
    tipo = await _obter_tipo_fornecedor(session, tenant_id)
    await _garantir_relacionamento_fornecedor(session, pessoa_id, tipo.id)


async def _buscar_pessoa_por_nome_normalizado(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    nome: str | None,
) -> Pessoa | None:
    nome_norm = normalizar_nome(nome)
    if not nome_norm:
        return None

    stmt = select(Pessoa).where(Pessoa.tenant_id == tenant_id, Pessoa.ativo == True)
    pessoas = (await session.execute(stmt)).scalars().all()
    candidatos = [p for p in pessoas if normalizar_nome(p.nome_exibicao) == nome_norm]

    if len(candidatos) == 1:
        return candidatos[0]
    return None


async def fornecedor_ja_vinculado_corretamente(
    session: AsyncSession,
    fornecedor: Fornecedor,
) -> bool:
    if not fornecedor.pessoa_id:
        return False

    pessoa = await session.get(Pessoa, fornecedor.pessoa_id)
    if not pessoa:
        return False

    if pessoa.tenant_id != fornecedor.tenant_id:
        return False

    documento_fornecedor = normalizar_documento(fornecedor.cnpj_cpf)
    if not documento_fornecedor:
        return True

    documentos = await _buscar_documentos_da_pessoa(session, pessoa.id)
    documentos_norm = {
        normalizar_documento(doc.numero)
        for doc in documentos
        if doc.tipo in {"CPF", "CNPJ"} and normalizar_documento(doc.numero)
    }
    if not documentos_norm:
        return True

    return documento_fornecedor in documentos_norm


async def backfill_fornecedor(
    session: AsyncSession,
    fornecedor: Fornecedor,
    stats: BackfillStats,
) -> str:
    stats.total_processado += 1

    if await fornecedor_ja_vinculado_corretamente(session, fornecedor):
        await _garantir_papel_fornecedor(session, fornecedor.tenant_id, fornecedor.pessoa_id)
        stats.ja_vinculados += 1
        return "ja_vinculado"

    pessoa = await _buscar_pessoa_por_documento(session, fornecedor.tenant_id, fornecedor.cnpj_cpf)
    if pessoa:
        fornecedor.pessoa_id = pessoa.id
        session.add(fornecedor)
        await _garantir_papel_fornecedor(session, fornecedor.tenant_id, pessoa.id)
        await session.flush()
        stats.vinculados_documento += 1
        return "documento"

    nome_referencia = fornecedor.razao_social or fornecedor.nome_fantasia
    pessoa = await _buscar_pessoa_por_nome_normalizado(session, fornecedor.tenant_id, nome_referencia)
    if pessoa:
        logger.warning(
            "Match por nome normalizado (baixa confiança) para fornecedor {} tenant {}: '{}'",
            fornecedor.id,
            fornecedor.tenant_id,
            nome_referencia,
        )
        fornecedor.pessoa_id = pessoa.id
        session.add(fornecedor)
        await _garantir_papel_fornecedor(session, fornecedor.tenant_id, pessoa.id)
        await session.flush()
        stats.vinculados_nome += 1
        return "nome"

    pessoa = await resolve_fornecedor(
        session,
        fornecedor.tenant_id,
        nome_fantasia=fornecedor.nome_fantasia,
        cnpj_cpf=fornecedor.cnpj_cpf,
        razao_social=fornecedor.razao_social,
        email=fornecedor.email,
        telefone=fornecedor.telefone,
    )
    fornecedor.pessoa_id = pessoa.id
    session.add(fornecedor)
    await session.flush()
    stats.criados_novos += 1
    return "criado"


async def _listar_fornecedores_ids(apenas_sem_pessoa: bool) -> list[uuid.UUID]:
    async with async_session_maker() as session:
        stmt = select(Fornecedor.id).order_by(Fornecedor.tenant_id, Fornecedor.nome_fantasia)
        if apenas_sem_pessoa:
            stmt = stmt.where(Fornecedor.pessoa_id.is_(None))
        return list((await session.execute(stmt)).scalars().all())


async def executar_backfill(apenas_sem_pessoa: bool = False, dry_run: bool = False) -> BackfillStats:
    stats = BackfillStats()
    fornecedor_ids = await _listar_fornecedores_ids(apenas_sem_pessoa)

    for fornecedor_id in fornecedor_ids:
        async with async_session_maker() as session:
            fornecedor = await session.get(Fornecedor, fornecedor_id)
            if not fornecedor:
                continue

            fornecedor_log_id = fornecedor.id
            tenant_log_id = fornecedor.tenant_id
            try:
                acao = await backfill_fornecedor(session, fornecedor, stats)
                if dry_run:
                    await session.rollback()
                else:
                    await session.commit()
                logger.info(
                    "Fornecedor {} tenant {} -> {}",
                    fornecedor_log_id,
                    tenant_log_id,
                    acao,
                )
            except Exception:
                stats.erros += 1
                await session.rollback()
                logger.exception(
                    "Erro no backfill do fornecedor {} tenant {}",
                    fornecedor_log_id,
                    tenant_log_id,
                )

    return stats


def imprimir_resumo(stats: BackfillStats, dry_run: bool) -> None:
    logger.info("Resumo do backfill de fornecedores")
    logger.info("Modo dry-run: {}", "sim" if dry_run else "nao")
    logger.info("Total processado: {}", stats.total_processado)
    logger.info("Ja vinculados: {}", stats.ja_vinculados)
    logger.info("Vinculados por documento: {}", stats.vinculados_documento)
    logger.info("Vinculados por nome: {}", stats.vinculados_nome)
    logger.info("Criados novos: {}", stats.criados_novos)
    logger.info("Erros: {}", stats.erros)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill de pessoa_id em compras_fornecedores")
    parser.add_argument(
        "--apenas-sem-pessoa",
        action="store_true",
        help="Processa apenas fornecedores com pessoa_id nulo",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa sem persistir alteracoes",
    )
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    stats = await executar_backfill(
        apenas_sem_pessoa=args.apenas_sem_pessoa,
        dry_run=args.dry_run,
    )
    imprimir_resumo(stats, args.dry_run)
    return 0 if stats.erros == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
