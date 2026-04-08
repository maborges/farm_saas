---
modulo: "Agrícola"
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

## Descrição Funcional

O submódulo de Planejamento de Safra permite ao produtor e ao agrônomo planejar o ciclo produtivo antes de iniciar a execução. Ele integra orçamento previsto, cronograma de operações, necessidade de insumos, alocação de maquinário e metas de produtividade.

O planejamento funciona como um "blueprint" da safra que, uma vez aprovado, serve como referência para acompanhamento de execução (planejado vs realizado). Está vinculado ao flag de módulo `A1_PLANEJAMENTO` — somente tenants com este módulo contratado têm acesso.

### Contexto Brasileiro

No Brasil, o planejamento de safra é crítico devido às particularidades climáticas e econômicas:

#### Janelas de Plantio (ZARC)
O Zoneamento Agroclimático de Risco (ZARC) define períodos ideais de plantio por município, cultura e variedade. Plantar fora da janela ZARC:
- Aumenta risco de perda por seca ou geada
- Pode impedir acesso ao seguro rural (Programa PSR)
- Pode inviabilizar financiamento do Plano Safra

#### Safra Dupla (Soja + Milho Safrinha)
No Cerrado (MT/GO/BA), o sucesso da safrinha depende do timing:
- Cada dia de atraso no plantio do milho após a soja reduz produtividade em 1-2%
- Janela ideal: 30-45 dias entre colheita da soja e plantio do milho
- Planejamento deve prever maquinário e insumos para ambas as safras sobrepostas

#### Custos de Insumos
Fertilizantes (NPK) e defensivos representam 60-70% do custo de produção:
- Produtor que planeja com antecedência pode comprar em baixa (entressafra)
- Cooperativas fazem compra consolidada para negociar melhor preço
- Planejamento de necessidade evita compras emergenciais a preços elevados

#### Financiamento Bancário
Bancos exigem plano de safra para liberar crédito rural:
- Plano de Custeio: cobre despesas até a colheita
- Plano de Investimento: maquinário, benfeitorias
- Banco analisa custo estimado vs receita projetada para definir limite

Funcionalidades principais:
- Planejamento de safra com cronograma de operações (Gantt simplificado)
- Orçamento previsto por talhão/safra com categorias de custo
- Necessidade de insumos calculada automaticamente (área x dosagem recomendada)
- Alocação de maquinário e mão de obra por período
- Metas de produtividade por talhão
- Comparativo planejado vs realizado em tempo real
- Checklist de safra com templates reutilizáveis
- Aprovação do plano por níveis hierárquicos
- Geração de relatório para financiamento bancário

## Personas — Quem usa este submódulo

- **Agrônomo (Cooperativa/Consultor)**: Cria o plano técnico — cronograma de operações, dosagens, metas de produtividade. Usa dados da Embrapa e histórico da fazenda para recomendar variedades e manejo.

- **Gerente de Fazenda**: Valida o plano operacional — alocação de maquinário e mão de obra. Precisa garantir que colheitadeiras estarão disponíveis na janela de colheita.

- **Diretor/Proprietário**: Aprova o orçamento e as metas financeiras. Compara ROI projetado com outras safras e culturas.

- **Comprador/Almoxarife**: Recebe lista de necessidade de insumos para planejamento de compras. Negocia com fornecedores e programa entregas.

- **Gerente Financeiro**: Usa o plano para negociar crédito rural com bancos. Compara custo de produção com preços de mercado para definir estratégia de venda.

## Dores que resolve

1. **Improviso**: Safras iniciadas sem planejamento geram custos maiores e produtividade menor. Comum em pequenas propriedades que não usam gestão profissional.

2. **Compras emergenciais**: Sem previsão de necessidade de insumos, compras são feitas em cima da hora a preços piores. Fertilizante comprado na entressafra pode custar 30% menos.

3. **Ociosidade de maquinário**: Sem cronograma, máquinas ficam ociosas ou sobrecarregadas. Colheitadeira parada custa R$ 5.000-10.000/dia em oportunidade perdida.

4. **Falta de metas**: Sem meta de produtividade, não há referência para avaliar resultado. Produtor não sabe se 55 sc/ha de soja é bom ou ruim para sua região.

5. **Orçamento estourado**: Sem previsão de custos, o produtor só descobre o resultado financeiro no fim da safra. Tarde demais para corrigir rumo.

6. **Financiamento negado**: Banco nega crédito por falta de planejamento técnico. Produtor não consegue comprovar viabilidade da safra.

7. **Janela ZARC ignorada**: Produtor planta fora do período recomendado e perde safra por seca. Seguro não cobre por descumprimento do ZARC.

## Regras de Negócio

1. Requer módulo `A1_PLANEJAMENTO` ativo no tenant (verificado via `require_module()`)
2. Um plano de safra pertence a exatamente uma safra (1:1)
3. O plano só pode ser criado para safras com status `planejada`
4. O orçamento é dividido em categorias: insumos, maquinário, mão_de_obra, serviços_terceiros, outros
5. A necessidade de insumos é calculada: `area_talhao_ha x dosagem_recomendada_por_ha x numero_aplicacoes`
6. O cronograma de operações define janelas de execução (data início/fim) para cada tipo de operação
7. O plano pode ter status: `rascunho`, `em_aprovacao`, `aprovado`, `revisado`
8. Somente planos `aprovado` servem como referência para o comparativo planejado vs realizado
9. Alterações em planos aprovados geram nova versão (histórico de revisões)
10. **Validação ZARC**: Sistema verifica se datas de plantio estão dentro da janela ZARC
11. **Compatibilidade de maquinário**: Alerta se mesmo equipamento está alocado em dois talhões no mesmo período
12. Permissões: `agricola:planejamento:create/read/update/approve`
13. Checklist templates são reutilizáveis entre safras e compartilháveis entre fazendas do mesmo tenant
14. **Orçamento por centro de custo**: Permitir alocação de custos por talhão, cultura ou propriedade

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `PlanoSafra` | id, tenant_id, safra_id, status, versao, aprovado_por, data_aprovacao, observacoes | pertence a Safra |
| `PlanoOrcamento` | id, plano_id, categoria, subcategoria, valor_previsto, valor_realizado | pertence a PlanoSafra |
| `PlanoCronograma` | id, plano_id, tipo_operacao_id, talhao_id, data_inicio_prevista, data_fim_prevista, responsavel_id | operações planejadas |
| `PlanoInsumo` | id, plano_id, produto_id, quantidade_total, unidade, custo_estimado | necessidade de insumos |
| `PlanoMeta` | id, plano_id, talhao_id, produtividade_esperada_kg_ha, receita_esperada | metas por talhão |
| `PlanoMaquinario` | id, plano_id, equipamento_id, periodo_inicio, periodo_fim, talhoes_alocados | alocação de máquinas |
| `ChecklistTemplate` | id, tenant_id, nome, itens (JSON), tipo_safra | templates reutilizáveis |
| `SafraChecklist` | id, safra_id, template_id, itens_status (JSON), responsavel_id | checklist instanciado |
| `ZarcValidacaoPlano` | id, plano_id, municipio_ibge, cultura, variedade, data_plantio, risco_climatico, indice_risco | validação ZARC do plano |

## Integrações Necessárias

| Sistema/Modulo | Tipo | Descrição |
|----------------|------|-----------|
| `agricola/safras` | Bidirecional | Plano vinculado à safra; comparativo alimentado por dados reais |
| `agricola/operacoes` | Leitura | Operações realizadas vs cronograma planejado |
| `agricola/custos` | Leitura | Custo realizado vs orçamento previsto |
| `operacional/estoque` | Leitura | Saldo atual vs necessidade de insumos |
| `operacional/frota` | Leitura | Disponibilidade de maquinário por período |
| `financeiro/despesas` | Leitura | Despesas realizadas vs orçamento |
| `core/cadastros/produtos` | Leitura | Catálogo de insumos e dosagens recomendadas |
| `api/zarc` | Leitura | Validação de época de plantio conforme Zoneamento Agroclimático |
| `api/conab` | Leitura | Preços de referência e produtividade média regional |

## Fluxo de Uso Principal (step-by-step)

1. Agrônomo acessa `/agricola/planejamento` e seleciona uma safra com status `planejada`
2. Sistema carrega talhões vinculados à safra com áreas e culturas
3. **Validação ZARC**: Sistema verifica janelas de plantio recomendadas para cada município
4. Agrônomo define cronograma: para cada tipo de operação, define janela de datas e talhões
5. Sistema alerta se há conflito de maquinário (mesmo equipamento em dois lugares)
6. Sistema calcula automaticamente necessidade de insumos baseado em dosagens recomendadas x área
7. **Dosagens Embrapa**: Sistema sugere dosagens baseadas em recomendações técnicas por cultura/região
8. Agrônomo ajusta quantidades e adiciona insumos extras se necessário
9. Agrônomo define metas de produtividade por talhão (kg/ha ou sacas/ha)
10. **Benchmark CONAB**: Sistema compara metas com produtividade média regional
11. Sistema calcula orçamento previsto: insumos + maquinário (horas x custo/h) + mão de obra
12. **Projeção de receita**: Sistema calcula receita estimada (produtividade x preço de mercado)
13. **Margem projetada**: Sistema mostra lucro/ROI esperado
14. Agrônomo cria checklist da safra a partir de template (ou do zero)
15. Plano fica como `rascunho` — agrônomo envia para aprovação
16. Gerente/diretor revisa e aprova o plano
17. **Relatório para banco**: Sistema gera documento para financiamento (custeio/investimento)
18. Plano `aprovado` passa a ser referência — dashboard mostra planejado vs realizado em tempo real
19. Se necessário, agrônomo cria nova versão do plano (revisão)

## Casos Extremos e Exceções

- **Safra já iniciada**: Produtor quer planejar uma safra que já começou — permitir, mas alertar que operações já realizadas não serão retroativamente vinculadas ao cronograma

- **Orçamento zerado**: Safra de subsistência sem orçamento monetário — permitir plano sem valores financeiros

- **Insumo sem dosagem cadastrada**: Produto novo sem recomendação no sistema — permitir entrada manual

- **Conflito de maquinário**: Mesmo trator alocado em dois talhões no mesmo período — alertar conflito e sugerir realocação

- **Revisão após execução**: Plano revisado quando 50% das operações já foram realizadas — manter histórico da versão original

- **Template de checklist com itens obsoletos**: Template referencia produto descontinuado — manter no template, alertar ao instanciar

- **Mudança de cultura no meio do planejamento**: Produtor decide mudar de soja para milho — permitir recálculo automático do plano

- **Falta de insumo no mercado**: Produto planejado está em falta — sugerir alternativas com dosagens equivalentes

- **Alteração de preço de insumo**: Fertilizante sofre reajuste de 20% — permitir atualização em lote de todos os itens do orçamento

## Critérios de Aceite (Definition of Done)

- [ ] Verificação de módulo `A1_PLANEJAMENTO` em todas as rotas (require_module)
- [ ] CRUD de plano de safra com versionamento
- [ ] Cronograma de operações com visualização tipo Gantt ou lista
- [ ] Cálculo automático de necessidade de insumos
- [ ] Orçamento previsto por categorias com totalizadores
- [ ] Metas de produtividade por talhão
- [ ] Fluxo de aprovação com status (rascunho → em_aprovacao → aprovado)
- [ ] Dashboard planejado vs realizado funcional
- [ ] Checklist templates com CRUD e instanciamento por safra
- [ ] Validação ZARC integrada ao planejamento
- [ ] Detecção de conflito de alocação de maquinário
- [ ] Tenant isolation e RBAC testados
- [ ] Geração de relatório para financiamento bancário
- [ ] Benchmark de produtividade com dados CONAB

## Sugestões de Melhoria Futura

1. **IA para sugestão de plano**: Baseado em histórico de safras anteriores, sugerir cronograma e dosagens otimizados

2. **Integração com previsão climática**: Ajustar janelas de operação com base em previsão de chuva (INMET, Climatempo)

3. **Simulador de cenários**: "E se eu plantar variedade X em vez de Y?" com projeção de custo e produtividade

4. **Exportação para financiamento**: Gerar plano de safra no formato exigido por bancos (Plano de Crédito Rural)

5. **Workflow de aprovação customizável**: Definir cadeia de aprovação por valor de orçamento

6. **Benchmark regional**: Comparar metas com média da região/cooperativa

7. **Integração com fornecedores**: Enviar previsão de demanda para fornecedores de insumos

8. **Planejamento de safra dupla**: Visualização integrada de soja + milho safrinha com dependências

9. **Análise de sensibilidade**: Simular impacto de variação de preços (insumos + commodity) no ROI

10. **Recomendação de variedades**: Sugestão de cultivares baseada em dados da Embrapa por região
