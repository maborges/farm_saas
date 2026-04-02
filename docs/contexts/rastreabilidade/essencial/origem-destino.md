---
modulo: Rastreabilidade
submodulo: Origem e Destino
nivel: essencial
core: false
dependencias_core:
  - fazendas
  - talhoes
  - usuarios
dependencias_modulos:
  - ../essencial/lotes-producao.md
  - ../../agricola/safras/safras.md
  - ../../operacional/estoque/movimentacoes.md
complexidade: M
assinante_alvo:
  - produtor rural
  - cooperativas
  - agroindústrias
  - tradings
standalone: false
---

# Origem e Destino

## Descrição Funcional

Submódulo que rastreia o caminho completo de um lote de produção desde sua origem (talhão, safra, data de colheita) até seu destino final (comprador, cooperativa, indústria, exportação). Registra cada ponto de passagem — armazenamento, beneficiamento, transporte — criando uma linha do tempo geográfica e temporal do produto.

O rastreio origem-destino é o elo que conecta "onde foi produzido" a "para onde foi". Permite ao produtor responder instantaneamente perguntas como: "De qual talhão saiu o lote que foi para o cliente X?" ou "Para onde foram os lotes colhidos no talhão Y em março?".

## Personas — Quem usa este submódulo

- **Produtor rural:** Precisa saber para onde vendeu cada lote e conseguir comprovar a origem quando solicitado.
- **Setor comercial:** Registra o destino na expedição e consulta histórico de entregas por comprador.
- **Fiscal/auditor:** Rastreia um lote específico da prateleira até o campo em caso de recall ou fiscalização.
- **Comprador/cooperativa:** Solicita comprovação de origem para seus próprios programas de qualidade.

## Dores que resolve

- **"De onde veio esse lote?":** Pergunta frequente de compradores, fiscais e programas de certificação, hoje respondida com dificuldade.
- **Recall sem rastreio:** Em caso de contaminação ou problema de qualidade, sem rastreio de destino é impossível saber quais clientes receberam o lote afetado.
- **Perda de informação no transporte:** Dados de origem se perdem entre fazenda, armazém e comprador.
- **Duplicidade de registros:** Mesma informação registrada em planilhas do campo, da logística e do comercial, com divergências.
- **Exigência legal:** Normativas do MAPA exigem rastreabilidade mínima para diversos produtos (hortifrutis, leite, carnes).

## Regras de Negócio

1. **Origem obrigatória:** Todo lote deve ter ao menos uma origem registrada (talhão + safra). Lotes de terceiros registram origem como `fornecedor_externo` com dados do remetente.
2. **Destino no momento da expedição:** O registro de destino é obrigatório ao mudar o lote para status `expedido`.
3. **Pontos intermediários:** Armazéns, silos e unidades de beneficiamento são registrados como pontos intermediários na cadeia.
4. **Nota fiscal vinculada:** O registro de destino deve vincular número da nota fiscal de saída quando disponível.
5. **Rastreio reverso:** Dado um comprador, o sistema deve listar todos os lotes enviados. Dado um talhão, todos os destinos.
6. **Imutabilidade:** Registros de origem e destino não podem ser alterados após confirmação — apenas complementados com observações.
7. **Tenant isolation:** Toda consulta é filtrada por `tenant_id`.

## Entidades de Dados Principais

- **OrigemLote:** `id`, `tenant_id`, `lote_id`, `talhao_id`, `safra_id`, `data_colheita`, `coordenadas_gps`, `responsavel_colheita_id`, `observacoes`
- **DestinoLote:** `id`, `tenant_id`, `lote_id`, `tipo_destino` (comprador/cooperativa/industria/exportacao/interno), `destinatario_nome`, `destinatario_documento` (CNPJ/CPF), `endereco`, `nota_fiscal`, `data_expedicao`, `quantidade_kg`, `transportadora`, `placa_veiculo`, `observacoes`
- **PontoIntermediario:** `id`, `tenant_id`, `lote_id`, `tipo` (armazem/silo/beneficiamento/transbordo), `local_nome`, `data_entrada`, `data_saida`, `responsavel_id`, `observacoes`

## Integrações Necessárias

- **Lotes de Produção (este módulo):** Obter dados do lote e atualizar status na expedição.
- **core/fazendas:** Dados de talhão e fazenda de origem.
- **agricola/safras:** Informações da safra vinculada.
- **operacional/estoque:** Baixa de estoque na expedição.
- **financeiro/receitas:** Vincular venda/receita ao destino do lote.
- **Integração fiscal (futuro):** Emissão de NF-e com dados de rastreabilidade.

## Fluxo de Uso Principal (step-by-step)

1. Lote é criado (via colheita) — sistema registra automaticamente a **origem** (talhão, safra, data, responsável).
2. Lote passa por armazenamento — usuário registra **ponto intermediário** (armazém, silo).
3. Se houver beneficiamento, registra-se outro ponto intermediário com tipo `beneficiamento`.
4. Setor comercial fecha venda — acessa o lote e registra o **destino** (comprador, NF, transportadora).
5. Lote é marcado como `expedido` — registro de destino é confirmado e imutável.
6. Comprador ou fiscal pode consultar a cadeia completa: origem → intermediários → destino.
7. Em caso de recall, consulta reversa: a partir do destino, identificar todos os lotes e suas origens.

## Casos Extremos e Exceções

- **Lote fracionado para múltiplos destinos:** Cada fração gera um sublote com seu próprio registro de destino. O lote pai mantém referência a todos os destinos.
- **Lote mesclado:** A origem do lote mesclado é a combinação das origens dos lotes de entrada. Sistema mantém referência cruzada.
- **Destino desconhecido (venda a intermediário):** Registra-se o intermediário como destino. Se o destino final for conhecido depois, pode-se complementar.
- **Devolução:** Se um lote é devolvido, registra-se novo ponto intermediário com tipo `devolucao` e o lote volta ao status `fechado`.
- **Expedição sem nota fiscal:** Permitida com flag `nf_pendente`. Sistema gera alerta diário para pendências de NF.
- **Produto perecível com prazo:** Para produtos com validade, o sistema alerta se o lote está próximo do vencimento e ainda não foi expedido.

## Critérios de Aceite (Definition of Done)

- [ ] Registro automático de origem na criação do lote
- [ ] CRUD de destinos vinculados ao lote
- [ ] Registro de pontos intermediários (armazém, beneficiamento, transbordo)
- [ ] Consulta de cadeia completa: origem → intermediários → destino
- [ ] Consulta reversa: destino → lotes → origens
- [ ] Consulta reversa: talhão → lotes → destinos
- [ ] Imutabilidade de registros confirmados
- [ ] Vinculação de nota fiscal ao destino
- [ ] Teste de tenant isolation
- [ ] API com RBAC (`rastreabilidade:origem-destino:read`, `rastreabilidade:origem-destino:write`)
- [ ] Tela de timeline visual do lote (origem → destino)

## Sugestões de Melhoria Futura

- **Mapa interativo:** Visualizar a rota do lote no mapa (talhão → armazém → destino).
- **Integração com CTe:** Capturar dados de transporte automaticamente via CT-e.
- **Alerta de recall automático:** Ao identificar problema num lote, notificar automaticamente todos os destinos afetados.
- **Portal do comprador:** Área onde o comprador consulta a origem dos lotes recebidos sem precisar pedir ao produtor.
- **Rastreio em tempo real:** Integração com rastreadores veiculares para acompanhar lote em trânsito.
