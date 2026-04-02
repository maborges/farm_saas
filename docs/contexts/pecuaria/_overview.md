---
modulo: Pecuária
submodulo: Overview
nivel: essencial
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos: []
standalone: true
complexidade: M
assinante_alvo:
  - pecuarista
  - gestor-rural
  - veterinario
---

# Pecuária — Visão Geral do Módulo

## Descrição Funcional

O módulo Pecuária é o pilar central para gestão de rebanhos bovinos, abrangendo desde o cadastro básico de animais e lotes até funcionalidades avançadas como rastreabilidade SISBOV, gestão de confinamento e melhoramento genético. Organizado em três níveis (Essencial, Profissional e Enterprise), permite que fazendas de qualquer porte adotem gradualmente ferramentas mais sofisticadas conforme suas necessidades.

O nível Essencial cobre cadastro de rebanho, manejos básicos (pesagem, vacinação, movimentação) e controle de piquetes/pastagens. O Profissional adiciona reprodução assistida (IATF, monta), protocolos sanitários completos e gestão nutricional com custo por arroba. O Enterprise entrega rastreabilidade SISBOV com GTA digital, gestão completa de confinamento e ferramentas de genética/melhoramento com DEPs e genealogia.

## Personas — Quem usa este submódulo

- **Pecuarista / Proprietário:** visão geral do rebanho, indicadores de desempenho, custos
- **Gerente de Fazenda:** planejamento de manejos, movimentações, compras e vendas
- **Vaqueiro / Peão:** registro diário de manejos, movimentações de piquete
- **Veterinário:** protocolos sanitários, reprodução, diagnósticos
- **Nutricionista Animal:** formulação de dietas, controle de suplementação
- **Zootecnista:** melhoramento genético, DEPs, seleção

## Dores que resolve

- Falta de controle individual ou por lote dos animais
- Perda de dados de manejos realizados em caderno ou planilha
- Dificuldade para emitir GTA e cumprir exigências do SISBOV
- Ausência de indicadores zootécnicos (GMD, taxa de prenhez, mortalidade)
- Custo por arroba desconhecido, impossibilitando decisão de venda

## Regras de Negócio

1. Todo animal pertence a exatamente um lote e um tenant
2. Movimentações entre piquetes geram registro histórico imutável
3. Pesagens devem registrar peso e condição corporal; GMD calculado automaticamente
4. Vacinações exigem registro de lote da vacina para rastreabilidade
5. Animais com SISBOV ativo não podem ser excluídos, apenas abatidos/transferidos

## Entidades de Dados Principais

- `Animal` — identificação individual (brinco, SISBOV, raça, sexo, nascimento)
- `Lote` — agrupamento lógico de animais
- `Piquete` — unidade de pastagem com capacidade e tipo de pasto
- `Manejo` — registro polimórfico (pesagem, sanitário, reprodutivo, nutricional)
- `Movimentacao` — transferência de animais entre piquetes/fazendas
- `ProtocoloSanitario` — calendário vacinal e vermifugação
- `ProtocoloReproducao` — IATF, monta natural, diagnóstico gestação
- `Dieta` — composição nutricional e custo
- `Genealogia` — árvore genealógica com DEPs

## Integrações Necessárias

- **Core:** Autenticação, Tenants, Fazendas (obrigatório)
- **Estoque:** Consumo de insumos (vacinas, ração, sal mineral)
- **Financeiro:** Custo por animal/lote, receita de vendas
- **Fiscal:** GTA digital, notas de compra/venda de gado

## Fluxo de Uso Principal (step-by-step)

1. Cadastrar piquetes e definir capacidade de lotação
2. Criar lotes e cadastrar animais (individual ou importação em massa)
3. Alocar animais nos piquetes
4. Registrar manejos diários (pesagem, vacinação, movimentação)
5. Acompanhar indicadores no dashboard (GMD, lotação, mortalidade)
6. Planejar e executar protocolos reprodutivos e sanitários
7. Gerar relatórios e tomar decisões de venda/descarte

## Casos Extremos e Exceções

- Animal sem brinco: permitir cadastro temporário com identificação provisória
- Piquete superlotado: alerta ao ultrapassar capacidade, mas não bloqueia
- Morte de animal: registro obrigatório com causa; baixa automática do rebanho
- Transferência entre fazendas do mesmo tenant: GTA interna simplificada
- Importação CSV com dados duplicados: detecção e relatório de conflitos

## Critérios de Aceite (Definition of Done)

- [ ] Todos os endpoints protegidos por tenant_id via BaseService
- [ ] CRUD completo para Animal, Lote, Piquete, Manejo
- [ ] Testes de isolamento multi-tenant para cada entidade
- [ ] Dashboard com indicadores zootécnicos básicos
- [ ] Importação/exportação CSV funcional
- [ ] Documentação de API atualizada no Swagger

## Sugestões de Melhoria Futura

- Integração com balanças eletrônicas via IoT
- App mobile offline-first para registro de manejos no campo
- Integração com marketplaces de gado (Boi na Linha, etc.)
- Predição de ganho de peso com machine learning
- Dashboard comparativo entre fazendas do mesmo grupo
