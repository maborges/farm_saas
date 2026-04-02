# Sprint 5 - Backlog de Tarefas

**Sprint:** 5
**Período:** 2026-05-26 a 2026-06-06 (2 semanas)
**Tema:** CAR + Monitoramento Ambiental
**Objetivo:** Implementar gestão do CAR e monitoramento via satélite

---

## 📋 Tarefas da Sprint

### S5.T1 - Estudar API do SNA (CAR)
**Responsável:** Backend
**Pontos:** 3
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Documentação do SNA lida
- [ ] Endpoints mapeados
- [ ] Autenticação entendida

**Checklist:**
- [ ] Acessar portal do SNA (CAR)
- [ ] Obter credenciais de API
- [ ] Documentar endpoints
- [ ] Testar conexão em homologação

---

### S5.T2 - Criar modelo CAR
**Responsável:** Backend
**Pontos:** 3
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Migration criada
- [ ] Modelo SQLAlchemy implementado
- [ ] Campos do eSocial

**Checklist:**
- [ ] Criar tabela `ambiental_car`
- [ ] Campos: código CAR, áreas (total, APP, RL)
- [ ] Sobreposições (TI, UC, quilombos)
- [ ] Status, pendências
- [ ] Relacionamentos com fazenda

---

### S5.T3 - Importar recibo CAR
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Upload de recibo CAR
- [ ] Parse do PDF/XML
- [ ] Dados salvos no banco

**Checklist:**
- [ ] Endpoint de upload
- [ ] Parser de recibo CAR
- [ ] Extrair: código, áreas, imóveis
- [ ] Salvar no banco
- [ ] Validações

---

### S5.T4 - Integrar API SNA
**Responsável:** Backend
**Pontos:** 13
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Conexão estabelecida
- [ ] CAR consultado
- [ ] Dados sincronizados

**Checklist:**
- [ ] Criar cliente HTTP para SNA
- [ ] Implementar `consultar_car()`
- [ ] Implementar `baixar_recibo()`
- [ ] Tratar erros
- [ ] Log de requisições

---

### S5.T5 - Calcular área total (geoprocessamento)
**Responsável:** GIS
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Área calculada corretamente
- [ ] Unidade em hectares
- [ ] Precisão > 95%

**Checklist:**
- [ ] Usar GeoAlchemy2
- [ ] Calcular área do polígono
- [ ] Converter para hectares
- [ ] Testes com áreas conhecidas

---

### S5.T6 - Calcular área de APP
**Responsável:** GIS
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] APP identificada
- [ ] Área calculada
- [ ] Mapa gerado

**Checklist:**
- [ ] Identificar cursos d'água
- [ ] Calcular faixa de APP (30m, 50m, 100m)
- [ ] Calcular área
- [ ] Salvar no banco

---

### S5.T7 - Calcular área de Reserva Legal
**Responsável:** GIS
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] RL identificada
- [ ] Percentual calculado (20%, 35%, 80%)
- [ ] Área calculada

**Checklist:**
- [ ] Identificar vegetação nativa
- [ ] Calcular percentual por bioma
- [ ] Calcular área
- [ ] Comparar com mínimo exigido

---

### S5.T8 - Verificar sobreposições
**Responsável:** GIS
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Sobreposições detectadas
- [ ] TI, UC, quilombos identificados
- [ ] Alertas gerados

**Checklist:**
- [ ] Carregar shapefiles de TI
- [ ] Carregar shapefiles de UC
- [ ] Carregar shapefiles de quilombos
- [ ] Intersectar com imóvel
- [ ] Calcular área sobreposta

---

### S5.T9 - Frontend: Importar CAR
**Responsável:** Frontend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Upload de recibo
- [ ] Dados exibidos
- [ ] Validações

**Checklist:**
- [ ] Criar página de importação
- [ ] Upload de PDF/XML
- [ ] Exibir dados do CAR
- [ ] Confirmar importação

---

### S5.T10 - Frontend: Dashboard de áreas
**Responsável:** Frontend
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Gráficos de áreas
- [ ] Mapa do imóvel
- [ ] Percentuais exibidos

**Checklist:**
- [ ] Gráfico de pizza (áreas)
- [ ] Mapa interativo
- [ ] Cards com totais
- [ ] Alertas de pendências

---

### S5.T11 - Integrar Sentinel-2 API
**Responsável:** Backend
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Imagens obtidas
- [ ] NDVI calculado
- [ ] Atualização semanal

**Checklist:**
- [ ] Criar conta Copernicus
- [ ] Obter API key
- [ ] Buscar imagens por coordenadas
- [ ] Filtrar por data e cobertura de nuvens

---

### S5.T12 - Processar imagens de satélite
**Responsável:** GIS
**Pontos:** 13
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Imagem processada
- [ ] NDVI calculado
- [ ] Mudança detectada

**Checklist:**
- [ ] Baixar imagem
- [ ] Calcular NDVI
- [ ] Comparar com imagem anterior
- [ ] Detectar mudança de cobertura

---

### S5.T13 - Detectar mudança de cobertura
**Responsável:** GIS
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Mudança detectada
- [ ] Área calculada
- [ ] Alerta gerado

**Checklist:**
- [ ] Comparar NDVI atual com anterior
- [ ] Identificar áreas de desmatamento
- [ ] Calcular área desmatada
- [ ] Classificar mudança

---

### S5.T14 - Implementar alertas de desmatamento
**Responsável:** Backend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Alerta gerado
- [ ] Notificação enviada
- [ ] Log de alertas

**Checklist:**
- [ ] Criar modelo `AlertaDesmatamento`
- [ ] Definir thresholds
- [ ] Enviar e-mail/SMS
- [ ] Dashboard de alertas

---

### S5.T15 - Criar modelo MonitoramentoAPP
**Responsável:** Backend
**Pontos:** 3
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Migration criada
- [ ] Modelo implementado

**Checklist:**
- [ ] Criar tabela `ambiental_monitoramento_app`
- [ ] Campos: data, área, alertas
- [ ] Relacionamentos

---

### S5.T16 - Frontend: Mapa de monitoramento
**Responsável:** Frontend
**Pontos:** 8
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Mapa exibido
- [ ] Áreas coloridas
- [ ] Legenda

**Checklist:**
- [ ] Integrar Leaflet/Mapbox
- [ ] Carregar polígonos
- [ ] Exibir NDVI
- [ ] Highlight de alertas

---

### S5.T17 - Frontend: Histórico de alertas
**Responsável:** Frontend
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Lista de alertas
- [ ] Filtros por data, tipo
- [ ] Detalhes do alerta

**Checklist:**
- [ ] Criar tabela de alertas
- [ ] Filtros
- [ ] Detalhes em dialog
- [ ] Exportar relatório

---

### S5.T18 - Configurar notificações por e-mail
**Responsável:** Backend
**Pontos:** 3
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] E-mail enviado
- [ ] Template configurado

**Checklist:**
- [ ] Integrar com serviço de e-mail
- [ ] Criar template de alerta
- [ ] Configurar destinatários
- [ ] Testar envio

---

### S5.T19 - Testes de monitoramento
**Responsável:** QA
**Pontos:** 5
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Testes de importação CAR
- [ ] Testes de cálculo de área
- [ ] Testes de detecção de desmatamento
- [ ] Coverage > 90%

---

### S5.T20 - Documentar API ambiental
**Responsável:** Backend
**Pontos:** 2
**Status:** ⬜ A Fazer

**Critério de Aceite:**
- [ ] Swagger atualizado
- [ ] Exemplos de CAR
- [ ] Códigos de erro

---

## 📊 Burndown da Sprint

| Dia | Pontos Restantes |
|-----|-----------------|
| Dia 1 | 153 |
| Dia 2 | 130 |
| Dia 3 | 100 |
| Dia 4 | 70 |
| Dia 5 | 40 |
| Dia 6 | 20 |
| Dia 7 | 10 |
| Dia 8 | Buffer |
| Dia 9 | Buffer |
| Dia 10 | Revisão |

---

## 🎯 Definição de Pronto da Sprint

- [ ] CAR importado do SNA
- [ ] Áreas calculadas (total, APP, RL)
- [ ] Sobreposições detectadas
- [ ] Monitoramento via satélite ativo
- [ ] Alertas de desmatamento funcionando
- [ ] Frontend de monitoramento pronto
- [ ] Testes com coverage > 90%
- [ ] Documentação completa

---

## 📝 Notas da Sprint

**Dependências:**
- API do SNA (CAR) disponível
- Copernicus Sentinel (gratuito)
- Shapefiles de TI/UC disponíveis

**Riscos:**
- ⚠️ API do SNA pode ter limitações
- ⚠️ Imagens de satélite com nuvens
- ⚠️ Processamento de imagens é pesado

**Mitigações:**
- Usar cache de requisições
- Filtrar imagens por cobertura de nuvens
- Usar processamento assíncrono (Celery)

---

**Scrum Master:** _______________________
**Product Owner:** _______________________
**Tech Lead:** _______________________

**Data de Início:** 2026-05-26
**Data de Fim:** 2026-06-06
