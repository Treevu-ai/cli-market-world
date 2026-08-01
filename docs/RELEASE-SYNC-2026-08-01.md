# Sincronización de release — 2026-08-01

## Alcance

Registro conjunto de `cli-market-core`, `cli-market-backend`,
`cli-market-world`, `cli-market-index` y `cli-market-content` tras el
desbloqueo de salud de fuentes en producción.

## Hallazgo y decisión

| Fuente | País | Evidencia | Decisión |
|---|---:|---|---|
| `smartnutrition_pe` | PE | La Store API responde fuera de un datacenter; la IP del colector Fly.io recibe ModSecurity. | Cuarentena temporal en Core 1.12.4. |
| `thegreenkiss_ca` | CA | `products.json` responde fuera de un datacenter; el WAF bloquea la IP del colector Fly.io. | Cuarentena temporal en Core 1.12.4. |
| `simplynaturalcanada_ca` | CA | `products.json` responde fuera de un datacenter; el WAF bloquea la IP del colector Fly.io. | Cuarentena temporal en Core 1.12.4. |

La cuarentena es honesta respecto a cobertura: las fuentes no se ofrecen como
activas mientras el colector no pueda leerlas de manera repetible. No se
modificaron productos, precios, Golden Records ni equivalencias.

## Matriz de sincronización

| Repositorio | Estado | Acción / límite |
|---|---|---|
| `cli-market-core` | Publicado como `1.12.4` | Catálogo: tres fuentes marcadas `disabled` con motivo y prueba de regresión. |
| `cli-market-backend` | Espejo sin deploy directo | Su rango `cli-market-core>=1.12.3` acepta 1.12.4. Revalidar CI después de la propagación de PyPI antes de mergear su PR. |
| `cli-market-world` | Producción Fly.io | Pin exacto `cli-market-core==1.12.4`; despliegue y doctor gate verificados. |
| `cli-market-index` | Sin cambio funcional | No hubo modificación de identidad ni Golden Records; el pin de Index debe permanecer igual entre World y Backend. |
| `cli-market-content` | Sin cambio de copy público | No publicar conteos de cobertura derivados de esta cuarentena; sus claims siguen sujetos al data-gate. |

## Verificación realizada

- Core: prueba de cuarentena y estados de salud de fuente pasan; wheel y sdist
  1.12.4 construidos y publicados.
- World: pruebas Telegram y de fuente relevantes pasan; CI de código,
  PostgreSQL, lint y análisis pasan.
- Fly.io: workflow manual con sanity check, smoke posterior y rollback
  habilitado terminó correctamente.
- Producción: `GET /v1/sources/health?catalog_only=true` devuelve `dead: 0`
  y `total: 320`; `ops/doctor_prod_gate.py` pasa con `314 ok · 0 dead` y
  `golden linkage 68.1%`.

## Condición de reactivación

No retirar `disabled` ni `disabled_reason` por un único HTTP 200. Para cada
fuente se necesita validar una ruta sostenible desde el egress de producción:

1. proxy autorizado o allowlist del retailer;
2. al menos una recolección exitosa desde el entorno objetivo;
3. revisión de datos recolectados e identidad del producto;
4. reactivar en Core, publicar una nueva versión y repetir la secuencia
   `core → backend → world`.

## No hacer

- No elevar `DOCTOR_MAX_DEAD_SOURCES` para ocultar una fuente no disponible.
- No inferir que un endpoint público funcional desde una red residencial lo es
  también desde Fly.io.
- No convertir este ajuste operativo en una promesa comercial o métrica GTM.
