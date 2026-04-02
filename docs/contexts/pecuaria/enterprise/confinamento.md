---
modulo: Pecuária
submodulo: Confinamento
nivel: enterprise
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-rebanho.md
  - ../essencial/manejos-basicos.md
  - ../profissional/nutricao.md
standalone: false
complexidade: XL
assinante_alvo:
  - confinador
  - pecuarista
  - nutricionista-animal
  - gestor-rural
---

# Confinamento

## Descrição Funcional

Submódulo de gestão completa de confinamento bovino, cobrindo desde o planejamento de entrada (compra de boi magro, formação de lotes) até a saída para abate. Controla curral de confinamento com capacidade, dieta diária por curral, leitura de cocho (ajuste de consumo), pesagens intermediárias e cálculo de desempenho zootécnico e econômico em tempo real.

Fornece o fechamento econômico do confinamento com custo total por cabeça, custo @, receita projetada por cenário de preço do boi gordo e margem operacional.

## Personas — Quem usa este submódulo

- **Confinador / Proprietário:** planejamento econômico, decisão de venda por cenário de preço
- **Nutricionista:** formulação de dieta, leitura de cocho, ajustes de consumo
- **Gerente de Confinamento:** operação diária, pesagens, controle de lotes
- **Tratador:** fornecimento diário de ração, leitura de cocho
- **Financeiro:** fechamento econômico, custo por cabeça, margem

## Dores que resolve

- Confinamento sem controle de custo por cabeça levando a prejuízo oculto
- Leitura de cocho não registrada causando desperdício de ração
- Impossibilidade de simular cenários de preço para decisão de venda
- Falta de acompanhamento do GMD real vs. projetado
- Fechamento econômico só no final do confinamento, sem visibilidade parcial

## Regras de Negócio

1. Confinamento organizado em ciclos (safra) com data início e fim
2. Cada curral tem capacidade máxima e dieta vinculada
3. Leitura de cocho diária: sobra classificada em escala (0-limpo a 3-excesso)
4. Ajuste de dieta baseado na leitura de cocho (automático ou manual)
5. Pesagem de entrada obrigatória; intermediárias a cada 21-28 dias (configurável)
6. GMD projetado vs. real acompanhado diariamente
7. Custo diário = (consumo ração × custo/kg) + (custo operacional rateado)
8. Ponto ótimo de abate: quando custo marginal da @ > preço de venda da @
9. Mortalidade e morbidade registradas e descontadas do resultado
10. Rendimento de carcaça padrão: 52% (configurável por destino de venda)

## Entidades de Dados Principais

- **CicloConfinamento:** id, tenant_id, fazenda_id, nome, data_inicio, data_fim_prevista, data_fim_real, status
- **CurralConfinamento:** id, tenant_id, fazenda_id, nome, capacidade_cabecas, dieta_id, ciclo_id
- **EntradaConfinamento:** id, lote_id, curral_id, data_entrada, peso_medio_entrada, custo_boi_magro_cabeca
- **LeituraCocho:** id, curral_id, data, escore_sobra (0-3), ajuste_percentual, responsavel_id
- **FechamentoEconomico:** id, ciclo_id, lote_id, custo_boi_magro, custo_alimentacao, custo_sanitario, custo_operacional, peso_medio_saida, rendimento_carcaca, preco_arroba_venda, receita_bruta, margem_operacional

## Integrações Necessárias

- **Cadastro de Rebanho:** Lotes e animais confinados
- **Manejos Básicos:** Pesagens para cálculo de GMD
- **Nutrição:** Dietas e custo por kg de ração
- **Estoque:** Consumo de ração e insumos
- **Sanidade:** Tratamentos durante confinamento
- **Financeiro:** Fechamento econômico, compra de boi magro, venda de boi gordo

## Fluxo de Uso Principal (step-by-step)

1. Criar ciclo de confinamento com datas e projeção de resultado
2. Cadastrar currais com capacidade e dieta vinculada
3. Registrar entrada de lotes com peso médio e custo do boi magro
4. Diariamente: fornecimento de ração e leitura de cocho
5. Sistema ajusta consumo com base na leitura de cocho
6. Pesagens intermediárias a cada 21-28 dias
7. Acompanhar dashboard: GMD real vs. projetado, custo @, ponto de abate
8. Simular cenários de venda com diferentes preços de arroba
9. Registrar saída para abate com peso final e destino
10. Gerar fechamento econômico do ciclo

## Casos Extremos e Exceções

- **Boi que não ganha peso (GMD < 0,5 kg/dia):** Alerta para investigação (doença, dominância)
- **Mortalidade no confinamento:** Registro obrigatório; custo da perda rateado no lote
- **Curral superlotado:** Bloquear entrada acima da capacidade
- **Dieta alterada no meio do ciclo:** Registrar troca com data e justificativa; recalcular custos
- **Preço da arroba cai abaixo do break-even:** Alerta com simulação de prejuízo projetado
- **Boi com problema sanitário retirado do curral:** Transferência para curral enfermaria

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de Ciclo e Curral de confinamento
- [ ] Registro de entrada com peso e custo do boi magro
- [ ] Leitura de cocho diária com ajuste de consumo
- [ ] Cálculo de GMD real vs. projetado
- [ ] Cálculo de custo @ em tempo real
- [ ] Simulador de cenários de venda
- [ ] Fechamento econômico completo do ciclo
- [ ] Isolamento multi-tenant e testes

## Sugestões de Melhoria Futura

- Integração com cocho eletrônico para leitura automática de consumo
- Modelo preditivo de GMD baseado em histórico e dieta
- Integração com bolsa (B3) para preço do boi gordo em tempo real
- Hedge automático com sugestão de contratos futuros
- Benchmark de desempenho entre ciclos e entre fazendas
