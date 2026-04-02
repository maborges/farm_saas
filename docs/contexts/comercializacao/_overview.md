---
modulo: Comercialização
descricao: Gestão completa de vendas, contratos e operações comerciais da produção agropecuária
niveis:
  essencial:
    - registro-vendas
    - clientes-compradores
    - romaneios
  profissional:
    - contratos-venda
    - cotacoes-mercado
    - nfe-emissao
  enterprise:
    - cpr-cedulas
    - hedge-derivativos
    - exportacao
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../agricola/_overview.md
  - ../pecuaria/_overview.md
  - ../financeiro/_overview.md
  - ../operacional/_overview.md
---

# Comercialização

## Visão Geral

O módulo de Comercialização gerencia todo o ciclo de venda da produção agropecuária, desde o registro de vendas simples até operações sofisticadas de hedge em bolsa e exportação. Abrange grãos, leite, gado, e demais produtos da fazenda.

## Público-Alvo

- **Essencial:** Pequenos produtores que precisam registrar vendas e controlar entregas
- **Profissional:** Médios produtores que trabalham com contratos futuros e precisam de NF-e
- **Enterprise:** Grandes produtores e tradings que operam em bolsa e exportam

## Estrutura de Tiers

### Essencial
Funcionalidades básicas de registro de vendas, cadastro de compradores e controle de romaneios. Permite ao produtor ter visibilidade sobre o que vendeu, para quem e quanto entregou.

### Profissional
Adiciona contratos de venda futura com fixação de preço, consulta de cotações de mercado em tempo real (CBOT, ESALQ, B3) e emissão de NF-e do produtor rural. Essencial para quem precisa de gestão comercial mais estruturada.

### Enterprise
Operações avançadas como CPR (Cédula do Produtor Rural), hedge em bolsa de derivativos agrícolas e gestão completa de exportação com documentação internacional. Para operações de grande porte e tradings.

## Integrações Principais

- **Módulo Agrícola:** origem da produção (safras, talhões, colheita)
- **Módulo Pecuária:** origem de gado e leite
- **Módulo Financeiro:** receitas de vendas, contas a receber
- **Módulo Operacional:** estoque de produtos para venda
- **Externas:** SEFAZ (NF-e), B3/CBOT/ESALQ (cotações), SISCOMEX (exportação)
