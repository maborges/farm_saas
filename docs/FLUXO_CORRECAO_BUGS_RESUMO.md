# 🐛 Fluxo de Correção de Bugs - Resumo Visual

**Quick Reference para QA e Desenvolvedores**

---

## 🚀 Quando um Teste Falha

### Passo 1: Identificar (2 min)

```bash
# Rodar teste e ver erro
./scripts/run-tests.sh -p tests/modulo/test_feature.py -v

# OU usar debug assistant
./scripts/debug-test-failure.sh tests/modulo/test_feature.py
```

### Passo 2: Classificar (1 min)

| Erro | Causa Provável | Ação |
|------|----------------|------|
| `EntityNotFoundError` | Tenant isolation / Dados não criados | Verificar setup |
| `BusinessRuleError` | Validação de negócio | Validar regra |
| `AssertionError` | Valor inesperado | Debug cálculo |
| `IntegrityError` | Foreign key / Unique constraint | Verificar ordem |
| `TimeoutError` | Loading / Selector errado | Ajustar espera |
| `401 Unauthorized` | Auth falhou | Verificar login |

### Passo 3: Reproduzir (3 min)

```bash
# Modo debug interativo
./scripts/run-tests.sh -p tests/modulo/test_feature.py --pdb

# OU modo verbose com prints
./scripts/run-tests.sh -p tests/modulo/test_feature.py -v -s
```

### Passo 4: Corrigir (15-60 min)

```python
# 1. Criar branch
git checkout -b fix/bug-123-descricao

# 2. Implementar correção
# Editar arquivo com bug

# 3. Adicionar teste de regressão
# Copiar template e adaptar

# 4. Validar correção
./scripts/run-tests.sh -p tests/modulo/test_feature.py
```

### Passo 5: Validar (5 min)

```bash
# Rodar testes relacionados
./scripts/run-tests.sh -m modulo_afetado

# Verificar coverage
./scripts/run-tests.sh -c

# Rodar E2E se aplicável
./scripts/run-e2e-tests.sh -p chromium
```

### Passo 6: Commit (2 min)

```bash
# Commit descritivo
git add .
git commit -m "fix: corrige validação de fase em operações agrícolas

- Adiciona validação de fase antes de criar operação
- Lança BusinessRuleError para fase incompatível
- Adiciona teste de regressão bug-123

Fixes #123"

# Push e PR
git push origin fix/bug-123-descricao
```

---

## 📋 Checklist Rápido

### Antes de Começar

- [ ] Li a mensagem de erro cuidadosamente
- [ ] Identifiquei o módulo afetado
- [ ] Reproduzi o erro localmente
- [ ] Verifiquei se é bug no código ou no teste

### Durante Correção

- [ ] Entendi a causa raiz
- [ ] Implementei correção mínima
- [ ] Adicionei teste que previne regressão
- [ ] Validei que testes relacionados passam

### Depois de Corrigir

- [ ] Rodar todos testes do módulo
- [ ] Verificar coverage não diminuiu
- [ ] Code review solicitado
- [ ] Changelog atualizado

---

## 🎯 Padrões de Correção Comuns

### Pattern 1: Tenant Isolation

```python
# ❌ ERRADO: Usando tenant errado
safra = Safra(tenant_id=outro_tenant_id)  # ← Bug!

# ✅ CORRETO: Usar fixture do tenant
safra = Safra(tenant_id=tenant_id)  # ← Correto!
```

### Pattern 2: Setup Completo

```python
# ❌ ERRADO: Esqueceu dependências
async def test_incompleto(session):
    operacao = await service.criar(operacao_create)  # ← Falta safra!

# ✅ CORRETO: Criar todas dependências
async def test_completo(session, tenant_id, talhao_id):
    safra = Safra(id=uuid4(), tenant_id=tenant_id, talhao_id=talhao_id)
    session.add(safra)
    await session.commit()
    
    operacao_create = OperacaoAgricolaCreate(safra_id=safra.id, ...)
    operacao = await service.criar(operacao_create)
```

### Pattern 3: Validação de Negócio

```python
# ❌ ERRADO: Ignorando validação
async def test_validacao(session, tenant_id):
    operacao = await service.criar(operacao_create)
    assert operacao.id is not None  # ← Falha com BusinessRuleError

# ✅ CORRETO: Testar validação
async def test_validacao(session, tenant_id):
    with pytest.raises(BusinessRuleError) as exc_info:
        await service.criar(operacao_create)
    
    assert "não é permitido" in str(exc_info.value)
```

### Pattern 4: Webhook Automático

```python
# ❌ ERRADO: Ignorando webhook
async def test_webhook(session, tenant_id):
    operacao = await service.criar(operacao_create)
    despesa = await get_despesa(operacao.id)
    assert despesa is None  # ← Falha! Webhook criou despesa

# ✅ CORRETO: Considerar webhook
async def test_webhook(session, tenant_id):
    operacao = await service.criar(operacao_create)
    despesa = await get_despesa(operacao.id)
    assert despesa is not None  # ← Esperado
    assert despesa.valor_total == operacao.custo_total
```

---

## 🔧 Comandos Úteis

### Backend

```bash
# Todos testes
./scripts/run-tests.sh

# Teste específico
./scripts/run-tests.sh -p tests/modulo/test.py

# Com coverage
./scripts/run-tests.sh -c

# Debug mode
./scripts/run-tests.sh -p tests/modulo/test.py --pdb

# Ver apenas falhas
./scripts/run-tests.sh -p tests/modulo/test.py -v 2>&1 | grep FAILED
```

### Frontend

```bash
# Todos E2E
./scripts/run-e2e-tests.sh

# Projeto específico
./scripts/run-e2e-tests.sh -p chromium

# Debug mode
./scripts/run-e2e-tests.sh -d

# UI mode (visual)
./scripts/run-e2e-tests.sh --ui

# Ver relatório
./scripts/run-e2e-tests.sh --report
```

### Debug Assistant

```bash
# Diagnóstico automático
./scripts/debug-test-failure.sh tests/modulo/test.py

# Quick check (sem argumentos)
./scripts/debug-test-failure.sh
```

---

## 📊 Matriz de Prioridade

| Severidade | Impacto | Exemplo | SLA |
|------------|---------|---------|-----|
| 🔴 Crítico | Sistema fora, perda de dados | Login não funciona | 4h |
| 🟡 Alto | Feature principal quebrada | Operação não cria | 24h |
| 🟢 Médio | Feature secundária | Relatório errado | 1 semana |
| ⚪ Baixo | Cosmético, UX | Alinhamento CSS | 2 semanas |

---

## 🎓 Aprendizado

### Após Cada Bug Corrigido

1. **Post-mortem (5 min):**
   - Por que o bug aconteceu?
   - Como poderia ter sido prevenido?
   - O que aprendemos?

2. **Documentar:**
   - Adicionar ao `GUIA_CORRECAO_BUGS.md`
   - Atualizar testes se necessário
   - Compartilhar com time

3. **Prevenir:**
   - Adicionar teste de regressão
   - Melhorar coverage
   - Atualizar checklist de PR

---

## 🔗 Links Rápidos

- [Guia Completo de Correção](./GUIA_CORRECAO_BUGS.md)
- [Plano de Testes QA](./PLANO_TESTES_QA.md)
- [Guia de Testes](./GUIA_TESTES.md)
- [Checklist Sprint](./CHECKLIST_TESTES_SPRINT.md)

---

**Imprimir e colar na mesa!** 🖨️

**Última Atualização:** 2026-03-31
