---
modulo: Estoque
submodulo: Inventário Automatizado
nivel: enterprise
core: false
dependencias_core:
  - Identidade e Acesso
  - Cadastro da Propriedade
dependencias_modulos:
  - ../essencial/saldo-consulta.md
  - ../profissional/fifo-custo.md
standalone: false
complexidade: M
assinante_alvo: grandes operações, cooperativas
---

# Inventário Automatizado

## Descrição Funcional

Submódulo para gestão de contagens de inventário físico com reconciliação automática contra saldo do sistema. Suporta inventário total (todos os produtos) e rotativo (amostragem por categoria/localização). Gera ajustes de estoque com rastreabilidade completa.

## Personas — Quem usa este submódulo

- **Almoxarife:** Executa contagem física e registra quantidades
- **Gestor de Estoque:** Programa inventários, aprova ajustes, analisa divergências
- **Auditor:** Consulta histórico de inventários e ajustes

## Dores que resolve

1. Contagem manual em papel é lenta e propensa a erros de transcrição
2. Sem reconciliação automática, identificar divergências exige comparação manual
3. Ajustes de estoque sem justificativa comprometem rastreabilidade
4. Inventários infrequentes acumulam divergências significativas

## Regras de Negócio

1. **RN-IA-001:** Inventário pode ser total (todos os produtos) ou rotativo (filtro por categoria, almoxarifado ou localização)
2. **RN-IA-002:** Durante inventário ativo, movimentações nos produtos em contagem são bloqueadas
3. **RN-IA-003:** Cada item contado é comparado ao saldo do sistema → divergência calculada automaticamente
4. **RN-IA-004:** Ajustes com divergência > 5% requerem aprovação do gestor
5. **RN-IA-005:** Ajuste gera movimentação de estoque tipo "ajuste_inventario" com referência ao inventário
6. **RN-IA-006:** Inventário rotativo pode ser programado como recorrente (mensal, trimestral)

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `Inventario` | id, fazenda_id, tipo, status, data_inicio, data_fim, responsavel_id | → Fazenda, → Usuario |
| `InventarioItem` | id, inventario_id, produto_id, saldo_sistema, quantidade_contada, divergencia, status_ajuste | → Inventario, → Produto |
| `AjusteEstoque` | id, inventario_item_id, quantidade_ajuste, motivo, aprovado_por, aprovado_em | → InventarioItem |

## Integrações Necessárias

- **Saldo Consulta:** Captura saldo do sistema no momento da abertura do inventário
- **FIFO/Custo:** Ajustes impactam valoração do estoque
- **Notificações:** Alertas de inventário programado, aprovação pendente
- **Mobile (futuro):** Leitura de código de barras para contagem

## Fluxo de Uso Principal (step-by-step)

1. Gestor programa inventário (total ou rotativo) com data e responsável
2. Na data, sistema congela saldo dos produtos selecionados
3. Almoxarife acessa lista de itens → registra quantidade contada para cada produto
4. Sistema calcula divergência automática (contado - sistema)
5. Gestor revisa divergências → aprova ajustes dentro da tolerância
6. Divergências acima da tolerância requerem justificativa + aprovação superior
7. Ajustes aprovados geram movimentações de estoque automaticamente
8. Inventário é encerrado → produtos desbloqueados para movimentação

## Casos Extremos e Exceções

- **Movimentação durante inventário:** Bloqueada para produtos em contagem, permitida para demais
- **Inventário abandonado (não finalizado):** Após 7 dias sem atividade, sistema alerta gestor. Após 14 dias, cancela automaticamente
- **Divergência de 100% (zerado no sistema mas tem físico):** Exige foto como evidência + justificativa detalhada
- **Dois inventários simultâneos:** Não permitido para mesma fazenda/almoxarifado

## Critérios de Aceite (Definition of Done)

- [ ] Criação de inventário total e rotativo
- [ ] Bloqueio de movimentações durante contagem
- [ ] Cálculo automático de divergências
- [ ] Aprovação por alçada para divergências significativas
- [ ] Ajustes geram movimentações rastreáveis
- [ ] Inventário rotativo programável (recorrente)

## Sugestões de Melhoria Futura

1. Leitura de código de barras/QR via app mobile
2. Contagem cega (operador não vê saldo do sistema durante contagem)
3. Dashboard de acurácia de estoque ao longo do tempo
