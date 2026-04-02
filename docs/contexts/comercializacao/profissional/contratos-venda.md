---
modulo: Comercialização
submodulo: Contratos de Venda
nivel: profissional
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../essencial/clientes-compradores.md
  - ../essencial/registro-vendas.md
  - ../essencial/romaneios.md
  - ../../financeiro/essencial/receitas.md
standalone: false
complexidade: L
assinante_alvo:
  - Médio produtor rural
  - Grande produtor rural
  - Cooperativas
  - Tradings agrícolas
---

# Contratos de Venda

## Descrição Funcional

Gestão de contratos de venda futura da produção agropecuária. Permite registrar contratos com fixação de preço (preço fixo, preço a fixar, preço mínimo), prazos de entrega, volumes comprometidos e cláusulas comerciais. Controla a execução do contrato (entregas realizadas vs. compromissadas), vencimentos e status. Fundamental para produtores que comercializam antecipadamente parte da safra para garantir preços ou obter financiamento.

## Personas — Quem usa este submódulo

- **Produtor rural:** Negocia e acompanha contratos de venda futura
- **Gerente comercial:** Estratégia de comercialização, define percentual da safra a contratar
- **Financeiro:** Monitora recebíveis de contratos, concilia pagamentos
- **Consultor/Corretor:** Auxilia na negociação e acompanha execução
- **Jurídico:** Revisa termos e cláusulas contratuais

## Dores que resolve

- Falta de controle sobre volume comprometido vs. produção estimada
- Risco de vender mais do que vai produzir (over-hedge)
- Perda de prazos de entrega por falta de acompanhamento
- Dificuldade de comparar preços contratados com mercado spot
- Ausência de registro formal de condições negociadas
- Impossibilidade de avaliar resultado da estratégia comercial ao final da safra

## Regras de Negócio

1. Contrato deve ter comprador, produto, safra, volume, preço e prazo de entrega
2. Modalidades de preço: Fixo, A Fixar, Preço Mínimo (floor), Média do Período
3. Volume contratado não deve exceder percentual configurável da produção estimada (alerta de over-hedge)
4. Contrato A Fixar permite fixação parcial em múltiplas datas até o vencimento
5. Status do contrato: Rascunho -> Assinado -> Em Execução -> Concluído -> Encerrado
6. Contrato assinado gera obrigação de entrega — romaneios são vinculados ao contrato
7. Saldo do contrato = Volume total - Volume já entregue (via romaneios)
8. Contrato vencido com saldo pendente gera alerta (washout/liquidação)
9. Preço pode ser em BRL/saca, BRL/ton, USD/bushel conforme negociação
10. Contrato cancelado após entrega parcial exige acordo de encerramento (liquidação financeira)
11. Cada contrato deve ter número único sequencial por fazenda/safra

## Entidades de Dados Principais

- **ContratoVenda:** id, fazenda_id, tenant_id, comprador_id, numero_contrato, safra_id, produto_id, modalidade_preco, preco_fixado, moeda, unidade_preco, volume_total, unidade_volume, data_inicio_entrega, data_fim_entrega, local_entrega, clausulas, status, observacoes, created_at, updated_at
- **ContratoFixacao:** id, contrato_id, data_fixacao, volume_fixado, preco_fixado, referencia_mercado, usuario_id
- **ContratoEntrega:** id, contrato_id, romaneio_id, volume_entregue, data_entrega
- **ContratoDocumento:** id, contrato_id, tipo_documento, arquivo_url, descricao

## Integrações Necessárias

- **Clientes/Compradores (essencial):** parte compradora do contrato
- **Romaneios (essencial):** entregas vinculadas ao contrato
- **Cotações de Mercado (profissional):** referência para fixação de preço
- **Receitas (financeiro):** geração de receita conforme execução
- **Safras (agrícola):** produção estimada para validação de over-hedge
- **NF-e (profissional):** emissão de nota fiscal nas entregas

## Fluxo de Uso Principal (step-by-step)

1. Produtor negocia contrato com comprador (fora do sistema)
2. Acessa Comercialização > Contratos > Novo Contrato
3. Seleciona comprador, produto e safra
4. Define modalidade de preço (Fixo, A Fixar, etc.)
5. Informa volume, unidade, prazo de entrega e local
6. Se preço fixo, informa valor; se a fixar, define prazo limite para fixação
7. Anexa documento do contrato assinado (PDF)
8. Confirma — status muda para "Assinado"
9. Sistema verifica percentual da safra comprometida e alerta se over-hedge
10. Conforme entregas ocorrem, romaneios são vinculados ao contrato
11. Para contratos A Fixar, produtor registra fixações parciais ao longo do tempo
12. Ao concluir todas entregas, contrato é marcado como "Concluído"
13. Financeiro acompanha pagamentos conforme cláusulas do contrato

## Casos Extremos e Exceções

- **Over-hedge:** volume contratado supera produção estimada — alerta obrigatório, bloqueio configurável
- **Washout:** contrato vence sem entrega total — liquidação financeira pela diferença de preço
- **Quebra de safra:** produção insuficiente para honrar contratos — necessário renegociar ou comprar no mercado
- **Variação cambial:** contratos em USD exigem conversão na data de pagamento
- **Fixação expirada:** contrato A Fixar cujo prazo de fixação venceu — aplicar preço de referência do dia
- **Contrato verbal:** sem documento anexo — sistema aceita mas alerta sobre risco
- **Múltiplas safras:** contrato que abrange entrega em duas safras diferentes
- **Disputa de qualidade:** comprador contesta classificação — campo para registro de disputas

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de contratos com todas as modalidades de preço
- [ ] Fluxo de status funcional com transições validadas
- [ ] Cálculo de saldo do contrato (volume total - entregas)
- [ ] Fixação de preço parcial para contratos A Fixar
- [ ] Alerta de over-hedge baseado na produção estimada da safra
- [ ] Vínculo de romaneios ao contrato
- [ ] Upload de documentos do contrato
- [ ] Dashboard de contratos com saldos e vencimentos
- [ ] Relatório de posição comercial (contratado vs. entregue vs. estoque)
- [ ] Isolamento por tenant e fazenda
- [ ] Testes de integração para fluxo completo

## Sugestões de Melhoria Futura

- Simulador de resultado por contrato (preço contratado vs. mercado spot)
- Alerta de vencimento de entrega via push/e-mail
- Integração com assinatura digital de contratos (DocuSign, Clicksign)
- Painel de posição comercial visual (gráfico de funil: produção -> contratado -> entregue -> pago)
- Comparativo de desempenho comercial entre safras
- Modelo de contrato padrão editável pelo produtor
