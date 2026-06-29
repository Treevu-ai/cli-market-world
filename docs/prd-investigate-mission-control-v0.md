---
title: PRD — investigate v0 + Mission Control TUI v0
tags:
  - product
  - prd
  - cli
  - agentos
  - intelligence
status: Closed — Shipped v1.0 · 2026-06-29
owner: Ricardo Cuba
updated: 2026-06-29
closed: 2026-06-29
duration: 2 semanas (10 días hábiles)
repos: cli-market-core, cli-market-world
depends_on:
  - docs/prd-observatory-p0.md (P0 shipped)
  - T-173 core 1.9.35 (observatory_snapshot_streak)
---

# PRD: investigate v0 + Mission Control TUI v0

**Duración:** 2 semanas · **Prioridad:** P1 · **Capa comercial:** Build + Intelligence (no Procure)

## 1. Problem Statement

CLI Market ya tiene primitivas (`market search`, `market compare`, `market intel *`, MCP tools, Observatory API) pero el usuario **construye misiones a mano** encadenando comandos. Eso posiciona el producto como CLI de productividad, no como **sistema operativo para agentes comerciales**.

**Evidence:**
- `market_cli.py` ya declara “Sistema operativo de compras” pero el entrypoint real es argparse + REPL limitado (`market shell` solo expone ~10 handlers).
- Landing y GTM venden **54k+ precios, 38 retailers, MCP, inflación/spreads** — no “lista de comandos”.
- Observatory P0 entrega MAA, retention, streak — **sin superficie TUI** más allá de `doctor` / `account`.
- Intelligence ($300–500) necesita demo reproducible; hoy requiere conocer subcomandos `intel inflation|indicators|scores`.

**Cost of not solving:** builders no ven el moat en <60s; outbound Intelligence sigue siendo “API docs”; competimos con CLIs genéricas en UX, no en datos LATAM.

## 2. Goals & Success Metrics

| Goal | Metric | Baseline | Target (60 días) | Window |
|------|--------|----------|------------------|--------|
| Time-to-insight | Median time from `market shell` → report with ≥3 insights | N/A | <90s (demo path) | 60d |
| Mission adoption | % Pro/Starter users running ≥1 `investigate`/week | 0 | ≥15% of active CLI users | 60d |
| Intelligence pipeline | Outbound demos using `investigate` (logged) | 0 | ≥5 pilot conversations | 30d |
| Observatory surfacing | Users who see Mission Control header (MAA/freshness) | ~0 | 100% shell sessions | launch |
| Quality | Investigation reports with data-gate-only claims | N/A | 100% (zero invented metrics) | launch |

## 3. Non-Goals (v0)

- Web Console, Agent Marketplace, MCP Registry público third-party
- LLM planner libre (“chat con el mercado”) — v0 es **workflow determinístico**
- Procure flows (aprobaciones, checkout operador) — capa App separada
- Nuevos indicadores en core — solo **componer** los existentes
- Replacing MCP tools — `investigate` llama los mismos endpoints/tools
- Mobile / Cloudflare landing changes (salvo link docs)

## 4. User Personas & Stories

**Primary:** Agent builder (Pro) — integra MCP, quiere validar moat antes de embed.

**Secondary:** Intelligence analyst (pilot) — necesita reporte shareable inflación/spreads sin SQL.

### Story 1 — Investigate mission
As an agent builder, I want `market investigate "arroz peru"` so that I get search + compare + spread + inflación in one report without chaining 4 commands.

**Acceptance criteria:**
- [ ] Given query + country (explicit or default PE), when `investigate` runs, then output includes: retailers scanned, price leader/laggard, spread %, inflación línea si disponible
- [ ] Given `--json`, when complete, then envelope matches `market_ui.json_response` schema
- [ ] Given API errors, when partial data, then report marks sections `unavailable` — no hallucination
- [ ] Performance: p95 <15s on prod API with `MARKET_SKIP_LIVE` off (CI uses mock/live gate)

### Story 2 — Mission Control home
As a Pro user opening `market shell`, I want a Mission Control header so that I see data freshness, coverage, and suggested missions.

**Acceptance criteria:**
- [ ] Shell startup shows: package version, refresh hours, retailers/countries (from `market_stats` data-gate labels only)
- [ ] If authenticated + Observatory reachable: MAA display tier (respect public threshold from Observatory PRD)
- [ ] Menu lists: Investigate, Compare basket (link `compare`), Intel retail (link `intel inflation`), Doctor, MCP setup
- [ ] Unauthenticated: same shell but missions gated with `register` / `login` hints

### Story 3 — MCP Center (read-only v0)
As a Pro user, I want `market mcp` (alias `mcp center`) so that I see installed tool names + health from doctor.

**Acceptance criteria:**
- [ ] Lists tools from `market_core.market_mcp_registry.list_tools("default")`
- [ ] Shows doctor status (API reachable, auth tier, key valid)
- [ ] Does not install/configure — points to existing `market mcp-setup`

## 5. Solution Overview

### Narrative

v0 no crea “AgentOS” monolítico. Agrega **dos capas finas** sobre lo existente:

1. **`investigate` mission** en **core** — función pura que orquesta HTTP/API calls (misma lógica usable desde MCP tool futuro).
2. **Mission Control TUI** en **world** — mejora `market shell` + comandos CLI; consume Observatory + stats existentes.

```mermaid
flowchart LR
  subgraph world [cli-market-world]
    CLI[market_cli.py]
    UI[market_ui.py]
    Shell[market shell]
  end
  subgraph core [cli-market-core]
    Mission[market_missions.investigate]
    MCPReg[market_mcp_registry]
    Stats[market_stats]
  end
  subgraph api [Railway API]
    Search[/products/search]
    Compare[/products/compare]
    Intel[/v1/dispersion etc]
    Obs[/analytics/observatory]
  end
  CLI --> Shell
  Shell --> UI
  CLI --> Mission
  Mission --> Search
  Mission --> Compare
  Mission --> Intel
  UI --> Obs
  UI --> Stats
  CLI --> MCPReg
```

### UX — Mission Control (shell startup)

```
CLI MARKET OS · v1.9.35

Freshness     4h          Retailers     38
Countries     8           Prices        54,000+  (data-gate)

────────────────────────────────────────
MISSIONS
  1  investigate QUERY     Deep market report
  2  compare QUERY         Multi-retailer prices
  3  intel inflation       Line inflation (PE default)
  4  doctor                API · auth · MCP health
  5  mcp                   Tool registry (read-only)
────────────────────────────────────────
market>
```

### UX — investigate report (rich)

```
MISSION · investigate · arroz · PE

Sources     12 retailers · 847 SKUs matched
Leader      Metro S/ 4.89/kg
Laggard     Wong +18% vs mean
Spread      22% max
Inflation   Arroz +5.2% (30d)   [if intel available]

Recommendations (rules-based, v0)
  1. Monitor Wong if spread >25%
  2. Prefer Metro for basket baseline
```

Recommendations v0 = **template rules** on spread/inflation thresholds — no LLM.

### Key design decisions

| Decision | Choice | Trade-off |
|----------|--------|-----------|
| Planner | Deterministic pipeline | No “Deep Research” flex; ship fast, auditable |
| Core vs world | Mission logic in **core** | Requires PyPI release; enables future MCP `market_investigate` |
| Observatory in shell | Best-effort fetch public `/analytics/observatory` | Fails open if offline |
| Tier gate | `investigate` requires **Starter+** (export/intel adjacency) | Free users see CTA upgrade — aligns pricing |
| Intel sections | Optional if `/v1/*` auth fails | Report still valuable with search/compare only |

## 6. Technical Considerations

### Repo ownership

| Repo | Changes |
|------|---------|
| **cli-market-core** | New module `market_core/market_missions.py`: `run_investigate(query, country, *, client)` → structured dict; optional MCP tool stub (disabled flag until v0.2) |
| **cli-market-world** | `market_cli.py`: `cmd_investigate`, extend `cmd_shell` Mission Control; `market_ui.py`: `print_mission_control()`, `print_investigate_report()`; tests |
| **cli-market-backend** | **No change v0** unless new REST route desired — CLI calls existing endpoints |
| **cli-market-index** | None |

**Release order:** core → world (pin core in `requirements-railway.txt`).

### Dependencies

- Observatory P0 live (`GET /analytics/observatory`)
- Existing CLI auth (`get_token`, tier fetch in `market_ui.fetch_tier`)
- Data-gate labels from `market_stats` (no hardcoded 54k in code paths — use constants)

### API sequence (investigate)

1. `POST /products/search` — limit 20, country filter
2. `POST /products/compare` — same query, stores from search coverage
3. `GET /v1/dispersion?...` or intel inflation endpoint if tier ≥ Starter
4. Compute spread leader/laggard client-side from compare payload
5. Assemble report JSON + render rich

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Latency >15s | Medium | High | Parallel httpx calls; timeout 12s/step |
| Tier/auth confusion | Medium | Med | Reuse `ui.require_tier()` patterns |
| Claim drift vs GTM | Low | High | Only `market_stats` + API fields in copy |
| Scope creep to LLM | High | High | PRD non-goals; reviewer checklist |

### Open questions

- [ ] **Starter vs Pro gate for investigate?** — Owner: PM — Deadline: day 1 — Recommend Starter+ (intel section soft-gated)
- [ ] **Register MCP tool `market_investigate` in v0 or v0.1?** — Owner: Eng — Deadline: day 3 — Recommend v0.1 after CLI validated

## 7. Launch Plan

| Phase | Audience | Gate |
|-------|----------|------|
| Internal | Team + 2 design partners | Shell + investigate works on prod API; tests green |
| Pro beta | 10 Pro users (Slack `#bitácora`) | No P0 bugs; median demo <90s |
| GA silent | All CLI users | Mention in release notes only; no GTM post until Intelligence pilot feedback |

**Rollback:** Feature flag env `MARKET_MISSIONS=0` hides investigate + Mission Control menu (fallback to current shell).

## 8. Sprint breakdown (2 weeks)

### Week 1 — Core mission + CLI command

| Day | Deliverable | Repo |
|-----|-------------|------|
| 1–2 | `market_missions.run_investigate()` + unit tests (mock httpx) | core |
| 2 | PyPI core bump (patch/minor) | core |
| 3–4 | `market investigate QUERY` command + `--json` | world |
| 4–5 | Rich report renderer | world |

### Week 2 — Mission Control + MCP center + hardening

| Day | Deliverable | Repo |
|-----|-------------|------|
| 6–7 | Mission Control shell home + Observatory fetch | world |
| 7 | `market mcp` read-only center | world |
| 8 | Integration test smoke (live gate optional) | world |
| 9 | Intelligence demo script update (`docs/gtm/`) | world |
| 10 | Release world + docs snippet | world |

## 9. Appendix

- Observatory PRD: `docs/prd-observatory-p0.md`
- Pricing gates: `docs/pricing-strategy.md`
- Brand (Bloomberg terminal tone): `docs/BRAND.md`
- Existing CLI: `market_cli.py`, `market_ui.py`
- Tech debt backlog Next: N-1 payments split, N-3 slack/media tests (sprint Now cerrado 2026-06-13: T-174 ✅, T-177 ✅)

## 10. Press release (one paragraph)

CLI Market OS v0 convierte la terminal en un centro de mando para agentes comerciales LATAM: un solo comando `investigate` entrega comparación multi-retailer, spreads y señales de inflación sobre más de 54 mil precios verificados, mientras Mission Control muestra frescura de datos y salud MCP al abrir la sesión — la misma infraestructura que los developers ya usan vía API y MCP, ahora orchestrada para inteligencia de mercado en segundos.

---

## Aprobación P1 — 2026-06-29

**Aprobado para próximo sprint (2 semanas):**
- `market investigate <query>` — misión estructurada con insights ≥3 en <90s
- Mission Control TUI v0 — shell interactivo sobre primitivas existentes
- Depende de: Observatory P0 ✅ Shipped, T-173 core 1.9.35 ✅

**Precondiciones verificadas:**
- `market search`, `market compare`, `market intel *` disponibles
- Observatory MAA activo en producción
- `market shell` existente como base para Mission Control

**Targets sprint:**
- Time-to-insight: <90s en demo path
- Mission adoption: ≥15% Pro/Starter con ≥1 investigate/semana (baseline a medir en sprint)

---

## Cierre v1.0 — 2026-06-29

**Estado real:** Implementado y testeado. Sprint completado antes del cierre de PRD.

**Entregado:**
- `market_core/market_missions.py`: `run_investigate()` — search + compare + intel inflation paralelo, spread insights, recommendations rules-based
- `market investigate QUERY` — comando registrado en `market_cli.py` con tier gate Starter+
- `print_mission_control()` + `print_investigate_report()` en `market_ui.py`
- `market mcp` — MCP center read-only
- Feature flag `MARKET_MISSIONS=0` para disable
- `fetch_observatory_public()` en `market_ui.py` — Observatory probe en shell startup
- **14/14 tests pasando**: `test_cli_investigate.py`, `test_cli_mission_control.py`

**Open questions resueltas en impl:**
- Tier gate: Starter+ (intel section soft-gated si auth falla)
- MCP tool `market_investigate`: diferido a v0.1 (flag en `market_missions.py`)
