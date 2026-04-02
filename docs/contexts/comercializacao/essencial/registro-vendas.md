---
modulo: Comercialização
submodulo: Registro de Vendas
nivel: essencial
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../clientes-compradores.md
  - ../../operacional/essencial/estoque.md
  - ../../financeiro/essencial/receitas.md
standalone: false
complexidade: M
assinante_alvo:
  - Pequeno produtor rural
  - Médio produtor rural
  - Agricultor familiar
---

# Registro de Vendas

## Descrição Funcional

Submódulo responsável pelo registro completo de vendas da produção agropecuária. Permite cadastrar vendas de grãos (soja, milho, café, etc.), leite, gado em pé, e demais produtos da fazenda. Cada venda registra produto, quantidade, unidade de medida, preço unitário, comprador, data da venda, forma de pagamento e status (pendente, entregue, pago). Serve como fonte única de verdade para toda receita de comercialização.

## Personas — Quem usa este submódulo

- **Produtor rural:** Registra vendas realizadas, acompanha valores e status de pagamento
- **Gerente de fazenda:** Monitora volume de vendas, compara preços obtidos, avalia desempenho comercial
- **Financeiro:** Consulta vendas para conciliar receitas e contas a receber
- **Auxiliar administrativo:** Digita vendas a partir de notas e recibos

## Dores que resolve

- Falta de registro centralizado de vendas — produtor perde controle do que vendeu e para quem
- Dificuldade de saber quanto já foi entregue vs. quanto falta entregar
- Impossibilidade de comparar preços obtidos entre compradores e períodos
- Descontrole de pagamentos pendentes — não sabe quem deve e quanto
- Informações espalhadas em cadernos, planilhas e WhatsApp

## Regras de Negócio

1. Toda venda deve estar vinculada a um comprador cadastrado
2. Quantidade vendida não pode exceder o estoque disponível (se integração com estoque ativa)
3. Preço unitário deve ser positivo e na moeda configurada (BRL padrão)
4. Status da venda segue fluxo: Rascunho -> Confirmada -> Em Entrega -> Entregue -> Paga
5. Venda confirmada não pode ser excluída, apenas cancelada (com justificativa)
6. Cancelamento após entrega parcial exige estorno das quantidades entregues no estoque
7. Cada venda gera automaticamente um lançamento de receita no módulo financeiro (se contratado)
8. Vendas são isoladas por fazenda (tenant + fazenda_id)
9. Unidade de medida deve ser compatível com o produto (sacas 60kg para grãos, litros para leite, arroba/@/cabeça para gado)
10. Data da venda não pode ser futura (vendas futuras são contratos — tier profissional)

## Entidades de Dados Principais

- **Venda:** id, fazenda_id, tenant_id, comprador_id, produto_id, safra_id (opcional), data_venda, quantidade, unidade_medida, preco_unitario, valor_total, forma_pagamento, status, observacoes, created_at, updated_at
- **VendaItem:** id, venda_id, produto_id, quantidade, preco_unitario, subtotal (para vendas com múltiplos produtos)
- **VendaPagamento:** id, venda_id, data_pagamento, valor_pago, forma_pagamento, comprovante_url

## Integrações Necessárias

- **Clientes/Compradores (essencial):** vínculo obrigatório com comprador cadastrado
- **Estoque (operacional):** validação de disponibilidade e baixa automática na entrega
- **Receitas (financeiro):** geração automática de lançamento de receita
- **Safras (agrícola):** associação opcional da venda a uma safra específica
- **Romaneios (essencial):** vínculo com entregas físicas

## Fluxo de Uso Principal (step-by-step)

1. Produtor acessa tela de Vendas no menu Comercialização
2. Clica em "Nova Venda"
3. Seleciona o comprador (ou cadastra novo inline)
4. Seleciona o produto e a safra (opcional)
5. Informa quantidade, unidade de medida e preço unitário
6. Sistema calcula valor total automaticamente
7. Informa forma de pagamento e data prevista
8. Salva como rascunho ou confirma diretamente
9. Ao confirmar, sistema valida estoque (se integrado) e gera receita no financeiro
10. Acompanha status da venda no dashboard de vendas
11. Registra pagamentos recebidos conforme ocorrem
12. Venda é marcada como "Paga" quando valor total é quitado

## Casos Extremos e Exceções

- **Venda parcial:** comprador paga apenas parte — sistema mantém saldo devedor
- **Devolução:** comprador devolve produto — requer estorno parcial da venda e reentrada no estoque
- **Preço renegociado:** após confirmação, permite ajuste de preço com registro de histórico
- **Venda sem estoque integrado:** produtor no tier essencial sem módulo operacional pode registrar vendas sem validação de estoque
- **Venda de produto não cadastrado:** sistema deve permitir cadastro rápido de produto
- **Múltiplas formas de pagamento:** uma venda pode ter parte à vista e parte a prazo
- **Moeda estrangeira:** vendas em USD (exportação) são tratadas no tier enterprise

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de vendas com todos os campos obrigatórios
- [ ] Validação de estoque quando módulo operacional está contratado
- [ ] Fluxo de status funcional (Rascunho -> Confirmada -> Entregue -> Paga)
- [ ] Geração automática de receita no financeiro (quando contratado)
- [ ] Filtros por período, comprador, produto, status e safra
- [ ] Listagem com totalizadores (quantidade total, valor total, valor pendente)
- [ ] Cancelamento com justificativa e estorno de estoque
- [ ] Registro de pagamentos parciais
- [ ] Isolamento por tenant e fazenda
- [ ] Testes de integração cobrindo fluxo completo
- [ ] Testes de isolamento multi-tenant

## Sugestões de Melhoria Futura

- Dashboard de vendas com gráficos de evolução mensal e comparativo de safras
- Alerta automático de pagamentos vencidos via e-mail/WhatsApp
- Relatório de preço médio obtido por produto e por comprador
- Integração com cotações de mercado para comparar preço de venda vs. mercado
- Importação em lote de vendas via planilha CSV/Excel
- App mobile para registro de vendas em campo
