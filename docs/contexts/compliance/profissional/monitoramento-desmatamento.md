---
modulo: Compliance Ambiental
submodulo: Monitoramento de Desmatamento
nivel: profissional
core: false
dependencias_core:
  - Identidade e Acesso
  - Cadastro da Propriedade
dependencias_modulos:
  - ../essencial/car-gestao.md
  - ../essencial/app-reserva-legal.md
standalone: true
complexidade: L
assinante_alvo:
  - medio-produtor
  - grande-produtor
  - cooperativa
  - trading-agricola
---

# Monitoramento de Desmatamento

## Descricao Funcional

O submodulo de Monitoramento de Desmatamento integra dados dos sistemas PRODES (desmatamento anual) e DETER (alertas quase tempo real) do INPE para detectar e alertar sobre mudancas de cobertura vegetal dentro dos limites das propriedades rurais. O sistema sobrepoe alertas oficiais de desmatamento aos perimetros das fazendas e gera notificacoes imediatas quando ha intersecao.

Funcionalidades principais:
- Ingestao automatica de alertas DETER (atualizacao quinzenal) e dados PRODES (atualizacao anual)
- Sobreposicao espacial dos alertas com perimetros das fazendas cadastradas
- Mapa interativo com camadas de alertas, historico de desmatamento e areas protegidas
- Classificacao de alertas: dentro da propriedade, na vizinhanca (buffer configuravel), fora de interesse
- Workflow de investigacao: alerta → analise → acao corretiva → evidencia → encerramento
- Dashboard com serie temporal de desmatamento na regiao da fazenda
- Relatorio de conformidade "desmatamento zero" para cadeias de fornecimento
- Monitoramento de fornecedores: verificar se propriedades de origem estao livres de alertas

## Personas — Quem usa este submodulo

- **Produtor Rural:** recebe alertas de desmatamento em sua propriedade e toma acoes corretivas
- **Gerente de Fazenda:** monitora alertas em todas as propriedades do grupo e prioriza investigacoes
- **Analista de Compliance:** gera relatorios de "desmatamento zero" para auditorias de clientes e certificadoras
- **Trading Agricola:** verifica historico de desmatamento de fornecedores antes de fechar compra
- **Consultor Ambiental:** investiga alertas e elabora laudos de justificativa ou defesa

## Dores que resolve

1. **Desmatamento nao autorizado:** invasores ou arrendatarios desmatam sem conhecimento do proprietario
2. **Risco reputacional:** produtores aparecem em listas de desmatadores sem oportunidade de defesa
3. **Perda de mercado:** compradores internacionais exigem comprovacao de "desmatamento zero"
4. **Monitoramento manual inviavel:** consultar DETER e PRODES manualmente para dezenas de fazendas e impraticavel
5. **Falta de evidencia:** quando alerta e falso positivo (ex: area de manejo florestal), produtor nao tem como provar
6. **Cadeia de fornecimento opaca:** tradings nao conseguem verificar conformidade de centenas de fornecedores

## Regras de Negocio

1. Alertas DETER devem ser processados automaticamente em ate 24h apos publicacao pelo INPE
2. Dados PRODES devem ser atualizados anualmente quando disponibilizados
3. A sobreposicao espacial usa intersecao geometrica com tolerancia de 30m (precisao do DETER)
4. Alertas com intersecao devem gerar notificacao imediata ao responsavel da fazenda
5. Cada alerta deve seguir workflow obrigatorio: pendente → em_investigacao → resolvido/falso_positivo
6. Alertas resolvidos devem ter evidencia anexada (foto, laudo, documento do orgao ambiental)
7. O buffer de vizinhanca e configuravel por tenant (padrao: 5km)
8. Historico de alertas deve ser mantido por no minimo 10 anos (exigencia EUDR)
9. Permissoes: `compliance:desmatamento:read`, `compliance:desmatamento:investigate`, `compliance:desmatamento:report`
10. Dados vinculados ao tenant com isolamento multi-tenant obrigatorio

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `AlertaDesmatamento` | id, tenant_id, fazenda_id, fonte (DETER/PRODES), codigo_alerta_inpe, data_deteccao, area_ha, geometria_geojson, classificacao, status_investigacao | pertence a Fazenda |
| `InvestigacaoAlerta` | id, alerta_id, responsavel_id, data_inicio, data_conclusao, parecer, tipo_resolucao (confirmado, falso_positivo, area_manejo), evidencias | pertence a AlertaDesmatamento |
| `EvidenciaInvestigacao` | id, investigacao_id, tipo (foto, laudo, documento), url_storage, descricao, data_upload | pertence a InvestigacaoAlerta |
| `MonitoramentoFornecedor` | id, tenant_id, fornecedor_id, fazenda_origem_id, ultimo_check, status_desmatamento, alertas_encontrados | pertence a Tenant |
| `HistoricoDesmatamento` | id, fazenda_id, ano, fonte, area_desmatada_ha, area_total_monitorada_ha | pertence a Fazenda |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| INPE DETER | Leitura | Ingestao de alertas quase tempo real via API ou download de shapefiles |
| INPE PRODES | Leitura | Dados anuais de desmatamento consolidado |
| `core/cadastros/fazendas` | Leitura | Perimetros das fazendas para sobreposicao espacial |
| `compliance/essencial/car-gestao` | Leitura | Areas declaradas no CAR para contextualizacao dos alertas |
| `compliance/essencial/app-reserva-legal` | Leitura | Verificar se desmatamento ocorreu em area protegida |
| `core/notificacoes` | Escrita | Alertas urgentes por e-mail e push |
| `compliance/enterprise/due-diligence` | Escrita | Dados de desmatamento alimentam due diligence EUDR |
| `comercializacao/essencial/clientes-compradores` | Leitura | Dados de fornecedores para monitoramento de cadeia |

## Fluxo de Uso Principal (step-by-step)

1. Sistema executa job periodico de ingestao de alertas DETER (a cada 24h)
2. Para cada novo alerta, executa sobreposicao espacial com perimetros das fazendas do tenant
3. Alertas com intersecao sao classificados e vinculados a fazenda correspondente
4. Responsavel recebe notificacao imediata com localizacao e area do alerta
5. Usuario acessa `/compliance/desmatamento` e visualiza mapa com alertas
6. Clica no alerta e inicia investigacao, registrando responsavel
7. Realiza vistoria em campo ou analisa imagens de satelite de alta resolucao
8. Registra parecer e anexa evidencias (fotos, laudos)
9. Encerra investigacao como "confirmado" (com acao corretiva) ou "falso positivo" (com justificativa)
10. Relatorio de conformidade "desmatamento zero" pode ser gerado a qualquer momento

## Casos Extremos e Excecoes

- **Alerta em area de manejo florestal:** desmatamento autorizado (ex: PMFS) gera alerta — investigacao deve classificar como "area de manejo" com documento de autorizacao
- **Falso positivo por nuvem/sombra:** sensoriamento remoto confunde sombra com desmatamento — evidencia de imagem limpa resolve
- **Desmatamento em area arrendada:** proprietario e alertado mas quem desmatou foi arrendatario — registro deve identificar responsabilidade
- **Fazenda sem perimetro georreferenciado:** sobreposicao impossivel — sistema alerta que a fazenda nao esta sendo monitorada
- **INPE fora do ar ou com atraso:** sistema deve funcionar com ultimo dado disponivel e indicar data da ultima atualizacao
- **Alerta em area de divisa:** desmatamento ocorreu na propriedade vizinha mas intersecta buffer — classificar como "vizinhanca"

## Criterios de Aceite (Definition of Done)

- [ ] Ingestao automatica de alertas DETER com processamento em ate 24h
- [ ] Sobreposicao espacial funcional com perimetros das fazendas
- [ ] Mapa interativo com camadas de alertas e historico
- [ ] Workflow de investigacao completo com registro de evidencias
- [ ] Notificacoes imediatas para alertas com intersecao
- [ ] Relatorio de conformidade "desmatamento zero" exportavel em PDF
- [ ] Monitoramento de fornecedores com verificacao de historico
- [ ] Dashboard com serie temporal de desmatamento
- [ ] Isolamento multi-tenant validado com testes de integracao
- [ ] Permissoes RBAC aplicadas em todas as rotas

## Sugestoes de Melhoria Futura

1. **Imagens de alta resolucao:** integracao com Planet ou Sentinel-2 para validacao visual dos alertas
2. **IA para classificacao:** modelo de machine learning para pre-classificar alertas como confirmados ou falso positivo
3. **Integracao MapBiomas:** dados anuais de uso do solo para historico mais granular
4. **Alertas de regeneracao:** detectar areas em regeneracao natural para creditos ambientais
5. **API publica para clientes:** endpoint para compradores verificarem status de desmatamento de fornecedores
6. **Integracao com blockchain:** registro imutavel de evidencias para rastreabilidade em cadeias de exportacao
