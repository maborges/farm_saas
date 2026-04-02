---
modulo: Financeiro
tipo: overview
descricao: Visão geral do módulo Financeiro do AgroSaaS
---

# Módulo Financeiro — Visão Geral

## Propósito

O módulo Financeiro oferece gestão financeira completa para propriedades rurais, desde lançamentos básicos até conciliação automática e custeio de safra. Organizado em três níveis de assinatura (Essencial, Profissional e Enterprise), permite que pequenos produtores comecem com controle de caixa simples e escalem para ferramentas avançadas conforme a operação cresce.

## Níveis e Submódulos

### Essencial
| Submódulo | Complexidade | Descrição |
|-----------|-------------|-----------|
| [Lançamentos Básicos](essencial/lancamentos-basicos.md) | S | Registro de receitas e despesas com categorização |
| [Fluxo de Caixa](essencial/fluxo-caixa.md) | S | Visão consolidada de entradas, saídas e saldo |
| [Categorias e Contas](essencial/categorias-contas.md) | XS | Plano de contas e categorias customizáveis |

### Profissional
| Submódulo | Complexidade | Descrição |
|-----------|-------------|-----------|
| [Contas a Pagar/Receber](profissional/contas-pagar-receber.md) | M | Gestão de vencimentos, parcelas e baixas |
| [Centro de Custo](profissional/centro-custo.md) | M | Rateio de custos por talhão, safra, lote ou atividade |
| [Conciliação Bancária](profissional/conciliacao-bancaria.md) | L | Importação de extratos e conciliação manual |

### Enterprise
| Submódulo | Complexidade | Descrição |
|-----------|-------------|-----------|
| [Conciliação Automática](enterprise/conciliacao-automatica.md) | XL | Matching automático via OFX/API bancária |
| [Crédito Rural](enterprise/credito-rural.md) | L | Controle de contratos, parcelas e carência de crédito rural |
| [Custo de Produção por Safra](enterprise/custo-producao-safra.md) | XL | Apuração de custo completo por safra/talhão |

## Dependências entre Submódulos

```
categorias-contas ──► lancamentos-basicos ──► fluxo-caixa
                                │
                                ▼
                     contas-pagar-receber ──► conciliacao-bancaria ──► conciliacao-automatica
                                │
                                ▼
                          centro-custo ──► custo-producao-safra
                                                    │
                          credito-rural ◄───────────┘
```

## Integrações com Outros Módulos

- **Agrícola:** custeio de safra, operações vinculadas a lançamentos
- **Pecuária:** custos de manejo, compra/venda de animais
- **Operacional/Estoque:** compras de insumos, movimentações de estoque
- **Core/Billing:** limites de uso por plano de assinatura

## Princípios de Design

1. **Multi-tenancy obrigatório:** todo lançamento pertence a um `tenant_id`; isolamento via `BaseService`
2. **Auditoria completa:** toda movimentação financeira gera log imutável
3. **Competência vs. Caixa:** suporte a regime de competência e regime de caixa simultaneamente
4. **Moeda:** BRL como padrão; valores em centavos (`integer`) para evitar arredondamento
