---
modulo: "Agr\xEDcola"
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

## Descricao Funcional

O submodulo de Monitoramento NDVI (Normalized Difference Vegetation Index) permite ao produtor e agronomo acompanhar a saude da vegetacao nos talhoes via imagens de satelite. O NDVI e um indicador que varia de -1 a 1, onde valores proximos a 1 indicam vegetacao saudavel e vigorosa.

O sistema consome imagens de satelite (Sentinel-2, Landsat) processadas e gera mapas de NDVI por talhao ao longo do tempo, permitindo identificar areas com estresse hidrico, ataque de pragas, falhas de stand ou problemas nutricionais antes que sejam visiveis a olho nu.

Funcionalidades principais:
- Mapas de NDVI por talhao com escala de cores (vermelho a verde)
- Historico temporal de NDVI com grafico de evolucao
- Comparativo entre talhoes na mesma safra
- Alertas automaticos quando NDVI cai abaixo de limiar configuravel
- Sobreposicao de imagens satelite com limites do talhao
- Indices adicionais: NDRE, EVI, SAVI (modulo avancado)
- Integracao com caderno de campo: vincular anomalia NDVI a registro de monitoramento

## Personas — Quem usa este submodulo

- **Agronomo:** analisa mapas de NDVI para priorizar visitas de campo em areas com problemas
- **Gerente de Fazenda:** visao rapida da saude geral de todos os talhoes
- **Produtor Rural:** acompanha evolucao da lavoura sem precisar percorrer toda a area
- **Consultor Tecnico:** usa NDVI como ferramenta de diagnostico remoto

## Dores que resolve

1. **Area extensa:** propriedades grandes (1000+ ha) nao conseguem monitorar todos os talhoes presencialmente
2. **Deteccao tardia:** pragas e estresse hidrico sao detectados tarde demais quando dependem apenas de visita de campo
3. **Subjetividade:** avaliacao visual da lavoura varia entre observadores — NDVI e objetivo e mensuravel
4. **Historico de vigor:** sem dados historicos de NDVI, impossivel comparar evolucao entre safras
5. **Custo de drone:** voos de drone sao caros e frequentes — satelite oferece cobertura regular a custo zero

## Regras de Negocio

1. NDVI e calculado apenas para talhoes com geometria (poligono) cadastrada no sistema
2. Imagens com mais de 30% de cobertura de nuvens sao descartadas automaticamente (limiar configuravel)
3. A resolucao temporal depende do satelite: Sentinel-2 a cada 5 dias, Landsat a cada 16 dias
4. O NDVI medio do talhao e calculado excluindo pixels fora do poligono (mascaramento)
5. Alertas sao disparados quando NDVI medio cai mais de X% em relacao a medicao anterior (configuravel)
6. Dados historicos sao armazenados por no minimo 5 safras para comparativos
7. O usuario pode definir zonas dentro do talhao (zonas de manejo) para analise mais granular
8. Indices avancados (NDRE, EVI, SAVI) requerem modulo `ndvi_avancado` ativo
9. Imagens brutas nao sao armazenadas — apenas os indices calculados e thumbnails
10. Permissoes: `agricola:ndvi:read`, `agricola:ndvi:configure`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `NDVILeitura` | id, tenant_id, talhao_id, safra_id, data_imagem, ndvi_medio, ndvi_min, ndvi_max, desvio_padrao, satelite, cobertura_nuvens_pct | pertence a Talhao/Safra |
| `NDVIMapa` | id, leitura_id, url_thumbnail, url_geotiff, bbox | imagem processada |
| `NDVIAlerta` | id, leitura_id, tipo_alerta, variacao_pct, lido, resolvido | alertas gerados |
| `NDVIConfiguracao` | id, tenant_id, limiar_nuvens_pct, limiar_alerta_variacao_pct, indices_ativos | config por tenant |
| `ZonaManejo` | id, talhao_id, nome, geometria_geojson, tipo | subdivisao do talhao |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `core/cadastros/fazendas` | Leitura | Geometria (poligono) dos talhoes |
| `agricola/safras` | Leitura | Periodo da safra para filtrar imagens relevantes |
| `agricola/caderno-campo` | Escrita | Vincular anomalia NDVI a registro de monitoramento |
| `agricola/prescricoes` | Escrita | Gerar prescricao VRT baseada em mapa NDVI (Enterprise) |
| API Satelite (Sentinel Hub / Google Earth Engine) | Leitura | Obter imagens e calcular indices |
| `notificacoes` | Escrita | Disparar alertas de queda de NDVI |

## Fluxo de Uso Principal (step-by-step)

1. Sistema executa job periodico (diario) para buscar novas imagens de satelite dos talhoes cadastrados
2. Para cada imagem disponivel, calcula NDVI (e outros indices se configurados)
3. Aplica mascara do poligono do talhao e filtra imagens com excesso de nuvens
4. Armazena leitura com NDVI medio, min, max e thumbnail do mapa
5. Verifica limiares de alerta — se variacao excede configuracao, cria alerta
6. Usuario acessa `/agricola/safras/[id]/ndvi` e visualiza mapa de NDVI do talhao
7. Navega pelo historico temporal usando slider de datas
8. Identifica zona com NDVI baixo (vermelha no mapa)
9. Clica na zona e cria registro de monitoramento vinculado (caderno de campo)
10. Agronomo agenda visita de campo na area identificada
11. Apos visita, atualiza registro com diagnostico e recomendacao

## Casos Extremos e Excecoes

- **Talhao sem geometria:** NDVI nao pode ser calculado — exibir mensagem solicitando cadastro do poligono
- **Periodo nublado prolongado:** semanas sem imagem utilizavel — exibir ultima leitura disponivel com flag "desatualizado"
- **Talhao recem-colhido:** NDVI cai drasticamente apos colheita — nao gerar alerta se safra esta em status `colhida`
- **Solo exposto entre safras:** NDVI proximo a zero e normal — sistema deve distinguir safra ativa de entressafra
- **Talhao muito pequeno:** talhoes menores que a resolucao do satelite (10m Sentinel) geram leituras imprecisas — alertar o usuario
- **Mudanca de poligono:** se o talhao e redesenhado, leituras historicas mantêm referencia ao poligono original
- **Falha na API do satelite:** sistema deve ter retry com backoff e notificar admin se indisponivel por mais de 48h

## Criterios de Aceite (Definition of Done)

- [ ] Job periodico funcional consumindo API de satelite
- [ ] Calculo de NDVI com mascaramento por poligono do talhao
- [ ] Filtragem automatica de imagens com excesso de nuvens
- [ ] Mapa de NDVI renderizado com escala de cores no frontend
- [ ] Historico temporal com navegacao por datas
- [ ] Alertas automaticos de queda de NDVI
- [ ] Vinculacao de anomalia com registro no caderno de campo
- [ ] Configuracao de limiares por tenant
- [ ] Suporte a indices avancados (NDRE, EVI) quando modulo ativo
- [ ] Tenant isolation em todas as leituras e configuracoes
- [ ] Tratamento de erros de API externa com retry

## Sugestoes de Melhoria Futura

1. **Integracao com drones:** importar imagens de drone para NDVI de alta resolucao
2. **Machine Learning para deteccao de anomalias:** modelo treinado com historico para alertas mais precisos
3. **Comparativo regional:** NDVI do talhao vs media da regiao (benchmarking)
4. **Prescricao automatica VRT:** gerar mapa de aplicacao variavel diretamente do NDVI
5. **Notificacao push:** alerta no celular quando NDVI cai abruptamente
6. **Timelapse:** animacao da evolucao do NDVI ao longo da safra
7. **Integracao com estacao meteorologica:** correlacionar NDVI com dados de precipitacao e temperatura
