import { useEffect, useState } from "react";
import { X, Loader2 } from "lucide-react";

/**
 * Real checkout — POSTs to our own /api/checkout, which proxies to the CLI
 * Market API's POST /billing/build-checkout (same endpoint the production
 * Next.js site's BillingCheckoutModal uses). No fabricated success states:
 * the redirect link only appears once the real API confirms a PayPal
 * approve_url.
 */

type Plan = "starter" | "pro";

type CheckoutResult = {
  ok?: boolean;
  approve_url?: string;
  payment_link?: string;
  request_id?: string;
  detail?: string | { msg?: string }[];
  message?: string;
};

function parseApiError(data: CheckoutResult, fallback: string): string {
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail) && data.detail[0]?.msg) return data.detail[0].msg;
  return data.message || fallback;
}

export default function CheckoutModal({
  open,
  onClose,
  plan,
}: {
  open: boolean;
  onClose: () => void;
  plan: Plan;
}) {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [legal, setLegal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [checkoutHref, setCheckoutHref] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setEmail("");
    setUsername("");
    setLegal(false);
    setError("");
    setCheckoutHref(null);
  }, [open, plan]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const planLabel = plan === "starter" ? "Starter ($9/mes)" : "Pro ($39/mes)";

  const submit = async () => {
    setError("");
    if (!email.trim() || !email.includes("@")) {
      setError("Ingresa un email válido");
      return;
    }
    if (plan === "pro" && !username.trim()) {
      setError("Usuario CLI requerido — el de `market whoami`");
      return;
    }
    setLoading(true);
    try {
      const resolvedUsername =
        username.trim() ||
        email.split("@")[0].replace(/[^a-z0-9_-]/gi, "").slice(0, 32);
      const r = await fetch(`${import.meta.env.BASE_URL}api/checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email.trim(),
          username: resolvedUsername,
          lang: "es",
          plan,
          payment_method: "paypal",
        }),
      });
      const data = (await r.json()) as CheckoutResult;
      const href = data.approve_url || data.payment_link;
      if (r.ok && data.ok && href) {
        setCheckoutHref(href);
      } else {
        setError(parseApiError(data, "Error al preparar el pago"));
      }
    } catch {
      setError("Error de red al conectar con el checkout");
    }
    setLoading(false);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="checkout-modal-title"
    >
      <div className="w-full max-w-md rounded-sm border border-white/10 bg-[#0a0a0a] shadow-2xl">
        <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
          <h2 id="checkout-modal-title" className="text-sm font-bold text-white font-mono uppercase tracking-wider">
            Checkout · {planLabel}
          </h2>
          <button type="button" onClick={onClose} aria-label="Cerrar" className="text-white/40 hover:text-white">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="px-5 py-5 space-y-4">
          {checkoutHref ? (
            <div className="space-y-4 text-left">
              <p className="text-sm text-white/70">
                Listo — confirma el pago en PayPal para activar tu plan {plan === "starter" ? "Starter" : "Pro"}.
              </p>
              <a
                href={checkoutHref}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full inline-flex items-center justify-center rounded-sm bg-[#bef264] text-black py-3 px-4 text-xs font-mono font-bold uppercase tracking-widest hover:bg-[#d9f99d] transition-all"
              >
                Ir al pago en PayPal →
              </a>
              <button type="button" onClick={onClose} className="w-full text-xs text-white/40 hover:text-white">
                Cerrar
              </button>
            </div>
          ) : (
            <>
              <input
                type="email"
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu@email.com"
                className="w-full bg-white/5 border border-white/10 rounded-sm py-2.5 px-4 text-xs font-mono text-white placeholder-white/30 focus:outline-none focus:border-[#bef264]"
              />
              <div className="space-y-1">
                <label htmlFor="checkout-username" className="text-[10px] text-white/40 font-mono uppercase tracking-wider">
                  Usuario CLI {plan === "starter" ? "(opcional)" : ""}
                </label>
                <input
                  id="checkout-username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="market whoami"
                  className="w-full bg-white/5 border border-white/10 rounded-sm py-2.5 px-4 text-xs font-mono text-white placeholder-white/30 focus:outline-none focus:border-[#bef264]"
                />
              </div>
              <label className="flex items-start gap-2 text-[11px] text-white/50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={legal}
                  onChange={(e) => setLegal(e.target.checked)}
                  className="mt-0.5"
                />
                <span>Acepto los Términos de Servicio y la facturación recurrente vía PayPal.</span>
              </label>
              {error && <p className="text-xs text-red-400">{error}</p>}
              <button
                type="button"
                onClick={() => void submit()}
                disabled={loading || !legal}
                className="w-full inline-flex items-center justify-center gap-2 rounded-sm bg-[#bef264] text-black py-3 px-4 text-xs font-mono font-bold uppercase tracking-widest hover:bg-[#d9f99d] transition-all disabled:opacity-40"
              >
                {loading && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                {loading ? "Preparando…" : "Continuar en PayPal →"}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
