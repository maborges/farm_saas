---
modulo: Rastreabilidade
submodulo: Lotes de Produção
nivel: essencial
core: false
dependencias_core:
  - fazendas
  - talhoes
  - safras
dependencias_modulos:
  - ../essencial/origem-destino.md
  - ../../agricola/safras/safras.md
complexidade: M
assinante_alvo:
  - produtor rural médio
  - cooperativas
  - agroindústrias
standalone: false
---

# Lotes de Produção

## Descrição Funcional

Submódulo responsável pela criação, identificação e gerenciamento de lotes de produção agropecuária. Cada lote representa uma unidade rastreável — um conjunto de produto que compartilha as mesmas condições de produção (mesmo talhão, mesma safra, mesmo período de colheita). O lote recebe um código único que o acompanha por toda a cadeia, permitindo identificação instantânea em qualquer ponto do processo.

O sistema gera automaticamente lotes a partir de eventos de colheita, mas também permite criação manual para situações como recebimento de terceiros, beneficiamento e fracionamento. Cada lote mantém referência ao talhão de origem, safra, cultura, variedade, data de colheita e quantidade.

## Personas — Quem usa este submódulo

- **Produtor rural:** Cria e consulta lotes para atender fiscalizações e compradores. Precisa de visão rápida de quais lotes estão abertos, fechados ou expedidos.
- **Gerente de campo:** Registra colheitas e vincula ao lote correto. Precisa de praticidade no campo, muitas vezes via celular.
- **Responsável técnico (agrônomo):** Valida informações do lote e assina digitalmente quando necessário.
- **Setor comercial:** Consulta lotes disponíveis para venda, com informações de qualidade e quantidade.

## Dores que resolve

- **Identificação manual em cadernos:** Elimina anotações em papel que se perdem, borram ou são inconsistentes.
- **Rastreabilidade reativa:** Sem lotes codificados, o produtor só consegue rastrear após o problema acontecer, e de forma imprecisa.
- **Fiscalização sem resposta:** Quando o MAPA ou vigilância sanitária solicita informações, o produtor gasta horas buscando dados em planilhas.
- **Mistura involuntária de lotes:** Sem identificação clara, lotes de qualidades diferentes acabam misturados, gerando prejuízo.
- **Falta de padronização:** Cada funcionário registra de um jeito, impossibilitando consultas e análises.

## Regras de Negócio

1. **Código único por tenant:** Todo lote recebe um código sequencial no formato `{FAZENDA}-{SAFRA}-{SEQ:5}` (ex: `FAZ01-24B-00142`). O código é imutável após criação.
2. **Vínculo obrigatório:** Todo lote deve estar vinculado a pelo menos um talhão e uma safra.
3. **Status do lote:** `aberto` → `fechado` → `expedido`. Lote aberto aceita adições de quantidade. Lote fechado é imutável em quantidade. Lote expedido já saiu da fazenda.
4. **Fracionamento:** Um lote fechado pode ser fracionado em sublotes, mantendo rastreabilidade ao lote pai.
5. **Mesclagem:** Lotes do mesmo produto/variedade/safra podem ser mesclados, gerando novo lote com referência aos lotes de origem. Requer justificativa obrigatória.
6. **Quantidade:** A quantidade do lote deve ser compatível com a soma das colheitas vinculadas, com tolerância configurável (padrão: 2%).
7. **Tenant isolation:** Lotes são isolados por `tenant_id`. Nenhuma consulta retorna lotes de outro tenant.
8. **Soft delete:** Lotes não são deletados fisicamente. Recebem flag `cancelado` com motivo obrigatório.

## Entidades de Dados Principais

- **LoteProducao:** `id`, `tenant_id`, `fazenda_id`, `safra_id`, `talhao_id`, `codigo`, `cultura_id`, `variedade`, `data_colheita`, `quantidade_kg`, `unidade`, `status` (aberto/fechado/expedido/cancelado), `lote_pai_id`, `observacoes`, `created_at`, `updated_at`
- **LoteProducaoHistorico:** `id`, `lote_id`, `evento` (criacao/adicao/fechamento/fracionamento/mesclagem/expedicao/cancelamento), `usuario_id`, `detalhes_json`, `created_at`
- **LoteColheitaVinculo:** `id`, `lote_id`, `colheita_id`, `quantidade_kg` — vincula lote a eventos de colheita

## Integrações Necessárias

- **agricola/safras:** Obter safra ativa e cultura para vincular ao lote.
- **agricola/operacoes (colheita):** Criar lote automaticamente a partir de registro de colheita.
- **core/fazendas:** Validar fazenda e talhão de origem.
- **operacional/estoque:** Movimentar estoque ao fechar ou expedir lote.
- **Origem-Destino (este módulo):** Registrar destino do lote na expedição.

## Fluxo de Uso Principal (step-by-step)

1. Gerente de campo registra colheita no módulo agrícola (talhão, quantidade, data).
2. Sistema cria automaticamente um `LoteProducao` com status `aberto`, vinculando ao registro de colheita.
3. Ao longo do dia, novas colheitas do mesmo talhão/safra podem ser adicionadas ao lote aberto.
4. Ao final do dia (ou quando desejado), o gerente fecha o lote — status muda para `fechado`, quantidade é consolidada.
5. Setor comercial consulta lotes fechados disponíveis.
6. Na venda/expedição, o lote é marcado como `expedido` com registro do comprador/destino.
7. Todo o histórico fica registrado em `LoteProducaoHistorico` para auditoria.

## Casos Extremos e Exceções

- **Colheita sem talhão definido:** Sistema deve exigir talhão; se não informado, lote fica em status `pendente_validacao` até correção.
- **Lote com quantidade zerada:** Não é permitido fechar lote com quantidade zero. Sistema bloqueia e notifica.
- **Cancelamento de lote expedido:** Requer permissão especial (`rastreabilidade:lotes:cancelar_expedido`) e gera alerta ao gestor.
- **Fracionamento com perda:** Ao fracionar, soma dos sublotes pode ser menor que o lote pai (perdas no processo). Diferença é registrada como `perda_beneficiamento`.
- **Mesclagem de lotes de safras diferentes:** Bloqueada por padrão. Configuração permite override com justificativa.
- **Importação em massa:** Produtores migrando de planilhas podem importar lotes históricos via CSV, com validação de campos obrigatórios.

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de lotes com validação de código único por tenant
- [ ] Criação automática de lote a partir de evento de colheita
- [ ] Transições de status (aberto → fechado → expedido) com validações
- [ ] Fracionamento e mesclagem com rastreabilidade ao lote pai/origem
- [ ] Histórico completo de eventos por lote (auditoria)
- [ ] Filtros por safra, talhão, cultura, status e período
- [ ] Teste de isolamento de tenant (lote de tenant A não aparece para tenant B)
- [ ] API endpoints protegidos por RBAC (`rastreabilidade:lotes:read`, `rastreabilidade:lotes:write`)
- [ ] Tela de listagem com busca por código, filtros e paginação
- [ ] Tela de detalhe do lote com timeline de eventos

## Sugestões de Melhoria Futura

- **Leitura por código de barras/QR:** Integração com leitor de código para identificação rápida no campo.
- **Lote com geolocalização:** Vincular coordenadas GPS da colheita ao lote.
- **Foto do lote:** Permitir anexar fotos (ex: carga no caminhão) para evidência visual.
- **Integração com balança:** Capturar peso automaticamente de balanças conectadas via IoT.
- **Alerta de lote aberto há muito tempo:** Notificar quando um lote permanece aberto além de X dias configuráveis.
