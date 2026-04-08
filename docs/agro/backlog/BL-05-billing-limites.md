# BL-05 — Billing & Limites do Plano

**Módulo:** core/billing  
**Frente:** Backend  
**Dependências:** BL-01  
**Estimativa:** 2 dias

---

## Contexto

O plano contratado define limites que são compartilhados por toda a assinatura:
- `max_propriedades` — quantidade máxima de Propriedades ativas
- `max_usuarios_simultaneos` — usuários com acesso ativo simultâneo

Validação deve ocorrer em runtime, não só no frontend.

---

## User Stories

### US-05.1 — Limite de Propriedades
**Como** sistema,  
**quero** impedir a criação de propriedades além do limite do plano,  
**para** garantir que os recursos contratados sejam respeitados.

**Critérios de aceite:**
- [ ] `check_propriedade_limit()` executado antes de criar Propriedade
- [ ] Retorna `BusinessRuleError` (422) se limite atingido
- [ ] Mensagem clara: "Limite de X propriedades atingido. Faça upgrade do plano."
- [ ] Propriedades inativas não contam no limite
- [ ] Frontend exibe banner: "X de Y propriedades usadas"

---

### US-05.2 — Visualização de Uso do Plano
**Como** gestor da assinatura,  
**quero** ver o quanto estou usando do meu plano,  
**para** saber quando preciso fazer upgrade.

**Critérios de aceite:**
- [ ] `GET /billing/uso` retorna: propriedades usadas/limite, usuários ativos/limite
- [ ] Banner de alerta ao atingir 80% do limite
- [ ] Banner de bloqueio ao atingir 100%
- [ ] Link direto para upgrade no banner

---

### US-05.3 — Upgrade de Plano
**Como** gestor,  
**quero** fazer upgrade do meu plano diretamente no sistema,  
**para** aumentar os limites sem sair da plataforma.

**Critérios de aceite:**
- [ ] Página `/settings/billing` exibe plano atual e opções de upgrade
- [ ] Integração com Stripe/Asaas (já existe — adaptar)
- [ ] Após upgrade, limites atualizados imediatamente

---

## Tarefas Técnicas

### Backend
- [ ] Refatorar model `PlanoAssinatura` — adicionar `max_propriedades`, `max_usuarios_simultaneos`
- [ ] Função `check_propriedade_limit(tenant_id, session)` → `BusinessRuleError` se excedido
- [ ] Função `get_uso_plano(tenant_id, session)` → dict com contadores
- [ ] Endpoint `GET /billing/uso` — retorna uso atual vs limites
- [ ] Migration: adicionar colunas ao `planos`
- [ ] Hook no `PropriedadeService.create()` para verificar limite

### Frontend
- [ ] Componente `PlanUsageBanner` — barra de progresso com alertas
- [ ] Integrar banner na página `/settings/propriedades`
- [ ] Adaptar página `/settings/billing` para novo modelo
