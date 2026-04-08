---
modulo: Contabilidade
submodulo: Overview
nivel: all
core: false
dependencias_core:
  - Identidade e Acesso
  - Configurações Globais
dependencias_modulos:
  - ../financeiro/
standalone: false
complexidade: "-"
assinante_alvo:
  - Produtor Rural PF
  - Produtor Rural PJ
  - Escritórios de Contabilidade Rural
  - Cooperativas Agrícolas
---

# Contabilidade — Visão Geral do Módulo

## Descrição Funcional

O módulo de Contabilidade do AgroSaaS oferece funcionalidades contábeis especializadas para o agronegócio brasileiro, desde a escrituração básica do LCDPR até a consolidação multi-empresa e geração automatizada de obrigações fiscais (SPED). O módulo é organizado em três tiers progressivos que acompanham a maturidade contábil do produtor rural.

## Tabela de Tiers

| Tier | Submódulo | Complexidade | Descrição |
|------|-----------|-------------|-----------|
| **Essencial** | LCDPR | M | Livro Caixa Digital do Produtor Rural — obrigação fiscal para PF com receita bruta > R$ 56.000 |
| **Essencial** | Plano de Contas Rural | S | Plano de contas adaptado à atividade rural brasileira |
| **Essencial** | Lançamentos Contábeis | M | Escrituração por partidas dobradas com rastreabilidade |
| **Profissional** | Integração Contábil | L | Exportação para contabilidade externa (SPED, CSV, ERP) |
| **Profissional** | DRE Rural | M | Demonstrativo de Resultado por safra e fazenda |
| **Profissional** | Balancete | M | Balancete de verificação com filtros por período e centro de custo |
| **Enterprise** | Multi-Empresa | XL | Consolidação contábil multi-CNPJ com eliminações intercompany |
| **Enterprise** | IRPF Rural | L | Apuração automática do IRPF atividade rural |
| **Enterprise** | SPED Fiscal | XL | Geração de SPED Fiscal e EFD-Contribuições |

## Personas

- **Produtor Rural PF:** Precisa cumprir obrigação do LCDPR e acompanhar resultado da atividade.
- **Produtor Rural PJ:** Necessita de DRE, balancete e integração com contabilidade externa.
- **Contador Rural:** Precisa de dados estruturados para escrituração e entrega de obrigações acessórias.
- **Gestor de Grupo Agro:** Consolida resultados de múltiplas fazendas e CNPJs.

## Dores que resolve

- Falta de integração entre controle financeiro operacional e escrituração contábil.
- Dificuldade em gerar LCDPR a partir de dados dispersos em planilhas.
- Retrabalho na exportação de dados para o contador externo.
- Impossibilidade de visualizar resultado contábil por safra/talhão/fazenda.
- Risco de multas por atraso ou erro em obrigações acessórias (SPED, IRPF).

## Regras de Negócio

1. Todos os lançamentos seguem o método de partidas dobradas.
2. O plano de contas padrão segue a estrutura recomendada pelo CFC para atividade rural.
3. O LCDPR é obrigatório para PF com receita bruta anual > R$ 56.000 (limite atualizado conforme legislação vigente).
4. Lançamentos aprovados não podem ser excluídos, apenas estornados.
5. O fechamento mensal trava lançamentos do período.

## Entidades de Dados Principais

- `PlanoContas` — árvore hierárquica de contas contábeis
- `LancamentoContabil` — registro de partida dobrada (débito/crédito)
- `LivroLCDPR` — escrituração digital conforme layout da Receita Federal
- `DREReport` — demonstrativo de resultado gerado por período/safra
- `Balancete` — saldos de contas em período específico
- `SPEDExport` — registro de exportações SPED geradas
- `ConsolidacaoMultiEmpresa` — agregação de dados de múltiplos CNPJs

## Integrações Necessárias

- **Financeiro (despesas/receitas):** Origem dos dados para lançamentos automáticos.
- **Agrícola (safras/talhões):** Dimensão de rateio para DRE rural.
- **Estoque:** Movimentações impactam custo contábil.
- **Identidade e Acesso:** Permissões por módulo e tenant isolation.
- **Receita Federal:** Layout LCDPR e SPED Fiscal.

## Fluxo de Uso Principal

1. Configurar plano de contas (usar modelo padrão ou personalizar).
2. Lançamentos são gerados automaticamente a partir do módulo financeiro ou inseridos manualmente.
3. Revisar e aprovar lançamentos do período.
4. Gerar relatórios (balancete, DRE rural).
5. Exportar dados para contador externo ou gerar LCDPR/SPED diretamente.

## Casos Extremos e Exceções

- Produtor com múltiplos CPFs/CNPJs na mesma conta.
- Mudança de regime tributário no meio do exercício.
- Estorno de lançamento em período já fechado (requer reabertura).
- Atividade rural mista (agricultura + pecuária) com rateio de custos indiretos.

## Critérios de Aceite

- Plano de contas padrão rural disponível ao ativar o módulo.
- Lançamentos do financeiro refletidos automaticamente na contabilidade.
- LCDPR gerado no formato oficial da Receita Federal.
- Relatórios (DRE, balancete) conferem com lançamentos registrados.
- Exportação SPED validada pelo PVA sem erros.

## Sugestões de Melhoria Futura

- IA para classificação automática de lançamentos contábeis.
- Dashboard contábil com indicadores de saúde financeira rural.
- Integração direta com e-CAC para envio de LCDPR.
- Conciliação bancária automática com Open Banking.
- Comparativo de resultado entre safras para benchmarking.
