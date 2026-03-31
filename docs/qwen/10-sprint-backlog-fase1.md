# Sprint Backlog - Fase 1: Fundação Crítica

**Versão:** 1.0.0
**Data:** 2026-03-31
**Status:** Aprovado para Execução

---

## 📅 Sprint 1 (Semana 1-2)
**Tema:** NFP-e/NF-e - Configuração e XML
**Objetivo:** Configurar certificado digital e implementar geração de XML NFe 4.0

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S1.T1 | Configurar ambiente de desenvolvimento SEFAZ | DevOps | 3 | DevOps | ⬜ | Homologação SEFAZ acessível |
| S1.T2 | Comprar certificado digital A1 (e-CNPJ) | DevOps | 2 | DevOps | ⬜ | Certificado instalado |
| S1.T3 | Instalar biblioteca pynfe | Backend | 1 | Backend | ⬜ | pip install pynfe |
| S1.T4 | Criar modelo NotaFiscal no banco | Backend | 3 | Backend | ⬜ | Migration criada e testada |
| S1.T5 | Criar schemas Pydantic (NFP-e, NF-e) | Backend | 5 | Backend | ⬜ | Validação funcionando |
| S1.T6 | Implementar gerador de XML NFe 4.0 | Backend | 8 | Backend | ⬜ | XML válido gerado |
| S1.T7 | Criar testes unitários XML | QA | 3 | QA | ⬜ | 90% coverage |
| S1.T8 | Frontend: Tela de cadastro de nota | Frontend | 5 | Frontend | ⬜ | Formulário completo |

**Definição de Pronto:**
- [ ] XML NFe 4.0 gerado e validado
- [ ] Schemas Pydantic testados
- [ ] Frontend de cadastro funcional

---

## 📅 Sprint 2 (Semana 3-4)
**Tema:** NFP-e/NF-e - Transmissão SEFAZ
**Objetivo:** Assinar XML, transmitir para SEFAZ e gerar DANFE

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S2.T1 | Implementar assinatura digital A1 | Backend | 5 | Backend | ⬜ | XML assinado válido |
| S2.T2 | Integrar WebService SEFAZ (produção) | Backend | 13 | Backend | ⬜ | Conexão estabelecida |
| S2.T3 | Implementar transmissão de lote | Backend | 5 | Backend | ⬜ | Lote transmitido |
| S2.T4 | Processar retorno SEFAZ | Backend | 5 | Backend | ⬜ | Status processado |
| S2.T5 | Armazenar chave de acesso | Backend | 2 | Backend | ⬜ | Chave salva no DB |
| S2.T6 | Gerar DANFE (PDF) | Backend | 5 | Backend | ⬜ | PDF gerado |
| S2.T7 | Frontend: Tela de emissão | Frontend | 8 | Frontend | ⬜ | Botão emitir funcional |
| S2.T8 | Frontend: Listar notas emitidas | Frontend | 5 | Frontend | ⬜ | Lista com status |
| S2.T9 | Testes de integração SEFAZ | QA | 8 | QA | ⬜ | Nota autorizada em homologação |
| S2.T10 | Documentar API de emissão | Backend | 2 | Backend | ⬜ | Swagger atualizado |

**Definição de Pronto:**
- [ ] Nota fiscal emitida e autorizada
- [ ] DANFE gerado e disponível para download
- [ ] Status da nota atualizado no sistema
- [ ] Testes em homologação SEFAZ aprovados

---

## 📅 Sprint 3 (Semana 5-6)
**Tema:** eSocial - Configuração e Eventos de Admissão
**Objetivo:** Configurar eSocial e implementar evento S-2200

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S3.T1 | Credenciar empresa no eSocial | DevOps | 5 | DevOps | ⬜ | Credenciamento aprovado |
| S3.T2 | Configurar certificado eSocial | DevOps | 3 | DevOps | ⬜ | Certificado instalado |
| S3.T3 | Criar modelo Colaborador | Backend | 3 | Backend | ⬜ | Migration criada |
| S3.T4 | Criar schemas eSocial (S-2200) | Backend | 5 | Backend | ⬜ | Validação funcionando |
| S3.T5 | Implementar gerador XML S-2200 | Backend | 8 | Backend | ⬜ | XML válido |
| S3.T6 | Assinar XML eSocial | Backend | 5 | Backend | ⬜ | XML assinado |
| S3.T7 | Integrar WebService eSocial | Backend | 8 | Backend | ⬜ | Conexão estabelecida |
| S3.T8 | Processar recibo eSocial | Backend | 3 | Backend | ⬜ | Recibo armazenado |
| S3.T9 | Frontend: Cadastro de colaborador | Frontend | 8 | Frontend | ⬜ | Formulário completo |
| S3.T10 | Frontend: Enviar admissão | Frontend | 5 | Frontend | ⬜ | Botão enviar funcional |
| S3.T11 | Testes eSocial | QA | 5 | QA | ⬜ | Evento enviado em produção |

**Definição de Pronto:**
- [ ] Evento S-2200 enviado e recebido
- [ ] Recibo eSocial armazenado
- [ ] Frontend de admissão funcional

---

## 📅 Sprint 4 (Semana 7-8)
**Tema:** eSocial - Folha e LCDPR
**Objetivo:** Implementar evento S-1200 e gerar LCDPR

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S4.T1 | Criar modelo FolhaPagamento | Backend | 3 | Backend | ⬜ | Migration criada |
| S4.T2 | Implementar cálculo salário rural | Backend | 5 | Backend | ⬜ | Cálculo correto |
| S4.T3 | Implementar cálculo FUNRURAL | Backend | 5 | Backend | ⬜ | Alíquota correta |
| S4.T4 | Gerar XML S-1200 (Remuneração) | Backend | 8 | Backend | ⬜ | XML válido |
| S4.T5 | Transmitir S-1200 | Backend | 5 | Backend | ⬜ | Evento enviado |
| S4.T6 | Implementar evento S-2300 (Temporário) | Backend | 5 | Backend | ⬜ | Evento funcional |
| S4.T7 | Implementar evento S-2299 (Desligamento) | Backend | 5 | Backend | ⬜ | Evento funcional |
| S4.T8 | Criar modelo LCDPR | Backend | 3 | Backend | ⬜ | Migration criada |
| S4.T9 | Gerar XML LCDPR | Backend | 5 | Backend | ⬜ | XML no padrão RFB |
| S4.T10 | Frontend: Gestão de folha | Frontend | 8 | Frontend | ⬜ | Tela completa |
| S4.T11 | Frontend: Gerar LCDPR | Frontend | 5 | Frontend | ⬜ | Botão gerar funcional |
| S4.T12 | Testes folha e LCDPR | QA | 5 | QA | ⬜ | Testes aprovados |

**Definição de Pronto:**
- [ ] Folha de pagamento calculada
- [ ] S-1200 enviado ao eSocial
- [ ] LCDPR gerado e disponível
- [ ] Recibos de pagamento em PDF

---

## 📅 Sprint 5 (Semana 9-10)
**Tema:** CAR - Importação e Cálculo de Áreas
**Objetivo:** Integrar SNA e calcular áreas do CAR

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S5.T1 | Estudar API do SNA (CAR) | Backend | 3 | Backend | ⬜ | Documentação lida |
| S5.T2 | Criar modelo CAR | Backend | 3 | Backend | ⬜ | Migration criada |
| S5.T3 | Implementar importação de recibo | Backend | 5 | Backend | ⬜ | Recibo parseado |
| S5.T4 | Integrar API SNA | Backend | 8 | Backend | ⬜ | API conectada |
| S5.T5 | Calcular área total (geoprocessamento) | GIS | 8 | GIS | ⬜ | Área correta |
| S5.T6 | Calcular área de APP | GIS | 8 | GIS | ⬜ | APP mapeada |
| S5.T7 | Calcular área de Reserva Legal | GIS | 8 | GIS | ⬜ | RL mapeada |
| S5.T8 | Verificar sobreposições (TI, UC) | GIS | 8 | GIS | ⬜ | Sobreposições detectadas |
| S5.T9 | Frontend: Importar CAR | Frontend | 5 | Frontend | ⬜ | Upload funcional |
| S5.T10 | Frontend: Dashboard de áreas | Frontend | 8 | Frontend | ⬜ | Gráficos exibidos |
| S5.T11 | Testes de importação | QA | 5 | QA | ⬜ | CAR importado |

**Definição de Pronto:**
- [ ] CAR importado do SNA
- [ ] Áreas calculadas (APP, RL, total)
- [ ] Sobreposições identificadas
- [ ] Dashboard visual funcionando

---

## 📅 Sprint 6 (Semana 11-12)
**Tema:** CAR - Monitoramento e Alertas
**Objetivo:** Implementar monitoramento de desmatamento via satélite

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S6.T1 | Integrar API Sentinel-2 | Backend | 8 | Backend | ⬜ | Imagens acessíveis |
| S6.T2 | Processar imagens de satélite | GIS | 13 | GIS | ⬜ | Imagem processada |
| S6.T3 | Detectar mudança de cobertura | GIS | 13 | GIS | ⬜ | Mudança detectada |
| S6.T4 | Calcular área desmatada | GIS | 5 | GIS | ⬜ | Área calculada |
| S6.T5 | Criar modelo MonitoramentoAPP | Backend | 3 | Backend | ⬜ | Migration criada |
| S6.T6 | Implementar alertas de desmatamento | Backend | 5 | Backend | ⬜ | Alerta gerado |
| S6.T7 | Frontend: Mapa de monitoramento | Frontend | 8 | Frontend | ⬜ | Mapa exibido |
| S6.T8 | Frontend: Histórico de alertas | Frontend | 5 | Frontend | ⬜ | Lista de alertas |
| S6.T9 | Configurar notificações por e-mail | Backend | 3 | Backend | ⬜ | E-mail enviado |
| S6.T10 | Testes de monitoramento | QA | 5 | QA | ⬜ | Alerta disparado |

**Definição de Pronto:**
- [ ] Imagens de satélite processadas
- [ ] Desmatamento detectado automaticamente
- [ ] Alertas enviados por e-mail
- [ ] Mapa de monitoramento visual

---

## 📅 Sprint 7 (Semana 13-14)
**Tema:** App Mobile Offline - Setup e Offline DB
**Objetivo:** Configurar React Native e implementar IndexedDB

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S7.T1 | Setup Expo + React Native | Mobile | 5 | Mobile | ⬜ | Projeto criado |
| S7.T2 | Configurar navegação (Expo Router) | Mobile | 5 | Mobile | ⬜ | Navegação funcional |
| S7.T3 | Instalar Dexie.js (IndexedDB) | Mobile | 3 | Mobile | ⬜ | Dexie configurado |
| S7.T4 | Criar schemas offline | Mobile | 5 | Mobile | ⬜ | Tabelas criadas |
| S7.T5 | Implementar sync service | Mobile | 8 | Mobile | ⬜ | Sync service pronto |
| S7.T6 | Criar fila de operações pendentes | Backend | 8 | Backend | ⬜ | Fila funcionando |
| S7.T7 | API de sincronização | Backend | 8 | Backend | ⬜ | Endpoint sync |
| S7.T8 | Frontend: Login no app | Mobile | 5 | Mobile | ⬜ | Login funcional |
| S7.T9 | Frontend: Dashboard offline | Mobile | 5 | Mobile | ⬜ | Dashboard visível |
| S7.T10 | Testes offline | QA | 8 | QA | ⬜ | App funciona sem internet |

**Definição de Pronto:**
- [ ] App React Native configurado
- [ ] IndexedDB funcionando
- [ ] Fila de operações pendentes
- [ ] Sync service implementado

---

## 📅 Sprint 8 (Semana 15-16)
**Tema:** App Mobile Offline - Operações de Campo
**Objetivo:** Implementar operações offline e sincronização

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S8.T1 | Offline: Listar fazendas | Mobile | 5 | Mobile | ⬜ | Lista carregada offline |
| S8.T2 | Offline: Listar talhões | Mobile | 5 | Mobile | ⬜ | Lista carregada offline |
| S8.T3 | Offline: Registrar operação | Mobile | 8 | Mobile | ⬜ | Operação salva offline |
| S8.T4 | Offline: Apontamentos de campo | Mobile | 8 | Mobile | ⬜ | Apontamento salvo |
| S8.T5 | Offline: Capturar fotos | Mobile | 5 | Mobile | ⬜ | Foto salva offline |
| S8.T6 | Sincronização automática (online) | Mobile | 13 | Mobile | ⬜ | Sync automático |
| S8.T7 | Resolver conflitos de sync | Backend | 8 | Backend | ⬜ | Conflitos tratados |
| S8.T8 | Frontend: Status de sincronização | Mobile | 3 | Mobile | ⬜ | Status visível |
| S8.T9 | Publicar TestFlight | Mobile | 3 | Mobile | ⬜ | App na TestFlight |
| S8.T10 | Publicar Play Console (beta) | Mobile | 3 | Mobile | ⬜ | App na Play Store |
| S8.T11 | Testes em campo | QA | 8 | QA | ⬜ | Testado sem internet |

**Definição de Pronto:**
- [ ] App funciona 100% offline
- [ ] Sincronização automática ao conectar
- [ ] Publicado nas lojas (beta)
- [ ] Testado em condições reais de campo

---

## 📅 Sprint 9 (Semana 17-18)
**Tema:** Conciliação Bancária - OFX
**Objetivo:** Implementar importação e parse de OFX

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S9.T1 | Estudar formato OFX | Backend | 2 | Backend | ⬜ | Formato compreendido |
| S9.T2 | Criar parser de OFX | Backend | 5 | Backend | ⬜ | OFX parseado |
| S9.T3 | Importar extrato OFX (upload) | Backend | 5 | Backend | ⬜ | Upload funcional |
| S9.T4 | Mapear transações OFX | Backend | 5 | Backend | ⬜ | Transações mapeadas |
| S9.T5 | Criar modelo LancamentoBancario | Backend | 3 | Backend | ⬜ | Migration criada |
| S9.T6 | Algoritmo de casamento automático | Backend | 8 | Backend | ⬜ | Casamento > 70% |
| S9.T7 | Frontend: Upload de OFX | Frontend | 5 | Frontend | ⬜ | Upload funcional |
| S9.T8 | Frontend: Conferir conciliação | Frontend | 8 | Frontend | ⬜ | Interface de conferência |
| S9.T9 | Frontend: Aprovar conciliação | Frontend | 5 | Frontend | ⬜ | Aprovação funcional |
| S9.T10 | Testes de conciliação | QA | 5 | QA | ⬜ | Conciliação aprovada |

**Definição de Pronto:**
- [ ] OFX importado e parseado
- [ ] Casamento automático funcionando
- [ ] Interface de conferência
- [ ] Conciliação aprovada salva

---

## 📅 Sprint 10 (Semana 19-20)
**Tema:** Conciliação Bancária - Open Banking
**Objetivo:** Integrar Open Banking para extrato automático

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S10.T1 | Contratar Pluggy ou Belvo | DevOps | 3 | DevOps | ⬜ | Contrato assinado |
| S10.T2 | Configurar API Pluggy | Backend | 5 | Backend | ⬜ | API configurada |
| S10.T3 | Implementar OAuth bancário | Backend | 8 | Backend | ⬜ | OAuth funcionando |
| S10.T4 | Buscar extrato automático | Backend | 8 | Backend | ⬜ | Extrato buscado |
| S10.T5 | Agendar busca diária | Backend | 3 | Backend | ⬜ | Cron configurado |
| S10.T6 | Atualizar conciliação automática | Backend | 5 | Backend | ⬜ | Conciliação atualizada |
| S10.T7 | Frontend: Conectar banco | Frontend | 8 | Frontend | ⬜ | Conexão funcional |
| S10.T8 | Frontend: Listar contas | Frontend | 5 | Frontend | ⬜ | Contas listadas |
| S10.T9 | Frontend: Extrato em tempo real | Frontend | 5 | Frontend | ⬜ | Extrato visível |
| S10.T10 | Testes Open Banking | QA | 5 | QA | ⬜ | Extrato atualizado |

**Definição de Pronto:**
- [ ] Open Banking integrado
- [ ] Extrato buscado automaticamente
- [ ] Conciliação atualizada diariamente
- [ ] Frontend de conexão bancária

---

## 📅 Sprint 11 (Semana 21-22)
**Tema:** Pecuária e RH Completo
**Objetivo:** Implementar reprodução animal e folha de pagamento

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S11.T1 | Criar modelo ProtocoloIATF | Pecuária | 3 | Backend | ⬜ | Migration criada |
| S11.T2 | Cadastrar protocolos (J-Sync, CoSynch) | Pecuária | 3 | Backend | ⬜ | Protocolos cadastrados |
| S11.T3 | Registrar IATF | Pecuária | 5 | Backend | ⬜ | IATF registrada |
| S11.T4 | Diagnóstico de prenhez | Pecuária | 5 | Backend | ⬜ | Diagnóstico registrado |
| S11.T5 | Multi-espécies (aves, suínos) | Pecuária | 13 | Backend | ⬜ | Espécies implementadas |
| S11.T6 | Lotes de aves (peso, conversão) | Pecuária | 8 | Backend | ⬜ | Lotes de aves |
| S11.T7 | Suínos (leitegada, ciclos) | Pecuária | 8 | Backend | ⬜ | Suínos implementados |
| S11.T8 | Calcular folha de pagamento | RH | 13 | Backend | ⬜ | Folha calculada |
| S11.T9 | Gerar recibos (PDF) | RH | 5 | RH | ⬜ | PDF gerado |
| S11.T10 | Frontend: Gestão de IATF | Frontend | 8 | Frontend | ⬜ | Tela completa |
| S11.T11 | Frontend: Folha de pagamento | Frontend | 8 | Frontend | ⬜ | Tela completa |
| S11.T12 | Testes pecuária e RH | QA | 5 | QA | ⬜ | Testes aprovados |

**Definição de Pronto:**
- [ ] IATF registrada e acompanhada
- [ ] Aves e suínos implementados
- [ ] Folha de pagamento calculada
- [ ] Recibos disponíveis

---

## 📅 Sprint 12 (Semana 23-24)
**Tema:** Estabilização e Preparação Fase 2
**Objetivo:** Bug fixes, performance e preparação para IA/IoT

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S12.T1 | Corrigir bugs reportados (Fiscal) | Backend | 8 | Backend | ⬜ | Bugs críticos resolvidos |
| S12.T2 | Corrigir bugs reportados (eSocial) | Backend | 5 | Backend | ⬜ | Bugs resolvidos |
| S12.T3 | Otimizar queries lentas | Backend | 8 | Backend | ⬜ | Queries < 200ms |
| S12.T4 | Adicionar índices no banco | Backend | 5 | Backend | ⬜ | Índices criados |
| S12.T5 | Configurar Redis cache | DevOps | 5 | DevOps | ⬜ | Cache funcionando |
| S12.T6 | Melhorar UX do app mobile | Mobile | 5 | Mobile | ⬜ | Feedback incorporado |
| S12.T7 | Documentar APIs (Swagger) | Backend | 3 | Backend | ⬜ | Swagger completo |
| S12.T8 | Treinar suporte (Fiscal) | Suporte | 5 | Suporte | ⬜ | Treinamento realizado |
| S12.T9 | Coletar feedback dos clientes | Produto | 5 | Produto | ⬜ | Feedback documentado |
| S12.T10 | Planejar Fase 2 (IA/IoT) | Todos | 3 | Todos | ⬜ | Planejamento aprovado |
| S12.T11 | Testes de carga | QA | 8 | QA | ⬜ | 1000 usuários simultâneos |
| S12.T12 | Bug bash (time todo) | Todos | 5 | Todos | ⬜ | Bugs encontrados e corrigidos |

**Definição de Pronto:**
- [ ] Bugs críticos resolvidos
- [ ] Performance otimizada
- [ ] Documentação completa
- [ ] Time treinado
- [ ] Fase 2 planejada

---

## 📊 Resumo da Fase 1

| Sprint | Pontos | Entregáveis Principais |
|--------|--------|----------------------|
| 1 | 30 | XML NFe 4.0, Schemas |
| 2 | 54 | NFP-e emitida, DANFE |
| 3 | 50 | eSocial S-2200 |
| 4 | 55 | Folha, LCDPR, S-1200 |
| 5 | 56 | CAR importado, áreas |
| 6 | 71 | Monitoramento desmatamento |
| 7 | 53 | App offline setup |
| 8 | 66 | App offline operações |
| 9 | 51 | Conciliação OFX |
| 10 | 50 | Open Banking |
| 11 | 81 | Pecuária, RH completo |
| 12 | 65 | Estabilização |
| **TOTAL** | **632** | **12 sprints** |

---

## 🎯 Critérios de Aceite da Fase 1

- [ ] NFP-e/NF-e emitida em produção
- [ ] eSocial enviando eventos S-2200 e S-1200
- [ ] LCDPR gerado e disponível
- [ ] CAR importado do SNA
- [ ] Alertas de desmatamento ativos
- [ ] App mobile publicado (iOS e Android)
- [ ] App funciona 100% offline
- [ ] Conciliação bancária automática
- [ ] Open Banking integrado
- [ ] Folha de pagamento rural calculada
- [ ] Pecuária (bovinos, aves, suínos) implementada

---

**Aprovado por:** _______________________
**Data:** ___/___/_____
**Scrum Master:** _______________________
**Product Owner:** _______________________
