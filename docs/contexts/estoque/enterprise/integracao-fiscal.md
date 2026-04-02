---
modulo: Estoque
submodulo: Integração Fiscal
nivel: enterprise
core: false
dependencias_core:
  - Identidade e Acesso
  - Integrações Essenciais
dependencias_modulos:
  - ../essencial/movimentacoes.md
  - ../profissional/lotes-validade.md
  - ../../comercializacao/profissional/nfe-emissao.md
standalone: false
complexidade: XL
assinante_alvo: grandes operações, cooperativas, exportadores
---

# Integração Fiscal

## Descrição Funcional

Submódulo que conecta o estoque com o sistema fiscal: importação automática de XML de NF-e de entrada (fornecedores), validação de dados fiscais contra pedido de compra, e entrada automática no estoque com dados completos (lote, validade, NCM, CFOP). Reduz digitação manual e garante conformidade fiscal.

## Personas — Quem usa este submódulo

- **Almoxarife/Compras:** Recebe NF-e e confere com pedido
- **Fiscal/Contador:** Valida dados fiscais, CFOP, NCM
- **Gestor de Estoque:** Monitora entradas automáticas

## Dores que resolve

1. Digitação manual de dados de NF-e no estoque é lenta e propensa a erros
2. Divergências entre NF-e e pedido de compra passam despercebidas
3. Dados fiscais (NCM, CFOP) não vinculados ao produto no estoque
4. Sem importação automática, conferência fiscal é retrabalho

## Regras de Negócio

1. **RN-IF-001:** XML de NF-e pode ser importado via upload manual, email automático (caixa postal) ou consulta à SEFAZ
2. **RN-IF-002:** Sistema extrai automaticamente: fornecedor, produtos, quantidades, valores, lotes, NCM, CFOP
3. **RN-IF-003:** Matching automático produto NF-e ↔ produto cadastrado via código do fornecedor ou EAN
4. **RN-IF-004:** Divergências de quantidade ou valor entre NF-e e pedido geram alerta para conferência manual
5. **RN-IF-005:** Após aprovação, entrada no estoque é criada automaticamente com dados completos
6. **RN-IF-006:** NF-e importada é armazenada como documento vinculado à movimentação

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `NfeImportada` | id, fazenda_id, chave_acesso, xml_s3_key, fornecedor_cnpj, valor_total, status, importada_em | → Fazenda |
| `NfeItem` | id, nfe_id, produto_nfe, ean, ncm, cfop, quantidade, valor_unitario, lote, validade | → NfeImportada |
| `NfeMatchProduto` | nfe_item_id, produto_id, status_match, conferido_por | → NfeItem, → Produto |

## Integrações Necessárias

- **SEFAZ:** Consulta de NF-e por chave de acesso (Distribuição DFe)
- **Email (IMAP):** Caixa postal para recebimento automático de XMLs
- **Estoque Movimentações:** Criação automática de entrada
- **Compras:** Matching com pedido de compra para conferência
- **S3/MinIO:** Armazenamento de XMLs originais

## Fluxo de Uso Principal (step-by-step)

1. XML de NF-e chega (upload manual, email ou SEFAZ)
2. Sistema parseia XML e extrai dados estruturados
3. Matching automático de produtos (código fornecedor ou EAN)
4. Produtos não reconhecidos → marcados para associação manual
5. Se há pedido de compra vinculado → conferência automática de quantidades e valores
6. Divergências listadas para aprovação do operador
7. Operador aprova → entrada no estoque criada com dados completos (lote, validade, custo)
8. XML armazenado e vinculado à movimentação para auditoria

## Casos Extremos e Exceções

- **XML com formato inválido:** Rejeição com mensagem descritiva do erro
- **Produto na NF-e sem correspondência no cadastro:** Fluxo de cadastro rápido ou associação manual
- **NF-e duplicada (mesma chave de acesso):** Bloqueio automático com aviso
- **NF-e de devolução:** Tratamento invertido — gera saída de estoque

## Critérios de Aceite (Definition of Done)

- [ ] Importação de XML de NF-e com parsing completo
- [ ] Matching automático de produtos por código/EAN
- [ ] Conferência contra pedido de compra com lista de divergências
- [ ] Entrada automática no estoque após aprovação
- [ ] Armazenamento do XML original vinculado à movimentação
- [ ] Detecção de NF-e duplicada
- [ ] Suporte a NF-e de devolução (saída)

## Sugestões de Melhoria Futura

1. Consulta automática à SEFAZ (Distribuição DFe) por agendamento
2. OCR de DANFE para NF-e recebidas em papel
3. Manifestação do destinatário automática
