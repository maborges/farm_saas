# 🔌 API Admin SaaS - Exemplos de Implementação

## 📋 Visão Geral

Este documento contém exemplos práticos de implementação das APIs de administração do SaaS.

---

## 🏗️ Estrutura Base das Rotas

### Router Principal (`services/api/app/admin/router.py`)

```python
from fastapi import APIRouter, Depends
from app.admin import (
    dashboard,
    assinantes,
    assinaturas,
    suporte,
    pacotes,
    cupons,
    financeiro,
    emails,
    modulos,
    config
)
from app.core.security import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

# Incluir sub-routers
router.include_router(
    dashboard.router,
    prefix="/dashboard",
    dependencies=[Depends(require_admin)]
)

router.include_router(
    assinantes.router,
    prefix="/assinantes",
    dependencies=[Depends(require_admin)]
)

router.include_router(
    assinaturas.router,
    prefix="/assinaturas",
    dependencies=[Depends(require_admin)]
)

router.include_router(
    suporte.router,
    prefix="/suporte",
    dependencies=[Depends(require_admin)]
)

router.include_router(
    pacotes.router,
    prefix="/pacotes",
    dependencies=[Depends(require_admin)]
)

router.include_router(
    cupons.router,
    prefix="/cupons",
    dependencies=[Depends(require_admin)]
)

router.include_router(
    financeiro.router,
    prefix="/financeiro",
    dependencies=[Depends(require_admin)]
)

router.include_router(
    emails.router,
    prefix="/emails",
    dependencies=[Depends(require_admin)]
)

router.include_router(
    modulos.router,
    prefix="/modulos",
    dependencies=[Depends(require_admin)]
)

router.include_router(
    config.router,
    prefix="/config",
    dependencies=[Depends(require_admin)]
)
```

---

## 📊 Dashboard - Métricas

### Router (`app/admin/dashboard/router.py`)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.admin.dashboard import service, schemas

router = APIRouter()

@router.get("/metricas", response_model=schemas.DashboardMetrics)
async def obter_metricas_dashboard(
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna métricas principais para o dashboard admin
    """
    return await service.obter_metricas(db)

@router.get("/novos-assinantes", response_model=schemas.NovosAssinantesChart)
async def obter_grafico_novos_assinantes(
    meses: int = 12,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna dados para o gráfico de novos assinantes
    """
    return await service.obter_novos_assinantes_por_mes(db, meses)

@router.get("/alertas", response_model=list[schemas.AlertaCritico])
async def obter_alertas_criticos(
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna alertas que requerem atenção imediata
    """
    return await service.obter_alertas_criticos(db)
```

### Schemas (`app/admin/dashboard/schemas.py`)

```python
from pydantic import BaseModel
from datetime import datetime

class MetricaVariacao(BaseModel):
    total: int
    variacao_percentual: float
    periodo: str

class DashboardMetrics(BaseModel):
    # Assinantes
    novos_assinantes: MetricaVariacao
    assinantes_ativos: int
    assinantes_inativos: int
    assinantes_trial: int

    # Organização
    total_grupos_fazendas: int
    total_fazendas: int

    # Suporte
    chamados_abertos: int
    chamados_pendentes: int
    tempo_medio_resposta_horas: float
    satisfacao_media: float

    # Receita
    mrr: float
    taxa_churn: float

class NovosAssinantesChart(BaseModel):
    labels: list[str]  # ["Jan", "Fev", "Mar", ...]
    valores: list[int]
    comparacao_anterior: list[int]

class AlertaCritico(BaseModel):
    tipo: str  # pagamento_pendente, ticket_critico, storage_limite
    titulo: str
    descricao: str
    severidade: str  # alta, media, baixa
    link: str
    data: datetime
```

### Service (`app/admin/dashboard/service.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from datetime import datetime, timedelta
from app.models import Tenant, Subscription, Ticket
from app.admin.dashboard import schemas

async def obter_metricas(db: AsyncSession) -> schemas.DashboardMetrics:
    """
    Calcula todas as métricas do dashboard
    """
    # Novos assinantes
    mes_atual = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    mes_anterior = (mes_atual - timedelta(days=1)).replace(day=1)

    novos_mes_atual = await db.scalar(
        select(func.count(Tenant.id))
        .where(Tenant.data_cadastro >= mes_atual)
    )

    novos_mes_anterior = await db.scalar(
        select(func.count(Tenant.id))
        .where(and_(
            Tenant.data_cadastro >= mes_anterior,
            Tenant.data_cadastro < mes_atual
        ))
    )

    variacao = ((novos_mes_atual - novos_mes_anterior) / novos_mes_anterior * 100
                if novos_mes_anterior > 0 else 0)

    # Assinantes por status
    status_counts = await db.execute(
        select(
            Tenant.status,
            func.count(Tenant.id)
        ).group_by(Tenant.status)
    )
    status_dict = dict(status_counts.all())

    # Suporte
    tickets_abertos = await db.scalar(
        select(func.count(Ticket.id))
        .where(Ticket.status.in_(['aberto', 'em_atendimento']))
    )

    # Tempo médio de resposta (em horas)
    tempo_medio = await db.scalar(
        select(
            func.avg(
                func.extract('epoch',
                    Ticket.data_primeira_resposta - Ticket.data_abertura
                ) / 3600
            )
        ).where(
            and_(
                Ticket.data_primeira_resposta.isnot(None),
                Ticket.data_abertura >= mes_atual
            )
        )
    ) or 0

    # Satisfação média
    satisfacao = await db.scalar(
        select(func.avg(Ticket.avaliacao_nota))
        .where(
            and_(
                Ticket.avaliacao_nota.isnot(None),
                Ticket.data_resolucao >= mes_atual
            )
        )
    ) or 0

    # MRR
    mrr = await db.scalar(
        select(
            func.sum(
                case(
                    (Subscription.tipo == 'mensal',
                     Subscription.valor_mensal - Subscription.valor_desconto),
                    (Subscription.tipo == 'anual',
                     Subscription.valor_mensal - Subscription.valor_desconto),
                    else_=0
                )
            )
        ).where(Subscription.status == 'ativa')
    ) or 0

    # Taxa de Churn
    total_inicio_mes = await db.scalar(
        select(func.count(Subscription.id))
        .where(and_(
            Subscription.status == 'ativa',
            Subscription.data_inicio < mes_atual
        ))
    )

    cancelados_mes = await db.scalar(
        select(func.count(Subscription.id))
        .where(and_(
            Subscription.status == 'cancelada',
            Subscription.data_cancelamento >= mes_atual
        ))
    )

    taxa_churn = (cancelados_mes / total_inicio_mes * 100
                  if total_inicio_mes > 0 else 0)

    return schemas.DashboardMetrics(
        novos_assinantes=schemas.MetricaVariacao(
            total=novos_mes_atual,
            variacao_percentual=round(variacao, 2),
            periodo="vs. mês anterior"
        ),
        assinantes_ativos=status_dict.get('ativo', 0),
        assinantes_inativos=status_dict.get('suspenso', 0) + status_dict.get('cancelado', 0),
        assinantes_trial=status_dict.get('trial', 0),
        total_grupos_fazendas=0,  # Implementar
        total_fazendas=0,  # Implementar
        chamados_abertos=tickets_abertos,
        chamados_pendentes=0,  # Implementar
        tempo_medio_resposta_horas=round(tempo_medio, 2),
        satisfacao_media=round(satisfacao, 2),
        mrr=float(mrr),
        taxa_churn=round(taxa_churn, 2)
    )

async def obter_novos_assinantes_por_mes(
    db: AsyncSession,
    meses: int = 12
) -> schemas.NovosAssinantesChart:
    """
    Retorna dados de novos assinantes por mês
    """
    data_inicial = datetime.now() - timedelta(days=meses * 30)

    result = await db.execute(
        select(
            func.to_char(Tenant.data_cadastro, 'YYYY-MM').label('mes'),
            func.count(Tenant.id).label('total')
        )
        .where(Tenant.data_cadastro >= data_inicial)
        .group_by('mes')
        .order_by('mes')
    )

    dados = result.all()

    # Formatar labels (Jan, Fev, Mar...)
    meses_pt = {
        '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr',
        '05': 'Mai', '06': 'Jun', '07': 'Jul', '08': 'Ago',
        '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
    }

    labels = [meses_pt[mes.split('-')[1]] for mes, _ in dados]
    valores = [total for _, total in dados]

    return schemas.NovosAssinantesChart(
        labels=labels,
        valores=valores,
        comparacao_anterior=[]  # Implementar comparação
    )

async def obter_alertas_criticos(
    db: AsyncSession
) -> list[schemas.AlertaCritico]:
    """
    Retorna lista de alertas que requerem atenção
    """
    alertas = []

    # Tickets críticos próximos ao SLA
    tickets_sla = await db.execute(
        select(Ticket)
        .where(and_(
            Ticket.status.in_(['aberto', 'em_atendimento']),
            Ticket.sla_vencimento < datetime.now() + timedelta(hours=2)
        ))
        .limit(5)
    )

    for ticket in tickets_sla.scalars():
        alertas.append(schemas.AlertaCritico(
            tipo='ticket_sla',
            titulo=f'Ticket #{ticket.numero} próximo ao SLA',
            descricao=ticket.assunto,
            severidade='alta',
            link=f'/admin/suporte/tickets/{ticket.id}',
            data=ticket.sla_vencimento
        ))

    # Assinantes com storage próximo ao limite
    tenants_storage = await db.execute(
        select(Tenant)
        .where(and_(
            Tenant.status == 'ativo',
            Tenant.storage_usado_mb > Tenant.storage_limite_mb * 0.9
        ))
        .limit(5)
    )

    for tenant in tenants_storage.scalars():
        percentual = (tenant.storage_usado_mb / tenant.storage_limite_mb) * 100
        alertas.append(schemas.AlertaCritico(
            tipo='storage_limite',
            titulo=f'{tenant.nome_empresa} - Storage em {percentual:.0f}%',
            descricao=f'Storage: {tenant.storage_usado_mb}MB / {tenant.storage_limite_mb}MB',
            severidade='media',
            link=f'/admin/assinantes/{tenant.id}',
            data=datetime.now()
        ))

    return alertas
```

---

## 👥 Assinantes - CRUD e Ações

### Router (`app/admin/assinantes/router.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_admin_user
from app.models import AdminUser
from app.admin.assinantes import service, schemas
from app.admin.assinantes.actions import impersonate, reset_password

router = APIRouter()

@router.get("", response_model=schemas.AssinantesListResponse)
async def listar_assinantes(
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os assinantes com filtros e paginação
    """
    return await service.listar_assinantes(
        db, page, per_page, status, search
    )

@router.get("/{assinante_id}", response_model=schemas.AssinanteDetalhado)
async def obter_assinante(
    assinante_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna detalhes completos de um assinante
    """
    assinante = await service.obter_assinante_detalhado(db, assinante_id)
    if not assinante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assinante não encontrado"
        )
    return assinante

@router.post("/{assinante_id}/impersonate", response_model=schemas.ImpersonateResponse)
async def impersonar_assinante(
    assinante_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Gera token temporário para acessar o tenant como admin
    """
    return await impersonate.impersonar_tenant(db, assinante_id, admin.id)

@router.post("/{assinante_id}/reset-password", response_model=schemas.ResetPasswordResponse)
async def resetar_senha_assinante(
    assinante_id: UUID,
    payload: schemas.ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Reseta a senha do assinante e opcionalmente envia email
    """
    return await reset_password.resetar_senha(
        db, assinante_id, payload, admin.id
    )

@router.patch("/{assinante_id}/status")
async def alterar_status_assinante(
    assinante_id: UUID,
    payload: schemas.AlterarStatusRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Suspende, reativa ou cancela assinante
    """
    return await service.alterar_status(
        db, assinante_id, payload.novo_status, payload.motivo, admin.id
    )
```

### Actions - Impersonate (`app/admin/assinantes/actions/impersonate.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timedelta
from app.models import Tenant, AdminAuditLog
from app.core.security import create_access_token
from app.admin.assinantes import schemas

async def impersonar_tenant(
    db: AsyncSession,
    tenant_id: UUID,
    admin_id: UUID
) -> schemas.ImpersonateResponse:
    """
    Gera token temporário para admin acessar tenant
    """
    # Buscar tenant
    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        raise ValueError("Tenant não encontrado")

    # Gerar token temporário (1 hora)
    token_data = {
        "sub": str(tenant_id),
        "tenant_id": str(tenant_id),
        "is_impersonated": True,
        "impersonated_by": str(admin_id),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    access_token = create_access_token(token_data)

    # Registrar ação no audit log
    audit = AdminAuditLog(
        admin_user_id=admin_id,
        acao="tenant.impersonate",
        entidade="tenant",
        entidade_id=tenant_id,
        descricao=f"Admin impersonou tenant {tenant.nome_empresa}"
    )
    db.add(audit)
    await db.commit()

    # Montar URL do tenant
    tenant_url = f"https://{tenant.subdomain}.agrosass.com"

    return schemas.ImpersonateResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600,
        tenant_url=tenant_url
    )
```

### Actions - Reset Password (`app/admin/assinantes/actions/reset_password.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import secrets
import string
from app.models import Tenant, AdminAuditLog
from app.core.security import hash_password
from app.core.email import send_email
from app.admin.assinantes import schemas

def gerar_senha_aleatoria(tamanho: int = 12) -> str:
    """
    Gera senha aleatória segura
    """
    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(secrets.choice(caracteres) for _ in range(tamanho))

async def resetar_senha(
    db: AsyncSession,
    tenant_id: UUID,
    payload: schemas.ResetPasswordRequest,
    admin_id: UUID
) -> schemas.ResetPasswordResponse:
    """
    Reseta senha do responsável pelo tenant
    """
    # Buscar tenant
    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        raise ValueError("Tenant não encontrado")

    # Gerar ou usar senha fornecida
    senha_temporaria = payload.senha_temporaria or gerar_senha_aleatoria()

    # Buscar usuário responsável no banco do tenant
    # (Aqui você precisa implementar a lógica de acesso ao banco do tenant)
    # Por simplicidade, vou mostrar a estrutura

    senha_hash = hash_password(senha_temporaria)

    # Atualizar senha no banco do tenant
    # await atualizar_senha_usuario_tenant(tenant.database_name, tenant.email, senha_hash)

    # Registrar no audit log
    audit = AdminAuditLog(
        admin_user_id=admin_id,
        acao="tenant.reset_password",
        entidade="tenant",
        entidade_id=tenant_id,
        descricao=f"Senha resetada para {tenant.nome_empresa}"
    )
    db.add(audit)
    await db.commit()

    # Enviar email se solicitado
    if payload.enviar_email:
        await send_email(
            to=tenant.email,
            subject="Redefinição de Senha - AgroSaaS",
            template="password_reset",
            context={
                "nome_responsavel": tenant.nome_responsavel,
                "senha_temporaria": senha_temporaria,
                "tenant_url": f"https://{tenant.subdomain}.agrosass.com",
                "forcar_troca": payload.forcar_troca
            }
        )

    return schemas.ResetPasswordResponse(
        success=True,
        senha_temporaria=senha_temporaria if not payload.enviar_email else None,
        email_enviado=payload.enviar_email
    )
```

---

## 🎫 Suporte - Sistema de Tickets

### Router (`app/admin/suporte/router.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_admin_user
from app.models import AdminUser
from app.admin.suporte import service, schemas

router = APIRouter()

@router.get("/tickets", response_model=schemas.TicketsListResponse)
async def listar_tickets(
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    prioridade: str | None = None,
    atendente_id: UUID | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista tickets com filtros
    """
    return await service.listar_tickets(
        db, page, per_page, status, prioridade, atendente_id
    )

@router.get("/tickets/{ticket_id}", response_model=schemas.TicketDetalhado)
async def obter_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna detalhes completos do ticket incluindo mensagens
    """
    ticket = await service.obter_ticket_detalhado(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    return ticket

@router.post("/tickets/{ticket_id}/atribuir")
async def atribuir_ticket(
    ticket_id: UUID,
    atendente_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Atribui ticket para um atendente (ou para si mesmo se não informar)
    """
    atendente = atendente_id or admin.id
    return await service.atribuir_ticket(db, ticket_id, atendente, admin.id)

@router.post("/tickets/{ticket_id}/responder", response_model=schemas.TicketMensagem)
async def responder_ticket(
    ticket_id: UUID,
    payload: schemas.ResponderTicketRequest,
    anexos: list[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Adiciona resposta ao ticket
    """
    return await service.responder_ticket(
        db, ticket_id, payload.mensagem, admin.id, anexos
    )

@router.patch("/tickets/{ticket_id}/status")
async def alterar_status_ticket(
    ticket_id: UUID,
    payload: schemas.AlterarStatusTicketRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Altera status do ticket (em_atendimento, resolvido, fechado)
    """
    return await service.alterar_status_ticket(
        db, ticket_id, payload.novo_status, admin.id
    )

@router.get("/metricas", response_model=schemas.MetricasSuporte)
async def obter_metricas_suporte(
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna métricas de suporte (SLA, tempo médio, satisfação)
    """
    return await service.obter_metricas_suporte(db)
```

### Service - Responder Ticket (`app/admin/suporte/service.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime
from app.models import Ticket, TicketMensagem, TicketAnexo
from app.core.storage import upload_file
from app.core.notificacao import notificar_usuario
from app.admin.suporte import schemas

async def responder_ticket(
    db: AsyncSession,
    ticket_id: UUID,
    mensagem: str,
    admin_id: UUID,
    anexos: list = None
) -> schemas.TicketMensagem:
    """
    Adiciona resposta do atendente ao ticket
    """
    # Buscar ticket
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise ValueError("Ticket não encontrado")

    # Buscar admin
    from app.models import AdminUser
    admin = await db.get(AdminUser, admin_id)

    # Criar mensagem
    nova_mensagem = TicketMensagem(
        ticket_id=ticket_id,
        autor_tipo='atendente',
        autor_id=admin_id,
        autor_nome=admin.nome,
        mensagem=mensagem
    )
    db.add(nova_mensagem)

    # Atualizar data_primeira_resposta se for a primeira
    if not ticket.data_primeira_resposta:
        ticket.data_primeira_resposta = datetime.now()

    # Atualizar status
    if ticket.status == 'aberto':
        ticket.status = 'em_atendimento'

    # Upload de anexos
    if anexos:
        for anexo in anexos:
            # Upload para storage
            url = await upload_file(
                anexo.file,
                f"tickets/{ticket_id}/{anexo.filename}"
            )

            ticket_anexo = TicketAnexo(
                mensagem_id=nova_mensagem.id,
                nome_arquivo=anexo.filename,
                tamanho_bytes=anexo.size,
                mime_type=anexo.content_type,
                url=url
            )
            db.add(ticket_anexo)

    await db.commit()
    await db.refresh(nova_mensagem)

    # Notificar cliente
    await notificar_usuario(
        tenant_id=ticket.tenant_id,
        tipo='ticket_resposta',
        dados={
            'ticket_numero': ticket.numero,
            'mensagem': mensagem
        }
    )

    return nova_mensagem
```

---

## 💼 Pacotes - CRUD

### Router (`app/admin/pacotes/router.py`)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.core.security import require_permission
from app.admin.pacotes import service, schemas

router = APIRouter()

@router.get("", response_model=list[schemas.Pacote])
async def listar_pacotes(
    apenas_ativos: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os pacotes
    """
    return await service.listar_pacotes(db, apenas_ativos)

@router.get("/{pacote_id}", response_model=schemas.PacoteDetalhado)
async def obter_pacote(
    pacote_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna detalhes do pacote incluindo módulos
    """
    return await service.obter_pacote_detalhado(db, pacote_id)

@router.post("", response_model=schemas.Pacote)
async def criar_pacote(
    payload: schemas.CriarPacoteRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("pacotes:create"))
):
    """
    Cria novo pacote comercial
    """
    return await service.criar_pacote(db, payload)

@router.put("/{pacote_id}", response_model=schemas.Pacote)
async def atualizar_pacote(
    pacote_id: UUID,
    payload: schemas.AtualizarPacoteRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("pacotes:update"))
):
    """
    Atualiza pacote existente
    """
    return await service.atualizar_pacote(db, pacote_id, payload)

@router.delete("/{pacote_id}")
async def deletar_pacote(
    pacote_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("pacotes:delete"))
):
    """
    Desativa pacote (soft delete)
    """
    return await service.deletar_pacote(db, pacote_id)

@router.get("/{pacote_id}/assinantes", response_model=list[schemas.AssinantePacote])
async def listar_assinantes_pacote(
    pacote_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os assinantes deste pacote
    """
    return await service.listar_assinantes_pacote(db, pacote_id)
```

---

## ⚙️ Configurações

### Router (`app/admin/config/router.py`)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_role
from app.admin.config import service, schemas

router = APIRouter()

@router.get("/geral", response_model=schemas.ConfigGeral)
async def obter_config_geral(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("super_admin"))
):
    """
    Retorna configurações gerais do sistema
    """
    return await service.obter_config_geral(db)

@router.put("/geral")
async def atualizar_config_geral(
    payload: schemas.AtualizarConfigGeral,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("super_admin"))
):
    """
    Atualiza configurações gerais
    """
    return await service.atualizar_config_geral(db, payload)

@router.get("/smtp", response_model=schemas.ConfigSMTP)
async def obter_config_smtp(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("super_admin"))
):
    return await service.obter_config_smtp(db)

@router.put("/smtp")
async def atualizar_config_smtp(
    payload: schemas.ConfigSMTP,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("super_admin"))
):
    return await service.atualizar_config_smtp(db, payload)

@router.post("/smtp/testar")
async def testar_smtp(
    email_destino: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("super_admin"))
):
    """
    Envia email de teste
    """
    return await service.testar_config_smtp(db, email_destino)

# Repetir para: storage, push, stripe, transferencia_bancaria...
```

---

## 🔐 Segurança e Permissões

### Dependency para verificar permissões

```python
# app/core/security.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import AdminUser

security = HTTPBearer()

PERMISSIONS = {
    "super_admin": ["*"],
    "admin": [
        "dashboard:view",
        "assinantes:*",
        "assinaturas:*",
        "suporte:*",
        "pacotes:*",
        "cupons:*",
        "emails:*",
        "financeiro:view"
    ],
    "suporte": [
        "dashboard:view",
        "assinantes:view",
        "suporte:*"
    ],
    "financeiro": [
        "dashboard:view",
        "financeiro:*",
        "assinantes:view"
    ],
    "comercial": [
        "dashboard:view",
        "pacotes:*",
        "cupons:*",
        "assinaturas:*"
    ]
}

async def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> AdminUser:
    """
    Valida token e retorna admin user
    """
    token = credentials.credentials
    # Validar token JWT
    payload = decode_jwt(token)

    admin_id = payload.get("sub")
    admin = await db.get(AdminUser, admin_id)

    if not admin or not admin.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    return admin

def require_admin(admin: AdminUser = Depends(get_current_admin_user)) -> AdminUser:
    """
    Requer que usuário seja admin
    """
    return admin

def require_role(role: str):
    """
    Requer role específico
    """
    def dependency(admin: AdminUser = Depends(get_current_admin_user)) -> AdminUser:
        if admin.role != role and admin.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requer role: {role}"
            )
        return admin
    return dependency

def require_permission(permission: str):
    """
    Verifica se admin tem permissão específica
    """
    def dependency(admin: AdminUser = Depends(get_current_admin_user)) -> AdminUser:
        user_permissions = PERMISSIONS.get(admin.role, [])

        # Super admin tem tudo
        if "*" in user_permissions:
            return admin

        # Verificar permissão exata ou wildcard
        resource, action = permission.split(":")
        has_permission = any([
            perm == permission,
            perm == f"{resource}:*",
            perm == "*"
        ] for perm in user_permissions)

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada: {permission}"
            )

        return admin
    return dependency
```

---

**Última atualização:** 2026-03-10
**Versão:** 1.0
