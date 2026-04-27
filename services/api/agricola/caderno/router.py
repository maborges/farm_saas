from fastapi import APIRouter, Depends, status, Request, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from pathlib import Path

from core.constants import PlanTier
from core.dependencies import get_tenant_id, require_module, require_role, require_tier, get_session_with_tenant
from agricola.caderno.models import CadernoExportacao
from agricola.caderno.schemas import (
    EntradaCreate,
    EntradaUpdate,
    EntradaDeleteRequest,
    EntradaResponse,
    FotoResponse,
    VisitaTecnicaCreate,
    VisitaTecnicaResponse,
    AssinarVisitaRequest,
    EPIEntregaCreate,
    EPIEntregaResponse,
    ExportacaoCreate,
    ExportacaoResponse,
    AssinarExportacaoRequest,
    TimelineItem,
)
from agricola.caderno.service import (
    CadernoCampoService,
    VisitaTecnicaService,
    EPIEntregaService,
    CadernoExportacaoService,
)

router = APIRouter(prefix="/caderno", tags=["Caderno de Campo"])

_MODULE = require_module("A1_PLANEJAMENTO")


# ─── Timeline ─────────────────────────────────────────────────────────────────

@router.get("/safra/{safra_id}/timeline", response_model=List[TimelineItem])
async def timeline(
    safra_id: UUID,
    talhao_id: UUID | None = None,
    tipo: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    incluir_excluidas: bool = False,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
):
    svc = CadernoCampoService(session, tenant_id)
    return await svc.timeline(
        safra_id,
        talhao_id=talhao_id,
        tipo=tipo,
        data_inicio=data_inicio,
        data_fim=data_fim,
        incluir_excluidas=incluir_excluidas,
    )


@router.get("/timeline", response_model=List[TimelineItem])
async def timeline_global(
    safra_id: UUID | None = None,
    talhao_id: UUID | None = None,
    tipo: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    incluir_excluidas: bool = False,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
):
    """Timeline global cross-safras. Se safra_id não informado, agrega todas as safras ativas."""
    from agricola.safras.models import Safra

    if safra_id:
        # Comportamento normal: timeline de uma safra específica
        svc = CadernoCampoService(session, tenant_id)
        return await svc.timeline(
            safra_id,
            talhao_id=talhao_id,
            tipo=tipo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            incluir_excluidas=incluir_excluidas,
        )

    # Cross-safras: busca todas as safras ativas do tenant
    svc = CadernoCampoService(session, tenant_id)
    safras = await svc.listar_safras_ativas()

    if not safras:
        return []

    # Agrega timeline de todas as safras
    svc = CadernoCampoService(session, tenant_id)
    todos_items = []
    for safra in safras:
        items = await svc.timeline(
            safra.id,
            talhao_id=talhao_id,
            tipo=tipo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            incluir_excluidas=incluir_excluidas,
        )
        todos_items.extend(items)

    # Ordena por data desc
    todos_items.sort(key=lambda x: x.data_registro, reverse=True)
    return todos_items


# ─── Alertas ──────────────────────────────────────────────────────────────────

@router.get("/alertas")
async def caderno_alertas(
    safra_id: UUID | None = None,
    dias_sem_registro: int = 7,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
):
    """Retorna safras ativas sem registros há X dias (padrão: 7 dias, configurável)."""
    svc = CadernoCampoService(session, tenant_id)
    return await svc.listar_alertas(safra_id=safra_id, dias_sem_registro=dias_sem_registro)


# ─── Entradas ─────────────────────────────────────────────────────────────────

@router.post("/entradas", response_model=EntradaResponse, status_code=status.HTTP_201_CREATED)
async def criar_entrada(
    dados: EntradaCreate,
    request: Request,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
    user: dict = Depends(require_role(["admin", "agronomo", "operador", "gerente"])),
):
    svc = CadernoCampoService(session, tenant_id)
    usuario_id = UUID(user["sub"])
    ip = request.client.host if request.client else None
    entrada = await svc.criar_entrada(dados, usuario_id=usuario_id, ip=ip)
    await session.commit()
    await session.refresh(entrada)
    return EntradaResponse.model_validate(entrada)


@router.get("/entradas/{entrada_id}", response_model=EntradaResponse)
async def detalhar_entrada(
    entrada_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
):
    svc = CadernoCampoService(session, tenant_id)
    return EntradaResponse.model_validate(await svc.get_or_fail(entrada_id))


@router.patch("/entradas/{entrada_id}", response_model=EntradaResponse)
async def atualizar_entrada(
    entrada_id: UUID,
    dados: EntradaUpdate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
    user: dict = Depends(require_role(["admin", "agronomo", "gerente"])),
):
    svc = CadernoCampoService(session, tenant_id)
    entrada = await svc.update(entrada_id, dados.model_dump(exclude_none=True))
    await session.commit()
    await session.refresh(entrada)
    return EntradaResponse.model_validate(entrada)


@router.delete("/entradas/{entrada_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_entrada(
    entrada_id: UUID,
    body: EntradaDeleteRequest,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
    user: dict = Depends(require_role(["admin", "agronomo"])),
):
    svc = CadernoCampoService(session, tenant_id)
    await svc.soft_delete(entrada_id, body.motivo_exclusao)
    await session.commit()


@router.post("/entradas/{entrada_id}/fotos", response_model=FotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_foto_entrada(
    entrada_id: UUID,
    file: UploadFile = File(...),
    latitude: float | None = Form(None),
    longitude: float | None = Form(None),
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
    user: dict = Depends(require_role(["admin", "agronomo", "operador", "gerente"])),
):
    """Upload de foto para uma entrada do caderno. Armazena metadados; arquivo vai para storage local/S3."""
    # Verifica se entrada existe e pertence ao tenant
    svc = CadernoCampoService(session, tenant_id)
    entrada = await svc.get_or_fail(entrada_id)

    # Em produção: upload para S3/MinIO. Por enquanto: path local.
    import uuid as _uuid
    from pathlib import Path
    from datetime import datetime as _dt

    STORAGE_DIR = Path("/tmp/agrossa_fotos_caderno")
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "").suffix or ".jpg"
    filename = f"{_uuid.uuid4()}{ext}"
    file_path = STORAGE_DIR / filename

    content = await file.read()
    file_path.write_bytes(content)

    url = f"/static/fotos_caderno/{filename}"

    foto = await svc.adicionar_foto(
        entrada_id=entrada_id,
        url=url,
        latitude=latitude,
        longitude=longitude,
        data_captura=_dt.now(),
    )

    # Rastreia uso de storage do tenant
    from core.services.storage_service import increment_storage
    await increment_storage(session, tenant_id, len(content))

    await session.commit()
    return FotoResponse.model_validate(foto)


# ─── Visitas Técnicas ─────────────────────────────────────────────────────────

@router.post("/visitas", response_model=VisitaTecnicaResponse, status_code=status.HTTP_201_CREATED)
async def criar_visita(
    dados: VisitaTecnicaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
    user: dict = Depends(require_role(["admin", "agronomo"])),
):
    svc = VisitaTecnicaService(session, tenant_id)
    visita = await svc.criar(dados, usuario_id=UUID(user["sub"]))
    await session.commit()
    await session.refresh(visita)
    return VisitaTecnicaResponse.model_validate(visita)


@router.get("/visitas/safra/{safra_id}", response_model=List[VisitaTecnicaResponse])
async def listar_visitas(
    safra_id: UUID,
    talhao_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
):
    svc = VisitaTecnicaService(session, tenant_id)
    return [VisitaTecnicaResponse.model_validate(v) for v in await svc.listar_por_safra(safra_id, talhao_id)]


@router.post("/visitas/{visita_id}/assinar", response_model=VisitaTecnicaResponse)
async def assinar_visita(
    visita_id: UUID,
    body: AssinarVisitaRequest,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
    user: dict = Depends(require_role(["admin", "agronomo"])),
):
    svc = VisitaTecnicaService(session, tenant_id)
    visita = await svc.assinar(visita_id, body.nome_rt, body.crea)
    await session.commit()
    return VisitaTecnicaResponse.model_validate(visita)


# ─── EPIs ──────────────────────────────────────────────────────────────────────

@router.post("/epis", response_model=EPIEntregaResponse, status_code=status.HTTP_201_CREATED)
async def registrar_epi(
    dados: EPIEntregaCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
    user: dict = Depends(require_role(["admin", "agronomo", "gerente"])),
):
    svc = EPIEntregaService(session, tenant_id)
    epi = await svc.criar(dados)
    await session.commit()
    await session.refresh(epi)
    return EPIEntregaResponse.model_validate(epi)


@router.get("/epis", response_model=List[EPIEntregaResponse])
async def listar_epis(
    operacao_id: UUID | None = None,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
):
    svc = EPIEntregaService(session, tenant_id)
    return [EPIEntregaResponse.model_validate(e) for e in await svc.listar(operacao_id)]


# ─── Exportação PDF ───────────────────────────────────────────────────────────

@router.post("/exportar", response_model=ExportacaoResponse, status_code=status.HTTP_201_CREATED)
async def exportar_caderno(
    dados: ExportacaoCreate,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
    _tier: None = Depends(require_tier(PlanTier.ENTERPRISE)),
    user: dict = Depends(require_role(["admin", "agronomo", "gerente", "proprietario"])),
):
    svc = CadernoExportacaoService(session, tenant_id)
    exportacao = await svc.gerar(dados)
    await session.commit()
    await session.refresh(exportacao)
    return ExportacaoResponse.model_validate(exportacao)


@router.get("/exportacoes/safra/{safra_id}", response_model=List[ExportacaoResponse])
async def listar_exportacoes(
    safra_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
    _tier: None = Depends(require_tier(PlanTier.ENTERPRISE)),
):
    svc = CadernoExportacaoService(session, tenant_id)
    return [ExportacaoResponse.model_validate(e) for e in await svc.listar_por_safra(safra_id)]


@router.get("/exportacoes", response_model=List[ExportacaoResponse])
async def listar_exportacoes_global(
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
    _tier: None = Depends(require_tier(PlanTier.ENTERPRISE)),
):
    """Lista todas as exportações do tenant, cross-safras."""
    svc = CadernoExportacaoService(session, tenant_id)
    return [ExportacaoResponse.model_validate(e) for e in await svc.listar_todas()]


@router.get("/exportacoes/{exportacao_id}/download")
async def download_pdf(
    exportacao_id: UUID,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
    _tier: None = Depends(require_tier(PlanTier.ENTERPRISE)),
):
    """Download do PDF do caderno de campo."""
    svc = CadernoExportacaoService(session, tenant_id)
    exportacao = await svc.get_or_fail(exportacao_id)

    filename = exportacao.url_pdf.split("/")[-1]
    file_path = Path("/tmp/agrossa_caderno_exports") / filename

    if not file_path.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="PDF não encontrado. Gere novamente.")

    return FileResponse(
        path=str(file_path),
        filename=f"Caderno_Campo_{exportacao.safra_id}.pdf",
        media_type="application/pdf",
    )


@router.post("/exportacoes/{exportacao_id}/assinar", response_model=ExportacaoResponse)
async def assinar_exportacao(
    exportacao_id: UUID,
    body: AssinarExportacaoRequest,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
    _tier: None = Depends(require_tier(PlanTier.ENTERPRISE)),
    user: dict = Depends(require_role(["admin", "agronomo"])),
):
    """Registra assinatura do RT na exportação do caderno."""
    from datetime import date, timedelta
    svc = CadernoExportacaoService(session, tenant_id)
    exportacao = await svc.get_or_fail(exportacao_id)

    # Validação do CREA: verifica se está vencido ou vencendo em 30 dias
    if body.crea_validade:
        hoje = date.today()
        dias_para_vencer = (body.crea_validade - hoje).days
        if dias_para_vencer < 0:
            raise BusinessRuleError(
                f"O CREA informado está vencido desde {body.crea_validade.strftime('%d/%m/%Y')}. "
                "Renove o registro antes de assinar."
            )
        elif dias_para_vencer <= 30:
            raise BusinessRuleError(
                f"O CREA informado vence em {dias_para_vencer} dias ({body.crea_validade.strftime('%d/%m/%Y')}). "
                "Renove o registro antes de assinar."
            )

    exportacao.assinado_por = body.assinado_por
    exportacao.crea_rt = body.crea_rt
    exportacao.crea_validade = body.crea_validade
    await session.commit()
    await session.refresh(exportacao)
    return ExportacaoResponse.model_validate(exportacao)


@router.post("/exportacoes/assinar-ultima", response_model=ExportacaoResponse)
async def assinar_ultima_exportacao(
    body: dict,
    session: AsyncSession = Depends(get_session_with_tenant),
    tenant_id: UUID = Depends(get_tenant_id),
    _: None = Depends(_MODULE),
    _tier: None = Depends(require_tier(PlanTier.ENTERPRISE)),
    user: dict = Depends(require_role(["admin", "agronomo"])),
):
    """Assina a última exportação de uma safra. Cria uma nova se não existir."""
    from uuid import UUID as _UUID
    from datetime import datetime as _dt, date as _date
    from agricola.caderno.schemas import ExportacaoCreate

    safra_id = _UUID(body["safra_id"])
    assinado_por = body["assinado_por"]
    crea_rt = body["crea_rt"]
    crea_validade = body.get("crea_validade")

    # Validação do CREA: verifica se está vencido ou vencendo em 30 dias
    if crea_validade:
        cria_validade_date = _date.fromisoformat(crea_validade) if isinstance(crea_validade, str) else crea_validade
        hoje = _date.today()
        dias_para_vencer = (cria_validade_date - hoje).days
        if dias_para_vencer < 0:
            raise BusinessRuleError(
                f"O CREA informado está vencido desde {cria_validade_date.strftime('%d/%m/%Y')}. "
                "Renove o registro antes de assinar."
            )
        elif dias_para_vencer <= 30:
            raise BusinessRuleError(
                f"O CREA informado vence em {dias_para_vencer} dias ({cria_validade_date.strftime('%d/%m/%Y')}). "
                "Renove o registro antes de assinar."
            )

    svc = CadernoExportacaoService(session, tenant_id)
    exportacoes = await svc.listar_por_safra(safra_id)

    if exportacoes:
        # Usa a mais recente
        exportacao = exportacoes[0]
    else:
        # Cria uma nova exportação placeholder
        exportacao = await svc.gerar(ExportacaoCreate(safra_id=safra_id))

    exportacao.assinado_por = assinado_por
    exportacao.crea_rt = crea_rt
    exportacao.crea_validade = cria_validade_date if crea_validade else None
    await session.commit()
    await session.refresh(exportacao)
    return ExportacaoResponse.model_validate(exportacao)
