---
modulo: "Agr\xEDcola"
submodulo: Caderno de Campo
nivel: essencial
core: false
dependencias_core:
  - core/auth
  - core/cadastros/fazendas
  - core/tenant
dependencias_modulos:
  - ../essencial/safras.md
  - ../essencial/operacoes-campo.md
standalone: false
complexidade: M
assinante_alvo:
  - pequeno-produtor
  - medio-produtor
  - grande-produtor
  - cooperativa
  - exportador
---

# Caderno de Campo

## Descricao Funcional

O Caderno de Campo e o registro digital de todas as atividades, observacoes e eventos que ocorrem nos talhoes ao longo de uma safra. Ele substitui o tradicional caderno de papel exigido por legislacao e certificacoes (GlobalG.A.P., Rainforest Alliance, organicos).

O submodulo consolida automaticamente as operacoes registradas e permite adicionar entradas manuais de monitoramento: pragas detectadas, condicoes climaticas observadas, estagio fenologico, fotos geolocalizadas e anotacoes livres.

Funcionalidades principais:
- Visao cronologica (timeline) de todos os eventos do talhao/safra
- Registro de monitoramento de campo: pragas, doencas, plantas daninhas, condicoes do solo
- Captura de fotos com geolocalizacao e vinculacao ao talhao
- Consolidacao automatica de operacoes (plantio, pulverizacao, colheita) no caderno
- Exportacao em PDF para auditorias e certificacoes
- Filtros por talhao, periodo, tipo de registro
- Assinatura digital do responsavel tecnico (agronomo)

## Personas — Quem usa este submodulo

- **Agronomo:** principal usuario — registra visitas, diagnosticos, recomendacoes e assina digitalmente
- **Operador de Campo:** registra observacoes durante o trabalho diario (pragas, falhas de stand, etc.)
- **Produtor Rural:** consulta historico do talhao para tomada de decisao
- **Auditor/Certificador:** acessa o caderno exportado em PDF para verificar conformidade

## Dores que resolve

1. **Compliance:** legislacao brasileira (IN 02/2008 MAPA) exige caderno de campo — versao papel e fragil e facilmente perdida
2. **Certificacoes:** GlobalG.A.P., Rainforest Alliance e certificacoes organicas exigem rastreabilidade completa
3. **Historico perdido:** anotacoes em papel de safras passadas sao descartadas ou iliegiveis
4. **Falta de fotos:** diagnosticos de pragas e doencas sem registro fotografico dificultam assistencia tecnica remota
5. **Assinatura do RT:** agronomo precisa assinar o caderno — processo manual e burocratico

## Regras de Negocio

1. O caderno de campo e gerado automaticamente por safra/talhao (tenant isolation obrigatorio)
2. Entradas de operacoes (plantio, pulverizacao, etc.) sao inseridas automaticamente quando a operacao e concluida
3. Entradas manuais de monitoramento exigem: data, tipo (praga/doenca/daninha/solo/clima/outro), descricao
4. Fotos sao obrigatorias para registros de monitoramento de pragas e doencas (configuravel por tenant)
5. O caderno nao pode ser editado retroativamente alem de 72 horas (periodo configuravel) sem aprovacao do RT
6. A exportacao PDF deve conter: cabecalho com dados da fazenda/safra/talhao, todas as entradas ordenadas cronologicamente, fotos em miniatura, e campo de assinatura do RT
7. Cada entrada registra automaticamente: usuario, data/hora, IP/dispositivo (auditoria)
8. Entradas deletadas sao mantidas com flag `excluida = true` e motivo (auditabilidade)
9. O RT (Responsavel Tecnico) deve ter registro CREA vinculado ao perfil
10. Permissoes: `agricola:caderno:create`, `agricola:caderno:read`, `agricola:caderno:export`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `CadernoCampoEntrada` | id, tenant_id, safra_id, talhao_id, tipo, descricao, data_registro, usuario_id, operacao_id (nullable), excluida, motivo_exclusao | pertence a Safra/Talhao |
| `CadernoCampoFoto` | id, entrada_id, url, latitude, longitude, data_captura | pertence a Entrada |
| `MonitoramentoRegistro` | id, tenant_id, safra_id, talhao_id, tipo_monitoramento, nivel_severidade, praga_doenca_id, descricao, recomendacao | registro de praga/doenca |
| `CadernoExportacao` | id, safra_id, talhao_id, url_pdf, data_geracao, assinado_por, crea_rt | PDF gerado |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `agricola/operacoes` | Leitura | Importa operacoes concluidas como entradas do caderno |
| `agricola/safras` | Leitura | Contexto de safra e talhao |
| `agricola/monitoramento` | Bidirecional | Registros de monitoramento alimentam o caderno |
| `core/auth` | Leitura | Dados do RT (CREA) para assinatura |
| `storage/s3` | Escrita/Leitura | Upload de fotos e armazenamento de PDFs |
| `agricola/defensivos` | Leitura | Dados de receituario para entradas de pulverizacao |

## Fluxo de Uso Principal (step-by-step)

1. Usuario acessa `/agricola/monitoramento` ou entra via safra (`/agricola/safras/[id]/monitoramento`)
2. Visualiza timeline cronologica com todas as entradas (operacoes automaticas + manuais)
3. Clica em "Novo Registro" e seleciona tipo (praga, doenca, daninha, solo, clima, observacao geral)
4. Preenche descricao, nivel de severidade (se aplicavel) e recomendacao
5. Tira foto com o celular — sistema captura geolocalizacao automaticamente
6. Salva o registro — entrada aparece na timeline do caderno
7. Ao final do periodo, agronomo acessa "Exportar Caderno"
8. Sistema gera PDF com todas as entradas, fotos e dados da safra
9. Agronomo assina digitalmente (nome + CREA)
10. PDF fica disponivel para download e e armazenado no historico

## Casos Extremos e Excecoes

- **Sem internet no campo:** operador registra offline no celular — sincroniza quando tiver conexao (data original preservada)
- **Foto sem GPS:** celular sem GPS ativo — permitir registro sem coordenadas mas com alerta
- **Monitoramento sem safra ativa:** permitir registro avulso vinculado apenas ao talhao (periodo entre-safras)
- **Volume de fotos:** uma visita pode gerar 20+ fotos — comprimir automaticamente para armazenamento, manter original por 90 dias
- **Caderno retroativo:** novo cliente digitalizando cadernos antigos — permitir entradas com data passada marcadas como `digitalizacao_retroativa`
- **Auditoria surpresa:** auditor solicita caderno imediatamente — exportacao deve ser rapida (cache de PDF pre-gerado para safras encerradas)
- **Dois agronomos:** fazenda com mais de um RT — ambos podem assinar, registro indica qual assinou

## Criterios de Aceite (Definition of Done)

- [ ] Timeline cronologica renderizando entradas manuais e automaticas (operacoes)
- [ ] Registro de monitoramento com tipo, severidade, descricao e recomendacao
- [ ] Upload de fotos com captura automatica de geolocalizacao
- [ ] Entradas de operacoes inseridas automaticamente no caderno ao serem concluidas
- [ ] Exportacao PDF com layout profissional (cabecalho, entradas, fotos, assinatura)
- [ ] Assinatura digital do RT com nome e CREA
- [ ] Protecao contra edicao retroativa (regra de 72h configuravel)
- [ ] Soft delete com motivo para auditabilidade
- [ ] Filtros por tipo, periodo e talhao
- [ ] Tenant isolation testado
- [ ] Responsivo para uso em celular no campo

## Sugestoes de Melhoria Futura

1. **Modo offline completo:** PWA com sincronizacao automatica ao recuperar conexao
2. **Reconhecimento de pragas por IA:** enviar foto e receber sugestao de diagnostico
3. **Integracao com estacao meteorologica:** inserir dados de clima automaticamente
4. **Alertas de compliance:** notificar quando o caderno esta com mais de X dias sem registros
5. **QR Code por talhao:** auditor escaneia placa no campo e acessa o caderno digital
6. **Versionamento de entradas:** historico de edicoes para auditoria completa
7. **Assinatura com certificado digital ICP-Brasil:** validade juridica plena
