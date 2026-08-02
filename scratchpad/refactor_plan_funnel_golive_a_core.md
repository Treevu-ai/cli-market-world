# Plan de Refactor: extraer `market_funnel` / `market_golive` a `cli-market-core`

**Objetivo:** eliminar la duplicación real de lógica entre `cli-market-backend` y
`cli-market-world`, siguiendo el patrón que ya usaste para Observatory (`market_observatory.py`
ya vive en `cli-market-core/market_core/` — funcionó, es el precedente a copiar) y que tu propio
doc (`docs/prd-observatory-p0.md` §0.2) ya prescribe: *"Lógica reutilizable → extraer a core;
world y backend solo importan."*

**No toco código todavía** — esto es la propuesta para que la confirmes antes de ejecutar
cualquier paso, como corresponde a un refactor multi-repo.

---

## 0. Qué confirmó la investigación

- `cli-market-observatory.py` **ya está migrado** a `cli-market-core/market_core/market_observatory.py`
  — es la prueba de que este patrón ya se hizo una vez y funciona.
- Lo que sigue duplicado y diverge activamente: `market_funnel.py` y `market_golive.py`.
  Backend (`cli-market-backend`, prod) va un commit adelante de world — tiene `dropoff_summary`,
  `mcp_analytics`, `include_test` param que world todavía no tiene. Esa es la fuente de verdad.
- **`market_adoption_index.py` NO se toca** — tu propio doc (0.4) ya lo marca como
  "world canónico" a propósito (corre en world, lee la DB de prod remota). No es duplicación, es
  diseño intencional. Sacarlo de este refactor.
- Blast radius real por repo — no son solo los 2 routers, son ~10 archivos que importan
  `record_funnel_event` / `FUNNEL_EVENTS` para instrumentar eventos (search, retailers,
  mercadopago, billing/activation, slack_ops, mcp_http, auth):

  **Backend:** `market_adoption.py`, `market_adoption_index.py`, `market_server.py`,
  `ops/billing_slack.py`, `ops/command_control_daily.py`, `ops/grant_pro_by_api_key.py`,
  `pre_checkout_validate.py`, `routers/admin.py`, `routers/auth.py`, `routers/funnel.py`,
  `routers/mcp_http.py`, `routers/mercadopago.py`, `routers/payments.py`,
  `routers/retailers.py`, `routers/search.py`, `tests/test_funnel.py`

  **World:** `audit_funnel.py`, `market_adoption.py`, `market_adoption_index.py`,
  `market_cli.py`, `market_server.py`, `ops/activate_pro.py`, `ops/billing_slack.py`,
  `ops/command_control_daily.py`, `ops/daily_briefing.py`, `ops/go_live_check.py`,
  `pre_checkout_validate.py`, `routers/auth.py`, `routers/billing/activation.py`,
  `routers/billing/routes.py`, `routers/funnel.py`, `routers/mcp_http.py`,
  `routers/public_demo.py`, `routers/retailers.py`, `routers/search.py`,
  `routers/slack_ops.py`, `tests/test_activation_summary.py`, `tests/test_adoption_recent.py`,
  `tests/test_billing_slack.py`, `tests/test_funnel.py`, `tests/test_golive.py`,
  `tests/test_paypal_reconcile.py`

  → La mitigación de riesgo: **no cambiamos las firmas de las funciones**, solo el path de
  import (`from market_funnel import X` → `from market_core.market_funnel import X`). Si las
  firmas quedan idénticas, estos ~30 archivos no necesitan tocarse en su lógica, solo el import.

---

## 1. Estrategia — shim de compatibilidad, no big-bang

Para no romper 30 archivos de golpe en dos repos, cada módulo duplicado se reemplaza por un
**shim de re-export** durante la transición, en vez de borrar y salir a cazar imports:

```python
# cli-market-backend/market_funnel.py (después del refactor)
"""Shim de compatibilidad — la lógica real vive en cli-market-core.
Eliminar este archivo una vez confirmado que ningún import directo quedó pendiente (fase 5)."""
from market_core.market_funnel import *  # noqa: F401,F403
from market_core.market_funnel import FUNNEL_EVENTS, record_funnel_event, funnel_summary  # noqa: F401
```

Esto significa que los ~30 archivos que hacen `from market_funnel import record_funnel_event`
**siguen funcionando sin cambios** durante la migración. Solo tocamos explícitamente
`routers/funnel.py` y `routers/dashboard.py` (los que definen los endpoints), y limpiamos el
shim en la fase final cuando ya no quede riesgo.

---

## 2. Orden de ejecución (respeta tu propia regla de versionado, §0.3)

```
Fase 1: cli-market-core     → PR + tag + publish PyPI
Fase 2: cli-market-backend  → bump requirements.txt → PR + deploy prod
Fase 3: cli-market-world    → bump pyproject.toml → PR + tag PyPI
Fase 4: verificación cruzada (mirror_diff_gate + tests + canary)
Fase 5: cleanup (borrar shims, actualizar docs)
```

### Fase 1 — `cli-market-core`

1. Crear `market_core/market_funnel.py`, sembrado desde la versión de **backend** (es la más
   completa/actual: tiene `dropoff_summary`, `mcp_analytics`, `include_test`).
2. Crear `market_core/market_golive.py`, igual sembrado desde backend.
3. Ambos módulos dependen de `get_db()` — verificar que usan la misma convención de acceso a
   DB que ya usa `market_core/market_observatory.py` (probablemente `DATABASE_URL` inyectado,
   no una conexión hardcodeada — revisar antes de copiar tal cual).
4. Portar los tests relevantes de `cli-market-backend/tests/test_funnel.py` a
   `cli-market-core/tests/` (adaptando imports).
5. Bump `pyproject.toml` version + `market_core/market_stats.py` `PACKAGE_VERSION` (mismo
   patrón que ya documentaste para Observatory en 0.3).
6. PR → merge → tag → publish a PyPI (`cli-market-core` nueva versión, ej. `1.11.23`).

### Fase 2 — `cli-market-backend` (prod primero, por regla del repo)

1. Bump `requirements.txt`: `cli-market-core>=1.11.23`.
2. Reemplazar `market_funnel.py` y `market_golive.py` por los shims de re-export (sección 1).
3. Actualizar `routers/funnel.py` y `routers/dashboard.py` (donde viven los endpoints
   `/dashboard/go-live`, `/dashboard/funnel`, etc.) para importar directo de
   `market_core.market_funnel` / `market_core.market_golive` en vez de pasar por el shim
   (más limpio, y valida que el import directo funciona).
4. Correr `tests/test_funnel.py` completo — debe pasar sin cambios en la lógica de test.
5. PR → merge → deploy a Railway/Fly.
6. **Canary de 24-48h**: monitorear `/dashboard/go-live`, `/analytics/funnel`,
   `/dashboard/funnel` en prod — confirmar que los números no cambiaron vs. antes del deploy
   (mismo input, mismo output esperado, ya que la lógica no cambió, solo el path de import).

### Fase 3 — `cli-market-world`

1. Bump `pyproject.toml`: `cli-market-core>=1.11.23`.
2. Mismo reemplazo: `market_funnel.py` / `market_golive.py` → shims; `routers/funnel.py` /
   `routers/dashboard.py` → import directo de core.
3. Correr `tests/test_funnel.py`, `tests/test_golive.py`, `tests/test_activation_summary.py`,
   `tests/test_adoption_recent.py`, `tests/test_billing_slack.py`, `tests/test_paypal_reconcile.py`
   — son los que tocan esta área, todos deben seguir pasando.
4. PR → merge → tag `v*` → publish PyPI (`cli-market-world` nueva versión).

### Fase 4 — Verificación cruzada

1. Correr `ops/mirror_diff_gate.py` contra ambos repos — debería pasar trivialmente ahora,
   porque ambos importan la misma función de `core` en vez de mantener copias que puedan
   divergir. Si el gate ya no encuentra nada que comparar (porque ya no hay lógica duplicada,
   solo el shim), es la señal de que el refactor cumplió su objetivo.
2. Diff manual rápido: confirmar que `/dashboard/go-live?days=7` devuelve el mismo shape/valores
   en backend antes/después del deploy (ya lo probaste manualmente con el GPT interno — sirve
   como smoke test real).

### Fase 5 — Cleanup (solo después de 1-2 semanas estables en prod)

1. Buscar imports directos de `market_funnel`/`market_golive` que aún no se movieron a
   `market_core.*` en los ~30 archivos listados en la sección 0 — migrarlos uno a uno
   (mecánico: cambiar el path de import, sin tocar lógica).
2. Una vez que ningún archivo importe desde el shim, **borrar** `market_funnel.py` /
   `market_golive.py` de ambos repos (ya no son más que el shim vacío).
3. Actualizar `docs/prd-observatory-p0.md` §0.2 para reflejar que `market_funnel` /
   `market_golive` ya no son "archivos que deben mantenerse sincronizados" — ahora son
   "importados desde core", moviendo la tabla de la sección 0.2 a la sección 0.4
   ("Dónde vive cada capa").
4. Evaluar si `ops/mirror_diff_gate.py` todavía necesita reglas para funnel/golive, o si se
   puede reducir su alcance ahora que esa lógica ya no puede divergir por definición.

---

## 3. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| DB access pattern distinto entre core y los repos (core no tiene conexión directa a Postgres de prod hoy) | Verificar en Fase 1 cómo `market_observatory.py` en core resuelve esto (ya lo hizo) y replicar el mismo patrón — probablemente inyección de conexión, no hardcoded |
| Algún archivo de los ~30 importa un símbolo interno no exportado por el shim (`import *` no siempre cubre todo) | El shim explícito re-exporta los símbolos conocidos (`FUNNEL_EVENTS`, `record_funnel_event`, `funnel_summary`); correr `pytest` completo en ambos repos ANTES de mergear detecta cualquier símbolo faltante como `ImportError` |
| Romper telemetría de prod en el canary | Backend se despliega primero y se monitorea 24-48h antes de tocar world — si algo falla, rollback es solo bajar el pin de `cli-market-core` en `requirements.txt` (no revertir código) |
| `market_adoption_index.py` se confunde con parte del refactor | Explícitamente fuera de alcance — ya se resolvió en la sección 0 |

---

## 4. Qué NO cambia

- Los endpoints (`GET /dashboard/go-live`, `GET /dashboard/funnel`, etc.) siguen viviendo en
  `routers/` de cada repo — eso es correcto, cada repo corre su propio servidor.
- El comportamiento observable (valores devueltos por los endpoints) no cambia — es un refactor
  de organización de código, no de lógica de negocio.
- `market_adoption_index.py` sigue solo en world.

---

## 5. Checklist para arrancar (cuando confirmes)

- [ ] Confirmar que quieres empezar por Fase 1 (`cli-market-core`)
- [ ] Confirmar acceso/permisos de push a los 3 repos (`cli-market-core`, `cli-market-backend`, `cli-market-world`)
- [ ] Decidir si el PR de cada fase lo reviso yo con `code-reviewer` antes de que lo mergees (recomendado, por la regla global de tu CLAUDE.md de invocar code-reviewer en cualquier cambio)
