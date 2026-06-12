---
title: CLI Market — Pitch Agéntico
tags:
  - gtm
  - pitch
  - psp
  - investors
date: 2026-06-12
status: active
audience: Inversores · PSPs (Culqi/BCP/Niubiz) · Partners estratégicos
---

# CLI Market — Pitch Agéntico (Jun 2026)

**Versión:** 2026-06-12 · **Confidencial — uso en propuestas B2B y conversaciones estratégicas**

---

## 1. El momento — por qué esto importa ahora

El mercado está construyendo dos capas que definen el comercio de los próximos 5 años:

### Riel de pagos agénticos (resuelto)
Visa + OpenAI, Mastercard Agent Pay, PayPal ACS están estandarizando el checkout sin fricción humana. El pago ya no es el cuello de botella.

### Guerra de protocolos de descubrimiento (en curso)
| Protocolo | Respaldo | Rol |
|-----------|----------|-----|
| **ACP** | OpenAI + Stripe | Cómo los agentes encuentran y evalúan productos |
| **UCP** | Google + Shopify + Visa + Walmart | Estándar alternativo con tracción institucional |

**La consecuencia directa:** con checkout resuelto, el cuello de botella se mueve al **descubrimiento y comparación**. Los agentes necesitan saber *dónde comprar*, *a qué precio*, y *cuándo* es el mejor momento. CLI Market vive exactamente ahí.

### Señales de validación *(intel de mercado — citar fuente antes de posts públicos)*
- **~43%** de retailers globales piloteando agentes — demanda de datos normalizados, no en 2028. *[Fuente pendiente: añadir estudio/industry report antes de GTM público]*
- OpenAI Instant Checkout con adopción limitada (orden de magnitud: decenas de comercios, no cientos) — la fricción de integración es el problema real; CLI Market es el anti-fricción. *[Fuente pendiente: verificar conteo merchants ACP/Instant Checkout, corte Q2 2026]*
- Amazon ofreciendo agentes a retailers vía AWS — el retailer mediano necesita alternativa para no depender 100% de Amazon. *[Fuente pendiente: comunicado AWS/agent commerce]*

---

## 2. Qué es CLI Market

**El middleware LATAM entre los protocolos agénticos y los retailers que aún no están listos.**

| Dimensión | Dato |
|-----------|------|
| Retailers verificados activos | 38 |
| Países cubiertos | 8 |
| Precios de góndola indexados | 55,000+ |
| Frecuencia de actualización | Cada 4 horas |
| Historial disponible | Hasta 12 meses (Pro) / completo (Enterprise) |
| Herramientas MCP | 22 (curated profile) |
| Rieles de pago LATAM | PayPal · Yape · Plin |
| PyPI downloads | 27K |

Una sola API · Un schema JSON · Diseñado para mapear a ACP y UCP (MCP-native hoy; adapters de protocolo según demanda — ver `docs/STRATEGY.md`).

---

## 3. El problema que nadie más resuelve en LATAM

Falabella, Ripley, Wong, Metro, Plaza Vea **no van a implementar UCP o ACP por su cuenta.** No tienen equipos de protocolo agéntico. No tienen incentivos para hacerlo antes de que la demanda llegue masivamente.

Cuando los agentes empiecen a comprar a escala, estos retailers serán **invisibles para el ecosistema agéntico** — a menos que alguien los conecte.

CLI Market ya tiene las conexiones. Ya tiene los datos. Ya está indexando.

**El pitch cambia:** de "API de precios" a "tu retailer peruano/LATAM disponible en cualquier agente que use UCP o ACP, sin tocar tu backend."

---

## 4. Tres ventajas competitivas

### Ventaja 1 — Datos únicos en LATAM (moat irreplicable)
El archivo histórico de precios de CLI Market es imposible de replicar en 6 meses. 55,000+ precios actualizados cada 4 horas, con historial por producto. Ningún retailer publica esto públicamente. Ningún competidor tiene cobertura comparable en PE/AR/CO/CL/MX.

Los agentes no solo necesitan saber *qué* comprar — necesitan saber *cuándo* comprar. CLI Market tiene esas señales de timing.

### Ventaja 2 — Riel local de pagos (Yape/Plin)
CLI Market ya integra los rieles de pago dominantes en Perú. Cuando Visa agéntico llegue a la región, CLI Market + Yape/Plin = la propuesta local más completa para agentes que operan en Perú.

### Ventaja 3 — Schema agnóstico de protocolo
CLI Market no apuesta ni por ACP ni por UCP. Normaliza los datos una vez y los entrega en el formato que cualquier protocolo requiera. El retailer no necesita elegir un bando.

---

## 5. La oportunidad para PSPs (Culqi / BCP / Niubiz)

Cuando Visa o Mastercard agéntico llegue a Perú, el PSP que adopte primero necesitará:
1. **Riel de pago** — lo tiene el PSP
2. **Datos de retailers normalizados** — los tiene CLI Market

**La conversación correcta:**

> ¿Tu PSP quiere ser el puente entre el ecosistema agéntico global y el retail peruano? CLI Market tiene los datos. Tú tienes el riel. Juntos somos la infraestructura completa.

**El timing es crítico.** Esta conversación hay que tenerla *antes* de que Visa/Mastercard lleguen con su propio partner de datos en la región. Amazon ya está moviendo fichas.

### Acción inmediata
Mapear si Falabella, Ripley, Saga, BCP ya tienen intención de implementar UCP/ACP. Si no (probable), CLI Market es el puente — y la reunión con Dante Soto / Culqi es el primer paso.

---

## 6. Canasta Perú — señal pública del moat

El **Índice Canasta Perú** — precios de 12 productos básicos en 6 cadenas principales, actualizado semanalmente — es el activo público que demuestra que CLI Market tiene datos únicos y trazables.

Publicarlo es la primera señal para cualquier PSP, inversor o partner: el moat existe, es verificable, y nadie más lo tiene.

---

## 7. Riesgos y cómo los mitigamos

| Riesgo | Mitigación |
|--------|-----------|
| UCP gana adopción masiva → retailers grandes publican feeds directos | CLI Market está *encima* del protocolo: normaliza y conecta, no compite |
| Amazon absorbe el middleware vía AWS | Enfoque LATAM: Amazon no tiene Yape/Plin ni cobertura de retailers medianos peruanos |
| Hey Savi / PayPal en vertical fashion (UK) | Valida el modelo; CLI Market tiene ventaja de timing y datos en LATAM |

---

## 8. Prioridades de ejecución

| Urgencia | Acción |
|----------|--------|
| **Inmediato** | Usar este pitch en reunión Dante Soto (Culqi/BCP) — framing UCP/ACP middleware ✅ (PR #157) |
| **Corto plazo** | Publicar Índice Canasta Perú como señal pública del data moat |
| **Vigilancia** | Monitorear si Culqi, Niubiz o BCP mencionan "agent pay" en comunicaciones públicas |

---

## 9. Próximo paso

1. Coordinar reunión con Dante Soto (Culqi/BCP) con este framing — no solo EWA/Treevü, sino CLI Market como infraestructura agéntica para el PSP
2. Preparar demo en vivo del Índice Canasta Perú con datos verificables
3. Evaluar qué retailers LATAM son más vulnerables al argumento "necesitas estar en UCP/ACP o te vuelves invisible para agentes"

---

*CLI Market · SINAPSIS INNOVADORA S.A.C. · RUC 20613045563 · Lima, Perú*
*hello@cli-market.dev · [cli-market.dev](https://cli-market.dev)*

Ver también: [[api-positioning-es]] · [[intelligence-pilot-one-pager]] · [[data-moat-strategy]]
