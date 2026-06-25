"use client";

import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { PROCURE_APP_URL } from "@/lib/procurePlans";
import { buildPlanLabel, normalizeBuildPlanSlug, type BuildPlanSlug } from "@/lib/buildPlans";
import { MARKET_STATS } from "@/lib/marketStats";

export type PaymentReturnState = "success" | "pending" | "cancelled" | null;
export type PaymentReturnProvider = "paypal" | "mercadopago" | null;

export function readPaymentReturnState(): {
  state: PaymentReturnState;
  audience: "build" | "procure";
  provider: PaymentReturnProvider;
  ref: string | null;
  buildPlan: BuildPlanSlug | null;
} {
  if (typeof window === "undefined") {
    return { state: null, audience: "build", provider: null, ref: null, buildPlan: null };
  }
  const params = new URLSearchParams(window.location.search);
  const sub = params.get("sub");
  const payment = params.get("payment");
  const mp = params.get("mp");
  const audience = params.get("audience") === "procure" ? "procure" : "build";
  const ref = params.get("ref");
  const buildPlan = normalizeBuildPlanSlug(params.get("plan"));

  let state: PaymentReturnState = null;
  let provider: PaymentReturnProvider = null;

  if (sub === "success" || payment === "success" || mp === "success") {
    state = "success";
    provider = mp === "success" ? "mercadopago" : "paypal";
  } else if (mp === "pending") {
    state = "pending";
    provider = "mercadopago";
  } else if (sub === "cancelled" || mp === "failure") {
    state = "cancelled";
    provider = mp === "failure" ? "mercadopago" : "paypal";
  }

  return { state, audience, provider, ref, buildPlan };
}

export function clearPaymentReturnQuery(): void {
  if (typeof window === "undefined") return;
  const url = new URL(window.location.href);
  url.searchParams.delete("sub");
  url.searchParams.delete("payment");
  url.searchParams.delete("mp");
  url.searchParams.delete("ref");
  url.searchParams.delete("plan");
  url.searchParams.delete("audience");
  window.history.replaceState(null, "", url.pathname + url.search + url.hash);
}

export default function PaymentReturnBanner() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [visible, setVisible] = useState(false);
  const [state, setState] = useState<PaymentReturnState>(null);
  const [audience, setAudience] = useState<"build" | "procure">("build");
  const [provider, setProvider] = useState<PaymentReturnProvider>(null);
  const [ref, setRef] = useState<string | null>(null);
  const [buildPlan, setBuildPlan] = useState<BuildPlanSlug | null>(null);

  useEffect(() => {
    const next = readPaymentReturnState();
    if (!next.state) return;
    setState(next.state);
    setAudience(next.audience);
    setProvider(next.provider);
    setRef(next.ref);
    setBuildPlan(next.buildPlan);
    setVisible(true);
    clearPaymentReturnQuery();
  }, []);

  if (!visible || !state) return null;

  const isProcure = audience === "procure";
  const isSuccess = state === "success";
  const isPending = state === "pending";
  const isMp = provider === "mercadopago";

  const planLabel = buildPlanLabel(buildPlan, isES);

  const title = (() => {
    if (isSuccess) {
      if (isProcure) {
        if (isMp) {
          return isES
            ? "Pago Mercado Pago recibido — Procure"
            : "Mercado Pago payment received — Procure";
        }
        return isES ? "Suscripción Procure confirmada" : "Procure subscription confirmed";
      }
      if (planLabel) {
        return isES
          ? `${planLabel} confirmado en PayPal`
          : `${planLabel} confirmed on PayPal`;
      }
      if (isMp) {
        return isES ? "Pago Mercado Pago recibido — Build" : "Mercado Pago payment received — Build";
      }
      return isES ? "Suscripción Build confirmada en PayPal" : "Build subscription confirmed on PayPal";
    }
    if (isPending) {
      return isES ? "Pago Mercado Pago pendiente de confirmación" : "Mercado Pago payment pending confirmation";
    }
    return isMp
      ? isES
        ? "Pago cancelado en Mercado Pago"
        : "Payment cancelled on Mercado Pago"
      : isES
        ? "Pago cancelado en PayPal"
        : "Payment cancelled on PayPal";
  })();

  return (
    <div
      role="status"
      className={`mb-8 rounded-xl border px-5 py-4 text-left ${
        isSuccess
          ? "border-[var(--cm-mint)]/40 bg-[var(--cm-mint)]/10"
          : isPending
            ? "border-[var(--cm-outline-variant)]/40 bg-[var(--cm-surface-low)]/60"
            : "border-[var(--cm-outline-variant)]/40 bg-[var(--cm-surface-low)]/60"
      }`}
    >
      <p className="text-sm font-semibold text-white mb-2">{title}</p>
      {ref && (
        <p className="text-xs font-mono text-[var(--cm-on-surface-variant)] mb-2">
          {isES ? "Referencia:" : "Reference:"} {ref}
        </p>
      )}
      {isSuccess ? (
        <div className="space-y-2 text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
          {isProcure ? (
            <>
              <p>
                {isES
                  ? "La activación tarda unos segundos vía webhook. Luego:"
                  : "Activation takes a few seconds via webhook. Then:"}
              </p>
              <ol className="list-decimal list-inside space-y-1 font-mono text-xs">
                <li>{isES ? "market register  (si es cuenta nueva)" : "market register  (if new account)"}</li>
                <li>{isES ? "market account  → copia sk-…" : "market account  → copy sk-…"}</li>
                <li>{isES ? "Pega la API key en el dashboard Procure" : "Paste API key in Procure dashboard"}</li>
              </ol>
              <a href={PROCURE_APP_URL} className="inline-block text-[var(--cm-mint)] text-xs hover:underline">
                {isES ? "Abrir dashboard Procure →" : "Open Procure dashboard →"}
              </a>
            </>
          ) : (
            <>
              <p>
                {isES
                  ? `${planLabel ?? "Tu plan Build"} se activa en minutos. Verifica con market whoami.`
                  : `${planLabel ?? "Your Build plan"} activates within minutes. Verify with market whoami.`}
              </p>
              <p className="font-mono text-xs">{`${MARKET_STATS.pipInstallCmd} && market whoami`}</p>
              <a href="/account" className="inline-block text-[var(--cm-mint)] text-xs hover:underline">
                {isES
                  ? "Confirmar tier en /account (pega tu API key sk-…)"
                  : "Confirm tier on /account (paste your sk-… API key)"}
              </a>
            </>
          )}
        </div>
      ) : isPending ? (
        <div className="space-y-2 text-sm text-[var(--cm-on-surface-variant)]">
          <p>
            {isProcure
              ? isES
                ? "Cuando Mercado Pago confirme el pago, tu plan Procure se activará automáticamente."
                : "When Mercado Pago confirms payment, your Procure plan will activate automatically."
              : isES
                ? "Cuando Mercado Pago confirme el pago, tu plan Build se activará automáticamente."
                : "When Mercado Pago confirms payment, your Build plan will activate automatically."}
          </p>
          <ol className="list-decimal list-inside space-y-1 text-xs">
            {isProcure ? (
              <>
                <li className="font-mono">market register → market account</li>
                <li>{isES ? "Pega sk-… en el dashboard Procure" : "Paste sk-… in Procure dashboard"}</li>
              </>
            ) : (
              <li className="font-mono">market whoami</li>
            )}
            <li>
              {isES
                ? "Si no se activa tras 30 min: hello@cli-market.dev con la referencia de arriba"
                : "If not active after 30 min: email hello@cli-market.dev with the reference above"}
            </li>
          </ol>
          {isProcure ? (
            <a href={PROCURE_APP_URL} className="inline-block text-[var(--cm-mint)] text-xs hover:underline">
              {isES ? "Abrir dashboard Procure →" : "Open Procure dashboard →"}
            </a>
          ) : (
            <a href="/account" className="inline-block text-[var(--cm-mint)] text-xs hover:underline">
              {isES ? "Ver uso en /account →" : "View usage on /account →"}
            </a>
          )}
        </div>
      ) : (
        <p className="text-sm text-[var(--cm-on-surface-variant)]">
          {isES
            ? "Puedes volver a intentar desde el botón de suscripción."
            : "You can try again from the subscribe button."}
        </p>
      )}
      <button
        type="button"
        onClick={() => setVisible(false)}
        className="mt-3 text-xs text-[var(--cm-on-surface-variant)]/70 hover:text-white"
      >
        {isES ? "Cerrar" : "Dismiss"}
      </button>
    </div>
  );
}