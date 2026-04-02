---
modulo: Estoque
submodulo: Cadastro de Produtos
nivel: essencial
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos: []
standalone: true
complexidade: S
assinante_alvo:
  - gestor-rural
  - almoxarife
  - comprador
---

# Cadastro de Produtos

## Descrição Funcional

Submódulo de cadastro e manutenção de insumos, produtos e materiais utilizados na fazenda. Organiza itens em categorias hierárquicas (ex.: Defensivos > Herbicidas > Pré-emergentes), define unidades de medida com conversão, e mantém dados fiscais (NCM, CFOP) para integração com NF-e. Suporta produtos com múltiplos fornecedores e preço de referência.

## Personas — Quem usa este submódulo

- **Almoxarife:** cadastro e manutenção de produtos, categorização
- **Comprador:** consulta de produtos, fornecedores e preços de referência
- **Gerente:** padronização do catálogo, aprovação de novos itens
- **Financeiro:** dados fiscais (NCM, CFOP) para integração contábil

## Dores que resolve

- Catálogo de produtos desorganizado com duplicidades e nomes inconsistentes
- Falta de padronização de unidades de medida entre setores
- Dados fiscais incompletos gerando retrabalho na emissão de NF
- Impossibilidade de comparar preços entre fornecedores sem cadastro centralizado
- Produtos cadastrados sem categoria, dificultando relatórios

## Regras de Negócio

1. Produto deve ter nome, unidade de medida principal e categoria obrigatórios
2. Código interno gerado automaticamente; código de barras (EAN) opcional
3. Categorias hierárquicas com até 3 níveis de profundidade
4. Unidades de medida com fator de conversão (ex.: 1 caixa = 12 unidades)
5. Produto pode ter múltiplos fornecedores com preço de referência cada
6. Produto inativo não aparece em novas movimentações mas mantém histórico
7. NCM e CFOP obrigatórios para produtos que entram via NF-e
8. Produto não pode ser excluído se houver saldo ou movimentação vinculada

## Entidades de Dados Principais

- **Produto:** id, tenant_id, codigo, nome, descricao, categoria_id, unidade_medida_id, ncm, cfop, codigo_barras, status (ativo|inativo), created_at, updated_at
- **CategoriaProduto:** id, tenant_id, nome, categoria_pai_id, nivel
- **UnidadeMedida:** id, tenant_id, sigla, nome, tipo (massa|volume|unidade|area)
- **ConversaoUnidade:** id, produto_id, unidade_origem_id, unidade_destino_id, fator_conversao
- **ProdutoFornecedor:** id, produto_id, fornecedor_id, preco_referencia, ultima_compra_data

## Integrações Necessárias

- **Core/Tenants:** Isolamento por tenant
- **Movimentações:** Produtos como item das movimentações
- **NF-e (Enterprise):** Dados fiscais para importação automática
- **Fornecedores:** Cadastro de fornecedores vinculados ao produto

## Fluxo de Uso Principal (step-by-step)

1. Acessar Estoque > Produtos > Categorias
2. Criar estrutura hierárquica de categorias
3. Cadastrar unidades de medida e conversões
4. Cadastrar produtos com dados completos
5. Vincular fornecedores e preços de referência
6. Importar produtos via CSV (para migração)
7. Consultar catálogo com filtros por categoria, status e fornecedor

## Casos Extremos e Exceções

- **Produto duplicado:** Validação por nome + unidade dentro da mesma categoria; alerta de possível duplicidade
- **Categoria com produtos filhos:** Não permitir exclusão; exigir reclassificação
- **Unidade de medida sem conversão:** Bloquear movimentação em unidade diferente da principal
- **Importação CSV com categoria inexistente:** Criar categoria automaticamente ou rejeitar (configurável)
- **Produto com NCM inválido:** Validação contra tabela TIPI; alerta mas não bloqueia

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de Produto com isolamento tenant
- [ ] Categorias hierárquicas com até 3 níveis
- [ ] Unidades de medida com conversão
- [ ] Vínculo produto-fornecedor com preço referência
- [ ] Importação CSV com validação
- [ ] Filtros e busca no catálogo
- [ ] Testes unitários e de integração

## Sugestões de Melhoria Futura

- Catálogo compartilhado entre tenants (produtos padrão do setor)
- Integração com ANVISA para defensivos regulados
- Foto do produto vinculada ao cadastro
- Histórico de preços com gráfico de tendência
- Sugestão automática de NCM baseada na descrição do produto
