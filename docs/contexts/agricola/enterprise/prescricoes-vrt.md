---
modulo: "Agrícola"
submodulo: Prescrições VRT
nivel: enterprise
core: false
dependencias_core:
  - core/auth
  - core/cadastros/fazendas
  - core/cadastros/produtos
  - core/tenant
dependencias_modulos:
  - ../essencial/safras.md
  - ../essencial/operacoes-campo.md
  - ../profissional/monitoramento-ndvi.md
  - ../profissional/custos-producao.md
standalone: false
complexidade: XL
assinante_alvo:
  - grande-produtor
  - cooperativa
  - agricultura-de-precisao
---

# Prescrições VRT (Taxa Variável)

## Descrição Funcional

O submódulo de Prescrições VRT (Variable Rate Technology) permite criar mapas de aplicação com taxa variável para operações agrícolas. Em vez de aplicar a mesma dosagem de insumo em todo o talhão, a VRT ajusta a dosagem metro a metro com base em mapas de fertilidade do solo, NDVI, produtividade histórica ou zonas de manejo.

O sistema gera arquivos de prescrição compatíveis com os principais controladores de máquinas (formato Shapefile, ISO-XML, ISOBUS), que são carregados nos equipamentos para execução automática da aplicação variável.

### Contexto Brasileiro

#### Adoção de VRT no Brasil

A Agricultura de Precisão no Brasil tem crescido rapidamente:

- **Soja no MT/GO**: 60-70% das propriedades >1000ha usam VRT para fertilizantes
- **Milho Safrinha**: 40-50% de adoção em propriedades médias e grandes
- **Cana-de-açúcar (SP)**: 80% das usinas usam VRT para correção de solo
- **Café (MG/SP)**: 30-40% em regiões de café especial (Cerrado Mineiro, Mogiana)

#### Economia com VRT

Estudos da Embrapa e universidades brasileiras mostram:

| Cultura | Insumo | Economia Média | ROI Típico |
|---------|--------|----------------|------------|
| Soja | Fertilizante (NPK) | 10-20% | 3:1 a 5:1 |
| Milho | Fertilizante (NPK) | 15-25% | 4:1 a 7:1 |
| Café | Calcário | 20-30% | 5:1 a 10:1 |
| Cana | Corretivos | 15-25% | 4:1 a 6:1 |

**Exemplo real (Sorriso-MT)**:
- Fazenda de 5.000ha de soja
- Aplicação uniforme: 400kg/ha de NPK em toda a área
- VRT: 250kg/ha em zonas férteis, 500kg/ha em zonas pobres (média 350kg/ha)
- Economia: 50kg/ha × 5.000ha = 250 toneladas de fertilizante
- Valor: 250t × R$ 2.500/t = R$ 625.000 de economia por safra

#### Fontes de Dados para VRT no Brasil

**Análise de Solo por Grade Amostral**:
- Amostragem a cada 2-5 hectares (grid 200m × 200m ou 500m × 500m)
- Parâmetros: pH, MO, P, K, Ca, Mg, Al, V%
- Laboratórios credenciados pelo MAPA
- Custo: R$ 80-150 por amostra

**NDVI/Satélite**:
- Sentinel-2 (gratuito, 10m resolução)
- Mapas de vigor para aplicação variável de nitrogênio em cobertura
- Custo: zero (satélite gratuito)

**Mapa de Produtividade**:
- Colheitadeiras com monitor de colheita (John Deere, Case IH, New Holland)
- Dados de produtividade a cada segundo
- Identifica zonas de alta/baixa produtividade

**Condutividade Elétrica do Solo**:
- Sensor Veris ou similar
- Mapeia variabilidade de textura e matéria orgânica
- Custo: R$ 15-30/ha

Funcionalidades principais:
- Criação de mapas de prescrição baseados em: análise de solo, NDVI, mapa de produtividade, zonas de manejo
- Editor visual de zonas com ajuste de dosagem por zona
- Cálculo automático de quantidade total de insumo necessário
- Exportação em formatos compatíveis: Shapefile (.shp), ISO-XML, CSV georreferenciado
- Histórico de prescrições por talhão/safra
- Comparativo de custo: aplicação uniforme vs taxa variável
- Integração com mapas NDVI para prescrição automática
- Compatibilidade com controladores: John Deere Operations Center, Case IH AFS, New Holland PLM, Trimble

## Personas — Quem usa este submódulo

- **Agrônomo de Precisão (Cooperativa/Consultor)**: Cria prescrições baseadas em dados de solo e satélite. Usa ferramentas de zoneamento para delimitar áreas com necessidades diferentes.

- **Operador de Máquina**: Carrega arquivo de prescrição no controlador do equipamento (ex: John Deere GreenStar, Trimble FMX). Executa aplicação automática com taxa variável.

- **Consultor Técnico**: Analisa dados e recomenda dosagens por zona. Compara resultado econômico da VRT vs aplicação uniforme.

- **Gerente de Fazenda**: Avalia economia gerada pela aplicação variável. Decide se investe em equipamento VRT ou terceiriza operação.

- **Produtor de Café Especial (Cerrado Mineiro)**: Usa VRT para aplicar fertilizantes em zonas de alta produtividade, maximizando qualidade do café.

## Dores que resolve

1. **Desperdício de insumo**: Aplicação uniforme gasta insumo demais em áreas férteis e de menos em áreas pobres. Fertilizante é 60% do custo — economia de 15% impacta diretamente o lucro.

2. **Produtividade desigual**: Sem VRT, áreas com deficiência nutricional não recebem correção adequada. Zonas de baixa produtividade continuam produzindo pouco.

3. **Custo alto de insumos**: Fertilizantes e corretivos representam 30-40% do custo — VRT pode reduzir 10-20%. Em 1000ha de soja, economia de R$ 150.000-300.000 por safra.

4. **Impacto ambiental**: Excesso de fertilizante causa lixiviação e contaminação de aquíferos. VRT aplica apenas o necessário, reduzindo impacto ambiental.

5. **Incompatibilidade de formatos**: Cada marca de máquina usa formato diferente — converter manualmente é trabalhoso. Sistema exporta em múltiplos formatos automaticamente.

6. **Falta de histórico**: Produtor não tem histórico de aplicações variáveis para comparar evolução da fertilidade do solo.

7. **Retorno desconhecido**: Produtor não sabe se investimento em VRT valeu a pena. Sistema compara custo VRT vs uniforme e mostra economia real.

## Regras de Negócio

1. Prescrições só podem ser criadas para talhões com geometria (polígono) cadastrada
2. O mapa de prescrição deve cobrir 100% da área do talhão — não pode haver lacunas
3. A dosagem mínima e máxima por zona devem respeitar limites do produto (registro MAPA)
4. O cálculo de quantidade total considera: `soma(area_zona * dosagem_zona)` para todas as zonas
5. O formato de exportação deve ser selecionado pelo usuário conforme o equipamento disponível
6. Cada prescrição deve ter referência à fonte de dados utilizada (análise de solo, NDVI, produtividade)
7. Prescrições aprovadas geram vínculo com a operação executada para rastreabilidade
8. Alterações em prescrições aprovadas geram nova versão (imutabilidade)
9. O sistema deve alertar quando a quantidade total prescrita excede o estoque disponível do insumo
10. **Zonas de preservação**: APP ou reserva legal dentro do talhão devem ter dosagem zero (não aplicar)
11. **Resolução do grid**: Grid muito fino (<10m) pode gerar arquivo grande demais para controlador — alertar usuário
12. Permissões: `agricola:prescricoes:create/read/update/export`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `Prescricao` | id, tenant_id, safra_id, talhao_id, produto_id, tipo_fonte (solo/ndvi/produtividade/manual), status, versao, data_criacao, aprovado_por | pertence a Safra/Talhão |
| `PrescricaoZona` | id, prescricao_id, zona_manejo_id, geometria_geojson, dosagem_kg_ha, area_ha | dosagem por zona |
| `PrescricaoExportacao` | id, prescricao_id, formato, url_arquivo, data_exportacao | arquivo gerado |
| `ZonaManejo` | id, talhao_id, nome, geometria_geojson, fertilidade_classe, ndvi_medio | subdivisão do talhão |
| `MapaProdutividade` | id, talhao_id, safra_id, url_geotiff, produtividade_media_kg_ha | mapa de colheita |
| `AmostraSolo` | id, talhao_id, ponto_amostragem_geojson, data_coleta, ph, mo, p, k, ca, mg, al, v_pct | análise de solo |
| `RecomendacaoAdubacao` | id, amostra_id, cultura, npk_recomendado, calcario_recomendado | recomendação por amostra |

## Integrações Necessárias

| Sistema/Modulo | Tipo | Descrição |
|----------------|------|-----------|
| `agricola/monitoramento-ndvi` | Leitura | Mapa NDVI como fonte para prescrição |
| `agricola/analises-solo` | Leitura | Resultados de análise de solo por zona |
| `agricola/operacoes` | Escrita | Vincular prescrição à operação executada |
| `agricola/custos` | Escrita | Calcular economia da VRT vs aplicação uniforme |
| `operacional/estoque` | Leitura | Verificar disponibilidade do insumo prescrito |
| `core/cadastros/fazendas` | Leitura | Geometria do talhão |
| `operacional/frota` | Leitura | Verificar compatibilidade do equipamento com VRT |
| `api/laboratorio-solo` | Leitura | Importar resultados de análise de solo diretamente do laboratório |

## Fluxo de Uso Principal (step-by-step)

1. Agrônomo acessa `/dashboard/agricola/prescricoes` e seleciona "Nova Prescrição"
2. Seleciona safra, talhão e produto (ex: KCl para adubação potássica)
3. Escolhe fonte de dados: mapa de fertilidade do solo, NDVI, mapa de produtividade ou manual
4. **Análise de solo**: Sistema importa resultados do laboratório (pH, P, K, MO, V%)
5. **Zoneamento automático**: Sistema divide talhão em zonas baseadas na fonte de dados
6. Para cada zona, sistema sugere dosagem baseada na fonte de dados e na recomendação agronômica
7. **Recomendação Embrapa**: Sistema consulta tabela de recomendação (ex: Comissão de Química e Fertilidade do Solo)
8. Agrônomo ajusta dosagens conforme necessidade — editor visual mostra mapa com cores por dosagem
9. Sistema calcula quantidade total de insumo necessário e verifica estoque
10. **Comparativo**: Sistema mostra custo da aplicação uniforme vs taxa variável
11. Agrônomo finaliza e envia para aprovação
12. Gerente aprova a prescrição
13. Agrônomo exporta arquivo no formato do equipamento (Shapefile, ISO-XML)
14. **Compatibilidade**: Sistema verifica formato do controlador (John Deere, Case IH, Trimble)
15. Operador carrega arquivo no controlador da máquina e executa a aplicação
16. **As-applied**: Máquina registra aplicação real (telemetria) — sistema compara com prescrição
17. Após execução, operação é registrada vinculada à prescrição para rastreabilidade

## Casos Extremos e Exceções

- **Talhão sem análise de solo**: Não há dados para gerar prescrição automática — permitir criação manual por zonas desenhadas pelo agrônomo

- **NDVI muito antigo**: Dados de NDVI com mais de 30 dias — alertar sobre defasagem

- **Zona de preservação dentro do talhão**: APP ou reserva legal no meio do polígono — excluir automaticamente da prescrição (dosagem = 0)

- **Equipamento sem VRT**: Produtor não tem controlador compatível — gerar prescrição com dosagem média única (fallback uniforme)

- **Formato não suportado**: Marca de máquina exótica — oferecer CSV genérico como alternativa

- **Prescrição com dosagem zero**: Zona com fertilidade alta não precisa de aplicação — permitir dosagem zero

- **Resolução do grid**: Grade muito fina gera arquivo grande que o controlador não suporta — permitir ajuste de resolução

- **Talhão com declividade acentuada**: Áreas com >20% de declive podem ter restrição de aplicação — alertar operador

- **Condições climáticas**: Prescrição não deve ser executada com chuva ou vento forte — integrar com previsão do tempo

- **Telemetria falha**: Máquina não enviou dados as-applied — permitir registro manual da área aplicada

## Critérios de Aceite (Definition of Done)

- [ ] Criação de prescrição com seleção de fonte de dados (solo, NDVI, produtividade, manual)
- [ ] Editor visual de zonas com mapa e cores por dosagem
- [ ] Cálculo automático de quantidade total por zona e total geral
- [ ] Sugestão automática de dosagem baseada na fonte selecionada
- [ ] Exportação em Shapefile e ISO-XML funcional
- [ ] Verificação de estoque do insumo ao finalizar prescrição
- [ ] Fluxo de aprovação com versionamento
- [ ] Vinculação de prescrição à operação executada
- [ ] Comparativo de custo VRT vs uniforme
- [ ] Tenant isolation e RBAC testados
- [ ] Validação de geometria (sem lacunas, sem sobreposição de zonas)
- [ ] Suporte a múltiplos formatos (John Deere, Case IH, Trimble, ISO-XML)
- [ ] Exclusão automática de zonas de preservação (APP, reserva legal)

## Sugestões de Melhoria Futura

1. **Prescrição por IA**: Modelo de machine learning que sugere dosagem ótima baseado em histórico de resposta da cultura

2. **Integração telemetria**: Receber dados "as-applied" da máquina e comparar com prescrição (planejado vs executado)

3. **ISOBUS Task Controller**: Comunicação direta com controlador via ISOBUS sem necessidade de USB

4. **Prescrição de sementes**: VRT para população variável de plantio (sementes/m)

5. **Simulador de ROI**: Calcular retorno sobre investimento da VRT baseado em histórico de produtividade

6. **Marketplace de prescrições**: Compartilhar prescrições entre agrônomos da mesma cooperativa

7. **Integração com laboratórios**: Importar resultados de análise de solo diretamente do laboratório (via API)

8. **Prescrição de defensivos**: VRT para herbicidas/fungicidas baseado em NDVI e histórico de pragas

9. **Zoneamento por condutividade elétrica**: Importar mapas de condutividade do solo (Veris) para zoneamento

10. **Prescrição para irrigação**: VRT para água de irrigação baseado em capacidade de retenção do solo

11. **Recomendação automática de calcário**: Calcular necessidade de calagem baseada em análise de solo e cultura

12. **Integração com estações meteorológicas**: Ajustar prescrição baseado em previsão de chuva (evitar lixiviação)
