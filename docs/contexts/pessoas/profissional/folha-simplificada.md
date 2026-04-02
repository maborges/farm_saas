---
modulo: Pessoas e RH
submodulo: Folha Simplificada
nivel: profissional
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-colaboradores.md
  - ../essencial/controle-presenca.md
  - ../../financeiro/essencial/despesas.md
standalone: false
complexidade: L
assinante_alvo:
  - Médio produtor rural
  - Grande produtor rural
  - Cooperativas
---

# Folha de Pagamento Simplificada

## Descrição Funcional

Cálculo simplificado de folha de pagamento para colaboradores rurais. Calcula salário líquido a partir do salário base, horas extras, adicional noturno, insalubridade/periculosidade, descontos legais (INSS, IRRF) e benefícios (vale-transporte, moradia, alimentação). Gera holerites e resumo da folha para conferência. Não substitui sistema de folha completo (DP), mas dá autonomia ao produtor para estimar custos e preparar dados para o contador.

## Personas — Quem usa este submódulo

- **Produtor rural:** Calcula folha para pagar funcionários em dia
- **RH/Administrativo:** Processa folha mensal, gera holerites
- **Contador:** Recebe dados pré-processados para conferência e fechamento oficial
- **Gerente financeiro:** Acompanha custo de pessoal por fazenda/setor

## Dores que resolve

- Dependência total do contador para saber quanto pagar — atrasa pagamentos
- Falta de visibilidade sobre custo real de cada colaborador
- Erros frequentes no cálculo manual de horas extras e descontos
- Colaboradores sem holerite — irregularidade trabalhista
- Impossibilidade de projetar custo de pessoal para planejamento

## Regras de Negócio

1. Salário base conforme cadastro do colaborador (respeitando piso da categoria rural)
2. Hora extra 50%: horas extras em dias úteis = (salário/220) x 1,5
3. Hora extra 100%: horas extras em domingos e feriados = (salário/220) x 2,0
4. Adicional noturno rural: 25% sobre hora noturna (20h às 4h)
5. Insalubridade: 10%, 20% ou 40% sobre salário mínimo conforme grau
6. DSR: (salário mensal / dias úteis do mês) x domingos e feriados — descontado se falta injustificada na semana
7. INSS: tabela progressiva vigente (7,5% a 14%) até teto
8. IRRF: tabela progressiva vigente após dedução de INSS e dependentes
9. Vale-transporte: desconto de até 6% do salário base (se fornecido)
10. Moradia rural: se fornecida, pode descontar até 25% do salário (CLT art. 458)
11. Alimentação in natura: não integra salário se fornecida conforme PAT
12. FGTS: 8% sobre remuneração bruta (informativo — depósito via GRRF)
13. 13º salário: proporcional aos meses trabalhados no ano
14. Férias: salário + 1/3 constitucional

## Entidades de Dados Principais

- **FolhaMensal:** id, fazenda_id, tenant_id, mes_referencia, data_processamento, total_bruto, total_descontos, total_liquido, total_fgts, status (rascunho/processada/paga/exportada), processado_por, created_at
- **FolhaColaborador:** id, folha_mensal_id, colaborador_id, salario_base, horas_extras_50_valor, horas_extras_100_valor, adicional_noturno, insalubridade, dsr, outros_proventos, salario_bruto, inss, irrf, vale_transporte_desconto, outros_descontos, salario_liquido, fgts, observacoes
- **Holerite:** id, folha_colaborador_id, arquivo_pdf_url, enviado_colaborador, data_envio

## Integrações Necessárias

- **Cadastro de Colaboradores (essencial):** dados salariais e de contrato
- **Controle de Presença (essencial):** horas trabalhadas, extras, noturnas e faltas
- **Despesas (financeiro):** lançamento de despesa com pessoal
- **eSocial (enterprise):** eventos de remuneração (S-1200)
- **Banco (externa):** arquivo de pagamento em lote (CNAB 240)

## Fluxo de Uso Principal (step-by-step)

1. RH acessa Pessoas > Folha de Pagamento
2. Seleciona mês de referência e fazenda
3. Verifica se ponto do mês está fechado (pré-requisito)
4. Clica em "Processar Folha"
5. Sistema importa horas do ponto e calcula proventos por colaborador
6. Sistema aplica descontos legais (INSS, IRRF) conforme tabelas vigentes
7. Sistema calcula FGTS (informativo)
8. RH revisa folha — pode ajustar valores extras (adiantamentos, bônus, descontos)
9. Confirma processamento — status muda para "Processada"
10. Gera holerites individuais em PDF
11. Holerites podem ser enviados por e-mail ao colaborador
12. Dados são exportados para o contador (planilha ou integração)
13. Após pagamento efetivo, marca folha como "Paga"

## Casos Extremos e Exceções

- **Admissão no meio do mês:** salário proporcional aos dias trabalhados
- **Desligamento no mês:** calcular saldo de salário, férias proporcionais, 13º proporcional, aviso prévio
- **Colaborador afastado (INSS):** primeiros 15 dias pagos pelo empregador, depois INSS
- **Férias no mês:** calcular férias + 1/3 separadamente
- **Adiantamento salarial (vale):** descontar no fechamento da folha
- **Pensão alimentícia:** desconto conforme determinação judicial
- **Mudança de salário no meio do mês:** proporcionalizar
- **Tabela INSS/IRRF atualizada:** sistema deve permitir atualização das tabelas sem deploy
- **Colaborador sem ponto fechado:** bloquear inclusão na folha até regularização

## Critérios de Aceite (Definition of Done)

- [ ] Cálculo correto de proventos (salário, horas extras, adicional noturno, DSR)
- [ ] Cálculo correto de descontos (INSS, IRRF, VT, outros)
- [ ] Tabelas de INSS e IRRF configuráveis e atualizáveis
- [ ] Geração de holerite em PDF por colaborador
- [ ] Resumo da folha com totalizadores
- [ ] Cálculo de FGTS informativo
- [ ] Integração com dados do ponto mensal
- [ ] Fluxo de processamento com revisão e confirmação
- [ ] Exportação de dados para contador (CSV/Excel)
- [ ] Cálculo proporcional para admissão/desligamento no mês
- [ ] Isolamento por tenant e fazenda
- [ ] Testes com cenários reais de cálculo

## Sugestões de Melhoria Futura

- Geração de guia de FGTS (GRRF) automatizada
- Geração de DARF para recolhimento de IRRF
- Integração com internet banking para pagamento em lote (CNAB 240)
- Cálculo automático de rescisão trabalhista completa
- Simulador de custo de contratação (CLT vs. temporário vs. PJ)
- Provisão automática de férias e 13º no financeiro
