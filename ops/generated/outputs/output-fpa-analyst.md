# §7 Proyección de Canasta e Inflación — 30/60/90d

**Analista:** Riley · FP&A  
**Fecha de corte:** 2026-06-02T19:51 UTC  
**Metodología:** Proyección lineal simple sobre promedio móvil de 7 días de inflación observada por el collector CLI Market. Sin incorporación de CPI oficial ni variables macroeconómicas externas.

---

## 7.1 Estado de la Serie

| Indicador | Valor |
|-----------|-------|
| Inicio del moat (`moat_start`) | 2026-05-27 |
| Corte (`generated_at`) | 2026-06-02 |
| Días calendario transcurridos | 6 |
| Días con snapshots efectivos | 5 (27-may, 29-may, 30-may, 01-jun, 02-jun) |
| Promedio diario de snapshots | 9,131.2 |
| Total de snapshots acumulados | 45,656 |
| País principal (por volumen) | Brasil — 14,999 snapshots, 13 tiendas |
| Tienda más barata (canasta, BR) | Mambo BR — R$ 65.82 (6 ítems) |

**Dictamen:** ⛔ **Datos insuficientes para proyección.**

La serie tiene 6 días calendario, por debajo del umbral mínimo de 7 días requerido por la metodología CLI Market Price Pulse para habilitar cualquier proyección. Adicionalmente, los 5 días con snapshots presentan dos gaps (28-may y 31-may), lo que impide construir siquiera un promedio móvil de 7 días confiable.

**Razones técnicas que bloquean el forecast:**

1. **Ventana < 7 días.** La regla metodológica exige un mínimo de 7 días de datos para activar una proyección (aunque sea preliminar a 30d). Con 6 días calendario, el modelo no califica.
2. **Sin señal de inflación.** Todos los registros de la tabla `inflation` reportan `delta_pct = 0` y `avg_before = 0.0`. Esto significa que no existe un período «anterior» de comparación: el collector tiene una sola foto de precios, no dos puntos en el tiempo. Sin variación observada, no hay tasa base sobre la cual proyectar.
3. **Gaps en la serie diaria.** De 7 fechas calendario en el rango, solo 5 tienen snapshots. Esto introduce ruido incluso para una estimación naive.

---

## 7.2 Proyección de Canasta (Escenarios)

**Estado: no disponible.**

Para construir escenarios (optimista / base / pesimista) sobre la canasta básica se requiere:
- Una tasa de inflación diaria observada (actualmente `delta_pct = 0` en todas las líneas).
- Al menos 7 días de serie para calibrar bandas de confianza.

La canasta más barata del país principal (Brasil) es **Mambo BR a R$ 65.82**, pero ese valor es una foto puntual. Sin tendencia, cualquier proyección a 30/60/90d sería ruido.

| Escenario | 30 días | 60 días | 90 días |
|-----------|---------|---------|---------|
| Optimista | — | — | — |
| Base | — | — | — |
| Pesimista | — | — | — |

> ⏱️ **Proyección habilitada a partir de:** 2026-06-03 (cuando se cumplan 7 días calendario).  
> 📅 **Proyección a 30d (preliminar):** disponible con ≥7 días.  
> 📅 **Proyección a 60d y 90d:** disponible con >30 días de serie.

---

## 7.3 Proyección de Inflación por Línea

**Estado: no disponible.**

De las 17 líneas-país con datos en `inflation`, **cero** presentan variación (`delta_pct = 0` en todas). Las 3 líneas con mayor volumen de snapshots estimado son:

| Línea | País | `delta_pct` observado |
|-------|------|------------------------|
| Electro y Tecnología | BRL | 0.00% |
| Supermercados | BRL | 0.00% |
| Moda y Vestimenta | BRL | 0.00% |

Sin `delta_pct > 0` en ninguna línea, no es posible:
- Calcular la tasa base de inflación diaria.
- Derivar escenarios optimista (50% tasa base) ni pesimista (150% tasa base).
- Proyectar `avg_now` a 30/60/90d.

La tabla de proyección por línea permanece vacía hasta que el collector acumule al menos dos snapshots con diferencia temporal para las mismas líneas.

---

## 7.4 Factores de Riesgo

Aunque la proyección no está habilitada, se identifican los factores que —cuando exista serie— ejercerán mayor influencia sobre la desviación del forecast:

| # | Factor de Riesgo | Mecanismo de Impacto | Severidad |
|---|-----------------|----------------------|-----------|
| 1 | **Estacionalidad de precios** | Las canastas en supermercados y moda tienen ciclos semanales y quincenales (ofertas, fin de mes). Con <30 días de datos, estos ciclos no son capturados por el modelo lineal simple. | Alta |
| 2 | **Volatilidad cambiaria (BRL, ARS)** | Brasil y Argentina concentran el 55% de los snapshots. El BRL y ARS tienen regímenes de flotación con episodios de estrés. Un movimiento fuerte del tipo de cambio se transmite a precios de electro y supermercados en 7-15 días. El modelo no incorpora FX como variable exógena. | Alta |
| 3 | **Gaps de recolección** | Con solo 5 de 7 días con datos, la serie diaria tiene una completitud del 71%. Si los gaps persisten, el promedio móvil de 7 días será frágil y las bandas de confianza deberán ensancharse. | Media |
| 4 | **Efecto «first-mover» en inflación** | La primera medición de inflación del collector puede sobre-representar o sub-representar la inflación real del mercado porque las tiendas con mayor rotación de precios tienden a ser las primeras en aparecer en el scrape. Este sesgo se corrige solo con >30 días de serie. | Media |
| 5 | **Concentración geográfica** | Brasil representa el 33% de los snapshots totales (14,999 de 45,656). Una proyección agregada regional estará dominada por la dinámica brasileña, sub-representando a México (5,431), Colombia (5,043) y el Cono Sur. | Baja-Media |

---

## 7.5 Plan de Activación del Forecast

| Hito | Fecha estimada | Acción |
|------|---------------|--------|
| Serie ≥ 7 días | **2026-06-03** | Habilitar proyección preliminar a 30d con bandas de confianza ±50% |
| Serie ≥ 14 días | 2026-06-10 | Reducir bandas a ±35%; incorporar primer ciclo semanal |
| Serie ≥ 30 días | 2026-06-26 | Habilitar proyección completa a 30/60/90d con bandas estándar (±20% / ±30% / ±40%) |
| Serie ≥ 60 días | 2026-07-26 | Recalibrar con estacionalidad mensual; habilitar escenario «stress test» |
| Serie ≥ 90 días | 2026-08-25 | Modelo maduro: bandas ajustadas por volatilidad histórica real |

---

## 7.6 Disclaimer

> ⚠️ **Proyección basada exclusivamente en datos del collector CLI Market.** No incorpora variables macroeconómicas externas (tipo de cambio, política monetaria, inflación oficial, shocks de oferta). Los escenarios reflejan únicamente la tendencia observada en los precios de góndola capturados por el sistema. No constituye asesoría financiera, recomendación de inversión ni pronóstico oficial de inflación. Las bandas de confianza se amplían proporcionalmente al horizonte de proyección y a la longitud de la serie histórica disponible.
