"use client";

import { useState, useEffect } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import { MARKET_STATS } from "@/lib/marketStats";
import { AuthProvider, useApiKey } from "@/lib/useApiKey";
import ApiKeyGate from "@/components/dashboard/ApiKeyGate";
import ProSubscribeButton from "@/components/ProSubscribeButton";
import BillingCheckoutTrigger from "@/components/BillingCheckoutTrigger";

type AccountData = {
  username: string;
  tier: string;
  limits: {
    req_day: number | string;
    req_min: number | string;
    api_keys: number | string;
    checkout: boolean;
    alerts: number;
    export: boolean;
  };
  usage: {
    requests_today: number;
    requests_last_minute: number;
    api_keys_used: number;
    daily_pct?: number | null;
    minute_pct?: number | null;
  };
  upgrade: {
    next_tier?: string | null;
    title?: string;
    cli?: string;
    url?: string | null;
    cta?: string | null;
  };
  billing?: {
    state?: string;
    activation?: string | null;
    request_id?: string | null;
    approve_url?: string | null;
    message?: string | null;
    eta?: string | null;
    verify_cli?: string | null;
  };
};

function UsageBar({
  used,
  limit,
  label,
}: {
  used: number;
  limit: number | string;
  label: string;
}) {
  const unlimited = limit === "unlimited" || limit === -1;
  const lim = typeof limit === "number" ? limit : 0;
  const pct = unlimited || !lim ? 0 : Math.min((used / lim) * 100, 100);

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-[var(--cm-on-surface-variant)]">
        <span>{label}</span>
        <span className="font-mono tabular-nums">
          {unlimited ? `${used.toLocaleString()} / ∞` : `${used.toLocaleString()} / ${lim.toLocaleString()}`}
        </span>
      </div>
      <div className="h-2 rounded-full bg-[var(--cm-surface-high)] overflow-hidden">
        <div
          className="h-full bg-[var(--cm-mint)] transition-all duration-300"
          style={{ width: unlimited ? "8%" : `${pct}%` }}
        />
      </div>
    </div>
  );
}

/** /account lives outside app/dashboard/*, so it doesn't get that layout's
 *  AuthProvider — this component supplies its own, making it self-sufficient
 *  wherever it's mounted. */
export default function AccountDashboard() {
  return (
    <AuthProvider>
      <AccountDashboardInner />
    </AuthProvider>
  );
}

function AccountDashboardInner() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { apiKey } = useApiKey();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState<AccountData | null>(null);

  const load = async (key: string) => {
    setError("");
    setLoading(true);
    try {
      const r = await fetch(`${API_URL}/auth/account?lang=${isES ? "es" : "en"}`, {
        headers: { Authorization: `Bearer ${key}` },
      });
      const body = await r.json().catch(() => ({}));
      if (!r.ok) {
        setError(body.detail || body.error || `HTTP ${r.status}`);
        setData(null);
        return;
      }
      setData(body);
    } catch {
      setError(isES ? "Error de red" : "Network error");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  // Persisted key (via ApiKeyGate/useApiKey) loads the account automatically
  // -- no separate manual "view account" click needed once entered.
  useEffect(() => {
    if (apiKey) load(apiKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiKey]);

  return (
    <section className="landing-section animate-fade-in">
      <div className="landing-container-narrow">
        <p className="section-eyebrow mb-4 text-[var(--cm-mint)] text-center">
          {isES ? "Su cuenta" : "Your account"}
        </p>
        <h1 className="section-title text-center mb-2">
          {isES ? "Dashboard de uso" : "Usage dashboard"}
        </h1>
        <p className="text-sm text-[var(--cm-on-surface-variant)] text-center max-w-lg mx-auto mb-8">
          {isES
            ? "Consulte tier, límites y consumo. La API key se guarda solo en este navegador."
            : "View tier, limits, and consumption. Your API key is stored only in this browser."}
        </p>

        {!apiKey && (
          <div className="card-cyber p-5 max-w-xl mx-auto mb-6 space-y-3 border border-[var(--cm-outline-variant)]/30">
            <h2 className="text-sm font-bold text-[var(--cm-mint)] uppercase tracking-wider">
              {isES ? "Primeros pasos" : "Getting started"}
            </h2>
            <ol className="list-decimal list-inside space-y-2 text-sm text-[var(--cm-on-surface-variant)]">
              <li>
                <span className="font-mono text-xs text-[var(--cm-on-surface)]">{MARKET_STATS.pipInstallCmd}</span>
              </li>
              <li>
                <span className="font-mono text-xs text-[var(--cm-on-surface)]">market init</span>
                <span className="text-xs text-[var(--cm-on-surface-variant)]">
                  {isES ? " — cuenta + primera búsqueda" : " — account + first search"}
                </span>
              </li>
              <li>
                {isES
                  ? "Copia la API key (sk-…) y pégala abajo"
                  : "Copy your API key (sk-…) and paste it below"}
              </li>
            </ol>
            <a href="/docs#quickstart" className="text-xs text-[var(--cm-mint)] hover:underline inline-block">
              {isES ? "Guía completa →" : "Full guide →"}
            </a>
          </div>
        )}

        {!apiKey ? (
          <ApiKeyGate />
        ) : (
          loading && (
            <p className="text-sm text-[var(--cm-on-surface-variant)] text-center">
              {isES ? "Cargando..." : "Loading..."}
            </p>
          )
        )}
        {error && <p className="text-sm text-red-600 text-center mt-2">{error}</p>}

        {data && (
          <div className="mt-10 grid gap-4 md:grid-cols-2 max-w-3xl mx-auto">
            <div className="card-cyber p-5 space-y-3">
              <h2 className="text-sm font-bold text-[var(--cm-mint)] uppercase tracking-wider">
                {isES ? "Plan" : "Plan"}
              </h2>
              <p className="text-2xl font-black text-[var(--cm-on-surface)] capitalize">{data.tier}</p>
              <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]">
                {data.username}
              </p>
              <ul className="text-sm text-[var(--cm-on-surface-variant)] space-y-1">
                <li>
                  {isES ? "Checkout" : "Checkout"}: {data.limits.checkout ? "✓" : "—"}
                </li>
                <li>
                  {isES ? "Export" : "Export"}: {data.limits.export ? "✓" : "—"}
                </li>
                <li>
                  {isES ? "Alertas" : "Alerts"}: {data.limits.alerts}
                </li>
              </ul>
            </div>

            {data.billing?.message && (
              <div className="card-cyber p-5 md:col-span-2 space-y-2 border border-yellow-500/20 bg-yellow-500/5">
                <h2 className="text-sm font-bold text-yellow-400 uppercase tracking-wider">
                  {isES ? "Facturación" : "Billing"}
                </h2>
                <p className="text-sm text-[var(--cm-on-surface-variant)]">{data.billing.message}</p>
                {data.billing.eta && (
                  <p className="text-xs text-[var(--cm-on-surface-variant)]">
                    {isES ? "ETA activación:" : "Activation ETA:"}{" "}
                    <span className="font-mono text-yellow-300/90">{data.billing.eta}</span>
                  </p>
                )}
                {data.billing.verify_cli && (
                  <p className="text-xs font-mono text-[var(--cm-mint)]">
                    {data.billing.verify_cli}
                  </p>
                )}
                {data.billing.request_id && (
                  <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]/70">
                    ref: {data.billing.request_id}
                  </p>
                )}
                {data.billing.approve_url && data.billing.activation === "auto" && (
                  <a
                    href={data.billing.approve_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-mint inline-flex text-sm"
                  >
                    {isES ? "Confirmar en PayPal →" : "Confirm on PayPal →"}
                  </a>
                )}
              </div>
            )}

            <div className="card-cyber p-5 space-y-4">
              <h2 className="text-sm font-bold text-[var(--cm-mint)] uppercase tracking-wider">
                {isES ? "Uso" : "Usage"}
              </h2>
              <UsageBar
                used={data.usage.requests_today}
                limit={data.limits.req_day}
                label={isES ? "Hoy" : "Today"}
              />
              <UsageBar
                used={data.usage.requests_last_minute}
                limit={data.limits.req_min}
                label={isES ? "Último minuto" : "Last minute"}
              />
              <p className="text-xs text-[var(--cm-on-surface-variant)]">
                API keys: {data.usage.api_keys_used} / {String(data.limits.api_keys)}
              </p>
            </div>

            {data.upgrade?.next_tier && (
              <div className="card-cyber p-5 md:col-span-2 space-y-4 border border-[var(--cm-mint)]/20">
                <h2 className="text-sm font-bold text-[var(--cm-mint)] uppercase tracking-wider">
                  {isES ? "Siguiente paso" : "Next step"}
                </h2>
                <p className="text-[var(--cm-on-surface)] font-semibold">{data.upgrade.title}</p>
                {data.upgrade.cli && (
                  <pre className="code-snippet text-xs text-[var(--cm-mint)] bg-black/30 p-3 rounded-lg overflow-x-auto">
                    {data.upgrade.cli}
                  </pre>
                )}
                {data.upgrade.next_tier === "pro" ? (
                  <div id="account-pro-upgrade" className="space-y-3">
                    <ProSubscribeButton />
                  </div>
                ) : data.upgrade.next_tier === "starter" ? (
                  <div id="account-starter-upgrade" className="space-y-3">
                    <BillingCheckoutTrigger kind={{ type: "build-starter" }} />
                  </div>
                ) : data.upgrade.url ? (
                  <a href={data.upgrade.url} className="btn-mint inline-flex">
                    {data.upgrade.cta || (isES ? "Ver planes →" : "View plans →")}
                  </a>
                ) : null}
                <div className="flex flex-wrap gap-x-4 gap-y-2 pt-1">
                  <a href="/build#pricing" className="text-xs text-[var(--cm-mint)] hover:underline">
                    {isES ? "Comparar planes Build →" : "Compare Build plans →"}
                  </a>
                  <a href="/docs#billing" className="text-xs text-[var(--cm-mint)] hover:underline">
                    {isES ? "Facturación Sinapsis →" : "Sinapsis billing →"}
                  </a>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}