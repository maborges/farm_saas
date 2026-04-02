---
modulo: "Agr\xEDcola"
submodulo: Planejamento de Safra
nivel: profissional
core: false
dependencias_core:
  - core/auth
  - core/cadastros/fazendas
  - core/cadastros/produtos
  - core/tenant
  - core/modulos (A1_PLANEJAMENTO)
dependencias_modulos:
  - ../essencial/safras.md
  - ../essencial/operacoes-campo.md
  - ../profissional/custos-producao.md
standalone: false
complexidade: XL
assinante_alvo:
  - medio-produtor
  - grande-produtor
  - cooperativa
---

# Planejamento de Safra

## Descricao Funcional

O submodulo de Planejamento de Safra permite ao produtor e ao agronomo planejar o ciclo produtivo antes de iniciar a execucao. Ele integra orcamento previsto, cronograma de operacoes, necessidade de insumos, alocacao de maquinario e metas de produtividade.

O planejamento funciona como um "blueprint" da safra que, uma vez aprovado, serve como referencia para acompanhamento de execucao (planejado vs realizado). Esta vinculado ao flag de modulo `A1_PLANEJAMENTO` — somente tenants com este modulo contratado tem acesso.

Funcionalidades principais:
- Planejamento de safra com cronograma de operacoes (Gantt simplificado)
- Orcamento previsto por talhao/safra com categorias de custo
- Necessidade de insumos calculada automaticamente (area x dosagem recomendada)
- Alocacao de maquinario e mao de obra por periodo
- Metas de produtividade por talhao
- Comparativo planejado vs realizado em tempo real
- Checklist de safra com templates reutilizaveis
- Aprovacao do plano por niveis hierarquicos

## Personas — Quem usa este submodulo

- **Agronomo:** cria o plano tecnico — cronograma de operacoes, dosagens, metas de produtividade
- **Gerente de Fazenda:** valida o plano operacional — alocacao de maquinario e mao de obra
- **Diretor/Proprietario:** aprova o orcamento e as metas financeiras
- **Comprador/Almoxarife:** recebe lista de necessidade de insumos para planejamento de compras

## Dores que resolve

1. **Improviso:** safras iniciadas sem planejamento geram custos maiores e produtividade menor
2. **Compras emergenciais:** sem previsao de necessidade de insumos, compras sao feitas em cima da hora a precos piores
3. **Ociosidade de maquinario:** sem cronograma, maquinas ficam ociosas ou sobrecarregadas
4. **Falta de metas:** sem meta de produtividade, nao ha referencia para avaliar resultado
5. **Orcamento estourado:** sem previsao de custos, o produtor so descobre o resultado financeiro no fim da safra

## Regras de Negocio

1. Requer modulo `A1_PLANEJAMENTO` ativo no tenant (verificado via `require_module()`)
2. Um plano de safra pertence a exatamente uma safra (1:1)
3. O plano so pode ser criado para safras com status `planejada`
4. O orcamento e dividido em categorias: insumos, maquinario, mao_de_obra, servicos_terceiros, outros
5. A necessidade de insumos e calculada: `area_talhao_ha x dosagem_recomendada_por_ha x numero_aplicacoes`
6. O cronograma de operacoes define janelas de execucao (data inicio/fim) para cada tipo de operacao
7. O plano pode ter status: `rascunho`, `em_aprovacao`, `aprovado`, `revisado`
8. Somente planos `aprovado` servem como referencia para o comparativo planejado vs realizado
9. Alteracoes em planos aprovados geram nova versao (historico de revisoes)
10. Permissoes: `agricola:planejamento:create/read/update/approve`
11. Checklist templates sao reutilizaveis entre safras e compartilhaveis entre fazendas do mesmo tenant

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `PlanoSafra` | id, tenant_id, safra_id, status, versao, aprovado_por, data_aprovacao, observacoes | pertence a Safra |
| `PlanoOrcamento` | id, plano_id, categoria, subcategoria, valor_previsto, valor_realizado | pertence a PlanoSafra |
| `PlanoCronograma` | id, plano_id, tipo_operacao_id, talhao_id, data_inicio_prevista, data_fim_prevista, responsavel_id | operacoes planejadas |
| `PlanoInsumo` | id, plano_id, produto_id, quantidade_total, unidade, custo_estimado | necessidade de insumos |
| `PlanoMeta` | id, plano_id, talhao_id, produtividade_esperada_kg_ha, receita_esperada | metas por talhao |
| `ChecklistTemplate` | id, tenant_id, nome, itens (JSON), tipo_safra | templates reutilizaveis |
| `SafraChecklist` | id, safra_id, template_id, itens_status (JSON), responsavel_id | checklist instanciado |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `agricola/safras` | Bidirecional | Plano vinculado a safra; comparativo alimentado por dados reais |
| `agricola/operacoes` | Leitura | Operacoes realizadas vs cronograma planejado |
| `agricola/custos` | Leitura | Custo realizado vs orcamento previsto |
| `operacional/estoque` | Leitura | Saldo atual vs necessidade de insumos |
| `operacional/frota` | Leitura | Disponibilidade de maquinario por periodo |
| `financeiro/despesas` | Leitura | Despesas realizadas vs orcamento |
| `core/cadastros/produtos` | Leitura | Catalogo de insumos e dosagens recomendadas |

## Fluxo de Uso Principal (step-by-step)

1. Agronomo acessa `/agricola/planejamento` e seleciona uma safra com status `planejada`
2. Sistema carrega talhoes vinculados a safra com areas e culturas
3. Agronomo define cronograma: para cada tipo de operacao, define janela de datas e talhoes
4. Sistema calcula automaticamente necessidade de insumos baseado em dosagens recomendadas x area
5. Agronomo ajusta quantidades e adiciona insumos extras se necessario
6. Agronomo define metas de produtividade por talhao (kg/ha ou sacas/ha)
7. Sistema calcula orcamento previsto: insumos + maquinario (horas x custo/h) + mao de obra
8. Agronomo cria checklist da safra a partir de template (ou do zero)
9. Plano fica como `rascunho` — agronomo envia para aprovacao
10. Gerente/diretor revisa e aprova o plano
11. Plano `aprovado` passa a ser referencia — dashboard mostra planejado vs realizado em tempo real
12. Se necessario, agronomo cria nova versao do plano (revisao)

## Casos Extremos e Excecoes

- **Safra ja iniciada:** produtor quer planejar uma safra que ja comecou — permitir, mas alertar que operacoes ja realizadas nao serao retroativamente vinculadas ao cronograma
- **Orcamento zerado:** safra de subsistencia sem orcamento monetario — permitir plano sem valores financeiros
- **Insumo sem dosagem cadastrada:** produto novo sem recomendacao no sistema — permitir entrada manual
- **Conflito de maquinario:** mesmo trator alocado em dois talhoes no mesmo periodo — alertar conflito
- **Revisao apos execucao:** plano revisado quando 50% das operacoes ja foram realizadas — manter historico da versao original
- **Template de checklist com itens obsoletos:** template referencia produto descontinuado — manter no template, alertar ao instanciar

## Criterios de Aceite (Definition of Done)

- [ ] Verificacao de modulo `A1_PLANEJAMENTO` em todas as rotas (require_module)
- [ ] CRUD de plano de safra com versionamento
- [ ] Cronograma de operacoes com visualizacao tipo Gantt ou lista
- [ ] Calculo automatico de necessidade de insumos
- [ ] Orcamento previsto por categorias com totalizadores
- [ ] Metas de produtividade por talhao
- [ ] Fluxo de aprovacao com status (rascunho → em_aprovacao → aprovado)
- [ ] Dashboard planejado vs realizado funcional
- [ ] Checklist templates com CRUD e instanciamento por safra
- [ ] Tenant isolation e RBAC testados
- [ ] Deteccao de conflito de alocacao de maquinario

## Sugestoes de Melhoria Futura

1. **IA para sugestao de plano:** baseado em historico de safras anteriores, sugerir cronograma e dosagens otimizados
2. **Integracao com previsao climatica:** ajustar janelas de operacao com base em previsao de chuva
3. **Simulador de cenarios:** "e se eu plantar variedade X em vez de Y?" com projecao de custo e produtividade
4. **Exportacao para financiamento:** gerar plano de safra no formato exigido por bancos (Plano de Credito Rural)
5. **Workflow de aprovacao customizavel:** definir cadeia de aprovacao por valor de orcamento
6. **Benchmark regional:** comparar metas com media da regiao/cooperativa
