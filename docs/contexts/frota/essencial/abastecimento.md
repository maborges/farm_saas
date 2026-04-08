---
modulo: Frota e Máquinas
submodulo: Abastecimento
nivel: essencial
core: false
dependencias_core: [Identidade e Acesso, Cadastro da Propriedade]
dependencias_modulos: [../essencial/cadastro-equipamentos.md]
standalone: true
complexidade: S
assinante_alvo: [pequeno produtor, medio produtor, grande produtor]
---

# Abastecimento

## Descricao Funcional

Registro de todos os abastecimentos realizados nos equipamentos da frota, com calculo automatico de consumo medio (litros/hora ou km/litro). Permite controlar gastos com combustivel, identificar equipamentos com consumo anormal e gerar relatorios por periodo, equipamento ou operador.

## Personas

- **Operador/Motorista:** registra o abastecimento no momento em que ocorre
- **Gestor de frota:** analisa consumo medio e identifica anomalias
- **Financeiro:** consulta gastos com combustivel por periodo

## Dores que resolve

- Sem controle de quanto combustivel cada maquina consome
- Impossibilidade de detectar furto ou vazamento de combustivel
- Dificuldade de projetar custos operacionais
- Falta de historico para comparar eficiencia entre equipamentos

## Regras de Negocio

1. Abastecimento deve referenciar um equipamento ativo do tenant
2. Leitura de horimetro/odometro no momento do abastecimento e obrigatoria
3. Horimetro/odometro informado deve ser >= ultimo registro do equipamento
4. Consumo medio calculado automaticamente: litros / (horimetro_atual - horimetro_anterior)
5. Tipos de combustivel: `DIESEL`, `DIESEL_S10`, `GASOLINA`, `ETANOL`, `ARLA32`
6. Se consumo medio desviar mais de 30% da media historica, gerar alerta
7. Valor total = quantidade * preco_unitario (validar consistencia)

## Entidades de Dados Principais

- **Abastecimento:** id, tenant_id, equipamento_id, data_hora, combustivel_tipo, quantidade_litros, preco_unitario, valor_total, horimetro_momento, odometro_momento, operador_id, posto_origem, observacao, consumo_medio_calculado

## Integracoes Necessarias

- **Cadastro de Equipamentos:** referencia ao equipamento e atualizacao de horimetro/odometro
- **Estoque:** baixa automatica do tanque de combustivel da fazenda (se aplicavel)
- **Financeiro:** lancamento de despesa automatica
- **Custo/Hora Maquina:** alimenta calculo de custo operacional

## Fluxo de Uso Principal

1. Operador acessa Frota > Abastecimento > Novo
2. Seleciona equipamento (ou escaneia QR Code)
3. Informa tipo de combustivel, quantidade, preco por litro
4. Informa leitura atual de horimetro/odometro
5. Sistema calcula valor total e consumo medio desde ultimo abastecimento
6. Se consumo estiver fora da faixa, exibe alerta visual
7. Operador confirma e salva
8. Horimetro/odometro do equipamento e atualizado automaticamente

## Casos Extremos e Excecoes

- Primeiro abastecimento de um equipamento: consumo medio nao pode ser calculado, armazenar como baseline
- Horimetro informado menor que o anterior: bloquear registro, sugerir verificacao
- Abastecimento parcial (tanque nao cheio): marcar flag `parcial` para ajustar calculo de consumo
- Abastecimento externo (posto de combustivel): campo `posto_origem` obrigatorio
- Dois abastecimentos no mesmo horimetro: permitir, somar quantidades no calculo

## Criterios de Aceite

- [ ] Registro de abastecimento com todos os campos obrigatorios
- [ ] Calculo automatico de consumo medio correto
- [ ] Alerta quando consumo desvia >30% da media
- [ ] Horimetro/odometro do equipamento atualizado apos registro
- [ ] Relatorio de abastecimentos por periodo e equipamento
- [ ] Isolamento por tenant

## Sugestoes de Melhoria Futura

- Registro via app mobile com foto do hodometro/bomba
- Integracao com bombas de combustivel (leitura automatica)
- Dashboard de consumo com graficos de tendencia
- Ranking de eficiencia entre equipamentos similares
