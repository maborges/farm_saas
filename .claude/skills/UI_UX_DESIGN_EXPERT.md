# UI/UX Design Expert - AgroSaaS

You are a specialist in **UI/UX Design** for AgroSaaS, responsible for creating consistent, accessible, and user-friendly interfaces across all modules.

## Overview

AgroSaaS uses a modern design system built on **shadcn/ui** components with **Tailwind CSS 4**. This skill defines the visual language, component standards, layout patterns, and accessibility guidelines for the entire application.

**Technology Stack:**
- **UI Library:** shadcn/ui (headless components)
- **Styling:** Tailwind CSS 4 (utility-first)
- **Icons:** Lucide React
- **Theme:** CSS variables + dark mode support
- **Typography:** Inter font family

## Design Tokens

### Colors

Defined in [apps/web/src/app/globals.css](../../apps/web/src/app/globals.css)

**Light Mode:**
```css
--background: oklch(0.98 0 0);
--foreground: oklch(0.145 0 0);
--primary: #43A047;             /* Green-600 - Agricultural theme */
--primary-foreground: #ffffff;
--secondary: #E8F5E9;           /* green-50 */
--muted: oklch(0.96 0 0);
--accent: #E8F5E9;
--destructive: oklch(0.58 0.22 27);  /* Red for errors/delete */
--border: oklch(0.922 0 0);
--ring: #43A047;
```

**Usage Guidelines:**
- **Primary (Green):** Main actions, brand elements, active states
- **Destructive (Red):** Delete, block, critical warnings
- **Muted:** Backgrounds, disabled states, secondary text
- **Accent:** Highlights, hover states, notifications

### Spacing Scale

**Tailwind Standard Scale (rem-based):**
```
xs:  0.5  (2px)   - Minimal spacing
sm:  0.75 (3px)   - Compact spacing
md:  1    (4px)   - Default spacing
lg:  1.5  (6px)   - Comfortable spacing
xl:  2    (8px)   - Generous spacing
2xl: 3    (12px)  - Large spacing
```

**Component Spacing:**
- **Forms:** `space-y-1.5` or `space-y-2` (compact to default)
- **Sections:** `space-y-3` or `space-y-4` (default to comfortable)
- **Page Layout:** `space-y-6` (generous)
- **Grid Gaps:** `gap-2` (compact), `gap-3` (default), `gap-4` (comfortable)

### Typography

**Font Family:**
```css
font-family: 'Inter', sans-serif;
```

**Size Scale:**
```
text-xs:   0.75rem (12px)  - Labels, captions, helper text
text-sm:   0.875rem (14px) - Body text, form inputs
text-base: 1rem (16px)     - Default body text
text-lg:   1.125rem (18px) - Subtitles, section headers
text-xl:   1.25rem (20px)  - Page titles
text-2xl:  1.5rem (24px)   - Main headings
```

**Weight Scale:**
```
font-normal:   400 - Body text
font-medium:   500 - Labels, emphasized text
font-semibold: 600 - Headings, buttons
font-bold:     700 - Page titles, important headings
```

**Line Height:**
- **Headings:** `leading-tight` (1.25)
- **Body:** `leading-normal` (1.5)
- **Forms:** `leading-none` (1) for labels

## Component Standards

### Buttons

**Variants:**
```tsx
// Primary (default) - Main actions
<Button>Salvar</Button>

// Outline - Secondary actions, most common
<Button variant="outline">Cancelar</Button>

// Destructive - Delete/remove actions
<Button variant="destructive">Excluir</Button>

// Ghost - Tertiary actions, icon buttons
<Button variant="ghost"><Eye /></Button>

// Link - Text-like buttons
<Button variant="link">Ver detalhes</Button>
```

**Sizes:**
```tsx
// Small (preferred for high-density UIs)
<Button size="sm">Criar</Button>        // h-8, px-3, text-sm

// Default
<Button size="default">Criar</Button>   // h-10, px-4, text-base

// Large
<Button size="lg">Criar</Button>        // h-11, px-8, text-base

// Icon only
<Button size="icon"><Plus /></Button>   // h-10 w-10
```

**AgroSaaS Standard:**
- **Backoffice pages:** Use `size="sm"` and `variant="outline"` for most buttons
- **Form actions:** Primary button = outline, Cancel = outline
- **Icon buttons:** Use `size="sm"` with `className="h-7 px-2"` for table actions
- **Always include icons** with text for better scannability

**Example:**
```tsx
<Button size="sm" variant="outline" className="gap-2">
  <Plus className="size-4" />
  Novo Tenant
</Button>
```

### Form Inputs

**Text Inputs (AgroSaaS Standard — use shadcn `<Input>`):**
```tsx
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

<Input
  type="text"
  className="h-8 text-sm"
  placeholder="Digite aqui..."
/>
```

**Labels:**
```tsx
<Label className="text-xs font-medium">Nome Completo *</Label>
```

**Form Layout Pattern:**
```tsx
<div className="space-y-1.5">
  <Label htmlFor="email" className="text-xs font-medium">Email *</Label>
  <Input
    id="email"
    type="email"
    className="h-8 text-sm"
    placeholder="email@empresa.com"
  />
</div>
```

### Select Dropdowns

**Standard Select (shadcn):**
```tsx
<Select value={value} onValueChange={setValue}>
  <SelectTrigger className="w-full h-8 text-sm">
    <SelectValue placeholder="Selecione..." />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="opcao1" className="text-sm">Opção 1</SelectItem>
    <SelectItem value="opcao2" className="text-sm">Opção 2</SelectItem>
  </SelectContent>
</Select>
```

**AgroSaaS Standard:**
- **Trigger:** `h-8 text-sm` (compact)
- **Items:** `className="text-sm"` (consistent size)
- Always provide placeholder text

### Checkboxes

```tsx
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"

<div className="flex items-center gap-2">
  <Checkbox
    id="trial"
    checked={comTrial}
    onCheckedChange={(checked) => setComTrial(Boolean(checked))}
  />
  <Label htmlFor="trial" className="text-xs font-normal">
    Iniciar com período de trial (15 dias)
  </Label>
</div>
```

### Cards & Sections

**Section Card:**
```tsx
<div className="space-y-2 p-3 rounded-sm border bg-muted/20">
  <h3 className="text-xs font-semibold uppercase text-muted-foreground">
    Título da Seção
  </h3>
  {/* Content */}
</div>
```

**Metric Card:**
```tsx
<div className="p-4 rounded-sm border bg-card shadow-sm flex items-center gap-4">
  <div className="size-10 rounded-sm bg-primary/10 flex items-center justify-center text-primary">
    <Icon className="size-5" />
  </div>
  <div>
    <p className="text-xs font-medium text-muted-foreground uppercase">
      Total de Contas
    </p>
    <p className="text-2xl font-bold tabular-nums">142</p>
  </div>
</div>
```

### Dialogs/Modals

**Standard Dialog Structure:**
```tsx
<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent className="sm:max-w-[600px]">
    <DialogHeader>
      <DialogTitle className="flex items-center gap-2 text-lg">
        <Icon className="h-4 w-4 text-primary" />
        Título do Dialog
      </DialogTitle>
      <DialogDescription className="text-xs">
        Descrição explicativa do que este dialog faz
      </DialogDescription>
    </DialogHeader>

    <div className="space-y-3 py-3">
      {/* Form content */}
    </div>

    <DialogFooter>
      <Button size="sm" variant="outline" onClick={() => setIsOpen(false)}>
        Cancelar
      </Button>
      <Button size="sm" variant="outline" onClick={handleSubmit}>
        Confirmar
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

**Dialog Sizing:**
- **Small forms:** `max-w-[425px]`
- **Standard forms:** `max-w-[600px]`
- **Wide forms (horizontal layout):** `max-w-[900px]`
- **Full-width:** `max-w-[1200px]`

### Tables

**Standard Table (shadcn):**
```tsx
<Table>
  <TableHeader className="bg-muted/50">
    <TableRow>
      <TableHead className="w-[300px]">Nome</TableHead>
      <TableHead>Status</TableHead>
      <TableHead className="text-right">Ações</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {data.map((item) => (
      <TableRow key={item.id} className="hover:bg-muted/30">
        <TableCell className="font-medium">{item.nome}</TableCell>
        <TableCell>
          <Badge variant="outline">{item.status}</Badge>
        </TableCell>
        <TableCell className="text-right">
          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              size="sm"
              className="h-7 px-2"
              onClick={() => handleView(item.id)}
            >
              <Eye size={14} />
            </Button>
          </div>
        </TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

### Badges

**Status Badges:**
```tsx
// Success/Active
<Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
  ATIVO
</Badge>

// Warning/Pending
<Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
  PENDENTE
</Badge>

// Error/Blocked
<Badge variant="destructive">
  BLOQUEADO
</Badge>

// Info/Trial
<Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
  TRIAL
</Badge>
```

## Layout Patterns

### Page Layout (Standard)

```tsx
<div className="p-6 space-y-6 w-full">
  {/* Page Header */}
  <div className="flex items-center justify-between">
    <div>
      <h1 className="text-2xl font-bold tracking-tight">Título da Página</h1>
      <p className="text-muted-foreground text-sm">Descrição breve</p>
    </div>
    <Button size="sm" variant="outline" className="gap-2">
      <Plus className="size-4" />
      Nova Ação
    </Button>
  </div>

  {/* Metrics Row (optional) */}
  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
    {/* Metric cards */}
  </div>

  {/* Main Content */}
  <div className="rounded-sm border bg-card shadow-sm overflow-hidden">
    {/* Table or content */}
  </div>
</div>
```

### Form Layout (Horizontal - Preferred)

**For dialogs with multiple sections, use 2-column grid:**

```tsx
<div className="space-y-3 py-3">
  {/* Row 1: Two sections side by side */}
  <div className="grid grid-cols-2 gap-3">
    <div className="space-y-2 p-3 rounded-lg border bg-muted/20">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Seção 1
      </h3>
      {/* Fields */}
    </div>

    <div className="space-y-2 p-3 rounded-lg border bg-muted/20">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Seção 2
      </h3>
      {/* Fields */}
    </div>
  </div>

  {/* Row 2: Two more sections */}
  <div className="grid grid-cols-2 gap-3">
    {/* ... */}
  </div>
</div>
```

**Benefits:**
- Better use of horizontal space (widescreen-optimized)
- Less scrolling required
- Grouped related fields visually
- Cleaner, more organized appearance

### Responsive Grid

**Dashboard Cards:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {/* Cards auto-adjust based on screen size */}
</div>
```

**Form Fields:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 gap-2">
  {/* 1 column on mobile, 2 on desktop */}
</div>
```

## Icons

**Library:** Lucide React

**Size Guidelines:**
```tsx
// In buttons (sm)
<Icon className="size-4" />

// In headings
<Icon className="size-5" />

// In metric cards
<Icon size={20} />  // or size={24}

// In table action buttons
<Icon size={14} />
```

**Common Icons:**
- `Plus` - Create/Add
- `Edit`, `Settings2` - Edit
- `Eye` - View/Details
- `Trash2` - Delete
- `ShieldAlert`, `ShieldCheck` - Block/Unblock
- `Building2` - Tenants/Companies
- `Users` - Team/Users
- `CreditCard` - Billing/Payments
- `Calendar` - Dates/Schedule
- `MapPin` - Location/Farms

## Accessibility (a11y)

### Form Accessibility

**Always associate labels with inputs:**
```tsx
<div className="space-y-1.5">
  <label htmlFor="email" className="text-xs font-medium">
    Email *
  </label>
  <input
    id="email"
    type="email"
    className="w-full px-2 py-1.5 text-sm border rounded-md"
    aria-required="true"
    aria-invalid={hasError}
    aria-describedby={hasError ? "email-error" : undefined}
  />
  {hasError && (
    <p id="email-error" className="text-xs text-destructive">
      Email inválido
    </p>
  )}
</div>
```

### Button Accessibility

**Always provide accessible names for icon-only buttons:**
```tsx
<Button
  variant="outline"
  size="sm"
  aria-label="Visualizar detalhes"
  onClick={handleView}
>
  <Eye size={14} />
</Button>
```

### Loading States

**Button loading:**
```tsx
<Button disabled={isLoading}>
  {isLoading ? "Salvando..." : "Salvar"}
</Button>
```

**Page loading:**
```tsx
{isLoading ? (
  <div className="space-y-2 p-4">
    <Skeleton className="h-8 w-full" />
    <Skeleton className="h-8 w-full" />
    <Skeleton className="h-8 w-3/4" />
  </div>
) : (
  <Content />
)}
```

### Focus States

All interactive elements have visible focus rings via Tailwind's `ring` utilities (automatically applied by shadcn components).

## Common Patterns

### Empty States

```tsx
<div className="py-12 text-center">
  <Icon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
  <h3 className="text-lg font-semibold mb-2">Nenhum item encontrado</h3>
  <p className="text-sm text-muted-foreground mb-4">
    Comece criando seu primeiro item
  </p>
  <Button size="sm" variant="outline" onClick={handleCreate}>
    <Plus className="h-4 w-4 mr-2" />
    Criar Novo
  </Button>
</div>
```

### Error States

```tsx
<div className="p-4 rounded-md bg-destructive/10 border border-destructive/20">
  <div className="flex items-start gap-3">
    <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
    <div>
      <h4 className="text-sm font-semibold text-destructive">Erro ao carregar dados</h4>
      <p className="text-xs text-destructive/80 mt-1">
        {error.message}
      </p>
    </div>
  </div>
</div>
```

### Success Notifications (Toast)

```tsx
import { toast } from "sonner";

// Success
toast.success("Tenant criado com sucesso!");

// Error
toast.error("Erro ao criar tenant");

// Info
toast.info("Processando...");

// With action
toast.success("Arquivo enviado", {
  action: {
    label: "Desfazer",
    onClick: () => handleUndo()
  }
});
```

## Performance Considerations

### Image Optimization

```tsx
import Image from "next/image";

<Image
  src="/logo.png"
  alt="AgroSaaS Logo"
  width={200}
  height={50}
  priority  // For above-the-fold images
/>
```

### Lazy Loading

```tsx
import dynamic from "next/dynamic";

const HeavyComponent = dynamic(() => import("./HeavyComponent"), {
  loading: () => <div>Carregando...</div>,
  ssr: false  // Client-side only if needed
});
```

### Debounced Search

```tsx
import { useDebouncedCallback } from "use-debounce";

const debouncedSearch = useDebouncedCallback(
  (value: string) => {
    setSearchTerm(value);
  },
  300  // 300ms delay
);

<input
  type="search"
  onChange={(e) => debouncedSearch(e.target.value)}
  className="w-full px-2 py-1.5 text-sm border rounded-md"
/>
```

## Design Checklist

When implementing a new UI feature:

- [ ] Used `size="sm"` and `variant="outline"` for buttons
- [ ] Applied compact spacing (`space-y-1.5`, `gap-2`, `p-3`)
- [ ] Used `text-xs` for labels, `text-sm` for inputs
- [ ] Added icons to buttons for better scannability
- [ ] Implemented horizontal layout (2-column grid) for forms
- [ ] Associated labels with inputs (id/htmlFor)
- [ ] Added accessible names to icon-only buttons
- [ ] Included loading states for async actions
- [ ] Implemented proper error handling with user feedback
- [ ] Tested responsive behavior (mobile, tablet, desktop)
- [ ] Verified keyboard navigation works
- [ ] Ensured color contrast meets WCAG AA standards

## Examples

### Complete Form Dialog (AgroSaaS Standard)

See implementation in [apps/web/src/app/(dashboard)/backoffice/tenants/page.tsx:694-927](../../apps/web/src/app/(dashboard)/backoffice/tenants/page.tsx#L694-L927)

**Key Features:**
- 900px max-width for horizontal layout
- 2-column grid for sections
- Compact inputs (`px-2 py-1.5 text-sm`)
- Small labels (`text-xs`)
- Section headers (`text-xs font-semibold uppercase`)
- Small buttons (`size="sm" variant="outline"`)
- Minimal spacing (`space-y-1.5`, `gap-2`, `p-3`)

### Data Table with Actions

See implementation in [apps/web/src/app/(dashboard)/backoffice/tenants/page.tsx:539-615](../../apps/web/src/app/(dashboard)/backoffice/tenants/page.tsx#L539-L615)

**Key Features:**
- Icon-only action buttons (`h-7 px-2`)
- Hover states with color transitions
- Status badges with semantic colors
- Responsive column widths

## Troubleshooting

### "My buttons look too large"
→ Use `size="sm"` instead of default size

### "Too much whitespace in my form"
→ Reduce spacing: `space-y-1.5` instead of `space-y-4`, use `gap-2` instead of `gap-4`

### "Select dropdown doesn't match input height"
→ Add `h-8` to `SelectTrigger`: `<SelectTrigger className="w-full h-8 text-sm">`

### "Labels are too prominent"
→ Use `text-xs` instead of `text-sm`: `<label className="text-xs font-medium">`

### "Form feels cramped on mobile"
→ Use responsive grid: `grid-cols-1 md:grid-cols-2` instead of always `grid-cols-2`

### "Button text is too small to read"
→ Don't go below `size="sm"` and `text-sm` - this is the minimum readable size

---

**Author:** Claude Code (Anthropic)
**Date:** 15/03/2026
**Version:** 1.0
