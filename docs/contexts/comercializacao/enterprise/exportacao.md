---
modulo: Comercialização
submodulo: Exportação
nivel: enterprise
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../profissional/contratos-venda.md
  - ../profissional/nfe-emissao.md
  - ../essencial/clientes-compradores.md
  - ../essencial/romaneios.md
  - ../../financeiro/essencial/receitas.md
standalone: false
complexidade: XL
assinante_alvo:
  - Grande produtor rural
  - Tradings agrícolas
  - Cooperativas exportadoras
---

# Exportação

## Descrição Funcional

Gestão completa do processo de exportação de commodities agrícolas. Abrange desde a negociação com compradores internacionais até a emissão de documentos para embarque. Controla contratos internacionais (FOB, CIF, CFR), documentação de exportação (invoice, packing list, bill of lading, certificado fitossanitário), integração com SISCOMEX, câmbio e logística portuária. Voltado para operações de grande porte que vendem produção para o mercado externo.

## Personas — Quem usa este submódulo

- **Diretor comercial:** Negocia contratos internacionais e define estratégia de exportação
- **Analista de exportação/comex:** Prepara documentação, acompanha processo de embarque
- **Despachante aduaneiro:** Consulta dados para despacho e liberação alfandegária
- **Financeiro:** Controla câmbio, ACC/ACE e recebimentos internacionais
- **Logística:** Coordena transporte até o porto e agendamento de embarque

## Dores que resolve

- Complexidade documental da exportação — muitos documentos diferentes com regras específicas
- Risco de embarque barrado por falta de documento ou certificado vencido
- Falta de controle sobre prazos de embarque e janelas portuárias
- Dificuldade de conciliar câmbio contratado com câmbio efetivo
- Ausência de visão integrada do processo (contrato -> documentação -> embarque -> pagamento)

## Regras de Negócio

1. Contrato de exportação deve especificar Incoterm (FOB, CIF, CFR, etc.)
2. Moeda obrigatoriamente em divisas (USD, EUR) com taxa de câmbio de referência
3. Documentos obrigatórios mínimos: Commercial Invoice, Packing List, Bill of Lading
4. Certificado fitossanitário obrigatório para produtos agrícolas (MAPA)
5. Registro no SISCOMEX/DU-E (Declaração Única de Exportação) obrigatório
6. ACC (Adiantamento sobre Contrato de Câmbio) pode ser vinculado ao contrato
7. Prazo de embarque deve ser respeitado — penalidades por atraso (demurrage)
8. Exportação isenta de ICMS (Lei Kandir) — NF-e com CFOP 7101
9. PIS/COFINS não incide sobre receita de exportação
10. Câmbio deve ser fechado na data do embarque ou conforme contrato de ACC/ACE
11. Peso embarcado deve ser conciliado com peso contratado (tolerância de +/- 5% padrão)

## Entidades de Dados Principais

- **ContratoExportacao:** id, fazenda_id, tenant_id, comprador_id, numero_contrato, produto_id, safra_id, incoterm, quantidade_toneladas, preco_por_tonelada, moeda, valor_total, porto_embarque, porto_destino, prazo_embarque_inicio, prazo_embarque_fim, tolerancia_percentual, status, created_at, updated_at
- **DocumentoExportacao:** id, contrato_exportacao_id, tipo_documento (invoice/packing_list/bl/certificado_fito/due/outros), numero, data_emissao, data_validade, arquivo_url, status (rascunho/emitido/aprovado)
- **Embarque:** id, contrato_exportacao_id, navio, data_embarque, porto, terminal, quantidade_embarcada_ton, bl_numero, container_numeros, status
- **OperacaoCambio:** id, contrato_exportacao_id, tipo (ACC/ACE/pronto), banco, valor_usd, taxa_cambio, valor_brl, data_contratacao, data_liquidacao, status

## Integrações Necessárias

- **SISCOMEX (externa):** registro de DU-E e acompanhamento do despacho aduaneiro
- **MAPA (externa):** certificado fitossanitário para exportação de produtos agrícolas
- **Contratos de Venda (profissional):** contrato base da operação
- **NF-e (profissional):** emissão de NF-e de exportação (CFOP 7101)
- **Clientes/Compradores (essencial):** dados do importador
- **Romaneios (essencial):** controle de entrega no porto/armazém
- **Receitas (financeiro):** receita de exportação em moeda estrangeira
- **Câmbio/BCB (externa):** taxas de câmbio para conversão
- **Cotações de Mercado (profissional):** referência de preço internacional

## Fluxo de Uso Principal (step-by-step)

1. Diretor comercial negocia contrato com comprador internacional
2. Acessa Comercialização > Exportação > Novo Contrato de Exportação
3. Preenche dados: comprador, produto, volume, Incoterm, preço em USD, prazo de embarque
4. Se houver ACC, registra operação de câmbio antecipado
5. Analista prepara documentação: Commercial Invoice, Packing List
6. Solicita certificado fitossanitário ao MAPA
7. Registra DU-E no SISCOMEX
8. Coordena logística de transporte até o porto
9. Na data do embarque, registra dados do navio, containers e quantidades
10. Obtém Bill of Lading do agente marítimo
11. Envia documentos ao comprador (diretamente ou via banco)
12. Fecha câmbio (se não houver ACC) e registra operação
13. Comprador confirma recebimento e efetua pagamento
14. Financeiro concilia pagamento em USD com câmbio e registra receita

## Casos Extremos e Exceções

- **Embarque atrasado (demurrage):** navio esperando no porto — custos de sobre-estadia
- **Certificado fitossanitário vencido:** embarque bloqueado até renovação
- **Rejeição no destino:** problema de qualidade — produto devolvido ou renegociado
- **Variação cambial entre contrato e embarque:** diferença de câmbio gera ganho/perda financeira
- **Força maior:** greve portuária, pandemia — cláusula de force majeure no contrato
- **Embarque parcial:** comprador aceita entrega em múltiplos navios
- **Washout de exportação:** cancelamento de contrato com liquidação financeira
- **Mudança de destino:** comprador redireciona carga para outro porto/país
- **Sanções internacionais:** destino sob embargo — bloquear operação

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de contratos de exportação com Incoterms
- [ ] Gestão de documentos de exportação (upload, status, validade)
- [ ] Registro de embarques com dados de navio e containers
- [ ] Controle de operações de câmbio (ACC/ACE/pronto)
- [ ] Emissão de NF-e de exportação (CFOP 7101)
- [ ] Dashboard de exportações com status e prazos
- [ ] Alerta de documentos a vencer e prazos de embarque
- [ ] Conciliação de volumes (contratado vs. embarcado)
- [ ] Cálculo de resultado da exportação em BRL
- [ ] Isolamento por tenant e fazenda
- [ ] Testes de integração

## Sugestões de Melhoria Futura

- Integração direta com SISCOMEX via API para registro automático de DU-E
- Rastreamento de navio em tempo real (AIS/vessel tracking)
- Integração com bancos para fechamento de câmbio online
- Checklist automático de documentos por Incoterm
- Relatório de rentabilidade por operação de exportação
- Integração com certificadoras de sustentabilidade (ex: RTRS para soja responsável)
