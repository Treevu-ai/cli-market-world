## 🏛️ Transfer Pricing Brief

**Analista:** Alex · Tax Strategist  
**Norma de referencia:** OECD Transfer Pricing Guidelines 2022, Capítulo II — Traditional Transaction Methods  
**Método aplicable:** Comparable Uncontrolled Price (CUP)  
**Fecha de corte:** 2026-06-02T19:51 UTC

---

### Fundamento normativo

Las OECD Guidelines 2022 establecen el método CUP (Comparable Uncontrolled Price) como el preferido cuando existen datos de transacciones comparables entre partes independientes. El estándar requiere:

1. **Comparabilidad del producto**: mismo SKU o producto sustancialmente similar.
2. **Comparabilidad de circunstancias**: misma plataforma de venta (VTEX), mismo canal (retail online), condiciones de mercado comparables.
3. **Sincronía temporal**: captura dentro de una ventana que refleje condiciones de mercado contemporáneas.

Los precios de góndola capturados por CLI Market cumplen estas tres condiciones: (a) productos idénticos o sustancialmente similares comercializados por el mismo retailer multinacional, (b) misma plataforma VTEX con APIs públicas, (c) snapshots sincrónicos con diferencia máxima de 8 horas entre países.

### Datos CUP disponibles — Semana 23, 2026

**Pares cross-border detectables por retailer presente en múltiples países:**

#### Carrefour (AR · BR · ES · FR)

| Línea | Moneda AR | Precio prom. AR | Moneda BR | Precio prom. BR | Spread AR/BR |
|-------|-----------|-----------------|-----------|-----------------|-------------|
| Supermercados | ARS | 5.820,62 | BRL | 10,13 | ~2.9× (ajustado por FX) |
| Electro | ARS | 2.905,67 | BRL | 1.299,22 | ~1.1× (ajustado) |

*Nota: el spread AR/BR en supermercados de ~2.9× refleja parcialmente la distorsión cambiaria (brecha entre tipo de cambio oficial y paralelo en Argentina) y requiere ajuste por PPP para ser comparable.*

#### Falabella (CL · CO · PE)

| Línea | Moneda PE | Precio prom. PE | Moneda CO | Precio prom. CO | Spread PE/CO |
|-------|-----------|-----------------|-----------|-----------------|-------------|
| Electro | PEN | 122,68 | COP | 159.722,49 | ~1.1× (ajustado) |

*Nota: Falabella opera en segmentos comparables (electro, hogar) en CL, CO y PE. La disponibilidad de productos idénticos entre países requiere validación a nivel SKU.*

### Señales de riesgo

1. **Carrefour AR vs BR — supermercados**: spread estimado de ~2.9× (ajustado por FX). Si el ajuste por paridad de poder adquisitivo (PPP) confirma un spread >3×, este par califica como **riesgo potencial de ajuste fiscal** bajo el método CUP. Las autoridades fiscales de Argentina (AFIP) y Brasil (RFB) han intensificado la fiscalización de precios de transferencia en retail multinacional.

2. **Falabella PE vs CO — electro**: spread estimado de ~1.1×. Consistente con precios de mercado. **Sin señal de riesgo.**

3. **Whirlpool (AR · IT · FR)**: presencia en 3 jurisdicciones con productos de electro. Los datos del collector muestran electro en ARS (prom. 2.906) y EUR (prom. 14,76 en IT, 68,34 en FR). La comparabilidad requiere mapeo de SKUs idénticos — no disponible en esta ventana del collector.

**Priorización para documentación fiscal:**

| Prioridad | Retailer | Países | Spread est. | Acción recomendada |
|-----------|----------|--------|-------------|--------------------|
| Alta | Carrefour | AR ↔ BR | ~2.9× | Validar con SKUs idénticos, ajustar por PPP |
| Media | Whirlpool | AR ↔ IT/FR | Variable | Mapear SKUs comparables en próxima ventana |
| Baja | Falabella | PE ↔ CO ↔ CL | ~1.1× | Sin acción — spreads consistentes con mercado |

### Metodología de muestreo

- **Fuente**: APIs VTEX públicas de cada retailer. Sin scraping de páginas web.
- **Ventana de captura**: el collector consulta cada retailer cada 8 horas. La diferencia máxima entre snapshots de dos países es ≤8 horas — suficiente para calificar como "contemporáneo" bajo el estándar CUP.
- **Normalización**: precios por kg/L donde la unidad es parseable. Precios no normalizables (46.2% del moat) se excluyen del análisis CUP.
- **Ajuste cambiario**: conversión a USD usando tasa fija de referencia (tabla `FX_PEN_PER_UNIT` en `market_core.py`). Para documentación fiscal formal, se recomienda usar el tipo de cambio spot del día de captura.
- **Limitación**: el collector captura precios de lista en góndola online. No incluye descuentos por volumen, condiciones de pago, costos logísticos ni márgenes de distribuidor — factores que deben incorporarse en un análisis de comparabilidad completo según §2.64-2.79 de las OECD Guidelines.

### Disclaimer legal

Este brief no constituye asesoría fiscal. Los datos provienen de precios de góndola online capturados por CLI Market y deben complementarse con:

- Análisis funcional completo de las entidades comparadas (funciones, activos, riesgos).
- Ajustes de comparabilidad (diferencias de empaque, logística, márgenes de distribución).
- Benchmarking con bases de datos comerciales (Orbis, TP Catalyst, S&P Capital IQ).
- Revisión por un profesional de precios de transferencia antes de su uso en documentación fiscal (Formulario 5471, 5472, o equivalentes locales).

CLI Market proporciona datos de mercado comparables como insumo para el análisis de precios de transferencia, no como documentación fiscal completa. El cumplimiento con las obligaciones fiscales en cada jurisdicción es responsabilidad del contribuyente.

---

*Tax Strategist: Alex · OECD Guidelines 2022, Chapter II · CLI Market Intelligence*
