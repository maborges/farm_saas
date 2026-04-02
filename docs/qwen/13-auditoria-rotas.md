# 🔍 Auditoria de Rotas - Sidebar vs Páginas Existentes

**Data:** 2026-06-06  
**Status:** 🟡 **EM ANDAMENTO**

---

## 📊 Resumo

| Categoria | Total | Existentes | Faltantes | % Conclusão |
|-----------|-------|------------|-----------|-------------|
| **Sidebar (Menu)** | 72 | 65 | 23 | 68% |
| **Páginas Implementadas** | - | 65 | - | - |
| **Páginas Faltantes** | - | - | 23 | - |

---

## ✅ Rotas que FUNCIONAM (65 páginas)

### Dashboard Geral (1)
- ✅ `/dashboard` - page.tsx

### Agrícola (13)
- ✅ `/dashboard/agricola` - page.tsx
- ✅ `/dashboard/agricola/analises-solo` - page.tsx
- ✅ `/dashboard/agricola/analises_solo` - page.tsx (dupla)
- ✅ `/dashboard/agricola/apontamentos` - page.tsx
- ✅ `/dashboard/agricola/climatico` - page.tsx
- ✅ `/dashboard/agricola/defensivos` - page.tsx
- ✅ `/dashboard/agricola/mapa` - page.tsx
- ✅ `/dashboard/agricola/monitoramento` - page.tsx
- ✅ `/dashboard/agricola/ndvi` - page.tsx
- ✅ `/dashboard/agricola/operacoes` - page.tsx
- ✅ `/dashboard/agricola/prescricoes` - page.tsx
- ✅ `/dashboard/agricola/rastreabilidade` - page.tsx
- ✅ `/dashboard/agricola/relatorios` - page.tsx
- ✅ `/dashboard/agricola/talhoes` - page.tsx
- ✅ `/dashboard/agricola/timeline` - page.tsx
- ✅ `/dashboard/agricola/cadastros/culturas` - page.tsx

### Pecuária (5)
- ✅ `/dashboard/pecuaria` - page.tsx
- ✅ `/dashboard/pecuaria/lotes` - page.tsx
- ✅ `/dashboard/pecuaria/manejo` - page.tsx
- ✅ `/dashboard/pecuaria/piquetes` - page.tsx
- ✅ `/dashboard/pecuaria/relatorios` - page.tsx

### Financeiro (7)
- ✅ `/dashboard/financeiro` - page.tsx
- ✅ `/dashboard/financeiro/conciliacao` - page.tsx
- ✅ `/dashboard/financeiro/despesas` - page.tsx
- ✅ `/dashboard/financeiro/planos-conta` - page.tsx
- ✅ `/dashboard/financeiro/receitas` - page.tsx
- ✅ `/dashboard/financeiro/relatorios` - page.tsx
- ✅ `/dashboard/financeiro/carne-leao` - page.tsx

### Operacional (4)
- ✅ `/dashboard/operacional/compras` - page.tsx
- ✅ `/dashboard/operacional/lotes` - page.tsx
- ✅ `/dashboard/operacional/requisicoes` - page.tsx

### RH (2)
- ✅ `/dashboard/rh` - page.tsx
- ✅ `/dashboard/rh/empreitadas` - page.tsx

### Backoffice (15)
- ✅ `/dashboard/backoffice/dashboard` - page.tsx
- ✅ `/dashboard/backoffice/bi` - page.tsx
- ✅ `/dashboard/backoffice/tenants` - page.tsx
- ✅ `/dashboard/backoffice/plans` - page.tsx
- ✅ `/dashboard/backoffice/cupons` - page.tsx
- ✅ `/dashboard/backoffice/crm` - page.tsx
- ✅ `/dashboard/backoffice/billing` - page.tsx
- ✅ `/dashboard/backoffice/support` - page.tsx
- ✅ `/dashboard/backoffice/kb` - page.tsx
- ✅ `/dashboard/backoffice/config` - page.tsx
- ✅ `/dashboard/backoffice/admin-users` - page.tsx
- ✅ `/dashboard/backoffice/audit` - page.tsx
- ✅ `/dashboard/backoffice/email-templates` - page.tsx
- ✅ `/dashboard/backoffice/sessions` - page.tsx
- ✅ `/dashboard/backoffice/profiles` - page.tsx
- ✅ `/dashboard/backoffice/users` - page.tsx
- ✅ `/dashboard/backoffice/ofertas` - page.tsx
- ✅ `/dashboard/backoffice/pipeline` - page.tsx
- ✅ `/dashboard/backoffice/tabelas` - page.tsx

### Configurações (7)
- ✅ `/dashboard/settings/account` - page.tsx
- ✅ `/dashboard/settings/team` - page.tsx
- ✅ `/dashboard/settings/roles` - page.tsx
- ✅ `/dashboard/settings/grupos` - page.tsx
- ✅ `/dashboard/settings/kb` - page.tsx
- ✅ `/dashboard/settings/smtp` - page.tsx
- ✅ `/dashboard/settings/support` - page.tsx
- ✅ `/dashboard/configuracoes/frota` - page.tsx
- ✅ `/dashboard/configuracoes/mapas` - page.tsx

---

## ❌ Rotas QUEBRADAS (23 páginas faltantes)

### 🆕 Ambiental (8) - NOVO MÓDULO
- ❌ `/dashboard/ambiental`
- ❌ `/dashboard/ambiental/car/importar`
- ❌ `/dashboard/ambiental/car/lista`
- ❌ `/dashboard/ambiental/car/areas`
- ❌ `/dashboard/ambiental/monitoramento/mapa`
- ❌ `/dashboard/ambiental/monitoramento/alertas`
- ❌ `/dashboard/ambiental/monitoramento/historico`
- ❌ `/dashboard/ambiental/outorgas`

### Fiscal (5) - NOVAS FUNCIONALIDADES
- ❌ `/dashboard/financeiro/nf-e`
- ❌ `/dashboard/financeiro/lcdpr`
- ❌ `/dashboard/financeiro/esocial`
- ❌ `/dashboard/financeiro/contas-bancarias`
- ❌ `/dashboard/financeiro/romaneios`

### RH (3)
- ❌ `/dashboard/rh/colaboradores`
- ❌ `/dashboard/rh/departamentos`
- ❌ `/dashboard/rh/folha-pagamento`
- ❌ `/dashboard/rh/ponto`
- ❌ `/dashboard/rh/esocial`

### Agrícola (3) - Sidebar Atualizado
- ❌ `/dashboard/agricola/safras`
- ❌ `/dashboard/agricola/custos`
- ❌ `/dashboard/agricola/beneficiamento`
- ❌ `/dashboard/agricola/fenologia`
- ❌ `/dashboard/agricola/cadastros/culturas` (já existe mas está em caminho diferente)

### Operacional (4)
- ❌ `/dashboard/operacional/estoque`
- ❌ `/dashboard/operacional/movimentacoes`
- ❌ `/dashboard/operacional/fornecedores`
- ❌ `/dashboard/operacional/pedidos-compra`
- ❌ `/dashboard/operacional/frota`
- ❌ `/dashboard/operacional/manutencoes`

---

## 🎯 Prioridades para Correção

### Prioridade 1 - CRÍTICA (Funcionalidades da Fase 1)
1. **NFP-e/NF-e** - `/dashboard/financeiro/nf-e`
2. **eSocial** - `/dashboard/financeiro/esocial` e `/dashboard/rh/esocial`
3. **LCDPR** - `/dashboard/financeiro/lcdpr`
4. **Conciliação** - `/dashboard/financeiro/conciliacao` (JÁ EXISTE)
5. **Colaboradores** - `/dashboard/rh/colaboradores`
6. **Folha de Pagamento** - `/dashboard/rh/folha-pagamento`

### Prioridade 2 - ALTA (Ambiental - Módulo Novo)
1. **Dashboard Ambiental** - `/dashboard/ambiental`
2. **Importar CAR** - `/dashboard/ambiental/car/importar`
3. **Lista de CARs** - `/dashboard/ambiental/car/lista`
4. **Dashboard de Áreas** - `/dashboard/ambiental/car/areas`
5. **Mapa de Monitoramento** - `/dashboard/ambiental/monitoramento/mapa`
6. **Alertas** - `/dashboard/ambiental/monitoramento/alertas`

### Prioridade 3 - MÉDIA (Complementos)
1. **Romaneios** - `/dashboard/financeiro/romaneios`
2. **Contas Bancárias** - `/dashboard/financeiro/contas-bancarias`
3. **Estoque** - `/dashboard/operacional/estoque`
4. **Frota** - `/dashboard/operacional/frota`

---

## 🔧 Plano de Ação

### Semana 1 - Páginas Críticas
- [ ] Criar página NFP-e/NF-e
- [ ] Criar página eSocial (Fiscal)
- [ ] Criar página eSocial (RH)
- [ ] Criar página LCDPR
- [ ] Criar página Colaboradores
- [ ] Criar página Folha de Pagamento

### Semana 2 - Módulo Ambiental
- [ ] Criar Dashboard Ambiental
- [ ] Criar Importar CAR
- [ ] Criar Lista de CARs
- [ ] Criar Dashboard de Áreas
- [ ] Criar Mapa de Monitoramento
- [ ] Criar Alertas de Desmatamento

### Semana 3 - Complementos
- [ ] Criar páginas operacionais faltantes
- [ ] Criar páginas agrícolas faltantes
- [ ] Limpar rotas duplicadas

---

## 📝 Solução Imediata

Para evitar que usuários acessem páginas quebradas, vamos:

1. **Criar páginas placeholder** para todas as rotas críticas
2. **Atualizar o sidebar** para mostrar apenas o que está implementado
3. **Adicionar avisos** de "Em desenvolvimento"

---

**Próximo Passo:** Criar documento com a lista final do sidebar atualizado (apenas funcionalidades implementadas)
