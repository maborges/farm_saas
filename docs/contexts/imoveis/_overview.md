---
modulo: Imóveis Rurais
tipo: overview
nivel: core
complexidade: M
descricao: Visão geral do módulo de Imóveis Rurais do AgroSaaS
---

# Imóveis Rurais — Visão Geral do Módulo

## Propósito

O módulo Imóveis Rurais oferece gestão documental e patrimonial de propriedades rurais, desde o cadastro básico com documentos legais obrigatórios (CCIR, CAR, ITR) até contratos de arrendamento e avaliação patrimonial. Complementa o Core ao adicionar a dimensão legal e imobiliária das fazendas, essencial para conformidade fiscal, acesso a crédito rural e gestão de parcerias agrícolas.

Este módulo foi desenhado para atender às exigências da legislação brasileira (Lei 9.393/1996 - ITR, Lei 12.651/2012 - Código Florestal, Lei 4.504/1964 - Estatuto da Terra) e normas do INCRA, Receita Federal e SICAR.

## Níveis e Submódulos

### Essencial (Core + Essencial)
| Submódulo | Complexidade | Descrição |
|-----------|-------------|-----------|
| [Cadastro de Imóvel](essencial/cadastro-imovel.md) | M | Matrícula, NIRF, área total, módulos fiscais, vínculo com fazenda |
| [Documentos Legais](essencial/documentos-legais.md) | S | Gestão de CCIR, ITR, CAR, escritura, registro, controle de vencimentos |

### Profissional
| Submódulo | Complexidade | Descrição |
|-----------|-------------|-----------|
| [Arrendamentos](profissional/arrendamentos.md) | M | Contratos de arrendamento e parceria rural, integração com financeiro |

### Enterprise
| Submódulo | Complexidade | Descrição |
|-----------|-------------|-----------|
| Avaliação Patrimonial | L | Laudo de avaliação, valor de mercado, histórico de valorização |
| Gestão Multi-Imóvel | M | Consolidação de imóveis de um grupo, indicadores patrimoniais |

## Dependências entre Submódulos

```
cadastro-imovel ──► documentos-legais
       │
       ▼
  arrendamentos ──► financeiro (lançamentos automáticos)
       │
       ▼
avaliacao-patrimonial ──► gestao-multi-imovel
```

## Dependências com Outros Módulos

- **Core — Cadastro da Propriedade:** Fazenda deve existir antes de cadastrar imóvel vinculado. Imóvel é a representação legal da fazenda operacional.

- **Core — Identidade e Acesso:** RBAC controla quem pode visualizar/editar documentos sensíveis (escritura, matrícula). Documentos legais exigem perfil admin ou owner.

- **Core — Notificações e Alertas:** Alertas de vencimento de CCIR, ITR e CAR são disparados pelo módulo de Imóveis.

- **Financeiro — Lançamentos Básicos:** Contratos de arrendamento geram lançamentos automáticos (receita de arrendamento ou despesa de arrendatário).

- **Financeiro — Ativo Imobilizado:** Imóveis rurais podem ser registrados como ativo imobilizado para depreciação e balanço.

## Integrações Externas

- **SIGEF (Sistema de Gestão Fundiária — INCRA):** Importação de perímetros e certificação de georreferenciamento. Validação de sobreposição com terras indígenas/quilombolas.

- **SNCR (Sistema Nacional de Cadastro Rural — INCRA):** Consulta e validação de CCIR e módulos fiscais. API INCRA para certificação de imóveis.

- **Receita Federal (CAFIR/ITR):** Consulta de NIRF (Número do Imóvel na Receita Federal) e situação fiscal do imóvel para ITR.

- **SICAR (Sistema Nacional de Cadastro Ambiental Rural):** Validação de código CAR e situação de regularidade ambiental.

- **Cartórios de Registro de Imóveis:** Integração futura com Central de Registro de Imóveis (CRI) para consulta de matrículas online.

- **SEI (Sistema de Escrituração Imobiliária):** Futura integração para escrituração digital de imóveis rurais.

## Princípios de Design

1. **Multi-tenancy obrigatório:** todo imóvel pertence a um `tenant_id`; isolamento via `BaseService` com filtro automático.

2. **Documentos imutáveis:** uploads de documentos legais não podem ser excluídos, apenas substituídos (versionamento). Audit trail completo de quem fez upload e quando.

3. **Alertas de vencimento:** CCIR, ITR e CAR têm datas de renovação; sistema alerta com 60, 30, 7 e 1 dias de antecedência via Notificações.

4. **Área em hectares:** valores de área sempre em hectares com 4 casas decimais para precisão legal. Conversão para alqueire apenas na exibição.

5. **Vínculo obrigatório com fazenda:** imóvel não existe sem fazenda operacional. Uma fazenda pode ter múltiplos imóveis (matrículas distintas).

6. **Conformidade legal:** campos e validações seguem normas da Receita Federal (IN RFB 1.902/2019), INCRA e MAPA.

7. **Soft delete:** imóveis nunca são excluídos fisicamente. `deleted_at` marca exclusão lógica para preservação de histórico fiscal.

## Modelo de Dados Central

```
Tenant (1) ── (N) Fazenda
Fazenda (1) ── (N) ImovelRural
ImovelRural (1) ── (N) DocumentoLegal
ImovelRural (1) ── (N) ContratoArrendamento
ImovelRural (1) ── (1) AvaliacaoPatrimonial
Tenant (1) ── (N) ContratoArrendamento
```

## Fluxo de Uso Principal

1. **Cadastro inicial:** Owner cadastra fazenda no Core → vincula imóvel rural com dados legais (NIRF, matrícula, área).

2. **Documentação:** Upload de documentos legais (CCIR, ITR, CAR, escritura) com versionamento.

3. **Monitoramento:** Sistema dispara alertas de vencimento de CCIR e ITR automaticamente.

4. **Arrendamento (opcional):** Se imóvel é arrendado, cria contrato com integração ao Financeiro.

5. **Avaliação (Enterprise):** Laudo de avaliação patrimonial para garantia de financiamento ou balanço.

## Casos de Uso Reais

- **Financiamento bancário:** Banco exige CCIR, ITR e CAR atualizados para liberar crédito rural. Sistema gera relatório de regularidade fiscal em 1 clique.

- **Due diligence de aquisição:** Comprador verifica situação documental do imóvel (matrícula, CAR, pendências fiscais) antes de fechar negócio.

- **Sucessão familiar:** Inventário de imóveis rurais para planejamento sucessório. Sistema consolida patrimônio do grupo familiar.

- **Arrendamento para terceiro:** Proprietário arrenda 200 ha para parceiro cultivar soja. Contrato gera recebimentos mensais automáticos no Financeiro.

- **Regularização ambiental:** Imóvel com CAR pendente é identificado. Sistema orienta documentação necessária para regularização no SICAR.
