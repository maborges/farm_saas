# AgroSaaS — Guia Completo do Sistema

**Plataforma de Gestao Rural Inteligente**
Borgus Software Ltda | Atualizado em: Abril 2026

---

## Sumario

1. [Visao Geral](#1-visao-geral)
2. [Nucleo (Core)](#2-nucleo-core)
3. [Modulo Agricola](#3-modulo-agricola)
4. [Modulo Pecuaria](#4-modulo-pecuaria)
5. [Modulo Financeiro](#5-modulo-financeiro)
6. [Modulo Imoveis Rurais](#6-modulo-imoveis-rurais)
7. [Modulo Operacional](#7-modulo-operacional)
8. [Modulo RH](#8-modulo-rh)
9. [Modulo Ambiental](#9-modulo-ambiental)
10. [Extensoes Enterprise (Addons)](#10-extensoes-enterprise-addons)
11. [Integracoes](#11-integracoes)
12. [Planos e Precificacao](#12-planos-e-precificacao)
13. [Controle de Acesso (RBAC)](#13-controle-de-acesso-rbac)
14. [Backoffice Administrativo](#14-backoffice-administrativo)

---

## 1. Visao Geral

O AgroSaaS e uma plataforma multi-tenant de gestao rural completa que cobre toda a operacao da propriedade — do planejamento de safra ao balanco financeiro.

### Principais Caracteristicas

- **Multi-tenant:** Cada cliente (produtor/empresa) tem seus dados completamente isolados
- **Multi-fazenda:** Gerencie varias propriedades em um unico painel, com consolidacao de dados
- **Modular:** O cliente paga apenas pelos modulos que usa
- **3 Tiers de profundidade:** Basico, Profissional, Premium — cada tier libera funcionalidades mais avancadas dentro dos modulos contratados
- **Cloud-native:** Acesso web e mobile de qualquer lugar
- **RBAC granular:** Permissoes por perfil, por modulo e ate por fazenda individual

### Aplicacoes

| App | Descricao | Porta |
|-----|-----------|-------|
| **Web (apps/web)** | Aplicacao principal — dashboard, modulos, configuracoes | 3000 |
| **Backoffice (apps/backoffice)** | Painel administrativo do SaaS (gestao de tenants, planos, CRM) | 3001 |
| **Mobile (apps/mobile)** | App React Native para campo (offline-first) | — |
| **API (services/api)** | Backend FastAPI — todos os endpoints REST | 8000 |

---

## 2. Nucleo (Core)

> **Incluido em todos os planos.** Preco: R$ 0,00 (embutido na assinatura)

O Core e a base obrigatoria do sistema. Tudo passa por ele.

### 2.1 Autenticacao e Sessoes

| Funcionalidade | Descricao |
|----------------|-----------|
| Login / Registro | Cadastro self-service com wizard de onboarding |
| JWT com claims | Token seguro com tenant_id, permissoes, is_owner |
| Sessoes ativas | Controle de sessoes simultaneas com heartbeat |
| Forgot / Reset password | Fluxo completo de recuperacao de senha por email |
| Convites | Proprietario convida membros da equipe por email |
| Tenant-switcher | Usuarios com acesso a multiplos tenants alternam entre eles |

### 2.2 Cadastros Gerais

| Funcionalidade | Descricao |
|----------------|-----------|
| Propriedades / Fazendas | Cadastro com dados economicos, NIRF, localizacao GIS |
| Unidades Produtivas | Areas dentro da fazenda (talhoes, piquetes, etc.) |
| Pessoas | Fornecedores, clientes, funcionarios, parceiros |
| Tipos de Relacionamento | Classificacao de pessoas (fornecedor, comprador, etc.) |
| Culturas | Catalogo de culturas agricolas |
| Commodities | Tabela de produtos comercializaveis |
| Equipamentos | Cadastro de maquinas, implementos, veiculos |
| Infraestrutura | Armazens, silos, barracoes, galpoes |

### 2.3 Configuracoes

| Funcionalidade | Descricao |
|----------------|-----------|
| SMTP / Email | Configuracao de servidor de email para notificacoes |
| Perfis de acesso | Criacao de perfis customizados com permissoes granulares |
| Auditoria | Log completo de acoes (quem fez o que, quando) |
| Notificacoes | Central de notificacoes com alertas em tempo real |

### 2.4 Suporte

| Funcionalidade | Descricao |
|----------------|-----------|
| Tickets de suporte | Abertura e acompanhamento de chamados |
| Chat em tempo real | WebSocket para comunicacao com suporte |
| Knowledge Base | Base de conhecimento com artigos de ajuda |

### 2.5 Relatorios

| Funcionalidade | Descricao |
|----------------|-----------|
| Relatorios gerais | Exportacao de dados em diversos formatos |
| Dashboard geral | Visao consolidada de todas as operacoes |

---

## 3. Modulo Agricola

O maior modulo do sistema, com **25+ submodulos** cobrindo todo o ciclo produtivo agricola.

### 3.1 Planejamento de Safra (A1_PLANEJAMENTO)

> **Categoria:** Agricola | **Preco avulso:** R$ 199/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| Safras | CRUD completo de safras com ciclo de fases (Planejada → Preparo Solo → Plantio → Desenvolvimento → Colheita → Finalizada) |
| Talhoes por safra | Associacao N:N entre safras e talhoes, com area plantada |
| Orcamento de safra | Planejamento financeiro por safra com itens de custo |
| Avancar fase | Transicao controlada de fase com validacao de regras de negocio |
| Timeline | Visualizacao cronologica do ciclo da safra |

**Telas no frontend:**
- `/agricola/safras` — Lista de safras
- `/agricola/safras/[id]` — Detalhe da safra (com abas: orcamento, talhoes, operacoes, colheita, etc.)
- `/agricola/planejamento` — Visao de planejamento

### 3.2 Caderno de Campo (A2_CAMPO)

> **Categoria:** Agricola | **Preco avulso:** R$ 249/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| Ordens de servico | Criacao e acompanhamento de OS para operacoes de campo |
| Apontamentos | Registro de atividades realizadas (horas, insumos, maquinas) |
| Operacoes agricolas | Tratos culturais (pulverizacao, adubacao, capina, etc.) |
| Checklist operacional | Templates de checklist para padronizar atividades |
| Checklist por safra | Checklists vinculados a safra especifica |

**Telas no frontend:**
- `/agricola/caderno` — Caderno de campo
- `/agricola/operacoes` — Operacoes agricolas
- `/agricola/checklist-templates` — Modelos de checklist
- `/agricola/safras/[id]/operacoes` — Operacoes da safra
- `/agricola/safras/[id]/checklist` — Checklist da safra

### 3.3 Defensivos e Receituario (A3_DEFENSIVOS)

> **Categoria:** Agricola | **Preco avulso:** R$ 199/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| Prescricoes | Receituario agronomico com dosagem, carencia, classe toxicologica |
| Cadastro de defensivos | Base de dados de produtos fitossanitarios |
| Rastreabilidade | Registro de aplicacao vinculado a talhao e safra |
| Relatorio de aplicacoes | Historico completo de defensivos aplicados |

**Telas no frontend:**
- `/agricola/defensivos` — Gestao de defensivos

### 3.4 Agricultura de Precisao (A4_PRECISAO)

> **Categoria:** Agricola | **Preco avulso:** R$ 399/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| NDVI basico | Indices de vegetacao via imagens de satelite |
| NDVI avancado | Analise temporal, comparacao de talhoes, zonas de manejo |
| Irrigacao | Manejo de irrigacao com lamina, turno de rega, sensores |
| Mapa interativo | Visualizacao GIS dos talhoes com overlays de dados |
| Amostragem de solo | Planejamento de coleta, grade amostral, georeferenciamento |
| Prescricoes VRA | Mapas de aplicacao a taxa variavel |

**Telas no frontend:**
- `/agricola/ndvi` — Mapa NDVI
- `/agricola/mapa` — Mapa interativo
- `/agricola/safras/[id]/ndvi` — NDVI por safra

### 3.5 Colheita e Romaneio (A5_COLHEITA)

> **Categoria:** Agricola | **Preco avulso:** R$ 199/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| Romaneios | Registro de cargas colhidas (peso bruto, tara, liquido, umidade, impureza) |
| Lotes de romaneio | Agrupamento de romaneios em lotes para rastreio |
| Fornecedores por lote | Rastreio de origem por fornecedor |
| Devolucao | Reversal de romaneios com estorno automatico |
| Aprovacao/baixa | Fluxo de aprovacao e baixa de romaneios |

**Telas no frontend:**
- `/agricola/romaneios` — Lista de romaneios
- `/agricola/safras/[id]/estoque` — Estoque da safra

### 3.6 Submodulos Adicionais (incluidos nos blocos agricolas)

| Submodulo | Funcionalidade | Tela |
|-----------|---------------|------|
| **Beneficiamento** | Pos-colheita (cafe): secagem, classificacao, lotes processados | `/agricola/beneficiamento` |
| **Analises de Solo** | Laudos de fertilidade, pH, macro/micronutrientes | `/agricola/analises-solo` |
| **Fenologia** | Registro de estagios fenologicos por talhao | `/agricola/fenologia` |
| **Monitoramento** | Pragas, doencas, plantas daninhas — MIP/MID | `/agricola/monitoramento` |
| **Climatico** | Dados meteorologicos, estacoes, historico | `/agricola/climatico` |
| **Custos** | Custo por operacao, por talhao, por safra | `/agricola/custos` |
| **Agronomo** | Visitas tecnicas, laudos, recomendacoes | — |
| **Alertas** | Notificacoes automaticas (clima, pragas, vencimentos) | — |
| **Previsoes** | Modelo preditivo de produtividade | — |
| **Rastreabilidade** | Rastreio campo-a-porto, historico de lote | `/agricola/rastreabilidade` |
| **Dashboard Agricola** | KPIs, graficos, resumo por safra/fazenda | `/agricola/dashboard` |
| **Cadastros Agricolas** | Culturas, variedades, dados mestres | `/agricola/cadastros/culturas` |
| **Relatorios** | Relatorios especificos do modulo agricola | `/agricola/relatorios` |
| **Financeiro por Safra** | Receitas e despesas vinculadas a safra | `/agricola/safras/[id]/financeiro` |

---

## 4. Modulo Pecuaria

### 4.1 Controle de Rebanho (P1_REBANHO)

> **Categoria:** Pecuaria | **Preco avulso:** R$ 249/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| Rastreio individual | Brinco, SISBOV, GTA por animal |
| Pesagens | Registro de peso com calculo de GMD (Ganho Medio Diario) |
| Sanidade basica | Calendario sanitario, vacinacoes, vermifugacoes |
| Lotes e piquetes | Gestao de lotes em pastagens/piquetes |
| Manejos | Registro de manejos sanitarios, nutricionais, reprodutivos |

### 4.2 Genetica Reprodutiva (P2_GENETICA)

> **Categoria:** Pecuaria | **Preco avulso:** R$ 349/mes | **Depende de:** P1_REBANHO

| Funcionalidade | Descricao |
|----------------|-----------|
| IATF | Protocolos de inseminacao artificial em tempo fixo |
| Diagnostico de prenhez | Registro de exames com resultado e data prevista de parto |
| Genealogia | Arvore genealogica, DEPs, merito genetico |
| Acasalamentos | Planejamento de cruzamentos |
| Racas | Cadastro de racas e linhagens |

### 4.3 Feedlot Control — Confinamento (P3_CONFINAMENTO)

> **Categoria:** Pecuaria | **Preco avulso:** R$ 399/mes | **Depende de:** P1_REBANHO

| Funcionalidade | Descricao |
|----------------|-----------|
| Lotes de confinamento | Entrada, saida, mortalidade |
| Fabrica de racao | Formulacao de dietas, TMR |
| Controle de cochos | Leitura de cocho, ajuste de oferta |
| Arracoamento | Registro diario de distribuicao de racao |

### 4.4 Pecuaria Leiteira (P4_LEITE)

> **Categoria:** Pecuaria | **Preco avulso:** R$ 299/mes | **Depende de:** P1_REBANHO

| Funcionalidade | Descricao |
|----------------|-----------|
| Controle leiteiro | Producao diaria por animal |
| Qualidade | CCS (Contagem de Celulas Somaticas), CBT |
| Curvas de lactacao | Analise de produtividade ao longo da lactacao |
| Secagem | Protocolo de secagem e periodo seco |

---

## 5. Modulo Financeiro

### 5.1 Tesouraria (F1_TESOURARIA)

> **Categoria:** Financeiro | **Preco avulso:** R$ 199/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| Contas a pagar | Lancamento, agendamento, baixa de pagamentos |
| Contas a receber | Lancamento de receitas, controle de inadimplencia |
| Fluxo de caixa (DFC) | Visao consolidada de entradas e saidas |
| Conciliacao bancaria | Confronto extrato x lancamentos |
| Plano de contas | Plano de contas personalizavel |
| Centros de custo | Rateio por fazenda, safra ou atividade |
| Relatorios financeiros | DRE, balancete, extrato por periodo |

### 5.2 Custos ABC / Rateio (F2_CUSTOS_ABC)

> **Categoria:** Financeiro | **Preco avulso:** R$ 349/mes | **Depende de:** F1_TESOURARIA | **Tier minimo:** Profissional

| Funcionalidade | Descricao |
|----------------|-----------|
| Custeio por atividade | Custo real por hectare, por talhao, por operacao |
| Rateio automatico | Distribuicao proporcional de custos indiretos |
| Cenarios | Simulacao de cenarios de custo |
| FIFO | Custeio de estoque por metodo FIFO |

### 5.3 Fiscal (F3_FISCAL)

> **Categoria:** Financeiro | **Preco avulso:** R$ 499/mes | **Depende de:** F1_TESOURARIA

| Funcionalidade | Descricao |
|----------------|-----------|
| NF-e | Emissao e recepcao de notas fiscais eletronicas |
| SPED | Geracao de arquivos SPED Fiscal e Contribuicoes |
| LCDPR | Livro Caixa Digital do Produtor Rural |
| Carne-Leao | Calculo e geracao de DARF para pessoa fisica |
| Conformidade | Alertas de obrigacoes fiscais vencendo |

### 5.4 Hedging e Barter (F4_HEDGING)

> **Categoria:** Financeiro | **Preco avulso:** R$ 599/mes | **Depende de:** F1_TESOURARIA | **Tier minimo:** Premium

| Funcionalidade | Descricao |
|----------------|-----------|
| Contratos futuros | Registro e acompanhamento de posicoes na B3 |
| Barter | Troca de insumos por producao futura |
| Simulacao de hedge | Cenarios de protecao de preco |
| Comparador de precos | Cotacoes de commodities em tempo real |

---

## 6. Modulo Imoveis Rurais

### 6.1 Cadastro de Imoveis (IMOVEIS_CADASTRO)

> **Categoria:** Imoveis | **Preco avulso:** R$ 149/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| NIRF | Numero do Imovel na Receita Federal |
| CAR | Cadastro Ambiental Rural |
| CCIR | Certificado de Cadastro de Imovel Rural |
| Documentos legais | Upload e gestao de certidoes, escrituras, matriculas |
| Georreferenciamento | Limites do imovel com coordenadas GIS |
| Arquivos geoespaciais | Upload de shapefiles, KML, GeoJSON |

### 6.2 Arrendamentos e Parcerias (IMOVEIS_ARRENDAMENTOS)

> **Categoria:** Imoveis | **Preco avulso:** R$ 199/mes | **Depende de:** IMOVEIS_CADASTRO

| Funcionalidade | Descricao |
|----------------|-----------|
| Contratos de arrendamento | Cadastro com vigencia, valor, reajuste |
| Parcerias agricolas | Contratos de parceria com percentuais |
| Alertas de vencimento | Notificacoes de contratos vencendo |

### 6.3 Avaliacao Patrimonial (IMOVEIS_AVALIACAO)

> **Categoria:** Imoveis | **Preco avulso:** R$ 399/mes | **Depende de:** IMOVEIS_CADASTRO | **Tier minimo:** Premium

| Funcionalidade | Descricao |
|----------------|-----------|
| Avaliacao de terra | Valor por hectare, benfeitorias |
| Evolucao patrimonial | Historico de valorizacao/depreciacao |
| Laudos | Geracao de laudos de avaliacao |

---

## 7. Modulo Operacional

### 7.1 Controle de Frota (O1_FROTA)

> **Categoria:** Operacional | **Preco avulso:** R$ 199/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| Cadastro de maquinas | Tratores, colhedoras, implementos, veiculos |
| Horímetro / Odometro | Controle de horas e quilometragem |
| Abastecimento | Registro de abastecimentos com custo por hora/km |
| Manutencao preventiva | Calendario de revisoes e trocas |
| Documentos | CNH, CRLV, seguros, licencas dos equipamentos |
| Apontamento de uso | Registro de uso por operador, atividade, talhao |

### 7.2 Estoque Multi-armazens (O2_ESTOQUE)

> **Categoria:** Operacional | **Preco avulso:** R$ 199/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| Multi-armazem | Controle de estoque por local (armazem, silo, galpao) |
| Movimentacoes | Entrada, saida, transferencia entre armazens |
| Lotes | Rastreio por lote com data de validade |
| Inventario | Contagem de estoque com ajustes |
| Custo FIFO | Custeio por metodo FIFO com historico |
| Estoque por safra | Vinculo de estoque a safra especifica |

### 7.3 Compras e Supply (O3_COMPRAS)

> **Categoria:** Operacional | **Preco avulso:** R$ 249/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| Cotacoes | Solicitacao de cotacao a fornecedores |
| Pedidos de compra | Workflow de aprovacao |
| Recebimento | Conferencia e entrada em estoque |
| Catalogo de produtos | Tipos: insumo, semente, defensivo, fertilizante, combustivel, peca, racao, medicamento, etc. |

### 7.4 Oficina (manutencao corretiva)

| Funcionalidade | Descricao |
|----------------|-----------|
| Ordens de servico | OS para reparos e manutencoes corretivas |
| Pecas e insumos | Baixa automatica do estoque |
| Historico | Historico completo por equipamento |

---

## 8. Modulo RH

### 8.1 Remuneracao de Temporarios (RH1_REMUNERACAO)

> **Categoria:** RH | **Preco avulso:** R$ 199/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| Colaboradores | Cadastro com dados pessoais, funcao, admissao |
| Folha simplificada | Calculo de diarias, producao, hora extra |
| eSocial | Integracao com webservice eSocial |
| Historico | Registro de pagamentos e ocorrencias |

### 8.2 Seguranca do Trabalho (RH2_SEGURANCA)

> **Categoria:** RH | **Preco avulso:** R$ 149/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| EPIs | Controle de entrega e validade de EPIs |
| EPCs | Equipamentos de protecao coletiva |
| SESMT | Documentacao de seguranca e medicina do trabalho |
| Treinamentos | Registro de treinamentos obrigatorios (NRs) |

---

## 9. Modulo Ambiental

### 9.1 Compliance Ambiental (AM1_COMPLIANCE)

> **Categoria:** Ambiental | **Preco avulso:** R$ 299/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| CAR | Gestao do Cadastro Ambiental Rural |
| CCIR | Controle de certificados |
| Outorgas hidricas | Licencas de uso de agua |
| APP / Reserva Legal | Demarcacao e monitoramento de areas protegidas |
| Licencas ambientais | Controle de licencas e suas renovacoes |

### 9.2 Gestao de Carbono (AM2_CARBONO)

> **Categoria:** Ambiental | **Preco avulso:** R$ 499/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| MRV | Mensuracao, Relato e Verificacao de emissoes |
| Pegada de carbono | Calculo de emissoes por atividade |
| Creditos de carbono | Gestao de projetos de credito de carbono |
| Relatorios ESG | Indicadores de sustentabilidade |

---

## 10. Extensoes Enterprise (Addons)

Addons que podem ser contratados independentemente do plano.

### 10.1 IA Copilot Agronoma (EXT_IA)

> **Preco:** R$ 799/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| LLM treinado | Modelo de IA especializado em agronomia |
| Alertas preditivos | Previsao de pragas, doencas, deficit hidrico |
| Recomendacoes EMBRAPA | Sugestoes baseadas em pesquisa cientifica |
| Diagnostico por imagem | Identificacao de problemas via foto (mobile) |

### 10.2 Integracao IoT (EXT_IOT)

> **Preco:** R$ 599/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| John Deere Ops Center | Integracao com telemetria John Deere |
| Case IH AFS | Integracao com plataforma Case IH |
| New Holland PLM | Dados de maquinas New Holland |
| Balancas inteligentes | Leitura automatica de peso (romaneios) |
| Sensores de solo | Umidade, temperatura, condutividade |
| Estacoes meteorologicas | Dados climaticos automaticos |

### 10.3 Bridge ERP Corporativo (EXT_ERP)

> **Preco:** R$ 1.299/mes

| Funcionalidade | Descricao |
|----------------|-----------|
| SAP | Integracao bidirecional com SAP ERP |
| Datasul (TOTVS) | Integracao com Datasul/Protheus |
| Open Banking | Conexao com bancos para conciliacao automatica |
| Power BI | Exportacao de dados para dashboards corporativos |
| Benchmarking | Comparativo de performance entre fazendas/regioes |

---

## 11. Integracoes

### 11.1 Pagamentos e Billing

| Integracao | Funcionalidade |
|------------|---------------|
| **Stripe** | Checkout, assinaturas recorrentes, webhooks de pagamento, portal do cliente |
| **Asaas** | Boleto, Pix, cartao — gateway brasileiro com webhooks |
| **Cupons** | Sistema de cupons de desconto para campanhas comerciais |

### 11.2 Comunicacao

| Integracao | Funcionalidade |
|------------|---------------|
| **Email (SMTP)** | Notificacoes transacionais, convites, recuperacao de senha — servidor configuravel |
| **Templates de email** | Templates personalizaveis pelo backoffice |
| **WhatsApp** | Envio de alertas e notificacoes via WhatsApp Business API |
| **WebSocket** | Chat de suporte em tempo real |
| **Notificacoes push** | Alertas no app mobile |

### 11.3 Maquinas e Telemetria (IoT)

| Integracao | Fabricante |
|------------|-----------|
| **John Deere Ops Center** | John Deere — telemetria de maquinas, mapas de colheita |
| **Case IH AFS Connect** | Case IH — dados de operacao, GPS |
| **New Holland PLM** | New Holland — dados de maquinas e implementos |
| **Balancas** | Balancas rodoviarias e de precisao — leitura automatica de peso |
| **Sensores IoT** | Estacoes meteorologicas, sensores de solo, armadilhas de pragas |

### 11.4 ERP e BI

| Integracao | Descricao |
|------------|-----------|
| **SAP** | Exportacao/importacao de dados financeiros e operacionais |
| **TOTVS Datasul** | Integracao com ERP Datasul/Protheus |
| **Power BI** | Datasets e conectores para dashboards corporativos |
| **Open Banking** | Conciliacao bancaria automatica |

### 11.5 Fiscal e Governo

| Integracao | Descricao |
|------------|-----------|
| **SPED** | Geracao de arquivos SPED Fiscal e Contribuicoes |
| **NF-e / NFC-e** | Emissao e recepcao de notas fiscais eletronicas |
| **eSocial** | Webservice eSocial para obrigacoes trabalhistas rurais |
| **LCDPR** | Livro Caixa Digital do Produtor Rural (Receita Federal) |
| **SISBOV** | Rastreabilidade bovina (Ministerio da Agricultura) |

### 11.6 Geoespacial e Satelite

| Integracao | Descricao |
|------------|-----------|
| **NDVI / Satelite** | Indices de vegetacao via imagens de satelite |
| **Shapefiles / KML / GeoJSON** | Import/export de arquivos geoespaciais |
| **Mapas interativos** | Visualizacao GIS de talhoes, areas, overlays |

### 11.7 API Publica

| Recurso | Descricao |
|---------|-----------|
| **REST API** | API completa documentada (Swagger/OpenAPI) |
| **Tokens de API** | Autenticacao por API Key para integracoes de terceiros |
| **Webhooks** | Notificacoes de eventos para sistemas externos |
| **Comparador de precos** | Cotacoes de commodities de fontes externas |

---

## 12. Planos e Precificacao

### 12.1 Tiers

| Tier | Nivel | O que libera |
|------|-------|-------------|
| **Basico** | 1 | Funcionalidades essenciais de cada modulo contratado |
| **Profissional** | 2 | Rateio automatico, cenarios, custos ABC, analises avancadas |
| **Premium** | 3 | IA, benchmarking, preditivo, funcionalidades enterprise |

### 12.2 Estrutura de Planos

Cada plano define:

| Parametro | Descricao |
|-----------|-----------|
| `modulos_inclusos` | Lista de modulos incluidos no preco do plano |
| `plan_tier` | BASICO, PROFISSIONAL ou PREMIUM |
| `max_fazendas` | Limite de fazendas (-1 = ilimitado) |
| `max_talhoes` | Limite de talhoes (-1 = ilimitado) |
| `max_cabecas` | Limite de cabecas de gado (-1 = ilimitado) |
| `max_hectares` | Limite de area total |
| `max_usuarios` | Limite de usuarios |
| `preco_mensal` / `preco_anual` | Valores de assinatura |
| `disponivel_site` | Visivel no checkout publico |
| `disponivel_crm` | Visivel no CRM para ofertas personalizadas |

### 12.3 Tabela de Precos Avulsos (por modulo)

| Modulo | Preco/mes |
|--------|-----------|
| Core (Nucleo) | Incluido |
| Cadastro de Imoveis | R$ 149 |
| Arrendamentos | R$ 199 |
| Avaliacao Patrimonial | R$ 399 |
| Planejamento de Safra | R$ 199 |
| Caderno de Campo | R$ 249 |
| Defensivos e Receituario | R$ 199 |
| Agricultura de Precisao | R$ 399 |
| Colheita e Romaneio | R$ 199 |
| Controle de Rebanho | R$ 249 |
| Genetica Reprodutiva | R$ 349 |
| Feedlot Control | R$ 399 |
| Pecuaria Leiteira | R$ 299 |
| Tesouraria | R$ 199 |
| Custos ABC / Rateio | R$ 349 |
| Fiscal (SPED/NF-e) | R$ 499 |
| Hedging e Barter | R$ 599 |
| Frota | R$ 199 |
| Estoque | R$ 199 |
| Compras | R$ 249 |
| RH Remuneracao | R$ 199 |
| RH Seguranca | R$ 149 |
| Compliance Ambiental | R$ 299 |
| Gestao de Carbono | R$ 499 |
| **Addon:** IA Copilot | R$ 799 |
| **Addon:** IoT | R$ 599 |
| **Addon:** Bridge ERP | R$ 1.299 |

---

## 13. Controle de Acesso (RBAC)

### 13.1 Perfis do Backoffice (Admin SaaS)

| Perfil | Acesso |
|--------|--------|
| **Super Admin** | Acesso total a tudo (*) |
| **Admin** | Dashboard, BI, tenants, planos, suporte, KB, perfis |
| **Suporte** | Dashboard, visualizar tenants/users, suporte, KB |
| **Financeiro** | Dashboard, BI, billing, visualizar tenants/planos/users |
| **Comercial** | Dashboard, planos, cupons, converter leads, BI |

### 13.2 Perfis do Tenant (Usuario final)

| Perfil | Acesso |
|--------|--------|
| **Owner** | Acesso total no tenant (*) — bypasssa RBAC |
| **Admin** | Gestao de equipe, fazendas, configuracoes + todos os modulos contratados |
| **Gerente** | Visualizar equipe, convidar, todos os modulos contratados |
| **Tecnico** | Modulos operacionais (agricola, pecuaria, operacional) — criar e editar |
| **Operador** | Apenas visualizar e listar dados dos modulos |
| **Financeiro** | Acesso total ao modulo financeiro + visualizacao de outros |
| **Auditor** | Somente leitura e exportacao em todos os modulos |

### 13.3 Permissoes Granulares

Formato: `modulo:recurso:acao`

Exemplos:
- `agricola:operacoes:create` — Criar operacoes agricolas
- `financeiro:*` — Acesso total ao modulo financeiro
- `tenant:users:invite` — Convidar usuarios
- `tenant:billing:view` — Visualizar billing

### 13.4 Perfis por Fazenda

Um usuario pode ter um perfil diferente em cada fazenda. Exemplo:
- Fazenda A: **Gerente** (acesso total)
- Fazenda B: **Operador** (apenas visualizacao)

---

## 14. Backoffice Administrativo

Painel exclusivo da equipe Borgus para administrar o SaaS.

### 14.1 Gestao de Tenants

| Funcionalidade | Descricao |
|----------------|-----------|
| Lista de tenants | Todos os clientes com status, plano, uso |
| Detalhes do tenant | Usuarios, fazendas, assinaturas, auditoria |
| Impersonacao | "Logar como" o cliente para suporte (com audit log) |
| Toggle status | Ativar/desativar tenant |

### 14.2 Gestao de Planos

| Funcionalidade | Descricao |
|----------------|-----------|
| CRUD de planos | Criar, editar, desativar planos de assinatura |
| Modulos inclusos | Definir quais modulos cada plano inclui |
| Precificacao dinamica | Preco por usuario, por hectare, por cabeca |
| Mudancas de plano | Upgrade/downgrade com pro-rata |

### 14.3 CRM e Comercial

| Funcionalidade | Descricao |
|----------------|-----------|
| Leads | Pipeline de conversao de leads |
| Ofertas personalizadas | Criar ofertas com modulos e precos especiais |
| Cupons | Geracao de codigos de desconto |
| Tabelas comerciais | Tabelas de precos por segmento |

### 14.4 Suporte e Qualidade

| Funcionalidade | Descricao |
|----------------|-----------|
| Tickets | Gestao de chamados de suporte |
| Chat ao vivo | Atendimento em tempo real (WebSocket) |
| Knowledge Base | Criacao e manutencao de artigos de ajuda |
| Templates de email | Personalizacao de emails transacionais |

### 14.5 Monitoramento

| Funcionalidade | Descricao |
|----------------|-----------|
| Sessoes ativas | Monitoramento de sessoes em tempo real |
| Auditoria | Log completo de acoes administrativas |
| BI / Dashboard | Metricas de uso, MRR, churn, conversao |

---

## Apendice: Mapa de Rotas do Frontend

### Autenticacao
```
/login
/register
/forgot-password
/reset-password
/convite/aceitar
```

### Dashboard Principal
```
/agricola                         — Home do modulo agricola
/agricola/dashboard               — Dashboard com KPIs
```

### Agricola
```
/agricola/safras                  — Lista de safras
/agricola/safras/[id]             — Detalhe da safra
/agricola/safras/[id]/orcamento   — Orcamento da safra
/agricola/safras/[id]/operacoes   — Operacoes da safra
/agricola/safras/[id]/caderno     — Caderno de campo da safra
/agricola/safras/[id]/checklist   — Checklists da safra
/agricola/safras/[id]/estoque     — Estoque da safra
/agricola/safras/[id]/beneficiamento — Beneficiamento
/agricola/safras/[id]/analises-solo  — Analises de solo
/agricola/safras/[id]/fenologia   — Fenologia
/agricola/safras/[id]/monitoramento — Monitoramento
/agricola/safras/[id]/ndvi        — NDVI
/agricola/safras/[id]/financeiro  — Financeiro da safra
/agricola/planejamento            — Planejamento
/agricola/romaneios               — Romaneios de colheita
/agricola/beneficiamento          — Beneficiamento geral
/agricola/operacoes               — Operacoes
/agricola/caderno                 — Caderno de campo
/agricola/defensivos              — Defensivos
/agricola/analises-solo           — Analises de solo
/agricola/fenologia               — Fenologia
/agricola/monitoramento           — Monitoramento
/agricola/climatico               — Dados climaticos
/agricola/ndvi                    — NDVI
/agricola/custos                  — Custos
/agricola/rastreabilidade         — Rastreabilidade
/agricola/mapa                    — Mapa interativo
/agricola/relatorios              — Relatorios
/agricola/checklist-templates     — Templates de checklist
/agricola/cadastros/culturas      — Cadastro de culturas
```

### Estoque e Operacional
```
/estoque                          — Gestao de estoque
/estoque/movimentacoes            — Movimentacoes
/frota                            — Gestao de frota
/frota/abastecimentos             — Abastecimentos
/frota/manutencoes                — Manutencoes
```

### Configuracoes
```
/configuracoes                    — Configuracoes gerais (SMTP, etc.)
/configuracoes/equipe             — Gestao de equipe
/configuracoes/equipe/convites    — Convites pendentes
/configuracoes/perfis-acesso      — Perfis de acesso
/configuracoes/propriedades       — Propriedades/fazendas
/configuracoes/plano              — Plano e assinatura
```

### Perfil
```
/perfil                           — Perfil do usuario
```

---

*Documento gerado em Abril 2026 — Borgus Software Ltda*
