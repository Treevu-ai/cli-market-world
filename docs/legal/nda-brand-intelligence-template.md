---
title: NDA Template — Brand Intelligence (borrador)
tags:
  - legal
  - nda
  - brand-intelligence
status: Borrador — requiere revisión de un abogado antes de usarse con un cliente real
owner: Ricardo Cuba
created: 2026-07-06
---

# ⚠️ Aviso antes de usar este documento

Este es un **borrador de partida generado con asistencia de IA**, no asesoría legal. No lo
envíes a un cliente ni lo firmes sin que un abogado (idealmente con práctica en Perú, dado el
mercado objetivo del piloto) lo revise y adapte a la jurisdicción y al caso concreto. En
particular, revisar: definición de "información confidencial" (que cubra suficientemente los
datos de precios/alertas sin ser tan ancha que sea inejecutable), plazo de vigencia, y la
cláusula de no-cross-sharing (sección 4) — es el punto que más le importa a una agencia con
marcas competidoras como clientes.

---

# Acuerdo de Confidencialidad (NDA) — CLI Market Brand Intelligence

**Entre:** CLI Market ("el Proveedor") y **[Nombre de la Agencia/Marca]** ("el Cliente"),
en adelante conjuntamente "las Partes".

**Fecha:** [_______]

## 1. Objeto

El Proveedor entrega al Cliente acceso al servicio Brand Intelligence (monitoreo de precios,
detección de desvíos vs. PVP sugerido, y reportes periódicos) para la(s) marca(s) declaradas
por el Cliente en el onboarding. Este acuerdo regula el tratamiento confidencial de la
información que cada parte comparte con la otra en el marco de dicho servicio.

## 2. Definición de Información Confidencial

Se considera Información Confidencial, sin limitarse a:

- PVPs (precios de venta al público) sugeridos, registrados por el Cliente en el servicio.
- Alertas de desvío de precio, reportes PDF mensuales, y cualquier análisis derivado de ellos.
- Metodología propietaria de cálculo (`dispersion_score`, umbrales de alerta) en la medida en
  que no esté ya publicada en `docs/methodology-brand-intelligence.md`.
- Credenciales de acceso (API keys) y cualquier dato de configuración de cuenta.
- Términos comerciales del piloto (precio, condiciones, duración).

No se considera confidencial la información que: (a) ya sea de dominio público, (b) el
receptor ya conociera antes de recibirla, o (c) deba divulgarse por mandato legal o de
autoridad competente (notificando previamente a la otra parte cuando sea legalmente posible).

## 3. Obligaciones de las Partes

Cada parte se compromete a:

- Usar la Información Confidencial únicamente para los fines de este acuerdo.
- No divulgarla a terceros sin autorización previa por escrito de la otra parte.
- Proteger la Información Confidencial con el mismo grado de cuidado que aplica a su propia
  información sensible, y como mínimo con cuidado razonable.
- Limitar el acceso interno a las personas que lo necesiten para ejecutar el servicio.

## 4. Cláusula de no-cross-sharing (agencias con marcas competidoras)

Cuando el Cliente sea una **agencia que administra Brand Intelligence para más de una marca**,
incluyendo marcas que compiten entre sí en la misma categoría:

1. La agencia **no podrá compartir, divulgar, ni dar acceso** — directa o indirectamente,
   total o parcialmente — a los datos, alertas, reportes o insights generados para la Marca A
   con ninguna persona, equipo, o sistema que trabaje para la Marca B (o viceversa), cuando A
   y B sean marcas competidoras dentro del servicio.
2. El acceso técnico ya está segregado por diseño: cada marca opera en un silo separado
   identificado por `brand_slug` + `api_key` propios, sin acceso cruzado entre marcas distintas
   dentro de la plataforma.
3. La agencia designará, para cada marca cliente, un equipo o responsable distinto cuando
   existan marcas competidoras entre sus cuentas gestionadas, y documentará internamente esa
   separación (murallas chinas / "ethical wall").
4. El incumplimiento de esta cláusula es causal de terminación inmediata del servicio para
   todas las marcas de la agencia involucradas, sin perjuicio de otras acciones legales que
   correspondan.

## 5. Duración

Este acuerdo entra en vigor en la fecha de firma y las obligaciones de confidencialidad
permanecen vigentes por **[24 meses]** después de finalizado el servicio, salvo que la
naturaleza de la información (p. ej. metodología propietaria) justifique un plazo mayor.

## 6. Excepciones

Ninguna parte será responsable por divulgación de Información Confidencial cuando:

- Sea requerida por orden judicial o autoridad competente (con notificación previa razonable
  a la otra parte cuando sea legalmente posible).
- Sea necesaria para hacer valer los derechos de una parte bajo este acuerdo.

## 7. Jurisdicción

Este acuerdo se rige por las leyes de la República del Perú. Cualquier controversia derivada
de su interpretación o cumplimiento se someterá a los jueces y tribunales de Lima, Perú, salvo
que las partes acuerden expresamente arbitraje.

---

**Por el Proveedor**

Nombre: ______________________  Firma: ______________________  Fecha: __________

**Por el Cliente**

Nombre: ______________________  Firma: ______________________  Fecha: __________
