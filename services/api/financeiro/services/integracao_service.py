"""
Serviços de integração externa:
  - OFX parser + conciliação bancária
  - Exportação Carnê-Leão (RFB)
  - Resumo para escritório contábil
"""
import io
import uuid
import csv
from datetime import date, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func

from financeiro.models.despesa import Despesa
from financeiro.models.receita import Receita
from financeiro.models.plano_conta import PlanoConta
from financeiro.models.conciliacao import ContaBancaria, LancamentoBancario


# ── OFX Parser ────────────────────────────────────────────────────────────────

def _parse_ofx(content: str) -> list[dict]:
    """
    Parser mínimo para OFX/QFX (SGML legado e OFX 2.x).
    Retorna lista de transações: {fitid, data, valor, descricao, tipo}.
    """
    import re

    # Normaliza quebras de linha
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    transacoes = []
    # Encontra blocos STMTTRN
    for bloco in re.findall(r"<STMTTRN>(.*?)</STMTTRN>", content, re.DOTALL | re.IGNORECASE):
        def _tag(name: str) -> str | None:
            m = re.search(rf"<{name}>(.*?)(?:<|$)", bloco, re.IGNORECASE | re.DOTALL)
            return m.group(1).strip() if m else None

        fitid = _tag("FITID")
        dtposted = _tag("DTPOSTED") or ""
        trnamt = _tag("TRNAMT") or "0"
        memo = _tag("MEMO") or _tag("NAME") or ""
        trntype = _tag("TRNTYPE") or "OTHER"

        # Converte data YYYYMMDD[HHMM[SS[.mmm][+-ZH:ZM]]]
        data_str = dtposted[:8] if len(dtposted) >= 8 else ""
        try:
            dt = date(int(data_str[:4]), int(data_str[4:6]), int(data_str[6:8]))
        except Exception:
            continue

        try:
            valor = float(trnamt.replace(",", "."))
        except ValueError:
            continue

        transacoes.append({
            "fitid": fitid,
            "data": dt,
            "valor": valor,
            "descricao": memo[:500],
            "tipo": "CREDIT" if valor >= 0 else "DEBIT",
        })

    return transacoes


# ── Conciliação Service ───────────────────────────────────────────────────────

class ConciliacaoService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def criar_conta(self, dados: dict) -> ContaBancaria:
        dados["tenant_id"] = self.tenant_id
        conta = ContaBancaria(**dados)
        self.session.add(conta)
        await self.session.flush()
        await self.session.refresh(conta)
        return conta

    async def listar_contas(self) -> list[ContaBancaria]:
        stmt = select(ContaBancaria).where(ContaBancaria.tenant_id == self.tenant_id)
        return list((await self.session.execute(stmt)).scalars().all())

    async def importar_ofx(self, conta_id: uuid.UUID, ofx_content: str) -> dict:
        """
        Importa extrato OFX para uma conta bancária.
        Deduplica por FITID. Retorna contagem de importados/duplicados.
        """
        # Valida conta pertence ao tenant
        stmt = select(ContaBancaria).where(
            ContaBancaria.id == conta_id,
            ContaBancaria.tenant_id == self.tenant_id,
        )
        conta = (await self.session.execute(stmt)).scalar_one_or_none()
        if not conta:
            from core.exceptions import EntityNotFoundError
            raise EntityNotFoundError(f"Conta bancária {conta_id} não encontrada.")

        transacoes = _parse_ofx(ofx_content)
        importados = 0
        duplicados = 0

        for t in transacoes:
            # Deduplicação por FITID
            if t["fitid"]:
                stmt_dup = select(LancamentoBancario.id).where(
                    LancamentoBancario.conta_id == conta_id,
                    LancamentoBancario.id_ofx == t["fitid"],
                )
                if (await self.session.execute(stmt_dup)).scalar():
                    duplicados += 1
                    continue

            lanc = LancamentoBancario(
                id=uuid.uuid4(),
                tenant_id=self.tenant_id,
                conta_id=conta_id,
                data=t["data"],
                valor=t["valor"],
                descricao=t["descricao"],
                id_ofx=t["fitid"],
                tipo=t["tipo"],
                status_conciliacao="NAO_CONCILIADO",
            )
            self.session.add(lanc)
            importados += 1

        await self.session.flush()
        return {"importados": importados, "duplicados": duplicados, "total_ofx": len(transacoes)}

    async def listar_lancamentos(
        self,
        conta_id: uuid.UUID,
        status: Optional[str] = None,
        data_de: Optional[date] = None,
        data_ate: Optional[date] = None,
    ) -> list[LancamentoBancario]:
        stmt = select(LancamentoBancario).where(
            LancamentoBancario.tenant_id == self.tenant_id,
            LancamentoBancario.conta_id == conta_id,
        ).order_by(LancamentoBancario.data.desc())
        if status:
            stmt = stmt.where(LancamentoBancario.status_conciliacao == status)
        if data_de:
            stmt = stmt.where(LancamentoBancario.data >= data_de)
        if data_ate:
            stmt = stmt.where(LancamentoBancario.data <= data_ate)
        return list((await self.session.execute(stmt)).scalars().all())

    async def conciliar(
        self,
        lancamento_id: uuid.UUID,
        despesa_id: Optional[uuid.UUID] = None,
        receita_id: Optional[uuid.UUID] = None,
    ) -> LancamentoBancario:
        """Vincula um lançamento bancário a uma despesa ou receita."""
        stmt = select(LancamentoBancario).where(
            LancamentoBancario.id == lancamento_id,
            LancamentoBancario.tenant_id == self.tenant_id,
        )
        lanc = (await self.session.execute(stmt)).scalar_one_or_none()
        if not lanc:
            from core.exceptions import EntityNotFoundError
            raise EntityNotFoundError(f"Lançamento {lancamento_id} não encontrado.")

        lanc.despesa_id = despesa_id
        lanc.receita_id = receita_id
        lanc.status_conciliacao = "CONCILIADO"
        self.session.add(lanc)
        await self.session.flush()
        await self.session.refresh(lanc)
        return lanc

    async def sugerir_conciliacao(self, conta_id: uuid.UUID) -> list[dict]:
        """
        Sugere conciliações automáticas: cruza lançamentos bancários com
        despesas/receitas por valor + data (tolerância de ±3 dias).
        """
        stmt = select(LancamentoBancario).where(
            LancamentoBancario.conta_id == conta_id,
            LancamentoBancario.tenant_id == self.tenant_id,
            LancamentoBancario.status_conciliacao == "NAO_CONCILIADO",
        )
        lancamentos = list((await self.session.execute(stmt)).scalars().all())
        sugestoes = []

        for lanc in lancamentos:
            tolerancia = timedelta(days=3)
            if lanc.valor < 0:  # débito → despesa
                stmt_desp = select(Despesa).where(
                    Despesa.tenant_id == self.tenant_id,
                    Despesa.valor_total == abs(lanc.valor),
                    Despesa.data_vencimento >= lanc.data - tolerancia,
                    Despesa.data_vencimento <= lanc.data + tolerancia,
                    Despesa.status.in_(["A_PAGAR", "PAGO"]),
                )
                desp = (await self.session.execute(stmt_desp)).scalars().first()
                if desp:
                    sugestoes.append({
                        "lancamento_id": lanc.id,
                        "tipo": "DESPESA",
                        "sugestao_id": desp.id,
                        "descricao_lanc": lanc.descricao,
                        "descricao_fin": desp.descricao,
                        "valor": abs(lanc.valor),
                        "data_lanc": lanc.data,
                        "confianca": "ALTA" if lanc.data == desp.data_vencimento else "MEDIA",
                    })
            else:  # crédito → receita
                stmt_rec = select(Receita).where(
                    Receita.tenant_id == self.tenant_id,
                    Receita.valor_total == lanc.valor,
                    Receita.data_vencimento >= lanc.data - tolerancia,
                    Receita.data_vencimento <= lanc.data + tolerancia,
                    Receita.status.in_(["A_RECEBER", "RECEBIDO"]),
                )
                rec = (await self.session.execute(stmt_rec)).scalars().first()
                if rec:
                    sugestoes.append({
                        "lancamento_id": lanc.id,
                        "tipo": "RECEITA",
                        "sugestao_id": rec.id,
                        "descricao_lanc": lanc.descricao,
                        "descricao_fin": rec.descricao,
                        "valor": lanc.valor,
                        "data_lanc": lanc.data,
                        "confianca": "ALTA" if lanc.data == rec.data_vencimento else "MEDIA",
                    })

        return sugestoes


# ── Carnê-Leão Export ─────────────────────────────────────────────────────────

class CarneLeaoService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def exportar_csv(
        self,
        ano: int,
        fazenda_id: Optional[uuid.UUID] = None,
    ) -> str:
        """
        Gera CSV compatível com o layout de Livro Caixa do Produtor Rural (RFB).
        Colunas: competencia, tipo, categoria_rfb, descricao, valor, cpf_cnpj, nota_fiscal
        """
        jan1 = date(ano, 1, 1)
        dez31 = date(ano, 12, 31)

        # Receitas realizadas
        stmt_rec = select(
            Receita.data_recebimento,
            Receita.descricao,
            Receita.valor_recebido,
            Receita.valor_total,
            Receita.numero_nf,
            Receita.plano_conta_id,
        ).where(
            Receita.tenant_id == self.tenant_id,
            Receita.ativo == True,
            Receita.status.in_(["RECEBIDO", "RECEBIDO_PARCIAL"]),
            Receita.data_recebimento >= jan1,
            Receita.data_recebimento <= dez31,
        )
        if fazenda_id:
            stmt_rec = stmt_rec.where(Receita.fazenda_id == fazenda_id)
        receitas = (await self.session.execute(stmt_rec)).all()

        # Despesas pagas
        stmt_desp = select(
            Despesa.data_pagamento,
            Despesa.descricao,
            Despesa.valor_pago,
            Despesa.valor_total,
            Despesa.numero_nf,
            Despesa.fornecedor,
            Despesa.plano_conta_id,
        ).where(
            Despesa.tenant_id == self.tenant_id,
            Despesa.ativo == True,
            Despesa.status.in_(["PAGO", "PAGO_PARCIAL"]),
            Despesa.data_pagamento >= jan1,
            Despesa.data_pagamento <= dez31,
        )
        if fazenda_id:
            stmt_desp = stmt_desp.where(Despesa.fazenda_id == fazenda_id)
        despesas = (await self.session.execute(stmt_desp)).all()

        # Carrega planos de conta para categoria_rfb
        plano_ids = {r.plano_conta_id for r in receitas} | {d.plano_conta_id for d in despesas}
        planos: dict[uuid.UUID, PlanoConta] = {}
        if plano_ids:
            stmt_pc = select(PlanoConta).where(PlanoConta.id.in_(plano_ids))
            for pc in (await self.session.execute(stmt_pc)).scalars().all():
                planos[pc.id] = pc

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow([
            "Competência", "Tipo", "Categoria RFB", "Descrição",
            "Valor (R$)", "NF / Documento", "Pagador/Recebedor",
        ])

        for r in receitas:
            pc = planos.get(r.plano_conta_id)
            competencia = r.data_recebimento.strftime("%m/%Y") if r.data_recebimento else ""
            valor = float(r.valor_recebido or r.valor_total or 0)
            writer.writerow([
                competencia, "RECEITA",
                pc.categoria_rfb if pc else "RECEITA_ATIVIDADE",
                r.descricao, f"{valor:.2f}".replace(".", ","),
                r.numero_nf or "", "",
            ])

        for d in despesas:
            pc = planos.get(d.plano_conta_id)
            competencia = d.data_pagamento.strftime("%m/%Y") if d.data_pagamento else ""
            valor = float(d.valor_pago or d.valor_total or 0)
            writer.writerow([
                competencia, "DESPESA",
                pc.categoria_rfb if pc else "CUSTEIO",
                d.descricao, f"{valor:.2f}".replace(".", ","),
                d.numero_nf or "", d.fornecedor or "",
            ])

        return output.getvalue()


# ── API Contábil ─────────────────────────────────────────────────────────────

class ContabilService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def resumo(
        self,
        data_inicio: date,
        data_fim: date,
        fazenda_id: Optional[uuid.UUID] = None,
    ) -> dict:
        """
        Resumo financeiro estruturado para escritório contábil.
        Retorna receitas e despesas agrupadas por categoria RFB + totais.
        """
        # Receitas por categoria
        stmt_rec = (
            select(
                PlanoConta.categoria_rfb,
                PlanoConta.nome.label("categoria_nome"),
                func.sum(Receita.valor_recebido).label("total_recebido"),
                func.count(Receita.id).label("qtd"),
            )
            .join(PlanoConta, Receita.plano_conta_id == PlanoConta.id)
            .where(
                Receita.tenant_id == self.tenant_id,
                Receita.ativo == True,
                Receita.status.in_(["RECEBIDO", "RECEBIDO_PARCIAL"]),
                Receita.data_recebimento >= data_inicio,
                Receita.data_recebimento <= data_fim,
            )
            .group_by(PlanoConta.categoria_rfb, PlanoConta.nome)
        )
        if fazenda_id:
            stmt_rec = stmt_rec.where(Receita.fazenda_id == fazenda_id)

        # Despesas por categoria
        stmt_desp = (
            select(
                PlanoConta.categoria_rfb,
                PlanoConta.nome.label("categoria_nome"),
                func.sum(Despesa.valor_pago).label("total_pago"),
                func.count(Despesa.id).label("qtd"),
            )
            .join(PlanoConta, Despesa.plano_conta_id == PlanoConta.id)
            .where(
                Despesa.tenant_id == self.tenant_id,
                Despesa.ativo == True,
                Despesa.status.in_(["PAGO", "PAGO_PARCIAL"]),
                Despesa.data_pagamento >= data_inicio,
                Despesa.data_pagamento <= data_fim,
            )
            .group_by(PlanoConta.categoria_rfb, PlanoConta.nome)
        )
        if fazenda_id:
            stmt_desp = stmt_desp.where(Despesa.fazenda_id == fazenda_id)

        receitas_rows = (await self.session.execute(stmt_rec)).all()
        despesas_rows = (await self.session.execute(stmt_desp)).all()

        receitas = [
            {
                "categoria_rfb": r.categoria_rfb,
                "categoria_nome": r.categoria_nome,
                "total_recebido": float(r.total_recebido or 0),
                "quantidade": int(r.qtd),
            }
            for r in receitas_rows
        ]
        despesas = [
            {
                "categoria_rfb": d.categoria_rfb,
                "categoria_nome": d.categoria_nome,
                "total_pago": float(d.total_pago or 0),
                "quantidade": int(d.qtd),
            }
            for d in despesas_rows
        ]

        total_receitas = sum(r["total_recebido"] for r in receitas)
        total_despesas = sum(d["total_pago"] for d in despesas)

        return {
            "periodo": {"inicio": data_inicio.isoformat(), "fim": data_fim.isoformat()},
            "receitas": receitas,
            "despesas": despesas,
            "totais": {
                "total_receitas": round(total_receitas, 2),
                "total_despesas": round(total_despesas, 2),
                "resultado_liquido": round(total_receitas - total_despesas, 2),
            },
            "gerado_em": date.today().isoformat(),
        }
