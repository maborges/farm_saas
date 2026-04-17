# AgroSaaS: Premium Orange Design System

Este documento define os padrões visuais e de interface (UI/UX) para a identidade **Premium Orange**, garantindo consistência e alta qualidade em toda a plataforma.

## 🎨 Paleta de Cores (Brand Identity)

A cor principal do sistema é o **Premium Orange**, projetado para transmitir modernidade, energia e sofisticação no contexto agrícola.

- **Primary (Premium Orange):** `HSL(15 64% 59%)` / Hex: `#D97757`
- **Primary-Foreground:** `white` (ou tom de contraste máximo)
- **Accent:** Tons sutis de laranja para estados hover e backgrounds leves (`bg-primary/5` ou `bg-primary/10`).

## 🧱 Componentes Base

Todos os componentes devem seguir rigorosamente as medidas abaixo para manter o equilíbrio visual:

### Inputs (Campos de Entrada)
- **Altura (Default):** `h-8` (Small standard)
- **Borda:** `rounded-sm` (Bordas quadradas/suaves, não totalmente arredondadas)
- **Estilo Base:** `border-primary/10 bg-muted/10`
- **Foco (Focus):** `border-primary/40 ring-2 ring-primary/5`
- **Sombra:** `shadow-inner` para sensação de profundidade.

### Botões (Actions)
- **Variante Padrão:** `outline`
- **Tamanho Padrão:** `sm` (h-8)
- **Comportamento Tátil:** `active:scale-95` (Micro-animação de clique)
- **Tipografia:** `font-black`, `uppercase`, `tracking-widest` para ações principais.
- **Ícones:** Tamanho padronizado e alinhados com o texto.

### Cards e Containers
- **Borda:** `rounded-sm`
- **Aesthetic:** Glassmorphism (`backdrop-blur-xl`, `bg-card/60`)
- **Sombra Premium:** Layered shadows para profundidade (`shadow-premium`).

## 🖋️ Tipografia e Hierarquia

- **Títulos e Headers:** Deve-se priorizar o uso de `italic`, `font-black` e `uppercase` em cabeçalhos de módulos para um visual "premium/esportivo".
- **Labels:** Devem ser pequenas (`text-[10px]`), em negrito (`font-bold/semibold`), `uppercase` e com `tracking-wider`.
- **Contrastes:** Manter alto contraste entre `muted-foreground` e `foreground` para garantir legibilidade.

## 🌑 Modo Dark / Light

- O sistema deve suportar ambos os modos de forma nativa.
- Em modo Dark, as bordas e fundos devem ser ajustados para manter a transparência e o brilho do **Premium Orange** sem perder a legibilidade.

## 🚀 Princípios de UX

1. **Micro-interações:** Transições suaves de cor e escala em todos os elementos clicáveis.
2. **Zero Layout Shift:** Containers com alturas fixas ou skeletons durante o carregamento.
3. **Feedback Visual:** Uso de `toast` para mensagens de sucesso/erro sempre na cor de marca ou semântica.

---
*Atualizado em: 12 de Abril de 2026*
