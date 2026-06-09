# Journey de pago — versión cliente

Texto listo para pegar en emails, `#contact` o confirmación post-pago. Sin pasos internos de ops.

---

## Diagrama (cliente)

```mermaid
flowchart TB
  A[Instalar CLI Market] --> B[Cuenta free]
  B --> C{¿Qué necesitas?}
  C -->|Integrar API/MCP en tu agente| D[Build Pro — tab Build]
  C -->|Compras de empresa con aprobaciones| E[Procure — tab Procure]
  D --> F[Modal: método de pago + email]
  E --> G[Modal: PayPal + email]
  F --> H{Pago}
  H -->|PayPal o Mercado Pago| I[Confirmar en el proveedor]
  H -->|Yape o Plin| J[Transferir desde la app con ref PRO-xxx]
  I --> K[Pro activo en minutos]
  J --> L[Pro activo en hasta 24 h]
  K --> M[market whoami → usar API]
  L --> M
  G --> N[PayPal Procure]
  N --> O[Pegar API key en dashboard Procure]
```

---

## Paso a paso — Build Pro (desarrolladores / agentes)

### 1. Instalar y crear cuenta

```bash
python -m pip install cli-market-world
market init           # registra cuenta + primera búsqueda guiada
market whoami         # tier: free · copia username
```

### 2. Suscribirse en la web

1. Abre [cli-market.dev/#pricing](https://cli-market.dev/#pricing) → tab **Build**
2. **Configurar Pro** → paso 1: elige método de pago y acepta términos
3. Paso 2: email + **usuario CLI** (el de `market whoami`)
4. Sigue las instrucciones en pantalla

### 3. Pagar

| Método | Qué haces tú |
|--------|----------------|
| **PayPal** | Clic en «Ir al pago» → aprueba la suscripción en PayPal |
| **Mercado Pago** | Redirige a MP → paga en soles (PEN) |
| **Yape / Plin** | Abre la app → transfiere al número indicado → monto exacto → mensaje: `PRO-XXXXXXXX` |

### 4. Confirmación

| Método | Cuándo está activo |
|--------|-------------------|
| PayPal / Mercado Pago | Unos minutos (automático) |
| Yape / Plin | Hasta 24 h hábiles tras confirmar el pago |

Verifica:

```bash
market whoami    # tier: pro
```

### 5. Usar Pro

```bash
market search "arroz" --country PE
market account                 # tier, uso y API keys
market checkout --payment yape # checkout retail (Pro)
```

MCP: `market-mcp` con `MCP_TOOL_PROFILE=default` — ver [cli-market.dev/docs](https://cli-market.dev/docs)

---

## Paso a paso — Procure (equipos de compras)

1. [cli-market.dev/#procure](https://cli-market.dev/#procure) → elige plan → **Suscribir**
2. Modal: email + usuario CLI → **Continuar — PayPal**
3. Aprueba la suscripción en PayPal
4. Crea credenciales si aún no las tienes:

```bash
market init        # o market register si solo necesitas credenciales
market account     # copia sk-… (o la que recibiste en register)
```

5. Abre el [dashboard Procure](https://procure-copilot.contacto-8e4.workers.dev) y pega tu API key

No necesitas Build Pro aparte: la API va incluida en Procure Pro+.

---

## Email post-pago — Yape/Plin (copiar/pegar)

**Asunto:** CLI Market Pro — recibimos tu solicitud (`PRO-XXXXXXXX`)

Hola,

Gracias por tu pago con Yape/Plin. Para activar **Build Pro**:

1. Confirma que transferiste **S/ [monto]** con referencia **`PRO-XXXXXXXX`** en el mensaje.
2. Cuando activemos tu cuenta (≤24 h hábiles), corre:

```bash
market whoami
```

Deberías ver `tier: pro`. Luego:

```bash
market search "leche" --country PE
market checkout --payment yape
```

Si aún no tienes cuenta:

```bash
pip install cli-market-world
market init
```

Usa el mismo **usuario CLI** que indicaste al suscribirte (`market whoami`).

¿Dudas? Responde a este email con tu ref `PRO-XXXXXXXX`.

— CLI Market · hello@cli-market.dev

---

## Email post-pago — PayPal / Mercado Pago (copiar/pegar)

**Asunto:** CLI Market Pro — suscripción confirmada

Hola,

Tu suscripción **Build Pro** debería estar activa en minutos.

Verifica:

```bash
pip install cli-market-world
market init
market whoami
```

`tier: pro` → listo para API, MCP y checkout.

Documentación: [cli-market.dev/docs](https://cli-market.dev/docs)

— CLI Market · hello@cli-market.dev

---

## FAQ rápido (cliente)

**¿Necesito Build Pro y Procure?**  
Solo si eres developer *y* operador de compras. Procure Pro+ ya incluye la API.

**¿Dónde pago Procure con Yape?**  
Procure hoy solo vía PayPal en la web. Yape/Plin aplica a **Build Pro**.

**¿Stripe?**  
No disponible aún. Usa PayPal, Mercado Pago o Yape/Plin (Build).

**¿Olvidé mi usuario CLI?**  
El email de confirmación y la ref `PRO-xxx` vinculan tu pago. Escribe a hello@cli-market.dev.