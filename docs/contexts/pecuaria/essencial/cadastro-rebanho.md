---
modulo: Pecuária
submodulo: Cadastro de Rebanho
nivel: essencial
core: false
dependencias_core:
  - autenticacao
  - tenant
  - fazendas
dependencias_modulos: []
standalone: true
complexidade: M
assinante_alvo:
  - pecuarista
  - gestor-rural
  - vaqueiro
---

# Cadastro de Rebanho

## Descrição Funcional

Submódulo responsável pelo cadastro e gestão de lotes, categorias animais e identificação individual do rebanho. Permite organizar o plantel em lotes lógicos (cria, recria, engorda, matrizes), categorizar animais por finalidade e manter ficha completa de cada animal com dados de identificação (brinco visual, brinco eletrônico, número SISBOV), raça, sexo, data de nascimento e origem (nascido na fazenda ou comprado).

Suporta cadastro individual e importação em massa via CSV/planilha, facilitando a migração de fazendas que já possuem controle em planilha.

## Personas — Quem usa este submódulo

- **Pecuarista / Proprietário:** consulta do plantel total, composição por categoria
- **Gerente de Fazenda:** organização de lotes, planejamento de manejos por lote
- **Vaqueiro:** cadastro de bezerros nascidos, identificação de animais no campo
- **Escritório da fazenda:** importação de dados, manutenção cadastral

## Dores que resolve

- Controle de rebanho em cadernos ou planilhas desatualizadas
- Dificuldade em saber quantos animais existem por categoria/lote
- Perda de histórico quando animais mudam de lote
- Impossibilidade de rastrear origem de cada animal
- Retrabalho na contagem manual durante manejos

## Regras de Negócio

1. Cada animal pertence a exatamente um lote ativo por vez
2. Transferência de lote gera registro histórico com data e motivo
3. Número de brinco visual deve ser único dentro da fazenda
4. Número SISBOV, quando informado, deve ser único no sistema
5. Categorias padrão: Bezerro(a), Novilho(a), Garrote, Boi, Vaca, Touro — customizáveis por tenant
6. Animais não podem ser excluídos fisicamente; status muda para Vendido, Morto ou Transferido
7. Lote deve ter ao menos um animal para estar ativo; lotes vazios ficam como Inativo
8. Importação CSV valida duplicidades antes de inserir e gera relatório de conflitos

## Entidades de Dados Principais

- **Animal:** id, tenant_id, fazenda_id, lote_id, brinco_visual, brinco_eletronico, sisbov, raca, sexo, data_nascimento, categoria, origem, status, observacoes, created_at, updated_at
- **Lote:** id, tenant_id, fazenda_id, nome, categoria, finalidade, status, created_at
- **CategoriaAnimal:** id, tenant_id, nome, descricao, faixa_etaria_meses_min, faixa_etaria_meses_max
- **HistoricoLote:** id, animal_id, lote_origem_id, lote_destino_id, data, motivo

## Integrações Necessárias

- **Core/Fazendas:** Animal sempre vinculado a uma fazenda do tenant
- **Manejos Básicos:** Animais cadastrados são alvo de pesagens, vacinações
- **Piquetes:** Lotes são alocados em piquetes
- **Estoque (opcional):** Baixa de brincos/identificadores do estoque

## Fluxo de Uso Principal (step-by-step)

1. Acessar módulo Pecuária > Rebanho
2. Criar categorias customizadas (ou usar as padrão)
3. Criar lotes com nome e finalidade (ex.: "Lote Recria 2026")
4. Cadastrar animais individualmente ou via importação CSV
5. Associar cada animal a um lote
6. Visualizar dashboard com totais por categoria, lote e status
7. Filtrar e buscar animais por brinco, raça, categoria ou lote
8. Transferir animais entre lotes quando necessário

## Casos Extremos e Exceções

- **Animal sem brinco:** Permitir cadastro com identificação provisória (ex.: "S/B-001"), marcar como pendente
- **Importação com brinco duplicado:** Rejeitar linha e incluir no relatório de erros, sem abortar importação inteira
- **Lote com 0 animais:** Marcar como Inativo automaticamente; reativar ao receber animal
- **Animal nascido de matriz não cadastrada:** Permitir cadastro com campo "mãe" vazio; alerta para completar
- **Mudança de categoria por idade:** Sugestão automática com base na data de nascimento, mas não automática (requer confirmação)
- **Raça não cadastrada:** Permitir texto livre; sugerir padronização via dropdown

## Critérios de Aceite (Definition of Done)

- [ ] CRUD completo de Animal com isolamento por tenant_id
- [ ] CRUD de Lote com validação de fazenda_id
- [ ] Importação CSV com validação e relatório de erros
- [ ] Histórico de transferências entre lotes
- [ ] Filtros por categoria, lote, raça, status
- [ ] Dashboard com contagem por categoria e lote
- [ ] Testes unitários e de integração para serviço e rotas
- [ ] Teste de isolamento multi-tenant

## Sugestões de Melhoria Futura

- Leitura de brinco eletrônico via NFC/RFID no app mobile
- Foto do animal vinculada ao cadastro
- QR Code no brinco visual para consulta rápida
- Reconhecimento facial bovino para identificação sem brinco
- Importação direta de planilhas do Ideagri/PecSoft
