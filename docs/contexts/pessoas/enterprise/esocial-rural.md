---
modulo: Pessoas e RH
submodulo: eSocial Rural
nivel: enterprise
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ../essencial/cadastro-colaboradores.md
  - ../essencial/controle-presenca.md
  - ../essencial/epi-seguranca.md
  - ../profissional/folha-simplificada.md
  - ../profissional/treinamentos.md
standalone: false
complexidade: XL
assinante_alvo:
  - Grande produtor rural
  - Cooperativas
  - Agroindústrias
---

# eSocial Rural

## Descrição Funcional

Integração completa com o eSocial para empregadores rurais (pessoa física e jurídica). Gera e transmite os eventos obrigatórios do eSocial: tabelas (S-1000 a S-1080), eventos não periódicos (S-2190 a S-2420) e eventos periódicos (S-1200 a S-1299). Contempla as particularidades do empregador rural: CAEPF (Cadastro de Atividade Econômica de Pessoa Física), FUNRURAL, contribuição sobre comercialização, safristas e trabalhadores rurais temporários. Automatiza a geração de XML conforme leiautes do governo.

## Personas — Quem usa este submódulo

- **Contador/DP:** Gera e transmite eventos do eSocial, corrige inconsistências
- **RH:** Mantém dados cadastrais atualizados para conformidade
- **Produtor rural (empregador):** Acompanha status de conformidade
- **Consultor trabalhista:** Audita eventos e identifica pendências

## Dores que resolve

- Multas por atraso ou não envio de eventos obrigatórios do eSocial
- Complexidade dos leiautes e regras de validação do eSocial
- Retrabalho ao preencher dados que já existem no sistema (admissão, remuneração)
- Divergências entre dados do sistema e dados enviados ao governo
- Particularidades do empregador rural pouco suportadas por sistemas genéricos de DP

## Regras de Negócio

1. Empregador rural pessoa física usa CAEPF como identificador (não CNPJ)
2. Eventos de tabela devem ser enviados antes dos demais (hierarquia de dependência)
3. S-2200 (Admissão): obrigatório antes do início do trabalho
4. S-2190 (Admissão preliminar): permitido até 1 dia antes da admissão
5. S-1200 (Remuneração): envio mensal até dia 15 do mês seguinte
6. S-2210 (CAT): até 1 dia útil após acidente (fatal = imediato)
7. S-2220 (Monitoramento de saúde): ASO admissional, periódico, demissional
8. S-2245 (Treinamentos): capacitações obrigatórias por NR
9. S-2299 (Desligamento): até 10 dias após término do contrato
10. Safrista/temporário: S-2200 com tipo de contrato específico, S-2299 no fim da safra
11. FUNRURAL: contribuição sobre receita bruta da comercialização (empregador rural PF)
12. Eventos devem seguir leiaute vigente (versão S-1.2 ou posterior)
13. Retificação de evento: enviar evento com indicativo de retificação referenciando recibo original

## Entidades de Dados Principais

- **EventoeSocial:** id, tenant_id, fazenda_id, tipo_evento (S-1000/S-2200/S-1200/etc.), colaborador_id (quando aplicável), periodo_referencia, xml_gerado, xml_retorno, protocolo_envio, recibo, status (pendente/enviado/aceito/rejeitado/retificado), erro_descricao, tentativas, created_at, updated_at
- **LoteeSocial:** id, tenant_id, tipo_lote (tabelas/nao_periodicos/periodicos), eventos_ids, data_envio, protocolo_lote, status
- **ConfiguracaoeSocial:** id, tenant_id, caepf, certificado_digital_id, ambiente (producao/producao_restrita), versao_leiaute, procuracao_eletronica

## Integrações Necessárias

- **Portal eSocial/Governo Federal (externa):** transmissão de eventos via Web Service SOAP/REST
- **Certificado Digital (A1/A3):** assinatura dos eventos XML
- **Cadastro de Colaboradores (essencial):** dados de admissão, alteração, desligamento
- **Controle de Presença (essencial):** dados de jornada
- **EPI/Segurança (essencial):** CAT (S-2210), monitoramento de saúde (S-2220)
- **Folha Simplificada (profissional):** remuneração mensal (S-1200)
- **Treinamentos (profissional):** capacitações (S-2245)

## Fluxo de Uso Principal (step-by-step)

1. Configuração inicial: cadastrar CAEPF, certificado digital e ambiente (produção restrita para testes)
2. Enviar eventos de tabela (S-1000 Empregador, S-1005 Estabelecimentos, etc.)
3. No dia a dia, ações no sistema geram eventos automaticamente:
   - Admissão de colaborador -> S-2200
   - Alteração cadastral -> S-2205
   - Acidente de trabalho -> S-2210
   - ASO realizado -> S-2220
4. Mensalmente, ao processar folha -> S-1200 (Remuneração) + S-1299 (Fechamento)
5. Usuário acessa Pessoas > eSocial > Painel de Eventos
6. Painel exibe eventos pendentes, enviados, aceitos e rejeitados
7. Para eventos rejeitados, exibe erro e permite correção e retransmissão
8. Eventos aceitos exibem recibo de entrega
9. Relatório de conformidade mostra eventos obrigatórios pendentes

## Casos Extremos e Exceções

- **Evento rejeitado por inconsistência:** detalhar erro, permitir correção e retransmissão
- **Certificado digital vencido:** bloquear envio e alertar para renovação
- **eSocial fora do ar:** enfileirar eventos e enviar quando disponível (retry automático)
- **Admissão retroativa:** evento S-2200 com data anterior — pode gerar multa mas deve ser enviado
- **Trabalhador sem CPF válido na base do governo:** rejeição — orientar regularização
- **Mudança de leiaute:** atualização da versão do XML — deve ser transparente para o usuário
- **Procuração eletrônica:** contador envia eventos em nome do produtor
- **Empregador com múltiplos CAEPFs:** cada fazenda pode ter CAEPF diferente

## Critérios de Aceite (Definition of Done)

- [ ] Geração automática de eventos a partir de ações no sistema (admissão, folha, etc.)
- [ ] Transmissão de eventos via Web Service com certificado digital
- [ ] Painel de status de eventos (pendente/enviado/aceito/rejeitado)
- [ ] Tratamento de erros de rejeição com orientação de correção
- [ ] Retificação de eventos com referência ao recibo original
- [ ] Suporte a CAEPF (empregador rural pessoa física)
- [ ] Configuração de ambiente (produção restrita para testes)
- [ ] Relatório de conformidade com eventos obrigatórios pendentes
- [ ] Retry automático para falhas de comunicação
- [ ] Isolamento por tenant
- [ ] Testes com ambiente de produção restrita do eSocial

## Sugestões de Melhoria Futura

- Dashboard de conformidade com semáforo por tipo de evento
- Geração automática de DCTFWEB a partir dos eventos do eSocial
- Integração com FGTS Digital para recolhimento
- Auditoria pré-envio (validação de regras do eSocial antes da transmissão)
- Agendamento automático de envio de eventos periódicos
- Relatório de pendências para o contador com exportação
