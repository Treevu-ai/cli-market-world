"use client";

import { useLiveStats } from "@/hooks/useLiveStats";
import { useLang } from "@/lib/LanguageContext";

export default function MoatSparkline() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { stats, liveLoaded } = useLiveStats();
  const inventoryDaily = stats.inventoryDaily;

  if (!liveLoaded || !inventoryDaily?.length) return null;

  const points = inventoryDaily.slice(-14);
  const values = points.map((p) => p.snapshots);
  const max = Math.max(...values, 1);
  const min = Math.min(...values);
  const w = 200;
  const h = 48;
  const pad = 4;

  const coords = values.map((v, i) => {
    const x = pad + (i / Math.max(values.length - 1, 1)) * (w - pad * 2);
    const y = h - pad - ((v - min) / Math.max(max - min, 1)) * (h - pad * 2);
    return `${x},${y}`;
  });

  const last = points[points.length - 1];

  return (
    <div className="card-cyber p-5 text-left">
      <p className="text-xs uppercase tracking-widest text-[var(--cm-on-surface-variant)]/60 mb-2">
        {isES ? "Histórico del moat (14d)" : "Moat history (14d)"}
      </p>
      <svg
        viewBox={`0 0 ${w} ${h}`}
        className="w-full max-w-[240px] h-12 text-[var(--cm-data)]"
        role="img"
        aria-label={
          isES
            ? `Serie de snapshots diarios, último día ${last.day}`
            : `Daily snapshot series, last day ${last.day}`
        }
      >
        <polyline
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinejoin="round"
          strokeLinecap="round"
          points={coords.join(" ")}
        />
      </svg>
      <p className="text-xs text-[var(--cm-on-surface-variant)] mt-2 font-mono tabular-nums">
        {last.day}: {last.snapshots.toLocaleString()} snapshots
      </p>
    </div>
  );
}
