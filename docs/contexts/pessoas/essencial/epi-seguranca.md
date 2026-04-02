---
modulo: Pessoas e RH
submodulo: EPI e Segurança
nivel: essencial
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ./cadastro-colaboradores.md
  - ../../operacional/essencial/estoque.md
standalone: false
complexidade: M
assinante_alvo:
  - Pequeno produtor rural
  - Médio produtor rural
  - Agricultor familiar
  - Cooperativas
---

# EPI e Segurança do Trabalho

## Descrição Funcional

Gestão de Equipamentos de Proteção Individual (EPI) e conformidade com normas de segurança do trabalho rural, especialmente a NR-31 (Segurança e Saúde no Trabalho na Agricultura, Pecuária, Silvicultura, Exploração Florestal e Aquicultura). Controla entrega de EPIs por colaborador, estoque de EPIs, vencimento de Certificados de Aprovação (CA), registro de ocorrências/acidentes e acompanhamento de conformidade com as NRs aplicáveis.

## Personas — Quem usa este submódulo

- **Gerente de fazenda:** Garante que equipe está equipada corretamente
- **Técnico de segurança/SESMT:** Gerencia EPIs, investiga acidentes, faz inspeções
- **Encarregado de campo:** Distribui EPIs e fiscaliza uso no dia a dia
- **Colaborador:** Recebe EPI e assina ficha de entrega
- **Proprietário:** Acompanha conformidade para evitar multas e ações trabalhistas

## Dores que resolve

- Falta de controle sobre entrega de EPIs — fichas de papel perdidas
- Multas por não conformidade com NR-31 (Ministério do Trabalho)
- CA vencido torna EPI irregular — risco de interdição
- Desconhecimento sobre quais EPIs são obrigatórios por atividade (aplicação de defensivos, operação de máquinas, manejo de animais)
- Acidentes sem registro formal — risco trabalhista e previdenciário
- Falta de rastreabilidade de quem recebeu qual EPI e quando

## Regras de Negócio

1. NR-31 é a norma principal para segurança do trabalho rural — todos os itens devem ter referência à NR
2. EPI deve ter CA (Certificado de Aprovação) válido emitido pelo MTE
3. Cada entrega de EPI gera ficha de entrega que deve ser assinada pelo colaborador
4. EPI tem vida útil — sistema deve alertar sobre vencimento/troca
5. EPIs obrigatórios variam por atividade: aplicação de defensivos (conjunto completo), operação de máquinas (protetor auricular, óculos), manejo de gado (bota, luva)
6. Colaborador que recusa EPI deve assinar termo de recusa (risco para o empregador)
7. Acidente de trabalho deve gerar CAT (Comunicação de Acidente de Trabalho) em até 24h
8. Acidente fatal ou grave deve ser comunicado imediatamente ao MTE
9. Estoque mínimo de EPIs deve ser mantido — alerta quando abaixo do mínimo
10. Treinamento de uso correto de EPI é obrigatório (NR-31.8)
11. Inspeções periódicas de segurança devem ser registradas

## Entidades de Dados Principais

- **EPI:** id, tenant_id, descricao, tipo (luva/bota/capacete/oculos/protetor_auricular/mascara/roupa_protecao/outros), ca_numero, ca_validade, fabricante, tamanhos_disponiveis, atividades_obrigatorias, nr_referencia, foto_url, created_at
- **EntregaEPI:** id, epi_id, colaborador_id, fazenda_id, tenant_id, data_entrega, quantidade, tamanho, motivo (admissao/substituicao/vencimento/perda), assinatura_url, observacoes, created_at
- **EstoqueEPI:** id, epi_id, fazenda_id, tenant_id, quantidade_disponivel, quantidade_minima, ultima_reposicao
- **OcorrenciaSeguranca:** id, fazenda_id, tenant_id, tipo (acidente/incidente/quase_acidente), data_ocorrencia, colaborador_id, descricao, local, gravidade (leve/moderada/grave/fatal), causa_provavel, acao_corretiva, cat_numero, cat_emitida, fotos_url, status (aberta/em_investigacao/concluida), created_at
- **InspecaoSeguranca:** id, fazenda_id, tenant_id, data_inspecao, inspetor_nome, area_inspecionada, conformidades, nao_conformidades, acoes_requeridas, prazo_correcao, status

## Integrações Necessárias

- **Cadastro de Colaboradores (essencial):** vincula EPIs a colaboradores ativos
- **Estoque (operacional):** controle de estoque de EPIs (se módulo operacional contratado)
- **Treinamentos (profissional):** treinamentos obrigatórios de segurança (NR-31)
- **eSocial (enterprise):** eventos de acidente de trabalho (S-2210) e monitoramento de saúde (S-2220)
- **Financeiro (despesas):** custos com EPIs e segurança do trabalho

## Fluxo de Uso Principal (step-by-step)

1. Administrador cadastra os EPIs disponíveis com CA e NR de referência
2. Define quais EPIs são obrigatórios por tipo de atividade
3. Na admissão, sistema lista EPIs obrigatórios para a função do colaborador
4. Encarregado entrega EPIs ao colaborador e registra no sistema
5. Colaborador (ou encarregado) assina ficha de entrega (assinatura digital ou upload de foto)
6. Sistema controla vida útil e alerta quando EPI precisa ser substituído
7. Quando CA vence, sistema alerta para substituição por EPI com CA válido
8. Se ocorrer acidente, registra ocorrência com detalhes e gravidade
9. Para acidentes com afastamento, sistema orienta emissão de CAT
10. Inspeções periódicas são registradas com conformidades e não-conformidades
11. Não-conformidades geram ações corretivas com prazo e acompanhamento

## Casos Extremos e Exceções

- **CA vencido sem substituto:** EPI não pode ser usado — bloquear atividade até regularização
- **Colaborador alérgico ao material do EPI:** registrar e fornecer alternativa compatível
- **Acidente em fim de semana/feriado:** CAT deve ser emitida no primeiro dia útil seguinte
- **Acidente com terceirizado:** responsabilidade solidária — registrar e comunicar empresa contratante
- **Perda/extravio de EPI:** registrar ocorrência, pode haver desconto conforme acordo
- **Colaborador recusa EPI:** registrar termo de recusa, advertência, risco de justa causa
- **Atividade com múltiplos riscos:** EPI combinado (ex: aplicação de defensivo em área com ruído)
- **Fiscalização do MTE:** sistema deve gerar relatórios de conformidade rapidamente

## Critérios de Aceite (Definition of Done)

- [ ] Cadastro de EPIs com CA, validade e NR de referência
- [ ] Registro de entrega de EPI com ficha assinada
- [ ] Alerta de vencimento de CA e vida útil de EPI
- [ ] Controle de estoque de EPIs com alerta de mínimo
- [ ] Matriz de EPIs obrigatórios por atividade
- [ ] Registro de ocorrências/acidentes com classificação de gravidade
- [ ] Orientação para emissão de CAT em acidentes com afastamento
- [ ] Registro de inspeções de segurança com não-conformidades
- [ ] Ficha de EPI por colaborador (histórico completo de entregas)
- [ ] Isolamento por tenant e fazenda
- [ ] Testes de integração

## Sugestões de Melhoria Futura

- Consulta automática de CA no sistema do MTE para validação
- Assinatura digital biométrica na entrega de EPI (via tablet no campo)
- Dashboard de conformidade NR-31 com semáforo por área
- Checklist digital de inspeção de segurança configurável
- Integração com app de campo para reporte de incidentes com foto e geolocalização
- Relatório de custo de segurança per capita por setor
