---
modulo: Frota e Máquinas
tipo: overview
---

# Frota e Máquinas

Gestao completa de veiculos, maquinas agricolas e implementos, desde o cadastro basico ate telemetria avancada e indicadores de performance.

## Visao Geral dos Tiers

| Tier | Submodulo | Complexidade | Descricao |
|------|-----------|-------------|-----------|
| Essencial | Cadastro de Equipamentos | S | Registro de maquinas, veiculos e implementos |
| Essencial | Abastecimento | S | Controle de abastecimentos e consumo medio |
| Essencial | Checklist Diario | S | Checklist pre-operacao obrigatorio |
| Profissional | Manutencao Preventiva | M | Planos de manutencao, OS, historico |
| Profissional | Custo/Hora Maquina | M | Custo/hora, depreciacao, alocacao por talhao |
| Profissional | Documentacao | S | IPVA, seguro, licenciamento, vencimentos |
| Enterprise | Telemetria | XL | GPS tracking, horas trabalhadas, ociosidade |
| Enterprise | Oficina Interna | L | Gestao de oficina, pecas, mecanicos |
| Enterprise | Indicadores de Frota | L | MTBF, disponibilidade mecanica, TCO |

## Dependencias Core

- Identidade e Acesso (autenticacao, RBAC)
- Cadastro da Propriedade (fazendas, talhoes)

## Integracao com Outros Modulos

- **Agricola:** alocacao de maquinas por operacao/talhao
- **Financeiro:** lancamento automatico de custos de manutencao e abastecimento
- **Estoque:** consumo de pecas e insumos (oleo, filtros)
- **Operacional:** horímetro e odometro vinculados a operacoes

## Perfis de Assinante

- **Essencial:** pequeno produtor com frota reduzida (1-5 equipamentos)
- **Profissional:** medio produtor com frota diversificada e necessidade de controle de custos
- **Enterprise:** grande operacao com oficina propria, telemetria e KPIs avancados
