---
modulo: Compliance Ambiental
submodulo: Relatorios ESG
nivel: profissional
core: false
dependencias_core:
  - Identidade e Acesso
  - Cadastro da Propriedade
dependencias_modulos:
  - ../essencial/car-gestao.md
  - ../essencial/app-reserva-legal.md
  - ../essencial/documentos-ambientais.md
  - ./monitoramento-desmatamento.md
  - ./gestao-residuos.md
standalone: true
complexidade: M
assinante_alvo:
  - medio-produtor
  - grande-produtor
  - cooperativa
  - trading-agricola
---

# Relatorios ESG

## Descricao Funcional

O submodulo de Relatorios ESG (Environmental, Social and Governance) gera relatorios simplificados de sustentabilidade para propriedades rurais, consolidando dados ambientais ja existentes no sistema em formatos reconhecidos pelo mercado. O foco e permitir que produtores demonstrem conformidade ambiental para compradores, bancos, certificadoras e investidores sem necessidade de consultoria especializada.

Funcionalidades principais:
- Geracao automatica de scorecard ESG ambiental por fazenda
- Indicadores padronizados: area preservada (%), taxa de devolucao de embalagens, alertas de desmatamento, documentos em dia
- Templates de relatorio alinhados a frameworks simplificados (GRI basico, SASB agricultura)
- Comparativo de desempenho ESG entre periodos e entre fazendas
- Exportacao em PDF e formatos digitais para anexar a propostas comerciais
- Painel de gaps: o que falta para melhorar o score ESG
- Selo de conformidade interna com QR code verificavel

## Personas — Quem usa este submodulo

- **Produtor Rural:** gera relatorio ESG para apresentar a compradores e bancos
- **Gerente de Fazenda:** acompanha evolucao do score ESG de todas as propriedades
- **Analista de Compliance:** identifica gaps e prioriza acoes de melhoria
- **Trading Agricola:** exige e verifica relatorios ESG de fornecedores
- **Analista de Credito:** utiliza score ESG como criterio para taxas diferenciadas de financiamento verde

## Dores que resolve

1. **Relatorios caros:** contratar consultoria ESG custa dezenas de milhares de reais — inviavel para a maioria dos produtores
2. **Dados dispersos:** informacoes ambientais estao espalhadas em modulos diferentes sem visao consolidada
3. **Falta de padronizacao:** cada comprador pede informacoes em formato diferente
4. **Desconhecimento de gaps:** produtor nao sabe o que precisa melhorar para atender exigencias ESG
5. **Perda de oportunidades:** sem relatorio, produtor perde acesso a premios por sustentabilidade e linhas de credito verde
6. **Atualizacao manual:** relatorios ficam desatualizados porque dependem de coleta manual de dados

## Regras de Negocio

1. O score ESG e calculado automaticamente com base em dados do sistema — nao permite input manual de indicadores
2. Indicadores com dados insuficientes sao marcados como "nao disponivel" e reduzem o score proporcionalmente
3. O relatorio deve ter periodo de referencia obrigatorio (trimestral, semestral ou anual)
4. Cada indicador tem peso configuravel pelo tenant (padrao: pesos iguais)
5. O selo de conformidade tem validade de 90 dias e precisa ser renovado com dados atualizados
6. Relatorios gerados sao imutaveis — qualquer alteracao gera nova versao
7. O QR code do selo aponta para URL publica de verificacao (nao expoe dados sigilosos)
8. Permissoes: `compliance:esg:read`, `compliance:esg:generate`, `compliance:esg:configure`
9. Dados vinculados ao tenant com isolamento multi-tenant obrigatorio

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `RelatorioESG` | id, tenant_id, fazenda_id, periodo_inicio, periodo_fim, score_total, status (rascunho, publicado), versao, data_geracao, url_pdf | pertence a Fazenda |
| `IndicadorESG` | id, relatorio_id, categoria (ambiental, social, governanca), nome, valor, meta, unidade, peso, status_dado (disponivel, insuficiente) | pertence a RelatorioESG |
| `ConfiguracaoESG` | id, tenant_id, pesos_indicadores_json, template_id, logo_url, texto_complementar | pertence a Tenant |
| `SeloConformidade` | id, relatorio_id, codigo_verificacao, data_emissao, data_validade, qr_code_url, url_verificacao | pertence a RelatorioESG |
| `GapESG` | id, relatorio_id, indicador_id, descricao_gap, acao_sugerida, prioridade | pertence a RelatorioESG |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `compliance/essencial/car-gestao` | Leitura | Status do CAR para indicador de regularidade documental |
| `compliance/essencial/app-reserva-legal` | Leitura | Percentual de area preservada e deficit de RL |
| `compliance/essencial/documentos-ambientais` | Leitura | Taxa de documentos em dia |
| `compliance/profissional/monitoramento-desmatamento` | Leitura | Alertas de desmatamento no periodo |
| `compliance/profissional/gestao-residuos` | Leitura | Taxa de devolucao de embalagens |
| `pessoas/essencial/epi-seguranca` | Leitura | Indicadores sociais (EPIs, seguranca) |
| Storage (S3/MinIO) | Escrita | Armazenamento dos relatorios PDF gerados |

## Fluxo de Uso Principal (step-by-step)

1. Usuario acessa `/compliance/esg` e visualiza dashboard com score ESG atual
2. Clica em "Gerar Relatorio" e seleciona fazenda e periodo de referencia
3. Sistema coleta automaticamente dados de todos os modulos integrados
4. Calcula score por indicador e score total ponderado
5. Exibe preview do relatorio com indicadores, graficos e analise de gaps
6. Usuario revisa e pode adicionar texto complementar
7. Publica o relatorio, gerando PDF e selo de conformidade com QR code
8. Relatorio fica disponivel para download e compartilhamento
9. QR code pode ser verificado por terceiros em URL publica
10. Painel de gaps sugere acoes prioritarias para melhorar o score

## Casos Extremos e Excecoes

- **Fazenda nova sem historico:** poucos dados disponiveis — relatorio e gerado com indicadores "nao disponivel" e score parcial
- **Modulo nao contratado:** tenant sem modulo de residuos — indicador correspondente e omitido e score recalculado
- **Dados contradictorios:** area preservada no CAR diverge do monitoramento de satelite — sistema usa dado mais conservador e sinaliza divergencia
- **Periodo com gap de dados:** sistema ficou offline por semanas — indicar periodo sem dados e calcular com o disponivel
- **Selo vencido:** relatorio com selo expirado — URL de verificacao informa que o selo nao esta mais valido

## Criterios de Aceite (Definition of Done)

- [ ] Geracao automatica de relatorio ESG com dados coletados dos modulos integrados
- [ ] Score ESG calculado com pesos configuraveis
- [ ] Template de relatorio com indicadores, graficos e analise de gaps
- [ ] Exportacao em PDF com identidade visual do tenant
- [ ] Selo de conformidade com QR code e URL de verificacao publica
- [ ] Comparativo entre periodos e entre fazendas
- [ ] Painel de gaps com sugestoes de melhoria
- [ ] Versionamento de relatorios (imutaveis apos publicacao)
- [ ] Isolamento multi-tenant validado com testes de integracao
- [ ] Permissoes RBAC aplicadas em todas as rotas

## Sugestoes de Melhoria Futura

1. **Indicadores sociais completos:** integrar dados de RH (salarios, rotatividade, treinamentos) para pilar Social
2. **Indicadores de governanca:** controles internos, politicas anticorrupcao, diversidade em cargos de gestao
3. **Benchmark setorial:** comparar score do produtor com media do setor/regiao
4. **Integracao com plataformas de certificacao:** envio automatico de dados para Bonsucro, Rainforest Alliance, etc.
5. **Marketplace de creditos:** vincular score ESG a oportunidades de premios e creditos verdes
6. **Relatorio em ingles:** versao traduzida para compradores internacionais
