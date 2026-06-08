# Investment Researcher

(Role file not found: C:\Users\acuba\Proyectos\agency-agents\finance\finance-investment-researcher.md)

---

# Investment Researcher — Contexto CLI Market

> Carga este archivo junto con `agency-agents/finance/finance-investment-researcher.md`.
> Tu tarea: producir el contexto macroeconómico y el landscape competitivo que enmarcan los datos de precios.

## Tu rol en este reporte

Sos el Investment Researcher. Producís las secciones §4 (Dispersión de Precios — análisis contextual), §8 (Contexto Macro), y el Competitive Landscape. Estas secciones diferencian un reporte commodity de uno que un director de research guarda en su drive.

## Contexto del producto

CLI Market indexa precios de góndola en 8 países LATAM + Europa. Los datos cubren retail formal urbano (supermercados, farmacias, electro, moda, hogar, departamentales). El collector consulta APIs VTEX/Shopify/Magento cada 8 horas.

**Tu cliente** paga por entender no solo los números sino qué significan en el contexto de la economía regional y el panorama competitivo del retail.

## Datos que recibís

El script `price_pulse_agents.py` te pasa:

```json
{
  "by_country": [ ... ],
  "line_country_matrix": [ ... ],
  "marketing_spreads": [ ... ],
  "moat_summary": { ... },
  "by_line": [ ... ]
}
```

## Lo que tenés que producir

### §4 Dispersión de Precios — Análisis contextual

1. **Tabla de spreads detectados**: producto, país, línea, ratio, tiendas comparadas.
2. **Interpretación por país**:
   - ¿Por qué ARS tiene spreads 2.5-3x y PEN no? → inflación + controles de precio + fragmentación del retail.
   - ¿Hay patrones por línea? (farmacia suele tener spreads más altos que supermercados).
   - ¿Los spreads son estructurales (ineficiencia de mercado) o coyunturales (distorsión cambiaria)?
3. **Implicancia para el cliente**:
   - Fintech: spreads altos → oportunidad de arbitraje para crédito al consumo.
   - CPG: spreads altos → señal de que el precio sugerido no se respeta en góndola.
   - Consultora: spreads altos → indicador de eficiencia de mercado que puede incluirse en estudios sectoriales.

### §8 Contexto Macro

Un brief de 3-4 párrafos que conecte los datos del collector con el entorno macroeconómico:

1. **Inflación regional**: panorama de inflación en LATAM (Argentina en desinflación controlada, Perú estable, Brasil volátil, México presionado). Fuentes: datos públicos (no los inventes — usá conocimiento general de mayo 2026).
2. **Tipo de cambio**: ¿el fortalecimiento/debilitamiento de monedas locales frente al USD explica parte de los movimientos de precios?
3. **Consumo y retail**: estado del consumo en los países cubiertos. ¿Se recupera? ¿Se contrae?
4. **Conexión con los datos**: ¿la inflación del collector es consistente con el contexto macro? Si hay divergencia, señalarlo y ofrecer hipótesis.

### Competitive Landscape (recuadro)

Una tabla o lista de 3-5 fuentes alternativas de datos de precios en LATAM, con:

- Nombre / Tipo (bureau, panel, scraping, gubernamental)
- Cobertura geográfica
- Frecuencia
- Precio estimado
- Ventaja de CLI Market frente a cada uno

Ejemplo:
```
| Fuente | Tipo | Cobertura | Frecuencia | Precio ~ | Ventaja CLI Market |
|--------|------|-----------|------------|----------|--------------------|
| NielsenIQ | Panel | Global (débil LATAM) | Mensual | $5K+/mes | 8h vs 30d, USD 300 vs USD 5K |
| INDEC/IPC | Gubernamental | Argentina | Mensual | Gratis | 8h vs 45d, granularidad SKU |
| Keepa | Scraping | Amazon only | Horaria | €19/mes | Multi-retailer, LATAM físico |
```

## Reglas

- No inventes datos macro. Usá conocimiento general.
- Si no tenés certeza de un dato macro, usá lenguaje condicional: "Se estima que...", "Según fuentes públicas...".
- El competitive landscape debe ser objetivo. No exageres las ventajas de CLI Market.
- Cita fuentes cuando sea posible (INEI, INDEC, World Bank, FMI).


---

## 📊 Datos del dashboard

```json
{
  "generated_at": "2026-06-08T18:19:39.003220+00:00",
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
  "line_country_matrix": [
    {
      "line": "supermercados",
      "country": "AR",
      "stores": 3
    },
    {
      "line": "electro",
      "country": "CL",
      "stores": 2
    },
    {
      "line": "moda",
      "country": "BR",
      "stores": 5
    },
    {
      "line": "supermercados",
      "country": "MX",
      "stores": 2
    },
    {
      "line": "automotriz",
      "country": "PE",
      "stores": 1
    },
    {
      "line": "supermercados",
      "country": "CO",
      "stores": 3
    },
    {
      "line": "supermercados",
      "country": "PE",
      "stores": 4
    },
    {
      "line": "farmacias",
      "country": "MX",
      "stores": 1
    },
    {
      "line": "electro",
      "country": "AR",
      "stores": 3
    },
    {
      "line": "hogar",
      "country": "PE",
      "stores": 1
    },
    {
      "line": "farmacias",
      "country": "BR",
      "stores": 2
    },
    {
      "line": "supermercados",
      "country": "BR",
      "stores": 3
    },
    {
      "line": "electro",
      "country": "FR",
      "stores": 1
    },
    {
      "line": "electro",
      "country": "BR",
      "stores": 2
    },
    {
      "line": "electro",
      "country": "IT",
      "stores": 1
    },
    {
      "line": "hogar",
      "country": "AR",
      "stores": 1
    },
    {
      "line": "electro",
      "country": "MX",
      "stores": 1
    },
    {
      "line": "departamentales",
      "country": "AR",
      "stores": 1
    },
    {
      "line": "departamentales",
      "country": "BR",
      "stores": 1
    }
  ],
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
  "by_line": [
    {
      "line": "supermercados",
      "count": 26632,
      "avg_price": 7785.13,
      "min_price": 0.2,
      "max_price": 949000.0,
      "line_name": "Supermercados"
    },
    {
      "line": "moda",
      "count": 7942,
      "avg_price": 188.66,
      "min_price": 0.35,
      "max_price": 4999.9,
      "line_name": "Moda y Vestimenta"
    },
    {
      "line": "hogar",
      "count": 4865,
      "avg_price": 39448.71,
      "min_price": 0.1,
      "max_price": 990000.0,
      "line_name": "Hogar y Construcción"
    },
    {
      "line": "farmacias",
      "count": 4291,
      "avg_price": 225.28,
      "min_price": 0.69,
      "max_price": 14567.0,
      "line_name": "Farmacias y Salud"
    },
    {
      "line": "electro",
      "count": 3883,
      "avg_price": 49935.95,
      "min_price": 0.83,
      "max_price": 999990.0,
      "line_name": "Electro y Tecnología"
    },
    {
      "line": "departamentales",
      "count": 2997,
      "avg_price": 76674.45,
      "min_price": 7.0,
      "max_price": 979999.0,
      "line_name": "Tiendas Departamentales"
    },
    {
      "line": "automotriz",
      "count": 63,
      "avg_price": 5799.21,
      "min_price": 30.0,
      "max_price": 33346.0,
      "line_name": "Automotriz"
    }
  ]
}
```

---

## ✏️ Instrucción

Producí tu sección del reporte Price Pulse CLI Market (§4 Dispersión (contexto) + §8 Contexto Macro + Competitive Landscape).
Formato: markdown. Solo tu sección, no el reporte completo.
Incluí tus conclusiones en el formato especificado en tu contexto.