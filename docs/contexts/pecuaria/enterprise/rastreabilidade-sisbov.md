---
modulo: Pecuária
submodulo: Rastreabilidade SISBOV
nivel: enterprise
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-rebanho.md
  - ../essencial/manejos-basicos.md
  - ../profissional/sanidade.md
standalone: false
complexidade: XL
assinante_alvo:
  - pecuarista-exportacao
  - gestor-rural
  - veterinario
  - frigorifico
---

# Rastreabilidade SISBOV

## Descrição Funcional

Submódulo de rastreabilidade bovina individual conforme exigências do SISBOV (Serviço de Rastreabilidade da Cadeia Produtiva de Bovinos e Bubalinos) do MAPA. Gerencia o cadastro de animais rastreados com brinco SISBOV, controle de movimentações com GTA (Guia de Trânsito Animal) digital, declaração de rebanho e conformidade com certificadoras (ERAS). Essencial para fazendas que vendem para mercado de exportação (Lista Trace).

Automatiza a geração e acompanhamento de GTAs, validação de conformidade sanitária e emissão de relatórios para auditorias.

## Personas — Quem usa este submódulo

- **Responsável SISBOV da fazenda:** cadastro e manutenção dos animais rastreados, emissão de GTA
- **Veterinário habilitado:** atestados sanitários, supervisão de conformidade
- **Gerente de Fazenda:** acompanhamento de conformidade e prazos
- **Certificadora (ERAS):** auditorias de conformidade (visualização de relatórios)
- **Proprietário:** decisão de quais animais manter na Lista Trace

## Dores que resolve

- Perda de rastreabilidade por falha no registro de movimentações
- GTAs emitidas com erro ou fora do prazo, gerando multas
- Animais perdendo status SISBOV por vacinação não comprovada
- Auditorias da certificadora encontrando inconsistências
- Complexidade de manter conformidade com múltiplas exigências simultâneas

## Regras de Negócio

1. Animal SISBOV deve ter brinco oficial com número único de 15 dígitos
2. Toda movimentação de animal SISBOV exige GTA com dados de origem, destino e finalidade
3. GTA deve ser emitida antes da movimentação física do animal
4. Animal SISBOV deve ter todas as vacinações obrigatórias em dia
5. Período mínimo de permanência na fazenda: 40 dias antes do abate (Lista Trace)
6. Declaração de rebanho semestral obrigatória com contagem total
7. Perda de brinco: notificação em 24h e substituição em até 7 dias
8. Animal que sai do SISBOV não pode retornar (exclusão definitiva)
9. Histórico completo de movimentações deve ser mantido por 5 anos mínimo

## Entidades de Dados Principais

- **AnimalSISBOV:** animal_id, numero_sisbov, data_identificacao, certificadora_eras, status_rastreamento, lista_trace
- **GTA:** id, tenant_id, numero, fazenda_origem_id, destino (fazenda/frigorifico), finalidade (cria|recria|engorda|abate), data_emissao, data_validade, status (emitida|em_transito|concluida|cancelada), animais_json
- **DeclaracaoRebanho:** id, tenant_id, fazenda_id, semestre, ano, total_animais_sisbov, total_rebanho, data_declaracao, protocolo
- **OcorrenciaSISBOV:** id, animal_sisbov_id, tipo (perda_brinco|substituicao|exclusao|obito), data, justificativa

## Integrações Necessárias

- **Cadastro de Rebanho:** Animais base com dados de identificação
- **Sanidade:** Comprovação de vacinações obrigatórias para emissão de GTA
- **Manejos Básicos:** Movimentações que geram necessidade de GTA
- **Fiscal/NF-e (Enterprise):** Vínculo GTA com nota fiscal de venda de gado
- **API MAPA/Defesa Estadual (futuro):** Emissão eletrônica de GTA

## Fluxo de Uso Principal (step-by-step)

1. Cadastrar fazenda como propriedade SISBOV com código ERAS
2. Identificar animais com brinco SISBOV e registrar no sistema
3. Manter vacinações obrigatórias em dia (integração com Sanidade)
4. Para movimentação: gerar GTA com dados de origem, destino e animais
5. Registrar saída dos animais da fazenda com GTA vinculada
6. Registrar chegada no destino e conclusão da GTA
7. Emitir declaração de rebanho semestral
8. Gerar relatórios de conformidade para auditorias da certificadora

## Casos Extremos e Exceções

- **Perda de brinco SISBOV:** Registrar ocorrência imediatamente; sistema gera alerta de substituição em 7 dias
- **Animal SISBOV morre:** Registro obrigatório com causa; notificação à certificadora
- **GTA vencida (animal não chegou ao destino):** Alerta crítico; exigir justificativa
- **Fazenda com ERAS vencido:** Bloquear emissão de GTA; alerta de renovação
- **Auditoria com divergência de contagem:** Ferramenta de reconciliação com relatório de diferenças
- **Transferência entre fazendas do mesmo proprietário:** GTA simplificada mas obrigatória

## Critérios de Aceite (Definition of Done)

- [ ] Cadastro de animais SISBOV com número de brinco oficial
- [ ] Geração de GTA com todos os campos obrigatórios
- [ ] Fluxo completo de GTA: emissão > trânsito > conclusão/cancelamento
- [ ] Declaração de rebanho semestral com geração de relatório
- [ ] Controle de ocorrências (perda de brinco, exclusão, óbito)
- [ ] Validação de conformidade sanitária antes da emissão de GTA
- [ ] Relatórios para auditoria da certificadora
- [ ] Isolamento multi-tenant e testes

## Sugestões de Melhoria Futura

- Integração direta com API e-GTA dos órgãos estaduais de defesa
- Blockchain para certificação imutável de rastreabilidade
- App mobile para leitura de brinco SISBOV em campo
- Dashboard de conformidade com semáforo por animal
- Integração com frigoríficos para confirmação automática de abate
