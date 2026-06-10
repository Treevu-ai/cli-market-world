"use client";

import { useEffect, useRef } from "react";
import { motion, useInView, useSpring, useTransform } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLiveStats, refreshLabel } from "@/hooks/useLiveStats";
const vtexLines = {
  supermercados: ["Carrefour AR/BR", "Jumbo AR", "Vea AR", "Chedraui MX", "HEB MX", "Exito CO", "Carulla CO", "Olimpica CO", "Sams Club BR", "Mambo BR", "Wong PE", "Metro PE", "Plaza Vea PE"],
  farmacias: ["Drogaria Pacheco BR", "Farmatodo MX", "Cruz Verde CO/CL"],
  electro: ["Motorola AR/BR/MX/CL", "Electrolux AR/CL", "Whirlpool AR/IT/FR", "Samsung"],
  moda: ["C&A Brasil", "Hering Brasil"],
};

const magentoStores = ["Falabella PE/CL/CO", "Paris CL", "Ripley CL", "Liverpool MX", "El Palacio MX"];

function Counter({ end, label, delay }: { end: number; label: string; delay: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "0px 0px -80px 0px" });
  const spring = useSpring(end, { stiffness: 60, damping: 20 });
  const display = useTransform(spring, (v) => Math.round(v).toLocaleString());

  useEffect(() => {
    if (inView) {
      const timer = setTimeout(() => spring.set(end), delay);
      return () => clearTimeout(timer);
    }
  }, [inView, end, delay, spring]);

  return (
    <div className="flex flex-col items-center gap-1">
      <motion.span ref={ref} className="text-2xl font-medium text-white tracking-tight tabular-nums">{display}</motion.span>
      <span className="text-xs text-[var(--cm-on-surface-variant)] font-mono uppercase tracking-widest text-center">{label}</span>
    </div>
  );
}

export default function ScaleCoverageSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { priceLong, priceChip, stats, retailersVerified, retailersDefined } = useLiveStats();

  const scaleStats = [
    { end: retailersDefined, label: isES ? "retailers catálogo" : "retailers in catalog" },
    { end: retailersVerified, label: isES ? "verificados activos" : "verified active" },
    { end: MARKET_STATS.countries, label: isES ? "países" : "countries" },
    { end: MARKET_STATS.platforms, label: isES ? "plataformas" : "platforms" },
  ];

  return (
    <section id="coverage" className="brand-mode-terminal landing-section landing-section-glow animate-fade-in">
      <div className="landing-container text-center">
        <p className="section-eyebrow mb-4">
          {isES ? "Escala y cobertura" : "Scale and coverage"}
        </p>
        <h2 className="section-title">
          {isES ? "Cobertura retail en LatAm" : "Retail coverage across LatAm"}
        </h2>
        <p className="inline-flex items-center gap-2 text-xs font-mono text-[var(--cm-mint)] bg-[var(--cm-mint)]/10 border border-[var(--cm-mint)]/30 rounded-full px-3 py-1 mb-4">
          {priceChip} · {refreshLabel(isES)}
        </p>
        <p className="section-intro">
          {isES
            ? `${MARKET_STATS.platformsPhraseEs}. ${priceLong} precios verificados · ${refreshLabel(isES)}.`
            : `${MARKET_STATS.platformsPhraseEn}. ${priceLong} verified prices · ${refreshLabel(isES)}.`}
        </p>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-10 sm:mb-14">
          {scaleStats.map((s, i) => (
            <Counter key={s.label} end={s.end} label={s.label} delay={i * 100} />
          ))}
        </div>

        <div className="mb-10 sm:mb-12 text-left max-w-3xl mx-auto">
          <p className="font-label-caps text-[var(--cm-on-surface-variant)]/60 mb-3 text-center">
            {isES ? "Retailers verificados (muestra)" : "Verified retailers (sample)"}
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {["Wong PE", "Metro PE", "Plaza Vea PE", "Carrefour AR", "Jumbo AR", "Vea AR", "Chedraui MX", "HEB MX", "Exito CO", "Falabella CL"].map((store) => (
              <span
                key={store}
                className="touch-compact text-xs font-mono text-[var(--cm-on-surface-variant)] bg-white/5 border border-[var(--cm-outline-variant)]/30 rounded-full px-2.5 py-1"
              >
                {store}
              </span>
            ))}
          </div>
          <p className="text-center text-xs text-[var(--cm-on-surface-variant)]/60 mt-3 font-mono">
            {isES
              ? `Golden Record: mismo producto comparable entre cadenas · ${retailersVerified} activos`
              : `Golden Record: same product comparable across chains · ${retailersVerified} active`}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-14 text-left">
          <div className="card-cyber p-6">
            <p className="text-xs uppercase tracking-widest text-[var(--cm-on-surface-variant)]/60 mb-1">
              {isES ? "Inventario" : "Inventory"}
            </p>
            <p className="text-3xl font-black text-white tabular-nums">{priceLong}</p>
            <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1">
              {isES
                ? `precios indexados · normalizados kg/L · ${MARKET_STATS.indicatorsCount} indicadores`
                : `indexed prices · kg/L normalized · ${MARKET_STATS.indicatorsCount} indicators`}
            </p>
          </div>
          <div className="card-cyber p-6">
            <p className="text-xs uppercase tracking-widest text-[var(--cm-on-surface-variant)]/60 mb-2">
              {isES ? "Frescura" : "Freshness"}
            </p>
            <p className="text-3xl font-black text-white tabular-nums">
              {stats.fresh24hPct != null ? `${stats.fresh24hPct.toFixed(0)}%` : "—"}
            </p>
            <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1">
              {stats.snapshots24h != null ? `${stats.snapshots24h.toLocaleString()} snapshots 24h` : "—"}
              {stats.moatAgeHours != null ? ` · ${isES ? "último" : "last"} ${stats.moatAgeHours.toFixed(1)}h` : ""}
            </p>
          </div>
          <div className="card-cyber p-6">
            <p className="text-xs uppercase tracking-widest text-[var(--cm-on-surface-variant)]/60 mb-2">
              {isES ? "Cobertura" : "Coverage"}
            </p>
            <p className="text-3xl font-black text-white tabular-nums">
              {stats.coverage7dPct != null ? `${stats.coverage7dPct.toFixed(0)}%` : "—"}
            </p>
            <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1">
              {retailersVerified} {isES ? "verificados ·" : "verified ·"} collector {stats.collectorStatus ?? "—"}
            </p>
          </div>
        </div>

        <div className="max-w-3xl mx-auto text-left space-y-4">
          <details className="details-disclosure">
            <summary>{isES ? "Métricas técnicas del collector" : "Collector technical metrics"}</summary>
            <div className="details-body">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4">
                {[
                  { label: isES ? "Precios acumulados" : "Total snapshots", value: stats.totalSnapshotsAll != null ? stats.totalSnapshotsAll.toLocaleString() : "—" },
                  { label: isES ? "Promedio diario (7d)" : "Daily avg (7d)", value: stats.avgDaily7d != null ? stats.avgDaily7d.toLocaleString() : "—" },
                  { label: isES ? "Serie histórica desde" : "Historical series since", value: stats.moatStart != null ? stats.moatStart.slice(0, 10) : "—" },
                  { label: isES ? "Intervalo collector" : "Collector interval", value: `cada ${MARKET_STATS.pricesRefreshHours}h` },
                ].map((item) => (
                  <div key={item.label} className="card-cyber p-4 border-l-2 border-[var(--cm-mint)]/40">
                    <p className="text-xs uppercase tracking-widest text-[var(--cm-mint)] mb-2">{item.label}</p>
                    <p className="text-lg font-bold text-white tabular-nums">{item.value}</p>
                  </div>
                ))}
              </div>
            </div>
          </details>

          <details className="details-disclosure">
            <summary>{isES ? "Plataformas y retailers" : "Platforms and retailers"}</summary>
            <div className="details-body space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4">
                {[
                  { name: "VTEX", count: MARKET_STATS.platformVtex, note: isES ? "supermercados, electro, moda LatAm" : "supermarkets, electronics, LatAm fashion" },
                  { name: "Shopify", count: MARKET_STATS.platformShopify, note: isES ? "moda & beauty global" : "global fashion & beauty" },
                  { name: "Magento", count: MARKET_STATS.platformMagento, note: isES ? "departamentales" : "department stores" },
                  { name: "WooCommerce", count: MARKET_STATS.platformWooCommerce, note: isES ? "FMCG organico PE (piloto)" : "organic FMCG PE (pilot)" },
                ].map((p) => (
                  <div key={p.name} className="card-cyber p-5">
                    <p className="text-lg font-bold text-white">{p.name}</p>
                    <p className="text-2xl font-black text-white tabular-nums mt-1">{p.count}</p>
                    <p className="text-sm text-[var(--cm-on-surface-variant)] mt-2 leading-relaxed">{p.note}</p>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <p className="font-label-caps text-[var(--cm-on-surface-variant)]/60 mb-3">VTEX</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {Object.entries(vtexLines).map(([line, stores]) => (
                      <div key={line} className="card-cyber p-4">
                        <h3 className="text-xs font-bold uppercase text-white mb-2">{line}</h3>
                        <ul className="text-sm text-[var(--cm-on-surface-variant)] space-y-1 leading-relaxed list-disc pl-4">
                          {stores.slice(0, 4).map((store) => (
                            <li key={store}>{store}</li>
                          ))}
                          {stores.length > 4 && (
                            <li className="list-none pl-0 text-[var(--cm-on-surface-variant)]/60">
                              +{stores.length - 4} {isES ? "más" : "more"}
                            </li>
                          )}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="space-y-5">
                  <div>
                    <p className="font-label-caps text-[var(--cm-on-surface-variant)]/60 mb-3">
                      Shopify · {isES ? "marcas moda & beauty" : "fashion & beauty brands"}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {MARKET_STATS.shopifyBrands.map((brand) => (
                        <span key={brand} className="touch-compact text-xs font-mono text-[var(--cm-on-surface-variant)] bg-white/5 border border-[var(--cm-outline-variant)]/30 rounded-full px-2.5 py-1">
                          {brand}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="font-label-caps text-[var(--cm-on-surface-variant)]/60 mb-3">Magento</p>
                    <div className="flex flex-wrap gap-2">
                      {magentoStores.map((store) => (
                        <span key={store} className="touch-compact text-xs font-mono text-[var(--cm-on-surface-variant)] bg-white/5 border border-[var(--cm-outline-variant)]/30 rounded-full px-2.5 py-1">
                          {store}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <p className="font-label-caps text-[var(--cm-on-surface-variant)]/60 mb-3">{isES ? "Países" : "Countries"}</p>
                <div className="flex flex-wrap gap-2">
                  {MARKET_STATS.countryCodes.map((c) => (
                    <span key={c} className="touch-compact text-xs font-mono text-[var(--cm-on-surface-variant)] bg-white/5 border border-[var(--cm-outline-variant)]/30 rounded-full px-2.5 py-1">{c}</span>
                  ))}
                </div>
              </div>
            </div>
          </details>
        </div>

        <p className="text-sm text-[var(--cm-on-surface-variant)]/70 mt-10">
          {isES ? `${MARKET_STATS.pricesVerifiedLabel} precios indexados` : `${MARKET_STATS.pricesVerifiedLabel} prices indexed`}
        </p>
      </div>
    </section>
  );
}
