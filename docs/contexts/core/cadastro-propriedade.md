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

## Personas — Quem usa este submódulo

- **Administrador do Tenant (Owner):** Cadastra novas propriedades, define dados legais e fiscais, importa mapas georreferenciados.
- **Gestor de Fazenda:** Atualiza informações da propriedade sob sua responsabilidade, gerencia hierarquia de talhões e glebas.
- **Agrônomo / Consultor Técnico:** Consulta mapas e áreas para planejamento de safra, recomendações de manejo e laudos técnicos.
- **Operador de Campo:** Visualiza mapas e localização de talhões para execução de operações diárias.

## Dores que resolve

1. **Dados cadastrais dispersos:** Sem centralização, informações de CNPJ, CAR e áreas ficam em planilhas, cartórios e sistemas diferentes.
2. **Falta de georreferenciamento digital:** Propriedades sem mapa digital dificultam planejamento de safra, cálculo de insumos e fiscalização ambiental.
3. **Hierarquia de áreas inexistente:** Sem estrutura Fazenda → Talhão → Gleba, é impossível rastrear operações por área específica.
4. **Infraestrutura não catalogada:** Sem registro de silos, currais e galpões, o controle de capacidade e manutenção é feito "de cabeça".
5. **Dificuldade em auditorias:** Sem CAR e IE vinculados digitalmente, preparar documentação para auditorias ambientais e fiscais é demorado.

## Regras de Negócio

1. **RN-CP-001:** Toda fazenda deve ter pelo menos: nome, CPF ou CNPJ do proprietário, estado (UF) e área total em hectares.
2. **RN-CP-002:** O código CAR (Cadastro Ambiental Rural) deve ter formato válido para o estado informado (2 letras UF + sequência numérica).
3. **RN-CP-003:** A hierarquia é fixa: `Fazenda → Talhão → Gleba`. Talhão pertence a exatamente uma Fazenda. Gleba pertence a exatamente um Talhão.
4. **RN-CP-004:** A soma das áreas dos talhões não pode exceder a área total da fazenda (tolerância de 5% para arredondamento).
5. **RN-CP-005:** Upload de shapefiles aceita formatos: `.shp` (com `.dbf`, `.shx`, `.prj`), `.kml`, `.kmz`, `.geojson`.
6. **RN-CP-006:** Coordenadas geográficas devem estar no sistema de referência SIRGAS 2000 (EPSG:4674), padrão brasileiro.
7. **RN-CP-007:** Cada fazenda é vinculada a exatamente um `tenant_id`. Não existe fazenda sem tenant.
8. **RN-CP-008:** Exclusão de fazenda só é permitida se não houver safras, lotes de gado ou operações vinculadas. Caso contrário, apenas inativação.
9. **RN-CP-009:** Infraestrutura cadastrada deve ter tipo (enum: sede, silo, curral, galpão, oficina, outro), capacidade (quando aplicável) e coordenada GPS opcional.

## Entidades de Dados Principais

| Entidade | Campos-chave | Relacionamentos |
|----------|-------------|-----------------|
| `Fazenda` | id, tenant_id, nome, cpf_cnpj, inscricao_estadual, codigo_car, uf, municipio, area_total_ha, geojson, is_active | → Tenant, → Talhao[], → Infraestrutura[], → FazendaUsuario[] |
| `Talhao` | id, fazenda_id, nome, codigo, area_ha, geojson, tipo_solo, uso_atual | → Fazenda, → Gleba[], → Safra[] (módulo agrícola) |
| `Gleba` | id, talhao_id, nome, area_ha, geojson | → Talhao |
| `Infraestrutura` | id, fazenda_id, nome, tipo (enum), capacidade, unidade_capacidade, latitude, longitude, observacoes | → Fazenda |
| `ArquivoGeo` | id, fazenda_id, nome_arquivo, formato, tamanho_bytes, s3_key, uploaded_at | → Fazenda |

## Integrações Necessárias

- **Serviço de Geocodificação (Google Maps / Nominatim):** Conversão de endereço em coordenadas e vice-versa.
- **Validação de CNPJ (Receita Federal / API pública):** Consulta automática de dados cadastrais a partir do CNPJ.
- **SICAR (Sistema Nacional de Cadastro Ambiental Rural):** Validação e consulta de código CAR (quando API disponível).
- **S3 / MinIO:** Armazenamento de arquivos georreferenciados (shapefiles, KML).
- **Leaflet / MapLibre (frontend):** Renderização de mapas com polígonos de talhões e marcadores de infraestrutura.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Cadastro de nova propriedade
1. Owner acessa "Propriedades" → "Nova Propriedade".
2. Preenche dados obrigatórios: nome, CPF/CNPJ, UF, município, área total.
3. Opcionalmente preenche: IE, CAR, endereço completo.
4. Sistema valida formato de CPF/CNPJ e CAR.
5. Fazenda é criada vinculada ao `tenant_id` do owner.
6. Owner é redirecionado à tela de detalhes para adicionar talhões.

### Fluxo 2: Importação de mapa georreferenciado
1. Na tela de detalhes da fazenda, usuário clica em "Importar Mapa".
2. Faz upload de arquivo shapefile (.shp + .dbf + .shx + .prj) ou KML/GeoJSON.
3. Backend converte para GeoJSON e valida SIRGAS 2000.
4. Sistema renderiza preview do mapa com polígonos identificados.
5. Usuário associa cada polígono a um talhão (existente ou novo).
6. Polígonos são salvos no campo `geojson` de cada talhão.

### Fluxo 3: Cadastro de hierarquia de áreas
1. Na tela de detalhes da fazenda, aba "Talhões".
2. Usuário clica em "Novo Talhão", preenche nome, código, área e tipo de solo.
3. Opcionalmente desenha o polígono diretamente no mapa (sem upload de arquivo).
4. Dentro do talhão, pode criar glebas (subdivisões).
5. Sistema valida que soma das áreas dos talhões ≤ 105% da área total da fazenda.

## Casos Extremos e Exceções

- **CNPJ inválido ou inexistente na Receita Federal:** Sistema permite o cadastro com aviso de que o CNPJ não foi validado. Flag `cnpj_validado = false`.
- **Shapefile com sistema de coordenadas diferente de SIRGAS 2000:** Sistema tenta reprojetar automaticamente. Se falhar, solicita upload em SIRGAS 2000.
- **Área dos talhões excede 105% da área total:** Cadastro dos talhões é bloqueado até que a área total seja corrigida ou o talhão excedente seja redimensionado.
- **Fazenda com safras ativas tenta ser excluída:** Exclusão bloqueada. Exibe mensagem com lista de safras vinculadas. Permite apenas inativação.
- **Upload de shapefile corrompido ou incompleto:** Backend valida presença dos 4 arquivos obrigatórios (.shp, .dbf, .shx, .prj). Rejeita com mensagem descritiva se faltar algum.
- **Dois talhões com polígonos sobrepostos:** Sistema detecta overlap via cálculo geométrico e exibe alerta (não bloqueia, pois pode ser intencional em culturas consorciadas).

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de Fazenda com validação de CPF/CNPJ e CAR.
- [ ] Hierarquia Fazenda → Talhão → Gleba funcional com validação de soma de áreas.
- [ ] Upload e processamento de shapefiles (.shp), KML e GeoJSON.
- [ ] Conversão automática para SIRGAS 2000 quando possível.
- [ ] Renderização de mapa interativo com polígonos de talhões.
- [ ] CRUD de infraestrutura com tipos pré-definidos e coordenadas GPS.
- [ ] Isolamento de dados por `tenant_id` validado em todos os endpoints.
- [ ] Inativação (soft delete) de fazendas com dependências ativas.
- [ ] Testes de integração cobrindo upload de shapefiles e validação geográfica.
- [ ] Responsividade: mapa funcional em telas de tablet (uso em campo).

## Sugestões de Melhoria Futura

1. **Integração com drones para mapeamento aéreo:** Upload direto de ortomosaicos gerados por drones com conversão automática em polígonos de talhões.
2. **Histórico de uso do solo por talhão:** Registro temporal de culturas plantadas, permitindo análise de rotação e pousio.
3. **Integração com INCRA/SIGEF:** Importação automática de dados fundiários e certificação de georreferenciamento.
4. **Alertas de sobreposição com áreas protegidas:** Cruzamento do mapa da fazenda com bases de APP, Reserva Legal e Unidades de Conservação.
5. **QR Code por talhão:** Gerar QR Code para identificação rápida em campo via app mobile.
6. **Cálculo automático de área via GPS do celular:** Permitir que o operador "caminhe" o perímetro do talhão para gerar o polígono.
