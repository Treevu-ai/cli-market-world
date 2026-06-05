# Fase 0 — Mitigación de deuda técnica y alineación GTM

**Fecha:** 2026-05-30 · **Rama:** `cursor/phase0-mitigation-f414`

Plan de mitigación inmediato antes de ampliar ventas Intelligence o escalar Build Pro.

---

## Objetivos completados

| Área | Cambio | Archivos |
|------|--------|----------|
| Narrativa landing | Hero → Flujo → API → Cobertura → puente → Casos → Planes → Retailers → FAQ → Contact | `landing/app/page.tsx`, nav |
| Intelligence-first | Pricing (Puerta C primero), UseCases, bridge, FAQ, HowItWorks | `landing/components/*` |
| Métricas unificadas | 43K+ precios, 60 retailers (30 verificados) | `llms.txt`, `mcp.json`, `/retailers` |
| Copy GTM | README + FAQ alineados a Build + Intelligence | `README.md`, `FAQ.tsx` |
| Ops Pro | SLA activación manual documentado | `ops/BILLING_MANUAL.md`, `ops/E2E_CLIENT_JOURNEY.md` |

---

## Métricas canónicas

Fuente de verdad: `ops/sync_market_stats.py` → `landing/lib/marketStats.ts`

| Métrica | Valor | Notas |
|---------|-------|-------|
| Precios verificados | **43,000+** | Dashboard + collector |
| Retailers catálogo | 60 | Definidos en config |
| Retailers verificados activos | 30 | Collector OK últimas 24 h |
| Refresh | 8 h | Collector daemon |
| Países | 8 | PE, AR, BR, MX, CO, CL, IT, FR |
| MCP tools | 36 | `mcp.json` |

Regenerar tras cambios en collector:

```bash
python3 ops/sync_market_stats.py
git diff landing/lib/marketStats.ts
```

---

## Productos visibles (GTM)

| Puerta | Producto | Precio | Canal |
|--------|----------|--------|-------|
| A | Build (Free / Pro) | $0 / $79/mo | PyPI, landing `#pricing-build` |
| B | Retailer listing | Gratis | `/retailers`, `#contact-retailers` |
| C | Intelligence | USD 300–500/mo piloto | `#pricing-intelligence`, one-pager |

**Foco comercial Q2 2026:** Puerta C (Intelligence). Build Pro sigue disponible pero activación manual.

---

## Pro — SLA ops (manual)

Ver detalle en `ops/BILLING_MANUAL.md` y journey en `ops/E2E_CLIENT_JOURNEY.md`.

| Paso | SLA objetivo | Responsable |
|------|--------------|-------------|
| Solicitud Pro recibida | Email auto con `PRO-xxx` + link pago | API (`/billing/request-pro`) |
| Pago confirmado | Activar en **≤24 h hábiles** | Ops (`ops/activate_pro.py`) |
| PayPal «Agotado» | CTA verde `PRO_PAYMENT_URL` en landing | Landing (#49) |
| Cliente verifica | `market whoami` → tier pro | Cliente |

Comando activación:

```bash
python3 ops/activate_pro.py USERNAME --request-id PRO-XXXXXXXX
```

---

## Pendiente (Fase 2+)

Completado en Fase 1 — ver `docs/ops/phase1-debt-cleanup.md`:

- ~~Componentes landing huérfanos~~ ✅
- ~~Content template 13K → 43K~~ ✅ (sync repo privado pendiente)
- ~~Dual SQLite/Postgres doc~~ ✅ → `docs/ops/database-migration.md`
- ~~`market_core.py` split (billing)~~ ✅ → `market_billing.py`

Queda para sprints siguientes:

1. **PayPal inventory** — corregir «Agotado» en panel PayPal Hosted Button
2. **Checkout autónomo** — roadmap Build; no prometer en copy comercial
3. **`market_db.py` split** — extraer capa `_DB` + DDL monolito
4. **Content repo privado** — `campaign sync` tras actualizar template

---

## Verificación post-merge

```bash
cd landing && npm run build
MARKET_DATA_DIR=/tmp/market-test-data pytest tests/ -q -m "not integration"
python3 ops/sync_market_stats.py  # debe ser no-op si stats al día
```

Smoke landing (orden secciones):

1. `#coverage` antes de `#casos`
2. `#pricing-intelligence` antes de `#pricing-build`
3. `#faq` antes de `#contact`
