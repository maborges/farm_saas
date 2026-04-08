---
modulo: Frota e Máquinas
submodulo: Cadastro de Equipamentos
nivel: essencial
core: false
dependencias_core: [Identidade e Acesso, Cadastro da Propriedade]
dependencias_modulos: []
standalone: true
complexidade: S
assinante_alvo: [pequeno produtor, medio produtor, grande produtor]
---

# Cadastro de Equipamentos

## Descricao Funcional

Permite registrar e gerenciar todos os equipamentos da propriedade rural: maquinas agricolas (tratores, colheitadeiras, pulverizadores), veiculos (caminhoes, utilitarios, motos) e implementos (grades, plantadeiras, carretas). Cada equipamento possui ficha tecnica completa com dados de fabricante, modelo, ano, numero de serie, horimetro/odometro atual, e status operacional.

## Personas

- **Gestor de frota:** cadastra e mantem a ficha dos equipamentos, controla status
- **Operador de maquina:** consulta dados do equipamento que vai operar
- **Proprietario:** visualiza panorama geral da frota

## Dores que resolve

- Falta de controle sobre quais equipamentos a fazenda possui
- Informacoes dispersas em planilhas ou cadernos
- Dificuldade para saber status operacional (ativo, em manutencao, inativo)
- Impossibilidade de rastrear historico do equipamento

## Regras de Negocio

1. Todo equipamento deve pertencer a uma fazenda do tenant
2. Tipos validos: `MAQUINA`, `VEICULO`, `IMPLEMENTO`
3. Numero de serie/chassi deve ser unico por tenant
4. Status validos: `ATIVO`, `EM_MANUTENCAO`, `INATIVO`, `VENDIDO`
5. Horimetro/odometro so pode incrementar (nunca diminuir, exceto reset documentado)
6. Equipamento com status `VENDIDO` nao pode ser alocado a operacoes
7. Implemento pode ser vinculado a uma maquina (ex: grade puxada por trator)

## Entidades de Dados Principais

- **Equipamento:** id, tenant_id, fazenda_id, tipo, marca, modelo, ano_fabricacao, numero_serie, placa (se veiculo), horimetro_atual, odometro_atual, status, data_aquisicao, valor_aquisicao, foto_url
- **EquipamentoImplementoVinculo:** id, equipamento_maquina_id, equipamento_implemento_id, data_vinculo

## Integracoes Necessarias

- **Cadastro da Propriedade:** vincular equipamento a fazenda
- **Identidade e Acesso:** permissoes de CRUD por perfil
- **Abastecimento:** referenciar equipamento no registro de abastecimento
- **Manutencao Preventiva:** referenciar equipamento na OS

## Fluxo de Uso Principal

1. Gestor acessa modulo Frota > Equipamentos
2. Clica em "Novo Equipamento"
3. Seleciona tipo (Maquina/Veiculo/Implemento)
4. Preenche dados obrigatorios (marca, modelo, ano, serie)
5. Opcionalmente adiciona foto e dados de aquisicao
6. Salva — equipamento fica com status `ATIVO`
7. Lista exibe todos os equipamentos com filtros por tipo, status e fazenda

## Casos Extremos e Excecoes

- Tentativa de cadastrar numero de serie duplicado: retornar erro 422
- Tentativa de diminuir horimetro: bloquear e exigir justificativa de reset
- Equipamento transferido entre fazendas do mesmo tenant: manter historico
- Exclusao de equipamento com historico de abastecimento/manutencao: soft-delete obrigatorio

## Criterios de Aceite

- [ ] CRUD completo de equipamentos com validacao de campos obrigatorios
- [ ] Filtro por tipo, status e fazenda funcionando
- [ ] Numero de serie unico por tenant validado no backend
- [ ] Horimetro/odometro nao permite decremento sem justificativa
- [ ] Soft-delete para equipamentos com historico
- [ ] Isolamento por tenant validado em teste automatizado

## Sugestoes de Melhoria Futura

- QR Code para identificacao rapida do equipamento em campo
- Importacao em lote via CSV/Excel
- Galeria de fotos por equipamento (multiplas imagens)
- Historico de transferencias entre fazendas
