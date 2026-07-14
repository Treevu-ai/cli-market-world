"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { useLang } from "@/lib/LanguageContext";

type CanastaRow = { store_name: string; items: number; total: number; currency: string };

type DashboardData = {
  generated_at: string;
  kpis: { coverage_7d_pct: number };
  canasta_basica: CanastaRow[];
};

const CANASTA_ITEMS = ["leche", "arroz", "aceite", "azúcar", "huevos", "pan", "café", "pollo", "queso", "jabón"];

export default function IndiceCanastaPePage() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch("https://cli-market-api.fly.dev/dashboard/data")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setData)
      .catch(() => setError(true));
  }, []);

  const peRows = (data?.canasta_basica ?? [])
    .filter((r) => r.currency === "PEN")
    .sort((a, b) => a.total - b.total);
  const cheapest = peRows[0];
  const priciest = peRows[peRows.length - 1];
  const ratio = cheapest && priciest && cheapest.total ? priciest.total / cheapest.total : null;

  return (
    <main className="bg-[var(--cm-canvas)] min-h-screen">
      <Navbar />

      <div className="landing-container-wide pt-24 pb-16 max-w-3xl mx-auto">
        <span className="stripe-tag-soft inline-flex mb-3">
          {isES ? "Señal pública del data moat" : "Public data moat signal"}
        </span>
        <h1 className="hero-garamond-headline text-balance mb-2" style={{ fontSize: "clamp(1.875rem, 4.5vw, 2.75rem)" }}>
          {isES ? "Índice Canasta Perú" : "Peru Basket Index"}
        </h1>
        <p className="text-sm text-[var(--cm-on-surface-variant)] mb-8">
          {data ? (
            isES ? (
              <>Actualizado: {new Date(data.generated_at).toLocaleString("es-PE")} (UTC)</>
            ) : (
              <>Updated: {new Date(data.generated_at).toLocaleString("en-US")} (UTC)</>
            )
          ) : isES ? (
            "Cargando…"
          ) : (
            "Loading…"
          )}
          {" · "}
          <a href="/indice-canasta-pe.md" className="text-[var(--cm-mint)] hover:underline">
            {isES ? "Versión markdown" : "Markdown version"}
          </a>
        </p>

        <p className="text-[var(--cm-on-surface-variant)] leading-relaxed mb-10">
          {isES
            ? "Canasta básica comparable (10 ítems) en cadenas peruanas con cobertura activa."
            : "Comparable basic basket (10 items) across Peruvian chains with active coverage."}
        </p>

        {error ? (
          <p className="text-sm text-[var(--cm-on-surface-variant)]/70">
            {isES ? "No se pudo cargar el índice." : "Could not load the index."}
          </p>
        ) : !data ? (
          <p className="text-sm text-[var(--cm-on-surface-variant)]/70">{isES ? "Cargando…" : "Loading…"}</p>
        ) : (
          <>
            <section className="mb-10">
              <h2 className="section-title !mb-4" style={{ fontSize: "1.25rem" }}>
                {isES ? "Resumen" : "Summary"}
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                <div className="card-cyber p-4 text-center">
                  <div className="text-2xl font-mono text-[var(--cm-mint)] tabular-nums">{peRows.length}</div>
                  <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">
                    {isES ? "Cadenas PE en canasta" : "PE chains in basket"}
                  </div>
                </div>
                <div className="card-cyber p-4 text-center">
                  <div className="text-2xl font-mono text-[var(--cm-mint)] tabular-nums">
                    {data.kpis.coverage_7d_pct}%
                  </div>
                  <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">
                    {isES ? "Cobertura 7d (global)" : "7d coverage (global)"}
                  </div>
                </div>
                {ratio != null && (
                  <div className="card-cyber p-4 text-center">
                    <div className="text-2xl font-mono text-[var(--cm-mint)] tabular-nums">{ratio.toFixed(2)}×</div>
                    <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">
                      {isES ? "Ratio máx/mín" : "Max/min ratio"}
                    </div>
                  </div>
                )}
              </div>
            </section>

            <section className="mb-10">
              <h2 className="section-title !mb-4" style={{ fontSize: "1.25rem" }}>
                {isES ? "Totales por cadena (PEN)" : "Totals by chain (PEN)"}
              </h2>
              <div className="card-cyber overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[var(--cm-hairline)]">
                      <th className="text-left px-4 py-3 font-semibold text-[var(--cm-on-surface)]">
                        {isES ? "Cadena" : "Chain"}
                      </th>
                      <th className="text-right px-4 py-3 font-semibold text-[var(--cm-on-surface)]">
                        {isES ? "Ítems" : "Items"}
                      </th>
                      <th className="text-right px-4 py-3 font-semibold text-[var(--cm-on-surface)]">
                        {isES ? "Total canasta" : "Basket total"}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {peRows.map((row) => (
                      <tr key={row.store_name} className="border-b border-[var(--cm-hairline)] last:border-0">
                        <td className="px-4 py-3 text-[var(--cm-on-surface)]">{row.store_name}</td>
                        <td className="px-4 py-3 text-right font-mono text-[var(--cm-on-surface-variant)]">
                          {row.items}/10
                        </td>
                        <td className="px-4 py-3 text-right font-mono text-[var(--cm-on-surface)]">
                          S/ {row.total.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {cheapest && priciest && (
                <p className="text-xs text-[var(--cm-on-surface-variant)] mt-3">
                  {isES ? "Más barata: " : "Cheapest: "}
                  <strong className="text-[var(--cm-on-surface)]">{cheapest.store_name}</strong> (S/{" "}
                  {cheapest.total.toFixed(2)}) · {isES ? "más cara: " : "priciest: "}
                  <strong className="text-[var(--cm-on-surface)]">{priciest.store_name}</strong> (S/{" "}
                  {priciest.total.toFixed(2)})
                </p>
              )}
            </section>
          </>
        )}

        <section className="mb-10">
          <h2 className="section-title !mb-4" style={{ fontSize: "1.25rem" }}>
            {isES ? "Metodología" : "Methodology"}
          </h2>
          <ul className="text-sm text-[var(--cm-on-surface-variant)] space-y-2 list-disc list-inside">
            <li>
              {isES ? "Ítems: " : "Items: "}
              {CANASTA_ITEMS.join(", ")} ({isES ? "canasta CLI Market" : "CLI Market basket"})
            </li>
            <li>
              {isES
                ? "Precios de góndola online, normalizados cuando aplica; actualización collector cada 4 h"
                : "Online shelf prices, normalized when applicable; collector refresh every 4h"}
            </li>
            <li>
              {isES
                ? "Solo cadenas con ≥60% ítems encontrados en el snapshot"
                : "Only chains with ≥60% items found in the snapshot"}
            </li>
          </ul>
        </section>

        <section>
          <h2 className="section-title !mb-4" style={{ fontSize: "1.25rem" }}>
            API
          </h2>
          <div className="code-block-cyber p-4">
            <pre className="text-sm">{`pip install cli-market-world
market basket "arroz:1 aceite:1 leche:1" --country PE`}</pre>
          </div>
        </section>
      </div>

      <Footer />
    </main>
  );
}
