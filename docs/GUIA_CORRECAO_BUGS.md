# 🔧 Guia de Correção de Bugs - AgroSaaS

**Versão:** 1.0.0
**Data:** 2026-03-31
**Status:** ✅ Ativo

---

## 📋 Índice

1. [Fluxo de Correção de Bugs](#1-fluxo-de-correção-de-bugs)
2. [Problemas Comuns e Soluções](#2-problemas-comuns-e-soluções)
3. [Debug Passo a Passo](#3-debug-passo-a-passo)
4. [Padrões de Correção](#4-padrões-de-correção)
5. [Prevenção de Regressões](#5-prevenção-de-regressões)

---

## 1. Fluxo de Correção de Bugs

### Quando um Teste Falha

```
┌─────────────────────────────────────────────────────────────┐
│ 1. IDENTIFICAR O PROBLEA                                    │
│    - Ler mensagem de erro                                   │
│    - Verificar stack trace                                  │
│    - Identificar módulo afetado                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. REPRODUZIR O PROBLEMA                                    │
│    - Rodar teste em modo debug                              │
│    - Verificar se é consistente                             │
│    - Isolar causa raiz                                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. ANALISAR CAUSA RAIZ                                      │
│    - É bug no código ou no teste?                           │
│    - É problema de dados?                                   │
│    - É problema de integração?                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. CORRIGIR                                                 │
│    - Criar branch de correção                               │
│    - Implementar fix                                        │
│    - Adicionar teste que previne regressão                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. VALIDAR                                                  │
│    - Rodar testes locais                                    │
│    - Rodar testes relacionados                              │
│    - Verificar coverage                                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. COMMIT E PR                                              │
│    - Commit descritivo                                      │
│    - Linkar issue/bug                                       │
│    - Code review                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Problemas Comuns e Soluções

### 2.1 Teste Falha com `EntityNotFoundError`

**Sintoma:**
```python
E   core.exceptions.EntityNotFoundError: Entity not found: Safra
```

**Causas Possíveis:**

1. **Tenant isolation:** Teste tentando acessar dados de outro tenant
2. **Dados não criados:** Setup do teste incompleto
3. **Foreign key inválida:** Referenciando ID que não existe

**Solução:**

```python
# ❌ ERRADO: Esqueceu de criar a safra no setup
async def test_operacao_sem_safra(session, tenant_id):
    service = OperacaoService(session, tenant_id)
    # Vai falhar pois safra_id não existe
    await service.criar(operacao_create)

# ✅ CORRETO: Criar safra no setup
async def test_operacao_com_safra(session, tenant_id, talhao_id):
    # Setup completo
    safra = Safra(
        id=uuid4(),
        tenant_id=tenant_id,  # ← Mesmo tenant!
        talhao_id=talhao_id,
        ano_safra="2025/26",
        cultura="SOJA",
        status="PLANTIO",
        area_plantada_ha=100.0
    )
    session.add(safra)
    await session.commit()
    
    # Agora usa o ID correto
    operacao_create = OperacaoAgricolaCreate(
        safra_id=safra.id,  # ← ID válido
        # ...
    )
```

---

### 2.2 Teste Falha com `BusinessRuleError`

**Sintoma:**
```python
E   core.exceptions.BusinessRuleError: Tipo de operação PLANTIO 
    não é permitido na fase COLHEITA
```

**Causas Possíveis:**

1. **Fase da safra incompatível:** Operação não permitida na fase atual
2. **Validação de negócio:** Regra está funcionando corretamente
3. **Teste errado:** Teste esperando comportamento incorreto

**Solução:**

```python
# ❌ ERRADO: Teste esperando sucesso em operação inválida
async def test_operacao_fase_errada(session, tenant_id, talhao_id):
    safra = Safra(
        id=uuid4(),
        tenant_id=tenant_id,
        talhao_id=talhao_id,
        status="COLHEITA"  # ← Fase COLHEITA
    )
    session.add(safra)
    await session.commit()
    
    # Teste vai falhar - PLANTIO não é permitido em COLHEITA
    operacao_create = OperacaoAgricolaCreate(
        safra_id=safra.id,
        tipo="PLANTIO",  # ← Não permitido!
        # ...
    )
    operacao = await service.criar(operacao_create)  # ← Vai lançar erro
    assert operacao.id is not None  # ← Nunca chega aqui

# ✅ CORRETO: Testar que a validação funciona
async def test_operacao_fase_errada_validacao(session, tenant_id, talhao_id):
    safra = Safra(
        id=uuid4(),
        tenant_id=tenant_id,
        talhao_id=talhao_id,
        status="COLHEITA"
    )
    session.add(safra)
    await session.commit()
    
    service = OperacaoService(session, tenant_id)
    
    operacao_create = OperacaoAgricolaCreate(
        safra_id=safra.id,
        tipo="PLANTIO",  # ← Não permitido em COLHEITA
        # ...
    )
    
    # Testar que a validação lança erro
    with pytest.raises(BusinessRuleError) as exc_info:
        await service.criar(operacao_create)
    
    # Validar mensagem de erro
    assert "não é permitido" in str(exc_info.value).lower()
    assert "PLANTIO" in str(exc_info.value)
    assert "COLHEITA" in str(exc_info.value)
```

---

### 2.3 Teste Falha com `AssertionError`

**Sintoma:**
```python
E   AssertionError: assert 5000.0 == 0.0
E    +  where 5000.0 = Despesa.valor_total
```

**Causas Possíveis:**

1. **Webhook criando dados extras:** Operação criando despesa automaticamente
2. **Cálculo incorreto:** Fórmula errada no código
3. **Dados sujos:** Teste anterior não limpou dados

**Solução:**

```python
# ❌ ERRADO: Ignorando que webhook cria despesa
async def test_operacao_sem_despesa(session, tenant_id):
    operacao = await service.criar(operacao_create)
    
    # Teste falha porque webhook criou despesa automaticamente
    despesa = await get_despesa(operacao.id)
    assert despesa is None  # ← Falha! Webhook criou despesa

# ✅ CORRETO: Considerar comportamento do webhook
async def test_operacao_com_despesa_automatica(session, tenant_id):
    operacao = await service.criar(operacao_create)
    
    # Webhook deve criar despesa
    despesa = await get_despesa(operacao.id)
    assert despesa is not None  # ← Esperado
    assert despesa.valor_total == operacao.custo_total
    assert despesa.origem_id == operacao.id
```

---

### 2.4 Teste Falha com `IntegrityError` (Database)

**Sintoma:**
```python
E   sqlalchemy.exc.IntegrityError: FOREIGN KEY constraint failed
```

**Causas Possíveis:**

1. **Referência circular:** Criando dados em ordem errada
2. **Foreign key faltando:** Referenciando ID inexistente
3. **Unique constraint:** Duplicando valor único

**Solução:**

```python
# ❌ ERRADO: Criando operação antes da safra
async def test_ordem_errada(session, tenant_id):
    operacao = OperacaoAgricola(
        id=uuid4(),
        tenant_id=tenant_id,
        safra_id=uuid4(),  # ← ID que não existe!
        # ...
    )
    session.add(operacao)
    await session.commit()  # ← IntegrityError!

# ✅ CORRETO: Criar dependências primeiro
async def test_ordem_correta(session, tenant_id, talhao_id):
    # 1. Criar safra primeiro
    safra = Safra(
        id=uuid4(),
        tenant_id=tenant_id,
        talhao_id=talhao_id,
        # ...
    )
    session.add(safra)
    await session.commit()
    
    # 2. Agora criar operação referenciando safra
    operacao = OperacaoAgricola(
        id=uuid4(),
        tenant_id=tenant_id,
        safra_id=safra.id,  # ← ID válido
        # ...
    )
    session.add(operacao)
    await session.commit()  # ← Sucesso!
```

---

### 2.5 Teste E2E Falha com `TimeoutError`

**Sintoma:**
```
TimeoutError: Timeout 30000ms exceeded waiting for selector
[data-testid="loading"]
```

**Causas Possíveis:**

1. **Loading não aparece:** Elemento já renderizou direto
2. **Loading infinito:** API travou ou erro não tratado
3. **Selector errado:** data-testid incorreto

**Solução:**

```typescript
// ❌ ERRADO: Esperar loading que pode não aparecer
test('deve carregar safras', async ({ page }) => {
  await page.goto('/agricola/safras');
  
  // Loading pode não aparecer se dados estiverem em cache
  await page.waitForSelector('[data-testid="loading"]');
  
  await expect(page.locator('[data-testid="safras-table"]')).toBeVisible();
});

// ✅ CORRETO: Esperar elemento final ou loading opcional
test('deve carregar safras', async ({ page }) => {
  await page.goto('/agricola/safras');
  
  // Esperar tabela OU loading (o que aparecer primeiro)
  await Promise.race([
    page.waitForSelector('[data-testid="loading"]', { state: 'attached' }),
    page.waitForSelector('[data-testid="safras-table"]', { state: 'visible' }),
  ]);
  
  // Aguardar loading sumir (se apareceu)
  await page.waitForSelector('[data-testid="loading"]', { 
    state: 'detached',
    timeout: 10000 
  }).catch(() => {}); // Ignora se não existir
  
  // Validar tabela carregada
  await expect(page.locator('[data-testid="safras-table"]')).toBeVisible();
});
```

---

### 2.6 Teste E2E Falha com `401 Unauthorized`

**Sintoma:**
```
Response 401 Unauthorized from POST /api/v1/auth/login
```

**Causas Possíveis:**

1. **Backend fora do ar:** API não está rodando
2. **Credenciais erradas:** Email/senha inválidos
3. **Tenant inativo:** Conta desativada

**Solução:**

```typescript
// ❌ ERRADO: Credenciais hardcoded sem validar
test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid="email-input"]', 'usuario@fazenda.com');
  await page.fill('[data-testid="password-input"]', 'senha123');
  await page.click('[data-testid="login-button"]');
  // Falha silenciosa - não verifica se login funcionou
});

// ✅ CORRETO: Validar login com sucesso
test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  
  // Preencher credenciais válidas
  await page.fill('[data-testid="email-input"]', 'test@agrosaas.com.br');
  await page.fill('[data-testid="password-input"]', 'password123');
  await page.click('[data-testid="login-button"]');
  
  // Validar que login funcionou
  await page.waitForURL(/\/dashboard/);
  await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
});
```

---

## 3. Debug Passo a Passo

### Backend (pytest)

```bash
# 1. Rodar teste específico em modo verbose
./scripts/run-tests.sh -p tests/agricola/test_operacoes.py -v

# 2. Rodar com print de debug
./scripts/run-tests.sh -p tests/agricola/test_operacoes.py -s

# 3. Rodar com pdb (debug interativo)
./scripts/run-tests.sh -p tests/agricola/test_operacoes.py --pdb

# 4. Adicionar prints no código
async def test_minha_feature(session, tenant_id):
    print(f"\n\n=== DEBUG: tenant_id={tenant_id} ===\n\n")
    
    safra = Safra(...)
    session.add(safra)
    await session.commit()
    
    print(f"\n\n=== DEBUG: safra criada id={safra.id} ===\n\n")
    
    # ... resto do teste
```

### Frontend (Playwright)

```bash
# 1. Rodar em modo debug
./scripts/run-e2e-tests.sh -d

# 2. Abrir UI mode (visual)
./scripts/run-e2e-tests.sh --ui

# 3. Gerar trace para análise
# No playwright.config.ts, adicionar:
use: {
  trace: 'on-first-retry',
}

# 4. Ver trace após falha
pnpm playwright show-trace playwright-results/traces/
```

### Debug com Logs

**Backend:**
```python
import logging

logger = logging.getLogger(__name__)

async def criar(self, operacao_create):
    logger.info(f"Criando operação: {operacao_create.tipo}")
    logger.debug(f"Dados completos: {operacao_create.dict()}")
    
    # Validar fase
    safra = await self.get_safra(operacao_create.safra_id)
    logger.info(f"Safra fase: {safra.status}")
    
    if not self.fase_permite(safra.status, operacao_create.tipo):
        logger.error(f"Fase {safra.status} não permite {operacao_create.tipo}")
        raise BusinessRuleError(...)
    
    # ...
```

**Frontend:**
```typescript
test('deve criar safra', async ({ page }) => {
  // Habilitar logs de console
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.error('PAGE ERROR:', err));
  
  await page.goto('/agricola/safras/novo');
  
  // ... resto do teste
});
```

---

## 4. Padrões de Correção

### Pattern 1: Setup Completo

```python
@pytest.fixture
async def setup_safra_completa(session, tenant_id, talhao_id):
    """Fixture com setup completo de safra para testes."""
    safra = Safra(
        id=uuid4(),
        tenant_id=tenant_id,
        talhao_id=talhao_id,
        ano_safra="2025/26",
        cultura="SOJA",
        status="PLANTIO",
        area_plantada_ha=100.0,
        produtividade_meta_sc_ha=65.0
    )
    session.add(safra)
    await session.commit()
    
    return safra

# Uso nos testes
async def test_operacao_com_setup(session, setup_safra_completa):
    safra = setup_safra_completa
    # Teste usa safra já configurada
```

### Pattern 2: Cleanup Automático

```python
@pytest.fixture
async def session_limpa(engine_memory):
    """Session que limpa dados após cada teste."""
    async_session = async_sessionmaker(engine_memory)
    
    async with async_session() as session:
        yield session
        
        # Cleanup após teste
        await session.rollback()
        # Deletar todas tabelas
        await session.execute(text("DELETE FROM operacoes_agricolas"))
        await session.execute(text("DELETE FROM safras"))
        await session.commit()

# Uso
async def test_limpo(session_limpa, tenant_id):
    # Teste roda com banco limpo
```

### Pattern 3: Validação Múltipla

```python
async def test_validacao_completa(session, tenant_id):
    """Teste valida múltiplos aspectos."""
    # Act
    resultado = await service.processar(dados)
    
    # Assert: Valida estrutura
    assert resultado is not None
    assert hasattr(resultado, 'id')
    
    # Assert: Valida dados
    assert resultado.valor > 0
    assert resultado.data is not None
    
    # Assert: Valida banco de dados
    from_db = await session.get(Model, resultado.id)
    assert from_db is not None
    assert from_db.valor == resultado.valor
    
    # Assert: Valida efeitos colaterais
    webhook_chamado = await get_webhook_log()
    assert webhook_chamado is not None
```

---

## 5. Prevenção de Regressões

### Após Corrigir Bug

```markdown
## Checklist Pós-Correção

- [ ] Bug reproduzido e entendido
- [ ] Correção implementada
- [ ] Teste que falha agora passa
- [ ] Novo teste adicionado (se não existia)
- [ ] Testes relacionados rodam
- [ ] Coverage não diminuiu
- [ ] Code review feito
- [ ] Changelog atualizado
```

### Adicionar Teste de Regressão

```python
# tests/regressao/test_bug_123_operacao_fase.py
"""
Teste de regressão para Bug #123

Problema: Operação era criada mesmo com fase incompatível
Correção: Adicionar validação de fase antes de criar operação
"""

class TestBug123OperacaoFaseInvalida:
    """Garante que bug #123 não volte a acontecer."""
    
    @pytest.mark.asyncio
    async def test_operacao_nao_cria_com_fase_invalida(
        self, session, tenant_id, talhao_id
    ):
        """Operação PLANTIO em safra COLHEITA deve falhar."""
        # Setup
        safra = Safra(
            id=uuid4(),
            tenant_id=tenant_id,
            talhao_id=talhao_id,
            status="COLHEITA"  # ← Fase que causa bug
        )
        session.add(safra)
        await session.commit()
        
        # Act & Assert
        service = OperacaoService(session, tenant_id)
        
        with pytest.raises(BusinessRuleError) as exc_info:
            await service.criar(OperacaoAgricolaCreate(
                safra_id=safra.id,
                tipo="PLANTIO",  # ← Não permitido
                # ...
            ))
        
        # Validar mensagem específica do bug
        assert "não é permitido" in str(exc_info.value)
        assert "PLANTIO" in str(exc_info.value)
        assert "COLHEITA" in str(exc_info.value)
```

---

## 📊 Matriz de Decisão

| Sintoma | Provável Causa | Ação |
|---------|----------------|------|
| `EntityNotFoundError` | Tenant isolation ou dados não criados | Verificar tenant_id e setup |
| `BusinessRuleError` | Validação de negócio | Validar se teste ou código está errado |
| `AssertionError` | Valor inesperado | Verificar cálculo ou webhook |
| `IntegrityError` | Foreign key ou unique constraint | Verificar ordem de criação |
| `TimeoutError` | Loading ou selector errado | Ajustar espera ou selector |
| `401 Unauthorized` | Auth ou backend fora | Verificar credenciais e API |

---

## 🔗 Links Úteis

- [Plano de Testes](./PLANO_TESTES_QA.md)
- [Guia de Testes](./GUIA_TESTES.md)
- [Checklist Sprint](./CHECKLIST_TESTES_SPRINT.md)

---

**Última Atualização:** 2026-03-31
**Responsável:** Tech Lead
