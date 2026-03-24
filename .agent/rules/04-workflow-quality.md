---
trigger: always_on
---

# AGRO-04: Workflow, Qualidade e Qualidade

**CONTEXTO:** Disciplina de engenharia para um SaaS modular e resiliente.

### 1. TDD & TESTES (Lei 10)
- **Red/Green/Refactor**: Escreva o teste antes da implementação da lógica de negócio.
- **Cobertura**: Focar em edge cases (null, empty array, limites numéricos de pesagem).
- **Integridade**: `api-pecuaria` deve ter testes que simulam falha na `api-financeiro` se houver dependência.

### 2. GIT & COMMITS (Lei 12)
- **Conventional Commits**: `feat(rebanho): ...`, `fix(auth): ...`, `refactor(core): ...`.
- **Atomic Commits**: Cada commit resolve uma e apenas uma coisa.

### 3. DEPENDÊNCIAS & HIGIENE (Lei 09)
- **Freshness**: Apenas pacotes com última release < 12 meses.
- **Anti-Vazamento**: NUNCA commitar `.env`. Use `scripts/check-secrets.sh` se disponível.
- **Zero redundância**: Use a stdlib de Python/JS sempre que possível.

### 4. ISOLAMENTO DE AMBIENTE (Lei 13)
- **Bancos Separados**: Dev, Staging e Prod NUNCA compartilham DB.
- **Check de Prod**: Scripts destrutivos DEVEM validar `APP_ENV != 'production'`.

### 5. CLEAN CODE E ESTRUTURA
- **Docstrings & Intenção**: Toda função de service DEVE ter docstring detalhando *Args*, *Return* e *Raises*. Nomes DEVEM revelar intenção real (ex: `is_active_subscription` > `flag`). Use Substantivos para Classes e Verbos Descritivos para Funções. Evitar `Manager`, `handle()`, `do()`. NUNCA use abreviações ambíguas (`usr`, `tmp`).
- **Funções Atômicas**: Funções DEVEM fazer **UMA** coisa. Máximo de 20 linhas e estritamente limite de 3 argumentos por função (acima disso, agrupar em objeto/dataclass/Pydantic model). NÃO gerar side-effects ocultos como alteração de estado global.
- **Lei de Demeter**: NUNCA encadear acessos excessivos (ex: `a.get_b().get_c()`). Crie um método direto via fachada ou service.
- **Código Limpo Limpo**: Funções não usadas, imports não usados e variáveis comentadas DEVEM ser **removidos**, nunca apenas comentados de código para "talvez usar depois".

### 6. DOCUMENTAÇÃO NO README
- **Funcionalidades e Fluxos**: Toda feature nova concluída DEVE ser explicada no `README.md` relatando: *Nome da Feature*, *Descrição curta* e *Fluxo de funcionamento*.
- **Bugfixes Focados**: Todo fix relevante também tem registro de documentação com: *o problema corrigido* e o *comportamento esperado*.
- **Separação de Preocupações**: O README detém apenas fluxo funcional, na seção `## Features`. Não poluir README com refatorações internas ou ajustes estéticos triviais.

```bash
# Exemplo de Commit
git commit -m "feat(pecuaria): add birth registration logic with business validation"
```
