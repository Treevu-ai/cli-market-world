# ✅ Checklist: Taller de Inteligencia de Mercados y Optimización de Compras

**Duración:** 75-90 min
**Modalidad:** Presencial o Zoom
**Audiencia:** [Módulo A — Compras] / [Módulo B — Pricing/Trade] / [Ambos]

---

## 📱 Tecnología

- [ ] Laptop con WiFi estable (o datos móviles de respaldo)
- [ ] Terminal con `market` CLI instalado y logueado (`market whoami` para confirmar)
- [ ] Pantalla compartida lista (Zoom) o proyector (presencial)
- [ ] `market doctor` corrido ANTES — confirmar 100% readiness

---

## 🔍 Verificar antes de cada sesión (el día de hoy, no una vez por siempre)

- [ ] `market compare "leche" --country PE` — funciona y muestra dispersión
- [ ] `market inflation-report --country PE` — funciona
- [ ] `market basket "leche:2" "aceite:1" --country PE` — funciona
- [ ] `market optimize "leche:1" --country PE` — funciona (fijo en cli-market-core 1.11.40, 2026-07-11; si vuelve a 500, usar `basket` como respaldo)
- [ ] Retailer scorecard + promo detector (curl, ver deck) — confirmar que responden 200
- [ ] Confirmar que `cli-market.dev/account` y `cli-market.dev/build` cargan y el checkout funciona

---

## 📄 Antes de la sesión — Pedir al prospecto

**Módulo A (Compras):**
- [ ] Su lista de compra recurrente real (5-10 productos con marca si la tienen)
- [ ] País/ciudad donde compran

**Módulo B (Pricing/Trade):**
- [ ] Su categoría o marca principal
- [ ] Tiendas donde más les importa su posicionamiento (si lo saben)

---

## 💰 Números para tener memorizados

- [ ] Procure Copilot: **desde $29/mes**, API incluida
- [ ] CLI Build Pro: **$49/mes**, API + MCP completo
- [ ] CLI Build Starter: **$9/mes** (mencionar solo si $49 se ve caro)
- [ ] Dispersión típica observada leche/aceite PE: **15-25%** entre cadenas

---

## 🎯 Información del prospecto (llenar durante la sesión)

- [ ] Nombre / empresa: _______________
- [ ] Rol (compras / pricing / trade / dirección): _______________
- [ ] Email: _______________
- [ ] Módulo dictado: [ ] A [ ] B [ ] Ambos
- [ ] Categoría/lista usada en la demo: _______________

---

## ⏱️ Timeline (ver también TALLER_INTELIGENCIA_MERCADOS.md)

```
0:00 - 0:25  | Columna común: problema + demo de dispersión
0:25 - 0:50  | Módulo específico según audiencia
0:50 - 1:05  | Módulo secundario (resumido) si aplica
1:05 - 1:20  | Ejercicio en vivo con datos del prospecto
1:20 - 1:30  | Cierre + suscripción en vivo
```

---

## 🤝 Cierre

**Si se suscribe en vivo:**
- [ ] Registro completado en `cli-market.dev/account` o `/build`
- [ ] Primera consulta corrida juntos
- [ ] Follow-up agendado a 3 días (no antes)

**Si dice "déjame pensarlo":**
- [ ] Enviar el link directo a la demo corrida (screenshot o export)
- [ ] Agendar follow-up a 3 días
- [ ] Anotar objeción real, no genérica

**Si dice que no:**
- [ ] Preguntar qué no convenció
- [ ] Anotar para mejorar el próximo taller
- [ ] Dejar la puerta abierta, sin presión

---

## 🚫 Errores a evitar

- [ ] ❌ NO asumir que `market optimize` funciona sin probarlo el mismo día — verificar siempre antes de la sesión
- [ ] ❌ NO usar el ejemplo genérico si el prospecto ya dio su lista/categoría real — siempre correr con SU dato
- [ ] ❌ NO prometer cobertura de informal/ferias — decir explícitamente que no se cubre
- [ ] ❌ NO comparar el dato con el IPC oficial como si fuera lo mismo
- [ ] ❌ NO dejar pasar más de 3 días sin follow-up si se registró

---

## 📝 Notas de la sesión

```
Empresa: _________________________
Contacto: _________________________
Módulo dictado: _________________________
Resultado:
  [ ] Se suscribió (plan: _______, $/mes: _______)
  [ ] Interesado, follow-up en ___ días
  [ ] No interesado (razón: _________________________)

Feedback del prospecto sobre el taller:
_________________________________________________
```

---

**Relacionado:** `TALLER_INTELIGENCIA_MERCADOS.md` (guion completo)
**Template version:** 1.0
