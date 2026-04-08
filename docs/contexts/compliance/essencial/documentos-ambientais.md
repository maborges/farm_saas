---
modulo: Compliance Ambiental
submodulo: Documentos Ambientais
nivel: essencial
core: false
dependencias_core:
  - Identidade e Acesso
  - Cadastro da Propriedade
dependencias_modulos:
  - ./car-gestao.md
standalone: true
complexidade: S
assinante_alvo:
  - pequeno-produtor
  - medio-produtor
  - grande-produtor
  - cooperativa
---

# Documentos Ambientais

## Descricao Funcional

O submodulo de Documentos Ambientais centraliza o controle de licencas, outorgas, autorizacoes e demais documentos exigidos pela legislacao ambiental brasileira. O sistema rastreia validade, emite alertas de vencimento e mantem historico completo para auditorias e fiscalizacoes.

Funcionalidades principais:
- Cadastro de documentos ambientais: licencas (LP, LI, LO), outorgas de uso de agua, autorizacoes de supressao vegetal, licenca de transporte de produtos perigosos, CTF/AIDA do IBAMA
- Upload de arquivos digitalizados (PDF, imagem) vinculados a cada documento
- Alertas configuráveis de vencimento (30, 60, 90 dias antes)
- Dashboard de situacao documental por fazenda: regular, vencendo, vencido, pendente
- Historico de renovacoes com protocolo e numero de processo
- Filtros por tipo de documento, fazenda, status e periodo de vencimento
- Exportacao de relatorio consolidado para auditorias

## Personas — Quem usa este submodulo

- **Produtor Rural:** consulta situacao dos documentos e recebe alertas de vencimento
- **Gerente de Fazenda:** monitora documentacao de todas as propriedades do grupo
- **Consultor Ambiental:** gerencia renovacoes e protocolos junto aos orgaos ambientais
- **Auditor:** verifica conformidade documental em auditorias internas ou externas
- **Analista de Credito:** confirma regularidade documental para liberacao de financiamento

## Dores que resolve

1. **Documentos vencidos:** licencas e outorgas vencem sem que o produtor perceba, gerando multas
2. **Documentacao dispersa:** arquivos em pastas fisicas, e-mails e escritorios de contabilidade
3. **Renovacao tardia:** protocolos de renovacao sao iniciados tarde demais e a operacao fica irregular
4. **Falta de rastreabilidade:** sem historico, e impossivel provar que a propriedade estava regular em determinada data
5. **Auditorias trabalhosas:** reunir documentos para fiscalizacao ou certificacao leva dias

## Regras de Negocio

1. Cada documento pertence a uma fazenda e a um tenant (isolamento multi-tenant obrigatorio)
2. O sistema deve emitir alertas de vencimento nos marcos configurados (padrao: 90, 60, 30 dias)
3. Documentos vencidos devem ser destacados visualmente e gerar notificacao ao responsavel
4. A renovacao cria novo registro vinculado ao anterior, mantendo cadeia de historico
5. Tipos de documento sao parametrizaveis por tenant (cada estado pode exigir documentos diferentes)
6. Nao e permitido excluir documento com historico de renovacao — apenas soft delete
7. Upload de arquivo e obrigatorio para documentos com status "ativo" (pode ser cadastrado pendente sem arquivo)
8. Permissoes: `compliance:documentos:read`, `compliance:documentos:create`, `compliance:documentos:update`, `compliance:documentos:delete`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `DocumentoAmbiental` | id, tenant_id, fazenda_id, tipo_documento_id, numero, orgao_emissor, data_emissao, data_validade, status, observacoes | pertence a Fazenda, pertence a TipoDocumento |
| `TipoDocumento` | id, tenant_id, nome, sigla, descricao, requer_renovacao, antecedencia_alerta_dias | pertence a Tenant |
| `ArquivoDocumento` | id, documento_id, nome_arquivo, url_storage, mime_type, tamanho_bytes, data_upload | pertence a DocumentoAmbiental |
| `RenovacaoDocumento` | id, documento_anterior_id, documento_novo_id, data_protocolo, numero_protocolo, observacoes | vincula dois DocumentoAmbiental |
| `AlertaVencimento` | id, documento_id, data_alerta, dias_para_vencimento, notificado, data_notificacao | pertence a DocumentoAmbiental |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `core/cadastros/fazendas` | Leitura | Dados da fazenda para vinculacao de documentos |
| `compliance/essencial/car-gestao` | Leitura | Recibo do CAR registrado automaticamente como documento |
| `core/notificacoes` | Escrita | Envio de alertas de vencimento por e-mail e push |
| Storage (S3/MinIO) | Leitura/Escrita | Armazenamento dos arquivos digitalizados |
| `financeiro/despesas` | Leitura | Custos de taxas e renovacoes de licencas |

## Fluxo de Uso Principal (step-by-step)

1. Usuario acessa `/compliance/documentos` e visualiza dashboard de situacao documental
2. Clica em "Novo Documento" e seleciona tipo, fazenda, preenche numero e datas
3. Faz upload do arquivo digitalizado (PDF ou imagem)
4. Sistema calcula e agenda alertas de vencimento conforme configuracao
5. Quando alerta e disparado, responsavel recebe notificacao por e-mail
6. Ao iniciar renovacao, usuario clica em "Renovar" e registra protocolo junto ao orgao
7. Quando novo documento e emitido, cadastra e vincula ao anterior
8. Dashboard atualiza automaticamente o status de regular/vencendo/vencido
9. Para auditorias, usuario exporta relatorio consolidado em PDF

## Casos Extremos e Excecoes

- **Documento sem validade:** algumas autorizacoes nao tem prazo de vencimento — sistema deve aceitar data de validade nula
- **Orgao emissor com sistemas diferentes:** cada estado tem portal proprio para consulta — integracao manual inicialmente
- **Multiplas fazendas na mesma licenca:** licenca estadual que cobre varias propriedades — permitir vinculo a multiplas fazendas
- **Perda de arquivo:** documento fisico extraviado — sistema deve permitir registrar documento sem upload com status "pendente de digitalizacao"
- **Renovacao em andamento sem novo documento:** protocolo registrado mas licenca ainda nao emitida — status intermediario "em renovacao"

## Criterios de Aceite (Definition of Done)

- [ ] CRUD completo de documentos ambientais com upload de arquivo
- [ ] Tipos de documento parametrizaveis por tenant
- [ ] Alertas de vencimento configuráveis e funcionais
- [ ] Dashboard de situacao documental com indicadores visuais (semaforo)
- [ ] Historico de renovacoes com cadeia de rastreabilidade
- [ ] Relatorio consolidado exportavel em PDF
- [ ] Isolamento multi-tenant validado com testes de integracao
- [ ] Permissoes RBAC aplicadas em todas as rotas
- [ ] Soft delete para documentos com historico

## Sugestoes de Melhoria Futura

1. **OCR automatico:** extrair dados (numero, validade, orgao) automaticamente do PDF digitalizado
2. **Integracao com portais estaduais:** consulta automatica de status de licencas nos sistemas dos orgaos ambientais
3. **Workflow de renovacao:** fluxo automatizado com checklist de etapas e responsaveis
4. **Assinatura digital:** assinar documentos gerados pelo sistema com certificado ICP-Brasil
5. **Calendario integrado:** visualizacao de vencimentos em calendario mensal/anual
