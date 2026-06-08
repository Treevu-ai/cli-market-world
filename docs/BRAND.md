# Identidad visual — CLI Market (v1.1)

**Última actualización:** 2026-06-08  
**Estado:** Aprobado para implementación gradual. Decisión pendiente del founder: verde acción `#C8FF00` vs mint datos `#3AFECF` en CTAs globales.

## Propuesta de valor (copy madre)

> **La capa programable del retail físico de LatAm.**

No somos marketplace (Amazon, Mercado Libre) ni storefront SaaS (Shopify). Somos **infraestructura + datos verificados + agentes** — retail programable, comercio máquina-a-máquina.

## Mantra visual

```
BLACK · WHITE · NEON (acción) · MINT (datos)

DATA · NETWORKS · COMMERCE

NO PEOPLE · NO ROBOTS · ONLY INFRASTRUCTURE
```

Referencias de tono (no de copiar pixel a pixel):

| Uso | Referencia |
|-----|------------|
| Landing Build, API, MCP | Stripe · Linear · Vercel |
| Métricas, spreads, inflación | Bloomberg (terminal) |
| Intelligence / Price Pulse | Bloomberg + densidad Palantir |
| Procure (operadores) | Misma paleta, **menos terminal** — confianza operativa |

Evitar parecer: e-commerce genérico, IA con ilustraciones stock, crypto billboard en todo el producto.

---

## Tokens semánticos (CSS)

Implementados en `landing/app/globals.css` y `procure-copilot/app/globals.css`. Usar **nombres semánticos** en código nuevo; `--cm-mint` sigue siendo alias de `--cm-data` por compatibilidad.

| Token | Valor | Rol |
|-------|-------|-----|
| `--cm-void` | `#000000` | Hero marketing, fondos 1:1 social — **no** en app/docs densos |
| `--cm-canvas` | `#0a0a0b` | Fondo principal producto (preferir sobre negro puro) |
| `--cm-ink` | `#ffffff` | Tipografía principal sobre oscuro |
| `--cm-action` | `#c8ff00` | CTA primario, glow, énfasis marketing |
| `--cm-action-glow` | `#dfff00` | Highlights, halos 1px |
| `--cm-data` | `#3afecf` | Links, código, estados OK, gráficos de precios |
| `--cm-signal` | `#ffe500` | Alertas, métricas de crecimiento, inflación |
| `--cm-surface-card` | `#111111` | Cards |
| `--cm-surface-container` | `#1c1c1c` | Contenedores, paneles |
| `--cm-text-secondary` | `#7a7a7a` | Texto secundario |
| `--cm-radius-lg` | `24px` | Cards, secciones marketing |
| `--cm-radius-md` | `12px` | Inputs, chips |
| `--cm-radius-sm` | `8px` | Tablas, badges densos |
| `--cm-radius-pill` | `9999px` | CTAs pill |

Alias legacy (no usar en componentes nuevos):

- `--cm-mint` → `--cm-data`
- `--cm-background` → `--cm-canvas`

---

## Dos modos de superficie

### Terminal (default)

**Productos:** CLI Market Build, Intelligence, docs técnicos, MCP, API.

- Grid de nodos, wireframes, grafos, terminales
- Glow verde en bordes activos (`energy-border-active`)
- Tipografía display **muy grande** solo en hero y social
- Iconografía outline (Linear / Vercel / Stripe)

Clase CSS: `brand-mode-terminal` (default en `:root`)

### Operations

**Productos:** Procure Copilot, outbound compras, demos a gerentes.

- Misma paleta, **50% menos glow** (`--cm-glow-strength: 0.35`)
- Más espacio en blanco entre bloques, copy orientado a operación
- Métricas legibles, no “billboard”
- Sin jerga Palantir / red de agentes autónomos en hero

Clase CSS: `brand-mode-operations` — aplicar en secciones Procure y dashboard operativo.

---

## Matriz por producto

| Producto | ICP | Modo | Color dominante | Visual clave | Evitar en posts |
|----------|-----|------|-----------------|--------------|-----------------|
| **CLI Market Build** | Agent builders | Terminal | `--cm-data` + `--cm-action` en hero | Nodos MCP, `pip install`, terminal | Procure, restaurantes |
| **Intelligence** | Pricing, fintech | Terminal + Signal | `--cm-signal` en gráficos | Spreads, inflación góndola, export | Checkout, dashboard |
| **Procure** | Compras, horeca | Operations | `--cm-data` (acción moderada) | Flujo compare → approve → checkout | `pip install` en mismo post |

Pricing canónico: `docs/pricing-strategy.md`.

---

## Matriz por canal

| Canal | Formato | Modo | Estructura |
|-------|---------|------|------------|
| **cli-market.dev** | Web | Terminal (Procure = Operations block) | Stripe-like: hero métricas → prueba → pricing |
| **LinkedIn / X** | 1:1 | Terminal | Headline → **métrica gigante** → visual red → insight |
| **PyPI / README** | Markdown | Terminal | Negro en badges opcionales; sin imágenes stock |
| **Outbound Procure** | Email / deck | Operations | Beneficio operativo, un CTA a `#procure` |
| **Docs / Legal** | Lectura larga | Neutral | Sin glow; `--cm-canvas` + texto `--cm-on-surface-variant` |

---

## Tipografía

| Rol | Familia | Fallback web |
|-----|---------|--------------|
| Display / métricas hero | Geist Sans | Inter |
| UI / body | Inter | system-ui |
| Código / terminal | JetBrains Mono | ui-monospace |

**Regla gigante:** solo en hero y piezas 1:1. Ejemplo:

```
50K+
PRECIOS VERIFICADOS
```

En pricing, tablas y forms: escala normal (16–18px body).

---

## Estilo visual

### No

- Gradientes arcoíris
- Ilustraciones genéricas IA
- Robots humanoides
- Stock photos / personas trabajando
- Iconos rellenos (salvo micro-estados UI: ✓, ⚠)

### Sí

- Red de nodos (patrón oficial): retailers ↔ API ↔ agentes
- Wireframes, data maps, grafos, dashboards
- Líneas 1px con glow `--cm-action-glow` (modo Terminal)
- Bordes `--cm-radius-lg` en marketing; `--cm-radius-sm` en datos densos

### Patrón nodos (oficial)

```
○────○
│    │
○────○
```

Representa: MCP, APIs, retailers, agentes. No tiendas dibujadas, no personas.

### Gráficos

- Fondo `--cm-canvas` o `--cm-void`
- Línea `--cm-data` o `--cm-signal` (Intelligence)
- Área sombreada + glow suave
- Estética terminal financiera

---

## Reglas de implementación (equipo)

1. **Neón (`--cm-action`) en &lt;15% del viewport** por página — CTA, una métrica hero, un acento de gráfico.
2. **Métricas solo data-gate** — usar `MARKET_STATS` / `make gate` en content repo; no inventar cifras en diseño.
3. **Procure = Operations** — clase `brand-mode-operations` en `#procure` y app Worker.
4. **Negro puro `#000`** solo hero y assets sociales; producto usa `--cm-canvas`.
5. **Founder lock** — antes de migrar todos los `btn-mint` a `--cm-action`, validar contraste WCAG en móvil LATAM.

---

## Componentes

| Componente | Tokens | Notas |
|------------|--------|-------|
| Hero Build | `--cm-void`, `--cm-action`, métricas display | Subhead en `--cm-text-secondary` |
| CTA primario | `btn-mint` (hoy `--cm-data`) → futuro `btn-action` | Un CTA principal por fold |
| Cards | `card-cyber`, `--cm-surface-card`, `--cm-radius-lg` | Borde `outline-variant` |
| Terminal / code | `--cm-data`, JetBrains Mono | Fondo `black/30` |
| Alertas moat | `--cm-signal` | Data-gate stale |
| Intelligence charts | `--cm-signal` línea, `--cm-data` área | |

---

## Ilustraciones (sistema)

**Tema:** Agent Commerce Network

```
Retailers → CLI Market → AI Agents
```

Solo flujos y nodos. Sin personas, sin fachadas de supermercado.

---

## Archivos de referencia

| Archivo | Contenido |
|---------|-----------|
| `docs/BRAND.md` | Este documento |
| `landing/app/globals.css` | Tokens + modos Terminal/Operations |
| `landing/DESIGN.md` | Auditoría histórica (Ollama/minimal) |
| `docs/pricing-strategy.md` | Tres capas comerciales |
| `../cli-market-content/linkedin/STYLE-es.md` | Copy LATAM |
| `ops/generate_all_linkedin_assets.py` | Assets 1:1 (respetar data-gate) |

---

## Checklist antes de publicar creative

- [ ] ¿Métricas pasan data-gate?
- [ ] ¿Canal alineado con producto (sin mezclar pip + Procure)?
- [ ] ¿Modo correcto (Terminal vs Operations)?
- [ ] ¿Neón &lt;15% del layout?
- [ ] ¿Sin personas/robots/stock?