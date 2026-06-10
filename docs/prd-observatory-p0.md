---
title: PRD Observatory P0 — MCP Telemetry Layer
tags:
  - product
  - prd
  - observatory
  - telemetry
status: P0 — listo para implementar
owner: Ricardo Cuba
updated: 2026-06-09
repos: cli-market-world, cli-market-backend, cli-market-core, cli-market-index
supersedes: "PRD — CLI Market Observatory v1.docx (draft)"
---

# Observatory P0 — MCP Telemetry Layer

**Duración:** 45 días · **Prioridad:** P0 · **Estado:** Aprobado para ejecución (post-revisión)

## Resumen ejecutivo

Observatory **no es un producto paralelo**. Es la capa de telemetría MCP que cierra el hueco documentado en código:

> `MCP execution telemetry pending gateway V2` (`market_adoption_index.py`)

**Extiende** lo existente (`funnel_events`, Adoption Index V1, command-control, APIs públicas). **No reemplaza** tablas ni dashboards actuales sin migración explícita.

| Antes (PRD v1 draft) | P0 (este doc) |
|----------------------|---------------|
| Greenfield: `agent_events`, `agents`, `daily_metrics` | Evolución: telemetry layer + integración con funnel/index |
| Adoption Index en Backlog Fase 2 | **Existente v1** — evolucionar señal `agent_usage_proxy` |
| North Star ambiguo vs Adoption Index | **MAA** ejecutivo; Adoption Index = score derivado |
| Retención sin cohorte definida | Cohorte = **primera llamada MCP exitosa** |
| Dashboard nuevo aislado | Sub-vista **Observatory** + feed para command-control |

---

## 0. Ecosistema — 4 repos (obligatorio)

El producto CLI Market son **cuatro repos**. Cualquier cambio de Observatory debe respetar ownership, sincronizar mirrors y **bump de dependencias en orden**.

```
cli-market-index    →  Golden Records (semantic moat)
cli-market-core     →  Intelligence SDK (PyPI) — identidad, MCP registry, agregación compartida
cli-market-backend  →  API producción Railway (fuente de verdad de telemetría en prod)
cli-market-world    →  PyPI `cli-market-world`, landing, ops/CI, mirror API para dev y paridad
```

> `cli-market-content` es GTM autónomo — fuera del scope de implementación Observatory (solo consume métricas data-gated).

### 0.1 Ownership por repo

| Repo | Rol en Observatory P0 | Cambios P0 |
|------|----------------------|------------|
| **cli-market-core** | Primitivas compartidas importables vía PyPI | `market_observatory/` (schema DDL, `resolve_agent_id`, `record_agent_event`, noise filter re-export), `X-Agent-ID` en docs MCP, bump `PACKAGE_VERSION` |
| **cli-market-backend** | **Deploy producción** — middleware + persistencia | `market_observatory.py`, `ObservatoryMiddleware` en `market_server.py`, `routers/observatory.py`, tests, `requirements.txt` pin core |
| **cli-market-world** | Mirror API + ops + landing | **Mismos archivos API que backend** (paridad), `ops/observatory_daily.py`, `market_adoption_index.py`, `landing/app/stats/`, workflows CI, `pyproject.toml` pin core |
| **cli-market-index** | Sin cambios P0 | Ninguno — no instrumentar entity resolution en telemetry |

### 0.2 Regla de mirror (world ↔ backend)

Patrón existente (`ops/PRICING-CHANGE-CHECKLIST.md`, `market_funnel.py`, `routers/funnel.py`):

1. Implementar en **backend** primero (Railway es prod).
2. **Copiar/sync** al mismo path relativo en **world** antes de merge.
3. Lógica reutilizable → extraer a **core**; world y backend solo importan.

Archivos que deben mantenerse **sincronizados** en P0:

| Archivo | backend | world |
|---------|---------|-------|
| `market_observatory.py` | ✓ | ✓ (mirror) |
| `routers/observatory.py` | ✓ | ✓ |
| `market_server.py` (middleware) | ✓ | ✓ |
| `server_deps.py` (si auth agent) | ✓ | ✓ |

Archivos **solo world** (ops / landing):

- `ops/observatory_daily.py`, `ops/adoption_index.py`, `market_adoption_index.py`
- `landing/app/stats/page.tsx`, `landing/hooks/useObservatoryStats.ts`
- `.github/workflows/observatory-nightly.yml`

### 0.3 Orden de release y dependencias

Cada entrega Observatory sigue este orden (checklist: `ops/OBSERVATORY-CHANGE-CHECKLIST.md`):

```
1. cli-market-core     → PR + tag + PyPI publish (cli-market-core>=X.Y.Z)
2. cli-market-backend  → bump requirements.txt → PR + Railway deploy
3. cli-market-world    → bump pyproject.toml → mirror API → PR + PyPI tag v*
4. cli-market-index    → sin bump (salvo doc README ecosystem si aplica)
```

**Pins actuales (2026-06-09):**

| Consumidor | Dependencia | Versión |
|------------|-------------|---------|
| `cli-market-world` `pyproject.toml` | `cli-market-core` | `>=1.9.16` |
| `cli-market-backend` `requirements.txt` | `cli-market-core` | `>=1.9.5` → alinear a `>=1.9.17` post-Observatory |
| `cli-market-backend` `requirements-private.txt` | `cli-market-index` | pin git SHA (sin cambio P0) |
| PyPI publish workflow | `cli-market-core` | `>=1.9.6` en CI install step |

**Versiones a bump juntas** cuando Observatory ship:

- `cli-market-core` `pyproject.toml` `version`
- `cli-market-core` `market_core/market_stats.py` `PACKAGE_VERSION`
- `cli-market-world` `pyproject.toml` `version` + `cli-market-core>=` pin
- `CHANGELOG.md` (entrada por repo afectado)

### 0.4 Dónde vive cada capa (decisión P0)

| Capa | Repo canónico | Notas |
|------|---------------|-------|
| Tablas `agent_events`, `agents`, `daily_observatory_metrics` | Postgres prod (backend) | DDL en `market_observatory` (core); migrate en startup backend + world |
| Middleware HTTP | backend (+ mirror world) | backend ya tiene `AccessLogMiddleware` — extender, no duplicar |
| MCP `tool_name` registry | core `market_mcp_registry` | Una fuente para nombres instrumentados |
| Adoption Index / MAA | world `market_adoption_index.py` | Job CI en world; lee DB prod vía `DATABASE_URL` remoto o API |
| Landing `/stats` | world `landing/` | Consume `GET /analytics/observatory` |
| Command-control Slack | world `ops/` | Remoto `--remote` contra API prod |

### 0.5 Producción vs desarrollo

- **Telemetría real** solo cuenta si corre en **cli-market-backend** desplegado (Railway).
- **cli-market-world** `market-server` local sirve para dev/tests; debe comportarse igual (mismo middleware).
- Ops nightly (`observatory_daily`, `adoption_index`) viven en world pero apuntan a prod (`MARKET_API_URL` / `DATABASE_URL`).

---

## 1. Objetivo estratégico (sin cambio)

Transformar CLI Market de infraestructura de commerce hacia plataforma que **mide adopción real de agentes** — herramientas, retailers, países, workflows y retorno.

Al cerrar P0, el sistema debe responder **sin análisis manual**:

1. ¿Cuántos agentes únicos usaron CLI Market en los últimos 30 días?
2. ¿Cuántas consultas MCP/API se ejecutaron (exitosas)?
3. ¿Qué herramientas son las más usadas?
4. ¿Qué retailers generan más interés?
5. ¿Qué países concentran actividad?
6. ¿Cuál es la retención 7d / 30d?
7. ¿Cuál es el crecimiento semanal de agentes activos?

**Fuente canónica:** `GET /analytics/observatory` (nuevo) + snapshots diarios + command-control.

---

## 2. Inventario — qué ya existe (no reconstruir)

### 2.1 Embudo de onboarding (`funnel_events`)

| Pieza | Ubicación |
|-------|-----------|
| Tabla + schema | `market_funnel.py` → `funnel_events` |
| Ingesta | `POST /v1/events` (`routers/funnel.py`) |
| Eventos | `install`, `register`, `first_search`, `activated`, `mcp_setup_completed`, … |
| Agregados públicos | `GET /analytics/funnel` |
| Admin | `GET /dashboard/funnel` |
| Noise filter | `is_noise_username()` — smoke, CI, `user-<hex>` |
| Retención actual | `funnel_retention_summary()` — cohorte `first_search` |

**Rol en Observatory:** señales de **activación y conversión** (humano/agente que completa onboarding). No sustituye telemetría por llamada.

### 2.2 Adoption Index V1 (existente — integrar, no backlog)

| Pieza | Ubicación |
|-------|-----------|
| Score compuesto | `market_adoption_index.py` |
| Job diario | `ops/adoption_index.py` + `.github/workflows/adoption-index-nightly.yml` |
| Snapshots | `adoption_index_snapshots`, `ops/metrics/adoption-index/` |
| API pública | `GET /analytics/adoption-index` |
| Admin | `GET /dashboard/adoption-index` |
| Proxy actual de “agentes” | `agent_usage_proxy` = `first_search` users |

**Cambio P0:** reemplazar `agent_usage_proxy` por **MAA / unique agents desde `agent_events`** cuando telemetry esté activa. Mantener peso `real_usage` en el índice.

### 2.3 Data moat y analytics de precios

| Pieza | Ubicación | Nota |
|-------|-----------|------|
| Dashboard operativo | `routers/dashboard.py` | Precios, cobertura, collector — **no mezclar** con Observatory |
| Stats de moat | `GET /analytics/stats` | `price_snapshots`, `search_queries` — catálogo, no agentes |
| Registry | `GET /index/stats` | Golden records |

### 2.4 Ops y GTM

| Pieza | Ubicación |
|-------|-----------|
| Panel founder | `ops/command_control_daily.py` → `#command-control` |
| Funnel digest | `ops/funnel_digest_daily.py` → `#funnel-cli-market` |
| Landing funnel UI | `landing/components/FunnelMetrics.tsx` |
| Data-gate GTM | `make gate` en cli-market-content |

---

## 3. Jerarquía de métricas (P0 — unificación)

### North Star (ejecutivo)

**Monthly Active Agents (MAA)** — agentes únicos con ≥1 llamada MCP/API **exitosa** en ventana rolling 30 días.

- Reportado en: command-control, Epic Executive (interno), `/stats` (si data-gate OK).
- No confundir con: descargas PyPI, registros, ni `first_search`.

### Métricas operativas (diarias)

| KPI | Definición | Tabla / job |
|-----|------------|-------------|
| DAA | Unique agents con ≥1 call exitosa en 24h | `daily_observatory_metrics` |
| Successful Calls | `success = true` en `agent_events` | `agent_events` |
| Success Rate | successful / total calls | agregación diaria |
| 7d / 30d Retention | Ver §5 | agregación diaria |
| Organizations | Distinct `organization_id` con actividad | `agents` |

### Adoption Index (derivado — no North Star)

Score compuesto V1 (pesos actuales en `market_adoption_index.py`):

- `downloads` 30% — PyPI multi-package
- `real_usage` 25% — **P0: alimentar desde MAA**, no solo `first_search`
- `growth` 20%
- `activation` 15%
- `revenue_intent` 10%

El índice **resume** salud de adopción; MAA **manda** en decisiones de producto.

---

## 4. Glosario (obligatorio en implementación)

| Término | Definición | Fuente de identidad |
|---------|------------|---------------------|
| **Agent** | Actor que invoca herramientas MCP o endpoints API instrumentados | Ver §6 |
| **User** | Cuenta CLI (`username`) autenticada | `auth_user()`, funnel |
| **Session** | Instalación CLI sin login (`session_id` en funnel) | `POST /v1/events` |
| **Organization** | Tenant de facturación o equipo (Pro+) | API key metadata / billing |
| **Call** | Una invocación instrumentada de tool o ruta API | `agent_events` |
| **Successful Call** | Call con `success = true` y sin error de negocio | middleware |
| **Activation** | Usuario con `first_search` o `mcp_setup_completed` | `funnel_events` |
| **Active Agent** | Agent con ≥1 successful call en ventana | `agent_events` |

**Regla:** un User autenticado mapea 1:1 a `agent_id` cuando usa API key o `X-Agent-ID` estable. Session anónima usa fingerprint hasta `register`.

---

## 5. Retención — cohorte canónica (P0)

### Cohorte

**Día 0 = timestamp de la primera llamada MCP/API exitosa** del agente (`agent_events`, `success = true`).

No usar solo `first_search` del funnel para retención de producto MCP (métrica distinta — mantener como **Activation Retention** en funnel).

### Retained

Agente con ≥1 successful call en días `(1 .. N]` tras día 0, donde N ∈ {7, 30}.

### Fórmula

```
retention_7d = agents_with_followup_7d / agents_with_first_success_in_cohort_window
```

### Dual reporting (interno)

| Métrica | Cohorte | Uso |
|---------|---------|-----|
| `mcp_retention_7d` | Primera call exitosa | Observatory, MAA, `/stats` |
| `activation_retention_7d` | `first_search` (actual) | Funnel, GTM, onboarding |

Ambas coexisten; command-control muestra **mcp_retention_7d** como primaria post-P0.

---

## 6. Identidad de agente (P0)

Prioridad de resolución (igual que PRD original, con reglas de repo):

1. **`X-Agent-ID`** — header explícito del cliente MCP/CLI (nuevo, documentar en MCP setup).
2. **`agent_id` desde API key** — hash estable del key id (no el secret).
3. **`username`** — si Bearer auth resuelve usuario.
4. **`session_id`** — solo pre-registro; migrar a username en `register`.
5. **Hash derivado** — último recurso: `sha256(ip + user_agent + day_bucket)` — marcar `metadata.identity_confidence = low`.

Tabla `agents` (nueva, derivada de eventos):

```sql
CREATE TABLE agents (
    agent_id TEXT PRIMARY KEY,
    first_seen_at TIMESTAMPTZ NOT NULL,
    last_seen_at TIMESTAMPTZ NOT NULL,
    country TEXT,
    organization_id TEXT,
    identity_source TEXT NOT NULL,  -- x_agent_id | api_key | username | session | fingerprint
    linked_username TEXT,           -- nullable, join funnel
    metadata JSONB DEFAULT '{}'
);
```

Upsert en cada evento; **no** mantener agentes solo en memoria.

---

## 7. Telemetría — `agent_events` (P0)

### Schema

```sql
CREATE TABLE agent_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    agent_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    route TEXT,                    -- ej. POST /mcp/tools/market_search
    country TEXT,
    organization_id TEXT,
    success BOOLEAN NOT NULL,
    latency_ms INTEGER,
    retailer TEXT,
    query_type TEXT,               -- search | compare | checkout | catalog | other
    error_code TEXT,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_agent_events_occurred ON agent_events(occurred_at);
CREATE INDEX idx_agent_events_agent ON agent_events(agent_id, occurred_at);
CREATE INDEX idx_agent_events_tool ON agent_events(tool_name, occurred_at);
CREATE INDEX idx_agent_events_retailer ON agent_events(retailer) WHERE retailer IS NOT NULL;
```

### Qué instrumentar (P0)

| Superficie | `tool_name` | Notas |
|------------|-------------|-------|
| MCP `market_search` | `market_search` | retailer, country desde args |
| MCP `market_compare` | `market_compare` | |
| MCP `market_checkout` | `market_checkout` | |
| MCP `market_login` / auth tools | nombre registry | |
| REST equivalentes bajo `/v1/*` | mismo nombre | dedupe si doble path |
| **No instrumentar P0** | health, static, admin cron | excluir ruido |

### Middleware (requisitos)

- Escritura **async** (cola en memoria + batch insert o background task) — latencia añadida < 5ms p95.
- Fallo de telemetry **nunca** rompe la request (fail-open).
- `metadata` allowlist: `client`, `mcp_version`, `cli_version`, `identity_confidence` — **sin** queries ni PII.
- Heredar noise filter: excluir tokens/usernames de smoke (`is_noise_username`).

### Cliente MCP (gap conocido)

Llamadas 100% locales sin API **no** aparecen en `agent_events` hasta P1. P0 acepta cobertura **server-side**; CLI reportará `X-Agent-ID` en requests autenticadas. Documentar % cobertura en dashboard.

---

## 8. Agregación diaria (P0)

Nueva tabla — **no** duplicar `adoption_index_snapshots`:

```sql
CREATE TABLE daily_observatory_metrics (
    date DATE PRIMARY KEY,
    unique_agents INTEGER NOT NULL,
    daily_active_agents INTEGER NOT NULL,
    calls_total INTEGER NOT NULL,
    calls_success INTEGER NOT NULL,
    success_rate NUMERIC(5,4),
    mcp_retention_7d NUMERIC(5,4),
    mcp_retention_30d NUMERIC(5,4),
    countries_active INTEGER,
    retailers_queried INTEGER,
    top_tools JSONB,
    top_retailers JSONB,
    top_countries JSONB,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Job:** `ops/observatory_daily.py` (nuevo), schedule junto a `adoption_index.py` (nightly CI).

**Flujo:**

1. Agregar `agent_events` → `daily_observatory_metrics`
2. Pasar `unique_agents` / MAA a `compute_adoption_index()` → actualiza señal `real_usage`
3. Append snapshot command-control (`ops/metrics/command-control/`)

---

## 9. APIs y UI (P0 mínimo)

### Nuevos endpoints

| Método | Ruta | Auth | Contenido |
|--------|------|------|-----------|
| GET | `/analytics/observatory` | Público, agregados | MAA, calls, top tools/retailers/countries, retention |
| GET | `/dashboard/observatory` | Admin | Series 30d, cohortes, cobertura telemetry |
| GET | `/stats` | Público (landing) | Subset data-gated para prueba social |

### Reutilizar (sin breaking changes)

- `GET /analytics/funnel` — onboarding
- `GET /analytics/adoption-index` — score; internals actualizados
- `GET /dashboard` — data moat sin cambios

### Command-control

Extender `ops/command_control_daily.py` con bloque **Observatory**: MAA, DAA, success rate, mcp_retention_7d, sparkline 7d.

---

## 10. Data-gate — métricas públicas (`/stats`)

Solo publicar cifras que pasen gate (mismo criterio GTM que `make gate`):

| Métrica | Público P0 | Condición |
|---------|------------|-----------|
| Countries covered | Sí | Catálogo estático / collector |
| Retailers covered | Sí | `MARKET_STATS` / index |
| Products indexed | Sí | data moat verificado |
| Queries served | Sí | `agent_events` agregado, ≥7 días estable |
| Active agents (30d) | Sí | MAA ≥ umbral founder (default: mostrar solo si ≥10) |
| Success rate | Interno | Solo dashboard admin |
| Rankings detallados | Interno P0 | `/stats` solo top-5 agregados |

---

## 11. No objetivos (sin cambio)

Durante P0 **no** se desarrolla:

- Marketplace, pagos, Trust Index, Commerce Index, certificaciones
- ClickHouse / warehouse split (solo nota de compatibilidad schema)
- Rankings públicos avanzados
- Telemetría client-side 100% (diferido P1)

---

## 12. Roadmap P0 (45 días) — por repo

### Sprint 1 — Semanas 1–2 (fundación)

| # | Entregable | core | backend | world | index |
|---|------------|------|---------|-------|-------|
| 1 | Paquete `market_observatory` (DDL, identity, record) | ✓ nuevo | import | import | — |
| 2 | `market_observatory.py` shim + schema startup | — | ✓ | ✓ mirror | — |
| 3 | `ObservatoryMiddleware` async | — | ✓ | ✓ mirror | — |
| 4 | `X-Agent-ID` + MCP docs | ✓ registry | — | README, `market mcp-setup` | — |
| 5 | Bump `cli-market-core` PyPI | ✓ tag | pin | pin | — |
| 6 | Job `daily_observatory_metrics` | agregador opcional | — | ✓ `ops/observatory_daily.py` + CI | — |
| 7 | Adoption Index ← MAA | — | — | ✓ `market_adoption_index.py` | — |

### Sprint 2 — Semanas 3–4 (superficie)

| # | Entregable | core | backend | world | index |
|---|------------|------|---------|-------|-------|
| 8 | `GET /analytics/observatory` | — | ✓ router | ✓ mirror | — |
| 9 | `GET /dashboard/observatory` | — | ✓ | ✓ mirror | — |
| 10 | Dashboard HTML (opcional) | ✓ renderer hook | — | ✓ o core | — |
| 11 | Landing `/stats` | — | — | ✓ | — |
| 12 | command-control + digest | — | — | ✓ `ops/` | — |
| 13 | Tests | ✓ unit identity | ✓ integration | ✓ mirror tests | — |
| 14 | Railway deploy + PyPI tag | — | ✓ deploy | ✓ `v*` tag | — |

### Semanas 5–6 — Buffer

- Rollout gradual (`OBSERVATORY_TELEMETRY=1`)
- Validación vs funnel (sanity: MAA ≤ registros activos + sesiones)
- Privacy review (`landing/app/legal/privacy`)
- Documentar migración ClickHouse (diseño solamente)

---

## 13. Criterios de aceptación P0

### Ecosistema (4 repos)

- [ ] `cli-market-core` publicado en PyPI con módulo `market_observatory`
- [ ] `cli-market-backend` y `cli-market-world` pinnean la **misma** versión mínima de core
- [ ] Archivos mirror (§0.2) diff-clean entre backend y world antes de release
- [ ] Railway prod desplegado desde backend **antes** de publicar tag PyPI world
- [ ] `CHANGELOG.md` actualizado en cada repo tocado
- [ ] `cli-market-index` sin cambios de código (o justificación documentada si cambia)

### Telemetría y producto

- [ ] ≥95% de llamadas MCP/API instrumentadas en server-side pasan por `agent_events`
- [ ] 100% de eventos tienen `agent_id` resoluble (ningún NULL)
- [ ] `daily_observatory_metrics` generado automáticamente 7 días consecutivos sin fallo
- [ ] `GET /analytics/observatory?days=30` responde las 7 preguntas del §1
- [ ] Adoption Index `real_usage` usa MAA, no solo `first_search`
- [ ] `mcp_retention_7d` calculado con cohorte §5, documentado en API
- [ ] command-control muestra MAA + sparkline sin consultas manuales
- [ ] `/stats` publicado con data-gate; sin PII
- [ ] Noise filter excluye smoke/CI de métricas founder
- [ ] Tests cubren: identity resolution, aggregation, retention, public API shape

---

## 14. Baseline y targets (founder — completar antes de Sprint 2)

| Métrica | Baseline (2026-06-09) | Target 45d | Fuente baseline |
|---------|----------------------|------------|-----------------|
| MAA | ~1 (`first_search` proxy) | 25 | `ops/metrics/adoption-index/latest.json` |
| Successful calls / día | 0 (no telemetry) | 100 | — |
| MCP success rate | — | ≥92% | — |
| mcp_retention_7d | — | ≥25% | — |
| Adoption Index score | 66.4 (C) | ≥72 (C+) | adoption-index nightly |

---

## 15. Referencias

- PRD original: `PRD — CLI Market Observatory v1.docx`
- PRD growth: `docs/cli-market-prd-v2.md`
- Checklist release 4 repos: `ops/OBSERVATORY-CHANGE-CHECKLIST.md`
- Patrón multi-repo: `ops/PRICING-CHANGE-CHECKLIST.md`, `CHANGELOG.md` [2026-06-05]
- Ecosystem READMEs: `../cli-market-core/README.md`, `../cli-market-backend/README.md`, `../cli-market-index/README.md`
- Código funnel: `market_funnel.py`, `routers/funnel.py` (world + backend mirror)
- Adoption Index: `market_adoption_index.py`, `ops/adoption_index.py` (world)
- Ops founder: `ops/COMMAND_CONTROL.md`, `ops/command_control_daily.py`
- Marca / data en creative: `docs/BRAND.md`, `AGENTS.md` (data-gate)

---

## Changelog P0 vs PRD v1 draft

| Cambio | Razón |
|--------|-------|
| Initiative renombrada a **MCP Telemetry Layer** | Evita greenfield duplicado |
| Adoption Index → existente v1 | Ya en prod con nightly job |
| `daily_metrics` → `daily_observatory_metrics` | No colisionar con adoption snapshots |
| Retención dual MCP vs activation | Métricas distintas, mismas herramientas |
| Dashboard Observatory separado de data moat | UX y ownership claros |
| Epic 6 ClickHouse → diseño only | Fuera de capacidad 45d |
| Executive dashboard → command-control | Un solo panel founder |
| Single-repo assumption | §0 ecosistema 4 repos + mirror world/backend |
| `market_observatory` solo en world | Primitivas en core; API en backend+world |
