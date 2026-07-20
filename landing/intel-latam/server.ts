import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import "dotenv/config";

// CLI Market's real Data Moat — POST /v1/intel/ask runs a grounded tool-use
// agent over live intelligence data (inflation, indicators, dispersion,
// staple momentum). Requires a Starter+ API token. Never fabricate numbers
// here — if this isn't configured or the call fails, say so plainly instead
// of falling back to invented prices (that was the previous, wrong design).
const MARKET_API_URL = process.env.MARKET_API_URL || "https://cli-market-api.fly.dev";
const MARKET_API_TOKEN = process.env.MARKET_API_TOKEN || "";

// Manual Pro/Procure activation — POST /admin/activate-pro-request requires
// a real admin bearer token, so it never leaves this server. The browser
// only ever sends ADMIN_UI_PASSPHRASE (a local, low-stakes gate compared to
// the real token), checked server-side before the real API call is made.
const ADMIN_API_TOKEN = process.env.ADMIN_API_TOKEN || "";
const ADMIN_UI_PASSPHRASE = process.env.ADMIN_UI_PASSPHRASE || "";

async function askDataMoat(question: string): Promise<{ text: string; source: string }> {
  if (!MARKET_API_TOKEN) {
    return {
      text: "⚠️ Este demo aún no está conectado al Data Moat (falta MARKET_API_TOKEN). Ninguna cifra se está inventando — configura el token para ver datos reales.",
      source: "not_configured",
    };
  }
  try {
    const response = await fetch(`${MARKET_API_URL}/v1/intel/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${MARKET_API_TOKEN}`,
      },
      body: JSON.stringify({ question }),
      signal: AbortSignal.timeout(65_000), // ask_intel's own tool-use loop can take up to ~60s
    });
    if (!response.ok) {
      const detail = await response.text().catch(() => "");
      console.error(`Data Moat /v1/intel/ask returned ${response.status}: ${detail}`);
      return {
        text: `⚠️ El Data Moat respondió con un error (${response.status}). Intenta de nuevo en unos segundos.`,
        source: "error",
      };
    }
    const data = await response.json();
    return { text: data.answer || "El Data Moat no encontró una respuesta para esta consulta.", source: "data_moat" };
  } catch (error) {
    console.error("Error connecting to Data Moat:", error);
    return {
      text: "⚠️ *Error de conexión:* no se pudo alcanzar el Data Moat en este momento. Por favor intenta de nuevo.",
      source: "error",
    };
  }
}

async function startServer() {
  const app = express();
  app.use(express.json());
  const PORT = 3000;

  // API chat route — every answer comes from the real Data Moat, never fabricated.
  app.post("/api/chat", async (req, res) => {
    const { message } = req.body;
    if (!message || typeof message !== "string") {
      return res.status(400).json({ error: "Mensaje es requerido y debe ser un texto." });
    }

    const { text, source } = await askDataMoat(message.trim());
    return res.json({ text, source });
  });

  // Checkout proxy — forwards to the real CLI Market API's POST
  // /billing/build-checkout (same endpoint the production Next.js site's
  // BillingCheckoutModal uses for starter/pro/pro_annual PayPal checkout).
  // Proxied server-side, not called directly from the browser, so this
  // works the same in dev and prod regardless of CORS config on the API.
  app.post("/api/checkout", async (req, res) => {
    const { email, username, lang, plan, payment_method } = req.body || {};
    if (!email || typeof email !== "string") {
      return res.status(400).json({ ok: false, detail: "email es requerido" });
    }
    if (!plan || (plan !== "starter" && plan !== "pro" && plan !== "pro_annual")) {
      return res.status(400).json({ ok: false, detail: "plan debe ser starter, pro o pro_annual" });
    }
    try {
      const response = await fetch(`${MARKET_API_URL}/billing/build-checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          username: username || "",
          lang: lang || "es",
          plan,
          payment_method: payment_method || "paypal",
        }),
        signal: AbortSignal.timeout(30_000),
      });
      const data = await response.json();
      return res.status(response.status).json(data);
    } catch (error) {
      console.error("Error connecting to billing/build-checkout:", error);
      return res.status(502).json({ ok: false, detail: "No se pudo conectar con el checkout" });
    }
  });

  // Manual activation proxy — gated by ADMIN_UI_PASSPHRASE (checked here,
  // never sent past this server), then forwards to the real CLI Market
  // API's POST /admin/activate-pro-request using ADMIN_API_TOKEN. That
  // endpoint only accepts PRO-/PCS-/PCP-/PCB- request ids (Pro/Procure —
  // Starter has no manual override, it activates via PayPal webhook only)
  // and writes a real audit record (record_audit("activate_pro_request", ...))
  // server-side, which is the persisted evidence of activation.
  app.post("/api/activate", async (req, res) => {
    const { request_id, passphrase, force } = req.body || {};
    if (!ADMIN_UI_PASSPHRASE || !ADMIN_API_TOKEN) {
      return res.status(501).json({
        ok: false,
        detail: "Activación manual no configurada (falta ADMIN_UI_PASSPHRASE/ADMIN_API_TOKEN).",
      });
    }
    if (!passphrase || passphrase !== ADMIN_UI_PASSPHRASE) {
      return res.status(401).json({ ok: false, detail: "Passphrase incorrecta." });
    }
    if (!request_id || typeof request_id !== "string" || !/^(PRO|PCS|PCP|PCB)-/i.test(request_id.trim())) {
      return res.status(400).json({ ok: false, detail: "request_id debe ser PRO-/PCS-/PCP-/PCB-XXXXXXXX" });
    }
    try {
      const response = await fetch(`${MARKET_API_URL}/admin/activate-pro-request`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${ADMIN_API_TOKEN}`,
        },
        body: JSON.stringify({ request_id: request_id.trim().toUpperCase(), force: Boolean(force) }),
        signal: AbortSignal.timeout(30_000),
      });
      const data = await response.json();
      return res.status(response.status).json(data);
    } catch (error) {
      console.error("Error connecting to admin/activate-pro-request:", error);
      return res.status(502).json({ ok: false, detail: "No se pudo conectar con la activación." });
    }
  });

  // Configure Vite or production static file serving
  const isProduction = process.env.NODE_ENV === "production";

  if (!isProduction) {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
    console.log("Vite dev server mounted as middleware");
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
    console.log("Production static files mounted");
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
