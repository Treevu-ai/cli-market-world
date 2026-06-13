# Tech debt backlog — CLI Market multirepo

**Last updated:** 2026-06-13 (N-1 closed) · **Owner:** PM + eng  
**North star de deuda:** paridad multirepo verificable, gates CI duros en revenue/data, Observatory auditado antes de claims GTM.

**Sprint activo:** N-4 — Automatizar `RELEASE-DISPERSION.md` post-PyPI

---

## ✅ Sprint cerrado — Now (2026-06-08 → 2026-06-13)

| ID | Repo | Entrega | Estado |
|----|------|---------|--------|
| **#172** | world | `fix(ops): tech debt Now block — tests v1, observatory shim, CI pin` | ✅ Merged |
| **T-173** | core | `feat(observatory): export observatory_snapshot_streak` → PyPI **1.9.35** | ✅ Shipped |
| **T-174** | world | `test(intel): add test_sources_health + test_dashboard_view_model smoke` | ✅ Shipped |
| **T-175** | world | `ci: require backend contract parity when GH_PAT has backend read` | ✅ Shipped |
| **T-176** | world | `ops: PayPal live E2E gate — close GO-LIVE §5` | ✅ Shipped |
| **T-177** | core + backend + world | `chore: mirror diff gate observatory + server_deps` | ✅ Shipped (#185) |
| **T-178** | backend | `chore: sync observatory mirror from world (streak route)` | ✅ Shipped (#186, #188) |
| **N-5** | world | `ops: linkage_pct alerts in command-control` | ✅ Shipped (#187) |

### Entregables Now (#172 + ciclo)

- [x] `ops/TECH-DEBT-BACKLOG.md` (este doc)
- [x] `tests/test_data_v1.py` — smoke `/v1/*`
- [x] `ops/verify_phase_docs.py` + manifest required tests (13/13)
- [x] CI/Railway pin `cli-market-core` @ **1.9.36** — post-PyPI 2026-06-13
- [x] `market_observatory.py` → pure shim (core **1.9.36** on PyPI)
- [x] `ops/observatory_audit.py` — auditoría cuantitativa PRD §13
- [x] `ops/mirror_diff_gate.py` + CI en `contract_parity.py` (T-177)
- [x] `sync-backend-observatory-mirror.yml` auto-PR backend (T-178)
- [x] Linkage alerts en command-control (N-5)

---

## 🟡 Next — 1–2 ciclos

| ID | Item | Repo | Effort |
|----|------|------|--------|
| ~~N-1~~ | ~~Partir `routers/payments.py`~~ | world | ✅ Merged 2026-06-13 (#210 #211 #212) |
| ~~N-2~~ | ~~Desacoplar GTM de `morning-ops-chain`~~ | world | ✅ Merged 2026-06-13 (#213) |
| ~~N-3~~ | ~~Tests `slack_ops`, `media`, `retailer_admin`~~ | world | ✅ Merged 2026-06-13 (#214) |
| N-4 | Automatizar `RELEASE-DISPERSION.md` post-PyPI | world | S |
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

## 👤 Ops humano (no código — backlog operativo)

| Item | Owner | Notas |
|------|-------|-------|
| Merge backend PR #22 | eng | Auto-PR observatory mirror — cierra gap streak |
| Merge backend CI PR (sync-backend-ci) | eng | ✅ Resuelto 2026-06-13 — ruff embed + CI verde |
| PayPal live E2E GO-LIVE §5 | founder | `ops/paypal_live_e2e.py --prepare` + aprobación manual + `--verify` |
| Observatory adoption CI 7 días | eng | Validar post-deploy ~2026-06-19 (`observatory-nightly`) |
| Landing `/stats` data-gate | GTM | `make gate` en content repo antes de creative con cifras |
| `observatory_daily.py --dry-run` | eng | Requiere `DATABASE_URL` en entorno con DB prod/staging |

---

## ❌ No es deuda (mantener)

- Stripe off · Procure billing separado · Yape/Plin manual con guard PayPal/MP · Index sin telemetry P0

---

## Métricas de cierre (sprint Now)

| Métrica | Baseline | Target | Actual |
|---------|----------|--------|--------|
| `/v1/*` con test smoke | 0/5 | 5/5 | **5/5** ✅ |
| CI core ref | `main` | PyPI `==1.9.36` | **1.9.36** ✅ |
| `market_observatory` LOC world | ~900 | shim <20 | **shim** ✅ |
| PRD §13 Observatory | ~60% | 100% | **~95%** (ops humano pendiente) |
| Phase docs → missing tests | ≥5 refs | 0 required | **0/13 required** ✅ (3 optional phase5/7) |
| Mirror gate CI | none | semantic parity | **contract_parity** ✅ |
| Linkage alerts command-control | none | warn + drop | **N-5** ✅ |

---

## Orden de release (sin cambio)

`core → backend → world → index` · Checklists: `ops/OBSERVATORY-CHANGE-CHECKLIST.md`, `ops/RELEASE-DISPERSION.md`
