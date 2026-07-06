"use client";

export interface SkuRow {
  product_id: string;
  name: string;
  brand: string;
  store: string;
  store_name: string;
  price: number;
  list_price: number | null;
  discount: number | null;
  currency: string;
  queried_at: string;
  promo_active: boolean;
  dispersion_score: number | null;
  pvp_suggested: number | null;
  pvp_deviation_pct: number | null;
  pvp_alert: "above_pvp" | "far_below_pvp" | null;
}

function DeviationBadge({ pct, alert }: { pct: number | null; alert: SkuRow["pvp_alert"] }) {
  if (pct === null) return <span className="text-[var(--cm-text-secondary)] text-xs">—</span>;
  const color =
    alert === "above_pvp"
      ? "text-[var(--cm-signal)] border-[var(--cm-signal)]/30"
      : alert === "far_below_pvp"
      ? "text-red-400 border-red-400/30"
      : "text-[var(--cm-data)] border-[var(--cm-data)]/30";
  const sign = pct > 0 ? "+" : "";
  return (
    <span className={`text-xs font-mono border rounded px-1 py-0.5 ${color}`}>
      {sign}{pct}%
    </span>
  );
}

function PromoBadge({ active, discount }: { active: boolean; discount: number | null }) {
  if (!active) return <span className="text-[var(--cm-text-secondary)] text-xs">—</span>;
  return (
    <span className="text-xs font-mono bg-[var(--cm-action-soft)] text-[var(--cm-action)] border border-[var(--cm-action)]/30 rounded px-1 py-0.5">
      {discount ? `-${discount}%` : "PROMO"}
    </span>
  );
}

function freshnessLabel(queried_at: string): string {
  const diff = Date.now() - new Date(queried_at).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return "< 1h";
  if (h < 24) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}

interface Props {
  skus: SkuRow[];
  hasPvp: boolean;
}

export default function BrandSkuTable({ skus, hasPvp }: Props) {
  if (skus.length === 0) {
    return (
      <p className="text-[var(--cm-text-secondary)] text-sm py-8 text-center">
        No se encontraron SKUs para esta marca en el moat.{" "}
        <span className="text-[var(--cm-data)]">
          El collector indexa SKUs de marcas con cobertura en Plaza Vea, Metro y Wong PE.
        </span>
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b border-white/10 text-[var(--cm-text-secondary)] text-xs uppercase tracking-wider">
            <th className="text-left py-2 pr-4 font-medium">Producto</th>
            <th className="text-left py-2 pr-4 font-medium">Tienda</th>
            <th className="text-right py-2 pr-4 font-mono font-medium">Precio</th>
            {hasPvp && <th className="text-right py-2 pr-4 font-mono font-medium">PVP</th>}
            {hasPvp && <th className="text-right py-2 pr-4 font-medium">Desvío</th>}
            <th className="text-center py-2 pr-4 font-medium">Promo</th>
            <th className="text-right py-2 font-mono font-medium">Dispersión</th>
            <th className="text-right py-2 pl-4 font-medium text-xs">Actualizado</th>
          </tr>
        </thead>
        <tbody>
          {skus.map((s, i) => (
            <tr
              key={`${s.product_id}-${s.store}-${i}`}
              className={`border-b border-white/5 hover:bg-white/[0.02] transition-colors ${
                s.pvp_alert ? "bg-[var(--cm-signal)]/[0.03]" : ""
              }`}
            >
              <td className="py-2 pr-4 text-[var(--cm-ink)] max-w-[220px]">
                <span className="block truncate" title={s.name}>{s.name}</span>
              </td>
              <td className="py-2 pr-4 text-[var(--cm-text-secondary)] whitespace-nowrap">
                {s.store_name}
              </td>
              <td className="py-2 pr-4 text-right font-mono text-[var(--cm-ink)] whitespace-nowrap">
                {s.currency} {s.price.toFixed(2)}
              </td>
              {hasPvp && (
                <td className="py-2 pr-4 text-right font-mono text-[var(--cm-text-secondary)] whitespace-nowrap">
                  {s.pvp_suggested !== null ? `${s.currency} ${s.pvp_suggested.toFixed(2)}` : "—"}
                </td>
              )}
              {hasPvp && (
                <td className="py-2 pr-4 text-right">
                  <DeviationBadge pct={s.pvp_deviation_pct} alert={s.pvp_alert} />
                </td>
              )}
              <td className="py-2 pr-4 text-center">
                <PromoBadge active={s.promo_active} discount={s.discount} />
              </td>
              <td className="py-2 text-right font-mono text-xs text-[var(--cm-text-secondary)]">
                {s.dispersion_score !== null ? (s.dispersion_score * 100).toFixed(1) + "%" : "—"}
              </td>
              <td className="py-2 pl-4 text-right text-xs text-[var(--cm-text-secondary)] whitespace-nowrap">
                {freshnessLabel(s.queried_at)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
