# Procurement Copilot — Plan de Validación

## Landing
https://procure-copilot.vercel.app

---

## Semana 1: Validación de problema (sin producto)

**Objetivo:** Confirmar que el dolor existe en al menos 5 empresas reales.

| Día | Acción | Meta |
|-----|--------|------|
| Lun | LinkedIn: buscar gerentes de operaciones/compradores en restaurantes, hoteles, farmacias, constructoras de Perú. Enviar 10 mensajes directos. | 10 DMs |
| Mar | Seguimiento a los que respondieron. Ofrecer llamada de 10 min "para entender cómo compran hoy". | 3 llamadas |
| Mié | 3 entrevistas. Preguntar: ¿cuánto tiempo pasás comprando?, ¿cuántos proveedores tenés?, ¿cómo comparás precios hoy?, ¿cuánto creés que perdés por no comparar? | 3 entrevistas |
| Jue | 2 entrevistas más. Mismo formato. | 5 entrevistas total |
| Vie | Analizar patrones: ¿todos sufren lo mismo? ¿cuánto duele en plata? | 1 informe de 1 párrafo |

**Criterio de stop/go:** Si al menos 3 de 5 dicen "esto me ahorraría X horas/semana", se avanza a Semana 2.

---

## Semana 2: MVP de papel + demos

**Objetivo:** Validar que pagarían por la solución ANTES de escribir código de integración.

| Día | Acción | Meta |
|-----|--------|------|
| Lun | Preparar un slide deck de 5 slides: problema → solución → cómo funciona → cuánto ahorrás → precio | Deck listo |
| Mar | Volver a los 5 entrevistados. Mostrar el deck. Preguntar: "¿pagarías $199/mes por esto?" | 3 respuestas |
| Mié | Si 2 dicen que sí: preparar un mockup funcional. Nada de backend real. Solo frontend con datos fake de SUS proveedores reales. | Mockup |
| Jue | Mostrar el mockup a los 2 que dijeron que sí. Preguntar: "¿cuándo empezamos?" | Compromiso verbal |
| Vie | Si al menos 1 dice "ya": construir el conector mínimo para sus 3 proveedores principales. | MVP |

**Criterio de stop/go:** 1 cliente comprometido verbalmente = avanzar a construcción real.

---

## Semana 3-4: Primer cliente pago

**Objetivo:** Facturar la primera suscripción.

| Paso | Qué | Quién |
|------|-----|-------|
| 1 | Conectar sus 3-5 proveedores reales al backend de CLI Market | Dev |
| 2 | Configurar búsqueda cross-proveedor para sus SKUs | Dev |
| 3 | Entregar dashboard simple: buscás "aceite" y ves precios de sus proveedores | Dev |
| 4 | Cobrar primera mensualidad ($199/mes) | Cliente |
| 5 | Medir ahorro real en la primera semana de uso | Ambos |

---

## Métricas de validación

| Métrica | Semana 1 | Semana 2 | Semana 4 |
|---------|----------|----------|----------|
| Entrevistas | 5 | — | — |
| Compromisos verbales | — | 1-2 | — |
| Clientes pagos | 0 | 0 | 1+ |
| Ahorro medido | 0 | 0 | >$200/mes |

---

## Lo que NO hacer

- No construir features que nadie pidió
- No automatizar todo. Dejar human-in-the-loop
- No gastar en ads. Todo es outreach manual
- No cambiar el pricing antes de facturar el primero
- No integrar ERPs hasta que el cliente lo pida

---

## Stack técnico para MVP

| Capa | Qué usamos |
|------|-----------|
| Backend | CLI Market existente (FastAPI + SQLite) |
| Frontend demo | procore-copilot.vercel.app (ya deployado) |
| Email | hello@cli-market.dev |
| CRM | Google Sheets (literal) |
| Pagos | Stripe Payment Links |

---

## Contactos fríos para empezar hoy

Buscar en LinkedIn con estos filtros:
- Cargo: "Jefe de Compras", "Gerente de Operaciones", "Procurement Manager"
- Industria: Restaurantes, Hoteles, Farmacias, Construcción
- Ubicación: Perú (Lima, Arequipa, Trujillo)
