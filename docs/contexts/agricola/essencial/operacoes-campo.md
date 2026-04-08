---
modulo: "Agrícola"
submodulo: "Operações de Campo"
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

# Operações de Campo

## Descrição Funcional

O submódulo de Operações de Campo registra todas as atividades executadas nos talhões durante uma safra. Cada operação possui tipo (plantio, pulverização, adubação, colheita, preparo de solo, irrigação, etc.), data de execução, talhão/safra associados, insumos utilizados, maquinário empregado, mão de obra e custo.

Este é o submódulo com maior volume de dados no sistema — um produtor médio de soja no MT registra 40-60 operações por safra (preparo de solo, plantio, 4-6 pulverizações, adubações de cobertura, colheita). Ele alimenta diretamente os submódulos de custos, caderno de campo, rastreabilidade e financeiro.

### Contexto Brasileiro

As operações de campo no Brasil seguem o calendário agrícola regional:

#### Soja (Cerrado - MT/GO/BA)
1. **Preparo de solo** (ago-set): Aração, gradagem, correção de solo (calcário)
2. **Adubação de base** (set-out): Aplicação de NPK antes do plantio
3. **Plantio** (out-dez): Semeadura com tratamento de sementes
4. **Pulverização pós-plantio** (DAP 0-5): Herbicida em pré-emergência
5. **Pulverizações em pós-emergência** (DAP 15-60): Fungicidas, inseticidas, herbicidas
6. **Colheita** (jan-mar): Colheita de grãos com regulagem de umidade

#### Milho Safrinha (MT/GO)
1. **Plantio** (jan-fev): Imediatamente após colheita da soja (janela crítica)
2. **Pulverizações** (DAP 20-70): Controle de lagartas (Spodoptera, Helicoverpa)
3. **Colheita** (mai-jul): Colheita com secagem artificial se necessário

Funcionalidades principais:
- CRUD de operações com tipagem por fase da safra (pré-plantio, plantio, tratos culturais, colheita, pós-colheita)
- Registro de insumos consumidos por operação (agrotóxicos, fertilizantes, sementes) com lote e dosagem
- Registro de maquinário (trator, pulverizador, colheitadeira) com horas/ha
- Cálculo automático de custo da operação (insumos + maquinário + mão de obra)
- Vinculação a receituários agronômicos (para defensivos - Lei 7.802/89)
- Apontamentos de campo com foto e geolocalização
- Listagem com filtros por tipo, período, talhão, safra

## Personas — Quem usa este submódulo

- **Operador de Campo (MT/GO)**: Registra operações realizadas diretamente no celular, com fotos e coordenadas. Muitas vezes em áreas sem cobertura de internet (modo offline essencial).

- **Gerente de Fazenda (MATOPIBA)**: Aprova operações, monitora execução vs planejado, controla gastos de insumos que representam 70% do custo.

- **Agrônomo (Cooperativa - PR/RS)**: Prescreve operações (pulverização com receituário), valida dosagens conforme bula e recomendação técnica.

- **Administrador Financeiro**: Consulta custos de operações para conciliação financeira e cálculo de custo de produção para venda de sacas.

## Dores que resolve

1. **Registro tardio**: Operações anotadas no papel dias depois, com dados imprecisos. Comum em regiões remotas do MATOPIBA onde operador fica dias no campo.

2. **Rastreabilidade de insumos**: Impossível saber qual lote de defensivo foi aplicado em qual talhão. Crítico para recall de produtos e compliance com MAPA.

3. **Controle de custo real**: Sem registro de insumos e horas-máquina, custo por hectare é estimativa grosseira. Produtor de soja não sabe se está tendo lucro por talhão.

4. **Compliance ambiental**: Sem caderno de campo digital, produtor não consegue comprovar boas práticas para auditorias do IBAMA ou certificações.

5. **Duplicidade**: Mesma operação registrada por pessoas diferentes sem sistema centralizado. Comum em grandes propriedades com múltiplas equipes.

6. **Receituário agronômico**: Lei 7.802/89 exige receituário para aplicação de defensivos. Sistema vincula operação ao receituário para fiscalização.

## Regras de Negócio

1. Toda operação pertence a exatamente uma safra e um talhão (tenant isolation obrigatório)
2. O tipo de operação deve ser compatível com a fase atual da safra (warning para inconsistências)
3. **Receituário agronômico**: Operações de pulverização exigem: produto, dosagem (L/ha ou kg/ha), volume de calda, e obrigatoriamente número do receituário agronômico (Lei 7.802/89)
4. A data de execução não pode ser futura (exceto agendamentos no plano Profissional)
5. Insumos consumidos na operação devem dar baixa no estoque automaticamente (se módulo estoque ativo)
6. O custo da operação é calculado: `custo_insumos + (horas_maquina * custo_hora) + custo_mao_obra`
7. Operações de colheita geram romaneios automaticamente ou são vinculadas a romaneios existentes
8. Não é permitido editar operações de safras encerradas sem permissão de administrador
9. Operações podem ter status: `planejada`, `em_execucao`, `concluida`, `cancelada`
10. Ao criar uma despesa vinculada à operação, o webhook `operacao_despesa_webhook` é disparado para sincronizar o financeiro
11. **Carência de defensivos**: Sistema alerta se operação de colheita está dentro do período de carência do último defensivo aplicado
12. **Receituário vencido**: Alertar se receituário agronômico está fora do prazo de validade (máximo 1 ano)

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `Operacao` | id, tenant_id, safra_id, talhao_id, tipo_operacao_id, data_execucao, status, custo_total, observacoes, responsavel_id, receituario_id | pertence a Safra e Talhão |
| `OperacaoTipoFase` | id, tipo_operacao, fase_safra, descricao | enum de tipos por fase |
| `OperacaoInsumo` | id, operacao_id, produto_id, lote_id, quantidade, unidade, dosagem_ha, custo_unitario | insumos consumidos |
| `OperacaoMaquinario` | id, operacao_id, equipamento_id, horas, custo_hora | máquinas utilizadas |
| `Apontamento` | id, operacao_id, descricao, foto_url, latitude, longitude, data_hora | registro de campo |
| `ReceituarioAgronomico` | id, tenant_id, numero_registro, responsavel_tecnico, cret, data_emissao, data_validade, produtos (JSON) | receituário para defensivos |

## Integrações Necessárias

| Sistema/Modulo | Tipo | Descrição |
|----------------|------|-----------|
| `agricola/safras` | Leitura | Obtém safra e talhão para vincular operação |
| `operacional/estoque` | Escrita | Baixa automática de insumos consumidos |
| `operacional/frota` | Leitura | Obtém equipamentos e custo/hora |
| `financeiro/despesas` | Escrita | Gera lançamento de despesa via webhook |
| `agricola/custos` | Escrita | Alimenta custo por talhão/safra |
| `agricola/rastreabilidade` | Escrita | Registra lote de insumo aplicado por talhão |
| `agricola/romaneios` | Bidirecional | Operações de colheita vinculam a romaneios |
| `agricola/caderno-campo` | Escrita | Operação concluída gera entrada automática no caderno |

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa `/agricola/operacoes` ou entra via safra específica (`/agricola/safras/[id]/operacoes`)
2. Clica em "Nova Operação" e seleciona o tipo (ex: pulverização)
3. Seleciona safra e talhão (ou múltiplos talhões para operação em lote)
4. Preenche data de execução, responsável e observações
5. **Para pulverização**: Informa número do receituário agronômico (obrigatório por lei)
6. Adiciona insumos: seleciona produto, lote, quantidade e dosagem por hectare
7. Sistema valida dosagem conforme bula do produto (registro MAPA)
8. Adiciona maquinário: seleciona equipamento e horas trabalhadas
9. Sistema calcula custo total automaticamente
10. Usuário salva a operação com status `concluida`
11. Sistema dá baixa no estoque dos insumos consumidos
12. Sistema gera lançamento de despesa no módulo financeiro
13. Operação aparece no timeline da safra e no caderno de campo
14. **Validação de carência**: Sistema verifica período de carência e alerta se necessário

## Casos Extremos e Exceções

- **Operação em múltiplos talhões**: Uma pulverização pode cobrir 5 talhões — o sistema deve criar operações individuais por talhão ou uma operação com vínculo múltiplo, rateando insumos por área

- **Estoque insuficiente**: Se o insumo não tem saldo suficiente, a operação deve ser registrada com alerta (não bloquear) — o estoque pode ser regularizado depois

- **Lote de insumo vencido**: Alertar o usuário mas permitir registro (para auditorias de compliance o alerta fica registrado). Comum em propriedades grandes com controle precário de validade.

- **Operação retroativa**: Produtor registrando operação de 15 dias atrás — permitir com flag `registro_retroativo = true` e justificar motivo (ex: falta de internet no campo)

- **Cancelamento após baixa**: Se uma operação é cancelada após dar baixa no estoque, o estorno deve ser automático

- **Operação sem custo**: Trabalho manual sem insumo nem máquina — custo zero é válido (comum em pequenas propriedades)

- **Clima**: Operação cancelada por chuva após início — permitir status parcial com área efetiva menor que planejada

- **Deriva de defensivo**: Operação de pulverização com vento acima do recomendado (>10 km/h) — alertar sobre risco de deriva

- **Receituário ausente**: Pulverização sem receituário — bloquear e exigir regularização (fiscalização MAPA aplica multa)

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de operações com todos os tipos suportados
- [ ] Registro de insumos com lote, dosagem e cálculo de custo
- [ ] Registro de maquinário com horas e custo/hora
- [ ] Cálculo automático de custo total da operação
- [ ] Baixa automática no estoque ao concluir operação
- [ ] Webhook de despesa disparado ao registrar custo
- [ ] Filtros por tipo, safra, talhão, período e status
- [ ] Apontamentos com foto e geolocalização funcionando no mobile
- [ ] Tenant isolation testado em todas as rotas
- [ ] Permissões RBAC: `agricola:operacoes:create/read/update/delete`
- [ ] Validação de fase da safra vs tipo de operação (warning)
- [ ] Validação de receituário agronômico para pulverizações
- [ ] Validação de dosagem conforme bula (registro MAPA)
- [ ] Alerta de período de carência para colheita

## Sugestões de Melhoria Futura

1. **Operações em lote**: Selecionar múltiplos talhões e registrar uma única operação com rateio automático

2. **Agendamento**: Criar operações futuras com lembretes (requer plano Profissional)

3. **Reconhecimento de voz**: Operador dita a operação no campo e o sistema transcreve (útil para mãos ocupadas)

4. **Integração com telemetria**: Importar dados de máquinas automaticamente (horas, área coberta, velocidade) via satélite (Trimble, John Deere Operations Center)

5. **Aprovação em dois níveis**: Operador registra, agrônomo valida, gerente aprova

6. **Receituário digital**: Gerar PDF do receituário agronômico diretamente no sistema com assinatura do RT

7. **Modo offline**: Registrar operações sem internet e sincronizar quando houver conexão (crítico para MATOPIBA)

8. **Integração com previsão climática**: Alertar sobre condições inadequadas (vento, chuva) antes de iniciar pulverização

9. **Checklist de segurança**: Checklist obrigatório antes de aplicar defensivos (EPIs, condições climáticas, etc.)

10. **Rastreabilidade de aplicação**: Mapa de aplicação com sobreposição de passes para evitar falhas ou sobreposição
