---
modulo: Comercialização
submodulo: Clientes e Compradores
nivel: essencial
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos: []
standalone: true
complexidade: S
assinante_alvo:
  - Pequeno produtor rural
  - Médio produtor rural
  - Agricultor familiar
---

# Clientes e Compradores

## Descrição Funcional

Cadastro centralizado de todos os clientes e compradores da produção agropecuária. Inclui cerealistas, cooperativas, frigoríficos, laticínios, tradings, exportadores e compradores pessoa física. Armazena dados cadastrais (CNPJ/CPF, razão social, endereço, contato), condições comerciais habituais e histórico de transações. Serve como base para todos os demais submódulos de comercialização.

## Personas — Quem usa este submódulo

- **Produtor rural:** Cadastra compradores com quem negocia frequentemente
- **Gerente comercial:** Mantém base de compradores atualizada, avalia relacionamentos
- **Auxiliar administrativo:** Registra dados cadastrais e documentos dos compradores
- **Financeiro:** Consulta dados do comprador para cobrança e emissão de documentos

## Dores que resolve

- Dados de compradores espalhados em agenda, celular e caderno
- Falta de histórico de negociações por comprador
- Dificuldade de contatar comprador rapidamente em época de venda
- Retrabalho ao preencher dados do comprador em cada venda/NF-e
- Impossibilidade de avaliar quais compradores pagam melhor ou pontualmente

## Regras de Negócio

1. CNPJ/CPF deve ser único por tenant (não pode duplicar comprador)
2. CNPJ deve ser validado (dígitos verificadores)
3. CPF deve ser validado (dígitos verificadores)
4. Comprador pode ser pessoa física (CPF) ou jurídica (CNPJ)
5. Pelo menos um contato (telefone ou e-mail) é obrigatório
6. Comprador com vendas vinculadas não pode ser excluído, apenas inativado
7. Inscrição Estadual é obrigatória para pessoa jurídica (necessária para NF-e)
8. Classificação por tipo: Cerealista, Cooperativa, Frigorífico, Laticínio, Trading, Outro
9. Dados são isolados por tenant (multi-tenancy)
10. Comprador pode atender múltiplas fazendas do mesmo tenant

## Entidades de Dados Principais

- **Comprador:** id, tenant_id, tipo_pessoa (PF/PJ), cpf_cnpj, razao_social, nome_fantasia, inscricao_estadual, endereco_completo, cidade, uf, cep, telefone, email, tipo_comprador, ativo, observacoes, created_at, updated_at
- **CompradorContato:** id, comprador_id, nome, cargo, telefone, email, principal (boolean)
- **CompradorCondicaoComercial:** id, comprador_id, prazo_pagamento_dias, forma_pagamento_padrao, desconto_padrao_percentual

## Integrações Necessárias

- **Registro de Vendas (essencial):** comprador é referenciado em toda venda
- **Romaneios (essencial):** destinatário das entregas
- **Contratos de Venda (profissional):** parte contratante
- **NF-e (profissional):** dados do destinatário para emissão
- **Receitas (financeiro):** identificação do pagador

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa menu Comercialização > Clientes/Compradores
2. Clica em "Novo Comprador"
3. Seleciona tipo de pessoa (PF ou PJ)
4. Preenche CPF/CNPJ — sistema valida automaticamente
5. Preenche razão social, nome fantasia (PJ) ou nome completo (PF)
6. Informa endereço completo, telefone e e-mail
7. Seleciona tipo de comprador (Cerealista, Cooperativa, etc.)
8. Opcionalmente adiciona contatos adicionais (representantes)
9. Opcionalmente configura condições comerciais padrão
10. Salva o cadastro
11. Comprador fica disponível para seleção em vendas, contratos e romaneios

## Casos Extremos e Exceções

- **CNPJ duplicado:** sistema impede cadastro e sugere o registro existente
- **Comprador de outro estado:** necessário informar IE para operações interestaduais
- **Comprador internacional:** sem CPF/CNPJ, usa documento estrangeiro (tier enterprise/exportação)
- **Comprador inativado com vendas pendentes:** sistema alerta antes de inativar
- **Fusão/aquisição de empresas:** comprador muda CNPJ — manter histórico do antigo e vincular ao novo
- **Cooperativa como comprador e fornecedor:** mesmo CNPJ pode existir no cadastro de fornecedores separadamente

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo com validação de CPF/CNPJ
- [ ] Busca por nome, CPF/CNPJ, cidade e tipo
- [ ] Validação de unicidade de CPF/CNPJ por tenant
- [ ] Inativação (soft delete) com verificação de vendas vinculadas
- [ ] Cadastro de múltiplos contatos por comprador
- [ ] Condições comerciais padrão configuráveis
- [ ] Listagem com filtros e paginação
- [ ] Isolamento por tenant
- [ ] Testes unitários e de integração
- [ ] Testes de isolamento multi-tenant

## Sugestões de Melhoria Futura

- Consulta automática de dados cadastrais via CNPJ (ReceitaWS/BrasilAPI)
- Score de confiabilidade baseado em histórico de pagamentos
- Ranking de compradores por volume e pontualidade
- Integração com CRM para gestão de relacionamento
- Geolocalização do comprador no mapa
- Importação em lote via planilha
