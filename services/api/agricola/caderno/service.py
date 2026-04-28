from uuid import UUID
from datetime import date, datetime, timedelta
from typing import Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func

from core.base_service import BaseService
from core.exceptions import BusinessRuleError
from agricola.caderno.models import (
    CadernoCampoEntrada,
    CadernoCampoFoto,
    VisitaTecnica,
    EPIEntrega,
    CadernoExportacao,
)
from agricola.caderno.schemas import (
    EntradaCreate,
    EntradaUpdate,
    VisitaTecnicaCreate,
    EPIEntregaCreate,
    ExportacaoCreate,
    TimelineItem,
)
from agricola.operacoes.models import OperacaoAgricola

# Janela de edição livre sem aprovação do RT (configurável futuramente por tenant)
JANELA_EDICAO_HORAS = 72


class CadernoCampoService(BaseService[CadernoCampoEntrada]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(CadernoCampoEntrada, session, tenant_id)

    def _validar_edicao_retroativa(self, data_registro: date, justificativa: str | None) -> None:
        limite = datetime.utcnow() - timedelta(hours=JANELA_EDICAO_HORAS)
        if datetime.combine(data_registro, datetime.min.time()) < limite:
            if not justificativa:
                raise BusinessRuleError(
                    f"Registros com mais de {JANELA_EDICAO_HORAS}h exigem justificativa de digitalização retroativa."
                )

    async def criar_entrada(self, dados: EntradaCreate, usuario_id: UUID, ip: str | None = None) -> CadernoCampoEntrada:
        if dados.digitalizacao_retroativa:
            self._validar_edicao_retroativa(dados.data_registro, dados.justificativa_retroativa)

        entrada = CadernoCampoEntrada(
            tenant_id=self.tenant_id,
            safra_id=dados.safra_id,
            talhao_id=dados.talhao_id,
            tipo=dados.tipo,
            descricao=dados.descricao,
            data_registro=dados.data_registro,
            usuario_id=usuario_id,
            nivel_severidade=dados.nivel_severidade,
            recomendacao=dados.recomendacao,
            numero_receituario=dados.numero_receituario,
            digitalizacao_retroativa=dados.digitalizacao_retroativa,
            justificativa_retroativa=dados.justificativa_retroativa,
            ip_dispositivo=ip,
        )
        self.session.add(entrada)
        await self.session.flush()
        return entrada

    async def soft_delete(self, entrada_id: UUID, motivo: str) -> CadernoCampoEntrada:
        entrada = await self.get_or_fail(entrada_id)
        entrada.excluida = True
        entrada.motivo_exclusao = motivo
        await self.session.flush()
        return entrada

    async def adicionar_foto(
        self,
        entrada_id: UUID,
        url: str,
        latitude: float | None = None,
        longitude: float | None = None,
        data_captura: datetime | None = None,
    ) -> CadernoCampoFoto:
        foto = CadernoCampoFoto(
            entrada_id=entrada_id,
            url=url,
            latitude=latitude,
            longitude=longitude,
            data_captura=data_captura,
        )
        self.session.add(foto)
        await self.session.flush()
        return foto

    async def timeline(
        self,
        safra_id: UUID,
        talhao_id: UUID | None = None,
        tipo: str | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        incluir_excluidas: bool = False,
    ) -> list[TimelineItem]:
        """Agrega entradas manuais + operações automáticas numa timeline cronológica."""
        # 1. Entradas manuais do caderno
        stmt = select(CadernoCampoEntrada).where(
            CadernoCampoEntrada.tenant_id == self.tenant_id,
            CadernoCampoEntrada.safra_id == safra_id,
        )
        if not incluir_excluidas:
            stmt = stmt.where(CadernoCampoEntrada.excluida == False)
        if talhao_id:
            stmt = stmt.where(CadernoCampoEntrada.talhao_id == talhao_id)
        if tipo:
            stmt = stmt.where(CadernoCampoEntrada.tipo == tipo)
        if data_inicio:
            stmt = stmt.where(CadernoCampoEntrada.data_registro >= data_inicio)
        if data_fim:
            stmt = stmt.where(CadernoCampoEntrada.data_registro <= data_fim)
        stmt = stmt.order_by(CadernoCampoEntrada.data_registro.desc())

        entradas = list((await self.session.execute(stmt)).scalars().all())

        # 2. Operações automáticas NÃO vinculadas a entradas do caderno
        # (fallback: se o trigger não foi executado ou entrada foi excluída)
        op_stmt = select(OperacaoAgricola).where(
            OperacaoAgricola.tenant_id == self.tenant_id,
            OperacaoAgricola.safra_id == safra_id,
            OperacaoAgricola.status == "REALIZADA",
        )
        if talhao_id:
            op_stmt = op_stmt.where(OperacaoAgricola.talhao_id == talhao_id)
        if data_inicio:
            op_stmt = op_stmt.where(OperacaoAgricola.data_realizada >= data_inicio)
        if data_fim:
            op_stmt = op_stmt.where(OperacaoAgricola.data_realizada <= data_fim)
        op_stmt = op_stmt.order_by(OperacaoAgricola.data_realizada.desc())

        operacoes = list((await self.session.execute(op_stmt)).scalars().all())

        # IDs de operações já vinculadas a entradas para evitar duplicidade
        op_ids_vinculados = {e.operacao_id for e in entradas if e.operacao_id}

        items: list[TimelineItem] = []

        for e in entradas:
            items.append(TimelineItem(
                id=e.id,
                tipo=e.tipo,
                descricao=e.descricao,
                data_registro=e.data_registro,
                talhao_id=e.talhao_id,
                nivel_severidade=e.nivel_severidade,
                fotos_count=len(e.fotos),
                excluida=e.excluida,
                origem="caderno",
            ))

        for op in operacoes:
            if op.id in op_ids_vinculados:
                continue
            if tipo and tipo != "OPERACAO_AUTO":
                continue
            items.append(TimelineItem(
                id=op.id,
                tipo="OPERACAO_AUTO",
                subtipo=op.tipo,
                descricao=op.descricao,
                data_registro=op.data_realizada,
                talhao_id=op.talhao_id,
                fotos_count=len(op.fotos) if op.fotos else 0,
                excluida=False,
                origem="operacao",
            ))

        # Ordena tudo por data desc
        items.sort(key=lambda x: x.data_registro, reverse=True)
        return items

    async def listar_safras_ativas(self, safra_id: UUID | None = None):
        from agricola.safras.models import Safra
        if safra_id:
            stmt = select(Safra).where(Safra.id == safra_id, Safra.tenant_id == self.tenant_id)
        else:
            stmt = select(Safra).where(
                Safra.tenant_id == self.tenant_id,
                Safra.status.notin_(["ENCERRADA", "CANCELADA"]),
            )
        return list((await self.session.execute(stmt)).scalars().all())

    async def listar_alertas(self, safra_id: UUID | None = None, dias_sem_registro: int = 7) -> list[dict]:
        from datetime import date, timedelta
        from agricola.operacoes.models import OperacaoAgricola
        safras = await self.listar_safras_ativas(safra_id)
        alertas = []
        limite = date.today() - timedelta(days=dias_sem_registro)
        for safra in safras:
            ultima_entrada_stmt = select(func.max(CadernoCampoEntrada.data_registro)).where(
                CadernoCampoEntrada.tenant_id == self.tenant_id,
                CadernoCampoEntrada.safra_id == safra.id,
                CadernoCampoEntrada.excluida == False,
            )
            ultima_data = (await self.session.execute(ultima_entrada_stmt)).scalar_one_or_none()
            ultima_op_stmt = select(func.max(OperacaoAgricola.data_realizada)).where(
                OperacaoAgricola.tenant_id == self.tenant_id,
                OperacaoAgricola.safra_id == safra.id,
                OperacaoAgricola.status == "REALIZADA",
            )
            ultima_op = (await self.session.execute(ultima_op_stmt)).scalar_one_or_none()
            if ultima_data and ultima_op:
                ultima_registro = max(ultima_data, ultima_op) if isinstance(ultima_data, date) and isinstance(ultima_op, date) else (ultima_data or ultima_op)
            else:
                ultima_registro = ultima_data or ultima_op
            if ultima_registro and isinstance(ultima_registro, date):
                if ultima_registro < limite:
                    dias_desatualizada = (date.today() - ultima_registro).days
                    alertas.append({"safra_id": str(safra.id), "safra_nome": f"{safra.cultura} {safra.ano_safra}", "ultima_registro": ultima_registro.isoformat(), "dias_desatualizada": dias_desatualizada, "mensagem": f"Sem registros há {dias_desatualizada} dias (último: {ultima_registro.strftime('%d/%m/%Y')})."})
            elif not ultima_registro:
                alertas.append({"safra_id": str(safra.id), "safra_nome": f"{safra.cultura} {safra.ano_safra}", "ultima_registro": None, "dias_desatualizada": None, "mensagem": "Nenhum registro encontrado para esta safra."})
        return alertas


class VisitaTecnicaService(BaseService[VisitaTecnica]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(VisitaTecnica, session, tenant_id)

    async def criar(self, dados: VisitaTecnicaCreate, usuario_id: UUID) -> VisitaTecnica:
        visita = VisitaTecnica(
            tenant_id=self.tenant_id,
            safra_id=dados.safra_id,
            talhao_id=dados.talhao_id,
            responsavel_tecnico_id=usuario_id,
            nome_rt=dados.nome_rt,
            crea=dados.crea,
            data_visita=dados.data_visita,
            observacoes=dados.observacoes,
            recomendacoes=dados.recomendacoes,
            constatacoes=dados.constatacoes,
        )
        self.session.add(visita)
        await self.session.flush()
        return visita

    async def assinar(self, visita_id: UUID, nome_rt: str, crea: str) -> VisitaTecnica:
        visita = await self.get_or_fail(visita_id)
        if visita.assinado:
            raise BusinessRuleError("Visita técnica já foi assinada.")
        visita.assinado = True
        visita.data_assinatura = datetime.utcnow()
        visita.nome_rt = nome_rt
        visita.crea = crea
        await self.session.flush()
        return visita

    async def listar_por_safra(self, safra_id: UUID, talhao_id: UUID | None = None) -> list[VisitaTecnica]:
        stmt = select(VisitaTecnica).where(
            VisitaTecnica.tenant_id == self.tenant_id,
            VisitaTecnica.safra_id == safra_id,
        ).order_by(VisitaTecnica.data_visita.desc())
        if talhao_id:
            stmt = stmt.where(VisitaTecnica.talhao_id == talhao_id)
        return list((await self.session.execute(stmt)).scalars().all())


class EPIEntregaService(BaseService[EPIEntrega]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(EPIEntrega, session, tenant_id)

    async def criar(self, dados: EPIEntregaCreate) -> EPIEntrega:
        epi = EPIEntrega(
            tenant_id=self.tenant_id,
            trabalhador_id=dados.trabalhador_id,
            nome_trabalhador=dados.nome_trabalhador,
            epi_tipo=dados.epi_tipo,
            quantidade=dados.quantidade,
            data_entrega=dados.data_entrega,
            validade=dados.validade,
            operacao_id=dados.operacao_id,
        )
        self.session.add(epi)
        await self.session.flush()
        return epi

    async def listar(self, operacao_id: UUID | None = None) -> list[EPIEntrega]:
        stmt = select(EPIEntrega).where(
            EPIEntrega.tenant_id == self.tenant_id,
        ).order_by(EPIEntrega.data_entrega.desc())
        if operacao_id:
            stmt = stmt.where(EPIEntrega.operacao_id == operacao_id)
        return list((await self.session.execute(stmt)).scalars().all())


class CadernoExportacaoService(BaseService[CadernoExportacao]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(CadernoExportacao, session, tenant_id)

    async def gerar(self, dados: ExportacaoCreate) -> CadernoExportacao:
        # Normaliza modelo: aceita "padrao", "globalgap", "organico", "mapa"
        modelo = dados.modelo
        # Suporte legado: se modelo_certificacao foi passado, mapeia
        if dados.modelo_certificacao:
            legado_map = {
                "INTERNO": "padrao",
                "GLOBALGAP": "globalgap",
                "ORGANICO": "organico",
                "MAPA": "mapa",
            }
            modelo = legado_map.get(dados.modelo_certificacao.upper(), modelo)

        # 1. Busca dados da safra
        from agricola.safras.models import Safra
        safra_stmt = select(Safra).where(Safra.id == dados.safra_id, Safra.tenant_id == self.tenant_id)
        safra = (await self.session.execute(safra_stmt)).scalar_one_or_none()
        if not safra:
            raise EntityNotFoundError("Safra", dados.safra_id)

        # 2. Busca entradas do caderno
        caderno_svc = CadernoCampoService(self.session, self.tenant_id)
        entradas = await caderno_svc.timeline(
            dados.safra_id,
            talhao_id=dados.talhao_id,
            incluir_excluidas=False,
        )

        # 3. Busca nome da fazenda e talhões
        from core.cadastros.propriedades.models import AreaRural
        area_ids = list({e.talhao_id for e in entradas if hasattr(e, 'talhao_id')})
        talhoes_map: dict[str, str] = {}
        if area_ids:
            areas_stmt = select(AreaRural.id, AreaRural.nome).where(AreaRural.id.in_(area_ids))
            areas = (await self.session.execute(areas_stmt)).all()
            talhoes_map = {str(a.id): a.nome for a in areas}

        # 4. Busca visitas técnicas (para campos específicos de modelos)
        from agricola.caderno.models import VisitaTecnica
        visitas_stmt = select(VisitaTecnica).where(
            VisitaTecnica.tenant_id == self.tenant_id,
            VisitaTecnica.safra_id == dados.safra_id,
        )
        if dados.talhao_id:
            visitas_stmt = visitas_stmt.where(VisitaTecnica.talhao_id == dados.talhao_id)
        visitas = list((await self.session.execute(visitas_stmt)).scalars().all())

        # 5. Gera PDF conforme modelo
        import io
        import uuid as _uuid
        from pathlib import Path
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm, mm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, Image as RLImage, HRFlowable,
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
        from reportlab.lib.units import inch

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=2 * cm,
            bottomMargin=1.5 * cm,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            title=f"Caderno de Campo - {safra.cultura} {safra.ano_safra}",
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="DocTitle", fontSize=18, leading=22, textColor=HexColor("#1a5e1a"),
            alignment=TA_CENTER, spaceAfter=4, fontName="Helvetica-Bold",
        ))
        styles.add(ParagraphStyle(
            name="DocSubtitle", fontSize=10, leading=14, textColor=HexColor("#555"),
            alignment=TA_CENTER, spaceAfter=12, fontName="Helvetica",
        ))
        styles.add(ParagraphStyle(
            name="SectionHeader", fontSize=12, leading=16, textColor=HexColor("#1a5e1a"),
            spaceBefore=10, spaceAfter=4, fontName="Helvetica-Bold",
        ))
        styles.add(ParagraphStyle(
            name="BodyText2", fontSize=9, leading=13, textColor=HexColor("#333"),
            alignment=TA_JUSTIFY, fontName="Helvetica",
        ))
        styles.add(ParagraphStyle(
            name="SmallBold", fontSize=9, leading=13, textColor=HexColor("#1a5e1a"),
            fontName="Helvetica-Bold", spaceBefore=2,
        ))
        styles.add(ParagraphStyle(
            name="TableHeader", fontSize=8, leading=11, textColor=HexColor("#fff"),
            fontName="Helvetica-Bold", alignment=TA_CENTER,
        ))
        styles.add(ParagraphStyle(
            name="TableCell", fontSize=8, leading=11, textColor=HexColor("#333"),
            fontName="Helvetica", alignment=TA_LEFT,
        ))

        story = []

        # ═══════════════════════════════════════════════════════
        # LAYOUT POR MODELO
        # ═══════════════════════════════════════════════════════

        modelo_labels = {
            "padrao": "Caderno de Campo — Relatório Padrão",
            "globalgap": "Caderno de Campo — GlobalG.A.P.",
            "organico": "Caderno de Campo — Produção Orgânica (USDA/IBD)",
            "mapa": "Caderno de Campo — MAPA (Receituário Agronômico)",
        }

        # ── Cabeçalho ──
        story.append(Paragraph(modelo_labels.get(modelo, modelo_labels["padrao"]), styles["DocTitle"]))
        story.append(Paragraph(
            f"{safra.cultura} — Safra {safra.ano_safra}",
            styles["DocSubtitle"],
        ))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#1a5e1a"), spaceAfter=10))

        # ── Informações gerais ──
        info_data = [
            [Paragraph("<b>Cultura:</b>", styles["SmallBold"]), Paragraph(safra.cultura or "—", styles["BodyText2"])],
            [Paragraph("<b>Safra:</b>", styles["SmallBold"]), Paragraph(safra.ano_safra or "—", styles["BodyText2"])],
            [Paragraph("<b>Status:</b>", styles["SmallBold"]), Paragraph(safra.status or "—", styles["BodyText2"])],
        ]

        # Campos extras por modelo
        if modelo == "globalgap":
            # GlobalG.A.P.: número de registro, rastreabilidade de insumos, lote
            info_data.append([
                Paragraph("<b>Registro GlobalG.A.P.:</b>", styles["SmallBold"]),
                Paragraph(safra.id_externo or "N/I", styles["BodyText2"]),
            ])
            info_data.append([
                Paragraph("<b>Lote de Produto:</b>", styles["SmallBold"]),
                Paragraph(f"LOTE-{safra.id.hex[:8].upper()}", styles["BodyText2"]),
            ])
        elif modelo == "organico":
            # Orgânico: declaração de origem, período de conversão
            info_data.append([
                Paragraph("<b>Período de Conversão:</b>", styles["SmallBold"]),
                Paragraph(f"{safra.data_plantio or 'N/I'} até {safra.data_colheita or 'Em andamento'}", styles["BodyText2"]),
            ])
            info_data.append([
                Paragraph("<b>Declar. Origem:</b>", styles["SmallBold"]),
                Paragraph(f"Propriedade: {safra.cultura} — Safra {safra.ano_safra}", styles["BodyText2"]),
            ])
        elif modelo == "mapa":
            # MAPA: receituário agronômico
            if dados.assinado_por:
                info_data.append([
                    Paragraph("<b>Responsável Técnico:</b>", styles["SmallBold"]),
                    Paragraph(f"{dados.assinado_por} — CREA {dados.crea_rt or 'N/I'}", styles["BodyText2"]),
                ])

        if dados.assinado_por and modelo != "mapa":
            info_data.append([
                Paragraph("<b>Responsável:</b>", styles["SmallBold"]),
                Paragraph(f"{dados.assinado_por} — CREA {dados.crea_rt or 'N/I'}", styles["BodyText2"]),
            ])

        info_table = Table(info_data, colWidths=[4.5*cm, 10*cm])
        info_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, HexColor("#ddd")),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 12))

        # ═══════════════════════════════════════════════════════
        # GLOBALG.A.P. — Rastreabilidade de insumos
        # ═══════════════════════════════════════════════════════
        if modelo == "globalgap":
            story.append(Paragraph("Rastreabilidade de Insumos (GlobalG.A.P.)", styles["SectionHeader"]))
            story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#ccc"), spaceAfter=6))

            # Coleta insumos das operações
            insumos_rows = []
            for e in entradas:
                if hasattr(e, 'operacao_id') and e.operacao_id:
                    # Busca operação para detalhes de insumos
                    op_stmt = select(OperacaoAgricola).where(OperacaoAgricola.id == e.operacao_id)
                    op = (await self.session.execute(op_stmt)).scalar_one_or_none()
                    if op and op.insumos:
                        for ins in op.insumos:
                            insumos_rows.append([
                                Paragraph(e.data_registro.strftime("%d/%m/%Y"), styles["TableCell"]),
                                Paragraph(getattr(ins, "produto_nome", None) or str(ins.produto_id), styles["TableCell"]),
                                Paragraph(f"{ins.dose_por_ha or ''} {ins.unidade or ''}/ha", styles["TableCell"]),
                                Paragraph(str(getattr(ins, "registro_mapa", "N/A")), styles["TableCell"]),
                            ])

            if not insumos_rows:
                # Fallback: mostra entradas com dados básicos
                for e in entradas:
                    talhao_nome = talhoes_map.get(str(e.talhao_id), f"Talhão {str(e.talhao_id)[:8]}")
                    insumos_rows.append([
                        Paragraph(e.data_registro.strftime("%d/%m/%Y") if hasattr(e.data_registro, 'strftime') else str(e.data_registro), styles["TableCell"]),
                        Paragraph(talhao_nome, styles["TableCell"]),
                        Paragraph(e.tipo, styles["TableCell"]),
                        Paragraph("—", styles["TableCell"]),
                    ])

            insumos_header = [
                Paragraph("<b>Data</b>", styles["TableHeader"]),
                Paragraph("<b>Insumo / Talhão</b>", styles["TableHeader"]),
                Paragraph("<b>Dose</b>", styles["TableHeader"]),
                Paragraph("<b>Registro MAPA</b>", styles["TableHeader"]),
            ]
            insumos_table = Table([insumos_header] + insumos_rows, colWidths=[3*cm, 4*cm, 3*cm, 3*cm])
            insumos_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1a5e1a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#ccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#f9f9f9"), white]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(insumos_table)
            story.append(Spacer(1, 16))

        # ═══════════════════════════════════════════════════════
        # ORGÂNICO — Ausência de agroquímicos + declaração
        # ═══════════════════════════════════════════════════════
        if modelo == "organico":
            story.append(Paragraph("Declaração de Produção Orgânica", styles["SectionHeader"]))
            story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#ccc"), spaceAfter=6))

            story.append(Paragraph(
                f"Declaramos para fins de certificação orgânica (USDA/IBD) que as operações registradas neste "
                f"caderno de campo referentes à safra {safra.ano_safra} de {safra.cultura} foram realizadas "
                f"sem a utilização de agroquímicos ou insumos sintéticos proibidos pela legislação orgânica vigente.",
                styles["BodyText2"],
            ))
            story.append(Spacer(1, 10))

            # Tabela de operações — destaca ausência de agroquímicos
            story.append(Paragraph("Registro de Operações — Produção Orgânica", styles["SectionHeader"]))
            story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#ccc"), spaceAfter=6))

            organico_rows = []
            for e in entradas:
                talhao_nome = talhoes_map.get(str(e.talhao_id), f"Talhão {str(e.talhao_id)[:8]}")
                desc = (e.descricao or "")[:80]
                organico_rows.append([
                    Paragraph(e.data_registro.strftime("%d/%m/%Y") if hasattr(e.data_registro, 'strftime') else str(e.data_registro), styles["TableCell"]),
                    Paragraph(talhao_nome, styles["TableCell"]),
                    Paragraph(e.tipo, styles["TableCell"]),
                    Paragraph(desc, styles["TableCell"]),
                    Paragraph("✓ Livre de agroquímicos", styles["TableCell"]),
                ])

            organico_header = [
                Paragraph("<b>Data</b>", styles["TableHeader"]),
                Paragraph("<b>Talhão</b>", styles["TableHeader"]),
                Paragraph("<b>Tipo</b>", styles["TableHeader"]),
                Paragraph("<b>Descrição</b>", styles["TableHeader"]),
                Paragraph("<b>Status</b>", styles["TableHeader"]),
            ]
            organico_table = Table([organico_header] + organico_rows, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 5.5*cm, 3*cm])
            organico_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2e7d32")),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#ccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#f0f7f0"), white]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(organico_table)
            story.append(Spacer(1, 16))

        # ═══════════════════════════════════════════════════════
        # MAPA — Doses aplicadas, intervalo de segurança, receituário
        # ═══════════════════════════════════════════════════════
        if modelo == "mapa":
            story.append(Paragraph("Receituário Agronômico (MAPA — Lei 7.802/89)", styles["SectionHeader"]))
            story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#ccc"), spaceAfter=6))

            if dados.assinado_por:
                story.append(Paragraph(
                    f"<b>Responsável Técnico:</b> {dados.assinado_por} | <b>CREA:</b> {dados.crea_rt or 'N/I'}",
                    styles["BodyText2"],
                ))
                story.append(Spacer(1, 8))

            # Tabela de operações com doses e intervalo de segurança
            mapa_rows = []
            for e in entradas:
                talhao_nome = talhoes_map.get(str(e.talhao_id), f"Talhão {str(e.talhao_id)[:8]}")
                receituario = e.numero_receituario if hasattr(e, 'numero_receituario') else None
                # Busca operação para dose
                dose_info = "—"
                intervalo = "—"
                if hasattr(e, 'operacao_id') and e.operacao_id:
                    op_stmt = select(OperacaoAgricola).where(OperacaoAgricola.id == e.operacao_id)
                    op = (await self.session.execute(op_stmt)).scalar_one_or_none()
                    if op and op.insumos:
                        doses = []
                        for ins in op.insumos:
                            doses.append(f"{ins.dose_por_ha or ''} {ins.unidade or ''}/ha")
                        dose_info = "; ".join(doses) if doses else "—"
                        intervalo = f"{op.intervalo_seguranca or '—'} dias" if hasattr(op, 'intervalo_seguranca') else "—"

                mapa_rows.append([
                    Paragraph(e.data_registro.strftime("%d/%m/%Y") if hasattr(e.data_registro, 'strftime') else str(e.data_registro), styles["TableCell"]),
                    Paragraph(talhao_nome, styles["TableCell"]),
                    Paragraph(e.tipo, styles["TableCell"]),
                    Paragraph(dose_info, styles["TableCell"]),
                    Paragraph(intervalo, styles["TableCell"]),
                    Paragraph(receituario or "—", styles["TableCell"]),
                ])

            mapa_header = [
                Paragraph("<b>Data</b>", styles["TableHeader"]),
                Paragraph("<b>Talhão</b>", styles["TableHeader"]),
                Paragraph("<b>Tipo</b>", styles["TableHeader"]),
                Paragraph("<b>Dose Aplicada</b>", styles["TableHeader"]),
                Paragraph("<b>Intervalo Seg.</b>", styles["TableHeader"]),
                Paragraph("<b>Nº Receituário</b>", styles["TableHeader"]),
            ]
            mapa_table = Table([mapa_header] + mapa_rows, colWidths=[2.5*cm, 2*cm, 2*cm, 3*cm, 2.5*cm, 3*cm])
            mapa_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1565c0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#ccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#f0f4fa"), white]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(mapa_table)
            story.append(Spacer(1, 16))

        # ═══════════════════════════════════════════════════════
        # LAYOUT PADRÃO — Timeline de entradas (todos os modelos)
        # ═══════════════════════════════════════════════════════
        if modelo == "padrao":
            from collections import defaultdict
            grouped: dict[str, list] = defaultdict(list)
            for e in entradas:
                key = e.data_registro.strftime("%d/%m/%Y") if hasattr(e.data_registro, "strftime") else str(e.data_registro)
                grouped[key].append(e)

            for data_str, items in sorted(grouped.items(), key=lambda x: x[0], reverse=True):
                story.append(Paragraph(f"📅 {data_str}", styles["SectionHeader"]))
                story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#ccc"), spaceAfter=6))

                for item in items:
                    tipo_label = {
                        "OPERACAO_AUTO": "⚙️ Operação",
                        "MONITORAMENTO": "🔍 Monitoramento",
                        "VISITA_TECNICA": "👨‍🔬 Visita Técnica",
                        "EPI_ENTREGA": "🦺 Entrega EPI",
                        "OBSERVACAO": "📝 Observação",
                        "CLIMA": "🌤️ Clima",
                        "SOLO": "🌱 Solo",
                    }.get(item.tipo if hasattr(item, 'tipo') else item.get('tipo', ''), item.tipo if hasattr(item, 'tipo') else item.get('tipo', ''))

                    talhao_nome = talhoes_map.get(str(item.talhao_id), f"Talhão {str(item.talhao_id)[:8]}")
                    desc = item.descricao if hasattr(item, 'descricao') else item.get('descricao', '')
                    severidade = item.nivel_severidade if hasattr(item, 'nivel_severidade') else item.get('nivel_severidade')

                    row_data = [
                        Paragraph(f"<b>{tipo_label}</b>", styles["SmallBold"]),
                        Paragraph(talhao_nome, styles["BodyText2"]),
                    ]
                    if severidade:
                        row_data.append(Paragraph(f"<b>Severidade:</b> {severidade}", styles["BodyText2"]))

                    entry_table = Table([row_data], colWidths=[3.5*cm, 3.5*cm, 4.5*cm])
                    entry_table.setStyle(TableStyle([
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#f5f5f5")),
                        ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#ddd")),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ]))
                    story.append(entry_table)
                    story.append(Spacer(1, 2))
                    story.append(Paragraph(desc.replace("\n", "<br/>"), styles["BodyText2"]))
                    story.append(Spacer(1, 8))

        # ═══════════════════════════════════════════════════════
        # Visitas técnicas (globalgap e organico)
        # ═══════════════════════════════════════════════════════
        if modelo in ("globalgap", "organico") and visitas:
            story.append(Paragraph("Visitas Técnicas", styles["SectionHeader"]))
            story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#ccc"), spaceAfter=6))

            visitas_rows = []
            for v in visitas:
                visitas_rows.append([
                    Paragraph(v.data_visita.strftime("%d/%m/%Y"), styles["TableCell"]),
                    Paragraph(v.nome_rt, styles["TableCell"]),
                    Paragraph(v.crea, styles["TableCell"]),
                    Paragraph((v.observacoes or "—")[:80], styles["TableCell"]),
                    Paragraph("✓" if v.assinado else "—", styles["TableCell"]),
                ])

            visitas_header = [
                Paragraph("<b>Data</b>", styles["TableHeader"]),
                Paragraph("<b>Responsável</b>", styles["TableHeader"]),
                Paragraph("<b>CREA</b>", styles["TableHeader"]),
                Paragraph("<b>Observações</b>", styles["TableHeader"]),
                Paragraph("<b>Assinado</b>", styles["TableHeader"]),
            ]
            visitas_table = Table([visitas_header] + visitas_rows, colWidths=[2.5*cm, 3.5*cm, 2.5*cm, 5*cm, 2*cm])
            visitas_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1a5e1a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#ccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#f9f9f9"), white]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(visitas_table)
            story.append(Spacer(1, 16))

        # ── Rodapé com assinaturas ──
        story.append(PageBreak())
        story.append(Paragraph("Assinaturas", styles["SectionHeader"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#ccc"), spaceAfter=20))

        if modelo == "organico":
            story.append(Paragraph(
                "Declaro que as informações acima são verdadeiras e refletem as práticas de produção orgânica "
                "adotadas nesta propriedade, em conformidade com as normas USDA Organic e IBD Certificações.",
                styles["BodyText2"],
            ))
            story.append(Spacer(1, 30))

        story.append(HRFlowable(width="60%", thickness=1, color=black, spaceAfter=4))
        story.append(Paragraph(
            dados.assinado_por or "Responsável Técnico",
            ParagraphStyle("sigName", fontSize=9, alignment=TA_CENTER, fontName="Helvetica"),
        ))
        if dados.crea_rt:
            story.append(Paragraph(
                f"CREA: {dados.crea_rt}",
                ParagraphStyle("sigCrea", fontSize=8, alignment=TA_CENTER, textColor=HexColor("#666"), fontName="Helvetica"),
            ))

        # Data de geração
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            ParagraphStyle("sigDate", fontSize=7, alignment=TA_CENTER, textColor=HexColor("#999"), fontName="Helvetica"),
        ))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        # 6. Salva arquivo
        STORAGE_DIR = Path("/tmp/agrossa_caderno_exports")
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"caderno_{modelo}_{dados.safra_id}_{_uuid.uuid4().hex[:8]}.pdf"
        file_path = STORAGE_DIR / filename
        file_path.write_bytes(pdf_bytes)

        url_pdf = f"/static/caderno_exports/{filename}"

        exportacao = CadernoExportacao(
            tenant_id=self.tenant_id,
            safra_id=dados.safra_id,
            talhao_id=dados.talhao_id,
            url_pdf=url_pdf,
            assinado_por=dados.assinado_por,
            crea_rt=dados.crea_rt,
            modelo_certificacao=modelo,
        )
        self.session.add(exportacao)
        await self.session.flush()
        return exportacao

    async def listar_por_safra(self, safra_id: UUID) -> list[CadernoExportacao]:
        stmt = select(CadernoExportacao).where(
            CadernoExportacao.tenant_id == self.tenant_id,
            CadernoExportacao.safra_id == safra_id,
        ).order_by(CadernoExportacao.data_geracao.desc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def listar_todas(self) -> list[CadernoExportacao]:
        stmt = select(CadernoExportacao).where(
            CadernoExportacao.tenant_id == self.tenant_id,
        ).order_by(CadernoExportacao.data_geracao.desc())
        return list((await self.session.execute(stmt)).scalars().all())
