"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import { API_URL } from "@/lib/api";
import BrandSkuTable, { type SkuRow } from "./BrandSkuTable";
import BrandCompetitorTable from "./BrandCompetitorTable";
import BrandPromoTimeline, { type PromoEvent } from "./BrandPromoTimeline";

// ── types ────────────────────────────────────────────────────────────────────

interface MonitorSummary {
  brand: string;
  country: string;
  days_window: number;
  my_skus_count: number;
  my_skus_with_promo: number;
  competitor_skus_count: number;
  competitor_skus_with_promo: number;
  pvp_alerts_count: number;
  stores_covered: number;
  competitors_found: string[];
}

interface MonitorData {
  summary: MonitorSummary;
  my_skus: SkuRow[];
  competitor_skus: SkuRow[];
}

type Tab = "my-skus" | "competitors" | "promos";

// ── helpers ───────────────────────────────────────────────────────────────────

function MetricCard({
  label,
  value,
  accent,
  alert,
}: {
  label: string;
  value: string | number;
  accent?: boolean;
  alert?: boolean;
}) {
  return (
    <div
      className={`rounded border px-4 py-3 bg-[var(--cm-surface-card)] ${
        alert
          ? "border-[var(--cm-signal)]/30"
          : accent
          ? "border-[var(--cm-data)]/30"
          : "border-white/10"
      }`}
    >
      <p className="text-[var(--cm-text-secondary)] text-xs uppercase tracking-wider mb-1">
        {label}
      </p>
      <p
        className={`font-mono text-xl font-semibold ${
          alert
            ? "text-[var(--cm-signal)]"
            : accent
            ? "text-[var(--cm-data)]"
            : "text-[var(--cm-ink)]"
        }`}
      >
        {value}
      </p>
    </div>
  );
}

// ── main component ────────────────────────────────────────────────────────────

export default function BrandMonitorDashboard() {
  const params = useParams();
  const slug = typeof params?.slug === "string" ? params.slug : "demo";

  // Config from URL params or defaults
  const [apiKey, setApiKey] = useState("");
  const [brand, setBrand] = useState("");
  const [competitors, setCompetitors] = useState("");
  const [country] = useState("PE");
  const [days] = useState(30);

  const [tab, setTab] = useState<Tab>("my-skus");
  const [data, setData] = useState<MonitorData | null>(null);
  const [promos, setPromos] = useState<PromoEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [promoLoading, setPromoLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [configMode, setConfigMode] = useState(false);
  const [search, setSearch] = useState("");

  // On mount: read API key + brand from localStorage / URL hash
  useEffect(() => {
    const stored = localStorage.getItem("brand_monitor_api_key") || "";
    const storedBrand = localStorage.getItem(`brand_monitor_brand_${slug}`) || slug;
    const storedComp = localStorage.getItem(`brand_monitor_competitors_${slug}`) || "";
    setApiKey(stored);
    setBrand(storedBrand);
    setCompetitors(storedComp);
  }, [slug]);

  const fetchData = useCallback(async () => {
    if (!apiKey || !brand) return;
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        brand,
        country,
        days: String(days),
      });
      if (competitors) params.set("competitors", competitors);

      const r = await fetch(`${API_URL}/v1/brand-monitor?${params}`, {
        headers: { Authorization: `Bearer ${apiKey}` },
      });
      if (!r.ok) {
        const err = await r.json().catch(() => ({}));
        throw new Error(err.detail ?? `HTTP ${r.status}`);
      }
      setData(await r.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Error desconocido");
    } finally {
      setLoading(false);
    }
  }, [apiKey, brand, competitors, country, days]);

  const fetchPromos = useCallback(async () => {
    if (!apiKey || !brand) return;
    setPromoLoading(true);
    try {
      const params = new URLSearchParams({ brand, country, days: String(days) });
      if (competitors) params.set("competitors", competitors);
      const r = await fetch(`${API_URL}/v1/brand-monitor/promos?${params}`, {
        headers: { Authorization: `Bearer ${apiKey}` },
      });
      if (r.ok) {
        const d = await r.json();
        setPromos(d.promo_events ?? []);
      }
    } catch {
      /* non-fatal */
    } finally {
      setPromoLoading(false);
    }
  }, [apiKey, brand, competitors, country, days]);

  useEffect(() => {
    if (apiKey && brand) {
      fetchData();
      fetchPromos();
    }
  }, [fetchData, fetchPromos, apiKey, brand]);

  const saveConfig = () => {
    localStorage.setItem("brand_monitor_api_key", apiKey);
    localStorage.setItem(`brand_monitor_brand_${slug}`, brand);
    localStorage.setItem(`brand_monitor_competitors_${slug}`, competitors);
    setConfigMode(false);
    fetchData();
    fetchPromos();
  };

  const hasPvp = Boolean(data?.my_skus.some((s) => s.pvp_suggested !== null));

  const searchNorm = search.trim().toLowerCase();
  const matchesSearch = (s: SkuRow) => s.name.toLowerCase().includes(searchNorm);
  const filteredMySkus = data && searchNorm ? data.my_skus.filter(matchesSearch) : data?.my_skus ?? [];
  const filteredCompetitorSkus =
    data && searchNorm ? data.competitor_skus.filter(matchesSearch) : data?.competitor_skus ?? [];

  // Competidores tab keeps the "TÚ" benchmark row unfiltered even when the
  // search only matches a competitor product — otherwise a search for e.g.
  // "Laive" would drop the user's own brand row with no explanation.
  const noMySkuMatch = tab === "my-skus" && Boolean(searchNorm) && filteredMySkus.length === 0 && data && data.my_skus.length > 0;
  const noCompetitorMatch =
    tab === "competitors" && Boolean(searchNorm) && filteredCompetitorSkus.length === 0 && data && data.competitor_skus.length > 0;
  const showNoMatchState = Boolean(noMySkuMatch || noCompetitorMatch);

  // ── CONFIG SCREEN ────────────────────────────────────────────────────────

  if (!apiKey || configMode) {
    return (
      <div className="min-h-screen bg-[var(--cm-canvas)] flex items-center justify-center px-4">
        <div className="w-full max-w-md border border-white/10 rounded-xl p-6 bg-[var(--cm-surface-card)] space-y-4">
          <div>
            <p className="text-xs text-[var(--cm-data)] uppercase tracking-widest font-mono mb-1">
              CLI MARKET
            </p>
            <h1 className="text-[var(--cm-ink)] text-xl font-semibold">Brand Monitor</h1>
            <p className="text-[var(--cm-text-secondary)] text-sm mt-1">
              Ingresa tu API key y la marca a monitorear.
            </p>
          </div>

          <div className="space-y-3">
            <div>
              <label className="text-xs text-[var(--cm-text-secondary)] mb-1 block">
                API Key
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full bg-[var(--cm-surface-container)] border border-white/10 rounded px-3 py-2 text-sm font-mono text-[var(--cm-ink)] focus:outline-none focus:border-[var(--cm-data)]/50 transition-colors"
              />
            </div>
            <div>
              <label className="text-xs text-[var(--cm-text-secondary)] mb-1 block">
                Marca principal
              </label>
              <input
                type="text"
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
                placeholder="ej. Gloria, Laive, Don Vittorio"
                className="w-full bg-[var(--cm-surface-container)] border border-white/10 rounded px-3 py-2 text-sm text-[var(--cm-ink)] focus:outline-none focus:border-[var(--cm-data)]/50 transition-colors"
              />
            </div>
            <div>
              <label className="text-xs text-[var(--cm-text-secondary)] mb-1 block">
                Competidores{" "}
                <span className="text-[var(--cm-text-secondary)]/60">(separados por coma, opcional)</span>
              </label>
              <input
                type="text"
                value={competitors}
                onChange={(e) => setCompetitors(e.target.value)}
                placeholder="ej. Laive,Nestlé"
                className="w-full bg-[var(--cm-surface-container)] border border-white/10 rounded px-3 py-2 text-sm text-[var(--cm-ink)] focus:outline-none focus:border-[var(--cm-data)]/50 transition-colors"
              />
            </div>
          </div>

          <button
            onClick={saveConfig}
            disabled={!apiKey || !brand}
            className="w-full bg-[var(--cm-data)] text-black font-semibold rounded px-4 py-2 text-sm hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Acceder al dashboard
          </button>

          <p className="text-xs text-[var(--cm-text-secondary)] text-center">
            Sin cuenta?{" "}
            <a
              href="https://cli-market.dev"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--cm-data)] hover:underline"
            >
              cli-market.dev
            </a>
          </p>
        </div>
      </div>
    );
  }

  // ── MAIN DASHBOARD ────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-[var(--cm-canvas)] text-[var(--cm-ink)]">
      {/* Header */}
      <header className="border-b border-white/10 bg-[var(--cm-surface-card)] sticky top-0 z-20">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xs text-[var(--cm-data)] font-mono uppercase tracking-widest">
              CLI MARKET
            </span>
            <span className="text-white/20">|</span>
            <span className="text-sm font-semibold">
              Brand Monitor{brand ? ` · ${brand}` : ""}
            </span>
            {data && (
              <span className="text-xs text-[var(--cm-text-secondary)] font-mono">
                {country} · {days}d
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchData}
              disabled={loading}
              className="text-xs text-[var(--cm-text-secondary)] hover:text-[var(--cm-data)] transition-colors font-mono disabled:opacity-40"
            >
              {loading ? "↻ cargando…" : "↻ actualizar"}
            </button>
            <button
              onClick={() => setConfigMode(true)}
              className="text-xs text-[var(--cm-text-secondary)] hover:text-[var(--cm-ink)] transition-colors"
            >
              ⚙
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        {/* Error */}
        {error && (
          <div className="border border-red-500/30 bg-red-500/10 rounded p-3 text-sm text-red-400 font-mono">
            Error: {error}
          </div>
        )}

        {/* Loading skeleton */}
        {loading && !data && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-16 rounded border border-white/10 bg-white/[0.02] animate-pulse" />
            ))}
          </div>
        )}

        {/* Summary cards */}
        {data && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <MetricCard
              label="Mis SKUs"
              value={data.summary.my_skus_count}
              accent
            />
            <MetricCard
              label="Con promo activa"
              value={data.summary.my_skus_with_promo}
              alert={data.summary.my_skus_with_promo > 0}
            />
            <MetricCard
              label="Alertas PVP"
              value={data.summary.pvp_alerts_count}
              alert={data.summary.pvp_alerts_count > 0}
            />
            <MetricCard
              label="Tiendas cubiertas"
              value={data.summary.stores_covered}
            />
          </div>
        )}

        {/* Tabs */}
        {data && (
          <div>
            <div className="flex gap-1 border-b border-white/10 mb-4">
              {(
                [
                  { id: "my-skus", label: `Mis SKUs (${data.summary.my_skus_count})` },
                  {
                    id: "competitors",
                    label: `Competidores (${data.summary.competitor_skus_count})`,
                  },
                  {
                    id: "promos",
                    label: `Promo tracker (${promos.length ?? 0})`,
                  },
                ] as { id: Tab; label: string }[]
              ).map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTab(t.id)}
                  className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors -mb-px ${
                    tab === t.id
                      ? "border-[var(--cm-data)] text-[var(--cm-data)]"
                      : "border-transparent text-[var(--cm-text-secondary)] hover:text-[var(--cm-ink)]"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {(tab === "my-skus" || tab === "competitors") && (
              <div className="mb-3 relative w-full sm:w-72">
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Buscar producto por nombre…"
                  aria-label="Buscar producto por nombre"
                  className="w-full bg-[var(--cm-surface-container)] border border-white/10 rounded px-3 py-2 text-sm text-[var(--cm-ink)] focus:outline-none focus:border-[var(--cm-data)]/50 transition-colors"
                />
                {search && (
                  <button
                    onClick={() => setSearch("")}
                    aria-label="Limpiar búsqueda"
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--cm-text-secondary)] hover:text-[var(--cm-ink)] text-xs"
                  >
                    ✕
                  </button>
                )}
              </div>
            )}

            <div className="border border-white/10 rounded-xl p-4 bg-[var(--cm-surface-card)]">
              {showNoMatchState ? (
                <p className="text-[var(--cm-text-secondary)] text-sm py-8 text-center">
                  Ningún producto coincide con &ldquo;{search}&rdquo;.
                </p>
              ) : (
                <>
                  {tab === "my-skus" && (
                    <BrandSkuTable skus={filteredMySkus} hasPvp={hasPvp} />
                  )}
                  {tab === "competitors" && (
                    <BrandCompetitorTable
                      myBrand={brand}
                      mySkus={data.my_skus}
                      competitorSkus={filteredCompetitorSkus}
                    />
                  )}
                </>
              )}
              {tab === "promos" && (
                promoLoading ? (
                  <p className="text-[var(--cm-text-secondary)] text-sm py-8 text-center animate-pulse">
                    Cargando eventos de promo…
                  </p>
                ) : (
                  <BrandPromoTimeline events={promos} myBrand={brand} />
                )
              )}
            </div>
          </div>
        )}

        {/* Footer note */}
        <p className="text-xs text-[var(--cm-text-secondary)] text-center font-mono">
          Datos de góndola digital · refresh cada 8h · solo retail online indexado · no reemplaza
          IPC oficial{" "}
          <a
            href="https://cli-market.dev"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[var(--cm-data)] hover:underline"
          >
            cli-market.dev
          </a>
        </p>
      </main>
    </div>
  );
}
