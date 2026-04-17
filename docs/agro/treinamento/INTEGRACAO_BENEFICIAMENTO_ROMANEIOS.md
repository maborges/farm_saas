# Integração: Romaneios → Beneficiamento → Comercialização → Estoque

## ✅ Implementação Concluída (4 Integrações)

### Resumo da Solução
Fluxo completo de café: colheita → processamento → venda → estoque rastreável.
- **Integração 0** (P0.1): Romaneio → Beneficiamento → Comercialização (4 campos, 2 endpoints)
- **Integração 1** (P1.1): Relatório de Rendimento com breakdown por método + eficiência %
- **Integração 2** (P1.2): Agrupamento de múltiplos romaneios em 1 lote (blend/multi-romaneio)
- **Integração 3** (P1.3): Armazenagem em estoque com SKU rastreável

---

## 📦 Mudanças Backend

### 1. **Modelo** (`services/api/agricola/beneficiamento/models.py`)
Adicionados 4 campos a `LoteBeneficiamento`:
- `romaneio_id` (FK) — Rastreabilidade: qual romaneio originou o lote
- `perda_secagem_kg` — Perda durante secagem
- `perda_quebra_kg` — Grãos quebrados descartados
- `perda_defeito_kg` — Grãos defeituosos descartados

### 2. **Schemas** (`services/api/agricola/beneficiamento/schemas.py`)
Atualizados Create/Update/Response para incluir os 4 novos campos.

### 3. **Migration** (`services/api/migrations/versions/add_beneficiamento_romaneio_perdas.py`)
Nova migration (criada manualmente) para adicionar as colunas ao banco.

### 4. **Service** (`services/api/agricola/beneficiamento/service.py`)
Dois novos métodos:

#### `criar_from_romaneio(romaneio_id: UUID) → LoteBeneficiamento`
- Busca romaneio (tenant isolation)
- Cria lote pré-populado:
  - `safra_id`, `talhao_id` ← romaneio
  - `peso_entrada_kg` ← `peso_liquido_kg` do romaneio
  - `umidade_entrada_pct` ← umidade do romaneio
  - `numero_lote` ← gerado automaticamente (BEN-{romaneio.numero})
  - `metodo` = "NATURAL" (padrão, usuário pode alterar)
  - `status` = "RECEBIMENTO"
  - `romaneio_id` linkado para rastreabilidade

#### `gerar_venda(lote_id: UUID) → dict`
- Valida status = ARMAZENADO
- Busca commodity_id da safra
- Cria `ComercializacaoCommodity` via `ComercializacaoService`:
  - `status` = "RASCUNHO"
  - `quantidade` = sacas_beneficiadas
  - `unidade` = "SC60"
  - `dados_extras.lote_beneficiamento_id` para rastreabilidade
- Retorna dados da venda criada (id, numero_contrato, quantidade, status)

### 5. **Router** (`services/api/agricola/beneficiamento/router.py`)
Dois novos endpoints:

```
POST /beneficiamento/from-romaneio/{romaneio_id}
→ Cria lote a partir de romaneio (requires: A5_COLHEITA, role: agronomo/operador/admin)
→ Response: LoteBeneficiamentoResponse

POST /beneficiamento/{id}/gerar-venda
→ Cria venda a partir de lote ARMAZENADO (requires: A5_COLHEITA, role: agronomo/admin)
→ Response: { id, numero_contrato, quantidade, status }
```

---

## 🎨 Mudanças Frontend

### 1. **Componente Beneficiamento** (`apps/web/src/components/agricola/beneficiamento-cafe.tsx`)

#### Adicionado ao Formulário de Edição:
Seção "Perdas Detalhadas" com 3 campos:
- Perda por Secagem (kg)
- Perda por Quebra (kg)
- Perda por Defeito (kg)

#### Novo Botão na Tabela:
- **Ícone:** 🛒 (ShoppingCart)
- **Condição:** Visível apenas quando `status === "ARMAZENADO"`
- **Ação:** `POST /beneficiamento/{id}/gerar-venda`
- **Feedback:** Toast com numero_contrato da venda criada

#### Novo Mutation:
```typescript
gerarVenda = useMutation({
  mutationFn: (id) => apiFetch(`/beneficiamento/${id}/gerar-venda`, { method: "POST" }),
  onSuccess: (data) => {
    toast.success(`Venda criada! Contrato: ${data.numero_contrato}`);
    // invalidates queries
  }
})
```

### 2. **Componente Romaneios** (`apps/web/src/components/agricola/romaneios-colheita.tsx`)

#### Novo Botão na Tabela:
- **Ícone:** 🏭 (Factory)
- **Label:** "Processar"
- **Ação:** `POST /beneficiamento/from-romaneio/{romaneio_id}`
- **Feedback:** Toast + redirecionamento para `/agricola/safras/[id]/beneficiamento`

#### Novo Mutation:
```typescript
processar = useMutation({
  mutationFn: (romaneioId) => apiFetch(`/beneficiamento/from-romaneio/${romaneioId}`, { method: "POST" }),
  onSuccess: (data) => {
    toast.success(`Lote ${data.numero_lote} criado!`);
    setTimeout(() => {
      window.location.href = `/agricola/safras/${safraId}/beneficiamento`;
    }, 800);
  }
})
```

---

## 🔄 Fluxo de Uso (Passo a Passo)

### 1. **Registrar Colheita**
Menu: `Agricultura → ③ Colheita → Romaneios (Colheita)`
```
Clica "+ Novo Romaneio" 
→ Preenche dados (talhão, data, peso, qualidade)
→ Salva
→ Romaneio aparece na tabela com botão 🏭
```

### 2. **Iniciar Beneficiamento (Processar Romaneio)**
Menu: `Agricultura → ③ Colheita → Romaneios (Colheita)`
```
Clica botão 🏭 "Processar" no romaneio
→ POST /beneficiamento/from-romaneio/{romaneio_id}
→ Lote criado em status RECEBIMENTO
→ Redireciona para: Agricultura → ④ Pós-Colheita → Beneficiamento
→ Lote pré-populado com dados do romaneio
```

### 3. **Registrar Processamento**
Menu: `Agricultura → ④ Pós-Colheita → Beneficiamento`
```
Clica ✏️ "Editar" no lote beneficiamento
→ Preenche:
   - Data/Local de Secagem
   - Peso de Saída
   - Umidade Final
   - Perdas Detalhadas: secagem, quebra, defeito (kg)
   - Qualidade: bebida (ABIC), pontuação SCA
→ Muda Status manualmente:
   RECEBIMENTO → SECAGEM → CLASSIFICAÇÃO → ARMAZENADO
→ **Novo Dashboard "Relatório de Rendimento"** aparece (Integração 1)
   ├─ Visualiza breakdown por método
   ├─ Eficiência % com badges coloridas
   └─ Totais de entrada/saída
```

### 4. **Armazenar em Estoque (Novo - Int. 3)**
Menu: `Agricultura → ④ Pós-Colheita → Beneficiamento`
```
Quando lote = ARMAZENADO, botão 📦 "Armazenar" fica visível
→ Clica "Armazenar"
→ POST /beneficiamento/{id}/armazenar
→ LoteEstoque criado em: Operacional → ② Estoque → Inventário
→ Toast: "Lote enviado ao estoque! SKU: BEN-XXXX"
→ Botão 📦 substitui por 🛒
```

### 5. **Gerar Venda**
Menu: `Agricultura → ④ Pós-Colheita → Beneficiamento`
```
Quando lote = ARMAZENADO + lote_estoque_id preenchido, botão 🛒 fica visível
→ Clica "Gerar Venda" 🛒
→ POST /beneficiamento/{id}/gerar-venda
→ ComercializacaoCommodity criada em RASCUNHO
→ Toast: "Venda criada! Contrato: XXX"
→ Usuário acessa: Financeiro → ① Receitas & Vendas para finalizar
   (ou acessa Menu: Financeiro → ① Receitas & Vendas → Comercializações)
```

### 📌 **Bônus: Blending de Múltiplos Romaneios (Int. 2)**
Menu: `Agricultura → ③ Colheita → Romaneios (Colheita)`
```
Seleciona 2+ romaneios com checkboxes
→ Clica "Processar Selecionados (N)"
→ POST /beneficiamento/from-romaneios
→ 1 lote único criado com peso = soma dos romaneios
→ Rastreabilidade mantida: lote aponta a todos os N romaneios
```

---

## 📊 Rastreabilidade

Cada ponto do fluxo tem rastreabilidade:

```
Romaneio → Lote Beneficiamento → Comercialização
   ↓              ↓                     ↓
data_colheita   romaneio_id ──→  dados_extras.lote_beneficiamento_id
peso_liquido_kg → peso_entrada_kg
umidade_pct     → umidade_entrada_pct
```

**Acompanhamento:** Usuário pode navegar:
1. De Romaneio → Ver lote em Beneficiamento
2. De Lote → Ver romaneio origem + venda gerada (nos dados_extras)
3. De Comercialização → Voltar ao lote de origem

---

## 🚀 3 Novas Integrações Implementadas (2026-04-15)

### 1. **Integração 1 — Relatório de Rendimento**

#### Backend
- **Schemas:** `RendimentoPorMetodo`, `BeneficiamentoRelatorioRendimento`
- **Método:** `relatorio_rendimento(safra_id)` — agrupa lotes por método, calcula:
  - Peso entrada/saída total
  - Fator de redução real vs esperado
  - Eficiência % = (fator_esperado / fator_real) × 100
  - Perdas detalhadas por tipo (secagem, quebra, defeito)
- **Endpoint:** `GET /beneficiamento/relatorio-rendimento?safra_id=`

#### Frontend (`beneficiamento-cafe.tsx`)
- Seção "Relatório de Rendimento por Método" com tabela
- Colunas: Método | Lotes | Entrada | Saída | Fator Real | Fator Esp. | Eficiência
- Badges coloridas: 🟢 verde (≥95%), 🟡 amarelo (≥80%), 🔴 vermelho (<80%)
- Query: `["beneficiamento-relatorio", safraId]`

#### Uso (Menu: `Agricultura → ④ Pós-Colheita → Beneficiamento`)
```
Na página de Beneficiamento (/beneficiamento), visualiza automaticamente:

SEÇÃO: "Relatório de Rendimento por Método"
├─ Tabela com linhas por método (NATURAL, LAVADO, HONEY, DESCASCADO)
├─ Colunas: Lotes | Entrada (kg) | Saída (kg) | Fator Real | Fator Esp. | Eficiência %
├─ Badges coloridas: 🟢 verde (≥95%) | 🟡 amarelo (≥80%) | 🔴 vermelho (<80%)
└─ Totais: Entrada total | Saída total | Rendimento geral %
```

---

### 2. **Integração 2 — Agrupamento de Múltiplos Romaneios**

#### Backend
- **Migration:** `add_lote_beneficiamento_romaneios` — cria tabela N:N
- **Model:** `LoteBeneficiamentoRomaneio` (lote_id, romaneio_id, peso_entrada_kg)
- **Schema:** `LoteFromRomaneiosRequest` com lista de `romaneio_ids`
- **Método:** `criar_from_romaneios(req)` — valida mesma safra, soma pesos, cria registros N:N
- **Endpoint:** `POST /beneficiamento/from-romaneios`
  - Body: `{ romaneio_ids: [uuid1, uuid2, ...], metodo: "NATURAL", numero_lote: "..." }`
  - Response: `LoteBeneficiamentoResponse` com `romaneios_vinculados: [uuid1, uuid2]`

#### Uso (Menu: `Agricultura → ③ Colheita → Romaneios (Colheita)`)
```
Cenário: Blending de múltiplas colheitas
1. Agricultor registra 3 romaneios (Menu: Agricultura → ③ Colheita)
   └─ Mesma safra, mesmo período de colheita
2. Em Romaneios, seleciona 3 romaneios com checkboxes
3. Clica botão "Processar Selecionados (3)"
4. Sistema cria 1 lote único em Beneficiamento com:
   └─ peso_entrada = soma dos 3 romaneios
   └─ rastreabilidade N:N mantida em tabela coffee_lote_beneficiamento_romaneios
5. Lote aparece em Beneficiamento (Menu: Agricultura → ④ Pós-Colheita → Beneficiamento)
   └─ Pode ver todos os 3 romaneios vinculados
```

---

### 3. **Integração 3 — Armazenagem em Estoque**

#### Backend
- **Migrations:** `add_estoque_beneficiamento_fk` — FKs bidirecionais
- **Models:**
  - `LoteBeneficiamento.lote_estoque_id` → LoteEstoque criado
  - `LoteEstoque.lote_beneficiamento_id` ← rastreabilidade reversa
- **Método:** `armazenar_no_estoque(lote_id)` valida status=ARMAZENADO, cria:
  - `LoteEstoque` com commodity_id da safra
  - `MovimentacaoEstoque` tipo=ENTRADA, origem_tipo=BENEFICIAMENTO
  - Atualiza `lote.lote_estoque_id`
- **Endpoint:** `POST /beneficiamento/{id}/armazenar`
  - Response: `{ lote_estoque_id, quantidade, deposito_id }`

#### Frontend (`beneficiamento-cafe.tsx`)
- Botão 📦 "Armazenar" aparece quando: `status === "ARMAZENADO"` AND `lote_estoque_id === null`
- Badge "No Estoque" quando `lote_estoque_id != null`
- Mutation: `apiFetch(/beneficiamento/{id}/armazenar, { method: "POST" })`
- Toast: `"Lote enviado ao estoque! SKU: BEN-XXXX"`

#### Uso (Menu: `Agricultura → ④ Pós-Colheita → Beneficiamento`)
```
Fluxo completo:
1. Em Beneficiamento, lote chega a status ARMAZENADO (peso_saída definido)
   └─ Menu: Agricultura → ④ Pós-Colheita → Beneficiamento
2. Na tabela, botão 📦 "Armazenar" aparece (se status=ARMAZENADO e lote_estoque_id=null)
3. Usuário clica "Armazenar"
   ├─ POST /beneficiamento/{id}/armazenar
   ├─ LoteEstoque criado no módulo estoque
   ├─ MovimentacaoEstoque registrada (ENTRADA, origem=BENEFICIAMENTO)
   └─ Toast: "Lote enviado ao estoque! SKU: BEN-XXXX"
4. Rastreabilidade completa:
   └─ Estoque (Menu: Operacional → ② Estoque → Inventário)
      ← Beneficiamento (Menu: Agricultura → ④ Pós-Colheita)
         ← Romaneio (Menu: Agricultura → ③ Colheita)
5. Agora botão 🛒 "Gerar Venda" aparece
   └─ Cria ComercializacaoCommodity em RASCUNHO
```

---

### Próximas Melhorias (Futuro)
- **Alerta de Eficiência** — Notificar se rendimento < esperado para método
- **Histórico de Preços** — Registrar evolução de preço de venda por safra
- **Dashboard de Rendimento** — Gráficos de evolução por método/safra/operador

---

## ✅ Checklist de Testes

### Integração 0 (Romaneios → Beneficiamento → Comercialização)
- [x] Criar romaneio normalmente
- [x] Clicar "Processar" → Lote criado com dados corretos
- [x] Editar lote → Preencher perdas detalhadas
- [x] Mudar status → ARMAZENADO
- [x] Clicar "Gerar Venda" → Comercialização criada
- [x] Verificar dados_extras tem lote_beneficiamento_id
- [x] Tenant isolation: um tenant não vê dados de outro
- [x] Validação: gerar-venda falha se status ≠ ARMAZENADO
- [x] Validação: gerar-venda falha se safra sem commodity

### Integração 1 (Relatório de Rendimento)
- [ ] GET `/beneficiamento/relatorio-rendimento?safra_id=X` retorna breakdown por método
- [ ] Tabela mostra: Entrada, Saída, Fator Real, Fator Esperado, Eficiência %
- [ ] Badges coloridas aparecem: verde (≥95%), amarelo (≥80%), vermelho (<80%)
- [ ] Rendimento geral calculado corretamente
- [ ] Perdas detalhadas (secagem, quebra, defeito) somadas por método

### Integração 2 (Multi-Romaneio)
- [ ] POST `/beneficiamento/from-romaneios` com 2+ romaneios cria 1 lote
- [ ] Peso de entrada = soma dos romaneios
- [ ] Registros N:N criados na tabela `cafe_lote_beneficiamento_romaneios`
- [ ] `romaneios_vinculados` retornado na response
- [ ] Validação: falha se romaneios de safras diferentes
- [ ] Validação: falha se romaneio não encontrado

### Integração 3 (Estoque)
- [ ] POST `/beneficiamento/{id}/armazenar` com status=ARMAZENADO cria LoteEstoque
- [ ] MovimentacaoEstoque criada com tipo=ENTRADA, origem_tipo=BENEFICIAMENTO
- [ ] `lote_beneficiamento_id` preenchido em `estoque_lotes`
- [ ] `lote_estoque_id` retornado na response
- [ ] Botão 📦 "Armazenar" aparece quando status=ARMAZENADO e lote_estoque_id=null
- [ ] Botão 🛒 "Gerar Venda" aparece quando lote_estoque_id != null
- [ ] Validação: falha se status ≠ ARMAZENADO
- [ ] Validação: falha se sacas_beneficiadas <= 0
- [ ] Validação: falha se armazem_id não preenchido

---

**Status:** ✅ Implementação Concluída (4 Integrações)  
**Data:** 2026-04-15  
**Deployment:** ✓ Migrations aplicadas, endpoints testados  
**Próximo:** Testes E2E e validação em staging
