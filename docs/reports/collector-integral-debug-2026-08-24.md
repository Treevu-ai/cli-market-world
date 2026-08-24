# Debug integral del collector — 2026-08-24

**Veredicto:** el collector de producción **está sano**. No hay outage, no hay moat stale, el data-gate GTM está **abierto**. El trabajo pendiente es de **calidad de cobertura, observabilidad y conectores**, no de “el daemon se cayó”.

| Campo | Valor live (captura ~17:01 UTC) |
|---|---|
| Status `/health/collector` | `ok` |
| Último ciclo | 2026-08-24 14:39:55 → 14:45:25 UTC (~5.5 min) |
| Edad del ciclo | **2.3 h** (SLA interno stale = 12 h; intervalo configurado = 4 h) |
| Yield del ciclo | **343/343** tiendas · **15,512** precios |
| Runs acumulados | 987 |
| Snapshots PG | 194,424 |
| Moat | 193,397 indexados · 104,308 refresh 24 h · `collector_stale=false` |
| Gate GTM | `open` · coverage 7d **93.6%** · fresh 24h **91.0%** · publishable |
| Fuentes | 336 ok / 4 partial / 0 dead (n=340) |

Fuentes de evidencia: `GET https://cli-market-api.fly.dev/health/collector`, `/health/db`, `/dashboard/data`, `/dashboard/data?slim=1`, `/v1/sources/health`; Slack `#command-control-cli-market` y `#bitacora-cli-market` 14:03 UTC; GitHub Actions `DB Lock & Collector Freshness Monitor` (verde cada 15 min) y `Collect egress-blocked stores` (verde 09:30 UTC).

---

## 1. Qué se debuggeó

Se cruzaron cinco capas, no solo el semáforo `ok`:

1. **Proceso** — daemon Fly `cli-market-collector` (`fly.collector.toml`, intervalo 4 h, `collect_prices.py --daemon`).
2. **Persistencia** — Postgres `cli-market-db` (`/health/db`: 194,424 snapshots, tabla `collector_runs` presente, `pg_error=null`).
3. **Contrato API** — `/health/collector`, `/v1/sources/health`, `/dashboard/data`.
4. **Ops** — freshness monitor (15 min), workflow WAF-bypass, Slack C&C / bitácora / data-gate.
5. **Código** — circuit breaker persistente (`CB_PERSIST_SKIP=10`), dual-write `price_history` (fix 2026-08-20), Docker/Fly command alignment.

No se pudo inspeccionar `fly status`/`fly logs` desde este entorno (CLI Fly no instalada). El estado del proceso se infiere de `collector_runs` + snapshots recientes + monitor de frescura en verde.

---

## 2. Status operativo (capa proceso)

El daemon **sí está recolectando**. El último `collector_runs` cerró a las 14:45 UTC con 100% de tiendas intentadas en éxito a nivel de ciclo.

```
status:            ok
last_run:          2026-08-24T14:39:55Z
last_finished:     2026-08-24T14:45:25Z
age_hours:         2.3
stores_attempted:  343
stores_succeeded:  343
prices_collected:  15,512
stores_active:     332
stores_total:      388
runs_total:        987
interval:          4h  (COLLECT_INTERVAL_HOURS / COLLECT_INTERVAL_HOURS)
```

Próximo ciclo esperado ~18:40 UTC si el sleep del daemon es 4 h desde el fin del ciclo.

**Desalineación de reloj de frescura (no es una caída):**

| Reloj | Timestamp | Edad |
|---|---|---|
| Fin de `collector_runs` | 14:45:25Z | 2.3 h |
| `kpis.last_collected_at` (MAX snapshot) | 16:51:13Z | 0.1–0.2 h |

El moat sigue recibiendo writes **entre** ciclos del daemon (workflow de tiendas WAF-bloqueadas, backfills, growth catalog). El monitor de frescura usa `last_collected_at` del dashboard (umbral 6 h) — por eso sigue verde aunque el ciclo principal tenga 2+ h.

`Dockerfile.collector` y `fly.collector.toml` coinciden: `python collect_prices.py --daemon`. No hay split de comando.

---

## 3. Status del moat (capa datos)

| KPI | Live | Umbral | Semáforo |
|---|---|---|---|
| Indexados | 193.4k | ≥ 50k | OK |
| Refresh 24h | 104.3k | ≥ 5k/día | OK |
| Coverage 7d (dashboard) | 93.6% | ≥ 80% gate | OK |
| Fresh 24h % snapshots | 91.0% | ≥ 70% | OK |
| Tiendas con snapshot 24h | 312 | — | OK |
| Tiendas activas 7d | 321 | — | OK |
| Collector stale | false | false | OK |
| Data-gate | open / publishable | open | OK |
| Linkage Golden Records (C&C 14:03Z) | 100% · 73,991 GR | ≥ 85% | OK |

Slack 14:03 UTC: *Collector: ok · Moat stale: False · Sin tiendas críticas*. La bitácora marca en vigilancia las mismas 4 US DTC + 2 LATAM de éxito <90%.

---

## 4. Hallazgos (priorizados)

### H1 — Gap de catálogo: 388 vs 343 vs 340 vs 332  (P1)

Tres denominadores conviven y nadie los reconcilia en un solo panel:

| Contador | Valor | Significado probable |
|---|---|---|
| `stores_total` (`len(STORES)`) | 388 | Catálogo estático en código |
| Último ciclo `stores_attempted` | 343 | Lo que el daemon realmente visitó |
| `/v1/sources/health` n | 340 | Filas de `store_health` (catalog_only) |
| `stores_active` (DISTINCT store con price>0) | 332 | Tiendas con al menos un precio histórico |

**~45 tiendas del catálogo no entran al ciclo.** Candidatos: growth (`is_growth=1`) fuera de rotación, sin seed queries, circuit breaker persistente, o WAF-bypass que vive solo en GH Actions.

**Riesgo:** el 100% de éxito del ciclo (343/343) es un denominador recortado. No prueba cobertura del catálogo completo.

**Fix:** inventario explícito `in_cycle | skipped_cb | skipped_no_seeds | growth_deferred | waf_gha_only | inactive`. Exponerlo en `/health/collector`.

---

### H2 — Métrica `last_seen` vs `last_success` miente frescura por tienda  (P0 observabilidad)

En `/v1/sources/health`, **29 tiendas** salen `fresh_24h=false` con `last_seen=null` **aunque `last_success` es de hoy 14:40–14:44 UTC** (ej. `falabella_cl`, `sodimac_cl`, `estacion90_pe`, todo PY).

El flag `fresh_24h` está anclado a `last_seen`, no a `last_success` / `MAX(queried_at)` de snapshots. Falabella CL “no fresh” es un **falso negativo de telemetría**, no un retailer caído.

Efecto: C&C y bitácora no las marcan críticas (usan success_pct), pero cualquier consumidor de `fresh_24h` / `coverage_7d_pct` por tienda ve un agujero enorme.

**`coverage_7d_pct` por tienda (media 40.6%, 236 tiendas <50%) contradice el 93.6% del dashboard.** Son definiciones distintas:

- Dashboard: % de tiendas del catálogo activo con **algún** dato en 7 días.
- Sources: fracción de días con hit / 7, y se derrumba cuando `last_seen` es null.

**Fix:** `fresh_24h = last_success OR last_seen OR max(queried_at) < 24h`. Unificar `coverage_7d` o documentar ambos nombres (`store_day_hit_rate_7d` vs `stores_with_any_data_7d_pct`).

---

### H3 — Circuit breaker persistente vs status `ok`  (P1)

`santiagonativo_cl` y `rootscosmetica_ec`:

- `consecutive_failures = 10` (= `CB_PERSIST_SKIP`)
- `status = ok` (success_pct 93% lifetime)
- `last_success` 18-ago y 21-ago
- `last_error` posterior al last_success
- `fresh_24h = false` (este sí es real)

El collector **deja de intentarlas** al llegar a 10 fallos seguidos (`collect_prices.py`), pero el semáforo de sources no pasa a `partial`/`dead`. Quedan en silencio: no rompen el 343/343 y no alertan.

**Fix:** si `consecutive_failures >= CB_PERSIST_SKIP`, forzar `status=dead` o `circuit_open`, y un job semanal de “probe once” para resetear el CB si el retailer volvió.

---

### H4 — Cuatro US DTC en `partial` crónico  (P1 producto)

Misma lista desde al menos el 20-ago (bitácora diaria):

| Store | success_pct | cov7d | Estado |
|---|---|---|---|
| casper | 30.7 | 14.3 | partial · fresh 24h |
| parachute | 31.0 | 42.9 | partial · fresh 24h |
| brooklinen | 31.1 | 85.7 | partial · fresh 24h |
| alo_yoga | 50.1 | 100.0 | partial · fresh 24h |

Responden (last_seen hoy), pero el conector rinde ~1/3. No es WAF de Fly (el workaround GHA es para `smartnutrition_pe` / `simplynaturalcanada_ca`, y ese workflow está verde). Hipótesis: anti-bot / GraphQL / catalog vacío en queries seed.

**Fix:** captura HAR/status codes por query; si es bloqueo de User-Agent, meterlas al workflow GHA; si es seed, rotar queries; si es negocio irrelevante al ICP LATAM, **sacarlas del denominador del gate**.

---

### H5 — SLA de “stale” más laxo que el intervalo  (P2)

| Componente | Umbral |
|---|---|
| Daemon | 4 h |
| `derive_collector_status` | stale >12 h run u >8 h moat; dead >24 h |
| Freshness monitor GH | 6 h sobre `last_collected_at` |

Un daemon colgado 11 h seguiría `ok` en `/health/collector`. El monitor de GH cubre parte del hueco (6 h), pero alerta por el MAX snapshot, no por `collector_runs.finished_at`. Un backfill puede tapar un daemon muerto.

**Fix:** status `degraded` si `age_hours > 5` (un ciclo perdido); `stale` si `> 8`. El monitor debe chequear **ambos** relojes: último `collector_runs` y último snapshot.

---

### H6 — Sparklines C&C mienten tendencia  (P2)

Command & Control 14:03 UTC: Moat `193,102 (+193,102)`, sparkline `█▁▁▁▁▁▁▁▁▁`. El histórico `ops/metrics/command-control/history.jsonl` no tiene baseline de días previos (o se reseteó). No afecta el collector; sí afecta la lectura de “¿crecimos hoy?”.

**Fix:** no emitir delta si `n_history < 2`; backfill del jsonl desde briefings diarios 20–24 ago.

---

### H7 — CI adyacente rojo (no es el collector, pero toca el ritual)  (P2)

| Workflow | Run | Causa |
|---|---|---|
| Morning Ops Chain | [32735442616](https://github.com/Treevu-ai/cli-market-world/actions/runs/32735442616) | PAM tier1: 6 FAIL billing `403` (paypal/MP/yape/plin/request_pro). Jobs de moat/collector **verdes**. |
| Canasta PE weekly | [32736874443](https://github.com/Treevu-ai/cli-market-world/actions/runs/32736874443) | `TimeoutError` 45s al fetchear dashboard/canasta. |

El collector no es la causa. PAM 403 es gating de billing (posible regresión de security scan 21-ago). Canasta es timeout de endpoint pesado (hay incidente documentado de OOM en `/dashboard/data`).

---

### H8 — Deuda conocida ya mitigada (no reabrir)

- **WAF Fly egress** (`smartnutrition_pe`, `simplynaturalcanada_ca`): workflow diario 09:30 UTC, 5/5 runs verdes (20–24 ago), túnel `flyctl proxy` + `FLY_DB_PROXY_TOKEN`.
- **`collect_full_catalog_pg` no escribía `price_history`** ni Algolia: fix 20-ago (`970fdb2c`). Verificar en el próximo ciclo que history de esas dos tiendas tenga puntos nuevos.
- **Imagen collector vacía (10-jul-2026):** Dockerfile ya no encadena `&&`/`||` de forma que un pip fallido reporte success.

---

## 5. Qué NO está roto

- Daemon vivo, ciclo < 6 h, 15.5k precios/ciclo.
- Postgres reachable, upsert de snapshots listo.
- Data-gate abierto; claims GTM de moat/coverage **sí se pueden publicar hoy**.
- 0 tiendas `dead` en sources health.
- Monitor de locks/frescura en verde.
- Bypass WAF por GHA operativo.
- Docker/Fly entrypoint alineados.

---

## 6. Plan de abordaje

Canónico para build: **[PRD — Collector Observability & Coverage Integrity](../prd-collector-observability-coverage.md)** (issues COL-1…COL-13 + user stories). El resto de esta sección es el resumen operativo del debug.

### Fase 0 — hoy (sin deploy de collector)

1. Tratar el collector como **verde** en C&C / data-gate.
2. No pausar GTM data-gated por H2–H4.
3. Anotar en bitácora: “false stale por `last_seen`; CB abierto en 2 tiendas LATAM; 4 US DTC partial crónico”.

### Fase 1 — observabilidad (un PR, bajo riesgo)

| ID | Cambio | Done when |
|---|---|---|
| F1.1 | `fresh_24h` usa `COALESCE(last_success, last_seen, max_queried_at)` | Las ~20 Falabella/Sodimac/PY pasan a fresh si recolectaron hoy |
| F1.2 | Renombrar o documentar `coverage_7d_pct` per-store vs dashboard | Un solo número “gate” en C&C |
| F1.3 | `/health/collector` expone `stores_skipped`, `circuit_open[]`, `waf_gha_only[]` | 388 = 343 + skipped + … cierra |
| F1.4 | Monitor GH alerta si `collector_runs.age_hours > 5` **o** snapshot age > 6 | Daemon muerto no se esconde detrás de un backfill |
| F1.5 | `consecutive_failures >= 10` ⇒ status `circuit_open`, no `ok` | santiagonativo/rootscosmetica visibles |

Tests: extender `tests/test_sources_health.py`; fixture con `last_success` hoy y `last_seen` null.

### Fase 2 — cobertura real (connectors)

| ID | Tienda / clase | Acción |
|---|---|---|
| F2.1 | casper, parachute, brooklinen, alo_yoga | Log de status/body por query; decidir GHA vs seed vs delist del gate |
| F2.2 | santiagonativo_cl, rootscosmetica_ec | Probe manual 1 ciclo con CB bypass; si 200, reset `consecutive_failures` |
| F2.3 | Gap 388−343 | Script `ops/collector_catalog_diff.py` que liste las 45 ausentes y clasifique |
| F2.4 | smartnutrition / simplynatural | Confirmar `price_history` post-fix 20-ago; si no, re-run `--catalog-store` |

No mezclar F2.1 en el mismo PR que F1.* — son conectores, no telemetría.

### Fase 3 — SLA y ritual

| ID | Acción |
|---|---|
| F3.1 | `derive_collector_status`: `degraded` >5 h, `stale` >8 h (hoy 12/24) |
| F3.2 | Sparklines C&C: no delta si history < 2 puntos; backfill jsonl |
| F3.3 | PAM 403 billing: fuera de este plan (security gating). Ticket aparte. |
| F3.4 | Canasta PE: timeout 45s → 90s + slim payload; no es collector |

### Orden de release (si hay código)

`world` solo (health + sources + monitor). No toca core/backend/index. Collector image **solo** si F2 cambia `collect_prices.py` (entonces deploy `cli-market-collector` con `--build-secret`, nunca PAT en build-arg).

### Criterios de cierre

- [ ] `/health/collector` = ok y `age_hours < 5` en dos ciclos seguidos
- [ ] `fresh_24h` false **solo** cuando no hay `last_success` <24 h
- [ ] 0 tiendas con CB≥10 y status `ok`
- [ ] Decisión documentada (fix o delist) para las 4 US DTC
- [ ] Catálogo: `attempted + skipped + inactive = stores_total`
- [ ] Data-gate sigue open con coverage 7d ≥ 80%

---

## 7. Comandos de re-verificación

```bash
curl -sS https://cli-market-api.fly.dev/health/collector | python3 -m json.tool
curl -sS 'https://cli-market-api.fly.dev/dashboard/data?slim=1' | python3 -m json.tool
curl -sS https://cli-market-api.fly.dev/v1/sources/health \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['summary'], 'n', len(d['stores']))"
python3 ops/gtm_gate_remote.py
# Si hay flyctl:
fly status -a cli-market-collector
fly logs -a cli-market-collector --no-tail | tail -80
```

---

## 8. Apéndice — evidencias

- Probe JSON: artefacto de agente `collector_live_probe_2026-08-24.json` (health, db, collector, slim, sources summary).
- Slack 2026-08-24 14:03 UTC: C&C collector OK, bitácora sin críticas, data-gate abierto 193,186 / 94% / 332 retailers.
- GH: freshness monitor success 16:43Z; egress-blocked stores success 10:09Z; Morning Ops PAM 403; Canasta PE timeout.
- Código: `collect_prices.py` (`CB_PERSIST_SKIP`, `--daemon`); `routers/health.py` (`derive_collector_status`); `ops/db_lock_monitor.py` (6 h); `fly.collector.toml` / `Dockerfile.collector`.
