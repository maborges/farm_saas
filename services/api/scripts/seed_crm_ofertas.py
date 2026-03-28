#!/usr/bin/env python3
"""
Seed para criar produtos e planos comerciais padrão do CRM.

Estrutura:
1. Produtos (módulos)
2. Precificação dos módulos
3. Planos comerciais (bundles)
"""
import asyncio
from sqlalchemy import text
import os
from datetime import datetime, timezone
import uuid
import json

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine

# Dados dos produtos padrão
PRODUTOS = [
    {
        "nome": "CRM",
        "slug": "crm",
        "descricao": "Gestão de leads e pipeline comercial",
        "categoria": "core",
        "icone": "📊",
        "features": ["Pipeline customizável", "Funil de vendas", "Relatórios básicos"],
    },
    {
        "nome": "Email Marketing",
        "slug": "email-marketing",
        "descricao": "Campanhas de email e automação",
        "categoria": "core",
        "icone": "✉️",
        "features": ["Templates personalizados", "Automação", "Analytics"],
    },
    {
        "nome": "Analytics",
        "slug": "analytics",
        "descricao": "Análise e inteligência de vendas",
        "categoria": "core",
        "icone": "📈",
        "features": ["Dashboard customizável", "Previsões", "Inteligência artificial"],
    },
    {
        "nome": "API Premium",
        "slug": "api-premium",
        "descricao": "Acesso via API com limites maiores",
        "categoria": "addon",
        "icone": "⚙️",
        "features": ["10M requisições/mês", "Webhooks", "Suporte prioritário"],
    },
    {
        "nome": "Integrações",
        "slug": "integraciones",
        "descricao": "Integrações com ferramentas externas",
        "categoria": "addon",
        "icone": "🔗",
        "features": ["Salesforce", "Zapier", "Microsoft Teams"],
    },
    {
        "nome": "SLA Premium",
        "slug": "sla-premium",
        "descricao": "Suporte SLA com tempo de resposta garantido",
        "categoria": "addon",
        "icone": "⭐",
        "features": ["Suporte 24/7", "SLA 2h", "Dedicado"],
    },
]

# Preços dos produtos (mensal/anual)
PRECOS = {
    "crm": {"mensal": 200, "anual": 2000},
    "email-marketing": {"mensal": 150, "anual": 1500},
    "analytics": {"mensal": 200, "anual": 2000},
    "api-premium": {"mensal": 100, "anual": 1000},
    "integraciones": {"mensal": 75, "anual": 750},
    "sla-premium": {"mensal": 300, "anual": 3000},
}

# Planos comerciais (bundles)
PLANOS = [
    {
        "nome": "Starter",
        "slug": "starter",
        "descricao": "Perfeito para pequenos times começando",
        "tipo_oferta": "bundle",
        "modulos": ["crm"],  # slug dos módulos
        "preco_mensal": 200,
        "preco_anual": 2000,
        "publico_alvo": "startup",
        "tier": 1,
    },
    {
        "nome": "Profissional",
        "slug": "profissional",
        "descricao": "Para equipes em crescimento com necessidades completas",
        "tipo_oferta": "misto",  # base + add-ons
        "modulos": ["crm", "email-marketing", "analytics"],
        "preco_mensal": 450,
        "preco_anual": 4500,
        "publico_alvo": "pme",
        "tier": 2,
    },
    {
        "nome": "Enterprise",
        "slug": "enterprise",
        "descricao": "Solução completa com tudo incluído e suporte dedicado",
        "tipo_oferta": "modular",  # totalmente customizável
        "modulos": ["crm", "email-marketing", "analytics", "api-premium", "integraciones", "sla-premium"],
        "preco_mensal": None,  # Preço customizado
        "preco_anual": None,
        "publico_alvo": "enterprise",
        "tier": 3,
    },
]


async def seed():
    """Seed de produtos e planos usando SQL direto com transações separadas."""
    print("🌱 Seedando produtos e planos do CRM...\n")

    # 1. Criar produtos
    print("📦 Criando produtos...")
    produtos_map = {}

    for dados in PRODUTOS:
        produto_id = str(uuid.uuid4())
        async with engine.begin() as conn:
            try:
                await conn.execute(text("""
                    INSERT INTO crm_produtos (id, nome, slug, descricao, categoria, ativo, posicao, icone, features, created_at)
                    VALUES (:id, :nome, :slug, :descricao, :categoria, :ativo, :posicao, :icone, :features, :created_at)
                """), {
                    "id": produto_id,
                    "nome": dados["nome"],
                    "slug": dados["slug"],
                    "descricao": dados["descricao"],
                    "categoria": dados["categoria"],
                    "ativo": True,
                    "posicao": 0,
                    "icone": dados["icone"],
                    "features": json.dumps(dados["features"]),
                    "created_at": datetime.now(timezone.utc),
                })
                produtos_map[dados["slug"]] = produto_id
                print(f"  ✓ {dados['icone']} {dados['nome']}")
            except Exception as e:
                print(f"  ✗ {dados['nome']}: {str(e)[:80]}")

    # 2. Criar precificações
    print("\n💰 Criando precificações...")

    for slug, preco in PRECOS.items():
        if slug not in produtos_map:
            continue
        async with engine.begin() as conn:
            try:
                await conn.execute(text("""
                    INSERT INTO crm_precificacao_modulo (id, modulo_oferta_id, preco_mensal, preco_anual, vigencia_inicio, vigencia_fim, ativo, created_at)
                    VALUES (:id, :modulo_oferta_id, :preco_mensal, :preco_anual, :vigencia_inicio, :vigencia_fim, :ativo, :created_at)
                """), {
                    "id": str(uuid.uuid4()),
                    "modulo_oferta_id": produtos_map[slug],
                    "preco_mensal": preco["mensal"],
                    "preco_anual": preco["anual"],
                    "vigencia_inicio": datetime.now(timezone.utc),
                    "vigencia_fim": None,
                    "ativo": True,
                    "created_at": datetime.now(timezone.utc),
                })
                print(f"  ✓ {slug}: R${preco['mensal']}/mês, R${preco['anual']}/ano")
            except Exception as e:
                print(f"  ✗ {slug}: {str(e)[:80]}")

    # 3. Criar planos
    print("\n📋 Criando planos comerciais...")

    for dados in PLANOS:
        plano_id = str(uuid.uuid4())
        modulos_inclusos = [produtos_map[slug] for slug in dados["modulos"] if slug in produtos_map]

        async with engine.begin() as conn:
            try:
                await conn.execute(text("""
                    INSERT INTO crm_planos_comerciais (id, nome, slug, descricao, tipo_oferta, modulos_inclusos, preco_mensal_padrao, preco_anual_padrao, público_alvo, tier, ativo, posicao, created_at)
                    VALUES (:id, :nome, :slug, :descricao, :tipo_oferta, :modulos_inclusos, :preco_mensal_padrao, :preco_anual_padrao, :publico_alvo, :tier, :ativo, :posicao, :created_at)
                """), {
                    "id": plano_id,
                    "nome": dados["nome"],
                    "slug": dados["slug"],
                    "descricao": dados["descricao"],
                    "tipo_oferta": dados["tipo_oferta"],
                    "modulos_inclusos": json.dumps(modulos_inclusos),
                    "preco_mensal_padrao": dados["preco_mensal"],
                    "preco_anual_padrao": dados["preco_anual"],
                    "publico_alvo": dados["publico_alvo"],
                    "tier": dados["tier"],
                    "ativo": True,
                    "posicao": 0,
                    "created_at": datetime.now(timezone.utc),
                })

                modulos_str = " + ".join(dados["modulos"])
                if dados["preco_mensal"]:
                    print(f"  ✓ {dados['nome']} (R${dados['preco_mensal']}/mês): {modulos_str}")
                else:
                    print(f"  ✓ {dados['nome']} (Customizado): {modulos_str}")
            except Exception as e:
                print(f"  ✗ {dados['nome']}: {str(e)[:80]}")

    print("\n✅ Seed concluído com sucesso!")
    print("\n📊 Resumo:")
    print(f"   - {len(PRODUTOS)} produtos criados")
    print(f"   - {len(PRECOS)} precificações criadas")
    print(f"   - {len(PLANOS)} planos comerciais criados")


if __name__ == "__main__":
    asyncio.run(seed())
