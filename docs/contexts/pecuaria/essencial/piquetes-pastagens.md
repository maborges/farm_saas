---
modulo: Pecuária
submodulo: Piquetes e Pastagens
nivel: essencial
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos:
  - ./cadastro-rebanho.md
standalone: false
complexidade: S
assinante_alvo:
  - pecuarista
  - gestor-rural
  - vaqueiro
---

# Piquetes e Pastagens

## Descrição Funcional

Submódulo de gestão das áreas de pastagem da fazenda. Permite cadastrar piquetes com informações de área (hectares), tipo de pasto (Brachiaria, Panicum, etc.), capacidade de lotação (UA/ha), status (ativo, em descanso, reformando) e histórico de ocupação. Controla a rotação de pastagens, alertando quando um piquete atinge o período máximo de ocupação e precisa descansar.

A visão consolidada mostra a taxa de lotação atual de cada piquete em relação à capacidade, permitindo decisões rápidas de manejo.

## Personas — Quem usa este submódulo

- **Gerente de Fazenda:** planejamento de rotação de pastagens, alocação de lotes
- **Vaqueiro:** execução de movimentações entre piquetes no dia a dia
- **Proprietário:** visão geral da utilização das pastagens
- **Agrônomo/Zootecnista:** avaliação de capacidade suporte e manejo de pastagem

## Dores que resolve

- Superlotação de piquetes levando à degradação do pasto
- Falta de controle do período de descanso das pastagens
- Desconhecimento da taxa de lotação real vs. ideal
- Ausência de histórico de ocupação para planejar reformas
- Dificuldade em planejar a rotação sem visualização consolidada

## Regras de Negócio

1. Cada piquete pertence a uma fazenda do tenant
2. Capacidade de lotação expressa em UA/ha (1 UA = 450 kg de peso vivo)
3. Taxa de lotação atual calculada pela soma de UA dos animais alocados / área
4. Status: Ativo, Em Descanso, Em Reforma, Inativo
5. Período de descanso configurável por tipo de pasto (padrão: 30 dias)
6. Alerta automático quando ocupação exceder 100% da capacidade
7. Alerta quando período máximo de ocupação contínua for atingido
8. Histórico de ocupação imutável: registra entrada e saída de cada lote

## Entidades de Dados Principais

- **Piquete:** id, tenant_id, fazenda_id, nome, area_hectares, tipo_pasto, capacidade_ua_ha, status, dias_max_ocupacao, dias_descanso, observacoes, created_at, updated_at
- **OcupacaoPiquete:** id, piquete_id, lote_id, data_entrada, data_saida, ua_total
- **TipoPasto:** id, tenant_id, nome, dias_descanso_padrao, capacidade_ua_ha_referencia

## Integrações Necessárias

- **Cadastro de Rebanho:** Lotes e animais alocados nos piquetes
- **Manejos Básicos:** Movimentações atualizam ocupação dos piquetes
- **Imóveis (opcional):** Vinculação de piquetes a talhões/glebas do cadastro imobiliário

## Fluxo de Uso Principal (step-by-step)

1. Acessar Pecuária > Piquetes
2. Cadastrar piquetes com nome, área, tipo de pasto e capacidade
3. Definir parâmetros de descanso e ocupação máxima
4. Alocar lotes nos piquetes (ou via manejo de movimentação)
5. Monitorar dashboard com taxa de lotação de cada piquete (semáforo: verde/amarelo/vermelho)
6. Receber alertas de superlotação ou necessidade de descanso
7. Registrar saída do lote e início do período de descanso
8. Consultar histórico de ocupação para planejamento de reformas

## Casos Extremos e Exceções

- **Piquete sem área definida:** Obrigatório; bloquear cadastro sem informar hectares
- **Dois lotes no mesmo piquete:** Permitido; somar UAs para cálculo de lotação
- **Piquete em reforma recebendo animais:** Bloquear com mensagem explicativa
- **Tipo de pasto misto:** Permitir texto descritivo; usar média dos parâmetros
- **Piquete com 0 UA de capacidade:** Bloquear; valor mínimo 0,1 UA/ha
- **Animal sem peso registrado:** Usar peso padrão da categoria para cálculo de UA

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de Piquete com isolamento por tenant
- [ ] Cálculo automático de taxa de lotação (UA atual / capacidade)
- [ ] Registro de ocupação com datas de entrada/saída
- [ ] Alertas de superlotação e período de descanso
- [ ] Dashboard visual com semáforo de lotação
- [ ] Integração com movimentações de manejos básicos
- [ ] Testes unitários para cálculo de UA e regras de lotação

## Sugestões de Melhoria Futura

- Mapa georreferenciado dos piquetes com visualização de lotação
- Integração com drones para avaliação de cobertura de pasto
- Índice NDVI para monitoramento remoto de qualidade da pastagem
- Recomendação automática de rotação via algoritmo de otimização
- Cálculo de capacidade suporte baseado em análise de solo
