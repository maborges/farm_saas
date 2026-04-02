---
modulo: "Agr\xEDcola"
submodulo: "Prescri\xE7\xF5es VRT"
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

# Prescricoes VRT (Taxa Variavel)

## Descricao Funcional

O submodulo de Prescricoes VRT (Variable Rate Technology) permite criar mapas de aplicacao com taxa variavel para operacoes agricolas. Em vez de aplicar a mesma dosagem de insumo em todo o talhao, a VRT ajusta a dosagem metro a metro com base em mapas de fertilidade do solo, NDVI, produtividade historica ou zonas de manejo.

O sistema gera arquivos de prescricao compativeis com os principais controladores de maquinas (formato Shapefile, ISO-XML, ISOBUS), que sao carregados nos equipamentos para execucao automatica da aplicacao variavel.

Funcionalidades principais:
- Criacao de mapas de prescricao baseados em: analise de solo, NDVI, mapa de produtividade, zonas de manejo
- Editor visual de zonas com ajuste de dosagem por zona
- Calculo automatico de quantidade total de insumo necessario
- Exportacao em formatos compatveis: Shapefile (.shp), ISO-XML, CSV georreferenciado
- Historico de prescricoes por talhao/safra
- Comparativo de custo: aplicacao uniforme vs taxa variavel
- Integracao com mapas NDVI para prescricao automatica

## Personas — Quem usa este submodulo

- **Agronomo de Precisao:** cria prescricoes baseadas em dados de solo e satelite
- **Operador de Maquina:** carrega arquivo de prescricao no controlador do equipamento
- **Consultor Tecnico:** analisa dados e recomenda dosagens por zona
- **Gerente de Fazenda:** avalia economia gerada pela aplicacao variavel

## Dores que resolve

1. **Desperdicio de insumo:** aplicacao uniforme gasta insumo demais em areas ferteis e de menos em areas pobres
2. **Produtividade desigual:** sem VRT, areas com deficiencia nutricional nao recebem correcao adequada
3. **Custo alto de insumos:** fertilizantes e corretivos representam 30-40% do custo — VRT pode reduzir 10-20%
4. **Impacto ambiental:** excesso de fertilizante causa lixiviacao e contaminacao de aquiferos
5. **Incompatibilidade de formatos:** cada marca de maquina usa formato diferente — converter manualmente e trabalhoso

## Regras de Negocio

1. Prescricoes so podem ser criadas para talhoes com geometria (poligono) cadastrada
2. O mapa de prescricao deve cobrir 100% da area do talhao — nao pode haver lacunas
3. A dosagem minima e maxima por zona devem respeitar limites do produto (registro MAPA)
4. O calculo de quantidade total considera: `soma(area_zona * dosagem_zona)` para todas as zonas
5. O formato de exportacao deve ser selecionado pelo usuario conforme o equipamento disponivel
6. Cada prescricao deve ter referencia a fonte de dados utilizada (analise de solo, NDVI, produtividade)
7. Prescricoes aprovadas geram vinculo com a operacao executada para rastreabilidade
8. Alteracoes em prescricoes aprovadas geram nova versao (imutabilidade)
9. O sistema deve alertar quando a quantidade total prescrita excede o estoque disponivel do insumo
10. Permissoes: `agricola:prescricoes:create/read/update/export`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `Prescricao` | id, tenant_id, safra_id, talhao_id, produto_id, tipo_fonte (solo/ndvi/produtividade/manual), status, versao, data_criacao, aprovado_por | pertence a Safra/Talhao |
| `PrescricaoZona` | id, prescricao_id, zona_manejo_id, geometria_geojson, dosagem_kg_ha, area_ha | dosagem por zona |
| `PrescricaoExportacao` | id, prescricao_id, formato, url_arquivo, data_exportacao | arquivo gerado |
| `ZonaManejo` | id, talhao_id, nome, geometria_geojson, fertilidade_classe, ndvi_medio | subdivisao do talhao |
| `MapaProdutividade` | id, talhao_id, safra_id, url_geotiff, produtividade_media_kg_ha | mapa de colheita |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `agricola/monitoramento-ndvi` | Leitura | Mapa NDVI como fonte para prescricao |
| `agricola/analises-solo` | Leitura | Resultados de analise de solo por zona |
| `agricola/operacoes` | Escrita | Vincular prescricao a operacao executada |
| `agricola/custos` | Escrita | Calcular economia da VRT vs aplicacao uniforme |
| `operacional/estoque` | Leitura | Verificar disponibilidade do insumo prescrito |
| `core/cadastros/fazendas` | Leitura | Geometria do talhao |
| `operacional/frota` | Leitura | Verificar compatibilidade do equipamento com VRT |

## Fluxo de Uso Principal (step-by-step)

1. Agronomo acessa `/dashboard/agricola/prescricoes` e seleciona "Nova Prescricao"
2. Seleciona safra, talhao e produto (ex: KCl para adubacao potassica)
3. Escolhe fonte de dados: mapa de fertilidade do solo, NDVI ou mapa de produtividade
4. Sistema carrega mapa base e divide talhao em zonas de manejo (automatico ou manual)
5. Para cada zona, sistema sugere dosagem baseada na fonte de dados e na recomendacao agronomica
6. Agronomo ajusta dosagens conforme necessidade — editor visual mostra mapa com cores por dosagem
7. Sistema calcula quantidade total de insumo necessario e verifica estoque
8. Agronomo finaliza e envia para aprovacao
9. Gerente aprova a prescricao
10. Agronomo exporta arquivo no formato do equipamento (Shapefile, ISO-XML)
11. Operador carrega arquivo no controlador da maquina e executa a aplicacao
12. Apos execucao, operacao e registrada vinculada a prescricao para rastreabilidade

## Casos Extremos e Excecoes

- **Talhao sem analise de solo:** nao ha dados para gerar prescricao automatica — permitir criacao manual por zonas desenhadas pelo agronomo
- **NDVI muito antigo:** dados de NDVI com mais de 30 dias — alertar sobre defasagem
- **Zona de preservacao dentro do talhao:** APP ou reserva legal no meio do poligono — excluir automaticamente da prescricao (dosagem = 0)
- **Equipamento sem VRT:** produtor nao tem controlador compativel — gerar prescricao com dosagem media unica (fallback uniforme)
- **Formato nao suportado:** marca de maquina exotica — oferecer CSV generico como alternativa
- **Prescricao com dosagem zero:** zona com fertilidade alta nao precisa de aplicacao — permitir dosagem zero
- **Resolucao do grid:** grade muito fina gera arquivo grande que o controlador nao suporta — permitir ajuste de resolucao

## Criterios de Aceite (Definition of Done)

- [ ] Criacao de prescricao com selecao de fonte de dados (solo, NDVI, produtividade, manual)
- [ ] Editor visual de zonas com mapa e cores por dosagem
- [ ] Calculo automatico de quantidade total por zona e total geral
- [ ] Sugestao automatica de dosagem baseada na fonte selecionada
- [ ] Exportacao em Shapefile e ISO-XML funcional
- [ ] Verificacao de estoque do insumo ao finalizar prescricao
- [ ] Fluxo de aprovacao com versionamento
- [ ] Vinculacao de prescricao a operacao executada
- [ ] Comparativo de custo VRT vs uniforme
- [ ] Tenant isolation e RBAC testados
- [ ] Validacao de geometria (sem lacunas, sem sobreposicao de zonas)

## Sugestoes de Melhoria Futura

1. **Prescricao por IA:** modelo de machine learning que sugere dosagem otima baseado em historico de resposta da cultura
2. **Integracao telemetrica:** receber dados "as-applied" da maquina e comparar com prescricao (planejado vs executado)
3. **ISOBUS Task Controller:** comunicacao direta com controlador via ISOBUS sem necessidade de USB
4. **Prescricao de sementes:** VRT para populacao variavel de plantio (sementes/m)
5. **Simulador de ROI:** calcular retorno sobre investimento da VRT baseado em historico de produtividade
6. **Marketplace de prescricoes:** compartilhar prescricoes entre agronomos da mesma cooperativa
7. **Integracao com laboratorios:** importar resultados de analise de solo diretamente do laboratorio (via API)
