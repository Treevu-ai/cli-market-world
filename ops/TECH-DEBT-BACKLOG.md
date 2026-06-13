# Tech debt backlog — CLI Market multirepo

**Last updated:** 2026-06-12 · **Owner:** PM + eng  
**North star de deuda:** paridad multirepo verificable, gates CI duros en revenue/data, Observatory auditado antes de claims GTM.

---

## 🟢 Now — PRs pequeños (este ciclo)

| PR | Repo | Título | Estado |
|----|------|--------|--------|
| **#172** | world | `fix(ops): tech debt Now block — tests v1, observatory shim, CI pin` | ✅ Merged |
| **T-173** | core | `feat(observatory): export observatory_snapshot_streak` → PyPI **1.9.35** | En curso (#173) |
| T-174 | world | `test(intel): add test_sources_health + test_dashboard_view_model smoke` | Pendiente |
| T-175 | world | `ci: require backend contract parity when GH_PAT has backend read` | Pendiente |
| T-176 | world | `ops: PayPal live E2E gate — close GO-LIVE §5` | Pendiente (`ops/paypal_live_e2e.py`) |
| T-177 | core + backend + world | `chore: mirror diff gate observatory + server_deps` | Pendiente |

### Entregables Now (#172)

- [x] `ops/TECH-DEBT-BACKLOG.md` (este doc)
- [x] `tests/test_data_v1.py` — smoke `/v1/*`
- [x] `ops/verify_phase_docs.py` + manifest required tests
- [x] CI pin `cli-market-core` @ **1.9.35** PyPI (git tag `v1.9.34` + `v1.9.35` — T-173)
- [x] `market_observatory.py` → pure shim (streak in core **1.9.35**)
- [x] `ops/observatory_audit.py` — auditoría cuantitativa PRD §13

---

## 🟡 Next — 1–2 ciclos

| ID | Item | Repo | Effort |
|----|------|------|--------|
| N-1 | Partir `routers/payments.py` (webhooks / checkout / email) | world | L |
| N-2 | Desacoplar GTM de `morning-ops-chain` (briefing independiente) | world | M |
| N-3 | Tests `slack_ops`, `media`, `retailer_admin` | world | M |
| N-4 | Automatizar `RELEASE-DISPERSION.md` post-PyPI | world | S |
| N-5 | Alerta linkage_pct en command-control | world + index | S |
| N-6 | `tests/test_price_confidence.py` + `test_market_basket.py` | world | M |
| N-7 | Actualizar phase6/7 docs o crear tests faltantes | world | S |

---

## 🔵 Later — diferido explícito

| Item | Notas |
|------|-------|
| Checkout autónomo (Fase 8) | Sin validación demanda vs ops manual |
| Stripe `/billing/checkout` | Deshabilitado hasta webhook loop |
| i18n centralizado landing | Inline ES/EN suficiente hoy |
| Landing unit tests en CI | Solo build Cloudflare |

---

## ❌ No es deuda (mantener)

- Stripe off · Procure billing separado · Yape/Plin manual con guard PayPal/MP · Index sin telemetry P0

---

## Métricas de cierre

| Métrica | Baseline | Target |
|---------|----------|--------|
| `/v1/*` con test smoke | 0/5 | 5/5 |
| CI core ref | `main` | PyPI `==1.9.35` + git tags `v1.9.34`, `v1.9.35` |
| `market_observatory` LOC world | ~900 | shim <20 |
| PRD §13 Observatory | ~60% | 100% |
| Phase docs → missing tests | ≥5 refs | 0 (manifest) |

---

## Orden de release (sin cambio)

`core → backend → world → index` · Checklists: `ops/OBSERVATORY-CHANGE-CHECKLIST.md`, `ops/RELEASE-DISPERSION.md`
