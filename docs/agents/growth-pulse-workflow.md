# Growth Pulse — Multi-Agent Workflow (Design/Marketing/Sales)

> Cómo las 6 personas de agency-agents que quedaron sin usar (brand-guardian,
> ui-designer, ux-architect, ux-researcher, content-creator, sales-engineer)
> producen entregables reales para CLI Market, sin inventar cifras.

## Por qué es distinto de Price Pulse

[`price_pulse_agents.py`](../../ops/price_pulse_agents.py) corta **un mismo JSON**
financiero en 5 secciones de **un mismo reporte**. Estas 6 personas no comparten
fuente de datos ni destino — cada una produce su propio documento standalone:

| Agente | Fuente de datos real | Destino |
|--------|----------------------|---------|
| Brand Guardian | Copy/estructura viva de `cli-market.dev` | `docs/brand-guidelines.md` |
| UI Designer | Copy/estructura viva de `cli-market.dev` | `docs/ui-component-library.md` |
| UX Architect | Copy/estructura viva de `cli-market.dev` | `docs/design-system.md` |
| UX Researcher | PyPI downloads (`pypistats.org`) + GitHub stars/issues (`gh api`) | `docs/ux-research.md` |
| Content Creator | `/health/stats` (números reales para no inventar claims) | `ops/generated/outputs/content-ideas.md` |
| Sales Engineer | `/health/stats` + flag `moat_stale` (coverage/frescura) | `docs/sales-demo-brief.md` |

## Arquitectura

```
site_snapshot (HTML→texto de cli-market.dev)  ─┐
public_signals (pypistats + gh api)            ├─► ops/growth_pulse_agents.py
live_claims (/health/stats + moat_stale)       ─┘        │
                                                          ▼
                                          role_file (agency-agents) + context_file
                                          (docs/agents/contexts/) + datos reales
                                                          │
                                                          ▼
                                    ops/generated/prompts/prompt-<id>.md
                                                          │
                                       (paso manual: correr en tu LLM de preferencia)
                                                          │
                                                          ▼
                                    ops/generated/outputs/output-<id>.md
                                                          │
                                                          ▼
                                        --assemble copia a su destino real (tabla arriba)
```

Igual que Price Pulse, **es semi-manual**: `--prepare` fetchea las señales reales y
genera los 6 prompts; un humano corre cada uno en un LLM y guarda la respuesta en
`ops/generated/outputs/output-<id>.md`; `--assemble` copia cada output a su destino
real en `docs/`.

## Fuentes de datos (todas públicas, sin auth)

- **Sitio en vivo**: `GET https://cli-market.dev/` → HTML limpiado a texto (script/style
  removidos), primeros 4000 caracteres. Le da a Brand Guardian / UI Designer / UX
  Architect la copy y estructura REAL del sitio para auditar, en vez de asumir.
- **PyPI**: `GET https://pypistats.org/api/packages/cli-market-world/recent` — descargas
  reales `last_day`/`last_week`/`last_month`.
- **GitHub**: `gh api repos/Treevu-ai/cli-market-world` → stars, watchers, issues abiertos.
- **Data-gate**: `GET https://cli-market-api.fly.dev/health/stats` — cobertura 7d, edad
  del moat, estado del collector. Se deriva `moat_stale` (`true` si cobertura < 80% o
  edad > 6h) para que Sales Engineer sepa si puede demostrar compra o debe mostrar el
  data-gate como diferenciador y reprogramar (regla ya definida en su contexto).

Cada fuente se fetchea **una sola vez por corrida** aunque varios agentes la compartan
(cache en memoria por `data_source`) — por ejemplo los 3 agentes de diseño comparten un
solo fetch de `site_snapshot`.

## Cómo ejecutar

```bash
python3 ops/growth_pulse_agents.py --prepare   # genera los 6 prompts con datos reales
python3 ops/growth_pulse_agents.py --report    # ver qué falta (prompt/output/destino)
python3 ops/growth_pulse_agents.py --assemble  # copia cada output a su docs/*.md real
python3 ops/growth_pulse_agents.py --run       # prepare + assemble en un solo paso
```

## Verificado (2026-07-12)

`--prepare` corrido en vivo: generó los 6 prompts (13k–26k caracteres cada uno) contra
las 3 fuentes reales sin errores. El de Sales Engineer trajo `moat_stale: false` con
cobertura 7d real y 40 tiendas indexadas — confirmando que hoy sí se puede demostrar el
flujo de compra completo.

## Dependencia externa

Igual que Price Pulse, los `role_file` de estos 6 agentes viven en el repo externo
[`msitarzewski/agency-agents`](https://github.com/msitarzewski/agency-agents), clonado en
`~/Proyectos/agency-agents` (carpetas `design/`, `marketing/`, `sales/` — no `finance/`).
Ver [price-pulse-workflow.md](price-pulse-workflow.md#estado-actual-verificado-2026-07-12)
para el detalle de esa dependencia.
