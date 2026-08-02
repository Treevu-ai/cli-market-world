# Taller de Inteligencia de Mercados y Optimización de Compras

Material de venta self-serve — no propuesta 1:1 (esa línea sigue en `docs/consultoria/` y `docs/parrilleria/`).

## Archivos

- **`TALLER_INTELIGENCIA_MERCADOS.md`** — guion completo (75-90 min), columna vertebral común + módulo A (compras) + módulo B (pricing/trade)
- **`CHECKLIST_DEMO_TALLER.md`** — checklist pre-sesión, incluye verificación de comandos en vivo antes de cada dictado
- **`PITCH_60SEG_TALLER.md`** — pitch corto para agendar el taller (LinkedIn, email frío, llamada de calificación)

## Audiencia

- **Módulo A** — category/compras managers, negocios con compra recurrente
- **Módulo B** — equipos de pricing/trade marketing de marcas grandes

## CTA

Suscripción self-serve en vivo durante el cierre — no pasa por flujo de propuesta:
- Módulo A → Procure Copilot desde $29/mes
- Módulo B → CLI Build Pro $49/mes

## Historial

`market optimize` devolvía 500 en producción al armar este material (2026-07-11) — encontrado y arreglado el mismo día (cli-market-core 1.11.40: `as_completed()` no atrapaba su propio timeout cuando la resolución de sustitutos vía Open Food Facts tardaba más de lo esperado). Verificado en vivo, ya funciona. `market basket` sigue siendo un respaldo válido si vuelve a fallar.
