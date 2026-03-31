# Sprint Backlog - Fase 2: Diferenciação Competitiva

**Versão:** 1.0.0
**Data:** 2026-03-31
**Status:** Aprovado para Execução

---

## 📅 Sprint 13 (Semana 25-26)
**Tema:** IA - Dataset e Treinamento
**Objetivo:** Coletar dataset de pragas/doenças e treinar modelo

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S13.T1 | Levantar datasets públicos (EMBRAPA) | ML | 5 | ML | ⬜ | Datasets listados |
| S13.T2 | Parceria EMBRAPA (coleta imagens) | Produto | 8 | Produto | ⬜ | Acordo assinado |
| S13.T3 | Coletar imagens de pragas (web scraping) | ML | 8 | ML | ⬜ | 1000+ imagens |
| S13.T4 | Coletar imagens de doenças | ML | 8 | ML | ⬜ | 1000+ imagens |
| S13.T5 | Rotular imagens (labeling) | ML | 13 | ML | ⬜ | 100% rotuladas |
| S13.T6 | Aumentar dataset (data augmentation) | ML | 5 | ML | ⬜ | 5000+ imagens |
| S13.T7 | Configurar ambiente ML (GPU) | DevOps | 5 | DevOps | ⬜ | Ambiente pronto |
| S13.T8 | Escolher arquitetura (EfficientNet) | ML | 3 | ML | ⬜ | Arquitetura definida |
| S13.T9 | Treinar modelo v1 | ML | 13 | ML | ⬜ | Modelo treinado |
| S13.T10 | Avaliar acurácia (>85%) | ML | 5 | ML | ⬜ | Métricas documentadas |
| S13.T11 | Frontend: Upload de imagem | Frontend | 5 | Frontend | ⬜ | Upload funcional |

**Definição de Pronto:**
- [ ] Dataset com 5000+ imagens rotuladas
- [ ] Modelo treinado com >85% acurácia
- [ ] Ambiente de inferência configurado

---

## 📅 Sprint 14 (Semana 27-28)
**Tema:** IA - API de Diagnóstico
**Objetivo:** Implementar API de inferência e app de captura

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S14.T1 | Criar endpoint de inferência | ML | 5 | ML | ⬜ | Endpoint funcional |
| S14.T2 | Otimizar modelo (TensorRT) | ML | 8 | ML | ⬜ | Inferência < 500ms |
| S14.T3 | Implementar batch inference | ML | 5 | ML | ⬜ | Batch funcionando |
| S14.T4 | Criar base de tratamentos | Backend | 8 | Backend | ⬜ | 50+ tratamentos |
| S14.T5 | Mapear praga → tratamento | Backend | 5 | Backend | ⬜ | Mapeamento completo |
| S14.T6 | API de recomendações | Backend | 5 | Backend | ⬜ | Recomendações geradas |
| S14.T7 | App: Capturar foto da folha | Mobile | 8 | Mobile | ⬜ | Câmera funcional |
| S14.T8 | App: Exibir diagnóstico | Mobile | 5 | Mobile | ⬜ | Diagnóstico visível |
| S14.T9 | App: Mostrar tratamento | Mobile | 5 | Mobile | ⬜ | Tratamento exibido |
| S14.T10 | Frontend: Dashboard de diagnósticos | Frontend | 5 | Frontend | ⬜ | Dashboard completo |
| S14.T11 | Testes de acurácia | QA | 8 | QA | ⬜ >85% acurácia |
| S14.T12 | Testes de usabilidade | QA | 5 | QA | ⬜ | Feedback positivo |

**Definição de Pronto:**
- [ ] API de diagnóstico em produção
- [ ] App captura e exibe diagnóstico
- [ ] Tratamentos recomendados
- [ ] Acurácia >85% em produção

---

## 📅 Sprint 15 (Semana 29-30)
**Tema:** IoT - John Deere Ops Center
**Objetivo:** Integrar API John Deere para dados de máquinas

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S15.T1 | Registrar app John Deere Developer | DevOps | 3 | DevOps | ⬜ | Registro aprovado |
| S15.T2 | Obter client_id e secret | DevOps | 2 | DevOps | ⬜ | Credenciais obtidas |
| S15.T3 | Implementar OAuth2 JD | Backend | 8 | Backend | ⬜ | OAuth funcionando |
| S15.T4 | Buscar lista de máquinas | Backend | 5 | Backend | ⬜ | Máquinas listadas |
| S15.T5 | Buscar dados da máquina (horas) | Backend | 8 | Backend | ⬜ | Dados obtidos |
| S15.T6 | Buscar localização GPS | Backend | 5 | Backend | ⬜ | GPS obtido |
| S15.T7 | Buscar operações de campo | Backend | 8 | Backend | ⬜ | Operações listadas |
| S15.T8 | Buscar dados de colheita | Backend | 8 | Backend | ⬜ | Yield data obtida |
| S15.T9 | Criar modelo TelemetriaMaquina | Backend | 3 | Backend | ⬜ | Migration criada |
| S15.T10 | Frontend: Conectar John Deere | Frontend | 8 | Frontend | ⬜ | Conexão funcional |
| S15.T11 | Frontend: Dashboard máquinas | Frontend | 8 | Frontend | ⬜ | Dashboard completo |
| S15.T12 | Frontend: Mapa de operações | Frontend | 8 | Frontend | ⬜ | Mapa exibido |
| S15.T13 | Testes de integração JD | QA | 5 | QA | ⬜ | Dados sincronizados |

**Definição de Pronto:**
- [ ] OAuth John Deere funcionando
- [ ] Dados de máquinas em tempo real
- [ ] Operações de campo listadas
- [ ] Dashboard de telemetria

---

## 📅 Sprint 16 (Semana 31-32)
**Tema:** IoT - Case IH e Alertas WhatsApp
**Objetivo:** Integrar Case IH AFS e implementar alertas WhatsApp

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S16.T1 | Registrar Case IH Developer | DevOps | 3 | DevOps | ⬜ | Registro aprovado |
| S16.T2 | Integrar AFS Connect API | Backend | 13 | Backend | ⬜ | API conectada |
| S16.T3 | Buscar dados de máquinas Case | Backend | 8 | Backend | ⬜ | Dados obtidos |
| S16.T4 | Contratar Twilio (WhatsApp) | DevOps | 3 | DevOps | ⬜ | Conta Twilio ativa |
| S16.T5 | Configurar WhatsApp Business API | Backend | 5 | Backend | ⬜ | API configurada |
| S16.T6 | Template: Alerta de estoque | Backend | 3 | Backend | ⬜ | Template aprovado |
| S16.T7 | Template: Alerta de manutenção | Backend | 3 | Backend | ⬜ | Template aprovado |
| S16.T8 | Enviar alerta de estoque mínimo | Backend | 5 | Backend | ⬜ | WhatsApp enviado |
| S16.T9 | Enviar alerta de manutenção | Backend | 5 | Backend | ⬜ | WhatsApp enviado |
| S16.T10 | Frontend: Configurar alertas | Frontend | 5 | Frontend | ⬜ | Configuração salva |
| S16.T11 | Frontend: Histórico de alertas | Frontend | 5 | Frontend | ⬜ | Histórico visível |
| S16.T12 | Comparador de preços regional | Backend | 8 | Backend | ⬜ | Comparação funcionando |
| S16.T13 | Testes WhatsApp | QA | 5 | QA | ⬜ | Alertas recebidos |

**Definição de Pronto:**
- [ ] Case IH AFS integrado
- [ ] WhatsApp Business configurado
- [ ] Alertas de estoque enviados
- [ ] Alertas de manutenção enviados
- [ ] Comparador de preços regional

---

## 📅 Sprint 17 (Semana 33-34)
**Tema:** Agricultura de Precisão - Amostragem de Solo
**Objetivo:** Implementar cadastro de amostras georreferenciadas

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S17.T1 | Criar modelo AmostraSolo | Backend | 3 | Backend | ⬜ | Migration criada |
| S17.T2 | Cadastro de amostras (lat/long) | Backend | 5 | Backend | ⬜ | Amostras salvas |
| S17.T3 | Importar amostras (CSV) | Backend | 5 | Backend | ⬜ | CSV importado |
| S17.T4 | Validar coordenadas GPS | Backend | 3 | Backend | ⬜ | Validação funcional |
| S17.T5 | Frontend: Mapa de amostras | Frontend | 8 | Frontend | ⬜ | Mapa exibido |
| S17.T6 | Frontend: Cadastrar amostra | Frontend | 8 | Frontend | ⬜ | Formulário funcional |
| S17.T7 | Frontend: Editar amostra | Frontend | 5 | Frontend | ⬜ | Edição funcional |
| S17.T8 | Exportar amostras (shapefile) | Backend | 5 | Backend | ⬜ | Shapefile gerado |
| S17.T9 | Integrar laboratórios (opcional) | Backend | 8 | Backend | ⬜ | Integração pronta |
| S17.T10 | Testes de amostragem | QA | 5 | QA | ⬜ | Testes aprovados |

**Definição de Pronto:**
- [ ] Amostras georreferenciadas cadastradas
- [ ] Mapa de amostras visual
- [ ] Importação/exportação funcional

---

## 📅 Sprint 18 (Semana 35-36)
**Tema:** Agricultura de Precisão - Mapa de Fertilidade
**Objetivo:** Implementar interpolação e geração de mapas

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S18.T1 | Implementar Krigagem | GIS | 13 | GIS | ⬜ | Krigagem funcionando |
| S18.T2 | Implementar IDW (Inverse Distance) | GIS | 8 | GIS | ⬜ | IDW funcionando |
| S18.T3 | Gerar mapa de pH | GIS | 8 | GIS | ⬜ | Mapa gerado |
| S18.T4 | Gerar mapa de Matéria Orgânica | GIS | 8 | GIS | ⬜ | Mapa gerado |
| S18.T5 | Gerar mapa de Fósforo | GIS | 8 | GIS | ⬜ | Mapa gerado |
| S18.T6 | Gerar mapa de Potássio | GIS | 8 | GIS | ⬜ | Mapa gerado |
| S18.T7 | Exportar mapa (GeoJSON) | GIS | 5 | GIS | ⬜ | GeoJSON gerado |
| S18.T8 | Exportar mapa (shapefile) | GIS | 5 | GIS | ⬜ | Shapefile gerado |
| S18.T9 | Frontend: Visualizar mapas | Frontend | 13 | Frontend | ⬜ | Mapas exibidos |
| S18.T10 | Frontend: Legenda interativa | Frontend | 5 | Frontend | ⬜ | Legenda funcional |
| S18.T11 | Frontend: Exportar mapa | Frontend | 5 | Frontend | ⬜ | Exportação funcional |
| S18.T12 | Testes de interpolação | QA | 5 | QA | ⬜ | Mapas validados |

**Definição de Pronto:**
- [ ] Interpolação (Krigagem/IDW) funcionando
- [ ] Mapas de fertilidade gerados
- [ ] Visualização no frontend
- [ ] Exportação para máquinas

---

## 📅 Sprint 19 (Semana 37-38)
**Tema:** Agricultura de Precisão - NDVI e Irrigação
**Objetivo:** Implementar NDVI e gestão de irrigação

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S19.T1 | Integrar Sentinel-2 API | Backend | 8 | Backend | ⬜ | API conectada |
| S19.T2 | Calcular NDVI | GIS | 8 | GIS | ⬜ | NDVI calculado |
| S19.T3 | Gerar mapa NDVI por talhão | GIS | 8 | GIS | ⬜ | Mapa gerado |
| S19.T4 | Atualizar NDVI semanalmente | Backend | 3 | Backend | ⬜ | Cron configurado |
| S19.T5 | Frontend: Mapa NDVI | Frontend | 8 | Frontend | ⬜ | Mapa exibido |
| S19.T6 | Criar modelo SistemaIrrigacao | Backend | 3 | Backend | ⬜ | Migration criada |
| S19.T7 | Cadastro de sistemas de irrigação | Backend | 5 | Backend | ⬜ | Cadastro funcional |
| S19.T8 | Calcular ET0 (evapotranspiração) | Backend | 8 | Backend | ⬜ | ET0 calculada |
| S19.T9 | Balanço hídrico | Backend | 8 | Backend | ⬜ | Balanço calculado |
| S19.T10 | Programação de irrigação | Backend | 5 | Backend | ⬜ | Programação gerada |
| S19.T11 | Frontend: Gestão de irrigação | Frontend | 8 | Frontend | ⬜ | Tela completa |
| S19.T12 | Testes NDVI e irrigação | QA | 5 | QA | ⬜ | Testes aprovados |

**Definição de Pronto:**
- [ ] NDVI calculado e exibido
- [ ] Atualização semanal automática
- [ ] Irrigação programada
- [ ] Balanço hídrico calculado

---

## 📅 Sprint 20 (Semana 39-40)
**Tema:** Agricultura de Precisão - VRA e Telemetria
**Objetivo:** Implementar prescrição VRA e telemetria de máquinas

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S20.T1 | Criar modelo PrescricaoVRA | Backend | 3 | Backend | ⬜ | Migration criada |
| S20.T2 | Gerar prescrição taxa variável | GIS | 13 | GIS | ⬜ | Prescrição gerada |
| S20.T3 | Exportar VRA (ISOXML) | GIS | 8 | GIS | ⬜ | ISOXML gerado |
| S20.T4 | Frontend: Criar prescrição | Frontend | 8 | Frontend | ⬜ | Formulário funcional |
| S20.T5 | Frontend: Visualizar prescrição | Frontend | 5 | Frontend | ⬜ | Visualização OK |
| S20.T6 | Telemetria: Integrar sensores | IoT | 8 | IoT | ⬜ | Sensores conectados |
| S20.T7 | Telemetria: Buscar dados em tempo real | IoT | 8 | IoT | ⬜ | Dados em tempo real |
| S20.T8 | Telemetria: Armazenar histórico | Backend | 5 | Backend | ⬜ | Histórico salvo |
| S20.T9 | Frontend: Dashboard telemetria | Frontend | 8 | Frontend | ⬜ | Dashboard completo |
| S20.T10 | Alertas de consumo anormal | Backend | 5 | Backend | ⬜ | Alertas gerados |
| S20.T11 | Testes VRA e telemetria | QA | 5 | QA | ⬜ | Testes aprovados |

**Definição de Pronto:**
- [ ] Prescrição VRA gerada
- [ ] Exportação ISOXML para máquinas
- [ ] Telemetria em tempo real
- [ ] Alertas de consumo

---

## 📅 Sprint 21 (Semana 41-42)
**Tema:** Enterprise - API Pública
**Objetivo:** Implementar API pública documentada

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S21.T1 | Criar modelo APIKey | Backend | 3 | Backend | ⬜ | Migration criada |
| S21.T2 | Gerar API Key para clientes | Backend | 5 | Backend | ⬜ | Keys geradas |
| S21.T3 | Implementar rate limiting | Backend | 5 | Backend | ⬜ | Rate limit funcionando |
| S21.T4 | Documentar endpoints (Swagger) | Backend | 8 | Backend | ⬜ | Swagger completo |
| S21.T5 | Criar portal do desenvolvedor | Frontend | 13 | Frontend | ⬜ | Portal no ar |
| S21.T6 | Frontend: Gerar API Key | Frontend | 5 | Frontend | ⬜ | Geração funcional |
| S21.T7 | Frontend: Documentação | Frontend | 5 | Frontend | ⬜ | Docs visíveis |
| S21.T8 | Implementar versionamento (v1, v2) | Backend | 5 | Backend | ⬜ | Versionamento OK |
| S21.T9 | Criar SDK Python | Backend | 8 | Backend | ⬜ | SDK publicado |
| S21.T10 | Criar SDK JavaScript | Backend | 8 | Backend | ⬜ | SDK publicado |
| S21.T11 | Testes de API pública | QA | 5 | QA | ⬜ | Testes aprovados |
| S21.T12 | Documentação para devs | Produto | 5 | Produto | ⬜ | Docs publicadas |

**Definição de Pronto:**
- [ ] API pública documentada
- [ ] Portal do desenvolvedor no ar
- [ ] SDKs publicados
- [ ] Rate limiting funcionando

---

## 📅 Sprint 22 (Semana 43-44)
**Tema:** Enterprise - SAP e Power BI
**Objetivo:** Integrar SAP e implementar Power BI Embedded

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S22.T1 | Configurar SAP RFC | DevOps | 5 | DevOps | ⬜ | RFC configurado |
| S22.T2 | Integrar SAP BAPI | Backend | 21 | Backend | ⬜ | BAPI funcionando |
| S22.T3 | Mapear dados AgroSaaS → SAP | Backend | 8 | Backend | ⬜ | Mapeamento completo |
| S22.T4 | Sync de lançamentos financeiros | Backend | 8 | Backend | ⬜ | Sync automático |
| S22.T5 | Contratar Power BI Embedded | DevOps | 3 | DevOps | ⬜ | Conta ativa |
| S22.T6 | Configurar Power BI | Backend | 5 | Backend | ⬜ | Configuração OK |
| S22.T7 | Criar templates de relatórios | Frontend | 8 | Frontend | ⬜ | Templates prontos |
| S22.T8 | Embed Power BI no frontend | Frontend | 13 | Frontend | ⬜ | Dashboards embed |
| S22.T9 | Frontend: Galeria de relatórios | Frontend | 5 | Frontend | ⬜ | Galeria visível |
| S22.T10 | Benchmarks regionais | Backend | 8 | Backend | ⬜ | Benchmarks calculados |
| S22.T11 | Testes SAP e Power BI | QA | 5 | QA | ⬜ | Testes aprovados |

**Definição de Pronto:**
- [ ] SAP integrado
- [ ] Power BI embed funcionando
- [ ] Benchmarks regionais disponíveis

---

## 📅 Sprint 23 (Semana 45-46)
**Tema:** Enterprise - Análise Preditiva
**Objetivo:** Implementar modelos preditivos de safra

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S23.T1 | Coletar histórico de safras | ML | 5 | ML | ⬜ | Histórico coletado |
| S23.T2 | Coletar dados climáticos | ML | 5 | ML | ⬜ | Dados coletados |
| S23.T3 | Treinar modelo de previsão | ML | 13 | ML | ⬜ | Modelo treinado |
| S23.T4 | Previsão de produtividade | ML | 8 | ML | ⬜ | Previsão gerada |
| S23.T5 | Riscos climáticos (geada, seca) | ML | 8 | ML | ⬜ | Riscos identificados |
| S23.T6 | Surto de pragas (epidemiológico) | ML | 13 | ML | ⬜ | Alertas gerados |
| S23.T7 | Preços de commodities | ML | 8 | ML | ⬜ | Preços previstos |
| S23.T8 | Frontend: Dashboard preditivo | Frontend | 8 | Frontend | ⬜ | Dashboard completo |
| S23.T9 | Frontend: Alertas preditivos | Frontend | 5 | Frontend | ⬜ | Alertas visíveis |
| S23.T10 | Programa de pontos (parcerias) | Backend | 8 | Backend | ⬜ | Programa ativo |
| S23.T11 | Testes preditivos | QA | 5 | QA | ⬜ | Testes aprovados |

**Definição de Pronto:**
- [ ] Previsão de safra funcionando
- [ ] Alertas de riscos climáticos
- [ ] Alertas de pragas
- [ ] Dashboard preditivo

---

## 📅 Sprint 24 (Semana 47-48)
**Tema:** Estabilização Fase 2
**Objetivo:** Bug fixes, performance e preparação Fase 3

### Tarefas

| ID | Tarefa | Tipo | Pontos | Responsável | Status | Critério de Aceite |
|----|--------|------|--------|-------------|--------|-------------------|
| S24.T1 | Corrigir bugs IA | ML | 8 | ML | ⬜ | Bugs resolvidos |
| S24.T2 | Corrigir bugs IoT | Backend | 8 | Backend | ⬜ | Bugs resolvidos |
| S24.T3 | Otimizar modelos ML | ML | 8 | ML | ⬜ | Inferência < 300ms |
| S24.T4 | Otimizar queries GIS | GIS | 8 | GIS | ⬜ | Queries < 500ms |
| S24.T5 | Melhorar UX app mobile | Mobile | 5 | Mobile | ⬜ | Feedback incorporado |
| S24.T6 | Documentar APIs IA/IoT | Backend | 5 | Backend | ⬜ | Docs completas |
| S24.T7 | Treinar suporte (IA/IoT) | Suporte | 5 | Suporte | ⬜ | Treinamento realizado |
| S24.T8 | Coletar feedback clientes | Produto | 5 | Produto | ⬜ | Feedback documentado |
| S24.T9 | Planejar Fase 3 (Ecossistema) | Todos | 5 | Todos | ⬜ | Planejamento aprovado |
| S24.T10 | Testes de carga (IA) | QA | 8 | QA | ⬜ | 500 req/min |
| S24.T11 | Testes de carga (IoT) | QA | 8 | QA | ⬜ | 1000 dispositivos |
| S24.T12 | Bug bash (time todo) | Todos | 5 | Todos | ⬜ | Bugs corrigidos |

**Definição de Pronto:**
- [ ] Bugs críticos resolvidos
- [ ] Performance otimizada
- [ ] Documentação completa
- [ ] Fase 3 planejada

---

## 📊 Resumo da Fase 2

| Sprint | Pontos | Entregáveis Principais |
|--------|--------|----------------------|
| 13 | 75 | Dataset IA, Modelo treinado |
| 14 | 67 | API Diagnóstico, App captura |
| 15 | 76 | John Deere integrado |
| 16 | 71 | Case IH, WhatsApp alertas |
| 17 | 50 | Amostragem solo |
| 18 | 86 | Mapas de fertilidade |
| 19 | 77 | NDVI, Irrigação |
| 20 | 76 | VRA, Telemetria |
| 21 | 75 | API Pública, SDKs |
| 22 | 76 | SAP, Power BI |
| 23 | 86 | Análise preditiva |
| 24 | 76 | Estabilização |
| **TOTAL** | **891** | **12 sprints** |

---

## 🎯 Critérios de Aceite da Fase 2

- [ ] IA diagnostica 10+ pragas/doenças com >85% acurácia
- [ ] John Deere Ops Center integrado
- [ ] Case IH AFS Connect integrado
- [ ] Alertas WhatsApp ativos
- [ ] Mapas de fertilidade gerados (Krigagem/IDW)
- [ ] NDVI atualizado semanalmente
- [ ] Irrigação programada
- [ ] Prescrição VRA exportada (ISOXML)
- [ ] Telemetria em tempo real
- [ ] API pública documentada
- [ ] Power BI embedded
- [ ] SAP integrado
- [ ] Previsão de safra funcionando

---

**Aprovado por:** _______________________
**Data:** ___/___/_____
**Scrum Master:** _______________________
**Product Owner:** _______________________
