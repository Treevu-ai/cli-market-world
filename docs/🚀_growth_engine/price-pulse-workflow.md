# Price Pulse — Multi-Agent Workflow

> Cómo 5 agentes financieros de agency-agents producen un reporte semanal de inteligencia de precios para CLI Market.

## Arquitectura

```
/dashboard/data (JSON, ~200KB)
        │
        ▼
ops/price_pulse_agents.py  ←  coordinator: fetch + slice + dispatch
        │
        ├── 📒 Bookkeeper & Controller   → §5 Calidad + §6 Metodología
        ├── 📊 Financial Analyst         → §1 Resumen + §2 Inflación + §3 Canasta
        ├── 📈 FP&A Analyst              → §7 Forecast 30/60/90d
        ├── 🔬 Investment Researcher    → §8 Macro Context + Competitive Landscape
        └── 🏛️ Tax Strategist           → §9 Transfer Pricing Brief
        │
        ▼
price-pulse-client-YYYY-MM-DD.md → pandoc → PDF
```

## Agentes y sus fuentes

| Agente | Rol md | Contexto CLI Market |
|--------|--------|---------------------|
| Bookkeeper & Controller | `agency-agents/finance/finance-bookkeeper-controller.md` | `docs/agents/contexts/bookkeeper-context.md` |
| Financial Analyst | `agency-agents/finance/finance-financial-analyst.md` | `docs/agents/contexts/financial-analyst-context.md` |
| FP&A Analyst | `agency-agents/finance/finance-fpa-analyst.md` | `docs/agents/contexts/fpa-analyst-context.md` |
| Investment Researcher | `agency-agents/finance/finance-investment-researcher.md` | `docs/agents/contexts/investment-researcher-context.md` |
| Tax Strategist | `agency-agents/finance/finance-tax-strategist.md` | `docs/agents/contexts/tax-strategist-context.md` |

## Flujo de ejecución

### Fase 1 — Validación (paralelo)
Bookkeeper valida quality_funnel + collector + moat_summary. Financial Analyst analiza inflation + canasta_basica.

### Fase 2 — Análisis profundo (paralelo)
FP&A proyecta inflación 30/60/90d. Investment Researcher produce macro context. Tax Strategist analiza spreads para transfer pricing.

### Fase 3 — Ensamblado (secuencial)
Coordinator recibe 5 outputs, inserta en template, genera markdown + PDF.

## Slice de datos por agente

Cada agente recibe solo los campos del dashboard que necesita (no el JSON completo).

| Agente | Campos | ~Tamaño |
|--------|--------|---------|
| Bookkeeper | `kpis`, `quality_funnel`, `moat_summary`, `collector`, `store_health` | 1.5 KB |
| Financial Analyst | `inflation`, `canasta_basica`, `by_line_currency`, `canasta_spreads` | 3 KB |
| FP&A Analyst | `inflation`, `canasta_basica`, `inventory_daily`, `moat_start`, `by_country` | 4 KB |
| Investment Researcher | `by_country`, `line_country_matrix`, `marketing_spreads`, `moat_summary` | 5 KB |
| Tax Strategist | `marketing_spreads`, `by_country`, `by_line_currency` | 3 KB |

## Cómo ejecutar

```bash
python3 ops/price_pulse_agents.py --prepare   # genera prompts
python3 ops/price_pulse_agents.py --assemble  # ensambla reporte
python3 ops/price_pulse_agents.py --run       # todo en uno
```

## Output final

10 secciones en PDF de 10-15 páginas:

1. Resumen Ejecutivo (Financial Analyst)
2. Retail Price Velocity 7d (Financial Analyst)
3. Canasta Básica c/ trazabilidad IPC (Financial Analyst)
4. Dispersión de Precios (Investment Researcher)
5. Calidad del Dato (Bookkeeper)
6. Metodología y Audit Trail (Bookkeeper)
7. Proyección 30/60/90d (FP&A Analyst)
8. Contexto Macro (Investment Researcher)
9. Transfer Pricing Brief (Tax Strategist)
10. Disclaimer y fuentes

## Estado actual (verificado 2026-07-12)

**El flujo es semi-manual, no un pipeline autónomo.** `--prepare` solo genera los 5
archivos de prompt; un humano tiene que pegar cada uno en una herramienta LLM (Claude,
ChatGPT, Claude Code, etc.), guardar la respuesta en
`ops/generated/outputs/output-<agent>.md`, y recién ahí `--assemble` arma el reporte
final. No hay ninguna llamada automática a un LLM dentro de `price_pulse_agents.py`.

El repo externo `agency-agents` (fuente de los 5 `role_file` de finanzas) **no estaba
clonado en esta máquina** — el script apunta a `~/Proyectos/agency-agents/finance/*.md`
de forma hardcodeada (`AGENCY_AGENTS_BASE`), y esa ruta no existía. Se clonó
[`msitarzewski/agency-agents`](https://github.com/msitarzewski/agency-agents) ahí el
2026-07-12 para restaurar el flujo — confirmado que los 5 archivos coinciden exacto con
lo que el script espera. Antes de esto, `--prepare` fallaba con `FileNotFoundError`, y
solo funcionaba con prompts generados previamente (probablemente en otra máquina donde sí
estaba clonado).

Ese mismo repo `agency-agents` trae **11 personas en total** (`docs/agents/contexts/`
tiene un contexto CLI-Market por cada una), pero **solo las 5 de finanzas** listadas
arriba están conectadas a este script. Las otras 6 —`brand-guardian`, `content-creator`,
`sales-engineer`, `ui-designer`, `ux-architect`, `ux-researcher`— ya están conectadas a
un pipeline propio, ver [growth-pulse-workflow.md](growth-pulse-workflow.md)
(`ops/growth_pulse_agents.py`), separado de este porque no comparten fuente de datos ni
producen secciones de un mismo reporte.

Separado de todo esto: `submit_job()` (el `--submit` / `POST /v1/intel/price-pulse`)
NO usa agency-agents — dispara un job server-side que corre sobre
`market_core/market_intel_agent.py` (un único agente conversacional Claude tool-use),
no sobre las 5 personas de finanzas.

## Tiers

| Tier | Secciones | Agentes | Precio |
|------|-----------|---------|--------|
| Pilot S | 1-3, 5-6, 10 | Bookkeeper + Financial Analyst | $300/mes |
| Pilot M | + 4, 7, 8 | + FP&A + Investment Researcher | $400/mes |
| Pilot L | + 9 | + Tax Strategist | $500/mes |
