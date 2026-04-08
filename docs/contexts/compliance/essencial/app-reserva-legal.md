---
modulo: Compliance Ambiental
submodulo: APP e Reserva Legal
nivel: essencial
core: false
dependencias_core:
  - Identidade e Acesso
  - Cadastro da Propriedade
dependencias_modulos:
  - ./car-gestao.md
  - ../../agricola/essencial/safras.md
standalone: true
complexidade: M
assinante_alvo:
  - pequeno-produtor
  - medio-produtor
  - grande-produtor
  - cooperativa
---

# APP e Reserva Legal

## Descricao Funcional

O submodulo de APP (Area de Preservacao Permanente) e Reserva Legal permite ao produtor monitorar a conformidade das areas protegidas de suas propriedades conforme o Codigo Florestal (Lei 12.651/2012). O sistema importa as delimitacoes declaradas no CAR, sobrepoe com imagens de satelite e gera alertas quando detecta uso indevido, degradacao ou deficit de vegetacao nativa.

Funcionalidades principais:
- Mapeamento visual de APPs (margens de rios, nascentes, topos de morro, encostas) e Reserva Legal
- Calculo automatico do percentual de Reserva Legal exigido por bioma (20% Mata Atlantica, 35% Cerrado na Amazonia Legal, 80% Amazonia)
- Deteccao de deficit ou superavit de Reserva Legal com base na area efetiva de vegetacao nativa
- Alertas de invasao de APP por atividades agricolas ou pastagem
- Acompanhamento de planos de recuperacao (PRA/PRAD) com cronograma e marcos
- Mapa interativo com camadas de APP, RL, uso do solo e hidrografia
- Relatorio de situacao ambiental por fazenda para fins de fiscalizacao ou credito

## Personas — Quem usa este submodulo

- **Produtor Rural:** visualiza areas protegidas de sua propriedade e verifica se esta em conformidade
- **Agronomo:** planeja operacoes evitando areas de APP e RL, orienta recuperacao
- **Consultor Ambiental:** elabora laudos de situacao ambiental e acompanha PRA
- **Gerente de Fazenda:** monitora conformidade de multiplas propriedades e prioriza acoes corretivas
- **Fiscal Ambiental (externo):** recebe relatorios gerados pelo sistema como evidencia de conformidade

## Dores que resolve

1. **Desconhecimento dos limites:** produtor nao sabe exatamente onde comecam e terminam suas APPs
2. **Deficit de Reserva Legal:** muitas propriedades tem deficit historico e nao sabem o tamanho do passivo
3. **Invasao acidental de APP:** operacoes mecanizadas avancam sobre APP por falta de demarcacao clara
4. **PRA sem acompanhamento:** planos de recuperacao sao protocolados mas nao monitorados na pratica
5. **Risco regulatorio:** propriedades irregulares perdem acesso a credito rural e podem ser embargadas
6. **Calculo manual de percentuais:** cada bioma tem regra diferente para RL, gerando erros de calculo

## Regras de Negocio

1. O percentual minimo de Reserva Legal depende do bioma e localizacao (Amazonia Legal vs demais regioes)
2. APPs sao definidas pela legislacao e nao podem ser suprimidas — qualquer uso e considerado irregular
3. A largura da APP de margem de rio depende da largura do curso d'agua (30m a 500m conforme Art. 4)
4. APPs de nascente tem raio minimo de 50 metros
5. Superavit de Reserva Legal pode ser compensado via Cota de Reserva Ambiental (CRA)
6. Deficit de Reserva Legal deve ser regularizado via PRA, compensacao ou regeneracao
7. Propriedades com ate 4 modulos fiscais tem regras diferenciadas (Art. 67 do Codigo Florestal)
8. O sistema nao substitui laudo tecnico — dados sao indicativos e devem ser validados por profissional habilitado
9. Permissoes: `compliance:app_rl:read`, `compliance:app_rl:update`, `compliance:app_rl:report`
10. Dados vinculados ao tenant com isolamento multi-tenant obrigatorio

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `AreaProtegida` | id, tenant_id, fazenda_id, tipo (APP_margem, APP_nascente, APP_topo, APP_encosta, reserva_legal), area_ha, geometria_geojson, status_vegetacao | pertence a Fazenda |
| `DeficitRL` | id, tenant_id, fazenda_id, bioma, percentual_exigido, percentual_atual, area_deficit_ha, data_calculo | pertence a Fazenda |
| `PlanoRecuperacao` | id, tenant_id, fazenda_id, tipo (PRA, PRAD), numero_protocolo, data_inicio, data_previsao_fim, status, orgao_responsavel | pertence a Fazenda |
| `MarcoRecuperacao` | id, plano_id, descricao, data_prevista, data_realizada, evidencia_url, status | pertence a PlanoRecuperacao |
| `AlertaAPP` | id, area_protegida_id, tipo_alerta, descricao, data_deteccao, geometria_invasao_geojson, resolvido | pertence a AreaProtegida |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `compliance/essencial/car-gestao` | Leitura | Importa delimitacoes de APP e RL declaradas no CAR |
| `core/cadastros/fazendas` | Leitura | Dados da fazenda, area total, bioma, modulos fiscais |
| `core/cadastros/talhoes` | Leitura | Geometrias dos talhoes para deteccao de sobreposicao com APP/RL |
| `agricola/essencial/operacoes-campo` | Leitura | Verifica se operacoes foram realizadas dentro de areas protegidas |
| Satelite (Sentinel-2/Planet) | Leitura | Imagens para deteccao de mudanca de cobertura vegetal |
| IBGE/MMA | Leitura | Dados de bioma e hidrografia para calculo de APP |

## Fluxo de Uso Principal (step-by-step)

1. Usuario acessa `/compliance/app-reserva-legal` e seleciona a fazenda
2. Sistema exibe mapa com camadas de APP e Reserva Legal importadas do CAR
3. Calculo automatico do percentual de RL exigido com base no bioma e localizacao
4. Sistema compara area de vegetacao nativa atual com o exigido e exibe deficit/superavit
5. Em caso de deficit, sistema sugere opcoes: regeneracao natural, plantio, compensacao via CRA
6. Usuario pode registrar um PRA/PRAD com cronograma de marcos
7. Sistema monitora periodicamente imagens de satelite e gera alertas de invasao de APP
8. Para cada alerta, usuario registra acao corretiva e evidencia fotografica
9. Relatorio de situacao ambiental pode ser exportado em PDF para bancos ou fiscalizacao
10. Dashboard consolidado mostra conformidade de todas as fazendas do tenant

## Casos Extremos e Excecoes

- **Propriedade em dois biomas:** fazenda na transicao Cerrado/Amazonia — percentual de RL deve considerar o bioma predominante ou aplicar regra por talhao
- **APP de rio intermitente:** rios que secam em parte do ano — APP deve ser mantida com base na maior largura historica
- **Reserva Legal em condominio:** proprietarios vizinhos que averbam RL em conjunto — sistema deve permitir referencia cruzada
- **Propriedade com area menor que 4 modulos fiscais:** regras simplificadas do Art. 67 — RL pode ser a vegetacao existente em 22/07/2008
- **Mudanca de legislacao estadual:** alguns estados tem regras complementares mais restritivas — parametrizacao por UF
- **Imagem de satelite com nuvens:** deteccao falha em periodos chuvosos — sistema deve indicar data da ultima analise confiavel

## Criterios de Aceite (Definition of Done)

- [ ] Mapa interativo com camadas de APP e Reserva Legal renderizando corretamente
- [ ] Calculo automatico de deficit/superavit de RL por bioma
- [ ] Importacao de areas do CAR com sobreposicao visual aos talhoes
- [ ] Alertas de invasao de APP com localizacao geografica
- [ ] CRUD de Planos de Recuperacao com marcos e evidencias
- [ ] Relatorio PDF de situacao ambiental por fazenda
- [ ] Regras diferenciadas para propriedades ate 4 modulos fiscais
- [ ] Testes de integracao com isolamento multi-tenant
- [ ] Permissoes RBAC aplicadas em todas as rotas
- [ ] Dashboard consolidado de conformidade

## Sugestoes de Melhoria Futura

1. **NDVI para monitoramento de regeneracao:** usar indice de vegetacao para acompanhar evolucao de areas em recuperacao
2. **Integracao com CRA:** marketplace de Cotas de Reserva Ambiental para compensacao de deficit
3. **Alertas preditivos:** machine learning para prever risco de degradacao com base em padroes historicos
4. **App mobile para vistoria:** coleta de evidencias fotograficas georreferenciadas em campo
5. **Integracao com SICAR automatica:** sincronizar delimitacoes quando o CAR for retificado
6. **Calculo de servicos ecossistemicos:** estimar valor economico da vegetacao nativa preservada
