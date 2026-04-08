---
modulo: Core
submodulo: Cadastro da Propriedade
nivel: core
core: true
dependencias_core:
  - Identidade e Acesso
dependencias_modulos: []
standalone: false
complexidade: M
assinante_alvo: todos os assinantes
---

# Cadastro da Propriedade

## Descrição Funcional

Submódulo responsável pelo registro completo de propriedades rurais na plataforma. Abrange o cadastro de dados legais (nome, CNPJ/CPF, Inscrição Estadual, código CAR), a hierarquia de áreas (Fazenda → Talhão → Gleba), geolocalização com upload de shapefiles e KML, e o registro de infraestrutura (sedes, silos, currais, galpões). Serve como base cadastral para todos os módulos de negócio que operam sobre áreas e estruturas da propriedade.

Este submódulo é o alicerce de toda a plataforma AgroSaaS. Sem uma propriedade cadastrada corretamente, não é possível registrar safras, rebanhos, operações ou custos. O cadastro segue as normas do INCRA e da Receita Federal para garantir conformidade com ITR, CAR e programas de crédito rural.

A hierarquia de áreas permite rastreabilidade completa: cada operação (plantio, pulverização, colheita) é vinculada a um talhão específico, possibilitando cálculo de produtividade, custo por hectare e histórico de uso do solo.

## Personas — Quem usa este submódulo

- **Administrador do Tenant (Owner):** Cadastra novas propriedades, define dados legais e fiscais, importa mapas georreferenciados. Precisa de visão completa do patrimônio fundiário para tomada de decisão estratégica e compliance fiscal.

- **Gestor de Fazenda:** Atualiza informações da propriedade sob sua responsabilidade, gerencia hierarquia de talhões e glebas. Registra infraestrutura (currais, silos) e mantém mapas atualizados para planejamento operacional.

- **Agrônomo / Consultor Técnico:** Consulta mapas e áreas para planejamento de safra, recomendações de manejo e laudos técnicos. Precisa de precisão geográfica para prescrição de insumos em taxa variável.

- **Operador de Campo:** Visualiza mapas e localização de talhões para execução de operações diárias. Usa coordenadas GPS para navegação em campo e identificação de áreas de manejo.

- **Contador Rural:** Consulta dados fiscais (CNPJ, IE, CAR, área total) para apuração de ITR e obrigações acessórias. Precisa de informações precisas para evitar autuações fiscais.

- **Técnico de Regularização Ambiental:** Verifica código CAR, áreas de APP e Reserva Legal para compliance ambiental. Interface com órgãos fiscalizadores (SICAR, IBAMA).

## Dores que resolve

1. **Dados cadastrais dispersos:** Sem centralização, informações de CNPJ, CAR e áreas ficam em planilhas, cartórios e sistemas diferentes. Produtor perde horas reunindo documentação para banco ou auditoria.

2. **Falta de georreferenciamento digital:** Propriedades sem mapa digital dificultam planejamento de safra, cálculo de insumos e fiscalização ambiental. Mapa em papel não permite análise espacial.

3. **Hierarquia de áreas inexistente:** Sem estrutura Fazenda → Talhão → Gleba, é impossível rastrear operações por área específica. Produtor não sabe produtividade por talhão nem custo por hectare.

4. **Infraestrutura não catalogada:** Sem registro de silos, currais e galpões, o controle de capacidade e manutenção é feito "de cabeça". Quebra de equipamento por falta de manutenção preventiva.

5. **Dificuldade em auditorias:** Sem CAR e IE vinculados digitalmente, preparar documentação para auditorias ambientais e fiscais é demorado. Risco de multas por informação inconsistente.

6. **Divergência de áreas:** Área da matrícula, área do CAR e área operacional (talhões) divergem. Produtor não sabe qual valor usar para ITR ou planejamento.

7. **Ausência de histórico de uso:** Sem registro temporal de culturas por talhão, não há como fazer rotação adequada ou comprovar práticas sustentáveis para certificações.

## Regras de Negócio

1. **RN-CP-001:** Toda fazenda deve ter pelo menos: nome, CPF ou CNPJ do proprietário, estado (UF) e área total em hectares. Campos obrigatórios para conformidade com Lei 9.393/1996 (ITR).

2. **RN-CP-002:** O código CAR (Cadastro Ambiental Rural) deve ter formato válido para o estado informado (2 letras UF + sequência numérica de 12 dígitos). Validação conforme Manual Técnico do SICAR.

3. **RN-CP-003:** A hierarquia é fixa: `Fazenda → Talhão → Gleba`. Talhão pertence a exatamente uma Fazenda. Gleba pertence a exatamente um Talhão. Não existe gleba avulsa.

4. **RN-CP-004:** A soma das áreas dos talhões não pode exceder a área total da fazenda (tolerância de 5% para arredondamento e sobreposição de APP). Divergência maior gera alerta bloqueante.

5. **RN-CP-005:** Upload de shapefiles aceita formatos: `.shp` (com `.dbf`, `.shx`, `.prj`), `.kml`, `.kmz`, `.geojson`. Arquivo deve estar em SIRGAS 2000 (EPSG:4674) ou sistema converte automaticamente.

6. **RN-CP-006:** Coordenadas geográficas devem estar no sistema de referência SIRGAS 2000 (EPSG:4674), padrão brasileiro conforme IN MAPA 01/2020. Conversão de WGS84 é automática.

7. **RN-CP-007:** Cada fazenda é vinculada a exatamente um `tenant_id`. Não existe fazenda sem tenant. Exclusão de tenant em cascata inativa todas as fazendas (soft delete).

8. **RN-CP-008:** Exclusão de fazenda só é permitida se não houver safras, lotes de gado ou operações vinculadas. Caso contrário, apenas inativação (`is_active = false`).

9. **RN-CP-009:** Infraestrutura cadastrada deve ter tipo (enum: sede, silo, curral, galpão, oficina, outro), capacidade (quando aplicável) e coordenada GPS opcional. Tipos padronizados conforme NBR 15.575.

10. **RN-CP-010:** NIRF (Número do Imóvel na Receita Federal) é único por estado. Validação de dígito verificador conforme algoritmo da RFB (IN RFB 1.902/2019).

11. **RN-CP-011:** Módulos fiscais são calculados automaticamente pela área total e município (tabela INCRA). Campo editável apenas por contador com justificativa.

12. **RN-CP-012:** Área de APP e Reserva Legal devem ser registradas como talhões com tipo especial. Soma de APP + RL deve respeitar percentual mínimo por bioma (Lei 12.651/2012).

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `Fazenda` | id (UUID), tenant_id (UUID FK), nome (String 100), cpf_cnpj (String 18), inscricao_estadual (String 20), codigo_car (String 20), nirf (String 20), uf (Char 2), municipio (String 100), area_total_ha (Decimal 12,4), area_aproveitavel_ha (Decimal 12,4), area_app_ha (Decimal 12,4), area_rl_ha (Decimal 12,4), modulos_fiscais (Decimal 6,2), geojson (JSONB), is_active (Boolean), created_at (DateTime) | → Tenant, → Talhao[], → Infraestrutura[], → FazendaUsuario[], → ImovelRural[] |
| `Talhao` | id (UUID), fazenda_id (UUID FK), nome (String 100), codigo (String 20), area_ha (Decimal 12,4), geojson (JSONB), tipo_solo (Enum), uso_atual (String 50), tipo_talhao (Enum: producao/app/rl/outro), created_at (DateTime) | → Fazenda, → Gleba[], → SafraAgricola[], → Operacao[] |
| `Gleba` | id (UUID), talhao_id (UUID FK), nome (String 100), area_ha (Decimal 12,4), geojson (JSONB), observacao (Text) | → Talhao |
| `Infraestrutura` | id (UUID), fazenda_id (UUID FK), nome (String 100), tipo (Enum: sede/silo/curral/galpao/oficina/outro), capacidade (Decimal 12,2), unidade_capacidade (String 20), latitude (Decimal 10,8), longitude (Decimal 11,8), observacoes (Text), created_at (DateTime) | → Fazenda |
| `ArquivoGeo` | id (UUID), fazenda_id (UUID FK), nome_arquivo (String 255), formato (Enum: shp/kml/kmz/geojson), tamanho_bytes (Integer), s3_key (String 512), uploaded_by (UUID FK), uploaded_at (DateTime) | → Fazenda, → Usuario |
| `Cartorio` | id (UUID), nome (String 255), comarca (String 100), uf (Char 2), codigo_censec (String 20) | → ImovelRural[] |

## Integrações Necessárias

- **Serviço de Geocodificação (Google Maps / Nominatim):** Conversão de endereço em coordenadas e vice-versa. Útil para localizar sede da fazenda a partir do nome/município.

- **Validação de CNPJ (Receita Federal / API pública):** Consulta automática de dados cadastrais a partir do CNPJ. Valida situação cadastral e endereço.

- **SICAR (Sistema Nacional de Cadastro Ambiental Rural):** Validação e consulta de código CAR (quando API disponível). Verifica se imóvel está regular no CAR.

- **SNCR (Sistema Nacional de Cadastro Rural — INCRA):** Consulta de módulos fiscais por município e validação de CCIR. Integração futura via API INCRA.

- **S3 / MinIO:** Armazenamento de arquivos georreferenciados (shapefiles, KML). URLs assinadas para download seguro.

- **Leaflet / MapLibre (frontend):** Renderização de mapas com polígonos de talhões e marcadores de infraestrutura. Tiles do IBGE ou Mapbox.

- **IBGE (API de Malha Municipal):** Validação de município/UF e obtenção de código IBGE para integração com sistemas governamentais.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Cadastro de nova propriedade
1. Owner acessa "Propriedades" → "Nova Propriedade".
2. Preenche dados obrigatórios: nome, CPF/CNPJ, UF, município, área total.
3. Opcionalmente preenche: IE, CAR, NIRF, endereço completo, coordenadas da sede.
4. Sistema valida formato de CPF/CNPJ (algoritmo oficial) e CAR (formato SICAR).
5. Se CNPJ informado, sistema consulta Receita Federal e preenche endereço automaticamente.
6. Fazenda é criada vinculada ao `tenant_id` do owner.
7. Owner é redirecionado à tela de detalhes para adicionar talhões e infraestrutura.

### Fluxo 2: Importação de mapa georreferenciado
1. Na tela de detalhes da fazenda, usuário clica em "Importar Mapa".
2. Faz upload de arquivo shapefile (.shp + .dbf + .shx + .prj) ou KML/GeoJSON.
3. Backend converte para SIRGAS 2000 se necessário e extrai polígonos.
4. Sistema renderiza preview do mapa com polígonos identificados sobre imagem de satélite.
5. Usuário associa cada polígono a um talhão (existente ou novo) e define tipo (produção, APP, RL).
6. Polígonos são salvos no campo `geojson` de cada talhão.
7. Sistema valida que soma das áreas dos talhões ≤ 105% da área total da fazenda.

### Fluxo 3: Cadastro de hierarquia de áreas
1. Na tela de detalhes da fazenda, aba "Talhões".
2. Usuário clica em "Novo Talhão", preenche nome, código, área e tipo de solo.
3. Opcionalmente desenha o polígono diretamente no mapa (ferramenta de desenho).
4. Sistema calcula área do polígono desenhado e sugere o valor.
5. Dentro do talhão, pode criar glebas (subdivisões para manejo diferenciado).
6. Sistema valida que soma das áreas dos talhões ≤ 105% da área total da fazenda.
7. Talhões do tipo APP/RL não entram no cálculo de área aproveitável.

### Fluxo 4: Cadastro de infraestrutura
1. Na tela de detalhes da fazenda, aba "Infraestrutura".
2. Usuário clica em "Nova Infraestrutura", seleciona tipo (silo, curral, galpão, etc.).
3. Preenche nome, capacidade (ex: 5000 toneladas para silo), unidade.
4. Opcionalmente clica no mapa para marcar coordenadas GPS da estrutura.
5. Sistema exibe marcador no mapa. Usuário pode ajustar posição com precisão.
6. Infraestrutura é salva e listada com foto opcional (upload futuro).

## Casos Extremos e Exceções

- **CNPJ inválido ou inexistente na Receita Federal:** Sistema permite o cadastro com aviso de que o CNPJ não foi validado. Flag `cnpj_validado = false`. Contador deve regularizar posteriormente.

- **Shapefile com sistema de coordenadas diferente de SIRGAS 2000:** Sistema tenta reprojetar automaticamente usando bibliotecas PROJ.4. Se falhar, solicita upload em SIRGAS 2000 e oferece guia de conversão.

- **Área dos talhões excede 105% da área total:** Cadastro dos talhões é bloqueado até que a área total seja corrigida ou o talhão excedente seja redimensionado. Mensagem clara: "Soma dos talhões (X ha) excede área total (Y ha) em Z%."

- **Fazenda com safras ativas tenta ser excluída:** Exclusão bloqueada. Exibe mensagem com lista de safras vinculadas: "Esta fazenda possui 3 safras ativas. Inative a fazenda ao invés de excluir."

- **Upload de shapefile corrompido ou incompleto:** Backend valida presença dos 4 arquivos obrigatórios (.shp, .dbf, .shx, .prj). Rejeita com mensagem descritiva se faltar algum: "Arquivo .prj não encontrado. Este arquivo define o sistema de coordenadas."

- **Dois talhões com polígonos sobrepostos:** Sistema detecta overlap via cálculo geométrico (Shapely) e exibe alerta (não bloqueia, pois pode ser intencional em culturas consorciadas). Alerta: "Talhões A e B possuem 15% de sobreposição."

- **Fazenda em divisa de estados:** Propriedade que abrange dois municípios/estados diferentes. Sistema permite cadastro com município principal e registra observação. Área total é rateada proporcionalmente (futuro).

- **CAR pendente de análise:** Imóvel com CAR protocolado mas não aprovado. Sistema aceita código com status "Em análise" e exibe badge amarelo.

- **NIRF não encontrado na RFB:** Imóvel em processo de regularização fiscal. Campo NIRF é opcional. Sistema exibe alerta: "NIRF não informado — imóvel pode ter pendência fiscal."

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de Fazenda com validação de CPF/CNPJ e CAR.
- [ ] Hierarquia Fazenda → Talhão → Gleba funcional com validação de soma de áreas.
- [ ] Upload e processamento de shapefiles (.shp), KML e GeoJSON.
- [ ] Conversão automática para SIRGAS 2000 quando possível.
- [ ] Renderização de mapa interativo com polígonos de talhões e marcadores de infraestrutura.
- [ ] CRUD de infraestrutura com tipos pré-definidos e coordenadas GPS.
- [ ] Isolamento de dados por `tenant_id` validado em todos os endpoints.
- [ ] Inativação (soft delete) de fazendas com dependências ativas.
- [ ] Testes de integração cobrindo upload de shapefiles e validação geográfica.
- [ ] Responsividade: mapa funcional em telas de tablet (uso em campo).
- [ ] Validação de formato de CAR por estado (UF + 12 dígitos).
- [ ] Cálculo automático de área do polígono desenhado no mapa.

## Sugestões de Melhoria Futura

1. **Integração com drones para mapeamento aéreo:** Upload direto de ortomosaicos gerados por drones com conversão automática em polígonos de talhões. Processamento em nuvem.

2. **Histórico de uso do solo por talhão:** Registro temporal de culturas plantadas, permitindo análise de rotação e pousio. Relatório de conformidade para certificações.

3. **Integração com INCRA/SIGEF:** Importação automática de dados fundiários e certificação de georreferenciamento. Validação de sobreposição com terras indígenas/quilombolas.

4. **Alertas de sobreposição com áreas protegidas:** Cruzamento do mapa da fazenda com bases de APP, Reserva Legal e Unidades de Conservação. Notificação de passivo ambiental.

5. **QR Code por talhão:** Gerar QR Code para identificação rápida em campo via app mobile. Operador escaneia e registra operação diretamente no talhão.

6. **Cálculo automático de área via GPS do celular:** Permitir que o operador "caminhe" o perímetro do talhão para gerar o polígono. Precisão de 2-5 metros com GNSS de smartphone.

7. **Mapa de produtividade sobreposto:** Importar mapas de colheita de máquinas com monitor e exibir produtividade por talhão diretamente no mapa.

8. **Integração com Sentinel-2:** Imagens de satélite gratuitas para monitoramento de NDVI e detecção de estresse vegetativo.
