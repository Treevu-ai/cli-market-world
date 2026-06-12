"use client";

import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";

type FunnelStep = { step: string; count: number; drop_off_pct: number | null };

type FunnelData = {
  window_days: number;
  funnel_steps: FunnelStep[];
  conversion: Record<string, number | null>;
  ttfv_median_minutes: number | null;
  ttc_median_hours: number | null;
};

const STEP_LABELS: Record<string, { es: string; en: string }> = {
  install: { es: "CLI install", en: "CLI install" },
  register: { es: "Registro", en: "Register" },
  first_search: { es: "Primera búsqueda", en: "First search" },
  starter_subscribe: { es: "Checkout Starter", en: "Starter checkout" },
  request_pro: { es: "Checkout Pro", en: "Pro checkout" },
  activated: { es: "Activado", en: "Activated" },
};

export default function FunnelMetrics() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [data, setData] = useState<FunnelData | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/analytics/funnel?days=30`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setData(d))
      .catch(() => {});
  }, []);

  if (!data?.funnel_steps?.length) return null;

  const visible = data.funnel_steps.filter((s) => s.count > 0);
  if (visible.length < 2) return null;

  const ttfv = data.ttfv_median_minutes;
  const ttc = data.ttc_median_hours;
  const conv = data.conversion || {};

  return (
    <details className="details-disclosure mt-8 max-w-2xl mx-auto text-left">
      <summary>
        {isES ? "Embudo de onboarding (30 días)" : "Onboarding funnel (30 days)"}
      </summary>
      <div className="details-body pt-4 space-y-3">
        {visible.map((step) => {
          const label = STEP_LABELS[step.step]?.[isES ? "es" : "en"] ?? step.step;
          return (
            <div
              key={step.step}
              className="flex items-center justify-between gap-4 text-sm border-b border-[var(--cm-outline-variant)]/20 pb-2"
            >
              <span className="text-[var(--cm-on-surface-variant)]">{label}</span>
              <span className="font-mono text-white tabular-nums">
                {step.count.toLocaleString()}
                {step.drop_off_pct != null && step.drop_off_pct > 0 ? (
                  <span className="text-[var(--cm-on-surface-variant)]/50 text-xs ml-2">
                    −{step.drop_off_pct}%
                  </span>
                ) : null}
              </span>
            </div>
          );
        })}
        {(ttfv != null || ttc != null || conv.search_to_pro != null) && (
          <div className="text-xs text-[var(--cm-on-surface-variant)]/70 pt-2 space-y-1">
            {ttfv != null && (
              <p>
                {isES
                  ? `TTFV mediana: ${ttfv} min (registro → primera búsqueda)`
                  : `Median TTFV: ${ttfv} min (register → first search)`}
              </p>
            )}
            {ttc != null && (
              <p>
                {isES
                  ? `TTC mediana: ${ttc} h (checkout Pro → activado)`
                  : `Median TTC: ${ttc} h (Pro checkout → activated)`}
              </p>
            )}
            {conv.search_to_pro != null && (
              <p>
                {isES ? "Conversión búsqueda → Pro:" : "Search → Pro conversion:"}{" "}
                <span className="font-mono text-white/80">
                  {(Number(conv.search_to_pro) * 100).toFixed(1)}%
                </span>
              </p>
            )}
          </div>
        )}
      </div>
    </details>
  );
}