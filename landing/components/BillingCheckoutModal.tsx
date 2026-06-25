"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { useBodyScrollLock } from "@/hooks/useBodyScrollLock";
import { useLang } from "@/lib/LanguageContext";
import { API_URL, PROCURE_MP_CHECKOUT, WALLET_MANUAL_FALLBACK } from "@/lib/api";
import { recordFunnelEvent } from "@/lib/funnel";
import { MARKET_STATS } from "@/lib/marketStats";
import { paymentsChannelsForCheckout } from "@/lib/billingCopy";
import LegalConsentCheckbox from "@/components/LegalConsentCheckbox";
import PayPalHostedButton from "@/components/PayPalHostedButton";
import { PROCURE_APP_URL, type ProcurePlanSlug } from "@/lib/procurePlans";
import { PROCURE_PLANS } from "@/lib/procurePlans";
import WalletManualTransfer from "@/components/WalletManualTransfer";
import { checkoutRedirectFromResult } from "@/lib/safeCheckoutUrl";
import {
  defaultProPaymentMethod,
  orderProPaymentOptions,
  type ProCheckoutPaymentId,
} from "@/lib/checkoutLocale";
import { LANDING_MODAL_BACKDROP, LANDING_MODAL_OVERLAY, LANDING_MODAL_PANEL, LANDING_MODAL_PANEL_MD } from "@/lib/modalLayout";

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
type PaymentMethod = ProCheckoutPaymentId;

export type BillingCheckoutKind =
  | { type: "build-starter" }
  | { type: "build-pro"; annual?: boolean }
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
  const isStarter = kind.type === "build-starter";
  const isProcure = kind.type === "procure";
  const isPayPalOnly = isStarter;
  const isSingleStepCheckout = isPayPalOnly || isPro || isProcure;
  const procureMeta =
    kind.type === "procure" ? PROCURE_PLANS.find((p) => p.slug === kind.plan) : null;
  const showProcurePaymentPicker = isProcure && PROCURE_MP_CHECKOUT;

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
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);
  useBodyScrollLock(open);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
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
      setManualTransfer(false);
      setApiKey("");
      setDetectingUser(false);
      setCliWizardOpen(true);
      return;
    }
    setPaymentMethod(defaultProPaymentMethod());
  }, [open, kind]);

  if (!open || !mounted) return null;

  const title = isStarter
    ? isES
      ? "Build · Starter · $9/mes"
      : "Build · Starter · $9/mo"
    : kind.type === "build-pro" && kind.annual
      ? isES
        ? "Build · Pro · $490/año"
        : "Build · Pro · $490/yr"
      : kind.type === "build-pro"
        ? isES
          ? "Build · Pro · $49/mes"
          : "Build · Pro · $49/mo"
        : isProcure
          ? isES
            ? `Procure · ${procureMeta?.name ?? kind.plan} · $${procureMeta?.price ?? ""}/mes`
            : `Procure · ${procureMeta?.name ?? kind.plan} · $${procureMeta?.price ?? ""}/mo`
          : "Procure";

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
    recordFunnelEvent(
      isStarter ? "starter_subscribe" : isProcure ? "procure_subscribe" : "request_pro",
      {
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
    let resolvedUsername = username.trim();
    if (isStarter && !resolvedUsername) {
      resolvedUsername = email.split("@")[0].replace(/[^a-z0-9_-]/gi, "").slice(0, 32) || "";
    }
    setLoading(true);
    try {
      const payload = {
        email: email.trim(),
        username: resolvedUsername,
        display_name: displayName.trim() || undefined,
        lang: isES ? "es" : "en",
        ...(opts?.resend ? { resend: true } : {}),
      };

      if (isPro || isStarter) {
        const buildPlan = isStarter
          ? "starter"
          : kind.type === "build-pro" && kind.annual
              ? "pro_annual"
              : "pro";

        if (isStarter || paymentMethod === "paypal") {
          const { ok, data } = await postCheckout("/billing/build-checkout", {
            ...payload,
            plan: buildPlan,
            payment_method: "paypal",

          });
          if (ok && checkoutSucceeded(data)) {
            applyCheckoutResult(data, `landing_build_checkout_${buildPlan}`);
            return;
          }
          setError(parseApiError(data, isES ? "Error al preparar el pago" : "Error preparing checkout"));
          setLoading(false);
          return;
        }

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
      } else if (isProcure) {
        const procurePlan = kind.plan;
        const usePayPal = paymentMethod === "paypal" || !showProcurePaymentPicker;
        if (usePayPal) {
          const { ok, data } = await postCheckout("/billing/procure-subscribe", {
            ...payload,
            plan: procurePlan,
            payment_method: "paypal",
          });
          if (ok && checkoutSucceeded(data)) {
            applyCheckoutResult(data, "landing_procure_subscribe_paypal");
            return;
          }
          setError(
            parseApiError(data, isES ? "Error al iniciar suscripción" : "Subscription error"),
          );
        } else {
          const apiMethod = apiPaymentMethod(paymentMethod);
          const { ok, data } = await postCheckout("/billing/procure-subscribe", {
            ...payload,
            plan: procurePlan,
            payment_method: apiMethod,
            ...(WALLET_MANUAL_FALLBACK &&
            manualTransfer &&
            paymentMethod === "soles"
              ? { payment_method: "yape", manual_transfer: true }
              : {}),
          });
          if (ok && checkoutSucceeded(data)) {
            applyCheckoutResult(data, `landing_procure_checkout_${paymentMethod}`);
            return;
          }
          setError(
            parseApiError(data, isES ? "Error al iniciar suscripción" : "Subscription error"),
          );
        }
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

    const productName = isProcure ? "Procure" : "Pro";

    return (
      <div className="space-y-4 text-left">
        {isAutoWallet && !result.duplicate && (
          <p className="text-sm font-semibold text-white">
            {isES
              ? `Paga en Mercado Pago (Yape, Plin o tarjeta) — ${productName} se activa en minutos`
              : `Pay on Mercado Pago (Yape, Plin, or card) — ${productName} activates in minutes`}
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
          {isProcure ? (
            <>
              <p className="font-semibold text-white">{isES ? "Después del pago" : "After payment"}</p>
              <p>
                {isES
                  ? "Tras confirmar el pago, recibirás un email con enlace mágico al dashboard (API key precargada)."
                  : "After payment confirms, you'll get an email with a magic link to the dashboard (API key preloaded)."}
              </p>
              <a href={PROCURE_APP_URL} className="text-[var(--cm-mint)] hover:underline inline-block">
                {isES ? "Abrir Procure →" : "Open Procure →"}
              </a>
            </>
          ) : (
            <>
              <p className="font-semibold text-white">{isES ? "Después del pago" : "After payment"}</p>
              <p className="font-mono">{MARKET_STATS.pipInstallCmd}</p>
              <p className="font-mono">market login --username {resolvedUser || "TU_USUARIO"}</p>
              <p className="font-mono">market whoami</p>
              <p className="text-[var(--cm-on-surface-variant)]/80">
                {isES
                  ? `→ debe mostrar tier: ${isStarter ? "starter" : "pro"}`
                  : `→ should show tier: ${isStarter ? "starter" : "pro"}`}
              </p>
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
  const paymentOptions = orderProPaymentOptions(PRO_PAYMENT_OPTIONS);
  const recommendedMethod = defaultProPaymentMethod();

  return createPortal(
    <div
      className={LANDING_MODAL_OVERLAY}
      role="dialog"
      aria-modal="true"
      aria-labelledby="billing-checkout-title"
    >
      <button
        type="button"
        className={LANDING_MODAL_BACKDROP}
        aria-label={isES ? "Cerrar" : "Close"}
        onClick={onClose}
      />
      <div className={`${LANDING_MODAL_PANEL} ${LANDING_MODAL_PANEL_MD} modal-panel-dark max-h-[min(88dvh,640px)] overflow-y-auto overscroll-contain rounded-2xl border border-white/10 shadow-xl`}>
        <div className="flex items-start justify-between gap-3 border-b border-[var(--cm-outline-variant)]/30 px-5 py-4">
          <div className="min-w-0">
            {!isSingleStepCheckout && step !== "done" && (
              <p className="font-mono text-[10px] uppercase tracking-widest text-[var(--cm-action)] mb-1">
                {isES ? "Paso" : "Step"} {step} / 2
              </p>
            )}
            <h2 id="billing-checkout-title" className="text-lg font-bold text-white leading-snug">
              {title}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-[var(--cm-on-surface-variant)] hover:text-white p-2 shrink-0"
            aria-label={isES ? "Cerrar" : "Close"}
          >
            ✕
          </button>
        </div>

        <div className="px-5 py-5">
          {step === "done" ? (
            renderSuccess()
          ) : isPro || isProcure ? (
            <div className="form-stack">
              {isProcure && procureMeta && (
                <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
                  {isES ? procureMeta.description_es : procureMeta.description_en}
                </p>
              )}
              {(isPro || showProcurePaymentPicker) && (
                <div className="space-y-2">
                  <p className="text-[11px] text-[var(--cm-on-surface-variant)]/70">
                    {isES ? "Método de pago" : "Payment method"}
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {paymentOptions.map((m) => (
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
                        <span className="block">
                          {isES ? m.label_es : m.label_en}
                          {m.id === recommendedMethod ? (
                            <span className="ml-1.5 text-[10px] font-mono text-[var(--cm-mint)]">
                              {isES ? "recomendado" : "recommended"}
                            </span>
                          ) : null}
                        </span>
                        <span className="block text-[10px] font-mono opacity-70 mt-0.5">
                          {isES ? m.hint_es : m.hint_en}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {isProcure && !showProcurePaymentPicker && (
                <p className="text-xs rounded border border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]/40 px-3 py-2 text-[var(--cm-on-surface-variant)]">
                  {isES
                    ? "Pago vía PayPal (USD) · auto-activación en minutos."
                    : "PayPal (USD) checkout · auto-activation in minutes."}
                </p>
              )}
              <div className="rounded border border-[var(--cm-outline-variant)]/35 bg-[var(--cm-surface-low)]/50 px-3 py-3 space-y-3">
                <button
                  type="button"
                  onClick={() => setCliWizardOpen((v) => !v)}
                  className="w-full text-left text-sm font-semibold text-white flex items-center justify-between gap-2"
                >
                  <span>{isES ? "¿Aún no tienes usuario CLI?" : "Don't have a CLI user yet?"}</span>
                  <span className="text-[var(--cm-on-surface-variant)] text-xs">{cliWizardOpen ? "▾" : "▸"}</span>
                </button>
                {cliWizardOpen && (
                  <div className="space-y-2 text-xs text-[var(--cm-on-surface-variant)]">
                    <ol className="list-decimal list-inside space-y-1 font-mono text-[11px] text-white/90">
                      <li>{MARKET_STATS.pipInstallCmd}</li>
                      <li>market register</li>
                      <li>market whoami</li>
                    </ol>
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
                        {detectingUser ? "…" : isES ? "Detectar" : "Detect"}
                      </button>
                    </div>
                  </div>
                )}
              </div>
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
                <label htmlFor="checkout-username-pro" className="text-xs text-[var(--cm-on-surface-variant)]">
                  {isES ? "Usuario CLI" : "CLI username"}
                  {isProcure ? (isES ? " (opcional)" : " (optional)") : null}
                </label>
                <input
                  id="checkout-username-pro"
                  type="text"
                  required={isPro}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder={isES ? "market whoami" : "market whoami"}
                  className="w-full input-cyber text-sm"
                />
              </div>
              <p className="text-xs text-[var(--cm-on-surface-variant)]/70 leading-relaxed">
                {isES
                  ? `Facturación ${paymentsChannelsForCheckout(true)} · comprobante en la moneda del pago.`
                  : `Billing ${paymentsChannelsForCheckout(false)} · receipt in payment currency.`}
              </p>
              <LegalConsentCheckbox checked={legal} onChange={setLegal} includeSubscriptions />
              {error && <p className="text-xs text-[#ffb4ab]">{error}</p>}
              <button
                type="button"
                onClick={() => submit()}
                disabled={loading || !legal}
                className="btn-mint w-full disabled:opacity-50"
              >
                {loading
                  ? isES
                    ? "Preparando…"
                    : "Preparing…"
                  : paymentMethod === "paypal" || (isProcure && !showProcurePaymentPicker)
                    ? isES
                      ? "Continuar en PayPal →"
                      : "Continue on PayPal →"
                    : isES
                      ? "Continuar en Mercado Pago →"
                      : "Continue on Mercado Pago →"}
              </button>
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
              {(isPro || showProcurePaymentPicker) && WALLET_MANUAL_FALLBACK && paymentMethod === "soles" && (
                <label className="flex items-start gap-2 text-xs text-[var(--cm-on-surface-variant)]/70 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={manualTransfer}
                    onChange={(e) => setManualTransfer(e.target.checked)}
                    className="mt-0.5"
                  />
                  <span>
                    {isES
                      ? "Sin Mercado Pago: transferencia manual Yape/Plin"
                      : "No Mercado Pago: manual Yape/Plin transfer"}
                  </span>
                </label>
              )}
            </div>
          ) : isPayPalOnly ? (
            <div className="form-stack">
              <p className="text-sm text-[var(--cm-on-surface-variant)]">
                {isES
                    ? "PayPal (USD). CSV, alertas y API completo."
                    : "PayPal (USD). CSV, alerts, and full API."}
              </p>
              <input
                type="email"
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={isES ? "su@email.com" : "you@email.com"}
                className="w-full input-cyber"
              />

              <LegalConsentCheckbox checked={legal} onChange={setLegal} includeSubscriptions />
              {error && <p className="text-xs text-[#ffb4ab]">{error}</p>}
              <button
                type="button"
                onClick={() => submit()}
                disabled={loading || !legal}
                className="btn-mint w-full disabled:opacity-50"
              >
                {loading
                  ? isES
                    ? "Preparando…"
                    : "Preparing…"
                  : isES
                    ? "Continuar en PayPal →"
                    : "Continue on PayPal →"}
              </button>
            </div>
          ) : null}
        </div>
      </div>
    </div>,
    document.body,
  );
}