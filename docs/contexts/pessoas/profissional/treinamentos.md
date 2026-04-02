---
modulo: Pessoas e RH
submodulo: Treinamentos
nivel: profissional
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-colaboradores.md
  - ../essencial/epi-seguranca.md
standalone: false
complexidade: M
assinante_alvo:
  - Médio produtor rural
  - Grande produtor rural
  - Cooperativas
---

# Treinamentos e Capacitação

## Descrição Funcional

Gestão de treinamentos, capacitações e certificações dos colaboradores da fazenda. Foco especial na NR-31 que exige treinamentos obrigatórios para atividades rurais de risco (aplicação de agrotóxicos, operação de máquinas, trabalho em altura, manejo de animais). Controla agenda de treinamentos, participações, certificados emitidos, validade e reciclagem. Garante conformidade legal e desenvolvimento da equipe.

## Personas — Quem usa este submódulo

- **Gerente de fazenda:** Planeja treinamentos necessários para a equipe
- **Técnico de segurança:** Define e ministra treinamentos obrigatórios de NR
- **RH/Administrativo:** Organiza agenda, registra participações, controla certificados
- **Colaborador:** Participa de treinamentos, consulta certificados
- **Auditor/Fiscal:** Verifica conformidade de treinamentos obrigatórios

## Dores que resolve

- Multas por falta de treinamento obrigatório (NR-31, NR-35, NR-12)
- Colaboradores operando máquinas ou aplicando defensivos sem capacitação formal
- Certificados de treinamento vencidos sem controle de reciclagem
- Dificuldade de comprovar treinamentos em caso de fiscalização ou acidente
- Falta de planejamento — treinamentos feitos apenas quando há autuação

## Regras de Negócio

1. Treinamentos NR-31 obrigatórios conforme atividade: aplicação de agrotóxicos (NR-31.8), operação de máquinas (NR-31.12), trabalho em altura, CIPA rural
2. Treinamento tem carga horária mínima definida pela NR aplicável
3. Certificado deve conter: nome do treinamento, carga horária, data, conteúdo programático, nome do instrutor, nome do participante
4. Certificados têm validade — reciclagem obrigatória conforme NR (ex: NR-31 a cada 2 anos)
5. Colaborador não pode exercer atividade de risco sem treinamento válido
6. Instrutor deve ter qualificação comprovada (registro ou habilitação)
7. Lista de presença é obrigatória com assinatura dos participantes
8. Treinamento admissional deve ser realizado antes do início das atividades de risco
9. Treinamento pode ser interno (ministrado na fazenda) ou externo (empresa contratada)
10. Custos de treinamento são registrados como investimento em pessoal

## Entidades de Dados Principais

- **Treinamento:** id, tenant_id, nome, descricao, tipo (obrigatorio_nr/capacitacao/reciclagem), nr_referencia, carga_horaria_minima, validade_meses, conteudo_programatico, created_at
- **TurmatreinTreinamento:** id, treinamento_id, fazenda_id, tenant_id, data_inicio, data_fim, local, instrutor_nome, instrutor_qualificacao, empresa_instrutora, custo, max_participantes, status (agendada/em_andamento/concluida/cancelada), observacoes
- **ParticipacaoTreinamento:** id, turma_id, colaborador_id, presente, nota_avaliacao, certificado_numero, certificado_url, data_validade_certificado, assinatura_url
- **AgendaReciclagem:** id, colaborador_id, treinamento_id, data_vencimento, status (pendente/agendada/concluida/vencida)

## Integrações Necessárias

- **Cadastro de Colaboradores (essencial):** lista de colaboradores e suas funções/atividades
- **EPI/Segurança (essencial):** treinamento de uso de EPI é obrigatório (NR-31.8)
- **Escalas/Tarefas (profissional):** bloquear atribuição de tarefa de risco sem treinamento válido
- **eSocial (enterprise):** evento de treinamento/capacitação (S-2245)
- **Financeiro (despesas):** custos de treinamentos externos

## Fluxo de Uso Principal (step-by-step)

1. RH ou técnico de segurança acessa Pessoas > Treinamentos
2. Dashboard exibe treinamentos obrigatórios pendentes e certificados a vencer
3. Para agendar treinamento: clica em "Nova Turma"
4. Seleciona o treinamento (ex: "NR-31 — Aplicação de Agrotóxicos")
5. Define data, local, instrutor e lista de participantes
6. Sistema verifica quais colaboradores precisam deste treinamento (função + vencimento)
7. Após realização, registra presença de cada participante
8. Gera certificados individuais com dados do treinamento
9. Upload de lista de presença assinada
10. Sistema calcula data de reciclagem e agenda alertas automáticos
11. Colaboradores com certificado válido ficam aptos para atividades de risco

## Casos Extremos e Exceções

- **Colaborador faltou ao treinamento:** reagendar — não pode exercer atividade sem certificado
- **Instrutor sem qualificação comprovada:** treinamento pode ser invalidado em fiscalização
- **Treinamento vencido durante período de safra:** reciclagem urgente ou afastar da atividade
- **Colaborador transferido de fazenda:** treinamentos acompanham o colaborador (são por CPF, não por fazenda)
- **Treinamento online/EAD:** permitido para alguns conteúdos, mas parte prática exige presencial
- **Colaborador analfabeto:** treinamento deve ser adaptado — registro por impressão digital
- **Treinamento cancelado:** reagendar automaticamente e notificar participantes
- **Novo requisito legal:** NR atualizada exige novo treinamento — identificar colaboradores afetados

## Critérios de Aceite (Definition of Done)

- [ ] Cadastro de treinamentos com NR de referência e carga horária
- [ ] Agendamento de turmas com instrutor e participantes
- [ ] Registro de presença por participante
- [ ] Geração de certificado individual em PDF
- [ ] Controle de validade com alerta de reciclagem (30, 15, 7 dias)
- [ ] Dashboard de conformidade (quem precisa de qual treinamento)
- [ ] Matriz de treinamentos obrigatórios por função/atividade
- [ ] Upload de lista de presença assinada
- [ ] Histórico completo de treinamentos por colaborador
- [ ] Isolamento por tenant
- [ ] Testes de integração

## Sugestões de Melhoria Futura

- Plataforma de treinamento EAD integrada (vídeos, quiz, certificação automática)
- Avaliação de eficácia do treinamento (teste pré e pós)
- Gamificação com ranking de colaboradores mais capacitados
- Integração com plataformas de treinamento externas (API)
- Relatório de gap de competências por equipe
- Certificado digital com QR Code para validação online
