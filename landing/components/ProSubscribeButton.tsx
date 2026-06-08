"use client";

import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import { recordFunnelEvent } from "@/lib/funnel";
import { MARKET_STATS } from "@/lib/marketStats";
import PayPalHostedButton from "@/components/PayPalHostedButton";
import LegalConsentCheckbox from "@/components/LegalConsentCheckbox";

type PaymentMethod = "paypal" | "mercadopago" | "yape" | "plin";

type ProResponse = {
  ok?: boolean;
  approve_url?: string;
  checkout_url?: string;
  payment_link?: string;
  subscription_id?: string;
  username?: string;
  auto_activate?: boolean;
  message?: string;
  detail?: string | { msg?: string }[];
  email_sent?: boolean;
  duplicate?: boolean;
  payment_method?: PaymentMethod | string;
  qr_url?: string;
  qr_reference?: string;
  amount_pen?: number;
  amount_usd?: number;
  currency?: string;
  request_id?: string;
};

const PAYMENT_METHODS: {
  id: PaymentMethod;
  label_es: string;
  label_en: string;
}[] = [
  { id: "paypal", label_es: "PayPal", label_en: "PayPal" },
  { id: "mercadopago", label_es: "Mercado Pago", label_en: "Mercado Pago" },
  { id: "yape", label_es: "Yape", label_en: "Yape" },
  { id: "plin", label_es: "Plin", label_en: "Plin" },
];

function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, "\u0026amp;")
    .replace(/</g, "\u0026lt;")
    .replace(/>/g, "\u0026gt;")
    .replace(/\"/g, "\u0026quot;")
    .replace(/'/g, "\u0026#039;");
}

function parseApiError(data: ProResponse, fallback: string): string {
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail) && data.detail[0]?.msg) return data.detail[0].msg;
  return data.message || fallback;
}

function methodLabel(method: string | undefined, isES: boolean): string {
  const found = PAYMENT_METHODS.find((m) => m.id === method);
  if (!found) return method || "";
  return isES ? found.label_es : found.label_en;
}

export default function ProSubscribeButton() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("paypal");
  const [legal, setLegal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProResponse | null>(null);
  const [error, setError] = useState("");

  const payload = () => ({
    email: email.trim(),
    username: username.trim() || undefined,
    lang: isES ? "es" : "en",
    payment_method: paymentMethod,
  });

  const submit = async () => {
    setError("");
    if (!email.trim()) {
      setError(isES ? "Ingrese su email" : "Enter your email");
      return;
    }
    if (!legal) {
      setError(
        isES
          ? "Debe aceptar los Términos y la Política de Privacidad."
          : "You must accept the Terms and Privacy Policy.",
      );
      return;
    }
    setLoading(true);
    try {
      const r = await fetch(`${API_URL}/billing/pro-checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload()),
      });
      const data: ProResponse = await r.json();

      const redirectUrl = data.approve_url || data.checkout_url || data.payment_link;
      const hasQr = Boolean(data.qr_url);

      if (r.ok && data.ok && (redirectUrl || hasQr)) {
        recordFunnelEvent("request_pro", {
          username: data.username || username.trim() || undefined,
          meta: {
            source: `landing_pro_checkout_${paymentMethod}`,
            auto_activate: data.auto_activate !== false,
            email: email.trim(),
            payment_method: paymentMethod,
          },
        });
        setResult({
          ...data,
          approve_url: redirectUrl,
        });
        setLoading(false);
        return;
      }

      setError(
        parseApiError(
          data,
          isES ? "Error al preparar el pago" : "Error preparing checkout",
        ),
      );
    } catch {
      setError(isES ? "Error de red" : "Network error");
    }
    setLoading(false);
  };

  if (result?.ok) {
    const safeUser = String(result.username || "");
    const method = result.payment_method || paymentMethod;
    const isQr = method === "yape" || method === "plin";
    const isManualHosted =
      Boolean(result.payment_link && !result.subscription_id) &&
      result.auto_activate === false &&
      !isQr;
    const redirectUrl = result.approve_url || result.checkout_url || result.payment_link;

    return (
      <div className="space-y-3 text-left">
        <div className="rounded border border-[var(--cm-mint)]/20 bg-[var(--cm-mint)]/5 p-3 text-sm text-[var(--cm-on-surface-variant)]">
          <p>
            {result.message ||
              (isQr
                ? isES
                  ? `Escanee el QR con ${methodLabel(method, true)}. Pro se activa ≤24 h tras confirmar el pago.`
                  : `Scan the QR with ${methodLabel(method, false)}. Pro activates within 24h after payment.`
                : isManualHosted
                  ? isES
                    ? "Le enviamos el link de pago. Activación manual ≤24 h tras pagar."
                    : "We sent the payment link. Manual activation within 24h after payment."
                  : method === "mercadopago"
                    ? isES
                      ? "Complete el pago en Mercado Pago — Pro se activa tras confirmación."
                      : "Complete payment on Mercado Pago — Pro activates after confirmation."
                    : isES
                      ? "Confirme en PayPal — Pro se activa en segundos (webhook)."
                      : "Confirm in PayPal — Pro activates in seconds (webhook).")}
          </p>
          {safeUser && (
            <p className="mt-1 font-mono text-[11px] text-[var(--cm-on-surface-variant)]/60">
              {isES ? "Usuario CLI" : "CLI user"}: {escapeHtml(safeUser)}
            </p>
          )}
          {result.qr_reference && (
            <p className="mt-1 font-mono text-[11px] text-[var(--cm-mint)]">
              {isES ? "Referencia" : "Reference"}: {escapeHtml(result.qr_reference)}
            </p>
          )}
          {typeof result.amount_pen === "number" && (
            <p className="mt-1 text-[11px]">
              {isES ? "Monto" : "Amount"}: S/ {result.amount_pen.toFixed(2)}
              {typeof result.amount_usd === "number" ? ` (USD ${result.amount_usd.toFixed(0)}/mo)` : ""}
            </p>
          )}
        </div>

        {isQr && result.qr_url && (
          <div className="flex flex-col items-center gap-2 rounded border border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]/40 p-4">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={result.qr_url}
              alt={isES ? `QR ${methodLabel(method, true)}` : `${methodLabel(method, false)} QR`}
              width={200}
              height={200}
              className="rounded bg-white p-2"
            />
            <p className="text-xs text-[var(--cm-on-surface-variant)]/70 text-center">
              {isES
                ? `Abra ${methodLabel(method, true)} y escanee — referencia obligatoria`
                : `Open ${methodLabel(method, false)} and scan — reference required`}
            </p>
          </div>
        )}

        {redirectUrl && !isQr && (
          <a
            href={redirectUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center text-sm font-semibold px-6 py-3 transition-colors w-full btn-mint"
          >
            {isManualHosted
              ? isES
                ? "Abrir link de pago →"
                : "Open payment link →"
              : method === "mercadopago"
                ? isES
                  ? "Pagar en Mercado Pago →"
                  : "Pay on Mercado Pago →"
                : isES
                  ? "Suscribirse en PayPal — $39/mes →"
                  : "Subscribe on PayPal — $39/mo →"}
          </a>
        )}

        <p className="text-xs text-[var(--cm-on-surface-variant)]/60 leading-relaxed">
          {isES
            ? `Pagos: ${MARKET_STATS.paymentsLabel}. Tras pagar ejecute market whoami — tier: pro.`
            : `Payments: ${MARKET_STATS.paymentsLabel}. After payment run market whoami — tier: pro.`}
        </p>

        {paymentMethod === "paypal" && (
          <details className="text-xs text-[var(--cm-on-surface-variant)]/50">
            <summary className="cursor-pointer hover:text-white">
              {isES ? "Alternativa: botón alojado PayPal" : "Alternative: PayPal hosted button"}
            </summary>
            <div className="mt-2">
              <PayPalHostedButton className="w-full" />
            </div>
          </details>
        )}
      </div>
    );
  }

  return (
    <div className="form-stack">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder={isES ? "su@email.com" : "you@email.com"}
        className="w-full input-cyber"
      />
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder={isES ? "usuario CLI (market whoami) — opcional" : "CLI username (market whoami) — optional"}
        className="w-full input-cyber text-sm"
      />

      <div className="space-y-2">
        <p className="text-[11px] text-[var(--cm-on-surface-variant)]/70">
          {isES ? "Método de pago" : "Payment method"}
        </p>
        <div className="grid grid-cols-2 gap-2">
          {PAYMENT_METHODS.map((m) => {
            const selected = paymentMethod === m.id;
            return (
              <button
                key={m.id}
                type="button"
                onClick={() => setPaymentMethod(m.id)}
                className={`text-sm px-3 py-2.5 rounded border transition-colors ${
                  selected
                    ? "border-[var(--cm-mint)] bg-[var(--cm-mint)]/10 text-white"
                    : "border-[var(--cm-outline-variant)]/40 text-[var(--cm-on-surface-variant)] hover:border-[var(--cm-mint)]/40"
                }`}
              >
                {isES ? m.label_es : m.label_en}
              </button>
            );
          })}
        </div>
      </div>

      <p className="text-[11px] text-[var(--cm-on-surface-variant)]/70 leading-relaxed rounded border border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]/50 p-2.5">
        {isES ? (
          <>
            Plan Pro: <strong>USD 39/mes</strong>. Pagos y facturación por {MARKET_STATS.paymentsLabel} — mismos
            canales que el checkout retail. Puede cancelar escribiendo a{" "}
            <a href="mailto:hello@cli-market.dev" className="text-[var(--cm-mint)] underline">
              hello@cli-market.dev
            </a>
            . Comprobantes en USD — Sinapsis Innovadora S.A.C. (RUC 20613045563).
          </>
        ) : (
          <>
            Pro plan: <strong>USD 39/mo</strong>. Billing via {MARKET_STATS.paymentsLabel} — same channels as retail
            checkout. Cancel anytime by emailing{" "}
            <a href="mailto:hello@cli-market.dev" className="text-[var(--cm-mint)] underline">
              hello@cli-market.dev
            </a>
            . USD receipts — Sinapsis Innovadora S.A.C. (tax ID 20613045563).
          </>
        )}
      </p>

      <LegalConsentCheckbox checked={legal} onChange={setLegal} includeSubscriptions />

      {error && <p className="text-xs text-[#ffb4ab]">{error}</p>}
      <button
        onClick={submit}
        disabled={loading || !legal}
        className="btn-mint w-full disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading
          ? isES
            ? "Preparando pago..."
            : "Preparing checkout..."
          : isES
            ? `Obtener Pro — ${methodLabel(paymentMethod, true)} · $39/mes`
            : `Get Pro — ${methodLabel(paymentMethod, false)} · $39/mo`}
      </button>
      <p className="text-xs text-center text-[var(--cm-on-surface-variant)]/60">
        {isES
          ? `${MARKET_STATS.paymentsLabel} · Mismos canales para suscripción Pro y checkout retail`
          : `${MARKET_STATS.paymentsLabel} · Same channels for Pro billing and retail checkout`}
      </p>
    </div>
  );
}