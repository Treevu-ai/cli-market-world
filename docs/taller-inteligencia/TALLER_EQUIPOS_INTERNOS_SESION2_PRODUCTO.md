# 🎓 Taller de Agentes de Inteligencia de Mercado — Equipos Internos
## Sesión 2 de 3 — Producto

**Audiencia:** equipos internos de Innovación, Producto, Marketing y Marca de una misma empresa.
**Duración:** 2h.
**Formato:** sin código — cada participante dirige en lenguaje natural un agente ya conectado (Claude o ChatGPT con el MCP de CLI Market habilitado).
**Pregunta ancla de la sesión:** ¿dónde está el hueco de portafolio, y qué elige el consumidor cuando mi producto no está?
**Insumo de entrada:** el Brief de Categoría de la Sesión 1 (Investigación).
**Entregable:** una "Ficha de Oportunidad de Producto" por equipo — se retoma en la Sesión 3 (Costos).

**Relacionado:** `TALLER_EQUIPOS_INTERNOS_SESION1_INVESTIGACION.md`, `TALLER_INTELIGENCIA_MERCADOS.md` (taller de venta, distinto objetivo).

---

## Antes de la sesión (preparación)

**El facilitador debe tener, probado el mismo día:**
- [ ] Confirmar que `market_substitutes`, `market_dispersion`, `market_ecosystem_radar` y `market_trending` responden con datos reales para el país/línea de la empresa.
- [ ] Una categoría de ejemplo propia (no de los equipos) con un caso de sustitución claro y conocido, lista para la demo de apertura.
- [ ] Revisar `market_coverage_matrix` para el país/línea de cada equipo — si algún equipo trabaja una línea con cobertura débil (ej. farmacias en algunos países), avisarles ANTES del laboratorio, no dejar que lo descubran solos y pierdan los 45 minutos.

**Pedir a cada equipo, con anticipación:**
- [ ] Traer su Brief de Categoría completo de la Sesión 1.
- [ ] Un SKU/producto específico propio (no solo la categoría general) para trabajar el mapa de sustitución — cuanto más específico, mejor sale el ejercicio.

---

## Agenda (120 min)

### 1. Apertura y retomar el hilo (10 min)

Pedir a 2-3 equipos que lean en voz alta la conclusión de su Brief de Categoría (Sesión 1) — especialmente si su creencia inicial fue contradicha por el dato. Esa conclusión es el punto de partida de hoy:

> "Ya saben si vale la pena seguir invirtiendo en esta categoría. Hoy la pregunta cambia: si vale la pena, ¿dónde exactamente está el espacio que pueden ocupar?"

### 2. Demo en vivo — sustitución y huecos de precio (20 min)

Con la categoría/SKU de ejemplo del facilitador:

**Paso 1 — mapa de sustitución:**
> "Si [mi producto específico] no está disponible o sube de precio, ¿qué elige el consumidor en su lugar?"

Esto invoca `market_substitutes`. Señalar explícitamente qué tan cerca o lejos está el sustituto (¿misma subcategoría? ¿mismo rango de precio?) — un sustituto lejano (ej. de otra subcategoría, mucho más barato) es una señal de vulnerabilidad distinta a uno cercano.

**Paso 2 — huecos de precio:**
> "Muéstrame cómo se distribuyen los precios en [la subcategoría], agrupados."

Esto invoca `market_dispersion`. Buscar en vivo un rango de precio donde no hay nadie compitiendo — ese es el hueco. Remarcar: un hueco de precio no es automáticamente una oportunidad, hay que cruzarlo con lo que se aprendió en Investigación (Sesión 1) — si la demanda de esa categoría está débil, un hueco de precio ahí no vale lo mismo.

### 3. Tour de tools de producto (15 min)

| Tool | Qué responde | Frase de ejemplo al agente |
|---|---|---|
| `market_substitutes` | Qué elige el consumidor si mi SKU no está o sube de precio | "¿Qué sustituye a [mi producto] si no está disponible?" |
| `market_dispersion` | Cómo se agrupan los precios dentro de una subcategoría — dónde hay huecos | "Muéstrame la dispersión de precios de [subcategoría] en [país]" |
| `market_ecosystem_radar` | Lanzamientos curados + cache de Product Hunt en categorías cercanas | "¿Qué se está lanzando cerca de [mi categoría] en los últimos 30 días?" |
| `market_trending` | Señal de qué está creciendo en búsquedas/interés | "¿Qué está creciendo en [categoría/país] esta semana?" |
| `market_coverage_matrix` | Si hay suficiente dato para confiar en lo anterior, por país/línea | "¿Qué tan buena es la cobertura de datos para [línea] en [país]?" |

Insistir: `market_ecosystem_radar` no es curiosidad — si alguien más ya está lanzando en el hueco que creen haber encontrado, es información crítica, no una anécdota.

### 4. Preparación del laboratorio (10 min)

Cada equipo:
1. Tiene a mano su Brief de Categoría de la Sesión 1.
2. Elige el SKU/producto específico a mapear (no la categoría completa).
3. Revisa si su línea/país tiene cobertura declarada como fuerte o débil (consultado por el facilitador antes de la sesión).

### 5. Laboratorio guiado (45 min)

1. **(10 min) Mapa de sustitución** — "¿Qué elige el consumidor si [mi SKU específico] no está disponible o sube de precio?" Clasificar el/los sustituto(s): ¿mismo tier de precio o más barato? ¿misma marca u otra?
2. **(10 min) Huecos de precio** — "Muéstrame la dispersión de precios en [mi subcategoría]." Identificar si hay un rango sin competencia. Cruzar contra el Brief de Categoría: ¿ese hueco está en una categoría que el dato de Investigación dice que vale la pena?
3. **(10 min) Radar de lanzamientos** — "¿Qué se está lanzando cerca de [mi categoría] en los últimos 30 días?" y "¿qué está en tendencia en [categoría/país] esta semana?" Si alguien ya está en el hueco identificado, anotarlo — cambia la conclusión, no la invalida.
4. **(10 min) Validación de confianza** — "¿Qué tan buena es la cobertura de datos para [línea] en [país]?" Si es débil, el equipo debe decidir si el hallazgo se sostiene solo con esto o necesita validación adicional (ej. trabajo de campo, panel).
5. **(5 min) Síntesis** — llenar la Ficha de Oportunidad de Producto (plantilla abajo).

**El facilitador circula** — el error más común en este bloque es confundir "no hay nadie ahí" con "hay demanda ahí"; corregir en vivo pidiendo que crucen siempre contra el Brief de Categoría de la Sesión 1.

### 6. Show & tell (15 min)

2-3 equipos comparten: el sustituto que encontraron, el hueco de precio (si lo hay), y si alguien más ya está ahí según el radar de lanzamientos. El caso más valioso es el que combina un hueco real **con** demanda confirmada en la Sesión 1 — señalarlo si aparece.

### 7. Cierre + entregable + puente a Sesión 3 (15 min)

Cada equipo se queda con su **Ficha de Oportunidad de Producto** — es el insumo para la Sesión 3 (Costos), donde la pregunta pasa de "¿dónde está el hueco?" a "¿cuánto cuesta ocuparlo y con qué margen?".

> "Hoy encontraron dónde jugar. La Sesión 3 responde si les conviene jugar ahí."

---

## Plantilla: Ficha de Oportunidad de Producto (entregable de la sesión)

```
Categoría / marca (de Sesión 1):      _______________________
SKU/producto específico analizado:    _______________________

Sustituto(s) identificado(s):         _______________________
  Tier de precio del sustituto:       [ ] Mismo  [ ] Más barato  [ ] Más caro
  Riesgo de canibalización:           [ ] Alto  [ ] Medio  [ ] Bajo

Hueco de precio detectado:            [ ] Sí — rango: _______  [ ] No
  ¿Cruza con demanda confirmada
  en el Brief de Categoría (S1)?      [ ] Sí  [ ] No  [ ] Parcial

Lanzamientos/tendencias cercanas:     [ ] Nada detectado
                                       [ ] Alguien ya está en este espacio: _______
Confiabilidad de cobertura de datos:  [ ] Alta  [ ] Media  [ ] Baja

Conclusión del equipo:
  [ ] Hay una oportunidad de portafolio real — descripción: _______________________
  [ ] El hueco existe pero sin demanda confirmada — no priorizar todavía
  [ ] No hay hueco / ya está ocupado — descartar

¿Qué oportunidad específica llevamos a la Sesión 3 (Costos)?
  _______________________________________________
```

---

## 🚫 Errores a evitar

- ❌ NO tratar "no hay nadie compitiendo ahí" como sinónimo de "hay demanda ahí" — siempre cruzar contra el Brief de Categoría de la Sesión 1.
- ❌ NO ignorar `market_ecosystem_radar` como dato secundario — si alguien más ya vio el mismo hueco, es información que cambia la estrategia, no un detalle.
- ❌ NO analizar la categoría completa quí en `market_substitutes` — usar un SKU específico, el ejercicio pierde precisión con generalidades.
- ❌ NO dejar pasar un equipo con cobertura de datos "Baja" sin marcarlo explícitamente en su Ficha — la conclusión debe reflejar esa incertidumbre.

---

**Template version:** 1.0 — Sesión 2 de 3 (Investigación → Producto → Costos)
**Anterior:** Sesión 1 — Investigación
**Siguiente:** Sesión 3 — Costos (pendiente de desarrollar)
