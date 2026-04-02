---
modulo: Comercialização
submodulo: CPR e Cédulas
nivel: enterprise
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../profissional/contratos-venda.md
  - ../essencial/clientes-compradores.md
  - ../essencial/romaneios.md
  - ../../financeiro/essencial/receitas.md
standalone: false
complexidade: XL
assinante_alvo:
  - Grande produtor rural
  - Cooperativas
  - Tradings agrícolas
  - Instituições financeiras rurais
---

# CPR — Cédula do Produtor Rural

## Descrição Funcional

Gestão de Cédulas do Produtor Rural (CPR), o principal título de crédito do agronegócio brasileiro. Permite registrar, acompanhar e controlar CPR Física (entrega de produto) e CPR Financeira (liquidação em dinheiro). Controla emissão, registro em cartório, vencimentos, entregas, liquidação e baixa. Integra com o fluxo de contratos de venda e entregas (romaneios) para acompanhamento da execução da obrigação.

## Personas — Quem usa este submódulo

- **Produtor rural (emitente):** Emite CPR para obter financiamento antecipado da safra
- **Gerente financeiro:** Controla vencimentos, saldos e liquidação das CPRs
- **Gerente comercial:** Vincula CPRs a contratos e entregas
- **Banco/Financiadora (credor):** Consulta status de execução da CPR
- **Jurídico:** Acompanha registro, averbações e execuções judiciais

## Dores que resolve

- Falta de controle sobre CPRs emitidas — produtor esquece vencimentos e volumes
- Risco de descumprimento por falta de acompanhamento de entregas
- Descontrole entre CPR emitida, contrato associado e entregas realizadas
- Dificuldade de calcular exposição total (quanto está comprometido em CPRs)
- Ausência de alertas de vencimento

## Regras de Negócio

1. CPR deve ter: emitente (produtor), credor/beneficiário, produto, quantidade, prazo, local de entrega
2. CPR Física: obrigação de entregar o produto na quantidade e qualidade especificadas
3. CPR Financeira: obrigação de pagar valor em dinheiro indexado a indicador (ESALQ, CBOT)
4. CPR deve ser registrada em cartório de registro de imóveis para ter validade como título executivo
5. CPR pode ter avalista (garantidor) — dados do avalista devem ser registrados
6. Garantias podem incluir: penhor da safra, hipoteca do imóvel, alienação fiduciária
7. Volume comprometido em CPRs + contratos não deve exceder produção estimada (alerta de over-commitment)
8. CPR vencida sem liquidação gera alerta de inadimplência
9. CPR com registro na B3 (CRA lastro) tem regras adicionais de compliance
10. Status: Rascunho -> Emitida -> Registrada -> Em Execução -> Liquidada -> Baixada

## Entidades de Dados Principais

- **CPR:** id, fazenda_id, tenant_id, tipo (fisica/financeira), numero, serie, emitente_nome, emitente_cpf_cnpj, credor_id, avalista_nome, avalista_cpf_cnpj, produto_id, safra_id, quantidade, unidade, preco_referencia, valor_total, indice_referencia, data_emissao, data_vencimento, local_entrega, cartorio_registro, numero_registro, data_registro, garantias, status, observacoes, created_at, updated_at
- **CPRGarantia:** id, cpr_id, tipo_garantia (penhor_safra/hipoteca/alienacao_fiduciaria), descricao, matricula_imovel, valor_garantia
- **CPREntrega:** id, cpr_id, romaneio_id, data_entrega, quantidade_entregue
- **CPRLiquidacao:** id, cpr_id, tipo_liquidacao (entrega/financeira), data_liquidacao, valor_liquidado, comprovante_url

## Integrações Necessárias

- **Contratos de Venda (profissional):** CPR pode estar vinculada a um contrato de venda
- **Romaneios (essencial):** entregas que liquidam a CPR Física
- **Clientes/Compradores (essencial):** credor da CPR
- **Receitas/Despesas (financeiro):** fluxo financeiro da CPR
- **Safras (agrícola):** produção estimada para controle de over-commitment
- **Registro de imóveis (externo):** registro da CPR em cartório (manual)

## Fluxo de Uso Principal (step-by-step)

1. Produtor negocia CPR com credor (banco, trading, cooperativa)
2. Acessa Comercialização > CPR > Nova CPR
3. Seleciona tipo (Física ou Financeira)
4. Preenche dados do credor, produto, safra, quantidade e prazo
5. Para CPR Financeira, define índice de referência e fórmula de cálculo
6. Registra garantias oferecidas (penhor, hipoteca)
7. Sistema verifica exposição total (CPRs + contratos vs. produção estimada)
8. Salva e imprime modelo de CPR para assinatura
9. Após assinatura e registro em cartório, atualiza status para "Registrada"
10. Informa número e data de registro no cartório
11. Conforme entregas (CPR Física) ou pagamentos (CPR Financeira) ocorrem, registra liquidações
12. Ao completar a obrigação, CPR é marcada como "Liquidada"
13. Após confirmação do credor, status final "Baixada"

## Casos Extremos e Exceções

- **Over-commitment:** volume em CPRs supera produção — alerta grave de risco
- **Quebra de safra:** produção insuficiente para honrar CPR — renegociação ou execução judicial
- **CPR vencida:** credor pode executar judicialmente — registrar status e acompanhar
- **Endosso de CPR:** credor transfere CPR para terceiro — registrar novo beneficiário
- **CPR cancelada antes do registro:** permitido sem restrições
- **CPR cancelada após registro:** exige averbação de cancelamento no cartório
- **Variação de índice (CPR Financeira):** valor a liquidar muda conforme indicador — recalcular no vencimento
- **Garantia com imóvel em mais de uma CPR:** alerta de sobreposição de garantias

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de CPR Física e Financeira
- [ ] Fluxo de status com transições validadas
- [ ] Registro de garantias vinculadas
- [ ] Controle de entregas/liquidações parciais
- [ ] Cálculo de saldo pendente (quantidade ou valor)
- [ ] Alerta de over-commitment vs. produção estimada
- [ ] Alerta de vencimento (30, 15, 7 dias antes)
- [ ] Impressão de modelo de CPR para assinatura
- [ ] Dashboard de CPRs ativas com saldos e vencimentos
- [ ] Isolamento por tenant e fazenda
- [ ] Testes de integração

## Sugestões de Melhoria Futura

- Integração com cartórios digitais para registro eletrônico
- Integração com B3/CRA para CPRs registradas em bolsa
- Modelo de CPR padronizado conforme Lei 8.929/94 atualizada
- Workflow de aprovação interna antes da emissão
- Relatório de exposição total consolidado (CPRs + contratos + hedge)
- Score de risco de inadimplência por CPR
