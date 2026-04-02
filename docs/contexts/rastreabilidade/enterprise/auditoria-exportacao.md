---
modulo: Rastreabilidade
submodulo: Auditoria para Exportação
nivel: enterprise
core: false
dependencias_core:
  - fazendas
dependencias_modulos:
  - ../essencial/lotes-producao.md
  - ../essencial/origem-destino.md
  - ../essencial/historico-aplicacoes.md
  - ../profissional/cadeia-custodia.md
  - ../profissional/laudos-analises.md
  - ../enterprise/certificacoes.md
  - ../../compliance/enterprise/due-diligence.md
complexidade: XL
assinante_alvo:
  - exportadores
  - tradings
  - cooperativas de exportação
standalone: false
---

# Auditoria para Exportação

## Descrição Funcional

Submódulo que consolida toda a documentação de rastreabilidade necessária para exportação agropecuária, atendendo requisitos de mercados internacionais — União Europeia (EU Deforestation Regulation, MRLs da EFSA), Estados Unidos (FSMA, EPA tolerances), Japão, China e outros. Gera dossiês de exportação por lote/embarque, verifica conformidade com requisitos do destino e mantém registro auditável de cada exportação.

Atua como um "compliance checker" pré-embarque, garantindo que toda a documentação esteja completa e conforme antes do produto sair do país.

## Personas — Quem usa este submódulo

- **Gestor de exportação:** Prepara documentação, verifica conformidade por mercado, gera dossiês.
- **Despachante aduaneiro:** Recebe dossiê organizado para agilizar despacho.
- **Comprador/importador:** Solicita e valida documentação pré-embarque.
- **Fiscal do MAPA (SIF/VIGIAGRO):** Verifica documentação na origem para emissão de certificados fitossanitários.
- **Diretor comercial:** Monitora status de embarques e conformidade.

## Dores que resolve

- **Container retido no porto:** Documentação incompleta causa retenção, demurrage e prejuízo.
- **Produto devolvido no destino:** Não conformidade com LMR (limite máximo de resíduos) do país importador gera devolução ou destruição.
- **Cada mercado, um padrão:** EU, US, Japão têm LMRs diferentes. Sem sistema, verificação manual é caótica.
- **EU Deforestation Regulation:** Nova regulamentação exige geolocalização e prova de não-desmatamento — sem sistema automatizado, compliance é inviável.
- **Retrabalho na documentação:** Mesmos documentos preparados repetidamente para cada embarque.

## Regras de Negócio

1. **Requisitos por mercado-destino:** Sistema mantém base de requisitos por país/bloco. Na criação do dossiê, verifica conformidade com o destino selecionado.
2. **LMR por mercado:** Limites máximos de resíduos de defensivos variam por país. Sistema cruza laudo de resíduos com LMR do destino.
3. **Documentos obrigatórios:** Cada mercado tem lista de documentos obrigatórios (certificado fitossanitário, laudo de resíduos, certificado de origem, packing list, bill of lading, etc.).
4. **Checklist pré-embarque:** Dossiê só é liberado quando 100% dos documentos obrigatórios estão anexados e validados.
5. **Geolocalização (EUDR):** Para EU, cada lote deve ter coordenadas GPS do talhão de origem com prova de não-desmatamento pós-2020.
6. **Declaração de due diligence:** Para EUDR, gerar declaração automática com dados de geolocalização e avaliação de risco.
7. **Validade de documentos:** Certificados e laudos devem estar válidos na data do embarque.
8. **Registro de embarque:** Cada exportação gera registro com dados do embarque (container, navio, data, destino, volumes).

## Entidades de Dados Principais

- **DossieExportacao:** `id`, `tenant_id`, `numero`, `mercado_destino`, `importador`, `data_criacao`, `data_embarque_prevista`, `status` (em_preparacao/completo/embarcado/entregue), `observacoes`
- **DossieItem:** `id`, `dossie_id`, `lote_id`, `quantidade_kg`, `valor_usd`
- **DocumentoExportacao:** `id`, `dossie_id`, `tipo` (fitossanitario/laudo_residuos/certificado_origem/packing_list/bill_of_lading/invoice/eudr_declaration/outro), `numero`, `data_emissao`, `data_validade`, `arquivo_url`, `status` (pendente/anexado/validado/vencido)
- **RequisitoMercado:** `id`, `pais_bloco`, `produto_tipo`, `documentos_obrigatorios[]`, `lmr_json`, `requisitos_especiais_json`, `vigencia_inicio`, `vigencia_fim`
- **EmbarqueRegistro:** `id`, `dossie_id`, `container_numero`, `navio`, `porto_origem`, `porto_destino`, `data_embarque`, `data_chegada_prevista`, `booking_reference`

## Integrações Necessárias

- **Todos os submódulos de Rastreabilidade:** Lotes, origem, aplicações, cadeia de custódia, laudos, certificações.
- **Due Diligence (Compliance):** Avaliação de risco e declaração EUDR.
- **Financeiro:** Valores de exportação, câmbio, custos de embarque.
- **Base de LMR:** EU Pesticide Database, EPA Tolerance, Codex Alimentarius — atualizável.
- **Sistemas de comércio exterior (futuro):** SISCOMEX, Certificado Fitossanitário eletrônico.

## Fluxo de Uso Principal (step-by-step)

1. Gestor de exportação cria dossiê informando mercado destino e importador.
2. Adiciona lotes ao dossiê — sistema verifica automaticamente conformidade de cada lote com requisitos do mercado.
3. Para cada lote, sistema checa: laudo de resíduos vs LMR do destino, certificações exigidas, documentos ambientais.
4. Sistema gera checklist de documentos obrigatórios. Gestor anexa cada documento.
5. Para EU: sistema gera declaração de due diligence com geolocalização e avaliação de risco (integração Compliance).
6. Quando checklist está 100%: dossiê é marcado como `completo`.
7. No embarque, dados do container/navio são registrados. Status muda para `embarcado`.
8. Dossiê é exportado em PDF para envio ao importador e despachante.
9. Confirmação de entrega no destino encerra o dossiê.

## Casos Extremos e Exceções

- **LMR de substância não coberta pelo laudo:** Sistema alerta que laudo não analisou substância com LMR no destino. Sugere reanálise.
- **Mudança de mercado destino durante preparação:** Sistema recalcula conformidade e atualiza checklist. Documentos já anexados são reavaliados.
- **Lote com não-conformidade:** Lote é removido do dossiê automaticamente (ou bloqueado). Alternativa: outro mercado onde é conforme.
- **Certificado fitossanitário vence antes do embarque:** Alerta com prazo. Necessário renovar antes do embarque.
- **Container misto (múltiplos produtores):** Para tradings que consolidam, cada produtor contribui com seu dossiê. Sistema gera consolidação.
- **Embargo de mercado:** Se país de destino fecha mercado para o produto, sistema bloqueia dossiê e alerta.
- **Alteração regulatória em trânsito:** Produto embarcado sob regra A, chega sob regra B. Sistema registra a regra vigente no embarque.

## Critérios de Aceite (Definition of Done)

- [ ] CRUD de dossiês de exportação por mercado destino
- [ ] Base de requisitos por mercado (EU, US, Japão como mínimo)
- [ ] Verificação automática de LMR: laudo vs limites do destino
- [ ] Checklist de documentos obrigatórios por mercado
- [ ] Geração de declaração de due diligence (EUDR)
- [ ] Verificação de geolocalização e não-desmatamento (EUDR)
- [ ] Registro de embarque (container, navio, datas)
- [ ] Exportação de dossiê em PDF
- [ ] Alerta de documento vencendo antes do embarque
- [ ] Teste de tenant isolation

## Sugestões de Melhoria Futura

- **Integração SISCOMEX:** Automatizar preenchimento de dados no sistema de comércio exterior.
- **Certificado fitossanitário eletrônico:** Integração com e-Phyto do MAPA.
- **Tracking de container:** Integração com APIs de rastreamento marítimo (MarineTraffic, etc.).
- **IA para análise regulatória:** Monitorar mudanças regulatórias e alertar impactos nos mercados de destino.
- **Portal do importador:** Área onde importador acompanha preparação do dossiê em tempo real.
- **Câmbio automático:** Integração com APIs de câmbio para precificação em tempo real.
