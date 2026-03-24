# 🎯 Próximos Passos - Modularização AgroSaaS

## ✅ O Que Foi Feito

### 1. Infraestrutura Base de Modularização
- ✅ **Constantes de Módulos** ([core/constants.py](services/api/core/constants.py))
  - 25+ módulos definidos com IDs, preços e metadados
  - Sistema de validação de dependências
  - Cálculo automático de preços

- ✅ **Sistema de Feature Gates** ([core/dependencies.py](services/api/core/dependencies.py))
  - `require_module()` - Gate para módulo único
  - `require_any_module()` - Gate para qualquer módulo
  - `require_all_modules()` - Gate para todos os módulos
  - Validação em 2 níveis (JWT + Database)

- ✅ **Template de Módulo** ([docs/architecture/MODULO_TEMPLATE.md](docs/architecture/MODULO_TEMPLATE.md))
  - Estrutura padrão completa
  - Exemplos de código
  - Boas práticas documentadas

- ✅ **Script Gerador** ([services/api/scripts/create_module.py](services/api/scripts/create_module.py))
  - Criação automática de estrutura
  - Arquivos pré-populados
  - Comandos de próximos passos

- ✅ **Plano de Modularização** ([docs/PLANO_MODULARIZACAO.md](docs/PLANO_MODULARIZACAO.md))
  - Cronograma completo
  - 20 módulos mapeados
  - Processo detalhado

- ✅ **Módulo A1 (Exemplo)** ([services/api/agricola/a1_planejamento/](services/api/agricola/a1_planejamento/))
  - Estrutura criada
  - Health check funcional
  - Feature gate implementado

## 🚀 Próximas Ações

### Fase 1: Validar a Infraestrutura (1-2 dias)

#### 1.1 Testar Feature Gates

```bash
cd services/api

# Iniciar servidor
source .venv/bin/activate
uvicorn main:app --reload
```

Criar um plano de testes no backoffice:

```python
# No shell interativo Python
from core.models.billing import PlanoAssinatura
from core.constants import Modulos

# Criar plano de teste com A1
plano_teste = PlanoAssinatura(
    nome="Teste A1",
    modulos_inclusos=[Modulos.CORE, Modulos.AGRICOLA_PLANEJAMENTO],
    preco_mensal=199.0
)
```

Testar endpoint:
```bash
# Deve retornar 200 se tiver módulo, 402 se não tiver
GET /api/v1/agricola/planejamento/health
```

#### 1.2 Registrar Módulo A1 no main.py

```python
# services/api/main.py

# Adicionar import
from agricola.a1_planejamento.router import router as router_a1_planejamento

# Adicionar registro (junto com outros routers)
app.include_router(router_a1_planejamento, prefix="/api/v1")
```

#### 1.3 Testar Sistema de Billing

Validar que os planos estão pegando os módulos corretos:

```sql
-- Ver planos e módulos
SELECT nome, modulos_inclusos, preco_mensal
FROM planos_assinatura;

-- Ver assinaturas ativas
SELECT t.nome_fantasia, p.nome, p.modulos_inclusos
FROM assinaturas_tenant AS a
JOIN tenants AS t ON a.tenant_id = t.id
JOIN planos_assinatura AS p ON a.plano_id = p.id
WHERE a.status = 'ATIVA';
```

### Fase 2: Implementar Módulos Agrícolas (2 semanas)

#### 2.1 Módulo A1 - Planejamento (3 dias - PRIORITÁRIO)

**Dia 1: Models e Schemas**
```bash
# Editar:
services/api/agricola/a1_planejamento/models.py
services/api/agricola/a1_planejamento/schemas.py
```

Implementar:
- Model `Safra` (completo)
- Model `OrcamentoSafra`
- Schemas CRUD

**Dia 2: Services e Lógica de Negócio**
```bash
# Editar:
services/api/agricola/a1_planejamento/services.py
```

Implementar:
- `SafraService.criar_safra()`
- `SafraService.listar_safras()`
- `SafraService.buscar_safra()`
- `SafraService.atualizar_safra()`
- Validações de negócio

**Dia 3: Router e Testes**
```bash
# Editar:
services/api/agricola/a1_planejamento/router.py
services/api/agricola/a1_planejamento/tests/test_services.py
```

Implementar:
- Todos os endpoints
- Testes unitários
- Testes de integração

**Migration:**
```bash
cd services/api
alembic revision --autogenerate -m "add_a1_planejamento_safras_orcamentos"
alembic upgrade head
```

#### 2.2 Módulo A2 - Caderno de Campo (4 dias)

Repetir processo:
1. Criar estrutura com script
2. Implementar models (OrdemServico, Apontamento)
3. Implementar services
4. Criar endpoints com feature gate
5. Testes
6. Migration

#### 2.3 Módulos A3, A4, A5 (seguir mesmo padrão)

### Fase 3: Frontend - Adaptar para Módulos (paralelo)

#### 3.1 Criar Hook de Feature Gates

```typescript
// apps/web/src/hooks/use-has-module.ts
import { useAppStore } from '@/lib/stores/app-store'

export function useHasModule(moduleId: string): boolean {
  const { modules } = useAppStore()
  return modules.includes(moduleId)
}

export function useHasAnyModule(...moduleIds: string[]): boolean {
  const { modules } = useAppStore()
  return moduleIds.some(id => modules.includes(id))
}
```

#### 3.2 Componente de Gate no Frontend

```typescript
// apps/web/src/components/shared/module-gate.tsx
"use client"

import { useHasModule } from '@/hooks/use-has-module'

interface ModuleGateProps {
  moduleId: string
  children: React.ReactNode
  fallback?: React.ReactNode
}

export function ModuleGate({ moduleId, children, fallback }: ModuleGateProps) {
  const hasModule = useHasModule(moduleId)

  if (!hasModule) {
    return fallback || (
      <div className="p-4 border rounded bg-yellow-50">
        <h3>Módulo não contratado</h3>
        <p>Faça upgrade do seu plano para acessar esta funcionalidade.</p>
      </div>
    )
  }

  return <>{children}</>
}
```

#### 3.3 Uso no Frontend

```typescript
// apps/web/src/app/(dashboard)/agricola/planejamento/page.tsx
import { ModuleGate } from '@/components/shared/module-gate'
import { Modulos } from '@/lib/constants/modulos'

export default function PlanejamentoPage() {
  return (
    <ModuleGate moduleId={Modulos.AGRICOLA_PLANEJAMENTO}>
      <div>
        <h1>Planejamento de Safra</h1>
        {/* Conteúdo do módulo */}
      </div>
    </ModuleGate>
  )
}
```

### Fase 4: Backoffice - Gestão de Módulos (1 semana)

#### 4.1 Tela de Catálogo de Módulos

Criar no admin:
- Lista todos os módulos disponíveis
- Agrupa por categoria
- Mostra preço e dependências
- Permite criar pacotes customizados

#### 4.2 Tela de Gestão de Planos

- CRUD de planos
- Seleção visual de módulos
- Cálculo automático de preço
- Validação de dependências

#### 4.3 Dashboard de Uso por Módulo

Implementar telemetria:
```python
# core/models/telemetry.py
class ModuloUsageMetric(Base):
    tenant_id: Mapped[uuid.UUID]
    modulo_id: Mapped[str]
    endpoint: Mapped[str]
    data_acesso: Mapped[datetime]
```

Middleware para registrar acessos:
```python
# core/middleware/telemetry.py
async def log_module_usage(request, call_next):
    # Se rota tem feature gate, registrar uso
    pass
```

## 📋 Checklist de Ações Imediatas

### Hoje (Dia 1)
- [ ] Ler este documento completo
- [ ] Revisar [core/constants.py](services/api/core/constants.py)
- [ ] Testar feature gates com Postman/Insomnia
- [ ] Registrar módulo A1 no main.py
- [ ] Testar endpoint `/api/v1/agricola/planejamento/health`

### Esta Semana (Dias 2-5)
- [ ] Implementar completamente módulo A1
  - [ ] Models de Safra e OrcamentoSafra
  - [ ] Services com toda lógica de negócio
  - [ ] Endpoints CRUD completos
  - [ ] Testes com 80%+ cobertura
- [ ] Criar migration e aplicar
- [ ] Documentar no README do módulo
- [ ] Code review

### Próxima Semana (Dias 6-10)
- [ ] Implementar módulo A2 (Caderno de Campo)
- [ ] Implementar módulo A3 (Defensivos)
- [ ] Começar frontend (Module Gates)

### Próximas 2 Semanas (Dias 11-20)
- [ ] Completar todos módulos agrícolas (A1-A5)
- [ ] Implementar catálogo de módulos no backoffice
- [ ] Criar tela de gestão de planos

## 🛠️ Comandos Úteis

### Criar novo módulo
```bash
cd services/api

# Exemplo para P1 - Controle de Rebanho
python3 scripts/create_module.py \
  --modulo P1_REBANHO \
  --dominio pecuaria
```

### Rodar testes
```bash
# Todos os testes
pytest

# Módulo específico
pytest agricola/a1_planejamento/tests/ -v

# Com cobertura
pytest --cov=agricola/a1_planejamento --cov-report=html
```

### Migrations
```bash
# Criar migration
alembic revision --autogenerate -m "descricao"

# Aplicar
alembic upgrade head

# Reverter
alembic downgrade -1
```

### Verificar feature gates
```bash
# Ver todos os módulos de um tenant
python3 -c "
from core.models.billing import PlanoAssinatura
from core.database import async_session_maker
import asyncio

async def check():
    async with async_session_maker() as session:
        plano = await session.get(PlanoAssinatura, 'uuid-do-plano')
        print(plano.modulos_inclusos)

asyncio.run(check())
"
```

## 📚 Documentação de Referência

### Arquitetura
- [Manual de Desenvolvimento](docs/architecture/AgroSaaS-Manual.md)
- [Template de Módulo](docs/architecture/MODULO_TEMPLATE.md)
- [Plano de Modularização](docs/PLANO_MODULARIZACAO.md)

### Código
- [Constantes de Módulos](services/api/core/constants.py)
- [Feature Gates](services/api/core/dependencies.py)
- [Exemplo Módulo A1](services/api/agricola/a1_planejamento/)

### Requisitos
- [Requisitos Funcionais](docs/functional_requirements/funtionals.md)

## 🆘 Troubleshooting

### Erro: "Módulo não contratado" (402)
- Verificar se o plano do tenant tem o módulo em `modulos_inclusos`
- Verificar se a assinatura está `ATIVA`
- Verificar JWT (campo `modules`)

### Erro: Import de core.constants
- Certificar que está rodando de dentro de `services/api/`
- Verificar PYTHONPATH
- Usar `python3 -m <comando>` ao invés de path direto

### Migration não detecta mudanças
```bash
# Forçar
alembic revision -m "manual" --autogenerate
alembic upgrade head --sql  # Ver SQL antes de aplicar
```

## 🎯 Meta de 30 Dias

**Objetivo:** Sistema 100% modularizado e funcional

- [ ] 20 módulos criados
- [ ] Todos com feature gates
- [ ] 80%+ cobertura de testes
- [ ] Frontend adaptado
- [ ] Backoffice com gestão de módulos
- [ ] 5+ pacotes pré-montados
- [ ] Documentação completa

## 🚀 Vamos Começar!

```bash
# 1. Ativar ambiente
cd /opt/lampp/htdocs/farm/services/api
source .venv/bin/activate

# 2. Registrar módulo A1 no main.py
# (editar manualmente)

# 3. Testar
uvicorn main:app --reload

# 4. Acessar
curl http://localhost:8000/api/v1/agricola/planejamento/health
```

**Boa sorte! 🎉**

---

**Dúvidas?** Consulte a documentação ou abra uma issue.
**Criado em:** 2026-03-10
