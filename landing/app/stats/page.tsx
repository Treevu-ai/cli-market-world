"use client";

import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLang } from "@/lib/LanguageContext";
import { useObservatoryStats, type ObservatoryRank } from "@/hooks/useObservatoryStats";
import FunnelMetrics from "@/components/FunnelMetrics";
import DataMoatHealth from "@/components/DataMoatHealth";

function RankList({
  title,
  items,
  empty,
}: {
  title: string;
  items: ObservatoryRank[];
  empty: string;
}) {
  if (!items?.length) return null;
  return (
    <div className="card-cyber p-5">
      <h3 className="text-sm font-semibold text-[var(--cm-on-surface)] mb-3">{title}</h3>
      <ul className="space-y-2">
        {items.slice(0, 5).map((row) => (
          <li
            key={row.name}
            className="flex justify-between gap-4 text-sm border-b border-[var(--cm-hairline)] pb-2 last:border-0"
          >
            <span className="text-[var(--cm-on-surface-variant)] truncate">{row.name}</span>
            <span className="font-mono text-[var(--cm-on-surface)] tabular-nums shrink-0">
              {row.count.toLocaleString()}
            </span>
          </li>
        ))}
      </ul>
      {!items.length && (
        <p className="text-xs text-[var(--cm-on-surface-variant)]/70">{empty}</p>
      )}
    </div>
  );
}

export default function StatsPage() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { data, loading, showMaa, showQueries, maaValue, maaIsProxy } = useObservatoryStats(30);

  const catalogStats = [
    {
      n: MARKET_STATS.pricesVerifiedLabel,
      l: isES ? "Precios verificados" : "Verified prices",
    },
    {
      n: String(MARKET_STATS.retailersVerified),
      l: isES ? "Retailers activos" : "Active retailers",
    },
    {
      n: String(MARKET_STATS.countries),
      l: isES ? "Países" : "Countries",
    },
    {
      n: String(MARKET_STATS.mcpTools),
      l: isES ? "API tools" : "API tools",
    },
  ];

  const agentStats = [
    showMaa && maaValue > 0
      ? {
          n: maaValue.toLocaleString(),
          l: maaIsProxy
            ? isES
              ? "Agentes activos (proxy, 30 d)"
              : "Active agents (proxy, 30d)"
            : isES
              ? "Agentes activos (MAA, 30 d)"
              : "Active agents (MAA, 30d)",
        }
      : null,
    showQueries
      ? {
          n: data!.calls_success.toLocaleString(),
          l: isES ? "Consultas exitosas (30 d)" : "Successful queries (30d)",
        }
      : null,
  ].filter(Boolean) as { n: string; l: string }[];

  return (
    <main className="bg-[var(--cm-canvas)] min-h-screen">
      <Navbar />

      <div className="landing-container-wide pt-24 pb-16 max-w-4xl mx-auto">
        <span className="stripe-tag-soft inline-flex mb-3">
          {isES ? "Métricas públicas · data-gate" : "Public metrics · data-gate"}
        </span>
        <h1 className="hero-garamond-headline text-balance mb-4" style={{ fontSize: "clamp(1.875rem, 4.5vw, 2.75rem)" }}>
          {isES ? "Adopción y cobertura" : "Adoption & coverage"}
        </h1>
        <p className="text-[var(--cm-on-surface-variant)] text-sm md:text-base mb-10 max-w-2xl">
          {isES
            ? "Cifras del catálogo verificadas por el collector. MAA es la north star; antes del umbral 10 mostramos un proxy (API keys activas 30d)."
            : "Catalog figures verified by the collector. MAA is our north star; below the threshold of 10 we show a proxy (active API keys, 30d)."}
        </p>

        <section className="mb-12" aria-labelledby="catalog-heading">
          <h2 id="catalog-heading" className="text-lg font-semibold text-[var(--cm-on-surface)] mb-4">
            {isES ? "Catálogo" : "Catalog"}
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {catalogStats.map((s) => (
              <div key={s.l} className="card-cyber p-4 text-center">
                <div className="text-2xl font-mono text-[var(--cm-mint)] tabular-nums">{s.n}</div>
                <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">{s.l}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-12" aria-labelledby="moat-heading">
          <h2 id="moat-heading" className="text-lg font-semibold text-[var(--cm-on-surface)] mb-4">
            {isES ? "Salud del data moat" : "Data moat health"}
          </h2>
          <DataMoatHealth />
        </section>

        {loading ? (
          <p className="text-sm text-[var(--cm-on-surface-variant)]/70">
            {isES ? "Cargando telemetría agregada…" : "Loading aggregate telemetry…"}
          </p>
        ) : agentStats.length > 0 ? (
          <section className="mb-12" aria-labelledby="agents-heading">
            <h2 id="agents-heading" className="text-lg font-semibold text-[var(--cm-on-surface)] mb-4">
              {isES ? "Uso por agentes" : "Agent usage"}
            </h2>
            <div className="grid grid-cols-2 gap-4 mb-8 max-w-md">
              {agentStats.map((s) => (
                <div key={s.l} className="card-cyber p-4 text-center">
                  <div className="text-2xl font-mono text-[var(--cm-on-surface)] tabular-nums">{s.n}</div>
                  <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">{s.l}</div>
                </div>
              ))}
            </div>

            <div className="grid md:grid-cols-3 gap-4">
              <RankList
                title={isES ? "Top herramientas" : "Top tools"}
                items={data?.top_tools ?? []}
                empty={isES ? "Sin datos aún" : "No data yet"}
              />
              <RankList
                title={isES ? "Top retailers" : "Top retailers"}
                items={data?.top_retailers ?? []}
                empty={isES ? "Sin datos aún" : "No data yet"}
              />
              <RankList
                title={isES ? "Top países" : "Top countries"}
                items={data?.top_countries ?? []}
                empty={isES ? "Sin datos aún" : "No data yet"}
              />
            </div>
          </section>
        ) : (
          <p className="text-sm text-[var(--cm-on-surface-variant)]/80 border border-[var(--cm-outline-variant)]/25 rounded-lg p-4">
            {isES
              ? "Telemetría activa pero sin volumen aún — vuelve cuando haya consultas o agentes activos."
              : "Telemetry is on but volume is still building — check back as queries and agents accumulate."}
          </p>
        )}

        <section className="mb-10" aria-labelledby="funnel-heading">
          <h2 id="funnel-heading" className="text-lg font-semibold text-[var(--cm-on-surface)] mb-2">
            {isES ? "Embudo de onboarding" : "Onboarding funnel"}
          </h2>
          <FunnelMetrics />
        </section>

        <p className="text-sm text-[var(--cm-on-surface-variant)] mt-8">
          <a
            href="/indice-canasta-pe.md"
            className="text-[var(--cm-mint)] hover:underline font-mono text-xs"
          >
            {isES ? "Índice Canasta Perú (markdown público) →" : "Peru basket index (public markdown) →"}
          </a>
        </p>

        <p className="text-xs text-[var(--cm-on-surface-variant)]/60 mt-4">
          {isES
            ? `Ventana: 30 días · refresh catálogo cada ${MARKET_STATS.pricesRefreshHours}h · sin PII`
            : `Window: 30 days · catalog refresh every ${MARKET_STATS.pricesRefreshHours}h · no PII`}
        </p>
      </div>

      <Footer />
    </main>
  );
}
