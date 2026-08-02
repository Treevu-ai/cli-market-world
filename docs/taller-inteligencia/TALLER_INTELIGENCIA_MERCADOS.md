# 🎓 Taller: Inteligencia de Mercados y Optimización de Compras

**Objetivo:** Que el prospecto vea, en vivo, el dato real detrás de una decisión de compra o de pricing que hoy toma a ciegas — y se suscriba ahí mismo.
**Formato:** Sirve para dictar en vivo (75-90 min, presencial o Zoom) o dejar como material de autoservicio.
**Audiencia:** Dos perfiles con una columna vertebral común y un módulo específico cada uno:
- **Módulo A** — category/compras managers de negocios con compra recurrente (retail, F&B, hotelería, oficinas).
- **Módulo B** — equipos de pricing / trade marketing de marcas grandes de consumo masivo.

**CTA de cierre:** suscripción self-serve, no propuesta 1:1.
- Módulo A → **Procure Copilot desde $29/mes** (cli-market.dev/account)
- Módulo B → **CLI Build Pro $49/mes** (API + MCP completo, checkout directo)

---

## Timeline (90 min)

```
0:00 - 0:25  | Columna común: el problema + la prueba en vivo
0:25 - 0:50  | Módulo A (compras) o Módulo B (pricing/trade) — según audiencia
0:50 - 1:05  | El otro módulo, versión resumida (10-15 min) — si la audiencia es mixta
1:05 - 1:20  | Ejercicio en vivo con el caso del prospecto
1:20 - 1:30  | Cierre + suscripción en vivo
```

Si la audiencia es de un solo perfil, salta el módulo que no aplica y usa ese tiempo para el ejercicio en vivo.

---

## Columna común (25 min) — El problema y la prueba

### El problema (5 min)

> "Hoy, una decisión de compra o de pricing en LATAM se toma con tres tipos de datos malos:
> encuestas trimestrales, el IPC oficial con 1-2 meses de rezago, o lo que dice el proveedor por teléfono.
> Ninguno de los tres te dice qué pasó esta semana en la góndola."

Preguntar a la audiencia: *"¿Cuándo fue la última vez que supiste, con certeza, cuánto subió el precio de tu categoría esta semana — no este trimestre?"*

### Qué es inteligencia de mercado real (5 min)

- Precios observados directamente en tiendas online (VTEX, Shopify, Magento, WooCommerce) — no encuestas, no paneles.
- Refresco cada 4 horas, no cada trimestre.
- Cobertura declarada honestamente: **si no lo medimos, lo decimos** — nunca se inventa un número de "economía informal" o de tiendas no cubiertas.

### Demo en vivo #1 — Dispersión de precio (10 min)

```
market compare "leche" --country PE
market compare "aceite" --country PE
```

Mostrar en vivo cómo el mismo producto varía 15-25% entre Wong, Metro y Plaza Vea — sin que nadie lo sepa a menos que lo mida.

> "Esto que acaban de ver — la diferencia entre pagar de más o comprar bien — es el mismo dato que van a usar en los próximos 20 minutos, pero aplicado a lo que ustedes compran o venden."

### Honestidad de datos (5 min)

Mostrar en vivo el disclaimer real que devuelve la herramienta:

```
market inflation-report --country PE
```

Señalar explícitamente: *"internal_inflation_pct: X% — no equivalente al IPC oficial, distinta canasta y metodología"*. Esa honestidad metodológica es lo que hace creíble todo lo que sigue — no es un truco de venta, es la razón por la que estos números se pueden defender frente a Finance o Compras.

---

## Módulo A — Compras / Category Managers (20-25 min)

**Para quién:** el que decide dónde y cuándo comprar la canasta recurrente del negocio.

### Caso de uso

> "Ya vimos que el mismo producto varía 15-25% entre tiendas. La pregunta real es: ¿tu canasta completa — no un producto — está comprada en el lugar correcto, en el momento correcto?"

### Demo en vivo #2 — Optimizar la canasta (10 min)

```
market optimize "leche:4" "aceite:2" "arroz:2" --country PE
```

o, con la lista real del prospecto (formato `producto:cantidad`, separados por espacio):

```
market optimize "<item1>:<cant>" "<item2>:<cant>" --country PE --budget <presupuesto>
```

Mostrar: recomendación buy_now/wait, TCO real (góndola + delivery), y presupuesto restante — no solo comparar precio, sino decidir si es buen momento para comprar.

Si por algo `market optimize` no responde, `market basket "<items>" --country PE` da la comparativa de canasta sin la capa de afordabilidad/timing — respaldo válido, versión más simple.

### Alertas de precio (5 min)

```
market price-alerts "<producto clave del prospecto>" --threshold-pct 5
```

> "No tienen que estar revisando precios todos los días. La herramienta les avisa cuando conviene comprar."

### Cierre Módulo A

- **Procure Copilot desde $29/mes** — API incluida, sin tarjeta para probar 7 días.
- Ir en vivo a `cli-market.dev/account`, registrar con el email del prospecto, primera búsqueda juntos.

---

## Módulo B — Pricing / Trade Marketing de marcas (20-25 min)

**Para quién:** el que necesita saber cómo se comporta su categoría/marca frente a la competencia, retailer por retailer.

### Caso de uso

> "Ya vimos que hay 15-25% de dispersión entre tiendas. Para un equipo de pricing eso no es curiosidad — es margen que un competidor te está quitando, o margen que estás dejando sobre la mesa."

### Demo en vivo #3 — Retailer Scorecard + integridad promocional (12 min)

> **Nota para quien dicta el taller:** estas dos capacidades todavía no tienen wrapper en el CLI de `market` (solo API/MCP por ahora) — usar `curl` o el tool MCP directo, no un comando `market` que no existe.

```bash
TOKEN=$(cat ~/.market/session.json | python -c "import json,sys; print(json.load(sys.stdin)['token'])")

curl -s -H "Authorization: Bearer $TOKEN" \
  "https://cli-market-api.fly.dev/v1/intel/retailer-scorecard?store=wong"
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://cli-market-api.fly.dev/v1/intel/retailer-scorecard?store=metro"
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://cli-market-api.fly.dev/v1/intel/retailer-scorecard?store=plazavea"
```

Mostrar cobertura de catálogo, calidad de datos, disponibilidad y competitividad de precio cruzado — lado a lado.

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://cli-market-api.fly.dev/v1/intel/promo-detector?product=<categoría del prospecto>&days=30"
```

> "Esto revisa si el retailer está inflando el precio de lista antes de anunciar un 'descuento'. Si nunca lo midieron, están confiando en el número que el retailer les da."

Si el prospecto ya usa Claude/Cursor con el MCP de CLI Market conectado, es más natural pedirle a un agente `market_retailer_scorecard` / `market_promo_detector` en lenguaje natural en vez de mostrar `curl` — usar lo que dé mejor impresión según el público.

### Acciones por área (8 min)

Presentar el formato de "Acciones sugeridas" (Pricing / Trade Marketing / Ventas / Compras / Dirección General) usando datos reales de la categoría del prospecto — el mismo formato del *Weekly Market* de CLI Market Intelligence.

### Cierre Módulo B

- **CLI Build Pro $49/mes** — API + MCP completo, checkout directo, sin llamada de ventas.
- Ir en vivo a `cli-market.dev/build`, registrar, generar la primera API key juntos.

---

## Ejercicio en vivo (15 min)

Pedir con anticipación (ver checklist de demo):
- **Módulo A:** su lista de compra recurrente real (5-10 productos).
- **Módulo B:** su categoría o marca principal.

Correr la demo correspondiente EN VIVO con sus datos reales, no con el ejemplo genérico. El momento en que ven su propio número es el que convierte.

---

## Cierre común (10 min)

> "Todo lo que vieron hoy no es un reporte que alguien preparó para esta llamada — es lo mismo que está disponible 24/7 vía CLI, API o MCP. No necesitan agendar otra reunión para volver a verlo."

**CTA en vivo, sin fricción:**
1. Abrir `cli-market.dev/account` (Módulo A) o `cli-market.dev/build` (Módulo B) en pantalla compartida.
2. Registrar con el email del prospecto, ahí mismo.
3. Correr la primera búsqueda/consulta juntos.
4. Agendar follow-up a 3 días (no antes — dejar que prueben solos primero).

---

## Qué SÍ hace / qué NO hace (decir siempre, sin que pregunten)

- **SÍ** cubre retail formal online (VTEX, Shopify, Magento, WooCommerce) en los países soportados.
- **NO** cubre ferias, mercados de abastos ni venta ambulante — y lo decimos explícitamente en cada respuesta, no lo escondemos.
- **NO** reemplaza el IPC oficial ni encuestas de hogares — es una señal de góndola online, complementaria, no un sustituto.
- **SÍ** se refresca cada 4 horas — no es una foto vieja de hace un mes.

---

**Preparado para:** Taller de venta self-serve, CLI Market
**Relacionado:** `docs/parrilleria/` (consultoría 1:1 por vertical), `docs/consultoria/` (propuestas personalizadas)
**Template version:** 1.0
