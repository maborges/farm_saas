---
trigger: glob: services/api-*/**/*.py
---

# AGRO-02: Backend Core (FastAPI & Domain Logic)

**CONTEXTO:** Garantir performance async, código limpo e conformidade REST entre microsserviços.

### 1. PERFORMANCE ASYNC (Lei 02)
- **Async First**: TODAS as rotas e services DEVEM ser assíncronas (`async def`). DB, Redis e todas as APIs externas (Supabase, Stripe, OpenAI, Fal.ai) DEVEM ser obrigatoriamente acessadas via `await` — nunca bloqueantes.
- **Conexões Resilientes**: Conexões com banco banco de dados e APIs externas DEVEM ter timeout explicitamente configurado.
- **Proibição Bloqueante**: NUNCA usar `time.sleep()` ou `requests`. Use `asyncio.sleep()` e `httpx.AsyncClient()`.
- **Background Tasks**: Operações longas delegar para Celery Workers. Emissão de dados de IA via *Streaming* deve utilizar SSE (Server-Sent Events) sem aguardar a resposta completa.

### 2. ARQUITETURA LIMPA & TIPAGEM
- **Organização por Domínio**: Cada módulo com seus routes, service, schemas — nunca misturar domínios. Um arquivo, uma responsabilidade.
- **Tipagem Obrigatória**: Type hints obrigatórios em todas as funções e variáveis em Python. Sem uso de `Any` genérico.
- **Routers**: Apenas validação de input (Pydantic), sem lógica de negócios.
- **Models vs Schemas**: NUNCA retornar models SQLAlchemy diretamente. Sempre serializar via schemas Pydantic.

### 3. PADRÃO REST & ERROR HANDLING
- **Exceptions Limpas**: NUNCA retornar `None` ou `null` para indicar erro — use *Exceptions* e mantenha a lógica principal limpa. NUNCA passar None/null como argumento padrão mutável.
- **Tipos de Execptions**: Try/except DEVE ser focado e específico (ex: `except ValueError`, `except HTTPException`). É PROIBIDO o uso de `except Exception:` genérico (a não ser num catch-all em middleware global).
- **Erros de Domínio**: Erros de negócios DEVEM usar exceções customizadas (ex: `SubscriptionExpiredError`, `QuotaExceededError`).
- **Zero Swallow**: Nunca capturar exceção sem logar (`logger.bind(request_id=...)`).

### 4. AGENTES DE IA (LANGGRAPH)
- **State Machine**: Agentes DEVEM ser implementados estruturalmente com LangGraph (state machine, nós e transições explícitas).
- **Responsabilidade Única**: Cada nó do grafo DEVE ter responsabilidade única e saída rigorosamente tipada.
- **Structured Output**: Respostas de agente usam *Structured Output* por via de modelos Pydantic — nunca responder texto livre para geração de dados estruturados.
- **Isolamento de Erros**: Configurar *error handling* individual nas *Tools* e *Nodes*; a falha de uma tool menor não deve derrubar globalmente o grafo. Prompts NUNCA podem estar "hardcoded" na lógica do nó, residindo em arquivos dedicados.

### 5. MODULARIDADE INTER-SERVIÇOS
- Use `httpx` com retries (tenacity) para comunicação entre microsserviços.
- Prefira eventos (Redis Pub/Sub) para ações que não precisam de resposta imediata (ex: Alerta de peso baixo).

```python
# Padrão Service
class AnimalService(BaseService[Animal]):
    async def registrar_pesagem(self, animal_id: UUID, peso: float):
        # Lógica de negócio aqui
        pass
```
