---
modulo: Rastreabilidade
submodulo: Histórico de Aplicações
nivel: essencial
core: false
dependencias_core:
  - fazendas
  - talhoes
dependencias_modulos:
  - ../essencial/lotes-producao.md
  - ../../agricola/operacoes/aplicacoes.md
  - ../../operacional/estoque/insumos.md
complexidade: M
assinante_alvo:
  - produtor rural
  - agrônomo responsável técnico
  - cooperativas
standalone: false
---

# Histórico de Aplicações

## Descrição Funcional

Submódulo que registra e vincula ao lote de produção todo o histórico de defensivos agrícolas, fertilizantes e demais insumos aplicados no talhão durante o ciclo da cultura. Consolida informações do módulo agrícola (operações de aplicação) e as apresenta de forma rastreável por lote, permitindo comprovar conformidade com períodos de carência, dosagens permitidas e regulamentações do MAPA.

O histórico de aplicações é a peça central da rastreabilidade de insumos — responde à pergunta "o que foi aplicado neste lote, quando, quanto e por quem?".

## Personas — Quem usa este submódulo

- **Agrônomo / Responsável Técnico (RT):** Prescreve aplicações, valida períodos de carência e assina receituário. Precisa de visão consolidada por lote para emitir laudos.
- **Gerente de campo / operador:** Registra a execução da aplicação no campo (produto, dose, data, equipamento).
- **Produtor rural:** Consulta para responder a fiscalizações e exigências de compradores.
- **Auditor de certificação:** Verifica conformidade com normas (ex: número de aplicações permitidas, carência respeitada).

## Dores que resolve

- **Caderno de campo manual:** Registros em papel se perdem, são ilegíveis ou inconsistentes. Digitalização elimina esses problemas.
- **Carência não respeitada:** Sem alerta automático, colheitas ocorrem dentro do período de carência do defensivo, gerando risco de resíduo.
- **Fiscalização do MAPA sem documentação:** Produtor não consegue comprovar o que aplicou, quando e em qual dosagem.
- **Certificação negada:** Auditorias de Rainforest, GlobalG.A.P. e orgânicos exigem registro completo de aplicações — sem isso, certificação é negada.
- **Compradores exigentes:** Redes de supermercados e exportadores pedem relatório de aplicações por lote; sem sistema, é produzido manualmente com alto risco de erro.

## Regras de Negócio

1. **Vínculo lote-aplicação:** Toda aplicação registrada em um talhão/safra é automaticamente vinculada aos lotes de produção gerados naquele talhão/safra.
2. **Período de carência:** O sistema calcula a data mínima de colheita com base na última aplicação e no período de carência do produto. Colheita antes dessa data gera **alerta bloqueante** (configurável para alerta ou bloqueio).
3. **Dosagem:** O sistema valida se a dosagem registrada está dentro da faixa recomendada na bula. Desvios geram alerta.
4. **Receituário agronômico:** Aplicações de defensivos devem estar vinculadas a um receituário agronômico (número do receituário e RT responsável).
5. **Produtos registrados:** Apenas produtos com registro ativo no MAPA/AGROFIT podem ser usados. Sistema mantém base atualizada.
6. **Cultura autorizada:** O produto deve ser registrado para a cultura em questão. Sistema alerta se houver uso off-label.
7. **Intervalo entre aplicações:** Respeitar intervalo mínimo entre aplicações do mesmo princípio ativo, quando definido.
8. **Imutabilidade:** Registros de aplicação confirmados não podem ser excluídos — apenas marcados como `corrigido` com novo registro.

## Entidades de Dados Principais

- **AplicacaoLoteVinculo:** `id`, `tenant_id`, `lote_id`, `aplicacao_id` (referência ao módulo agrícola), `created_at`
- **AplicacaoRegistro** (do módulo agrícola, referenciado): `id`, `tenant_id`, `talhao_id`, `safra_id`, `produto_id`, `principio_ativo`, `dosagem`, `unidade_dosagem`, `area_aplicada_ha`, `data_aplicacao`, `hora_aplicacao`, `equipamento`, `operador_id`, `receituario_numero`, `rt_responsavel_id`, `condicoes_climaticas_json`, `observacoes`
- **ProdutoDefensivo:** `id`, `nome_comercial`, `principio_ativo`, `registro_mapa`, `classe_toxicologica`, `periodo_carencia_dias`, `culturas_autorizadas[]`, `dosagem_min`, `dosagem_max`, `unidade`
- **AlertaCarencia:** `id`, `tenant_id`, `lote_id`, `produto_id`, `data_aplicacao`, `data_carencia_fim`, `status` (ativo/resolvido), `created_at`

## Integrações Necessárias

- **agricola/operacoes:** Fonte primária dos registros de aplicação. Integração bidirecional — aplicação registrada no campo aparece automaticamente no histórico do lote.
- **Lotes de Produção (este módulo):** Vincular aplicações ao lote correto.
- **operacional/estoque:** Baixar insumo do estoque na aplicação; validar disponibilidade.
- **Base AGROFIT/MAPA:** Consultar produtos registrados, culturas autorizadas e períodos de carência.
- **Laudos e Análises (profissional):** Vincular resultado de análise de resíduos ao histórico de aplicações.

## Fluxo de Uso Principal (step-by-step)

1. Agrônomo emite receituário agronômico no sistema (ou registra número do receituário emitido externamente).
2. Operador de campo executa a aplicação e registra no módulo agrícola: produto, dose, talhão, área, data/hora.
3. Sistema vincula automaticamente a aplicação ao(s) lote(s) de produção do talhão/safra.
4. Sistema calcula data de fim de carência e cria `AlertaCarencia` se houver lotes próximos de colheita.
5. Sistema valida dosagem contra faixa da bula e cultura autorizada — gera alertas se necessário.
6. Na consulta do lote, o histórico completo de aplicações é exibido em ordem cronológica.
7. Na colheita, sistema verifica se todos os períodos de carência foram respeitados antes de permitir criação do lote.
8. Relatório de aplicações por lote pode ser exportado em PDF para entrega a compradores/auditores.

## Casos Extremos e Exceções

- **Aplicação em talhão sem lote:** Se ainda não houve colheita, a aplicação fica vinculada ao talhão/safra. Quando o lote for criado (na colheita), o vínculo é estabelecido retroativamente.
- **Aplicação em múltiplos talhões simultâneos:** Operação de aplicação pode cobrir vários talhões. Cada talhão recebe seu registro individual com área proporcional.
- **Produto não encontrado na base AGROFIT:** Permitir cadastro manual com flag `produto_nao_verificado`. Gera alerta para o RT.
- **Correção de aplicação registrada errada:** Não é possível deletar. Cria-se registro de `estorno` e novo registro correto, ambos vinculados.
- **Carência em período de chuvas:** O período de carência não muda com chuvas no sistema (seguir bula). Campo de observações para o RT justificar decisões.
- **Mistura de tanque:** Registrar cada produto separadamente, com flag `mistura_tanque` e referência cruzada entre os registros.

## Critérios de Aceite (Definition of Done)

- [ ] Vínculo automático de aplicações do módulo agrícola ao lote
- [ ] Cálculo automático de data fim de carência por produto
- [ ] Alerta bloqueante/informativo quando colheita viola período de carência
- [ ] Validação de dosagem contra faixa da bula
- [ ] Validação de cultura autorizada para o produto
- [ ] Registro de receituário agronômico vinculado à aplicação
- [ ] Relatório de histórico de aplicações por lote (tela + PDF)
- [ ] Imutabilidade de registros confirmados (estorno em vez de delete)
- [ ] Teste de tenant isolation
- [ ] API com RBAC (`rastreabilidade:aplicacoes:read`, `rastreabilidade:aplicacoes:write`)

## Sugestões de Melhoria Futura

- **Integração direta com AGROFIT:** API para consultar base atualizada de produtos registrados.
- **OCR de receituário:** Escanear receituário em papel e extrair dados automaticamente.
- **Alerta de produto proibido:** Notificar quando produto usado perde registro no MAPA.
- **Análise preditiva de resíduos:** Com base no histórico, estimar probabilidade de detecção de resíduo em análise.
- **Integração com drones de aplicação:** Capturar dados de aplicação automaticamente de equipamentos conectados.
- **Dashboard de conformidade:** Visão consolidada de todos os lotes com status de carência (verde/amarelo/vermelho).
