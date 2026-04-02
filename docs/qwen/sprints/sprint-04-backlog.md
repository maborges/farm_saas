# Sprint 4 - Backlog de Tarefas

**Sprint:** 4
**Período:** 2026-05-12 a 2026-05-23 (2 semanas)
**Tema:** eSocial + LCDPR
**Objetivo:** Implementar eventos do eSocial e gerar LCDPR

---

## 📋 Tarefas da Sprint

### S4.T1 - Configurar certificado eSocial
**Responsável:** DevOps
**Pontos:** 3
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Certificado eSocial instalado
- [ ] Credenciais configuradas
- [ ] Ambiente de homologação acessível

**Checklist:**
- [ ] Comprar certificado eSocial (e-CNPJ)
- [ ] Credenciar no portal eSocial
- [ ] Obter credenciais de homologação
- [ ] Configurar no AWS Secrets Manager
- [ ] Testar conexão

---

### S4.T2 - Criar modelo Colaborador
**Responsável:** Backend
**Pontos:** 3
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Migration criada
- [ ] Modelo SQLAlchemy implementado
- [ ] Campos obrigatórios do eSocial

**Checklist:**
- [ ] Criar tabela `rh_colaboradores`
- [ ] Campos: nome, CPF, NIS, cargo, salário
- [ ] Dados de endereço completo
- [ ] Dados bancários (agência, conta)
- [ ] Vínculo empregatício

---

### S4.T3 - Criar schemas eSocial (S-2200)
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Schema Pydantic S-2200
- [ ] Validações de campos
- [ ] Estrutura conforme layout eSocial

**Checklist:**
- [ ] Estudar layout eSocial 2.4.02
- [ ] Criar schema `EventoS2200`
- [ ] Campos: trabalhador, vínculo, remuneração
- [ ] Validações de CPF, NIS, etc.
- [ ] Testes de validação

---

### S4.T4 - Implementar gerador XML S-2200
**Responsável:** Backend
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] XML no padrão eSocial
- [ ] Assinatura digital
- [ ] Validação XSD

**Checklist:**
- [ ] Criar classe `ESocialXMLGenerator`
- [ ] Implementar método `gerar_s2200()`
- [ ] Estrutura XML conforme manual
- [ ] Assinar XML
- [ ] Validar com XSD eSocial

---

### S4.T5 - Integrar WebService eSocial
**Responsável:** Backend
**Pontos:** 13
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Conexão estabelecida
- [ ] Evento transmitido
- [ ] Recibo obtido

**Checklist:**
- [ ] Mapear URLs eSocial (produção/homologação)
- [ ] Criar cliente SOAP
- [ ] Implementar `enviar_lote()`
- [ ] Implementar `consultar_recibo()`
- [ ] Tratar retornos (sucesso/erro)
- [ ] Log de eventos

---

### S4.T6 - Implementar evento S-1200 (Remuneração)
**Responsável:** Backend
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] XML S-1200 gerado
- [ ] Remuneração transmitida
- [ ] Protocolo obtido

**Checklist:**
- [ ] Criar schema `EventoS1200`
- [ ] Implementar `gerar_s1200()`
- [ ] Campos: matrícula, competências, rubricas
- [ ] Transmitir para eSocial
- [ ] Processar retorno

---

### S4.T7 - Implementar evento S-2300 (Temporário)
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] XML S-2300 gerado
- [ ] Trabalhador temporário cadastrado

**Checklist:**
- [ ] Criar schema `EventoS2300`
- [ ] Implementar `gerar_s2300()`
- [ ] Campos específicos de temporário
- [ ] Transmitir
- [ ] Testes

---

### S4.T8 - Implementar evento S-2299 (Desligamento)
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] XML S-2299 gerado
- [ ] Desligamento transmitido

**Checklist:**
- [ ] Criar schema `EventoS2299`
- [ ] Implementar `gerar_s2299()`
- [ ] Campos: data, motivo, verbas
- [ ] Transmitir
- [ ] Testes

---

### S4.T9 - Criar modelo FolhaPagamento
**Responsável:** Backend
**Pontos:** 3
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Migration criada
- [ ] Modelo implementado
- [ ] Cálculos básicos

**Checklist:**
- [ ] Criar tabela `rh_folha_pagamento`
- [ ] Campos: colaborador, competência, proventos, descontos
- [ ] Salário base, diárias, horas extras
- [ ] INSS, IRRF, FUNRURAL
- [ ] Líquido a pagar

---

### S4.T10 - Implementar cálculo FUNRURAL
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Alíquota correta (2.5%)
- [ ] Base de cálculo correta
- [ ] Integração com folha

**Checklist:**
- [ ] Estudar legislação FUNRURAL
- [ ] Implementar classe `FunRuralCalculator`
- [ ] Alíquota 2.5% sobre receita bruta
- [ ] Integração com folha de pagamento
- [ ] Testes de cálculo

---

### S4.T11 - Gerar recibos de pagamento (PDF)
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] PDF gerado
- [ ] Layout padrão
- [ ] Download disponível

**Checklist:**
- [ ] Usar reportlab ou fpdf2
- [ ] Template de recibo
- [ ] Campos: proventos, descontos, líquido
- [ ] Gerar PDF em base64
- [ ] Endpoint de download

---

### S4.T12 - Criar modelo LCDPR
**Responsável:** Backend
**Pontos:** 3
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Migration criada
- [ ] Modelo implementado

**Checklist:**
- [ ] Criar tabela `lcdpr`
- [ ] Campos: produtor, mês/ano, receitas, despesas
- [ ] Saldos (anterior, atual)
- [ ] Hash RFB
- [ ] XML gerado

---

### S4.T13 - Gerar XML LCDPR
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] XML no padrão RFB
- [ ] Assinado digitalmente
- [ ] Validação

**Checklist:**
- [ ] Estudar layout LCDPR
- [ ] Criar classe `LCDPRGenerator`
- [ ] Implementar `gerar_xml()`
- [ ] Assinar com certificado
- [ ] Validar

---

### S4.T14 - Frontend: Gestão de colaboradores
**Responsável:** Frontend
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] CRUD de colaboradores
- [ ] Validações de CPF, NIS
- [ ] Upload de documentos

**Checklist:**
- [ ] Criar página de colaboradores
- [ ] Formulário completo
- [ ] Lista com filtros
- [ ] Upload de documentos
- [ ] Testes E2E

---

### S4.T15 - Frontend: Folha de pagamento
**Responsável:** Frontend
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Tela de folha
- [ ] Cálculos automáticos
- [ ] Recibos em PDF

**Checklist:**
- [ ] Criar página de folha
- [ ] Lançar proventos/descontos
- [ ] Calcular líquido
- [ ] Gerar recibos
- [ ] Transmitir eSocial

---

### S4.T16 - Frontend: LCDPR
**Responsável:** Frontend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Tela de LCDPR
- [ ] Consolidação automática
- [ ] Exportação XML

**Checklist:**
- [ ] Criar página LCDPR
- [ ] Selecionar mês/ano
- [ ] Consolidar receitas/despesas
- [ ] Gerar XML
- [ ] Download

---

### S4.T17 - Testes eSocial
**Responsável:** QA
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Eventos transmitidos em homologação
- [ ] Recibos obtidos
- [ ] Coverage > 90%

**Checklist:**
- [ ] Testes de S-2200
- [ ] Testes de S-1200
- [ ] Testes de S-2300
- [ ] Testes de S-2299
- [ ] Medir coverage

---

### S4.T18 - Testes LCDPR
**Responsável:** QA
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] XML gerado
- [ ] Validação RFB
- [ ] Coverage > 90%

**Checklist:**
- [ ] Testes de geração
- [ ] Testes de validação
- [ ] Testes de assinatura
- [ ] Medir coverage

---

### S4.T19 - Documentar API eSocial
**Responsável:** Backend
**Pontos:** 2
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Swagger atualizado
- [ ] Exemplos de eventos
- [ ] Códigos de erro

**Checklist:**
- [ ] Documentar endpoints
- [ ] Adicionar exemplos
- [ ] Listar códigos de retorno
- [ ] Guia de integração

---

## 📊 Burndown da Sprint

| Dia | Pontos Restantes |
|-----|-----------------|
| Dia 1 | 111 |
| Dia 2 | 95 |
| Dia 3 | 75 |
| Dia 4 | 55 |
| Dia 5 | 35 |
| Dia 6 | 20 |
| Dia 7 | 10 |
| Dia 8 | Buffer |
| Dia 9 | Buffer |
| Dia 10 | Revisão |

---

## 🎯 Definição de Pronto da Sprint

- [ ] eSocial: S-2200 transmitido
- [ ] eSocial: S-1200 transmitido
- [ ] eSocial: S-2300 transmitido
- [ ] eSocial: S-2299 transmitido
- [ ] LCDPR: XML gerado
- [ ] Folha de pagamento: Calculada
- [ ] Recibos: PDF gerados
- [ ] Frontend: Telas prontas
- [ ] Testes: Coverage > 90%
- [ ] Documentação: Completa

---

## 📝 Notas da Sprint

**Dependências:**
- Certificado eSocial (comprar com antecedência)
- Credenciais de homologação

**Riscos:**
- ⚠️ Complexidade do layout eSocial
- ⚠️ Mudanças no layout
- ⚠️ Tempo de resposta do WebService

**Mitigações:**
- Usar biblioteca esocial (se disponível)
- Manter-se atualizado com notas técnicas
- Implementar retry e timeout

---

**Scrum Master:** _______________________
**Product Owner:** _______________________
**Tech Lead:** _______________________

**Data de Início:** 2026-05-12
**Data de Fim:** 2026-05-23
