# Issues — PRD Collector Observability

Cuerpos listos para pegar en GitHub. Spec completa: [prd-collector-observability-coverage.md](../prd-collector-observability-coverage.md).  
Diagnóstico: [collector-integral-debug-2026-08-24.md](../reports/collector-integral-debug-2026-08-24.md).

Labels: `collector`, `prd`, `P0`|`P1`|`P2`.

---

## COL-1 — P0 — `fresh_24h` deja de mentir

**US-COL-1.1** Como operador de C&C, quiero que una tienda con recolección exitosa en las últimas 24 h aparezca `fresh_24h=true`, para no vigilar falsos negativos.

**US-COL-1.2** Como publisher GTM, quiero que el data-gate y `/v1/sources/health` no contradigan el dashboard slim en frescura 24 h, para no publicar claims incoherentes.

**US-COL-1.3** Como ingeniero, quiero un test con `last_success=now`, `last_seen=null` y un snapshot reciente, para que el falso negativo no regrese.

**AC**
- [ ] `fresh_24h = age(COALESCE(last_seen, last_success, max_snapshot_ts)) < 24h`
- [ ] Fixture `last_seen=null` + `last_success` hace 2 h → `fresh_24h is True`
- [ ] Pin/bump core si el fix sale en `market_core/source_health.py`

---

## COL-2 — P0 — Un solo coverage 7d para el gate

**US-COL-2.1** Como publisher GTM, quiero un campo canónico para el gate y otro nombre para el hit-rate por tienda, para no citar 40% cuando el gate es 94%.

**US-COL-2.2** Como operador de C&C, quiero que el scoreboard muestre un coverage 7d etiquetado, para no explicar dos porcentajes en el briefing.

**AC**
- [ ] Slim/dashboard `coverage_7d_pct` = % tiendas con ≥1 snapshot en 7d
- [ ] Per-store = `store_day_hit_rate_7d_pct` (o glosario explícito)
- [ ] Doc moat reporting actualizado

---

## COL-3 — P1 — Identidad de catálogo en `/health/collector`

**US-COL-3.1** Como ingeniero, quiero `stores_total`, `attempted`, `succeeded`, `skipped`, `inactive` + arrays de skip, para que `total = attempted + skipped + inactive`.

**US-COL-3.2** Como operador, quiero ver “343/388 en ciclo · N skipped” en C&C, para no inflar cobertura con 343/343.

**AC**
- [ ] Payload cuadra ±0
- [ ] Test de contrato del endpoint

---

## COL-4 — P1 — Circuit breaker visible

**US-COL-4.1** Como operador, quiero `state=circuit_open` cuando el collector ya no intenta la tienda, para que salga como crítica en bitácora.

**US-COL-4.2** Como ingeniero, quiero el mismo umbral en daemon y sources (`CB_PERSIST_SKIP`), para no tener dos verdades.

**AC**
- [ ] `consecutive_failures >= skip` ⇒ no `ok` aunque success_pct lifetime sea alto
- [ ] Test 10 fallos + 93% lifetime

---

## COL-5 — P1 — Probe semanal de circuitos abiertos

**US-COL-5.1** Como ingeniero collector, quiero un job semanal que pruebe una vez cada store `circuit_open` y resetee fallos si hay 200 + precios, para recuperar retailers que volvieron.

**AC**
- [ ] Script/workflow acotado a `circuit_open`
- [ ] Resultado documentado para santiagonativo_cl y rootscosmetica_ec

---

## COL-6 — P1 — Inventario del gap 388 − 343

**US-COL-6.1** Como ingeniero, quiero un script que clasifique cada store (`in_cycle` / `skipped_cb` / `no_seeds` / `growth_deferred` / `waf_gha_only` / `inactive` / `unknown`).

**US-COL-6.2** Como operador, quiero esa tabla en el briefing semanal, para decidir onboarding vs delist.

**AC**
- [ ] Suma de clases = catálogo
- [ ] Artefacto de una corrida adjunto al issue

---

## COL-7 — P1 — Conectar o delistar 4 US DTC

**US-COL-7.1** Como ingeniero, quiero status/body por query seed de casper, parachute, brooklinen, alo_yoga.

**US-COL-7.2** Como founder, quiero decisión por tienda: `gha_bypass` | `fix_seed` | `delist_from_gate`.

**US-COL-7.3** Como publisher GTM, quiero que un delist no cuente en el denominador del gate.

**AC**
- [ ] Log de 1 ciclo por store
- [ ] Tabla de decisión en el PRD §7
- [ ] PR aparte de COL-1–4

---

## COL-8 — P1 — Monitor de doble reloj

**US-COL-8.1** Como operador, quiero alerta si `collector_runs.finished_at` >5 h **o** último snapshot >6 h.

**US-COL-8.2** Como ingeniero, quiero fallback HTTP `/health/collector` si el proxy PG falla.

**AC**
- [ ] Slack nombra qué reloj falló
- [ ] Test con fixture dashboard + health

---

## COL-9 — P2 — SLA degraded / stale (ciclo 4 h)

**US-COL-9.1** Como operador, quiero `degraded` >5 h y `stale` >8 h, para ver un ciclo perdido sin esperar 12 h.

**AC**
- [ ] Estados documentados; C&C mapea `degraded` a amarillo
- [ ] Data-gate no cierra en `degraded`

---

## COL-10 — P2 — Sparklines C&C con baseline

**US-COL-10.1** Como founder, quiero no ver Moat `+193k` si no hay historia.

**US-COL-10.2** Como operador, quiero backfill 20–24 ago o cierre “sin fuente”.

**AC**
- [ ] Delta/sparkline n/a si `len(history) < 2`
- [ ] Test del renderer

---

## COL-11 — P2 — Verificar `price_history` WAF bypass

**US-COL-11.1** Como ingeniero, quiero confirmar history 7d para smartnutrition_pe y simplynaturalcanada_ca.

**AC**
- [ ] Query prod; re-run `--catalog-store` si vacío

---

## COL-12 — P2 (fuera de epic) PAM billing 403

**US-COL-12.1** Como operador de PAM, quiero que billing 403 no ponga roja la Morning Ops Chain (aceptar 403 gated o token de prueba).

---

## COL-13 — P2 (fuera de epic) Timeout Canasta PE

**US-COL-13.1** Como operador del índice Canasta PE, quiero timeout ≥90 s y/o payload slim.

---

## Orden de PRs

1. COL-1 + COL-2  
2. COL-3 + COL-4  
3. COL-8  
4. COL-5 + COL-6  
5. COL-7  
6. COL-9 + COL-10 + COL-11  
7. COL-12 / COL-13 en PRs de CI, no de collector
