---
modulo: Frota e Máquinas
submodulo: Manutenção Preventiva
nivel: profissional
core: false
dependencias_core: [Identidade e Acesso, Cadastro da Propriedade]
dependencias_modulos: [../essencial/cadastro-equipamentos.md, ../essencial/checklist-diario.md]
standalone: true
complexidade: M
assinante_alvo: [medio produtor, grande produtor]
---

# Manutencao Preventiva

## Descricao Funcional

Gestao completa de manutencao preventiva da frota com planos configurados por horimetro/odometro ou intervalo de tempo. Gera ordens de servico (OS) automaticamente quando um equipamento atinge o limiar de manutencao. Mantem historico completo de todas as intervencoes, custos e pecas utilizadas.

## Personas

- **Gestor de frota:** configura planos de manutencao, acompanha OS pendentes
- **Mecanico:** recebe e executa OS, registra pecas e tempo
- **Financeiro:** acompanha custos de manutencao por equipamento
- **Proprietario:** visualiza indicadores de saude da frota

## Dores que resolve

- Manutencoes esquecidas que geram quebras caras e paradas nao programadas
- Falta de historico de manutencao para decisao de compra/venda
- Impossibilidade de controlar custos de manutencao por equipamento
- Dificuldade de planejar paradas de manutencao em periodos de menor demanda

## Regras de Negocio

1. Plano de manutencao define: tipo de servico, intervalo (horas ou km ou dias), pecas previstas
2. OS gerada automaticamente quando faltam 10% para atingir intervalo (ex: troca de oleo a cada 250h, alerta em 225h)
3. Status da OS: `ABERTA`, `EM_ANDAMENTO`, `AGUARDANDO_PECA`, `CONCLUIDA`, `CANCELADA`
4. Ao abrir OS, equipamento muda status para `EM_MANUTENCAO` automaticamente
5. Ao concluir OS, horimetro/odometro do momento e registrado e contador do plano e reiniciado
6. OS pode ser preventiva (gerada pelo plano) ou corretiva (criada manualmente)
7. Custo da OS = soma de pecas + mao de obra (horas * valor/hora do mecanico)
8. Manutencao corretiva originada de checklist NAO_CONFORME deve referenciar o checklist

## Entidades de Dados Principais

- **PlanoManutencao:** id, tenant_id, nome, tipo_equipamento, tipo_intervalo (HORAS/KM/DIAS), intervalo_valor, descricao_servico, ativo
- **PlanoManutencaoPeca:** id, plano_id, descricao_peca, quantidade, custo_estimado
- **OrdemServico:** id, tenant_id, equipamento_id, plano_id (nullable), tipo (PREVENTIVA/CORRETIVA), status, data_abertura, data_conclusao, horimetro_abertura, horimetro_conclusao, mecanico_id, descricao, custo_total, checklist_origem_id (nullable)
- **OrdemServicoPeca:** id, os_id, descricao, quantidade, custo_unitario
- **OrdemServicoMaoObra:** id, os_id, mecanico_id, horas, valor_hora

## Integracoes Necessarias

- **Cadastro de Equipamentos:** leitura de horimetro/odometro, mudanca de status
- **Checklist Diario:** item NAO_CONFORME critico gera OS corretiva
- **Estoque:** baixa de pecas do estoque ao concluir OS
- **Financeiro:** lancamento de despesa de manutencao
- **Custo/Hora Maquina:** custo de manutencao compoe custo operacional

## Fluxo de Uso Principal

1. Gestor configura plano de manutencao (ex: troca de oleo a cada 250h)
2. Sistema monitora horimetro dos equipamentos
3. Ao atingir 90% do intervalo, gera OS preventiva automaticamente
4. Mecanico recebe notificacao, inicia OS (status EM_ANDAMENTO)
5. Equipamento fica com status EM_MANUTENCAO
6. Mecanico registra pecas utilizadas e horas trabalhadas
7. Ao concluir, informa horimetro atual e fecha a OS
8. Equipamento volta para status ATIVO, contador do plano reinicia

## Casos Extremos e Excecoes

- Equipamento atinge intervalo sem que OS anterior tenha sido concluida: gerar segunda OS com flag `ATRASADA`
- Plano de manutencao alterado: nao afetar OS ja abertas, aplicar a partir da proxima
- Peca nao disponivel em estoque: OS fica em `AGUARDANDO_PECA`, gera solicitacao de compra
- Mecanico externo (terceirizado): registrar como mao de obra sem vinculo de usuario
- Multiplos planos para o mesmo equipamento com intervalos diferentes: cada plano gera OS independente

## Criterios de Aceite

- [ ] CRUD de planos de manutencao com intervalo configuravel
- [ ] Geracao automatica de OS ao atingir 90% do intervalo
- [ ] Mudanca automatica de status do equipamento ao abrir/fechar OS
- [ ] Registro de pecas e mao de obra na OS com calculo de custo total
- [ ] Historico completo de OS por equipamento
- [ ] OS corretiva vinculada a checklist quando aplicavel
- [ ] Isolamento por tenant

## Sugestoes de Melhoria Futura

- Calendario visual de manutencoes programadas (Gantt)
- Previsao de custos de manutencao por periodo
- Integracao com fornecedores de pecas para cotacao automatica
- Analise de tendencia: frequencia de corretivas por equipamento
