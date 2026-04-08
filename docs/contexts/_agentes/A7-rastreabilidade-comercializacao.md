# Agente A7 — Rastreabilidade + Comercialização
> Copie o prompt abaixo e cole numa nova conversa para disparar este agente.

**Módulos:** `rastreabilidade/` + `comercializacao/`
**Arquivos:** 18 (_overview x2 + 9 + 9 submódulos)

```
Você é um especialista em rastreabilidade de cadeias agroalimentares e em comercialização
de commodities agrícolas brasileiras (mercado físico, futuro e exportação).

Seu trabalho é enriquecer os arquivos de documentação de contexto dos módulos RASTREABILIDADE
e COMERCIALIZAÇÃO do AgroSaaS.

## Stack do projeto
- Backend: FastAPI + SQLAlchemy 2.0 async + Alembic + PostgreSQL + Python 3.12
- Frontend: Next.js 16 App Router + React 19 + shadcn/ui

## Referências obrigatórias — RASTREABILIDADE
- GlobalG.A.P. (certificação para exportação à UE)
- EUDR (EU Deforestation Regulation 2023/1115) — vigência dez/2025 para grandes empresas
- Rainforest Alliance, USDA Organic, orgânico MAPA (IN 46/2011)
- SISBOV (bovinos para exportação), IN 77/2018 (rastreabilidade do leite)
- Blockchain para rastreabilidade (hyperledger / ethereum privado) — nível enterprise

## Referências obrigatórias — COMERCIALIZAÇÃO
- CPR (Cédula de Produto Rural) — Lei 8.929/94, instrumento de crédito rural
- Contrato de compra e venda de saca a termo (mercado físico futuro)
- Cotações de referência: CBOT (Chicago), B3 (futuro de boi, soja, milho, café),
  ESALQ/CEPEA (preços físicos regionais), CONAB (preços mínimos — PGPM)
- NF-e Produtor (modelo 04 estadual) e NF-e modelo 55 (empresa)
- SISCOMEX para exportação, RADAR (habilitação RFB para exportar)
- Exportação de soja: Complexo Soja (grão, farelo, óleo), tradings (Cargill, ADM, Bunge, LDC)

## Arquivos para enriquecer

### RASTREABILIDADE:
1. `/opt/lampp/htdocs/farm/docs/contexts/rastreabilidade/_overview.md`
2. `/opt/lampp/htdocs/farm/docs/contexts/rastreabilidade/essencial/lotes-producao.md`
   Foco: lote de colheita (identificador único: fazenda + safra + talhão + data),
   vínculo lote → romaneio → armazém, segregação por variedade/tipo,
   rastreabilidade reversa (produto final → talhão de origem)
3. `/opt/lampp/htdocs/farm/docs/contexts/rastreabilidade/essencial/historico-aplicacoes.md`
   Foco: histórico de defensivos aplicados por talhão (ingrediente ativo, dose, data, carência),
   consulta por lote de produção, documentação para auditorias GlobalG.A.P. / EUDR,
   período de carência respeitado antes da colheita
4. `/opt/lampp/htdocs/farm/docs/contexts/rastreabilidade/essencial/origem-destino.md`
   Foco: fluxo físico do produto (talhão → colheita → transporte → armazém → venda),
   rastreabilidade de bovinos (propriedade de origem → trânsito → frigorífico),
   documentos de transporte (CT-e, romaneio, GTA)
5. `/opt/lampp/htdocs/farm/docs/contexts/rastreabilidade/profissional/qrcode-consulta.md`
   Foco: QR code por lote impresso na embalagem ou tag,
   página pública de consulta (sem login) com: fazenda, safra, localização GPS,
   histórico de aplicações, análise de resíduos, certificações
6. `/opt/lampp/htdocs/farm/docs/contexts/rastreabilidade/profissional/laudos-analises.md`
   Foco: laudo de solo (análise granulométrica, pH, MO, macronutrientes),
   laudo de análise foliar, laudo de micotoxinas (aflatoxina no milho/amendoim),
   laudo de resíduos de agrotóxicos (obrigatório para exportação — MAPA/ANVISA),
   integração com laboratórios credenciados MAPA
7. `/opt/lampp/htdocs/farm/docs/contexts/rastreabilidade/profissional/cadeia-custodia.md`
   Foco: segregação física de produto certificado (orgânico, fair trade, sustentável),
   mass balance vs physical separation vs book-and-claim,
   auditoria de cadeia de custódia por certificadora credenciada
8. `/opt/lampp/htdocs/farm/docs/contexts/rastreabilidade/enterprise/certificacoes.md`
   Foco: processo de certificação GlobalG.A.P. (checklist de pontos de controle),
   USDA Organic / IBD Orgânico (3 anos de transição, sistema interno de controle),
   Rainforest Alliance (biodiversidade, trabalhadores, clima),
   integração com organismos certificadores (IBD, Ecocert, Control Union)
9. `/opt/lampp/htdocs/farm/docs/contexts/rastreabilidade/enterprise/auditoria-exportacao.md`
   Foco: EUDR — declaração de due diligence georreferenciada obrigatória,
   fornecedor de dados geoespaciais (coordenadas do talhão no EUDR registry),
   rastreabilidade para commodities: soja, carne bovina, café, cacau, madeira,
   integração com SISCOMEX para exportação
10. `/opt/lampp/htdocs/farm/docs/contexts/rastreabilidade/enterprise/blockchain.md`

### COMERCIALIZAÇÃO:
11. `/opt/lampp/htdocs/farm/docs/contexts/comercializacao/_overview.md`
12. `/opt/lampp/htdocs/farm/docs/contexts/comercializacao/essencial/clientes-compradores.md`
    Foco: cadastro de compradores (trading, cooperativa, cerealista, frigorífico, indústria),
    CNPJ + inscrição estadual, histórico de negociações, limite de crédito concedido
13. `/opt/lampp/htdocs/farm/docs/contexts/comercializacao/essencial/registro-vendas.md`
    Foco: venda spot (pronto entrega), venda a termo (entrega futura, preço fixo hoje),
    preço em R$/saca ou US$/bushel, vinculação à safra e lote,
    integração com financeiro (contas a receber), estoque (baixa de produto)
14. `/opt/lampp/htdocs/farm/docs/contexts/comercializacao/essencial/romaneios.md`
    Foco: romaneio de entrega (peso bruto, tara, umidade, impureza, classificação MAPA),
    desconto de umidade e impureza na sacagem final,
    integração com NF-e de venda (peso líquido tributável),
    P0.1/P0.2 já implementado no sistema (preservar referências)
15. `/opt/lampp/htdocs/farm/docs/contexts/comercializacao/profissional/contratos-venda.md`
    Foco: contrato a termo (fixação de preço para entrega futura),
    CPR Física (produto como garantia) vs CPR Financeira (liquidação em dinheiro),
    cláusula de qualidade (padrão mínimo para recebimento), multa por inadimplência,
    registro em cartório para validade plena
16. `/opt/lampp/htdocs/farm/docs/contexts/comercializacao/profissional/cotacoes-mercado.md`
    Foco: integração com APIs de cotação (B3 futuros, CEPEA/ESALQ preços físicos),
    cálculo de preço de equilíbrio (break-even) baseado no custo de produção da safra,
    alertas quando cotação atinge preço-alvo do produtor,
    gráfico histórico de preços por commodity
17. `/opt/lampp/htdocs/farm/docs/contexts/comercializacao/profissional/nfe-emissao.md`
    Foco: NF-e modelo 55 (produtor rural PJ) vs NF-e Produtor modelo 04 (estadual, PF),
    CFOP correto por operação (5.101 venda dentro do estado, 6.101 venda para outro estado,
    7.101 exportação), ICMS na saída de produtos rurais (isenção em muitos estados),
    integração com SEFAZ para autorização
18. `/opt/lampp/htdocs/farm/docs/contexts/comercializacao/enterprise/cpr-cedulas.md`
    Foco: emissão de CPR (Cédula de Produto Rural) como instrumento de crédito,
    CPR Física (entrega de soja futuramente) vs CPR Financeira (liquidação em dinheiro),
    registro em cartório obrigatório, averbação na matrícula do imóvel,
    risco de perda de safra vs seguro agrícola (PROAGRO/SEAF)
19. `/opt/lampp/htdocs/farm/docs/contexts/comercializacao/enterprise/hedge-derivativos.md`
    Foco: hedge via B3 (contratos futuros de soja, milho, boi gordo, café),
    compra de put (proteção de preço mínimo), venda de call (teto de preço),
    custo de hedge (margem, prêmio de opção), relação com crédito rural
20. `/opt/lampp/htdocs/farm/docs/contexts/comercializacao/enterprise/exportacao.md`
    Foco: habilitação RADAR (RFB) para exportar, drawback (suspensão de IPI/ICMS/II em insumos),
    Registro de Exportação (RE) no SISCOMEX, COA (Certificado de Origem Agrícola) MAPA,
    phytossanitary certificate, cotação FOB vs CIF, agente de carga (freight forwarder)

Use a ferramenta Write para reescrever cada arquivo.
Mantenha o frontmatter YAML original. Reescreva TODO o conteúdo abaixo do frontmatter.
```
