"use client";

import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import { recordFunnelEvent } from "@/lib/funnel";
import { MARKET_STATS } from "@/lib/marketStats";
import LegalConsentCheckbox from "@/components/LegalConsentCheckbox";
import PayPalHostedButton from "@/components/PayPalHostedButton";
import { PROCURE_APP_URL, type ProcurePlanSlug } from "@/lib/procurePlans";
import { PROCURE_PLANS } from "@/lib/procurePlans";
import WalletManualTransfer from "@/components/WalletManualTransfer";

type PaymentMethod = "paypal" | "mercadopago" | "yape" | "plin";

export type BillingCheckoutKind =
  | { type: "build-pro" }
  | { type: "procure"; plan: ProcurePlanSlug };

const PAYMENT_METHODS: {
  id: PaymentMethod;
  label_es: string;
  label_en: string;
  auto_es: string;
  auto_en: string;
}[] = [
  {
    id: "paypal",
    label_es: "PayPal",
    label_en: "PayPal",
    auto_es: "Auto · segundos",
    auto_en: "Auto · seconds",
  },
  {
    id: "mercadopago",
    label_es: "Mercado Pago",
    label_en: "Mercado Pago",
    auto_es: "Auto · webhook",
    auto_en: "Auto · webhook",
  },
  {
    id: "yape",
    label_es: "Yape",
    label_en: "Yape",
    auto_es: "Auto · vía Mercado Pago",
    auto_en: "Auto · via Mercado Pago",
  },
  {
    id: "plin",
    label_es: "Plin",
    label_en: "Plin",
    auto_es: "Auto · vía Mercado Pago",
    auto_en: "Auto · via Mercado Pago",
  },
];

type CheckoutResult = {
  ok?: boolean;
  duplicate?: boolean;
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
  request_id?: string;
  payment_mode?: string;
  payment_rail?: string;
  wallet_checkout?: boolean;
  payment_phone?: string | null;
  manual_steps?: string[];
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

async function postCheckout(
  path: string,
  body: Record<string, unknown>,
): Promise<{ ok: boolean; status: number; data: CheckoutResult }> {
  const r = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = (await r.json()) as CheckoutResult;
  return { ok: r.ok, status: r.status, data };
}

function checkoutSucceeded(data: CheckoutResult): boolean {
  if (!data.ok) return false;
  const redirectUrl = data.approve_url || data.checkout_url || data.payment_link;
  const manualWallet =
    data.payment_mode === "manual_transfer" &&
    (data.payment_method === "yape" || data.payment_method === "plin");
  return Boolean(redirectUrl || (manualWallet && data.request_id));
}

function paymentRedirectLabel(method: string | undefined, isES: boolean): string {
  if (method === "mercadopago" || method === "yape" || method === "plin") {
    return isES ? "Ir a Mercado Pago →" : "Go to Mercado Pago →";
  }
  return isES ? "Ir al pago en PayPal →" : "Go to PayPal →";
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
  const [manualTransfer, setManualTransfer] = useState(false);

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
      setManualTransfer(false);
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

  const applyCheckoutResult = (data: CheckoutResult, source: string) => {
    const redirectUrl = data.approve_url || data.checkout_url || data.payment_link;
    recordFunnelEvent(isPro ? "request_pro" : "starter_subscribe", {
      username: data.username || username.trim() || undefined,
      meta: {
        source,
        auto_activate: data.auto_activate !== false,
        email: email.trim(),
        payment_method: data.payment_method || paymentMethod,
        duplicate: Boolean(data.duplicate),
      },
    });
    setResult({ ...data, approve_url: redirectUrl });
    setStep("done");
    setLoading(false);
  };

  const submit = async (opts?: { resend?: boolean }) => {
    setError("");
    if (!email.trim() || !email.includes("@")) {
      setError(isES ? "Ingrese un email válido" : "Enter a valid email");
      return;
    }
    setLoading(true);
    try {
      const payload = {
        email: email.trim(),
        username: username.trim() || undefined,
        lang: isES ? "es" : "en",
        ...(opts?.resend ? { resend: true } : {}),
      };

      if (isPro) {
        const { ok, data } = await postCheckout("/billing/pro-checkout", {
          ...payload,
          payment_method: paymentMethod,
          ...(manualTransfer && (paymentMethod === "yape" || paymentMethod === "plin")
            ? { manual_transfer: true }
            : {}),
        });
        if (ok && checkoutSucceeded(data)) {
          applyCheckoutResult(data, `landing_checkout_modal_${paymentMethod}`);
          return;
        }
        setError(parseApiError(data, isES ? "Error al preparar el pago" : "Error preparing checkout"));
      } else {
        const { ok, data } = await postCheckout("/billing/procure-subscribe", {
          ...payload,
          plan: kind.plan,
        });
        if (ok && checkoutSucceeded(data)) {
          applyCheckoutResult(data, "landing_procure_subscribe");
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
    const isManualWallet = result.payment_mode === "manual_transfer";
    const isAutoWallet =
      result.wallet_checkout || ((method === "yape" || method === "plin") && !isManualWallet);
    const redirectUrl = result.approve_url || result.checkout_url || result.payment_link;
    const resolvedUser = result.username || username.trim();

    return (
      <div className="space-y-4 text-left">
        {isAutoWallet && !result.duplicate && (
          <p className="text-sm font-semibold text-white">
            {isES
              ? `Paga con ${methodLabel(method, true)} en Mercado Pago — Pro se activa en minutos`
              : `Pay with ${methodLabel(method, false)} on Mercado Pago — Pro activates in minutes`}
          </p>
        )}
        {result.duplicate && (
          <p className="text-xs rounded border border-[var(--cm-outline-variant)]/40 bg-[var(--cm-surface-low)]/50 px-3 py-2 text-[var(--cm-on-surface-variant)]">
            {result.message}
          </p>
        )}
        {!result.duplicate && result.message && (
          <p className="text-sm text-[var(--cm-on-surface-variant)]">{result.message}</p>
        )}
        {resolvedUser && (
          <p className="font-mono text-xs text-[var(--cm-on-surface-variant)]/80">
            {isES ? "Usuario CLI:" : "CLI user:"} <span className="text-white">{resolvedUser}</span>
          </p>
        )}
        {isManualWallet && (
          <WalletManualTransfer
            method={method as "yape" | "plin"}
            amountPen={result.amount_pen}
            reference={result.request_id || result.qr_reference}
            phone={result.payment_phone}
            steps={result.manual_steps}
            isES={isES}
          />
        )}
        {redirectUrl && !isManualWallet && (
          <a href={redirectUrl} target="_blank" rel="noopener noreferrer" className="btn-mint w-full inline-flex justify-center">
            {paymentRedirectLabel(method, isES)}
          </a>
        )}
        <div className="rounded border border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]/30 px-3 py-3 text-xs text-[var(--cm-on-surface-variant)] space-y-1">
          {isPro ? (
            <>
              <p className="font-semibold text-white">{isES ? "Después del pago" : "After payment"}</p>
              <p className="font-mono">pip install cli-market-world</p>
              <p className="font-mono">market login --username {resolvedUser || "TU_USUARIO"}</p>
              <p className="font-mono">market whoami</p>
              <p className="text-[var(--cm-on-surface-variant)]/80">
                {isES ? "→ debe mostrar tier: pro" : "→ should show tier: pro"}
              </p>
            </>
          ) : (
            <>
              <p className="font-semibold text-white">{isES ? "Después del pago" : "After payment"}</p>
              <p className="font-mono">market register → market account</p>
              <p>{isES ? "Pega sk-… en el dashboard Procure:" : "Paste sk-… in Procure dashboard:"}</p>
              <a href={PROCURE_APP_URL} className="text-[var(--cm-mint)] hover:underline inline-block">
                {isES ? "Abrir Procure →" : "Open Procure →"}
              </a>
            </>
          )}
        </div>
        {result.duplicate && (
          <button
            type="button"
            disabled={loading}
            onClick={() => submit({ resend: true })}
            className="w-full rounded-full border border-[var(--cm-outline-variant)]/50 py-2.5 text-sm text-[var(--cm-on-surface-variant)] hover:text-white disabled:opacity-50"
          >
            {loading
              ? isES
                ? "Reenviando…"
                : "Resending…"
              : isES
                ? "Reenviar enlace por email"
                : "Resend link by email"}
          </button>
        )}
        <button type="button" onClick={onClose} className="w-full text-sm text-[var(--cm-on-surface-variant)] hover:text-white">
          {isES ? "Cerrar" : "Close"}
        </button>
      </div>
    );
  };

  const selectedMethod = PAYMENT_METHODS.find((m) => m.id === paymentMethod);

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
                        className={`text-left text-sm px-3 py-2.5 rounded border transition-colors ${
                          paymentMethod === m.id
                            ? "border-[var(--cm-action)] bg-[var(--cm-action)]/10 text-white"
                            : "border-[var(--cm-outline-variant)]/40 text-[var(--cm-on-surface-variant)]"
                        }`}
                      >
                        <span className="block">{isES ? m.label_es : m.label_en}</span>
                        <span className="block text-[10px] font-mono opacity-70 mt-0.5">
                          {isES ? m.auto_es : m.auto_en}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {!isPro && procureMeta && (
                <>
                  <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
                    {isES ? procureMeta.description_es : procureMeta.description_en}
                  </p>
                  <p className="text-xs rounded border border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]/40 px-3 py-2 text-[var(--cm-on-surface-variant)]">
                    {isES
                      ? "Pago solo vía PayPal (auto-activación). Incluye API Build — no necesitas Build Pro aparte."
                      : "PayPal only (auto-activation). Includes Build API — no separate Build Pro needed."}
                  </p>
                </>
              )}
              <p className="text-xs text-[var(--cm-on-surface-variant)]/70 leading-relaxed">
                {isPro
                  ? isES
                    ? `Facturación ${MARKET_STATS.paymentsLabel}. Sinapsis Innovadora S.A.C. · RUC 20613045563.`
                    : `Billing via ${MARKET_STATS.paymentsLabel}. Sinapsis Innovadora S.A.C. · tax ID 20613045563.`
                  : isES
                    ? "Suscripción mensual vía PayPal. Tras confirmar, conecta tu API key en Procure."
                    : "Monthly PayPal subscription. After confirming, connect your API key in Procure."}
              </p>
              <LegalConsentCheckbox checked={legal} onChange={setLegal} includeSubscriptions />
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
                  ? "Email para activación y comprobantes."
                  : "Email for activation and receipts."}
              </p>
              <input
                type="email"
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={isES ? "su@email.com" : "you@email.com"}
                className="w-full input-cyber"
              />
              <div className="space-y-1">
                <label htmlFor="checkout-username" className="text-xs text-[var(--cm-on-surface-variant)]">
                  {isES ? "Usuario CLI (recomendado si ya hiciste market login)" : "CLI username (recommended if you ran market login)"}
                </label>
                <input
                  id="checkout-username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder={isES ? "el de market whoami" : "from market whoami"}
                  className="w-full input-cyber text-sm"
                />
                <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60">
                  {isES
                    ? "Si lo dejas vacío, se crea uno desde tu email — puede no coincidir con tu sesión CLI."
                    : "If empty, one is derived from your email — may not match your CLI session."}
                </p>
              </div>
              {error && <p className="text-xs text-[#ffb4ab]">{error}</p>}
              <div className="flex gap-2">
                <button type="button" onClick={() => setStep(1)} className="flex-1 rounded-full border border-[var(--cm-outline-variant)]/50 py-2.5 text-sm text-[var(--cm-on-surface-variant)]">
                  {isES ? "Atrás" : "Back"}
                </button>
                <button type="button" onClick={() => submit()} disabled={loading} className="btn-mint flex-[2] disabled:opacity-50">
                  {loading
                    ? isES
                      ? "Preparando…"
                      : "Preparing…"
                    : isPro
                      ? isES
                        ? `Pagar — ${methodLabel(paymentMethod, true)}`
                        : `Pay — ${methodLabel(paymentMethod, false)}`
                      : isES
                        ? "Continuar — PayPal"
                        : "Continue — PayPal"}
                </button>
              </div>
              {isPro && paymentMethod === "paypal" && selectedMethod && (
                <p className="text-[10px] text-center text-[var(--cm-on-surface-variant)]/50 font-mono">
                  {isES ? selectedMethod.auto_es : selectedMethod.auto_en}
                </p>
              )}
              {isPro && paymentMethod === "paypal" && (
                <details className="text-xs text-[var(--cm-on-surface-variant)]/50">
                  <summary className="cursor-pointer">{isES ? "Respaldo: botón PayPal alojado" : "Fallback: PayPal hosted button"}</summary>
                  <div className="mt-2">
                    <PayPalHostedButton className="w-full" />
                  </div>
                </details>
              )}
              {isPro && (paymentMethod === "yape" || paymentMethod === "plin") && (
                <label className="flex items-start gap-2 text-xs text-[var(--cm-on-surface-variant)]/70 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={manualTransfer}
                    onChange={(e) => setManualTransfer(e.target.checked)}
                    className="mt-0.5"
                  />
                  <span>
                    {isES
                      ? "Sin Mercado Pago: transferencia manual a número Yape/Plin (activación ≤24 h)"
                      : "No Mercado Pago: manual transfer to Yape/Plin number (activation ≤24 h)"}
                  </span>
                </label>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}