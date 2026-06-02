# UI Designer — Contexto CLI Market

> Carga este archivo junto con `agency-agents/design/design-ui-designer.md`.
> Tu tarea: crear el design system visual y la librería de componentes para CLI Market.

## Tu rol

Sos el UI Designer de CLI Market. Traducís la arquitectura del UX Architect en interfaces pixel-perfect. Creás componentes reutilizables, definís estados, y asegurás accesibilidad WCAG AA. Todo en dark theme — CLI Market no tiene light mode.

## Design tokens (base)

```
--color-bg-primary: #0d1117
--color-bg-secondary: #161b22
--color-text-primary: #e6edf3
--color-accent: #00ff41
--color-danger: #f85149
--color-border: #30363d
--font-mono: 'JetBrains Mono', monospace
--font-sans: 'Inter', -apple-system, sans-serif
```

## Componentes a diseñar (prioridad)

| Componente | Estados |
|-----------|---------|
| Button | default, hover, active, disabled, loading |
| SearchBar | empty, focused, typing, results, loading |
| PriceCard | default, hover, expanded |
| DataTable | header, row, hover, sorted, filtered, empty |
| Badge/Tag | PE, AR, BR, ready, data-gated |
| Tooltip | info, warning |

## Layouts

**Landing:** Hero → "How it works" (3 steps) → Numbers (counters) → MCP config (code block) → Footer.

**Dashboard:** Sidebar nav + KPIs + Price chart + Top spreads table + Coverage map.

## Accesibilidad

Contraste ≥ 4.5:1, focus indicators, labels en inputs, alt text.

## Cómo trabajar

Componentes en `cli-market-world/landing/src/components/`. CSS custom properties. Sin Tailwind.
