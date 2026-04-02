---
modulo: "Agr\xEDcola"
submodulo: Rastreabilidade de Campo
nivel: enterprise
core: false
dependencias_core:
  - core/auth
  - core/cadastros/fazendas
  - core/cadastros/produtos
  - core/tenant
dependencias_modulos:
  - ../essencial/safras.md
  - ../essencial/operacoes-campo.md
  - ../essencial/caderno-campo.md
  - ../../operacional/estoque.md
standalone: false
complexidade: XL
assinante_alvo:
  - grande-produtor
  - cooperativa
  - exportador
  - agroindústria
---

# Rastreabilidade de Campo

## Descricao Funcional

O submodulo de Rastreabilidade de Campo implementa rastreabilidade completa "campo a mesa" — desde os lotes de insumos aplicados ate os lotes de produto colhido. Ele conecta cada saca ou tonelada colhida aos insumos utilizados (lote do defensivo, lote do fertilizante, lote da semente), operacoes realizadas, talhao de origem e responsaveis.

Este e um requisito critico para exportacao, certificacoes internacionais e compliance com legislacao de seguranca alimentar (EU Regulation 178/2002, FSMA dos EUA).

O sistema utiliza rastreamento FIFO (First In, First Out) de lotes de insumos no estoque, garantindo que o lote mais antigo seja o primeiro registrado nas operacoes.

Funcionalidades principais:
- Arvore de rastreabilidade: dado um lote de colheita, visualizar todos os insumos, operacoes e talhoes envolvidos
- Rastreabilidade reversa: dado um lote de insumo, visualizar em quais talhoes/safras foi aplicado
- Numero de lote de fornecedor (numero_lote_fornecedor) rastreado desde o recebimento
- Romaneios de colheita com numero de lote gerado automaticamente
- Devolucao de insumos com estorno no rastreamento (P0.3)
- Relatorio de rastreabilidade exportavel (PDF/JSON) para auditorias
- QR Code por lote de colheita vinculando a arvore completa

## Personas — Quem usa este submodulo

- **Responsavel de Qualidade:** gera relatorios de rastreabilidade para auditorias e certificacoes
- **Exportador:** precisa comprovar rastreabilidade para acessar mercados internacionais
- **Auditor/Certificador:** consulta a arvore de rastreabilidade durante auditoria
- **Gerente de Fazenda:** precisa saber rapidamente quais talhoes receberam um insumo com recall
- **Consumidor Final:** escaneia QR Code do produto e ve a origem

## Dores que resolve

1. **Recall impossivel:** sem rastreabilidade, um recall de insumo contamina toda a producao — com rastreabilidade, afeta apenas lotes especificos
2. **Barreira a exportacao:** mercados exigem rastreabilidade certificada — sem ela, o produtor perde acesso
3. **Certificacao negada:** auditorias reprovam por falta de documentacao de rastreabilidade
4. **Tempo de resposta:** levantar rastreabilidade manualmente leva dias — no sistema, leva segundos
5. **Fraude de origem:** sem rastreabilidade, e possivel misturar producao de origens diferentes

## Regras de Negocio

1. Todo lote de insumo recebido deve ter `numero_lote_fornecedor` registrado na entrada
2. A baixa de insumos em operacoes segue FIFO obrigatoriamente (lote mais antigo primeiro)
3. Cada operacao registra: produto_id, lote_id, quantidade, data_validade do lote
4. Cada romaneio de colheita gera um lote de producao com numero unico (formato: `{safra}-{talhao}-{seq}`)
5. A devolucao de insumos (P0.3) deve estornar o vinculo de rastreabilidade automaticamente
6. A arvore de rastreabilidade deve ser imutavel — entradas corretivas adicionam registros, nao editam existentes
7. Lotes de producao podem ser fracionados ou agrupados no beneficiamento — o vinculo de rastreabilidade se propaga
8. O sistema deve permitir rastreamento em ambas as direcoes: forward (insumo → colheita) e backward (colheita → insumos)
9. Dados de rastreabilidade devem ser retidos por no minimo 5 anos (configuravel por tenant)
10. Permissoes: `agricola:rastreabilidade:read`, `agricola:rastreabilidade:export`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `LoteInsumo` | id, tenant_id, produto_id, numero_lote_fornecedor, data_entrada, data_validade, quantidade_inicial, quantidade_atual, custo_unitario | pertence a Produto |
| `RastreioInsumoOperacao` | id, lote_insumo_id, operacao_id, quantidade_consumida, data_consumo | vincula lote a operacao |
| `LoteProducao` | id, tenant_id, safra_id, talhao_id, romaneio_id, numero_lote, data_colheita, quantidade_kg, qualidade_grade | lote colhido |
| `RastreioProducaoInsumo` | view: lote_producao → operacoes → lotes_insumo | arvore de rastreabilidade |
| `DevolucaoInsumo` | id, lote_insumo_id, quantidade, motivo, data_devolucao, operacao_estorno_id | estorno de rastreio |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `operacional/estoque` | Bidirecional | Lotes de insumo, FIFO, baixas e devolucoes |
| `agricola/operacoes` | Leitura | Insumos consumidos por operacao com lote |
| `agricola/safras` | Leitura | Safra e talhao de origem |
| `agricola/romaneios` | Bidirecional | Romaneios geram lotes de producao |
| `agricola/beneficiamento` | Bidirecional | Lotes de producao entram no beneficiamento e saem como lotes beneficiados |
| `core/cadastros/produtos` | Leitura | Catalogo de insumos e produtos |

## Fluxo de Uso Principal (step-by-step)

1. Fornecedor entrega insumo — almoxarife registra recebimento com `numero_lote_fornecedor` e data de validade
2. Sistema cria `LoteInsumo` no estoque com controle FIFO
3. Operador registra operacao de pulverizacao — sistema seleciona lote mais antigo (FIFO) para baixa
4. `RastreioInsumoOperacao` e criado vinculando lote ao talhao/safra via operacao
5. Na colheita, operador registra romaneio com peso, talhao e data
6. Sistema gera `LoteProducao` com numero unico e vincula ao talhao/safra
7. A arvore de rastreabilidade e construida: LoteProducao ← Operacoes ← LotesInsumo
8. Usuario acessa `/agricola/rastreabilidade` e pesquisa por lote de producao
9. Sistema exibe arvore visual com todos os insumos, operacoes, datas e responsaveis
10. Usuario exporta relatorio PDF/JSON para auditoria
11. Opcionalmente, gera QR Code que redireciona para a arvore publica (dados anonimizados)

## Casos Extremos e Excecoes

- **Lote de insumo usado em multiplas safras:** um big bag de fertilizante pode durar duas safras — o rastreamento acompanha fracao consumida em cada safra
- **Devolucao parcial:** 50% do insumo e devolvido — estornar apenas a fracao devolvida no rastreamento
- **Recall de insumo:** fornecedor informa recall de lote — sistema deve identificar rapidamente todos os talhoes/safras/lotes de producao afetados
- **Mistura de lotes na colheita:** colheitadeira colhe dois talhoes e despeja no mesmo caminhao — o lote de producao deve ser vinculado a ambos os talhoes com percentual estimado
- **Beneficiamento agrupa lotes:** na secagem, lotes de talhoes diferentes sao misturados — rastreabilidade deve propagar todos os vinculos de origem
- **Lote sem numero do fornecedor:** insumo comprado informalmente — permitir registro com flag `sem_rastreio_fornecedor` e alerta de compliance
- **Retencao de dados:** apos 5 anos, dados podem ser arquivados mas nao deletados (compliance)

## Criterios de Aceite (Definition of Done)

- [ ] Registro de `numero_lote_fornecedor` obrigatorio na entrada de insumos
- [ ] Baixa FIFO automatica ao consumir insumos em operacoes
- [ ] Geracao automatica de lote de producao em romaneios de colheita
- [ ] Arvore de rastreabilidade forward e backward funcional
- [ ] Devolucao de insumos com estorno automatico no rastreamento
- [ ] Exportacao de relatorio de rastreabilidade (PDF e JSON)
- [ ] Busca rapida por lote (insumo ou producao) com resultado em < 2 segundos
- [ ] Imutabilidade: registros de rastreamento nao podem ser editados, apenas complementados
- [ ] Tenant isolation rigoroso em todas as consultas
- [ ] 13/13 testes de integracao P0 passando

## Sugestoes de Melhoria Futura

1. **Blockchain:** registrar hashes de rastreabilidade em blockchain para imutabilidade verificavel
2. **API publica:** endpoint publico para consulta de rastreabilidade por QR Code (consumidor final)
3. **Integracao com SISBOV:** para rastreabilidade animal em fazendas mistas
4. **Alertas de recall automatico:** webhook do fornecedor dispara alerta no sistema
5. **Certificacao digital:** assinar relatorio de rastreabilidade com certificado ICP-Brasil
6. **Dashboard de compliance:** percentual de lotes com rastreabilidade completa vs incompleta
7. **Integracao EDI:** troca automatica de dados de rastreabilidade com cooperativas e tradings
