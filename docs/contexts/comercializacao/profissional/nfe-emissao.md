---
modulo: Comercialização
submodulo: Emissão de NF-e
nivel: profissional
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../essencial/registro-vendas.md
  - ../essencial/clientes-compradores.md
  - ../essencial/romaneios.md
  - ./contratos-venda.md
  - ../../financeiro/essencial/receitas.md
standalone: false
complexidade: XL
assinante_alvo:
  - Médio produtor rural
  - Grande produtor rural
  - Cooperativas
---

# Emissão de NF-e

## Descrição Funcional

Emissão de Nota Fiscal Eletrônica (NF-e) do produtor rural, modelo 55, diretamente pelo sistema. Cobre NF-e de venda de produção (grãos, gado, leite), NF-e de remessa para armazém, NF-e de devolução e NF-e de transferência entre fazendas. Integra com a SEFAZ estadual via Web Service para autorização, cancelamento, carta de correção e inutilização. Preenche automaticamente dados a partir de vendas, romaneios e cadastro de compradores.

## Personas — Quem usa este submódulo

- **Produtor rural:** Emite NF-e para vendas de produção
- **Auxiliar administrativo/fiscal:** Preenche e emite NF-e, gerencia documentos fiscais
- **Contador:** Consulta NF-e emitidas, exporta XML para escrituração
- **Gerente de fazenda:** Autoriza emissão e acompanha status de notas

## Dores que resolve

- Dependência de contador ou escritório para emitir NF-e — atrasa entregas
- Erro de preenchimento manual de dados (CNPJ, NCM, CFOP) em emissores genéricos
- Retrabalho ao preencher dados que já existem no sistema (comprador, produto, peso)
- Falta de controle sobre NF-e emitidas, canceladas e pendentes
- Dificuldade de exportar XMLs para o contador/escritório contábil

## Regras de Negócio

1. Emitente deve ter certificado digital A1 ou A3 válido (e-CPF ou e-CNPJ)
2. Inscrição Estadual do produtor rural deve estar ativa
3. CFOP determinado automaticamente conforme operação e UF (5101/6101 venda interna/interestadual)
4. NCM do produto deve estar cadastrado e válido
5. Cálculo de ICMS conforme regime tributário e UF de origem/destino
6. Produtor rural pessoa física usa modelo 55 com IE de produtor
7. NF-e deve ser autorizada na SEFAZ antes de liberar a carga
8. Prazo de cancelamento: 24 horas após autorização (regra SEFAZ)
9. Carta de correção permitida após 24h para correções não-financeiras
10. Inutilização de numeração para sequências não utilizadas
11. Contingência (DPEC/FS-DA) quando SEFAZ indisponível
12. XML autorizado deve ser armazenado por 5 anos (obrigação fiscal)
13. DANFE gerado automaticamente para impressão e acompanhamento da carga

## Entidades de Dados Principais

- **NotaFiscal:** id, fazenda_id, tenant_id, venda_id, romaneio_id, serie, numero, chave_acesso, tipo_operacao (saida/entrada), cfop, natureza_operacao, destinatario_id, data_emissao, valor_total, status_sefaz (autorizada/cancelada/rejeitada/contingência), xml_autorizado_url, pdf_danfe_url, protocolo_autorizacao, created_at
- **NotaFiscalItem:** id, nota_fiscal_id, produto_id, ncm, cfop, quantidade, unidade, valor_unitario, valor_total, icms_base, icms_aliquota, icms_valor
- **NotaFiscalEvento:** id, nota_fiscal_id, tipo_evento (cancelamento/carta_correcao/inutilizacao), protocolo, data_evento, justificativa, xml_evento_url
- **CertificadoDigital:** id, tenant_id, tipo (A1/A3), validade, arquivo_pfx_encrypted, senha_encrypted, ativo

## Integrações Necessárias

- **SEFAZ estadual (externa):** autorização, cancelamento, carta de correção, inutilização via Web Service SOAP
- **Registro de Vendas (essencial):** dados da operação comercial
- **Clientes/Compradores (essencial):** dados do destinatário (CNPJ, IE, endereço)
- **Romaneios (essencial):** dados de peso e classificação
- **Receitas (financeiro):** vínculo da NF-e ao lançamento financeiro
- **Contador (exportação):** exportação de XMLs em lote

## Fluxo de Uso Principal (step-by-step)

1. Usuário acessa Comercialização > Notas Fiscais > Emitir NF-e
2. Seleciona a venda ou romaneio de referência
3. Sistema preenche automaticamente: emitente, destinatário, produtos, quantidades, valores
4. Usuário revisa e ajusta dados fiscais (CFOP, NCM, tributação)
5. Sistema valida todos os campos obrigatórios e regras fiscais
6. Usuário clica em "Emitir" — sistema envia XML para SEFAZ
7. SEFAZ retorna autorização com protocolo e chave de acesso
8. Sistema armazena XML autorizado e gera DANFE (PDF)
9. DANFE é impresso para acompanhar a carga
10. XML fica disponível para download e exportação ao contador
11. Se necessário cancelar (até 24h): Notas Fiscais > selecionar > Cancelar (com justificativa)
12. Se necessário corrigir (após 24h): Notas Fiscais > selecionar > Carta de Correção

## Casos Extremos e Exceções

- **Certificado digital expirado:** bloqueio de emissão com alerta para renovação
- **SEFAZ fora do ar:** emissão em contingência (DPEC) com transmissão posterior
- **Rejeição da SEFAZ:** exibir código e mensagem de rejeição, permitir correção e retransmissão
- **Cancelamento após 24h:** não permitido — orientar carta de correção ou NF-e de devolução
- **Destinatário com IE irregular:** SEFAZ pode rejeitar — alertar antes da emissão
- **Operação interestadual com ST:** cálculo de substituição tributária
- **Produtor sem IE ativa:** bloqueio com orientação para regularização
- **NF-e de devolução:** gera NF-e de entrada referenciando a NF-e original
- **Múltiplos produtos na mesma NF-e:** cada item com NCM e tributação próprios

## Critérios de Aceite (Definition of Done)

- [ ] Emissão de NF-e modelo 55 com autorização na SEFAZ (ambiente de homologação)
- [ ] Preenchimento automático a partir de vendas/romaneios
- [ ] Cálculo correto de ICMS conforme UF e regime tributário
- [ ] Geração de DANFE em PDF
- [ ] Armazenamento de XML autorizado
- [ ] Cancelamento de NF-e com protocolo
- [ ] Carta de correção
- [ ] Inutilização de numeração
- [ ] Exportação de XMLs em lote (ZIP)
- [ ] Gerenciamento de certificado digital (upload, validade)
- [ ] Modo contingência quando SEFAZ indisponível
- [ ] Listagem com filtros (período, status, destinatário)
- [ ] Isolamento por tenant e fazenda
- [ ] Testes com SEFAZ de homologação

## Sugestões de Melhoria Futura

- Emissão de NF-e de serviço (NFS-e) para prestadores
- Emissão de CT-e para transporte próprio
- Integração com sistemas de contabilidade (exportação SPED)
- Manifestação do destinatário (MDe) automática
- Dashboard fiscal com resumo de impostos por período
- Emissão em lote para múltiplos romaneios do mesmo dia
