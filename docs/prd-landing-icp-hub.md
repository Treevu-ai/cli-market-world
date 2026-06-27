---
title: PRD — Landing ICP Hub (cli-market.dev)
tags:
  - product
  - prd
  - landing
  - gtm
  - icp
status: In Development — Fase 1+2 shipped 2026-06-27
owner: Ricardo Cuba
updated: 2026-06-27
repos: cli-market-world (landing/)
supersedes: diagnóstico conversación 2026-06-27 · fragmentos de docs/ops/phase4-i18n-landing.md
related:
  - docs/pricing-strategy.md
  - docs/gtm/README.md
  - docs/BRAND.md
  - landing/lib/productDoors.ts
---

# PRD: Landing ICP Hub — cli-market.dev

**Prioridad:** P1 · **Repo:** `cli-market-world` → `landing/` · **Deploy:** Cloudflare Pages (`cli-market.dev`)

## Resumen ejecutivo

La home de **cli-market.dev** mezcla tres compradores (devs, operadores de compras, analistas) y un actor supply-side (retailers) en un **scroll monolítico** de ~10 secciones. El hero dice “elige tu puerta”, pero los CTAs globales (navbar, FAQ, CTA final) empujan solo al ICP **Build**.

**Decisión:** convertir `/` en un **hub router de ICP** — una pantalla principal que enruta a spokes dedicados. El hub comparte credibilidad (métricas, trust); cada spoke lleva pitch, pricing y FAQ de su audiencia.

**No es** un rediseño visual completo ni un cambio de pricing. Es **reorganización de arquitectura de información** alineada a `docs/pricing-strategy.md`.

| Hoy | Target |
|-----|--------|
| `/` = pitch de los 3 productos en secuencia | `/` = selector de ICP + proof compartido |
| CTA primario = Get API Key (dev) | CTA primario = el de la tarjeta elegida |
| Procure + Intelligence como secciones inline | Spokes: dominio hermano o rutas dedicadas |
| SideNav 9 puntos mezclando ICPs | Nav por producto / spoke |
| WhoItsFor + UseCases + Hero doors = triple redundancia | Una sola bifurcación en hub |

---

## 1. Problem Statement

### Quién sufre el problema

| Persona | Qué espera al llegar | Qué encuentra hoy |
|---------|----------------------|-------------------|
| **Developer / agent builder** | Quickstart, API, MCP, pricing Build | Contenido correcto pero enterrado tras secciones Procure/Intelligence |
| **Operador de compras** (Procure) | Comparar, aprobar, pagar — sin código | Scroll de dev + analista antes de ver Procure; CTA final = `pip install` |
| **Analista / fintech** (Intelligence) | Piloto, spreads, inflación | Sección Intelligence existe pero compite con 8 secciones previas; pricing en bloque separado del hub |
| **Retailer supply-side** | Listar catálogo gratis | Link suelto en navbar; **no** aparece en las “tres puertas” del hero |

### Evidencia (código actual)

- Home stack: `Hero → TrustBar → Solution → UseCases → Procure → Intelligence → Metrics → WhoItsFor → Pricing → FAQ → FinalCTA` (`landing/app/page.tsx`).
- Hero CTAs: `getApiKey` + `watchDemo` — ambos dev (`landing/components/Hero.tsx`, `landing/lib/ctaCopy.ts`).
- Navbar `signUp` → `/#pricing` (Build only).
- Pricing público: tab Build visible; Procure solo vía `?audience=procure`; Intelligence fuera de `#pricing` (`landing/lib/pricingAudiences.ts`).
- Procure: redirect a `procurecopilot.com` (`landing/app/procure/page.tsx`) pero home conserva 2 bloques Procure inline.
- FAQ + Final CTA: copy 100% developer (`pip install`, MCP).

### Coste de no resolver

- **Bounce** de compradores y analistas que interpretan cli-market.dev como “solo para devs”.
- **SEO diluido**: una URL compite por keywords de API, procurement e intelligence.
- **GTM incoherente**: posts de Procure/Intelligence mandan tráfico a una landing que no cierra su loop.
- **Canibalización percibida**: mezclar `pip install` con Procure en la misma página viola regla GTM (`AGENTS.md`, `docs/pricing-strategy.md`).

---

## 2. Goals & Success Metrics

| Goal | Metric | Baseline | Target | Window |
|------|--------|----------|--------|--------|
| Claridad de routing | % sesiones con click en tarjeta ICP hub (evento `icp_door_click`) | — | ≥ 35% de sesiones home | 30 días post-launch |
| Conversión dev | `pip_install_intent` desde `/` o `/build` | medir pre-launch | ≥ baseline (no regresión) | 30 días |
| Conversión Procure | Clicks outbound → procurecopilot.com desde hub | medir pre-launch | +20% vs. baseline | 30 días |
| Conversión Intelligence | `contact` con `topic=intelligence` desde hub/spoke | medir pre-launch | +15% vs. baseline | 30 días |
| Retailers supply | Visitas `/retailers` con origen `/` | medir pre-launch | +10% vs. baseline | 30 días |
| Scroll depth | Mediana secciones vistas en `/` | ~7–9 | ≤ 3 (hub corto) | 14 días |

**Instrumentación mínima:** extender `recordPipInstallIntent` / funnel beacon con eventos `icp_door_click`, `icp_spoke_view`, `icp_outbound_procure`.

---

## 3. Non-Goals

- Rediseño visual completo (tokens `docs/BRAND.md` se mantienen).
- Cambios de pricing o tiers (`docs/pricing-strategy.md` intacto).
- Migrar Procure de `procurecopilot.com` de vuelta a cli-market.dev.
- Reescribir `/docs`, `/retailers`, `/intelligence-pilot-es` — solo enlazarlos como spokes.
- i18n centralizado (se mantiene patrón inline ES/EN por componente).
- Contenido GTM / calendario (`cli-market-content`).

---

## 4. User Personas & Stories

### Persona A — **Morgan, AI Agent Builder**
Integra MCP en Cursor/Claude. Necesita API key, docs, pricing Build.

**Story A1:** Como developer, quiero ver en 5 segundos que cli-market.dev es para mí, para obtener API key sin leer sobre procurement.

**Acceptance:**
- [ ] Tarjeta Build visible above the fold con CTA “Get API Key”.
- [ ] Spoke `/build` o ancla `#build` con pricing Starter/Pro y link a `/docs`.
- [ ] FAQ del spoke menciona `pip install`, MCP, límites req/día.

### Persona B — **Camila, Gerente de Compras**
Restaurante/hotel. No escribe código. Necesita Procure.

**Story B1:** Como operadora de compras, quiero entrar por una puerta “Compras” y llegar a Procure sin ver terminal ni MCP.

**Acceptance:**
- [ ] Tarjeta Procure en hub con CTA “Ver Procure →” a `procurecopilot.com/procure`.
- [ ] Home `/` **no** incluye sección ProcureCopilot completa post-migración.
- [ ] Navbar incluye entrada “Procure” o “Compras” (no solo link dev).

### Persona C — **Diego, Analista Fintech**
Pricing/trade marketing. Necesita piloto Intelligence $300–500.

**Story C1:** Como analista, quiero ver tiers de piloto y solicitar demo sin confundirme con API self-serve.

**Acceptance:**
- [ ] Tarjeta Intelligence en hub con CTA “Solicitar piloto”.
- [ ] Spoke `/intelligence` (nueva ruta) con Commerce Pulse embed, tiers S/M/L, one-pager link.
- [ ] Pricing Build **no** aparece como CTA primario en spoke Intelligence.

### Persona D — **Lucía, Retailer (supply-side)**
Dueña de tienda online. Quiere indexación gratis.

**Story D1:** Como retailer, quiero encontrar “Listar mi tienda” sin confundirme con Procure (compradores).

**Acceptance:**
- [ ] Link secundario en hub: “¿Eres retailer? → /retailers”.
- [ ] Copy distingue **supply** (listar catálogo) vs **demand** (comprar con Procure).
- [ ] Tarjeta hub **no** usa la palabra “retailer” para Procure.

---

## 5. Solution Overview

### Modelo hub-and-spoke

```
                    ┌─────────────────────┐
                    │   cli-market.dev/   │
                    │   HUB (router)      │
                    │   · trust / metrics │
                    │   · 3 tarjetas ICP  │
                    │   · link retailers  │
                    └──────────┬──────────┘
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
    ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
    │ Build spoke │    │Procure spoke │    │Intelligence     │
    │ /build o     │    │procurecopilot│    │spoke /intelligence│
    │ /docs focus  │    │.com/procure  │    │+ contact pilot  │
    └─────────────┘    └──────────────┘    └─────────────────┘
           │
    ┌──────┴──────┐
    │  /retailers │  (supply — link secundario desde hub)
    └─────────────┘
```

### Principios de diseño

1. **Una bifurcación, una vez** — el hub presenta las puertas; los spokes profundizan.
2. **CTA = ICP del contexto** — prohibido CTA global dev en páginas no-dev.
3. **Credibilidad compartida** — métricas data-gate (`MARKET_STATS`) solo en hub o footer; claims GTM Hub únicamente.
4. **Procure vive en dominio hermano** — hub solo enruta; no duplicar checkout Procure en cli-market.dev.
5. **Anti-canibalización GTM** — hub no mezcla `pip install` y Procure en el mismo bloque de CTA primario.

### Wireframe hub (contenido)

```
┌────────────────────────────────────────────────────────────┐
│ NAV: Build · Procure · Intelligence · Docs · Retailers     │
├────────────────────────────────────────────────────────────┤
│ EYEBROW: Inteligencia de precios retail en LATAM           │
│ H1: Precios verificados. Elige cómo los usas.             │
│ SUB: Una capa de data — tres formas de consumirla.         │
│ CHIPS: 63K+ precios · 41 retailers · MCP                   │
│                                                            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │
│ │ CLI Build   │ │Procure      │ │Intelligence │             │
│ │ Devs        │ │ Compras     │ │ Analistas   │             │
│ │ Free·$9·$49 │ │ desde $29   │ │ desde $300  │             │
│ │ [API Key →] │ │ [Procure →] │ │ [Piloto →]  │             │
│ └─────────────┘ └─────────────┘ └─────────────┘             │
│                                                            │
│ ¿Eres retailer? Listar catálogo gratis → /retailers       │
├────────────────────────────────────────────────────────────┤
│ TRUST BAR (logos / métricas)                               │
├────────────────────────────────────────────────────────────┤
│ CÓMO FUNCIONA (3 pasos genéricos — sin demo por ICP)       │
├────────────────────────────────────────────────────────────┤
│ DATA MOAT (métricas verificables — compacto)               │
├────────────────────────────────────────────────────────────┤
│ FOOTER (links por producto)                                │
└────────────────────────────────────────────────────────────┘
```

---

## 6. Information Architecture

### Rutas target

| Ruta | Rol | Fuente actual |
|------|-----|---------------|
| `/` | Hub router | Refactor `landing/app/page.tsx` |
| `/build` | Spoke developer (pricing Build + quickstart teaser) | Nuevo — extraer de `#pricing` + Hero dev |
| `/intelligence` | Spoke analista | Nuevo — migrar `IntelligenceSection` |
| `/retailers` | Spoke supply | **Existe** — sin cambios mayores |
| `/docs` | Spoke dev (técnico) | **Existe** |
| `/procure` | Redirect | **Existe** → procurecopilot.com |
| `/#pricing` | Redirect → `/build#pricing` | Redirect 301 o client replace |

### Navegación

**TOP_NAV propuesto:**

| id | ES | EN | href |
|----|----|----|------|
| build | Build | Build | `/build` |
| procure | Procure | Procure | `procurecopilot.com/procure` (external) |
| intelligence | Intelligence | Intelligence | `/intelligence` |
| docs | Docs | Docs | `/docs` |

- “Para retailers” → `/retailers` (secundario, mint — conservar posición actual o mover a footer).
- `signUp` contextual: en hub → `/build`; en spoke → CTA del spoke.

**SideNav:** eliminar en hub (página corta). En spokes, dots solo de secciones **del mismo ICP**.

### Secciones a retirar del hub `/`

| Componente | Acción |
|------------|--------|
| `UseCasesSection` | Mover demos a spokes (`/build`, `/intelligence`) o `/tools` |
| `ProcureCopilotSection` | Eliminar del hub — enlace a dominio hermano |
| `IntelligenceSection` | Mover a `/intelligence` |
| `WhoItsForSection` | **Eliminar** (redundante con hub cards) |
| `Pricing` (Build) | Mover a `/build` |
| `FAQ` (dev-only) | Mover a `/build`; FAQ Intelligence en spoke |
| `FinalCTASection` | Reemplazar por CTAs en tarjetas hub o eliminar |

### Secciones a conservar en hub

| Componente | Notas |
|------------|-------|
| `Hero` | Refactor → hub cards centrales, sin CTA dev duplicado |
| `TrustBar` | Credibilidad compartida |
| `SolutionSection` | 3 pasos genéricos — acortar copy paso 3 |
| `MetricsSection` | Compacto — data moat |
| `Footer` | Ya tiene columnas por producto |

---

## 7. Copy & Messaging

### Mensaje hub (canónico)

| Elemento | ES | EN |
|----------|----|----|
| H1 | Precios verificados. Elige cómo los usas. | Verified prices. Choose how you use them. |
| Subhead | Una capa de data verificada — tres productos para construir, comprar o analizar. | One verified data layer — three products to build, buy, or analyze. |
| Retailer link | ¿Vendes en retail? Indexa tu catálogo gratis → | Sell retail? List your catalog free → |

### Glosario (evitar confusión)

| Término | Significa | No confundir con |
|---------|-----------|------------------|
| **Build / CLI Build** | API, MCP, devs | Procure |
| **Procure Copilot** | App de compras (demand) | Retailers supply |
| **Intelligence** | Datos, índices, pilotos | CLI Market Pro |
| **Para retailers** | Supply-side listing gratis | Equipos que compran |

### Claims

Solo métricas **data-gate** vía `MARKET_STATS` / `make gate`. Sin inventar números. Ver `docs/gtm/README.md`.

---

## 8. Technical Considerations

### Repo y deploy

- **Único repo afectado:** `cli-market-world` → `landing/`
- **Build:** `cd landing && npm run build` → Cloudflare Pages
- **CI:** `.github/workflows/deploy-landing-cloudflare.yml` (push `landing/`)

### Archivos clave a tocar

| Archivo | Cambio |
|---------|--------|
| `landing/app/page.tsx` | Hub slim |
| `landing/app/build/page.tsx` | **Nuevo** spoke |
| `landing/app/intelligence/page.tsx` | **Nuevo** spoke |
| `landing/components/Hero.tsx` | Hub variant |
| `landing/lib/siteNav.ts` | TOP_NAV, SECTION_NAV |
| `landing/lib/ctaCopy.ts` | CTAs por ICP |
| `landing/lib/productDoors.ts` | Fuente de verdad tarjetas (ya existe) |
| `landing/components/Navbar.tsx` | Nav + signUp contextual |
| `landing/public/llms.txt` | Actualizar entry points por ICP |

### Redirects / SEO

| From | To | Tipo |
|------|-----|------|
| `/#pricing` | `/build#pricing` | replaceState + canonical |
| `/#procure` | `procurecopilot.com/procure` | redirect externo |
| `/#intelligence` | `/intelligence` | redirect interno |
| `/#who-its-for` | `/` | 301 o hash ignore |

- Actualizar `canonical` en layout por ruta.
- Actualizar `llms.txt` y `llms-full.txt` con hub + spokes.
- Revisar `docs/seo-audit.md` post-deploy.

### Checkout / billing (no romper)

- `?audience=procure` en pricing: mantener en `/build` o página oculta hasta sunset checkout Procure en cli-market.dev.
- `PaymentReturnBanner`: seguir funcionando en ruta que renderice Procure panel legacy.

### Analytics / funnel

Eventos nuevos (mínimo):

```typescript
// landing/lib/funnel.ts — extender
icp_door_click: { door: "build" | "procure" | "intelligence" | "retailers" }
icp_spoke_view: { spoke: "build" | "intelligence" | "retailers" }
icp_outbound_procure: { source: "hub" | "nav" | "footer" }
```

---

## 9. Implementation Phases

### Fase 1 — Hub slim (MVP)

**Scope:** Reorganizar `/` sin crear rutas nuevas aún.

- [ ] Hero = 3 tarjetas centrales (`ProductDoorCard`); quitar CTAs dev duplicados del hero.
- [ ] Eliminar `WhoItsForSection`, `ProcureCopilotSection`, `IntelligenceSection` del scroll home.
- [ ] Mover `Pricing` + `FAQ` + `FinalCTASection` fuera del home **o** colapsar FAQ/CTA.
- [ ] Actualizar `TOP_NAV` con Build / Procure / Intelligence.
- [ ] Link retailers secundario bajo tarjetas.

**Gate:** Home ≤ 4 secciones visibles (Hero, Trust, Solution, Metrics).

### Fase 2 — Spokes dedicados

- [ ] Crear `/build` con pricing Build, FAQ dev, quickstart teaser → `/docs`.
- [ ] Crear `/intelligence` migrando `IntelligenceSection` + contact CTA.
- [ ] Redirects hash legacy (`/#pricing`, `/#intelligence`).
- [ ] Navbar `signUp` → `/build` desde hub.

**Gate:** Cada ICP tiene URL única compartible en GTM.

### Fase 3 — Polish & GTM sync

- [ ] Mover `UseCasesSection` demos a spokes correspondientes.
- [ ] Actualizar `llms.txt`, sitemap, OG tags por ruta.
- [ ] Sync copy en `cli-market-content` calendario (links por ICP).
- [ ] Verificar data-gate en creativos hub.

**Gate:** `npm run build` + smoke test 4 rutas + lighthouse ≥ baseline.

---

## 10. Launch Plan

| Phase | Audience | Success gate |
|-------|----------|--------------|
| **Preview** | Team + staging CF | Hub ≤ 4 secciones; 3 tarjetas funcionales; redirects hash OK |
| **Soft launch** | 100% tráfico orgánico | Error rate 0; funnel events firing |
| **GTM update** | Content repo links | Posts Procure → procurecopilot; posts dev → /build; Intelligence → /intelligence |

**Rollback:** revert deploy Cloudflare (commit anterior `landing/`). Redirects hash son client-side — rollback no deja links rotos permanentes.

---

## 11. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tráfico legacy a `/#pricing` | High | Med | Redirect `/build#pricing` + 30d monitor Search Console |
| Checkout Procure `?audience=procure` | Med | High | Mantener panel oculto en `/build` hasta sunset documentado |
| SEO temporal dip | Med | Med | Canonicals + sitemap; no eliminar contenido — mover |
| Confusión retailer vs Procure | Med | Med | Copy glossary §7; user test 3 personas |
| Scope creep (redesign visual) | High | Med | Non-goals §3; diff mínimo por Fase 1 |

---

## 12. Open Questions

| # | Question | Owner | Deadline |
|---|----------|-------|----------|
| 1 | ¿Spoke Build = `/build` o consolidar todo en `/docs`? | PM + Eng | Antes Fase 2 |
| 2 | ¿Sunset fecha panel Procure en cli-market.dev pricing? | PM | Antes Fase 2 |
| 3 | ¿SideNav se elimina globalmente o solo en hub? | Design | Fase 1 |
| 4 | ¿Tarjeta hub Procure abre nueva pestaña siempre? | GTM | Fase 1 |
| 5 | ¿Intelligence spoke bilingüe o redirect a `/intelligence-pilot-es`? | PM | Fase 2 |

---

## 13. Acceptance Criteria (Definition of Done)

### Hub `/`

- [ ] Above the fold: 3 tarjetas ICP con CTA independiente (Build, Procure, Intelligence).
- [ ] Link “Para retailers” visible sin scroll en desktop.
- [ ] No existe sección `ProcureCopilotSection` ni `IntelligenceSection` en home.
- [ ] No existe `WhoItsForSection` en home.
- [ ] CTA navbar no fuerza “Get API Key” como única acción primaria sin contexto.
- [ ] ≤ 4 secciones de contenido en scroll home (excl. footer).

### Spoke `/build`

- [ ] Pricing tabs Build (Starter, Pro, Enterprise).
- [ ] FAQ con `pip install`, MCP, refresh cadence.
- [ ] CTA primario: Get API Key / Start free.

### Spoke `/intelligence`

- [ ] Tiers Pilot S/M/L visibles.
- [ ] Commerce Pulse embed.
- [ ] CTA: Solicitar piloto → `/contact?topic=intelligence`.
- [ ] Sin pricing Build above the fold.

### Cross-cutting

- [ ] ES/EN en todos los componentes tocados.
- [ ] `npm run build` pasa.
- [ ] Eventos funnel `icp_door_click` instrumentados.
- [ ] `llms.txt` actualizado.
- [ ] Sin claims fuera de data-gate.

---

## Appendix A — Mapping diagnóstico → acción

| Hallazgo diagnóstico | Acción PRD |
|----------------------|------------|
| CTA hero/nav solo dev | §5 wireframe + §6 signUp contextual |
| Redundancia tres puertas ×4 | Eliminar WhoItsFor; hub único |
| Nav no refleja ICPs | §6 TOP_NAV |
| Pricing hub incompleto | Spoke `/build` + `/intelligence` |
| Procure en home pero dominio externo | Eliminar secciones inline; enlace hub |
| FAQ/CTA final dev-only | Mover a `/build` |
| Retailers huérfano del hub | Link secundario §5 |
| Drift phase4 doc | Supersedes frontmatter |

## Appendix B — Referencias código

- Home composition: `landing/app/page.tsx`
- Product doors data: `landing/lib/productDoors.ts`
- Pricing audiences: `landing/lib/pricingAudiences.ts`
- Nav config: `landing/lib/siteNav.ts`
- Pricing strategy: `docs/pricing-strategy.md`
- Brand tokens: `docs/BRAND.md`

---

**Status:** Draft · **Next step:** Aprobación → Fase 1 en branch `cursor/landing-icp-hub-*`
