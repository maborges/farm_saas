---
modulo: Pessoas e RH
descricao: Gestão de colaboradores, jornada, segurança do trabalho e recursos humanos da fazenda
niveis:
  essencial:
    - cadastro-colaboradores
    - controle-presenca
    - epi-seguranca
  profissional:
    - folha-simplificada
    - treinamentos
    - escalas-tarefas
  enterprise:
    - esocial-rural
    - indicadores-rh
    - terceirizados
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../financeiro/_overview.md
---

# Pessoas e RH

## Visão Geral

O módulo de Pessoas e RH gerencia todo o ciclo de vida dos colaboradores da fazenda, desde o cadastro e controle de presença até a integração com o eSocial e indicadores avançados de RH. Contempla as particularidades do trabalho rural: sazonalidade, NRs específicas (NR-31), EPIs agrícolas, safristas e regime de trabalho rural.

## Público-Alvo

- **Essencial:** Pequenas propriedades com poucos funcionários que precisam de controle básico
- **Profissional:** Médias fazendas com equipe estruturada que precisam de folha e treinamentos
- **Enterprise:** Grandes operações com RH profissionalizado, obrigações trabalhistas complexas e terceirizados

## Estrutura de Tiers

### Essencial
Cadastro de colaboradores com dados pessoais e documentos, controle de presença (ponto manual) e gestão de EPIs e segurança do trabalho. Mínimo necessário para conformidade e organização.

### Profissional
Adiciona cálculo simplificado de folha de pagamento, gestão de treinamentos e certificações (NR-31), e escalas de trabalho com atribuição de tarefas. Para fazendas que querem profissionalizar a gestão de pessoas.

### Enterprise
Integração completa com eSocial rural, indicadores de RH (turnover, absenteísmo, custo per capita) e gestão de terceirizados e safristas. Para operações de grande porte com compliance trabalhista rigoroso.

## Integrações Principais

- **Módulo Financeiro:** custos com pessoal, folha de pagamento
- **Módulo Operacional:** alocação de mão de obra em atividades
- **Módulo Agrícola:** equipes de campo por talhão/operação
- **Externas:** eSocial, INSS, FGTS, sindicatos rurais
