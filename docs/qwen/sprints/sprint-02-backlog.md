# Sprint 2 - Backlog de Tarefas

**Sprint:** 2
**Período:** 2026-04-14 a 2026-04-25 (2 semanas)
**Tema:** NFP-e/NF-e - Transmissão SEFAZ
**Objetivo:** Assinar XML, transmitir para SEFAZ e gerar DANFE

---

## 📋 Tarefas da Sprint

### S2.T1 - Implementar assinatura digital A1
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer | 🔄 Fazendo | ✅ Concluído

**Critério de Aceite:**
- [ ] Certificado A1 carregado do secrets manager
- [ ] XML assinado com assinatura válida
- [ ] Assinatura no padrão ICP-Brasil

**Checklist:**
- [ ] Criar service `AssinaturaDigital`
- [ ] Carregar certificado do AWS Secrets Manager
- [ ] Implementar assinatura XML (RSA-SHA1)
- [ ] Assinar elemento `infNFe`
- [ ] Adicionar assinatura ao XML
- [ ] Testes de assinatura

---

### S2.T2 - Integrar WebService SEFAZ (produção)
**Responsável:** Backend
**Pontos:** 13
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Conexão estabelecida com SEFAZ
- [ ] WebService de homologação respondendo
- [ ] Tratamento de erros implementado

**Checklist:**
- [ ] Mapear URLs dos WebServices por estado
- [ ] Criar cliente SOAP para NFe
- [ ] Implementar método `recepcionar_lote`
- [ ] Tratar timeouts e retries
- [ ] Log de requisições/respostas
- [ ] Testes de conexão

---

### S2.T3 - Implementar transmissão de lote
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Lote transmitido com sucesso
- [ ] Número de recibo obtido
- [ ] Status do lote processado

**Checklist:**
- [ ] Criar estrutura de lote (1-50 notas)
- [ ] Montar envelope SOAP
- [ ] Transmitir para SEFAZ
- [ ] Obter número do recibo
- [ ] Atualizar status da nota
- [ ] Testes de transmissão

---

### S2.T4 - Processar retorno SEFAZ
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Retorno da SEFAZ parseado
- [ ] Status atualizado no banco
- [ ] Chave de acesso armazenada
- [ ] Erros tratados e logados

**Checklist:**
- [ ] Criar método `consultar_recibo`
- [ ] Parse do XML de retorno
- [ ] Extrair: status, chave, protocolo
- [ ] Atualizar modelo NotaFiscal
- [ ] Tratar rejeições (300+ códigos)
- [ ] Notificar usuário por email

---

### S2.T5 - Armazenar chave de acesso
**Responsável:** Backend
**Pontos:** 2
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Chave de acesso salva no banco
- [ ] Chave formatada para exibição
- [ ] URL de consulta gerada

**Checklist:**
- [ ] Atualizar campo `chave_acesso`
- [ ] Calcular dígito verificador
- [ ] Criar propriedade `chave_formatada`
- [ ] Gerar URL de consulta pública
- [ ] Testes de armazenamento

---

### S2.T6 - Gerar DANFE (PDF)
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] PDF no modelo oficial do DANFE
- [ ] Código de barras (Code128)
- [ ] QR Code para NFC-e
- [ ] PDF armazenado em base64

**Checklist:**
- [ ] Escolher biblioteca (reportlab ou fpdf2)
- [ ] Criar template do DANFE
- [ ] Implementar código de barras
- [ ] Adicionar QR Code (NFC-e)
- [ ] Gerar PDF em base64
- [ ] Armazenar no campo `xml_danfe`

---

### S2.T7 - Frontend: Tela de emissão
**Responsável:** Frontend
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Botão "Emitir Nota" funcional
- [ ] Status de transmissão exibido
- [ ] Visualização do DANFE
- [ ] Download do PDF

**Checklist:**
- [ ] Criar página de emissão
- [ ] Botão de transmitir
- [ ] Polling de status
- [ ] Exibir chave de acesso
- [ ] Download do DANFE
- [ ] Tratamento de erros

---

### S2.T8 - Frontend: Listar notas emitidas
**Responsável:** Frontend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Lista de notas com filtros
- [ ] Status colorido (autorizada, cancelada)
- [ ] Ações por nota (visualizar, cancelar)

**Checklist:**
- [ ] Criar tabela de notas
- [ ] Filtros: período, status, destinatário
- [ ] Paginação
- [ ] Badge de status
- [ ] Menu de ações
- [ ] Testes E2E

---

### S2.T9 - Testes de integração SEFAZ
**Responsável:** QA
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Nota autorizada em homologação
- [ ] Testes de erro (rejeições)
- [ ] Coverage > 90%

**Checklist:**
- [ ] Criar testes de transmissão
- [ ] Testar cenários de erro
- [ ] Validar com notas reais
- [ ] Medir coverage
- [ ] Documentar falhas conhecidas

---

### S2.T10 - Documentar API de emissão
**Responsável:** Backend
**Pontos:** 2
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Swagger atualizado
- [ ] Exemplos de requisição/resposta
- [ ] Documentação de erros

**Checklist:**
- [ ] Adicionar tags no router
- [ ] Documentar endpoints
- [ ] Adicionar exemplos
- [ ] Listar códigos de erro
- [ ] Revisar documentação

---

## 📊 Burndown da Sprint

| Dia | Pontos Restantes |
|-----|-----------------|
| Dia 1 | 58 |
| Dia 2 | 50 |
| Dia 3 | 40 |
| Dia 4 | 30 |
| Dia 5 | 20 |
| Dia 6 | 10 |
| Dia 7 | 0 |
| Dia 8 | Buffer |
| Dia 9 | Buffer |
| Dia 10 | Revisão |

---

## 🎯 Definição de Pronto da Sprint

- [ ] Todas as tarefas concluídas
- [ ] XML assinado e transmitido
- [ ] Nota autorizada pela SEFAZ
- [ ] DANFE gerado e disponível
- [ ] Testes de integração passando
- [ ] Code review aprovado
- [ ] Deploy em homologação
- [ ] Sprint review realizada

---

## 📝 Notas da Sprint

**Dependências:**
- Certificado digital instalado (Sprint 1)
- Credenciais SEFAZ ativas (Sprint 1)

**Riscos:**
- ⚠️ Complexidade do WebService SEFAZ
- ⚠️ Tempo de resposta lento da SEFAZ
- ⚠️ Mudanças no layout da NFe

**Mitigações:**
- Usar biblioteca pynfe como base
- Implementar retry com backoff exponencial
- Manter-se atualizado com notas técnicas

---

**Scrum Master:** _______________________
**Product Owner:** _______________________
**Tech Lead:** _______________________

**Data de Início:** 2026-04-14
**Data de Fim:** 2026-04-25
