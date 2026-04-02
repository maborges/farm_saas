---
modulo: Pecuária
submodulo: Sanidade
nivel: profissional
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-rebanho.md
  - ../essencial/manejos-basicos.md
standalone: false
complexidade: M
assinante_alvo:
  - pecuarista
  - veterinario
  - gestor-rural
---

# Sanidade

## Descrição Funcional

Submódulo de gestão sanitária com foco em protocolos vacinais estruturados, calendário sanitário anual, controle de vermifugação e tratamentos curativos. Diferencia-se dos manejos básicos ao oferecer protocolos pré-configurados (ex.: calendário de febre aftosa, brucelose, raiva), controle de carência de medicamentos e rastreabilidade completa de produtos aplicados para atender exigências de defesa sanitária animal.

Gera relatórios de cobertura vacinal e alertas de vacinações pendentes conforme o calendário.

## Personas — Quem usa este submódulo

- **Veterinário:** elaboração de protocolos, prescrição de tratamentos, atestados sanitários
- **Gerente de Fazenda:** acompanhamento do calendário e cobertura vacinal
- **Vaqueiro:** execução de aplicações conforme protocolo
- **Órgãos de defesa sanitária:** comprovação de vacinações obrigatórias

## Dores que resolve

- Vacinações obrigatórias perdidas gerando multas e bloqueio de GTA
- Falta de rastreabilidade de lotes de vacina aplicados
- Período de carência de medicamentos não controlado, gerando resíduo em carne
- Ausência de calendário sanitário automatizado
- Impossibilidade de gerar relatórios de cobertura vacinal por exigência legal

## Regras de Negócio

1. Protocolo sanitário define: vacina/medicamento, dose, via, idade alvo, periodicidade, obrigatoriedade
2. Calendário gerado automaticamente com base nos protocolos e no plantel atual
3. Vacinações obrigatórias (aftosa, brucelose) seguem calendário estadual configurável
4. Período de carência registrado por produto; animal em carência não pode ser vendido para abate
5. Cobertura vacinal = animais vacinados / animais elegíveis × 100
6. Tratamento curativo exige: diagnóstico, prescrição, produto, dose, duração, veterinário responsável
7. Histórico sanitário por animal inclui todas as aplicações e tratamentos
8. Alertas gerados 7 dias antes da data programada (configurável)

## Entidades de Dados Principais

- **ProtocoloSanitario:** id, tenant_id, nome, tipo (vacinacao|vermifugacao|tratamento), obrigatorio, periodicidade_meses, idade_min_meses, idade_max_meses, produto_id
- **CalendarioSanitario:** id, tenant_id, fazenda_id, ano, protocolo_id, data_programada, status (pendente|executado|atrasado)
- **AplicacaoSanitaria:** id, tenant_id, animal_id, protocolo_id, produto, lote_produto, dose, via, data, aplicador_id, veterinario_responsavel_id
- **TratamentoCurativo:** id, tenant_id, animal_id, diagnostico, prescricao, data_inicio, data_fim, veterinario_id
- **CarenciaMedicamento:** id, produto_id, dias_carencia_carne, dias_carencia_leite

## Integrações Necessárias

- **Cadastro de Rebanho:** Animais como alvo dos protocolos sanitários
- **Estoque:** Baixa de vacinas e medicamentos, controle de lotes e validade
- **Rastreabilidade SISBOV (Enterprise):** Comprovação de vacinação para GTA
- **Financeiro (opcional):** Custo sanitário por animal/lote

## Fluxo de Uso Principal (step-by-step)

1. Acessar Pecuária > Sanidade > Protocolos
2. Criar ou importar protocolos sanitários (vacinações obrigatórias, vermifugação, etc.)
3. Sistema gera calendário sanitário anual automaticamente
4. Receber alertas de vacinações/tratamentos programados
5. Registrar aplicação com dados do produto e lote
6. Sistema baixa vacina do estoque e atualiza cobertura vacinal
7. Para tratamentos curativos: registrar diagnóstico e prescrição
8. Consultar relatórios de cobertura vacinal e histórico sanitário

## Casos Extremos e Exceções

- **Animal alérgico a produto:** Registrar contraindicação; bloquear aplicação com alerta
- **Lote de vacina vencido:** Bloquear aplicação; exigir troca de lote
- **Vacinação obrigatória atrasada:** Alerta crítico; bloquear emissão de GTA para animais não vacinados
- **Animal em período de carência vendido:** Alerta bloqueante para venda a frigorífico
- **Protocolo aplicado a animal fora da faixa etária:** Alerta mas permite com justificativa
- **Reação adversa à vacina:** Campo para registro de ocorrência vinculada à aplicação

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de Protocolo Sanitário com periodicidade e obrigatoriedade
- [ ] Geração automática de calendário sanitário anual
- [ ] Registro de aplicação com rastreabilidade de lote de produto
- [ ] Controle de período de carência por animal
- [ ] Relatório de cobertura vacinal por protocolo
- [ ] Alertas de vacinações pendentes e atrasadas
- [ ] Isolamento multi-tenant em todas as entidades
- [ ] Testes para regras de carência e cobertura vacinal

## Sugestões de Melhoria Futura

- Integração com IDARON/IAGRO para comprovação digital de vacinação
- Dashboard de saúde do rebanho com indicadores de morbidade e mortalidade
- Protocolos pré-configurados por região/estado
- Alertas de surtos sanitários na região via dados públicos
- Prescrição digital com assinatura eletrônica do veterinário
