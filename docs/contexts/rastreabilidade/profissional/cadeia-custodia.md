---
modulo: Rastreabilidade
submodulo: Cadeia de Custódia
nivel: profissional
core: false
dependencias_core:
  - fazendas
  - usuarios
dependencias_modulos:
  - ../essencial/lotes-producao.md
  - ../essencial/origem-destino.md
  - ../essencial/historico-aplicacoes.md
complexidade: L
assinante_alvo:
  - produtor com certificação
  - cooperativas de exportação
  - agroindústrias
standalone: false
---

# Cadeia de Custódia

## Descrição Funcional

A cadeia de custódia (chain of custody) documenta a sequência ininterrupta de responsáveis por um lote de produção em cada etapa — desde a colheita até o destino final. Diferente do simples rastreio de origem-destino, a cadeia de custódia registra **quem** foi responsável, **quando** assumiu e transferiu a custódia, e **em quais condições** o produto estava em cada ponto.

Este submódulo é essencial para certificações que exigem chain of custody (Rainforest Alliance, UTZ, Fair Trade) e para operações de exportação onde cada elo da cadeia precisa ser documentado e auditável.

## Personas — Quem usa este submódulo

- **Gestor de qualidade:** Configura os pontos de custódia, define responsáveis e monitora a integridade da cadeia.
- **Operadores em cada ponto:** Registram recebimento e transferência de custódia (colheita, armazém, beneficiamento, expedição).
- **Auditor de certificação:** Verifica que a cadeia está completa e sem gaps para emitir certificado.
- **Comprador/importador:** Consulta a cadeia de custódia para validar procedência e integridade.

## Dores que resolve

- **Gaps na cadeia:** Sem registro formal de transferência, há "buracos" onde não se sabe quem era responsável pelo produto.
- **Certificação rejeitada:** Auditorias de Rainforest/UTZ rejeitam certificação por falta de chain of custody documentada.
- **Responsabilidade indefinida:** Em caso de problema (contaminação, perda), não se sabe quem era responsável naquele momento.
- **Exportação bloqueada:** Importadores exigem documentação de custódia que o produtor não consegue gerar.
- **Mistura de produto certificado e não certificado:** Sem controle de custódia, produto certificado pode ser misturado com convencional, perdendo a certificação.

## Regras de Negócio

1. **Cadeia ininterrupta:** Entre a criação do lote e seu destino final, não pode haver gap temporal — cada minuto do lote deve estar sob custódia de um responsável.
2. **Transferência formal:** A transferência de custódia requer aceite do receptor. O transferente registra a saída; o receptor confirma o recebimento.
3. **Condições no momento da transferência:** Cada ponto de custódia registra condições do produto (peso, temperatura, umidade, aspecto visual — conforme configuração).
4. **Segregação obrigatória:** Produto certificado deve estar segregado de produto convencional. Sistema alerta se lotes de tipos diferentes forem armazenados no mesmo local.
5. **Assinatura digital:** Cada evento de custódia é assinado digitalmente pelo responsável (assinatura simplificada via app/senha).
6. **Imutabilidade total:** Eventos de custódia são append-only. Correções geram novo evento do tipo `correcao` referenciando o original.
7. **Tempo máximo sem evento:** Configurável por ponto. Se um lote fica mais de X horas em um ponto sem evento, gera alerta.

## Entidades de Dados Principais

- **CadeiaCustodia:** `id`, `tenant_id`, `lote_id`, `status` (em_andamento/completa/com_gaps), `created_at`, `completed_at`
- **EventoCustodia:** `id`, `tenant_id`, `cadeia_id`, `lote_id`, `tipo` (recebimento/armazenamento/processamento/transferencia/expedicao/correcao), `ponto_custodia_id`, `responsavel_id`, `data_hora`, `condicoes_json` (peso, temp, umidade), `assinatura_hash`, `evento_anterior_id`, `observacoes`, `created_at`
- **PontoCustodia:** `id`, `tenant_id`, `nome`, `tipo` (campo/armazem/beneficiamento/transporte/expedição), `localizacao`, `capacidade`, `condicoes_requeridas_json`, `ativo`
- **TransferenciaCustodia:** `id`, `tenant_id`, `evento_saida_id`, `evento_entrada_id`, `status` (pendente/confirmada/rejeitada), `motivo_rejeicao`

## Integrações Necessárias

- **Lotes de Produção:** Ponto de partida — criação do lote inicia a cadeia de custódia.
- **Origem-Destino:** Destino final encerra a cadeia de custódia.
- **Certificações (enterprise):** Validar que cadeia atende requisitos da certificação específica.
- **QR Code (este módulo):** QR code inclui link para consulta da cadeia de custódia.
- **core/usuarios:** Identificar responsáveis em cada ponto.

## Fluxo de Uso Principal (step-by-step)

1. Lote é criado na colheita → sistema inicia `CadeiaCustodia` e registra primeiro `EventoCustodia` (tipo: recebimento, ponto: campo, responsável: gerente de campo).
2. Lote é transferido para armazém → gerente de campo registra evento de `transferencia` (saída). Responsável do armazém confirma `recebimento` (entrada).
3. Sistema valida que não há gap temporal entre saída e entrada.
4. No armazém, eventos de `armazenamento` registram condições periódicas (temperatura, umidade).
5. Lote vai para beneficiamento → nova transferência com aceite do receptor.
6. Após beneficiamento, transferência para expedição.
7. Na expedição, evento final encerra a cadeia. Status muda para `completa`.
8. Auditor consulta a cadeia completa e valida integridade (sem gaps, com assinaturas).

## Casos Extremos e Exceções

- **Receptor não confirma recebimento:** Transferência fica em status `pendente`. Alerta é enviado após tempo configurável. Cadeia mostra gap potencial.
- **Transferência rejeitada:** Receptor rejeita (ex: peso divergente). Lote volta à custódia do transferente com evento de `retorno`.
- **Lote fracionado durante custódia:** Cada fração recebe sua própria cadeia de custódia, herdando o histórico do lote pai até o ponto de fracionamento.
- **Perda parcial em ponto de custódia:** Registrada como evento especial com quantidade perdida e justificativa.
- **Falha de conectividade no campo:** App permite registro offline com sincronização posterior. Timestamp do dispositivo é usado, com flag `registro_offline`.
- **Custódia compartilhada:** Em pontos onde múltiplas pessoas são responsáveis (ex: turno), o responsável é o líder do turno.

## Critérios de Aceite (Definition of Done)

- [ ] Criação automática de cadeia de custódia ao criar lote
- [ ] Registro de eventos de custódia com assinatura digital simplificada
- [ ] Transferência com fluxo de aceite (pendente → confirmada/rejeitada)
- [ ] Detecção automática de gaps temporais na cadeia
- [ ] Registro de condições do produto em cada ponto (configurável)
- [ ] Visualização da cadeia completa em timeline
- [ ] Imutabilidade (append-only) de eventos
- [ ] Alerta para transferências pendentes há mais de X horas
- [ ] Suporte a registro offline com sincronização
- [ ] Teste de tenant isolation
- [ ] API com RBAC (`rastreabilidade:custodia:read`, `rastreabilidade:custodia:write`)

## Sugestões de Melhoria Futura

- **NFC/RFID:** Tags físicas nos lotes que registram automaticamente passagem por pontos de custódia.
- **Câmeras com IA:** Registro visual automático em pontos de custódia via câmeras.
- **Integração com blockchain:** Cada evento de custódia registrado em blockchain para imutabilidade absoluta.
- **App dedicado para operadores:** App simplificado apenas para registro de custódia, sem acesso ao sistema completo.
- **Indicador de integridade:** Score de integridade da cadeia (0-100%) baseado em completude, pontualidade e conformidade.
