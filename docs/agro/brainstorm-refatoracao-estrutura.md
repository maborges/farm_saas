# Brainstorm — Refatoração Estrutura Organizacional

**Data:** 2026-04-07  
**Status:** Aprovado para implementação  
**Abordagem escolhida:** Hierarquia Flexível (B)

---

## Decisões Conceituais

### Terminologia
- **"Propriedade"** como termo âncora (neutro — cobre fazenda/sítio/arrendamento, próximo ao MAPA/SISBOV)
- Identificadores regulatórios (CAR, NIRF, CCIR) são campos da Propriedade, não do Produtor

### Modelo de Identidade
```
Usuario (global — CPF/email únicos na plataforma)
  └── AssinaturaUsuario (pertence à assinatura/tenant por convite)
        └── PropriedadeAcesso (acesso explícito por propriedade)
              ├── perfil_id (permissões)
              └── vigencia_inicio / vigencia_fim (opcional)
```

### Hierarquia Territorial
```
Tenant (= Produtor — isolado por assinatura)
  └── Propriedade ← limite do plano, acesso explícito por usuário
        └── Gleba (opcional)
              └── UnidadeOperacional: Talhão | Piquete | ÁreaFuncional (opcional)
```

### Modelo de Assinatura
- Tenant = Assinatura = Produtor (GrupoRural)
- Um usuário pode ter múltiplas assinaturas (múltiplos produtores)
- tenant-switcher já trata isso na UI
- Plano define: `max_propriedades`, `max_usuarios_simultaneos`
- Limites compartilhados entre todas as Propriedades da assinatura

### Integrações Regulatórias — MVP
- ✅ CEP/IBGE — preenche município/UF automaticamente
- ✅ CNPJ/CPF (Receita Federal) — valida produtor ao criar assinatura
- ✅ CAR/SICAR (IBAMA) — valida e importa dados da propriedade

### Integrações Regulatórias — Fase 2
- CCIR (INCRA), NIRF (Receita), SIGEF, CIF/MAPA

---

## Schema Resumido

### Plataforma (sem tenant_id)
- `usuarios` — CPF/email únicos globais
- `planos` — max_propriedades, max_usuarios_simultaneos, tier
- `assinaturas` — tenant_id, usuario_id (gestor), plano_id

### Territorial (com tenant_id)
- `propriedades` — nome, tipo, área, localização, CAR, NIRF, CCIR, SIGEF
- `glebas` — opcional, subdivisão da propriedade
- `unidades_operacionais` — talhão | piquete | área_funcional

### Acesso
- `assinatura_usuarios` — vínculo usuário ↔ assinatura
- `propriedade_acessos` — acesso explícito por propriedade + vigência

---

## Gaps de Segurança a Implementar
1. `require_propriedade_access()` — nova dependency
2. `check_propriedade_limit()` — ao criar Propriedade
3. Verificação de vigência em runtime (não só no login)
4. Atualizar `_resolve_grupo_id` de `Fazenda` → `Propriedade`

---

## Backlogs Gerados
- [BL-01 Identidade & Usuário](backlog/BL-01-identidade-usuario.md)
- [BL-02 Território](backlog/BL-02-territorio.md)
- [BL-03 Acesso & Permissões](backlog/BL-03-acesso-permissoes.md)
- [BL-04 Onboarding](backlog/BL-04-onboarding.md)
- [BL-05 Billing & Limites](backlog/BL-05-billing-limites.md)
- [BL-06 Integrações Regulatórias](backlog/BL-06-integracoes-regulatorias.md)
- [BL-07 Segurança](backlog/BL-07-seguranca.md)
- [BL-08 Frontend](backlog/BL-08-frontend.md)
- [Sprint Overview](sprints/SPRINT-OVERVIEW.md)
