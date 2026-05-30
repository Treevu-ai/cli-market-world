# Fase 4 — i18n landing unificado

**Fecha:** 2026-05-30 · **Rama:** `cursor/phase4-i18n-landing-f414`

Continúa `docs/ops/phase3-content-sync.md`. Resuelve la duplicidad entre copy inline en componentes y el diccionario obsoleto `translations.ts`.

---

## Decisión

| Opción | Resultado |
|--------|-----------|
| Migrar todo a `t('key')` | ~200 keys, muchas de secciones eliminadas en F1; refactor masivo sin ganancia inmediata |
| **Inline como fuente de verdad** | ✅ Copy ya alineado a Intelligence-first + mensaje canónico; usa `MARKET_STATS` donde aplica |

**Estrategia adoptada:** eliminar `landing/lib/translations.ts` (dead code) y mantener i18n inline en cada componente activo.

---

## Arquitectura actual

```
landing/lib/i18n.ts          → type Lang, helper isES()
landing/lib/LanguageContext  → lang + setLang (React context)
landing/lib/marketStats.ts   → métricas canónicas (43K+, 60/30, etc.)
landing/components/*.tsx     → copy ES/EN inline o arrays *_es / *_en
```

### Patrones en componentes

1. **Ternario simple:** `isES ? "Texto ES" : "Text EN"`
2. **Arrays bilingües:** `{ title_es, title_en, desc_es, desc_en }` (Pricing, UseCases)
3. **Funciones con stats:** `faqsFor(lang)` en FAQ — interpola `MARKET_STATS`
4. **Nav compartido:** `{ id, es, en }` en Navbar / SideNav

No hay diccionario central de strings. Las métricas sí tienen fuente única (`marketStats.ts` ← `ops/sync_market_stats.py`).

---

## Eliminado

- `landing/lib/translations.ts` (~200 keys obsoletas: Terminal, Features, DataSection, checkout-first, 39K precios, nav huérfano)
- `t()` en `LanguageContext` — ningún componente lo invocaba

---

## Componentes con i18n activo

| Componente | Notas |
|------------|-------|
| Hero | Intelligence-first, 3 CTAs (Build / Intelligence / Retailers) |
| Navbar, SideNav | Nav alineado a secciones actuales |
| ScaleCoverageSection | Stats live + `MARKET_STATS` |
| CoverageToUseCasesBridge | Puente cobertura → casos |
| HowItWorks, QuickstartAPI | Flujo Build |
| UseCasesSection | Build vs Intelligence |
| Pricing | Puertas A (Build) + C (Intelligence) |
| FAQ | `faqsFor()` + stats dinámicos |
| RetailersSection, ContactSection | Puerta B |
| Footer, AboutSection, ProSubscribeButton, ContactForm | Misc |

---

## Verificación

```bash
cd landing && npm run build
rg "translations\\.ts|from ['\"]@/lib/translations" landing/   # sin resultados
```

---

## Pendiente Fase 5+

| Item | Notas |
|------|-------|
| PayPal live + «Agotado» | Panel PayPal Business (externo) |
| ~~Regenerar price-pulse~~ | ✅ Fase 5 — ver `docs/ops/phase5-metrics-pipeline.md` |
| i18n futuro | Si crece el copy, extraer por sección |
| Checkout autónomo | Roadmap Build |
