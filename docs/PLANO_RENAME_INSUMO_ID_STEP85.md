# Plano de Rename: `insumo_id` → `produto_id` em `insumos_operacao`

**Data:** 2026-04-28  
**Step:** 85  
**Status:** Planejamento — nenhum rename executado ainda.

---

## Contexto

`InsumoOperacao.insumo_id` referencia `cadastros_produtos.id` — o catálogo canônico de produtos.  
Todos os demais módulos usam `produto_id` para a mesma FK. O nome `insumo_id` é uma inconsistência semântica identificada na auditoria Step 82 (INC-01).

A coluna já tem FK correta; o rename é puramente de nomenclatura.

---

## Inventário de Impacto

### Banco de Dados

| Objeto | Tipo | Ação necessária |
|--------|------|----------------|
| `insumos_operacao.insumo_id` | Coluna | `ALTER TABLE ... RENAME COLUMN insumo_id TO produto_id` |
| `ix_insumos_operacao_insumo_id` (se existir) | Índice | Recriar como `ix_insumos_operacao_produto_id` |
| FK sem nome explícito na migration original | FK constraint | Verificar nome gerado; recriar se necessário |

### Backend — Python

| Arquivo | Referências | Tipo de mudança |
|---------|------------|----------------|
| `agricola/operacoes/models.py:93` | `insumo_id: Mapped[UUID]` | Renomear campo no model |
| `agricola/operacoes/schemas.py:7` | `InsumoOperacaoCreate.insumo_id` | Renomear campo no schema |
| `agricola/operacoes/schemas.py:17` | `InsumoOperacaoResponse.insumo_id` | Renomear campo no schema |
| `agricola/operacoes/service.py:94,96,102,107,116,142,160` | `insumo.insumo_id` (7 refs) | Renomear atributo — acesso ao schema e ao model |
| `agricola/rastreabilidade/router.py:102,193` | `i.insumo_id` (2 refs) | Acesso ao model — renomear |
| `agricola/rastreabilidade/service.py:58,144` | `i.insumo_id` (2 refs) | Acesso ao model — renomear |
| `operacional/services/relatorio_service.py:115,125,127,132` | `ins.insumo_id` (4 refs) | Acesso ao model — renomear |
| `agricola/caderno/service.py:488` | `ins.get("insumo_id", ...)` | Dict key — renomear |

**Total backend: 18 referências em 6 arquivos.**

### Shared Schemas (package)

| Arquivo | Referências | Tipo de mudança |
|---------|------------|----------------|
| `packages/zod-schemas/src/agricola/operacao.ts:6` | `insumo_id: z.string().uuid()` | Renomear campo no schema Zod |

### Frontend (`apps/web/src`)

Nenhuma referência direta a `insumo_id` encontrada em `.ts` / `.tsx`.  
O frontend consome via `InsumoOperacaoResponse` — será impactado apenas se renderizar o campo pelo nome (`response.insumo_id`). Verificar componentes que mapeiam insumos de operação antes de executar.

### Testes

| Arquivo | Referências | Tipo de mudança |
|---------|------------|----------------|
| `tests/unit/agricola/test_insumo_campos_canonicos.py:15,57,80` | `"insumo_id"` / variável local `insumo_id` | Renomear campo no payload e variáveis |

---

## Estratégia de Migração Compatível

### Opção A — Rename direto com janela de manutenção (recomendada)

Execução em um único step atômico:

1. **Migration DDL** (`step27_rename_insumo_id`):
   ```sql
   ALTER TABLE insumos_operacao RENAME COLUMN insumo_id TO produto_id;
   -- Recriar índice se necessário
   DROP INDEX IF EXISTS ix_insumos_operacao_insumo_id;
   CREATE INDEX ix_insumos_operacao_produto_id ON insumos_operacao (produto_id);
   ```

2. **Code changes** (mesmo deploy):
   - `models.py`: `insumo_id` → `produto_id`
   - `schemas.py` (Create + Response): `insumo_id` → `produto_id`
   - `service.py`, `rastreabilidade/router.py`, `rastreabilidade/service.py`, `relatorio_service.py`, `caderno/service.py`: substituição de `insumo_id` por `produto_id`
   - `zod-schemas/operacao.ts`: `insumo_id` → `produto_id`
   - `test_insumo_campos_canonicos.py`: campo e variáveis locais

**Janela:** O rename de coluna no PostgreSQL é instantâneo (operação metadata, sem rewrite). Risco de downtime: zero se migration e código forem deployados juntos.

---

### Opção B — Alias temporário via `@property` (sem migration imediata)

Adicionar um alias Python no model para suportar `produto_id` enquanto a coluna ainda se chama `insumo_id`:

```python
# models.py — alias de transição
@property
def produto_id(self) -> UUID:
    return self.insumo_id

@produto_id.setter
def produto_id(self, value: UUID) -> None:
    self.insumo_id = value
```

Permite migrar os consumidores de código antes da migration DDL.  
**Desvantagem:** não funciona com `select(InsumoOperacao.produto_id)` no SQLAlchemy — queries SQL continuariam usando `insumo_id`. Útil apenas como passo intermediário de semana.

---

## Sequência Recomendada (Opção A)

| # | Ação | Arquivo(s) |
|---|------|-----------|
| 1 | Migration `step27_rename_insumo_id` | `migrations/versions/step27_rename_insumo_id.py` |
| 2 | Model | `agricola/operacoes/models.py` |
| 3 | Schemas | `agricola/operacoes/schemas.py` |
| 4 | Service | `agricola/operacoes/service.py` |
| 5 | Rastreabilidade | `agricola/rastreabilidade/router.py` + `service.py` |
| 6 | Relatório | `operacional/services/relatorio_service.py` |
| 7 | Caderno | `agricola/caderno/service.py` |
| 8 | Shared schemas | `packages/zod-schemas/src/agricola/operacao.ts` |
| 9 | Testes | `tests/unit/agricola/test_insumo_campos_canonicos.py` |
| 10 | Validação | `pytest` + `alembic upgrade head` |

---

## Checklist de Validação Pós-Rename

- [ ] `alembic upgrade head` sem erro
- [ ] `\d insumos_operacao` confirma coluna `produto_id` (sem `insumo_id`)
- [ ] `grep -r "insumo_id" services/api --include="*.py" | grep -v migrations` retorna zero resultados
- [ ] `grep -r "insumo_id" packages/zod-schemas --include="*.ts"` retorna zero resultados
- [ ] `pytest tests/integration/agricola/` — todos passam
- [ ] `pytest tests/unit/agricola/test_insumo_campos_canonicos.py` — todos passam
- [ ] `pytest tests/integration/operacional/test_relatorio_estoque_ledger.py` — passa

---

## Riscos

| Risco | Probabilidade | Mitigação |
|-------|--------------|-----------|
| API antiga quebra clientes que passam `insumo_id` no body | Média | Pydantic ignora campos extras por padrão; receber `insumo_id` sem efeito. Documentar breaking change no changelog |
| Frontend renderiza `response.insumo_id` diretamente | Baixa | Nenhuma ref encontrada em `.tsx`; verificar antes de executar |
| FK constraint name hardcoded em alguma migration histórica | Baixa | Verificar `02e5c1fef995` e `f1569f5e75f7` antes de renomear |
| `caderno/service.py:488` usa `ins.get("insumo_id")` em dict | Média | Verificar origem do dict: se for `model_dump()` o campo já terá novo nome |

---

## Referências

- `docs/AUDITORIA_PRODUTO_CANONICO_STEP82.md` — INC-01
- `agricola/operacoes/models.py:93`
- `agricola/operacoes/schemas.py:7,17`
- `agricola/operacoes/service.py` — 7 referências
