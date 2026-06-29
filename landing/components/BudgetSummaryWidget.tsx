"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

type Summary = {
  budget_monthly: number;
  currency: string;
  budget_remaining: number;
  budget_spent_mtd: number;
  days_left_in_period: number;
  projected_overspend_pct: number | null;
  suggested_action: "setup_profile" | "monitor" | "wait" | "buy_now";
};

const ACTION_LABEL: Record<Summary["suggested_action"], { label: string; color: string }> = {
  setup_profile: { label: "Configura tu perfil para ver el pace", color: "text-[var(--cm-on-surface-variant)]" },
  monitor: { label: "Ritmo normal — monitoreando", color: "text-[var(--cm-mint)]" },
  wait: { label: "Vas algo acelerado — esperá antes de comprar", color: "text-[#FFD700]" },
  buy_now: { label: "Presupuesto holgado — buen momento para comprar", color: "text-[var(--cm-mint)]" },
};

type Props = { apiKey: string; refreshKey?: number };

export default function BudgetSummaryWidget({ apiKey, refreshKey }: Props) {
  const [data, setData] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!apiKey) return;
    setLoading(true);
    fetch(`${API_URL}/v1/household/summary`, {
      headers: { Authorization: `Bearer ${apiKey}` },
    })
      .then((r) => r.json())
      .then((b) => setData(b?.data ?? b))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [apiKey, refreshKey]);

  if (!apiKey || (!loading && !data)) return null;

  if (loading) {
    return (
      <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] p-4">
        <div className="h-4 w-32 rounded bg-[var(--cm-on-surface-variant)]/10 animate-pulse" />
      </div>
    );
  }

  if (!data) return null;

  const spentPct = data.budget_monthly > 0
    ? Math.min((data.budget_spent_mtd / data.budget_monthly) * 100, 100)
    : 0;
  const action = ACTION_LABEL[data.suggested_action] ?? ACTION_LABEL.monitor;
  const fmt = (n: number) =>
    n.toLocaleString("es-PE", { minimumFractionDigits: 0, maximumFractionDigits: 0 });

  return (
    <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] p-5 space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]">Presupuesto del mes</p>
        <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]">{data.days_left_in_period}d restantes</p>
      </div>

      {/* Progress bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-sm font-mono">
          <span className="text-[var(--cm-on-surface)]">{data.currency} {fmt(data.budget_spent_mtd)}</span>
          <span className="text-[var(--cm-on-surface-variant)]">/ {data.currency} {fmt(data.budget_monthly)}</span>
        </div>
        <div className="h-2 rounded-full bg-[var(--cm-surface-low)] overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${spentPct}%`,
              backgroundColor: spentPct > 90 ? "#FF4444" : spentPct > 70 ? "#FFD700" : "var(--cm-mint)",
            }}
          />
        </div>
      </div>

      <div className="flex items-start gap-2">
        <span className="w-1.5 h-1.5 rounded-full mt-1 shrink-0" style={{ backgroundColor: spentPct > 90 ? "#FF4444" : spentPct > 70 ? "#FFD700" : "var(--cm-mint)" as string }} />
        <p className={`text-xs font-mono ${action.color}`}>{action.label}</p>
      </div>

      {data.projected_overspend_pct != null && data.projected_overspend_pct > 0 && (
        <p className="text-xs font-mono text-[#FF8C00]">
          Proyección: +{Math.round(data.projected_overspend_pct)}% sobre presupuesto
        </p>
      )}

      <div className="pt-1 border-t border-[var(--cm-outline-variant)]">
        <p className="text-xs font-mono text-[var(--cm-mint)] tabular-nums">
          {data.currency} {fmt(data.budget_remaining)} disponibles
        </p>
      </div>
    </div>
  );
}
