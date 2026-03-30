# API Endpoints Reference — Integração de Colheita

**Data:** 2026-03-30
**Base URL:** `http://localhost:8000/api/v1` (local) ou `https://api.example.com/api/v1` (produção)

---

## 📋 Novos Endpoints

### 1. Dashboard Financeiro da Safra

**GET** `/agricola/dashboard/safras/{safra_id}/resumo-financeiro`

Retorna resumo financeiro completo de uma safra com agregações de custos, receitas, ROI e produtividade.

#### Request

```bash
curl -X GET "http://localhost:8000/api/v1/agricola/dashboard/safras/abc123-def456/resumo-financeiro" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json"
```

#### Parameters

| Nome | Tipo | Localização | Obrigatório | Descrição |
|------|------|-------------|-------------|-----------|
| safra_id | UUID | Path | Sim | ID da safra |

#### Headers

| Nome | Valor | Obrigatório |
|------|-------|-------------|
| Authorization | Bearer `<jwt_token>` | Sim |
| Content-Type | application/json | Não (GET) |

#### Permissions

```
agricola:safras:view
```

#### Response 200 (Success)

```json
{
  "id": "abc123-def456-789012",
  "cultura": "MILHO",
  "ano_safra": "2025/26",
  "status": "COLHEITA",
  "area_plantada_ha": 100.0,
  "financeiro": {
    "total_operacoes": 5,
    "custo_operacoes_total": 5000.00,
    "custo_por_ha": 50.00,
    "total_romaneios": 3,
    "total_sacas": 3000.00,
    "produtividade_sc_ha": 30.00,
    "despesa_total": 5000.00,
    "receita_total": 300000.00,
    "lucro_bruto": 295000.00,
    "roi_pct": 5900.00
  }
}
```

#### Response 404 (Not Found)

```json
{
  "detail": "Safra not found"
}
```

#### Response 403 (Forbidden)

```json
{
  "detail": "Not authorized to view this safra"
}
```

#### Error Codes

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso — resumo retornado |
| 404 | Safra não encontrada ou não pertence ao tenant |
| 403 | Usuário sem permissão |
| 500 | Erro interno do servidor |

#### Exemplo de Uso (JavaScript)

```typescript
import { apiFetch } from "@/lib/api";

const safraId = "abc123-def456-789012";
const resumo = await apiFetch(
  `/agricola/dashboard/safras/${safraId}/resumo-financeiro`
);

console.log(resumo.financeiro.roi_pct);  // 5900.0
```

#### Cálculos Implementados

```
1. Custo Total
   = SUM(operacoes.custo_total) + SUM(despesas.valor_total)
   WHERE despesas.origem_tipo = 'OPERACAO_AGRICOLA'

2. Receita Total
   = SUM(romaneios.receita_total) + SUM(receitas.valor_total)
   WHERE receitas.origem_tipo = 'ROMANEIO_COLHEITA'

3. Lucro Bruto
   = Receita Total - Custo Total

4. ROI (Return on Investment)
   = (Lucro Bruto / Custo Total) × 100
   = NULL se Custo Total = 0

5. Produtividade
   = Total Sacas / Area Plantada (ha)
   = NULL se Area = 0
```

#### Tempo de Resposta

- **Sem Cache:** ~200-500ms (primeira chamada)
- **Com Cache:** ~50ms (chamadas subsequentes)
- **Revalidação:** A cada 30 segundos (TanStack Query)

---

## 🔄 Webhooks Internos

### Webhook 1: Operação → Despesa

**Acionado:** Quando operação é criada com `custo_total > 0`

#### Lógica

```python
# Em agricola/operacoes/service.py → criar()

if operacao_create.custo_total and operacao_create.custo_total > 0:
    # 1. Buscar plano de conta padrão
    plano = await self._buscar_plano_custeio(tenant_id)

    # 2. Criar Despesa
    despesa = Despesa(
        tenant_id=tenant_id,
        fazenda_id=safra.fazenda_id,
        plano_conta_id=plano.id,
        descricao=f"{operacao.tipo} — {safra.cultura} {safra.ano_safra}",
        valor_total=operacao.custo_total,
        data_emissao=operacao.data_realizada,
        data_vencimento=operacao.data_realizada,
        data_pagamento=operacao.data_realizada,
        status="PAGO",
        origem_id=operacao.id,              # ← Link para operação
        origem_tipo="OPERACAO_AGRICOLA"     # ← Tipo genérico
    )
    session.add(despesa)
    await session.commit()
```

#### Campos Criados

| Campo | Valor | Origem |
|-------|-------|--------|
| `id` | UUID aleatório | Gerado |
| `tenant_id` | Do contexto | JWT |
| `fazenda_id` | De safra | Link operação → safra → fazenda |
| `plano_conta_id` | Conta de custeio padrão | Config |
| `valor_total` | operacao.custo_total | Operação |
| `data_emissao` | operacao.data_realizada | Operação |
| `status` | "PAGO" | Padrão |
| `origem_id` | operacao.id | Operação |
| `origem_tipo` | "OPERACAO_AGRICOLA" | Constante |

#### Exemplo

```
Operação Criada:
  id: 789012-abcd-efgh
  tipo: COLHEITA
  custo_total: 5000.00
  data_realizada: 2026-03-30

↓ Webhook executado ↓

Despesa Criada:
  id: xyz987-abcd-efgh
  valor_total: 5000.00
  origem_id: 789012-abcd-efgh
  origem_tipo: OPERACAO_AGRICOLA
  descricao: "COLHEITA — MILHO 2025/26"
```

---

### Webhook 2: Romaneio → Receita

**Acionado:** Quando romaneio é criado com `receita_total > 0`

#### Lógica

```python
# Em agricola/romaneios/service.py → criar()

if romaneio.receita_total and romaneio.receita_total > 0:
    # 1. Buscar plano de conta de receita
    plano = await self._buscar_plano_receita(tenant_id)

    # 2. Calcular campos derivados ANTES de criar receita
    sacas = romaneio.sacas_60kg  # Já calculado por MAPA
    receita = sacas * romaneio.preco_saca

    # 3. Criar Receita
    receita = Receita(
        tenant_id=tenant_id,
        fazenda_id=safra.fazenda_id,
        plano_conta_id=plano.id,
        descricao=f"Venda de grãos — {safra.cultura} {safra.ano_safra}",
        valor_total=receita,
        data_emissao=romaneio.data_colheita,
        data_vencimento=romaneio.data_colheita,
        data_recebimento=romaneio.data_colheita,
        status="RECEBIDO",
        origem_id=romaneio.id,              # ← Link para romaneio
        origem_tipo="ROMANEIO_COLHEITA"     # ← Tipo genérico
    )
    session.add(receita)
    await session.commit()
```

#### Campos Criados

| Campo | Valor | Origem |
|-------|-------|--------|
| `id` | UUID aleatório | Gerado |
| `tenant_id` | Do contexto | JWT |
| `fazenda_id` | De safra | Link romaneio → safra → fazenda |
| `plano_conta_id` | Conta de receita padrão | Config |
| `valor_total` | sacas × preco | Romaneio |
| `data_emissao` | romaneio.data_colheita | Romaneio |
| `status` | "RECEBIDO" | Padrão |
| `origem_id` | romaneio.id | Romaneio |
| `origem_tipo` | "ROMANEIO_COLHEITA" | Constante |

#### Exemplo

```
Romaneio Criado:
  id: abc456-xyz-pqr
  data_colheita: 2026-03-30
  sacas_60kg: 1000.0
  preco_saca: 100.00

↓ Webhook executado ↓

Receita Criada:
  id: def789-xyz-pqr
  valor_total: 100000.00  (1000 × 100)
  origem_id: abc456-xyz-pqr
  origem_tipo: ROMANEIO_COLHEITA
  descricao: "Venda de grãos — MILHO 2025/26"
```

---

## 🔍 Queries de Validação

### Validação 1: Fase Permitida

**Arquivo:** `agricola/operacoes/service.py` (linhas 45-55)

```python
# Buscar tipo de operação
stmt = select(OperacaoTipoFase).where(
    OperacaoTipoFase.tipo_operacao == operacao_create.tipo
)
tipo_fase = (await session.execute(stmt)).scalar_one_or_none()

if not tipo_fase:
    raise BusinessRuleError(f"Tipo {operacao_create.tipo} não cadastrado")

# Verificar se fase é permitida
fases_permitidas = json.loads(tipo_fase.fases_permitidas)
if safra.status not in fases_permitidas:
    raise BusinessRuleError(
        f"{operacao_create.tipo} não permitido em fase {safra.status}"
    )
```

### Validação 2: Data Não Futura

```python
if operacao_create.data_realizada > date.today():
    raise BusinessRuleError("Data de operação não pode ser futura")
```

### Validação 3: Tenant Isolation

```python
# Em cada method de service
if not safra or safra.tenant_id != self.tenant_id:
    raise EntityNotFoundError("Safra", safra_id)
```

---

## 📊 Agregações SQL

### Query: Custo Total de Safra

```sql
SELECT
  COALESCE(SUM(oa.custo_total), 0) +
  COALESCE(SUM(CASE
    WHEN fd.origem_tipo = 'OPERACAO_AGRICOLA' THEN fd.valor_total
    ELSE 0
  END), 0) as custo_total
FROM operacoes_agricolas oa
FULL OUTER JOIN fin_despesas fd ON oa.id = fd.origem_id
WHERE oa.safra_id = $1
  AND oa.tenant_id = $2
```

### Query: Receita Total de Safra

```sql
SELECT
  COALESCE(SUM(rc.receita_total), 0) +
  COALESCE(SUM(CASE
    WHEN fr.origem_tipo = 'ROMANEIO_COLHEITA' THEN fr.valor_total
    ELSE 0
  END), 0) as receita_total
FROM romaneios_colheita rc
FULL OUTER JOIN fin_receitas fr ON rc.id = fr.origem_id
WHERE rc.safra_id = $1
  AND rc.tenant_id = $2
```

---

## 🔐 Security & Permissions

### Permission Matrix

| Endpoint | Permissão | Descrição |
|----------|-----------|-----------|
| GET `/safras/{id}/resumo-financeiro` | `agricola:safras:view` | Apenas ver |
| GET `/safras/{id}/operacoes` | `agricola:safras:view` | Apenas ver |
| POST `/operacoes` | `agricola:operacoes:create` | Criar operações |
| PATCH `/operacoes/{id}` | `agricola:operacoes:edit` | Editar operações |

### Tenant Isolation

Todos os endpoints validam:
```python
if safra.tenant_id != get_tenant_id(request):
    raise TenantViolationError()
```

---

## 📈 Performance Notes

### Índices Necessários

```sql
-- Já existem em base
CREATE INDEX idx_operacoes_safra_id ON operacoes_agricolas(safra_id);
CREATE INDEX idx_romaneios_safra_id ON romaneios_colheita(safra_id);
CREATE INDEX idx_despesas_origem ON fin_despesas(origem_id, origem_tipo);
CREATE INDEX idx_receitas_origem ON fin_receitas(origem_id, origem_tipo);
```

### Cache Strategy

- **Frontend:** TanStack Query com 30s de `staleTime`
- **Backend:** Sem cache (sempre fresh)
- **CDN:** Cache headers: `Cache-Control: public, max-age=30`

---

## 🐛 Troubleshooting

### Problema: Dashboard mostra R$ 0 em tudo

**Causa possível:** Webhook não executou

**Debug:**
```sql
SELECT COUNT(*) FROM fin_despesas WHERE origem_tipo = 'OPERACAO_AGRICOLA';
-- Esperado: > 0

SELECT COUNT(*) FROM fin_receitas WHERE origem_tipo = 'ROMANEIO_COLHEITA';
-- Esperado: > 0
```

### Problema: Erro 404 ao acessar dashboard

**Causa possível:** Safra não existe OU tenant_id não bate

**Debug:**
```bash
# Verificar safra existe
psql -d farm_db -c "SELECT id, tenant_id FROM safras WHERE id = 'YOUR_ID';"

# Verificar tenant no token
# Decode JWT: https://jwt.io
# Verificar claim "tenant_id"
```

### Problema: ROI mostra NULL

**Causa esperada:** Sem despesas (custo = 0)

```python
# ROI é NULL quando:
if despesa_total == 0:
    roi_pct = None
```

---

## 📚 Documentação Relacionada

- [IMPLEMENTACAO_COLHEITA_COMPLETA.md](./IMPLEMENTACAO_COLHEITA_COMPLETA.md)
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- [E2E_TEST_SCENARIOS.md](./E2E_TEST_SCENARIOS.md)

