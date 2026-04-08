---
modulo: Contabilidade
submodulo: LCDPR
nivel: essencial
core: false
dependencias_core:
  - Identidade e Acesso
  - Configurações Globais
dependencias_modulos:
  - ../../financeiro/essencial/despesas.md
  - ../../financeiro/essencial/receitas.md
standalone: false
complexidade: M
assinante_alvo:
  - Produtor Rural PF com receita bruta > R$ 56.000/ano
  - Contador Rural
---

# LCDPR — Livro Caixa Digital do Produtor Rural

## Descrição Funcional

O LCDPR (Livro Caixa Digital do Produtor Rural) é uma obrigação acessória da Receita Federal para pessoas físicas que exerçam atividade rural e tenham receita bruta anual superior a R$ 56.000. Este submódulo automatiza a escrituração do livro caixa digital, importando lançamentos do módulo financeiro e formatando-os conforme o layout oficial da RFB. Permite geração do arquivo para importação no programa da Receita Federal, eliminando escrituração manual e reduzindo erros.

## Personas

- **Produtor Rural PF:** Precisa entregar o LCDPR anualmente e deseja que os dados financeiros já registrados no sistema alimentem automaticamente o livro.
- **Contador Rural:** Necessita revisar, ajustar e validar os dados antes da transmissão à Receita Federal.
- **Administrador da Fazenda:** Acompanha a escrituração para garantir que todas as receitas e despesas estejam classificadas corretamente.

## Dores que resolve

- Escrituração manual do LCDPR em planilhas ou no programa da RFB, sujeita a erros e retrabalho.
- Dificuldade em classificar receitas e despesas conforme as categorias exigidas pela Receita Federal.
- Risco de multa por entrega fora do prazo ou com inconsistências.
- Falta de rastreabilidade entre o lançamento financeiro operacional e o registro no LCDPR.
- Necessidade de reprocessar dados quando há retificação.

## Regras de Negócio

1. **Obrigatoriedade:** Somente produtores PF com receita bruta anual > R$ 56.000 são obrigados. O sistema deve alertar quando o limite for atingido.
2. **Regime de Caixa:** O LCDPR segue estritamente o regime de caixa — somente pagamentos e recebimentos efetivos são registrados.
3. **Classificação obrigatória:** Todo lançamento deve ter: tipo (receita/despesa), histórico, participante (CPF/CNPJ), imóvel rural vinculado e código de conta LCDPR.
4. **Imóvel Rural:** Cada lançamento deve estar vinculado a pelo menos um imóvel rural cadastrado (NIRF/CAEPF).
5. **Participantes:** CPF/CNPJ de todos os participantes (clientes, fornecedores, bancos) devem estar cadastrados e válidos.
6. **Saldo inicial:** O saldo inicial do exercício deve ser informado e deve corresponder ao saldo final do exercício anterior.
7. **Retificação:** O sistema deve permitir gerar LCDPR retificador, mantendo histórico de versões.
8. **Prazo:** Entrega até o último dia útil de maio do exercício seguinte (sincronizar com IRPF).

## Entidades de Dados Principais

- `LivroLCDPR` — cabeçalho do livro por exercício fiscal e CPF do produtor.
- `LancamentoLCDPR` — registro individual com data, tipo, valor, histórico, conta LCDPR, participante e imóvel.
- `ImovelRural` — cadastro do imóvel com NIRF, CAEPF, endereço e área.
- `ParticipanteLCDPR` — cadastro de participantes (CPF/CNPJ) referenciados nos lançamentos.
- `ContaLCDPR` — tabela de contas conforme layout da RFB (receitas da atividade rural, despesas de custeio, investimentos, etc.).

## Integrações Necessárias

- **Financeiro (Despesas/Receitas):** Importação automática de lançamentos pagos/recebidos, com mapeamento para contas LCDPR.
- **Cadastro de Fazendas:** Vínculo do imóvel rural (NIRF) com a fazenda cadastrada no sistema.
- **Cadastro de Fornecedores/Clientes:** Dados de participantes para preenchimento automático.
- **Receita Federal:** Conformidade com layout oficial do arquivo LCDPR (versão vigente).
- **IRPF Rural (Enterprise):** Dados do LCDPR alimentam a apuração do IRPF atividade rural.

## Fluxo de Uso Principal

1. **Configuração inicial:** Cadastrar imóveis rurais (NIRF/CAEPF) e informar saldo inicial do exercício.
2. **Importação de lançamentos:** Sistema importa automaticamente receitas e despesas pagas do módulo financeiro, classificando-as nas contas LCDPR.
3. **Revisão:** Usuário ou contador revisa lançamentos importados, ajusta classificações e corrige inconsistências.
4. **Validação:** Sistema executa validações (saldo, participantes, imóveis, campos obrigatórios) e apresenta relatório de pendências.
5. **Geração do arquivo:** Gerar arquivo no formato oficial da RFB para importação no programa LCDPR.
6. **Entrega:** Contador importa o arquivo no programa da Receita Federal e transmite.
7. **Arquivamento:** Sistema armazena cópia do arquivo gerado e recibo de entrega.

## Casos Extremos e Exceções

- Produtor com múltiplos imóveis rurais e necessidade de rateio de despesas entre eles.
- Lançamentos de exercícios anteriores descobertos após fechamento (exige retificação).
- Receita bruta que ultrapassa o limite de obrigatoriedade no meio do exercício.
- Despesas compartilhadas entre atividade rural e não-rural (ex.: veículo de uso misto).
- Participante sem CPF/CNPJ válido (ex.: trabalhador informal — deve ser regularizado).
- Imóvel rural arrendado parcialmente — rateio proporcional à área utilizada.
- Mudança de titularidade do imóvel durante o exercício (espólio, doação).

## Critérios de Aceite

- [ ] Lançamentos financeiros pagos/recebidos são importados automaticamente para o LCDPR com classificação sugerida.
- [ ] Imóveis rurais cadastrados com NIRF e vinculados às fazendas do sistema.
- [ ] Validação completa antes da geração do arquivo (participantes, imóveis, saldos, campos obrigatórios).
- [ ] Arquivo gerado no formato oficial da RFB, importável no programa LCDPR sem erros.
- [ ] Saldo final do exercício confere com a soma de saldo inicial + receitas - despesas.
- [ ] Histórico de versões mantido para LCDPR retificador.
- [ ] Relatório de conferência disponível antes da entrega.

## Sugestões de Melhoria Futura

- Integração direta com e-CAC para envio do LCDPR sem necessidade do programa da RFB.
- Classificação automática de lançamentos via IA baseada no histórico do produtor.
- Alerta automático quando receita bruta se aproxima do limite de obrigatoriedade.
- Conciliação automática entre LCDPR e extrato bancário.
- Painel de acompanhamento do prazo de entrega com notificações push/email.
