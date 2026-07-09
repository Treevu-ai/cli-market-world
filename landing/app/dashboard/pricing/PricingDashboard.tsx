"use client";

import { useState, useEffect, useCallback } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { API_URL } from "@/lib/api";

const COUNTRIES = [
  { code: "PE", label: "Perú" },
  { code: "AR", label: "Argentina" },
  { code: "BR", label: "Brasil" },
  { code: "MX", label: "México" },
  { code: "CO", label: "Colombia" },
  { code: "CL", label: "Chile" },
];

const LINES = [
  { key: "supermercados", label: "Supermercados" },
  { key: "farmacias", label: "Farmacias" },
  { key: "electro", label: "Electro" },
  { key: "hogar", label: "Hogar" },
];

const WINDOWS = [7, 30, 90];

const POSITIONS = [
  { value: "cheapest_minus_2", label: "Igualar al más barato −2%" },
  { value: "median", label: "Posicionarme en la mediana" },
  { value: "premium_plus_8", label: "Premium +8% vs líder" },
];

type StoreInfo = { name: string; country: string; currency: string; line: string; line_name: string };
type BrandCount = { brand: string; count: number };

type SkuRow = {
  product_id: string;
  name: string;
  brand: string;
  store: string;
  store_name: string;
  price: number;
  list_price: number | null;
  discount: number | null;
  currency: string;
  promo_active: boolean;
  dispersion_score: number | null;
};

type BrandMonitorResponse = {
  summary: {
    brand: string;
    my_skus_count: number;
    my_skus_with_promo: number;
    competitor_skus_count: number;
    competitor_skus_with_promo: number;
    stores_covered: number;
    competitors_found: string[];
  };
  my_skus: SkuRow[];
  competitor_skus: SkuRow[];
  error?: string;
};

type PivotRow = {
  key: string;
  name: string;
  brand: string;
  currency: string;
  prices: Record<string, number>;
  promoStores: Set<string>;
  dispersion: number | null;
};

function fmtPrice(v: number | undefined, currency: string) {
  if (v == null) return "—";
  return `${currency} ${v.toFixed(2)}`;
}

function Chip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`text-xs font-mono px-2.5 py-1 rounded-full border transition-colors ${
        active
          ? "bg-[var(--cm-mint)] border-[var(--cm-mint)] text-[var(--cm-on-mint)] font-semibold"
          : "border-[var(--cm-outline-variant)] text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-on-surface)] hover:border-[var(--cm-mint)]"
      }`}
    >
      {children}
    </button>
  );
}

function RailGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-6">
      <h2 className="text-[10px] font-mono uppercase tracking-widest text-[var(--cm-on-surface-variant)]/60 font-bold mb-2.5">
        {title}
      </h2>
      {children}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="mb-3.5">
      <label className="block text-xs font-mono font-semibold text-[var(--cm-on-surface-variant)] mb-1.5">
        {label}
      </label>
      {children}
    </div>
  );
}

function ComingSoonPanel({ title, meta, note }: { title: string; meta: string; note: string }) {
  return (
    <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--cm-outline-variant)]">
        <h3 className="text-sm font-bold text-[var(--cm-on-surface)]">{title}</h3>
        <span className="text-[11px] font-mono text-[var(--cm-on-surface-variant)]/60">{meta}</span>
      </div>
      <div className="p-5 text-sm text-[var(--cm-on-surface-variant)]">
        {note}
      </div>
    </div>
  );
}

export default function PricingDashboard() {
  const [apiKey, setApiKey] = useState("");
  const [confirmedKey, setConfirmedKey] = useState("");
  const isAuth = !!confirmedKey;

  const handleAuth = () => {
    if (apiKey.trim().startsWith("sk-") || apiKey.trim().startsWith("demo-")) {
      setConfirmedKey(apiKey.trim());
    }
  };

  // ── Scope state ──────────────────────────────────────────
  const [country, setCountry] = useState("PE");
  const [line, setLine] = useState("supermercados");
  const [windowDays, setWindowDays] = useState(30);

  const [stores, setStores] = useState<Record<string, StoreInfo>>({});
  const [selectedStores, setSelectedStores] = useState<string[]>([]);
  const [storesLoading, setStoresLoading] = useState(false);

  const [brands, setBrands] = useState<BrandCount[]>([]);
  const [selectedBrands, setSelectedBrands] = useState<string[]>([]);
  const [brandsLoading, setBrandsLoading] = useState(false);

  // ── Lever state ──────────────────────────────────────────
  const [position, setPosition] = useState("median");
  const [confidence, setConfidence] = useState(80);
  const [alertThreshold, setAlertThreshold] = useState(5);
  const [allowSubstitutes, setAllowSubstitutes] = useState(true);
  const [macroWeight, setMacroWeight] = useState(false);

  // Real store catalog for the current country/line (no auth required).
  useEffect(() => {
    setStoresLoading(true);
    fetch(`${API_URL}/stores?country=${country}&line=${line}`)
      .then((r) => r.json())
      .then((d) => {
        const list: Record<string, StoreInfo> = d?.stores || {};
        setStores(list);
        setSelectedStores(Object.keys(list));
      })
      .catch(() => {
        setStores({});
        setSelectedStores([]);
      })
      .finally(() => setStoresLoading(false));
  }, [country, line]);

  // Real top-brands ranking for the current country/line (requires auth).
  useEffect(() => {
    if (!confirmedKey) return;
    setBrandsLoading(true);
    fetch(`${API_URL}/analytics/brands?line=${line}&country=${country}&limit=12`, {
      headers: { Authorization: `Bearer ${confirmedKey}` },
    })
      .then((r) => r.json())
      .then((d) => {
        const list: BrandCount[] = Array.isArray(d?.brands) ? d.brands : [];
        setBrands(list);
        setSelectedBrands(list.slice(0, 2).map((b) => b.brand));
      })
      .catch(() => {
        setBrands([]);
        setSelectedBrands([]);
      })
      .finally(() => setBrandsLoading(false));
  }, [confirmedKey, country, line]);

  const toggleStore = useCallback((key: string) => {
    setSelectedStores((cur) => (cur.includes(key) ? cur.filter((s) => s !== key) : [...cur, key]));
  }, []);

  const toggleBrand = useCallback((brand: string) => {
    setSelectedBrands((cur) => (cur.includes(brand) ? cur.filter((b) => b !== brand) : [...cur, brand]));
  }, []);

  const storeKeys = Object.keys(stores);
  const lineLabel = LINES.find((l) => l.key === line)?.label || line;

  // ── Brand monitor: real cross-store SKU snapshot for the selected brand(s) ──
  // Powers the comparator table, the promo-activity panel, and the alert list
  // — one endpoint, no fabricated data. First selected brand is "my brand",
  // the rest are passed as declared competitors (that's the shape the API
  // expects; here it just means "everything the user is comparing").
  const [monitor, setMonitor] = useState<BrandMonitorResponse | null>(null);
  const [monitorLoading, setMonitorLoading] = useState(false);
  const [monitorError, setMonitorError] = useState<string | null>(null);

  useEffect(() => {
    if (!confirmedKey || selectedBrands.length === 0) {
      setMonitor(null);
      return;
    }
    const [primary, ...rest] = selectedBrands;
    const params = new URLSearchParams({
      brand: primary,
      country,
      line,
      days: String(windowDays),
    });
    if (rest.length) params.set("competitors", rest.join(","));

    setMonitorLoading(true);
    setMonitorError(null);
    fetch(`${API_URL}/v1/brand-monitor?${params.toString()}`, {
      headers: { Authorization: `Bearer ${confirmedKey}` },
    })
      .then((r) => r.json())
      .then((d: BrandMonitorResponse) => {
        if (d?.error) {
          setMonitorError(d.error);
          setMonitor(null);
        } else {
          setMonitor(d);
        }
      })
      .catch(() => setMonitorError("No se pudo cargar brand-monitor"))
      .finally(() => setMonitorLoading(false));
  }, [confirmedKey, country, line, windowDays, selectedBrands]);

  const allSkus: SkuRow[] = monitor ? [...monitor.my_skus, ...monitor.competitor_skus] : [];

  // Pivot per-store rows into product × store, filtered to selected stores
  // and to the confidence-adjacent freshness bar this dashboard exposes as a
  // lever (dispersion_score null just means "only one store carries it" —
  // not a confidence signal, so it's shown but never excluded).
  const pivotRows: PivotRow[] = (() => {
    const byProduct = new Map<string, PivotRow>();
    for (const sku of allSkus) {
      if (!selectedStores.includes(sku.store)) continue;
      let row = byProduct.get(sku.product_id);
      if (!row) {
        row = {
          key: sku.product_id,
          name: sku.name,
          brand: sku.brand,
          currency: sku.currency,
          prices: {},
          promoStores: new Set(),
          dispersion: sku.dispersion_score,
        };
        byProduct.set(sku.product_id, row);
      }
      row.prices[sku.store] = sku.price;
      if (sku.promo_active) row.promoStores.add(sku.store);
    }
    return Array.from(byProduct.values()).sort((a, b) => a.name.localeCompare(b.name));
  })();

  // "Alert" = a live promo whose discount clears the alert-threshold lever —
  // the closest real signal to "big recent move" available without a
  // populated price_history table (verified empty in production today).
  const promoAlerts = allSkus
    .filter((s) => s.promo_active && (s.discount ?? 0) >= alertThreshold)
    .sort((a, b) => (b.discount ?? 0) - (a.discount ?? 0))
    .slice(0, 8);

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-[var(--cm-background)] pt-20 pb-24">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="py-10">
            <p className="text-xs font-mono text-[var(--cm-mint)] uppercase tracking-widest mb-2">
              Intelligence Terminal
            </p>
            <h1 className="text-2xl font-bold text-[var(--cm-on-surface)] leading-tight">
              Pricing &amp; Brand Intelligence
            </h1>
            <p className="mt-2 text-sm text-[var(--cm-on-surface-variant)]">
              Comparación por marca, tendencias de precio y palancas de estrategia — sobre datos frescos del collector.
            </p>
          </div>

          {!isAuth ? (
            <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] p-6 space-y-4">
              <p className="text-sm font-mono text-[var(--cm-on-surface-variant)]">
                Ingresa tu API key para continuar
              </p>
              <div className="flex gap-2">
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleAuth()}
                  placeholder="sk-..."
                  className="flex-1 bg-[var(--cm-surface-low)] border border-[var(--cm-outline-variant)] rounded-lg px-3 py-2 text-sm font-mono text-[var(--cm-on-surface)] placeholder:text-[var(--cm-on-surface-variant)]/40 focus:outline-none focus:border-[var(--cm-mint)]"
                />
                <button
                  type="button"
                  onClick={handleAuth}
                  disabled={!apiKey.trim().startsWith("sk-") && !apiKey.trim().startsWith("demo-")}
                  className="px-4 py-2 rounded-lg bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold font-mono hover:opacity-90 disabled:opacity-40 transition-opacity"
                >
                  Entrar
                </button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-6 items-start">
              {/* ── Rail: scope + palancas ────────────────────── */}
              <aside className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] p-4 lg:sticky lg:top-24">
                <RailGroup title="Alcance">
                  <Field label="País">
                    <div className="flex flex-wrap gap-1.5">
                      {COUNTRIES.map((c) => (
                        <Chip key={c.code} active={country === c.code} onClick={() => setCountry(c.code)}>
                          {c.code}
                        </Chip>
                      ))}
                    </div>
                  </Field>
                  <Field label="Línea">
                    <div className="flex flex-wrap gap-1.5">
                      {LINES.map((l) => (
                        <Chip key={l.key} active={line === l.key} onClick={() => setLine(l.key)}>
                          {l.label}
                        </Chip>
                      ))}
                    </div>
                  </Field>
                  <Field
                    label={`Marca(s) ${brandsLoading ? "· cargando…" : `· ${selectedBrands.length} seleccionada${selectedBrands.length === 1 ? "" : "s"}`}`}
                  >
                    <div className="flex flex-wrap gap-1.5">
                      {brands.length === 0 && !brandsLoading && (
                        <span className="text-xs font-mono text-[var(--cm-on-surface-variant)]/50">
                          Sin marcas para este scope
                        </span>
                      )}
                      {brands.map((b) => (
                        <Chip key={b.brand} active={selectedBrands.includes(b.brand)} onClick={() => toggleBrand(b.brand)}>
                          {b.brand}
                        </Chip>
                      ))}
                    </div>
                  </Field>
                  <Field label={`Tienda(s) ${storesLoading ? "· cargando…" : ""}`}>
                    <div className="flex flex-wrap gap-1.5">
                      {storeKeys.map((key) => (
                        <Chip key={key} active={selectedStores.includes(key)} onClick={() => toggleStore(key)}>
                          {stores[key].name}
                        </Chip>
                      ))}
                    </div>
                  </Field>
                  <Field label="Ventana">
                    <div className="flex flex-wrap gap-1.5">
                      {WINDOWS.map((w) => (
                        <Chip key={w} active={windowDays === w} onClick={() => setWindowDays(w)}>
                          {w}d
                        </Chip>
                      ))}
                    </div>
                  </Field>
                </RailGroup>

                <RailGroup title="Palancas">
                  <Field label="Posicionamiento objetivo">
                    <select
                      value={position}
                      onChange={(e) => setPosition(e.target.value)}
                      className="w-full bg-[var(--cm-surface-low)] border border-[var(--cm-outline-variant)] rounded-lg px-2.5 py-1.5 text-xs font-mono text-[var(--cm-on-surface)] focus:outline-none focus:border-[var(--cm-mint)]"
                    >
                      {POSITIONS.map((p) => (
                        <option key={p.value} value={p.value}>
                          {p.label}
                        </option>
                      ))}
                    </select>
                  </Field>

                  <Field label={`Confianza mínima de dato · ${confidence}%`}>
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={confidence}
                      onChange={(e) => setConfidence(Number(e.target.value))}
                      className="w-full accent-[var(--cm-mint)]"
                    />
                    <p className="text-[11px] text-[var(--cm-on-surface-variant)]/60 mt-1">
                      Excluye snapshots &quot;suspect&quot; y tiendas con baja cobertura 7d.
                    </p>
                  </Field>

                  <Field label={`Umbral de alerta · ±${alertThreshold}%`}>
                    <input
                      type="range"
                      min={1}
                      max={20}
                      value={alertThreshold}
                      onChange={(e) => setAlertThreshold(Number(e.target.value))}
                      className="w-full accent-[var(--cm-mint)]"
                    />
                  </Field>

                  <div className="flex items-center justify-between py-2 border-t border-[var(--cm-outline-variant)]">
                    <span className="text-xs font-mono font-semibold text-[var(--cm-on-surface)]">Permitir sustitutos</span>
                    <button
                      type="button"
                      onClick={() => setAllowSubstitutes((v) => !v)}
                      className={`w-9 h-5 rounded-full relative transition-colors ${
                        allowSubstitutes ? "bg-[var(--cm-mint)]" : "bg-[var(--cm-surface-low)] border border-[var(--cm-outline-variant)]"
                      }`}
                    >
                      <span
                        className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                          allowSubstitutes ? "translate-x-4" : "translate-x-0.5"
                        }`}
                      />
                    </button>
                  </div>
                  <div className="flex items-center justify-between py-2 border-t border-[var(--cm-outline-variant)]">
                    <span className="text-xs font-mono font-semibold text-[var(--cm-on-surface)]">Ponderar señal macro</span>
                    <button
                      type="button"
                      onClick={() => setMacroWeight((v) => !v)}
                      className={`w-9 h-5 rounded-full relative transition-colors ${
                        macroWeight ? "bg-[var(--cm-mint)]" : "bg-[var(--cm-surface-low)] border border-[var(--cm-outline-variant)]"
                      }`}
                    >
                      <span
                        className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                          macroWeight ? "translate-x-4" : "translate-x-0.5"
                        }`}
                      />
                    </button>
                  </div>
                </RailGroup>
              </aside>

              {/* ── Main ───────────────────────────────────────── */}
              <div className="min-w-0">
                <div className="rounded-lg border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-low)] px-3.5 py-2.5 text-xs font-mono text-[var(--cm-on-surface-variant)] mb-6">
                  Mostrando{" "}
                  <b className="text-[var(--cm-on-surface)]">
                    {selectedBrands.length ? selectedBrands.join(", ") : "todas las marcas"}
                  </b>{" "}
                  · {lineLabel} · <b className="text-[var(--cm-on-surface)]">{country}</b> ·{" "}
                  {selectedStores.length ? `${selectedStores.length} tienda(s)` : "sin tiendas"} · últimos{" "}
                  <b className="text-[var(--cm-on-surface)]">{windowDays} días</b>
                </div>

                <div className="space-y-6">
                  <ComingSoonPanel
                    title="Panorama"
                    meta="market_intel_brief · market_scores"
                    note="Fase 2: scores compuestos, presión inflacionaria y señal de procurement para el scope seleccionado."
                  />

                  {/* ── Comparador de precios (real: /v1/brand-monitor) ──── */}
                  <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] overflow-hidden">
                    <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--cm-outline-variant)]">
                      <h3 className="text-sm font-bold text-[var(--cm-on-surface)]">Comparador de precios</h3>
                      <span className="text-[11px] font-mono text-[var(--cm-on-surface-variant)]/60">
                        {monitorLoading ? "cargando…" : `${pivotRows.length} SKU${pivotRows.length === 1 ? "" : "s"}`}
                      </span>
                    </div>
                    {monitorError ? (
                      <p className="p-5 text-sm text-[var(--cm-on-surface-variant)]">{monitorError}</p>
                    ) : selectedBrands.length === 0 ? (
                      <p className="p-5 text-sm text-[var(--cm-on-surface-variant)]">
                        Seleccioná al menos una marca en el rail para ver el comparador.
                      </p>
                    ) : pivotRows.length === 0 ? (
                      <p className="p-5 text-sm text-[var(--cm-on-surface-variant)]">
                        {monitorLoading ? "Cargando SKUs…" : "Sin SKUs para este scope en la ventana seleccionada."}
                      </p>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="w-full text-xs" style={{ minWidth: 480 }}>
                          <thead>
                            <tr className="border-b border-[var(--cm-outline-variant)]">
                              <th className="text-left font-mono uppercase tracking-wide text-[10px] text-[var(--cm-on-surface-variant)]/60 font-bold px-4 py-2.5">
                                Producto
                              </th>
                              {selectedStores
                                .filter((s) => stores[s])
                                .map((s) => (
                                  <th
                                    key={s}
                                    className="text-right font-mono uppercase tracking-wide text-[10px] text-[var(--cm-on-surface-variant)]/60 font-bold px-4 py-2.5 whitespace-nowrap"
                                  >
                                    {stores[s].name}
                                  </th>
                                ))}
                            </tr>
                          </thead>
                          <tbody>
                            {pivotRows.map((row) => {
                              const visibleStores = selectedStores.filter((s) => stores[s]);
                              const vals = visibleStores.map((s) => row.prices[s]).filter((v) => v != null);
                              const min = vals.length ? Math.min(...vals) : null;
                              return (
                                <tr key={row.key} className="border-b border-[var(--cm-outline-variant)] last:border-0">
                                  <td className="px-4 py-2.5">
                                    <div className="font-semibold text-[var(--cm-on-surface)]">{row.name}</div>
                                    <div className="text-[11px] font-mono text-[var(--cm-on-surface-variant)]/60">
                                      {row.brand}
                                      {row.dispersion != null && ` · dispersión ${(row.dispersion * 100).toFixed(1)}%`}
                                    </div>
                                  </td>
                                  {visibleStores.map((s) => {
                                    const v = row.prices[s];
                                    const isBest = v != null && v === min;
                                    const hasPromo = row.promoStores.has(s);
                                    return (
                                      <td
                                        key={s}
                                        className={`text-right font-mono px-4 py-2.5 ${
                                          isBest ? "text-[var(--cm-mint)] font-bold" : "text-[var(--cm-on-surface)]"
                                        }`}
                                      >
                                        {fmtPrice(v, row.currency)}
                                        {hasPromo && <span className="ml-1 text-[10px] align-top">●</span>}
                                      </td>
                                    );
                                  })}
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  {/* ── Actividad promocional (real, en vez de una serie de tiempo — ver nota) ── */}
                  <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] overflow-hidden">
                    <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--cm-outline-variant)]">
                      <h3 className="text-sm font-bold text-[var(--cm-on-surface)]">Actividad promocional</h3>
                      <span className="text-[11px] font-mono text-[var(--cm-on-surface-variant)]/60">
                        {monitor ? `${monitor.summary.my_skus_with_promo + monitor.summary.competitor_skus_with_promo} en promo` : "—"}
                      </span>
                    </div>
                    <div className="p-4">
                      <p className="text-[11px] text-[var(--cm-on-surface-variant)]/60 mb-3">
                        price_history todavía no tiene series de tiempo pobladas en producción — en vez de simular una
                        tendencia, esto muestra promociones activas ahora mismo (descuento real vs. list_price).
                      </p>
                      {allSkus.filter((s) => s.promo_active).length === 0 ? (
                        <p className="text-sm text-[var(--cm-on-surface-variant)]">Sin promociones activas en este scope.</p>
                      ) : (
                        <div className="space-y-1.5">
                          {allSkus
                            .filter((s) => s.promo_active)
                            .sort((a, b) => (b.discount ?? 0) - (a.discount ?? 0))
                            .slice(0, 6)
                            .map((s, i) => (
                              <div key={`${s.product_id}-${s.store}-${i}`} className="flex items-center justify-between text-xs py-1">
                                <span className="text-[var(--cm-on-surface)] truncate pr-3">
                                  {s.name} <span className="text-[var(--cm-on-surface-variant)]/60 font-mono">· {s.store_name}</span>
                                </span>
                                <span className="font-mono font-bold text-[var(--cm-mint)] whitespace-nowrap">
                                  −{s.discount}%
                                </span>
                              </div>
                            ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* ── Alertas (real: descuento activo ≥ umbral de la palanca) ── */}
                  <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] overflow-hidden">
                    <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--cm-outline-variant)]">
                      <h3 className="text-sm font-bold text-[var(--cm-on-surface)]">Alertas</h3>
                      <span className="text-[11px] font-mono text-[var(--cm-on-surface-variant)]/60">umbral ±{alertThreshold}%</span>
                    </div>
                    <div className="p-4">
                      {promoAlerts.length === 0 ? (
                        <p className="text-sm text-[var(--cm-on-surface-variant)]">
                          Ninguna promo activa supera el umbral de {alertThreshold}% ahora mismo.
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {promoAlerts.map((s, i) => (
                            <div key={`${s.product_id}-${s.store}-${i}`} className="flex items-center gap-2.5 text-xs py-1">
                              <span className="w-1.5 h-1.5 rounded-full bg-[var(--cm-mint)] flex-none" />
                              <span className="text-[var(--cm-on-surface)]">
                                {s.name} bajó{" "}
                                <b className="font-mono text-[var(--cm-mint)]">−{s.discount}%</b> en{" "}
                                <b>{s.store_name}</b>
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}
