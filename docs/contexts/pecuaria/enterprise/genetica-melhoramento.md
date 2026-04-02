---
modulo: Pecuária
submodulo: Genética e Melhoramento
nivel: enterprise
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-rebanho.md
  - ../profissional/reproducao.md
standalone: false
complexidade: XL
assinante_alvo:
  - melhorista
  - zootecnista
  - pecuarista-elite
  - central-de-semen
---

# Genética e Melhoramento

## Descrição Funcional

Submódulo de gestão genética e melhoramento animal, abrangendo registro genealógico (pedigree), DEPs (Diferenças Esperadas na Progênie), importação de sumários de touros, índices de seleção e planejamento de acasalamentos dirigidos. Permite que fazendas de genética e criadores de elite tomem decisões de seleção e descarte baseadas em dados genéticos, maximizando o progresso genético do rebanho.

Suporta importação de dados de programas de melhoramento (PMGZ, Aliança, Paint, Delta G) e cálculo de índices econômicos customizados.

## Personas — Quem usa este submódulo

- **Zootecnista / Melhorista:** análise de DEPs, planejamento de acasalamentos, seleção
- **Proprietário de genética:** decisão de descarte e venda de reprodutores
- **Central de sêmen:** catálogo de touros com DEPs e genealogia
- **Comprador de genética:** consulta de pedigree e mérito genético

## Dores que resolve

- Genealogia mantida em fichas de papel ou sistemas legados sem integração
- DEPs consultadas manualmente em PDFs de sumários
- Planejamento de acasalamento sem considerar consanguinidade
- Índices de seleção não customizados para o objetivo da fazenda
- Impossibilidade de comparar touros de diferentes sumários/programas

## Regras de Negócio

1. Genealogia registra pai, mãe e avós (mínimo 3 gerações); importação de pedigree via CSV
2. DEPs importadas de sumários oficiais com ano e base genética
3. Índice de seleção = soma ponderada de DEPs conforme pesos do critério econômico
4. Acasalamento dirigido considera: complementaridade de DEPs, consanguinidade máxima (<6,25%), e índice de mérito do cruzamento
5. Consanguinidade calculada via coeficiente de Wright
6. Touro provado: mínimo 30 filhos avaliados; jovem: genômica ou progênie parcial
7. Animais com DEPs abaixo do limiar de corte: sugeridos para descarte
8. Dados genômicos (quando disponíveis) integrados às DEPs tradicionais

## Entidades de Dados Principais

- **Genealogia:** id, animal_id, pai_id, mae_id, avo_paterno_id, avo_paterna_id, avo_materno_id, avo_materna_id, registro_genealogico
- **DEP:** id, animal_id, sumario_id, caracteristica (peso_desmama|peso_sobreano|perimetro_escrotal|habilidade_materna|etc.), valor, acuracia, percentil
- **Sumario:** id, tenant_id, programa (PMGZ|Aliança|Paint), raca, ano, base_genetica
- **IndiceSelecao:** id, tenant_id, nome, criterios_json (lista de DEPs com pesos)
- **AcasalamentoDirigido:** id, tenant_id, matriz_id, touro_id, indice_merito, consanguinidade_estimada, status (planejado|executado|cancelado)

## Integrações Necessárias

- **Cadastro de Rebanho:** Animais com dados de identificação e raça
- **Reprodução:** Inseminações e monta para registro de pai
- **Programas de Melhoramento (externo):** Importação de sumários e DEPs
- **Genômica (futuro):** Resultados de genotipagem para DEPs genômicas

## Fluxo de Uso Principal (step-by-step)

1. Importar genealogia do rebanho (CSV ou manual)
2. Importar sumário de DEPs do programa de melhoramento
3. Definir critérios de seleção com pesos econômicos
4. Sistema calcula índice de seleção para cada animal
5. Rankear animais e identificar candidatos a seleção e descarte
6. Planejar acasalamentos dirigidos com verificação de consanguinidade
7. Sistema sugere melhores combinações por índice de mérito
8. Executar acasalamentos (integração com módulo Reprodução)
9. Acompanhar progresso genético do rebanho ao longo das gerações

## Casos Extremos e Exceções

- **Animal sem genealogia conhecida:** Permitir cadastro parcial; DEPs calculadas como "base"
- **DEPs de programas diferentes:** Não comparar diretamente; alertar sobre bases genéticas distintas
- **Consanguinidade acima do limiar:** Bloquear acasalamento com alerta; permitir override com justificativa
- **Touro sem sumário atualizado:** Alertar que DEPs podem estar desatualizadas
- **Importação de sumário com formato não reconhecido:** Parser configurável; rejeitar com relatório de erros
- **Animal com registro genealógico duplicado:** Detecção e merge com confirmação manual

## Critérios de Aceite (Definition of Done)

- [ ] Cadastro de genealogia com mínimo 3 gerações
- [ ] Importação de sumários de DEPs (CSV/planilha)
- [ ] Cálculo de índice de seleção customizável
- [ ] Ranking de animais por índice
- [ ] Planejamento de acasalamento com verificação de consanguinidade
- [ ] Cálculo de coeficiente de Wright
- [ ] Visualização de árvore genealógica
- [ ] Isolamento multi-tenant e testes

## Sugestões de Melhoria Futura

- Integração com laboratórios de genotipagem para importação de SNPs
- Seleção genômica com DEPs moleculares
- Simulação de progresso genético em X gerações
- Marketplace de genética com catálogo de touros e matrizes
- Integração com ABCZ/ABC para registro genealógico digital
