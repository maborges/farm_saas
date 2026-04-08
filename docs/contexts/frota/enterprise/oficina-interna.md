---
modulo: Frota e Máquinas
submodulo: Oficina Interna
nivel: enterprise
core: false
dependencias_core: [Identidade e Acesso, Cadastro da Propriedade]
dependencias_modulos: [../essencial/cadastro-equipamentos.md, ../profissional/manutencao-preventiva.md]
standalone: false
complexidade: L
assinante_alvo: [grande produtor, cooperativa, empresa agricola]
---

# Oficina Interna

## Descricao Funcional

Gestao completa da oficina mecanica propria da fazenda, incluindo cadastro de mecanicos e suas especialidades, controle de estoque de pecas e insumos de manutencao, fila de servicos, alocacao de mecanicos a ordens de servico e controle de produtividade da oficina. Complementa o modulo de Manutencao Preventiva com capacidade de execucao interna.

## Personas

- **Chefe de oficina:** distribui OS entre mecanicos, gerencia fila de servicos
- **Mecanico:** recebe OS, registra execucao, solicita pecas
- **Almoxarife:** controla estoque de pecas, atende solicitacoes
- **Gestor de frota:** monitora produtividade da oficina e backlog

## Dores que resolve

- Falta de controle sobre a fila de servicos da oficina
- Pecas de manutencao sem controle de estoque (compras duplicadas, falta de pecas)
- Impossibilidade de medir produtividade dos mecanicos
- Desconhecimento do tempo medio de reparo por tipo de servico
- Alocacao ineficiente de mecanicos (uns sobrecarregados, outros ociosos)

## Regras de Negocio

1. Mecanico cadastrado com especialidades (motor, eletrica, hidraulica, pneus, etc.)
2. OS da fila e atribuida a mecanico com especialidade compativel
3. Prioridade de OS: `CRITICA` (equipamento parado na safra), `ALTA`, `NORMAL`, `BAIXA`
4. Mecanico nao pode ter mais de N OS simultaneas em andamento (configuravel, padrao 2)
5. Solicitacao de peca gera reserva no estoque; se indisponivel, gera pedido de compra
6. Estoque minimo de pecas criticas configuravel com alerta automatico
7. Tempo de servico registrado por OS para calculo de produtividade
8. OS concluida exige registro de pecas usadas e horas trabalhadas

## Entidades de Dados Principais

- **Mecanico:** id, tenant_id, usuario_id (nullable), nome, especialidades[], ativo, custo_hora
- **PecaEstoque:** id, tenant_id, codigo, descricao, unidade, quantidade_atual, estoque_minimo, localizacao_almoxarifado, custo_medio
- **MovimentacaoPeca:** id, peca_id, tipo (ENTRADA/SAIDA/RESERVA), quantidade, os_id (nullable), data_hora, responsavel_id, observacao
- **FilaServico:** id, tenant_id, os_id, mecanico_id (nullable), prioridade, posicao_fila, data_entrada_fila, prazo_estimado
- **RegistroTrabalho:** id, os_id, mecanico_id, data, hora_inicio, hora_fim, descricao_atividade

## Integracoes Necessarias

- **Manutencao Preventiva:** OS geradas alimentam a fila da oficina
- **Estoque (Operacional):** baixa de pecas do almoxarifado
- **Financeiro:** custo de pecas e mao de obra lancados como despesa
- **Compras:** pedido de compra quando peca indisponivel
- **Identidade e Acesso:** perfil de mecanico com permissoes especificas

## Fluxo de Uso Principal

1. OS e gerada (preventiva ou corretiva) e entra na fila da oficina
2. Chefe de oficina visualiza fila ordenada por prioridade
3. Atribui OS a mecanico com especialidade compativel e disponibilidade
4. Mecanico inicia OS, registra hora de inicio
5. Solicita pecas necessarias ao almoxarifado
6. Almoxarife separa e registra saida de pecas vinculada a OS
7. Mecanico conclui servico, registra hora de fim e descricao
8. Chefe de oficina valida e fecha a OS

## Casos Extremos e Excecoes

- Todos os mecanicos ocupados e OS critica chega: permitir realocar mecanico de OS de menor prioridade
- Peca sem estoque e fornecedor demora: OS fica em AGUARDANDO_PECA, mecanico liberado para outra OS
- Mecanico ausente (ferias/atestado): redistribuir OS pendentes automaticamente
- Servico terceirizado (peca enviada para retifica externa): registrar como etapa externa na OS
- Peca usada de outra OS devolvida: movimentacao de estorno

## Criterios de Aceite

- [ ] CRUD de mecanicos com especialidades
- [ ] CRUD de pecas com estoque minimo e alerta
- [ ] Fila de servicos ordenada por prioridade
- [ ] Atribuicao de OS a mecanico com validacao de especialidade
- [ ] Registro de trabalho com hora inicio/fim
- [ ] Movimentacao de pecas vinculada a OS
- [ ] Alerta de estoque minimo para pecas criticas
- [ ] Relatorio de produtividade por mecanico
- [ ] Isolamento por tenant

## Sugestoes de Melhoria Futura

- Kanban visual da fila de servicos
- App mobile para mecanico registrar servico em tempo real
- Historico de pecas por equipamento (quais pecas mais trocadas)
- Integracao com catalogo de pecas do fabricante
- Previsao de demanda de pecas baseada em historico
