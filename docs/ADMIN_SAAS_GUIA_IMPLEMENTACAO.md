# 🚀 Guia de Implementação - Admin SaaS

## 📋 Visão Geral

Este documento fornece um guia passo a passo para implementar o sistema de administração do SaaS.

---

## 📅 Cronograma Sugerido

### **Semana 1-2: Backend Foundation**
- Estrutura de banco de dados
- Modelos SQLAlchemy
- Sistema de autenticação admin
- Dashboard básico

### **Semana 3-4: Backend Features**
- CRUD de Assinantes
- Sistema de Tickets
- Gestão de Pacotes
- Integração Stripe

### **Semana 5-6: Frontend**
- Layout admin
- Dashboard
- Páginas de gestão
- Componentes reutilizáveis

### **Semana 7: Integração e Testes**
- Testes end-to-end
- Ajustes de UX
- Documentação

### **Semana 8: Deploy e Monitoramento**
- Deploy em produção
- Configuração de monitoramento
- Treinamento da equipe

---

## 🔧 Fase 1: Setup Inicial (Dia 1-2)

### 1.1. Criar estrutura de diretórios

```bash
# Backend
mkdir -p services/api/app/admin/{dashboard,assinantes,assinaturas,suporte,pacotes,cupons,financeiro,emails,modulos,config}
mkdir -p services/api/app/admin/assinantes/actions

# Frontend
mkdir -p apps/web/src/app/\(admin\)/admin/{dashboard,assinantes,assinaturas,suporte,pacotes,cupons,financeiro,emails,modulos,config}
```

### 1.2. Configurar banco de dados

```python
# services/api/alembic/versions/XXX_create_admin_tables.py

"""Create admin tables

Revision ID: XXX
Revises: YYY
Create Date: 2026-03-10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'XXX'
down_revision = 'YYY'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Criar tabelas conforme ADMIN_SAAS_DATABASE.md
    op.create_table(
        'admin_users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('senha_hash', sa.String(255), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('role', sa.String(20), nullable=False, server_default='admin'),
        sa.Column('ativo', sa.Boolean, default=True),
        sa.Column('ultimo_acesso', sa.DateTime),
        sa.Column('criado_em', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('atualizado_em', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
    )

    # Repetir para outras tabelas...

def downgrade() -> None:
    op.drop_table('admin_users')
    # Repetir para outras tabelas...
```

```bash
# Executar migração
cd services/api
alembic upgrade head
```

### 1.3. Criar primeiro usuário admin

```python
# services/api/scripts/create_admin.py

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session
from app.models import AdminUser
from app.core.security import hash_password

async def criar_admin():
    async with async_session() as db:
        admin = AdminUser(
            email="admin@agrosass.com",
            senha_hash=hash_password("admin123"),
            nome="Administrador",
            role="super_admin",
            ativo=True
        )
        db.add(admin)
        await db.commit()
        print(f"Admin criado: {admin.email}")

if __name__ == "__main__":
    asyncio.run(criar_admin())
```

```bash
# Executar script
python scripts/create_admin.py
```

---

## 🏗️ Fase 2: Backend - Dashboard (Dia 3-4)

### 2.1. Criar modelo AdminUser

```python
# services/api/app/models/admin_user.py

from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.core.database import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    nome = Column(String(255), nullable=False)
    avatar_url = Column(String(500))
    role = Column(String(20), nullable=False, default='admin')
    ativo = Column(Boolean, default=True)
    ultimo_acesso = Column(DateTime)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def tem_permissao(self, permissao: str) -> bool:
        """Verifica se admin tem permissão"""
        from app.core.security import PERMISSIONS
        user_perms = PERMISSIONS.get(self.role, [])
        return "*" in user_perms or permissao in user_perms
```

### 2.2. Implementar autenticação

```python
# services/api/app/api/admin/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models import AdminUser
from app.core.security import verify_password, create_access_token
from pydantic import BaseModel

router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

@router.post("/login", response_model=TokenResponse)
async def login_admin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login de administrador
    """
    # Buscar admin por email
    result = await db.execute(
        select(AdminUser).where(AdminUser.email == form_data.username)
    )
    admin = result.scalar_one_or_none()

    # Verificar credenciais
    if not admin or not verify_password(form_data.password, admin.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )

    if not admin.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário desativado"
        )

    # Atualizar último acesso
    admin.ultimo_acesso = datetime.utcnow()
    await db.commit()

    # Gerar token
    token_data = {
        "sub": str(admin.id),
        "email": admin.email,
        "role": admin.role,
        "type": "admin"
    }
    access_token = create_access_token(token_data, expires_delta=timedelta(hours=8))

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=28800  # 8 horas
    )
```

### 2.3. Implementar Dashboard

Seguir os exemplos em [ADMIN_SAAS_API_EXAMPLES.md](./ADMIN_SAAS_API_EXAMPLES.md#-dashboard---métricas)

---

## 👥 Fase 3: Backend - Assinantes (Dia 5-7)

### 3.1. Criar modelos relacionados

```python
# services/api/app/models/__init__.py

from app.models.admin_user import AdminUser
from app.models.tenant import Tenant
from app.models.subscription import Subscription, SubscriptionModule
from app.models.pacote import Pacote, PacoteModulo
from app.models.modulo_sistema import ModuloSistema

__all__ = [
    "AdminUser",
    "Tenant",
    "Subscription",
    "SubscriptionModule",
    "Pacote",
    "PacoteModulo",
    "ModuloSistema"
]
```

### 3.2. Implementar CRUD de Assinantes

Seguir exemplos em [ADMIN_SAAS_API_EXAMPLES.md](./ADMIN_SAAS_API_EXAMPLES.md#-assinantes---crud-e-ações)

### 3.3. Implementar Impersonate

```python
# services/api/app/admin/assinantes/actions/impersonate.py

# Ver implementação completa em ADMIN_SAAS_API_EXAMPLES.md
```

### 3.4. Testar endpoints

```bash
# Criar arquivo de testes
# services/api/tests/admin/test_assinantes.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_listar_assinantes(admin_client: AsyncClient):
    response = await admin_client.get("/admin/assinantes")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

@pytest.mark.asyncio
async def test_impersonate_assinante(admin_client: AsyncClient, tenant_id: str):
    response = await admin_client.post(f"/admin/assinantes/{tenant_id}/impersonate")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "tenant_url" in data
```

---

## 🎫 Fase 4: Backend - Suporte (Dia 8-10)

### 4.1. Criar modelos de Ticket

```python
# services/api/app/models/ticket.py

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=False)
    usuario_id = Column(UUID(as_uuid=True))
    usuario_nome = Column(String(255), nullable=False)
    usuario_email = Column(String(255), nullable=False)

    categoria = Column(String(20), nullable=False)
    prioridade = Column(String(20), nullable=False, default='normal')
    status = Column(String(30), nullable=False, default='aberto')

    assunto = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=False)

    atendente_id = Column(UUID(as_uuid=True), ForeignKey('admin_users.id'))
    data_abertura = Column(DateTime, nullable=False, default=datetime.utcnow)
    data_primeira_resposta = Column(DateTime)
    data_resolucao = Column(DateTime)
    sla_vencimento = Column(DateTime, nullable=False)

    avaliacao_nota = Column(Integer)
    avaliacao_comentario = Column(Text)
    avaliacao_data = Column(DateTime)

    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="tickets")
    atendente = relationship("AdminUser")
    mensagens = relationship("TicketMensagem", back_populates="ticket", cascade="all, delete-orphan")
    anexos = relationship("TicketAnexo", back_populates="ticket", cascade="all, delete-orphan")

class TicketMensagem(Base):
    __tablename__ = "ticket_mensagens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey('tickets.id'), nullable=False)
    autor_tipo = Column(String(20), nullable=False)
    autor_id = Column(UUID(as_uuid=True))
    autor_nome = Column(String(255), nullable=False)
    mensagem = Column(Text, nullable=False)
    mensagem_html = Column(Text)
    visualizado = Column(Boolean, default=False)
    data_visualizacao = Column(DateTime)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    ticket = relationship("Ticket", back_populates="mensagens")
    anexos = relationship("TicketAnexo", back_populates="mensagem")
```

### 4.2. Implementar sistema de SLA

```python
# services/api/app/admin/suporte/sla.py

from datetime import datetime, timedelta

SLA_CONFIG = {
    'critica': {'primeira_resposta': 1, 'resolucao': 4},  # horas
    'alta': {'primeira_resposta': 2, 'resolucao': 8},
    'normal': {'primeira_resposta': 4, 'resolucao': 24},
    'baixa': {'primeira_resposta': 8, 'resolucao': 48}
}

def calcular_sla_vencimento(
    prioridade: str,
    data_abertura: datetime,
    tipo: str = 'primeira_resposta'
) -> datetime:
    """
    Calcula data de vencimento do SLA
    """
    horas = SLA_CONFIG.get(prioridade, SLA_CONFIG['normal'])[tipo]
    return data_abertura + timedelta(hours=horas)

def verificar_sla_vencido(ticket) -> bool:
    """
    Verifica se SLA foi violado
    """
    agora = datetime.utcnow()

    # SLA de primeira resposta
    if not ticket.data_primeira_resposta:
        return agora > ticket.sla_vencimento

    # SLA de resolução
    if ticket.status not in ['resolvido', 'fechado']:
        sla_resolucao = calcular_sla_vencimento(
            ticket.prioridade,
            ticket.data_abertura,
            'resolucao'
        )
        return agora > sla_resolucao

    return False
```

### 4.3. Implementar rotas de Suporte

Seguir exemplos em [ADMIN_SAAS_API_EXAMPLES.md](./ADMIN_SAAS_API_EXAMPLES.md#-suporte---sistema-de-tickets)

---

## 💼 Fase 5: Backend - Pacotes e Módulos (Dia 11-13)

### 5.1. Criar modelos

```python
# services/api/app/models/pacote.py

from sqlalchemy import Column, String, Text, Numeric, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

class Pacote(Base):
    __tablename__ = "pacotes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(50), unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    descricao_marketing = Column(Text)

    preco_mensal = Column(Numeric(10, 2), nullable=False)
    preco_anual = Column(Numeric(10, 2), nullable=False)
    desconto_anual = Column(Integer, default=0)

    max_usuarios_simultaneos = Column(Integer, default=5)
    storage_gb = Column(Integer, default=10)

    tem_trial = Column(Boolean, default=True)
    dias_trial = Column(Integer, default=15)
    is_free = Column(Boolean, default=False)

    limites_customizados = Column(JSONB, default={})

    ativo = Column(Boolean, default=True)
    destaque = Column(Boolean, default=False)
    ordem = Column(Integer, default=0)

    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    modulos = relationship("PacoteModulo", back_populates="pacote", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="pacote")

class PacoteModulo(Base):
    __tablename__ = "pacote_modulos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pacote_id = Column(UUID(as_uuid=True), ForeignKey('pacotes.id'), nullable=False)
    modulo_codigo = Column(String(50), nullable=False)

    # Relationships
    pacote = relationship("Pacote", back_populates="modulos")
```

### 5.2. Seed de dados iniciais

```python
# services/api/scripts/seed_pacotes.py

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session
from app.models import Pacote, PacoteModulo

PACOTES_INICIAIS = [
    {
        "codigo": "PLAN-BASIC",
        "nome": "Básico",
        "descricao": "Ideal para pequenos produtores",
        "preco_mensal": 99.00,
        "preco_anual": 990.00,
        "modulos": ["CORE", "A1_PLANEJAMENTO", "F1_TESOURARIA"]
    },
    {
        "codigo": "PLAN-PRO",
        "nome": "Profissional",
        "descricao": "Para médias propriedades",
        "preco_mensal": 299.00,
        "preco_anual": 2990.00,
        "destaque": True,
        "modulos": [
            "CORE", "A1_PLANEJAMENTO", "A2_CAMPO",
            "F1_TESOURARIA", "F2_CUSTOS_ABC", "O1_FROTA"
        ]
    },
    {
        "codigo": "PLAN-ENTERPRISE",
        "nome": "Empresarial",
        "descricao": "Solução completa",
        "preco_mensal": 999.00,
        "preco_anual": 9990.00,
        "max_usuarios_simultaneos": 50,
        "storage_gb": 100,
        "modulos": ["*"]  # Todos os módulos
    }
]

async def seed_pacotes():
    async with async_session() as db:
        for pacote_data in PACOTES_INICIAIS:
            modulos = pacote_data.pop("modulos")

            pacote = Pacote(**pacote_data)
            db.add(pacote)
            await db.flush()

            for modulo_codigo in modulos:
                pacote_modulo = PacoteModulo(
                    pacote_id=pacote.id,
                    modulo_codigo=modulo_codigo
                )
                db.add(pacote_modulo)

        await db.commit()
        print("Pacotes criados com sucesso!")

if __name__ == "__main__":
    asyncio.run(seed_pacotes())
```

---

## 🎨 Fase 6: Frontend - Layout Admin (Dia 14-16)

### 6.1. Criar layout separado

```tsx
// apps/web/src/app/(admin)/layout.tsx

import { AdminSidebar } from "@/components/admin/admin-sidebar"
import { AdminHeader } from "@/components/admin/admin-header"

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <AdminSidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <AdminHeader />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
```

### 6.2. Criar Sidebar

```tsx
// apps/web/src/components/admin/admin-sidebar.tsx

"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Users,
  FileCheck,
  Headset,
  ShoppingCart,
  DollarSign,
  Mail,
  Settings
} from "lucide-react"
import { cn } from "@/lib/utils"

const MENU_ITEMS = [
  {
    icon: LayoutDashboard,
    label: "Dashboard",
    href: "/admin/dashboard"
  },
  {
    icon: Users,
    label: "Assinantes",
    href: "/admin/assinantes"
  },
  {
    icon: FileCheck,
    label: "Assinaturas",
    href: "/admin/assinaturas",
    badge: 3
  },
  {
    icon: Headset,
    label: "Suporte",
    href: "/admin/suporte/tickets",
    badge: 5
  },
  {
    icon: ShoppingCart,
    label: "Pacotes",
    href: "/admin/pacotes"
  },
  {
    icon: DollarSign,
    label: "Financeiro",
    href: "/admin/financeiro"
  },
  {
    icon: Mail,
    label: "E-mails",
    href: "/admin/emails"
  },
  {
    icon: Settings,
    label: "Configurações",
    href: "/admin/config"
  }
]

export function AdminSidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-slate-900 text-white flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-700">
        <h1 className="text-xl font-bold">AgroSaaS Admin</h1>
      </div>

      {/* Menu */}
      <nav className="flex-1 p-4 space-y-1">
        {MENU_ITEMS.map((item) => {
          const Icon = item.icon
          const isActive = pathname.startsWith(item.href)

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                isActive
                  ? "bg-slate-800 text-white"
                  : "text-slate-300 hover:bg-slate-800/50"
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="flex-1">{item.label}</span>
              {item.badge && (
                <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                  {item.badge}
                </span>
              )}
            </Link>
          )
        })}
      </nav>

      {/* User Info */}
      <div className="p-4 border-t border-slate-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-slate-700 rounded-full" />
          <div className="flex-1">
            <p className="text-sm font-medium">Admin User</p>
            <p className="text-xs text-slate-400">Super Admin</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
```

### 6.3. Criar Dashboard

```tsx
// apps/web/src/app/(admin)/admin/dashboard/page.tsx

import { MetricCard } from "@/components/admin/dashboard/metric-card"
import { NovosAssinantesChart } from "@/components/admin/dashboard/novos-assinantes-chart"
import { AlertasCriticos } from "@/components/admin/dashboard/alertas-criticos"
import { Users, UserCheck, UserX, Ticket } from "lucide-react"

export default async function DashboardPage() {
  // Buscar métricas da API
  const metricas = await fetch('http://localhost:8000/admin/dashboard/metricas').then(r => r.json())

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {/* Cards de Métricas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Novos Assinantes"
          value={metricas.novos_assinantes.total}
          change={metricas.novos_assinantes.variacao_percentual}
          icon={<Users />}
        />
        <MetricCard
          title="Assinantes Ativos"
          value={metricas.assinantes_ativos}
          icon={<UserCheck />}
        />
        <MetricCard
          title="Tickets Abertos"
          value={metricas.chamados_abertos}
          icon={<Ticket />}
        />
        <MetricCard
          title="MRR"
          value={`R$ ${metricas.mrr.toLocaleString('pt-BR')}`}
          icon={<DollarSign />}
        />
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <NovosAssinantesChart />
        <AlertasCriticos />
      </div>
    </div>
  )
}
```

---

## ✅ Checklist Completo

### Backend

#### Infraestrutura
- [ ] Migrations criadas
- [ ] Modelos SQLAlchemy implementados
- [ ] Seeds de dados iniciais
- [ ] Sistema de autenticação admin

#### Dashboard
- [ ] Endpoint de métricas
- [ ] Gráfico de novos assinantes
- [ ] Alertas críticos

#### Assinantes
- [ ] Listagem com filtros
- [ ] Detalhes do assinante
- [ ] Impersonate
- [ ] Reset de senha
- [ ] Alterar status

#### Assinaturas
- [ ] Listagem e filtros
- [ ] Workflow de aprovação
- [ ] Suspensão/Reativação

#### Suporte
- [ ] CRUD de tickets
- [ ] Sistema de mensagens
- [ ] Upload de anexos
- [ ] Cálculo de SLA
- [ ] Métricas de suporte

#### Pacotes
- [ ] CRUD de pacotes
- [ ] Gestão de módulos
- [ ] Cupons de desconto

#### Financeiro
- [ ] Transferências bancárias
- [ ] Conciliação
- [ ] Relatórios (MRR, Churn)

#### Emails
- [ ] Templates
- [ ] Histórico de envios
- [ ] Variáveis dinâmicas

#### Configurações
- [ ] SMTP
- [ ] Storage
- [ ] Push
- [ ] Stripe
- [ ] Gerais

### Frontend

#### Layout
- [ ] Layout admin separado
- [ ] Sidebar com menu
- [ ] Header
- [ ] Breadcrumbs

#### Dashboard
- [ ] Cards de métricas
- [ ] Gráficos
- [ ] Alertas críticos

#### Assinantes
- [ ] Listagem
- [ ] Detalhes
- [ ] Botão impersonate
- [ ] Dialog reset senha
- [ ] Filtros

#### Assinaturas
- [ ] Painel de aprovação
- [ ] Histórico
- [ ] Filtros

#### Suporte
- [ ] Lista de tickets
- [ ] Detalhes do ticket
- [ ] Responder ticket
- [ ] Indicador de SLA

#### Pacotes
- [ ] Listagem
- [ ] Formulário criar/editar
- [ ] Seletor de módulos

#### Financeiro
- [ ] Dashboard financeiro
- [ ] Tabela de transferências
- [ ] Gráficos MRR/Churn

#### Emails
- [ ] Lista de templates
- [ ] Editor de templates
- [ ] Preview

#### Configurações
- [ ] Formulários de config
- [ ] Teste de integrações

---

**Última atualização:** 2026-03-10
**Versão:** 1.0
