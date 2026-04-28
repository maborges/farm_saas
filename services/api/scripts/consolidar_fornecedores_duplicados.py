"""Consolidação de duplicidades legadas em compras_fornecedores.

Objetivo:
- eliminar duplicidades por tenant_id + pessoa_id;
- reapontar dependências para um fornecedor canônico;
- remover o fornecedor duplicado somente após reapontar referências;
- manter execução idempotente.
"""

import argparse
import asyncio
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

import core.models  # noqa: F401
from core.database import async_session_maker
from operacional.models.compras import CotacaoFornecedor, DevolucaoFornecedor, Fornecedor


REFERENCIAS_FORNECEDOR = (
    ("compras_cotacoes", CotacaoFornecedor.__table__, CotacaoFornecedor.fornecedor_id),
    ("compras_devolucoes", DevolucaoFornecedor.__table__, DevolucaoFornecedor.fornecedor_id),
)


@dataclass
class ConsolidacaoStats:
    grupos_processados: int = 0
    fornecedores_removidos: int = 0
    referencias_reapontadas: int = 0
    erros: int = 0


def _valor_preenchido(valor) -> bool:
    if valor is None:
        return False
    if isinstance(valor, str):
        return valor.strip() != ""
    return True


async def contar_referencias(session: AsyncSession, fornecedor_id: uuid.UUID) -> int:
    total = 0
    for _nome, tabela, coluna in REFERENCIAS_FORNECEDOR:
        stmt = select(func.count()).select_from(tabela).where(coluna == fornecedor_id)
        total += (await session.execute(stmt)).scalar_one()
    return total


def score_fornecedor(fornecedor: Fornecedor, referencias: int) -> tuple:
    preenchimento = sum(
        1
        for valor in (
            fornecedor.nome_fantasia,
            fornecedor.razao_social,
            fornecedor.cnpj_cpf,
            fornecedor.email,
            fornecedor.telefone,
            fornecedor.condicoes_pagamento,
            fornecedor.prazo_entrega_dias,
            fornecedor.avaliacao,
        )
        if _valor_preenchido(valor)
    )
    return (
        referencias,
        preenchimento,
        1 if _valor_preenchido(fornecedor.cnpj_cpf) else 0,
        str(fornecedor.id),
    )


def merge_dados_fornecedor(canonico: Fornecedor, duplicado: Fornecedor) -> bool:
    alterou = False
    for campo in (
        "nome_fantasia",
        "razao_social",
        "cnpj_cpf",
        "email",
        "telefone",
        "condicoes_pagamento",
        "prazo_entrega_dias",
        "avaliacao",
    ):
        valor_canonico = getattr(canonico, campo)
        valor_duplicado = getattr(duplicado, campo)
        if not _valor_preenchido(valor_canonico) and _valor_preenchido(valor_duplicado):
            setattr(canonico, campo, valor_duplicado)
            alterou = True
    return alterou


async def reapontar_referencias(
    session: AsyncSession,
    duplicado_id: uuid.UUID,
    canonico_id: uuid.UUID,
) -> int:
    total = 0
    for _nome, tabela, coluna in REFERENCIAS_FORNECEDOR:
        stmt = (
            update(tabela)
            .where(coluna == duplicado_id)
            .values({coluna.key: canonico_id})
        )
        result = await session.execute(stmt)
        total += result.rowcount or 0
    return total


async def obter_grupos_duplicados(
    session: AsyncSession,
    tenant_id: uuid.UUID | None = None,
    pessoa_id: uuid.UUID | None = None,
) -> list[tuple[uuid.UUID, uuid.UUID, int]]:
    stmt = (
        select(Fornecedor.tenant_id, Fornecedor.pessoa_id, func.count().label("total"))
        .where(Fornecedor.pessoa_id.is_not(None))
        .group_by(Fornecedor.tenant_id, Fornecedor.pessoa_id)
        .having(func.count() > 1)
        .order_by(Fornecedor.tenant_id, Fornecedor.pessoa_id)
    )
    if tenant_id:
        stmt = stmt.where(Fornecedor.tenant_id == tenant_id)
    if pessoa_id:
        stmt = stmt.where(Fornecedor.pessoa_id == pessoa_id)

    return list((await session.execute(stmt)).all())


async def carregar_fornecedores_grupo(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    pessoa_id: uuid.UUID,
) -> list[Fornecedor]:
    stmt = (
        select(Fornecedor)
        .where(Fornecedor.tenant_id == tenant_id, Fornecedor.pessoa_id == pessoa_id)
        .order_by(Fornecedor.id)
    )
    return list((await session.execute(stmt)).scalars().all())


async def escolher_canonico(session: AsyncSession, fornecedores: list[Fornecedor]) -> Fornecedor:
    referencias = {fornecedor.id: await contar_referencias(session, fornecedor.id) for fornecedor in fornecedores}
    return max(fornecedores, key=lambda fornecedor: score_fornecedor(fornecedor, referencias[fornecedor.id]))


async def consolidar_grupo(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    pessoa_id: uuid.UUID,
    stats: ConsolidacaoStats,
) -> dict:
    fornecedores = await carregar_fornecedores_grupo(session, tenant_id, pessoa_id)
    if len(fornecedores) <= 1:
        return {"status": "sem_duplicidade"}

    canonico = await escolher_canonico(session, fornecedores)
    duplicados = [fornecedor for fornecedor in fornecedores if fornecedor.id != canonico.id]

    stats.grupos_processados += 1
    referencias_reapontadas = 0

    for duplicado in duplicados:
        merge_dados_fornecedor(canonico, duplicado)
        referencias_reapontadas += await reapontar_referencias(session, duplicado.id, canonico.id)
        await session.delete(duplicado)
        stats.fornecedores_removidos += 1

    session.add(canonico)
    await session.flush()
    stats.referencias_reapontadas += referencias_reapontadas

    return {
        "status": "consolidado",
        "canonico_id": canonico.id,
        "duplicados_removidos": [fornecedor.id for fornecedor in duplicados],
        "referencias_reapontadas": referencias_reapontadas,
    }


async def executar_consolidacao(
    *,
    tenant_id: uuid.UUID | None = None,
    pessoa_id: uuid.UUID | None = None,
    dry_run: bool = False,
) -> ConsolidacaoStats:
    stats = ConsolidacaoStats()

    async with async_session_maker() as session:
        grupos = await obter_grupos_duplicados(session, tenant_id=tenant_id, pessoa_id=pessoa_id)

    for grupo_tenant_id, grupo_pessoa_id, _total in grupos:
        async with async_session_maker() as session:
            try:
                resultado = await consolidar_grupo(session, grupo_tenant_id, grupo_pessoa_id, stats)
                if dry_run:
                    await session.rollback()
                else:
                    await session.commit()
                logger.info(
                    "Grupo tenant {} pessoa {} -> {} canonico={} removidos={} refs={}",
                    grupo_tenant_id,
                    grupo_pessoa_id,
                    resultado["status"],
                    resultado.get("canonico_id"),
                    resultado.get("duplicados_removidos", []),
                    resultado.get("referencias_reapontadas", 0),
                )
            except Exception:
                stats.erros += 1
                await session.rollback()
                logger.exception(
                    "Erro na consolidacao do grupo tenant {} pessoa {}",
                    grupo_tenant_id,
                    grupo_pessoa_id,
                )

    return stats


async def coletar_auditoria_pos_consolidacao() -> dict[str, int]:
    queries = {
        "total_fornecedores": "SELECT COUNT(*) FROM compras_fornecedores",
        "sem_pessoa": "SELECT COUNT(*) FROM compras_fornecedores WHERE pessoa_id IS NULL",
        "pessoa_orfa": """
            SELECT COUNT(*) FROM compras_fornecedores f
            WHERE f.pessoa_id IS NOT NULL
              AND NOT EXISTS (SELECT 1 FROM cadastros_pessoas p WHERE p.id = f.pessoa_id)
        """,
        "duplicidade_tenant_pessoa": """
            SELECT COUNT(*) FROM (
                SELECT tenant_id, pessoa_id, COUNT(*) c
                FROM compras_fornecedores
                WHERE pessoa_id IS NOT NULL
                GROUP BY tenant_id, pessoa_id
                HAVING COUNT(*) > 1
            ) x
        """,
        "duplicidade_tenant_doc_normalizado": """
            SELECT COUNT(*) FROM (
                SELECT tenant_id, regexp_replace(cnpj_cpf, '[^0-9]', '', 'g') doc, COUNT(*) c
                FROM compras_fornecedores
                WHERE cnpj_cpf IS NOT NULL
                  AND regexp_replace(cnpj_cpf, '[^0-9]', '', 'g') <> ''
                GROUP BY tenant_id, regexp_replace(cnpj_cpf, '[^0-9]', '', 'g')
                HAVING COUNT(*) > 1
            ) x
        """,
        "referencias_orfas_cotacoes": """
            SELECT COUNT(*) FROM compras_cotacoes c
            WHERE NOT EXISTS (SELECT 1 FROM compras_fornecedores f WHERE f.id = c.fornecedor_id)
        """,
        "referencias_orfas_devolucoes": """
            SELECT COUNT(*) FROM compras_devolucoes d
            WHERE NOT EXISTS (SELECT 1 FROM compras_fornecedores f WHERE f.id = d.fornecedor_id)
        """,
    }

    resultados: dict[str, int] = {}
    async with async_session_maker() as session:
        for nome, query in queries.items():
            result = await session.execute(text(query))
            resultados[nome] = int(result.scalar_one())
    return resultados


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Consolidacao de fornecedores duplicados por tenant+pessoa")
    parser.add_argument("--tenant-id", type=uuid.UUID, help="Filtra um tenant especifico")
    parser.add_argument("--pessoa-id", type=uuid.UUID, help="Filtra uma pessoa especifica")
    parser.add_argument("--dry-run", action="store_true", help="Executa sem persistir alteracoes")
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    stats = await executar_consolidacao(
        tenant_id=args.tenant_id,
        pessoa_id=args.pessoa_id,
        dry_run=args.dry_run,
    )
    auditoria = await coletar_auditoria_pos_consolidacao()

    logger.info("Resumo consolidacao: grupos={} removidos={} refs={} erros={}", stats.grupos_processados, stats.fornecedores_removidos, stats.referencias_reapontadas, stats.erros)
    for chave, valor in auditoria.items():
        logger.info("{}={}", chave, valor)

    return 0 if stats.erros == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
