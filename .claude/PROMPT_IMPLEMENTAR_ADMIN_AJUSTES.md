# 🎯 PROMPT: Implementar Ajustes do Sistema Admin SaaS

## 📋 Contexto

Você está trabalhando no AgroSaaS, uma aplicação FastAPI + SQLAlchemy (async) + PostgreSQL que já possui uma base sólida de sistema administrativo. Este prompt orienta a implementação dos ajustes e complementos necessários para completar o sistema admin, aproveitando ao máximo o código existente.

**IMPORTANTE:** Leia primeiro o documento [ADMIN_SAAS_ADERENCIA.md](../docs/ADMIN_SAAS_ADERENCIA.md) para entender o que já existe.

---

## 🎯 OBJETIVO

Completar o sistema de administração do SaaS implementando:
1. ✅ Ajustes em modelos existentes (adicionar campos)
2. ✅ Expansão do router backoffice existente
3. ✅ Novos modelos (Cupons, EmailTemplate, etc)
4. ✅ Novos routers e services

---

## 📁 ESTRUTURA ATUAL DA APLICAÇÃO

```
services/api/
├── core/
│   ├── models/
│   │   ├── tenant.py          ✅ Existe - Precisa ajustes
│   │   ├── auth.py            ✅ Existe
│   │   ├── billing.py         ✅ Existe - PlanoAssinatura, AssinaturaTenant, Fatura
│   │   ├── support.py         ✅ Existe - ChamadoSuporte, MensagemChamado
│   │   ├── configuration.py   ✅ Existe
│   │   └── fazenda.py         ✅ Existe
│   │
│   ├── routers/
│   │   ├── backoffice.py      ✅ Existe - 500+ linhas - EXPANDIR ESTE
│   │   ├── billing.py         ✅ Existe
│   │   ├── support.py         ✅ Existe
│   │   ├── auth.py            ✅ Existe
│   │   └── configuration.py   ✅ Existe
│   │
│   ├── services/
│   │   ├── email_service.py   ✅ Existe - Expandir
│   │   └── auth_service.py    ✅ Existe
│   │
│   ├── dependencies.py        ✅ Existe - get_current_admin JÁ IMPLEMENTADO
│   ├── database.py            ✅ Existe
│   └── constants.py           ✅ Existe - Módulos definidos
│
└── main.py                     ✅ Existe - Router principal
```

---

## 🚀 FASE 1: AJUSTAR MODELOS EXISTENTES

### 1.1. Ajustar `core/models/tenant.py`

**Ação:** Adicionar campos de controle de storage e último acesso

```python
# ADICIONAR estes campos no modelo Tenant existente:

from sqlalchemy import Integer

# Storage
storage_usado_mb: Mapped[int] = mapped_column(Integer, default=0)
storage_limite_mb: Mapped[int] = mapped_column(Integer, default=10240)  # 10GB padrão

# Último acesso
data_ultimo_acesso: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

# Contato (se não existir)
email_responsavel: Mapped[str | None] = mapped_column(String(255), nullable=True)
telefone_responsavel: Mapped[str | None] = mapped_column(String(20), nullable=True)
```

**IMPORTANTE:**
- ✅ NÃO remover campos existentes
- ✅ Manter a estrutura atual do modelo
- ✅ Adicionar apenas os campos listados acima

---

### 1.2. Ajustar `core/models/support.py`

**Ação:** Adicionar campos de SLA, atendente e avaliação no modelo `ChamadoSuporte`

```python
# ADICIONAR estes campos no modelo ChamadoSuporte existente:

from sqlalchemy import ForeignKey, Text

# Atendimento
atendente_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("usuarios.id"),
    nullable=True
)
data_primeira_resposta: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True
)
data_resolucao: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True
)
sla_vencimento: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True
)

# Avaliação
avaliacao_nota: Mapped[int | None] = mapped_column(nullable=True)  # 1-5
avaliacao_comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
avaliacao_data: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True
)

# Relationship (adicionar se não existir)
# atendente = relationship("Usuario", foreign_keys=[atendente_id])
```

**IMPORTANTE:**
- ✅ Manter todos os campos existentes
- ✅ Adicionar apenas os novos campos
- ✅ SLA pode ser None inicialmente (será calculado por trigger ou service)

---

### 1.3. Ajustar `core/models/billing.py`

**Ação:** Adicionar campos de trial em `PlanoAssinatura` (se não existirem)

```python
# VERIFICAR se estes campos existem, se não, ADICIONAR:

# Trial
tem_trial: Mapped[bool] = mapped_column(Boolean, default=True)
dias_trial: Mapped[int] = mapped_column(default=15)
is_free: Mapped[bool] = mapped_column(Boolean, default=False)

# Melhorar descrição
descricao_marketing: Mapped[str | None] = mapped_column(Text, nullable=True)

# Destacar plano
destaque: Mapped[bool] = mapped_column(Boolean, default=False)
ordem: Mapped[int] = mapped_column(default=0)
```

---

## 🆕 FASE 2: CRIAR NOVOS MODELOS

### 2.1. Criar `core/models/admin_user.py`

**Ação:** Criar novo modelo para usuários administrativos (separado dos usuários dos tenants)

```python
# core/models/admin_user.py - CRIAR ARQUIVO NOVO

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class AdminUser(Base):
    """Usuários administrativos do SaaS (separado dos usuários dos tenants)."""
    __tablename__ = "admin_users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Perfil: super_admin, admin, suporte, financeiro, comercial
    role: Mapped[str] = mapped_column(String(20), nullable=False, default='admin')
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_acesso: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Preferências
    timezone: Mapped[str] = mapped_column(String(50), default='America/Sao_Paulo')
    locale: Mapped[str] = mapped_column(String(10), default='pt-BR')

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def tem_permissao(self, permissao: str) -> bool:
        """Verifica se admin tem permissão."""
        from core.dependencies import ADMIN_PERMISSIONS
        user_perms = ADMIN_PERMISSIONS.get(self.role, [])

        if "*" in user_perms:
            return True

        resource, action = permissao.split(":")
        return any([
            perm == permissao,
            perm == f"{resource}:*",
        ] for perm in user_perms)
```

---

### 2.2. Criar `core/models/cupom.py`

**Ação:** Criar modelo para cupons de desconto

```python
# core/models/cupom.py - CRIAR ARQUIVO NOVO

import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, Boolean, DateTime, Numeric, Integer, Date, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from core.database import Base

class Cupom(Base):
    """Cupons de desconto para assinaturas."""
    __tablename__ = "cupons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # Tipo de Desconto
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # percentual, valor_fixo
    valor: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Aplicação
    aplicavel_em: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default='primeira_mensalidade'
    )  # primeira_mensalidade, todos_meses, plano_anual
    duracao_meses: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Restrições (Array de UUIDs de planos - vazio = todos)
    # Se seu PostgreSQL não suporta ARRAY, use JSON
    # planos_validos: Mapped[dict] = mapped_column(JSON, default=list)

    # Limites de uso
    uso_maximo: Mapped[int] = mapped_column(Integer, default=1)
    uso_atual: Mapped[int] = mapped_column(Integer, default=0)
    uso_por_cliente: Mapped[int] = mapped_column(Integer, default=1)

    # Validade
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date] = mapped_column(Date, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Auditoria
    criado_por_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def pode_ser_usado(self) -> bool:
        """Verifica se cupom ainda pode ser usado."""
        hoje = date.today()
        return (
            self.ativo and
            self.data_inicio <= hoje <= self.data_fim and
            self.uso_atual < self.uso_maximo
        )
```

---

### 2.3. Criar `core/models/email_template.py`

**Ação:** Criar modelos para templates de email e log de envios

```python
# core/models/email_template.py - CRIAR ARQUIVO NOVO

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class EmailTemplate(Base):
    """Templates de e-mail reutilizáveis."""
    __tablename__ = "email_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Conteúdo
    assunto: Mapped[str] = mapped_column(String(255), nullable=False)
    corpo_html: Mapped[str] = mapped_column(Text, nullable=False)
    corpo_texto: Mapped[str] = mapped_column(Text, nullable=False)

    # Variáveis disponíveis (array ou JSON)
    variaveis: Mapped[dict] = mapped_column(JSON, default=list)
    # Ex: ["nome_usuario", "tenant_nome", "data_vencimento"]

    # Configuração
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    # transacional, marketing, sistema
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Auditoria
    editado_por_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


class EmailLog(Base):
    """Log de e-mails enviados."""
    __tablename__ = "email_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Template (pode ser None se enviado manualmente)
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("email_templates.id"),
        nullable=True
    )
    template_codigo: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Destinatário
    destinatario_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    destinatario_nome: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=True
    )

    # Conteúdo enviado
    assunto: Mapped[str] = mapped_column(String(255), nullable=False)
    corpo_html: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    # enviado, falha, pendente
    erro_mensagem: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Provider
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Tracking
    aberto: Mapped[bool] = mapped_column(Boolean, default=False)
    data_abertura: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    clicado: Mapped[bool] = mapped_column(Boolean, default=False)
    data_clique: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Auditoria
    enviado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
```

---

### 2.4. Criar `core/models/admin_audit_log.py`

**Ação:** Criar modelo para log de auditoria de ações administrativas

```python
# core/models/admin_audit_log.py - CRIAR ARQUIVO NOVO

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class AdminAuditLog(Base):
    """Log de auditoria de ações administrativas."""
    __tablename__ = "admin_audit_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Quem fez a ação
    admin_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admin_users.id"),
        nullable=False,
        index=True
    )
    admin_email: Mapped[str] = mapped_column(String(255), nullable=False)

    # O que foi feito
    acao: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Ex: tenant.impersonate, subscription.suspend, ticket.assign

    entidade: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # tenant, subscription, ticket, etc

    entidade_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Detalhes
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_anteriores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    dados_novos: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Contexto
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
```

---

## 🔄 FASE 3: ATUALIZAR `core/models/__init__.py`

**Ação:** Adicionar os novos modelos no `__init__.py`

```python
# core/models/__init__.py - ADICIONAR as importações

from core.models.admin_user import AdminUser
from core.models.cupom import Cupom
from core.models.email_template import EmailTemplate, EmailLog
from core.models.admin_audit_log import AdminAuditLog

# Adicionar no __all__ se existir
__all__ = [
    # ... modelos existentes ...
    "AdminUser",
    "Cupom",
    "EmailTemplate",
    "EmailLog",
    "AdminAuditLog",
]
```

---

## 🗄️ FASE 4: CRIAR MIGRATION

**Ação:** Criar migration do Alembic para aplicar as mudanças

```bash
# No terminal, dentro de services/api/

# Criar migration automática
alembic revision --autogenerate -m "add_admin_models_and_fields"

# Revisar o arquivo gerado em migrations/versions/

# Aplicar migration
alembic upgrade head
```

**IMPORTANTE:**
- ✅ Revisar o arquivo de migration gerado
- ✅ Verificar se todos os campos foram detectados
- ✅ Testar em banco de desenvolvimento antes de produção

---

## 🚀 FASE 5: EXPANDIR `core/routers/backoffice.py`

**Ação:** Adicionar novos endpoints no router existente

### 5.1. Adicionar Reset de Senha

```python
# Adicionar no arquivo core/routers/backoffice.py

@router.post("/tenants/{tenant_id}/reset-password", dependencies=[Depends(get_current_admin)])
async def reset_tenant_password(
    tenant_id: uuid.UUID,
    enviar_email: bool = True,
    session: AsyncSession = Depends(get_session)
):
    """
    Reseta a senha do responsável pelo tenant e opcionalmente envia email.
    """
    import secrets
    import string
    from core.services.auth_service import hash_password

    # Buscar tenant
    tenant = await session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    # Gerar senha aleatória
    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    senha_temporaria = ''.join(secrets.choice(caracteres) for _ in range(12))

    # Buscar usuário principal do tenant (admin/owner)
    from core.models.auth import Usuario, TenantUsuario
    stmt = (
        select(Usuario)
        .join(TenantUsuario)
        .where(
            TenantUsuario.tenant_id == tenant_id,
            Usuario.is_owner == True  # Assumindo que existe esse campo
        )
    )
    result = await session.execute(stmt)
    usuario = result.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário responsável não encontrado")

    # Atualizar senha
    usuario.senha_hash = hash_password(senha_temporaria)
    usuario.force_password_change = True  # Obriga troca no próximo login

    await session.commit()

    # Enviar email se solicitado
    if enviar_email:
        from core.services.email_service import email_service
        await email_service.send_email(
            to=usuario.email,
            subject="Redefinição de Senha - AgroSaaS",
            html_content=f"""
            <h2>Olá {tenant.nome},</h2>
            <p>Sua senha foi redefinida pelo administrador do sistema.</p>
            <p><strong>Senha temporária:</strong> {senha_temporaria}</p>
            <p>Por segurança, você será obrigado a criar uma nova senha no próximo acesso.</p>
            <p><a href="https://app.agrosass.com">Acessar sistema</a></p>
            """
        )

    return {
        "success": True,
        "senha_temporaria": senha_temporaria if not enviar_email else None,
        "email_enviado": enviar_email,
        "usuario_email": usuario.email
    }
```

---

### 5.2. Adicionar Alterar Plano

```python
# Adicionar no arquivo core/routers/backoffice.py

@router.patch("/tenants/{tenant_id}/change-plan", dependencies=[Depends(get_current_admin)])
async def change_tenant_plan(
    tenant_id: uuid.UUID,
    novo_plano_id: uuid.UUID,
    admin_user: dict = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    """
    Altera o plano de assinatura de um tenant.
    """
    # Buscar tenant
    tenant = await session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    # Buscar novo plano
    novo_plano = await session.get(PlanoAssinatura, novo_plano_id)
    if not novo_plano or not novo_plano.ativo:
        raise HTTPException(status_code=404, detail="Plano não encontrado ou inativo")

    # Buscar assinatura atual
    stmt = select(AssinaturaTenant).where(AssinaturaTenant.tenant_id == tenant_id)
    result = await session.execute(stmt)
    assinatura = result.scalar_one_or_none()

    if not assinatura:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")

    # Guardar dados antigos para audit log
    plano_anterior_id = assinatura.plano_id

    # Atualizar assinatura
    assinatura.plano_id = novo_plano_id

    # Atualizar módulos do tenant
    tenant.modulos_ativos = novo_plano.modulos_inclusos
    tenant.max_usuarios_simultaneos = novo_plano.limite_usuarios

    # Registrar no audit log (se implementado)
    # audit = AdminAuditLog(...)

    await session.commit()

    return {
        "success": True,
        "tenant_id": tenant_id,
        "plano_anterior_id": plano_anterior_id,
        "plano_novo_id": novo_plano_id,
        "plano_novo_nome": novo_plano.nome,
        "novos_modulos": tenant.modulos_ativos
    }
```

---

### 5.3. Adicionar Métricas de Storage

```python
# Adicionar no arquivo core/routers/backoffice.py

@router.get("/tenants/storage/alertas", dependencies=[Depends(get_current_admin)])
async def get_storage_alerts(
    limite_percentual: float = 80.0,
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna tenants com storage próximo ao limite.
    """
    stmt = (
        select(Tenant)
        .where(
            Tenant.ativo == True,
            Tenant.storage_usado_mb > (Tenant.storage_limite_mb * (limite_percentual / 100))
        )
        .order_by((Tenant.storage_usado_mb / Tenant.storage_limite_mb).desc())
    )
    result = await session.execute(stmt)
    tenants = result.scalars().all()

    alertas = []
    for tenant in tenants:
        percentual = (tenant.storage_usado_mb / tenant.storage_limite_mb) * 100
        alertas.append({
            "tenant_id": tenant.id,
            "tenant_nome": tenant.nome,
            "storage_usado_mb": tenant.storage_usado_mb,
            "storage_limite_mb": tenant.storage_limite_mb,
            "percentual_uso": round(percentual, 2),
            "alerta": "critico" if percentual >= 95 else "alto" if percentual >= 90 else "medio"
        })

    return {
        "total_alertas": len(alertas),
        "tenants": alertas
    }
```

---

## 🆕 FASE 6: CRIAR ROUTER DE CUPONS

**Ação:** Criar novo arquivo `core/routers/cupons.py`

```python
# core/routers/cupons.py - CRIAR ARQUIVO NOVO

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from datetime import date

from core.dependencies import get_session, get_current_admin
from core.models.cupom import Cupom
from pydantic import BaseModel

router = APIRouter(prefix="/backoffice/cupons", tags=["Backoffice - Cupons"])


# Schemas
class CupomCreate(BaseModel):
    codigo: str
    tipo: str  # percentual, valor_fixo
    valor: float
    aplicavel_em: str
    duracao_meses: int | None = None
    uso_maximo: int = 1
    uso_por_cliente: int = 1
    data_inicio: date
    data_fim: date
    ativo: bool = True


class CupomResponse(BaseModel):
    id: uuid.UUID
    codigo: str
    tipo: str
    valor: float
    aplicavel_em: str
    uso_maximo: int
    uso_atual: int
    uso_por_cliente: int
    data_inicio: date
    data_fim: date
    ativo: bool
    pode_ser_usado: bool

    class Config:
        from_attributes = True


# Endpoints
@router.post("", response_model=CupomResponse, dependencies=[Depends(get_current_admin)])
async def criar_cupom(
    data: CupomCreate,
    session: AsyncSession = Depends(get_session)
):
    """Cria um novo cupom de desconto."""
    # Verificar se código já existe
    stmt = select(Cupom).where(Cupom.codigo == data.codigo.upper())
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de cupom já existe"
        )

    cupom = Cupom(
        codigo=data.codigo.upper(),
        tipo=data.tipo,
        valor=data.valor,
        aplicavel_em=data.aplicavel_em,
        duracao_meses=data.duracao_meses,
        uso_maximo=data.uso_maximo,
        uso_por_cliente=data.uso_por_cliente,
        data_inicio=data.data_inicio,
        data_fim=data.data_fim,
        ativo=data.ativo
    )

    session.add(cupom)
    await session.commit()
    await session.refresh(cupom)

    return CupomResponse(
        **cupom.__dict__,
        pode_ser_usado=cupom.pode_ser_usado()
    )


@router.get("", response_model=List[CupomResponse], dependencies=[Depends(get_current_admin)])
async def listar_cupons(
    apenas_ativos: bool = False,
    session: AsyncSession = Depends(get_session)
):
    """Lista todos os cupons."""
    stmt = select(Cupom)

    if apenas_ativos:
        stmt = stmt.where(Cupom.ativo == True)

    stmt = stmt.order_by(Cupom.created_at.desc())
    result = await session.execute(stmt)
    cupons = result.scalars().all()

    return [
        CupomResponse(
            **cupom.__dict__,
            pode_ser_usado=cupom.pode_ser_usado()
        )
        for cupom in cupons
    ]


@router.get("/{cupom_id}", response_model=CupomResponse, dependencies=[Depends(get_current_admin)])
async def obter_cupom(
    cupom_id: uuid.UUID,
    session: AsyncSession = Depends(get_session)
):
    """Retorna detalhes de um cupom."""
    cupom = await session.get(Cupom, cupom_id)
    if not cupom:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")

    return CupomResponse(
        **cupom.__dict__,
        pode_ser_usado=cupom.pode_ser_usado()
    )


@router.get("/validar/{codigo}", dependencies=[Depends(get_current_admin)])
async def validar_cupom(
    codigo: str,
    session: AsyncSession = Depends(get_session)
):
    """Valida se um cupom pode ser usado."""
    stmt = select(Cupom).where(Cupom.codigo == codigo.upper())
    result = await session.execute(stmt)
    cupom = result.scalar_one_or_none()

    if not cupom:
        return {"valido": False, "motivo": "Cupom não encontrado"}

    if not cupom.pode_ser_usado():
        motivos = []
        if not cupom.ativo:
            motivos.append("Cupom inativo")
        if cupom.uso_atual >= cupom.uso_maximo:
            motivos.append("Limite de uso atingido")
        hoje = date.today()
        if not (cupom.data_inicio <= hoje <= cupom.data_fim):
            motivos.append("Cupom fora do período de validade")

        return {"valido": False, "motivo": ", ".join(motivos)}

    return {
        "valido": True,
        "cupom": CupomResponse(
            **cupom.__dict__,
            pode_ser_usado=True
        )
    }


@router.delete("/{cupom_id}", dependencies=[Depends(get_current_admin)])
async def desativar_cupom(
    cupom_id: uuid.UUID,
    session: AsyncSession = Depends(get_session)
):
    """Desativa um cupom."""
    cupom = await session.get(Cupom, cupom_id)
    if not cupom:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")

    cupom.ativo = False
    await session.commit()

    return {"success": True, "message": "Cupom desativado"}
```

---

## 📝 FASE 7: ATUALIZAR `core/dependencies.py`

**Ação:** Adicionar permissões de admin se não existirem

```python
# Adicionar no arquivo core/dependencies.py (se não existir)

# Mapa de permissões por role
ADMIN_PERMISSIONS = {
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


def require_permission(permissao: str):
    """
    Dependency para verificar permissão específica do admin.

    Uso:
    @router.get("/rota", dependencies=[Depends(require_permission("pacotes:create"))])
    """
    async def dependency(admin = Depends(get_current_admin)):
        if not admin.tem_permissao(permissao):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada: {permissao}"
            )
        return admin
    return dependency
```

---

## 🔗 FASE 8: REGISTRAR NOVOS ROUTERS NO `main.py`

**Ação:** Adicionar import e registro do router de cupons

```python
# No arquivo main.py, ADICIONAR:

from core.routers import cupons

# Na seção de routers, ADICIONAR:
app.include_router(cupons.router, prefix="/api/v1")
```

---

## 🎯 FASE 9: CRIAR SCRIPT DE SEED PARA ADMIN

**Ação:** Criar script para popular dados iniciais

```python
# scripts/seed_admin.py - CRIAR ARQUIVO NOVO

import asyncio
import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import async_session_maker
from core.models.admin_user import AdminUser
from core.models.email_template import EmailTemplate
from core.services.auth_service import hash_password
import uuid


async def seed_admin_user():
    """Cria usuário admin padrão."""
    async with async_session_maker() as session:
        # Verificar se já existe
        from sqlalchemy import select
        stmt = select(AdminUser).where(AdminUser.email == "admin@agrosass.com")
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            print("✅ Admin user já existe")
            return

        admin = AdminUser(
            email="admin@agrosass.com",
            senha_hash=hash_password("admin123"),
            nome="Administrador",
            role="super_admin",
            ativo=True
        )

        session.add(admin)
        await session.commit()
        print("✅ Admin user criado: admin@agrosass.com / admin123")


async def seed_email_templates():
    """Cria templates de email padrão."""
    async with async_session_maker() as session:
        templates = [
            {
                "codigo": "WELCOME",
                "nome": "Boas-vindas",
                "assunto": "Bem-vindo ao AgroSaaS!",
                "corpo_html": """
                    <h2>Olá {{nome_responsavel}},</h2>
                    <p>Bem-vindo ao AgroSaaS!</p>
                    <p>Sua conta foi criada com sucesso.</p>
                    <p><strong>Dados de acesso:</strong></p>
                    <ul>
                        <li>URL: {{tenant_url}}</li>
                        <li>Email: {{email}}</li>
                    </ul>
                    <p><a href="{{tenant_url}}">Acessar sistema</a></p>
                """,
                "corpo_texto": "Bem-vindo ao AgroSaaS! Acesse: {{tenant_url}}",
                "variaveis": ["nome_responsavel", "tenant_url", "email"],
                "tipo": "transacional"
            },
            {
                "codigo": "PASSWORD_RESET",
                "nome": "Reset de Senha",
                "assunto": "Redefinição de Senha - AgroSaaS",
                "corpo_html": """
                    <h2>Olá {{nome_responsavel}},</h2>
                    <p>Sua senha foi redefinida.</p>
                    <p><strong>Senha temporária:</strong> {{senha_temporaria}}</p>
                    <p>Você será obrigado a alterar no próximo login.</p>
                    <p><a href="{{tenant_url}}">Acessar sistema</a></p>
                """,
                "corpo_texto": "Senha resetada: {{senha_temporaria}}",
                "variaveis": ["nome_responsavel", "senha_temporaria", "tenant_url"],
                "tipo": "transacional"
            }
        ]

        for tpl_data in templates:
            # Verificar se já existe
            from sqlalchemy import select
            stmt = select(EmailTemplate).where(EmailTemplate.codigo == tpl_data["codigo"])
            result = await session.execute(stmt)
            if result.scalar_one_or_none():
                print(f"✅ Template {tpl_data['codigo']} já existe")
                continue

            template = EmailTemplate(**tpl_data)
            session.add(template)

        await session.commit()
        print(f"✅ {len(templates)} templates criados")


async def main():
    print("🚀 Iniciando seed de dados admin...")
    await seed_admin_user()
    await seed_email_templates()
    print("✅ Seed concluído!")


if __name__ == "__main__":
    asyncio.run(main())
```

**Executar:**
```bash
cd services/api
python scripts/seed_admin.py
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

Marque conforme for implementando:

### Modelos
- [ ] Ajustar `core/models/tenant.py` (storage, último acesso)
- [ ] Ajustar `core/models/support.py` (SLA, avaliação)
- [ ] Ajustar `core/models/billing.py` (trial, destaque)
- [ ] Criar `core/models/admin_user.py`
- [ ] Criar `core/models/cupom.py`
- [ ] Criar `core/models/email_template.py`
- [ ] Criar `core/models/admin_audit_log.py`
- [ ] Atualizar `core/models/__init__.py`

### Migration
- [ ] Criar migration com `alembic revision --autogenerate`
- [ ] Revisar arquivo de migration
- [ ] Executar `alembic upgrade head`

### Routers
- [ ] Expandir `core/routers/backoffice.py` (reset senha, alterar plano, storage)
- [ ] Criar `core/routers/cupons.py`
- [ ] Registrar router de cupons no `main.py`

### Dependencies
- [ ] Adicionar `ADMIN_PERMISSIONS` em `core/dependencies.py`
- [ ] Adicionar `require_permission` em `core/dependencies.py`

### Seeds
- [ ] Criar `scripts/seed_admin.py`
- [ ] Executar seed de admin user
- [ ] Executar seed de templates

### Testes
- [ ] Testar endpoints de reset de senha
- [ ] Testar endpoints de alterar plano
- [ ] Testar CRUD de cupons
- [ ] Testar validação de cupons
- [ ] Verificar audit logs

---

## 🧪 TESTES MANUAIS

Após implementar, testar com curl ou Postman:

```bash
# 1. Login como admin (usar endpoint existente)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@agrosass.com", "password": "admin123"}'

# 2. Testar reset de senha
curl -X POST http://localhost:8000/api/v1/backoffice/tenants/{TENANT_ID}/reset-password \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"enviar_email": false}'

# 3. Testar criar cupom
curl -X POST http://localhost:8000/api/v1/backoffice/cupons \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "PROMO2024",
    "tipo": "percentual",
    "valor": 20,
    "aplicavel_em": "primeira_mensalidade",
    "uso_maximo": 100,
    "data_inicio": "2024-01-01",
    "data_fim": "2024-12-31"
  }'

# 4. Testar validar cupom
curl -X GET http://localhost:8000/api/v1/backoffice/cupons/validar/PROMO2024 \
  -H "Authorization: Bearer {TOKEN}"
```

---

## 📚 REFERÊNCIAS

- [ADMIN_SAAS_ADERENCIA.md](../docs/ADMIN_SAAS_ADERENCIA.md) - Análise completa
- [ADMIN_SAAS_ESTRUTURA.md](../docs/ADMIN_SAAS_ESTRUTURA.md) - Especificação funcional
- [ADMIN_SAAS_DATABASE.md](../docs/ADMIN_SAAS_DATABASE.md) - Esquema de banco
- [ADMIN_SAAS_API_EXAMPLES.md](../docs/ADMIN_SAAS_API_EXAMPLES.md) - Exemplos de código

---

## 💡 DICAS IMPORTANTES

1. **Manter compatibilidade:** Não altere nomes de campos/tabelas existentes
2. **Usar nomenclatura atual:** Manter português (PlanoAssinatura, ChamadoSuporte)
3. **Aproveitar código existente:** O `backoffice.py` já tem muita coisa boa
4. **Testar incrementalmente:** Implemente fase por fase e teste
5. **Documentar:** Adicione docstrings nos novos endpoints

---

**Criado em:** 2026-03-10
**Versão:** 1.0
**Status:** Pronto para implementação
