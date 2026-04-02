---
modulo: Comercialização
submodulo: Romaneios
nivel: essencial
core: false
dependencias_core:
  - auth
  - billing
  - fazendas
dependencias_modulos:
  - ./registro-vendas.md
  - ./clientes-compradores.md
  - ../../operacional/essencial/estoque.md
standalone: false
complexidade: M
assinante_alvo:
  - Pequeno produtor rural
  - Médio produtor rural
  - Cooperativas
---

# Romaneios

## Descrição Funcional

Gestão de romaneios de entrega e pesagem da produção. O romaneio é o documento que registra cada carga entregue ao comprador, incluindo dados de pesagem (peso bruto, tara, peso líquido), classificação do produto (umidade, impurezas, avariados), descontos por qualidade, placa do veículo, motorista e local de entrega. É essencial para controle de entregas parciais e conciliação com o comprador.

## Personas — Quem usa este submódulo

- **Produtor rural:** Acompanha entregas realizadas e saldo pendente de cada venda
- **Gerente de fazenda:** Monitora logística de entregas, verifica descontos aplicados
- **Balanceiro/Conferente:** Registra pesagens e classificação no momento da entrega
- **Financeiro:** Concilia romaneios com notas fiscais e pagamentos
- **Motorista/Transportador:** Recebe comprovante do romaneio

## Dores que resolve

- Perda de controle sobre entregas parciais — não sabe quanto já entregou de cada venda
- Divergências de pesagem entre fazenda e comprador sem documentação
- Descontos de classificação aplicados sem registro (umidade, impurezas)
- Falta de rastreabilidade da carga (qual veículo, qual motorista, qual data)
- Dificuldade de conciliar entregas com pagamentos

## Regras de Negócio

1. Romaneio deve estar vinculado a uma venda (ou contrato no tier profissional)
2. Peso líquido = Peso bruto - Tara
3. Descontos de classificação são calculados sobre o peso líquido conforme tabela do produto
4. Umidade acima do padrão gera desconto proporcional (ex: soja padrão 14%, cada ponto acima desconta)
5. Impurezas acima do padrão geram desconto proporcional
6. Peso líquido com descontos não pode exceder o saldo pendente da venda
7. Romaneio confirmado atualiza o saldo entregue da venda automaticamente
8. Romaneio confirmado efetua baixa no estoque (se integrado)
9. Placa do veículo deve seguir formato válido (AAA-0000 ou AAA0A00)
10. Romaneio pode ser impresso como comprovante de entrega
11. Cancelamento de romaneio confirmado exige justificativa e estorna saldo e estoque

## Entidades de Dados Principais

- **Romaneio:** id, fazenda_id, tenant_id, venda_id, numero_romaneio (sequencial), data_entrega, produto_id, placa_veiculo, motorista_nome, motorista_cpf, local_entrega, peso_bruto_kg, tara_kg, peso_liquido_kg, umidade_percentual, impurezas_percentual, avariados_percentual, desconto_umidade_kg, desconto_impurezas_kg, peso_liquido_final_kg, status, observacoes, created_at, updated_at
- **RomaneioClassificacao:** id, romaneio_id, parametro, valor_medido, valor_padrao, desconto_aplicado

## Integrações Necessárias

- **Registro de Vendas (essencial):** romaneio está vinculado a uma venda para controle de saldo
- **Clientes/Compradores (essencial):** identificação do destinatário
- **Estoque (operacional):** baixa automática de estoque na confirmação
- **NF-e (profissional):** dados do romaneio alimentam a nota fiscal
- **Contratos de Venda (profissional):** romaneio pode referenciar um contrato

## Fluxo de Uso Principal (step-by-step)

1. Caminhão chega na fazenda ou no armazém para carregar
2. Usuário acessa Comercialização > Romaneios > Novo Romaneio
3. Seleciona a venda (ou contrato) de referência
4. Informa placa do veículo e dados do motorista
5. Registra peso bruto (balança de entrada)
6. Após carregamento, registra tara (balança de saída) — sistema calcula peso líquido
7. Registra dados de classificação (umidade, impurezas, avariados)
8. Sistema calcula descontos automáticos conforme tabela do produto
9. Sistema exibe peso líquido final (após descontos)
10. Confirma o romaneio — sistema atualiza saldo da venda e baixa estoque
11. Imprime comprovante para o motorista
12. Romaneio aparece no histórico de entregas da venda

## Casos Extremos e Exceções

- **Balança indisponível:** permite registro manual com flag "pesagem estimada"
- **Umidade muito alta (>20%):** produto pode ser recusado ou exigir secagem prévia
- **Divergência de pesagem no destino:** campo para registrar peso no destino e calcular quebra de transporte
- **Entrega sem venda prévia:** permite criar romaneio avulso que depois é vinculado a uma venda
- **Múltiplos produtos no mesmo caminhão:** romaneio por produto, mesmo veículo
- **Cancelamento após faturamento:** romaneio vinculado a NF-e emitida exige cancelamento da NF-e primeiro
- **Carga devolvida:** romaneio de devolução com quantidade negativa

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de romaneios com cálculos automáticos de peso e descontos
- [ ] Numeração sequencial automática por fazenda
- [ ] Cálculo correto de descontos por umidade e impurezas
- [ ] Atualização automática do saldo da venda na confirmação
- [ ] Baixa automática de estoque (quando módulo operacional contratado)
- [ ] Validação de saldo disponível na venda
- [ ] Impressão de comprovante de romaneio
- [ ] Filtros por venda, comprador, período, produto e status
- [ ] Cancelamento com justificativa e estorno
- [ ] Isolamento por tenant e fazenda
- [ ] Testes de integração para fluxo completo

## Sugestões de Melhoria Futura

- Integração com balança digital via IoT para captura automática de peso
- Foto da carga anexada ao romaneio (câmera do celular)
- QR Code no comprovante para conferência digital
- Tabela de classificação configurável por produto e por comprador
- Relatório de quebra de transporte (peso origem vs. destino)
- Alerta quando entrega se aproxima do limite da venda
