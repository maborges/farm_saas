---
modulo: Frota e Máquinas
submodulo: Documentação
nivel: profissional
core: false
dependencias_core: [Identidade e Acesso, Cadastro da Propriedade]
dependencias_modulos: [../essencial/cadastro-equipamentos.md]
standalone: true
complexidade: S
assinante_alvo: [medio produtor, grande produtor]
---

# Documentacao

## Descricao Funcional

Controle de documentos obrigatorios dos veiculos e maquinas da frota: IPVA, licenciamento (CRLV), seguro obrigatorio (DPVAT), seguro facultativo, vistorias e demais certidoes. O sistema alerta sobre vencimentos proximos e bloqueia a operacao de veiculos com documentacao vencida.

## Personas

- **Gestor de frota:** cadastra documentos, monitora vencimentos
- **Administrativo/Financeiro:** programa pagamentos de IPVA e seguros
- **Proprietario:** garante conformidade legal da frota

## Dores que resolve

- Veiculos operando com documentacao vencida (risco de multas e apreensao)
- Esquecimento de datas de vencimento de seguros e licenciamentos
- Documentos fisicos extraviados sem copia digital
- Falta de visao consolidada do custo documental da frota

## Regras de Negocio

1. Tipos de documento: `IPVA`, `LICENCIAMENTO`, `SEGURO_OBRIGATORIO`, `SEGURO_FACULTATIVO`, `VISTORIA`, `OUTRO`
2. Cada documento tem data de emissao e data de vencimento
3. Alertas automaticos: 60, 30 e 7 dias antes do vencimento
4. Veiculos com licenciamento ou seguro obrigatorio vencido ficam bloqueados para operacao
5. Maquinas agricolas que nao circulam em vias publicas: licenciamento nao obrigatorio (configuravel)
6. Upload de arquivo digital do documento obrigatorio (PDF ou imagem)
7. Valor pago registrado para cada documento (compoe custo da frota)

## Entidades de Dados Principais

- **DocumentoEquipamento:** id, tenant_id, equipamento_id, tipo, descricao, data_emissao, data_vencimento, valor_pago, arquivo_url, status (VIGENTE/VENCIDO/PENDENTE), observacao

## Integracoes Necessarias

- **Cadastro de Equipamentos:** referenciar equipamento, bloquear operacao se vencido
- **Financeiro:** lancamento de despesa de documentacao
- **Custo/Hora Maquina:** seguro anual compoe custo operacional
- **Notificacoes:** alertas de vencimento por email/push

## Fluxo de Uso Principal

1. Gestor acessa Frota > Documentacao
2. Seleciona equipamento e clica "Novo Documento"
3. Seleciona tipo, informa datas e valor pago
4. Faz upload do arquivo digitalizado
5. Sistema agenda alertas de vencimento
6. Dashboard exibe documentos proximos do vencimento em destaque
7. Ao vencer, status muda automaticamente para VENCIDO e equipamento e bloqueado (se aplicavel)

## Casos Extremos e Excecoes

- Documento sem data de vencimento (ex: nota fiscal de compra): permitir sem vencimento
- Renovacao de documento: criar novo registro, manter historico do anterior
- Veiculo vendido com documentos vigentes: manter registros historicos vinculados
- Multa de transito: registrar como documento tipo OUTRO com valor e descricao
- Equipamento importado com documentacao internacional: campo de observacao livre

## Criterios de Aceite

- [ ] CRUD de documentos com upload de arquivo
- [ ] Alertas automaticos em 60, 30 e 7 dias antes do vencimento
- [ ] Mudanca automatica de status para VENCIDO na data
- [ ] Bloqueio de operacao para veiculos com documentos obrigatorios vencidos
- [ ] Dashboard com visao consolidada de vencimentos
- [ ] Historico de documentos por equipamento
- [ ] Isolamento por tenant

## Sugestoes de Melhoria Futura

- Integracao com DETRAN para consulta automatica de situacao do veiculo
- Renovacao automatica com pre-preenchimento de dados
- Relatorio anual de custos documentais por equipamento
- Integracao com seguradoras para cotacao online
