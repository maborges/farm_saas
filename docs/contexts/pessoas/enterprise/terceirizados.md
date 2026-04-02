---
modulo: Pessoas e RH
submodulo: Terceirizados
nivel: enterprise
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-colaboradores.md
  - ../essencial/epi-seguranca.md
  - ../profissional/treinamentos.md
  - ../../financeiro/essencial/despesas.md
standalone: false
complexidade: L
assinante_alvo:
  - Grande produtor rural
  - Cooperativas
  - Agroindústrias
  - Usinas
---

# Gestão de Terceirizados

## Descrição Funcional

Gestão completa de prestadores de serviço, empresas terceirizadas e safristas (trabalhadores temporários de safra). Controla contratos de prestação de serviço, documentação das empresas (CNPJ, certidões negativas, seguros), cadastro de trabalhadores terceirizados em atividade na fazenda, conformidade de segurança (NRs, EPIs, ASOs) e custos. Essencial para mitigar risco de responsabilidade solidária/subsidiária trabalhista e previdenciária.

## Personas — Quem usa este submódulo

- **Gerente de fazenda:** Contrata e supervisiona prestadores de serviço
- **RH/Administrativo:** Gerencia documentação e conformidade de terceirizados
- **Jurídico:** Monitora risco trabalhista de terceirização
- **Financeiro:** Controla custos e pagamentos a prestadores
- **Técnico de segurança:** Verifica conformidade de NRs dos terceirizados

## Dores que resolve

- Risco de responsabilidade solidária/subsidiária por irregularidades do terceirizado
- Falta de controle sobre quem está na fazenda (terceirizados sem registro)
- Documentação de empresas terceirizadas desatualizada (certidões vencidas)
- Terceirizados sem EPI ou treinamento adequado — risco de acidente e autuação
- Safristas contratados informalmente — passivo trabalhista
- Dificuldade de controlar custo total de mão de obra terceirizada

## Regras de Negócio

1. Empresa terceirizada deve ter CNPJ ativo e documentação válida
2. Documentação obrigatória da empresa: CNPJ, contrato social, certidão negativa de débitos trabalhistas (CNDT), CND FGTS, CND INSS, seguro de responsabilidade civil
3. Documentação deve ser renovada conforme validade — alerta de vencimento
4. Trabalhador terceirizado na fazenda deve ter: nome, CPF, função, empresa, ASO válido
5. Terceirizado deve ter EPIs adequados à atividade (responsabilidade solidária)
6. Terceirizado em atividade de risco deve ter treinamento NR válido
7. Contrato de prestação de serviço deve especificar: escopo, prazo, valor, obrigações trabalhistas
8. Responsabilidade subsidiária: tomador responde se prestador não pagar verbas trabalhistas
9. Safrista pode ser contratado por prazo determinado (Lei 5.889/73 + CLT art. 443)
10. Retenção de 11% INSS sobre nota fiscal de serviço (cessão de mão de obra)
11. Fiscalizar mensalmente: folha de pagamento, FGTS e INSS dos terceirizados (recomendação)

## Entidades de Dados Principais

- **EmpresaTerceirizada:** id, tenant_id, razao_social, cnpj, contato_nome, contato_telefone, contato_email, endereco, atividade_principal, ativa, observacoes, created_at, updated_at
- **DocumentoEmpresa:** id, empresa_id, tipo_documento (cndt/cnd_fgts/cnd_inss/contrato_social/seguro_rc/alvara/outros), numero, data_emissao, data_validade, arquivo_url, status (valido/vencido/pendente)
- **ContratoPrestacao:** id, empresa_id, fazenda_id, tenant_id, numero_contrato, objeto, data_inicio, data_fim, valor_mensal, valor_total, forma_pagamento, retencao_inss_percentual, status (vigente/encerrado/suspenso), arquivo_url
- **TrabalhadorTerceirizado:** id, empresa_id, fazenda_id, tenant_id, nome_completo, cpf, funcao, data_inicio, data_fim, aso_validade, treinamentos_validos, epi_conforme, ativo, observacoes
- **AvaliacaoPrestador:** id, empresa_id, tenant_id, periodo_referencia, qualidade_servico, pontualidade, seguranca, conformidade_documental, nota_geral, observacoes

## Integrações Necessárias

- **Cadastro de Colaboradores (essencial):** separar próprios de terceirizados em relatórios
- **EPI/Segurança (essencial):** conformidade de EPIs dos terceirizados
- **Treinamentos (profissional):** verificar treinamentos NR dos terceirizados
- **Despesas (financeiro):** custos de serviços terceirizados
- **NF-e (comercialização):** notas fiscais de serviço recebidas
- **Certidões online (externa):** consulta automática de validade de certidões

## Fluxo de Uso Principal (step-by-step)

1. Gerente identifica necessidade de serviço terceirizado (colheita, aplicação, transporte)
2. Acessa Pessoas > Terceirizados > Nova Empresa
3. Cadastra empresa com CNPJ e faz upload de documentação
4. Sistema verifica validade de certidões e alerta sobre pendências
5. Registra contrato de prestação de serviço com escopo e valores
6. Cadastra trabalhadores terceirizados que atuarão na fazenda
7. Verifica conformidade: ASO válido, EPIs, treinamentos NR
8. Trabalhadores conformes são liberados para atividade
9. Mensalmente, sistema alerta sobre documentos a vencer
10. Ao final do contrato, avalia prestador (qualidade, segurança, pontualidade)
11. Financeiro controla pagamentos e retenções (11% INSS)
12. Histórico completo mantido para auditoria e defesa trabalhista

## Casos Extremos e Exceções

- **Certidão negativa vencida:** alertar e recomendar suspensão até regularização
- **Terceirizado sem ASO:** não pode trabalhar — bloquear liberação
- **Acidente com terceirizado:** registrar ocorrência, empresa contratada emite CAT, tomador acompanha
- **Empresa terceirizada fecha/falência:** responsabilidade subsidiária ativada — documentar tudo
- **Safrista que alega vínculo empregatício:** manter registro detalhado do contrato temporário
- **Terceirizado em atividade-fim:** permitido por lei (Lei 13.429/2017) mas requer cuidados redobrados
- **Múltiplas empresas no mesmo serviço:** controlar separadamente, consolidar custos
- **Subcontratação:** empresa terceirizada subcontrata outra — exigir transparência

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de empresas terceirizadas com documentação
- [ ] Controle de validade de documentos com alertas de vencimento
- [ ] CRUD de contratos de prestação de serviço
- [ ] Cadastro de trabalhadores terceirizados com conformidade
- [ ] Verificação de ASO, EPIs e treinamentos NR
- [ ] Dashboard de conformidade documental (semáforo por empresa)
- [ ] Registro de avaliação de prestadores
- [ ] Cálculo de retenção INSS sobre notas fiscais
- [ ] Relatório de custo de terceirização por fazenda/serviço
- [ ] Isolamento por tenant
- [ ] Testes de integração

## Sugestões de Melhoria Futura

- Consulta automática de CNDT, CND FGTS e CND INSS via APIs governamentais
- Portal do terceirizado: empresa parceira faz upload de documentos direto no sistema
- Score de confiabilidade de prestadores baseado em avaliações históricas
- Marketplace de prestadores de serviço agro da região
- Integração com eSocial para eventos de terceirização (S-1060, S-2300)
- Checklist de due diligence trabalhista antes de contratar
