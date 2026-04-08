---
modulo: Frota e Máquinas
submodulo: Custo/Hora Máquina
nivel: profissional
core: false
dependencias_core: [Identidade e Acesso, Cadastro da Propriedade]
dependencias_modulos: [../essencial/cadastro-equipamentos.md, ../essencial/abastecimento.md, ../profissional/manutencao-preventiva.md]
standalone: false
complexidade: M
assinante_alvo: [medio produtor, grande produtor]
---

# Custo/Hora Maquina

## Descricao Funcional

Calcula o custo operacional por hora de cada equipamento, considerando combustivel, manutencao, depreciacao, seguro e mao de obra do operador. Permite alocar custos de maquinas a talhoes e operacoes agricolas especificas, fornecendo visibilidade real do custo de producao por area.

## Personas

- **Gestor de frota:** analisa custo/hora e identifica equipamentos ineficientes
- **Gestor agricola:** aloca custos de mecanizacao por talhao/safra
- **Financeiro:** consolida custos operacionais no orcamento
- **Proprietario:** decide sobre compra, venda ou terceirizacao de servicos

## Dores que resolve

- Desconhecimento do custo real de operar cada maquina
- Impossibilidade de comparar custo proprio vs. terceirizado
- Falta de alocacao de custos de mecanizacao por talhao/cultura
- Decisoes de investimento sem dados de depreciacao e TCO

## Regras de Negocio

1. Custo/hora = (combustivel + manutencao + depreciacao + seguro + operador) / horas_trabalhadas
2. Combustivel: consumo medio (L/h) * preco medio do combustivel no periodo
3. Manutencao: soma de OS concluidas no periodo / horas trabalhadas no periodo
4. Depreciacao: (valor_aquisicao - valor_residual) / vida_util_estimada_horas
5. Seguro: valor anual do seguro / horas estimadas por ano
6. Operador: custo/hora do operador alocado
7. Alocacao por talhao: horas registradas em cada talhao * custo/hora do equipamento
8. Periodo de calculo configuravel (mensal, trimestral, safra)
9. Recalculo automatico sempre que novos abastecimentos ou OS sao registrados

## Entidades de Dados Principais

- **EquipamentoCustoConfig:** id, tenant_id, equipamento_id, valor_aquisicao, valor_residual, vida_util_horas, custo_seguro_anual, horas_estimadas_ano, custo_operador_hora
- **CustoHoraCalculado:** id, tenant_id, equipamento_id, periodo_inicio, periodo_fim, custo_combustivel_hora, custo_manutencao_hora, custo_depreciacao_hora, custo_seguro_hora, custo_operador_hora, custo_total_hora
- **AlocacaoEquipamento:** id, tenant_id, equipamento_id, talhao_id, operacao_id, data, horas_trabalhadas, custo_total_alocado

## Integracoes Necessarias

- **Abastecimento:** consumo medio e custo de combustivel
- **Manutencao Preventiva:** custos de OS no periodo
- **Cadastro de Equipamentos:** valor de aquisicao, horimetro
- **Agricola (Operacoes):** vincular horas a operacao e talhao
- **Financeiro:** lancamento de custo por centro de custo/talhao

## Fluxo de Uso Principal

1. Gestor configura parametros de custo do equipamento (valor aquisicao, vida util, etc.)
2. Sistema coleta automaticamente dados de abastecimento e manutencao
3. Ao final do periodo, sistema calcula custo/hora consolidado
4. Gestor agricola registra alocacao de horas por talhao/operacao
5. Sistema distribui custo proporcional as horas alocadas
6. Relatorio exibe custo/hora por equipamento e custo de mecanizacao por talhao

## Casos Extremos e Excecoes

- Equipamento novo sem historico de abastecimento: usar consumo estimado do fabricante
- Equipamento parado por longo periodo: depreciacao continua, custo/hora sobe (considerar horas efetivas vs calendario)
- Horimetro zerado (reset/troca): ajustar calculo com horimetro anterior + novo
- Equipamento compartilhado entre fazendas: ratear custo proporcionalmente
- Operacao sem talhao definido (transporte interno): alocar como custo indireto

## Criterios de Aceite

- [ ] Configuracao de parametros de custo por equipamento
- [ ] Calculo automatico de custo/hora com 5 componentes
- [ ] Alocacao de horas por talhao com custo proporcional
- [ ] Relatorio de custo/hora por equipamento e periodo
- [ ] Relatorio de custo de mecanizacao por talhao
- [ ] Recalculo automatico ao registrar abastecimento ou OS
- [ ] Isolamento por tenant

## Sugestoes de Melhoria Futura

- Comparativo custo proprio vs. preco de servico terceirizado
- Simulacao de cenarios (comprar novo equipamento vs. manter atual)
- Integracao com modulo financeiro para orcamento de mecanizacao
- Projecao de custos futuros com base em tendencias
