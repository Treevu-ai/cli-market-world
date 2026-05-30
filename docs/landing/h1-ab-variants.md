# CLI Market — Variantes A/B del H1 (Hero)

**Control en producción (PR #44):** promesa-paraguas  
**Subtítulo fijo recomendado:** mantener el actual en todas las variantes para aislar el efecto del H1.

> *Los agentes de IA ya buscan, comparan y compran solos. CLI Market es la API que los conecta con 30 retailers verificados en 8 países — y el canal donde tu tienda aparece ante ellos.*

---

## Cómo leer este doc

| Eje | Qué prueba |
|-----|------------|
| **Paraguas** | Posicionamiento de categoría ("capa programable") |
| **Concreto** | Prueba tangible (API, retailers, checkout, precios) |
| **Urgencia** | FOMO / economía de agentes |
| **Dual** | Builders + retailers en una sola línea |

**Métrica primaria:** clic en Puerta A (*Empezar con la API — gratis →*).  
**Métrica secundaria:** clic Puerta B, scroll a `#casos`, scroll a `#pricing`.  
**Segmentar por:** referrer (GitHub / LinkedIn / orgánico), idioma, dispositivo.

---

## Variante A — Control (paraguas)

**ES:** `La capa programable del retail físico de LatAm.`  
**EN:** `The programmable layer for physical retail in LatAm.`

**Hipótesis:** El comprador técnico y el retailer entienden el *rol* de CLI Market antes que la feature list. Funciona cuando el visitante ya sabe que busca infraestructura, no un marketplace.

**Fortalezas:** Coherente con About ("infraestructura programable"). Diferencia de agregadores. Escala a fintechs y bureaus.

**Riesgos:** "Capa programable" puede sonar abstracto en tráfico frío (LinkedIn retail, no-dev).

---

## Variante B — Concreta (API + cobertura)

**ES:** `Una API. 30 retailers verificados. 8 países.`  
**EN:** `One API. 30 verified retailers. 8 countries.`

**Hipótesis:** Cifras y entregable concreto reducen fricción cognitiva en devs que llegan sin contexto previo.

**Fortalezas:** Escaneable en 2 s. Refuerza la barra de métricas sin repetirla. Familiar para compradores de API (Stripe, Twilio pattern).

**Riesgos:** Suena a catálogo de datos, no a checkout/agentes. Retailers pueden sentirse secundarios.

**Cuándo priorizar:** Tráfico desde GitHub, PyPI, docs técnicas, búsqueda "retail API LatAm".

---

## Variante C — Agente primero (economía de agentes)

**ES:** `Los agentes ya compran solos. Conéctalos al retail de LatAm.`  
**EN:** `Agents already buy on their own. Connect them to LatAm retail.`

**Hipótesis:** El dolor de "agentes autónomos sin infra" convierte mejor que categoría abstracta en audiencias AI/agentic (MCP, LangChain, Cursor).

**Fortalezas:** Narrativa del PRD. Puerta A encaja naturalmente. Genera curiosidad en builders.

**Riesgos:** Retailers pueden no verse reflejados. "Compran solos" puede generar escepticismo si no hay prueba inmediata (demo GIF ayuda).

**Cuándo priorizar:** Campaña LinkedIn agentic, posts MCP, conferencias AI.

---

## Variante D — Dual audiencia (builders + retailers comprimido)

**ES:** `La API para agentes. El canal para tu tienda. Gratis.`  
**EN:** `The API for agents. The channel for your store. Free.`

**Hipótesis:** Comunicar doble puerta en el H1 refuerza el layout de dos CTAs y evita que retailers se sientan escondidos.

**Fortalezas:** Alineado 1:1 con wireframe doble puerta. "Gratis" desarma objeción en ambos lados.

**Riesgos:** Tres ideas en una línea — puede sentirse apretado en mobile. Menos diferenciación vs agregadores.

**Cuándo priorizar:** Tráfico mixto (landing general, prensa, referidos sin segmentar).

---

## Variante E — Data moat (analysts / bureaus / fintechs)

**ES:** `43K+ precios de góndola. Una API. Cero scraping.`  
**EN:** `43K+ shelf prices. One API. Zero scraping.`

**Hipótesis:** La prueba numérica convierte perfiles data-driven que evalúan credibilidad antes que integración.

**Fortalezas:** Ataca objeción #1 de analysts ("¿de dónde salen los datos?"). "Cero scraping" es claim diferenciador.

**Riesgos:** Aleja el mensaje de checkout/agentes. Retailers no se ven. Cifra requiere mantenerse sincronizada con live stats.

**Cuándo priorizar:** Outreach a bureaus, fintechs, equipos de pricing. Tráfico desde `#casos` / sección cobertura.

---

## Variante F — Checkout / producción (Free → Pro)

**ES:** `Del search al checkout autónomo en retail físico.`  
**EN:** `From search to autonomous checkout in physical retail.`

**Hipótesis:** "Checkout autónomo" es el salto Free→Pro; un H1 orientado a producción filtra curiosos y atrae buyers con intent de deploy.

**Fortalezas:** Conecta Flujo → Planes. Lenguaje de producto, no de categoría.

**Riesgos:** Promesa fuerte — exige que demo y Planes estén visibles al scroll. Puede intimidar en tráfico exploratorio.

**Cuándo priorizar:** Retargeting, visitantes que ya vieron la landing, tráfico desde `#pricing`.

---

## Matriz rápida de decisión

| Variante | Dev / agente | Retailer | Analyst / bureau | Tráfico frío |
|----------|:------------:|:--------:|:----------------:|:------------:|
| A Control | ●●● | ●● | ●●● | ●● |
| B Concreta | ●●●● | ● | ●●● | ●●●● |
| C Agente | ●●●● | ●● | ● | ●●● |
| D Dual | ●●● | ●●●● | ●● | ●●● |
| E Data moat | ●● | ● | ●●●● | ●● |
| F Checkout | ●●●● | ● | ●●● | ●● |

---

## Implementación mínima (sin infra A/B)

1. Rotar manualmente 1 semana por variante (mismo subtítulo y CTAs).
2. Registrar en bitácora: variante activa + clics Puerta A/B (PostHog, Plausible o evento `data-hero-variant` en analytics).
3. Mínimo ~200 sesiones por variante antes de declarar ganador en tráfico orgánico bajo.

### Modos de operación

| Modo | Env | Comportamiento |
|------|-----|----------------|
| **Fijo** | `NEXT_PUBLIC_HERO_VARIANT=c` | Todos ven `c`. Cambiar = redeploy. |
| **Runtime** | `NEXT_PUBLIC_HERO_AB=1` | Cookie sticky 30 días, random uniforme a–f. Sin redeploy. |

**Runtime — activar en producción (Cloudflare Pages):**

1. Build env: `NEXT_PUBLIC_HERO_AB=1`
2. Runtime env: `HERO_AB=1` (para middleware en `landing/functions/_middleware.ts`)
3. Redeploy una vez. Luego rotás pesos o pausás AB cambiando env sin tocar copy.

**Override manual / QA:** `https://cli-market.dev/?hero=e` — funciona **siempre**, con o sin `NEXT_PUBLIC_HERO_AB=1`.

**Cookie:** `cm_hero_variant` · 30 días · `SameSite=Lax`

**Analytics:** `#hero[data-hero-ab="1"]` · `data-hero-variant` · CTAs `data-cta=puerta-a|puerta-b`

**Anti-FOUC:** script blocking en `<head>` actualiza `#hero-h1` antes del paint.

**Local (desde la raíz del repo):**

```bash
cp landing/.env.example landing/.env.local
echo "NEXT_PUBLIC_HERO_AB=1" >> landing/.env.local
npm run dev
# → http://localhost:3000/?hero=e
```

`.env.local` va en **`landing/.env.local`**, no en la raíz. El script `dev` vive en `landing/package.json`; en la raíz usa `npm run dev` (wrapper) o `cd landing && npm run dev`.

### Snippet para Hero

Implementado en:

- `landing/lib/heroVariants.ts` — copy
- `landing/lib/heroVariantAssign.ts` — cookie + URL override
- `landing/hooks/useHeroVariant.ts` — hook cliente
- `landing/functions/_middleware.ts` — cookie en edge (CF Pages)

---

## Recomendación inicial

| Fase | Variante sugerida | Motivo |
|------|-------------------|--------|
| Lanzamiento post-rediseño | **A** (control) | Establecer baseline con nueva estructura doble puerta |
| Campaña LinkedIn agentic | **C** | Alineada a audiencia MCP/agentes |
| Outreach bureaus / fintechs | **E** o **B** | Credibilidad numérica primero |
| Si Puerta B << Puerta A tras 2 semanas | **D** | Reforzar retailers en H1 sin subir tipografía en sección 5 |

---

*Última actualización: 2026-05-30 · Copy ES/EN · Alineado a wireframe landing v1.0 y PR #44*
