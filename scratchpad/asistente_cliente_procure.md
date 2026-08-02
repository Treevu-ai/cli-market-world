# Asistente de Cliente — Widget de Chat en Procure Copilot

Requisitos y contenido para el asistente pre-venta que hablará directo con clientes potenciales
en el sitio de Procure Copilot. A diferencia del GPT interno, este **no** vive en el GPT Builder —
va integrado vía API de OpenAI en tu propio backend, para no depender de que el visitante tenga
cuenta de ChatGPT.

**Nota de ubicación:** `procure.cli-market.dev` / `/procure` en el repo `cli-market-world` solo
hace `redirect()` a `procurecopilot.com` (ver `landing/app/procure/page.tsx` y
`landing/lib/procurePlans.ts`) — el frontend real de Procure Copilot vive en otro repo/deploy que
no tengo indexado en esta sesión. El backend de API sí es el mismo: `cli-market-api.fly.dev`.
Esta spec es válida para ese frontend externo; solo confírmame la ubicación del repo si quieres
que te ayude a implementarlo directamente.

---

## 1. Alcance (v1, ya decidido)

- **Canal:** widget de chat embebido en el sitio de Procure Copilot.
- **Función:** solo pre-venta — pitch, objeciones, cálculo de ROI, agendar prueba gratis. NO
  ejecuta búsquedas/comparaciones reales de producto (eso queda para v2, cuando el cliente ya
  esté en trial y use la app real).
- **Filosofía de venta:** la misma que ya está documentada y validada — honestidad, sin presión,
  ROI conservador, complementario al vendedor. Ver `QA_PARRILLERIA_HONESTO.md`,
  `PITCH_60SEG_PARRILLERIA.md`, `PROCURE_1PAGER_PARRILLERIA.md` (mismos archivos que usa el GPT interno).

---

## 2. Arquitectura recomendada

```
Visitante en procurecopilot.com
        │  (widget de chat, React/JS)
        ▼
POST /procure/chat  { session_id, message }      ← nuevo endpoint en tu backend FastAPI
        │
        ▼
Backend llama a OpenAI Responses API
  - system prompt (honestidad, pitch, objeciones)
  - tool: capture_lead(...)
        │
        ├─ si el modelo llama capture_lead →
        │     POST /v1/events (ya existe) con event="demo_request" + meta
        │     → dispara Slack (billing_slack.notify_funnel_event, ya existe)
        │     → aparece automáticamente en /dashboard/go-live y /dashboard/funnel
        │
        ▼
Respuesta de texto → al widget
```

**Por qué Responses API (no Assistants API, no Custom GPT):**
- Function calling determinístico: tu backend decide cuándo se ejecuta `capture_lead`, no
  depende de que el modelo "decida" invocar una Action (el mismo problema de fiabilidad que
  encontramos en el GPT interno).
- No requiere que el visitante tenga cuenta de ChatGPT.
- Reutiliza tu infraestructura de eventos/funnel ya existente — cero dashboards nuevos.

---

## 3. Backend — nuevo endpoint

### 3.1 Contrato

```
POST /procure/chat
Body: { "session_id": "uuid-v4-del-navegador", "message": "texto del visitante" }
Response: { "reply": "texto del asistente", "lead_captured": false }
```

- `session_id`: generado por el widget en el navegador (localStorage), NO requiere login.
  Se usa para encadenar turnos vía `previous_response_id` de la Responses API (guarda el mapping
  `session_id → last_response_id` en una tabla simple o en Redis/SQLite, TTL 24h).
- Rate limit por `session_id` e IP, reutilizando el patrón `check_rate_limit` que ya usas en
  `routers/funnel.py` (`check_rate_limit("funnel-events")`) — mismo mecanismo, nueva clave
  `"procure-chat"`.

### 3.2 Tool: `capture_lead`

```json
{
  "type": "function",
  "name": "capture_lead",
  "description": "Registra un lead cuando el visitante acepta la prueba gratis de 7 días o pide que le contacten.",
  "parameters": {
    "type": "object",
    "properties": {
      "nombre_negocio": { "type": "string" },
      "contacto": { "type": "string", "description": "email o teléfono/WhatsApp" },
      "tipo_negocio": { "type": "string", "description": "ej. parrillería, hotel, restaurante" },
      "nota": { "type": "string", "description": "contexto relevante de la conversación" }
    },
    "required": ["contacto"]
  }
}
```

Cuando el modelo la invoque, el backend hace lo que ya hace `POST /v1/events`:

```python
record_funnel_event(
    "demo_request",              # nuevo valor a agregar a FUNNEL_EVENTS en market_funnel.py
    username=None,
    session_id=session_id,
    meta={"contacto": ..., "nombre_negocio": ..., "tipo_negocio": ..., "nota": ..., "canal": "chat_web"},
)
```

Esto reutiliza `notify_funnel_event` (ya wireado en `routers/funnel.py:57`), así el lead te llega
a Slack igual que hoy, y el evento queda contado en `/dashboard/go-live` y `/dashboard/funnel`
sin tocar esos endpoints.

**Único cambio de código necesario:** agregar `"demo_request"` al `frozenset FUNNEL_EVENTS` en
`market_funnel.py` (ahora mismo no está — están `install`, `register`, `starter_subscribe`, etc.
pero no un evento específico de "lead capturado desde chat").

---

## 4. System prompt (backend, no expuesto al cliente)

```
Eres el asistente de Procure Copilot, hablando directo con el dueño o gerente de un pequeño
negocio (restaurante, parrillería, hotel pequeño) en Perú. NO eres un vendedor humano — sé
honesto sobre eso solo si te preguntan directamente "¿eres un bot?".

## QUÉ ES PROCURE COPILOT
Compara precios en tiempo real en Wong, Metro y Plaza Vea. Plan Starter: S/29/mes. Ahorro
conservador estimado: S/30-50/mes en abarrotes. Prueba gratis 7 días, sin tarjeta. Pago con
Yape/Plin. Cancelación inmediata sin penalidad.

## LO QUE SÍ HACE
- Compara precios de abarrotes, especias, carbón, insumos secos (NO carnes/frescos).
- Muestra la tienda más barata para cada producto, actualizado cada 4 horas.
- Alertas de precio.

## LO QUE NO HACE (dilo siempre que sea relevante, sin que te lo pregunten)
- No es delivery ni compra automática — el cliente sigue yendo a la tienda, pero informado.
- No compara tiendas pequeñas/locales, solo Wong/Metro/Plaza Vea.
- No reemplaza al vendedor/proveedor del cliente — es complementario.

## REGLAS DE HONESTIDAD (no negociables)
- Nunca exageres ("ahorra miles", "es automático", "compara todos los supermercados").
- Siempre que dan un número de ahorro, acláralo como estimado/conservador.
- Si preguntan algo que no sabes con certeza, dilo y ofrece escalar a support@cli-market.dev.
- Sin presión: el cierre es siempre "prueba 7 días gratis, sin riesgo, cancela cuando quieras".

## FLUJO DE CONVERSACIÓN
1. Si es el primer mensaje, saluda breve y pregunta qué le hace perder más tiempo comparando
   precios (empatía, no pitch de una vez).
2. Si muestra interés, explica el producto en 2-3 líneas máximo, con el ROI conservador.
3. Responde objeciones con las respuestas documentadas (banco de Q&A abajo).
4. Si acepta probar o pide que le contacten, USA la función capture_lead con los datos que
   tengas (aunque sea solo el contacto) — no sigas la conversación sin intentar capturarlo.
5. Si no quiere, no insistas: "Sin presión, aquí está el link si cambias de idea."

## BANCO DE OBJECIONES (resumen — igual al que usa el equipo humano)
- "¿Funciona con carnes?" → No, solo abarrotes/especias/carbón — es honesto decirlo.
- "¿Es automático?" → No, tú sigues yendo a la tienda, pero ya sabes dónde es más barato.
- "¿Reemplaza a mi proveedor?" → No, es complementario — ves precios, luego decides.
- "Suena a estafa" → Por eso es gratis 7 días, sin tarjeta, cancela cuando quieras.
- "¿Qué pasa con mis datos?" → Solo vemos qué buscas, no se vende a terceros, se borra a los
  30 días si cancelas.

## TONO
Cercano, en español (Perú), sin jerga corporativa. Como una conversación de WhatsApp, no un
discurso de ventas. Mensajes cortos (2-4 líneas), no párrafos largos.

## LÍMITES DUROS
- No proceses pagos ni pidas datos de tarjeta en el chat — siempre remite a
  procurecopilot.com/registro para pagar con Yape/Plin.
- No inventes funciones, planes o precios que no estén en este prompt.
- Si preguntan algo fuera de Procure Copilot, responde brevemente y redirige a support@cli-market.dev.
```

---

## 5. Requisitos del widget (frontend)

- Burbuja de chat flotante, esquina inferior derecha, visible en todas las páginas de
  `procurecopilot.com` (o al menos landing + pricing).
- `session_id` generado con `crypto.randomUUID()` y guardado en `localStorage` al abrir el
  widget por primera vez.
- Mensaje de apertura automático del asistente (no esperar a que el visitante escriba primero):
  *"Hola 👋 ¿Cuánto tiempo te toma decidir dónde comprar tus abarrotes/carbón?"*
- Botón visible "Hablar por WhatsApp" como salida directa a un humano en cualquier momento
  (mismo flujo que ya documentaste en `PITCH_60SEG_PARRILLERIA.md`).
- Nunca expongas la API key de OpenAI en el bundle del cliente — todas las llamadas pasan por
  tu backend (`POST /procure/chat`), el frontend nunca habla directo con OpenAI.
- Sanitiza cualquier HTML antes de renderizar la respuesta del asistente (aunque sea texto plano
  esperado, trátalo como no confiable — nunca uses `dangerouslySetInnerHTML` sin sanitizar).

---

## 6. Seguridad

- CORS del endpoint `/procure/chat` restringido al dominio de `procurecopilot.com` (y localhost
  en dev), no abierto (`*`).
- Rate limit por IP y por `session_id` (reutiliza `check_rate_limit`), para evitar abuso de tu
  cuota de OpenAI vía el widget público.
- El `system prompt` vive solo en el backend — nunca se manda al cliente ni se expone en el
  bundle de JS.
- Igual que con el GPT interno: si `capture_lead` falla, el asistente debe decirlo
  explícitamente ("tuve un problema guardando tu contacto, escríbeme a support@cli-market.dev")
  en vez de fingir que se registró.

---

## 7. Métricas de éxito (se miden solas via el funnel existente)

Al reusar `record_funnel_event`, estas conversiones ya aparecen en `/dashboard/go-live` y
`/dashboard/funnel` sin dashboards nuevos:

| Paso | Evento funnel |
|---|---|
| Visitante abre el widget | (opcional) nuevo evento `chat_start` |
| Acepta prueba / pide contacto | `demo_request` (nuevo) |
| Se registra de verdad | `register` (ya existe) |
| Paga Starter | `starter_subscribe` (ya existe) |

Meta de referencia (misma que usas para el pitch humano en `README_PARRILLERIA.md`):
~13% de conversión pitch→pago. Para el bot, esperar una tasa inicial más baja (10-15% de
chats → lead capturado) hasta calibrar el prompt con conversaciones reales.

---

## 8. Checklist de implementación

- [ ] Agregar `"demo_request"` a `FUNNEL_EVENTS` en `market_funnel.py`
- [ ] Nuevo endpoint `POST /procure/chat` en el backend (FastAPI, mismo patrón que `routers/funnel.py`)
- [ ] Tabla/cache `session_id → previous_response_id` con TTL 24h
- [ ] System prompt cargado desde archivo/config (no hardcodeado inline, para poder ajustarlo sin redeploy)
- [ ] Widget de chat en el frontend de `procurecopilot.com` (repo externo — confirmar ubicación)
- [ ] CORS restringido, rate limit activo
- [ ] Probado: 1 conversación completa (pitch → objeción → aceptar prueba → capture_lead dispara Slack)
- [ ] Confirmar que el lead aparece en `/dashboard/go-live` tras la prueba
