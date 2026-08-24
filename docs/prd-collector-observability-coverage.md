---
title: PRD — Collector Observability & Coverage Integrity
tags:
  - product
  - prd
  - collector
  - moat
  - observability
status: Draft v1.0
owner: Founder Ops + Engineering
created: 2026-08-24
repos: cli-market-world (API/ops/monitor), cli-market-core (source_health)
related:
  - docs/reports/collector-integral-debug-2026-08-24.md
  - docs/prd/collector-issues.md
  - docs/data-moat-reporting.md
  - collect_prices.py
  - routers/health.py
  - routers/dashboard.py
  - ../cli-market-core/market_core/source_health.py
origin: Debug integral collector 2026-08-24 (prod ok; deuda de métricas y cobertura)
---

# PRD — Collector Observability & Coverage Integrity

**Producto:** CLI Market moat (daemon Fly `cli-market-collector` + `/health/collector` + `/v1/sources/health` + data-gate GTM)  
**Estado:** Draft v1.0  
**Fecha:** 2026-08-24  
**Prioridad de producto:** P1 (no bloquea publicar hoy; sí bloquea operar el moat con números honestos)

## TL;DR

El collector de producción **está sano** (ciclo 4 h, 343/343, ~15.5k precios, gate abierto, coverage 7d 93.6%). El problema no es “se cayó”: **las métricas mienten, el catálogo no cuadra y hay tiendas en silencio**.

Este PRD convierte el plan del debug en un **epic** con **13 issues** y **user stories** implementables. Fase 0 (hoy) es operativa y no requiere código. Fase 1 es el corte mínimo de observabilidad.

**Propuesta de valor en una línea:**  
> Un operador debe poder responder en 30 segundos: ¿el daemon corrió? ¿qué catálogo visitó? ¿qué se saltó? ¿qué precio es fresco de verdad?

---

## 1. Problema

### 1.1 Qué ve el founder hoy

| Señal 2026-08-24 ~17:01 UTC | Lectura |
|---|---|
| `/health/collector` = `ok`, edad 2.3 h, 343/343 | Daemon vivo |
| Dashboard slim: gate `open`, coverage 93.6%, fresh 24h 91% | GTM puede publicar |
| `/v1/sources/health`: 29 tiendas `fresh_24h=false` con `last_success` de hoy | Falso stale |
| `stores_total=388` vs `attempted=343` vs `active=332` | Denominadores incompatibles |
| `santiagonativo_cl` / `rootscosmetica_ec`: 10 fallos seguidos, `state=ok` | Circuit breaker invisible |
| casper / parachute / brooklinen / alo_yoga ~31–50% success | Partial crónico, misma lista ≥ 20-ago |

### 1.2 Coste

- Un agente o un post data-gated puede citar “29 tiendas no fresh” cuando Falabella/Sodimac recolectaron hace 2 h.
- El 100% de éxito del ciclo (343/343) **no** prueba cobertura del catálogo de 388.
- Dos retailers LATAM salen del ciclo y nadie alerta.
- SLA `stale=12 h` frente a intervalo 4 h: un daemon muerto 11 h sigue `ok`.
- El monitor GH mira `kpis.last_collected_at` (MAX snapshot, puede ser un backfill), no `collector_runs.finished_at`.

### 1.3 Evidencia

Diagnóstico canónico: [collector-integral-debug-2026-08-24.md](reports/collector-integral-debug-2026-08-24.md).  
Código implicado: `market_core/source_health.py` (`_fresh_24h` solo usa `last_seen`), `routers/health.py` (`derive_collector_status` 12 h / 24 h), `collect_prices.py` (`CB_PERSIST_SKIP=10`), `ops/db_lock_monitor.py` (6 h sobre dashboard).

---

## 2. Objetivos

| Objetivo | Métrica de éxito |
|---|---|
| Frescura por tienda = realidad de recolección | `fresh_24h=false` solo si no hay `last_success` ni snapshot `<24h` |
| Un número de coverage para el gate | C&C y `/dashboard/data?slim=1` usan la misma definición documentada |
| Identidad de catálogo cerrada | `attempted + skipped + inactive = stores_total` en `/health/collector` |
| Circuit breaker observable | 0 tiendas con `consecutive_failures >= 10` y `state=ok` |
| Daemon muerto no se esconde | Alerta si `collector_runs.age > 5h` **o** snapshot age > 6h |
| US DTC con decisión | 4 tiendas: fix, GHA bypass, o delist del denominador del gate |

### 2.1 Fuera de scope

- Pausar el data-gate o el collector (prod está ok).
- Rediseñar el daemon (paralelismo, Playwright, new retailers).
- PAM billing 403 y timeout Canasta PE: issues **adyacentes**, no del epic de collector (COL-12, COL-13).
- Cambiar el intervalo 4 h.
- Unificar stdio MCP vs HTTP (otro sistema).

---

## 3. Personas

| Persona | Job |
|---|---|
| Operador / founder (C&C) | Semáforo diario: ¿publicamos? ¿qué vigilar? |
| Publisher GTM | Claims de moat/coverage sin inventar métricas |
| Ingeniero collector | Saber qué se skippeó y por qué, sin leer logs Fly |
| Agente (MCP / Slack bot) | Consumir `/health/collector` y `/v1/sources/health` sin contradicciones |

---

## 4. Epic

**Epic COL:** Collector Observability & Coverage Integrity  

**Repos:** `cli-market-world` (health, dashboard, monitor, ops scripts, C&C) + `cli-market-core` (si `fresh_24h` / `state` viven en `source_health.py`; pin y bump en world).  
**Orden de release si hay código:** core (si aplica) → world. Collector image solo si un issue toca `collect_prices.py`.

```
Fase 0  ops (sin código)     ── ya
Fase 1  observabilidad       ── COL-1 COL-2 COL-3 COL-4 COL-8
Fase 2  cobertura real       ── COL-5 COL-6 COL-7 COL-11
Fase 3  SLA / ritual         ── COL-9 COL-10
Fuera   CI adyacente         ── COL-12 COL-13
```

---

## 5. Issues y user stories

Convención: **COL-N** = issue / ticket. **US-COL-N.x** = historia de usuario del issue.  
Formato US: *Como [persona], quiero [capacidad], para [resultado].*  
Labels sugeridos al abrir en GitHub: `collector` `prd` `P0|P1|P2`.

### Índice

| Issue | P | Fase | Título | User stories |
|---|---|---|---|---|
| [COL-1](#col-1--p0--fresh_24h-deja-de-mentir) | P0 | 1 | `fresh_24h` usa last_success / snapshot | US-COL-1.1, 1.2, 1.3 |
| [COL-2](#col-2--p0--un-solo-coverage-7d-para-el-gate) | P0 | 1 | Un coverage 7d para el gate | US-COL-2.1, 2.2 |
| [COL-3](#col-3--p1--identidad-de-catálogo-en-healthcollector) | P1 | 1 | Identidad de catálogo en health | US-COL-3.1, 3.2 |
| [COL-4](#col-4--p1--circuit-breaker-visible) | P1 | 1 | `state=circuit_open` | US-COL-4.1, 4.2 |
| [COL-5](#col-5--p1--probe-semanal-de-circuitos-abiertos) | P1 | 2 | Probe semanal CB | US-COL-5.1 |
| [COL-6](#col-6--p1--inventario-del-gap-388--343) | P1 | 2 | Script gap catálogo | US-COL-6.1, 6.2 |
| [COL-7](#col-7--p1--conectar-o-delistar-4-us-dtc) | P1 | 2 | 4 US DTC: fix o delist | US-COL-7.1, 7.2, 7.3 |
| [COL-8](#col-8--p1--monitor-de-doble-reloj) | P1 | 1 | Monitor dual (run + snapshot) | US-COL-8.1, 8.2 |
| [COL-9](#col-9--p2--sla-degraded--stale-alineado-al-ciclo-4-h) | P2 | 3 | SLA 5 h / 8 h | US-COL-9.1 |
| [COL-10](#col-10--p2--sparklines-cc-con-baseline) | P2 | 3 | Sparklines con baseline | US-COL-10.1, 10.2 |
| [COL-11](#col-11--p2--verificar-price_history-post-waf-bypass) | P2 | 2 | History WAF stores | US-COL-11.1 |
| [COL-12](#col-12--p2-fuera-del-epic-pam-billing-403) | P2 | — | PAM billing 403 | US-COL-12.1 |
| [COL-13](#col-13--p2-fuera-del-epic-timeout-canasta-pe) | P2 | — | Timeout Canasta PE | US-COL-13.1 |

---

### COL-1 — P0 — `fresh_24h` deja de mentir

**Hallazgo:** H2. **Repo primario:** `cli-market-core` (`market_core/source_health.py`) + tests en world `tests/test_sources_health.py`.

**Problema:** `_fresh_24h` usa solo `last_seen` (`MAX(queried_at)` de snapshots). Si esa join falla o el timestamp no pega, `fresh_24h=false` aunque `last_success` sea de hoy (Falabella CL, Sodimac CL, PY, ~29 tiendas el 24-ago).

**US-COL-1.1**  
Como operador de C&C, quiero que una tienda con recolección exitosa en las últimas 24 h aparezca `fresh_24h=true`, para no vigilar falsos negativos.

**US-COL-1.2**  
Como publisher GTM, quiero que el data-gate y `/v1/sources/health` no contradigan el dashboard slim en frescura 24 h, para no publicar claims incoherentes.

**US-COL-1.3**  
Como ingeniero, quiero un test con `last_success=now`, `last_seen=null` y un snapshot reciente, para que el falso negativo no regrese.

**Criterios de aceptación**

- [ ] `fresh_24h = age(COALESCE(last_seen, last_success, max_snapshot_ts)) < 24h`
- [ ] Fixture: `last_seen=null`, `last_success` hace 2 h → `fresh_24h is True`
- [ ] Fixture: ambos null / >24 h → `fresh_24h is False`
- [ ] Pin/bump de `cli-market-core` en world si el fix sale en el paquete
- [ ] En prod, Falabella CL / Sodimac CL dejan de salir en la cola “no fresh” el mismo día que tienen `last_success`

**Notas técnicas:** alinear columna de snapshot (`queried_at` vs `queried_at`) y clave `store` entre `store_health` y `price_snapshots`. Si `queried_at` no existe, `last_seen` siempre es null — confirmar en PG antes de “arreglar” solo el COALESCE.

**Depends:** ninguno. **Blocks:** COL-2 (números de coverage por tienda).

---

### COL-2 — P0 — Un solo coverage 7d para el gate

**Hallazgo:** H2 (segunda parte). **Repo:** world (`routers/dashboard.py`, C&C, `docs/data-moat-reporting.md`) + core `coverage_7d_pct`.

**Problema:** dashboard `coverage_7d_pct` = % de tiendas del catálogo activo con **algún** dato en 7d (93.6%). Per-store `coverage_7d_pct` = días con hit / 7 (media ~40%). Mismo nombre, distinta fórmula.

**US-COL-2.1**  
Como publisher GTM, quiero un campo canónico para el gate (`stores_with_any_data_7d_pct` o equivalente) y otro nombre para el hit-rate por tienda, para no citar 40% cuando el gate es 94%.

**US-COL-2.2**  
Como operador de C&C, quiero que el scoreboard muestre **un** coverage 7d etiquetado, para no explicar dos porcentajes en el briefing.

**Criterios de aceptación**

- [ ] Contrato JSON: `coverage_7d_pct` en slim/dashboard = definición gate (≥1 snapshot en 7d / catálogo activo)
- [ ] Per-store se llama `store_day_hit_rate_7d_pct` (o se documenta en `metric_glossary` si se conserva el nombre viejo)
- [ ] `docs/data-moat-reporting.md` tabla “Collector / salud del moat” actualizada
- [ ] Slack C&C usa el campo gate; bitácora puede listar hit-rate bajo como “vigilar”, no como coverage del gate

**Depends:** COL-1 (last_seen null infla el hit-rate bajo).

---

### COL-3 — P1 — Identidad de catálogo en `/health/collector`

**Hallazgo:** H1. **Repo:** world `routers/health.py`, `collect_prices.py` (qué lista usa el daemon).

**Problema:** 388 / 343 / 340 / 332 conviven. El 100% de éxito es sobre 343.

**US-COL-3.1**  
Como ingeniero, quiero en `/health/collector` los conteos `stores_total`, `attempted`, `succeeded`, `skipped`, `inactive` y arrays `circuit_open[]`, `waf_gha_only[]`, `no_seeds[]`, para cerrar la identidad `total = attempted + skipped + inactive`.

**US-COL-3.2**  
Como operador, quiero ver en C&C “343/388 en ciclo · N skipped” en vez de “343/343 ok”, para no inflar cobertura.

**Criterios de aceptación**

- [ ] Payload incluye buckets explícitos; la suma cuadra (±0)
- [ ] Test de contrato del endpoint (shape + suma)
- [ ] C&C / health collector line usa attempted/total, no succeeded/attempted como única cifra
- [ ] Documentar `waf_gha_only` = `smartnutrition_pe`, `simplynaturalcanada_ca` (nombres canónicos de prod)

**Depends:** ninguno. Alimenta COL-6.

---

### COL-4 — P1 — Circuit breaker visible

**Hallazgo:** H3. **Repo:** core `store_health_state` + world consumers; umbral = `CB_PERSIST_SKIP` (default 10) en `collect_prices.py`.

**Problema:** `consecutive_failures=10` skippea el store pero `state` sigue `ok` por success_pct lifetime ~93%.

**US-COL-4.1**  
Como operador, quiero `state=circuit_open` (o `dead` operativo) cuando el collector ya no intenta la tienda, para que aparezca en bitácora como crítica.

**US-COL-4.2**  
Como ingeniero, quiero que el skip del daemon y el `state` de sources usen el mismo umbral, para no tener dos verdades.

**Criterios de aceptación**

- [ ] `consecutive_failures >= CB_PERSIST_SKIP` ⇒ `state` ∈ {`circuit_open`, `dead`} — no `ok`
- [ ] success_pct alto no pisa ese estado
- [ ] Test: 10 fallos + 93% lifetime → no `ok`
- [ ] Bitácora / sources summary cuenta `circuit_open`

**Depends:** ninguno. **Blocks:** COL-5.

---

### COL-5 — P1 — Probe semanal de circuitos abiertos

**Hallazgo:** H3 (remediación). **Repo:** world ops + opcional flag en `collect_prices.py`.

**US-COL-5.1**  
Como ingeniero collector, quiero un job semanal que pruebe **una vez** cada store `circuit_open` (bypass CB), y si hay 200 + precios, resetee `consecutive_failures`, para recuperar retailers que volvieron sin redeploy.

**Criterios de aceptación**

- [ ] Workflow o script `ops/collector_circuit_probe.py` (lista desde `/v1/sources/health` o SQL)
- [ ] Bypass acotado a esas tiendas; no desactiva CB global
- [ ] Si probe ok: reset failures; Slack opcional a bitácora
- [ ] Primera corrida documenta resultado de `santiagonativo_cl` y `rootscosmetica_ec`

**Depends:** COL-4.

---

### COL-6 — P1 — Inventario del gap 388 − 343

**Hallazgo:** H1. **Repo:** world `ops/collector_catalog_diff.py`.

**US-COL-6.1**  
Como ingeniero, quiero un script que clasifique cada store del catálogo (`in_cycle` / `skipped_cb` / `skipped_no_seeds` / `growth_deferred` / `waf_gha_only` / `inactive` / `unknown`), para atacar las ~45 ausentes con nombre y causa.

**US-COL-6.2**  
Como operador, quiero el output del script en el briefing semanal (tabla corta), para decidir onboarding vs delist.

**Criterios de aceptación**

- [ ] Script determinista contra prod o dump; exit 0; markdown + json
- [ ] Suma de clases = `len(STORES)` / catálogo usado por el daemon
- [ ] Corrida 2026-08-24+ adjuntada al issue (artefacto)
- [ ] Issues hijas solo para clases accionables (no un mega-ticket)

**Depends:** COL-3 ayuda; puede empezar en paralelo con heurística.

---

### COL-7 — P1 — Conectar o delistar 4 US DTC

**Hallazgo:** H4. Tiendas: `casper`, `parachute`, `brooklinen`, `alo_yoga`.

**US-COL-7.1**  
Como ingeniero, quiero status/body (o HAR) por query seed de esas 4, para distinguir WAF/UA vs seed vacío vs catalog GraphQL.

**US-COL-7.2**  
Como founder, quiero una decisión por tienda (`gha_bypass` | `fix_seed` | `delist_from_gate`) escrita en el issue, para no arrastrar 31% success desde el 20-ago.

**US-COL-7.3**  
Como publisher GTM, quiero que si se delistan, no cuenten en coverage del gate ni en “tiendas sanas”, para no ensuciar el 98% 336/343.

**Criterios de aceptación**

- [ ] Log de 1 ciclo (status HTTP, bytes, n productos) por store
- [ ] Decisión en tabla en este PRD §7 (actualizar al cerrar)
- [ ] Si delist: catálogo activo / `get_default_stores()` / gate no las incluye
- [ ] Si GHA: mismo patrón que `collect-egress-blocked-stores.yml`
- [ ] No mezclar este issue en el PR de COL-1–4

**Depends:** ninguno (investigación). Delist puede requerir COL-3.

---

### COL-8 — P1 — Monitor de doble reloj

**Hallazgo:** H5. **Repo:** world `.github/workflows/db-lock-monitor.yml`, `ops/db_lock_monitor.py`.

**Problema:** alerta 6 h sobre `kpis.last_collected_at`. Un backfill/GHA WAF puede tapar un daemon colgado.

**US-COL-8.1**  
Como operador, quiero alerta Slack `#alertas` si el último `collector_runs.finished_at` tiene >5 h **o** el último snapshot >6 h, para no depender de un solo reloj.

**US-COL-8.2**  
Como ingeniero, quiero el check de runs aunque falle el proxy PG (fallback HTTP `/health/collector`), para que un túnel caído no silencie el freshness del daemon.

**Criterios de aceptación**

- [ ] Ambos relojes evaluados; problema si **cualquiera** viola umbral
- [ ] Mensaje Slack nombra qué reloj falló
- [ ] Test unitario del parser con fixture dashboard + health collector
- [ ] `continue-on-error` no oculta un collector_runs stale

**Depends:** ninguno. Mejor si COL-3 ya expone `last_finished`.

---

### COL-9 — P2 — SLA degraded / stale alineado al ciclo 4 h

**Hallazgo:** H5. **Repo:** world `routers/health.py` `derive_collector_status`.

**US-COL-9.1**  
Como operador, quiero `degraded` si el run tiene >5 h y `stale` si >8 h (hoy stale=12 h, dead=24 h), para que un ciclo perdido se vea en `/health/collector` sin esperar medio día.

**Criterios de aceptación**

- [ ] Estados: `ok` | `empty` | `degraded` | `stale` | `dead` | `running` | `unknown`
- [ ] `degraded`: age_run > 5 h o moat ≥ 6 h; `stale`: age_run > 8 h o moat ≥ 8 h; `dead`: ≥ 24 h
- [ ] Tests de umbral; dashboard/C&C mapean `degraded` a amarillo, no a verde
- [ ] Data-gate **no** se cierra en `degraded` (solo stale/dead / coverage)

**Depends:** COL-8 puede shippear antes con umbrales propios.

---

### COL-10 — P2 — Sparklines C&C con baseline

**Hallazgo:** H6. **Repo:** world ops command-control + `ops/metrics/command-control/history.jsonl`.

**US-COL-10.1**  
Como founder, quiero no ver Moat `+193,102` ni sparkline `█▁▁▁▁▁▁▁▁▁` cuando no hay historia, para no leer un “récord” falso.

**US-COL-10.2**  
Como operador, quiero backfill de 20–24 ago desde briefings diarios, para que la tendencia de 10 días sea real.

**Criterios de aceptación**

- [ ] Delta y sparkline omitidos o “n/a” si `len(history) < 2`
- [ ] Backfill jsonl ≥ 5 puntos o issue cerrado con “no hay fuente”
- [ ] Test del renderer

**Depends:** ninguno.

---

### COL-11 — P2 — Verificar `price_history` post WAF bypass

**Hallazgo:** H8. Stores: `smartnutrition_pe`, `simplynaturalcanada_ca`. Fix 20-ago `970fdb2c`.

**US-COL-11.1**  
Como ingeniero, quiero confirmar que el workflow GHA escribe `price_history` (y no solo snapshots), para no reabrir el bug de catalog pull sin historia.

**Criterios de aceptación**

- [ ] Query: últimos 7d `price_history` (o tabla canónica) para esas 2 stores
- [ ] Si vacío: re-run `--catalog-store` y fix de write path
- [ ] Nota en bitácora

**Depends:** ninguno.

---

### COL-12 — P2 (fuera del epic) PAM billing 403

**Hallazgo:** H7. Morning Ops Chain [32735442616](https://github.com/Treevu-ai/cli-market-world/actions/runs/32735442616): 6 FAIL `public.billing_*` HTTP 403. Jobs de moat **verdes**.

**US-COL-12.1**  
Como operador de PAM, quiero que los checks de checkout Pro acepten 403 si el endpoint está gated a auth (o usen token de prueba), para que la cadena matutina no quede roja por un falso P0 de collector.

**Criterios:** PAM verde o skip explícito documentado; no mezclar con PRs de COL-1–11.

---

### COL-13 — P2 (fuera del epic) Timeout Canasta PE

**Hallazgo:** H7. Canasta PE weekly [32736874443](https://github.com/Treevu-ai/cli-market-world/actions/runs/32736874443): `TimeoutError` 45s.

**US-COL-13.1**  
Como operador del índice Canasta PE, quiero timeout ≥90 s y/o payload slim, para que el job semanal no caiga por el mismo dashboard pesado del incidente OOM.

**Criterios:** job verde en una corrida `workflow_dispatch`; no es collector.

---

## 6. Secuencia de implementación

```
COL-1 ─┬─► COL-2
       │
COL-3 ─┴─► COL-6 ─► (hijas de catálogo)
COL-4 ──► COL-5
COL-7  (paralelo, PR aparte)
COL-8  (paralelo a Fase 1)
COL-9  después de COL-8
COL-10, COL-11  (paralelo P2)
COL-12, COL-13  (otro epic / otro PR)
```

**PR slicing**

1. `fix(health): fresh_24h COALESCE + coverage names` → COL-1, COL-2  
2. `feat(health): collector catalog identity + circuit_open` → COL-3, COL-4  
3. `ops: dual-clock freshness monitor` → COL-8  
4. `ops: catalog diff + circuit probe` → COL-5, COL-6  
5. Research/fix US DTC → COL-7  
6. SLA + sparklines + history verify → COL-9, COL-10, COL-11  

Collector Docker/Fly **solo** en PRs que toquen `collect_prices.py` (COL-5 bypass, COL-7 seeds). Secret: `--build-secret`, nunca PAT en build-arg.

---

## 7. Decisiones COL-7 (llenar al cerrar)

| Store | success_pct 24-ago | Decisión | Fecha | Issue |
|---|---|---|---|---|
| casper | 30.7 | `delist_from_gate` — yield crónico ~31% pero fresh; no ensuciar el denominador del gate. Catalog se queda. | 2026-08-24 | COL-7 |
| parachute | 31.0 | `delist_from_gate` (mismo patrón US DTC hogar) | 2026-08-24 | COL-7 |
| brooklinen | 31.1 | `delist_from_gate` | 2026-08-24 | COL-7 |
| alo_yoga | 50.1 | `watch` — más cerca de 70%; re-evaluar tras COL-5 probe. No GHA todavía. | 2026-08-24 | COL-7 |

---

## 8. Criterios de cierre del epic

- [ ] COL-1 y COL-2 en prod: 0 Falabella/Sodimac “no fresh” el mismo día de `last_success`
- [ ] COL-3: identidad de catálogo cuadra en `/health/collector`
- [ ] COL-4: 0 tiendas CB≥10 con `state=ok`
- [ ] COL-6: lista clasificada de ausentes
- [ ] COL-7: 4 decisiones escritas en §7
- [ ] COL-8: alerta por `collector_runs` independiente del MAX snapshot
- [ ] Data-gate sigue `open` con coverage 7d ≥ 80%
- [ ] Dos ciclos collector `age_hours < 5` post-deploy

**No cierra el epic:** COL-12, COL-13.

---

## 9. Fase 0 (hoy, sin issue de código)

1. Tratar collector como **verde** en C&C / data-gate.  
2. No pausar GTM data-gated por H2–H4.  
3. Bitácora: “false stale por `last_seen`; CB abierto 2 LATAM; 4 US DTC partial crónico”.  
4. Abrir issues GitHub COL-1…COL-13 con el cuerpo de §5 (labels `collector` `prd`).

---

## 10. Títulos listos para GitHub

```
COL-1  fix(health): fresh_24h must use last_success when last_seen is null
COL-2  docs/api: split gate coverage_7d from per-store day hit rate
COL-3  feat(health): expose collector catalog identity (attempted/skipped/inactive)
COL-4  fix(health): circuit-open state when consecutive_failures >= skip threshold
COL-5  ops: weekly probe to reset open collector circuits
COL-6  ops: classify catalog gap (388 vs 343)
COL-7  collector: casper/parachute/brooklinen/alo_yoga — fix seed, GHA, or delist
COL-8  ops: freshness monitor on collector_runs AND last snapshot
COL-9  feat(health): degraded/stale SLA aligned to 4h cycle
COL-10 ops: command-control sparklines require history baseline
COL-11 ops: verify price_history for WAF-bypass stores
COL-12 ci: PAM billing 403 false-red on morning chain
COL-13 ci: Canasta PE weekly timeout
```

Cada issue se abre con las US y checkboxes de §5.

Cuerpos copy-paste: [prd/collector-issues.md](prd/collector-issues.md).
