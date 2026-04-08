---
modulo: Imóveis Rurais
submodulo: Cadastro de Imóvel
nivel: essencial
core: false
dependencias_core:
  - cadastro-propriedade
  - identidade-acesso
dependencias_modulos: []
standalone: false
complexidade: M
assinante_alvo:
  - proprietário rural
  - contador agrícola
  - advogado rural
---

# Cadastro de Imóvel Rural

## Descrição Funcional

Submódulo responsável pelo registro e manutenção das informações cadastrais dos imóveis rurais vinculados às fazendas do tenant. Centraliza os dados identificadores obrigatórios para obrigações fiscais (ITR), creditícias (acesso a crédito rural) e fundiárias (INCRA/SNCR), criando uma base documental confiável para toda a gestão patrimonial da propriedade.

Este submódulo implementa as exigências da Lei 9.393/1996 (ITR), IN RFB 1.902/2019 (NIRF), e normas do INCRA para cadastro de imóveis rurais. Cada imóvel é vinculado a uma fazenda existente no sistema, representando a dimensão legal da propriedade operacional.

Uma fazenda pode ter um ou mais imóveis (ex.: matrículas distintas que compõem a propriedade operacional, desmembramentos, glebas separadas). O sistema permite rateio de área total da fazenda entre múltiplos imóveis.

## Personas — Quem usa este submódulo

- **Proprietário Rural (Owner):** Registra e mantém os dados dos imóveis; precisa de visão consolidada do patrimônio fundiário para tomada de decisão, financiamento e planejamento sucessório.

- **Contador Agrícola:** Consulta NIRF, área total e módulos fiscais para apuração de ITR, entrega de DITR e LCDPR. Precisa de dados precisos para evitar autuações fiscais.

- **Advogado Rural / Assessor Jurídico:** Verifica matrícula, transcrição e situação do registro de imóveis para due diligence, aquisições e regularizações fundiárias.

- **Gerente de Fazenda:** Consulta dados do imóvel para abertura de financiamentos e crédito rural. Bancos exigem documentação completa para análise.

- **Técnico de Regularização Fundiária:** Responsável por manter cadastro atualizado junto ao INCRA/SNCR. Monitora pendências e certificações.

- **Gestor de Crédito Rural:** Compila documentação de imóveis para submissão a programas de financiamento (Plano Safra, Moderfrota, ABC).

## Dores que resolve

1. **Dados dispersos:** Matrícula, NIRF e CCIR em gavetas e pastas físicas, sem acesso digital rápido. Produtor perde dias reunindo documentação para banco.

2. **Desconhecimento de vencimentos:** CCIR e ITR vencem anualmente; sem controle centralizado há multas e bloqueios de crédito rural. Multa de CCIR é de 10% ao mês.

3. **Inconsistência de área:** Divergência entre área da matrícula, área do INCRA e área operacional (talhões). Produtor não sabe qual valor usar para ITR.

4. **Dificuldade de acesso a crédito:** Bancos exigem documentação fundiária organizada; produtores perdem tempo reunindo documentos e perdem prazo de safra.

5. **Gestão de múltiplos imóveis:** Proprietários com várias matrículas não têm visão consolidada do patrimônio. Dificulta planejamento sucessório e garantia de financiamentos.

6. **Imóvel sem NIRF:** Produtores desconhecem obrigatoriedade do NIRF para ITR. Sistema identifica e orienta regularização.

7. **Falta de histórico de transmissões:** Compras, partilhas e desmembramentos não são registrados. Em caso de fiscalização, não há comprovação de regularidade.

## Regras de Negócio

1. **RN-CI-001:** Todo imóvel deve pertencer a exatamente um `tenant_id` e estar vinculado a uma `fazenda_id` existente. Imóvel sem fazenda é órfão e não pode ser criado.

2. **RN-CI-002:** O campo `matricula` é único por cartório; combinação `(cartorio_id, numero_matricula)` deve ser única no tenant. Validação de duplicidade.

3. **RN-CI-003:** `nirf` (Número do Imóvel na Receita Federal) é único no sistema — não pode haver dois imóveis com mesmo NIRF. Validação de dígito verificador conforme algoritmo da RFB.

4. **RN-CI-004:** `area_total_ha` deve ser positiva e consistente com a soma dos talhões (alerta se divergência > 5%). Divergência exige justificativa.

5. **RN-CI-005:** `modulos_fiscais` é calculado automaticamente pela Receita Federal; o campo é informativo e editável apenas por contador com justificativa.

6. **RN-CI-006:** Imóvel não pode ser excluído se houver documentos legais ou contratos de arrendamento ativos vinculados. Exclusão é lógica (`deleted_at`).

7. **RN-CI-007:** Alteração de `area_total_ha` requer justificativa obrigatória (campo `motivo_alteracao_area`). Histórico de alterações é registrado.

8. **RN-CI-008:** NIRF deve seguir formato válido: 12 dígitos numéricos + dígito verificador (algoritmo Módulo 11 da RFB).

9. **RN-CI-009:** Código CAR deve ser vinculado ao imóvel quando disponível. CAR é obrigatório para todos os imóveis rurais (Lei 12.651/2012).

10. **RN-CI-010:** Imóvel com área superior a 500 ha exige certificação SIGEF do INCRA para georreferenciamento (Lei 10.267/2001).

11. **RN-CI-011:** Múltiplos imóveis podem estar vinculados à mesma fazenda. Soma das áreas dos imóveis não pode exceder área total da fazenda em mais de 10%.

12. **RN-CI-012:** Campos obrigatórios mínimos: nome, fazenda_id, municipio, uf, area_total_ha. Demais campos podem ser preenchidos posteriormente.

## Entidades de Dados Principais

### ImovelRural
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| fazenda_id | UUID | sim | FK → Fazenda |
| nome | VARCHAR(255) | sim | Nome do imóvel (ex.: "Fazenda São João — Gleba A") |
| matricula | VARCHAR(100) | não | Número da matrícula no Cartório de Registro de Imóveis |
| cartorio_id | UUID | não | FK → Cartorio (nome e comarca do cartório) |
| nirf | VARCHAR(20) | não | Número do Imóvel na Receita Federal (ITR) |
| car_numero | VARCHAR(50) | não | Número de inscrição no CAR |
| ccir_numero | VARCHAR(50) | não | Número do CCIR (Certificado de Cadastro de Imóvel Rural) |
| area_total_ha | DECIMAL(12,4) | sim | Área total em hectares |
| area_aproveitavel_ha | DECIMAL(12,4) | não | Área aproveitável (sem APP/RL) |
| area_app_ha | DECIMAL(12,4) | não | Área de Preservação Permanente |
| area_rl_ha | DECIMAL(12,4) | não | Área de Reserva Legal |
| modulos_fiscais | DECIMAL(6,2) | não | Quantidade de módulos fiscais (Receita Federal) |
| municipio | VARCHAR(100) | sim | Município de localização |
| uf | CHAR(2) | sim | UF de localização |
| codigo_municipio_ibge | VARCHAR(10) | não | Código IBGE do município (6 dígitos) |
| latitude | DECIMAL(10,8) | não | Latitude da sede do imóvel (SIRGAS 2000) |
| longitude | DECIMAL(11,8) | não | Longitude da sede do imóvel (SIRGAS 2000) |
| tipo | ENUM (rural, particular, devoluta, posse) | sim | Tipo de imóvel conforme INCRA |
| situacao | ENUM (regular, pendente, irregular) | sim | Situação cadastral |
| observacao | TEXT | não | Observações livres |
| motivo_alteracao_area | TEXT | não | Justificativa para alteração de área |
| created_by | UUID | sim | FK → Usuário que criou |
| created_at | TIMESTAMP | sim | Data de criação |
| updated_at | TIMESTAMP | sim | Última atualização |
| deleted_at | TIMESTAMP | não | Soft delete |

### Cartorio
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| nome | VARCHAR(255) | sim | Nome do cartório |
| comarca | VARCHAR(100) | sim | Comarca do cartório |
| uf | CHAR(2) | sim | UF |
| codigo_censec | VARCHAR(20) | não | Código CENSEC do cartório |
| telefone | VARCHAR(20) | não | Telefone |
| email | VARCHAR(255) | não | E-mail |
| endereco | VARCHAR(500) | não | Endereço completo |

## Integrações Necessárias

- **Core — Fazenda:** Imóvel deve estar vinculado a uma fazenda ativa. Validação de existência no momento do cadastro.

- **Documentos Legais (essencial):** CCIR, ITR, CAR e escritura são gerenciados no submódulo de documentos. Imóvel sem documentos é marcado como "pendente".

- **Talhões/Áreas Rurais (core):** Área total do imóvel deve ser consistente com a soma dos talhões cadastrados. Alerta de divergência > 5%.

- **Arrendamentos (profissional):** Contratos de arrendamento referenciam o imóvel cadastrado. Imóvel arrendado tem restrição de edição.

- **SNCR (externo):** Validação de CCIR e módulos fiscais via API do INCRA. Integração futura.

- **Receita Federal (CAFIR):** Consulta de situação fiscal do imóvel para ITR. Validação de NIRF.

- **SIGEF (INCRA):** Certificação de georreferenciamento para imóveis > 500 ha. Importação de perímetros certificados.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Cadastro de novo imóvel
1. Usuário acessa o menu Imóveis Rurais → "Novo Imóvel".
2. Seleciona a fazenda à qual o imóvel pertence (dropdown com fazendas do tenant).
3. Preenche dados identificadores: nome, município, UF, área total.
4. Opcionalmente informa matrícula, NIRF, CCIR e CAR.
5. Sistema valida unicidade de NIRF e matrícula/cartório.
6. Se NIRF informado, valida dígito verificador (algoritmo RFB).
7. Sistema alerta se área informada diverge mais de 5% da soma dos talhões cadastrados.
8. Salva o imóvel — sistema cria vínculo com fazenda e tenant.
9. Usuário acessa o submódulo de Documentos Legais para fazer upload dos documentos vinculados.

### Fluxo 2: Vínculo de múltiplos imóveis à mesma fazenda
1. Fazenda já possui 1 imóvel cadastrado.
2. Usuário clica em "Novo Imóvel" e seleciona a mesma fazenda.
3. Sistema exibe imóveis já vinculados àquela fazenda.
4. Usuário preenche dados do novo imóvel (ex.: gleba desmembrada).
5. Sistema valida que soma das áreas dos imóveis ≤ 110% da área da fazenda.
6. Novo imóvel é salvo com vínculo à mesma fazenda.
7. Dashboard da fazenda exibe rateio de área entre imóveis.

### Fluxo 3: Regularização de imóvel pendente
1. Sistema identifica imóvel sem NIRF ou CAR (status "pendente").
2. Usuário acessa "Pendências de Regularização" no dashboard.
3. Lista de imóveis pendentes é exibida com documentos faltantes.
4. Usuário clica em "Regularizar" e é orientado sobre documentação necessária.
5. Após obter documentação, usuário atualiza cadastro com NIRF/CAR.
6. Sistema valida dados e muda status para "regular".
7. Imóvel deixa de aparecer em pendências.

### Fluxo 4: Alteração de área com justificativa
1. Usuário acessa detalhes do imóvel → "Editar".
2. Altera campo `area_total_ha`.
3. Sistema exibe campo obrigatório `motivo_alteracao_area`.
4. Usuário preenche justificativa (ex.: "Retificação de área conforme nova medição").
5. Sistema registra alteração em `HistoricoAlteracao` (quem, quando, valor anterior, valor novo, motivo).
6. Nova área é salva. Alerta de divergência com talhões é recalculado.

## Casos Extremos e Exceções

- **Imóvel sem NIRF:** Permitido para imóveis em processo de regularização. Campo opcional com alerta visual. Status "pendente" até regularização.

- **Duas matrículas para um imóvel:** Representar como dois registros separados vinculados à mesma fazenda. Exemplo: glebas com matrículas distintas.

- **Área divergente dos talhões:** Alerta informativo, não bloqueia o cadastro. Mensagem: "Área do imóvel (100 ha) diverge em 15% da soma dos talhões (115 ha). Verifique medições."

- **NIRF duplicado:** Bloqueio com mensagem clara indicando qual imóvel já usa o NIRF informado. "NIRF 123.456.789-0 já está vinculado ao imóvel 'Fazenda X'."

- **Fazenda excluída:** Imóvel órfão não deve ser exibido. Validar integridade referencial no soft delete da fazenda. Imóvel é inativado junto com a fazenda.

- **Imóvel em divisa de municípios:** Cadastrar com município principal e registrar observação. Futuro: rateio de área entre municípios para ITR.

- **Imóvel com área sobreposta a terra indígena:** Sistema detecta sobreposição via SIGEF e exibe alerta crítico. Orienta regularização junto à FUNAI.

- **Matrícula cancelada no cartório:** Usuário marca imóvel como "cancelado". Sistema preserva histórico mas bloqueia novas operações.

- **CCIR com área diferente da matrícula:** Permitido (comum em retificações). Sistema exibe ambas as áreas e alerta divergência.

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de imóveis via API com tenant isolation testado.
- [ ] Unicidade de NIRF por sistema validada no banco e na API.
- [ ] Vinculação obrigatória com fazenda ativa.
- [ ] Alerta de divergência de área (> 5%) em relação aos talhões.
- [ ] Soft delete implementado; imóvel excluído não aparece em listagens.
- [ ] Listagem com filtro por fazenda, município, UF e situação.
- [ ] Testes de isolamento multi-tenant para ImovelRural.
- [ ] Tela frontend com formulário responsivo e listagem paginada.
- [ ] Validação de dígito verificador do NIRF (algoritmo RFB).
- [ ] Histórico de alterações de área registrado com justificativa.
- [ ] Suporte a múltiplos imóveis por fazenda com validação de soma de áreas.
- [ ] Status de regularização (regular/pendente/irregular) calculado automaticamente.

## Sugestões de Melhoria Futura

- **Integração SIGEF:** Importar automaticamente dados do georreferenciamento certificado pelo INCRA. Validação de sobreposição com terras indígenas.

- **Mapa do imóvel:** Exibir polígono do imóvel no mapa baseado nos dados do CAR/SIGEF. Sobreposição com talhões operacionais.

- **Alerta de regularização:** Identificar imóveis sem NIRF ou CAR e sugerir ação de regularização. Integração com SICAR para consulta de status.

- **Histórico de transmissões:** Registrar compras, partilhas e desmembramentos ao longo do tempo. Linha do tempo de titularidade.

- **Cálculo automático de ITR:** Integrar com módulo Financeiro para cálculo e emissão de DITR baseado em área, localização e tipo de imóvel.

- **Certidão negativa de débitos:** Integração com Receita Federal para consulta de débitos de ITR do imóvel.

- **Avaliação automática de valor de mercado:** Estimativa de valor do imóvel baseada em dados de mercado (preço por hectare na região).

- **Due diligence automatizada:** Relatório completo de situação documental para aquisições e financiamentos.
