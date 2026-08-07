---
title: Preparación técnica — Reunión Gerencia de Estudios Económicos INDECOPI
tags:
  - indecopi
  - meeting-prep
  - data-integrity
  - methodology
status: final
date: 2026-08-06
meeting_date: 2026-08-07
related: INDECOPI_ARCHITECTURE_ANALYSIS.md, methodology.md, 🏗️_moat_engine/data-integrity-prd.md
review_status: COMPLETO — code-reviewer (APPROVE, 0 CRITICAL/0 HIGH) y security-reviewer (0 CRITICAL/0 HIGH, seguro de presentar) corrieron sobre los 3 archivos tocados hoy; el único hallazgo de exactitud (market_discover) y los 4 de higiene de código ya se corrigieron. Ver §9.
---

# Reunión INDECOPI — Gerencia de Estudios Económicos (2026-08-07)

> **Nota de proceso:** este documento se preparó el 2026-08-06, un día antes de la
> reunión. Incluye tanto material ya estable (metodología, límites de datos) como
> dos entregables construidos específicamente ese día (detector de coordinación,
> audit logging reforzado). Ambos pasaron por revisión de código y seguridad
> antes de considerarse listos — ver §9. **Actualizado la tarde del 2026-08-06**
> con hallazgos adicionales de una auditoría de calidad del Golden Record — ver
> §9.5. **Actualizado la noche del 2026-08-06** con los 5 ejercicios
> demostrativos ya ejecutados y verificados contra datos reales — ver §10.
> **Actualizado el 2026-08-07 — día de la reunión** con una segunda ronda de
> correcciones de calidad de datos, dos causas raíz encontradas y corregidas
> en `cli-market-index`, ya desplegadas — ver §11. Todo lo desplegado en
> producción y verificado con evidencia real antes de agregarse aquí.

---

## 1. Tratamiento de datos — el bloque más sensible

**Naturaleza del dato.** CLI Market indexa **precios públicos de productos en
retail online** (catálogos VTEX/Magento/Shopify/WooCommerce públicos), no datos
personales de consumidores. No hay PII en el data moat. Esto es importante
aclararlo primero: "tratamiento de datos" en INDECOPI suele evocar protección de
datos personales — aquí el tema real es integridad y metodología de datos de
mercado.

**Cómo se recolecta.**
- Collector corre cada 4h contra APIs/catálogos públicos de retailers.
- Perú tiene **77 tiendas configuradas en catálogo, 67 activas** (`DEFAULT_STORES`
  filtrado por `country=PE`), cubriendo supermercados, electro, hogar,
  departamentales, moda, suplementos, belleza, papelería, flores/regalos,
  restaurantes, pet, industrial, y más.
- "Salud" de tienda = datos <24h + snapshots en ventana rolling de 7 días.
- Cobertura real es **retail digitalizado**, sesgada a Lima — no representa
  comercio informal ni todo el territorio. Decirlo de entrada, no dejar que lo
  descubran ellos.

**Qué NO es el dato** (regla de comunicación ya vigente internamente,
`docs/methodology.md`):
> "CLI Market mide precios observados en retail online indexado. No produce
> índices oficiales de inflación ni replica el IPC/INEI."

---

## 2. Metodología de indicadores

| Indicador | Fórmula (resumen) | Nota |
|---|---|---|
| **RPV** (Retail Price Velocity) | Δ% precio 7d vs 7d anterior, SKUs con ≥2 obs/ventana | No es inflación oficial |
| **BSI** (Basket Stress Index) | canasta hoy / mediana canasta 30d × 100 | 100=neutral, >105 estrés, <95 alivio |
| **CV** (Price Dispersion) | coef. variación entre tiendas | Exige ≥2 tiendas **distintas** (corregido, ver §4) |
| **Affordability Ratio** | salario mínimo / precio canasta | Variantes best/promedio/worst case |

**Regla de comparación con IPC** (`methodology.md §2`): nunca titular "brecha vs
IPC"; solo comparar contra el subíndice alimentos y bebidas, con períodos
alineados y nota metodológica visible en el mismo bloque, nunca solo en pie de
página.

---

## 3. Transparencia proactiva — limitaciones ya encontradas y corregidas

`docs/🏗️_moat_engine/data-integrity-prd.md` documenta una auditoría interna que
encontró y corrigió tres defectos reales (todos shipped, no pendientes):

1. Países sin tiendas registradas devolvían datos con apariencia válida sin
   flag de error → ahora `data_available: false` explícito.
2. El CV se calculaba con una sola tienda (mezclando varianza temporal con
   dispersión cross-retailer) → ahora exige ≥2 tiendas distintas.
3. Los scores compuestos no descontaban por frescura/cobertura → ahora cada
   score expone `confidence` (alto/medio/bajo).

Umbral de publicación: cobertura agregada ≥60% para claims públicos, si no
`[COBERTURA PARCIAL]`.

**Mensaje clave:** mostrar que hay un proceso de auditoría interna que
encuentra y corrige estos casos es mejor evidencia de rigor que no tener nada
que corregir.

---

## 4. Gap 1 — Detección de coordinación de precios (avance de hoy)

**Antes:** no existía ninguna herramienta para esto (`docs/INDECOPI_ARCHITECTURE_ANALYSIS.md`
§3.2, estimado 2-3 semanas de esfuerzo).

**Hoy:** `ops/market_coordination_detector.py` — MVP funcional, no solo diseño.
Dos señales independientes, sobre el schema real (`price_snapshots` +
`price_history`):

- **Señal A — uniformidad de precio:** CV cross-tienda anormalmente bajo
  (≤2%) entre ≥2 tiendas para el mismo producto.
- **Señal B — promociones sincronizadas:** ≥2 tiendas iniciando un descuento
  dentro de una ventana corta (48h), **recurrente** entre el mismo par de
  tiendas (una sola coincidencia no cuenta — evita confundir ruido con
  patrón).

Un producto se marca "alto riesgo" solo si ambas señales coinciden; "vigilar"
si solo una. Cada output incluye la nota metodológica: es screening
estadístico, no prueba de colusión — bots de price-matching o un MSRP común de
proveedor producen la misma firma.

### Acotado a Perú — resultado real, no sintético

Se corrió contra los datos reales de PE ya recolectados localmente (152 filas
`price_snapshots`, 498 `price_history`). Hallazgo de fondo: el enlace
`canonical_product_id` (Golden Record — vincula "Leche Gloria 1L" entre tiendas
como el mismo producto) solo estaba poblado en **2 de 152 filas**. Ese es el
cuello de botella real, independiente del país.

**Mitigación aplicada:** fallback a nombre de producto normalizado cuando no
hay `canonical_product_id`, **restringido a un país + una línea de negocio** —
seguro precisamente porque está acotado (baja probabilidad de colisión de
nombres dentro de una sola vertical en un solo país).

**Barrido por línea de negocio en PE, con datos reales:**

| Línea | Filas reales en PE | Señal encontrada |
|---|---|---|
| **Supermercados** | 101 | ✅ 1 producto en "vigilar" — Leche sin Lactosa UHT LAIVE, Makro vs Plaza Vea, CV=0% |
| Departamentales | 17 | Ninguna (datos insuficientes) |
| Belleza | 7 | Ninguna (datos insuficientes) |
| Electro | 6 | Ninguna (datos insuficientes) |
| Papelería | 6 | Ninguna (datos insuficientes) |
| Pet | 4 | Ninguna (datos insuficientes) |
| Hogar | 3 | Ninguna (datos insuficientes) |
| Moda | 3 | Ninguna (datos insuficientes) |
| Flores y regalos | 2 | Ninguna (datos insuficientes) |

Solo Supermercados tiene densidad suficiente hoy (múltiples tiendas activas:
Wong, Metro, Plaza Vea, Makro, Vega). Las demás líneas no tienen aún
superposición real entre tiendas — no es que el detector falle, es que no hay
nada que comparar todavía.

**Hallazgo colateral relevante:** correr sin filtro de línea sí produjo un
segundo "match" cruzando dos líneas de negocio distintas (un producto de bebé
en supermercados vs. departamentales) — confirma por qué restringir país+línea
es la forma segura de operar esta herramienta hoy.

**Comando para demo en vivo si lo piden:**
```bash
python3 ops/market_coordination_detector.py --demo                       # datos sintéticos, sin BD
python3 ops/market_coordination_detector.py --country PE --line supermercados  # datos reales
```

**Lo que sigue pendiente, explícitamente:**
- No es un endpoint HTTP ni tool MCP todavía — es un script. Convertirlo en
  producto (gating por tier, límites de costo, exposición vía API/MCP) es la
  siguiente etapa, no algo que se apura en un día sin meter riesgo.
- Cobertura de `canonical_product_id` sigue siendo el bloqueador estructural
  para escalar más allá de supermercados — es un problema de matching de
  productos (Golden Record), no del detector en sí.

---

## 5. Gap 2 — Audit logging regulatorio (avance de hoy)

**Antes:** logging básico de uso MCP (cliente, tool, país) vía
`mcp_tool_call`; sin IP de origen, sin correlación de request, sin outcome.

**Hoy:** en `routers/mcp_http.py`, cada llamada MCP genera dos eventos:
- `mcp_tool_call` — ahora incluye `source_ip` y `request_id`.
- `mcp_tool_result` (nuevo) — `outcome` (ok/error), `error_code`,
  `latency_ms`, mismo `request_id` para correlacionar una consulta
  institucional de inicio a fin.

Registrado en el allowlist `FUNNEL_EVENTS` de `market_funnel.py`.

**Corregido tras la revisión de seguridad (ver §9):** `market_discover` es el
único tool cuyo formato de respuesta no usa un `error` a nivel raíz (reporta
fallos anidados por sub-recurso). Sin corrección, sus fallas parciales
quedarían registradas como `outcome: "ok"` — se agregó `_result_outcome()`
para clasificar también ese caso (`outcome: "partial_error"`), de forma que
la afirmación "todo fallo queda registrado" sea cierta para los 65 tools, no
solo para la mayoría.

**Lo que sigue pendiente, explícitamente:** MFA nativo en el login/API key
sigue sin implementarse — es trabajo de infraestructura de auth que no se
apura en un día sin riesgo de romper el flujo de login existente. Tampoco hay
manejo explícito de `X-Forwarded-For`/proxy de confianza para `source_ip` —
hoy se lee `request.client.host` directo, mismo patrón ya usado en
`routers/auth.py` para rate-limiting; es una limitación pre-existente en todo
el repo, no algo que este cambio empeore, pero vale mencionarla si preguntan
por la fiabilidad de la IP registrada.

---

## 6. Si la reunión toca la arquitectura agéntica propuesta

Ver `docs/INDECOPI_ARCHITECTURE_ANALYSIS.md` (85% de alineación entre la
propuesta de 7 agentes de INDECOPI y las tools MCP existentes). Puntos clave:
qué existe hoy vs qué falta, roadmap por fases (prototipo 3 meses → core 6
meses → completo 12 meses), limitaciones de datos que no se resuelven rápido
(sin datos nutricionales, sin fechas de vencimiento).

---

## 7. Preguntas probables — respuesta corta

| Pregunta | Respuesta |
|---|---|
| ¿Esto reemplaza al IPC? | No, explícitamente no; hay reglas internas para no confundirlo (§2). |
| ¿Cómo verifican que el dato es correcto? | Freshness SLA, health por tienda, auditoría que ya encontró y corrigió 3 defectos reales (§3). |
| ¿Cobertura geográfica? | Retail digitalizado, sesgo a Lima, no informal — decirlo antes de que pregunten. |
| ¿Detectan colusión/precios coordinados? | Sí, MVP funcional hoy, acotado a PE + supermercados con datos reales; expansión a otras líneas espera mejor cobertura de matching de productos (§4). |
| ¿Seguridad/gobernanza de acceso? | API keys por tier + audit trail reforzado hoy (source IP, request_id, outcome); MFA nativo sigue pendiente (§5). |
| ¿Por qué solo supermercados? | Es la única línea con suficiente densidad de datos en PE hoy — mostrar la tabla del barrido (§4) como evidencia de honestidad metodológica. |

---

## 8. Checklist final antes de la reunión

- [x] Revisión `code-reviewer` sobre los 3 archivos tocados hoy — **APPROVE, 0 CRITICAL/0 HIGH** (ver §9)
- [x] Revisión `security-reviewer` sobre `mcp_http.py` / `market_funnel.py` — **0 CRITICAL/0 HIGH, seguro de presentar** (ver §9)
- [x] Hallazgos de ambas revisiones corregidos (ver §9)
- [x] Regresión post-corrección: `--demo` y `--country PE --line supermercados` dan resultados idénticos a antes del refactor
- [x] `python3 ops/market_coordination_detector.py --demo` corre sin errores en esta máquina, verificado 2026-08-07 (si la reunión usa una máquina distinta, repetir en 10s)
- [x] `docs/methodology.md` y `docs/🏗️_moat_engine/data-integrity-prd.md` confirmados presentes en esta máquina, 2026-08-07
- [x] Los 5 ejercicios demostrativos (`cli-market-indecopi/docs/06-EJERCICIOS-DEMOSTRATIVOS.md`) ejecutados contra datos reales — ver §10
- [x] `06-EJERCICIOS-DEMOSTRATIVOS.md` confirmado presente en esta máquina, 2026-08-07 (repo local, no está en GitHub)
- [x] Trabajo adicional del 2026-08-07 (día de la reunión) sobre calidad del Golden Record — ver §11

---

## 9.5. Actualización — calidad del Golden Record (tarde 2026-08-06)

Después de cerrar §4-§8, se hizo una auditoría separada sobre el mecanismo de
`canonical_product_id` (el mismo que §4 identifica como el cuello de botella
real para escalar el detector de coordinación más allá de supermercados).
Mismo patrón que §3: se buscó, se encontró, se corrigió — con evidencia real
de producción, no solo diseño.

**Hallazgos y correcciones, todas desplegadas y verificadas en producción:**

1. **Fallos silenciosos del pipeline de vinculación → ahora visibles.** Si el
   proceso que resuelve un producto a su Golden Record empieza a fallar,
   antes no quedaba registro; ahora hay un health-check consultable
   (`GET /index/stats`) con estado, errores consecutivos y último error.
2. **Backfill y certificación de vínculos → ahora corren de verdad.** Existían
   en el código pero nunca se ejecutaban en el ciclo real del collector
   (código muerto desde su creación). Ahora corren automáticamente cada
   ciclo.
3. **Auditabilidad por fila → nueva.** Cada snapshot vinculado ahora guarda
   *cómo* se resolvió (`match_type`: exacto/fuzzy/auto, y `match_confidence`)
   — antes no había forma de distinguir después del hecho un match exacto de
   uno dudoso.
4. **~8,750 registros con marca mal normalizada → ~99% corregidos.** Auditoría
   sobre datos reales de producción encontró marcas mal resueltas (acentos
   perdidos, sub-líneas de marca fragmentadas, etc.). Se corrigieron 16
   mapeos de marca y se re-resolvieron los snapshots afectados.
5. **Bug estructural de fondo, encontrado y corregido en la librería de
   resolución (`cli-market-index`).** De esos ~8,750, un remanente de 212
   quedaba atascado por un bug real en el motor de matching: un producto viejo
   con marca incorrecta podía "contaminar" el bucket de búsqueda de su marca
   correcta y ser reencontrado por resoluciones nuevas, heredando el ID
   incorrecto. Se diagnosticó con evidencia directa de producción, se corrigió
   la causa raíz (no solo el síntoma), se cubrió con tests de regresión, y se
   confirmó en producción que ya no puede volver a pasar para este caso.
6. **Consistencia de taxonomía entre sistemas.** Se encontró y corrigió un
   desfase entre la taxonomía de canasta básica de dos componentes internos
   (faltaba "mantequilla" como categoría; un snack frito se etiquetaba
   incorrectamente como queso).

**Por qué importa para la reunión:** si preguntan "¿cómo se aseguran de que el
Golden Record vincula correctamente el mismo producto entre tiendas?", la
respuesta ahora tiene evidencia concreta de auditoría activa, no solo diseño
en el papel — mismo argumento de §3, reforzado con un caso más reciente y más
técnico si el interlocutor pide profundidad.

---

## 9. Resultado de las revisiones de código y seguridad (2026-08-06)

Por regla propia (`code-review.md`: todo cambio de código dispara `code-reviewer`;
`security.md`: cambios de auth/logging disparan `security-reviewer`), ambos
agentes revisaron los tres archivos tocados hoy antes de dar esto por cerrado.

### `security-reviewer` — veredicto: seguro de presentar

- Sin inyección SQL: todas las queries usan `?` parametrizado; `record_funnel_event`
  serializa `meta` con `json.dumps` antes de insertar, así que ni siquiera un
  `request_id` hostil (controlado por el llamante, campo JSON-RPC `id`) puede
  romper la estructura o inyectar SQL.
- Sin fuga de credenciales: `error_code` solo lleva strings cortos fijos
  (`pro_required`, `enterprise_required`, etc.) — nunca el bearer token, nunca
  el `detail`/cuerpo de respuesta upstream.
- `source_ip` (`request.client.host`) sigue el mismo patrón ya usado en
  `routers/auth.py` para rate-limiting — no es una debilidad nueva, es
  consistente con el resto del repo. Limitación conocida y documentada: no
  hay manejo de `X-Forwarded-For`/proxy de confianza en ningún lado del
  repo, no solo aquí.
- Sin XSS: ningún dashboard actual renderiza estos campos como HTML crudo.
- Hallazgo de exactitud (no de seguridad) sobre `market_discover` — **corregido** (ver §5).

### `code-reviewer` — veredicto: APPROVE

0 CRITICAL, 0 HIGH. Edge cases (lista de tiendas vacía, canonical linkage
ausente, timestamps malformados, división por cero en CV) todos manejados
correctamente. 1 MEDIUM + 3 LOW, todos de higiene/eficiencia, no de
corrección — **los cuatro se corrigieron** en `ops/market_coordination_detector.py`:

| Hallazgo | Severidad | Corrección aplicada |
|---|---|---|
| Monkeypatch de `golden_taxonomy.get_all_stores` en `--demo` nunca se restauraba (inerte hoy, pero mala higiene si el código se reutiliza en un proceso más largo) | MEDIUM | Eliminado — el módulo ya no depende de `golden_taxonomy` tras el refactor de abajo |
| 3 escaneos redundantes de `price_snapshots` por cada corrida (`find_uniformity_flags` y `find_synchronized_promotions` recalculaban el mapa de identidad cada uno) | LOW | Consolidado en un solo `_fetch_snapshot_rows()` + `_identity_key_map()` compartido, pasado por parámetro a ambas señales |
| Rama muerta en un ternario anidado (`if stores else "''"` dentro de una expresión ya protegida por `if stores else []`) | LOW | Eliminada junto con la consolidación anterior |
| Conexión sqlite del modo `--demo` nunca se cerraba | LOW | Cerrada en el `finally` de `_run_demo()` |

**Verificación post-fix:** se re-corrieron `--demo` y `--country PE --line
supermercados` — resultados idénticos byte a byte a los reportados en §4, lo
que confirma que las correcciones fueron de higiene/eficiencia, no cambiaron
ningún comportamiento observable.

---

## 10. Actualización — ejercicios demostrativos verificados con datos reales (noche 2026-08-06)

Documento separado (`cli-market-indecopi/docs/06-EJERCICIOS-DEMOSTRATIVOS.md`,
no versionado en este repo — repo local sin git) contiene 5 prompts para
que la gerencia ejecute en vivo o revise como anexo. Los 5 se corrieron
contra datos reales de producción antes de la reunión, no solo se
diseñaron — mismo estándar de rigor que el resto de este documento.

**Resultado por ejercicio:**

| Ejercicio | Veredicto | Hallazgo |
|---|---|---|
| 1 — Coordinación GLORIA leche UHT | ✅ Ejecutado, sin señal de coordinación | Formato real 946ml (no 1L); Vivanda no vende el SKU básico (surtido premium, verificado — no es hueco de datos) |
| 2 — Concentración yogur (HHI) | ✅ Ejecutado | Encontré y corregí un defecto real en la fórmula de HHI propuesta (no sumaba 100%); con la fórmula corregida: HHI=2,174 (concentrado), Gloria 39.2% |
| 3 — Precios predatorios queso | 🔴 No ejecutable hoy, reformulado | `price_history` insuficiente para todos los candidatos revisados — ni el endpoint dedicado del sistema (`promo-detector`) puede confirmarlo. Convertido en ejemplo de que el sistema no infla conclusiones sin evidencia |
| 4 — Impacto regulatorio | 🔴 No ejecutable hoy, reformulado | El historial de precios más antiguo en toda la canasta básica es del 3 de julio de 2026 (~35 días) — insuficiente para un diseño de 30+30 días con cualquier fecha regulatoria |
| 5 — Sincronización de promociones | ✅✅ La señal más fuerte de los 5 | Plaza Vea (grupo InRetail) y Cencosud (Metro+Wong) iniciaron el mismo descuento en aceite Primor el mismo día (6-jul-2026), sostenido ~32 días — con el matiz correcto de que Metro+Wong sincronizados entre sí no es señal (misma empresa) |

**Hallazgo transversal, corrige retroactivamente los ejercicios 1-3:** el
buscador de productos (`/products/search`) tiene un parámetro `require_all`
(default `false`) que hace matching por cualquier palabra de la consulta,
no todas — sin él, "aceite primor" devolvía atún enlatado antes que aceite
de cocina. Con `require_all: true` la búsqueda es limpia y ordenable. Ya
corregido en el documento de ejercicios.

**Recomendación para la demo en vivo:** mostrar los ejercicios 1 y 5 (los
dos con señal real, ya verificados) en pantalla; presentar el 2 y el 4 ya
resueltos desde el documento; usar el 3 como ejemplo explícito de honestidad
metodológica si preguntan cómo evita el sistema fabricar conclusiones sin
evidencia suficiente.

**Por qué importa para la reunión:** refuerza el mismo argumento de §3 y
§9.5 con un caso más — y es evidencia directa de que las capacidades de
detección mencionadas en §4 (coordinación de precios) y §6 (arquitectura
agéntica) no son solo diseño: se probaron contra datos reales de
producción y arrojaron señales concretas, con sus propias limitaciones
declaradas explícitamente en vez de ocultadas.

---

## 11. Actualización — segunda ronda de calidad del Golden Record (2026-08-07, día de la reunión)

Continuación directa de §9.5: se encontraron y corrigieron dos causas raíz
adicionales en el motor de matching (`cli-market-index`), y se corrió un
barrido de re-resolución sobre datos reales de producción para aplicar
ambas correcciones retroactivamente.

**Hallazgo 1 — sobre-fusión de variantes en Golden Records viejos.**
Varios `canonical_product_id` agrupaban productos genuinamente distintos
bajo un mismo ID (ej. distintas variedades de queso, o leche vs. crema de
leche de cocina bajo el mismo ID) — Golden Records registrados antes de
que la lógica actual de diferenciación de variedades existiera, nunca
re-resueltos. Confirmado que la lógica actual **ya calcula correctamente**
un ID distinto para cada variedad — no era un bug del resolver, sino datos
viejos sin refrescar. Corregido en `cli-market-index` (PR mergeado,
issue #16).

**Hallazgo 2 — "5G" interpretado como gramos.** Bug real en la extracción
de medidas: el marcador de red celular ("3G"/"4G"/"5G", presente en casi
todo nombre de celular/tablet/router) se confundía con una medida de 5
gramos, dando pesos falsos (0.005kg) a productos electrónicos y
fusionándolos incorrectamente. Corregido en `cli-market-index` (PR
mergeado, issue #17), aprovechando que en el catálogo real la red celular
siempre se escribe en mayúscula ("5G") y los pesos reales en gramos
siempre en minúscula.

**Resultado del barrido de re-resolución (aplicado hoy, verificado en
producción, 0 errores en todos los lotes):**

| Categoría | Filas corregidas |
|---|---|
| Casos iniciales (queso/leche GLORIA) | 88 |
| Categoría A — Golden Records viejos (25 IDs) | 1,722 |
| Categoría B — celulares/telecom con "5G" (5 IDs) | 466 |
| Lote extendido (45 IDs) | 1,679 |
| Lote extendido (99 IDs, incluye marca propia "Orange" de Promart) | 3,323 |
| Bucket "Orange" (836 filas) | 836 |
| Cola larga, ronda 1 (100 IDs) | 1,617 |
| Cola larga, ronda 2 (148 IDs) | 1,924 |
| **Total** | **~11,655** |

**Por qué importa para la reunión (si preguntan por rigor metodológico o
proceso de mejora continua):** en un solo día se auditó, diagnosticó con
causa raíz confirmada (no solo síntoma), corrigió en la librería
compartida, desplegó, y aplicó retroactivamente sobre production real —
sin un solo error en ningún lote de más de 300 productos afectados. Es el
mismo patrón de rigor que §3 y §9.5 ya documentan, ahora a mayor escala.

**Nota de transparencia:** queda un caso residual conocido y documentado
(un producto Samsung con "5g" escrito en minúscula por el retailer, que
el fix de mayúscula no cubre) y una cola larga de contaminación de bajo
volumen aún sin barrer por completo — mencionarlo si preguntan si "ya está
todo arreglado": la respuesta honesta es "la mayoría del volumen real sí,
quedan casos residuales de baja frecuencia, documentados y con plan claro
para cerrarlos".
