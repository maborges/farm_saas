ok# Sprint Overview — Refatoração Estrutura Organizacional

**Projeto:** AgroSaaS — Refatoração Estrutura Organizacional  
**Referência:** [Brainstorm](../brainstorm-refatoracao-estrutura.md)  
**Total estimado:** ~18 dias de desenvolvimento

---

## Mapa de Dependências

```
BL-01 (Identidade)
  └── BL-02 (Território)
  │     └── BL-07 (Segurança — gaps)
  └── BL-03 (Acesso)
  │     └── BL-07 (Segurança — gaps)
  └── BL-05 (Billing)
  └── BL-06 (Integrações) ──┐
                             └── BL-04 (Onboarding)
                             └── BL-08 (Frontend)
```

---

## Sprint 1 — Fundação (dias 1–5)

**Objetivo:** Schema limpo no banco, modelos funcionando, migrations aplicadas.  
**Frentes paralelas possíveis:** BL-01 + BL-06 podem andar em paralelo.

| Backlog | Escopo | Dias |
|---|---|---|
| **BL-01** | Model Usuario, Assinatura, Plano — migrations | 3d |
| **BL-06** | Integrações CEP, CNPJ/CPF (sem CAR ainda) | 2d |

**Entregável:** Banco refatorado, usuario/assinatura funcionando, lookups CEP/CNPJ prontos.

---

## Sprint 2 — Território & Acesso (dias 6–12)

**Objetivo:** Hierarquia territorial completa, controle de acesso explícito por propriedade.  
**Frentes paralelas possíveis:** BL-02 + BL-03 em paralelo. BL-07 ao final.

| Backlog | Escopo | Dias |
|---|---|---|
| **BL-02** | Propriedade, Gleba, UnidadeOperacional — models, services, routers | 4d |
| **BL-03** | AssinaturaUsuario, PropriedadeAcesso, convites — models, services, routers | 3d |
| **BL-07** | Gaps de segurança: require_propriedade_access, check_limit, RLS, testes | 2d |

**Entregável:** API completa de território e acesso, segurança fechada.

---

## Sprint 3 — Frontend & Integrações (dias 13–18)

**Objetivo:** UI funcional para gestão de propriedades, equipe e onboarding.  
**Frentes paralelas possíveis:** BL-08 + BL-06(CAR) em paralelo. BL-04 ao final.

| Backlog | Escopo | Dias |
|---|---|---|
| **BL-08** | Páginas Settings/Propriedades, Estrutura, Equipe/Acessos | 4d |
| **BL-06** | Integração CAR/SICAR | 1d |
| **BL-05** | Billing/limites: check_limit, uso do plano, banner UI | 2d |
| **BL-04** | Wizard de Onboarding (front + back) | 2d |

**Entregável:** Sistema funcional end-to-end — cadastro, estrutura, acessos, onboarding.

---

## Frentes de Trabalho Independentes

Para trabalho paralelo entre times:

| Frente | Responsável | Backlogs |
|---|---|---|
| **Backend Core** | Dev 1 | BL-01 → BL-02 → BL-07 |
| **Backend Acesso/Billing** | Dev 2 | BL-03 → BL-05 |
| **Backend Integrações** | Dev 3 | BL-06 (CEP+CNPJ+CAR) |
| **Frontend** | Dev 4 | BL-08 (aguarda Sprint 2) |
| **Frontend Onboarding** | Dev 5 | BL-04 (aguarda BL-06) |

---

## Definition of Done (DoD)

Cada US está "done" quando:
- [ ] Código implementado seguindo padrões (BaseService, async/await, Pydantic v2)
- [ ] Teste de isolamento de tenant passa
- [ ] Schemas Zod alinhados com Pydantic
- [ ] Sem raw SQLAlchemy em routers
- [ ] PR aprovado com revisão

---

## Backlog Futuro (Fase 2 — fora do escopo desta refatoração)

- BL-06B: Integração CCIR (INCRA)
- BL-06C: Integração NIRF (Receita Federal)
- BL-06D: Integração SIGEF (georreferenciamento)
- BL-06E: Sincronização CAR periódica (cron)
- BL-02B: Georreferenciamento de talhões (GeoJSON editor)
- BL-03B: Exportação CSV de acessos
- BL-08B: Drag-and-drop na ÁrvoreÁrea
