# Agrícola — Workflow de Implantação

## Visão Geral
O módulo Agrícola depende do Core completo. Permite gestão de safras, operações de campo e monitoramento de talhões, escalando de um caderno de campo digital até rastreabilidade e prescrições de agricultura de precisão.

## Pré-requisitos
- Core completo (fazendas + talhões cadastrados)
- Pelo menos 1 fazenda ativa com talhões mapeados
- Módulo agrícola habilitado no plano de assinatura

## Sequência de Implantação

### Fase 1 — Essencial: Safra e Caderno de Campo (Semana 1-2)
1. Criar safra ativa (cultura, variedade, ano-safra, talhões vinculados)
2. Cadastrar tipos de operações de campo (plantio, pulverização, colheita, etc.)
3. Configurar caderno de campo (registro de atividades por talhão e data)
4. Testar lançamento de operação vinculada à safra ativa

### Fase 2 — Profissional: Planejamento e Monitoramento (Semana 3-5)
1. Elaborar planejamento de safra por talhão (metas de produtividade, insumos previstos)
2. Configurar monitoramento NDVI (integrar imagens de satélite, definir alertas)
3. Vincular custos de produção ao módulo Financeiro (lançamentos automáticos por operação)
4. Habilitar dashboard agrícola com indicadores por talhão/safra

### Fase 3 — Enterprise: Rastreabilidade e Precisão (Semana 6-8)
1. Ativar rastreabilidade de campo (lotes de insumos, operadores, equipamentos)
2. Configurar prescrições VRT por zona de manejo
3. Habilitar beneficiamento (pós-colheita: secagem, classificação, armazenagem)
4. Integrar com romaneios de colheita para fechamento de safra

## Critérios de Conclusão
- [ ] Safra ativa criada com talhões vinculados
- [ ] Pelo menos 1 operação de campo registrada por talhão
- [ ] Caderno de campo acessível para a equipe de campo
- [ ] Custos de operações refletindo no módulo Financeiro
- [ ] Dashboard com produtividade estimada vs. realizada

## Armadilhas Comuns
- Toda operação de campo deve ser vinculada à safra ativa — operações sem safra não entram nos relatórios de custo
- Custos FIFO de insumos (estoque) são calculados no fechamento — não alterar lotes de estoque após operação lançada
- NDVI requer integração externa (Google Earth Engine ou API de satélite) — validar credenciais antes da ativação
- Talhões criados após o início da safra precisam ser explicitamente adicionados à safra vigente
