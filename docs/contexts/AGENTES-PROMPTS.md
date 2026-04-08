# Agentes de Documentação — Índice de Execução

Cada agente enriquece os arquivos `.md` de contexto de seu módulo com:
dores reais, regras de negócio (com legislação brasileira), entidades de dados,
fluxos de uso, casos extremos e critérios de aceite.

## Como usar

1. Abra o arquivo do agente desejado (links abaixo)
2. Copie o bloco de prompt
3. Inicie uma nova conversa e cole — o agente lê, enriquece e sobrescreve os arquivos via `Write`

## Ordem de execução

| Ordem | Arquivo | Módulos | Prioridade | Status |
|-------|---------|---------|------------|--------|
| 1° | [A1 — Core + Imóveis](_agentes/A1-core-imoveis.md) | `core/` + `imoveis/` | 🔴 Alta | Pendente |
| 2° | [A2 — Agrícola](_agentes/A2-agricola.md) | `agricola/` | 🔴 Alta | Pendente |
| 3° (paralelo) | [A3 — Pecuária](_agentes/A3-pecuaria.md) | `pecuaria/` | 🟡 Média | Pendente |
| 3° (paralelo) | [A4 — Financeiro + Contabilidade](_agentes/A4-financeiro-contabilidade.md) | `financeiro/` + `contabilidade/` | 🟡 Média | Pendente |
| 4° (paralelo) | [A5 — Estoque + Frota](_agentes/A5-estoque-frota.md) | `estoque/` + `frota/` | 🟢 Normal | Pendente |
| 4° (paralelo) | [A6 — Pessoas + Compliance](_agentes/A6-pessoas-compliance.md) | `pessoas/` + `compliance/` | 🟢 Normal | Pendente |
| 4° (paralelo) | [A7 — Rastreabilidade + Comercialização](_agentes/A7-rastreabilidade-comercializacao.md) | `rastreabilidade/` + `comercializacao/` | 🟢 Normal | Pendente |

## Regras para os agentes

- Preservar o frontmatter YAML de cada arquivo
- Reescrever TODO o conteúdo abaixo do frontmatter
- Usar `Write` (não `Edit`) para sobrescrever — os arquivos já existem
- Conteúdo deve ser específico para o **agronegócio brasileiro** — citar normas, culturas, regiões
- Cada seção com mínimo de qualidade: Descrição Funcional, Personas (≥3), Dores (≥4 concretas),
  Regras de Negócio (≥6 numeradas), Entidades (tabela com tipos), Integrações, Fluxo (6-10 passos),
  Casos Extremos (≥5), Critérios de Aceite (≥8 checkboxes), Sugestões Futuras (≥4)

## Atualizar status

Quando um agente concluir, atualize a coluna Status nesta tabela:
- `Pendente` → `✅ Concluído` ou `🔄 Em andamento`
