# Auditoria — Produto Canônico (Step 82)

**Data:** 2026-04-28  
**Escopo:** mapeamento de entidades de produto/insumo entre módulos, identificação de inconsistências e proposta de padronização.  
**Ação neste step:** apenas auditoria e plano — nenhum dado migrado, nenhuma tabela removida.

---

## 1. Fonte da Verdade

**Tabela:** `cadastros_produtos`  
**Model:** `core/cadastros/produtos/models.py → class Produto`

### Campos principais de `Produto`

| Campo | Tipo | Observação |
|-------|------|------------|
| `id` | UUID PK | identificador canônico |
| `tenant_id` | UUID FK(tenants) | isolamento multi-tenant |
| `nome` | String(200) | |
| `tipo` | String(30) | enum `TipoProduto` |
| `unidade_medida` | String(10) | ⚠️ campo livre, não FK |
| `codigo_interno` | String(50) | único por tenant |
| `sku` / `codigo_barras` | String | opcionais |
| `marca_id` | UUID FK(cadastros_marcas) | nullable — tem fallback `marca: String` |
| `modelo_id` | UUID FK(cadastros_modelos_produto) | nullable |
| `categoria_id` | UUID FK(cadastros_categorias_produto) | nullable |
| `dados_extras` | JSON | |

### Subtipos (herança 1:1)

| Tabela | Model | Cobre |
|--------|-------|-------|
| `cadastros_produtos_agricola` | `ProdutoAgricola` | defensivos, sementes, fertilizantes |
| `cadastros_produtos_estoque` | `ProdutoEstoque` | controle físico de almoxarifado |
| `cadastros_produtos_epi` | `ProdutoEPI` | EPI (CA, validade NR-6) |
| `cadastros_culturas` | `ProdutoCultura` | culturas agrícolas |

### `TipoProduto` — enum unificado

Cobre insumos agrícolas (SEMENTE, DEFENSIVO, FERTILIZANTE, INOCULANTE, ADJUVANTE), pecuários (RACAO, MEDICAMENTO, VACINA, MINERAL), almoxarifado (PECA, LUBRIFICANTE, COMBUSTIVEL, MATERIAL_GERAL), EPI e SERVICO — **todos os módulos compartilham o mesmo enum.**

---

## 2. Mapa de Consumidores

### 2.1 Estoque (ledger + auxiliares)

| Tabela | Campo FK | ondelete | Status |
|--------|----------|----------|--------|
| `estoque_movimentos` (ledger) | `produto_id → cadastros_produtos.id` | RESTRICT | ✅ canônico |
| `estoque_saldos` | `produto_id → cadastros_produtos.id` | CASCADE | ✅ |
| `estoque_lotes` | `produto_id → cadastros_produtos.id` | CASCADE | ✅ |
| `estoque_requisicoes_itens` | `produto_id → cadastros_produtos.id` | — (sem ondelete) | ⚠️ ondelete ausente |
| `estoque_reservas` | `produto_id → cadastros_produtos.id` | CASCADE | ✅ |

### 2.2 Compras

| Tabela | Campo FK | ondelete | Status |
|--------|----------|----------|--------|
| `compras_pedidos_itens` (ItemPedidoCompra) | `produto_id → cadastros_produtos.id` | — | ⚠️ ondelete ausente |
| `compras_recebimentos_itens` (ItemRecebimentoCompra) | `produto_id → cadastros_produtos.id` | — | ⚠️ ondelete ausente |

### 2.3 Agricultura

| Tabela | Campo FK | ondelete | Status |
|--------|----------|----------|--------|
| `insumos_operacao` (InsumoOperacao) | `insumo_id → cadastros_produtos.id` | — | ⚠️ nome diverge (`insumo_id` ≠ `produto_id`) + ondelete ausente |

### 2.4 Pecuária

| Tabela | Campo FK | ondelete | Status |
|--------|----------|----------|--------|
| `pec_eventos_animal` (EventoAnimal) | `produto_id → cadastros_produtos.id` | SET NULL | ✅ (nullable, correto para evento opcional) |
| `pec_manejos_lote` (ManejoLote) | — | — | ❌ sem produto_id: vacinação/medicação em massa não vincula ao catálogo |

### 2.5 Frota

| Tabela | Campo FK | ondelete | Status |
|--------|----------|----------|--------|
| `frota_os_itens` | `produto_id → cadastros_produtos.id` | — | ⚠️ ondelete ausente |

---

## 3. Inconsistências Identificadas

### INC-01 — Nome de chave divergente em `insumos_operacao`
**Severidade:** Média

`InsumoOperacao` usa `insumo_id` para referenciar `cadastros_produtos.id`.  
Todos os demais módulos usam `produto_id`.  
Impacto: joins cruzados entre módulos exigem alias explícito; código de relatório resolve manualmente com fallback.

```python
# Atual (insumos_operacao)
insumo_id: Mapped[UUID] = mapped_column(ForeignKey("cadastros_produtos.id"))

# Padrão esperado
produto_id: Mapped[UUID] = mapped_column(ForeignKey("cadastros_produtos.id"))
```

---

### INC-02 — `InsumoOperacao.unidade` é campo livre (String)
**Severidade:** Alta

`InsumoOperacao.unidade: String(20)` é preenchido como texto livre, enquanto `OperacaoExecucao` (tabela irmã) usa `unidade_medida_id FK(unidades_medida.id)`. Essa divergência impede rastreabilidade de conversão de unidades e cálculo de custo por ha consistente.

```python
# Atual — campo livre
unidade: Mapped[str] = mapped_column(String(20), nullable=False)

# Esperado — FK canônica
unidade_medida_id: Mapped[UUID] = mapped_column(ForeignKey("unidades_medida.id", ondelete="RESTRICT"))
```

---

### INC-03 — `InsumoOperacao.lote_insumo` é campo livre (String)
**Severidade:** Baixa

`lote_insumo: String(50)` armazena o número do lote como texto, sem referência a `estoque_lotes.id`. Impede rastreabilidade direta entre consumo agrícola e o lote físico no almoxarifado.

---

### INC-04 — `Produto.unidade_medida` é campo livre (String)
**Severidade:** Média

O catálogo base `cadastros_produtos` armazena `unidade_medida: String(10)` como texto livre. O sistema possui a tabela `unidades_medida` com FK formal usada pelo ledger. Inconsistência: o cadastro de produto e o movimento usam representações diferentes da mesma informação.

---

### INC-05 — `pec_manejos_lote` sem vínculo ao catálogo de produtos
**Severidade:** Média

`ManejoLote` registra eventos em massa (vacinação, medicação) sem `produto_id`. Apenas `EventoAnimal` (individual) tem `produto_id nullable`. Manejo coletivo com medicamentos ou vacinas não tem rastreabilidade para o catálogo canônico.

---

### INC-06 — FKs sem `ondelete` em tabelas transacionais
**Severidade:** Baixa

`estoque_requisicoes_itens`, `compras_pedidos_itens`, `compras_recebimentos_itens` e `frota_os_itens` referenciam `cadastros_produtos.id` sem `ondelete` declarado. Comportamento depende do default do banco (RESTRICT no PostgreSQL), mas a intenção não está explícita no model.

---

## 4. Classificação

| Entidade | Papel | Fonte canônica? |
|----------|-------|----------------|
| `cadastros_produtos` | Catálogo mestre de insumos e produtos | ✅ Fonte da verdade |
| `cadastros_produtos_agricola` | Extensão para agrícola | ✅ Subtipo correto |
| `cadastros_produtos_estoque` | Extensão para almoxarifado | ✅ Subtipo correto |
| `cadastros_produtos_epi` | Extensão para EPI | ✅ Subtipo correto |
| `estoque_movimentos.produto_id` | Ledger de movimentação | ✅ Consumidor correto |
| `insumos_operacao.insumo_id` | Consumo agrícola | ⚠️ Correto conceitualmente, nome divergente |
| `pec_eventos_animal.produto_id` | Vacinas/medicamentos individuais | ✅ Correto |
| `pec_manejos_lote` | Manejo coletivo | ❌ Sem vínculo ao produto |
| `InsumoOperacao.unidade` | Unidade de medida do insumo | ❌ Campo livre duplicado |
| `Produto.unidade_medida` | Unidade padrão do produto | ⚠️ Campo livre no catálogo |

---

## 5. Proposta de Modelo Canônico

### 5.1 Regra geral

> Toda referência a produto/insumo no sistema DEVE usar `produto_id UUID FK(cadastros_produtos.id)`.  
> Nenhum módulo deve armazenar nome, tipo ou unidade de produto como campo de texto livre em tabelas transacionais.

### 5.2 Padronização de nome de campo

Renomear `insumos_operacao.insumo_id` → `produto_id` via migration com renomeação de coluna (sem perda de dados).

### 5.3 Unidade de medida

- Remover `InsumoOperacao.unidade` e adicionar `unidade_medida_id FK(unidades_medida.id)`
- Migrar valores string existentes para registros em `unidades_medida` (mapeamento direto por string)
- A longo prazo: converter `Produto.unidade_medida: String` → `unidade_medida_id FK`

### 5.4 Lote em `InsumoOperacao`

Adicionar `lote_id UUID nullable FK(estoque_lotes.id)` mantendo `lote_insumo: String` como fallback legado enquanto a migração não for completa.

### 5.5 Pecuária — manejo coletivo

Adicionar `produto_id UUID nullable FK(cadastros_produtos.id, SET NULL)` em `pec_manejos_lote` para os tipos de evento que consomem insumos (VACINACAO, MEDICACAO).

---

## 6. Estratégia de Migração (fases)

| Fase | Ação | Risco | Impacto |
|------|------|-------|---------|
| **F1** | Renomear `insumo_id` → `produto_id` em `insumos_operacao` + atualizar model/service/schema | Baixo | Renomeação de coluna com alias temporário |
| **F2** | Adicionar `unidade_medida_id` em `InsumoOperacao` (nullable) + migrar dados + tornar NOT NULL | Médio | Depende de mapeamento de strings existentes |
| **F3** | Adicionar `lote_id nullable` em `InsumoOperacao` | Baixo | Additive only |
| **F4** | Adicionar `produto_id nullable` em `pec_manejos_lote` | Baixo | Additive only |
| **F5** | Converter `Produto.unidade_medida: String` → FK (longo prazo) | Alto | Requer migração de todos os cadastros existentes |

---

## 7. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Renomear `insumo_id` quebra queries em relatórios e rastreabilidade | Alta | Médio | Alias SQL na migration + varredura grep antes |
| Migração de `unidade: String` para FK falha por valores não mapeados | Média | Alto | Seed de `unidades_medida` antes da migration |
| `pec_manejos_lote` com produto opcional pode gerar relatórios incompletos | Baixa | Baixo | Campo nullable não quebra existentes |
| `Produto.unidade_medida` (F5) afeta todos os cadastros existentes | Alta | Alto | Adiar para sprint dedicado com freeze de cadastros |

---

## Arquivos de referência

- `core/cadastros/produtos/models.py` — fonte da verdade
- `operacional/models/estoque.py` — ledger canônico
- `agricola/operacoes/models.py` — InsumoOperacao (INC-01, INC-02, INC-03)
- `pecuaria/models/manejo.py` — ManejoLote (INC-05)
- `docs/ESTOQUE_CANONICO_LEDGER_2026-04-28.md` — ledger canônico de estoque
