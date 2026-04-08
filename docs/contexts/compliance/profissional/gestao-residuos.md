---
modulo: Compliance Ambiental
submodulo: Gestao de Residuos
nivel: profissional
core: false
dependencias_core:
  - Identidade e Acesso
  - Cadastro da Propriedade
dependencias_modulos:
  - ../essencial/documentos-ambientais.md
  - ../../estoque/essencial/movimentacoes.md
  - ../../rastreabilidade/essencial/historico-aplicacoes.md
standalone: true
complexidade: M
assinante_alvo:
  - medio-produtor
  - grande-produtor
  - cooperativa
---

# Gestao de Residuos

## Descricao Funcional

O submodulo de Gestao de Residuos controla o ciclo completo de embalagens vazias de agrotoxicos e demais residuos perigosos gerados na atividade rural, conforme a Lei 7.802/89 e o Decreto 4.074/2002. O sistema rastreia desde a compra do produto ate a devolucao da embalagem na unidade de recebimento (posto do inpEV), garantindo a logistica reversa obrigatoria.

Funcionalidades principais:
- Rastreamento de embalagens vazias de agrotoxicos: quantidade, tipo, triplice lavagem realizada
- Controle de estoque de embalagens aguardando devolucao no deposito da fazenda
- Agendamento e registro de devolucoes em postos do inpEV ou centrais de recebimento
- Emissao de comprovante de devolucao e conciliacao com notas fiscais de compra
- Gestao de residuos solidos (oleos lubrificantes, pneus, baterias, residuos eletronicos)
- Controle de destinacao de residuos organicos (compostagem, biodigestao)
- Dashboard com indicadores: embalagens pendentes, taxa de devolucao, vencimentos

## Personas — Quem usa este submodulo

- **Produtor Rural:** acompanha pendencias de devolucao e agenda entregas nos postos
- **Operador de Campo:** registra triplice lavagem e armazena embalagens corretamente
- **Gerente de Fazenda:** monitora taxa de devolucao e conformidade de todas as propriedades
- **Fiscal Ambiental (externo):** verifica comprovantes de devolucao durante fiscalizacao
- **Consultor Ambiental:** elabora plano de gerenciamento de residuos solidos (PGRS)

## Dores que resolve

1. **Embalagens acumuladas:** depositos lotados de embalagens vazias sem controle de quantidade ou tipo
2. **Multas por descarte irregular:** embalagens descartadas em lixo comum ou queimadas geram autuacao
3. **Falta de comprovante:** produtor devolve embalagens mas nao guarda comprovante para fiscalizacao
4. **Conciliacao impossivel:** sem vincular compra ao descarte, nao ha como provar que todas as embalagens foram devolvidas
5. **Desconhecimento de postos:** produtor nao sabe onde fica a unidade de recebimento mais proxima
6. **Residuos diversos negligenciados:** foco apenas em agrotoxicos, mas oleos e baterias tambem exigem destinacao correta

## Regras de Negocio

1. Toda embalagem de agrotoxico deve ser devolvida em ate 1 ano apos a compra (Lei 7.802/89)
2. A triplice lavagem ou lavagem sob pressao e obrigatoria antes da devolucao
3. Embalagens nao lavaveis devem ser devolvidas ao estabelecimento onde foram compradas
4. O comprovante de devolucao do inpEV deve ser armazenado por no minimo 5 anos
5. O sistema deve conciliar automaticamente embalagens compradas (via NF) com embalagens devolvidas
6. Alertas devem ser emitidos quando embalagens estiverem a 60 e 30 dias do prazo de devolucao
7. Residuos perigosos (oleos, baterias) devem ser destinados a empresas licenciadas — sistema deve registrar MTR (Manifesto de Transporte de Residuos)
8. Permissoes: `compliance:residuos:read`, `compliance:residuos:create`, `compliance:residuos:update`
9. Dados vinculados ao tenant com isolamento multi-tenant obrigatorio

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `EmbalagemAgrotoxico` | id, tenant_id, fazenda_id, produto_id, nota_fiscal_compra, quantidade, tipo_embalagem, data_compra, triplice_lavagem, status (pendente, devolvida, vencida) | pertence a Fazenda |
| `DevolucaoEmbalagem` | id, tenant_id, fazenda_id, posto_inpev_id, data_devolucao, quantidade_total, comprovante_url, numero_comprovante | pertence a Fazenda |
| `DevolucaoItem` | id, devolucao_id, embalagem_id, quantidade | vincula Devolucao a Embalagem |
| `PostoInpEV` | id, nome, endereco, latitude, longitude, horario_funcionamento, telefone | independente |
| `ResiduoPerigoso` | id, tenant_id, fazenda_id, tipo (oleo, bateria, pneu, eletronico), quantidade, unidade, data_geracao, mtr_numero, destinacao_empresa, status | pertence a Fazenda |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `operacional/estoque` | Leitura | Notas fiscais de compra de agrotoxicos para vincular embalagens |
| `rastreabilidade/essencial/historico-aplicacoes` | Leitura | Consumo de agrotoxicos para calcular embalagens geradas |
| `compliance/essencial/documentos-ambientais` | Escrita | Comprovantes de devolucao registrados como documentos ambientais |
| inpEV | Leitura | Consulta de postos de recebimento e horarios |
| SINIR (MTR) | Escrita | Emissao de Manifesto de Transporte de Residuos para residuos perigosos |
| `core/notificacoes` | Escrita | Alertas de prazo de devolucao |

## Fluxo de Uso Principal (step-by-step)

1. Ao registrar compra de agrotoxico no estoque, sistema cria automaticamente registro de embalagem pendente
2. Apos uso do produto, operador registra que a triplice lavagem foi realizada
3. Embalagens lavadas sao armazenadas no deposito temporario da fazenda
4. Sistema exibe lista de embalagens pendentes com prazo de devolucao
5. Usuario consulta postos inpEV proximos e agenda devolucao
6. No dia da devolucao, registra saida das embalagens com quantidade e tipo
7. Apos devolucao, faz upload do comprovante emitido pelo posto
8. Sistema concilia embalagens devolvidas com registro de compra e atualiza status
9. Dashboard mostra taxa de devolucao e embalagens proximas do vencimento

## Casos Extremos e Excecoes

- **Embalagem danificada:** embalagem furada nao aceita pelo posto — registrar como "rejeitada" com motivo e buscar destinacao alternativa
- **Posto inpEV fechado:** unidade de recebimento mais proxima fechou — sistema deve sugerir alternativas
- **Compra sem nota fiscal:** produtor comprou agrotoxico informal — sistema permite registro manual com alerta de irregularidade
- **Embalagem de produto vencido nunca usado:** produto venceu no estoque — embalagem cheia deve ser devolvida ao fabricante (logistica diferente)
- **Fazenda remota:** distancia inviavel ate posto — registrar justificativa e aguardar campanha itinerante do inpEV

## Criterios de Aceite (Definition of Done)

- [ ] Registro automatico de embalagens ao cadastrar compra de agrotoxico
- [ ] Controle de triplice lavagem por embalagem
- [ ] Workflow de devolucao com upload de comprovante
- [ ] Conciliacao automatica entre compras e devolucoes
- [ ] Alertas de prazo de devolucao funcionais
- [ ] Consulta de postos inpEV proximos com mapa
- [ ] Gestao de residuos perigosos com MTR
- [ ] Dashboard com taxa de devolucao e indicadores
- [ ] Isolamento multi-tenant validado com testes de integracao
- [ ] Permissoes RBAC aplicadas em todas as rotas

## Sugestoes de Melhoria Futura

1. **Leitura de codigo de barras:** escanear embalagem para registro automatico de tipo e produto
2. **Integracao direta inpEV:** agendamento de devolucao online via API do inpEV
3. **Gamificacao:** ranking de fazendas com melhor taxa de devolucao para incentivar compliance
4. **PGRS automatizado:** geracao automatica do Plano de Gerenciamento de Residuos Solidos
5. **Rastreamento por lote:** vincular embalagem ao talhao e safra onde o produto foi aplicado
6. **Economia circular:** marketplace de residuos reciclaveis entre produtores e recicladores
