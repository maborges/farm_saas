---
modulo: Estoque
submodulo: Lotes e Validade
nivel: profissional
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-produtos.md
  - ../essencial/movimentacoes.md
standalone: false
complexidade: M
assinante_alvo:
  - almoxarife
  - gestor-rural
  - veterinario
  - agronomo
---

# Lotes e Validade

## Descrição Funcional

Submódulo de rastreabilidade de lotes de produtos com controle de data de fabricação, validade e fornecedor. Permite rastrear cada unidade em estoque até seu lote de origem, controlando FEFO (First Expired, First Out) para produtos perecíveis. Gera alertas de produtos próximos ao vencimento e bloqueia saída de produtos vencidos.

Essencial para defensivos agrícolas, vacinas, medicamentos veterinários e insumos com prazo de validade.

## Personas — Quem usa este submódulo

- **Almoxarife:** controle de validade, organização FEFO, descarte de vencidos
- **Veterinário:** rastreabilidade de lote de vacina/medicamento aplicado
- **Agrônomo:** rastreabilidade de lote de defensivo aplicado
- **Gerente:** visão de produtos próximos ao vencimento para ação preventiva
- **Qualidade/Auditoria:** rastreamento de lote em caso de recall ou problema

## Dores que resolve

- Produtos vencidos utilizados por falta de controle de validade
- Impossibilidade de rastrear qual lote de vacina foi aplicado em qual animal
- Desperdício por vencimento de produtos estocados sem rotação adequada
- Multas e problemas legais por uso de defensivos vencidos
- Falta de rastreabilidade para atender auditorias e recalls

## Regras de Negócio

1. Lote de produto registra: número do lote, data fabricação, data validade, fornecedor
2. FEFO: saídas consomem primeiro os lotes com validade mais próxima
3. Produto vencido: bloqueio de saída para uso; apenas saída tipo DESCARTE permitida
4. Alerta de vencimento: 30, 15 e 7 dias antes (configurável)
5. Lote obrigatório para produtos classificados como "controlado" (defensivos, medicamentos)
6. Número do lote do fornecedor registrado para rastreabilidade externa
7. Lote pode ser bloqueado manualmente (suspeita de qualidade) impedindo saída
8. Rastreabilidade reversa: a partir do lote, listar todas as saídas/aplicações

## Entidades de Dados Principais

- **LoteProduto:** id, tenant_id, produto_id, numero_lote, numero_lote_fornecedor, data_fabricacao, data_validade, fornecedor_id, quantidade_recebida, quantidade_disponivel, status (ativo|vencido|bloqueado|esgotado)
- **MovimentacaoLote:** id, movimentacao_id, lote_produto_id, quantidade
- **AlertaValidade:** id, tenant_id, lote_produto_id, dias_para_vencimento, data_alerta, status

## Integrações Necessárias

- **Movimentações:** Saídas vinculadas a lotes específicos
- **FIFO/Custo:** Lote de custo vinculado ao lote físico
- **Pecuária/Sanidade:** Lote de vacina aplicado registrado no manejo
- **Agrícola:** Lote de defensivo aplicado registrado na operação
- **Fiscal (Enterprise):** Lote recebido via NF-e

## Fluxo de Uso Principal (step-by-step)

1. Na entrada de produto, registrar dados do lote (número, fabricação, validade)
2. Sistema organiza lotes por FEFO automaticamente
3. Na saída, sistema sugere lote com validade mais próxima
4. Almoxarife confirma lote e registra saída
5. Sistema gera alertas de produtos próximos ao vencimento
6. Produtos vencidos bloqueados; almoxarife registra descarte
7. Consultar rastreabilidade: lote > movimentações > destino final
8. Em caso de recall: rastreabilidade reversa para localizar uso

## Casos Extremos e Exceções

- **Produto sem data de validade:** Não obrigar; tratar como validade infinita
- **Lote vencido com saldo:** Bloquear uso; gerar alerta de descarte obrigatório
- **Dois lotes com mesma validade:** FEFO por data de entrada (mais antigo primeiro)
- **Recall de fornecedor:** Bloquear lote manualmente; alertar todos que usaram
- **Lote parcialmente consumido e bloqueado:** Manter saldo bloqueado; registrar motivo
- **Entrada sem número de lote:** Gerar lote interno automático com flag de regularização

## Critérios de Aceite (Definition of Done)

- [ ] Registro de lote com dados de fabricação, validade e fornecedor
- [ ] FEFO automático na sugestão de saída
- [ ] Bloqueio de saída de produto vencido
- [ ] Alertas configuráveis de proximidade de vencimento
- [ ] Rastreabilidade direta e reversa por lote
- [ ] Bloqueio manual de lote com justificativa
- [ ] Isolamento multi-tenant e testes

## Sugestões de Melhoria Futura

- Leitura de lote e validade via OCR da embalagem
- Integração com ANVISA/MAPA para alertas de recall automáticos
- Dashboard de validade com visualização tipo timeline
- Doação automática sugerida para produtos próximos ao vencimento
- QR Code por lote para rastreabilidade rápida em campo
