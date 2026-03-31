# AgroSaaS - UI/UX Guidelines

**Versão:** 1.0.0  
**Última Atualização:** 2026-03-31  
**Status:** Ativo  

---

## 📋 Índice

1. [Princípios de Design](#1-princípios-de-design)
2. [Sistema de Cores](#2-sistema-de-cores)
3. [Tipografia](#3-tipografia)
4. [Componentes](#4-componentes)
5. [Layout e Grid](#5-layout-e-grid)
6. [Formulários](#6-formulários)
7. [Tabelas e Data Tables](#7-tabelas-e-data-tables)
8. [Feedback e Estados](#8-feedback-e-estados)
9. [Responsividade](#9-responsividade)
10. [Acessibilidade](#10-acessibilidade)

---

## 1. Princípios de Design

### Valores Fundamentais

1. **Clareza**: Interface limpa e compreensível
2. **Eficiência**: Menos cliques possível para tarefas comuns
3. **Consistência**: Padrões visuais e de interação uniformes
4. **Confiança**: Dados agrícolas críticos exigem precisão
5. **Acessibilidade**: Inclusivo para todos os usuários

### Público-Alvo

- **Agrônomos**: 25-55 anos, familiaridade com tecnologia variável
- **Produtores Rurais**: 35-65 anos, preferem interfaces simples
- **Operadores**: 20-50 anos, uso frequente em campo (mobile)
- **Gestores Financeiros**: 30-60 anos, foco em dados e relatórios

### Contextos de Uso

| Contexto | Dispositivo | Prioridade |
|----------|-------------|------------|
| Escritório | Desktop | Funcionalidades completas |
| Campo | Mobile/Tablet | Offline, rapidez |
| Reunião | Tablet | Visualização e apresentação |

---

## 2. Sistema de Cores

### Cores Principais

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        // Primary - Verde Agro
        primary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e', // Main
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        
        // Secondary - Terra
        secondary: {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c', // Main
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917',
          950: '#0c0a09',
        },
        
        // Accent - Dourado (Colheita)
        accent: {
          50: '#fefce8',
          100: '#fef9c3',
          200: '#fef08a',
          300: '#fde047',
          400: '#facc15',
          500: '#eab308', // Main
          600: '#ca8a04',
          700: '#a16207',
          800: '#854d0e',
          900: '#713f12',
          950: '#422006',
        },
      }
    }
  }
}
```

### Cores Semânticas

```typescript
{
  // Status
  success: '#22c55e',    // Concluído, ativo
  warning: '#eab308',    // Atenção, pendente
  error: '#ef4444',      // Erro, crítico
  info: '#3b82f6',       // Informação, neutro
  
  // Módulos
  agricola: '#16a34a',   // Verde
  pecuaria: '#d97706',   // Âmbar
  financeiro: '#2563eb', // Azul
  operacional: '#9333ea',// Roxo
  rh: '#ea580c',         // Laranja
  ambiental: '#059669',  // Esmeralda
}
```

### Uso de Cores

| Elemento | Cor | Exemplo |
|----------|-----|---------|
| Primary Actions | `primary-500` | Botões principais |
| Secondary Actions | `secondary-500` | Botões secundários |
| Links | `primary-600` | Links em texto |
| Headings | `secondary-900` | Títulos |
| Body Text | `secondary-700` | Texto corrido |
| Muted Text | `secondary-500` | Texto secundário |
| Borders | `secondary-200` | Bordas de inputs |
| Background | `white` | Fundo de cards |
| Surface | `secondary-50` | Fundo de seções |

---

## 3. Tipografia

### Fontes

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    }
  }
}
```

### Escala Tipográfica

| Classe | Tamanho | Peso | Uso |
|--------|---------|------|-----|
| `text-4xl` | 36px | 700 | Títulos de página |
| `text-3xl` | 30px | 700 | Títulos de seção |
| `text-2xl` | 24px | 600 | Títulos de card |
| `text-xl` | 20px | 600 | Subtítulos |
| `text-lg` | 18px | 500 | Destaques |
| `text-base` | 16px | 400 | Texto corrido |
| `text-sm` | 14px | 400 | Labels, captions |
| `text-xs` | 12px | 400 | Microcopy |

### Hierarquia

```tsx
// Página típica
<h1 className="text-3xl font-bold text-secondary-900">
  Safras
</h1>

<section>
  <h2 className="text-xl font-semibold text-secondary-800">
    Safra Atual
  </h2>
  
  <Card>
    <CardHeader>
      <CardTitle className="text-lg font-semibold">
        Soja 2025/26
      </CardTitle>
      <CardDescription className="text-sm text-secondary-500">
        Ciclo principal
      </CardDescription>
    </CardHeader>
  </Card>
</section>
```

---

## 4. Componentes

### Botões

```tsx
// Primário - Ação principal
<Button>
  Criar Safra
</Button>

// Secundário - Ações secundárias
<Button variant="secondary">
  Cancelar
</Button>

// Outline - Ações menos proeminentes
<Button variant="outline">
  Exportar
</Button>

// Ghost - Ações discretas
<Button variant="ghost">
  <Eye className="h-4 w-4" />
</Button>

// Destructive - Ações destrutivas
<Button variant="destructive">
  Excluir
</Button>

// Tamanhos
<Button size="sm">Pequeno</Button>
<Button size="default">Padrão</Button>
<Button size="lg">Grande</Button>
<Button size="icon">Ícone</Button>
```

### Cards

```tsx
<Card>
  <CardHeader>
    <CardTitle>Título do Card</CardTitle>
    <CardDescription>Descrição opcional</CardDescription>
  </CardHeader>
  <CardContent>
    Conteúdo principal
  </CardContent>
  <CardFooter>
    Ações do footer
  </CardFooter>
</Card>
```

### Dialogs (Modais)

```tsx
<Dialog>
  <DialogTrigger asChild>
    <Button>Abrir Modal</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Título do Modal</DialogTitle>
      <DialogDescription>
        Descrição do que vai acontecer
      </DialogDescription>
    </DialogHeader>
    <form>
      {/* Campos do formulário */}
      <DialogFooter>
        <Button type="submit">Salvar</Button>
        <Button variant="outline" onClick={() => setOpen(false)}>
          Cancelar
        </Button>
      </DialogFooter>
    </form>
  </DialogContent>
</Dialog>
```

### Badges

```tsx
// Status de safra
<Badge variant="default">Ativa</Badge>
<Badge variant="secondary">Planejada</Badge>
<Badge variant="destructive">Encerrada</Badge>
<Badge variant="outline">Rascunho</Badge>

// Cores por módulo
<Badge className="bg-agricola">Agrícola</Badge>
<Badge className="bg-pecuaria">Pecuária</Badge>
<Badge className="bg-financeiro">Financeiro</Badge>
```

### Avatar

```tsx
<Avatar>
  <AvatarImage src="/user.jpg" alt="Nome" />
  <AvatarFallback>NS</AvatarFallback>
</Avatar>
```

---

## 5. Layout e Grid

### Container

```tsx
// Container principal
<div className="container mx-auto px-4 py-8">
  {/* Conteúdo */}
</div>

// Container full-width
<div className="w-full">
  {/* Conteúdo */}
</div>
```

### Grid System

```tsx
// Grid responsivo
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <Card>Card 1</Card>
  <Card>Card 2</Card>
  <Card>Card 3</Card>
</div>

// Dashboard KPIs
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
  <KPICard title="Área Plantada" value="500 ha" />
  <KPICard title="Produtividade" value="65 sc/ha" />
  <KPICard title="Custo/ha" value="R$ 3.500" />
  <KPICard title="Receita" value="R$ 1.2M" />
</div>
```

### Sidebar Layout

```tsx
<div className="flex h-screen">
  {/* Sidebar */}
  <aside className="w-64 border-r bg-white">
    <AppSidebar />
  </aside>
  
  {/* Main content */}
  <div className="flex-1 flex flex-col">
    {/* Navbar */}
    <header className="h-16 border-b bg-white">
      <Navbar />
    </header>
    
    {/* Page content */}
    <main className="flex-1 overflow-auto p-6">
      {children}
    </main>
  </div>
</div>
```

---

## 6. Formulários

### Estrutura Padrão

```tsx
<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
    <FormField
      control={form.control}
      name="nome"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Nome da Safra</FormLabel>
          <FormControl>
            <Input placeholder="Ex: Soja 2025/26" {...field} />
          </FormControl>
          <FormDescription>
            Nome identificador da safra
          </FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />
    
    <FormField
      control={form.control}
      name="cultura"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Cultura</FormLabel>
          <Select onValueChange={field.onChange} defaultValue={field.value}>
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder="Selecione" />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              <SelectItem value="soja">Soja</SelectItem>
              <SelectItem value="milho">Milho</SelectItem>
              <SelectItem value="trigo">Trigo</SelectItem>
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      )}
    />
    
    <Button type="submit">Salvar</Button>
  </form>
</Form>
```

### Validação

```typescript
// Schema Zod
const safraSchema = z.object({
  nome: z
    .string()
    .min(3, "Nome deve ter pelo menos 3 caracteres")
    .max(100, "Nome deve ter no máximo 100 caracteres"),
  
  cultura: z
    .string()
    .min(1, "Cultura é obrigatória"),
  
  hectares_planejados: z
    .number()
    .positive("Hectares deve ser positivo")
    .max(100000, "Valor inválido"),
  
  data_inicio: z
    .date()
    .refine(
      (date) => date > new Date(),
      "Data de início deve ser futura"
    ),
})
```

### Estados de Input

```tsx
// Normal
<Input />

// Focus
<Input className="focus:ring-2 focus:ring-primary-500" />

// Error
<Input className="border-destructive" />
<FormMessage>Erro de validação</FormMessage>

// Disabled
<Input disabled />

// With icon
<div className="relative">
  <Search className="absolute left-3 top-3 h-4 w-4 text-secondary-400" />
  <Input className="pl-10" />
</div>
```

---

## 7. Tabelas e Data Tables

### Tabela Simples

```tsx
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Nome</TableHead>
      <TableHead>Cultura</TableHead>
      <TableHead>Área (ha)</TableHead>
      <TableHead>Status</TableHead>
      <TableHead>Ações</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {safras.map((safra) => (
      <TableRow key={safra.id}>
        <TableCell className="font-medium">{safra.nome}</TableCell>
        <TableCell>{safra.cultura}</TableCell>
        <TableCell>{safra.hectares_planejados}</TableCell>
        <TableCell>
          <Badge>{safra.status}</Badge>
        </TableCell>
        <TableCell>
          <DropdownMenu>
            <DropdownMenuTrigger>
              <MoreHorizontal className="h-4 w-4" />
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem>Editar</DropdownMenuItem>
              <DropdownMenuItem>Excluir</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

### DataTable Avançada

```tsx
// components/ui/data-table.tsx
interface DataTableProps<T> {
  columns: ColumnDef<T>[]
  data: T[]
  searchKey?: string
  filters?: FilterConfig[]
}

export function DataTable<T>({ 
  columns, 
  data, 
  searchKey,
  filters 
}: DataTableProps<T>) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [filtering, setFiltering] = useState("")
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  })
  
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    state: { 
      sorting, 
      globalFilter: filtering,
      pagination,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setFiltering,
    onPaginationChange: setPagination,
  })
  
  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        {searchKey && (
          <Input
            placeholder={`Buscar ${searchKey}...`}
            value={filtering}
            onChange={(e) => setFiltering(e.target.value)}
            className="max-w-sm"
          />
        )}
        <div className="flex items-center gap-2">
          {filters?.map((filter) => (
            <FilterDropdown key={filter.key} config={filter} />
          ))}
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>
      
      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((group) => (
              <TableRow key={group.id}>
                {group.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  Nenhum resultado.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      
      {/* Pagination */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-secondary-500">
          {table.getFilteredRowModel().rows.length} resultado(s)
        </p>
        <Pagination table={table} />
      </div>
    </div>
  )
}
```

---

## 8. Feedback e Estados

### Toast Notifications

```tsx
// Usando Sonner
import { toast } from "sonner"

// Sucesso
toast.success("Safra criada com sucesso!")

// Erro
toast.error("Erro ao salvar safra")

// Loading
const promise = () => new Promise((resolve) => setTimeout(resolve, 2000))

toast.promise(promise, {
  loading: 'Salvando...',
  success: 'Salvo com sucesso!',
  error: 'Erro ao salvar',
})

// Info
toast.info("Há atualizações disponíveis")

// Warning
toast.warning("Safra está vencida")
```

### Loading States

```tsx
// Skeleton
<Skeleton className="h-10 w-full" />
<Skeleton className="h-24 w-full" />

// Spinner
<Spinner className="h-6 w-6" />

// Button loading
<Button disabled>
  <Spinner className="mr-2 h-4 w-4" />
  Salvando...
</Button>

// Page loading
<div className="flex items-center justify-center h-64">
  <Spinner className="h-8 w-8" />
</div>
```

### Empty States

```tsx
<div className="flex flex-col items-center justify-center h-64 text-center">
  <FileQuestion className="h-12 w-12 text-secondary-400 mb-4" />
  <h3 className="text-lg font-semibold">Nenhuma safra encontrada</h3>
  <p className="text-secondary-500 mb-4">
    Comece criando uma nova safra
  </p>
  <Button>
    <Plus className="h-4 w-4 mr-2" />
    Criar Safra
  </Button>
</div>
```

### Error States

```tsx
<div className="flex flex-col items-center justify-center h-64 text-center">
  <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
  <h3 className="text-lg font-semibold">Erro ao carregar</h3>
  <p className="text-secondary-500 mb-4">
    Não foi possível carregar as safras
  </p>
  <Button onClick={retry}>
    <RefreshCw className="h-4 w-4 mr-2" />
    Tentar Novamente
  </Button>
</div>
```

---

## 9. Responsividade

### Breakpoints

```typescript
// tailwind.config.ts
export default {
  theme: {
    screens: {
      'sm': '640px',   // Mobile landscape
      'md': '768px',   // Tablet
      'lg': '1024px',  // Desktop
      'xl': '1280px',  // Desktop grande
      '2xl': '1536px', // Desktop extra grande
    }
  }
}
```

### Padrões Responsivos

```tsx
// Grid responsivo
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {cards}
</div>

// Tabela responsiva
<div className="overflow-x-auto">
  <Table>
    {/* Tabela com scroll horizontal em mobile */}
  </Table>
</div>

// Layout responsivo
<div className="flex flex-col lg:flex-row gap-4">
  <aside className="w-full lg:w-64">
    {/* Sidebar */}
  </aside>
  <main className="flex-1">
    {/* Conteúdo principal */}
  </main>
</div>

// Esconder/mostrar elementos
<div className="hidden md:block">
  {/* Visível apenas em desktop */}
</div>

<button className="md:hidden">
  {/* Visível apenas em mobile */}
</button>
```

---

## 10. Acessibilidade

### ARIA Labels

```tsx
// Botão com ícone
<Button aria-label="Editar safra">
  <Edit className="h-4 w-4" />
</Button>

// Input com label
<label htmlFor="nome" className="sr-only">
  Nome
</label>
<Input id="nome" aria-describedby="nome-help" />
<span id="nome-help" className="text-sm">
  Digite o nome completo
</span>

// Modal
<Dialog aria-labelledby="dialog-title" aria-describedby="dialog-desc">
  <DialogTitle id="dialog-title">Título</DialogTitle>
  <DialogDescription id="dialog-desc">
    Descrição do modal
  </DialogDescription>
</Dialog>
```

### Keyboard Navigation

```tsx
// Foco visível
<Button className="focus:ring-2 focus:ring-primary-500 focus:outline-none">
  Botão
</Button>

// Skip links
<a href="#main-content" className="sr-only focus:not-sr-only">
  Pular para conteúdo principal
</a>

<main id="main-content">
  {/* Conteúdo principal */}
</main>
```

### Contraste

- **Texto normal**: Mínimo 4.5:1
- **Texto grande**: Mínimo 3:1
- **Elementos de UI**: Mínimo 3:1

### Screen Readers

```tsx
// Conteúdo apenas para screen readers
<span className="sr-only">
  Informação adicional para screen readers
</span>

// Esconder de screen readers
<span aria-hidden="true">
  Ícone decorativo
</span>

// Anunciar mudanças dinâmicas
<div role="status" aria-live="polite">
  {isLoading && "Carregando..."}
</div>
```

---

## Referências Cruzadas

| Documento | Descrição |
|-----------|-----------|
| `docs/qwen/04-frontend.md` | Frontend Next.js |
| `docs/qwen/01-arquitetura.md` | Arquitetura geral |

---

## Changelog

| Data | Versão | Descrição |
|------|--------|-----------|
| 2026-03-31 | 1.0.0 | Documentação inicial completa |
