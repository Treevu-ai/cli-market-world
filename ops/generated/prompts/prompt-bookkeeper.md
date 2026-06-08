# Bookkeeper

(Role file not found: C:\Users\acuba\Proyectos\agency-agents\finance\finance-bookkeeper-controller.md)

---

# Bookkeeper & Controller — Contexto CLI Market

> Carga este archivo junto con `agency-agents/finance/finance-bookkeeper-controller.md`.
> Tu tarea: validar la integridad, trazabilidad y calidad de los datos del Price Pulse semanal.

## Tu rol en este reporte

Sos Dana, Controller con 13+ años. Producís las secciones §5 (Calidad del Dato) y §6 (Metodología y Audit Trail). Además, generás un "Controller's Sign-off" que certifica que los números de este reporte son trazables, reconciliables y auditables.

## Contexto del producto

CLI Market es una capa de agregación de precios de góndola para LATAM. Un collector programado consulta APIs públicas de retailers (VTEX, Shopify, Magento) cada 8 horas y acumula precios en una tabla `price_snapshots`. El dashboard (`/dashboard/data`) expone estos datos en JSON.

**Tu cliente** es un equipo de fintech, consultora o CPG que paga USD 300–500/mes por este reporte. Esperan que los números sean defendibles bajo escrutinio. Si hay un error en los datos y no lo detectás, el cliente lo detectará.

## Datos que recibís

El script `price_pulse_agents.py` te pasa estos campos del dashboard:

```json
{
  "kpis": { ... },
  "quality_funnel": { ... },
  "moat_summary": { ... },
  "collector": { ... },
  "store_health": [ ... ]
}
```

## Lo que tenés que producir

### §5 Calidad del Dato

Formato markdown. Incluí:

1. **Resumen del funnel**: captured → flagged discounts → flagged outliers → citable. Explicá cada etapa en una frase.
2. **Tabla de calidad**:
   - Capturados (total_indexed)
   - Flagged por descuento >90% (con explicación de por qué >90% es sospechoso)
   - Flagged por outlier 5x (con explicación de la metodología de mediana)
   - Citables (marketing-ready, los que pasaron todos los filtros)
3. **Health del collector**: estado, antigüedad del último snapshot, tiendas fresh 24h, cobertura 7d.
4. **Juicio del Controller**: una frase que declare si los datos de esta semana son "aptos para uso en decisiones" o "requieren verificación adicional". Si coverage_7d < 80% o moat_age > 24h, es "requiere verificación".

### §6 Metodología y Audit Trail

1. **Cadena de custodia**: fuente → collector → DB → dashboard → reporte. Cada eslabón con timestamp.
2. **Query fuente**: `GET /dashboard/data` ejecutado el [fecha]. Hash SHA256 del JSON usado.
3. **Criterios de inclusión/exclusión**: qué precios entran (price>0, price<999999), cuáles se excluyen.
4. **Limitaciones**: retail formal urbano, no IPC nacional, no incluye mercados informales.

### Controller's Sign-off

Un bloque al final de §5:

```
✅ CONTROLLER'S SIGN-OFF
Yo, Dana [Bookkeeper & Controller], certifico que:
- Los datos de este reporte fueron extraídos de /dashboard/data el [fecha] a las [hora] UTC.
- El funnel de calidad fue aplicado con los criterios documentados en §6.
- Los números son trazables a queries reproducibles.
- [ coverage_7d >= 80 and moat_age < 24 → "Los datos son aptos para uso en decisiones comerciales." ]
- [ otherwise → "ADVERTENCIA: Los datos requieren verificación adicional. Coverage 7d: X%. Moat age: Y horas." ]
```

## Reglas

- No inventes números. Si un campo no está en el JSON, escribí "—".
- Si el collector está stale (>24h), señalalo explícitamente.
- No uses "store_success_pct lifetime" — esa métrica tiene sesgo histórico.
- Todo número debe poder trazarse a un campo del JSON de entrada.


---

## 📊 Datos del dashboard

```json
{
  "generated_at": "2026-06-08T18:19:39.003220+00:00",
  "kpis": {
    "total_indexed": 50673,
    "unique_products": 50931,
    "stores_indexed": 38,
    "total_snapshots": 39291,
    "snapshots_24h": 39291,
    "active_stores": 38,
    "active_stores_24h": 38,
    "total_stores": 38,
    "catalog_stores": 68,
    "healthy_stores": 19,
    "store_success_pct": 50.0,
    "health_breakdown": {
      "ok": 19,
      "partial": 19,
      "dead": 0,
      "stale": 0
    },
    "stores_dead": 0,
    "stores_stale": 0,
    "coverage_7d_pct": 100.0,
    "stores_fresh_24h": 38,
    "fresh_24h_pct": 100.0,
    "total_runs": 347,
    "stores_24h": 38,
    "last_collected_at": "2026-06-08 18:17:41.227727+00:00",
    "moat_age_hours": 0.0
  },
  "quality_funnel": {
    "captured": 50673,
    "flagged": 7348,
    "flagged_discounts": 3559,
    "flagged_outliers": 3789,
    "clean": 43325,
    "citable": 4,
    "filters": [
      "discount>=90%",
      "spread>10x",
      "median_outlier_5x"
    ],
    "non_normalizable_names": 23370,
    "confidence_dist": {
      "suspect": 3307,
      "ok": 47624
    }
  },
  "moat_summary": {
    "purpose": "Verified cross-retailer prices for agent compare, basket, and inflation signals.",
    "refresh_hours": 4,
    "total_indexed": 50673,
    "unique_products": 50931,
    "stores_indexed": 38,
    "snapshots_24h": 39291,
    "last_collected_at": "2026-06-08 18:17:41.227727+00:00",
    "moat_age_hours": 0.0,
    "collector_stale": false,
    "stores_active_catalog": 38,
    "stores_fresh_24h": 38,
    "stores_active_7d": 38,
    "coverage_7d_pct": 100.0,
    "fresh_24h_pct": 100.0,
    "marketing_gate_pct": 80,
    "marketing_gate_pass": true,
    "stale_stores": [],
    "health_breakdown": {
      "ok": 19,
      "partial": 19,
      "dead": 0,
      "stale": 0
    },
    "agent_surfaces": [
      "market compare",
      "market basket",
      "market intel indicators",
      "market intel scores",
      "market intel enrichment",
      "market intel inflation",
      "/v1/intel/inflation",
      "/v1/intel/scores",
      "/v1/intel/enrichment",
      "/v1/intel/enrichment/subcategories",
      "/analytics/indicators",
      "MCP market_stats"
    ]
  },
  "collector": {
    "status": "ok",
    "age_hours": 0.9,
    "interval_hours": 8,
    "last_run": "2026-06-08T17:25:48.932581+00:00",
    "last_finished": "2026-06-08T17:26:01.768793+00:00",
    "stores_succeeded": 34,
    "prices_collected": 1593,
    "last_prices_collected": 1593
  },
  "store_health": [
    {
      "store": "nunaorganica_pe",
      "total_requests": 52,
      "total_successes": 30,
      "success_pct": 57.7,
      "consecutive_failures": 5,
      "last_success": "2026-06-08 11:13:28.509522+00",
      "last_error": "2026-06-08 17:25:58.615802+00",
      "coverage_7d_pct": 100.0
    },
    {
      "store": "promart",
      "total_requests": 36675,
      "total_successes": 21407,
      "success_pct": 58.4,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:57.873715+00",
      "last_error": "2026-06-06 04:14:47.771206+00",
      "coverage_7d_pct": 65.4
    },
    {
      "store": "globo_br",
      "total_requests": 153,
      "total_successes": 92,
      "success_pct": 60.1,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:57.514395+00",
      "last_error": "2026-06-08 12:50:01.462099+00",
      "coverage_7d_pct": 94.7
    },
    {
      "store": "oster_br",
      "total_requests": 155,
      "total_successes": 94,
      "success_pct": 60.6,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:56.988957+00",
      "last_error": "2026-06-06 20:00:44.951114+00",
      "coverage_7d_pct": 98.0
    },
    {
      "store": "farmatodo_mx",
      "total_requests": 22001,
      "total_successes": 14495,
      "success_pct": 65.9,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:56.118014+00",
      "last_error": "2026-06-07 16:11:17.050027+00",
      "coverage_7d_pct": 90.9
    },
    {
      "store": "carulla",
      "total_requests": 38426,
      "total_successes": 25764,
      "success_pct": 67.0,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:26:01.754353+00",
      "last_error": "2026-06-01 00:58:35.049904+00",
      "coverage_7d_pct": 86.8
    },
    {
      "store": "exito",
      "total_requests": 38212,
      "total_successes": 25739,
      "success_pct": 67.4,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:26:01.303812+00",
      "last_error": "2026-06-01 00:58:35.606173+00",
      "coverage_7d_pct": 90.4
    },
    {
      "store": "pacheco_br",
      "total_requests": 21441,
      "total_successes": 14510,
      "success_pct": 67.7,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:53.630645+00",
      "last_error": "2026-06-08 12:50:02.761597+00",
      "coverage_7d_pct": 84.4
    },
    {
      "store": "jumbo_ar",
      "total_requests": 45919,
      "total_successes": 33325,
      "success_pct": 72.6,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:58.186023+00",
      "last_error": "2026-06-07 19:14:02.560176+00",
      "coverage_7d_pct": 75.6
    },
    {
      "store": "vea_ar",
      "total_requests": 45784,
      "total_successes": 33334,
      "success_pct": 72.8,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:58.128336+00",
      "last_error": "2026-06-07 19:14:02.586148+00",
      "coverage_7d_pct": 76.3
    },
    {
      "store": "chedraui",
      "total_requests": 44942,
      "total_successes": 33312,
      "success_pct": 74.1,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:58.212632+00",
      "last_error": "2026-05-31 23:30:13.65775+00",
      "coverage_7d_pct": 80.8
    },
    {
      "store": "easy_ar",
      "total_requests": 30559,
      "total_successes": 22661,
      "success_pct": 74.2,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:56.525739+00",
      "last_error": "2026-06-01 00:58:32.119596+00",
      "coverage_7d_pct": 85.3
    },
    {
      "store": "heb_mx",
      "total_requests": 44756,
      "total_successes": 33275,
      "success_pct": 74.3,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:59.152882+00",
      "last_error": "2026-05-31 23:30:15.994178+00",
      "coverage_7d_pct": 80.4
    },
    {
      "store": "plazavea",
      "total_requests": 43873,
      "total_successes": 32620,
      "success_pct": 74.4,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:58.92062+00",
      "last_error": "2026-06-07 16:11:17.488753+00",
      "coverage_7d_pct": 80.8
    },
    {
      "store": "carrefour",
      "total_requests": 44368,
      "total_successes": 33298,
      "success_pct": 75.0,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:58.40222+00",
      "last_error": "2026-06-07 19:14:02.266559+00",
      "coverage_7d_pct": 80.5
    },
    {
      "store": "aramis_br",
      "total_requests": 152,
      "total_successes": 116,
      "success_pct": 76.3,
      "consecutive_failures": 1,
      "last_success": "2026-06-08 15:54:39.708302+00",
      "last_error": "2026-06-08 17:25:52.244445+00",
      "coverage_7d_pct": 88.4
    },
    {
      "store": "carrefour_br",
      "total_requests": 43113,
      "total_successes": 33230,
      "success_pct": 77.1,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:26:00.88092+00",
      "last_error": "2026-06-01 02:11:31.389867+00",
      "coverage_7d_pct": 46.8
    },
    {
      "store": "wong",
      "total_requests": 42238,
      "total_successes": 32711,
      "success_pct": 77.4,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:58.86636+00",
      "last_error": "2026-06-07 19:14:02.653782+00",
      "coverage_7d_pct": 84.9
    },
    {
      "store": "metro",
      "total_requests": 42295,
      "total_successes": 32777,
      "success_pct": 77.5,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:58.148505+00",
      "last_error": "2026-06-07 19:14:02.630167+00",
      "coverage_7d_pct": 87.3
    },
    {
      "store": "xray_pe",
      "total_requests": 55,
      "total_successes": 44,
      "success_pct": 80.0,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:53.302445+00",
      "last_error": "2026-06-06 18:42:25.135831+00",
      "coverage_7d_pct": 100.0
    },
    {
      "store": "cea_br",
      "total_requests": 30612,
      "total_successes": 25430,
      "success_pct": 83.1,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:53.25692+00",
      "last_error": "2026-06-08 14:22:39.573875+00",
      "coverage_7d_pct": 83.0
    },
    {
      "store": "olimpica",
      "total_requests": 39293,
      "total_successes": 32686,
      "success_pct": 83.2,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:58.82699+00",
      "last_error": "2026-06-07 10:06:12.222759+00",
      "coverage_7d_pct": 85.9
    },
    {
      "store": "mambo_br",
      "total_requests": 39786,
      "total_successes": 33256,
      "success_pct": 83.6,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:52.207351+00",
      "last_error": "2026-06-08 14:22:32.997015+00",
      "coverage_7d_pct": 83.7
    },
    {
      "store": "miess_br",
      "total_requests": 145,
      "total_successes": 124,
      "success_pct": 85.5,
      "consecutive_failures": 1,
      "last_success": "2026-06-08 15:54:41.70746+00",
      "last_error": "2026-06-08 17:25:54.599074+00",
      "coverage_7d_pct": 85.2
    },
    {
      "store": "sams_club_br",
      "total_requests": 38689,
      "total_successes": 33231,
      "success_pct": 85.9,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:53.543011+00",
      "last_error": "2026-06-07 19:14:02.560603+00",
      "coverage_7d_pct": 84.3
    },
    {
      "store": "electrolux_ar",
      "total_requests": 41156,
      "total_successes": 36411,
      "success_pct": 88.5,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:57.804064+00",
      "last_error": "2026-06-06 20:00:44.976838+00",
      "coverage_7d_pct": 99.0
    },
    {
      "store": "hering_br",
      "total_requests": 28169,
      "total_successes": 25221,
      "success_pct": 89.5,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:52.420156+00",
      "last_error": "2026-06-08 12:50:04.38389+00",
      "coverage_7d_pct": 82.6
    },
    {
      "store": "decathlon_br",
      "total_requests": 145,
      "total_successes": 130,
      "success_pct": 89.7,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:52.34413+00",
      "last_error": "2026-06-08 14:22:32.862773+00",
      "coverage_7d_pct": 92.0
    },
    {
      "store": "motorola_br",
      "total_requests": 44928,
      "total_successes": 40495,
      "success_pct": 90.1,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:53.720347+00",
      "last_error": "2026-06-08 14:22:33.06715+00",
      "coverage_7d_pct": 99.1
    },
    {
      "store": "coppel_ar",
      "total_requests": 11322,
      "total_successes": 10709,
      "success_pct": 94.6,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:58.253684+00",
      "last_error": "2026-06-05 05:14:06.747597+00",
      "coverage_7d_pct": 86.6
    },
    {
      "store": "whirlpool_it",
      "total_requests": 41149,
      "total_successes": 39066,
      "success_pct": 94.9,
      "consecutive_failures": 1,
      "last_success": "2026-06-08 15:54:39.309527+00",
      "last_error": "2026-06-08 17:25:51.580289+00",
      "coverage_7d_pct": 93.6
    },
    {
      "store": "electrolux_cl",
      "total_requests": 41397,
      "total_successes": 39896,
      "success_pct": 96.4,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:57.345478+00",
      "last_error": "2026-06-06 20:00:44.708133+00",
      "coverage_7d_pct": 99.7
    },
    {
      "store": "rihappy_br",
      "total_requests": 140,
      "total_successes": 135,
      "success_pct": 96.4,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:55.590676+00",
      "last_error": "2026-06-07 11:37:26.87461+00",
      "coverage_7d_pct": 91.0
    },
    {
      "store": "motorola_mx",
      "total_requests": 41166,
      "total_successes": 40166,
      "success_pct": 97.6,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:52.263893+00",
      "last_error": "2026-06-08 14:22:33.078232+00",
      "coverage_7d_pct": 100.0
    },
    {
      "store": "motorola_ar",
      "total_requests": 41378,
      "total_successes": 40404,
      "success_pct": 97.6,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:52.9275+00",
      "last_error": "2026-06-08 14:22:33.51865+00",
      "coverage_7d_pct": 99.4
    },
    {
      "store": "whirlpool_fr",
      "total_requests": 39307,
      "total_successes": 38604,
      "success_pct": 98.2,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:57.698675+00",
      "last_error": "2026-06-06 20:00:44.964161+00",
      "coverage_7d_pct": 100.0
    },
    {
      "store": "whirlpool_ar",
      "total_requests": 40957,
      "total_successes": 40213,
      "success_pct": 98.2,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:57.277202+00",
      "last_error": "2026-06-06 20:00:44.70761+00",
      "coverage_7d_pct": 99.7
    },
    {
      "store": "motorola_cl",
      "total_requests": 39872,
      "total_successes": 39175,
      "success_pct": 98.3,
      "consecutive_failures": 0,
      "last_success": "2026-06-08 17:25:53.046134+00",
      "last_error": "2026-06-08 14:22:34.12027+00",
      "coverage_7d_pct": 100.0
    }
  ]
}
```

---

## ✏️ Instrucción

Producí tu sección del reporte Price Pulse CLI Market (§5 Calidad del Dato + §6 Metodología y Audit Trail).
Formato: markdown. Solo tu sección, no el reporte completo.
Incluí tus conclusiones en el formato especificado en tu contexto.