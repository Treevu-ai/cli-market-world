# 🎓 Taller de Agentes de Inteligencia de Mercado — Equipos Internos
## Sesión 1 de 3 — Investigación

**Audiencia:** equipos internos de Innovación, Producto, Marketing y Marca de una misma empresa.
**Duración:** 2h.
**Formato:** sin código — cada participante dirige en lenguaje natural un agente ya conectado (Claude o ChatGPT con el MCP de CLI Market habilitado). Lo que se enseña es qué preguntar y en qué orden, no sintaxis.
**Pregunta ancla de la sesión:** ¿vale la pena mover recursos hacia esta categoría/mercado ahora mismo?
**Entregable:** un "Brief de Categoría" de una página por equipo — se retoma en la Sesión 2 (Producto).

**Relacionado:** `TALLER_INTELIGENCIA_MERCADOS.md` (taller de venta 1:1, distinto objetivo/audiencia), `CHECKLIST_DEMO_TALLER.md`.

---

## Antes de la sesión (preparación)

**El facilitador debe tener, probado el mismo día:**
- [ ] Claude Desktop o ChatGPT con el MCP de CLI Market conectado y funcionando en su propia laptop (para la demo en vivo) y en al menos una laptop de respaldo.
- [ ] Confirmar que `market_intel_brief`, `market_inflation_report`, `market_basket_stress`, `market_promo_detector` y `market_gov_observations` responden con datos reales para el país de la empresa — correrlos una vez antes, no asumir.
- [ ] Una categoría de ejemplo propia (no de la empresa) lista para la demo de apertura, para no "gastar" la categoría real del equipo antes del laboratorio.

**Pedir a cada equipo participante, con 3-5 días de anticipación:**
- [ ] Una categoría o marca real de la empresa para trabajar las 3 sesiones (la misma en las 3).
- [ ] Una creencia o supuesto sobre esa categoría que hoy defienden "porque así ha sido siempre" o "porque lo dice el proveedor/la encuesta trimestral" — sin dato semanal que lo respalde.
- [ ] Acceso a Claude o ChatGPT con el MCP de CLI Market ya conectado (mandar guía de setup aparte, no usar tiempo de sesión en instalar nada).

---

## Agenda (120 min)

### 1. Apertura y encuadre (10 min)

Frase de apertura:

> "Hoy toda decisión de dónde invertir en esta categoría se apoya en tres tipos de dato malo: una encuesta trimestral, el IPC oficial con 1-2 meses de rezago, o lo que dice el proveedor por teléfono. Ninguno de los tres te dice qué pasó esta semana en la góndola."

Preguntar a la sala: *"¿Cuál es la creencia que traen sobre su categoría que hoy no pueden defender con un dato de esta semana?"* — anotar 2-3 respuestas en vivo, se retoman al cierre.

Explicar el hilo de las 3 sesiones (Investigación → Producto → Costos) y que hoy solo se responde "¿vale la pena seguir?", no "qué hacemos" — eso es la Sesión 2.

### 2. Demo en vivo — el dato y su propia honestidad (20 min)

Con la categoría de ejemplo del facilitador (no la de los equipos):

**Paso 1 — el brief completo, en una sola pregunta al agente:**
> "Dame un brief de inteligencia de mercado para [categoría] en [país] de los últimos 7 días."

Esto invoca `market_intel_brief` — mostrar que agrega inflación, basket stress, actividad de promos y cobertura de retailers en una sola respuesta, no cinco búsquedas sueltas.

**Paso 2 — la honestidad metodológica (el momento que da credibilidad a todo lo demás):**
Señalar explícitamente en la respuesta el campo de disclaimer (`internal_inflation_pct: X% — no equivalente al IPC oficial, distinta canasta y metodología`). Decir en voz alta:

> "Esto no es un truco de venta — es la razón por la que este número se puede defender frente a Finanzas o un comité, y el IPC oficial no se puede refutar con un truco de venta tampoco."

**Paso 3 — cruzar contra el dato oficial:**
> "Compara eso contra el tipo de cambio y el IPC de Lima del BCRP."

Esto invoca `market_gov_observations` — mostrar que CLI Market no reemplaza el dato oficial, lo complementa y permite ver el "gap macro" (shelf vs. IPC oficial) con matiz explícito.

### 3. Tour de tools de investigación (15 min)

No demo en vivo aquí — solo explicar qué responde cada una y cuándo pedirla, con una frase de ejemplo por tool:

| Tool | Qué responde | Frase de ejemplo al agente |
|---|---|---|
| `market_intel_brief` | Resumen agregado: inflación + basket stress + promos + cobertura | "Dame el brief de [categoría] en [país]" |
| `market_inflation_report` | Inflación de góndola vs. gap con IPC oficial | "¿Cómo viene subiendo el precio de [categoría] este mes?" |
| `market_basket_stress` | Índice de estrés de canasta básica — presión sobre el bolsillo del consumidor | "¿Cómo está la presión de precios en [país] esta semana?" |
| `market_promo_detector` | Detecta descuentos "inflados" (subir precio de lista antes de anunciar rebaja) | "¿Los descuentos de [categoría] son reales o inflados?" |
| `market_gov_observations` | Dato oficial BCRP (tipo de cambio, IPC Lima) para cruzar | "Compara eso contra el IPC oficial" |
| `market_informal_signal` | Honestidad de cobertura — qué tan confiable es la señal para esta categoría/país | "¿Qué tan confiable es este dato para [categoría]?" |

Insistir en `market_informal_signal`: no mide el mercado informal, mide qué tan bien cubierto está el canal formal — es la herramienta que evita presentar una señal débil como si fuera fuerte.

### 4. Preparación del laboratorio (10 min)

Cada equipo:
1. Confirma su categoría/marca real (la que trajeron de tarea).
2. Escribe en una tarjeta la creencia que quieren poner a prueba (de la apertura).
3. Define el país o los países donde eso importa.

### 5. Laboratorio guiado (45 min)

Instrucciones paso a paso que cada equipo sigue con su propio agente, sobre su propia categoría:

1. **(10 min) Brief base** — "Dame un brief de inteligencia de mercado para [su categoría] en [su país] de los últimos 7 y 30 días." Comparar ambas ventanas: ¿la señal es consistente o es ruido de corto plazo?
2. **(10 min) Cruce oficial** — "Cruza eso contra el tipo de cambio y el IPC oficial." Anotar el gap (shelf vs. oficial) y si es defendible o no.
3. **(10 min) Integridad promocional** — "¿Hay descuentos inflados en mi categoría en las últimas 4 semanas?" Si el equipo tiene marca propia, revisar también su propia marca, no solo competencia.
4. **(10 min) Honestidad de cobertura** — "¿Qué tan confiable es este dato para mi categoría/país?" Si la cobertura es baja, el equipo debe decidir: ¿seguimos con este dato con esa salvedad explícita, o necesitamos otra fuente?
5. **(5 min) Síntesis** — cada equipo llena el Brief de Categoría (plantilla abajo) con lo que encontró.

**El facilitador circula durante todo el bloque** — el error más común es que el equipo acepte el primer número sin cruzarlo contra el oficial o sin revisar la cobertura; corregir eso en vivo, mesa por mesa.

### 6. Show & tell (15 min)

2-3 equipos comparten, en 3 minutos cada uno: su creencia original, lo que el dato realmente dijo, y si coincidió o la contradijo. El caso más valioso para la sala es el que **contradice** la creencia inicial — señalarlo explícitamente si aparece.

### 7. Cierre + entregable + puente a Sesión 2 (15 min)

Cada equipo se queda con su **Brief de Categoría** completo (plantilla abajo) — es el insumo que traen a la Sesión 2 (Producto), donde la pregunta pasa de "¿vale la pena?" a "¿dónde está el hueco?".

> "La Sesión 2 no empieza de cero — empieza exactamente donde termina esto que tienen en la mano."

---

## Plantilla: Brief de Categoría (entregable de la sesión)

```
Categoría / marca:                    _______________________
País(es):                             _______________________
Creencia que pusimos a prueba:        _______________________

Inflación de góndola (7d / 30d):      _______ % / _______ %
Gap vs. IPC oficial:                  _______ pp (dirección: ⬆ / ⬇ / neutro)
Estrés de canasta (basket stress):    _______________________
Integridad promocional:               [ ] Sin señales de descuento inflado
                                       [ ] Se detectaron descuentos inflados en: _______
Confiabilidad de cobertura:           [ ] Alta  [ ] Media  [ ] Baja — nota: _______

Conclusión del equipo:
  [ ] La creencia se confirma con el dato
  [ ] La creencia se contradice — nuevo hallazgo: _______________________
  [ ] Dato insuficiente — necesitamos: _______________________

¿Vale la pena seguir invirtiendo tiempo/recursos en esta categoría ahora?
  [ ] Sí, con evidencia de: _______________________
  [ ] No todavía, porque: _______________________
  [ ] Necesita más investigación en: _______________________
```

---

## 🚫 Errores a evitar

- ❌ NO dejar que un equipo presente `internal_inflation_pct` como si fuera el IPC oficial del INEI/BCRP — siempre el disclaimer explícito.
- ❌ NO saltarse `market_informal_signal` — presentar una señal de baja cobertura como si fuera concluyente es peor que no tener dato.
- ❌ NO dejar que el laboratorio se vuelva "buscar por buscar" — cada equipo debe cerrar con una conclusión sobre SU creencia inicial, no solo con números sueltos.
- ❌ NO gastar la categoría real del equipo en la demo de apertura — usar siempre una categoría del facilitador para eso.

---

**Template version:** 1.0 — Sesión 1 de 3 (Investigación → Producto → Costos)
**Siguiente:** Sesión 2 — Producto (pendiente de desarrollar)
