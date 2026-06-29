"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

type InflationItem = {
  product: string;
  delta_pct: number;
  last_price: number;
  first_price: number;
  currency: string;
  store: string;
};

type InflationData = {
  avg_inflation_pct: number;
  products_tracked: number;
  days: number;
  items: InflationItem[];
};

type Props = { country: string; apiKey: string };

export default function InflationPulseWidget({ country, apiKey }: Props) {
  const [data, setData] = useState<InflationData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!country || !apiKey) return;
    setLoading(true);
    fetch(`${API_URL}/v1/intel/inflation?country=${country}&days=30&limit=8`, {
      headers: { Authorization: `Bearer ${apiKey}` },
    })
      .then((r) => r.json())
      .then((b) => setData(b?.data ?? b))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [country, apiKey]);

  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-8 rounded-lg bg-[var(--cm-on-surface-variant)]/10 animate-pulse" />
        ))}
      </div>
    );
  }

  if (!data) return null;

  const avg = data.avg_inflation_pct ?? 0;
  const avgColor = avg > 5 ? "#FF4444" : avg > 2 ? "#FFD700" : "var(--cm-mint)";

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-mono text-[var(--cm-on-surface-variant)] uppercase tracking-widest">Pulso inflación</p>
          <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/50 mt-0.5">últimos {data.days} días · {data.products_tracked} productos</p>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold font-mono tabular-nums" style={{ color: avgColor }}>
            {avg > 0 ? "+" : ""}{avg.toFixed(1)}%
          </p>
          <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/50">variación media</p>
        </div>
      </div>

      {/* Item list */}
      {data.items.length > 0 && (
        <div className="space-y-1">
          {data.items.slice(0, 6).map((it, i) => {
            const up = it.delta_pct > 0;
            const color = up ? (it.delta_pct > 5 ? "#FF4444" : "#FFD700") : "var(--cm-mint)";
            const barPct = Math.min(Math.abs(it.delta_pct) / 20 * 100, 100);
            return (
              <div key={i} className="flex items-center gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-[11px] font-mono text-[var(--cm-on-surface)] truncate">{it.product}</p>
                  <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/50 truncate">{it.store}</p>
                </div>
                {/* Mini bar */}
                <div className="w-16 h-1.5 rounded-full bg-[var(--cm-surface-low)] overflow-hidden shrink-0">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{ width: `${barPct}%`, backgroundColor: color }}
                  />
                </div>
                <p className="text-[11px] font-mono tabular-nums shrink-0 w-12 text-right" style={{ color }}>
                  {up ? "+" : ""}{it.delta_pct.toFixed(1)}%
                </p>
              </div>
            );
          })}
        </div>
      )}

      {data.items.length === 0 && (
        <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]/60">Sin datos suficientes para {country}.</p>
      )}

      <p className="text-[9px] font-mono text-[var(--cm-on-surface-variant)]/40 leading-relaxed">
        Señal interna del data moat — no es IPC oficial. Variación por unidad base para filtrar cambios de presentación.
      </p>
    </div>
  );
}
