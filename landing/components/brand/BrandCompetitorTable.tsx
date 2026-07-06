"use client";

import type { SkuRow } from "./BrandSkuTable";

interface CompetitorGroup {
  brand: string;
  skus: SkuRow[];
  minPrice: number;
  maxPrice: number;
  promoCount: number;
  currency: string;
}

function groupByBrand(skus: SkuRow[]): CompetitorGroup[] {
  const map = new Map<string, SkuRow[]>();
  for (const s of skus) {
    const key = s.brand;
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(s);
  }
  return Array.from(map.entries()).map(([brand, rows]) => ({
    brand,
    skus: rows,
    minPrice: Math.min(...rows.map((r) => r.price)),
    maxPrice: Math.max(...rows.map((r) => r.price)),
    promoCount: rows.filter((r) => r.promo_active).length,
    currency: rows[0].currency,
  }));
}

interface Props {
  myBrand: string;
  mySkus: SkuRow[];
  competitorSkus: SkuRow[];
}

export default function BrandCompetitorTable({ myBrand, mySkus, competitorSkus }: Props) {
  const myGroup: CompetitorGroup = {
    brand: myBrand,
    skus: mySkus,
    minPrice: mySkus.length ? Math.min(...mySkus.map((s) => s.price)) : 0,
    maxPrice: mySkus.length ? Math.max(...mySkus.map((s) => s.price)) : 0,
    promoCount: mySkus.filter((s) => s.promo_active).length,
    currency: mySkus[0]?.currency ?? "PEN",
  };

  const compGroups = groupByBrand(competitorSkus);
  const allGroups = [myGroup, ...compGroups].filter((g) => g.skus.length > 0);

  if (allGroups.length === 0) {
    return (
      <p className="text-[var(--cm-text-secondary)] text-sm py-8 text-center">
        Sin datos de competidores.{" "}
        <span className="text-[var(--cm-data)]">
          Agrega competidores con <code className="font-mono">?competitors=Laive,Nestlé</code> en la URL
          o vía <code className="font-mono">POST /v1/brand-monitor/config</code>.
        </span>
      </p>
    );
  }

  const globalMin = Math.min(...allGroups.map((g) => g.minPrice).filter(Boolean));

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-white/10 text-[var(--cm-text-secondary)] text-xs uppercase tracking-wider">
              <th className="text-left py-2 pr-4 font-medium">Marca</th>
              <th className="text-right py-2 pr-4 font-mono font-medium">Precio mín</th>
              <th className="text-right py-2 pr-4 font-mono font-medium">Precio máx</th>
              <th className="text-right py-2 pr-4 font-medium">SKUs</th>
              <th className="text-right py-2 pr-4 font-medium">Promos activas</th>
              <th className="text-left py-2 font-medium">Precio relativo</th>
            </tr>
          </thead>
          <tbody>
            {allGroups.map((g) => {
              const isMe = g.brand === myBrand;
              const ratio = globalMin > 0 ? g.minPrice / globalMin : 1;
              const barWidth = Math.min(100, Math.round((ratio - 1) * 200 + 10));
              return (
                <tr
                  key={g.brand}
                  className={`border-b border-white/5 hover:bg-white/[0.02] transition-colors ${
                    isMe ? "bg-[var(--cm-data)]/[0.03]" : ""
                  }`}
                >
                  <td className="py-2 pr-4 whitespace-nowrap">
                    <span
                      className={`font-medium ${
                        isMe ? "text-[var(--cm-data)]" : "text-[var(--cm-ink)]"
                      }`}
                    >
                      {g.brand}
                      {isMe && (
                        <span className="ml-2 text-[10px] text-[var(--cm-data)] border border-[var(--cm-data)]/30 rounded px-1">
                          TÚ
                        </span>
                      )}
                    </span>
                  </td>
                  <td className="py-2 pr-4 text-right font-mono text-[var(--cm-ink)] whitespace-nowrap">
                    {g.currency} {g.minPrice.toFixed(2)}
                  </td>
                  <td className="py-2 pr-4 text-right font-mono text-[var(--cm-text-secondary)] whitespace-nowrap">
                    {g.currency} {g.maxPrice.toFixed(2)}
                  </td>
                  <td className="py-2 pr-4 text-right text-[var(--cm-text-secondary)]">
                    {g.skus.length}
                  </td>
                  <td className="py-2 pr-4 text-right">
                    {g.promoCount > 0 ? (
                      <span className="text-xs font-mono text-[var(--cm-action)] bg-[var(--cm-action-soft)] border border-[var(--cm-action)]/30 rounded px-1 py-0.5">
                        {g.promoCount}
                      </span>
                    ) : (
                      <span className="text-[var(--cm-text-secondary)] text-xs">0</span>
                    )}
                  </td>
                  <td className="py-2">
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 bg-white/5 rounded-full w-32 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            isMe ? "bg-[var(--cm-data)]" : "bg-[var(--cm-text-secondary)]"
                          }`}
                          style={{ width: `${Math.max(4, barWidth)}%` }}
                        />
                      </div>
                      <span className="text-xs font-mono text-[var(--cm-text-secondary)]">
                        {ratio.toFixed(2)}×
                      </span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Expanded rows per competitor */}
      {compGroups.map((g) => (
        <details key={g.brand} className="group">
          <summary className="text-xs text-[var(--cm-text-secondary)] cursor-pointer hover:text-[var(--cm-data)] transition-colors py-1">
            Ver SKUs de {g.brand} ({g.skus.length})
          </summary>
          <div className="overflow-x-auto mt-2 pl-4 border-l border-white/10">
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr className="text-[var(--cm-text-secondary)] border-b border-white/10">
                  <th className="text-left py-1 pr-3 font-medium">Producto</th>
                  <th className="text-left py-1 pr-3 font-medium">Tienda</th>
                  <th className="text-right py-1 pr-3 font-mono font-medium">Precio</th>
                  <th className="text-center py-1 font-medium">Promo</th>
                </tr>
              </thead>
              <tbody>
                {g.skus.map((s, i) => (
                  <tr key={i} className="border-b border-white/5">
                    <td className="py-1 pr-3 text-[var(--cm-ink)] max-w-[200px] truncate" title={s.name}>
                      {s.name}
                    </td>
                    <td className="py-1 pr-3 text-[var(--cm-text-secondary)]">{s.store_name}</td>
                    <td className="py-1 pr-3 text-right font-mono text-[var(--cm-ink)]">
                      {s.currency} {s.price.toFixed(2)}
                    </td>
                    <td className="py-1 text-center">
                      {s.promo_active ? (
                        <span className="text-[var(--cm-action)] text-[10px]">
                          {s.discount ? `-${s.discount}%` : "PROMO"}
                        </span>
                      ) : (
                        <span className="text-[var(--cm-text-secondary)] text-[10px]">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      ))}
    </div>
  );
}
