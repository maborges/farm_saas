# BL-06 — Integrações Regulatórias

**Módulo:** core/integracoes  
**Frente:** Backend — Integrações Externas  
**Dependências:** BL-01, BL-02  
**Estimativa:** 3 dias

---

## Contexto

Integrações para preenchimento automático e validação de dados regulatórios.

**MVP (esta sprint):**
- CEP/IBGE — preenche município/UF
- CNPJ/CPF (Receita Federal) — valida produtor
- CAR/SICAR (IBAMA) — valida e importa dados da propriedade

**Fase 2 (backlog futuro):**
- CCIR (INCRA), NIRF (Receita Federal), SIGEF, CIF/MAPA

---

## User Stories

### US-06.1 — Lookup por CEP
**Como** usuário,  
**quero** digitar o CEP e ter município/UF preenchidos automaticamente,  
**para** evitar erros de digitação e agilizar o cadastro.

**Critérios de aceite:**
- [ ] API ViaCEP ou BrasilAPI como fonte
- [ ] Preenche: logradouro, bairro, município, UF, código IBGE
- [ ] Campos editáveis após preenchimento automático
- [ ] Timeout de 3s — não bloqueia o cadastro se falhar
- [ ] Cache do resultado por CEP (Redis ou memória)

---

### US-06.2 — Validação de CPF/CNPJ do Produtor
**Como** sistema,  
**quero** validar CPF/CNPJ via Receita Federal ao criar assinatura,  
**para** garantir que os dados do produtor estejam corretos.

**Critérios de aceite:**
- [ ] CPF: validação de dígitos verificadores (algoritmo local — sem API)
- [ ] CNPJ: consulta API Receita Federal (BrasilAPI ou ReceitaWS)
- [ ] CNPJ retorna: razão social, nome fantasia, situação cadastral, endereço
- [ ] Situação `ATIVA` obrigatória para PJ
- [ ] Dados preenchidos automaticamente (editáveis)
- [ ] Rate limit respeitado (BrasilAPI: 3 req/min gratuito)

---

### US-06.3 — Integração CAR/SICAR
**Como** usuário,  
**quero** informar o código CAR e ter os dados da propriedade importados automaticamente,  
**para** garantir que área e localização estejam corretos conforme registro ambiental.

**Critérios de aceite:**
- [ ] Campo CAR com máscara: `UF-XXXXXXXX-XXXX.XXXX.XXXX/XXXX-XX`
- [ ] Consulta API SICAR/IBAMA ao informar o código
- [ ] Importa: área total, município, UF, status do CAR, data de cadastro
- [ ] Status exibido como badge: `Regular | Pendente | Cancelado | Suspenso`
- [ ] `car_data_ultima_sync` registrado para auditoria
- [ ] Falha na consulta não bloqueia o cadastro (campos manuais como fallback)

---

### US-06.4 — Sincronização CAR (Fase 2 — backlog)
**Como** sistema,  
**quero** re-sincronizar dados do CAR periodicamente,  
**para** detectar mudanças de status ambiental automaticamente.

**Critérios de aceite:**
- [ ] Job agendado (cron) — re-consulta CAR a cada 30 dias
- [ ] Notifica gestor se status do CAR mudar
- [ ] Histórico de status mantido

---

## Tarefas Técnicas

### Backend
- [ ] `IntegracaoService` — classe com métodos para cada API
- [ ] `get_endereco_por_cep(cep: str)` — BrasilAPI/ViaCEP
- [ ] `validar_cpf(cpf: str)` — algoritmo local
- [ ] `consultar_cnpj(cnpj: str)` — BrasilAPI
- [ ] `consultar_car(car_codigo: str)` — SICAR/IBAMA
- [ ] Cache em memória com TTL para CEP e CNPJ
- [ ] Endpoints proxy: `GET /integracoes/cep/{cep}`, `GET /integracoes/cnpj/{cnpj}`, `GET /integracoes/car/{codigo}`
- [ ] Tratamento de erros: timeout, rate limit, dado não encontrado
- [ ] Testes com mocks para cada API externa

### Frontend
- [ ] Hook `useCepLookup(cep)` — debounce 500ms
- [ ] Hook `useCnpjLookup(cnpj)` — debounce 500ms
- [ ] Hook `useCarLookup(codigo)` — trigger manual (botão "Consultar")
- [ ] Estados: loading spinner inline, erro inline (não bloqueia o form)
