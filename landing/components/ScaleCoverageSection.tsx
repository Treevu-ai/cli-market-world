"use client";

import { useEffect, useRef } from "react";
import { motion, useInView, useSpring, useTransform } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLiveStats, refreshLabel } from "@/hooks/useLiveStats";
import MoatSparkline from "@/components/MoatSparkline";
const vtexLines = {
  supermercados: ["Carrefour AR/BR", "Jumbo AR", "Vea AR", "Chedraui MX", "HEB MX", "Exito CO", "Carulla CO", "Olimpica CO", "Sams Club BR", "Mambo BR", "Wong PE", "Metro PE", "Plaza Vea PE"],
  farmacias: ["Drogaria Pacheco BR", "Farmatodo MX", "Cruz Verde CO/CL"],
  electro: ["Motorola AR/BR/MX/CL", "Electrolux AR/CL", "Whirlpool AR/IT/FR", "Samsung"],
  moda: ["C&A Brasil", "Hering Brasil"],
};

const magentoStores = ["Falabella PE/CL/CO", "Paris CL", "Ripley CL", "Liverpool MX", "El Palacio MX"];

function LiveMetricValue({
  value,
  liveLoaded,
}: {
  value: string | null;
  liveLoaded: boolean;
}) {
  if (value) return <>{value}</>;
  if (!liveLoaded) {
    return <span className="inline-block w-16 h-8 bg-white/10 rounded animate-pulse" aria-hidden />;
  }
  return null;
}

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
      <motion.span ref={ref} className="text-3xl font-bold text-white tracking-tight tabular-nums">{display}</motion.span>
      <span className="text-xs text-white/50 font-mono uppercase tracking-widest text-center">{label}</span>
    </div>
  );
}

export default function ScaleCoverageSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { priceLong, priceChip, stats, liveLoaded, retailersVerified, retailersDefined } = useLiveStats();

  const freshnessPct =
    stats.fresh24hPct != null ? `${stats.fresh24hPct.toFixed(0)}%` : null;
  const freshnessSub = [
    stats.snapshots24h != null ? `${stats.snapshots24h.toLocaleString()} snapshots 24h` : null,
    stats.moatAgeHours != null
      ? `${isES ? "último" : "last"} ${stats.moatAgeHours.toFixed(1)}h`
      : null,
  ]
    .filter(Boolean)
    .join(" · ");

  const coveragePct =
    stats.coverage7dPct != null ? `${stats.coverage7dPct.toFixed(0)}%` : null;
  const coverageSub = [
    `${retailersVerified} ${isES ? "verificados" : "verified"}`,
    stats.collectorStatus ? `collector ${stats.collectorStatus}` : null,
  ]
    .filter(Boolean)
    .join(" · ");

  const technicalMetrics = [
    {
      label: isES ? "Precios acumulados" : "Total snapshots",
      value:
        stats.totalSnapshotsAll != null ? stats.totalSnapshotsAll.toLocaleString() : null,
    },
    {
      label: isES ? "Promedio diario (7d)" : "Daily avg (7d)",
      value: stats.avgDaily7d != null ? stats.avgDaily7d.toLocaleString() : null,
    },
    {
      label: isES ? "Serie histórica desde" : "Historical series since",
      value: stats.moatStart != null ? stats.moatStart.slice(0, 10) : null,
    },
    {
      label: isES ? "Intervalo collector" : "Collector interval",
      value: `cada ${MARKET_STATS.pricesRefreshHours}h`,
    },
  ].filter((item) => item.value != null);

  const scaleStats = [
    { end: retailersDefined, label: isES ? "retailers catálogo" : "retailers in catalog" },
    { end: retailersVerified, label: isES ? "verificados activos" : "verified active" },
    { end: MARKET_STATS.countries, label: isES ? "países" : "countries" },
    { end: MARKET_STATS.platforms, label: isES ? "plataformas" : "platforms" },
  ];

  return (
    <section id="coverage" className="landing-section animate-fade-in bg-[#0A2540]">
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="text-[11px] font-mono uppercase tracking-widest text-white/40 mb-4">
            {isES ? "Escala y cobertura" : "Scale and coverage"}
          </p>
          <h2 className="text-[clamp(1.5rem,4vw,2rem)] font-semibold text-white tracking-tight mb-4">
            {isES ? "Cobertura retail en LatAm" : "Retail coverage across LatAm"}
          </h2>
          <p className="inline-flex items-center gap-2 text-xs font-mono text-[#b9b9f9] bg-white/10 border border-white/10 rounded-full px-3 py-1 mb-4">
            {priceChip} · {refreshLabel(isES)}
          </p>
          <p className="text-base text-white/60 max-w-2xl mx-auto leading-relaxed mb-12">
            {isES
              ? `${MARKET_STATS.platformsPhraseEs}. ${priceLong} precios verificados · ${refreshLabel(isES)}.`
              : `${MARKET_STATS.platformsPhraseEn}. ${priceLong} verified prices · ${refreshLabel(isES)}.`}
          </p>
        </div>

        <div className="landing-content-rail mb-8">
          <div className="flex flex-wrap justify-center gap-2 mb-3">
            {["Wong PE", "Metro PE", "Plaza Vea PE", "Carrefour AR", "Jumbo AR", "Vea AR", "Chedraui MX", "HEB MX", "Éxito CO", "Carulla CO", "Falabella CL", "Ripley CL", "Liverpool MX"].map((store) => (
              <span
                key={store}
                className="touch-compact text-xs font-mono text-white/60 bg-white/5 border border-white/10 rounded-full px-2.5 py-1"
              >
                {store}
              </span>
            ))}
            <span className="text-xs font-mono text-white/30 px-2.5 py-1">
              +{retailersVerified - 13} {isES ? "más" : "more"}
            </span>
          </div>
          <p className="text-center text-xs text-white/30 font-mono">
            {isES
              ? `VTEX · Shopify · Magento · WooCommerce · Golden Record · ${retailersVerified} activos`
              : `VTEX · Shopify · Magento · WooCommerce · Golden Record · ${retailersVerified} active`}
          </p>
        </div>

        <div className="landing-content-rail grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-4">
          {scaleStats.map((s, i) => (
            <Counter key={s.label} end={s.end} label={s.label} delay={i * 100} />
          ))}
        </div>

        <p className="text-xs font-mono text-white/30 text-center mb-10 sm:mb-14 max-w-lg mx-auto">
          {isES
            ? `${retailersVerified} verificados = precios activos y en producción · ${retailersDefined} en catálogo = integrados, algunos en proceso de activación`
            : `${retailersVerified} verified = active, live prices · ${retailersDefined} in catalog = integrated, some pending activation`}
        </p>

        <div className="landing-content-rail grid grid-cols-1 md:grid-cols-3 gap-6 mb-14 text-left">
          <div className="card-cyber-dark p-6">
            <p className="text-xs uppercase tracking-widest text-white/40 mb-1">
              {isES ? "Inventario" : "Inventory"}
            </p>
            <p className="text-3xl font-black text-white tabular-nums">{priceLong}</p>
            <p className="text-xs text-white/50 mt-1">
              {isES
                ? `precios indexados · normalizados kg/L · ${MARKET_STATS.indicatorsCount} datos de mercado`
                : `indexed prices · kg/L normalized · ${MARKET_STATS.indicatorsCount} data points`}
            </p>
          </div>
          <div className="card-cyber-dark p-6">
            <p className="text-xs uppercase tracking-widest text-white/40 mb-2">
              {isES ? "Frescura" : "Freshness"}
            </p>
            <p className="text-3xl font-black text-white tabular-nums min-h-[2.25rem]">
              <LiveMetricValue value={freshnessPct} liveLoaded={liveLoaded} />
            </p>
            {freshnessSub ? (
              <p className="text-xs text-white/50 mt-1">{freshnessSub}</p>
            ) : null}
          </div>
          <div className="card-cyber-dark p-6">
            <p className="text-xs uppercase tracking-widest text-white/40 mb-2">
              {isES ? "Cobertura" : "Coverage"}
            </p>
            <p className="text-3xl font-black text-white tabular-nums min-h-[2.25rem]">
              <LiveMetricValue value={coveragePct} liveLoaded={liveLoaded} />
            </p>
            {coverageSub ? (
              <p className="text-xs text-white/50 mt-1">{coverageSub}</p>
            ) : null}
          </div>
        </div>

        <div className="landing-content-rail mb-10">
          <MoatSparkline />
        </div>

        <div className="landing-content-rail text-left space-y-4">
          <details className="rounded-xl border border-white/10 bg-white/5">
            <summary className="px-5 py-4 text-sm font-semibold text-white/70 cursor-pointer select-none hover:text-white transition-colors">
              {isES ? "Métricas técnicas del collector" : "Collector technical metrics"}
            </summary>
            <div className="px-5 pb-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4">
                {technicalMetrics.map((item) => (
                  <div key={item.label} className="card-cyber-dark p-4 border-l-2 border-[#533afd]/60">
                    <p className="text-xs uppercase tracking-widest text-[#b9b9f9] mb-2">{item.label}</p>
                    <p className="text-lg font-bold text-white tabular-nums">{item.value}</p>
                  </div>
                ))}
              </div>
            </div>
          </details>

          <details className="rounded-xl border border-white/10 bg-white/5">
            <summary className="px-5 py-4 text-sm font-semibold text-white/70 cursor-pointer select-none hover:text-white transition-colors">
              {isES ? "Plataformas y retailers" : "Platforms and retailers"}
            </summary>
            <div className="px-5 pb-5 space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4">
                {[
                  { name: "VTEX", count: MARKET_STATS.platformVtex, note: isES ? "supermercados, electro, moda LatAm" : "supermarkets, electronics, LatAm fashion" },
                  { name: "Shopify", count: MARKET_STATS.platformShopify, note: isES ? "moda & beauty global" : "global fashion & beauty" },
                  { name: "Magento", count: MARKET_STATS.platformMagento, note: isES ? "departamentales" : "department stores" },
                  { name: "WooCommerce", count: MARKET_STATS.platformWooCommerce, note: isES ? "FMCG organico PE (piloto)" : "organic FMCG PE (pilot)" },
                ].map((p) => (
                  <div key={p.name} className="card-cyber-dark p-5">
                    <p className="text-lg font-bold text-white">{p.name}</p>
                    <p className="text-2xl font-black text-white tabular-nums mt-1">{p.count}</p>
                    <p className="text-sm text-white/50 mt-2 leading-relaxed">{p.note}</p>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <p className="text-[10px] font-mono uppercase tracking-widest text-white/40 mb-3">VTEX</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {Object.entries(vtexLines).map(([line, stores]) => (
                      <div key={line} className="card-cyber-dark p-4">
                        <h3 className="text-xs font-bold uppercase text-white mb-2">{line}</h3>
                        <ul className="text-sm text-white/50 space-y-1 leading-relaxed list-disc pl-4">
                          {stores.slice(0, 4).map((store) => (
                            <li key={store}>{store}</li>
                          ))}
                          {stores.length > 4 && (
                            <li className="list-none pl-0 text-white/30">
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
                    <p className="text-[10px] font-mono uppercase tracking-widest text-white/40 mb-3">
                      Shopify · {isES ? "marcas moda & beauty" : "fashion & beauty brands"}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {MARKET_STATS.shopifyBrands.map((brand) => (
                        <span key={brand} className="touch-compact text-xs font-mono text-white/60 bg-white/5 border border-white/10 rounded-full px-2.5 py-1">
                          {brand}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-[10px] font-mono uppercase tracking-widest text-white/40 mb-3">Magento</p>
                    <div className="flex flex-wrap gap-2">
                      {magentoStores.map((store) => (
                        <span key={store} className="touch-compact text-xs font-mono text-white/60 bg-white/5 border border-white/10 rounded-full px-2.5 py-1">
                          {store}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-[10px] font-mono uppercase tracking-widest text-white/40 mb-3">WooCommerce</p>
                    <div className="flex flex-wrap gap-2">
                      {MARKET_STATS.woocommerceStores.map((store) => (
                        <span key={store} className="touch-compact text-xs font-mono text-white/60 bg-white/5 border border-white/10 rounded-full px-2.5 py-1">
                          {store}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <p className="text-[10px] font-mono uppercase tracking-widest text-white/40 mb-3">{isES ? "Países" : "Countries"}</p>
                <div className="flex flex-wrap gap-2">
                  {MARKET_STATS.countryCodes.map((c) => (
                    <span key={c} className="touch-compact text-xs font-mono text-white/60 bg-white/5 border border-white/10 rounded-full px-2.5 py-1">{c}</span>
                  ))}
                </div>
              </div>
            </div>
          </details>
        </div>

      </div>
    </section>
  );
}
