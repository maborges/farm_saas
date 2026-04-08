# Core — Workflow de Implantação

## Visão Geral
O Core é obrigatório para todos os tenants. Deve ser implantado antes de qualquer outro módulo.

## Pré-requisitos
- Infraestrutura PostgreSQL provisionada
- Tenant criado via onboarding

## Sequência de Implantação

### Fase 1 — Identidade e Acesso (Semana 1)
1. Configurar autenticação JWT
2. Criar perfis de acesso (is_owner, admin, operador, viewer)
3. Configurar RBAC por fazenda (FazendaUsuario.perfil_fazenda_id)

### Fase 2 — Propriedade (Semana 1-2)
1. Cadastrar fazendas/propriedades
2. Importar talhões (shapefile/KML ou manual)
3. Configurar áreas rurais e módulos ativos

### Fase 3 — Configurações Globais (Semana 2)
1. Configurar SMTP / notificações
2. Definir integrações (Stripe/Asaas para billing)
3. Habilitar módulos contratados (feature gates)

### Fase 4 — Multipropriedade (se aplicável)
1. Criar grupos de fazendas
2. Configurar permissões cross-fazenda
3. Testar isolamento de tenant (RLS)

## Critérios de Conclusão
- [ ] Login funcionando com MFA opcional
- [ ] Pelo menos 1 fazenda cadastrada
- [ ] Pelo menos 1 talhão mapeado
- [ ] Módulos contratados habilitados
- [ ] Notificações SMTP testadas

## Armadilhas Comuns
- Nunca confiar no `tenant_id` vindo do frontend — usar `get_tenant_id()` dependency
- RLS não funciona em SQLite (apenas PostgreSQL)
- Após mudanças em `main.py` (CORS), reiniciar o servidor
