---
modulo: Pessoas e RH
submodulo: Cadastro de Colaboradores
nivel: essencial
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos: []
standalone: true
complexidade: M
assinante_alvo:
  - Pequeno produtor rural
  - Médio produtor rural
  - Agricultor familiar
---

# Cadastro de Colaboradores

## Descrição Funcional

Cadastro centralizado de todos os colaboradores da fazenda. Armazena dados pessoais (nome, CPF, RG, data de nascimento, endereço), dados profissionais (função, data de admissão, salário, tipo de contrato), documentos digitalizados (CTPS, ASO, certificados) e dados bancários para pagamento. Serve como base para todos os demais submódulos de Pessoas e RH.

## Personas — Quem usa este submódulo

- **Produtor rural/proprietário:** Cadastra funcionários, consulta dados
- **Gerente de fazenda:** Gerencia equipe, consulta dados de colaboradores
- **RH/Administrativo:** Mantém cadastro atualizado, digitaliza documentos
- **Contador:** Consulta dados para folha de pagamento e obrigações trabalhistas

## Dores que resolve

- Dados de funcionários em cadernos e pastas físicas — risco de perda e desorganização
- Falta de controle sobre vencimento de ASO, contratos e experiência
- Dificuldade de localizar documentos rapidamente (CTPS, certificados)
- Retrabalho ao informar dados do funcionário para contador, sindicato, governo
- Desconhecimento de quem trabalha em qual fazenda (multi-fazenda)

## Regras de Negócio

1. CPF deve ser único por tenant — não permite duplicar colaborador
2. CPF deve ser validado (dígitos verificadores)
3. Campos obrigatórios mínimos: nome completo, CPF, data de nascimento, função, data de admissão
4. Tipo de contrato: CLT, Temporário/Safrista, Diarista, Parceiro/Meeiro, Estagiário
5. Colaborador pode estar alocado em uma ou mais fazendas do mesmo tenant
6. Status: Ativo, Afastado, Férias, Desligado
7. Desligamento registra data, motivo e tipo (pedido de demissão, dispensa sem justa causa, etc.)
8. Colaborador desligado não pode ser excluído — mantém histórico por obrigação legal (5 anos CLT, 30 anos FGTS)
9. ASO (Atestado de Saúde Ocupacional) deve ter data de validade — alerta quando próximo ao vencimento
10. Foto do colaborador é opcional mas recomendada para identificação
11. Dados bancários são criptografados em repouso

## Entidades de Dados Principais

- **Colaborador:** id, fazenda_id, tenant_id, nome_completo, cpf, rg, data_nascimento, sexo, estado_civil, endereco_completo, cidade, uf, cep, telefone, email, funcao, cargo, setor, tipo_contrato, data_admissao, data_desligamento, motivo_desligamento, salario_base, banco, agencia, conta, tipo_conta, pix, foto_url, status, observacoes, created_at, updated_at
- **ColaboradorDocumento:** id, colaborador_id, tipo_documento (ctps/rg/cpf/aso/certificado/outros), numero, data_emissao, data_validade, arquivo_url, observacoes
- **ColaboradorFazenda:** id, colaborador_id, fazenda_id, funcao_na_fazenda, data_inicio, data_fim, ativo
- **ColaboradorDependente:** id, colaborador_id, nome, parentesco, cpf, data_nascimento

## Integrações Necessárias

- **Controle de Presença (essencial):** colaborador vinculado ao ponto
- **EPI/Segurança (essencial):** colaborador recebe EPIs
- **Folha Simplificada (profissional):** dados para cálculo de folha
- **Treinamentos (profissional):** colaborador participa de treinamentos
- **Escalas/Tarefas (profissional):** colaborador alocado em escalas
- **eSocial (enterprise):** envio de eventos de admissão, alteração, desligamento

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa Pessoas > Colaboradores > Novo Colaborador
2. Preenche dados pessoais: nome, CPF, data de nascimento, endereço
3. Preenche dados profissionais: função, tipo de contrato, data de admissão, salário
4. Preenche dados bancários para pagamento
5. Faz upload de documentos digitalizados (CTPS, RG, ASO)
6. Define em qual(is) fazenda(s) o colaborador atuará
7. Opcionalmente cadastra dependentes (para IR, vale-transporte, etc.)
8. Salva o cadastro — colaborador aparece na lista de ativos
9. Sistema gera alerta automático para vencimento de ASO e contratos
10. Ao desligar, registra data, motivo e tipo de desligamento — status muda para "Desligado"

## Casos Extremos e Exceções

- **Safrista readmitido:** mesmo CPF, nova admissão — criar novo registro vinculado ao anterior
- **Colaborador em múltiplas fazendas:** funções e alocações diferentes por fazenda
- **Menor aprendiz:** regras específicas de jornada e atividades (proibições NR-31)
- **Colaborador estrangeiro:** sem CPF inicialmente — usar documento de identidade estrangeiro
- **Transferência entre fazendas:** encerrar alocação na origem e abrir na destino
- **ASO vencido:** alerta bloqueante — colaborador irregular para trabalho
- **Dados bancários inválidos:** validação de banco, agência e conta antes de pagamento
- **LGPD:** dados pessoais sensíveis — controle de acesso e consentimento

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo com validação de CPF e campos obrigatórios
- [ ] Upload e gestão de documentos digitalizados
- [ ] Alocação de colaborador em múltiplas fazendas
- [ ] Fluxo de desligamento com registro de motivo
- [ ] Alertas de vencimento de ASO e contratos
- [ ] Busca e filtros por nome, CPF, função, status e fazenda
- [ ] Dados bancários criptografados em repouso
- [ ] Cadastro de dependentes
- [ ] Soft delete (colaborador desligado mantido no histórico)
- [ ] Isolamento por tenant
- [ ] Testes de integração e multi-tenant

## Sugestões de Melhoria Futura

- Integração com consulta de CPF (ReceitaWS) para preenchimento automático
- Reconhecimento de documentos via OCR (digitalização inteligente)
- Prontuário digital do colaborador com timeline de eventos
- App mobile para o colaborador consultar seus dados e holerites
- Portal de admissão digital (colaborador preenche próprios dados)
- Integração com relógio de ponto biométrico para foto automática
