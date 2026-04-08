---
modulo: "Agrícola"
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

## Descrição Funcional

O submódulo de Rastreabilidade de Campo implementa rastreabilidade completa "campo à mesa" — desde os lotes de insumos aplicados até os lotes de produto colhido. Ele conecta cada saca ou tonelada colhida aos insumos utilizados (lote do defensivo, lote do fertilizante, lote da semente), operações realizadas, talhão de origem e responsáveis.

Este é um requisito crítico para exportação, certificações internacionais e compliance com legislação de segurança alimentar (EU Regulation 178/2002, FSMA dos EUA).

O sistema utiliza rastreamento FIFO (First In, First Out) de lotes de insumos no estoque, garantindo que o lote mais antigo seja o primeiro registrado nas operações.

### Contexto Brasileiro para Exportação

#### Regulamentações Internacionais

**União Europeia — Due Diligence Regulation 2023/1115 (EUDR)**

Entrou em vigor em junho de 2023, com aplicação a partir de dezembro de 2024:

- **Requisito**: Comprovar que produtos (soja, café, cacau, carne bovina) não vêm de áreas desmatadas após 31/12/2020
- **Geolocalização**: Obrigatório fornecer coordenadas GPS de todos os talhões de origem
- **Due Diligence**: Importador deve avaliar risco de desmatamento na cadeia
- **Multas**: Até 4% do faturamento anual na UE ou € 40 milhões

O AgroSaaS fornece:
- Geolocalização precisa de cada talhão (polígono GPS)
- Histórico de uso do solo (comprovando ausência de desmatamento)
- Rastreabilidade completa do lote até o talhão de origem

**FDA Food Safety Modernization Act (FSMA) — EUA**

- **Requisito**: Rastreabilidade de alimentos para resposta rápida a recalls
- **Rule 204**: Lista de alimentos com rastreabilidade reforçada (frutas, vegetais)
- **Registro**: Manter registros de origem por 2 anos

**GlobalG.A.P. — Certificação para Europa**

- **Padrão**: Exigido por supermercados europeus (Alemanha, França, Holanda)
- **Rastreabilidade**: Lote deve ser rastreável até o talhão de origem
- **Caderno de campo**: Obratório com registros de aplicações de defensivos
- **Auditoria**: Anual, com amostragem de lotes para verificação

**Rainforest Alliance — Café, Cacau, Soja**

- **Sustentabilidade**: Comprovar práticas agrícolas sustentáveis
- **Rastreabilidade**: Massa balanceada ou segregada
- **Social**: Condições de trabalho, EPIs, treinamento

#### Legislação Brasileira

**Lei 7.802/89 (Lei dos Agrotóxicos)**

- Exige receituário agronômico para aplicação de defensivos
- Registro de aplicações no caderno de campo
- Período de carência deve ser respeitado

**IN 02/2008 MAPA**

- Institui o Caderno de Campo para rastreabilidade
- Registro de todas as operações culturais
- Identificação de responsáveis técnicos

**Programa de Análise de Resíduos de Agrotóxicos (PARA) — ANVISA**

- Coleta de amostras em mercados
- Se resíduo acima do limite, rastreia até o produtor
- Caderno de campo é exigido na investigação

**SISCOMEX — Exportação**

- Sistema Integrado de Comércio Exterior
- Registro de exportação com origem do produto
- Integração com rastreabilidade do AgroSaaS

Funcionalidades principais:
- Árvore de rastreabilidade: dado um lote de colheita, visualizar todos os insumos, operações e talhões envolvidos
- Rastreabilidade reversa: dado um lote de insumo, visualizar em quais talhões/safras foi aplicado
- Número de lote de fornecedor (numero_lote_fornecedor) rastreado desde o recebimento
- Romaneios de colheita com número de lote gerado automaticamente
- Devolução de insumos com estorno no rastreamento (P0.3)
- Relatório de rastreabilidade exportável (PDF/JSON) para auditorias
- QR Code por lote de colheita vinculando à árvore completa
- Geolocalização de talhões para EUDR (Due Diligence Regulation)
- Integração com SISCOMEX para exportação

## Personas — Quem usa este submódulo

- **Responsável de Qualidade (Exportador)**: Gera relatórios de rastreabilidade para auditorias e certificações. Precisa comprovar conformidade com EUDR, GlobalG.A.P., FDA.

- **Exportador de Soja/Café (MT/SP/MG)**: Vende para Europa/Ásia. Precisa fornecer rastreabilidade completa para importador e cumprir EUDR.

- **Auditor/Certificador**: Consulta a árvore de rastreabilidade durante auditoria. Verifica se lote de colheita está vinculado a insumos registrados e operações documentadas.

- **Gerente de Fazenda**: Precisa saber rapidamente quais talhões receberam um insumo com recall. Se fornecedor notifica problema com lote de defensivo, identifica áreas afetadas em segundos.

- **Consumidor Final (Europa/EUA)**: Escaneia QR Code no produto e vê a origem: fazenda, talhão, data de colheita, insumos utilizados.

- **Fiscal do MAPA/ANVISA**: Solicita rastreabilidade em fiscalizações ou investigações de resíduos.

## Dores que resolve

1. **Recall impossível**: Sem rastreabilidade, um recall de insumo contamina toda a produção — com rastreabilidade, afeta apenas lotes específicos. Ex: Defensivo com problema foi aplicado em 3 talhões → apenas colheita desses talhões é afetada.

2. **Barreira à exportação**: Mercados exigem rastreabilidade certificada — sem ela, o produtor perde acesso. Europa exige EUDR compliance a partir de 2024.

3. **Certificação negada**: Auditorias reprovam por falta de documentação de rastreabilidade. GlobalG.A.P. exige rastreabilidade completa.

4. **Tempo de resposta**: Levantar rastreabilidade manualmente leva dias — no sistema, leva segundos. Crítico para recall ou auditoria surpresa.

5. **Fraude de origem**: Sem rastreabilidade, é possível misturar produção de origens diferentes. Café do Cerrado Mineiro (IG) pode ser misturado com café de origem desconhecida.

6. **Multas por não conformidade**: EUDR prevê multas de até 4% do faturamento. Produtor que não consegue comprovar origem perde contrato.

7. **Investigação de resíduos**: ANVISA detecta resíduo acima do limite em mercado — sem rastreabilidade, investigação trava e produtor é penalizado.

## Regras de Negócio

1. Todo lote de insumo recebido deve ter `numero_lote_fornecedor` registrado na entrada
2. A baixa de insumos em operações segue FIFO obrigatoriamente (lote mais antigo primeiro)
3. Cada operação registra: produto_id, lote_id, quantidade, data_validade do lote
4. Cada romaneio de colheita gera um lote de produção com número único (formato: `{safra}-{talhao}-{seq}`)
5. A devolução de insumos (P0.3) deve estornar o vínculo de rastreabilidade automaticamente
6. A árvore de rastreabilidade deve ser imutável — entradas corretivas adicionam registros, não editam existentes
7. Lotes de produção podem ser fracionados ou agrupados no beneficiamento — o vínculo de rastreabilidade se propaga
8. O sistema deve permitir rastreamento em ambas as direções: forward (insumo → colheita) e backward (colheita → insumos)
9. Dados de rastreabilidade devem ser retidos por no mínimo 5 anos (configurável por tenant)
10. **Geolocalização EUDR**: Cada talhão deve ter polígono GPS cadastrado para exportação para UE
11. **Due Diligence**: Sistema gera declaração de ausência de desmatamento pós-2020 baseada em histórico de imagens de satélite
12. Permissões: `agricola:rastreabilidade:read`, `agricola:rastreabilidade:export`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `LoteInsumo` | id, tenant_id, produto_id, numero_lote_fornecedor, data_entrada, data_validade, quantidade_inicial, quantidade_atual, custo_unitario | pertence a Produto |
| `RastreioInsumoOperacao` | id, lote_insumo_id, operacao_id, quantidade_consumida, data_consumo | vincula lote à operação |
| `LoteProducao` | id, tenant_id, safra_id, talhao_id, romaneio_id, numero_lote, data_colheita, quantidade_kg, qualidade_grade | lote colhido |
| `RastreioProducaoInsumo` | view: lote_producao → operações → lotes_insumo | árvore de rastreabilidade |
| `DevoluicaoInsumo` | id, lote_insumo_id, quantidade, motivo, data_devolucao, operacao_estorno_id | estorno de rastreio |
| `TalhaoGeolocalizacao` | id, talhao_id, poligono_geojson, area_ha, data_cadastro | polígono GPS para EUDR |
| `DueDiligenceDeclaracao` | id, tenant_id, talhao_id, data_referencia, desmatamento_detectado, url_relatorio | declaração EUDR |

## Integrações Necessárias

| Sistema/Modulo | Tipo | Descrição |
|----------------|------|-----------|
| `operacional/estoque` | Bidirecional | Lotes de insumo, FIFO, baixas e devoluções |
| `agricola/operacoes` | Leitura | Insumos consumidos por operação com lote |
| `agricola/safras` | Leitura | Safra e talhão de origem |
| `agricola/romaneios` | Bidirecional | Romaneios geram lotes de produção |
| `agricola/beneficiamento` | Bidirecional | Lotes de produção entram no beneficiamento e saem como lotes beneficiados |
| `core/cadastros/produtos` | Leitura | Catálogo de insumos e produtos |
| `api/satelite` (Global Forest Watch, INPE) | Leitura | Verificar histórico de desmatamento por talhão |
| `siscomex` | Escrita | Exportar dados de rastreabilidade para SISCOMEX |

## Fluxo de Uso Principal (step-by-step)

1. Fornecedor entrega insumo — almoxarife registra recebimento com `numero_lote_fornecedor` e data de validade
2. Sistema cria `LoteInsumo` no estoque com controle FIFO
3. Operador registra operação de pulverização — sistema seleciona lote mais antigo (FIFO) para baixa
4. `RastreioInsumoOperacao` é criado vinculando lote ao talhão/safra via operação
5. Na colheita, operador registra romaneio com peso, talhão e data
6. Sistema gera `LoteProducao` com número único e vincula ao talhão/safra
7. A árvore de rastreabilidade é construída: LoteProducao ← Operações ← LotesInsumo
8. **Geolocalização EUDR**: Sistema associa coordenadas GPS do talhão ao lote de produção
9. **Due Diligence**: Sistema verifica histórico de imagens de satélite (2020-atual) para comprovar ausência de desmatamento
10. Usuário acessa `/agricola/rastreabilidade` e pesquisa por lote de produção
11. Sistema exibe árvore visual com todos os insumos, operações, datas e responsáveis
12. Usuário exporta relatório PDF/JSON para auditoria
13. Opcionalmente, gera QR Code que redireciona para a árvore pública (dados anonimizados)
14. **Exportação**: Sistema exporta dados para SISCOMEX com rastreabilidade completa

## Casos Extremos e Exceções

- **Lote de insumo usado em múltiplas safras**: Um big bag de fertilizante pode durar duas safras — o rastreamento acompanha fração consumida em cada safra

- **Devolução parcial**: 50% do insumo é devolvido — estornar apenas a fração devolvida no rastreamento

- **Recall de insumo**: Fornecedor informa recall de lote — sistema deve identificar rapidamente todos os talhões/safras/lotes de produção afetados

- **Mistura de lotes na colheita**: Colheitadeira colhe dois talhões e despeja no mesmo caminhão — o lote de produção deve ser vinculado a ambos os talhões com percentual estimado

- **Beneficiamento agrupa lotes**: Na secagem, lotes de talhões diferentes são misturados — rastreabilidade deve propagar todos os vínculos de origem

- **Lote sem número do fornecedor**: Insumo comprado informalmente — permitir registro com flag `sem_rastreio_fornecedor` e alerta de compliance

- **Retenção de dados**: Após 5 anos, dados podem ser arquivados mas não deletados (compliance)

- **Talhão sem geolocalização**: Exportação para UE exige GPS — bloquear exportação se talhão não tem polígono cadastrado

- **Desmatamento detectado**: Imagem de satélite mostra desmatamento pós-2020 — alertar que lote não é elegível para EUDR

- **QR Code público**: Consumidor escaneia QR Code — sistema deve mostrar apenas dados não sensíveis (fazenda, cultura, data), ocultando insumos específicos

## Critérios de Aceite (Definition of Done)

- [ ] Registro de `numero_lote_fornecedor` obrigatório na entrada de insumos
- [ ] Baixa FIFO automática ao consumir insumos em operações
- [ ] Geração automática de lote de produção em romaneios de colheita
- [ ] Árvore de rastreabilidade forward e backward funcional
- [ ] Devolução de insumos com estorno automático no rastreamento
- [ ] Exportação de relatório de rastreabilidade (PDF e JSON)
- [ ] Busca rápida por lote (insumo ou produção) com resultado em < 2 segundos
- [ ] Imutabilidade: registros de rastreamento não podem ser editados, apenas complementados
- [ ] Tenant isolation rigoroso em todas as consultas
- [ ] Geolocalização de talhões (polígono GPS) para EUDR
- [ ] Geração de declaração Due Diligence para exportação UE
- [ ] Integração com SISCOMEX para exportação
- [ ] QR Code por lote de produção
- [ ] 13/13 testes de integração P0 passando

## Sugestões de Melhoria Futura

1. **Blockchain**: Registrar hashes de rastreabilidade em blockchain para imutabilidade verificável

2. **API pública**: Endpoint público para consulta de rastreabilidade por QR Code (consumidor final)

3. **Integração com SISBOV**: Para rastreabilidade animal em fazendas mistas

4. **Alertas de recall automático**: Webhook do fornecedor dispara alerta no sistema

5. **Certificação digital**: Assinar relatório de rastreabilidade com certificado ICP-Brasil

6. **Dashboard de compliance**: Percentual de lotes com rastreabilidade completa vs incompleta

7. **Integração EDI**: Troca automática de dados de rastreabilidade com cooperativas e tradings

8. **Rastreabilidade de carbono**: Calcular pegada de carbono por lote baseado em insumos e operações

9. **Marketplace B2B**: Publicar lotes com rastreabilidade completa para compradores premium

10. **Integração com certificadoras**: API direta com GlobalG.A.P., Rainforest Alliance para auditoria remota

11. **Due Diligence automatizada**: Verificação automática de desmatamento via satélite (Global Forest Watch)

12. **Rastreabilidade por DNA**: Integração com laboratórios que fazem análise de DNA para comprovar origem (café especial)
