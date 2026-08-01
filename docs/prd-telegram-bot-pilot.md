---
title: PRD — CLI Market Telegram Bot Pilot
tags:
  - product
  - prd
  - telegram
  - integrations
status: v0.6 — Core entrega coincidencia alta/media/baja; canasta verificable tras release coordinado pendiente
owner: Ricardo Cuba
created: 2026-08-01
repos: cli-market-world, cli-market-core
related:
  - routers/integrations/telegram.py
  - server_deps.py
  - tests/test_telegram_webhook_secret.py
  - tests/test_telegram_callback_buttons.py
  - tests/test_telegram_rate_limit.py
  - docs/TROUBLESHOOTING-MCP.md
  - docs/pricing-strategy.md
---

# PRD — CLI Market Telegram Bot Pilot

## TL;DR

CLI Market ya dispone de un bridge de Telegram que recibe mensajes. Para
`/buscar`, consulta `/products/search` con una clave dedicada y permite al
usuario elegir una oferta observada; para consultas abiertas mantiene
`/v1/intel/ask` bajo reglas explícitas de evidencia. Este PRD convierte ese
bridge en un producto de piloto confiable y trazable para compradores que
prefieren chat antes que CLI, API o MCP.

La primera versión no es un checkout ni una promesa de monitoreo automático.
Su trabajo es responder consultas de producto y lanzar una comparación entre
tiendas únicamente cuando la identidad del producto y la cobertura disponible
lo permiten.

**Decisión de lanzamiento:** habilitar solo para chats permitidos durante el
piloto. La apertura pública requiere presupuesto global, telemetría y revisión
de abuso aprobados.

---

## 1. Problema y oportunidad

### Problema

Operadores de compra, equipos comerciales y analistas ligeros hacen preguntas
de precio mientras están en operaciones: “¿cuánto cuesta Nescafé en Perú?” o
“compara leche Gloria entre tiendas”. Instalar una CLI o configurar MCP es una
fricción innecesaria para ese trabajo puntual.

Un bot de chat reduce esa fricción, pero una respuesta conversacional sin
evidencia puede confundir producto, presentación, retailer o fecha. El producto
debe conservar los principios de CLI Market: identidad del SKU, cobertura,
frescura y confianza antes de sugerir una acción.

### Oportunidad

Telegram puede ser una puerta de entrada de baja fricción a CLI Market y un
canal de investigación asistida para pilotos. La conversación debe llevar al
usuario de pregunta libre a una respuesta verificable, no a una afirmación
comercial sin datos.

### Personas objetivo del piloto

| Persona | Trabajo a resolver | Resultado esperado |
|---|---|---|
| Comprador operativo | Validar un precio antes de pedir cotización o reponer | Precio, tienda, frescura y caveat de cobertura |
| Analista comercial | Hacer una comparación rápida sin abrir dashboard | Comparación de equivalentes confirmados |
| Líder de piloto | Ver si el canal genera consultas resolubles y seguras | Tasa de respuesta, calidad y coste por consulta |

---

## 2. Objetivo, no objetivos y principios

### Objetivo de producto

Permitir que un usuario autorizado consulte precios de productos monitoreados y
active una comparación de tiendas desde Telegram, recibiendo una respuesta
trazable y honesta sobre sus límites.

### No objetivos de v1

- Comprar, cobrar, generar QR de pago o ejecutar checkout.
- Declarar ahorro o una “mejor tienda” cuando la canasta o identidad está
  incompleta.
- Prometer alertas de precio persistentes antes de conectar el sistema real de
  alertas y consentimiento del usuario.
- Admitir medios, notas de voz, imágenes, mensajes editados o cualquier grupo
  durante el piloto P1.
- Sustituir API, CLI o MCP para integraciones de alto volumen.

### Principios de decisión

1. **Datos antes que fluidez.** La respuesta debe preservar retailer, producto,
   presentación, fecha/cobertura y confianza cuando estén disponibles.
2. **Identidad antes que comparación.** Si no se confirma equivalencia, se pide
   aclaración; no se calcula ahorro.
3. **Piloto cerrado por defecto.** Una allowlist vacía no debe abrir tráfico
   público accidentalmente.
4. **Clave con alcance mínimo.** El tráfico del bot usa `MARKET_BOT_API_TOKEN`;
   la clave administrativa nunca se usa para usuarios regulares.
5. **Una interacción, una observación.** Cada update se reconoce una sola vez y
   su resultado queda observable, aunque falle el procesamiento posterior.

---

## 3. Estado actual y gaps

| Capacidad actual | Estado | Gap a cerrar |
|---|---|---|
| Webhook HTTPS con secreto de Telegram | Implementado | Registrar y verificar webhook en entorno de piloto |
| Consulta a inteligencia | Implementada con token dedicado | Sustituir texto por contrato completo para comparaciones |
| Búsqueda de producto | Implementado vía `/products/search`, con identidad canónica cuando existe | Confirmación de equivalencia entre retailers |
| Canasta exploratoria | Implementada vía `/v1/basket/compare`, enriquecida con snapshot | Publicar Core 1.12.4 y validar en producción |
| Comparación por botón | Implementada para la última consulta | Aislar sesión por usuario en grupos y confirmar identidad |
| Límite por chat | 20/min y 300/día por defecto | Reconocer con 2xx y comunicar límite; añadir presupuesto global |
| HTML seguro para nombre y respuesta | Implementado | Mantener pruebas de mensajes largos y respuesta vacía |
| Menú de comandos | Implementado | Verificarlo con el bot de piloto |
| Alertas de caída de precio | No implementadas en el bridge | No anunciarlas hasta tener alerta persistente y consentimiento |
| Acknowledgement del webhook | El typing se espera antes de responder | Moverlo a trabajo posterior al 200 y medir la latencia de acknowledgement |

---

## 4. Experiencia de usuario

### Flujo A — consulta de precio

1. El usuario autorizado inicia el bot o escribe una pregunta.
2. El servicio reconoce el webhook antes de cualquier llamada saliente; el bot
   muestra “Buscando…” después del acknowledgement.
3. Para búsqueda de un producto, CLI Market devuelve candidatos de catálogo y
   el usuario elige una oferta con un botón.
4. El bot muestra producto, marca, tienda, precio observado, stock y confianza
   tal como llegaron en el resultado. No presenta comparación ni ganador.
5. Si faltan marca, presentación, país o retailer, el bot pide ese dato y no
   infiere equivalencia.

**Formato actual de una oferta observada:**

```text
Nescafé Tradición 200 g
Marca: Nescafé
Tienda: Wong
Precio observado: S/ 16.90
Stock reportado: [valor de catálogo]
Confianza del registro: [valor de catálogo]
```

Si alguno de esos campos no está disponible en la fuente, se indica “Sin dato”;
no se inventan fecha, cobertura, equivalencia ni ahorro.

### Flujo B — comparación de tiendas

1. El usuario pulsa “Comparar tiendas”.
2. El bot recupera la última consulta de **ese usuario**, no la del chat.
3. Ejecuta una comparación para país y producto confirmados.
4. Responde con las ofertas equivalentes encontradas.
5. Si `items_found < items_searched`, no nombra ganador ni ahorro; pide
   corregir o completar la identidad.

### Flujo C — cotización exploratoria de canasta

1. El usuario elige segmento y envía de 2 a 20 productos, una línea por
   producto; puede anteponer la cantidad (`12 x leche Gloria 390 g`).
2. El bot consulta `/v1/basket/compare` sin TCO ni enlaces de compra.
3. Si falta un producto o ninguna tienda cubre la canasta, bloquea total,
   ahorro y recomendación; pide una especificación más precisa.
4. Si una tienda cubre todos los productos, el usuario elige la tienda y
   revisa cada coincidencia solicitada versus el nombre, marca y precio
   resueltos antes de ver el total observado.
5. El bot solo permite revisar una tienda cuando cada línea tiene
   `canonical_product_id` y `match_confidence=high`. El total sigue siendo
   exploratorio: no se presenta como cotización contractual ni como
   recomendación.

### Flujo D — límite, fallo o contenido no soportado

- Límite: “Alcanzaste el límite temporal. Inténtalo nuevamente en [ventana]”. El
  webhook se reconoce con 200 para evitar reintentos del proveedor.
- Fallo de datos: “No pude verificar precios ahora; no tomes una decisión de
  compra con esta consulta. Inténtalo más tarde.”
- Mensaje no textual: “Por ahora envíame el producto en texto, con marca y
  tamaño si lo conoces.”
- Chat no autorizado: mensaje de acceso denegado sin consultar inteligencia.

---

## 5. Requisitos funcionales

### RF-01 — onboarding y comandos

- El bot debe exponer `/start` y `/ayuda` mediante el menú de Telegram.
- `/start` debe describir búsqueda y comparación; no debe prometer alertas ni
  compras si esas capacidades no están activas.
- El mensaje inicial incluye un ejemplo con país, marca y presentación.

### RF-02 — autorización

- En modo piloto, solo procesa `TELEGRAM_ALLOWED_CHAT_IDS`.
- Un flag explícito habilita modo público; la ausencia de allowlist no cambia
  el modo piloto a público.
- `TELEGRAM_PUBLIC_MODE` empieza en `false`; solo se cambia a `true` tras la
  puerta de activación y no como sustituto de una allowlist de piloto.
- `TELEGRAM_ADMIN_CHAT_IDS` solo se usa para operaciones explícitamente
  aprobadas. Los usuarios regulares nunca heredan `MARKET_API_TOKEN`.

### RF-03 — sesión y botones

- La clave de sesión en chat privado es `telegram:{user_id}`. Si se evalúan
  grupos después de P1, debe ser `telegram:{chat_id}:{user_id}`.
- El callback usa la identidad de `callback_query.from.id`.
- Un botón solo reutiliza la última consulta válida del mismo usuario y expira
  de forma clara cuando ya no hay contexto. En P1, este requisito solo aplica
  a chats privados; los grupos permanecen deshabilitados.

### RF-04 — respuesta de datos

- El bridge conserva HTML escapado y no permite marcado inyectado por usuario
  o por modelo.
- El texto se divide de forma segura antes del límite de Telegram y maneja
  respuesta vacía con un fallback.
- La búsqueda de producto usa `/products/search` directamente y conserva solo
  campos de su respuesta: identificador, nombre, marca, tienda, precio,
  moneda, stock, confianza, hora de observación e identidad canónica cuando
  está disponible. El botón porta un índice corto; el resultado se recupera
  desde la sesión del mismo usuario.
- La cotización exploratoria usa `/v1/basket/compare` solo con
  `items_found == items_searched` y tiendas donde cada producto fue encontrado.
  Además exige identidad canónica y `match_confidence=high` por línea. El total
  se muestra después de revisar sus coincidencias; no se muestran ganador,
  ahorro ni TCO.
- El bridge no afirma tendencia, alerta, ahorro o ganador cuando el endpoint
  subyacente no entrega evidencia suficiente.

### RF-05 — límites e idempotencia

- Se mantienen límites por usuario/chat configurables.
- Cuando el límite se alcanza, el handler devuelve 200 y no agenda una
  consulta a inteligencia.
- Se registra `update_id` para no procesar dos veces una actualización
  reentregada.
- Debe existir un límite global configurable para proteger el coste de LLM.

### RF-06 — observabilidad

- Cada interacción registra: `update_id`, tipo de update, identificador de
  usuario anonimizado, resultado, latencia, estado de Telegram y estado de
  inteligencia.
- `/health` expone configuración booleana de Telegram, secreto y token de bot;
  no expone valores secretos.
- El piloto puede consultar volumen, tasa de errores, límites y latencia sin
  guardar el texto íntegro de las consultas en logs.

### Contrato mínimo de respuesta verificable

La capa de inteligencia actual devuelve texto. Antes de mostrar una comparación
como hecho, el bridge debe poder construir el siguiente contrato interno:

| Campo | Obligatorio para comparar | Regla |
|---|---|---|
| `canonical_product_id` | Sí | Identifica el producto equivalente; si falta, pedir aclaración |
| `product_name` y `presentation` | Sí | Se muestran al usuario para validar la identidad |
| `retailer`, `price` y `observed_at` | Sí | Cada oferta debe tener sus tres valores |
| `match_confidence` | Sí | Solo el nivel alto permite declarar equivalencia; otro nivel pide confirmación |
| `coverage` | Sí | Expresa tiendas solicitadas, consultadas y con oferta encontrada |
| `data_limit` | Cuando aplique | Explica ausencia de datos, historia o cobertura parcial |

La búsqueda actual cumple un subconjunto exploratorio del contrato: entrega una
oferta observada después de que el usuario la selecciona. Cuando la migración
de Golden Records está presente, `/products/search` devuelve
`canonical_product_id` y `queried_at`. Aun así, no entrega
`match_confidence` ni cobertura de equivalencia por producto, por lo que el
bot no expresa ganador, ahorro, tendencia ni comparación concluyente.

La canasta actual añade un control de cobertura. Core 1.12.4 añade
`match_confidence` por línea: `high` requiere marca/presentación específica o
un número de presentación que aparezca en el producto resuelto; una consulta
genérica como “leche” queda en `medium`. World enriquece cada línea con
`canonical_product_id`, `observed_at` y stock del snapshot cuando existen. El
bot exige ambos controles antes de permitir la revisión de un total observado.

---

## 6. Requisitos no funcionales y seguridad

| Área | Requisito |
|---|---|
| Webhook | Validar siempre `X-Telegram-Bot-Api-Secret-Token`; sin secreto, fallar cerrado |
| Coste | Clave dedicada, límite por identidad y presupuesto global; no usar token admin por fallback |
| Privacidad | Contexto por usuario; no mezclar búsquedas entre miembros de un grupo |
| Entrega | Reconocer webhook rápido; el trabajo lento se ejecuta fuera de la respuesta HTTP |
| Fiabilidad | Registrar error de API de Telegram y de inteligencia; mensajes de fallback claros |
| Contenido | Máximo y división compatible con Telegram; HTML escapado antes de formatear |
| Datos | Mostrar limitaciones de cobertura y no inferir equivalencia, ahorro o historial ausente |

### Contrato de estado efímero

| Dato | Almacenamiento y clave | Caducidad / regla |
|---|---|---|
| Sesión de chat privado | `messenger_sessions`, por `telegram:{user_id}` | 15 minutos desde la última consulta; después el botón pide reconsultar |
| Update recibido | Tabla de deduplicación, `telegram:update_id` único | 7 días; inserción atómica antes de agendar trabajo |
| Botón de comparación | Referencia a la sesión del usuario | Invalida al expirar la sesión o al cambiar la consulta |
| Límite global | Contador persistente de consultas originadas por Telegram | Ventana de 24 horas; al agotarse, responder 200 sin llamar a inteligencia |

Los valores de expiración se configuran para el piloto. Cualquier modificación
debe quedar registrada junto con el responsable y la fecha.

---

## 7. Arquitectura y contrato

```mermaid
flowchart LR
    U[Usuario autorizado] --> T[Telegram]
    T -->|Webhook + secreto| W[CLI Market /telegram/webhook]
    W --> A[Autorización y límites]
    A --> S[Sesión por chat y usuario]
    S --> P[/products/search con token de bot]
    S --> B[/v1/basket/compare con token de bot]
    S --> I[/v1/intel/ask con token de bot]
    I --> F[Formatter: evidencia, longitud y HTML seguro]
    F --> T
    W --> O[Telemetría sin contenido sensible]
```

**Secrets de despliegue:**

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET`
- `MARKET_BOT_API_TOKEN`
- `TELEGRAM_ALLOWED_CHAT_IDS`
- `TELEGRAM_ADMIN_CHAT_IDS` (solo si existe una necesidad operativa aprobada)
- `TELEGRAM_PUBLIC_MODE` (por defecto, `false`)
- límites por ventana, día y presupuesto global

No se registran ni se incluyen en documentación, chat, repositorio o cliente.

---

## 8. Métricas y criterios de éxito del piloto

La instrumentación debe permitir medir, por período y sin contenido sensible:

| Métrica | Definición | Decisión que habilita |
|---|---|---|
| Consultas autorizadas | Updates que pasan secreto, allowlist y límite | Demanda real del piloto |
| Tasa de respuesta útil | Respuestas con datos verificables / consultas autorizadas | Calidad de cobertura y resolución |
| Tasa de aclaración | Consultas que requieren marca, tamaño, país o tienda | Calidad del onboarding y del parser |
| Error de upstream | Fallos Telegram o inteligencia / consultas autorizadas | Confiabilidad técnica |
| Latencia de respuesta | Tiempo desde webhook hasta mensaje final | Experiencia de chat |
| Coste por consulta | Uso de inteligencia atribuible / consultas autorizadas | Viabilidad de expansión |
| Incidentes de aislamiento | Contexto o botón cruzado entre usuarios | Bloqueador de grupos o apertura pública |

El piloto termina con una decisión explícita: iterar, ampliar a más chats o
mantener cerrado. No se abre al público por volumen de mensajes solamente.

### Puerta de activación y salida

Antes de registrar el webhook, el responsable del piloto completa esta tabla.
Una celda vacía bloquea la activación; los valores no se infieren desde código.

| Parámetro | Valor para el piloto | Responsable | Regla de salida |
|---|---|---|---|
| Inicio y duración | Por aprobar; mínimo 10 días hábiles | Product owner | Evaluación al cierre |
| Chats privados permitidos | Por aprobar | Product owner | No habilitar grupos en P1 |
| Límite global diario | Por aprobar, en consultas de inteligencia | Operaciones | Al agotarse: 200 + mensaje de espera |
| Presupuesto de IA | Por aprobar, moneda y período explícitos | Owner financiero | Detener consultas al agotarse |
| Acknowledgement p95 | Menor a 1 segundo | Ingeniería | Corregir antes de ampliar |
| Respuesta final p95 | Menor a 40 segundos | Ingeniería | Investigar upstream antes de ampliar |
| Incidentes de aislamiento | Cero | Product + ingeniería | Bloquea grupos y apertura pública |
| Error upstream máximo | Por aprobar tras línea base | Ingeniería | Iterar o pausar piloto |

“Respuesta útil” significa una respuesta que cumple el contrato mínimo o que
explica claramente por qué no puede verificar la consulta. “Frescura” es el
valor `observed_at` de la oferta; el piloto no declara un umbral universal de
vigencia sin acordarlo por país, retailer y categoría.

---

## 9. Plan de entrega

### Fase 0 — correcciones de fiabilidad (P0)

1. Hecho: capturar el rate limit y devolver 200 con respuesta al usuario.
2. Hecho: corregir la clave de sesión de Telegram y callbacks; rechazar grupos en P1.
3. Hecho: quitar la promesa de alertas del onboarding.
4. Hecho: mover `sendChatAction` a trabajo posterior al acknowledgement, registrar errores de Telegram y dividir de forma segura mensajes largos.
5. Hecho: registrar comandos privados en español.
6. Hecho: eliminar el montaje duplicado del router de Telegram en `market_server.py`.

### Fase 1 — piloto cerrado (P1)

1. Configurar secretos, allowlist y webhook de un bot de prueba.
2. Añadir presupuesto global, idempotencia persistente por `update_id` y health
   ampliado.
3. Instrumentar métricas del piloto.
4. Ejecutar pruebas de aceptación con conversación privada y grupo de prueba.

### Fase 2 — calidad de respuesta (P2)

1. Hecho parcialmente: añadir la revisión de canasta completa antes de revelar
   su total observado, y exponer identidad canónica y observación de snapshot
   cuando ya existen en CLI Market.
2. Hecho en código, pendiente de release coordinado: normalización de tildes y
   `match_confidence` por línea en Core; World bloquea la canasta si falta
   confianza alta o identidad canónica.
3. Adaptar la comparación entre retailers a estructura de producto canónico,
   presentación, frescura y cobertura compartida.
4. Evaluar integración con alertas persistentes solo si hay consentimiento,
   cuenta asociada y datos reales de seguimiento.

---

## 10. Criterios de aceptación

### Seguridad y acceso

- Un webhook sin secreto, con secreto erróneo o sin configuración válida no
  llega a la inteligencia ni envía mensajes.
- Un chat fuera de allowlist no consume cuota de inteligencia.
- Un usuario regular no puede provocar uso de una clave administrativa.

### Experiencia y datos

- `/start` no promete capacidades ausentes.
- Una consulta de texto recibe un resultado o un fallback comprensible.
- Una respuesta superior al límite de Telegram llega completa mediante partes
  seguras o se resume con transparencia.
- El botón “Comparar tiendas” usa la consulta del usuario que lo pulsó.
- Con identidad o cobertura incompleta, el bot no declara ganador, ahorro ni
  equivalencia.

### Operación

- Al exceder cuota, Telegram recibe 200 y el usuario ve un mensaje de límite.
- Un mismo `update_id` no dispara dos consultas de inteligencia.
- El servidor devuelve acknowledgement antes de llamar a Telegram o a
  inteligencia; la métrica p95 queda por debajo del objetivo acordado.
- Health y telemetría permiten diagnosticar token ausente, error Telegram,
  error upstream y latencia sin revelar secretos o texto de usuarios.
- La suite cubre chat privado, grupo rechazado, callback, límite, mensaje
  largo, error Telegram, contenido no textual, expiración e idempotencia.

---

## 11. Riesgos y decisiones pendientes

| Riesgo o decisión | Tratamiento |
|---|---|
| Cobertura incompleta o identidad ambigua | Pedir aclaración y mostrar límites; no recomendar ganador |
| Coste LLM por uso público | Piloto cerrado, clave dedicada y presupuesto global antes de apertura |
| Reintentos de Telegram | Responder 200 tras procesar validaciones y deduplicar `update_id` |
| Fallo de BackgroundTasks tras responder | Registrar resultado; evaluar cola durable si el piloto demuestra necesidad |
| Grupos con conversaciones compartidas | P1 restringido a chat privado; habilitarlos solo tras pruebas de aislamiento |
| Alertas inexistentes | Mantener fuera de UI y copy hasta conectar backend real |
| Expansión pública | Requiere revisión de abuso, coste, soporte, privacidad y métricas del piloto |
