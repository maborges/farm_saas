---
modulo: "Agrícola"
submodulo: Monitoramento NDVI
nivel: profissional
core: false
dependencias_core:
  - core/auth
  - core/cadastros/fazendas
  - core/tenant
dependencias_modulos:
  - ../essencial/safras.md
  - ../essencial/caderno-campo.md
standalone: false
complexidade: XL
assinante_alvo:
  - medio-produtor
  - grande-produtor
  - cooperativa
---

# Monitoramento NDVI

## Descrição Funcional

O submódulo de Monitoramento NDVI (Normalized Difference Vegetation Index) permite ao produtor e agrônomo acompanhar a saúde da vegetação nos talhões via imagens de satélite. O NDVI é um indicador que varia de -1 a 1, onde valores próximos a 1 indicam vegetação saudável e vigorosa.

O sistema consome imagens de satélite (Sentinel-2, Landsat) processadas e gera mapas de NDVI por talhão ao longo do tempo, permitindo identificar áreas com estresse hídrico, ataque de pragas, falhas de stand ou problemas nutricionais antes que sejam visíveis a olho nu.

### Contexto Brasileiro

#### Satélites Disponíveis para o Brasil

| Satélite | Resolução Espacial | Resolução Temporal | Bandas | Custo |
|----------|-------------------|-------------------|--------|-------|
| Sentinel-2 | 10m | 5 dias | 13 | Gratuito |
| Landsat 8/9 | 30m | 16 dias | 11 | Gratuito |
| CBERS-4 (INPE) | 20m | 26 dias | 4 | Gratuito |
| PlanetScope | 3m | Diário | 4 | Pago (US$ 500-2000/mês) |

Para a maioria dos produtores brasileiros, o **Sentinel-2** oferece o melhor custo-benefício:
- Resolução de 10m adequada para talhões de 50+ hectares
- Revisita a cada 5 dias permite monitoramento frequente
- Gratuito, sem custo adicional para o produtor

#### Aplicações por Cultura no Brasil

**Soja (MT/GO/BA/PR/RS)**:
- DAP 0-30: NDVI baixo (solo exposto), identificar falhas de plantio
- DAP 30-60: NDVI em crescimento rápido (fechamento de linhas)
- DAP 60-90: NDVI máximo (pico de vigor), detectar estresse hídrico
- DAP 90+: NDVI em declínio (maturação), estimar ponto de colheita

**Milho Safrinha (MT/GO)**:
- Plantio em janeiro/fevereiro (período chuvoso)
- NDVI ajuda a identificar áreas com excesso de água (alagamento)
- Detecção precoce de ataque de lagartas (Spodoptera, Helicoverpa)

**Café (MG/SP/ES)**:
- Cultura perene, monitoramento anual
- Identificar talhões com declínio de vigor (renovação necessária)
- Correlação NDVI vs produtividade ajuda na previsão de safra

**Cana-de-açúcar (SP/MG/GO)**:
- Monitoramento de rebrota após corte
- Detecção de falhas na entrelinha
- Estimativa de tonelagem por hectare para planejamento de moagem

#### Regiões com Desafios de Nuvens

- **MATOPIBA**: Alta nebulosidade em outubro-março — pode haver períodos de 15-20 dias sem imagem útil
- **Sul (RS/SC)**: Inverno nublado — junho-agosto tem menos imagens disponíveis
- **Amazônia Legal**: Nebulosidade constante — monitoramento via satélite é limitado

Funcionalidades principais:
- Mapas de NDVI por talhão com escala de cores (vermelho a verde)
- Histórico temporal de NDVI com gráfico de evolução
- Comparativo entre talhões na mesma safra
- Alertas automáticos quando NDVI cai abaixo de limiar configurável
- Sobreposição de imagens satélite com limites do talhão
- Índices adicionais: NDRE, EVI, SAVI (módulo avançado)
- Integração com caderno de campo: vincular anomalia NDVI a registro de monitoramento
- Zonas de manejo dentro do talhão baseadas em NDVI histórico

## Personas — Quem usa este submódulo

- **Agrônomo (Cooperativa/Consultor)**: Analisa mapas de NDVI para priorizar visitas de campo em áreas com problemas. Usa NDVI para recomendar aplicação variável de fertilizantes.

- **Gerente de Fazenda (MT/GO/BA)**: Visão rápida da saúde geral de todos os talhões (10.000+ ha). Identifica problemas antes que se tornem visíveis em campo.

- **Produtor Rural**: Acompanha evolução da lavoura sem precisar percorrer toda a área. Usa NDVI para negociar venda de safra com trading (comprova qualidade).

- **Consultor Técnico**: Usa NDVI como ferramenta de diagnóstico remoto. Atende múltiplos clientes sem deslocamento constante.

- **Seguradora Rural**: Avalia danos de safra para seguro (seca, geada). NDVI histórico comprova perda de produtividade.

## Dores que resolve

1. **Área extensa**: Propriedades grandes (1000+ ha) não conseguem monitorar todos os talhões presencialmente. NDVI permite varredura completa em minutos.

2. **Detecção tardia**: Pragas e estresse hídrico são detectados tarde demais quando dependem apenas de visita de campo. NDVI mostra anomalias 7-14 dias antes de serem visíveis.

3. **Subjetividade**: Avaliação visual da lavoura varia entre observadores — NDVI é objetivo e mensurável. Dois agrônomos podem discordar visualmente, mas NDVI é consistente.

4. **Histórico de vigor**: Sem dados históricos de NDVI, impossível comparar evolução entre safras. Produtor não sabe se queda de produtividade é climática ou de manejo.

5. **Custo de drone**: Voos de drone são caros (R$ 15-30/ha) e frequentes — satélite oferece cobertura regular a custo zero após assinatura do sistema.

6. **Acesso a áreas remotas**: Talhões no MATOPIBA podem ficar inacessíveis em período de chuva. NDVI permite monitoramento remoto.

7. **Comprovação para seguro**: Produtor precisa comprovar perda para seguradora. NDVI histórico mostra queda de vigor no período do evento climático.

## Regras de Negócio

1. NDVI é calculado apenas para talhões com geometria (polígono) cadastrada no sistema
2. Imagens com mais de 30% de cobertura de nuvens são descartadas automaticamente (limiar configurável)
3. A resolução temporal depende do satélite: Sentinel-2 a cada 5 dias, Landsat a cada 16 dias
4. O NDVI médio do talhão é calculado excluindo pixels fora do polígono (mascaramento)
5. Alertas são disparados quando NDVI médio cai mais de X% em relação à medição anterior (configurável)
6. Dados históricos são armazenados por no mínimo 5 safras para comparativos
7. O usuário pode definir zonas dentro do talhão (zonas de manejo) para análise mais granular
8. Índices avançados (NDRE, EVI, SAVI) requerem módulo `ndvi_avancado` ativo
9. Imagens brutas não são armazenadas — apenas os índices calculados e thumbnails
10. **Período de entressafra**: NDVI próximo a zero é normal — sistema não deve gerar alertas se safra está encerrada
11. **Geometria mínima**: Talhões menores que 1 hectare podem ter leitura imprecisa — alertar usuário
12. Permissões: `agricola:ndvi:read`, `agricola:ndvi:configure`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `NDVILeitura` | id, tenant_id, talhao_id, safra_id, data_imagem, ndvi_medio, ndvi_min, ndvi_max, desvio_padrao, satelite, cobertura_nuvens_pct | pertence a Talhão/Safra |
| `NDVIMapa` | id, leitura_id, url_thumbnail, url_geotiff, bbox | imagem processada |
| `NDVIAlerta` | id, leitura_id, tipo_alerta, variacao_pct, lido, resolvido | alertas gerados |
| `NDVIConfiguracao` | id, tenant_id, limiar_nuvens_pct, limiar_alerta_variacao_pct, indices_ativos | config por tenant |
| `ZonaManejo` | id, talhao_id, nome, geometria_geojson, tipo | subdivisão do talhão |
| `NDVHHistorico` | id, talhao_id, data, ndvi_medio, safra_id | histórico multi-safra |

## Integrações Necessárias

| Sistema/Modulo | Tipo | Descrição |
|----------------|------|-----------|
| `core/cadastros/fazendas` | Leitura | Geometria (polígono) dos talhões |
| `agricola/safras` | Leitura | Período da safra para filtrar imagens relevantes |
| `agricola/caderno-campo` | Escrita | Vincular anomalia NDVI a registro de monitoramento |
| `agricola/prescricoes` | Escrita | Gerar prescrição VRT baseada em mapa NDVI (Enterprise) |
| `api/sentinel-hub` ou `api/google-earth-engine` | Leitura | Obter imagens e calcular índices |
| `notificacoes` | Escrita | Disparar alertas de queda de NDVI |
| `agricola/custos` | Leitura | Correlacionar NDVI com custo de insumos aplicados |

## Fluxo de Uso Principal (step-by-step)

1. Sistema executa job periódico (diário) para buscar novas imagens de satélite dos talhões cadastrados
2. Para cada imagem disponível, calcula NDVI (e outros índices se configurados)
3. Aplica máscara do polígono do talhão e filtra imagens com excesso de nuvens
4. Armazena leitura com NDVI médio, min, max e thumbnail do mapa
5. Verifica limiares de alerta — se variação excede configuração, cria alerta
6. Usuário acessa `/agricola/safras/[id]/ndvi` e visualiza mapa de NDVI do talhão
7. Navega pelo histórico temporal usando slider de datas
8. Identifica zona com NDVI baixo (vermelha no mapa) — ex: NDVI 0.3 vs média 0.7
9. Clica na zona e cria registro de monitoramento vinculado (caderno de campo)
10. **Diagnóstico**: Sistema sugere causas possíveis (estresse hídrico, praga, deficiência nutricional)
11. Agrônomo agenda visita de campo na área identificada
12. Após visita, atualiza registro com diagnóstico e recomendação
13. **Zonas de manejo**: Usuário pode delimitar zonas baseadas em NDVI histórico para VRT
14. **Correlação com produtividade**: Ao final da safra, sistema correlaciona NDVI com produtividade real

## Casos Extremos e Exceções

- **Talhão sem geometria**: NDVI não pode ser calculado — exibir mensagem solicitando cadastro do polígono

- **Período nublado prolongado**: Semanas sem imagem utilizável (comum no MATOPIBA em dezembro-janeiro) — exibir última leitura disponível com flag "desatualizado"

- **Talhão recém-colhido**: NDVI cai drasticamente após colheita — não gerar alerta se safra está em status `colhida`

- **Solo exposto entre safras**: NDVI próximo a zero é normal — sistema deve distinguir safra ativa de entressafra

- **Talhão muito pequeno**: Talhões menores que a resolução do satélite (10m Sentinel) geram leituras imprecisas — alertar o usuário

- **Mudança de polígono**: Se o talhão é redesenhado, leituras históricas mantêm referência ao polígono original

- **Falha na API do satélite**: Sistema deve ter retry com backoff e notificar admin se indisponível por mais de 48h

- **Nuvem parcial**: Nuvem cobre apenas parte do talhão — calcular NDVI apenas na área limpa, alertar sobre cobertura parcial

- **Sombra de nuvem**: Sombra pode ser confundida com NDVI baixo — usar banda de nuvem/sombra para filtragem

- **Cultura perene (café/cana)**: NDVI não zera na entressafra — ajustar limiares de alerta para culturas perenes

## Critérios de Aceite (Definition of Done)

- [ ] Job periódico funcional consumindo API de satélite
- [ ] Cálculo de NDVI com mascaramento por polígono do talhão
- [ ] Filtragem automática de imagens com excesso de nuvens
- [ ] Mapa de NDVI renderizado com escala de cores no frontend
- [ ] Histórico temporal com navegação por datas
- [ ] Alertas automáticos de queda de NDVI
- [ ] Vinculação de anomalia com registro no caderno de campo
- [ ] Configuração de limiares por tenant
- [ ] Suporte a índices avançados (NDRE, EVI) quando módulo ativo
- [ ] Tenant isolation em todas as leituras e configurações
- [ ] Tratamento de erros de API externa com retry
- [ ] Identificação de períodos de entressafra (não alertar)
- [ ] Zonas de manejo baseadas em NDVI histórico

## Sugestões de Melhoria Futura

1. **Integração com drones**: Importar imagens de drone para NDVI de alta resolução (1-5m)

2. **Machine Learning para detecção de anomalias**: Modelo treinado com histórico para alertas mais precisos

3. **Comparativo regional**: NDVI do talhão vs média da região (benchmarking com dados de outros tenants anonimizados)

4. **Prescrição automática VRT**: Gerar mapa de aplicação variável diretamente do NDVI (Enterprise)

5. **Notificação push**: Alerta no celular quando NDVI cai abruptamente

6. **Timelapse**: Animação da evolução do NDVI ao longo da safra

7. **Integração com estação meteorológica**: Correlacionar NDVI com dados de precipitação e temperatura

8. **Previsão de produtividade**: Modelo preditivo que estima produtividade baseado em NDVI no pico de vigor

9. **Índices específicos por cultura**: NDVI para soja, NDRE para milho, EVI para cana

10. **Detecção de geada**: Alerta automático quando imagem pós-geada mostra queda brusca de NDVI

11. **Integração com IBGE/CONAB**: Comparar NDVI da região com estimativas oficiais de safra

12. **API para traders**: Exportar NDVI para trading de grãos (avaliação de risco de safra)
