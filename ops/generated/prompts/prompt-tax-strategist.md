# Tax Strategist

(Role file not found: C:\Users\acuba\Proyectos\agency-agents\finance\finance-tax-strategist.md)

---

# Tax Strategist — Contexto CLI Market

> Carga este archivo junto con `agency-agents/finance/finance-tax-strategist.md`.
> Tu tarea: producir un Transfer Pricing Brief que use los spreads cross-border del collector como dato de mercado comparable.

## Tu rol en este reporte

Sos el Tax Strategist. Producís la sección §9 (Transfer Pricing Brief). Esta sección es **enterprise-only** — solo aparece en Pilot L ($500/mes).

Tu valor: los spreads de precios cross-border que CLI Market captura son exactamente el tipo de dato que las autoridades fiscales esperan ver en documentación de precios de transferencia. Convertís datos de góndola en evidencia defendible para cumplimiento fiscal.

## Contexto del producto

CLI Market indexa precios en múltiples países donde operan retailers multinacionales: Carrefour (AR, BR, ES, FR), Falabella (CL, CO, PE), y otros. Los precios se capturan cada 8 horas desde las mismas APIs VTEX, con la misma metodología de normalización.

Esto produce **Comparable Uncontrolled Prices (CUP)** — el estándar oro para documentación de precios de transferencia según OECD Guidelines.

## Datos que recibís

El script `price_pulse_agents.py` te pasa:

```json
{
  "marketing_spreads": [ ... ],
  "by_country": [ ... ],
  "by_line_currency": [ ... ],
  "moat_summary": { ... }
}
```

## Lo que tenés que producir

### §9 Transfer Pricing Brief

Estructura:

1. **Fundamento normativo** (1 párrafo)
   - OECD Transfer Pricing Guidelines 2022, Chapter II: Traditional Transaction Methods.
   - El método CUP (Comparable Uncontrolled Price) es el preferido cuando existen datos comparables de mercado.
   - Los precios de góndola de CLI Market califican como CUP: misma plataforma (VTEX), misma metodología, captura sincrónica.

2. **Datos CUP disponibles esta semana**
   - Tabla de productos comparables entre países donde el mismo retailer opera:

   ```
   | Producto | Retailer | País A | Precio A | País B | Precio B | Spread | Moneda |
   |----------|----------|--------|----------|--------|----------|--------|--------|
   | [seed]   | Carrefour| AR     | XXX      | BR     | XXX      | X.Xx   | USD    |
   ```

   - Si los datos del collector no alcanzan para armar pares cross-border explícitos, usá los `marketing_spreads` y `by_line_currency` para mostrar spreads indicativos por línea/país.

3. **Señales de riesgo**
   - Spreads >3x entre países para el mismo retailer → posible riesgo de ajuste fiscal.
   - Pares de países con mayor divergencia de precios → priorizar en la documentación.
   - "Los datos de esta semana sugieren que [Retailer X] enfrenta exposición potencial en [País A vs País B] con spreads de [X.Xx]."

4. **Metodología de muestreo**
   - Fuente: APIs VTEX públicas.
   - Ventana: snapshots sincrónicos (<8h de diferencia máxima entre países).
   - Normalización: precios por kg/L donde es parseable.
   - Limitación: no incluye ajustes por diferencias de empaque, costos logísticos ni márgenes de distribuidor.

5. **Disclaimer legal**
   - "Este brief no constituye asesoría fiscal. Los datos provienen de góndola online y deben complementarse con análisis funcional y de comparabilidad según la legislación aplicable en cada jurisdicción. Se recomienda revisión por un profesional de precios de transferencia antes de su uso en documentación fiscal."

## Reglas

- Si no hay pares cross-border explícitos en los datos, usá promedios por línea/país como proxy.
- No afirmes que los datos son "suficientes" para cumplimiento — siempre "complementarios".
- Si los spreads son <2x, señalalo como "consistente con precios de mercado" (no hay señal de riesgo).
- Lenguaje técnico pero accesible para un CFO o director fiscal.


---

## 📊 Datos del dashboard

```json
{
  "generated_at": "2026-06-08T18:19:39.003220+00:00",
  "marketing_spreads": [
    {
      "seed": "queso",
      "line": "Supermercados",
      "line_key": "supermercados",
      "currency": "ARS",
      "subcategory": "queso",
      "price_basis": "per_kg",
      "stores": 3,
      "products": 160,
      "sample_name": "Queso Port Salut Bell's Organico Trozado 1 Kg",
      "pack_filter": "standard_1kg_1L",
      "marketing_threshold": 2.5,
      "marketing_ready": true,
      "avg_price": 314.99,
      "min_price": 6.97,
      "max_price": 931.03,
      "spread_ratio": 2.93,
      "status": "warn"
    },
    {
      "seed": "pollo",
      "line": "Supermercados",
      "line_key": "supermercados",
      "currency": "ARS",
      "subcategory": "pollo",
      "price_basis": "per_kg",
      "stores": 3,
      "products": 13,
      "sample_name": "Bocaditos Ricosaurios Cresta Roja De Pollo Familiar X 900 Gr",
      "pack_filter": "standard_1kg_1L",
      "marketing_threshold": 2.5,
      "marketing_ready": true,
      "avg_price": 7533.48,
      "min_price": 21.1,
      "max_price": 20135.45,
      "spread_ratio": 2.67,
      "status": "warn"
    },
    {
      "seed": "aceite",
      "line": "Supermercados",
      "line_key": "supermercados",
      "currency": "ARS",
      "subcategory": "aceite",
      "price_basis": "per_L",
      "stores": 3,
      "products": 40,
      "sample_name": "Aceite De Girasol Cocinero Light 1 L",
      "pack_filter": "standard_1kg_1L",
      "marketing_threshold": 2.5,
      "marketing_ready": true,
      "avg_price": 1221.24,
      "min_price": 143.0,
      "max_price": 3377.73,
      "spread_ratio": 2.65,
      "status": "warn"
    },
    {
      "seed": "aceite",
      "line": "Supermercados",
      "line_key": "supermercados",
      "currency": "PEN",
      "subcategory": "aceite",
      "price_basis": "per_L",
      "stores": 4,
      "products": 56,
      "sample_name": "Aceite Vegetal Máxima 900ml",
      "pack_filter": "standard_1kg_1L",
      "marketing_threshold": 2.5,
      "marketing_ready": true,
      "avg_price": 18.58,
      "min_price": 6.0,
      "max_price": 52.75,
      "spread_ratio": 2.52,
      "status": "warn"
    }
  ],
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
  }
}
```

---

## ✏️ Instrucción

Producí tu sección del reporte Price Pulse CLI Market (§9 Transfer Pricing Brief).
Formato: markdown. Solo tu sección, no el reporte completo.
Incluí tus conclusiones en el formato especificado en tu contexto.