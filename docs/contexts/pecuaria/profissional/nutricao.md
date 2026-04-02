---
modulo: Pecuária
submodulo: Nutrição
nivel: profissional
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-rebanho.md
  - ../essencial/manejos-basicos.md
standalone: false
complexidade: L
assinante_alvo:
  - pecuarista
  - zootecnista
  - nutricionista-animal
  - gestor-rural
---

# Nutrição

## Descrição Funcional

Submódulo de gestão nutricional do rebanho, abrangendo formulação de dietas, controle de suplementação (sal mineral, proteinado, ração), consumo diário por lote e cálculo de custo por arroba produzida (custo @). Permite registrar dietas com composição percentual de ingredientes, calcular consumo previsto vs. real e gerar análise econômica de cada estratégia nutricional.

O custo @ é calculado dividindo o custo total de alimentação pelo ganho de peso em arrobas, permitindo comparação entre diferentes estratégias nutricionais e decisão de venda.

## Personas — Quem usa este submódulo

- **Nutricionista Animal / Zootecnista:** formulação de dietas, ajuste de suplementação
- **Gerente de Fazenda:** controle de consumo e custos nutricionais
- **Proprietário:** análise de custo @ para decisão de venda
- **Vaqueiro:** registro diário de fornecimento de ração/suplemento

## Dores que resolve

- Custo por arroba desconhecido, impossibilitando saber se há lucro na engorda
- Desperdício de suplemento por falta de controle de consumo real
- Dietas formuladas em planilha sem vínculo com estoque e custo atualizado
- Impossibilidade de comparar estratégias nutricionais economicamente
- Consumo por lote estimado por "achismo" em vez de medição real

## Regras de Negócio

1. Dieta composta por ingredientes com proporção percentual (deve somar 100%)
2. Consumo previsto calculado: peso vivo médio do lote × % PV × número de animais
3. Consumo real registrado diariamente pelo responsável
4. Custo @ = custo total alimentação do lote / ganho de peso total em arrobas
5. 1 arroba = 15 kg (padrão brasileiro); configurável por tenant
6. Custo dos ingredientes vinculado ao preço do estoque (atualizado automaticamente)
7. Dieta pode ser vinculada a um ou mais lotes simultaneamente
8. Troca de dieta gera registro histórico com data e justificativa

## Entidades de Dados Principais

- **Dieta:** id, tenant_id, nome, descricao, tipo (pastagem|suplementacao|confinamento), consumo_pv_percentual, status
- **DietaIngrediente:** id, dieta_id, produto_id, percentual, custo_kg_override
- **FornecimentoDiario:** id, tenant_id, lote_id, dieta_id, data, quantidade_kg_fornecida, responsavel_id
- **CustoArroba:** id, tenant_id, lote_id, periodo_inicio, periodo_fim, custo_total_alimentacao, ganho_peso_total_kg, custo_arroba_calculado
- **HistoricoDieta:** id, lote_id, dieta_id, data_inicio, data_fim, motivo_troca

## Integrações Necessárias

- **Cadastro de Rebanho:** Lotes como unidade de manejo nutricional
- **Manejos Básicos:** Pesagens para cálculo de GMD e custo @
- **Estoque:** Ingredientes e preços para composição de dieta e baixa de consumo
- **Financeiro:** Custo nutricional para análise de rentabilidade
- **Confinamento (Enterprise):** Dietas de confinamento com formulação diária

## Fluxo de Uso Principal (step-by-step)

1. Acessar Pecuária > Nutrição > Dietas
2. Criar dieta com ingredientes e proporções
3. Sistema calcula custo/kg da dieta com base nos preços do estoque
4. Vincular dieta a um ou mais lotes
5. Registrar fornecimento diário (quantidade kg fornecida)
6. Sistema compara consumo previsto vs. real
7. Após pesagem, sistema calcula custo @ do período
8. Analisar dashboard nutricional: custo @, consumo, eficiência alimentar

## Casos Extremos e Exceções

- **Ingrediente sem preço no estoque:** Exigir preço manual ou bloquear cálculo de custo
- **Dieta com proporções que não somam 100%:** Bloquear salvamento; alertar diferença
- **Lote sem pesagem recente:** Não calcular custo @ sem dados de ganho de peso; alertar pesagem pendente
- **Troca frequente de dieta (<7 dias):** Alerta informativo ao responsável
- **Consumo real muito acima do previsto (>130%):** Alerta de possível desperdício ou erro
- **Ingrediente descontinuado:** Permitir substituição e manter histórico da dieta original

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de Dieta com composição percentual de ingredientes
- [ ] Cálculo automático de custo/kg da dieta
- [ ] Registro de fornecimento diário por lote
- [ ] Cálculo de custo @ por período
- [ ] Comparativo consumo previsto vs. real
- [ ] Dashboard nutricional com indicadores
- [ ] Integração com estoque para preços e baixa
- [ ] Isolamento multi-tenant e testes

## Sugestões de Melhoria Futura

- Formulação de dieta por otimização linear (custo mínimo atendendo exigências nutricionais)
- Integração com análise bromatológica de laboratório
- Cálculo de pegada de carbono por estratégia nutricional
- Recomendação automática de dieta baseada em GMD alvo
- Comparativo de custo @ entre fazendas e regiões (benchmark)
