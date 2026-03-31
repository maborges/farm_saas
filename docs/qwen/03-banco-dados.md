# AgroSaaS - Banco de Dados

**Versão:** 1.0.0  
**Última Atualização:** 2026-03-31  
**Status:** Ativo  

---

## 📋 Índice

1. [Visão Geral](#1-visão-geral)
2. [Core Models](#2-core-models)
3. [Módulo Agrícola](#3-módulo-agrícola)
4. [Módulo Pecuária](#4-módulo-pecuária)
5. [Módulo Financeiro](#5-módulo-financeiro)
6. [Módulo Operacional](#6-módulo-operacional)
7. [Módulo RH](#7-módulo-rh)
8. [Cadastros Compartilhados](#8-cadastros-compartilhados)
9. [Migrações](#9-migrações)
10. [Padrões de Modelagem](#10-padrões-de-modelagem)

---

## 1. Visão Geral

### Tecnologia

- **PostgreSQL 16** com PostGIS (produção)
- **SQLite** com SpatiaLite fallback (desenvolvimento)
- **SQLAlchemy 2.0** ORM async
- **Alembic** para migrações

### Schema Multi-Tenancy

**Regra:** TODAS tabelas (exceto core global) possuem `tenant_id`.

```sql
-- Exemplo de estrutura padrão
CREATE TABLE safras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    -- ... outros campos
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para performance do tenant
CREATE INDEX idx_safras_tenant ON safras(tenant_id);
```

### Row Level Security (RLS)

Quando usando PostgreSQL, RLS é habilitado para defesa em profundidade:

```sql
-- Exemplo de política RLS
ALTER TABLE safras ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON safras
    USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

---

## 2. Core Models

**Path:** `services/api/core/models/`

### 2.1 Tenants e Multi-Tenancy

#### `tenants`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único do tenant |
| `nome` | VARCHAR(100) | Nome fantasia |
| `razao_social` | VARCHAR(100) | Razão social |
| `cnpj_cpf` | VARCHAR(18) | CNPJ ou CPF |
| `email` | VARCHAR(100) | Email principal |
| `telefone` | VARCHAR(20) | Telefone |
| `ativo` | BOOLEAN | Status do tenant |
| `created_at` | TIMESTAMPTZ | Data criação |

#### `tenants_usuarios`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `usuario_id` | UUID | FK → usuarios.id |
| `perfil_id` | UUID | FK → perfis_acesso.id |
| `fazenda_id` | UUID | FK → fazendas.id (opcional) |
| `ativo` | BOOLEAN | Status do vínculo |

### 2.2 Autenticação e Usuários

#### `usuarios`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `email` | VARCHAR(100) | Email (login) |
| `senha_hash` | VARCHAR(255) | Hash bcrypt |
| `nome` | VARCHAR(100) | Nome completo |
| `telefone` | VARCHAR(20) | Telefone |
| `cpf` | VARCHAR(14) | CPF |
| `ativo` | BOOLEAN | Status do usuário |
| `email_verificado` | BOOLEAN | Email verificado |
| `created_at` | TIMESTAMPTZ | Data criação |

#### `perfis_acesso`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `nome` | VARCHAR(50) | Nome do perfil |
| `descricao` | TEXT | Descrição |
| `permissoes` | JSONB | Permissões customizadas |
| `eh_sistema` | BOOLEAN | Perfil do sistema (não editável) |

#### `convites_acesso`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `email` | VARCHAR(100) | Email do convidado |
| `perfil_id` | UUID | FK → perfis_acesso.id |
| `token` | VARCHAR(255) | Token de aceite |
| `status` | VARCHAR(20) | PENDENTE, ACEITO, EXPIRADO |
| `expires_at` | TIMESTAMPTZ | Expiração do convite |

### 2.3 Fazendas e Propriedades

#### `fazendas`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `nome` | VARCHAR(100) | Nome da fazenda |
| `codigo_car` | VARCHAR(50) | CAR (Cadastro Ambiental Rural) |
| `area_total_ha` | NUMERIC(12,2) | Área total |
| `geometria` | JSONB/GEOMETRY | Polígono da fazenda |
| `endereco_completo` | TEXT | Endereço completo |

#### `grupos_fazendas`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `nome` | VARCHAR(100) | Nome do grupo |
| `descricao` | TEXT | Descrição |

#### `grupo_fazendas_rel`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `grupo_id` | UUID | FK → grupos_fazendas.id |
| `fazenda_id` | UUID | FK → fazendas.id |

### 2.4 Billing e Assinaturas

#### `planos_assinatura`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `nome` | VARCHAR(100) | Nome do plano |
| `descricao` | TEXT | Descrição |
| `preco_mensal` | NUMERIC(10,2) | Preço mensal |
| `modulos_inclusos` | JSONB | Módulos incluídos |
| `tier` | VARCHAR(20) | BASICO, PROFISSIONAL, PREMIUM |
| `ativo` | BOOLEAN | Status do plano |

#### `assinaturas_tenant`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `plano_id` | UUID | FK → planos_assinatura.id |
| `status` | VARCHAR(20) | ATIVA, CANCELADA, SUSPENSA |
| `data_inicio` | DATE | Início da vigência |
| `data_fim` | DATE | Fim da vigência |
| `stripe_customer_id` | VARCHAR(100) | ID Stripe |
| `stripe_subscription_id` | VARCHAR(100) | ID assinatura Stripe |

#### `faturas`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `assinatura_id` | UUID | FK → assinaturas_tenant.id |
| `valor` | NUMERIC(10,2) | Valor da fatura |
| `status` | VARCHAR(20) | ABERTA, PAGA, VENCIDA, CANCELADA |
| `vencimento` | DATE | Data de vencimento |
| `stripe_invoice_id` | VARCHAR(100) | ID fatura Stripe |
| `url_pdf` | VARCHAR(255) | URL do PDF |

### 2.5 Backoffice e Admin

#### `admin_users`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `email` | VARCHAR(100) | Email |
| `senha_hash` | VARCHAR(255) | Hash bcrypt |
| `nome` | VARCHAR(100) | Nome completo |
| `role` | VARCHAR(20) | super_admin, admin, suporte, financeiro, comercial |
| `ativo` | BOOLEAN | Status |

#### `admin_audit_log`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `admin_user_id` | UUID | FK → admin_users.id |
| `acao` | VARCHAR(50) | CREATE, UPDATE, DELETE, LOGIN |
| `recurso` | VARCHAR(100) | Recurso afetado |
| `recurso_id` | UUID | ID do recurso |
| `tenant_id` | UUID | FK → tenants.id (se aplicável) |
| `detalhes` | JSONB | Detalhes da ação |
| `ip_address` | VARCHAR(45) | IP do admin |
| `created_at` | TIMESTAMPTZ | Data da ação |

### 2.6 CRM e Vendas

#### `crm_leads`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `nome` | VARCHAR(100) | Nome do lead |
| `empresa` | VARCHAR(100) | Empresa/fazenda |
| `email` | VARCHAR(100) | Email |
| `telefone` | VARCHAR(20) | Telefone |
| `area_hectares` | NUMERIC(10,2) | Área em hectares |
| `fonte` | VARCHAR(50) | Fonte do lead |
| `estagio_id` | UUID | FK → crm_pipeline_estagios.id |
| `score` | INTEGER | Score do lead (0-100) |

#### `crm_ofertas`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `lead_id` | UUID | FK → crm_leads.id |
| `plano_id` | UUID | FK → planos_assinatura.id |
| `modulos_sugeridos` | JSONB | Módulos sugeridos |
| `valor_total` | NUMERIC(10,2) | Valor total |
| `desconto_pct` | NUMERIC(5,2) | Desconto percentual |
| `status` | VARCHAR(20) | RASCUNHO, ENVIADA, ACEITA, RECUSADA |
| `validade` | DATE | Validade da oferta |

### 2.7 Suporte e Knowledge Base

#### `support_chamados`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `titulo` | VARCHAR(100) | Título |
| `descricao` | TEXT | Descrição |
| `status` | VARCHAR(20) | ABERTO, EM_ANDAMENTO, AGUARDANDO_CLIENTE, FECHADO |
| `prioridade` | VARCHAR(20) | BAIXA, MEDIA, ALTA, CRITICA |
| `admin_responsavel_id` | UUID | FK → admin_users.id |
| `created_at` | TIMESTAMPTZ | Data criação |

#### `knowledge_base`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `titulo` | VARCHAR(200) | Título do artigo |
| `conteudo` | TEXT | Conteúdo em Markdown |
| `categoria` | VARCHAR(50) | Categoria |
| `tags` | JSONB | Tags |
| `visivel_tenant` | BOOLEAN | Visível para tenants |
| `ordem` | INTEGER | Ordem de exibição |

---

## 3. Módulo Agrícola

**Path:** `services/api/agricola/*/models.py`

### 3.1 Safras e Planejamento

#### `safras`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `nome` | VARCHAR(100) | Nome (ex: "Soja 2025/26") |
| `cultura` | VARCHAR(50) | Cultura (ex: "Soja", "Milho") |
| `variedade` | VARCHAR(100) | Variedade |
| `ciclo` | VARCHAR(30) | PRINCIPAL, SAFRINHA, PERENE |
| `fase_atual` | VARCHAR(30) | PLANEJADA, PREPARO_SOLO, PLANTIO, DESENVOLVIMENTO, COLHEITA, POS_COLHEITA, ENCERRADA |
| `data_inicio` | DATE | Data de início |
| `data_fim_prevista` | DATE | Data prevista de fim |
| `data_plantio_real` | DATE | Data real de plantio |
| `data_colheita_real` | DATE | Data real de colheita |
| `hectares_planejados` | NUMERIC(10,2) | Hectares planejados |
| `hectares_plantados` | NUMERIC(10,2) | Hectares plantados |
| `produtividade_meta_sc_ha` | NUMERIC(10,2) | Meta de produtividade (sc/ha) |
| `custo_previsto_ha` | NUMERIC(10,2) | Custo previsto por ha |
| `custo_realizado_ha` | NUMERIC(10,2) | Custo realizado por ha |
| `ativo` | BOOLEAN | Safra ativa |

#### `safras_talhoes`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `safra_id` | UUID | FK → safras.id |
| `talhao_id` | UUID | FK → talhoes.id |
| `area_ha` | NUMERIC(10,2) | Área do talhão na safra |
| `data_plantio` | DATE | Data de plantio no talhão |

#### `safras_fases_historico`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `safra_id` | UUID | FK → safras.id |
| `fase_anterior` | VARCHAR(30) | Fase anterior |
| `fase_nova` | VARCHAR(30) | Nova fase |
| `data_transicao` | TIMESTAMPTZ | Data da transição |
| `usuario_id` | UUID | FK → usuarios.id |
| `observacoes` | TEXT | Observações |

### 3.2 Talhões e Áreas

#### `talhoes`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `fazenda_id` | UUID | FK → fazendas.id |
| `nome` | VARCHAR(100) | Nome do talhão |
| `geometria` | JSONB/GEOMETRY | Polígono do talhão |
| `centroide` | JSONB/GEOMETRY | Centroide do polígono |
| `area_ha` | NUMERIC(10,2) | Área em hectares (PostGIS) |
| `area_ha_manual` | NUMERIC(10,2) | Área manual (fallback SQLite) |
| `tipo_solo` | VARCHAR(50) | Tipo de solo |
| `classe_solo` | VARCHAR(50) | Classe de solo |
| `textura_solo` | VARCHAR(30) | Textura (argilosa, arenosa, etc.) |
| `relevo` | VARCHAR(30) | Relevo (plano, ondulado, etc.) |
| `irrigado` | BOOLEAN | É irrigado |
| `sistema_irrigacao` | VARCHAR(50) | Sistema de irrigação |

### 3.3 Operações de Campo

#### `operacoes_agricolas`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `safra_id` | UUID | FK → safras.id |
| `talhao_id` | UUID | FK → talhoes.id |
| `tipo_operacao` | VARCHAR(50) | PLANTIO, PULVERIZACAO, ADUBACAO, COLHEITA, etc. |
| `data_operacao` | DATE | Data da operação |
| `hora_inicio` | TIME | Hora de início |
| `hora_fim` | TIME | Hora de fim |
| `maquinario_id` | UUID | FK → equipamentos.id |
| `operador_id` | UUID | FK → pessoas.id |
| `area_aplicada_ha` | NUMERIC(10,2) | Área aplicada |
| `custo_total` | NUMERIC(10,2) | Custo total |
| `custo_por_ha` | NUMERIC(10,2) | Custo por hectare |
| `condicoes_clima` | JSONB | Condições climáticas no momento |
| `observacoes` | TEXT | Observações |

#### `insumos_operacao`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `operacao_id` | UUID | FK → operacoes_agricolas.id |
| `produto_id` | UUID | FK → produtos.id |
| `lote_estoque_id` | UUID | FK → estoque_lotes.id |
| `dose_aplicada` | NUMERIC(10,3) | Dose aplicada |
| `unidade_dose` | VARCHAR(20) | Unidade da dose (L, kg, g) |
| `carencia_dias` | INTEGER | Período de carência (dias) |
| `receituario_agronomico_id` | UUID | FK → prescricoes.id |

### 3.4 Romaneios de Colheita

#### `romaneios_colheita`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `safra_id` | UUID | FK → safras.id |
| `talhao_id` | UUID | FK → talhoes.id |
| `data_colheita` | DATE | Data da colheita |
| `maquinario_id` | UUID | FK → equipamentos.id |
| `operador_id` | UUID | FK → pessoas.id |
| `peso_bruto_kg` | NUMERIC(12,2) | Peso bruto |
| `tara_kg` | NUMERIC(12,2) | Tara (peso do caminhão) |
| `peso_liquido_kg` | NUMERIC(12,2) | Peso líquido |
| `umidade_pct` | NUMERIC(5,2) | Umidade (%) |
| `impureza_pct` | NUMERIC(5,2) | Impureza (%) |
| `avariados_pct` | NUMERIC(5,2) | Avariados (%) |
| `peso_liquido_padrao_kg` | NUMERIC(12,2) | Peso líquido padronizado |
| `sacas_60kg` | NUMERIC(10,2) | Número de sacas de 60kg |
| `produtividade_sc_ha` | NUMERIC(10,2) | Produtividade (sc/ha) |
| `preco_saca` | NUMERIC(10,2) | Preço por saca |
| `receita_total` | NUMERIC(12,2) | Receita total |
| `destino` | VARCHAR(50) | ARMAZEM, BENEFICIAMENTO, VENDA_DIRETA |
| `origem_id` | UUID | FK para origem (rateio) |
| `origem_tipo` | VARCHAR(50) | Tipo da origem |

### 3.5 Monitoramento de Pragas e Doenças

#### `monitoramentos_pragas`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `safra_id` | UUID | FK → safras.id |
| `talhao_id` | UUID | FK → talhoes.id |
| `data_monitoramento` | DATE | Data do monitoramento |
| `tipo` | VARCHAR(30) | PRAGA, DOENCA, PLANTA_DANINHA |
| `catalogo_id` | UUID | FK → monitoramento_catalogo.id |
| `nivel_infestacao` | VARCHAR(20) | BAIXO, MEDIO, ALTO, CRITICO |
| `nde_ultrapassado` | BOOLEAN | NDE (Nível de Dano Econômico) ultrapassado |
| `acao_tomada` | VARCHAR(30) | CONTROLE, MONITORAR, NENHUMA |
| `pontos_amostragem` | INTEGER | Número de pontos de amostragem |
| `geolocalizacao` | JSONB/GEOMETRY | Localização do foco |
| `diagnostico_ia` | JSONB | Resultado do diagnóstico por IA |
| `observacoes` | TEXT | Observações |

#### `monitoramento_catalogo`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id (NULL para catálogo global) |
| `nome_cientifico` | VARCHAR(100) | Nome científico |
| `nome_comum` | VARCHAR(100) | Nome comum |
| `tipo` | VARCHAR(30) | PRAGA, DOENCA, PLANTA_DANINHA |
| `culturas_afetadas` | JSONB | Culturas afetadas |
| `sintomas` | TEXT | Descrição dos sintomas |
| `controle_recomendado` | TEXT | Controle recomendado |
| `imagem_url` | VARCHAR(255) | URL da imagem |
| `eh_sistema` | BOOLEAN | Item do sistema (não editável) |

### 3.6 Análises de Solo

#### `analises_solo`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `talhao_id` | UUID | FK → talhoes.id |
| `data_coleta` | DATE | Data da coleta |
| `data_resultado` | DATE | Data do resultado |
| `laboratorio` | VARCHAR(100) | Laboratório |
| `ph` | NUMERIC(4,2) | pH |
| `materia_organica_pct` | NUMERIC(5,2) | Matéria orgânica (%) |
| `fosforo_mg_dm3` | NUMERIC(8,2) | Fósforo (mg/dm³) |
| `potassio_mg_dm3` | NUMERIC(8,2) | Potássio (mg/dm³) |
| `calcio_cmolc_dm3` | NUMERIC(8,2) | Cálcio (cmolc/dm³) |
| `magnesio_cmolc_dm3` | NUMERIC(8,2) | Magnésio (cmolc/dm³) |
| `aluminio_cmolc_dm3` | NUMERIC(8,2) | Alumínio (cmolc/dm³) |
| `capacidade_troca_catica` | NUMERIC(8,2) | CTC |
| `saturacao_base_pct` | NUMERIC(5,2) | Saturação por bases (%) |
| `recomendacoes` | TEXT | Recomendações do laudo |
| `laudo_pdf_url` | VARCHAR(255) | URL do PDF do laudo |

---

## 4. Módulo Pecuária

**Path:** `services/api/pecuaria/*/models.py`

### 4.1 Animais e Lotes

#### `lotes_animais`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `nome` | VARCHAR(50) | Nome/identificação do lote |
| `especie` | VARCHAR(50) | Espécie (BOVINO, OVINO, etc.) |
| `categoria` | VARCHAR(50) | Categoria (BEEF, LEITE, MISTO) |
| `quantidade_cabecas` | INTEGER | Número de cabeças |
| `peso_medio_kg` | NUMERIC(8,2) | Peso médio do lote |
| `data_entrada` | DATE | Data de entrada |
| `piquete_id` | UUID | FK → piquetes.id |
| `status` | VARCHAR(20) | ATIVO, TERMINADO, VENDIDO |

#### `animais`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `numero_brinco` | VARCHAR(50) | Número do brinco |
| `numero_sisbov` | VARCHAR(50) | Número SISBOV |
| `microchip` | VARCHAR(50) | Microchip ID |
| `especie` | VARCHAR(50) | Espécie |
| `raca` | VARCHAR(50) | Raça |
| `sexo` | VARCHAR(10) | MACHO, FEMEA |
| `categoria` | VARCHAR(50) | Categoria |
| `data_nascimento` | DATE | Data de nascimento |
| `pai_id` | UUID | FK → animais.id |
| `mae_id` | UUID | FK → animais.id |
| `peso_atual_kg` | NUMERIC(8,2) | Peso atual |
| `data_ultima_pesagem` | DATE | Data da última pesagem |
| `status` | VARCHAR(20) | ATIVO, VENDIDO, MORTO, ABATIDO |
| `valor_aquisicao` | NUMERIC(10,2) | Valor de aquisição |
| `valor_atual` | NUMERIC(10,2) | Valor atual (IAS 41) |

#### `eventos_animais`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `animal_id` | UUID | FK → animais.id (NULL para eventos de lote) |
| `lote_id` | UUID | FK → lotes_animais.id |
| `tipo_evento` | VARCHAR(30) | NASCIMENTO, COMPRA, PESAGEM, DESMAME, COBERTURA, INSEMINACAO, PARTO, VACINACAO, MEDICACAO, VENDA, ABATE, MORTE |
| `data_evento` | DATE | Data do evento |
| `valor_numerico` | NUMERIC(12,2) | Valor numérico (peso, preço, etc.) |
| `dados_extras` | JSONB | Dados extras do evento |
| `produto_id` | UUID | FK → produtos.id (para medicamentos, vacinas) |
| `pessoa_id` | UUID | FK → pessoas.id (veterinário, técnico) |
| `observacoes` | TEXT | Observações |

### 4.2 Piquetes e Pastagens

#### `piquetes`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `fazenda_id` | UUID | FK → fazendas.id |
| `nome` | VARCHAR(100) | Nome do piquete |
| `area_ha` | NUMERIC(10,2) | Área em hectares |
| `geometria` | JSONB/GEOMETRY | Polígono do piquete |
| `tipo_pastagem` | VARCHAR(50) | Tipo de pastagem |
| `lotação_maxima` | INTEGER | Lotação máxima (cabeças) |
| `status` | VARCHAR(20) | ATIVO, EM_DESCANSO, EM_REFORMA |

### 4.3 Produção Leiteira

#### `producao_leite`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `animal_id` | UUID | FK → animais.id (NULL para produção de lote) |
| `lote_id` | UUID | FK → lotes_animais.id |
| `data_ordenha` | DATE | Data da ordenha |
| `turno` | VARCHAR(10) | MANHA, TARDE, NOITE, TOTAL |
| `volume_litros` | NUMERIC(8,2) | Volume em litros |
| `gordura_pct` | NUMERIC(5,2) | Teor de gordura (%) |
| `proteina_pct` | NUMERIC(5,2) | Teor de proteína (%) |
| `lactose_pct` | NUMERIC(5,2) | Teor de lactose (%) |
| `ccs` | INTEGER | Contagem de Células Somáticas |
| `cbt` | INTEGER | Contagem Bacteriana Total |
| `destino` | VARCHAR(30) | LATICINIO, QUEIJARIA, CONSUMO_PROPRIO, DESCARTE |
| `preco_litro` | NUMERIC(8,2) | Preço por litro |
| `valor_total` | NUMERIC(10,2) | Valor total |

---

## 5. Módulo Financeiro

**Path:** `services/api/financeiro/models.py`

### 5.1 Receitas e Despesas

#### `fin_receitas`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `pessoa_id` | UUID | FK → pessoas.id (cliente) |
| `cliente` | VARCHAR(100) | Nome do cliente (se não cadastrado) |
| `descricao` | TEXT | Descrição |
| `valor` | NUMERIC(12,2) | Valor total |
| `data_vencimento` | DATE | Data de vencimento |
| `data_pagamento` | DATE | Data de pagamento |
| `status` | VARCHAR(20) | A_RECEBER, RECEBIDO, RECEBIDO_PARCIAL, CANCELADO |
| `grupo_parcela_id` | UUID | ID do grupo de parcelas |
| `numero_parcela` | INTEGER | Número da parcela |
| `total_parcelas` | INTEGER | Total de parcelas |
| `plano_conta_id` | UUID | FK → fin_planos_conta.id |
| `numero_nf` | VARCHAR(50) | Número da nota fiscal |
| `chave_nfe` | VARCHAR(44) | Chave da NFe |
| `competencia` | DATE | Competência |
| `origem_id` | UUID | FK para origem (romaneio, venda animal) |
| `origem_tipo` | VARCHAR(50) | Tipo da origem |
| `observacoes` | TEXT | Observações |

#### `fin_despesas`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `pessoa_id` | UUID | FK → pessoas.id (fornecedor) |
| `fornecedor` | VARCHAR(100) | Nome do fornecedor (se não cadastrado) |
| `descricao` | TEXT | Descrição |
| `valor` | NUMERIC(12,2) | Valor total |
| `data_vencimento` | DATE | Data de vencimento |
| `data_pagamento` | DATE | Data de pagamento |
| `status` | VARCHAR(20) | A_PAGAR, PAGO, PAGO_PARCIAL, ATRASADO, CANCELADO |
| `grupo_parcela_id` | UUID | ID do grupo de parcelas |
| `numero_parcela` | INTEGER | Número da parcela |
| `total_parcelas` | INTEGER | Total de parcelas |
| `plano_conta_id` | UUID | FK → fin_planos_conta.id |
| `numero_nf` | VARCHAR(50) | Número da nota fiscal |
| `competencia` | DATE | Competência |
| `origem_id` | UUID | FK para origem (operacao, os, compra) |
| `origem_tipo` | VARCHAR(50) | Tipo da origem |
| `observacoes` | TEXT | Observações |

### 5.2 Plano de Contas

#### `fin_planos_conta`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `parent_id` | UUID | FK → fin_planos_conta.id (hierarquia) |
| `nome` | VARCHAR(100) | Nome da conta |
| `codigo` | VARCHAR(20) | Código da conta |
| `natureza` | VARCHAR(20) | SINTETICA (grupo), ANALITICA (lançamentos) |
| `tipo` | VARCHAR(20) | RECEITA, DESPESA |
| `categoria_rfb` | VARCHAR(50) | Categoria RFB (Livro Caixa) |
| `is_sistema` | BOOLEAN | Conta do sistema (não editável) |

### 5.3 Rateio de Custos

#### `fin_rateios`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `despesa_id` | UUID | FK → fin_despesas.id |
| `safra_id` | UUID | FK → safras.id |
| `talhao_id` | UUID | FK → talhoes.id |
| `lote_animal_id` | UUID | FK → lotes_animais.id |
| `valor_rateado` | NUMERIC(12,2) | Valor rateado |
| `percentual` | NUMERIC(5,2) | Percentual do rateio |
| `tipo_centro_custo` | VARCHAR(30) | SAFRA, TALHAO, LOTE |

### 5.4 Contas Bancárias e Conciliação

#### `fin_contas_bancarias`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `nome` | VARCHAR(100) | Nome da conta |
| `banco` | VARCHAR(50) | Banco |
| `agencia` | VARCHAR(20) | Agência |
| `conta` | VARCHAR(20) | Conta |
| `tipo` | VARCHAR(20) | CORRENTE, POUPANCA, INVESTIMENTO |
| `saldo_inicial` | NUMERIC(12,2) | Saldo inicial |
| `ativo` | BOOLEAN | Conta ativa |

#### `fin_lancamentos_bancarios`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `conta_bancaria_id` | UUID | FK → fin_contas_bancarias.id |
| `data_lancamento` | DATE | Data do lançamento |
| `descricao` | TEXT | Descrição |
| `valor` | NUMERIC(12,2) | Valor (positivo = crédito, negativo = débito) |
| `tipo` | VARCHAR(20) | CREDITO, DEBITO |
| `categoria` | VARCHAR(50) | Categoria |
| `receita_id` | UUID | FK → fin_receitas.id |
| `despesa_id` | UUID | FK → fin_despesas.id |
| `conciliado` | BOOLEAN | Lançamento conciliado |
| `dados_ofx` | JSONB | Dados originais do OFX |

---

## 6. Módulo Operacional

**Path:** `services/api/operacional/models.py`

### 6.1 Frota e Manutenções

#### `frota_equipamentos`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `nome` | VARCHAR(100) | Nome do equipamento |
| `tipo` | VARCHAR(50) | TRATOR, COLHEITADEIRA, PULVERIZADOR, CAMINHAO, etc. |
| `marca_id` | UUID | FK → marcas.id |
| `modelo_id` | UUID | FK → modelos.id |
| `ano_fabricacao` | INTEGER | Ano de fabricação |
| `numero_serie` | VARCHAR(50) | Número de série |
| `placa` | VARCHAR(20) | Placa (se veículo) |
| `horimetro_atual` | NUMERIC(10,2) | Horímetro atual (horas) |
| `odometro_atual` | NUMERIC(10,2) | Odômetro atual (km) |
| `status` | VARCHAR(20) | ATIVO, MANUTENCAO, BAIXADO |

#### `frota_planos_manutencao`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `equipamento_id` | UUID | FK → frota_equipamentos.id |
| `nome` | VARCHAR(100) | Nome do plano |
| `tipo` | VARCHAR(30) | PREVENTIVA, CORRETIVA, PREDICTIVA |
| `frequencia_horas` | INTEGER | Frequência em horas |
| `frequencia_km` | INTEGER | Frequência em km |
| `descricao_servico` | TEXT | Descrição do serviço |

#### `frota_ordens_servico`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `equipamento_id` | UUID | FK → frota_equipamentos.id |
| `plano_manutencao_id` | UUID | FK → frota_planos_manutencao.id |
| `tipo` | VARCHAR(30) | PREVENTIVA, CORRETIVA, REVISAO |
| `status` | VARCHAR(20) | ABERTA, EM_EXECUCAO, CONCLUIDA, CANCELADA |
| `descricao_problema` | TEXT | Descrição do problema |
| `descricao_servico` | TEXT | Descrição do serviço realizado |
| `horimetro_km` | NUMERIC(10,2) | Horímetro/km no momento |
| `data_abertura` | DATE | Data de abertura |
| `data_conclusao` | DATE | Data de conclusão |
| `custo_total_pecas` | NUMERIC(10,2) | Custo total de peças |
| `custo_mao_obra` | NUMERIC(10,2) | Custo de mão de obra |

#### `frota_itens_ordem_servico`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `ordem_servico_id` | UUID | FK → frota_ordens_servico.id |
| `produto_id` | UUID | FK → produtos.id |
| `lote_estoque_id` | UUID | FK → estoque_lotes.id |
| `quantidade` | NUMERIC(10,3) | Quantidade |
| `custo_unitario` | NUMERIC(10,2) | Custo unitário |
| `custo_total` | NUMERIC(10,2) | Custo total |

### 6.2 Estoque

#### `estoque_depositos`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `nome` | VARCHAR(100) | Nome do depósito |
| `tipo` | VARCHAR(30) | GERAL, COMBUSTIVEL, DEFENSIVOS, PECAS |
| `endereco` | TEXT | Endereço completo |
| `responsavel_id` | UUID | FK → pessoas.id |
| `ativo` | BOOLEAN | Depósito ativo |

#### `estoque_lotes`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `produto_id` | UUID | FK → produtos.id |
| `deposito_id` | UUID | FK → estoque_depositos.id |
| `codigo_lote` | VARCHAR(50) | Código do lote |
| `data_fabricacao` | DATE | Data de fabricação |
| `data_validade` | DATE | Data de validade |
| `quantidade_inicial` | NUMERIC(10,3) | Quantidade inicial |
| `quantidade_atual` | NUMERIC(10,3) | Quantidade atual |
| `unidade` | VARCHAR(20) | Unidade (L, kg, un) |
| `status` | VARCHAR(20) | ATIVO, VENCIDO, ESGOTADO, BLOQUEADO |
| `custo_unitario` | NUMERIC(10,2) | Custo unitário |

#### `estoque_saldos`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `produto_id` | UUID | FK → produtos.id |
| `deposito_id` | UUID | FK → estoque_depositos.id |
| `quantidade_total` | NUMERIC(10,3) | Quantidade total |
| `quantidade_reservada` | NUMERIC(10,3) | Quantidade reservada |
| `quantidade_disponivel` | NUMERIC(10,3) | Quantidade disponível |
| `unidade` | VARCHAR(20) | Unidade |

#### `estoque_movimentacoes`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `produto_id` | UUID | FK → produtos.id |
| `lote_id` | UUID | FK → estoque_lotes.id |
| `deposito_origem_id` | UUID | FK → estoque_depositos.id |
| `deposito_destino_id` | UUID | FK → estoque_depositos.id |
| `tipo` | VARCHAR(20) | ENTRADA, SAIDA, TRANSFERENCIA, AJUSTE |
| `quantidade` | NUMERIC(10,3) | Quantidade |
| `data_movimentacao` | DATE | Data da movimentação |
| `origem_id` | UUID | FK para origem (operacao, os, etc.) |
| `origem_tipo` | VARCHAR(50) | Tipo da origem |
| `responsavel_id` | UUID | FK → pessoas.id |
| `observacoes` | TEXT | Observações |

#### `estoque_requisicoes`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `solicitante_id` | UUID | FK → pessoas.id |
| `deposito_id` | UUID | FK → estoque_depositos.id |
| `status` | VARCHAR(20) | PENDENTE, APROVADA, SEPARANDO, ENTREGUE, RECUSADA |
| `data_solicitacao` | DATE | Data da solicitação |
| `data_aprovacao` | DATE | Data da aprovação |
| `data_entrega` | DATE | Data da entrega |
| `observacoes` | TEXT | Observações |

#### `estoque_reservas`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `produto_id` | UUID | FK → produtos.id |
| `deposito_id` | UUID | FK → estoque_depositos.id |
| `quantidade` | NUMERIC(10,3) | Quantidade reservada |
| `referencia_id` | UUID | FK para referência (OS, pedido) |
| `referencia_tipo` | VARCHAR(50) | ORDEM_SERVICO, PEDIDO_COMPRA, SAFRA |
| `data_reserva` | DATE | Data da reserva |
| `data_validade` | DATE | Validade da reserva |
| `status` | VARCHAR(20) | ATIVA, CANCELADA, CONSUMIDA |

---

## 7. Módulo RH

**Path:** `services/api/rh/models.py`

### 7.1 Colaboradores e Remuneração

#### `rh_colaboradores`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `pessoa_id` | UUID | FK → pessoas.id |
| `departamento_id` | UUID | FK → rh_departamentos.id |
| `cargo` | VARCHAR(50) | Cargo |
| `data_admissao` | DATE | Data de admissão |
| `data_demissao` | DATE | Data de demissão |
| `salario_base` | NUMERIC(10,2) | Salário base |
| `tipo_contrato` | VARCHAR(30) | TEMPORARIO, FIXO, SAFRISTA |
| `ativo` | BOOLEAN | Colaborador ativo |

#### `rh_lancamento_diarias`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `colaborador_id` | UUID | FK → rh_colaboradores.id |
| `data` | DATE | Data da diária |
| `valor_diaria` | NUMERIC(10,2) | Valor da diária |
| `quantidade` | INTEGER | Quantidade de diárias |
| `motivo` | TEXT | Motivo |
| `observacoes` | TEXT | Observações |

#### `rh_empreitadas`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `colaborador_id` | UUID | FK → rh_colaboradores.id |
| `descricao` | TEXT | Descrição da empreitada |
| `valor_total` | NUMERIC(10,2) | Valor total |
| `data_inicio` | DATE | Data de início |
| `data_fim` | DATE | Data de fim |
| `status` | VARCHAR(20) | EM_ANDAMENTO, CONCLUIDA, CANCELADA |

---

## 8. Cadastros Compartilhados

**Path:** `services/api/core/cadastros/`

### 8.1 Pessoas e Parceiros

#### `pessoas`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `nome` | VARCHAR(100) | Nome completo/razão social |
| `nome_fantasia` | VARCHAR(100) | Nome fantasia |
| `tipo` | VARCHAR(20) | PESSOA_FISICA, PESSOA_JURIDICA |
| `cpf_cnpj` | VARCHAR(18) | CPF ou CNPJ |
| `rg_ie` | VARCHAR(20) | RG ou Inscrição Estadual |
| `data_nascimento` | DATE | Data de nascimento/fundação |
| `email` | VARCHAR(100) | Email principal |
| `telefone` | VARCHAR(20) | Telefone principal |
| `categoria` | VARCHAR(30) | CLIENTE, FORNECEDOR, PARCEIRO, COLABORADOR |
| `ativo` | BOOLEAN | Pessoa ativa |

#### `pessoas_contatos`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `pessoa_id` | UUID | FK → pessoas.id |
| `nome` | VARCHAR(100) | Nome do contato |
| `cargo` | VARCHAR(50) | Cargo |
| `email` | VARCHAR(100) | Email |
| `telefone` | VARCHAR(20) | Telefone |
| `principal` | BOOLEAN | Contato principal |

#### `pessoas_enderecos`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `pessoa_id` | UUID | FK → pessoas.id |
| `tipo` | VARCHAR(20) | RESIDENCIAL, COMERCIAL, COBRANCA, ENTREGA |
| `logradouro` | VARCHAR(100) | Logradouro |
| `numero` | VARCHAR(20) | Número |
| `complemento` | VARCHAR(50) | Complemento |
| `bairro` | VARCHAR(50) | Bairro |
| `cidade` | VARCHAR(100) | Cidade |
| `estado` | VARCHAR(2) | UF |
| `cep` | VARCHAR(10) | CEP |
| `principal` | BOOLEAN | Endereço principal |

### 8.2 Produtos e Catálogo

#### `produtos`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `nome` | VARCHAR(100) | Nome do produto |
| `descricao` | TEXT | Descrição |
| `categoria_id` | UUID | FK → produtos_categorias.id |
| `tipo` | VARCHAR(30) | INSUMO_AGRICOLA, SEMENTE, DEFENSIVO, FERTILIZANTE, COMBUSTIVEL, PECA_MAQUINARIO, MATERIAL_GERAL, RACAO_ANIMAL, MEDICAMENTO_ANIMAL, SERVICO, OUTROS |
| `unidade` | VARCHAR(20) | Unidade (L, kg, un, sc) |
| `custo_medio` | NUMERIC(10,2) | Custo médio |
| `preco_venda` | NUMERIC(10,2) | Preço de venda |
| `estoque_minimo` | NUMERIC(10,3) | Estoque mínimo |
| `ativo` | BOOLEAN | Produto ativo |

#### `produtos_categorias`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `nome` | VARCHAR(100) | Nome da categoria |
| `parent_id` | UUID | FK → produtos_categorias.id |

### 8.3 Equipamentos

#### `equipamentos`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `tenant_id` | UUID | FK → tenants.id |
| `nome` | VARCHAR(100) | Nome |
| `tipo` | VARCHAR(50) | Tipo |
| `marca_id` | UUID | FK → marcas.id |
| `modelo_id` | UUID | FK → modelos.id |

### 8.4 Tabelas Auxiliares

#### `marcas`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `nome` | VARCHAR(100) | Nome da marca |
| `ativo` | BOOLEAN | Marca ativa |

#### `modelos`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `marca_id` | UUID | FK → marcas.id |
| `nome` | VARCHAR(100) | Nome do modelo |
| `ativo` | BOOLEAN | Modelo ativo |

#### `culturas`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `nome` | VARCHAR(100) | Nome da cultura |
| `nome_cientifico` | VARCHAR(100) | Nome científico |
| `ciclo_medio_dias` | INTEGER | Ciclo médio (dias) |
| `ativo` | BOOLEAN | Cultura ativa |

#### `commodities`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | ID único |
| `nome` | VARCHAR(100) | Nome da commodity |
| `unidade_padrao` | VARCHAR(20) | Unidade padrão (sc, kg, L) |
| `ativo` | BOOLEAN | Commodity ativa |

---

## 9. Migrações

**Path:** `services/api/migrations/versions/`

### 9.1 Estrutura de Migrações

Cada migration file segue o padrão:
```
{timestamp}_{description}.py
```

Exemplo: `2026_03_15_123456_add_tenant_modules.py`

### 9.2 Migrações Principais

| Migration | Descrição |
|-----------|-----------|
| `001_initial_core.py` | Criação das tabelas core (tenants, usuarios, auth) |
| `002_fazendas_grupos.py` | Fazendas e grupos de fazendas |
| `003_billing.py` | Planos, assinaturas, faturas |
| `004_agricola_safras.py` | Módulo agrícola - safras |
| `005_agricola_talhoes.py` | Módulo agrícola - talhões |
| `006_agricola_operacoes.py` | Módulo agrícola - operações |
| `007_agricola_romaneios.py` | Módulo agrícola - romaneios |
| `008_pecuaria_animais.py` | Módulo pecuária - animais e lotes |
| `009_financeiro.py` | Módulo financeiro - receitas, despesas, plano contas |
| `010_operacional_frota.py` | Módulo operacional - frota |
| `011_operacional_estoque.py` | Módulo operacional - estoque |
| `012_rh_colaboradores.py` | Módulo RH |
| `013_cadastros_pessoas.py` | Cadastros - pessoas |
| `014_cadastros_produtos.py` | Cadastros - produtos |
| `015_multi_sub_rbac.py` | RBAC multi-assinatura |
| `016_crm.py` | CRM e ofertas |
| `017_support.py` | Suporte e knowledge base |

### 9.3 Comandos Alembic

```bash
# Criar nova migration
alembic revision --autogenerate -m "description"

# Aplicar migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1

# Ver status das migrations
alembic current

# Histórico de migrations
alembic history
```

---

## 10. Padrões de Modelagem

### 10.1 Convenções de Nomenclatura

- **Tabelas:** snake_case plural (ex: `safras`, `operacoes_agricolas`)
- **Colunas:** snake_case (ex: `data_nascimento`, `peso_liquido_kg`)
- **IDs:** `id` (primary), `{tabela}_id` (foreign keys)
- **Timestamps:** `created_at`, `updated_at`

### 10.2 Multi-Tenancy

**Regra obrigatória:** Todas tabelas de domínio devem ter `tenant_id`.

```python
# Padrão em todos models
class Safra(Base):
    __tablename__ = "safras"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    # ...
```

### 10.3 Soft Delete

Alguns models usam soft delete via campo `ativo`:

```python
ativo: Mapped[bool] = mapped_column(default=True)

# Query sempre filtrar por ativo=True
stmt = select(Model).where(Model.ativo == True)
```

### 10.4 Foreign Keys com Cascade

```python
# onDelete=CASCADE para dados do tenant
tenant_id: Mapped[uuid.UUID] = mapped_column(
    ForeignKey("tenants.id", ondelete="CASCADE")
)

# onDelete=SET NULL para relacionamentos opcionais
pai_id: Mapped[uuid.UUID | None] = mapped_column(
    ForeignKey("animais.id", ondelete="SET NULL")
)
```

### 10.5 JSONB para Dados Flexíveis

```python
# Dados extras, configurações, condições
dados_extras: Mapped[dict] = mapped_column(JSONB, default=dict)
condicoes_clima: Mapped[dict] = mapped_column(JSONB)
permissoes: Mapped[dict] = mapped_column(JSONB)
```

### 10.6 Índices de Performance

```python
# Índices compostos para queries frequentes
__table_args__ = (
    Index('idx_safras_tenant_ativo', 'tenant_id', 'ativo'),
    Index('idx_operacoes_safra_data', 'safra_id', 'data_operacao'),
)
```

---

## Referências Cruzadas

| Documento | Descrição |
|-----------|-----------|
| `docs/qwen/01-arquitetura.md` | Arquitetura geral |
| `docs/qwen/02-modulos.md` | Detalhamento de módulos |
| `docs/qwen/05-api.md` | API reference |

---

## Changelog

| Data | Versão | Descrição |
|------|--------|-----------|
| 2026-03-31 | 1.0.0 | Documentação inicial completa |
