"use client";

import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL, WALLET_MANUAL_FALLBACK } from "@/lib/api";
import { recordFunnelEvent } from "@/lib/funnel";
import { MARKET_STATS } from "@/lib/marketStats";
import LegalConsentCheckbox from "@/components/LegalConsentCheckbox";
import PayPalHostedButton from "@/components/PayPalHostedButton";
import { PROCURE_APP_URL, type ProcurePlanSlug } from "@/lib/procurePlans";
import { PROCURE_PLANS } from "@/lib/procurePlans";
import WalletManualTransfer from "@/components/WalletManualTransfer";
import { checkoutRedirectFromResult } from "@/lib/safeCheckoutUrl";

const CHECKOUT_HOST_SUFFIXES = [
  "paypal.com",
  "mercadopago.com",
  "mercadopago.com.pe",
  "mercadolibre.com",
  "mercadolibre.com.pe",
] as const;

function sanitizeCheckoutHref(raw: string | null | undefined): string | null {
  if (!raw?.trim()) return null;
  try {
    const u = new URL(raw.trim());
    if (u.protocol !== "https:") return null;
    const host = u.hostname.toLowerCase();
    const allowed = CHECKOUT_HOST_SUFFIXES.some(
      (suffix) => host === suffix || host.endsWith(`.${suffix}`),
    );
    return allowed ? u.toString() : null;
  } catch {
    return null;
  }
}

/** Landing Pro checkout: PayPal (USD) or Soles via Mercado Pago (Yape · Plin · tarjeta). */
type PaymentMethod = "paypal" | "soles";

export type BillingCheckoutKind =
  | { type: "build-pro" }
  | { type: "procure"; plan: ProcurePlanSlug };

const PRO_PAYMENT_OPTIONS: {
  id: PaymentMethod;
  label_es: string;
  label_en: string;
  hint_es: string;
  hint_en: string;
}[] = [
  {
    id: "soles",
    label_es: "Soles (Yape · Plin · tarjeta)",
    label_en: "Soles (Yape · Plin · card)",
    hint_es: "Auto · Mercado Pago",
    hint_en: "Auto · Mercado Pago",
  },
  {
    id: "paypal",
    label_es: "PayPal (USD)",
    label_en: "PayPal (USD)",
    hint_es: "Auto · segundos",
    hint_en: "Auto · seconds",
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

function apiPaymentMethod(method: PaymentMethod): string {
  return method === "soles" ? "mercadopago" : "paypal";
}

function displayMethodLabel(method: string | undefined, isES: boolean): string {
  if (method === "mercadopago" || method === "yape" || method === "plin") {
    return isES ? "Soles (Mercado Pago)" : "Soles (Mercado Pago)";
  }
  if (method === "paypal") return "PayPal";
  return method || "";
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
  const redirectUrl = checkoutRedirectFromResult(data);
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
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("soles");
  const [legal, setLegal] = useState(false);
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<CheckoutResult | null>(null);
  const [trustedCheckoutHref, setTrustedCheckoutHref] = useState<string | null>(null);
  const [manualTransfer, setManualTransfer] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [detectingUser, setDetectingUser] = useState(false);
  const [cliWizardOpen, setCliWizardOpen] = useState(true);

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
      setDisplayName("");
      setUsername("");
      setError("");
      setResult(null);
      setTrustedCheckoutHref(null);
      setPaymentMethod("soles");
      setManualTransfer(false);
      setApiKey("");
      setDetectingUser(false);
      setCliWizardOpen(true);
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

  const detectUsernameFromApiKey = async () => {
    const key = apiKey.trim();
    if (!key.startsWith("sk-")) {
      setError(
        isES
          ? "Pega una API key válida (sk-...) de market register"
          : "Paste a valid API key (sk-...) from market register",
      );
      return;
    }
    setError("");
    setDetectingUser(true);
    try {
      const r = await fetch(`${API_URL}/auth/whoami`, {
        headers: { Authorization: `Bearer ${key}` },
      });
      const data = (await r.json()) as { username?: string; detail?: string };
      if (r.ok && data.username) {
        setUsername(data.username);
        setCliWizardOpen(false);
      } else {
        const detail =
          typeof data.detail === "string"
            ? data.detail
            : isES
              ? "API key inválida o expirada"
              : "Invalid or expired API key";
        setError(detail);
      }
    } catch {
      setError(isES ? "Error de red al verificar la API key" : "Network error verifying API key");
    }
    setDetectingUser(false);
  };

  const applyCheckoutResult = (data: CheckoutResult, source: string) => {
    const redirectUrl = checkoutRedirectFromResult(data);
    setTrustedCheckoutHref(redirectUrl);
    recordFunnelEvent(isPro ? "request_pro" : "starter_subscribe", {
      username: data.username || username.trim() || undefined,
      meta: {
        source,
        auto_activate: data.auto_activate !== false,
        email: email.trim(),
        payment_method: data.payment_method || apiPaymentMethod(paymentMethod),
        duplicate: Boolean(data.duplicate),
      },
    });
    const { approve_url: _a, checkout_url: _c, payment_link: _p, ...rest } = data;
    setResult(rest);
    setStep("done");
    setLoading(false);
  };

  const submit = async (opts?: { resend?: boolean }) => {
    setError("");
    if (!email.trim() || !email.includes("@")) {
      setError(isES ? "Ingrese un email válido" : "Enter a valid email");
      return;
    }
    if (isPro && !username.trim()) {
      setError(
        isES
          ? "Usuario CLI requerido — el de market whoami"
          : "CLI username required — from market whoami",
      );
      return;
    }
    setLoading(true);
    try {
      const payload = {
        email: email.trim(),
        username: username.trim(),
        display_name: displayName.trim() || undefined,
        lang: isES ? "es" : "en",
        ...(opts?.resend ? { resend: true } : {}),
      };

      if (isPro) {
        const apiMethod = apiPaymentMethod(paymentMethod);
        const { ok, data } = await postCheckout("/billing/pro-checkout", {
          ...payload,
          payment_method: apiMethod,
          ...(WALLET_MANUAL_FALLBACK &&
          manualTransfer &&
          paymentMethod === "soles"
            ? { payment_method: "yape", manual_transfer: true }
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
    const method = result.payment_method || apiPaymentMethod(paymentMethod);
    const isManualWallet = result.payment_mode === "manual_transfer";
    const isAutoWallet =
      result.wallet_checkout || ((method === "yape" || method === "plin") && !isManualWallet);
    const resolvedUser = result.username || username.trim();

    return (
      <div className="space-y-4 text-left">
        {isAutoWallet && !result.duplicate && (
          <p className="text-sm font-semibold text-white">
            {isES
              ? `Paga en Mercado Pago (Yape, Plin o tarjeta) — Pro se activa en minutos`
              : `Pay on Mercado Pago (Yape, Plin, or card) — Pro activates in minutes`}
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
        {(() => {
          const href = sanitizeCheckoutHref(trustedCheckoutHref);
          if (!href || isManualWallet) return null;
          return (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-mint w-full inline-flex justify-center"
            >
              {paymentRedirectLabel(method, isES)}
            </a>
          );
        })()}
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

  const selectedOption = PRO_PAYMENT_OPTIONS.find((m) => m.id === paymentMethod);

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
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {PRO_PAYMENT_OPTIONS.map((m) => (
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
                          {isES ? m.hint_es : m.hint_en}
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
              {isPro && (
                <div className="rounded border border-[var(--cm-outline-variant)]/35 bg-[var(--cm-surface-low)]/50 px-3 py-3 space-y-3">
                  <button
                    type="button"
                    onClick={() => setCliWizardOpen((v) => !v)}
                    className="w-full text-left text-sm font-semibold text-white flex items-center justify-between gap-2"
                  >
                    <span>
                      {isES
                        ? "¿Aún no tienes usuario CLI?"
                        : "Don't have a CLI user yet?"}
                    </span>
                    <span className="text-[var(--cm-on-surface-variant)] text-xs">
                      {cliWizardOpen ? "▾" : "▸"}
                    </span>
                  </button>
                  {cliWizardOpen && (
                    <div className="space-y-2 text-xs text-[var(--cm-on-surface-variant)]">
                      <p>
                        {isES
                          ? "Pro se activa en el usuario que pagas. Sigue estos pasos en tu terminal:"
                          : "Pro activates on the user you pay for. Run these in your terminal:"}
                      </p>
                      <ol className="list-decimal list-inside space-y-1 font-mono text-[11px] text-white/90">
                        <li>{MARKET_STATS.pipInstallCmd}</li>
                        <li>market register</li>
                        <li>market whoami</li>
                      </ol>
                      <p className="text-[10px] text-[var(--cm-on-surface-variant)]/70">
                        {isES
                          ? "Copia el username de whoami abajo, o pega tu API key para detectarlo."
                          : "Copy the username from whoami below, or paste your API key to detect it."}
                      </p>
                      <div className="flex gap-2">
                        <input
                          type="password"
                          value={apiKey}
                          onChange={(e) => setApiKey(e.target.value)}
                          placeholder={isES ? "sk-... (opcional)" : "sk-... (optional)"}
                          className="flex-1 input-cyber text-xs font-mono"
                          autoComplete="off"
                        />
                        <button
                          type="button"
                          onClick={() => void detectUsernameFromApiKey()}
                          disabled={detectingUser || !apiKey.trim()}
                          className="shrink-0 rounded-full border border-[var(--cm-outline-variant)]/50 px-3 py-2 text-[11px] text-[var(--cm-on-surface-variant)] hover:text-white disabled:opacity-50"
                        >
                          {detectingUser
                            ? isES
                              ? "…"
                              : "…"
                            : isES
                              ? "Detectar"
                              : "Detect"}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
              <p className="text-sm text-[var(--cm-on-surface-variant)]">
                {isES
                  ? "Datos para tu correo de bienvenida y activación Pro."
                  : "Details for your welcome email and Pro activation."}
              </p>
              <input
                type="text"
                autoFocus
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder={isES ? "Tu nombre" : "Your name"}
                className="w-full input-cyber"
              />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={isES ? "su@email.com" : "you@email.com"}
                className="w-full input-cyber"
              />
              <div className="space-y-1">
                <label htmlFor="checkout-username" className="text-xs text-[var(--cm-on-surface-variant)]">
                  {isES ? "Usuario CLI (obligatorio)" : "CLI username (required)"}
                </label>
                <input
                  id="checkout-username"
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder={isES ? "el de market whoami" : "from market whoami"}
                  className="w-full input-cyber text-sm"
                />
                <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60">
                  {isES
                    ? "Debe coincidir con tu sesión CLI para que Pro se active en el usuario correcto."
                    : "Must match your CLI session so Pro activates on the right user."}
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
                        ? `Pagar — ${selectedOption ? (isES ? selectedOption.label_es : selectedOption.label_en) : ""}`
                        : `Pay — ${selectedOption ? selectedOption.label_en : ""}`
                      : isES
                        ? "Continuar — PayPal"
                        : "Continue — PayPal"}
                </button>
              </div>
              {isPro && paymentMethod === "paypal" && selectedOption && (
                <p className="text-[10px] text-center text-[var(--cm-on-surface-variant)]/50 font-mono">
                  {isES ? selectedOption.hint_es : selectedOption.hint_en}
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
              {isPro && WALLET_MANUAL_FALLBACK && paymentMethod === "soles" && (
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