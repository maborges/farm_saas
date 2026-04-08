---
modulo: Frota e Máquinas
submodulo: Checklist Diário
nivel: essencial
core: false
dependencias_core: [Identidade e Acesso, Cadastro da Propriedade]
dependencias_modulos: [../essencial/cadastro-equipamentos.md]
standalone: true
complexidade: S
assinante_alvo: [pequeno produtor, medio produtor, grande produtor]
---

# Checklist Diario

## Descricao Funcional

Checklist pre-operacao obrigatorio que o operador deve preencher antes de utilizar qualquer equipamento. Cada tipo de equipamento possui um modelo de checklist configuravel com itens de verificacao (nivel de oleo, pneus, luzes, freios, etc.). O sistema bloqueia a alocacao do equipamento ate que o checklist seja concluido, garantindo seguranca e conformidade.

## Personas

- **Operador de maquina:** preenche o checklist antes de iniciar o turno
- **Gestor de frota:** configura modelos de checklist, monitora conformidade
- **Seguranca do trabalho:** audita historico de checklists para conformidade

## Dores que resolve

- Equipamentos operando sem inspecao previa, causando acidentes
- Falta de registro que comprove a verificacao diaria (responsabilidade legal)
- Problemas mecanicos detectados tarde demais por falta de inspecao
- Impossibilidade de rastrear quem operou o equipamento e em que condicoes

## Regras de Negocio

1. Cada tipo de equipamento pode ter um ou mais modelos de checklist
2. Checklist deve ser preenchido no inicio de cada turno/dia por equipamento
3. Itens podem ser: `CONFORME`, `NAO_CONFORME`, `NAO_APLICAVEL`
4. Se qualquer item critico estiver `NAO_CONFORME`, equipamento fica bloqueado para uso
5. Itens criticos sao configurados pelo gestor no modelo de checklist
6. Checklist preenchido e imutavel (nao pode ser editado apos submissao)
7. Registro deve conter: operador, equipamento, data/hora, localizacao (GPS opcional)
8. Gestor pode adicionar/remover itens do modelo a qualquer momento (nao afeta checklists ja preenchidos)

## Entidades de Dados Principais

- **ChecklistModelo:** id, tenant_id, nome, tipo_equipamento, ativo
- **ChecklistModeloItem:** id, modelo_id, descricao, critico (bool), ordem
- **ChecklistPreenchido:** id, tenant_id, equipamento_id, operador_id, data_hora, status_geral, observacao_geral
- **ChecklistPreenchidoItem:** id, checklist_preenchido_id, modelo_item_id, resultado, observacao, foto_url

## Integracoes Necessarias

- **Cadastro de Equipamentos:** referenciar equipamento, bloquear uso se NAO_CONFORME critico
- **Identidade e Acesso:** identificar operador logado
- **Manutencao Preventiva:** item NAO_CONFORME pode gerar OS automatica

## Fluxo de Uso Principal

1. Operador acessa Frota > Checklist Diario
2. Seleciona equipamento que vai operar
3. Sistema carrega modelo de checklist do tipo de equipamento
4. Operador marca cada item como CONFORME ou NAO_CONFORME
5. Para itens NAO_CONFORME, pode adicionar observacao e foto
6. Submete o checklist
7. Se todos os itens criticos estao CONFORME: equipamento liberado
8. Se algum item critico NAO_CONFORME: equipamento bloqueado, notificacao ao gestor

## Casos Extremos e Excecoes

- Equipamento sem modelo de checklist configurado: permitir uso com aviso, sem exigir checklist
- Operador tenta operar sem checklist do dia: sistema bloqueia e redireciona para checklist
- Dois operadores preenchem checklist para o mesmo equipamento no mesmo dia: ambos ficam registrados, ultimo determina status
- Modelo de checklist alterado entre o inicio e fim do preenchimento: usar versao que foi carregada
- Sem conexao de internet no campo: permitir preenchimento offline com sincronizacao posterior

## Criterios de Aceite

- [ ] CRUD de modelos de checklist com itens configuraveis
- [ ] Preenchimento de checklist com registro de operador e data/hora
- [ ] Bloqueio de equipamento quando item critico NAO_CONFORME
- [ ] Checklist imutavel apos submissao
- [ ] Notificacao ao gestor quando equipamento bloqueado
- [ ] Historico de checklists consultavel por equipamento e periodo
- [ ] Isolamento por tenant

## Sugestoes de Melhoria Futura

- Preenchimento offline via PWA com sincronizacao
- Assinatura digital do operador no checklist
- Dashboard de conformidade (% de checklists preenchidos por dia)
- Integracao com NR-12 para itens de seguranca obrigatorios
