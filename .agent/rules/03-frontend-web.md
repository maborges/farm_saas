---
trigger: always_on
---

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
*Use prioritariamente bibliotecas padronizadas da stack, como `/components/ui/` (shadcn), Componentes Nativos do React. 
*Código customizado SOMENTE se o usuário solicitar explicitamente.
*User toast para apresentar mensagens ao usuário. * Botões devem ser outline e size sm
*Inputes devem ter tamanho small
*As bordas dos componentes devem ser rounded-sm 
*Usar sidebar para os menus separando os itens por módulo contratado que devem expandir conforme selecionados  
*Utilize ícones que signifiquem a ação nos botões 
*Usar sidebar para navegação de menus que pode ser retraidos 
*Procure sempre usar o datatables com pesquisa, exportação para pdf e excel, quando houver a coluna de ações não colocar header na coluna, botões de ação sem bordas, sem texto, gap-0, cor pertinente à ação

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
```