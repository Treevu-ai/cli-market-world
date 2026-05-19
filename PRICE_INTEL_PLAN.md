# Price Intelligence — Plan de Validación

## Landing
https://price-intelligence.vercel.app

---

## Semana 1: Validar demanda (sin construir nada)

**Objetivo:** Confirmar que alguien paga por datos de precios en tiempo real.

| Día | Acción | Meta |
|-----|--------|------|
| Lun | Identificar 10 compradores potenciales: hedge funds pequeños, fintechs de comparación de precios, marcas de consumo masivo, consultoras de mercado. Buscar en LinkedIn + Google. | 10 leads |
| Mar | Enviar 10 emails fríos: "Tenemos datos de precios en tiempo real de 3,760 retailers en 67 países. ¿Te sirve para algo?" | 10 emails |
| Mié | Seguimiento a los que abrieron. Ofrecer 15 min de llamada. | 3 llamadas |
| Jue | 3 entrevistas. Preguntar: ¿ya comprás datos de precios hoy?, ¿de quién?, ¿cuánto pagás?, ¿qué dato te falta? | 3 entrevistas |
| Vie | Si al menos 2 dicen "esto nos sirve": preparar un sample de datos real (10 productos, 3 países, último mes) | Sample listo |

**Criterio de stop/go:** 2 de 10 leads expresan interés real → avanzar.

---

## Semana 2: Sample data + primera venta

**Objetivo:** Cerrar la primera suscripción paga.

| Día | Acción | Meta |
|-----|--------|------|
| Lun | Preparar sample de datos: CSV con precios de 50 productos en 5 retailers de 3 países. Datos reales del último mes. | Sample entregable |
| Mar | Enviar el sample a los 2 leads interesados. Sin cobrar. | 2 entregas |
| Mié | Llamada de feedback: ¿el formato sirve?, ¿la frecuencia sirve?, ¿qué falta? | Feedback |
| Jue | Si feedback positivo: enviar propuesta formal. $499/mes. Factura por Stripe. | Propuesta |
| Vie | Cerrar primer cliente. O iterar. | 1 cliente o aprendizaje |

**Criterio de stop/go:** 1 cliente pago o feedback concreto de por qué no.

---

## Semana 3-4: Iterar

Si hay cliente: mejorar el feed según su feedback. Buscar cliente #2.

Si no hay cliente: pivotar el formato (¿quieren API en vez de CSV?, ¿quieren más frecuencia?, ¿quieren solo commodities?, ¿quieren solo un país?).

---

## Lo que NO hacer

- No construir la API completa hasta tener 3 clientes pagos
- No automatizar la recolección de datos antes de validar formato y frecuencia
- No gastar en ads
- No bajar el precio antes de recibir 5 "no" por precio

---

## Stack técnico para MVP

| Capa | Qué usamos |
|------|-----------|
| Datos | CLI Market backend existente (ya scrapea VTEX) |
| Formato entrega | CSV por email / Google Sheets compartido |
| Facturación | Stripe Payment Links |
| CRM | Google Sheets |
| Landing | price-intelligence.vercel.app |
