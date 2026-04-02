---
modulo: "Agr\xEDcola"
submodulo: "Opera\xE7\xF5es de Campo"
nivel: essencial
core: false
dependencias_core:
  - core/auth
  - core/cadastros/fazendas
  - core/cadastros/produtos
  - core/tenant
dependencias_modulos:
  - ../essencial/safras.md
  - ../../operacional/estoque.md
standalone: false
complexidade: L
assinante_alvo:
  - pequeno-produtor
  - medio-produtor
  - grande-produtor
  - cooperativa
---

# Operacoes de Campo

## Descricao Funcional

O submodulo de Operacoes de Campo registra todas as atividades executadas nos talhoes durante uma safra. Cada operacao possui tipo (plantio, pulverizacao, adubacao, colheita, preparo de solo, irrigacao, etc.), data de execucao, talhao/safra associados, insumos utilizados, maquinario empregado, mao de obra e custo.

Este e o submodulo com maior volume de dados no sistema — um produtor medio registra dezenas de operacoes por safra. Ele alimenta diretamente os submodulos de custos, caderno de campo, rastreabilidade e financeiro.

Funcionalidades principais:
- CRUD de operacoes com tipagem por fase da safra (pre-plantio, plantio, tratos culturais, colheita, pos-colheita)
- Registro de insumos consumidos por operacao (agrotoxicos, fertilizantes, sementes) com lote e dosagem
- Registro de maquinario (trator, pulverizador, colheitadeira) com horas/ha
- Calculo automatico de custo da operacao (insumos + maquinario + mao de obra)
- Vinculacao a receituarios agronomicos (para defensivos)
- Apontamentos de campo com foto e geolocalizacao
- Listagem com filtros por tipo, periodo, talhao, safra

## Personas — Quem usa este submodulo

- **Operador de Campo:** registra operacoes realizadas diretamente no celular, com fotos e coordenadas
- **Gerente de Fazenda:** aprova operacoes, monitora execucao vs planejado, controla gastos
- **Agronomo:** prescreve operacoes (pulverizacao com receituario), valida dosagens
- **Administrador Financeiro:** consulta custos de operacoes para conciliacao financeira

## Dores que resolve

1. **Registro tardio:** operacoes anotadas no papel dias depois, com dados imprecisos
2. **Rastreabilidade de insumos:** impossivel saber qual lote de defensivo foi aplicado em qual talhao
3. **Controle de custo real:** sem registro de insumos e horas-maquina, custo por hectare e estimativa grosseira
4. **Compliance ambiental:** sem caderno de campo digital, o produtor nao consegue comprovar boas praticas
5. **Duplicidade:** mesma operacao registrada por pessoas diferentes sem sistema centralizado

## Regras de Negocio

1. Toda operacao pertence a exatamente uma safra e um talhao (tenant isolation obrigatorio)
2. O tipo de operacao deve ser compativel com a fase atual da safra (warning para inconsistencias)
3. Operacoes de pulverizacao exigem: produto, dosagem (L/ha ou kg/ha), volume de calda, e opcionalmente numero do receituario agronomico
4. A data de execucao nao pode ser futura (exceto agendamentos no plano Profissional)
5. Insumos consumidos na operacao devem dar baixa no estoque automaticamente (se modulo estoque ativo)
6. O custo da operacao e calculado: `custo_insumos + (horas_maquina * custo_hora) + custo_mao_obra`
7. Operacoes de colheita geram romaneios automaticamente ou sao vinculadas a romaneios existentes
8. Nao e permitido editar operacoes de safras encerradas sem permissao de administrador
9. Operacoes podem ter status: `planejada`, `em_execucao`, `concluida`, `cancelada`
10. Ao criar uma despesa vinculada a operacao, o webhook `operacao_despesa_webhook` e disparado para sincronizar o financeiro

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `Operacao` | id, tenant_id, safra_id, talhao_id, tipo_operacao_id, data_execucao, status, custo_total, observacoes, responsavel_id | pertence a Safra e Talhao |
| `OperacaoTipoFase` | id, tipo_operacao, fase_safra, descricao | enum de tipos por fase |
| `OperacaoInsumo` | id, operacao_id, produto_id, lote_id, quantidade, unidade, dosagem_ha, custo_unitario | insumos consumidos |
| `OperacaoMaquinario` | id, operacao_id, equipamento_id, horas, custo_hora | maquinas utilizadas |
| `Apontamento` | id, operacao_id, descricao, foto_url, latitude, longitude, data_hora | registro de campo |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `agricola/safras` | Leitura | Obtem safra e talhao para vincular operacao |
| `operacional/estoque` | Escrita | Baixa automatica de insumos consumidos |
| `operacional/frota` | Leitura | Obtem equipamentos e custo/hora |
| `financeiro/despesas` | Escrita | Gera lancamento de despesa via webhook |
| `agricola/custos` | Escrita | Alimenta custo por talhao/safra |
| `agricola/rastreabilidade` | Escrita | Registra lote de insumo aplicado por talhao |
| `agricola/romaneios` | Bidirecional | Operacoes de colheita vinculam a romaneios |

## Fluxo de Uso Principal (step-by-step)

1. Usuario acessa `/agricola/operacoes` ou entra via safra especifica (`/agricola/safras/[id]/operacoes`)
2. Clica em "Nova Operacao" e seleciona o tipo (ex: pulverizacao)
3. Seleciona safra e talhao (ou multiplos talhoes para operacao em lote)
4. Preenche data de execucao, responsavel e observacoes
5. Adiciona insumos: seleciona produto, lote, quantidade e dosagem por hectare
6. Adiciona maquinario: seleciona equipamento e horas trabalhadas
7. Sistema calcula custo total automaticamente
8. Usuario salva a operacao com status `concluida`
9. Sistema da baixa no estoque dos insumos consumidos
10. Sistema gera lancamento de despesa no modulo financeiro
11. Operacao aparece no timeline da safra e no caderno de campo

## Casos Extremos e Excecoes

- **Operacao em multiplos talhoes:** uma pulverizacao pode cobrir 5 talhoes — o sistema deve criar operacoes individuais por talhao ou uma operacao com vinculo multiplo, rateando insumos por area
- **Estoque insuficiente:** se o insumo nao tem saldo suficiente, a operacao deve ser registrada com alerta (nao bloquear) — o estoque pode ser regularizado depois
- **Lote de insumo vencido:** alertar o usuario mas permitir registro (para auditorias de compliance o alerta fica registrado)
- **Operacao retroativa:** produtor registrando operacao de 15 dias atras — permitir com flag `registro_retroativo = true`
- **Cancelamento apos baixa:** se uma operacao e cancelada apos dar baixa no estoque, o estorno deve ser automatico
- **Operacao sem custo:** trabalho manual sem insumo nem maquina — custo zero e valido
- **Clima:** operacao cancelada por chuva apos inicio — permitir status parcial com area efetiva menor que planejada

## Criterios de Aceite (Definition of Done)

- [ ] CRUD completo de operacoes com todos os tipos suportados
- [ ] Registro de insumos com lote, dosagem e calculo de custo
- [ ] Registro de maquinario com horas e custo/hora
- [ ] Calculo automatico de custo total da operacao
- [ ] Baixa automatica no estoque ao concluir operacao
- [ ] Webhook de despesa disparado ao registrar custo
- [ ] Filtros por tipo, safra, talhao, periodo e status
- [ ] Apontamentos com foto e geolocalizacao funcionando no mobile
- [ ] Tenant isolation testado em todas as rotas
- [ ] Permissoes RBAC: `agricola:operacoes:create/read/update/delete`
- [ ] Validacao de fase da safra vs tipo de operacao (warning)

## Sugestoes de Melhoria Futura

1. **Operacoes em lote:** selecionar multiplos talhoes e registrar uma unica operacao com rateio automatico
2. **Agendamento:** criar operacoes futuras com lembretes (requer plano Profissional)
3. **Reconhecimento de voz:** operador dita a operacao no campo e o sistema transcreve
4. **Integracao com telemetria:** importar dados de maquinas automaticamente (horas, area coberta, velocidade)
5. **Aprovacao em dois niveis:** operador registra, agronomo valida, gerente aprova
6. **Receituario digital:** gerar PDF do receituario agronomico diretamente no sistema
7. **Modo offline:** registrar operacoes sem internet e sincronizar quando houver conexao
