# Módulo A1 - Planejamento de Safra e Orçamento

**ID:** `A1_PLANEJAMENTO`
**Categoria:** AGRICOLA
**Status:** 🔄 Em Desenvolvimento
**Preço Base:** R$ 199,00/mês

## 📋 Descrição

Módulo para gestão completa de ciclos agrícolas com foco em planejamento estratégico e controle orçamentário.

## ✨ Funcionalidades

### Implementadas
- ✅ Health check do módulo
- ✅ Feature gate de acesso

### Em Desenvolvimento
- 🔄 Cadastro de safras (PRINCIPAL, SAFRINHA, PERENE)
- 🔄 Orçamento de custos por hectare
- 🔄 Projeção de receita e margem
- 🔄 Histórico de safras anteriores
- 🔄 Comparação orçado vs realizado

### Planejadas
- 📅 Rotação de culturas inteligente
- 📅 Integração com módulo de custos (F2)
- 📅 Dashboards analíticos de performance
- 📅 Alertas de desvio orçamentário

## 🔗 Dependências

- **CORE** (obrigatório) - Multi-tenancy, autenticação, GIS

## 🤝 Integrações

Este módulo se integra com:

| Módulo | Tipo | Descrição |
|--------|------|-----------|
| **A2_CAMPO** | Opcional | Operações planejadas viram ordens de serviço |
| **A5_COLHEITA** | Opcional | Comparação produção real vs planejada |
| **F2_CUSTOS_ABC** | Opcional | Rateio automático de custos por safra |
| **O2_ESTOQUE** | Opcional | Previsão de necessidade de insumos |

## 🚀 Endpoints

| Método | Rota | Descrição | Status |
|--------|------|-----------|--------|
| GET | `/agricola/planejamento/health` | Health check | ✅ |
| POST | `/agricola/planejamento/safras` | Criar safra | 🔄 |
| GET | `/agricola/planejamento/safras` | Listar safras | 🔄 |
| GET | `/agricola/planejamento/safras/{id}` | Buscar safra | 🔄 |
| PATCH | `/agricola/planejamento/safras/{id}` | Atualizar safra | 🔄 |
| POST | `/agricola/planejamento/safras/{id}/orcamento` | Criar orçamento | 🔄 |

## 📦 Modelos de Dados

### Safra
```python
{
    "id": "uuid",
    "tenant_id": "uuid",
    "nome": "Soja 2025/26",
    "cultura": "Soja",
    "ciclo": "PRINCIPAL",  # ou SAFRINHA, PERENE
    "data_inicio": "2025-09-15",
    "data_fim_prevista": "2026-03-30",
    "hectares_planejados": 1500.00,
    "producao_esperada_sc": 90000.00  # sacas
}
```

### OrcamentoSafra
```python
{
    "id": "uuid",
    "safra_id": "uuid",
    "custo_total_previsto": 4500000.00,
    "custo_por_hectare_previsto": 3000.00,
    "receita_esperada": 7200000.00,
    "margem_esperada": 2700000.00
}
```

## 🔧 Como Usar

### 1. Registrar no main.py

```python
from agricola.a1_planejamento.router import router as router_planejamento

app.include_router(router_planejamento, prefix="/api/v1")
```

### 2. Testar o módulo

```bash
# Health check
curl -H "Authorization: Bearer {token}" \
     http://localhost:8000/api/v1/agricola/planejamento/health
```

### 3. Criar safra (quando implementado)

```bash
curl -X POST \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Soja 2025/26",
    "cultura": "Soja",
    "ciclo": "PRINCIPAL",
    "data_inicio": "2025-09-15",
    "hectares_planejados": 1500
  }' \
  http://localhost:8000/api/v1/agricola/planejamento/safras
```

## 🧪 Testes

```bash
cd services/api
pytest agricola/a1_planejamento/tests/ -v --cov=agricola/a1_planejamento
```

## 📈 Roadmap

### v1.0.0 (MVP - Sprint 1)
- [x] Estrutura base do módulo
- [x] Feature gate implementado
- [ ] CRUD de safras
- [ ] Orçamentos básicos

### v1.1.0 (Sprint 2)
- [ ] Comparação orçado vs realizado
- [ ] Relatórios de performance
- [ ] Integração com A2_CAMPO

### v1.2.0 (Sprint 3)
- [ ] Rotação de culturas inteligente
- [ ] Dashboards analíticos
- [ ] Integração com F2_CUSTOS_ABC

## 🐛 Issues Conhecidos

Nenhum issue conhecido no momento.

## 📝 Changelog

### [Unreleased] - 2026-03-10
- Estrutura inicial criada
- Health check implementado
- Feature gate configurado
- Documentação base criada

---

**Última atualização:** 2026-03-10
**Responsável:** Equipe de Desenvolvimento
**Suporte:** [Abrir chamado](https://github.com/farm/issues)
