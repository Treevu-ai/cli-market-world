---
title: Estilo — español LinkedIn y ops
tags:
  - linkedin
  - style
---

# Español estándar (neutro LATAM / Perú)

Copy para LinkedIn, Slack, outreach y reportes ops en **castellano estándar**, no rioplatense.

## Usar

| Contexto | Tratamiento | Ejemplo |
|----------|-------------|---------|
| CTA retailers B2B | **usted** | Registre su tienda · Complete el formulario |
| Métricas / datos | neutro | 19.452 precios indexados · 8 países |
| Preguntas engagement | tú aceptable | ¿Qué producto le gustaría comparar en PE? |
| Ortografía | RAE / LATAM | éxito · países · integración · últimas · cambió · avísenos |

## Evitar (voseo / rioplatense)

| No | Sí |
|----|-----|
| Listá tu tienda | Registre su tienda |
| Probá / probá | Pruebe |
| querés | quiera |
| avisanos | avísenos |
| cambio (sin tilde) | cambió |
| exito | éxito |
| ultimos | últimos |
| integracion | integración |
| se te trabó | se detuvo |
| soltara la tecla | soltar la tecla |

## Fuentes en repo

- Borradores: `docs/linkedin/Day-*.md`
- Regenerar: `python3 ops/generate_linkedin_days.py` (respeta este estilo en `DAYS`)
- Outreach tiendas: `ops/monday.py` → `OUTREACH_ES`
- Calendario: [[linkedin-calendar]]

[[GTM-Hub]]
