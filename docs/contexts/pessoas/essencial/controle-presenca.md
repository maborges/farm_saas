---
modulo: Pessoas e RH
submodulo: Controle de Presença
nivel: essencial
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ./cadastro-colaboradores.md
standalone: false
complexidade: M
assinante_alvo:
  - Pequeno produtor rural
  - Médio produtor rural
  - Agricultor familiar
---

# Controle de Presença

## Descrição Funcional

Registro e controle de ponto (presença) dos colaboradores da fazenda. Permite registro manual de entrada, saída e intervalos, com controle de jornada diária e semanal. Calcula horas trabalhadas, horas extras, adicional noturno e faltas. Contempla as particularidades da jornada rural: trabalho por produção, jornada flexível conforme safra, intervalo intrajornada diferenciado e trabalho aos domingos em período de colheita.

## Personas — Quem usa este submódulo

- **Gerente de fazenda/Encarregado:** Registra ponto dos funcionários da sua equipe
- **Colaborador:** Consulta seu espelho de ponto e horas trabalhadas
- **RH/Administrativo:** Revisa, ajusta e fecha o ponto mensal
- **Contador:** Recebe espelho de ponto para cálculo de folha

## Dores que resolve

- Controle de ponto em caderno — ilegível, sem cálculos, fácil de perder
- Não saber quantas horas extras foram realizadas no mês
- Dificuldade de comprovar jornada em caso de ação trabalhista
- Falta de controle sobre faltas e atrasos
- Trabalho rural sem horário fixo dificulta acompanhamento

## Regras de Negócio

1. Ponto registra: data, hora de entrada, hora de saída para almoço, hora de retorno, hora de saída
2. Jornada padrão rural: 8h diárias, 44h semanais (CLT art. 7º + peculiaridades rurais)
3. Intervalo intrajornada mínimo: 1h para jornada > 6h (pode ser reduzido por convenção coletiva)
4. Horas extras: horas que excedem a jornada diária ou semanal — adicional mínimo de 50%
5. Adicional noturno rural: 25% sobre hora normal (20h às 4h, CLT art. 73 + Lei 5.889/73)
6. Hora noturna rural: 60 minutos (diferente do urbano que é 52:30)
7. DSR (Descanso Semanal Remunerado): preferencialmente domingo — pode ser alternado na rural
8. Falta justificada: atestado médico, falecimento familiar, casamento (CLT art. 473)
9. Falta injustificada: desconto no salário + perda do DSR da semana
10. Tolerância de atraso: até 10 minutos por dia sem desconto (CLT art. 58 §1º)
11. Banco de horas: se habilitado, horas extras compensam folgas futuras (acordo individual ou coletivo)
12. Ponto deve ser fechado mensalmente — após fechamento, alterações requerem justificativa

## Entidades de Dados Principais

- **RegistroPonto:** id, colaborador_id, fazenda_id, tenant_id, data, entrada_1, saida_1, entrada_2, saida_2, entrada_3, saida_3, horas_normais, horas_extras_50, horas_extras_100, horas_noturnas, tipo_dia (normal/falta_justificada/falta_injustificada/feriado/folga/ferias/atestado), justificativa, ajustado_por, ajuste_motivo, created_at, updated_at
- **FechamentoPonto:** id, fazenda_id, tenant_id, mes_referencia, data_fechamento, fechado_por, total_colaboradores, status (aberto/fechado/exportado)
- **BancoHoras:** id, colaborador_id, tenant_id, mes_referencia, horas_credito, horas_debito, saldo_acumulado

## Integrações Necessárias

- **Cadastro de Colaboradores (essencial):** lista de colaboradores ativos para registro de ponto
- **Folha Simplificada (profissional):** horas trabalhadas alimentam cálculo de folha
- **Escalas/Tarefas (profissional):** escala define jornada esperada para comparação
- **eSocial (enterprise):** eventos de jornada e afastamento
- **Financeiro (despesas):** custo de horas extras por centro de custo

## Fluxo de Uso Principal (step-by-step)

1. Encarregado acessa Pessoas > Controle de Presença
2. Seleciona a data (padrão: hoje)
3. Lista de colaboradores ativos da fazenda é exibida
4. Para cada colaborador, registra horários de entrada/saída (até 3 pares)
5. Sistema calcula automaticamente horas normais, extras e noturnas
6. Se houver falta, seleciona tipo (justificada/injustificada) e anexa justificativa
7. Ao final do mês, RH revisa todos os registros
8. Ajustes são feitos com justificativa obrigatória (auditável)
9. RH fecha o ponto do mês — sistema gera resumo
10. Espelho de ponto pode ser impresso por colaborador para assinatura
11. Dados fechados são enviados ao contador ou à folha simplificada

## Casos Extremos e Exceções

- **Colaborador sem registro no dia:** tratado como falta — gerente pode corrigir com justificativa
- **Jornada noturna contínua:** entrada às 20h, saída às 4h — ponto cruza meia-noite
- **Trabalho em feriado:** horas computadas como extras 100% (ou compensadas)
- **Atestado médico parcial:** colaborador trabalha meio período — registrar horas e atestado
- **Banco de horas negativo:** colaborador deve horas — desconto na rescisão se desligado
- **Jornada 12x36:** permitida por acordo — validar configuração de escala
- **Menor aprendiz:** jornada máxima de 6h — sistema deve limitar
- **Período de colheita:** jornada estendida autorizada por convenção — configurar limite

## Critérios de Aceite (Definition of Done)

- [ ] Registro de ponto com até 3 pares de entrada/saída por dia
- [ ] Cálculo automático de horas normais, extras (50% e 100%) e noturnas
- [ ] Registro de faltas (justificada/injustificada) com justificativa
- [ ] Tolerância de 10 minutos configurável
- [ ] Fechamento mensal com bloqueio de edição
- [ ] Espelho de ponto por colaborador (tela e impressão)
- [ ] Ajustes com justificativa obrigatória e log de auditoria
- [ ] Resumo mensal por colaborador (horas normais, extras, faltas, DSR)
- [ ] Banco de horas opcional com saldo acumulado
- [ ] Isolamento por tenant e fazenda
- [ ] Testes de integração

## Sugestões de Melhoria Futura

- Registro de ponto via app mobile com geolocalização (prova de local)
- Integração com relógio de ponto eletrônico/biométrico
- Reconhecimento facial para registro de ponto
- Alerta automático de horas extras excessivas (limite legal ou de custo)
- Relatório de absenteísmo por setor e período
- Integração com wearables para registro automático em campo
