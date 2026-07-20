# Propuesta — Página web CLI Market Academy

**Versión:** 1.0 · **Fecha:** 2026-07-20 · **Estado:** draft para diseño/producto  
**Mock visual:** [`index.html`](./index.html) (abrir en navegador)  
**Assets Optimus portados:**
- Canvas **AnimatedSphere** (hero) · **AnimatedLattice** (medio `#signal`) · **AnimatedTetrahedron** (CTA) · **AnimatedWave** (footer) → `js/optimus-graphics.js`
  - Pause off-screen (IntersectionObserver) · `prefers-reduced-motion` · parallax sutil en sphere · DPR cap 2
  - Lattice: cubo wireframe + plano de scan + pilares (mismo charset mono / depth-sort)
- SVG animados de capabilities (barras, red de nodos, A/B collab, escudo) + filas alternadas
- How-it-works con steps auto-rotating + **code char-reveal** + syntax tint (cmd/flag/key/comment)
- Marquee de métricas + **stack dual marquee** (CLI/API/MCP/SIRI/DDM) + reverse
- Char-in palabra rotativa, counters, CTA spotlight, nav pill + active section, noise overlay
- Scroll cue, syllabus rico desde `content-data.js`, FAQ desde data, track panel fade
- **Google AI Studio (portado, estilo Optimus + claims honestos):**
  - `#lab` terminal sandbox (`market intel` · `procure cart` · `quality-check`)
  - `#semaforo` sliders cobertura/confianza + toggle informal + sync al lab
  - `#lentes` multi-rol (Comercial · Pricing · Research · Growth · Compras)
  - `#pedagogia` micro-ciclo 5 etapas + banner DDM/SIRI
- **Ecosystem brief (portado, sin chart/feed/% fake):**
  - `#moat` 3 pilares (góndola formal ≠ IPC ≠ informal)
  - Tracks: pasos **SIRI/DDM** con prosa + syllabus expandible con **keyConcept**
  - `#pipeline` Ingesta → Normalización → Core → Consumo + **log demo SIMULACIÓN** (sin conteos/% live)
  - `#mcp` 3 cards + explorador **Tools / Resources / Prompts** (JSON ilustrativo) + CTA /tools
  - `#capstone` entregables workbook + rúbrica 4×25%
- CSS: `css/academy.css` · App: `js/academy-app.js` · Data: `js/content-data.js`
- **No portado (a propósito):** chart shock IPC, feed “live”, % ahorro, token sandbox fake, chat Gemini, precios de cadenas inventados

**Referencia:** template Optimus (*The AI platform to build and ship*)  
**Fuente de verdad de contenido:** [`../DOCUMENTACION.md`](../DOCUMENTACION.md)  
**Nota:** `_ref-optimus/` es extracto local gitignored.

---

## 1. Objetivo de la página

| Objetivo | Detalle |
|----------|---------|
| **Primario** | Convertir visitantes en **alumnos** (lista de espera / acceso al track / demo de módulo 0) |
| **Secundario** | Explicar **qué es Academy** (oficio, no blog) y **dos tracks** sin mezclar CTAs de producto |
| **Terciario** | Empujar a producto solo como *next step* post-formación: Intelligence o Procure según track |

**No es** la home de cli-market.dev. Es un **subdominio o ruta dedicada**:

- Preferido: `https://academy.cli-market.dev`  
- Alternativa: `https://cli-market.dev/academy`

---

## 2. Audiencias y jobs-to-be-done

| Segmento | Job en la página | CTA principal |
|----------|------------------|---------------|
| **Compras / facilities** | “¿Esto me enseña a cotizar y ejecutar mejor?” | Track Procure |
| **Pricing / comercial / revenue** | “¿Esto es inteligencia de góndola real, no un curso genérico?” | Track Intelligence |
| **Research / fintech** | “¿Hay rigor metodológico y methods?” | Intelligence + disclaimer IPC |
| **People / L&D / founder** | “¿Puedo formar al equipo con rúbrica?” | Lista org / cohort |
| **Dev / agent builder** | No es el hero; enlace secundario a docs/MCP | cli-market.dev/docs |

**Anti-mezcla en UI:** en un mismo viewport de CTA, no ofrecer “pip install + demo Procure + plan Intelligence” juntos. Selector de track → un CTA.

---

## 3. Mensaje central

### Headline (hero)
**Del acceso a los datos al oficio de decidir.**

### Subhead
CLI Market Academy forma desks y operadores sobre precios de góndola formal en LATAM: **comprar con método** (Procure) o **leer el mercado con rigor** (Intelligence). Mismo motor de datos. Distinta pregunta.

### Promesa en una línea
> Convierte el moat de CLI Market en capacidad organizacional — con workbook, capstone y claims honestos.

### Lo que no prometemos (bloque “honestidad”)
- No somos el IPC oficial  
- No medimos comercio informal  
- No garantizamos un % fijo de ahorro  
- No sustituimos el juicio del desk  

---

## 4. Arquitectura de información (IA)

### Sitemap v2 — journey cliente (implementado en `index.html`)

```
/academy  (o academy.cli-market.dev)
├── #hero            ← outcome + trust strip (una sola pasada)
├── #para-usted      ← 3 puertas de rol + quiz opcional
├── #resultados      ← entregables por track
├── #formato         ← tiempo, prerequisitos, oferta (sin tarjeta)
├── #tracks          ← syllabus (jerga SIRI/DDM como sello)
├── #ejemplo         ← brief de estructura + antes/después
├── #metodo          ← journey I–V + sellos metodológicos
├── #capstone        ← rúbrica + next step de producto (suave)
├── #confianza       ← límites + métricas moat (después del valor)
├── #faq             ← objeciones (tiempo, técnico, cobro, IPC)
└── #cta             ← qué pasa al enviar (≤48 h, sin tarjeta)
```

### Páginas v1.1 (fase 2)

| Ruta | Contenido |
|------|-----------|
| `/academy` | Landing |
| `/academy/intelligence` | Detalle track + syllabus 00–08 |
| `/academy/procure` | Detalle track + syllabus 00–08 |
| `/academy/workbook` | Overview del workbook (no PDF completo público si es gated) |
| `/academy/certificacion` | Niveles + rúbrica |
| `/academy/aplicar` o form Beehiiv/Typeform | Conversión |

---

## 5. Secciones detalladas (copy + UI)

### 5.1 Nav
- Logo: CLI Market **Academy** (wordmark + badge “Academy”)  
- Links: Tracks · Método · Capstone · FAQ  
- CTA derecha: **Empezar** (scroll a #cta o form)  
- Link texto: Producto → cli-market.dev  

### 5.2 Hero
- **Eyebrow:** CLI Market Academy  
- **H1:** Del acceso a los datos al oficio de decidir  
- **Lead:** (subhead de §3)  
- **CTAs:**  
  - Primario: `Elegir mi track` → #tracks  
  - Secundario: `Ver cómo funciona` → #como-funciona  
- **Trust strip (claims canónicos, no MRR inventado):**  
  ~65–70K+ precios · ~40 retailers verificados · 82 en catálogo · refresh ~4 h · multi-país  
- **Visual:** mock de terminal con `market intel brief` **o** split card Procure/Intelligence (no checkout genérico de stock photo)

### 5.3 Problema
Título: **Tener datos no es lo mismo que tener un desk.**  
Dos columnas de dolor:

| Compras | Inteligencia de mercado |
|---------|-------------------------|
| Pestañas, Excel, “el de siempre” | IPC tarde + anécdota de pasillo + scrapers rotos |
| Sin multi-retailer sistemático | 7d leído como “inflación del país” |
| Recompras que consumen el 80% del tiempo | Claims públicos indefendibles |

### 5.4 Qué es / qué no es
Cards en grid 2×N. Reutilizar tabla de `DOCUMENTACION.md`.

### 5.5 Tracks (corazón de la página)
**Toggle o dos paneles grandes:**

| | Procure | Intelligence |
|--|---------|--------------|
| Color acento | Blue primary | Teal/data secondary |
| Verbo | Comprar y ejecutar | Leer y decidir |
| Método | DDM | SIRI |
| Para | Compras, facilities | Comercial, pricing, revenue, research, growth |
| Capstone | Compra del trimestre (ciclo DDM) | Brief + risk + category + methods |
| CTA | Quiero Procure | Quiero Intelligence |

Syllabus en accordion (9 módulos cada uno) — títulos solo en landing; detalle en fase 2.

### 5.6 Métodos
Diagrama horizontal:

```
DDM:  Detect → Compare → Decide → Execute → Improve
SIRI: Sense  → Interpret → Risk  → Insight
```

Microcopy: misma pedagogía de módulo en ambos tracks: Problema → Concepto → Demo → Práctica → Reflexión.

### 5.7 Cómo funciona (journey)
1. Diagnóstico (workbook Parte 0)  
2. Módulos 00–08 del track  
3. Labs con CLI / API / MCP reales  
4. Capstone con rúbrica  
5. Ritual 90 días + CTA de producto según lente  

### 5.8 Capstone & certificación
- Niveles en ladder visual (Foundations → … → Desk Lead / Enterprise)  
- Rúbrica Intelligence (trazabilidad, honestidad, SIRI, multi-lente, accionabilidad)  
- Badge mock “Shelf Analyst” / “Procurement Pro” (diseño, no implica sistema de badges live)

### 5.9 Para quién (multi-lente)
Cinco chips/cards: Comercial · Pricing · Revenue · Research · Growth + card Procure aparte.

### 5.10 Moat & honestidad
Bloque oscuro (navy) con claims + disclaimer grande:

> Inflación y precios observados en **góndola formal online**. No reemplazan el IPC oficial (INEI, DANE, INDEC, IBGE, …). No miden feria ni informal.

### 5.11 FAQ (mínimo 6)
1. ¿Es un curso de e-commerce genérico?  
2. ¿Necesito saber programar?  
3. ¿Qué es shelf inflation vs IPC?  
4. ¿Puedo hacer ambos tracks?  
5. ¿Incluye acceso al producto pago?  
6. ¿En qué idioma está?  
7. ¿Hay cohort en vivo o self-paced? (definir oferta real antes de publicar)  
8. ¿Cómo se certifica?

### 5.12 CTA final
- Título: **Empiece por el oficio, no por otro dashboard.**  
- Form: email + rol (taxonomía 6 audiencias GTM) + track de interés + país  
- Botón: Unirme a la lista / Solicitar acceso  
- Microcopy legal: sin spam; castellano LATAM; datos de góndola formal  

---

## 6. Oferta y conversión (definir antes de launch)

| Opción | Descripción | Cuándo |
|--------|-------------|--------|
| **A — Waitlist** | Solo email + rol + track | Launch soft (recomendado ahora) |
| **B — Self-paced open** | Material público en repo/docs + form de certificación | Si el contenido ya es público |
| **C — Cohort** | Fechas, cupo, precio o bundled con plan Intelligence/Procure | Cuando haya instructor |
| **D — Bundle producto** | Academy gratis/incluida en trial Intelligence o Procure Pro | Experiment GTM |

**Recomendación v1 de página:** Opción **A** en el form, con copy “Acceso prioritario al track + workbook”. No publicar precio inventado.

Campos del form (Beehiiv / Typeform / API propia):

```
email*
rol* (Developer | Abastecimiento | Comercial | Pricing/Revenue | Growth | Otro)
track* (Procure | Intelligence | Ambos | No sé)
pais* (ISO)
empresa (opcional)
consentimiento marketing*
```

---

## 7. Diseño visual

### Principios
- Minimalista, **técnico pero accesible** (brand guidelines)  
- Fondo claro dominante; navy en bloques de rigor/disclaimer  
- Tipografía: **Inter** UI · **JetBrains Mono** en terminales  
- Verde success solo para badges “verified / certified”  
- Evitar stock photos de “equipo sonriente en oficina”  

### Paleta (de brand)

| Token | Hex | Uso en Academy |
|-------|-----|----------------|
| primary | `#0066FF` | CTAs, links, track Procure accent |
| dark | `#0A1628` | Hero text, footer, bloque honestidad |
| success | `#00D75F` | Badge verified / nivel aprobado |
| warning | `#FFB800` | Semáforo calidad “amarillo” |
| error | `#FF3B30` | Semáforo “no publicar” |
| gray | `#8B95A1` | Secondary text |
| teal (data) | `#14B8A6` | Accent track Intelligence |
| purple (data) | `#8B5CF6` | SIRI diagram accent opcional |

### Componentes clave
1. **Track cards** con toggle  
2. **Terminal window** (comando + output fake pero realista, sin inventar métricas de país)  
3. **Semáforo de calidad** (verde/ámbar/rojo) — teachable moment en landing  
4. **Syllabus accordion**  
5. **Ladder de certificación**  
6. **FAQ accordion**  
7. **Form** limpio, mobile-first  

### Responsive
- Mobile: hero apilado, tracks en stack, form sticky CTA inferior opcional  
- Desktop: max-width ~1120px, grid 12  

### Accesibilidad
- Contraste AA en texto  
- Focus visible en CTAs  
- Acordeones con `aria-expanded`  
- No depender solo del color del semáforo (incluye label texto)

---

## 8. SEO y AEO

### Title
`CLI Market Academy — Oficio de compras e inteligencia de góndola LATAM`

### Meta description
`Formación aplicada sobre precios de góndola formal: track Procure (DDM) e Intelligence (SIRI). Workbook, capstone y claims honestos. No es el IPC.`

### H1 único
Del acceso a los datos al oficio de decidir.

### FAQ schema
JSON-LD de las 6–8 preguntas del FAQ.

### AEO / llms.txt (fase 2)
Bloque corto en `/academy` o entrada en llms.txt del sitio:

```
CLI Market Academy: training tracks Procure (buy) and Intelligence (market signal).
Shelf data formal retail LATAM; not official CPI; not informal market.
```

---

## 9. Analytics y eventos

| Evento | Trigger |
|--------|---------|
| `academy_view` | Page load |
| `academy_track_select` | Click Procure / Intelligence |
| `academy_syllabus_open` | Open accordion módulo |
| `academy_cta_click` | Click CTA primario |
| `academy_form_submit` | Submit waitlist |
| `academy_product_click` | Click a cli-market.dev |

UTM default para links desde LinkedIn Day-75:  
`?utm_source=linkedin&utm_medium=social&utm_campaign=academy_launch`

---

## 10. Stack técnico sugerido

| Opción | Pros | Contras |
|--------|------|---------|
| **A. Página en landing world (Next.js)** | Misma marca, deploy unificado | Depende de release de world |
| **B. HTML estático en content (este mock)** | Rápido de revisar copy/diseño | No es prod |
| **C. Framer/Webflow** | Velocidad marketing | Menos control dev |

**Recomendación:** mock HTML en este repo para alineación → implementar en **world landing** (`/academy` o subdominio) con form a Beehiiv.

---

## 11. Criterios de aceptación (launch waitlist)

- [ ] Hero + tracks + disclaimer IPC/informal visibles above/near fold en mobile  
- [ ] Form captura email + rol + track  
- [ ] Cero claims de MRR inventado  
- [ ] Claims de moat alineados a GTM-Hub / marketStats  
- [ ] CTAs no mezclan Procure checkout con pip install  
- [ ] Links a docs/producto en footer  
- [ ] Página en castellano LATAM  
- [ ] Lighthouse a11y razonable (manual check focus/contrast)  

---

## 12. Roadmap de la web

| Fase | Entrega |
|------|---------|
| **P0** | Landing one-page + waitlist (este diseño) |
| **P1** | Páginas por track + syllabus completo |
| **P1** | Embed o descarga gated del workbook overview |
| **P2** | Área alumno (progreso, self-certification) |
| **P2** | Badges / LinkedIn certificate |
| **P3** | Cohort calendar + pagos si aplica |

---

## 13. Copy bank (microtextos)

| UI | Copy |
|----|------|
| Badge hero | Formación aplicada · LATAM |
| CTA primario | Elegir mi track |
| CTA form | Solicitar acceso prioritario |
| Trust | Datos de góndola formal · no IPC oficial |
| Footer legal | CLI Market Academy forma parte del ecosistema CLI Market. |
| Empty state form success | Recibimos su solicitud. Le escribiremos con el siguiente paso del track. |

---

## 14. Entregables en este folder

| Archivo | Rol |
|---------|-----|
| `PROPUESTA_LANDING.md` | Este documento (spec) |
| `index.html` | Mock visual navegable one-page |

Siguiente paso de implementación en producto: portar secciones a la landing de world y conectar form real.
