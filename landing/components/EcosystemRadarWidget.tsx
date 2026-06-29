"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

type Store = {
  name: string;
  country: string;
  currency: string;
  line: string;
  line_name: string;
  base: string;
};

type Props = { country: string };

const LINE_COLOR: Record<string, string> = {
  supermarket: "var(--cm-mint)",
  wholesale: "#FFD700",
  pharmacy: "#7DD3FC",
  convenience: "#C084FC",
  ecommerce: "#FB923C",
  specialty: "#F472B6",
};

export default function EcosystemRadarWidget({ country }: Props) {
  const [stores, setStores] = useState<Record<string, Store>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!country) return;
    setLoading(true);
    fetch(`${API_URL}/stores?country=${country}`)
      .then((r) => r.json())
      .then((b) => setStores(b?.stores ?? {}))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [country]);

  const list = Object.entries(stores);
  const byLine = list.reduce<Record<string, [string, Store][]>>((acc, entry) => {
    const line = entry[1].line ?? "other";
    (acc[line] ??= []).push(entry);
    return acc;
  }, {});

  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-8 rounded-lg bg-[var(--cm-on-surface-variant)]/10 animate-pulse" />
        ))}
      </div>
    );
  }

  if (!list.length) return <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]/60">Sin datos de retailers para {country}.</p>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-xs font-mono text-[var(--cm-on-surface-variant)] uppercase tracking-widest">Retailers activos</p>
        <span className="text-xs font-mono font-bold text-[var(--cm-mint)]">{list.length}</span>
      </div>

      {Object.entries(byLine).map(([line, entries]) => (
        <div key={line} className="space-y-1.5">
          <p className="text-[10px] font-mono uppercase tracking-wider" style={{ color: LINE_COLOR[line] ?? "var(--cm-on-surface-variant)" }}>
            {entries[0][1].line_name ?? line}
          </p>
          <div className="flex flex-wrap gap-1.5">
            {entries.map(([key, s]) => (
              <span
                key={key}
                className="inline-flex items-center px-2 py-1 rounded-md text-[11px] font-mono border"
                style={{
                  borderColor: (LINE_COLOR[line] ?? "var(--cm-outline-variant)") + "44",
                  color: "var(--cm-on-surface)",
                  backgroundColor: (LINE_COLOR[line] ?? "var(--cm-outline-variant)") + "12",
                }}
              >
                {s.name}
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
