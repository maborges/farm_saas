---
modulo: Contabilidade
submodulo: Integração Contábil
nivel: profissional
core: false
dependencias_core:
  - Identidade e Acesso
  - Configurações Globais
dependencias_modulos:
  - ../essencial/plano-contas-rural.md
  - ../essencial/lancamentos-contabeis.md
  - ../../financeiro/essencial/despesas.md
  - ../../financeiro/essencial/receitas.md
standalone: false
complexidade: L
assinante_alvo:
  - Produtor Rural PJ
  - Contador Rural
  - Escritórios de Contabilidade
---

# Integração Contábil — Exportação para Contabilidade Externa

## Descrição Funcional

O submódulo de Integração Contábil permite exportar dados contábeis do AgroSaaS para sistemas de contabilidade externos e escritórios contábeis. Suporta múltiplos formatos de saída: layout SPED Contábil (ECD), CSV parametrizável, e formatos específicos de ERPs contábeis populares no Brasil (Domínio, Fortes, Questor, Prosoft). Também permite importação de plano de contas e lançamentos de sistemas externos para migração.

## Personas

- **Produtor Rural PJ:** Precisa enviar dados para o escritório de contabilidade externo mensalmente.
- **Contador Rural:** Importa dados do AgroSaaS no sistema contábil do escritório, evitando digitação manual.
- **Administrador do Escritório:** Configura o layout de exportação conforme o sistema contábil utilizado.

## Dores que resolve

- Digitação manual de lançamentos do sistema do produtor no sistema do contador.
- Incompatibilidade de plano de contas entre o sistema do produtor e o do escritório.
- Falta de padronização nos dados exportados, gerando retrabalho de ajuste.
- Atraso na entrega de dados contábeis ao escritório.
- Dificuldade na migração de dados de outros sistemas para o AgroSaaS.

## Regras de Negócio

1. **Formatos obrigatórios:** O sistema deve suportar no mínimo: SPED Contábil (ECD), CSV genérico e pelo menos 2 layouts de ERPs contábeis.
2. **Mapeamento de contas:** De/Para entre plano de contas interno e plano de contas do sistema destino (configurável por escritório/contador).
3. **Período de exportação:** Exportação por período (mensal, trimestral, anual) com filtro por fazenda.
4. **Validação pré-exportação:** Antes de gerar o arquivo, validar: lançamentos aprovados, contas mapeadas, período fechado.
5. **Integridade:** Arquivo exportado deve incluir hash de verificação e totalizadores para conferência.
6. **Histórico de exportações:** Manter registro de todas as exportações realizadas (data, formato, período, arquivo, usuário).
7. **De/Para de participantes:** Mapear fornecedores/clientes do AgroSaaS para códigos do sistema contábil externo.
8. **Importação:** Suportar importação de plano de contas (CSV) e lançamentos (CSV/SPED) para migração inicial.
9. **Agendamento:** Permitir exportação automática mensal via agendamento.

## Entidades de Dados Principais

- `LayoutExportacao` — definição do formato de saída: colunas, separadores, encoding, layout SPED/ERP.
- `MapeamentoContas` — De/Para entre conta interna e conta do sistema destino, por layout.
- `MapeamentoParticipantes` — De/Para entre participantes internos e códigos do sistema destino.
- `ExportacaoContabil` — registro de exportação realizada: data, período, formato, arquivo gerado, status.
- `ImportacaoContabil` — registro de importação: data, origem, arquivo, status, erros.

## Integrações Necessárias

- **Plano de Contas Rural:** Contas internas que serão mapeadas para o sistema destino.
- **Lançamentos Contábeis:** Dados dos lançamentos aprovados que serão exportados.
- **Receita Federal (SPED):** Layout oficial do SPED Contábil (ECD) — registros I050, I150, I200, I250.
- **ERPs contábeis:** Layouts específicos de Domínio Sistemas, Fortes Contábil, Questor, Prosoft.
- **Armazenamento:** Arquivos exportados armazenados no storage do tenant.

## Fluxo de Uso Principal

1. **Configuração inicial:** Selecionar o formato de exportação (SPED, CSV, ERP específico).
2. **Mapeamento:** Configurar De/Para de contas entre o plano interno e o sistema destino.
3. **Mapeamento de participantes:** Vincular fornecedores/clientes aos códigos do sistema externo (opcional).
4. **Seleção do período:** Escolher mês/ano e fazenda(s) para exportação.
5. **Validação:** Sistema verifica lançamentos aprovados, contas mapeadas e pendências.
6. **Geração:** Gerar arquivo no formato selecionado.
7. **Download/envio:** Disponibilizar arquivo para download ou enviar por e-mail ao contador.
8. **Registro:** Exportação registrada no histórico com hash de verificação.

## Casos Extremos e Exceções

- Conta contábil sem mapeamento no sistema destino — bloquear exportação ou gerar com conta genérica e alerta.
- Caracteres especiais no histórico que não são suportados pelo layout do ERP destino.
- Lançamentos em período não fechado — permitir exportação parcial com aviso.
- Mudança no layout do SPED entre exercícios fiscais — versionamento de layouts.
- Exportação de volume muito grande (>100.000 lançamentos) — geração assíncrona com notificação.
- Re-exportação de período já exportado — alerta de duplicidade e versionamento.
- Importação com contas que não existem no plano — criar automaticamente ou rejeitar com relatório.

## Critérios de Aceite

- [ ] Exportação em formato SPED Contábil (ECD) validável pelo PVA.
- [ ] Exportação em CSV com colunas configuráveis e encoding selecionável (UTF-8, ISO-8859-1).
- [ ] Mapeamento De/Para de contas funcional e reutilizável entre exportações.
- [ ] Validação pré-exportação identifica e reporta todas as pendências.
- [ ] Histórico de exportações acessível com possibilidade de re-download.
- [ ] Importação de plano de contas via CSV funcional.
- [ ] Hash de verificação gerado para cada arquivo exportado.

## Sugestões de Melhoria Futura

- API direta com sistemas contábeis (Domínio, Fortes) para envio automático sem arquivo intermediário.
- Marketplace de layouts de exportação contribuídos pela comunidade de contadores.
- Reconciliação bidirecional: confirmar que o sistema destino importou corretamente.
- Exportação incremental (apenas lançamentos novos desde a última exportação).
- Dashboard para o escritório de contabilidade com status de exportação de todos os clientes.
