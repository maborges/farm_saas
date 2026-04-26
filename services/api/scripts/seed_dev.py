"""
Seed de Desenvolvimento - AgroSaaS

Cria dados básicos para teste e desenvolvimento:
- Planos de assinatura
- Tenant (empresa)
- Usuários (admin, owner, operador)
- Fazenda
- Perfis de acesso
- Configurações

Uso:
    cd services/api
    source .venv/bin/activate
    python scripts/seed_dev.py
"""

import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_maker, DB_URL
from core.models.tenant import Tenant
from core.models.auth import Usuario, PerfilAcesso, TenantUsuario, FazendaUsuario
from core.models.billing import PlanoAssinatura, AssinaturaTenant
from core.models.unidade_produtiva import UnidadeProdutiva as Fazenda
from core.constants import Modulos


async def seed() -> None:
    """Popula banco com dados de desenvolvimento."""
    
    print("=" * 60)
    print("🌱 SEED DE DESENVOLVIMENTO - AgroSaaS")
    print("=" * 60)
    
    async with async_session_maker() as session:
        try:
            # ==========================================================================
            # 1. CRIAR PLANOS DE ASSINATURA
            # ==========================================================================
            print("\n📦 Criando planos de assinatura...")
            
            planos = [
                {
                    "nome": "Plano Básico",
                    "descricao": "Para pequenos produtores",
                    "descricao_marketing": "Ideal para quem está começando na agricultura digital",
                    "preco_mensal": 199.0,
                    "preco_anual": 1990.0,
                    "modulos_inclusos": [Modulos.CORE, Modulos.AGRICOLA_PLANEJAMENTO],
                    "max_fazendas": 3,
                    "limite_usuarios_maximo": 5,
                    "tem_trial": True,
                    "dias_trial": 15,
                    "ativo": True,
                    "destaque": False,
                    "disponivel_site": True,
                    "disponivel_crm": True,
                },
                {
                    "nome": "Plano Profissional",
                    "descricao": "Para médios produtores",
                    "descricao_marketing": "Completo para gestão integrada da fazenda",
                    "preco_mensal": 399.0,
                    "preco_anual": 3990.0,
                    "modulos_inclusos": [
                        Modulos.CORE, Modulos.AGRICOLA_PLANEJAMENTO,
                        Modulos.AGRICOLA_CAMPO, Modulos.AGRICOLA_DEFENSIVOS,
                        Modulos.PECUARIA_REBANHO, Modulos.FINANCEIRO_TESOURARIA,
                    ],
                    "max_fazendas": 10,
                    "limite_usuarios_maximo": 15,
                    "tem_trial": True,
                    "dias_trial": 15,
                    "ativo": True,
                    "destaque": True,
                    "disponivel_site": True,
                    "disponivel_crm": True,
                },
                {
                    "nome": "Plano Enterprise",
                    "descricao": "Para grandes operações",
                    "descricao_marketing": "Máxima performance e personalização",
                    "preco_mensal": 799.0,
                    "preco_anual": 7990.0,
                    "modulos_inclusos": [
                        Modulos.CORE, Modulos.AGRICOLA_PLANEJAMENTO,
                        Modulos.AGRICOLA_CAMPO, Modulos.AGRICOLA_DEFENSIVOS,
                        Modulos.AGRICOLA_PRECISAO, Modulos.AGRICOLA_COLHEITA,
                        Modulos.PECUARIA_REBANHO, Modulos.FINANCEIRO_TESOURARIA,
                        Modulos.OPERACIONAL_FROTA, Modulos.OPERACIONAL_ESTOQUE,
                        Modulos.RH_REMUNERACAO,
                    ],
                    "max_fazendas": -1,  # Ilimitado
                    "limite_usuarios_maximo": 50,
                    "tem_trial": True,
                    "dias_trial": 30,
                    "ativo": True,
                    "destaque": False,
                    "disponivel_site": True,
                    "disponivel_crm": True,
                },
            ]
            
            from core.models.billing import PlanoAssinatura
            
            for plano_data in planos:
                # Verificar se já existe
                result = await session.execute(
                    text("SELECT id FROM planos_assinatura WHERE nome = :nome"),
                    {"nome": plano_data["nome"]}
                )
                if result.fetchone():
                    print(f"  ⚠️  Plano '{plano_data['nome']}' já existe")
                    continue
                
                plano = PlanoAssinatura(**plano_data)
                session.add(plano)
                print(f"  ✅ Plano '{plano_data['nome']}' criado")
            
            await session.commit()
            
            # ==========================================================================
            # 2. CRIAR PERFIS DE ACESSO PADRÃO
            # ==========================================================================
            print("\n👤 Criando perfis de acesso...")
            
            perfis_data = [
                {
                    "nome": "Owner",
                    "descricao": "Acesso total ao tenant",
                    "is_custom": False,
                    "permissoes": {"*": "*"},
                },
                {
                    "nome": "Administrador",
                    "descricao": "Acesso administrativo completo",
                    "is_custom": False,
                    "permissoes": {
                        "agricola": "write",
                        "pecuaria": "write",
                        "financeiro": "write",
                        "operacional": "write",
                        "rh": "write",
                    },
                },
                {
                    "nome": "Agrônomo",
                    "descricao": "Gestão agrícola e monitoramento",
                    "is_custom": False,
                    "permissoes": {
                        "agricola": "write",
                        "pecuaria": "read",
                        "financeiro": "read",
                    },
                },
                {
                    "nome": "Operador",
                    "descricao": "Registro de operações de campo",
                    "is_custom": False,
                    "permissoes": {
                        "agricola": "write",
                        "pecuaria": "write",
                        "financeiro": "none",
                    },
                },
                {
                    "nome": "Consultor",
                    "descricao": "Apenas leitura para consultoria",
                    "is_custom": False,
                    "permissoes": {
                        "agricola": "read",
                        "pecuaria": "read",
                        "financeiro": "read",
                    },
                },
            ]
            
            for perfil_data in perfis_data:
                result = await session.execute(
                    text("SELECT id FROM perfis_acesso WHERE nome = :nome"),
                    {"nome": perfil_data["nome"]}
                )
                if result.fetchone():
                    print(f"  ⚠️  Perfil '{perfil_data['nome']}' já existe")
                    continue
                
                perfil = PerfilAcesso(**perfil_data)
                session.add(perfil)
                print(f"  ✅ Perfil '{perfil_data['nome']}' criado")
            
            await session.commit()
            
            # ==========================================================================
            # 3. CRIAR TENANT (EMPRESA)
            # ==========================================================================
            print("\n🏢 Criando tenant (empresa)...")
            
            # Verificar se já existe
            result = await session.execute(
                text("SELECT id FROM tenants WHERE documento = :documento"),
                {"documento": "12345678000199"}
            )
            tenant_existente = result.fetchone()
            
            if tenant_existente:
                print("  ⚠️  Tenant de teste já existe")
                result = await session.execute(
                    text("SELECT id, nome FROM tenants WHERE documento = :documento"),
                    {"documento": "12345678000199"}
                )
                tenant_data = result.fetchone()
                tenant_id = tenant_data[0]
                tenant_nome = tenant_data[1]
                print(f"  ✅ Usando tenant existente: {tenant_nome} (ID: {tenant_id})")
            else:
                tenant = Tenant(
                    nome="Fazenda Santa Bárbara",
                    documento="12345678000199",
                    email_responsavel="contato@santabarbara.com.br",
                    telefone_responsavel="(65) 99999-9999",
                    ativo=True,
                    storage_limite_mb=10240,
                    storage_usado_mb=0,
                )
                session.add(tenant)
                await session.commit()
                await session.refresh(tenant)
                
                tenant_id = tenant.id
                tenant_nome = tenant.nome
                print(f"  ✅ Tenant '{tenant_nome}' criado (ID: {tenant_id})")
            
            # ==========================================================================
            # 4. CRIAR ASSINATURA DO TENANT
            # ==========================================================================
            print("\n💳 Criando assinatura...")
            
            # Buscar plano profissional
            result = await session.execute(
                text("SELECT id FROM planos_assinatura WHERE nome = 'Plano Profissional'")
            )
            plano_result = result.fetchone()
            
            if not plano_result:
                print("  ❌ Plano Profissional não encontrado!")
                return
            
            plano_id = plano_result[0]
            
            # Verificar assinatura existente
            result = await session.execute(
                text("SELECT id FROM assinaturas_tenant WHERE tenant_id = :tenant_id"),
                {"tenant_id": tenant_id}
            )
            assinatura_existente = result.fetchone()

            from core.models.billing import AssinaturaTenant
            from datetime import timedelta

            if assinatura_existente:
                print("  ⚠️  Assinatura já existe")
            else:
                assinatura = AssinaturaTenant(
                    tenant_id=tenant_id,
                    plano_id=plano_id,
                    status="ATIVA",
                    tipo_assinatura="TENANT",
                    data_inicio=datetime.now(timezone.utc),
                    data_proxima_renovacao=datetime.now(timezone.utc) + timedelta(days=30),
                )
                session.add(assinatura)
                await session.commit()
                print("  ✅ Assinatura 'Plano Profissional' ativada")
            
            # ==========================================================================
            # 5. CRIAR USUÁRIOS
            # ==========================================================================
            print("\n👥 Criando usuários...")
            
            usuarios_data = [
                {
                    "email": "owner@santabarbara.com.br",
                    "nome": "João Silva",
                    "senha": "senha123",
                    "perfil": "Owner",
                    "is_owner": True,
                },
                {
                    "email": "admin@santabarbara.com.br",
                    "nome": "Maria Santos",
                    "senha": "senha123",
                    "perfil": "Administrador",
                    "is_owner": False,
                },
                {
                    "email": "agronomo@santabarbara.com.br",
                    "nome": "Pedro Oliveira",
                    "senha": "senha123",
                    "perfil": "Agrônomo",
                    "is_owner": False,
                },
                {
                    "email": "operador@santabarbara.com.br",
                    "nome": "Carlos Souza",
                    "senha": "senha123",
                    "perfil": "Operador",
                    "is_owner": False,
                },
            ]
            
            from core.models.auth import Usuario, TenantUsuario
            from core.services.auth_service import hash_password
            
            for usuario_data in usuarios_data:
                # Verificar se usuário já existe
                result = await session.execute(
                    text("SELECT id FROM usuarios WHERE email = :email"),
                    {"email": usuario_data["email"]}
                )
                usuario_existente = result.fetchone()
                
                if usuario_existente:
                    print(f"  ⚠️  Usuário '{usuario_data['email']}' já existe")
                    usuario_id = usuario_existente[0]
                else:
                    # Criar usuário
                    usuario = Usuario(
                        email=usuario_data["email"],
                        username=usuario_data["email"].split("@")[0],  # Parte antes do @
                        nome_completo=usuario_data["nome"],
                        senha_hash=hash_password(usuario_data["senha"]),
                        ativo=True,
                    )
                    session.add(usuario)
                    await session.commit()
                    await session.refresh(usuario)
                    usuario_id = usuario.id
                    print(f"  ✅ Usuário '{usuario_data['email']}' criado")
                
                # Vincular usuário ao tenant
                result = await session.execute(
                    text("SELECT id FROM tenant_usuarios WHERE usuario_id = :usuario_id AND tenant_id = :tenant_id"),
                    {"usuario_id": usuario_id, "tenant_id": tenant_id}
                )
                vinculo_existente = result.fetchone()
                
                if vinculo_existente:
                    print(f"  ⚠️  Vínculo com tenant já existe")
                else:
                    # Buscar perfil
                    result = await session.execute(
                        text("SELECT id FROM perfis_acesso WHERE nome = :nome"),
                        {"nome": usuario_data["perfil"]}
                    )
                    perfil_result = result.fetchone()
                    
                    if perfil_result:
                        perfil_id = perfil_result[0]
                        
                        tenant_usuario = TenantUsuario(
                            tenant_id=tenant_id,
                            usuario_id=usuario_id,
                            perfil_id=perfil_id,
                            status="ATIVO",
                            is_owner=usuario_data["is_owner"],
                        )
                        session.add(tenant_usuario)
                        await session.commit()
                        print(f"  ✅ Vínculo {usuario_data['perfil']} criado")
            
            # ==========================================================================
            # 6. CRIAR FAZENDA
            # ==========================================================================
            print("\n🚜 Criando fazenda...")
            
            result = await session.execute(
                text("SELECT id FROM unidades_produtivas WHERE tenant_id = :tenant_id AND nome = :nome"),
                {"tenant_id": tenant_id, "nome": "Fazenda Santa Bárbara"}
            )
            fazenda_existente = result.fetchone()
            
            if fazenda_existente:
                print("  ⚠️  Fazenda já existe")
                unidade_produtiva_id = fazenda_existente[0]
            else:
                fazenda = Fazenda(
                    tenant_id=tenant_id,
                    nome="Fazenda Santa Bárbara",
                    cpf_cnpj="12345678000199",
                    inscricao_estadual="123456789",
                    area_total_ha=1500.0,
                    coordenadas_sede="-15.7801,-47.9292",
                    ativo=True,
                )
                session.add(fazenda)
                await session.commit()
                await session.refresh(fazenda)
                unidade_produtiva_id = fazenda.id
                print(f"  ✅ Fazenda '{fazenda.nome}' criada (ID: {unidade_produtiva_id})")
            
            # ==========================================================================
            # 7. RESUMO
            # ==========================================================================
            print("\n" + "=" * 60)
            print("✅ SEED CONCLUÍDO COM SUCESSO!")
            print("=" * 60)
            print("\n📋 RESUMO:")
            print(f"  • Tenant: {tenant_nome}")
            print(f"  • Plano: Profissional")
            print(f"  • Fazenda: Fazenda Santa Bárbara (1500 ha)")
            print(f"  • Usuários: 4 criados/vinculados")
            print(f"  • Perfis: 5 perfis padrão")
            print("\n🔐 CREDENCIAIS DE TESTE:")
            print("  • Owner: owner@santabarbara.com.br / senha123")
            print("  • Admin: admin@santabarbara.com.br / senha123")
            print("  • Agrônomo: agronomo@santabarbara.com.br / senha123")
            print("  • Operador: operador@santabarbara.com.br / senha123")
            print("\n🌐 ACESSO:")
            print("  • Frontend: http://localhost:3000")
            print("  • Backend: http://localhost:8000")
            print("  • API Docs: http://localhost:8000/docs")
            print("=" * 60)
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(seed())
