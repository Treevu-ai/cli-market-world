# Financial Analyst

(Role file not found: C:\Users\acuba\Proyectos\agency-agents\finance\finance-financial-analyst.md)

---

# Financial Analyst — Contexto CLI Market

> Carga este archivo junto con `agency-agents/finance/finance-financial-analyst.md`.
> Tu tarea: producir la narrativa de "qué significan" los números de precios de esta semana.

## Tu rol en este reporte

Sos el Financial Analyst principal. Producís las secciones §1 (Resumen Ejecutivo), §2 (Inflación Observada), y §3 (Canasta Básica). Sos la voz que traduce datos crudos en narrativa accionable para un cliente B2B.

## Contexto del producto

CLI Market agrega precios de góndola de retailers LATAM (VTEX, Shopify, Magento). El collector corre cada 8 horas. El dashboard expone ~45K precios de 36 tiendas en 6 líneas de negocio, 8+ países.

**Tu cliente** es un equipo de fintech (credit scoring), CPG (trade marketing/pricing), o consultora (research). Necesitan saber: ¿subieron o bajaron los precios? ¿dónde? ¿cuánto? ¿qué significa para su negocio?

## Datos que recibís

El script `price_pulse_agents.py` te pasa:

```json
{
  "inflation": [ ... ],
  "canasta_basica": [ ... ],
  "by_line_currency": [ ... ],
  "canasta_spreads": [ ... ],
  "top_risers": [ ... ],
  "top_fallers": [ ... ]
}
```

## Lo que tenés que producir

### §1 Resumen Ejecutivo

3-5 bullets que resuman lo más importante de la semana. Priorizá:

1. **Señal de inflación**: ¿subió o bajó el nivel general de precios? ¿en qué líneas?
2. **Canasta**: ¿cuánto cuesta la canasta básica en la tienda más barata? ¿y en la más cara?
3. **Frescura**: ¿qué % de los datos tiene <24h?
4. **Hecho destacado**: si hay un spread anómalo (>5x) o un mover >20%, mencionarlo.
5. **Tendencia**: ¿la dirección es consistente con semanas anteriores o hay cambio de régimen?

No uses más de 5 bullets. Cada bullet, una idea. lenguaje ejecutivo.

### §2 Inflación Observada

1. **Tabla de inflación por línea/moneda**: línea, moneda, avg_precio_7d, avg_precio_14d, delta_pct, señal (📈/📉/➡️).
2. **Narrativa**: ¿qué líneas lideran la inflación? ¿hay deflación en alguna? ¿el patrón es consistente entre monedas?
3. **Señal agregada**: promedio ponderado (simple) de los deltas. "La señal agregada del collector indica una variación de +X.X% en 7 días."
4. **Disclaimer**: "Inflación observada desde góndola online. No reemplaza IPC oficial (INEI, INDEC, IBGE)."
5. Si no hay datos suficientes (serie <7 días), declararlo explícitamente y explicar que el piloto acumulará historia.

### §3 Canasta Básica

1. **Tabla de canasta**: tienda, país, ítems/10, total, moneda, total_usd (si se puede convertir).
2. **Análisis de ratios**:
   - Spread entre la tienda más barata y la más cara (en misma moneda).
   - Comparación con referencia externa si existe (salario mínimo, canasta oficial).
3. **Nota metodológica**: "La canasta CLI Market consiste en 10 productos de consumo diario (leche, arroz, aceite, azúcar, huevos, pan, café, pollo, queso, jabón). Los precios corresponden a retail formal urbano. No replica la canasta completa del IPC nacional."
4. **Trazabilidad IPC**: incluir la tabla de mapeo a categorías INEI (leche → Alimentos y Bebidas No Alcohólicas, subclase Leche/Queso/Huevos, ponderación 5.03%, etc.). Esta tabla viene pre-definida en `market_spread.py` como `CANASTA_IPC_MAP`.

## Reglas

- Lenguaje: castellano neutro LATAM, tratamiento "usted" para el cliente.
- No uses "store_success_pct". Es métrica lifetime con sesgo histórico.
- Si delta_pct = 0 para todas las líneas, no digas "sin cambios" — decí "serie histórica insuficiente" si es el caso.
- Cada afirmación sobre precios debe poder trazarse a un campo del JSON.
- Los totales en USD son aproximados (FX estático). Aclararlo.


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
  "by_line_currency": [
    {
      "line": "automotriz",
      "line_name": "Automotriz",
      "category_label": "Automotriz · PEN",
      "currency": "PEN",
      "count": 63,
      "p25": 1585.0,
      "p50": 3317.0,
      "p75": 7265.5,
      "min_price": 30.0,
      "max_price": 33346.0,
      "normalizable_pct": 2.1,
      "normalized_unit": "unit"
    },
    {
      "line": "departamentales",
      "line_name": "Tiendas Departamentales",
      "category_label": "Tiendas Departamentales · ARS",
      "currency": "ARS",
      "count": 1593,
      "p25": 34999.0,
      "p50": 64999.0,
      "p75": 149999.0,
      "min_price": 799.0,
      "max_price": 979999.0,
      "normalizable_pct": 9.9,
      "normalized_unit": "unit"
    },
    {
      "line": "departamentales",
      "line_name": "Tiendas Departamentales",
      "category_label": "Tiendas Departamentales · BRL",
      "currency": "BRL",
      "count": 1404,
      "p25": 69.99,
      "p50": 109.99,
      "p75": 194.24,
      "min_price": 7.0,
      "max_price": 8559.63,
      "normalizable_pct": 2.3,
      "normalized_unit": "L"
    },
    {
      "line": "electro",
      "line_name": "Electro y Tecnología",
      "category_label": "Electro y Tecnología · ARS",
      "currency": "ARS",
      "count": 729,
      "p25": 38103.0,
      "p50": 90000.0,
      "p75": 249999.0,
      "min_price": 2249.0,
      "max_price": 999855.0,
      "normalizable_pct": 15.4,
      "normalized_unit": "unit"
    },
    {
      "line": "electro",
      "line_name": "Electro y Tecnología",
      "category_label": "Electro y Tecnología · BRL",
      "currency": "BRL",
      "count": 532,
      "p25": 108.48,
      "p50": 564.45,
      "p75": 1299.0,
      "min_price": 4.9,
      "max_price": 16999.0,
      "normalizable_pct": 27.0,
      "normalized_unit": "kg"
    },
    {
      "line": "electro",
      "line_name": "Electro y Tecnología",
      "category_label": "Electro y Tecnología · CLP",
      "currency": "CLP",
      "count": 407,
      "p25": 26990.0,
      "p50": 47990.0,
      "p75": 119990.0,
      "min_price": 4990.0,
      "max_price": 999990.0,
      "normalizable_pct": 12.3,
      "normalized_unit": "L"
    },
    {
      "line": "electro",
      "line_name": "Electro y Tecnología",
      "category_label": "Electro y Tecnología · EUR",
      "currency": "EUR",
      "count": 2125,
      "p25": 24.4,
      "p50": 134.2,
      "p75": 609.0,
      "min_price": 0.83,
      "max_price": 9999.0,
      "normalizable_pct": 14.6,
      "normalized_unit": "kg"
    },
    {
      "line": "electro",
      "line_name": "Electro y Tecnología",
      "category_label": "Electro y Tecnología · MXN",
      "currency": "MXN",
      "count": 90,
      "p25": 699.0,
      "p50": 1099.0,
      "p75": 5499.0,
      "min_price": 299.0,
      "max_price": 59999.0,
      "normalizable_pct": 11.1,
      "normalized_unit": "kg"
    },
    {
      "line": "farmacias",
      "line_name": "Farmacias y Salud",
      "category_label": "Farmacias y Salud · BRL",
      "currency": "BRL",
      "count": 2899,
      "p25": 16.49,
      "p50": 32.15,
      "p75": 69.34,
      "min_price": 0.69,
      "max_price": 3549.74,
      "normalizable_pct": 45.7,
      "normalized_unit": "kg"
    },
    {
      "line": "farmacias",
      "line_name": "Farmacias y Salud",
      "category_label": "Farmacias y Salud · MXN",
      "currency": "MXN",
      "count": 1392,
      "p25": 95.0,
      "p50": 295.25,
      "p75": 663.5,
      "min_price": 6.0,
      "max_price": 14567.0,
      "normalizable_pct": 48.0,
      "normalized_unit": "kg"
    },
    {
      "line": "hogar",
      "line_name": "Hogar y Construcción",
      "category_label": "Hogar y Construcción · ARS",
      "currency": "ARS",
      "count": 1905,
      "p25": 10555.0,
      "p50": 39995.0,
      "p75": 118500.0,
      "min_price": 285.0,
      "max_price": 990000.0,
      "normalizable_pct": 24.1,
      "normalized_unit": "L"
    },
    {
      "line": "hogar",
      "line_name": "Hogar y Construcción",
      "category_label": "Hogar y Construcción · PEN",
      "currency": "PEN",
      "count": 2960,
      "p25": 26.9,
      "p50": 89.9,
      "p75": 299.0,
      "min_price": 0.1,
      "max_price": 25499.0,
      "normalizable_pct": 21.5,
      "normalized_unit": "kg"
    },
    {
      "line": "moda",
      "line_name": "Moda y Vestimenta",
      "category_label": "Moda y Vestimenta · BRL",
      "currency": "BRL",
      "count": 7942,
      "p25": 49.99,
      "p50": 119.99,
      "p75": 199.99,
      "min_price": 0.35,
      "max_price": 4999.9,
      "normalizable_pct": 7.7,
      "normalized_unit": "L"
    },
    {
      "line": "supermercados",
      "line_name": "Supermercados",
      "category_label": "Supermercados · ARS",
      "currency": "ARS",
      "count": 6549,
      "p25": 1628.79,
      "p50": 3300.0,
      "p75": 6000.0,
      "min_price": 0.5,
      "max_price": 949000.0,
      "normalizable_pct": 88.3,
      "normalized_unit": "kg"
    },
    {
      "line": "supermercados",
      "line_name": "Supermercados",
      "category_label": "Supermercados · BRL",
      "currency": "BRL",
      "count": 4196,
      "p25": 13.98,
      "p50": 25.98,
      "p75": 62.99,
      "min_price": 1.29,
      "max_price": 12142.67,
      "normalizable_pct": 78.2,
      "normalized_unit": "kg"
    },
    {
      "line": "supermercados",
      "line_name": "Supermercados",
      "category_label": "Supermercados · COP",
      "currency": "COP",
      "count": 5479,
      "p25": 7470.0,
      "p50": 14900.0,
      "p75": 29500.0,
      "min_price": 300.0,
      "max_price": 635300.0,
      "normalizable_pct": 80.6,
      "normalized_unit": "L"
    },
    {
      "line": "supermercados",
      "line_name": "Supermercados",
      "category_label": "Supermercados · MXN",
      "currency": "MXN",
      "count": 4320,
      "p25": 34.5,
      "p50": 62.0,
      "p75": 119.1,
      "min_price": 1.8,
      "max_price": 36289.0,
      "normalizable_pct": 76.6,
      "normalized_unit": "kg"
    },
    {
      "line": "supermercados",
      "line_name": "Supermercados",
      "category_label": "Supermercados · PEN",
      "currency": "PEN",
      "count": 6088,
      "p25": 6.9,
      "p50": 12.9,
      "p75": 23.9,
      "min_price": 0.2,
      "max_price": 4649.0,
      "normalizable_pct": 80.7,
      "normalized_unit": "kg"
    }
  ],
  "canasta_spreads": [
    {
      "item": "jabon",
      "currency": "ARS",
      "stores": 3,
      "price_basis": "mixed",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Molde Jabon Formas X 1 Un.",
      "avg_price": 1635.9,
      "min_price": 1.35,
      "max_price": 4905.0,
      "spread_ratio": 3.0,
      "status": "warn"
    },
    {
      "item": "queso",
      "currency": "ARS",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Queso Port Salut Bell's Organico Trozado 1 Kg",
      "avg_price": 314.99,
      "min_price": 6.97,
      "max_price": 931.03,
      "spread_ratio": 2.93,
      "status": "warn"
    },
    {
      "item": "pan",
      "currency": "ARS",
      "stores": 3,
      "price_basis": "mixed",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Jabón Zorro En Pan X 2 Un",
      "avg_price": 853.95,
      "min_price": 2.19,
      "max_price": 2486.4,
      "spread_ratio": 2.91,
      "status": "warn"
    },
    {
      "item": "pollo",
      "currency": "ARS",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Bocaditos Ricosaurios Cresta Roja De Pollo Familiar X 900 Gr",
      "avg_price": 7533.48,
      "min_price": 21.1,
      "max_price": 20135.45,
      "spread_ratio": 2.67,
      "status": "warn"
    },
    {
      "item": "aceite",
      "currency": "ARS",
      "stores": 3,
      "price_basis": "per_L",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Aceite De Girasol Cocinero Light 1 L",
      "avg_price": 1221.24,
      "min_price": 143.0,
      "max_price": 3377.73,
      "spread_ratio": 2.65,
      "status": "warn"
    },
    {
      "item": "aceite",
      "currency": "PEN",
      "stores": 4,
      "price_basis": "per_L",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Aceite Vegetal Máxima 900ml",
      "avg_price": 18.58,
      "min_price": 6.0,
      "max_price": 52.75,
      "spread_ratio": 2.52,
      "status": "warn"
    },
    {
      "item": "jabon",
      "currency": "COP",
      "stores": 3,
      "price_basis": "mixed",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Jabon Facial Antioxidante Class Gold X2",
      "avg_price": 68916.67,
      "min_price": 12500.0,
      "max_price": 181000.0,
      "spread_ratio": 2.44,
      "status": "warn"
    },
    {
      "item": "jabon",
      "currency": "PEN",
      "stores": 4,
      "price_basis": "mixed",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Jabón Tocador REXONA Antibacterial Bamboo y Aloe Paquete 3un",
      "avg_price": 82.99,
      "min_price": 2.63,
      "max_price": 198.89,
      "spread_ratio": 2.36,
      "status": "warn"
    },
    {
      "item": "huevos",
      "currency": "ARS",
      "stores": 3,
      "price_basis": "per_unit",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Huevo Blanco Eggs Hons Libre D Jaula X30",
      "avg_price": 93.77,
      "min_price": 23.62,
      "max_price": 232.19,
      "spread_ratio": 2.22,
      "status": "warn"
    },
    {
      "item": "queso",
      "currency": "BRL",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Pão De Queijo Tradicional Member's Mark 1kg",
      "avg_price": 53.47,
      "min_price": 21.98,
      "max_price": 113.48,
      "spread_ratio": 1.71,
      "status": "ok"
    },
    {
      "item": "leche",
      "currency": "ARS",
      "stores": 3,
      "price_basis": "per_L",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Leche Milkaut Entera Brick X 1 Lt. X 2 Un. + Leche Con Calci",
      "avg_price": 1132.7,
      "min_price": 1.29,
      "max_price": 1750.0,
      "spread_ratio": 1.54,
      "status": "ok"
    },
    {
      "item": "azucar",
      "currency": "BRL",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Açúcar Cristal Especial Colombo Caravelas Pacote 1kg",
      "avg_price": 6.96,
      "min_price": 2.79,
      "max_price": 13.1,
      "spread_ratio": 1.48,
      "status": "ok"
    },
    {
      "item": "leche",
      "currency": "PEN",
      "stores": 4,
      "price_basis": "per_L",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Leche Light BELL'S Caja 1L",
      "avg_price": 8.65,
      "min_price": 5.5,
      "max_price": 17.5,
      "spread_ratio": 1.39,
      "status": "ok"
    },
    {
      "item": "cafe",
      "currency": "MXN",
      "stores": 2,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Cremador para Café Coffee Mate Líquido  530g",
      "avg_price": 190.41,
      "min_price": 64.15,
      "max_price": 316.67,
      "spread_ratio": 1.33,
      "status": "ok"
    },
    {
      "item": "cafe",
      "currency": "PEN",
      "stores": 4,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Toffees de Café ARCOR Butter Bolsa 480g",
      "avg_price": 61.99,
      "min_price": 26.25,
      "max_price": 107.6,
      "spread_ratio": 1.31,
      "status": "ok"
    },
    {
      "item": "pan",
      "currency": "BRL",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Pão de Forma Seven Boys Pacote 450g",
      "avg_price": 25.97,
      "min_price": 12.84,
      "max_price": 46.33,
      "spread_ratio": 1.29,
      "status": "ok"
    },
    {
      "item": "pollo",
      "currency": "BRL",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Sobrecoxa de Frango Aprox. 2,3kg",
      "avg_price": 14.46,
      "min_price": 6.51,
      "max_price": 23.9,
      "spread_ratio": 1.2,
      "status": "ok"
    },
    {
      "item": "huevos",
      "currency": "PEN",
      "stores": 4,
      "price_basis": "per_unit",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Huevos de Codorniz BELL'S Bandeja 24un",
      "avg_price": 0.6,
      "min_price": 0.35,
      "max_price": 0.99,
      "spread_ratio": 1.07,
      "status": "ok"
    },
    {
      "item": "arroz",
      "currency": "BRL",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Arroz Polido Longo Fino Tipo 1 Camil Pacote 1 kg",
      "avg_price": 10.83,
      "min_price": 5.39,
      "max_price": 15.98,
      "spread_ratio": 0.98,
      "status": "ok"
    },
    {
      "item": "pan",
      "currency": "MXN",
      "stores": 2,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Pan Blanco de Caja Selecto 675g",
      "avg_price": 50.84,
      "min_price": 28.15,
      "max_price": 73.53,
      "spread_ratio": 0.89,
      "status": "ok"
    },
    {
      "item": "cafe",
      "currency": "BRL",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Café Torrado e Moído Extraforte Café Brasileiro 500g",
      "avg_price": 85.8,
      "min_price": 45.98,
      "max_price": 121.51,
      "spread_ratio": 0.88,
      "status": "ok"
    },
    {
      "item": "leche",
      "currency": "MXN",
      "stores": 2,
      "price_basis": "per_L",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Leche Marsella 1.5L",
      "avg_price": 20.33,
      "min_price": 12.67,
      "max_price": 28.0,
      "spread_ratio": 0.75,
      "status": "ok"
    },
    {
      "item": "pollo",
      "currency": "COP",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Trozo De Pollo Marinado* SMN 900  gr",
      "avg_price": 14866.67,
      "min_price": 8777.78,
      "max_price": 18755.56,
      "spread_ratio": 0.67,
      "status": "ok"
    },
    {
      "item": "arroz",
      "currency": "ARS",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Arroz La Esquina De Las Flores 1 Kg",
      "avg_price": 750.23,
      "min_price": 600.35,
      "max_price": 1050.0,
      "spread_ratio": 0.6,
      "status": "ok"
    },
    {
      "item": "leche",
      "currency": "COP",
      "stores": 3,
      "price_basis": "per_L",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Leche deslactosada FRESCAMPO semidescremada (900  ml)",
      "avg_price": 3197.98,
      "min_price": 2222.22,
      "max_price": 3944.44,
      "spread_ratio": 0.54,
      "status": "ok"
    },
    {
      "item": "pollo",
      "currency": "PEN",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Molleja de Pollo SADIA Bolsa 1kg",
      "avg_price": 9.77,
      "min_price": 7.5,
      "max_price": 10.9,
      "spread_ratio": 0.35,
      "status": "ok"
    },
    {
      "item": "queso",
      "currency": "MXN",
      "stores": 2,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Prosa Salchicha Para Asar con Queso 800 g",
      "avg_price": 128.75,
      "min_price": 107.5,
      "max_price": 150.0,
      "spread_ratio": 0.33,
      "status": "ok"
    },
    {
      "item": "queso",
      "currency": "PEN",
      "stores": 4,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Queso Fresco BELL'S Paquete 300g",
      "avg_price": 31.01,
      "min_price": 28.0,
      "max_price": 35.33,
      "spread_ratio": 0.24,
      "status": "ok"
    },
    {
      "item": "azucar",
      "currency": "COP",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Azúcar FRESCAMPO blanco (1000  gr)",
      "avg_price": 3543.33,
      "min_price": 3190.0,
      "max_price": 3990.0,
      "spread_ratio": 0.23,
      "status": "ok"
    },
    {
      "item": "aceite",
      "currency": "MXN",
      "stores": 2,
      "price_basis": "per_L",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Mi Tienda Aceite Comestible Vegetal 946 ml",
      "avg_price": 34.8,
      "min_price": 31.61,
      "max_price": 38.0,
      "spread_ratio": 0.18,
      "status": "ok"
    },
    {
      "item": "pan",
      "currency": "PEN",
      "stores": 4,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Pan de Molde Integral Avena 655gr Calypso",
      "avg_price": 14.45,
      "min_price": 12.98,
      "max_price": 15.45,
      "spread_ratio": 0.17,
      "status": "ok"
    },
    {
      "item": "cafe",
      "currency": "ARS",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Café molido torrado Carrefour Classic 500 grs",
      "avg_price": 24688.67,
      "min_price": 22482.0,
      "max_price": 26600.0,
      "spread_ratio": 0.17,
      "status": "ok"
    },
    {
      "item": "huevos",
      "currency": "COP",
      "stores": 3,
      "price_basis": "per_unit",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Huevo Santa Anita Rojo B Amarrado X30 Unds",
      "avg_price": 464.33,
      "min_price": 430.0,
      "max_price": 496.67,
      "spread_ratio": 0.14,
      "status": "ok"
    },
    {
      "item": "queso",
      "currency": "COP",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Pan Olimpica Francés con Ajo y Queso 350 G",
      "avg_price": 21879.37,
      "min_price": 19971.43,
      "max_price": 22833.33,
      "spread_ratio": 0.13,
      "status": "ok"
    },
    {
      "item": "azucar",
      "currency": "MXN",
      "stores": 2,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Azúcar Chedraui Estándar 900g",
      "avg_price": 27.22,
      "min_price": 25.54,
      "max_price": 28.89,
      "spread_ratio": 0.12,
      "status": "ok"
    },
    {
      "item": "cafe",
      "currency": "COP",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Café EKONO tostado y molido (500  gr)",
      "avg_price": 41466.67,
      "min_price": 39800.0,
      "max_price": 44800.0,
      "spread_ratio": 0.12,
      "status": "ok"
    },
    {
      "item": "pan",
      "currency": "COP",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Harina PAN maíz blanco (1000  gr)",
      "avg_price": 3563.33,
      "min_price": 3400.0,
      "max_price": 3800.0,
      "spread_ratio": 0.11,
      "status": "ok"
    },
    {
      "item": "jabon",
      "currency": "MXN",
      "stores": 2,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Zote Jabón de Lavandería Barra Rosa 200 g",
      "avg_price": 66.25,
      "min_price": 62.5,
      "max_price": 70.0,
      "spread_ratio": 0.11,
      "status": "ok"
    },
    {
      "item": "arroz",
      "currency": "PEN",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Arroz Superior Paisana Bolsa 1 kg",
      "avg_price": 4.77,
      "min_price": 4.5,
      "max_price": 5.0,
      "spread_ratio": 0.1,
      "status": "ok"
    },
    {
      "item": "azucar",
      "currency": "ARS",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Azucar Azucel X 1kg",
      "avg_price": 1229.33,
      "min_price": 1191.0,
      "max_price": 1298.0,
      "spread_ratio": 0.09,
      "status": "ok"
    },
    {
      "item": "azucar",
      "currency": "PEN",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Azúcar Rubia BELL'S Bolsa 1Kg",
      "avg_price": 3.87,
      "min_price": 3.8,
      "max_price": 4.0,
      "spread_ratio": 0.05,
      "status": "ok"
    },
    {
      "item": "arroz",
      "currency": "COP",
      "stores": 3,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Arroz DIANA blanco vitamor (1000  gr)",
      "avg_price": 4050.0,
      "min_price": 3950.0,
      "max_price": 4100.0,
      "spread_ratio": 0.04,
      "status": "ok"
    },
    {
      "item": "aceite",
      "currency": "COP",
      "stores": 3,
      "price_basis": "per_L",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Aceite FRESCAMPO vegetal multiusos (900  ml)",
      "avg_price": 7307.41,
      "min_price": 7211.11,
      "max_price": 7500.0,
      "spread_ratio": 0.04,
      "status": "ok"
    },
    {
      "item": "arroz",
      "currency": "MXN",
      "stores": 2,
      "price_basis": "per_kg",
      "pack_filter": "standard_1kg_1L",
      "sample_name": "Mi Tienda Arroz Extra 907 g",
      "avg_price": 15.44,
      "min_price": 15.33,
      "max_price": 15.56,
      "spread_ratio": 0.01,
      "status": "ok"
    }
  ],
  "top_risers": [],
  "top_fallers": []
}
```

---

## ✏️ Instrucción

Producí tu sección del reporte Price Pulse CLI Market (§1 Resumen Ejecutivo + §2 Inflación + §3 Canasta Básica).
Formato: markdown. Solo tu sección, no el reporte completo.
Incluí tus conclusiones en el formato especificado en tu contexto.