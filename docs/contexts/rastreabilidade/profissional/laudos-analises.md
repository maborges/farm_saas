---
modulo: Rastreabilidade
submodulo: Laudos e Análises
nivel: profissional
core: false
dependencias_core:
  - fazendas
dependencias_modulos:
  - ../essencial/lotes-producao.md
  - ../essencial/historico-aplicacoes.md
  - ../profissional/cadeia-custodia.md
complexidade: M
assinante_alvo:
  - produtor com venda para redes
  - cooperativas de exportação
  - agroindústrias
standalone: false
---

# Laudos e Análises

## Descrição Funcional

Submódulo para vincular laudos de análises laboratoriais aos lotes de produção — análises de resíduos de defensivos, qualidade de grãos (umidade, impurezas, defeitos), análises microbiológicas, análise de solo e foliar. Centraliza os resultados em um único local rastreável, com controle de validade, laboratório emissor e conformidade com padrões.

Transforma o laudo — hoje um PDF solto ou papel — em um dado estruturado, vinculado ao lote, consultável e verificável.

## Personas — Quem usa este submódulo

- **Responsável de qualidade:** Solicita análises, recebe laudos e vincula aos lotes. Verifica conformidade com padrões.
- **Agrônomo/RT:** Interpreta resultados e decide ações (liberação, reprocessamento, descarte).
- **Setor comercial:** Apresenta laudos ao comprador como prova de qualidade.
- **Auditor de certificação:** Verifica laudos vinculados para validar conformidade.
- **Laboratório externo (futuro):** Envia laudos diretamente ao sistema via integração.

## Dores que resolve

- **Laudos perdidos:** PDFs em e-mails, papéis em gavetas. Centralização digital elimina perda.
- **Laudo desvinculado do lote:** Produtor tem o laudo mas não sabe a qual lote pertence, ou vice-versa.
- **Conformidade manual:** Comparar resultado do laudo com padrão de qualidade manualmente é lento e propenso a erros.
- **Validade vencida:** Laudos têm validade. Sem controle, produtor apresenta laudo vencido ao comprador.
- **Múltiplos padrões:** Cada comprador/mercado tem padrões diferentes. Sem sistema, verificação manual para cada um.

## Regras de Negócio

1. **Vínculo obrigatório:** Todo laudo deve estar vinculado a pelo menos um lote de produção.
2. **Tipos de análise:** `residuos_defensivos`, `qualidade_graos`, `microbiologica`, `solo`, `foliar`, `agua`, `outros`.
3. **Laboratório credenciado:** Registrar dados do laboratório (nome, CNPJ, credenciamento INMETRO/MAPA).
4. **Validade do laudo:** Cada laudo tem data de validade. Sistema alerta 15 dias antes do vencimento.
5. **Conformidade automática:** Sistema compara resultados com padrões configurados (LMR para resíduos, classificação oficial para grãos) e indica conformidade/não-conformidade.
6. **Laudo reprovado:** Se análise indica não-conformidade, lote recebe flag `qualidade_pendente` e não pode ser expedido até resolução.
7. **Upload de documento:** Laudo original (PDF/imagem) é armazenado junto com dados estruturados.
8. **Imutabilidade:** Dados de laudo não são editáveis após confirmação. Novo laudo pode ser vinculado como `reanálise`.

## Entidades de Dados Principais

- **LaudoAnalise:** `id`, `tenant_id`, `lote_id`, `tipo_analise`, `laboratorio_id`, `numero_laudo`, `data_coleta_amostra`, `data_emissao`, `data_validade`, `resultados_json`, `conformidade` (conforme/nao_conforme/parcial), `arquivo_url`, `observacoes`, `created_at`
- **Laboratorio:** `id`, `tenant_id`, `nome`, `cnpj`, `credenciamento`, `contato`, `ativo`
- **PadraoQualidade:** `id`, `tenant_id`, `nome` (ex: "Exportação EU", "Mercado Interno"), `tipo_analise`, `parametros_json` (limites por substância/parâmetro), `ativo`
- **LaudoParametro:** `id`, `laudo_id`, `parametro_nome`, `valor_encontrado`, `unidade`, `limite_maximo`, `conforme`

## Integrações Necessárias

- **Lotes de Produção:** Vincular laudo ao lote e atualizar flag de qualidade.
- **Histórico de Aplicações:** Cruzar resultado de resíduos com aplicações registradas (validação cruzada).
- **QR Code:** Página pública pode exibir resumo do laudo (conforme/não conforme + selo).
- **Cadeia de Custódia:** Registro de evento de "amostragem" na cadeia quando amostra é coletada.
- **Notificações:** Alerta de laudo vencendo, resultado recebido, não-conformidade detectada.

## Fluxo de Uso Principal (step-by-step)

1. Responsável de qualidade coleta amostra do lote e registra no sistema (data, ponto de coleta, responsável).
2. Amostra é enviada ao laboratório.
3. Laboratório emite laudo → responsável registra no sistema: dados estruturados + upload do PDF.
4. Sistema compara automaticamente resultados com padrões de qualidade configurados.
5. Se conforme: lote recebe selo de qualidade e está liberado para expedição.
6. Se não conforme: lote é bloqueado. RT avalia e decide ação (reprocessar, descartar, reanalisar).
7. Laudo fica disponível na ficha do lote e pode ser compartilhado via QR code ou link direto.
8. Sistema monitora validade e alerta quando laudo está próximo do vencimento.

## Casos Extremos e Exceções

- **Laudo com resultado limítrofe:** Valor encontrado muito próximo do limite. Sistema exibe alerta amarelo e sugere reanálise.
- **Múltiplos laudos para o mesmo lote:** Permitido. Último laudo do mesmo tipo é considerado vigente.
- **Laudo de lote mesclado:** Requer nova análise do lote resultante. Laudos dos lotes de origem ficam como referência.
- **Laboratório descredenciado:** Sistema alerta se laudos foram emitidos por laboratório que perdeu credenciamento.
- **Resultado parcial:** Laboratório emite laudo parcial (alguns parâmetros pendentes). Sistema aceita com status `parcial`.
- **Padrão de qualidade atualizado:** Ao atualizar padrão, sistema pode re-checar laudos vigentes contra novo padrão.

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de laudos com upload de documento original
- [ ] Vínculo laudo-lote obrigatório
- [ ] Cadastro de laboratórios
- [ ] Configuração de padrões de qualidade por tipo de análise
- [ ] Comparação automática resultado vs padrão com indicação de conformidade
- [ ] Bloqueio de expedição de lote com laudo não-conforme
- [ ] Alerta de validade de laudo (15 dias antes)
- [ ] Registro de dados estruturados por parâmetro
- [ ] Teste de tenant isolation
- [ ] API com RBAC (`rastreabilidade:laudos:read`, `rastreabilidade:laudos:write`)

## Sugestões de Melhoria Futura

- **Integração direta com laboratórios:** API para receber laudos automaticamente do LIMS do laboratório.
- **OCR de laudos em PDF:** Extrair dados estruturados automaticamente de laudos digitalizados.
- **Histórico de qualidade por talhão:** Análise longitudinal de qualidade por talhão ao longo das safras.
- **Selo digital verificável:** Selo de qualidade com verificação online (similar a certificado digital).
- **Benchmark de qualidade:** Comparar resultados do produtor com média da região/cooperativa (anônimo).
