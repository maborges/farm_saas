"""
Motor de Alertas Automáticos do AgroSaaS.

Gera notificações baseadas em eventos e regras de negócio:
- Vencimentos de contas a pagar/receber
- Estoque baixo de insumos
- Tarefas atrasadas
- Carência de defensivos
- Condições climáticas adversas
- Alertas de NDVI
- Etc.

Execução:
- Via Celery Beat (agendado diariamente)
- Via webhook (eventos em tempo real)
- Manual (admin)

Uso:
    python -m notificacoes.alertas_engine
"""
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from core.database import async_session_maker
from notificacoes.service import NotificacaoService
from notificacoes.schemas import NotificacaoCreate


class AlertasEngine:
    """Motor de geração automática de alertas."""

    async def verificar_todos_tenants(self) -> dict:
        """Itera sobre todos os tenants ativos e verifica alertas."""
        from core.models.tenant import Tenant
        from core.models.billing import AssinaturaTenant

        async with async_session_maker() as session:
            # Buscar todos os tenants com assinatura ativa
            stmt = (
                select(Tenant)
                .join(AssinaturaTenant, AssinaturaTenant.tenant_id == Tenant.id)
                .where(
                    Tenant.ativo == True,
                    AssinaturaTenant.status == "ATIVA",
                    AssinaturaTenant.tipo_assinatura == "GRUPO",
                )
                .distinct()
            )
            result = await session.execute(stmt)
            tenants = list(result.scalars().all())

        logger.info(f"Verificando alertas para {len(tenants)} tenants ativos")

        resultados = {
            "tenants_verificados": len(tenants),
            "alertas_gerados": 0,
            "erros": 0,
        }

        for tenant in tenants:
            try:
                alertas = await self.verificar_tenant(tenant.id)
                resultados["alertas_gerados"] += len(alertas)
                logger.info(f"Tenant {tenant.nome}: {len(alertas)} alertas gerados")
            except Exception as e:
                logger.error(f"Erro ao verificar tenant {tenant.nome}: {e}")
                resultados["erros"] += 1

        return resultados

    async def verificar_tenant(self, tenant_id: UUID) -> List[NotificacaoCreate]:
        """Verifica todas as regras de alerta para um tenant específico."""
        alertas_gerados = []

        async with async_session_maker() as session:
            svc = NotificacaoService(session, tenant_id)

            # 1. Vencimentos próximos (5 dias)
            vencimentos = await self._verificar_vencimentos(session, tenant_id)
            alertas_gerados.extend(vencimentos)

            # 2. Estoque baixo
            estoque_baixo = await self._verificar_estoque_baixo(session, tenant_id)
            alertas_gerados.extend(estoque_baixo)

            # 3. Carência de defensivos
            carencia = await self._verificar_carencia_defensivos(session, tenant_id)
            alertas_gerados.extend(carencia)

            # 4. Tarefas atrasadas
            tarefas_atrasadas = await self._verificar_tarefas_atrasadas(session, tenant_id)
            alertas_gerados.extend(tarefas_atrasadas)

            # Criar notificações
            for alerta in alertas_gerados:
                await svc.criar_e_push(alerta)

        return alertas_gerados

    async def _verificar_vencimentos(
        self, session: AsyncSession, tenant_id: UUID
    ) -> List[NotificacaoCreate]:
        """Verifica contas a pagar/receber vencendo nos próximos 5 dias."""
        from financeiro.models.despesa import Despesa
        from financeiro.models.receita import Receita

        alertas = []
        hoje = datetime.now(timezone.utc).date()
        daqui_5_dias = hoje + timedelta(days=5)

        # Despesas vencendo
        stmt = (
            select(Despesa)
            .where(
                Despesa.tenant_id == tenant_id,
                Despesa.status == "PENDENTE",
                Despesa.data_vencimento >= hoje,
                Despesa.data_vencimento <= daqui_5_dias,
            )
            .limit(10)
        )
        result = await session.execute(stmt)
        despesas = result.scalars().all()

        if despesas:
            total = sum(d.valor for d in despesas)
            alertas.append(
                NotificacaoCreate(
                    tipo="VENCIMENTO_CONTAS_PAGAR",
                    titulo=f"{len(despesas)} contas a pagar vencendo em 5 dias",
                    mensagem=f"Total: R$ {total:.2f}. Verifique o fluxo de caixa para evitar atrasos.",
                    meta={
                        "quantidade": len(despesas),
                        "total": float(total),
                        "periodo": "5 dias",
                    },
                )
            )

        # Receitas vencendo
        stmt = (
            select(Receita)
            .where(
                Receita.tenant_id == tenant_id,
                Receita.status == "PENDENTE",
                Receita.data_vencimento >= hoje,
                Receita.data_vencimento <= daqui_5_dias,
            )
            .limit(10)
        )
        result = await session.execute(stmt)
        receitas = result.scalars().all()

        if receitas:
            total = sum(r.valor for r in receitas)
            alertas.append(
                NotificacaoCreate(
                    tipo="VENCIMENTO_CONTAS_RECEBER",
                    titulo=f"{len(receitas)} contas a receber vencendo em 5 dias",
                    mensagem=f"Total: R$ {total:.2f}. Acompanhe o recebimento.",
                    meta={
                        "quantidade": len(receitas),
                        "total": float(total),
                        "periodo": "5 dias",
                    },
                )
            )

        return alertas

    async def _verificar_estoque_baixo(
        self, session: AsyncSession, tenant_id: UUID
    ) -> List[NotificacaoCreate]:
        """Verifica produtos com estoque abaixo do mínimo."""
        from operacional.models.estoque import Produto, SaldoEstoque

        alertas = []

        # Produtos com estoque abaixo do mínimo
        stmt = (
            select(Produto, SaldoEstoque)
            .join(SaldoEstoque, SaldoEstoque.produto_id == Produto.id)
            .where(
                Produto.tenant_id == tenant_id,
                Produto.estoque_minimo > 0,
                SaldoEstoque.quantidade < Produto.estoque_minimo,
                SaldoEstoque.ativo == True,
            )
            .limit(10)
        )
        result = await session.execute(stmt)
        produtos_baixo = result.all()

        if produtos_baixo:
            itens = [
                f"{p.Produto.nome}: {p.SaldoEstoque.quantidade}/{p.Produto.estoque_minimo} {p.Produto.unidade}"
                for p in produtos_baixo
            ]
            alertas.append(
                NotificacaoCreate(
                    tipo="ESTOQUE_BAIXO",
                    titulo=f"{len(produtos_baixo)} produtos com estoque baixo",
                    mensagem="Produtos: " + ", ".join(itens[:5]) + ("..." if len(itens) > 5 else ""),
                    meta={
                        "quantidade": len(produtos_baixo),
                        "produtos": [
                            {
                                "id": str(p.Produto.id),
                                "nome": p.Produto.nome,
                                "quantidade_atual": float(p.SaldoEstoque.quantidade),
                                "estoque_minimo": float(p.Produto.estoque_minimo),
                                "unidade": p.Produto.unidade,
                            }
                            for p in produtos_baixo
                        ],
                    },
                )
            )

        return alertas

    async def _verificar_carencia_defensivos(
        self, session: AsyncSession, tenant_id: UUID
    ) -> List[NotificacaoCreate]:
        """Verifica carência de defensivos agrícolas vencendo em 24-48h."""
        from agricola.models.aplicacao import AplicacaoDefensivo

        alertas = []
        agora = datetime.now(timezone.utc)
        daqui_24h = agora + timedelta(hours=24)
        daqui_48h = agora + timedelta(hours=48)

        # Aplicações com carência vencendo em 24h
        stmt = (
            select(AplicacaoDefensivo)
            .where(
                AplicacaoDefensivo.tenant_id == tenant_id,
                AplicacaoDefensivo.data_aplicacao + AplicacaoDefensivo.carencia_dias >= agora,
                AplicacaoDefensivo.data_aplicacao + AplicacaoDefensivo.carencia_dias <= daqui_48h,
            )
            .limit(10)
        )
        result = await session.execute(stmt)
        aplicacoes = result.scalars().all()

        if aplicacoes:
            itens = [
                f"{a.defensivo_nome} (Talhão {a.talhao_nome}) - vence em {(a.data_aplicacao + timedelta(days=a.carencia_dias) - agora).days} dias"
                for a in aplicacoes
            ]
            alertas.append(
                NotificacaoCreate(
                    tipo="CARENCIA_DEFENSIVO",
                    titulo=f"{len(aplicacoes)} defensivos com carência vencendo",
                    mensagem="Atenção: " + ", ".join(itens[:3]) + ("..." if len(itens) > 3 else ""),
                    meta={
                        "quantidade": len(aplicacoes),
                        "aplicacoes": [
                            {
                                "id": str(a.id),
                                "defensivo": a.defensivo_nome,
                                "talhao": a.talhao_nome,
                                "carencia_dias": a.carencia_dias,
                                "data_fim_carencia": (a.data_aplicacao + timedelta(days=a.carencia_dias)).isoformat(),
                            }
                            for a in aplicacoes
                        ],
                    },
                )
            )

        return alertas

    async def _verificar_tarefas_atrasadas(
        self, session: AsyncSession, tenant_id: UUID
    ) -> List[NotificacaoCreate]:
        """Verifica tarefas/operações atrasadas."""
        from agricola.models.operacao import OperacaoCampo

        alertas = []
        hoje = datetime.now(timezone.utc).date()

        # Operações não concluídas com data prevista vencida
        stmt = (
            select(OperacaoCampo)
            .where(
                OperacaoCampo.tenant_id == tenant_id,
                OperacaoCampo.status.not_in(["CONCLUIDA", "CANCELADA"]),
                OperacaoCampo.data_prevista < hoje,
            )
            .limit(10)
        )
        result = await session.execute(stmt)
        operacoes = result.scalars().all()

        if operacoes:
            atraso_medio = sum((hoje - o.data_prevista).days for o in operacoes) / len(operacoes)
            alertas.append(
                NotificacaoCreate(
                    tipo="TAREFAS_ATRASADAS",
                    titulo=f"{len(operacoes)} operações agrícolas atrasadas",
                    mensagem=f"Atraso médio: {atraso_medio:.0f} dias. Verifique o cronograma.",
                    meta={
                        "quantidade": len(operacoes),
                        "atraso_medio_dias": float(atraso_medio),
                        "operacoes": [
                            {
                                "id": str(o.id),
                                "nome": o.nome,
                                "data_prevista": o.data_prevista.isoformat(),
                                "dias_atraso": (hoje - o.data_prevista).days,
                            }
                            for o in operacoes
                        ],
                    },
                )
            )

        return alertas


# =============================================================================
# EXECUÇÃO MANUAL / CLI
# =============================================================================

async def main():
    """Executa o motor de alertas manualmente."""
    logger.info("Iniciando motor de alertas automáticos...")

    engine = AlertasEngine()
    resultados = await engine.verificar_todos_tenants()

    logger.info(f"✓ Tenants verificados: {resultados['tenants_verificados']}")
    logger.info(f"✓ Alertas gerados: {resultados['alertas_gerados']}")
    logger.info(f"✗ Erros: {resultados['erros']}")

    return resultados


if __name__ == "__main__":
    asyncio.run(main())
