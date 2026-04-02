# Sprint 3 - Backlog de Tarefas

**Sprint:** 3
**Período:** 2026-04-28 a 2026-05-09 (2 semanas)
**Tema:** Conciliação Bancária + App Mobile Offline
**Objetivo:** Implementar importação OFX, conciliação automática e setup do app mobile

---

## 📋 Tarefas da Sprint

### S3.T1 - Parser de OFX
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] OFX parseado corretamente
- [ ] Suporte a múltiplos bancos
- [ ] Transações mapeadas

**Checklist:**
- [ ] Estudar formato OFX 2.1.1
- [ ] Criar parser com regex
- [ ] Mapear transações (crédito/débito)
- [ ] Extrair: data, valor, descrição, tipo
- [ ] Testes com OFX reais

---

### S3.T2 - Importar extrato OFX (upload)
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Upload de arquivo OFX
- [ ] Validação de formato
- [ ] Transações salvas no banco

**Checklist:**
- [ ] Criar endpoint POST /upload-ofx
- [ ] Validar arquivo (mime type, extensão)
- [ ] Parse do OFX
- [ ] Salvar transações em tabela temporária
- [ ] Retornar resumo para conferência

---

### S3.T3 - Algoritmo de casamento automático
**Responsável:** Backend
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Casamento > 70%
- [ ] Critérios: valor, data, descrição
- [ ] Sugestões de casamento

**Checklist:**
- [ ] Definir regras de casamento
- [ ] Implementar matching por valor
- [ ] Implementar matching por descrição (fuzzy)
- [ ] Implementar matching por data (±3 dias)
- [ ] Calcular score de confiança
- [ ] Retornar sugestões

---

### S3.T4 - Interface de conferência
**Responsável:** Frontend
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Lista de transações do extrato
- [ ] Lançamentos do sistema para casar
- [ ] Interface de arrastar-e-soltar
- [ ] Aprovação em lote

**Checklist:**
- [ ] Criar tela de conciliação
- [ ] Exibir transações não casadas
- [ ] Exibir lançamentos pendentes
- [ ] Implementar drag-and-drop
- [ ] Botão aprovar conciliação
- [ ] Feedback visual

---

### S3.T5 - Integração Pluggy/Belvo (Open Banking)
**Responsável:** Backend
**Pontos:** 13
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Conta Pluggy/Belvo criada
- [ ] OAuth bancário funcionando
- [ ] Extrato buscado automaticamente

**Checklist:**
- [ ] Contratar Pluggy ou Belvo
- [ ] Configurar API credentials
- [ ] Implementar fluxo OAuth
- [ ] Buscar extrato via API
- [ ] Agendar busca diária (cron)
- [ ] Tratar erros de conexão

---

### S3.T6 - Setup React Native + Expo
**Responsável:** Mobile
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Projeto Expo criado
- [ ] Navegação configurada
- [ ] Estrutura de pastas definida

**Checklist:**
- [ ] Instalar Expo CLI
- [ ] Criar projeto: `npx create-expo-app`
- [ ] Configurar TypeScript
- [ ] Instalar dependências (navigation, expo-router)
- [ ] Criar estrutura de pastas
- [ ] Testar em simulador

---

### S3.T7 - Instalar Dexie.js (IndexedDB)
**Responsável:** Mobile
**Pontos:** 3
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Dexie instalado
- [ ] Schemas definidos
- [ ] CRUD funcionando

**Checklist:**
- [ ] Instalar dexie: `npm install dexie`
- [ ] Criar database helper
- [ ] Definir schemas (fazendas, talhoes, safras)
- [ ] Implementar métodos: get, set, update, delete
- [ ] Testar offline

---

### S3.T8 - Implementar sync service
**Responsável:** Mobile
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Fila de operações pendentes
- [ ] Sincronização automática
- [ ] Resolução de conflitos

**Checklist:**
- [ ] Criar tabela de operações pendentes
- [ ] Implementar enqueue operation
- [ ] Implementar sync quando online
- [ ] Tratar conflitos (last-write-wins)
- [ ] Feedback de status de sync

---

### S3.T9 - Fila de operações pendentes (Backend)
**Responsável:** Backend
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Endpoint de sync
- [ ] Processamento em lote
- [ ] Retorno de conflitos

**Checklist:**
- [ ] Criar modelo OperacaoPendente
- [ ] Endpoint POST /sync
- [ ] Processar operações em lote
- [ ] Validar permissões
- [ ] Retornar resultados
- [ ] Log de auditoria

---

### S3.T10 - Frontend: Login no app
**Responsável:** Mobile
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Tela de login
- [ ] Autenticação JWT
- [ ] Armazenamento seguro de token

**Checklist:**
- [ ] Criar tela LoginScreen
- [ ] Formulário email/senha
- [ ] Chamar API de login
- [ ] Armazenar token (SecureStore)
- [ ] Navegar para home
- [ ] Persistir sessão

---

### S3.T11 - Testes offline
**Responsável:** QA
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] App funciona sem internet
- [ ] Operações salvas offline
- [ ] Sincronização ao reconectar

**Checklist:**
- [ ] Testar em modo avião
- [ ] Criar operações offline
- [ ] Verificar salvamento no IndexedDB
- [ ] Reconectar e verificar sync
- [ ] Testar conflitos
- [ ] Documentar bugs

---

## 📊 Burndown da Sprint

| Dia | Pontos Restantes |
|-----|-----------------|
| Dia 1 | 76 |
| Dia 2 | 65 |
| Dia 3 | 50 |
| Dia 4 | 35 |
| Dia 5 | 20 |
| Dia 6 | 10 |
| Dia 7 | 0 |
| Dia 8 | Buffer |
| Dia 9 | Buffer |
| Dia 10 | Revisão |

---

## 🎯 Definição de Pronto da Sprint

- [ ] OFX importado e parseado
- [ ] Conciliação automática > 70%
- [ ] App React Native configurado
- [ ] IndexedDB funcionando
- [ ] Sync offline/online
- [ ] Login no app
- [ ] Testes offline aprovados
- [ ] Code review aprovado
- [ ] Deploy em homologação

---

## 📝 Notas da Sprint

**Dependências:**
- NFP-e funcional (Sprint 2) ✅
- Contrato Pluggy/Belvo

**Riscos:**
- ⚠️ Complexidade do parser OFX (múltiplos formatos)
- ⚠️ App mobile requer aprendizado de React Native
- ⚠️ Open Banking pode ter limitações

**Mitigações:**
- Usar biblioteca ofxparse como base
- Pair programming para mobile
- Começar com OFX antes de Open Banking

---

**Scrum Master:** _______________________
**Product Owner:** _______________________
**Tech Lead:** _______________________

**Data de Início:** 2026-04-28
**Data de Fim:** 2026-05-09
