# AgroSaaS - Plataforma de Gestão Rural Modular

Sistema avançado para gestão de fazendas, focada em produtividade, isolamento de dados (Multi-tenancy) e interface de alta performance.

## 🏗️ Arquitetura do Sistema

O projeto é dividido em um monorepo contendo:
- **apps/web**: Interface Next.js 16 com shadcn/ui e Zustand.
- **services/api**: Backend Python com FastAPI, SQLAlchemy e banco de dados PostgreSQL.
- **packages/zod-schemas**: Definições de contratos compartilhados (Shared Schemas).

## 🚀 Funcionalidades (Features)

### 1. Sistema de Identidade e Multi-Tenancy (Fase 1 e 2)
- **Isolamento Absoluto**: Cada produtor (Tenant) possui seus dados cercados por segurança de nível de serviço.
- **Vincular Contextos**: Um único usuário pode ter acesso a múltiplas empresas rurais (Holdings) e transitar entre elas sem deslogar.
- **Perfis de Acesso**: Controle granular por papéis (Proprietário, Agrônomo, Gerente, Operador).

### 2. Onboarding e Expansão de Equipe (Fase 3)
- **Auto-Cadastro de Produtores**: Fluxo simplificado que cria Identidade + Tenant + Fazenda + Assinatura em uma única operação.
- **Sistema de Convites**: Donos de fazendas podem convidar técnicos e funcionários via e-mail.
- **Segurança de Convites**: Tokens expiráveis e vínculos automáticos de propriedade ao aceitar o acesso.

### 3. Gestão Agrícola e Pecuária (Módulos Base)
- **Meus Talhões**: Visualização geográfica de áreas produtivas.
- **Controle de Lotes**: Gestão técnica de rebanho.
- **Financeiro Rural**: DRE, Contas a Pagar/Receber com foco em custeio de safra.

---

## 🛠️ Como Executar

### Backend
1. Navegue até `services/api`.
2. Ative o venv: `source .venv/bin/activate`.
3. Rode: `uvicorn main:app --reload`.

cd services/api
source .venv/bin/activate
./start_server.sh

uvicorn main:app --reload


### Frontend
1. Navegue até `apps/web`.
2. Rode: `pnpm run dev`.

cd apps/web
pnpm run dev


### Matar processo do servidor
pkill -f "uvicorn main:app" && sleep 2 && echo "✅ Processo uvicorn parado" (Parar processo uvicorn travado)

# AGRO-03: Frontend Web (Next.js 16 & UI)

**CONTEXTO:** Interface premium, performance RSC e estado sincronizado para gestão rural.

### 1. SERVER VS CLIENT COMPONENTS
- **RSC Default**: Todo componente é Server Component por padrão.
- **"use client"**: Restrito a: Interatividade (forms, click), Client Browser APIs, TanStack Query hooks.
- **Page Rules**: `page.tsx` DEVE ser RSC — busca dados no servidor e passa para Client Components via props.

### 2. ESTADO E CACHE
- **Server State**: Use TanStack Query (v5) para cache, revalidação automática e optimistic updates.
- **Client State**: Use Zustand para estados leves (tenant ativo, módulo aberto).
- **Formulários**: React Hook Form + Zod (schemas compartilhados com backend no `packages/zod-schemas`).

### 3. UX & PERFORMANCE
- **Skeletons**: Use `loading.tsx` para Suspense nativo em telas pesadas (Dashboard Agricola).
- **Data Grids**: AG Grid para planilhas com 10k+ linhas (Rebanho/Financeiro).
- **Zero Layout Shift**: Definir alturas fixas ou placeholders de imagem (`generate_image`).

### 4. DESIGN SYSTEM (shadcn/ui)
- **Componentes**: 
* Use prioritariamente bibliotecas padronizadas da stack, como `/components/ui/` (shadcn), Componentes Nativos do React. 
* Código customizado SOMENTE se o usuário solicitar explicitamente.
* User toast para apresentar mensagens ao usuário. 
* Botões devem ser outline e size sm
* Utilize ícones que signifiquem a ação nos botões 
* Input devem ter tamanho small
* Todas as sombras com a blasse shadow-xm
* As bordas dos componentes devem ser rounded-xm 
* Usar sidebar para os menus separando os itens por módulo e seus submodulos que devem expandir conforme selecionados  
* Usar sidebar para navegação de menus que pode ser retraidos 
* Procure sempre usar o datatables com pesquisa, ordenação de colunas, exportação para pdf e excel. Quando houver a coluna de ações não colocar header na coluna, botões de ação sem bordas, sem texto, gap-0, cor e ícone pertinente à ação e tooltips curto.

- **Estética Agro**: Use paletas harmoniosas (Verde Esmeralda, Tons Terra) e Dark/Light Mode premiun e o usuário pode mudar.

### 5. TIPAGEM E QUALIDADE ESTRITA (TS)
- **Strict Mode**: Habilitado e rigorosamente cumprido na `tsconfig.json`.
- **Abolição do `any`**: PROIBIDO o uso de tipagem `any` ou subterfúgios como `@ts-ignore` e `as unknown as Type`.
- **Importação Ordenada**: Respeitar a taxonomia: `react -> libs -> components -> utils`.

```tsx
// page.tsx (RSC)
export default async function Page() {
    const data = await getAnimais(); // Busca direta no servidor
    return <AnimaisGrid initialData={data} />;
}
