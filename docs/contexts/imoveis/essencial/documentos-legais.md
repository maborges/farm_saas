---
modulo: Imóveis Rurais
submodulo: Documentos Legais
nivel: essencial
core: false
dependencias_core:
  - cadastro-propriedade
  - identidade-acesso
  - notificacoes-alertas
dependencias_modulos:
  - imoveis/essencial/cadastro-imovel
standalone: false
complexidade: S
assinante_alvo:
  - proprietário rural
  - contador agrícola
  - advogado rural
---

# Documentos Legais

## Descrição Funcional

Submódulo responsável pela gestão documental dos imóveis rurais: upload, organização, controle de vencimentos e alertas para documentos legais obrigatórios. Cobre os principais documentos exigidos em financiamentos, auditorias e obrigações fiscais: CCIR, Declaração do ITR (DITR/DIAT), CAR, escritura, matrícula atualizada e outros documentos fundiários.

O foco é garantir que o produtor sempre tenha acesso rápido à documentação atualizada e seja alertado proativamente sobre vencimentos. O sistema implementa versionamento de documentos — cada novo upload de um mesmo tipo gera nova versão, preservando o histórico completo.

Este submódulo atende às exigências da Lei 9.393/1996 (ITR), Lei 12.651/2012 (Código Florestal - CAR), Lei 6.015/1973 (Registro de Imóveis) e normas do INCRA (CCIR).

## Personas — Quem usa este submódulo

- **Proprietário Rural (Owner):** Faz upload e consulta documentos; precisa ter tudo organizado para financiamentos, auditorias e due diligence. Recebe alertas de vencimento.

- **Contador Agrícola:** Acessa DITR e CCIR para obrigações fiscais anuais. Precisa de documentos atualizados para entrega de ITR e LCDPR dentro do prazo.

- **Advogado Rural:** Consulta matrícula e escritura para operações imobiliárias (compra, venda, arrendamento, garantia de financiamento).

- **Gerente de Fazenda:** Monitora vencimentos e providencia renovações. Responsável por manter documentação em dia para crédito rural.

- **Auditor (interno ou externo):** Verifica conformidade documental em auditorias de certificação (GlobalGAP, RTRS, Bonsucro) e fiscais.

- **Técnico de Regularização Ambiental:** Consulta CAR e documentos ambientais para manutenção de regularidade no SICAR.

## Dores que resolve

1. **Documentos vencidos:** CCIR vence anualmente (multa de 10% ao mês + juros). ITR vence em agosto de cada ano (multa de 1% ao mês). Sem alertas, produtor é multado.

2. **Documentos perdidos:** Físicos ou em e-mails dispersos, difíceis de localizar na hora que o banco pede. Produtor perde dias procurando documentação.

3. **Falta de alertas:** Produtor só descobre o vencimento quando já multou. Sistema alerta em T-60, T-30, T-7 e T-1 dias.

4. **Sem histórico de versões:** Não sabe qual é a última certidão de matrícula válida. Sistema versiona automaticamente e exibe sempre a versão ativa.

5. **Acesso restrito inadequado:** Documentos sensíveis (escritura, matrícula) acessíveis a qualquer usuário. Sistema permite restrição por perfil.

6. **Dificuldade em auditorias:** Auditor exige documentos específicos; produtor não encontra rapidamente. Sistema organiza por tipo e imóvel.

7. **CCIR bloqueia crédito:** Banco nega crédito rural por CCIR vencido. Sistema impede criação de contrato de arrendamento com CCIR vencido.

## Regras de Negócio

1. **RN-DL-001:** Todo documento está vinculado a exatamente um `imovel_id` e um `tenant_id`. Isolamento total por tenant.

2. **RN-DL-002:** Tipos de documento: `CCIR`, `ITR_DITR`, `CAR`, `ESCRITURA`, `MATRICULA`, `GEOREFERENCIAMENTO`, `OUTRO`. Tipos pré-definidos com validação.

3. **RN-DL-003:** Documentos dos tipos `CCIR` e `ITR_DITR` têm vencimento anual obrigatório. Campo `data_vencimento` é obrigatório para estes tipos.

4. **RN-DL-004:** Alertas de vencimento são disparados em T-60, T-30, T-7 e T-1 dias para CCIR e ITR. Após vencimento, alerta diário até regularização.

5. **RN-DL-005:** Upload aceita apenas PDF; tamanho máximo 20 MB por arquivo. Validação de integridade do PDF (não corrompido).

6. **RN-DL-006:** Documentos não podem ser excluídos — apenas marcados como `SUBSTITUIDO` ao fazer upload de versão mais recente. Exclusão é lógica (`deleted_at`).

7. **RN-DL-007:** Cada tipo de documento pode ter múltiplas versões; somente a mais recente (maior `versao`) é exibida como ativa. Histórico é preservado.

8. **RN-DL-008:** Acesso a documentos sensíveis (escritura, matrícula) pode ser restrito a perfis `admin` e `owner`. Configuração por tipo de documento.

9. **RN-DL-009:** CCIR vencido bloqueia criação de contrato de arrendamento. Sistema exibe erro: "CCIR do imóvel está vencido. Regularize antes de criar contrato."

10. **RN-DL-010:** Documento CAR sem prazo de vencimento (obrigatório mas sem renovação anual). Campo `data_vencimento` é opcional para CAR.

11. **RN-DL-011:** Upload de documento substitui automaticamente a versão ativa anterior. Versão anterior é marcada como `SUBSTITUIDO` com referência à nova versão.

12. **RN-DL-012:** Download de documento gera URL assinada com validade de 15 minutos. Logs registram quem baixou qual documento e quando.

## Entidades de Dados Principais

### DocumentoLegal
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| tenant_id | UUID | sim | FK → Tenant |
| imovel_id | UUID | sim | FK → ImovelRural |
| tipo | ENUM | sim | CCIR, ITR_DITR, CAR, ESCRITURA, MATRICULA, GEOREFERENCIAMENTO, OUTRO |
| descricao | VARCHAR(255) | não | Descrição livre (ex.: "CCIR 2025 - Fazenda São João") |
| numero_documento | VARCHAR(100) | não | Número do documento (ex.: número do CCIR) |
| data_emissao | DATE | não | Data de emissão do documento |
| data_vencimento | DATE | não | Data de vencimento (obrigatório para CCIR e ITR_DITR) |
| status | ENUM | sim | ATIVO, SUBSTITUIDO, VENCIDO, CANCELADO |
| path_storage | VARCHAR(512) | sim | Caminho no storage (S3/local) |
| nome_arquivo | VARCHAR(255) | sim | Nome original do arquivo |
| tamanho_bytes | INTEGER | sim | Tamanho do arquivo em bytes |
| versao | INTEGER | sim | Número da versão (autoincremento por tipo/imóvel) |
| substituido_por | UUID | não | FK → DocumentoLegal (versão mais recente) |
| restrito | BOOLEAN | sim | Se true, apenas admin/owner podem acessar |
| hash_conteudo | VARCHAR(64) | não | SHA-256 do arquivo para integridade |
| created_by | UUID | sim | FK → Usuário que fez upload |
| created_at | TIMESTAMP | sim | Data do upload |
| updated_at | TIMESTAMP | sim | Última atualização |
| deleted_at | TIMESTAMP | não | Soft delete |

### HistoricoDocumento
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| id | UUID | sim | PK |
| documento_id | UUID | sim | FK → DocumentoLegal |
| acao | ENUM | sim | UPLOAD, SUBSTITUICAO, VISUALIZACAO, DOWNLOAD, EXCLUSAO |
| usuario_id | UUID | sim | FK → Usuario |
| dados_acao | JSONB | não | Dados adicionais da ação (ex.: versão anterior, IP) |
| created_at | TIMESTAMP | sim | Data da ação |

## Integrações Necessárias

- **Imóvel Rural (essencial):** Documento deve estar vinculado a imóvel cadastrado. Validação de existência do imóvel.

- **Notificações (core):** Sistema de alertas dispara notificações de vencimento para o owner e admin. Integração via eventos.

- **Storage (S3/MinIO):** PDFs armazenados em S3 ou storage local configurado no tenant. URLs assinadas para download seguro.

- **Identidade e Acesso:** Restrição de acesso a documentos sensíveis por perfil. Validação de permissão antes de download.

- **Antivírus (futuro):** Scan de arquivos uploadados em busca de malware. Quarentena de arquivos suspeitos.

- **OCR (futuro):** Extração automática de dados do CCIR/ITR via OCR. Preenchimento automático de campos.

## Fluxo de Uso Principal (step-by-step)

### Fluxo 1: Upload de novo documento
1. Usuário acessa o imóvel e abre a aba "Documentos".
2. Clica em "Upload de Documento".
3. Seleciona o tipo de documento (dropdown: CCIR, ITR, CAR, etc.).
4. Informa número do documento, data de emissão e data de vencimento (quando aplicável).
5. Marca checkbox "Restrito" se documento for sensível (escritura, matrícula).
6. Faz upload do PDF (drag-and-drop ou seleção de arquivo).
7. Sistema valida tipo de arquivo (PDF) e tamanho (máx. 20 MB).
8. Sistema valida integridade do PDF (não corrompido).
9. Documento aparece na listagem como "Ativo" com versão 1.
10. Se houver versão anterior do mesmo tipo, ela é marcada como "Substituído".

### Fluxo 2: Substituição de documento (nova versão)
1. Imóvel já possui CCIR 2024 ativo (versão 1).
2. Usuário obtém CCIR 2025 renovado.
3. Acessa imóvel → Documentos → "Nova Versão" no documento existente.
4. Sistema exibe formulário pré-preenchido com dados da versão anterior.
5. Usuário atualiza número do documento, data de emissão e vencimento.
6. Faz upload do novo PDF.
7. Sistema cria versão 2 com status "Ativo".
8. Versão 1 é marcada como "Substituído" com referência à versão 2.
9. Histórico registra substituição com usuário e timestamp.

### Fluxo 3: Alerta de vencimento
1. Cron job diário verifica documentos com vencimento nos próximos 60 dias.
2. Para cada documento, calcula dias até vencimento.
3. Se dias == 60, 30, 7 ou 1, cria notificação para owner e admin.
4. Notificação inclui: tipo de documento, imóvel, data de vencimento, link para upload.
5. Se documento já venceu (dias < 0), cria notificação diária até regularização.
6. Usuário clica na notificação e é direcionado para upload de nova versão.
7. Após upload de nova versão, alertas cessam.

### Fluxo 4: Download de documento restrito
1. Usuário clica em "Download" em um documento.
2. Sistema verifica se documento é restrito (`restrito = true`).
3. Se restrito, verifica se usuário tem perfil admin ou owner.
4. Se não tem permissão, retorna erro 403: "Acesso restrito a administradores."
5. Se tem permissão, gera URL assinada do S3 com validade de 15 minutos.
6. Registra em `HistoricoDocumento`: ação = DOWNLOAD, usuario_id, timestamp, IP.
7. Usuário faz download do arquivo.

### Fluxo 5: Visualização de histórico de versões
1. Usuário acessa detalhes de um documento (ex.: CCIR).
2. Clica em "Ver Histórico".
3. Sistema exibe timeline com todas as versões (Ativo, Substituído, Vencido).
4. Cada versão mostra: número, data de emissão, vencimento, quem fez upload, quando.
5. Usuário pode visualizar/download de versões antigas (se tiver permissão).
6. Histórico ajuda em auditorias: "Qual CCIR estava válido em março/2024?"

## Casos Extremos e Exceções

- **Documento sem vencimento:** Tipos como ESCRITURA e MATRICULA não têm vencimento. Campo `data_vencimento` é opcional para esses tipos. Não geram alertas de vencimento.

- **CCIR vencido:** Exibir badge vermelho na listagem do imóvel. Bloquear criação de contratos de arrendamento com imóvel com CCIR vencido. Mensagem: "CCIR vencido em 15/08/2024. Regularize antes de criar contrato."

- **Upload de formato inválido:** Rejeitar com mensagem clara: "Apenas PDF é aceito. Você enviou 'documento.docx'."

- **Arquivo corrompido:** Validar integridade do PDF no upload (cabeçalho %PDF, estrutura válida). Rejeitar arquivos que não abrem. Mensagem: "Arquivo PDF corrompido. Faça upload novamente."

- **Múltiplos documentos do mesmo tipo:** Permitido. Sistema organiza por versão e exibe sempre a mais recente. Exemplo: múltiplas certidões de matrícula ao longo do tempo.

- **Documento perdido no S3:** Hash do conteúdo é verificado. Se arquivo não existe ou hash diverge, exibe erro: "Arquivo não encontrado. Contate o suporte."

- **Upload simultâneo de duas versões:** Concorrência é tratada com lock no `imovel_id + tipo`. Segundo upload aguarda primeiro completar e então cria versão subsequente.

- **Documento com vírus (futuro):** Antivírus detecta malware em upload. Arquivo é colocado em quarentena. Usuário e admin são notificados.

- **Exclusão acidental:** Soft delete preserva documento. Backoffice pode restaurar se necessário. Logs registram quem excluiu e quando.

## Critérios de Aceite (Definition of Done)

- [ ] Upload de PDF com validação de tipo e tamanho (máx. 20 MB).
- [ ] Versionamento automático por tipo de documento por imóvel.
- [ ] Documento anterior marcado como SUBSTITUIDO ao fazer novo upload do mesmo tipo.
- [ ] Alertas de vencimento disparados via notificação em T-60, T-30, T-7 e T-1 dias.
- [ ] Listagem de documentos do imóvel com status visual (ativo, substituído, vencido).
- [ ] Acesso restrito para documentos sensíveis (escritura, matrícula) por perfil.
- [ ] Testes de tenant isolation para upload e consulta de documentos.
- [ ] Download de documento com URL assinada (validade 15 minutos).
- [ ] Histórico de ações registrado em `HistoricoDocumento`.
- [ ] Validação de integridade de PDF (não corrompido).
- [ ] Bloqueio de criação de arrendamento com CCIR vencido.
- [ ] Timeline de versões funcional para auditoria.

## Sugestões de Melhoria Futura

- **OCR de documentos:** Extrair número, datas e dados do CCIR/ITR automaticamente do PDF. Preenchimento automático de campos. Redução de digitação.

- **Integração CAR:** Consultar situação do CAR diretamente no SICAR via número de inscrição. Status: "Em análise", "Aprovado", "Pendência".

- **Painel de compliance documental:** Dashboard com status de todos os documentos de todos os imóveis do tenant. Semáforo de regularidade (verde/amarelo/vermelho).

- **Assinatura digital:** Integração com Gov.br ou DocuSign para documentos que exigem assinatura eletrônica. Validade jurídica.

- **Validação automática de NIRF/CCIR:** Integração com Receita Federal e INCRA para validar números de documento no momento do upload.

- **Renovação automática de CCIR:** Parceria com contador para renovação automática mediante autorização do produtor.

- **Notificação por WhatsApp:** Alertas de vencimento enviados também por WhatsApp (integração com WhatsApp Business API).

- **Busca full-text em documentos:** Indexação de conteúdo de PDFs para busca por palavras-chave (ex.: encontrar todos os documentos que mencionam "gleba norte").
