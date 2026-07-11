"use client";

import { useRef, useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import BasketOptimizer, { type BasketOptimizerHandle } from "@/components/BasketOptimizer";
import { useApiKey } from "@/lib/useApiKey";
import { apiFetch, ApiError } from "@/lib/apiClient";

type SearchResult = {
  product_id: string;
  name: string;
  brand?: string;
  price: number;
  currency: string;
  store: string;
  store_name: string;
};

type SearchResponse = { query: string; results: SearchResult[]; total: number };

const COUNTRIES = ["PE", "MX", "CO", "AR", "CL", "BO", "EC", "UY"];

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
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

export default function ExplorerDashboard() {
  const { apiKey } = useApiKey();
  const [country, setCountry] = useState("PE");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const basketRef = useRef<BasketOptimizerHandle>(null);

  const search = async () => {
    const q = query.trim();
    if (!q) return;
    setError("");
    setLoading(true);
    try {
      const data = await apiFetch<SearchResponse>("/products/search", {
        apiKey,
        method: "POST",
        body: { query: q, limit: 15, country },
      });
      setResults(data.results ?? []);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Error de búsqueda");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-[var(--cm-surface)] pt-20 pb-24">
        <div className="max-w-2xl mx-auto px-4 sm:px-6">
          <div className="py-10">
            <p className="section-eyebrow mb-2 text-[var(--cm-mint)]">Explorer</p>
            <h1 className="section-title mb-2">Buscar, comparar, armar canasta</h1>
            <p className="text-sm text-[var(--cm-on-surface-variant)]">
              Buscá un producto, agregalo a tu canasta, y optimizá dónde comprar.
            </p>
          </div>

          {/* Country */}
          <div className="flex items-center gap-2 mb-4 flex-wrap">
            {COUNTRIES.map((c) => (
              <Chip key={c} active={c === country} onClick={() => setCountry(c)}>
                {c}
              </Chip>
            ))}
          </div>

          {/* Search */}
          <div className="flex gap-2 mb-4">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && search()}
              placeholder="ej. leche, arroz 1kg"
              className="input-cyber font-mono text-sm flex-1"
            />
            <button
              type="button"
              onClick={search}
              disabled={loading || !query.trim()}
              className="btn-mint disabled:opacity-40 shrink-0"
            >
              {loading ? "Buscando..." : "Buscar"}
            </button>
          </div>
          {error && <p className="text-xs font-mono text-red-400 mb-4">{error}</p>}

          {/* Results */}
          {results.length > 0 && (
            <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] divide-y divide-[var(--cm-outline-variant)] mb-8">
              {results.map((r) => (
                <div key={`${r.store}-${r.product_id}`} className="px-4 py-2.5 flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-mono text-[var(--cm-on-surface)] truncate">{r.name}</p>
                    <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/60">
                      {r.store_name} · {r.brand ?? "—"}
                    </p>
                  </div>
                  <p className="text-xs font-mono tabular-nums text-[var(--cm-mint)] shrink-0">
                    {r.currency} {r.price?.toFixed(2)}
                  </p>
                  <button
                    type="button"
                    onClick={() => basketRef.current?.addItem(r.name)}
                    className="shrink-0 px-2.5 py-1 rounded-lg border border-[var(--cm-outline-variant)] text-[10px] font-mono text-[var(--cm-on-surface-variant)] hover:border-[var(--cm-mint)] hover:text-[var(--cm-on-surface)] transition-colors"
                  >
                    + Canasta
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Basket */}
          <div className="pt-4 border-t border-[var(--cm-outline-variant)]/30">
            <h2 className="text-sm font-bold text-[var(--cm-mint)] uppercase tracking-wider mb-4">
              Canasta
            </h2>
            <BasketOptimizer ref={basketRef} apiKey={apiKey ?? ""} country={country} />
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
