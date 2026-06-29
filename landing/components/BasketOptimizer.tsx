"use client";

import { useState, useEffect } from "react";
import { API_URL } from "@/lib/api";

type Item = { name: string; qty: number };

type Recommendation = {
  action?: string;
  primary_store?: string;
  primary_store_name?: string;
  shelf_total?: number;
  tco_total?: number;
  currency?: string;
  items?: { name: string; store: string; price: number; currency: string; unit_price?: number; unit?: string }[];
};

type ProductLink = { requested: string; resolved_name?: string; url: string; store?: string };

type ActionLink = {
  type: "retailer_deeplink" | "export_list" | string;
  url: string;
  store?: string;
  label?: string;
  token?: string;
};

type ResultData = {
  status?: string;
  recommendation?: Recommendation;
  action_links?: ActionLink[];
  product_links?: ProductLink[];
  substitutes?: { original: string; substitute: string; reason: string }[];
};

type Props = { apiKey: string; country?: string };

const COUNTRIES = ["PE", "MX", "CO", "AR", "CL", "BO", "EC", "UY"];

export default function BasketOptimizer({ apiKey, country: defaultCountry = "PE" }: Props) {
  const [items, setItems] = useState<Item[]>([{ name: "", qty: 1 }]);
  const [country, setCountry] = useState(defaultCountry);

  useEffect(() => { setCountry(defaultCountry); }, [defaultCountry]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResultData | null>(null);
  const [error, setError] = useState("");

  const setItem = (i: number, field: keyof Item, val: string | number) =>
    setItems((prev) => prev.map((it, idx) => idx === i ? { ...it, [field]: val } : it));

  const addItem = () => setItems((prev) => [...prev, { name: "", qty: 1 }]);

  const removeItem = (i: number) =>
    setItems((prev) => prev.length > 1 ? prev.filter((_, idx) => idx !== i) : prev);

  const run = async () => {
    const validItems = items.filter((it) => it.name.trim());
    if (!validItems.length) return;
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const r = await fetch(`${API_URL}/v1/missions/optimize-purchase`, {
        method: "POST",
        headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          country,
          items: validItems.map((it) => ({ name: it.name.trim(), qty: it.qty })),
          constraints: { include_tco: true, allow_substitutes: true, include_action_links: true },
          include_intel: false,
        }),
      });
      const body = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(body.detail ?? `HTTP ${r.status}`);
      setResult(body?.data ?? body);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al optimizar");
    } finally {
      setLoading(false);
    }
  };

  const rec = result?.recommendation;

  return (
    <div className="space-y-5">
      {/* Country selector */}
      <div className="flex items-center gap-3">
        <label className="text-xs font-mono text-[var(--cm-on-surface-variant)] shrink-0">País</label>
        <select
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          className="bg-[var(--cm-surface-low)] border border-[var(--cm-outline-variant)] rounded-lg px-3 py-1.5 text-sm font-mono text-[var(--cm-on-surface)] focus:outline-none focus:border-[var(--cm-mint)]"
        >
          {COUNTRIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      {/* Items list */}
      <div className="space-y-2">
        {items.map((it, i) => (
          <div key={i} className="flex gap-2 items-center">
            <input
              value={it.name}
              onChange={(e) => setItem(i, "name", e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && i === items.length - 1 && addItem()}
              placeholder={`Producto ${i + 1} — ej. leche, arroz 1kg`}
              className="flex-1 bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg px-3 py-2 text-sm font-mono text-[var(--cm-on-surface)] placeholder:text-[var(--cm-on-surface-variant)]/40 focus:outline-none focus:border-[var(--cm-mint)]"
            />
            <input
              type="number"
              min={1}
              max={99}
              value={it.qty}
              onChange={(e) => setItem(i, "qty", Number(e.target.value))}
              className="w-14 bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg px-2 py-2 text-sm font-mono text-center text-[var(--cm-on-surface)] focus:outline-none focus:border-[var(--cm-mint)]"
            />
            <button
              type="button"
              onClick={() => removeItem(i)}
              disabled={items.length === 1}
              className="text-[var(--cm-on-surface-variant)]/50 hover:text-red-400 transition-colors disabled:opacity-20 text-lg leading-none px-1"
            >
              ×
            </button>
          </div>
        ))}
      </div>

      {/* Add item + run */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={addItem}
          className="px-3 py-2 rounded-lg border border-[var(--cm-outline-variant)] text-xs font-mono text-[var(--cm-on-surface-variant)] hover:border-[var(--cm-mint)] hover:text-[var(--cm-on-surface)] transition-colors"
        >
          + Agregar producto
        </button>
        <button
          type="button"
          onClick={run}
          disabled={loading || !items.some((it) => it.name.trim())}
          className="px-5 py-2 rounded-lg bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold font-mono hover:opacity-90 disabled:opacity-40 transition-opacity"
        >
          {loading ? "Optimizando..." : "Optimizar canasta →"}
        </button>
      </div>

      {error && <p className="text-xs font-mono text-red-400">{error}</p>}

      {/* Results */}
      {rec && (
        <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] divide-y divide-[var(--cm-outline-variant)]">
          {/* Summary header */}
          <div className="p-4 space-y-2">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div>
                <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]">Mejor opción</p>
                <p className="text-base font-bold font-mono text-[var(--cm-on-surface)]">
                  {rec.primary_store_name ?? rec.primary_store ?? "—"}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]">Total góndola</p>
                <p className="text-lg font-bold font-mono text-[var(--cm-mint)] tabular-nums">
                  {rec.currency} {rec.shelf_total?.toFixed(2) ?? "—"}
                </p>
                {rec.tco_total != null && rec.tco_total !== rec.shelf_total && (
                  <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/60">
                    TCO {rec.currency} {rec.tco_total?.toFixed(2)}
                  </p>
                )}
              </div>
            </div>
            {rec.action && (
              <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]/70">{rec.action}</p>
            )}
          </div>

          {/* Line items */}
          {(rec.items ?? []).length > 0 && (
            <div className="divide-y divide-[var(--cm-outline-variant)]">
              {rec.items!.map((it, i) => {
                const productLink = result?.product_links?.find(
                  (pl) => pl.requested?.toLowerCase() === it.name.toLowerCase()
                );
                return (
                  <div key={i} className="px-4 py-2.5 flex items-center gap-3">
                    <div className="flex-1 min-w-0">
                      {productLink ? (
                        <a
                          href={productLink.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs font-mono text-[var(--cm-on-surface)] hover:text-[var(--cm-mint)] truncate block transition-colors"
                        >
                          {it.name} ↗
                        </a>
                      ) : (
                        <p className="text-xs font-mono text-[var(--cm-on-surface)] truncate">{it.name}</p>
                      )}
                      <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/60">{it.store}</p>
                    </div>
                    <div className="text-right shrink-0">
                      <p className="text-xs font-mono tabular-nums text-[var(--cm-on-surface)]">
                        {it.currency} {it.price?.toFixed(2)}
                      </p>
                      {it.unit_price != null && (
                        <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/60">
                          {it.currency} {it.unit_price?.toFixed(2)}/{it.unit ?? "u"}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Substitutes */}
          {(result?.substitutes ?? []).length > 0 && (
            <div className="p-4 space-y-2">
              <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)] uppercase tracking-widest">Sustitutos sugeridos</p>
              {result!.substitutes!.map((s, i) => (
                <div key={i} className="flex items-start gap-2 text-xs font-mono">
                  <span className="text-[var(--cm-on-surface-variant)]/60 shrink-0">{s.original} →</span>
                  <span className="text-[var(--cm-mint)]">{s.substitute}</span>
                  <span className="text-[var(--cm-on-surface-variant)]/50 text-[10px]">{s.reason}</span>
                </div>
              ))}
            </div>
          )}

          {/* Action links — primary CTA + secondary */}
          {(result?.action_links ?? []).length > 0 && (() => {
            const resolveUrl = (url: string) =>
              url.startsWith("/") ? `${API_URL}${url}` : url;
            const primaryLink = result!.action_links!.find((lk) => lk.type === "retailer_deeplink")
              ?? result!.action_links![0];
            const secondaryLinks = result!.action_links!.filter((lk) => lk !== primaryLink);
            return (
              <div className="p-4 space-y-3">
                <a
                  href={resolveUrl(primaryLink.url)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 w-full py-3 rounded-xl bg-[var(--cm-mint)] text-[var(--cm-on-mint)] font-semibold font-mono text-sm hover:opacity-90 transition-opacity"
                >
                  <span>Ir al carrito — {rec.primary_store_name ?? rec.primary_store}</span>
                  <span className="text-base leading-none">→</span>
                </a>
                {secondaryLinks.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {secondaryLinks.map((lk, i) => {
                      const secLabel = lk.label
                        ?? (lk.type === "export_list" ? "Exportar lista" : lk.store ?? lk.type);
                      return (
                        <a
                          key={i}
                          href={resolveUrl(lk.url)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-[var(--cm-outline-variant)] text-xs font-mono text-[var(--cm-on-surface-variant)] hover:border-[var(--cm-mint)] hover:text-[var(--cm-on-surface)] transition-colors"
                        >
                          {secLabel} ↗
                        </a>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
}
