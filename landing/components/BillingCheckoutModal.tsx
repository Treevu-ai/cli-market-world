"use client";

import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import { recordFunnelEvent } from "@/lib/funnel";
import { MARKET_STATS } from "@/lib/marketStats";
import LegalConsentCheckbox from "@/components/LegalConsentCheckbox";
import PayPalHostedButton from "@/components/PayPalHostedButton";
import type { ProcurePlanSlug } from "@/lib/procurePlans";
import { PROCURE_PLANS } from "@/lib/procurePlans";

type PaymentMethod = "paypal" | "mercadopago" | "yape" | "plin";

export type BillingCheckoutKind =
  | { type: "build-pro" }
  | { type: "procure"; plan: ProcurePlanSlug };

const PAYMENT_METHODS: { id: PaymentMethod; label_es: string; label_en: string }[] = [
  { id: "paypal", label_es: "PayPal", label_en: "PayPal" },
  { id: "mercadopago", label_es: "Mercado Pago", label_en: "Mercado Pago" },
  { id: "yape", label_es: "Yape", label_en: "Yape" },
  { id: "plin", label_es: "Plin", label_en: "Plin" },
];

type CheckoutResult = {
  ok?: boolean;
  approve_url?: string;
  checkout_url?: string;
  payment_link?: string;
  message?: string;
  detail?: string | { msg?: string }[];
  username?: string;
  payment_method?: string;
  qr_url?: string;
  qr_reference?: string;
  amount_pen?: number;
  amount_usd?: number;
  auto_activate?: boolean;
  subscription_id?: string;
};

function parseApiError(data: CheckoutResult, fallback: string): string {
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail) && data.detail[0]?.msg) return data.detail[0].msg;
  return data.message || fallback;
}

function methodLabel(method: string | undefined, isES: boolean): string {
  const found = PAYMENT_METHODS.find((m) => m.id === method);
  if (!found) return method || "";
  return isES ? found.label_es : found.label_en;
}

export default function BillingCheckoutModal({
  open,
  onClose,
  kind,
}: {
  open: boolean;
  onClose: () => void;
  kind: BillingCheckoutKind;
}) {
  const { lang } = useLang();
  const isES = lang === "es";
  const isPro = kind.type === "build-pro";
  const procureMeta = !isPro ? PROCURE_PLANS.find((p) => p.slug === kind.plan) : null;

  const [step, setStep] = useState<1 | 2 | "done">(1);
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("paypal");
  const [legal, setLegal] = useState(false);
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<CheckoutResult | null>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKey);
    };
  }, [open, onClose]);

  useEffect(() => {
    if (!open) {
      setStep(1);
      setLegal(false);
      setEmail("");
      setUsername("");
      setError("");
      setResult(null);
      setPaymentMethod("paypal");
    }
  }, [open, kind]);

  if (!open) return null;

  const title = isPro
    ? isES
      ? "Build Pro — USD 39/mes"
      : "Build Pro — USD 39/mo"
    : isES
      ? `Procure ${procureMeta?.name ?? kind.plan} — USD ${procureMeta?.price ?? ""}/mes`
      : `Procure ${procureMeta?.name ?? kind.plan} — USD ${procureMeta?.price ?? ""}/mo`;

  const submit = async () => {
    setError("");
    if (!email.trim() || !email.includes("@")) {
      setError(isES ? "Ingrese un email válido" : "Enter a valid email");
      return;
    }
    setLoading(true);
    try {
      if (isPro) {
        const r = await fetch(`${API_URL}/billing/pro-checkout`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: email.trim(),
            username: username.trim() || undefined,
            lang: isES ? "es" : "en",
            payment_method: paymentMethod,
          }),
        });
        const data: CheckoutResult = await r.json();
        const redirectUrl = data.approve_url || data.checkout_url || data.payment_link;
        const hasQr = Boolean(data.qr_url);
        if (r.ok && data.ok && (redirectUrl || hasQr)) {
          recordFunnelEvent("request_pro", {
            username: data.username || username.trim() || undefined,
            meta: {
              source: `landing_checkout_modal_${paymentMethod}`,
              auto_activate: data.auto_activate !== false,
              email: email.trim(),
              payment_method: paymentMethod,
            },
          });
          setResult({ ...data, approve_url: redirectUrl });
          setStep("done");
          setLoading(false);
          return;
        }
        setError(parseApiError(data, isES ? "Error al preparar el pago" : "Error preparing checkout"));
      } else {
        const r = await fetch(`${API_URL}/billing/procure-subscribe`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: email.trim(),
            username: username.trim() || undefined,
            plan: kind.plan,
            lang: isES ? "es" : "en",
          }),
        });
        const data = (await r.json()) as CheckoutResult;
        if (r.ok && data.ok && data.approve_url) {
          window.location.assign(data.approve_url);
          return;
        }
        if (r.ok && data.ok) {
          setResult(data);
          setStep("done");
          setLoading(false);
          return;
        }
        setError(
          parseApiError(data, isES ? "Error al iniciar suscripción" : "Subscription error"),
        );
      }
    } catch {
      setError(isES ? "Error de red" : "Network error");
    }
    setLoading(false);
  };

  const renderSuccess = () => {
    if (!result?.ok) return null;
    const method = result.payment_method || paymentMethod;
    const isQr = method === "yape" || method === "plin";
    const redirectUrl = result.approve_url || result.checkout_url || result.payment_link;

    return (
      <div className="space-y-4 text-left">
        <p className="text-sm text-[var(--cm-on-surface-variant)]">{result.message}</p>
        {isQr && result.qr_url && (
          <div className="flex flex-col items-center gap-2 rounded border border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]/40 p-4">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={result.qr_url} alt="QR" width={200} height={200} className="rounded bg-white p-2" />
          </div>
        )}
        {redirectUrl && !isQr && (
          <a href={redirectUrl} target="_blank" rel="noopener noreferrer" className="btn-mint w-full inline-flex justify-center">
            {isES ? "Ir al pago →" : "Go to payment →"}
          </a>
        )}
        <button type="button" onClick={onClose} className="w-full text-sm text-[var(--cm-on-surface-variant)] hover:text-white">
          {isES ? "Cerrar" : "Close"}
        </button>
      </div>
    );
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center p-0 sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="billing-checkout-title"
    >
      <button
        type="button"
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        aria-label={isES ? "Cerrar" : "Close"}
        onClick={onClose}
      />
      <div className="relative w-full sm:max-w-md max-h-[92dvh] overflow-y-auto rounded-t-2xl sm:rounded-2xl border border-[var(--cm-outline-variant)]/40 bg-[var(--cm-surface-low)] shadow-[0_0_48px_rgba(200,255,0,0.06)]">
        <div className="sticky top-0 z-10 flex items-center justify-between gap-3 border-b border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]/95 backdrop-blur-md px-5 py-4">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-widest text-[var(--cm-action)] mb-1">
              {isES ? "Paso" : "Step"} {step === "done" ? "✓" : step} / 2
            </p>
            <h2 id="billing-checkout-title" className="text-base font-bold text-white">
              {title}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-[var(--cm-on-surface-variant)] hover:text-white p-2"
            aria-label={isES ? "Cerrar" : "Close"}
          >
            ✕
          </button>
        </div>

        <div className="px-5 py-5">
          {step === "done" ? (
            renderSuccess()
          ) : step === 1 ? (
            <div className="form-stack">
              {isPro && (
                <div className="space-y-2">
                  <p className="text-[11px] text-[var(--cm-on-surface-variant)]/70">
                    {isES ? "Método de pago" : "Payment method"}
                  </p>
                  <div className="grid grid-cols-2 gap-2">
                    {PAYMENT_METHODS.map((m) => (
                      <button
                        key={m.id}
                        type="button"
                        onClick={() => setPaymentMethod(m.id)}
                        className={`text-sm px-3 py-2.5 rounded border transition-colors ${
                          paymentMethod === m.id
                            ? "border-[var(--cm-action)] bg-[var(--cm-action)]/10 text-white"
                            : "border-[var(--cm-outline-variant)]/40 text-[var(--cm-on-surface-variant)]"
                        }`}
                      >
                        {isES ? m.label_es : m.label_en}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {!isPro && procureMeta && (
                <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
                  {isES ? procureMeta.description_es : procureMeta.description_en}
                </p>
              )}
              <p className="text-xs text-[var(--cm-on-surface-variant)]/70 leading-relaxed">
                {isPro
                  ? isES
                    ? `Facturación ${MARKET_STATS.paymentsLabel}. Sinapsis Innovadora S.A.C. · RUC 20613045563.`
                    : `Billing via ${MARKET_STATS.paymentsLabel}. Sinapsis Innovadora S.A.C. · tax ID 20613045563.`
                  : isES
                    ? "Pago vía PayPal. Tras confirmar, pega tu API key en el dashboard Procure."
                    : "Pay via PayPal. After confirmation, paste your API key in the Procure dashboard."}
              </p>
              <LegalConsentCheckbox checked={legal} onChange={setLegal} includeSubscriptions={isPro} />
              {error && <p className="text-xs text-[#ffb4ab]">{error}</p>}
              <button
                type="button"
                disabled={!legal}
                onClick={() => {
                  setError("");
                  setStep(2);
                }}
                className="btn-mint w-full disabled:opacity-50"
              >
                {isES ? "Continuar — datos de cuenta →" : "Continue — account details →"}
              </button>
            </div>
          ) : (
            <div className="form-stack">
              <p className="text-sm text-[var(--cm-on-surface-variant)]">
                {isES
                  ? "Email para activación y comprobantes. Si ya tienes cuenta CLI, indícalo abajo (opcional)."
                  : "Email for activation and receipts. If you already have a CLI account, add it below (optional)."}
              </p>
              <input
                type="email"
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={isES ? "su@email.com" : "you@email.com"}
                className="w-full input-cyber"
              />
              <details className="details-disclosure">
                <summary>{isES ? "Usuario CLI existente (opcional)" : "Existing CLI user (optional)"}</summary>
                <div className="details-body pt-3">
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder={isES ? "market whoami" : "market whoami"}
                    className="w-full input-cyber text-sm"
                  />
                </div>
              </details>
              {error && <p className="text-xs text-[#ffb4ab]">{error}</p>}
              <div className="flex gap-2">
                <button type="button" onClick={() => setStep(1)} className="flex-1 rounded-full border border-[var(--cm-outline-variant)]/50 py-2.5 text-sm text-[var(--cm-on-surface-variant)]">
                  {isES ? "Atrás" : "Back"}
                </button>
                <button type="button" onClick={submit} disabled={loading} className="btn-mint flex-[2] disabled:opacity-50">
                  {loading
                    ? isES
                      ? "Preparando…"
                      : "Preparing…"
                    : isPro
                      ? isES
                        ? `Pagar — ${methodLabel(paymentMethod, true)}`
                        : `Pay — ${methodLabel(paymentMethod, false)}`
                      : isES
                        ? "Suscribir en PayPal"
                        : "Subscribe on PayPal"}
                </button>
              </div>
              {isPro && paymentMethod === "paypal" && (
                <details className="text-xs text-[var(--cm-on-surface-variant)]/50">
                  <summary className="cursor-pointer">{isES ? "Botón PayPal alojado" : "PayPal hosted button"}</summary>
                  <div className="mt-2">
                    <PayPalHostedButton className="w-full" />
                  </div>
                </details>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}