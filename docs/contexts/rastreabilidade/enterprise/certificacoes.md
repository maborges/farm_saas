---
modulo: Rastreabilidade
submodulo: Certificações
nivel: enterprise
core: false
dependencias_core:
  - fazendas
  - talhoes
dependencias_modulos:
  - ../essencial/lotes-producao.md
  - ../essencial/historico-aplicacoes.md
  - ../profissional/cadeia-custodia.md
  - ../profissional/laudos-analises.md
  - ../../compliance/essencial/documentos-ambientais.md
complexidade: XL
assinante_alvo:
  - grandes produtores
  - cooperativas de exportação
  - tradings
standalone: false
---

# Certificações

## Descrição Funcional

Gerenciamento completo do ciclo de vida de certificações agrícolas — Rainforest Alliance, UTZ (agora parte do Rainforest), GlobalG.A.P., orgânico (IBD, Ecocert, USDA Organic), Fair Trade, 4C, entre outras. Inclui preparação para auditoria, checklist de requisitos por norma, gestão de documentos obrigatórios, acompanhamento de validade, renovação e vinculação de certificados aos lotes de produção.

O módulo não substitui o organismo certificador, mas prepara o produtor para a auditoria, monitora conformidade contínua e vincula os certificados obtidos aos lotes, agregando valor comercial.

## Personas — Quem usa este submódulo

- **Gestor de certificação:** Profissional dedicado à manutenção de certificações. Prepara documentos, acompanha requisitos, agenda auditorias.
- **Produtor/diretor:** Decide quais certificações buscar e monitora status geral.
- **Agrônomo/RT:** Garante que práticas de campo atendem requisitos técnicos da certificação.
- **Auditor externo:** Recebe dossiê digital organizado pelo sistema, agilizando a auditoria.
- **Comprador/trading:** Verifica certificações válidas antes de fechar negócio.

## Dores que resolve

- **Preparação caótica para auditoria:** Sem sistema, produtor corre para juntar documentos semanas antes da auditoria.
- **Certificação perdida por não-conformidade evitável:** Falhas simples (documento vencido, registro faltante) causam perda de certificação.
- **Custo de conformidade alto:** Sem automação, manter múltiplas certificações exige equipe grande.
- **Desconhecimento dos requisitos:** Cada certificação tem centenas de critérios. Sem checklist digital, é fácil esquecer itens.
- **Validade vencida sem perceber:** Certificado vence e produtor só descobre quando comprador exige.

## Regras de Negócio

1. **Certificação por fazenda/grupo:** Certificações podem ser por fazenda individual ou grupo de fazendas.
2. **Checklist por norma:** Cada certificação tem seu checklist de requisitos (importável/configurável). Status: conforme/não-conforme/não-aplicável/em-andamento.
3. **Documentos vinculados:** Cada item do checklist pode ter documentos comprobatórios vinculados.
4. **Validade e renovação:** Certificado tem data de emissão e validade. Alerta em 90/60/30 dias antes do vencimento.
5. **Vinculação lote-certificação:** Lotes produzidos sob certificação válida recebem selo automaticamente.
6. **Segregação:** Sistema valida que lotes certificados não foram misturados com não-certificados (integração com cadeia de custódia).
7. **Histórico de auditorias:** Registrar cada auditoria (data, auditor, resultado, não-conformidades, prazos de correção).
8. **Plano de ação corretiva:** Não-conformidades geram tarefas com responsável e prazo.

## Entidades de Dados Principais

- **Certificacao:** `id`, `tenant_id`, `fazenda_id`, `tipo` (rainforest/globalGAP/organico/fairtrade/4c/outro), `organismo_certificador`, `numero_certificado`, `data_emissao`, `data_validade`, `status` (ativa/suspensa/vencida/em_processo), `escopo`, `arquivo_url`
- **ChecklistCertificacao:** `id`, `certificacao_id`, `norma_versao`, `total_itens`, `conformes`, `nao_conformes`, `nao_aplicaveis`, `percentual_conformidade`
- **ItemChecklist:** `id`, `checklist_id`, `codigo_requisito`, `descricao`, `categoria`, `status` (conforme/nao_conforme/na/em_andamento), `evidencia_url`, `responsavel_id`, `prazo`, `observacoes`
- **Auditoria:** `id`, `certificacao_id`, `data`, `tipo` (inicial/manutencao/renovacao), `auditor_nome`, `organismo`, `resultado` (aprovada/aprovada_com_ressalvas/reprovada), `relatorio_url`
- **NaoConformidade:** `id`, `auditoria_id`, `codigo`, `descricao`, `severidade` (menor/maior/critica), `prazo_correcao`, `responsavel_id`, `status` (aberta/em_correcao/corrigida/verificada), `evidencia_correcao_url`

## Integrações Necessárias

- **Cadeia de Custódia:** Validar segregação de produto certificado.
- **Laudos e Análises:** Laudos como evidência de conformidade.
- **Histórico de Aplicações:** Verificar que defensivos usados são permitidos pela certificação.
- **Compliance Ambiental:** Documentos ambientais como requisito de certificação.
- **QR Code:** Exibir selos de certificação na página pública do lote.
- **Calendário/notificações:** Alertas de vencimento e prazos de correção.

## Fluxo de Uso Principal (step-by-step)

1. Produtor decide buscar certificação → cria registro no sistema com tipo e fazenda.
2. Sistema carrega checklist padrão da norma selecionada (pré-configurado).
3. Gestor de certificação percorre o checklist, marcando conformidade e vinculando evidências.
4. Sistema calcula percentual de conformidade e indica gaps.
5. Não-conformidades geram plano de ação com responsáveis e prazos.
6. Quando checklist está suficientemente conforme, produtor agenda auditoria.
7. Auditor externo realiza auditoria → resultado é registrado no sistema.
8. Se aprovado, certificado é cadastrado com validade. Lotes da fazenda recebem selo.
9. Sistema monitora validade e alerta para renovação.
10. No ciclo seguinte, checklist é reavaliado e auditoria de manutenção é agendada.

## Casos Extremos e Exceções

- **Certificação suspensa:** Comprador notificado automaticamente. Lotes em trânsito perdem selo.
- **Múltiplas certificações simultâneas:** Itens comuns entre checklists são compartilhados (preencher uma vez, contar para várias).
- **Mudança de norma:** Quando certificadora atualiza norma, sistema permite migrar checklist para nova versão, mantendo histórico.
- **Fazenda nova no grupo:** Ao incluir fazenda em certificação de grupo, checklist individual é criado.
- **Não-conformidade crítica:** Bloqueia expedição de lotes certificados até resolução.
- **Certificação de terceiros (fornecedores):** Registrar certificações de fornecedores para rastreabilidade completa.

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de certificações por fazenda com dados do certificado
- [ ] Checklists pré-configurados para Rainforest, GlobalG.A.P. e orgânico
- [ ] Gestão de itens de checklist com evidências
- [ ] Cálculo de percentual de conformidade
- [ ] Registro de auditorias e não-conformidades
- [ ] Plano de ação corretiva com responsáveis e prazos
- [ ] Alerta de vencimento (90/60/30 dias)
- [ ] Vinculação automática lote-certificação
- [ ] Dashboard de status de todas as certificações
- [ ] Teste de tenant isolation

## Sugestões de Melhoria Futura

- **IA para análise de gaps:** Sugerir ações prioritárias com base em não-conformidades mais comuns.
- **Integração com organismos certificadores:** Receber resultado de auditoria automaticamente.
- **Marketplace de certificações:** Conectar produtor a organismos certificadores parceiros.
- **Benchmarking:** Comparar nível de conformidade com média do setor (anônimo).
- **Certificação como serviço:** Consultoria automatizada para preparação de auditoria.
