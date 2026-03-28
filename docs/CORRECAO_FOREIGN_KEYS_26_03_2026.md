# Correção de Foreign Keys - 26/03/2026

## Sumário Executivo

✅ **7 foreign keys adicionadas com sucesso**
✅ **Migration aplicada no banco de dados**
✅ **Models Python atualizados**
✅ **Auditoria final: 0 FKs críticas faltando**

---

## Problema Identificado

Durante auditoria completa do sistema, foram identificadas **7 foreign keys faltantes** em tabelas que referenciam outras entidades.

### Foreign Keys Adicionadas

| Tabela | Coluna | Referência | Ação |
|--------|--------|------------|------|
| `frota_abastecimentos` | `fornecedor_id` | `cadastros_pessoas.id` | ✅ Adicionada |
| `frota_apontamentos_uso` | `talhao_id` | `talhoes.id` | ✅ Adicionada |
| `frota_apontamentos_uso` | `operacao_id` | `operacoes_agricolas.id` | ✅ Adicionada |
| `operacoes_agricolas` | `operador_id` | `cadastros_pessoas.id` | ✅ Adicionada |
| `rh_empreitadas` | `safra_id` | `safras.id` | ✅ Adicionada |
| `rh_lancamentos_diarias` | `safra_id` | `safras.id` | ✅ Adicionada |
| `romaneios_colheita` | `operador_id` | `cadastros_pessoas.id` | ✅ Adicionada |

---

## Arquivos Modificados

### 1. Migration

**Arquivo:** `services/api/migrations/versions/1c6b9bf2f122_add_missing_foreign_keys.py`

```python
# Adiciona 7 foreign keys faltantes com constraints apropriadas:
# - SET NULL para referências opcionais (fornecedor, operador, talhao, operacao)
# - CASCADE para referências obrigatórias (safra em RH)
```

**Status:** ✅ Aplicada com sucesso via `alembic upgrade head`

### 2. Models Python Atualizados

#### 2.1. `operacional/models/abastecimento.py`

```python
fornecedor_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("cadastros_pessoas.id", ondelete="SET NULL"),
    nullable=True,
    comment="Fornecedor do combustível (quando abastecimento externo)"
)
```

#### 2.2. `operacional/models/apontamento.py`

```python
talhao_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("talhoes.id", ondelete="SET NULL"),
    nullable=True,
    comment="Talhão onde a operação foi realizada"
)

operacao_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("operacoes_agricolas.id", ondelete="SET NULL"),
    nullable=True,
    comment="Tipo de operação realizada (plantio, pulverização, etc)"
)
```

#### 2.3. `agricola/operacoes/models.py`

```python
operador_id: Mapped[UUID | None] = mapped_column(
    Uuid,
    ForeignKey("cadastros_pessoas.id", ondelete="SET NULL"),
    nullable=True,
    comment="Operador que realizou a operação agrícola"
)
```

#### 2.4. `rh/models.py` (LancamentoDiaria)

```python
safra_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("safras.id", ondelete="CASCADE"),
    nullable=True,
    comment="Safra à qual o lançamento está vinculado"
)
```

#### 2.5. `rh/models.py` (Empreitada)

```python
safra_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("safras.id", ondelete="CASCADE"),
    nullable=True,
    comment="Safra à qual a empreitada está vinculada"
)
```

#### 2.6. `agricola/romaneios/models.py`

```python
operador_id: Mapped[UUID | None] = mapped_column(
    Uuid,
    ForeignKey("cadastros_pessoas.id", ondelete="SET NULL"),
    nullable=True,
    comment="Operador da colhedora"
)
```

---

## Scripts Criados

### 1. `scripts/audit_all_foreign_keys.py`

**Funcionalidade:**
- Varre todas as 103 tabelas do sistema
- Identifica colunas UUID que deveriam ter FK
- Compara com FKs existentes no banco
- Gera relatório completo de issues

**Como executar:**
```bash
cd services/api
source .venv/bin/activate
python scripts/audit_all_foreign_keys.py
```

### 2. `scripts/check_orphaned_data.py`

**Funcionalidade:**
- Verifica se há dados órfãos antes de criar FKs
- Previne erros ao aplicar constraints

**Como executar:**
```bash
cd services/api
source .venv/bin/activate
python scripts/check_orphaned_data.py
```

### 3. `scripts/check_missing_fks.py`

**Funcionalidade:**
- Verifica FKs específicas de equipamentos
- Útil para validação rápida

---

## Validação Final

### Estatísticas Após Correção

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| Total de FKs | 230 | **237** | +7 |
| Taxa de cobertura | 91.6% | **94.4%** | +2.8% |
| FKs críticas faltando | 0 | **0** | ✅ |
| Avisos | 56 | **50** | -6 |

### Verificação de FKs Criadas

Todas as 7 FKs foram verificadas no banco de dados PostgreSQL:

```sql
✅ frota_abastecimentos.fornecedor_id → cadastros_pessoas.id (ON DELETE SET NULL)
✅ frota_apontamentos_uso.talhao_id → talhoes.id (ON DELETE SET NULL)
✅ frota_apontamentos_uso.operacao_id → operacoes_agricolas.id (ON DELETE SET NULL)
✅ operacoes_agricolas.operador_id → cadastros_pessoas.id (ON DELETE SET NULL)
✅ rh_empreitadas.safra_id → safras.id (ON DELETE CASCADE)
✅ rh_lancamentos_diarias.safra_id → safras.id (ON DELETE CASCADE)
✅ romaneios_colheita.operador_id → cadastros_pessoas.id (ON DELETE SET NULL)
```

---

## Benefícios da Correção

### 1. Integridade Referencial ✅
- Impossível criar registros órfãos
- Banco de dados garante consistência dos dados
- Cascata de deleção apropriada

### 2. Performance 🚀
- PostgreSQL pode otimizar JOINs melhor
- Índices automáticos nas FKs
- Planos de execução mais eficientes

### 3. Manutenibilidade 📚
- Documentação automática via constraints
- Erros detectados no banco, não na aplicação
- Facilita desenvolvimento de novas features

### 4. Segurança 🔒
- Previne inconsistências de dados
- Impossível referenciar IDs inexistentes
- Auditoria mais confiável

---

## Observações Importantes

### Campos Polimórficos (sem FK proposital)

Os seguintes campos **não têm** e **não devem ter** FK pois são polimórficos:

- `admin_audit_log.entidade_id` - Pode referenciar qualquer entidade
- `estoque_movimentacoes.origem_id` - Pode ser compra, produção, etc.
- `estoque_requisicoes.origem_id` - Pode ser OS, operação, etc.
- `estoque_reservas.referencia_id` - Pode ser venda, operação, etc.

### FKs que Usam Tabelas Especializadas (correto)

- `cadastros_produtos.modelo_id` → `cadastros_modelos_produto` ✅
- `cadastros_produtos.categoria_id` → `cadastros_categorias_produto` ✅
- `compras_*.fornecedor_id` → `compras_fornecedores` ✅
- `estoque_*.lote_id` → `estoque_lotes` ✅

---

## Rollback

Se necessário, a migration pode ser revertida:

```bash
cd services/api
source .venv/bin/activate
alembic downgrade -1
```

Isso removerá as 7 FKs adicionadas.

---

## Próximos Passos (Opcional)

### Melhorias Futuras

1. **Adicionar `relationship()` nos models** para navegação ORM
2. **Criar índices compostos** para queries frequentes
3. **Documentar campos polimórficos** de forma mais explícita

---

**Data:** 2026-03-26
**Responsável:** Claude Code Assistant
**Status:** ✅ Concluído com sucesso
**Impacto:** Baixo risco, alta melhoria de qualidade
