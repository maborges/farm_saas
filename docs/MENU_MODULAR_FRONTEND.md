# 🎨 Estrutura de Menu Modular - Frontend

## 📋 Visão Geral

Este documento descreve como a navegação do frontend reflete a estrutura modular do AgroSaaS, permitindo que apenas os módulos contratados apareçam no menu.

## 🗂️ Arquivos Criados

### 1. Constantes de Módulos
📁 `apps/web/src/lib/constants/modulos.ts`

Define todos os IDs de módulos sincronizados com o backend:

```typescript
import { Modulos } from "@/lib/constants/modulos";

// Usar em components
<ModuleGate moduleId={Modulos.AGRICOLA_PLANEJAMENTO}>
```

### 2. Hooks de Feature Gates
📁 `apps/web/src/hooks/use-has-module.ts`

Hooks React para verificar módulos contratados:

```typescript
import { useHasModule, useHasAnyModule, useHasAllModules } from "@/hooks/use-has-module";

// Verificar módulo único
const hasPlanning = useHasModule(Modulos.AGRICOLA_PLANEJAMENTO);

// Qualquer um
const hasFinancial = useHasAnyModule(
  Modulos.FINANCEIRO_TESOURARIA,
  Modulos.FINANCEIRO_CUSTOS_ABC
);

// Todos
const hasAdvanced = useHasAllModules(
  Modulos.AGRICOLA_PLANEJAMENTO,
  Modulos.FINANCEIRO_CUSTOS_ABC
);
```

### 3. Componente ModuleGate Aprimorado
📁 `apps/web/src/components/shared/module-gate.tsx`

Componente para proteger conteúdo:

```typescript
<ModuleGate
  moduleId={Modulos.AGRICOLA_PLANEJAMENTO}
  showUpgradePrompt={true} // Mostra tela de upgrade
>
  <ConteudoDoModulo />
</ModuleGate>
```

## 📐 Nova Estrutura do Menu (app-sidebar.tsx)

### Menu Organizado por Blocos de Módulos

#### BLOCO AGRÍCOLA

```typescript
<ModuleGate moduleId={Modulos.AGRICOLA_PLANEJAMENTO}>
  <Collapsible>
    <CollapsibleTrigger>
      <Sprout /> Lavoura
    </CollapsibleTrigger>
    <CollapsibleContent>
      {/* A1 - Planejamento */}
      <ModuleGate moduleId={Modulos.AGRICOLA_PLANEJAMENTO}>
        <MenuItem href="/agricola/planejamento">
          📊 Planejamento de Safra
        </MenuItem>
      </ModuleGate>

      {/* A2 - Caderno de Campo */}
      <ModuleGate moduleId={Modulos.AGRICOLA_CAMPO}>
        <MenuItem href="/agricola/campo">
          📝 Caderno de Campo
        </MenuItem>
        <MenuItem href="/agricola/operacoes">
          🚜 Ordens de Serviço
        </MenuItem>
      </ModuleGate>

      {/* A3 - Defensivos */}
      <ModuleGate moduleId={Modulos.AGRICOLA_DEFENSIVOS}>
        <MenuItem href="/agricola/defensivos">
          🛡️ Defensivos
        </MenuItem>
      </ModuleGate>

      {/* A4 - Agricultura de Precisão */}
      <ModuleGate moduleId={Modulos.AGRICOLA_PRECISAO}>
        <MenuItem href="/agricola/ndvi">
          🛰️ NDVI & Satélite
        </MenuItem>
        <MenuItem href="/agricola/prescricoes">
          📍 Mapas VRA
        </MenuItem>
      </ModuleGate>

      {/* A5 - Colheita */}
      <ModuleGate moduleId={Modulos.AGRICOLA_COLHEITA}>
        <MenuItem href="/agricola/colheita">
          🚜 Colheita & Romaneio
        </MenuItem>
      </ModuleGate>
    </CollapsibleContent>
  </Collapsible>
</ModuleGate>
```

#### BLOCO PECUÁRIA

```typescript
<ModuleGate moduleId={Modulos.PECUARIA_REBANHO}>
  <Collapsible>
    <CollapsibleTrigger>
      <Beef /> Pecuária
    </CollapsibleTrigger>
    <CollapsibleContent>
      {/* P1 - Controle de Rebanho */}
      <ModuleGate moduleId={Modulos.PECUARIA_REBANHO}>
        <MenuItem href="/pecuaria/lotes">
          🐄 Controle de Lotes
        </MenuItem>
        <MenuItem href="/pecuaria/piquetes">
          📍 Piquetes e Pastos
        </MenuItem>
      </ModuleGate>

      {/* P2 - Genética */}
      <ModuleGate moduleId={Modulos.PECUARIA_GENETICA}>
        <MenuItem href="/pecuaria/genetica">
          🧬 Genética & Reprodução
        </MenuItem>
        <MenuItem href="/pecuaria/iatf">
          💉 IATF e Diagnósticos
        </MenuItem>
      </ModuleGate>

      {/* P3 - Confinamento */}
      <ModuleGate moduleId={Modulos.PECUARIA_CONFINAMENTO}>
        <MenuItem href="/pecuaria/confinamento">
          🏭 Feedlot Control
        </MenuItem>
        <MenuItem href="/pecuaria/racao">
          🌾 Fábrica de Ração
        </MenuItem>
      </ModuleGate>

      {/* P4 - Leite */}
      <ModuleGate moduleId={Modulos.PECUARIA_LEITE}>
        <MenuItem href="/pecuaria/leite">
          🥛 Controle Leiteiro
        </MenuItem>
      </ModuleGate>
    </CollapsibleContent>
  </Collapsible>
</ModuleGate>
```

#### BLOCO FINANCEIRO

```typescript
<ModuleGate moduleId={Modulos.FINANCEIRO_TESOURARIA}>
  <Collapsible>
    <CollapsibleTrigger>
      <HandCoins /> Financeiro
    </CollapsibleTrigger>
    <CollapsibleContent>
      {/* F1 - Tesouraria */}
      <ModuleGate moduleId={Modulos.FINANCEIRO_TESOURARIA}>
        <MenuItem href="/financeiro/despesas">
          💳 Contas a Pagar
        </MenuItem>
        <MenuItem href="/financeiro/receitas">
          💰 Contas a Receber
        </MenuItem>
      </ModuleGate>

      {/* F2 - Custos ABC */}
      <ModuleGate moduleId={Modulos.FINANCEIRO_CUSTOS_ABC}>
        <MenuItem href="/financeiro/custos">
          📊 Rateio de Custos
        </MenuItem>
      </ModuleGate>

      {/* F3 - Fiscal */}
      <ModuleGate moduleId={Modulos.FINANCEIRO_FISCAL}>
        <MenuItem href="/financeiro/nfe">
          📋 Emissão NF-e
        </MenuItem>
        <MenuItem href="/financeiro/sped">
          📁 SPED & LCDPR
        </MenuItem>
      </ModuleGate>

      {/* F4 - Hedging */}
      <ModuleGate moduleId={Modulos.FINANCEIRO_HEDGING}>
        <MenuItem href="/financeiro/hedging">
          📈 Hedging & Futuros
        </MenuItem>
      </ModuleGate>
    </CollapsibleContent>
  </Collapsible>
</ModuleGate>
```

#### BLOCO OPERACIONAL

```typescript
<ModuleGate moduleId={Modulos.OPERACIONAL_FROTA}>
  <Collapsible>
    <CollapsibleTrigger>
      <Settings /> Operacional
    </CollapsibleTrigger>
    <CollapsibleContent>
      {/* O1 - Frota */}
      <ModuleGate moduleId={Modulos.OPERACIONAL_FROTA}>
        <MenuItem href="/operacional/frota">
          🚜 Frota e Máquinas
        </MenuItem>
        <MenuItem href="/operacional/oficina">
          🔧 Oficina e Manutenções
        </MenuItem>
      </ModuleGate>

      {/* O2 - Estoque */}
      <ModuleGate moduleId={Modulos.OPERACIONAL_ESTOQUE}>
        <MenuItem href="/operacional/estoque">
          📦 Almoxarifado
        </MenuItem>
      </ModuleGate>

      {/* O3 - Compras */}
      <ModuleGate moduleId={Modulos.OPERACIONAL_COMPRAS}>
        <MenuItem href="/operacional/compras">
          🛒 Supply & Compras
        </MenuItem>
      </ModuleGate>
    </CollapsibleContent>
  </Collapsible>
</ModuleGate>
```

## 🎨 Componentes Visuais

### ModuleBadge

Exibir badge de módulo com status:

```typescript
import { ModuleBadge } from "@/components/shared/module-gate";

<ModuleBadge moduleId={Modulos.AGRICOLA_PLANEJAMENTO} />
// Renderiza: 📊 Planejamento de Safra [✓ ou 🔒]
```

### Tela de Upgrade

Quando usuário tenta acessar módulo não contratado:

```typescript
<ModuleGate
  moduleId={Modulos.AGRICOLA_PRECISAO}
  showUpgradePrompt={true}
>
  {/* Conteúdo só aparece se tiver módulo */}
  <AgriculturaPrec isao />
</ModuleGate>

// Se NÃO tiver, mostra:
// 🔒 Módulo não contratado
// Agricultura de Precisão
// A partir de R$ 499,00/mês
// [Fazer Upgrade do Plano]
```

## 📱 Exemplo de Página com Feature Gate

```typescript
// apps/web/src/app/(dashboard)/agricola/planejamento/page.tsx

import { ModuleGate } from "@/components/shared/module-gate";
import { Modulos } from "@/lib/constants/modulos";

export default function PlanejamentoPage() {
  return (
    <ModuleGate
      moduleId={Modulos.AGRICOLA_PLANEJAMENTO}
      showUpgradePrompt={true}
    >
      <div className="p-6">
        <h1>Planejamento de Safra</h1>
        {/* Conteúdo da página */}
      </div>
    </ModuleGate>
  );
}
```

## 🔄 Sincronização Backend → Frontend

### No Login (JWT)

O backend deve incluir módulos no JWT:

```json
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",
  "modules": [
    "CORE",
    "A1_PLANEJAMENTO",
    "A2_CAMPO",
    "P1_REBANHO",
    "F1_TESOURARIA"
  ],
  "exp": 1234567890
}
```

### No Zustand Store

```typescript
// apps/web/src/lib/stores/app-store.ts

interface AppState {
  modules: string[];
  setModules: (modules: string[]) => void;
}

export const useAppStore = create<AppState>((set) => ({
  modules: [],
  setModules: (modules) => set({ modules }),
}));
```

### Ao fazer login

```typescript
// Após autenticação bem-sucedida
const decodedToken = jwt.decode(accessToken);
useAppStore.getState().setModules(decodedToken.modules);
```

## 🎯 Checklist de Implementação

### Backend
- [x] Criar `core/constants.py`
- [x] Implementar feature gates em `core/dependencies.py`
- [x] Adicionar `modules` ao JWT
- [ ] Atualizar endpoint de login para retornar módulos

### Frontend
- [x] Criar `lib/constants/modulos.ts`
- [x] Criar `hooks/use-has-module.ts`
- [x] Atualizar `components/shared/module-gate.tsx`
- [ ] Atualizar `app-sidebar.tsx` com módulos granulares
- [ ] Adicionar `modules` ao Zustand store
- [ ] Atualizar fluxo de login para salvar módulos

### Páginas
- [ ] Adicionar `ModuleGate` em todas as páginas protegidas
- [ ] Criar páginas de upgrade para cada módulo
- [ ] Adicionar `ModuleBadge` em cards e dashboards

## 🚀 Próximos Passos

1. **Atualizar app-sidebar.tsx**
   - Substituir IDs antigos ("A1", "P1") pelos novos
   - Organizar menu por módulos granulares
   - Adicionar badges de módulos

2. **Atualizar Zustand Store**
   - Adicionar campo `modules: string[]`
   - Criar método `hasModule(id: string)`

3. **Atualizar Auth Flow**
   - Backend incluir módulos no JWT
   - Frontend salvar módulos no store após login

4. **Criar Tela de Planos**
   - Catálogo visual de módulos
   - Seletor de módulos para upgrade
   - Integração com billing

## 📚 Referências

- [Constantes Backend](../services/api/core/constants.py)
- [Feature Gates Backend](../services/api/core/dependencies.py)
- [Plano de Modularização](./PLANO_MODULARIZACAO.md)

---

**Última atualização:** 2026-03-10
**Versão:** 1.0
