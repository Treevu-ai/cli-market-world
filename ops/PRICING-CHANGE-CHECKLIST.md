# Pricing Change Checklist — Definition of Done

Cada vez que cambien precios, tiers o payment methods, esta lista debe quedar 100% verde antes de hacer deploy.

---

## 1. Fuente canónica (hacerlo primero)

- [ ] `cli-market-core/market_billing.py` — tiers y límites
- [ ] `cli-market-core/market_stats.py` — `PAYMENTS_LABEL`, `PACKAGE_VERSION` (bump)
- [ ] `cli-market-core/market_connectors/email_outbound.py` — `PRO_PRICE_LABEL`
- [ ] `cli-market-core/market_connectors/paypal_payments.py` — precio en labels

## 2. Landing (cli-market-world)

- [ ] `landing/components/Pricing.tsx` — cards de tiers, grid, precios anuales
- [ ] `landing/app/layout.tsx` — JSON-LD `offers[]`
- [ ] `landing/components/FAQ.tsx` — respuestas de preguntas de precios
- [ ] `landing/lib/faqSchema.ts` — FAQ structured data
- [ ] `landing/components/ProSubscribeButton.tsx` — label del botón
- [ ] `landing/public/llms.txt` — sección "Key Numbers" y "Pricing tiers"
- [ ] `landing/public/llms-full.txt` — línea de payments
- [ ] `landing/lib/marketStats.ts` — `packageVersion` (si fue bumpeado)

## 3. Backend / CLI (cli-market-world)

- [ ] `market_cli.py` — prompt `cmd_upgrade`
- [ ] `routers/misc.py` — strings de respuesta
- [ ] `routers/payments.py` — labels de planes
- [ ] `server_deps.py` — constantes de plan

## 4. Backend repo (cli-market-backend)

- [ ] `market_cli.py` — prompt `cmd_upgrade`
- [ ] `routers/alerts.py` — mensajes de upgrade
- [ ] `routers/misc.py` — strings de respuesta
- [ ] `routers/payments.py` — labels de planes
- [ ] `server_deps.py` — constantes de plan

## 5. Docs y ops (cli-market-world)

- [ ] `README.md` — tabla de pricing (ES + EN)
- [ ] `ops/BILLING_MANUAL.md`
- [ ] `ops/PAYPAL_SANDBOX.md`
- [ ] `docs/cli-market-prd-v2.md`
- [ ] `docs/ops/GO-LIVE-CHECKOUT.md`
- [ ] `docs/ops/phase0-mitigation.md`
- [ ] `pyproject.toml` — `version` (bump junto con market_stats.py)

## 6. Procure Copilot

- [ ] `lib/types.ts` — `PlanSlug`
- [ ] `lib/plans.ts` — tiers, precios, límites
- [ ] `app/procure/page.tsx` — PLANS array
- [ ] `app/dashboard/page.tsx` — PLANS local y CURRENT_PLAN
- [ ] `app/api/procurement/run/route.ts` — validación de slugs y upgrade strings

## 7. PyPI (hacer al final — desde tu máquina local)

```bash
# 1. Sincronizar repo local con main ANTES de buildear
git fetch origin && git checkout origin/main -- README.md

# 2. Verificar que el README tenga los precios correctos
grep "Starter\|Pro\|Builder" README.md | grep "\$"
# Debe mostrar $29, $79, $149 — si no, NO continuar

# 3. Bump de versión (elegir el próximo número)
sed -i 's/version = "X.X.X"/version = "X.X.Y"/' pyproject.toml

# 4. Build y upload
python3 -m build
twine upload dist/cli_market-X.X.Y*

# 5. Verificar en PyPI que el README muestre los precios correctos
# https://pypi.org/project/cli-market/
```

- [ ] `pyproject.toml` version bumpeado (paso 5)
- [ ] `market_stats.py` PACKAGE_VERSION bumpeado (paso 1)
- [ ] `git fetch origin && git checkout origin/main -- README.md` ejecutado
- [ ] `grep "Starter\|Pro\|Builder" README.md | grep "\$"` muestra $29/$79/$149
- [ ] `python3 -m build && twine upload dist/cli_market-NUEVA_VERSION*`
- [ ] https://pypi.org/project/cli-market/ muestra precios correctos

## 8. Content (cli-market-content)

- [ ] Solo archivos FUTUROS (no publicados): buscar con `grep -r "old_price" linkedin/ twitter/ strategy/`
- [ ] No tocar Day-01 al día actual de campaña

---

## Regla: Fuente de verdad

| Dato | Fuente canónica | Se propaga a |
|------|----------------|--------------|
| Precios de tiers | `market_billing.py` | plans.ts, Pricing.tsx, FAQ, README, llms.txt |
| Stats (retailers, precios, refresh) | `market_stats.py` | Regenerar con `ops/sync_market_stats.py` → marketStats.ts → resto de landing |
| Payment methods | `market_stats.py:PAYMENTS_LABEL` | llms.txt, llms-full.txt, FAQ, README |
| Versión del paquete | `market_stats.py:PACKAGE_VERSION` + `pyproject.toml:version` | marketStats.ts, PyPI |
