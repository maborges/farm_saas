# AgroSaaS - Dependências e Impacto entre Módulos

**Versão:** 1.0.0  
**Última Atualização:** 2026-03-31  
**Status:** Ativo  

---

## 📋 Índice

1. [Matriz de Dependências](#1-matriz-de-dependências)
2. [Fluxo de Dados](#2-fluxo-de-dados)
3. [Impacto de Mudanças](#3-impacto-de-mudanças)
4. [Dependências de Cadastro](#4-dependências-de-cadastro)
5. [Dependências de Módulos](#5-dependências-de-módulos)
6. [Checklist de Impacto](#6-checklist-de-impacto)

---

## 1. Matriz de Dependências

### Visão Geral

```
Legenda:
  →  = "depende de" (consome dados/serviços)
  ←  = "é dependido por" (fornece dados/serviços)
  ↔  = "dependência bidirecional"
```

### Matriz Completa

| Módulo | Depende De | Fornece Para |
|--------|------------|--------------|
| **CORE** | - | TODOS |
| **A1_PLANEJAMENTO** | CORE, Cadastros | F1, A5 |
| **A2_CAMPO** | CORE, A1, O2 | F1, O2 |
| **A3_DEFENSIVOS** | CORE, A2 | A2, O2 |
| **A4_PRECISAO** | CORE, A1 | A2 |
| **A5_COLHEITA** | CORE, A1 | F1, A1 |
| **P1_REBANHO** | CORE, Cadastros | F1, O2 |
| **P4_LEITE** | CORE, P1 | F1 |
| **F1_TESOURARIA** | CORE | - |
| **F2_CUSTOS_ABC** | CORE, F1 | - |
| **O1_FROTA** | CORE, O2 | F1, A2 |
| **O2_ESTOQUE** | CORE, Cadastros | A2, O1, P1, F1 |
| **O3_COMPRAS** | CORE, O2, Cadastros | O2, F1 |
| **RH1_REMUNERACAO** | CORE | F1 |

---

## 2. Fluxo de Dados

### Fluxo Principal - Agricultura

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUXO AGRÍCOLA COMPLETO                      │
└─────────────────────────────────────────────────────────────────┘

1. PLANEJAMENTO (A1)
   ┌──────────────┐
   │  A1_PLANEJA- │
   │    MENTO     │
   └──────┬───────┘
          │ Cria: Safras, Orçamentos
          ▼
2. PREPARO
   ┌──────────────┐     ┌──────────────┐
   │  O2_ESTOQUE  │────→│  A2_CAMPO    │
   │  (Insumos)   │     │  (Operações) │
   └──────────────┘     └──────┬───────┘
                               │ Consome insumos
                               │ Gera custos
                               ▼
3. EXECUÇÃO
   ┌──────────────┐     ┌──────────────┐
   │  O1_FROTA    │────→│  A2_CAMPO    │
   │  (Máquinas)  │     │  (Operações) │
   └──────────────┘     └──────┬───────┘
                               │
                               ▼
4. COLHEITA (A5)
   ┌──────────────┐
   │  A5_COLHEITA │
   │  (Romaneios) │
   └──────┬───────┘
          │ Gera: Produtividade, Receita
          ▼
5. FINANCEIRO (F1)
   ┌──────────────┐
   │  F1_TESOURA- │
   │     RIA      │
   └──────────────┘
   Recebe: Receitas (romaneios)
           Despesas (operações)
```

### Fluxo Pecuária

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUXO PECUÁRIO COMPLETO                      │
└─────────────────────────────────────────────────────────────────┘

1. ANIMAIS (P1)
   ┌──────────────┐
   │  P1_REBANHO  │
   │  (Animais)   │
   └──────┬───────┘
          │ Registra: Eventos, Pesagens
          │
          ├──→ O2_ESTOQUE: Consome ração/medicamentos
          │
          └──→ F1_TESOURARIA: Vendas, Compras

2. PRODUÇÃO LEITE (P4)
   ┌──────────────┐
   │  P4_LEITE    │
   │  (Produção)  │
   └──────┬───────┘
          │
          └──→ F1_TESOURARIA: Receitas de venda de leite
```

### Fluxo Financeiro

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUXO FINANCEIRO COMPLETO                    │
└─────────────────────────────────────────────────────────────────┘

                    TODOS OS MÓDULOS
                         │
                         │ (transações)
                         ▼
   ┌─────────────────────────────────────────┐
   │           F1_TESOURARIA                 │
   │  ┌───────────────────────────────────┐  │
   │  │  Receitas ←→ Despesas ←→ Rateios  │  │
   │  └───────────────────────────────────┘  │
   └─────────────────────────────────────────┘
                         │
                         │ (consolidação)
                         ▼
   ┌─────────────────────────────────────────┐
   │           F2_CUSTOS_ABC                 │
   │  ┌───────────────────────────────────┐  │
   │  │  Rateios → Centros de Custo       │  │
   │  │  (Safras, Talhões, Lotes)         │  │
   │  └───────────────────────────────────┘  │
   └─────────────────────────────────────────┘
```

---

## 3. Impacto de Mudanças

### Níveis de Impacto

| Nível | Descrição | Exemplo |
|-------|-----------|---------|
| **CRÍTICO** | Quebra sistema ou multi-tenancy | Alterar `BaseService`, `tenant_id` |
| **ALTO** | Afeta múltiplos módulos | Schema de `safras`, `fin_despesas` |
| **MÉDIO** | Afeta 1-2 módulos | Endpoint específico de módulo |
| **BAIXO** | Impacto localizado | UI de um componente |

### Matriz de Impacto por Tabela

| Tabela | Impacto | Módulos Afetados |
|--------|---------|------------------|
| `tenants` | CRÍTICO | TODOS |
| `usuarios` | CRÍTICO | TODOS |
| `safras` | ALTO | A1, A2, A5, F1, F2 |
| `talhoes` | ALTO | A1, A2, A4, A5, F2 |
| `operacoes_agricolas` | ALTO | A2, F1, O2 |
| `romaneios_colheita` | ALTO | A5, F1 |
| `animais` | ALTO | P1, F1 |
| `eventos_animais` | ALTO | P1, F1 |
| `fin_receitas` | ALTO | F1, A5, P1 |
| `fin_despesas` | ALTO | F1, A2, O1, O3 |
| `estoque_lotes` | MÉDIO | O2, A2, P1 |
| `frota_equipamentos` | MÉDIO | O1, A2 |

### Matriz de Impacto por Endpoint

| Endpoint | Impacto | Frontend Afetado |
|----------|---------|------------------|
| `POST /auth/login` | CRÍTICO | Todo o app |
| `POST /agricola/safras` | ALTO | `/agricola/safras`, Dashboard |
| `POST /financeiro/receitas` | ALTO | `/financeiro/receitas`, Dashboard |
| `POST /operacional/estoque/movimentacoes` | MÉDIO | `/operacional/estoque` |

---

## 4. Dependências de Cadastro

### Tipos de Produto por Módulo

```python
# services/api/core/constants.py
CADASTRO_REQUERIDO_POR = {
    # Agrícola
    "INSUMO_AGRICOLA": [A1_PLANEJAMENTO, A2_CAMPO],
    "SEMENTE":         [A1_PLANEJAMENTO, A2_CAMPO],
    "DEFENSIVO":       [A3_DEFENSIVOS],
    "FERTILIZANTE":    [A1_PLANEJAMENTO, A2_CAMPO],
    
    # Operacional
    "COMBUSTIVEL":     [O1_FROTA, O2_ESTOQUE],
    "PECA_MAQUINARIO": [O1_FROTA, O2_ESTOQUE],
    "MATERIAL_GERAL":  [O2_ESTOQUE, O3_COMPRAS],
    
    # Pecuária
    "RACAO_ANIMAL":    [P1_REBANHO],
    "MEDICAMENTO_ANIMAL": [P1_REBANHO],
    
    # Todos
    "SERVICO":         [CORE],
    "OUTROS":          [CORE],
}
```

### Impacto de Adicionar Novo Tipo

Ao adicionar novo tipo de produto:

1. **Atualizar:** `core/constants.py`
2. **Verificar:** Catálogo de produtos em cada módulo
3. **Frontend:** Filtros de produtos por módulo

---

## 5. Dependências de Módulos

### Árvore de Dependências

```
CORE (Núcleo)
│
├── AGRICOLA
│   ├── A1_PLANEJAMENTO
│   │   └── → A5_COLHEITA (compara planejado vs realizado)
│   │   └── → F1_TESOURARIA (orçamento)
│   │
│   ├── A2_CAMPO
│   │   └── → O2_ESTOQUE (baixa de insumos)
│   │   └── → F1_TESOURARIA (custos)
│   │   └── → O1_FROTA (máquinas)
│   │
│   ├── A3_DEFENSIVOS
│   │   └── → A2_CAMPO (aplicações)
│   │
│   ├── A4_PRECISAO
│   │   └── → A2_CAMPO (prescrições)
│   │
│   └── A5_COLHEITA
│       └── → F1_TESOURARIA (receitas)
│       └── → A1_PLANEJAMENTO (realizado)
│
├── PECUARIA
│   ├── P1_REBANHO
│   │   └── → O2_ESTOQUE (ração/medicamentos)
│   │   └── → F1_TESOURARIA (vendas/compras)
│   │
│   └── P4_LEITE
│       └── → F1_TESOURARIA (receitas)
│
├── FINANCEIRO
│   ├── F1_TESOURARIA
│   │   ← Recebe de: TODOS módulos operacionais
│   │
│   └── F2_CUSTOS_ABC
│       └── → F1_TESOURARIA (rateios)
│       └── → A1, A2, P1 (centros de custo)
│
├── OPERACIONAL
│   ├── O1_FROTA
│   │   └── → O2_ESTOQUE (peças)
│   │   └── → F1_TESOURARIA (custos)
│   │   └── → A2_CAMPO (máquinas em uso)
│   │
│   ├── O2_ESTOQUE
│   │   └── → A2_CAMPO (insumos)
│   │   └── → O1_FROTA (peças)
│   │   └── → P1_REBANHO (ração)
│   │   └── → F1_TESOURARIA (compras)
│   │
│   └── O3_COMPRAS
│       └── → O2_ESTOQUE (entrada)
│       └── → F1_TESOURARIA (despesas)
│
└── RH
    └── RH1_REMUNERACAO
        └── → F1_TESOURARIA (pagamentos)
```

### Regras de Validação

```python
# Ao contratar módulo, validar dependências
def validar_contratacao_modulo(modulo: str, modulos_atuais: list[str]) -> tuple[bool, list[str]]:
    """
    Valida se todas dependências estão presentes.
    Retorna (valido, erros)
    """
    dependencias = {
        "A5_COLHEITA": ["A1_PLANEJAMENTO"],
        "A3_DEFENSIVOS": ["A2_CAMPO"],
        "F2_CUSTOS_ABC": ["F1_TESOURARIA"],
        "O3_COMPRAS": ["O2_ESTOQUE"],
        "P4_LEITE": ["P1_REBANHO"],
    }
    
    erros = []
    for dep in dependencias.get(modulo, []):
        if dep not in modulos_atuais:
            erros.append(f"{modulo} requer {dep}")
    
    return len(erros) == 0, erros
```

---

## 6. Checklist de Impacto

### Ao Modificar CORE

- [ ] Atualizar `01-arquitetura.md`
- [ ] Atualizar `02-modulos.md` (seção Core)
- [ ] Atualizar `03-banco-dados.md` (Core Models)
- [ ] Atualizar `05-api.md` (Core API)
- [ ] Atualizar `06-permissoes.md` (se aplicável)
- [ ] Testar em TODOS módulos
- [ ] Verificar backward compatibility
- [ ] Criar migration (se banco)
- [ ] Atualizar frontend (se API mudou)

### Ao Modificar Módulo Agrícola

- [ ] Atualizar `02-modulos.md` (seção Agrícola)
- [ ] Atualizar `03-banco-dados.md` (tabelas agrícolas)
- [ ] Atualizar `05-api.md` (endpoints agrícolas)
- [ ] Verificar impacto em: F1_TESOURARIA, O2_ESTOQUE
- [ ] Atualizar frontend (`/agricola/*`)
- [ ] Testar integrações (Financeiro, Operacional)

### Ao Modificar Módulo Financeiro

- [ ] Atualizar `02-modulos.md` (seção Financeiro)
- [ ] Atualizar `03-banco-dados.md` (tabelas financeiras)
- [ ] Atualizar `05-api.md` (endpoints financeiros)
- [ ] Verificar impacto em: Todos módulos (é folha)
- [ ] Atualizar frontend (`/financeiro/*`)
- [ ] Testar rateios e consolidações

### Ao Adicionar Nova Tabela

- [ ] Criar model em `core/models/` ou `modulo/models.py`
- [ ] Atualizar `03-banco-dados.md`
- [ ] Criar migration (`alembic revision --autogenerate`)
- [ ] Adicionar em `02-modulos.md` (entidades do módulo)
- [ ] Criar service (herdando `BaseService`)
- [ ] Criar router (com feature gate)
- [ ] Atualizar `05-api.md`
- [ ] Criar schemas Pydantic
- [ ] Frontend: Criar hooks TanStack Query
- [ ] Frontend: Criar componentes

### Ao Adicionar Novo Endpoint

- [ ] Criar router function
- [ ] Adicionar dependências (`require_module`, `require_permission`)
- [ ] Criar schemas (input/output)
- [ ] Atualizar `05-api.md`
- [ ] Atualizar `06-permissoes.md` (nova permissão)
- [ ] Frontend: Criar função em `lib/api.ts`
- [ ] Frontend: Criar hook TanStack Query
- [ ] Testar autenticação/autorização
- [ ] Testar tenant isolation

### Ao Modificar Permissões

- [ ] Atualizar `06-permissoes.md`
- [ ] Atualizar `core/constants.py` (TenantPermissions)
- [ ] Atualizar frontend (`lib/permissions.ts`)
- [ ] Atualizar hooks (`hooks/use-permission.ts`)
- [ ] Testar em diferentes roles
- [ ] Testar em backoffice

---

## Referências Cruzadas

| Documento | Descrição |
|-----------|-----------|
| `docs/qwen/01-arquitetura.md` | Arquitetura geral |
| `docs/qwen/02-modulos.md` | Módulos do sistema |
| `docs/qwen/03-banco-dados.md` | Schema do banco |
| `docs/qwen/05-api.md` | API reference |
| `docs/qwen/06-permissoes.md` | Permissões e RBAC |

---

## Changelog

| Data | Versão | Descrição |
|------|--------|-----------|
| 2026-03-31 | 1.0.0 | Documentação inicial completa |
