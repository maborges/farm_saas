# Sprint 1 - Backlog de Tarefas

**Sprint:** 1
**Período:** 2026-03-31 a 2026-04-11 (2 semanas)
**Tema:** NFP-e/NF-e - Configuração e XML
**Objetivo:** Configurar certificado digital e implementar geração de XML NFe 4.0

---

## 📋 Tarefas da Sprint

### ✅ S1.T1 - Configurar ambiente de desenvolvimento SEFAZ
**Responsável:** DevOps
**Pontos:** 3
**Status:** ⬜ A Fazer | 🔄 Fazendo | ✅ Concluído

**Critério de Aceite:**
- [ ] Homologação SEFAZ acessível
- [ ] Credenciais de teste configuradas
- [ ] Documentação de acesso salva

**Checklist:**
- [ ] Acessar portal SEFAZ do estado
- [ ] Solicitar credenciais de homologação
- [ ] Configurar URLs de produção/homologação
- [ ] Testar conexão com WebService
- [ ] Documentar no Notion/Confluence

---

### ✅ S1.T2 - Comprar certificado digital A1 (e-CNPJ)
**Responsável:** DevOps
**Pontos:** 2
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Certificado comprado
- [ ] Certificado instalado no servidor
- [ ] Senha armazenada no cofre

**Checklist:**
- [ ] Selecionar certificadora (Serasa, Certisign, etc.)
- [ ] Comprar certificado e-CNPJ A1
- [ ] Agendar videoconferência
- [ ] Instalar certificado
- [ ] Armazenar senha no AWS Secrets Manager

---

### ✅ S1.T3 - Instalar biblioteca pynfe
**Responsável:** Backend
**Pontos:** 1
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] pynfe instalado no requirements.txt
- [ ] Teste de importação funcionando

**Checklist:**
- [ ] Adicionar ao requirements.txt: `pynfe==0.4`
- [ ] Rodar `pip install -r requirements.txt`
- [ ] Criar teste de importação
- [ ] Documentar versão

---

### ✅ S1.T4 - Criar modelo NotaFiscal no banco
**Responsável:** Backend
**Pontos:** 3
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Migration criada
- [ ] Migration testada
- [ ] Modelo SQLAlchemy implementado

**Checklist:**
- [ ] Criar arquivo `services/api/financeiro/models/notas_fiscais.py`
- [ ] Definir classe `NotaFiscal`
- [ ] Criar migration Alembic
- [ ] Rodar migration em dev
- [ ] Testar CRUD básico

---

### ✅ S1.T5 - Criar schemas Pydantic (NFP-e, NF-e)
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Schemas de entrada criados
- [ ] Schemas de saída criados
- [ ] Validações implementadas

**Checklist:**
- [ ] Criar `schemas/nota_fiscal.py`
- [ ] Schema `NotaFiscalCreate`
- [ ] Schema `NotaFiscalResponse`
- [ ] Validações de campos obrigatórios
- [ ] Testes de validação

---

### ✅ S1.T6 - Implementar gerador de XML NFe 4.0
**Responsável:** Backend
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] XML válido gerado
- [ ] XML valida contra schema XSD
- [ ] Todos campos obrigatórios presentes

**Checklist:**
- [ ] Criar service `NFeXMLGenerator`
- [ ] Mapear modelo para XML
- [ ] Implementar `gerar_xml()`
- [ ] Validar com XSD da NFe 4.0
- [ ] Testes unitários

---

### ✅ S1.T7 - Criar testes unitários XML
**Responsável:** QA
**Pontos:** 3
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] 90% coverage
- [ ] Testes de campos obrigatórios
- [ ] Testes de validação

**Checklist:**
- [ ] Criar `tests/financeiro/test_nfe_xml.py`
- [ ] Testar geração de XML
- [ ] Testar validações
- [ ] Rodar coverage
- [ ] Atingir 90%+

---

### ✅ S1.T8 - Frontend: Tela de cadastro de nota
**Responsável:** Frontend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Formulário completo
- [ ] Validações de campo
- [ ] UX responsiva

**Checklist:**
- [ ] Criar página `/financeiro/notas-fiscais/nova`
- [ ] Campos: emitente, destinatário, produtos, valores
- [ ] Validações em tempo real
- [ ] Botão salvar
- [ ] Testes E2E

---

## 📊 Burndown da Sprint

| Dia | Pontos Restantes |
|-----|-----------------|
| Dia 1 | 30 |
| Dia 2 | 25 |
| Dia 3 | 20 |
| Dia 4 | 15 |
| Dia 5 | 10 |
| Dia 6 | 5 |
| Dia 7 | 0 |
| Dia 8 | Buffer |
| Dia 9 | Buffer |
| Dia 10 | Revisão |

---

## 🎯 Definição de Pronto da Sprint

- [ ] Todas as tarefas concluídas
- [ ] Todos os testes passando
- [ ] Code review aprovado
- [ ] Deploy em homologação
- [ ] Sprint review realizada

---

## 📝 Notas da Sprint

**Dependências:**
- Certificado digital precisa ser comprado antes da Sprint 2
- Credenciais SEFAZ necessárias para Sprint 2

**Riscos:**
- Atraso na emissão do certificado
- Dificuldade com documentação SEFAZ

**Mitigações:**
- Comprar certificado com urgência
- Contratar consultoria se necessário

---

**Scrum Master:** _______________________
**Product Owner:** _______________________
**Tech Lead:** _______________________

**Data de Início:** 2026-03-31
**Data de Fim:** 2026-04-11
