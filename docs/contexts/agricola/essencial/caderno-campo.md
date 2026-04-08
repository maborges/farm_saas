---
modulo: "Agrícola"
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

## Descrição Funcional

O Caderno de Campo é o registro digital de todas as atividades, observações e eventos que ocorrem nos talhões ao longo de uma safra. Ele substitui o tradicional caderno de papel exigido por legislação e certificações (GlobalG.A.P., Rainforest Alliance, orgânicos).

O submódulo consolida automaticamente as operações registradas e permite adicionar entradas manuais de monitoramento: pragas detectadas, condições climáticas observadas, estágio fenológico, fotos geolocalizadas e anotações livres.

### Contexto Brasileiro e Legislação

No Brasil, o caderno de campo é **obrigatório** por múltiplas legislações:

1. **Lei 7.802/89 (Lei dos Agrotóxicos)**: Exige registro de todas as aplicações de defensivos agrícolas
2. **IN 02/2008 MAPA**: Institui o Caderno de Campo para rastreabilidade de produtos vegetais
3. **Portaria Conjunta ANVISA/IBAMA/MAPA 01/2020**: Dispõe sobre notificação de suspeita de fitointoxicação
4. **Programa de Análise de Resíduos de Agrotóxicos em Alimentos (PARA)**: ANVISA pode solicitar caderno de campo para investigação

Para **exportação**, o caderno de campo é exigência crítica:

- **GlobalG.A.P.**: Certificação exigida por supermercados europeus. Auditoria verifica caderno de campo completo com aplicações, carências e EPIs
- **USDA Organic**: Para exportação de orgânicos para EUA, caderno deve comprovar ausência de sintéticos por 3+ anos
- **Rainforest Alliance**: Certificação para café, cacau, soja exige registro de práticas sustentáveis
- **Due Diligence Regulation 2023/1115 (UE)**: Regulamentação de desmatamento importado exige geolocalização de talhões e histórico de manejo

Funcionalidades principais:
- Visão cronológica (timeline) de todos os eventos do talhão/safra
- Registro de monitoramento de campo: pragas, doenças, plantas daninhas, condições do solo
- Captura de fotos com geolocalização e vinculação ao talhão
- Consolidação automática de operações (plantio, pulverização, colheita) no caderno
- Exportação em PDF para auditorias e certificações
- Filtros por talhão, período, tipo de registro
- Assinatura digital do responsável técnico (agrônomo com CREA)

## Personas — Quem usa este submódulo

- **Agrônomo/Responsável Técnico**: Principal usuário — registra visitas, diagnósticos, recomendações e assina digitalmente. Precisa ter CREA ativo e registro no conselho regional.

- **Operador de Campo**: Registra observações durante o trabalho diário (pragas, falhas de stand, condições de solo). Muitas vezes usa celular no modo offline.

- **Produtor Rural**: Consulta histórico do talhão para tomada de decisão. Exporta caderno para financiamento bancário (Plano Safra) ou seguro rural.

- **Auditor/Certificador**: Acessa o caderno exportado em PDF para verificar conformidade com GlobalG.A.P., MAPA, orgânicos.

- **Fiscal do MAPA/ANVISA**: Solicita caderno de campo em fiscalizações ou investigações de resíduos.

## Dores que resolve

1. **Compliance legal**: Legislação brasileira (IN 02/2008 MAPA) exige caderno de campo — versão papel é frágil e facilmente perdida. Multas podem chegar a R$ 150.000.

2. **Certificações**: GlobalG.A.P., Rainforest Alliance e certificações orgânicas exigem rastreabilidade completa. Sem caderno, produtor perde acesso a mercados premium.

3. **Histórico perdido**: Anotações em papel de safras passadas são descartadas ou ilegíveis. Produtor de café não consegue comprovar manejo orgânico de 3 anos.

4. **Falta de fotos**: Diagnósticos de pragas e doenças sem registro fotográfico dificultam assistência técnica remota. Comum em regiões remotas do MATOPIBA.

5. **Assinatura do RT**: Agrônomo precisa assinar o caderno — processo manual é burocrático. Assinatura digital agiliza e dá validade técnica.

6. **Fiscalização surpresa**: Produtor é notificado de fiscalização e tem 48h para apresentar caderno. Versão digital permite exportação imediata.

7. **Rastreabilidade de EPIs**: Auditoria exige comprovação de entrega de EPIs para aplicadores. Caderno digital registra entrega e treinamento.

## Regras de Negócio

1. O caderno de campo é gerado automaticamente por safra/talhão (tenant isolation obrigatório)
2. Entradas de operações (plantio, pulverização, etc.) são inseridas automaticamente quando a operação é concluída
3. Entradas manuais de monitoramento exigem: data, tipo (praga/doença/daninha/solo/clima/outro), descrição
4. **Fotos obrigatórias**: Para registros de monitoramento de pragas e doenças, foto é obrigatória (configurável por tenant)
5. **Período de carência**: O caderno não pode ser editado retroativamente além de 72 horas (período configurável) sem aprovação do RT
6. A exportação PDF deve conter: cabeçalho com dados da fazenda/safra/talhão, todas as entradas ordenadas cronologicamente, fotos em miniatura, e campo de assinatura do RT
7. Cada entrada registra automaticamente: usuário, data/hora, IP/dispositivo (auditoria)
8. Entradas deletadas são mantidas com flag `excluida = true` e motivo (auditabilidade)
9. O RT (Responsável Técnico) deve ter registro CREA vinculado ao perfil
10. **Entrega de EPIs**: Registro de entrega de Equipamento de Proteção Individual deve ser feito com assinatura do trabalhador
11. **Receituário agronômico**: Entradas de pulverização devem referenciar número do receituário (Lei 7.802/89)
12. Permissões: `agricola:caderno:create`, `agricola:caderno:read`, `agricola:caderno:export`, `agricola:caderno:assinar`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `CadernoCampoEntrada` | id, tenant_id, safra_id, talhao_id, tipo, descricao, data_registro, usuario_id, operacao_id (nullable), excluida, motivo_exclusao | pertence a Safra/Talhão |
| `CadernoCampoFoto` | id, entrada_id, url, latitude, longitude, data_captura | pertence a Entrada |
| `MonitoramentoRegistro` | id, tenant_id, safra_id, talhao_id, tipo_monitoramento, nivel_severidade, praga_doenca_id, descricao, recomendacao | registro de praga/doença |
| `CadernoExportacao` | id, safra_id, talhao_id, url_pdf, data_geracao, assinado_por, crea_rt | PDF gerado |
| `EPIEntrega` | id, tenant_id, trabalhador_id, epi_tipo, data_entrega, validade, assinatura | registro de EPI |
| `VisitaTecnica` | id, tenant_id, safra_id, talhao_id, responsavel_tecnico, cret, data_visita, observacoes, recomendacoes | visita do agrônomo |

## Integrações Necessárias

| Sistema/Modulo | Tipo | Descrição |
|----------------|------|-----------|
| `agricola/operacoes` | Leitura | Importa operações concluídas como entradas do caderno |
| `agricola/safras` | Leitura | Contexto de safra e talhão |
| `agricola/monitoramento` | Bidirecional | Registros de monitoramento alimentam o caderno |
| `core/auth` | Leitura | Dados do RT (CREA) para assinatura |
| `storage/s3` | Escrita/Leitura | Upload de fotos e armazenamento de PDFs |
| `agricola/defensivos` | Leitura | Dados de receituário para entradas de pulverização |
| `core/cadastros/trabalhadores` | Leitura | Dados de trabalhadores para registro de EPI |

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa `/agricola/monitoramento` ou entra via safra (`/agricola/safras/[id]/monitoramento`)
2. Visualiza timeline cronológica com todas as entradas (operações automáticas + manuais)
3. Clica em "Novo Registro" e seleciona tipo (praga, doença, daninha, solo, clima, observação geral)
4. Preenche descrição, nível de severidade (se aplicável) e recomendação
5. Tira foto com o celular — sistema captura geolocalização automaticamente
6. **Para pragas/doenças**: Sistema sugere identificação baseada em imagem (IA futura) e cultura
7. Salva o registro — entrada aparece na timeline do caderno
8. **Visita técnica**: Agrônomo registra visita com recomendações e assina com CREA
9. **Entrega de EPIs**: Registro de entrega de equipamentos com assinatura do trabalhador
10. Ao final do período, agrônomo acessa "Exportar Caderno"
11. Sistema gera PDF com todas as entradas, fotos e dados da safra
12. Agrônomo assina digitalmente (nome + CREA)
13. PDF fica disponível para download e é armazenado no histórico
14. **Para certificação**: Exportar com modelo específico (GlobalG.A.P., orgânicos)

## Casos Extremos e Exceções

- **Sem internet no campo**: Operador registra offline no celular — sincroniza quando tiver conexão (data original preservada). Crítico para MATOPIBA e regiões remotas.

- **Foto sem GPS**: Celular sem GPS ativo — permitir registro sem coordenadas mas com alerta. Aceitável para caderno interno, não para certificação.

- **Monitoramento sem safra ativa**: Permitir registro avulso vinculado apenas ao talhão (período entre-safras). Comum para monitoramento de solo ou plantas daninhas.

- **Volume de fotos**: Uma visita pode gerar 20+ fotos — comprimir automaticamente para armazenamento, manter original por 90 dias.

- **Caderno retroativo**: Novo cliente digitalizando cadernos antigos — permitir entradas com data passada marcadas como `digitalizacao_retroativa` com justificativa.

- **Auditoria surpresa**: Auditor solicita caderno imediatamente — exportação deve ser rápida (cache de PDF pré-gerado para safras encerradas).

- **Dois agrônomos**: Fazenda com mais de um RT — ambos podem assinar, registro indica qual assinou.

- **CREA vencido**: Responsável técnico com registro vencido — alertar e bloquear assinatura até regularização.

- **Fiscalização MAPA**: Produtor notificado de fiscalização — sistema deve gerar relatório específico com todas as aplicações de defensivos da safra.

- **Certificação orgânica**: Caderno deve comprovar ausência de sintéticos por 36 meses — exportar histórico completo com destaque para insumos permitidos.

## Critérios de Aceite (Definition of Done)

- [ ] Timeline cronológica renderizando entradas manuais e automáticas (operações)
- [ ] Registro de monitoramento com tipo, severidade, descrição e recomendação
- [ ] Upload de fotos com captura automática de geolocalização
- [ ] Entradas de operações inseridas automaticamente no caderno ao serem concluídas
- [ ] Exportação PDF com layout profissional (cabeçalho, entradas, fotos, assinatura)
- [ ] Assinatura digital do RT com nome e CREA
- [ ] Proteção contra edição retroativa (regra de 72h configurável)
- [ ] Soft delete com motivo para auditabilidade
- [ ] Filtros por tipo, período e talhão
- [ ] Tenant isolation testado
- [ ] Responsivo para uso em celular no campo
- [ ] Modo offline funcional com sincronização
- [ ] Registro de entrega de EPIs com assinatura
- [ ] Modelos de exportação para certificações (GlobalG.A.P., orgânicos)

## Sugestões de Melhoria Futura

1. **Modo offline completo**: PWA com sincronização automática ao recuperar conexão

2. **Reconhecimento de pragas por IA**: Enviar foto e receber sugestão de diagnóstico baseado em banco de dados da Embrapa

3. **Integração com estação meteorológica**: Inserir dados de clima automaticamente (precipitação, temperatura, umidade)

4. **Alertas de compliance**: Notificar quando o caderno está com mais de X dias sem registros

5. **QR Code por talhão**: Auditor escaneia placa no campo e acessa o caderno digital

6. **Versionamento de entradas**: Histórico de edições para auditoria completa

7. **Assinatura com certificado digital ICP-Brasil**: Validade jurídica plena

8. **Integração com MAPA**: Envio automático de dados para sistemas do ministério (SISCOMEX, etc.)

9. **Relatório de resíduos**: Gerar relatório para PARA (Programa de Análise de Resíduos) da ANVISA

10. **Treinamento online**: Módulo de capacitação para aplicadores com registro no caderno
