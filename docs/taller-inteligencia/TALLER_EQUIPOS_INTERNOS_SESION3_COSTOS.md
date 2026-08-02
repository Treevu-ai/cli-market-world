# 🎓 Taller de Agentes de Inteligencia de Mercado — Equipos Internos
## Sesión 3 de 3 — Costos

**Audiencia:** equipos internos de Innovación, Producto, Marketing y Marca de una misma empresa.
**Duración:** 2h.
**Formato:** sin código — cada participante dirige en lenguaje natural un agente ya conectado (Claude o ChatGPT con el MCP de CLI Market habilitado).
**Pregunta ancla de la sesión:** de la oportunidad que encontramos, ¿cuánto cuesta traerla al mercado, con qué riesgo de margen, y se sostiene en el tiempo?
**Insumo de entrada:** la Ficha de Oportunidad de Producto de la Sesión 2.
**Entregable final:** un "Caso de Negocio Integrado" por equipo — cierra la serie completa (Investigación → Producto → Costos).

**Relacionado:** `TALLER_EQUIPOS_INTERNOS_SESION1_INVESTIGACION.md`, `TALLER_EQUIPOS_INTERNOS_SESION2_PRODUCTO.md`.

---

## Antes de la sesión (preparación)

**El facilitador debe tener, probado el mismo día:**
- [ ] Confirmar que `market_price_risk`, `market_price_forecast` y `market_procurement_signal` responden con datos reales para el país/línea de cada equipo.
- [ ] Revisar con anticipación **cuáles equipos tienen insumos/componentes importados** — solo ellos necesitan `market_arbitrage` + `market_exchange`; el resto salta ese paso del laboratorio. Avisarles antes, no perder tiempo de sesión decidiéndolo en el momento.
- [ ] Una categoría de ejemplo propia con componente de importación clara, para poder mostrar `market_arbitrage`+`market_exchange` en la demo aunque no todos los equipos lo usen después.

**Pedir a cada equipo, con anticipación:**
- [ ] Traer su Ficha de Oportunidad de Producto completa de la Sesión 2.
- [ ] Un margen objetivo de referencia para la oportunidad identificada (aunque sea aproximado) — sin esto, "riesgo de margen" no tiene con qué compararse.

---

## Agenda (120 min)

### 1. Apertura y retomar el hilo (10 min)

Pedir a 2-3 equipos que lean su conclusión de la Ficha de Oportunidad de Producto (Sesión 2). Encuadre:

> "Ya saben si vale la pena seguir en esta categoría (Sesión 1) y dónde está el espacio para jugar (Sesión 2). Hoy es la pregunta que decide si esto se presenta a un comité o se archiva: ¿el número sale a cuenta?"

### 2. Demo en vivo — riesgo de margen y costo aterrizado (20 min)

Con la categoría de ejemplo del facilitador (con componente importado):

**Paso 1 — riesgo de margen:**
> "¿Cuánto varía el precio dentro de [la subcategoría]? ¿hay espacio para sostener un margen de [X]%?"

Esto invoca `market_price_risk`. Mostrar que no es solo "el precio promedio" — es la dispersión/volatilidad, que es lo que realmente pone en riesgo un margen objetivo.

**Paso 2 — costo aterrizado si hay importación:**
> "¿En qué país de la región es más barato este insumo, y cuánto es eso en soles hoy?"

Esto invoca `market_arbitrage` + `market_exchange` en cadena. Remarcar la limitación explícita: el spread es de precio de góndola, no incluye aranceles, flete ni volatilidad cambiaria entre el momento comparado y el momento de compra real — es una señal de dirección, no una cotización final.

**Paso 3 — ¿el número aguanta en el tiempo?**
> "¿Va a subir el precio de esto en las próximas 3 semanas?"

Esto invoca `market_price_forecast`. Señalar que si hay pocos datos históricos, el forecast devuelve confianza baja **en vez de inventar una tendencia** — eso es señal de calidad, no un defecto de la herramienta.

### 3. Tour de tools de costos (15 min)

| Tool | Qué responde | Frase de ejemplo al agente | Cuándo usarla |
|---|---|---|---|
| `market_price_risk` | Volatilidad/dispersión de precio en una subcategoría | "¿Hay espacio para sostener [X]% de margen en [subcategoría]?" | Siempre |
| `market_arbitrage` + `market_exchange` | Dónde es más barato un insumo cross-border, ajustado por FX | "¿En qué país es más barato [insumo]?" | Solo si hay componente importado |
| `market_price_forecast` | Tendencia + banda de confianza a futuro | "¿Va a subir el precio de [producto/insumo] antes de lanzar?" | Siempre |
| `market_procurement_signal` | Señal de comprar ahora vs. esperar | "¿Es buen momento para comprometer la compra de [insumo] ahora?" | Si hay decisión de timing de compra |

### 4. Preparación del laboratorio (10 min)

Cada equipo:
1. Tiene a mano su Ficha de Oportunidad de Producto de la Sesión 2.
2. Confirma su margen objetivo de referencia.
3. Confirma si su oportunidad tiene componente importado (según lo revisado por el facilitador antes de la sesión) — si no, salta el paso 2 del laboratorio.

### 5. Laboratorio guiado (45 min)

1. **(10 min) Riesgo de margen** — "¿Hay espacio para sostener [mi margen objetivo] en [mi subcategoría]?" Clasificar: margen defendible / ajustado / en riesgo.
2. **(10 min) Costo aterrizado** *(solo equipos con insumo importado)* — "¿En qué país es más barato [mi insumo], ajustado por tipo de cambio de hoy?" Los equipos sin importación usan este tiempo para revisar dos escenarios de margen (conservador/optimista) con `market_price_risk`.
3. **(10 min) Proyección** — "¿Va a subir el precio de [producto/insumo] en las próximas 3 semanas?" Anotar la banda de confianza, no solo la dirección.
4. **(10 min) Timing de decisión** — "¿Es buen momento para comprometer esto ahora o conviene esperar?" Cruzar con la proyección del paso anterior.
5. **(5 min) Síntesis integradora** — llenar el **Caso de Negocio Integrado** (plantilla abajo), que junta las 3 sesiones en un solo documento.

**El facilitador circula** — el error más común aquí es tratar un forecast de baja confianza como si no dijera nada; corregir en vivo: baja confianza es información (no hay suficiente historial), no ausencia de información.

### 6. Show & tell — cierre integrador de las 3 sesiones (25 min)

Cada equipo presenta en 4-5 minutos su **caso completo**, no solo lo de hoy:
1. Lo que el mercado dice (Sesión 1).
2. Dónde está el hueco (Sesión 2).
3. Si el número sale a cuenta y con qué riesgo (Sesión 3).
4. Recomendación: seguir / no seguir / seguir con condición.

Cerrar la serie señalando: esto no es un ejercicio de un solo uso — el mismo agente responde estas preguntas cada semana; la recomendación es fijar una cadencia (mensual o trimestral) para volver a correrlo antes de cada decisión de portafolio real.

---

## Plantilla: Caso de Negocio Integrado (entregable final de la serie)

```
═══ SESIÓN 1 — INVESTIGACIÓN ═══
Categoría / marca:                    _______________________
Inflación de góndola (7d/30d):        _______% / _______%
Gap vs. IPC oficial:                  _______ pp
Conclusión:                           [ ] Vale la pena  [ ] No todavía  [ ] Necesita más dato

═══ SESIÓN 2 — PRODUCTO ═══
SKU/oportunidad identificada:         _______________________
Hueco de precio:                      [ ] Sí — rango: _______  [ ] No
Riesgo de canibalización:             [ ] Alto  [ ] Medio  [ ] Bajo
Competencia ya presente en el hueco:  [ ] No  [ ] Sí: _______

═══ SESIÓN 3 — COSTOS ═══
Margen objetivo:                      _______%
Riesgo de margen (price_risk):        [ ] Defendible  [ ] Ajustado  [ ] En riesgo
Costo aterrizado (si aplica):         País más barato: _______  Ahorro estimado: _______
Proyección de precio (3 semanas):     [ ] Estable  [ ] Sube  [ ] Baja — confianza: [ ] Alta [ ] Baja
Timing de compra/compromiso:          [ ] Ahora  [ ] Esperar

═══ RECOMENDACIÓN FINAL ═══
  [ ] Seguir adelante — evidencia: _______________________
  [ ] No seguir por ahora — razón: _______________________
  [ ] Seguir condicionado a: _______________________

Próxima revisión de este caso (cadencia sugerida): _______________________
```

---

## 🚫 Errores a evitar

- ❌ NO forzar `market_arbitrage`/`market_exchange` en equipos sin componente importado — no aporta y consume tiempo del laboratorio.
- ❌ NO tratar una proyección de baja confianza como "no hay riesgo" — es lo opuesto: hay incertidumbre real, decirlo así en la recomendación final.
- ❌ NO dejar que el Caso de Negocio Integrado sea solo la parte de Costos — debe traer literalmente los datos de las 3 sesiones, es el entregable de la serie completa, no de hoy.
- ❌ NO cerrar sin una recomendación explícita (seguir/no seguir/condicionado) — el objetivo de las 6 horas es una decisión, no un reporte de datos sueltos.

---

**Template version:** 1.0 — Sesión 3 de 3 (Investigación → Producto → Costos)
**Anteriores:** Sesión 1 — Investigación · Sesión 2 — Producto
**Serie completa cerrada.**
