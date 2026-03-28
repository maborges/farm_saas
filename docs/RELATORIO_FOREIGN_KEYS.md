# Relatório de Auditoria de Foreign Keys

**Data:** 2026-03-26
**Sistema:** AgroSaaS API
**Banco de Dados:** PostgreSQL (schema: farms)

## Sumário Executivo

✅ **Resultado:** Sistema está em bom estado geral
⚠️ **Avisos:** 7 foreign keys faltantes (não críticas)
📊 **Total de tabelas:** 103
📊 **Total de colunas UUID:** 251
📊 **Foreign Keys existentes:** 230 (91.6% de cobertura)

---

## 🎯 Principais Descobertas

### ✅ O que está correto

1. **Todas as foreign keys críticas existem:**
   - `tenant_id` → `tenants.id` (isolamento multi-tenant)
   - Todos os campos de equipamento referenciam `cadastros_equipamentos.id`
   - Relacionamentos principais entre módulos estão corretos

2. **Integridade referencial bem implementada:**
   - 230 foreign keys encontradas no total
   - Uso consistente de `ON DELETE CASCADE` onde apropriado
   - Uso de `ON DELETE SET NULL` para referências opcionais

### ⚠️ Foreign Keys Faltantes (7 casos)

Estes campos terminam em `_id` mas **não têm constraint de FK no banco**. Isso pode ser proposital (FKs lógicas) ou pode ser uma omissão:

#### 1. **frota_abastecimentos.fornecedor_id**
- **Deveria referenciar:** `cadastros_pessoas.id`
- **Status atual:** Campo UUID sem FK
- **Comentário no model:** "FK lógica para pessoas/fornecedores"
- **Ação sugerida:** Adicionar FK ou documentar melhor que é proposital

#### 2. **frota_apontamentos_uso.talhao_id**
- **Deveria referenciar:** `talhoes.id`
- **Status atual:** Campo UUID sem FK
- **Comentário no model:** "FK lógica para talhoes.id"
- **Ação sugerida:** Adicionar FK para garantir integridade

#### 3. **frota_apontamentos_uso.operacao_id**
- **Deveria referenciar:** `operacoes.id`
- **Status atual:** Campo UUID sem FK
- **Comentário no model:** "FK lógica para operacoes.id"
- **Ação sugerida:** Adicionar FK para garantir integridade

#### 4. **operacoes_agricolas.operador_id**
- **Deveria referenciar:** `cadastros_pessoas.id`
- **Status atual:** Campo UUID sem FK
- **Ação sugerida:** Adicionar FK

#### 5. **rh_empreitadas.safra_id**
- **Deveria referenciar:** `safras.id`
- **Status atual:** Campo UUID sem FK
- **Ação sugerida:** Adicionar FK

#### 6. **rh_lancamentos_diarias.safra_id**
- **Deveria referenciar:** `safras.id`
- **Status atual:** Campo UUID sem FK
- **Ação sugerida:** Adicionar FK

#### 7. **romaneios_colheita.operador_id**
- **Deveria referenciar:** `cadastros_pessoas.id`
- **Status atual:** Campo UUID sem FK
- **Ação sugerida:** Adicionar FK

---

## 📝 Observações Sobre Mapeamentos Diferentes

Alguns campos têm FK mas apontam para tabelas diferentes do esperado pelo padrão de nomenclatura. **Isso é normal e correto** quando há tabelas especializadas:

### Corretos (mas diferentes do padrão genérico)

1. **cadastros_produtos.modelo_id** → `cadastros_modelos_produto` ✅
   - Usa tabela específica de modelos de produto (correto)

2. **cadastros_produtos.categoria_id** → `cadastros_categorias_produto` ✅
   - Usa tabela específica de categorias de produto (correto)

3. **compras_cotacoes.fornecedor_id** → `compras_fornecedores` ✅
   - Usa tabela específica de fornecedores (correto)

4. **estoque_movimentacoes.lote_id** → `estoque_lotes` ✅
   - Usa lote de estoque, não lote de pecuária (correto)

5. **cadastros_pessoas_acesso_log.usuario_id** → `usuarios` ✅
   - Log de acesso backoffice usa tabela de usuários admin (correto)

### Campos Polimórficos (sem FK proposital)

Estes campos podem referenciar múltiplas tabelas dependendo do contexto, por isso **não devem ter FK**:

1. **admin_audit_log.entidade_id** - Pode ser qualquer entidade
2. **estoque_movimentacoes.origem_id** - Pode ser compra, produção, transferência
3. **estoque_requisicoes.origem_id** - Pode ser ordem de serviço, operação, etc.
4. **estoque_reservas.referencia_id** - Pode ser venda, operação, etc.
5. **crm_leads.tenant_convertido_id** - Só preenchido após conversão
6. **cupons.criado_por_id** - Pode ser admin ou sistema
7. **email_templates.editado_por_id** - Pode ser admin ou sistema

---

## 🔧 Recomendações de Ação

### Alta Prioridade ⚠️

Adicionar foreign keys para garantir integridade referencial:

```sql
-- Migration para adicionar FKs faltantes

-- 1. frota_abastecimentos
ALTER TABLE farms.frota_abastecimentos
  ADD CONSTRAINT frota_abastecimentos_fornecedor_id_fkey
  FOREIGN KEY (fornecedor_id)
  REFERENCES farms.cadastros_pessoas(id)
  ON DELETE SET NULL;

-- 2. frota_apontamentos_uso
ALTER TABLE farms.frota_apontamentos_uso
  ADD CONSTRAINT frota_apontamentos_uso_talhao_id_fkey
  FOREIGN KEY (talhao_id)
  REFERENCES farms.talhoes(id)
  ON DELETE SET NULL;

ALTER TABLE farms.frota_apontamentos_uso
  ADD CONSTRAINT frota_apontamentos_uso_operacao_id_fkey
  FOREIGN KEY (operacao_id)
  REFERENCES farms.operacoes(id)
  ON DELETE SET NULL;

-- 3. operacoes_agricolas
ALTER TABLE farms.operacoes_agricolas
  ADD CONSTRAINT operacoes_agricolas_operador_id_fkey
  FOREIGN KEY (operador_id)
  REFERENCES farms.cadastros_pessoas(id)
  ON DELETE SET NULL;

-- 4. rh_empreitadas
ALTER TABLE farms.rh_empreitadas
  ADD CONSTRAINT rh_empreitadas_safra_id_fkey
  FOREIGN KEY (safra_id)
  REFERENCES farms.safras(id)
  ON DELETE CASCADE;

-- 5. rh_lancamentos_diarias
ALTER TABLE farms.rh_lancamentos_diarias
  ADD CONSTRAINT rh_lancamentos_diarias_safra_id_fkey
  FOREIGN KEY (safra_id)
  REFERENCES farms.safras(id)
  ON DELETE CASCADE;

-- 6. romaneios_colheita
ALTER TABLE farms.romaneios_colheita
  ADD CONSTRAINT romaneios_colheita_operador_id_fkey
  FOREIGN KEY (operador_id)
  REFERENCES farms.cadastros_pessoas(id)
  ON DELETE SET NULL;
```

### Média Prioridade 📝

Atualizar models Python para refletir as FKs que serão adicionadas:

```python
# Exemplo: operacional/models/abastecimento.py
fornecedor_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("cadastros_pessoas.id", ondelete="SET NULL"),
    nullable=True,
    comment="Fornecedor do combustível"
)
```

### Baixa Prioridade 📚

Documentar explicitamente os campos polimórficos que **não devem ter FK**:

```python
# Exemplo: estoque/models.py
origem_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    nullable=True,
    comment="POLIMÓRFICO: pode ser compra_id, producao_id, transferencia_id. Não usar FK."
)
```

---

## 📊 Estatísticas Detalhadas

| Métrica | Valor |
|---------|-------|
| Total de tabelas | 103 |
| Total de colunas UUID (exceto PK) | 251 |
| Foreign Keys implementadas | 230 |
| Foreign Keys faltantes (críticas) | 0 |
| Foreign Keys faltantes (avisos) | 7 |
| Campos polimórficos (sem FK proposital) | 7 |
| Taxa de cobertura de FK | 91.6% |

---

## ✅ Conclusão

O sistema está **bem estruturado** em termos de integridade referencial:

1. ✅ **Nenhuma FK crítica faltando** (tenant_id, user_id, etc. estão todos corretos)
2. ✅ **Alta cobertura de FKs** (91.6%)
3. ⚠️ **7 FKs opcionais faltantes** - todas não críticas
4. ✅ **Campos polimórficos corretamente identificados**

### Próximos Passos

1. Revisar os 7 campos listados acima e decidir se devem ter FK
2. Criar migration para adicionar as FKs decididas
3. Atualizar models Python para refletir as mudanças
4. Documentar explicitamente campos polimórficos

---

**Script de auditoria:** `services/api/scripts/audit_all_foreign_keys.py`
**Como executar:** `cd services/api && source .venv/bin/activate && python scripts/audit_all_foreign_keys.py`
