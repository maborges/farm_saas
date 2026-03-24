# AgroSaaS - Índice de Skills Especializadas

Este documento fornece acesso rápido às skills especializadas para cada módulo do AgroSaaS.

## 📚 Skills Disponíveis

### 🔐 [Core Module Expert](.claude/skills/CORE_MODULE_EXPERT.md)
**Autenticação, Autorização, Multi-tenancy, Billing**

Especialista em:
- JWT e autenticação
- RBAC de dois níveis (Backoffice + Tenant)
- Multi-assinatura e grupos de fazendas
- BaseService e isolamento de tenant
- Onboarding e gestão de equipe
- Sistema de impersonation

**Use quando:** Implementar features de auth, billing, ou gerenciar multi-tenancy

---

### 🌾 [Agricola Module Expert](.claude/skills/AGRICOLA_MODULE_EXPERT.md)
**Gestão de Lavouras, Operações de Campo, Agricultura de Precisão**

Especialista em:
- Safras e talhões (geoespacial)
- Ordens de serviço agrícolas
- Prescrições agronômicas
- NDVI e sensoriamento remoto
- Romaneios de colheita
- Rastreabilidade da produção

**Use quando:** Trabalhar com culturas, campo, precisão ou colheita

---

### 🐄 [Pecuaria Module Expert](.claude/skills/PECUARIA_MODULE_EXPERT.md)
**Gestão de Rebanho, Reprodução, Alimentação, Sanidade**

Especialista em:
- Lotes e piquetes
- Manejos sanitários e reprodutivos
- IATF e genética
- Confinamento (feedlot)
- Pecuária leiteira
- Rastreabilidade individual

**Use quando:** Trabalhar com gado, pastagens, reprodução ou leite

---

### 💰 [Financeiro Module Expert](.claude/skills/FINANCEIRO_MODULE_EXPERT.md)
**Gestão Financeira, Contabilidade de Custos, Compliance Fiscal**

Especialista em:
- Plano de contas rural
- Contas a pagar/receber
- Rateio de custos (ABC)
- DRE e fluxo de caixa
- Análise de rentabilidade por safra
- Barter e hedge de commodities

**Use quando:** Implementar features financeiras, custos ou compliance fiscal

---

### 🚜 [Operacional Module Expert](.claude/skills/OPERACIONAL_MODULE_EXPERT.md)
**Frota, Estoque, Manutenção, Compras**

Especialista em:
- Gestão de maquinário
- Planos de manutenção preventiva
- Ordens de serviço (oficina)
- Inventário multi-armazém
- Processo de compras
- Cotações e fornecedores

**Use quando:** Trabalhar com equipamentos, peças, estoque ou compras

---

### 👨‍💼 [Backoffice/Admin Expert](.claude/skills/BACKOFFICE_ADMIN_EXPERT.md)
**Administração SaaS, Gestão de Assinantes (tenants), Suporte**

Especialista em:
- Gestão de assinantes
- Operações de billing e assinaturas
- Sistema de suporte (tickets)
- Impersonation (admin → tenant)
- Analytics e KPIs (MRR, ARR, churn)
- Configurações globais

**Use quando:** Construir features de backoffice, admin ou analytics

---

## 🎯 Guia Rápido de Uso

### Para Desenvolvimento
1. Identifique o módulo que você vai trabalhar
2. Leia a skill correspondente
3. Consulte a seção **Common Workflows** para entender o fluxo
4. Siga os padrões estabelecidos em **Key Business Rules**
5. Use os exemplos de código fornecidos

### Para Code Review
- Verifique se a implementação segue as **Business Rules** do módulo
- Confirme os **Integration Points** com outros módulos
- Valide os testes conforme **Testing Guidelines**
- Certifique-se do isolamento de tenant (Core Module)

### Para Onboarding
**Dia 1-2:** Leia [CLAUDE.md](CLAUDE.md) + [Core Module Expert](.claude/skills/CORE_MODULE_EXPERT.md)

**Dia 3-5:** Leia as skills dos módulos que você vai trabalhar

**Semana 2+:** Consulte as skills conforme necessário durante desenvolvimento

### Para Troubleshooting
Cada skill tem uma seção **Troubleshooting** com problemas comuns e soluções.

---

## 🔗 Integrações Entre Módulos

```
CORE (Base)
  └─ Autenticação, Multi-tenancy, Billing
      │
      ├─ AGRICOLA ──┬──> OPERACIONAL (equipamentos, insumos)
      │             └──> FINANCEIRO (custos/receitas safra)
      │
      ├─ PECUARIA ──┬──> OPERACIONAL (ração, medicamentos)
      │             ├──> AGRICOLA (pastagens compartilhadas)
      │             └──> FINANCEIRO (custos gado, venda leite)
      │
      ├─ FINANCEIRO ←─── TODOS (recebe custos e receitas)
      │
      └─ OPERACIONAL ──> TODOS (fornece estoque e equipamentos)

BACKOFFICE (Administração)
  └─ Gerencia todos os módulos via backoffice
```

---

## 📖 Documentação Adicional

- [README.md](README.md) - Visão geral do projeto
- [CLAUDE.md](CLAUDE.md) - Guia completo de arquitetura
- [IMPLEMENTACAO_RBAC_MULTI_SUB.md](IMPLEMENTACAO_RBAC_MULTI_SUB.md) - Detalhes de RBAC
- [API_REFERENCE_RBAC.md](API_REFERENCE_RBAC.md) - Referência API RBAC
- [FRONTEND_MAINTENANCE_GUIDE.md](FRONTEND_MAINTENANCE_GUIDE.md) - Guia frontend
- [.claude/skills/README.md](.claude/skills/README.md) - Guia detalhado das skills

---

## 🏗️ Padrões Críticos

### 1. Isolamento de Tenant (OBRIGATÓRIO)
```python
# SEMPRE use BaseService
service = FazendaService(Fazenda, session, tenant_id)
fazendas = await service.list_all()  # Auto-filtra por tenant_id

# NUNCA faça queries diretas
fazendas = session.query(Fazenda).all()  # ❌ ERRADO - vaza dados
```

### 2. Verificação de Permissões
```python
# Backend (source of truth)
@router.get("/safras", dependencies=[Depends(require_tenant_permission("agricola:safras:view"))])

# Frontend (UX apenas)
if (hasPermission('agricola:safras:view')) {
  // Show safras menu
}
```

### 3. Controle de Módulos
```python
# Validate module subscription
@router.get("/safras", dependencies=[Depends(require_module("A1_PLANEJAMENTO"))])
```

---

## 💡 Quando Usar Cada Skill

| Tarefa | Skill Primária | Skills Secundárias |
|--------|---------------|-------------------|
| Implementar login/signup | Core | - |
| Criar safra | Agricola | Financeiro (custos) |
| Registrar pesagem de gado | Pecuaria | - |
| Lançar despesa | Financeiro | Agricola/Pecuaria (rateio) |
| Criar ordem de serviço (campo) | Agricola | Operacional (equipamento) |
| Manutenção de trator | Operacional | Financeiro (custos) |
| Processar billing | Backoffice | Core (subscription) |
| Criar ticket suporte | Backoffice | Core (impersonation) |

---

## ✅ Checklist de Implementação

Ao implementar uma nova feature:

- [ ] Consultei a skill do módulo correspondente
- [ ] Segui os padrões de Business Rules
- [ ] Implementei isolamento de tenant (BaseService)
- [ ] Adicionei verificação de permissões
- [ ] Validei acesso ao módulo (se aplicável)
- [ ] Criei testes conforme Testing Guidelines
- [ ] Documentei integrações com outros módulos
- [ ] Revisei seção de Performance Considerations

---

**Autor:** Claude Code (Anthropic)  
**Data:** 14/03/2025  
**Versão:** 1.0
