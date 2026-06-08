# Fpa Analyst

(Role file not found: C:\Users\acuba\Proyectos\agency-agents\finance\finance-fpa-analyst.md)

---

# FP&A Analyst — Contexto CLI Market

> Carga este archivo junto con `agency-agents/finance/finance-fpa-analyst.md`.
> Tu tarea: proyectar la inflación de canasta a 30, 60 y 90 días usando la serie histórica del collector como leading indicator.

## Tu rol en este reporte

Sos el FP&A Analyst. Producís la sección §7 (Proyección y Escenarios). Esta sección es **premium** — solo aparece en los tiers Pilot M ($400/mes) y Pilot L ($500/mes).

Tu valor: convertís una serie histórica de precios en un forecast con bandas de confianza que un gerente de pricing o un analista de crédito puede usar para planificar.

## Contexto del producto

CLI Market tiene una serie histórica de precios de góndola (tabla `price_snapshots`, columna `queried_at`). El dashboard expone `inventory_daily` (snapshots por día, últimos 90 días) y `moat_start` (fecha del primer snapshot). Con estos datos podés construir una proyección.

**Limitación real**: si el moat tiene menos de 30 días de datos, no podés proyectar a 90 días con confianza. En ese caso, producí un forecast "preliminar" con bandas anchas y la nota de que se ajustará conforme se acumulen datos.

## Datos que recibís

El script `price_pulse_agents.py` te pasa:

```json
{
  "inflation": [ ... ],
  "canasta_basica": [ ... ],
  "inventory_daily": [ ... ],
  "moat_start": "2026-05-28T...",
  "by_country": [ ... ]
}
```

## Lo que tenés que producir

### §7 Proyección de Canasta e Inflación

Estructura:

1. **Estado de la serie**
   - Días de datos disponibles: (today - moat_start)
   - Promedio diario de snapshots: (avg_daily_snapshots_7d)
   - Suficiencia: "Serie suficiente para proyección" (>30 días) o "Serie preliminar — proyección con bandas anchas" (<30 días)

2. **Proyección de canasta (escenarios)**
   - Tabla con 3 escenarios (optimista, base, pesimista) para la canasta en la tienda más barata del país principal.
   - Cada escenario a 30, 60, 90 días.
   - Metodología: "Proyección lineal simple sobre el promedio móvil de 7 días de la inflación observada por el collector."
   - Bandas de confianza: ±X% (más anchas si la serie es corta).

   ```
   | Escenario | 30 días | 60 días | 90 días |
   |-----------|---------|---------|---------|
   | Optimista | S/ XX   | S/ XX   | S/ XX   |
   | Base      | S/ XX   | S/ XX   | S/ XX   |
   | Pesimista | S/ XX   | S/ XX   | S/ XX   |
   ```

3. **Proyección de inflación por línea**
   - Para las 3 líneas con más datos: proyectar delta_pct a 30/60/90d.
   - Usar el promedio de inflación de los últimos 7 días como tasa base.
   - Escenario optimista: 50% de la tasa base. Pesimista: 150% de la tasa base.

4. **Factores de riesgo**
   - Listar 3-5 factores que podrían desviar la proyección (estacionalidad, tipo de cambio, política monetaria, shocks de oferta).
   - Esto muestra que entendés los límites del modelo.

5. **Disclaimer**
   - "Proyección basada exclusivamente en datos del collector CLI Market. No incorpora variables macroeconómicas externas. No constituye asesoría financiera."

## Reglas

- Si la serie tiene <7 días, no proyectes — decí "datos insuficientes para proyección" y explicá cuándo estarán disponibles.
- Si la serie tiene 7-30 días, proyectá solo a 30 días con la nota "preliminar — se ajustará semanalmente".
- No uses inflación oficial (INEI, INDEC) como input de tu modelo. Solo datos del collector.
- Redondeá a 2 decimales. Montos en moneda local.


---

## 📊 Datos del dashboard

```json
{
  "generated_at": "2026-06-08T18:19:39.003220+00:00",
  "inflation": [
    {
      "line": "Automotriz · PEN",
      "line_key": "automotriz",
      "currency": "PEN",
      "avg_now": 5799.21,
      "avg_before": 0.0,
      "delta_pct": 0,
      "avg_now_usd": 1567.3541,
      "avg_before_usd": null
    },
    {
      "line": "Tiendas Departamentales · ARS",
      "line_key": "departamentales",
      "currency": "ARS",
      "avg_now": 137392.34,
      "avg_before": 189580.28,
      "delta_pct": -27.5,
      "avg_now_usd": 100.2593,
      "avg_before_usd": 138.3424
    },
    {
      "line": "Tiendas Departamentales · BRL",
      "line_key": "departamentales",
      "currency": "BRL",
      "avg_now": 236.14,
      "avg_before": 249.01,
      "delta_pct": -5.2,
      "avg_now_usd": 65.0981,
      "avg_before_usd": 68.646
    },
    {
      "line": "Electro y Tecnología · ARS",
      "line_key": "electro",
      "currency": "ARS",
      "avg_now": 194724.2,
      "avg_before": 60993.0,
      "delta_pct": 219.3,
      "avg_now_usd": 142.096,
      "avg_before_usd": 44.5084
    },
    {
      "line": "Electro y Tecnología · BRL",
      "line_key": "electro",
      "currency": "BRL",
      "avg_now": 1077.7,
      "avg_before": 547.84,
      "delta_pct": 96.7,
      "avg_now_usd": 297.0957,
      "avg_before_usd": 151.0262
    },
    {
      "line": "Electro y Tecnología · CLP",
      "line_key": "electro",
      "currency": "CLP",
      "avg_now": 121698.6,
      "avg_before": 479990.0,
      "delta_pct": -74.6,
      "avg_now_usd": 174.325,
      "avg_before_usd": 687.5532
    },
    {
      "line": "Electro y Tecnología · EUR",
      "line_key": "electro",
      "currency": "EUR",
      "avg_now": 572.74,
      "avg_before": 146.37,
      "delta_pct": 291.3,
      "avg_now_usd": 626.9181,
      "avg_before_usd": 160.2158
    },
    {
      "line": "Electro y Tecnología · MXN",
      "line_key": "electro",
      "currency": "MXN",
      "avg_now": 6354.11,
      "avg_before": 0.0,
      "delta_pct": 0,
      "avg_now_usd": 498.0248,
      "avg_before_usd": null
    },
    {
      "line": "Farmacias y Salud · BRL",
      "line_key": "farmacias",
      "currency": "BRL",
      "avg_now": 70.95,
      "avg_before": 68.38,
      "delta_pct": 3.8,
      "avg_now_usd": 19.5592,
      "avg_before_usd": 18.8507
    },
    {
      "line": "Farmacias y Salud · MXN",
      "line_key": "farmacias",
      "currency": "MXN",
      "avg_now": 555.85,
      "avg_before": 461.02,
      "delta_pct": 20.6,
      "avg_now_usd": 43.5666,
      "avg_before_usd": 36.134
    },
    {
      "line": "Hogar y Construcción · ARS",
      "line_key": "hogar",
      "currency": "ARS",
      "avg_now": 97767.46,
      "avg_before": 114322.61,
      "delta_pct": -14.5,
      "avg_now_usd": 71.3438,
      "avg_before_usd": 83.4246
    },
    {
      "line": "Hogar y Construcción · PEN",
      "line_key": "hogar",
      "currency": "PEN",
      "avg_now": 272.72,
      "avg_before": 463.12,
      "delta_pct": -41.1,
      "avg_now_usd": 73.7081,
      "avg_before_usd": 125.1676
    },
    {
      "line": "Moda y Vestimenta · BRL",
      "line_key": "moda",
      "currency": "BRL",
      "avg_now": 193.28,
      "avg_before": 160.62,
      "delta_pct": 20.3,
      "avg_now_usd": 53.2826,
      "avg_before_usd": 44.279
    },
    {
      "line": "Supermercados · ARS",
      "line_key": "supermercados",
      "currency": "ARS",
      "avg_now": 6559.52,
      "avg_before": 5491.27,
      "delta_pct": 19.5,
      "avg_now_usd": 4.7867,
      "avg_before_usd": 4.0071
    },
    {
      "line": "Supermercados · BRL",
      "line_key": "supermercados",
      "currency": "BRL",
      "avg_now": 85.55,
      "avg_before": 195.13,
      "delta_pct": -56.2,
      "avg_now_usd": 23.5841,
      "avg_before_usd": 53.7926
    },
    {
      "line": "Supermercados · COP",
      "line_key": "supermercados",
      "currency": "COP",
      "avg_now": 29867.04,
      "avg_before": 30980.66,
      "delta_pct": -3.6,
      "avg_now_usd": 10.4938,
      "avg_before_usd": 10.8851
    },
    {
      "line": "Supermercados · MXN",
      "line_key": "supermercados",
      "currency": "MXN",
      "avg_now": 139.23,
      "avg_before": 463.39,
      "delta_pct": -70.0,
      "avg_now_usd": 10.9126,
      "avg_before_usd": 36.3198
    },
    {
      "line": "Supermercados · PEN",
      "line_key": "supermercados",
      "currency": "PEN",
      "avg_now": 33.81,
      "avg_before": 47.46,
      "delta_pct": -28.8,
      "avg_now_usd": 9.1378,
      "avg_before_usd": 12.827
    }
  ],
  "canasta_basica": [
    {
      "store_name": "Mambo BR",
      "items": 6,
      "total": 64.32,
      "currency": "BRL"
    },
    {
      "store_name": "Plaza Vea",
      "items": 10,
      "total": 65.19,
      "currency": "PEN"
    },
    {
      "store_name": "Metro",
      "items": 10,
      "total": 75.16,
      "currency": "PEN"
    },
    {
      "store_name": "Wong",
      "items": 10,
      "total": 90.35,
      "currency": "PEN"
    },
    {
      "store_name": "Sam's Club BR",
      "items": 6,
      "total": 96.49,
      "currency": "BRL"
    },
    {
      "store_name": "Nuna Orgánica",
      "items": 9,
      "total": 168.72,
      "currency": "PEN"
    },
    {
      "store_name": "Chedraui",
      "items": 10,
      "total": 206.49,
      "currency": "MXN"
    },
    {
      "store_name": "HEB",
      "items": 10,
      "total": 316.2,
      "currency": "MXN"
    },
    {
      "store_name": "Carrefour BR",
      "items": 9,
      "total": 600.18,
      "currency": "BRL"
    },
    {
      "store_name": "Vea AR",
      "items": 10,
      "total": 8598.19,
      "currency": "ARS"
    }
  ],
  "inventory_daily": [
    {
      "day": "2026-05-27",
      "snapshots": 4118
    },
    {
      "day": "2026-05-29",
      "snapshots": 1339
    },
    {
      "day": "2026-05-30",
      "snapshots": 931
    },
    {
      "day": "2026-06-01",
      "snapshots": 2000
    },
    {
      "day": "2026-06-02",
      "snapshots": 75
    },
    {
      "day": "2026-06-03",
      "snapshots": 5
    },
    {
      "day": "2026-06-04",
      "snapshots": 81
    },
    {
      "day": "2026-06-06",
      "snapshots": 467
    },
    {
      "day": "2026-06-07",
      "snapshots": 3108
    },
    {
      "day": "2026-06-08",
      "snapshots": 38807
    }
  ],
  "moat_start": "2026-05-27T01:00:17.122218+00:00",
  "by_country": [
    {
      "country": "BR",
      "count": 16973,
      "stores": 13
    },
    {
      "country": "AR",
      "count": 11024,
      "stores": 8
    },
    {
      "country": "PE",
      "count": 9111,
      "stores": 6
    },
    {
      "country": "MX",
      "count": 5802,
      "stores": 4
    },
    {
      "country": "CO",
      "count": 5482,
      "stores": 3
    },
    {
      "country": "IT",
      "count": 1200,
      "stores": 1
    },
    {
      "country": "FR",
      "count": 925,
      "stores": 1
    },
    {
      "country": "CL",
      "count": 414,
      "stores": 2
    }
  ]
}
```

---

## ✏️ Instrucción

Producí tu sección del reporte Price Pulse CLI Market (§7 Proyección 30/60/90d).
Formato: markdown. Solo tu sección, no el reporte completo.
Incluí tus conclusiones en el formato especificado en tu contexto.