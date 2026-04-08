---
modulo: Contabilidade
submodulo: Multi-Empresa
nivel: enterprise
core: false
dependencias_core:
  - Identidade e Acesso
  - Configurações Globais
dependencias_modulos:
  - ../essencial/plano-contas-rural.md
  - ../essencial/lancamentos-contabeis.md
  - ../profissional/dre-rural.md
  - ../profissional/balancete.md
  - ../../financeiro/essencial/despesas.md
  - ../../financeiro/essencial/receitas.md
standalone: false
complexidade: XL
assinante_alvo:
  - Grupos Agrícolas
  - Holdings Rurais
  - Cooperativas
  - Escritórios de Contabilidade com múltiplos clientes rurais
---

# Multi-Empresa — Consolidação Contábil Multi-CNPJ

## Descrição Funcional

O submódulo Multi-Empresa permite a consolidação contábil de múltiplas empresas (CNPJs) e produtores rurais (CPFs) dentro de um mesmo grupo econômico. Suporta eliminações intercompany, conversão de planos de contas entre empresas, e geração de demonstrações financeiras consolidadas (DRE, Balanço Patrimonial, Balancete). Atende grupos agrícolas que operam com múltiplas fazendas sob diferentes entidades jurídicas.

## Personas

- **Diretor do Grupo Agrícola:** Precisa de visão consolidada do resultado de todas as empresas.
- **Controller:** Configura regras de consolidação, eliminações e ajustes intercompany.
- **Contador do Grupo:** Gera demonstrações consolidadas para auditoria e obrigações legais.
- **Escritório de Contabilidade:** Consolida dados de múltiplos clientes rurais.

## Dores que resolve

- Impossibilidade de ter visão unificada do resultado de múltiplas empresas do grupo.
- Duplicidade de receitas/despesas em transações intercompany distorcendo o resultado consolidado.
- Diferentes planos de contas entre empresas dificultando a consolidação.
- Processo manual de consolidação em planilha, demorado e sujeito a erros.
- Falta de rastreabilidade das eliminações intercompany.

## Regras de Negócio

1. **Grupo econômico:** Definir quais CNPJs/CPFs compõem o grupo para consolidação.
2. **Plano de contas consolidado:** Mapear contas de cada empresa para um plano de contas consolidado (De/Para por empresa).
3. **Eliminações intercompany:** Transações entre empresas do grupo devem ser identificadas e eliminadas automaticamente na consolidação (receitas x despesas, contas a receber x contas a pagar).
4. **Moeda única:** Todas as empresas devem ser consolidadas na mesma moeda (BRL).
5. **Período unificado:** A consolidação exige que todas as empresas tenham o mesmo período contábil fechado.
6. **Participação societária:** Consolidação proporcional quando a participação é inferior a 100%.
7. **Ajustes de consolidação:** Lançamentos de ajuste que existem apenas na consolidação (não afetam a contabilidade individual).
8. **Auditoria:** Todas as eliminações e ajustes devem ser rastreáveis e justificados.
9. **Histórico:** Manter histórico de consolidações por período para comparação.
10. **Segregação:** A contabilidade individual de cada empresa permanece independente.

## Entidades de Dados Principais

- `GrupoEconomico` — definição do grupo: nome, empresas participantes, participação societária.
- `EmpresaGrupo` — empresa membro: CNPJ/CPF, nome, participação percentual, plano de contas.
- `MapeamentoContasConsolidacao` — De/Para entre conta da empresa individual e conta consolidada.
- `EliminacaoIntercompany` — regra de eliminação: empresa origem, empresa destino, contas envolvidas, tipo.
- `ConsolidacaoContabil` — cabeçalho da consolidação: período, grupo, status, ajustes.
- `AjusteConsolidacao` — lançamento de ajuste exclusivo da consolidação.
- `DREConsolidado` — DRE do grupo após eliminações.
- `BalanceteConsolidado` — balancete do grupo após eliminações.

## Integrações Necessárias

- **Plano de Contas Rural (por empresa):** Cada empresa tem seu plano; necessário mapeamento para consolidação.
- **Lançamentos Contábeis (por empresa):** Dados individuais que alimentam a consolidação.
- **DRE Rural:** DRE individual de cada empresa para geração do DRE consolidado.
- **Balancete:** Balancete individual para geração do balancete consolidado.
- **Financeiro:** Identificação de transações intercompany para eliminação automática.
- **Identidade e Acesso:** Permissões específicas para acesso a dados multi-empresa.

## Fluxo de Uso Principal

1. **Configuração do grupo:** Cadastrar grupo econômico com empresas participantes e percentuais de participação.
2. **Mapeamento de contas:** Configurar De/Para entre plano de contas de cada empresa e o plano consolidado.
3. **Regras de eliminação:** Definir pares de contas intercompany para eliminação automática.
4. **Fechamento individual:** Garantir que todas as empresas tenham o período contábil fechado.
5. **Geração:** Executar consolidação para o período selecionado.
6. **Eliminações:** Sistema aplica eliminações intercompany automaticamente e apresenta relatório.
7. **Ajustes:** Controller insere ajustes de consolidação adicionais se necessário.
8. **Revisão:** Conferir balancete e DRE consolidados.
9. **Aprovação:** Consolidação aprovada fica disponível para relatórios e exportação.

## Casos Extremos e Exceções

- Empresa adquirida no meio do exercício — consolidar apenas a partir da data de aquisição.
- Empresa vendida/encerrada durante o exercício — consolidar até a data de saída.
- Participação societária indireta (empresa A controla B que controla C) — consolidação em cascata.
- Transações intercompany parcialmente registradas (uma empresa registrou, a outra não) — alertar divergência.
- Empresas com exercícios fiscais diferentes (ex.: uma encerra em dezembro, outra em março).
- Moedas diferentes em empresas com operações internacionais (raro mas possível em grupos de exportação).
- Mais de 20 empresas no grupo — performance da consolidação (processamento assíncrono).

## Critérios de Aceite

- [ ] Cadastro de grupo econômico com múltiplas empresas funcional.
- [ ] Mapeamento De/Para de contas entre cada empresa e o plano consolidado.
- [ ] Eliminações intercompany aplicadas automaticamente com relatório detalhado.
- [ ] DRE consolidado gerado com valores após eliminações.
- [ ] Balancete consolidado equilibrado (débitos = créditos).
- [ ] Ajustes de consolidação rastreáveis e justificados.
- [ ] Consolidação proporcional funcional para participações < 100%.
- [ ] Histórico de consolidações acessível para comparação.
- [ ] Performance aceitável com até 10 empresas no grupo.

## Sugestões de Melhoria Futura

- Consolidação em tempo real (não apenas mensal) para dashboards executivos.
- Detecção automática de transações intercompany via IA (matching inteligente).
- Consolidação estatutária e gerencial em paralelo (visões diferentes do mesmo grupo).
- Integração com sistemas de CVM para grupos de capital aberto no agronegócio.
- Portal do investidor com demonstrações consolidadas publicadas automaticamente.
