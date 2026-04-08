---
modulo: Compliance Ambiental
submodulo: CAR - Gestao
nivel: essencial
core: false
dependencias_core:
  - Identidade e Acesso
  - Cadastro da Propriedade
dependencias_modulos:
  - ../../agricola/essencial/safras.md
standalone: true
complexidade: S
assinante_alvo:
  - pequeno-produtor
  - medio-produtor
  - grande-produtor
  - cooperativa
---

# CAR - Gestao

## Descricao Funcional

O submodulo de Gestao do CAR (Cadastro Ambiental Rural) permite ao produtor consultar, importar e acompanhar o status do registro ambiental de cada propriedade rural. O CAR e obrigatorio para todos os imoveis rurais conforme o Codigo Florestal (Lei 12.651/2012) e condicao para acesso a credito rural, licenciamento ambiental e programas governamentais.

Funcionalidades principais:
- Importacao de recibo e dados do CAR via numero de registro ou arquivo XML/PDF do SICAR
- Visualizacao do perimetro da propriedade e areas declaradas (APP, Reserva Legal, uso consolidado, remanescente de vegetacao nativa)
- Painel de status do CAR: ativo, pendente de analise, cancelado, com retificacao pendente
- Alertas de inconsistencias entre area declarada no CAR e area real do cadastro da fazenda
- Historico de retificacoes e protocolo de acompanhamento junto ao orgao estadual
- Verificacao automatica de sobreposicao com areas publicas (Terras Indigenas, Unidades de Conservacao)

## Personas — Quem usa este submodulo

- **Produtor Rural:** consulta status do CAR de suas propriedades e recebe alertas de pendencias
- **Gerente de Fazenda:** valida que todas as fazendas do grupo possuem CAR ativo e regular
- **Consultor Ambiental:** verifica dados do CAR para elaboracao de laudos e regularizacao
- **Analista de Credito:** confirma situacao do CAR antes de liberar financiamento vinculado a propriedade

## Dores que resolve

1. **Desconhecimento do status:** muitos produtores nao sabem se o CAR esta ativo, pendente ou cancelado
2. **Documentacao descentralizada:** recibos e protocolos ficam em e-mails, pastas fisicas ou com o contador
3. **Risco de perda de credito:** sem CAR ativo, o produtor nao consegue acessar linhas de financiamento rural
4. **Retificacoes esquecidas:** notificacoes do orgao ambiental passam despercebidas e geram cancelamento
5. **Sobreposicao nao detectada:** propriedades com sobreposicao em areas publicas podem ter o CAR suspenso

## Regras de Negocio

1. Cada fazenda deve ter no maximo um CAR ativo vinculado por vez
2. O numero do CAR segue o padrao SICAR: UF-MUNICIPIO-HASH (validacao de formato obrigatoria)
3. O sistema deve alertar quando a area total do CAR divergir mais de 5% da area cadastrada da fazenda
4. Retificacoes devem manter historico completo com data, motivo e protocolo
5. O status do CAR e somente leitura no sistema — reflete o que consta no SICAR
6. Permissoes: `compliance:car:read`, `compliance:car:import`, `compliance:car:update`
7. Dados do CAR sao vinculados ao tenant e a fazenda — isolamento multi-tenant obrigatorio
8. A exclusao de um registro de CAR e logica (soft delete) para manter rastreabilidade

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `CARRegistro` | id, tenant_id, fazenda_id, numero_car, status, area_total_ha, data_inscricao, data_ultima_retificacao, orgao_estadual, protocolo | pertence a Fazenda |
| `CARAreaDeclarada` | id, car_registro_id, tipo_area (APP, RL, uso_consolidado, remanescente), area_ha, geometria_geojson | pertence a CARRegistro |
| `CARRetificacao` | id, car_registro_id, data_protocolo, motivo, numero_protocolo, status | pertence a CARRegistro |
| `CARAlerta` | id, car_registro_id, tipo_alerta, descricao, data_geracao, resolvido | pertence a CARRegistro |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `core/cadastros/fazendas` | Leitura | Obtem dados da fazenda e area total para validacao |
| `core/cadastros/talhoes` | Leitura | Compara geometrias dos talhoes com areas declaradas no CAR |
| SICAR (API publica) | Leitura | Consulta status e dados do CAR por numero de registro |
| `compliance/essencial/app-reserva-legal` | Bidirecional | Areas de APP e RL declaradas no CAR alimentam o monitoramento |
| `compliance/essencial/documentos-ambientais` | Escrita | Recibo do CAR e registrado como documento ambiental |

## Fluxo de Uso Principal (step-by-step)

1. Usuario acessa `/compliance/car` e visualiza lista de fazendas com status do CAR
2. Para fazenda sem CAR vinculado, clica em "Importar CAR"
3. Informa o numero de registro do CAR ou faz upload do recibo/XML
4. Sistema valida o formato, importa os dados e busca status no SICAR
5. Exibe mapa com perimetro da propriedade e areas declaradas sobrepostas aos talhoes
6. Sistema gera alertas automaticos se detectar divergencias de area ou sobreposicoes
7. Usuario acompanha status e recebe notificacoes quando houver mudanca no SICAR
8. Em caso de retificacao, usuario registra protocolo e acompanha andamento

## Casos Extremos e Excecoes

- **CAR de propriedade compartilhada:** dois produtores dividem imovel com um unico CAR — sistema permite vinculo do mesmo CAR a fazendas de tenants diferentes (somente leitura para o segundo)
- **SICAR fora do ar:** sistema deve funcionar offline com dados ja importados e tentar sincronizar periodicamente
- **CAR cancelado:** sistema alerta com urgencia e orienta sobre procedimento de novo registro
- **Mudanca de estado:** produtor compra terra em outro estado — CAR tem formato e orgao diferentes
- **Area zero:** CAR importado com area de APP ou RL zerada — gerar alerta de possivel irregularidade

## Criterios de Aceite (Definition of Done)

- [ ] Importacao de CAR por numero de registro ou upload de arquivo
- [ ] Visualizacao de areas declaradas em mapa com sobreposicao aos talhoes
- [ ] Alertas automaticos de divergencia de area (tolerancia de 5%)
- [ ] Historico de retificacoes com protocolo e status
- [ ] Painel de status consolidado para todas as fazendas do tenant
- [ ] Isolamento multi-tenant validado com testes de integracao
- [ ] Permissoes RBAC aplicadas em todas as rotas
- [ ] Soft delete implementado para registros de CAR

## Sugestoes de Melhoria Futura

1. **Sincronizacao automatica com SICAR:** polling periodico para atualizar status sem intervencao do usuario
2. **Validacao geometrica avancada:** deteccao automatica de sobreposicao com dados de Terras Indigenas e UCs via API do ICMBio
3. **Integracao com PRA:** acompanhamento do Programa de Regularizacao Ambiental vinculado ao CAR
4. **Relatorio para banco:** geracao de documento consolidado do CAR para anexar a propostas de credito rural
5. **Notificacao push:** alerta imediato no celular quando status do CAR mudar
